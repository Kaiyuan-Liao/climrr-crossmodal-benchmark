#!/usr/bin/env python3
"""Mentor sheet v3 package, section A: apply the reviewer-verified provenance corrections v1a (D-057, D-058) as an overlay.

Reads `data/metadata/benchmark/provenance_corrections_v1a.yaml` (manifest-pinned; v1 plus the Polaris re-slice of the
corrected passage, a corrected statement and the group label overrides), the literature statements
(`artifacts/litstatements/run2/statements_ingested.jsonl`), the groups (`artifacts/litgroups/run2/groups_enriched.jsonl`),
the independence map, the current pilot items (items index, each checked against its hash), the packets they were built
from and the EXECUTOR support map v3 (which mentor items show each overlay). Takes the recorded re-slice, checked for
consistency with the passage, and against an exact local re-slice when the paper JSON is under a configured corpus root on
this machine. Writes `artifacts/litstatements/corrections/provenance_corrections_v1a_applied.json`: the corrected
statement record, every affected group's strength recomputed (group file and per packet), every affected item's
`provenance_corrections_applied`, the label overrides, and where each overlay is applied (`uses`). The v1 record
(`provenance_corrections_v1_applied.json`) is kept as built. **No statement, group, packet or item file is modified**
(checked). Rules: `src/climrr/litstatements.py`, `src/climrr/p2b_mentor_v2.py`, `src/climrr/p2b_mentor_v3.py`.

    python scripts/apply_provenance_corrections.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litstatements as ls  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import litsynth_run2 as s2  # noqa: E402
from climrr import litsynth_run3 as s3  # noqa: E402
from climrr import p2b_mentor_export as mx  # noqa: E402
from climrr import p2b_mentor_v2 as m2  # noqa: E402
from climrr import p2b_mentor_v3 as m3  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    watched = [mx.STATEMENTS_PATH, mx.STATEMENTS_INGESTED_PATH, m2.GROUPS_ENRICHED_PATH, s3.INDEX_PATH]
    before = [sha256_file(p) for p in watched]
    corrections, overrides = m3.corrections_v1a()
    items = s3.current_items()
    packets = {it["item_id"]: s2.packet_for_item(it) for it in items}
    item_files = [sha256_file(s3.ITEMS_ROOT / x["current"]["path"])
                  for x in json.loads(s3.INDEX_PATH.read_text(encoding="utf-8"))["items"]]
    statements = {r["statement_id"]: r for r in ls.load_statements(mx.STATEMENTS_INGESTED_PATH)}
    reslices = m3.reslices_v1a(corrections, statements)
    rec = m3.applied_record_v1a(corrections, overrides, items, packets, reslices, m3.support_map_v3())
    r2.write_json(m3.APPLIED_V1A_PATH, rec)
    after_items = [sha256_file(s3.ITEMS_ROOT / x["current"]["path"])
                   for x in json.loads(s3.INDEX_PATH.read_text(encoding="utf-8"))["items"]]
    if before != [sha256_file(p) for p in watched] or item_files != after_items:
        raise SystemExit("a statements, groups, index or item file changed during the overlay")

    result = {"applied_sha256": sha256_file(m3.APPLIED_V1A_PATH), "corrections_sha256": rec["corrections_file"]["sha256"],
              "reslices": {k: {f: v[f] for f in ("reslice", "span_start", "span_end", "occurrences", "verified_on")}
                           for k, v in reslices.items()},
              "groups": {g["group_id"]: {"before": g["strength_before"], "after": g["strength_after"],
                                         "stays_multi_source": g["stays_multi_source"],
                                         "core_cited_papers_after": g["core_cited_papers_after"]} for g in rec["groups"]},
              "corrected_statements": {r["statement_id"]: r["proposal"]["statement"] for r in rec["corrected_statements"]},
              "group_label_overrides": {o["group_id"]: o["label"] for o in rec["group_label_overrides"]},
              "items_with_corrections_applied": [x["item_id"] for x in rec["items"]], "files_modified": 0}
    run = write_run_record(
        "apply_provenance_corrections", result_summary=result, passed=True, data_path=ls.CORRECTIONS_V1A_PATH,
        output_path=m3.APPLIED_V1A_PATH,
        config_snapshot={"corrections": repo_relative(ls.CORRECTIONS_V1A_PATH), "items_index_sha256": sha256_file(s3.INDEX_PATH),
                         "statements_ingested_sha256": sha256_file(mx.STATEMENTS_INGESTED_PATH),
                         "groups_enriched_sha256": sha256_file(m2.GROUPS_ENRICHED_PATH),
                         "support_map_v3_sha256": sha256_file(m3.SUPPORT_MAP_V3_PATH), "corpus_root_keys": list(m2.CORPUS_ROOT_KEYS),
                         "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(run)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
