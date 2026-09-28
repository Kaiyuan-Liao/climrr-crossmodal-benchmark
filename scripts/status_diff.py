#!/usr/bin/env python3
"""M1-WP2 Phase C.3: every column status change since the WP1 baseline, and who caused it.

M1-WP2's first acceptance criterion is that **every status change from the WP1
baseline is tied to a specific authoritative answer, date, and provenance
record**. This script is how that is demonstrated rather than asserted: it reads
`artifacts/profiles/dictionary_coverage.json`, compares each column's `status`
against the `status_baseline_wp1` frozen at classification time, and prints the
rows that moved with the resolution record and decision number responsible.

Its output is what the WP2 report cites. With an empty
`data/metadata/resolutions.yaml` it prints no rows, which is the correct and
expected result until mentor answers arrive.

Since M1-WP3 (D-011) a status has a third possible source, weaker than both
others: an **inferred-candidate record** in
`data/metadata/inferred_candidates.yaml`, carrying column-specific reasoning and
dictionary spans for a meaning the dictionary never stated. Those columns appear
in the diff too, citing their IC-record rather than a resolution record, and the
per-column table says which of the two moved each column.

Five invariants are checked, and a violation fails the run:

1. no column changed status without naming at least one resolution record or
   inferred-candidate record;
2. no resolution record produced `verified_from_dictionary` --- that status is
   reserved for what the tracked dictionary states in its own words (D-009);
3. every resolution record cited by a column is one the coverage run actually
   applied;
4. no column at `inferred_candidate` reached it without citing an IC-record,
   and no column citing an IC-record holds any other status;
5. no column fell from `verified_from_dictionary` or `owner_confirmed` to
   `inferred_candidate` --- the weaker status never overrides a stronger one
   (D-011).

This script assigns no meaning. It compares two recorded statuses.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr.checksums import sha256_file  # noqa: E402
from climrr.dictionary import (  # noqa: E402
    IC_BLOCKING_STATUSES,
    INFERRED_CANDIDATE,
    VERIFIED_FROM_DICTIONARY,
)
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

COVERAGE_PATH = REPO_ROOT / "artifacts" / "profiles" / "dictionary_coverage.json"
OUT_PATH = REPO_ROOT / "artifacts" / "profiles" / "status_diff.md"


def collect_changes(coverage: dict) -> list[dict]:
    """Columns whose status differs from the WP1 baseline, in index order."""
    decision_by_record = {
        applied["id"]: applied["decision_ref"] for applied in coverage["resolutions_applied"]
    }
    changes = []
    for column in coverage["columns"]:
        if column["status"] == column["status_baseline_wp1"]:
            continue
        refs = column["resolution_refs"]
        # A column that gained `inferred_candidate` cites an IC-record instead
        # of a resolution record. Both routes are shown in one table so the
        # question "what moved this column, and on whose evidence?" has one
        # place to look.
        inferred_refs = column.get("inferred_candidate_refs") or []
        changes.append(
            {
                "index": column["index"],
                "column": column["column"],
                "from": column["status_baseline_wp1"],
                "to": column["status"],
                "resolution_refs": refs,
                "inferred_candidate_refs": inferred_refs,
                "decision_refs": [decision_by_record.get(ref, "UNKNOWN") for ref in refs]
                or (["D-011"] if inferred_refs else []),
                "resolved_section": column.get("resolved_section"),
            }
        )
    return changes


def check_invariants(coverage: dict, changes: list[dict]) -> list[str]:
    """Return one message per violated invariant; an empty list is a pass."""
    applied_ids = {applied["id"] for applied in coverage["resolutions_applied"]}
    violations = []

    unattributed = [
        change["index"]
        for change in changes
        if not change["resolution_refs"] and not change["inferred_candidate_refs"]
    ]
    if unattributed:
        violations.append(
            "columns changed status with neither a resolution record nor an "
            f"inferred-candidate record cited: {unattributed}"
        )

    invented = [
        change["index"]
        for change in changes
        if change["to"] == VERIFIED_FROM_DICTIONARY
    ]
    if invented:
        violations.append(
            f"columns reached {VERIFIED_FROM_DICTIONARY} through a resolution record, which "
            f"D-009 forbids: {invented}"
        )

    unknown = sorted(
        {
            ref
            for change in changes
            for ref in change["resolution_refs"]
            if ref not in applied_ids
        }
    )
    if unknown:
        violations.append(f"columns cite resolution records the coverage run did not apply: {unknown}")

    # D-011: `inferred_candidate` and an IC-record imply each other exactly.
    # A column at that status with no record would be an inference nobody wrote
    # down; a column citing a record while holding some other status would mean
    # the record had been applied and then quietly overwritten.
    uncited = [
        column["index"]
        for column in coverage["columns"]
        if column["status"] == INFERRED_CANDIDATE and not column.get("inferred_candidate_refs")
    ]
    if uncited:
        violations.append(
            f"columns hold {INFERRED_CANDIDATE} without citing an IC-record: {uncited}"
        )
    mismatched = [
        column["index"]
        for column in coverage["columns"]
        if column.get("inferred_candidate_refs") and column["status"] != INFERRED_CANDIDATE
    ]
    if mismatched:
        violations.append(
            f"columns cite an IC-record but do not hold {INFERRED_CANDIDATE}: {mismatched}"
        )
    demoted = [
        change["index"]
        for change in changes
        if change["to"] == INFERRED_CANDIDATE and change["from"] in IC_BLOCKING_STATUSES
    ]
    if demoted:
        violations.append(
            f"columns fell from a stronger status to {INFERRED_CANDIDATE}, which D-011 forbids: "
            f"{demoted}"
        )

    return violations


def render_markdown(coverage: dict, changes: list[dict]) -> str:
    baseline = coverage["status_counts_baseline_wp1"]
    current = coverage["status_counts"]
    statuses = sorted(set(baseline) | set(current))
    lines = [
        "# Column status changes since the M1-WP1 baseline",
        "",
        "Generated by `scripts/status_diff.py` from",
        f"`{coverage.get('data_path', 'the coverage report')}`'s coverage run. Never hand-edited.",
        "",
        f"- Coverage source: `{repo_relative(COVERAGE_PATH)}`",
        f"- Resolutions applied: **{coverage['n_resolutions']}**"
        f" (`{coverage.get('resolutions_path')}`, sha256 `{coverage.get('resolutions_sha256')}`)",
        f"- Inferred-candidate records applied: **{coverage.get('n_inferred_candidates', 0)}**"
        f" (`{coverage.get('inferred_candidates_path')}`, sha256"
        f" `{coverage.get('inferred_candidates_sha256')}`)",
        f"- Columns changed: **{len(changes)}** of {coverage['n_columns']}",
        "",
        "## Status counts",
        "",
        "| Status | WP1 baseline | Now | Change |",
        "| --- | ---: | ---: | ---: |",
    ]
    for status in statuses:
        before, after = baseline.get(status, 0), current.get(status, 0)
        delta = after - before
        lines.append(f"| `{status}` | {before} | {after} | {delta:+d} |")
    lines += [
        f"| **Total** | **{sum(baseline.values())}** | **{sum(current.values())}** | |",
        "",
        "## Resolution records applied",
        "",
    ]
    if coverage["resolutions_applied"]:
        lines += [
            "| Record | Date | Source | Questions | Decision | Confidence | To status | Columns |",
            "| --- | --- | --- | --- | --- | --- | --- | ---: |",
        ]
        for applied in coverage["resolutions_applied"]:
            lines.append(
                f"| `{applied['id']}` | {applied['date']} | {applied['source']} | "
                f"{', '.join(applied['question_ids']) or '—'} | {applied['decision_ref']} | "
                f"{applied['confidence']} | "
                f"{'— (records only)' if applied['status_to'] is None else '`' + applied['status_to'] + '`'} | "
                f"{applied['n_columns_changed']} |"
            )
    else:
        lines.append(
            "None. `data/metadata/resolutions.yaml` is empty --- no answer has arrived yet. "
            "The machinery is in place and inert, which is the intended M1-WP2a state."
        )
    lines += ["", "## Inferred-candidate records applied", ""]
    inferred = coverage.get("inferred_candidates_applied") or []
    if inferred:
        lines += [
            "Reasoned, column-specific interpretations (D-011). **Not verified and not "
            "owner-confirmed** --- each cites its own dictionary spans, reasoning and "
            "unresolved alternatives in `data/metadata/inferred_candidates.yaml`.",
            "",
            "| Record | Index | Column | Questions | Baseline status | Applied |",
            "| --- | ---: | --- | --- | --- | --- |",
        ]
        for applied in inferred:
            outcome = (
                "yes"
                if applied["applied"]
                else f"**no** --- blocked by `{applied['blocked_by_status']}`"
            )
            lines.append(
                f"| `{applied['id']}` | {applied['column_index']} | "
                f"`{applied['column_name']}` | "
                f"{', '.join(applied['question_ids']) or '—'} | "
                f"`{applied['status_before']}` | {outcome} |"
            )
    else:
        lines.append(
            "None. `data/metadata/inferred_candidates.yaml` holds no record --- no column "
            "has been interpreted by reasoning."
        )
    lines += ["", "## Per-column changes", ""]
    if changes:
        lines += [
            "| Index | Column | From | To | Record | Decision | Confirmed section |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
        for change in changes:
            record = ", ".join(change["resolution_refs"] + change["inferred_candidate_refs"])
            lines.append(
                f"| {change['index']} | `{change['column']}` | `{change['from']}` | "
                f"`{change['to']}` | {record} | "
                f"{', '.join(change['decision_refs'])} | {change['resolved_section'] or '—'} |"
            )
    else:
        lines.append("No column has moved from its WP1 baseline status.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", type=Path, default=COVERAGE_PATH)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    parser.add_argument(
        "--no-write", action="store_true", help="print only; do not write the markdown report"
    )
    args = parser.parse_args()

    if not args.coverage.is_file():
        print(
            f"FAIL: coverage report not found: {args.coverage}\n"
            "Run scripts/dictionary_coverage.py first.",
            file=sys.stderr,
        )
        return 2
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))

    missing_fields = [
        field
        for field in ("status_counts_baseline_wp1", "resolutions_applied", "n_resolutions")
        if field not in coverage
    ]
    if missing_fields:
        print(
            f"FAIL: {args.coverage} predates the M1-WP2 resolution machinery "
            f"(no {', '.join(missing_fields)}). Re-run scripts/dictionary_coverage.py.",
            file=sys.stderr,
        )
        return 2

    changes = collect_changes(coverage)
    violations = check_invariants(coverage, changes)

    baseline = coverage["status_counts_baseline_wp1"]
    current = coverage["status_counts"]
    print(f"  coverage report           : {repo_relative(args.coverage)}")
    print(f"  resolution records applied: {coverage['n_resolutions']}")
    print(f"  IC records applied        : {coverage.get('n_inferred_candidates', 0)}")
    print(f"  columns changed           : {len(changes)} of {coverage['n_columns']}")
    for status in sorted(set(baseline) | set(current)):
        before, after = baseline.get(status, 0), current.get(status, 0)
        print(f"    {status:<28}: {before:>4} -> {after:>4} ({after - before:+d})")
    for change in changes:
        record = ", ".join(change["resolution_refs"] + change["inferred_candidate_refs"])
        print(
            f"    [{change['index']:>3}] {change['column']}: {change['from']} -> {change['to']} "
            f"({record}; {', '.join(change['decision_refs'])})"
        )
    if not changes:
        print("    no column has moved from its WP1 baseline status")

    for violation in violations:
        print(f"FAIL: {violation}", file=sys.stderr)

    output_path = None
    if not args.no_write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(render_markdown(coverage, changes), encoding="utf-8")
        output_path = args.out
        print(f"  report                    : {repo_relative(args.out)}")

    passed = not violations
    record_path = write_run_record(
        "status_diff",
        result_summary={
            "coverage_path": repo_relative(args.coverage),
            "coverage_sha256": sha256_file(args.coverage),
            "resolutions_sha256": coverage.get("resolutions_sha256"),
            "resolutions_applied": coverage["n_resolutions"],
            "inferred_candidates_sha256": coverage.get("inferred_candidates_sha256"),
            "inferred_candidates_applied": coverage.get("n_inferred_candidates", 0),
            "columns_changed": len(changes),
            "changes": changes or "none",
            "baseline_status_counts": baseline,
            "current_status_counts": current,
            "invariant_violations": violations or "none",
        },
        passed=passed,
        data_path=args.coverage,
        data_sha256=sha256_file(args.coverage),
        output_path=output_path,
        config_snapshot={
            "coverage_path": repo_relative(args.coverage),
            "out_path": repo_relative(args.out) if output_path is not None else None,
        },
    )
    print(f"Run record: {repo_relative(record_path)}")
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
