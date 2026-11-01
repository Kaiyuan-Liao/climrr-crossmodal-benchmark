#!/usr/bin/env python3
"""Pilot P2b-prep Phase B: the grouping agent's input partitions (D-048).

Reads `artifacts/litstatements/run2/statements_ingested.jsonl`, `independence_v2.json`
and the pinned NCA5 map. Writes `artifacts/litgroups/partitions_v1.jsonl` (tracked; read by
`scripts/litcollect/litgroup_agent.py` on Polaris) and `partitions_v1_summary.json`.
Rules: `src/climrr/litgroups.py`. Deterministic; no model call, no table value.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import litgeo as lg  # noqa: E402
from climrr import litgroups as lgr  # noqa: E402
from climrr import litindependence as li  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    records = sd.read_jsonl(r2.INGESTED_PATH)
    indep = json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    parts = lgr.build_partitions(records, indep, lg.Gazetteer(sd.nca_map()))
    r2.write_jsonl(lgr.PARTITIONS_PATH, parts)
    summary = lgr.summarise_partitions(parts)
    summary["partitions_file"] = {"path": "artifacts/litgroups/partitions_v1.jsonl", "sha256": sha256_file(lgr.PARTITIONS_PATH)}
    summary["inputs"] = {"statements_ingested_sha256": sha256_file(r2.INGESTED_PATH),
                         "independence_v2_sha256": sha256_file(li.INDEPENDENCE_PATH),
                         "exclusions_sha256": sha256_file(lg.EXCLUSIONS_PATH)}
    r2.write_json(lgr.PARTITIONS_SUMMARY_PATH, summary)
    rec = write_run_record(
        "build_group_partitions", result_summary=summary, passed=True, data_path=r2.INGESTED_PATH, output_path=lgr.PARTITIONS_PATH,
        config_snapshot={"version": lgr.VERSION, "max_partition": lgr.MAX_PARTITION, "family_phrase": lgr.FAMILY_PHRASE, "model_calls": 0},
    )
    print(json.dumps(summary, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
