#!/usr/bin/env python3
"""Pilot P2b: seed packets for the item-synthesis agent, from the selected shortlist seeds and the grouping run.

Reads `artifacts/benchmark/item_seeds_v2.jsonl` (gitignored; checked against its pin), the
shortlist CSV (the level each seed is built at), the grouping run's `groups.jsonl`,
`statements_ingested.jsonl` and `independence_v2.json`. For each selected seed id, in the
order given, writes `<out>/PK-<seed_id>.json` with item id `BI-P2B-<nnnn>` and an
`index.json`. Rules: `src/climrr/synthpackets.py`. Deterministic; no model call, no table value computed.

    python scripts/build_synth_packets.py --groups <litgroups run1>/groups.jsonl \\
        --select SD2-TP1-00071,SD2-TP1-00017,... [--shortlist artifacts/benchmark/pilot_shortlist_v1.csv] \\
        [--out artifacts/benchmark/synth_packets]
"""

from __future__ import annotations

import argparse
import csv
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
from climrr import pilot_shortlist as ps  # noqa: E402
from climrr import synthpackets as spk  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--groups", required=True, type=Path)
    ap.add_argument("--select", required=True, help="seed ids, comma-separated, in item order")
    ap.add_argument("--shortlist", type=Path, default=ps.SHORTLIST_PATH)
    ap.add_argument("--out", type=Path, default=spk.PACKETS_DIR)
    a = ap.parse_args()
    pin = json.loads(s2.SUMMARY_PATH.read_text(encoding="utf-8"))["seeds_file"]["sha256"]
    if sha256_file(s2.SEEDS_PATH) != pin:
        raise SystemExit(f"{repo_relative(s2.SEEDS_PATH)} differs from its pin {pin}; run scripts/build_item_seeds_v2.py")
    level_of = {r["seed_id"]: int(r["level"]) for r in csv.DictReader(open(a.shortlist, encoding="utf-8"))}
    select = [x.strip() for x in a.select.split(",") if x.strip()]
    missing = [x for x in select if x not in level_of]
    if missing:
        raise SystemExit(f"not on the shortlist: {missing}")
    seeds = {s["seed_id"]: s for s in sd.read_jsonl(s2.SEEDS_PATH) if s["seed_id"] in set(select)}
    records = sd.read_jsonl(r2.INGESTED_PATH)
    indep = json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    nca = sd.nca_map()
    gz = lg.Gazetteer(nca)
    by_statement = spk.statement_lookup(records, indep)
    rows_geo = {sid: lg.classify(r["proposal"].get("region"), r["proposal"].get("region_scope"), gz) for sid, r in by_statement.items()}
    groups = lgr.read_groups(a.groups)
    hashes = spk.inputs_hashes(s2.SEEDS_PATH, a.groups)
    a.out.mkdir(parents=True, exist_ok=True)
    index = []
    for n, sid in enumerate(select, 1):
        pk = spk.build_packet(seeds[sid], level_of[sid], f"BI-P2B-{n:04d}", groups, by_statement, rows_geo, nca, hashes)
        path = a.out / f"{pk['packet_id']}.json"
        r2.write_json(path, pk)
        index.append({"packet_id": pk["packet_id"], "item_id": pk["item_id"], "seed_id": sid, "level": pk["use_case_level"],
                      "groups": len(pk["model_view"]["groups"]), "sha256": sha256_file(path)})
    r2.write_json(a.out / "index.json", {"version": spk.VERSION, "inputs_sha256": hashes, "packets": index})
    rec = write_run_record(
        "build_synth_packets", result_summary={"packets": index}, passed=True, data_path=a.groups, output_path=a.out / "index.json",
        config_snapshot={"version": spk.VERSION, "select": select, "max_passage": spk.MAX_PASSAGE,
                         "max_groups": [spk.MAX_EXPLAIN_GROUPS, spk.MAX_CAVEAT_GROUPS], "inputs_sha256": hashes, "model_calls": 0},
    )
    print(json.dumps(index, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
