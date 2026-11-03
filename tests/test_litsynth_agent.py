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
v3.1 / post-checks v2.1 (D-055a), on the real Florida rung-7 packet (v3a): "80 °F" passes in a literature sentence or a
rubric point that cites `LG-extreme_heat_v1-caveat-c1-024` (whose label and statement state it), and fails when another
group is cited, when the point has no `source_ids`, or in a table-pattern sentence.
v3.2 / post-checks v2.2 (D-055b): "one" is not a number-word ("one high-emissions scenario", "one study" pass anywhere;
"two" still traced); "has been reported" is a hedge; the fixed not-required sentence passes in every rubric list; a reply
whose failures are all format-class gets one corrective turn and every check runs again; a leakage failure mixed with
format failures gets none; an unparseable corrective reply keeps the first item, rejected.
Packets v3b (D-054a; the agent unchanged): on the real Florida rung-7 packet, a reply that cites the scenario caveat
`LG-extreme_heat_v1-pattern-c2-003` (typed `pattern` in the run, carried as a caveat) for the RCP8.5 vs RCP4.5 contrast,
hedged, passes every post-check and schema v2, and the group lands in `literature_caveats`.
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
AGENT_SHA256 = "f5778fbf54ea44794d40086b997a504971812fe8a4481f7fedefae5f6d4b8b5e"
FORMAT_CORRECTIVE_PROMPT_SHA256 = "919f52cb2612c6f7544a2d62f4488231a16092376e43ebef03e4a23ca7066d20"
SYSTEM_PROMPT_SHA256 = "9c79f45262b1a039e43edb46c928b6d32fa75f903eca34229d32838a734f5715"
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
    assert a.GENERATOR_VERSION == "litsynth_agent v3.2"
    assert a.CORRECTIVE_PROMPT == ('Your reply did not contain a JSON object with the keys "prompt" and "reference_answer". '
                                   "Return the complete JSON object.")
    assert hashlib.sha256(a.SYSTEM_PROMPT.encode("utf-8")).hexdigest() == SYSTEM_PROMPT_SHA256
    assert hashlib.sha256(a.FORMAT_CORRECTIVE_PROMPT.encode("utf-8")).hexdigest() == FORMAT_CORRECTIVE_PROMPT_SHA256
    for phrase in ("Use ONLY facts in the packet", "closed-book question", "must NOT name or hint at any table", '"according to"',
                   "tagged with the pattern id", "must be hedged", "never present a single-source claim as consensus",
                   "a Fire Weather Index is meteorological fire danger, never fire occurrence", "hazard is not exposure",
                   "graded at the PATTERN level", "Never put a decimal number or an exact pattern value", "AS DIGITS",
                   '"allowed_descriptors"', 'Never write a number as a word ("sixteen", "forty-five", "twice", "double", "triple", "half"',
                   "Do not state horizon years unless the packet states them", "the threshold stays",
                   'A specific number may appear only under "optional_points"', "must be hedged",
                   'Every required and optional point MUST carry "source_ids"', 'a threshold such as "80 °F"',
                   'Copy magnitude language VERBATIM from "allowed_descriptors": write "roughly tripling", never "threefold"',
                   'The rubric must contain NO numeral with a decimal point and NO exact pattern value at all, in any of its lists',
                   'write exactly: "' + a.NOT_REQUIRED_SENTENCE + '"',
                   'one of these hedge words: "one study", "a single study", "suggests", "has been reported"'):
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
    assert res["check_version"] == "synthesis_post_checks v2.2" and res["checks"]["number_words_untraced"] == []


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


# --- post-checks v2.1: the literature-number rule (D-055a) on the real Florida rung-7 packet -------------------

CAVEAT_80F = "LG-extreme_heat_v1-caveat-c1-024"
FLORIDA = spk.PACKETS_DIR / "PK-SD2-TP1-00075.json"


def _florida_reply(pk, cite=CAVEAT_80F, point_ids=(CAVEAT_80F,)):
    d = pk["model_view"]["patterns"][0]["allowed_descriptors"]
    point = {"point": "notes that one study may not compute the heat index below 80 °F", "weight": 1}
    if point_ids is not None:
        point["source_ids"] = list(point_ids)
    return {
        "prompt": "How is the number of summer days with a dangerous heat index (above 95 °F) projected to change in Florida by "
                  "mid-century under a high-emissions scenario, and what limits that projection?",
        "reference_answer": {
            "table_pattern": [{"sentence": f"Summer {d['quantity']} {d['direction']} in Florida {d['horizon']} {d['scenario']}: "
                                           f"{d['magnitude_class']}.", "pattern_ids": ["TP1-00075"]}],
            "literature_interpretation": [
                {"sentence": "One study notes that the heat index may not be computed when apparent temperature is below 80 °F.",
                 "group_ids": [cite], "hedged": True}],
            "integrated": "Dangerous humid-heat days become more common in Florida by mid-century under a high-emissions scenario."},
        "rubric": {"required_points": [{"point": "states that the number of days increases", "weight": 3, "source_ids": ["TP1-00075"]},
                                       point],
                   "acceptable_variants": [], "optional_points": [{"point": d["anchor_pair"], "source_ids": ["TP1-00075"]}],
                   "disallowed_claims": ["RCP8.5 is a forecast"], "fatal_errors": ["says the number of days decreases"]},
        "guardrails": ["RCP8.5 is one high-emissions scenario, not a forecast and not the only plausible future."],
        "source_independent_answerability": "yes", "source_independence_note": "A general regional climate question.",
        "capability_tested": "states a pattern and its limits", "system_task": "explains the projected change and its caveat",
        "key_relationships": "heat index, threshold, scenario", "evidence_needed": "direction of change; caveat",
        "desired_output_characteristics": "direction, caveat", "expected_knowledge_level": "general_climate_science"}


@pytest.fixture(scope="module")
def florida():
    pk = json.loads(FLORIDA.read_text(encoding="utf-8"))
    assert pk["version"] == "synthpackets v3b" and CAVEAT_80F in pk["checks_input"]["group_strength"]
    assert "80" not in pk["checks_input"]["allowed_numbers"]                     # not a pattern number: v2 would reject it
    assert any("80\u202f°F" in t for t in pk["checks_input"]["group_texts"][CAVEAT_80F])
    return pk


def _number_reasons(res, n="80"):
    return [r for r in res["reasons"] if f"number {n} " in r]


def test_post_checks_v2_1_allow_80f_where_the_caveat_is_cited(florida):
    res = _checked(_florida_reply(florida), florida)
    assert res["pass"], res["reasons"]
    assert res["checks"]["texts_traced_to_literature"] == ["literature_interpretation", "rubric.required_points"]
    assert res["checks"]["rubric_points_without_source_ids"] == 0


def test_post_checks_v2_1_reject_80f_without_the_caveat(florida):
    other = "LG-extreme_heat_v1-mechanism-c1-024"                                # in the packet, but does not state 80 °F
    res = _checked(_florida_reply(florida, cite=other, point_ids=(other,)), florida)
    assert _number_reasons(res) == [
        "literature_interpretation: number 80 does not trace to a pattern value or allowed descriptor in the packet",
        "rubric.required_points: number 80 does not trace to a pattern value or allowed descriptor in the packet"]
    res = _checked(_florida_reply(florida, point_ids=None), florida)            # the point carries no source_ids
    assert _number_reasons(res) == ["rubric.required_points: number 80 does not trace to a pattern value or allowed descriptor in the packet"]
    assert res["checks"]["rubric_points_without_source_ids"] == 1


def test_post_checks_v2_1_keep_the_v2_rule_in_table_sentences(florida):
    r = _florida_reply(florida)
    r["reference_answer"]["table_pattern"].append({"sentence": "Days with a heat index above 80 °F increase.",
                                                   "pattern_ids": ["TP1-00075"], "group_ids": [CAVEAT_80F]})
    res = _checked(r, florida)
    assert _number_reasons(res) == ["table_pattern: number 80 does not trace to a pattern value or allowed descriptor in the packet"]


def test_literature_trace_normalises_spellings_and_keeps_units():
    texts = {"G": ["Not applied below 80\u202f°F; ninety studies agree."]}
    lit = bi.literature_trace(["G"], texts)
    assert bi.untraced_numbers("below 80℉", set(), lit) == [] and bi.untraced_numbers("below 80 ° F", set(), lit) == []
    assert bi.untraced_numbers("below 80", set(), lit) == []                        # stated, with or without its unit
    assert bi.untraced_numbers("below 80 °C", set(), lit) == ["80"] and bi.untraced_numbers("below 81 °F", set(), lit) == ["81"]
    assert "ninety" in lit[2] and bi.literature_trace(["H"], texts) == (set(), set(), set())


# --- v3.2 / post-checks v2.2 (D-055b) ---------------------------------------------------------------------

SCEN = "under RCP8.5, one high-emissions scenario"


def test_post_checks_v2_2_one_is_not_a_number_word():
    pk = _tripling_packet()
    r = good_reply(pk)
    r["prompt"] = r["prompt"].replace("under a high-emissions scenario", "under one high-emissions scenario")
    r["reference_answer"]["integrated"] += " This is one high-emissions scenario, not a forecast."
    r["reference_answer"]["literature_interpretation"][1]["sentence"] = "One study suggests that urban surfaces may add to local humid heat."
    for k in ("disallowed_claims", "fatal_errors", "acceptable_variants"):
        r["rubric"][k].append("treats one high-emissions scenario as a forecast")
    r["rubric"]["required_points"].append({"point": "says the projection is one high-emissions scenario, not a forecast", "weight": 1})
    res = _checked(r, pk)
    assert res["pass"], res["reasons"]
    assert res["check_version"] == "synthesis_post_checks v2.2"
    assert bi.untraced_number_words("One study, a single study, an analysis, once, one high‑emissions scenario", []) == []
    assert bi.untraced_number_words("two studies and twenty-one days", []) == ["two", "twenty-one"]
    assert bi.untraced_number_words("doubles, threefold, half", []) == ["doubles", "threefold", "half"]


def test_post_checks_v2_2_two_is_still_traced():
    pk = _tripling_packet()
    res = _checked(_with_table_sentence(pk, "Dangerous heat-index days rise for two reasons by mid-century."), pk)
    assert "table_pattern: number-word 'two' does not trace to an allowed descriptor in the packet" in res["reasons"]


def test_post_checks_v2_2_has_been_reported_is_a_hedge_and_the_fixed_sentence_passes():
    pk = _tripling_packet()
    a = _agent()
    r = good_reply(pk)
    r["reference_answer"]["literature_interpretation"][1]["sentence"] = "It has been reported that urban surfaces add to local humid heat."
    r["rubric"]["optional_points"].append(a.NOT_REQUIRED_SENTENCE)
    r["rubric"]["disallowed_claims"].append(a.NOT_REQUIRED_SENTENCE)
    res = _checked(r, pk)
    assert res["pass"], res["reasons"]


def test_format_class_only():
    d = ["roughly tripling", "from about 16 to about 45 days", "about half again as many"]
    num = "rubric.optional_points: number {} does not trace to a pattern value or allowed descriptor in the packet"
    fmt = ["integrated: number-word 'threefold' does not trace to an allowed descriptor in the packet",
           "rubric.disallowed_claims: exact_value_in_graded_text 44.9 (exact values belong to provenance)",
           "literature_interpretation[1]: rests only on single-source groups but is not marked hedged",
           "literature_interpretation[1]: rests only on single-source groups but carries no hedge word",
           num.format("16.0"), num.format("3"), num.format("0.5")]
    assert bi.format_class_only(fmt, d)
    assert not bi.format_class_only([], d)
    assert not bi.format_class_only([num.format("17")], d)                        # a number no descriptor states
    for other in ("integrated leakage: ClimRR named", "prompt leakage: exact value: 12.5%", "table_pattern[0]: pattern id TP1-9 not in the packet",
                  "literature_interpretation[0]: group id LG-x not in the packet", "schema: x", "consistency: x", "parse: x"):
        assert not bi.format_class_only(fmt + [other], d), other
    assert [bi.number_word_value(w) for w in ("forty-five", "tripling", "threefold", "halved", "twice", "several-fold")] == [45, 3, 3, .5, 2, None]


def _format_reply(pk, leak=False):
    r = good_reply(pk)
    r["reference_answer"]["integrated"] = "Dangerous humid-heat days rise threefold in Alabama by mid-century."
    if leak:
        r["reference_answer"]["integrated"] += " ClimRR shows this."
    r["rubric"]["disallowed_claims"].append("requires the exact values 15.8 and 44.9")
    return r


def _run_agent(tmp_path, pk, texts):
    pdir, out = tmp_path / "packets", tmp_path / "out"
    pdir.mkdir()
    (pdir / f"{pk['packet_id']}.json").write_text(json.dumps(pk), encoding="utf-8")
    mock = _Mock({"TP1-00009": texts})
    try:
        p = subprocess.run([sys.executable, str(AGENT), "--packets", str(pdir), "--out", str(out), "--base-url", mock.url,
                            "--model", "mock-model", "--source-commit", "abc1234", "--backoff", "0,0,0"],
                           env={**os.environ, "TOK" + "EN": "test-value"}, capture_output=True, text=True)
    finally:
        mock.server.shutdown()
    assert p.returncode == 0, p.stderr
    it = json.loads((out / "items" / f"{pk['seed_id']}.json").read_text())
    return mock, it, json.loads((out / "summary.json").read_text())


@pytest.mark.parametrize("second", ["good", "unparseable"])
def test_format_only_failures_get_one_corrective_turn(tmp_path, second):
    pytest.importorskip("duckdb")
    pk = _tripling_packet()
    texts = [json.dumps(_format_reply(pk)), json.dumps(good_reply(pk)) if second == "good" else "Still thinking."]
    mock, it, summary = _run_agent(tmp_path, pk, texts)
    assert len(mock.calls) == 2
    msgs = mock.calls[1]["messages"]
    assert [m["role"] for m in msgs] == ["system", "user", "assistant", "user"] and msgs[2]["content"] == texts[0]
    assert msgs[3]["content"].startswith("Your item failed these format checks:\n- ")
    assert "number-word 'threefold'" in msgs[3]["content"] and "exact_value_in_graded_text 44.9" in msgs[3]["content"]
    h = it["review"]["history"][0]
    assert h["corrective_turn_used"] is True and h["corrective_class"] == "format" and h["model_attempts"] == 2
    assert h["corrective_retry_used"] is False and h["first_check"]["event"] == "deterministic_fail"
    assert h["first_check"]["raw_response"] == texts[0] and bi.format_class_only(h["first_check"]["reasons"], pk["checks_input"]["allowed_descriptors"])
    if second == "good":
        assert it["review"]["status"] == "deterministic_pass" and h["reasons"] == [] and h["raw_response"] == texts[1]
        assert summary["format_corrective_used"] == 1 and summary["format_corrective_pass"] == 1
    else:
        assert it["review"]["status"] == "rejected_pre_review"
        assert h["reasons"][:-1] == h["first_check"]["reasons"] and h["reasons"][-1].startswith("format corrective: no JSON object")
        assert it["reference_answer"]["integrated"].startswith("Dangerous humid-heat days rise threefold")
        assert summary["format_corrective_used"] == 1 and summary["format_corrective_pass"] == 0


def test_a_leakage_failure_mixed_with_format_failures_gets_no_turn(tmp_path):
    pytest.importorskip("duckdb")
    pk = _tripling_packet()
    mock, it, summary = _run_agent(tmp_path, pk, [json.dumps(_format_reply(pk, leak=True)), json.dumps(good_reply(pk))])
    assert len(mock.calls) == 1
    h = it["review"]["history"][0]
    assert it["review"]["status"] == "rejected_pre_review" and h["corrective_turn_used"] is False and h["corrective_class"] is None
    assert "integrated leakage: ClimRR named" in h["reasons"] and any("threefold" in r for r in h["reasons"])
    assert summary["format_corrective_used"] == 0


SCENARIO_CAVEAT = "LG-extreme_heat_v1-pattern-c2-003"


def test_packets_v3b_a_scenario_caveat_reply_passes_and_is_a_literature_caveat(florida):
    assert florida["rank_rule"] == "DR-SEED-RANK-3a" and "rung_instruction" in florida["model_view"]
    g = next(x for x in florida["provenance"]["groups"] if x["group_id"] == SCENARIO_CAVEAT)
    assert (g["role"], g["statement_type"], g["statement_type_run"]) == ("caveat", "caveat", "pattern")
    r = _florida_reply(florida)
    r["prompt"] = ("How does the projected change in summer days with a dangerous heat index (above 95 °F) in Florida by mid-century "
                   "depend on the emissions scenario, and what caveats apply?")
    r["reference_answer"]["literature_interpretation"].append(
        {"sentence": "One study reports that heat-wave duration is projected to be about one day longer under the high-emission "
                     "RCP8.5 scenario than under the moderate RCP4.5 scenario.", "group_ids": [SCENARIO_CAVEAT], "hedged": True})
    r["rubric"]["optional_points"].append({"point": "contrasts RCP8.5 with the moderate RCP4.5 scenario", "source_ids": [SCENARIO_CAVEAT]})
    res = _checked(r, florida)
    assert res["pass"], res["reasons"]
    a = _agent()
    common = {"model": "m", "prompt_hash": "0" * 64, "generation_timestamp": "2026-11-02T00:00:00Z", "packet_sha256": "0" * 64,
              "system_prompt_sha256": "0" * 64}
    item, _ = a.assemble(r, florida, common, bi.column_names())
    assert [s["group_id"] for s in item["reference_components"]["literature_caveats"]] == [CAVEAT_80F, SCENARIO_CAVEAT]
    assert bi.schema_errors(item) == []
