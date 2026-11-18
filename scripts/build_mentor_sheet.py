#!/usr/bin/env python3
"""Work package P3a, section E: the mentor sample sheet v2 from synthesis run 4 and polish run 1 (no model call).

Reads the seed packets v4 (`artifacts/benchmark/synth_packets_v4`, each checked against the manifest's SHA-256), the
synthesis run's output directory (`--items`, litsynth_agent v4: `items/<seed_id>.json`) and, when given, the polish run's
(`--polished`, litpolish_agent v1; its item is taken when present). Writes `artifacts/benchmark/review/MENTOR_SAMPLE_SHEET_v2.xlsx`
(gitignored; sheets ITEMS and README) and the tracked `MENTOR_SAMPLE_SHEET_v2.md` (same content; the pre-polish text in
small type). Columns `#`, `Question`, `Answer`, `Table side`, `Paper side`, `Original passages`; README of three lines.
Rules: `src/climrr/mentor_sheet_v2.py`.

    python scripts/build_mentor_sheet.py --items <synthesis run 4 output> [--polished <polish run 1 output>]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import mentor_sheet_v2 as ms  # noqa: E402
from climrr import synthpackets_v4 as v4  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.xlsxlite import write_xlsx  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--packets", type=Path, default=v4.PACKETS_DIR)
    ap.add_argument("--items", type=Path, required=True, help="synthesis run output directory (items/*.json)")
    ap.add_argument("--polished", type=Path, default=None, help="polish run output directory (items/*.json)")
    ap.add_argument("--out-md", type=Path, default=ms.MD_PATH)
    ap.add_argument("--out-xlsx", type=Path, default=ms.XLSX_PATH)
    a = ap.parse_args()
    man = json.loads((a.packets / "manifest.json").read_text(encoding="utf-8"))
    packets = {}
    for p in man["packets"]:
        f = a.packets / f"{p['packet_id']}.json"
        if sha256_file(f) != p["sha256"]:
            raise SystemExit(f"{f.name} differs from the packet manifest")
        packets[p["item_id"]] = json.loads(f.read_text(encoding="utf-8"))
    items = ms.load_items(man, a.items, a.polished)
    for iid, (it, _) in items.items():
        if it["generation"]["inputs_sha256"]["packet"] != next(p["sha256"] for p in man["packets"] if p["item_id"] == iid):
            raise SystemExit(f"{iid}: built from another packet than the manifest's")
    rs = ms.rows(man, packets, items)
    write_xlsx(a.out_xlsx, ms.sheets(rs))
    a.out_md.write_text(ms.render_md(rs, items), encoding="utf-8")
    result = {"rows": len(rs) - 1, "items": {iid: src for iid, (_, src) in items.items()},
              "polish_status": {iid: (ms.polish_event(it) or {}).get("status") for iid, (it, _) in items.items()},
              "missing": [p["item_id"] for p in man["packets"] if p["item_id"] not in items],
              "md_sha256": sha256_file(a.out_md), "xlsx_sha256": sha256_file(a.out_xlsx)}
    rec = write_run_record(
        "build_mentor_sheet", result_summary=result, passed=True, data_path=a.packets / "manifest.json", output_path=a.out_md,
        config_snapshot={"packets_manifest_sha256": sha256_file(a.packets / "manifest.json"), "items_dir": a.items.name,
                         "polished_dir": a.polished.name if a.polished else None, "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
