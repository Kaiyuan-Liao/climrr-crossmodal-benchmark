"""Seed packets for the item-synthesis agent (pilot P2b-prep; D-041, D-048).

One packet per selected seed (`item_seeds_v2.jsonl`), built deterministically with the
grouping agent's `groups.jsonl`. A packet has three parts:

- `model_view` --- the **only** part `litsynth_agent.py` sends to the model: the table
  pattern rendered in plain words with its computed values (rounded as stated below),
  geography, season, horizon, scenario (RCP8.5 named, with the guardrail text), statistic,
  robustness and relative tercile; the relevant literature groups (label, evidence
  strength, each member statement verbatim with its passage cut to 400 characters and its
  paper id); the item schema v2 field list; the guardrails; the D-038 rung; the numbers
  the reference answer may use. No column name, no derivation rule id, no table hash.
- `provenance` --- what the agent needs to assemble a schema-v2 item and the model never
  sees: the full pattern records, and per group member its paper SHA-256, json path, span
  and the full verbatim passage.
- `checks_input` --- what the deterministic post-checks (`benchmark_items.synthesis_post_checks`)
  compare against: pattern ids, group ids and strengths, allowed numbers, forbidden strings.

**Rounding** (EXECUTOR): a value is shown to one decimal place (half up); the allowed
numbers are that form, the nearest integer, and the exact stored string, without sign.

**Groups in a packet** (EXECUTOR, recorded for COORDINATOR confirmation): a group enters
when >= 1 member is geography-relevant to the seed's pattern (D-047), its type is
mechanism / driver / consensus / caveat (schema v2 has no `pattern` literature type), and its
strength over the **relevant** members is not `background_only` (schema v2 has no such
strength). Only relevant members are carried; `strength_in_packet` is recomputed over them
(D-045 definitions, D-046 independence) beside the run's group strength. Ranked by strength,
then members matched by state / NCA region name, then size, then group id; at most 10
mechanism / driver / consensus groups and 4 caveat groups (scenario-naming caveats first).
A level-1 packet (pattern only) carries no group.

No model call; no table value computed here (values are copied from the pattern).
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal

from climrr import itemseeds as sd
from climrr import litaggregate as la
from climrr import litgeo as lg
from climrr import litindependence as li
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

VERSION = "synthpackets v1"
PACKETS_DIR = REPO_ROOT / "artifacts" / "benchmark" / "synth_packets"
MAX_PASSAGE = 400
MAX_EXPLAIN_GROUPS, MAX_CAVEAT_GROUPS = 10, 4
PACKET_TYPES = ("mechanism", "driver", "consensus", "caveat")
SCHEMA_STRENGTHS = ("multi_source_supported", "review_supported", "single_source_supported")
HORIZON_WORDS = {"mid": "mid-century", "end": "end of the century"}
LEVEL_TEXT = {
    1: ("Hazard pattern identification", "Hazard",
        "Identify a projected hazard pattern (direction, rough size, ranking) for a place, season, horizon and scenario."),
    3: ("Pattern + mechanism", "Hazard + Text",
        "State the projected pattern and explain the physical mechanisms or drivers behind it."),
    4: ("Regional comparison", "Hazard + Text",
        "Compare or rank regions by a projected hazard change and explain the contrast."),
    7: ("Scenario and uncertainty", "Hazard + Text",
        "State the projected pattern and what the scenario and the evidence do and do not support."),
}
GUARDRAILS = (
    "A modeled historical baseline is model output for a past period, not an observation.",
    "A Fire Weather Index is a meteorological fire-danger index; it is never fire occurrence, ignition, burned area or damage.",
    "RCP8.5 is one high-emissions scenario, not a forecast and not the only plausible future.",
    "Hazard is not exposure, and exposure is not risk.",
)
SCENARIO_NOTE = {"RCP8.5": "RCP8.5 (one high-emissions scenario; not a forecast and not the only plausible future)"}
ITEM_FIELDS = ("prompt", "reference_answer.table_pattern", "reference_answer.literature_interpretation",
               "reference_answer.integrated", "rubric.required_points", "rubric.acceptable_variants", "rubric.optional_points",
               "rubric.disallowed_claims", "rubric.fatal_errors", "guardrails", "source_independent_answerability",
               "source_independence_note", "capability_tested", "system_task", "key_relationships", "evidence_needed",
               "desired_output_characteristics", "expected_knowledge_level")
_THRESHOLD = re.compile(r"above (\d+) F\b")
_TERCILE_N = re.compile(r"among the (\d+) U\.S\. State labels")
TERCILE_WORDS = {"small": "lower tercile", "moderate": "middle tercile", "large": "upper tercile"}
UNIT_WORDS = {"cell": "grid cell", "state": "state", "nca_region": "NCA5 region"}
UNRANKED_WORDS = {"zero_baseline": "no percent change: its modeled historical baseline mean is zero"}


# --- numbers --------------------------------------------------------------------------------


def _q(v: str, places: str) -> str:
    return str(Decimal(v).quantize(Decimal(places), rounding=ROUND_HALF_UP))


def show(v) -> str:
    """One decimal place, half up, with its sign for a change."""
    return _q(str(v), "0.1")


def number_forms(v) -> set[str]:
    if v is None:
        return set()
    s = str(v).lstrip("+-")
    out = {s}
    try:
        out |= {_q(s, "0.1"), _q(s, "1")}
    except ArithmeticError:
        pass
    return {x.lstrip("-") for x in out}


# --- pattern rendering ------------------------------------------------------------------------


def threshold(p: dict) -> str | None:
    m = _THRESHOLD.search(p.get("metric_wording") or "")
    return m.group(1) if m else None


def quantity(p: dict) -> str:
    w = p.get("metric_wording") or p["metric"]
    w = re.sub(r"\babove (\d+) F\b", r"above \1 °F", w)
    return w.replace("daily max ", "daily maximum ")


def place_words(p: dict, nca: dict) -> str:
    gt, geo = p["geography_type"], p["geography"]
    if p["pattern_kind"] == "regional_contrast":
        return "the NCA5 climate regions covered (" + ", ".join(r["name"] for r in p["computed_value_or_range"]["regions_ordered"]) + ")"
    if gt == "state":
        rid = nca["state_region"].get(geo)
        return f"the U.S. state of {geo}" + (f" (NCA5 region: {nca['region_name'][rid]})" if rid else "")
    if gt == "nca_region":
        covered = ", ".join(p.get("region_member_states_covered") or [])
        return f"the NCA5 {nca['region_name'][geo]} region" + (f" (states covered: {covered})" if covered else "")
    return "one control grid cell"


def statistic_words(p: dict) -> str:
    return {"direction": "direction of change of the mean",
            "absolute_change": "change of the mean (future minus modeled historical baseline)",
            "percent_change": "percent change of the mean (the mean change divided by the mean modeled historical baseline)",
            }.get(p["statistic"], p["statistic"])


def _unit_words(p: dict, over_cells: bool) -> str:
    v = p["computed_value_or_range"]
    if over_cells and p["statistic"] == "percent_change":
        return "days" if p["metric"].startswith("heatindex_days") else ""
    return {"percent": "%", None: ""}.get(v.get("unit"), v.get("unit") or "")


def render_pattern(p: dict, nca: dict) -> tuple[str, dict, set[str]]:
    """(plain-words text, the rounded values shown, allowed number strings)."""
    v = p["computed_value_or_range"]
    allowed: set[str] = set()
    shown: dict = {}
    lines = [f"Pattern {p['pattern_id']} ({'regional contrast' if p['pattern_kind'] == 'regional_contrast' else 'single place'}).",
             f"Place: {place_words(p, nca)}.", f"Quantity: {quantity(p)}.", f"Season: {p['season']}.",
             f"Horizon: {HORIZON_WORDS.get(p['horizon'], p['horizon'])} ({p['horizon_window']}), compared with the modeled historical baseline.",
             f"Scenario: {SCENARIO_NOTE.get(p['scenario'], p['scenario'])}.", f"Statistic: {statistic_words(p)}.",
             f"Direction: {p['direction']}."]
    t = threshold(p)
    if t:
        allowed.add(t)
    allowed |= set(re.findall(r"\d+", p["horizon_window"]))
    if p["pattern_kind"] == "regional_contrast":
        unit = _unit_words(p, False)
        order = [r for r in v["regions_ordered"] if r.get("value") is not None]
        unranked = [r for r in v["regions_ordered"] if r.get("value") is None]
        lines.append("Ranking, largest first: " + "; ".join(
            f"{r['rank']}. {r['name']} {'+' if Decimal(r['value']) > 0 else ''}{show(r['value'])}{(' ' + unit) if unit and unit != '%' else unit}"
            for r in order) + ".")
        if unranked:
            lines.append("Not ranked: " + "; ".join(f"{r['name']} ({UNRANKED_WORDS.get(r.get('reason'), r.get('reason'))})"
                                                     for r in unranked) + ".")
        shown["regions"] = [{"rank": r["rank"], "name": r["name"], "value": show(r["value"])} for r in order]
        shown["not_ranked"] = [r["name"] for r in unranked]
        for r in order:
            allowed |= number_forms(r["value"]) | {str(r["rank"])}
    else:
        unit = _unit_words(p, False)
        if v.get("value") is not None and p["statistic"] != "direction":
            sign = "+" if Decimal(v["value"]) > 0 else ""
            lines.append(f"Value: {sign}{show(v['value'])}{(' ' + unit) if unit and unit != '%' else unit}.")
            shown["value"] = show(v["value"])
            allowed |= number_forms(v["value"])
        if v.get("mean_from") is not None and v.get("mean_to") is not None:
            mu = p["computed_value_or_range"].get("unit") if p["statistic"] != "percent_change" else _unit_words(p, True)
            mu = "" if mu in (None, "percent") else mu
            lines.append(f"Mean: {show(v['mean_from'])} {mu} in the modeled historical baseline, {show(v['mean_to'])} {mu} at "
                         f"{HORIZON_WORDS.get(p['horizon'], p['horizon'])}.".replace("  ", " "))
            shown["mean_from"], shown["mean_to"] = show(v["mean_from"]), show(v["mean_to"])
            allowed |= number_forms(v["mean_from"]) | number_forms(v["mean_to"])
        rng = v.get("range") or {}
        if rng.get("min") is not None and rng.get("max") is not None:
            over_cells = rng.get("over") == "cells"
            ru = _unit_words(p, over_cells)
            what = "change per grid cell" if over_cells else "value across member states"
            if ru or not over_cells:
                lines.append(f"Range of the {what}: {show(rng['min'])} to {show(rng['max'])}{(' ' + ru) if ru and ru != '%' else ru}.")
                shown["range"] = [show(rng["min"]), show(rng["max"])]
                allowed |= number_forms(rng["min"]) | number_forms(rng["max"])
    rob = p.get("pattern_robustness")
    if rob:
        unit = UNIT_WORDS.get(p.get("robustness_unit"), p.get("robustness_unit") or "unit")
        share = p.get("robustness_share")
        if share:
            same, of = share.split("/")
            lines.append(f"Robustness: {same} of {of} {unit}s change in the same direction as the mean ({rob}).")
        else:
            lines.append(f"Robustness: {rob}, over {p['pattern_support_n']} {unit}s.")
            allowed.add(str(p["pattern_support_n"]))
        allowed |= set(re.findall(r"\d+", share or ""))
    rm = p.get("relative_magnitude")
    if rm:
        n = _TERCILE_N.search(rm["definition"])
        lines.append(f"Relative magnitude: {rm['class']} ({TERCILE_WORDS.get(rm['class'], rm['class'])}, by signed value, among "
                     f"{n.group(1) + ' ' if n else ''}U.S. states for this quantity, season, horizon, scenario and statistic; "
                     "a relative descriptor among states, not an absolute threshold).")
        shown["tercile"] = rm["class"]
        if n:
            allowed.add(n.group(1))
    return " ".join(lines), shown, allowed


# --- groups -----------------------------------------------------------------------------------


def _strength(members: list[dict]) -> str:
    return li.strength_v2([{"evidence_role": m["evidence_role"], "paper_item_id": m["canonical_paper"],
                            "passage_type": m["passage_type"]} for m in members], {})


def packet_groups(level: int, groups: list[dict], by_statement: dict, seed_basis: dict) -> list[dict]:
    """The groups a packet at `level` carries, ranked and capped (module docstring)."""
    if level == 1:
        return []
    picked = []
    for g in groups:
        if g["statement_type"] not in PACKET_TYPES:
            continue
        rel = [sid for sid in g["member_ids"] if sid in seed_basis]
        if not rel:
            continue
        members = []
        for sid in rel:
            r = by_statement[sid]
            ev = r["evidence"] or {}
            members.append({"statement_id": sid, "statement": r["proposal"]["statement"], "paper_item_id": r["paper_item_id"],
                            "canonical_paper": r["canonical_paper"], "paper_sha256": r["paper_sha256"],
                            "json_path": ev.get("json_path"), "span_start": ev.get("span_start"), "span_end": ev.get("span_end"),
                            "verbatim_passage": r["verbatim_passage"], "evidence_role": r["evidence_role"],
                            "passage_type": r["proposal"].get("passage_type"), "region": r["proposal"].get("region"),
                            "scenario": r["scenario"]["value"], "basis": seed_basis[sid]})
        st = _strength(members)
        if st not in SCHEMA_STRENGTHS:
            continue
        scen = g["statement_type"] == "caveat" and any(m["scenario"] not in la.UNNAMED and m["scenario"] for m in members)
        picked.append({"group_id": g["group_id"], "kind": g["kind"], "statement_type": g["statement_type"],
                       "label": g["label"] if g["kind"] == "group" else None, "group_strength_run": g["evidence_strength"],
                       "strength_in_packet": st, "n_members_run": g["n_members"], "names_scenario": scen,
                       "n_specific": sum(m["basis"] in ("state", "nca_region") for m in members), "members": members})
    key = lambda x: (sd.STRENGTH_ORDER[x["strength_in_packet"]], -x["n_specific"], -len(x["members"]), x["group_id"])  # noqa: E731
    expl = sorted((x for x in picked if x["statement_type"] != "caveat"), key=key)[:MAX_EXPLAIN_GROUPS]
    cav = sorted((x for x in picked if x["statement_type"] == "caveat"), key=lambda x: (not x["names_scenario"],) + key(x))
    return expl + cav[:MAX_CAVEAT_GROUPS]


def _model_group(g: dict) -> dict:
    return {"group_id": g["group_id"], "statement_type": g["statement_type"],
            "label": g["label"] or g["members"][0]["statement"], "evidence_strength": g["strength_in_packet"],
            "independent_papers": len({m["canonical_paper"] for m in g["members"] if m["evidence_role"] in la.CORE_OR_CITED}),
            "members": [{"statement": m["statement"], "passage": (m["verbatim_passage"] or "")[:MAX_PASSAGE],
                         "passage_truncated": len(m["verbatim_passage"] or "") > MAX_PASSAGE, "paper_id": m["paper_item_id"],
                         "region": m["region"]} for m in g["members"]]}


# --- packet -----------------------------------------------------------------------------------


def build_packet(seed: dict, level: int, item_id: str, groups: list[dict], by_statement: dict, rows_geo: dict, nca: dict,
                 inputs_sha256: dict) -> dict:
    """`level`: the rung the item is built at (the shortlist's, which may be below the seed's highest)."""
    places = sd.pattern_places(seed["pattern"], nca)
    seed_basis = {sid: lg.relevance(rows_geo[sid], places) for sid in seed["relevant_statement_ids"]}
    pg = packet_groups(level, groups, by_statement, seed_basis)
    return assemble_packet(seed["seed_id"], seed["pattern"], level, item_id, pg, nca, inputs_sha256)


def assemble_packet(seed_id: str, p: dict, lvl: int, item_id: str, pg: list[dict], nca: dict, inputs_sha256: dict) -> dict:
    """The packet for one pattern and its chosen groups (`packet_groups` records)."""
    text, shown, allowed = render_pattern(p, nca)
    name, modality, desc = LEVEL_TEXT[lvl]
    cols = sorted({c["column"] for c in p["provenance"]["columns"]})
    paper_ids = sorted({m["paper_item_id"] for g in pg for m in g["members"]})
    return {
        "packet_id": f"PK-{seed_id}", "version": VERSION, "item_id": item_id, "seed_id": seed_id,
        "use_case_level": lvl,
        "model_view": {
            "use_case_level": lvl, "rung": f"{lvl}. {name}: {desc}", "reasoning_modalities": modality,
            "patterns": [{"pattern_id": p["pattern_id"], "text": text, "values_shown": shown}],
            "groups": [_model_group(g) for g in pg],
            "allowed_numbers": sorted(allowed, key=lambda s: (len(s), s)),
            "guardrails": list(GUARDRAILS), "item_fields": list(ITEM_FIELDS),
        },
        "provenance": {"patterns": [p], "groups": pg, "item_frame": {"use_case_level": lvl, "reasoning_modalities": modality,
                                                                      "level_name": name}},
        "checks_input": {"pattern_ids": [p["pattern_id"]],
                         "group_strength": {g["group_id"]: g["strength_in_packet"] for g in pg},
                         "allowed_numbers": sorted(allowed), "forbidden_strings": cols + paper_ids,
                         "level": lvl},
        "inputs_sha256": inputs_sha256,
    }


def statement_lookup(records: list[dict], indep: dict) -> dict:
    canon = li.canonical_map(indep)
    return {r["statement_id"]: dict(r, canonical_paper=canon.get(r["paper_item_id"], r["paper_item_id"]))
            for r in la.entering(records)}


def inputs_hashes(seeds_path, groups_path) -> dict:
    return {"item_seeds_v2": sha256_file(seeds_path), "groups": sha256_file(groups_path),
            "statements_ingested": sha256_file(la.r2.INGESTED_PATH), "independence_v2": sha256_file(li.INDEPENDENCE_PATH)}
