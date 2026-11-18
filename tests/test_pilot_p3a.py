"""Work package P3a (mentor feedback 2026-11-13; D-059 -- D-065): working assumptions, descriptors v3, item seeds v3, the
fire-weather shortlist, selection v2, packets v4, the item and NCA5 overlays, and the mentor sample sheet v2.

No model call. The packets are rebuilt in memory from the pinned inputs and compared byte-for-byte with the files.
"""

from __future__ import annotations

import copy
import csv
import importlib.util
import json
import sys

import pytest
import yaml

from climrr import benchmark_items as bi
from climrr import dictionary as dc
from climrr import item_dispositions as idisp
from climrr import itemseeds as sd
from climrr import itemseeds_v3 as s3
from climrr import mentor_sheet_v2 as ms
from climrr import pattern_descriptors as pd
from climrr import pilot_selection as psel
from climrr import pilot_shortlist as ps
from climrr import plain_language as pl
from climrr import synthpackets_v4 as v4
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

RES_PATH = REPO_ROOT / "data" / "metadata" / "resolutions.yaml"
SUMMARY = json.loads(s3.SUMMARY_PATH.read_text(encoding="utf-8"))
MANIFEST = json.loads((v4.PACKETS_DIR / "manifest.json").read_text(encoding="utf-8"))
PACKETS = {p["item_id"]: json.loads((v4.PACKETS_DIR / f"{p['packet_id']}.json").read_text(encoding="utf-8")) for p in MANIFEST["packets"]}
NCA = sd.nca_map()
WA_IDS = ["WA-FWI-SUMMER", "WA-STATE-LABEL", "WA-NAME-LABEL", "WA-FWI-PCT-SCENARIO", "WA-UNWEIGHTED-MEAN"]


def _seeds():
    if not s3.SEEDS_PATH.is_file():
        pytest.fail("artifacts/benchmark/item_seeds_v3.jsonl is absent (gitignored); run scripts/build_item_seeds_v3.py")
    assert sha256_file(s3.SEEDS_PATH) == SUMMARY["seeds_file"]["sha256"]
    return {s["seed_id"]: s for s in sd.read_jsonl(s3.SEEDS_PATH)}


@pytest.fixture(scope="module")
def seeds():
    return _seeds()


# --- D-064: working assumptions in resolutions.yaml ----------------------------------------------------------------


def test_the_working_assumption_records():
    recs = dc.load_resolutions(RES_PATH.read_text(encoding="utf-8"))
    assert [r["id"] for r in recs] == [f"R-00{i}" for i in range(1, 9)]
    was = dc.working_assumptions(recs)
    assert list(was) == WA_IDS and [was[w]["resolution"] for w in WA_IDS] == ["R-004", "R-005", "R-006", "R-007", "R-008"]
    for r in recs[3:]:
        assert r["effect"] is None and r["columns"] == [] and r["decision_ref"] == "D-064" and r["date"] == "2026-11-13"
        assert r["working_assumption"]["status"] == dc.OWNER_AUTHORIZED_WORKING_ASSUMPTION
    assert was["WA-FWI-SUMMER"]["covers"] == ["IC-006", "IC-007", "IC-008", "IC-009", "IC-010"]
    assert was["WA-FWI-SUMMER"]["columns_relied_on"] == [189, 190, 191, 192, 193]
    assert "never fire occurrence" in was["WA-FWI-SUMMER"]["reading"] and "not an observation" in was["WA-FWI-SUMMER"]["reading"]


def test_a_working_assumption_moves_no_status():
    cov = {c["index"]: c for c in json.loads((REPO_ROOT / "artifacts" / "profiles" / "dictionary_coverage.json").read_text())["columns"]}
    assert all(cov[i]["status"] == "inferred_candidate" for i in (2, 3, 189, 190, 191, 192, 193))
    rec = copy.deepcopy(dc.load_resolutions(RES_PATH.read_text(encoding="utf-8"))[3])
    with pytest.raises(dc.ResolutionError, match="moves no column status"):
        dc.validate_resolution({**rec, "columns": [189], "effect": {"field": "status", "to": "owner_confirmed"}})
    with pytest.raises(dc.ResolutionError, match="must be `owner_authorized_working_assumption`"):
        dc.validate_resolution({**rec, "working_assumption": {**rec["working_assumption"], "status": "owner_confirmed"}})
    with pytest.raises(dc.ResolutionError, match="relied_on_by"):
        dc.validate_resolution({**rec, "working_assumption": {**rec["working_assumption"], "relied_on_by": "fwi"}})


# --- D-060 / D-061: plain language and descriptors v3 ---------------------------------------------------------------


def test_plain_language_phrases():
    plain = pl.load()
    assert plain["families"]["heat_index"]["quantity"] == "days hot and humid enough to be dangerous"
    assert plain["families"]["heat_index"]["quantity_short"] == "dangerous heat-index days"
    assert plain["families"]["fire_weather_index"]["quantity"] == "fire-weather danger"
    assert plain["scenario"] == {"RCP8.5": "under a high-emissions future"}
    assert plain["horizon"] == {"mid": "by mid-century", "end": "by late this century"}
    assert pl.hedge("multi_source_supported") == pl.hedge("review_supported") == ["research shows", "research has shown"]
    assert pl.hedge("single_source_supported") == ["research suggests"]


def test_descriptors_v3(seeds):
    rules = pd.load_rules(pd.RULES_V3_PATH)
    heat = pd.descriptors(seeds["SD2-TP1-00071"]["pattern"], rules)
    assert (heat["horizon"], heat["scenario"], heat["quantity"]) == ("by mid-century", "under a high-emissions future",
                                                                    "days hot and humid enough to be dangerous")
    assert heat["anchor_pair"] == "from about 15 to about 24 days a summer"
    assert pd.descriptors(seeds["SD2-TP1-00589"]["pattern"], rules)["anchor_pair"] == "from about 1 day to about 45 days a summer"
    fire = pd.descriptors(seeds["SD2-TP1-01463"]["pattern"], rules)
    assert fire["quantity"] == "fire-weather danger" and fire["magnitude_class"] == "a slight increase"
    assert fire["anchor_pair"] is None and fire["anchors"] == []
    pct = next(s for s in seeds.values() if s["metric"] == "fwi_summer_percent_change_column" and s["geography_type"] == "state")
    d = pd.descriptors(pct["pattern"], rules)
    assert d["scenario"] == "under a high-emissions future" and d["scenario_working_assumption"] == {"assumed": "RCP8.5", "resolution": "R-007"}
    for x in (heat, fire, d):
        assert bi.generality_flags(" ".join(pd.phrases(x))) == []
    v2 = pd.descriptors(seeds["SD2-TP1-00071"]["pattern"], pd.load_rules(pd.RULES_V2_PATH))
    assert v2["horizon"] == "by mid-century (2045–2054)" and v2["anchor_pair"] == "from about 15 to about 24 days"   # v2 unchanged


# --- item seeds v3 and the fire-weather shortlist ------------------------------------------------------------------


def test_seeds_v3_summary(seeds):
    assert (SUMMARY["seeds"], SUMMARY["eligible"], SUMMARY["eligible_v2"]) == (2812, 2720, 2368)
    assert SUMMARY["eligible_by_family"] == {"fire_weather_index": 1404, "heat_index": 1316}
    assert SUMMARY["became_eligible"] == 352 and SUMMARY["became_ineligible"] == 0 and SUMMARY["blockers_remaining"] == {}
    assert SUMMARY["fwi"]["acceptance_blocked_v2"] == 352 and SUMMARY["fwi"]["acceptance_blocked_v3"] == 0
    assert set(SUMMARY["eligible_by_level"]) == {"3", "4"}
    assert all(not ({1, 7} & set(s["use_case_levels_applicable"])) for s in seeds.values())


def test_seeds_v3_replace_the_fwi_blocker(seeds):
    s = seeds["SD2-TP1-01463"]
    assert s["eligible_for_pilot"] and not s["eligible_for_pilot_v2"] and s["acceptance_blockers"] == []
    p = s["pattern"]
    assert p["acceptance_blocked"] is False and p["acceptance_blocked_by_original"] == ["IC-006", "IC-007", "IC-008", "IC-009", "IC-010"]
    assert p["working_assumptions"] == ["WA-FWI-SUMMER", "WA-STATE-LABEL", "WA-UNWEIGHTED-MEAN"]
    assert {b["replaced_by"] for b in s["acceptance_blockers_replaced"]} == {"WA-FWI-SUMMER", "WA-STATE-LABEL"}
    raw = next(x for x in sd.read_jsonl(sd.PATTERNS_PATH) if x["pattern_id"] == "TP1-01463")
    assert raw["acceptance_blocked"] is True                                          # table_patterns_v1.jsonl unchanged


def test_the_fwi_shortlist_rule(seeds):
    picks = ps.fwi_select(list(seeds.values()))
    assert [(s["seed_id"], s["geography"], s["horizon"]) for s in picks] == [("SD2-TP1-01463", "California", "mid"),
                                                                            ("SD2-TP1-01654", "Minnesota", "end")]
    assert sha256_file(ps.FWI_SHORTLIST_PATH) == SUMMARY["fwi_shortlist"]["sha256"]
    rows = list(csv.DictReader(open(ps.FWI_SHORTLIST_PATH, encoding="utf-8")))
    assert [r["seed_id"] for r in rows if r["pick"] == "selected"] == ["SD2-TP1-01463", "SD2-TP1-01654"]
    first_end = ps.fwi_candidates(list(seeds.values()), "end")[0]
    assert first_end["geography"] == "California"                                     # skipped: a state already used


# --- selection v2 ---------------------------------------------------------------------------------------------------


def test_selection_v2(seeds):
    sel = psel.load(psel.SELECTION_V2_PATH)
    assert psel.check_v2(sel, seeds) == []
    xs = psel.selected(sel)
    assert [x["seed_id"] for x in xs] == ["SD2-TP1-00071", "SD2-TP1-00271", "SD2-TP1-00460", "SD2-TP1-00589", "SD2-TP1-02785",
                                         "SD2-TP1-02789", "SD2-TP1-01463", "SD2-TP1-01654"]
    assert [x["rung"] for x in xs] == [3, 3, 3, 3, 4, 4, 3, 3] and sel["owner_confirmation"].startswith("pending")
    assert psel.threshold_conflicts(sel, seeds) == MANIFEST["threshold_conflicts"]
    assert [c["place"] for c in MANIFEST["threshold_conflicts"]] == ["all_covered_nca5_regions"]
    bad = copy.deepcopy(sel)
    bad["selected"][6]["seed_id"] = "SD2-TP1-01459"
    assert any("not the shortlist rule's picks" in e for e in psel.check_v2(bad, seeds))


# --- packets v4 -------------------------------------------------------------------------------------------------------


def test_packets_v4_rebuild_byte_identically():
    b = v4.build_selection()
    for pk in b["packets"]:
        assert (v4.PACKETS_DIR / f"{pk['packet_id']}.json").read_text(encoding="utf-8") == json.dumps(pk, indent=2, ensure_ascii=False) + "\n"
    for p in MANIFEST["packets"]:
        assert sha256_file(v4.PACKETS_DIR / f"{p['packet_id']}.json") == p["sha256"]
    assert MANIFEST["inputs_sha256"] == b["hashes"]


def test_packets_v4_name_no_threshold_scenario_or_year():
    for iid, pk in PACKETS.items():
        mv = pk["model_view"]
        p = pk["provenance"]["patterns"][0]
        assert pk["version"] == "synthpackets v4" and pk["use_case_level"] in (3, 4) and "rung_instruction" not in mv
        assert bi.generality_flags(mv["patterns"][0]["text"]) == [], iid
        assert bi.generality_flags(" ".join(pk["checks_input"]["allowed_descriptors"])) == [], iid
        assert bi.generality_flags(" ".join(mv["guardrails"])) == [] and "RCP" not in json.dumps(mv["plain_language"])
        assert not set(mv["allowed_numbers"]) & ({"95", "105"} | set(p["horizon_window"].split("-")))
        assert pk["provenance"]["exact"]["scenario"] == p["scenario"] and pk["provenance"]["exact"]["horizon_window"] == p["horizon_window"]
        for g in mv["groups"]:
            assert g["hedge"] == pl.hedge(g["evidence_strength"])


def test_packets_v4_fire_groups_and_overlays():
    for iid, pk in PACKETS.items():
        g = pk["provenance"]["groups"]
        if pk["family"] == "fire_weather_index":
            assert pk["fire_groups_unreviewed"] is True and g and all(x["review_state"] == "unreviewed_agent_tag" for x in g)
            assert [w["id"] for w in pk["working_assumptions_relied_on"]] == ["WA-FWI-SUMMER", "WA-STATE-LABEL", "WA-UNWEIGHTED-MEAN"]
        else:
            assert pk["fire_groups_unreviewed"] is False and all(x["disposition"] is not None for x in g)
            ov = next(x for x in g if x["group_id"] == "LG-extreme_heat_v1-driver-c1-008")
            assert ov["label"].startswith("Large-scale warming") and ov["label_override"]["origin"] == "reviewer"
            m = next(m for m in ov["members"] if m["statement_id"] == "LS-199098498-04")
            assert m["statement"].startswith("Citing Schoof") and m["span_start"] == 4602
        assert pk["inputs_sha256"]["nca_map"] == sd.NCA_MAP_SHA256
        assert pk["inputs_sha256"]["nca_regions_disposition"] == sha256_file(v4.NCA_DISPOSITION_PATH)
    listed = {p["packet_id"]: p["fire_groups_attached"] for p in MANIFEST["packets"]}
    assert [len(listed[k]) for k in ("PK-SD2-TP1-01463", "PK-SD2-TP1-01654")] == [14, 14]


# --- D-059 / D-065 overlays ------------------------------------------------------------------------------------------


def test_item_design_dispositions():
    doc = idisp.load()
    assert idisp.check(doc) == []
    run2 = REPO_ROOT / "artifacts" / "benchmark" / "items" / "run2" / "items"
    for iid in ("BI-P2B-0001", "BI-P2B-0002"):
        it = json.loads((run2 / f"{iid}.json").read_text(encoding="utf-8"))
        assert it["review"]["status"] == "human_review" and idisp.effective_status(it, doc) == "rejected_by_design (D-059)"
    it = json.loads((run2 / "BI-P2B-0003.json").read_text(encoding="utf-8"))
    assert idisp.effective_status(it, doc) == "human_review"


def test_nca_disposition_sidecar():
    doc = yaml.safe_load(v4.NCA_DISPOSITION_PATH.read_text(encoding="utf-8"))
    assert doc["map"]["sha256"] == sd.NCA_MAP_SHA256 == sha256_file(REPO_ROOT / doc["map"]["path"])
    assert doc["owner_disposition"] == "accepted_as_project_grouping (2026-11-13)" and doc["map"]["source_verification"] == "pending"
    assert "source_verification: pending_kaiyuan" in (REPO_ROOT / doc["map"]["path"]).read_text(encoding="utf-8")


# --- mentor sample sheet v2 ------------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def run_dirs(tmp_path_factory):
    """A synthesis run (heat BI-P3-0001 and fire BI-P3-0007, from the v4 agent's assemble / finish) and a polish run of
    the heat item."""
    pytest.importorskip("duckdb")
    tools = REPO_ROOT / "scripts" / "litcollect"
    sys.path.insert(0, str(tools))
    sys.path.insert(0, str(REPO_ROOT / "tests"))
    spec = importlib.util.spec_from_file_location("litsynth_agent_v4_sheet", tools / "litsynth_agent.py")
    a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(a)
    from test_litsynth_agent_v4 import fire_reply, heat_reply
    base = tmp_path_factory.mktemp("sheet")
    synth, polish = base / "run4" / "items", base / "polish1" / "items"
    synth.mkdir(parents=True)
    polish.mkdir(parents=True)
    for iid, reply in (("BI-P3-0001", heat_reply), ("BI-P3-0007", fire_reply)):
        pk = PACKETS[iid]
        common = {"model": "m", "prompt_hash": "0" * 64, "generation_timestamp": "2026-11-17T00:00:00Z",
                  "packet_sha256": next(p["sha256"] for p in MANIFEST["packets"] if p["item_id"] == iid), "system_prompt_sha256": "0" * 64}
        it, tagged = a.assemble(reply(pk), pk, common, bi.column_names())
        it = a.finish(it, tagged, pk, common, bi.column_names())
        assert it["review"]["status"] == "deterministic_pass", it["review"]["history"][0]["reasons"]
        (synth / f"{pk['seed_id']}.json").write_text(json.dumps(it), encoding="utf-8")
        if iid == "BI-P3-0001":
            pol = copy.deepcopy(it)
            pre = {"prompt": it["prompt"], "answer": it["reference_answer"]["integrated"]}
            pol["prompt"] = "How will days hot and humid enough to be dangerous change in California by mid-century, and why?"
            pol["review"]["history"].append({"event": "polish", "status": "polished", "pre_polish": pre})
            (polish / f"{pk['seed_id']}.json").write_text(json.dumps(pol), encoding="utf-8")
    return base / "run4", base / "polish1"


def test_mentor_sheet_rows(run_dirs):
    items = ms.load_items(MANIFEST, *run_dirs)
    assert {k: v[1] for k, v in items.items()} == {"BI-P3-0001": "polish", "BI-P3-0007": "synthesis"}
    rs = ms.rows(MANIFEST, PACKETS, items)
    assert rs[0] == ["#", "Question", "Answer", "Table side", "Paper side", "Original passages"] and len(rs) == 3
    heat, fire = rs[1], rs[2]
    assert heat[0] == "1\nBI-P3-0001" and heat[1].startswith("How will days hot and humid")
    assert "threshold 95 °F" in heat[3] and "scenario: RCP8.5" in heat[3] and "2045-2054" in heat[3]
    assert "heatindex_HIS_Day95 (240)" in heat[3] and "WA-STATE-LABEL (R-005)" in heat[3]
    assert heat[4].startswith("Research shows: Large-scale warming") and "Research suggests: humidity magnifies" in heat[4]
    assert "Citing Schoof" not in heat[5] and "Schoof et al 2019" in heat[5]                 # the verbatim corrected passage
    assert fire[0] == "7\nBI-P3-0007" and "WA-FWI-SUMMER (R-004)" in fire[3] and "not yet human-reviewed" in fire[4]
    md = ms.render_md(rs, items)
    assert "<small>Before the readability polish: How are days hot and humid" in md and len(ms.README_LINES) == 3
    assert "What 'research suggests' means" in md


def test_build_mentor_sheet_script(run_dirs, tmp_path, monkeypatch, capsys):
    from climrr import runrecord as rr
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path / "runs")
    md, xlsx = tmp_path / "sheet.md", tmp_path / "sheet.xlsx"
    spec = importlib.util.spec_from_file_location("build_mentor_sheet", REPO_ROOT / "scripts" / "build_mentor_sheet.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(sys, "argv", ["build_mentor_sheet.py", "--items", str(run_dirs[0]), "--polished", str(run_dirs[1]),
                                      "--out-md", str(md), "--out-xlsx", str(xlsx)])
    assert mod.main() == 0
    out = json.loads(capsys.readouterr().out.split("\nrun record:")[0])
    assert out["rows"] == 2 and out["missing"] == ["BI-P3-0002", "BI-P3-0003", "BI-P3-0004", "BI-P3-0005", "BI-P3-0006", "BI-P3-0008"]
    assert out["polish_status"] == {"BI-P3-0001": "polished", "BI-P3-0007": None}
    assert md.read_text(encoding="utf-8").startswith("# Sample items for mentor review --- v2") and xlsx.stat().st_size > 0
    assert len(list((tmp_path / "runs").glob("*_build_mentor_sheet.json"))) == 1
