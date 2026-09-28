"""Inferred candidates: the weakest status, and the refusals that keep it weak.

`inferred_candidate` exists because the 2026-09-10 mentor meeting established
that no further documentation exists (R-001) and gave no per-column answers
(R-002). Something had to carry a reasoned reading of a column. The danger the
GUIDANCE ruling names is that such a status quietly becomes ground truth, so
almost every test here is about what the machinery **refuses**:

* a record with no dictionary spans, or with no reasoning, is not a record;
* no resolution record may assign the status, and no IC-record may assign any
  other;
* the status never overwrites `verified_from_dictionary` or `owner_confirmed`;
* a record and the table must agree about which column is which.

The fixture is the same four-field synthetic dictionary `test_resolutions.py`
uses, for the same reason: these tests are about records, not about parsing.
"""

from __future__ import annotations

import pytest

from climrr.dictionary import (
    IC_DISCLAIMER,
    INFERRED_CANDIDATE,
    OWNER_CONFIRMED,
    VERIFIED_FROM_DICTIONARY,
    InferredCandidateError,
    ResolutionError,
    apply_inferred_candidates,
    build_coverage,
    load_inferred_candidates,
    validate_inferred_candidate,
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
    "id": "IC-001",
    "column_index": 4,
    "column_name": "mystery_col",
    "proposed_meaning": "An Alpha Value reading whose layer the dictionary does not name.",
    "proposed_unit": {"value": "degrees Fahrenheit", "provenance": "inferred"},
    "proposed_scenario": None,
    "proposed_horizon": None,
    "proposed_season": None,
    "dictionary_spans": [
        {"line": 5, "quote": "hist Alpha Value (°F) - Annual Average - Historical"}
    ],
    "name_evidence": "The name matches no field in the dictionary at all.",
    "value_evidence": {
        "range": "9.47 to 85.50",
        "emptiness": "no empty rows",
        "distinct": "58,542 distinct values",
    },
    "reasoning": "The only table in this fixture states degrees Fahrenheit for every field.",
    "alternatives_unresolved": ["It could belong to a layer the dictionary omits."],
    "assumptions": ["That the one table in the fixture covers this column."],
    "question_ids": ["Q1"],
    "status": INFERRED_CANDIDATE,
    "disclaimer": IC_DISCLAIMER,
}


def record(**overrides) -> dict:
    return {**VALID, **overrides}


@pytest.fixture
def lines():
    return FIXTURE.splitlines()


@pytest.fixture
def baseline(lines):
    return build_coverage(COLUMNS, lines)


def statuses(coverage: dict) -> list[str]:
    return [column["status"] for column in coverage["columns"]]


# --- the fixture, so a later failure is read correctly ------------------------


def test_the_fixture_baseline_is_unchanged_by_the_new_machinery(baseline):
    """Adding a third status source must not move a column on its own."""
    assert statuses(baseline) == [
        VERIFIED_FROM_DICTIONARY,
        VERIFIED_FROM_DICTIONARY,
        "unresolved",
        "unresolved",
        "structurally_observed_only",
    ]
    assert baseline["status_counts"] == baseline["status_counts_baseline_wp1"]
    assert baseline["n_inferred_candidates"] == 0
    assert all(column["inferred_candidate_refs"] == [] for column in baseline["columns"])


# --- what a record does -------------------------------------------------------


def test_a_record_moves_exactly_the_column_it_names(lines):
    coverage = build_coverage(COLUMNS, lines, None, [record()])

    assert statuses(coverage)[4] == INFERRED_CANDIDATE
    assert statuses(coverage)[:4] == statuses(build_coverage(COLUMNS, lines))[:4]


def test_a_changed_column_keeps_its_wp1_baseline_and_cites_the_record(lines):
    coverage = build_coverage(COLUMNS, lines, None, [record()])
    column = coverage["columns"][4]

    assert column["status_baseline_wp1"] == "structurally_observed_only"
    assert column["status"] == INFERRED_CANDIDATE
    assert column["inferred_candidate_refs"] == ["IC-001"]
    # The two audit trails stay separate: this column was not resolved.
    assert column["resolution_refs"] == []


def test_apply_reports_what_each_record_did(baseline):
    applied = apply_inferred_candidates(baseline["columns"], [record()])

    assert applied == [
        {
            "id": "IC-001",
            "column_index": 4,
            "column_name": "mystery_col",
            "question_ids": ["Q1"],
            "applied": True,
            "blocked_by_status": None,
            "status_before": "structurally_observed_only",
        }
    ]


def test_a_record_may_reach_an_unresolved_column(lines):
    """The stem columns are exactly where the real pilot's reasoning lives."""
    coverage = build_coverage(
        COLUMNS, lines, None, [record(column_index=2, column_name="alpha_rcp85_midc")]
    )

    assert coverage["columns"][2]["status"] == INFERRED_CANDIDATE
    assert coverage["columns"][2]["status_baseline_wp1"] == "unresolved"


def test_the_executor_candidate_map_is_left_untouched(lines):
    """`candidate_section` stays an EXECUTOR proposal; an IC-record is not a confirmation."""
    coverage = build_coverage(
        COLUMNS, lines, None, [record(column_index=2, column_name="alpha_rcp85_midc")]
    )
    column = coverage["columns"][2]

    assert column["resolved_section"] is None
    assert column["resolved_section_source"] is None


# --- never overriding a stronger status ---------------------------------------


@pytest.mark.parametrize("index", [0, 1])
def test_a_record_never_overwrites_verified_from_dictionary(lines, index):
    aimed = record(column_index=index, column_name=COLUMNS[index])
    coverage = build_coverage(COLUMNS, lines, None, [aimed])

    assert coverage["columns"][index]["status"] == VERIFIED_FROM_DICTIONARY
    assert coverage["columns"][index]["inferred_candidate_refs"] == []


def test_a_blocked_record_is_reported_rather_than_dropped(lines):
    coverage = build_coverage(COLUMNS, lines, None, [record(column_index=0, column_name="Crossmodel")])

    (applied,) = coverage["inferred_candidates_applied"]
    assert applied["applied"] is False
    assert applied["blocked_by_status"] == VERIFIED_FROM_DICTIONARY


def test_a_record_never_overwrites_owner_confirmed(lines):
    """A mentor answer outranks reasoning, whichever order the two files are written in."""
    resolution = {
        "id": "R-001",
        "date": "2026-09-10",
        "source": "mentor",
        "source_detail": "Weekly one-on-one, 2026-09-10",
        "question_ids": ["Q1"],
        "columns": [4],
        "statement": "That column is the Alpha layer's historical field.",
        "effect": {"field": "status", "to": OWNER_CONFIRMED},
        "decision_ref": "D-011",
        "confidence": "confirmed",
    }
    coverage = build_coverage(COLUMNS, lines, [resolution], [record()])

    assert coverage["columns"][4]["status"] == OWNER_CONFIRMED
    assert coverage["columns"][4]["resolution_refs"] == ["R-001"]
    assert coverage["columns"][4]["inferred_candidate_refs"] == []
    assert coverage["inferred_candidates_applied"][0]["blocked_by_status"] == OWNER_CONFIRMED


def test_no_record_can_raise_the_verified_count(lines, baseline):
    aimed = [
        record(id=f"IC-00{index + 1}", column_index=index, column_name=name)
        for index, name in enumerate(COLUMNS)
    ]
    coverage = build_coverage(COLUMNS, lines, None, aimed)

    before = baseline["status_counts"].get(VERIFIED_FROM_DICTIONARY, 0)
    assert coverage["status_counts"].get(VERIFIED_FROM_DICTIONARY, 0) == before


# --- the two statuses may not be reached through each other -------------------


def test_a_resolution_record_may_never_assign_inferred_candidate():
    with pytest.raises(ResolutionError, match="may never be `inferred_candidate`"):
        validate_resolution(
            {
                "id": "R-001",
                "date": "2026-09-10",
                "source": "mentor",
                "source_detail": "Weekly one-on-one, 2026-09-10",
                "question_ids": ["Q1"],
                "columns": [4],
                "statement": "Something the mentor said.",
                "effect": {"field": "status", "to": INFERRED_CANDIDATE},
                "decision_ref": "D-011",
                "confidence": "confirmed",
            }
        )


@pytest.mark.parametrize("status", [VERIFIED_FROM_DICTIONARY, OWNER_CONFIRMED, "partially_resolved"])
def test_an_ic_record_may_assign_no_other_status(status):
    with pytest.raises(InferredCandidateError, match="`status` must be the literal"):
        validate_inferred_candidate(record(status=status))


# --- the two refusals that carry the ruling -----------------------------------


def test_a_record_with_no_dictionary_spans_is_refused():
    with pytest.raises(InferredCandidateError, match="dictionary_spans` is empty"):
        validate_inferred_candidate(record(dictionary_spans=[]))


@pytest.mark.parametrize("blank", ["", "   ", "\n"])
def test_a_record_with_no_reasoning_is_refused(blank):
    with pytest.raises(InferredCandidateError, match="`reasoning` is empty"):
        validate_inferred_candidate(record(reasoning=blank))


def test_the_refusals_survive_loading_a_file():
    text = """\
schema_version: 1
inferred_candidates:
  - id: IC-001
    column_index: 4
    column_name: mystery_col
    proposed_meaning: Something.
    proposed_unit: null
    proposed_scenario: null
    proposed_horizon: null
    proposed_season: null
    dictionary_spans: []
    name_evidence: The name suggests it.
    value_evidence:
      range: "0 to 1"
      emptiness: none
      distinct: "2"
    reasoning: The name suggests it.
    alternatives_unresolved: []
    assumptions: []
    question_ids: [Q1]
    status: inferred_candidate
    disclaimer: not verified, not owner-confirmed
"""
    with pytest.raises(InferredCandidateError, match="dictionary_spans` is empty"):
        load_inferred_candidates(text)


# --- schema strictness --------------------------------------------------------


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"id": "IC-1"}, "must look like IC-001"),
        ({"id": "R-001"}, "must look like IC-001"),
        ({"column_index": -1}, "non-negative integer"),
        ({"column_index": "4"}, "non-negative integer"),
        ({"column_name": "  "}, "exact name"),
        ({"proposed_meaning": ""}, "proposed_meaning"),
        ({"name_evidence": ""}, "name_evidence"),
        ({"question_ids": ["Q1a"]}, "must look like Q1"),
        ({"alternatives_unresolved": "not a list"}, "must be a list"),
        ({"assumptions": [""]}, "must be a non-empty string"),
        ({"disclaimer": "unverified"}, "disclaimer` must read exactly"),
    ],
)
def test_a_malformed_record_is_refused(overrides, message):
    with pytest.raises(InferredCandidateError, match=message):
        validate_inferred_candidate(record(**overrides))


def test_an_unknown_key_is_refused_rather_than_ignored():
    """A misspelled field that silently does nothing is the failure mode this cannot afford."""
    with pytest.raises(InferredCandidateError, match="unknown key"):
        validate_inferred_candidate(record(propose_unit="°F"))


def test_a_missing_required_key_is_refused():
    incomplete = {key: value for key, value in VALID.items() if key != "reasoning"}
    with pytest.raises(InferredCandidateError, match="missing required key"):
        validate_inferred_candidate(incomplete)


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ({"value": "°F"}, "exactly the keys value and provenance"),
        ({"value": "", "provenance": "inferred"}, "must be a non-empty string"),
        ({"value": "°F", "provenance": "obvious"}, "provenance` must be one of"),
        ("°F", "must be null or a mapping"),
    ],
)
def test_a_tagged_field_must_say_which_kind_of_evidence_it_rests_on(field, message):
    with pytest.raises(InferredCandidateError, match=message):
        validate_inferred_candidate(record(proposed_unit=field))


def test_a_null_tagged_field_is_a_deliberate_do_not_know():
    validated = validate_inferred_candidate(record(proposed_unit=None))

    assert validated["proposed_unit"] is None


@pytest.mark.parametrize(
    ("span", "message"),
    [
        ({"line": 0, "quote": "x"}, "1-based line number"),
        ({"line": 5, "quote": "  "}, "verbatim"),
        ({"line": 5}, "exactly the keys line and quote"),
        ({"line": 5, "quote": "x", "page": 1}, "exactly the keys line and quote"),
    ],
)
def test_a_malformed_span_is_refused(span, message):
    with pytest.raises(InferredCandidateError, match=message):
        validate_inferred_candidate(record(dictionary_spans=[span]))


@pytest.mark.parametrize(
    "evidence",
    [
        {"range": "0 to 1", "emptiness": "none"},
        {"range": "0 to 1", "emptiness": "none", "distinct": "2", "mode": "0"},
        {"range": "0 to 1", "emptiness": "none", "distinct": ""},
    ],
)
def test_value_evidence_must_carry_all_three_facts(evidence):
    with pytest.raises(InferredCandidateError):
        validate_inferred_candidate(record(value_evidence=evidence))


def test_a_duplicate_record_id_is_refused():
    text = _file_text(VALID, {**VALID, "column_index": 3, "column_name": "beta_rcp85_midc"})
    with pytest.raises(InferredCandidateError, match="duplicate inferred-candidate id"):
        load_inferred_candidates(text)


def test_two_records_for_one_column_are_refused():
    """One column, one reasoning --- otherwise an example rests on an ambiguous record."""
    text = _file_text(VALID, {**VALID, "id": "IC-002"})
    with pytest.raises(InferredCandidateError, match="both reason about column index 4"):
        load_inferred_candidates(text)


def test_a_wrong_schema_version_is_refused():
    with pytest.raises(InferredCandidateError, match="`schema_version` must be 1"):
        load_inferred_candidates("schema_version: 2\ninferred_candidates: []\n")


def test_an_empty_or_absent_list_loads_as_no_records():
    assert load_inferred_candidates("schema_version: 1\n") == []
    assert load_inferred_candidates("schema_version: 1\ninferred_candidates:\n") == []
    assert load_inferred_candidates("") == []


# --- the record and the table must agree --------------------------------------


def test_a_column_index_past_the_end_of_the_table_is_an_error(baseline):
    with pytest.raises(InferredCandidateError, match="but the table has 5 columns"):
        apply_inferred_candidates(baseline["columns"], [record(column_index=99)])


def test_a_column_name_that_disagrees_with_the_table_is_an_error(baseline):
    with pytest.raises(InferredCandidateError, match="but the table has 'mystery_col'"):
        apply_inferred_candidates(baseline["columns"], [record(column_name="other_col")])


# --- the tracked file ---------------------------------------------------------


def _file_text(*records: dict) -> str:
    import yaml

    return yaml.safe_dump(
        {"schema_version": 1, "inferred_candidates": list(records)}, allow_unicode=True
    )


def test_the_repository_inferred_candidates_file_is_valid():
    from climrr.paths import REPO_ROOT

    path = REPO_ROOT / "data" / "metadata" / "inferred_candidates.yaml"
    records = load_inferred_candidates(path.read_text(encoding="utf-8"))

    assert len(records) == 20
    assert [r["id"] for r in records] == [f"IC-{n:03d}" for n in range(1, 21)]
    assert all(r["status"] == INFERRED_CANDIDATE for r in records)
    assert all(r["disclaimer"] == IC_DISCLAIMER for r in records)


def test_every_tracked_span_quotes_the_extracted_text_verbatim():
    """A span is a citation. A citation that does not match the cited line is worthless.

    Whitespace is normalised because the PDF extractor's line wrapping is not
    part of the quote; nothing else is.
    """
    import re

    from climrr.paths import REPO_ROOT

    lines = (
        (REPO_ROOT / "data" / "metadata" / "dictionary_extracted.txt")
        .read_text(encoding="utf-8")
        .splitlines()
    )
    records = load_inferred_candidates(
        (REPO_ROOT / "data" / "metadata" / "inferred_candidates.yaml").read_text(encoding="utf-8")
    )
    normalise = lambda text: re.sub(r"\s+", " ", text).strip()  # noqa: E731

    mismatches = [
        (record["id"], span["line"])
        for record in records
        for span in record["dictionary_spans"]
        if normalise(span["quote"]) not in normalise(lines[span["line"] - 1])
    ]
    assert mismatches == []


def test_no_tracked_record_reasons_about_a_column_the_dictionary_verifies():
    """Nothing in the pilot needs reasoning where the dictionary already speaks."""
    import json

    from climrr.paths import REPO_ROOT

    coverage = json.loads(
        (REPO_ROOT / "artifacts" / "profiles" / "dictionary_coverage.json").read_text(
            encoding="utf-8"
        )
    )
    blocked = [
        applied["id"]
        for applied in coverage["inferred_candidates_applied"]
        if not applied["applied"]
    ]
    assert blocked == []
    assert coverage["status_counts"][INFERRED_CANDIDATE] == 20
    assert coverage["status_counts"][VERIFIED_FROM_DICTIONARY] == 21


def test_the_coverage_report_pins_the_metadata_files_as_they_stand():
    """The report records the SHA-256 of the files it read. Those must be these files.

    Not a formality. A coverage report generated before a record was edited
    still *looks* current --- same counts, same column list --- while pinning
    bytes that no longer exist, so every status in it would cite reasoning that
    had since changed. Caught exactly that way once: the Phase A report pinned
    `inferred_candidates.yaml` as it was before a wording fix in Phase B, and
    nothing in the artifact said so.
    """
    import json

    from climrr.checksums import sha256_file
    from climrr.paths import REPO_ROOT

    coverage = json.loads(
        (REPO_ROOT / "artifacts" / "profiles" / "dictionary_coverage.json").read_text(
            encoding="utf-8"
        )
    )
    for key, relative in (
        ("inferred_candidates", "data/metadata/inferred_candidates.yaml"),
        ("resolutions", "data/metadata/resolutions.yaml"),
        ("extracted_text", "data/metadata/dictionary_extracted.txt"),
    ):
        assert coverage[f"{key}_path"] == relative
        assert coverage[f"{key}_sha256"] == sha256_file(REPO_ROOT / relative), (
            f"{relative} has changed since the coverage report was generated. "
            "Re-run scripts/dictionary_coverage.py."
        )
