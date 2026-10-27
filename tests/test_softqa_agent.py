"""Track C agent --- `scripts/litcollect/softqa_agent.py`, byte-identical to the delivered file (D-033).

Runs the pinned agent end to end against a local mock chat-completions server
and a synthetic `build_index.py` index, with the tracked units, QA types and a
synthetic paper list. Checks the deterministic pre-review check: an exact
passage passes with the right `[start,end)`; a fabricated passage, an unknown
unit or QA type is rejected; the place rule for `same` and `different`
geography relations; a units file with a value field is refused at startup;
restart skips finished papers; every `candidates.jsonl` record maps onto
`candidate_schema_v1.json` and validates.

The Polaris invocation is in `src/climrr/softqa.py`'s docstring (the agent's
own docstring cannot change without breaking its pin).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from climrr import softqa
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
AGENT = TOOLS / "softqa_agent.py"
AGENT_SHA256 = "159e2c5c4f00608da37b1bc85556fecfd82dbd2e1a5abfd10c59a2e46061397c"
UNITS = REPO_ROOT / "data" / "metadata" / "softqa" / "units_definitions_v1.json"
QA_TYPES = REPO_ROOT / "data" / "metadata" / "softqa" / "qa_types_v1.json"

OK_PASSAGE = "We study the fire weather index (FWI) across Oklahoma during summer."
PT_PASSAGE = "Fire weather index levels in central Portugal were high in our study region."
DOCS = {
    "4001": {"title": "Fire weather in the southern plains",
             "abstract": "Background text first. " + OK_PASSAGE + " More text follows here.",
             "results": "Projected FWI under RCP8.5 is higher in Oklahoma by the end of the century."},
    "4003": {"title": "Fire weather in Iberia", "abstract": PT_PASSAGE},
    "4002": {"title": "Heat in California", "abstract": "The heat index in California is studied in summer."},
}
PAPERS = [{"item_id": "4001", "arm": "fire_weather_v1"}, {"item_id": "4003", "arm": "fire_weather_v1"},
          {"item_id": "4002", "arm": "extreme_heat_v1"}]


def group(passage, unit="P-COUNTY-1", qa="cross_source_validation", rel="same", geo="Oklahoma", role="study_area",
          section="abstract"):
    return {"passage": passage, "section_key": section, "unit_id": unit, "qa_type": qa,
            "example_question": "How does the table-side unit compare with the paper's finding?",
            "paper_side_fact": "x", "table_side_needed": "y", "paper_geography": geo, "paper_geography_role": role,
            "paper_time": "unknown", "paper_scenario": "unknown", "paper_concept": "fire weather index",
            "concept_relation": "direct", "geography_relation": rel, "link_rationale": "r",
            "unmatched_dimensions": ["time"], "confidence": "medium"}


REPLIES = {
    "4001": [group(OK_PASSAGE),                                                    # 01 pass
             group("Oklahoma fire weather index doubled by 2050 in our results."),  # 02 fabricated
             group(OK_PASSAGE, unit="P-NOPE"),                                      # 03 unknown unit
             group(OK_PASSAGE, qa="made_up_type")],                                 # 04 unknown qa_type
    "4003": [group(PT_PASSAGE, rel="same", geo="Portugal"),                         # 01 unit place absent
             group(PT_PASSAGE, rel="different", geo="central Portugal"),            # 02 own study area
             group(PT_PASSAGE, rel="different", geo="central Portugal", role="affiliation"),  # 03 wrong role
             group(PT_PASSAGE, unit="F-FWI", rel="unknown", geo="central Portugal")],  # 04 unplaced unit
    "4002": [],
}


class _Mock:
    def __init__(self):
        self.prompts: list[str] = []
        mock = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                user = body["messages"][1]["content"]
                mock.prompts.append(user)
                iid = user.split("PAPER (item ", 1)[1].split(";", 1)[0]
                content = "Here you go: " + json.dumps({"groups": REPLIES[iid]})
                out = json.dumps({"model": body["model"], "choices": [
                    {"message": {"role": "assistant", "content": content}}]}).encode()
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


def _cmd(idx, cands, out, url, units=UNITS):
    return [sys.executable, str(AGENT), "--index", str(idx), "--candidates", str(cands), "--units", str(units),
            "--qa-types", str(QA_TYPES), "--out", str(out), "--base-url", url, "--model", "mock-model",
            "--source-commit", "abc1234"]


@pytest.fixture(scope="module")
def index(tmp_path_factory):
    pytest.importorskip("duckdb")
    base = tmp_path_factory.mktemp("softqa_idx")
    src, idx = base / "src", base / "idx"
    (src / "00").mkdir(parents=True)
    for d, obj in DOCS.items():
        (src / "00" / f"{d}.json").write_text(json.dumps(obj), encoding="utf-8")
    subprocess.run([sys.executable, str(TOOLS / "build_index.py"), "--root", str(src), "--out", str(idx)],
                   check=True, capture_output=True)
    return {"idx": idx, "src": src}


@pytest.fixture(scope="module")
def run(index, tmp_path_factory):
    base = tmp_path_factory.mktemp("softqa_run")
    cands, out = base / "cands.json", base / "out"
    cands.write_text(json.dumps(PAPERS), encoding="utf-8")
    mock = _Mock()
    cmd = _cmd(index["idx"], cands, out, mock.url)
    first = subprocess.run(cmd + ["--limit", "1"], env=_env(), capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    after_first = list(mock.prompts)
    r1 = (out / "4001" / "result.json").read_bytes()
    second = subprocess.run(cmd, env=_env(), capture_output=True, text=True)
    assert second.returncode == 0, second.stderr
    cands_out = {c["candidate_id"]: c for c in
                 (json.loads(ln) for ln in (out / "candidates.jsonl").read_text().splitlines())}
    yield {"out": out, "mock": mock, "after_first": after_first, "r1": r1, "c": cands_out, "src": index["src"]}
    mock.server.shutdown()


# --- pins ------------------------------------------------------------------------

def test_the_agent_is_byte_identical_to_the_delivered_file():
    assert sha256_file(AGENT) == AGENT_SHA256


def test_the_agent_carries_no_absolute_path():
    text = AGENT.read_text(encoding="utf-8")
    assert "/eagl" + "e/" not in text and "/User" + "s/" not in text and "/hom" + "e/" not in text


# --- the deterministic pre-review check -------------------------------------------

def test_an_exact_passage_passes_with_the_correct_span(run):
    c = run["c"]["C-4001-01"]
    text = DOCS["4001"]["abstract"]
    start = text.find(OK_PASSAGE)
    assert c["status"] == "deterministic_pass"
    assert c["evidence"]["json_path"] == "$.abstract"
    assert (c["evidence"]["span_start"], c["evidence"]["span_end"]) == (start, start + len(OK_PASSAGE))
    assert text[c["evidence"]["span_start"]:c["evidence"]["span_end"]] == c["verbatim_passage"]
    assert c["place_hit"]["term"] == "oklahoma" and c["concept_hit"] is not None


def test_a_fabricated_passage_is_rejected_before_review(run):
    c = run["c"]["C-4001-02"]
    assert c["status"] == "rejected_pre_review"
    assert c["pre_review_checks"]["span_reslice_pass"] is False and c["evidence"] is None


def test_an_unknown_unit_or_qa_type_is_rejected(run):
    unit, qa = run["c"]["C-4001-03"], run["c"]["C-4001-04"]
    assert unit["status"] == "rejected_pre_review" and unit["pre_review_checks"]["unit_id_known"] is False
    assert qa["status"] == "rejected_pre_review" and qa["pre_review_checks"]["qa_type_known"] is False
    assert qa["pre_review_checks"]["span_reslice_pass"] is True        # rejected on qa_type alone


def test_same_geography_needs_the_unit_place_term_in_the_paper(run):
    c = run["c"]["C-4003-01"]
    assert c["status"] == "rejected_pre_review" and c["place_hit"] is None
    assert c["pre_review_checks"]["place_location_pass"] is False
    assert c["pre_review_checks"]["place_check_mode"] == "unit_place_in_paper"


def test_different_geography_needs_the_papers_own_study_area(run):
    ok, bad = run["c"]["C-4003-02"], run["c"]["C-4003-03"]
    assert ok["status"] == "deterministic_pass"
    assert ok["pre_review_checks"]["place_check_mode"] == "paper_names_own_place"
    assert bad["status"] == "rejected_pre_review" and bad["pre_review_checks"]["place_location_pass"] is False


def test_an_unplaced_family_unit_needs_no_place_term(run):
    c = run["c"]["C-4003-04"]
    assert c["status"] == "deterministic_pass" and c["pre_review_checks"]["place_location_pass"] is True


def test_the_prompt_carries_definitions_and_no_table_value(run):
    prompt = run["mock"].prompts[0]
    units = json.loads(UNITS.read_text(encoding="utf-8"))["units"]
    for u in units:
        assert u["definition"] in prompt
    for v in ("6.109", "6.083", "13.209", "25.08", "31.18", "increase"):
        assert v not in prompt
    rec = json.loads((run["out"] / "4001" / "result.json").read_text())["candidates"][0]
    assert rec["table_values_visible_to_generator"] is False and rec["answer_visible_to_generator"] is False


# --- startup refusal and restart -------------------------------------------------

def test_a_units_file_with_a_value_field_is_refused_at_startup(index, tmp_path):
    units = json.loads(UNITS.read_text(encoding="utf-8"))
    units["units"][0]["value"] = 1.0
    bad = tmp_path / "units.json"
    bad.write_text(json.dumps(units), encoding="utf-8")
    cands = tmp_path / "c.json"
    cands.write_text(json.dumps(PAPERS))
    mock = _Mock()
    r = subprocess.run(_cmd(index["idx"], cands, tmp_path / "out", mock.url, units=bad), env=_env(),
                       capture_output=True, text=True)
    mock.server.shutdown()
    assert r.returncode != 0 and "definitions only" in r.stderr and mock.prompts == []


def test_restart_skips_finished_papers(run):
    assert len(run["after_first"]) == 1 and "PAPER (item 4001;" in run["after_first"][0]
    later = run["mock"].prompts[1:]
    assert [p.split("PAPER (item ", 1)[1].split(";", 1)[0] for p in later] == ["4003", "4002"]
    assert (run["out"] / "4001" / "result.json").read_bytes() == run["r1"]


def test_summary_counts_every_candidate(run):
    s = json.loads((run["out"] / "summary.json").read_text())
    assert s["papers"] == 3 and s["groups"] == 8
    assert (s["deterministic_pass"], s["rejected_pre_review"]) == (3, 5)


# --- schema mapping ----------------------------------------------------------------

def test_every_agent_record_maps_onto_the_schema_and_validates(run):
    recs = softqa.map_and_validate_jsonl(run["out"] / "candidates.jsonl")
    assert len(recs) == 8
    by_id = {r["candidate_identity"]["candidate_id"]: r for r in recs}
    p = by_id["C-4001-01"]
    assert p["paper_provenance"]["span_end"] - p["paper_provenance"]["span_start"] == len(OK_PASSAGE)
    assert p["paper_provenance"]["paper_sha256"] == sha256_file(run["src"] / "00" / "4001.json")
    assert p["candidate_identity"]["source_commit"] == "abc1234"
    assert p["mapping"]["invalid_agent_values"] == {}
    assert all(r["human_review"]["final_status"] is None for r in recs)

