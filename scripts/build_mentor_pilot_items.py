#!/usr/bin/env python3
"""Mentor sheet v3 package, section C: the five-item mentor sheet for 2026-11-05, rebuilt from the v3 texts (no model call;
nothing frozen).

Reads the current pilot items (items index, each checked against its hash) and the packets they were built from, the
COORDINATOR-proposed texts v3 (`artifacts/benchmark/review/P2b_coordinator_edits_2026-11-03_v3.yaml`, pinned), the EXECUTOR
support map v3 (`P2b_mentor_support_map_v3.yaml`: groups, member statements and the sentence-support verdicts), the
provenance corrections v1a (D-057, D-058; overlay: corrected passage and statement, reviewer group label; re-slice from
`artifacts/litstatements/corrections/provenance_corrections_v1a_applied.json`), DR-DESC-1 v2 (`descriptor_rules_v2.yaml`),
the literature statements (verbatim passages), the data dictionary text, the NCA5 map and, for the regional item,
`artifacts/benchmark/table_patterns_v1.jsonl` (gitignored; pinned). Writes
`artifacts/benchmark/review/MENTOR_PILOT_ITEMS_2026-11-05.xlsx` (gitignored; sheets ITEMS and README; the agent's group
label in a small run), the tracked `MENTOR_PILOT_ITEMS_2026-11-05.md` (same content; `<small>`) and
`MENTOR_PILOT_ITEMS_2026-11-05_v3_checks.json` (post-checks v2.3 leakage on the v3 texts, the sentence-support verdicts,
the clauses changed since v2, the v2 descriptors). The v2 checks file is kept as built. Rules:
`src/climrr/p2b_mentor_v3.py`, `src/climrr/p2b_mentor_v2.py`, `src/climrr/p2b_mentor_export.py`.

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
from climrr import p2b_mentor_v3 as m3  # noqa: E402
from climrr import pattern_descriptors as pd  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.xlsxlite import write_xlsx  # noqa: E402


def main() -> int:
    items = {it["item_id"]: it for it in s3.current_items()}
    ed, smap = m3.edits_v3(), m3.support_map_v3()
    if sorted(ed) != sorted(smap):
        raise SystemExit(f"edits name {sorted(ed)}, the support map {sorted(smap)}")
    corrections, overrides = m3.corrections_v1a()
    applied = json.loads(m3.APPLIED_V1A_PATH.read_text(encoding="utf-8"))
    if applied["corrections_file"]["sha256"] != sha256_file(ls.CORRECTIONS_V1A_PATH):
        raise SystemExit("the applied overlay was built from another corrections file: re-run apply_provenance_corrections.py")
    reslices = applied["reslices"]
    descs = m2.descriptors_v2(items, list(ed))
    rows = m3.mentor_rows_v3(items, ed, smap, corrections, overrides, reslices, descs)
    write_xlsx(mx.MENTOR_XLSX_PATH, m3.sheets_v3(rows))
    mx.MENTOR_MD_PATH.write_text(m3.render_md_v3(rows), encoding="utf-8")
    checks = m3.checks_record_v3(ed, smap, descs, m2.edited_texts_check(ed))
    r2.write_json(m3.CHECKS_V3_PATH, checks)

    result = {"md_sha256": sha256_file(mx.MENTOR_MD_PATH), "xlsx_sha256": sha256_file(mx.MENTOR_XLSX_PATH),
              "checks_sha256": sha256_file(m3.CHECKS_V3_PATH), "rows": len(rows) - 1, "items": list(ed),
              "leakage_v2_3_hits": checks["leakage_hits"], "clause_verdicts": checks["clause_verdicts"],
              "not_fully_supported": checks["not_fully_supported"],
              "reslices": {k: v["reslice"] for k, v in reslices.items()},
              "group_label_overrides": [o["group_id"] for o in overrides],
              "descriptors_v2_changed": {k: v["changed"] for k, v in descs.items() if v["changed"]}}
    rec = write_run_record(
        "build_mentor_pilot_items", result_summary=result, passed=True, data_path=s3.INDEX_PATH, output_path=mx.MENTOR_MD_PATH,
        config_snapshot={"items_index_sha256": sha256_file(s3.INDEX_PATH), "coordinator_edits_v3_sha256": sha256_file(m3.EDITS_V3_PATH),
                         "support_map_v3_sha256": sha256_file(m3.SUPPORT_MAP_V3_PATH), "statements_sha256": sha256_file(mx.STATEMENTS_PATH),
                         "corrections_sha256": sha256_file(ls.CORRECTIONS_V1A_PATH),
                         "corrections_applied_sha256": sha256_file(m3.APPLIED_V1A_PATH),
                         "descriptor_rules_v2_sha256": sha256_file(pd.RULES_V2_PATH), "table_patterns_sha256": sd.PATTERNS_SHA256,
                         "passage_max_chars": mx.PASSAGE_MAX, "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
