#!/usr/bin/env python3
"""Work package P3c, section B: the mentor sample sheet v2 (2026-11-19) from packets v4b and the ingested run 5 (no model call).

Reads the seed packets v4b (`artifacts/benchmark/synth_packets_v4b`, each checked against the manifest's SHA-256) and the
ingested synthesis run 5 (`artifacts/benchmark/items/run5`: `items/<item_id>.json` = run-5 item + polish-run-2 event +
human_review, each checked against the run manifest). Writes `artifacts/benchmark/review/MENTOR_SAMPLE_ITEMS_2026-11-19.xlsx`
(gitignored; sheets ITEMS and README) and the tracked `MENTOR_SAMPLE_ITEMS_2026-11-19.md` (same content). Seven rows in the
work package's order; columns `#`, `Question`, `Answer` (display text), `Table side`, `Paper side`, `Original passages`;
README of three lines. Rules: `src/climrr/mentor_sheet_v2b.py`. Sheet v2 (P3c hotfix, 2026-11-18): the COORDINATOR display
edits `artifacts/benchmark/review/P3_display_edits_v1.yaml` override five display texts (`display_source: coordinator_edit`)
and their checks (leakage v2.3, post-checks v3.1) are written to `P3_display_edits_v1_checks.json`; `--no-edits` rebuilds v1. (Until P3c this script built the P3a draft from packets v4
and raw run directories, `mentor_sheet_v2.py`; that version is held by its bytes at `f6f7543`.)

    python scripts/build_mentor_sheet.py [--packets <dir>] [--items <ingested run dir>] [--edits <yaml> | --no-edits]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litsynth_run5 as s5  # noqa: E402
from climrr import mentor_sheet_v2b as ms  # noqa: E402
from climrr import synthpackets_v4 as v4  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.xlsxlite import write_xlsx  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--packets", type=Path, default=v4.PACKETS_V4B_DIR)
    ap.add_argument("--items", type=Path, default=s5.ART, help="ingested synthesis run directory (manifest.json, items/)")
    ap.add_argument("--out-md", type=Path, default=ms.MD_PATH)
    ap.add_argument("--out-xlsx", type=Path, default=ms.XLSX_PATH)
    ap.add_argument("--edits", type=Path, default=ms.EDITS_PATH, help="COORDINATOR display edits (sheet v2)")
    ap.add_argument("--no-edits", action="store_true", help="rebuild sheet v1 (no display edits)")
    ap.add_argument("--out-checks", type=Path, default=ms.EDITS_CHECKS_PATH)
    a = ap.parse_args()
    man, packets = ms.load_packets(a.packets)
    items = ms.load_items(a.items, man)
    edits = {} if a.no_edits else ms.load_edits(a.edits)
    rs = ms.rows(packets, items, edits)
    version = None if a.no_edits else ms.SHEET_VERSION
    write_xlsx(a.out_xlsx, ms.sheets(rs))
    a.out_md.write_text(ms.render_md(rs, version), encoding="utf-8")
    checks = None
    if edits:
        checks = ms.edited_text_checks(items, packets, edits, edits_path=a.edits)
        a.out_checks.write_text(json.dumps(checks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    result = {"rows": len(rs) - 1, "sheet_version": version or 1, "order": [iid for iid, _ in ms.ORDER],
              "display_source": ms.display_sources(items, edits), "md_sha256": sha256_file(a.out_md),
              "xlsx_sha256": sha256_file(a.out_xlsx)}
    if checks is not None:
        result.update(edits_sha256=sha256_file(a.edits), edited_text_failures=checks["failures"],
                      checks_sha256=sha256_file(a.out_checks))
    rec = write_run_record(
        "build_mentor_sheet", result_summary=result, passed=True, data_path=a.packets / "manifest.json", output_path=a.out_md,
        config_snapshot={"packets_manifest_sha256": sha256_file(a.packets / "manifest.json"),
                         "items_manifest_sha256": sha256_file(a.items / "manifest.json"), "items_dir": repo_relative(a.items),
                         "sheet": ms.SHEET_DATE, "sheet_version": version or 1,
                         "edits": repo_relative(a.edits) if edits else None, "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
