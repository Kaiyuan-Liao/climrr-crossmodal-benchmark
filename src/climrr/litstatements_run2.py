"""Literature-statement run 2 (agent v2, Polaris, Sophia vLLM): verification, ingest, evidence roles, independence (pilot P2a; D-043, D-044).

The delivered `litstatements_run2_evidence.tar.gz` holds `litstatements/run2/<item_id>/
{prompt_user.txt, response.json, result.json}` for 243 papers, `statements.jsonl`,
`summary.json` and `agent.log`; `litstatements/run1/` (the interrupted Metis attempt,
recorded only, never ingested); `reports/litstatements_run{1,2}.log`; and
`reports/run2_parse_error_ids.txt`.

Ingest copies, into `artifacts/litstatements/run2/`, `statements.jsonl`, `summary.json`,
`agent.log`, both report logs and the parse-error id list, and every `result.json` to
`papers/<item_id>.json` byte-identical (it holds only passages already in the corpus).
`prompt_user.txt` (the full paper text --- the corpus stays external) and
`response.json` (passages and model reasoning) are **not** copied, as for Track C run 1;
their SHA-256 go into `manifest.json`. From each parse-error paper's `response.json`
only counts are read (finish reason, completion tokens, characters of content and of
reasoning), never its text.

Every statement gets an id `LS-<item_id>-<nn>` (nn = its position in the paper's
statement list) and an **evidence role** (work package Phase A; D-044):

- `core_candidate` --- `deterministic_pass` and passage_type own_finding / own_projection / review_synthesis;
- `cited_candidate` --- `deterministic_pass` and passage_type cited_finding;
- `background_consensus_candidate` --- rejected **only** by `passage_type_pass`, the
  passage_type is `background`, and the passage re-sliced;
- `unusable` --- everything else.

**DR-LIT-IND-1** (independence): two papers are independent when their ids differ and,
if authors are available, they share no author surname + initial; with authors
unavailable the basis is `assumed_independent_distinct_ids` and `author_check:
unavailable`. The corpus index (`build_index.py`) stores per document only `doc_id,
rel_path, bytes, sha256, n_sections, n_nonstring, parse_ok`, and per section
`section_key, text`: **no year, venue or author field**. Two diagnostics that DR-LIT-IND-1
does not use are recorded beside it: papers whose file SHA-256 is equal, and papers
whose `title` section is equal after lowercasing and whitespace collapse.

Nothing here calls a model, reads a table value, or changes the concept map, a column
status or a compatibility rule.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

RUN_ID = "litstatements_run2"
ART = REPO_ROOT / "artifacts" / "litstatements" / "run2"
PAPERS_DIR = ART / "papers"
MANIFEST_PATH = ART / "manifest.json"
STATEMENTS_PATH = ART / "statements.jsonl"
INGESTED_PATH = ART / "statements_ingested.jsonl"
PAPERS_META_PATH = ART / "papers_meta.json"
PARSE_ERRORS_PATH = ART / "parse_errors.json"

TARBALL_SHA256 = "7d9077392ceb961035790a9dc3c89d9a825aabe56bca5ce0184ad674b9ffc414"
STATEMENTS_SHA256 = "26ba676c004adb0bdb7018b0e748b30f0d8eee0225c968e48786fecb2742a15f"
SUMMARY_SHA256 = "4da75e2d4cd3ba700afb6b13ecfe206bd8d1d531f6d7eed5e0a75d5ae1cf9a78"
AGENT_V2_SHA256 = "f70edbb33929354c4a5a3d3786f72c49ad41d201032a778725f3d004a1d370d6"
SYSTEM_PROMPT_SHA256 = "fbedadd25a8a6a048983f9ed3c49997c73c4de771e9f5d689dacd9f56cb01fff"
SOURCE_COMMIT = "7919bbfbaa1aecd56e39808e3728d7e06cf4ae1f"
INDEX_IDENTITY_PREFIX = "fbb4affb7162"
GENERATOR_VERSION = "litstatement_agent v2"
ENDPOINT_LABEL, MODEL = "sophia_vllm", "openai/gpt-oss-120b"
BASE_URL = "https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1"
ENDPOINT = f"{ENDPOINT_LABEL} {MODEL}"

#: The run's facts as the work package states them; the ingest fails if any differs.
RUN_FACTS = {"papers": 243, "statements": 1018, "deterministic_pass": 485, "rejected_pre_review": 533,
             "papers_with_error": 0, "parse_errors": 21}
REJECTED_BY_CHECK = {"passage_type_pass": 340, "span_reslice_pass": 129, "enums_valid": 84,
                     "statement_value_pass": 90, "passage_length_pass": 7}

SUPERSEDED_RUNS = [{"run": "run1", "endpoint": "metis", "papers": 2, "reason": "gateway timeouts", "decision": "D-043"}]

ROLES = ("core_candidate", "cited_candidate", "background_consensus_candidate", "unusable")
CORE_PASSAGE_TYPES = ("own_finding", "own_projection", "review_synthesis")
EXCLUDED_NAMES = ("prompt_user.txt", "response.json")
COPIED = {  # source (relative to the extracted tarball) -> destination name under ART
    "litstatements/run2/statements.jsonl": "statements.jsonl",
    "litstatements/run2/summary.json": "summary.json",
    "litstatements/run2/agent.log": "agent.log",
    "reports/litstatements_run2.log": "litstatements_run2.log",
    "reports/litstatements_run1.log": "litstatements_run1.log",
    "reports/run2_parse_error_ids.txt": "run2_parse_error_ids.txt",
}

#: The corpus index's stored fields (scripts/litcollect/build_index.py).
INDEX_DOC_FIELDS = ("doc_id", "rel_path", "bytes", "sha256", "n_sections", "n_nonstring", "parse_ok")
INDEX_SECTION_FIELDS = ("doc_id", "rel_path", "section_idx", "section_key", "text")
INDEPENDENCE_FIELDS = ("year", "venue", "authors")
DR_LIT_IND_1 = ("DR-LIT-IND-1: two papers are independent when their item ids differ and (authors unavailable -> "
                "basis assumed_independent_distinct_ids, author_check unavailable; authors available -> they share no "
                "author surname + initial). Equal file SHA-256 and equal title sections are recorded as diagnostics; "
                "the rule does not use them.")


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]


def _run(src: Path) -> Path:
    return Path(src) / "litstatements" / "run2"


def _result_paths(run: Path) -> list[Path]:
    return sorted(run.glob("*/result.json"))  # the agent's own order (summarise)


def parse_log(text: str) -> dict:
    lines = text.splitlines()
    start = [ln for ln in lines if " START " in ln]
    done = [ln for ln in lines if " DONE " in ln]
    if len(start) != 1 or len(done) != 1:
        raise ValueError(f"expected one START and one DONE line, found {len(start)} and {len(done)}")
    kv = lambda ln: dict(re.findall(r"(\w+)=(\S+)", ln))  # noqa: E731
    return {"start": kv(start[0]), "done": kv(done[0]), "start_utc": start[0].split()[0], "end_utc": done[0].split()[0],
            "paper_lines": sum(1 for ln in lines if " arm=" in ln), "retry_lines": sum(1 for ln in lines if " RETRY " in ln),
            "fail_lines": sum(1 for ln in lines if " FAIL " in ln)}


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def verify_source(src: Path) -> dict:
    """Every run-2 fact the work package states, re-derived from the delivered files. Raises on any difference."""
    src, run = Path(src), _run(src)
    _check(sha256_file(run / "statements.jsonl") == STATEMENTS_SHA256, "statements.jsonl SHA-256 differs")
    _check(sha256_file(run / "summary.json") == SUMMARY_SHA256, "summary.json SHA-256 differs")
    results = [json.loads(p.read_text(encoding="utf-8")) for p in _result_paths(run)]
    _check(len(results) == RUN_FACTS["papers"], f"{len(results)} result.json, expected {RUN_FACTS['papers']}")
    _check(all("statements" in r for r in results), "a result.json records an error")
    # statements.jsonl is the agent's concatenation of every result.json, in path order
    lines = [json.dumps(x, ensure_ascii=False) for r in results for x in r["statements"]]
    _check((run / "statements.jsonl").read_text(encoding="utf-8") == "".join(ln + "\n" for ln in lines),
           "statements.jsonl is not the concatenation of the result.json files")
    recs = [x for r in results for x in r["statements"]]
    k = Counter(x["status"] for x in recs)
    _check(len(recs) == RUN_FACTS["statements"], f"{len(recs)} statements, expected {RUN_FACTS['statements']}")
    for s in ("deterministic_pass", "rejected_pre_review"):
        _check(k[s] == RUN_FACTS[s], f"{k[s]} {s}, expected {RUN_FACTS[s]}")
    by_check = Counter(c for x in recs for c in x["pre_review_checks"]["failed"])
    _check(dict(by_check) == REJECTED_BY_CHECK, f"rejected_by_check {dict(by_check)} differs")
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    for key in ("papers", "statements", "deterministic_pass", "rejected_pre_review", "papers_with_error"):
        _check(summary[key] == RUN_FACTS[key], f"summary {key}={summary[key]}, expected {RUN_FACTS[key]}")
    _check(summary["rejected_by_check"] == REJECTED_BY_CHECK, "summary rejected_by_check differs")
    _check(summary["endpoints_in_results"] == {f"{ENDPOINT} {BASE_URL}": RUN_FACTS["papers"]}, "summary endpoints differ")
    for r in results:
        _check(f"{r['endpoint_label']} {r['model']}" == ENDPOINT and r["base_url"] == BASE_URL, f"{r['item_id']}: endpoint")
        _check(r["generator_version"] == GENERATOR_VERSION, f"{r['item_id']}: generator {r['generator_version']}")
        for i, x in enumerate(r["statements"], 1):
            _check(x["statement_id"] == f"S-{r['item_id']}-{i:02d}", f"{x['statement_id']}: not at position {i}")
            _check(x["system_prompt_sha256"] == SYSTEM_PROMPT_SHA256, f"{x['statement_id']}: system prompt")
            _check(x["source_commit"] == SOURCE_COMMIT, f"{x['statement_id']}: source commit {x['source_commit']}")
            _check(f"{x['endpoint_label']} {x['model']}" == ENDPOINT, f"{x['statement_id']}: endpoint")
    perr = sorted(r["item_id"] for r in results if r["model_parse_error"])
    listed = (src / "reports" / "run2_parse_error_ids.txt").read_text(encoding="utf-8").split()
    _check(len(perr) == RUN_FACTS["parse_errors"] and sorted(listed) == perr, "parse-error ids differ from the results")
    agent_log = (run / "agent.log").read_text(encoding="utf-8")
    _check(agent_log == (src / "reports" / "litstatements_run2.log").read_text(encoding="utf-8"),
           "agent.log and reports/litstatements_run2.log differ")
    log = parse_log(agent_log)
    exp = {"candidates": str(RUN_FACTS["papers"]), "endpoint_label": ENDPOINT_LABEL, "model": MODEL, "base_url": BASE_URL,
           "system_sha": SYSTEM_PROMPT_SHA256[:12], "index": INDEX_IDENTITY_PREFIX}
    for key, v in exp.items():
        _check(log["start"].get(key) == v, f"log START {key}={log['start'].get(key)!r}, expected {v!r}")
    for key, field in (("papers", "papers"), ("statements", "statements"), ("deterministic_pass", "pass"),
                       ("rejected_pre_review", "reject")):
        _check(log["done"].get(field) == str(RUN_FACTS[key]), f"log DONE {field}={log['done'].get(field)!r}")
    _check(log["paper_lines"] == RUN_FACTS["papers"] and log["fail_lines"] == 0, "log paper / FAIL lines")
    return {"log": log, "parse_error_ids": perr, "run1": run1_facts(src)}


def run1_facts(src: Path) -> dict:
    """Run 1 as delivered, for the record only (its statements are never ingested)."""
    run1 = Path(src) / "litstatements" / "run1"
    dirs = sorted(p for p in run1.iterdir() if p.is_dir())
    with_statements, http_errors, prompt_only = [], [], []
    for d in dirs:
        if not (d / "result.json").exists():
            prompt_only.append(d.name)
            continue
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        (with_statements if r.get("statements") else http_errors).append(d.name)
    log = (Path(src) / "reports" / "litstatements_run1.log").read_text(encoding="utf-8")
    start = re.search(r"START (litstatement_agent v\d+)", log)
    return {"paper_dirs": len(dirs), "papers_with_statements": with_statements, "papers_with_http_error": http_errors,
            "papers_prompt_only": prompt_only, "generator_version": start.group(1) if start else None}


# --- copy ---------------------------------------------------------------------------------------


def _copy(src_file: Path, dest: Path) -> bool:
    """Copy byte-identical; an existing copy must already be identical. True if copied."""
    if dest.exists():
        if sha256_file(dest) != sha256_file(src_file):
            raise ValueError(f"{dest} exists and differs from {src_file.name}")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src_file, dest)
    return True


def copy_run(src: Path) -> int:
    src, n = Path(src), 0
    for rel, name in COPIED.items():
        n += _copy(src / rel, ART / name)
    for p in _result_paths(_run(src)):
        n += _copy(p, PAPERS_DIR / f"{p.parent.name}.json")
    return n


def excluded_files(src: Path) -> list[dict]:
    run = _run(src)
    return [{"path": f"litstatements/run2/{p.parent.name}/{p.name}", "sha256": sha256_file(p), "bytes": p.stat().st_size}
            for p in sorted(run.glob("*/*")) if p.name in EXCLUDED_NAMES]


# --- parse errors (counts only) ------------------------------------------------------------------


def parse_error_diagnostics(src: Path, ids: list[str]) -> list[dict]:
    """Per parse-error paper: arm, chars, truncated, and from response.json only counts --- no text."""
    run, out = _run(src), []
    for iid in ids:
        r = json.loads((run / iid / "result.json").read_text(encoding="utf-8"))
        resp = json.loads((run / iid / "response.json").read_text(encoding="utf-8"))
        ch = resp["choices"][0]
        msg = ch.get("message") or {}
        reasoning = msg.get("reasoning_content") or msg.get("reasoning") or ""
        out.append({"item_id": iid, "arm": r["arm"], "paper_chars": r["paper_chars"], "truncated": r["truncated"],
                    "model_parse_error": r["model_parse_error"], "finish_reason": ch.get("finish_reason"),
                    "completion_tokens": (resp.get("usage") or {}).get("completion_tokens"),
                    "content_chars": len(msg.get("content") or ""), "reasoning_chars": len(reasoning)})
    return out


# --- evidence roles -----------------------------------------------------------------------------


def evidence_role(rec: dict) -> str:
    ptype = rec["proposal"].get("passage_type")
    failed = rec["pre_review_checks"]["failed"]
    if rec["status"] == "deterministic_pass":
        if ptype in CORE_PASSAGE_TYPES:
            return "core_candidate"
        if ptype == "cited_finding":
            return "cited_candidate"
        return "unusable"  # unreachable: a passing record has a valid, non-background passage_type
    if failed == ["passage_type_pass"] and ptype == "background" and rec["pre_review_checks"]["span_reslice_pass"]:
        return "background_consensus_candidate"
    return "unusable"


def ingest_record(rec: dict) -> dict:
    iid, nn = rec["paper_item_id"], rec["statement_id"].rsplit("-", 1)[1]
    out = {"statement_id": f"LS-{iid}-{nn}", "agent_statement_id": rec["statement_id"]}
    out.update({k: v for k, v in rec.items() if k != "statement_id"})
    out.update({"precheck_status": "pass" if rec["status"] == "deterministic_pass" else "rejected",
                "rejected_checks": list(rec["pre_review_checks"]["failed"]), "recovery": rec["passage_recovery"],
                "evidence_role": evidence_role(rec)})
    return out


def ingested_records(papers_dir: Path = PAPERS_DIR) -> list[dict]:
    """Every statement of every ingested result.json, in the agent's order, with id, role and pre-check fields."""
    out = []
    for p in sorted(papers_dir.glob("*.json"), key=lambda q: q.stem):
        r = json.loads(p.read_text(encoding="utf-8"))
        out.extend(ingest_record(x) for x in r["statements"])
    return out


def role_counts(records: list[dict]) -> dict:
    k = Counter(r["evidence_role"] for r in records)
    return {role: k.get(role, 0) for role in ROLES}


# --- independence metadata ------------------------------------------------------------------------


def _title(prompt: str) -> str | None:
    m = re.search(r"\[SECTION: title\]\n(.*?)(?:\n\n\[SECTION: |\n\n\[PAPER TRUNCATED\]|\Z)", prompt, re.S)
    return m.group(1) if m else None


def _norm_title(t: str) -> str:
    return " ".join(t.lower().split())


def papers_meta(src: Path) -> dict:
    """Independence metadata for the 243 papers (DR-LIT-IND-1) and the two diagnostics it does not use."""
    run, papers = _run(src), []
    for p in _result_paths(run):
        r = json.loads(p.read_text(encoding="utf-8"))
        title = _title((p.parent / "prompt_user.txt").read_text(encoding="utf-8"))
        rel = r["statements"][0]["paper_rel_path"] if r["statements"] else None
        papers.append({"item_id": r["item_id"], "arm": r["arm"], "paper_sha256": r["paper_sha256"], "rel_path": rel,
                       "year": None, "venue": None, "authors": None, "author_check": "unavailable",
                       "title_section_present": title is not None,
                       "title_normalized_sha256": hashlib.sha256(_norm_title(title).encode("utf-8")).hexdigest() if title else None})
    papers.sort(key=lambda x: x["item_id"])

    def groups(key):
        g: dict[str, list[str]] = {}
        for x in papers:
            if x[key]:
                g.setdefault(x[key], []).append(x["item_id"])
        return sorted(v for v in g.values() if len(v) > 1)

    return {"rule": DR_LIT_IND_1, "rule_id": "DR-LIT-IND-1",
            "index_fields": {"docs": list(INDEX_DOC_FIELDS), "sections": list(INDEX_SECTION_FIELDS)},
            "independence_fields_available": {f: False for f in INDEPENDENCE_FIELDS},
            "author_check": "unavailable", "independence_basis": "assumed_independent_distinct_ids",
            "n_title_section_present": sum(x["title_section_present"] for x in papers),
            "diagnostic_same_file_sha256": groups("paper_sha256"),
            "diagnostic_same_title_section": groups("title_normalized_sha256"),
            "papers": papers}


def independent(a: str, b: str, meta_by_id: dict | None = None) -> tuple[bool, str]:
    """DR-LIT-IND-1 for two paper ids: (independent, basis)."""
    if a == b:
        return False, "same_id"
    ma, mb = (meta_by_id or {}).get(a, {}), (meta_by_id or {}).get(b, {})
    if ma.get("authors") and mb.get("authors"):
        key = lambda au: {(x["surname"].lower(), x["initial"].lower()) for x in au}  # noqa: E731
        return (not (key(ma["authors"]) & key(mb["authors"]))), "author_check"
    return True, "assumed_independent_distinct_ids"


def n_independent(ids, meta_by_id: dict | None = None) -> int:
    """Size of a set of mutually independent papers, chosen greedily in ascending id order (deterministic)."""
    chosen: list[str] = []
    for i in sorted(set(ids)):
        if all(independent(i, j, meta_by_id)[0] for j in chosen):
            chosen.append(i)
    return len(chosen)


# --- manifest ---------------------------------------------------------------------------------


def _file_entry(path: Path) -> dict:
    return {"path": path.relative_to(ART).as_posix(), "sha256": sha256_file(path), "bytes": path.stat().st_size}


def manifest(src_facts: dict, excluded: list[dict], records: list[dict], ingested_at: str | None = None) -> dict:
    files = [_file_entry(ART / name) for name in COPIED.values()]
    files += [_file_entry(p) for p in sorted(PAPERS_DIR.glob("*.json"), key=lambda q: q.stem)]
    files += [_file_entry(p) for p in (INGESTED_PATH, PAPERS_META_PATH, PARSE_ERRORS_PATH)]
    by_check = Counter(c for r in records for c in r["rejected_checks"])
    return {
        "run": "run2", "diagnostic_id": RUN_ID, "decision": "D-044",
        "tarball": {"name": "litstatements_run2_evidence.tar.gz", "sha256": TARBALL_SHA256},
        "counts": {"papers": RUN_FACTS["papers"], "statements": len(records),
                   "deterministic_pass": sum(r["precheck_status"] == "pass" for r in records),
                   "rejected_pre_review": sum(r["precheck_status"] == "rejected" for r in records),
                   "rejected_by_check": dict(sorted(by_check.items())), "papers_with_error": 0,
                   "parse_errors": len(src_facts["parse_error_ids"]), "evidence_roles": role_counts(records)},
        "generator": {"version": GENERATOR_VERSION, "agent_sha256": AGENT_V2_SHA256, "system_prompt_sha256": SYSTEM_PROMPT_SHA256},
        "endpoint": {"endpoint_label": ENDPOINT_LABEL, "model": MODEL, "base_url": BASE_URL, "papers": RUN_FACTS["papers"]},
        "source_commit": SOURCE_COMMIT,
        "log": {"start_utc": src_facts["log"]["start_utc"], "end_utc": src_facts["log"]["end_utc"],
                "retry_lines": src_facts["log"]["retry_lines"], "fail_lines": src_facts["log"]["fail_lines"]},
        "statement_ids": "LS-<item_id>-<nn>, nn = position in the paper's statement list (the agent's S-<item_id>-<nn>)",
        "superseded_runs": [dict(SUPERSEDED_RUNS[0], observed=src_facts["run1"])],
        "files": files, "excluded_files": excluded,
        "ingested_at": ingested_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ingested_by": "EXECUTOR",
    }


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
