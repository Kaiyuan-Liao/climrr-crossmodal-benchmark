#!/usr/bin/env python3
"""M1-WP2b: are `OBJECTID_12` and `OBJECTID_12_13` the same column twice?

`METADATA_QUESTIONS.md` Q11.4 asks whether CSV indices 235 and 236 are
duplicates of one another. Unlike the rest of Q11, that sub-question does not
need the mentor: it is a property of the bytes, and the mentor meeting of
2026-09-10 produced no per-column answers (R-002), so answering the part that
can be answered deterministically is worth more than waiting.

What this settles, and what it does not
---------------------------------------

A row-wise comparison can establish that the two columns hold **identical text
in every row**, or that they differ in some row and where. That is a fact about
characters.

It cannot establish what either column *means*, which layer it came from, why
the export carries it twice, or whether either is a usable key. Identical
contents are consistent with "the same field duplicated by a join" and equally
consistent with "two different fields that happen to agree in this extract".
The question of which one it is stays with the mentor.

Every value is compared as the raw string the file holds. No value is stripped,
coerced, or parsed as a number --- `01` and `1` are different text, and deciding
they are the same number would be exactly the identifier-destroying coercion the
charter forbids.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr.manifest import ManifestMismatchError, verify_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.profile import ENCODING, read_header  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

DATA_PATH = REPO_ROOT / "data" / "raw" / "FullData.csv"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"

#: The pair Q11.4 names. Addressed by **ordinal index**, with the expected name
#: checked against the header --- the table has duplicate-looking names and a
#: name lookup could silently pick the wrong one.
LEFT_INDEX = 235
RIGHT_INDEX = 236
LEFT_NAME = "OBJECTID_12"
RIGHT_NAME = "OBJECTID_12_13"

#: How many differing rows to quote in the report, if any differ at all.
MAX_EXAMPLES = 5


def compare_columns(path: Path, left: int, right: int) -> dict:
    """Stream the CSV once, comparing two columns row by row as raw text."""
    n_rows = 0
    n_equal = 0
    left_values: set[str] = set()
    right_values: set[str] = set()
    n_differing = 0
    n_both_empty = 0
    n_only_left_empty = 0
    n_only_right_empty = 0
    left_empty_rows: set[int] = set()
    right_empty_rows: set[int] = set()
    examples: list[dict] = []

    with path.open("r", encoding=ENCODING, newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        for row_number, row in enumerate(reader, start=1):
            n_rows += 1
            left_value = row[left] if left < len(row) else ""
            right_value = row[right] if right < len(row) else ""

            left_values.add(left_value)
            right_values.add(right_value)

            left_blank = left_value.strip() == ""
            right_blank = right_value.strip() == ""
            if left_blank:
                left_empty_rows.add(row_number)
            if right_blank:
                right_empty_rows.add(row_number)
            if left_blank and right_blank:
                n_both_empty += 1
            elif left_blank:
                n_only_left_empty += 1
            elif right_blank:
                n_only_right_empty += 1

            if left_value == right_value:
                n_equal += 1
                continue
            n_differing += 1
            if len(examples) < MAX_EXAMPLES:
                examples.append(
                    {"row": row_number, "left": left_value, "right": right_value}
                )

    return {
        "n_rows": n_rows,
        "n_equal_as_text": n_equal,
        "n_differing": n_differing,
        "n_both_empty": n_both_empty,
        "n_only_left_empty": n_only_left_empty,
        "n_only_right_empty": n_only_right_empty,
        "n_left_empty": len(left_empty_rows),
        "n_right_empty": len(right_empty_rows),
        "empty_row_sets_identical": left_empty_rows == right_empty_rows,
        # Row-wise inequality and set equality are different questions, and here
        # they have different answers. Asking both is what separates "two
        # unrelated columns" from "the same identifiers assigned to different
        # rows" --- a distinction the mentor question depends on.
        "n_distinct_left": len(left_values),
        "n_distinct_right": len(right_values),
        "value_sets_identical": left_values == right_values,
        "n_values_only_in_left": len(left_values - right_values),
        "n_values_only_in_right": len(right_values - left_values),
        "differing_examples": examples,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--left", type=int, default=LEFT_INDEX)
    parser.add_argument("--right", type=int, default=RIGHT_INDEX)
    args = parser.parse_args()

    try:
        verified = verify_file(args.data, args.manifest)
    except (ManifestMismatchError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print(f"Manifest check OK: {args.data.name} sha256={verified['sha256']}")

    header = read_header(args.data)
    for index, expected in ((args.left, LEFT_NAME), (args.right, RIGHT_NAME)):
        if index >= len(header):
            print(f"FAIL: column index {index} is past the {len(header)}-column header", file=sys.stderr)
            return 2
        if args.left == LEFT_INDEX and args.right == RIGHT_INDEX and header[index] != expected:
            print(
                f"FAIL: column index {index} is named {header[index]!r}, not {expected!r}. "
                "The column layout is not what Q11.4 describes; stop and report.",
                file=sys.stderr,
            )
            return 2

    left_name, right_name = header[args.left], header[args.right]
    result = compare_columns(args.data, args.left, args.right)
    result = {
        "left_index": args.left,
        "left_column": left_name,
        "right_index": args.right,
        "right_column": right_name,
        **result,
    }

    identical = result["n_differing"] == 0
    print(f"  compared                  : [{args.left}] {left_name} vs [{args.right}] {right_name}")
    print(f"  rows                      : {result['n_rows']}")
    print(f"  identical as text         : {result['n_equal_as_text']}")
    print(f"  differing                 : {result['n_differing']}")
    print(f"  both empty                : {result['n_both_empty']}")
    print(f"  only left empty           : {result['n_only_left_empty']}")
    print(f"  only right empty          : {result['n_only_right_empty']}")
    print(f"  empty-row sets identical  : {result['empty_row_sets_identical']}")
    print(f"  distinct values           : {result['n_distinct_left']} / {result['n_distinct_right']}")
    print(f"  value sets identical      : {result['value_sets_identical']}")
    print(
        f"  values in one only        : {result['n_values_only_in_left']} left, "
        f"{result['n_values_only_in_right']} right"
    )
    for example in result["differing_examples"]:
        print(f"    row {example['row']}: {example['left']!r} != {example['right']!r}")
    print(
        "  VERDICT                   : "
        + (
            "the two columns hold identical text in every row"
            if identical
            else f"the two columns differ in {result['n_differing']} row(s)"
        )
        + (
            ", while holding the identical set of values"
            if result["value_sets_identical"] and not identical
            else ""
        )
    )
    print(
        "  NOTE                      : this is a fact about characters. It does not say what "
        "either column means, which layer it came from, or which is the key --- that stays Q11."
    )

    # The run passes whichever way the comparison comes out: the script's job is
    # to measure, not to hope for an answer. It fails only if it could not.
    passed = result["n_rows"] > 0
    record_path = write_run_record(
        "check_objectid_pair",
        result_summary={
            "data_sha256": verified["sha256"],
            "question": "Q11.4",
            **result,
            "columns_identical_as_text": identical,
        },
        passed=passed,
        data_path=args.data,
        data_sha256=verified["sha256"],
        output_path=None,
        config_snapshot={
            "data_path": repo_relative(args.data),
            "left_index": args.left,
            "right_index": args.right,
            "comparison": "raw string equality; no stripping, no numeric coercion",
        },
    )
    print(f"Run record: {repo_relative(record_path)}")
    print(json.dumps({"identical_as_text": identical, "differing": result["n_differing"]}))
    print("PASS" if passed else "FAIL: no data rows were read")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
