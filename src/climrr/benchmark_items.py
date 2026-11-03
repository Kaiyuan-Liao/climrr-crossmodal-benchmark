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


# --- synthesis post-checks (pilot P2b-prep; litsynth_agent.py) ---------------------------------

SYNTH_CHECK_VERSION = "synthesis_post_checks v2.2"
# v2.3 (mentor-export package, 2026-11-03): v2.2 plus `MODEL_SOURCE_RES` --- a reference text or prompt that cites the
# model, projection, data or table as its source ("The model shows ..."). Opt-in (`check_version=`): the default stays
# v2.2, which the frozen litsynth_agent v3.2 runs and runs 2 and 3 are reproduced with; v2.3 was a report-only re-run.
SYNTH_CHECK_VERSION_V23 = "synthesis_post_checks v2.3"
SYNTH_CHECK_VERSIONS = (SYNTH_CHECK_VERSION, SYNTH_CHECK_VERSION_V23)
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

    v2.3 (`check_version=SYNTH_CHECK_VERSION_V23`): also `model_source_flags` on the prompt and the reference texts."""
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
    for i, s in enumerate(lit_s):
        ids = s.get("group_ids") if isinstance(s.get("group_ids"), list) else []
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
    if check_version == SYNTH_CHECK_VERSION_V23:
        reasons += [f"{w} leakage: {f}" for w, t in [("prompt", item.get("prompt") or "")] + texts for f in model_source_flags(t)]

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
                       "n_table_sentences": len(tp_s), "n_literature_sentences": len(lit_s)}}


# --- format-class failures (D-055b; litsynth_agent v3.2 corrective turn) ---------------------------------

_WORD_VALUES = {w: i for i, w in enumerate(_ONES.split("|"), 1)} | {w: i for i, w in enumerate(_TEENS.split("|"), 10)} | \
               {w: 10 * i for i, w in enumerate(_TENS.split("|"), 2)} | {"hundred": 100, "thousand": 1000, "twice": 2}
_FORMAT_NUMBER_RE = re.compile(r"^[^:]+: number (\S+) does not trace to a pattern value or allowed descriptor in the packet$")
_FORMAT_REASON_RES = (re.compile(r"^[^:]+: number-word '.*' does not trace to an allowed descriptor in the packet$"),
                      re.compile(r"^[^:]+: exact_value_in_graded_text \S+ \(exact values belong to provenance\)$"),
                      re.compile(r"^literature_interpretation\[\d+\]: rests only on single-source groups but "
                                 r"(?:is not marked hedged|carries no hedge word)$"))


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
    states under another form (digits "16.0" for "about 16 days", "3" for "roughly tripling"). Anything else (leakage,
    an untraced fact or id, schema, consistency, parse) is not."""
    vals = descriptor_values(allowed_descriptors)

    def fmt(r: str) -> bool:
        if any(x.match(r) for x in _FORMAT_REASON_RES):
            return True
        m = _FORMAT_NUMBER_RE.match(r)
        return bool(m) and float(m.group(1)) in vals

    return bool(reasons) and all(fmt(r) for r in reasons)
