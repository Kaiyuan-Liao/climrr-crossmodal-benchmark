#!/usr/bin/env python3
"""Pilot P2a Phase B: deterministic cross-paper aggregation of run-2 literature statements (DR-LIT-AGG-1 v2; D-045).

Reads `artifacts/litstatements/run2/statements_ingested.jsonl` and `papers_meta.json`
(written by `scripts/ingest_litstatements.py`). Writes the two generated frequency
files `data/metadata/litstatements/concept_lexicon_v1.yaml` (reported, not used for
merging) and `df_filter_dropped_v1.yaml`, then `artifacts/litstatements/run2/clusters_v1.jsonl`
and `clusters_v1_summary.json` (counts by arm x type x strength, the ten largest
clusters, the cosine / Jaccard threshold grid, and the replay of the first rule).
Rules: `src/climrr/litaggregate.py`. Deterministic; no model call, no table value.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litaggregate as la  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    records = [json.loads(ln) for ln in r2.INGESTED_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
    meta = json.loads(r2.PAPERS_META_PATH.read_text(encoding="utf-8"))
    ingested_sha = sha256_file(r2.INGESTED_PATH)

    p = la.Prepared(records)
    lexicon = la.concept_lexicon(p.ent, p.stop)
    la.CONCEPT_LEXICON.write_text(la.render_concept_lexicon(lexicon, ingested_sha), encoding="utf-8")
    la.DF_DROPPED.write_text(la.render_df_dropped(p, ingested_sha), encoding="utf-8")

    clusters = la.cluster_records(p, la.clusters_at(p), meta)
    r2.write_jsonl(la.CLUSTERS_PATH, clusters)
    summary = la.summarise(clusters, p, meta, lexicon)
    r2.write_json(la.SUMMARY_PATH, summary)

    over = [r for r in summary["sensitivity"] if r["clusters_over_25"]]
    result = {k: summary[k] for k in ("rule", "threshold", "entering_statements", "clusters", "singletons",
                                      "by_strength", "multi_source_relies_on_diagnostic_pair")}
    result.update({"clusters_sha256": summary["clusters_file"]["sha256"], "summary_sha256": sha256_file(la.SUMMARY_PATH),
                   "lexicons": {k: v["sha256"] for k, v in summary["lexicons"].items()},
                   "grid_thresholds_with_cluster_over_25": [(r["measure"], r["threshold"]) for r in over]})
    rec = write_run_record(
        "aggregate_litstatements", result_summary=result, passed=True, data_path=r2.INGESTED_PATH, output_path=la.CLUSTERS_PATH,
        config_snapshot={"rule": la.RULE_ID, "threshold": la.THRESHOLD, "grid": list(la.GRID), "df_max_share": la.DF_MAX_SHARE,
                         "lexicon_top": la.LEXICON_TOP, "version": la.VERSION, "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
