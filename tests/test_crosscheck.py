"""The pandas cross-check: it must detect a disagreement, not paper over one."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_script():
    path = REPO_ROOT / "scripts" / "crosscheck_profile_pandas.py"
    spec = importlib.util.spec_from_file_location("crosscheck_profile_pandas", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


crosscheck_module = _load_script()


@pytest.fixture
def frame():
    return pandas.DataFrame(
        {
            "geoid": ["01001", "01003", "06075", "12345"],
            "value": ["-9999", "1.5", "-9999", ""],
        },
        dtype=str,
    )


def _profile_for(frame):
    """The stdlib-side numbers that a correct Phase B profile would carry."""
    return {
        "n_rows": 4,
        "n_columns": 2,
        "columns": [
            {"index": 0, "name": "geoid", "n_empty": 0, "n_distinct": 4,
             "n_with_leading_zero_any": 3},
            {"index": 1, "name": "value", "n_empty": 1, "n_distinct": 3,
             "n_with_leading_zero_any": 0},
        ],
    }


def test_matching_counts_agree_on_every_column(frame):
    report = crosscheck_module.crosscheck(frame, _profile_for(frame))
    assert report["n_columns_disagree"] == 0
    assert report["n_columns_agree"] == 2
    assert all(check["agree"] for check in report["table_level_checks"])


def test_a_wrong_count_is_surfaced_as_a_disagreement(frame):
    profile = _profile_for(frame)
    profile["columns"][1]["n_empty"] = 0  # pandas will see 1
    report = crosscheck_module.crosscheck(frame, profile)
    assert report["n_columns_disagree"] == 1
    disagreement = report["disagreements"][0]
    assert disagreement["index"] == 1
    assert disagreement["fields"][0]["field"] == "n_empty"
    assert disagreement["fields"][0]["stdlib"] == 0
    assert disagreement["fields"][0]["pandas"] == 1


def test_a_renamed_column_is_surfaced_rather_than_matched_by_position_alone(frame):
    profile = _profile_for(frame)
    profile["columns"][0]["name"] = "GEOID"
    report = crosscheck_module.crosscheck(frame, profile)
    assert report["disagreements"][0]["fields"][0]["field"] == "name"


def test_leading_zero_counts_are_compared_under_both_readers(frame):
    """Criterion 4 evidence: a second parser must also see the zeros survive."""
    report = crosscheck_module.crosscheck(frame, _profile_for(frame))
    checks = {c["field"]: c for c in report["columns"][0]["checks"]}
    assert checks["n_with_leading_zero_any"]["pandas"] == 3
    assert checks["n_with_leading_zero_any"]["agree"] is True


def test_read_options_disable_type_inference_and_na_conversion():
    options = crosscheck_module.READ_OPTIONS
    assert options["dtype"] == "str"
    assert options["keep_default_na"] is False
    assert options["na_filter"] is False
    assert options["encoding"] == "utf-8-sig"
