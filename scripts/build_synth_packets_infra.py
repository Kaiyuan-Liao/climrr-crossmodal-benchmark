#!/usr/bin/env python3
"""Work package P5c, part C: the rung-8 seed packets v1 for Alvi's samples (`synth_packets_infra_v1/`; D-075 rules, D-076).

Reads the selection (`artifacts/benchmark/pilot_selection_infra_v1.yaml`) and the seeds (`item_seeds_infra_v1.jsonl`), each
checked against the hash in `item_seeds_infra_v1_summary.json`; the enriched infra groups
(`artifacts/litgroups/infra_run1/groups_enriched.jsonl`, checked against the ingest manifest), the ingested infra statements
and their independence. Builds one packet per selected cell (`climrr.synthpackets_infra`): the rung-3 v4b base of the
seed's pattern (driver groups only), the impact groups (capped at 10), scope per group (D-069a), plain language v1b, the
assigned question form, `must_not_use`, `checks_input.rung8`, `review_state: impact_groups_unreviewed`. Writes
`artifacts/benchmark/synth_packets_infra_v1/PK-<seed>.json` and `manifest.json` (per packet: pattern summary, impact groups
attached with label, strength and place class, driver groups, excluded groups). **Provisional** until the COORDINATOR's
dispositions of the impact groups are applied (P5c-hotfix). Deterministic; no model call, no table value computed.

    python scripts/build_synth_packets_infra.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import litgroups_infra_run1 as gi  # noqa: E402
from climrr import litstatements_infra1 as ir  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import seeds_infra as si  # noqa: E402
from climrr import synthpackets_infra as spi  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    summ = json.loads(si.SEEDS_SUMMARY_PATH.read_text(encoding="utf-8"))
    for key, path in (("seeds_file", si.SEEDS_PATH), ("selection_file", si.SELECTION_PATH)):
        if sha256_file(path) != summ[key]["sha256"]:
            raise SystemExit(f"{repo_relative(path)} differs from its pin in {repo_relative(si.SEEDS_SUMMARY_PATH)}; run build_seeds_infra.py")
    man = json.loads(gi.MANIFEST_PATH.read_text(encoding="utf-8"))
    pinned = {d["path"]: d["sha256"] for d in man["derived_files"]}
    if sha256_file(gi.ENRICHED_PATH) != pinned["groups_enriched.jsonl"]:
        raise SystemExit("groups_enriched.jsonl differs from the ingest manifest; run scripts/ingest_litgroups_infra1.py")
    sel = yaml.safe_load(si.SELECTION_PATH.read_text(encoding="utf-8"))
    seeds = sd.read_jsonl(si.SEEDS_PATH)
    enriched = sd.read_jsonl(gi.ENRICHED_PATH)
    records = sd.read_jsonl(ir.INGESTED_PATH)
    indep = json.loads(ir.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    extra = {"item_seeds_infra_v1": sha256_file(si.SEEDS_PATH), "pilot_selection_infra_v1": sha256_file(si.SELECTION_PATH),
             "groups_infra_run1": sha256_file(gi.ART / "groups.jsonl"), "groups_enriched_infra_run1": sha256_file(gi.ENRICHED_PATH),
             "statements_infra_run1": sha256_file(ir.INGESTED_PATH), "independence_infra_run1": sha256_file(ir.INDEPENDENCE_PATH)}
    packets = spi.build(sel, seeds, enriched, records, indep, extra)

    out = spi.PACKETS_DIR
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for pk in packets:
        path = out / f"{pk['packet_id']}.json"
        r2.write_json(path, pk)
        index.append(spi.report_entry(pk, path))
    manifest = {"version": spi.VERSION, "decision": spi.DECISION, "rules": spi.RULES, "review_state": spi.REVIEW_STATE,
                "provisional": True,
                "provisional_note": "built before the COORDINATOR's dispositions of the impact groups; rebuilt by the P5c-hotfix",
                "selection": {"path": repo_relative(si.SELECTION_PATH), "sha256": extra["pilot_selection_infra_v1"],
                              "selected": len(sel["selected"]), "missing": sel["missing"]},
                "inputs_sha256": extra, "max_impact_groups": spi.MAX_IMPACT_GROUPS,
                "asset_class_phrase": spi.ASSET_CLASS_PHRASE, "rung8_must_not_use": list(spi.RUNG8_MUST_NOT_USE),
                "fire_words": list(spi.FIRE_WORDS), "wildfire_rule": spi.WILDFIRE_RULE, "rung_instruction": spi.RUNG8_INSTRUCTION,
                "packets": index}
    manifest_path = out / "manifest.json"
    r2.write_json(manifest_path, manifest)
    result = {"packets": [{k: p[k] for k in ("item_id", "packet_id", "family", "asset_class", "state", "question_form",
                                             "needs_general_clause", "place_named_impact_evidence", "excluded_groups", "sha256")}
                          | {"impact_groups": len(p["impact_groups"]), "driver_groups": len(p["driver_groups"])} for p in index],
              "missing_cells": [{k: m[k] for k in ("item_id", "family", "asset_class", "state", "reason")} for m in sel["missing"]],
              "manifest_sha256": sha256_file(manifest_path)}
    rec = write_run_record("build_synth_packets_infra", result_summary=result, passed=True, data_path=si.SELECTION_PATH,
                           output_path=manifest_path,
                           config_snapshot={"version": spi.VERSION, "decision": spi.DECISION, "max_impact_groups": spi.MAX_IMPACT_GROUPS,
                                            "asset_class_phrase": spi.ASSET_CLASS_PHRASE, "model_calls": 0})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
