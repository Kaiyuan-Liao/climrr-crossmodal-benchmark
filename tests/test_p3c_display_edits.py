"""P3c hotfix (COORDINATOR 2026-11-18): COORDINATOR display edits on the mentor sample sheet, sheet v2.

`P3_display_edits_v1.yaml` overrides the display answer of BI-P3-0002, 0003, 0004, 0007 and the display question and
answer of BI-P3-0005 (`edit_origin: coordinator_edit`); 0001 and 0008 unchanged. The generated and polished texts stay in
the items. Checks (leakage v2.3, post-checks v3.1) on every edited text: 0 failures. Sheet v2 and the check report rebuild
byte for byte; v1 is still reproduced without edits. No model call.
"""

from __future__ import annotations

import importlib.util
import json
import sys

import pytest
import yaml

from climrr import litsynth_run5 as s5
from climrr import mentor_sheet_v2b as ms
from climrr import synthpackets_v4 as v4
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

EDITED = ["BI-P3-0004", "BI-P3-0003", "BI-P3-0002", "BI-P3-0005", "BI-P3-0007"]


def _load():
    man, packets = ms.load_packets(v4.PACKETS_V4B_DIR)
    return packets, ms.load_items(s5.ART, man), ms.load_edits()


def test_edits_file():
    _, items, edits = _load()
    assert list(edits) == EDITED                                       # 0001 and 0008: no edit
    for iid, e in edits.items():
        assert e["edit_origin"] == "coordinator_edit" and e["date"] == "2026-11-18" and e["reason"]
        assert ("display_prompt" in e) == (iid == "BI-P3-0005") and "display_answer" in e
        # the generated / polished text is untouched in the item and differs from the edit
        assert items[iid]["reference_answer"]["integrated"] != e["display_answer"]
    assert edits["BI-P3-0005"]["display_prompt"].endswith("how do the changes differ across U.S. regions, and what drives them?")
    assert "strong winds" in edits["BI-P3-0007"]["display_answer"] and edits["BI-P3-0007"]["display_answer"].count("strong winds") == 1
    for iid in EDITED:
        assert " will " not in edits[iid]["display_answer"] and "Research shows that" in edits[iid]["display_answer"]


def test_sheet_v2_rebuilds_and_only_question_answer_change():
    packets, items, edits = _load()
    v1, v2 = ms.rows(packets, items), ms.rows(packets, items, edits)
    assert ms.render_md(v2, ms.SHEET_VERSION) == ms.MD_PATH.read_text(encoding="utf-8")
    assert ms.MD_PATH.read_text(encoding="utf-8").startswith("# Sample items for mentor review --- 2026-11-19 (v2)\n")
    for r1, r2 in zip(v1[1:], v2[1:]):
        iid = r1[0].split("\n")[1]
        assert r1[0] == r2[0] and r1[3:] == r2[3:]                     # #, Table side, Paper side, passages unchanged
        e = edits.get(iid)
        if e is None:
            assert r1[1:3] == r2[1:3] == list(s5.display_text(items[iid]).values())
        else:
            assert r2[2] == e["display_answer"] and r2[1] == e.get("display_prompt", r1[1])
    assert ms.display_sources(items, edits) == {
        "BI-P3-0001": "original", "BI-P3-0004": "coordinator_edit", "BI-P3-0003": "coordinator_edit",
        "BI-P3-0002": "coordinator_edit", "BI-P3-0005": "coordinator_edit", "BI-P3-0007": "coordinator_edit",
        "BI-P3-0008": "original"}


def test_checks_on_edited_texts_zero_failures():
    packets, items, edits = _load()
    rep = ms.edited_text_checks(items, packets, edits)
    assert json.dumps(rep, indent=2, ensure_ascii=False) + "\n" == ms.EDITS_CHECKS_PATH.read_text(encoding="utf-8")
    assert rep["failures"] == 0 and rep["items_failing"] == [] and [x["item_id"] for x in rep["items"]] == EDITED
    assert rep["edits_sha256"] == sha256_file(ms.EDITS_PATH) and rep["items_modified"] == 0
    for x in rep["items"]:
        assert x["leakage_v2_3"] == {"prompt": [], "answer": []} and x["post_checks_v3_1"]["pass"]
        assert x["post_checks_v3_1"]["reports"] == {"context_driver_report": [], "regional_contrast_report": []}


def test_checks_catch_a_bad_edit():
    packets, items, edits = _load()
    bad = {**edits, "BI-P3-0003": {**edits["BI-P3-0003"],
                                   "display_answer": "The model shows heat-index days rising by 0.78 days, a tercile ranking small."}}
    rep = ms.edited_text_checks(items, packets, bad)
    assert rep["items_failing"] == ["BI-P3-0003"] and rep["failures"] == 1


@pytest.mark.parametrize("change", [
    {"item_id": "BI-P3-0099"}, {"reason": ""}, {"note": "x"}, {"display_answer": ""}])
def test_load_edits_refuses(tmp_path, change):
    doc = yaml.safe_load(ms.EDITS_PATH.read_text(encoding="utf-8"))
    doc["items"][0].update(change)
    f = tmp_path / "e.yaml"
    f.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError):
        ms.load_edits(f)


def test_build_script_default_is_v2(tmp_path, monkeypatch, capsys):
    from climrr import runrecord as rr
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path / "runs")
    md, xlsx, ck = tmp_path / "sheet.md", tmp_path / "sheet.xlsx", tmp_path / "checks.json"
    spec = importlib.util.spec_from_file_location("build_mentor_sheet_p3c_hotfix", REPO_ROOT / "scripts" / "build_mentor_sheet.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(sys, "argv", ["build_mentor_sheet.py", "--out-md", str(md), "--out-xlsx", str(xlsx), "--out-checks", str(ck)])
    assert mod.main() == 0
    out = json.loads(capsys.readouterr().out.split("\nrun record:")[0])
    assert out["sheet_version"] == 2 and out["edited_text_failures"] == 0 and out["edits_sha256"] == sha256_file(ms.EDITS_PATH)
    assert md.read_bytes() == ms.MD_PATH.read_bytes() and ck.read_bytes() == ms.EDITS_CHECKS_PATH.read_bytes()
    assert [k for k, v in out["display_source"].items() if v == "coordinator_edit"] == EDITED
    rec = json.loads(next((tmp_path / "runs").glob("*_build_mentor_sheet.json")).read_text(encoding="utf-8"))
    assert rec["config_snapshot"]["sheet_version"] == 2 and rec["config_snapshot"]["model_calls"] == 0
