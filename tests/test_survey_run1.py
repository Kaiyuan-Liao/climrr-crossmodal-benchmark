"""Track B survey run 1, ingested as a diagnostic artifact (D-025, D-026).

The copy under `artifacts/literature/survey/run1/` equals its `manifest.csv`,
which is pinned in `data/manifest.json` under `diagnostics` (never
`external_corpora`); every row's counts re-derive from its id files; the
generated doc regenerates byte for byte; nothing reaches the concept map.
"""

from __future__ import annotations

import csv
import json

from climrr import coveragesurvey as cs
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

MANIFEST = json.loads((REPO_ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))
ENTRY = next(d for d in MANIFEST["diagnostics"] if d["diagnostic_id"] == cs.DIAGNOSTIC_ID)

EXPECTED = {  # (topical_only_count, context_filtered_count, status), from survey_table.csv
    "DC-001": (124420, 88245, "ok"), "DC-002": (123948, 88021, "ok"), "DC-003": (84926, 61190, "ok"),
    "DC-004": (27498, 17394, "ok"), "DC-005": (6981, 4946, "ok"), "DC-006": (3076, 2638, "ok"),
    "DC-007": (548, 395, "ok"), "DC-008": (551, 396, "ok"), "DC-009": (0, 0, "ok"),
    "DC-010": (1, 1, "ok"), "DC-011": (None, None, "error"), "DC-012": (0, 0, "ok"),
    "DC-013": (None, None, "error"), "DC-014": (2, 2, "ok"),
}


def test_the_run_manifest_is_pinned_under_diagnostics_not_external_corpora():
    assert sha256_file(cs.RUN_MANIFEST) == ENTRY["manifest_sha256"]
    assert sha256_file(cs.LOG_PATH) == ENTRY["log_sha256"]
    assert all(cs.DIAGNOSTIC_ID not in json.dumps(c) for c in MANIFEST["external_corpora"])


def test_the_copy_equals_its_manifest():
    with cs.RUN_MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    on_disk = sorted(p.relative_to(cs.RUN_DIR).as_posix() for p in cs.RUN_DIR.rglob("*")
                     if p.is_file() and p.name != "manifest.csv")
    assert [r["rel_path"] for r in rows] == on_disk
    assert (len(rows), sum(int(r["bytes"]) for r in rows)) == (ENTRY["n_files"], ENTRY["total_bytes"])
    for r in rows:
        p = cs.RUN_DIR / r["rel_path"]
        assert (p.stat().st_size, sha256_file(p)) == (int(r["bytes"]), r["sha256"]), r["rel_path"]
    assert cs.manifest_text() == cs.RUN_MANIFEST.read_text(encoding="utf-8")


def test_no_duckdb_tmp_and_no_topical_hits_files_were_copied():
    assert not [p for p in cs.RUN_DIR.rglob("_duckdb_tmp")]
    assert not list(cs.RUN_DIR.glob("DC-*/topical/hits.csv"))
    assert len(ENTRY["not_copied"]["header_only_hits_csv"]) == 12  # the 12 `ok` concepts


def test_rows_reverify_and_match_the_survey_table():
    rows = {r["row"]["concept_id"]: r["row"] for r in cs.verify_run(cs.RUN_DIR)}
    got = {cid: (r["topical_only_count"], r["context_filtered_count"], r["status"]) for cid, r in rows.items()}
    assert got == EXPECTED
    with (cs.RUN_DIR / "survey_table.csv").open(encoding="utf-8", newline="") as f:
        table = {r["concept_id"]: r for r in csv.DictReader(f)}
    for cid, (t, c, _) in EXPECTED.items():
        assert (table[cid]["topical_only_count"], table[cid]["context_filtered_count"]) == (
            "" if t is None else str(t), "" if c is None else str(c))


def test_the_run_used_the_pinned_inventory_clause_index_and_v3_tools():
    run = ENTRY["run"]
    assert run["inventory_sha256"] == sha256_file(REPO_ROOT / "data" / "metadata" / "dictionary_concepts.yaml")
    assert run["context_clause_sha256"] == sha256_file(cs.CONTEXT)
    assert run["context_clause_documents"] == 120050
    assert run["index_content_identity_sha256"].startswith("fbb4affb")
    for path, sha in run["tools_sha256"].items():  # the v3 files as committed (the working-tree driver is v4)
        assert cs._v3_tracked_sha256(path.rsplit("/", 1)[1]) == sha
    assert "untracked copies" in run["execution"] and "aborted first attempt" in run["prior_attempt"]


def test_dc007_topical_set_equals_the_litcorpus02_fire_diagnostic():
    f = cs.facts(cs.verify_run(cs.RUN_DIR))
    assert f["dc7_equals_l2"] and f["dc7_topical"] == f["l2_fire_topical"] == 548


def test_the_heat_index_family_vs_measure_figures():
    f = cs.facts(cs.verify_run(cs.RUN_DIR))
    assert (f["heat_family_group"], f["heat_index_alone"], f["measure_max"]) == (1082, 1080, 2)


def test_error_rows_are_sanitizer_drops_not_model_failures():
    rows = {r["row"]["concept_id"]: r for r in cs.verify_run(cs.RUN_DIR)}
    for cid in ("DC-011", "DC-013"):
        c = rows[cid]["candidates"]
        assert c["model_parse_error"] is None and c["model_raw_terms"] and c["candidates"] == []
        assert all("°" in d["term"] or ">" in d["term"] for d in c["dropped"] if d["source"] == "model")


def test_the_doc_regenerates_byte_for_byte():
    # since run 2 is ingested the doc covers both runs; the run-1 part is rendered by the same code
    from climrr import coveragesurvey_run2 as cs2
    assert cs2.render_full_doc() == cs.DOC_PATH.read_text(encoding="utf-8")
    rows = cs.verify_run(cs.RUN_DIR)
    run1_only = cs.render_doc(rows, ENTRY["manifest_sha256"])
    assert cs.RUN2_PENDING in run1_only and cs.RUN2_PENDING not in cs.DOC_PATH.read_text(encoding="utf-8")


def test_candidates_never_reach_the_concept_map():
    cm = (REPO_ROOT / "data" / "metadata" / "concept_map.yaml").read_text(encoding="utf-8")
    assert "candidate_surface_form" not in cm and "summer max heat index" not in cm
