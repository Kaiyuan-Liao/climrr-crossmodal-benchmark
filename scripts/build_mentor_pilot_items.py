#!/usr/bin/env python3
"""Mentor-export package Phase C: the five-item mentor sheet for 2026-11-05 (no model call; nothing frozen).

Reads the current pilot items (items index, each checked against its hash) and the packets they were built from, the
COORDINATOR-proposed texts (`artifacts/benchmark/review/P2b_coordinator_edits_2026-11-03.yaml`), the EXECUTOR support map
(`P2b_mentor_support_map_v1.yaml`: the groups and member statements each answer uses), the literature statements
(`artifacts/litstatements/run2/statements.jsonl`, verbatim passages), the data dictionary text and, for the regional item,
`artifacts/benchmark/table_patterns_v1.jsonl` (gitignored; pinned). Writes
`artifacts/benchmark/review/MENTOR_PILOT_ITEMS_2026-11-05.xlsx` (gitignored; sheets ITEMS and README) and the tracked
`MENTOR_PILOT_ITEMS_2026-11-05.md` (same content). Rules: `src/climrr/p2b_mentor_export.py`.

    python scripts/build_mentor_pilot_items.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import litsynth_run3 as s3  # noqa: E402
from climrr import p2b_mentor_export as mx  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.xlsxlite import write_xlsx  # noqa: E402


def main() -> int:
    items = {it["item_id"]: it for it in s3.current_items()}
    ed, smap = mx.edits(), mx.support_map()
    if sorted(ed) != sorted(smap):
        raise SystemExit(f"edits name {sorted(ed)}, the support map {sorted(smap)}")
    for iid, e in ed.items():
        missing = [c["text"] for c in smap[iid]["clauses"] if c["text"] not in e["edited_reference_integrated"]]
        if missing:
            raise SystemExit(f"{iid}: support-map clauses not in the edited answer: {missing}")
    rows = mx.mentor_rows(items, ed, smap)
    write_xlsx(mx.MENTOR_XLSX_PATH, mx.sheets(rows))
    mx.MENTOR_MD_PATH.write_text(mx.render_md(rows), encoding="utf-8")

    verdicts: dict = {}
    for iid in ed:
        for c in smap[iid]["clauses"]:
            verdicts.setdefault(c["verdict"], []).append(iid)
    result = {"md_sha256": sha256_file(mx.MENTOR_MD_PATH), "xlsx_sha256": sha256_file(mx.MENTOR_XLSX_PATH), "rows": len(rows) - 1,
              "items": list(ed), "clause_verdicts": {k: len(v) for k, v in sorted(verdicts.items())},
              "not_fully_supported": {k: v for k, v in verdicts.items() if k not in ("supported", "guardrail")}}
    rec = write_run_record(
        "build_mentor_pilot_items", result_summary=result, passed=True, data_path=s3.INDEX_PATH, output_path=mx.MENTOR_MD_PATH,
        config_snapshot={"items_index_sha256": sha256_file(s3.INDEX_PATH), "coordinator_edits_sha256": sha256_file(mx.EDITS_PATH),
                         "support_map_sha256": sha256_file(mx.SUPPORT_MAP_PATH), "statements_sha256": sha256_file(mx.STATEMENTS_PATH),
                         "table_patterns_sha256": sd.PATTERNS_SHA256, "passage_max_chars": mx.PASSAGE_MAX, "model_calls": 0},
    )
    print(json.dumps(result, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
