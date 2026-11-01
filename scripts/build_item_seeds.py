#!/usr/bin/env python3
"""Pilot P2a Phase C: item seeds --- table patterns paired with literature-statement clusters (DR-SEED-1; D-045).

Reads `artifacts/benchmark/table_patterns_v1.jsonl` (gitignored, checked against its
pinned SHA-256), `artifacts/litstatements/run2/clusters_v1.jsonl` and the pinned NCA5 map.
Writes `artifacts/benchmark/item_seeds_v1.jsonl` (gitignored, regenerable; pinned in the
summary) and the tracked `item_seeds_v1_summary.json`; prints the ten highest-ranked
eligible seeds. Rules: `src/climrr/itemseeds.py`. Deterministic; no model call, no table value computed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import litaggregate as la  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    for path, pin in ((sd.PATTERNS_PATH, sd.PATTERNS_SHA256), (sd.NCA_MAP_PATH, sd.NCA_MAP_SHA256)):
        if not path.is_file() or sha256_file(path) != pin:
            raise SystemExit(f"{repo_relative(path)} is absent or differs from its pin {pin}")
    patterns = sd.read_jsonl(sd.PATTERNS_PATH)
    clusters = sd.read_jsonl(la.CLUSTERS_PATH)
    nca = sd.nca_map()
    seeds = sd.build(patterns, clusters, nca)
    r2.write_jsonl(sd.SEEDS_PATH, seeds)
    summary = sd.summarise(seeds, clusters, nca)
    r2.write_json(sd.SUMMARY_PATH, summary)

    result = {k: summary[k] for k in ("seeds", "eligible", "eligible_without_diagnostic_pair", "eligible_not_computable_excluded",
                                      "by_level", "eligible_by_level", "levels_applicable", "by_family", "eligible_by_family", "fwi",
                                      "eligible_cluster_ids")}
    result.update({"seeds_sha256": summary["seeds_file"]["sha256"], "summary_sha256": sha256_file(sd.SUMMARY_PATH)})
    rec = write_run_record(
        "build_item_seeds", result_summary=result, passed=True, data_path=sd.PATTERNS_PATH, output_path=sd.SEEDS_PATH,
        config_snapshot={"rule": sd.RULE_ID, "version": sd.VERSION, "clusters_sha256": summary["inputs"]["clusters"]["sha256"],
                         "nca_map_sha256": sd.NCA_MAP_SHA256, "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\nTen highest-ranked eligible seeds:")
    for t in summary["top_eligible"]:
        print(f"\n{t['seed_rank_key']}. {t['seed_id']} (level {t['use_case_level']}; blockers {t['acceptance_blockers']}"
              f"{'; RELIES ON DIAGNOSTIC PAIR' if t['eligibility_relies_on_diagnostic_pair'] else ''})\n   {t['pattern_summary']}")
        for c in t["top_clusters"]:
            print(f"   - [{c['rank']}] {c['cluster_id']} {c['evidence_strength']} {c['relevance']} ({c['geography_match']}), "
                  f"n_papers={c['n_papers']}: {c['representative']}")
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
