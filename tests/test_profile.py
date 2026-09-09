"""The deterministic profile: matching rules, counting rules, and hash stability.

Every test here runs on a synthetic fixture. The real table is never touched:
these assert that the *rules* behave as the module docstring says they do, which
is what makes the profile of the real table interpretable at all.
"""

from __future__ import annotations

import csv
import json

import pytest

from climrr.profile import (
    DECIMAL_RE,
    INTEGER_RE,
    LEADING_ZERO_RE,
    build_profile,
    canonical_profile_bytes,
    duplicate_column_names,
    profile_content_hash,
    profile_column,
    profile_csv_rows,
    read_header,
)

# --- regex rules -------------------------------------------------------------

DECIMAL_ACCEPT = [
    "0",
    "007",  # a leading-zero integer is still a decimal numeral
    "-1",
    "+1",
    "1.5",
    "-2.75",
    "+0.001",
    "1.",  # digits with an empty fractional part
    ".5",  # bare fractional part
    "1e6",
    "1E6",
    "-2.5E-3",
    "+1.0e+10",
    "-9999",
    "0.0",
]

DECIMAL_REJECT = [
    "",  # blank is never a decimal; it is the empty case
    " ",
    "NA",
    "N/A",
    "null",
    "NULL",
    "None",
    "nan",  # Decimal() would parse it; a decimal numeral it is not
    "NaN",
    "inf",
    "-Infinity",
    "1,000",  # thousands separator
    "1 000",
    "--1",
    "1e",  # exponent marker with no exponent
    "e5",
    "1.2.3",
    "0x1F",
    "12abc",
    "abc",
    ".",
    "+",
    "1%",
    "1_000",
]


@pytest.mark.parametrize("value", DECIMAL_ACCEPT)
def test_decimal_regex_accepts(value):
    assert DECIMAL_RE.match(value), f"decimal regex should accept {value!r}"


@pytest.mark.parametrize("value", DECIMAL_REJECT)
def test_decimal_regex_rejects(value):
    assert not DECIMAL_RE.match(value), f"decimal regex should reject {value!r}"


@pytest.mark.parametrize("value", ["0", "007", "-1", "+42", "62834"])
def test_integer_regex_accepts(value):
    assert INTEGER_RE.match(value)


@pytest.mark.parametrize("value", ["", "1.0", "1e6", ".5", "1.", "NA", "1 "])
def test_integer_regex_rejects(value):
    assert not INTEGER_RE.match(value)


@pytest.mark.parametrize("value", ["01", "007", "01001", "06075", "00"])
def test_leading_zero_regex_accepts(value):
    assert LEADING_ZERO_RE.match(value)


@pytest.mark.parametrize("value", ["0", "1001", "-01", "+01", "0.5", "0x1", ""])
def test_leading_zero_regex_rejects(value):
    """`0` alone has no leading zero to lose, and a sign is not an identifier spelling."""
    assert not LEADING_ZERO_RE.match(value)


# --- per-column derivation ---------------------------------------------------


def test_empty_is_defined_by_strip_but_distinct_counts_use_raw_values():
    counts = {"": 2, "   ": 3, "1": 5}
    column = profile_column(0, "c", counts, n_rows=10)
    assert column["n_empty"] == 5
    assert column["n_nonempty"] == 5
    assert column["empty_rate"] == 0.5
    # "" and "   " are both empty but remain two distinct raw strings.
    assert column["n_distinct"] == 3
    assert column["n_distinct_nonempty"] == 1


def test_whitespace_padding_does_not_block_decimal_detection():
    column = profile_column(0, "c", {" 1.5 ": 1, "2": 1}, n_rows=2)
    assert column["all_nonempty_match_decimal"] is True
    assert column["min_decimal"] == " 1.5 "  # the raw spelling is what is reported
    assert column["max_decimal"] == "2"


def test_a_column_with_no_nonempty_values_is_not_called_decimal():
    """Vacuous truth would be a claim about a column that has no values at all."""
    column = profile_column(0, "c", {"": 4}, n_rows=4)
    assert column["all_nonempty_match_decimal"] is False
    assert column["all_nonempty_match_integer"] is False
    assert column["min_decimal"] is None
    assert column["min_len"] is None


def test_decimal_range_is_exact_and_not_float_rounded():
    counts = {"0.1": 1, "0.2": 1, "0.30000000000000004": 1, "9007199254740993": 1}
    column = profile_column(0, "c", counts, n_rows=4)
    assert column["all_nonempty_match_decimal"] is True
    assert column["min_decimal"] == "0.1"
    assert column["max_decimal"] == "9007199254740993"


def test_negative_and_zero_counts_are_over_rows_not_distinct_values():
    counts = {"-9999": 7, "-1": 2, "0": 3, "0.0": 4, "5": 1}
    column = profile_column(0, "c", counts, n_rows=17)
    assert column["n_negative"] == 9
    assert column["n_zero"] == 7  # "0" and "0.0" are numerically equal


def test_extreme_spelling_ties_break_lexicographically():
    """Two spellings of the same minimum must not let dict order pick the answer."""
    counts = {"-9999.0": 3, "-9999": 3, "1": 1}
    assert profile_column(0, "c", counts, n_rows=7)["min_decimal"] == "-9999"


def test_leading_zero_values_are_counted_and_never_coerced():
    counts = {"01001": 2, "01003": 1, "06075": 1, "12345": 6}
    column = profile_column(0, "geoid", counts, n_rows=10)
    assert column["all_nonempty_match_integer"] is True
    assert column["n_with_leading_zero"] == 4
    assert column["n_with_leading_zero_any"] == 4
    assert column["min_len"] == 5 and column["max_len"] == 5
    # The raw text survives into the reported values.
    assert {v["value"] for v in column["top5_values"]} >= {"01001", "12345"}


def test_leading_zero_count_is_reported_even_when_the_column_is_not_all_integer():
    counts = {"01001": 3, "not-a-number": 1}
    column = profile_column(0, "c", counts, n_rows=4)
    assert column["all_nonempty_match_integer"] is False
    assert column["n_with_leading_zero"] is None  # gated on the all-integer flag
    assert column["n_with_leading_zero_any"] == 3


# --- candidate sentinels -----------------------------------------------------


def test_candidate_sentinel_needs_both_extremeness_and_frequency():
    # 1000 rows; threshold at 0.5% is 5 occurrences.
    counts = {"-9999": 40, "-1": 4, "50": 952, "99999": 4}
    column = profile_column(0, "c", counts, n_rows=1000)
    values = [v["value"] for v in column["candidate_sentinel_values"]]
    assert values == ["-9999"]  # the max, 99999, is too rare to qualify
    assert column["candidate_sentinel_values"][0]["count"] == 40


def test_a_frequent_value_that_is_not_an_extreme_is_not_a_candidate():
    """The overwhelmingly common value here is 0, and being common is not enough."""
    counts = {"-1": 1, "0": 900, "100": 99}
    column = profile_column(0, "c", counts, n_rows=1000)
    values = [v["value"] for v in column["candidate_sentinel_values"]]
    assert "0" not in values
    assert values == ["100"]  # the max clears the rate; the min, at 1 row, does not


def test_both_extremes_can_qualify_and_are_ordered_by_count():
    counts = {"-9999": 100, "88": 700, "9999": 200}
    column = profile_column(0, "c", counts, n_rows=1000)
    assert [v["value"] for v in column["candidate_sentinel_values"]] == ["9999", "-9999"]


def test_non_decimal_columns_have_no_sentinel_candidates():
    """The rule is arithmetic; without a numeric extreme there is nothing to flag."""
    counts = {"alpha": 900, "beta": 100}
    assert profile_column(0, "c", counts, n_rows=1000)["candidate_sentinel_values"] == []


def test_sentinel_threshold_is_inclusive_at_the_rate():
    """Exactly 0.5% of rows qualifies; one row fewer does not."""
    at_threshold = profile_column(0, "c", {"-9999": 5, "1": 995}, n_rows=1000)
    below = profile_column(0, "c", {"-9999": 4, "1": 996}, n_rows=1000)
    assert "-9999" in [v["value"] for v in at_threshold["candidate_sentinel_values"]]
    assert "-9999" not in [v["value"] for v in below["candidate_sentinel_values"]]


# --- constancy, uniqueness, top values ---------------------------------------


def test_is_constant_ignores_empties_and_looks_unique_does_not_count_them():
    counts = {"CBURDI": 90, "": 10}
    column = profile_column(0, "c", counts, n_rows=100)
    assert column["is_constant"] is True
    assert column["looks_unique"] is False


def test_looks_unique_when_every_nonempty_value_occurs_once():
    counts = {"a": 1, "b": 1, "c": 1, "": 2}
    column = profile_column(0, "c", counts, n_rows=5)
    assert column["looks_unique"] is True


def test_top_values_are_ordered_by_count_then_value():
    counts = {"b": 5, "a": 5, "c": 9, "d": 1, "e": 1, "f": 1}
    top = [v["value"] for v in profile_column(0, "c", counts, n_rows=22)["top5_values"]]
    assert top == ["c", "a", "b", "d", "e"]


# --- header handling ---------------------------------------------------------


def test_duplicate_header_names_are_reported_by_ordinal_index():
    header = ["a", "b", "a", "c", "b", "a"]
    assert duplicate_column_names(header) == {"a": [0, 2, 5], "b": [1, 4]}


def test_no_duplicates_reports_an_empty_mapping():
    assert duplicate_column_names(["a", "b", "c"]) == {}


# --- end to end on a synthetic file ------------------------------------------

SYNTHETIC = (
    "geoid,dup,dup,value,label\n"
    "01001,a,x,-9999,alpha\n"
    "01003,b,y,1.5,beta\n"
    "06075,c,z,-9999,\n"
    "12345,d,w,2.25,delta\n"
)


@pytest.fixture
def synthetic_csv(tmp_path):
    path = tmp_path / "synthetic.csv"
    path.write_text(SYNTHETIC, encoding="utf-8", newline="")
    return path


def _build(path, **kwargs):
    defaults = dict(
        data_sha256="0" * 64,
        data_bytes=path.stat().st_size,
        data_path_label="tests/synthetic.csv",
        environment={"hostname": "test-host", "python_version": "0.0.0"},
    )
    defaults.update(kwargs)
    return build_profile(path, **defaults)


def test_end_to_end_shape_and_duplicate_reporting(synthetic_csv):
    profile = _build(synthetic_csv)
    assert profile["n_rows"] == 4
    assert profile["n_columns"] == 5
    assert profile["duplicate_column_names"] == {"dup": [1, 2]}
    # Duplicated names are kept verbatim, and the index is the key.
    assert [c["name"] for c in profile["columns"]] == ["geoid", "dup", "dup", "value", "label"]
    assert [c["index"] for c in profile["columns"]] == [0, 1, 2, 3, 4]
    assert profile["row_shape"]["n_rows_with_too_few_fields"] == 0
    assert profile["row_shape"]["n_rows_with_too_many_fields"] == 0


def test_end_to_end_preserves_leading_zeros(synthetic_csv):
    profile = _build(synthetic_csv)
    geoid = profile["columns"][0]
    assert geoid["all_nonempty_match_integer"] is True
    assert geoid["n_with_leading_zero"] == 3
    assert geoid["min_decimal"] == "01001"  # the text, not 1001
    assert {v["value"] for v in geoid["top5_values"]} == {"01001", "01003", "06075", "12345"}


def test_end_to_end_flags_a_repeated_extreme(synthetic_csv):
    profile = _build(synthetic_csv)
    value = profile["columns"][3]
    assert value["all_nonempty_match_decimal"] is True
    assert value["min_decimal"] == "-9999"
    # Four rows put the 0.5% threshold below one occurrence, so both extremes
    # qualify; the repeated minimum is the one that carries a count above 1.
    flagged = {v["value"]: v["count"] for v in value["candidate_sentinel_values"]}
    assert flagged["-9999"] == 2
    assert set(flagged) == {"-9999", "2.25"}


def test_utf8_bom_is_stripped_from_the_first_header_name_only_on_read(tmp_path):
    path = tmp_path / "bom.csv"
    path.write_bytes("﻿a,b\n1,2\n".encode("utf-8"))
    assert read_header(path) == ["a", "b"]
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")  # the file itself is untouched


def test_short_and_long_rows_are_counted_not_repaired(tmp_path):
    path = tmp_path / "ragged.csv"
    path.write_text("a,b,c\n1,2,3\n4,5\n6,7,8,9\n", encoding="utf-8", newline="")
    profile = _build(path)
    assert profile["row_shape"]["n_rows_with_too_few_fields"] == 1
    assert profile["row_shape"]["n_rows_with_too_many_fields"] == 1
    assert profile["row_shape"]["min_fields_per_row"] == 2
    assert profile["row_shape"]["max_fields_per_row"] == 4
    assert profile["columns"][2]["n_empty"] == 1  # the missing field, recorded as empty


# --- canonical hash ----------------------------------------------------------


def test_content_hash_is_stable_across_key_order(synthetic_csv):
    profile = _build(synthetic_csv)
    reordered = dict(reversed(list(profile.items())))
    reordered["columns"] = [dict(reversed(list(c.items()))) for c in profile["columns"]]
    assert profile_content_hash(reordered) == profile_content_hash(profile)


def test_content_hash_ignores_the_environment_block(synthetic_csv):
    profile = _build(synthetic_csv)
    other = _build(
        synthetic_csv,
        environment={"hostname": "sophia-login-02", "python_version": "3.13.13", "extra": [1, 2]},
    )
    assert profile_content_hash(other) == profile_content_hash(profile)
    assert b"sophia" not in canonical_profile_bytes(other)


def test_content_hash_changes_when_a_computed_fact_changes(synthetic_csv):
    profile = _build(synthetic_csv)
    mutated = json.loads(json.dumps(profile))
    mutated["columns"][0]["n_distinct"] += 1
    assert profile_content_hash(mutated) != profile_content_hash(profile)


def test_content_hash_changes_when_a_rule_constant_changes(synthetic_csv):
    profile = _build(synthetic_csv)
    other = _build(synthetic_csv, sentinel_min_rate=0.9)
    assert profile["sentinel_min_rate"] != other["sentinel_min_rate"]
    assert profile_content_hash(other) != profile_content_hash(profile)


def test_canonical_bytes_are_pure_ascii(synthetic_csv):
    """ASCII escaping keeps the hashed bytes independent of any encoding choice."""
    canonical_profile_bytes(_build(synthetic_csv)).decode("ascii")


# --- csv sibling -------------------------------------------------------------


def test_csv_sibling_has_one_row_per_column_and_a_header(synthetic_csv):
    profile = _build(synthetic_csv)
    rows = profile_csv_rows(profile)
    assert len(rows) == profile["n_columns"] + 1
    assert rows[0][0] == "index" and rows[0][1] == "name"
    assert rows[1][1] == "geoid"


def test_csv_sibling_writes_leading_zeros_as_text(tmp_path, synthetic_csv):
    from climrr.profile import write_profile_csv

    out = tmp_path / "profile.csv"
    write_profile_csv(out, _build(synthetic_csv))
    with out.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["min_decimal"] == "01001"
