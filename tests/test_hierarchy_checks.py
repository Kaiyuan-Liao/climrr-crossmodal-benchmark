"""Phase A hierarchy checks: the structural counts, on a synthetic table.

The checks exist to say what "cell", "county" and "state" can mean in this file
*before* anything is aggregated. These tests therefore pin the two properties
that decide that --- whether the cell key is unique, and whether `GEOID`
determines the `(State, NAME)` label --- in both directions, so that a change
which silently turns a False into a True fails here.

Nothing here reads the real table. `tests/test_examples.py` and the run records
cover that; what is under test is the counting.
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "hierarchy_checks", REPO_ROOT / "scripts" / "hierarchy_checks.py"
)
hierarchy_checks = importlib.util.module_from_spec(_spec)
sys.modules["hierarchy_checks"] = hierarchy_checks
_spec.loader.exec_module(hierarchy_checks)

N_COLUMNS = 275


def _row(oid, crossmodel, name, state, geoid, name_1, namelsad, blanks=()):
    """One synthetic row: a filled pilot subset, then the label columns on top.

    The order matters. Four of the label columns --- `Crossmodel`, `NAME`,
    `State`, `GEOID` --- are themselves members of the pilot subset, so the
    filler has to go down first or it overwrites the labels these checks count.
    """
    from climrr.examples import PILOT_INDICES

    row = [""] * N_COLUMNS
    for index in PILOT_INDICES:
        row[index] = "" if index in blanks else "1.0"
    row[hierarchy_checks.OID_INDEX] = oid
    row[hierarchy_checks.CROSSMODEL_INDEX] = crossmodel
    row[hierarchy_checks.NAME_INDEX] = name
    row[hierarchy_checks.STATE_INDEX] = state
    row[hierarchy_checks.GEOID_INDEX] = geoid
    row[hierarchy_checks.NAME_1_INDEX] = name_1
    row[hierarchy_checks.NAMELSAD_INDEX] = namelsad
    return row


def _write(tmp_path: Path, rows) -> Path:
    path = tmp_path / "synthetic.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([f"c{i}" for i in range(N_COLUMNS)])
        writer.writerows(rows)
    return path


@pytest.fixture
def clean_table(tmp_path):
    """Three states, four `(State, NAME)` pairs, every `GEOID` inside one pair."""
    rows = [
        _row("1", "R1C1", "Stephens", "Oklahoma", "40137000902", "Oklahoma", "Stephens County"),
        _row("2", "R1C2", "Stephens", "Oklahoma", "40137000902", "Oklahoma", "Stephens County"),
        _row("3", "R1C3", "Garvin", "Oklahoma", "40049000100", "Oklahoma", "Garvin County"),
        _row("14", "R2C1", "San Bernardino", "California", "06071010300", "California", "SB County"),
        _row("15", "R2C2", "San Bernardino", "California", "06071010400", "California", "SB County"),
        _row("16", "R2C3", "Kern", "California", "06029000100", "California", "Kern County"),
        _row("17", "R3C1", "District of Columbia", "", "11001000300", "DC", "DC"),
    ]
    return _write(tmp_path, rows)


def test_crossmodel_uniqueness_is_reported_true_when_it_holds(clean_table):
    check = hierarchy_checks.run_checks(clean_table)["check_1_crossmodel_uniqueness"]
    assert check["is_unique"] == "True"
    assert check["n_distinct"] == check["n_rows"] == "7"
    assert check["n_duplicated_values"] == "0"


def test_crossmodel_uniqueness_is_reported_false_with_the_duplicate_named(tmp_path):
    """A repeated cell key must surface as the value and its count, not as a flag.

    A1 and A-G0 both rest on this: if two rows share a `Crossmodel`, "one row is
    one grid cell" is refuted by the file and the prototypes have to say so.
    """
    rows = [
        _row("1", "R1C1", "Stephens", "Oklahoma", "40137000902", "Oklahoma", "Stephens County"),
        _row("2", "R1C1", "Stephens", "Oklahoma", "40137000902", "Oklahoma", "Stephens County"),
        _row("14", "R2C1", "Kern", "California", "06029000100", "California", "Kern County"),
    ]
    check = hierarchy_checks.run_checks(_write(tmp_path, rows))["check_1_crossmodel_uniqueness"]
    assert check["is_unique"] == "False"
    assert check["n_duplicated_values"] == "1"
    assert check["duplicated_values"] == {"R1C1": "2"}


def test_rows_per_state_name_pair_and_the_two_focus_pairs(clean_table):
    check = hierarchy_checks.run_checks(clean_table)["check_2_rows_per_state_name_pair"]
    assert check["n_keys"] == "5"
    assert check["min"] == "1"
    assert check["max"] == "2"
    assert check["total_rows"] == "7"
    assert check["focus_pair_OID_1"] == {"State": "Oklahoma", "NAME": "Stephens", "n_rows": "2"}
    assert check["focus_pair_OID_14"] == {
        "State": "California",
        "NAME": "San Bernardino",
        "n_rows": "2",
    }


def test_geoid_consistency_is_true_when_every_geoid_sits_in_one_pair(clean_table):
    check = hierarchy_checks.run_checks(clean_table)["check_3_rows_per_geoid"]
    assert check["each_geoid_one_state_name_pair"] == "True"
    assert check["n_geoid_spanning_multiple_state_name_pairs"] == "0"


def test_a_geoid_spanning_two_pairs_is_reported_with_both_pairs(tmp_path):
    """The finding that decides whether `GEOID` can key a county. It cannot here."""
    rows = [
        _row("1", "R1C1", "Baldwin", "Alabama", "01003010400", "Alabama", "Baldwin County"),
        _row("2", "R1C2", "Escambia", "Florida", "01003010400", "Alabama", "Baldwin County"),
        _row("14", "R2C1", "Kern", "California", "06029000100", "California", "Kern County"),
    ]
    check = hierarchy_checks.run_checks(_write(tmp_path, rows))["check_3_rows_per_geoid"]
    assert check["each_geoid_one_state_name_pair"] == "False"
    assert check["n_geoid_spanning_multiple_state_name_pairs"] == "1"
    assert check["geoid_spanning_multiple_state_name_pairs"]["01003010400"] == [
        "Alabama\tBaldwin",
        "Florida\tEscambia",
    ]


def test_name_1_and_namelsad_are_reported_as_functions_of_geoid(clean_table):
    check = hierarchy_checks.run_checks(clean_table)["check_4_name1_namelsad_by_geoid"]
    assert check["NAME_1_is_function_of_geoid"] == "True"
    assert check["NAMELSAD_is_function_of_geoid"] == "True"


def test_a_second_name_1_under_one_geoid_is_counted(tmp_path):
    rows = [
        _row("1", "R1C1", "Baldwin", "Alabama", "01003010400", "Alabama", "Baldwin County"),
        _row("2", "R1C2", "Baldwin", "Alabama", "01003010400", "Florida", "Baldwin County"),
        _row("14", "R2C1", "Kern", "California", "06029000100", "California", "Kern County"),
    ]
    check = hierarchy_checks.run_checks(_write(tmp_path, rows))["check_4_name1_namelsad_by_geoid"]
    assert check["NAME_1_is_function_of_geoid"] == "False"
    assert check["NAME_1_n_geoid_with_more_than_one_value"] == "1"
    assert check["NAMELSAD_is_function_of_geoid"] == "True"


def test_rows_with_empty_state_are_listed_with_their_other_labels(clean_table):
    check = hierarchy_checks.run_checks(clean_table)["check_5_rows_with_empty_state"]
    assert check["n_rows"] == "1"
    assert check["rows"] == [
        {
            "OID_": "17",
            "Crossmodel": "R3C1",
            "NAME": "District of Columbia",
            "GEOID": "11001000300",
        }
    ]


def test_focus_coverage_counts_rows_and_blank_pilot_columns(tmp_path):
    """Coverage is per pilot column, and a fully populated set reports nothing."""
    rows = [
        _row("1", "R1C1", "Stephens", "Oklahoma", "40137000902", "Oklahoma", "Stephens County"),
        _row(
            "2",
            "R1C2",
            "Stephens",
            "Oklahoma",
            "40137000902",
            "Oklahoma",
            "Stephens County",
            blanks=(241,),
        ),
        _row("3", "R1C3", "Garvin", "Oklahoma", "40049000100", "Oklahoma", "Garvin County"),
        _row("14", "R2C1", "Kern", "California", "06029000100", "California", "Kern County"),
    ]
    check = hierarchy_checks.run_checks(_write(tmp_path, rows))["check_6_focus_coverage"]
    assert check["state_of_OID_1"]["n_rows"] == "3"
    assert check["state_of_OID_1"]["empty_pilot_columns"] == {
        "241": {"n_empty": "1", "of_n_rows": "3"}
    }
    assert check["state_name_pair_of_OID_1"]["n_rows"] == "2"
    assert check["state_name_pair_of_OID_1"]["empty_pilot_columns"] == {
        "241": {"n_empty": "1", "of_n_rows": "2"}
    }
    assert check["state_of_OID_14"] == {"State": "California", "n_rows": "1"}


def test_a_missing_focus_row_is_a_finding_not_an_empty_result(tmp_path):
    rows = [_row("1", "R1C1", "Stephens", "Oklahoma", "40137000902", "OK", "Stephens County")]
    with pytest.raises(hierarchy_checks.HierarchyError, match="OID_"):
        hierarchy_checks.run_checks(_write(tmp_path, rows))


def test_every_reported_value_is_a_string(clean_table):
    """The charter's rule for identifiers, applied to the whole report."""
    result = hierarchy_checks.run_checks(clean_table)

    def walk(node):
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        else:
            assert isinstance(node, str), f"non-string value in the report: {node!r}"

    walk(result)
