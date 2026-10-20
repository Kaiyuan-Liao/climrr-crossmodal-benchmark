"""M5-WP4: frozen inputs, the geography role gate, the SHI flag, and the matrix's reproduction.

As for M5-WP1 / M5-WP2, nothing here asserts how many real pairs are
eligible; the matrix is checked by re-derivation from the frozen inputs.
"""

from __future__ import annotations

import copy
import json

import pytest

from climrr import compat, conceptmap, m5wp4
from climrr.checksums import sha256_file


def _frozen() -> dict:
    return json.loads(m5wp4.INPUTS_PATH.read_text(encoding="utf-8"))


def test_the_frozen_inputs_still_match():
    assert m5wp4.verify_inputs() == _frozen()


def test_the_freeze_names_what_the_package_asks_for():
    f = _frozen()
    assert f["concept_map_sha256"].startswith("27f7a44d")
    assert [(p["prototype_id"], p["version"]) for p in f["prototypes"]] == [("P-CELL-1", 1), ("P-COUNTY-1", 1), ("P-STATE-1", 2)]
    assert f["prototypes"][2]["prototype_file"].endswith("P-STATE-1.v2.json")
    assert f["n_pairs"] == 3 * f["n_claims"]
    assert {c["evidence_tier"] for c in f["claims"]} == {"A", "B", "C"}
    assert f["r_fwi_1_version"]["rule"] == "R-FWI-1" and f["r_fwi_1_version"]["version"] == "v1"
    assert f["untouched"]["m5wp2_inputs.json"] == sha256_file(m5wp4.BRIDGES / "m5wp2_inputs.json")
    assert f["untouched"]["m5wp1_matrix.json"] == "526ac573f58a027c53b99e90a88fc7b3509c550afe205a9d6f15f74072d4cd02"


def test_a_changed_claim_fails_the_freeze():
    t = copy.deepcopy(_frozen())
    t["claims"][0]["claim_record_sha256"] = "0" * 64
    with pytest.raises(m5wp4.FreezeError):
        m5wp4.verify_inputs(t)


def test_the_tracked_matrix_reproduces_from_the_frozen_inputs():
    f = _frozen()
    rows = m5wp4.run(f)
    saved = json.loads(m5wp4.MATRIX_JSON.read_text(encoding="utf-8"))
    assert saved["inputs_sha256"] == sha256_file(m5wp4.INPUTS_PATH)
    assert json.loads(json.dumps(rows, ensure_ascii=False)) == saved["rows"]
    assert m5wp4.MATRIX_CSV.read_text(encoding="utf-8") == m5wp4.to_csv(rows)
    assert len({r["pair_id"] for r in rows}) == len(rows) == f["n_pairs"]
    assert saved["summary"] == m5wp4.summarize(rows)


def test_every_row_carries_the_tier_and_the_adjudicated_role():
    for r in json.loads(m5wp4.MATRIX_JSON.read_text(encoding="utf-8"))["rows"]:
        assert r["evidence_tier"] in ("A", "B", "C")
        assert r["judgments"]["geography"]["claim_value"]["role_class"]


PROTOS = {p: json.loads((m5wp4.PROTO_DIR / f).read_text(encoding="utf-8")) for p, f in
          zip(("P-CELL-1", "P-COUNTY-1", "P-STATE-1"), m5wp4.PROTOTYPE_FILES)}


def _claim(geo: str, role_class: str, concept: str = "heat index") -> dict:
    return {"claim_id": "SYN", "claim_type": "projection", "claim_validation_status": "x",
            "concept": {"value": concept, "status": "explicit"},
            "relation_or_direction": {"value": "increase", "status": "explicit"},
            "geography": {"value": geo, "status": "explicit", "role": role_class, "role_class": role_class},
            "temporal_frame": {"value": "2085-2094", "status": "explicit"},
            "scenario": {"value": "RCP8.5", "status": "explicit"}, "experimental_condition": {"value": "unknown", "status": "unknown"}}


def _geo(geo: str, role_class: str, pid: str) -> dict:
    row = m5wp4.evaluate_pair(_claim(geo, role_class), PROTOS[pid], compat.load_geo_list(), conceptmap.load())
    return row["judgments"]["geography"]


@pytest.mark.parametrize("geo,role,pid,status,rule", [
    ("California", "study_area", "P-STATE-1", "compatible", "G-1"),
    ("California", "cited_study_area", "P-STATE-1", "compatible", "G-1"),
    ("California", "affiliation", "P-STATE-1", "not_evaluable", "G-R"),
    ("California", "citation_or_person", "P-STATE-1", "not_evaluable", "G-R"),
    ("California", "contextual", "P-STATE-1", "not_evaluable", "G-R"),
    ("California", "unknown", "P-STATE-1", "not_evaluable", "G-R"),
    ("Oklahoma", "study_area", "P-COUNTY-1", "not_evaluable", "G-3-granularity"),
    ("Oklahoma, Stephens", "study_area", "P-COUNTY-1", "compatible", "G-1"),
    ("Dewey County, NW Oklahoma", "study_area", "P-COUNTY-1", "not_evaluable", "G-3"),
    ("China", "affiliation", "P-STATE-1", "not_evaluable", "G-R"),
    ("China", "study_area", "P-STATE-1", "incompatible", "G-2"),
])
def test_geography_string_and_role(geo, role, pid, status, rule):
    j = _geo(geo, role, pid)
    assert (j["status"], j["rule_id"]) == (status, rule)


def test_a_role_gated_place_is_never_compatible_or_incompatible():
    for role in m5wp4.NON_LOCATIONAL_ROLES:
        for pid in PROTOS:
            for geo in ("California", "Oklahoma, Stephens", "China"):
                assert _geo(geo, role, pid)["status"] == "not_evaluable"


def test_standardized_heat_index_is_flagged_not_masked():
    row = m5wp4.evaluate_pair(_claim("Moscow", "study_area", "standardized heat index (SHI)"), PROTOS["P-STATE-1"],
                              compat.load_geo_list(), conceptmap.load())
    assert row["judgments"]["concept"]["status"] == compat.FAMILY_LEVEL
    assert m5wp4.COLLISION_FLAG in row["flags"]
    assert row["judgments"]["concept"]["possible_collision"]["hits"][0]["matched_text"] == "heat index"


def test_extended_heat_index_stays_masked_and_plain_heat_index_is_not_flagged():
    geo, cmap = compat.load_geo_list(), conceptmap.load()
    ext = m5wp4.evaluate_pair(_claim("X", "study_area", "extended heat index"), PROTOS["P-STATE-1"], geo, cmap)
    assert ext["judgments"]["concept"]["status"] == "not_evaluable" and not ext["flags"]
    plain = m5wp4.evaluate_pair(_claim("X", "study_area", "heat index trends"), PROTOS["P-STATE-1"], geo, cmap)
    assert plain["judgments"]["concept"]["status"] == compat.FAMILY_LEVEL and not plain["flags"]
