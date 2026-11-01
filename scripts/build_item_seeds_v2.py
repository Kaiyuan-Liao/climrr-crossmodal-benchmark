#!/usr/bin/env python3
"""Pilot P2b-prep Phase A: clusters v1b, region-string classification and item seeds v2 (D-046, D-047, D-048).

Reads the pinned table patterns and NCA5 map, `statements_ingested.jsonl`,
`clusters_v1.jsonl`, `independence_v2.json` (`scripts/build_independence_v2.py`) and
`region_match_exclusions_v1.yaml`. Writes:

- `artifacts/litstatements/run2/clusters_v1b.jsonl` + `clusters_v1b_summary.json` --- the v1
  clusters, same members, strengths under DR-LIT-IND-1 v2;
- `artifacts/litstatements/run2/region_strings_v1.csv` --- every distinct (region string,
  scope) of the 747 entering statements with its count, the v2 classification and the rule
  that fired (inspection file, generated);
- `artifacts/benchmark/item_seeds_v2.jsonl` (gitignored, pinned in the summary) and the
  tracked `item_seeds_v2_summary.json`.

Rules: `src/climrr/litindependence.py`, `litgeo.py`, `itemseeds_v2.py`. Deterministic; no
model call, no table value computed.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import itemseeds_v2 as s2  # noqa: E402
from climrr import litaggregate as la  # noqa: E402
from climrr import litgeo as lg  # noqa: E402
from climrr import litindependence as li  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    for path, pin in ((sd.PATTERNS_PATH, sd.PATTERNS_SHA256), (sd.NCA_MAP_PATH, sd.NCA_MAP_SHA256)):
        if not path.is_file() or sha256_file(path) != pin:
            raise SystemExit(f"{repo_relative(path)} is absent or differs from its pin {pin}")
    records = sd.read_jsonl(r2.INGESTED_PATH)
    indep = json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8"))

    v1b = li.clusters_v1b(sd.read_jsonl(la.CLUSTERS_PATH), indep)
    r2.write_jsonl(li.CLUSTERS_V1B_PATH, v1b)
    v1b_summary = li.summarise_v1b(v1b, indep)
    r2.write_json(li.CLUSTERS_V1B_SUMMARY_PATH, v1b_summary)

    nca = sd.nca_map()
    gz = lg.Gazetteer(nca)
    ent = la.entering(records)
    region_rows = lg.region_rows(ent, gz)
    with open(s2.REGION_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=lg.CSV_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(region_rows)

    rows = s2.statement_table(records, v1b, indep, gz)
    seeds = s2.build(sd.read_jsonl(sd.PATTERNS_PATH), rows, v1b, nca, indep)
    r2.write_jsonl(s2.SEEDS_PATH, seeds)
    v1_summary = json.loads(sd.SUMMARY_PATH.read_text(encoding="utf-8"))
    summary = s2.summarise(seeds, rows, region_rows, v1_summary)
    r2.write_json(s2.SUMMARY_PATH, summary)

    result = {"clusters_v1b_by_strength": v1b_summary["by_strength"], "clusters_v1b_strength_changed": len(v1b_summary["strength_changed"]),
              **{k: summary[k] for k in ("region_string_classification", "seeds", "eligible", "eligible_v1", "eligible_by_family",
                                         "eligible_by_level", "eligible_heat_index_by_level", "fwi")},
              "statement_geography": {k: v for k, v in summary["statement_geography"].items() if k != "by_arm_type"},
              "clusters_v1b_sha256": v1b_summary["clusters_file"]["sha256"],
              "region_strings_sha256": summary["region_strings_file"]["sha256"],
              "seeds_sha256": summary["seeds_file"]["sha256"], "summary_sha256": sha256_file(s2.SUMMARY_PATH)}
    rec = write_run_record(
        "build_item_seeds_v2", result_summary=result, passed=True, data_path=sd.PATTERNS_PATH, output_path=s2.SEEDS_PATH,
        config_snapshot={"rule": s2.RULE_ID, "decisions": list(s2.DECISIONS), "version": s2.VERSION, "geo_version": lg.VERSION,
                         "independence_sha256": sha256_file(li.INDEPENDENCE_PATH),
                         "exclusions_sha256": sha256_file(lg.EXCLUSIONS_PATH), "nca_map_sha256": sd.NCA_MAP_SHA256, "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
