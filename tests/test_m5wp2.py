"""M5-WP2: frozen inputs, effective claims, relation precedence, and the matrix's reproduction.

Like M5-WP1's tests, nothing here asserts how many real pairs are eligible;
the matrix is checked by re-derivation from the frozen inputs.
"""

from __future__ import annotations

import copy
import json

import pytest

from climrr import compat, conceptmap, m5wp2
from climrr.checksums import sha256_file


def _frozen() -> dict:
    return json.loads(m5wp2.INPUTS_PATH.read_text(encoding="utf-8"))


def test_the_frozen_inputs_still_match():
    m5wp2.verify_inputs()


def test_the_freeze_uses_p_state_1_v2_and_leaves_m5wp1_untouched():
    f = _frozen()
    assert [(p["prototype_id"], p["version"]) for p in f["prototypes"]] == [("P-CELL-1", 1), ("P-COUNTY-1", 1), ("P-STATE-1", 2)]
    assert f["prototypes"][2]["prototype_file"].endswith("P-STATE-1.v2.json")
    assert f["untouched"]["m5wp1_inputs.json"] == "bc22b4fa9344283fd31e9b7ac1f70fa53276d8dd171d6749933a4cf0b6a628cc"
    assert f["untouched"]["m5wp1_matrix.json"] == "526ac573f58a027c53b99e90a88fc7b3509c550afe205a9d6f15f74072d4cd02"
    assert (f["n_claims"], f["n_prototypes"], f["n_pairs"]) == (26, 3, 78)
    assert {c["evidence_tier"] for c in f["claims"]} == {"A", "B", "C"}


def test_a_changed_claim_fails_the_freeze():
    t = copy.deepcopy(_frozen())
    t["claims"][0]["claim_record_sha256"] = "0" * 64
    with pytest.raises(m5wp2.FreezeError):
        m5wp2.verify_inputs(t)


def test_the_tracked_matrix_reproduces_from_the_frozen_inputs():
    rows = m5wp2.run(_frozen())
    saved = json.loads(m5wp2.MATRIX_JSON.read_text(encoding="utf-8"))
    assert saved["inputs_sha256"] == sha256_file(m5wp2.INPUTS_PATH)
    assert json.loads(json.dumps(rows, ensure_ascii=False)) == saved["rows"]
    assert m5wp2.MATRIX_CSV.read_text(encoding="utf-8") == m5wp2.to_csv(rows)
    assert len({r["pair_id"] for r in rows}) == len(rows) == 78


def test_adopted_dimensions_are_what_the_matrix_compares():
    c = {"claim_id": "X", "claim_type": "finding", "geography": {"value": "44 states (United States)", "status": "explicit"},
         "adjudication": {"adopted_dimensions": {"geography": {"value": "44 states", "tag": "explicit"},
                                                 "claim_type": "unresolved_tie"}}}
    e = m5wp2.effective_claim(c)
    assert e["geography"] == {"value": "44 states", "status": "explicit"} and e["claim_type"] == "unresolved_tie"
    assert e["adopted_dimensions_applied"] == ["claim_type", "geography"]


def _row(**st):
    st = {"concept": "not_evaluable", "geography": "not_evaluable", "time": "not_evaluable", "scenario": "not_evaluable",
          "direction": "not_evaluable", **st}
    return {"pair_id": "SYN", "judgments": {d: {"status": s} for d, s in st.items()}}


@pytest.mark.parametrize("st,rel", [
    ({"concept": "compatible", "geography": "compatible", "time": "compatible", "scenario": "compatible", "direction": "compatible"}, "supporting"),
    ({"concept": "compatible", "geography": "compatible", "time": "compatible", "direction": "compatible"}, "supporting_qualified"),
    ({"concept": compat.FAMILY_LEVEL, "geography": "compatible", "time": "compatible", "scenario": "compatible"}, "supporting_qualified"),
    ({"concept": "compatible", "geography": "compatible", "direction": "incompatible"}, "contradicting"),
    ({"concept": compat.FAMILY_LEVEL, "geography": "compatible", "time": "incompatible"}, "incompatible"),
    ({"concept": compat.FAMILY_LEVEL}, "related_insufficient"),
    ({"geography": "compatible"}, "uncertain"),
    ({"time": "incompatible"}, "incompatible"),
])
def test_relation_precedence(st, rel):
    assert m5wp2.assign_relation(_row(**st))[0] == rel


def test_unknown_scenario_or_family_concept_never_yields_supporting():
    for st in ({"concept": compat.FAMILY_LEVEL, "geography": "compatible", "time": "compatible", "scenario": "compatible", "direction": "compatible"},
               {"concept": "compatible", "geography": "compatible", "time": "compatible", "direction": "compatible"}):
        assert m5wp2.assign_relation(_row(**st))[0] != "supporting"


PROTOS = {p: json.loads((m5wp2.PROTO_DIR / f).read_text(encoding="utf-8")) for p, f in
          zip(("P-CELL-1", "P-COUNTY-1", "P-STATE-1"), m5wp2.PROTOTYPE_FILES)}


@pytest.mark.parametrize("geo,pid,status", [("California", "P-STATE-1", "compatible"),
                                            ("Oklahoma", "P-COUNTY-1", "not_evaluable"),
                                            ("Dewey County, NW Oklahoma", "P-COUNTY-1", "not_evaluable"),
                                            ("Oklahoma, Stephens", "P-COUNTY-1", "compatible"),
                                            ("California, Arizona and Nevada", "P-STATE-1", "not_evaluable")])
def test_geography_cases_named_in_the_work_package(geo, pid, status):
    c = {"claim_id": "SYN", "claim_type": "projection", "claim_validation_status": "x",
         "concept": {"value": "heat index", "status": "explicit"}, "relation_or_direction": {"value": "increase", "status": "explicit"},
         "geography": {"value": geo, "status": "explicit"}, "temporal_frame": {"value": "2085-2094", "status": "explicit"},
         "scenario": {"value": "RCP8.5", "status": "explicit"}}
    row = compat.evaluate_pair(c, PROTOS[pid], compat.load_geo_list(), conceptmap.load())
    assert row["judgments"]["geography"]["status"] == status
