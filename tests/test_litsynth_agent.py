"""Item-synthesis agent `scripts/litcollect/litsynth_agent.py` v3 and the post-checks v2 (pilot P2b-final-prep; D-051, D-055).

Two hand-written packets (real example patterns TP1-00009 Alabama and TP1-00010 Alaska; synthetic
literature groups with consistent spans) against a local mock server: the Alabama reply is a
clean item that passes every post-check and validates against schema v2; the Alaska reply leaks
the source, uses a number the packet does not give, cites a group not in the packet and states a
single-source claim without a hedge, and is written as `rejected_pre_review` with the reasons.
v2: `reasoning_effort` and `max_tokens` 16000 in the request body; one corrective turn on a reply
with no item JSON, which can recover the item or leave it a parse-failure stub; a post-check
failure is not retried. v3 / post-checks v2 (D-055): the clean reply is pattern-level (descriptors, no exact value);
number-words, rounded or decimal values in the graded text fail, a copied descriptor such as "roughly tripling" passes.
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
from climrr import itemseeds as sd
from climrr import synthpackets as spk
from climrr import table_patterns as tp
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
AGENT = TOOLS / "litsynth_agent.py"
AGENT_SHA256 = "d582c008fa689f06fba4ed4e994238654f9d2bbc97e92c99a4ae9ed1604b4dac"
SYSTEM_PROMPT_SHA256 = "d5805e5dcdcbaac56b05f26f3aef6ebff58d3bf106c9313df36eeb71507e0272"
NCA = sd.nca_map()
EX = {p["pattern_id"]: p for p in tp.read_jsonl(tp.EXAMPLES_PATH)}
PASS_A = "Higher humidity at a given temperature raises the heat index, so moister summers bring more days of dangerous humid heat."
PASS_B = "Urban surfaces store heat during the day and release it at night, which may raise local heat index values."
PASS_C = "Projections under a single high-emissions scenario do not span the range of plausible futures."


def _m(sid, paper, passage, role="core_candidate", scenario="unknown"):
    return {"statement_id": sid, "statement": passage.split(",")[0] + ".", "paper_item_id": paper, "canonical_paper": paper,
            "paper_sha256": hashlib.sha256(paper.encode()).hexdigest(), "json_path": "$.results", "span_start": 10,
            "span_end": 10 + len(passage), "verbatim_passage": passage, "evidence_role": role, "passage_type": "own_finding",
            "region": "United States", "scenario": scenario, "basis": "us_national"}


def _g(gid, stype, strength, members, label=None):
    return {"group_id": gid, "kind": "group" if label else "singleton", "statement_type": stype, "label": label,
            "role": "caveat" if stype == "caveat" else "driver", "claim_about": "other" if stype == "caveat" else "hazard_change_mechanism",
            "group_strength_run": strength, "strength_in_packet": strength, "n_members_run": len(members), "names_scenario": False,
            "n_specific": 0, "members": members}


GROUPS = [_g("LG-extreme_heat_v1-driver-001", "driver", "multi_source_supported",
             [_m("LS-7001-01", "7001", PASS_A), _m("LS-7002-01", "7002", PASS_A)], "Higher humidity raises the heat index."),
          _g("LG-extreme_heat_v1-mechanism-001", "mechanism", "single_source_supported", [_m("LS-7003-01", "7003", PASS_B)]),
          _g("LG-extreme_heat_v1-caveat-001", "caveat", "single_source_supported", [_m("LS-7004-01", "7004", PASS_C, scenario="RCP8.5")])]


def packet(pid, item_id):
    return spk.assemble_packet(f"SD2-{pid}", EX[pid], 3, item_id, GROUPS, NCA, {})


def good_reply(pk):
    d = pk["model_view"]["patterns"][0]["allowed_descriptors"]
    return {
        "prompt": "How is the number of summer days with a dangerous heat index (above 95 °F) projected to change in Alabama by "
                  "mid-century under a high-emissions scenario, and what drives that change?",
        "reference_answer": {
            "table_pattern": [{"sentence": f"Summer {d['quantity']} {d['direction']} in Alabama {d['horizon']} {d['scenario']}: "
                                           f"{d['magnitude_class']}.",
                               "pattern_ids": ["TP1-00009"]}],
            "literature_interpretation": [
                {"sentence": "Higher humidity at a given temperature raises the heat index.", "group_ids": ["LG-extreme_heat_v1-driver-001"], "hedged": False},
                {"sentence": "One study reports that urban surfaces may add to local humid heat.", "group_ids": ["LG-extreme_heat_v1-mechanism-001"], "hedged": True}],
            "integrated": "Dangerous humid-heat days become more common in Alabama by mid-century under a high-emissions scenario, "
                          "consistent with warmer, moister summers."},
        "rubric": {"required_points": [{"point": "states that the number of days increases", "weight": 3},
                                       {"point": "names humidity as a driver", "weight": 2}],
                   "acceptable_variants": ["more frequent dangerous humid heat"], "optional_points": ["urban heat", d["anchor_pair"]],
                   "disallowed_claims": ["RCP8.5 is a forecast"], "fatal_errors": ["says the number of days decreases"]},
        "guardrails": ["RCP8.5 is one high-emissions scenario, not a forecast and not the only plausible future."],
        "source_independent_answerability": "yes", "source_independence_note": "A general regional climate question.",
        "capability_tested": "joins a projected pattern to its driver", "system_task": "retrieves and explains the projected change",
        "key_relationships": "heat index, humidity, season, scenario", "evidence_needed": "direction of change; driver",
        "desired_output_characteristics": "direction, driver, caveat", "expected_knowledge_level": "general_climate_science"}


def bad_reply(pk):
    r = good_reply(pk)
    r["prompt"] = "According to the ClimRR table, by how much (12.5%) do heatindex_M85_Day95 days rise in Alaska?"
    r["reference_answer"]["table_pattern"] = [{"sentence": "Days rise by 99.9 in Alaska.", "pattern_ids": ["TP1-99999"]}]
    r["reference_answer"]["literature_interpretation"] = [
        {"sentence": "Urban surfaces add to humid heat (Smith et al., 2019).", "group_ids": ["LG-extreme_heat_v1-mechanism-001"], "hedged": False},
        {"sentence": "Humidity matters.", "group_ids": ["LG-extreme_heat_v1-driver-999"], "hedged": False}]
    return r


class _Mock:
    """`replies[key]` is the reply object, or a list of reply texts by turn."""

    def __init__(self, replies):
        self.calls = []
        mock = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                user = body["messages"][1]["content"]
                mock.calls.append(body)
                key = "TP1-00009" if "Pattern TP1-00009" in user else "TP1-00010"
                r = replies[key]
                text = r[len(body["messages"]) // 2 - 1] if isinstance(r, list) else "Here is the item: " + json.dumps(r)
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


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    pytest.importorskip("duckdb")
    base = tmp_path_factory.mktemp("litsynth")
    pdir, out = base / "packets", base / "out"
    pdir.mkdir()
    pks = {"TP1-00009": packet("TP1-00009", "BI-P2B-0001"), "TP1-00010": packet("TP1-00010", "BI-P2B-0002")}
    for pk in pks.values():
        (pdir / f"{pk['packet_id']}.json").write_text(json.dumps(pk), encoding="utf-8")
    mock = _Mock({"TP1-00009": good_reply(pks["TP1-00009"]), "TP1-00010": bad_reply(pks["TP1-00010"])})
    env = {**os.environ, "TOK" + "EN": "test-value"}
    cmd = [sys.executable, str(AGENT), "--packets", str(pdir), "--out", str(out), "--base-url", mock.url, "--model", "mock-model",
           "--source-commit", "abc1234", "--backoff", "0,0,0"]
    for _ in range(2):                                                    # the second run skips both packets
        p = subprocess.run(cmd, env=env, capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
    items = {json.loads(x)["item_id"]: json.loads(x) for x in (out / "items.jsonl").read_text().splitlines()}
    yield {"out": out, "mock": mock, "items": items, "pks": pks, "summary": json.loads((out / "summary.json").read_text())}
    mock.server.shutdown()


def _agent():
    pytest.importorskip("duckdb")
    sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location("litsynth_agent_v2", AGENT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_agent_is_pinned():
    assert sha256_file(AGENT) == AGENT_SHA256


def test_the_system_prompt():
    a = _agent()
    assert a.GENERATOR_VERSION == "litsynth_agent v3"
    assert a.CORRECTIVE_PROMPT == ('Your reply did not contain a JSON object with the keys "prompt" and "reference_answer". '
                                   "Return the complete JSON object.")
    assert hashlib.sha256(a.SYSTEM_PROMPT.encode("utf-8")).hexdigest() == SYSTEM_PROMPT_SHA256
    for phrase in ("Use ONLY facts in the packet", "closed-book question", "must NOT name or hint at any table", '"according to"',
                   "tagged with the pattern id", "must be hedged", "never present a single-source claim as consensus",
                   "a Fire Weather Index is meteorological fire danger, never fire occurrence", "hazard is not exposure",
                   "graded at the PATTERN level", "Never put a decimal number or an exact pattern value", "AS DIGITS",
                   '"allowed_descriptors"', 'Never write a number as a word ("sixteen", "forty-five", "twice", "double", "triple", "half"',
                   "Do not state horizon years unless the packet states them", "the threshold stays",
                   'A specific number may appear only under "optional_points"', "must be hedged"):
        assert phrase in a.SYSTEM_PROMPT
    text = AGENT.read_text(encoding="utf-8")
    assert "/eagl" + "e/" not in text and "/User" + "s/" not in text


def test_only_the_model_view_is_sent(run):
    assert len(run["mock"].calls) == 2
    for body in run["mock"].calls:
        user = body["messages"][1]["content"]
        assert body["temperature"] == 0 and body["max_tokens"] == 16000 and body["reasoning_effort"] == "low"
        assert len(body["messages"]) == 2                                  # a post-check failure is not retried
        assert "paper_sha256" not in user and "span_start" not in user and "heatindex_HIS" not in user and "LS-700" not in user
        assert "checks_input" not in user and "provenance" not in user and "exact_values" not in user
        assert '"allowed_descriptors"' in user and '"magnitude_class"' in user


def test_a_clean_item_passes_and_validates(run):
    it = run["items"]["BI-P2B-0001"]
    h = it["review"]["history"][0]
    assert it["review"]["status"] == "deterministic_pass" and h["event"] == "deterministic_pass" and h["reasons"] == []
    assert bi.schema_errors(it) == [] and bi.consistency_errors(it) == []
    rc = it["reference_components"]
    assert [s["group_id"] for s in rc["literature_mechanisms"]] == ["LG-extreme_heat_v1-driver-001", "LG-extreme_heat_v1-mechanism-001"]
    assert rc["literature_mechanisms"][1]["reference_scope"] == "single_study_observation" and rc["literature_caveats"] == []
    assert rc["table_patterns"][0]["pattern_id"] == "TP1-00009" and it["rubric"]["required_points"][0].startswith("[w=3] ")
    assert h["reference_answer_tagged"]["table_pattern"][0]["pattern_ids"] == ["TP1-00009"]
    assert it["generation"]["inputs_sha256"]["packet"] and it["source_leakage_check"]["pass"]
    v = bi.validity(it)
    assert all(v[k]["met"] for k in ("A_source_independent_prompt", "C_provenance_backed_literature", "D_explicit_evidence_strength"))
    assert not v["F_human_acceptance"]["met"]


def test_a_bad_item_is_rejected_with_its_reasons(run):
    it = run["items"]["BI-P2B-0002"]
    reasons = it["review"]["history"][0]["reasons"]
    assert it["review"]["status"] == "rejected_pre_review" and it["review"]["history"][0]["event"] == "deterministic_fail"
    joined = "\n".join(reasons)
    for needle in ("number 99.9 does not trace", "prompt leakage: exact value: 12.5%", "pattern id TP1-99999 not in the packet",
                   "group id LG-extreme_heat_v1-driver-999 not in the packet", "not marked hedged", "carries no hedge word",
                   "prompt leakage: ClimRR named", "prompt leakage: column name: heatindex_M85_Day95", "source phrase: According to",
                   "'et al.'", "year in parentheses"):
        assert needle in joined, needle
    assert run["summary"] == {**run["summary"], "items": 2, "deterministic_pass": 1, "deterministic_fail": 1, "corrective_retry_used": 0,
                              "reasoning_effort": "low", "max_tokens": 16000}
    h = run["items"]["BI-P2B-0001"]["review"]["history"][0]
    assert h["model_attempts"] == 1 and h["corrective_retry_used"] is False and h["reasoning_effort_applied"] is True
    assert h["finish_reason"] == "stop" and h["content_chars"] > 0 and h["reasoning_chars"] == 0


@pytest.mark.parametrize("second", ["good", "bad"])
def test_a_reply_without_the_item_gets_one_corrective_turn(tmp_path, second):
    pytest.importorskip("duckdb")
    pdir, out = tmp_path / "packets", tmp_path / "out"
    pdir.mkdir()
    pk = packet("TP1-00009", "BI-P2B-0001")
    (pdir / f"{pk['packet_id']}.json").write_text(json.dumps(pk), encoding="utf-8")
    texts = ["I will think about this.", json.dumps(good_reply(pk)) if second == "good" else "Still thinking."]
    mock = _Mock({"TP1-00009": texts})
    try:
        p = subprocess.run([sys.executable, str(AGENT), "--packets", str(pdir), "--out", str(out), "--base-url", mock.url,
                            "--model", "mock-model", "--source-commit", "abc1234", "--backoff", "0,0,0"],
                           env={**os.environ, "TOK" + "EN": "test-value"}, capture_output=True, text=True)
    finally:
        mock.server.shutdown()
    assert p.returncode == 0, p.stderr
    assert len(mock.calls) == 2
    msgs = mock.calls[1]["messages"]
    assert [m["role"] for m in msgs] == ["system", "user", "assistant", "user"] and msgs[2]["content"] == texts[0]
    assert msgs[3]["content"].startswith("Your reply did not contain a JSON object")
    it = json.loads((out / "items" / f"{pk['seed_id']}.json").read_text())
    h = it["review"]["history"][0]
    assert h["corrective_retry_used"] is True and h["model_attempts"] == 2 and h["first_turn"]["raw_response"] == texts[0]
    if second == "good":
        assert it["review"]["status"] == "deterministic_pass" and h["reasons"] == []
    else:
        assert it["review"]["status"] == "rejected_pre_review" and h["reasons"][0].startswith("parse: ") and "(corrective turn)" in h["reasons"][0]
    assert json.loads((out / "summary.json").read_text())["corrective_retry_used"] == 1


# --- post-check units ---------------------------------------------------------------------------------


def test_reference_numbers_ignore_scenarios_and_ordinals():
    assert bi.reference_numbers("Under RCP8.5 and SSP5-8.5 (CMIP6), by the 21st century, 1,211 cells rose 9.0 days") == ["1211", "9.0"]


def test_text_leakage_flags():
    flags = bi.text_leakage("As the paper shows (2019), LIT-000123 and LG-x-driver-001 and TP1-00009 and 7001", columns=[],
                            forbidden=["7001"])
    assert any(f.startswith("source phrase") for f in flags) and any("year in parentheses" in f for f in flags)
    assert "corpus id: LIT-000123" in flags and "internal id: LG-x-driver-001" in flags and "internal id: TP1-00009" in flags
    assert "packet source string: 7001" in flags
    assert bi.text_leakage("Mid-century (2045-2054) brings more humid heat.", columns=[]) == []


# --- post-checks v2 (D-055) on the hand-written packet ----------------------------------------------------


def _tripling_packet():
    p = copy.deepcopy(EX["TP1-00009"])
    p["computed_value_or_range"] = dict(p["computed_value_or_range"], mean_from="15.783252490397672", mean_to="44.933818281416101")
    return spk.assemble_packet("SD2-TP1-00009", p, 3, "BI-P2B-0001", GROUPS, NCA, {})


def _checked(reply, pk):
    a = _agent()
    common = {"model": "m", "prompt_hash": "0" * 64, "generation_timestamp": "2026-11-02T00:00:00Z", "packet_sha256": "0" * 64,
              "system_prompt_sha256": "0" * 64}
    item, tagged = a.assemble(reply, pk, common, bi.column_names())
    return bi.synthesis_post_checks(item, tagged, pk["checks_input"])


def _with_table_sentence(pk, sentence):
    r = good_reply(pk)
    r["reference_answer"]["table_pattern"] = [{"sentence": sentence, "pattern_ids": ["TP1-00009"]}]
    return r


def test_post_checks_v2_pass_a_copied_descriptor():
    pk = _tripling_packet()
    d = pk["model_view"]["patterns"][0]["allowed_descriptors"]
    assert d["magnitude_class"] == "roughly tripling" and d["anchor_pair"] == "from about 16 to about 45 days"
    res = _checked(good_reply(pk), pk)
    assert res["pass"], res["reasons"]
    assert res["check_version"] == "synthesis_post_checks v2" and res["checks"]["number_words_untraced"] == []


@pytest.mark.parametrize("sentence,needle", [
    ("Dangerous heat-index days rise from sixteen to forty-five days by mid-century.", "number-word 'forty-five'"),
    ("Dangerous heat-index days roughly triple by mid-century.", "number-word 'triple'"),
    ("Dangerous heat-index days rise twice as fast by mid-century.", "number-word 'twice'"),
    ("Dangerous heat-index days rise threefold by mid-century.", "number-word 'threefold'"),
    ("Dangerous heat-index days rise from about 15 to about 44 days.", "number 15 does not trace"),
    ("Dangerous heat-index days rise from 15.8 to 44.9 days.", "exact_value_in_graded_text 44.9"),
    ("Dangerous heat-index days rise to 44.933818281416101 days.", "exact_value_in_graded_text 44.933818281416101"),
])
def test_post_checks_v2_fail_number_words_rounding_and_exact_values(sentence, needle):
    pk = _tripling_packet()
    res = _checked(_with_table_sentence(pk, sentence), pk)
    assert not res["pass"] and any(needle in r for r in res["reasons"]), res["reasons"]


def test_post_checks_v2_trace_the_prompt_and_the_rubric_and_exempt_the_hedge():
    pk = _tripling_packet()
    r = good_reply(pk)
    r["prompt"] = r["prompt"].replace("projected to change", "projected to change over the next fifty years")
    r["rubric"]["required_points"].append({"point": "says the count roughly doubles", "weight": 1})
    res = _checked(r, pk)
    assert "prompt: number-word 'fifty' does not trace to an allowed descriptor in the packet" in res["reasons"]
    assert any("rubric.required_points: number-word 'doubles'" in x for x in res["reasons"])
    assert bi.untraced_number_words("One study reports more humid heat under RCP8.5, one high-emissions scenario.", []) == []
    assert bi.untraced_number_words("Days rise by about half again as many.", ["about half again as many"]) == []
