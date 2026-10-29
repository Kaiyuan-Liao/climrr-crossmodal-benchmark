"""Closed-book benchmark items v2 (D-041; GUIDANCE re-anchor ruling 2026-10-29; D-035..D-040).

`data/metadata/benchmark/item_schema_v2.json` is the item record. `schema_errors`
checks a record against it with the soft-QA validator (`climrr.softqa`: the JSON
Schema subset the schemas use, no new dependency) after resolving the schema's
local `$ref`s. `consistency_errors` checks what a schema cannot: the leakage
check recomputes to what is stored; evidence strength agrees with the supports;
a single-source statement is not framed as consensus; a relative magnitude says
it is relative; the review status agrees with the two human dispositions.
`validity` returns the ruling's six conditions A--F, each met or not with the
reasons --- only an item meeting all six is benchmark-valid.

**Leakage check** (`leakage_check`, ruling 4 "Source leakage check"). Deterministic
and conservative: a hit fails the prompt and goes to review, it never edits it.

- `clmrr_named`: "ClimRR" (any spacing / hyphen / case) or "Climate Risk and
  Resilience Portal".
- `row_or_column_named`: a table column name as a whole word, case-insensitive
  (names from the coverage report, whose data hash is the manifest's; the
  manifest itself records counts, not names); a grid-cell id `R<row>C<col>`. Four
  generic names (`NAME`, `State`, `X`, `Y`) cannot be told from ordinary words and
  are not checked --- listed in `GENERIC_COLUMN_NAMES`.
- `paper_named`: a corpus id (`LIT-…`, `LIT2-…`). Paper titles and authors are
  not available here (no corpus index on this machine), so two proxies also set
  it and add a `review:` flag: "et al." and a year in parentheses ("(2019)",
  "(Smith, 2019)").
- `hidden_exact_value_required`: a decimal number or a percentage in the prompt.
  A heat-index threshold such as "105 °F" is not flagged (it names a metric).
- `according_to_phrase`: "according to", "this/the table", "this/the dataset",
  "this/the paper", "this/the study", "in the table".

Nothing here calls a model, reads table values, or touches the concept map,
column statuses or compatibility rules.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

from climrr import softqa
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

SCHEMA_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "item_schema_v2.json"
SCHEMA_VERSION = "benchmark_item_v2"
COVERAGE_PATH = REPO_ROOT / "artifacts" / "profiles" / "dictionary_coverage.json"
LEAKAGE_CHECK_VERSION = "leakage_check v1"
USE_CASE_LEVELS = range(1, 9)  # ladder v1, D-038 (proposed)

GENERIC_COLUMN_NAMES = frozenset({"NAME", "State", "X", "Y"})
ACCEPTING = ("accept", "accept_after_edit")
VALID_FINAL = softqa.VALID_FINAL

CLIMRR_RE = re.compile(r"\bclim\s*-?\s*rr\b|\bclimate\s+risk\s+(?:and|&)\s+resilience\s+portal\b", re.I)
ACCORDING_RE = re.compile(r"\baccording\s+to\b|\b(?:this|the)\s+(?:table|dataset|data\s+set|paper|study)\b"
                          r"|\bin\s+the\s+table\b", re.I)
CELL_ID_RE = re.compile(r"\bR\d+C\d+\b")
CORPUS_ID_RE = re.compile(r"\bLIT2?-\d+\b")
ET_AL_RE = re.compile(r"\bet\s+al\b\.?", re.I)
YEAR_PAREN_RE = re.compile(r"\((?:[A-Z][^()]*?,\s*)?(?:1[89]\d\d|20\d\d)[a-z]?\)")
DECIMAL_RE = re.compile(r"\b\d+\.\d+\b")
PERCENT_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:%|percent\b|per\s+cent\b)", re.I)
TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


class ItemError(ValueError):
    """An item does not satisfy schema v2 or its rules."""


# --- schema ------------------------------------------------------------------------


def load_schema(path: Path | str = SCHEMA_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def schema_sha256(path: Path | str = SCHEMA_PATH) -> str:
    return sha256_file(path)


def resolve_refs(schema: dict) -> dict:
    """The schema with every local `{"$ref": "#/$defs/x"}` replaced by its target."""
    defs = schema.get("$defs", {})

    def walk(node):
        if isinstance(node, dict):
            if "$ref" in node:
                name = node["$ref"].removeprefix("#/$defs/")
                if name not in defs:
                    raise ItemError(f"unresolved $ref {node['$ref']!r}")
                return walk(copy.deepcopy(defs[name]))
            return {k: walk(v) for k, v in node.items() if k != "$defs"}
        if isinstance(node, list):
            return [walk(v) for v in node]
        return node

    return walk(schema)


def schema_errors(item: dict, schema: dict | None = None) -> list[str]:
    errors: list[str] = []
    softqa._check(item, resolve_refs(schema or load_schema()), "$", errors)
    return errors


def table_pattern_errors(pattern: dict, schema: dict | None = None) -> list[str]:
    """A table-pattern record (e.g. a line of table_patterns_v1.jsonl) against `$defs/table_pattern`."""
    errors: list[str] = []
    softqa._check(pattern, resolve_refs(schema or load_schema())["properties"]["reference_components"]
                  ["properties"]["table_patterns"]["items"], "$", errors)
    return errors


# --- leakage -----------------------------------------------------------------------


def column_names(path: Path | str = COVERAGE_PATH) -> list[str]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [c["column"] for c in data["columns"]]


def leakage_check(prompt: str, columns: list[str] | None = None) -> dict:
    cols = columns if columns is not None else column_names()
    checked = {c.lower() for c in cols if c not in GENERIC_COLUMN_NAMES}
    flags: list[str] = []
    climrr = bool(CLIMRR_RE.search(prompt))
    if climrr:
        flags.append("ClimRR named")
    col_hits = sorted({t for t in TOKEN_RE.findall(prompt) if t.lower() in checked})
    cell_hits = CELL_ID_RE.findall(prompt)
    flags += [f"column name: {t}" for t in col_hits] + [f"cell id: {t}" for t in cell_hits]
    ids = CORPUS_ID_RE.findall(prompt)
    flags += [f"corpus id: {t}" for t in ids]
    et_al = bool(ET_AL_RE.search(prompt))
    years = YEAR_PAREN_RE.findall(prompt)
    if et_al:
        flags.append("review: 'et al.' (paper-author proxy)")
    flags += [f"review: year in parentheses {y!r} (citation proxy)" for y in years]
    values = DECIMAL_RE.findall(prompt) + PERCENT_RE.findall(prompt)
    flags += [f"exact value: {v.strip()}" for v in values]
    according = ACCORDING_RE.findall(prompt)
    flags += [f"source phrase: {a}" for a in according]
    out = {"clmrr_named": climrr, "row_or_column_named": bool(col_hits or cell_hits),
           "paper_named": bool(ids or et_al or years), "hidden_exact_value_required": bool(values),
           "according_to_phrase": bool(according)}
    out["pass"] = not any(out.values())
    out["flags"] = flags
    out["check_version"] = LEAKAGE_CHECK_VERSION
    return out


# --- rules beyond the schema ---------------------------------------------------------


def _statements(item: dict) -> list[tuple[str, dict]]:
    rc = item["reference_components"]
    return [(f"literature_mechanisms[{i}]", s) for i, s in enumerate(rc["literature_mechanisms"])] + \
           [(f"literature_caveats[{i}]", s) for i, s in enumerate(rc["literature_caveats"])]


def statement_errors(where: str, s: dict) -> list[str]:
    """Evidence strength against the supports (ruling 2; acceptance criteria 8-11)."""
    errs = []
    papers = {sup["paper_sha256"] for sup in s["supports"]}
    if not s["supports"]:
        errs.append(f"{where}: no supporting passage (every literature sentence needs exact provenance)")
    for j, sup in enumerate(s["supports"]):
        if sup["span_end"] <= sup["span_start"]:
            errs.append(f"{where}.supports[{j}]: empty span")
        elif sup["span_end"] - sup["span_start"] != len(sup["verbatim_passage"]):
            errs.append(f"{where}.supports[{j}]: span length != passage length")
    strength = s["evidence_strength"]
    if strength == "multi_source_supported" and len(papers) < 2:
        errs.append(f"{where}: multi_source_supported needs >= 2 independent papers, has {len(papers)}")
    if strength == "review_supported" and not any(sup.get("is_review_or_synthesis") for sup in s["supports"]):
        errs.append(f"{where}: review_supported needs a support marked is_review_or_synthesis")
    if strength == "single_source_supported":
        if len(papers) != 1:
            errs.append(f"{where}: single_source_supported must cite exactly one paper, has {len(papers)}")
        if s["statement_type"] == "consensus" or s["reference_scope"] == "broad_consensus":
            errs.append(f"{where}: a single-source statement is not framed as consensus")
    return errs


def consistency_errors(item: dict, columns: list[str] | None = None) -> list[str]:
    errs = []
    if item["use_case_level"] not in USE_CASE_LEVELS:
        errs.append(f"use_case_level {item['use_case_level']} not in ladder v1 (1-8)")
    recomputed = leakage_check(item["prompt"], columns)
    stored = item["source_leakage_check"]
    for k in ("clmrr_named", "row_or_column_named", "paper_named", "hidden_exact_value_required",
              "according_to_phrase", "pass"):
        if stored.get(k) != recomputed[k]:
            errs.append(f"source_leakage_check.{k} = {stored.get(k)!r}, recomputed {recomputed[k]!r}")
    for i, p in enumerate(item["reference_components"]["table_patterns"]):
        rm = p.get("relative_magnitude")
        if rm and ("relative" not in rm["definition"] or "tercile" not in rm["definition"]):
            errs.append(f"table_patterns[{i}]: relative_magnitude.definition must say it is a relative tercile")
        if rm and p["computed_value_or_range"].get("value") is None and not p["computed_value_or_range"].get("range"):
            errs.append(f"table_patterns[{i}]: a tercile needs the underlying value or range retained")
        if p["geography_type"] == "nca_region" and not (str(p["geography"]).startswith("NCA5-")
                                                    or p["geography"] == "all_covered_nca5_regions"):
            errs.append(f"table_patterns[{i}]: an nca_region geography must be an NCA5 region id")
    for where, s in _statements(item):
        errs += statement_errors(where, s)
    r = item["review"]
    final = r["status"] in VALID_FINAL
    dispositions = [(r.get(k) or {}).get("disposition") for k in ("kaiyuan_disposition", "mentor_disposition")]
    if final:
        if not all(d in ACCEPTING for d in dispositions):
            errs.append(f"review.status {r['status']} needs Kaiyuan and mentor acceptance, got {dispositions}")
        if r["final_frozen"] is None:
            errs.append(f"review.status {r['status']} needs final_frozen prompt / reference_answer / rubric")
    return errs


def validate(item: dict, schema: dict | None = None, columns: list[str] | None = None) -> dict:
    errors = schema_errors(item, schema)
    if not errors:
        errors = consistency_errors(item, columns)
    if errors:
        raise ItemError("item invalid:\n  " + "\n  ".join(errors))
    return item


# --- the six validity conditions ---------------------------------------------------------


def validity(item: dict, columns: list[str] | None = None) -> dict:
    """Ruling conditions A-F: {condition: {"met": bool, "reasons": [...]}}, plus `benchmark_valid`."""
    rc = item["reference_components"]
    out: dict = {}

    a = []
    if item["source_independent_answerability"] != "yes":
        a.append(f"source_independent_answerability is {item['source_independent_answerability']!r}; only 'yes' is valid")
    leak = leakage_check(item["prompt"], columns)
    if not leak["pass"]:
        a.append("leakage check fails: " + "; ".join(leak["flags"]))
    out["A_source_independent_prompt"] = a

    b = []
    for i, p in enumerate(rc["table_patterns"]):
        if p.get("acceptance_blocked"):
            b.append(f"table_patterns[{i}] acceptance blocked by {p.get('acceptance_blocked_by')}")
        if p.get("status", "computed") != "computed":
            b.append(f"table_patterns[{i}] is {p.get('status')}")
        b += [f"table_patterns[{i}]: {e}" for e in table_pattern_errors(p)]
    if item["reasoning_modalities"] != "Text" and not rc["table_patterns"]:
        b.append("a Hazard item needs at least one table pattern")
    out["B_deterministic_table_facts"] = b

    c = []
    for where, s in _statements(item):
        if not s["supports"]:
            c.append(f"{where}: no provenance")
    if item["reasoning_modalities"] != "Hazard" and not (rc["literature_mechanisms"] or rc["literature_caveats"]):
        c.append("a Text item needs at least one literature statement")
    out["C_provenance_backed_literature"] = c

    d = []
    for where, s in _statements(item):
        d += statement_errors(where, s)
        if s["statement_type"] in ("mechanism", "consensus") and s["evidence_strength"] == "single_source_supported" \
                and s["reference_scope"] != "single_study_observation":
            d.append(f"{where}: a single-source core mechanism must be scoped single_study_observation")
    out["D_explicit_evidence_strength"] = d

    e = []
    ra = item["reference_answer"]
    if rc["table_patterns"] and not ra["table_pattern"]:
        e.append("reference_answer.table_pattern empty while table patterns are used")
    if (rc["literature_mechanisms"] or rc["literature_caveats"]) and not ra["literature_interpretation"]:
        e.append("reference_answer.literature_interpretation empty while literature statements are used")
    rub = item["rubric"]
    for k in ("required_points", "acceptable_variants", "fatal_errors"):
        if not rub[k]:
            e.append(f"rubric.{k} is empty")
    if item["c_g_t_s_d_audit"] is None and rc["table_patterns"] and rc["literature_mechanisms"]:
        e.append("c_g_t_s_d_audit not recorded (audit metadata, criterion 23)")
    out["E_reference_answer_decomposition"] = e

    f = []
    r = item["review"]
    for who in ("kaiyuan_disposition", "mentor_disposition"):
        disp = (r.get(who) or {}).get("disposition")
        if disp not in ACCEPTING:
            f.append(f"{who} is {disp!r}")
    if r["final_frozen"] is None:
        f.append("final prompt / reference / rubric not frozen")
    if r["status"] not in VALID_FINAL:
        f.append(f"review.status is {r['status']!r}")
    out["F_human_acceptance"] = f

    result = {k: {"met": not v, "reasons": v} for k, v in out.items()}
    result["benchmark_valid"] = all(v["met"] for v in result.values())
    return result
