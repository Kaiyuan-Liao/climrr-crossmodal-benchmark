"""Readability polish agent `scripts/litcollect/litpolish_agent.py` v1 and its invariance checks (D-063; work package P3a).

A synthesized item (litsynth_agent v4 `assemble` / `finish` on the real California heat packet v4, BI-P3-0001,
deterministic_pass) is polished against a local mock server: a faithful rewrite replaces the prompt and the integrated
answer (leakage check recomputed), keeps `pre_polish` in the `polish` history event and still validates against schema
v2; a rewrite that drops a place, adds a number, changes a hedge, adds a source word, loses a mechanism keyword or
shrinks too far is `polish_rejected` and the item's text is unchanged; a reply without the JSON gets one corrective
turn; an item that failed the synthesis checks is skipped. Each invariance check is also tested on its own.
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
from climrr import polish_checks as pc
from climrr import synthpackets_v4 as v4
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
AGENT = TOOLS / "litpolish_agent.py"
AGENT_SHA256 = "901e39540885b461fccb666803eb5d088ade229dc75253bc5901f3937a9f10dc"
SYSTEM_PROMPT = ("Rewrite for a general scientific reader: shorter sentences, plain words, same meaning. Do not add, remove or "
                 "change any fact, number, place, time phrase, hedge word (shows/suggests) or mechanism. Do not mention data, "
                 "tables, models, papers or studies beyond the hedge words already present. Return JSON {prompt, answer}.")
NCA = sd.nca_map()
SYN = pc.load_synonyms()
LABELS = ["Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat",
          "humidity magnifies heat stress and its effect grows with temperature"]
ORIG = {"prompt": "How are days hot and humid enough to be dangerous projected to change in California by mid-century under a "
                  "high-emissions future, and what drives that change?",
        "answer": "Dangerous humid-heat days become more common in California by mid-century under a high-emissions future. "
                  "Research shows that large-scale warming drives increases in extreme heat, and research suggests that humidity "
                  "magnifies heat stress."}
GOOD = {"prompt": "How will days hot and humid enough to be dangerous change in California by mid-century under a high-emissions "
                  "future, and why?",
        "answer": "By mid-century, under a high-emissions future, dangerous humid-heat days become more common in California. "
                  "Research shows that large-scale warming drives increases in extreme heat. Research suggests that humidity "
                  "magnifies heat stress."}


def _load(name, path):
    pytest.importorskip("duckdb")
    sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def item():
    """A deterministic_pass item from litsynth_agent v4 on the real packet, with the texts above."""
    synth = _load("litsynth_agent_v4_for_polish", TOOLS / "litsynth_agent.py")
    sys.path.insert(0, str(REPO_ROOT / "tests"))
    from test_litsynth_agent_v4 import HEAT, heat_reply
    pk = json.loads((v4.PACKETS_DIR / f"{HEAT}.json").read_text(encoding="utf-8"))
    r = heat_reply(pk)
    r["prompt"] = ORIG["prompt"]
    r["reference_answer"]["integrated"] = ORIG["answer"]
    common = {"model": "m", "prompt_hash": "0" * 64, "generation_timestamp": "2026-11-17T00:00:00Z", "packet_sha256": "0" * 64,
              "system_prompt_sha256": "0" * 64}
    it, tagged = synth.assemble(r, pk, common, bi.column_names())
    it = synth.finish(it, tagged, pk, common, bi.column_names())
    assert it["review"]["status"] == "deterministic_pass", it["review"]["history"][0]["reasons"]
    return it


class _Mock:
    def __init__(self, texts):
        self.calls = []
        mock = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                mock.calls.append(body)
                text = texts[len(body["messages"]) // 2 - 1]
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


def _run(tmp_path, items, texts):
    pytest.importorskip("duckdb")
    src, out = tmp_path / "run4", tmp_path / "polish"
    (src / "items").mkdir(parents=True)
    for it in items:
        sid = it["review"]["history"][0]["seed_id"]
        (src / "items" / f"{sid}.json").write_text(json.dumps(it), encoding="utf-8")
    mock = _Mock(texts)
    try:
        p = subprocess.run([sys.executable, str(AGENT), "--items", str(src), "--out", str(out), "--base-url", mock.url,
                            "--model", "mock-model", "--source-commit", "abc1234", "--backoff", "0,0,0"],
                           env={**os.environ, "TOK" + "EN": "test-value"}, capture_output=True, text=True)
    finally:
        mock.server.shutdown()
    assert p.returncode == 0, p.stderr
    recs = [json.loads(x) for x in (out / "polished.jsonl").read_text().splitlines()] if (out / "polished.jsonl").exists() else []
    outs = {json.loads(f.read_text())["item_id"]: json.loads(f.read_text()) for f in (out / "items").glob("*.json")}
    return mock, recs, outs, json.loads((out / "summary.json").read_text())


def test_the_agent_is_pinned_and_its_prompt_is_verbatim():
    assert sha256_file(AGENT) == AGENT_SHA256
    a = _load("litpolish_agent_v1", AGENT)
    assert a.GENERATOR_VERSION == "litpolish_agent v1" and a.SYSTEM_PROMPT == SYSTEM_PROMPT
    assert hashlib.sha256(a.SYSTEM_PROMPT.encode()).hexdigest() == hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()
    text = AGENT.read_text(encoding="utf-8")
    assert "/eagl" + "e/" not in text and "/User" + "s/" not in text
    assert "litsynth/run4" in text and "litpolish/run1" in text and "--reasoning-effort low" in text and "gpt-oss-120b" in text


def test_a_faithful_rewrite_is_used(tmp_path, item):
    mock, recs, outs, summary = _run(tmp_path, [item], [json.dumps(GOOD)])
    body = mock.calls[0]
    assert body["messages"][0]["content"] == SYSTEM_PROMPT and json.loads(body["messages"][1]["content"]) == ORIG
    assert body["temperature"] == 0 and body["reasoning_effort"] == "low"
    it = outs["BI-P3-0001"]
    assert it["prompt"] == GOOD["prompt"] and it["reference_answer"]["integrated"] == GOOD["answer"]
    ev = it["review"]["history"][-1]
    assert ev["event"] == "polish" and ev["status"] == "polished" and ev["pre_polish"] == ORIG and ev["reasons"] == []
    assert it["review"]["status"] == "deterministic_pass" and it["source_leakage_check"] == bi.leakage_check(GOOD["prompt"])
    assert bi.schema_errors(it) == [] and bi.consistency_errors(it) == []
    assert recs[0]["status"] == "polished" and summary["polished"] == 1 and summary["polish_rejected"] == 0


@pytest.mark.parametrize("change,needle", [
    (lambda r: r.update(answer=r["answer"].replace(" in California", "")), "answer: places differ"),
    (lambda r: r.update(answer=r["answer"].replace("more common", "more common, about 16 more")), "answer: numbers differ"),
    (lambda r: r.update(answer=r["answer"].replace("Research shows", "Research suggests")), "answer: hedges differ"),
    (lambda r: r.update(prompt=r["prompt"].replace("change in", "change, in the model, in")), "prompt: new source word 'model'"),
    (lambda r: r.update(answer=r["answer"].replace("large-scale warming drives", "climate change drives")),
     "answer: mechanism keyword 'warming' lost"),
    (lambda r: r.update(answer="Dangerous days rise in California by mid-century under a high-emissions future. Research shows "
                               "this; research suggests more."), "answer: length ratio"),
    (lambda r: r.update(prompt=r["prompt"].replace("high-emissions future", "RCP8.5 future")), "prompt: new leakage flag generality: RCP"),
])
def test_an_unfaithful_rewrite_is_rejected_and_the_text_kept(tmp_path, item, change, needle):
    bad = copy.deepcopy(GOOD)
    change(bad)
    _, recs, outs, summary = _run(tmp_path, [item], [json.dumps(bad)])
    it = outs["BI-P3-0001"]
    assert it["prompt"] == item["prompt"] and it["reference_answer"] == item["reference_answer"]
    ev = it["review"]["history"][-1]
    assert ev["status"] == "polish_rejected" and ev["pre_polish"] == ORIG and ev["rewrite"] == bad
    assert any(r.startswith(needle) for r in ev["reasons"]), ev["reasons"]
    assert recs[0]["status"] == "polish_rejected" and summary["polish_rejected"] == 1


def test_a_reply_without_json_gets_one_corrective_turn(tmp_path, item):
    mock, recs, outs, _ = _run(tmp_path, [item], ["Let me think.", json.dumps(GOOD)])
    assert len(mock.calls) == 2 and mock.calls[1]["messages"][-1]["content"].startswith("Your reply did not contain")
    assert recs[0]["status"] == "polished" and outs["BI-P3-0001"]["review"]["history"][-1]["corrective_retry_used"] is True
    mock, recs, outs, summary = _run(tmp_path / "b", [item], ["Let me think.", "Still thinking."])
    assert recs[0]["status"] == "polish_parse_failed" and outs["BI-P3-0001"]["prompt"] == item["prompt"]
    assert summary["polish_parse_failed"] == 1


def test_an_item_that_failed_synthesis_is_skipped(tmp_path, item):
    bad = copy.deepcopy(item)
    bad["review"]["status"] = "rejected_pre_review"
    mock, recs, outs, summary = _run(tmp_path, [bad], [json.dumps(GOOD)])
    assert mock.calls == [] and recs == [] and outs == {} and summary["skipped_not_deterministic_pass"] == ["BI-P3-0001"]


# --- the invariance checks on their own --------------------------------------------------------------------------


def _inv(polished, labels=LABELS):
    return pc.invariance(ORIG, polished, labels, NCA, SYN, columns=[])


def test_invariance_passes_the_faithful_rewrite():
    res = _inv(GOOD)
    assert res["pass"], res["reasons"]
    assert res["checks"]["answer"]["places"]["original"] == ["California"]
    assert res["checks"]["answer"]["hedges"]["original"] == ["shows", "suggests"]
    assert "warming" in res["checks"]["answer"]["mechanism_keywords_in_original"]


def test_a_listed_synonym_keeps_the_mechanism():
    p = copy.deepcopy(GOOD)
    p["answer"] = p["answer"].replace("humidity magnifies", "moisture magnifies")
    assert _inv(p)["pass"]
    p["answer"] = GOOD["answer"].replace("heat stress", "heat strain")             # "stress" has no listed synonym
    assert _inv(p)["reasons"] == ["answer: mechanism keyword 'stress' lost (no listed synonym present)"]


def test_place_names_take_the_longest_match():
    names = pc.place_names(NCA)
    assert pc.places("West Virginia and the Southern Great Plains, not Arkansas's Kansas", names) == \
        ["Arkansas", "Kansas", "Southern Great Plains", "West Virginia"]
    assert pc.places("the southeastern United States", names) == ["United States"]


def test_numbers_hedges_and_source_words():
    assert pc.numbers("from about 16 to about 45 days a summer, 1,211 cells") == ["1211", "16", "45"]
    assert pc.hedges("Research shows ...; research has shown; research suggests") == ["shown", "shows", "suggests"]
    assert pc.source_words("The model data and two studies") == ["data", "model", "studies"]
    assert pc.stem("feedbacks") == "feedback" and pc.stem("stress") == "stress" and pc.stem("gas") == "gas"


def test_the_synonym_list_is_pinned():
    assert SYN["version"] == "polish_synonyms_v1" and SYN["decision"] == "D-063" and "humidity" in SYN["synonyms"]
