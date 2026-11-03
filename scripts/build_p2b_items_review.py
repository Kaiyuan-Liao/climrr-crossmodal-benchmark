#!/usr/bin/env python3
"""Pilot P2b-ingest-items Phase C: the item review workbook and its tracked ITEMS CSV (D-056).

Copies the COORDINATOR review notes (`--notes`, checked against their SHA-256) byte-identical to
`artifacts/benchmark/review/P2b_items_coordinator_notes_v1.csv` (an existing copy must be identical). Reads the
synthesis run-2 ingest (`artifacts/benchmark/items/run2/manifest.json` and the items it lists, each checked against
its SHA-256), the rubric lint (`rubric_lint_v1.json`) and the packets v3a at the run's source commit. Writes
`artifacts/benchmark/review/P2b_items_review_v1.xlsx` (gitignored) and the tracked `P2b_items_review_v1.csv` (the ITEMS
sheet). Rules: `src/climrr/p2b_items_review.py`. No model call, no table value.

    python scripts/build_p2b_items_review.py [--notes <P2b_items_coordinator_notes_v1.csv>]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import litsynth_run2 as s2  # noqa: E402
from climrr import p2b_items_review as rv  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.xlsxlite import write_xlsx  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--notes", type=Path, help="the COORDINATOR notes as delivered (default: the tracked copy)")
    a = ap.parse_args()
    if a.notes:
        if sha256_file(a.notes) != rv.COORDINATOR_NOTES_SHA256:
            raise SystemExit(f"{a.notes.name} is not the delivered notes {rv.COORDINATOR_NOTES_SHA256}")
        r2._copy(a.notes, rv.COORDINATOR_NOTES_PATH)
    if sha256_file(rv.COORDINATOR_NOTES_PATH) != rv.COORDINATOR_NOTES_SHA256:
        raise SystemExit(f"{repo_relative(rv.COORDINATOR_NOTES_PATH)} differs from its SHA-256")

    man, items, packets, lint, notes, item_sha = rv.inputs()
    for x in man["items_ingested"]:
        if sha256_file(s2.ART / x["path"]) != x["sha256"]:
            raise SystemExit(f"{x['path']} differs from the hash in the items manifest")
    for it in items:
        if s2.packet_at_source(it["review"]["history"][0]["seed_id"])[1] != it["review"]["history"][0]["packet_sha256"]:
            raise SystemExit(f"{it['item_id']}: packet at the source commit differs from the item's packet hash")
    if sorted(notes) != sorted(it["item_id"] for it in items):
        raise SystemExit(f"COORDINATOR notes name {sorted(notes)}, the items are {sorted(it['item_id'] for it in items)}")

    sheets = rv.workbook_sheets(man, items, packets, lint, notes, item_sha)
    write_xlsx(rv.WORKBOOK_PATH, sheets)
    item_rows = next(rows for name, rows, _ in sheets if name == "ITEMS")
    rv.ITEMS_CSV_PATH.write_text(rv.items_csv(item_rows), encoding="utf-8")

    result = {"sheets": {name: len(rows) - 1 for name, rows, _ in sheets}, "workbook_sha256": sha256_file(rv.WORKBOOK_PATH),
              "items_csv_sha256": sha256_file(rv.ITEMS_CSV_PATH), "coordinator_notes_sha256": rv.COORDINATOR_NOTES_SHA256}
    rec = write_run_record(
        "build_p2b_items_review", result_summary=result, passed=True, data_path=s2.MANIFEST_PATH, output_path=rv.WORKBOOK_PATH,
        config_snapshot={"items_manifest_sha256": sha256_file(s2.MANIFEST_PATH), "lint_sha256": sha256_file(rv.LINT_PATH),
                         "coordinator_notes": repo_relative(rv.COORDINATOR_NOTES_PATH),
                         "packets": f"synthpackets v3a at {s2.SOURCE_COMMIT}", "kaiyuan_dispositions": list(rv.KAIYUAN_DISPOSITIONS),
                         "model_calls": 0},
    )
    print(json.dumps(result, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
