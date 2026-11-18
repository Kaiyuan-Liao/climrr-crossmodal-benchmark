#!/usr/bin/env python3
"""Work package P3b (D-066, D-067): seed packets v4b --- packets v4a with DR-DESC-1 v4 and the readability inputs.

As `scripts/build_synth_packets_v4a.py` (packets v4a, kept unchanged: synthesis run 4 read them): the same selection v2a,
plain language v1a, heat dispositions v1a and fire-arm dispositions v1, with: the descriptors of `descriptor_rules_v4.yaml`
(magnitude and tercile `forms`; "rising from rare to common" only for a baseline below 2 days and a future of at least 10
days, else "remaining rare"), `model_view.must_not_use` (the plain-language never_write words, the v4 tercile words, "RCP",
"SSP"), the pattern text's relative-magnitude sentence written as the comparison with other states, and `checks_input`
`group_role` (and `regions` for a regional contrast) for post-checks v3.1. Writes
`artifacts/benchmark/synth_packets_v4b/PK-<seed_id>.json` and `manifest.json` (per packet as v4a's manifest, plus the
descriptor record's magnitude class and forms, the tercile class and forms, the anchor pair and `must_not_use`). Rules:
`src/climrr/synthpackets_v4.py` (`variant="v4b"`). Deterministic; no model call, no table value computed.

    python scripts/build_synth_packets_v4b.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds_v3 as s3  # noqa: E402
from climrr import litgeo as lg  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import pattern_descriptors as pd  # noqa: E402
from climrr import pilot_selection as psel  # noqa: E402
from climrr import synthpackets as spk  # noqa: E402
from climrr import synthpackets_v4 as v4  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def manifest_entry(x: dict, pk: dict, path: Path, groups: dict, reslices: dict) -> dict:
    g = pk["provenance"]["groups"]
    roles = [y["role"] for y in g]
    fire = [y for y in g if y.get("review_state") == "reviewer_tagged"]
    exc = pk["excluded_groups"]
    undisposed = [{"group_id": e["group_id"], "arm": groups[e["group_id"]]["arm"],
                   "label": groups[e["group_id"]]["label"] or None, "statement_type": e["statement_type"],
                   "claim_about": e["claim_about"]} for e in exc if e["reason"] == "no_disposition"]
    by_disp = [{"group_id": e["group_id"], "disposition": groups[e["group_id"]]["disposition"], "reason": e["reason"]}
               for e in exc if groups[e["group_id"]]["arm"] in v4.REVIEWED_ARMS_V4A and groups[e["group_id"]]["disposition"]]
    return {
        "packet_id": pk["packet_id"], "item_id": pk["item_id"], "seed_id": x["seed_id"], "level": pk["use_case_level"],
        "family": pk["family"], "groups": len(g), **{f"groups_{r}": roles.count(r) for r in ("driver", "context", "caveat")},
        "groups_multi_source_or_review": sum(y["strength_in_packet"] != "single_source_supported" for y in g),
        "excluded_groups": len(exc), "excluded_no_disposition": len(undisposed),
        "fire_groups_unreviewed": pk["fire_groups_unreviewed"],
        "fire_groups_attached": [{"group_id": y["group_id"], "label": y["label"] or y["members"][0]["statement"],
                                  "kind": y["kind"], "statement_type": y["statement_type"], "claim_about": y["claim_about"],
                                  "claim_about_source": y["claim_about_source"], "disposition": y["disposition"],
                                  "role": y["role"], "strength_in_packet": y["strength_in_packet"], "n_papers": y["n_papers"],
                                  "review_state": y["review_state"]} for y in fire],
        "fire_candidates_excluded_by_disposition": by_disp,
        "undisposed_candidates": undisposed,
        "corrections_applied": sorted({m["statement_id"] for y in g for m in y["members"] if m["statement_id"] in reslices}),
        "label_overrides_applied": [y["group_id"] for y in g if y.get("label_override")],
        "working_assumptions_relied_on": [w["id"] for w in pk["working_assumptions_relied_on"]],
        "allowed_descriptors": pk["checks_input"]["allowed_descriptors"],
        "descriptors_v4": {k: pk["model_view"]["patterns"][0]["allowed_descriptors"].get(k)
                           for k in ("magnitude_class", "magnitude_forms", "anchor_pair", "tercile_class", "tercile_forms",
                                     "largest", "smallest", "magnitude_note")},
        "must_not_use": pk["model_view"]["must_not_use"],
        "group_roles": pk["checks_input"]["group_role"],
        "top3_labels": [y["label"] for y in pk["model_view"]["groups"][:3]], "sha256": sha256_file(path)}


def main() -> int:
    b = v4.build_selection(variant="v4b")
    sel, rules, plain, reslices = b["selection"], b["rules"], b["plain"], b["reslices"]
    groups = {g["group_id"]: g for g in b["groups"]}
    chosen = psel.selected(sel)
    out = v4.PACKETS_V4B_DIR
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for x, pk in zip(chosen, b["packets"]):
        path = out / f"{pk['packet_id']}.json"
        r2.write_json(path, pk)
        index.append(manifest_entry(x, pk, path, groups, reslices))
    undisposed = sorted({u["group_id"] for p in index for u in p["undisposed_candidates"]})
    undisposed_fire = sorted({u["group_id"] for p in index for u in p["undisposed_candidates"] if u["arm"] in v4.REVIEWED_ARMS_V4A})
    conflicts, hashes = b["conflicts"], b["hashes"]
    manifest_path = out / "manifest.json"
    r2.write_json(manifest_path, {"version": v4.VERSION_V4B, "rank_rule": v4.RANK_RULE, "descriptor_rule": rules["rule"],
                                  "descriptor_rules": {"file": repo_relative(pd.RULES_V4_PATH), "sha256": rules["sha256"]},
                                  "base": {"version": v4.VERSION_V4A, "manifest_sha256": sha256_file(v4.PACKETS_V4A_DIR / "manifest.json")},
                                  "plain_language": plain["version"], "geography": lg.VERSION, "unreviewed_arms": [],
                                  "reviewed_arms": list(v4.REVIEWED_ARMS_V4A),
                                  "selection": {"file": repo_relative(psel.SELECTION_V2A_PATH), "sha256": sha256_file(psel.SELECTION_V2A_PATH),
                                                "owner_confirmation": sel["owner_confirmation"],
                                                "excluded_from_v2": sel["excluded_from_v2"]},
                                  "group_dispositions_fire": {"file": repo_relative(v4.FIRE_DISPOSITIONS_PATH),
                                                              "sha256": sha256_file(v4.FIRE_DISPOSITIONS_PATH)},
                                  "undisposed_candidates": {"n": len(undisposed), "n_fire_arm": len(undisposed_fire),
                                                            "group_ids": undisposed},
                                  "threshold_conflicts": conflicts, "inputs_sha256": hashes, "packets": index})
    result = {"packets": [{k: p[k] for k in ("packet_id", "item_id", "level", "family", "groups", "groups_driver", "groups_context",
                                             "groups_multi_source_or_review", "excluded_no_disposition", "sha256")} for p in index],
              "descriptors_v4": {p["item_id"]: {k: p["descriptors_v4"][k] for k in ("magnitude_class", "anchor_pair", "tercile_class")}
                                 for p in index},
              "fire_groups_attached": {p["packet_id"]: [{k: y[k] for k in ("group_id", "label", "role", "strength_in_packet", "disposition")}
                                                        for y in p["fire_groups_attached"]] for p in index if p["family"] == "fire_weather_index"},
              "undisposed_candidates": {p["packet_id"]: [u["group_id"] for u in p["undisposed_candidates"]] for p in index
                                        if p["undisposed_candidates"]},
              "n_undisposed_candidates": len(undisposed), "n_undisposed_fire": len(undisposed_fire),
              "threshold_conflicts": conflicts, "manifest_sha256": sha256_file(manifest_path)}
    rec = write_run_record(
        "build_synth_packets_v4b", result_summary=result, passed=True, data_path=s3.SEEDS_PATH, output_path=manifest_path,
        config_snapshot={"version": v4.VERSION_V4B, "rank_rule": v4.RANK_RULE, "descriptor_rule": rules["rule"],
                         "descriptor_rules_sha256": rules["sha256"], "plain_language": plain["version"],
                         "geography": lg.VERSION, "unreviewed_arms": [], "reviewed_arms": list(v4.REVIEWED_ARMS_V4A),
                         "select": [x["seed_id"] for x in chosen], "selection": repo_relative(psel.SELECTION_V2A_PATH),
                         "group_dispositions_fire": repo_relative(v4.FIRE_DISPOSITIONS_PATH), "max_passage": spk.MAX_PASSAGE,
                         "max_groups": {"driver": spk.MAX_DRIVER_GROUPS, "context": spk.MAX_CONTEXT_GROUPS, "caveat": spk.MAX_CAVEAT_GROUPS},
                         "inputs_sha256": hashes, "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
