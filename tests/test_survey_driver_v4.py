"""Track B run 2 tooling --- `scripts/litcollect/survey_driver.py` v4 (D-027, B2--B4).

Against a local mock chat-completions server and a synthetic `build_index.py` index:

- `--mode measure` (default) writes byte-identical outputs to v3 (the driver survey run 1
  executed, recovered from git) for the same inputs, under a frozen clock;
- `--mode family`: prompt F, JSON-object parsing (reasoning-field fallback included),
  `family.json` with exactly the ruling's fields and `status: candidate_family`, run-1 measure
  counts copied beside the family counts, the side-by-side table;
- normalization under the frozen table, original kept, rule ids recorded, 6/10 word limits;
- fail-closed checks: the context cache, the run-1 rows, the normalization table hash.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
DRIVER = TOOLS / "survey_driver.py"
CONTEXT = REPO_ROOT / "data" / "metadata" / "litcollect" / "survey_context_clause_v1.txt"
NORM_TABLE = REPO_ROOT / "data" / "metadata" / "litcollect" / "normalization_table_v1.yaml"

#: v3 = the driver survey run 1 executed, as committed on main before this package.
V3_COMMIT, V3_SHA256 = "d7032de", "e1fb664c98e4ff866bb348c8930bfc1b9243957441b8a19ea0893e0b711af4cd"
NORM_TABLE_SHA256 = "80a5e0e386dfe8a984e1a5ba2ace781d15601f9b0723b75d238b6de5d1226e03"

DOCS = {
    "3001": {"t": "Fire weather index projections under climate change"},
    "3002": {"t": "The FWI and fire danger rating"},
    "3003": {"t": "Heat index rises with warming"},
    "3004": {"t": "Days with heat index above 95 degrees F under climate change"},
    "3005": {"t": "Apparent temperature in cities"},
    "3006": {"t": "Heat stress at 100 percent humidity"},
}
CONTEXT_IDS = {"3001", "3003", "3004"}
THRESHOLD = "Number of Summer days with daily max heat index above 95 F"
INVENTORY = {"concepts": [
    {"id": "DC-901", "name": "Fire Weather Index", "passage": "synthetic passage one", "page": 1},
    {"id": "DC-902", "name": "Heat Index", "passage": "synthetic passage two", "page": 2},
    {"id": "DC-911", "name": THRESHOLD, "passage": "synthetic passage three", "page": 3},
]}
MEASURE_REPLIES = {
    "Fire Weather Index": {"content": None, "reasoning_content": 'thinking... ["fwi", "Fire Weather Index"]'},
    "Heat Index": {"content": '["heat index", "95°f"]'},
    THRESHOLD: {"content": '["100%", "95°f"]'},
}
FAMILY_REPLIES = {
    # content null; the reasoning field holds a non-JSON brace and a draft before the answer.
    "Fire Weather Index": {"content": None, "reasoning_content":
                           'Think {briefly}. Draft: {"candidate_family": "draft"}. Final: '
                           '{"candidate_family": "fire_weather_index", '
                           '"family_surface_forms": ["fire weather index", "FWI", "fire danger"]}'},
    "Heat Index": {"content": json.dumps({"candidate_family": "heat_index", "family_surface_forms": [
        "heat index", "apparent temperature", "days with heat index above 95°f", "100%",
        "one two three four five six seven", "Heat Index"]}, ensure_ascii=False)},
    THRESHOLD: {"content": "I cannot answer that."},
}
FAMILY_JSON_FIELDS = {
    "dictionary_concept_id", "dictionary_passage", "model_id", "endpoint", "prompt_sha256", "candidate_family",
    "candidate_family_surface_forms", "date", "status", "model_raw_response_excerpt", "parse_error"}
FROZEN_CLOCK = """import time
_gmtime = time.gmtime
time.time = lambda: 1760000000.0
time.gmtime = lambda secs=None: _gmtime(1760000000 if secs is None else secs)
"""


def _driver():
    spec = importlib.util.spec_from_file_location("survey_driver_v4", DRIVER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
                replies = FAMILY_REPLIES if '"candidate_family"' in prompt else MEASURE_REPLIES
                out = json.dumps({"model": body["model"], "choices": [
                    {"message": {"role": "assistant", **replies[name]}}]}).encode()
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


class _Env:
    """A synthetic index, the inventory, a mock server and a runner for the driver."""

    def __init__(self, base):
        self.base = base
        src, self.idx = base / "src", base / "idx"
        (src / "00").mkdir(parents=True)
        for d, obj in DOCS.items():
            (src / "00" / f"{d}.json").write_text(json.dumps(obj), encoding="utf-8")
        subprocess.run([sys.executable, str(TOOLS / "build_index.py"), "--root", str(src), "--out", str(self.idx)],
                       check=True, capture_output=True)
        self.inv = base / "inventory.json"
        self.inv.write_text(json.dumps(INVENTORY), encoding="utf-8")
        self.mock = _Mock()

    def run(self, out, *extra, driver=DRIVER, pythonpath=None):
        env = {**os.environ, "TOK" + "EN": "test-value",  # fragments: keeps this file scannable
               "PYTHONPATH": os.pathsep.join(pythonpath or [str(REPO_ROOT / "src")])}
        cmd = [sys.executable, str(driver), "--inventory", str(self.inv), "--index", str(self.idx),
               "--context", str(CONTEXT), "--out", str(out), "--base-url", self.mock.url, "--model", "mock-model",
               *extra]
        return subprocess.run(cmd, env=env, capture_output=True, text=True, cwd=self.base)


@pytest.fixture(scope="module")
def env(tmp_path_factory):
    pytest.importorskip("duckdb")
    e = _Env(tmp_path_factory.mktemp("v4"))
    yield e
    e.mock.server.shutdown()


@pytest.fixture(scope="module")
def runs(env):
    """Run 1 in measure mode, then run 2 in family mode over it (first --limit 1, then the rest)."""
    run1, run2 = env.base / "run1", env.base / "run2"
    r = env.run(run1)
    assert r.returncode == 0, r.stderr
    first = env.run(run2, "--mode", "family", "--run1", str(run1), "--limit", "1")
    assert first.returncode == 0, first.stderr
    n_after_first = len(env.mock.prompts)
    row1 = (run2 / "DC-901" / "row.json").read_bytes()
    second = env.run(run2, "--mode", "family", "--run1", str(run1))
    assert second.returncode == 0, second.stderr
    return {"run1": run1, "run2": run2, "row1": row1, "n_after_first": n_after_first}


def _row(d, cid):
    return json.loads((d / cid / "row.json").read_text(encoding="utf-8"))


def _family(d, cid):
    return json.loads((d / cid / "family.json").read_text(encoding="utf-8"))


# --- pins ----------------------------------------------------------------------

def test_v3_is_recoverable_from_git_at_its_recorded_hash():
    blob = subprocess.run(["git", "show", f"{V3_COMMIT}:scripts/litcollect/survey_driver.py"], cwd=REPO_ROOT,
                          capture_output=True, check=True).stdout
    assert hashlib.sha256(blob).hexdigest() == V3_SHA256


def test_prompt_f_and_the_normalization_pin():
    d = _driver()
    assert d.NORM_TABLE_SHA256 == NORM_TABLE_SHA256 == sha256_file(NORM_TABLE)
    assert '"candidate_family"' in d.PROMPT_F and '"family_surface_forms"' in d.PROMPT_F
    assert "no place names, years, scenario names, thresholds or statistics" in d.PROMPT_F
    filled = d.fill_prompt_f(8, "Heat Index", "a passage")
    assert "up to 8 lowercase" in filled and "Dictionary name: Heat Index\nDictionary passage: a passage" in filled
    assert d.PROMPT_TEMPLATE.startswith("You are helping build a lexical search")  # v3 prompt kept


def test_the_docstring_gives_the_polaris_run2_invocation():
    doc = _driver().__doc__
    for part in ('PYTHONPATH="$CLIMRR_REPO/src"', "--mode family", "--run1 survey/run1", "--out survey/run2",
                 "--index index/full_705k_v2_filtered"):
        assert part in doc


# --- measure mode is v3, byte for byte --------------------------------------------

def test_measure_mode_outputs_are_byte_identical_to_v3(env, tmp_path):
    v3dir, clock = tmp_path / "v3", tmp_path / "clock"
    v3dir.mkdir(); clock.mkdir()
    blob = subprocess.run(["git", "show", f"{V3_COMMIT}:scripts/litcollect/survey_driver.py"], cwd=REPO_ROOT,
                          capture_output=True, check=True).stdout
    (v3dir / "survey_driver.py").write_bytes(blob)
    shutil.copyfile(TOOLS / "run_query.py", v3dir / "run_query.py")
    (clock / "sitecustomize.py").write_text(FROZEN_CLOCK, encoding="utf-8")
    trees = {}
    for tag, driver in (("v3", v3dir / "survey_driver.py"), ("v4", DRIVER)):
        out = env.base / "same_out"           # the same path for both: the log records it
        for extra in (["--limit", "1"], []):  # a restart, as in run 1
            r = env.run(out, *extra, driver=driver, pythonpath=[str(clock)])
            assert r.returncode == 0, r.stderr
        trees[tag] = {p.relative_to(out).as_posix(): p.read_bytes() for p in sorted(out.rglob("*")) if p.is_file()}
        shutil.move(out, tmp_path / f"out_{tag}")
    assert trees["v3"].keys() == trees["v4"].keys()
    assert [k for k in trees["v3"] if trees["v3"][k] != trees["v4"][k]] == []
    assert "DC-911/candidates.json" in trees["v4"] and "survey.log" in trees["v4"]


def test_measure_mode_without_normalize_never_imports_termnorm(env, tmp_path):
    r = env.run(tmp_path / "m", "--only", "DC-902", pythonpath=[str(tmp_path / "nothing")])
    assert r.returncode == 0, r.stderr
    assert "surface_forms" not in json.loads((tmp_path / "m" / "DC-902" / "candidates.json").read_text())


# --- family mode ---------------------------------------------------------------------

def test_family_json_has_exactly_the_ruling_fields_and_status_candidate_family(runs):
    for cid in ("DC-901", "DC-902", "DC-911"):
        fam = _family(runs["run2"], cid)
        assert set(fam) == FAMILY_JSON_FIELDS
        assert fam["status"] == "candidate_family" and fam["dictionary_concept_id"] == cid
        assert fam["model_id"] == "mock-model" and fam["date"].endswith("Z")
        assert fam["dictionary_passage"] == next(c["passage"] for c in INVENTORY["concepts"] if c["id"] == cid)
        prompt = (runs["run2"] / cid / "prompt.txt").read_text(encoding="utf-8")
        assert fam["prompt_sha256"] == hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        assert prompt == _driver().fill_prompt_f(8, next(c["name"] for c in INVENTORY["concepts"] if c["id"] == cid),
                                                 fam["dictionary_passage"])


def test_json_object_parsed_from_the_reasoning_field_last_object_wins(runs):
    fam = _family(runs["run2"], "DC-901")
    assert fam["candidate_family"] == "fire_weather_index" and fam["parse_error"] is None
    assert [r["original"] for r in fam["candidate_family_surface_forms"]] == ["fire weather index", "FWI", "fire danger"]
    assert [r["search_term"] for r in fam["candidate_family_surface_forms"]] == ["fire weather index", "fwi", "fire danger"]


def test_normalization_is_applied_and_recorded_original_kept(runs):
    recs = {r["original"]: r for r in _family(runs["run2"], "DC-902")["candidate_family_surface_forms"]}
    t = recs["days with heat index above 95°f"]
    assert t["normalized"] == t["search_term"] == "days with heat index above 95 degrees f"
    assert t["rules_applied"] == ["N-3"] and t["searched"] is True and t["reason"] is None
    assert recs["100%"]["search_term"] == "100 percent" and recs["100%"]["rules_applied"] == ["N-7"]
    assert recs["heat index"]["rules_applied"] == [] and recs["heat index"]["normalized"] == "heat index"
    # 6 words stays the limit for a form no rule changed; 10 for a normalized one (8 words here).
    assert recs["one two three four five six seven"]["reason"] == "more than 6 words"
    assert recs["one two three four five six seven"]["searched"] is False
    assert recs["Heat Index"]["reason"] == "duplicate"
    assert _row(runs["run2"], "DC-902")["sanitizer_word_limits"] == {"unnormalized": 6, "normalized": 10}


def test_family_counts_beside_the_run1_measure_counts(runs):
    run1, run2 = runs["run1"], runs["run2"]
    ctx = set((run2 / "_context" / "ids.txt").read_text().split())
    assert ctx == CONTEXT_IDS
    expected = {"DC-901": ({"3001", "3002"}, (2, 1)), "DC-902": ({"3003", "3004", "3005", "3006"}, (2, 2))}
    for cid, (ids, measure) in expected.items():
        row, m = _row(run2, cid), _row(run1, cid)
        topical = set((run2 / cid / "topical" / "ids.txt").read_text().split())
        assert topical == ids
        assert row["family_topical_only_count"] == len(ids)
        assert row["family_context_filtered_count"] == len(ids & ctx)
        assert set((run2 / cid / "topical_and_context_ids.txt").read_text().split()) == ids & ctx
        assert (row["measure_topical_only_count"], row["measure_context_filtered_count"]) == measure == (
            m["topical_only_count"], m["context_filtered_count"])
        assert row["run1_row_sha256"] == sha256_file(run1 / cid / "row.json")
        assert row["label"] == "diagnostic — family coverage is not attributable to the measure"
        assert row["candidate_family_status"] == "candidate_family" and row["status"] == "ok"
        assert row["normalization_table_sha256"] == NORM_TABLE_SHA256
        assert row["driver_sha256"] == sha256_file(DRIVER)
        assert row["prompt_template_sha256"] == hashlib.sha256(_driver().PROMPT_F.encode()).hexdigest()
    assert _row(run2, "DC-902")["per_term_doc_counts"]["days with heat index above 95 degrees f"] == 1


def test_an_unparseable_reply_gives_an_error_row_with_the_measure_kept(runs):
    row, fam = _row(runs["run2"], "DC-911"), _family(runs["run2"], "DC-911")
    assert fam["candidate_family"] is None and fam["parse_error"] == "no JSON object with candidate_family found"
    assert fam["model_raw_response_excerpt"] == "I cannot answer that."
    assert row["status"] == "error" and row["family_topical_only_count"] is None
    assert row["family_context_filtered_count"] is None and row["topical_query_sha256"] is None
    assert row["measure_topical_only_count"] is None and row["measure_status"] == "error"  # run 1: all dropped


def test_family_table_is_side_by_side_sorted_by_concept(runs):
    with (runs["run2"] / "survey_table.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert list(rows[0]) == ["concept_id", "dictionary_name", "measure_topical_only_count",
                             "measure_context_filtered_count", "candidate_family", "family_topical_only_count",
                             "family_context_filtered_count", "notes"]
    assert [r["concept_id"] for r in rows] == ["DC-901", "DC-902", "DC-911"]
    assert [(r["measure_topical_only_count"], r["family_topical_only_count"]) for r in rows] == [
        ("2", "2"), ("2", "4"), ("", "")]
    assert rows[1]["candidate_family"] == "heat_index"


def test_family_restart_skips_completed_concepts(runs, env):
    assert (runs["run2"] / "DC-901" / "row.json").read_bytes() == runs["row1"]
    family_prompts = [p for p in env.mock.prompts if '"candidate_family"' in p]
    assert sum("Dictionary name: Fire Weather Index" in p for p in family_prompts) == 1


def test_family_run_writes_nothing_into_the_repository():
    cm = REPO_ROOT / "data" / "metadata" / "concept_map.yaml"
    assert "candidate_family" not in cm.read_text(encoding="utf-8")


# --- measure mode with --normalize --------------------------------------------------

def test_measure_mode_normalize_records_and_searches_normalized_terms(env, tmp_path):
    out = tmp_path / "mn"
    r = env.run(out, "--normalize", "--only", "DC-902")
    assert r.returncode == 0, r.stderr
    cand, row = json.loads((out / "DC-902" / "candidates.json").read_text()), _row(out, "DC-902")
    assert [k["term"] for k in cand["candidates"]] == ["heat index", "95 degrees f"]
    rec = next(x for x in cand["surface_forms"] if x["original"] == "95°f")
    assert rec["rules_applied"] == ["N-3"] and rec["searched"] and rec["source"] == "model"
    assert cand["status"] == "candidate_surface_form"
    assert row["normalization_table_sha256"] == NORM_TABLE_SHA256
    assert row["sanitizer_word_limits"] == {"unnormalized": 6, "normalized": 10}
    assert row["topical_only_count"] == 2  # 3003, 3004


# --- fail closed --------------------------------------------------------------------

def test_family_mode_requires_run1(env, tmp_path):
    r = env.run(tmp_path / "x", "--mode", "family")
    assert r.returncode != 0 and "requires --run1" in r.stderr


def test_run1_rows_must_match_this_run(env, runs, tmp_path):
    bad = tmp_path / "run1_bad"
    shutil.copytree(runs["run1"], bad)
    row = _row(bad, "DC-902"); row["inventory_sha256"] = "0" * 64
    (bad / "DC-902" / "row.json").write_text(json.dumps(row), encoding="utf-8")
    r = env.run(tmp_path / "x", "--mode", "family", "--run1", str(bad))
    assert r.returncode != 0 and "DC-902: run-1 inventory_sha256" in r.stderr
    assert not (tmp_path / "x" / "DC-901").exists()  # checked before any model call
    (bad / "DC-911" / "row.json").unlink()
    r = env.run(tmp_path / "y", "--mode", "family", "--run1", str(bad), "--only", "DC-911")
    assert r.returncode != 0 and "DC-911: no run-1 row.json" in r.stderr


def test_a_tampered_normalization_table_stops_the_run(env, runs, tmp_path):
    t = tmp_path / "table.yaml"
    t.write_bytes(NORM_TABLE.read_bytes() + b"\n")
    for extra in (["--mode", "family", "--run1", str(runs["run1"])], ["--normalize"]):
        r = env.run(tmp_path / "x", *extra, "--norm-table", str(t))
        assert r.returncode != 0 and "refusing to run" in r.stderr


@pytest.mark.parametrize("field,value,message", [
    ("query_sha256", "0" * 64, "context clause SHA-256"),
    ("index", {"content_identity_sha256": "f" * 64}, "index identity"),
    ("admitted_count", 999, "ids.txt holds"),
])
@pytest.mark.parametrize("mode", ["measure", "family"])
def test_the_context_cache_is_reused_only_if_it_matches(env, runs, tmp_path, field, value, message, mode):
    out = tmp_path / "c"
    shutil.copytree(runs["run2"] / "_context", out / "_context")
    extra = ["--mode", "family", "--run1", str(runs["run1"])] if mode == "family" else []
    summ = json.loads((out / "_context" / "summary.json").read_text())
    summ[field] = value
    (out / "_context" / "summary.json").write_text(json.dumps(summ), encoding="utf-8")
    r = env.run(out, *extra, "--only", "DC-901")
    assert r.returncode != 0 and "refusing to reuse" in r.stderr and message in r.stderr
    assert not (out / "DC-901").exists()


def test_a_matching_context_cache_is_reused(env, runs, tmp_path):
    out = tmp_path / "ok"
    shutil.copytree(runs["run2"] / "_context", out / "_context")
    r = env.run(out, "--mode", "family", "--run1", str(runs["run1"]), "--only", "DC-901")
    assert r.returncode == 0, r.stderr
    assert "cached id set reused" in (out / "survey.log").read_text(encoding="utf-8")
    assert _row(out, "DC-901")["family_context_filtered_count"] == 1


# --- the parser and the screen, directly ----------------------------------------------

@pytest.mark.parametrize("content,expected", [
    ('{"candidate_family": "x_y", "family_surface_forms": ["a", "b"]}', ("x_y", ["a", "b"], None)),
    ('{"candidate_family": "x"}', ("x", [], None)),
    ('["a", "b"]', (None, [], "no JSON object with candidate_family found")),
    ('{"candidate_family": ""}', (None, [], "candidate_family is not a non-empty string")),
    ('{"candidate_family": "x", "family_surface_forms": "a"}', ("x", [], "family_surface_forms is not a list")),
    ('{"candidate_family": "x", "family_surface_forms": [1, "b"]}', ("x", ["1", "b"], None)),
])
def test_extract_family(content, expected):
    assert _driver().extract_family(content) == expected


def test_screen_forms_never_normalizes_a_dictionary_name():
    d = _driver()
    recs = d.screen_forms(["heat index > 95"], ["heat index > 95"], d.load_norm_table())
    assert recs[0]["source"] == "dictionary_name" and recs[0]["rules_applied"] == [] and not recs[0]["searched"]
    assert recs[1]["source"] == "model" and recs[1]["search_term"] == "heat index above 95"


def test_run1_ingest_checks_the_v3_tools_as_committed_not_the_working_tree():
    from climrr import coveragesurvey as cs

    assert cs.TOOL_SHA256["survey_driver.py"] == V3_SHA256 != sha256_file(DRIVER)
    assert {n: cs._v3_tracked_sha256(n) for n in cs.TOOL_SHA256} == cs.TOOL_SHA256
    assert sha256_file(TOOLS / "run_query.py") == cs.TOOL_SHA256["run_query.py"]  # run_query.py v3 unchanged
