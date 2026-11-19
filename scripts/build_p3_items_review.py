#!/usr/bin/env python3
"""Work package P3c, section C: the P3 item review workbook v1 and the run-5 review-flag list (report only; no model call).

Reads packets v4b and the ingested run 5 (each file checked against its manifest). Writes
`artifacts/benchmark/review/P3_items_review_v1.csv` (tracked; sheet ITEMS), `P3_items_review_v1.xlsx` (gitignored; ITEMS,
FLAGS, README) and `P3_review_flags_v1.json` (tracked). BI-P3-0005's question carries the COORDINATOR's proposed edit
(`coordinator_proposed`; not applied). **No item is modified** (checked). Rules: `src/climrr/p3_items_review.py`.

    python scripts/build_p3_items_review.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import litsynth_run5 as s5  # noqa: E402
from climrr import mentor_sheet_v2b as ms  # noqa: E402
from climrr import p3_items_review as pr  # noqa: E402
from climrr import synthpackets_v4 as v4  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.xlsxlite import write_xlsx  # noqa: E402


def main() -> int:
    man, packets = ms.load_packets(v4.PACKETS_V4B_DIR)
    items = ms.load_items(s5.ART, man)
    before = {i: sha256_file(s5.ITEMS_DIR / f"{i}.json") for i in items}
    report = pr.flags(items, packets)
    rows = pr.item_rows(items, report)
    with open(pr.CSV_PATH, "w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)
    write_xlsx(pr.XLSX_PATH, [("ITEMS", rows, [6, 12, 20, 14, 10, 14, 40, 50, 70, 50, 70, 50, 30, 18, 40, 30, 14, 30, 14, 30]),
                              ("FLAGS", pr.flag_rows(report), [12, 12, 18, 24, 26, 70, 90]),
                              ("README", pr.README_ROWS, [14, 120])])
    r2.write_json(pr.FLAGS_PATH, report)
    if any(sha256_file(s5.ITEMS_DIR / f"{i}.json") != h for i, h in before.items()):
        raise SystemExit("an item file changed during the build")
    result = {"csv_sha256": sha256_file(pr.CSV_PATH), "flags_sha256": sha256_file(pr.FLAGS_PATH),
              "xlsx_sha256": sha256_file(pr.XLSX_PATH), "counts_by_source": report["counts_by_source"],
              "context_driver_report_hits": report["context_driver_report_hits"],
              "regional_contrast_report_hits": report["regional_contrast_report_hits"], "rubric_lint": report["rubric_lint"],
              "coordinator_proposed": {i: p["prompt"] for i, p in pr.PROPOSED.items()},
              "flags_per_item": {i: [f["flag_id"] for f in report["flags"] if f["item_id"] == i] for i, _ in ms.ORDER}}
    rec = write_run_record(
        "build_p3_items_review", result_summary=result, passed=True, data_path=s5.MANIFEST_PATH, output_path=pr.CSV_PATH,
        config_snapshot={"packets_manifest_sha256": sha256_file(v4.PACKETS_V4B_DIR / "manifest.json"),
                         "items_manifest_sha256": sha256_file(s5.MANIFEST_PATH), "model_calls": 0, "items_modified": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
