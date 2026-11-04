"""Mentor sheet v2 (2026-11-03): provenance correction LS-199098498-04 (D-057), DR-DESC-1 v2 (D-055c), edited answers v2.

Checks: the corrections file pinned and consistent with the recorded statement; the overlay changes one statement record
and no file; `reslice_correction` on synthetic papers; driver-c1-008's strength recomputed (group file and every packet);
the items that get `provenance_corrections_applied`; v1 rules still reproduce every frozen packet's descriptors and v2
changes only the two classes named; the v2 texts (questions carried from v1 where the work package gives none); the support
map v2 clauses verbatim; the applied overlay, the workbook v3 CSV, the checks report and the mentor Markdown rebuilt
from their inputs.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os

import pytest

from climrr import itemseeds as sd
from climrr import litstatements as ls
from climrr import litsynth_run2 as s2
from climrr import litsynth_run3 as s3
from climrr import p2b_items_review as rv
from climrr import p2b_mentor_export as mx
from climrr import p2b_mentor_v2 as m2
from climrr import pattern_descriptors as pd
from climrr.checksums import sha256_file
from climrr.manifest import load_entry

MENTOR_IDS = ["BI-P2B-0001", "BI-P2B-0003", "BI-P2B-0006", "BI-P2B-0007", "BI-P2B-0010"]
CID = "LS-199098498-04"
GID = "LG-extreme_heat_v1-driver-c1-008"
V2_BUILD = "7825fcf"  # the mentor sheet v2 build; the workbook v3 CSV and the mentor Markdown are rebuilt in place by v3


def _rel(path):
    return path.relative_to(mx.REPO_ROOT).as_posix()


@pytest.fixture(scope="module")
def current():
    return s3.current_items()


@pytest.fixture(scope="module")
def packets(current):
    return {it["item_id"]: s2.packet_for_item(it) for it in current}


@pytest.fixture(scope="module")
def corrections():
    return ls.load_provenance_corrections()


@pytest.fixture(scope="module")
def statements():
    return {r["statement_id"]: r for r in ls.load_statements(mx.STATEMENTS_INGESTED_PATH)}


@pytest.fixture(scope="module")
def applied():
    return json.loads(m2.APPLIED_PATH.read_text(encoding="utf-8"))


def _need(path, what):
    if not path.is_file():
        if os.environ.get("CLIMRR_ALLOW_MISSING_RAW") == "1":
            pytest.skip(f"{what} absent and CLIMRR_ALLOW_MISSING_RAW=1 is set")
        pytest.fail(f"{what} is absent (gitignored); regenerate it, or set CLIMRR_ALLOW_MISSING_RAW=1 for code-only work")


# --- A: the correction ------------------------------------------------------------------------------------------------


def test_corrections_file_is_pinned_and_matches_the_record(corrections, statements):
    assert load_entry("provenance_corrections_v1.yaml")["sha256"] == sha256_file(ls.CORRECTIONS_PATH)
    (c,) = corrections
    r = statements[CID]
    assert c["statement_id"] == CID and c["paper_item_id"] == r["paper_item_id"] == "199098498"
    assert c["paper_sha256"] == r["paper_sha256"]
    assert c["original_passage"] == r["verbatim_passage"] and c["original_passage"].endswith("is beyond the scope of this study.")
    assert c["original_passage_type"] == r["proposal"]["passage_type"] == "cited_finding" == c["corrected_passage_type"]
    assert c["original_evidence"] == r["evidence"] and c["original_recovery"] == r["passage_recovery"] == "prefix_anchor"
    assert c["corrected_passage"].startswith("However, recent work examining") and c["corrected_passage"].endswith("(Schoof et al 2019).")
    assert c["corrected_section_key"] == r["proposal"]["section_key"] == "late century results"


def test_overlay_changes_one_record_and_keeps_the_original(corrections, statements):
    recs = list(statements.values())
    out = ls.apply_provenance_corrections(recs, corrections)
    changed = [b for a, b in zip(recs, out) if a != b]
    assert [x["statement_id"] for x in changed] == [CID] and statements[CID]["verbatim_passage"] == corrections[0]["original_passage"]
    x = changed[0]
    assert x["verbatim_passage"] == corrections[0]["corrected_passage"] and x["proposal"]["passage_type"] == "cited_finding"
    assert x["evidence"] == {"json_path": "$.late century results", "section_idx": None, "span_start": None, "span_end": None}
    pc = x["provenance_correction"]
    assert pc["reslice"] == ls.RESLICE_PENDING and pc["original_passage"] == corrections[0]["original_passage"] and pc["decision"] == "D-057"
    # applying twice is the same as once; a foreign passage is refused
    assert ls.apply_provenance_corrections(out, corrections) == ls.apply_provenance_corrections(recs, corrections)
    bad = dict(statements[CID], verbatim_passage="something else entirely")
    with pytest.raises(ValueError):
        ls.apply_provenance_corrections([bad], corrections)


def _paper(c, before="Intro text. ", extra_key=True):
    sec = before + c["original_passage"] + " " + c["corrected_passage"] + " Tail."
    obj = {"title": "T"}
    if extra_key:
        obj["numbers"] = [1, 2]
    obj[c["corrected_section_key"]] = sec
    return obj, json.dumps(obj).encode("utf-8")


def test_reslice_correction_on_synthetic_papers(corrections):
    c0 = corrections[0]
    obj, raw = _paper(c0)
    sec = obj[c0["corrected_section_key"]]
    c = dict(c0, paper_sha256=hashlib.sha256(raw).hexdigest(),
             original_evidence={**c0["original_evidence"], "span_start": sec.index(c0["original_passage"]),
                                "span_end": sec.index(c0["original_passage"]) + len(c0["original_passage"])})
    r = ls.reslice_correction(c, raw)
    assert r["reslice"] == "exact" and r["section_idx"] == 2 and r["occurrences"] == 1 and r["original_reslices"] is True
    assert sec[r["span_start"]:r["span_end"]] == c0["corrected_passage"]
    assert ls.reslice_correction(c0, raw)["reslice"] == "paper_sha256_mismatch"
    obj2 = dict(obj, **{c0["corrected_section_key"]: "nothing here"})
    raw2 = json.dumps(obj2).encode("utf-8")
    assert ls.reslice_correction(dict(c, paper_sha256=hashlib.sha256(raw2).hexdigest()), raw2)["reslice"] == "not_found"
    out = ls.apply_provenance_corrections([{"statement_id": CID, "verbatim_passage": c0["original_passage"],
                                            "json_path": "$.x", "span_start": 1, "span_end": 2}], [c], {CID: r})
    assert (out[0]["span_start"], out[0]["span_end"], out[0]["json_path"]) == (r["span_start"], r["span_end"], "$.late century results")


def test_group_strength_after_correction(corrections, current, packets):
    rec = m2.applied_record(corrections, current, packets, {})
    (g,) = rec["groups"]
    assert g["group_id"] == GID and g["strength_before"] == g["strength_after"] == "multi_source_supported" and g["stays_multi_source"]
    assert g["core_cited_papers_after"] == ["158091651", "199098498", "5838629"]
    assert [m["corrected"] for m in g["members"]].count(True) == 1
    per = {p["item_id"]: p for p in g["per_packet"]}
    assert sorted(per) == [f"BI-P2B-{i:04d}" for i in range(3, 11)]
    assert all(p["strength_after"] == "multi_source_supported" and p["unchanged"] for p in per.values())
    two = [i for i, p in per.items() if p["core_cited_papers_after"] == ["199098498", "5838629"]]
    assert two == ["BI-P2B-0004", "BI-P2B-0005", "BI-P2B-0006", "BI-P2B-0010"]
    assert [x["item_id"] for x in rec["items"]] == sorted(per) and all(x["provenance_corrections_applied"] == [CID] for x in rec["items"])
    # the overlay leaves the loaded items untouched
    assert all("provenance_corrections_applied" not in it["reference_components"] for it in current)


def test_item_with_corrections(corrections, current):
    it = next(x for x in current if x["item_id"] == "BI-P2B-0006")
    before = copy.deepcopy(it)
    o = m2.item_with_corrections(it, corrections, {})
    assert it == before and o["reference_components"]["provenance_corrections_applied"] == [CID]
    sups = [x for s in o["reference_components"]["literature_mechanisms"] for x in s["supports"] if x["statement_id"] == CID]
    assert sups and all(x["verbatim_passage"] == corrections[0]["corrected_passage"] and x["span_start"] is None for x in sups)
    g = next(x for x in current if x["item_id"] == "BI-P2B-0001")
    assert "provenance_corrections_applied" not in m2.item_with_corrections(g, corrections, {})["reference_components"]


def test_applied_overlay_rebuilds(corrections, current, packets, statements, applied):
    reslices = m2.local_reslices(corrections, statements)
    assert m2.applied_record(corrections, current, packets, reslices) == applied
    assert applied["files_modified"] == 0 and applied["reslices"][CID]["reslice"] in (ls.RESLICE_PENDING, "exact")
    if applied["reslices"][CID]["reslice"] == ls.RESLICE_PENDING:
        assert "sources/full_705k_v2_filtered/98/199098498.json" in applied["reslices"][CID]["polaris_command"]


# --- B: DR-DESC-1 v2 ----------------------------------------------------------------------------------------------------


def test_v1_rules_still_reproduce_every_packet(current, packets):
    r1 = pd.load_rules()
    for it in current:
        ps = packets[it["item_id"]]["checks_input"]["allowed_descriptors"]
        p = it["reference_components"]["table_patterns"][0]
        assert pd.phrases(pd.descriptors(p, r1)) == ps, it["item_id"]


def test_v2_rules_pinned_and_mentor_descriptors(current):
    assert load_entry("descriptor_rules_v2.yaml")["sha256"] == sha256_file(pd.RULES_V2_PATH)
    d = m2.descriptors_v2({it["item_id"]: it for it in current}, MENTOR_IDS)
    assert {k: v["changed"] for k, v in d.items() if v["changed"]} == {
        "BI-P2B-0006": ["anchor_pair", "magnitude_class", "magnitude_note"], "BI-P2B-0007": ["negligible_regions", "smallest"]}
    a = d["BI-P2B-0006"]["v2"]
    assert (a["magnitude_class"], a["anchor_pair"], a["anchors"]) == ("rising from rare to common", "from about 1 day to about 45 days",
                                                                   ["about 1 day", "about 45 days"])
    assert d["BI-P2B-0006"]["v1"]["magnitude_class"] == "more than tripling"
    b = d["BI-P2B-0007"]["v2"]
    assert b["negligible_regions"] == ["Alaska"] and b["smallest"] == "essentially no change: Alaska"
    assert b["largest"] == "the largest increase: Southeast"


def _pat(mf, mt, direction="increase"):
    return {"pattern_id": "X", "pattern_kind": "single", "metric": "heatindex_days_above_105F", "metric_wording": "above 105 F",
            "horizon": "end", "horizon_window": "2085-2094", "scenario": "RCP8.5", "direction": direction,
            "computed_value_or_range": {"mean_from": mf, "mean_to": mt, "unit": "days"}}


def test_v2_rare_to_common_class():
    r1, r2 = pd.load_rules(), pd.load_rules(pd.RULES_V2_PATH)
    d = pd.descriptors(_pat("0.2", "11.4"), r2)
    assert d["magnitude_class"] == "rising from rare to common" and d["anchor_pair"] == "from essentially none to about 11 days"
    assert pd.descriptors(_pat("0.2", "11.4"), r1)["magnitude_class"] == "from rare or no such days to about 11 days"
    assert pd.descriptors(_pat("1.9", "3.0"), r2)["magnitude_class"] == "rising from rare to common"           # baseline < 2
    assert pd.descriptors(_pat("2.0", "3.0"), r2)["magnitude_class"] == "a moderate increase (about half again as many)"
    assert pd.descriptors(_pat("3.0", "31.0"), r2)["anchor_pair"] == "from about 3 days to about 31 days"      # ratio > 10
    assert pd.descriptors(_pat("3.0", "30.0"), r2)["magnitude_class"] == "more than tripling"                   # ratio = 10
    assert pd.descriptors(_pat("1.0", "0.5", "decrease"), r2)["magnitude_class"] is None


def test_v2_negligible_regions():
    p = {"pattern_id": "R", "pattern_kind": "regional_contrast", "metric": "heatindex_days_above_95F", "metric_wording": "above 95 F",
         "horizon": "mid", "horizon_window": "2045-2054", "scenario": "RCP8.5", "direction": "increase",
         "computed_value_or_range": {"regions_ordered": [{"name": "A", "value": "3.0"}, {"name": "B", "value": "0.04"},
                                                         {"name": "C", "value": "-0.049"}]}}
    r1, r2 = pd.load_rules(), pd.load_rules(pd.RULES_V2_PATH)
    assert pd.descriptors(p, r2)["negligible_regions"] == ["B", "C"] and pd.descriptors(p, r2)["smallest"] == "essentially no change: B, C"
    assert "negligible_regions" not in pd.descriptors(p, r1) and pd.descriptors(p, r1)["smallest"] == "the smallest increase: C"


# --- C: edited answers v2 -----------------------------------------------------------------------------------------------


def test_edits_v2():
    e1, e2 = mx.edits(), m2.edits_v2()
    assert list(e2) == MENTOR_IDS and {e["edit_origin"] for e in e2.values()} == {"coordinator_proposed_v2"}
    assert e2["BI-P2B-0001"]["edited_prompt"] == e1["BI-P2B-0001"]["edited_prompt"]
    assert e2["BI-P2B-0001"]["edited_reference_integrated"] == e1["BI-P2B-0001"]["edited_reference_integrated"]
    assert [i for i in MENTOR_IDS if e2[i]["edited_prompt"] != e1[i]["edited_prompt"]] == ["BI-P2B-0007"]
    assert "where is the change smallest" in e2["BI-P2B-0007"]["edited_prompt"]
    for i in MENTOR_IDS[1:]:
        assert e2[i]["edited_reference_integrated"] != e1[i]["edited_reference_integrated"]
    assert "table used here" not in e2["BI-P2B-0010"]["edited_reference_integrated"]
    assert not any("urban" in e2[i]["edited_reference_integrated"].lower() for i in MENTOR_IDS)


def test_support_map_v2_and_checks():
    ed, smap = m2.edits_v2(), m2.support_map_v2()
    assert sorted(smap) == sorted(MENTOR_IDS)
    v = m2.clause_verdicts(ed, smap)
    assert {k: len(x) for k, x in v.items()} == {"supported": 17, "guardrail": 2, "partially_supported": 5,
                                                 "supported_by_uncited_packet_group": 3}
    assert "not_supported_by_verbatim_passage" not in v
    leak = m2.edited_texts_check(ed)
    assert not any(x["prompt"] or x["reference_integrated"] for x in leak)


# --- D: workbook v3 and the mentor sheet v2 -----------------------------------------------------------------------------


def test_items_csv_v3_rebuilds(applied):
    # the tracked CSV carries the v3 texts since the mentor sheet v3 package (tests/test_mentor_v3.py); the v2-text build is
    # compared with the file as committed at the mentor sheet v2 build 7825fcf
    man2, man3, index, items, packets, lint, notes, item_sha = rv.inputs_v2()
    sheets = rv.workbook_sheets_v3(man2, man3, index, items, packets, lint, notes, item_sha, m2.edits_v2(), applied)
    rows = next(r for n, r, _ in sheets if n == "ITEMS")
    assert rv.items_csv(rows) == s2.git_blob(V2_BUILD, _rel(rv.ITEMS_CSV_V3_PATH)).decode("utf-8")
    h = rows[0]
    assert [r[0] for r in rows[1:] if r[h.index(rv.EDIT_ORIGIN_COL)] == "coordinator_proposed_v2"] == MENTOR_IDS
    assert all(r[h.index("kaiyuan_disposition")] == "" for r in rows[1:])            # nothing confirmed, nothing frozen
    ov = dict((r[0], r[1]) for r in next(r for n, r, _ in sheets if n == "OVERVIEW"))
    assert "COORDINATOR-proposed edits" not in ov and CID in ov["provenance corrections (D-057)"]


def test_mentor_md_v2_rebuilds(current, corrections, applied):
    _need(sd.PATTERNS_PATH, "artifacts/benchmark/table_patterns_v1.jsonl")
    items = {it["item_id"]: it for it in current}
    ed, smap = m2.edits_v2(), m2.support_map_v2()
    descs = m2.descriptors_v2(items, list(ed))
    rows = m2.mentor_rows_v2(items, ed, smap, corrections, applied["reslices"], descs)
    md = m2.render_md_v2(rows)
    assert md == s2.git_blob(V2_BUILD, _rel(mx.MENTOR_MD_PATH)).decode("utf-8")  # the tracked Markdown is v3 since then
    assert "provenance note" not in md and md.count(m2.CORRECTED_NOTE) == 4
    assert corrections[0]["original_passage"] not in md and md.count(corrections[0]["corrected_passage"]) == 4
    assert m2.README_V2_LINES[:-1] == mx.README_LINES and "one study, citing earlier work" in m2.README_V2_LINES[-1][1]
    by_id = {r[0].split("\n")[1]: r for r in rows[1:]}
    assert "U.S. Caribbean; Hawai'i and U.S.-Affiliated Pacific Islands" in by_id["BI-P2B-0007"][3]
    assert "mean 1.4 days -> 45.2 days" in by_id["BI-P2B-0006"][3]
    checks = m2.checks_record(ed, smap, descs, m2.edited_texts_check(ed))
    assert checks == json.loads(m2.CHECKS_V2_PATH.read_text(encoding="utf-8")) and checks["leakage_hits"] == []
