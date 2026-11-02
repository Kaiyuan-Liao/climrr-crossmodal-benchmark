"""Seed packets for the synthesis agent (pilot P2b-prep): rendering, allowed numbers, group selection."""

from __future__ import annotations

import copy
import json

from climrr import itemseeds as sd
from climrr import synthpackets as spk
from climrr import table_patterns as tp

NCA = sd.nca_map()
EX = {p["pattern_id"]: p for p in tp.read_jsonl(tp.EXAMPLES_PATH)}


def test_numbers_are_shown_to_one_decimal_half_up_and_allowed_in_three_forms():
    assert spk.show("29.249999") == "29.2" and spk.show("0.05") == "0.1" and spk.show("-2.25") == "-2.3"
    assert spk.number_forms("146.382940622041848") == {"146.382940622041848", "146.4", "146"}
    assert spk.number_forms(None) == set()


def test_a_state_pattern_renders_in_plain_words_without_columns():
    p = EX["TP1-00009"]
    text, shown, allowed = spk.render_pattern(p, NCA)
    assert text.startswith("Pattern TP1-00009 (single place). Place: the U.S. state of Alabama (NCA5 region: Southeast).")
    assert "above 95 °F" in text and "RCP8.5 (one high-emissions scenario; not a forecast" in text and "modeled historical baseline" in text
    assert "heatindex_" not in text and "DR-" not in text and "sha256" not in text
    assert {"95", "2045", "2054", shown["mean_from"], shown["mean_to"]} <= allowed


def test_a_percent_pattern_labels_its_cell_range_in_days():
    p = copy.deepcopy(EX["TP1-00009"])
    p.update(statistic="percent_change", computed_value_or_range=dict(p["computed_value_or_range"], unit="percent", value="146.38"))
    text, shown, _ = spk.render_pattern(p, NCA)
    assert "Value: +146.4%." in text
    assert "Range of the change per grid cell: 11.1 to 43.5 days." in text


def _member(sid, paper, role="core_candidate", pt="own_finding", basis="state", scenario="unknown"):
    return {"statement_id": sid, "statement": "Humidity raises the heat index.", "paper_item_id": paper, "canonical_paper": paper, "paper_sha256": paper[0] * 64,
            "json_path": "$.results", "span_start": 0, "span_end": 3, "verbatim_passage": "abc", "evidence_role": role,
            "passage_type": pt, "region": "Texas", "scenario": scenario, "basis": basis}


def _rec(sid, paper, role="core_candidate", scen="unknown", pt="own_finding"):
    return {"statement_id": sid, "paper_item_id": paper, "canonical_paper": paper, "paper_sha256": paper[0] * 64, "evidence": {},
            "verbatim_passage": "abc", "evidence_role": role, "proposal": {"statement": sid, "passage_type": pt, "region": "Texas"},
            "scenario": {"value": scen}}


def _g(gid, stype, members, claim, kind="singleton", strength="single_source_supported"):
    return {"group_id": gid, "kind": kind, "statement_type": stype, "label": "x" if kind == "group" else None,
            "evidence_strength": strength, "n_members": len(members), "member_ids": members, "claim_about": claim}


def test_packet_groups_drop_pattern_types_background_only_and_irrelevant_members():
    groups = [_g("LG-a-driver-001", "driver", ["A", "B", "Z"], "hazard_change_mechanism", "group", "multi_source_supported"),
              _g("LG-a-pattern-001", "pattern", ["C"], "hazard_change_mechanism"),
              _g("LG-a-caveat-001", "caveat", ["D"], "other", strength="background_only"),
              _g("LG-a-caveat-002", "caveat", ["E"], "method_or_data")]
    by = {"A": _rec("A", "1"), "B": _rec("B", "2"), "Z": _rec("Z", "3"), "C": _rec("C", "4"),
          "D": _rec("D", "5", "background_consensus_candidate"), "E": _rec("E", "6", scen="RCP8.5")}
    basis = {"A": "state", "B": "us_national", "C": "state", "D": "state", "E": "global"}     # Z is not relevant
    pg, ex = spk.packet_groups(7, groups, by, basis)
    assert [g["group_id"] for g in pg] == ["LG-a-driver-001", "LG-a-caveat-002"] and ex == []
    assert [m["statement_id"] for m in pg[0]["members"]] == ["A", "B"] and pg[0]["strength_in_packet"] == "multi_source_supported"
    assert [g["role"] for g in pg] == ["driver", "caveat"] and pg[1]["claim_about"] == "method_or_data"   # caveats: not filtered by claim
    assert pg[1]["names_scenario"] and spk.packet_groups(1, groups, by, basis) == ([], [])


def test_dr_seed_rank_2_roles_exclusions_and_order():
    groups = [_g("LG-d-01", "driver", ["A"], "hazard_change_mechanism"),
              _g("LG-d-02", "mechanism", ["B"], "hazard_change_mechanism"),
              _g("LG-d-03", "driver", ["C"], "hazard_definition_or_measurement"),
              _g("LG-d-04", "driver", ["D"], "impact_or_exposure"),
              _g("LG-d-05", "consensus", ["E"], "method_or_data"),
              _g("LG-d-06", "driver", ["F"], "other"),
              _g("LG-d-07", "driver", ["G"], "not_a_value"),
              _g("LG-d-08", "driver", ["H", "I"], "hazard_change_mechanism", "group", "multi_source_supported"),
              _g("LG-c-01", "caveat", ["J"], "other")]
    by = {k: _rec(k, str(n)) for n, k in enumerate("ABCDEFGHIJ", 1)}
    basis = {"A": "us_national", "B": "us_subregion", "C": "global", "D": "state", "E": "state", "F": "state", "G": "state",
             "H": "global", "I": "global", "J": "state"}
    pg, ex = spk.packet_groups(3, groups, by, basis)
    # relevance class first: us_subregion > us_national > global, even over a multi-source group
    assert [(g["group_id"], g["role"]) for g in pg] == [("LG-d-02", "driver"), ("LG-d-01", "driver"), ("LG-d-08", "driver"),
                                                       ("LG-d-03", "context")]
    assert {(x["group_id"], x["reason"]) for x in ex} == {
        ("LG-d-04", "claim_about:impact_or_exposure"), ("LG-d-05", "claim_about:method_or_data"), ("LG-d-06", "claim_about:other"),
        ("LG-d-07", "claim_about:not_a_value"), ("LG-c-01", "caveat_outside_rung_7")}
    pg7, ex7 = spk.packet_groups(7, groups, by, basis)
    assert [g["group_id"] for g in pg7][-1] == "LG-c-01" and "LG-c-01" not in {x["group_id"] for x in ex7}
    geo = {"B": {"class": "us_subregion", "qualifier": "southeastern"}}
    pgq, _ = spk.packet_groups(3, groups, by, basis, geo)
    assert pgq[0]["members"][0]["region_qualifier"] == "southeastern"                        # the qualifier is carried
    assert spk._model_group(pgq[0])["members"][0]["region_qualifier"] == "southeastern"
    assert "region_qualifier" not in spk._model_group(pgq[1])["members"][0]


def test_dr_seed_rank_2_caps_record_the_overflow():
    groups = [_g(f"LG-d-{i:02d}", "driver", [f"S{i}"], "hazard_change_mechanism") for i in range(12)] + \
             [_g(f"LG-x-{i:02d}", "driver", [f"T{i}"], "hazard_definition_or_measurement") for i in range(5)]
    by = {**{f"S{i}": _rec(f"S{i}", str(100 + i)) for i in range(12)}, **{f"T{i}": _rec(f"T{i}", str(200 + i)) for i in range(5)}}
    basis = {k: "us_national" for k in by}
    pg, ex = spk.packet_groups(4, groups, by, basis)
    assert [g["role"] for g in pg].count("driver") == 10 and [g["role"] for g in pg].count("context") == 4
    assert [x["group_id"] for x in ex] == ["LG-d-10", "LG-d-11", "LG-x-04"] and ex[0]["reason"] == "over_cap:driver"


def test_relevance_in_packets_uses_the_v2_geography_and_the_seed_pairing():
    from climrr import litgeo as lg
    gz2 = lg.Gazetteer(NCA)
    p = EX["TP1-00009"]
    row = lambda sid, region, scope, direction="unspecified", arm="extreme_heat_v1": {  # noqa: E731
        "statement_id": sid, "arm": arm, "direction": direction, "geo": lg.classify(region, scope, gz2)}
    rows = [row("A", "southeastern United States", "subnational"), row("B", "Alabama", "subnational"),
            row("C", "United States", "subnational"), row("D", "Canada", "national"),
            row("E", "United States", "national", direction="decrease"), row("F", "United States", "national", arm="fire_weather_v1")]
    assert spk.relevant_basis(p, rows, NCA) == {"A": "us_subregion", "B": "state", "C": "us_national"}


def test_the_model_view_carries_no_provenance():
    g = {"group_id": "LG-a-driver-001", "kind": "group", "statement_type": "driver", "label": "Humidity raises the heat index.",
         "role": "driver", "claim_about": "hazard_change_mechanism",
         "group_strength_run": "single_source_supported", "strength_in_packet": "single_source_supported", "n_members_run": 1,
         "names_scenario": False, "n_specific": 1, "members": [_member("LS-7001-01", "7001")]}
    pk = spk.assemble_packet("SD2-TP1-00009", EX["TP1-00009"], 3, "BI-P2B-0001", [g], NCA, {})
    view = json.dumps(pk["model_view"])
    assert "paper_sha256" not in view and "span_start" not in view and "heatindex_HIS" not in view and "LS-7001-01" not in view
    assert pk["model_view"]["groups"][0]["members"][0]["paper_id"] == "7001"
    assert pk["checks_input"]["forbidden_strings"] == ["heatindex_HIS_Day95", "heatindex_M85_Day95", "7001"]
    assert pk["provenance"]["item_frame"] == {"use_case_level": 3, "reasoning_modalities": "Hazard + Text", "level_name": "Pattern + mechanism"}
    assert pk["model_view"]["groups"][0]["role"] == "driver" and pk["excluded_groups"] == [] and pk["rank_rule"] == "DR-SEED-RANK-2"
