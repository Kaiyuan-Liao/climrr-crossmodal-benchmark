"""M5-WP1: frozen inputs, compatibility rules on synthetic fixtures, and the real matrix's shape.

The rule tests use **synthetic claims** against the real prototype records, so
the positive path is exercised even though the real claim set may never reach
it. No test here asserts how many real pairs are compatible (ruling action 14,
criterion 18).
"""

from __future__ import annotations

import copy
import json

import pytest

from climrr import compat


def _frozen() -> dict:
    return json.loads(compat.INPUTS_PATH.read_text(encoding="utf-8"))


# --- Phase A: frozen inputs -----------------------------------------------------


def test_the_frozen_inputs_still_match_every_referenced_record():
    compat.verify_inputs()


def test_the_freeze_pins_27_claims_3_prototypes_and_81_pairs():
    f = _frozen()
    assert (f["n_claims"], f["n_prototypes"], f["n_pairs"]) == (27, 3, 81)
    assert len({c["claim_id"] for c in f["claims"]}) == 27
    assert [p["prototype_id"] for p in f["prototypes"]] == list(compat.PROTOTYPE_IDS)
    assert all(c["claim_validation_status"] == "single_reader_provisional" for c in f["claims"])


def test_a_changed_claim_record_fails_the_freeze():
    tampered = copy.deepcopy(_frozen())
    tampered["claims"][0]["claim_record_sha256"] = "0" * 64
    with pytest.raises(compat.FreezeError):
        compat.verify_inputs(tampered)


def test_a_changed_prototype_record_fails_the_freeze():
    tampered = copy.deepcopy(_frozen())
    tampered["prototypes"][2]["prototype_record_sha256"] = "0" * 64
    with pytest.raises(compat.FreezeError):
        compat.verify_inputs(tampered)


#: The M5-WP1 artifacts as reviewed (D-018). They are frozen: a later package
#: versions a prototype or adds a rule, it never rewrites these bytes.
M5WP1_FROZEN_SHA256 = {
    "m5wp1_inputs.json": "bc22b4fa9344283fd31e9b7ac1f70fa53276d8dd171d6749933a4cf0b6a628cc",
    "m5wp1_matrix.json": "526ac573f58a027c53b99e90a88fc7b3509c550afe205a9d6f15f74072d4cd02",
}


@pytest.mark.parametrize("name", sorted(M5WP1_FROZEN_SHA256))
def test_the_reviewed_m5wp1_artifacts_are_byte_identical(name):
    from climrr.checksums import sha256_file
    assert sha256_file(compat.BRIDGES / name) == M5WP1_FROZEN_SHA256[name]


def test_record_hash_ignores_key_order_but_not_content():
    assert compat.record_sha256({"a": 1, "b": "x"}) == compat.record_sha256({"b": "x", "a": 1})
    assert compat.record_sha256({"a": 1}) != compat.record_sha256({"a": 2})


# --- Phase D: rules on synthetic claims against the real prototype records ------

PROTOS = {pid: json.loads(compat.prototype_file(pid).read_text(encoding="utf-8")) for pid in compat.PROTOTYPE_IDS}
GEO = compat.load_geo_list()


def _dim(value: str, status: str = "explicit") -> dict:
    return {"value": value, "status": status}


UNKNOWN = {"value": "unknown", "status": "unknown"}


def _claim(**over) -> dict:
    """A synthetic claim built to match P-COUNTY-1 on every dimension."""
    c = {
        "claim_id": "SYN-C1",
        "claim_type": "projection",
        "claim_validation_status": "single_reader_provisional",
        "concept": _dim("fwi_seasonal_value"),
        "relation_or_direction": _dim("increase"),
        "geography": _dim("Oklahoma, Stephens"),
        "temporal_frame": _dim("2085-2094"),
        "scenario": _dim("RCP8.5"),
        "experimental_condition": UNKNOWN,
    }
    c.update(over)
    return c


def _status(row: dict) -> dict:
    return {d: row["judgments"][d]["status"] for d in compat.DIMENSIONS}


@pytest.mark.parametrize("pid,geo", [("P-COUNTY-1", "oklahoma,  STEPHENS"), ("P-CELL-1", "R106C361")])
def test_the_positive_path_a_fully_matching_claim_is_compatible_on_all_five(pid, geo):
    row = compat.evaluate_pair(_claim(geography=_dim(geo)), PROTOS[pid], GEO)
    assert _status(row) == {d: "compatible" for d in compat.DIMENSIONS}
    assert row["all_compatible"] and row["n_incompatible"] == 0
    assert [row["judgments"][d]["rule_id"] for d in compat.DIMENSIONS] == ["C-1", "G-1", "T-1", "S-1", "D-1"]


def test_the_state_prototype_matches_concept_geography_scenario_direction_but_has_no_year_window():
    claim = _claim(concept=_dim("heatindex_days_above_105F"), geography=_dim("California"))
    row = compat.evaluate_pair(claim, PROTOS["P-STATE-1"], GEO)
    assert _status(row) == {"concept": "compatible", "geography": "compatible", "time": "not_evaluable",
                            "scenario": "compatible", "direction": "compatible"}
    assert row["judgments"]["time"]["reason"] == "prototype_window_has_no_year_range"


@pytest.mark.parametrize("dim", ["concept", "relation_or_direction", "geography", "temporal_frame", "scenario"])
@pytest.mark.parametrize("pid", compat.PROTOTYPE_IDS)
def test_unknown_never_yields_incompatible(dim, pid):
    # Every other dimension set to a value that would conflict, so a leak would show.
    conflicting = _claim(concept=_dim("fwi_seasonal_value"), relation_or_direction=_dim("decrease"),
                         geography=_dim("China"), temporal_frame=_dim("1950-1960"), claim_type="finding",
                         scenario=_dim("RCP4.5"))
    conflicting[dim] = dict(UNKNOWN)
    row = compat.evaluate_pair(conflicting, PROTOS[pid], GEO)
    name = {"relation_or_direction": "direction", "temporal_frame": "time"}.get(dim, dim)
    j = row["judgments"][name]
    assert j["status"] == "not_evaluable"
    assert j["rule_id"] in ("U-1", "D-1")


@pytest.mark.parametrize("geo,status,rule", [
    ("Bangalore city, India", "incompatible", "G-2"),
    ("semi-arid northwest Australia", "incompatible", "G-2"),
    ("Khorog, Western Pamirs, Tajikistan", "incompatible", "G-2"),
    ("urban settlement areas of Bangalore", "not_evaluable", "G-3"),   # a city: different granularity
    ("Shirgin Village, Western Pamirs", "not_evaluable", "G-3"),
    ("Oklahoma City", "not_evaluable", "G-3"),                         # a US city vs a county label
    ("Oklahoma", "not_evaluable", "G-3"),                              # a state vs a county label
    ("global / worldwide", "not_evaluable", "G-3"),
    ("Northwest Atlantic", "not_evaluable", "G-3"),
    ("China and the United States", "not_evaluable", "G-3"),
    ("Indiana", "not_evaluable", "G-3"),                               # whole words only: not "India"
])
def test_geography_incompatibility_requires_an_explicitly_disjoint_named_place(geo, status, rule):
    j = compat.evaluate_pair(_claim(geography=_dim(geo)), PROTOS["P-COUNTY-1"], GEO)["judgments"]["geography"]
    assert (j["status"], j["rule_id"]) == (status, rule)


def test_an_inferred_non_us_geography_is_not_evaluable():
    j = compat.evaluate_pair(_claim(geography=_dim("China", "inferred")), PROTOS["P-STATE-1"], GEO)
    assert j["judgments"]["geography"]["status"] == "not_evaluable"


@pytest.mark.parametrize("concept", ["fire weather index", "wildfire smoke", "drought", "urban heat island",
                                     "heat index"])
@pytest.mark.parametrize("pid", compat.PROTOTYPE_IDS)
def test_concept_mismatch_is_never_incompatible_and_direction_is_then_not_evaluated(concept, pid):
    row = compat.evaluate_pair(_claim(concept=_dim(concept)), PROTOS[pid], GEO)
    assert row["judgments"]["concept"]["status"] == "not_evaluable"
    assert row["judgments"]["concept"]["reason"] == "no_approved_mapping"
    d = row["judgments"]["direction"]
    assert (d["status"], d["rule_id"], d["reason"]) == ("not_evaluable", "D-1", "concept_not_comparable")


def test_no_concept_mapping_has_been_approved():
    assert compat.APPROVED_CONCEPT_MAPPINGS == {}


def test_direction_compares_only_listed_words_once_concept_is_compatible():
    p = PROTOS["P-COUNTY-1"]
    assert compat.evaluate_pair(_claim(relation_or_direction=_dim("decrease")), p, GEO)["judgments"]["direction"]["status"] == "incompatible"
    assert compat.evaluate_pair(_claim(relation_or_direction=_dim("rose sharply")), p, GEO)["judgments"]["direction"]["status"] == "not_evaluable"


@pytest.mark.parametrize("frame,ctype,status,rule", [
    ("2080 to 2100", "projection", "compatible", "T-1"),
    ("censuses 1992-2015", "finding", "incompatible", "T-2"),
    ("censuses 1992-2015", "mechanism", "not_evaluable", "T-3"),
    ("censuses 1992-2015", "projection", "not_evaluable", "T-3"),
    ("2030-2060", "finding", "not_evaluable", "T-3"),
    ("late 1930s to early 1960s", "finding", "not_evaluable", "T-3"),   # decades are not four-digit years
    ("2001 and 2021", "finding", "not_evaluable", "T-3"),               # two years are not a range
])
def test_time_rules(frame, ctype, status, rule):
    j = compat.evaluate_pair(_claim(temporal_frame=_dim(frame), claim_type=ctype), PROTOS["P-CELL-1"], GEO)
    assert (j["judgments"]["time"]["status"], j["judgments"]["time"]["rule_id"]) == (status, rule)


def test_a_prototype_without_a_year_window_never_yields_time_incompatible():
    j = compat.evaluate_pair(_claim(temporal_frame=_dim("1950-1960"), claim_type="finding"), PROTOS["P-STATE-1"], GEO)
    assert j["judgments"]["time"]["status"] == "not_evaluable"


@pytest.mark.parametrize("scen,status", [("RCP8.5", "compatible"), ("RCP 4.5", "incompatible"),
                                         ("SSP5-8.5", "not_evaluable"), ("high emissions", "not_evaluable")])
def test_scenario_rule(scen, status):
    j = compat.evaluate_pair(_claim(scenario=_dim(scen)), PROTOS["P-COUNTY-1"], GEO)["judgments"]["scenario"]
    assert j["status"] == status


def test_experimental_condition_cannot_reach_the_scenario_comparison():
    claim = _claim(scenario=dict(UNKNOWN), experimental_condition=_dim("RCP8.5 treatment, 750 ppm CO2"))
    j = compat.evaluate_pair(claim, PROTOS["P-COUNTY-1"], GEO)["judgments"]["scenario"]
    assert (j["status"], j["reason"]) == ("not_evaluable", "claim_value_unknown")
    assert "experimental" not in json.dumps(j)
    for path in (compat.__file__, compat.REPO_ROOT / "scripts" / "compat_matrix.py"):
        assert "experimental_condition" not in open(path, encoding="utf-8").read()


@pytest.mark.parametrize("path", ["src/climrr/compat.py", "scripts/compat_matrix.py"])
def test_no_embedding_model_or_similarity_code(path):
    import ast
    tree = ast.parse((compat.REPO_ROOT / path).read_text(encoding="utf-8"))
    mods = {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    mods |= {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert mods <= {"__future__", "hashlib", "json", "re", "pathlib", "yaml", "climrr", "csv", "io", "sys"}


def test_summary_counts_an_all_compatible_row_when_one_exists():
    rows = [compat.evaluate_pair(_claim(), PROTOS["P-COUNTY-1"], GEO),
            compat.evaluate_pair(_claim(geography=_dim("India")), PROTOS["P-COUNTY-1"], GEO)]
    s = compat.summarize(rows)
    assert (s["n_all_compatible"], s["n_pairs_with_any_incompatible"], s["incompatible_by_rule"]) == (1, 1, {"G-2": 1})


# --- Phase C: the real matrix's shape, never its totals ---------------------------

MATRIX = json.loads((compat.BRIDGES / "m5wp1_matrix.json").read_text(encoding="utf-8"))


def test_every_frozen_pair_appears_exactly_once():
    f = _frozen()
    expected = {f"{c['claim_id']}__{p['prototype_id']}" for c in f["claims"] for p in f["prototypes"]}
    ids = [r["pair_id"] for r in MATRIX["rows"]]
    assert len(ids) == 81 and len(set(ids)) == 81 and set(ids) == expected


def test_every_row_has_five_judgments_with_rule_values_and_reason():
    for r in MATRIX["rows"]:
        assert set(r["judgments"]) == set(compat.DIMENSIONS)
        for j in r["judgments"].values():
            assert j["status"] in compat.STATUSES
            assert j["rule_id"] in compat.RULES
            assert "raw" in j["claim_value"] and j["prototype_value"]
            assert j["claim_value"]["derivation_rule"] and j["prototype_value"]["derivation_rule"]
            assert j["reason"]


def test_every_row_carries_claim_type_background_flag_and_validation_status():
    for r in MATRIX["rows"]:
        assert r["claim_type"] in ("finding", "projection", "mechanism", "recommendation", "background_citation")
        assert r["is_background_citation"] == (r["claim_type"] == "background_citation")
        assert r["claim_validation_status"] == "single_reader_provisional"
        assert r["prototype_validation_only"] is True


def test_the_tracked_matrix_reproduces_from_the_frozen_inputs():
    claims, protos = compat.load_frozen_claims_and_prototypes(compat.verify_inputs())
    rows = compat.build_matrix(claims, protos, GEO)
    assert rows == MATRIX["rows"]
    assert compat.summarize(rows) == MATRIX["summary"]


def test_unknown_never_produced_incompatible_in_the_real_matrix():
    for r in MATRIX["rows"]:
        for j in r["judgments"].values():
            if j["claim_value"].get("tag") == "unknown":
                assert j["status"] == "not_evaluable"


def test_the_bounded_conclusion_appears_if_and_only_if_no_pair_is_all_compatible():
    doc = (compat.REPO_ROOT / "docs" / "M5_WP1_COMPATIBILITY.md").read_text(encoding="utf-8")
    sentence = ("No fully compatible pair was found under the current deterministic rules "
                "in this fixed provisional pilot set.")
    assert (sentence in doc) == (MATRIX["summary"]["n_all_compatible"] == 0)
    assert "estimate nothing about the" in doc
