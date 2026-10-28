"""Soft-QA schema, review protocol and Track C inputs (D-033), frozen before any generation run.

The schema has the ruling's seven field groups field for field; the built-in
validator agrees with `jsonschema` where it is installed; the Track C mapper
keeps everything the agent did not produce null with its stage named. The unit
definitions carry no number and no direction; the paper list is the frozen
100 + 143 place candidates. The review view withholds the agent's rationale and
confidence until asked.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import re

import pytest
import yaml

from climrr import softqa
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

SOFTQA = REPO_ROOT / "data" / "metadata" / "softqa"
RULING = REPO_ROOT / "docs" / "TRACKC_TRACKD_SOFT_QA_GUARDRAILS_RULING.md"
PROTOCOL = REPO_ROOT / "docs" / "SOFTQA_REVIEW_PROTOCOL.md"
PLACE_DIR = REPO_ROOT / "artifacts" / "literature" / "litcorpus02" / "place_candidates"

#: The ruling's "Candidate-record fields", group by group, in its order.
RULING_GROUPS = {
    "candidate_identity": ["candidate_id", "track", "generator_version", "generator_model", "prompt_hash",
                           "generation_timestamp", "source_commit"],
    "paper_provenance": ["paper_item_id", "paper_sha256", "json_path", "span_start", "span_end", "verbatim_passage",
                         "claim_or_passage_type", "paper_geography", "paper_geography_role", "paper_time",
                         "paper_scenario", "paper_concept"],
    "table_provenance": ["unit_id_or_template_id", "table_data_sha256", "row_ids", "column_ids", "column_statuses",
                         "raw_cell_values", "derived_value", "derivation_rule_id", "concept_family", "metric",
                         "location", "period", "scenario", "season", "statistic"],
    "soft_link": ["qa_type", "link_rationale", "concept_relation", "geography_relation", "time_relation",
                  "scenario_relation", "direction_relation", "c_g_t_s_d_audit", "unmatched_dimensions", "assumptions"],
    "generation_controls": ["table_values_visible_to_generator", "answer_visible_to_generator", "retrieval_terms",
                            "retrieval_source"],
    "deterministic_validation": ["span_reslice_pass", "table_recompute_pass", "concept_location_pass",
                                 "place_location_pass", "place_role_recorded", "slot_validation_pass",
                                 "verified_columns_only", "pre_review_status"],
    "human_review": ["reviewer_1_id", "reviewer_1_date", "paper_fidelity", "table_fidelity", "concept_validity",
                     "geography_validity", "temporal_validity", "scenario_validity", "question_validity",
                     "answer_validity", "overclaim_check", "reviewer_1_disposition", "requires_second_review",
                     "reviewer_2_id", "reviewer_2_disposition", "adjudication_status", "final_status",
                     "final_question", "final_answer", "edit_history"],
}
LIFECYCLE = ["llm_candidate", "deterministic_pass", "human_review", "accepted", "rejected_pre_review",
             "needs_second_review", "needs_adjudication", "rejected_human", "accepted_after_edit"]
CHECKLIST = ["paper_fidelity", "table_fidelity", "concept_validity", "geography_validity", "temporal_validity",
             "scenario_validity", "question_validity", "answer_validity", "overclaim_check", "overall_disposition"]

PASSAGE = "Summer fire weather index values in Oklahoma rose over the study period."


def agent_record(**over) -> dict:
    """A softqa_agent v1 candidate, shaped exactly as the agent writes it."""
    proposal = {
        "passage": PASSAGE, "section_key": "results", "unit_id": "P-COUNTY-1", "qa_type": "cross_source_validation",
        "example_question": "Does the table agree with the paper?", "paper_side_fact": "FWI rose in Oklahoma.",
        "table_side_needed": "the unit's summer FWI comparison", "paper_geography": "Oklahoma",
        "paper_geography_role": "study_area", "paper_time": "unknown", "paper_scenario": "unknown",
        "paper_concept": "fire weather index", "concept_relation": "direct", "geography_relation": "same",
        "link_rationale": "SECRET-RATIONALE same family and place", "unmatched_dimensions": ["time", "scenario"],
        "confidence": "SECRET-CONFIDENCE-high",
    }
    rec = {
        "candidate_id": "C-4001-01", "track": "C", "status": "deterministic_pass",
        "generator_version": "softqa_agent v1", "generator_model": "mock-model", "endpoint": "http://mock",
        "prompt_hash": "a" * 64, "system_prompt_sha256": "b" * 64, "units_sha256": "c" * 64,
        "qa_types_sha256": "d" * 64, "generation_timestamp": "2026-10-27T00:00:00Z", "source_commit": "abc1234",
        "paper_item_id": "4001", "paper_rel_path": "00/4001.json", "paper_sha256": "e" * 64, "arm": "fire_weather_v1",
        "evidence": {"json_path": "$.results", "section_idx": 2, "span_start": 10, "span_end": 10 + len(PASSAGE)},
        "verbatim_passage": PASSAGE,
        "concept_hit": {"term": "fire weather index", "json_path": "$.results", "section_idx": 2, "span": [27, 45]},
        "place_hit": {"term": "oklahoma", "json_path": "$.results", "section_idx": 2, "span": [56, 64]},
        "proposal": proposal,
        "table_values_visible_to_generator": False, "answer_visible_to_generator": False,
        "pre_review_checks": {"span_reslice_pass": True, "concept_location_pass": True, "place_location_pass": True,
                              "place_check_mode": "unit_place_in_paper", "place_role_recorded": True,
                              "proposal_fields_complete": True, "missing_fields": [],
                              "question_has_no_table_number": True, "unit_id_known": True, "qa_type_known": True},
        "pre_review_status": "deterministic_pass",
        "table_side": None, "c_g_t_s_d_audit": None, "human_review": None,
    }
    rec.update(over)
    return rec


@pytest.fixture(scope="module")
def schema():
    return softqa.load_schema()


# --- the frozen schema -------------------------------------------------------

def test_schema_groups_are_the_rulings_field_for_field(schema):
    for group, fields in RULING_GROUPS.items():
        g = schema["properties"][group]
        assert list(g["properties"]) == fields, group
        assert g["required"] == fields and g["additionalProperties"] is False
    assert [k for k in schema["properties"] if k in RULING_GROUPS] == list(RULING_GROUPS)
    assert set(schema["properties"]) - set(RULING_GROUPS) == {"schema_version", "status", "agent_record", "mapping"}


def test_status_enum_is_the_lifecycle_and_generator_blindness_is_constant(schema):
    assert schema["properties"]["status"]["enum"] == LIFECYCLE
    gc = schema["properties"]["generation_controls"]["properties"]
    assert gc["table_values_visible_to_generator"] == {"const": False}
    assert gc["answer_visible_to_generator"] == {"const": False}
    hr = schema["properties"]["human_review"]["properties"]
    for k in ("reviewer_1_disposition", "reviewer_2_disposition"):
        assert hr[k]["enum"] == ["accept", "accept_with_edit", "ambiguous", "reject", None]


def test_table_side_and_human_review_fields_are_nullable(schema):
    for group in ("table_provenance", "human_review"):
        for f, sch in schema["properties"][group]["properties"].items():
            assert softqa._fits(None, sch), f"{group}.{f}"


def test_schema_is_valid_json_schema_2020_12(schema):
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator.check_schema(schema)


def test_schema_hash_is_pinned_in_the_manifest():
    files = {f["path"]: f for f in json.loads((REPO_ROOT / "data" / "manifest.json").read_text())["files"]}
    for name in ("candidate_schema_v1.json", "review_form_v1.yaml", "units_definitions_v1.json",
                 "qa_types_v1.json", "trackc_candidates_v1.json"):
        e = files[f"data/metadata/softqa/{name}"]
        p = SOFTQA / name
        assert e["sha256"] == sha256_file(p) and e["bytes"] == p.stat().st_size, name
        assert e["decision_ref"] == "D-033"
        p.read_bytes().decode("utf-8" if name == "units_definitions_v1.json" else "ascii")  # as the encoding note says
        assert b"\r" not in p.read_bytes()


# --- mapper and validator ------------------------------------------------------

def test_a_passing_agent_record_maps_and_validates(schema):
    rec = softqa.validate(softqa.map_trackc(agent_record(), schema), schema)
    pp, dv = rec["paper_provenance"], rec["deterministic_validation"]
    assert rec["status"] == "deterministic_pass"
    assert (pp["json_path"], pp["span_start"], pp["span_end"]) == ("$.results", 10, 10 + len(PASSAGE))
    assert pp["verbatim_passage"] == PASSAGE and pp["paper_geography_role"] == "study_area"
    assert rec["table_provenance"]["unit_id_or_template_id"] == "P-COUNTY-1"
    assert all(dv[k] is True for k in softqa.TRACKC_MANDATORY_CHECKS)
    assert rec["soft_link"]["unmatched_dimensions"] == ["time", "scenario"]
    assert rec["agent_record"] == agent_record()


def test_everything_the_agent_did_not_produce_is_null_with_its_stage(schema):
    rec = softqa.map_trackc(agent_record(), schema)
    pending = rec["mapping"]["pending_stages"]
    for f in RULING_GROUPS["table_provenance"][1:]:
        assert rec["table_provenance"][f] is None and pending[f"table_provenance.{f}"] == softqa.STAGE_TABLE
    for f in RULING_GROUPS["human_review"]:
        assert rec["human_review"][f] is None and pending[f"human_review.{f}"] == softqa.STAGE_HUMAN
    for f in ("table_recompute_pass", "slot_validation_pass", "verified_columns_only"):
        assert rec["deterministic_validation"][f] is None and f"deterministic_validation.{f}" in pending
    assert rec["soft_link"]["c_g_t_s_d_audit"] is None and pending["soft_link.c_g_t_s_d_audit"] == softqa.STAGE_AUDIT
    # every null field in the seven groups is accounted for
    for g in RULING_GROUPS:
        for f, v in rec[g].items():
            if v is None:
                assert f"{g}.{f}" in pending, f"{g}.{f}"


def test_a_vocabulary_violation_is_nulled_and_recorded_not_coerced(schema):
    a = agent_record(status="rejected_pre_review", pre_review_status="rejected_pre_review")
    a["proposal"] = {**a["proposal"], "paper_geography_role": "somewhere", "concept_relation": "kinda"}
    rec = softqa.validate(softqa.map_trackc(a, schema), schema)
    assert rec["paper_provenance"]["paper_geography_role"] is None
    assert rec["mapping"]["invalid_agent_values"] == {"paper_provenance.paper_geography_role": "somewhere",
                                                      "soft_link.concept_relation": "kinda"}


def test_an_unknown_unit_rejection_maps_and_validates(schema):
    a = agent_record(status="rejected_pre_review", pre_review_status="rejected_pre_review", evidence=None,
                     concept_hit=None, place_hit=None, pre_review_checks={"unit_id_known": False, "qa_type_known": True})
    rec = softqa.validate(softqa.map_trackc(a, schema), schema)
    assert rec["paper_provenance"]["span_start"] is None
    assert rec["deterministic_validation"]["span_reslice_pass"] is None


def test_a_generator_that_saw_values_fails_the_schema(schema):
    rec = softqa.map_trackc(agent_record(table_values_visible_to_generator=True), schema)
    with pytest.raises(softqa.SchemaError, match="table_values_visible_to_generator"):
        softqa.validate(rec, schema)


def test_deterministic_pass_with_a_failed_mechanical_check_is_inconsistent(schema):
    a = agent_record()
    a["pre_review_checks"] = {**a["pre_review_checks"], "span_reslice_pass": False}
    with pytest.raises(softqa.SchemaError, match="span_reslice_pass"):
        softqa.validate(softqa.map_trackc(a, schema), schema)


def _on_unit(unit: str) -> dict:
    a = agent_record()
    a["proposal"] = {**a["proposal"], "unit_id": unit}
    return a


def _accept(rec: dict, status: str = "accepted") -> dict:
    rec["status"] = status
    rec["human_review"].update(reviewer_1_id="R1", reviewer_1_date="2026-10-28", reviewer_1_disposition="accept",
                               final_question="Q?", final_answer="A", final_status=status,
                               requires_second_review=False)
    return rec


def test_accepted_requires_a_frozen_final_qa_and_edit_history_for_edits(schema):
    # P-STATE-1: not under the FWI hold, so only the lifecycle rules apply here.
    rec = softqa.map_trackc(_on_unit("P-STATE-1"), schema)
    rec["status"] = "accepted"
    assert any("final_question" in e for e in softqa.consistency_errors(rec))
    hr = rec["human_review"]
    hr.update(reviewer_1_id="R1", reviewer_1_date="2026-10-28", reviewer_1_disposition="accept",
              final_question="Q?", final_answer="A", final_status="accepted", requires_second_review=False)
    assert softqa.consistency_errors(rec) == []
    softqa.validate(rec, schema)
    rec["status"] = hr["final_status"] = "accepted_after_edit"
    assert any("edit_history" in e for e in softqa.consistency_errors(rec))
    hr["edit_history"] = [{"reviewer_id": "R1", "date": "2026-10-28", "field": "final_question",
                           "before": "Does the table agree with the paper?", "after": "Q?"}]
    softqa.validate(rec, schema)
    hr["requires_second_review"] = True
    assert any("second review" in e for e in softqa.consistency_errors(rec))


# --- FWI hold (D-033 addendum) ------------------------------------------------

@pytest.mark.parametrize("unit", ["P-CELL-1", "P-COUNTY-1"])
@pytest.mark.parametrize("status", ["accepted", "accepted_after_edit"])
def test_fwi_units_cannot_be_accepted_and_get_hold_owner_confirmation(schema, unit, status):
    rec = softqa.map_trackc(_on_unit(unit), schema)
    gate = softqa.acceptance_gate(rec)
    assert gate["status"] == "hold_owner_confirmation" and unit in gate["reason"]
    assert "IC-006" in gate["reason"] and "owner-confirmed" in gate["reason"]
    _accept(rec, status)
    rec["human_review"]["edit_history"] = [{"reviewer_id": "R1", "date": "2026-10-28", "field": "final_question",
                                            "before": "Does the table agree with the paper?", "after": "Q?"}]
    with pytest.raises(softqa.SchemaError, match="hold_owner_confirmation"):
        softqa.validate(rec, schema)


def test_the_hold_also_refuses_a_final_status_left_in_human_review_alone(schema):
    rec = softqa.map_trackc(_on_unit("P-COUNTY-1"), schema)
    rec["status"] = "human_review"
    rec["human_review"]["final_status"] = "accepted"
    assert any("hold_owner_confirmation" in e for e in softqa.consistency_errors(rec))


def test_the_hold_does_not_block_review_or_other_units(schema):
    rec = softqa.map_trackc(_on_unit("P-COUNTY-1"), schema)
    rec["status"] = "human_review"
    assert softqa.consistency_errors(rec) == []                 # proposed and reviewed: allowed
    for unit in ("P-STATE-1", "F-HEAT", "F-FWI"):
        r = softqa.map_trackc(_on_unit(unit), schema)
        assert softqa.acceptance_gate(r) == {"status": "clear", "reason": None}
        softqa.validate(_accept(r), schema)


@pytest.mark.parametrize("col", ["wildfire_summer_Hist", "191", "wildfire_summer_Dend"])
def test_any_unit_whose_columns_include_the_unconfirmed_fwi_columns_is_held(schema, col):
    rec = softqa.map_trackc(_on_unit("F-FWI"), schema)
    rec["table_provenance"]["column_ids"] = ["some_other_column", col]
    gate = softqa.acceptance_gate(rec)
    assert gate["status"] == "hold_owner_confirmation"
    with pytest.raises(softqa.SchemaError, match="hold_owner_confirmation"):
        softqa.validate(_accept(rec), schema)


def test_the_hold_records_are_still_unconfirmed():
    """If IC-006/008/010 are ever promoted, this fails: lifting the hold needs a logged decision."""
    held = softqa.fwi_hold_columns()
    assert set(held.values()) == {"IC-006", "IC-008", "IC-010"}
    assert {"wildfire_summer_Hist", "wildfire_summer_Endc", "wildfire_summer_Dend", "189", "191", "193"} == set(held)


def test_the_protocol_documents_the_fwi_hold():
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "hold_owner_confirmation" in text and "IC-006" in text and "P-COUNTY-1" in text


def test_builtin_validator_agrees_with_jsonschema(schema):
    jsonschema = pytest.importorskip("jsonschema")
    v = jsonschema.Draft202012Validator(schema)
    good = softqa.map_trackc(agent_record(), schema)
    bad = []
    for mutate in (lambda r: r.pop("mapping"),
                   lambda r: r.__setitem__("status", "maybe"),
                   lambda r: r["paper_provenance"].__setitem__("span_start", -1),
                   lambda r: r["paper_provenance"].__setitem__("span_start", True),
                   lambda r: r["paper_provenance"].__setitem__("paper_sha256", "XYZ"),
                   lambda r: r["soft_link"].__setitem__("unmatched_dimensions", ["colour"]),
                   lambda r: r["human_review"].__setitem__("paper_fidelity", "maybe"),
                   lambda r: r["generation_controls"].__setitem__("answer_visible_to_generator", 0),
                   lambda r: r["candidate_identity"].__setitem__("extra", 1)):
        r = copy.deepcopy(good)
        mutate(r)
        bad.append(r)
    assert softqa.schema_errors(good, schema) == [] and v.is_valid(good)
    for r in bad:
        assert softqa.schema_errors(r, schema) != [] and not v.is_valid(r)


# --- Track C inputs --------------------------------------------------------------

#: Years, labels, and the P-STATE-1 metric's threshold (COORDINATOR, D-033 addendum: the threshold is the metric name).
ALLOWED_NUMERIC = re.compile(r"\b(?:19|20)\d{2}\b|R106C361|RCP8\.5|P-(?:CELL|COUNTY|STATE)-1|\bv\d\b|_v\d\b|105 \u00b0F")


def test_unit_definitions_carry_no_number_and_no_direction():
    text = (SOFTQA / "units_definitions_v1.json").read_text(encoding="utf-8")
    assert not re.search(r"\d", ALLOWED_NUMERIC.sub("", text))
    assert not re.search(r"value|increase|decrease|change[- ]by", text, re.IGNORECASE)


def test_units_pass_the_agents_startup_check_and_match_the_concept_map():
    units = json.loads((SOFTQA / "units_definitions_v1.json").read_text(encoding="utf-8"))["units"]
    assert [u["unit_id"] for u in units] == ["P-CELL-1", "P-COUNTY-1", "P-STATE-1", "F-FWI", "F-HEAT"]
    forbidden = {"value", "values", "computed", "answer", "change", "baseline_value", "future_value"}
    assert all(not (forbidden & set(u)) for u in units)
    cmap = yaml.safe_load((REPO_ROOT / "data" / "metadata" / "concept_map.yaml").read_text(encoding="utf-8"))
    approved = {e["canonical_id"]: list(e["accepted_surface_terms"]) + [
        t["term"] for t in e.get("additional_surface_terms", []) if t["status"] == "approved_lexical"]
        for e in cmap["entries"] if e["level"] == "family" and e["status"] == "approved_lexical"}
    for u in units:
        assert u["family_surface_terms"] == approved[u["family"]], u["unit_id"]
        assert "extended heat index" not in u["family_surface_terms"]
    places = {u["unit_id"]: u["place_terms"] for u in units}
    assert places == {"P-CELL-1": [], "P-COUNTY-1": ["oklahoma", "stephens"], "P-STATE-1": ["california"],
                      "F-FWI": [], "F-HEAT": []}
    assert {u["unit_id"]: u["place_label"] for u in units}["F-FWI"] == "none"
    assert [u["family"] for u in units] == ["fire_weather_index"] * 2 + ["heat_index", "fire_weather_index",
                                                                         "heat_index"]


def test_p_state_1_names_its_metric_and_threshold():
    units = {u["unit_id"]: u for u in json.loads((SOFTQA / "units_definitions_v1.json").read_text(encoding="utf-8"))["units"]}
    assert units["P-STATE-1"]["definition"].startswith(
        "The number of summer days with daily maximum heat index above 105 \u00b0F, over the ClimRR rows")
    text = (SOFTQA / "units_definitions_v1.json").read_text(encoding="utf-8")
    assert text.count("105") == 1                                     # the threshold, nowhere else


def test_fwi_definitions_say_index_not_fire_and_historical_is_modeled():
    for u in json.loads((SOFTQA / "units_definitions_v1.json").read_text(encoding="utf-8"))["units"]:
        if u["family"] == "fire_weather_index":
            assert "not fire occurrence" in u["definition"]
        if "1995-2004" in u["definition"]:
            assert "modeled historical baseline 1995-2004" in u["definition"]


def test_qa_types_are_the_six_candidates_none_validated():
    q = json.loads((SOFTQA / "qa_types_v1.json").read_text(encoding="utf-8"))["qa_types"]
    assert [t["qa_type"] for t in q] == ["pattern_to_explanation", "claim_to_region_identification",
                                         "cross_source_validation", "compound_risk_reasoning", "regional_contrast",
                                         "cross_location_comparison"]
    assert all(t["status"] == "candidate QA type, not yet validated" for t in q)
    assert all(t["description"].count(". ") == 0 and t["description"].endswith(".") for t in q)


def _freeze():
    spec = importlib.util.spec_from_file_location("ftc", REPO_ROOT / "scripts" / "freeze_trackc_candidates.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_trackc_candidates_are_the_frozen_place_lists_with_the_twenty_read_papers():
    path = SOFTQA / "trackc_candidates_v1.json"
    recs = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(recs, list) and len(recs) == 243
    assert all(set(r) == {"item_id", "arm"} for r in recs)
    for arm, n in (("fire_weather_v1", 100), ("extreme_heat_v1", 143)):
        ids = (PLACE_DIR / f"{arm}_place_candidates.txt").read_text().split()
        assert [r["item_id"] for r in recs if r["arm"] == arm] == ids and len(ids) == n
    mod = _freeze()
    built, info = mod.build()
    assert mod.render(built) == path.read_text(encoding="utf-8")
    entry = next(f for f in json.loads((REPO_ROOT / "data" / "manifest.json").read_text())["files"]
                 if f["filename"] == "trackc_candidates_v1.json")
    assert entry["already_read_m4_wp4"] == info["already_read"] and len(info["already_read"]) == 20
    assert {(r["item_id"], r["arm"]) for r in info["already_read"]} <= {(r["item_id"], r["arm"]) for r in recs}


# --- review protocol, form and view ---------------------------------------------

def _ruling_list(heading: str) -> list[str]:
    """The bullet items under a ruling heading, verbatim."""
    text = RULING.read_text(encoding="utf-8").split(heading, 1)[1]
    items = []
    for line in text.splitlines()[1:]:
        if line.startswith("- "):
            items.append(line[2:])
        elif items and (line.startswith("#") or (line.strip() and not line.startswith("- ") and items)):
            break
    return items


def test_protocol_carries_the_rulings_lists_verbatim():
    proto = PROTOCOL.read_text(encoding="utf-8")
    prereq = _ruling_list("#### Deterministic prerequisites before human review")
    second = _ruling_list("#### Mandatory second reviewer")
    checklist = _ruling_list("#### Human-review checklist")
    assert (len(prereq), len(second), len(checklist)) == (14, 10, 10)
    for i, item in enumerate(prereq, 1):
        assert f"{i}. {item}" in proto
    for i, item in enumerate(second, 1):
        assert f"{i}. {item}" in proto
    for i, item in enumerate(checklist, 1):
        assert f"{i}. {item}" in proto
    for line in ("1. paper passage;", "2. table provenance and deterministic values;", "3. QA pair;",
                 "4. candidate semantic annotations;", "5. agent rationale/confidence last."):
        assert line in proto
    assert "status = needs_adjudication" in proto and "status = rejected_pre_review" in proto
    assert "with the final edited QA frozen." in proto


def test_review_form_has_exactly_the_ten_checklist_fields():
    form = yaml.safe_load((SOFTQA / "review_form_v1.yaml").read_text(encoding="utf-8"))
    assert form["form_version"] == "review_form_v1"
    assert list(form["checklist"]) == CHECKLIST
    assert all(v is None for v in form["checklist"].values())
    text = (SOFTQA / "review_form_v1.yaml").read_text(encoding="utf-8")
    assert "accept | accept_with_edit | ambiguous | reject" in text


def _view():
    spec = importlib.util.spec_from_file_location("srv", REPO_ROOT / "scripts" / "softqa_review_view.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_view_renders_in_review_order_and_withholds_rationale(schema):
    view = _view()
    rec = softqa.map_trackc(agent_record(), schema)
    hidden = view.render(rec)
    positions = [hidden.index(t) for t in view.SECTION_TITLES]
    assert positions == sorted(positions)
    assert hidden.index(PASSAGE) < positions[1]                       # the passage is in section 1
    assert hidden.index("Does the table agree with the paper?") > positions[2]
    assert "SECRET-RATIONALE" not in hidden and "SECRET-CONFIDENCE" not in hidden
    assert view.WITHHELD in hidden
    assert "pending: " + softqa.STAGE_TABLE in hidden
    shown = view.render(rec, show_rationale=True)
    assert shown.index("SECRET-RATIONALE") > shown.index(view.SECTION_TITLES[4])
    assert "SECRET-CONFIDENCE-high" in shown and view.WITHHELD not in shown


def test_view_cli_reads_agent_jsonl_and_writes_a_run_record(tmp_path, capsys):
    view = _view()
    src = tmp_path / "candidates.jsonl"
    src.write_text(json.dumps(agent_record()) + "\n" + json.dumps(agent_record(candidate_id="C-4001-02")) + "\n")
    runs = tmp_path / "runs"
    assert view.main(["--candidates", str(src), "--candidate-id", "C-4001-02", "--runs-dir", str(runs)]) == 0
    assert "CANDIDATE C-4001-02" in capsys.readouterr().out
    rr = json.loads(next(runs.glob("*.json")).read_text())
    assert rr["result_summary"]["rationale_shown"] is False and rr["data_sha256"] == sha256_file(src)
    assert view.main(["--candidates", str(src), "--candidate-id", "C-NONE", "--runs-dir", str(runs)]) == 2
