"""Resolution records: what may move a column status after M1-WP1, and what may not.

The machinery these tests guard exists to answer one question about any status
in `dictionary_coverage.json`: **who said so, and when?** Its value is entirely
in what it refuses --- a record that reaches a column it never named, or that
manufactures `verified_from_dictionary` out of a conversation, would be worse
than no machinery at all, because it would look traceable while not being so.

The fixture is a four-field synthetic dictionary, deliberately smaller than the
one in `test_dictionary.py`: these tests are about resolutions, not parsing.
"""

from __future__ import annotations

import pytest

from climrr.dictionary import (
    OWNER_CONFIRMED,
    VERIFIED_FROM_DICTIONARY,
    ResolutionError,
    apply_resolutions,
    build_coverage,
    load_resolutions,
    resolution_targets,
    validate_resolution,
)

FIXTURE = """\
Data Dictionary
Alpha Measure - Annual
Field Name Description
Crossmodel Truncated name for "Crossmodel_CellName". Text ID for each cell in the polygon grid.
hist Alpha Value (°F) - Annual Average - Historical
rcp85_midc Alpha Value (°F) - Annual Average - Mid-Century RCP8.5
"""

#: index 0 and 1 verify from the dictionary; 2 and 3 carry the stems `alpha` and
#: `beta`; 4 matches nothing at all.
COLUMNS = ["Crossmodel", "hist", "alpha_rcp85_midc", "beta_rcp85_midc", "mystery_col"]

VALID = {
    "id": "R-001",
    "date": "2026-09-10",
    "source": "mentor",
    "source_detail": "Weekly one-on-one, 2026-09-10, relayed by Kaiyuan Liao",
    "question_ids": ["Q1"],
    "columns": [2, 3],
    "statement": "Both of those columns are the Alpha layer's mid-century RCP8.5 field.",
    "effect": {"field": "status", "to": OWNER_CONFIRMED},
    "decision_ref": "D-010",
    "confidence": "confirmed",
}


def record(**overrides) -> dict:
    return {**VALID, **overrides}


@pytest.fixture
def lines():
    return FIXTURE.splitlines()


@pytest.fixture
def baseline(lines):
    """The coverage with no resolutions at all --- the WP1 behaviour."""
    return build_coverage(COLUMNS, lines)


def statuses(coverage: dict) -> list[str]:
    return [column["status"] for column in coverage["columns"]]


# --- the fixture behaves as the tests below assume ---------------------------


def test_the_fixture_gives_two_verified_two_stemmed_and_one_unmatched(baseline):
    assert statuses(baseline) == [
        VERIFIED_FROM_DICTIONARY,
        VERIFIED_FROM_DICTIONARY,
        "unresolved",
        "unresolved",
        "structurally_observed_only",
    ]
    assert [column["stem"] for column in baseline["columns"]] == [
        None,
        None,
        "alpha",
        "beta",
        None,
    ]


def test_with_no_resolutions_the_baseline_and_current_status_agree(baseline):
    for column in baseline["columns"]:
        assert column["status"] == column["status_baseline_wp1"]
        assert column["resolution_refs"] == []
        assert column["resolved_section"] is None
    assert baseline["status_counts"] == baseline["status_counts_baseline_wp1"]
    assert baseline["n_resolutions"] == 0
    assert baseline["resolutions_applied"] == []


# --- what a record does when it names columns --------------------------------


def test_a_record_naming_two_columns_changes_exactly_those_two(lines):
    coverage = build_coverage(COLUMNS, lines, [record(columns=[2, 3])])

    assert statuses(coverage) == [
        VERIFIED_FROM_DICTIONARY,
        VERIFIED_FROM_DICTIONARY,
        OWNER_CONFIRMED,
        OWNER_CONFIRMED,
        "structurally_observed_only",
    ]
    changed = [column["index"] for column in coverage["columns"] if column["resolution_refs"]]
    assert changed == [2, 3]
    assert coverage["resolutions_applied"][0]["columns_changed"] == [2, 3]


def test_a_changed_column_keeps_its_wp1_baseline_and_cites_the_record(lines):
    coverage = build_coverage(COLUMNS, lines, [record(columns=[2])])
    column = coverage["columns"][2]

    assert column["status"] == OWNER_CONFIRMED
    assert column["status_baseline_wp1"] == "unresolved"
    assert column["resolution_refs"] == ["R-001"]


def test_the_executor_candidate_map_is_left_untouched_by_a_resolution(lines):
    """A confirmed section is recorded separately; the candidate stays a candidate."""
    coverage = build_coverage(
        COLUMNS, lines, [record(columns=[], stem_section_map={"alpha": "Alpha Measure - Annual"})]
    )
    column = coverage["columns"][2]

    assert column["resolved_section"] == "Alpha Measure - Annual"
    assert column["resolved_section_source"] == "R-001"
    assert column["candidate_section"] is None
    assert column["candidate_section_source"] is None


# --- what a record does when it names nothing --------------------------------


def test_a_record_naming_no_columns_and_no_stem_map_changes_nothing(lines, baseline):
    """The central refusal: an answer that names nothing reaches nothing.

    Matching the *text* of a statement against column names is exactly the
    pattern-guessing D-009 forbids, so an answer this specific about Alpha
    still moves no column until someone writes down which columns it means.
    """
    coverage = build_coverage(
        COLUMNS,
        lines,
        [
            record(
                columns=[],
                statement="The alpha columns are all mid-century RCP8.5 values in degrees F.",
            )
        ],
    )

    assert statuses(coverage) == statuses(baseline)
    assert all(column["resolution_refs"] == [] for column in coverage["columns"])
    assert coverage["resolutions_applied"][0]["columns_changed"] == []
    assert coverage["resolutions_applied"][0]["n_columns_changed"] == 0


def test_a_record_naming_nothing_is_still_valid_and_still_recorded(lines):
    """Worth recording without moving a status --- not an error."""
    coverage = build_coverage(COLUMNS, lines, [record(columns=[])])
    assert coverage["n_resolutions"] == 1
    assert coverage["resolutions_applied"][0]["id"] == "R-001"


# --- the stem route ----------------------------------------------------------


def test_a_stem_map_reaches_exactly_the_columns_carrying_that_stem(lines):
    coverage = build_coverage(
        COLUMNS, lines, [record(columns=[], stem_section_map={"alpha": "Alpha Measure - Annual"})]
    )

    assert coverage["columns"][2]["status"] == OWNER_CONFIRMED
    assert coverage["columns"][3]["status"] == "unresolved"
    assert coverage["resolutions_applied"][0]["columns_changed"] == [2]


def test_a_stem_no_column_carries_is_an_error_not_a_silent_no_op(baseline):
    with pytest.raises(ResolutionError, match="which no column in this table carries"):
        resolution_targets(
            record(columns=[], stem_section_map={"gamma": "Gamma Measure"}),
            baseline["columns"],
        )


def test_a_column_index_past_the_end_of_the_table_is_an_error(baseline):
    with pytest.raises(ResolutionError, match="the table has 5 columns"):
        resolution_targets(record(columns=[99]), baseline["columns"])


def test_the_two_routes_combine_without_double_counting(lines):
    coverage = build_coverage(
        COLUMNS,
        lines,
        [record(columns=[2, 4], stem_section_map={"alpha": "Alpha Measure - Annual"})],
    )
    assert coverage["resolutions_applied"][0]["columns_changed"] == [2, 4]
    assert coverage["columns"][2]["resolution_refs"] == ["R-001"]


# --- verified_from_dictionary is unreachable ---------------------------------


def test_a_record_may_never_produce_verified_from_dictionary():
    with pytest.raises(ResolutionError, match="may never be `verified_from_dictionary`"):
        validate_resolution(record(effect={"field": "status", "to": VERIFIED_FROM_DICTIONARY}))


def test_the_refusal_survives_loading_a_file(lines):
    text = """\
schema_version: 1
resolutions:
  - id: R-001
    date: 2026-09-10
    source: mentor
    source_detail: "Weekly one-on-one, 2026-09-10"
    question_ids: [Q1]
    columns: [2]
    statement: "Yes, that is the Alpha layer field."
    effect:
      field: status
      to: verified_from_dictionary
    decision_ref: D-010
    confidence: confirmed
"""
    with pytest.raises(ResolutionError, match="may never be `verified_from_dictionary`"):
        load_resolutions(text)


def test_no_applied_record_can_raise_the_verified_count(lines, baseline):
    """Whatever a record does, it cannot add to the dictionary-verified set."""
    coverage = build_coverage(
        COLUMNS, lines, [record(columns=[2, 3, 4], effect={"field": "status", "to": OWNER_CONFIRMED})]
    )
    before = baseline["status_counts"].get(VERIFIED_FROM_DICTIONARY, 0)
    after = coverage["status_counts"].get(VERIFIED_FROM_DICTIONARY, 0)
    assert after <= before


def test_only_the_status_field_may_be_changed():
    with pytest.raises(ResolutionError, match="`effect.field` must be `status`"):
        validate_resolution(record(effect={"field": "unit", "to": OWNER_CONFIRMED}))


# --- validation refuses what it cannot trace ---------------------------------


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"id": "R1"}, "must look like R-001"),
        ({"date": "10/09/2026"}, "must be an ISO date"),
        ({"source": "a colleague"}, "`source` must be one of"),
        ({"source_detail": "   "}, "may not be blank"),
        ({"statement": ""}, "may not be blank"),
        ({"confidence": "pretty sure"}, "`confidence` must be one of"),
        ({"decision_ref": "D10"}, "must look like D-009"),
        ({"question_ids": ["question 1"]}, "entries must look like Q1"),
        ({"columns": [2, 2]}, "lists an index twice"),
        ({"columns": ["2"]}, "must be non-negative integer indices"),
        ({"columns": [-1]}, "must be non-negative integer indices"),
        ({"effect": {"field": "status"}}, "exactly the keys field and to"),
        ({"effect": {"field": "status", "to": "nearly_sure"}}, "`effect.to` must be one of"),
        ({"stem_section_map": {"alpha": ""}}, "must name a dictionary section"),
    ],
)
def test_a_malformed_record_is_refused(overrides, message):
    with pytest.raises(ResolutionError, match=message):
        validate_resolution(record(**overrides))


def test_an_unknown_key_is_refused_rather_than_ignored():
    """A misspelled `columns` that silently did nothing is the worst failure mode."""
    with pytest.raises(ResolutionError, match="unknown key\\(s\\): colums"):
        validate_resolution({**record(), "colums": [2, 3]})


def test_a_missing_required_key_is_refused():
    incomplete = record()
    del incomplete["statement"]
    with pytest.raises(ResolutionError, match="missing required key\\(s\\): statement"):
        validate_resolution(incomplete)


def test_a_duplicate_record_id_is_refused():
    text = """\
schema_version: 1
resolutions:
  - id: R-001
    date: 2026-09-10
    source: mentor
    source_detail: "first"
    question_ids: []
    columns: []
    statement: "first answer"
    effect: {field: status, to: owner_confirmed}
    decision_ref: D-010
    confidence: confirmed
  - id: R-001
    date: 2026-09-11
    source: mentor
    source_detail: "second"
    question_ids: []
    columns: []
    statement: "second answer"
    effect: {field: status, to: owner_confirmed}
    decision_ref: D-011
    confidence: confirmed
"""
    with pytest.raises(ResolutionError, match="duplicate resolution id R-001"):
        load_resolutions(text)


def test_an_unquoted_yaml_date_is_accepted_and_normalised():
    """YAML turns an unquoted 2026-09-10 into a date object; requiring quotes would be a trap."""
    loaded = load_resolutions(
        """\
schema_version: 1
resolutions:
  - id: R-001
    date: 2026-09-10
    source: mentor
    source_detail: "Weekly one-on-one"
    question_ids: []
    columns: []
    statement: "an answer"
    effect: {field: status, to: owner_confirmed}
    decision_ref: D-010
    confidence: confirmed
"""
    )
    assert loaded[0]["date"] == "2026-09-10"


def test_a_timestamp_is_still_refused():
    """A resolution is dated to a day; a time of day is a sign something else went in."""
    import datetime as dt

    with pytest.raises(ResolutionError, match="must be an ISO date"):
        validate_resolution(record(date=dt.datetime(2026, 9, 10, 14, 30)))


def test_a_wrong_schema_version_is_refused():
    with pytest.raises(ResolutionError, match="`schema_version` must be 1"):
        load_resolutions("schema_version: 2\nresolutions: []\n")


def test_an_empty_or_absent_list_loads_as_no_resolutions():
    assert load_resolutions("schema_version: 1\nresolutions: []\n") == []
    assert load_resolutions("schema_version: 1\n") == []
    assert load_resolutions("") == []


# --- the tracked file itself -------------------------------------------------


def test_the_repository_resolutions_file_is_valid_and_currently_empty():
    """M1-WP2a ships the machinery inert. WP2b is what fills this file."""
    from climrr.paths import REPO_ROOT

    path = REPO_ROOT / "data" / "metadata" / "resolutions.yaml"
    assert path.is_file(), "the resolutions audit trail must be tracked, even when empty"
    assert load_resolutions(path.read_text(encoding="utf-8")) == []


# --- application order -------------------------------------------------------


def test_a_later_record_supersedes_an_earlier_one_and_both_are_cited(lines):
    """Records apply in file order, and the column keeps the whole chain."""
    first = record(id="R-001", columns=[2], effect={"field": "status", "to": OWNER_CONFIRMED})
    second = record(
        id="R-002",
        columns=[2],
        decision_ref="D-011",
        effect={"field": "status", "to": "partially_resolved"},
    )
    coverage = build_coverage(COLUMNS, lines, [first, second])
    column = coverage["columns"][2]

    assert column["status"] == "partially_resolved"
    assert column["resolution_refs"] == ["R-001", "R-002"]
    assert column["status_baseline_wp1"] == "unresolved"


def test_apply_resolutions_reports_what_each_record_did(baseline):
    applied = apply_resolutions(baseline["columns"], [record(columns=[2, 3])])
    assert applied == [
        {
            "id": "R-001",
            "date": "2026-09-10",
            "source": "mentor",
            "decision_ref": "D-010",
            "confidence": "confirmed",
            "question_ids": ["Q1"],
            "status_to": OWNER_CONFIRMED,
            "columns_changed": [2, 3],
            "n_columns_changed": 2,
        }
    ]
