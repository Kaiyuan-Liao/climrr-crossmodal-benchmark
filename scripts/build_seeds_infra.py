#!/usr/bin/env python3
"""Work package P5b, part C (implemented; runs in P5c): rung-8 seeds (DR-SEED-INFRA-1) and the rung-8 pilot selection (D-075).

Runs after the infra grouping run (`litgroups/infra_run1`) is ingested. Reads the v3 seeds (pinned), the ingested infra
statements and their independence, and the infra groups (`--groups`: the grouping run's `groups.jsonl`); writes
`artifacts/benchmark/item_seeds_infra_v1.jsonl` (+ summary) and `artifacts/benchmark/pilot_selection_infra_v1.yaml` (P5c:
item ids, `place_named_impact_evidence`, `review_state: impact_groups_unreviewed`). Rules: `src/climrr/seeds_infra.py`.
Deterministic; no model call, no table value computed.

    python scripts/build_seeds_infra.py --groups artifacts/litgroups/infra_run1/groups.jsonl

P5c hotfix (D-078; v1a): with `--dispositions data/metadata/benchmark/group_dispositions_infra_v1.csv` the COORDINATOR's
dispositions are applied first (`climrr.dispositions_infra`; the file's SHA-256 is checked), the dispositioned records and
the log of counts written to `artifacts/litgroups/infra_run1/groups_dispositioned_v1.jsonl` and `dispositions_v1_applied.json`,
and the seeds / selection written as v1a (`item_seeds_infra_v1a.jsonl` + summary, `pilot_selection_infra_v1a.yaml`;
`review_state: impact_groups_reviewed`; candidate states read through the dispositions). v1 is untouched.

    python scripts/build_seeds_infra.py --groups artifacts/litgroups/infra_run1/groups.jsonl \
        --dispositions data/metadata/benchmark/group_dispositions_infra_v1.csv
"""

from __future__ import annotations

import argparse
import json
import sys

import yaml
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import dispositions_infra as di  # noqa: E402
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
    ap.add_argument("--dispositions", type=Path, default=None, help="P5c hotfix: the COORDINATOR's dispositions CSV (v1a outputs)")
    a = ap.parse_args()
    pin = json.loads(s3.SUMMARY_PATH.read_text(encoding="utf-8"))["seeds_file"]["sha256"]
    if not s3.SEEDS_PATH.is_file() or sha256_file(s3.SEEDS_PATH) != pin:
        raise SystemExit(f"{repo_relative(s3.SEEDS_PATH)} is absent or differs from its pin {pin}; run scripts/build_item_seeds_v3.py")
    seeds_v3 = sd.read_jsonl(s3.SEEDS_PATH)
    records = sd.read_jsonl(ir.INGESTED_PATH)
    indep = json.loads(ir.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    groups = sd.read_jsonl(a.groups)
    ctx = si.Context(records, indep, lg.Gazetteer(sd.nca_map()))
    reviewed = a.dispositions is not None
    seeds_path, summary_path, sel_path = ((si.SEEDS_V1A_PATH, si.SEEDS_V1A_SUMMARY_PATH, si.SELECTION_V1A_PATH) if reviewed
                                          else (si.SEEDS_PATH, si.SEEDS_SUMMARY_PATH, si.SELECTION_PATH))
    log, views = None, None
    if reviewed:
        groups, log = di.apply(groups, di.load(a.dispositions))
        ir.write_jsonl(si.GROUPS_DISPOSITIONED_PATH, groups)
        views = si.impact_views(groups, ctx)
        log["usable_impact_views"] = len(views)
        log["usable_impact_views_by_family_class"] = dict(sorted(Counter(f"{v['family']}|{c}" for v in views for c in v["asset_classes"]).items()))
        log["groups_dispositioned"] = {"path": repo_relative(si.GROUPS_DISPOSITIONED_PATH), "sha256": sha256_file(si.GROUPS_DISPOSITIONED_PATH)}
        ir.write_json(si.DISPOSITIONS_LOG_PATH, log)
    seeds = si.build_seeds(seeds_v3, groups, ctx, si.rung3_driver_ids_factory(), reviewed=reviewed)
    ir.write_jsonl(seeds_path, seeds)
    forms = si.load_question_forms_v2()
    sel = si.select_pilot(seeds, seeds_v3, records, ctx, forms, views=views)
    sel_path.write_text(yaml.safe_dump(sel, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    summary = {"version": si.VERSION_V1A if reviewed else si.VERSION, "rule": si.RULE_ID, "decision": si.DECISION, "seeds": len(seeds),
               "by_family_class": dict(sorted(Counter(f"{s['family']}|{s['asset_class']}" for s in seeds).items())),
               "by_best_relevance": dict(sorted(Counter(s["best_relevance"] for s in seeds).items())),
               "seeds_file": {"path": repo_relative(seeds_path), "sha256": sha256_file(seeds_path)},
               "selection_file": {"path": repo_relative(sel_path), "sha256": sha256_file(sel_path)},
               "review_state": si.REVIEW_STATE_REVIEWED if reviewed else si.REVIEW_STATE_UNREVIEWED,
               "selected": [{k: x[k] for k in ("order", "item_id", "family", "asset_class", "state", "state_basis", "candidate_states",
                                               "table_change", "place_named_impact_evidence", "seed_id", "question_form_id",
                                               "needs_general_clause")} for x in sel["selected"]],
               "missing": sel["missing"],
               "inputs": {"item_seeds_v3": pin, "statements_ingested": sha256_file(ir.INGESTED_PATH),
                          "independence_v2": sha256_file(ir.INDEPENDENCE_PATH), "groups": sha256_file(a.groups),
                          "question_forms_v2": forms["sha256"]}}
    if reviewed:
        summary["decision_dispositions"] = di.DECISION
        summary["inputs"]["dispositions"] = sha256_file(a.dispositions)
        summary["inputs"]["groups_dispositioned"] = sha256_file(si.GROUPS_DISPOSITIONED_PATH)
        summary["dispositions_log"] = {"path": repo_relative(si.DISPOSITIONS_LOG_PATH), "sha256": sha256_file(si.DISPOSITIONS_LOG_PATH)}
    ir.write_json(summary_path, summary)
    rec = write_run_record("build_seeds_infra", result_summary=summary, passed=True, data_path=a.dispositions or a.groups, output_path=seeds_path,
                           config_snapshot={"rule": si.RULE_ID, "table_setting": si.TABLE_SETTING, "pilot_cells": si.PILOT_CELLS,
                                            "fallback_state": si.FALLBACK_STATE, "geography": lg.VERSION, "model_calls": 0,
                                            "dispositions": repo_relative(a.dispositions) if reviewed else None})
    print(json.dumps(summary, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
