#!/usr/bin/env python3
"""M1-WP3 Phases C and D: pick three rows structurally, and build their records.

Authorised by D-011 as bounded M1-WP3 work: **2--3 row-centered candidate
examples**, built from real rows, for the mentor to confirm or correct field by
field. They are not M2 phenomenon records and this script does nothing that
would make them one --- no aggregation, no threshold, no ranking, and no rule
that mentions how large a value is.

What it does, in order
----------------------

1. Verifies `data/raw/FullData.csv` against `data/manifest.json`. Fail-closed
   (D-005): an absent or altered file stops the run rather than skipping it.
2. Reads the coverage report and the inferred-candidate records, and checks that
   every one of the 41 pilot columns holds one of the three statuses the ruling
   allows. A column that has drifted stops the run.
3. Streams the CSV once, applying the three **structural** selection rules of
   `climrr.examples.SELECTION_RULES`. Every value is read as a string and no
   value is parsed as a number anywhere in this script.
4. Writes `artifacts/examples/example_<OID_>.json` per selected row, with the
   five blocks in the fixed order: provenance, raw, semantics, assumptions,
   presentation.
5. Checks the record's own invariant --- no inferred value appears in the
   presentation outside a `[provisional: ...]` label --- and fails the run if it
   does not hold.
6. Writes a run record, as every script in this repository must.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr.dictionary import (  # noqa: E402
    INFERRED_CANDIDATE,
    InferredCandidateError,
    load_inferred_candidates,
)
from climrr.examples import (  # noqa: E402
    PILOT_INDICES,
    SELECTION_RULES,
    ExampleError,
    build_example,
    select_rows,
    unlabelled_inferred_values,
)
from climrr.manifest import ManifestMismatchError, verify_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

DATA_PATH = REPO_ROOT / "data" / "raw" / "FullData.csv"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"
COVERAGE_PATH = REPO_ROOT / "artifacts" / "profiles" / "dictionary_coverage.json"
INFERRED_PATH = REPO_ROOT / "data" / "metadata" / "inferred_candidates.yaml"
OUT_DIR = REPO_ROOT / "artifacts" / "examples"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--coverage", type=Path, default=COVERAGE_PATH)
    parser.add_argument("--inferred-candidates", type=Path, default=INFERRED_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    try:
        verified = verify_file(args.data, args.manifest)
    except (ManifestMismatchError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print(f"Manifest check OK: {args.data.name} sha256={verified['sha256']}")

    if not args.coverage.is_file():
        print(
            f"FAIL: coverage report not found: {args.coverage}\n"
            "Run scripts/dictionary_coverage.py first.",
            file=sys.stderr,
        )
        return 2
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    if coverage.get("data_sha256") != verified["sha256"]:
        print(
            "FAIL: the coverage report was built from different CSV bytes than the ones "
            f"just verified (coverage {coverage.get('data_sha256')}, "
            f"data {verified['sha256']}). Re-run scripts/dictionary_coverage.py.",
            file=sys.stderr,
        )
        return 2

    try:
        records = load_inferred_candidates(
            args.inferred_candidates.read_text(encoding="utf-8")
        )
    except (InferredCandidateError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    inferred_by_index = {record["column_index"]: record for record in records}

    print(f"  pilot columns             : {len(PILOT_INDICES)} of {coverage['n_columns']}")
    statuses: dict[str, int] = {}
    for index in PILOT_INDICES:
        status = coverage["columns"][index]["status"]
        statuses[status] = statuses.get(status, 0) + 1
    for status, count in sorted(statuses.items()):
        print(f"    {status:<28}: {count:>3}")

    try:
        selected = select_rows(args.data, PILOT_INDICES)
    except ExampleError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    missing = [rule["id"] for rule in SELECTION_RULES if rule["id"] not in selected]
    if missing:
        print(
            f"FAIL: no row in the file satisfies selection rule(s) {missing}. That is a "
            "finding about the data, not an empty result; stop and report.",
            file=sys.stderr,
        )
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    offences = []
    for rule in SELECTION_RULES:
        hit = selected[rule["id"]]
        try:
            example = build_example(
                rule_id=rule["id"],
                ordinal=hit["ordinal"],
                values=hit["values"],
                coverage=coverage,
                inferred_by_index=inferred_by_index,
                csv_sha256=verified["sha256"],
            )
        except ExampleError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 2
        unlabelled = unlabelled_inferred_values(example)
        offences.extend((rule["id"], *item) for item in unlabelled)
        path = args.out_dir / f"example_{example['provenance']['OID_']}.json"
        path.write_text(
            json.dumps(example, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        blanks = sum(1 for item in example["raw"] if item["value"] == "")
        inferred_used = sum(
            1 for item in example["semantics"] if item["status"] == INFERRED_CANDIDATE
        )
        written.append(
            {
                "rule": rule["id"],
                "OID_": example["provenance"]["OID_"],
                "Crossmodel": example["provenance"]["Crossmodel"],
                "row_ordinal": hit["ordinal"],
                "GEOID": hit["values"][109],
                "blank_pilot_columns": blanks,
                "inferred_columns_used": inferred_used,
                "assumptions": len(example["assumptions"]),
                "path": repo_relative(path),
            }
        )
        print(
            f"    {rule['id']}: ordinal {hit['ordinal']}, OID_ {example['provenance']['OID_']}, "
            f"Crossmodel {example['provenance']['Crossmodel']}, GEOID "
            f"{hit['values'][109] or '(empty)'}, {blanks} blank pilot column(s) "
            f"-> {repo_relative(path)}"
        )

    for offence in offences:
        print(
            f"FAIL: inferred value shown unlabelled in {offence[0]} "
            f"(column {offence[1]}, {offence[2]}): {offence[3]!r}",
            file=sys.stderr,
        )

    passed = not offences
    record_path = write_run_record(
        "build_examples",
        result_summary={
            "pilot_columns": len(PILOT_INDICES),
            "pilot_status_counts": statuses,
            "inferred_candidate_records": len(records),
            "examples_written": len(written),
            "examples": written,
            "unlabelled_inferred_values": offences or "none",
        },
        passed=passed,
        data_path=args.data,
        data_sha256=verified["sha256"],
        output_path=args.out_dir,
        config_snapshot={
            "data_path": repo_relative(args.data),
            "coverage_path": repo_relative(args.coverage),
            "inferred_candidates_path": repo_relative(args.inferred_candidates),
            "out_dir": repo_relative(args.out_dir),
            "pilot_indices": list(PILOT_INDICES),
            "selection_rules": [rule["id"] for rule in SELECTION_RULES],
        },
    )
    print(f"Run record: {repo_relative(record_path)}")
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
