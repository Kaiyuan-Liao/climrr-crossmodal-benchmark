#!/usr/bin/env python3
"""M1-WP1 Phase D.2: what the data dictionary does and does not say about each column.

Reads the 275 column names from the manifest-verified CSV header and the
extracted dictionary text, matches each name against the dictionary's field
tables, and writes `artifacts/profiles/dictionary_coverage.json`: per column a
match rule, the exact quoted spans with line numbers, an evidence-based status,
and --- wherever the status is not `verified_from_dictionary` --- one specific,
answerable question.

The matching and status rules live in `climrr.dictionary`, which documents why a
stem-based match can never reach `verified_from_dictionary`: the dictionary
names its fields by suffix within a per-variable section and never states that a
CSV name's stem denotes that section.

This script assigns no meaning of its own. Every status it writes is backed by a
span, and every span is a verbatim line of the extracted text.
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

from climrr.checksums import sha256_file  # noqa: E402
from climrr.dictionary import build_coverage  # noqa: E402
from climrr.manifest import ManifestMismatchError, verify_file  # noqa: E402
from climrr.profile import read_header  # noqa: E402
from climrr.runrecord import (  # noqa: E402
    detect_location,
    git_commit,
    git_dirty,
    pinned_libraries,
    write_run_record,
)

DATA_PATH = REPO_ROOT / "data" / "raw" / "FullData.csv"
PDF_PATH = REPO_ROOT / "data" / "metadata" / "ClimRR_Metadata_and_Data_Dictionary.pdf"
TEXT_PATH = REPO_ROOT / "data" / "metadata" / "dictionary_extracted.txt"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"
OUT_PATH = REPO_ROOT / "artifacts" / "profiles" / "dictionary_coverage.json"

STATUS_ORDER = (
    "verified_from_dictionary",
    "partially_resolved",
    "unresolved",
    "structurally_observed_only",
)

HEADER_FIELD_RE = re.compile(r"^#\s*(\w+)\s*:\s*(.+?)\s*$")


def read_extraction_header(lines: list[str]) -> dict:
    """The provenance block the extractor wrote at the top of the text file."""
    header = {}
    for line in lines:
        if not line.startswith("#"):
            break
        match = HEADER_FIELD_RE.match(line)
        if match:
            header[match.group(1)] = match.group(2)
    return header


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--pdf", type=Path, default=PDF_PATH)
    parser.add_argument("--text", type=Path, default=TEXT_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args()

    try:
        verified_csv = verify_file(args.data, args.manifest)
        verified_pdf = verify_file(args.pdf, args.manifest)
    except (ManifestMismatchError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print(f"Manifest check OK: {args.data.name} sha256={verified_csv['sha256']}")
    print(f"Manifest check OK: {args.pdf.name} sha256={verified_pdf['sha256']}")

    if not args.text.is_file():
        print(
            f"FAIL: extracted dictionary text not found: {args.text}\n"
            "Run scripts/extract_dictionary_text.py first.",
            file=sys.stderr,
        )
        return 2

    lines = args.text.read_text(encoding="utf-8").splitlines()
    extraction = read_extraction_header(lines)

    # The extraction must come from the manifest-pinned PDF. Without this the
    # citations could point into text produced from some other document.
    if extraction.get("source_pdf_sha256") != verified_pdf["sha256"]:
        print(
            "FAIL: the extracted text records a different source PDF than the manifest pins "
            f"(text {extraction.get('source_pdf_sha256')}, manifest {verified_pdf['sha256']}). "
            "Re-run scripts/extract_dictionary_text.py.",
            file=sys.stderr,
        )
        return 2

    columns = read_header(args.data)
    coverage = build_coverage(columns, lines)

    without_span = [
        record["index"]
        for record in coverage["columns"]
        if record["status"] in {"verified_from_dictionary", "partially_resolved"}
        and not record["dictionary_evidence"]
    ]

    report = {
        "coverage_version": 1,
        "data_path": str(args.data.relative_to(REPO_ROOT)),
        "data_sha256": verified_csv["sha256"],
        "source_pdf_path": str(args.pdf.relative_to(REPO_ROOT)),
        "source_pdf_sha256": verified_pdf["sha256"],
        "extracted_text_path": str(args.text.relative_to(REPO_ROOT)),
        "extracted_text_sha256": sha256_file(args.text),
        "extractor": extraction.get("extractor"),
        "note": (
            "Line numbers refer to the extracted text file. A stem or narrative match is an "
            "EXECUTOR-proposed candidate and is never verified: the dictionary does not state "
            "which section a CSV column-name stem belongs to."
        ),
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
        **coverage,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    counts = coverage["status_counts"]
    print(f"  dictionary sections parsed: {len(coverage['sections'])}")
    print(f"  columns classified        : {coverage['n_columns']}")
    for status in STATUS_ORDER:
        print(f"    {status:<28}: {counts.get(status, 0)}")
    print(f"  match rules               : {coverage['match_rule_counts']}")
    print(f"  report                    : {args.out.relative_to(REPO_ROOT)}")

    passed = coverage["n_columns"] == len(columns) and not without_span
    if without_span:
        print(f"FAIL: statuses without a cited span at column indices {without_span}", file=sys.stderr)

    record_path = write_run_record(
        "dictionary_coverage",
        result_summary={
            "columns_classified": coverage["n_columns"],
            "source_pdf_sha256": verified_pdf["sha256"],
            "extracted_text_sha256": sha256_file(args.text),
            "extractor": extraction.get("extractor"),
            "dictionary_sections_parsed": len(coverage["sections"]),
            **{f"status_{status}": counts.get(status, 0) for status in STATUS_ORDER},
            "match_rule_counts": coverage["match_rule_counts"],
            "statuses_without_span": without_span or "none",
        },
        passed=passed,
        data_path=args.pdf,
        data_sha256=verified_pdf["sha256"],
        output_path=args.out,
        config_snapshot={
            "data_path": str(args.data.relative_to(REPO_ROOT)),
            "pdf_path": str(args.pdf.relative_to(REPO_ROOT)),
            "extracted_text_path": str(args.text.relative_to(REPO_ROOT)),
        },
    )
    print(f"Run record: {record_path.relative_to(REPO_ROOT)}")
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
