"""Item seeds v3: the v2 seeds under the mentor feedback of 2026-11-13 (DR-SEED-1 v3; D-059, D-061, D-064; work package P3a).

Built from the pinned `item_seeds_v2.jsonl` (`itemseeds_v2.py`, unchanged: pairing, geography v1 at seed level,
relevance, strength), one v3 seed per v2 seed, by three changes and nothing else:

- **Working assumptions (D-064).** The owner-authorized working assumptions in `data/metadata/resolutions.yaml` (records
  with a `working_assumption`, status `owner_authorized_working_assumption`) are attached to every pattern that relies on
  them (`pattern_working_assumptions`): WA-FWI-SUMMER (a pattern reading columns 189--193), WA-STATE-LABEL (the IC-012
  provisional State label), WA-NAME-LABEL (a pattern reading column 2 or selecting rows by `NAME`), WA-FWI-PCT-SCENARIO (an
  FWI percent-change column whose scenario the dictionary leaves unstated), WA-UNWEIGHTED-MEAN (the unweighted-mean
  provisional aggregation rule). An acceptance blocker a working assumption covers is replaced by it: the FWI-summer
  blocker IC-006 -- IC-010 (which blocked eligibility) and the non-blocking IC-012 marker. The seed's pattern copy then
  reads `acceptance_blocked: false`, keeps the original blockers in `acceptance_blocked_by_original`, and carries
  `working_assumptions` (ids); `table_patterns_v1.jsonl` is unchanged. Those patterns become eligible.
- **Rungs (D-059, D-061).** Rung 1 (pattern only) is dropped from the benchmark and rung 7 (scenario) is retired for now:
  both leave `use_case_levels_applicable` (the v2 list is kept as `use_case_levels_applicable_v2`).
- **Eligibility and rank.** Eligible = not blocked after the replacement, computed, >= 1 relevant mechanism / driver
  statement (DR-SEED-1 v2, unchanged) and a rung left; the seed rank is recomputed over the v3 eligibility by the v2 key
  (`itemseeds_v2.seed_order_key`); the v2 rank and eligibility are kept beside it.

No model call, no table value computed, no column status changed (a working assumption is not a status).
"""

from __future__ import annotations

import copy
from collections import Counter

from climrr import dictionary as dc
from climrr import itemseeds_v2 as s2
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

VERSION = "itemseeds v3"
RULE_ID = "DR-SEED-1 v3"
DECISIONS = ("D-059", "D-061", "D-064")
SEEDS_PATH = REPO_ROOT / "artifacts" / "benchmark" / "item_seeds_v3.jsonl"
SUMMARY_PATH = REPO_ROOT / "artifacts" / "benchmark" / "item_seeds_v3_summary.json"
RESOLUTIONS_PATH = REPO_ROOT / "data" / "metadata" / "resolutions.yaml"
RETIRED_LEVELS = {1: "D-059", 7: "D-061"}
FWI_SUMMER, STATE_LABEL, NAME_LABEL = "WA-FWI-SUMMER", "WA-STATE-LABEL", "WA-NAME-LABEL"
FWI_PCT_SCENARIO, UNWEIGHTED_MEAN = "WA-FWI-PCT-SCENARIO", "WA-UNWEIGHTED-MEAN"


def load_working_assumptions(path=RESOLUTIONS_PATH) -> dict:
    return dc.working_assumptions(dc.load_resolutions(open(path, encoding="utf-8").read()))


def pattern_working_assumptions(p: dict, was: dict) -> list[str]:
    """The working-assumption ids pattern `p` relies on, in a fixed order."""
    cols = {c["index"] for c in p["provenance"]["columns"]}
    reasons = p.get("provisional_reasons") or []
    out = []
    if cols & set(was[FWI_SUMMER]["columns_relied_on"]):
        out.append(FWI_SUMMER)
    if any("IC-012" in r for r in reasons) or "State" in (p["provenance"].get("row_rule") or ""):
        out.append(STATE_LABEL)
    if cols & set(was[NAME_LABEL]["columns_relied_on"]) or "NAME" in (p["provenance"].get("row_rule") or ""):
        out.append(NAME_LABEL)
    if cols & set(was[FWI_PCT_SCENARIO]["columns_relied_on"]) and p["scenario"] == "unstated_in_dictionary":
        out.append(FWI_PCT_SCENARIO)
    if any(r.startswith("unweighted_mean") for r in reasons):
        out.append(UNWEIGHTED_MEAN)
    return out


def replaced(blocker: dict, ids: list[str], was: dict) -> str | None:
    """The working assumption that replaces `blocker` (an `itemseeds.blockers` record), or None."""
    for wid in ids:
        if blocker["blocker"] in was[wid]["covers"]:
            return wid
    return None


def seed_v3(s: dict, was: dict) -> dict:
    p = s["pattern"]
    ids = pattern_working_assumptions(p, was)
    keep = [b for b in s["acceptance_blockers"] if replaced(b, ids, was) is None]
    gone = [dict(b, replaced_by=replaced(b, ids, was)) for b in s["acceptance_blockers"] if replaced(b, ids, was) is not None]
    blocked = any(b["blocks_eligibility"] for b in keep)
    pv = copy.deepcopy(p)
    if p["acceptance_blocked"] and not blocked:
        pv["acceptance_blocked_by_original"] = list(p.get("acceptance_blocked_by") or [])
        pv["acceptance_blocked_by"] = []
        pv["acceptance_blocked"] = False
    pv["working_assumptions"] = ids
    levels = [lv for lv in s["use_case_levels_applicable"] if lv not in RETIRED_LEVELS]
    eligible = (not blocked) and s["pattern_computed"] and s["n_relevant_explaining"] > 0 and bool(levels)
    out = dict(s, rule=RULE_ID, version=VERSION, decisions=list(DECISIONS), pattern=pv,
               use_case_levels_applicable=levels, use_case_levels_applicable_v2=s["use_case_levels_applicable"],
               use_case_level=levels[0] if levels else None,
               use_case_level_name=s2.sd.LEVELS[levels[0]] if levels else None,
               acceptance_blockers=keep, acceptance_blockers_replaced=gone, acceptance_blocked=blocked,
               working_assumptions=[{"id": w, "resolution": was[w]["resolution"], "status": was[w]["status"]} for w in ids],
               eligible_for_pilot=eligible, eligible_for_pilot_v2=s["eligible_for_pilot"],
               seed_rank_key=None, seed_rank_key_v2=s["seed_rank_key"])
    return out


def build(seeds_v2: list[dict], was: dict) -> list[dict]:
    seeds = [seed_v3(s, was) for s in seeds_v2]
    for rank, i in enumerate(sorted(range(len(seeds)), key=lambda i: s2.seed_order_key(seeds[i])), 1):
        seeds[i]["seed_rank_key"] = rank
    return seeds


def summarise(seeds: list[dict], v2_summary: dict) -> dict:
    elig = [s for s in seeds if s["eligible_for_pilot"]]
    fwi = [s for s in seeds if s["family"] == "fire_weather_index"]
    return {
        "version": VERSION, "rule": RULE_ID, "decisions": list(DECISIONS),
        "inputs": {"item_seeds_v2": {"path": "artifacts/benchmark/item_seeds_v2.jsonl", "sha256": v2_summary["seeds_file"]["sha256"]},
                   "resolutions": {"path": "data/metadata/resolutions.yaml", "sha256": sha256_file(RESOLUTIONS_PATH)}},
        "seeds_file": {"path": "artifacts/benchmark/item_seeds_v3.jsonl", "sha256": sha256_file(SEEDS_PATH), "gitignored": True},
        "retired_levels": {str(k): v for k, v in RETIRED_LEVELS.items()},
        "seeds": len(seeds), "eligible": len(elig), "eligible_v2": v2_summary["eligible"],
        "eligible_by_family": dict(sorted(Counter(s["family"] for s in elig).items())),
        "eligible_by_level": dict(sorted(Counter(str(s["use_case_level"]) for s in elig).items())),
        "eligible_levels_applicable": dict(sorted(Counter(str(lv) for s in elig for lv in s["use_case_levels_applicable"]).items())),
        "eligible_by_metric": dict(sorted(Counter(s["metric"] for s in elig).items())),
        "became_eligible": sum(s["eligible_for_pilot"] and not s["eligible_for_pilot_v2"] for s in seeds),
        "became_ineligible": sum(s["eligible_for_pilot_v2"] and not s["eligible_for_pilot"] for s in seeds),
        "fwi": {"seeds": len(fwi),
                "acceptance_blocked_v2": sum(any(b["blocks_eligibility"] for b in s["acceptance_blockers"] + s["acceptance_blockers_replaced"])
                                             for s in fwi),
                "acceptance_blocked_v3": sum(s["acceptance_blocked"] for s in fwi), "eligible": sum(s["eligible_for_pilot"] for s in fwi),
                "eligible_fwi_summer_seasonal_value": sum(s["eligible_for_pilot"] and s["metric"] == "fwi_summer_seasonal_value" for s in fwi)},
        "heat_index": {"seeds": sum(s["family"] == "heat_index" for s in seeds),
                       "eligible": sum(s["eligible_for_pilot"] and s["family"] == "heat_index" for s in seeds)},
        "seeds_by_working_assumption": dict(sorted(Counter(w["id"] for s in seeds for w in s["working_assumptions"]).items())),
        "eligible_by_working_assumption": dict(sorted(Counter(w["id"] for s in elig for w in s["working_assumptions"]).items())),
        "blockers_replaced": dict(sorted(Counter(f"{b['blocker']} -> {b['replaced_by']}" for s in seeds
                                                 for b in s["acceptance_blockers_replaced"]).items())),
        "blockers_remaining": dict(sorted(Counter(b["blocker"] for s in seeds for b in s["acceptance_blockers"]).items())),
    }
