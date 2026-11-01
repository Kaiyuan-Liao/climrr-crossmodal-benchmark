"""Pilot shortlist v1: 20 seeds chosen by rule from the eligible v2 seeds; Kaiyuan selects 10 (pilot P2b-prep; D-041, D-048).

**Rule** (work package P2b-prep, Phase D): heat index only (FWI is not shortlisted); at
most 2 seeds per state; levels and quotas ---

- **1** (3 seeds): pattern only; statistic `direction`, or a pattern carrying a relative tercile;
- **3** (9 seeds): pattern + drivers; a single-place pattern with a relevant mechanism /
  driver statement; 95 °F and 105 °F thresholds, mid and end century, absolute and percent
  change --- the 8 combinations are filled in turn (95 mid abs, 95 mid pct, 95 end abs, 95
  end pct, then 105 likewise), each with its highest-ranked candidate, and the ninth seed
  goes to the first combination again;
- **4** (6 seeds): a regional contrast (NCA5-region ranking) with a relevant mechanism /
  driver statement;
- **7** (2 seeds): a single-place pattern with a relevant caveat statement that names a
  scenario.

Within a level, highest-ranked first (`seed_rank_key`, `itemseeds_v2`), skipping a seed whose
state is already used twice; a seed is chosen once.

**EXECUTOR choices (recorded):** levels are filled scarcest-first --- 7, 3, 4, 1 --- so the
per-state cap does not spend states on pattern-only items before the levels that need
state literature; the cap counts a state pattern's state and an NCA5-region pattern's
region (a regional contrast covers all regions and is not capped); the control cell
(`cell_control`) is not shortlisted --- it is neither a state nor a region. A shortfall is
reported, never filled from another level.

No model call, no table value computed (values are copied from the pattern, rounded as
`synthpackets.show`).
"""

from __future__ import annotations

from collections import Counter

from climrr import synthpackets as spk
from climrr.paths import REPO_ROOT

VERSION = "pilot_shortlist v1"
SHORTLIST_PATH = REPO_ROOT / "artifacts" / "benchmark" / "pilot_shortlist_v1.csv"
POOL_PATH = REPO_ROOT / "artifacts" / "benchmark" / "pilot_shortlist_v1_level4_level7_pool.csv"
SUMMARY_PATH = REPO_ROOT / "artifacts" / "benchmark" / "pilot_shortlist_v1_summary.json"
QUOTA = {1: 3, 3: 9, 4: 6, 7: 2}
FILL_ORDER = (7, 3, 4, 1)
STATE_CAP = 2
L3_COMBOS = [(t, h, s) for t in ("95", "105") for h in ("mid", "end") for s in ("absolute_change", "percent_change")]
COLUMNS = ("seed_id", "level", "state_or_region", "threshold_F", "season", "horizon", "horizon_window", "scenario", "statistic",
           "value", "direction", "relative_tercile", "best_strength", "n_relevant_core_cited_background",
           "n_relevant_explaining_core_cited_background", "n_explaining_named_state_or_region", "seed_rank_key",
           "top_statement_1", "top_statement_2", "top_statement_3", "top_named_place_statements", "blockers", "pattern_id", "level3_combination")


def place(s: dict) -> str:
    return "all covered NCA5 regions" if s["pattern_kind"] == "regional_contrast" else s["geography"]


def cap_key(s: dict) -> str | None:
    return None if s["pattern_kind"] == "regional_contrast" else s["geography"]


def combination(s: dict) -> tuple:
    return (spk.threshold(s["pattern"]), s["horizon"], s["statistic"])


def candidates(seeds: list[dict], level: int) -> list[dict]:
    base = [s for s in seeds if s["eligible_for_pilot"] and s["family"] == "heat_index" and s["geography_type"] != "cell_control"]
    if level == 1:
        out = [s for s in base if s["pattern_kind"] == "single" and (s["statistic"] == "direction" or s["has_relative_tercile"])]
    elif level == 3:
        out = [s for s in base if s["pattern_kind"] == "single" and 3 in s["use_case_levels_applicable"] and combination(s) in L3_COMBOS]
    elif level == 4:
        out = [s for s in base if s["pattern_kind"] == "regional_contrast" and 4 in s["use_case_levels_applicable"]]
    else:
        out = [s for s in base if s["pattern_kind"] == "single" and 7 in s["use_case_levels_applicable"]]
    return sorted(out, key=lambda s: s["seed_rank_key"])


def select(seeds: list[dict]) -> tuple[list[tuple[int, dict, str | None]], dict]:
    used: Counter = Counter()
    chosen: set[str] = set()
    picks: list[tuple[int, dict, str | None]] = []
    shortfall = {}

    def ok(s):
        k = cap_key(s)
        return s["seed_id"] not in chosen and (k is None or used[k] < STATE_CAP)

    def take(level, s, combo=None):
        picks.append((level, s, combo))
        chosen.add(s["seed_id"])
        if cap_key(s):
            used[cap_key(s)] += 1

    for level in FILL_ORDER:
        cands = candidates(seeds, level)
        if level == 3:
            exhausted, i = set(), 0
            while sum(p[0] == 3 for p in picks) < QUOTA[3] and len(exhausted) < len(L3_COMBOS):
                combo = L3_COMBOS[i % len(L3_COMBOS)]
                i += 1
                if combo in exhausted:
                    continue
                s = next((c for c in cands if ok(c) and combination(c) == combo), None)
                if s is None:
                    exhausted.add(combo)
                    continue
                take(3, s, "/".join(combo))
        else:
            for s in cands:
                if len([p for p in picks if p[0] == level]) >= QUOTA[level]:
                    break
                if ok(s):
                    take(level, s)
        got = sum(p[0] == level for p in picks)
        if got < QUOTA[level]:
            shortfall[level] = {"quota": QUOTA[level], "chosen": got, "candidates": len(candidates(seeds, level))}
    picks.sort(key=lambda p: ((1, 3, 4, 7).index(p[0]), p[1]["seed_rank_key"]))
    return picks, shortfall


def _value(s: dict) -> str:
    v = s["pattern"]["computed_value_or_range"]
    if s["pattern_kind"] == "regional_contrast":
        return " > ".join(f"{r['name']} {spk.show(r['value'])}" if r.get("value") is not None else f"({r['name']} not ranked: {r.get('reason')})"
                          for r in v["regions_ordered"])
    if v.get("value") is None:
        return ""
    unit = "%" if v.get("unit") == "percent" else f" {v.get('unit')}"
    return f"{spk.show(v['value'])}{unit}" + (" (mean change)" if s["statistic"] == "direction" else "")


def row(level: int, s: dict, combo: str | None) -> dict:
    fmt = lambda t: f"[{t['statement_id']}; {t['statement_type']}; {t['role']}; {t['basis']}; {t['cluster_strength']}] {t['statement']}"  # noqa: E731
    tops = [fmt(t) for t in (s["top_scenario_caveats"] if level == 7 else s["top_explaining"])]
    r = s["n_relevant_by_role"]
    e = s["n_relevant_explaining_by_role"]
    return {"seed_id": s["seed_id"], "level": level, "state_or_region": place(s), "threshold_F": spk.threshold(s["pattern"]) or "",
            "season": s["season"], "horizon": s["horizon"], "horizon_window": s["horizon_window"], "scenario": s["scenario"],
            "statistic": s["statistic"], "value": _value(s), "direction": s["direction"],
            "relative_tercile": (s["pattern"].get("relative_magnitude") or {}).get("class", ""),
            "best_strength": s["best_explaining_strength"] or "",
            "n_relevant_core_cited_background": f"{r['core']}/{r['cited']}/{r['background']}",
            "n_relevant_explaining_core_cited_background": f"{e['core']}/{e['cited']}/{e['background']}",
            "n_explaining_named_state_or_region": s["n_relevant_explaining_specific"], "seed_rank_key": s["seed_rank_key"],
            **{f"top_statement_{i + 1}": tops[i] if i < len(tops) else "" for i in range(3)},
            "top_named_place_statements": " || ".join(fmt(t) for t in s["top_explaining_named_place"]),
            "blockers": ";".join(b["blocker"] + ("" if b["blocks_eligibility"] else " (non-blocking)") for b in s["acceptance_blockers"]),
            "pattern_id": s["pattern"]["pattern_id"], "level3_combination": combo or ""}
