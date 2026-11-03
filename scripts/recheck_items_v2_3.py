#!/usr/bin/env python3
"""Mentor-export package Phase B: post-checks v2.3 report-only re-run over the ten pilot items (no item changed).

Reads the current version of every pilot item from the items index (`artifacts/benchmark/items/index.json`, each checked
against its hash) and the packet each was built from (at the item's own source commit); re-runs `synthesis_post_checks`
v2.2 (must equal the recorded result) and v2.3 (v2.2 + the model-source leakage phrases); does the same for the
superseded run-2 BI-P2B-0010; and runs v2.3's leakage checks on the COORDINATOR-proposed texts
(`artifacts/benchmark/review/P2b_coordinator_edits_2026-11-03.yaml`). Writes
`artifacts/benchmark/items/post_checks_v2_3_report.json`. **Report only: no item is modified, no status changes.**
Rules: `src/climrr/benchmark_items.py` (`MODEL_SOURCE_RES`), `src/climrr/p2b_mentor_export.py`. No model call.

    python scripts/recheck_items_v2_3.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import benchmark_items as bi  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import litsynth_run3 as s3  # noqa: E402
from climrr import p2b_mentor_export as mx  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    items = s3.current_items()
    idx = json.loads(s3.INDEX_PATH.read_text(encoding="utf-8"))
    superseded = [json.loads((s3.ITEMS_ROOT / v["path"]).read_text(encoding="utf-8"))
                  for x in idx["items"] for v in x["versions"] if v["index_status"] != "current"]
    before = [sha256_file(s3.ITEMS_ROOT / v["path"]) for x in idx["items"] for v in x["versions"]]
    report = mx.recheck_v23(items, superseded, list(mx.edits().values()))
    report["inputs"] = {"items_index_sha256": sha256_file(s3.INDEX_PATH), "coordinator_edits_sha256": sha256_file(mx.EDITS_PATH)}
    r2.write_json(mx.RECHECK_PATH, report)
    if before != [sha256_file(s3.ITEMS_ROOT / v["path"]) for x in idx["items"] for v in x["versions"]]:
        raise SystemExit("an item file changed during the re-run")

    result = {"report_sha256": sha256_file(mx.RECHECK_PATH), "items_hit": report["items_hit"],
              "hits": {x["item_id"]: x["v2_3_new_reasons"] for x in report["current_items"] if x["hit"]},
              "superseded_hits": {x["item_id"]: x["v2_3_new_reasons"] for x in report["superseded_items"] if x["hit"]},
              "coordinator_proposed_hits": {x["item_id"]: x["prompt"] + x["reference_integrated"]
                                            for x in report["coordinator_proposed_texts"] if x["prompt"] or x["reference_integrated"]}}
    rec = write_run_record("recheck_items_v2_3", result_summary=result, passed=True, data_path=s3.INDEX_PATH, output_path=mx.RECHECK_PATH,
                           config_snapshot={"check_version": bi.SYNTH_CHECK_VERSION_V23, "patterns": report["patterns"],
                                            "report_only": True, "items_modified": 0, "model_calls": 0})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
