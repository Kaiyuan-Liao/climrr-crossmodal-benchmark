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


def test_packet_groups_drop_pattern_types_background_only_and_irrelevant_members():
    groups = [{"group_id": "LG-a-driver-001", "kind": "group", "statement_type": "driver", "label": "x", "evidence_strength": "multi_source_supported",
               "n_members": 3, "member_ids": ["A", "B", "Z"]},
              {"group_id": "LG-a-pattern-001", "kind": "singleton", "statement_type": "pattern", "label": None, "evidence_strength": "single_source_supported",
               "n_members": 1, "member_ids": ["C"]},
              {"group_id": "LG-a-caveat-001", "kind": "singleton", "statement_type": "caveat", "label": None, "evidence_strength": "background_only",
               "n_members": 1, "member_ids": ["D"]},
              {"group_id": "LG-a-caveat-002", "kind": "singleton", "statement_type": "caveat", "label": None, "evidence_strength": "single_source_supported",
               "n_members": 1, "member_ids": ["E"]}]
    rec = lambda sid, paper, role="core_candidate", scen="unknown": {  # noqa: E731
        "statement_id": sid, "paper_item_id": paper, "canonical_paper": paper, "paper_sha256": paper[0] * 64, "evidence": {},
        "verbatim_passage": "abc", "evidence_role": role, "proposal": {"statement": sid, "passage_type": "own_finding", "region": "Texas"},
        "scenario": {"value": scen}}
    by = {"A": rec("A", "1"), "B": rec("B", "2"), "Z": rec("Z", "3"), "C": rec("C", "4"),
          "D": rec("D", "5", "background_consensus_candidate"), "E": rec("E", "6", scen="RCP8.5")}
    basis = {"A": "state", "B": "us_national", "C": "state", "D": "state", "E": "global"}     # Z is not relevant
    pg = spk.packet_groups(3, groups, by, basis)
    assert [g["group_id"] for g in pg] == ["LG-a-driver-001", "LG-a-caveat-002"]
    assert [m["statement_id"] for m in pg[0]["members"]] == ["A", "B"] and pg[0]["strength_in_packet"] == "multi_source_supported"
    assert pg[1]["names_scenario"] and spk.packet_groups(1, groups, by, basis) == []


def test_the_model_view_carries_no_provenance():
    g = {"group_id": "LG-a-driver-001", "kind": "group", "statement_type": "driver", "label": "Humidity raises the heat index.",
         "group_strength_run": "single_source_supported", "strength_in_packet": "single_source_supported", "n_members_run": 1,
         "names_scenario": False, "n_specific": 1, "members": [_member("LS-7001-01", "7001")]}
    pk = spk.assemble_packet("SD2-TP1-00009", EX["TP1-00009"], 3, "BI-P2B-0001", [g], NCA, {})
    view = json.dumps(pk["model_view"])
    assert "paper_sha256" not in view and "span_start" not in view and "heatindex_HIS" not in view and "LS-7001-01" not in view
    assert pk["model_view"]["groups"][0]["members"][0]["paper_id"] == "7001"
    assert pk["checks_input"]["forbidden_strings"] == ["heatindex_HIS_Day95", "heatindex_M85_Day95", "7001"]
    assert pk["provenance"]["item_frame"] == {"use_case_level": 3, "reasoning_modalities": "Hazard + Text", "level_name": "Pattern + mechanism"}
