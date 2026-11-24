#!/usr/bin/env python3
"""P5a hotfix (D-069a, D-073a): seed packets v5a --- packets v5 with the majority scope rule and plain language v1b.

Builds packets v4b in memory and checks them against the tracked v4b packets byte for byte (as the v5 builder does);
builds v5 in memory and checks it against the tracked v5 packets byte for byte; then builds v5a
(`synthpackets_v5.build(variant="v5a")`): per group the scope class is the MAJORITY class among the cited members (ties ->
`mixed`, "In general, research"), the cited members of a place-specific class more specific than the group's class become
`scope_optional_clause` (", including work on <Place>"), and `model_view.plain_language` comes from plain_language_v1b
(`broader_hazard_phrase`). Checks that every group is byte-identical to v4b once the three scope fields are removed. Writes
`artifacts/benchmark/synth_packets_v5a/PK-<seed>.json` and `manifest.json`: per packet the scope per group (class, phrase,
optional clause, cited members by class), and `changes_from_v5`: every group whose class, phrase or clause differs from v5,
with the five v5 minority cases (`place_specific_class_from_minority_of_cited` of the v5 manifest) named. Deterministic; no
model call, no table value computed.

    python scripts/build_synth_packets_v5a.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import benchmark_items as bi  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import plain_language as pl  # noqa: E402
from climrr import synthpackets_v4 as v4  # noqa: E402
from climrr import synthpackets_v5 as v5  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def entry(pk: dict, path: Path) -> dict:
    strength = {g["group_id"]: g["strength_in_packet"] for g in pk["provenance"]["groups"]}
    groups = []
    for g in pk["model_view"]["groups"]:
        d = pk["scope_detail"][g["group_id"]]
        groups.append({"group_id": g["group_id"], "role": g["role"], "strength_in_packet": strength[g["group_id"]],
                       "scope_class": g["scope_class"], "scope_phrase": g["scope_phrase"],
                       "scope_optional_clause": g["scope_optional_clause"], "cited_members": d["cited_members"],
                       "cited_by_class": d["cited_by_class"], "regions": d["regions"],
                       "minority_places": d["minority_places"], "minority_cited_members": d["minority_cited_members"]})
    mv = pk["model_view"]
    return {"packet_id": pk["packet_id"], "item_id": pk["item_id"], "seed_id": pk["seed_id"], "level": pk["use_case_level"],
            "family": pk["family"], "place": mv["scope"]["place"], "classes_present": mv["scope"]["classes_present"],
            "needs_general_clause": mv["scope"]["needs_general_clause"], "general_clause": mv["scope"]["general_clause"],
            "broader_hazard_phrase": mv["plain_language"]["broader_hazard_phrase"],
            "question_form": mv["question_form"], "groups": groups, "sha256": sha256_file(path)}


def changes(v5_pk: dict, v5a_pk: dict, minority_v5: set) -> list[dict]:
    old = {g["group_id"]: g for g in v5_pk["model_view"]["groups"]}
    out = []
    for g in v5a_pk["model_view"]["groups"]:
        o = old[g["group_id"]]
        if (o["scope_class"], o["scope_phrase"]) != (g["scope_class"], g["scope_phrase"]) or g["scope_optional_clause"]:
            out.append({"item_id": v5a_pk["item_id"], "group_id": g["group_id"], "role": g["role"],
                        "cited_by_class": v5a_pk["scope_detail"][g["group_id"]]["cited_by_class"],
                        "v5": {"scope_class": o["scope_class"], "scope_phrase": o["scope_phrase"]},
                        "v5a": {"scope_class": g["scope_class"], "scope_phrase": g["scope_phrase"],
                                "scope_optional_clause": g["scope_optional_clause"]},
                        "v5_minority_case": (v5a_pk["item_id"], g["group_id"]) in minority_v5})
    return out


def main() -> int:
    b5 = v5.build("v5")
    for pk in b5["v4b"]:
        tracked = (v4.PACKETS_V4B_DIR / f"{pk['packet_id']}.json").read_text(encoding="utf-8")
        if tracked != v5.dumps(pk):
            raise SystemExit(f"{pk['packet_id']}: the v4b rebuild differs from the tracked packet")
    for pk in b5["v5"]:
        if (v5.PACKETS_V5_DIR / f"{pk['packet_id']}.json").read_text(encoding="utf-8") != v5.dumps(pk):
            raise SystemExit(f"{pk['packet_id']}: the v5 rebuild differs from the tracked packet")
    b = v5.build("v5a")
    v5_manifest_path = v5.PACKETS_V5_DIR / "manifest.json"
    man5 = json.loads(v5_manifest_path.read_text(encoding="utf-8"))
    minority_v5 = {(x["item_id"], x["group_id"]) for x in man5["place_specific_class_from_minority_of_cited"]}
    out = v5.PACKETS_V5A_DIR
    out.mkdir(parents=True, exist_ok=True)
    index, diff = [], []
    by_id5 = {pk["item_id"]: pk for pk in b5["v5"]}
    for pk in b["v5"]:
        path = out / f"{pk['packet_id']}.json"
        r2.write_json(path, pk)
        index.append(entry(pk, path))
        diff += changes(by_id5[pk["item_id"]], pk, minority_v5)
    five = [d for d in diff if d["v5_minority_case"]]
    if len(five) != len(minority_v5):
        raise SystemExit(f"{len(minority_v5)} v5 minority cases, {len(five)} found among the changes")
    skeletons = bi.opening_trigram_report([p["question_form"]["skeleton"] for p in index], b["forms"]["diversity"]["max_share"])
    plain = b["plain_v1b"]
    manifest = {"version": v5.VERSION_V5A, "decision": f"{v5.DECISION_V5A}, D-073a",
                "base": {"version": v5.VERSION, "manifest_sha256": sha256_file(v5_manifest_path),
                         "v4b_manifest_sha256": sha256_file(v4.PACKETS_V4B_DIR / "manifest.json"),
                         "v4b_and_v5_rebuilt_byte_identical": True, "groups_identical_to_v4b_beyond_scope_fields": True,
                         "scope_fields": list(v5.SCOPE_FIELDS_V5A)},
                "plain_language": {"file": repo_relative(pl.PLAIN_V1B_PATH), "version": plain["version"], "sha256": plain["sha256"],
                                   "broader_hazard_phrase": {f: x["broader_hazard_phrase"] for f, x in plain["families"].items()}},
                "question_forms": {"sha256": b["forms"]["sha256"], "assignment": b["assignment"], "as_v5": True},
                "scope_rule": {"class": "majority class among the group's cited members (plurality over the member classes); a tie for the most, or no cited member -> mixed",
                               "member_class": "as v5: litgeo v2 basis state > nca_region > us_subregion > us_national > global, else region_class other / unknown",
                               "stems": {"state": "Research on <State>", "nca": "Research on the <Region>",
                                         "us_subregion": "Research on the United States", "us_national": "Research on the United States",
                                         "global": "In general, research", "other": "In general, research", "unknown": "In general, research",
                                         "mixed": "In general, research"},
                               "optional_clause": ", including work on <State> / <the Region>: the cited members of a place-specific class (state, nca) more specific than the group's class; the phrase then reads <stem>, including work on <Place>, <verb>",
                               "verbs": {"multi_source_or_review": ["shows", "has shown"], "single_source": ["suggests"]},
                               "general_clause": "These are general drivers of <quantity_short>, not findings specific to <Place>."},
                "changes_from_v5": diff, "v5_minority_cases": five,
                "diversity": {"assigned_skeletons": skeletons},
                "packets": index}
    manifest_path = out / "manifest.json"
    r2.write_json(manifest_path, manifest)
    result = {"packets": [{k: p[k] for k in ("packet_id", "item_id", "needs_general_clause", "classes_present", "sha256")} for p in index],
              "groups_changed_from_v5": len(diff),
              "v5_minority_cases": [{"item_id": d["item_id"], "group_id": d["group_id"], "v5": d["v5"]["scope_phrase"],
                                     "v5a": d["v5a"]["scope_phrase"], "clause": d["v5a"]["scope_optional_clause"]} for d in five],
              "needs_general_clause_v5": {p["item_id"]: p["model_view"]["scope"]["needs_general_clause"] for p in b5["v5"]},
              "needs_general_clause_v5a": {p["item_id"]: p["needs_general_clause"] for p in index},
              "manifest_sha256": sha256_file(manifest_path)}
    rec = write_run_record(
        "build_synth_packets_v5a", result_summary=result, passed=True, data_path=v5_manifest_path, output_path=manifest_path,
        config_snapshot={"version": v5.VERSION_V5A, "decision": v5.DECISION_V5A, "base": v5.VERSION,
                         "plain_language": repo_relative(pl.PLAIN_V1B_PATH), "plain_language_sha256": plain["sha256"],
                         "question_forms_sha256": b["forms"]["sha256"], "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
