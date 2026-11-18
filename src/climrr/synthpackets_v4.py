"""Seed packets v4 (work package P3a; D-059 -- D-065): the sample set for the mentor, under the generality rules.

One packet per seed of `data/metadata/benchmark/pilot_selection_v2.yaml`, built from the v3 seed (`item_seeds_v3.jsonl`:
the pattern copy with its working assumptions, D-064) and the grouping run's groups, by the v3 / v3a rules of
`synthpackets.py` (relevance under geography v2; DR-SEED-RANK-3 order and caps; dispositions v1a and the no-disposition
rule for the heat arm) with these changes:

- **Plain language (D-060, D-061).** `model_view.plain_language` carries the phrases the graded text must use (quantity
  without its threshold, "under a high-emissions future", "by mid-century" / "by late this century", the D-062 hedges;
  `plain_language_v1.yaml`). The pattern text names the quantity, the horizon and the scenario in those words: no
  threshold, no window years, no RCP label; the threshold and the years are not allowed numbers. The exact threshold,
  scenario, window and values stay in `provenance` (the pattern record). Descriptors are DR-DESC-1 v3.
- **Hedges (D-062).** Every group in `model_view` carries `hedge`: "research shows" / "research has shown" for a
  multi-source or review group, "research suggests" for a single-source one. The strength label is unchanged.
- **Scenario (D-061).** No rung 7 (retired); no rung instruction; the guardrail on the scenario names no RCP label.
- **Fire arm unreviewed.** The fire-arm groups' claim tags were never human-reviewed and no disposition file covers them:
  they are attached by the agent's claim tag under the same rules, without the no-disposition rule
  (`synthpackets.packet_groups(unreviewed_arms=...)`), each marked `review_state: unreviewed_agent_tag`, and the packet
  carries `fire_groups_unreviewed: true` for the COORDINATOR's review before the run.
- **Corrections v1a (D-057, D-058).** The reviewer-verified overlay is applied to the statement records (corrected passage,
  location and statement of LS-199098498-04) and to the groups (reviewer label of LG-extreme_heat_v1-driver-c1-008)
  before the groups are chosen, so the model sees the corrected text; the originals stay in each record. EXECUTOR choice,
  recorded for confirmation (packets v3 did not carry the overlay: they predate it).
- **Working assumptions (D-064).** `working_assumptions_relied_on` (packet top level and `provenance`) lists every
  owner-authorized working assumption the pattern relies on; the pattern record carries its ids.
- **NCA5 grouping (D-065).** `inputs_sha256` names the NCA5 map and its owner-disposition sidecar, so every item built
  from a packet references the map hash (`generation.inputs_sha256`).

**Packets v4a (P3a hotfix, D-053b).** `build_selection(variant="v4a")`: selection v2a (seven items, BI-P3-0006 dropped,
ids kept), plain language v1a (the fire-weather quantity "fire-weather danger (how hot, dry and windy conditions favour
fire)" and its `never_write` words), and the fire-arm dispositions v1 (`group_dispositions_fire_v1.csv`) applied with the
heat dispositions v1a under the same rule set: the fire arm is no longer an unreviewed arm, so the no-disposition rule
applies to it (an undisposed fire group that would otherwise be attached is excluded, `no_disposition`, never refilled
with another undisposed group; listed as `undisposed_candidates`); every attached fire group carries
`review_state: reviewer_tagged`. `checks_input` gains `family` and `plain_quantity`, which post-checks v3 use for the
fire-weather words. Packets v4 (`variant="v4"`, the default) are built exactly as before.

**Packets v4b (work package P3b, D-066, D-067).** `build_selection(variant="v4b")`: packets v4a (same selection, plain
language v1a, dispositions and groups) with DR-DESC-1 **v4** descriptors (`descriptor_rules_v4.yaml`: magnitude and
tercile `forms`, the fixed rare rule), and:
- `model_view.must_not_use`: the words the graded text never writes, anywhere --- the plain-language `never_write` words
  (for fire weather "wildfire", "fires", "burned area"), the tercile words of the v4 rules, "RCP", "SSP";
- the pattern text's relative-magnitude sentence written as the comparison ("Comparison with other U.S. states: a larger
  change than in most states (...)"), so "tercile" is not in the text the model reads;
- `checks_input.group_role` (each group's role: driver / context / caveat) and, for a regional contrast,
  `checks_input.regions` (the ranked regions), which post-checks v3.1 use.
Packets v4 and v4a stay as built.

No model call; no table value computed here (values are copied from the pattern).
"""

from __future__ import annotations

from climrr import benchmark_items as bi
from climrr import dictionary as dc
from climrr import itemseeds as sd
from climrr import litgeo as lg
from climrr import pattern_descriptors as pd
from climrr import plain_language as pl
from climrr import synthpackets as spk
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

VERSION = "synthpackets v4"
RANK_RULE = "DR-SEED-RANK-3"
PACKETS_DIR = REPO_ROOT / "artifacts" / "benchmark" / "synth_packets_v4"
NCA_DISPOSITION_PATH = REPO_ROOT / "data" / "metadata" / "geography" / "nca_regions_v1_disposition.yaml"
UNREVIEWED_ARMS = ("fire_weather_v1",)
VERSION_V4A = "synthpackets v4a"
PACKETS_V4A_DIR = REPO_ROOT / "artifacts" / "benchmark" / "synth_packets_v4a"
FIRE_DISPOSITIONS_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "group_dispositions_fire_v1.csv"
REVIEWED_ARMS_V4A = ("fire_weather_v1",)                         # arms whose dispositions D-053b adds: review_state marked
VERSION_V4B = "synthpackets v4b"
PACKETS_V4B_DIR = REPO_ROOT / "artifacts" / "benchmark" / "synth_packets_v4b"
VARIANTS = ("v4", "v4a", "v4b")
EXTRA_MUST_NOT_USE = ("RCP", "SSP")


def comparison_text(text: str, descr: dict) -> str:
    """v4b: the pattern text with its relative-magnitude sentence written as the DR-DESC-1 v4 comparison (first form)."""
    import re

    if not descr.get("tercile_forms"):
        return text
    out, n = re.subn(r"Relative magnitude: (?:small|moderate|large) \((?:lower|middle|upper) tercile, ",
                     f"Comparison with other U.S. states: {descr['tercile_forms'][0]} (", text)
    if n != 1:
        raise ValueError(f"{descr['pattern_id']}: relative-magnitude sentence not found once in the pattern text")
    return out


def must_not_use(phrases_view: dict, rules: dict) -> list[str]:
    """v4b: the words the graded text never writes (plain-language never_write, the v4 tercile words, RCP / SSP)."""
    return list(dict.fromkeys(list(phrases_view["never_write"]) + list(rules["tercile"]["never_in_graded_text"])
                              + list(EXTRA_MUST_NOT_USE)))
LEVELS = (3, 4)
GUARDRAILS = (
    "A modeled historical baseline is model output for a past period, not an observation.",
    "A Fire Weather Index is a meteorological fire-danger index; it is never fire occurrence, ignition, burned area or damage.",
    "A high-emissions future is one plausible future, not a forecast and not the only plausible future.",
    "Hazard is not exposure, and exposure is not risk.",
)


def effective_scenario(p: dict, rules: dict) -> str:
    """The scenario whose phrase the pattern takes: its own, or the working assumption's (DR-DESC-1 v3, D-064)."""
    wa = (rules.get("scenario_working_assumption") or {}).get(p["scenario"])
    return wa["scenario"] if wa else p["scenario"]


def group_hedge(strength: str, plain: dict) -> list[str]:
    return pl.hedge(strength, plain)


def working_assumptions_relied_on(p: dict, was: dict) -> list[dict]:
    return [{"id": w, "resolution": was[w]["resolution"], "status": was[w]["status"], "covers": list(was[w]["covers"])}
            for w in p.get("working_assumptions") or []]


def assemble_packet(seed_id: str, p: dict, lvl: int, item_id: str, pg: list[dict], nca: dict, inputs_sha256: dict,
                    excluded: list[dict], rules: dict, plain: dict, was: dict, variant: str = "v4") -> dict:
    if lvl not in LEVELS:
        raise ValueError(f"packets v4 build rungs {LEVELS} only (D-059, D-061), got {lvl}")
    scen = effective_scenario(p, rules)
    phrases_view = pl.model_view(p["family"], scen, p["horizon"], plain)
    text, shown, allowed = spk.render_pattern(p, nca, plain=phrases_view)
    descr = pd.descriptors(p, rules, plain)
    if variant == "v4b":
        text = comparison_text(text, descr)
    phrases = pd.phrases(descr) + [phrases_view["quantity_short"]]
    phrases = list(dict.fromkeys(phrases))
    allowed |= {n for ph in phrases for n in bi.reference_numbers(ph)}
    name, modality, desc = spk.LEVEL_TEXT[lvl]
    cols = sorted({c["column"] for c in p["provenance"]["columns"]})
    paper_ids = sorted({m["paper_item_id"] for g in pg for m in g["members"]})
    wa = working_assumptions_relied_on(p, was)
    groups_view = []
    for g in pg:
        x = spk._model_group(g)
        x["hedge"] = group_hedge(g["strength_in_packet"], plain)
        if g.get("review_state"):
            x["review_state"] = g["review_state"]
        groups_view.append(x)
    unreviewed = any(g.get("review_state") == "unreviewed_agent_tag" for g in pg)
    checks_extra = {"family": p["family"], "plain_quantity": [phrases_view["quantity"], phrases_view["quantity_short"]]} \
        if variant in ("v4a", "v4b") else {}
    view_extra = {}
    if variant == "v4b":
        checks_extra["group_role"] = {g["group_id"]: g["role"] for g in pg}
        if descr.get("ranking_largest_first"):
            checks_extra["regions"] = list(descr["ranking_largest_first"])
        view_extra["must_not_use"] = must_not_use(phrases_view, rules)
    version = {"v4": VERSION, "v4a": VERSION_V4A, "v4b": VERSION_V4B}[variant]
    return {
        "packet_id": f"PK-{seed_id}", "version": version, "rank_rule": RANK_RULE, "descriptor_rule": rules["rule"],
        "descriptor_rules_sha256": rules["sha256"], "plain_language": plain["version"], "plain_language_sha256": plain["sha256"],
        "item_id": item_id, "seed_id": seed_id, "use_case_level": lvl, "family": p["family"],
        "fire_groups_unreviewed": unreviewed, "working_assumptions_relied_on": wa,
        "model_view": {
            "use_case_level": lvl, "rung": f"{lvl}. {name}: {desc}", "reasoning_modalities": modality,
            "plain_language": phrases_view, **view_extra,
            "patterns": [{"pattern_id": p["pattern_id"], "text": text, "values_shown": shown, "allowed_descriptors": descr}],
            "groups": groups_view,
            "allowed_numbers": sorted(allowed, key=lambda s: (len(s), s)),
            "guardrails": list(GUARDRAILS), "item_fields": list(spk.ITEM_FIELDS),
        },
        "provenance": {"patterns": [p], "groups": pg, "working_assumptions_relied_on": wa,
                       "item_frame": {"use_case_level": lvl, "reasoning_modalities": modality, "level_name": name},
                       "exact": {"scenario": p["scenario"], "scenario_effective": scen, "horizon_window": p["horizon_window"],
                                 "threshold_F": spk.threshold(p), "metric_wording": p.get("metric_wording")}},
        "checks_input": {"pattern_ids": [p["pattern_id"]],
                         "group_strength": {g["group_id"]: g["strength_in_packet"] for g in pg},
                         "allowed_numbers": sorted(allowed), "allowed_descriptors": phrases, "exact_values": spk.exact_values(p),
                         "forbidden_strings": cols + paper_ids,
                         "group_texts": {g["group_id"]: ([g["label"]] if g["label"] else []) + [m["statement"] for m in g["members"]]
                                         for g in pg},
                         "level": lvl, **checks_extra},
        "excluded_groups": list(excluded),
        "inputs_sha256": inputs_sha256,
    }


def build_packet(seed: dict, level: int, item_id: str, groups: list[dict], by_statement: dict, rows: list[dict], nca: dict,
                 inputs_sha256: dict, rules: dict, plain: dict, was: dict, selection: dict | None = None,
                 variant: str = "v4") -> dict:
    """`groups`: dispositions and label overrides applied; `by_statement`: the corrected statement lookup; `rows`:
    `itemseeds_v2.statement_table` with the v2 gazetteer. `variant`: "v4" (fire arm unreviewed) or "v4a" (D-053b: the fire
    arm under its dispositions and the no-disposition rule; attached fire groups `review_state: reviewer_tagged`)."""
    if variant not in VARIANTS:
        raise ValueError(f"unknown packet variant {variant!r}")
    basis = spk.relevant_basis(seed["pattern"], rows, nca)
    geo = {r["statement_id"]: r["geo"] for r in rows}
    pg, excluded = spk.packet_groups(level, groups, by_statement, basis, geo,
                                     unreviewed_arms=UNREVIEWED_ARMS if variant == "v4" else ())
    src = {g["group_id"]: g for g in groups}
    for g in pg:                                                   # D-058: the reviewer label is marked, the agent's kept
        if src[g["group_id"]].get("label_override"):
            g["label_override"] = src[g["group_id"]]["label_override"]
        if variant in ("v4a", "v4b") and src[g["group_id"]]["arm"] in REVIEWED_ARMS_V4A:
            if g["disposition"] is None:                           # the no-disposition rule keeps these out
                raise ValueError(f"{g['group_id']}: attached with no disposition")
            g["review_state"] = "reviewer_tagged"
    pk = assemble_packet(seed["seed_id"], seed["pattern"], level, item_id, pg, nca, inputs_sha256, excluded, rules, plain, was,
                         variant=variant)
    pk["relevance"] = {"geography": lg.VERSION, "n_relevant_statements": len(basis),
                       "by_basis": {b: sum(x == b for x in basis.values()) for b in lg.BASIS_ORDER}}
    if selection is not None:
        pk["selection"] = selection
    return pk


def inputs_hashes(seeds_path, groups_path, selection_path, dispositions_path, corrections_path, rules: dict, plain: dict,
                  fire_dispositions_path=None) -> dict:
    from climrr import itemseeds_v3 as s3
    from climrr import litaggregate as la
    from climrr import litindependence as li

    return {"item_seeds_v3": sha256_file(seeds_path), "groups": sha256_file(groups_path),
            "statements_ingested": sha256_file(la.r2.INGESTED_PATH), "independence_v2": sha256_file(li.INDEPENDENCE_PATH),
            "clusters_v1b": sha256_file(li.CLUSTERS_V1B_PATH), "exclusions": sha256_file(lg.EXCLUSIONS_PATH),
            "pilot_selection": sha256_file(selection_path), "group_dispositions": sha256_file(dispositions_path),
            "provenance_corrections": sha256_file(corrections_path), "descriptor_rules": rules["sha256"],
            "plain_language": plain["sha256"], "resolutions": sha256_file(s3.RESOLUTIONS_PATH),
            "nca_map": sd.NCA_MAP_SHA256, "nca_regions_disposition": sha256_file(NCA_DISPOSITION_PATH),
            **({"group_dispositions_fire": sha256_file(fire_dispositions_path)} if fire_dispositions_path else {})}


def load_working_assumptions() -> dict:
    from climrr import itemseeds_v3 as s3

    return dc.working_assumptions(dc.load_resolutions(s3.RESOLUTIONS_PATH.read_text(encoding="utf-8")))


GROUPS_PATH = REPO_ROOT / "artifacts" / "litgroups" / "run2" / "groups_enriched.jsonl"


def load_dispositions_v4a() -> dict:
    """Heat dispositions v1a and fire-arm dispositions v1 (D-053b), each checked against its manifest pin; no group twice."""
    from climrr import litgroups as lgr

    heat, fire = lgr.load_dispositions(lgr.DISPOSITIONS_PATH), lgr.load_dispositions(FIRE_DISPOSITIONS_PATH)
    both = sorted(set(heat) & set(fire))
    if both:
        raise ValueError(f"groups disposed in both files: {both}")
    if any(not k.startswith("LG-fire_weather_v1-") for k in fire):
        raise ValueError("the fire dispositions name a group outside the fire arm")
    return {**heat, **fire}


def build_selection(selection_path=None, variant: str = "v4") -> dict:
    """Every packet of the pilot selection v2 (v4) or v2a (v4a), in order, from the pinned inputs: {"selection", "packets",
    "conflicts", "hashes", "rules", "plain", "reslices", "groups"}. Raises when an input differs from its pin or the
    selection fails its checks."""
    import json

    from climrr import itemseeds_v2 as s2
    from climrr import itemseeds_v3 as s3
    from climrr import litgroups as lgr
    from climrr import litindependence as li
    from climrr import litstatements as ls
    from climrr import litstatements_run2 as r2
    from climrr import p2b_mentor_v3 as m3
    from climrr import pilot_selection as psel
    from climrr.paths import repo_relative

    if variant not in VARIANTS:
        raise ValueError(f"unknown packet variant {variant!r}")
    v4a = variant in ("v4a", "v4b")                                # v4b: v4a's inputs, DR-DESC-1 v4
    selection_path = selection_path or (psel.SELECTION_V2A_PATH if v4a else psel.SELECTION_V2_PATH)
    sel = psel.load(selection_path)
    pin = json.loads(s3.SUMMARY_PATH.read_text(encoding="utf-8"))["seeds_file"]["sha256"]
    if not s3.SEEDS_PATH.is_file() or sha256_file(s3.SEEDS_PATH) != pin or sel["seeds_file"]["sha256"] != pin:
        raise ValueError(f"{repo_relative(s3.SEEDS_PATH)} is absent or differs from its pin {pin} (or the selection's); "
                         "run scripts/build_item_seeds_v3.py")
    seeds = {s["seed_id"]: s for s in sd.read_jsonl(s3.SEEDS_PATH)}
    errs = psel.check_v2a(sel, seeds) if v4a else psel.check_v2(sel, seeds)
    if errs:
        raise ValueError(f"pilot selection {sel['version']} fails its checks: " + "; ".join(errs))
    records = sd.read_jsonl(r2.INGESTED_PATH)
    corrections, overrides = m3.corrections_v1a()
    statements = {r["statement_id"]: r for r in ls.load_statements(m3.mx.STATEMENTS_INGESTED_PATH)}
    reslices = m3.reslices_v1a(corrections, statements)
    corrected = ls.apply_provenance_corrections(records, corrections, reslices, correction_file=ls.CORRECTIONS_V1A_PATH.name)
    indep = json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    nca = sd.nca_map()
    by_statement = spk.statement_lookup(corrected, indep)
    rows = s2.statement_table(records, sd.read_jsonl(li.CLUSTERS_V1B_PATH), indep, lg.Gazetteer(nca))   # geography v2 (D-047a)
    disp = load_dispositions_v4a() if v4a else lgr.load_dispositions(lgr.DISPOSITIONS_PATH)
    groups = ls.apply_group_label_overrides(lgr.apply_dispositions(lgr.read_groups(GROUPS_PATH), disp), overrides)
    rules, was = pd.load_rules(pd.RULES_V4_PATH if variant == "v4b" else pd.RULES_V3_PATH), load_working_assumptions()
    plain = pl.load(pl.PLAIN_V1A_PATH) if v4a else pl.load()
    hashes = inputs_hashes(s3.SEEDS_PATH, GROUPS_PATH, selection_path, lgr.DISPOSITIONS_PATH, ls.CORRECTIONS_V1A_PATH, rules, plain,
                           fire_dispositions_path=FIRE_DISPOSITIONS_PATH if v4a else None)
    packets = [build_packet(seeds[x["seed_id"]], x["rung"], x["item_id"], groups, by_statement, rows, nca, hashes, rules, plain, was,
                            selection={"file": repo_relative(selection_path), "decision": sel["decision"], **x}, variant=variant)
               for x in psel.selected(sel)]
    return {"selection": sel, "packets": packets, "conflicts": psel.threshold_conflicts(sel, seeds), "hashes": hashes,
            "rules": rules, "plain": plain, "reslices": reslices, "groups": groups}

