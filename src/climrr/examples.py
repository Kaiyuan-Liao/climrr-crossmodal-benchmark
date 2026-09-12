"""Row-centered candidate examples: raw bytes, recorded semantics, generated prose.

Authorised by D-011 as bounded M1-WP3 work. These are **not** M2 phenomenon
records. In the GUIDANCE ruling's words they are

    row-centered candidate event prototypes for semantic validation

and they exist for one purpose: to turn abstract metadata ambiguity into
specific decisions a mentor can confirm or correct field by field.

The three-layer separation is the whole design
----------------------------------------------

Each record keeps three things apart, in this order, and never lets one leak
into another:

1. **`raw`** --- what the file says. Every selected column's value exactly as
   read, as a string, empty string preserved. This layer is checkable against
   the CSV byte for byte and contains no interpretation at all.
2. **`semantics`** --- what the project claims the values mean, per column, each
   claim carrying its own status and its own provenance: `dictionary` where a
   cited span states it, `inferred` where an IC-record reasons it, `unknown`
   where nothing does. This layer contains no prose about the row.
3. **`presentation`** --- a mentor-readable description **generated from layer 2
   by template**. Not written by hand, and not written by a model. Every clause
   resting on an `inferred` attribute is wrapped as `[provisional: ...]`, so a
   reader can see the boundary between what the dictionary says and what this
   project reasoned without consulting anything else.

Between 2 and 3 sits `assumptions`, the enumerated list the record depends on.
It always starts with **A1: one CSV row is one "event"**, which is an assumption
under mentor review and not a property of this file.

What the template may say
-------------------------

Only what a semantics entry or an assumption supports. Three standing cautions
are emitted when, and only when, an entry in *this* record triggers them --- a
Fire Weather Index column, a `Historical` attribute, an empty cell --- and each
records which entries triggered it and which dictionary line it rests on. There
is no fourth source of sentences. If the template ever needs one, that is a
defect to escalate, not a string to add.

What no part of this module does
--------------------------------

No aggregation. No threshold. No selection of rows by magnitude --- the three
selection rules are structural and say nothing about climate. No adjective about
how large a value is. No reading of a Fire Weather Index as a fire. No treating
of a modeled historical baseline as an observation. No treating of an empty cell
as a zero or as a meaning.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from climrr.dictionary import (
    INFERRED_CANDIDATE,
    OWNER_CONFIRMED,
    SEASON_WORDS,
    UNIT_MARKERS,
    VERIFIED_FROM_DICTIONARY,
)
from climrr.profile import ENCODING

EXAMPLES_VERSION = 1

#: The three statuses a pilot column may hold. A selected column at any other
#: status means the subset and the coverage run disagree, which is a defect.
ALLOWED_PILOT_STATUSES = frozenset(
    {VERIFIED_FROM_DICTIONARY, OWNER_CONFIRMED, INFERRED_CANDIDATE}
)

#: Split out of the dictionary's scenario markers so that a record can say
#: "which pathway" and "which decade" separately, as the M1 metadata
#: requirements ask. Both halves are literal strings the dictionary prints.
HORIZON_MARKERS = ("Historical", "Mid-Century", "End-Century")
PATHWAY_MARKERS = ("RCP4.5", "RCP8.5", "RCP 4.5", "RCP 8.5")

#: Provenance of one semantic attribute, as it appears in a record.
FROM_DICTIONARY = "dictionary"
FROM_INFERENCE = "inferred"
FROM_NOWHERE = "unknown"

#: `from_dictionary` in an IC-record means the same thing as `dictionary` here.
_IC_PROVENANCE_TO_RECORD = {"from_dictionary": FROM_DICTIONARY, "inferred": FROM_INFERENCE}

PROVISIONAL_OPEN = "[provisional: "
PROVISIONAL_CLOSE = "]"
PROVISIONAL_RE = re.compile(r"\[provisional: ([^\]]*)\]")

#: How an empty cell is rendered. Never a zero, never "missing", never "N/A" ---
#: all three of those would assign a meaning the file does not carry.
NO_VALUE = "no value in this file"

#: The grain the whole pilot rests on, and the thing the mentor is being asked
#: about first. Kaiyuan's reading of the 2026-09-10 direction (R-002), not the
#: mentor's words, and explicitly an assumption under review (D-011).
A1_STATEMENT = (
    'One CSV row is treated as one "event". That grain is under mentor review '
    "and is **not** established as a property of this file."
)


class ExampleError(RuntimeError):
    """The subset, the coverage report and the data file disagree about something."""


# --- the pilot subset ---------------------------------------------------------
#
# Selected under D-010/D-011 and documented, with the rationale per family and
# the exclusions, in `docs/PILOT_SUBSET.md`. Held here as data rather than as
# prose so that the examples, the tests and the document cannot drift apart.
#
# `caution` is a standing sentence the presentation template emits once per
# family when that family appears in a record. It is not commentary: each one
# names the dictionary line it rests on, and the repository's operating rules
# require the Fire Weather Index one on every mention of those columns.

PILOT_FAMILIES = (
    {
        "key": "heat_index",
        "label": "Heat Index – Summer",
        "indices": (238, 240, 241, 242, 243, 244, 246, 247, 248, 249, 250, 252, 253, 254, 255, 256, 262),
        "caution": None,
        "caution_span": None,
    },
    {
        "key": "fire_weather",
        "label": "Fire Weather Index - Averages",
        "indices": (180, 181, 187, 188, 189, 190, 191, 192, 193, 194, 195, 201, 202),
        "caution": (
            "Every `wildfire_*` column below holds a **Fire Weather Index** --- a "
            "meteorological fire-danger index, listed in the dictionary under the section "
            '"Fire Weather Index - Averages". It is not a wildfire, an ignition, a burned '
            "area, or a probability of any of those, and nothing in this record says that it is."
        ),
        "caution_span": {"line": 637, "quote": "Fire Weather Index - Averages"},
    },
    {
        "key": "location",
        "label": "Location anchor",
        "indices": (1, 2, 3, 4, 106, 107, 108, 109),
        "caution": (
            "The Census vintage and the coordinate reference system of these columns are "
            "**unknown**. They locate this one row; no part of this pilot groups rows by any "
            "of them."
        ),
        "caution_span": None,
    },
    {
        "key": "stem_probe",
        "label": "Temperature Maximum – Annual (stem-assumption probe)",
        "indices": (44, 48, 52),
        "caution": (
            "These three columns reach their meaning through an **unconfirmed** link between "
            "the CSV name stem `tempmaxann` and a dictionary section (Q1). The dictionary "
            "never states that link, and 101 columns of this file depend on it."
        ),
        "caution_span": {"line": 513, "quote": "Temperature Maximum - Annual"},
    },
)

#: Every selected column, in file order.
PILOT_INDICES = tuple(
    sorted(index for family in PILOT_FAMILIES for index in family["indices"])
)

#: Columns used to address a row. Reported in `provenance` so a reader has a
#: stable handle on the row, and **not** members of the pilot subset: naming
#: `OID_` here is not a claim about what it means, and Q11 stays open.
OID_INDEX = 0
CROSSMODEL_INDEX = 1
GEOID_INDEX = 109


def family_of(index: int) -> dict:
    for family in PILOT_FAMILIES:
        if index in family["indices"]:
            return family
    raise ExampleError(f"column index {index} is not in the pilot subset")


# --- Phase C: row selection, on structural criteria only ----------------------
#
# Every rule below can be evaluated without looking at how large a value is.
# That is the point: GUIDANCE forbids selecting rows by magnitude or salience,
# so no rule may mention one. Each rule instead tests something about the
# *presentation* problem --- a fully populated row, a leading-zero identifier, a
# row with a blank --- and each example records the rule that found it.

SELECTION_RULES = (
    {
        "id": "R-A",
        "description": (
            "the first row, in file order, that is non-empty on every selected pilot column"
        ),
        "tests": "the ordinary case, where nothing about presentation is in question",
    },
    {
        "id": "R-B",
        "description": (
            "the first row, in file order, whose `GEOID` begins with `0` and that is "
            "non-empty on every selected pilot column"
        ),
        "tests": (
            "whether a leading-zero Census identifier survives into what the mentor reads. "
            "Coercing `GEOID` to an integer would delete the zero and silently corrupt every "
            "join; 19,074 rows of this file carry one"
        ),
    },
    {
        "id": "R-C",
        "description": (
            "the first row, in file order, that is empty on at least one selected pilot column"
        ),
        "tests": (
            "how a blank is presented --- as \"no value in this file\", never as a zero and "
            "never as a claim that something is missing"
        ),
    },
)


def _rule(rule_id: str) -> dict:
    return next(rule for rule in SELECTION_RULES if rule["id"] == rule_id)


def select_rows(path: Path | str, indices=PILOT_INDICES) -> dict:
    """Stream the CSV once and return the row each rule selects.

    Returns `{rule_id: {"ordinal": int, "values": [...]}}`, the values being the
    complete row as read. A rule that matches no row is absent from the result,
    which the caller must treat as a finding rather than as an empty case.
    """
    wanted = tuple(indices)
    found: dict[str, dict] = {}
    with Path(path).open("r", encoding=ENCODING, newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        for ordinal, row in enumerate(reader):
            if len(row) <= max(wanted):
                raise ExampleError(
                    f"row ordinal {ordinal} has {len(row)} fields, fewer than the "
                    f"{max(wanted) + 1} the pilot subset needs. Stop and report."
                )
            complete = all(row[index] != "" for index in wanted)
            if complete and "R-A" not in found:
                found["R-A"] = {"ordinal": ordinal, "values": list(row)}
            if complete and "R-B" not in found and row[GEOID_INDEX].startswith("0"):
                found["R-B"] = {"ordinal": ordinal, "values": list(row)}
            if not complete and "R-C" not in found:
                found["R-C"] = {"ordinal": ordinal, "values": list(row)}
            if len(found) == len(SELECTION_RULES):
                break
    return found


# --- Phase D block 3: semantics, per column -----------------------------------


def _attribute(value: str | None, provenance: str) -> dict:
    """One semantic attribute: a value, or an explicit nothing, and where it came from."""
    if value is None:
        return {"value": None, "provenance": FROM_NOWHERE}
    return {"value": value, "provenance": provenance}


def _markers_in(description: str, markers) -> str | None:
    """The dictionary's own words, where it printed them. Never a paraphrase."""
    found = [marker for marker in markers if marker in description]
    return ", ".join(found) if found else None


def _season_in(description: str) -> str | None:
    lowered = description.lower()
    found = [word.capitalize() for word in sorted(SEASON_WORDS) if word in lowered]
    return ", ".join(found) if found else None


def _semantics_from_dictionary(column: dict) -> dict:
    """Attributes for a column the dictionary itself describes.

    Everything here is either a verbatim description or a literal marker the
    dictionary printed inside it --- the same markers `climrr.dictionary` used to
    decide that the column was verified in the first place. Nothing is
    paraphrased, and nothing is derived from the column's name.
    """
    spans = column["dictionary_evidence"]
    entries = [span for span in spans if span.get("kind") == "field_entry"]
    span = entries[0] if entries else spans[0]
    description = span["text"]
    # The extracted line is "<field name> <description>"; the field name is the
    # first token and is not part of the meaning.
    meaning = description.split(" ", 1)[1].strip() if " " in description else description
    return {
        "meaning": _attribute(meaning, FROM_DICTIONARY),
        "unit": _attribute(_markers_in(description, UNIT_MARKERS), FROM_DICTIONARY),
        "scenario": _attribute(_markers_in(description, PATHWAY_MARKERS), FROM_DICTIONARY),
        "horizon": _attribute(_markers_in(description, HORIZON_MARKERS), FROM_DICTIONARY),
        "season": _attribute(_season_in(description), FROM_DICTIONARY),
        "rests_on": {
            "kind": "dictionary_span",
            "line": span["line"],
            "quote": span["text"],
        },
    }


def _semantics_from_inferred(record: dict) -> dict:
    """Attributes for a column an IC-record reasons about."""

    def tagged(key: str) -> dict:
        field = record[key]
        if field is None:
            return _attribute(None, FROM_NOWHERE)
        return _attribute(field["value"], _IC_PROVENANCE_TO_RECORD[field["provenance"]])

    return {
        "meaning": _attribute(record["proposed_meaning"].strip(), FROM_INFERENCE),
        "unit": tagged("proposed_unit"),
        "scenario": tagged("proposed_scenario"),
        "horizon": tagged("proposed_horizon"),
        "season": tagged("proposed_season"),
        "rests_on": {
            "kind": "inferred_candidate_record",
            "id": record["id"],
            "disclaimer": record["disclaimer"],
            "lines": [span["line"] for span in record["dictionary_spans"]],
        },
    }


def build_semantics(coverage: dict, inferred_by_index: dict[int, dict]) -> list[dict]:
    """One semantics entry per selected column, in file order."""
    entries = []
    for index in PILOT_INDICES:
        column = coverage["columns"][index]
        if column["status"] not in ALLOWED_PILOT_STATUSES:
            raise ExampleError(
                f"pilot column {index} `{column['column']}` holds status "
                f"{column['status']!r}, which is not one of "
                f"{sorted(ALLOWED_PILOT_STATUSES)}. The pilot subset and the coverage run "
                "disagree; stop and report."
            )
        if column["status"] == INFERRED_CANDIDATE:
            record = inferred_by_index.get(index)
            if record is None:
                raise ExampleError(
                    f"pilot column {index} `{column['column']}` is at {INFERRED_CANDIDATE} "
                    "but no IC-record was loaded for it."
                )
            attributes = _semantics_from_inferred(record)
        else:
            attributes = _semantics_from_dictionary(column)
        family = family_of(index)
        entries.append(
            {
                "index": index,
                "column": column["column"],
                "family": family["label"],
                "family_key": family["key"],
                "family_caution": family["caution"],
                "family_caution_span": family["caution_span"],
                "status": column["status"],
                **attributes,
            }
        )
    return entries


# --- Phase D block 4: assumptions ---------------------------------------------


def build_assumptions(semantics: list[dict], inferred_by_index: dict[int, dict]) -> list[dict]:
    """A1 first, then every assumption the record's inferred columns depend on.

    Deduplicated by statement and ordered by the column that first raised it, so
    the list is stable across runs and the mentor can answer it line by line.
    """
    assumptions = [
        {
            "id": "A1",
            "statement": A1_STATEMENT,
            "question_ids": [],
            "raised_by": [],
            "source": "D-011",
        }
    ]
    seen: dict[str, dict] = {}
    for entry in semantics:
        record = inferred_by_index.get(entry["index"])
        if record is None:
            continue
        for statement in record["assumptions"]:
            text = " ".join(statement.split())
            existing = seen.get(text)
            if existing is not None:
                existing["raised_by"].append(entry["index"])
                for question in record["question_ids"]:
                    if question not in existing["question_ids"]:
                        existing["question_ids"].append(question)
                continue
            item = {
                "id": f"A{len(assumptions) + 1}",
                "statement": text,
                "question_ids": list(record["question_ids"]),
                "raised_by": [entry["index"]],
                "source": record["id"],
            }
            seen[text] = item
            assumptions.append(item)
    return assumptions


# --- Phase D block 5: the presentation template -------------------------------
#
# Generated, never written. Every sentence below comes from a semantics entry,
# an assumption, or one of the three standing cautions --- and each caution
# records the entries that triggered it, so nothing in the output is untraceable.


def _provisional(text: str) -> str:
    if "[" in text or "]" in text:
        raise ExampleError(
            f"a semantic value contains a square bracket and cannot be labelled "
            f"provisional unambiguously: {text!r}"
        )
    return f"{PROVISIONAL_OPEN}{text}{PROVISIONAL_CLOSE}"


def _clause(attribute: dict) -> str | None:
    """Render one attribute, wrapping it if it rests on inference."""
    if attribute["value"] is None:
        return None
    if attribute["provenance"] == FROM_INFERENCE:
        return _provisional(attribute["value"])
    return attribute["value"]


def _value_phrase(raw: str) -> str:
    return NO_VALUE if raw == "" else f"`{raw}`"


def _column_sentence(entry: dict, raw: str) -> str:
    """One column, one line: what the file holds, and what it is claimed to mean."""
    parts = [f"- **[{entry['index']}] `{entry['column']}`** = {_value_phrase(raw)}"]
    meaning = _clause(entry["meaning"])
    if meaning is not None:
        parts.append(f" --- {meaning}")
    qualifiers = []
    # "unit or type" rather than "unit": the dictionary's own markers mix the
    # two --- `(°F)` is a unit, `Text ID` and `Number of` are types --- and
    # `climrr.dictionary` verifies a column on either. Calling a type a unit
    # here would be this module inventing a distinction the source does not make.
    for key, label in (
        ("unit", "unit or type"),
        ("scenario", "scenario"),
        ("horizon", "horizon"),
        ("season", "season"),
    ):
        clause = _clause(entry[key])
        if clause is not None:
            qualifiers.append(f"{label}: {clause}")
    if qualifiers:
        parts.append(f" ({'; '.join(qualifiers)})")
    parts.append(f" [status: `{entry['status']}`]")
    return "".join(parts)


def build_cautions(semantics: list[dict], raw: list[dict]) -> list[dict]:
    """The standing cautions this record triggers, with what triggered each."""
    cautions = []
    raw_by_index = {item["index"]: item["value"] for item in raw}

    for family in PILOT_FAMILIES:
        if family["caution"] is None:
            continue
        triggered = [
            entry["index"] for entry in semantics if entry["family_key"] == family["key"]
        ]
        if triggered:
            cautions.append(
                {
                    "id": f"C-{family['key']}",
                    "text": family["caution"],
                    "basis": f"every semantics entry in the family {family['label']!r}",
                    "span": family["caution_span"],
                    "triggered_by": triggered,
                }
            )

    historical = [
        entry["index"]
        for entry in semantics
        if any(
            (entry[key]["value"] or "").find("Historical") >= 0
            for key in ("meaning", "scenario", "horizon")
        )
    ]
    if historical:
        cautions.append(
            {
                "id": "C-historical",
                "text": (
                    "`Historical` wherever it appears below means a **modeled historical "
                    "baseline** --- the dictionary's historical period, 1995 to 2004, run "
                    "through the same climate models. It is not an observation, a "
                    "measurement, or a record of anything that happened."
                ),
                "basis": "the meaning, scenario or horizon of the semantics entries listed",
                "span": {
                    "line": 102,
                    "quote": (
                        "2094). A historical period (1995 to 2004) is also modeled using GHG "
                        "concentrations during this period."
                    ),
                },
                "triggered_by": historical,
            }
        )

    blanks = [
        entry["index"] for entry in semantics if raw_by_index.get(entry["index"], "") == ""
    ]
    if blanks:
        cautions.append(
            {
                "id": "C-blank",
                "text": (
                    f'An empty cell is written "{NO_VALUE}". It is **not** a zero and this '
                    "record does not claim it means anything else; what the empty rows of "
                    "this file are is an open question (Q16)."
                ),
                "basis": "the raw values of the entries listed, which are the empty string",
                "span": None,
                "triggered_by": blanks,
            }
        )
    return cautions


def render_presentation(
    provenance: dict,
    raw: list[dict],
    semantics: list[dict],
    assumptions: list[dict],
    cautions: list[dict],
) -> str:
    """The mentor-readable text, assembled from the blocks above and nothing else."""
    raw_by_index = {item["index"]: item["value"] for item in raw}
    a1 = next(item for item in assumptions if item["id"] == "A1")

    lines = [
        f"### Candidate record --- row `OID_` {provenance['OID_']}, "
        f"`Crossmodel` `{provenance['Crossmodel']}`",
        "",
        f"Row ordinal {provenance['row_ordinal']} of the file, selected by rule "
        f"**{provenance['selection_rule']['id']}** --- "
        f"{provenance['selection_rule']['description']}. "
        f"The rule tests {provenance['selection_rule']['tests']}.",
        "",
        f"**A1.** {a1['statement']}",
        "",
    ]

    by_family: dict[str, list[dict]] = {}
    for entry in semantics:
        by_family.setdefault(entry["family_key"], []).append(entry)
    caution_by_id = {caution["id"]: caution for caution in cautions}

    # The two record-wide cautions come before the lines they qualify, not
    # after: a reader must meet "this is a modeled baseline" before meeting the
    # first `Historical`, not once they have already read it as an observation.
    for caution_id in ("C-historical", "C-blank"):
        caution = caution_by_id.get(caution_id)
        if caution is not None:
            lines.append(f"> {caution['text']}")
            lines.append("")

    for family in PILOT_FAMILIES:
        entries = by_family.get(family["key"])
        if not entries:
            continue
        lines.append(f"**{family['label']}**")
        lines.append("")
        caution = caution_by_id.get(f"C-{family['key']}")
        if caution is not None:
            lines.append(f"> {caution['text']}")
            lines.append("")
        for entry in entries:
            lines.append(_column_sentence(entry, raw_by_index[entry["index"]]))
        lines.append("")

    lines.append(
        f"Every clause marked {PROVISIONAL_OPEN.strip()}...{PROVISIONAL_CLOSE} rests on an "
        "inferred-candidate record: reasoned and written down, **not verified and not "
        "owner-confirmed**. Clauses without that mark are quoted from the tracked data "
        "dictionary."
    )
    return "\n".join(lines).rstrip() + "\n"


# --- Phase D: the record ------------------------------------------------------


def build_example(
    *,
    rule_id: str,
    ordinal: int,
    values: list[str],
    coverage: dict,
    inferred_by_index: dict[int, dict],
    csv_sha256: str,
) -> dict:
    """One complete example record, blocks in the order D-011 fixes."""
    raw = [
        {"index": index, "column": coverage["columns"][index]["column"], "value": values[index]}
        for index in PILOT_INDICES
    ]
    semantics = build_semantics(coverage, inferred_by_index)
    assumptions = build_assumptions(semantics, inferred_by_index)
    cautions = build_cautions(semantics, raw)
    provenance = {
        "csv_sha256": csv_sha256,
        "OID_": values[OID_INDEX],
        "Crossmodel": values[CROSSMODEL_INDEX],
        "row_ordinal": ordinal,
        "selection_rule": _rule(rule_id),
    }
    return {
        "examples_version": EXAMPLES_VERSION,
        "record_kind": (
            "row-centered candidate event prototype for semantic validation "
            "(M1-WP3, D-011). Not an M2 phenomenon record."
        ),
        "provenance": provenance,
        "raw": raw,
        "semantics": semantics,
        "assumptions": assumptions,
        "presentation": {
            "generated_by": "template in climrr.examples.render_presentation",
            "cautions": cautions,
            "text": render_presentation(provenance, raw, semantics, assumptions, cautions),
        },
    }


def column_line(text: str, index: int) -> str | None:
    """The presentation line the template wrote for one column, or None."""
    prefix = f"- **[{index}] "
    for line in text.splitlines():
        if line.startswith(prefix):
            return line
    return None


def unlabelled_inferred_values(example: dict) -> list[tuple[int, str, str]]:
    """Inferred values shown in a column's own line outside a provisional label.

    An empty list is the property the record has to have. Anything else means a
    reasoned claim is being shown to the mentor as though the dictionary had
    said it, which is the exact failure D-011 exists to prevent.

    The check is scoped to the column's own line on purpose. A value like
    `RCP8.5` is inferred for one column and quoted verbatim from the dictionary
    for another, so counting occurrences across the whole document would flag
    the dictionary's own words as an unlabelled inference. Within one line there
    is no such ambiguity: every clause on it describes that one column.
    """
    text = example["presentation"]["text"]
    offences = []
    for entry in example["semantics"]:
        line = column_line(text, entry["index"])
        if line is None:
            offences.append((entry["index"], "line", "no presentation line was generated"))
            continue
        labelled = " ".join(PROVISIONAL_RE.findall(line))
        for key in ("meaning", "unit", "scenario", "horizon", "season"):
            attribute = entry[key]
            if attribute["provenance"] != FROM_INFERENCE or attribute["value"] is None:
                continue
            value = attribute["value"]
            if line.count(value) != labelled.count(value) or line.count(value) == 0:
                offences.append((entry["index"], key, value))
    return offences
