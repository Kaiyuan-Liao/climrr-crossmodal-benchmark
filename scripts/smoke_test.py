#!/usr/bin/env python3
"""M0 smoke test: prove the raw CSV is present, unaltered, and readable.

Read-only by construction. It opens `data/raw/FullData.csv`, recomputes the
SHA-256 and byte size, counts rows and columns by streaming, and compares all
four against `data/manifest.json`. It writes nothing under `data/` -- its only
output is a run record under `reports/runs/`.

No column is interpreted, renamed, filtered or typed. Column names are read as
opaque strings.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr.checksums import byte_size, sha256_file  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

DATA_PATH = REPO_ROOT / "data" / "raw" / "FullData.csv"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"

# csv fields in this export can be long; raise the limit rather than fail late.
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def count_rows_and_columns(path: Path) -> tuple[int, int, list[str]]:
    """Stream the CSV once. Returns (data_row_count, column_count, header).

    utf-8-sig strips the byte-order mark from the first header name without
    touching the file on disk.
    """
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return 0, 0, []
        rows = sum(1 for _ in reader)
    return rows, len(header), header


def load_manifest_entry(manifest_path: Path, filename: str) -> dict:
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    for entry in manifest.get("files", []):
        if entry.get("filename") == filename:
            return entry
    raise KeyError(f"No manifest entry for '{filename}' in {manifest_path}")


def compare_to_manifest(observed: dict, expected: dict) -> list[dict]:
    """Return one check dict per compared field."""
    checks = []
    for field in ("sha256", "bytes", "row_count", "column_count"):
        exp = expected.get(field)
        obs = observed.get(field)
        checks.append(
            {
                "field": field,
                "expected": exp,
                "observed": obs,
                "ok": exp == obs,
            }
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    args = parser.parse_args()

    if not args.data.is_file():
        print(f"FAIL: raw data file not found: {args.data}", file=sys.stderr)
        return 2

    print(f"Reading (read-only): {args.data.relative_to(REPO_ROOT)}")
    digest = sha256_file(args.data)
    size = byte_size(args.data)
    rows, cols, header = count_rows_and_columns(args.data)

    observed = {"sha256": digest, "bytes": size, "row_count": rows, "column_count": cols}
    print(f"  sha256       : {digest}")
    print(f"  bytes        : {size}")
    print(f"  data rows    : {rows}")
    print(f"  columns      : {cols}")
    print(f"  first column : {header[0] if header else '(none)'}")
    print(f"  last column  : {header[-1] if header else '(none)'}")

    expected = load_manifest_entry(args.manifest, args.data.name)
    checks = compare_to_manifest(observed, expected)
    for check in checks:
        flag = "OK  " if check["ok"] else "MISMATCH"
        print(f"  [{flag}] {check['field']}: expected {check['expected']!r}, observed {check['observed']!r}")

    passed = all(check["ok"] for check in checks)
    record_path = write_run_record(
        "smoke_test",
        result_summary={
            "observed_sha256": digest,
            "observed_bytes": size,
            "observed_row_count": rows,
            "observed_column_count": cols,
            "manifest_checks": "; ".join(
                f"{c['field']}={'ok' if c['ok'] else 'MISMATCH'}" for c in checks
            ),
        },
        passed=passed,
        data_path=args.data,
        data_sha256=digest,
        output_path=None,
        config_snapshot={
            "data_path": str(args.data.relative_to(REPO_ROOT)),
            "manifest_path": str(args.manifest.relative_to(REPO_ROOT)),
        },
    )
    print(f"Run record: {record_path.relative_to(REPO_ROOT)}")
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
