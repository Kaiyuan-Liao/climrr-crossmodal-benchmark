"""Literature-statement agent --- `scripts/litcollect/litstatement_agent.py` v1 (pilot P1, D-041).

Runs the pinned agent end to end against a local mock chat-completions server and
a synthetic `build_index.py` index. Checks the deterministic pre-check: an exact
passage passes with the right `[start,end)`; a fabricated passage, a `background`
passage, an over-long passage, an unknown enum and a digit-heavy general statement
are rejected; a digit-heavy `specific_result` passes; an `elsewhere_in_paper`
scenario keeps its value only if its quote re-slices exactly, else `unsupported`;
statements past eight are recorded and flagged; the reasoning-field fallback
parses; restart skips finished papers; no units or table values reach the model.
The Polaris invocation is in `src/climrr/litstatements.py`.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from climrr import litstatements as ls
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
AGENT = ls.AGENT_PATH
AGENT_SHA256 = "42efdafd9d956fccff9697793048988b03bac85acbaad9c6e0634df0f17114d9"
SYSTEM_PROMPT_SHA256 = "998640ac2cfb53e5f8135a14a1d86686477c45dfa30d7e664b4960967e138cc8"

MECH = "Higher temperatures and lower relative humidity dry fine fuels and raise the fire weather index in summer."
BACKGROUND = "The fire weather index combines temperature, humidity, wind and precipitation into one rating."
HEAT = "Rising humidity together with warming increases the heat index more than temperature alone would suggest."
LONG = ("Across the many regions examined in this study the fire weather index shows " + "a consistent pattern, " * 40
        + "which we discuss below.")
DOCS = {
    "5001": {"title": "Fire weather drivers",
             "methods": "We use an RCP8.5 ensemble of regional simulations. " + BACKGROUND,
             "results": "Opening words. " + MECH + " " + LONG + " The end."},
    "5002": {"title": "Nothing here", "abstract": "A paper with nothing to extract."},
    "5003": {"title": "Humid heat", "abstract": "Intro. " + HEAT + " More text."},
}
PAPERS = [{"item_id": "5001", "arm": "fire_weather_v1"}, {"item_id": "5002", "arm": "fire_weather_v1"},
          {"item_id": "5003", "arm": "extreme_heat_v1"}]


def st(passage, *, statement="Hot, dry conditions raise fire weather danger.", stype="mechanism", ptype="own_finding",
       section="results", generality="general_mechanism", scenario="unknown", ssrc="unknown", squote="", sloc=""):
    return {"statement": statement, "statement_type": stype, "passage": passage, "section_key": section,
            "passage_type": ptype, "region": "unknown", "region_scope": "unknown", "scenario": scenario,
            "scenario_source": ssrc, "scenario_quote": squote, "scenario_location": sloc, "time": "unknown",
            "time_source": "unknown", "time_quote": "", "time_location": "", "generality": generality, "confidence": "medium"}


REPLIES = {
    "5001": [st(MECH),                                                                         # 01 pass, exact
             st("The fire weather index tripled everywhere in our simulations of the future."),  # 02 fabricated
             st(BACKGROUND, ptype="background", section="methods"),                            # 03 background
             st(MECH, statement="Summer FWI rises by 12.5% under warming."),                   # 04 digit-heavy, general
             st(MECH, statement="Summer FWI rises by 12.5% under warming.", generality="specific_result"),  # 05 pass
             st(MECH, scenario="RCP8.5", ssrc="elsewhere_in_paper", squote="RCP8.5 ensemble", sloc="methods"),  # 06 kept
             st(MECH, scenario="RCP8.5", ssrc="elsewhere_in_paper", squote="RCP 8.5 runs", sloc="methods"),     # 07 unsupported
             st(MECH, stype="speculation"),                                                    # 08 bad enum
             st(LONG),                                                                         # 09 > 700 chars
             st(MECH, stype="caveat")],                                                        # 10 past eight
    "5002": [],
    "5003": [st(HEAT, statement="Humidity amplifies heat-index increases under warming.", section="abstract")],
}


class _Mock:
    def __init__(self):
        self.prompts: list[tuple[str, str]] = []
        mock = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                system, user = body["messages"][0]["content"], body["messages"][1]["content"]
                mock.prompts.append((system, user))
                iid = user.split("PAPER (item ", 1)[1].split(";", 1)[0]
                text = "Answer: " + json.dumps({"statements": REPLIES[iid]})
                msg = {"role": "assistant", "content": None, "reasoning_content": text} if iid == "5003" else \
                    {"role": "assistant", "content": text}
                out = json.dumps({"model": body["model"], "choices": [{"message": msg}]}).encode()
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


def _env():
    return {**os.environ, "TOK" + "EN": "test-value"}  # fragments: keeps this file scannable


def _cmd(idx, cands, out, url):
    return [sys.executable, str(AGENT), "--index", str(idx), "--candidates", str(cands), "--out", str(out),
            "--base-url", url, "--model", "mock-model", "--source-commit", "abc1234"]


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    pytest.importorskip("duckdb")
    base = tmp_path_factory.mktemp("litst")
    src, idx = base / "src", base / "idx"
    (src / "00").mkdir(parents=True)
    for d, obj in DOCS.items():
        (src / "00" / f"{d}.json").write_text(json.dumps(obj), encoding="utf-8")
    subprocess.run([sys.executable, str(TOOLS / "build_index.py"), "--root", str(src), "--out", str(idx)],
                   check=True, capture_output=True)
    cands, out = base / "cands.json", base / "out"
    cands.write_text(json.dumps(PAPERS), encoding="utf-8")
    mock = _Mock()
    first = subprocess.run(_cmd(idx, cands, out, mock.url) + ["--limit", "1"], env=_env(), capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    after_first = list(mock.prompts)
    r1 = (out / "5001" / "result.json").read_bytes()
    second = subprocess.run(_cmd(idx, cands, out, mock.url), env=_env(), capture_output=True, text=True)
    assert second.returncode == 0, second.stderr
    recs = {r["statement_id"]: r for r in ls.load_statements(out / "statements.jsonl")}
    yield {"out": out, "mock": mock, "after_first": after_first, "r1": r1, "s": recs}
    mock.server.shutdown()


def _agent():
    pytest.importorskip("duckdb")
    sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location("litstatement_agent_v1", AGENT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- pins ------------------------------------------------------------------------------------


def test_the_agent_is_pinned():
    assert sha256_file(AGENT) == AGENT_SHA256


def test_version_and_system_prompt_hash():
    a = _agent()
    assert a.GENERATOR_VERSION == ls.GENERATOR_VERSION == "litstatement_agent v1"
    assert hashlib.sha256(a.SYSTEM_PROMPT.encode("utf-8")).hexdigest() == SYSTEM_PROMPT_SHA256
    for phrase in ("GENERAL statements", "at most 8 statements", "never restate it as fire occurrence",
                   '"elsewhere_in_paper"', '"specific_result"', "at most 700 characters"):
        assert phrase in a.SYSTEM_PROMPT


def test_the_agent_carries_no_absolute_path():
    text = AGENT.read_text(encoding="utf-8")
    assert "/eagl" + "e/" not in text and "/User" + "s/" not in text and "/hom" + "e/" not in text


def test_the_agent_reuses_the_v2_locator():
    from climrr.checksums import sha256_file as h

    assert "from softqa_agent import call_model, locate_passage" in AGENT.read_text(encoding="utf-8")
    assert h(TOOLS / "softqa_agent.py") == "25a79a5b8bebbb67c8e080b05d08b736ee40ea62fbe3fc891d86cfab22f63b9c"


# --- the pre-check -------------------------------------------------------------------------------


def test_an_exact_passage_passes_with_the_correct_span(run):
    r = run["s"]["S-5001-01"]
    text = DOCS["5001"]["results"]
    start = text.find(MECH)
    assert r["status"] == "deterministic_pass" and r["passage_recovery"] == "exact"
    assert (r["evidence"]["json_path"], r["evidence"]["span_start"], r["evidence"]["span_end"]) == ("$.results", start, start + len(MECH))
    assert r["verbatim_passage"] == MECH and r["table_values_visible_to_generator"] is False


@pytest.mark.parametrize("sid,check", [("S-5001-02", "span_reslice_pass"), ("S-5001-03", "passage_type_pass"),
                                       ("S-5001-04", "statement_value_pass"), ("S-5001-08", "enums_valid"),
                                       ("S-5001-09", "passage_length_pass")])
def test_rejections_name_the_failed_check(run, sid, check):
    r = run["s"][sid]
    assert r["status"] == "rejected_pre_review" and r["pre_review_checks"]["failed"] == [check]


def test_a_specific_result_may_carry_its_number(run):
    r = run["s"]["S-5001-05"]
    assert r["status"] == "deterministic_pass" and r["pre_review_checks"]["statement_numbers"] == ["12.5%"]


def test_elsewhere_scenario_needs_an_exact_quote(run):
    kept, lost = run["s"]["S-5001-06"], run["s"]["S-5001-07"]
    assert kept["scenario"]["check"] == "quote_exact" and kept["scenario"]["value"] == "RCP8.5"
    assert kept["scenario"]["quote_span"]["json_path"] == "$.methods"
    assert lost["scenario"]["check"] == "unsupported" and lost["scenario"]["value"] == "unsupported"
    assert lost["scenario"]["value_as_proposed"] == "RCP8.5"
    assert lost["status"] == "deterministic_pass"            # a context field becomes unsupported; not a rejection


def test_statements_past_eight_are_recorded_and_flagged(run):
    r = json.loads((run["out"] / "5001" / "result.json").read_text())
    assert r["n_statements_proposed"] == 10 and len(r["statements"]) == 10
    assert [s["over_limit"] for s in r["statements"]] == [False] * 8 + [True] * 2


def test_reasoning_field_fallback_is_parsed(run):
    r = run["s"]["S-5003-01"]
    assert r["status"] == "deterministic_pass" and r["verbatim_passage"] == HEAT


def test_digit_rule_spares_years_and_scenario_names():
    a = _agent()
    assert not a.digit_heavy("Under RCP8.5 and SSP5-8.5 in CMIP6, fire danger rises by the 2080s and the 21st century.")
    assert not a.digit_heavy("Days above a 105 °F heat index become more frequent.")
    assert a.digit_heavy("Days above 105 °F rise from 10 to 40.")
    assert a.digit_heavy("FWI rises 3.5 units.")


# --- prompt, restart, summary ------------------------------------------------------------------


def test_the_prompt_carries_no_units_or_values(run):
    system, user = run["mock"].prompts[0]
    assert "UNITS" not in user and "PERMITTED QUESTION TYPES" not in user
    for v in ("13.209", "6.109", "P-STATE-1", "P-CELL-1", "increase"):
        assert v not in user
    assert user.startswith("PAPER (item 5001;")


def test_restart_skips_finished_papers(run):
    assert len(run["after_first"]) == 1
    later = [u.split("PAPER (item ", 1)[1].split(";", 1)[0] for _, u in run["mock"].prompts[1:]]
    assert later == ["5002", "5003"]
    assert (run["out"] / "5001" / "result.json").read_bytes() == run["r1"]


def test_summary_counts_every_statement(run):
    s = json.loads((run["out"] / "summary.json").read_text())
    assert s["papers"] == 3 and s["statements"] == 11 and s["papers_over_limit"] == 1
    assert (s["deterministic_pass"], s["rejected_pre_review"]) == (6, 5)
    assert s["rejected_by_check"] == {"span_reslice_pass": 1, "passage_type_pass": 1, "statement_value_pass": 1,
                                      "enums_valid": 1, "passage_length_pass": 1}
    assert s["scenario_check"] == {"n/a": 9, "quote_exact": 1, "unsupported": 1}


def test_to_support_maps_a_passing_record(run):
    sup = ls.to_support(run["s"]["S-5001-01"], "test note")
    assert sup["span_end"] - sup["span_start"] == len(sup["verbatim_passage"]) and sup["json_path"] == "$.results"
    with pytest.raises(ValueError):
        ls.to_support(run["s"]["S-5001-02"], "x")
