"""Pilot shortlist v1 (pilot P2b-prep, Phase D): the rule on synthetic seeds, and the frozen CSV."""

from __future__ import annotations

import csv
import json
from collections import Counter

from climrr import pilot_shortlist as ps


def _seed(n, state, stat="absolute_change", horizon="mid", thr="95", levels=(3, 1), kind="single", tercile=False, family="heat_index",
          eligible=True, gtype="state"):
    return {"seed_id": f"SD2-TP1-{n:05d}", "seed_rank_key": n, "eligible_for_pilot": eligible, "family": family, "geography_type": gtype,
            "geography": state, "pattern_kind": kind, "statistic": stat, "horizon": horizon, "has_relative_tercile": tercile,
            "use_case_levels_applicable": list(levels),
            "pattern": {"metric_wording": f"number of days with daily max heat index above {thr} F", "pattern_id": f"TP1-{n:05d}"}}


def test_the_state_cap_the_fill_order_and_distinct_seeds():
    seeds = [_seed(1, "Texas", levels=(3, 7, 1)), _seed(2, "Texas", stat="percent_change", levels=(3, 7, 1)),
             _seed(3, "Texas", stat="direction", levels=(3, 1)), _seed(4, "Ohio", stat="direction", levels=(3, 1))]
    picks, short = ps.select(seeds)
    got = [(lv, s["seed_id"]) for lv, s, _ in picks]
    assert got == [(1, "SD2-TP1-00004"), (7, "SD2-TP1-00001"), (7, "SD2-TP1-00002")]   # level 7 first takes both Texas slots
    assert short[3]["chosen"] == 0 and short[1] == {"quota": 3, "chosen": 1, "candidates": 2}


def test_level_3_cycles_the_eight_combinations_then_repeats_the_first():
    seeds = [_seed(i * 10 + j, f"S{i}{j}", stat=s, horizon=h, thr=t)
             for i, (t, h, s) in enumerate(ps.L3_COMBOS) for j in range(2)]
    picks, _ = ps.select(seeds)
    combos = [c for lv, _, c in picks if lv == 3]
    assert Counter(combos) == Counter(["/".join(c) for c in ps.L3_COMBOS] + ["95/mid/absolute_change"])
    assert {s["seed_id"] for lv, s, c in picks if c == "95/mid/absolute_change"} == {"SD2-TP1-00000", "SD2-TP1-00001"}


def test_fwi_control_cells_and_ineligible_seeds_are_never_shortlisted():
    seeds = [_seed(1, "Texas", family="fire_weather_index"), _seed(2, "cell", gtype="cell_control"), _seed(3, "Ohio", eligible=False)]
    assert ps.select(seeds)[0] == []


def test_regional_contrasts_are_not_capped():
    seeds = [_seed(i, "all_covered_nca5_regions", kind="regional_contrast", levels=(4, 3, 1)) for i in range(1, 8)]
    picks, short = ps.select(seeds)
    assert sum(lv == 4 for lv, _, _ in picks) == 6 and 4 not in short


def test_the_frozen_shortlist():
    rows = list(csv.DictReader(open(ps.SHORTLIST_PATH, encoding="utf-8")))
    assert len(rows) == 20 and len({r["seed_id"] for r in rows}) == 20
    assert Counter(int(r["level"]) for r in rows) == {1: 3, 3: 9, 4: 6, 7: 2}
    caps = Counter(r["state_or_region"] for r in rows if r["state_or_region"] != "all covered NCA5 regions")
    assert max(caps.values()) <= 2
    assert sorted(r["level3_combination"] for r in rows if r["level"] == "3") == sorted(
        ["/".join(c) for c in ps.L3_COMBOS] + ["95/mid/absolute_change"])
    s = json.loads(ps.SUMMARY_PATH.read_text(encoding="utf-8"))
    assert s["shortfall"] == {} and s["chosen"] == 20 and tuple(rows[0].keys()) == ps.COLUMNS
