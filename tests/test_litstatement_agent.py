"""Literature-statement agent --- `scripts/litcollect/litstatement_agent.py` v2 (pilot P1, D-041, D-043).

Runs the pinned agent end to end against a local mock chat-completions server and
a synthetic `build_index.py` index. Checks the deterministic pre-check: an exact
passage passes with the right `[start,end)`; a fabricated passage, a `background`
passage, an over-long passage, an unknown enum and a digit-heavy general statement
are rejected; a digit-heavy `specific_result` passes; an `elsewhere_in_paper`
scenario keeps its value only if its quote re-slices exactly, else `unsupported`;
statements past six are recorded and flagged; the reasoning-field fallback
parses; restart skips finished papers; no units or table values reach the model.
v2: HTTP 5xx / connection errors / empty bodies are retried with `RETRY` lines; a
paper whose attempts all fail gets no result.json and is listed in
failed_papers.txt; a v1 result.json recording an HTTP error is migrated aside;
`base_url` / `model` / `endpoint_label` are recorded.
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
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from climrr import litstatements as ls
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
AGENT = ls.AGENT_PATH
AGENT_SHA256 = "f70edbb33929354c4a5a3d3786f72c49ad41d201032a778725f3d004a1d370d6"
SYSTEM_PROMPT_SHA256 = "fbedadd25a8a6a048983f9ed3c49997c73c4de771e9f5d689dacd9f56cb01fff"

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
             st(MECH, stype="caveat")],                                                        # 10 past six
    "5002": [],
    "5003": [st(HEAT, statement="Humidity amplifies heat-index increases under warming.", section="abstract")],
}


class _Mock:
    def __init__(self, failures=()):
        """`failures`: what the first calls return before a normal reply --- an HTTP status (int) or "empty"."""
        self.prompts: list[tuple[str, str]] = []
        self.failures = list(failures)
        mock = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                system, user = body["messages"][0]["content"], body["messages"][1]["content"]
                mock.prompts.append((system, user))
                iid = user.split("PAPER (item ", 1)[1].split(";", 1)[0]
                fail = mock.failures.pop(0) if mock.failures else None
                if isinstance(fail, int):
                    self.send_response(fail)
                    self.send_header("Content-Length", "11")
                    self.end_headers()
                    self.wfile.write(b"Bad Gateway")
                    return
                text = "" if fail == "empty" else "Answer: " + json.dumps({"statements": REPLIES[iid]})
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
            "--base-url", url, "--model", "mock-model", "--source-commit", "abc1234", "--backoff", "0,0,0"]


@pytest.fixture(scope="module")
def index(tmp_path_factory):
    pytest.importorskip("duckdb")
    base = tmp_path_factory.mktemp("litst_idx")
    src, idx = base / "src", base / "idx"
    (src / "00").mkdir(parents=True)
    for d, obj in DOCS.items():
        (src / "00" / f"{d}.json").write_text(json.dumps(obj), encoding="utf-8")
    subprocess.run([sys.executable, str(TOOLS / "build_index.py"), "--root", str(src), "--out", str(idx)],
                   check=True, capture_output=True)
    return idx


@pytest.fixture(scope="module")
def run(tmp_path_factory, index):
    base, idx = tmp_path_factory.mktemp("litst"), index
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
    assert a.GENERATOR_VERSION == ls.GENERATOR_VERSION == "litstatement_agent v2"
    assert hashlib.sha256(a.SYSTEM_PROMPT.encode("utf-8")).hexdigest() == SYSTEM_PROMPT_SHA256
    assert a.MAX_STATEMENTS == 6 and "at most 8 statements" not in a.SYSTEM_PROMPT
    for phrase in ("GENERAL statements", "at most 6 statements", "never restate it as fire occurrence",
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


def test_statements_past_six_are_recorded_and_flagged(run):
    r = json.loads((run["out"] / "5001" / "result.json").read_text())
    assert r["n_statements_proposed"] == 10 and len(r["statements"]) == 10
    assert [s["over_limit"] for s in r["statements"]] == [False] * 6 + [True] * 4


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


# --- v2: endpoint, retries, migration (D-043) ----------------------------------------------------------


def test_endpoint_label_is_derived_from_the_url():
    a = _agent()
    assert a.endpoint_label(a.DEFAULT_BASE_URL) == "metis"
    assert a.endpoint_label("https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1") == "sophia_vllm"
    assert a.endpoint_label("http://127.0.0.1:8000/v1") == "other"


def test_the_default_host_is_still_metis_and_the_caps_are_v2():
    text = AGENT.read_text(encoding="utf-8")
    assert 'DEFAULT_BASE_URL = "https://inference-api.alcf.anl.gov/resource_server/metis/api/v1"' in text
    assert 'ap.add_argument("--base-url", default=DEFAULT_BASE_URL)' in text
    assert 'ap.add_argument("--model", default="gpt-oss-120b")' in text
    assert 'ap.add_argument("--max-tokens", type=int, default=3500)' in text
    assert 'ap.add_argument("--timeout", type=int, default=300)' in text
    assert _agent().BACKOFF_SECONDS == (10, 30, 60)


def test_records_and_summary_carry_the_endpoint(run):
    r = json.loads((run["out"] / "5001" / "result.json").read_text())
    assert (r["base_url"], r["model"], r["endpoint_label"]) == (run["mock"].url, "mock-model", "other")
    assert all(x["endpoint_label"] == "other" and x["base_url"] == run["mock"].url for x in r["statements"])
    s = json.loads((run["out"] / "summary.json").read_text())
    assert (s["base_url"], s["model"], s["endpoint_label"]) == (run["mock"].url, "mock-model", "other")
    assert s["endpoints_in_results"] == {f"other mock-model {run['mock'].url}": 3}
    log = (run["out"] / "agent.log").read_text()
    assert f"endpoint_label=other base_url={run['mock'].url} model=mock-model" in log


def _one_paper(tmp_path, index, failures, iid="5003"):
    cands, out = tmp_path / "cands.json", tmp_path / "out"
    cands.write_text(json.dumps([p for p in PAPERS if p["item_id"] == iid]), encoding="utf-8")
    mock = _Mock(failures)
    try:
        proc = subprocess.run(_cmd(index, cands, out, mock.url), env=_env(), capture_output=True, text=True)
    finally:
        mock.server.shutdown()
    assert proc.returncode == 0, proc.stderr
    return out, mock, (out / "agent.log").read_text()


def test_two_502s_then_success_gives_one_record(tmp_path, index):
    out, mock, log = _one_paper(tmp_path, index, [502, 502])
    assert len(mock.prompts) == 3
    assert [l.split(" ", 1)[1] for l in log.splitlines() if " RETRY " in l] == [
        "RETRY paper=5003 attempt=2 reason=HTTP 502 Bad Gateway", "RETRY paper=5003 attempt=3 reason=HTTP 502 Bad Gateway"]
    r = json.loads((out / "5003" / "result.json").read_text())
    assert r["model_attempts"] == 3 and len(r["statements"]) == 1 and r["statements"][0]["status"] == "deterministic_pass"
    assert not (out / "failed_papers.txt").exists()


def test_an_empty_body_is_retried(tmp_path, index):
    out, mock, log = _one_paper(tmp_path, index, ["empty"])
    assert "RETRY paper=5003 attempt=2 reason=empty body" in log
    assert json.loads((out / "5003" / "result.json").read_text())["model_attempts"] == 2


def test_four_502s_leave_no_result_and_list_the_paper(tmp_path, index):
    out, mock, log = _one_paper(tmp_path, index, [502] * 4)
    assert len(mock.prompts) == 4 and log.count(" RETRY ") == 3
    assert "FAIL paper=5003 reason=HTTP 502 Bad Gateway" in log
    assert not (out / "5003" / "result.json").exists()
    assert (out / "failed_papers.txt").read_text() == "5003\n"
    assert json.loads((out / "summary.json").read_text())["papers"] == 0


def test_a_4xx_is_not_retried(tmp_path, index):
    out, mock, log = _one_paper(tmp_path, index, [401])
    assert len(mock.prompts) == 1 and " RETRY " not in log and "FAIL paper=5003 reason=HTTP 401" in log
    assert not (out / "5003" / "result.json").exists()


def test_a_connection_error_is_retried_then_failed(tmp_path, index):
    mock = _Mock()
    mock.server.shutdown()
    mock.server.server_close()                                   # nothing listens on the port any more
    cands, out = tmp_path / "cands.json", tmp_path / "out"
    cands.write_text(json.dumps(PAPERS[2:]), encoding="utf-8")
    proc = subprocess.run(_cmd(index, cands, out, mock.url), env=_env(), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    log = (out / "agent.log").read_text()
    assert log.count(" RETRY ") == 3 and "reason=URLError" in log and "FAIL paper=5003" in log
    assert (out / "failed_papers.txt").read_text() == "5003\n"


def test_an_http_error_result_is_migrated_and_reprocessed(tmp_path, index):
    out = tmp_path / "out"
    (out / "5003").mkdir(parents=True)
    stale = {"item_id": "5003", "model_parse_error": "HTTP 504", "statements": [], "n_statements_proposed": 0}
    (out / "5003" / "result.json").write_text(json.dumps(stale))
    keep = {"item_id": "5002", "model_parse_error": None, "statements": [], "n_statements_proposed": 0}
    (out / "5002").mkdir()
    (out / "5002" / "result.json").write_text(json.dumps(keep))
    out, mock, log = _one_paper(tmp_path, index, [])
    assert "MIGRATED paper=5003" in log and "MIGRATED paper=5002" not in log
    moved = list((out / "5003").glob("result.failed_*.json"))
    assert len(moved) == 1 and json.loads(moved[0].read_text()) == stale
    assert len(mock.prompts) == 1
    assert json.loads((out / "5003" / "result.json").read_text())["n_deterministic_pass"] == 1
    assert json.loads((out / "5002" / "result.json").read_text()) == keep


def test_sleep_paces_papers(tmp_path, index):
    cands, out = tmp_path / "cands.json", tmp_path / "out"
    cands.write_text(json.dumps(PAPERS[1:]), encoding="utf-8")
    mock = _Mock()
    try:
        proc = subprocess.run(_cmd(index, cands, out, mock.url) + ["--sleep", "2.5"], env=_env(), capture_output=True,
                              text=True)
    finally:
        mock.server.shutdown()
    assert proc.returncode == 0, proc.stderr
    stamps = [datetime.strptime(l.split(" ", 1)[0], "%Y-%m-%dT%H:%M:%SZ")
              for l in (out / "agent.log").read_text().splitlines() if " arm=" in l]
    assert len(stamps) == 2 and (stamps[1] - stamps[0]).total_seconds() >= 2
