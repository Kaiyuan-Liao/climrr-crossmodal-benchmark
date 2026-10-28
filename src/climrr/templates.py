"""Track D v1 --- table-grounded question templates (D-031, D-033, D-034).

A template is a question string with `[SLOT]` markers, after the WildfireGPT
`QuestionTemplate` mechanism (docs/REFERENCES.md, D-032). The slot values are
the table-grounded vocabularies of `data/metadata/templates/slots_v1.yaml`, and
every `table_only` template is filled by **exhaustive enumeration**, never at
random. Each filled question's answer is computed here, deterministically, from
`data/raw/FullData.csv` after its manifest hash check --- never by a model.

The gate, in one place (`concept_block_reason`): a concept column is read for an
answer only if its status is `verified_from_dictionary` or `owner_confirmed`.
Anything weaker makes the question `blocked_inferred_columns`: its answer is
`None`, its retrieval terms are recorded but not authorized (D-033: no unverified
column, even as a query term), and its question text is not usable. A location
weaker than `verified` is computed and tagged provisional (owner decision
2026-10-28, D-034).

The arithmetic is the prototypes' (src/climrr/phenomenon.py): Decimal from the
raw strings, every derived value rounded to 15 places half-to-even, every mean
labelled with the M1-WP3b ruling's verbatim phrase. `audit=True` lets
`compute_statistic` read inferred-candidate columns for one purpose only ---
reproducing the frozen P-CELL-1 / P-COUNTY-1 values --- and its results never
enter a question record.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from decimal import Decimal, localcontext
from pathlib import Path

import yaml

from climrr.paths import REPO_ROOT
from climrr.phenomenon import (
    PRECISION,
    PROVISIONAL_AGGREGATION_LABEL,
    PROVISIONAL_AGGREGATION_LABEL_SOURCE,
    direction_of,
    dstr,
    mean_from_total,
    quantise_derived,
    to_decimal,
)

TEMPLATES_DIR = REPO_ROOT / "data" / "metadata" / "templates"
SLOTS_PATH = TEMPLATES_DIR / "slots_v1.yaml"
TEMPLATES_PATH = TEMPLATES_DIR / "templates_v1.yaml"
QA_TYPES_PATH = REPO_ROOT / "data" / "metadata" / "softqa" / "qa_types_v1.json"
COVERAGE_PATH = REPO_ROOT / "artifacts" / "profiles" / "dictionary_coverage.json"
DICTIONARY_TEXT_PATH = REPO_ROOT / "data" / "metadata" / "dictionary_extracted.txt"
CONCEPT_MAP_PATH = REPO_ROOT / "data" / "metadata" / "concept_map.yaml"
PROTOTYPES_DIR = REPO_ROOT / "artifacts" / "phenomena" / "prototypes"
OUT_DIR = REPO_ROOT / "artifacts" / "templates"
QUESTIONS_PATH = OUT_DIR / "questions_v1.jsonl"
SAMPLE_PATH = OUT_DIR / "questions_v1_sample.jsonl"
SUMMARY_PATH = OUT_DIR / "questions_v1_summary.json"
REPRODUCTION_PATH = OUT_DIR / "prototype_reproduction_v1.json"
DOC_PATH = REPO_ROOT / "docs" / "TEMPLATE_QUESTIONS_V1.md"

QUESTION_SCHEMA_VERSION = "td-questions-v1"
ENCODING = "utf-8-sig"

AUTHORIZATIONS = ("verified", "owner_confirmed", "inferred_candidate", "our_reading", "not_authorized")
#: Weakest last. A filled question's authorization is the weakest of its slots.
AUTHORIZATION_ORDER = {name: rank for rank, name in enumerate(AUTHORIZATIONS)}
COMPUTABLE_COLUMN_STATUSES = frozenset({"verified_from_dictionary", "owner_confirmed"})
#: What each column status allows a slot to claim, at most.
STATUS_MAX_AUTHORIZATION = {
    "verified_from_dictionary": "verified",
    "owner_confirmed": "owner_confirmed",
    "inferred_candidate": "inferred_candidate",
}

COMPUTED = "computed"
NOT_COMPUTABLE = "not_computable"
BLOCKED = "blocked_inferred_columns"
ANSWER_STATUSES = (COMPUTED, NOT_COMPUTABLE, BLOCKED)

MARKER_RE = re.compile(r"\[([A-Z][A-Z0-9_]*)\]")
CELL_LABEL_RE = re.compile(r"^R\d+C\d+$")
TEMPLATE_COUNT_RANGE = (15, 20)

CROSSMODEL_INDEX, NAME_INDEX, STATE_INDEX = 1, 2, 3

#: The single-statistic template whose record a comparison cites for its parts.
STATISTIC_TEMPLATE = {"direction": "TD-T01", "absolute_change": "TD-T02", "percent_change": "TD-T03"}

#: Words RT-1 never lets into a query.
FORBIDDEN_RETRIEVAL_WORDS = ("wildfire", "95 f", "105 f", "115 f", "125 f", "summer", "percent", "change")


class TemplateError(RuntimeError):
    """A slot, template or answer cannot be built from what was supplied. Never patched."""


# --- loading -----------------------------------------------------------------


def load_yaml(path: Path | str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def file_sha256(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_coverage(path: Path | str = COVERAGE_PATH) -> dict[int, dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {record["index"]: record for record in data["columns"]}


def load_qa_types(path: Path | str = QA_TYPES_PATH) -> set[str]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {entry["qa_type"] for entry in data["qa_types"]}


# --- slot values -------------------------------------------------------------


def slot_values(slots: dict) -> list[tuple[str, dict]]:
    """Every slot value in the file, with where it sits. A test requires each to
    carry a `source` and an `authorization`."""
    out: list[tuple[str, dict]] = []

    def add(where: str, node: dict) -> None:
        out.append((where, node))

    for family in slots["concept"]["governed"]:
        fid = family["id"]
        add(f"concept.{fid}", family)
        for i, term in enumerate(family["surface_forms"]):
            add(f"concept.{fid}.surface_forms[{i}]", term)
        for metric in family["metrics"]:
            mid = metric["metric_id"]
            add(f"concept.{fid}.{mid}", metric)
            for period, col in metric["period_columns"].items():
                add(f"concept.{fid}.{mid}.period_columns.{period}", col)
            for pair, col in (metric.get("change_columns") or {}).items():
                add(f"concept.{fid}.{mid}.change_columns.{pair}", col)
            for i, col in enumerate(metric.get("verified_columns_not_used") or []):
                add(f"concept.{fid}.{mid}.verified_columns_not_used[{i}]", col)
        for key in ("seasons_excluded", "metrics_excluded"):
            for i, entry in enumerate(family.get(key) or []):
                add(f"concept.{fid}.{key}[{i}]", entry)
    for i, entry in enumerate(slots["concept"]["ungoverned"]):
        add(f"concept.ungoverned[{i}]", entry)
    for level, block in slots["location"].items():
        add(f"location.{level}", block)
        for i, value in enumerate(block["values"]):
            add(f"location.{level}.values[{i}]", value)
        for i, value in enumerate(block.get("excluded") or []):
            add(f"location.{level}.excluded[{i}]", value)
    for key in ("period", "scenario", "season", "statistic"):
        for entry in slots[key]:
            add(f"{key}.{entry['id']}", entry)
    return out


def _column_entries(slots: dict) -> list[tuple[str, dict]]:
    """Slot values that name exactly one table column (`index` + `column`)."""
    return [(w, n) for w, n in slot_values(slots) if "index" in n and "column" in n]


def _normalise(text: str) -> str:
    return " ".join(text.split())


def validate_slots(
    slots: dict,
    *,
    dictionary_lines: list[str],
    coverage: dict[int, dict],
    concept_map: dict,
) -> None:
    """Raise unless every slot value is sourced, authorized and consistent with
    the dictionary text, the coverage statuses and the concept map."""
    problems: list[str] = []
    for where, node in slot_values(slots):
        source = node.get("source")
        auth = node.get("authorization")
        if not source:
            problems.append(f"{where}: no source")
        if auth not in AUTHORIZATIONS:
            problems.append(f"{where}: authorization {auth!r} not in {AUTHORIZATIONS}")
        if isinstance(source, dict) and source.get("kind") == "dictionary_line" or (
            isinstance(source, dict) and "line" in source and "quote" in source
        ):
            line_no = source["line"]
            if not 1 <= line_no <= len(dictionary_lines):
                problems.append(f"{where}: dictionary line {line_no} out of range")
            elif _normalise(source["quote"]) not in _normalise(dictionary_lines[line_no - 1]):
                problems.append(f"{where}: quote not on dictionary line {line_no}")
    for where, node in _column_entries(slots):
        record = coverage.get(node["index"])
        if record is None or record["column"] != node["column"]:
            problems.append(f"{where}: column {node['index']} is not {node['column']!r} in the coverage report")
            continue
        if node.get("status") != record["status"]:
            problems.append(f"{where}: status {node.get('status')!r} != coverage {record['status']!r}")
        ceiling = STATUS_MAX_AUTHORIZATION.get(record["status"], "not_authorized")
        if AUTHORIZATION_ORDER[node["authorization"]] < AUTHORIZATION_ORDER[ceiling]:
            problems.append(f"{where}: authorization {node['authorization']!r} stronger than status {record['status']!r}")
    entries = {entry["canonical_id"]: entry for entry in concept_map["entries"]}
    for family in slots["concept"]["governed"]:
        entry = entries.get(family["id"])
        if entry is None or entry["status"] != "approved_lexical" or entry["level"] != "family":
            problems.append(f"concept.{family['id']}: not an approved_lexical family in the concept map")
            continue
        allowed = set(entry["accepted_surface_terms"]) | {
            t["term"] for t in entry.get("additional_surface_terms") or [] if "retrieval" in t["usage"]
        }
        for term in family["surface_forms"]:
            if term["term"] not in allowed:
                problems.append(f"concept.{family['id']}: surface form {term['term']!r} not in the concept map")
        for metric in family["metrics"]:
            statuses = {c["status"] for c in metric["period_columns"].values()}
            weakest = "verified" if statuses <= COMPUTABLE_COLUMN_STATUSES else "inferred_candidate"
            if metric["authorization"] != weakest:
                problems.append(f"concept.{family['id']}.{metric['metric_id']}: authorization should be {weakest!r}")
    for level, block in slots["location"].items():
        for value in block["values"]:
            if level == "cell" and not CELL_LABEL_RE.match(value["label"]):
                problems.append(f"location.cell: {value['label']!r} is not R<row>C<col>")
    if problems:
        raise TemplateError("slots_v1 invalid:\n  " + "\n  ".join(problems))


def validate_templates(templates: dict, slots: dict, qa_types: set[str]) -> None:
    problems: list[str] = []
    items = templates["templates"]
    low, high = TEMPLATE_COUNT_RANGE
    if not low <= len(items) <= high:
        problems.append(f"{len(items)} templates; expected {low}-{high}")
    ids = [t["template_id"] for t in items]
    if len(set(ids)) != len(ids):
        problems.append("duplicate template_id")
    statistic_ids = {s["id"] for s in slots["statistic"]}
    for t in items:
        tid = t["template_id"]
        markers = set(MARKER_RE.findall(t["text"]))
        if not markers <= set(templates["markers"]):
            problems.append(f"{tid}: unknown markers {sorted(markers - set(templates['markers']))}")
        if markers != set(t["required_slots"]):
            problems.append(f"{tid}: required_slots {sorted(t['required_slots'])} != markers {sorted(markers)}")
        if t["category_type"] not in templates["category_types"]:
            problems.append(f"{tid}: category_type {t['category_type']!r}")
        if t["research_method"] not in templates["research_methods"]:
            problems.append(f"{tid}: research_method {t['research_method']!r}")
        if t["answer_mode"] not in templates["answer_modes"]:
            problems.append(f"{tid}: answer_mode {t['answer_mode']!r}")
        if t["qa_type"] not in qa_types:
            problems.append(f"{tid}: qa_type {t['qa_type']!r} not in qa_types_v1")
        if t["answerable_now"] != (t["answer_mode"] == "table_only"):
            problems.append(f"{tid}: answerable_now must be true exactly for table_only")
        if t["answer_mode"] != "table_only" and not t.get("needs"):
            problems.append(f"{tid}: a non-table_only template must say what it needs")
        for stat in t.get("statistics") or [t.get("statistic")]:
            if stat not in statistic_ids:
                problems.append(f"{tid}: statistic {stat!r} not in slots_v1")
        rule = t["retrieval_terms_rule"]
        if rule["rule"] != templates["retrieval_terms_rule_id"]:
            problems.append(f"{tid}: retrieval rule {rule['rule']!r}")
        if not set(rule["slots"]) <= markers:
            problems.append(f"{tid}: retrieval slots not all in the template")
        if "CONCEPT" not in rule["slots"]:
            problems.append(f"{tid}: RT-1 always takes the concept surface forms")
    if problems:
        raise TemplateError("templates_v1 invalid:\n  " + "\n  ".join(problems))


# --- the vocabularies as objects ---------------------------------------------


def governed_metrics(slots: dict) -> list[dict]:
    """Every (family, metric) a [CONCEPT] slot can take, in file order."""
    out = []
    for family in slots["concept"]["governed"]:
        for metric in family["metrics"]:
            out.append({"family": family, "metric": metric})
    return out


def by_id(entries: list[dict]) -> dict[str, dict]:
    return {entry["id"]: entry for entry in entries}


def location_values(slots: dict, level: str) -> list[dict]:
    block = slots["location"][level]
    out = []
    for value in block["values"]:
        if level == "state" and value["n_cells"] < block["min_cells"]:
            continue
        out.append({"level": level, "block": block, **value})
    if level == "state":
        out.sort(key=lambda v: v["label"])
    return out


def location_key(location: dict) -> tuple[str, str]:
    return (location["level"], location["label"])


def location_text(location: dict) -> str:
    return location.get("wording") or location["label"]


def concept_block_reason(metric: dict, period_ids: list[str]) -> str | None:
    """Why this metric's columns may not be read for an answer, or None."""
    weak = []
    for period in period_ids:
        col = metric["period_columns"].get(period)
        if col is not None and col["status"] not in COMPUTABLE_COLUMN_STATUSES:
            weak.append(col)
    for pair, col in (metric.get("change_columns") or {}).items():
        a, b = pair.split("->")
        if a in period_ids and b in period_ids and col["status"] not in COMPUTABLE_COLUMN_STATUSES:
            weak.append(col)
    if not weak:
        return None
    named = ", ".join(f"{c['index']} {c['column']} ({c['source'].get('id', c['status'])})" for c in weak)
    return f"concept columns are not verified or owner-confirmed: {named}"


# --- the table scan ----------------------------------------------------------


def _change_column(metric: dict, period_from: str, period_to: str) -> dict | None:
    return (metric.get("change_columns") or {}).get(f"{period_from}->{period_to}")


def scan_table(path: Path | str, slots: dict, period_pairs: list[list[str]]) -> dict:
    """One pass over the table: per location, per metric, the sums the
    statistics need. Read as text; nothing coerced but the value columns, and
    those only through `to_decimal`, which raises on anything not a number."""
    metrics = governed_metrics(slots)
    cells = {v["label"] for v in slots["location"]["cell"]["values"]}
    counties = {(v["state"], v["name"]) for v in slots["location"]["county"]["values"]}
    states = {v["label"] for v in slots["location"]["state"]["values"]}

    expected = {CROSSMODEL_INDEX: "Crossmodel", NAME_INDEX: "NAME", STATE_INDEX: "State"}
    for m in metrics:
        for col in list(m["metric"]["period_columns"].values()) + list((m["metric"].get("change_columns") or {}).values()):
            expected[col["index"]] = col["column"]

    single: dict = {}
    pair: dict = {}
    members: dict = {}
    n_rows = 0
    with Path(path).open("r", encoding=ENCODING, newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        for index, name in expected.items():
            if index >= len(header) or header[index] != name:
                raise TemplateError(f"table column {index} is {header[index] if index < len(header) else None!r}, not {name!r}")
        for row in reader:
            n_rows += 1
            keys = []
            if row[CROSSMODEL_INDEX] in cells:
                keys.append(("cell", row[CROSSMODEL_INDEX]))
            if (row[STATE_INDEX], row[NAME_INDEX]) in counties:
                keys.append(("county", f"{row[STATE_INDEX]}|{row[NAME_INDEX]}"))
            if row[STATE_INDEX] in states:
                keys.append(("state", row[STATE_INDEX]))
            if not keys:
                continue
            for key in keys:
                entry = members.setdefault(key, {"n_cells": 0, "sha": hashlib.sha256(), "cells": []})
                entry["n_cells"] += 1
                entry["sha"].update(row[CROSSMODEL_INDEX].encode("utf-8") + b"\n")
                if key[0] != "state":
                    entry["cells"].append(row[CROSSMODEL_INDEX])
            for m in metrics:
                metric = m["metric"]
                mid = metric["metric_id"]
                raw = {p: row[c["index"]] for p, c in metric["period_columns"].items()}
                for period, value in raw.items():
                    if value == "":
                        continue
                    number = to_decimal(value, index=metric["period_columns"][period]["index"])
                    for key in keys:
                        acc = single.setdefault((key, mid, period), [Decimal(0), 0, []])
                        acc[0] += number
                        acc[1] += 1
                        if key[0] != "state":
                            acc[2].append(value)
                for p_from, p_to in period_pairs:
                    if p_from not in raw or p_to not in raw or raw[p_from] == "" or raw[p_to] == "":
                        continue
                    change_col = _change_column(metric, p_from, p_to)
                    if change_col is not None:
                        if row[change_col["index"]] == "":
                            continue
                        change = quantise_derived(to_decimal(row[change_col["index"]], index=change_col["index"]))
                    else:
                        change = quantise_derived(
                            to_decimal(raw[p_to], index=metric["period_columns"][p_to]["index"])
                            - to_decimal(raw[p_from], index=metric["period_columns"][p_from]["index"])
                        )
                    v_from = to_decimal(raw[p_from], index=metric["period_columns"][p_from]["index"])
                    v_to = to_decimal(raw[p_to], index=metric["period_columns"][p_to]["index"])
                    for key in keys:
                        acc = pair.setdefault((key, mid, p_from, p_to), [Decimal(0), Decimal(0), Decimal(0), 0])
                        acc[0] += v_from
                        acc[1] += v_to
                        acc[2] += change
                        acc[3] += 1
    for entry in members.values():
        entry["cells_sha256"] = entry.pop("sha").hexdigest()
    return {"n_rows": n_rows, "single": single, "pair": pair, "members": members}


# --- statistics ----------------------------------------------------------------


def _label_block(level: str) -> dict:
    """The ruling's verbatim label beside every mean over a unit's cells --- at
    county and state level, whatever the number of cells used."""
    if level == "cell":
        return {}
    return {"aggregation_label": PROVISIONAL_AGGREGATION_LABEL,
            "aggregation_label_source": PROVISIONAL_AGGREGATION_LABEL_SOURCE}


def _columns_read(metric: dict, period_ids: list[str]) -> list[dict]:
    cols = [metric["period_columns"][p] for p in period_ids if p in metric["period_columns"]]
    if len(period_ids) == 2:
        change_col = _change_column(metric, *period_ids)
        if change_col is not None:
            cols.append(change_col)
    return [{"index": c["index"], "column": c["column"], "status": c["status"]} for c in cols]


def compute_statistic(
    scan: dict,
    location: dict,
    metric: dict,
    statistic: str,
    period_from: str | None,
    period_to: str | None,
    *,
    audit: bool = False,
) -> dict:
    """One statistic at one location. Returns {status, value, reason, derivation}.

    Refuses (status `blocked_inferred_columns`) when a concept column read is not
    verified or owner-confirmed --- unless `audit`, which only the prototype
    reproduction passes and whose result never enters a question record."""
    periods = [p for p in (period_from, period_to) if p is not None]
    reason = concept_block_reason(metric, periods)
    if reason is not None and not audit:
        return {"status": BLOCKED, "value": None, "reason": reason,
                "derivation": {"columns": _columns_read(metric, periods)}}
    key = location_key(location)
    member = scan["members"].get(key)
    if member is None:
        return {"status": NOT_COMPUTABLE, "value": None, "reason": "no_member_rows", "derivation": None}
    loc_block = {"level": location["level"], "label": location["label"], "n_cells": member["n_cells"],
                 "member_cells_sha256": member["cells_sha256"]}
    if location["level"] != "state":
        loc_block["member_cells"] = member["cells"]
    rule = {s: r for s, r in (("baseline_value", "DR-TD-001"), ("future_value", "DR-TD-002"),
                              ("absolute_change", "DR-TD-003"), ("percent_change", "DR-TD-004"),
                              ("direction", "DR-TD-005"))}[statistic]
    derivation = {"rule_id": rule, "location": loc_block, "columns": None, "raw_aggregates": None}

    if statistic in ("baseline_value", "future_value"):
        period = period_from if statistic == "baseline_value" else period_to
        derivation["columns"] = _columns_read(metric, [period])
        acc = scan["single"].get((key, metric["metric_id"], period))
        if acc is None or acc[1] == 0:
            return {"status": NOT_COMPUTABLE, "value": None, "reason": "no_cell_with_a_value", "derivation": derivation}
        mean = mean_from_total(acc[0], acc[1])
        derivation["raw_aggregates"] = {"n_cells_used": acc[1], "sum": dstr(acc[0]), "mean": dstr(mean), **_label_block(location["level"])}
        if location["level"] != "state":
            derivation["raw_aggregates"]["per_cell_raw_values"] = acc[2]
        return {"status": COMPUTED, "value": dstr(mean), "reason": None, "derivation": derivation}

    derivation["columns"] = _columns_read(metric, [period_from, period_to])
    acc = scan["pair"].get((key, metric["metric_id"], period_from, period_to))
    if acc is None or acc[3] == 0:
        return {"status": NOT_COMPUTABLE, "value": None, "reason": "no_cell_with_both_values", "derivation": derivation}
    sum_from, sum_to, sum_change, n = acc
    mean_from = mean_from_total(sum_from, n)
    mean_to = mean_from_total(sum_to, n)
    change = mean_from_total(sum_change, n)
    change_col = _change_column(metric, period_from, period_to)
    derivation["raw_aggregates"] = {
        "n_cells_used": n, "sum_from": dstr(sum_from), "sum_to": dstr(sum_to), "sum_change": dstr(sum_change),
        "mean_from": dstr(mean_from), "mean_to": dstr(mean_to), "mean_change": dstr(change),
        "change_operation": "change_column_value" if change_col is not None else "difference_of_horizon_values",
        **_label_block(location["level"]),
    }
    if statistic == "absolute_change":
        return {"status": COMPUTED, "value": dstr(change), "reason": None, "derivation": derivation}
    if statistic == "direction":
        derivation["change_value"] = dstr(change)
        return {"status": COMPUTED, "value": direction_of(change), "reason": None, "derivation": derivation}
    # percent_change, DR-TD-004
    if mean_from == 0:
        return {"status": NOT_COMPUTABLE, "value": None, "reason": "zero_baseline", "derivation": derivation}
    with localcontext() as ctx:
        ctx.prec = PRECISION
        percent = quantise_derived(Decimal(100) * change / mean_from)
    return {"status": COMPUTED, "value": dstr(percent), "reason": None, "derivation": derivation}


def compare_signed(a: str, b: str, label_a: str, label_b: str) -> str:
    """DR-TD-006: the label of the larger signed value, or `equal`."""
    da, db = Decimal(a), Decimal(b)
    if da > db:
        return label_a
    if db > da:
        return label_b
    return "equal"


# --- filling -------------------------------------------------------------------


def fill_text(text: str, fills: dict[str, dict]) -> str:
    def repl(match: re.Match) -> str:
        marker = match.group(1)
        if marker not in fills:
            raise TemplateError(f"no fill for [{marker}]")
        return fills[marker]["text"]

    out = MARKER_RE.sub(repl, text)
    if MARKER_RE.search(out):
        raise TemplateError(f"unfilled marker left in {out!r}")
    return out


def source_ref(source: dict) -> str:
    """A slot value's source as a short, resolvable reference (the full source
    sits in slots_v1.yaml under the value_id)."""
    kind = source["kind"]
    if kind == "dictionary_line":
        return f"dictionary_extracted.txt:L{source['line']}"
    if kind in ("inferred_candidate_record",):
        return source["id"]
    if kind == "inferred_candidate_records":
        return "+".join(source["ids"])
    if kind == "table_column_values":
        return f"FullData.csv:col{source['column_index']}"
    if kind == "prototype_record":
        return f"{source['record_id']}.{source['field']}"
    if kind == "derivation_rule":
        return source["rule_id"]
    if kind.startswith("concept_map"):
        return f"concept_map.yaml:{source['canonical_id']}"
    raise TemplateError(f"no short reference for source kind {kind!r}")


def _fill(value_id: str, text: str, authorization: str, source) -> dict:
    return {"value_id": value_id, "text": text, "authorization": authorization, "source_ref": source_ref(source)}


def concept_fill(entry: dict) -> dict:
    family, metric = entry["family"], entry["metric"]
    return _fill(f"{family['id']}:{metric['metric_id']}", metric["wording"], metric["authorization"], metric["source"])


def location_fill(location: dict) -> dict:
    return _fill(f"{location['level']}:{location['label']}", location_text(location),
                 location["authorization"], location["source"])


def plain_fill(entry: dict) -> dict:
    return _fill(entry["id"], entry["wording"], entry["authorization"], entry["source"])


def retrieval_terms(template: dict, fills: dict[str, dict], context: dict) -> list[str]:
    """RT-1. `context` maps markers to the slot objects behind the fills."""
    terms: list[str] = []

    def add(term: str) -> None:
        if term not in terms:
            terms.append(term)

    for marker in template["retrieval_terms_rule"]["slots"]:
        obj = context[marker]
        if marker.startswith("CONCEPT"):
            for t in obj["family"]["surface_forms"]:
                add(t["term"])
        elif marker.startswith("LOCATION"):
            if obj["level"] == "state":
                add(obj["label"])
            elif obj["level"] == "county":
                add(obj["state"])
        elif marker.startswith(("SCENARIO", "PERIOD")):
            for t in obj.get("retrieval_terms") or []:
                add(t)
    for term in terms:
        low = term.lower()
        if any(word in low for word in FORBIDDEN_RETRIEVAL_WORDS):
            raise TemplateError(f"RT-1 forbids the query term {term!r}")
    return terms


def weakest_authorization(fills: dict[str, dict]) -> str:
    return max((f["authorization"] for f in fills.values()), key=lambda a: AUTHORIZATION_ORDER[a])


# --- enumeration ---------------------------------------------------------------


class _Builder:
    def __init__(self, slots: dict, templates: dict, scan: dict, table_sha256: str):
        self.slots = slots
        self.templates = templates
        self.scan = scan
        self.table_sha256 = table_sha256
        self.periods = by_id(slots["period"])
        self.scenarios = by_id(slots["scenario"])
        self.seasons = by_id(slots["season"])
        self.statistics = by_id(slots["statistic"])
        self.metrics = governed_metrics(slots)
        self.pairs = [tuple(p) for p in templates["period_pairs"]]
        self.records: list[dict] = []
        self.counters: dict[str, int] = {}
        #: (template_id, metric_id, location key, from, to) -> question_id, for the
        #: single-statistic templates whose derivations comparisons cite.
        self.index: dict[tuple, str] = {}

    # -- helpers
    def _locations(self, kinds: list[str]) -> list[dict]:
        out = []
        for kind in kinds:
            out.extend(location_values(self.slots, kind))
        return out

    def _next_id(self, template_id: str) -> str:
        n = self.counters.get(template_id, 0) + 1
        self.counters[template_id] = n
        return f"TD1-{template_id.split('-')[1]}-{n:05d}"

    def _scenario_reason(self, family: dict, scenario_ids: list[str]) -> str | None:
        for sid in scenario_ids:
            if not self.scenarios[sid]["realized_by"].get(family["id"]):
                return f"no_column_realizes_scenario: {sid} for {family['id']}"
        return None

    def _provisional(self, locations: list[dict], aggregated: bool) -> list[str]:
        reasons = []
        for loc in locations:
            if loc["authorization"] != "verified":
                reason = f"location_{loc['authorization']}:{loc['level']} ({', '.join(loc['block']['assumptions'])}; D-034)"
                if reason not in reasons:
                    reasons.append(reason)
        if aggregated:
            reasons.append(f"unweighted_mean: {PROVISIONAL_AGGREGATION_LABEL}")
        return reasons

    def _emit(self, template: dict, fills: dict, context: dict, answer: dict, *,
              locations: list[dict], metrics: list[dict], statistic: str) -> None:
        status = answer["status"]
        terms = retrieval_terms(template, fills, context)
        blocked = status == BLOCKED
        aggregated = any(loc["level"] != "cell" for loc in locations) or not locations
        record = {
            "schema_version": QUESTION_SCHEMA_VERSION,
            "question_id": self._next_id(template["template_id"]),
            "template_id": template["template_id"],
            "category_type": template["category_type"],
            "research_method": template["research_method"],
            "qa_type": template["qa_type"],
            "answer_mode": template["answer_mode"],
            "slots": {marker: fills[marker] for marker in template["required_slots"]},
            "weakest_slot_authorization": weakest_authorization(fills),
            "question_text": fill_text(template["text"], fills),
            "retrieval_terms": terms,
            "retrieval_authorized": not blocked,
            "usable_for": [] if blocked else (["question_wording", "retrieval", "answer"] if status == COMPUTED
                                              else ["question_wording", "retrieval"]),
            "answer_status": status,
            "answer": answer.get("value") if status == COMPUTED else None,
            "answer_unit": answer.get("unit"),
            "answer_reason": answer.get("reason"),
            "answer_derivation": answer.get("derivation"),
            "statistic": statistic,
            "provisional": status == COMPUTED and bool(self._provisional(locations, aggregated)),
            "provisional_reasons": self._provisional(locations, aggregated) if status == COMPUTED else [],
            "assumptions": sorted({a for loc in locations for a in loc["block"]["assumptions"]}
                                  | set(self.statistics[statistic]["assumptions"])),
            "cautions": sorted({"C-fire_weather" for m in metrics if m["family"]["id"] == "fire_weather_index"}
                               | {"C-historical" for p in fills if p.startswith("PERIOD") and fills[p]["value_id"] == "historical"}),
            "table_data_sha256": self.table_sha256,
        }
        if blocked:
            record["blocked_until"] = "owner confirmation of the concept columns (docs/MENTOR_BRIEF.md, item 0; D-033 addendum)"
        self.records.append(record)

    def _single(self, template, metric_entry, location, statistic, p_from, p_to, scenario_ids):
        metric, family = metric_entry["metric"], metric_entry["family"]
        answer = compute_statistic(self.scan, location, metric, statistic, p_from, p_to)
        if answer["status"] != BLOCKED:
            reason = self._scenario_reason(family, scenario_ids)
            if reason is not None:
                answer = {"status": NOT_COMPUTABLE, "value": None, "reason": reason, "derivation": None}
        if answer["status"] == COMPUTED and statistic != "direction":
            answer["unit"] = metric["unit"] if statistic != "percent_change" else "percent"
        answer["ref"] = self.index.get((STATISTIC_TEMPLATE.get(statistic), metric["metric_id"],
                                        location_key(location), p_from, p_to))
        return answer

    def _fills(self, template, metric_entry, location=None, p_from=None, p_to=None, scenario=None, statistic=None,
               extra=None):
        fills, ctx = {}, {}
        markers = set(template["required_slots"])
        if "CONCEPT" in markers:
            fills["CONCEPT"], ctx["CONCEPT"] = concept_fill(metric_entry), metric_entry
        if "SEASON" in markers:
            season = self.seasons[metric_entry["metric"]["season"]]
            fills["SEASON"], ctx["SEASON"] = plain_fill(season), season
        if "LOCATION" in markers:
            fills["LOCATION"], ctx["LOCATION"] = location_fill(location), location
        if "PERIOD_FROM" in markers:
            fills["PERIOD_FROM"], ctx["PERIOD_FROM"] = plain_fill(self.periods[p_from]), self.periods[p_from]
        if "PERIOD_TO" in markers:
            fills["PERIOD_TO"], ctx["PERIOD_TO"] = plain_fill(self.periods[p_to]), self.periods[p_to]
        if "SCENARIO" in markers:
            fills["SCENARIO"], ctx["SCENARIO"] = plain_fill(self.scenarios[scenario]), self.scenarios[scenario]
        if "STATISTIC" in markers:
            fills["STATISTIC"], ctx["STATISTIC"] = plain_fill(self.statistics[statistic]), self.statistics[statistic]
        for marker, (fill, obj) in (extra or {}).items():
            fills[marker], ctx[marker] = fill, obj
        return fills, ctx

    # -- per template shape
    def build(self) -> list[dict]:
        for template in self.templates["templates"]:
            if template["answer_mode"] != "table_only":
                continue
            getattr(self, "_t_" + template["template_id"].split("-")[1].lower())(template)
        return self.records

    def _pairs_of(self, template):
        spec = template["enumeration"].get("period_pairs", "all")
        return self.pairs if spec == "all" else [tuple(p) for p in spec]

    def _per_location(self, template):
        stat = template["statistic"]
        enum = template["enumeration"]
        for m in self.metrics:
            for loc in self._locations(enum["locations"]):
                if "periods_from" in enum:
                    combos = [(p, None) for p in enum["periods_from"]]
                elif "periods_to" in enum:
                    combos = [(None, p) for p in enum["periods_to"]]
                else:
                    combos = self._pairs_of(template)
                for p_from, p_to in combos:
                    for scen in enum["scenarios"] or [None]:
                        answer = self._single(template, m, loc, stat, p_from, p_to, [scen] if scen else [])
                        fills, ctx = self._fills(template, m, loc, p_from, p_to, scen, stat)
                        self._emit(template, fills, ctx, answer, locations=[loc], metrics=[m], statistic=stat)
                        self.index[(template["template_id"], m["metric"]["metric_id"], location_key(loc),
                                    p_from, p_to)] = self.records[-1]["question_id"]

    _t_t01 = _t_t02 = _t_t03 = _t_t04 = _t_t05 = _per_location

    def _t_t06(self, template):
        stat = template["statistic"]
        enum = template["enumeration"]
        for m in self.metrics:
            for loc in self._locations(enum["locations"]):
                for p_from, p_to in self._pairs_of(template):
                    for s1, s2 in enum["scenario_pairs"]:
                        a = self._single(template, m, loc, stat, p_from, p_to, [s1, s2])
                        if a["status"] == COMPUTED:  # unreachable in v1; kept honest
                            raise TemplateError("TD-T06 computed with no RCP4.5 column")
                        extra = {"SCENARIO_2": (plain_fill(self.scenarios[s2]), self.scenarios[s2])}
                        fills, ctx = self._fills(template, m, loc, p_from, p_to, s1, stat, extra)
                        self._emit(template, fills, ctx, a, locations=[loc], metrics=[m], statistic=stat)

    def _t_t07(self, template):
        stat = template["statistic"]
        enum = template["enumeration"]
        states = location_values(self.slots, "state")
        anchor = next(s for s in states if s["label"] == enum["anchor_state"])
        for m in self.metrics:
            for other in states:
                if other["label"] == anchor["label"]:
                    continue
                for p_from, p_to in self._pairs_of(template):
                    for scen in enum["scenarios"]:
                        a = self._single(template, m, anchor, stat, p_from, p_to, [scen])
                        b = self._single(template, m, other, stat, p_from, p_to, [scen])
                        answer = self._combine(a, b, anchor["label"], other["label"], "DR-TD-006")
                        extra = {"LOCATION_2": (location_fill(other), other)}
                        fills, ctx = self._fills(template, m, anchor, p_from, p_to, scen, stat, extra)
                        self._emit(template, fills, ctx, answer, locations=[anchor, other], metrics=[m], statistic=stat)

    def _t_t08(self, template):
        stat = template["statistic"]
        enum = template["enumeration"]
        for m in self.metrics:
            for loc in self._locations(enum["locations"]):
                for p_from, p_to, p_to_2 in enum["period_triples"]:
                    for scen in enum["scenarios"]:
                        a = self._single(template, m, loc, stat, p_from, p_to, [scen])
                        b = self._single(template, m, loc, stat, p_from, p_to_2, [scen])
                        answer = self._combine(a, b, p_to, p_to_2, "DR-TD-006")
                        extra = {"PERIOD_TO_2": (plain_fill(self.periods[p_to_2]), self.periods[p_to_2])}
                        fills, ctx = self._fills(template, m, loc, p_from, p_to, scen, stat, extra)
                        self._emit(template, fills, ctx, answer, locations=[loc], metrics=[m], statistic=stat)

    def _t_t09(self, template):
        stat = template["statistic"]
        enum = template["enumeration"]
        for fam_1, fam_2 in enum["concept_pairs"]:
            firsts = [m for m in self.metrics if m["family"]["id"] == fam_1]
            seconds = [m for m in self.metrics if m["family"]["id"] == fam_2]
            for m1 in firsts:
                for m2 in seconds:
                    if m1["metric"]["season"] != m2["metric"]["season"]:
                        continue
                    for loc in self._locations(enum["locations"]):
                        for p_from, p_to in self._pairs_of(template):
                            for scen in enum["scenarios"]:
                                a = self._single(template, m1, loc, stat, p_from, p_to, [scen])
                                b = self._single(template, m2, loc, stat, p_from, p_to, [scen])
                                answer = self._both_increase(a, b)
                                extra = {"CONCEPT_2": (concept_fill(m2), m2)}
                                fills, ctx = self._fills(template, m1, loc, p_from, p_to, scen, stat, extra)
                                self._emit(template, fills, ctx, answer, locations=[loc], metrics=[m1, m2], statistic=stat)

    def _extremum(self, template):
        enum = template["enumeration"]
        states = location_values(self.slots, "state")
        for m in self.metrics:
            for stat in template["statistics"]:
                for p_from, p_to in self._pairs_of(template):
                    for scen in enum["scenarios"]:
                        results = {s["label"]: self._single(template, m, s, stat, p_from, p_to, [scen]) for s in states}
                        answer = self._rank(results, template["extremum"])
                        fills, ctx = self._fills(template, m, None, p_from, p_to, scen, stat)
                        self._emit(template, fills, ctx, answer, locations=states, metrics=[m], statistic=stat)

    _t_t10 = _t_t11 = _extremum

    # -- combining
    @staticmethod
    def _gate(*answers: dict) -> dict | None:
        for status in (BLOCKED, NOT_COMPUTABLE):
            for a in answers:
                if a["status"] == status:
                    return {"status": status, "value": None, "reason": a["reason"],
                            "derivation": {"parts": [_part(x) for x in answers]}}
        return None

    def _combine(self, a: dict, b: dict, label_a: str, label_b: str, rule: str) -> dict:
        gated = self._gate(a, b)
        if gated is not None:
            return gated
        return {"status": COMPUTED, "value": compare_signed(a["value"], b["value"], label_a, label_b),
                "reason": None, "unit": None,
                "derivation": {"rule_id": rule, "compared": {label_a: a["value"], label_b: b["value"]},
                               "parts": [_part(a), _part(b)]}}

    def _both_increase(self, a: dict, b: dict) -> dict:
        gated = self._gate(a, b)
        if gated is not None:
            return gated
        both = a["value"] == "increase" and b["value"] == "increase"
        return {"status": COMPUTED, "value": "yes" if both else "no", "reason": None, "unit": None,
                "derivation": {"rule_id": "DR-TD-005", "directions": [a["value"], b["value"]],
                               "parts": [_part(a), _part(b)]}}

    def _rank(self, results: dict[str, dict], which: str) -> dict:
        blocked = [r for r in results.values() if r["status"] == BLOCKED]
        if blocked:
            return {"status": BLOCKED, "value": None, "reason": blocked[0]["reason"],
                    "derivation": {"rule_id": "DR-TD-007", "columns": blocked[0]["derivation"]["columns"]}}
        ranked = {label: r["value"] for label, r in results.items() if r["status"] == COMPUTED}
        excluded = {label: r["reason"] for label, r in results.items() if r["status"] != COMPUTED}
        if not ranked:
            return {"status": NOT_COMPUTABLE, "value": None, "reason": "no_state_computable",
                    "derivation": {"rule_id": "DR-TD-007", "excluded": excluded}}
        pick = max if which == "largest" else min
        best = pick(Decimal(v) for v in ranked.values())
        winners = sorted(label for label, v in ranked.items() if Decimal(v) == best)
        return {"status": COMPUTED, "value": winners, "reason": None, "unit": None,
                "derivation": {"rule_id": "DR-TD-007", "extremum": which, "statistic_value": dstr(best),
                               "tie": len(winners) > 1, "n_ranked": len(ranked),
                               "n_excluded_not_computable": len(excluded), "excluded": excluded,
                               "ranked_values": dict(sorted(ranked.items())),
                               "aggregation_label": PROVISIONAL_AGGREGATION_LABEL}}


def _part(answer: dict):
    """A comparison's part: the question_id whose record carries this
    derivation, or the derivation itself when no such record exists."""
    if answer.get("ref"):
        return {"question_id": answer["ref"], "status": answer["status"], "value": answer["value"]}
    return answer["derivation"]


def build_questions(slots: dict, templates: dict, scan: dict, table_sha256: str) -> list[dict]:
    return _Builder(slots, templates, scan, table_sha256).build()


def summarise(records: list[dict], templates: dict) -> dict:
    def count(key_fn) -> dict:
        out: dict = {}
        for r in records:
            k = key_fn(r)
            if k is not None:
                out[k] = out.get(k, 0) + 1
        return dict(sorted(out.items()))

    def family(r):
        return "+".join(sorted({s["value_id"].split(":")[0] for m, s in r["slots"].items() if m.startswith("CONCEPT")}))

    def level(r):
        locs = [s["value_id"].split(":")[0] for m, s in r["slots"].items() if m.startswith("LOCATION")]
        return "+".join(sorted(set(locs))) if locs else "all_states"

    items = templates["templates"]
    return {
        "schema_version": QUESTION_SCHEMA_VERSION,
        "n_templates": len(items),
        "n_templates_table_only": sum(t["answer_mode"] == "table_only" for t in items),
        "n_templates_need_passage": sum(t["answer_mode"] != "table_only" for t in items),
        "n_questions": len(records),
        "by_answer_status": {s: sum(r["answer_status"] == s for r in records) for s in ANSWER_STATUSES},
        "by_template": count(lambda r: r["template_id"]),
        "by_template_and_status": count(lambda r: f"{r['template_id']}|{r['answer_status']}"),
        "by_concept_family": count(family),
        "by_concept_family_and_status": count(lambda r: f"{family(r)}|{r['answer_status']}"),
        "by_location_level": count(level),
        "by_location_level_and_status": count(lambda r: f"{level(r)}|{r['answer_status']}"),
        "not_computable_reasons": count(lambda r: (r["answer_reason"] or "").split(":")[0] if r["answer_status"] == NOT_COMPUTABLE else None),
        "n_provisional": sum(r["provisional"] for r in records),
        "table_data_sha256": records[0]["table_data_sha256"] if records else None,
    }


# --- prototype reproduction ------------------------------------------------------

#: The three frozen prototypes as filled TD-T02 templates (absolute change,
#: historical -> end-century, RCP8.5). P-STATE-1 is read at v2 (V and D are v1's).
PROTOTYPE_FILLS = (
    {"record_id": "P-CELL-1", "file": "P-CELL-1.json", "metric_id": "fwi_summer_seasonal_value",
     "location": ("cell", "R106C361")},
    {"record_id": "P-COUNTY-1", "file": "P-COUNTY-1.json", "metric_id": "fwi_summer_seasonal_value",
     "location": ("county", "Oklahoma|Stephens")},
    {"record_id": "P-STATE-1", "file": "P-STATE-1.v2.json", "metric_id": "heatindex_days_above_105F",
     "location": ("state", "California")},
)


def frozen_prototype_values(record: dict) -> dict:
    """baseline / future / change / direction as the frozen record holds them."""
    by_role = {c["role"]: c for c in record["V"]["per_column"]}

    def value(role: str) -> str:
        c = by_role[role]
        return c["raw_value"] if "raw_value" in c else c["aggregates"]["unweighted_mean"]

    return {"baseline_value": value("baseline"), "future_value": value("future"),
            "absolute_change": record["D"]["change_value"], "direction": record["D"]["direction"]}


def reproduce_prototypes(slots: dict, scan: dict, records: list[dict], prototypes_dir: Path = PROTOTYPES_DIR) -> dict:
    metrics = {m["metric"]["metric_id"]: m for m in governed_metrics(slots)}
    locations = {location_key(v): v for level in ("cell", "county", "state") for v in location_values(slots, level)}
    out = []
    for spec in PROTOTYPE_FILLS:
        path = Path(prototypes_dir) / spec["file"]
        frozen = frozen_prototype_values(json.loads(path.read_text(encoding="utf-8")))
        metric = metrics[spec["metric_id"]]["metric"]
        loc = locations[spec["location"]]
        blocked = concept_block_reason(metric, ["historical", "end_century"]) is not None
        computed = {}
        for stat in ("baseline_value", "future_value", "absolute_change", "direction"):
            p_from = "historical" if stat != "future_value" else None
            p_to = "end_century" if stat != "baseline_value" else None
            r = compute_statistic(scan, loc, metric, stat, p_from, p_to, audit=True)
            computed[stat] = r["value"]
        match = next(
            r for r in records
            if r["template_id"] == "TD-T02"
            and r["slots"]["CONCEPT"]["value_id"].endswith(":" + spec["metric_id"])
            and r["slots"]["LOCATION"]["value_id"] == f"{spec['location'][0]}:{spec['location'][1]}"
            and r["slots"]["PERIOD_FROM"]["value_id"] == "historical"
            and r["slots"]["PERIOD_TO"]["value_id"] == "end_century"
        )
        out.append({
            "record_id": spec["record_id"],
            "prototype_file": f"artifacts/phenomena/prototypes/{spec['file']}",
            "prototype_sha256": file_sha256(path),
            "template_id": "TD-T02",
            "question_id": match["question_id"],
            "question_text": match["question_text"],
            "question_answer_status": match["answer_status"],
            "question_answer": match["answer"],
            "audit_only": blocked,
            "audit_note": ("concept columns are inferred_candidate: values computed in audit mode to tie the "
                           "machinery to the frozen numbers; NOT an answer, never in questions_v1.jsonl")
                          if blocked else None,
            "computed": computed,
            "frozen": frozen,
            "equal": {k: computed[k] == frozen[k] for k in frozen},
            "question_answer_equals_frozen_change": (match["answer"] == frozen["absolute_change"]) if not blocked else None,
        })
    return {"schema_version": "td-reproduction-v1", "all_equal": all(all(e["equal"].values()) for e in out)
            and all(e["question_answer_equals_frozen_change"] in (True, None) for e in out), "prototypes": out}


def sample_records(records: list[dict], templates: dict) -> list[dict]:
    """The tracked sample: the first question of each table_only template, and
    every doc example, in enumeration order. `example_records` over the sample
    gives the same examples as over the full file."""
    keep = {r["question_id"] for r in example_records(records, templates)}
    seen: set[str] = set()
    for r in records:
        if r["template_id"] not in seen:
            seen.add(r["template_id"])
            keep.add(r["question_id"])
    return [r for r in records if r["question_id"] in keep]


def questions_file_pin(path: Path | str) -> dict:
    """questions_v1.jsonl is regenerable and too large to track (14 MB): it is
    pinned by hash instead, as D-005 pins the raw table."""
    path = Path(path)
    return {"path": "artifacts/templates/questions_v1.jsonl", "sha256": file_sha256(path),
            "bytes": path.stat().st_size, "n_records": len(read_jsonl(path)), "tracked_in_git": False,
            "regenerate_with": "python scripts/generate_template_questions.py"}


def doc_hashes(table_sha256: str, questions_sha256: str) -> dict:
    """The hashes the generated doc prints (inputs, then outputs). The full
    questions file may be absent (gitignored): its hash comes from the pin."""
    def rel(p: Path) -> str:
        return str(p.relative_to(REPO_ROOT))

    return {
        "data/raw/FullData.csv": table_sha256,
        rel(SLOTS_PATH): file_sha256(SLOTS_PATH),
        rel(TEMPLATES_PATH): file_sha256(TEMPLATES_PATH),
        rel(QUESTIONS_PATH) + " (gitignored)": questions_sha256,
        rel(SAMPLE_PATH): file_sha256(SAMPLE_PATH),
        rel(SUMMARY_PATH): file_sha256(SUMMARY_PATH),
        rel(REPRODUCTION_PATH): file_sha256(REPRODUCTION_PATH),
    }


def write_jsonl(records: list[dict], path: Path | str) -> None:
    with Path(path).open("w", encoding="utf-8", newline="\n") as handle:
        for r in records:
            handle.write(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def read_jsonl(path: Path | str) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


# --- the generated document ------------------------------------------------------


def example_records(records: list[dict], templates: dict) -> list[dict]:
    """The doc's ten examples, by rule: the first `computed` question_id of each
    table_only template (template order), then the first `not_computable`
    question_id of TD-T03 (the zero-baseline guard); first ten."""
    out = []
    for t in templates["templates"]:
        if t["answer_mode"] != "table_only":
            continue
        first = next((r for r in records if r["template_id"] == t["template_id"] and r["answer_status"] == COMPUTED), None)
        if first is not None:
            out.append(first)
    guard = next((r for r in records if r["template_id"] == "TD-T03" and r["answer_status"] == NOT_COMPUTABLE), None)
    if guard is not None:
        out.append(guard)
    return out[:10]


def _md_escape(text: str) -> str:
    return str(text).replace("|", "\\|")


def _derivation_lines(d: dict | None) -> list[str]:
    if not d:
        return ["  - derivation: none"]
    lines = []
    if "rule_id" in d:
        lines.append(f"  - rule: `{d['rule_id']}`")
    if d.get("location"):
        loc = d["location"]
        lines.append(f"  - location: {loc['level']} `{loc['label']}`, {loc['n_cells']} rows, member-cell hash `{loc['member_cells_sha256'][:12]}…`")
    if d.get("columns"):
        lines.append("  - columns: " + ", ".join(f"{c['index']} `{c['column']}` ({c['status']})" for c in d["columns"]))
    if d.get("raw_aggregates"):
        agg = {k: v for k, v in d["raw_aggregates"].items() if k != "per_cell_raw_values"}
        lines.append("  - aggregates: " + ", ".join(f"{k} `{v}`" for k, v in agg.items()))
    if d.get("compared"):
        lines.append("  - compared: " + ", ".join(f"{k} `{v}`" for k, v in d["compared"].items()))
    if "statistic_value" in d:
        lines.append(f"  - {d['extremum']} value `{d['statistic_value']}`; ranked {d['n_ranked']}, excluded {d['n_excluded_not_computable']}, tie {d['tie']}")
    if d.get("parts") and not d.get("compared"):
        lines.append(f"  - parts: {len(d['parts'])}")
    return lines


def render_doc(slots: dict, templates: dict, records: list[dict], summary: dict, reproduction: dict, hashes: dict) -> str:
    L: list[str] = []
    add = L.append
    add("# Track D v1 --- table-grounded question templates")
    add("")
    add("**Generated by `scripts/generate_template_questions.py` --- never hand-edited; regenerate.**")
    add("")
    add("Design and dry run only (D-031, D-033, D-034). **No model call. No corpus retrieval run. "
        "No QA accepted.** No column status, concept-map entry or compatibility rule is changed. "
        "A filled question is a table-side object; it becomes a QA candidate only after a linked "
        "passage, the deterministic checks and human review (D-033).")
    add("")
    add("## Inputs and outputs")
    add("")
    add("| File | SHA-256 |")
    add("| --- | --- |")
    for name, sha in hashes.items():
        add(f"| `{name}` | `{sha}` |")
    add("")
    add("## Slots")
    add("")
    add("Every value carries a `source` and an `authorization` (test). Authorization vocabulary: "
        + ", ".join(f"`{a}`" for a in AUTHORIZATIONS) + ".")
    add("")
    add("### [CONCEPT] --- governed families")
    add("")
    add("| Family | Metric (question wording) | Columns: historical / mid / end (status) | Authorization |")
    add("| --- | --- | --- | --- |")
    for m in governed_metrics(slots):
        fam, met = m["family"], m["metric"]
        cols = " / ".join(f"{c['index']} `{c['column']}` ({c['status']})" for c in met["period_columns"].values())
        add(f"| `{fam['id']}` | {met['wording']} | {cols} | `{met['authorization']}` |")
    add("")
    for fam in slots["concept"]["governed"]:
        add(f"- `{fam['id']}` surface forms (retrieval): " + ", ".join(f"`{t['term']}`" for t in fam["surface_forms"]))
        if fam.get("authorization_note"):
            add(f"  - {_md_escape(' '.join(fam['authorization_note'].split()))}")
    add("")
    add("**Excluded --- visible on purpose:**")
    add("")
    for fam in slots["concept"]["governed"]:
        for e in fam.get("seasons_excluded") or []:
            add(f"- `{fam['id']}` {e['season']}: columns {e['columns']} `{e['status']}` --- {e['reason']}")
        for e in fam.get("metrics_excluded") or []:
            add(f"- `{fam['id']}` {e['metric']}: columns {e['columns']} `{e['status']}` --- {' '.join(e['reason'].split())}")
        for m in fam["metrics"]:
            for e in m.get("verified_columns_not_used") or []:
                add(f"- `{fam['id']}` {e['index']} `{e['column']}` (verified, not used): {' '.join(e['reason_not_used'].split())}")
    for e in slots["concept"]["ungoverned"]:
        add(f"- {e['name']} ({', '.join(e['dictionary_concepts'])}): {e['status']}")
    add("")
    add("### [LOCATION]")
    add("")
    add("| Level | Column(s) (status) | Authorization | Values |")
    add("| --- | --- | --- | --- |")
    for level, block in slots["location"].items():
        cols = block.get("columns") or [block["column"]]
        cols_txt = ", ".join(f"{c['index']} `{c['column']}` ({c['status']})" for c in cols)
        values = location_values(slots, level)
        shown = ", ".join(f"{v['label']} ({v['n_cells']})" if "n_cells" in v else v["label"] for v in values)
        add(f"| {level} | {cols_txt} | `{block['authorization']}` | {len(values)}: {_md_escape(shown)} |")
    add("")
    st = slots["location"]["state"]
    add(f"State enumeration rule: {' '.join(st['enumeration_rule'].split())} `min_cells` = {st['min_cells']}. "
        f"Excluded: " + "; ".join(f"label `{e['label']!s}` ({e['n_cells']} rows) --- {e['reason']}" for e in st["excluded"]) + ".")
    add("")
    add("### [PERIOD], [SCENARIO], [SEASON]")
    add("")
    add("| Slot | Value | Wording | Source | Authorization |")
    add("| --- | --- | --- | --- | --- |")
    for key in ("period", "scenario", "season"):
        for e in slots[key]:
            src = e["source"]
            add(f"| {key} | `{e['id']}` | {e['wording'] or '---'} | line {src['line']}: \"{_md_escape(src['quote'])}\" | `{e['authorization']}` |")
    add("")
    add("### [STATISTIC]")
    add("")
    add("| Statistic | Rule | Reuses | Authorization | Rule text |")
    add("| --- | --- | --- | --- | --- |")
    for e in slots["statistic"]:
        add(f"| `{e['id']}` | `{e['rule_id']}` | {e['reuses'] or 'new'} | `{e['authorization']}` | {_md_escape(' '.join(e['rule'].split()))} |")
    add("")
    add("## Templates")
    add("")
    add("| Id | Name | Category | Method | QA type | Answer mode | Answerable now | Statistic | Text |")
    add("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for t in templates["templates"]:
        stat = ", ".join(t.get("statistics") or [t["statistic"]])
        add(f"| {t['template_id']} | {t['name']} | {t['category_type']} | {t['research_method']} | {t['qa_type']} | "
            f"{t['answer_mode']} | {'yes' if t['answerable_now'] else 'no --- needs a linked passage'} | {stat} | {_md_escape(t['text'])} |")
    add("")
    add("Retrieval-terms rule RT-1 (all templates): concept surface forms always; a state label (a "
        "county contributes its State label only; a cell none); the scenario's terms; future-period "
        "words. Never a heat-index threshold, a statistic or season word, a column name, a cell id, or "
        "an ungoverned term. A blocked question's terms are recorded with `retrieval_authorized: false`.")
    add("")
    add("## Enumeration rule")
    add("")
    add("Exhaustive, not random, over `table_only` templates only. Concepts: every metric of both governed "
        "families (FWI summer seasonal value; heat-index days above 95 / 105 / 115 / 125 F). Locations: "
        "the P-CELL-1 cell, the P-COUNTY-1 county, and every enumerated state. Period pairs: historical → "
        "mid-century, historical → end-of-century, mid-century → end-of-century. Scenario: RCP8.5 (the only "
        "scenario a governed column realizes); TD-T06 pairs RCP4.5 with RCP8.5 and is therefore "
        "not computable. TD-T04 uses the historical period only; TD-T05 the two future periods. TD-T07 "
        "pairs California (the P-STATE-1 state) with every other state. TD-T08 compares historical → "
        "mid-century with historical → end-of-century. TD-T09 pairs the FWI metric with each heat-index "
        "metric. TD-T10 / TD-T11 rank all enumerated states, for absolute and percent change. "
        "Question ids are `TD1-<template>-<n>` in enumeration order (metric, location, period, scenario).")
    add("")
    add("## Counts")
    add("")
    add(f"- Templates: **{summary['n_templates']}** ({summary['n_templates_table_only']} `table_only`, "
        f"{summary['n_templates_need_passage']} need a linked passage).")
    add(f"- Filled questions: **{summary['n_questions']}** --- "
        + ", ".join(f"`{k}` {summary['by_answer_status'][k]}" for k in ANSWER_STATUSES)
        + f"; provisional (computed) {summary['n_provisional']}.")
    add(f"- Not-computable reasons: " + ", ".join(f"`{k}` {v}" for k, v in summary["not_computable_reasons"].items() if k) + ".")
    add("")
    add("| Template | " + " | ".join(ANSWER_STATUSES) + " | total |")
    add("| --- | " + " | ".join("---" for _ in ANSWER_STATUSES) + " | --- |")
    for tid, total in summary["by_template"].items():
        cells = [str(summary["by_template_and_status"].get(f"{tid}|{s}", 0)) for s in ANSWER_STATUSES]
        add(f"| {tid} | " + " | ".join(cells) + f" | {total} |")
    add("")
    for title, key in (("Concept family", "by_concept_family"), ("Location granularity", "by_location_level")):
        add(f"| {title} | " + " | ".join(ANSWER_STATUSES) + " | total |")
        add("| --- | " + " | ".join("---" for _ in ANSWER_STATUSES) + " | --- |")
        for k, total in summary[key].items():
            cells = [str(summary[key + "_and_status"].get(f"{k}|{s}", 0)) for s in ANSWER_STATUSES]
            add(f"| {k} | " + " | ".join(cells) + f" | {total} |")
        add("")
    add("## Prototype reproduction")
    add("")
    add("Each frozen prototype as a filled TD-T02 (absolute change, historical → end-of-century, RCP8.5). "
        "FWI values are computed in **audit mode only** (`artifacts/templates/prototype_reproduction_v1.json`) "
        "and never enter `questions_v1.jsonl`, where those questions stay `blocked_inferred_columns`.")
    add("")
    add("| Prototype | Question | Status in questions | Baseline | Future | Change | Direction | Equal |")
    add("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for e in reproduction["prototypes"]:
        c = e["computed"]
        add(f"| {e['record_id']} | `{e['question_id']}` | `{e['question_answer_status']}` | `{c['baseline_value']}` | "
            f"`{c['future_value']}` | `{c['absolute_change']}` | {c['direction']} | {all(e['equal'].values())} |")
    add("")
    add(f"All equal to the frozen values: **{reproduction['all_equal']}**.")
    add("")
    add("## Ten examples")
    add("")
    add("Rule: the first `computed` question_id of each `table_only` template, in template order (templates "
        "with none --- TD-T06, TD-T09 --- are skipped), then the first `not_computable` question_id of "
        "TD-T03 (the zero-baseline guard); the first ten.")
    add("")
    for r in example_records(records, templates):
        add(f"- **`{r['question_id']}`** ({r['template_id']}, `{r['answer_status']}`) --- {r['question_text']}")
        ans = r["answer"] if r["answer_status"] == COMPUTED else f"--- ({r['answer_reason']})"
        unit = f" {r['answer_unit']}" if r.get("answer_unit") else ""
        add(f"  - answer: `{ans}`{unit}" + (f"; provisional: {'; '.join(r['provisional_reasons'])}" if r["provisional"] else ""))
        add(f"  - retrieval terms: " + ", ".join(f"`{t}`" for t in r["retrieval_terms"]))
        L.extend(_derivation_lines(r["answer_derivation"]))
    add("")
    add("## How a template question meets the paper side")
    add("")
    add("1. **Retrieval terms → corpus index.** A filled question's `retrieval_terms` (RT-1) are the query "
        "against the frozen LITCORPUS-02 index --- only where `retrieval_authorized` is true. Not run in v1.")
    add("2. **Track C agent proposes passages** (D-030). The agent sees the filled question's slots and "
        "definitions only --- never the computed answer, its direction, or prior verdicts (D-033).")
    add("3. **Candidate record** (`data/metadata/softqa/candidate_schema_v1.json`): table side = template id, "
        "filled slots with their authorizations, columns, member-cell hash, scenario, period, and --- "
        "populated by deterministic code only after the structure is frozen --- the computed answer and its "
        "derivation; paper side = item id, file SHA-256, JSON path, `[start,end)` span, verbatim passage. "
        "Status `llm_candidate`.")
    add("4. **Deterministic checks** (span re-slices; concept and place terms located; place role recorded); "
        "failure → `rejected_pre_review`.")
    add("5. **Human review** by `docs/SOFTQA_REVIEW_PROTOCOL.md`; a second reviewer for multi-concept, "
        "cross-location with differing granularity, and derived-statistic cases. C/G/T/S/D is recorded, "
        "not a gate. Only `accepted` / `accepted_after_edit` is benchmark-valid.")
    add("")
    add("`table_only` questions need no passage for their answer, but they are not benchmark QA until a "
        "ruling says so. FWI questions stay blocked until the FWI columns are owner-confirmed.")
    add("")
    return "\n".join(L)
