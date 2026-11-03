"""Synthesis run 3 ingest, items index, post-checks v2.3, rubric lint v1a, review workbook v2 and the mentor sheet
(mentor-export package, 2026-11-03).

Checks the ingested copy, not the delivered tarball (outside the repository): every manifest hash; the run facts; the
item in human_review, schema-v2 valid and equal to the run's record but for the lifecycle step; post-checks v2.2
reproduced against packets v3b at the source commit; the items index rebuilt (0010 current in run 3, the run-2 version
superseded and unchanged); the v2.3 phrases and the report rebuilt, v2.2 still the default; lint v1a closing the two
D-056 gaps and its report rebuilt; the workbook v2 CSV and the mentor Markdown rebuilt from their inputs; the support
map's clauses verbatim in the COORDINATOR texts.
"""

from __future__ import annotations

import copy
import json
import os

import pytest

from climrr import benchmark_items as bi
from climrr import itemseeds as sd
from climrr import litsynth_run2 as s2
from climrr import litsynth_run3 as s3
from climrr import p2b_items_review as rv
from climrr import p2b_mentor_export as mx
from climrr import rubric_lint as rl
from climrr.checksums import sha256_file

MAN = json.loads(s3.MANIFEST_PATH.read_text(encoding="utf-8"))
IDS = [f"BI-P2B-{i:04d}" for i in range(1, 11)]
MENTOR_IDS = ["BI-P2B-0001", "BI-P2B-0003", "BI-P2B-0006", "BI-P2B-0007", "BI-P2B-0010"]


@pytest.fixture(scope="module")
def item():
    (x,) = MAN["items_ingested"]
    return json.loads((s3.ART / x["path"]).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def current():
    return s3.current_items()


def _need(path, what):
    if not path.is_file():
        if os.environ.get("CLIMRR_ALLOW_MISSING_RAW") == "1":
            pytest.skip(f"{what} absent and CLIMRR_ALLOW_MISSING_RAW=1 is set")
        pytest.fail(f"{what} is absent (gitignored); regenerate it, or set CLIMRR_ALLOW_MISSING_RAW=1 for code-only work")


# --- run 3 --------------------------------------------------------------------------------------------------------


def test_every_manifest_file_matches_its_hash():
    for f in MAN["files"]:
        assert sha256_file(s3.ART / f["path"]) == f["sha256"], f["path"]
    for x in MAN["items_ingested"]:
        assert sha256_file(s3.ART / x["path"]) == x["sha256"], x["path"]
    assert sha256_file(s3.ART / "items.jsonl") == MAN["items_sha256"] == s3.ITEMS_SHA256
    assert sha256_file(s3.ART / "summary.json") == MAN["summary_sha256"] == s3.SUMMARY_SHA256
    assert MAN["tarball"]["sha256"] == s3.TARBALL_SHA256 and MAN["packets"]["manifest_sha256"] == s3.PACKETS_MANIFEST_SHA256
    assert sha256_file(s2.REPO_ROOT / s2.AGENT_REL) == MAN["generator"]["agent_sha256"] == s2.AGENT_SHA256
    assert [e["path"] for e in MAN["excluded_files"]] == ["litsynth/run3/raw/SD2-TP1-00075/prompt_user.txt",
                                                          "litsynth/run3/raw/SD2-TP1-00075/response.json"]


def test_run_facts_and_item(item):
    assert MAN["counts"] == s3.RUN_FACTS and MAN["checks_reproduced"] is True and MAN["source_commit"] == s3.SOURCE_COMMIT
    assert MAN["packets"]["version"] == "synthpackets v3b" and MAN["packets"]["packet_sha256"] == s3.PACKET_SHA256
    r = item["review"]
    assert item["item_id"] == "BI-P2B-0010" and item["use_case_level"] == 7
    assert r["status"] == "human_review" and r["kaiyuan_disposition"] is None and r["final_frozen"] is None
    assert [h["event"] for h in r["history"]] == ["deterministic_pass", "human_review"] and r["history"][1]["at"] == MAN["ingested_at"]
    assert bi.schema_errors(item) == [] and bi.consistency_errors(item) == []
    before = copy.deepcopy(item)
    before["review"]["status"] = "deterministic_pass"
    before["review"]["history"] = before["review"]["history"][:1]
    assert [before] == s2.read_items(s3.ART / "items.jsonl")                     # nothing but the lifecycle step
    assert not bi.validity(item)["benchmark_valid"]


def test_post_checks_reproduce_against_packets_v3b(item):
    rep = s2.reproduce_checks([item], commit=s3.SOURCE_COMMIT)
    assert rep == MAN["checks"] and rep["items"][0]["pass"] and rep["items"][0]["first_check_reasons"] is None
    with pytest.raises(ValueError):                                              # not the v3a packet
        s2.reproduce_checks([item])


# --- the items index ------------------------------------------------------------------------------------------------


def test_index_rebuilds_and_records_the_supersession():
    idx = json.loads(s3.INDEX_PATH.read_text(encoding="utf-8"))
    assert s3.index() == idx and [x["item_id"] for x in idx["items"]] == IDS
    cur = {x["item_id"]: x["current"]["run"] for x in idx["items"]}
    assert cur == {i: "run2" for i in IDS[:9]} | {"BI-P2B-0010": "run3"}
    (ten,) = [x for x in idx["items"] if x["item_id"] == "BI-P2B-0010"]
    assert [(v["run"], v["index_status"]) for v in ten["versions"]] == [("run2", "superseded_by_run3"), ("run3", "current")]
    run2 = json.loads(s2.MANIFEST_PATH.read_text(encoding="utf-8"))
    assert {x["item_id"]: x["sha256"] for x in run2["items_ingested"]}["BI-P2B-0010"] == ten["versions"][0]["sha256"]
    assert sha256_file(s2.MANIFEST_PATH) == "c9c6bc9bc1a4f19d94e7a5e9c9514c34c9a3ad18b60dc97a11b87df2b84d60e9"  # run 2 untouched


# --- post-checks v2.3 ---------------------------------------------------------------------------------------------


def test_model_source_phrases():
    f = bi.model_source_flags
    assert f("The model shows an increase.") == ["source phrase (v2.3): The model shows"]
    assert f("The modeled projection shows more days.") == ["source phrase (v2.3): The modeled projection shows"]  # flagged once
    assert f("our data suggest a rise; this table indicates it; the projection projects") == [
        "source phrase (v2.3): our data suggest", "source phrase (v2.3): this table indicates",
        "source phrase (v2.3): the projection projects"]
    assert f("Climate models project an increase; a modeled baseline.") == []
    assert bi.SYNTH_CHECK_VERSION == "synthesis_post_checks v2.2"                  # the frozen agent's default
    with pytest.raises(bi.ItemError, match="unknown post-check version"):
        bi.synthesis_post_checks({}, {}, {}, [], "synthesis_post_checks v9")


def test_v23_report_rebuilds_and_edits_nothing(current):
    rep = json.loads(mx.RECHECK_PATH.read_text(encoding="utf-8"))
    idx = json.loads(s3.INDEX_PATH.read_text(encoding="utf-8"))
    sup = [json.loads((s3.ITEMS_ROOT / v["path"]).read_text(encoding="utf-8"))
           for x in idx["items"] for v in x["versions"] if v["index_status"] != "current"]
    again = mx.recheck_v23(current, sup, list(mx.edits().values()))
    assert {k: rep[k] for k in again} == again and rep["items_modified"] == 0
    assert rep["items_hit"] == ["BI-P2B-0002", "BI-P2B-0003", "BI-P2B-0004", "BI-P2B-0005", "BI-P2B-0007", "BI-P2B-0008"]
    assert all(r.split(": ", 1)[1].startswith("source phrase (v2.3)") for x in rep["current_items"] for r in x["v2_3_new_reasons"])
    assert all(x["v2_2_pass"] for x in rep["current_items"]) and rep["coordinator_proposed_hits"] == ["BI-P2B-0010"]


# --- rubric lint v1a ----------------------------------------------------------------------------------------------


def test_lint_v1a_closes_the_two_gaps():
    for line in ("[w=1] Exact numeric values are not required; any statement consistent with the magnitude class counts.",
                 "Including any numeric value not listed in the allowed numbers"):
        assert rl.GENERATION_CONSTRAINT_RES[rl.VERSION].search(line) and not rl.GENERATION_CONSTRAINT_RES[rl.VERSION_V1].search(line)


def test_lint_v1a_report_rebuilds(current):
    report = json.loads(rv.LINT_V1A_PATH.read_text(encoding="utf-8"))
    again = rl.lint(current, {it["item_id"]: s2.packet_for_item(it)["checks_input"]["group_strength"] for it in current})
    assert {k: report[k] for k in again} == again and report["version"] == "rubric_lint v1a" and report["edits_made"] == 0
    v1 = json.loads((s2.ART / "rubric_lint_v1.json").read_text(encoding="utf-8"))
    new = {x["item_id"]: x["n_flags"] for x in report["items"]}
    old = {x["item_id"]: x["n_flags"] for x in v1["items"]}
    assert {i for i in IDS[:9] if new[i] != old[i]} == {"BI-P2B-0007"} and new["BI-P2B-0007"] - old["BI-P2B-0007"] == 2


# --- workbook v2 and the mentor sheet ---------------------------------------------------------------------------------


def test_items_csv_v2_rebuilds():
    man2, man3, index, items, packets, lint, notes, item_sha = rv.inputs_v2()
    rows = rv.item_rows_v2(items, packets, lint, notes, mx.edits())
    assert rv.items_csv(rows) == rv.ITEMS_CSV_V2_PATH.read_text(encoding="utf-8")
    h = rows[0]
    assert h.index(rv.EDIT_ORIGIN_COL) == h.index("edited_reference_integrated") + 1
    by_id = {r[0]: r for r in rows[1:]}
    assert [i for i in IDS if by_id[i][h.index(rv.EDIT_ORIGIN_COL)] == "coordinator_proposed"] == MENTOR_IDS
    assert by_id["BI-P2B-0010"][h.index("prompt")] == items[-1]["prompt"] and items[-1]["review"]["history"][0]["source_commit"] == s3.SOURCE_COMMIT
    assert [by_id[i][h.index("coordinator_disposition")] for i in IDS] == ["accept_with_edits"] * 9 + ["regenerate"]
    assert all(by_id[i][h.index("kaiyuan_disposition")] == "" for i in IDS)        # nothing confirmed, nothing frozen


def test_support_map_clauses_are_verbatim_and_cited():
    ed, smap = mx.edits(), mx.support_map()
    assert list(ed) == MENTOR_IDS and sorted(smap) == sorted(MENTOR_IDS)
    for iid in MENTOR_IDS:
        assert all(c["text"] in ed[iid]["edited_reference_integrated"] for c in smap[iid]["clauses"]), iid
    verdicts = [c["verdict"] for i in MENTOR_IDS for c in smap[i]["clauses"]]
    assert verdicts.count("not_supported_by_verbatim_passage") == 2 and verdicts.count("supported_by_uncited_packet_group") == 1


def test_mentor_md_v1_rebuilds(current):
    # the tracked Markdown is v2 since the mentor sheet v2 package (tests/test_mentor_v2.py); v1 is compared with the file
    # as committed at the mentor-export build 37c7037
    _need(sd.PATTERNS_PATH, "artifacts/benchmark/table_patterns_v1.jsonl")
    rows = mx.mentor_rows({it["item_id"]: it for it in current}, mx.edits(), mx.support_map())
    assert rows[0] == mx.MENTOR_HEADER and len(rows) == 6
    rel = mx.MENTOR_MD_PATH.relative_to(mx.REPO_ROOT).as_posix()
    assert mx.render_md(rows) == s2.git_blob("37c7037", rel).decode("utf-8")
    assert rows[1][4] == "none — table-only item (pattern identification)"
    assert all("State label provisional (IC-012)" in r[3] for r in rows[1:])


def test_cut_passage():
    s = "First sentence here. " * 40
    out = mx.cut_passage(s)
    assert len(out) <= mx.PASSAGE_MAX + 4 and out.endswith(". […]") and mx.cut_passage("short.") == "short."
