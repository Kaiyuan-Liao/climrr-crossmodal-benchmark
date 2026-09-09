#!/usr/bin/env python3
"""M1-WP1 Phase B: the deterministic, semantics-neutral profile of FullData.csv.

Verifies the manifest SHA-256 first and refuses to read the table otherwise
(D-005/D-006, fail closed). Then reads every field as text with the stdlib
`csv` module and writes:

    artifacts/profiles/fulldata_profile.json   machine-readable, one object per column
    artifacts/profiles/fulldata_profile.csv    the same, key fields only, for reading

and prints the **profile content hash** --- the SHA-256 of the JSON with its
`environment` block removed. That hash, not the file hash, is what must match
between this host and Sophia.

No column is interpreted, renamed, filtered, aggregated, or unit-converted. See
`climrr.profile` for the matching rules and what they do and do not claim.
"""

from __future__ import annotations

import argparse
import platform
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr.manifest import ManifestMismatchError, verify_file  # noqa: E402
from climrr.profile import (  # noqa: E402
    SENTINEL_MIN_RATE,
    build_profile,
    profile_content_hash,
    write_profile_csv,
    write_profile_json,
)
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
JSON_NAME = "fulldata_profile.json"
CSV_NAME = "fulldata_profile.csv"


def environment_block() -> dict:
    """Everything about *this host* --- and therefore everything the content hash excludes."""
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "git_dirty": git_dirty(),
        "hostname": socket.gethostname(),
        "location": detect_location(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "pinned_libraries": pinned_libraries(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--sentinel-min-rate", type=float, default=SENTINEL_MIN_RATE)
    args = parser.parse_args()

    try:
        verified = verify_file(args.data, args.manifest)
    except (ManifestMismatchError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print(f"Manifest check OK: {args.data.name} sha256={verified['sha256']}")

    environment = environment_block()
    drift = [lib for lib in environment["pinned_libraries"] if not lib["matches_pin"]]
    if drift:
        print(f"WARNING: environment drifted from requirements.txt pins: {drift}", file=sys.stderr)

    profile = build_profile(
        args.data,
        data_sha256=verified["sha256"],
        data_bytes=verified["bytes"],
        data_path_label=str(args.data.relative_to(REPO_ROOT)),
        environment=environment,
        sentinel_min_rate=args.sentinel_min_rate,
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.out_dir / JSON_NAME
    csv_path = args.out_dir / CSV_NAME
    write_profile_json(json_path, profile)
    write_profile_csv(csv_path, profile)

    content_hash = profile_content_hash(profile)

    n_decimal = sum(1 for c in profile["columns"] if c["all_nonempty_match_decimal"])
    n_integer = sum(1 for c in profile["columns"] if c["all_nonempty_match_integer"])
    n_leading_zero = sum(1 for c in profile["columns"] if c["n_with_leading_zero_any"])
    n_constant = sum(1 for c in profile["columns"] if c["is_constant"])
    n_unique = sum(1 for c in profile["columns"] if c["looks_unique"])
    n_any_empty = sum(1 for c in profile["columns"] if c["n_empty"])
    n_sentinel_cols = sum(1 for c in profile["columns"] if c["candidate_sentinel_values"])

    print(f"  rows                      : {profile['n_rows']}")
    print(f"  columns                   : {profile['n_columns']}")
    print(f"  duplicate column names    : {profile['duplicate_column_names'] or 'none'}")
    print(f"  rows with wrong width     : {profile['row_shape']['n_rows_with_too_few_fields']}"
          f" short / {profile['row_shape']['n_rows_with_too_many_fields']} long")
    print(f"  all-decimal columns       : {n_decimal}")
    print(f"  all-integer columns       : {n_integer}")
    print(f"  columns w/ leading zeros  : {n_leading_zero}")
    print(f"  constant columns          : {n_constant}")
    print(f"  looks-unique columns      : {n_unique}")
    print(f"  columns with any empty    : {n_any_empty}")
    print(f"  columns w/ sentinel cands : {n_sentinel_cols}")
    print(f"  JSON                      : {json_path.relative_to(REPO_ROOT)}")
    print(f"  CSV                       : {csv_path.relative_to(REPO_ROOT)}")
    print(f"PROFILE CONTENT HASH: {content_hash}")

    passed = profile["n_columns"] > 0 and profile["n_rows"] > 0 and not drift
    record_path = write_run_record(
        "profile_fulldata",
        result_summary={
            "profile_content_hash": content_hash,
            "n_rows": profile["n_rows"],
            "n_columns": profile["n_columns"],
            "duplicate_column_names": profile["duplicate_column_names"] or "none",
            "rows_with_unexpected_width": (
                profile["row_shape"]["n_rows_with_too_few_fields"]
                + profile["row_shape"]["n_rows_with_too_many_fields"]
            ),
            "all_decimal_columns": n_decimal,
            "all_integer_columns": n_integer,
            "columns_with_leading_zero_values": n_leading_zero,
            "constant_columns": n_constant,
            "looks_unique_columns": n_unique,
            "columns_with_any_empty": n_any_empty,
            "columns_with_candidate_sentinels": n_sentinel_cols,
            "pin_drift": drift or "none",
        },
        passed=passed,
        data_path=args.data,
        data_sha256=verified["sha256"],
        output_path=json_path,
        config_snapshot={
            "data_path": str(args.data.relative_to(REPO_ROOT)),
            "manifest_path": str(args.manifest.relative_to(REPO_ROOT)),
            "sentinel_min_rate": args.sentinel_min_rate,
            "decimal_regex": profile["decimal_regex"],
            "profile_version": profile["profile_version"],
        },
    )
    print(f"Run record: {record_path.relative_to(REPO_ROOT)}")
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
