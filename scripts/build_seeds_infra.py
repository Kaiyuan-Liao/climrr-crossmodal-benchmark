#!/usr/bin/env python3
"""Work package P5b, part C (implemented; runs in P5c): rung-8 seeds (DR-SEED-INFRA-1) and the rung-8 pilot selection (D-075).

Runs after the infra grouping run (`litgroups/infra_run1`) is ingested. Reads the v3 seeds (pinned), the ingested infra
statements and their independence, and the infra groups (`--groups`: the grouping run's `groups.jsonl`); writes
`artifacts/benchmark/item_seeds_infra_v1.jsonl` (+ summary) and `artifacts/benchmark/pilot_selection_rung8_v1.json`.
Rules: `src/climrr/seeds_infra.py`. Deterministic; no model call, no table value computed.

    python scripts/build_seeds_infra.py --groups artifacts/litgroups/infra_run1/groups.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import itemseeds_v3 as s3  # noqa: E402
from climrr import litgeo as lg  # noqa: E402
from climrr import litstatements_infra1 as ir  # noqa: E402
from climrr import seeds_infra as si  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--groups", required=True, type=Path, help="the infra grouping run's groups.jsonl (ingested)")
    a = ap.parse_args()
    pin = json.loads(s3.SUMMARY_PATH.read_text(encoding="utf-8"))["seeds_file"]["sha256"]
    if not s3.SEEDS_PATH.is_file() or sha256_file(s3.SEEDS_PATH) != pin:
        raise SystemExit(f"{repo_relative(s3.SEEDS_PATH)} is absent or differs from its pin {pin}; run scripts/build_item_seeds_v3.py")
    seeds_v3 = sd.read_jsonl(s3.SEEDS_PATH)
    records = sd.read_jsonl(ir.INGESTED_PATH)
    indep = json.loads(ir.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    groups = sd.read_jsonl(a.groups)
    ctx = si.Context(records, indep, lg.Gazetteer(sd.nca_map()))
    seeds = si.build_seeds(seeds_v3, groups, ctx, si.rung3_driver_ids_factory())
    ir.write_jsonl(si.SEEDS_PATH, seeds)
    forms = si.load_question_forms_v2()
    sel = si.select_pilot(seeds, seeds_v3, records, ctx, forms)
    ir.write_json(si.SELECTION_PATH, sel)
    summary = {"version": si.VERSION, "rule": si.RULE_ID, "decision": si.DECISION, "seeds": len(seeds),
               "by_family_class": dict(sorted(Counter(f"{s['family']}|{s['asset_class']}" for s in seeds).items())),
               "by_best_relevance": dict(sorted(Counter(s["best_relevance"] for s in seeds).items())),
               "seeds_file": {"path": repo_relative(si.SEEDS_PATH), "sha256": sha256_file(si.SEEDS_PATH)},
               "selection_file": {"path": repo_relative(si.SELECTION_PATH), "sha256": sha256_file(si.SELECTION_PATH)},
               "selected": [{k: x[k] for k in ("order", "family", "asset_class", "state", "seed_id", "question_form_id")} for x in sel["selected"]],
               "missing": sel["missing"],
               "inputs": {"item_seeds_v3": pin, "statements_ingested": sha256_file(ir.INGESTED_PATH),
                          "independence_v2": sha256_file(ir.INDEPENDENCE_PATH), "groups": sha256_file(a.groups),
                          "question_forms_v2": forms["sha256"]}}
    ir.write_json(si.SEEDS_SUMMARY_PATH, summary)
    rec = write_run_record("build_seeds_infra", result_summary=summary, passed=True, data_path=a.groups, output_path=si.SEEDS_PATH,
                           config_snapshot={"rule": si.RULE_ID, "table_setting": si.TABLE_SETTING, "pilot_cells": si.PILOT_CELLS,
                                            "fallback_state": si.FALLBACK_STATE, "geography": lg.VERSION, "model_calls": 0})
    print(json.dumps(summary, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
