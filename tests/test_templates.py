"""Track D v1 templates (D-031, D-033, D-034): slots, templates, the answer gate,
the arithmetic, the prototype reproduction and the committed outputs.

Synthetic tables only for the engine; the real table is never read here. The
full `questions_v1.jsonl` is gitignored (regenerable, pinned by hash): its test
fails when the file is absent unless CLIMRR_ALLOW_MISSING_RAW=1, as for the raw
table it is computed from.
"""

from __future__ import annotations

import copy
import csv
import json
import os
import pytest

from climrr import templates as td
from climrr.phenomenon import PROVISIONAL_AGGREGATION_LABEL

SLOTS = td.load_yaml(td.SLOTS_PATH)
TEMPLATES = td.load_yaml(td.TEMPLATES_PATH)
COVERAGE = td.load_coverage()
CONCEPT_MAP = td.load_yaml(td.CONCEPT_MAP_PATH)
DICT_LINES = td.DICTIONARY_TEXT_PATH.read_text(encoding="utf-8").splitlines()
SUMMARY = json.loads(td.SUMMARY_PATH.read_text(encoding="utf-8"))
REPRO = json.loads(td.REPRODUCTION_PATH.read_text(encoding="utf-8"))
SAMPLE = td.read_jsonl(td.SAMPLE_PATH)


def _validate(slots):
    td.validate_slots(slots, dictionary_lines=DICT_LINES, coverage=COVERAGE, concept_map=CONCEPT_MAP)


# --- slots ----------------------------------------------------------------------


def test_no_slot_value_without_a_source_or_authorization():
    values = td.slot_values(SLOTS)
    assert len(values) > 80
    for where, node in values:
        assert node.get("source"), f"{where}: no source"
        assert node.get("authorization") in td.AUTHORIZATIONS, f"{where}: {node.get('authorization')!r}"


def test_slots_validate_against_dictionary_coverage_and_concept_map():
    _validate(SLOTS)


@pytest.mark.parametrize("mutate", [
    lambda s: s["period"][0].pop("source"),
    lambda s: s["location"]["state"]["values"][0].pop("authorization"),
    lambda s: s["concept"]["governed"][0]["metrics"][0]["period_columns"]["historical"].update(authorization="verified"),
    lambda s: s["concept"]["governed"][1]["metrics"][0]["period_columns"]["historical"].update(status="inferred_candidate"),
    lambda s: s["scenario"][1]["source"].update(quote="RCP8.5 is observed"),
    lambda s: s["concept"]["governed"][1]["surface_forms"].append(
        {"term": "extreme heat days", "source": {"kind": "concept_map_accepted_surface_term", "canonical_id": "heat_index"},
         "authorization": "verified"}),
    lambda s: s["concept"]["governed"][0]["metrics"][0].update(authorization="verified"),
])
def test_validate_slots_rejects(mutate):
    slots = copy.deepcopy(SLOTS)
    mutate(slots)
    with pytest.raises(td.TemplateError):
        _validate(slots)


def test_fwi_value_columns_are_inferred_candidate_and_heat_index_verified():
    fwi, heat = SLOTS["concept"]["governed"]
    assert fwi["id"] == "fire_weather_index" and heat["id"] == "heat_index"
    for col in fwi["metrics"][0]["period_columns"].values():
        assert COVERAGE[col["index"]]["status"] == "inferred_candidate"
    assert fwi["metrics"][0]["authorization"] == "inferred_candidate"
    assert "NOT usable for answer computation" in fwi["authorization_note"]
    assert len(heat["metrics"]) == 4
    for metric in heat["metrics"]:
        for col in metric["period_columns"].values():
            assert COVERAGE[col["index"]]["status"] == "verified_from_dictionary"


def test_ungoverned_concepts_are_listed_and_never_fillable():
    names = " ".join(e["name"] for e in SLOTS["concept"]["ungoverned"])
    for word in ("temperature", "precipitation", "wind speed", "consecutive", "degree days"):
        assert word in names
    for e in SLOTS["concept"]["ungoverned"]:
        assert e["authorization"] == "not_authorized"
        assert e["status"].startswith("ungoverned")
    families = {m["family"]["id"] for m in td.governed_metrics(SLOTS)}
    assert families == {"fire_weather_index", "heat_index"}


def test_location_statuses_and_state_list():
    states = td.location_values(SLOTS, "state")
    assert len(states) == 49 and "" not in {s["label"] for s in states}
    assert sum(s["n_cells"] for s in states) + 7 == 62834
    assert SLOTS["location"]["state"]["column"]["status"] == COVERAGE[3]["status"] == "inferred_candidate"
    assert SLOTS["location"]["county"]["authorization"] == "our_reading"
    assert SLOTS["location"]["cell"]["authorization"] == "verified"


def test_rcp45_is_realized_by_no_governed_column():
    rcp45 = td.by_id(SLOTS["scenario"])["RCP4.5"]
    assert all(not v for v in rcp45["realized_by"].values())


def test_statistics_carry_rule_ids():
    rules = {s["id"]: s["rule_id"] for s in SLOTS["statistic"]}
    for stat in ("absolute_change", "percent_change", "baseline_value", "future_value", "direction"):
        assert rules[stat].startswith("DR-TD-")
    assert "zero" in td.by_id(SLOTS["statistic"])["percent_change"]["rule"]


# --- templates --------------------------------------------------------------------


def test_templates_validate():
    td.validate_templates(TEMPLATES, SLOTS, td.load_qa_types())


def test_template_coverage_of_required_kinds():
    items = TEMPLATES["templates"]
    assert 15 <= len(items) <= 20
    names = " ".join(t["name"] for t in items)
    for kind in ("direction of change", "magnitude of change", "two scenarios", "two places", "two periods",
                 "multi-concept", "cross-location comparison", "claim to region"):
        assert kind in names, kind
    assert {t["category_type"] for t in items} == set(TEMPLATES["category_types"])
    assert {t["research_method"] for t in items} == set(TEMPLATES["research_methods"])
    assert {t["answer_mode"] for t in items} == set(TEMPLATES["answer_modes"])
    for t in items:
        assert t["answerable_now"] is (t["answer_mode"] == "table_only")
    multi = [t for t in items if "CONCEPT_2" in t["required_slots"]]
    assert multi and all(t["enumeration"]["concept_pairs"] == [["fire_weather_index", "heat_index"]]
                         for t in multi if t["answer_mode"] == "table_only")


def test_validate_templates_rejects_marker_mismatch():
    bad = copy.deepcopy(TEMPLATES)
    bad["templates"][0]["text"] += " [LOCATION_2]"
    with pytest.raises(td.TemplateError):
        td.validate_templates(bad, SLOTS, td.load_qa_types())


# --- the engine on a synthetic table ------------------------------------------------


def _synthetic_slots():
    slots = copy.deepcopy(SLOTS)
    block = slots["location"]["state"]
    proto = block["values"][0]
    block["values"] = [dict(proto, label="Alpha", n_cells=2), dict(proto, label="Beta", n_cells=2)]
    slots["location"]["county"]["values"][0].update(state="Alpha", name="Gamma", label="Alpha|Gamma", n_cells=2)
    slots["location"]["cell"]["values"][0].update(label="R1C1", wording="grid cell R1C1")
    return slots


def _write_table(tmp_path, rows):
    header = [COVERAGE[i]["column"] for i in range(len(COVERAGE))]
    path = tmp_path / "synthetic.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for values in rows:
            row = [""] * len(header)
            for index, value in values.items():
                row[index] = value
            writer.writerow(row)
    return path


def _row(cell, state, name, his105, m105, e105, fwi=("10.0", "12.0", "15.0", "2.0", "5.0")):
    values = {1: cell, 2: name, 3: state}
    for base, val in ((240, his105), (241, his105), (242, "0.000000000000000"), (243, "0.000000000000000")):
        values[base] = val
    for base, val in ((246, m105), (247, m105), (248, "0.000000000000000"), (249, "0.000000000000000")):
        values[base] = val
    for base, val in ((252, e105), (253, e105), (254, "0.000000000000000"), (255, "0.000000000000000")):
        values[base] = val
    for index, val in zip((189, 190, 191, 192, 193), fwi):
        values[index] = val
    return values


@pytest.fixture
def synthetic(tmp_path):
    rows = [
        _row("R1C1", "Alpha", "Gamma", "2.000000000000000", "3.000000000000000", "5.000000000000000"),
        _row("R1C2", "Alpha", "Gamma", "4.000000000000000", "4.000000000000000", "9.000000000000000"),
        _row("R2C1", "Beta", "Delta", "0.000000000000000", "1.000000000000000", "1.000000000000000"),
        _row("R2C2", "Beta", "Delta", "", "", ""),  # empty: excluded, never read as zero
        _row("R3C1", "", "", "1.000000000000000", "1.000000000000000", "1.000000000000000"),
    ]
    slots = _synthetic_slots()
    scan = td.scan_table(_write_table(tmp_path, rows), slots, TEMPLATES["period_pairs"])
    return slots, scan


def _metric(slots, metric_id):
    return next(m for m in td.governed_metrics(slots) if m["metric"]["metric_id"] == metric_id)["metric"]


def _loc(slots, level, label):
    return next(v for v in td.location_values(slots, level) if v["label"] == label)


def test_generator_refuses_inferred_columns(synthetic):
    slots, scan = synthetic
    fwi = _metric(slots, "fwi_summer_seasonal_value")
    for stat in ("absolute_change", "direction", "percent_change"):
        r = td.compute_statistic(scan, _loc(slots, "cell", "R1C1"), fwi, stat, "historical", "end_century")
        assert r["status"] == td.BLOCKED and r["value"] is None and "IC-006" in r["reason"]
    audit = td.compute_statistic(scan, _loc(slots, "cell", "R1C1"), fwi, "absolute_change", "historical",
                                 "end_century", audit=True)
    assert audit["status"] == td.COMPUTED and audit["value"] == "5.000000000000000"  # the Dend column, not 15 - 10
    assert audit["derivation"]["raw_aggregates"]["change_operation"] == "change_column_value"


def test_state_mean_skips_empty_cells_and_labels_the_mean(synthetic):
    slots, scan = synthetic
    hi = _metric(slots, "heatindex_days_above_105F")
    beta = _loc(slots, "state", "Beta")
    r = td.compute_statistic(scan, beta, hi, "absolute_change", "historical", "end_century")
    assert r["status"] == td.COMPUTED and r["value"] == "1.000000000000000"
    agg = r["derivation"]["raw_aggregates"]
    assert agg["n_cells_used"] == 1 and agg["aggregation_label"] == PROVISIONAL_AGGREGATION_LABEL
    assert r["derivation"]["location"]["n_cells"] == 2
    alpha = td.compute_statistic(scan, _loc(slots, "state", "Alpha"), hi, "absolute_change", "historical", "end_century")
    assert alpha["value"] == "4.000000000000000"  # mean of (5-2, 9-4)


def test_percent_change_guards_zero_baseline(synthetic):
    slots, scan = synthetic
    hi = _metric(slots, "heatindex_days_above_105F")
    r = td.compute_statistic(scan, _loc(slots, "state", "Beta"), hi, "percent_change", "historical", "end_century")
    assert r["status"] == td.NOT_COMPUTABLE and r["reason"] == "zero_baseline" and r["value"] is None
    ok = td.compute_statistic(scan, _loc(slots, "state", "Alpha"), hi, "percent_change", "historical", "end_century")
    assert ok["value"] == "133.333333333333333"  # 100 x mean change 4 / mean baseline 3


def test_baseline_value_and_direction(synthetic):
    slots, scan = synthetic
    hi = _metric(slots, "heatindex_days_above_105F")
    alpha = _loc(slots, "state", "Alpha")
    assert td.compute_statistic(scan, alpha, hi, "baseline_value", "historical", None)["value"] == "3.000000000000000"
    assert td.compute_statistic(scan, alpha, hi, "future_value", None, "mid_century")["value"] == "3.500000000000000"
    assert td.compute_statistic(scan, alpha, hi, "direction", "mid_century", "end_century")["value"] == "increase"


def test_compare_signed():
    assert td.compare_signed("1.0", "2.0", "a", "b") == "b"
    assert td.compare_signed("-1.0", "-2.0", "a", "b") == "a"
    assert td.compare_signed("1.0", "1.00", "a", "b") == "equal"


def test_scan_rejects_a_wrong_header(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("a,b,c,d\n", encoding="utf-8")
    with pytest.raises(td.TemplateError):
        td.scan_table(path, _synthetic_slots(), TEMPLATES["period_pairs"])


def test_build_questions_on_synthetic_table(synthetic):
    slots, scan = synthetic
    templates = copy.deepcopy(TEMPLATES)
    next(t for t in templates["templates"] if t["template_id"] == "TD-T07")["enumeration"]["anchor_state"] = "Alpha"
    records = td.build_questions(slots, templates, scan, "0" * 64)
    _check_invariants(records)
    by_t = {}
    for r in records:
        by_t.setdefault(r["template_id"], []).append(r)
    assert all(r["answer_status"] == td.NOT_COMPUTABLE or r["answer_status"] == td.BLOCKED for r in by_t["TD-T06"])
    assert all(r["answer_status"] == td.BLOCKED for r in by_t["TD-T09"])
    t10 = [r for r in by_t["TD-T10"] if r["answer_status"] == td.COMPUTED]
    assert t10 and all(isinstance(r["answer"], list) for r in t10)
    ids = [r["question_id"] for r in records]
    assert len(ids) == len(set(ids))
    again = td.build_questions(slots, templates, scan, "0" * 64)
    assert again == records  # deterministic


def _columns_in(derivation):
    if not derivation:
        return []
    cols = list(derivation.get("columns") or [])
    for part in derivation.get("parts") or []:
        if isinstance(part, dict) and "question_id" not in part:
            cols.extend(_columns_in(part))
    return cols


def _check_invariants(records):
    for r in records:
        assert r["answer_status"] in td.ANSWER_STATUSES
        assert not td.MARKER_RE.search(r["question_text"])
        families = {s["value_id"].split(":")[0] for m, s in r["slots"].items() if m.startswith("CONCEPT")}
        if "fire_weather_index" in families:
            assert r["answer_status"] == td.BLOCKED, r["question_id"]
            assert r["answer"] is None and r["retrieval_authorized"] is False and r["usable_for"] == []
            assert "C-fire_weather" in r["cautions"]
        if r["answer_status"] == td.COMPUTED:
            assert r["answer"] is not None and r["answer_reason"] is None
            for col in _columns_in(r["answer_derivation"]):
                assert col["status"] in td.COMPUTABLE_COLUMN_STATUSES, (r["question_id"], col)
            if any(s["authorization"] != "verified" for m, s in r["slots"].items() if m.startswith("LOCATION")):
                assert r["provisional"] is True
        else:
            assert r["answer"] is None and r["answer_reason"]
        for term in r["retrieval_terms"]:
            low = term.lower()
            assert not any(w in low for w in td.FORBIDDEN_RETRIEVAL_WORDS), term
            assert not td.CELL_LABEL_RE.match(term)
        assert "Stephens" not in r["retrieval_terms"] and "Gamma" not in r["retrieval_terms"]
        for s in r["slots"].values():
            assert s["source_ref"] and s["authorization"] in td.AUTHORIZATIONS


# --- the committed outputs ------------------------------------------------------------


def test_prototype_reproduction_equals_frozen_values():
    assert REPRO["all_equal"] is True
    by_id = {e["record_id"]: e for e in REPRO["prototypes"]}
    assert set(by_id) == {"P-CELL-1", "P-COUNTY-1", "P-STATE-1"}
    for spec in td.PROTOTYPE_FILLS:
        frozen = td.frozen_prototype_values(json.loads((td.PROTOTYPES_DIR / spec["file"]).read_text(encoding="utf-8")))
        entry = by_id[spec["record_id"]]
        assert entry["computed"] == frozen == entry["frozen"]
        assert entry["prototype_sha256"] == td.file_sha256(td.PROTOTYPES_DIR / spec["file"])
    # the two FWI prototypes: audit only; their questions stay blocked
    for rid in ("P-CELL-1", "P-COUNTY-1"):
        assert by_id[rid]["audit_only"] is True
        assert by_id[rid]["question_answer_status"] == td.BLOCKED and by_id[rid]["question_answer"] is None
    state = by_id["P-STATE-1"]
    assert state["question_answer_status"] == td.COMPUTED
    assert state["question_answer"] == "13.209951652865228" == state["frozen"]["absolute_change"]


def test_sample_invariants_and_examples():
    _check_invariants(SAMPLE)
    examples = td.example_records(SAMPLE, TEMPLATES)
    assert len(examples) == 10
    assert sum(r["answer_status"] == td.COMPUTED for r in examples) == 9


def test_summary_counts_are_consistent():
    s = SUMMARY
    assert s["n_templates"] == len(TEMPLATES["templates"]) == 18
    assert s["n_templates_table_only"] == 11
    assert sum(s["by_answer_status"].values()) == s["n_questions"] == s["questions_file"]["n_records"]
    assert sum(s["by_template"].values()) == s["n_questions"]
    assert s["by_concept_family_and_status"].get("fire_weather_index|computed", 0) == 0
    assert s["questions_file"]["tracked_in_git"] is False


def test_generated_doc_is_current():
    hashes = td.doc_hashes(SUMMARY["table_data_sha256"], SUMMARY["questions_file"]["sha256"])
    expected = td.render_doc(SLOTS, TEMPLATES, SAMPLE, SUMMARY, REPRO, hashes)
    assert td.DOC_PATH.read_text(encoding="utf-8") == expected


def _allow_missing() -> bool:
    return os.environ.get("CLIMRR_ALLOW_MISSING_RAW") == "1"


def test_full_questions_file_matches_pin_and_invariants():
    if not td.QUESTIONS_PATH.is_file():
        if _allow_missing():
            pytest.skip("questions_v1.jsonl absent and CLIMRR_ALLOW_MISSING_RAW=1 is set")
        pytest.fail("artifacts/templates/questions_v1.jsonl is absent (gitignored); regenerate with "
                    "scripts/generate_template_questions.py, or set CLIMRR_ALLOW_MISSING_RAW=1 for code-only work")
    pin = SUMMARY["questions_file"]
    assert td.file_sha256(td.QUESTIONS_PATH) == pin["sha256"]
    records = td.read_jsonl(td.QUESTIONS_PATH)
    assert len(records) == pin["n_records"]
    _check_invariants(records)
    assert td.summarise(records, TEMPLATES) == {k: v for k, v in SUMMARY.items() if k != "questions_file"}
    sample_ids = {r["question_id"] for r in SAMPLE}
    assert [r for r in records if r["question_id"] in sample_ids] == SAMPLE
    match = next(r for r in records if r["question_id"] == next(
        e["question_id"] for e in REPRO["prototypes"] if e["record_id"] == "P-STATE-1"))
    assert match["answer"] == "13.209951652865228"
