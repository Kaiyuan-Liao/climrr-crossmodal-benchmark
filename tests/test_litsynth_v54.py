"""Work package litsynth v5.4 (2026-11-24; D-075a): rung-8 answer shape v2 --- synthesis agent v5.4, post-checks v3.5, the
asset short forms v1, packets v1b. No model call: local mock server only. Synthesis run 1 (v5.3, packets v1a) is superseded;
its item files are not in the repository (the owner chose to proceed without them), so the "run-1 items still pass" check is
made on synthetic v1a-shaped items written to the v3.4 rules.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from climrr import benchmark_items as bi
from climrr import p5c2
from climrr import synthpackets_infra as spi
from climrr.checksums import sha256_file
from climrr.manifest import load_entry
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
AGENT = TOOLS / "litsynth_agent.py"
ENV = {**os.environ, "TOK" + "EN": "test-value"}  # fragments: keeps this file scannable
SHORT_SHA256 = "de28eaa2d65759d7c09c2e95e8388b17f477f7c0f6d21aa72bcc3681055c444d"
SYNTH_V54_PROMPT_SHA256 = "1a023c1e98e822f74304801fce5a8b4605f6148c528c3dc4f5e236c5c87c3ade"
SYNTH_V54_FORMAT_SHA256 = "a21eb42a4a61ecf540803ba1b0da19fc80bb4c9c8077089b2d0cf58b8c6f10e8"
V35 = bi.SYNTH_CHECK_VERSION_V35
V34 = bi.SYNTH_CHECK_VERSION_V34
NB_HYPHEN = "‑"

MAN_A = json.loads((spi.PACKETS_V1A_DIR / "manifest.json").read_text(encoding="utf-8"))
MAN_B = json.loads((spi.PACKETS_V1B_DIR / "manifest.json").read_text(encoding="utf-8"))
PK_A = {e["item_id"]: json.loads((spi.PACKETS_V1A_DIR / f"{e['packet_id']}.json").read_text(encoding="utf-8")) for e in MAN_A["packets"]}
PK_B = {e["item_id"]: json.loads((spi.PACKETS_V1B_DIR / f"{e['packet_id']}.json").read_text(encoding="utf-8")) for e in MAN_B["packets"]}


def _load(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- the short-form table and packets v1b ---------------------------------------------------------------------------------


def test_short_forms_pinned_and_loaded():
    assert sha256_file(spi.SHORT_FORMS_PATH) == SHORT_SHA256 == load_entry("asset_short_forms_v1.yaml")["sha256"]
    d = spi.load_short_forms()
    assert set(d["classes"]) == set(spi.ASSET_CLASS_PHRASE)
    assert d["classes"]["energy"]["short"][0] == "the grid" and d["classes"]["transportation_systems"]["short"] == ["roads and rail"]
    assert "hospitals and emergency services" in d["classes"]["healthcare_and_public_health"]["short"]


def test_short_forms_refuses_a_changed_file(tmp_path):
    bad = tmp_path / "asset_short_forms_v1.yaml"
    bad.write_text(spi.SHORT_FORMS_PATH.read_text(encoding="utf-8").replace("roads and rail", "roads"), encoding="utf-8")
    with pytest.raises(ValueError, match="differs from its data/manifest.json pin"):
        spi.load_short_forms(bad)


def test_packets_v1b_rebuild_byte_identical_from_v1a():
    short = spi.load_short_forms()
    assert MAN_B["built_from"]["manifest_sha256"] == sha256_file(spi.PACKETS_V1A_DIR / "manifest.json")
    for e in MAN_A["packets"]:
        src = spi.PACKETS_V1A_DIR / f"{e['packet_id']}.json"
        assert sha256_file(src) == e["sha256"] == MAN_B["built_from"]["packets_sha256"][e["packet_id"]]
        pk = spi.to_v1b(json.loads(src.read_text(encoding="utf-8")), short, e["sha256"])
        assert spi.dumps(pk) == (spi.PACKETS_V1B_DIR / f"{e['packet_id']}.json").read_text(encoding="utf-8"), e["packet_id"]
    for e in MAN_B["packets"]:
        assert sha256_file(spi.PACKETS_V1B_DIR / f"{e['packet_id']}.json") == e["sha256"]
    assert MAN_B["version"] == "synthpackets infra v1b" and MAN_B["answer_shape"] == "rung8_v2"
    assert MAN_B["asset_short_forms"]["sha256"] == SHORT_SHA256 and MAN_B["rung_instruction"] == spi.RUNG8_INSTRUCTION_V2


def test_packets_v1b_differ_from_v1a_only_in_the_shape_fields():
    for iid, b in PK_B.items():
        a = PK_A[iid]
        top = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
        assert top == {"version", "decision", "rules", "answer_shape", "v1a_packet_sha256", "inputs_sha256", "model_view", "checks_input"}, iid
        assert {k for k in set(a["inputs_sha256"]) | set(b["inputs_sha256"]) if a["inputs_sha256"].get(k) != b["inputs_sha256"].get(k)} == {"asset_short_forms_v1"}
        mv = {k for k in set(a["model_view"]) | set(b["model_view"]) if a["model_view"].get(k) != b["model_view"].get(k)}
        assert mv == {"answer_shape", "asset_class_short_forms", "rung_instruction"}, iid
        ci = {k for k in set(a["checks_input"]) | set(b["checks_input"]) if a["checks_input"].get(k) != b["checks_input"].get(k)}
        assert ci == {"answer_shape", "rung8"}
        r8a, r8b = a["checks_input"]["rung8"], b["checks_input"]["rung8"]
        assert {k for k in set(r8a) | set(r8b) if r8a.get(k) != r8b.get(k)} == {"asset_class_short_forms"}
        assert b["model_view"]["asset_class_short_forms"] == r8b["asset_class_short_forms"] == spi.load_short_forms()["classes"][b["asset_class"]]["short"]
        assert "Only when citing a group listed in place_named_impact_group_ids" in a["model_view"]["rung_instruction"]
        assert "Only when citing" not in b["model_view"]["rung_instruction"]
        assert "do not write 'this implies more exposure to'" in b["model_view"]["rung_instruction"]
        assert b["model_view"]["rung_instruction"].endswith(spi.RUNG8_INSTRUCTION_V1A_TAIL) == bool(b["model_view"].get("two_hop_group_ids"))
        assert b["provenance"] == a["provenance"] and b["item_schema"] == "benchmark_item_v2a"


# --- normalisation (rule 6) -------------------------------------------------------------------------------------------------


def test_phrase_norm():
    assert bi.phrase_norm(f"fire{NB_HYPHEN}weather‐danger‒x") == "fire-weather-danger-x"
    assert bi.phrase_norm("a  b") == "a b"                                      # NFKC: no-break space
    assert bi.phrase_key("Fire-Weather Danger") == bi.phrase_key(f"fire{NB_HYPHEN}weather danger")
    assert bi.phrase_norm("en–dash") == "en–dash"                         # an en dash is not a hyphen
    assert bi.bridge_count(f"Fire{NB_HYPHEN}weather danger describes conditions that favour wildfire; it is not fire occurrence.",
                           spi.BRIDGE_CLAUSE, normalise=True) == 1
    assert bi.bridge_count(f"fire{NB_HYPHEN}weather danger describes conditions that favour wildfire; it is not fire occurrence.",
                           spi.BRIDGE_CLAUSE) == 0                                   # v3.4 missed it (run 1, 0005 / 0006)


# --- a well-formed shape-v2 answer for BI-P5-0006 ---------------------------------------------------------------------------

G = {
    "drv_ca": "LG-fire_weather_v1-mechanism-c1-002",          # Research on California shows (multi-source)
    "drv_gen": "LG-fire_weather_v1-mechanism-c1-003",         # In general, research shows (multi-source)
    "hop": "LG-infra_fire_weather_index__transportation_systems-impact-c1-003",   # two-hop, Research on the United States suggests
    "d1": "LG-infra_fire_weather_index__transportation_systems-impact-c1-004",    # direct, In general, research suggests
    "d2": "LG-infra_fire_weather_index__transportation_systems-impact-c1-005",    # direct, In general, research suggests
}
TABLE = "Under a high-emissions future, fire-weather danger in California is projected to increase slightly by mid-century."
BRIDGE = "Fire-weather danger describes conditions that favour wildfire; it is not fire occurrence."
BROADER = "conditions that favour wildfire, of which fire-weather danger is one measure"
LIT = [
    ("Research on California shows that strong winds and low humidity raise fire-weather danger.", [G["drv_ca"]], False),
    ("In general, research shows that higher temperatures and aridity dry out fuels.", [G["drv_gen"]], False),
    ("Research on the United States suggests that when wildfires occur, they can expose road networks of transportation systems.",
     [G["hop"]], True),
    (f"In general, research suggests that {BROADER}, can damage roads and bridges, and that such conditions can expose roads and rail.",
     [G["d1"], G["d2"]], True),
]


def _reply(lit=LIT, table=TABLE, integrated=None):
    pid = PK_B["BI-P5-0006"]["checks_input"]["pattern_ids"][0]
    ref_lit = [{"sentence": s, "group_ids": g, "hedged": h} for s, g, h in lit]
    para = integrated if integrated is not None else " ".join([table, BRIDGE] + [s for s, _, _ in lit])
    return {"prompt": "Why does fire-weather danger matter for transportation systems, and how is it projected to change in California?",
            "reference_answer": {"table_pattern": [{"sentence": table, "pattern_ids": [pid]}], "literature_interpretation": ref_lit,
                                 "integrated": para},
            "rubric": {"required_points": [{"point": "Fire-weather danger increases.", "weight": 3, "source_ids": [pid]},
                                           {"point": "The increase is slight.", "weight": 2, "source_ids": [pid]},
                                           {"point": "The change is projected for California.", "weight": 1, "source_ids": [pid]},
                                           {"point": "Strong winds and low humidity raise fire-weather danger.", "weight": 2,
                                            "source_ids": [G["drv_ca"]]}],
                       "acceptable_variants": ["A small rise in fire-weather danger.",
                                               "Exact values are not required; any statement consistent with the magnitude class counts."],
                       "optional_points": [{"point": "Such conditions can damage roads and bridges.", "source_ids": [G["d1"]]}],
                       "disallowed_claims": ["Fire-weather danger measures fire occurrence."],
                       "fatal_errors": ["Reading fire-weather danger as fire occurrence.", "Stating the projection as a certainty."]},
            "guardrails": ["A Fire Weather Index is meteorological fire danger, never fire occurrence."],
            "source_independent_answerability": "yes", "source_independence_note": "General knowledge of fire weather suffices.",
            **{k: "c" for k in ("capability_tested", "system_task", "key_relationships", "evidence_needed", "desired_output_characteristics")},
            "expected_knowledge_level": "general_climate_science"}


#: The run-1 defects (WP evidence): bridge with U+2011 and a lower-case start, the broader-hazard phrase in every impact
#: sentence (4x), "that that when wildfires occur", five driver sentences before any impact.
BAD_LIT = [
    ("Research on California shows that strong winds and low humidity raise fire-weather danger.", [G["drv_ca"]], False),
    ("Research on California shows that strong winds are a primary driver of fire-weather danger.", ["LG-fire_weather_v1-driver-c1-003"], False),
    ("In general, research shows that higher temperatures and aridity dry out fuels.", [G["drv_gen"]], False),
    ("In general, research shows that humidity affects fire-weather danger.", ["LG-fire_weather_v1-driver-c1-002"], False),
    ("Research on California suggests that a warmer atmosphere lowers fuel moisture.", ["LG-fire_weather_v1-mechanism-c1-001"], True),
    ("Research on the United States suggests that that when wildfires occur, they can expose road networks of transportation systems.",
     [G["hop"]], True),
    (f"In general, research suggests that {BROADER}, can damage roads and bridges of transportation systems.", [G["d1"]], True),
    (f"In general, research suggests that {BROADER}, can expose transportation systems; {BROADER}, also matter; {BROADER}, again.",
     [G["d2"]], True),
]


def _bad_reply():
    r = _reply(BAD_LIT)
    bridge = f"fire{NB_HYPHEN}weather danger describes conditions that favour wildfire; it is not fire occurrence."
    r["reference_answer"]["integrated"] = " ".join([TABLE, bridge] + [s for s, _, _ in BAD_LIT])
    return r


def _check(obj, pk, version=V35):
    a = _load("litsynth_agent_v54_checks", AGENT)
    common = {"model": "m", "prompt_hash": "0" * 64, "generation_timestamp": "t", "packet_sha256": "0" * 64, "system_prompt_sha256": "0" * 64}
    item, tagged = a.assemble(obj, pk, common, bi.column_names())
    return bi.synthesis_post_checks(item, tagged, pk["checks_input"], bi.column_names(), check_version=version)


def test_good_shape_v2_answer_passes():
    res = _check(_reply(), PK_B["BI-P5-0006"])
    assert res["pass"], res["reasons"]
    rep = res["checks"]["rung8_report"]
    assert rep["answer_shape"] == "rung8_v2" and rep["budget"]["enforced"] and rep["budget"]["within"]
    assert rep["budget"]["impact_claims"] == 3 and rep["budget"]["driver_claims"] == 2 and rep["budget"]["integrated_sentences"] == 6
    assert rep["broader_hazard_phrase_count"] == {"literature_interpretation": 1, "integrated": 1}
    assert rep["bridge_clause_count"] == 1 and rep["bridge_clause_sentence"] == 2 and rep["bridge_clause_second_sentence"] is True
    assert res["checks"]["scope_openers"] == 4


def test_run1_defects_fail_and_are_format_class():
    pk = PK_B["BI-P5-0006"]
    res = _check(_bad_reply(), pk)
    r = res["reasons"]
    assert not res["pass"]
    assert any("doubled 'that' (D-075a)" in x for x in r)
    assert any("the broader hazard" in x and "exactly once" in x and "(found 4)" in x for x in r)
    assert any("integrated: rung 8 answer shape (D-075a): the broader hazard" in x and "(found 4)" in x for x in r)
    assert any("at most 2 driver claims" in x and "(found 5)" in x for x in r)
    assert any("sentence starts with a lower-case letter: 'fire" in x for x in r)
    assert not any("bridge clause (D-073c)" in x for x in r)                   # normalised: the U+2011 bridge is found once
    assert res["checks"]["rung8_report"]["bridge_clause_count"] == 1
    assert bi.format_class_only(r, pk["checks_input"]["allowed_descriptors"]), [x for x in r if not bi.format_class_only([x], [])]
    old = _check(_bad_reply(), PK_A["BI-P5-0006"], version=V34)              # what v3.4 said on run 1
    assert any("bridge clause (D-073c)" in x and "found 0" in x for x in old["reasons"])


# --- each rule, on the good answer with one change --------------------------------------------------------------------------


def _reasons(**kw):
    return _check(_reply(**kw), PK_B["BI-P5-0006"])["reasons"]


def test_rule1_budget():
    two_tables = TABLE + " " + TABLE
    obj = _reply()
    obj["reference_answer"]["table_pattern"].append(dict(obj["reference_answer"]["table_pattern"][0]))
    r = _check(obj, PK_B["BI-P5-0006"])["reasons"]
    assert any("exactly one table sentence (found 2)" in x for x in r)
    four = LIT[:3] + [(LIT[3][0][:-1] + ", and that such conditions can close roads and rail.", LIT[3][1], True)]
    assert any("2 to 3 impact claims" in x and "(found 4)" in x for x in _reasons(lit=four))
    one = LIT[:3]                                              # one impact claim while the packet has three impact groups
    assert any("2 to 3 impact claims" in x and "(found 1)" in x for x in _reasons(lit=one))
    long_para = " ".join([TABLE, BRIDGE] + [s for s, _, _ in LIT] + ["Research on California shows that winds matter."])
    assert any("integrated: rung 8 answer shape (D-075a): at most 6 sentences" in x for x in _reasons(integrated=long_para))
    assert two_tables                                          # (the table sentence is counted in table_pattern, not by text)


def test_rule1_budget_floor_follows_the_packet():
    """BI-P5-0008 has one impact group: one impact claim is within budget."""
    ci = PK_B["BI-P5-0008"]["checks_input"]
    g = ci["rung8"]["impact_group_ids"][0]
    b = bi.rung8_budget([{"sentence": "T."}], [{"sentence": "In general, research suggests that x.", "group_ids": [g]}], "T. X.", ci, False)
    assert b["limits"]["impact_claims_min_here"] == 1 and b["impact_claims"] == 1 and b["within"]


def test_rule2_broader_phrase_once_and_in_the_first_impact_sentence():
    moved = LIT[:3] + [("In general, research suggests that such conditions can damage roads and bridges, and that such conditions "
                        "can expose roads and rail.", LIT[3][1], True)]
    r = _reasons(lit=moved)
    assert any("the first impact sentence must name the broader hazard" in x for x in r)
    assert any("exactly once" in x and "(found 0)" in x for x in r)
    twice = LIT[:3] + [(LIT[3][0].replace("such conditions", BROADER + ","), LIT[3][1], True)]
    assert any("exactly once" in x and "(found 2)" in x for x in _reasons(lit=twice))


def test_rule2_asset_full_first_then_short():
    no_full = [LIT[0], LIT[1], (LIT[2][0].replace("of transportation systems", "of roads and rail"), LIT[2][1], True), LIT[3]]
    assert any("the first impact sentence must name the asset class in full 'transportation systems'" in x for x in _reasons(lit=no_full))
    no_asset = LIT[:3] + [(f"In general, research suggests that {BROADER}, can damage bridges, and that such conditions close them.",
                           LIT[3][1], True)]
    assert any("or a short form ('roads and rail')" in x for x in _reasons(lit=no_asset))
    assert _reasons() == []                                    # the short form "roads and rail" in the later sentence passes


def test_rule3_merged_openers_counted_as_claims():
    assert bi.claim_count("In general, research shows that A, that B, and that C.") == 3
    assert bi.claim_count("Research on the United States suggests that when wildfires occur, they can block roads.") == 1
    assert bi.claim_count(f"In general, research suggests that {BROADER}, can damage roads.") == 1


def test_rule4_that_that():
    bad = LIT[:2] + [(LIT[2][0].replace("suggests that when", "suggests that that when"), LIT[2][1], True), LIT[3]]
    r = _reasons(lit=bad)
    assert any(x.startswith("literature_interpretation: doubled 'that' (D-075a)") for x in r)
    assert bi.format_class_only([x for x in r if "doubled" in x], [])


def test_rule5_implies_exposure_never_under_shape_v2():
    para = " ".join([TABLE, BRIDGE] + [s for s, _, _ in LIT[:-1]] + ["For transportation systems in California, this implies more exposure to damage."])
    r = _reasons(integrated=para)
    assert any("'this implies more exposure to' is not written in the pilot" in x for x in r)
    # without the shape (packets v1a) the v3.3 rule stands: allowed with a cited place-named impact group
    ci = PK_A["BI-P5-0001"]["checks_input"]
    pn = ci["rung8"]["place_named_impact_group_ids"]
    every = [("integrated", "For energy systems in Virginia, this implies more exposure to outages.")]
    lit = [{"sentence": "Research on Virginia suggests that extreme heat, of which dangerous heat-index days are one measure, can cut "
                        "capacity of energy systems.", "group_ids": [pn[0]]}]
    assert not any("exposure" in x for x in bi.rung8_reasons(lit, "", every, ci, two_hop=True, v35=True, tp_s=[{"sentence": "T."}])[0])


def test_rule6_normalised_phrase_checks():
    nb = [(s.replace("fire-weather", f"fire{NB_HYPHEN}weather").replace("In general", "In general"), g, h) for s, g, h in LIT]
    para = " ".join([TABLE, BRIDGE.replace("-", NB_HYPHEN)] + [s for s, _, _ in nb])
    assert _reasons(lit=nb, integrated=para) == []
    wild = LIT[:3] + [(LIT[3][0] + " Wild" + NB_HYPHEN + "fire spreads.", LIT[3][1], True)]
    assert any("fire-weather wording" in x and "Wild-fire" in x for x in _reasons(lit=wild))


def test_v1a_items_keep_the_v34_rules_and_only_report_the_budget():
    """Stand-in for the two run-1 passes (their files are not in the repository): a long v3.4-conformant answer on the v1a
    packet of BI-P5-0006 --- the broader-hazard phrase in every direct impact sentence, five driver sentences --- passes v3.4
    and v3.5; v3.5 reports the budget as exceeded, not enforced."""
    long_lit = BAD_LIT[:5] + [
        ("Research on the United States suggests that when wildfires occur, they can expose road networks of transportation systems.",
         [G["hop"]], True),
        (f"In general, research suggests that {BROADER}, can damage roads and bridges of transportation systems.", [G["d1"]], True),
        (f"In general, research suggests that {BROADER}, can expose critical transportation systems.", [G["d2"]], True)]
    obj = _reply(long_lit)
    for v in (V34, V35):
        res = _check(obj, PK_A["BI-P5-0006"], version=v)
        assert res["pass"], (v, res["reasons"])
    rep = _check(obj, PK_A["BI-P5-0006"])["checks"]["rung8_report"]
    assert rep["answer_shape"] is None and rep["budget"]["enforced"] is False and rep["budget"]["within"] is False
    assert rep["budget"]["driver_claims"] == 5
    assert not _check(obj, PK_B["BI-P5-0006"])["pass"]       # the same text fails under shape v2


# --- agent v5.4 -----------------------------------------------------------------------------------------------------------


def test_agent_v54_pins_and_prompt():
    a = _load("litsynth_agent_v54", AGENT)
    assert a.GENERATOR_VERSION == "litsynth_agent v5.4" and a.CHECK_VERSION == V35 == "synthesis_post_checks v3.5"
    assert a.sha(a.SYSTEM_PROMPT) == SYNTH_V54_PROMPT_SHA256 and a.sha(a.FORMAT_CORRECTIVE_PROMPT) == SYNTH_V54_FORMAT_SHA256
    for needle in ('answer shape "rung8_v2"', "At most TWO driver claims", "TWO or THREE impact claims", "EXACTLY ONCE",
                   '"such heat"', '"such conditions"', '"asset_class_short_forms"', "MERGE OPENERS", "that A, that B, and that C",
                   'never "that that"', 'Do not write "this implies more exposure to"',
                   "Fire-weather danger describes conditions that favour wildfire; it is not fire occurrence.", "SECOND sentence",
                   'plain "-" character'):
        assert needle in a.SYSTEM_PROMPT, needle
    assert "only when you cite a group listed in \"place_named_impact_group_ids\"" not in a.FORMAT_CORRECTIVE_PROMPT
    assert "RUNG 8 (answer shape rung8_v2)" in a.FORMAT_CORRECTIVE_PROMPT and "never write \"this implies more exposure to\"" in a.FORMAT_CORRECTIVE_PROMPT
    text = AGENT.read_text(encoding="utf-8")
    assert "--packets artifacts/benchmark/synth_packets_infra_v1b" in text and "litsynth/infra_run2" in text
    held = p5c2.held_bytes("litsynth_agent.py")
    assert hashlib.sha256(held).hexdigest() == p5c2.HELD["litsynth_agent.py"] and b'GENERATOR_VERSION = "litsynth_agent v5.3"' in held


class _Mock:
    """One packet; `replies` by turn."""

    def __init__(self, replies):
        self.calls = []
        mock = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                mock.calls.append(body)
                text = replies[len(body["messages"]) // 2 - 1]
                out = json.dumps({"choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": "stop"}]}).encode()
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


def test_agent_v54_end_to_end_run1_defects_then_corrected(tmp_path):
    pk = PK_B["BI-P5-0006"]
    pdir, out = tmp_path / "packets", tmp_path / "out"
    pdir.mkdir()
    (pdir / f"{pk['packet_id']}.json").write_text((spi.PACKETS_V1B_DIR / f"{pk['packet_id']}.json").read_text(encoding="utf-8"),
                                                  encoding="utf-8")
    mock = _Mock([json.dumps(_bad_reply(), ensure_ascii=False), json.dumps(_reply())])
    try:
        p = subprocess.run([sys.executable, str(AGENT), "--packets", str(pdir), "--out", str(out), "--base-url", mock.url,
                            "--model", "mock-model", "--source-commit", "abc1234", "--backoff", "0,0,0"], env=ENV, capture_output=True, text=True)
    finally:
        mock.server.shutdown()
    assert p.returncode == 0, p.stderr
    view = json.loads(mock.calls[0]["messages"][1]["content"].split("SEED PACKET:\n", 1)[1])
    assert view["answer_shape"] == "rung8_v2" and view["asset_class_short_forms"] == ["roads and rail"]
    it = json.loads((out / "items.jsonl").read_text().splitlines()[0])
    h = it["review"]["history"][0]
    assert len(mock.calls) == 2 and h["corrective_turn_used"] and h["corrective_class"] == "format"
    assert it["review"]["status"] == "deterministic_pass", h["reasons"]
    first = h["first_check"]["reasons"]
    assert any("doubled 'that'" in x for x in first) and any("(found 4)" in x for x in first)
    assert any("lower-case letter" in x for x in first)
    assert "doubled 'that'" in mock.calls[1]["messages"][-1]["content"]          # the reasons went into the corrective turn
    assert it["schema_version"] == "benchmark_item_v2a" and h["check_version"] == V35
    s = json.loads((out / "summary.json").read_text())
    assert s["generator_version"] == "litsynth_agent v5.4" and s["format_corrective_pass"] == 1


def test_bad_reply_is_independent_of_the_good_one():
    assert _bad_reply() != _reply() and copy.deepcopy(_reply()) == _reply()
