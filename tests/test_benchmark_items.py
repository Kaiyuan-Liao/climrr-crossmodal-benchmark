"""Item schema v2 and its validator (pilot P1, D-041; GUIDANCE re-anchor ruling 2026-10-29).

The item here is a synthetic test fixture --- not a benchmark item, not generated,
not an answer key. Its table pattern is a real extractor record (from the tracked
examples file); its literature supports are synthetic.
"""

from __future__ import annotations

import copy
import json

import pytest

from climrr import benchmark_items as bi
from climrr import table_patterns as tp

SCHEMA = bi.load_schema()
PATTERN = tp.read_jsonl(tp.EXAMPLES_PATH)[0]
PASSAGE = "Warming raises the saturation vapor pressure, so humid heat extremes intensify."

FIELDS = ["schema_version", "item_id", "use_case_level", "capability_tested", "system_task", "reasoning_modalities",
          "key_relationships", "evidence_needed", "desired_output_characteristics", "expected_knowledge_level",
          "prompt", "source_independent_answerability", "source_independence_note", "source_leakage_check",
          "reference_components", "reference_answer", "rubric", "guardrails", "c_g_t_s_d_audit", "generation", "review"]


def _support(paper, review=False):
    return {"paper_item_id": paper, "paper_sha256": (paper * 64)[:64].replace(paper[0], "a"), "json_path": "$.results",
            "span_start": 10, "span_end": 10 + len(PASSAGE), "verbatim_passage": PASSAGE,
            "independence_note": "different author group and data", "is_review_or_synthesis": review}


def _statement(strength="multi_source_supported", stype="mechanism", scope="regional_climate_expectation", papers=("1", "2")):
    sups = [_support(p) for p in papers]
    for i, s in enumerate(sups):
        s["paper_sha256"] = f"{i + 1:x}" * 64
    return {"statement": "Warmer, moister summers raise heat-index extremes.", "statement_type": stype,
            "evidence_strength": strength, "reference_scope": scope, "supports": sups}


def make_item(**over):
    prompt = ("How are days with a dangerously high heat index projected to change across the southern Great Plains "
              "by mid-century under a high-emissions scenario, and why?")
    item = {
        "schema_version": "benchmark_item_v2", "item_id": "BI-TEST-0001", "use_case_level": 3,
        "capability_tested": "joins a projected hazard pattern to its mechanism",
        "system_task": "retrieves the projected pattern and explains it",
        "reasoning_modalities": "Hazard + Text", "key_relationships": "heat index → season → region → scenario → horizon",
        "evidence_needed": "direction of change; physical driver", "desired_output_characteristics": "direction, mechanism, caveats",
        "expected_knowledge_level": "general_climate_science", "prompt": prompt,
        "source_independent_answerability": "yes", "source_independence_note": "a general regional climate question",
        "source_leakage_check": bi.leakage_check(prompt),
        "reference_components": {"table_patterns": [copy.deepcopy(PATTERN)], "literature_mechanisms": [_statement()],
                                 "literature_caveats": []},
        "reference_answer": {"table_pattern": "increase", "literature_interpretation": "moister, warmer air", "integrated": "x"},
        "rubric": {"required_points": ["direction"], "acceptable_variants": ["more frequent"], "optional_points": [],
                   "disallowed_claims": ["RCP8.5 is the only future"], "fatal_errors": ["says decrease"]},
        "guardrails": ["RCP8.5 is one high-emissions scenario"], "c_g_t_s_d_audit": {"C": "match"},
        "generation": {"generator_version": "test", "model": None, "prompt_hash": None, "timestamp": "2026-10-29T00:00:00Z",
                       "inputs_sha256": {}},
        "review": {"status": "human_review", "history": [], "kaiyuan_disposition": None, "mentor_disposition": None,
                   "final_frozen": None},
    }
    item.update(over)
    return item


def test_schema_names_every_field_exactly():
    assert SCHEMA["required"] == FIELDS
    rc = SCHEMA["properties"]["reference_components"]["properties"]
    assert set(rc) == {"table_patterns", "literature_mechanisms", "literature_caveats"}
    tp_req = SCHEMA["$defs"]["table_pattern"]["required"]
    assert tp_req == ["family", "season", "horizon", "scenario", "statistic", "geography_type", "geography", "direction",
                      "computed_value_or_range", "rank", "relative_magnitude", "pattern_support_n", "pattern_robustness",
                      "provenance"]
    assert SCHEMA["$defs"]["table_pattern"]["properties"]["provenance"]["required"] == [
        "columns", "column_statuses", "row_rule", "derivation_rule_id", "code_version", "table_data_sha256"]
    assert SCHEMA["$defs"]["literature_statement"]["properties"]["supports"]["items"]["required"] == [
        "paper_item_id", "paper_sha256", "json_path", "span_start", "span_end", "verbatim_passage", "independence_note"]
    assert SCHEMA["properties"]["source_leakage_check"]["required"] == [
        "clmrr_named", "row_or_column_named", "paper_named", "hidden_exact_value_required", "according_to_phrase", "pass"]
    assert set(SCHEMA["properties"]["rubric"]["required"]) == {"required_points", "acceptable_variants", "optional_points",
                                                                "disallowed_claims", "fatal_errors"}
    assert SCHEMA["properties"]["review"]["required"] == ["status", "history", "kaiyuan_disposition", "mentor_disposition",
                                                           "final_frozen"]


def test_a_well_formed_item_validates():
    assert bi.validate(make_item())


def test_schema_refuses_unknown_and_missing_fields():
    item = make_item(extra="x")
    assert any("unexpected field 'extra'" in e for e in bi.schema_errors(item))
    item = make_item()
    del item["system_task"]
    assert any("system_task" in e for e in bi.schema_errors(item))
    assert bi.schema_errors(make_item(expected_knowledge_level="expert"))


# --- leakage ---------------------------------------------------------------------------


@pytest.mark.parametrize("prompt,field", [
    ("What does ClimRR project for Texas heat?", "clmrr_named"),
    ("What does Clim-RR show?", "clmrr_named"),
    ("How does heatindex_E85_Day105 change in Texas?", "row_or_column_named"),
    ("Is the GEOID relevant to heat?", "row_or_column_named"),
    ("What happens in cell R106C361?", "row_or_column_named"),
    ("What did LIT2-000185 find about fire weather?", "paper_named"),
    ("Do you agree with Smith et al. on fire weather?", "paper_named"),
    ("Is the finding (Jones, 2019) on heat correct?", "paper_named"),
    ("Why does fire weather rise by 3.25 in California?", "hidden_exact_value_required"),
    ("Why do heat days rise 40% in Texas?", "hidden_exact_value_required"),
    ("According to the data, how does heat change?", "according_to_phrase"),
    ("What does this table show for heat?", "according_to_phrase"),
])
def test_leakage_check_flags(prompt, field):
    out = bi.leakage_check(prompt)
    assert out[field] is True and out["pass"] is False and out["flags"]


def test_leakage_check_passes_a_general_question_and_a_threshold_name():
    out = bi.leakage_check("How will days with a heat index above 105 °F change across the Southeast by mid-century "
                           "(2045–2054) under a high-emissions scenario?")
    assert out["pass"] is True and out["flags"] == []
    assert bi.leakage_check("Which state has the most heat?")["pass"] is True   # 'State' is a generic column name


def test_stored_leakage_check_must_match_the_recomputation():
    item = make_item(prompt="According to ClimRR, how does heat change?")
    errs = bi.consistency_errors(item)
    assert any("clmrr_named" in e for e in errs) and any("according_to_phrase" in e for e in errs)


# --- evidence strength -------------------------------------------------------------------


def test_multi_source_needs_two_papers():
    s = _statement(papers=("1",))
    assert any(">= 2 independent papers" in e for e in bi.statement_errors("m", s))


def test_single_source_is_never_consensus():
    s = _statement(strength="single_source_supported", stype="consensus", papers=("1",))
    assert any("not framed as consensus" in e for e in bi.statement_errors("m", s))
    s = _statement(strength="single_source_supported", scope="broad_consensus", papers=("1",))
    assert any("not framed as consensus" in e for e in bi.statement_errors("m", s))
    ok = _statement(strength="single_source_supported", stype="caveat", scope="single_study_observation", papers=("1",))
    assert bi.statement_errors("m", ok) == []


def test_review_supported_needs_a_marked_synthesis():
    s = _statement(strength="review_supported", papers=("1",))
    assert any("is_review_or_synthesis" in e for e in bi.statement_errors("m", s))
    s["supports"][0]["is_review_or_synthesis"] = True
    assert bi.statement_errors("m", s) == []


def test_span_length_must_match_the_passage():
    s = _statement()
    s["supports"][0]["span_end"] += 1
    assert any("span length" in e for e in bi.statement_errors("m", s))


def test_relative_magnitude_must_be_disclosed_as_relative():
    item = make_item()
    item["reference_components"]["table_patterns"][0]["relative_magnitude"] = {"class": "large", "definition": "x" * 50}
    assert any("relative tercile" in e for e in bi.consistency_errors(item))


# --- validity conditions A-F -----------------------------------------------------------------


def test_unreviewed_item_fails_only_human_acceptance():
    v = bi.validity(make_item())
    assert v["benchmark_valid"] is False
    assert [k for k, x in v.items() if k != "benchmark_valid" and not x["met"]] == ["F_human_acceptance"]


def test_accepted_by_both_and_frozen_is_valid():
    item = make_item()
    item["review"].update(status="accepted", kaiyuan_disposition={"disposition": "accept"},
                          mentor_disposition={"disposition": "accept_after_edit"},
                          final_frozen={"prompt": item["prompt"], "reference_answer": item["reference_answer"],
                                        "rubric": item["rubric"]})
    bi.validate(item)
    assert bi.validity(item)["benchmark_valid"] is True


def test_accepted_without_the_mentor_is_inconsistent():
    item = make_item()
    item["review"].update(status="accepted", kaiyuan_disposition={"disposition": "accept"},
                          final_frozen={"prompt": "p", "reference_answer": {}, "rubric": {}})
    assert any("mentor acceptance" in e for e in bi.consistency_errors(item))


@pytest.mark.parametrize("answerability", ["borderline", "no"])
def test_only_yes_answerability_is_valid(answerability):
    v = bi.validity(make_item(source_independent_answerability=answerability))
    assert not v["A_source_independent_prompt"]["met"]


def test_an_acceptance_blocked_pattern_fails_condition_b():
    item = make_item()
    item["reference_components"]["table_patterns"][0].update(acceptance_blocked=True, acceptance_blocked_by=["IC-006"])
    assert not bi.validity(item)["B_deterministic_table_facts"]["met"]


def test_single_source_core_mechanism_must_be_scoped_as_one_study():
    item = make_item()
    item["reference_components"]["literature_mechanisms"] = [
        _statement(strength="single_source_supported", papers=("1",))]
    assert not bi.validity(item)["D_explicit_evidence_strength"]["met"]


def test_decomposition_requires_both_parts_and_rubric_tolerance():
    item = make_item()
    item["reference_answer"]["literature_interpretation"] = None
    item["rubric"]["fatal_errors"] = []
    reasons = bi.validity(item)["E_reference_answer_decomposition"]["reasons"]
    assert any("literature_interpretation" in r for r in reasons) and any("fatal_errors" in r for r in reasons)


def test_every_tracked_example_pattern_validates():
    assert all(bi.table_pattern_errors(p, SCHEMA) == [] for p in tp.read_jsonl(tp.EXAMPLES_PATH))


def test_schema_is_json_and_resolves():
    resolved = bi.resolve_refs(SCHEMA)
    assert "$ref" not in json.dumps(resolved)


def test_schema_is_pinned_in_the_manifest():
    from climrr.manifest import MANIFEST_PATH, load_entry

    entry = load_entry("item_schema_v2.json", MANIFEST_PATH)
    assert entry["path"] == "data/metadata/benchmark/item_schema_v2.json"
    assert bi.schema_sha256() == entry["sha256"]
