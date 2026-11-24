"""Rung-8 seeds (DR-SEED-INFRA-1) and the rung-8 pilot selection (work package P5b, part C; D-075). Implemented, not run.

Runs after the Polaris grouping run over `partitions_infra_v1.jsonl` is ingested (P5c); the rung-8 packets are built in P5c
from these seeds. Inputs: the v3 seeds (`item_seeds_v3.jsonl`, pinned; their pattern copies carry the working assumptions
and acceptance flags, D-064), the ingested infra statements (`artifacts/litstatements/infra_run1/statements_ingested.jsonl`)
and their independence (D-046), and the infra groups (the grouping agent's `groups.jsonl` records: `group_id`,
`statement_type`, `claim_about`, `member_ids` --- everything else is recomputed here from the member statements).

**DR-SEED-INFRA-1 (D-075).** A rung-8 seed = (a table pattern for family F at place P) + the impact groups of family F for
asset class A + the family's driver groups as in rung 3.

- *Table patterns*: the eligible single-state patterns of F (computed, not acceptance-blocked after the working
  assumptions) at the rung-8 table setting `TABLE_SETTING` (metric, statistic, horizon per family; EXECUTOR default, for
  confirmation: the rung-3 pilot's choices, days above 95 F and the summer seasonal FWI, absolute change, mid-century).
- *Impact groups of F for A*: groups of `statement_type` impact with `claim_about` `hazard_impact_on_asset` (the agent's
  tag; `disposition_exclude` honoured when present), whose members' family is F and at least one of whose passing members
  has asset class A; strength over the core / cited members (D-045, D-046) not `background_only`.
- *Geography relevance* (litgeo v2, per member, the best over the group's core / cited members): `place_named` when a
  member names P (class state, P among its states), `us` for an NCA5-region, U.S.-subregion or U.S.-national member,
  `general` otherwise (global, other countries, unknown). Order place_named > us > general; general is expected and
  allowed (D-069; the closing clause is then mandatory).
- *Driver groups*: the family's driver groups as a rung-3 packet attaches them (`synthpackets.packet_groups(3, ...)`, role
  driver, over the LITCORPUS-02 grouping run 2 with dispositions; `rung3_driver_ids`), recorded by group id.
- One seed per (pattern, asset class) with >= 1 impact group. Impact groups ranked by (relevance, strength, more
  independent papers, group id); seeds ranked by (best impact-group strength, more independent papers over the seed's
  impact groups, pattern id, asset class).

**Rung-8 pilot selection (D-075; for Alvi's samples).** Eight (family, asset class) cells: heat x {energy, transportation,
water, healthcare} and fire weather x {energy, transportation, emergency services, communications}. Each at the state
with the largest table change (the pattern value at the table setting) among the states that have a passing,
place-named impact statement of that family and class (litgeo v2 class state naming the state), else California; then
that state's seed for the class. A cell whose seed does not exist (no impact group of the class) is reported, not filled.
Question forms: QF-08, QF-09, QF-10 (`question_forms_v2.yaml`) round-robin in selection order.

No model call; no table value computed (values are read from the pattern records).
"""

from __future__ import annotations

from collections import Counter

import yaml

from climrr import litaggregate as la
from climrr import litgeo as lg
from climrr import litindependence as li
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

VERSION = "seeds_infra v1"
RULE_ID = "DR-SEED-INFRA-1"
DECISION = "D-075"
RUNG = 8
IMPACT_CLAIM = "hazard_impact_on_asset"
STRENGTH_ORDER = {s: i for i, s in enumerate(la.STRENGTHS)}
GEO_TIERS = ("place_named", "us", "general")
US_CLASSES = ("nca", "us_subregion", "us_national")
#: Rung-8 table setting per family (EXECUTOR default, for confirmation; the rung-3 pilot's choices, pilot_selection_v2a).
TABLE_SETTING = {"heat_index": {"metric": "heatindex_days_above_95F", "statistic": "absolute_change", "horizon": "mid"},
                 "fire_weather_index": {"metric": "fwi_summer_seasonal_value", "statistic": "absolute_change", "horizon": "mid"}}
PILOT_CELLS = (("heat_index", "energy"), ("heat_index", "transportation_systems"), ("heat_index", "water_and_wastewater"),
               ("heat_index", "healthcare_and_public_health"), ("fire_weather_index", "energy"),
               ("fire_weather_index", "transportation_systems"), ("fire_weather_index", "emergency_services"),
               ("fire_weather_index", "communications"))
FALLBACK_STATE = "California"
QUESTION_FORMS_V2_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "question_forms_v2.yaml"
SEEDS_PATH = REPO_ROOT / "artifacts" / "benchmark" / "item_seeds_infra_v1.jsonl"
SEEDS_SUMMARY_PATH = REPO_ROOT / "artifacts" / "benchmark" / "item_seeds_infra_v1_summary.json"
SELECTION_PATH = REPO_ROOT / "artifacts" / "benchmark" / "pilot_selection_rung8_v1.json"


# --- table patterns --------------------------------------------------------------------------------------


def table_patterns(seeds_v3: list[dict], family: str, setting: dict | None = None) -> dict[str, dict]:
    """{state: v3 seed} --- the eligible single-state patterns of `family` at the rung-8 table setting."""
    st = setting or TABLE_SETTING[family]
    out = {}
    for s in seeds_v3:
        p = s["pattern"]
        if (p["family"] == family and p["pattern_kind"] == "single" and p["geography_type"] == "state"
                and p["metric"] == st["metric"] and p["statistic"] == st["statistic"] and p["horizon"] == st["horizon"]
                and p["status"] == "computed" and not p["acceptance_blocked"]):
            if p["geography"] in out:
                raise ValueError(f"two patterns for {family} at {p['geography']} under {st}")
            out[p["geography"]] = s
    return out


def table_change(seed: dict) -> float | None:
    v = (seed["pattern"].get("computed_value_or_range") or {}).get("value")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# --- groups ----------------------------------------------------------------------------------------------


class Context:
    """The ingested infra statements with their geography (litgeo v2) and canonical papers (D-046)."""

    def __init__(self, records: list[dict], indep: dict, gz: lg.Gazetteer):
        self.by_id = {r["statement_id"]: r for r in records}
        self.canon = li.canonical_map(indep)
        self.geo = {r["statement_id"]: lg.classify(r["proposal"].get("region"), r["proposal"].get("region_scope"), gz) for r in records}

    def tier(self, sid: str, state: str) -> str:
        g = self.geo[sid]
        if g["class"] == "state" and state in g["states"]:
            return "place_named"
        if g["class"] in US_CLASSES or (g["class"] == "state"):
            return "us"
        return "general"


def impact_group_view(g: dict, ctx: Context) -> dict | None:
    """An impact group's members and facts, or None when it is not a usable impact group (module docstring)."""
    if g.get("statement_type") != "impact" or g.get("claim_about") != IMPACT_CLAIM or g.get("disposition_exclude"):
        return None
    ms = [ctx.by_id[s] for s in g["member_ids"] if s in ctx.by_id and ctx.by_id[s]["precheck_status"] == "pass"]
    if not ms:
        return None
    fams = {m["statement_family"] for m in ms}
    if len(fams) != 1:
        raise ValueError(f"{g['group_id']}: members of more than one family {sorted(map(str, fams))}")
    cc = [m for m in ms if m["evidence_role"] in la.CORE_OR_CITED]
    strength = li.strength_v2([{"evidence_role": m["evidence_role"], "paper_item_id": m["paper_item_id"],
                                "passage_type": m["proposal"].get("passage_type")} for m in ms], ctx.canon)
    if strength == "background_only":
        return None
    return {"group_id": g["group_id"], "family": fams.pop(), "members": [m["statement_id"] for m in ms],
            "cited_members": [m["statement_id"] for m in cc],
            "asset_classes": dict(sorted(Counter(m["proposal"].get("asset_class") or "" for m in ms).items())),
            "hazard_relation": "broader_hazard" if any(m.get("hazard_relation") == "broader_hazard" for m in ms) else "governed_term",
            "evidence_strength": strength, "n_papers": li.n_independent([m["paper_item_id"] for m in cc], ctx.canon),
            "label": g.get("label")}


def group_tier(v: dict, state: str, ctx: Context) -> str:
    tiers = [ctx.tier(s, state) for s in v["cited_members"]]
    return min(tiers, key=GEO_TIERS.index) if tiers else "general"


def impact_rank_key(x: dict) -> tuple:
    return (GEO_TIERS.index(x["relevance"]), STRENGTH_ORDER[x["evidence_strength"]], -x["n_papers"], x["group_id"])


# --- seeds -----------------------------------------------------------------------------------------------


def build_seeds(seeds_v3: list[dict], groups: list[dict], ctx: Context, rung3_driver_ids=None,
                setting: dict | None = None) -> list[dict]:
    """DR-SEED-INFRA-1 seeds, ranked. `rung3_driver_ids(v3_seed) -> [group_id]` (None: recorded as not attached)."""
    views = [v for v in (impact_group_view(g, ctx) for g in groups) if v]
    out = []
    for fam in TABLE_SETTING:
        pats = table_patterns(seeds_v3, fam, (setting or {}).get(fam))
        fam_views = [v for v in views if v["family"] == fam]
        classes = sorted({c for v in fam_views for c in v["asset_classes"] if c})
        for state, s3 in sorted(pats.items()):
            drivers = rung3_driver_ids(s3) if rung3_driver_ids else None
            for a in classes:
                ig = [dict(v, relevance=group_tier(v, state, ctx), n_members_in_class=v["asset_classes"].get(a, 0))
                      for v in fam_views if a in v["asset_classes"]]
                if not ig:
                    continue
                ig.sort(key=impact_rank_key)
                p = s3["pattern"]
                out.append({"seed_id": f"SD8-{p['pattern_id']}-{a}", "rule": RULE_ID, "version": VERSION, "decision": DECISION,
                            "rung": RUNG, "family": fam, "place": state, "asset_class": a, "pattern_id": p["pattern_id"],
                            "rung3_seed_id": s3["seed_id"], "table_change": table_change(s3),
                            "table_setting": dict((setting or {}).get(fam) or TABLE_SETTING[fam]),
                            "working_assumptions": [w["id"] for w in s3.get("working_assumptions") or []],
                            "impact_groups": ig, "place_named_impact_group_ids": [x["group_id"] for x in ig if x["relevance"] == "place_named"],
                            "best_relevance": ig[0]["relevance"],
                            "needs_general_clause": not any(x["relevance"] == "place_named" for x in ig),
                            "driver_group_ids": drivers,
                            "driver_groups_rule": "as in rung 3: synthpackets.packet_groups(3, ...), role driver (LITCORPUS-02 grouping run 2, dispositions)",
                            "best_strength": min((x["evidence_strength"] for x in ig), key=STRENGTH_ORDER.get),
                            "n_papers_impact": li.n_independent([ctx.by_id[s]["paper_item_id"] for x in ig for s in x["cited_members"]], ctx.canon)})
    out.sort(key=lambda s: (STRENGTH_ORDER[s["best_strength"]], -s["n_papers_impact"], s["pattern_id"], s["asset_class"]))
    for k, s in enumerate(out, 1):
        s["seed_rank"] = k
    return out


# --- pilot selection -------------------------------------------------------------------------------------


def place_named_states(records: list[dict], ctx: Context, family: str, asset_class: str) -> list[str]:
    """States named (litgeo v2 class state) by a passing impact statement of `family` and `asset_class`."""
    out = set()
    for r in records:
        if r.get("impact_candidate") and r["statement_family"] == family and r["proposal"].get("asset_class") == asset_class:
            g = ctx.geo[r["statement_id"]]
            if g["class"] == "state":
                out.update(g["states"])
    return sorted(out)


def load_question_forms_v2(path=QUESTION_FORMS_V2_PATH) -> dict:
    import re

    d = yaml.safe_load(path.read_text(encoding="utf-8"))
    ids = [f["id"] for f in d["forms"]]
    if d["version"] != "question_forms_v2" or len(ids) != 10 or len(set(ids)) != 10:
        raise ValueError("question_forms_v2 must hold ten distinct forms")
    for f in d["forms"]:
        re.compile(f["opening_regex"])
    return {**d, "sha256": sha256_file(path)}


def rung8_forms(forms: dict) -> list[dict]:
    return [f for f in forms["forms"] if RUNG in f["rungs"]]


def select_pilot(seeds: list[dict], seeds_v3: list[dict], records: list[dict], ctx: Context, forms: dict,
                 setting: dict | None = None) -> dict:
    """The eight-cell rung-8 pilot selection (module docstring)."""
    by = {(s["family"], s["place"], s["asset_class"]): s for s in seeds}
    f8 = rung8_forms(forms)
    picked, missing = [], []
    for fam, a in PILOT_CELLS:
        pats = table_patterns(seeds_v3, fam, (setting or {}).get(fam))
        named = [st for st in place_named_states(records, ctx, fam, a) if st in pats and table_change(pats[st]) is not None]
        if named:
            state = max(named, key=lambda st: (table_change(pats[st]), st))
            basis = "largest table change among states with a place-named impact statement"
        else:
            state, basis = FALLBACK_STATE, "fallback: no state with a place-named impact statement of this class"
        s = by.get((fam, state, a))
        cell = {"family": fam, "asset_class": a, "state": state, "state_basis": basis, "candidate_states": named,
                "table_change": table_change(pats[state]) if state in pats else None}
        if s is None:
            missing.append({**cell, "reason": "no seed (no usable impact group of this family and class)"})
            continue
        form = f8[len(picked) % len(f8)]
        picked.append({**cell, "order": len(picked) + 1, "seed_id": s["seed_id"], "pattern_id": s["pattern_id"],
                       "question_form_id": form["id"], "impact_group_ids": [x["group_id"] for x in s["impact_groups"]],
                       "place_named_impact_group_ids": s["place_named_impact_group_ids"], "needs_general_clause": s["needs_general_clause"]})
    return {"version": "pilot_selection_rung8 v1", "rule": "D-075 rung-8 pilot selection", "rung": RUNG,
            "table_setting": setting or TABLE_SETTING, "cells": [list(c) for c in PILOT_CELLS], "selected": picked,
            "missing": missing, "question_forms": {"version": forms["version"], "sha256": forms["sha256"], "rung8": [f["id"] for f in f8]}}


# --- driver groups as in rung 3 ---------------------------------------------------------------------------


def rung3_driver_ids_factory():
    """seed_v3 -> [group_id] of the driver groups a rung-3 packet (v4b inputs: LITCORPUS-02 grouping run 2, dispositions v1a
    + fire v1, corrections v1a, geography v2) attaches to the seed's pattern. Loads the pinned inputs once."""
    import json

    from climrr import itemseeds as sd
    from climrr import itemseeds_v2 as s2
    from climrr import litgroups as lgr
    from climrr import litstatements as ls
    from climrr import litstatements_run2 as r2
    from climrr import p2b_mentor_v3 as m3
    from climrr import synthpackets as spk
    from climrr import synthpackets_v4 as v4

    records = sd.read_jsonl(r2.INGESTED_PATH)
    corrections, overrides = m3.corrections_v1a()
    statements = {r["statement_id"]: r for r in ls.load_statements(m3.mx.STATEMENTS_INGESTED_PATH)}
    reslices = m3.reslices_v1a(corrections, statements)
    corrected = ls.apply_provenance_corrections(records, corrections, reslices, correction_file=ls.CORRECTIONS_V1A_PATH.name)
    indep = json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    nca = sd.nca_map()
    by_statement = spk.statement_lookup(corrected, indep)
    rows = s2.statement_table(records, sd.read_jsonl(li.CLUSTERS_V1B_PATH), indep, lg.Gazetteer(nca))
    groups = ls.apply_group_label_overrides(lgr.apply_dispositions(lgr.read_groups(v4.GROUPS_PATH), v4.load_dispositions_v4a()), overrides)

    def ids(seed: dict) -> list[str]:
        basis = spk.relevant_basis(seed["pattern"], rows, nca)
        geo = {r["statement_id"]: r["geo"] for r in rows}
        pg, _ = spk.packet_groups(3, groups, by_statement, basis, geo)
        return [g["group_id"] for g in pg if g["role"] == "driver"]

    return ids
