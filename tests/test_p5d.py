"""Work package P5d (2026-11-25; D-079, D-080): ingest of infra synthesis runs 1 -- 2 and polish runs 1 -- 2, the D-079
display rule, the run-1 regression fixture, the COORDINATOR display edits and the Alvi sample sheet. No model call.

The delivered tarball is not in the repository; `verify_source` and the reproductions ran in the ingest (run record
`ingest_litsynth_infra_run2`). These tests work on the ingested files, each pinned by its manifest.
"""

from __future__ import annotations

import json

import pytest

from climrr import benchmark_items as bi
from climrr import litsynth_infra_run2 as ir
from climrr import litsynth_run2 as s2
from climrr import mentor_sheet_alvi as ma
from climrr import synthpackets_infra as spi
from climrr.checksums import sha256_file

MAN = json.loads(ir.MANIFEST_PATH.read_text(encoding="utf-8"))
PMAN = json.loads(ir.POLISH_MANIFEST_PATH.read_text(encoding="utf-8"))
MAN1 = json.loads(ir.MANIFEST1_PATH.read_text(encoding="utf-8"))
PMAN1 = json.loads(ir.POLISH_MANIFEST1_PATH.read_text(encoding="utf-8"))
ITEMS = {x["item_id"]: json.loads((ir.ART / x["path"]).read_text(encoding="utf-8")) for x in MAN["items_ingested"]}
SHEET_MD_SHA256 = "abf1adc5c7d758f9013574cdaeb7e4165dc28ab0cc325e22bb87e59bd3324465"   # P5d hotfix (closing clause as generated)
DISPLAY = {"BI-P5-0001": "original", "BI-P5-0002": "polished", "BI-P5-0004": "original", "BI-P5-0006": "original",
           "BI-P5-0007": "original", "BI-P5-0008": "original"}


# --- A: ingest ---------------------------------------------------------------------------------------------------------


def test_manifests_pin_every_copied_and_written_file():
    for man, base in ((MAN, ir.ART), (PMAN, ir.POLISH_ART), (MAN1, ir.ART1), (PMAN1, ir.POLISH_ART1)):
        assert man["tarball"]["sha256"] == ir.TARBALL_SHA256
        for f in man["files"]:
            assert sha256_file(base / f["path"]) == f["sha256"], f["path"]
    for x in MAN["items_ingested"]:
        assert sha256_file(ir.ART / x["path"]) == x["sha256"], x["path"]
    assert sha256_file(ir.ART / "items.jsonl") == ir.ITEMS_SHA256 == MAN["items_sha256"]
    assert sha256_file(ir.POLISH_ART / "summary.json") == ir.POLISH_SUMMARY_SHA256
    assert MAN["checks_reproduced"] is PMAN["checks_reproduced"] is MAN1["checks_reproduced"] is True
    assert MAN["source_commit"] == ir.SOURCE_COMMIT and MAN["packets"]["manifest_sha256"] == ir.PACKETS_MANIFEST_SHA256
    assert MAN["packets"]["manifest_sha256"] == sha256_file(spi.PACKETS_V1B_DIR / "manifest.json")


def test_lifecycle_six_in_human_review_two_rejected_with_two_redraws():
    assert sorted(ITEMS) == list(ir.ITEM_IDS)
    for iid, it in ITEMS.items():
        x = next(r for r in MAN["items_ingested"] if r["item_id"] == iid)
        if iid in ir.PASSING:
            assert it["review"]["status"] == x["status"] == "human_review"
            assert [h["event"] for h in it["review"]["history"]] == ["deterministic_pass", "polish", "human_review"]
            assert it["review"]["kaiyuan_disposition"] is it["review"]["final_frozen"] is None
        else:
            assert it["review"]["status"] == x["status"] == "rejected_pre_review" and x["redraws"] == 2
            assert x["reasons"] == ir.REJECTED[iid] and [a["attempt"] for a in x["attempts"]] == [1, 2]
        assert bi.schema_errors(it) == [] and bi.consistency_errors(it) == []
    assert MAN["counts"]["deterministic_pass"] == 6 and MAN["counts"]["redraws"] == 3


def test_superseded_attempts_and_run1_are_byte_identical_and_marked():
    for s in MAN["superseded_attempts"]:
        assert s["role"] == "superseded_attempt" and sha256_file(ir.ART / s["path"]) == s["sha256"] == ir.SUPERSEDED[s["item_id"]]["sha256"]
        att = json.loads((ir.ART / s["path"]).read_text(encoding="utf-8"))
        assert att["review"]["status"] == "rejected_pre_review" and att["review"]["history"][0]["reasons"] == s["reasons"]
    assert sorted(s["item_id"] for s in MAN["superseded_attempts"]) == ["BI-P5-0002", "BI-P5-0003", "BI-P5-0005"]
    assert MAN1["role"] == PMAN1["role"] == "superseded" and MAN1["counts"]["deterministic_pass"] == 2


# --- A: D-079 ------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("iid", ir.PASSING)
def test_d079_display_rule_reproduced(iid):
    it = ITEMS[iid]
    hr = it["review"]["history"][-1]
    ev = ir.polish_event(it)
    packet = json.loads((spi.PACKETS_V1B_DIR / f"PK-{it['review']['history'][0]['seed_id']}.json").read_text(encoding="utf-8"))
    again = ir.recheck(it, ev["rewrite"], packet)
    assert {k: hr["display_recheck"][k] for k in ("check_version", "pass", "reasons")} == again
    assert hr["display_source"] == DISPLAY[iid] == ("polished" if ev["status"] == "polished" and again["pass"] else "original")
    assert ir.display_text(it) == (ev["rewrite"] if DISPLAY[iid] == "polished" else ev["pre_polish"])
    # the original text passed v3.5 when generated; it still does as display text
    assert ir.recheck(it, ev["pre_polish"], packet)["pass"]


def test_display_text_refuses_a_polished_display_without_a_passing_recheck():
    it = json.loads(json.dumps(ITEMS["BI-P5-0004"]))
    hr = it["review"]["history"][-1]
    hr["display_source"], hr["display_text"] = "polished", ir.polish_event(it)["rewrite"]
    with pytest.raises(ValueError, match="D-079"):
        ir.display_text(it)


# --- A: the run-1 regression fixture -----------------------------------------------------------------------------------


def test_run1_passing_items_pass_v35_with_budget_reported():
    assert sha256_file(ir.ART1 / "items.jsonl") == ir.RUN1_ITEMS_SHA256
    items1 = s2.read_items(ir.ART1 / "items.jsonl")
    res = ir.run1_regression(items1)
    assert [r["item_id"] for r in res] == ["BI-P5-0001", "BI-P5-0003"]
    for r in res:
        assert r["pass"] and r["reasons"] == [] and r["check_version"] == bi.SYNTH_CHECK_VERSION_V35
        assert r["budget"]["enforced"] is False and {"driver_claims", "impact_claims", "within"} <= set(r["budget"])
    assert [{k: r[k] for k in ("item_id", "pass", "reasons")} for r in res] == \
        [{k: r[k] for k in ("item_id", "pass", "reasons")} for r in MAN["run1_regression"]]


# --- B: COORDINATOR display edits --------------------------------------------------------------------------------------


def _sheet():
    return ma.build()


def test_edits_applied_as_written():
    _, rs, disp, *_ = _sheet()
    a = {iid: d["answer"] for iid, d in disp.items()}
    # P5d hotfix: the closing clause stays as generated (rewording deferred to prompt v5.5, D-079)
    for iid, place in (("BI-P5-0001", "Virginia"), ("BI-P5-0002", "Arizona"), ("BI-P5-0004", "California")):
        assert a[iid].endswith(f"These are general drivers of dangerous heat-index days, not findings specific to {place}.")
        assert "general research findings" not in a[iid]
    assert not any(op["id"] == "closing_clause" for op in ma.load_edits()["all_items"])
    assert "Research on the United States, including work on the Southwest, shows that" in a["BI-P5-0002"]
    assert "shows, including" not in a["BI-P5-0002"] and "a moderate increase," not in a["BI-P5-0002"]
    assert "roads and rail" not in a["BI-P5-0002"] and "when wildfires occur" not in a["BI-P5-0002"]
    assert "extreme heat and wind raise the chance of ignitions near power lines." in a["BI-P5-0001"]
    assert "drier air, with a higher vapor-pressure deficit, raises fire danger." in a["BI-P5-0007"]
    assert disp["BI-P5-0004"]["display_source"] == disp["BI-P5-0006"]["display_source"] == disp["BI-P5-0008"]["display_source"] == "original"
    assert disp["BI-P5-0006"]["answer"] == disp["BI-P5-0006"]["base_answer"]
    assert disp["BI-P5-0002"]["groups_removed"] == ["LG-infra_heat_index__transportation_systems-impact-c1-007"]
    # the generated and polished texts are untouched in the items
    assert ITEMS["BI-P5-0002"]["reference_answer"]["integrated"] == ir.polish_event(ITEMS["BI-P5-0002"])["rewrite"]["answer"]


def test_item_edit_must_match_once():
    doc = ma.load_edits()
    doc["items"][0]["edits"][0]["find"] = "a sentence that is not there."
    with pytest.raises(ValueError, match="must be once"):
        ma.apply_edits(ir.display_text(ITEMS["BI-P5-0001"])["answer"], "BI-P5-0001", doc)


def test_edited_text_checks_report():
    _, _, disp, packets, items, _ = _sheet()
    chk = ma.edited_text_checks(items, packets, disp)
    assert chk == json.loads(ma.EDITS_CHECKS_PATH.read_text(encoding="utf-8"))
    assert chk["not_edited"] == ["BI-P5-0004", "BI-P5-0006", "BI-P5-0008"]
    # P5d hotfix: all six display texts checked; 0 failures
    assert [x["item_id"] for x in chk["items"]] == ma.order()
    assert chk["leakage_failures"] == chk["failures"] == 0 and chk["items_failing"] == []
    assert all(x["post_checks_v3_5"]["pass"] and not x["leakage_v2_3"]["prompt"] and not x["leakage_v2_3"]["answer"] for x in chk["items"])


# --- C: the sheet ------------------------------------------------------------------------------------------------------


def test_sheet_rebuilds_byte_identical_and_layout():
    _, rs, disp, packets, items, run = _sheet()
    assert ma.render_md(rs) == ma.MD_PATH.read_text(encoding="utf-8")
    assert sha256_file(ma.MD_PATH) == SHEET_MD_SHA256
    chk = json.loads(ma.EDITS_CHECKS_PATH.read_text(encoding="utf-8"))
    assert ma.render_notes(rs, disp, packets, items, run, chk) == ma.NOTES_PATH.read_text(encoding="utf-8")
    assert rs[0] == ["#", "Question", "Answer", "Asset class (CISA sector)", "Table side", "Paper side", "Original passages"]
    assert [r[0].split("\n")[1] for r in rs[1:]] == ["BI-P5-0001", "BI-P5-0002", "BI-P5-0004", "BI-P5-0006", "BI-P5-0007", "BI-P5-0008"]
    assert len(ma.README_LINES) == 5 and "not findings specific to California" in ma.README_LINES[4][1]
    for r in rs[1:]:
        side = r[5].split("\n")
        kinds = [ln.split(",")[0] for ln in side]
        assert kinds == sorted(kinds, key=lambda k: k != "Impact")          # impact groups first, then drivers
        assert all(" research shows (" in ln or " research suggests (1 paper)" in ln for ln in side)
        assert r[4].splitlines()[-1].startswith("Place-named impact evidence: ")
    assert "via wildfire occurrence" in rs[1][5]


def test_alvi_sheet_shows_no_rejected_item():
    _, rs, *_ = _sheet()
    text = "\n".join("\n".join(r) for r in rs)
    assert "BI-P5-0003" not in text and "BI-P5-0005" not in text
