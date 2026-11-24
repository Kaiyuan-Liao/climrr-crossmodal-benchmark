"""Work package P5a (2026-11-23; D-069 -- D-073): infrastructure lexicon v1, run_query.py v4 (lexicon mode, DR-CAND-INFRA-1),
the corpus inventory tool, litstatement_agent v4 (infra arm), post-checks v3.2 (scope marking, question forms), question
forms v1, packets v5 and litsynth_agent v5. Synthetic indexes and local mock servers only; no model call.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
import yaml

from climrr import benchmark_items as bi
from climrr import infra_lexicon as il
from climrr import litsynth_run2 as ls2
from climrr import litsynth_run5 as s5
from climrr import p5a
from climrr import synthpackets_v4 as v4
from climrr import synthpackets_v5 as v5
from climrr.checksums import sha256_file
from climrr.manifest import load_entry
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
LEXICON_SHA256 = "dd16959260006514af18396aba78aa47c60fd95901405b859f1a97f1939b1753"
QUESTION_FORMS_SHA256 = "d123b381f6807a9b8d6cc9b6b901a86e8c48dfe617cb1f26ff9c6be9fdd4c910"
RUN_QUERY_V41_SHA256 = "819f223dc4739079e0b5d6fc7a3c2f5bd38078315d9f168b8ad79b7cf843dc42"   # v4.1 (P5a hotfix); v4 never ran
INVENTORY_SHA256 = "de18fe7da59909410b4036185b04ff82c8a16b73618601148d3a0a615ba958e0"   # v1.1 (P5a hotfix); v1 never ran
LITSTATEMENT_V41_SHA256 = "e2e204e066436cd6bfaea7758ce8125777c6ba9a69ae6a3fc71bc056b839445e"   # v4.1 (P5a hotfix); v4 never ran
LITSTATEMENT_V3_PROMPT_SHA256 = "fbedadd25a8a6a048983f9ed3c49997c73c4de771e9f5d689dacd9f56cb01fff"
LITSTATEMENT_INFRA_PROMPT_SHA256 = "945b487ca515d89fd25755d82e3c4d63e662888dea61f9f386028857ed69e095"
LITSYNTH_V51_SHA256 = "8ff71879c234375299e74a7c7f1d8777f47d86350f3ccf218ed6910bc5aa1a43"   # v5.1 (P5a hotfix); v5 never ran
LITSYNTH_V51_PROMPT_SHA256 = "b81b71abb75a9d57b9f3f08f53f945b99b3f5d6966d42d982da407a185cb3793"
LITSYNTH_V51_FORMAT_SHA256 = "73278b5c7cf0da7e419588850b8c16c90d96a90d10008e14b6d998d176081fe1"
PACKETS_V5_MANIFEST_SHA256 = "1f92c194411ea12152c6659058633bf250812bdb234328fa8f39fb81dd8ea0fd"
HEAT_Q = REPO_ROOT / "artifacts" / "literature" / "litcorpus02" / "evidence" / "queries" / "extreme_heat_diag_topical_only_query.txt"
FIRE_Q = REPO_ROOT / "artifacts" / "literature" / "litcorpus02" / "evidence" / "queries" / "fire_weather_diag_topical_only_query.txt"
ENV = {**os.environ, "TOK" + "EN": "test-value"}  # fragments: keeps this file scannable


def _load(name, path):
    pytest.importorskip("duckdb")
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _index(base, docs):
    pytest.importorskip("duckdb")
    src, idx = base / "src", base / "idx"
    for rel, obj in docs.items():
        (src / rel).parent.mkdir(parents=True, exist_ok=True)
        (src / rel).write_text(obj if isinstance(obj, str) else json.dumps(obj), encoding="utf-8")
    subprocess.run([sys.executable, str(TOOLS / "build_index.py"), "--root", str(src), "--out", str(idx)], check=True, capture_output=True)
    return src, idx


# --- B: the infrastructure lexicon ---------------------------------------------------------------------------------


def test_lexicon_pinned_valid_and_counted():
    assert sha256_file(il.LEXICON_PATH) == LEXICON_SHA256 == load_entry(il.LEXICON_PATH.name)["sha256"]
    lex = il.load()
    assert il.validate(lex) == []
    assert il.counts(lex) | {"per_class": None} == {"asset_classes": 16, "surface_forms": 119, "surface_forms_cisa": 20,
                                                    "surface_forms_executor": 99, "impact_terms": 15, "per_class": None}
    assert lex["never_used_for"] == ["table_columns"] and lex["taxonomy"]["accessed"] == "2026-11-23"
    assert "cisa.gov" in lex["taxonomy"]["url"]


def test_lexicon_validation_catches_bad_provenance():
    lex = il.load()
    bad = copy.deepcopy(lex)
    bad["asset_classes"][0]["surface_forms"][0].pop("authorization")
    bad["asset_classes"][1]["surface_forms"].append({"form": "Chemical Plant", "source": "EXECUTOR (common usage)", "authorization": "our_reading"})
    bad["asset_classes"][2]["surface_forms"][0]["source"] = "somewhere"
    errs = il.validate(bad)
    assert any("without authorization" in e for e in errs) and any("in chemical and commercial_facilities" in e for e in errs)
    assert any("source 'somewhere'" in e for e in errs)


# --- C2: run_query.py v4, lexicon mode --------------------------------------------------------------------------------

DOCS = {
    "01/101.json": {"title": "Heat index and the power grid", "body": "A higher heat index stresses transmission lines and causes outages.",
                    "other": "heat index alone"},
    "01/102.json": {"title": "FWI near substations", "body": "FWI near substations rises."},             # bare FWI, no disambiguator
    "02/201.json": {"a": "The fire weather index and power lines; damage to bridges.", "b": "fire-weather index near roads",
                    "c": "FWI and railway"},                                                         # bare FWI admitted: same document
    "02/202.json": {"a": "Nothing relevant here; roads only."},
    "02/203.json": {"a": "Heat index near hospitals.", "b": "heat-index and pavements"},              # 2 sections, ties 101
    "03/301.json": {"a": "Heat indexes and power grids"},                                            # whole word: 'indexes' is no hit
}


@pytest.fixture(scope="module")
def lexrun(tmp_path_factory):
    base = tmp_path_factory.mktemp("p5a_lex")
    _, idx = _index(base, DOCS)
    out = base / "out"
    p = subprocess.run([sys.executable, str(TOOLS / "run_query.py"), "--index", str(idx), "--out", str(out), "--lexicon", str(il.LEXICON_PATH),
                        "--family", f"heat_index={HEAT_Q}", "--family", f"fire_weather_index={FIRE_Q}",
                        "--family-disambiguate", "fire_weather_index:fwi=fire weather|fire-weather", "--cap", "1"],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return {"idx": idx, "out": out, "summary": json.loads((out / "summary.json").read_text()),
            "cand": json.loads((out / "candidates.json").read_text()),
            "papers": {json.loads(x)["doc_id"]: json.loads(x) for x in (out / "paper_hits.jsonl").read_text().splitlines()}}


def test_run_query_v4_pinned_and_v3_held():
    assert sha256_file(TOOLS / "run_query.py") == RUN_QUERY_V41_SHA256
    assert hashlib.sha256(p5a.held_bytes("run_query.py")).hexdigest() == p5a.HELD["run_query.py"]


def test_lexicon_mode_hits_cooccurrence_and_rfwi1(lexrun):
    P = lexrun["papers"]
    assert sorted(P) == ["101", "102", "201", "203"]                                  # 202 and 301: no hazard hit
    assert P["101"]["cooc"]["heat_index"]["n_sections"] == 2 and P["101"]["impact"] is True
    assert P["101"]["cooc"]["heat_index"]["sections"][1]["impact_forms"] == ["outages"]
    assert P["102"]["families"]["fire_weather_index"] == {"terms": ["fwi"], "admitted": False} and P["102"]["cooc"] == {}
    sec = P["201"]["cooc"]["fire_weather_index"]["sections"]
    assert [s["hazard_terms"] for s in sec] == [["fire weather index"], ["fire-weather index"], ["fwi"]]
    assert sec[0]["asset_classes"] == ["energy", "transportation_systems"] and sec[0]["impact_forms"] == ["damage"]
    assert P["203"]["cooc"]["heat_index"]["n_sections"] == 2
    assert {"healthcare_and_public_health", "transportation_systems"} <= set(P["203"]["asset_classes"])
    s = lexrun["summary"]
    assert s["documents_in_index"] == 6 and s["per_family_doc_counts"]["fire_weather_index"] == {"any_term": 2, "admitted": 1}
    assert s["per_family_cooc_doc_counts"] == {"heat_index": 2, "fire_weather_index": 1} and s["lexicon"]["sha256"] == LEXICON_SHA256


def test_dr_cand_infra_1_rank_ties_cap_and_reverification(lexrun):
    c = lexrun["cand"]
    assert c["rule"] == "DR-CAND-INFRA-1" and c["cap_per_family"] == 1
    assert c["by_family"]["heat_index"] == {"eligible": 2, "selected": 1, "distribution_n_cooc_sections": {"2": 2}, "cutoff_n_cooc_sections": 2}
    assert [x["item_id"] for x in c["candidates"]] == ["101", "201"]                 # tie at 2 sections: '101' < '203'
    assert c["candidates"][0]["families"] == [{"family": "heat_index", "rank": 1, "n_cooc_sections": 2}]
    assert il.verify_candidates(c, lexrun["out"] / "paper_hits.jsonl") == []
    tampered = copy.deepcopy(c)
    tampered["candidates"] = tampered["candidates"][::-1]
    assert il.verify_candidates(tampered, lexrun["out"] / "paper_hits.jsonl")


def test_default_mode_equals_v3(tmp_path, lexrun):
    """Without --lexicon, v4 gives the v3 outputs (run_utc and elapsed aside) on the same index and query."""
    held = p5a.materialize_tools("run_query.py") / "run_query.py"
    outs = {}
    for name, tool in (("v3", held), ("v4", TOOLS / "run_query.py")):
        out = tmp_path / name
        subprocess.run([sys.executable, str(tool), "--index", str(lexrun["idx"]), "--query-file", str(FIRE_Q), "--out", str(out), "--name", "x",
                        "--disambiguate", "fwi=fire weather|fire-weather"], check=True, capture_output=True)
        summ = json.loads((out / "summary.json").read_text())
        summ.pop("run_utc"), summ.pop("elapsed_seconds")
        outs[name] = (summ, *[(out / f).read_bytes() for f in ("ids.txt", "ids_raw.txt", "hits.csv", "disambiguation.csv")])
    assert outs["v3"] == outs["v4"]


def test_lexicon_mode_refuses_mixed_arguments(tmp_path, lexrun):
    p = subprocess.run([sys.executable, str(TOOLS / "run_query.py"), "--index", str(lexrun["idx"]), "--out", str(tmp_path / "o"),
                        "--lexicon", str(il.LEXICON_PATH), "--query-file", str(FIRE_Q)], capture_output=True, text=True)
    assert p.returncode != 0 and "not --query-file" in p.stderr


# --- C1: the corpus inventory ---------------------------------------------------------------------------------------


def test_inventory_counts_tags_duplicates_overlap_and_identity(tmp_path):
    docs = {"kept/01/101.json": {"title": "Heat and Grids!", "body": "x", "_araiadoc_tags": ["infrastructure", "energy"]},
            "kept/01/201.json": {"title": "heat and  grids", "body": "y", "_araiadoc_tags": ["energy"]},       # same normalised title
            "kept/02/102.json": {"title": "Other paper title", "body": "x", "_araiadoc_tags": "single"},
            "kept/02/302.json": {"title": "Other paper title", "body": "x", "_araiadoc_tags": "single"} | {},
            "kept/03/103.json": "not json"}
    docs["kept/03/303.json"] = json.dumps(docs["kept/02/102.json"])          # identical bytes to 102
    src, idx = _index(tmp_path, docs)
    ids = tmp_path / "ids.txt"
    ids.write_text("101\n999\n303\n", encoding="utf-8")
    out = tmp_path / "inv.json"
    assert sha256_file(TOOLS / "inventory_corpus.py") == INVENTORY_SHA256
    subprocess.run([sys.executable, str(TOOLS / "inventory_corpus.py"), "--root", str(src / "kept"), "--out", str(out), "--corpus-id", "T",
                    "--compare-ids", str(ids)], check=True, capture_output=True)
    r = json.loads(out.read_text())
    assert r["files"] == 6 and r["parse_failures"] == 1 and r["shards"]["count"] == 3
    assert r["araiadoc_tags"]["value_type_per_file"] == {"array": 2, "string": 3}
    assert r["araiadoc_tags"]["top_20_values"][0] == ["single", 3]
    assert r["duplicates"]["by_content_sha256"]["groups"] == 1 and r["duplicates"]["by_normalised_title"]["groups"] == 2
    assert r["overlap"]["overlap_by_paper_id"] == 2 and r["overlap"]["overlap_first_20"] == ["101", "303"]
    # the build_index identity of the same root (kept/ as the root)
    _, idx2 = _index(tmp_path / "b", {k[len("kept/"):]: v for k, v in docs.items()})
    assert r["content_identity_sha256"] == json.loads((idx2 / "index_summary.json").read_text())["content_identity_sha256"]
    assert subprocess.run([sys.executable, str(TOOLS / "inventory_corpus.py"), "--root", str(src / "kept"), "--out", str(out)],
                          capture_output=True).returncode != 0                                      # refuses to overwrite


# --- C3: litstatement_agent v4, infra arm -------------------------------------------------------------------------------

AGENT_LS = TOOLS / "litstatement_agent.py"
IMPACT = "High heat index values raise the cooling demand on the power grid and cause transformer failures."


def _impact_st(**kw):
    st = {"statement": "High heat index conditions raise grid load and failures.", "statement_type": "impact", "passage": IMPACT,
          "section_key": "results", "passage_type": "own_finding", "region": "unknown", "region_scope": "unknown",
          "scenario": "unknown", "scenario_source": "unknown", "time": "unknown", "time_source": "unknown",
          "generality": "general_mechanism", "confidence": "high", "hazard_term": "heat index", "asset_class": "energy",
          "impact_mechanism": "higher cooling demand loads the grid", "impact_outcome": "equipment failures and outages"}
    return {**st, **kw}


def test_litstatement_v4_pins_constants_and_v3_prompt_unchanged():
    a = _load("litstatement_agent_v4", AGENT_LS)
    assert sha256_file(AGENT_LS) == LITSTATEMENT_V41_SHA256 and a.GENERATOR_VERSION == "litstatement_agent v4.1"
    assert a.sha(a.SYSTEM_PROMPT) == LITSTATEMENT_V3_PROMPT_SHA256 and a.sha(a.SYSTEM_PROMPT_INFRA) == LITSTATEMENT_INFRA_PROMPT_SHA256
    assert a.INFRA_ASSET_CLASSES == il.class_ids(il.load()) + ("other",)
    cm = yaml.safe_load((REPO_ROOT / "data" / "metadata" / "concept_map.yaml").read_text(encoding="utf-8"))
    gov = [t for e in cm["entries"] if e["canonical_id"] in ("heat_index", "fire_weather_index")
           for t in e["accepted_surface_terms"] + [x["term"] for x in e.get("additional_surface_terms") or []]]
    pl = yaml.safe_load((REPO_ROOT / "data" / "metadata" / "benchmark" / "plain_language_v1a.yaml").read_text(encoding="utf-8"))
    plain = [v for fam in pl["families"].values() for k, v in fam.items() if k in ("quantity", "quantity_short")]
    assert len(gov) == 8 and len(plain) == 4
    assert sorted(t.lower() for t in a.INFRA_HAZARD_TERMS) == sorted(t.lower() for t in gov + plain)
    for c in a.INFRA_ASSET_CLASSES:
        assert f'"{c}"' in a.SYSTEM_PROMPT_INFRA
    for t in a.INFRA_HAZARD_TERMS:
        if "(" not in t:
            assert f'"{t}"' in a.SYSTEM_PROMPT_INFRA, t


def test_litstatement_v4_impact_prechecks():
    a = _load("litstatement_agent_v4_checks", AGENT_LS)
    secs = [{"section_idx": 0, "section_key": "results", "text": "Intro. " + IMPACT + " More."}]
    ok = a.pre_review_check(_impact_st(), secs, a.INFRA_ARM)
    assert ok[0] == "deterministic_pass" and ok[1]["impact_fields_pass"]
    assert a.pre_review_check(_impact_st(hazard_term="HEAT INDEX"), secs, a.INFRA_ARM)[0] == "deterministic_pass"
    for kw, needle in ((dict(hazard_term="drought"), "impact_fields_pass"),   # v4.1: "heat wave" is a proxy term (D-073a) (dict(asset_class="power"), "impact_fields_pass"),
                       (dict(impact_outcome=" "), "impact_fields_pass")):
        st, chk, _ = a.pre_review_check(_impact_st(**kw), secs, a.INFRA_ARM)
        assert st == "rejected_pre_review" and needle in chk["failed"], kw
    st, chk, _ = a.pre_review_check(_impact_st(), secs)                           # the default arm has no impact type
    assert st == "rejected_pre_review" and "enums_valid" in chk["failed"] and "impact_fields_pass" not in chk
    mech = _impact_st(statement_type="mechanism", hazard_term="", asset_class="", impact_mechanism="", impact_outcome="")
    assert a.pre_review_check(mech, secs, a.INFRA_ARM)[0] == "deterministic_pass"


class _LSMock:
    def __init__(self, reject_effort=False):
        self.bodies = []
        mock = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                mock.bodies.append(body)
                if reject_effort and "reasoning_effort" in body:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"unknown field reasoning_effort")
                    return
                reply = {"statements": [_impact_st(), _impact_st(hazard_term="extreme heat")]}
                out = json.dumps({"choices": [{"message": {"role": "assistant", "content": json.dumps(reply)}, "finish_reason": "stop"}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)

            def log_message(self, *a):
                pass

        self.server = HTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/v1"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()


@pytest.mark.parametrize("reject_effort", [False, True])
def test_litstatement_v4_infra_run_end_to_end(tmp_path, reject_effort):
    _, idx = _index(tmp_path, {"01/7001.json": {"title": "Grid", "results": "Intro. " + IMPACT + " More."}})
    cands = tmp_path / "candidates.json"
    cands.write_text(json.dumps({"rule": "DR-CAND-INFRA-1", "candidates": [
        {"item_id": "7001", "arm": "infra_impact_v1", "families": [{"family": "heat_index", "rank": 1, "n_cooc_sections": 1}]}]}))
    mock, out = _LSMock(reject_effort), tmp_path / "out"
    try:
        p = subprocess.run([sys.executable, str(AGENT_LS), "--index", str(idx), "--candidates", str(cands), "--out", str(out), "--arm", "infra_impact_v1",
                            "--base-url", mock.url, "--model", "mock-model", "--reasoning-effort", "low", "--max-tokens", "6000",
                            "--backoff", "0,0,0", "--source-commit", "abc1234"], env=ENV, capture_output=True, text=True)
    finally:
        mock.server.shutdown()
    assert p.returncode == 0, p.stderr
    a = _load("litstatement_agent_v4_e2e", AGENT_LS)
    assert mock.bodies[0]["messages"][0]["content"] == a.SYSTEM_PROMPT_INFRA and mock.bodies[0]["reasoning_effort"] == "low"
    assert mock.bodies[0]["max_tokens"] == 6000
    assert ("reasoning_effort" in mock.bodies[-1]) is (not reject_effort)
    r = json.loads((out / "7001" / "result.json").read_text())
    assert r["arm"] == "infra_impact_v1" and r["reasoning_effort_applied"] is (not reject_effort)
    assert r["system_prompt_sha256"] == LITSTATEMENT_INFRA_PROMPT_SHA256
    assert [x["status"] for x in r["statements"]] == ["deterministic_pass", "deterministic_pass"]   # v4.1: "extreme heat" a proxy
    assert [x["hazard_relation"] for x in r["statements"]] == ["governed_term", "broader_hazard"]
    assert r["statements"][0]["candidate_families"][0]["family"] == "heat_index"
    s = json.loads((out / "summary.json").read_text())
    assert s["by_statement_type"] == {"impact": 2} and s["by_asset_class"] == {"energy": 2}
    assert s["by_hazard_relation"] == {"governed_term": 1, "broader_hazard": 1}
    log = (out / "agent.log").read_text()
    assert "arm=infra_impact_v1" in log and ("REASONING_EFFORT_REJECTED" in log) is reject_effort


# --- D: question forms, packets v5, post-checks v3.2 ------------------------------------------------------------------

MAN5 = json.loads((v5.PACKETS_V5_DIR / "manifest.json").read_text(encoding="utf-8"))
PK5 = {p["item_id"]: json.loads((v5.PACKETS_V5_DIR / f"{p['packet_id']}.json").read_text(encoding="utf-8")) for p in MAN5["packets"]}


def test_question_forms_pinned_and_assigned():
    assert sha256_file(v5.QUESTION_FORMS_PATH) == QUESTION_FORMS_SHA256 == load_entry(v5.QUESTION_FORMS_PATH.name)["sha256"]
    f = v5.load_question_forms()
    assert [x["id"] for x in f["forms"]] == [f"QF-0{i}" for i in range(1, 9)] and f["diversity"]["max_share"] == 0.30
    assert MAN5["question_forms"]["assignment"] == {"BI-P3-0001": "QF-01", "BI-P3-0002": "QF-02", "BI-P3-0003": "QF-03",
                                                    "BI-P3-0004": "QF-05", "BI-P3-0005": "QF-04", "BI-P3-0007": "QF-06",
                                                    "BI-P3-0008": "QF-07"}
    p = {"pattern_kind": "single", "direction": "decrease"}
    got = v5.assign_question_forms([("a", 3, p), ("b", 3, p), ("c", 8, p)], f)
    assert got["a"]["id"] == "QF-01" and got["b"]["id"] == "QF-02" and got["c"]["id"] == "QF-08"   # QF-05: increase only
    with pytest.raises(ValueError):
        v5.assign_question_forms([("x", 7, p)], f)


def test_packets_v5_rebuild_byte_identical_and_groups_unchanged():
    assert sha256_file(v5.PACKETS_V5_DIR / "manifest.json") == PACKETS_V5_MANIFEST_SHA256
    b = v5.build()
    for x, base in zip(b["v5"], b["v4b"]):
        assert (v5.PACKETS_V5_DIR / f"{x['packet_id']}.json").read_text(encoding="utf-8") == v5.dumps(x)
        assert (v4.PACKETS_V4B_DIR / f"{base['packet_id']}.json").read_text(encoding="utf-8") == v5.dumps(base)
        assert v5.group_identity(base, x)
        assert {k for k in x if k not in base} == {"question_form_id", "scope_detail"}
        assert {k for k in x["model_view"] if k not in base["model_view"]} == {"scope", "question_form"}
        assert {k for k in x["checks_input"] if k not in base["checks_input"]} == {"scope", "question_form"}
        assert x["provenance"] == base["provenance"]
    assert MAN5["base"]["manifest_sha256"] == sha256_file(v4.PACKETS_V4B_DIR / "manifest.json")


def test_scope_phrases_and_clauses():
    g = {x["group_id"]: x for x in PK5["BI-P3-0007"]["model_view"]["groups"]}
    assert g["LG-fire_weather_v1-mechanism-c1-002"]["scope_phrase"] == "Research on California shows"
    assert g["LG-fire_weather_v1-mechanism-c1-001"]["scope_phrase"] == "Research on California suggests"
    assert g["LG-fire_weather_v1-driver-c2-021"]["scope_phrase"] == "Research on the United States suggests"
    h = {x["group_id"]: x for x in PK5["BI-P3-0001"]["model_view"]["groups"]}
    assert h["LG-extreme_heat_v1-driver-c1-008"]["scope_phrase"] == "Research on the Southwest shows"   # the cited NCA member
    assert h["LG-extreme_heat_v1-driver-c2-001"]["scope_phrase"] == "In general, research shows"
    need = {k: p["model_view"]["scope"]["needs_general_clause"] for k, p in PK5.items()}
    assert need == {"BI-P3-0001": False, "BI-P3-0002": True, "BI-P3-0003": True, "BI-P3-0004": True, "BI-P3-0005": False,
                    "BI-P3-0007": False, "BI-P3-0008": False}
    assert PK5["BI-P3-0002"]["model_view"]["scope"]["general_clause"] == \
        "These are general drivers of dangerous heat-index days, not findings specific to New York."
    assert PK5["BI-P3-0005"]["model_view"]["scope"]["general_clause"].endswith("not findings specific to any one region.")
    assert len(MAN5["place_specific_class_from_minority_of_cited"]) == 5


def test_diversity_reports():
    d = MAN5["diversity"]
    assert d["assigned_skeletons"]["pass"] is True and d["baseline_run5_prompts"]["pass"] is False
    assert d["baseline_run5_prompts"]["trigrams"][0] == {"trigram": "how are dangerous", "n": 3, "share": 0.429}
    r = bi.opening_trigram_report(["How are x y", "How are x z", "Why is it", "What does it"], 0.30)
    assert r["pass"] is False and r["largest_share"] == 0.5


# replies built from the run-5 items with the scope phrases, the clause and the assigned form (all facts unchanged)

PROMPTS = {"BI-P3-0002": "Why are dangerous heat-index days in New York projected to change by late this century under a high-emissions "
                         "future, and in which direction?",
           "BI-P3-0007": "What factors drive the projected change in fire-weather danger in California by mid-century under a "
                         "high-emissions future, and how large is that change?"}
RUN5 = {it["item_id"]: it for it in ls2.read_items(s5.ART / "items.jsonl")}


def _reply(iid):
    it, pk = RUN5[iid], PK5[iid]
    t = it["review"]["history"][0]["reference_answer_tagged"]
    sc, st = pk["checks_input"]["scope"], pk["checks_input"]["group_strength"]
    head = re.compile(r"^Research (?:shows|suggests|has shown)")
    lit = [{**s, "sentence": head.sub(bi.scope_openings(s["group_ids"], sc["groups"], st)[0], s["sentence"])} for s in t["literature_interpretation"]]
    opens = [bi.scope_openings(s["group_ids"], sc["groups"], st)[0] for s in t["literature_interpretation"]]
    parts, k = [], 0
    for x in bi.SENTENCE_SPLIT_RE.split(t["integrated"]):
        if head.match(x):
            x, k = head.sub(opens[min(k, len(opens) - 1)], x), k + 1
        parts.append(x)
    integrated = " ".join(parts)
    if not any(sc["groups"][g]["class"] in ("state", "nca") for s in lit for g in s["group_ids"]):
        lit.append({"sentence": sc["general_clause"], "group_ids": [], "hedged": False})
        integrated += " " + sc["general_clause"]
    pts = t["rubric_points"]
    req = [{"point": w["point"], "weight": w["weight"],
            "source_ids": next(x["source_ids"] for x in pts if x["point"] == w["point"] and x["field"] == "required_points")}
           for w in t["rubric_required_weights"]]
    rub = it["rubric"]
    return {"prompt": PROMPTS[iid], "reference_answer": {"table_pattern": t["table_pattern"], "literature_interpretation": lit,
                                                          "integrated": integrated},
            "rubric": {"required_points": req, "acceptable_variants": rub["acceptable_variants"],
                       "optional_points": [{"point": x["point"], "source_ids": x["source_ids"]} for x in pts if x["field"] == "optional_points"],
                       "disallowed_claims": rub["disallowed_claims"], "fatal_errors": rub["fatal_errors"]},
            "guardrails": it["guardrails"], "source_independent_answerability": it["source_independent_answerability"],
            "source_independence_note": it["source_independence_note"],
            **{k: it[k] for k in ("capability_tested", "system_task", "key_relationships", "evidence_needed", "desired_output_characteristics",
                                  "expected_knowledge_level")}}


def _check(iid, obj):
    a = _load("litsynth_agent_v5_checks", TOOLS / "litsynth_agent.py")
    common = {"model": "m", "prompt_hash": "0" * 64, "generation_timestamp": "2026-11-23T00:00:00Z", "packet_sha256": "0" * 64,
              "system_prompt_sha256": "0" * 64}
    item, tagged = a.assemble(obj, PK5[iid], common, bi.column_names())
    return bi.synthesis_post_checks(item, tagged, PK5[iid]["checks_input"], bi.column_names(), check_version=bi.SYNTH_CHECK_VERSION_V32)


@pytest.mark.parametrize("iid", ["BI-P3-0002", "BI-P3-0007"])
def test_v32_passes_scoped_answers(iid):
    r = _check(iid, _reply(iid))
    assert r["pass"], r["reasons"]
    assert r["checks"]["scope_clause_required"] is (iid == "BI-P3-0002") and r["checks"]["mixed_scope_report"] == []


def test_v32_failures_are_format_class():
    pk = PK5["BI-P3-0002"]
    obj = _reply("BI-P3-0002")
    obj["reference_answer"]["literature_interpretation"][0]["sentence"] = re.sub(
        r"^Research on the United States shows", "Research shows", obj["reference_answer"]["literature_interpretation"][0]["sentence"])
    obj["reference_answer"]["literature_interpretation"] = obj["reference_answer"]["literature_interpretation"][:-1]   # no clause
    obj["reference_answer"]["integrated"] = obj["reference_answer"]["integrated"].replace(pk["checks_input"]["scope"]["general_clause"], "")
    obj["prompt"] = "How are dangerous heat-index days in New York projected to change by late this century, and why?"
    r = _check("BI-P3-0002", obj)
    kinds = {k for k in ("scope phrase (D-069)", "closing clause (D-069) missing as the last entry", "integrated: closing clause",
                         "question form QF-02") if any(k in x for x in r["reasons"])}
    assert kinds == {"scope phrase (D-069)", "closing clause (D-069) missing as the last entry", "integrated: closing clause", "question form QF-02"}
    assert bi.format_class_only(r["reasons"], pk["checks_input"]["allowed_descriptors"]), r["reasons"]


def test_v32_clause_when_specific_and_place_in_required_point():
    obj = _reply("BI-P3-0007")
    clause = PK5["BI-P3-0007"]["checks_input"]["scope"]["general_clause"]
    obj["reference_answer"]["literature_interpretation"].append({"sentence": clause, "group_ids": [], "hedged": False})
    gid = obj["reference_answer"]["literature_interpretation"][0]["group_ids"][0]
    obj["rubric"]["required_points"].append({"point": "says strong winds drive fire-weather danger in California", "weight": 2, "source_ids": [gid]})
    r = _check("BI-P3-0007", obj)
    assert any("present though a cited group is state- or NCA-specific" in x for x in r["reasons"])
    assert any("place-specific mechanism required (D-069)" in x for x in r["reasons"])
    mixed = _reply("BI-P3-0007")
    s0 = mixed["reference_answer"]["literature_interpretation"][0]
    s0["group_ids"] = s0["group_ids"] + ["LG-fire_weather_v1-driver-c2-021"]
    r2 = _check("BI-P3-0007", mixed)
    assert r2["checks"]["mixed_scope_report"] and r2["checks"]["mixed_scope_report"][0]["classes"] == ["state", "us_subregion"]


def test_v31_and_earlier_unchanged_by_v32():
    assert bi.SYNTH_CHECK_VERSION == "synthesis_post_checks v2.2" and bi.SYNTH_CHECK_VERSION_V31 in bi.SYNTH_CHECK_VERSIONS
    obj = _reply("BI-P3-0002")
    obj["reference_answer"]["literature_interpretation"] = obj["reference_answer"]["literature_interpretation"][:-1]
    a = _load("litsynth_agent_v5_v31", TOOLS / "litsynth_agent.py")
    common = {"model": "m", "prompt_hash": "0" * 64, "generation_timestamp": "t", "packet_sha256": "0" * 64, "system_prompt_sha256": "0" * 64}
    item, tagged = a.assemble(obj, PK5["BI-P3-0002"], common, bi.column_names())
    r = bi.synthesis_post_checks(item, tagged, PK5["BI-P3-0002"]["checks_input"], bi.column_names(), check_version=bi.SYNTH_CHECK_VERSION_V31)
    assert not any("D-069" in x or "question form" in x for x in r["reasons"]) and "mixed_scope_report" not in r["checks"]


# --- D: litsynth_agent v5 ------------------------------------------------------------------------------------------------


def test_litsynth_v5_pinned_and_prompt():
    path = TOOLS / "litsynth_agent.py"
    a = _load("litsynth_agent_v5", path)
    assert sha256_file(path) == LITSYNTH_V51_SHA256 and a.GENERATOR_VERSION == "litsynth_agent v5.1"
    assert a.CHECK_VERSION == "synthesis_post_checks v3.2"
    assert a.sha(a.SYSTEM_PROMPT) == LITSYNTH_V51_PROMPT_SHA256 and a.sha(a.FORMAT_CORRECTIVE_PROMPT) == LITSYNTH_V51_FORMAT_SHA256
    for needle in ("SCOPE (where the research comes from)", '"Research on <State> shows"', '"In general, research shows"',
                   "general_clause", "QUESTION FORM", '"question_form"', "OPTIONAL point"):
        assert needle in a.SYSTEM_PROMPT, needle
    assert hashlib.sha256(p5a.held_bytes("litsynth_agent.py")).hexdigest() == "f41c0b9537912779076bfac81e1341f94e07bd87723177cc583350ce164d33d7"


def test_litsynth_v5_end_to_end_with_the_format_turn(tmp_path):
    helpers = _load("test_litsynth_agent_v4_helpers_p5a", REPO_ROOT / "tests" / "test_litsynth_agent_v4.py")
    pk = PK5["BI-P3-0002"]
    good = _reply("BI-P3-0002")
    bad = copy.deepcopy(good)
    bad["reference_answer"]["literature_interpretation"] = bad["reference_answer"]["literature_interpretation"][:-1]
    pdir, out = tmp_path / "packets", tmp_path / "out"
    pdir.mkdir()
    (pdir / f"{pk['packet_id']}.json").write_text((v5.PACKETS_V5_DIR / f"{pk['packet_id']}.json").read_text(encoding="utf-8"), encoding="utf-8")
    mock = helpers._Mock({pk["packet_id"]: [json.dumps(bad), json.dumps(good)]})
    try:
        p = subprocess.run([sys.executable, str(TOOLS / "litsynth_agent.py"), "--packets", str(pdir), "--out", str(out), "--base-url", mock.url,
                            "--model", "mock-model", "--source-commit", "abc1234", "--backoff", "0,0,0"], env=ENV, capture_output=True, text=True)
    finally:
        mock.server.shutdown()
    assert p.returncode == 0, p.stderr
    view = json.loads(mock.calls[0]["messages"][1]["content"].split("SEED PACKET:\n", 1)[1])
    assert view["question_form"]["id"] == "QF-02" and view["scope"]["needs_general_clause"] is True
    assert all("scope_phrase" in g for g in view["groups"]) and "scope_detail" not in view
    it = json.loads((out / "items.jsonl").read_text().splitlines()[0])
    h = it["review"]["history"][0]
    assert len(mock.calls) == 2 and h["corrective_turn_used"] and it["review"]["status"] == "deterministic_pass", h["reasons"]
    assert any("closing clause (D-069)" in r for r in h["first_check"]["reasons"])
    s = json.loads((out / "summary.json").read_text())
    assert s["check_version"] == "synthesis_post_checks v3.2" and s["question_diversity"]["n"] == 1 and s["mixed_scope_flags"] == 0
