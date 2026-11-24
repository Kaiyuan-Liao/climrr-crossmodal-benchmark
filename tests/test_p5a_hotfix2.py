"""P5a hotfix 2 (D-070b): hazard-proxy lexicon v1a ("high temperatures" conditional on climate_coterms_v1) and
run_query.py v4.2 (DR-CAND-INFRA-3: basis a only, impact first, basis-b papers listed). v4.1 ran on Polaris and is held at
9890a00; its INFRA-1 / INFRA-2 outputs equal v4.2's. No model call."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys

import pytest

from climrr import infra_lexicon as il
from climrr import p5a
from climrr.checksums import sha256_file
from climrr.manifest import load_entry

from test_p5a import FIRE_Q, HEAT_Q, TOOLS, _index, _load
from test_p5a_hotfix import PROXY_SHA256, _ci

PROXY_V1A_SHA256 = "018e5e69cb5c3700dc026ed87a672c81edd6b17efe3b660a34c9b9cf6d94b5f8"
RUN_QUERY_V42_SHA256 = "aeb3b8cb33c747f8d14e865584856213157044bff4b66625de7f2b8333d6bc3e"


# --- the lexicon ---------------------------------------------------------------------------------------------------


def test_proxy_v1a_pinned_valid_and_v1_unchanged():
    assert sha256_file(il.PROXY_V1A_PATH) == PROXY_V1A_SHA256 == load_entry(il.PROXY_V1A_PATH.name)["sha256"]
    assert sha256_file(il.PROXY_PATH) == PROXY_SHA256 == load_entry(il.PROXY_PATH.name)["sha256"]
    v1, v1a = il.load_proxy(), il.load_proxy(il.PROXY_V1A_PATH)
    assert v1a["version"] == "hazard_proxy_lexicon_v1a" and il.validate_proxy_v1a(v1a, v1) == []
    assert il.proxy_terms(v1a) == il.proxy_terms(v1)
    assert il.conditional_terms(v1a) == {("heat_index", "high temperatures"): "climate_coterms_v1"}
    assert il.conditional_terms(v1) == {}
    assert il.expand_plurals(il.CLIMATE_COTERMS_V1_WP) == il.CLIMATE_COTERMS_V1 == tuple(v1a["coterm_lists"]["climate_coterms_v1"]["terms"])


def test_proxy_v1a_validation_catches_changes():
    v1a = il.load_proxy(il.PROXY_V1A_PATH)
    a = copy.deepcopy(v1a)
    a["families"]["heat_index"]["terms"][0]["conditional"] = True                         # "extreme heat" conditional too
    a["coterm_lists"]["climate_coterms_v1"]["terms"].append("summers")
    assert any("conditional terms are not" in e for e in il.validate_proxy_v1a(a))
    assert any("not the work package's list" in e for e in il.validate_proxy_v1a(a))
    b = copy.deepcopy(v1a)
    b["families"]["fire_weather_index"]["terms"].pop()
    assert any("differ from hazard_proxy_lexicon_v1" in e for e in il.validate_proxy_v1a(b))


def test_litstatement_v41_terms_equal_v1a():
    a = _load("litstatement_agent_v41_h2", TOOLS / "litstatement_agent.py")
    assert {f: list(t) for f, t in a.INFRA_PROXY_TERMS.items()} == il.proxy_terms(il.load_proxy(il.PROXY_V1A_PATH))


# --- run_query v4.2: pinned; v4.1 held; INFRA-1 / INFRA-2 unchanged --------------------------------------------------


def test_run_query_v42_pinned_and_v41_held():
    assert sha256_file(TOOLS / "run_query.py") == RUN_QUERY_V42_SHA256
    assert hashlib.sha256(p5a.held_bytes_hotfix2("run_query.py")).hexdigest() == p5a.HELD_HOTFIX2["run_query.py"]


CORPUS = {
    # heat
    "kept/01/401.json": {"title": "Oil palm mills", "s": "High temperatures in the integrated CPO and PKO processes use electricity.",
                         "t": "Electricity output.", "_araiadoc_tags": _ci({"sector": "Energy", "subsectors": ["Electricity"]})},
    "kept/02/402.json": {"title": "Lines", "a": "High temperatures under climate change damage transmission lines.", "_araiadoc_tags": _ci()},
    "kept/03/403.json": {"title": "Roads", "a": "The heat index near roads.",
                         "_araiadoc_tags": _ci({"sector": "Transportation", "subsectors": ["Highways"]})},
    "kept/04/404.json": {"title": "Bridges", "a": "Extreme heat stresses bridges.", "b": "Heat waves buckle railways and cause failures.",
                         "c": "Wildfire smoke closes airports.", "_araiadoc_tags": _ci()},                      # both families
    "kept/05/405.json": {"title": "Waves", "a": "Heat waves are frequent.", "_araiadoc_tags": _ci({"sector": "Energy", "subsectors": []})},
    "kept/06/406.json": {"title": "Grid", "a": "A rising heat index stresses the power grid.", "b": "Outages follow.", "_araiadoc_tags": _ci()},
    "kept/07/407.json": {"title": "Rail", "a": "High temperatures in summers stress rail tracks.", "_araiadoc_tags": _ci()},   # 'summers': no co-term
    "kept/08/408.json": {"title": "Plant", "a": "High temperatures recorded in the plant.", "b": "High temperatures and global warming.",
                         "_araiadoc_tags": _ci({"sector": "Energy", "subsectors": []})},
    # fire weather
    "kept/01/501.json": {"title": "Wires", "a": "Wildfires damage power lines.", "_araiadoc_tags": _ci({"sector": "Energy", "subsectors": []})},
    "kept/02/502.json": {"title": "Towers", "a": "FWI near towers.", "_araiadoc_tags": _ci()},                         # bare FWI: not admitted
    "kept/03/503.json": {"title": "Both", "a": "The fire weather index near substations.",
                         "b": "high temperatures and fire danger near roads under climate change", "_araiadoc_tags": _ci()},
}
FAMILIES = ["--family", f"heat_index={HEAT_Q}", "--family", f"fire_weather_index={FIRE_Q}",
            "--family-disambiguate", "fire_weather_index:fwi=fire weather|fire-weather"]


def _query(tool, idx, out, *extra):
    return subprocess.run([sys.executable, str(tool), "--index", str(idx), "--out", str(out), "--lexicon", str(il.LEXICON_PATH),
                           *FAMILIES, *extra], capture_output=True, text=True)


@pytest.fixture(scope="module")
def infra3(tmp_path_factory):
    base = tmp_path_factory.mktemp("p5a_hotfix2")
    src, _ = _index(base / "s", CORPUS)
    _, idx = _index(base / "i", {k[len("kept/"):]: v for k, v in CORPUS.items()})
    tags, ids = base / "tags.jsonl", base / "ids.txt"
    ids.write_text("402\n501\n", encoding="utf-8")
    subprocess.run([sys.executable, str(TOOLS / "inventory_corpus.py"), "--root", str(src / "kept"), "--out", str(base / "inv.json"),
                    "--corpus-id", "T", "--tags-out", str(tags)], check=True, capture_output=True)
    out = base / "q3"
    p = _query(TOOLS / "run_query.py", idx, out, "--rule", "DR-CAND-INFRA-3", "--proxy-lexicon", str(il.PROXY_V1A_PATH),
               "--sector-tags", str(tags), "--in-set-ids", str(ids), "--in-set-label", "186k", "--cap", "3")
    assert p.returncode == 0, p.stderr
    return {"base": base, "idx": idx, "tags": tags, "ids": ids, "out": out,
            "cand": json.loads((out / "candidates.json").read_text()), "summary": json.loads((out / "summary.json").read_text()),
            "bb": json.loads((out / "basis_b_only.json").read_text()),
            "papers": {json.loads(x)["doc_id"]: json.loads(x) for x in (out / "paper_hits.jsonl").read_text().splitlines()}}


@pytest.mark.parametrize("rule", ["DR-CAND-INFRA-1", "DR-CAND-INFRA-2"])
def test_v41_and_v42_equal_on_infra1_and_infra2(tmp_path, infra3, rule):
    held = tmp_path / "run_query_v41.py"
    held.write_bytes(p5a.held_bytes_hotfix2("run_query.py"))
    extra = ["--rule", rule, "--cap", "2"] + (["--proxy-lexicon", str(il.PROXY_PATH), "--sector-tags", str(infra3["tags"]),
                                               "--in-set-ids", str(infra3["ids"])] if rule == "DR-CAND-INFRA-2" else [])
    outs = {}
    for name, tool in (("v41", held), ("v42", TOOLS / "run_query.py")):
        out = tmp_path / name
        p = _query(tool, infra3["idx"], out, "--name", "x", *extra)
        assert p.returncode == 0, p.stderr
        s = json.loads((out / "summary.json").read_text())
        s.pop("run_utc"), s.pop("elapsed_seconds"), s["index"].pop("path")
        outs[name] = (s, (out / "candidates.json").read_bytes(), (out / "paper_hits.jsonl").read_bytes(), sorted(x.name for x in out.iterdir()))
    assert outs["v41"] == outs["v42"]


# --- DR-CAND-INFRA-3 ------------------------------------------------------------------------------------------------


def test_conditional_rule_per_section(infra3):
    P = infra3["papers"]
    h = lambda d: P[d]["infra3"]["heat_index"]  # noqa: E731
    # the v2 false positive: "high temperatures" + "electricity", no co-term -> dropped; admitted before, not after
    assert P["401"]["families"]["heat_index"]["admitted"] is True and P["401"]["families"]["heat_index"]["admitted_after_conditional"] is False
    assert (h("401")["n_qualifying_sections_before_conditional"], h("401")["n_qualifying_sections"], h("401")["basis_b_only"]) == (1, 0, False)
    assert h("401")["qualifying_only_conditional_terms_before"] is True
    s = h("402")["qualifying_sections"][0]
    assert s["conditional_terms"] == ["high temperatures"] and s["coterms"] == ["climate", "climate change"] and s["impact_forms"] == ["damage"]
    assert h("402")["qualifying_only_conditional_terms"] is True and h("402")["hazard_relation"] == "broader_hazard"
    assert h("407")["n_qualifying_sections"] == 0 and h("407")["n_qualifying_sections_before_conditional"] == 1    # no stemming
    assert h("408")["n_hazard_sections"] == 1 and h("408")["basis_b_only"] is True                                # sec b: co-term, no asset
    assert h("405")["basis_b_only"] is True and h("404")["n_qualifying_sections"] == 2
    assert P["503"]["infra3"]["fire_weather_index"]["hazard_relation"] == "governed_term" and h("503")["n_qualifying_sections"] == 1
    assert P["502"]["infra3"] == {} and P["502"]["families"]["fire_weather_index"]["admitted"] is False


def test_infra3_rank_cap_basis_b_and_report(infra3):
    c, r = infra3["cand"], infra3["cand"]["report"]
    assert c["rule"] == "DR-CAND-INFRA-3" and c["proxy_lexicon"]["sha256"] == PROXY_V1A_SHA256 and c["cap_per_family"] == 3
    assert c["proxy_lexicon"]["conditional_terms"] == {"heat_index:high temperatures": "climate_coterms_v1"}
    # heat: impact first (404 n2, 406 governed n1, 402 proxy n1), then 403 (no impact, governed), 503 -- cap 3
    assert c["by_family"]["heat_index"]["eligible"] == 5 and c["by_family"]["heat_index"]["cutoff"] == \
        {"impact": True, "n_qualifying_sections": 1, "hazard_relation": "broader_hazard"}
    # fire: impact beats the number of sections (404, 501 n1 impact before 503 n2 governed)
    assert [x["item_id"] for x in c["candidates"]] == ["404", "406", "402", "501", "503"]
    first = c["candidates"][0]
    assert first["impact"] is True and first["basis"] == {"heat_index": "a", "fire_weather_index": "a"} and first["families"][0] == \
        {"family": "heat_index", "rank": 1, "n_qualifying_sections": 2, "basis": "a", "n_cooc_sections": 2, "n_hazard_sections": 2,
         "hazard_relation": "broader_hazard"}
    assert {k for k in first} == {"item_id", "arm", "in_186k_set", "asset_sector_tag", "sector_tag_origin", "impact", "basis", "families"}
    assert r["heat_index"] == {
        "admitted": {"before_conditional": 9, "after_conditional": 7,
                     "after_conditional_split": {"n": 7, "governed_term": 2, "impact_true": 3, "in_186k_set": {"False": 6, "True": 1}}},
        "qualifying": {"before_conditional": 7, "after_conditional": 5,
                       "before_conditional_split": {"n": 7, "governed_term": 2, "impact_true": 3, "in_186k_set": {"False": 6, "True": 1}},
                       "after_conditional_split": {"n": 5, "governed_term": 2, "impact_true": 3, "in_186k_set": {"False": 4, "True": 1}},
                       "only_conditional_terms_before": 4, "only_conditional_terms_after": 2},
        "candidates": {"n": 3, "governed_term": 1, "impact_true": 3, "in_186k_set": {"False": 2, "True": 1}},
        "basis_b_only": 2, "hazard_sections_dropped_by_conditional": 3}
    assert r["fire_weather_index"]["candidates"] == {"n": 3, "governed_term": 1, "impact_true": 2, "in_186k_set": {"False": 2, "True": 1}}
    assert r["fire_weather_index"]["admitted"]["before_conditional"] == 3 and r["fire_weather_index"]["basis_b_only"] == 0
    assert [x["doc_id"] for x in infra3["bb"]["families"]["heat_index"]["papers"]] == ["405", "408"]
    s = infra3["summary"]
    assert s["candidates_in_both_families"] == 1 and s["per_hazard_term_doc_counts"]["heat_index:high temperatures"] == \
        {"kind": "proxy", "conditional": True, "docs": 5}


def test_verify_candidates_3_and_tampering(infra3):
    out, c = infra3["out"], infra3["cand"]
    assert il.verify_candidates_3(c, out / "paper_hits.jsonl", out / "basis_b_only.json") == []
    t = copy.deepcopy(c)
    t["candidates"][0], t["candidates"][1] = t["candidates"][1], t["candidates"][0]
    t["candidates"][2]["impact"] = False
    errs = il.verify_candidates_3(t, out / "paper_hits.jsonl")
    assert any("order differs" in e for e in errs) and any(e.startswith("402:") for e in errs)
    bad = out.parent / "bb_tampered.json"
    bb = copy.deepcopy(infra3["bb"])
    bb["families"]["heat_index"]["papers"].pop()
    bad.write_text(json.dumps(bb), encoding="utf-8")
    errs = il.verify_candidates_3(c, out / "paper_hits.jsonl", bad)
    assert any("basis_b_only.json differs from the hash" in e for e in errs) and any("heat_index: basis_b_only.json differs" in e for e in errs)
    assert il.verify_candidates_3({**c, "rule": "DR-CAND-INFRA-2"}, out / "paper_hits.jsonl") == ["rule is not DR-CAND-INFRA-3"]


def test_infra3_argument_rules(infra3, tmp_path):
    run = lambda out, *extra: _query(TOOLS / "run_query.py", infra3["idx"], tmp_path / out, "--rule", "DR-CAND-INFRA-3", *extra)  # noqa: E731
    assert "needs --proxy-lexicon and --sector-tags" in run("a").stderr
    p = run("b", "--proxy-lexicon", str(il.PROXY_PATH), "--sector-tags", str(infra3["tags"]))           # v1: no conditional term
    assert p.returncode != 0 and "needs a proxy lexicon with a conditional term" in p.stderr and not (tmp_path / "b").exists()
