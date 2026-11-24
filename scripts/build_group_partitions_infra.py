#!/usr/bin/env python3
"""Work package P5b, part B: the grouping agent's input partitions for the LITCORPUS-03 impact arm (D-075).

Reads `artifacts/litstatements/infra_run1/statements_ingested.jsonl` and `independence_v2.json` (both from
`scripts/ingest_litstatements_infra1.py`) and the pinned NCA5 map. Writes `artifacts/litgroups/partitions_infra_v1.jsonl`
(tracked; read by `scripts/litcollect/litgroup_agent.py` v3.1 on Polaris) and `partitions_infra_v1_summary.json`.
Rules: `src/climrr/litgroups_infra.py`. Deterministic; no model call, no table value.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import litgeo as lg  # noqa: E402
from climrr import litgroups_infra as lgi  # noqa: E402
from climrr import litstatements_infra1 as ir  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    records = sd.read_jsonl(ir.INGESTED_PATH)
    indep = json.loads(ir.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    parts, report = lgi.build_partitions(records, indep, lg.Gazetteer(sd.nca_map()))
    ir.write_jsonl(lgi.PARTITIONS_PATH, parts)
    summary = lgi.summarise(parts, report)
    summary["partitions_file"] = {"path": repo_relative(lgi.PARTITIONS_PATH), "sha256": sha256_file(lgi.PARTITIONS_PATH)}
    summary["inputs"] = {"statements_ingested_sha256": sha256_file(ir.INGESTED_PATH),
                         "independence_v2_sha256": sha256_file(ir.INDEPENDENCE_PATH),
                         "exclusions_sha256": sha256_file(lg.EXCLUSIONS_PATH), "nca_map_sha256": sd.NCA_MAP_SHA256}
    ir.write_json(lgi.SUMMARY_PATH, summary)
    rec = write_run_record(
        "build_group_partitions_infra", result_summary={k: v for k, v in summary.items() if k != "passing_not_partitioned_ids"},
        passed=True, data_path=ir.INGESTED_PATH, output_path=lgi.PARTITIONS_PATH,
        config_snapshot={"version": lgi.VERSION, "decision": lgi.DECISION, "min_class": lgi.MIN_CLASS, "chunk_size": lgi.CHUNK_SIZE,
                         "family_phrase": lgi.FAMILY_PHRASE, "geography": lg.VERSION, "model_calls": 0},
    )
    print(json.dumps({k: v for k, v in summary.items() if k != "passing_not_partitioned_ids"}, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
