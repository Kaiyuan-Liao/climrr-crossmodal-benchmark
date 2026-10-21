"""Track B survey run 2 (family level), ingested as a diagnostic artifact (D-025, D-026, D-027, D-028).

The copy under `artifacts/literature/survey/run2/` equals its `manifest.csv`,
pinned in `data/manifest.json` under `diagnostics`; run 1 is untouched (its
manifest hash is unchanged); every row re-verifies against its pins, its id
files and the ingested run-1 row; the computed statements in the doc hold; the
doc regenerates byte for byte; no candidate family reaches the concept map.
"""

from __future__ import annotations

import csv
import json

import yaml

from climrr import coveragesurvey as cs
from climrr import coveragesurvey_run2 as cs2
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

MANIFEST = json.loads((REPO_ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))
ENTRY = next(d for d in MANIFEST["diagnostics"] if d["diagnostic_id"] == cs2.DIAGNOSTIC_ID)
RUN1_MANIFEST_SHA256 = "74ba7d7c72e7920ac16e1cc7c49ab2543add316df37baf60ff3b52c10c2d125d"

EXPECTED = {  # measure topical/context (run 1) | candidate_family | family topical/context, from survey_table.csv
    "DC-001": ((124420, 88245), "temperature", (123948, 88021)),
    "DC-002": ((123948, 88021), "temperature", (123948, 88021)),
    "DC-003": ((84926, 61190), "hydrology", (124314, 84437)),
    "DC-004": ((27498, 17394), "wind", (58320, 38833)),
    "DC-005": ((6981, 4946), "dry_spell", (7351, 5267)),
    "DC-006": ((3076, 2638), "temperature", (143266, 101847)),
    "DC-007": ((548, 395), "fire_risk", (4465, 3044)),
    "DC-008": ((551, 396), "fire_danger", (4323, 2942)),
    "DC-009": ((0, 0), "heat_index", (15749, 11719)),
    "DC-010": ((1, 1), "heat_index", (15731, 11704)),
    "DC-011": ((None, None), "extreme_heat_days", (3335, 2985)),
    "DC-012": ((0, 0), "extreme_heat_days", (2681, 2397)),
    "DC-013": ((None, None), "heat_wave_days", (3347, 2996)),
    "DC-014": ((2, 2), "extreme_heat_days", (2686, 2402)),
}


def _rows():
    return cs2.verify_run(cs2.RUN_DIR)


def test_run1_is_untouched():
    run1 = next(d for d in MANIFEST["diagnostics"] if d["diagnostic_id"] == cs.DIAGNOSTIC_ID)
    assert sha256_file(cs.RUN_MANIFEST) == run1["manifest_sha256"] == RUN1_MANIFEST_SHA256
    assert cs.manifest_text() == cs.RUN_MANIFEST.read_text(encoding="utf-8")
    assert ENTRY["run"]["run1_manifest_sha256"] == RUN1_MANIFEST_SHA256


def test_run2_manifest_is_pinned_under_diagnostics_not_external_corpora():
    assert sha256_file(cs2.RUN_MANIFEST) == ENTRY["manifest_sha256"]
    assert sha256_file(cs2.LOG_PATH) == ENTRY["log_sha256"] == sha256_file(cs2.RUN_DIR / "survey.log")
    assert ENTRY["source_tarball_sha256"] == cs2.TARBALL_SHA256
    assert all(cs2.DIAGNOSTIC_ID not in json.dumps(c) for c in MANIFEST["external_corpora"])


def test_the_copy_equals_its_manifest():
    with cs2.RUN_MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    on_disk = sorted(p.relative_to(cs2.RUN_DIR).as_posix() for p in cs2.RUN_DIR.rglob("*")
                     if p.is_file() and p.name != "manifest.csv")
    assert [r["rel_path"] for r in rows] == on_disk
    assert (len(rows), sum(int(r["bytes"]) for r in rows)) == (ENTRY["n_files"], ENTRY["total_bytes"])
    for r in rows:
        p = cs2.RUN_DIR / r["rel_path"]
        assert (p.stat().st_size, sha256_file(p)) == (int(r["bytes"]), r["sha256"]), r["rel_path"]
    assert cs.manifest_text(cs2.RUN_DIR) == cs2.RUN_MANIFEST.read_text(encoding="utf-8")


def test_no_topical_hits_files_were_copied():
    assert not list(cs2.RUN_DIR.glob("DC-*/topical/hits.csv"))
    assert len(ENTRY["not_copied"]["header_only_hits_csv"]) == 14
    assert not list(cs2.RUN_DIR.rglob("_duckdb_tmp"))


def test_the_log_carries_the_pinned_run_identity():
    log = cs2.verify_log(cs2.LOG_PATH.read_text(encoding="utf-8"))
    f = log["fields"]
    assert (f["driver_sha"], f["prompt_f_sha"], f["norm_table_sha"]) == ("f929ab6a3669", "7097c86ccbb6", "80a5e0e386df")
    assert (f["inventory_sha"], f["context_sha"], f["index_identity"]) == ("288d08c5b92a", "fec9b5ca97f1", "fbb4affb7162")
    assert (f["model"], f["mode"], log["context_documents"]) == ("gpt-oss-120b", "family", 120050)
    assert sha256_file(cs2.DRIVER) == cs2.DRIVER_SHA256


def test_rows_reverify_and_match_the_side_by_side_table():
    got = {r["row"]["concept_id"]: (
        (r["row"]["measure_topical_only_count"], r["row"]["measure_context_filtered_count"]),
        r["row"]["candidate_family"],
        (r["row"]["family_topical_only_count"], r["row"]["family_context_filtered_count"])) for r in _rows()}
    assert got == EXPECTED


def test_every_family_is_a_candidate_family_hypothesis():
    rows = _rows()
    assert all(r["family"]["status"] == "candidate_family" for r in rows)
    assert all(r["row"]["candidate_family_status"] == "candidate_family" for r in rows)
    assert all(r["row"]["label"] == cs2.FAMILY_LABEL for r in rows)


def test_normalization_and_form_counts():
    st = cs2.form_stats(_rows())
    assert st["rules_fired"] == {} and st["forms_changed_by_normalization"] == 0
    assert (st["forms_total"], st["forms_searched"], st["forms_over_cap"], st["forms_dropped_other"]) == (112, 112, 0, 0)
    assert st["forms_per_concept"] == [8] and st["prompt_k"] == [8]


def test_the_computed_statements():
    f = cs2.facts(_rows())
    assert f["all_candidate_family"]
    assert f["dc3"] == (124314, True) and f["dc6"] == (143266, True) and f["dc9"] == (15749, True)
    assert f["dc10"] == (15731, True, False)  # DC-010's forms do not include "humid heat"
    assert f["heat_index_l2"] == 1080 and f["heat_index_run2"] == {"DC-009": 1080, "DC-010": 1080}
    assert f["fire"] == {"DC-007": ("fire_risk", 4465, True), "DC-008": ("fire_danger", 4323, True)}
    assert f["fire_terms_in_concept_map"] == []
    assert (f["fire_weather_run2"], f["fire_weather_l2"], f["fire_danger_run2"]) == (1298, 1298, 1041)
    assert f["threshold_range"] == (2681, 3347) and f["heat_measure_range"] == (0, 2)
    assert all(v[2] for v in f["thresholds"].values())  # "hot days" in all four
    assert [c for c, v in f["thresholds"].items() if v[3]] == ["DC-011", "DC-013"]  # "warm days"
    assert (f["fwi_group_l2"], f["fwi_rfwi1"], f["family_range"]) == (548, 473, (2681, 143266))


def test_the_doc_regenerates_byte_for_byte():
    assert cs2.render_full_doc() == cs.DOC_PATH.read_text(encoding="utf-8")


def test_candidate_families_never_reach_the_concept_map():
    text = (REPO_ROOT / "data" / "metadata" / "concept_map.yaml").read_text(encoding="utf-8")
    ids = {e["canonical_id"] for e in yaml.safe_load(text)["entries"]}
    assert "candidate_family" not in text
    assert not ids & {r["row"]["candidate_family"] for r in _rows()} - {"heat_index"}
    assert ids >= {"heat_index"}  # pre-existing D-018 entry; run 2 proposed the same name, nothing added


def test_the_doc_names_the_three_levels_and_the_standing_rule_as_ruled():
    """D-028 R2: level names exactly as the ruling; never ranked or combined; the Level-1-zero sentence."""
    text = cs.DOC_PATH.read_text(encoding="utf-8")
    ruling = (REPO_ROOT / "docs" / "TRACKB_STAGE2_RUN2_GUIDANCE_RULING.md").read_text(encoding="utf-8")
    for n, name in ((1, "Dictionary-measure diagnostic coverage"), (2, "Governed concept-map family coverage"),
                    (3, "Model-proposed candidate-family diagnostic coverage")):
        assert f"| Level {n} | **{name}** |" in ruling
        assert f"**Level {n} --- {name}**" in text
    flat = " ".join(text.split())
    assert "the three levels are never ranked or combined" in flat
    assert "Level-2 or Level-3 coverage is never attributed to a Level-1 threshold measure" in flat
    assert ("A Level-1 zero means no direct lexical match under the current measure representation and "
            "search rules, not that no relevant literature exists.") in flat
    assert "TRACKB-SURVEY-RUN2 --- family-level diagnostic coverage survey" in flat


def test_run2_host_and_environment_are_owner_confirmed_and_python_is_unknown():
    """D-028 actions 13--14: owner_confirmed, not run-derived; run 1's Python version not copied."""
    run = ENTRY["run"]
    assert run["host"].startswith("polaris-login-01") and "`owner_confirmed`" in run["host"]
    assert "globus_env" in run["environment"] and "`owner_confirmed`" in run["environment"]
    assert "`unknown`" in run["python"] and "3.11" not in run["python"]
    assert {k: run[k] for k in ("host", "environment", "python")} == {
        k: cs2.RUN_FACTS[k] for k in ("host", "environment", "python")}
