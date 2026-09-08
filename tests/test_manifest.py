"""Manifest comparison, plus the real-data immutability assertion.

The immutability test is the M0 byte-identity gate in executable form: if the
tracked CSV ever stops matching data/manifest.json, this fails.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from climrr.checksums import byte_size, sha256_file  # noqa: E402
from smoke_test import compare_to_manifest, count_rows_and_columns, load_manifest_entry  # noqa: E402

MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"
RAW_CSV = REPO_ROOT / "data" / "raw" / "FullData.csv"


# --- comparison logic, exercised on the synthetic fixture -----------------

def test_load_manifest_entry(tiny_manifest):
    entry = load_manifest_entry(tiny_manifest, "tiny.csv")
    assert entry["row_count"] == 3
    assert entry["column_count"] == 3


def test_load_manifest_entry_missing_filename(tiny_manifest):
    with pytest.raises(KeyError):
        load_manifest_entry(tiny_manifest, "not_in_manifest.csv")


def test_compare_to_manifest_all_match(tiny_csv, tiny_manifest):
    expected = load_manifest_entry(tiny_manifest, "tiny.csv")
    rows, cols, _ = count_rows_and_columns(tiny_csv)
    observed = {
        "sha256": sha256_file(tiny_csv),
        "bytes": byte_size(tiny_csv),
        "row_count": rows,
        "column_count": cols,
    }
    checks = compare_to_manifest(observed, expected)
    assert [c["field"] for c in checks] == ["sha256", "bytes", "row_count", "column_count"]
    assert all(c["ok"] for c in checks)


def test_compare_to_manifest_detects_each_mismatch(tiny_csv, tiny_manifest):
    expected = load_manifest_entry(tiny_manifest, "tiny.csv")
    good = {
        "sha256": expected["sha256"],
        "bytes": expected["bytes"],
        "row_count": 3,
        "column_count": 3,
    }
    for field, bad_value in [
        ("sha256", "0" * 64),
        ("bytes", 999_999),
        ("row_count", 4),
        ("column_count", 2),
    ]:
        observed = dict(good, **{field: bad_value})
        checks = {c["field"]: c["ok"] for c in compare_to_manifest(observed, expected)}
        assert checks[field] is False, f"{field} mismatch not detected"
        assert all(ok for f, ok in checks.items() if f != field)


def test_count_rows_and_columns_excludes_header(tiny_csv):
    rows, cols, header = count_rows_and_columns(tiny_csv)
    assert (rows, cols) == (3, 3)
    assert header == ["geoid", "name", "value_hist"]


def test_count_handles_utf8_bom(tmp_path):
    """The real export carries a BOM; it must not become part of a column name."""
    path = tmp_path / "bom.csv"
    path.write_bytes("﻿a,b\n1,2\n".encode("utf-8"))
    rows, cols, header = count_rows_and_columns(path)
    assert (rows, cols) == (1, 2)
    assert header[0] == "a"


# --- the real data file: immutability gate --------------------------------

@pytest.mark.skipif(not RAW_CSV.is_file(), reason="data/raw/FullData.csv not present in this clone")
def test_tracked_csv_matches_manifest_hash():
    entry = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["files"][0]
    assert entry["filename"] == "FullData.csv"
    assert sha256_file(RAW_CSV) == entry["sha256"], (
        "data/raw/FullData.csv no longer matches data/manifest.json. "
        "The raw data is immutable: escalate, do not update the manifest."
    )
    assert byte_size(RAW_CSV) == entry["bytes"]


def test_manifest_lists_the_data_dictionary():
    files = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["files"]
    names = [f["filename"] for f in files]
    assert "ClimRR_Metadata_and_Data_Dictionary.pdf" in names


def test_manifest_records_no_interpretation():
    for entry in json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["files"]:
        assert "no interpretation assigned" in entry["interpretation_notes"]
