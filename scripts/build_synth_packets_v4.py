#!/usr/bin/env python3
"""Work package P3a, section D: seed packets v4 --- the eight-item sample set for the mentor (D-059 -- D-065; no model call).

Reads the pilot selection v2 (`data/metadata/benchmark/pilot_selection_v2.yaml`, manifest-pinned; checked against the
shortlists and the seeds it names), `artifacts/benchmark/item_seeds_v3.jsonl` (gitignored; checked against its pin), the
grouping run's groups (`artifacts/litgroups/run2/groups_enriched.jsonl`), the group dispositions v1a (heat arm), the
provenance corrections v1a (overlay: corrected statement and passage, reviewer label), the plain-language phrases and
DR-DESC-1 v3 (both manifest-pinned), the working assumptions in `data/metadata/resolutions.yaml` (D-064), the statements,
clusters and independence map. Builds exactly the selected seeds, in order and at their rungs, into
`artifacts/benchmark/synth_packets_v4/PK-<seed_id>.json` (item ids BI-P3-<nnnn>) with `manifest.json`: per packet its
SHA-256, group counts, `fire_groups_unreviewed`, the attached fire-arm groups (id, label, claim tag, strength) for the
COORDINATOR's review, the working assumptions relied on, and the selection's threshold conflicts (D-060, reported).
Rules: `src/climrr/synthpackets_v4.py`. Deterministic; no model call, no table value computed.

    python scripts/build_synth_packets_v4.py
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
from climrr import pilot_selection as psel  # noqa: E402
from climrr import synthpackets as spk  # noqa: E402
from climrr import synthpackets_v4 as v4  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    b = v4.build_selection()
    sel, rules, plain, reslices = b["selection"], b["rules"], b["plain"], b["reslices"]
    chosen = psel.selected(sel)
    out = v4.PACKETS_DIR
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for x, pk in zip(chosen, b["packets"]):
        path = out / f"{pk['packet_id']}.json"
        r2.write_json(path, pk)
        g = pk["provenance"]["groups"]
        roles = [y["role"] for y in g]
        index.append({
            "packet_id": pk["packet_id"], "item_id": pk["item_id"], "seed_id": x["seed_id"], "level": pk["use_case_level"],
            "family": pk["family"], "groups": len(g), **{f"groups_{r}": roles.count(r) for r in ("driver", "context", "caveat")},
            "groups_multi_source_or_review": sum(y["strength_in_packet"] != "single_source_supported" for y in g),
            "excluded_groups": len(pk["excluded_groups"]),
            "excluded_no_disposition": sum(e["reason"] == "no_disposition" for e in pk["excluded_groups"]),
            "fire_groups_unreviewed": pk["fire_groups_unreviewed"],
            "fire_groups_attached": [{"group_id": y["group_id"], "label": y["label"] or y["members"][0]["statement"],
                                      "kind": y["kind"], "statement_type": y["statement_type"], "claim_about": y["claim_about"],
                                      "role": y["role"], "strength_in_packet": y["strength_in_packet"], "n_papers": y["n_papers"]}
                                     for y in g if y.get("review_state") == "unreviewed_agent_tag"],
            "corrections_applied": sorted({m["statement_id"] for y in g for m in y["members"] if m["statement_id"] in reslices}),
            "label_overrides_applied": [y["group_id"] for y in g if y.get("label_override")],
            "working_assumptions_relied_on": [w["id"] for w in pk["working_assumptions_relied_on"]],
            "allowed_descriptors": pk["checks_input"]["allowed_descriptors"],
            "top3_labels": [y["label"] for y in pk["model_view"]["groups"][:3]], "sha256": sha256_file(path)})
    conflicts, hashes = b["conflicts"], b["hashes"]
    manifest_path = out / "manifest.json"
    r2.write_json(manifest_path, {"version": v4.VERSION, "rank_rule": v4.RANK_RULE, "descriptor_rule": rules["rule"],
                                  "plain_language": plain["version"], "geography": lg.VERSION, "unreviewed_arms": list(v4.UNREVIEWED_ARMS),
                                  "selection": {"file": repo_relative(psel.SELECTION_V2_PATH), "sha256": sha256_file(psel.SELECTION_V2_PATH),
                                                "owner_confirmation": sel["owner_confirmation"]},
                                  "threshold_conflicts": conflicts, "inputs_sha256": hashes, "packets": index})
    result = {"packets": [{k: p[k] for k in ("packet_id", "item_id", "level", "family", "groups", "groups_multi_source_or_review",
                                             "fire_groups_unreviewed", "working_assumptions_relied_on", "sha256")} for p in index],
              "fire_groups_attached": {p["packet_id"]: p["fire_groups_attached"] for p in index if p["fire_groups_attached"]},
              "threshold_conflicts": conflicts, "manifest_sha256": sha256_file(manifest_path)}
    rec = write_run_record(
        "build_synth_packets_v4", result_summary=result, passed=True, data_path=s3.SEEDS_PATH, output_path=manifest_path,
        config_snapshot={"version": v4.VERSION, "rank_rule": v4.RANK_RULE, "descriptor_rule": rules["rule"], "plain_language": plain["version"],
                         "geography": lg.VERSION, "unreviewed_arms": list(v4.UNREVIEWED_ARMS), "select": [x["seed_id"] for x in chosen],
                         "selection": repo_relative(psel.SELECTION_V2_PATH), "max_passage": spk.MAX_PASSAGE,
                         "max_groups": {"driver": spk.MAX_DRIVER_GROUPS, "context": spk.MAX_CONTEXT_GROUPS, "caveat": spk.MAX_CAVEAT_GROUPS},
                         "inputs_sha256": hashes, "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
