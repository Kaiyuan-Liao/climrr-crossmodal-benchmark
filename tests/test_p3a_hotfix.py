"""P3a hotfix (D-053b): fire-arm dispositions v1, selection v2a (BI-P3-0006 dropped), plain language v1a, packets v4a, and
the fire-weather words in post-checks v3 and the polish checks.

No model call. Packets v4a are rebuilt in memory from the pinned inputs and compared byte-for-byte with the files.
"""

from __future__ import annotations

import copy
import csv
import importlib.util
import json

import pytest

from climrr import benchmark_items as bi
from climrr import itemseeds as sd
from climrr import itemseeds_v3 as s3
from climrr import litgroups as lgr
from climrr import pilot_selection as psel
from climrr import plain_language as pl
from climrr import polish_checks as pc
from climrr import synthpackets_v4 as v4
from climrr.checksums import sha256_file
from climrr.manifest import load_entry
from climrr.paths import REPO_ROOT

MANIFEST = json.loads((v4.PACKETS_V4A_DIR / "manifest.json").read_text(encoding="utf-8"))
PACKETS = {p["item_id"]: json.loads((v4.PACKETS_V4A_DIR / f"{p['packet_id']}.json").read_text(encoding="utf-8"))
           for p in MANIFEST["packets"]}
FIRE_PHRASE = "fire-weather danger (how hot, dry and windy conditions favour fire)"
CA, MN = "BI-P3-0007", "BI-P3-0008"


def _disp_rows():
    with open(v4.FIRE_DISPOSITIONS_PATH, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _seeds():
    summary = json.loads(s3.SUMMARY_PATH.read_text(encoding="utf-8"))
    if not s3.SEEDS_PATH.is_file():
        pytest.fail("artifacts/benchmark/item_seeds_v3.jsonl is absent (gitignored); run scripts/build_item_seeds_v3.py")
    assert sha256_file(s3.SEEDS_PATH) == summary["seeds_file"]["sha256"]
    return {s["seed_id"]: s for s in sd.read_jsonl(s3.SEEDS_PATH)}


def _v4_agent_tests():
    spec = importlib.util.spec_from_file_location("test_litsynth_agent_v4_helpers", REPO_ROOT / "tests" / "test_litsynth_agent_v4.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- dispositions ----------------------------------------------------------------------------------------------------


def test_fire_dispositions_v1_pinned_and_counted():
    assert sha256_file(v4.FIRE_DISPOSITIONS_PATH) == load_entry(v4.FIRE_DISPOSITIONS_PATH.name)["sha256"] == \
        "94a88f5d3228f3fdc4cf68a585475bb0cbc08b6c8d2ffe95430c8cf029ed907a"
    rows = _disp_rows()
    kinds = [r["proposed_disposition"].split(":")[0] for r in rows]
    assert len(rows) == 21 and kinds.count("accept") == 10 and kinds.count("relabel") == 8 and kinds.count("not_about_family") == 3
    assert all(not r["kaiyuan_disposition"] for r in rows)                      # confirmed as proposed (Kaiyuan 2026-11-17)
    d = lgr.load_dispositions(v4.FIRE_DISPOSITIONS_PATH)
    assert set(d) == {r["group_id"] for r in rows} and all(x["source"] == "proposed" for x in d.values())


def test_fire_dispositions_cover_exactly_the_v4_fire_groups():
    m4 = json.loads((v4.PACKETS_DIR / "manifest.json").read_text(encoding="utf-8"))
    attached = {y["group_id"] for p in m4["packets"] for y in p["fire_groups_attached"]}
    assert attached == {r["group_id"] for r in _disp_rows()}


def test_combined_dispositions_refuse_overlap():
    both = v4.load_dispositions_v4a()
    assert len(both) == 110 + 21


# --- selection v2a ---------------------------------------------------------------------------------------------------


def test_selection_v2a():
    seeds = _seeds()
    sel = psel.load(psel.SELECTION_V2A_PATH)
    assert psel.check_v2a(sel, seeds) == []
    xs = psel.selected(sel)
    assert [x["item_id"] for x in xs] == ["BI-P3-0001", "BI-P3-0002", "BI-P3-0003", "BI-P3-0004", "BI-P3-0005", "BI-P3-0007",
                                         "BI-P3-0008"]
    assert [x["selected_by"] for x in xs if x["source"] == "fwi_shortlist"] == ["Kaiyuan, 2026-11-17"] * 2
    assert [(x["item_id"], x["seed_id"]) for x in sel["excluded_from_v2"]] == [("BI-P3-0006", "SD2-TP1-02789")]
    assert psel.threshold_conflicts(sel, seeds) == [] == MANIFEST["threshold_conflicts"]
    renumbered = copy.deepcopy(sel)
    for i, x in enumerate(renumbered["selected"], 1):
        x["order"], x["item_id"] = i, f"BI-P3-{i:04d}"
    assert psel.check_v2a(renumbered, seeds)
    noreason = copy.deepcopy(sel)
    noreason["excluded_from_v2"][0]["reason"] = ""
    assert "BI-P3-0006: excluded with no reason" in psel.check_v2a(noreason, seeds)
    dropped = copy.deepcopy(sel)
    dropped["excluded_from_v2"] = []
    assert "selected + excluded_from_v2 are not exactly selection v2's entries" in psel.check_v2a(dropped, seeds)


# --- plain language v1a ----------------------------------------------------------------------------------------------


def test_plain_language_v1a():
    v1, v1a = pl.load(), pl.load(pl.PLAIN_V1A_PATH)
    assert v1a["families"]["fire_weather_index"]["quantity"] == FIRE_PHRASE
    assert v1a["families"]["fire_weather_index"]["quantity_short"] == "fire-weather danger"
    assert v1a["families"]["heat_index"] == v1["families"]["heat_index"] and v1a["hedges"] == v1["hedges"]
    assert v1["families"]["fire_weather_index"]["quantity"] == "fire-weather danger"           # v1 unchanged
    mv = pl.model_view("fire_weather_index", "RCP8.5", "mid", v1a)
    assert mv["never_write"] == ["one study", "a single study", "wildfire", "fires", "burned area"]
    assert pl.model_view("heat_index", "RCP8.5", "mid", v1a)["never_write"] == ["one study", "a single study"]
    for w in v1a["families"]["fire_weather_index"]["never_write"]:
        assert bi.fwi_forbidden_flags(w), w                                                   # the yaml and the check agree


# --- packets v4a -----------------------------------------------------------------------------------------------------


def test_packets_v4a_rebuild_byte_identically():
    b = v4.build_selection(variant="v4a")
    assert [pk["item_id"] for pk in b["packets"]] == [p["item_id"] for p in MANIFEST["packets"]]
    for pk in b["packets"]:
        assert (v4.PACKETS_V4A_DIR / f"{pk['packet_id']}.json").read_text(encoding="utf-8") == \
            json.dumps(pk, indent=2, ensure_ascii=False) + "\n"
    for p in MANIFEST["packets"]:
        assert sha256_file(v4.PACKETS_V4A_DIR / f"{p['packet_id']}.json") == p["sha256"]
    assert MANIFEST["inputs_sha256"] == b["hashes"]
    assert b["hashes"]["group_dispositions_fire"] == sha256_file(v4.FIRE_DISPOSITIONS_PATH)
    assert b["hashes"]["plain_language"] == sha256_file(pl.PLAIN_V1A_PATH)
    assert b["hashes"]["pilot_selection"] == sha256_file(psel.SELECTION_V2A_PATH)
    assert not (v4.PACKETS_V4A_DIR / "PK-SD2-TP1-02789.json").exists()


def test_packets_v4a_fire_groups_follow_the_dispositions():
    disp = lgr.load_dispositions(v4.FIRE_DISPOSITIONS_PATH)
    for iid in (CA, MN):
        pk = PACKETS[iid]
        g = pk["provenance"]["groups"]
        assert pk["version"] == "synthpackets v4a" and pk["fire_groups_unreviewed"] is False
        assert g and all(x["review_state"] == "reviewer_tagged" and x["disposition"] == disp[x["group_id"]]["disposition"] for x in g)
        assert all(disp[x["group_id"]]["kind"] in ("accept", "relabel") for x in g)
        for x in g:                                       # a relabel moves the tag; only definition relabels stay (context)
            if disp[x["group_id"]]["kind"] == "relabel":
                assert x["claim_about"] == disp[x["group_id"]]["arg"] == "hazard_definition_or_measurement" and x["role"] == "context"
        exc = {e["group_id"]: e["reason"] for e in pk["excluded_groups"]}
        for gid, d in disp.items():
            if d["kind"] == "not_about_family" and gid in exc:
                assert exc[gid] == "disposition:not_about_family"
        mine = next(p for p in MANIFEST["packets"] if p["item_id"] == iid)
        assert {u["group_id"] for u in mine["undisposed_candidates"]} == {k for k, r in exc.items() if r == "no_disposition"}
        assert not {u["group_id"] for u in mine["undisposed_candidates"]} & {x["group_id"] for x in g}   # never refilled
        assert mine["groups_driver"] >= 2
        assert pk["checks_input"]["family"] == "fire_weather_index" and FIRE_PHRASE in pk["checks_input"]["plain_quantity"]
        assert pk["model_view"]["plain_language"]["quantity"] == FIRE_PHRASE
        assert f"Quantity: {FIRE_PHRASE}." in pk["model_view"]["patterns"][0]["text"]
    assert MANIFEST["undisposed_candidates"]["n_fire_arm"] == len(MANIFEST["undisposed_candidates"]["group_ids"]) == 8


def test_packets_v4a_heat_packets_unchanged_but_for_the_inputs():
    old = {p["item_id"]: json.loads((v4.PACKETS_DIR / f"{p['packet_id']}.json").read_text(encoding="utf-8"))
           for p in json.loads((v4.PACKETS_DIR / "manifest.json").read_text(encoding="utf-8"))["packets"]}
    for iid in ("BI-P3-0001", "BI-P3-0002", "BI-P3-0003", "BI-P3-0004", "BI-P3-0005"):
        a, b = copy.deepcopy(old[iid]), copy.deepcopy(PACKETS[iid])
        for k in (a, b):
            k.pop("inputs_sha256"), k.pop("selection"), k.pop("version"), k.pop("plain_language"), k.pop("plain_language_sha256")
            k["model_view"].pop("plain_language")
            for x in ("family", "plain_quantity"):
                k["checks_input"].pop(x, None)
        assert a == b, iid
        assert PACKETS[iid]["model_view"]["plain_language"]["quantity"] == old[iid]["model_view"]["plain_language"]["quantity"]


# --- post-checks v3: fire-weather words ------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def helpers():
    pytest.importorskip("duckdb")
    return _v4_agent_tests()


def test_a_general_fire_item_passes_on_v4a(helpers):
    pk = PACKETS[CA]
    reply = helpers.fire_reply(pk)
    reply["reference_answer"]["integrated"] = f"Summer {FIRE_PHRASE} rises slightly in California by mid-century."
    _, res = helpers._checked(reply, pk)
    assert res["pass"], res["reasons"]
    rep = res["checks"]["fire_word_report"]          # "favour fire" in the plain phrase is not reported; the rubric's are
    assert {"field": "rubric.disallowed_claims", "word": "fires", "kind": "forbidden_word_in_wrong_answer_list"} in rep
    assert {"field": "rubric.fatal_errors", "word": "fire", "kind": "fire_alone"} in rep
    assert not [r for r in rep if r["field"] == "integrated"]


@pytest.mark.parametrize("text,word", [("Wildfires become more common.", "Wildfires"), ("More fires will burn.", "fires"),
                                       ("The burned area grows.", "burned area"), ("Wild-fire risk rises.", "Wild-fire")])
def test_fire_occurrence_words_fail_fire_items(helpers, text, word):
    pk = PACKETS[CA]
    reply = helpers.fire_reply(pk)
    reply["reference_answer"]["integrated"] += " " + text
    _, res = helpers._checked(reply, pk)
    assert not res["pass"]
    assert f"integrated: fire-weather wording (an FWI is never fire occurrence): {word!r} in graded text" in res["reasons"]
    assert not bi.format_class_only(res["reasons"], pk["checks_input"]["allowed_descriptors"])


def test_fire_alone_is_reported_not_failed(helpers):
    pk = PACKETS[MN]
    reply = helpers.fire_reply(pk)
    reply["prompt"] = reply["prompt"].replace("California", "Minnesota")
    reply["reference_answer"]["integrated"] = "Conditions that favor fire become slightly more common in Minnesota by late this century."
    _, res = helpers._checked(reply, pk)
    assert {"field": "integrated", "word": "fire", "kind": "fire_alone"} in res["checks"]["fire_word_report"]
    assert not any("fire-weather wording" in r for r in res["reasons"])


def test_v4_packets_and_heat_items_skip_the_fire_words(helpers):
    old = json.loads((v4.PACKETS_DIR / "PK-SD2-TP1-01463.json").read_text(encoding="utf-8"))
    reply = helpers.fire_reply(old)
    reply["reference_answer"]["integrated"] += " Wildfires become more common."
    _, res = helpers._checked(reply, old)
    assert "fire_word_report" not in res["checks"] and not any("fire-weather wording" in r for r in res["reasons"])


def test_fire_word_regexes():
    assert bi.fwi_forbidden_flags("wildfire, wild fires, Fires, burned  area") == ["wildfire", "wild fires", "Fires", "burned  area"]
    assert bi.fwi_forbidden_flags("fire-weather danger and a fire") == []
    assert bi.fwi_fire_words("fire-weather, fire weather, fire danger, fire-danger, a fire, fires, wildfire") == ["fire"]
    assert bi.fwi_fire_words(f"More {FIRE_PHRASE}.", [FIRE_PHRASE, "fire-weather danger"]) == []


# --- polish checks v1a -----------------------------------------------------------------------------------------------


def test_polish_refuses_a_new_fire_occurrence_word():
    assert pc.VERSION == "polish_checks v1a"
    o = "Fire-weather danger rises slightly in California."
    assert pc.leakage_flags(o, "answer", []) == set()
    new = pc.leakage_flags("Wildfire danger rises slightly in California.", "answer", [])
    assert "fire-occurrence word: wildfire" in new
