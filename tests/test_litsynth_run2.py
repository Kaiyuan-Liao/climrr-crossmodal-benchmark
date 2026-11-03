"""Synthesis run 2 ingest, rubric lint v1 and the item review CSV (pilot P2b-ingest-items; D-056).

Checks the ingested copy, not the delivered tarball (which stays outside the repository): every manifest hash; the run
facts (10 items, 10 deterministic_pass, 0 leakage flags, the format corrective turn on 0001, 0002, 0006, 0008, 0009, 0010);
each item in human_review, schema-v2 valid, and equal to the run's `items.jsonl` record but for the lifecycle step;
post-checks v2.2 reproduced from tracked files against packets v3a at the source commit; the lint rules on hand-made
items and the tracked lint report rebuilt; the tracked ITEMS CSV rebuilt from the tracked files.
"""

from __future__ import annotations

import copy
import json

import pytest

from climrr import benchmark_items as bi
from climrr import litsynth_run2 as s2
from climrr import p2b_items_review as rv
from climrr import rubric_lint as rl
from climrr.checksums import sha256_file

MAN = json.loads(s2.MANIFEST_PATH.read_text(encoding="utf-8"))
IDS = [f"BI-P2B-{i:04d}" for i in range(1, 11)]


@pytest.fixture(scope="module")
def items():
    return [json.loads((s2.ART / x["path"]).read_text(encoding="utf-8")) for x in MAN["items_ingested"]]


def test_every_manifest_file_matches_its_hash():
    for f in MAN["files"]:
        assert sha256_file(s2.ART / f["path"]) == f["sha256"], f["path"]
    for x in MAN["items_ingested"]:
        assert sha256_file(s2.ART / x["path"]) == x["sha256"], x["path"]
    assert sha256_file(s2.ART / "items.jsonl") == MAN["items_sha256"] == s2.ITEMS_SHA256
    assert sha256_file(s2.ART / "summary.json") == MAN["summary_sha256"] == s2.SUMMARY_SHA256
    assert MAN["tarball"]["sha256"] == s2.TARBALL_SHA256 and MAN["packets"]["manifest_sha256"] == s2.PACKETS_MANIFEST_SHA256
    assert sha256_file(s2.REPO_ROOT / s2.AGENT_REL) == MAN["generator"]["agent_sha256"] == s2.AGENT_SHA256
    assert all("prompt_user.txt" not in f["path"] and "response" not in f["path"] for f in MAN["files"])


def test_run_facts():
    assert MAN["counts"] == s2.RUN_FACTS and MAN["checks_reproduced"] is True
    assert MAN["format_corrective_items"] == list(s2.FORMAT_CORRECTIVE_ITEMS)
    assert [x["seed_id"] for x in MAN["http_retries_recovered"]] == ["SD2-TP1-00069", "SD2-TP1-02787"]
    assert MAN["http_retries_recovered"][1]["reason"].startswith("HTTP 502")
    assert [x["run"] for x in MAN["superseded_runs"]] == ["run0_rung1", "run1"]
    assert [x["observed"]["deterministic_pass"] for x in MAN["superseded_runs"]] == [0, 0]
    assert MAN["source_commit"] == s2.SOURCE_COMMIT and MAN["endpoint"]["model"] == "openai/gpt-oss-120b"
    s = json.loads((s2.ART / "summary.json").read_text(encoding="utf-8"))
    assert s["by_level"] == {"1": 2, "3": 4, "4": 3, "7": 1}


def test_items_are_in_human_review_and_valid(items):
    assert [it["item_id"] for it in items] == IDS
    run = {it["item_id"]: it for it in s2.read_items(s2.ART / "items.jsonl")}
    schema = bi.load_schema()
    for it in items:
        r = it["review"]
        assert r["status"] == "human_review" and r["kaiyuan_disposition"] is None and r["mentor_disposition"] is None
        assert r["final_frozen"] is None and [h["event"] for h in r["history"]] == ["deterministic_pass", "human_review"]
        assert r["history"][1]["decision"] == "D-056" and r["history"][1]["at"] == MAN["ingested_at"]
        assert bi.schema_errors(it, schema) == [] and bi.consistency_errors(it) == []
        before = copy.deepcopy(it)
        before["review"]["status"] = "deterministic_pass"
        before["review"]["history"] = before["review"]["history"][:1]
        assert before == run[it["item_id"]]                                       # nothing but the lifecycle step
        assert it["source_leakage_check"]["pass"] and it["source_leakage_check"]["flags"] == []
    assert not any(bi.validity(it)["benchmark_valid"] for it in items)          # condition F: nothing is accepted


def test_the_lifecycle_step_takes_only_a_passed_item(items):
    x = copy.deepcopy(items[0])
    x["review"]["status"] = "rejected_pre_review"
    with pytest.raises(ValueError, match="status rejected_pre_review"):
        s2.human_review_item(x, "2026-11-02T00:00:00Z")


def test_post_checks_reproduce_from_tracked_files(items):
    rep = s2.reproduce_checks(items)
    assert rep["checks_reproduced"] and [x["item_id"] for x in rep["items"]] == IDS and all(x["pass"] for x in rep["items"])
    assert [x["item_id"] for x in rep["items"] if x["first_check_reasons"]] == list(s2.FORMAT_CORRECTIVE_ITEMS)
    recorded = MAN["checks"]                                                      # in items.jsonl order
    assert {k: v for k, v in rep.items() if k != "items"} == {k: v for k, v in recorded.items() if k != "items"}
    assert rep["items"] == sorted(recorded["items"], key=lambda x: x["item_id"])


# --- rubric lint v1 -------------------------------------------------------------------------------------------------


def _item(level=3, prompt="How will hot days change?", rubric=None, lit=(), points=()):
    rub = {k: [] for k in rl.RUBRIC_LISTS} | (rubric or {})
    return {"item_id": "BI-X", "use_case_level": level, "prompt": prompt, "rubric": rub,
            "review": {"history": [{"reference_answer_tagged": {"literature_interpretation": list(lit), "rubric_points": list(points)}}]}}


def test_lint_rules_on_hand_made_items():
    strengths = {"LG-m": "multi_source_supported", "LG-s": "single_source_supported", "LG-s2": "single_source_supported"}
    it = _item(rubric={"fatal_errors": ["Using numbers not listed in allowed_numbers.", "Calling RCP8.5 a forecast."],
                       "required_points": ["[w=3] Cite a multi-source supported driver", "[w=2] Upper tercile among states",
                                           "[w=2] Humidity matters"],
                       "disallowed_claims": ["A mechanism not provided in the packet"]},
               lit=[{"sentence": "One study reports warming.", "group_ids": ["LG-m"]},
                    {"sentence": "One study reports humidity.", "group_ids": ["LG-s"]},
                    {"sentence": "A single study reports both.", "group_ids": ["LG-m", "LG-s"]}],
               points=[{"field": "required_points", "point": "Cite a ...", "source_ids": ["TP1-1"]},
                       {"field": "required_points", "point": "Upper tercile", "source_ids": ["TP1-1", "LG-s"]},
                       {"field": "required_points", "point": "Humidity matters", "source_ids": ["LG-s", "LG-s2"]},
                       {"field": "optional_points", "point": "x", "source_ids": ["LG-s"]}])
    fl = rl.lint_item(it, strengths)
    got = sorted((f["rule"], f["field"], f["index"]) for f in fl)
    assert got == sorted([("generation_constraint", "rubric.fatal_errors", 0), ("generation_constraint", "rubric.required_points", 0),
                          ("generation_constraint", "rubric.disallowed_claims", 0), ("required_tercile", "rubric.required_points", 1),
                          ("required_single_source_only", "rubric.required_points", 2),
                          ("hedge_strength_mismatch", "reference_answer.literature_interpretation", 0)])
    assert rl.lint_item(_item(level=1, prompt="What causes it, and why, because of what driver?"), {})[0]["detail"] == "matches 'cause'"
    assert rl.lint_item(_item(level=1, prompt="How much, because of warming?"), {}) == []      # "because" is not "cause"
    assert rl.lint_item(_item(level=3, prompt="What are the drivers?"), {}) == []              # rung 1 only


def test_the_lint_report_rebuilds_and_edits_nothing(items):
    report = json.loads((s2.ART / "rubric_lint_v1.json").read_text(encoding="utf-8"))
    strengths = {it["item_id"]: s2.packet_at_source(it["review"]["history"][0]["seed_id"])[0]["checks_input"]["group_strength"]
                 for it in items}
    again = rl.lint(items, strengths)
    assert {k: report[k] for k in again} == again and report["edits_made"] == 0
    assert report["totals"]["all"] == 25 and [x["n_flags"] for x in report["items"]] == [2, 3, 2, 4, 2, 2, 1, 7, 1, 1]


# --- the item review CSV --------------------------------------------------------------------------------------------


def test_items_csv_rebuilds_from_tracked_files():
    man, items, packets, lint, notes, item_sha = rv.inputs()
    assert sha256_file(rv.COORDINATOR_NOTES_PATH) == rv.COORDINATOR_NOTES_SHA256 and sorted(notes) == IDS
    rows = rv.item_rows(items, packets, lint, notes)
    assert rv.items_csv(rows) == rv.ITEMS_CSV_PATH.read_text(encoding="utf-8")
    h = rows[0]
    assert h[:4] == ["item_id", "rung", "capability_tested", "prompt"] and h[-11:] == rv.REVIEWER_COLS
    assert h.index("coordinator_disposition") == h.index("kaiyuan_disposition") - 2
    assert all(r[-11:] == [""] * 11 for r in rows[1:])
    assert [r[h.index("coordinator_disposition")] for r in rows[1:]] == ["accept_with_edits"] * 9 + ["regenerate"]
    prov = rv.provenance_rows(items, packets, item_sha)
    assert len(prov) - 1 == 10 and all(r[prov[0].index("table_data_is_fulldata_manifest_sha256")] is True for r in prov[1:])
    assert all(r[prov[0].index("packet_version")] == "synthpackets v3a" for r in prov[1:])
    assert len(rv.group_rows(items, packets)) - 1 == len({g for it in items for g, _ in rv.cited_groups(it)})
