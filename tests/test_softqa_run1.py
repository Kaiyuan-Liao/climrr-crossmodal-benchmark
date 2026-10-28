"""Track C run 1 ingest, counts, v2-locator replay and review batch 01 (D-029, D-030, D-033).

The ingested copy matches its pinned manifest and re-derives the run's totals;
`prompt_user.txt` and `response.json` were not copied (their hashes are); every
record maps onto `candidate_schema_v1.json`; the generated doc is current; the
replay output gives 117 exact / 8 normalized / 34 prefix_anchor / 34 not found;
the triage gives 11 candidates; batch 01 is frozen, pinned, renders evidence
first with the rationale withheld, and its reviewer forms are unfilled.
"""

from __future__ import annotations

import importlib.util
import json

import pytest
import yaml

from climrr import softqa
from climrr import softqa_run1 as r1
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TRIAGE_11 = ["C-199098498-01", "C-226260658-01", "C-236782701-01", "C-245473445-01", "C-247623438-01",
             "C-247866001-01", "C-247866001-02", "C-253196482-01", "C-254679818-01", "C-4238342-01",
             "C-5882914-01"]


def _entry() -> dict:
    data = json.loads(r1.MANIFEST.read_text(encoding="utf-8"))
    return next(d for d in data["diagnostics"] if d["diagnostic_id"] == r1.DIAGNOSTIC_ID)


# --- ingest -----------------------------------------------------------------------

def test_the_ingested_copy_matches_its_pinned_manifest():
    e = _entry()
    assert sha256_file(r1.RUN_MANIFEST) == e["manifest_sha256"]
    assert r1.manifest_text() == r1.RUN_MANIFEST.read_text(encoding="utf-8")
    assert sha256_file(r1.LOG_PATH) == e["log_sha256"]
    assert sha256_file(r1.EXCLUDED_CSV) == e["not_copied"]["excluded_files_csv_sha256"]
    assert e["source_tarball_sha256"] == r1.TARBALL_SHA256


def test_the_ingested_copy_re_derives_the_run_and_its_pins():
    facts = r1.verify_run(r1.RUN_DIR, with_excluded=False)
    assert facts["papers"] == 243 and facts["candidates"] == 193


def test_the_log_start_line_carries_the_run_pins():
    log = r1.verify_log(r1.LOG_PATH.read_text(encoding="utf-8"))
    assert log["start"]["units_sha"] == "5bb486ef6428" and log["start"]["qa_sha"] == "f0d0f07bf0fd"
    assert log["start"]["system_sha"] == "f2e493e179aa" and log["start"]["index"] == "fbb4affb7162"
    assert (r1.RUN_DIR / "agent.log").read_bytes() == r1.LOG_PATH.read_bytes()


def test_as_loaded_input_hashes_differ_from_file_hashes_by_construction():
    run = _entry()["run"]
    assert run["units_sha256_as_loaded"] == r1.canonical_sha256(r1.UNITS)
    assert run["units_sha256_as_loaded"].startswith("5bb486ef")
    assert run["units_file_sha256"] == sha256_file(r1.UNITS) != run["units_sha256_as_loaded"]
    assert run["qa_types_sha256_as_loaded"].startswith("f0d0f07b")
    assert run["qa_types_file_sha256"] == sha256_file(r1.QA_TYPES) != run["qa_types_sha256_as_loaded"]


def test_no_paper_text_or_model_response_was_copied():
    assert not list(r1.SOFTQA_ART.rglob("prompt_user.txt")) and not list(r1.SOFTQA_ART.rglob("response.json"))
    rows = r1.EXCLUDED_CSV.read_text(encoding="utf-8").splitlines()[1:]
    assert len(rows) == 2 * 243
    assert {r.split(",")[0].split("/")[1] for r in rows} == {"prompt_user.txt", "response.json"}


def test_every_record_maps_onto_the_schema_and_validates():
    recs = [json.loads(ln) for ln in r1.SCHEMA_JSONL.read_text(encoding="utf-8").splitlines()]
    assert len(recs) == 193
    schema = softqa.load_schema()
    fresh = softqa.map_and_validate_jsonl(r1.RUN_DIR / "candidates.jsonl")
    assert recs == json.loads(json.dumps(fresh, ensure_ascii=False))
    for r in recs:
        softqa.validate(r, schema)
        assert all(v is None for v in r["human_review"].values())
        assert all(v is None for k, v in r["table_provenance"].items() if k != "unit_id_or_template_id")
        assert r["mapping"]["pending_stages"]["human_review.final_status"] == softqa.STAGE_HUMAN
        assert r["mapping"]["pending_stages"]["table_provenance.raw_cell_values"] == softqa.STAGE_TABLE


# --- counts -------------------------------------------------------------------------

def test_run_totals_and_rejection_reasons():
    k = r1.counts()
    assert (k["papers"], k["groups"], k["deterministic_pass"], k["rejected_pre_review"]) == (243, 193, 103, 90)
    assert k["papers_with_zero_groups"] == 68 and k["groups_per_paper"] == {0: 68, 1: 158, 2: 16, 3: 1}
    assert k["rejection_reason_counts_incl_combos"] == {"span_reslice_pass": 76, "concept_location_pass": 9,
                                                        "place_location_pass": 10}
    assert sum(k["rejection_combinations"].values()) == 90
    assert k["question_has_no_table_number_false"] == {"deterministic_pass": 16, "rejected_pre_review": 25}
    assert (k["truncated_papers"], k["model_parse_errors"]) == (21, 0)
    assert len(k["passages_over_700_chars"]) == 5


def test_summary_distributions():
    k = r1.counts()
    assert k["by_unit"] == {"F-HEAT": 62, "P-STATE-1": 33, "F-FWI": 72, "P-CELL-1": 15, "P-COUNTY-1": 11}
    assert k["by_concept_relation"] == {"direct": 145, "related": 48}
    assert sum(k["by_qa_type"].values()) == sum(k["by_place_role"].values()) == 193


def test_triage_gives_the_eleven_candidates():
    tri = r1.triage(r1.load_candidates())
    assert [c["candidate_id"] for c in tri] == TRIAGE_11


# --- replay ---------------------------------------------------------------------------

def test_the_replay_output_is_pinned_and_gives_the_recovery_counts():
    e = _entry()["locator_replay_v2"]
    assert sha256_file(r1.REPLAY_PATH) == e["sha256"] and e["agent_sha256"] == r1.V2_AGENT_SHA256
    rp = json.loads(r1.REPLAY_PATH.read_text(encoding="utf-8"))
    assert rp["recovery"] == {"exact": 117, "normalized": 8, "prefix_anchor": 34, "not_found": 34} == e["recovery"]
    assert rp["v1_to_v2"] == {"v1_fail->normalized": 8, "v1_fail->not_found": 34,
                              "v1_fail->prefix_anchor": 34, "v1_pass->exact": 117}
    assert rp["recovered_reslice_ok"] == 159 and rp["v1_failures_in_truncated_papers"] == 11
    assert rp["input_checks"] == {"prompt_sha256_match": 243,
                                  "untruncated_reproduce_paper_chars_and_n_sections": 222, "truncated": 21}
    assert rp["run1_candidates_sha256"] == sha256_file(r1.RUN_DIR / "candidates.jsonl")


def test_the_replay_rows_are_the_run_one_proposals_and_carry_no_passage_text():
    rp = json.loads(r1.REPLAY_PATH.read_text(encoding="utf-8"))
    cands = r1.load_candidates()
    assert [r["candidate_id"] for r in rp["rows"]] == [c["candidate_id"] for c in cands]
    for row, c in zip(rp["rows"], cands):
        assert row["v1_span_reslice_pass"] == c["pre_review_checks"]["span_reslice_pass"]
        assert not any(isinstance(v, str) and len(v) > 100 for k, v in row.items() if k != "json_path")
        assert not {"passage", "verbatim_passage", "recovered", "text"} & set(row)
    norm = [r for r in rp["rows"] if r["v2_passage_recovery"] == "normalized"]
    assert all("U+2011" in r["typographic_codepoints"] for r in norm)


def test_the_generated_doc_is_current():
    assert r1.DOC_PATH.read_text(encoding="utf-8") == r1.render_doc()
    text = r1.DOC_PATH.read_text(encoding="utf-8")
    assert "**11 candidates**" in text and "never fire occurrence" in text


# --- review batch 01 --------------------------------------------------------------------

def _freeze():
    spec = importlib.util.spec_from_file_location("fsrb", REPO_ROOT / "scripts" / "freeze_softqa_review_batch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _view():
    spec = importlib.util.spec_from_file_location("srv", REPO_ROOT / "scripts" / "softqa_review_view.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_batch_01_is_frozen_pinned_and_rebuilds_identically():
    data = json.loads(r1.MANIFEST.read_text(encoding="utf-8"))
    entry = next(f for f in data["files"] if f["path"] == "artifacts/softqa/review_batch_01.json")
    assert sha256_file(r1.BATCH_PATH) == entry["sha256"] and entry["candidate_ids"] == TRIAGE_11
    batch = json.loads(r1.BATCH_PATH.read_text(encoding="utf-8"))
    assert batch == json.loads(json.dumps(_freeze().build_batch(), ensure_ascii=False))
    assert [r["candidate_identity"]["candidate_id"] for r in batch["candidates"]] == TRIAGE_11 == sorted(TRIAGE_11)
    assert batch["reviewer_1"] == "Kaiyuan Liao"


def test_batch_01_has_no_table_value_and_no_review_yet():
    batch = json.loads(r1.BATCH_PATH.read_text(encoding="utf-8"))
    for r in batch["candidates"]:
        softqa.validate(r)
        assert r["status"] == "deterministic_pass"
        assert r["table_provenance"]["raw_cell_values"] is None and r["table_provenance"]["derived_value"] is None
        assert all(v is None for v in r["human_review"].values())


def test_batch_01_records_the_fwi_hold():
    gates = json.loads(r1.BATCH_PATH.read_text(encoding="utf-8"))["acceptance_gate"]
    held = sorted(i for i, g in gates.items() if g["status"] == "hold_owner_confirmation")
    assert held == ["C-245473445-01", "C-247866001-01"]                   # P-COUNTY-1, P-CELL-1


@pytest.mark.parametrize("cid", TRIAGE_11)
def test_each_batch_candidate_renders_in_review_order_with_rationale_withheld(cid):
    view = _view()
    recs = [r for r in view.load_records(r1.BATCH_PATH) if r["candidate_identity"]["candidate_id"] == cid]
    assert len(recs) == 1
    rec = recs[0]
    hidden = view.render(rec)
    pos = [hidden.index(t) for t in view.SECTION_TITLES]
    assert pos == sorted(pos)
    assert hidden.index(rec["paper_provenance"]["verbatim_passage"]) < pos[1]
    assert view.WITHHELD in hidden and rec["soft_link"]["link_rationale"] not in hidden
    assert "acceptance gate:" in hidden[pos[1]:pos[2]]
    shown = view.render(rec, show_rationale=True)
    assert shown.index(rec["soft_link"]["link_rationale"]) > shown.index(view.SECTION_TITLES[4])


@pytest.mark.parametrize("cid", TRIAGE_11)
def test_each_batch_candidate_has_an_unfilled_reviewer_form(cid):
    form = yaml.safe_load((r1.FORMS_DIR / f"{cid}.reviewer_1.yaml").read_text(encoding="utf-8"))
    template = yaml.safe_load(r1.FORM.read_text(encoding="utf-8"))
    assert form["identity"]["candidate_id"] == cid and form["identity"]["reviewer_role"] == "reviewer_1"
    assert form["identity"]["reviewer_id"] is None and form["identity"]["review_date"] is None
    assert form["checklist"] == template["checklist"] and all(v is None for v in form["checklist"].values())
    assert form["edit"] == template["edit"] and form["notes"] is None
    assert sorted(p.name for p in r1.FORMS_DIR.iterdir()) == sorted(f"{i}.reviewer_1.yaml" for i in TRIAGE_11)
