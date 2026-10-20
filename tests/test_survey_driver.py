"""Track B Stage 2b/2c tooling --- `scripts/litcollect/survey_driver.py`, unmodified.

Runs the pinned driver end to end against a local mock chat-completions server
and a synthetic `build_index.py` index, with the tracked survey context clause
v1. Checks what the ruling asks of Stage 2b/2c (criteria 26--29): the reasoning-
field fallback, the sanitizer, the dictionary name first, restart, the
context-filtered count, and that every `candidates.json` is
`candidate_surface_form` with model and prompt provenance.
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

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
CONTEXT = REPO_ROOT / "data" / "metadata" / "litcollect" / "survey_context_clause_v1.txt"

#: Byte-identical to the files in trackb_scripts.tar.gz (SHA-256 8c3f75fe...0f59).
TOOL_SHA256 = {
    "survey_driver.py": "b3292e22f067f6f2388e1233ec17b521c753d6d955e54b67751798c98f340d3a",
    "probe_alcf_inference.py": "79181c48981c709b49b90d78fc8aaddffaf12d2f1bb0591b9a9daa3aad438c66",
}

DOCS = {
    "2001": {"t": "Fire weather index projections under climate change"},
    "2002": {"t": "The FWI and fire danger rating"},               # topical, no context term
    "2003": {"t": "Heat index rises with warming"},
    "2004": {"t": "Wind speed observations"},
    "2005": {"t": "fire weather index trends under RCP8.5"},       # context via the bareword rcp8
}
INVENTORY = {"concepts": [
    {"id": "DC-901", "name": "Fire Weather Index", "passage": "synthetic passage one", "page": 1},
    {"id": "DC-902", "name": "Heat Index", "passage": "synthetic passage two", "page": 2},
]}
#: Per concept name: (message fields the mock returns).
REPLIES = {
    # content null --- the terms arrive only in the reasoning field.
    "Fire Weather Index": {"content": None, "reasoning_content":
                           'thinking... ["fwi", "Fire Weather Index", "fire-weather index", '
                           '"FWI (index)", "one two three four five six seven"]'},
    "Heat Index": {"content": '["heat index", "apparent temperature"]'},
}


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _driver():
    spec = importlib.util.spec_from_file_location("survey_driver", TOOLS / "survey_driver.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- pins ----------------------------------------------------------------

def test_the_tools_are_byte_identical_to_the_delivered_files():
    assert {p: sha256_file(TOOLS / p) for p in TOOL_SHA256} == TOOL_SHA256


def test_no_tool_carries_an_absolute_path():
    for p in TOOL_SHA256:
        text = (TOOLS / p).read_text(encoding="utf-8")
        assert "/eagl" + "e/" not in text and "/User" + "s/" not in text


def test_context_clause_is_the_v1_context_minus_the_family_terms():
    rq_spec = importlib.util.spec_from_file_location("rq", TOOLS / "run_query.py")
    pytest.importorskip("duckdb")
    rq = importlib.util.module_from_spec(rq_spec)
    rq_spec.loader.exec_module(rq)
    q = REPO_ROOT / "artifacts" / "literature" / "litcorpus02" / "evidence" / "queries"
    fire = rq.parse((q / "fire_weather_v1_query.txt").read_text(encoding="utf-8"))[1]
    heat = rq.parse((q / "extreme_heat_v1_query.txt").read_text(encoding="utf-8"))[1]
    clause = rq.parse(CONTEXT.read_text(encoding="utf-8"))
    assert len(clause) == 1 and clause[0] == [t for t in fire if t in heat]
    assert set(fire) | set(heat) == set(clause[0]) | {
        "fire season", "fire danger", "public health", "heat wave", "heatwave"}


# --- the sanitizer, directly ----------------------------------------------

def test_sanitizer_drops_non_plain_long_and_duplicate_terms_and_caps_at_ten():
    sanitize = _driver().sanitize
    kept, dropped = sanitize("Fire Weather Index", [
        "FWI", "fire weather index", "FWI (index)", "fwi|x", "one two three four five six seven",
        "  Fire   Danger  ", *[f"term {i}" for i in range(20)],
    ])
    assert [k["term"] for k in kept] == [
        "fire weather index", "fwi", "fire danger", *[f"term {i}" for i in range(7)]]
    assert len(kept) == 10
    reasons = {d["term"]: d["reason"] for d in dropped}
    assert reasons["fire weather index"] == "duplicate"
    assert reasons["FWI (index)"] == reasons["fwi|x"] == "not a plain lowercase phrase"
    assert reasons["one two three four five six seven"] == "more than 6 words"


def test_dictionary_name_is_the_first_candidate_even_when_the_model_repeats_it():
    kept, dropped = _driver().sanitize("Heat Index", ["heat index", "HEAT INDEX", "hi"])
    assert kept[0] == {"term": "heat index", "source": "dictionary_name"}
    assert [d["source"] for d in dropped] == ["model", "model"]


def test_a_non_plain_dictionary_name_is_dropped_not_rewritten():
    """Driver behaviour, recorded: a name with parentheses, a dash or more than six
    words fails the sanitizer and is dropped with its reason --- never rewritten.
    7 of the 14 Stage 2a names fall here (see TRACKB_STAGE2_REPORT.md)."""
    kept, dropped = _driver().sanitize("Temperature (Annual)", ["annual mean temperature"])
    assert [k["source"] for k in kept] == ["model"]
    assert dropped[0] == {"term": "Temperature (Annual)", "reason": "not a plain lowercase phrase",
                          "source": "dictionary_name"}


def test_the_stage2a_inventory_loads_in_the_driver():
    items = _driver().load_inventory(REPO_ROOT / "data" / "metadata" / "dictionary_concepts.yaml")
    assert [c["id"] for c in items][:2] == ["DC-001", "DC-002"] and len(items) == 14


# --- end to end against a mock server --------------------------------------

class _Mock:
    def __init__(self):
        self.prompts: list[str] = []
        mock = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                prompt = body["messages"][0]["content"]
                mock.prompts.append(prompt)
                name = prompt.split("Dictionary name: ", 1)[1].split("\n", 1)[0]
                out = json.dumps({"model": body["model"], "choices": [
                    {"message": {"role": "assistant", **REPLIES[name]}}]}).encode()
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
def survey(tmp_path_factory):
    pytest.importorskip("duckdb")
    base = tmp_path_factory.mktemp("survey")
    src, idx, out = base / "src", base / "idx", base / "out"
    (src / "00").mkdir(parents=True)
    for d, obj in DOCS.items():
        (src / "00" / f"{d}.json").write_text(json.dumps(obj), encoding="utf-8")
    subprocess.run([sys.executable, str(TOOLS / "build_index.py"), "--root", str(src), "--out", str(idx)],
                   check=True, capture_output=True)
    inv = base / "inventory.json"
    inv.write_text(json.dumps(INVENTORY), encoding="utf-8")
    mock = _Mock()
    env = {**os.environ, "TOK" + "EN": "test-value"}  # fragments: keeps this file scannable
    cmd = [sys.executable, str(TOOLS / "survey_driver.py"), "--inventory", str(inv), "--index", str(idx),
           "--context", str(CONTEXT), "--out", str(out), "--base-url", mock.url, "--model", "mock-model"]
    first = subprocess.run(cmd + ["--limit", "1"], env=env, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    after_first = list(mock.prompts)
    row1 = (out / "DC-901" / "row.json").read_bytes()
    second = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert second.returncode == 0, second.stderr
    yield {"out": out, "mock": mock, "after_first": after_first, "row1": row1, "base_url": mock.url}
    mock.server.shutdown()


def test_reasoning_field_fallback_when_content_is_null(survey):
    c = json.loads((survey["out"] / "DC-901" / "candidates.json").read_text())
    assert c["model_parse_error"] is None
    assert c["model_raw_terms"][:3] == ["fwi", "Fire Weather Index", "fire-weather index"]
    assert [k["term"] for k in c["candidates"]] == ["fire weather index", "fwi", "fire-weather index"]


def test_restart_skips_completed_concepts(survey):
    assert len(survey["after_first"]) == 1 and "Dictionary name: Fire Weather Index" in survey["after_first"][0]
    later = survey["mock"].prompts[1:]
    assert len(later) == 1 and "Dictionary name: Heat Index" in later[0]
    assert (survey["out"] / "DC-901" / "row.json").read_bytes() == survey["row1"]


def test_context_filtered_count_is_topical_intersect_context(survey):
    out = survey["out"]
    ctx = set((out / "_context" / "ids.txt").read_text().split())
    assert ctx == {"2001", "2003", "2005"}
    expected = {"DC-901": (3, 2), "DC-902": (1, 1)}
    for cid, (n_topical, n_ctx) in expected.items():
        row = json.loads((out / cid / "row.json").read_text())
        topical = set((out / cid / "topical" / "ids.txt").read_text().split())
        assert row["topical_only_count"] == len(topical) == n_topical
        assert row["context_filtered_count"] == len(topical & ctx) == n_ctx
        assert set((out / cid / "topical_and_context_ids.txt").read_text().split()) == topical & ctx
        assert row["context_clause_sha256"] == sha256_file(CONTEXT)


def test_every_candidates_file_is_inert_with_model_and_prompt_provenance(survey):
    out = survey["out"]
    for cid in ("DC-901", "DC-902"):
        c = json.loads((out / cid / "candidates.json").read_text())
        assert c["status"] == "candidate_surface_form"
        assert c["concept_id"] == cid
        assert c["model"] == "mock-model" and c["endpoint"] == survey["base_url"]
        assert c["prompt_sha256"] == _sha((out / cid / "prompt.txt").read_text(encoding="utf-8"))
        assert c["date_utc"].endswith("Z")
        assert "not in concept_map.yaml" in c["note"]


def test_survey_table_lists_every_row_labelled_diagnostic(survey):
    out = survey["out"]
    lines = (out / "survey_table.csv").read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("concept_id,dictionary_name")
    assert {ln.split(",")[0] for ln in lines[1:]} == {"DC-901", "DC-902"}
    for cid in ("DC-901", "DC-902"):
        assert json.loads((out / cid / "row.json").read_text())["label"].startswith("diagnostic")


def test_survey_writes_nothing_into_the_repository(survey):
    """Candidates stay in the survey output dir: the concept map is untouched."""
    cm = REPO_ROOT / "data" / "metadata" / "concept_map.yaml"
    assert "candidate_surface_form" not in cm.read_text(encoding="utf-8")
