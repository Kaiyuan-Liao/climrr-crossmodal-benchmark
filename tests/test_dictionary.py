"""Dictionary parsing, match rules, and the evidence discipline behind each status.

The fixture below is synthetic but reproduces the two layouts the real extracted
text actually has: a page where one title precedes one table, and a page where
*all* the titles precede *all* the tables. The second is why titles and tables
are paired in document order rather than by proximity.
"""

from __future__ import annotations

import pytest

from climrr.dictionary import (
    build_coverage,
    classify_column,
    find_narrative_spans,
    index_entries,
    parse_dictionary,
    states_scenario_or_horizon,
    states_unit_or_type,
)

FIXTURE = """\
Contents
Calculating Widget Classes ....................................................... 9
=== PAGE 1 ===
Calculating Widget Classes
Widgets are grouped into classes by percentile.
=== PAGE 2 ===
Data Dictionary
This document contains descriptions of all field names within the following variables.
1. Alpha Measure - Annual
2. Beta Measure - Annual
Alpha Measure - Annual
Field Name Description
Crossmodel Truncated name for "Crossmodel_CellName". Text ID for each cell in the polygon grid.
hist Alpha Value (°F) - Annual Average - Historical
rcp85_midc Alpha Value (°F) - Annual Average - Mid-Century RCP8.5
shared_field Alpha Value (°F) - Annual Average - Historical
lonely_field
rcp45_endc_ Spring Spring - Alpha Value (°F) - Annual Average - End-Century RCP4.5
=== PAGE 3 ===
Beta Measure - Annual
Gamma Measure - Annual
FIELD NAME DESCRIPTION
CROSSMODEL Truncated name for "Crossmodel_CellName". Text ID for each cell in the polygon grid.
HIST Beta Value (in) - Annual Total - Historical
SHARED_FIELD Beta Value (in) - Annual Total - Historical
Field Name Description
Crossmodel Truncated name for "Crossmodel_CellName". Text ID for each cell in the polygon grid.
gamma_only Gamma seasonal value
"""


@pytest.fixture
def lines():
    return FIXTURE.splitlines()


@pytest.fixture
def sections(lines):
    return parse_dictionary(lines)


@pytest.fixture
def entry_index(sections):
    return index_entries(sections)


def _classify(column, sections, entry_index, lines, index=0):
    return classify_column(index, column, sections, entry_index, lines)


# --- parsing -----------------------------------------------------------------


def test_three_titles_pair_with_three_tables_in_document_order(sections):
    assert [section["title"] for section in sections] == [
        "Alpha Measure - Annual",
        "Beta Measure - Annual",
        "Gamma Measure - Annual",
    ]


def test_a_page_whose_titles_all_precede_its_tables_is_paired_correctly(sections):
    """Proximity pairing would give the Gamma table to the Beta title."""
    gamma = sections[2]
    assert [entry["field_name"] for entry in gamma["entries"]] == ["Crossmodel", "gamma_only"]


def test_prose_and_numbered_contents_lines_are_not_titles(sections):
    titles = {section["title"] for section in sections}
    assert not any(title.startswith("This document") for title in titles)
    assert not any(title.startswith("1.") for title in titles)


def test_rows_are_recognised_by_underscore_or_a_bare_known_name(sections):
    alpha = {entry["field_name"] for entry in sections[0]["entries"]}
    assert {"Crossmodel", "hist", "rcp85_midc", "shared_field"} <= alpha


def test_a_field_name_split_before_a_season_is_rejoined(sections):
    names = {entry["field_name"] for entry in sections[0]["entries"]}
    assert "rcp45_endc_Spring" in names


def test_a_field_listed_with_no_description_is_kept_not_dropped(sections):
    entry = next(e for e in sections[0]["entries"] if e["field_name"] == "lonely_field")
    assert entry["description"] == ""


def test_line_numbers_are_one_based_and_point_at_the_quoted_line(sections, lines):
    entry = next(e for e in sections[0]["entries"] if e["field_name"] == "hist")
    assert lines[entry["line"] - 1].strip() == entry["text"]


def test_unequal_titles_and_tables_stop_the_parse(lines):
    broken = [line for line in lines if line != "Beta Measure - Annual"]
    with pytest.raises(ValueError, match="ambiguous"):
        parse_dictionary(broken)


# --- narrative spans ---------------------------------------------------------


def test_a_contents_line_with_dot_leaders_is_never_cited(lines):
    spans = find_narrative_spans(lines, ("Calculating Widget Classes",))
    assert len(spans) == 1
    assert "...." not in spans[0]["text"]
    assert lines[spans[0]["line"] - 1].strip() == "Calculating Widget Classes"


# --- marker predicates -------------------------------------------------------


@pytest.mark.parametrize(
    "description",
    ["Alpha Value (°F) - Annual", "Rain (in)", "Wind (mph)", "Number of days", "Text ID for a cell"],
)
def test_unit_markers_are_detected(description):
    assert states_unit_or_type(description)


def test_a_description_with_no_unit_is_not_credited_with_one():
    assert not states_unit_or_type("Seasonal value - Historical")


@pytest.mark.parametrize(
    "description", ["... Historical", "... Mid-Century RCP8.5", "... End-Century RCP4.5"]
)
def test_scenario_markers_are_detected(description):
    assert states_scenario_or_horizon(description)


# --- match rules -------------------------------------------------------------


def test_exact_name_match(sections, entry_index, lines):
    record = _classify("rcp85_midc", sections, entry_index, lines)
    assert record["match_rule"] == "exact_name"
    assert record["status"] == "verified_from_dictionary"
    assert record["dictionary_evidence"][0]["line"] > 0


def test_case_insensitive_match(sections, entry_index, lines):
    record = _classify("RCP85_MIDC", sections, entry_index, lines)
    assert record["match_rule"] == "case_insensitive"


def test_an_identifier_is_verified_without_a_scenario(sections, entry_index, lines):
    """`Text ID` is the dictionary's own words for a field that has no horizon."""
    record = _classify("Crossmodel", sections, entry_index, lines)
    assert record["status"] == "verified_from_dictionary"


def test_a_name_in_two_sections_with_different_descriptions_is_unresolved(
    sections, entry_index, lines
):
    record = _classify("shared_field", sections, entry_index, lines, index=7)
    # One section spells it exactly, the other in caps; an exact spelling
    # anywhere still names the rule, and both entries stay in the evidence.
    assert record["match_rule"] == "exact_name"
    assert record["status"] == "unresolved"
    assert "Which one applies to column index 7" in record["open_question"]
    assert len(record["dictionary_evidence"]) == 2


def test_a_field_with_a_blank_description_is_unresolved(sections, entry_index, lines):
    record = _classify("lonely_field", sections, entry_index, lines)
    assert record["status"] == "unresolved"
    assert "no description" in record["open_question"]


def test_a_description_missing_a_unit_is_only_partially_resolved(sections, entry_index, lines):
    record = _classify("gamma_only", sections, entry_index, lines, index=3)
    assert record["status"] == "partially_resolved"
    assert "a unit" in record["open_question"]
    assert "column index 3" in record["open_question"]


def test_a_stem_match_shows_the_stem_and_is_never_verified(sections, entry_index, lines):
    record = _classify("alphaann_rcp85_midc", sections, entry_index, lines)
    assert record["match_rule"] == "prefix_or_stem"
    assert record["stem"] == "alphaann"
    assert record["status"] != "verified_from_dictionary"


def test_an_ambiguous_stem_match_asks_which_section_applies(sections, entry_index, lines):
    record = _classify("someprefix_hist", sections, entry_index, lines, index=11)
    assert record["match_rule"] == "prefix_or_stem"
    assert record["status"] == "unresolved"
    assert "Which section describes this column" in record["open_question"]


def test_the_longest_matching_field_wins(sections, entry_index, lines):
    """`x_shared_field` must match `shared_field`, not the `hist` inside nothing."""
    record = _classify("x_shared_field", sections, entry_index, lines)
    assert record["stem"] == "x"


def test_an_unmatched_name_is_structurally_observed_only(sections, entry_index, lines):
    record = _classify("Shape_STLe", sections, entry_index, lines, index=274)
    assert record["match_rule"] == "none"
    assert record["status"] == "structurally_observed_only"
    assert record["dictionary_evidence"] == []
    assert "Column index 274" in record["open_question"]


# --- the discipline itself ---------------------------------------------------


def test_every_resolved_status_cites_at_least_one_span(sections, entry_index, lines):
    columns = ["Crossmodel", "hist", "gamma_only", "alphaann_rcp85_midc", "OID_", "shared_field"]
    for index, column in enumerate(columns):
        record = _classify(column, sections, entry_index, lines, index=index)
        if record["status"] != "structurally_observed_only":
            assert record["dictionary_evidence"], f"{column} has a status with no span"


def test_every_unverified_column_carries_a_question(sections, entry_index, lines):
    columns = ["gamma_only", "alphaann_rcp85_midc", "OID_", "shared_field", "lonely_field"]
    for index, column in enumerate(columns):
        record = _classify(column, sections, entry_index, lines, index=index)
        assert record["open_question"], f"{column} is unverified but asks nothing"


def test_spans_are_capped_in_length(sections, entry_index, lines):
    record = _classify("Crossmodel", sections, entry_index, lines)
    assert all(len(span["text"]) <= 300 for span in record["dictionary_evidence"])


def test_build_coverage_accounts_for_every_column_exactly_once(lines):
    columns = ["Crossmodel", "hist", "OID_", "alphaann_rcp85_midc"]
    coverage = build_coverage(columns, lines)
    assert coverage["n_columns"] == 4
    assert [record["index"] for record in coverage["columns"]] == [0, 1, 2, 3]
    assert sum(coverage["status_counts"].values()) == 4
    assert sum(coverage["match_rule_counts"].values()) == 4
