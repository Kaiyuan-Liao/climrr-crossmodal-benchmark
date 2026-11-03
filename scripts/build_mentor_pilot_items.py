#!/usr/bin/env python3
"""Mentor sheet v2 package, section D: the five-item mentor sheet for 2026-11-05, rebuilt from the v2 texts (no model call;
nothing frozen).

Reads the current pilot items (items index, each checked against its hash) and the packets they were built from, the
COORDINATOR-proposed texts v2 (`artifacts/benchmark/review/P2b_coordinator_edits_2026-11-03_v2.yaml`, pinned), the EXECUTOR
support map v2 (`P2b_mentor_support_map_v2.yaml`: groups, member statements and the sentence-support verdicts), the
provenance corrections v1 (D-057; overlay, re-slice status from `artifacts/litstatements/corrections/
provenance_corrections_v1_applied.json`), DR-DESC-1 v2 (`descriptor_rules_v2.yaml`), the literature statements (verbatim
passages), the data dictionary text, the NCA5 map and, for the regional item, `artifacts/benchmark/table_patterns_v1.jsonl`
(gitignored; pinned). Writes `artifacts/benchmark/review/MENTOR_PILOT_ITEMS_2026-11-05.xlsx` (gitignored; sheets ITEMS and
README), the tracked `MENTOR_PILOT_ITEMS_2026-11-05.md` (same content) and `MENTOR_PILOT_ITEMS_2026-11-05_v2_checks.json`
(post-checks v2.3 leakage on the v2 texts, the sentence-support verdicts, the v2 descriptors). Rules:
`src/climrr/p2b_mentor_v2.py`, `src/climrr/p2b_mentor_export.py`.

    python scripts/build_mentor_pilot_items.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import litstatements as ls  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import litsynth_run3 as s3  # noqa: E402
from climrr import p2b_mentor_export as mx  # noqa: E402
from climrr import p2b_mentor_v2 as m2  # noqa: E402
from climrr import pattern_descriptors as pd  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.xlsxlite import write_xlsx  # noqa: E402


def main() -> int:
    items = {it["item_id"]: it for it in s3.current_items()}
    ed, smap = m2.edits_v2(), m2.support_map_v2()
    if sorted(ed) != sorted(smap):
        raise SystemExit(f"edits name {sorted(ed)}, the support map {sorted(smap)}")
    corrections = ls.load_provenance_corrections()
    applied = json.loads(m2.APPLIED_PATH.read_text(encoding="utf-8"))
    if applied["corrections_file"]["sha256"] != sha256_file(ls.CORRECTIONS_PATH):
        raise SystemExit("the applied overlay was built from another corrections file: re-run apply_provenance_corrections.py")
    reslices = applied["reslices"]
    descs = m2.descriptors_v2(items, list(ed))
    rows = m2.mentor_rows_v2(items, ed, smap, corrections, reslices, descs)
    write_xlsx(mx.MENTOR_XLSX_PATH, m2.sheets_v2(rows))
    mx.MENTOR_MD_PATH.write_text(m2.render_md_v2(rows), encoding="utf-8")
    checks = m2.checks_record(ed, smap, descs, m2.edited_texts_check(ed))
    r2.write_json(m2.CHECKS_V2_PATH, checks)

    result = {"md_sha256": sha256_file(mx.MENTOR_MD_PATH), "xlsx_sha256": sha256_file(mx.MENTOR_XLSX_PATH),
              "checks_sha256": sha256_file(m2.CHECKS_V2_PATH), "rows": len(rows) - 1, "items": list(ed),
              "leakage_v2_3_hits": checks["leakage_hits"], "clause_verdicts": checks["clause_verdicts"],
              "not_fully_supported": checks["not_fully_supported"],
              "reslices": {k: v["reslice"] for k, v in reslices.items()},
              "descriptors_v2_changed": {k: v["changed"] for k, v in descs.items() if v["changed"]}}
    rec = write_run_record(
        "build_mentor_pilot_items", result_summary=result, passed=True, data_path=s3.INDEX_PATH, output_path=mx.MENTOR_MD_PATH,
        config_snapshot={"items_index_sha256": sha256_file(s3.INDEX_PATH), "coordinator_edits_v2_sha256": sha256_file(m2.EDITS_V2_PATH),
                         "support_map_v2_sha256": sha256_file(m2.SUPPORT_MAP_V2_PATH), "statements_sha256": sha256_file(mx.STATEMENTS_PATH),
                         "corrections_sha256": sha256_file(ls.CORRECTIONS_PATH), "corrections_applied_sha256": sha256_file(m2.APPLIED_PATH),
                         "descriptor_rules_v2_sha256": sha256_file(pd.RULES_V2_PATH), "table_patterns_sha256": sd.PATTERNS_SHA256,
                         "passage_max_chars": mx.PASSAGE_MAX, "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
