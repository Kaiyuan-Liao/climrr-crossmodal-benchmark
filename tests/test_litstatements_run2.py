"""Literature-statement run 2 ingest --- `scripts/ingest_litstatements.py` (pilot P2a Phase A; D-044).

Checks the ingested copy, not the delivered tarball (which stays outside the repository):
every manifest hash; the run facts; ids `LS-<item_id>-<nn>`; the four evidence roles and
their rule; `statements_ingested.jsonl` re-derived from the per-paper files; DR-LIT-IND-1
with authors absent and present; the parse-error counts; run 1 recorded, not ingested.
"""

from __future__ import annotations

import json
import re

import pytest

from climrr import litstatements_run2 as r2
from climrr.checksums import sha256_file

MAN = json.loads(r2.MANIFEST_PATH.read_text(encoding="utf-8"))
META = json.loads(r2.PAPERS_META_PATH.read_text(encoding="utf-8"))
PERR = json.loads(r2.PARSE_ERRORS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def records():
    return [json.loads(ln) for ln in r2.INGESTED_PATH.read_text(encoding="utf-8").splitlines()]


def test_every_manifest_file_matches_its_hash():
    assert MAN["tarball"]["sha256"] == r2.TARBALL_SHA256
    for f in MAN["files"]:
        p = r2.ART / f["path"]
        assert sha256_file(p) == f["sha256"] and p.stat().st_size == f["bytes"], f["path"]
    assert len([f for f in MAN["files"] if f["path"].startswith("papers/")]) == 243
    assert len(MAN["excluded_files"]) == 2 * 243
    assert {f["path"].rsplit("/", 1)[1] for f in MAN["excluded_files"]} == set(r2.EXCLUDED_NAMES)
    assert not list(r2.ART.rglob("prompt_user.txt")) and not list(r2.ART.rglob("response.json"))


def test_the_delivered_run_files_are_the_pinned_ones():
    assert sha256_file(r2.STATEMENTS_PATH) == r2.STATEMENTS_SHA256
    assert sha256_file(r2.ART / "summary.json") == r2.SUMMARY_SHA256
    assert (r2.ART / "agent.log").read_bytes() == (r2.ART / "litstatements_run2.log").read_bytes()


def test_run_facts_are_reproduced():
    k = MAN["counts"]
    assert (k["papers"], k["statements"], k["deterministic_pass"], k["rejected_pre_review"]) == (243, 1018, 485, 533)
    assert k["rejected_by_check"] == dict(sorted(r2.REJECTED_BY_CHECK.items()))
    assert k["papers_with_error"] == 0 and k["parse_errors"] == 21
    assert MAN["endpoint"] == {"endpoint_label": "sophia_vllm", "model": "openai/gpt-oss-120b", "base_url": r2.BASE_URL, "papers": 243}
    assert MAN["generator"]["agent_sha256"].startswith("f70edbb3") and MAN["generator"]["agent_sha256"].endswith("1d370d6")
    assert MAN["generator"]["system_prompt_sha256"].startswith("fbedadd2") and MAN["source_commit"].startswith("7919bbf")
    assert MAN["ingested_by"] == "EXECUTOR" and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", MAN["ingested_at"])


def test_run1_is_recorded_as_superseded_only():
    (s,) = MAN["superseded_runs"]
    assert {k: s[k] for k in ("run", "endpoint", "papers", "reason", "decision")} == \
        {"run": "run1", "endpoint": "metis", "papers": 2, "reason": "gateway timeouts", "decision": "D-043"}
    assert s["observed"]["papers_with_statements"] == ["134230133", "154007324"]
    assert not any(f["path"].startswith("run1") for f in MAN["files"])


def test_ingested_records_rederive_from_the_paper_files(records):
    rebuilt = r2.ingested_records()
    assert [json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rebuilt] == \
        [json.dumps(r, ensure_ascii=False, sort_keys=True) for r in records]
    agent = [json.loads(ln) for ln in r2.STATEMENTS_PATH.read_text(encoding="utf-8").splitlines()]
    assert sorted(r["agent_statement_id"] for r in records) == sorted(a["statement_id"] for a in agent)


def test_ids_name_paper_and_position(records):
    ids = [r["statement_id"] for r in records]
    assert len(set(ids)) == len(ids) == 1018
    for r in records:
        assert re.fullmatch(r"LS-\d+-\d\d", r["statement_id"])
        assert r["statement_id"] == "L" + r["agent_statement_id"]
        assert r["statement_id"].split("-")[1] == r["paper_item_id"]


def test_role_counts(records):
    assert r2.role_counts(records) == {"core_candidate": 379, "cited_candidate": 106,
                                       "background_consensus_candidate": 262, "unusable": 271}
    assert MAN["counts"]["evidence_roles"] == r2.role_counts(records)


def test_pre_check_fields(records):
    for r in records:
        assert r["precheck_status"] == ("pass" if r["status"] == "deterministic_pass" else "rejected")
        assert r["rejected_checks"] == r["pre_review_checks"]["failed"] and r["recovery"] == r["passage_recovery"]
        assert (r["rejected_checks"] == []) == (r["precheck_status"] == "pass")


def _rec(status, ptype, failed, resliced=True):
    return {"status": status, "proposal": {"passage_type": ptype},
            "pre_review_checks": {"failed": failed, "span_reslice_pass": resliced}}


@pytest.mark.parametrize("rec,role", [
    (_rec("deterministic_pass", "own_finding", []), "core_candidate"),
    (_rec("deterministic_pass", "own_projection", []), "core_candidate"),
    (_rec("deterministic_pass", "review_synthesis", []), "core_candidate"),
    (_rec("deterministic_pass", "cited_finding", []), "cited_candidate"),
    (_rec("rejected_pre_review", "background", ["passage_type_pass"]), "background_consensus_candidate"),
    (_rec("rejected_pre_review", "background", ["span_reslice_pass", "passage_type_pass"], resliced=False), "unusable"),
    (_rec("rejected_pre_review", "background", ["passage_type_pass", "statement_value_pass"]), "unusable"),
    (_rec("rejected_pre_review", "caveat", ["enums_valid", "passage_type_pass"]), "unusable"),
    (_rec("rejected_pre_review", "own_finding", ["passage_length_pass"]), "unusable"),
])
def test_evidence_role_rule(rec, role):
    assert r2.evidence_role(rec) == role


def test_background_candidates_only_failed_the_background_check(records):
    for r in records:
        if r["evidence_role"] == "background_consensus_candidate":
            assert r["rejected_checks"] == ["passage_type_pass"] and r["proposal"]["passage_type"] == "background"
            assert r["evidence"] is not None and r["verbatim_passage"]


def test_independence_without_authors():
    assert META["independence_fields_available"] == {"year": False, "venue": False, "authors": False}
    assert META["author_check"] == "unavailable" and META["independence_basis"] == "assumed_independent_distinct_ids"
    assert len(META["papers"]) == 243 and all(p["authors"] is None and p["year"] is None for p in META["papers"])
    assert r2.independent("1", "2") == (True, "assumed_independent_distinct_ids")
    assert r2.independent("1", "1") == (False, "same_id")
    assert r2.n_independent(["3", "1", "3", "2"]) == 3


def test_independence_with_authors_uses_surname_and_initial():
    meta = {"a": {"authors": [{"surname": "Smith", "initial": "J"}]}, "b": {"authors": [{"surname": "smith", "initial": "j"}]},
            "c": {"authors": [{"surname": "Smith", "initial": "K"}]}}
    assert r2.independent("a", "b", meta) == (False, "author_check")
    assert r2.independent("a", "c", meta) == (True, "author_check")
    assert r2.n_independent(["a", "b", "c"], meta) == 2


def test_independence_diagnostics_are_recorded():
    assert META["diagnostic_same_file_sha256"] == [["239052352", "257056592"]]
    assert ["239052352", "257056592"] in META["diagnostic_same_title_section"]


def test_parse_errors_are_counts_only():
    assert len(PERR) == 21 and sorted(p["item_id"] for p in PERR) == \
        sorted((r2.ART / "run2_parse_error_ids.txt").read_text().split())
    assert all(p["finish_reason"] == "length" and p["completion_tokens"] == 3500 for p in PERR)
    assert all(set(p) == {"item_id", "arm", "paper_chars", "truncated", "model_parse_error", "finish_reason",
                          "completion_tokens", "content_chars", "reasoning_chars"} for p in PERR)


def test_parse_log():
    log = r2.parse_log((r2.ART / "agent.log").read_text(encoding="utf-8"))
    assert log["paper_lines"] == 243 and log["retry_lines"] == 10 and log["fail_lines"] == 0
    assert log["done"] == {"papers": "243", "statements": "1018", "pass": "485", "reject": "533"}
