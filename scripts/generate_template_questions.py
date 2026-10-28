#!/usr/bin/env python3
"""Track D v1 dry run: fill the table_only templates and compute their answers.

Reads `data/metadata/templates/slots_v1.yaml` and `templates_v1.yaml`, validates
both against the dictionary text, the coverage statuses, the concept map and the
QA types, verifies `data/raw/FullData.csv` against `data/manifest.json`, then
enumerates every valid fill (no randomness) and computes each answer
deterministically. FWI questions stay `blocked_inferred_columns`.

Writes, deterministically:
  artifacts/templates/questions_v1.jsonl         (gitignored; pinned by SHA-256 in the summary)
  artifacts/templates/questions_v1_sample.jsonl  (tracked; the doc's examples come from it)
  artifacts/templates/questions_v1_summary.json
  artifacts/templates/prototype_reproduction_v1.json
  docs/TEMPLATE_QUESTIONS_V1.md
and a run record. No model call, no retrieval. Exits 1 if any prototype fails
to reproduce, or if a slot's recorded row count differs from the table.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import templates as td  # noqa: E402
from climrr.manifest import MANIFEST_PATH, ManifestMismatchError, verify_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

DATA_PATH = REPO_ROOT / "data" / "raw" / "FullData.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    args = parser.parse_args()

    slots = td.load_yaml(td.SLOTS_PATH)
    templates = td.load_yaml(td.TEMPLATES_PATH)
    try:
        td.validate_slots(
            slots,
            dictionary_lines=td.DICTIONARY_TEXT_PATH.read_text(encoding="utf-8").splitlines(),
            coverage=td.load_coverage(),
            concept_map=td.load_yaml(td.CONCEPT_MAP_PATH),
        )
        td.validate_templates(templates, slots, td.load_qa_types())
    except td.TemplateError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print("Slots and templates valid.")

    try:
        verified = verify_file(args.data, args.manifest)
    except (ManifestMismatchError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print(f"Manifest check OK: {args.data.name} sha256={verified['sha256']}")

    scan = td.scan_table(args.data, slots, templates["period_pairs"])
    print(f"  rows read: {scan['n_rows']}")
    mismatches = []
    for level in ("county", "state"):
        for value in slots["location"][level]["values"]:
            observed = scan["members"].get((level, value["label"]), {}).get("n_cells")
            if observed != value["n_cells"]:
                mismatches.append(f"{level} {value['label']!r}: slots {value['n_cells']}, table {observed}")
    if mismatches:
        print("FAIL: slot row counts differ from the table:\n  " + "\n  ".join(mismatches), file=sys.stderr)
        return 1

    records = td.build_questions(slots, templates, scan, verified["sha256"])
    summary = td.summarise(records, templates)
    reproduction = td.reproduce_prototypes(slots, scan, records)

    td.OUT_DIR.mkdir(parents=True, exist_ok=True)
    td.write_jsonl(records, td.QUESTIONS_PATH)
    td.write_jsonl(td.sample_records(records, templates), td.SAMPLE_PATH)
    summary["questions_file"] = td.questions_file_pin(td.QUESTIONS_PATH)
    td.SUMMARY_PATH.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    td.REPRODUCTION_PATH.write_text(json.dumps(reproduction, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    hashes = td.doc_hashes(verified["sha256"], td.file_sha256(td.QUESTIONS_PATH))
    # Rendered from the files just written --- exactly what the staleness test re-renders.
    td.DOC_PATH.write_text(
        td.render_doc(slots, templates, td.read_jsonl(td.SAMPLE_PATH),
                      json.loads(td.SUMMARY_PATH.read_text(encoding="utf-8")),
                      json.loads(td.REPRODUCTION_PATH.read_text(encoding="utf-8")), hashes),
        encoding="utf-8")

    print(f"  templates: {summary['n_templates']} ({summary['n_templates_table_only']} table_only)")
    print(f"  questions: {summary['n_questions']}  {summary['by_answer_status']}")
    for entry in reproduction["prototypes"]:
        print(f"  reproduce {entry['record_id']}: equal={entry['equal']} audit_only={entry['audit_only']}")
    for name, sha in hashes.items():
        print(f"  {name}: {sha}")

    record = write_run_record(
        "generate_template_questions",
        result_summary={"summary": summary, "prototypes_all_equal": reproduction["all_equal"],
                        "outputs": {k: v for k, v in hashes.items() if k != "data/raw/FullData.csv"}},
        passed=reproduction["all_equal"],
        data_path=args.data,
        data_sha256=verified["sha256"],
        output_path=td.QUESTIONS_PATH,
        config_snapshot={"slots_sha256": td.file_sha256(td.SLOTS_PATH),
                         "templates_sha256": td.file_sha256(td.TEMPLATES_PATH),
                         "coverage_sha256": td.file_sha256(td.COVERAGE_PATH),
                         "concept_map_sha256": td.file_sha256(td.CONCEPT_MAP_PATH),
                         "qa_types_sha256": td.file_sha256(td.QA_TYPES_PATH),
                         "dictionary_text_sha256": td.file_sha256(td.DICTIONARY_TEXT_PATH),
                         "model_calls": 0, "retrieval_runs": 0},
    )
    print(f"Run record: {repo_relative(record)}")
    if not reproduction["all_equal"]:
        print("FAIL: a prototype did not reproduce", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
