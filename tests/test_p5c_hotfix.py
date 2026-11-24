"""Work package P5c hotfix (2026-11-24; D-073c, D-077, D-078): item schema v2a, the COORDINATOR's dispositions of the infra
impact groups, the two-hop fire wording (synthesis agent v5.3, post-checks v3.4), seeds / selection / packets v1a. No model
call. The v1a artifacts are rebuilt and compared byte for byte; v1 stays as built (tests/test_p5c.py).
"""

from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import io
import json
import sys

import pytest
import yaml

from climrr import benchmark_items as bi
from climrr import dispositions_infra as di
from climrr import itemseeds as sd
from climrr import litgeo as lg
from climrr import litgroups_infra_run1 as gi
from climrr import litstatements_infra1 as ir
from climrr import p5c
from climrr import seeds_infra as si
from climrr import synthpackets_infra as spi
from climrr.checksums import sha256_file
from climrr.manifest import load_entry
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
SCHEMA_V2A_SHA256 = "deca317cfdf11c9aa9074b68b7305c3b8ea7922ddf45a0542bc316901400d2d8"
SYNTH_V53_SHA256 = "1be4ba2a6aec418b2729f6d165a3ed159208a0d31b786ad92413d7d195f43edd"
SYNTH_V53_PROMPT_SHA256 = "1157f73286a6de3a443a20becf924be401abd22e46170a62d6f4a580bbd75ea5"
SYNTH_V53_FORMAT_SHA256 = "46f2681cf29adce70900c04a920a3de5ff73005e648e91f7c6095ee668ca84d6"

REC = sd.read_jsonl(ir.INGESTED_PATH)
INDEP = json.loads(ir.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
ENR = sd.read_jsonl(gi.ENRICHED_PATH)
ROWS = di.load()
LOG = json.loads(si.DISPOSITIONS_LOG_PATH.read_text(encoding="utf-8"))
SUMMARY = json.loads(si.SEEDS_V1A_SUMMARY_PATH.read_text(encoding="utf-8"))
SEL = yaml.safe_load(si.SELECTION_V1A_PATH.read_text(encoding="utf-8"))
PMAN = json.loads((spi.PACKETS_V1A_DIR / "manifest.json").read_text(encoding="utf-8"))
PACKETS = {p["item_id"]: json.loads((spi.PACKETS_V1A_DIR / f"{p['packet_id']}.json").read_text(encoding="utf-8")) for p in PMAN["packets"]}


def _load(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _applied():
    return di.apply(sd.read_jsonl(gi.ART / "groups.jsonl"), ROWS)


# --- B: the dispositions -------------------------------------------------------------------------------------------------


def test_dispositions_file_is_pinned_and_in_the_manifest():
    assert sha256_file(di.PATH) == di.SHA256 == "9b94e028bc571d9d84e6714ef1264bf2e087ea405d6561bfcdbd6d333c601bef"
    e = load_entry("group_dispositions_infra_v1.csv")
    assert e["sha256"] == di.SHA256 and e["row_count"] == 103 and e["path"] == "data/metadata/benchmark/group_dispositions_infra_v1.csv"
    review = [r["group_id"] for r in csv.DictReader(io.StringIO(gi.REVIEW_PATH.read_text(encoding="utf-8")))]
    assert [r["group_id"] for r in ROWS] == review                    # one row per review-list record, same order


def test_dispositions_counts():
    assert LOG["by_disposition"] == {"accept": 41, "accept_two_hop": 13, "keep_excluded": 14, "merge_with": 1, "not_about_family": 9,
                                     "reject": 15, "relabel": 10}
    assert LOG["by_disposition_full"]["relabel:hazard_impact_on_asset"] == 6 and LOG["by_disposition_full"]["relabel:impact_or_exposure"] == 4
    assert LOG["by_source"] == {"coordinator": 103}                 # Kaiyuan's column is empty in v1
    assert LOG["records"] == 143 and LOG["no_disposition"] == 40 and LOG["usable"] == 60 and LOG["usable_two_hop"] == 13
    assert LOG["merges"] == [{"from": "LG-infra_heat_index__energy-impact-c1-016", "into": "LG-infra_heat_index__energy-impact-c2-002"}]
    assert LOG["statement_type_relabelled"] == {"LG-infra_heat_index-driver-c1-005": "driver", "LG-infra_heat_index-driver-c1-007": "driver"}
    assert len(LOG["asset_class_overrides"]) == 17 and LOG["usable_impact_views"] == 60


def test_dispositioned_groups_and_log_rebuild_byte_identical():
    recs, log = _applied()
    assert "".join(json.dumps(g, ensure_ascii=False, sort_keys=True) + "\n" for g in recs) == \
        si.GROUPS_DISPOSITIONED_PATH.read_text(encoding="utf-8")
    assert {k: log[k] for k in log} == {k: LOG[k] for k in log}
    assert LOG["groups_dispositioned"]["sha256"] == sha256_file(si.GROUPS_DISPOSITIONED_PATH)


def test_apply_semantics():
    recs = {g["group_id"]: g for g in _applied()[0]}
    merged = recs["LG-infra_heat_index__energy-impact-c2-002"]
    assert merged["merged_from"] == ["LG-infra_heat_index__energy-impact-c1-016"] and len(merged["member_ids"]) == 3
    assert recs["LG-infra_heat_index__energy-impact-c1-016"]["disposition_exclude"] == "merged_into:LG-infra_heat_index__energy-impact-c2-002"
    r = recs["LG-infra_fire_weather_index__other_assets-impact-c1-012"]       # the standby-cost singleton (BI-P5-0007)
    assert r["claim_about"] == "hazard_impact_on_asset" and r["claim_about_run"] == "impact_or_exposure" and not r.get("disposition_exclude")
    d = recs["LG-infra_heat_index-driver-c1-007"]
    assert d["statement_type"] == "impact" and d["statement_type_run"] == "driver" and d["asset_class_override"] == "energy"
    for gid in ("LG-infra_heat_index__healthcare_and_public_health-impact-c1-003", "LG-infra_heat_index__healthcare_and_public_health-impact-c1-004"):
        assert recs[gid]["disposition_exclude"] == "relabel:impact_or_exposure"      # the two Arizona people-statements
    assert recs["LG-infra_fire_weather_index__energy-impact-c1-001"]["two_hop"] is True
    assert recs["LG-infra_heat_index-driver-c1-001"]["disposition_exclude"] == "no_disposition"


def test_load_refuses_bad_vocabulary(tmp_path):
    text = di.PATH.read_text(encoding="utf-8")
    bad = tmp_path / "d.csv"
    bad.write_text(text.replace(",accept_two_hop,", ",accept_maybe,", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="not in the vocabulary"):
        di.load(bad, check_sha=False)
    bad.write_text(text.replace(",water_and_wastewater,", ",water,", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="not a lexicon class"):
        di.load(bad, check_sha=False)
    with pytest.raises(ValueError, match="differs from its pinned"):
        di.load(bad)


# --- A: item schema v2a --------------------------------------------------------------------------------------------------


def _impact_statement():
    return {"statement": "s", "statement_type": "impact", "evidence_strength": "single_source_supported",
            "reference_scope": "single_study_observation", "supports": [], "asset_class": "energy", "impact_mechanism": "m",
            "impact_outcome": "o", "hazard_relation": "broader_hazard", "two_hop": False}


def test_schema_v2a_pinned_and_dispatched():
    assert bi.schema_sha256(bi.SCHEMA_V2A_PATH) == SCHEMA_V2A_SHA256 == load_entry("item_schema_v2a.json")["sha256"]
    assert bi.schema_sha256() == load_entry("item_schema_v2.json")["sha256"]          # v2 unchanged
    v2a = bi.load_schema(bi.SCHEMA_V2A_PATH)
    assert v2a["properties"]["schema_version"]["const"] == "benchmark_item_v2a"
    assert v2a["$defs"]["literature_statement"]["properties"]["statement_type"]["enum"][-1] == "impact"
    assert bi.schema_for({"schema_version": "benchmark_item_v2"})["properties"]["schema_version"]["const"] == "benchmark_item_v2"
    assert bi.schema_for({"schema_version": "benchmark_item_v2a"})["properties"]["schema_version"]["const"] == "benchmark_item_v2a"


def test_schema_v2a_impact_statement_fields():
    sch = bi.resolve_refs(bi.load_schema(bi.SCHEMA_V2A_PATH))["properties"]["reference_components"]["properties"]["literature_mechanisms"]["items"]
    from climrr import softqa

    def errs(x):
        out = []
        softqa._check(x, sch, "$", out)
        return out

    assert errs(_impact_statement()) == []
    for k in ("asset_class", "impact_mechanism", "impact_outcome", "hazard_relation", "two_hop"):
        x = _impact_statement()
        x.pop(k)
        assert errs(x) == [f"$: missing required field {k!r}"], k
    assert errs({**_impact_statement(), "asset_class": "other"}) and errs({**_impact_statement(), "hazard_relation": "none"})
    mech = {**_impact_statement(), "statement_type": "mechanism"}
    for k in ("asset_class", "impact_mechanism", "impact_outcome", "hazard_relation", "two_hop"):
        mech.pop(k)
    assert errs(mech) == []                                            # the impact fields are required only for `impact`
    v2 = bi.resolve_refs(bi.load_schema())["properties"]["reference_components"]["properties"]["literature_mechanisms"]["items"]
    out = []
    softqa._check(_impact_statement(), v2, "$", out)
    assert any("'impact' not in" in e for e in out)                    # v2 still refuses it (frozen)


# --- C: seeds, selection, packets v1a ------------------------------------------------------------------------------------


def test_seeds_and_selection_v1a_rebuild_byte_identical():
    from climrr import itemseeds_v3 as s3

    recs, _ = _applied()
    seeds_v3 = sd.read_jsonl(s3.SEEDS_PATH)
    ctx = si.Context(REC, INDEP, lg.Gazetteer(sd.nca_map()))
    seeds = si.build_seeds(seeds_v3, recs, ctx, si.rung3_driver_ids_factory(), reviewed=True)
    assert "".join(json.dumps(s, ensure_ascii=False, sort_keys=True) + "\n" for s in seeds) == si.SEEDS_V1A_PATH.read_text(encoding="utf-8")
    sel = si.select_pilot(seeds, seeds_v3, REC, ctx, si.load_question_forms_v2(), views=si.impact_views(recs, ctx))
    assert yaml.safe_dump(sel, sort_keys=False, allow_unicode=True, width=120) == si.SELECTION_V1A_PATH.read_text(encoding="utf-8")
    assert SUMMARY["seeds_file"]["sha256"] == sha256_file(si.SEEDS_V1A_PATH) and SUMMARY["seeds"] == len(seeds) == 686
    assert SUMMARY["selection_file"]["sha256"] == sha256_file(si.SELECTION_V1A_PATH)
    assert all(s["review_state"] == "impact_groups_reviewed" and s["version"] == "seeds_infra v1a" for s in seeds)


def test_selection_v1a_cells():
    assert SEL["version"] == "pilot_selection_infra v1a" and SEL["review_state"] == "impact_groups_reviewed" and SEL["missing"] == []
    got = {x["item_id"]: (x["state"], x["place_named_impact_evidence"], x["candidate_states"]) for x in SEL["selected"]}
    assert got == {
        "BI-P5-0001": ("Virginia", "place_named_impact_statement", ["California", "Virginia"]),
        "BI-P5-0002": ("Arizona", "place_named_impact_statement", ["Arizona"]),
        "BI-P5-0003": ("California", "none", []),
        "BI-P5-0004": ("California", "none", []),          # the two Arizona people-statements relabelled out: general fallback
        "BI-P5-0005": ("California", "none", []),          # every place-named fire-energy group rejected (was Arizona in v1)
        "BI-P5-0006": ("California", "none", []),          # Montana rejected, the California group not about the family
        "BI-P5-0007": ("California", "none", []),          # filled by the relabelled standby-cost singleton
        "BI-P5-0008": ("California", "none", [])}
    cell7 = next(x for x in SEL["selected"] if x["item_id"] == "BI-P5-0007")
    assert cell7["impact_group_ids"] == ["LG-infra_fire_weather_index__other_assets-impact-c1-012"]
    cell4 = next(x for x in SEL["selected"] if x["item_id"] == "BI-P5-0004")
    assert cell4["place_named_impact_group_ids"] == [] and cell4["needs_general_clause"] is True
    assert [x["question_form_id"] for x in SEL["selected"]] == ["QF-08", "QF-09", "QF-10"] * 2 + ["QF-08", "QF-09"]


def test_packets_v1a_rebuild_byte_identical():
    seeds = sd.read_jsonl(si.SEEDS_V1A_PATH)
    packets = spi.build(SEL, seeds, ENR, REC, INDEP, dict(PMAN["inputs_sha256"]), variant="v1a")
    assert [p["item_id"] for p in packets] == [f"BI-P5-{k:04d}" for k in range(1, 9)]
    for pk in packets:
        assert spi.dumps(pk) == (spi.PACKETS_V1A_DIR / f"{pk['packet_id']}.json").read_text(encoding="utf-8"), pk["packet_id"]
    for e in PMAN["packets"]:
        assert sha256_file(spi.PACKETS_V1A_DIR / f"{e['packet_id']}.json") == e["sha256"]
    assert PMAN["inputs_sha256"]["group_dispositions_infra_v1"] == di.SHA256
    assert PMAN["inputs_sha256"]["item_schema_v2a"] == SCHEMA_V2A_SHA256


def test_packets_v1a_fields():
    for iid, pk in PACKETS.items():
        mv, ci = pk["model_view"], pk["checks_input"]
        assert pk["review_state"] == mv["review_state"] == "impact_groups_reviewed" and pk["provisional"] is False
        assert pk["item_schema"] == "benchmark_item_v2a" and pk["version"] == "synthpackets infra v1a"
        impact = [g for g in pk["provenance"]["groups"] if g["role"] == "impact"]
        assert all(g["review_state"] == "impact_groups_reviewed" and g["disposition"] for g in impact)
        for g in impact:
            f = g["item_fields"]
            assert f["asset_class"] == pk["asset_class"] and f["impact_mechanism"] and f["impact_outcome"]
            assert f["two_hop"] == g["two_hop"] == (g["disposition"] == "accept_two_hop")
        hop = [g["group_id"] for g in impact if g["two_hop"]]
        assert ci["rung8"]["two_hop_group_ids"] == hop == (mv.get("two_hop_group_ids") or [])
        fire = pk["family"] == "fire_weather_index"
        assert ci["rung8"]["bridge_clause"] == (spi.BRIDGE_CLAUSE if hop and fire else None)
        assert ("bridge_clause" in mv) == bool(hop and fire) and ("two_hop_rule" in mv) == bool(hop)
        assert ("wildfire" in mv["must_not_use"]) == (not fire and not hop)
    hops = {iid: len(pk["checks_input"]["rung8"]["two_hop_group_ids"]) for iid, pk in PACKETS.items()}
    assert hops == {"BI-P5-0001": 1, "BI-P5-0002": 1, "BI-P5-0003": 0, "BI-P5-0004": 0, "BI-P5-0005": 7, "BI-P5-0006": 1,
                    "BI-P5-0007": 0, "BI-P5-0008": 0}
    g = next(x for x in PACKETS["BI-P5-0001"]["provenance"]["groups"] if x["group_id"] == "LG-infra_heat_index-driver-c1-007")
    assert g["item_fields"]["impact_fields_source"] == "group_label" and g["claim_about_source"] == "coordinator_disposition"


# --- B: post-checks v3.4 (two-hop wording) -------------------------------------------------------------------------------


def _fire_ci():
    pk = PACKETS["BI-P5-0005"]
    return pk, pk["checks_input"]


def test_v34_two_hop_sentence_and_bridge():
    pk, ci = _fire_ci()
    mv = pk["model_view"]
    hop = ci["rung8"]["two_hop_group_ids"][0]
    direct = next(g for g in ci["rung8"]["impact_group_ids"] if g not in ci["rung8"]["two_hop_group_ids"])
    sp = {g["group_id"]: g["scope_phrase"] for g in mv["groups"]}
    asset = mv["asset_class_phrase"]
    ok = [{"sentence": f"{sp[hop]} that when wildfires occur, they can trip transmission lines in {asset}.", "group_ids": [hop]},
          {"sentence": f"{sp[direct]} that {ci['rung8']['broader_hazard_phrase']} can damage {asset}.", "group_ids": [direct]}]
    para = f"Fire-weather danger describes conditions that favour wildfire; it is not fire occurrence. More."
    r, rep = bi.rung8_reasons(ok, para, [("integrated", para)], ci, two_hop=True)
    assert r == [] and rep["cited_two_hop_group_ids"] == [hop] and rep["bridge_clause_count"] == 1
    bad = [{"sentence": f"{sp[hop]} that {ci['rung8']['broader_hazard_phrase']} can trip lines in {asset}.", "group_ids": [hop]}]
    r2, _ = bi.rung8_reasons(bad, "No bridge here.", [("integrated", "No bridge here.")], ci, two_hop=True)
    assert any("two-hop wording (D-073c)" in x for x in r2) and any("bridge clause (D-073c)" in x and "found 0" in x for x in r2)
    assert bi.format_class_only(r2, [])
    twice = para + " " + para
    assert any("found 2" in x for x in bi.rung8_reasons(ok, twice, [("integrated", twice)], ci, two_hop=True)[0])
    assert bi.rung8_reasons(ok, para, [("integrated", para)], ci, two_hop=False)[0] != []   # v3.3 has no two-hop exemption
    ign = [{"sentence": f"{sp[hop]} that extreme heat and wind raise the chance of ignitions near power lines in {asset}.", "group_ids": [hop]}]
    assert bi.rung8_reasons(ign, para, [("integrated", para)], ci, two_hop=True)[0] == []


def test_v34_masks_the_two_hop_phrases_in_a_fire_item_only_outside_the_prompt():
    t = "In general, research suggests that when wildfires occur, they can trip lines; wildfires can also cut output."
    assert bi.fwi_forbidden_flags(bi.mask_two_hop_phrases(t)) == []
    assert bi.fwi_forbidden_flags(bi.mask_two_hop_phrases("Wildfires spread fast.")) == ["Wildfires"]
    assert bi.TWO_HOP_RE.search("they raise the chance of ignition") and not bi.TWO_HOP_RE.search("wildfires spread")


def test_v34_equals_v33_without_two_hop_groups():
    """On a v1 packet (no two_hop_group_ids) v3.4 adds nothing to v3.3."""
    pk = json.loads(next(spi.PACKETS_DIR.glob("PK-*energy.json")).read_text(encoding="utf-8"))
    ci = pk["checks_input"]
    gid = ci["rung8"]["impact_group_ids"][0]
    g = next(x for x in pk["model_view"]["groups"] if x["group_id"] == gid)
    hz = ci["rung8"]["broader_hazard_phrase"] if ci["rung8"]["group_hazard_relation"][gid] == "broader_hazard" else ci["rung8"]["quantity_phrases"][1]
    lit = [{"sentence": f"{g['scope_phrase']} that {hz} can affect {pk['model_view']['asset_class_phrase']}.", "group_ids": [gid]}]
    a = bi.rung8_reasons(lit, "", [("integrated", "")], ci)
    b = bi.rung8_reasons(lit, "", [("integrated", "")], ci, two_hop=True)
    assert a[0] == b[0] == [] and {k: b[1][k] for k in a[1]} == a[1]


# --- B: synthesis agent v5.3 ---------------------------------------------------------------------------------------------


def test_synth_agent_v53_pins_and_prompt():
    path = TOOLS / "litsynth_agent.py"
    a = _load("litsynth_agent_v53", path)
    assert sha256_file(path) == SYNTH_V53_SHA256 and a.GENERATOR_VERSION == "litsynth_agent v5.3"
    assert a.CHECK_VERSION == bi.SYNTH_CHECK_VERSION_V34 == "synthesis_post_checks v3.4"
    assert a.sha(a.SYSTEM_PROMPT) == SYNTH_V53_PROMPT_SHA256 and a.sha(a.FORMAT_CORRECTIVE_PROMPT) == SYNTH_V53_FORMAT_SHA256
    for needle in ("TWO-HOP (D-073c)", '"two_hop_group_ids"', "when wildfires occur, they", "wildfires can",
                   "raise the chance of ignitions near power lines", '"bridge_clause"', "RUNG 8 (hazard impact on infrastructure)"):
        assert needle in a.SYSTEM_PROMPT, needle
    assert "TWO-HOP:" in a.FORMAT_CORRECTIVE_PROMPT
    assert "--packets artifacts/benchmark/synth_packets_infra_v1a" in path.read_text(encoding="utf-8")
    held = p5c.held_bytes("litsynth_agent.py")
    assert hashlib.sha256(held).hexdigest() == p5c.HELD["litsynth_agent.py"] and b'GENERATOR_VERSION = "litsynth_agent v5.2"' in held


def _obj(pk):
    mv = pk["model_view"]
    gid = pk["checks_input"]["rung8"]["impact_group_ids"][0]
    drv = next(g["group_id"] for g in mv["groups"] if g["role"] == "driver")
    pid = pk["checks_input"]["pattern_ids"][0]
    return {"prompt": mv["question_form"]["skeleton"],
            "reference_answer": {"table_pattern": [{"sentence": "S.", "pattern_ids": [pid]}],
                                 "literature_interpretation": [{"sentence": "A.", "group_ids": [gid], "hedged": True},
                                                               {"sentence": "B.", "group_ids": [drv], "hedged": False}],
                                 "integrated": "P."},
            "rubric": {"required_points": [{"point": "x", "weight": 2, "source_ids": [pid]}], "acceptable_variants": ["v"],
                       "optional_points": [], "disallowed_claims": ["d"], "fatal_errors": ["f"]},
            "guardrails": ["g"], "source_independent_answerability": "yes", "source_independence_note": "n",
            **{k: "c" for k in ("capability_tested", "system_task", "key_relationships", "evidence_needed", "desired_output_characteristics")},
            "expected_knowledge_level": "general_climate_science"}


def test_agent_v53_assembles_schema_v2a_items_with_impact_statements():
    a = _load("litsynth_agent_v53_assemble", TOOLS / "litsynth_agent.py")
    common = {"model": "m", "prompt_hash": "0" * 64, "generation_timestamp": "t", "packet_sha256": "0" * 64, "system_prompt_sha256": "0" * 64}
    for pk in PACKETS.values():
        item, _ = a.assemble(_obj(pk), pk, common, bi.column_names())
        assert item["schema_version"] == "benchmark_item_v2a"
        assert bi.schema_errors(item) == [], (pk["item_id"], bi.schema_errors(item))
        imp = [s for s in item["reference_components"]["literature_mechanisms"] if s["statement_type"] == "impact"]
        assert len(imp) == 1 and imp[0]["asset_class"] == pk["asset_class"] and isinstance(imp[0]["two_hop"], bool)
        drop = copy.deepcopy(item)
        next(s for s in drop["reference_components"]["literature_mechanisms"] if s["statement_type"] == "impact").pop("impact_outcome")
        assert any("impact_outcome" in e for e in bi.schema_errors(drop))
    v1 = json.loads(next(spi.PACKETS_DIR.glob("PK-*energy.json")).read_text(encoding="utf-8"))
    item, _ = a.assemble(_obj(v1), v1, common, bi.column_names())
    assert item["schema_version"] == "benchmark_item_v2" and any("'impact' not in" in e for e in bi.schema_errors(item))
