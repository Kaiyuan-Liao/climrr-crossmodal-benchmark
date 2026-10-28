"""Track C run 1 (agent v1, Polaris): verification, ingest, counts, triage and v2-locator replay (D-029, D-030, D-033).

Run 1 is a **diagnostic and a candidate pool**, not accepted QA. The delivered
`softqa_run1.tar.gz` holds `softqa/run1/<item_id>/{prompt_user.txt, response.json,
result.json}` for 243 papers, `candidates.jsonl`, `summary.json`, `agent.log` and
`reports/softqa_run1.log`.

Ingest keeps `result.json` (its passages are evidence excerpts, at most 700
characters each), `candidates.jsonl`, `summary.json` and both logs. It **excludes**
`prompt_user.txt` (the full paper text --- the corpus stays external) and
`response.json` (it carries passages and model reasoning); their SHA-256 are kept
in `excluded_files.csv`. Every `candidates.jsonl` record is mapped onto
`candidate_schema_v1.json` (`candidates_schema.jsonl`) and must validate.

The locator replay (`scripts/softqa_replay_locator.py`) runs agent v2's
`locate_passage` over every run-1 proposal against the paper sections rebuilt
from `prompt_user.txt` (the agent's own `[SECTION: key]` join, checked against
`paper_chars` and `n_sections`); each prompt's SHA-256 is checked against
`excluded_files.csv` first. A truncated paper is replayed against the text the
model saw (at most 90,000 characters), not the full paper.

Nothing here calls a model, reads a table value, or changes the concept map,
a column status or a compatibility rule.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import re
import shutil
from collections import Counter
from pathlib import Path

from climrr import softqa
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

DIAGNOSTIC_ID = "softqa_run1"
SOFTQA_ART = REPO_ROOT / "artifacts" / "softqa"
RUN_DIR = SOFTQA_ART / "run1"
RUN_MANIFEST = RUN_DIR / "manifest.csv"
EXCLUDED_CSV = RUN_DIR / "excluded_files.csv"
SCHEMA_JSONL = RUN_DIR / "candidates_schema.jsonl"
LOG_PATH = SOFTQA_ART / "softqa_run1.log"
REPLAY_PATH = SOFTQA_ART / "run1_locator_replay_v2.json"
BATCH_PATH = SOFTQA_ART / "review_batch_01.json"
FORMS_DIR = SOFTQA_ART / "review_batch_01_forms"
DOC_PATH = REPO_ROOT / "docs" / "SOFTQA_TRACKC_RUN1.md"
MANIFEST = REPO_ROOT / "data" / "manifest.json"
AGENT = REPO_ROOT / "scripts" / "litcollect" / "softqa_agent.py"
UNITS = softqa.SOFTQA_DIR / "units_definitions_v1.json"
QA_TYPES = softqa.SOFTQA_DIR / "qa_types_v1.json"
CANDIDATES = softqa.SOFTQA_DIR / "trackc_candidates_v1.json"
FORM = softqa.SOFTQA_DIR / "review_form_v1.yaml"

TARBALL_SHA256 = "8a0e444996cc09a87c848aa9013e228d39a3f831e7a701519eb7db41f3654e3e"
SOURCE_COMMIT = "95e1ec851f2ac703654df52ac1ccc9c3d777fcd7"
V1_AGENT_SHA256 = "159e2c5c4f00608da37b1bc85556fecfd82dbd2e1a5abfd10c59a2e46061397c"
V1_SYSTEM_PROMPT_SHA256 = "f2e493e179aa3619c8389e5c1756cce8f9a13693ddd586eae59138de33ee54f5"
V2_AGENT_SHA256 = "25a79a5b8bebbb67c8e080b05d08b736ee40ea62fbe3fc891d86cfab22f63b9c"
V2_SYSTEM_PROMPT_SHA256 = "a44181ee23441118e67364d80004d0a796a747bfbd3f66a9cf89e987cdfef319"
INDEX_IDENTITY = "fbb4affb71622e07259182ec4922d1496b47fa09ad08396d6e4ceaa8eeb77a94"
MODEL = "gpt-oss-120b"
GENERATOR_VERSION = "softqa_agent v1"
MAX_CHARS = 90000
TRUNC_MARK = "\n\n[PAPER TRUNCATED]"
EXCLUDED_NAMES = ("prompt_user.txt", "response.json")
PASSAGE_WINDOW = 700  # the prompt's "at most 700 characters"; the minimal-window premise of the ingest

#: The run's totals as the DONE line states them; re-derived from the records.
RUN_FACTS = {"papers": 243, "groups": 193, "deterministic_pass": 103, "rejected_pre_review": 90}

#: Triage rule for review batch 01 (work package, deterministic).
TRIAGE_ROLES = ("study_area", "cited_study_area")
TRIAGE_MAX_UNMATCHED = 2

#: Mandatory checks in the agent's order; a rejection's reasons are the ones that are False.
REJECT_CHECKS = ("unit_id_known", "qa_type_known", "span_reslice_pass", "concept_location_pass",
                 "place_location_pass", "place_role_recorded", "proposal_fields_complete")


def canonical_sha256(path: Path) -> str:
    """The agent's input hash: SHA-256 of `json.dumps(obj, sort_keys=True)` (not of the file bytes)."""
    return hashlib.sha256(json.dumps(json.loads(Path(path).read_text(encoding="utf-8")),
                                     sort_keys=True).encode("utf-8")).hexdigest()


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]


# --- verification of the delivered run ------------------------------------------

def parse_log(text: str) -> dict:
    lines = text.splitlines()
    start = [ln for ln in lines if " START " in ln]
    done = [ln for ln in lines if " DONE " in ln]
    if len(start) != 1 or len(done) != 1:
        raise ValueError(f"expected one START and one DONE line, found {len(start)} and {len(done)}")
    kv = lambda ln: dict(re.findall(r"(\w+)=(\S+)", ln))  # noqa: E731
    return {"start": kv(start[0]), "done": kv(done[0]), "start_utc": start[0].split()[0],
            "end_utc": done[0].split()[0], "paper_lines": len(lines) - 2}


def expected_pins() -> dict:
    return {"candidates": str(RUN_FACTS["papers"]), "units": "5", "qa_types": "6", "model": MODEL,
            "units_sha": canonical_sha256(UNITS)[:12], "qa_sha": canonical_sha256(QA_TYPES)[:12],
            "system_sha": V1_SYSTEM_PROMPT_SHA256[:12], "index": INDEX_IDENTITY[:12]}


def verify_log(text: str) -> dict:
    log = parse_log(text)
    for k, v in expected_pins().items():
        if log["start"].get(k) != v:
            raise ValueError(f"log START {k}={log['start'].get(k)!r}, expected {v!r}")
    done = {"papers": "papers", "groups": "groups", "deterministic_pass": "pass", "rejected_pre_review": "reject"}
    for k, field in done.items():
        if log["done"].get(field) != str(RUN_FACTS[k]):
            raise ValueError(f"log DONE {field}={log['done'].get(field)!r}, expected {RUN_FACTS[k]}")
    if log["paper_lines"] != RUN_FACTS["papers"]:
        raise ValueError(f"{log['paper_lines']} paper lines in the log, expected {RUN_FACTS['papers']}")
    return log


def _aggregate(run: Path) -> tuple[list[dict], dict]:
    """The agent's own end-of-run aggregation, replayed: `candidates.jsonl` and `summary.json` from every result.json."""
    allc, summary = [], {"papers": 0, "groups": 0, "deterministic_pass": 0, "rejected_pre_review": 0,
                         "by_qa_type": {}, "by_unit": {}, "by_concept_relation": {}, "by_place_role": {}}
    for p in sorted(run.glob("*/result.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        if "candidates" not in r:
            continue
        summary["papers"] += 1
        for x in r["candidates"]:
            allc.append(x)
            summary["groups"] += 1
            summary[x["status"]] += 1
            g = x["proposal"]
            for key, field in (("by_qa_type", "qa_type"), ("by_unit", "unit_id"),
                               ("by_concept_relation", "concept_relation"), ("by_place_role", "paper_geography_role")):
                summary[key][str(g.get(field))] = summary[key].get(str(g.get(field)), 0) + 1
    return allc, summary


def verify_run(run: Path, *, with_excluded: bool) -> dict:
    """Check a run directory (the delivered one, or the ingested copy without the excluded files)."""
    papers = sorted(p for p in run.iterdir() if p.is_dir())
    ids = [str(c["item_id"]) for c in json.loads(CANDIDATES.read_text(encoding="utf-8"))]
    if sorted(p.name for p in papers) != sorted(ids):
        raise ValueError("paper directories differ from trackc_candidates_v1.json")
    want = {"result.json", *EXCLUDED_NAMES} if with_excluded else {"result.json"}
    for p in papers:
        have = {f.name for f in p.iterdir()}
        if have != want:
            raise ValueError(f"{p.name}: files {sorted(have)}, expected {sorted(want)}")
    allc, summary = _aggregate(run)
    if _jsonl(run / "candidates.jsonl") != allc:
        raise ValueError("candidates.jsonl differs from the result.json files")
    if json.loads((run / "summary.json").read_text(encoding="utf-8")) != summary:
        raise ValueError("summary.json differs from the result.json files")
    for k, v in RUN_FACTS.items():
        if summary[k] != v:
            raise ValueError(f"summary {k}={summary[k]}, expected {v}")
    pins = {"source_commit": SOURCE_COMMIT, "generator_version": GENERATOR_VERSION, "generator_model": MODEL,
            "system_prompt_sha256": V1_SYSTEM_PROMPT_SHA256, "units_sha256": canonical_sha256(UNITS),
            "qa_types_sha256": canonical_sha256(QA_TYPES), "table_values_visible_to_generator": False,
            "answer_visible_to_generator": False}
    for c in allc:
        for k, v in pins.items():
            if c[k] != v:
                raise ValueError(f"{c['candidate_id']}: {k}={c[k]!r}, expected {v!r}")
    return {"papers": len(papers), "candidates": len(allc), "summary": summary}


def verify_source(src: Path) -> dict:
    run = src / "softqa" / "run1"
    agent_log = (run / "agent.log").read_bytes()
    if (src / "reports" / "softqa_run1.log").read_bytes() != agent_log:
        raise ValueError("reports/softqa_run1.log differs from softqa/run1/agent.log")
    log = verify_log(agent_log.decode("utf-8"))
    return {"log": log, **verify_run(run, with_excluded=True)}


# --- ingest -----------------------------------------------------------------------

def _csv(rows: list[list]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["rel_path", "bytes", "sha256"])
    w.writerows(rows)
    return buf.getvalue()


def excluded_text(src_run: Path) -> str:
    """`excluded_files.csv`: the files not copied (prompt_user.txt, response.json), with their bytes and SHA-256."""
    rows = []
    for p in sorted(src_run.glob("*/*"), key=lambda q: q.relative_to(src_run).as_posix()):
        if p.name in EXCLUDED_NAMES:
            rows.append([p.relative_to(src_run).as_posix(), p.stat().st_size, sha256_file(p)])
    return _csv(rows)


def manifest_text(run: Path = RUN_DIR) -> str:
    """`manifest.csv`: every file under the ingested run except itself, code-point order."""
    rows = []
    for p in sorted(run.rglob("*"), key=lambda q: q.relative_to(run).as_posix()):
        rel = p.relative_to(run).as_posix()
        if p.is_file() and rel != "manifest.csv":
            rows.append([rel, p.stat().st_size, sha256_file(p)])
    return _csv(rows)


def _put(src: Path, dst: Path) -> None:
    """Copy, or check that an existing copy is byte-identical (rerunnable ingest)."""
    if dst.exists():
        if dst.read_bytes() != src.read_bytes():
            raise ValueError(f"{dst} exists and differs from the delivered file")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def copy_run(src: Path, dest: Path = RUN_DIR, log_dest: Path = LOG_PATH) -> int:
    src_run = src / "softqa" / "run1"
    n = 0
    for p in sorted(src_run.glob("*/result.json")):
        _put(p, dest / p.parent.name / "result.json")
        n += 1
    for name in ("candidates.jsonl", "summary.json", "agent.log"):
        _put(src_run / name, dest / name)
        n += 1
    _put(src / "reports" / "softqa_run1.log", log_dest)
    return n


def write_schema_jsonl(run: Path = RUN_DIR, out: Path = SCHEMA_JSONL) -> list[dict]:
    recs = softqa.map_and_validate_jsonl(run / "candidates.jsonl")
    text = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in recs)
    if out.exists() and out.read_text(encoding="utf-8") != text:
        raise ValueError(f"{out} exists and differs from a fresh mapping")
    out.write_text(text, encoding="utf-8")
    return recs


# --- counts and triage ----------------------------------------------------------------

def load_candidates(run: Path = RUN_DIR) -> list[dict]:
    return _jsonl(run / "candidates.jsonl")


def load_results(run: Path = RUN_DIR) -> dict[str, dict]:
    return {p.parent.name: json.loads(p.read_text(encoding="utf-8")) for p in sorted(run.glob("*/result.json"))}


def counts(run: Path = RUN_DIR) -> dict:
    cands, results = load_candidates(run), load_results(run)
    single, combos = Counter(), Counter()
    advisory = Counter()
    for c in cands:
        ch = c["pre_review_checks"]
        if c["status"] == "rejected_pre_review":
            fails = tuple(k for k in REJECT_CHECKS if ch.get(k) is False)
            combos[" + ".join(fails)] += 1
            single.update(fails)
        advisory[(c["status"], ch.get("question_has_no_table_number"))] += 1
    groups_hist = Counter(r["n_groups_proposed"] for r in results.values())
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    return {
        "papers": len(results),
        "groups": len(cands),
        "papers_with_zero_groups": groups_hist.get(0, 0),
        "groups_per_paper": dict(sorted(groups_hist.items())),
        "deterministic_pass": sum(c["status"] == "deterministic_pass" for c in cands),
        "rejected_pre_review": sum(c["status"] == "rejected_pre_review" for c in cands),
        "rejection_reason_counts_incl_combos": {k: single[k] for k in REJECT_CHECKS if single[k]},
        "rejection_combinations": dict(sorted(combos.items(), key=lambda kv: (-kv[1], kv[0]))),
        "question_has_no_table_number_false": {
            "deterministic_pass": advisory[("deterministic_pass", False)],
            "rejected_pre_review": advisory[("rejected_pre_review", False)]},
        "truncated_papers": sum(r["truncated"] for r in results.values()),
        "model_parse_errors": sum(bool(r["model_parse_error"]) for r in results.values()),
        "passages_over_700_chars": {c["candidate_id"]: [len(c["proposal"].get("passage") or ""), c["status"]]
                                    for c in sorted(cands, key=lambda c: c["candidate_id"])
                                    if len(c["proposal"].get("passage") or "") > PASSAGE_WINDOW},
        "by_qa_type": summary["by_qa_type"], "by_unit": summary["by_unit"],
        "by_concept_relation": summary["by_concept_relation"], "by_place_role": summary["by_place_role"],
    }


def triage(cands: list[dict]) -> list[dict]:
    """deterministic_pass AND concept_relation direct AND place role study_area / cited_study_area AND
    at most two unmatched dimensions; order = candidate_id."""
    out = []
    for c in cands:
        p = c["proposal"]
        if (c["status"] == "deterministic_pass" and p.get("concept_relation") == "direct"
                and p.get("paper_geography_role") in TRIAGE_ROLES
                and len(p.get("unmatched_dimensions") or []) <= TRIAGE_MAX_UNMATCHED):
            out.append(c)
    return sorted(out, key=lambda c: c["candidate_id"])


# --- v2 locator replay ------------------------------------------------------------------

def load_agent(path: Path = AGENT):
    """The tracked agent as a module (its top-level `import duckdb` needs duckdb installed)."""
    spec = importlib.util.spec_from_file_location("softqa_agent_tracked", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sections_from_prompt(user: str) -> tuple[list[dict], bool]:
    """Rebuild the sections the agent showed the model from its `prompt_user.txt`.

    The agent writes `PAPER (item …; arm …):\\n` then `"\\n\\n".join("[SECTION: key]\\ntext")`, cut at
    `--max-chars`, then the truncation mark. `section_idx` here is the ordinal among the string
    sections, not the index's `section_idx` (which also counts non-string entries).
    """
    body = user.split("\n\nPAPER (item ", 1)[1].split(":\n", 1)[1]
    truncated = body.endswith(TRUNC_MARK)
    if truncated:
        body = body[: -len(TRUNC_MARK)]
    if not body.startswith("[SECTION: "):
        raise ValueError("paper text does not start with a section marker")
    secs = []
    for i, part in enumerate(body[len("[SECTION: "):].split("\n\n[SECTION: ")):
        key, _, text = part.partition("\n")
        if not key.endswith("]"):
            raise ValueError(f"malformed section header {key[:60]!r}")
        secs.append({"section_idx": i, "section_key": key[:-1], "text": text})
    if "\n\n".join(f"[SECTION: {s['section_key']}]\n{s['text']}" for s in secs) != body:
        raise ValueError("rebuilt sections do not reproduce the prompt's paper text")
    return secs, truncated


_TERM = re.compile(r"[.!?](?=\s|$)")


def replay(src_run: Path, run: Path = RUN_DIR, agent=None) -> dict:
    """Run agent v2's `locate_passage` over every run-1 proposal (sections rebuilt from the prompts)."""
    agent = agent or load_agent()
    excluded = {row["rel_path"]: row["sha256"] for row in
                csv.DictReader(io.StringIO((run / "excluded_files.csv").read_text(encoding="utf-8")))}
    results = load_results(run)
    sections, checks = {}, {"prompt_sha256_match": 0, "untruncated_reproduce_paper_chars_and_n_sections": 0,
                            "truncated": 0}
    for iid, r in results.items():
        p = src_run / iid / "prompt_user.txt"
        if sha256_file(p) != excluded[f"{iid}/prompt_user.txt"]:
            raise ValueError(f"{iid}: prompt_user.txt differs from excluded_files.csv")
        checks["prompt_sha256_match"] += 1
        secs, truncated = sections_from_prompt(p.read_text(encoding="utf-8"))
        if truncated != r["truncated"]:
            raise ValueError(f"{iid}: truncation flag differs from result.json")
        if truncated:
            checks["truncated"] += 1
        else:
            text = "\n\n".join(f"[SECTION: {s['section_key']}]\n{s['text']}" for s in secs)
            if len(text) != r["paper_chars"] or len(secs) != r["n_sections"]:
                raise ValueError(f"{iid}: rebuilt paper differs from paper_chars / n_sections")
            checks["untruncated_reproduce_paper_chars_and_n_sections"] += 1
        sections[iid] = secs

    rows, tally, by_v1 = [], Counter(), Counter()
    resliced = 0
    for c in load_candidates(run):
        passage = c["proposal"].get("passage") or ""
        secs = sections[c["paper_item_id"]]
        span, method, verbatim = agent.locate_passage(passage, secs)
        v1 = bool(c["pre_review_checks"].get("span_reslice_pass"))
        tally[method] += 1
        by_v1[f"v1_{'pass' if v1 else 'fail'}->{method}"] += 1
        row = {"candidate_id": c["candidate_id"], "paper_item_id": c["paper_item_id"],
               "v1_span_reslice_pass": v1, "v2_passage_recovery": method,
               "paper_truncated": results[c["paper_item_id"]]["truncated"], "proposal_chars": len(passage)}
        if span is not None:
            sec = next(s for s in secs if s["section_idx"] == span["section_idx"])
            ok = sec["text"][span["span_start"]:span["span_end"]] == verbatim
            resliced += ok
            row.update(json_path=span["json_path"], span_start=span["span_start"], span_end=span["span_end"],
                       recovered_chars=len(verbatim), recovered_sha256=hashlib.sha256(verbatim.encode()).hexdigest(),
                       recovered_reslices=ok)
        if method == "normalized":
            mapped = sorted({f"U+{ord(ch):04X}" for ch in passage + verbatim if ord(ch) in agent._TRANS})
            row["typographic_codepoints"] = mapped
            row["whitespace_only"] = not mapped
        if method == "not_found":
            prefix = agent.norm_plain(passage)[:80]
            hits = sum(agent.norm_with_map(s["text"])[0].count(prefix) for s in secs) if len(prefix) >= 60 else None
            row["prefix80_occurrences"] = hits
        rows.append(row)
    return {
        "replay": "agent v2 locate_passage over the run-1 proposals",
        "agent_sha256": sha256_file(AGENT),
        "run1_candidates_sha256": sha256_file(run / "candidates.jsonl"),
        "input_checks": checks,
        "n_proposals": len(rows),
        "recovery": {k: tally.get(k, 0) for k in ("exact", "normalized", "prefix_anchor", "not_found")},
        "v1_to_v2": dict(sorted(by_v1.items())),
        "recovered_reslice_ok": resliced,
        "v1_failures_in_truncated_papers": sum(1 for r in rows if not r["v1_span_reslice_pass"]
                                               and r["paper_truncated"]),
        "rows": rows,
    }


# --- manifest entry and generated doc --------------------------------------------------

def manifest_entry(manifest_sha: str, n_files: int, total: int, log: dict, excluded_sha: str) -> dict:
    return {
        "diagnostic_id": DIAGNOSTIC_ID,
        "role": ("Track C run 1 (softqa_agent v1) --- a diagnostic and a candidate pool, not accepted QA; every "
                 "candidate is llm_candidate -> deterministic_pass / rejected_pre_review; no human review, no "
                 "table value; FWI is a fire-danger index, never fire occurrence"),
        "manifest_path": repo_rel(RUN_MANIFEST),
        "manifest_sha256": manifest_sha,
        "n_files": n_files,
        "total_bytes": total,
        "log_path": repo_rel(LOG_PATH),
        "log_sha256": sha256_file(LOG_PATH),
        "source_tarball_sha256": TARBALL_SHA256,
        "not_copied": {
            "files": list(EXCLUDED_NAMES),
            "reason": ("prompt_user.txt holds the full paper text (the corpus stays external); response.json holds "
                       "passages and model reasoning; SHA-256 of each kept in excluded_files.csv"),
            "excluded_files_csv_sha256": excluded_sha,
        },
        "run": {
            "host": "Polaris (Kaiyuan); login node `unknown` --- not recorded in the run outputs",
            "python": "`unknown` --- not recorded in the run outputs",
            "model": MODEL,
            "endpoint": "https://inference-api.alcf.anl.gov/resource_server/metis/api/v1",
            "start_utc": log["start_utc"], "end_utc": log["end_utc"],
            "source_commit": SOURCE_COMMIT,
            "agent_sha256": V1_AGENT_SHA256,
            "system_prompt_sha256": V1_SYSTEM_PROMPT_SHA256,
            "units_sha256_as_loaded": canonical_sha256(UNITS),
            "units_file_sha256": sha256_file(UNITS),
            "qa_types_sha256_as_loaded": canonical_sha256(QA_TYPES),
            "qa_types_file_sha256": sha256_file(QA_TYPES),
            "hash_note": "the agent hashes json.dumps(obj, sort_keys=True), not the file bytes; both recorded",
            "index_content_identity_sha256": INDEX_IDENTITY,
        },
        "decision_ref": "D-029, D-030, D-033",
    }


def repo_rel(p: Path) -> str:
    return Path(p).relative_to(REPO_ROOT).as_posix()


def _table(rows: list[tuple], head: tuple) -> list[str]:
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return out


def render_doc() -> str:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry = next(d for d in data["diagnostics"] if d["diagnostic_id"] == DIAGNOSTIC_ID)
    k = counts()
    tri = triage(load_candidates())
    rp = json.loads(REPLAY_PATH.read_text(encoding="utf-8")) if REPLAY_PATH.exists() else None
    L = ["# Track C run 1 --- ingest, counts, locator replay, triage",
         "",
         "*Generated by `scripts/ingest_softqa_run1.py` / `scripts/softqa_replay_locator.py` from "
         "`artifacts/softqa/`; do not edit by hand.* Run 1 is a **diagnostic and a candidate pool**: every "
         "candidate is `llm_candidate` → `deterministic_pass` or `rejected_pre_review`. **No candidate is "
         "accepted QA**, none has been human-reviewed, and no table value has been computed. The Fire Weather "
         "Index is a meteorological fire-danger index, never fire occurrence; historical periods are modeled "
         "baselines.",
         "",
         "## 1. Provenance",
         ""]
    run = entry["run"]
    L += _table([
        ("Source tarball", f"`{TARBALL_SHA256}`"),
        ("Executed", f"Polaris, {run['start_utc']} → {run['end_utc']}; login node and Python `unknown` (not in the outputs)"),
        ("Agent", f"`softqa_agent v1`, `{V1_AGENT_SHA256}` (tracked at `{SOURCE_COMMIT[:7]}`)"),
        ("Source commit", f"`{SOURCE_COMMIT}` (every record)"),
        ("Model", f"`{MODEL}` (Metis)"),
        ("System prompt", f"`{V1_SYSTEM_PROMPT_SHA256}`"),
        ("Units, as loaded", f"`{run['units_sha256_as_loaded']}` (log `units_sha={run['units_sha256_as_loaded'][:12]}`)"),
        ("Units, file", f"`{run['units_file_sha256']}`"),
        ("QA types, as loaded", f"`{run['qa_types_sha256_as_loaded']}` (log `qa_sha={run['qa_types_sha256_as_loaded'][:12]}`)"),
        ("QA types, file", f"`{run['qa_types_file_sha256']}`"),
        ("Index identity", f"`{INDEX_IDENTITY}`"),
        ("Ingested", f"`{entry['manifest_path']}` `{entry['manifest_sha256']}`, {entry['n_files']} files, "
                     f"{entry['total_bytes']:,} bytes"),
        ("Not copied", "`prompt_user.txt` (full paper text), `response.json` (passages, reasoning); SHA-256 in "
                       f"`excluded_files.csv` `{entry['not_copied']['excluded_files_csv_sha256']}`"),
    ], ("", ""))
    L += ["", "The agent hashes its inputs as `json.dumps(obj, sort_keys=True)`; the as-loaded hashes therefore "
          "differ from the file hashes by construction. Both are recorded, and each as-loaded hash is "
          "recomputed from the tracked file.", "",
          "## 2. Totals", ""]
    L += _table([
        ("papers", k["papers"]), ("proposals (groups)", k["groups"]),
        ("papers with 0 proposals", k["papers_with_zero_groups"]),
        ("proposals per paper", ", ".join(f"{n}: {c}" for n, c in k["groups_per_paper"].items())),
        ("`deterministic_pass`", k["deterministic_pass"]), ("`rejected_pre_review`", k["rejected_pre_review"]),
        ("truncated papers (> 90,000 chars)", k["truncated_papers"]), ("model parse errors", k["model_parse_errors"]),
        ("proposed passages over 700 chars", len(k["passages_over_700_chars"])),
    ], ("", "n"))
    over = k["passages_over_700_chars"]
    L += ["", "**Passages over the 700-character window** (the prompt asked for at most 700): "
          + "; ".join(f"`{i}` {n} chars, {s}" for i, (n, s) in over.items())
          + ". They are kept verbatim in `result.json` / `candidates.jsonl` (not truncated: that would break the "
          "record and its hash) and flagged for the COORDINATOR."]
    L += ["", "## 3. Rejection reasons", "", "A rejected proposal can fail more than one check.", ""]
    L += _table(list(k["rejection_reason_counts_incl_combos"].items()), ("check failed (incl. combinations)", "n"))
    L += [""]
    L += _table(list(k["rejection_combinations"].items()), ("exact combination", "n"))
    adv = k["question_has_no_table_number_false"]
    L += ["", f"Advisory flag `question_has_no_table_number` = false (not a rejection reason): "
          f"{adv['deterministic_pass']} `deterministic_pass`, {adv['rejected_pre_review']} `rejected_pre_review`. "
          "The flag is a crude digit-plus-unit pattern; it also fires on a threshold quoted from the paper "
          "(e.g. `124 °F`).", "",
          "## 4. Distributions (from `summary.json`, all 193 proposals)", ""]
    for key, title in (("by_qa_type", "qa_type"), ("by_unit", "unit"), ("by_concept_relation", "concept_relation"),
                       ("by_place_role", "paper_geography_role")):
        L += _table(sorted(k[key].items(), key=lambda kv: (-kv[1], kv[0])), (title, "n")) + [""]
    L += ["## 5. Re-slice failures --- agent v2 locator replay", ""]
    if rp is None:
        L += ["**Pending** --- run `scripts/softqa_replay_locator.py`.", ""]
    else:
        rec = rp["recovery"]
        ic = rp["input_checks"]
        L += [f"`scripts/softqa_replay_locator.py` ran agent v2's `locate_passage` (agent `{rp['agent_sha256'][:12]}…`) "
              f"over all {rp['n_proposals']} run-1 proposals, against sections rebuilt from `prompt_user.txt` "
              f"({ic['prompt_sha256_match']} prompt hashes matched `excluded_files.csv`; "
              f"{ic['untruncated_reproduce_paper_chars_and_n_sections']} untruncated papers reproduce `paper_chars` "
              f"and `n_sections`; {ic['truncated']} truncated papers replayed against the 90,000 characters the model "
              f"saw). Output: `{repo_rel(REPLAY_PATH)}`.", ""]
        L += _table([(m, rec[m]) for m in ("exact", "normalized", "prefix_anchor", "not_found")],
                    ("v2 recovery", "n"))
        L += ["", "| v1 → v2 | n |", "| --- | --- |"] + [f"| {a} | {b} |" for a, b in rp["v1_to_v2"].items()]
        norm = [r for r in rp["rows"] if r["v2_passage_recovery"] == "normalized"]
        cps = Counter(cp for r in norm for cp in r.get("typographic_codepoints", []))
        L += ["", f"**Diagnosis of the {rec['normalized'] + rec['prefix_anchor'] + rec['not_found']} v1 re-slice "
              f"failures:** {rec['normalized']} typographic variants (`normalized`; code points involved: "
              + ", ".join(f"{c} ×{n}" for c, n in sorted(cps.items())) + "); "
              f"{rec['prefix_anchor']} altered tails recovered by prefix anchoring to one sentence with ≥ 0.6 word "
              f"overlap (`prefix_anchor`); {rec['not_found']} not found in the text the model saw. "
              f"Recoverable in total: {rec['normalized'] + rec['prefix_anchor']}. "
              f"Every recovered span re-slices to its recovered text ({rp['recovered_reslice_ok']} of "
              f"{rec['exact'] + rec['normalized'] + rec['prefix_anchor']}). "
              f"{rp['v1_failures_in_truncated_papers']} of the v1 failures are in truncated papers.", ""]
        nf = Counter(str(r.get("prefix80_occurrences")) for r in rp["rows"] if r["v2_passage_recovery"] == "not_found")
        L += ["Not-found proposals by occurrences of their first 80 normalized characters in the shown text "
              "(`None` = proposal too short for an anchor): "
              + ", ".join(f"{a}: {b}" for a, b in sorted(nf.items())) + ".", ""]
    L += ["## 6. Triage for review batch 01", "",
          "Deterministic rule: `deterministic_pass` AND `concept_relation` = `direct` AND `paper_geography_role` "
          f"∈ {{study_area, cited_study_area}} AND ≤ {TRIAGE_MAX_UNMATCHED} unmatched dimensions → "
          f"**{len(tri)} candidates** (order = `candidate_id`). These are model annotations used as a sort key, "
          "not judgments.", ""]
    rows = []
    for c in tri:
        p = c["proposal"]
        gate = "hold_owner_confirmation" if p["unit_id"] in softqa.FWI_HOLD_UNITS else (
            "column check at table stage" if p["unit_id"] == "F-FWI" else "clear")
        rows.append((f"`{c['candidate_id']}`", p["unit_id"], p["qa_type"],
                     ", ".join(p["unmatched_dimensions"]) or "(none)", p["geography_relation"], gate))
    L += _table(rows, ("candidate", "unit", "qa_type", "unmatched", "geography_relation", "acceptance gate"))
    L += ["", "P-CELL-1 / P-COUNTY-1 candidates may be reviewed but cannot be accepted until the FWI columns "
          "(IC-006, IC-008, IC-010) are owner-confirmed (D-033 addendum; `docs/SOFTQA_REVIEW_PROTOCOL.md` §11). "
          "F-FWI candidates are checked by their column ids once the table stage records them.", ""]
    return "\n".join(L) + "\n"
