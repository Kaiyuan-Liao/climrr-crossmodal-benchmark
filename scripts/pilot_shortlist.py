#!/usr/bin/env python3
"""Pilot P2b-prep Phase D: the 20-seed pilot shortlist (Kaiyuan selects 10 from it).

Reads `artifacts/benchmark/item_seeds_v2.jsonl` (gitignored; checked against the SHA-256 in
`item_seeds_v2_summary.json`). Writes the tracked `artifacts/benchmark/pilot_shortlist_v1.csv`
and `pilot_shortlist_v1_summary.json`; if a level-4 or level-7 quota is short, also the full
pool of eligible level-4 and level-7 seeds (`pilot_shortlist_v1_level4_level7_pool.csv`).
Rule: `src/climrr/pilot_shortlist.py`. Deterministic; no model call, no table value computed.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import itemseeds_v2 as s2  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import pilot_shortlist as ps  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ps.COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    pin = json.loads(s2.SUMMARY_PATH.read_text(encoding="utf-8"))["seeds_file"]["sha256"]
    if sha256_file(s2.SEEDS_PATH) != pin:
        raise SystemExit(f"{repo_relative(s2.SEEDS_PATH)} differs from its pin {pin}; run scripts/build_item_seeds_v2.py")
    seeds = sd.read_jsonl(s2.SEEDS_PATH)
    picks, shortfall = ps.select(seeds)
    write_csv(ps.SHORTLIST_PATH, [ps.row(lv, s, c) for lv, s, c in picks])
    pools = {lv: ps.candidates(seeds, lv) for lv in (4, 7)}
    if shortfall.get(4) or shortfall.get(7):
        write_csv(ps.POOL_PATH, [ps.row(lv, s, None) for lv in (4, 7) for s in pools[lv]])
    summary = {"version": ps.VERSION, "rule": "work package P2b-prep Phase D", "quota": ps.QUOTA, "fill_order": list(ps.FILL_ORDER),
               "state_cap": ps.STATE_CAP, "seeds_sha256": pin,
               "shortlist_file": {"path": "artifacts/benchmark/pilot_shortlist_v1.csv", "sha256": sha256_file(ps.SHORTLIST_PATH)},
               "chosen": len(picks), "chosen_by_level": {str(lv): sum(p[0] == lv for p in picks) for lv in ps.QUOTA},
               "candidates_by_level": {str(lv): len(ps.candidates(seeds, lv)) for lv in ps.QUOTA},
               "shortfall": {str(k): v for k, v in shortfall.items()},
               "level4_pool": [s["seed_id"] for s in pools[4]], "level7_pool": [s["seed_id"] for s in pools[7]],
               "states_used": dict(sorted(Counter(ps.place(p[1]) for p in picks).items()))}
    r2.write_json(ps.SUMMARY_PATH, summary)
    rec = write_run_record(
        "pilot_shortlist", result_summary=summary, passed=True, data_path=s2.SEEDS_PATH, output_path=ps.SHORTLIST_PATH,
        config_snapshot={"version": ps.VERSION, "quota": ps.QUOTA, "fill_order": list(ps.FILL_ORDER), "state_cap": ps.STATE_CAP,
                         "level3_combinations": ["/".join(c) for c in ps.L3_COMBOS], "model_calls": 0},
    )
    print(json.dumps({k: v for k, v in summary.items() if k not in ("level4_pool", "level7_pool")}, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
