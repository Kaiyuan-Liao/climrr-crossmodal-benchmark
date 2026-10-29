#!/usr/bin/env python3
"""Pilot P1: extract deterministic table patterns at state / NCA-region level.

Reads `data/metadata/templates/slots_v1.yaml` (validated as Track D validates it),
`data/metadata/geography/nca_regions_v1.yaml` (verified against its manifest
pin), the coverage statuses, and `data/raw/FullData.csv` after its manifest hash
check; computes every pattern by `climrr.table_patterns` (no model, no
randomness).

Writes, deterministically:
  artifacts/benchmark/table_patterns_v1.jsonl
  artifacts/benchmark/table_patterns_v1_summary.json
  artifacts/benchmark/table_patterns_v1_examples.jsonl   (the doc's ten examples)
  docs/TABLE_PATTERNS_V1.md
and a run record. Prints the counts and the ten examples. Exits 1 if a State
row count differs from slots_v1 or the NCA map does not cover a table State label.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import table_patterns as tp  # noqa: E402
from climrr import templates as td  # noqa: E402
from climrr.manifest import MANIFEST_PATH, ManifestMismatchError, load_entry, verify_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

DATA_PATH = REPO_ROOT / "data" / "raw" / "FullData.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    args = parser.parse_args()

    slots = td.load_yaml(td.SLOTS_PATH)
    coverage = td.load_coverage()
    try:
        td.validate_slots(slots, dictionary_lines=td.DICTIONARY_TEXT_PATH.read_text(encoding="utf-8").splitlines(),
                          coverage=coverage, concept_map=td.load_yaml(td.CONCEPT_MAP_PATH))
        verified = verify_file(args.data, args.manifest)
        nca_pin = load_entry(tp.NCA_MAP_PATH.name, args.manifest)["sha256"]
    except (td.TemplateError, ManifestMismatchError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    nca_sha = td.file_sha256(tp.NCA_MAP_PATH)
    if nca_sha != nca_pin:
        print(f"FAIL: nca_regions_v1.yaml sha256 {nca_sha} != manifest {nca_pin}. Escalate; do not re-pin.", file=sys.stderr)
        return 2
    print(f"Manifest check OK: {args.data.name} sha256={verified['sha256']}; NCA map {nca_sha}")

    nca = tp.load_nca_map()
    states = [v["label"] for v in td.location_values(slots, "state")]
    unmapped = sorted(set(states) - set(nca["state_to_region_map"]))
    if unmapped:
        print(f"FAIL: table State labels with no NCA5 region: {unmapped}", file=sys.stderr)
        return 1
    specs = tp.metric_specs(slots, coverage)
    control = slots["location"]["cell"]["values"][0]["label"]
    scanned = tp.scan(args.data, specs, states, control)
    print(f"  rows read: {scanned['n_rows']}")
    expected = {v["label"]: v["n_cells"] for v in slots["location"]["state"]["values"]}
    mismatches = [f"{s}: slots {expected[s]}, table {scanned['cells'].get(('state', s), {}).get('rows')}"
                  for s in states if scanned["cells"].get(("state", s), {}).get("rows") != expected[s]]
    if mismatches:
        print("FAIL: State row counts differ from slots_v1:\n  " + "\n  ".join(mismatches), file=sys.stderr)
        return 1

    records, skips = tp.build_patterns(slots, coverage, nca, scanned, verified["sha256"], nca_sha)
    regions = tp.region_members(nca, states)
    summary = tp.summarise(records, skips, regions, states, nca)

    tp.OUT_DIR.mkdir(parents=True, exist_ok=True)
    tp.write_jsonl(records, tp.PATTERNS_PATH)
    tp.write_jsonl(tp.example_records(records), tp.EXAMPLES_PATH)
    summary["patterns_file"] = {"path": repo_relative(tp.PATTERNS_PATH), "sha256": td.file_sha256(tp.PATTERNS_PATH),
                                "bytes": tp.PATTERNS_PATH.stat().st_size, "n_records": len(records)}
    summary["nca_map_sha256"] = nca_sha
    summary["code_version"] = tp.code_version()
    tp.SUMMARY_PATH.write_text(tp.dumps(summary), encoding="utf-8")
    hashes = tp.doc_hashes(verified["sha256"], td.file_sha256(tp.PATTERNS_PATH))
    tp.DOC_PATH.write_text(tp.render_doc(json.loads(tp.SUMMARY_PATH.read_text(encoding="utf-8")),
                                         tp.read_jsonl(tp.EXAMPLES_PATH), hashes, nca), encoding="utf-8")

    print(f"  patterns: {summary['n_patterns']}  {summary['by_kind']}")
    for key in ("by_family", "by_geography_type", "by_statistic", "by_status", "tercile_groups_skipped_by_reason"):
        print(f"  {key}: {summary[key]}")
    print(f"  with tercile: {summary['n_with_relative_tercile']}; acceptance blocked: {summary['n_acceptance_blocked']}")
    print("  ten examples:")
    for r in tp.example_records(records):
        for line in tp._example_line(r):
            print("   " + line)
    for name, sha in hashes.items():
        print(f"  {name}: {sha}")

    record = write_run_record(
        "extract_table_patterns",
        result_summary={k: v for k, v in summary.items() if k not in ("tercile_skips", "region_coverage")}
        | {"outputs": {k: v for k, v in hashes.items() if k != "data/raw/FullData.csv"}},
        passed=True,
        data_path=args.data,
        data_sha256=verified["sha256"],
        output_path=tp.PATTERNS_PATH,
        config_snapshot={"slots_sha256": td.file_sha256(td.SLOTS_PATH), "nca_map_sha256": nca_sha,
                         "coverage_sha256": td.file_sha256(td.COVERAGE_PATH),
                         "dictionary_text_sha256": td.file_sha256(td.DICTIONARY_TEXT_PATH),
                         "code_version": tp.code_version(), "model_calls": 0},
    )
    print(f"Run record: {repo_relative(record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
