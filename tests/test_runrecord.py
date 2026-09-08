"""Run-record schema and content."""

from __future__ import annotations

import json

import subprocess

from climrr.runrecord import (
    RUN_RECORD_SCHEMA,
    detect_location,
    git_dirty,
    untracked_file_count,
    write_run_record,
)


def _write(tmp_path, **kwargs):
    defaults = dict(result_summary={"checked": 1}, passed=True, runs_dir=tmp_path)
    defaults.update(kwargs)
    return write_run_record("unit", **defaults)


def test_record_has_every_required_field(tmp_path):
    path = _write(tmp_path)
    record = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in RUN_RECORD_SCHEMA if k not in record]
    assert not missing, f"run record missing required fields: {missing}"


def test_json_and_markdown_siblings_are_written(tmp_path):
    path = _write(tmp_path)
    md = path.with_suffix(".md")
    assert path.is_file() and md.is_file()
    assert path.stem == md.stem
    body = md.read_text(encoding="utf-8")
    assert "PASS" in body
    assert "pip freeze SHA-256" in body
    assert "Working tree dirty (tracked files)" in body
    assert "Untracked files present" in body


def test_dirty_flag_ignores_untracked_files(tmp_path):
    """An untracked stray file must not make a run record read as dirty.

    Regression: a stray .log beside the Sophia checkout reported dirty=True on
    an otherwise pristine pinned checkout, which is exactly the false alarm the
    flag exists to avoid.
    """
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert git_dirty() is bool(out.stdout.strip())


def test_untracked_count_matches_git(tmp_path):
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        text=True,
        check=True,
    )
    expected = sum(1 for line in out.stdout.splitlines() if line.startswith("??"))
    assert untracked_file_count() == expected


def test_untracked_count_is_recorded_as_an_integer(tmp_path):
    record = json.loads(_write(tmp_path).read_text(encoding="utf-8"))
    assert isinstance(record["untracked_files"], int)
    assert record["untracked_files"] >= 0


def test_filename_encodes_timestamp_location_and_name(tmp_path):
    path = _write(tmp_path)
    stem = path.stem
    stamp, location, name = stem.split("_", 2)
    assert stamp.endswith("Z") and len(stamp) == len("20260908T120000Z")
    assert location in {"local", "sophia"}
    assert name == "unit"


def test_failure_is_recorded_as_failure(tmp_path):
    path = _write(tmp_path, passed=False)
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["passed"] is False
    assert "FAIL" in path.with_suffix(".md").read_text(encoding="utf-8")


def test_data_hash_is_computed_when_not_supplied(tmp_path, tiny_csv):
    from climrr.checksums import sha256_file

    path = _write(tmp_path, data_path=tiny_csv)
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["data_sha256"] == sha256_file(tiny_csv)


def test_supplied_data_hash_is_not_recomputed(tmp_path, tiny_csv):
    path = _write(tmp_path, data_path=tiny_csv, data_sha256="deadbeef")
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["data_sha256"] == "deadbeef"


def test_paths_are_never_absolute(tmp_path, tiny_csv):
    """Run records are committed; absolute machine paths must not leak into them."""
    path = _write(tmp_path, data_path=tiny_csv, output_path=tiny_csv)
    record = json.loads(path.read_text(encoding="utf-8"))
    for key in ("data_path", "output_path"):
        assert not str(record[key]).startswith("/"), f"{key} leaked an absolute path"


def test_config_snapshot_round_trips(tmp_path):
    snapshot = {"data_path": "data/raw/FullData.csv", "mode": "read-only"}
    path = _write(tmp_path, config_snapshot=snapshot)
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["config_snapshot"] == snapshot


def test_detect_location_returns_a_known_label():
    assert detect_location() in {"local", "sophia"}
