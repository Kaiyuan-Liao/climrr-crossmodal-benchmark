"""Mentor sheet v3 (2026-11-03, final for 2026-11-05): corrections v1a (D-057 closed, D-058), texts v3, mentor sheet v3.

Checks: v1a pinned, a superset of v1 with the work package's re-slice, corrected statement and label override; the
recorded re-slice consistent with the passage; the statement and label overlays (originals kept, statement_type and the
group's strength unchanged, no file modified); the v3 texts differ from v2 only by the four named substitutions; the
support map v3 (the five v2 partial clauses re-read and supported); leakage v2.3 on the v3 texts; the applied overlay, the
workbook v3 CSV, the checks report and the mentor Markdown rebuilt from their inputs; the xlsx small run.
"""

from __future__ import annotations

import json
import os
import zipfile

import pytest

from climrr import itemseeds as sd
from climrr import litstatements as ls
from climrr import litsynth_run2 as s2
from climrr import litsynth_run3 as s3
from climrr import p2b_items_review as rv
from climrr import p2b_mentor_export as mx
from climrr import p2b_mentor_v2 as m2
from climrr import p2b_mentor_v3 as m3
from climrr.checksums import sha256_file
from climrr.manifest import load_entry
from climrr.xlsxlite import Rich, _cell

MENTOR_IDS = ["BI-P2B-0001", "BI-P2B-0003", "BI-P2B-0006", "BI-P2B-0007", "BI-P2B-0010"]
CID = "LS-199098498-04"
GID = "LG-extreme_heat_v1-driver-c1-008"
CORRECTED_STATEMENT = ("Citing Schoof et al. (2019), the paper reports that large-scale warming, rather than changes in regional "
                       "circulation, is the primary driver of future changes in extreme heat.")
REVIEWER_LABEL = "Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat"
SUBSTITUTIONS = {
    "BI-P2B-0003": [("Warming is the main driver:", "Warming drives the change:"),
                    ("a stronger factor in sustaining heat waves in the Southwest",
                     "a stronger factor in sustaining heat waves at southern latitudes")],
    "BI-P2B-0010": [("Warming is the main driver:", "Warming drives the change:"),
                    ("The change is scenario-dependent: one study of the eastern United States reports heat-wave duration almost one day longer",
                     "Projections differ between emissions pathways: one study reports heat-wave duration almost one day longer")]}


@pytest.fixture(scope="module")
def current():
    return s3.current_items()


@pytest.fixture(scope="module")
def packets(current):
    return {it["item_id"]: s2.packet_for_item(it) for it in current}


@pytest.fixture(scope="module")
def v1a():
    return m3.corrections_v1a()


@pytest.fixture(scope="module")
def statements():
    return {r["statement_id"]: r for r in ls.load_statements(mx.STATEMENTS_INGESTED_PATH)}


@pytest.fixture(scope="module")
def applied():
    return json.loads(m3.APPLIED_V1A_PATH.read_text(encoding="utf-8"))


def _need(path, what):
    if not path.is_file():
        if os.environ.get("CLIMRR_ALLOW_MISSING_RAW") == "1":
            pytest.skip(f"{what} absent and CLIMRR_ALLOW_MISSING_RAW=1 is set")
        pytest.fail(f"{what} is absent (gitignored); regenerate it, or set CLIMRR_ALLOW_MISSING_RAW=1 for code-only work")


# --- A: corrections v1a -----------------------------------------------------------------------------------------------


def test_v1a_pinned_and_a_superset_of_v1(v1a):
    assert load_entry("provenance_corrections_v1a.yaml")["sha256"] == sha256_file(ls.CORRECTIONS_V1A_PATH)
    assert load_entry("provenance_corrections_v1.yaml")["sha256"] == sha256_file(ls.CORRECTIONS_PATH)   # v1 kept
    (c,), (o,) = v1a
    (c1,) = ls.load_provenance_corrections()
    assert all(c[k] == v for k, v in c1.items())
    assert {k: c[k] for k in set(c) - set(c1)} == {
        "reslice": "exact", "json_path": "$.late century results", "section_idx": 8, "span_start": 4602, "span_end": 5001,
        "occurrences": 1, "original_reslices": True, "paper_sha256_match": True, "verified_on": "polaris, 2026-11-03, Kaiyuan",
        "corrected_statement": CORRECTED_STATEMENT, "corrected_statement_type": "cited_finding"}
    assert o == {"group_id": GID, "label": REVIEWER_LABEL, "agent_label": "Observed increase in heat‑wave and drought frequency",
                 "origin": "reviewer", "decision": "D-058"}


def test_recorded_reslice_is_consistent(v1a, statements):
    (c,), _ = v1a
    rs = m3.reslices_v1a([c], statements)[CID]
    assert rs["reslice"] == "exact" and rs["span_end"] - rs["span_start"] == len(c["corrected_passage"]) == 399
    assert rs["span_start"] == c["original_evidence"]["span_end"] + 1          # the next sentence of the same section
    assert ls.recorded_reslice(ls.load_provenance_corrections()[0]) is None     # v1 records no re-slice
    with pytest.raises(ValueError):
        m3.reslices_v1a([dict(c, span_end=5000)], statements)
    with pytest.raises(ValueError):
        m3.reslices_v1a([dict(c, occurrences=2)], statements)


def test_statement_overlay(v1a, statements):
    (c,), _ = v1a
    recs = list(statements.values())
    out = ls.apply_provenance_corrections(recs, [c], m3.reslices_v1a([c], statements), ls.CORRECTIONS_V1A_PATH.name)
    (x,) = [b for a, b in zip(recs, out) if a != b]
    assert x["proposal"]["statement"] == CORRECTED_STATEMENT and x["proposal"]["statement_type"] == "driver"   # type unchanged
    assert x["evidence"] == {"json_path": "$.late century results", "section_idx": 8, "span_start": 4602, "span_end": 5001}
    pc = x["provenance_correction"]
    assert pc["original_statement"] == statements[CID]["proposal"]["statement"] and pc["corrected_statement_type"] == "cited_finding"
    assert pc["reslice"] == "exact" and pc["correction_file"] == "provenance_corrections_v1a.yaml"
    again = ls.apply_provenance_corrections(out, [c])[recs.index(statements[CID])]
    assert again["provenance_correction"]["original_statement"] == statements[CID]["proposal"]["statement"]  # agent's kept
    # a packet member (top-level `statement`)
    m = {"statement_id": CID, "paper_item_id": "199098498", "statement": "agent text", "verbatim_passage": c["original_passage"],
         "passage_type": "cited_finding"}
    (y,) = ls.apply_provenance_corrections([m], [c])
    assert y["statement"] == CORRECTED_STATEMENT and y["provenance_correction"]["original_statement"] == "agent text"


def test_label_overlay(v1a, packets):
    _, (o,) = v1a
    groups = [g for g in m2._jsonl(m2.GROUPS_ENRICHED_PATH)]
    out = ls.apply_group_label_overrides(groups, [o])
    (g,) = [b for a, b in zip(groups, out) if a != b]
    assert g["group_id"] == GID and g["label"] == REVIEWER_LABEL and g["label_override"]["agent_label"] == o["agent_label"]
    assert ls.apply_group_label_overrides(out, [o]) == out
    with pytest.raises(ValueError):
        ls.apply_group_label_overrides([dict(g, label="something else")], [o])
    pk = packets["BI-P2B-0003"]["provenance"]["groups"]
    assert [x["label"] for x in ls.apply_group_label_overrides(pk, [o]) if x["group_id"] == GID] == [REVIEWER_LABEL]


def test_applied_v1a_rebuilds(v1a, current, packets, statements, applied):
    corrections, overrides = v1a
    rec = m3.applied_record_v1a(corrections, overrides, current, packets, m3.reslices_v1a(corrections, statements), m3.support_map_v3())
    assert rec == applied and applied["files_modified"] == 0
    assert applied["corrections_file"]["sha256"] == sha256_file(ls.CORRECTIONS_V1A_PATH)
    (g,) = applied["groups"]
    assert g["group_id"] == GID and g["stays_multi_source"] and g["strength_after"] == "multi_source_supported"
    assert [x["item_id"] for x in applied["items"]] == [f"BI-P2B-{i:04d}" for i in range(3, 11)]
    (u,), (lu,) = applied["uses"]["corrections"], applied["uses"]["group_label_overrides"]
    assert u["applied_in"]["mentor_sheet_paper_side"]["items"] == MENTOR_IDS[1:]
    assert lu["applied_in"]["mentor_sheet_paper_side"]["items"] == MENTOR_IDS[1:]
    assert lu["original_unchanged_in"]["packets (by item)"] == [f"BI-P2B-{i:04d}" for i in range(3, 11)]
    assert applied["corrected_statements"][0]["proposal"]["statement"] == CORRECTED_STATEMENT


# --- B: texts v3 ------------------------------------------------------------------------------------------------------


def test_texts_v3_are_v2_plus_the_named_substitutions():
    e2, e3 = m2.edits_v2(), m3.edits_v3()
    assert list(e3) == MENTOR_IDS and {e["edit_origin"] for e in e3.values()} == {"coordinator_proposed_v3"}
    for iid in MENTOR_IDS:
        assert e3[iid]["edited_prompt"] == e2[iid]["edited_prompt"]
        text = e2[iid]["edited_reference_integrated"]
        for a, b in SUBSTITUTIONS.get(iid, []):
            assert text.count(a) == 1
            text = text.replace(a, b)
        assert e3[iid]["edited_reference_integrated"] == text, iid
    assert not any("main driver" in e3[i]["edited_reference_integrated"] for i in MENTOR_IDS)


def test_support_map_v3_and_leakage():
    ed, smap = m3.edits_v3(), m3.support_map_v3()
    v = m2.clause_verdicts(ed, smap)
    assert {k: len(x) for k, x in v.items()} == {"supported": 22, "guardrail": 2, "supported_by_uncited_packet_group": 3}
    assert not any(c.get("conditional_on") for x in smap.values() for c in x["clauses"])
    # the five v2 partial clauses are gone; their v3 replacements are supported
    v2 = m2.checks_record(m2.edits_v2(), m2.support_map_v2(), {}, [])["not_fully_supported"]["partially_supported"]
    assert len(v2) == 5
    changed = m3.checks_record_v3(ed, smap, {}, [])["clauses_changed_since_v2"]
    assert sorted((x["item_id"], x["clause"]) for x in changed["removed"]) == sorted((x["item_id"], x["clause"]) for x in v2)
    assert len(changed["added"]) == 5 and {x["verdict_v3"] for x in changed["added"]} == {"supported"}
    leak = m2.edited_texts_check(ed)
    assert not any(x["prompt"] or x["reference_integrated"] for x in leak)


# --- C: workbook v3 and the mentor sheet v3 -----------------------------------------------------------------------------


def test_items_csv_v3_texts_rebuilds(applied):
    man2, man3, index, items, packets, lint, notes, item_sha = rv.inputs_v2()
    sheets = rv.workbook_sheets_v3(man2, man3, index, items, packets, lint, notes, item_sha, m3.edits_v3(), applied, texts="v3")
    rows = next(r for n, r, _ in sheets if n == "ITEMS")
    assert rv.items_csv(rows) == rv.ITEMS_CSV_V3_PATH.read_text(encoding="utf-8")
    h = rows[0]
    assert [r[0] for r in rows[1:] if r[h.index(rv.EDIT_ORIGIN_COL)] == "coordinator_proposed_v3"] == MENTOR_IDS
    assert all(r[h.index("kaiyuan_disposition")] == "" for r in rows[1:])            # nothing confirmed, nothing frozen
    ov = dict((r[0], r[1]) for r in next(r for n, r, _ in sheets if n == "OVERVIEW"))
    assert "reslice exact" in ov["provenance corrections (D-057)"] and REVIEWER_LABEL in ov["group label overrides (D-058)"]


def test_mentor_md_v3_rebuilds(current, v1a, applied):
    _need(sd.PATTERNS_PATH, "artifacts/benchmark/table_patterns_v1.jsonl")
    corrections, overrides = v1a
    items = {it["item_id"]: it for it in current}
    ed, smap = m3.edits_v3(), m3.support_map_v3()
    descs = m2.descriptors_v2(items, list(ed))
    rows = m3.mentor_rows_v3(items, ed, smap, corrections, overrides, applied["reslices"], descs)
    md = m3.render_md_v3(rows)
    assert md == mx.MENTOR_MD_PATH.read_text(encoding="utf-8")
    v2_md = s2.git_blob("7825fcf", mx.MENTOR_MD_PATH.relative_to(mx.REPO_ROOT).as_posix()).decode("utf-8")
    assert md.count(f"{REVIEWER_LABEL} <small>(agent label: {overrides[0]['agent_label']})</small>") == 4
    assert md.count(CORRECTED_STATEMENT + m2.STATEMENT_NOTE) == 4 and "is identified as the primary driver of future increases" not in md
    # passages, table side and README unchanged from v2
    by_v2 = {r: c for r, c in zip(v2_md.split("\n## ")[2:], md.split("\n## ")[2:])}
    for a, b in by_v2.items():
        assert a.split("### Original passages")[1] == b.split("### Original passages")[1]
        assert a.split("### Table side")[1].split("### Paper side")[0] == b.split("### Table side")[1].split("### Paper side")[0]
    assert v2_md.split("## 1 ·")[0].split("## README")[1] == md.split("## 1 ·")[0].split("## README")[1]
    checks = m3.checks_record_v3(ed, smap, descs, m2.edited_texts_check(ed))
    assert checks == json.loads(m3.CHECKS_V3_PATH.read_text(encoding="utf-8")) and checks["leakage_hits"] == []
    assert checks["conditional_on_reslice"] == []


def test_xlsx_small_run():
    _need(mx.MENTOR_XLSX_PATH, "artifacts/benchmark/review/MENTOR_PILOT_ITEMS_2026-11-05.xlsx")
    assert m3.rich("plain") == "plain"
    r = m3.rich("A <small>(b)</small> — c")
    assert isinstance(r, Rich) and list(r) == [("A ", False), ("(b)", True), (" — c", False)] and r.text() == "A (b) — c"
    assert '<r><rPr><sz val="8"/></rPr><t xml:space="preserve">(b)</t></r>' in _cell("A1", r, 2)
    x = zipfile.ZipFile(mx.MENTOR_XLSX_PATH).read("xl/worksheets/sheet1.xml").decode("utf-8")
    assert x.count('<rPr><sz val="8"/></rPr>') == 4 and "&lt;small&gt;" not in x
