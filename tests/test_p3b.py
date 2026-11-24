"""Work package P3b (D-066, D-067): the synthesis run-4 / polish run-1 ingest, DR-DESC-1 v4, packets v4b, post-checks v3.1,
synthesis agent v4.1, polish checks v2 and polish agent v1.1.

Checks the ingested copy (the tarball stays outside the repository): every manifest hash; the run facts; six items in
human_review (run-4 record + its polish event + the lifecycle step, text unchanged) and BI-P3-0007 rejected_pre_review;
post-checks v3 reproduced against packets v4a at the source commit; polish checks v1a reproduced from the polish events;
the checks-v2 replay rebuilt. Then the v4 descriptors (Washington "remaining rare", Minnesota), packets v4b rebuilt in memory
and compared byte-for-byte, the v3.1 rules on the run-4 texts and on unit cases, the v4.1 agent against a local mock server,
and checks v2 on unit cases. No model call.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from decimal import Decimal

import pytest

from climrr import benchmark_items as bi
from climrr import itemseeds as sd
from climrr import litsynth_run2 as s2
from climrr import litsynth_run4 as s4
from climrr import pattern_descriptors as pd
from climrr import plain_language as pl
from climrr import polish_checks as pc
from climrr import synthpackets_v4 as v4
from climrr.checksums import sha256_file
from climrr.manifest import load_entry
from climrr.paths import REPO_ROOT

MAN = json.loads(s4.MANIFEST_PATH.read_text(encoding="utf-8"))
PMAN = json.loads(s4.POLISH_MANIFEST_PATH.read_text(encoding="utf-8"))
V4B = json.loads((v4.PACKETS_V4B_DIR / "manifest.json").read_text(encoding="utf-8"))
PACKETS = {p["item_id"]: json.loads((v4.PACKETS_V4B_DIR / f"{p['packet_id']}.json").read_text(encoding="utf-8"))
           for p in V4B["packets"]}
WORK_TOOLS = REPO_ROOT / "scripts" / "litcollect"
from climrr import p5a  # noqa: E402
AGENT41 = p5a.materialize_tools("litsynth_agent.py") / "litsynth_agent.py"   # v4.1 held at the P5a base commit (v5 since P5a)
POLISH11 = WORK_TOOLS / "litpolish_agent.py"
AGENT41_SHA256 = "f41c0b9537912779076bfac81e1341f94e07bd87723177cc583350ce164d33d7"
SYSTEM_PROMPT41_SHA256 = "8ce96b076ee0f9366a25cc6caf50a72cd034c821f567f69b777ad4947481c8ab"
FORMAT_CORRECTIVE41_SHA256 = "41eac0f7b03b4d9e33726161638510f022f8f9c8526af09b4feb9ff2ee6ae8f0"
POLISH11_SHA256 = "6abc7b2b46298934682bf8342793e185cc73b85d69b505ef61e6cbe0c374366e"
POLISH11_PROMPT_SHA256 = "2dbbce7f345fdcdeccd4661c22f5c22d87e6c4bcaa070856b59e6234093f0a18"
RULES_V4_SHA256 = "dbfa8fd8a86a9379b4709b998bb33e673dceafd5f8ba7d199d55ff672d4c282d"
SYNONYMS_V2_SHA256 = "7d55d33ca1ca6212341ef06f3a2857f3bfd145ac637e667deb42955fa2267b2b"
PASSING = ["BI-P3-0001", "BI-P3-0002", "BI-P3-0003", "BI-P3-0004", "BI-P3-0005", "BI-P3-0008"]


def _items():
    return {x["item_id"]: json.loads((s4.ART / x["path"]).read_text(encoding="utf-8")) for x in MAN["items_ingested"]}


def _load(name, path):
    pytest.importorskip("duckdb")
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run4_records():
    """The run-4 records in the agent's key order (`items.jsonl` sorts keys, which reorders the rubric lists): the ingested
    item files with the polish and lifecycle events removed."""
    out = []
    for iid, it in sorted(_items().items()):
        x = copy.deepcopy(it)
        if iid != "BI-P3-0007":
            x["review"]["status"] = "deterministic_pass"
            x["review"]["history"] = x["review"]["history"][:1]
        out.append(x)
    return out


def _cand(item):
    x = copy.deepcopy(item)
    x["review"] = {"status": "llm_candidate", "history": [], "kaiyuan_disposition": None, "mentor_disposition": None, "final_frozen": None}
    return x


def _v31(item, tagged, pk):
    return bi.synthesis_post_checks(_cand(item), tagged, pk["checks_input"], bi.column_names(), check_version=bi.SYNTH_CHECK_VERSION_V31)


# --- A: the ingest ------------------------------------------------------------------------------------------------


def test_every_manifest_file_matches_its_hash():
    for base, man in ((s4.ART, MAN), (s4.POLISH_ART, PMAN)):
        for f in man["files"]:
            assert sha256_file(base / f["path"]) == f["sha256"], f["path"]
    for x in MAN["items_ingested"]:
        assert sha256_file(s4.ART / x["path"]) == x["sha256"], x["path"]
    assert sha256_file(s4.ART / "items.jsonl") == MAN["items_sha256"] == s4.ITEMS_SHA256
    assert sha256_file(s4.POLISH_ART / "summary.json") == PMAN["summary_sha256"] == s4.POLISH_SUMMARY_SHA256
    assert sha256_file(s4.POLISH_ART / "polished.jsonl") == PMAN["polished_sha256"] == s4.POLISHED_SHA256
    assert MAN["tarball"]["sha256"] == PMAN["tarball"]["sha256"] == s4.TARBALL_SHA256 == \
        "ebd502ac7aaea764a86a40501d5b5347d8372164f9b17a28d0299ebf55fb7168"
    assert MAN["packets"]["manifest_sha256"] == s4.PACKETS_MANIFEST_SHA256 == sha256_file(v4.PACKETS_V4A_DIR / "manifest.json")
    assert MAN["source_commit"] == PMAN["source_commit"] == s4.SOURCE_COMMIT
    for rel, sha in ((s4.AGENT_REL, s4.AGENT_SHA256), (s4.POLISH_AGENT_REL, s4.POLISH_AGENT_SHA256)):
        assert hashlib.sha256(s2.git_blob(s4.SOURCE_COMMIT, rel)).hexdigest() == sha


def test_run_facts_and_lifecycle():
    assert MAN["counts"] == s4.RUN_FACTS and PMAN["counts"] == s4.POLISH_FACTS
    assert MAN["checks_reproduced"] is True and PMAN["checks_reproduced"] is True
    assert MAN["format_corrective_items"] == ["BI-P3-0003", "BI-P3-0004"] and MAN["rejected_pre_review"] == s4.REJECTED
    items, run = _items(), {it["item_id"]: it for it in s2.read_items(s4.ART / "items.jsonl")}
    recs = {r["item_id"]: r for r in s2.read_items(s4.POLISH_ART / "polished.jsonl")}
    assert sorted(items) == sorted(run) == sorted(PASSING + ["BI-P3-0007"]) and sorted(recs) == PASSING
    for iid, it in items.items():
        r = it["review"]
        if iid == "BI-P3-0007":
            assert it == run[iid] and r["status"] == "rejected_pre_review"
            continue
        assert r["status"] == "human_review" and r["kaiyuan_disposition"] is None and r["final_frozen"] is None
        assert [h["event"] for h in r["history"]] == ["deterministic_pass", "polish", "human_review"]
        assert r["history"][2]["at"] == MAN["ingested_at"] and r["history"][2]["decision"] == "D-033"
        ev = r["history"][1]
        assert ev["status"] == "polish_rejected" and ev["pre_polish"] == recs[iid]["pre_polish"] and ev["rewrite"] == recs[iid]["polished"]
        before = copy.deepcopy(it)
        before["review"]["status"] = "deterministic_pass"
        before["review"]["history"] = before["review"]["history"][:1]
        assert before == run[iid]                                                    # nothing else changed: the text is run 4's
        assert it["prompt"] == ev["pre_polish"]["prompt"] and it["reference_answer"]["integrated"] == ev["pre_polish"]["answer"]
        assert bi.schema_errors(it) == [] and bi.consistency_errors(it) == []


def test_synthesis_checks_reproduce_against_packets_v4a():
    items = _run4_records()
    assert sorted(items, key=lambda x: x["item_id"]) == sorted(s2.read_items(s4.ART / "items.jsonl"), key=lambda x: x["item_id"])
    rep = s4.reproduce_synthesis(items)
    order = [x["item_id"] for x in MAN["checks"]["items"]]
    assert sorted(rep["items"], key=lambda x: order.index(x["item_id"])) == MAN["checks"]["items"]
    assert rep["checks_reproduced"] and rep["check_version"] == MAN["checks"]["check_version"] == "synthesis_post_checks v3"
    by = {x["item_id"]: x for x in rep["items"]}
    assert by["BI-P3-0007"]["reasons"] == s4.REJECTED["BI-P3-0007"] and not by["BI-P3-0007"]["pass"]
    assert [i for i, x in sorted(by.items()) if x["first_check_reasons"]] == ["BI-P3-0003", "BI-P3-0004"]


def test_polish_checks_reproduce_and_the_v2_replay():
    """From the ingested polish events: v1a reproduces the recorded reasons; v2 equals the manifest's replay."""
    agent = s4.load_agent_at(s4.SOURCE_COMMIT, s4.POLISH_AGENT_REL, s4.POLISH_AGENT_SHA256, "litpolish_agent_v1_test")
    items, nca, cols = _items(), sd.nca_map(), bi.column_names()
    syn1, syn2 = pc.load_synonyms(), pc.load_synonyms_v2()
    rules, plain = pd.load_rules(pd.RULES_V4_PATH), pl.load(pl.PLAIN_V1A_PATH)
    recs = {r["item_id"]: r for r in s2.read_items(s4.POLISH_ART / "polished.jsonl")}
    replay = {x["item_id"]: x for x in PMAN["replay_checks_v2"]["items"]}
    for iid in PASSING:
        ev = items[iid]["review"]["history"][1]
        obj = agent.extract(ev["raw_response"])
        assert {"prompt": obj["prompt"], "answer": obj["answer"]} == ev["rewrite"]
        v1 = pc.invariance(ev["pre_polish"], ev["rewrite"], agent.cited_labels(items[iid]), nca, syn1, cols)
        assert v1["reasons"] == recs[iid]["reasons"] and v1["checks"] == recs[iid]["checks"]
        v2 = pc.invariance_v2(ev["pre_polish"], ev["rewrite"], s4._cited(items[iid]), nca, syn2, rules, plain, cols)
        assert {"item_id": iid, "pass": v2["pass"], "reasons": v2["reasons"]} == replay[iid]
    # The EXECUTOR reading (report section 51): 0001, 0003, 0004 changed wording that carries meaning; 0002, 0005, 0008 did not.
    assert {i: x["pass"] for i, x in replay.items()} == {"BI-P3-0001": False, "BI-P3-0002": True, "BI-P3-0003": False,
                                                         "BI-P3-0004": False, "BI-P3-0005": True, "BI-P3-0008": True}
    assert any("50.0" in r for r in replay["BI-P3-0001"]["reasons"])                  # "about 50 %" for "a moderate increase"
    assert all(r["pre_polish"]["prompt"] == r["polished"]["prompt"] for r in recs.values())   # run 1 never touched a question


def test_the_runs_reason_kinds_are_what_the_work_package_states():
    recs = s2.read_items(s4.POLISH_ART / "polished.jsonl")
    kinds = [r.split(":")[1].strip().split(" ")[0] for x in recs for r in x["reasons"]]
    assert {k: kinds.count(k) for k in set(kinds)} == {"mechanism": 12, "numbers": 2}


# --- B: DR-DESC-1 v4 -------------------------------------------------------------------------------------------------


def _rules():
    return pd.load_rules(pd.RULES_V4_PATH)


def _pat(mf, mt, family="heat_index", rm=None, metric="heatindex_days_x", direction="increase"):
    return {"pattern_id": "TP-X", "pattern_kind": "single_place", "family": family, "metric": metric, "direction": direction,
            "horizon": "mid", "horizon_window": "2045-2054", "scenario": "RCP8.5", "season": "summer",
            "computed_value_or_range": {"mean_from": mf, "mean_to": mt}, "relative_magnitude": rm}


def test_rules_v4_pinned():
    assert sha256_file(pd.RULES_V4_PATH) == load_entry(pd.RULES_V4_PATH.name)["sha256"] == RULES_V4_SHA256
    r = _rules()
    assert r["rule"] == "DR-DESC-1 v4" and r["decision"] == "D-066"
    assert r["magnitude"]["classes"][0]["forms"][:4] == ["a slight increase", "increase slightly", "slightly higher", "a small rise"]
    assert r["magnitude"]["classes"][2]["forms"] == ["roughly double", "about twice as many", "roughly doubling"]
    assert r["magnitude"]["remaining_rare"]["forms"] == ["remain rare", "stay rare", "remaining rare"]


def test_washington_remains_rare_and_minnesota():
    wa, mn = PACKETS["BI-P3-0003"], PACKETS["BI-P3-0008"]
    d = wa["model_view"]["patterns"][0]["allowed_descriptors"]
    assert d["magnitude_class"] == "remaining rare" and d["magnitude_forms"] == ["remain rare", "stay rare", "remaining rare"]
    assert d["anchor_pair"] == "from essentially none to about 1 day a summer" and d["tercile"] is None
    assert d["tercile_forms"] == ["a smaller change than in most states", "among the states with the smallest changes"]
    d = mn["model_view"]["patterns"][0]["allowed_descriptors"]
    assert d["magnitude_class"] == "a slight increase" and d["anchor_pair"] is None and d["anchors"] == []
    assert d["tercile_class"] == "moderate" and d["tercile_forms"][0] == "a change similar to most states"
    assert d["quantity"] == "fire-weather danger (how hot, dry and windy conditions favour fire)"


@pytest.mark.parametrize("mf,mt,cls", [("1.9", "10.0", "rising from rare to common"), ("1.9", "9.9", "remaining rare"),
                                       ("0.0", "0.4", "remaining rare"), ("2.0", "30.0", "more than tripling"),
                                       ("15.0", "24.0", "a moderate increase"), ("10.0", "30.0", "roughly tripling")])
def test_rare_rule_and_ratio_classes(mf, mt, cls):
    assert pd.descriptors(_pat(mf, mt), _rules())["magnitude_class"] == cls


def test_v4_singular_anchor_and_fwi_ratio_only():
    d = pd.descriptors(_pat("1.4", "1.2", direction="decrease"), _rules())   # a decrease: no class (no decrease rule)
    assert d["magnitude_class"] is None
    d = pd.descriptors(_pat("0.3", "1.4"), _rules())
    assert d["anchor_pair"] == "from essentially none to about 1 day a summer"
    d = pd.descriptors(_pat("31.4", "33.6", family="fire_weather_index", metric="fwi_x",
                            rm={"class": "large", "definition": "x"}), _rules())
    assert d["magnitude_class"] == "a slight increase" and d["anchor_pair"] is None and d["tercile_class"] == "large"
    assert "rise slightly" in pd.phrases(d) and "a larger change than in most states" in pd.phrases(d)
    assert not any("tercile" in x for x in pd.phrases(d))


def test_v3_output_unchanged():
    v3 = pd.load_rules(pd.RULES_V3_PATH)
    d = pd.descriptors(_pat("0.04", "0.82"), v3, pl.load(pl.PLAIN_V1A_PATH))
    assert d["magnitude_class"] == "rising from rare to common" and "magnitude_forms" not in d


# --- packets v4b -----------------------------------------------------------------------------------------------------


def test_packets_v4b_rebuild_byte_identically():
    b = v4.build_selection(variant="v4b")
    assert [pk["item_id"] for pk in b["packets"]] == [p["item_id"] for p in V4B["packets"]]
    for pk in b["packets"]:
        assert (v4.PACKETS_V4B_DIR / f"{pk['packet_id']}.json").read_text(encoding="utf-8") == \
            json.dumps(pk, indent=2, ensure_ascii=False) + "\n"
    for p in V4B["packets"]:
        assert sha256_file(v4.PACKETS_V4B_DIR / f"{p['packet_id']}.json") == p["sha256"]
    assert V4B["inputs_sha256"] == b["hashes"] and b["hashes"]["descriptor_rules"] == RULES_V4_SHA256
    assert V4B["base"]["manifest_sha256"] == sha256_file(v4.PACKETS_V4A_DIR / "manifest.json")


def test_packets_v4b_differ_from_v4a_only_as_intended():
    allowed_top = {"version", "descriptor_rule", "descriptor_rules_sha256"}
    for iid, b in PACKETS.items():
        a = json.loads((v4.PACKETS_V4A_DIR / f"{b['packet_id']}.json").read_text(encoding="utf-8"))
        assert {k for k in a if a[k] != b.get(k)} - {"model_view", "checks_input", "inputs_sha256"} == allowed_top
        assert {k: v for k, v in a["inputs_sha256"].items() if k != "descriptor_rules"} == \
            {k: v for k, v in b["inputs_sha256"].items() if k != "descriptor_rules"}
        assert a["provenance"] == b["provenance"] and a["excluded_groups"] == b["excluded_groups"]
        assert a["model_view"]["groups"] == b["model_view"]["groups"] and a["checks_input"]["allowed_numbers"] == b["checks_input"]["allowed_numbers"]
        assert set(b["model_view"]) - set(a["model_view"]) == {"must_not_use"}
        assert set(b["checks_input"]) - set(a["checks_input"]) <= {"group_role", "regions"}
        assert b["checks_input"]["group_role"] == {g["group_id"]: g["role"] for g in b["provenance"]["groups"]}
        text = b["model_view"]["patterns"][0]["text"]
        d = b["model_view"]["patterns"][0]["allowed_descriptors"]
        assert "tercile" not in text and not any("tercile" in x for x in pd.phrases(d)) and d["tercile"] is None
        assert "tercile" in b["model_view"]["must_not_use"] and "RCP" in b["model_view"]["must_not_use"]
        assert ("fires" in b["model_view"]["must_not_use"]) == (b["family"] == "fire_weather_index")
    assert PACKETS["BI-P3-0005"]["checks_input"]["regions"][0] == "Southeast" and \
        PACKETS["BI-P3-0005"]["checks_input"]["regions"][-1] == "Alaska"


# --- C: post-checks v3.1 ---------------------------------------------------------------------------------------------


def test_v31_catches_the_run4_readability_errors_and_v3_does_not_change():
    items = {it["item_id"]: it for it in s2.read_items(s4.ART / "items.jsonl")}
    reasons, reports = {}, {}
    for iid, it in items.items():
        h = it["review"]["history"][0]
        pk = PACKETS[iid]
        r = _v31(it, h["reference_answer_tagged"], pk)
        v3 = bi.synthesis_post_checks(_cand(it), h["reference_answer_tagged"], pk["checks_input"], bi.column_names(),
                                      check_version=bi.SYNTH_CHECK_VERSION_V3)
        assert v3["reasons"] == h["reasons"] or iid == "BI-P3-0007"                    # v3 on v4b packets: unchanged verdicts
        reasons[iid] = [x for x in r["reasons"] if x not in v3["reasons"]]
        reports[iid] = r["checks"]
    assert any("doubled magnitude phrase" in x and "'increase by a slight increase'" in x for x in reasons["BI-P3-0008"])
    assert any("doubled magnitude phrase" in x for x in reasons["BI-P3-0007"])
    assert any("tercile wording" in x and "'ranking large'" in x for x in reasons["BI-P3-0004"])
    assert any("lower-case letter: 'research shows" in x for x in reasons["BI-P3-0002"] + reasons["BI-P3-0003"])
    assert not any("states by late" in x for xs in reasons.values() for x in xs)        # "U.S. states" does not end a sentence
    assert reasons["BI-P3-0001"] == [] and reasons["BI-P3-0005"] == []
    for iid in ("BI-P3-0002", "BI-P3-0003", "BI-P3-0004", "BI-P3-0008"):
        assert bi.format_class_only(reasons[iid], PACKETS[iid]["checks_input"]["allowed_descriptors"]), iid
    # D-067: the heat index listed among the drivers (paragraph; reported), the regional contrast claimed to be explained
    assert [c["field"] for c in reports["BI-P3-0004"]["context_driver_report"]] == ["integrated"]
    assert [c["field"] for c in reports["BI-P3-0005"]["context_driver_report"]] == ["integrated"]
    assert reports["BI-P3-0005"]["regional_contrast_report"][0]["field"] == "prompt"
    assert reports["BI-P3-0005"]["regional_contrast_report"][0]["regions_not_named_by_a_cited_group"] == ["Southeast", "Alaska"]


def _ctx_case(sentence):
    pk = PACKETS["BI-P3-0004"]
    ctx = next(g for g, r in pk["checks_input"]["group_role"].items() if r == "context")
    item = {"prompt": "How?", "rubric": {}}
    tagged = {"table_pattern": [], "literature_interpretation": [{"sentence": sentence, "group_ids": [ctx], "hedged": False}],
              "integrated": ""}
    return bi.readability_reasons("How?", [], tagged["literature_interpretation"], "", [], pk["checks_input"]), item


@pytest.mark.parametrize("sentence,hit", [
    ("Research has shown that the heat index is a driver of the increase because it combines temperature and humidity.", True),
    ("Research has shown that the change is driven by the heat index combining temperature and humidity.", True),
    ("Because the heat index combines temperature and humidity, research has shown it tracks perceived heat.", False),
    ("Research has shown that the heat index combines temperature and humidity as a perceived-heat metric.", False)])
def test_context_as_driver(sentence, hit):
    reasons, _ = _ctx_case(sentence)
    assert any("context_as_driver (D-067)" in r for r in reasons) is hit
    assert all(bi.format_class_only([r], []) for r in reasons)


def test_v31_unit_rules():
    rr = lambda t: bi.readability_reasons(t, [], [], "", [("integrated", t)], {})  # noqa: E731
    assert rr("Danger is projected to increase a slight increase.") and rr("Days increase by a moderate increase.")
    assert rr("Fire-weather danger is projected to increase slightly.") == []
    assert rr("It is in the upper tercile.") and rr("The state is ranking large.") and rr("A larger change than in most U.S. states.") == []
    assert bi.lower_case_starts("Research shows this. research suggests that. In the U.S. states rise. e.g. one.") == \
        ["research suggests that.", "e.g. one."]
    assert bi.SYNTH_CHECK_VERSION == "synthesis_post_checks v2.2"                       # the default stays


# --- C: the synthesis agent v4.1 -------------------------------------------------------------------------------------


def test_agent_v41_pinned_and_prompt():
    assert sha256_file(AGENT41) == AGENT41_SHA256
    a = _load("litsynth_agent_v4_1", AGENT41)
    assert a.GENERATOR_VERSION == "litsynth_agent v4.1" and a.CHECK_VERSION == "synthesis_post_checks v3.1"
    assert hashlib.sha256(a.SYSTEM_PROMPT.encode("utf-8")).hexdigest() == SYSTEM_PROMPT41_SHA256
    assert hashlib.sha256(a.FORMAT_CORRECTIVE_PROMPT.encode("utf-8")).hexdigest() == FORMAT_CORRECTIVE41_SHA256
    for needle in ('"increase a slight increase" and "increase by a slight increase" are errors', "starts with a capital letter",
                   'whose "role" is "context"', "never in a list of drivers or causes", "REGIONAL CONTRASTS",
                   '"must_not_use"', '"acceptable_variants", "optional_points", "disallowed_claims" and "fatal_errors"',
                   '"tercile_forms"'):
        assert needle in a.SYSTEM_PROMPT, needle
    assert "must_not_use" in a.FORMAT_CORRECTIVE_PROMPT and "capital letter" in a.FORMAT_CORRECTIVE_PROMPT


def _reply41(pk, integrated_extra=""):
    """A v4.1-style reply for the California heat packet v4b: one magnitude form, capitals, the comparison form."""
    d = pk["model_view"]["patterns"][0]["allowed_descriptors"]
    pid = pk["checks_input"]["pattern_ids"][0]
    roles = pk["checks_input"]["group_role"]
    strengths = pk["checks_input"]["group_strength"]
    drv = next(g for g in roles if roles[g] == "driver" and strengths[g] != "single_source_supported")
    return {
        "prompt": "How are days hot and humid enough to be dangerous projected to change in California by mid-century under a "
                  "high-emissions future, and what drives that change?",
        "reference_answer": {
            "table_pattern": [{"sentence": f"In California, days hot and humid enough to be dangerous show {d['magnitude_forms'][0]} "
                                           f"by mid-century under a high-emissions future, {d['tercile_forms'][0]}.", "pattern_ids": [pid]}],
            "literature_interpretation": [{"sentence": "Research shows that large-scale warming drives increases in extreme heat.",
                                           "group_ids": [drv], "hedged": False}],
            "integrated": "Dangerous humid-heat days show a moderate increase in California by mid-century under a high-emissions "
                          "future. Research shows that large-scale warming drives the increase." + integrated_extra},
        "rubric": {"required_points": [{"point": "states that such days increase", "weight": 3, "source_ids": [pid]},
                                       {"point": "gives the size as a moderate increase", "weight": 2, "source_ids": [pid]},
                                       {"point": "places the change in California", "weight": 1, "source_ids": [pid]},
                                       {"point": "names large-scale warming as the driver", "weight": 2, "source_ids": [drv]}],
                   "acceptable_variants": ["about half again as many dangerous days"],
                   "optional_points": [{"point": d["anchor_pair"], "source_ids": [pid]},
                                       {"point": "Exact values are not required; any statement consistent with the magnitude class counts.",
                                        "source_ids": [pid]}],
                   "disallowed_claims": ["presents the projection as a forecast"],
                   "fatal_errors": ["says such days decrease", "treats the modeled historical baseline as an observation"]},
        "guardrails": list(pk["model_view"]["guardrails"]),
        "source_independent_answerability": "yes", "source_independence_note": "A general regional climate question.",
        "capability_tested": "joins a projected pattern to its driver", "system_task": "explains the projected change",
        "key_relationships": "heat index, warming", "evidence_needed": "direction; driver",
        "desired_output_characteristics": "direction, size, driver", "expected_knowledge_level": "general_climate_science"}


def _run41(tmp_path, replies):
    helpers = _load("test_litsynth_agent_v4_helpers_p3b", REPO_ROOT / "tests" / "test_litsynth_agent_v4.py")
    pdir, out = tmp_path / "packets", tmp_path / "out"
    pdir.mkdir()
    for pid in replies:
        (pdir / f"{pid}.json").write_text((v4.PACKETS_V4B_DIR / f"{pid}.json").read_text(encoding="utf-8"), encoding="utf-8")
    mock = helpers._Mock(replies)
    try:
        p = subprocess.run([sys.executable, str(AGENT41), "--packets", str(pdir), "--out", str(out), "--base-url", mock.url,
                            "--model", "mock-model", "--source-commit", "abc1234", "--backoff", "0,0,0"],
                           env={**os.environ, "TOK" + "EN": "test-value"}, capture_output=True, text=True)
    finally:
        mock.server.shutdown()
    assert p.returncode == 0, p.stderr
    items = {json.loads(x)["item_id"]: json.loads(x) for x in (out / "items.jsonl").read_text().splitlines()}
    return mock, items, json.loads((out / "summary.json").read_text())


def test_agent_v41_end_to_end_and_the_format_turn(tmp_path):
    pk = PACKETS["BI-P3-0001"]
    good = _reply41(pk)
    bad = _reply41(pk)
    bad["reference_answer"]["table_pattern"][0]["sentence"] = ("In California, days hot and humid enough to be dangerous are projected "
                                                               "to increase a moderate increase by mid-century under a high-emissions "
                                                               "future, in the middle tercile.")
    mock, items, summary = _run41(tmp_path, {pk["packet_id"]: [json.dumps(bad), json.dumps(good)]})
    assert len(mock.calls) == 2
    view = json.loads(mock.calls[0]["messages"][1]["content"].split("SEED PACKET:\n", 1)[1])
    assert "tercile" in view["must_not_use"] and "tercile" not in view["patterns"][0]["text"]
    it = items["BI-P3-0001"]
    h = it["review"]["history"][0]
    assert it["review"]["status"] == "deterministic_pass" and h["corrective_turn_used"] and h["check_version"] == "synthesis_post_checks v3.1"
    assert any("doubled magnitude" in r for r in h["first_check"]["reasons"]) and any("tercile wording" in r for r in h["first_check"]["reasons"])
    assert it["generation"]["generator_version"] == "litsynth_agent v4.1" and summary["check_version"] == "synthesis_post_checks v3.1"


# --- D: polish checks v2 and the polish agent v1.1 --------------------------------------------------------------------


def test_synonyms_v2_pinned_and_v1_kept():
    assert sha256_file(pc.SYNONYMS_V2_PATH) == load_entry(pc.SYNONYMS_V2_PATH.name)["sha256"] == SYNONYMS_V2_SHA256
    assert sha256_file(pc.SYNONYMS_PATH) == "8236d5eb2444cfacbbbbf902499714f84902c3f15978683d02b53459f5dca549"
    syn = pc.load_synonyms_v2()
    for k, v in (("land–atmosphere feedbacks", "feedback between land and air"), ("urban heat island", "cities trapping heat"),
                 ("urban heat island", "urban heat"), ("vapor pressure deficit", "drier air")):      # the work package's examples
        assert v in syn["terms"][k]


def _v2(o, p, groups, **kw):
    return pc.invariance_v2(o, p, groups, sd.nca_map(), pc.load_synonyms_v2(), pd.load_rules(pd.RULES_V4_PATH),
                            pl.load(pl.PLAIN_V1A_PATH), bi.column_names())


G_WARM = {"group_id": "W", "label": "Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat"}
G_UHI = {"group_id": "U", "label": "urban heat island intensifies due to nighttime conditions and reduced moisture"}
G_FREQ = {"group_id": "F", "label": "global warming increases heatwave frequency and intensity"}
Q = "How will dangerous heat-index days change in Washington by mid-century under a high-emissions future, and why?"


def test_v2_mechanism_by_group_and_numbers_by_value():
    o = {"prompt": Q, "answer": "In Washington, dangerous heat-index days remain rare by mid-century under a high-emissions future, "
                                "from essentially none to about 1 day a summer. Research shows that land–atmosphere feedbacks and the "
                                "urban heat island effect intensify heat under calm conditions, with higher heatwave frequency."}
    p = {"prompt": Q, "answer": "In Washington, dangerous heat-index days remain rare by mid-century under a high-emissions future, "
                                "from essentially none to about one day a summer. Research shows that feedback between land and air "
                                "and cities trapping heat make calm nights hotter, with more frequent heatwaves."}
    r = _v2(o, p, [G_WARM, G_UHI, G_FREQ])
    assert r["pass"], r["reasons"]
    assert r["checks"]["answer"]["numbers"] == {"original": [1.0], "polished": [1.0]}
    lost = dict(p, answer=p["answer"].replace("feedback between land and air and ", "")
                .replace("cities trapping heat make calm nights hotter", "calm air matters"))   # "hotter" / "nights" recognise W / U
    r = _v2(o, lost, [G_WARM, G_UHI, G_FREQ])
    assert sorted(x.split("group ")[1].split(" ")[0] for x in r["reasons"] if "mechanism" in x) == ["U", "W"]


@pytest.mark.parametrize("change,needle", [
    (lambda t: t.replace("remain rare", "become common"), "descriptor phrase lost: magnitude: remaining rare"),
    (lambda t: t.replace("under a high-emissions future", "under a high-emissions scenario"), "descriptor phrase lost: scenario"),
    (lambda t: t.replace("by mid-century", "by 2050"), "descriptor phrase lost: horizon: mid"),
    (lambda t: t.replace("about 1 day", "about 2 days"), "numbers differ by value"),
    (lambda t: t.replace("a smaller change than in most states", "among the highest in the nation"), "comparison with other states: small"),
])
def test_v2_rejects_changed_descriptors(change, needle):
    o = {"prompt": Q, "answer": "In Washington, dangerous heat-index days remain rare by mid-century under a high-emissions future, "
                                "from essentially none to about 1 day a summer, a smaller change than in most states. Research shows "
                                "that the urban heat island intensifies at night."}
    p = dict(o, answer=change(o["answer"]))
    r = _v2(o, p, [G_UHI])
    assert not r["pass"] and any(needle in x for x in r["reasons"]), r["reasons"]


def test_v2_forms_of_one_class_are_interchangeable():
    o = {"prompt": Q, "answer": "Fire-weather danger in Minnesota shows a slight increase by late this century under a high-emissions "
                                "future, a change similar to most states. Research shows that higher temperatures and aridity dry fuels."}
    p = dict(o, answer="By late this century, under a high-emissions future, fire-weather danger in Minnesota is projected to rise "
                       "slightly, in the middle of the range among states. Research shows that higher temperatures and aridity dry fuels.")
    g = {"group_id": "A", "label": "higher temperatures and aridity dry fuels, creating extreme fire‑weather"}
    assert _v2(o, p, [g])["pass"]
    assert pc.number_values("about half again as many; roughly tripling; eleven days") == [11.0]


def test_polish_agent_v11_pinned_and_prompt():
    assert sha256_file(POLISH11) == POLISH11_SHA256
    a = _load("litpolish_agent_v1_1", POLISH11)
    assert a.GENERATOR_VERSION == "litpolish_agent v1.1" and a.CHECK_VERSION == "polish_checks v2"
    assert hashlib.sha256(a.SYSTEM_PROMPT.encode("utf-8")).hexdigest() == POLISH11_PROMPT_SHA256
    assert "Start sentences with a capital letter; prefer one idea per sentence; keep the hedge words exactly." in a.SYSTEM_PROMPT
    assert "never turn a magnitude phrase into a number or a percentage" in a.SYSTEM_PROMPT
    item = _items()["BI-P3-0001"]
    assert [g["group_id"] for g in a.cited_groups(item)] == [s["group_id"] for s in item["reference_components"]["literature_mechanisms"]]
