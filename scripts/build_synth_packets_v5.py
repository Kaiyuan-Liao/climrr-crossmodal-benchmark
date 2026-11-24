#!/usr/bin/env python3
"""Work package P5a (D-069): seed packets v5 --- packets v4b plus the scope fields and the assigned question form.

Builds packets v4b in memory (`synthpackets_v4.build_selection(variant="v4b")`, the seven sample seeds), checks that each
equals the tracked v4b packet byte for byte, adds per group `scope_class` / `scope_phrase`, per item `model_view.scope`
(`needs_general_clause`, `general_clause`) and `question_form` (`question_forms_v1.yaml`, round-robin within rung), and
`checks_input.scope` / `question_form` for post-checks v3.2 (`src/climrr/synthpackets_v5.py`). Checks that every group is
byte-identical to v4b once the two scope fields are removed. Writes `artifacts/benchmark/synth_packets_v5/PK-<seed>.json`
and `manifest.json` with, per packet, the scope per group (class, stem, cited members by class, and whether the class
rests on a minority of the cited members), the question form and its skeleton; and two diversity reports (opening
trigram, at most 30 %): on the assigned skeletons, and on the run-5 synthesis prompts as a baseline. Deterministic; no
model call, no table value computed.

    python scripts/build_synth_packets_v5.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import benchmark_items as bi  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import litsynth_run2 as ls2  # noqa: E402
from climrr import litsynth_run5 as s5  # noqa: E402
from climrr import synthpackets_v4 as v4  # noqa: E402
from climrr import synthpackets_v5 as v5  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def manifest_entry(pk: dict, path: Path) -> dict:
    strength = {g["group_id"]: g["strength_in_packet"] for g in pk["provenance"]["groups"]}
    groups = []
    for g in pk["model_view"]["groups"]:
        d = pk["scope_detail"][g["group_id"]]
        n_best = d["cited_by_class"].get(d["class"], 0)
        groups.append({"group_id": g["group_id"], "role": g["role"], "strength_in_packet": strength[g["group_id"]],
                       "scope_class": g["scope_class"], "scope_phrase": g["scope_phrase"], "cited_members": d["cited_members"],
                       "cited_by_class": d["cited_by_class"], "regions": d["regions"],
                       "class_from_minority_of_cited": d["cited_members"] > 0 and 2 * n_best < d["cited_members"]})
    mv = pk["model_view"]
    return {"packet_id": pk["packet_id"], "item_id": pk["item_id"], "seed_id": pk["seed_id"], "level": pk["use_case_level"],
            "family": pk["family"], "place": mv["scope"]["place"], "classes_present": mv["scope"]["classes_present"],
            "needs_general_clause": mv["scope"]["needs_general_clause"], "general_clause": mv["scope"]["general_clause"],
            "question_form": mv["question_form"], "groups": groups, "sha256": sha256_file(path)}


def main() -> int:
    b = v5.build()
    for pk in b["v4b"]:                                            # the in-memory v4b build equals the tracked packets
        tracked = (v4.PACKETS_V4B_DIR / f"{pk['packet_id']}.json").read_text(encoding="utf-8")
        if tracked != json.dumps(pk, indent=2, ensure_ascii=False) + "\n":
            raise SystemExit(f"{pk['packet_id']}: the v4b rebuild differs from the tracked packet")
    out = v5.PACKETS_V5_DIR
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for pk in b["v5"]:
        path = out / f"{pk['packet_id']}.json"
        r2.write_json(path, pk)
        index.append(manifest_entry(pk, path))
    skeletons = bi.opening_trigram_report([p["question_form"]["skeleton"] for p in index], b["forms"]["diversity"]["max_share"])
    run5 = [it["prompt"] for it in ls2.read_items(s5.ART / "items.jsonl")]
    baseline = bi.opening_trigram_report(run5, b["forms"]["diversity"]["max_share"])
    minority = [{"item_id": p["item_id"], "group_id": g["group_id"], "scope_class": g["scope_class"], "cited_by_class": g["cited_by_class"]}
                for p in index for g in p["groups"] if g["class_from_minority_of_cited"] and g["scope_class"] in ("state", "nca")]
    v4b_manifest = v4.PACKETS_V4B_DIR / "manifest.json"
    manifest = {"version": v5.VERSION, "decision": v5.DECISION,
                "base": {"version": v4.VERSION_V4B, "manifest_sha256": sha256_file(v4b_manifest),
                         "packets_rebuilt_byte_identical": True,
                         "groups_identical_beyond_scope_fields": True, "scope_fields": list(v5.SCOPE_FIELDS)},
                "question_forms": {"file": repo_relative(v5.QUESTION_FORMS_PATH), "sha256": b["forms"]["sha256"],
                                   "assignment": b["assignment"], "rule": "round-robin in selection order within rung, over the forms admitting the item (id order)"},
                "scope_rule": {"class": "most specific class among the group's cited members (core / cited candidates, review_synthesis passages): member basis state > nca_region > us_subregion > us_national > global, else region_class other / unknown",
                               "stems": {"state": "Research on <State>", "nca": "Research on the <Region>",
                                         "us_subregion": "Research on the United States", "us_national": "Research on the United States",
                                         "global": "In general, research", "other": "In general, research", "unknown": "In general, research"},
                               "verbs": {"multi_source_or_review": ["shows", "has shown"], "single_source": ["suggests"]},
                               "general_clause": "These are general drivers of <quantity_short>, not findings specific to <Place>."},
                "place_specific_class_from_minority_of_cited": minority,
                "diversity": {"assigned_skeletons": skeletons, "baseline_run5_prompts": baseline},
                "packets": index}
    manifest_path = out / "manifest.json"
    r2.write_json(manifest_path, manifest)
    result = {"packets": [{k: p[k] for k in ("packet_id", "item_id", "needs_general_clause", "sha256")} | {"question_form": p["question_form"]["id"]}
                          for p in index],
              "classes_by_item": {p["item_id"]: p["classes_present"] for p in index},
              "place_specific_class_from_minority_of_cited": len(minority),
              "diversity_skeletons": {k: skeletons[k] for k in ("pass", "largest_share")},
              "diversity_baseline_run5": {k: baseline[k] for k in ("pass", "largest_share")},
              "manifest_sha256": sha256_file(manifest_path)}
    rec = write_run_record(
        "build_synth_packets_v5", result_summary=result, passed=True, data_path=v4b_manifest, output_path=manifest_path,
        config_snapshot={"version": v5.VERSION, "decision": v5.DECISION, "base": v4.VERSION_V4B,
                         "question_forms": repo_relative(v5.QUESTION_FORMS_PATH), "question_forms_sha256": b["forms"]["sha256"],
                         "max_share": b["forms"]["diversity"]["max_share"], "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
