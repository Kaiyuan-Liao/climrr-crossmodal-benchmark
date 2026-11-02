"""Pilot seed selection v1 (D-050) and the packets built from it (pilot P2b-fix; D-047a, D-049; v3: DR-SEED-RANK-3)."""

from __future__ import annotations

import copy
import json

import pytest

from climrr import itemseeds as sd
from climrr import itemseeds_v2 as s2
from climrr import litgeo as lg
from climrr import litindependence as li
from climrr import litstatements_run2 as r2
from climrr import pilot_selection as psel
from climrr import synthpackets as spk
from climrr.checksums import sha256_file
from climrr.manifest import MANIFEST_PATH, load_entry

ORDER = [("SD2-TP1-00018", 1), ("SD2-TP1-00069", 1), ("SD2-TP1-00071", 3), ("SD2-TP1-00271", 3), ("SD2-TP1-00460", 3),
         ("SD2-TP1-00589", 3), ("SD2-TP1-02785", 4), ("SD2-TP1-02787", 4), ("SD2-TP1-02789", 4), ("SD2-TP1-00075", 7)]


def test_the_selection_is_pinned_in_the_manifest():
    entry = load_entry("pilot_selection_v1.yaml", MANIFEST_PATH)
    assert entry["path"] == "data/metadata/benchmark/pilot_selection_v1.yaml" and entry["decision_ref"] == "D-050"
    assert sha256_file(psel.SELECTION_PATH) == entry["sha256"]
    assert "no interpretation assigned" in entry["interpretation_notes"]


def test_the_owner_selection_in_order_with_its_exclusions():
    sel = psel.load()
    assert sel["selected_by"] == "Kaiyuan" and sel["decision"] == "D-050" and sel["date"] == "2026-11-01"
    assert [(x["seed_id"], x["rung"]) for x in psel.selected(sel)] == ORDER
    assert all(x["reason"] for x in sel["selected"])
    ex = {x["seed_id"]: x["reason"] for x in sel["excluded_from_shortlist"]}
    assert ex == {"SD2-TP1-00011": "duplicate_quantity", "SD2-TP1-00076": "duplicate_quantity",
                  **{f"SD2-TP1-{n}": "percent_change_near_zero_baseline" for n in ("00129", "00329", "00518", "00647", "02786", "02788", "02790")}}
    assert sel["not_selected_no_reason_recorded"] == ["SD2-TP1-00017"]
    assert psel.check(sel) == []


def test_the_checks_catch_a_wrong_rung_a_missing_seed_and_a_duplicate():
    sel = psel.load()
    bad = copy.deepcopy(sel)
    bad["selected"][0]["rung"] = 3
    assert any("rung 3 but shortlist level 1" in e for e in psel.check(bad))
    bad = copy.deepcopy(sel)
    bad["not_selected_no_reason_recorded"] = []
    assert any("missing ['SD2-TP1-00017']" in e for e in psel.check(bad))
    bad = copy.deepcopy(sel)
    bad["not_selected_no_reason_recorded"] = ["SD2-TP1-00017", "SD2-TP1-00018"]
    assert "a seed is listed more than once" in psel.check(bad)


@pytest.fixture(scope="module")
def packets():
    pin = json.loads(s2.SUMMARY_PATH.read_text(encoding="utf-8"))["seeds_file"]["sha256"]
    if not s2.SEEDS_PATH.is_file() or sha256_file(s2.SEEDS_PATH) != pin:
        pytest.skip("item_seeds_v2.jsonl (gitignored) absent or not at its pin; run scripts/build_item_seeds_v2.py")
    sel = psel.load()
    want = {x["seed_id"] for x in sel["selected"]}
    seeds = {}
    with open(s2.SEEDS_PATH, encoding="utf-8") as f:
        for ln in f:
            if any(w in ln for w in want):
                s = json.loads(ln)
                if s["seed_id"] in want:
                    seeds[s["seed_id"]] = s
    records = sd.read_jsonl(r2.INGESTED_PATH)
    indep = json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    nca = sd.nca_map()
    rows = s2.statement_table(records, sd.read_jsonl(li.CLUSTERS_V1B_PATH), indep, lg.Gazetteer(nca))
    by_statement = spk.statement_lookup(records, indep)
    # synthetic grouping output: every statement a singleton, its claim type fixed by its statement type
    claim = {"mechanism": "hazard_change_mechanism", "driver": "impact_or_exposure", "consensus": "hazard_definition_or_measurement",
             "caveat": "hazard_definition_or_measurement", "pattern": "other"}
    groups = [{"group_id": f"LG-{r['arm']}-{r['statement_type']}-{n:03d}", "kind": "singleton", "statement_type": r["statement_type"],
               "label": None, "evidence_strength": r["cluster_strength"], "n_members": 1, "member_ids": [r["statement_id"]],
               "claim_about": claim[r["statement_type"]]} for n, r in enumerate(rows, 1)]
    return {x["seed_id"]: spk.build_packet(seeds[x["seed_id"]], x["rung"], f"BI-P2B-{x['order']:04d}", groups, by_statement, rows, nca, {})
            for x in psel.selected(sel)}


def test_exactly_the_ten_at_their_rungs(packets):
    assert [(k, p["use_case_level"]) for k, p in packets.items()] == ORDER
    assert [p["item_id"] for p in packets.values()] == [f"BI-P2B-{n:04d}" for n in range(1, 11)]


def test_rung_1_carries_nothing_and_rungs_3_4_only_mechanism_and_context(packets):
    for sid, p in packets.items():
        roles = [g["role"] for g in p["model_view"]["groups"]]
        claims = {g["claim_about"] for g in p["model_view"]["groups"] if g["role"] != "caveat"}
        if p["use_case_level"] == 1:
            assert roles == [] and p["excluded_groups"] == []
            continue
        assert claims <= {"hazard_change_mechanism", "hazard_definition_or_measurement"}
        assert roles.count("driver") <= 10 and roles.count("context") <= 4
        assert ("caveat" in roles) == (p["use_case_level"] == 7)
        reasons = {x["reason"] for x in p["excluded_groups"]}
        assert "claim_about:impact_or_exposure" in reasons
        assert ("caveat_outside_rung_7" in reasons) == (p["use_case_level"] != 7)


def test_packet_relevance_includes_the_recovered_us_subregion_statements(packets):
    p = packets["SD2-TP1-00589"]                 # Alabama: southeastern-U.S. statements now count (v1: `other`)
    assert p["relevance"]["geography"] == "litgeo v2" and p["relevance"]["by_basis"]["us_subregion"] > 0
    assert p["relevance"]["n_relevant_statements"] > p["relevance"]["n_relevant_statements_seed_file_v1"]
    keys = [spk.rank_key(g) for g in p["provenance"]["groups"] if g["role"] == "driver"]
    assert keys == sorted(keys)                  # DR-SEED-RANK-3
