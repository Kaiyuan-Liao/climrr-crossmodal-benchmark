"""Track B survey run 1: ingest the Polaris output as a diagnostic artifact; render the coverage doc.

**Diagnostic only (D-025, D-026).** Nothing here touches `concept_map.yaml`, any
column status, index 117 or a production query. Every count is a *diagnostic
coverage count, not prevalence*; every model-proposed term is a
`candidate_surface_form` and inert (`docs/BRIDGE_ELIGIBILITY.md` section 7).

The input is `survey_run1.tar.gz` extracted outside the repository
(`survey/run1/`, `reports/survey_run1.log`, `scripts/`). `verify_source` checks
it against the tracked tools, the pinned inventory, context clause and index
identity, and re-derives every row's counts from its id files, before anything
is copied. `copy_run` copies all of `survey/run1/` except `_duckdb_tmp`
directories and the header-only `topical/hits.csv` files (`run_query.py
--no-hits`; their absence is recorded). `render_doc` builds
`docs/CONCEPT_COVERAGE_SURVEY.md` from the ingested rows only.
"""

from __future__ import annotations

import csv
import io
import json
import shutil
from pathlib import Path

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
INVENTORY = REPO_ROOT / "data" / "metadata" / "dictionary_concepts.yaml"
CONTEXT = REPO_ROOT / "data" / "metadata" / "litcollect" / "survey_context_clause_v1.txt"
MANIFEST = REPO_ROOT / "data" / "manifest.json"
SURVEY_DIR = REPO_ROOT / "artifacts" / "literature" / "survey"
RUN_DIR = SURVEY_DIR / "run1"
RUN_MANIFEST = RUN_DIR / "manifest.csv"
LOG_PATH = SURVEY_DIR / "survey_run1.log"
DOC_PATH = REPO_ROOT / "docs" / "CONCEPT_COVERAGE_SURVEY.md"
L2_RUNS = REPO_ROOT / "artifacts" / "literature" / "litcorpus02" / "evidence" / "runs"

DIAGNOSTIC_ID = "TRACKB-SURVEY-RUN1"

#: The v3 tools that executed run 1 (D-026); the tracked files must equal them.
TOOL_SHA256 = {
    "run_query.py": "5f56ee49f0da675f49ef490b506c030b307c693032e8be9097e499cf1c64030d",
    "survey_driver.py": "e1fb664c98e4ff866bb348c8930bfc1b9243957441b8a19ea0893e0b711af4cd",
}

HITS_HEADER = "doc_id,rel_path,sha256,group,term,section_key,section_idx,char_start,char_end"
LABEL = "diagnostic coverage count, not prevalence"

#: The run, as stated by Kaiyuan in the work package (host, environment, the aborted
#: first attempt, the untracked-copy execution) and as read from the run's own files
#: (start/end, DuckDB, model, endpoint, hashes). `verify_source` checks the second kind.
RUN_FACTS = {
    "host": "polaris-login-01 (Polaris login node)",
    "environment": "module conda/2026-10-01 + conda env globus_env",
    "python": "3.11.x (patch version not recorded in any run output)",
    "duckdb": "1.5.4",
    "model": "gpt-oss-120b",
    "endpoint": "https://inference-api.alcf.anl.gov/resource_server/metis/api/v1",
    "start_utc": "2026-10-20T21:54:34Z",
    "end_utc": "2026-10-20T22:09:18Z",
    "execution": ("executed from untracked copies in the litcollect `scripts/` folder whose "
                  "SHA-256 equal the tracked v3 files"),
    "prior_attempt": "an aborted first attempt (offsets stage; no outputs kept)",
}

QUESTIONS = [
    ("Q-a", "report coverage at both levels — authorize a run-2 prompt variant that asks for the "
            "*family* name of the quantity (one row per dictionary concept, same provenance, "
            "labelled diagnostic)?"),
    ("Q-b", "treat threshold measures as lexically unsearchable and survey them only at family level?"),
    ("Q-c", "may the sanitizer accept `°`, `>` and `%` by normalizing to words (`degrees f`, `above`, "
            "`percent`) — or is any transformation of a model term out of bounds?"),
]


class SurveyIngestError(RuntimeError):
    """The delivered run does not match its pins, or a copy differs from its source."""


def _ids(path: Path) -> set[str]:
    return set(path.read_text(encoding="utf-8").split())


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _concept_dirs(run: Path) -> list[Path]:
    return sorted(p for p in run.iterdir() if p.is_dir() and p.name.startswith("DC-"))


def _index_identity() -> str:
    corpora = _json(MANIFEST)["external_corpora"]
    return next(c for c in corpora if c["corpus_id"] == "LITCORPUS-02-conceptfirst-705k-v1")[
        "index_content_identity_sha256"]


def verify_run(run: Path) -> list[dict]:
    """Check a run directory (delivered or ingested) and return its rows sorted by concept id."""
    problems: list[str] = []
    inv_sha, ctx_sha, idx_id = sha256_file(INVENTORY), sha256_file(CONTEXT), _index_identity()
    ctx_summary = _json(run / "_context" / "summary.json")
    ctx = _ids(run / "_context" / "ids.txt")
    if ctx_summary["query_sha256"] != ctx_sha:
        problems.append("_context: query SHA-256 is not the pinned context clause")
    if ctx_summary["index"]["content_identity_sha256"] != idx_id:
        problems.append("_context: index identity differs from LITCORPUS-02")
    if ctx_summary["admitted_count"] != len(ctx) or ctx_summary["hits_recorded"] is not False:
        problems.append("_context: count/ids mismatch or hits recorded")
    if ctx_summary["duckdb_version"] != RUN_FACTS["duckdb"]:
        problems.append("_context: DuckDB version differs from RUN_FACTS")
    rows = []
    for d in _concept_dirs(run):
        row, cand = _json(d / "row.json"), _json(d / "candidates.json")
        cid = d.name
        if row["concept_id"] != cid or cand["concept_id"] != cid:
            problems.append(f"{cid}: concept id mismatch")
        if (row["inventory_sha256"], row["context_clause_sha256"], row["index_content_identity_sha256"]) != (
                inv_sha, ctx_sha, idx_id):
            problems.append(f"{cid}: inventory / context / index pin mismatch")
        if cand["status"] != "candidate_surface_form":
            problems.append(f"{cid}: candidates not labelled candidate_surface_form")
        if (cand["model"], cand["endpoint"]) != (RUN_FACTS["model"], RUN_FACTS["endpoint"]):
            problems.append(f"{cid}: model / endpoint differ from RUN_FACTS")
        if cand["prompt_sha256"] != sha256_file(d / "prompt.txt"):
            problems.append(f"{cid}: prompt SHA-256 mismatch")
        if not row["label"].startswith("diagnostic"):
            problems.append(f"{cid}: row not labelled diagnostic")
        if row["status"] == "ok":
            topical = _ids(d / "topical" / "ids.txt")
            summ = _json(d / "topical" / "summary.json")
            both = _ids(d / "topical_and_context_ids.txt")
            if row["topical_query_sha256"] != sha256_file(d / "query_topical.txt"):
                problems.append(f"{cid}: topical query SHA-256 mismatch")
            if not (row["topical_only_count"] == len(topical) == summ["admitted_count"]):
                problems.append(f"{cid}: topical count != ids")
            if not (row["context_filtered_count"] == len(both) == len(topical & ctx)) or both != topical & ctx:
                problems.append(f"{cid}: context-filtered count != |topical ∩ context|")
            if summ["hits_recorded"] is not False:
                problems.append(f"{cid}: hits recorded (expected --no-hits)")
            terms = {k.split(":", 1)[1]: v for k, v in summ["per_term_doc_counts"].items()}
            if terms != row["per_term_doc_counts"]:
                problems.append(f"{cid}: per-term counts differ between row and summary")
        elif row["topical_only_count"] is not None or row["context_filtered_count"] is not None:
            problems.append(f"{cid}: error row carries a count")
        rows.append({"row": row, "candidates": cand})
    if len(rows) != 14:
        problems.append(f"expected 14 concept rows, found {len(rows)}")
    if problems:
        raise SurveyIngestError("; ".join(problems))
    return rows


def verify_source(src: Path) -> list[dict]:
    """The extracted tarball: tools equal the tracked v3 files, then the run itself."""
    for name, sha in TOOL_SHA256.items():
        if sha256_file(TOOLS / name) != sha:
            raise SurveyIngestError(f"tracked {name} is not the v3 file")
        if sha256_file(src / "scripts" / name) != sha:
            raise SurveyIngestError(f"delivered {name} is not the v3 file")
    run = src / "survey" / "run1"
    for h in run.glob("DC-*/topical/hits.csv"):
        if h.read_text(encoding="utf-8").splitlines() != [HITS_HEADER]:
            raise SurveyIngestError(f"{h.relative_to(src)} is not header-only; refusing to drop it")
    if sha256_file(src / "reports" / "survey_run1.log") != sha256_file(run / "survey.log"):
        raise SurveyIngestError("reports/survey_run1.log differs from survey/run1/survey.log")
    return verify_run(run)


def _excluded(rel: Path) -> bool:
    return "_duckdb_tmp" in rel.parts or (rel.name == "hits.csv" and rel.parent.name == "topical")


def copy_run(src: Path) -> dict:
    """Copy the run into `RUN_DIR` (or confirm an existing copy is byte-identical)."""
    run = src / "survey" / "run1"
    copied, skipped_hits, skipped_tmp = [], [], []
    for p in sorted(run.rglob("*")):
        rel = p.relative_to(run)
        if "_duckdb_tmp" in rel.parts:
            skipped_tmp.append(rel.as_posix())
            continue
        if not p.is_file():
            continue
        if _excluded(rel):
            skipped_hits.append(rel.as_posix())
            continue
        dest = RUN_DIR / rel
        if dest.exists():
            if sha256_file(dest) != sha256_file(p):
                raise SurveyIngestError(f"existing {rel} differs from the delivered file")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest)
            if sha256_file(dest) != sha256_file(p):
                raise SurveyIngestError(f"copy of {rel} does not match its source")
        copied.append(rel.as_posix())
    log_src = src / "reports" / "survey_run1.log"
    if LOG_PATH.exists() and sha256_file(LOG_PATH) != sha256_file(log_src):
        raise SurveyIngestError("existing survey_run1.log differs from the delivered file")
    shutil.copyfile(log_src, LOG_PATH)
    return {"copied": copied, "skipped_header_only_hits": skipped_hits, "skipped_duckdb_tmp": skipped_tmp}


def manifest_text(run: Path = RUN_DIR) -> str:
    """`manifest.csv`: every file under the run except itself, code-point order."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["rel_path", "bytes", "sha256"])
    for p in sorted(run.rglob("*"), key=lambda q: q.relative_to(run).as_posix()):
        rel = p.relative_to(run).as_posix()
        if p.is_file() and rel != "manifest.csv":
            w.writerow([rel, p.stat().st_size, sha256_file(p)])
    return buf.getvalue()


def manifest_entry(manifest_sha: str, n_files: int, total_bytes: int, skipped_hits: list[str]) -> dict:
    return {
        "diagnostic_id": DIAGNOSTIC_ID,
        "role": ("Track B Stage 2b/2c dictionary concept coverage survey, run 1 --- a diagnostic, "
                 "not a corpus; counts are diagnostic coverage counts, not prevalence; candidate "
                 "terms are candidate_surface_form, inert"),
        "manifest_path": "artifacts/literature/survey/run1/manifest.csv",
        "manifest_sha256": manifest_sha,
        "n_files": n_files,
        "total_bytes": total_bytes,
        "log_path": "artifacts/literature/survey/survey_run1.log",
        "log_sha256": sha256_file(LOG_PATH),
        "not_copied": {
            "header_only_hits_csv": sorted(skipped_hits),
            "reason": "run_query.py --no-hits writes a header-only hits.csv; the topical copies are omitted",
            "duckdb_tmp_dirs": "none present",
        },
        "run": {
            **RUN_FACTS,
            "tools_sha256": {f"scripts/litcollect/{k}": v for k, v in TOOL_SHA256.items()},
            "inventory_sha256": sha256_file(INVENTORY),
            "context_clause_sha256": sha256_file(CONTEXT),
            "context_clause_documents": len(_ids(RUN_DIR / "_context" / "ids.txt")),
            "index_content_identity_sha256": _index_identity(),
        },
        "decision_ref": "D-025, D-026",
    }


# --- the generated document ---------------------------------------------------

def _fmt(n) -> str:
    return "—" if n is None else f"{n:,}"


def _sorted_rows(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda r: r["row"]["concept_id"])


def facts(rows: list[dict]) -> dict:
    """The computed findings the doc states, from the rows and the LITCORPUS-02 evidence."""
    by = {r["row"]["concept_id"]: r for r in rows}
    dc7 = _ids(RUN_DIR / "DC-007" / "topical" / "ids.txt")
    l2_fire = _ids(L2_RUNS / "fire_weather_diag_topical_only" / "ids_raw.txt")
    heat = _json(L2_RUNS / "extreme_heat_diag_topical_only" / "summary.json")
    bare = {}
    for cid, term in (("DC-001", "temperature"), ("DC-002", "temperature"), ("DC-003", "precipitation")):
        r = by[cid]["row"]
        bare[cid] = {"term": term, "bare": r["per_term_doc_counts"][term], "topical": r["topical_only_count"],
                     "per_term": r["per_term_doc_counts"]}
    heat_rows = {cid: by[cid] for cid in ("DC-009", "DC-010", "DC-011", "DC-012", "DC-013", "DC-014")}
    quotes = []
    for cid in ("DC-011", "DC-012", "DC-013"):
        q = next(d["term"] for d in by[cid]["candidates"]["dropped"]
                 if d["source"] == "model" and ("°" in d["term"] or ">" in d["term"]))
        quotes.append((cid, q))
    measure_max = max(r["row"]["topical_only_count"] or 0 for r in heat_rows.values())
    return {
        "dc7_topical": len(dc7), "l2_fire_topical": len(l2_fire), "dc7_equals_l2": dc7 == l2_fire,
        "bare": bare, "heat_rows": heat_rows, "quotes": quotes,
        "heat_family_group": heat["per_group_doc_counts"][0],
        "heat_index_alone": heat["per_term_doc_counts"]["g0:heat index"],
        "heat_family_terms": [t.split(":", 1)[1] for t in heat["per_term_doc_counts"]],
        "measure_max": measure_max,
        "context_docs": len(_ids(RUN_DIR / "_context" / "ids.txt")),
        "l2_fire_rfwi1": len(_ids(L2_RUNS / "fire_weather_diag_topical_only" / "ids.txt")),
        "cdd": (by["DC-005"]["row"]["per_term_doc_counts"]["cdd"], by["DC-006"]["row"]["per_term_doc_counts"]["cdd"]),
        "mat": by["DC-001"]["row"]["per_term_doc_counts"]["mat"],
    }


def render_doc(rows: list[dict], manifest_sha: str) -> str:
    f = facts(rows)
    table = []
    for r in _sorted_rows(rows):
        row = r["row"]
        terms = " · ".join(f"`{t}`" for t in row["candidate_surface_forms"]) or "— (none searchable)"
        note = row["status"] + (f" — {row['notes']}" if row["notes"] else "")
        table.append(f"| `{row['concept_id']}` | {row['dictionary_name']} | {row['dictionary_page']} | {terms} "
                     f"| {_fmt(row['topical_only_count'])} | {_fmt(row['context_filtered_count'])} | {note} |")
    bare_lines = []
    for cid, b in f["bare"].items():
        share = 100 * b["bare"] / b["topical"]
        others = ", ".join(f"`{t}` {n:,}" for t, n in b["per_term"].items() if t != b["term"])
        bare_lines.append(f"- **{cid}**: `{b['term']}` alone {b['bare']:,} of {b['topical']:,} topical "
                          f"documents ({share:.1f} %); {b['topical'] - b['bare']:,} documents match another "
                          f"term but not `{b['term']}`. Other terms: {others}.")
    heat_lines = []
    for cid, r in f["heat_rows"].items():
        row, cand = r["row"], r["candidates"]
        if row["status"] == "ok":
            heat_lines.append(f"| `{cid}` | ok | {_fmt(row['topical_only_count'])} | "
                              f"{_fmt(row['context_filtered_count'])} | {len(row['candidate_surface_forms'])} kept, "
                              f"{len(cand['dropped'])} dropped |")
        else:
            heat_lines.append(f"| `{cid}` | error | — | — | 0 kept, {len(cand['dropped'])} dropped; model returned "
                              f"{len(cand['model_raw_terms'])} terms, `model_parse_error` "
                              f"{json.dumps(cand['model_parse_error'])} |")
    quotes = "\n".join(f"- `{cid}`: \"{q}\"" for cid, q in f["quotes"])
    ratio = f["heat_family_group"] / f["measure_max"] if f["measure_max"] else None
    questions = "\n".join(f"- **({qid})** {text}" for qid, text in QUESTIONS)
    return f"""# Concept coverage survey --- run 1 (diagnostic)

**GENERATED by `scripts/ingest_survey_run1.py` from the ingested rows. Do not edit; regenerate.**

**Diagnostic only (D-025, D-026).** Every count below is a **{LABEL}**. Every
model-proposed term is a `candidate_surface_form` --- inert: not approved
vocabulary, not in `concept_map.yaml`, not used by production queries, C-2 or
compatibility (`docs/BRIDGE_ELIGIBILITY.md` §7). No paper was read; no column
status moved; index 117 stays unlabeled; nothing here selects a unit.

## Run

| | |
| --- | --- |
| Ingested run | `artifacts/literature/survey/run1/` (`manifest.csv` SHA-256 `{manifest_sha}`, pinned in `data/manifest.json` under `diagnostics`) |
| Host / environment | {RUN_FACTS['host']}; {RUN_FACTS['environment']}; Python {RUN_FACTS['python']}; DuckDB {RUN_FACTS['duckdb']} |
| Model / endpoint | `{RUN_FACTS['model']}` on Metis, `{RUN_FACTS['endpoint']}` |
| Time (UTC, from `survey.log`) | {RUN_FACTS['start_utc']} → {RUN_FACTS['end_utc']} |
| Index | LITCORPUS-02 source index, identity `{_index_identity()}` |
| Inventory | `data/metadata/dictionary_concepts.yaml`, `{sha256_file(INVENTORY)}` |
| Context clause | `survey_context_clause_v1.txt`, `{sha256_file(CONTEXT)}` --- matches **{f['context_docs']:,}** documents |
| Tools | `run_query.py` `{TOOL_SHA256['run_query.py']}`, `survey_driver.py` `{TOOL_SHA256['survey_driver.py']}` (v3) |
| Execution | {RUN_FACTS['execution']}, after {RUN_FACTS['prior_attempt']} |

## Table

Sorted by concept id. *Topical-only* = documents matching any candidate term;
*context-filtered* = topical ∩ the context clause. "—" = no count (no searchable
term).

| Concept | Dictionary name | Page | Candidate terms (`candidate_surface_form`) | Topical-only ({LABEL}) | Context-filtered ({LABEL}) | Status / notes |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(table)}

## Findings (computed)

**(a) Consistency check --- {'passed' if f['dc7_equals_l2'] else 'FAILED'}.** DC-007 topical = **{f['dc7_topical']:,}**;
the LITCORPUS-02 fire-weather topical-only diagnostic (`fire_weather_diag_topical_only`,
`ids_raw.txt`) = **{f['l2_fire_topical']:,}**. The two id sets are
**{'identical' if f['dc7_equals_l2'] else 'different'}**, although the term lists differ
(DC-007 has no `canadian …` terms and adds `daily` / `seasonal` / `average` /
`mean` / `… value` variants).

**(b) DC-001 / DC-002 / DC-003 are dominated by one bare word.** Per-term counts
from `row.json`:

{chr(10).join(bare_lines)}

**(c) The six heat-index measures (DC-009--014).** Four `ok` rows return
0--{f['measure_max']} documents; two are `error` rows:

| Concept | Status | Topical-only | Context-filtered | Candidates |
| --- | --- | --- | --- | --- |
{chr(10).join(heat_lines)}

The model proposed threshold phrases containing `°` or `>`; three verbatim, from
the `dropped` lists of `candidates.json`:

{quotes}

The sanitizer rejects them ("not a plain lowercase phrase"), because such
characters defeat whole-word (`\\b`) matching; the stored threshold names are
dropped as "more than 6 words". So the DC-011 / DC-013 `error` rows mean **"no
searchable phrase exists"**, not a model failure: the model answered, and its
output parsed.

**(d) Family level vs measure level.** In the LITCORPUS-02 heat-index
topical-only diagnostic (`extreme_heat_diag_topical_only`, same index), the
family topical group ({', '.join(f'`{t}`' for t in f['heat_family_terms'])})
matches **{f['heat_family_group']:,}** documents, and `heat index` alone
**{f['heat_index_alone']:,}**. The measure-level rows above reach at most
**{f['measure_max']}**{f' (ratio {ratio:,.0f})' if ratio else ''}: coverage differs by two to three orders of
magnitude between family level and measure level.

## Caveats

- **R-FWI-1 not applied.** Bare `fwi` is a candidate term in DC-007 and DC-008,
  and the survey runs no disambiguation; on the same documents the LITCORPUS-02
  diagnostic with R-FWI-1 admits {f['l2_fire_rfwi1']:,} of {f['l2_fire_topical']:,}
  (`fire_weather_diag_topical_only`, `ids.txt`).
- **No place filtering.** No geographic term enters any query.
- **Model-proposed terms are `candidate_surface_form`, inert** (see above).
- **`temperature` is not a concept-specific term.** It is the
  parenthetical-stripped dictionary name of DC-001 and DC-002 alike (driver
  behaviour, `TRACKB_STAGE2_REPORT.md` §11), so those two rows count almost the
  same documents.
- Observed in the rows, not interpreted: `cdd` is a candidate in both DC-005 and
  DC-006 ({f['cdd'][0]:,} / {f['cdd'][1]:,} documents); `mat`, a three-letter
  candidate in DC-001, matches {f['mat']:,}.

## Open questions for GUIDANCE

{questions}
"""
