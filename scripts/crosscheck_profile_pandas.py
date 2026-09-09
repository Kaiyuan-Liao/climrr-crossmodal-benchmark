#!/usr/bin/env python3
"""M1-WP1 Phase C: re-read FullData.csv with pinned pandas and compare counts.

The Phase B profile is stdlib-only by design. This script reads the same bytes
with a second, independent parser and recomputes the counts that both readers
can express -- row count, column count, and per column the empty count, the
distinct count, the exact name, and the number of values carrying a leading
zero. It then compares them to `artifacts/profiles/fulldata_profile.json`.

pandas is given `dtype=str, keep_default_na=False, na_filter=False` so that it
performs no type inference and invents no missing values: an empty field stays
the empty string rather than becoming NaN. Columns are addressed **by position**,
never by name, because a name is not guaranteed unique.

**A disagreement is reported, not resolved.** If the two readers differ, that
difference is the finding, and deciding which one is right is not this script's
call -- it is an escalation.
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import numpy  # noqa: E402
import pandas  # noqa: E402

from climrr.manifest import ManifestMismatchError, verify_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.profile import ENCODING, LEADING_ZERO_PATTERN, profile_content_hash  # noqa: E402
from climrr.runrecord import (  # noqa: E402
    detect_location,
    git_commit,
    git_dirty,
    pinned_libraries,
    write_run_record,
)

DATA_PATH = REPO_ROOT / "data" / "raw" / "FullData.csv"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"
OUT_DIR = REPO_ROOT / "artifacts" / "profiles"
PROFILE_NAME = "fulldata_profile.json"
OUT_NAME = "crosscheck_pandas.json"

READ_OPTIONS = {
    "dtype": "str",
    "keep_default_na": False,
    "na_filter": False,
    "encoding": ENCODING,
}


def compare(field: str, stdlib_value, pandas_value) -> dict:
    return {
        "field": field,
        "stdlib": stdlib_value,
        "pandas": pandas_value,
        "agree": stdlib_value == pandas_value,
    }


def crosscheck(frame, profile: dict) -> dict:
    """Compare every count both readers can express. Returns the report body."""
    leading_zero = re.compile(LEADING_ZERO_PATTERN)

    table_checks = [
        compare("n_rows", profile["n_rows"], int(frame.shape[0])),
        compare("n_columns", profile["n_columns"], int(frame.shape[1])),
    ]

    columns = []
    for index, column_profile in enumerate(profile["columns"]):
        series = frame.iloc[:, index]
        stripped = series.str.strip()
        checks = [
            compare("name", column_profile["name"], str(frame.columns[index])),
            compare("n_empty", column_profile["n_empty"], int((stripped == "").sum())),
            compare("n_distinct", column_profile["n_distinct"], int(series.nunique())),
            compare(
                "n_with_leading_zero_any",
                column_profile["n_with_leading_zero_any"],
                int(stripped.map(lambda value: bool(leading_zero.match(value))).sum()),
            ),
        ]
        columns.append(
            {
                "index": index,
                "name": column_profile["name"],
                "agree": all(check["agree"] for check in checks),
                "checks": checks,
            }
        )

    disagreements = [
        {
            "index": column["index"],
            "name": column["name"],
            "fields": [check for check in column["checks"] if not check["agree"]],
        }
        for column in columns
        if not column["agree"]
    ]

    return {
        "table_level_checks": table_checks,
        "n_columns_compared": len(columns),
        "n_columns_agree": sum(1 for column in columns if column["agree"]),
        "n_columns_disagree": len(disagreements),
        "disagreements": disagreements,
        "columns": columns,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--profile", type=Path, default=OUT_DIR / PROFILE_NAME)
    parser.add_argument("--out", type=Path, default=OUT_DIR / OUT_NAME)
    args = parser.parse_args()

    if not args.profile.is_file():
        print(
            f"FAIL: stdlib profile not found: {args.profile}\n"
            "Run scripts/profile_fulldata.py first; this script compares against it.",
            file=sys.stderr,
        )
        return 2

    try:
        verified = verify_file(args.data, args.manifest)
    except (ManifestMismatchError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print(f"Manifest check OK: {args.data.name} sha256={verified['sha256']}")

    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    content_hash = profile_content_hash(profile)

    if profile["data_sha256"] != verified["sha256"]:
        print(
            "FAIL: the stdlib profile was built from different bytes than the file "
            f"present now (profile {profile['data_sha256']}, file {verified['sha256']}).",
            file=sys.stderr,
        )
        return 2

    frame = pandas.read_csv(args.data, **READ_OPTIONS)
    body = crosscheck(frame, profile)

    report = {
        "crosscheck_version": 1,
        "data_path": repo_relative(args.data),
        "data_sha256": verified["sha256"],
        "data_bytes": verified["bytes"],
        "stdlib_profile_path": repo_relative(args.profile),
        "stdlib_profile_content_hash": content_hash,
        "pandas_version": pandas.__version__,
        "numpy_version": numpy.__version__,
        "pandas_read_options": READ_OPTIONS,
        "compared_fields": [
            "n_rows",
            "n_columns",
            "name",
            "n_empty",
            "n_distinct",
            "n_with_leading_zero_any",
        ],
        "note": "Disagreements are reported, never resolved. Columns are addressed by position.",
        "environment": {
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "git_commit": git_commit(),
            "git_dirty": git_dirty(),
            "hostname": socket.gethostname(),
            "location": detect_location(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "pinned_libraries": pinned_libraries(),
        },
        **body,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    table_ok = all(check["agree"] for check in body["table_level_checks"])
    for check in body["table_level_checks"]:
        print(f"  [{'OK  ' if check['agree'] else 'DIFF'}] {check['field']}: "
              f"stdlib {check['stdlib']!r}, pandas {check['pandas']!r}")
    print(f"  columns compared          : {body['n_columns_compared']}")
    print(f"  columns in agreement      : {body['n_columns_agree']}")
    print(f"  columns disagreeing       : {body['n_columns_disagree']}")
    for disagreement in body["disagreements"]:
        print(f"    DISAGREEMENT index {disagreement['index']} ({disagreement['name']}): "
              f"{disagreement['fields']}")
    print(f"  pandas / numpy            : {pandas.__version__} / {numpy.__version__}")
    print(f"  report                    : {repo_relative(args.out)}")

    passed = table_ok and body["n_columns_disagree"] == 0
    record_path = write_run_record(
        "crosscheck_profile_pandas",
        result_summary={
            "stdlib_profile_content_hash": content_hash,
            "pandas_version": pandas.__version__,
            "numpy_version": numpy.__version__,
            "table_level_agreement": "all agree" if table_ok else "DISAGREEMENT",
            "n_columns_compared": body["n_columns_compared"],
            "n_columns_agree": body["n_columns_agree"],
            "n_columns_disagree": body["n_columns_disagree"],
            "disagreeing_columns": (
                [d["index"] for d in body["disagreements"]] if body["disagreements"] else "none"
            ),
        },
        passed=passed,
        data_path=args.data,
        data_sha256=verified["sha256"],
        output_path=args.out,
        config_snapshot={
            "data_path": repo_relative(args.data),
            "manifest_path": repo_relative(args.manifest),
            "pandas_read_options": READ_OPTIONS,
        },
    )
    print(f"Run record: {repo_relative(record_path)}")
    print("PASS" if passed else "FAIL (disagreement reported, not resolved)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
