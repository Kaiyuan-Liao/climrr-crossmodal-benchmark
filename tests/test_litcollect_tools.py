"""The external collection tools under `scripts/litcollect/`, on a 5-document synthetic index.

Checks the behaviour LITCORPUS-02 rests on: the parser refuses `NOT`;
whole-word matching ("FWIs" is not "FWI"); R-FWI-1 exclusion of a bare-`FWI`
document; and hit offsets that re-slice the matched text from the
**unnormalized** decoded string (an accented prefix makes code points and
bytes differ). Also pins the tracked tools' SHA-256.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys

import pytest

from climrr import retrieval
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"

#: build_index.py and run_query.py are byte-identical to the files that ran on Polaris.
#: run_v1_on_705k.sh differs from the executed file (SHA-256 0c9516b7...) in one line only:
#: BASE is read from LITCOLLECT_ROOT_POLARIS instead of an absolute Eagle path.
TOOL_SHA256 = {
    "build_index.py": "5e063a44f30bee0da81205b6b119d647d87fd08ddf38998eb1d8fa0c235b99a9",
    "run_query.py": "a93eeba766f2eb4d487a8a157d2a2d207b41af0482fefdb774886a66c2d57708",
    "run_v1_on_705k.sh": "47fe1e17f3dc27fa8267ec21a173bbb3c773d4bc5f2e2045a7d5ccd379ffba59",
}

DOCS = {
    "1001": {"title": "Fire Weather Index (FWI) under climate change", "body": "warming trend"},
    "1002": {"title": "FWI increased under warming", "pages": 12},           # bare FWI + a non-string value
    "1003": None,                                                            # parse failure
    "1004": {"a": "the fire-weather index and FWIs in a climate change study"},  # hyphenated variant; FWIs
    "1005": {"t": "Résumé — Québec: Canadian FWI rises with warming"},       # accented; longer term
}
QUERY = '( "fire weather index" OR "fire-weather index" OR fwi OR "canadian fwi" ) AND ( "climate change" OR warming )\n'


def test_the_tracked_tools_are_pinned():
    assert {p: sha256_file(TOOLS / p) for p in TOOL_SHA256} == TOOL_SHA256


def test_no_tool_carries_an_absolute_path():
    for p in TOOL_SHA256:
        text = (TOOLS / p).read_text(encoding="utf-8")
        assert "/eagl" + "e/" not in text and "/User" + "s/" not in text


def _run_query_module():
    spec = importlib.util.spec_from_file_location("rq", TOOLS / "run_query.py")
    rq = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rq)
    return rq


def test_parser_refuses_not_and_nesting():
    pytest.importorskip("duckdb")
    rq = _run_query_module()
    assert rq.parse(QUERY)[0] == ["fire weather index", "fire-weather index", "fwi", "canadian fwi"]
    for bad in ('( fwi ) AND NOT ( "full waveform" )', "( ( fwi ) )", "fwi OR"):
        with pytest.raises((ValueError, IndexError)):
            rq.parse(bad)


@pytest.fixture(scope="module")
def synthetic(tmp_path_factory):
    pytest.importorskip("duckdb")
    base = tmp_path_factory.mktemp("lit")
    src, idx, runs = base / "src", base / "idx", base / "runs"
    (src / "00").mkdir(parents=True)
    for d, obj in DOCS.items():
        raw = b'{"title": "broken' if obj is None else json.dumps(obj, ensure_ascii=False).encode("utf-8")
        (src / "00" / f"{d}.json").write_bytes(raw)
    (base / "q.txt").write_text(QUERY, encoding="utf-8")
    subprocess.run([sys.executable, str(TOOLS / "build_index.py"), "--root", str(src), "--out", str(idx)],
                   check=True, capture_output=True)
    subprocess.run([sys.executable, str(TOOLS / "run_query.py"), "--index", str(idx), "--query-file",
                    str(base / "q.txt"), "--out", str(runs), "--threads", "1",
                    "--disambiguate", "fwi=fire weather|fire-weather"], check=True, capture_output=True)
    return src, idx, runs


def test_index_records_parse_failures_and_non_strings_without_repair(synthetic):
    _, idx, _ = synthetic
    s = json.loads((idx / "index_summary.json").read_text(encoding="utf-8"))
    assert (s["files"], s["parse_failures"], s["section_rows"]) == (5, 1, 5)
    with (idx / "manifest.csv").open(encoding="utf-8") as f:
        rows = {r["doc_id"]: r for r in csv.DictReader(f)}
    assert rows["1003"]["parse_ok"] == "0" and rows["1002"]["n_nonstring"] == "1"


def test_whole_word_and_rfwi1_exclusion(synthetic):
    _, _, runs = synthetic
    s = json.loads((runs / "summary.json").read_text(encoding="utf-8"))
    raw = (runs / "ids_raw.txt").read_text().split()
    admitted = (runs / "ids.txt").read_text().split()
    assert raw == ["1001", "1002", "1004", "1005"]
    assert admitted == ["1001", "1004", "1005"]            # 1002: bare FWI, no disambiguator
    assert s["excluded_by_disambiguation"] == 1
    assert s["per_term_doc_counts"]["g0:fwi"] == 3            # 1001, 1002, 1005 --- not 1004's "FWIs"


def test_the_repo_rule_agrees_with_the_tool_on_the_synthetic_documents(synthetic):
    _, _, runs = synthetic
    admitted = set((runs / "ids.txt").read_text().split())
    for d, obj in DOCS.items():
        if obj is None:
            continue
        assert retrieval.evaluate(retrieval.flat_sections(obj))["eligible"] is (d in admitted), d


def test_offsets_reslice_the_unnormalized_text(synthetic):
    src, _, runs = synthetic
    with (runs / "hits.csv").open(encoding="utf-8") as f:
        hits = list(csv.DictReader(f))
    assert hits
    for h in hits:
        obj = json.loads((src / h["rel_path"]).read_bytes().decode("utf-8"))
        text = obj[h["section_key"]]
        assert text[int(h["char_start"]):int(h["char_end"])].lower() == h["term"]
    accented = [h for h in hits if h["doc_id"] == "1005" and h["term"] == "canadian fwi"]
    assert accented and int(accented[0]["char_start"]) == DOCS["1005"]["t"].index("Canadian")
