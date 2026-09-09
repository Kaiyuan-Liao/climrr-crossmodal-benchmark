"""The WP1-baseline diff: it must show every change, and refuse to show a false one.

`status_diff.py` is the evidence for M1-WP2's first acceptance criterion --- that
every status change since WP1 is tied to a specific answer and provenance
record. A diff that quietly under-reports would defeat that criterion while
appearing to satisfy it, so these tests are mostly about the three invariants it
refuses to pass over.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_script():
    path = REPO_ROOT / "scripts" / "status_diff.py"
    spec = importlib.util.spec_from_file_location("status_diff", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


status_diff = _load_script()


def coverage(columns: list[dict], applied: list[dict] | None = None) -> dict:
    return {
        "n_columns": len(columns),
        "n_resolutions": len(applied or []),
        "resolutions_applied": applied or [],
        "status_counts_baseline_wp1": {},
        "status_counts": {},
        "columns": columns,
    }


def column(index: int, name: str, baseline: str, now: str, refs: list[str] | None = None) -> dict:
    return {
        "index": index,
        "column": name,
        "status_baseline_wp1": baseline,
        "status": now,
        "resolution_refs": refs or [],
        "resolved_section": None,
    }


def applied_record(identifier: str = "R-001", decision: str = "D-010") -> dict:
    return {
        "id": identifier,
        "date": "2026-09-10",
        "source": "mentor",
        "decision_ref": decision,
        "confidence": "confirmed",
        "question_ids": ["Q1"],
        "status_to": "owner_confirmed",
        "columns_changed": [1],
        "n_columns_changed": 1,
    }


def test_an_unchanged_column_is_not_reported():
    report = coverage([column(0, "a", "unresolved", "unresolved")])
    assert status_diff.collect_changes(report) == []


def test_a_changed_column_carries_its_record_and_decision():
    report = coverage(
        [
            column(0, "a", "unresolved", "unresolved"),
            column(1, "b", "unresolved", "owner_confirmed", ["R-001"]),
        ],
        [applied_record()],
    )
    (change,) = status_diff.collect_changes(report)

    assert change["index"] == 1
    assert change["from"] == "unresolved"
    assert change["to"] == "owner_confirmed"
    assert change["resolution_refs"] == ["R-001"]
    assert change["decision_refs"] == ["D-010"]


def test_a_change_with_no_record_cited_is_a_violation():
    report = coverage([column(0, "a", "unresolved", "owner_confirmed")])
    changes = status_diff.collect_changes(report)
    (violation,) = status_diff.check_invariants(report, changes)
    assert "no resolution record cited" in violation


def test_a_change_into_verified_from_dictionary_is_a_violation():
    """No record may manufacture the dictionary-verified status (D-009)."""
    report = coverage(
        [column(0, "a", "partially_resolved", "verified_from_dictionary", ["R-001"])],
        [applied_record()],
    )
    changes = status_diff.collect_changes(report)
    violations = status_diff.check_invariants(report, changes)
    assert any("D-009 forbids" in violation for violation in violations)


def test_citing_a_record_the_run_never_applied_is_a_violation():
    report = coverage(
        [column(0, "a", "unresolved", "owner_confirmed", ["R-099"])],
        [applied_record()],
    )
    changes = status_diff.collect_changes(report)
    (violation,) = status_diff.check_invariants(report, changes)
    assert "R-099" in violation


def test_a_clean_diff_reports_no_violations():
    report = coverage(
        [
            column(0, "a", "unresolved", "unresolved"),
            column(1, "b", "unresolved", "owner_confirmed", ["R-001"]),
        ],
        [applied_record()],
    )
    changes = status_diff.collect_changes(report)
    assert status_diff.check_invariants(report, changes) == []


@pytest.mark.parametrize("applied", [[], [applied_record()]])
def test_the_markdown_renders_in_both_the_empty_and_the_populated_case(applied):
    report = coverage(
        [column(1, "b", "unresolved", "owner_confirmed", ["R-001"])] if applied else [],
        applied,
    )
    report["status_counts_baseline_wp1"] = {"unresolved": 1} if applied else {}
    report["status_counts"] = {"owner_confirmed": 1} if applied else {}
    text = status_diff.render_markdown(report, status_diff.collect_changes(report))

    assert text.startswith("# Column status changes since the M1-WP1 baseline")
    if applied:
        assert "`R-001`" in text and "D-010" in text
    else:
        assert "no answer has arrived yet" in text


def test_the_tracked_coverage_report_shows_no_unattributed_change():
    """The real artifact, as committed: currently zero changes and zero violations."""
    import json

    path = REPO_ROOT / "artifacts" / "profiles" / "dictionary_coverage.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    changes = status_diff.collect_changes(report)

    assert status_diff.check_invariants(report, changes) == []
