#!/usr/bin/env python3
"""Pilot P2b: seed packets for the item-synthesis agent, from the pilot selection and the grouping run.

Reads the pilot selection (`data/metadata/benchmark/pilot_selection_v1.yaml`, D-050; checked against its
manifest pin and against the shortlist it was chosen from), `artifacts/benchmark/item_seeds_v2.jsonl`
(gitignored; checked against its pin; the pattern records), the grouping run's `groups.jsonl` (agent v2,
with `claim_about`), `statements_ingested.jsonl`, `clusters_v1b.jsonl` and `independence_v2.json`. Builds
**exactly the selected seeds**, in the selection's order and at its rungs: `<out>/PK-<seed_id>.json` with
item id `BI-P2B-<nnnn>`, and an `index.json`. Relevance under the D-047a geography (`litgeo` v2); groups by
DR-SEED-RANK-2. Rules: `src/climrr/synthpackets.py`. Deterministic; no model call, no table value computed.

    python scripts/build_synth_packets.py --groups <litgroups run1>/groups.jsonl \\
        [--selection data/metadata/benchmark/pilot_selection_v1.yaml] [--out artifacts/benchmark/synth_packets]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import itemseeds_v2 as s2  # noqa: E402
from climrr import litgeo as lg  # noqa: E402
from climrr import litgroups as lgr  # noqa: E402
from climrr import litindependence as li  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import pilot_selection as psel  # noqa: E402
from climrr import synthpackets as spk  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--groups", required=True, type=Path)
    ap.add_argument("--selection", type=Path, default=psel.SELECTION_PATH, help="pilot selection YAML (manifest-pinned)")
    ap.add_argument("--out", type=Path, default=spk.PACKETS_DIR)
    a = ap.parse_args()
    sel = psel.load(a.selection)
    errs = psel.check(sel)
    if errs:
        raise SystemExit("pilot selection fails its checks: " + "; ".join(errs))
    pin = json.loads(s2.SUMMARY_PATH.read_text(encoding="utf-8"))["seeds_file"]["sha256"]
    if sha256_file(s2.SEEDS_PATH) != pin:
        raise SystemExit(f"{repo_relative(s2.SEEDS_PATH)} differs from its pin {pin}; run scripts/build_item_seeds_v2.py")
    chosen = psel.selected(sel)
    select = [x["seed_id"] for x in chosen]
    seeds = {s["seed_id"]: s for s in sd.read_jsonl(s2.SEEDS_PATH) if s["seed_id"] in set(select)}
    for x in chosen:
        if x["rung"] not in seeds[x["seed_id"]]["use_case_levels_applicable"]:
            raise SystemExit(f"{x['seed_id']}: rung {x['rung']} not applicable to the seed")
    records = sd.read_jsonl(r2.INGESTED_PATH)
    indep = json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    nca = sd.nca_map()
    gz = lg.Gazetteer(nca)  # v2 (D-047a)
    by_statement = spk.statement_lookup(records, indep)
    rows = s2.statement_table(records, sd.read_jsonl(li.CLUSTERS_V1B_PATH), indep, gz)
    groups = lgr.read_groups(a.groups)
    hashes = spk.inputs_hashes(s2.SEEDS_PATH, a.groups, a.selection)
    a.out.mkdir(parents=True, exist_ok=True)
    index = []
    for x in chosen:
        sid = x["seed_id"]
        pk = spk.build_packet(seeds[sid], x["rung"], f"BI-P2B-{x['order']:04d}", groups, by_statement, rows, nca, hashes,
                              selection={"file": repo_relative(a.selection), "decision": sel["decision"], **x})
        path = a.out / f"{pk['packet_id']}.json"
        r2.write_json(path, pk)
        roles = [g["role"] for g in pk["model_view"]["groups"]]
        index.append({"packet_id": pk["packet_id"], "item_id": pk["item_id"], "seed_id": sid, "level": pk["use_case_level"],
                      "groups": len(roles), **{f"groups_{r}": roles.count(r) for r in ("driver", "context", "caveat")},
                      "excluded_groups": len(pk["excluded_groups"]), "sha256": sha256_file(path)})
    r2.write_json(a.out / "index.json", {"version": spk.VERSION, "rank_rule": spk.RANK_RULE, "geography": lg.VERSION,
                                         "inputs_sha256": hashes, "packets": index})
    rec = write_run_record(
        "build_synth_packets", result_summary={"packets": index}, passed=True, data_path=a.groups, output_path=a.out / "index.json",
        config_snapshot={"version": spk.VERSION, "rank_rule": spk.RANK_RULE, "geography": lg.VERSION, "select": select,
                         "selection": repo_relative(a.selection), "max_passage": spk.MAX_PASSAGE,
                         "max_groups": {"driver": spk.MAX_DRIVER_GROUPS, "context": spk.MAX_CONTEXT_GROUPS,
                                        "caveat": spk.MAX_CAVEAT_GROUPS}, "inputs_sha256": hashes, "model_calls": 0},
    )
    print(json.dumps(index, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
