"""P5a hotfix (2026-11-23): D-069a majority scope rule (packets v5a, post-checks v3.2 update, litsynth_agent v5.1), D-073a
hazard-proxy lexicon (litstatement_agent v4.1, plain language v1b), sector tags from the corpus (inventory_corpus v1.1,
run_query v4.1 DR-CAND-INFRA-2). No model call: the agents run against local mocks or not at all."""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys

import pytest
import yaml

from climrr import benchmark_items as bi
from climrr import infra_lexicon as il
from climrr import plain_language as pl
from climrr import synthpackets_v4 as v4
from climrr import synthpackets_v5 as v5
from climrr.checksums import sha256_file
from climrr.manifest import load_entry
from climrr.paths import REPO_ROOT

from test_p5a import FIRE_Q, HEAT_Q, TOOLS, TOOLS51, _index, _load

PROXY_SHA256 = "2da6895e232f57c9c6c254e42710002d00c6aa3a51afa2ec88c5fc03d9ab9d08"
PLAIN_V1B_SHA256 = "60598527bf21a9dbc5a68e31cb60ec76d75b95d5ede7411181c323f56832b140"
PACKETS_V5A_MANIFEST_SHA256 = "30c46fa15ee60a75817fd879fa7a2321ac91e472412100a6fbc53cb861c67de3"
WP_PROXY = {"heat_index": ["extreme heat", "heat wave", "heat waves", "heatwave", "heatwaves", "high temperatures", "hot days", "humid heat"],
            "fire_weather_index": ["fire weather", "fire danger", "fire-weather", "wildfire", "wildfires", "wildland fire"]}


# --- B: the hazard-proxy lexicon, plain language v1b, the infra arm --------------------------------------------------


def test_proxy_lexicon_pinned_valid_and_the_work_package_terms():
    assert sha256_file(il.PROXY_PATH) == PROXY_SHA256 == load_entry(il.PROXY_PATH.name)["sha256"]
    p = il.load_proxy()
    assert il.validate_proxy(p) == [] and il.proxy_terms(p) == WP_PROXY
    assert p["use"] == "literature classification only; never table matching" and p["never_used_for"] == ["table_columns"]
    bad = copy.deepcopy(p)
    bad["families"]["heat_index"]["terms"][0]["authorization"] = "confirmed"
    bad["families"]["fire_weather_index"]["terms"].append(dict(bad["families"]["heat_index"]["terms"][1]))
    bad["families"]["fire_weather_index"]["relation"] = "governed_term"
    errs = il.validate_proxy(bad)
    assert any("source / authorization / use" in e for e in errs) and any("in heat_index and fire_weather_index" in e for e in errs)
    assert any("relation 'governed_term'" in e for e in errs)


def test_plain_language_v1b_is_v1a_plus_the_phrases():
    assert sha256_file(pl.PLAIN_V1B_PATH) == PLAIN_V1B_SHA256 == load_entry(pl.PLAIN_V1B_PATH.name)["sha256"]
    assert sha256_file(pl.PLAIN_V1A_PATH) == load_entry(pl.PLAIN_V1A_PATH.name)["sha256"]          # v1a unchanged
    a, b = pl.load(pl.PLAIN_V1A_PATH), pl.load(pl.PLAIN_V1B_PATH)
    strip = copy.deepcopy(b)
    for f in strip["families"].values():
        f.pop("broader_hazard_phrase")
    assert {k: v for k, v in strip.items() if k not in ("version", "decision", "sha256")} == \
        {k: v for k, v in a.items() if k not in ("version", "decision", "sha256")}
    assert b["families"]["heat_index"]["broader_hazard_phrase"] == "extreme heat, of which dangerous heat-index days are one measure"
    assert b["families"]["fire_weather_index"]["broader_hazard_phrase"].startswith("conditions that favour wildfire")
    assert "broader_hazard_phrase" not in pl.model_view("heat_index", "RCP8.5", "mid", a)
    assert pl.model_view("heat_index", "RCP8.5", "mid", b)["broader_hazard_phrase"] == b["families"]["heat_index"]["broader_hazard_phrase"]
    # the escalated conflict: the fire-weather phrase trips the v3 forbidden-word rule
    assert bi.FWI_FORBIDDEN_RE.search(b["families"]["fire_weather_index"]["broader_hazard_phrase"])


def test_litstatement_v41_proxy_terms_and_relation():
    a = _load("litstatement_agent_v41", TOOLS / "litstatement_agent.py")
    assert {f: list(t) for f, t in a.INFRA_PROXY_TERMS.items()} == il.proxy_terms(il.load_proxy())
    assert sorted(t for ts in a.INFRA_HAZARD_FAMILY.values() for t in ts) == sorted(a.INFRA_HAZARD_TERMS)
    assert a.hazard_relation_of("Heat Wave") == ("broader_hazard", "heat_index")
    assert a.hazard_relation_of("FWI") == ("governed_term", "fire_weather_index")
    assert a.hazard_relation_of("wildland fire") == ("broader_hazard", "fire_weather_index")
    assert a.hazard_relation_of("drought") == (None, None)
    for ts in a.INFRA_PROXY_TERMS.values():
        for t in ts:
            assert f'"{t}"' in a.SYSTEM_PROMPT_INFRA, t
    assert "conditions that favour wildfire" in a.SYSTEM_PROMPT_INFRA and "return no \"impact\" statement for it" in a.SYSTEM_PROMPT_INFRA
    from test_p5a import IMPACT, _impact_st
    secs = [{"section_idx": 0, "section_key": "results", "text": "Intro. " + IMPACT + " More."}]
    for t in ("heat wave", "Wildfires", "humid heat"):
        assert a.pre_review_check(_impact_st(hazard_term=t), secs, a.INFRA_ARM)[0] == "deterministic_pass", t
    st, chk, _ = a.pre_review_check(_impact_st(hazard_term="flood"), secs, a.INFRA_ARM)
    assert st == "rejected_pre_review" and "governed or proxy list" in chk["impact_field_errors"][0]


# --- C: sector tags (inventory v1.1) and DR-CAND-INFRA-2 (run_query v4.1) ---------------------------------------------


def test_sector_mapping_twins_and_lexicon_names():
    inv = _load("inventory_corpus_v11", TOOLS / "inventory_corpus.py")
    assert inv.VERSION == "inventory_corpus v1.1"
    assert inv.CISA_SECTOR_CLASSES == tuple((c["id"], c["cisa_sector"]) for c in il.load()["asset_classes"])
    names = [n for _, n in inv.CISA_SECTOR_CLASSES] + ["Transportation", "Energy", "Communications", "Water", "Healthcare",
                                                      "Government Facilities", "Food & Agriculture", "Nuclear", "", "Unknown Sector",
                                                      "Information Technology Sector", "Commercial"]
    for n in names:
        assert inv.map_sector_name(n) == il.map_sector_name(n), n
    assert il.map_sector_name("Transportation") == {"class_id": "transportation_systems", "match": "prefix"}
    assert il.map_sector_name("Government Facilities") == {"class_id": None, "match": "unmapped"}
    assert all(il.map_sector_name(n)["match"] == "exact" for _, n in inv.CISA_SECTOR_CLASSES)


def _ci(*sectors):
    return {"critical_infrastructure": {"matched_groups": ["g1"], "sectors": list(sectors),
                                        "tags": [f"{s['sector']}/{x}" for s in sectors if isinstance(s, dict) and "sector" in s
                                                 for x in s.get("subsectors") or []]}}


CORPUS = {
    "kept/01/101.json": {"title": "Grid heat", "a": "Extreme heat stresses transmission lines.", "b": "Heat waves are frequent.",
                         "_araiadoc_tags": _ci({"sector": "Energy", "subsectors": ["Electricity"]})},
    "kept/02/102.json": {"title": "Hospitals", "a": "The heat index near hospitals.", "b": "heat index alone",
                         "_araiadoc_tags": _ci()},                                                    # no sector: untagged
    "kept/03/103.json": {"title": "Roads hot", "a": "Hot days increase.", "b": "humid heat rises",
                         "_araiadoc_tags": _ci({"sector": "Transportation", "subsectors": ["Highways", "Bridges"]}, {"bad": 1})},
    "kept/04/104.json": {"title": "Offices", "a": "Heat index values climb.",
                         "_araiadoc_tags": _ci({"sector": "Government Facilities", "subsectors": []})},
    "kept/01/201.json": {"title": "Lines", "a": "Wildfires damage transmission lines.", "_araiadoc_tags": _ci()},
    "kept/02/202.json": {"title": "Towers", "a": "FWI near towers.",                                  # bare FWI, not admitted
                         "_araiadoc_tags": _ci({"sector": "Communications", "subsectors": ["Wireless"]})},
    "kept/03/203.json": {"title": "Danger", "a": "Fire danger near roads.", "_araiadoc_tags": "a string"},
    "kept/04/301.json": {"title": "Nothing", "a": "Roads and bridges.", "_araiadoc_tags": _ci({"sector": "Energy", "subsectors": []})},
}


@pytest.fixture(scope="module")
def infra2(tmp_path_factory):
    base = tmp_path_factory.mktemp("p5a_hotfix")
    src, _ = _index(base / "s", CORPUS)
    _, idx = _index(base / "i", {k[len("kept/"):]: v for k, v in CORPUS.items()})
    inv, tags = base / "inv.json", base / "tags.jsonl"
    ids = base / "ids.txt"
    ids.write_text("101\n201\n999\n", encoding="utf-8")
    subprocess.run([sys.executable, str(TOOLS / "inventory_corpus.py"), "--root", str(src / "kept"), "--out", str(inv), "--corpus-id", "T",
                    "--tags-out", str(tags)], check=True, capture_output=True)
    out = base / "q"
    p = subprocess.run([sys.executable, str(TOOLS / "run_query.py"), "--index", str(idx), "--out", str(out), "--lexicon", str(il.LEXICON_PATH),
                        "--rule", "DR-CAND-INFRA-2", "--proxy-lexicon", str(il.PROXY_PATH), "--sector-tags", str(tags),
                        "--in-set-ids", str(ids), "--in-set-label", "186k",
                        "--family", f"heat_index={HEAT_Q}", "--family", f"fire_weather_index={FIRE_Q}",
                        "--family-disambiguate", "fire_weather_index:fwi=fire weather|fire-weather", "--cap", "3"],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return {"base": base, "idx": idx, "tags": tags, "ids": ids, "inv": json.loads(inv.read_text()), "out": out,
            "cand": json.loads((out / "candidates.json").read_text()), "summary": json.loads((out / "summary.json").read_text()),
            "papers": {json.loads(x)["doc_id"]: json.loads(x) for x in (out / "paper_hits.jsonl").read_text().splitlines()}}


def test_inventory_v11_sector_tags(infra2):
    st = infra2["inv"]["sector_tags"]
    assert st["files_with_critical_infrastructure_object"] == 7 and st["files_with_at_least_one_sector"] == 5
    assert st["shape_problems_files"] == {"sector_entry_malformed": 1, "tags_not_object": 1}
    assert st["files_per_sector_name"] == {"Energy": 2, "Transportation": 1, "Government Facilities": 1, "Communications": 1}
    assert st["mapping_to_lexicon_classes"]["Transportation"] == {"files": 1, "class_id": "transportation_systems", "match": "prefix"}
    assert st["unmapped_names"] == ["Government Facilities"] and st["mapped_names"] == ["Communications", "Energy", "Transportation"]
    rows = {json.loads(x)["doc_id"]: json.loads(x) for x in infra2["tags"].read_text().splitlines()}
    assert rows["103"]["asset_sector_tag"] == ["Transportation/Highways", "Transportation/Bridges"]
    assert rows["104"]["asset_sector_tag"] == ["Government Facilities"] and rows["102"]["asset_sector_tag"] == []
    assert rows["203"]["asset_sector_tag"] == [] and rows["101"]["origin"] == "external_model (JL pipeline)"
    assert st["tags_out_sha256"] == sha256_file(infra2["tags"]) and len(rows) == 8


def test_dr_cand_infra_2_basis_rank_relation_and_set(infra2):
    P = infra2["papers"]
    q = P["101"]["infra2"]["heat_index"]
    assert (q["n_hazard_sections"], q["n_cooc_sections"], q["n_qualifying_sections"], q["basis"], q["hazard_relation"]) == (2, 1, 2, "a", "broader_hazard")
    assert P["102"]["infra2"]["heat_index"] | {"qualifying_sections": None} == {"n_hazard_sections": 2, "n_cooc_sections": 1, "n_qualifying_sections": 1,
                                                                                "basis": "a", "hazard_relation": "governed_term", "qualifying_sections": None}
    assert P["103"]["infra2"]["heat_index"]["basis"] == "b" and P["103"]["infra2"]["heat_index"]["n_qualifying_sections"] == 2
    assert P["202"]["families"]["fire_weather_index"]["admitted"] is False and P["202"]["infra2"] == {}
    assert P["203"]["sector_tagged"] is False and P["203"]["infra2"]["fire_weather_index"]["basis"] == "a"
    assert P["101"]["in_186k_set"] is True and P["102"]["in_186k_set"] is False and "301" not in P
    c = infra2["cand"]
    assert c["rule"] == "DR-CAND-INFRA-2" and c["cap_per_family"] == 3 and c["proxy_lexicon"]["sha256"] == PROXY_SHA256
    h = c["by_family"]["heat_index"]
    assert h["eligible"] == 4 and h["selected"] == 3 and h["cutoff"] == {"n_qualifying_sections": 1, "basis": "a"}
    assert h["eligible_split"]["by_basis"] == {"a": 2, "b": 2} and h["distribution_n_qualifying_sections"] == {"1": 2, "2": 2}
    assert h["eligible_split"]["by_hazard_relation"] == {"broader_hazard": 2, "governed_term": 2}
    assert [x["item_id"] for x in c["candidates"]] == ["101", "103", "102", "201", "203"]     # ties at 2: basis a before b
    first = c["candidates"][0]
    assert first["in_186k_set"] is True and first["asset_sector_tag"] == ["Energy/Electricity"] and first["basis"] == {"heat_index": "a"}
    assert first["families"][0] == {"family": "heat_index", "rank": 1, "n_qualifying_sections": 2, "basis": "a", "n_cooc_sections": 1,
                                    "n_hazard_sections": 2, "hazard_relation": "broader_hazard"}
    assert c["sector_tags"]["index_papers_missing_from_file"] == 0 and c["in_set"]["ids"] == 3
    assert infra2["summary"]["per_hazard_term_doc_counts"]["heat_index:extreme heat"] == {"kind": "proxy", "docs": 1}
    assert infra2["summary"]["per_family_doc_counts"]["heat_index"]["admitted_proxy_only"] == 2
    assert il.verify_candidates_2(c, infra2["out"] / "paper_hits.jsonl") == []
    t = copy.deepcopy(c)
    t["candidates"][0], t["candidates"][1] = t["candidates"][1], t["candidates"][0]
    t["candidates"][2]["in_186k_set"] = True
    errs = il.verify_candidates_2(t, infra2["out"] / "paper_hits.jsonl")
    assert any("order differs" in e for e in errs) and any("102: in_186k_set" in e for e in errs)


def test_infra2_argument_rules_and_tag_hash_check(infra2, tmp_path):
    run = lambda *extra: subprocess.run([sys.executable, str(TOOLS / "run_query.py"), "--index", str(infra2["idx"]),  # noqa: E731
                                         "--lexicon", str(il.LEXICON_PATH), "--family", f"heat_index={HEAT_Q}", *extra],
                                        capture_output=True, text=True)
    assert "needs --proxy-lexicon and --sector-tags" in run("--out", str(tmp_path / "a"), "--rule", "DR-CAND-INFRA-2").stderr
    assert "belong to --rule DR-CAND-INFRA-2" in run("--out", str(tmp_path / "b"), "--sector-tags", str(infra2["tags"])).stderr
    bad = tmp_path / "tags.jsonl"
    rows = [json.loads(x) for x in infra2["tags"].read_text().splitlines()]
    rows[0]["sha256"] = "0" * 64
    bad.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    p = run("--out", str(tmp_path / "c"), "--rule", "DR-CAND-INFRA-2", "--proxy-lexicon", str(il.PROXY_PATH), "--sector-tags", str(bad))
    assert p.returncode != 0 and "sha256 differs from the index" in p.stderr
    p = subprocess.run([sys.executable, str(TOOLS / "run_query.py"), "--index", str(infra2["idx"]), "--out", str(tmp_path / "d"),
                        "--query-file", str(FIRE_Q), "--rule", "DR-CAND-INFRA-2"], capture_output=True, text=True)
    assert p.returncode != 0 and "need --lexicon" in p.stderr


# --- A: packets v5a and post-checks v3.2 with the optional clause ----------------------------------------------------

MAN5A = json.loads((v5.PACKETS_V5A_DIR / "manifest.json").read_text(encoding="utf-8"))
PK5A = {p["item_id"]: json.loads((v5.PACKETS_V5A_DIR / f"{p['packet_id']}.json").read_text(encoding="utf-8")) for p in MAN5A["packets"]}


def test_packets_v5a_rebuild_byte_identical_and_groups_unchanged():
    assert sha256_file(v5.PACKETS_V5A_DIR / "manifest.json") == PACKETS_V5A_MANIFEST_SHA256
    b = v5.build("v5a")
    for x, base in zip(b["v5"], b["v4b"]):
        assert (v5.PACKETS_V5A_DIR / f"{x['packet_id']}.json").read_text(encoding="utf-8") == v5.dumps(x)
        assert v5.group_identity(base, x, v5.SCOPE_FIELDS_V5A) and x["provenance"] == base["provenance"]
        assert x["version"] == "synthpackets v5a" and x["model_view"]["plain_language"]["version"] == "plain_language_v1b"
        assert x["inputs_sha256"]["plain_language"] == PLAIN_V1B_SHA256
        five = json.loads((v5.PACKETS_V5_DIR / f"{x['packet_id']}.json").read_text(encoding="utf-8"))
        assert x["question_form_id"] == five["question_form_id"] and x["checks_input"]["question_form"] == five["checks_input"]["question_form"]
    assert MAN5A["base"]["manifest_sha256"] == sha256_file(v5.PACKETS_V5_DIR / "manifest.json")


def test_v5a_majority_rule_minority_cases_and_ties():
    five = {(d["item_id"], d["group_id"]): d for d in MAN5A["v5_minority_cases"]}
    assert len(five) == 5 and len(MAN5A["changes_from_v5"]) == 11
    d = five[("BI-P3-0001", "LG-extreme_heat_v1-driver-c1-008")]["v5a"]
    assert d == {"scope_class": "us_national", "scope_phrase": "Research on the United States shows",
                 "scope_optional_clause": ", including work on the Southwest"}
    for gid in ("LG-fire_weather_v1-mechanism-c1-003", "LG-fire_weather_v1-driver-c1-002", "LG-fire_weather_v1-driver-c1-005"):
        x = five[("BI-P3-0007", gid)]["v5a"]
        assert x["scope_phrase"] == "In general, research shows" and x["scope_optional_clause"] == ", including work on California"
    assert five[("BI-P3-0007", "LG-fire_weather_v1-mechanism-c1-003")]["v5a"]["scope_class"] == "mixed"      # 1 / 1 / 1
    g = {x["group_id"]: x for x in PK5A["BI-P3-0008"]["model_view"]["groups"]}
    assert g["LG-fire_weather_v1-mechanism-c1-003"]["scope_class"] == "mixed"                                # tie 1 : 1
    assert g["LG-fire_weather_v1-mechanism-c1-003"]["scope_optional_clause"] is None
    g7 = {x["group_id"]: x for x in PK5A["BI-P3-0007"]["model_view"]["groups"]}
    assert g7["LG-fire_weather_v1-driver-c1-003"]["scope_phrase"] == "Research on California shows"           # 3 of 4: majority
    assert v5.majority_class(["state", "global", "global"]) == "global" and v5.majority_class(["nca", "us_national"]) == "mixed"
    assert v5.majority_class([]) == "mixed"
    need = {k: p["model_view"]["scope"]["needs_general_clause"] for k, p in PK5A.items()}
    assert need == {"BI-P3-0001": False, "BI-P3-0002": True, "BI-P3-0003": True, "BI-P3-0004": True, "BI-P3-0005": True,
                    "BI-P3-0007": False, "BI-P3-0008": False}


def _scoped(iid: str, use_clause: bool) -> dict:
    """test_p5a._reply on the v5a packet: the run-5 answer with the v5a scope openings (the optional-clause opening where
    the sentence's best group has one and `use_clause`), the closing clause when no cited group is place-specific."""
    import test_p5a as t5

    it, pk = t5.RUN5[iid], PK5A[iid]
    t = it["review"]["history"][0]["reference_answer_tagged"]
    sc, st = pk["checks_input"]["scope"], pk["checks_input"]["group_strength"]
    head = re.compile(r"^Research (?:shows|suggests|has shown)")

    def opening(ids):
        opens = bi.scope_openings(ids, sc["groups"], st)
        return next((o for o in opens if ", including work on" in o), opens[0]) if use_clause else opens[0]
    lit = [{**x, "sentence": head.sub(opening(x["group_ids"]), x["sentence"])} for x in t["literature_interpretation"]]
    opens = [opening(x["group_ids"]) for x in t["literature_interpretation"]]
    parts, k = [], 0
    for x in bi.SENTENCE_SPLIT_RE.split(t["integrated"]):
        if head.match(x):
            x, k = head.sub(opens[min(k, len(opens) - 1)], x), k + 1
        parts.append(x)
    integrated = " ".join(parts)
    if not any(sc["groups"][g]["class"] in ("state", "nca") for x in lit for g in x["group_ids"]):
        lit.append({"sentence": sc["general_clause"], "group_ids": [], "hedged": False})
        integrated += " " + sc["general_clause"]
    obj = t5._reply(iid)
    obj["reference_answer"]["literature_interpretation"] = lit
    obj["reference_answer"]["integrated"] = integrated
    return obj


def _check5a(iid, obj):
    a = _load("litsynth_agent_v51_checks", TOOLS51 / "litsynth_agent.py")
    common = {"model": "m", "prompt_hash": "0" * 64, "generation_timestamp": "2026-11-23T00:00:00Z", "packet_sha256": "0" * 64,
              "system_prompt_sha256": "0" * 64}
    item, tagged = a.assemble(obj, PK5A[iid], common, bi.column_names())
    return bi.synthesis_post_checks(item, tagged, PK5A[iid]["checks_input"], bi.column_names(), check_version=bi.SYNTH_CHECK_VERSION_V32)


def test_v32_scope_openings_with_the_optional_clause():
    sc = PK5A["BI-P3-0007"]["checks_input"]["scope"]["groups"]
    st = PK5A["BI-P3-0007"]["checks_input"]["group_strength"]
    gid = "LG-fire_weather_v1-driver-c1-002"
    assert bi.scope_openings([gid], sc, st) == ["In general, research shows", "In general, research has shown",
                                                "In general, research, including work on California, shows",
                                                "In general, research, including work on California, has shown"]
    # v5 groups carry no optional clause: their openings are unchanged
    import test_p5a as t5
    sc5 = t5.PK5["BI-P3-0007"]["checks_input"]["scope"]["groups"]
    assert bi.scope_openings([gid], sc5, st) == ["Research on California shows", "Research on California has shown"]


@pytest.mark.parametrize("use_clause", [False, True])
def test_v32_passes_v5a_answers_with_and_without_the_clause(use_clause):
    r = _check5a("BI-P3-0007", _scoped("BI-P3-0007", use_clause))
    assert r["pass"], r["reasons"]


def test_v32_place_first_fails_on_v5a():
    """Under v5a a group whose majority is general may name the place only in the optional clause, never first."""
    obj = _scoped("BI-P3-0007", False)
    lit = obj["reference_answer"]["literature_interpretation"]
    lit.insert(0, {"sentence": "Research on California shows that drier fuels raise fire-weather danger.",
                   "group_ids": ["LG-fire_weather_v1-driver-c1-002"], "hedged": False})
    r = _check5a("BI-P3-0007", obj)
    assert any(x.startswith("literature_interpretation[0]: scope phrase (D-069)") for x in r["reasons"]), r["reasons"]


# --- A / B: litsynth_agent v5.1 -------------------------------------------------------------------------------------


def test_litsynth_v51_prompt_and_default_packets():
    a = _load("litsynth_agent_v51", TOOLS51 / "litsynth_agent.py")
    assert a.GENERATOR_VERSION == "litsynth_agent v5.1" and a.CHECK_VERSION == "synthesis_post_checks v3.2"
    for needle in ('"scope_optional_clause"', "just before the verb", "BROADER HAZARD", '"broader_hazard_phrase"',
                   '"hazard_relation": "broader_hazard"', "papers split evenly"):
        assert needle in a.SYSTEM_PROMPT, needle
    assert '"scope_optional_clause" just before the verb' in a.FORMAT_CORRECTIVE_PROMPT
    assert "--packets artifacts/benchmark/synth_packets_v5a" in (TOOLS51 / "litsynth_agent.py").read_text(encoding="utf-8")


def test_v5_artifacts_unchanged_by_the_hotfix():
    """Packets v5 and v4b stay byte-identical to their build (test_p5a pins the v5 manifest); v5a only adds."""
    b = v5.build("v5")
    for x in b["v5"]:
        assert (v5.PACKETS_V5_DIR / f"{x['packet_id']}.json").read_text(encoding="utf-8") == v5.dumps(x)
        assert "scope_optional_clause" not in json.dumps(x["model_view"]["groups"])
    assert sha256_file(v4.PACKETS_V4B_DIR / "manifest.json") == MAN5A["base"]["v4b_manifest_sha256"]
    assert yaml.safe_load(pl.PLAIN_V1A_PATH.read_text(encoding="utf-8"))["version"] == "plain_language_v1a"


def test_inventory_v1_held_and_v11_equal_beyond_sector_tags(tmp_path, infra2):
    """inventory_corpus v1 ran on Polaris (2026-11-24); its bytes are held at 600c888. On the same corpus v1.1 gives v1's
    report plus `sector_tags` (and its own version and timing)."""
    from climrr import p5a

    held = tmp_path / "inventory_corpus_v1.py"
    held.write_bytes(p5a.held_bytes_hotfix("inventory_corpus.py"))
    root = infra2["base"] / "s" / "src" / "kept"
    reps = {}
    for name, tool in (("v1", held), ("v11", TOOLS / "inventory_corpus.py")):
        out = tmp_path / f"{name}.json"
        subprocess.run([sys.executable, str(tool), "--root", str(root), "--out", str(out), "--corpus-id", "T"], check=True, capture_output=True)
        r = json.loads(out.read_text())
        reps[name] = {k: v for k, v in r.items() if k not in ("tool_version", "inventory_utc", "elapsed_seconds", "sector_tags")}
        reps[name + "_version"] = r["tool_version"]
    assert reps["v1"] == reps["v11"] and (reps["v1_version"], reps["v11_version"]) == ("inventory_corpus v1", "inventory_corpus v1.1")
