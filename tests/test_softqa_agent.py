"""Track C agent --- `scripts/litcollect/softqa_agent.py` v2, byte-identical to the delivered file (D-033).

Runs the pinned agent end to end against a local mock chat-completions server
and a synthetic `build_index.py` index, with the tracked units, QA types and a
synthetic paper list. Checks the deterministic pre-review check: an exact
passage passes with the right `[start,end)`; a fabricated passage, an unknown
unit or QA type is rejected; the place rule for `same` and `different`
geography relations; a units file with a value field is refused at startup;
restart skips finished papers; every `candidates.jsonl` record maps onto
`candidate_schema_v1.json` and validates.

Agent v2 additions: the passage locator (`exact` → `normalized` → `prefix_anchor`,
`passage_recovery` recorded, the paper's text as `verbatim_passage` and the
model's as `passage_as_proposed`); `passage_type` with background / method
passages rejected; more than three groups recorded, not truncated.

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
AGENT_SHA256 = "25a79a5b8bebbb67c8e080b05d08b736ee40ea62fbe3fc891d86cfab22f63b9c"  # v2; v1 was 159e2c5c...397c
V1_SYSTEM_PROMPT_SHA256 = "f2e493e179aa3619c8389e5c1756cce8f9a13693ddd586eae59138de33ee54f5"
V2_SYSTEM_PROMPT_SHA256 = "a44181ee23441118e67364d80004d0a796a747bfbd3f66a9cf89e987cdfef319"
UNITS = REPO_ROOT / "data" / "metadata" / "softqa" / "units_definitions_v1.json"
QA_TYPES = REPO_ROOT / "data" / "metadata" / "softqa" / "qa_types_v1.json"

OK_PASSAGE = "We study the fire weather index (FWI) across Oklahoma during summer."
PT_PASSAGE = "Fire weather index levels in central Portugal were high in our study region."
# v2 locator cases (paper 4004): typographic variants, an altered tail, a stitched proposal.
TYPO_PAPER = "The \u201cfire\u2011weather index\u201d in the southern plains rose\u202fsharply during the drought summer."
TYPO_PROPOSAL = 'The "fire-weather index" in the southern plains rose sharply during the drought summer.'
TAIL_SENTENCE = ("Across the southern plains, the simulated fire weather index exceeded the modeled historical "
                 "baseline in most summers of the record.")
TAIL_PROPOSAL = ("Across the southern plains, the simulated fire weather index exceeded the modeled historical "
                 "baseline in most summers.")
LONG_SENTENCE = ("In this section we describe in considerable detail the spatial pattern of the fire weather index "
                 "over many counties, river basins, elevation bands and vegetation zones that differ markedly in "
                 "fuel moisture, wind exposure, slope, aspect and land management history.")
STITCHED = LONG_SENTENCE[:90] + " Elsewhere the drought index was unrelated to anything we measured."
BACKGROUND = "The fire weather index is a numeric rating of fire intensity computed from weather observations."
APPENDED = TAIL_SENTENCE + " The drought index fell in the following decade everywhere."
DOCS = {
    "4001": {"title": "Fire weather in the southern plains",
             "abstract": "Background text first. " + OK_PASSAGE + " More text follows here.",
             "results": "Projected FWI under RCP8.5 is higher in Oklahoma by the end of the century."},
    "4003": {"title": "Fire weather in Iberia", "abstract": PT_PASSAGE},
    "4002": {"title": "Heat in California", "abstract": "The heat index in California is studied in summer."},
    "4004": {"title": "Fire weather recovery cases", "introduction": BACKGROUND + " Other text here.",
             "results": "Opening words. " + TYPO_PAPER + " " + TAIL_SENTENCE + " Then more text follows.",
             "discussion": "Discussion opens. " + LONG_SENTENCE + " The end."},
}
PAPERS = [{"item_id": "4001", "arm": "fire_weather_v1"}, {"item_id": "4003", "arm": "fire_weather_v1"},
          {"item_id": "4002", "arm": "extreme_heat_v1"}, {"item_id": "4004", "arm": "fire_weather_v1"}]


def group(passage, unit="P-COUNTY-1", qa="cross_source_validation", rel="same", geo="Oklahoma", role="study_area",
          section="abstract", ptype="own_finding"):
    return {"passage": passage, "passage_type": ptype, "section_key": section, "unit_id": unit, "qa_type": qa,
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
    "4004": [group(TYPO_PROPOSAL, unit="F-FWI", rel="unknown"),                    # 01 normalized
             group(TAIL_PROPOSAL, unit="F-FWI", rel="unknown"),                    # 02 prefix_anchor
             group(STITCHED, unit="F-FWI", rel="unknown"),                         # 03 stitched -> not_found
             group(BACKGROUND, unit="F-FWI", rel="unknown", ptype="background_or_definition"),  # 04 rejected
             group(BACKGROUND, unit="F-FWI", rel="unknown", ptype="method_description"),        # 05 rejected
             group(APPENDED, unit="F-FWI", rel="unknown")],                        # 06 genuine + appended
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
    assert [p.split("PAPER (item ", 1)[1].split(";", 1)[0] for p in later] == ["4003", "4002", "4004"]
    assert (run["out"] / "4001" / "result.json").read_bytes() == run["r1"]


def test_summary_counts_every_candidate(run):
    s = json.loads((run["out"] / "summary.json").read_text())
    assert s["papers"] == 4 and s["groups"] == 14
    assert (s["deterministic_pass"], s["rejected_pre_review"]) == (6, 8)


# --- schema mapping ----------------------------------------------------------------

def test_every_agent_record_maps_onto_the_schema_and_validates(run):
    recs = softqa.map_and_validate_jsonl(run["out"] / "candidates.jsonl")
    assert len(recs) == 14
    by_id = {r["candidate_identity"]["candidate_id"]: r for r in recs}
    p = by_id["C-4001-01"]
    assert p["paper_provenance"]["span_end"] - p["paper_provenance"]["span_start"] == len(OK_PASSAGE)
    assert p["paper_provenance"]["paper_sha256"] == sha256_file(run["src"] / "00" / "4001.json")
    assert p["candidate_identity"]["source_commit"] == "abc1234"
    assert p["mapping"]["invalid_agent_values"] == {}
    assert all(r["human_review"]["final_status"] is None for r in recs)
    assert by_id["C-4004-01"]["paper_provenance"]["claim_or_passage_type"] == "own_finding"
    assert "paper_provenance.claim_or_passage_type" not in by_id["C-4004-01"]["mapping"]["pending_stages"]
    assert all(r["candidate_identity"]["generator_version"] == "softqa_agent v2" for r in recs)


# --- agent v2 -------------------------------------------------------------------------

def _agent():
    pytest.importorskip("duckdb")
    import importlib.util

    spec = importlib.util.spec_from_file_location("softqa_agent_v2", AGENT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_v2_version_and_system_prompt_hash():
    import hashlib

    a = _agent()
    assert a.GENERATOR_VERSION == "softqa_agent v2"
    sha = hashlib.sha256(a.SYSTEM_PROMPT.encode("utf-8")).hexdigest()
    assert sha == V2_SYSTEM_PROMPT_SHA256 and sha != V1_SYSTEM_PROMPT_SHA256
    for phrase in ("OWN finding", "at most 3 groups", '"passage_type"', "background_or_definition",
                   "CANNOT be answered from the paper alone or from the table alone"):
        assert phrase in a.SYSTEM_PROMPT


def test_v2_exact_passage_is_recorded_as_exact(run):
    c = run["c"]["C-4001-01"]
    assert c["passage_recovery"] == "exact" and c["pre_review_checks"]["passage_recovery"] == "exact"
    assert c["verbatim_passage"] == c["passage_as_proposed"] == OK_PASSAGE


def test_v2_typographic_variant_is_recovered_as_normalized_with_correct_offsets(run):
    c = run["c"]["C-4004-01"]
    text = DOCS["4004"]["results"]
    start = text.find(TYPO_PAPER)
    assert c["status"] == "deterministic_pass" and c["passage_recovery"] == "normalized"
    assert (c["evidence"]["span_start"], c["evidence"]["span_end"]) == (start, start + len(TYPO_PAPER))
    assert c["verbatim_passage"] == TYPO_PAPER == text[c["evidence"]["span_start"]:c["evidence"]["span_end"]]
    assert c["passage_as_proposed"] == TYPO_PROPOSAL != c["verbatim_passage"]


def test_v2_altered_tail_is_recovered_as_one_sentence_that_reslices(run):
    c = run["c"]["C-4004-02"]
    text = DOCS["4004"]["results"]
    assert c["status"] == "deterministic_pass" and c["passage_recovery"] == "prefix_anchor"
    assert c["verbatim_passage"] == TAIL_SENTENCE                          # the paper's sentence, not the proposal
    assert text[c["evidence"]["span_start"]:c["evidence"]["span_end"]] == TAIL_SENTENCE
    assert c["passage_as_proposed"] == TAIL_PROPOSAL


def test_v2_stitched_proposal_with_low_overlap_is_not_found(run):
    c = run["c"]["C-4004-03"]
    assert c["status"] == "rejected_pre_review" and c["passage_recovery"] == "not_found"
    assert c["evidence"] is None and c["verbatim_passage"] is None and c["passage_as_proposed"] == STITCHED


@pytest.mark.parametrize("cid,ptype", [("C-4004-04", "background_or_definition"), ("C-4004-05", "method_description")])
def test_v2_background_or_method_passage_is_rejected(run, cid, ptype):
    c = run["c"][cid]
    assert c["status"] == "rejected_pre_review"
    assert c["pre_review_checks"]["passage_type"] == ptype and c["pre_review_checks"]["passage_type_pass"] is False
    assert c["pre_review_checks"]["span_reslice_pass"] is True             # rejected on passage type alone


def test_v2_a_genuine_sentence_with_an_appended_one_recovers_the_first_sentence_only(run):
    """Documented behaviour: word overlap is measured over the recovered sentence, so an appended foreign
    sentence does not block recovery; the reviewer sees the paper's sentence and the proposal side by side."""
    c = run["c"]["C-4004-06"]
    assert c["passage_recovery"] == "prefix_anchor" and c["verbatim_passage"] == TAIL_SENTENCE
    assert c["passage_as_proposed"] == APPENDED


def test_v2_more_than_three_groups_are_all_recorded_not_truncated(run):
    r = json.loads((run["out"] / "4004" / "result.json").read_text())
    assert r["n_groups_proposed"] == 6 and len(r["candidates"]) == 6
    assert [c["candidate_id"] for c in r["candidates"]] == [f"C-4004-{i:02d}" for i in range(1, 7)]
    assert json.loads((run["out"] / "4001" / "result.json").read_text())["n_groups_proposed"] == 4


def test_v2_missing_passage_type_fails_the_completeness_check(index, tmp_path):
    a = _agent()
    g = group(OK_PASSAGE)
    del g["passage_type"]
    secs = [{"section_idx": 1, "section_key": "abstract", "text": DOCS["4001"]["abstract"]}]
    units = {u["unit_id"]: u for u in json.loads(UNITS.read_text(encoding="utf-8"))["units"]}
    status, checks, _ = a.pre_review_check(g, secs, units["P-COUNTY-1"], ["oklahoma", "stephens"])
    assert status == "rejected_pre_review" and "passage_type" in checks["missing_fields"]



# --- the run-1 replay machinery on the synthetic run -----------------------------------

def test_sections_rebuilt_from_the_prompt_equal_the_papers_sections(run):
    from climrr import softqa_run1 as r1

    for iid, doc in DOCS.items():
        secs, truncated = r1.sections_from_prompt((run["out"] / iid / "prompt_user.txt").read_text(encoding="utf-8"))
        assert not truncated
        assert [(s["section_key"], s["text"]) for s in secs] == list(doc.items())


def test_replay_reproduces_the_agents_own_recovery(run, tmp_path):
    import shutil

    from climrr import softqa_run1 as r1

    work = tmp_path / "run"
    shutil.copytree(run["out"], work)
    (work / "excluded_files.csv").write_text(r1.excluded_text(work), encoding="utf-8")
    out = r1.replay(work, run=work, agent=_agent())
    by_id = {r["candidate_id"]: r for r in out["rows"]}
    assert out["input_checks"]["prompt_sha256_match"] == 4
    for cid, c in run["c"].items():
        if c["pre_review_checks"].get("unit_id_known") is False:
            continue
        assert by_id[cid]["v2_passage_recovery"] == c["passage_recovery"], cid
    assert out["recovered_reslice_ok"] == sum(1 for r in out["rows"] if r["v2_passage_recovery"] != "not_found")
    assert by_id["C-4004-01"]["typographic_codepoints"] == ["U+201C", "U+201D", "U+202F", "U+2011"] or \
        set(by_id["C-4004-01"]["typographic_codepoints"]) == {"U+201C", "U+201D", "U+202F", "U+2011"}
    (work / "4001" / "prompt_user.txt").write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="excluded_files.csv"):
        r1.replay(work, run=work, agent=_agent())
