#!/usr/bin/env python3
"""Work package P3a, section D: item seeds v3 and the fire-weather application of the shortlist rule (D-059, D-061, D-064).

Reads the pinned `artifacts/benchmark/item_seeds_v2.jsonl` (gitignored; checked against the hash in
`item_seeds_v2_summary.json`) and the working assumptions in `data/metadata/resolutions.yaml` (D-064). Writes:

- `artifacts/benchmark/item_seeds_v3.jsonl` (gitignored, pinned in the summary) and the tracked
  `item_seeds_v3_summary.json`: working assumptions attached, the FWI-summer blocker replaced, rungs 1 and 7 retired,
  eligibility and rank recomputed (`src/climrr/itemseeds_v3.py`);
- `artifacts/benchmark/pilot_shortlist_fwi_v1.csv` (tracked): the two fire-weather seeds the shortlist rule picks (two
  different states, summer seasonal FWI, mid- and end-century; `pilot_shortlist.fwi_select`) and the next candidates of
  each horizon, for Kaiyuan's confirmation.

Deterministic; no model call, no table value computed, no column status changed.

    python scripts/build_item_seeds_v3.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import itemseeds_v2 as s2  # noqa: E402
from climrr import itemseeds_v3 as s3  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import pilot_shortlist as ps  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    v2_summary = json.loads(s2.SUMMARY_PATH.read_text(encoding="utf-8"))
    pin = v2_summary["seeds_file"]["sha256"]
    if not s2.SEEDS_PATH.is_file() or sha256_file(s2.SEEDS_PATH) != pin:
        raise SystemExit(f"{repo_relative(s2.SEEDS_PATH)} is absent or differs from its pin {pin}; run scripts/build_item_seeds_v2.py")
    was = s3.load_working_assumptions()
    seeds = s3.build(sd.read_jsonl(s2.SEEDS_PATH), was)
    r2.write_jsonl(s3.SEEDS_PATH, seeds)
    summary = s3.summarise(seeds, v2_summary)
    picks = ps.fwi_select(seeds)
    rows = ps.fwi_rows(seeds)
    with open(ps.FWI_SHORTLIST_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ps.FWI_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    summary["fwi_shortlist"] = {"version": ps.FWI_VERSION, "path": repo_relative(ps.FWI_SHORTLIST_PATH),
                                "sha256": sha256_file(ps.FWI_SHORTLIST_PATH),
                                "rule": {"metric": ps.FWI_METRIC, "statistic": ps.FWI_STATISTIC, "horizons": list(ps.FWI_HORIZONS),
                                         "geography_type": "state", "distinct_states": True, "level": 3},
                                "candidates": {h: len(ps.fwi_candidates(seeds, h)) for h in ps.FWI_HORIZONS},
                                "picks": [{"seed_id": s["seed_id"], "state": s["geography"], "horizon": s["horizon"],
                                           "seed_rank_key": s["seed_rank_key"], "pattern_id": s["pattern"]["pattern_id"]} for s in picks]}
    r2.write_json(s3.SUMMARY_PATH, summary)
    result = {k: summary[k] for k in ("seeds", "eligible", "eligible_v2", "eligible_by_family", "eligible_by_level", "became_eligible",
                                      "became_ineligible", "fwi", "heat_index", "eligible_by_working_assumption", "blockers_replaced",
                                      "blockers_remaining", "fwi_shortlist")}
    result.update(seeds_sha256=summary["seeds_file"]["sha256"], summary_sha256=sha256_file(s3.SUMMARY_PATH))
    rec = write_run_record(
        "build_item_seeds_v3", result_summary=result, passed=True, data_path=s2.SEEDS_PATH, output_path=s3.SEEDS_PATH,
        config_snapshot={"rule": s3.RULE_ID, "decisions": list(s3.DECISIONS), "version": s3.VERSION,
                         "retired_levels": {str(k): v for k, v in s3.RETIRED_LEVELS.items()},
                         "resolutions_sha256": sha256_file(s3.RESOLUTIONS_PATH), "seeds_v2_sha256": pin,
                         "working_assumptions": sorted(was), "fwi_shortlist_version": ps.FWI_VERSION, "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
