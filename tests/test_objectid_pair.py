"""The Q11.4 pair comparison: it must distinguish three different kinds of "same".

Row-wise equality, empty-row alignment, and value-set equality are three
separate questions, and on the real table they have three different answers.
A check that conflated any two of them would have reported "duplicates" or
"unrelated" where neither is true, so these tests pin each apart.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_script():
    path = REPO_ROOT / "scripts" / "check_objectid_pair.py"
    spec = importlib.util.spec_from_file_location("check_objectid_pair", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


check = _load_script()


@pytest.fixture
def csv_path(tmp_path):
    def write(rows: list[tuple[str, str]]) -> Path:
        path = tmp_path / "pair.csv"
        body = "".join(f"{left},{right}\n" for left, right in rows)
        path.write_text("a,b\n" + body, encoding="utf-8", newline="")
        return path

    return write


def test_identical_columns_are_reported_as_identical(csv_path):
    result = check.compare_columns(csv_path([("1", "1"), ("2", "2")]), 0, 1)
    assert result["n_differing"] == 0
    assert result["n_equal_as_text"] == 2
    assert result["value_sets_identical"] is True


def test_the_same_values_in_a_different_order_differ_row_wise_but_not_as_sets(csv_path):
    """A permutation: every row differs, yet nothing is missing from either side."""
    result = check.compare_columns(csv_path([("1", "2"), ("2", "1")]), 0, 1)
    assert result["n_differing"] == 2
    assert result["value_sets_identical"] is True
    assert result["n_values_only_in_left"] == 0


def test_different_value_sets_are_reported_as_different(csv_path):
    result = check.compare_columns(csv_path([("1", "3"), ("2", "4")]), 0, 1)
    assert result["value_sets_identical"] is False
    assert result["n_values_only_in_left"] == 2
    assert result["n_values_only_in_right"] == 2


def test_two_empty_values_count_as_equal_and_as_both_empty(csv_path):
    result = check.compare_columns(csv_path([("", ""), ("1", "1")]), 0, 1)
    assert result["n_both_empty"] == 1
    assert result["n_equal_as_text"] == 2
    assert result["empty_row_sets_identical"] is True


def test_an_empty_on_one_side_only_is_counted_on_that_side(csv_path):
    result = check.compare_columns(csv_path([("", "1"), ("2", "")]), 0, 1)
    assert result["n_only_left_empty"] == 1
    assert result["n_only_right_empty"] == 1
    assert result["empty_row_sets_identical"] is False
    assert result["n_differing"] == 2


def test_values_are_compared_as_raw_text_not_as_numbers(csv_path):
    """`01` and `1` are different identifiers, and coercion would hide that."""
    result = check.compare_columns(csv_path([("01", "1")]), 0, 1)
    assert result["n_differing"] == 1
    assert result["value_sets_identical"] is False


def test_whitespace_is_not_stripped_when_comparing_values(csv_path):
    result = check.compare_columns(csv_path([(" 1", "1")]), 0, 1)
    assert result["n_differing"] == 1


def test_differing_rows_are_quoted_up_to_the_cap(csv_path):
    rows = [(str(index), str(index + 1000)) for index in range(check.MAX_EXAMPLES + 3)]
    result = check.compare_columns(csv_path(rows), 0, 1)
    assert len(result["differing_examples"]) == check.MAX_EXAMPLES
    assert result["differing_examples"][0] == {"row": 1, "left": "0", "right": "1000"}


def test_a_short_row_contributes_an_empty_value_rather_than_raising(tmp_path):
    path = tmp_path / "ragged.csv"
    path.write_text("a,b\n1\n2,2\n", encoding="utf-8", newline="")
    result = check.compare_columns(path, 0, 1)
    assert result["n_rows"] == 2
    assert result["n_only_right_empty"] == 1
