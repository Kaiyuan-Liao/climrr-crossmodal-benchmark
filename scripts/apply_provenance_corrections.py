#!/usr/bin/env python3
"""Mentor sheet v2 package, section A: apply the reviewer-verified provenance corrections v1 (D-057) as an overlay.

Reads `data/metadata/benchmark/provenance_corrections_v1.yaml` (manifest-pinned), the literature statements
(`artifacts/litstatements/run2/statements_ingested.jsonl`), the groups (`artifacts/litgroups/run2/groups_enriched.jsonl`),
the independence map, the current pilot items (items index, each checked against its hash) and the packets they were built
from. Re-slices each corrected passage exactly in the paper's own text when the paper JSON is under a configured corpus
root on this machine; otherwise records `reslice: pending_polaris` and the one-line Polaris command. Writes
`artifacts/litstatements/corrections/provenance_corrections_v1_applied.json`: the corrected statement record, every
affected group's strength recomputed (group file and per packet), every affected item's
`provenance_corrections_applied`. **No statement, group, packet or item file is modified** (checked). Rules:
`src/climrr/litstatements.py`, `src/climrr/p2b_mentor_v2.py`.

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
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    watched = [mx.STATEMENTS_PATH, mx.STATEMENTS_INGESTED_PATH, m2.GROUPS_ENRICHED_PATH, s3.INDEX_PATH]
    before = [sha256_file(p) for p in watched]
    corrections = ls.load_provenance_corrections()
    items = s3.current_items()
    packets = {it["item_id"]: s2.packet_for_item(it) for it in items}
    item_files = [sha256_file(s3.ITEMS_ROOT / x["current"]["path"])
                  for x in json.loads(s3.INDEX_PATH.read_text(encoding="utf-8"))["items"]]
    statements = {r["statement_id"]: r for r in ls.load_statements(mx.STATEMENTS_INGESTED_PATH)}
    reslices = m2.local_reslices(corrections, statements)
    rec = m2.applied_record(corrections, items, packets, reslices)
    r2.write_json(m2.APPLIED_PATH, rec)
    after_items = [sha256_file(s3.ITEMS_ROOT / x["current"]["path"])
                   for x in json.loads(s3.INDEX_PATH.read_text(encoding="utf-8"))["items"]]
    if before != [sha256_file(p) for p in watched] or item_files != after_items:
        raise SystemExit("a statements, groups, index or item file changed during the overlay")

    result = {"applied_sha256": sha256_file(m2.APPLIED_PATH), "corrections_sha256": rec["corrections_file"]["sha256"],
              "reslices": {k: v["reslice"] for k, v in reslices.items()},
              "groups": {g["group_id"]: {"before": g["strength_before"], "after": g["strength_after"],
                                         "stays_multi_source": g["stays_multi_source"],
                                         "core_cited_papers_after": g["core_cited_papers_after"]} for g in rec["groups"]},
              "items_with_corrections_applied": [x["item_id"] for x in rec["items"]], "files_modified": 0}
    run = write_run_record(
        "apply_provenance_corrections", result_summary=result, passed=True, data_path=ls.CORRECTIONS_PATH, output_path=m2.APPLIED_PATH,
        config_snapshot={"corrections": repo_relative(ls.CORRECTIONS_PATH), "items_index_sha256": sha256_file(s3.INDEX_PATH),
                         "statements_ingested_sha256": sha256_file(mx.STATEMENTS_INGESTED_PATH),
                         "groups_enriched_sha256": sha256_file(m2.GROUPS_ENRICHED_PATH), "corpus_root_keys": list(m2.CORPUS_ROOT_KEYS),
                         "model_calls": 0},
    )
    print(json.dumps(result, indent=2))
    print(f"run record: {repo_relative(run)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
