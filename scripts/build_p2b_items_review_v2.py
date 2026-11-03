#!/usr/bin/env python3
"""Mentor-export package Phase B: the item review workbook v2 (run 3 for 0010; COORDINATOR-proposed edits; no freeze).

Reads the current items from the items index (`artifacts/benchmark/items/index.json`, each checked against its hash; run 2
for 0001--0009, run 3 for 0010), the packets they were built from (each at the item's own source commit), rubric lint v1a
(`artifacts/benchmark/items/rubric_lint_v1a.json`), the COORDINATOR notes (`P2b_items_coordinator_notes_v1.csv`, checked
against its SHA-256; unchanged) and the COORDINATOR-proposed texts (`P2b_coordinator_edits_2026-11-03.yaml`). Writes
`artifacts/benchmark/review/P2b_items_review_v2.xlsx` (gitignored) and the tracked `P2b_items_review_v2.csv` (the ITEMS
sheet). v1 stays as built. Rules: `src/climrr/p2b_items_review.py` (v2 section). No model call, no table value.

    python scripts/build_p2b_items_review_v2.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litsynth_run3 as s3  # noqa: E402
from climrr import p2b_items_review as rv  # noqa: E402
from climrr import p2b_mentor_export as mx  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.xlsxlite import write_xlsx  # noqa: E402


def main() -> int:
    if sha256_file(rv.COORDINATOR_NOTES_PATH) != rv.COORDINATOR_NOTES_SHA256:
        raise SystemExit(f"{repo_relative(rv.COORDINATOR_NOTES_PATH)} differs from its SHA-256")
    man2, man3, index, items, packets, lint, notes, item_sha = rv.inputs_v2()
    if sorted(notes) != sorted(it["item_id"] for it in items):
        raise SystemExit(f"COORDINATOR notes name {sorted(notes)}, the items are {sorted(it['item_id'] for it in items)}")
    edits = mx.edits()
    if not set(edits) <= set(notes):
        raise SystemExit(f"edits name items not in the set: {sorted(set(edits) - set(notes))}")

    sheets = rv.workbook_sheets_v2(man2, man3, index, items, packets, lint, notes, item_sha, edits)
    write_xlsx(rv.WORKBOOK_V2_PATH, sheets)
    item_rows = next(rows for name, rows, _ in sheets if name == "ITEMS")
    rv.ITEMS_CSV_V2_PATH.write_text(rv.items_csv(item_rows), encoding="utf-8")

    result = {"sheets": {name: len(rows) - 1 for name, rows, _ in sheets}, "workbook_sha256": sha256_file(rv.WORKBOOK_V2_PATH),
              "items_csv_sha256": sha256_file(rv.ITEMS_CSV_V2_PATH), "current_runs": {x["item_id"]: x["current"]["run"] for x in index["items"]},
              "edited_items": list(edits), "coordinator_notes_sha256": rv.COORDINATOR_NOTES_SHA256}
    rec = write_run_record(
        "build_p2b_items_review_v2", result_summary=result, passed=True, data_path=s3.INDEX_PATH, output_path=rv.WORKBOOK_V2_PATH,
        config_snapshot={"items_index_sha256": sha256_file(s3.INDEX_PATH), "lint_sha256": sha256_file(rv.LINT_V1A_PATH),
                         "coordinator_edits_sha256": sha256_file(mx.EDITS_PATH), "coordinator_notes": repo_relative(rv.COORDINATOR_NOTES_PATH),
                         "kaiyuan_dispositions": list(rv.KAIYUAN_DISPOSITIONS), "model_calls": 0},
    )
    print(json.dumps(result, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
