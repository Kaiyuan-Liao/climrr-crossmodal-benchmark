#!/usr/bin/env python3
"""Mentor sheet v3 package, section B: the item review workbook v3, rebuilt in place with the COORDINATOR-proposed texts
v3 (no freeze).

As `build_p2b_items_review_v2.py`, with the COORDINATOR-proposed texts v3 (`P2b_coordinator_edits_2026-11-03_v3.yaml`,
pinned) in the `edited_*` cells, `edit_origin` = coordinator_proposed_v3, and the overlay summary of the corrections v1a
(`artifacts/litstatements/corrections/provenance_corrections_v1a_applied.json`, written by
`scripts/apply_provenance_corrections.py`: the D-057 correction and the D-058 label override) on the OVERVIEW sheet.
Writes `artifacts/benchmark/review/P2b_items_review_v3.xlsx` (gitignored) and the tracked `P2b_items_review_v3.csv` (the
ITEMS sheet); the v2-text build of both is the one at commit 7825fcf. v1 and v2 stay as built. Rules:
`src/climrr/p2b_items_review.py` (v3 section). No model call, no table value.

    python scripts/build_p2b_items_review_v3.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litsynth_run3 as s3  # noqa: E402
from climrr import p2b_items_review as rv  # noqa: E402
from climrr import p2b_mentor_v3 as m3  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.xlsxlite import write_xlsx  # noqa: E402


def main() -> int:
    if sha256_file(rv.COORDINATOR_NOTES_PATH) != rv.COORDINATOR_NOTES_SHA256:
        raise SystemExit(f"{repo_relative(rv.COORDINATOR_NOTES_PATH)} differs from its SHA-256")
    man2, man3, index, items, packets, lint, notes, item_sha = rv.inputs_v2()
    edits = m3.edits_v3()
    if not set(edits) <= set(notes):
        raise SystemExit(f"edits name items not in the set: {sorted(set(edits) - set(notes))}")
    applied = json.loads(m3.APPLIED_V1A_PATH.read_text(encoding="utf-8"))

    sheets = rv.workbook_sheets_v3(man2, man3, index, items, packets, lint, notes, item_sha, edits, applied, texts="v3")
    write_xlsx(rv.WORKBOOK_V3_PATH, sheets)
    item_rows = next(rows for name, rows, _ in sheets if name == "ITEMS")
    rv.ITEMS_CSV_V3_PATH.write_text(rv.items_csv(item_rows), encoding="utf-8")

    result = {"sheets": {name: len(rows) - 1 for name, rows, _ in sheets}, "workbook_sha256": sha256_file(rv.WORKBOOK_V3_PATH),
              "items_csv_sha256": sha256_file(rv.ITEMS_CSV_V3_PATH), "edited_items": list(edits),
              "edit_origin": sorted({e["edit_origin"] for e in edits.values()}), "coordinator_notes_sha256": rv.COORDINATOR_NOTES_SHA256}
    rec = write_run_record(
        "build_p2b_items_review_v3", result_summary=result, passed=True, data_path=s3.INDEX_PATH, output_path=rv.WORKBOOK_V3_PATH,
        config_snapshot={"items_index_sha256": sha256_file(s3.INDEX_PATH), "lint_sha256": sha256_file(rv.LINT_V1A_PATH),
                         "coordinator_edits_v3_sha256": sha256_file(m3.EDITS_V3_PATH),
                         "corrections_applied_sha256": sha256_file(m3.APPLIED_V1A_PATH),
                         "coordinator_notes": repo_relative(rv.COORDINATOR_NOTES_PATH), "model_calls": 0},
    )
    print(json.dumps(result, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
