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

P5c hotfix (D-077, D-078, D-073c): `--variant v1a` reads the v1a seeds and selection (dispositions applied; checked against
`item_seeds_infra_v1a_summary.json`) and writes `artifacts/benchmark/synth_packets_infra_v1a/` (`review_state:
impact_groups_reviewed`, two-hop fields, schema-v2a item fields per impact group).

    python scripts/build_synth_packets_infra.py --variant v1a

Work package litsynth v5.4 (D-075a): `--variant v1b` reads the v1a packets (each checked against
`synth_packets_infra_v1a/manifest.json`) and the pinned asset short forms (`data/metadata/benchmark/asset_short_forms_v1.yaml`)
and writes `artifacts/benchmark/synth_packets_infra_v1b/` (`answer_shape: rung8_v2`, `asset_class_short_forms`, the shape-v2
rung instruction; nothing else of the packet changes).

    python scripts/build_synth_packets_infra.py --variant v1b
"""

from __future__ import annotations

import argparse
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
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--variant", choices=("v1", "v1a", "v1b"), default="v1")
    variant = ap.parse_args().variant
    if variant == "v1b":
        return build_v1b()
    v1a = variant == "v1a"
    seeds_path, summary_path, sel_path = ((si.SEEDS_V1A_PATH, si.SEEDS_V1A_SUMMARY_PATH, si.SELECTION_V1A_PATH) if v1a
                                          else (si.SEEDS_PATH, si.SEEDS_SUMMARY_PATH, si.SELECTION_PATH))
    summ = json.loads(summary_path.read_text(encoding="utf-8"))
    for key, path in (("seeds_file", seeds_path), ("selection_file", sel_path)):
        if sha256_file(path) != summ[key]["sha256"]:
            raise SystemExit(f"{repo_relative(path)} differs from its pin in {repo_relative(summary_path)}; run build_seeds_infra.py")
    man = json.loads(gi.MANIFEST_PATH.read_text(encoding="utf-8"))
    pinned = {d["path"]: d["sha256"] for d in man["derived_files"]}
    if sha256_file(gi.ENRICHED_PATH) != pinned["groups_enriched.jsonl"]:
        raise SystemExit("groups_enriched.jsonl differs from the ingest manifest; run scripts/ingest_litgroups_infra1.py")
    sel = yaml.safe_load(sel_path.read_text(encoding="utf-8"))
    seeds = sd.read_jsonl(seeds_path)
    enriched = sd.read_jsonl(gi.ENRICHED_PATH)
    records = sd.read_jsonl(ir.INGESTED_PATH)
    indep = json.loads(ir.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    tag = "v1a" if v1a else "v1"
    extra = {f"item_seeds_infra_{tag}": sha256_file(seeds_path), f"pilot_selection_infra_{tag}": sha256_file(sel_path),
             "groups_infra_run1": sha256_file(gi.ART / "groups.jsonl"), "groups_enriched_infra_run1": sha256_file(gi.ENRICHED_PATH),
             "statements_infra_run1": sha256_file(ir.INGESTED_PATH), "independence_infra_run1": sha256_file(ir.INDEPENDENCE_PATH)}
    if v1a:
        from climrr import benchmark_items as bi
        from climrr import dispositions_infra as di

        extra.update({"group_dispositions_infra_v1": sha256_file(di.PATH), "groups_dispositioned_v1": sha256_file(si.GROUPS_DISPOSITIONED_PATH),
                      "item_schema_v2a": bi.schema_sha256(bi.SCHEMA_V2A_PATH)})
    packets = spi.build(sel, seeds, enriched, records, indep, extra, variant)

    out = spi.PACKETS_V1A_DIR if v1a else spi.PACKETS_DIR
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for pk in packets:
        path = out / f"{pk['packet_id']}.json"
        r2.write_json(path, pk)
        index.append(spi.report_entry(pk, path))
    if v1a:
        head = {"version": spi.VERSION_V1A, "decision": spi.DECISION_V1A, "rules": spi.RULES_V1A, "review_state": spi.REVIEW_STATE_V1A,
                "provisional": False, "item_schema": "benchmark_item_v2a", "bridge_clause": spi.BRIDGE_CLAUSE,
                "two_hop_phrases": list(spi.TWO_HOP_PHRASES), "two_hop_rule": spi.TWO_HOP_RULE, "two_hop_rule_fire": spi.TWO_HOP_RULE_FIRE}
    else:
        head = {"version": spi.VERSION, "decision": spi.DECISION, "rules": spi.RULES, "review_state": spi.REVIEW_STATE,
                "provisional": True,
                "provisional_note": "built before the COORDINATOR's dispositions of the impact groups; rebuilt by the P5c-hotfix"}
    manifest = {**head,
                "selection": {"path": repo_relative(sel_path), "sha256": extra[f"pilot_selection_infra_{tag}"],
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
    rec = write_run_record("build_synth_packets_infra", result_summary=result, passed=True, data_path=sel_path,
                           output_path=manifest_path,
                           config_snapshot={"version": head["version"], "decision": head["decision"], "variant": variant,
                                            "max_impact_groups": spi.MAX_IMPACT_GROUPS,
                                            "asset_class_phrase": spi.ASSET_CLASS_PHRASE, "model_calls": 0})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


def build_v1b() -> int:
    """Packets v1b from the pinned v1a packets (module docstring)."""
    man_a = json.loads((spi.PACKETS_V1A_DIR / "manifest.json").read_text(encoding="utf-8"))
    short = spi.load_short_forms()
    out = spi.PACKETS_V1B_DIR
    out.mkdir(parents=True, exist_ok=True)
    index, sources = [], {}
    for e in man_a["packets"]:
        src = spi.PACKETS_V1A_DIR / f"{e['packet_id']}.json"
        if sha256_file(src) != e["sha256"]:
            raise SystemExit(f"{repo_relative(src)} differs from the v1a manifest; run build_synth_packets_infra.py --variant v1a")
        pk = spi.to_v1b(json.loads(src.read_text(encoding="utf-8")), short, e["sha256"])
        path = out / f"{pk['packet_id']}.json"
        r2.write_json(path, pk)
        index.append(spi.report_entry(pk, path))
        sources[e["packet_id"]] = e["sha256"]
    manifest = {**{k: man_a[k] for k in man_a if k not in ("packets", "version", "decision", "rules", "rung_instruction")},
                "version": spi.VERSION_V1B, "decision": spi.DECISION_V1B, "rules": spi.RULES_V1B, "answer_shape": spi.ANSWER_SHAPE,
                "built_from": {"manifest": repo_relative(spi.PACKETS_V1A_DIR / "manifest.json"),
                               "manifest_sha256": sha256_file(spi.PACKETS_V1A_DIR / "manifest.json"), "packets_sha256": sources},
                "asset_short_forms": {"path": repo_relative(spi.SHORT_FORMS_PATH), "sha256": short["sha256"],
                                      "classes": {k: v["short"] for k, v in short["classes"].items()}},
                "rung_instruction": spi.RUNG8_INSTRUCTION_V2, "packets": index}
    manifest_path = out / "manifest.json"
    r2.write_json(manifest_path, manifest)
    result = {"packets": [{k: p[k] for k in ("item_id", "packet_id", "family", "asset_class", "state", "answer_shape",
                                             "asset_class_short_forms", "bridge_clause_required", "sha256")} for p in index],
              "built_from_manifest_sha256": manifest["built_from"]["manifest_sha256"], "asset_short_forms_sha256": short["sha256"],
              "manifest_sha256": sha256_file(manifest_path)}
    rec = write_run_record("build_synth_packets_infra", result_summary=result, passed=True,
                           data_path=spi.PACKETS_V1A_DIR / "manifest.json", output_path=manifest_path,
                           config_snapshot={"version": spi.VERSION_V1B, "decision": spi.DECISION_V1B, "variant": "v1b",
                                            "answer_shape": spi.ANSWER_SHAPE, "model_calls": 0})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
