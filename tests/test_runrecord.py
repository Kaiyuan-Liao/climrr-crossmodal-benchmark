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


# --- D-007: pinned parsing/profiling libraries -------------------------------


def test_pins_are_parsed_from_requirements(tmp_path):
    from climrr.runrecord import read_pins

    req = tmp_path / "requirements.txt"
    req.write_text(
        "# a comment\n"
        "pandas==3.0.5\n"
        "\n"
        "  numpy==2.4.6  # trailing comment\n"
        "unpinned-package\n"
        "ranged>=1.0\n",
        encoding="utf-8",
    )
    assert read_pins(req) == [("pandas", "3.0.5"), ("numpy", "2.4.6")]


def test_pinned_libraries_reports_match_and_mismatch(tmp_path):
    from climrr.runrecord import pinned_libraries

    req = tmp_path / "requirements.txt"
    req.write_text("pytest==0.0.0-not-a-real-version\nabsent-distribution==1.2.3\n", encoding="utf-8")
    entries = {e["name"]: e for e in pinned_libraries(req)}
    assert entries["pytest"]["matches_pin"] is False
    assert entries["pytest"]["imported_version"] not in ("", None)
    assert entries["absent-distribution"]["imported_version"] == "not installed"
    assert entries["absent-distribution"]["matches_pin"] is False


def test_pyyaml_pin_resolves_through_its_import_name(tmp_path):
    """pyyaml imports as `yaml`; the mapping is what makes its version readable."""
    from climrr.runrecord import pinned_libraries

    req = tmp_path / "requirements.txt"
    req.write_text("pyyaml==0.0.0\n", encoding="utf-8")
    entry = pinned_libraries(req)[0]
    assert entry["imported_version"] != "not installed"


def test_repo_requirements_pins_are_all_satisfied():
    """The environment this test runs in must match the D-007 pin set exactly."""
    from climrr.runrecord import pinned_libraries

    drift = [e for e in pinned_libraries() if not e["matches_pin"]]
    assert not drift, f"environment drifted from requirements.txt pins: {drift}"


def test_pinned_libraries_are_recorded_in_the_run_record(tmp_path):
    record = json.loads(_write(tmp_path).read_text(encoding="utf-8"))
    assert isinstance(record["pinned_libraries"], list)
    assert {"name", "pinned_version", "imported_version", "matches_pin"} <= set(
        record["pinned_libraries"][0]
    )
    assert "Pinned libraries (D-007)" in _write(tmp_path).with_suffix(".md").read_text(
        encoding="utf-8"
    )
