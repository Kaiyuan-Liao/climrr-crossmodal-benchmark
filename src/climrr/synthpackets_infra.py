"""Rung-8 seed packets v1 for the infrastructure-impact pilot (work package P5c, part C; D-075 rules, D-076).

One packet per selected cell of `pilot_selection_infra_v1.yaml` (item ids `BI-P5-0001` ...), built from the cell's
DR-SEED-INFRA-1 seed (`item_seeds_infra_v1.jsonl`). **Provisional**: every packet carries
`review_state: impact_groups_unreviewed` until the COORDINATOR's dispositions of the impact groups are applied
(P5c-hotfix); the packets are then rebuilt.

**Base (the table pattern and the driver groups).** The rung-3 packet v4b of the seed's pattern
(`synthpackets_v4.build_packet(..., level=3, variant="v4b")` over the same pinned inputs as packets v4b / v5a: the v3 seed,
LITCORPUS-02 grouping run 2 with dispositions v1a + fire v1 and corrections v1a, DR-DESC-1 v4, plain language v1a,
geography v2). Its pattern text, descriptors, allowed numbers and checks are kept as built. Of its groups only the
`driver` groups are kept (DR-SEED-INFRA-1: "the family's driver groups as in rung 3"); their ids must equal the seed's
`driver_group_ids`; the rung-3 `context` groups go to `excluded_groups` (`rung8:context_not_attached`).

**Impact groups.** The seed's impact groups in its rank order (relevance place_named > us > general, strength,
independent papers, id), the first `MAX_IMPACT_GROUPS` (10 = the DR-SEED-RANK-3 driver cap; EXECUTOR, for confirmation)
attached with role `impact`, the rest excluded (`over_cap:impact`). Each carries its members (the passing infra
statements, with passage, paper, region, asset class), its `relevance` to the place, its `hazard_relation`
(`broader_hazard` when a member rests on a broader hazard term), its asset classes and the members' impact mechanisms and
outcomes, the D-062 hedge for its strength, and `review_state: impact_groups_unreviewed`.

**Scope (D-069a, every group).** The packets v5a rule (`synthpackets_v5.group_scope(rule="majority")`): the majority
geography class of the group's cited members (a tie -> `mixed`, "In general, research"), the optional ", including work on
<Place>". An impact member's relevance basis to the item's place is `litgeo.relevance` (state / nca_region / us_subregion /
us_national / global), else its region class (other / unknown); a member naming another U.S. state is therefore
`unknown` here (as a rung-3 member would be: not relevant to the place). `needs_general_clause` when no packet group is
state- or NCA-specific; the clause is the v5a one.

**Rung-8 fields.** `model_view`: `rung: 8`, `use_case_level: 8`, `rung_instruction` (the three-part answer, D-075),
`asset_class` and `asset_class_phrase`, `place_named_impact_group_ids`, `plain_language` v1b (`broader_hazard_phrase`),
`question_form` (QF-08 / QF-09 / QF-10 as the selection assigns, `question_forms_v2.yaml`), `must_not_use` (the v4b list +
the fire words + "will fail", "at risk"; in a fire-weather packet "wildfire" is left out and `wildfire_rule` states D-073b),
the rung-8 guardrails. `checks_input.rung8` is what post-checks v3.3 read (impact group ids, place-named ids, hazard
relation per group, asset-class phrase, broader-hazard phrase, quantity phrases).

No model call; no table value computed (values are the pattern's).
"""

from __future__ import annotations

import copy
import json
from collections import Counter

from climrr import itemseeds as sd
from climrr import litaggregate as la
from climrr import litgeo as lg
from climrr import plain_language as pl
from climrr import seeds_infra as si
from climrr import synthpackets as spk
from climrr import synthpackets_v4 as v4
from climrr import synthpackets_v5 as v5
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

VERSION = "synthpackets infra v1"
DECISION = "D-076"
RULES = "D-075 (DR-SEED-INFRA-1, rung-8 wording), D-073b, D-069a"
RUNG = 8
PACKETS_DIR = REPO_ROOT / "artifacts" / "benchmark" / "synth_packets_infra_v1"
MAX_IMPACT_GROUPS = spk.MAX_DRIVER_GROUPS
REVIEW_STATE = si.REVIEW_STATE_UNREVIEWED
LEVEL_TEXT_8 = ("Hazard impact on infrastructure", "Hazard + Text",
                "State the projected hazard change at a place and what research shows such conditions do to an asset class.")
#: Plain phrase per asset class for graded text (EXECUTOR wording, for confirmation); the CISA sector name stays alongside.
ASSET_CLASS_PHRASE = {"energy": "energy systems", "transportation_systems": "transportation systems",
                      "water_and_wastewater": "water and wastewater systems",
                      "healthcare_and_public_health": "healthcare and public health systems",
                      "emergency_services": "emergency services", "communications": "communications systems"}
FIRE_WORDS = ("wildfire", "fires", "burned area")
RUNG8_MUST_NOT_USE = ("will fail", "at risk")
WILDFIRE_RULE = ('D-073b: "wildfire" only inside the exact phrase "conditions that favour wildfire" (as in the broader-hazard '
                 'phrase); "wildfire" anywhere else, "fires" and "burned area" are never written.')
RUNG8_INSTRUCTION = (
    "Rung 8 (hazard impact on infrastructure). Write the answer in three parts: (1) the hazard change at the place, as "
    "projected, in the table-pattern sentence; (2) for the impact groups, '<scope phrase> that <hazard phrase> <impact "
    "mechanism> <asset class phrase>', where the hazard phrase is the broader-hazard phrase when a cited impact group has "
    "hazard_relation broader_hazard, else the plain quantity; the driver groups as in any item; the general closing clause "
    "when no cited group is state- or NCA-specific; (3) never state that an asset, or the asset class, in the place will "
    "fail, is at risk, is vulnerable or will be damaged. Only when citing a group listed in place_named_impact_group_ids "
    "may the answer write 'For <asset class phrase> in <Place>, this implies more exposure to <impact outcome>'.")
RUNG8_GUARDRAILS = (
    "Research on an asset class describes what such conditions can do to that kind of asset; it is not a forecast for a "
    "particular asset at the place.",
    "Impact statements are general unless a group is marked place_named for the place.",
)


def asset_phrase(asset_class: str) -> str:
    if asset_class not in ASSET_CLASS_PHRASE:
        raise ValueError(f"no plain phrase for asset class {asset_class!r}")
    return ASSET_CLASS_PHRASE[asset_class]


def cisa_sector_names() -> dict:
    import yaml

    d = yaml.safe_load((REPO_ROOT / "data" / "metadata" / "litstatements" / "infrastructure_lexicon_v1.yaml").read_text(encoding="utf-8"))
    return {a["id"]: a["cisa_sector"] for a in d["asset_classes"]}


def change_word(p: dict) -> str:
    if p.get("direction") not in ("increase", "decrease"):
        raise ValueError(f"{p['pattern_id']}: direction {p.get('direction')!r} has no rung-8 change word")
    return p["direction"]


def form_slots(form_id: str, p: dict, plain: dict, place: str, asset: str) -> dict:
    """The QF-08 / 09 / 10 slots (EXECUTOR, so that each question reads grammatically): the change is the pattern's
    direction ("increase"), for QF-09 ("What could a <change> ...") "projected <direction>"; for QF-10 ("Why does <hazard
    phrase> matter ...") a counted quantity (one with a season unit) is written "the number of <quantity_short>"."""
    hazard = plain["quantity_short"]
    if form_id == "QF-10" and plain.get("season_unit"):
        hazard = f"the number of {hazard}"
    change = f"projected {change_word(p)}" if form_id == "QF-09" else change_word(p)
    return {"change": change, "hazard_phrase": hazard, "place": place, "horizon": plain["horizon"], "asset_class": asset}


# --- inputs -----------------------------------------------------------------------------------------------------------


def rung3_inputs() -> dict:
    """The pinned inputs of packets v4b (`synthpackets_v4.build_selection(variant="v4b")`), for any v3 seed."""
    from climrr import itemseeds_v2 as s2
    from climrr import itemseeds_v3 as s3
    from climrr import litgroups as lgr
    from climrr import litindependence as li
    from climrr import litstatements as ls
    from climrr import litstatements_run2 as r2
    from climrr import p2b_mentor_v3 as m3
    from climrr import pattern_descriptors as pd
    from climrr import pilot_selection as psel

    pin = json.loads(s3.SUMMARY_PATH.read_text(encoding="utf-8"))["seeds_file"]["sha256"]
    if not s3.SEEDS_PATH.is_file() or sha256_file(s3.SEEDS_PATH) != pin:
        raise ValueError(f"item_seeds_v3.jsonl is absent or differs from its pin {pin}; run scripts/build_item_seeds_v3.py")
    records = sd.read_jsonl(r2.INGESTED_PATH)
    corrections, overrides = m3.corrections_v1a()
    statements = {r["statement_id"]: r for r in ls.load_statements(m3.mx.STATEMENTS_INGESTED_PATH)}
    reslices = m3.reslices_v1a(corrections, statements)
    corrected = ls.apply_provenance_corrections(records, corrections, reslices, correction_file=ls.CORRECTIONS_V1A_PATH.name)
    indep = json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    nca = sd.nca_map()
    rows = s2.statement_table(records, sd.read_jsonl(li.CLUSTERS_V1B_PATH), indep, lg.Gazetteer(nca))
    groups = ls.apply_group_label_overrides(lgr.apply_dispositions(lgr.read_groups(v4.GROUPS_PATH), v4.load_dispositions_v4a()), overrides)
    rules, was = pd.load_rules(pd.RULES_V4_PATH), v4.load_working_assumptions()
    plain = pl.load(pl.PLAIN_V1A_PATH)
    hashes = v4.inputs_hashes(s3.SEEDS_PATH, v4.GROUPS_PATH, psel.SELECTION_V2A_PATH, lgr.DISPOSITIONS_PATH, ls.CORRECTIONS_V1A_PATH,
                              rules, plain, fire_dispositions_path=v4.FIRE_DISPOSITIONS_PATH)
    hashes.pop("pilot_selection")                                   # not a rung-8 input
    return {"seeds_v3": {s["seed_id"]: s for s in sd.read_jsonl(s3.SEEDS_PATH)}, "groups": groups,
            "by_statement": spk.statement_lookup(corrected, indep), "rows": rows, "nca": nca, "rules": rules, "was": was,
            "plain": plain, "hashes": hashes}


# --- impact groups ----------------------------------------------------------------------------------------------------


def impact_members(view: dict, by_id: dict, canon: dict, places: dict, gz: lg.Gazetteer) -> list[dict]:
    out = []
    for sid in view["members"]:
        r = by_id[sid]
        pr, ev = r["proposal"], r.get("evidence") or {}
        geo = lg.classify(pr.get("region"), pr.get("region_scope"), gz)
        out.append({"statement_id": sid, "statement": pr["statement"], "paper_item_id": r["paper_item_id"],
                    "canonical_paper": canon.get(r["paper_item_id"], r["paper_item_id"]), "paper_sha256": r["paper_sha256"],
                    "json_path": ev.get("json_path"), "span_start": ev.get("span_start"), "span_end": ev.get("span_end"),
                    "verbatim_passage": r["verbatim_passage"], "evidence_role": r["evidence_role"],
                    "passage_type": pr.get("passage_type"), "region": pr.get("region"), "scenario": r["scenario"]["value"],
                    "basis": lg.relevance(geo, places), "region_class": geo["class"], "region_qualifier": geo.get("qualifier"),
                    "states": list(geo["states"]), "asset_class": pr.get("asset_class"), "hazard_relation": r.get("hazard_relation"),
                    "impact_mechanism": pr.get("impact_mechanism"), "impact_outcome": pr.get("impact_outcome")})
    return out


def impact_provenance(view: dict, members: list[dict], enriched: dict) -> dict:
    e = enriched[view["group_id"]]
    return {"group_id": view["group_id"], "kind": e["kind"], "statement_type": "impact", "claim_about": e["claim_about"],
            "role": "impact", "excluded_reason": None, "label": e["label"] if e["kind"] == "group" else None,
            "claim_about_source": "agent", "disposition": None, "review_state": REVIEW_STATE,
            "group_strength_run": e["evidence_strength"], "strength_in_packet": view["evidence_strength"],
            "n_members_run": e["n_members"], "relevance": view["relevance"], "hazard_relation": view["hazard_relation"],
            "asset_classes": view["asset_classes"], "partition": e["partition"],
            "n_papers": len({m["canonical_paper"] for m in members}), "members": members}


def impact_model_group(g: dict, plain: dict) -> dict:
    x = spk._model_group(g)
    for xm, m in zip(x["members"], g["members"]):
        xm["asset_class"] = m["asset_class"]
    x.update({"hedge": pl.hedge(g["strength_in_packet"], plain), "relevance": g["relevance"], "hazard_relation": g["hazard_relation"],
              "asset_classes": g["asset_classes"],
              "impact_mechanism": list(dict.fromkeys(m["impact_mechanism"] for m in g["members"] if m["impact_mechanism"])),
              "impact_outcome": list(dict.fromkeys(m["impact_outcome"] for m in g["members"] if m["impact_outcome"])),
              "review_state": REVIEW_STATE})
    return x


# --- packet -----------------------------------------------------------------------------------------------------------


def build_packet(cell: dict, seed8: dict, base_in: dict, infra: dict, forms: dict, plain_v1b: dict, sectors: dict,
                 extra_hashes: dict) -> dict:
    """The rung-8 packet of one selected cell (module docstring)."""
    s3 = base_in["seeds_v3"][seed8["rung3_seed_id"]]
    p = s3["pattern"]
    nca, gz = base_in["nca"], infra["gz"]
    base = v4.build_packet(s3, 3, cell["item_id"], base_in["groups"], base_in["by_statement"], base_in["rows"], nca,
                           base_in["hashes"], base_in["rules"], base_in["plain"], base_in["was"], variant="v4b")
    drivers = [g for g in base["provenance"]["groups"] if g["role"] == "driver"]
    if [g["group_id"] for g in drivers] != list(seed8["driver_group_ids"] or []):
        raise ValueError(f"{cell['item_id']}: the rung-3 driver groups differ from the seed's driver_group_ids")
    excluded = list(base["excluded_groups"]) + [
        {"group_id": g["group_id"], "statement_type": g["statement_type"], "claim_about": g["claim_about"],
         "reason": "rung8:context_not_attached"} for g in base["provenance"]["groups"] if g["role"] != "driver"]
    places = sd.pattern_places(p, nca)
    views = seed8["impact_groups"]
    kept, over = views[:MAX_IMPACT_GROUPS], views[MAX_IMPACT_GROUPS:]
    excluded += [{"group_id": v["group_id"], "statement_type": "impact", "claim_about": si.IMPACT_CLAIM, "reason": "over_cap:impact"}
                 for v in over]
    impact = [impact_provenance(v, impact_members(v, infra["by_id"], infra["canon"], places, gz), infra["enriched"]) for v in kept]
    place = p["geography"]
    a = seed8["asset_class"]
    phrase = asset_phrase(a)
    fam = plain_v1b["families"][p["family"]]

    x = copy.deepcopy(base)
    mv, ci, prov = x["model_view"], x["checks_input"], x["provenance"]
    plain = {**mv["plain_language"], "version": plain_v1b["version"], "broader_hazard_phrase": fam["broader_hazard_phrase"]}
    keep_ids = {g["group_id"] for g in drivers}
    mv["groups"] = [g for g in mv["groups"] if g["group_id"] in keep_ids] + [impact_model_group(g, base_in["plain"]) for g in impact]
    prov["groups"] = drivers + impact
    pgs = {g["group_id"]: g for g in prov["groups"]}
    scopes = {gid: v5.group_scope(g, p, nca, gz, rule="majority") for gid, g in pgs.items()}
    for g in mv["groups"]:
        sc = scopes[g["group_id"]]
        g["scope_class"] = sc["class"]
        g["scope_phrase"] = v5.scope_phrase(sc["stem"], pgs[g["group_id"]]["strength_in_packet"])
        g["scope_optional_clause"] = sc["optional_clause"]
    classes = sorted({s["class"] for s in scopes.values()}, key=v5.CLASS_ORDER_V5A.index)
    needs = not any(c in v5.PLACE_CLASSES for c in classes)
    clause = f"These are general drivers of {plain['quantity_short']}, not findings specific to {place}."
    form = next(f for f in forms["forms"] if f["id"] == cell["question_form_id"])
    qf = {"id": form["id"], "name": form["name"],
          "skeleton": v5.fill_skeleton(form, form_slots(form["id"], p, {**plain, "season_unit": fam.get("season_unit")}, place, phrase)),
          "opening_regex": form["opening_regex"], "min_question_marks": form["min_question_marks"]}
    fire = p["family"] == "fire_weather_index"
    mnu = list(dict.fromkeys(list(mv["must_not_use"]) + [w for w in FIRE_WORDS if not (fire and w == "wildfire")]
                             + list(RUNG8_MUST_NOT_USE)))
    if fire:
        mnu = [w for w in mnu if w != "wildfire"]
    place_named = [g["group_id"] for g in impact if g["relevance"] == "place_named"]
    name, modality, desc = LEVEL_TEXT_8
    infra_papers = sorted({m["paper_item_id"] for g in impact for m in g["members"]})

    mv.update({"use_case_level": RUNG, "rung": RUNG, "rung_name": f"{RUNG}. {name}: {desc}", "reasoning_modalities": modality,
               "rung_instruction": RUNG8_INSTRUCTION, "asset_class": a, "asset_class_phrase": phrase, "cisa_sector": sectors[a],
               "place_named_impact_group_ids": place_named, "plain_language": plain, "must_not_use": mnu,
               "guardrails": list(mv["guardrails"]) + list(RUNG8_GUARDRAILS), "review_state": REVIEW_STATE,
               "scope": {"decision": v5.DECISION_V5A, "place": place, "classes_present": classes, "needs_general_clause": needs,
                         "general_clause": clause, "rule": "majority of cited members; ties -> general; minority place mentions -> optional clause"},
               "question_form": qf})
    if fire:
        mv["wildfire_rule"] = WILDFIRE_RULE
    ci.update({"level": RUNG,
               "group_strength": {g["group_id"]: g["strength_in_packet"] for g in prov["groups"]},
               "group_role": {g["group_id"]: g["role"] for g in prov["groups"]},
               "group_texts": {g["group_id"]: ([g["label"]] if g["label"] else []) + [m["statement"] for m in g["members"]]
                               for g in prov["groups"]},
               "forbidden_strings": list(dict.fromkeys(list(ci["forbidden_strings"]) + infra_papers)),
               "scope": {"decision": v5.DECISION_V5A,
                         "groups": {gid: {"class": s["class"], "stem": s["stem"], "optional_clause": s["optional_clause"]}
                                    for gid, s in scopes.items()},
                         "general_clause": clause, "needs_general_clause": needs,
                         "place_names": list(dict.fromkeys(places["state"] + places["nca_region"]))},
               "question_form": {k: qf[k] for k in ("id", "name", "opening_regex", "min_question_marks")},
               "rung8": {"impact_group_ids": [g["group_id"] for g in impact], "place_named_impact_group_ids": place_named,
                         "group_hazard_relation": {g["group_id"]: g["hazard_relation"] for g in impact},
                         "asset_class_phrase": phrase, "broader_hazard_phrase": fam["broader_hazard_phrase"],
                         "quantity_phrases": [plain["quantity"], plain["quantity_short"]]}})
    prov["item_frame"] = {"use_case_level": RUNG, "reasoning_modalities": modality, "level_name": name}
    x.update({"packet_id": f"PK-{seed8['seed_id']}", "version": VERSION, "decision": DECISION, "rules": RULES,
              "item_id": cell["item_id"], "seed_id": seed8["seed_id"], "rung3_seed_id": s3["seed_id"], "use_case_level": RUNG,
              "asset_class": a, "state": place, "review_state": REVIEW_STATE, "provisional": True,
              "place_named_impact_evidence": cell["place_named_impact_evidence"], "question_form_id": form["id"],
              "plain_language": plain_v1b["version"], "plain_language_sha256": plain_v1b["sha256"],
              "excluded_groups": excluded, "scope_detail": scopes,
              "selection": {"file": "artifacts/benchmark/pilot_selection_infra_v1.yaml", "decision": "D-075",
                            **{k: cell[k] for k in ("order", "item_id", "family", "asset_class", "state", "state_basis",
                                                     "candidate_states", "table_change", "place_named_impact_evidence",
                                                     "question_form_id")}},
              "inputs_sha256": {**base["inputs_sha256"], **extra_hashes, "plain_language": plain_v1b["sha256"],
                                "question_forms": forms["sha256"]}})
    x.pop("fire_groups_unreviewed", None)
    return x


def build(selection: dict, seeds8: list[dict], enriched: list[dict], records: list[dict], indep: dict, extra_hashes: dict) -> list[dict]:
    """Every rung-8 packet of the selection, in selection order."""
    from climrr import litindependence as li

    base_in = rung3_inputs()
    infra = {"by_id": {r["statement_id"]: r for r in records}, "canon": li.canonical_map(indep),
             "enriched": {g["group_id"]: g for g in enriched}, "gz": lg.Gazetteer(base_in["nca"])}
    forms = si.load_question_forms_v2()
    plain_v1b = pl.load(pl.PLAIN_V1B_PATH)
    sectors = cisa_sector_names()
    by_seed = {s["seed_id"]: s for s in seeds8}
    return [build_packet(c, by_seed[c["seed_id"]], base_in, infra, forms, plain_v1b, sectors, extra_hashes) for c in selection["selected"]]


def report_entry(pk: dict, path=None) -> dict:
    """Per packet: the pattern summary, the impact groups (id, label, strength, place class), the driver groups, excluded."""
    p = pk["provenance"]["patterns"][0]
    d = pk["model_view"]["patterns"][0]["allowed_descriptors"]
    mv = pk["model_view"]
    groups = {g["group_id"]: g for g in mv["groups"]}
    prov = {g["group_id"]: g for g in pk["provenance"]["groups"]}
    return {"item_id": pk["item_id"], "packet_id": pk["packet_id"], "seed_id": pk["seed_id"], "family": pk["family"],
            "asset_class": pk["asset_class"], "state": pk["state"], "question_form": mv["question_form"]["id"],
            "question_skeleton": mv["question_form"]["skeleton"],
            "pattern": {"pattern_id": p["pattern_id"], "metric": p["metric"], "statistic": p["statistic"], "horizon": p["horizon"],
                        "direction": d["direction"], "value": pk["model_view"]["patterns"][0]["values_shown"].get("value"),
                        "magnitude_class": d["magnitude_class"], "anchor_pair": d.get("anchor_pair"),
                        "comparison": (d.get("tercile_forms") or [None])[0]},
            "place_named_impact_evidence": pk["place_named_impact_evidence"],
            "needs_general_clause": mv["scope"]["needs_general_clause"], "classes_present": mv["scope"]["classes_present"],
            "impact_groups": [{"group_id": gid, "label": prov[gid]["label"] or prov[gid]["members"][0]["statement"],
                               "is_singleton": prov[gid]["kind"] == "singleton", "evidence_strength": prov[gid]["strength_in_packet"],
                               "relevance": prov[gid]["relevance"], "scope_class": groups[gid]["scope_class"],
                               "scope_phrase": groups[gid]["scope_phrase"], "hazard_relation": prov[gid]["hazard_relation"]}
                              for gid in pk["checks_input"]["rung8"]["impact_group_ids"]],
            "place_named_impact_group_ids": mv["place_named_impact_group_ids"],
            "driver_groups": [{"group_id": g["group_id"], "label": g["label"], "evidence_strength": g["evidence_strength"],
                               "scope_class": g["scope_class"]} for g in mv["groups"] if g["role"] == "driver"],
            "excluded_groups": len(pk["excluded_groups"]),
            "excluded_by_reason": dict(sorted(Counter(str(e["reason"]) for e in pk["excluded_groups"]).items())),
            "review_state": pk["review_state"], **({"sha256": sha256_file(path)} if path else {})}


def dumps(pk: dict) -> str:
    return json.dumps(pk, indent=2, ensure_ascii=False) + "\n"
