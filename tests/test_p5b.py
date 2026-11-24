"""Work package P5b (2026-11-23; D-073b, D-074, D-075): infra run 1 ingest, the impact grouping partitions, grouping agent
v3.1, post-checks v3.3, synthesis agent v5.2, question forms v2, DR-SEED-INFRA-1 and the rung-8 pilot selection.

The ingest is checked on the committed artifacts (the delivered tarball stays outside the repository); the partitions are
rebuilt and compared byte for byte; the agents run against the local mock server; the seed builder and the selection run
on synthetic inputs (they run on the real groups only after the Polaris grouping run, P5c).
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

import pytest

from climrr import benchmark_items as bi
from climrr import itemseeds as sd
from climrr import litgeo as lg
from climrr import litgroups_infra as lgi
from climrr import litstatements_infra1 as ir
from climrr import p5b
from climrr import seeds_infra as si
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
MAN = json.loads(ir.MANIFEST_PATH.read_text(encoding="utf-8"))
CMAN = json.loads(ir.CORPUS_MANIFEST_PATH.read_text(encoding="utf-8"))
REC = sd.read_jsonl(ir.INGESTED_PATH)
REPORT = json.loads(ir.REPORT_PATH.read_text(encoding="utf-8"))
INDEP = json.loads(ir.INDEPENDENCE_PATH.read_text(encoding="utf-8"))

GROUP_V31_SHA256 = "9c4633692c3ae92b4a51cf96ee0bb540282a33c89cac8c52e941658ec2ea1c8f"
GROUP_TEMPLATE_V3_SHA256 = "ac135f00570d75f487c7bd414a662a18c271861afa5f026e3e17b3c4fb752ae7"
GROUP_TEMPLATE_IMPACT_SHA256 = "70018280938b269fe854de6baca520bb2b84429a66ea0d7ac58520acec353925"
SYNTH_V52_SHA256 = "e057c0ff3fecc4a7fe7be29d7aa059a238b750acfaaad3b3a285bd199fedb687"
SYNTH_V52_PROMPT_SHA256 = "0753023c4ad667f8e9d429fd1873bef658fc7a7d39b1f02a7515cf60a81e578a"
SYNTH_V52_FORMAT_SHA256 = "4df7c20f7dacb9dc13708bd9607d4b0b5b2da545d57279376a2f1353422dc851"
PARTITIONS_SHA256 = "0d8f3229e06b7b2dc209c33b108b9b58d477633d9602eaa8862840ded8bc9b50"
QF2_SHA256 = "520aafa0804b5308be7e9e59b8316d9fbe0d8b60b335da4a0414ed0a17ab283e"


def _load(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- A: ingest -----------------------------------------------------------------------------------------------------------


def test_manifest_counts_are_the_run_facts():
    c = MAN["counts"]
    for k, v in ir.RUN_FACTS.items():
        assert c[k] == v, k
    assert c["by_statement_type"] == ir.BY_TYPE and c["by_recovery"] == ir.BY_RECOVERY and c["impact_candidates"] == 151
    assert MAN["generator"] == {"version": "litstatement_agent v4.1", "arm": "infra_impact_v1",
                                "system_prompt_sha256": ir.SYSTEM_PROMPT_SHA256, "reasoning_effort": "low", "max_tokens": 6000}
    assert MAN["source_commit"].startswith("157e49d") and MAN["tarball"]["sha256"] == ir.TARBALL_SHA256
    assert MAN["endpoint"] == {"endpoint_label": "sophia_vllm", "model": "openai/gpt-oss-120b", "base_url": ir.BASE_URL}


def test_copied_files_match_the_manifest_and_nothing_excluded_is_copied():
    for f in MAN["files"]:
        assert sha256_file(ir.ART / f["path"]) == f["sha256"], f["path"]
    assert len(list(ir.PAPERS_DIR.glob("*.json"))) == 572 and len(MAN["excluded_files"]) == 2 * 572
    assert not [p for p in ir.ART.rglob("*") if p.name in ir.EXCLUDED_NAMES]
    assert sha256_file(ir.ART / "statements.jsonl") == ir.STATEMENTS_SHA256 and sha256_file(ir.ART / "summary.json") == ir.SUMMARY_SHA256


def test_statement_records_and_roles():
    assert len(REC) == 407 and all(r["statement_id"].startswith("LS3-") for r in REC)
    assert all(r["statement_id"] == "LS3-" + r["agent_statement_id"][2:] for r in REC)
    assert sum(r["impact_candidate"] for r in REC) == 151
    assert all(r["impact_candidate"] == (r["precheck_status"] == "pass" and r["proposal"]["statement_type"] == "impact") for r in REC)
    assert all(r["evidence_role"] in ("core_candidate", "cited_candidate") for r in REC if r["precheck_status"] == "pass")
    assert MAN["counts"]["evidence_roles"] == {"background_consensus_candidate": 71, "cited_candidate": 26, "core_candidate": 184, "unusable": 126}


def test_run_system_prompt_is_the_agent_prompt_at_the_source_commit():
    """The run's system_prompt_sha256 (945b487c...e095; the work package abbreviates it '...9095') is the hash of the
    v4.1 agent's SYSTEM_PROMPT_INFRA, unchanged in the working tree since the source commit."""
    a = _load("litstatement_agent_v41_prompt_p5b", TOOLS / "litstatement_agent.py")
    assert hashlib.sha256(a.SYSTEM_PROMPT_INFRA.encode("utf-8")).hexdigest() == ir.SYSTEM_PROMPT_SHA256
    from climrr import litsynth_run2 as s2
    assert s2.git_blob(ir.SOURCE_COMMIT, "scripts/litcollect/litstatement_agent.py") == (TOOLS / "litstatement_agent.py").read_bytes()


def test_family_lookup_equals_the_agent():
    a = _load("litstatement_agent_v41_p5b", TOOLS / "litstatement_agent.py")
    assert {k: tuple(v) for k, v in a.INFRA_HAZARD_FAMILY.items()} == ir.AGENT_GOVERNED_TERMS
    assert {k: tuple(v) for k, v in a.INFRA_PROXY_TERMS.items()} == ir.AGENT_PROXY_TERMS
    for r in REC:
        if r.get("hazard_family"):
            assert ir.family_lookup()[r["proposal"]["hazard_term"].strip().lower()][1] == r["hazard_family"]
    assert all(r["statement_family"] for r in REC if r["precheck_status"] == "pass")


def test_breakdowns_as_reported():
    assert REPORT["passing_by_type"] == {"caveat": 1, "consensus": 3, "driver": 34, "impact": 151, "mechanism": 13, "pattern": 8}
    us = REPORT["passing_impact_naming_us_place"]
    assert us["n"] == 38 and us["by_class"] == {"nca": 2, "state": 28, "us_national": 7, "us_subregion": 1}
    none = REPORT["impact_hazard_relation_none"]
    assert len(none) == 10 and all(x["status"] == "rejected_pre_review" for x in none)
    assert sorted({x["hazard_term"] for x in none}) == ["", "fire", "fire hazard", "high wind loads", "low temperatures", "marine heat waves"]
    assert sum(REPORT["passing_impact_by_asset_family"].values()) == 151


def test_independence_v2_over_the_infra_papers():
    assert INDEP["papers_n"] == 572 and INDEP["canonical_papers_n"] == 571 and INDEP["merged_groups"] == [["210275610", "226192613"]]
    assert INDEP["rule_id"] == "DR-LIT-IND-1 v2"


def test_corpus_evidence_redacted_and_candidates_pinned():
    for f in CMAN["files"]:
        p = ir.CORPUS_DIR / f["path"]
        assert sha256_file(p) == f["sha256"]
        text = p.read_text(encoding="utf-8")
        assert "/eagl" + "e/" not in text and "/lus/" not in text
    red = json.loads(ir.REDACTIONS_PATH.read_text(encoding="utf-8"))["files"]
    assert sorted(red) == ["artifacts/literature/litcorpus03/index/index_summary.json",
                           "artifacts/literature/litcorpus03/logs/litcorpus03_index_build.log",
                           "artifacts/literature/litcorpus03/runs/infra_lexicon_v2/summary.json",
                           "artifacts/literature/litcorpus03/runs/infra_lexicon_v3/summary.json"]
    assert sha256_file(ir.CANDIDATES_PIN_PATH) == ir.QUERY_RUNS["infra_lexicon_v3"]["files"]["candidates.json"]
    from climrr.manifest import load_entry
    assert load_entry("infra_candidates_v1.json")["sha256"] == sha256_file(ir.CANDIDATES_PIN_PATH)
    assert {x["path"] for x in CMAN["not_copied"]} == set(ir.NOT_COPIED)
    assert CMAN["index"]["distinct_sha256"] == 89388 and CMAN["index"]["content_identity_sha256"].startswith("2dfc8eca")
    assert set(CMAN["query_runs"]) == {"infra_lexicon_v2", "infra_lexicon_v3"}


def test_candidates_pin_names_the_run_papers():
    c = json.loads(ir.CANDIDATES_PIN_PATH.read_text(encoding="utf-8"))
    assert c["rule"] == "DR-CAND-INFRA-3" and sorted(x["item_id"] for x in c["candidates"]) == sorted(p.stem for p in ir.PAPERS_DIR.glob("*.json"))


def test_verify_source_fails_on_a_changed_fact(tmp_path):
    """verify_source raises on the first difference: here a summary.json whose bytes differ."""
    run = tmp_path / "litstatements" / "infra_run1"
    run.mkdir(parents=True)
    (run / "statements.jsonl").write_bytes((ir.ART / "statements.jsonl").read_bytes())
    (run / "summary.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="summary.json SHA-256 differs"):
        ir.verify_source(tmp_path)


# --- B: partitions ---------------------------------------------------------------------------------------------------------


def test_partitions_rebuild_byte_identical():
    parts, _ = lgi.build_partitions(REC, INDEP, lg.Gazetteer(sd.nca_map()))
    text = "".join(json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n" for p in parts)
    assert text == lgi.PARTITIONS_PATH.read_text(encoding="utf-8")
    assert sha256_file(lgi.PARTITIONS_PATH) == PARTITIONS_SHA256


def test_partition_layout():
    parts = sd.read_jsonl(lgi.PARTITIONS_PATH)
    s = json.loads(lgi.SUMMARY_PATH.read_text(encoding="utf-8"))
    assert s["partitions"] == 11 and s["chunks"] == 12 and s["statements"] == 198 and s["impact_statements"] == 151
    assert s["merged_into_other_assets"]["heat_index"] == ["commercial_facilities", "emergency_services", "food_and_agriculture", "other",
                                                            "water_and_wastewater"]
    for p in parts:
        assert p["n_statements"] <= lgi.lgr.MAX_PARTITION
        assert all(set(x) == {"local_id", "sentence"} for x in p["statements"])
        assert (p.get("prompt_variant") == "impact_v1") == (p["statement_type"] == "impact")
        if p["statement_type"] == "impact":
            assert all({"asset_class", "impact_mechanism", "impact_outcome", "hazard_relation"} <= set(m) for m in p["meta"].values())
            k = p["asset_classes_in_partition"]
            assert p["asset_partition"] == "other_assets" or set(k) == {p["asset_partition"]}
    ids = [m["statement_id"] for p in parts for m in p["meta"].values()]
    assert len(ids) == len(set(ids)) and all(r["precheck_status"] == "pass" for r in REC if r["statement_id"] in set(ids))


# --- B: grouping agent v3.1 ------------------------------------------------------------------------------------------------


def test_group_agent_v31_pins_and_templates():
    assert sha256_file(TOOLS / "litgroup_agent.py") == GROUP_V31_SHA256
    a = _load("litgroup_agent_v31", TOOLS / "litgroup_agent.py")
    assert a.GENERATOR_VERSION == "litgroup_agent v3.1"
    assert a.sha(a.SYSTEM_PROMPT_TEMPLATE) == GROUP_TEMPLATE_V3_SHA256 and a.sha(a.SYSTEM_PROMPT_TEMPLATE_IMPACT) == GROUP_TEMPLATE_IMPACT_SHA256
    assert a.CLAIM_ABOUT_IMPACT == ("hazard_impact_on_asset",) + a.CLAIM_ABOUT
    held = _load("litgroup_agent_v3_held_p5b", p5b.materialize_tools("litgroup_agent.py") / "litgroup_agent.py")
    from climrr import litgroups as lgr
    for arm in lgr.FAMILY_PHRASE:                               # a partition without prompt_variant is sent v3's prompt
        assert a.system_prompt(lgr.FAMILY_PHRASE[arm]) == held.system_prompt(lgr.FAMILY_PHRASE[arm])
    assert "names the asset class and the impact" in a.SYSTEM_PROMPT_TEMPLATE_IMPACT
    assert hashlib.sha256(p5b.held_bytes("litgroup_agent.py")).hexdigest() == p5b.HELD["litgroup_agent.py"]


def test_group_agent_v31_end_to_end_on_an_impact_partition(tmp_path):
    pytest.importorskip("duckdb")
    import test_litgroup_agent as t
    parts = [p for p in sd.read_jsonl(lgi.PARTITIONS_PATH) if p["partition_id"] in
             ("infra_fire_weather_index.impact.transportation_systems", "infra_fire_weather_index.mechanism")]

    def reply(body):
        user = body["messages"][1]["content"]
        ids = [ln.split(":", 1)[0] for ln in user.splitlines()[1:]]
        impact = "names the asset class and the impact" in body["messages"][0]["content"]
        claim = "hazard_impact_on_asset" if impact else "hazard_change_mechanism"
        return json.dumps({"groups": [{"label": "Transportation systems are affected.", "member_ids": ids[:2], "rationale": "same",
                                       "claim_about": claim}], "singletons": [{"id": i, "claim_about": claim} for i in ids[2:]]})

    mock = t._Mock(parts=parts, reply=reply)
    pf, out = tmp_path / "p.jsonl", tmp_path / "out"
    pf.write_text("".join(json.dumps(p) + "\n" for p in parts), encoding="utf-8")
    env = {**os.environ, "TOK" + "EN": "test-value"}
    try:
        cmd = [sys.executable, str(TOOLS / "litgroup_agent.py"), "--partitions", str(pf), "--out", str(out), "--base-url", mock.url,
               "--model", "mock-model", "--source-commit", "abc1234", "--backoff", "0,0,0", "--chunk-size", "40"]
        p = subprocess.run(cmd, env=env, capture_output=True, text=True)
    finally:
        mock.server.shutdown()
    assert p.returncode == 0, p.stderr
    systems = [c[0] for c in mock.calls]
    assert sum("names the asset class and the impact" in x for x in systems) == 1
    for _, user, _ in mock.calls:                                # ids and sentences only
        assert "LS3-" not in user and not any(m["paper_item_id"] in user for q in parts for m in q["meta"].values())
    groups = [json.loads(x) for x in (out / "groups.jsonl").read_text().splitlines()]
    imp = [g for g in groups if g["statement_type"] == "impact"]
    assert imp and all(g["claim_about"] == "hazard_impact_on_asset" and g["prompt_variant"] == "impact_v1" for g in imp)
    assert all(len(g["impact_outcomes"]) == len(g["member_ids"]) == len(g["asset_classes"]) for g in imp)
    assert imp[0]["group_id"].startswith("LG-infra_fire_weather_index__transportation_systems-impact-c1-")
    assert imp[0]["checks"]["label_names_asset_class_word"] is True
    s = json.loads((out / "summary.json").read_text())
    assert s["chunks_pass"] == 2 and s["prompt_variants"] == {"v3": 1, "impact_v1": 1} and s["claim_about_fail"] == 0
    assert s["system_prompt_template_impact_sha256"] == GROUP_TEMPLATE_IMPACT_SHA256


def test_group_agent_v31_impact_claim_is_refused_outside_the_variant():
    a = _load("litgroup_agent_v31_checks", TOOLS / "litgroup_agent.py")
    part = {"statements": [{"local_id": "S001", "sentence": "Heat buckles rails."}], "meta": {"S001": {}}}
    obj = {"groups": [], "singletons": [{"id": "S001", "claim_about": "hazard_impact_on_asset"}]}
    _, _, singles = a.check_partition(obj, part)
    assert singles[0]["checks"]["failed"] == ["claim_about_pass"]
    _, _, singles = a.check_partition(obj, dict(part, prompt_variant="impact_v1"))
    assert singles[0]["checks"]["failed"] == []


# --- C: post-checks v3.3 -----------------------------------------------------------------------------------------------------


def test_wildfire_phrase_mask_d073b():
    assert bi.fwi_forbidden_flags(bi.mask_wildfire_phrase("More conditions that favour wildfire are projected.")) == []
    assert bi.fwi_forbidden_flags(bi.mask_wildfire_phrase("Wildfire risk rises; conditions that favour wildfire too.")) == ["Wildfire"]
    assert bi.fwi_forbidden_flags(bi.mask_wildfire_phrase("conditions that favor wildfire")) == ["wildfire"]   # the exact spelling only


def _rung8_input():
    return {"group_strength": {"G1": "multi_source_supported", "G2": "single_source_supported", "D1": "multi_source_supported"},
            "scope": {"groups": {"G1": {"class": "global", "stem": "In general, research"},
                                 "G2": {"class": "state", "stem": "Research on California"},
                                 "D1": {"class": "us_national", "stem": "Research on the United States"}},
                      "general_clause": "These are general drivers of dangerous heat-index days, not findings specific to California.",
                      "place_names": ["California"]},
            "rung8": {"impact_group_ids": ["G1", "G2"], "place_named_impact_group_ids": ["G2"],
                      "group_hazard_relation": {"G1": "broader_hazard", "G2": "governed_term"}, "asset_class_phrase": "rail",
                      "broader_hazard_phrase": "extreme heat, of which dangerous heat-index days are one measure",
                      "quantity_phrases": ["dangerous heat-index days"]}}


def test_rung8_reasons():
    ci = _rung8_input()
    ok = [{"sentence": "In general, research shows that extreme heat, of which dangerous heat-index days are one measure, can buckle "
                       "rail track.", "group_ids": ["G1"]}]
    every = [("prompt", "What could more dangerous heat-index days mean for rail in California, and why?")]
    assert bi.rung8_reasons(ok, "", every, ci)[0] == []
    bad = [{"sentence": "In general, research shows extreme heat buckles track.", "group_ids": ["G1"]}]
    r, _ = bi.rung8_reasons(bad, "Rail in California will fail. For rail in California, this implies more exposure to delays.",
                            every + [("integrated", "Rail in California will fail. For rail in California, this implies more exposure to delays.")], ci)
    assert any("must begin with 'In general, research shows that'" in x for x in r)
    assert any("must name the asset class 'rail'" in x for x in r) and any("must name the broader hazard" in x for x in r)
    assert any("asset-failure claim" in x for x in r) and any("place exposure" in x for x in r)
    assert bi.format_class_only(r, [])
    named = [{"sentence": "Research on California suggests that dangerous heat-index days slow rail service.", "group_ids": ["G2"]}]
    r2, rep = bi.rung8_reasons(named, "", every + [("integrated", "For rail in California, this implies more exposure to delays.")], ci)
    assert r2 == [] and rep["cited_place_named_impact_group"] is True
    wrong = every + [("rubric.fatal_errors", "Stating that rail in California will fail.")]
    assert bi.rung8_reasons(ok, "", wrong, ci)[0] == []          # a wrong-answer list may name the error


def test_v33_equals_v32_on_v5a_packets_and_masks_wildfire():
    import test_p5a_hotfix as th
    obj = th._scoped("BI-P3-0007", False)
    a = _load("litsynth_agent_v52_checks", TOOLS / "litsynth_agent.py")
    common = {"model": "m", "prompt_hash": "0" * 64, "generation_timestamp": "t", "packet_sha256": "0" * 64, "system_prompt_sha256": "0" * 64}
    pk = th.PK5A["BI-P3-0007"]
    item, tagged = a.assemble(obj, pk, common, bi.column_names())
    r32 = bi.synthesis_post_checks(item, tagged, pk["checks_input"], bi.column_names(), check_version=bi.SYNTH_CHECK_VERSION_V32)
    r33 = bi.synthesis_post_checks(item, tagged, pk["checks_input"], bi.column_names(), check_version=bi.SYNTH_CHECK_VERSION_V33)
    assert r32["pass"] and r33["pass"] and "rung8_report" not in r33["checks"]
    obj2 = copy.deepcopy(obj)
    obj2["reference_answer"]["table_pattern"][0]["sentence"] += " Conditions that favour wildfire become more common."
    item2, tagged2 = a.assemble(obj2, pk, common, bi.column_names())
    f32 = bi.synthesis_post_checks(item2, tagged2, pk["checks_input"], bi.column_names(), check_version=bi.SYNTH_CHECK_VERSION_V32)
    f33 = bi.synthesis_post_checks(item2, tagged2, pk["checks_input"], bi.column_names(), check_version=bi.SYNTH_CHECK_VERSION_V33)
    assert any("fire-weather wording" in x for x in f32["reasons"]) and not any("fire-weather wording" in x for x in f33["reasons"])


# --- C: synthesis agent v5.2, question forms v2 ----------------------------------------------------------------------------


def test_synth_agent_v52_pins_and_prompt():
    path = TOOLS / "litsynth_agent.py"
    a = _load("litsynth_agent_v52", path)
    assert sha256_file(path) == SYNTH_V52_SHA256 and a.GENERATOR_VERSION == "litsynth_agent v5.2"
    assert a.CHECK_VERSION == "synthesis_post_checks v3.3"
    assert a.sha(a.SYSTEM_PROMPT) == SYNTH_V52_PROMPT_SHA256 and a.sha(a.FORMAT_CORRECTIVE_PROMPT) == SYNTH_V52_FORMAT_SHA256
    for needle in ("RUNG 8 (hazard impact on infrastructure)", '"place_named_impact_group_ids"', "this implies more exposure to",
                   "will fail, is at risk", "WILDFIRE (D-073b)", '"conditions that favour wildfire"', "SCOPE (where the research comes from)"):
        assert needle in a.SYSTEM_PROMPT, needle
    assert "RUNG 8:" in a.FORMAT_CORRECTIVE_PROMPT
    held = p5b.held_bytes("litsynth_agent.py")
    assert b'GENERATOR_VERSION = "litsynth_agent v5.1"' in held


def test_question_forms_v2():
    f = si.load_question_forms_v2()
    assert f["sha256"] == QF2_SHA256
    from climrr.manifest import load_entry
    assert load_entry("question_forms_v2.yaml")["sha256"] == QF2_SHA256
    v1 = sd_forms = __import__("climrr.synthpackets_v5", fromlist=["x"]).load_question_forms()
    assert f["forms"][:8] == sd_forms["forms"] and v1["version"] == "question_forms_v1"
    r8 = si.rung8_forms(f)
    assert [x["id"] for x in r8] == ["QF-08", "QF-09", "QF-10"]
    assert r8[1]["skeleton"] == "What could a {change} in {hazard_phrase} mean for {asset_class} in {place}, and why?"
    assert r8[2]["skeleton"] == "Why does {hazard_phrase} matter for {asset_class}, and how is it projected to change in {place}?"


# --- C: DR-SEED-INFRA-1 and the selection (synthetic) ----------------------------------------------------------------------


def _pattern(pid, fam, state, value, metric=None):
    st = si.TABLE_SETTING[fam]
    return {"seed_id": f"SD2-{pid}", "working_assumptions": [], "pattern": {
        "pattern_id": pid, "family": fam, "pattern_kind": "single", "geography_type": "state", "geography": state,
        "metric": metric or st["metric"], "statistic": st["statistic"], "horizon": st["horizon"], "status": "computed",
        "acceptance_blocked": False, "computed_value_or_range": {"value": str(value)}}}


def _rec(sid, paper, fam, asset, region, scope, role="core_candidate", stype="impact", rel="broader_hazard"):
    return {"statement_id": sid, "paper_item_id": paper, "precheck_status": "pass", "evidence_role": role,
            "statement_family": fam, "impact_candidate": stype == "impact", "hazard_relation": rel if stype == "impact" else None,
            "proposal": {"statement_type": stype, "asset_class": asset, "region": region, "region_scope": scope, "passage_type": "own_finding"}}


SEEDS_V3 = [_pattern("TP1-1", "heat_index", "California", 10), _pattern("TP1-2", "heat_index", "Texas", 30),
            _pattern("TP1-3", "heat_index", "Arizona", 50), _pattern("TP1-4", "heat_index", "Texas", 99, metric="heatindex_days_above_105F"),
            _pattern("TP1-5", "fire_weather_index", "California", 2)]
RECS = [_rec("LS3-1-01", "1", "heat_index", "energy", "Texas", "subnational"),
        _rec("LS3-2-01", "2", "heat_index", "energy", "Malaysia", "national"),
        _rec("LS3-3-01", "3", "heat_index", "energy", "United States", "national"),
        _rec("LS3-4-01", "4", "heat_index", "transportation_systems", "unknown", "unknown"),
        _rec("LS3-5-01", "5", "fire_weather_index", "energy", "global", "global", rel="governed_term")]
GROUPS = [{"group_id": "G-heat-energy-1", "statement_type": "impact", "claim_about": "hazard_impact_on_asset",
           "member_ids": ["LS3-1-01", "LS3-2-01"]},
          {"group_id": "G-heat-energy-2", "statement_type": "impact", "claim_about": "hazard_impact_on_asset", "member_ids": ["LS3-3-01"]},
          {"group_id": "G-heat-transport", "statement_type": "impact", "claim_about": "hazard_impact_on_asset", "member_ids": ["LS3-4-01"]},
          {"group_id": "G-heat-other", "statement_type": "impact", "claim_about": "impact_or_exposure", "member_ids": ["LS3-4-01"]},
          {"group_id": "G-fire-energy", "statement_type": "impact", "claim_about": "hazard_impact_on_asset", "member_ids": ["LS3-5-01"]}]


def _ctx():
    indep = {"papers": [{"item_id": str(i), "canonical_id": str(i)} for i in range(1, 6)]}
    return si.Context(RECS, indep, lg.Gazetteer(sd.nca_map()))


def test_dr_seed_infra_1():
    ctx = _ctx()
    seeds = si.build_seeds(SEEDS_V3, GROUPS, ctx, rung3_driver_ids=lambda s: [f"D-{s['pattern']['pattern_id']}"])
    by = {(s["family"], s["place"], s["asset_class"]): s for s in seeds}
    assert ("heat_index", "Texas", "energy") in by and ("heat_index", "California", "food_and_agriculture") not in by
    tx = by[("heat_index", "Texas", "energy")]
    assert [x["group_id"] for x in tx["impact_groups"]] == ["G-heat-energy-1", "G-heat-energy-2"]
    assert tx["impact_groups"][0]["relevance"] == "place_named" and tx["place_named_impact_group_ids"] == ["G-heat-energy-1"]
    assert tx["impact_groups"][0]["evidence_strength"] == "multi_source_supported" and not tx["needs_general_clause"]
    ca = by[("heat_index", "California", "energy")]
    assert [x["relevance"] for x in ca["impact_groups"]] == ["us", "us"] and ca["needs_general_clause"]
    assert by[("heat_index", "Arizona", "transportation_systems")]["impact_groups"][0]["relevance"] == "general"
    assert by[("fire_weather_index", "California", "energy")]["impact_groups"][0]["relevance"] == "general"
    assert tx["driver_group_ids"] == ["D-TP1-2"] and tx["pattern_id"] == "TP1-2"         # the 95 F pattern, not the 105 F one
    assert all("G-heat-other" not in [x["group_id"] for x in s["impact_groups"]] for s in seeds)
    assert [s["seed_rank"] for s in seeds] == list(range(1, len(seeds) + 1))


def test_rung8_pilot_selection():
    ctx = _ctx()
    seeds = si.build_seeds(SEEDS_V3, GROUPS, ctx)
    sel = si.select_pilot(seeds, SEEDS_V3, RECS, ctx, si.load_question_forms_v2())
    cells = {(x["family"], x["asset_class"]): x for x in sel["selected"]}
    he = cells[("heat_index", "energy")]
    assert he["state"] == "Texas" and he["candidate_states"] == ["Texas"] and he["seed_id"] == "SD8-TP1-2-energy"
    ht = cells[("heat_index", "transportation_systems")]
    assert ht["state"] == "California" and ht["state_basis"].startswith("fallback")
    assert cells[("fire_weather_index", "energy")]["state"] == "California"
    assert [x["question_form_id"] for x in sel["selected"]] == ["QF-08", "QF-09", "QF-10"]
    assert {(m["family"], m["asset_class"]) for m in sel["missing"]} == {
        ("heat_index", "water_and_wastewater"), ("heat_index", "healthcare_and_public_health"),
        ("fire_weather_index", "transportation_systems"), ("fire_weather_index", "emergency_services"), ("fire_weather_index", "communications")}


def test_place_named_states_on_the_real_ingest():
    """The states a passing impact statement names, per pilot cell (litgeo v2); the selection picks among these in P5c."""
    ctx = si.Context(REC, INDEP, lg.Gazetteer(sd.nca_map()))
    got = {f"{f}|{a}": si.place_named_states(REC, ctx, f, a) for f, a in si.PILOT_CELLS}
    assert all(isinstance(v, list) for v in got.values())
    assert sum(len(v) for v in got.values()) >= 1
