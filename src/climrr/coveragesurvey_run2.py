"""Track B survey run 2 (family level): ingest the Polaris output as a diagnostic; render its doc section.

**Diagnostic only (D-025, D-026, D-027 B2--B4).** Every `candidate_family` is a
model hypothesis with `status: candidate_family`, never an approved family;
every count is a *diagnostic coverage count, not prevalence*; family coverage is
never attributed to a measure. Nothing here touches `concept_map.yaml`, any
column status, index 117 or a production query.

The input is `survey_run2.tar.gz` extracted outside the repository
(`survey/run2/`, `reports/survey_run2.log`). `verify_source` checks the log's
START line and every row against the tracked v4 driver, prompt F, the frozen
normalization table, the pinned inventory, context clause and index identity,
re-derives every count from its id files, and checks each row's run-1 measure
counts against the **ingested** run-1 row (its SHA-256) --- before anything is
copied. `copy_run` copies all of `survey/run2/` except the header-only
`topical/hits.csv` files (as run 1). Run 1 is read, never written.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
from collections import Counter
from pathlib import Path

import yaml

from climrr import coveragesurvey as cs
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

RUN_DIR = cs.SURVEY_DIR / "run2"
RUN_MANIFEST = RUN_DIR / "manifest.csv"
LOG_PATH = cs.SURVEY_DIR / "survey_run2.log"
DRIVER = cs.TOOLS / "survey_driver.py"
NORM_TABLE = REPO_ROOT / "data" / "metadata" / "litcollect" / "normalization_table_v1.yaml"
CONCEPT_MAP = REPO_ROOT / "data" / "metadata" / "concept_map.yaml"

DIAGNOSTIC_ID = "TRACKB-SURVEY-RUN2"
TARBALL_SHA256 = "8f92e3c328e642ef142fc1e77edb7721926518e7d70087bd7503ade7a03bf85a"
DRIVER_SHA256 = "f929ab6a366987d29e5565fe9fa9f80b47cb1c57d19e01ff3af5affdd99baf9f"  # v4
PROMPT_F_SHA256 = "7097c86ccbb694fe34fa5f4dc51ed087594295e3c37ddd97c56ab94702a97931"
NORM_TABLE_SHA256 = "80a5e0e386dfe8a984e1a5ba2ace781d15601f9b0723b75d238b6de5d1226e03"
FAMILY_LABEL = "diagnostic — family coverage is not attributable to the measure"
MAX_KEPT = 10  # the driver's cap on searched forms per concept (`MAX_KEPT` in survey_driver.py v4)

#: From the run's own files (log, summaries, rows); `verify_source` checks them --- except host and
#: environment, which no run-2 output records: they are `owner_confirmed` (Kaiyuan Liao, D-028 action 13).
#: The Python patch version is in no run-2 output and was not supplied: `unknown`, never run 1's (action 14).
RUN_FACTS = {
    "host": "polaris-login-01 (Polaris login node) --- `owner_confirmed`, not run-derived",
    "environment": "module conda/2026-10-01 + conda env globus_env --- `owner_confirmed`, not run-derived",
    "python": "patch version `unknown` (not recorded in any run-2 output and not supplied; run 1's is not copied)",
    "duckdb": "1.5.4",
    "model": "gpt-oss-120b",
    "endpoint": "https://inference-api.alcf.anl.gov/resource_server/metis/api/v1",
    "start_utc": "2026-10-21T20:02:05Z",
    "end_utc": "2026-10-21T20:18:28Z",
    "mode": "family",
}

#: The START line's short hashes, as the work package lists them for verification.
LOG_PINS = {"driver_sha": DRIVER_SHA256, "prompt_f_sha": PROMPT_F_SHA256, "norm_table_sha": NORM_TABLE_SHA256,
            "inventory_sha": None, "context_sha": None, "index_identity": None}


class SurveyRun2Error(RuntimeError):
    """The delivered run 2 does not match its pins, or a copy differs from its source."""


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_log(text: str) -> dict:
    """The START line's fields and the context-clause document count."""
    start = next(ln for ln in text.splitlines() if " START " in ln)
    fields = dict(re.findall(r"(\w+)=(\S+)", start))
    m = re.search(r"context clause matches (\d+) documents", text)
    stamps = re.findall(r"^(\S+Z) ", text, flags=re.M)
    return {"fields": fields, "context_documents": int(m.group(1)) if m else None,
            "start_utc": stamps[0], "end_utc": stamps[-1], "done": " DONE rows=14 " in text}


def verify_log(text: str) -> dict:
    log = parse_log(text)
    f = log["fields"]
    want = {**LOG_PINS, "inventory_sha": sha256_file(cs.INVENTORY), "context_sha": sha256_file(cs.CONTEXT),
            "index_identity": cs._index_identity()}
    problems = [f"log {k}={f.get(k)} is not a prefix of {v}" for k, v in want.items()
                if not f.get(k) or not v.startswith(f[k])]
    if (f.get("mode"), f.get("model"), f.get("base_url")) != ("family", RUN_FACTS["model"], RUN_FACTS["endpoint"]):
        problems.append("log mode / model / endpoint differ")
    if (log["start_utc"], log["end_utc"]) != (RUN_FACTS["start_utc"], RUN_FACTS["end_utc"]):
        problems.append("log start/end differ from RUN_FACTS")
    if log["context_documents"] != 120050 or not log["done"]:
        problems.append("log context count is not 120,050 or the run did not finish 14 rows")
    if problems:
        raise SurveyRun2Error("; ".join(problems))
    return log


def verify_run(run: Path) -> list[dict]:
    """Check a run-2 directory (delivered or ingested); return rows sorted by concept id."""
    problems: list[str] = []
    if sha256_file(DRIVER) != DRIVER_SHA256:
        problems.append("tracked survey_driver.py is not v4")
    if sha256_file(NORM_TABLE) != NORM_TABLE_SHA256:
        problems.append("tracked normalization table differs from its pin")
    inv_sha, ctx_sha, idx_id = sha256_file(cs.INVENTORY), sha256_file(cs.CONTEXT), cs._index_identity()
    ctx_summary = _json(run / "_context" / "summary.json")
    ctx = cs._ids(run / "_context" / "ids.txt")
    if (ctx_summary["query_sha256"], ctx_summary["index"]["content_identity_sha256"]) != (ctx_sha, idx_id):
        problems.append("_context: clause or index identity differs")
    if not (ctx_summary["admitted_count"] == len(ctx) == 120050) or ctx_summary["hits_recorded"] is not False:
        problems.append("_context: count/ids mismatch or hits recorded")
    if ctx != cs._ids(cs.RUN_DIR / "_context" / "ids.txt"):
        problems.append("_context: id set differs from run 1's")
    if ctx_summary["duckdb_version"] != RUN_FACTS["duckdb"]:
        problems.append("_context: DuckDB version differs")
    rows = []
    for d in cs._concept_dirs(run):
        cid = d.name
        row, fam = _json(d / "row.json"), _json(d / "family.json")
        r1_path = cs.RUN_DIR / cid / "row.json"
        r1 = _json(r1_path)
        if (row["concept_id"], fam["dictionary_concept_id"], row["mode"]) != (cid, cid, "family"):
            problems.append(f"{cid}: concept id / mode mismatch")
        pins = (row["inventory_sha256"], row["context_clause_sha256"], row["index_content_identity_sha256"],
                row["driver_sha256"], row["prompt_template_sha256"], row["normalization_table_sha256"])
        if pins != (inv_sha, ctx_sha, idx_id, DRIVER_SHA256, PROMPT_F_SHA256, NORM_TABLE_SHA256):
            problems.append(f"{cid}: a pin differs")
        if fam["status"] != "candidate_family" or row["candidate_family_status"] != "candidate_family":
            problems.append(f"{cid}: candidate family not labelled candidate_family")
        if fam["candidate_family"] != row["candidate_family"] or fam["parse_error"] is not None:
            problems.append(f"{cid}: family differs between family.json and row.json, or a parse error")
        if (fam["model_id"], fam["endpoint"]) != (RUN_FACTS["model"], RUN_FACTS["endpoint"]):
            problems.append(f"{cid}: model / endpoint differ")
        if not (fam["prompt_sha256"] == row["prompt_sha256"] == sha256_file(d / "prompt.txt")):
            problems.append(f"{cid}: prompt SHA-256 mismatch")
        if row["label"] != FAMILY_LABEL or row["status"] != "ok":
            problems.append(f"{cid}: label or status")
        # the run-1 measure counts are copied unchanged from the ingested run-1 row
        if row["run1_row_sha256"] != sha256_file(r1_path) or (
                row["measure_topical_only_count"], row["measure_context_filtered_count"], row["measure_status"]) != (
                r1["topical_only_count"], r1["context_filtered_count"], r1["status"]):
            problems.append(f"{cid}: measure counts / run-1 row SHA-256 differ from the ingested run 1")
        searched = [s["search_term"] for s in fam["candidate_family_surface_forms"] if s["searched"]]
        topical = cs._ids(d / "topical" / "ids.txt")
        summ = _json(d / "topical" / "summary.json")
        both = cs._ids(d / "topical_and_context_ids.txt")
        if row["family_surface_forms_searched"] != searched or summ["parsed_groups"] != [searched]:
            problems.append(f"{cid}: searched forms differ between family.json, row.json and the query")
        if not (row["topical_query_sha256"] == sha256_file(d / "query_topical.txt") == summ["query_sha256"]):
            problems.append(f"{cid}: topical query SHA-256 mismatch")
        if not (row["family_topical_only_count"] == len(topical) == summ["admitted_count"]):
            problems.append(f"{cid}: topical count != ids")
        if not (row["family_context_filtered_count"] == len(both)) or both != topical & ctx:
            problems.append(f"{cid}: context-filtered count != |topical ∩ context|")
        if summ["hits_recorded"] is not False:
            problems.append(f"{cid}: hits recorded")
        if {k.split(":", 1)[1]: v for k, v in summ["per_term_doc_counts"].items()} != row["per_term_doc_counts"]:
            problems.append(f"{cid}: per-term counts differ between row and summary")
        rows.append({"row": row, "family": fam})
    if len(rows) != 14:
        problems.append(f"expected 14 concept rows, found {len(rows)}")
    with (run / "survey_table.csv").open(encoding="utf-8", newline="") as fh:
        table = list(csv.DictReader(fh))
    cols = ("concept_id", "dictionary_name", "measure_topical_only_count", "measure_context_filtered_count",
            "candidate_family", "family_topical_only_count", "family_context_filtered_count", "notes")
    want = [{k: "" if r["row"][k] is None else str(r["row"][k]) for k in cols} for r in rows]
    if table != want:
        problems.append("survey_table.csv differs from the rows")
    if problems:
        raise SurveyRun2Error("; ".join(problems))
    return rows


def verify_source(src: Path) -> list[dict]:
    run = src / "survey" / "run2"
    for h in [*run.glob("DC-*/topical/hits.csv"), run / "_context" / "hits.csv"]:
        if h.read_text(encoding="utf-8").splitlines() != [cs.HITS_HEADER]:
            raise SurveyRun2Error(f"{h.relative_to(src)} is not header-only")
    if sha256_file(src / "reports" / "survey_run2.log") != sha256_file(run / "survey.log"):
        raise SurveyRun2Error("reports/survey_run2.log differs from survey/run2/survey.log")
    verify_log((run / "survey.log").read_text(encoding="utf-8"))
    return verify_run(run)


def copy_run(src: Path) -> dict:
    """Copy run 2 into `RUN_DIR` (or confirm an existing copy is byte-identical). Run 1 is never written."""
    run = src / "survey" / "run2"
    copied, skipped_hits = [], []
    for p in sorted(run.rglob("*")):
        rel = p.relative_to(run)
        if not p.is_file():
            continue
        if cs._excluded(rel):
            skipped_hits.append(rel.as_posix())
            continue
        dest = RUN_DIR / rel
        if dest.exists():
            if sha256_file(dest) != sha256_file(p):
                raise SurveyRun2Error(f"existing {rel} differs from the delivered file")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest)
            if sha256_file(dest) != sha256_file(p):
                raise SurveyRun2Error(f"copy of {rel} does not match its source")
        copied.append(rel.as_posix())
    log_src = src / "reports" / "survey_run2.log"
    if LOG_PATH.exists() and sha256_file(LOG_PATH) != sha256_file(log_src):
        raise SurveyRun2Error("existing survey_run2.log differs from the delivered file")
    shutil.copyfile(log_src, LOG_PATH)
    return {"copied": copied, "skipped_header_only_hits": skipped_hits}


def form_stats(rows: list[dict], run: Path = RUN_DIR) -> dict:
    """Which normalization rules fired, and how many forms were searched vs recorded and not searched."""
    forms = [s for r in rows for s in r["family"]["candidate_family_surface_forms"]]
    reasons = Counter(s["reason"] for s in forms if not s["searched"])
    return {
        "forms_total": len(forms),
        "forms_searched": sum(s["searched"] for s in forms),
        "forms_over_cap": sum(n for k, n in reasons.items() if k.startswith("over the")),
        "forms_dropped_other": sum(n for k, n in reasons.items() if not k.startswith("over the")),
        "rules_fired": dict(sorted(Counter(i for s in forms for i in s["rules_applied"]).items())),
        "forms_changed_by_normalization": sum(s["normalized"] != s["original"] for s in forms),
        "forms_per_concept": sorted({len(r["family"]["candidate_family_surface_forms"]) for r in rows}),
        "prompt_k": sorted({int(re.search(r"\[up to (\d+) ", (run / r["row"]["concept_id"] / "prompt.txt")
                                          .read_text(encoding="utf-8")).group(1)) for r in rows}),
    }


def manifest_entry(manifest_sha: str, n_files: int, total_bytes: int, skipped_hits: list[str]) -> dict:
    return {
        "diagnostic_id": DIAGNOSTIC_ID,
        "role": ("Track B Stage 2 dictionary concept coverage survey, run 2 (family level, D-027 B2) --- a "
                 "diagnostic, not a corpus; counts are diagnostic coverage counts, not prevalence; every "
                 "candidate_family is a model hypothesis (status candidate_family), inert; family coverage is "
                 "not attributable to the measure"),
        "manifest_path": "artifacts/literature/survey/run2/manifest.csv",
        "manifest_sha256": manifest_sha,
        "n_files": n_files,
        "total_bytes": total_bytes,
        "log_path": "artifacts/literature/survey/survey_run2.log",
        "log_sha256": sha256_file(LOG_PATH),
        "source_tarball_sha256": TARBALL_SHA256,
        "not_copied": {
            "header_only_hits_csv": sorted(skipped_hits),
            "reason": "run_query.py --no-hits writes a header-only hits.csv; the topical copies are omitted (as run 1)",
            "duckdb_tmp_dirs": "none present",
        },
        "run": {
            **RUN_FACTS,
            "tools_sha256": {"scripts/litcollect/survey_driver.py": DRIVER_SHA256,
                             "scripts/litcollect/run_query.py": cs.TOOL_SHA256["run_query.py"]},
            "prompt_f_template_sha256": PROMPT_F_SHA256,
            "normalization_table_sha256": NORM_TABLE_SHA256,
            "inventory_sha256": sha256_file(cs.INVENTORY),
            "context_clause_sha256": sha256_file(cs.CONTEXT),
            "context_clause_documents": len(cs._ids(RUN_DIR / "_context" / "ids.txt")),
            "index_content_identity_sha256": cs._index_identity(),
            "run1_manifest_sha256": sha256_file(cs.RUN_MANIFEST),
        },
        "decision_ref": "D-025, D-026, D-027",
    }


# --- computed facts and the doc section ---------------------------------------------

def _concept_map_terms() -> set[str]:
    """Every surface term in `concept_map.yaml` (accepted and additional), lowercased."""
    out = set()
    for e in yaml.safe_load(CONCEPT_MAP.read_text(encoding="utf-8"))["entries"]:
        out |= {t.lower() for t in e.get("accepted_surface_terms") or []}
        out |= {a["term"].lower() for a in e.get("additional_surface_terms") or []}
    return out


def _l2(name: str) -> dict:
    s = _json(cs.L2_RUNS / name / "summary.json")
    return {"group": s["per_group_doc_counts"][0],
            "terms": {k.split(":", 1)[1]: v for k, v in s["per_term_doc_counts"].items()}}


def facts(rows2: list[dict]) -> dict:
    by = {r["row"]["concept_id"]: r["row"] for r in rows2}
    forms = {cid: r["family_surface_forms_searched"] for cid, r in by.items()}
    fire, heat = _l2("fire_weather_diag_topical_only"), _l2("extreme_heat_diag_topical_only")
    cmap = _concept_map_terms()
    broad = {cid: forms[cid] for cid in by}

    def has(cid, *terms):
        return all(t in broad[cid] for t in terms)

    thresholds = ("DC-011", "DC-012", "DC-013", "DC-014")
    heat_measure = [by[c]["measure_topical_only_count"] for c in ("DC-009", "DC-010", *thresholds)]
    family_counts = [r["family_topical_only_count"] for r in by.values()]
    fire_terms = ("wildfire risk", "fire hazard", "fire danger")
    return {
        "all_candidate_family": all(r["family"]["status"] == "candidate_family"
                                    and r["row"]["candidate_family_status"] == "candidate_family" for r in rows2),
        "families": {cid: r["candidate_family"] for cid, r in by.items()},
        "n_distinct_families": len({r["candidate_family"] for r in by.values()}),
        "dc3": (by["DC-003"]["family_topical_only_count"], has("DC-003", "moisture", "water cycle")),
        "dc6": (by["DC-006"]["family_topical_only_count"], has("DC-006", "heat", "cold", "warming")),
        "dc9": (by["DC-009"]["family_topical_only_count"],
                has("DC-009", "apparent temperature", "heat stress", "humid heat")),
        "dc10": (by["DC-010"]["family_topical_only_count"], has("DC-010", "apparent temperature", "heat stress"),
                 "humid heat" in broad["DC-010"]),
        "heat_index_run2": {c: by[c]["per_term_doc_counts"]["heat index"] for c in ("DC-009", "DC-010")},
        "heat_index_l2": heat["terms"]["heat index"], "heat_group_l2": heat["group"],
        "fire": {c: (by[c]["candidate_family"], by[c]["family_topical_only_count"], has(c, *fire_terms))
                 for c in ("DC-007", "DC-008")},
        "fire_terms_in_concept_map": sorted(t for t in fire_terms + ("fire risk",) if t in cmap),
        "fire_weather_run2": by["DC-007"]["per_term_doc_counts"]["fire weather"],
        "fire_danger_run2": by["DC-007"]["per_term_doc_counts"]["fire danger"],
        "fire_weather_l2": fire["terms"]["fire weather"],
        "fwi_group_l2": fire["group"],
        "fwi_rfwi1": len(cs._ids(cs.L2_RUNS / "fire_weather_diag_topical_only" / "ids.txt")), "fwi_term_l2": fire["terms"]["fire weather index"],
        "thresholds": {c: (by[c]["candidate_family"], by[c]["family_topical_only_count"],
                           "hot days" in broad[c], "warm days" in broad[c]) for c in thresholds},
        "threshold_range": (min(by[c]["family_topical_only_count"] for c in thresholds),
                            max(by[c]["family_topical_only_count"] for c in thresholds)),
        "hot_days": by["DC-011"]["per_term_doc_counts"]["hot days"],
        "warm_days": by["DC-011"]["per_term_doc_counts"]["warm days"],
        "heat_measure_range": (min(x for x in heat_measure if x is not None),
                               max(x for x in heat_measure if x is not None)),
        "family_range": (min(family_counts), max(family_counts)),
    }


def _n(x) -> str:
    return cs._fmt(x)


def render_section(rows2: list[dict], manifest_sha: str) -> str:
    f, st = facts(rows2), form_stats(rows2)
    side = []
    for r in sorted(rows2, key=lambda r: r["row"]["concept_id"]):
        row = r["row"]
        side.append(f"| `{row['concept_id']}` | {row['dictionary_name']} | {_n(row['measure_topical_only_count'])} / "
                    f"{_n(row['measure_context_filtered_count'])} | `{row['candidate_family']}` | "
                    f"{_n(row['family_topical_only_count'])} / {_n(row['family_context_filtered_count'])} |")
    per_term = []
    for r in sorted(rows2, key=lambda r: r["row"]["concept_id"]):
        row = r["row"]
        terms = " · ".join(f"`{t}` {row['per_term_doc_counts'][t]:,}" for t in row["family_surface_forms_searched"])
        per_term.append(f"- **{row['concept_id']}** (`{row['candidate_family']}`): {terms}")
    rules = (", ".join(f"{k} ×{v}" for k, v in st["rules_fired"].items()) if st["rules_fired"]
             else "**none** --- no rule of N-1 … N-7 fired on any form (every `rules_applied` is empty)")
    th = f["thresholds"]
    th_lines = "; ".join(f"{c} `{fam}` {n:,}" for c, (fam, n, _, _) in th.items())
    hot = [c for c, v in th.items() if v[2]]
    warm = [c for c, v in th.items() if v[3]]
    fire_ok = all(v[2] for v in f["fire"].values())
    lo, hi = f["family_range"]
    hlo, hhi = f["heat_measure_range"]
    return f"""## Run 2 (family level) --- executed (diagnostic)

Accepted by GUIDANCE (D-028) as **{DIAGNOSTIC_ID} --- family-level diagnostic
coverage survey**; never ontology generation.

**Every `candidate_family` below is a model hypothesis with `status:
candidate_family`, not an approved family** (D-027 B2). Each family count is a
**{cs.LABEL}**, labelled *"{FAMILY_LABEL}"*; measure counts are copied unchanged from
the run-1 rows (each row's SHA-256 checked against the ingested run 1). The two
are never added, merged or substituted. Method: prompt F, `family.json`,
normalization before the sanitizer, counts over the family forms only, as fixed
before execution (`reports/milestones/TRACKB_STAGE2_REPORT.md` §15).

| | |
| --- | --- |
| Ingested run | `artifacts/literature/survey/run2/` (`manifest.csv` SHA-256 `{manifest_sha}`, pinned in `data/manifest.json` under `diagnostics`); source `survey_run2.tar.gz` `{TARBALL_SHA256}` |
| Host / environment | {RUN_FACTS['host']}; environment {RUN_FACTS['environment']}; Python {RUN_FACTS['python']}; DuckDB {RUN_FACTS['duckdb']} |
| Model / endpoint | `{RUN_FACTS['model']}`, `{RUN_FACTS['endpoint']}` |
| Time (UTC, from `survey.log`) | {RUN_FACTS['start_utc']} → {RUN_FACTS['end_utc']} |
| Driver / prompt F / table | `survey_driver.py` v4 `{DRIVER_SHA256}`, `--mode family`; prompt F `{PROMPT_F_SHA256}`; `normalization_table_v1.yaml` `{NORM_TABLE_SHA256}` |
| Index, inventory, clause | as run 1; the `_context` id set equals run 1's (**{120050:,}** documents) |

### Side by side

*Topical-only / context-filtered.* "—" = no measure count (run-1 `error` row).

| Concept | Dictionary name | Measure (run 1) topical / context | `candidate_family` (hypothesis) | Family topical / context ({FAMILY_LABEL}) |
| --- | --- | --- | --- | --- |
{chr(10).join(side)}

### Searched family forms and per-term document counts (topical-only)

{chr(10).join(per_term)}

**Forms and normalization.** The prompt asked for up to {', '.join(map(str, st['prompt_k']))} forms; the model
returned {', '.join(map(str, st['forms_per_concept']))} per concept --- **{st['forms_total']}** forms in all,
**{st['forms_searched']} searched**, **{st['forms_over_cap']} recorded over the {MAX_KEPT}-term cap**,
{st['forms_dropped_other']} dropped for another reason. Normalization rules fired: {rules}; forms
changed by normalization: {st['forms_changed_by_normalization']}.

### Findings (computed)

**(1) Hypotheses, not families.** All 14 `family.json` carry `status:
candidate_family` and all 14 rows `candidate_family_status: candidate_family`
({'checked' if f['all_candidate_family'] else 'FAILED'}). {f['n_distinct_families']} distinct names were
proposed. None is approved, none enters `concept_map.yaml`, C-2, compatibility
or unit design.

**(2) Several families are broader than the dictionary concept.**
DC-003 Precipitation → `{f['families']['DC-003']}` **{f['dc3'][0]:,}** (forms include `moisture`,
`water cycle`: {'yes' if f['dc3'][1] else 'NO'}). DC-006 Degree Days → `{f['families']['DC-006']}`
**{f['dc6'][0]:,}** (forms include `heat`, `cold`, `warming`: {'yes' if f['dc6'][1] else 'NO'}).
DC-009 → `{f['families']['DC-009']}` **{f['dc9'][0]:,}** (forms include `apparent temperature`,
`heat stress`, `humid heat`: {'yes' if f['dc9'][1] else 'NO'}); DC-010 → `{f['families']['DC-010']}`
**{f['dc10'][0]:,}** (`apparent temperature`, `heat stress`: {'yes' if f['dc10'][1] else 'NO'};
`humid heat`: {'yes' if f['dc10'][2] else 'no'}). The approved term `heat index` alone is
**{f['heat_index_l2']:,}** (run-1 diagnostic, LITCORPUS-02 `extreme_heat_diag_topical_only`; run 2
per-term: {', '.join(f'{c} {n:,}' for c, n in f['heat_index_run2'].items())}).

**(3) The FWI families are built from non-concept-map terms; inert here.**
DC-007 → `{f['fire']['DC-007'][0]}` **{f['fire']['DC-007'][1]:,}**; DC-008 →
`{f['fire']['DC-008'][0]}` **{f['fire']['DC-008'][1]:,}**; both form lists include
`wildfire risk`, `fire hazard`, `fire danger` ({'yes' if fire_ok else 'NO'}). None of these
(nor `fire risk`) is a `concept_map.yaml` term (found: {f['fire_terms_in_concept_map'] or 'none'}); the
concept-first ruling of 2026-10-12 (D-021) restricts collection to approved
family-level concept-map vocabulary, so they are outside production vocabulary.
(`fire danger` does occur in the frozen v1 fire query, but only in its
*context* group, never as a topical term, and it is not in the survey context
clause.) Here they are **inert**: diagnostic counts only. Per-term: `fire
weather` **{f['fire_weather_run2']:,}** (equal to the LITCORPUS-02 diagnostic's
disambiguator count, {f['fire_weather_l2']:,}), `fire danger` **{f['fire_danger_run2']:,}**.

**(4) Threshold measures.** {th_lines} --- range {f['threshold_range'][0]:,}--{f['threshold_range'][1]:,}.
`hot days` ({f['hot_days']:,}) is a searched form in {', '.join(hot)}; `warm days` ({f['warm_days']:,})
in {', '.join(warm)}. **Family coverage is not attributed to any threshold
measure** (D-027 B3); the run-1 measure counts stand as they were.

**(5) Three coverage levels --- the standing presentation (D-028).**

| Level | What is searched | Documents (topical-only) |
| --- | --- | --- |
| **Level 1 --- Dictionary-measure diagnostic coverage** (run 1) | the dictionary measure's own wording, heat-index measures DC-009--014 | {hlo}--{hhi} |
| **Level 2 --- Governed concept-map family coverage** (LITCORPUS-02 diagnostics) | approved terms of the two concept-map families | fire weather index group **{f['fwi_group_l2']:,}** before R-FWI-1, {f['fwi_rfwi1']:,} after (`fire weather index` alone {f['fwi_term_l2']:,}); `heat index` **{f['heat_index_l2']:,}** (group {f['heat_group_l2']:,}) |
| **Level 3 --- Model-proposed candidate-family diagnostic coverage** (run 2) | `candidate_family` surface forms | {lo:,} -- {hi:,} |

Only Level 2 rests on governed (concept-map) vocabulary; the run-1
measure phrases and the run-2 family forms are model proposals
(`candidate_surface_form`, `candidate_family`). **Standing rule (D-028):** the
three levels are never ranked or combined, concepts are not ranked across levels
as though the counts were semantically comparable, and Level-2 or Level-3
coverage is never attributed to a Level-1 threshold measure. A Level-1 zero
means no direct lexical match under the current measure representation and
search rules, not that no relevant literature exists. Level-3 counts are never
family prevalence, approved family coverage, benchmark relevance, or evidence
for unit selection.

"""


def _entry(diagnostic_id: str) -> dict:
    return next(d for d in _json(cs.MANIFEST)["diagnostics"] if d["diagnostic_id"] == diagnostic_id)


def render_full_doc() -> str:
    """`docs/CONCEPT_COVERAGE_SURVEY.md` from the ingested run 1 and run 2 (both re-verified)."""
    rows1, rows2 = cs.verify_run(cs.RUN_DIR), verify_run(RUN_DIR)
    return cs.render_doc(rows1, _entry(cs.DIAGNOSTIC_ID)["manifest_sha256"],
                         render_section(rows2, _entry(DIAGNOSTIC_ID)["manifest_sha256"]))
