"""Match CSV column names against the extracted ClimRR data dictionary.

This module does **not** decide what a column means. It decides, mechanically
and citably, *how much the dictionary says* about each column name, and it
writes down the specific question that would resolve the rest.

What the dictionary actually is
-------------------------------

Reading `data/metadata/dictionary_extracted.txt` establishes one structural fact
that governs everything here: **the dictionary's field names are not the CSV's
column names.** The dictionary is organised as eleven per-variable tables, each
introduced by a section title, and inside a table the field name is only the
*suffix* --- `HIST`, `RCP45_MIDC`, `MID85_45` --- with the variable carried by the
section title above it. The CSV instead carries names like
`tempmaxann_rcp45_midc`: a stem, then that same suffix.

The dictionary never states that a CSV stem corresponds to a section title. It
describes eleven separate gridded layers, each with its own `HIST` field; the
CSV appears to be those layers side by side. Concluding that
`tempmaxann_rcp45_midc` *is* the `RCP45_MIDC` field of "Temperature Maximum -
Annual" therefore requires an inference about how the export was built --- an
inference this project's rules reserve for the data owner, not the EXECUTOR.

So a stem-based match can never reach `verified_from_dictionary` here, however
obvious it looks. It reaches `partially_resolved`, carries the proposed section
as an explicitly EXECUTOR-authored candidate, and produces a question that names
the column index, the candidate section, and the line to check.

Parsing rules
-------------

Applied to the extracted text after the line reading `Data Dictionary`:

* A **table** starts at a line reading `Field Name Description` in any case.
* A **row** inside a table is a line whose first word contains `_` or is one of
  `Crossmodel`, `hist` (either case). Everything else in a table is a title.
  Those four are the only underscore-free field names the dictionary uses, so
  this separates `hist Wind Speed (mph) ...` from the title `Heat Index -
  Summer` without guessing.
* The extractor sometimes splits a field name before a season, as in
  `rcp45_endc_ Spring`. A first word ending in `_` absorbs a following season
  word, and internal whitespace is removed from the recorded name.
* A **section title** is a short line (at most 60 characters) that does not end
  in a full stop. The length rule excludes the body paragraphs; the full-stop
  rule excludes the one short sentence among them, since no section title in
  this document ends in a period.
* Titles and tables are then paired **in document order**. This is required
  rather than cosmetic: on pages 17 and 18 every title appears above *all* the
  tables on the page, so pairing a table with the nearest preceding line would
  attribute three of the seven tables to the wrong variable. Parsing fails
  loudly if the two counts differ.

Status rules
------------

* `structurally_observed_only` --- the name matched nothing. Only Phase B facts.
* `unresolved` --- matched, but the evidence is blank or ambiguous.
* `partially_resolved` --- evidence found; some of meaning, unit and
  scenario/horizon stated, or the link to it is EXECUTOR-proposed.
* `verified_from_dictionary` --- the name itself appears in the dictionary, all
  matching entries agree, and the cited span states meaning, a unit or type,
  and a scenario/horizon. An entry the dictionary calls a "Text ID" satisfies
  the scenario/horizon requirement by being an identifier rather than a
  measurement.

Every status cites at least one span; a status without one is `unresolved`.
"""

from __future__ import annotations

import difflib
import re

#: Line that opens each field table, in either of the two cases the PDF uses.
TABLE_HEADER_RE = re.compile(r"^\s*field name\s+description\s*$", re.IGNORECASE)

#: Marks the start of the field-table part of the document.
DATA_DICTIONARY_MARKER = "Data Dictionary"

#: The only field names in the dictionary that contain no underscore.
BARE_FIELD_NAMES = {"crossmodel", "hist"}

SEASON_WORDS = {"winter", "spring", "summer", "autumn"}

PAGE_MARKER_RE = re.compile(r"^=== PAGE \d+ ===$")

CONTENTS_ENTRY_RE = re.compile(r"^\s*\d+\.\s")

#: A run of dots is the table-of-contents leader. A phrase found on such a line
#: is the contents entry, not the passage itself, and must never be cited as
#: evidence -- the contents says only that a section exists.
DOT_LEADER_RE = re.compile(r"\.{4,}")

MAX_SPAN_CHARS = 300

#: Literal markers, quoted from the dictionary, that state a unit or a type.
UNIT_MARKERS = ("(°F)", "(in)", "(mph)", "Degree Days", "Number of", "Text ID", "Percent Change")

#: Literal markers that state a scenario or a time horizon.
SCENARIO_MARKERS = (
    "Historical",
    "Mid-Century",
    "End-Century",
    "RCP4.5",
    "RCP8.5",
    "RCP 4.5",
    "RCP 8.5",
)

#: The dictionary's own words for a field that identifies rather than measures.
IDENTIFIER_MARKER = "Text ID"

#: **EXECUTOR-authored, not stated in the dictionary.** Proposed correspondence
#: between a CSV column-name stem and a dictionary section title, offered so the
#: open questions can be specific. Confirming these is a mentor decision; until
#: then no column matched through this map may be called verified.
STEM_SECTION_CANDIDATES = {
    "tempminann": "Temperature Minimum – Annual",
    "tempmin_seas": "Temperature Minimum – Seasonal",
    "tempmaxann": "Temperature Maximum - Annual",
    "tempmax_seas": "Temperature Maximum – Seasonal",
    "precipann": "Precipitation – Annual Total",
    "noprecip": "Precipitation None - Annual Average",
    "windspeed": "Wind Speed – Annual Average",
    "cdd": "Cooling Degree Days – Annual Total",
    "hdd": "Heating Degree Days – Annual Total",
}

#: **EXECUTOR-authored.** Narrative passages that discuss a column family whose
#: name appears in no field table. Located by searching for the phrase, so the
#: cited line numbers follow the extracted file rather than being hard-coded.
NARRATIVE_CANDIDATES = (
    {
        "applies_to_prefixes": ("FWI_Bins", "FWIBins"),
        "phrases": ("Calculating FWI Classes", "FWI Class Percentile range in"),
        "label": "Calculating FWI Classes",
    },
)


def _normalise_name(name: str) -> str:
    """Drop the whitespace the PDF extractor injects inside a field name."""
    return re.sub(r"\s+", "", name)


def _split_row(line: str) -> tuple[str, str] | None:
    """Split a table line into (field name, description), or return None.

    Returns a pair even when the description is empty: the dictionary really
    does list fields with nothing written against them, and that blank is a
    finding rather than a parse failure.
    """
    stripped = line.strip()
    if not stripped:
        return None
    parts = stripped.split()
    first = parts[0]
    if "_" not in first and first.lower() not in BARE_FIELD_NAMES:
        return None
    consumed = 1
    if first.endswith("_") and len(parts) > 1 and parts[1].lower() in SEASON_WORDS:
        first = first + parts[1]
        consumed = 2
    return _normalise_name(first), " ".join(parts[consumed:]).strip()


def parse_dictionary(lines: list[str]) -> list[dict]:
    """Parse the extracted text into sections, each with its field entries.

    `lines` is the file split on newlines; every recorded line number is
    1-based, so a citation can be checked with a text editor.
    """
    start = 0
    for index, line in enumerate(lines):
        if line.strip() == DATA_DICTIONARY_MARKER:
            start = index + 1
            break

    titles: list[tuple[int, str]] = []
    tables: list[dict] = []
    in_table = False

    for offset, line in enumerate(lines[start:], start=start):
        number = offset + 1
        stripped = line.strip()
        if not stripped or PAGE_MARKER_RE.match(stripped):
            continue
        if TABLE_HEADER_RE.match(stripped):
            tables.append({"header_line": number, "entries": []})
            in_table = True
            continue
        if CONTENTS_ENTRY_RE.match(stripped):
            continue
        row = _split_row(stripped) if in_table else None
        if row is not None:
            field_name, description = row
            tables[-1]["entries"].append(
                {
                    "field_name": field_name,
                    "description": description,
                    "line": number,
                    "text": stripped[:MAX_SPAN_CHARS],
                }
            )
            continue
        if len(stripped) <= 60 and not stripped.endswith("."):
            titles.append((number, stripped))
            in_table = False

    if len(titles) != len(tables):
        raise ValueError(
            "Data-dictionary parse is ambiguous: "
            f"{len(titles)} section titles but {len(tables)} field tables. "
            "Titles and tables are paired in document order, so unequal counts "
            "mean the pairing would be wrong. Stop and report."
        )

    return [
        {
            "title": title,
            "title_line": title_line,
            "title_text": title[:MAX_SPAN_CHARS],
            "header_line": table["header_line"],
            "entries": table["entries"],
        }
        for (title_line, title), table in zip(titles, tables)
    ]


def index_entries(sections: list[dict]) -> dict[str, list[tuple[int, dict]]]:
    """Map a case-folded field name to every (section index, entry) using it."""
    index: dict[str, list[tuple[int, dict]]] = {}
    for section_index, section in enumerate(sections):
        for entry in section["entries"]:
            index.setdefault(entry["field_name"].casefold(), []).append((section_index, entry))
    return index


def find_narrative_spans(lines: list[str], phrases: tuple[str, ...]) -> list[dict]:
    """Locate narrative evidence by searching for a phrase, not by line number."""
    spans = []
    for phrase in phrases:
        for offset, line in enumerate(lines):
            if phrase in line and not DOT_LEADER_RE.search(line):
                spans.append(
                    {"line": offset + 1, "text": line.strip()[:MAX_SPAN_CHARS], "kind": "narrative"}
                )
                break
    return spans


def states_unit_or_type(description: str) -> bool:
    return any(marker in description for marker in UNIT_MARKERS)


def states_scenario_or_horizon(description: str) -> bool:
    return any(marker in description for marker in SCENARIO_MARKERS)


def _entry_span(section: dict, entry: dict) -> dict:
    return {
        "line": entry["line"],
        "text": entry["text"],
        "kind": "field_entry",
        "section_title": section["title"],
        "section_title_line": section["title_line"],
    }


def _title_span(section: dict) -> dict:
    return {"line": section["title_line"], "text": section["title_text"], "kind": "section_title"}


def _name_level_match(column: str, entry_index: dict) -> tuple[str, list] | None:
    """Exact then case-insensitive match of the whole column name."""
    matches = entry_index.get(column.casefold())
    if not matches:
        return None
    if any(entry["field_name"] == column for _section, entry in matches):
        return "exact_name", matches
    return "case_insensitive", matches


def _affix_match(column: str, entry_index: dict) -> tuple[str, list, str] | None:
    """Longest dictionary field name that is a suffix or prefix of the column name.

    Returns (stem, matches, affix_kind). The stem is the part of the CSV name
    the dictionary does not account for --- the part that carries the variable
    identity in the CSV but not in the dictionary.
    """
    folded = column.casefold()
    best: tuple[str, list, str] | None = None
    best_field = ""
    for field, matches in entry_index.items():
        if len(folded) <= len(field) + 1:
            continue
        if folded.endswith("_" + field):
            stem = column[: len(column) - len(field) - 1]
            kind = "suffix"
        elif folded.startswith(field + "_"):
            stem = column[len(field) + 1 :]
            kind = "prefix"
        else:
            continue
        # Longest match wins: `mid85_hist` must beat the bare `hist` it contains.
        if len(field) > len(best_field):
            best, best_field = (stem, matches, kind), field
    return best


def _stem_prefix_candidate(column: str) -> tuple[str, str] | None:
    """Longest EXECUTOR-proposed stem that prefixes this column name.

    Used only when no field name matches: it turns "appears nowhere in the
    dictionary" into "the closest field in the section this stem probably names
    is X" for the columns whose spelling drifted from the dictionary's --- the
    seasonal names where the CSV writes `rcp85_mid_summer` for the dictionary's
    `RCP85_MIDC_SUMMER`, or truncates `spring` to `sprin`.
    """
    best: tuple[str, str] | None = None
    for stem, title in STEM_SECTION_CANDIDATES.items():
        if column.startswith(stem + "_") and (best is None or len(stem) > len(best[0])):
            best = (stem, title)
    return best


def _closest_entry(remainder: str, section: dict) -> dict | None:
    """The section's field name most similar to the unmatched part of the CSV name."""
    names = [entry["field_name"] for entry in section["entries"]]
    folded = [name.casefold() for name in names]
    close = difflib.get_close_matches(remainder.casefold(), folded, n=1, cutoff=0.6)
    if not close:
        return None
    return section["entries"][folded.index(close[0])]


def _narrative_match(column: str, lines: list[str]) -> tuple[list[dict], str] | None:
    for candidate in NARRATIVE_CANDIDATES:
        if column.startswith(candidate["applies_to_prefixes"]):
            spans = find_narrative_spans(lines, candidate["phrases"])
            if spans:
                return spans, candidate["label"]
    return None


def _descriptions_agree(matches: list) -> bool:
    return len({entry["description"] for _section, entry in matches}) == 1


def classify_column(
    index: int,
    column: str,
    sections: list[dict],
    entry_index: dict,
    lines: list[str],
) -> dict:
    """Return the coverage record for one column: rule, evidence, status, question."""
    record = {
        "index": index,
        "column": column,
        "match_rule": "none",
        "stem": None,
        "candidate_section": None,
        "candidate_section_source": None,
        "dictionary_evidence": [],
        "status": "structurally_observed_only",
        "open_question": None,
    }

    name_match = _name_level_match(column, entry_index)
    if name_match is not None:
        rule, matches = name_match
        record["match_rule"] = rule
        record["dictionary_evidence"] = [
            _entry_span(sections[section_index], entry) for section_index, entry in matches
        ]
        descriptions = {entry["description"] for _section, entry in matches}
        if not any(descriptions):
            record["status"] = "unresolved"
            record["open_question"] = (
                f"The dictionary lists a field named `{column}` "
                f"(line {matches[0][1]['line']}) with no description at all. "
                f"What does column index {index} hold, and in what unit?"
            )
            return record
        if not _descriptions_agree(matches):
            record["status"] = "unresolved"
            lines_cited = ", ".join(str(entry["line"]) for _section, entry in matches)
            record["open_question"] = (
                f"The dictionary has {len(matches)} entries named `{column}` with differing "
                f"descriptions (lines {lines_cited}). Which one applies to column index "
                f"{index}, and what is its unit?"
            )
            return record
        description = next(iter(descriptions))
        has_unit = states_unit_or_type(description)
        has_scenario = states_scenario_or_horizon(description) or IDENTIFIER_MARKER in description
        if has_unit and has_scenario:
            record["status"] = "verified_from_dictionary"
            return record
        record["status"] = "partially_resolved"
        missing = []
        if not has_unit:
            missing.append("a unit")
        if not has_scenario:
            missing.append("a scenario or time horizon")
        record["open_question"] = (
            f"The dictionary describes `{column}` (line {matches[0][1]['line']}) as "
            f"\"{description}\", which does not state {' or '.join(missing)}. "
            f"What is {' and '.join(missing)} for column index {index}?"
        )
        return record

    affix = _affix_match(column, entry_index)
    if affix is not None:
        stem, matches, affix_kind = affix
        record["match_rule"] = "prefix_or_stem"
        record["stem"] = stem
        candidate_title = STEM_SECTION_CANDIDATES.get(stem)
        chosen = None
        if candidate_title is not None:
            record["candidate_section"] = candidate_title
            record["candidate_section_source"] = (
                "EXECUTOR reading of the extracted text; the dictionary does not state "
                "that this CSV stem corresponds to this section"
            )
            chosen = next(
                (
                    (section_index, entry)
                    for section_index, entry in matches
                    if sections[section_index]["title"] == candidate_title
                ),
                None,
            )
        evidence_source = [chosen] if chosen is not None else matches
        record["dictionary_evidence"] = [
            _entry_span(sections[section_index], entry) for section_index, entry in evidence_source
        ]
        if chosen is not None:
            record["dictionary_evidence"].insert(0, _title_span(sections[chosen[0]]))

        if chosen is None:
            record["status"] = "unresolved"
            titles = "; ".join(
                f"\"{sections[section_index]['title']}\" (line {entry['line']})"
                for section_index, entry in matches
            )
            record["open_question"] = (
                f"Column index {index} `{column}` matches the dictionary field "
                f"`{column[len(stem) + 1:] if affix_kind == 'suffix' else column[: -len(stem) - 1]}` "
                f"in {len(matches)} section(s): {titles}. Which section describes this column, "
                f"and what is the meaning of the remaining name part `{stem}`?"
            )
            return record

        description = chosen[1]["description"]
        if not description:
            record["status"] = "unresolved"
            record["open_question"] = (
                f"Under the candidate section \"{candidate_title}\" the dictionary lists the "
                f"field matching column index {index} `{column}` at line {chosen[1]['line']} "
                "with no description. What does this column hold, and in what unit?"
            )
            return record
        record["status"] = "partially_resolved"
        record["open_question"] = (
            f"Does column index {index} `{column}` correspond to the dictionary field "
            f"`{chosen[1]['field_name']}` in section \"{candidate_title}\" (line "
            f"{chosen[1]['line']}), described as \"{description}\"? The dictionary does not "
            f"state that the CSV stem `{stem}` denotes that section, so the correspondence and "
            "the unit both need confirmation."
        )
        return record

    stem_candidate = _stem_prefix_candidate(column)
    if stem_candidate is not None:
        stem, candidate_title = stem_candidate
        section = next(s for s in sections if s["title"] == candidate_title)
        remainder = column[len(stem) + 1 :]
        closest = _closest_entry(remainder, section)
        record["match_rule"] = "manual_candidate"
        record["stem"] = stem
        record["candidate_section"] = candidate_title
        record["candidate_section_source"] = (
            "EXECUTOR reading of the extracted text; the dictionary lists no field of this name"
        )
        record["status"] = "unresolved"
        record["dictionary_evidence"] = [_title_span(section)]
        if closest is None:
            record["open_question"] = (
                f"Column index {index} `{column}` matches no dictionary field name. The nearest "
                f"candidate section is \"{candidate_title}\" (line {section['title_line']}), but "
                f"no field in it resembles `{remainder}`. Which field, if any, is this column?"
            )
            return record
        record["dictionary_evidence"].append(_entry_span(section, closest))
        record["open_question"] = (
            f"Column index {index} `{column}` matches no dictionary field name. Under the "
            f"candidate section \"{candidate_title}\" the closest field is "
            f"`{closest['field_name']}` (line {closest['line']}), described as "
            f"\"{closest['description']}\". Is `{remainder}` the same field under a different "
            "spelling, and if so what is this column's unit?"
        )
        return record

    narrative = _narrative_match(column, lines)
    if narrative is not None:
        spans, label = narrative
        record["match_rule"] = "manual_candidate"
        record["candidate_section"] = label
        record["candidate_section_source"] = (
            "EXECUTOR reading of the extracted text; the dictionary lists no field of this name"
        )
        record["dictionary_evidence"] = spans
        record["status"] = "partially_resolved"
        record["open_question"] = (
            f"Column index {index} `{column}` appears in no field table. The narrative section "
            f"\"{label}\" (line {spans[0]['line']}) is the only related passage. Does this column "
            "carry the values that passage defines, and what do the remaining parts of its name "
            "denote?"
        )
        return record

    record["open_question"] = (
        f"Column index {index} `{column}` appears nowhere in the data dictionary --- neither as a "
        "field name nor in the narrative. What is its source, its meaning, and its unit?"
    )
    return record


def build_coverage(columns: list[str], lines: list[str]) -> dict:
    """Coverage record for every column, plus the status summary."""
    sections = parse_dictionary(lines)
    entry_index = index_entries(sections)
    records = [
        classify_column(index, column, sections, entry_index, lines)
        for index, column in enumerate(columns)
    ]

    summary: dict[str, int] = {}
    for record in records:
        summary[record["status"]] = summary.get(record["status"], 0) + 1
    rules: dict[str, int] = {}
    for record in records:
        rules[record["match_rule"]] = rules.get(record["match_rule"], 0) + 1

    return {
        "n_columns": len(columns),
        "sections": [
            {
                "title": section["title"],
                "title_line": section["title_line"],
                "header_line": section["header_line"],
                "n_entries": len(section["entries"]),
            }
            for section in sections
        ],
        "status_counts": summary,
        "match_rule_counts": rules,
        "columns": records,
    }
