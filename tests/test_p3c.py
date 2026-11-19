"""Work package P3c (D-068): the synthesis run-5 / polish run-2 ingest, the mentor sample sheet v2 (2026-11-19) and the review
workbook / flag list.

Checks the ingested copy (the tarball stays outside the repository): every manifest hash; the run facts (including the 401
pre-run failures and the superseded attempt); seven items in human_review = run-5 record + polish event (text replaced only
when polished) + the lifecycle step with display_source; post-checks v3.1 reproduced against packets v4b for the items and
the superseded attempt; polish checks v2 reproduced from the polish events. Then the sheet and the review outputs rebuilt
and compared byte-for-byte with the tracked files. No model call.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import io
import json
import sys

import pytest

from climrr import benchmark_items as bi
from climrr import itemseeds as sd
from climrr import litsynth_run2 as s2
from climrr import litsynth_run4 as s4
from climrr import litsynth_run5 as s5
from climrr import mentor_sheet_v2b as ms
from climrr import p3_items_review as pr
from climrr import pattern_descriptors as pd
from climrr import plain_language as pl
from climrr import polish_checks as pc
from climrr import synthpackets_v4 as v4
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

MAN = json.loads(s5.MANIFEST_PATH.read_text(encoding="utf-8"))
PMAN = json.loads(s5.POLISH_MANIFEST_PATH.read_text(encoding="utf-8"))
IDS = ["BI-P3-0001", "BI-P3-0002", "BI-P3-0003", "BI-P3-0004", "BI-P3-0005", "BI-P3-0007", "BI-P3-0008"]
POLISHED = ["BI-P3-0002", "BI-P3-0003", "BI-P3-0004", "BI-P3-0005", "BI-P3-0007"]


def _items():
    return {x["item_id"]: json.loads((s5.ART / x["path"]).read_text(encoding="utf-8")) for x in MAN["items_ingested"]}


def _run5_records():
    """The run-5 records as the run wrote them: the ingested items without the polish and lifecycle events and with the
    pre-polish text (and its leakage check) back."""
    out, cols = [], bi.column_names()
    for _, it in sorted(_items().items()):
        x = copy.deepcopy(it)
        ev = x["review"]["history"][1]
        x["prompt"], x["reference_answer"]["integrated"] = ev["pre_polish"]["prompt"], ev["pre_polish"]["answer"]
        x["source_leakage_check"] = bi.leakage_check(x["prompt"], cols)
        x["review"]["status"] = "deterministic_pass"
        x["review"]["history"] = x["review"]["history"][:1]
        out.append(x)
    return out


# --- A: the ingest ------------------------------------------------------------------------------------------------


def test_every_manifest_file_matches_its_hash():
    for base, man in ((s5.ART, MAN), (s5.POLISH_ART, PMAN)):
        for f in man["files"]:
            assert sha256_file(base / f["path"]) == f["sha256"], f["path"]
    for x in MAN["items_ingested"]:
        assert sha256_file(s5.ART / x["path"]) == x["sha256"], x["path"]
    assert sha256_file(s5.ART / "items.jsonl") == MAN["items_sha256"] == s5.ITEMS_SHA256 == \
        "9fa632e9fc33b2e18e9c91c65dcad35ec0bf74fc03782eabb19672f89b1ddb3e"
    assert sha256_file(s5.POLISH_ART / "summary.json") == PMAN["summary_sha256"] == s5.POLISH_SUMMARY_SHA256 == \
        "bcba3bea461b367101e00f4becebda5dae35f20215f0c002cda5b0f172864bcd"
    assert sha256_file(s5.POLISH_ART / "polished.jsonl") == PMAN["polished_sha256"] == s5.POLISHED_SHA256
    assert MAN["tarball"]["sha256"] == PMAN["tarball"]["sha256"] == s5.TARBALL_SHA256 == \
        "e092875e21152f262e0a903e6e2dde41254782e6053dacb07385696c523acc4b"
    assert MAN["packets"]["manifest_sha256"] == s5.PACKETS_MANIFEST_SHA256 == sha256_file(v4.PACKETS_V4B_DIR / "manifest.json")
    assert MAN["source_commit"] == PMAN["source_commit"] == s5.SOURCE_COMMIT
    for rel, sha in ((s5.AGENT_REL, s5.AGENT_SHA256), (s5.POLISH_AGENT_REL, s5.POLISH_AGENT_SHA256)):
        assert hashlib.sha256(s2.git_blob(s5.SOURCE_COMMIT, rel)).hexdigest() == sha
    assert s5.AGENT_SHA256.startswith("f41c0b95") and s5.SYSTEM_PROMPT_SHA256.startswith("8ce96b07")
    assert s5.POLISH_AGENT_SHA256.startswith("6abc7b2b") and s5.POLISH_SYSTEM_PROMPT_SHA256.startswith("2dbbce7f")


def test_run_facts_pre_run_failures_and_restarts():
    assert MAN["counts"] == s5.RUN_FACTS and PMAN["counts"] == s5.POLISH_FACTS
    assert MAN["counts"]["pre_run_auth_failures"] == 2 and MAN["counts"]["deterministic_fail"] == 0
    assert MAN["checks_reproduced"] is True and PMAN["checks_reproduced"] is True
    assert MAN["format_corrective_items"] == ["BI-P3-0004", "BI-P3-0005"] and MAN["first_check_reasons"] == s5.FIRST_CHECK_REASONS
    lf = s5.log_facts((s5.ART / "agent.log").read_text(encoding="utf-8"))
    assert lf == MAN["log"] and lf["pre_run_auth_failed_seeds"] == ["SD2-TP1-00071", "SD2-TP1-00271"]
    assert [r["made"] for r in lf["restarts"]] == [0, 1]
    left = {x["path"] for x in MAN["excluded_files"] if x.get("pre_run_leftover")}
    assert left == set(s5.PRE_RUN_LEFTOVERS)


def test_superseded_attempt():
    (sup,) = MAN["superseded_attempts"]
    path = s5.ART / sup["path"]
    assert sup["role"] == "superseded_attempt" and sha256_file(path) == sup["sha256"] == s5.ATTEMPT1_SHA256
    att = json.loads(path.read_text(encoding="utf-8"))
    assert att["item_id"] == "BI-P3-0007" and att["review"]["status"] == "rejected_pre_review"
    assert att["review"]["history"][0]["reasons"] == sup["reasons"] == s5.SUPERSEDED["BI-P3-0007"]["reasons"]
    assert sup["superseded_by"]["sha256"] == sha256_file(s5.ITEMS_DIR / "BI-P3-0007.json")
    assert MAN["checks"]["superseded_attempt"]["reasons"] == sup["reasons"]
    assert "superseded" not in {x["item_id"] for x in MAN["items_ingested"]} and len(MAN["items_ingested"]) == 7


def test_lifecycle_and_display_source():
    items, run = _items(), {it["item_id"]: it for it in s2.read_items(s5.ART / "items.jsonl")}
    recs = {r["item_id"]: r for r in s2.read_items(s5.POLISH_ART / "polished.jsonl")}
    assert sorted(items) == sorted(run) == sorted(recs) == IDS
    assert {i: s5.display_source(it) for i, it in items.items()} == MAN["display_source"] == \
        {i: ("polished" if i in POLISHED else "original") for i in IDS}
    for iid, it in items.items():
        r = it["review"]
        assert r["status"] == "human_review" and r["kaiyuan_disposition"] is None and r["final_frozen"] is None
        assert [h["event"] for h in r["history"]] == ["deterministic_pass", "polish", "human_review"]
        hr, ev = r["history"][2], r["history"][1]
        assert hr["at"] == MAN["ingested_at"] and hr["decision"] == "D-033" and hr["display_source"] == MAN["display_source"][iid]
        assert ev["status"] == recs[iid]["status"] and ev["rewrite"] == recs[iid]["polished"] and ev["reasons"] == s5.POLISH_REJECTED.get(iid, [])
        want = ev["rewrite"] if iid in POLISHED else ev["pre_polish"]
        assert s5.display_text(it) == want
        assert ev["pre_polish"] == {"prompt": run[iid]["prompt"], "answer": run[iid]["reference_answer"]["integrated"]}
        assert bi.schema_errors(it) == [] and bi.consistency_errors(it) == []
    assert all(r["pre_polish"]["prompt"] == r["polished"]["prompt"] for r in recs.values())   # the polisher changed no question


def test_synthesis_checks_reproduce_against_packets_v4b():
    recs = _run5_records()
    assert sorted(recs, key=lambda x: x["item_id"]) == sorted(s2.read_items(s5.ART / "items.jsonl"), key=lambda x: x["item_id"])
    att = json.loads((s5.ART / MAN["superseded_attempts"][0]["path"]).read_text(encoding="utf-8"))
    rep = s5.reproduce_synthesis(recs, att)
    order = [x["item_id"] for x in MAN["checks"]["items"]]
    assert sorted(rep["items"], key=lambda x: order.index(x["item_id"])) == MAN["checks"]["items"]
    assert rep["superseded_attempt"] == MAN["checks"]["superseded_attempt"]
    assert rep["check_version"] == "synthesis_post_checks v3.1"
    assert [x["item_id"] for x in rep["items"] if x["first_check_reasons"]] == ["BI-P3-0004", "BI-P3-0005"]


def test_polish_checks_v2_reproduce():
    agent = s4.load_agent_at(s5.SOURCE_COMMIT, s5.POLISH_AGENT_REL, s5.POLISH_AGENT_SHA256, "litpolish_agent_v11_test")
    items, cols, nca = _items(), bi.column_names(), sd.nca_map()
    syn, rules, plain = pc.load_synonyms_v2(), pd.load_rules(pd.RULES_V4_PATH), pl.load(pl.PLAIN_V1A_PATH)
    recs = {r["item_id"]: r for r in s2.read_items(s5.POLISH_ART / "polished.jsonl")}
    for iid, it in items.items():
        ev = it["review"]["history"][1]
        obj = agent.extract(ev["raw_response"])
        assert {"prompt": obj["prompt"], "answer": obj["answer"]} == ev["rewrite"]
        res = pc.invariance_v2(ev["pre_polish"], ev["rewrite"], agent.cited_groups(it), nca, syn, rules, plain, cols)
        assert res["reasons"] == recs[iid]["reasons"] and res["checks"] == recs[iid]["checks"] and res["pass"] == (iid in POLISHED)
    kinds = [r.split(":")[1].strip().split(" ")[0] for x in recs.values() for r in x["reasons"]]
    assert {k: kinds.count(k) for k in set(kinds)} == {"descriptor": 1, "hedges": 1, "length": 1}


# --- B: the mentor sample sheet -------------------------------------------------------------------------------------


def _sheet_rows():
    man, packets = ms.load_packets(v4.PACKETS_V4B_DIR)
    return ms.rows(packets, ms.load_items(s5.ART, man)), packets


def test_sheet_rebuilds_byte_identically_and_follows_the_package():
    rs, packets = _sheet_rows()
    # v1 as sent (no display edits); the tracked file is v2 since the P3c hotfix (tests/test_p3c_display_edits.py)
    assert hashlib.sha256(ms.render_md(rs).encode("utf-8")).hexdigest() == ms.V1_MD_SHA256
    assert rs[0] == ["#", "Question", "Answer", "Table side", "Paper side", "Original passages"] and len(rs) == 8
    assert [r[0].split("\n")[1] for r in rs[1:]] == ["BI-P3-0001", "BI-P3-0004", "BI-P3-0003", "BI-P3-0002", "BI-P3-0005",
                                                     "BI-P3-0007", "BI-P3-0008"]
    items = _items()
    for r in rs[1:]:
        iid = r[0].split("\n")[1]
        assert [r[1], r[2]] == list(s5.display_text(items[iid]).values())
        ts = r[3]
        for key in ("Quantity: ", "Place: ", "Season: summer", "Baseline window: Historical, 1995 to 2004 (modeled)",
                    "Future window: ", "Scenario: RCP8.5", "Statistic: ", "Grid cells: "):
            assert key in ts, (iid, key)
        assert "working assumptions relied on: " + ", ".join(f"{w['id']} ({w['resolution']})"
                                                             for w in packets[iid]["working_assumptions_relied_on"]) in ts
        assert all(ln.startswith(("Research shows (", "Research suggests (1 paper)")) for ln in r[4].split("\n"))
        assert "RCP" not in r[1] + r[2] and "°F" not in r[1] + r[2]
    fire = rs[6][3]
    assert "WA-FWI-SUMMER (R-004)" in fire and "not fire occurrence" in fire and "(+2.2)" in fire and " days" not in fire.split("Values:")[1].split("\n")[0]
    assert "Values: mean 15.4 days -> 24.4 days (+9.0 days)" in rs[1][3]
    assert "1. Southeast: 18.9 -> 45.9 (+27.0)" in rs[5][3]
    # passages verbatim (no cut) with paper id and section
    pk = packets["BI-P3-0001"]
    members = [m for g in pk["provenance"]["groups"] if g["group_id"] in ms.cited_groups(items["BI-P3-0001"]) for m in g["members"]]
    for m in members:
        assert f"paper {m['paper_item_id']}, {m['json_path'][2:].replace('_', ' ')}: \"{m['verbatim_passage']}\"" in rs[1][5]
    assert len(ms.README_LINES) == 3


def test_build_mentor_sheet_script(tmp_path, monkeypatch, capsys):
    from climrr import runrecord as rr
    monkeypatch.setattr(rr, "RUNS_DIR", tmp_path / "runs")
    md, xlsx = tmp_path / "sheet.md", tmp_path / "sheet.xlsx"
    spec = importlib.util.spec_from_file_location("build_mentor_sheet_p3c", REPO_ROOT / "scripts" / "build_mentor_sheet.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(sys, "argv", ["build_mentor_sheet.py", "--out-md", str(md), "--out-xlsx", str(xlsx), "--no-edits"])
    assert mod.main() == 0
    out = json.loads(capsys.readouterr().out.split("\nrun record:")[0])
    assert out["rows"] == 7 and out["display_source"] == MAN["display_source"] and out["sheet_version"] == 1
    assert sha256_file(md) == ms.V1_MD_SHA256 and xlsx.stat().st_size > 0
    assert len(list((tmp_path / "runs").glob("*_build_mentor_sheet.json"))) == 1


# --- C: review workbook and flags -----------------------------------------------------------------------------------


def test_review_outputs_rebuild_and_flags():
    man, packets = ms.load_packets(v4.PACKETS_V4B_DIR)
    items = ms.load_items(s5.ART, man)
    rep = pr.flags(items, packets)
    assert json.dumps(rep, indent=2, ensure_ascii=False) + "\n" == pr.FLAGS_PATH.read_text(encoding="utf-8")
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(pr.item_rows(items, rep))
    assert buf.getvalue() == pr.CSV_PATH.read_text(encoding="utf-8")
    assert rep["context_driver_report_hits"] == {i: 0 for i in IDS} and rep["regional_contrast_report_hits"] == {i: 0 for i in IDS}
    assert rep["rubric_lint"]["totals"]["all"] == 4 and rep["items_modified"] == 0
    rows = {r[1]: dict(zip(pr.ITEM_HEADER, r)) for r in pr.item_rows(items, rep)[1:]}
    assert rows["BI-P3-0005"]["edit_origin"] == "coordinator_proposed" and rows["BI-P3-0005"]["edited_prompt"] == pr.PROPOSED["BI-P3-0005"]["prompt"]
    assert rows["BI-P3-0005"]["question_display"] == items["BI-P3-0005"]["prompt"]          # the sheet keeps the generated text
    assert all(rows[i]["edit_origin"] == "" for i in IDS if i != "BI-P3-0005")
    assert {f["flag_id"] for f in rep["flags"] if f["source"] == "work_package"} == {"WP-C1", "WP-C3"}


@pytest.mark.parametrize("flag", pr.EXECUTOR_FLAGS + pr.WORK_PACKAGE_FLAGS, ids=lambda f: f["id"])
def test_every_flag_is_pinned_to_its_text(flag):
    items = _items()
    for iid, field, needle in flag.get("where") or [(flag["item_id"], flag["field"], flag["needle"])]:
        assert needle in pr.field_text(items[iid], field), (flag["id"], iid, field)
