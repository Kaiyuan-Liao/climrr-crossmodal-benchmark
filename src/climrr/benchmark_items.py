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

**Synthesis post-checks** (`synthesis_post_checks`, pilot P2b-prep; run by
`scripts/litcollect/litsynth_agent.py` on every synthesized item). Against the seed
packet (`synthpackets.py`): every number in the reference answer and the rubric traces
to a pattern value the packet gives (exact string or a rounded form it lists; scenario
names and ordinals are not numbers); every table-pattern sentence is tagged with a
packet pattern id; every literature sentence cites >= 1 packet group id, and one resting
only on single-source groups is marked hedged and carries a hedge word; the prompt
passes `leakage_check` and names no internal id, identifier-like name or packet source
string (column, paper id); the reference texts pass `text_leakage` (ClimRR, column
names, identifier-like names, "according to" / "the table" / "the paper", "et al.",
years in parentheses, corpus and internal ids); schema v2 and `consistency_errors`.
v2 (pilot P2b-final-prep; D-055): numbers are traced in the prompt too, and against the packet's
`allowed_descriptors` (DR-DESC-1) as well as its pattern values; number-words (one ... ninety-nine,
hundred, thousand, "-fold", twice, double, triple, half) must lie inside an allowed descriptor phrase
("one study" and "one high-emissions scenario" excepted); and the reference answer and rubric carry no
exact pattern value with a decimal (`exact_value_in_graded_text`): exact values belong to provenance.
v2.2 (D-055b): number-words start at "two" --- "one", "a", "an", "once", "single" are never numeric
("twenty-one" still is); "has been reported" is a hedge word. `format_class_only` tells the synthesis
agent whether every failure reason is a format failure (one corrective turn, D-055b).
v3 (work package P3a; D-060, D-061, D-062; run by litsynth_agent v4): v2.3 (model-source phrases) on by default, plus
the generality rule --- the prompt, reference texts and rubric carry no RCP label, no threshold such as "95 °F", no year
and no "one study" / "a single study" (`GENERALITY_RE`, the work package's pattern); the number rule is unchanged (the
coarse anchor pair stays allowed). A hedge-by-strength report (`hedge_by_strength`; report only, not a failure): a
literature sentence citing only single-source groups should say "suggests"; one citing a multi-source or review group
should not say "suggests" without "shows" / "shown".
v3, fire-weather words (P3a hotfix, D-053b): for a packet whose `checks_input.family` is `fire_weather_index` (packets
v4a), "wildfire(s)", "fires" and "burned area" in the prompt, reference texts or rubric are a failure
(`FWI_FORBIDDEN_RE`; not a format class, so no corrective turn) --- except in `rubric.disallowed_claims` and
`rubric.fatal_errors`, which name the fire-occurrence misreading the guardrail rules out (EXECUTOR reading, for
confirmation); hits there, and "fire" alone anywhere --- not "fire-weather" / "fire danger", and not inside the packet's
plain quantity phrases (`checks_input.plain_quantity`) --- are reported in `checks.fire_word_report`, not failed. Packets
without `family` (v3, v4) are checked exactly as before.

**Item schema v2a** (work package P5c hotfix, D-077; `item_schema_v2a.json`): v2 plus the literature statement type
`impact` (rung 8), which must carry `asset_class` (a lexicon class), `impact_mechanism`, `impact_outcome`, `hazard_relation`
(governed_term | broader_hazard) and `two_hop`; `schema_version: benchmark_item_v2a`. `schema_errors` picks the schema by
the item's `schema_version` (v2 items are checked against v2, unchanged).

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
SCHEMA_V2A_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "item_schema_v2a.json"
SCHEMA_VERSION_V2A = "benchmark_item_v2a"
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


def schema_for(item: dict) -> dict:
    """D-077: schema v2a for an item whose `schema_version` is benchmark_item_v2a, else schema v2."""
    v2a = isinstance(item, dict) and item.get("schema_version") == SCHEMA_VERSION_V2A
    return load_schema(SCHEMA_V2A_PATH if v2a else SCHEMA_PATH)


def schema_errors(item: dict, schema: dict | None = None) -> list[str]:
    errors: list[str] = []
    softqa._check(item, resolve_refs(schema or schema_for(item)), "$", errors)
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


# --- synthesis post-checks (pilot P2b-prep; litsynth_agent.py) ---------------------------------

SYNTH_CHECK_VERSION = "synthesis_post_checks v2.2"
# v2.3 (mentor-export package, 2026-11-03): v2.2 plus `MODEL_SOURCE_RES` --- a reference text or prompt that cites the
# model, projection, data or table as its source ("The model shows ..."). Opt-in (`check_version=`): the default stays
# v2.2, which the frozen litsynth_agent v3.2 runs and runs 2 and 3 are reproduced with; v2.3 was a report-only re-run.
SYNTH_CHECK_VERSION_V23 = "synthesis_post_checks v2.3"
# v3 (work package P3a, D-060 -- D-062): v2.3 plus the generality rule and the hedge-by-strength report. Opt-in as well:
# litsynth_agent v4 passes it; v2.2 stays the default the ingest of runs 2 and 3 reproduces.
SYNTH_CHECK_VERSION_V3 = "synthesis_post_checks v3"
# v3.1 (work package P3b, D-066, D-067): v3 plus the readability rules --- a context group never written as a driver
# (`context_as_driver`), no tercile wording, no doubled magnitude phrase, sentences start with a capital letter (all four
# format-class failures), and two reports (a context phrase in a driver sentence of the paragraph; a regional contrast
# claimed to be explained). Opt-in: litsynth_agent v4.1 passes it; v3 stays what the run-4 reproduction uses.
SYNTH_CHECK_VERSION_V31 = "synthesis_post_checks v3.1"
# v3.2 (work package P5a, D-069; updated in the P5a hotfix for D-069a before any run: the `mixed` class and the optional
# ", including work on <Place>" clause after the stem): v3.1 plus scope marking --- every literature sentence opens with the scope phrase of its
# cited groups; the general closing clause when (and only when) no cited group is state- or NCA-specific; no required
# rubric point names the place on a group's authority; the question opens as its assigned question form (all format-
# class) --- and the mixed-scope report. Opt-in: litsynth_agent v5 passes it.
SYNTH_CHECK_VERSION_V32 = "synthesis_post_checks v3.2"
# v3.3 (work package P5b, D-073b, D-075): v3.2 plus (a) D-073b --- in a fire-weather item "wildfire" is allowed only inside
# the exact phrase "conditions that favour wildfire" (masked before FWI_FORBIDDEN_RE; any other "wildfire" still fails);
# (b) the rung-8 wording rules, applied when `checks_input.rung8` is present (rung-8 packets, P5c): no asset-failure claim
# ("<asset> in <Place> will fail / is at risk"); "this implies more exposure to" only when the item cites a place-named
# impact group; a literature sentence citing an impact group opens with its scope phrase + " that", names the packet's
# asset-class phrase, and names the broader-hazard phrase when a cited impact group rests on a broader hazard term (else the
# plain quantity). All format-class. Opt-in: litsynth_agent v5.2 passes it; v3.2 is unchanged.
SYNTH_CHECK_VERSION_V33 = "synthesis_post_checks v3.3"
# v3.4 (work package P5c hotfix, D-073c): v3.3 plus the two-hop wording, applied when `checks_input.rung8.two_hop_group_ids`
# is present (packets v1a): a literature sentence citing a two-hop group must contain "when wildfires occur", "wildfires can"
# or "raise the chance of ignition" (`TWO_HOP_RE`), and is exempt from the hazard-phrase rule (the direct groups it cites
# keep it); when the item cites a two-hop group and the packet gives a `bridge_clause` (fire-weather packets), the integrated
# paragraph contains it exactly once; in a fire-weather item the two two-hop phrases are masked like "conditions that favour
# wildfire" everywhere but the prompt. All format-class. Opt-in: litsynth_agent v5.3 passes it; v3.3 is unchanged.
SYNTH_CHECK_VERSION_V34 = "synthesis_post_checks v3.4"
SYNTH_CHECK_VERSIONS = (SYNTH_CHECK_VERSION, SYNTH_CHECK_VERSION_V23, SYNTH_CHECK_VERSION_V3, SYNTH_CHECK_VERSION_V31,
                        SYNTH_CHECK_VERSION_V32, SYNTH_CHECK_VERSION_V33, SYNTH_CHECK_VERSION_V34)
_V3_PLUS = (SYNTH_CHECK_VERSION_V3, SYNTH_CHECK_VERSION_V31, SYNTH_CHECK_VERSION_V32, SYNTH_CHECK_VERSION_V33, SYNTH_CHECK_VERSION_V34)
_V31_PLUS = (SYNTH_CHECK_VERSION_V31, SYNTH_CHECK_VERSION_V32, SYNTH_CHECK_VERSION_V33, SYNTH_CHECK_VERSION_V34)
_V32_PLUS = (SYNTH_CHECK_VERSION_V32, SYNTH_CHECK_VERSION_V33, SYNTH_CHECK_VERSION_V34)
_V33_PLUS = (SYNTH_CHECK_VERSION_V33, SYNTH_CHECK_VERSION_V34)
#: v3.1 (D-067): the driver / cause words a sentence resting only on context groups must not carry next to the context phrase.
DRIVER_WORD_RE = re.compile(r"\bdriven\s+by\b|\bdrivers?\b|\bdrives?\b|\bcause[sd]?\b|\bcausing\b|\bbecause\s+of\b", re.I)
#: v3.1 (DR-DESC-1 v4, D-066): the relative tercile is written as a comparison with other states, never with these words.
TERCILE_WORD_RE = re.compile(r"\btercile\b|\brank(?:s|ing)?\s+(?:small|moderate|large)\b", re.I)
#: v3.1 (D-066): a direction verb followed by a magnitude phrase of its own ("increase a slight increase").
DOUBLED_MAGNITUDE_RE = re.compile(r"\b(?:increase[sd]?|rises?|grows?)\s+(?:by\s+)?(?:a|an)\s+(?:slight|small|moderate)\s+(?:increase|rise)\b", re.I)
#: v3.1 report: a sentence claiming to explain a contrast, ranking or difference.
CONTRAST_CLAIM_RE = re.compile(r"\b(?:explain(?:s|ed|ing)?|account(?:s|ed)?\s+for|why)\b[^.]*\b(?:contrast|difference|differences|ranking)\b"
                               r"|\b(?:contrast|difference|differences|ranking)\b[^.]*\b(?:is|are)\s+(?:explained|driven|caused)\b", re.I)
CLAUSE_SPLIT_RE = re.compile(r"[,;:]|\s[–—-]\s")
SENTENCE_SPLIT_RE = re.compile(r"(?<!U\.S\.)(?<!e\.g\.)(?<!i\.e\.)(?<=[.!?])\s+")   # not after "U.S.", "e.g.", "i.e."
_CONTEXT_STOP = frozenset({"about", "also", "and", "are", "as", "based", "between", "both", "from", "have", "into", "more", "most",
                           "such", "than", "that", "their", "these", "they", "this", "used", "using", "when", "where", "which",
                           "while", "with", "within"})
#: The work package's pattern, `RCP|\d{2,}\s?°?F|\b(19|20)\d{2}\b|one study|a single study`, applied to the normalised text
#: (`normalise_number_text`: "95℉" and "95\u202f°F" read "95 °F"); the two phrases case-insensitively.
GENERALITY_RE = re.compile(r"RCP|\d{2,}\s?°?F|\b(?:19|20)\d{2}\b|(?i:one study|a single study)")
#: P3a hotfix (D-053b): never in a fire-weather item's graded text --- an FWI is a fire-danger index, never fire occurrence.
FWI_FORBIDDEN_RE = re.compile(r"\bwild[- ]?fires?\b|\bfires\b|\bburned\s+area\b", re.I)
#: "fire" alone (not "fire-weather", "fire weather", "fire-danger", "fire danger"): reported, not failed.
FWI_FIRE_WORD_RE = re.compile(r"\bfire\b(?![-\s](?:weather|danger)\b)", re.I)
FWI_FAMILY = "fire_weather_index"
#: Rubric lists that describe wrong answers: an FWI-forbidden word there is reported, not failed (EXECUTOR reading).
FWI_WRONG_ANSWER_FIELDS = ("rubric.disallowed_claims", "rubric.fatal_errors")
SHOW_RE = re.compile(r"\bshows?\b|\bshown\b", re.I)
SUGGEST_RE = re.compile(r"\bsuggests?\b", re.I)
MODEL_SOURCE_RES = (re.compile(r"\b(the|this|our) (model|projection|modeled projection|data|dataset|table) (shows?|indicates?|projects?|suggests?)\b", re.I),
                    re.compile(r"\bmodeled projection shows\b", re.I))
INTERNAL_ID_RE = re.compile(r"\b(?:LS|LG|LC|SD[12]|PK|BI)-[A-Za-z0-9_-]+|\bTP\d+-\d+\b")
COLUMN_LIKE_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+\b")  # an identifier such as heatindex_HIS_Day95
SCENARIO_NAME_RE = re.compile(r"\b(?:RCP|SSP)\s?\d(?:\.\d)?(?:\s?-\s?\d(?:\.\d)?)?\b|\bCMIP\d\b", re.I)
WEIGHT_PREFIX_RE = re.compile(r"^\[w=\d+\]\s*")  # litsynth_agent writes a required point's weight as "[w=2] point"
ORDINAL_RE = re.compile(r"\b\d+(?:st|nd|rd|th)\b", re.I)
NUMBER_RE = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
_ONES = "one|two|three|four|five|six|seven|eight|nine"
_ONES_FROM_TWO = "two|three|four|five|six|seven|eight|nine"
_TEENS = "ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen"
_TENS = "twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
# v2 (D-055): number-words --- one ... ninety-nine, hundred, thousand, "-fold", twice, double, triple, half (with their
# inflections: doubling, tripled, halved ...). v2.2 (D-055b): a standalone number-word starts at "two"; "one" (and "a",
# "an", "once", "single") is never numeric --- run 1 rejected 7 items on "one high-emissions scenario"
NUMBER_WORD_RE = re.compile(rf"\b(?:(?:{_TENS})(?:[-\s](?:{_ONES}))?|{_TEENS}|{_ONES_FROM_TWO}|hundreds?|thousands?|twice|doubl\w*"
                            rf"|tripl\w*|hal(?:f|ves|ved|ving)|\w+-fold|(?:{_ONES_FROM_TWO}|{_TEENS}|several|many)fold)\b", re.I)
HEDGE_RE = re.compile(r"\b(?:one|a single|a|an individual) (?:study|paper|analysis)\b|\bsuggests?\b|\bmay\b|\bmight\b|\bcould\b"
                      r"|\blimited evidence\b|\bsome evidence\b|\btentative(?:ly)?\b|\breportedly\b|\bhas been reported\b", re.I)


def reference_numbers(text: str) -> list[str]:
    """Numbers in a reference text, after removing scenario names (RCP8.5, SSP5-8.5, CMIP6) and ordinals (21st);
    thousands separators dropped."""
    stripped = ORDINAL_RE.sub(" ", SCENARIO_NAME_RE.sub(" ", text))
    return [m.group(0).replace(",", "") for m in NUMBER_RE.finditer(stripped)]


# v2.1 (D-055a): a number in a literature sentence tagged with group ids, or in a rubric point whose source_ids name
# groups, may trace to those groups' label or member statements instead, compared after this normalisation
UNIT_NUMBER_RE = re.compile(rf"({NUMBER_RE.pattern})(\s?°[FC]\b)?")


def normalise_number_text(text: str) -> str:
    """Whitespace (incl. narrow no-break space) collapsed; ℉ / ℃ / º° spellings to '°F' / '°C'; '80°F', '80 ° F' -> '80 °F'."""
    t = text.replace("℉", "°F").replace("℃", "°C").replace("º", "°")
    t = re.sub(r"\s+", " ", t)
    return re.sub(r"(\d)\s?°\s?([FC])\b", r"\1 °\2", t)


def literature_tokens(text: str) -> list[tuple[str, str]]:
    """[(number, number with its °F / °C unit, or the number alone)] in normalised `text`, after the scenario names and
    ordinals `reference_numbers` removes."""
    stripped = ORDINAL_RE.sub(" ", SCENARIO_NAME_RE.sub(" ", normalise_number_text(text)))
    return [(m.group(1).replace(",", ""), m.group(1).replace(",", "") + (m.group(2) or "")) for m in UNIT_NUMBER_RE.finditer(stripped)]


def literature_trace(group_ids, group_texts: dict) -> tuple[set[str], set[str], set[str]]:
    """(bare numbers, numbers with units, lower-case number-words) stated in the label or member statements of the
    cited groups that are in the packet."""
    src = [t for g in group_ids if g in group_texts for t in group_texts[g]]
    toks = [x for t in src for x in literature_tokens(t)]
    words = {m.group(0).lower() for t in src for m in NUMBER_WORD_RE.finditer(normalise_number_text(t))}
    return {n for n, _ in toks}, {u for _, u in toks}, words


def untraced_numbers(text: str, allowed: set[str], lit: tuple[set[str], set[str], set[str]] | None = None) -> list[str]:
    """Numbers in `text` not in `allowed` (v2). With `lit` (v2.1, a group-tagged sentence or rubric point): a number with a
    °F / °C unit also passes when the cited groups state it with that unit, a bare number when they state it at all."""
    if lit is None:
        return [n for n in reference_numbers(text) if n not in allowed]
    bare, with_unit, _ = lit
    return [n for n, u in literature_tokens(text) if n not in allowed and not (u in with_unit if u != n else n in bare)]


def untraced_number_words(text: str, phrases: list[str]) -> list[str]:
    """Number-words in `text` not inside an occurrence of an allowed phrase (case-insensitive)."""
    spans = []
    low = text.lower()
    for ph in phrases:
        ph, i = ph.lower(), 0
        while ph and (i := low.find(ph, i)) >= 0:
            spans.append((i, i + len(ph)))
            i += 1
    return [m.group(0) for m in NUMBER_WORD_RE.finditer(text) if not any(a <= m.start() and m.end() <= b for a, b in spans)]


def text_leakage(text: str, columns: list[str] | None = None, forbidden: list[str] = ()) -> list[str]:
    """Source-leakage flags for a reference text (the prompt uses `leakage_check`, which also flags exact values)."""
    cols = columns if columns is not None else column_names()
    checked = {c.lower() for c in cols if c not in GENERIC_COLUMN_NAMES}
    flags = []
    if CLIMRR_RE.search(text):
        flags.append("ClimRR named")
    flags += [f"column name: {t}" for t in sorted({t for t in TOKEN_RE.findall(text) if t.lower() in checked})]
    flags += [f"identifier-like name: {t}" for t in sorted(set(COLUMN_LIKE_RE.findall(text)))]
    flags += [f"source phrase: {a}" for a in ACCORDING_RE.findall(text)]
    if ET_AL_RE.search(text):
        flags.append("'et al.'")
    flags += [f"year in parentheses {y!r}" for y in YEAR_PAREN_RE.findall(text)]
    flags += [f"corpus id: {t}" for t in CORPUS_ID_RE.findall(text)]
    flags += [f"internal id: {t}" for t in INTERNAL_ID_RE.findall(text)]
    flags += [f"packet source string: {s}" for s in forbidden if re.search(rf"(?<![A-Za-z0-9_]){re.escape(s)}(?![A-Za-z0-9_])", text)]
    return flags


def model_source_flags(text: str) -> list[str]:
    """v2.3: the phrases citing the model / projection / data / table as the source; a match inside an earlier pattern's
    match ("The modeled projection shows" hits both patterns) is flagged once. Case-insensitive."""
    spans: list[tuple[int, int]] = []
    out = []
    for rx in MODEL_SOURCE_RES:
        for m in rx.finditer(text):
            if not any(a <= m.start() and m.end() <= b for a, b in spans):
                spans.append(m.span())
                out.append(f"source phrase (v2.3): {m.group(0)}")
    return out


def _sentences(xs) -> list[dict]:
    return [x for x in xs if isinstance(x, dict) and isinstance(x.get("sentence"), str)] if isinstance(xs, list) else []


def synthesis_post_checks(item: dict, tagged: dict, checks_input: dict, columns: list[str] | None = None,
                          check_version: str = SYNTH_CHECK_VERSION) -> dict:
    """Deterministic checks on a synthesized item (pilot P2b). `tagged` is the model's decomposed reference answer:
    {"table_pattern": [{sentence, pattern_ids}], "literature_interpretation": [{sentence, group_ids, hedged}],
    "integrated": str, "rubric_points": [{field, point, source_ids}]}; `checks_input` comes from the seed packet. Returns
    {pass, reasons, checks, check_version}.

    v2.1 (D-055a): a number or number-word in a literature sentence tagged with group ids, or in a rubric point whose
    `source_ids` name groups, also passes when it appears in those groups' label or member statements
    (`checks_input.group_texts`; `literature_trace`). Table-pattern sentences, the integrated paragraph, the prompt and
    rubric text without group source ids keep the v2 rule.

    v2.3 (`check_version=SYNTH_CHECK_VERSION_V23`): also `model_source_flags` on the prompt and the reference texts.

    v3 (`check_version=SYNTH_CHECK_VERSION_V3`; D-060 -- D-062): v2.3, and `generality_flags` on the prompt, the reference
    texts and every rubric list (a failure); `checks.hedge_by_strength` reports hedge words that do not match the cited
    groups' strength (not a failure).

    v3.1 (`check_version=SYNTH_CHECK_VERSION_V31`; D-066, D-067): v3, and `readability_reasons` (context group written as a
    driver, tercile wording, doubled magnitude phrase, lower-case sentence start: failures) and `readability_reports`
    (`checks.context_driver_report`, `checks.regional_contrast_report`: not failures). `checks_input.group_role` names
    each group's role (driver / context / caveat) and `checks_input.regions` a regional contrast's regions."""
    if check_version not in SYNTH_CHECK_VERSIONS:
        raise ItemError(f"unknown post-check version {check_version!r}")
    cols = columns if columns is not None else column_names()
    reasons: list[str] = []
    tp_s, lit_s = _sentences(tagged.get("table_pattern")), _sentences(tagged.get("literature_interpretation"))
    integrated = tagged.get("integrated") if isinstance(tagged.get("integrated"), str) else ""
    if len(tp_s) != len(tagged.get("table_pattern") or []) or len(lit_s) != len(tagged.get("literature_interpretation") or []):
        reasons.append("reference_answer: a tagged sentence is not an object with a 'sentence' string")
    phrases = list(checks_input.get("allowed_descriptors") or [])
    allowed = {a.lstrip("+-") for a in checks_input["allowed_numbers"]} | {n for ph in phrases for n in reference_numbers(ph)}
    exact = set(checks_input.get("exact_values") or [a for a in allowed if "." in a])
    pattern_ids, strengths = set(checks_input["pattern_ids"]), checks_input["group_strength"]

    texts = [("table_pattern", s["sentence"]) for s in tp_s] + [("literature_interpretation", s["sentence"]) for s in lit_s] + \
            [("integrated", integrated)]
    rub = item.get("rubric") or {}
    texts_rubric = [(f"rubric.{k}", WEIGHT_PREFIX_RE.sub("", t)) for k, v in rub.items() if isinstance(v, list) for t in v if isinstance(t, str)]
    graded = texts + texts_rubric
    every = [("prompt", item.get("prompt") or "")] + graded
    group_texts = checks_input.get("group_texts") or {}
    point_ids: dict = {}
    for r in tagged.get("rubric_points") or []:
        if isinstance(r, dict) and isinstance(r.get("point"), str) and isinstance(r.get("source_ids"), list):
            point_ids.setdefault((f"rubric.{r.get('field')}", r["point"]), []).extend(r["source_ids"])
    cites = [s.get("group_ids") if isinstance(s.get("group_ids"), list) else [] for s in lit_s]
    lit = {}                                                       # index into `every` -> literature_trace of its groups
    for i, (w, t) in enumerate(every):
        gids = cites[i - 1 - len(tp_s)] if w == "literature_interpretation" else point_ids.get((w, t), [])
        gids = [g for g in gids if isinstance(g, str) and g in group_texts]
        if gids:
            lit[i] = literature_trace(gids, group_texts)
    untraced = sorted({(w, n) for i, (w, t) in enumerate(every) for n in untraced_numbers(t, allowed, lit.get(i))})
    reasons += [f"{w}: number {n} does not trace to a pattern value or allowed descriptor in the packet" for w, n in untraced]
    words = sorted({(w, x) for i, (w, t) in enumerate(every) for x in untraced_number_words(t, phrases)
                    if i not in lit or x.lower() not in lit[i][2]})
    reasons += [f"{w}: number-word {x!r} does not trace to an allowed descriptor in the packet" for w, x in words]
    exact_hits = sorted({(w, n) for w, t in graded for n in reference_numbers(t) if n in exact})
    reasons += [f"{w}: exact_value_in_graded_text {n} (exact values belong to provenance)" for w, n in exact_hits]

    if checks_input["pattern_ids"] and not tp_s:
        reasons.append("reference_answer.table_pattern: no sentence while the packet has a table pattern")
    for i, s in enumerate(tp_s):
        ids = s.get("pattern_ids") if isinstance(s.get("pattern_ids"), list) else []
        if not ids:
            reasons.append(f"table_pattern[{i}]: no pattern id")
        reasons += [f"table_pattern[{i}]: pattern id {p} not in the packet" for p in ids if p not in pattern_ids]
    if strengths and not lit_s:
        reasons.append("reference_answer.literature_interpretation: no sentence while the packet has literature groups")
    clause = ((checks_input.get("scope") or {}).get("general_clause") or "").strip() if check_version in _V32_PLUS else ""
    for i, s in enumerate(lit_s):
        ids = s.get("group_ids") if isinstance(s.get("group_ids"), list) else []
        if not ids and clause and s["sentence"].strip() == clause:   # v3.2: the D-069 closing clause cites no group
            continue
        if not ids:
            reasons.append(f"literature_interpretation[{i}]: cites no group id")
        bad = [g for g in ids if g not in strengths]
        reasons += [f"literature_interpretation[{i}]: group id {g} not in the packet" for g in bad]
        good = [g for g in ids if g in strengths]
        if good and all(strengths[g] == "single_source_supported" for g in good):
            if s.get("hedged") is not True:
                reasons.append(f"literature_interpretation[{i}]: rests only on single-source groups but is not marked hedged")
            if not HEDGE_RE.search(s["sentence"]):
                reasons.append(f"literature_interpretation[{i}]: rests only on single-source groups but carries no hedge word")

    leak = leakage_check(item.get("prompt") or "", cols)
    if not leak["pass"]:
        reasons += [f"prompt leakage: {f}" for f in leak["flags"]]
    prompt_extra = [f for f in text_leakage(item.get("prompt") or "", cols, checks_input.get("forbidden_strings", []))
                    if f.startswith(("internal id", "identifier-like", "packet source"))]
    reasons += [f"prompt leakage: {f}" for f in prompt_extra]
    for w, t in texts:
        reasons += [f"{w} leakage: {f}" for f in text_leakage(t, cols, checks_input.get("forbidden_strings", []))]
    if check_version in (SYNTH_CHECK_VERSION_V23, *_V3_PLUS):
        reasons += [f"{w} leakage: {f}" for w, t in [("prompt", item.get("prompt") or "")] + texts for f in model_source_flags(t)]
    hedge_report = None
    if check_version in _V3_PLUS:
        reasons += [f"{w}: generality (D-060/D-062): {m!r} in graded text" for w, t in every for m in generality_flags(t)]
        hedge_report = hedge_by_strength(lit_s, strengths)
    fire_report = None
    if check_version in _V3_PLUS and checks_input.get("family") == FWI_FAMILY:
        mask = check_version in _V33_PLUS                                # D-073b
        hop = check_version == SYNTH_CHECK_VERSION_V34 and bool((checks_input.get("rung8") or {}).get("two_hop_group_ids"))  # D-073c

        def masked(w: str, t: str) -> str:
            t = mask_wildfire_phrase(t) if mask else t
            return mask_two_hop_phrases(t) if hop and w != "prompt" else t

        reasons += [f"{w}: fire-weather wording (an FWI is never fire occurrence): {m!r} in graded text"
                    for w, t in every if w not in FWI_WRONG_ANSWER_FIELDS for m in fwi_forbidden_flags(masked(w, t))]
        plain = [q for q in checks_input.get("plain_quantity") or [] if isinstance(q, str) and q]
        fire_report = [{"field": w, "word": m, "kind": "forbidden_word_in_wrong_answer_list"}
                       for w, t in every if w in FWI_WRONG_ANSWER_FIELDS for m in fwi_forbidden_flags(t)] + \
                      [{"field": w, "word": m, "kind": "fire_alone"} for w, t in every for m in fwi_fire_words(t, plain)]
    readability = None
    if check_version in _V31_PLUS:
        reasons += readability_reasons(item.get("prompt") or "", tp_s, lit_s, integrated, graded, checks_input)
        readability = readability_reports(tp_s, lit_s, integrated, item.get("prompt") or "", checks_input)
    scope_rep = None
    if check_version in _V32_PLUS:
        sr, scope_rep = scope_checks(lit_s, integrated, tagged.get("rubric_points") or [], checks_input)
        reasons += sr
        reasons += question_form_reasons(item.get("prompt") or "", checks_input)
    rung8_rep = None
    if check_version in _V33_PLUS and checks_input.get("rung8"):
        r8, rung8_rep = rung8_reasons(lit_s, integrated, every, checks_input, two_hop=check_version == SYNTH_CHECK_VERSION_V34)
        reasons += r8

    schema = schema_errors(item)
    reasons += [f"schema: {e}" for e in schema]
    if not schema:
        reasons += [f"consistency: {e}" for e in consistency_errors(item, cols)]
    return {"check_version": check_version, "pass": not reasons, "reasons": reasons,
            "checks": {"numbers_untraced": [n for _, n in untraced], "number_words_untraced": [x for _, x in words],
                       "exact_values_in_graded_text": [n for _, n in exact_hits], "prompt_leakage": leak, "schema_errors": schema,
                       "texts_traced_to_literature": [every[i][0] for i in sorted(lit)],
                       "rubric_points_without_source_ids": sum(not (isinstance(r, dict) and r.get("source_ids"))
                                                               for r in tagged.get("rubric_points") or []),
                       "n_table_sentences": len(tp_s), "n_literature_sentences": len(lit_s),
                       **({"hedge_by_strength": hedge_report} if hedge_report is not None else {}),
                       **({"fire_word_report": fire_report} if fire_report is not None else {}),
                       **(readability or {}), **(scope_rep or {}), **({"rung8_report": rung8_rep} if rung8_rep is not None else {})}}


def _terms(text: str) -> set[str]:
    """Content words (>= 4 letters, not a stopword), compared by their first 6 letters ("combines" ~ "combined")."""
    return {w.lower()[:6] for w in re.findall(r"[A-Za-z]{4,}", text or "") if w.lower() not in _CONTEXT_STOP}


def context_terms(group_ids, checks_input: dict) -> set[str]:
    """v3.1: content words (>= 4 letters) of the labels of the cited context groups --- the "context phrase"."""
    texts = checks_input.get("group_texts") or {}
    return {t for g in group_ids for t in _terms((texts.get(g) or [""])[0])}


def _context_only(ids, checks_input: dict) -> list[str]:
    role = checks_input.get("group_role") or {}
    ids = [g for g in ids if g in role]
    return ids if ids and all(role[g] == "context" for g in ids) else []


def lower_case_starts(text: str) -> list[str]:
    """v3.1: the sentences of `text` whose first letter is lower-case (their first 30 characters)."""
    out = []
    for sent in SENTENCE_SPLIT_RE.split(text.strip()):
        m = re.search(r"[A-Za-z]", sent)
        if m and sent[m.start()].islower():
            out.append(sent[:30])
    return out


def readability_reasons(prompt: str, tp_s: list[dict], lit_s: list[dict], integrated: str, graded: list[tuple[str, str]],
                        checks_input: dict) -> list[str]:
    """v3.1 failures (D-066, D-067; every one format-class): a literature sentence resting only on context groups that
    names a driver or cause in a clause with the context phrase (`context_as_driver`); tercile wording, or a doubled
    magnitude phrase, in the prompt or any graded text; a reference sentence starting with a lower-case letter."""
    out = []
    for i, s in enumerate(lit_s):
        ids = _context_only(s.get("group_ids") if isinstance(s.get("group_ids"), list) else [], checks_input)
        if not ids:
            continue
        terms = context_terms(ids, checks_input)
        for clause in CLAUSE_SPLIT_RE.split(s["sentence"]):
            if DRIVER_WORD_RE.search(clause) and _terms(clause) & terms:
                out.append(f"literature_interpretation[{i}]: context_as_driver (D-067): {clause.strip()!r}")
    for w, t in [("prompt", prompt)] + graded:
        out += [f"{w}: tercile wording (DR-DESC-1 v4): {m.group(0)!r} in graded text" for m in TERCILE_WORD_RE.finditer(t)]
        out += [f"{w}: doubled magnitude phrase (DR-DESC-1 v4): {m.group(0)!r}" for m in DOUBLED_MAGNITUDE_RE.finditer(t)]
    starts = [("prompt", prompt)] + [("table_pattern", s["sentence"]) for s in tp_s] + \
             [("literature_interpretation", s["sentence"]) for s in lit_s] + [("integrated", integrated)]
    out += [f"{w}: sentence starts with a lower-case letter: {x!r}" for w, t in starts for x in lower_case_starts(t)]
    return out


def readability_reports(tp_s: list[dict], lit_s: list[dict], integrated: str, prompt: str, checks_input: dict) -> dict:
    """v3.1 reports (not failures). `context_driver_report`: a sentence of the table-pattern or integrated text with a
    driver word and a context group's term (a context group listed among the drivers, D-067). `regional_contrast_report`:
    for a regional contrast (`checks_input.regions`), a sentence claiming to explain the contrast or ranking while a region
    it names (none named: the largest and the smallest) is named by no cited group."""
    role = checks_input.get("group_role") or {}
    cited = sorted({g for s in lit_s for g in (s.get("group_ids") or []) if isinstance(g, str) and g in role})
    cterms = context_terms([g for g in cited if role[g] == "context"], checks_input)
    cterms -= context_terms([g for g in cited if role[g] != "context"], checks_input)   # words of a cited driver too
    cterms -= {t for q in checks_input.get("plain_quantity") or [] for t in _terms(q)}  # the quantity's own words
    ctx_report = []
    for w, t in [("table_pattern", s["sentence"]) for s in tp_s] + [("integrated", integrated)]:
        for sent in SENTENCE_SPLIT_RE.split(t):
            hit = sorted(_terms(sent) & cterms)
            if hit and DRIVER_WORD_RE.search(sent):
                ctx_report.append({"field": w, "sentence": sent, "context_terms": hit})
    regions = checks_input.get("regions") or []
    reg_report = []
    if regions:
        texts = checks_input.get("group_texts") or {}
        for w, t in [("prompt", prompt)] + [("literature_interpretation", s["sentence"]) for s in lit_s] + [("integrated", integrated)]:
            for sent in SENTENCE_SPLIT_RE.split(t):
                if not CONTRAST_CLAIM_RE.search(sent):
                    continue
                claimed = [r for r in regions if r in sent] or [regions[0], regions[-1]]   # none named: largest and smallest
                unnamed = [r for r in claimed if not any(r in x for g in cited for x in texts.get(g, []))]
                if unnamed:
                    reg_report.append({"field": w, "sentence": sent, "regions_not_named_by_a_cited_group": unnamed})
    return {"context_driver_report": ctx_report, "regional_contrast_report": reg_report}


def fwi_forbidden_flags(text: str) -> list[str]:
    """P3a hotfix (D-053b): the matches of `FWI_FORBIDDEN_RE` in `text` ("wildfire", "fires", "burned area")."""
    return [m.group(0) for m in FWI_FORBIDDEN_RE.finditer(text or "")]


def fwi_fire_words(text: str, plain_phrases: list[str] = ()) -> list[str]:
    """P3a hotfix (D-053b), report only: "fire" alone in `text`, outside the plain quantity phrases (longest removed first)."""
    t = text or ""
    for ph in sorted(plain_phrases, key=len, reverse=True):
        t = re.sub(re.escape(ph), " ", t, flags=re.I)
    return [m.group(0) for m in FWI_FIRE_WORD_RE.finditer(t)]


#: D-073b (work package P5b): the only phrase in which a fire-weather item's graded text may write "wildfire".
WILDFIRE_ALLOWED_PHRASE = "conditions that favour wildfire"
_WILDFIRE_PHRASE_RE = re.compile(r"\bconditions\s+that\s+favour\s+wildfire\b", re.I)


def mask_wildfire_phrase(text: str) -> str:
    """v3.3 (D-073b): `text` with every "conditions that favour wildfire" replaced by a neutral placeholder word, so that
    FWI_FORBIDDEN_RE sees only the other uses of "wildfire"."""
    return _WILDFIRE_PHRASE_RE.sub("conditions that favour WFPHRASE", text or "")


#: D-073c (work package P5c hotfix): the two-hop phrases that may write "wildfires" in a fire-weather item (post-checks v3.4).
_TWO_HOP_MASK_RE = re.compile(r"\b(when\s+)wildfires(\s+occur)\b|\bwildfires(\s+can)\b", re.I)


def mask_two_hop_phrases(text: str) -> str:
    """v3.4 (D-073c): `text` with "wildfires" inside "when wildfires occur" / "wildfires can" replaced by a placeholder."""
    return _TWO_HOP_MASK_RE.sub(lambda m: f"{m.group(1)}WFHOP{m.group(2)}" if m.group(1) else f"WFHOP{m.group(3)}", text or "")


def generality_flags(text: str) -> list[str]:
    """v3 (D-060, D-062): the matches of `GENERALITY_RE` in the normalised `text`."""
    return [m.group(0) for m in GENERALITY_RE.finditer(normalise_number_text(text))]


def hedge_by_strength(lit_s: list[dict], strengths: dict) -> list[dict]:
    """v3 report (D-062): literature sentences whose hedge does not match the cited packet groups' strength --- only
    single-source groups and no "suggests"; or a multi-source / review group and "suggests" without "shows" / "shown"."""
    out = []
    for i, s in enumerate(lit_s):
        ids = [g for g in (s.get("group_ids") if isinstance(s.get("group_ids"), list) else []) if g in strengths]
        if not ids:
            continue
        single = all(strengths[g] == "single_source_supported" for g in ids)
        t = s["sentence"]
        if single and not SUGGEST_RE.search(t):
            out.append({"sentence": i, "issue": "single-source groups only, no 'suggests'", "group_ids": ids})
        elif not single and SUGGEST_RE.search(t) and not SHOW_RE.search(t):
            out.append({"sentence": i, "issue": "a multi-source or review group, 'suggests' without 'shows'", "group_ids": ids})
    return out


# --- v3.2: scope marking (D-069) and question forms (P5a) ------------------------------------------------

#: Most specific first. D-069: state, nca, us_subregion / us_national, then global / other / unknown ("In general").
#: D-069a (packets v5a): `mixed` --- a tie for the most cited members --- is general too ("In general").
SCOPE_CLASS_ORDER = ("state", "nca", "us_subregion", "us_national", "global", "other", "unknown", "mixed")
PLACE_SPECIFIC_CLASSES = ("state", "nca")
SCOPE_VERBS_MULTI = ("shows", "has shown")
SCOPE_VERBS_SINGLE = ("suggests",)


def scope_verbs(group_ids, strengths: dict) -> tuple[str, ...]:
    """D-062 under D-069: "shows" / "has shown" when a cited group is multi-source or review, else "suggests"."""
    ids = [g for g in group_ids if g in strengths]
    return SCOPE_VERBS_SINGLE if ids and all(strengths[g] == "single_source_supported" for g in ids) else SCOPE_VERBS_MULTI


def best_scope(group_ids, scope_groups: dict) -> dict | None:
    """The scope record (`class`, `stem`) of the most specific cited group."""
    recs = [scope_groups[g] for g in group_ids if g in scope_groups]
    return min(recs, key=lambda r: SCOPE_CLASS_ORDER.index(r["class"])) if recs else None


def scope_openings(group_ids, scope_groups: dict, strengths: dict) -> list[str]:
    """The allowed openings: the best group's stem + verb; D-069a (packets v5a) also stem + optional clause + ", " + verb,
    for the optional clause of any cited group with that stem ("In general, research, including work on California,
    shows"). A v5 packet carries no optional clause, so its openings are unchanged."""
    best = best_scope(group_ids, scope_groups)
    if not best:
        return []
    clauses = list(dict.fromkeys(scope_groups[g]["optional_clause"] for g in group_ids
                                 if g in scope_groups and scope_groups[g].get("optional_clause") and scope_groups[g]["stem"] == best["stem"]))
    verbs = scope_verbs(group_ids, strengths)
    return [f"{best['stem']} {v}" for v in verbs] + [f"{best['stem']}{c}, {v}" for c in clauses for v in verbs]


def scope_checks(lit_s: list[dict], integrated: str, rubric_points: list, checks_input: dict) -> tuple[list[str], dict]:
    """v3.2 (D-069). Failures: a literature sentence that does not begin with its scope phrase (stem of the most specific
    cited group + "shows" / "has shown", or "suggests" when every cited group is single-source); the closing clause
    missing (as the last literature entry, with no group, and as the end of the integrated paragraph) when no cited group
    is state- or NCA-specific, or present when one is; a sentence of the integrated paragraph that names "research" and does
    not begin with one of the cited groups' scope openings; a required rubric point resting on a group that names the place.
    Report: `mixed_scope_report` --- a literature sentence citing groups of different scope classes."""
    sc = checks_input.get("scope") or {}
    groups, strengths = sc.get("groups") or {}, checks_input.get("group_strength") or {}
    clause = (sc.get("general_clause") or "").strip()
    out, mixed = [], []
    cited = []
    for i, s in enumerate(lit_s):
        ids = [g for g in (s.get("group_ids") if isinstance(s.get("group_ids"), list) else []) if isinstance(g, str)]
        text = s["sentence"].strip()
        if not ids and clause and text == clause:
            continue
        cited += [g for g in ids if g in groups and g not in cited]
        opens = scope_openings(ids, groups, strengths)
        if opens and not any(text.startswith(o) for o in opens):
            out.append(f"literature_interpretation[{i}]: scope phrase (D-069): the sentence must begin with "
                       + " or ".join(repr(o) for o in opens))
        classes = sorted({groups[g]["class"] for g in ids if g in groups}, key=SCOPE_CLASS_ORDER.index)
        if len(classes) > 1:
            mixed.append({"sentence": i, "classes": classes, "group_ids": ids})
    specific = any(groups[g]["class"] in PLACE_SPECIFIC_CLASSES for g in cited)
    last = lit_s[-1] if lit_s else None
    clause_last = bool(last) and not (last.get("group_ids") or []) and last["sentence"].strip() == clause
    if clause:
        if not specific and not clause_last:
            out.append(f"literature_interpretation: closing clause (D-069) missing as the last entry: {clause!r}")
        if specific and clause_last:
            out.append("literature_interpretation: closing clause (D-069) present though a cited group is state- or NCA-specific")
        in_integrated = clause in (integrated or "")
        if not specific and not (integrated or "").strip().endswith(clause):
            out.append(f"integrated: closing clause (D-069) missing at the end: {clause!r}")
        if specific and in_integrated:
            out.append("integrated: closing clause (D-069) present though a cited group is state- or NCA-specific")
    allowed = sorted({o for g in cited for o in scope_openings([g], groups, strengths)} |
                     {o for s in lit_s for o in scope_openings([g for g in (s.get("group_ids") or []) if isinstance(g, str)], groups, strengths)})
    for sent in SENTENCE_SPLIT_RE.split((integrated or "").strip()):
        if re.search(r"\bresearch\b", sent, re.I) and allowed and not any(sent.startswith(o) for o in allowed):
            out.append(f"integrated: scope phrase (D-069): a sentence naming research must begin with one of the cited scope "
                       f"phrases: {sent[:60]!r}")
    places = [p for p in sc.get("place_names") or [] if p]
    for r in rubric_points:
        if not (isinstance(r, dict) and r.get("field") == "required_points" and isinstance(r.get("point"), str)):
            continue
        gids = [g for g in (r.get("source_ids") or []) if g in groups]
        hit = [p for p in places if re.search(rf"\b{re.escape(p)}\b", r["point"])]
        if gids and hit:
            out.append(f"rubric.required_points: place-specific mechanism required (D-069): {r['point'][:60]!r} names {hit[0]!r}")
    return out, {"mixed_scope_report": mixed, "scope_clause_required": bool(clause) and not specific}


def question_form_reasons(prompt: str, checks_input: dict) -> list[str]:
    """v3.2: the question opens as its assigned form (`opening_regex`) and holds at least `min_question_marks` '?'."""
    qf = checks_input.get("question_form") or {}
    if not qf:
        return []
    out = []
    if not re.match(qf["opening_regex"], (prompt or "").strip()):
        out.append(f"prompt: question form {qf['id']} ({qf['name']}): must open as {qf['opening_regex']!r}")
    if (prompt or "").count("?") < int(qf.get("min_question_marks", 1)):
        out.append(f"prompt: question form {qf['id']} ({qf['name']}): needs {qf.get('min_question_marks', 1)} question mark(s)")
    return out


# --- v3.3: rung-8 wording (D-075; work package P5b) ------------------------------------------------------------

#: "<asset> in <Place> will fail / is at risk" and its close forms: never in a rung-8 item's graded text (D-075 rule 3).
ASSET_FAILURE_RE = re.compile(r"\b(?:will|would|is\s+going\s+to|are\s+going\s+to)\s+(?:fail|break\s+down|collapse|be\s+(?:damaged|destroyed|disrupted))\b"
                              r"|\b(?:is|are)\s+(?:at\s+risk|vulnerable)\b|\bat\s+risk\s+of\s+fail\w*", re.I)
#: The one place-anchored impact form D-075 allows, only with a place-named impact group cited.
IMPLIES_EXPOSURE_RE = re.compile(r"\bthis\s+implies\s+more\s+exposure\s+to\b", re.I)
RUNG8_WRONG_ANSWER_FIELDS = FWI_WRONG_ANSWER_FIELDS


#: D-073c: a sentence resting on a two-hop group contains one of these.
TWO_HOP_RE = re.compile(r"\bwhen\s+wildfires\s+occur\b|\bwildfires\s+can\b|\braise\s+the\s+chance\s+of\s+ignitions?\b", re.I)


def bridge_count(text: str, bridge: str) -> int:
    """How often the D-073c bridge clause occurs in `text` (case and whitespace normalised)."""
    norm = lambda x: re.sub(r"\s+", " ", x or "").strip().lower()  # noqa: E731
    return norm(text).count(norm(bridge)) if bridge else 0


def rung8_reasons(lit_s: list[dict], integrated: str, every: list[tuple[str, str]], checks_input: dict,
                  two_hop: bool = False) -> tuple[list[str], dict]:
    """v3.3 (D-075). `checks_input.rung8`: {impact_group_ids, place_named_impact_group_ids, group_hazard_relation
    {group_id: governed_term | broader_hazard}, asset_class_phrase, broader_hazard_phrase, quantity_phrases}. Failures:
    an asset-failure claim anywhere in the graded text (the wrong-answer lists excepted); "this implies more exposure to"
    while no cited literature sentence rests on a place-named impact group; a literature sentence citing an impact group
    that does not open with its scope phrase + " that", does not name the asset-class phrase, or (a cited impact group
    resting on a broader hazard term) does not name the broader-hazard phrase / (otherwise) a plain quantity phrase."""
    r8 = checks_input["rung8"]
    sc = checks_input.get("scope") or {}
    groups, strengths = sc.get("groups") or {}, checks_input.get("group_strength") or {}
    impact = set(r8.get("impact_group_ids") or [])
    place_named = set(r8.get("place_named_impact_group_ids") or [])
    rel = r8.get("group_hazard_relation") or {}
    asset = (r8.get("asset_class_phrase") or "").lower()
    broader = (r8.get("broader_hazard_phrase") or "").lower()
    quantity = [q.lower() for q in r8.get("quantity_phrases") or [] if q]
    hop_ids = set(r8.get("two_hop_group_ids") or []) if two_hop else set()      # v3.4 (D-073c)
    bridge = (r8.get("bridge_clause") or "") if two_hop else ""
    out, cited_place_named, cited_hop = [], False, []
    for w, t in every:
        if w in RUNG8_WRONG_ANSWER_FIELDS:
            continue
        for m in ASSET_FAILURE_RE.finditer(t or ""):
            out.append(f"{w}: rung 8 asset-failure claim (D-075): {m.group(0)!r}")
    for i, s in enumerate(lit_s):
        ids = [g for g in (s.get("group_ids") if isinstance(s.get("group_ids"), list) else []) if isinstance(g, str)]
        cited_impact = [g for g in ids if g in impact]
        if not cited_impact:
            continue
        cited_place_named |= any(g in place_named for g in cited_impact)
        text = s["sentence"].strip()
        low = text.lower()
        opens = scope_openings(ids, groups, strengths)
        if opens and not any(text.startswith(o + " that ") for o in opens):
            out.append(f"literature_interpretation[{i}]: rung 8 impact sentence (D-075): must begin with "
                       + " or ".join(repr(o + " that") for o in opens))
        if asset and asset not in low:
            out.append(f"literature_interpretation[{i}]: rung 8 impact sentence (D-075): must name the asset class {asset!r}")
        direct = [g for g in cited_impact if g not in hop_ids]
        hop = [g for g in cited_impact if g in hop_ids]
        if not direct:
            pass                                                     # v3.4: a two-hop sentence takes the D-073c wording instead
        elif any(rel.get(g) == "broader_hazard" for g in direct):
            if broader and broader not in low:
                out.append(f"literature_interpretation[{i}]: rung 8 impact sentence (D-075): must name the broader hazard {broader!r}")
        elif quantity and not any(q in low for q in quantity):
            out.append(f"literature_interpretation[{i}]: rung 8 impact sentence (D-075): must name the hazard {quantity[0]!r}")
        if hop:
            cited_hop += [g for g in hop if g not in cited_hop]
            if not TWO_HOP_RE.search(text):
                out.append(f"literature_interpretation[{i}]: two-hop wording (D-073c): a sentence citing a two-hop group must say "
                           "'when wildfires occur', 'wildfires can' or 'raise the chance of ignition'")
    for w, t in every:
        if w in RUNG8_WRONG_ANSWER_FIELDS:
            continue
        if IMPLIES_EXPOSURE_RE.search(t or "") and not cited_place_named:
            out.append(f"{w}: rung 8 place exposure (D-075): 'this implies more exposure to' needs a cited place-named impact group")
    rep = {"cited_place_named_impact_group": cited_place_named, "impact_group_ids": sorted(impact)}
    if two_hop:
        n = bridge_count(integrated, bridge)
        if cited_hop and bridge and n != 1:
            out.append(f"integrated: bridge clause (D-073c): must contain {bridge!r} exactly once (found {n})")
        rep.update({"cited_two_hop_group_ids": cited_hop, "bridge_clause_count": n})
    return out, rep


def opening_trigram(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9'-]+", (text or "").lower())[:3])


def opening_trigram_report(prompts: list[str], max_share: float = 0.30) -> dict:
    """P5a diversity report (not a failure): the share of the batch per opening trigram; `pass` when none exceeds
    `max_share`."""
    from collections import Counter

    c = Counter(opening_trigram(p) for p in prompts)
    n = len(prompts)
    top = c.most_common()
    worst = top[0][1] / n if n else 0.0
    return {"rule": "opening_trigram", "max_share": max_share, "n": n, "pass": worst <= max_share,
            "largest_share": round(worst, 3), "trigrams": [{"trigram": t, "n": k, "share": round(k / n, 3)} for t, k in top]}


# --- format-class failures (D-055b; litsynth_agent v3.2 corrective turn) ---------------------------------

_WORD_VALUES = {w: i for i, w in enumerate(_ONES.split("|"), 1)} | {w: i for i, w in enumerate(_TEENS.split("|"), 10)} | \
               {w: 10 * i for i, w in enumerate(_TENS.split("|"), 2)} | {"hundred": 100, "thousand": 1000, "twice": 2}
_GENERALITY_REASON_RE = re.compile(r"^[^:]+: generality \(D-060/D-062\): (.+) in graded text$")
_FORMAT_NUMBER_RE = re.compile(r"^[^:]+: number (\S+) does not trace to a pattern value or allowed descriptor in the packet$")
_FORMAT_REASON_RES = (re.compile(r"^[^:]+: number-word '.*' does not trace to an allowed descriptor in the packet$"),
                      re.compile(r"^[^:]+: exact_value_in_graded_text \S+ \(exact values belong to provenance\)$"),
                      re.compile(r"^literature_interpretation\[\d+\]: rests only on single-source groups but "
                                 r"(?:is not marked hedged|carries no hedge word)$"),
                      re.compile(r"^[^:]+: generality \(D-060/D-062\): .+ in graded text$"),   # v3 only emits it
                      # v3.1 only emits these (D-066, D-067)
                      re.compile(r"^literature_interpretation\[\d+\]: context_as_driver \(D-067\): .+$"),
                      re.compile(r"^[^:]+: tercile wording \(DR-DESC-1 v4\): .+ in graded text$"),
                      re.compile(r"^[^:]+: doubled magnitude phrase \(DR-DESC-1 v4\): .+$"),
                      re.compile(r"^[^:]+: sentence starts with a lower-case letter: .+$"),
                      # v3.2 only emits these (D-069; question forms)
                      re.compile(r"^literature_interpretation\[\d+\]: scope phrase \(D-069\): .+$"),
                      re.compile(r"^(?:literature_interpretation|integrated): closing clause \(D-069\) .+$"),
                      re.compile(r"^integrated: scope phrase \(D-069\): .+$"),
                      re.compile(r"^rubric\.required_points: place-specific mechanism required \(D-069\): .+$"),
                      re.compile(r"^prompt: question form QF-\d+ .+$"),
                      # v3.3 only emits these (D-075, rung 8)
                      re.compile(r"^[^:]+: rung 8 asset-failure claim \(D-075\): .+$"),
                      re.compile(r"^literature_interpretation\[\d+\]: rung 8 impact sentence \(D-075\): .+$"),
                      re.compile(r"^[^:]+: rung 8 place exposure \(D-075\): .+$"),
                      # v3.4 only emits these (D-073c, two-hop wording)
                      re.compile(r"^literature_interpretation\[\d+\]: two-hop wording \(D-073c\): .+$"),
                      re.compile(r"^integrated: bridge clause \(D-073c\): .+$"))


def number_word_value(word: str) -> float | None:
    """The value of a number-word NUMBER_WORD_RE matches ("forty-five" 45, "tripling" 3, "threefold" 3, "halved" 0.5);
    None for "several" / "many" fold."""
    w = word.lower().replace(" ", "-")
    if w.endswith("fold"):
        return number_word_value(w[:-4].rstrip("-"))
    if w.startswith("doubl"):
        return 2.0
    if w.startswith("tripl"):
        return 3.0
    if w.startswith("hal"):
        return 0.5
    w = re.sub(r"s$", "", w) if w in ("hundreds", "thousands") else w
    parts = w.split("-")
    if all(x in _WORD_VALUES for x in parts):
        return float(sum(_WORD_VALUES[x] for x in parts))
    return None


def descriptor_values(phrases: list[str]) -> set[float]:
    """Numeric values the allowed descriptors state, as digits or as number-words."""
    vals = {float(n) for ph in phrases for n in reference_numbers(ph)}
    vals |= {v for ph in phrases for m in NUMBER_WORD_RE.finditer(ph) if (v := number_word_value(m.group(0))) is not None}
    return vals


def format_class_only(reasons: list[str], allowed_descriptors: list[str]) -> bool:
    """D-055b: True when there is at least one reason and every reason is a format failure --- `exact_value_in_graded_text`,
    an untraced number-word, a missing hedge (flag or word), or an untraced number whose value an allowed descriptor
    states under another form (digits "16.0" for "about 16 days", "3" for "roughly tripling"); v3: a generality failure, and
    an untraced number a generality reason names. Anything else (leakage, an untraced fact or id, schema, consistency,
    parse) is not."""
    vals = descriptor_values(allowed_descriptors)
    # v3: an untraced number that a generality reason itself names (a year, a threshold such as '95 °F') is that wording
    # failure seen twice; generality reasons appear only under post-checks v3.
    general = {n for r in reasons if (g := _GENERALITY_REASON_RE.match(r)) for n in re.findall(r"\d+", g.group(1))}

    def fmt(r: str) -> bool:
        if any(x.match(r) for x in _FORMAT_REASON_RES):
            return True
        m = _FORMAT_NUMBER_RE.match(r)
        return bool(m) and (float(m.group(1)) in vals or m.group(1) in general)

    return bool(reasons) and all(fmt(r) for r in reasons)
