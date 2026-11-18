"""Item-synthesis agent `scripts/litcollect/litsynth_agent.py` v4 and post-checks v3 (work package P3a; D-059 -- D-064).

On the real seed packets v4 (`artifacts/benchmark/synth_packets_v4`: California heat index, BI-P3-0001; California
fire weather, BI-P3-0007) against a local mock server: a reply in general words (plain-language quantity, "under a
high-emissions future", "by mid-century", "research shows" / "research suggests") passes every post-check v3 and schema v2
and carries the packet's working assumptions; a reply naming "RCP8.5", "95 °F", a year and "one study" fails the
generality rule, which is format-class --- one corrective turn, and a clean second reply passes; a leak mixed in gets no
turn. The hedge-by-strength report flags "suggests" on a multi-source group without failing the item. Post-checks v2.2
stay the default (the ingest of runs 2 and 3 reproduces with them).

Since work package P3b the working tree carries litsynth_agent v4.1 (`test_p3b.py`). These tests hold the v4 agent that
synthesis run 4 used: its bytes at the run's source commit (`litsynth_run4.materialize_agents`), beside the unchanged
sibling tools and `src`, run exactly as before.
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
from climrr import litsynth_run4 as s4
from climrr import synthpackets_v4 as v4
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TOOLS = s4.materialize_agents()                                    # v4 at the run-4 source commit
AGENT = TOOLS / "litsynth_agent.py"
AGENT_SHA256 = "8a8ca836a6cd6469ead6948305f721b9e0d6e7063770350f4c89810a3000fee1"
SYSTEM_PROMPT_SHA256 = "33d387fe5098806cac70822194dc34804d80fc98cdb69ec850c919f88993db05"
FORMAT_CORRECTIVE_PROMPT_SHA256 = "053037521584043f258b74c3e96fc1d5bf6e93f76d15b1c7a4d5229a041a239f"
HEAT, FIRE = "PK-SD2-TP1-00071", "PK-SD2-TP1-01463"
WARMING, HUMIDITY = "LG-extreme_heat_v1-driver-c1-008", "LG-extreme_heat_v1-mechanism-c2-003"


def _packet(pid):
    return json.loads((v4.PACKETS_DIR / f"{pid}.json").read_text(encoding="utf-8"))


def _agent():
    pytest.importorskip("duckdb")
    sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location("litsynth_agent_v4", AGENT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def heat_reply(pk):
    d = pk["model_view"]["patterns"][0]["allowed_descriptors"]
    pid = pk["checks_input"]["pattern_ids"][0]
    return {
        "prompt": "How are days hot and humid enough to be dangerous projected to change in California by mid-century under a "
                  "high-emissions future, and what drives that change?",
        "reference_answer": {
            "table_pattern": [{"sentence": f"In California, {d['quantity']} {d['direction']} {d['horizon']} {d['scenario']}: "
                                           f"{d['magnitude_class']}.", "pattern_ids": [pid]}],
            "literature_interpretation": [
                {"sentence": "Research shows that large-scale warming drives increases in extreme heat.", "group_ids": [WARMING], "hedged": False},
                {"sentence": "Research suggests that humidity magnifies heat stress.", "group_ids": [HUMIDITY], "hedged": True}],
            "integrated": "Dangerous humid-heat days become more common in California by mid-century under a high-emissions future, "
                          "as warming drives more extreme heat."},
        "rubric": {"required_points": [{"point": "states that such days increase", "weight": 3, "source_ids": [pid]},
                                       {"point": f"gives the size as {d['magnitude_class']}", "weight": 2, "source_ids": [pid]},
                                       {"point": "places the change in California", "weight": 1, "source_ids": [pid]},
                                       {"point": "names large-scale warming as the driver", "weight": 2, "source_ids": [WARMING]}],
                   "acceptable_variants": ["more frequent dangerous humid heat"],
                   "optional_points": [{"point": "mentions humidity amplifying heat stress", "source_ids": [HUMIDITY]},
                                       {"point": d["anchor_pair"], "source_ids": [pid]},
                                       {"point": "Exact values are not required; any statement consistent with the magnitude class counts.",
                                        "source_ids": [pid]}],
                   "disallowed_claims": ["presents the projection as a forecast"],
                   "fatal_errors": ["says such days decrease", "treats the modeled historical baseline as an observation",
                                    "states the projection as a certainty"]},
        "guardrails": list(pk["model_view"]["guardrails"]),
        "source_independent_answerability": "yes", "source_independence_note": "A general regional climate question.",
        "capability_tested": "joins a projected pattern to its driver", "system_task": "explains the projected change",
        "key_relationships": "heat index, humidity, warming", "evidence_needed": "direction; driver",
        "desired_output_characteristics": "direction, size, driver", "expected_knowledge_level": "general_climate_science"}


def fire_reply(pk):
    d = pk["model_view"]["patterns"][0]["allowed_descriptors"]
    pid = pk["checks_input"]["pattern_ids"][0]
    multi = next(g["group_id"] for g in pk["model_view"]["groups"] if g["evidence_strength"] != "single_source_supported"
                 and g["role"] == "driver")
    return {
        "prompt": "How is summer fire-weather danger projected to change in California by mid-century under a high-emissions "
                  "future? What drives the change?",
        "reference_answer": {
            "table_pattern": [{"sentence": f"In California, summer {d['quantity']} shows {d['magnitude_class']} {d['horizon']} "
                                           f"{d['scenario']}.", "pattern_ids": [pid]}],
            "literature_interpretation": [{"sentence": "Research shows that hotter, drier weather raises fire-weather danger.",
                                           "group_ids": [multi], "hedged": False}],
            "integrated": "Summer fire-weather danger rises slightly in California by mid-century under a high-emissions future."},
        "rubric": {"required_points": [{"point": "states that fire-weather danger increases", "weight": 3, "source_ids": [pid]},
                                       {"point": "names hotter, drier weather as a driver", "weight": 2, "source_ids": [multi]}],
                   "acceptable_variants": ["more dangerous fire weather"], "optional_points": [],
                   "disallowed_claims": ["says more fires will occur"],
                   "fatal_errors": ["reads fire-weather danger as fire occurrence", "says the danger decreases"]},
        "guardrails": list(pk["model_view"]["guardrails"]),
        "source_independent_answerability": "yes", "source_independence_note": "A general regional climate question.",
        "capability_tested": "joins a projected pattern to its driver", "system_task": "explains the projected change",
        "key_relationships": "fire weather, temperature, dryness", "evidence_needed": "direction; driver",
        "desired_output_characteristics": "direction, driver", "expected_knowledge_level": "general_climate_science"}


def specific_reply(pk):
    """The v3.2-style wording the mentor ruled out: RCP label, threshold, years, "one study"."""
    r = heat_reply(pk)
    r["prompt"] = r["prompt"].replace("days hot and humid enough to be dangerous", "days with a heat index above 95 °F") \
                             .replace("under a high-emissions future", "under RCP8.5")
    r["reference_answer"]["literature_interpretation"][1]["sentence"] = "One study suggests that humidity magnifies heat stress."
    r["reference_answer"]["integrated"] += " This holds for 2045 to 2054."
    return r


def _checked(reply, pk, version=bi.SYNTH_CHECK_VERSION_V3):
    a = _agent()
    common = {"model": "m", "prompt_hash": "0" * 64, "generation_timestamp": "2026-11-17T00:00:00Z", "packet_sha256": "0" * 64,
              "system_prompt_sha256": "0" * 64}
    item, tagged = a.assemble(reply, pk, common, bi.column_names())
    return item, bi.synthesis_post_checks(item, tagged, pk["checks_input"], check_version=version)


class _Mock:
    """`replies[packet_id]` is a list of reply texts by turn."""

    def __init__(self, replies):
        self.calls = []
        mock = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                user = body["messages"][1]["content"]
                mock.calls.append(body)
                key = next(k for k in replies if f"Pattern {k.split('SD2-')[1]}" in user)
                text = replies[key][len(body["messages"]) // 2 - 1]
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


def _run(tmp_path, replies):
    pytest.importorskip("duckdb")
    pdir, out = tmp_path / "packets", tmp_path / "out"
    pdir.mkdir()
    for pid in replies:
        (pdir / f"{pid}.json").write_text((v4.PACKETS_DIR / f"{pid}.json").read_text(encoding="utf-8"), encoding="utf-8")
    mock = _Mock(replies)
    try:
        p = subprocess.run([sys.executable, str(AGENT), "--packets", str(pdir), "--out", str(out), "--base-url", mock.url,
                            "--model", "mock-model", "--source-commit", "abc1234", "--backoff", "0,0,0"],
                           env={**os.environ, "TOK" + "EN": "test-value"}, capture_output=True, text=True)
    finally:
        mock.server.shutdown()
    assert p.returncode == 0, p.stderr
    items = {json.loads(x)["item_id"]: json.loads(x) for x in (out / "items.jsonl").read_text().splitlines()}
    return mock, items, json.loads((out / "summary.json").read_text())


def test_the_agent_is_pinned():
    assert sha256_file(AGENT) == AGENT_SHA256


def test_the_system_prompt():
    a = _agent()
    assert a.GENERATOR_VERSION == "litsynth_agent v4" and a.CHECK_VERSION == "synthesis_post_checks v3"
    assert hashlib.sha256(a.SYSTEM_PROMPT.encode("utf-8")).hexdigest() == SYSTEM_PROMPT_SHA256
    assert hashlib.sha256(a.FORMAT_CORRECTIVE_PROMPT.encode("utf-8")).hexdigest() == FORMAT_CORRECTIVE_PROMPT_SHA256
    for phrase in ('"plain_language"', '"under a high-emissions future"', '"by mid-century" or "by late this century"',
                   'no "RCP", no "SSP"', 'no "95 °F"', "a year or a range of years", 'never write "one study" or "a single study"',
                   "compare no scenarios", '"research shows" or "research has shown"', '"research suggests"',
                   "one sentence holding two linked questions", "two short sentences",
                   "The required points are exactly: the direction; the magnitude class; the place",
                   "is an optional point, never a required one", '"fatal_errors" lists climate errors only',
                   "reading fire-weather danger as fire occurrence", "treating a hazard as a risk",
                   "stating the projection as a certainty or a forecast", "a Fire Weather Index is meteorological fire danger",
                   'write exactly: "' + a.NOT_REQUIRED_SENTENCE + '"', "graded at the PATTERN level"):
        assert phrase in a.SYSTEM_PROMPT, phrase
    assert "RCP8.5" not in a.SYSTEM_PROMPT and "one high-emissions scenario" not in a.SYSTEM_PROMPT
    text = AGENT.read_text(encoding="utf-8")
    assert "/eagl" + "e/" not in text and "/User" + "s/" not in text
    assert "--packets artifacts/benchmark/synth_packets_v4" in text and "litsynth/run4" in text


def test_a_general_heat_item_passes_v3_and_validates():
    pk = _packet(HEAT)
    item, res = _checked(heat_reply(pk), pk)
    assert res["pass"], res["reasons"]
    assert res["check_version"] == "synthesis_post_checks v3" and res["checks"]["hedge_by_strength"] == []
    assert bi.schema_errors(item) == [] and bi.consistency_errors(item) == []
    rc = item["reference_components"]
    assert [s["group_id"] for s in rc["literature_mechanisms"]] == [WARMING, HUMIDITY]
    assert rc["table_patterns"][0]["working_assumptions"] == ["WA-STATE-LABEL", "WA-UNWEIGHTED-MEAN"]
    assert rc["table_patterns"][0]["scenario"] == "RCP8.5"                               # the exact scenario stays in provenance
    assert item["generation"]["inputs_sha256"]["nca_map"] == pk["inputs_sha256"]["nca_map"]   # D-065: the map hash travels


def test_a_general_fire_item_passes_v3():
    pk = _packet(FIRE)
    assert pk["fire_groups_unreviewed"] is True
    item, res = _checked(fire_reply(pk), pk)
    assert res["pass"], res["reasons"]
    assert item["reference_components"]["table_patterns"][0]["working_assumptions"][0] == "WA-FWI-SUMMER"
    assert item["reference_components"]["table_patterns"][0]["acceptance_blocked"] is False
    assert bi.validity(item)["B_deterministic_table_facts"]["met"]                           # D-064: no longer blocked


@pytest.mark.parametrize("needle", ["prompt: generality (D-060/D-062): '95 °F' in graded text",
                                    "prompt: generality (D-060/D-062): 'RCP' in graded text",
                                    "literature_interpretation: generality (D-060/D-062): 'One study' in graded text",
                                    "integrated: generality (D-060/D-062): '2045' in graded text"])
def test_specific_wording_fails_the_generality_rule(needle):
    pk = _packet(HEAT)
    _, res = _checked(specific_reply(pk), pk)
    assert not res["pass"] and needle in res["reasons"], res["reasons"]


def test_v2_2_stays_the_default_and_ignores_generality():
    pk = _packet(HEAT)
    _, res = _checked(specific_reply(pk), pk, version=bi.SYNTH_CHECK_VERSION)
    assert not any("generality" in r for r in res["reasons"]) and "hedge_by_strength" not in res["checks"]


def test_generality_failures_are_format_class():
    pk = _packet(HEAT)
    _, res = _checked(specific_reply(pk), pk)
    assert bi.format_class_only(res["reasons"], pk["checks_input"]["allowed_descriptors"]), res["reasons"]
    assert not bi.format_class_only(res["reasons"] + ["prompt leakage: ClimRR named"], pk["checks_input"]["allowed_descriptors"])


def test_hedge_by_strength_is_reported_not_failed():
    pk = _packet(HEAT)
    r = heat_reply(pk)
    r["reference_answer"]["literature_interpretation"][0]["sentence"] = "Research suggests that large-scale warming drives extreme heat."
    item, res = _checked(r, pk)
    assert res["pass"], res["reasons"]
    assert res["checks"]["hedge_by_strength"] == [{"sentence": 0, "issue": "a multi-source or review group, 'suggests' without 'shows'",
                                                   "group_ids": [WARMING]}]
    r["reference_answer"]["literature_interpretation"][1]["sentence"] = "Research indicates humidity magnifies heat stress, it may be."
    _, res = _checked(r, pk)
    assert any(x["issue"] == "single-source groups only, no 'suggests'" for x in res["checks"]["hedge_by_strength"])


def test_generality_regex_units():
    assert bi.generality_flags("under RCP8.5 by 2050, days above 95 °F; one study; A single study") == \
        ["RCP", "2050", "95 °F", "one study", "A single study"]
    assert bi.generality_flags("95 °F and 105℉") == ["95 °F", "105 °F"]
    assert bi.generality_flags("by late this century, from about 16 to about 45 days a summer; 45 fewer days") == []


def test_the_agent_end_to_end(tmp_path):
    pk = _packet(HEAT)
    mock, items, summary = _run(tmp_path, {HEAT: [json.dumps(heat_reply(pk))], FIRE: [json.dumps(fire_reply(_packet(FIRE)))]})
    assert len(mock.calls) == 2
    for body in mock.calls:
        user = body["messages"][1]["content"]
        view = json.loads(user.split("SEED PACKET:\n", 1)[1])
        assert body["temperature"] == 0 and body["max_tokens"] == 16000 and body["reasoning_effort"] == "low"
        assert '"plain_language"' in user and '"hedge"' in user and "checks_input" not in user and "provenance" not in user
        assert bi.generality_flags(view["patterns"][0]["text"]) == [] and "rung_instruction" not in view
    heat, fire = items["BI-P3-0001"], items["BI-P3-0007"]
    for it in (heat, fire):
        h = it["review"]["history"][0]
        assert it["review"]["status"] == "deterministic_pass" and h["reasons"] == [] and h["check_version"] == "synthesis_post_checks v3"
        assert it["generation"]["generator_version"] == "litsynth_agent v4"
    assert [w["id"] for w in heat["review"]["history"][0]["working_assumptions_relied_on"]] == ["WA-STATE-LABEL", "WA-UNWEIGHTED-MEAN"]
    assert heat["review"]["history"][0]["fire_groups_unreviewed"] is False and fire["review"]["history"][0]["fire_groups_unreviewed"] is True
    assert summary["check_version"] == "synthesis_post_checks v3" and summary["deterministic_pass"] == 2


@pytest.mark.parametrize("leak", [False, True])
def test_a_specific_reply_gets_one_format_turn(tmp_path, leak):
    pk = _packet(HEAT)
    first = specific_reply(pk)
    if leak:
        first["reference_answer"]["integrated"] += " ClimRR shows this."
    mock, items, summary = _run(tmp_path, {HEAT: [json.dumps(first), json.dumps(heat_reply(pk))]})
    it = items["BI-P3-0001"]
    h = it["review"]["history"][0]
    if leak:                                                                     # a leak is not format-class: no turn
        assert len(mock.calls) == 1 and it["review"]["status"] == "rejected_pre_review" and h["corrective_turn_used"] is False
    else:
        assert len(mock.calls) == 2 and it["review"]["status"] == "deterministic_pass" and h["corrective_turn_used"] is True
        assert any("generality" in r for r in h["first_check"]["reasons"])
        assert "plain_language" in mock.calls[1]["messages"][-1]["content"]
