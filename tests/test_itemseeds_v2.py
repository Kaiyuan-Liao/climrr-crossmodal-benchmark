"""Item seeds v2 (DR-SEED-1 v2; D-046--D-048; pilot P2b-prep): synthetic pairing cases and the frozen summary."""

from __future__ import annotations

import json

from climrr import itemseeds as sd
from climrr import itemseeds_v2 as s2
from climrr import litgeo as lg

NCA = sd.nca_map()
GZ = lg.Gazetteer(NCA)


def _row(sid, stype, region, scope, strength="background_only", role="background_consensus_candidate", direction="unspecified",
         scenario="unknown", paper="9"):
    return {"statement_id": sid, "arm": "extreme_heat_v1", "statement_type": stype, "evidence_role": role,
            "role": s2.ROLE_SHORT[role], "paper_item_id": paper, "canonical_paper": paper, "direction": direction,
            "statement": f"statement {sid}", "region": region, "region_scope": scope, "scenario": scenario, "passage_type": "background",
            "geo": lg.classify(region, scope, GZ), "cluster_id": f"LC-{sid}", "cluster_strength": strength}


def _pattern(pid="TP1-00001", state="Texas", blocked=False, status="computed", kind="single"):
    return {"pattern_id": pid, "pattern_kind": kind, "family": "heat_index", "geography_type": "state", "geography": state,
            "metric": "heatindex_days_above_95F", "season": "summer", "horizon": "mid", "horizon_window": "2045-2054",
            "scenario": "RCP8.5", "statistic": "absolute_change", "direction": "increase", "status": status,
            "acceptance_blocked": blocked, "acceptance_blocked_by": [], "provisional_reasons": [], "relative_magnitude": None,
            "computed_value_or_range": {"value": "1.0", "unit": "days"}}


def _seeds(rows, patterns):
    return s2.build(patterns, rows, [], NCA, {"papers": []})


def test_a_background_mechanism_statement_of_any_strength_makes_a_seed_eligible():
    [s] = _seeds([_row("A", "mechanism", "Texas", "subnational")], [_pattern()])
    assert s["eligible_for_pilot"] and s["best_explaining_strength"] == "background_only"
    assert s["n_relevant_by_basis"]["state"] == 1 and s["use_case_levels_applicable"] == [3, 1]


def test_a_non_us_national_scope_no_longer_makes_a_statement_relevant():
    [s] = _seeds([_row("A", "driver", "Malaysia", "national"), _row("B", "caveat", "Texas", "subnational")], [_pattern()])
    assert not s["eligible_for_pilot"] and s["n_relevant_statements"] == 1       # only the caveat, which does not explain


def test_global_and_us_statements_are_relevant_everywhere_but_other_states_are_not():
    rows = [_row("A", "driver", "unknown", "global"), _row("B", "driver", "United States", "national"),
            _row("C", "driver", "California", "subnational")]
    [s] = _seeds(rows, [_pattern(state="Texas")])
    assert s["relevant_statement_ids"] == ["B", "A"]                              # us_national before global; California dropped


def test_direction_pairing_is_kept():
    [s] = _seeds([_row("A", "driver", "Texas", "subnational", direction="decrease")], [_pattern()])
    assert not s["eligible_for_pilot"]


def test_blocked_or_not_computable_patterns_are_not_eligible():
    rows = [_row("A", "driver", "Texas", "subnational")]
    blocked, nc = _seeds(rows, [_pattern("TP1-00001", blocked=True), _pattern("TP1-00002", status="not_computable")])
    assert not blocked["eligible_for_pilot"] and not nc["eligible_for_pilot"]


def test_strength_ranks_and_scenario_caveats_give_level_7():
    rows = [_row("A", "driver", "Texas", "subnational"),
            _row("B", "driver", "United States", "national", strength="multi_source_supported", role="core_candidate"),
            _row("C", "caveat", "Texas", "subnational", scenario="RCP8.5")]
    a, b = _seeds(rows, [_pattern("TP1-00001", "Texas"), _pattern("TP1-00002", "Ohio")])
    assert a["relevant_statements"][0]["statement_id"] == "B" and a["best_explaining_strength"] == "multi_source_supported"
    assert a["use_case_levels_applicable"] == [3, 7, 1] and b["use_case_levels_applicable"] == [3, 1]
    assert a["seed_rank_key"] == 1                                                # same strength; more named-place statements


def test_the_frozen_summary():
    s = json.loads(s2.SUMMARY_PATH.read_text(encoding="utf-8"))
    assert (s["rule"], s["decisions"], s["seeds"], s["eligible"], s["eligible_v1"]) == ("DR-SEED-1 v2", ["D-046", "D-047", "D-048"], 2812, 2368, 1316)
    assert s["eligible_by_family"] == {"fire_weather_index": 1052, "heat_index": 1316}
    assert s["eligible_heat_index_by_level"] == {"3": 1300, "4": 16}
    assert s["fwi"] == {"seeds": 1404, "acceptance_blocked": 352, "eligible": 1052}
    g = s["statement_geography"]
    assert (g["entering_statements"], g["named_state_or_nca_region"], g["relevant_to_at_least_one_pattern"]) == (747, 124, 312)
    assert g["us_gazetteer_string_but_subnational_or_local"] == 50
