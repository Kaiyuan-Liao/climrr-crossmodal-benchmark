#!/usr/bin/env python3
"""Pilot P2b-ingest Phase C: the groups review workbook and its tracked GROUPS CSV (D-052).

Reads the grouping run 2 ingest (`artifacts/litgroups/run2/manifest.json`, `groups_enriched.jsonl`
and its summary) and the synthesis packets (`artifacts/benchmark/synth_packets/manifest.json` and the
packets it lists, each checked against its SHA-256). Writes `artifacts/benchmark/review/P2b_groups_v1.xlsx`
(gitignored) and the tracked `P2b_groups_v1.csv` (the GROUPS sheet). Rules: `src/climrr/p2b_review.py`.
No model call, no table value.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litgroups_run2 as g2  # noqa: E402
from climrr import p2b_review as rv  # noqa: E402
from climrr import synthpackets as spk  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.xlsxlite import write_xlsx  # noqa: E402


def main() -> int:
    man, summ, enriched, packets, pm = rv.inputs()
    derived = {f["path"]: f["sha256"] for f in man["derived_files"]}
    if sha256_file(g2.ENRICHED_PATH) != derived["groups_enriched.jsonl"]:
        raise SystemExit("groups_enriched.jsonl differs from the hash in the run-2 manifest")
    for x in pm["packets"]:
        if sha256_file(spk.PACKETS_DIR / f"{x['packet_id']}.json") != x["sha256"]:
            raise SystemExit(f"{x['packet_id']}.json differs from the hash in the packet manifest")

    sheets = rv.workbook_sheets(man, summ, enriched, packets, pm)
    write_xlsx(rv.WORKBOOK_PATH, sheets)
    group_rows = next(rows for name, rows, _ in sheets if name == "GROUPS")
    rv.GROUPS_CSV_PATH.write_text(rv.groups_csv(group_rows), encoding="utf-8")

    result = {"sheets": {name: len(rows) - 1 for name, rows, _ in sheets},
              "workbook_sha256": sha256_file(rv.WORKBOOK_PATH), "groups_csv_sha256": sha256_file(rv.GROUPS_CSV_PATH)}
    rec = write_run_record(
        "build_p2b_groups_review", result_summary=result, passed=True, data_path=g2.ENRICHED_PATH, output_path=rv.WORKBOOK_PATH,
        config_snapshot={"run2_manifest_sha256": sha256_file(g2.MANIFEST_PATH),
                         "packet_manifest_sha256": sha256_file(spk.PACKETS_DIR / "manifest.json"),
                         "dispositions": list(rv.DISPOSITIONS), "model_calls": 0},
    )
    print(json.dumps(result, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
