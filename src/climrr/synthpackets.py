"""Seed packets for the item-synthesis agent (pilot P2b; D-041, D-048, D-047a, D-049, D-050, D-053--D-055, D-053a, D-055a,
D-054a; DR-SEED-RANK-3, DR-SEED-RANK-3a).

One packet per seed of the pilot selection (`data/metadata/benchmark/pilot_selection_v1.yaml`, D-050), at the
rung the selection names, built deterministically from the seed's pattern (`item_seeds_v2.jsonl`) and the
grouping agent's `groups.jsonl` (v2, every record with a `claim_about`, D-049). A packet has three parts:

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
  compare against: pattern ids, group ids and strengths, allowed numbers, allowed descriptors, exact values,
  forbidden strings, and (v3a, D-055a) `group_texts` --- per attached group its label and member statements, which a
  number in a sentence or rubric point citing that group may be traced to.

**Descriptors** (v3, DR-DESC-1, D-055): every pattern in `model_view` carries `allowed_descriptors`
(`pattern_descriptors.descriptors`): the pattern-level words the graded text may use. Their phrases go into
`checks_input.allowed_descriptors`, and the digits they hold into the allowed numbers. `checks_input.exact_values`
lists the decimal forms of the pattern values, which belong to provenance only.

**Rounding** (EXECUTOR): a value is shown to one decimal place (half up); the allowed
numbers are that form, the nearest integer, and the exact stored string, without sign.

**Relevance** (v2): a statement is relevant to the seed's pattern under the D-047a geography
(`litgeo` v2, with `us_subregion`), the DR-SEED-1 family and direction pairing unchanged
(`relevant_basis`). It is recomputed here from the pattern, not read from the seed file, whose
relevance is the D-047 (v1) geography as frozen.

**Groups in a packet** (DR-SEED-RANK-2, COORDINATOR 2026-11-01; v3: DR-SEED-RANK-3 and the D-053 dispositions,
2026-11-02; EXECUTOR details recorded for confirmation): a group is a candidate when >= 1 member is relevant, its type is mechanism /
driver / consensus / caveat (schema v2 has no `pattern` literature type), and its strength over
the **relevant** members is not `background_only` (schema v2 has no such strength). Only relevant
members are carried; `strength_in_packet` is recomputed over them (D-045 definitions, D-046
independence) beside the run's group strength. A candidate's role, by its `claim_about` (D-049):

- a mechanism / driver / consensus group: `hazard_change_mechanism` -> **driver** (at most 10);
  `hazard_definition_or_measurement` -> **context** (at most 4); `impact_or_exposure`,
  `method_or_data`, `other` (or a value outside the enum) -> excluded;
- a caveat group: **caveat** at rung 7 only (at most 4), and only with `claim_about` in
  {hazard_change_mechanism, hazard_definition_or_measurement} (v3, D-054) and no `exclude_from_rung7`
  disposition; excluded at other rungs.

**Rung 7, scenario caveats** (v3b, DR-SEED-RANK-3a, D-054a): the caveat slots are filled **first** by groups of any
statement type --- `pattern` included --- whose carried (relevant) member statements name an emissions scenario
(`SCENARIO_CAVEAT_RE`, the ruling's pattern as written), with `claim_about` in the two caveat claims, ranked by the v3
order; then by caveat-type groups as before. Such a group takes a caveat slot instead of a driver or context slot
(`scenario_slot: true`), and, since schema v2's literature `statement_type` has no `pattern` value, it is carried with
`statement_type: caveat` and its run type in `statement_type_run` (EXECUTOR reading, for confirmation). An
`exclude_from_rung7` disposition still keeps a group out of every caveat slot. A rung-7 packet's `model_view` carries the
`rung_instruction` (scenario dependence and caveats; RCP8.5 as one high-emissions scenario, contrasted with a moderate
scenario where the groups support it): a packet field, so the agent and its system prompt are unchanged. v3b changes
rung-7 packets only: a packet at another rung is built exactly as in v3a and keeps the v3a stamp and rank rule.

Dispositions (D-053, `litgroups.apply_dispositions`, applied before the packets): a `not_about_family` or
`reject` group, or one merged into another, is excluded; a relabel changes the claim type the role is read from.
v3a (D-053a): a group or singleton with no disposition (`disposition` None) that would otherwise be attached --- it
has a role and is within its role's cap after the undisposed ones above it are skipped --- is excluded as
`no_disposition`, and the next disposed candidate takes its place; `scripts/build_synth_packets.py` lists these in
the manifest as `undisposed_candidates` for the next review round.

Order within a role (DR-SEED-RANK-3, D-054): (1) place-named --- a relevant member names the seed's state or NCA
region (basis `state` / `nca_region`) --- first; (2) `strength_in_packet` (multi > review > single); (3) best
relevance basis among the relevant members (us_subregion > us_national > global); (4) more canonical papers among
the relevant members; (5) group id. Every excluded candidate is listed with its reason in the packet's
`excluded_groups` (disposition, merge, claim type, caveat outside rung 7, caveat claim type, no disposition, or over the
cap). A
level-1 packet (pattern only) carries no group and lists none.

No model call; no table value computed here (values are copied from the pattern).
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal

from climrr import benchmark_items as bi
from climrr import itemseeds as sd
from climrr import litaggregate as la
from climrr import litgeo as lg
from climrr import litindependence as li
from climrr import pattern_descriptors as pd
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

VERSION = "synthpackets v3b"
RANK_RULE = "DR-SEED-RANK-3"
#: v3b (D-054a) changes rung-7 packets only; a packet at any other rung keeps the version and rank rule it was built with.
LEVEL_VERSION = {7: (VERSION, "DR-SEED-RANK-3a")}
UNCHANGED_VERSION = "synthpackets v3a"
SCENARIO_CAVEAT_RE = re.compile(r"RCP|SSP|emissions scenario|high-emissions|moderate")  # D-054a, as written
RUNG_INSTRUCTION = {
    7: ("Rung 7: the prompt must ask how the projected change depends on the emissions scenario and what uncertainties or "
        "caveats apply. The reference answer must state that RCP8.5 is one high-emissions scenario and, where the caveat "
        "groups support it, contrast it with the moderate scenario they name; state no scenario contrast the groups do not "
        "support."),
}
PACKETS_DIR = REPO_ROOT / "artifacts" / "benchmark" / "synth_packets"
MAX_PASSAGE = 400
MAX_DRIVER_GROUPS, MAX_CONTEXT_GROUPS, MAX_CAVEAT_GROUPS = 10, 4, 4
DRIVER_CLAIM, CONTEXT_CLAIM = "hazard_change_mechanism", "hazard_definition_or_measurement"
CAVEAT_LEVELS = (7,)
CAVEAT_CLAIMS = (DRIVER_CLAIM, CONTEXT_CLAIM)
PLACE_NAMED = ("state", "nca_region")
BASIS_RANK = {b: i for i, b in enumerate(lg.BASIS_ORDER)}
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


def relevant_basis(p: dict, rows: list[dict], nca: dict) -> dict:
    """{statement_id: basis} of the entering statements relevant to pattern `p`: the arm of its family, a direction
    equal to the pattern's or `unspecified` (DR-SEED-1), and `litgeo.relevance` over each row's `geo` (rows as
    `itemseeds_v2.statement_table` builds them, with the v2 gazetteer)."""
    places = sd.pattern_places(p, nca)
    out = {}
    for r in rows:
        if r["arm"] != sd.FAMILY_ARM[p["family"]] or r["direction"] not in (p["direction"], "unspecified"):
            continue
        b = lg.relevance(r["geo"], places)
        if b:
            out[r["statement_id"]] = b
    return out


def rank_key(x: dict) -> tuple:
    """DR-SEED-RANK-3: place-named first, strength, relevance basis, more papers, group id."""
    return (x["best_basis"] not in PLACE_NAMED, sd.STRENGTH_ORDER[x["strength_in_packet"]], x["best_basis_rank"], -x["n_papers"],
            x["group_id"])


def packet_groups(level: int, groups: list[dict], by_statement: dict, seed_basis: dict, geo: dict | None = None
                  ) -> tuple[list[dict], list[dict]]:
    """(the groups a packet at `level` carries, ranked and capped; the excluded candidates with reasons) --- module docstring.
    `geo`: {statement_id: litgeo classification}, for the members' region class and qualifier."""
    if level == 1:
        return [], []
    geo = geo or {}
    picked = []
    for g in groups:
        if g["statement_type"] not in PACKET_TYPES and level not in CAVEAT_LEVELS:
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
                            "scenario": r["scenario"]["value"], "basis": seed_basis[sid],
                            "region_class": (geo.get(sid) or {}).get("class"), "region_qualifier": (geo.get(sid) or {}).get("qualifier")})
        st = _strength(members)
        if st not in SCHEMA_STRENGTHS:
            continue
        scen = g["statement_type"] == "caveat" and any(m["scenario"] not in la.UNNAMED and m["scenario"] for m in members)
        claim = g.get("claim_about")
        names_emissions = level in CAVEAT_LEVELS and any(SCENARIO_CAVEAT_RE.search(m["statement"] or "") for m in members)
        if g["statement_type"] not in PACKET_TYPES and not names_emissions:
            continue
        scenario_slot = names_emissions and claim in CAVEAT_CLAIMS and not g.get("exclude_from_rung7") \
            and not g.get("disposition_exclude")
        if g.get("disposition_exclude"):
            role, why = None, g["disposition_exclude"]
        elif scenario_slot:
            role, why = "caveat", None
        elif g["statement_type"] not in PACKET_TYPES:
            role, why = None, ("disposition:exclude_from_rung7" if g.get("exclude_from_rung7")
                               else f"scenario_caveat_claim_about:{claim}")
        elif g["statement_type"] == "caveat":
            if level not in CAVEAT_LEVELS:
                role, why = None, "caveat_outside_rung_7"
            elif g.get("exclude_from_rung7"):
                role, why = None, "disposition:exclude_from_rung7"
            elif claim not in CAVEAT_CLAIMS:
                role, why = None, f"caveat_claim_about:{claim}"
            else:
                role, why = "caveat", None
        else:
            role = {DRIVER_CLAIM: "driver", CONTEXT_CLAIM: "context"}.get(claim)
            why = None if role else f"claim_about:{claim}"
        picked.append({"group_id": g["group_id"], "kind": g["kind"],
                       "statement_type": "caveat" if scenario_slot else g["statement_type"], "claim_about": claim,
                       **({"statement_type_run": g["statement_type"], "scenario_slot": True} if scenario_slot else {}),
                       "role": role, "excluded_reason": why, "label": g["label"] if g["kind"] == "group" else None,
                       "claim_about_source": g.get("claim_about_source", "agent"), "disposition": g.get("disposition"),
                       **({"merged_from": g["merged_from"]} if g.get("merged_from") else {}),
                       "group_strength_run": g["evidence_strength"], "strength_in_packet": st, "n_members_run": g["n_members"],
                       "names_scenario": scen, "n_specific": sum(m["basis"] in ("state", "nca_region") for m in members),
                       "best_basis": min((m["basis"] for m in members), key=BASIS_RANK.get),
                       "best_basis_rank": min(BASIS_RANK[m["basis"]] for m in members),
                       "n_papers": len({m["canonical_paper"] for m in members}), "members": members})
    excluded = [{"group_id": x["group_id"], "statement_type": x["statement_type"], "claim_about": x["claim_about"],
                 "reason": x["excluded_reason"]}
                for x in sorted(picked, key=lambda x: x["group_id"]) if x["role"] is None]
    out = []
    for role, cap in (("driver", MAX_DRIVER_GROUPS), ("context", MAX_CONTEXT_GROUPS), ("caveat", MAX_CAVEAT_GROUPS)):
        kept = []
        key = (lambda x: (not x.get("scenario_slot"), *rank_key(x))) if role == "caveat" else rank_key   # D-054a: scenario first
        for x in sorted((x for x in picked if x["role"] == role), key=key):
            if len(kept) < cap and x["disposition"] is not None:
                kept.append(x)
                continue
            why = f"over_cap:{role}" if len(kept) >= cap else "no_disposition"                  # D-053a
            excluded.append({"group_id": x["group_id"], "statement_type": x["statement_type"], "claim_about": x["claim_about"],
                             "reason": why})
        out += kept
    return out, excluded


def _model_group(g: dict) -> dict:
    return {"group_id": g["group_id"], "role": g["role"], "statement_type": g["statement_type"], "claim_about": g["claim_about"],
            "label": g["label"] or g["members"][0]["statement"], "evidence_strength": g["strength_in_packet"],
            "independent_papers": len({m["canonical_paper"] for m in g["members"] if m["evidence_role"] in la.CORE_OR_CITED}),
            "members": [{"statement": m["statement"], "passage": (m["verbatim_passage"] or "")[:MAX_PASSAGE],
                         "passage_truncated": len(m["verbatim_passage"] or "") > MAX_PASSAGE, "paper_id": m["paper_item_id"],
                         "region": m["region"], **({"region_qualifier": m["region_qualifier"]} if m.get("region_qualifier") else {})}
                        for m in g["members"]]}


# --- packet -----------------------------------------------------------------------------------


def build_packet(seed: dict, level: int, item_id: str, groups: list[dict], by_statement: dict, rows: list[dict], nca: dict,
                 inputs_sha256: dict, selection: dict | None = None, rules: dict | None = None) -> dict:
    """`level`: the rung the item is built at (the selection's). `rows`: `itemseeds_v2.statement_table` with the v2 gazetteer."""
    basis = relevant_basis(seed["pattern"], rows, nca)
    geo = {r["statement_id"]: r["geo"] for r in rows}
    pg, excluded = packet_groups(level, groups, by_statement, basis, geo)
    pk = assemble_packet(seed["seed_id"], seed["pattern"], level, item_id, pg, nca, inputs_sha256, excluded, rules)
    pk["relevance"] = {"geography": lg.VERSION, "n_relevant_statements": len(basis),
                       "by_basis": {b: sum(x == b for x in basis.values()) for b in lg.BASIS_ORDER},
                       "n_relevant_statements_seed_file_v1": len(seed["relevant_statement_ids"])}
    if selection is not None:
        pk["selection"] = selection
    return pk


def exact_values(p: dict) -> list[str]:
    """The decimal forms (stored and one-decimal) of the pattern's values: provenance only (D-055)."""
    v = p["computed_value_or_range"]
    vals = [v.get("value"), v.get("mean_from"), v.get("mean_to"), (v.get("range") or {}).get("min"), (v.get("range") or {}).get("max")]
    vals += [r.get("value") for r in v.get("regions_ordered") or []]
    return sorted({f for x in vals if x is not None for f in number_forms(x) if "." in f})


def assemble_packet(seed_id: str, p: dict, lvl: int, item_id: str, pg: list[dict], nca: dict, inputs_sha256: dict,
                    excluded: list[dict] | None = None, rules: dict | None = None) -> dict:
    """The packet for one pattern and its chosen groups (`packet_groups` records). `rules`: DR-DESC-1 (default: the
    pinned `descriptor_rules_v1.yaml`)."""
    rules = rules or pd.load_rules()
    text, shown, allowed = render_pattern(p, nca)
    descr = pd.descriptors(p, rules)
    phrases = pd.phrases(descr)
    allowed |= {n for ph in phrases for n in bi.reference_numbers(ph)}          # scenario names are not numbers
    name, modality, desc = LEVEL_TEXT[lvl]
    cols = sorted({c["column"] for c in p["provenance"]["columns"]})
    paper_ids = sorted({m["paper_item_id"] for g in pg for m in g["members"]})
    version, rank_rule = LEVEL_VERSION.get(lvl, (UNCHANGED_VERSION, RANK_RULE))
    return {
        "packet_id": f"PK-{seed_id}", "version": version, "rank_rule": rank_rule, "descriptor_rule": rules["rule"],
        "descriptor_rules_sha256": rules["sha256"], "item_id": item_id, "seed_id": seed_id,
        "use_case_level": lvl,
        "model_view": {
            "use_case_level": lvl, "rung": f"{lvl}. {name}: {desc}",
            **({"rung_instruction": RUNG_INSTRUCTION[lvl]} if lvl in RUNG_INSTRUCTION else {}), "reasoning_modalities": modality,
            "patterns": [{"pattern_id": p["pattern_id"], "text": text, "values_shown": shown, "allowed_descriptors": descr}],
            "groups": [_model_group(g) for g in pg],
            "allowed_numbers": sorted(allowed, key=lambda s: (len(s), s)),
            "guardrails": list(GUARDRAILS), "item_fields": list(ITEM_FIELDS),
        },
        "provenance": {"patterns": [p], "groups": pg, "item_frame": {"use_case_level": lvl, "reasoning_modalities": modality,
                                                                      "level_name": name}},
        "checks_input": {"pattern_ids": [p["pattern_id"]],
                         "group_strength": {g["group_id"]: g["strength_in_packet"] for g in pg},
                         "allowed_numbers": sorted(allowed), "allowed_descriptors": phrases, "exact_values": exact_values(p),
                         "forbidden_strings": cols + paper_ids,
                         "group_texts": {g["group_id"]: ([g["label"]] if g["label"] else []) + [m["statement"] for m in g["members"]]
                                         for g in pg},
                         "level": lvl},
        "excluded_groups": list(excluded or []),
        "inputs_sha256": inputs_sha256,
    }


def statement_lookup(records: list[dict], indep: dict) -> dict:
    canon = li.canonical_map(indep)
    return {r["statement_id"]: dict(r, canonical_paper=canon.get(r["paper_item_id"], r["paper_item_id"]))
            for r in la.entering(records)}


def inputs_hashes(seeds_path, groups_path, selection_path=None) -> dict:
    out = {"item_seeds_v2": sha256_file(seeds_path), "groups": sha256_file(groups_path),
           "statements_ingested": sha256_file(la.r2.INGESTED_PATH), "independence_v2": sha256_file(li.INDEPENDENCE_PATH),
           "clusters_v1b": sha256_file(li.CLUSTERS_V1B_PATH), "exclusions": sha256_file(lg.EXCLUSIONS_PATH)}
    if selection_path is not None:
        out["pilot_selection"] = sha256_file(selection_path)
    return out
