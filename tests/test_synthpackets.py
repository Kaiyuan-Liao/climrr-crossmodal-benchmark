"""Seed packets for the synthesis agent (pilot P2b-prep; v3 P2b-final-prep): rendering, allowed numbers, group selection
(DR-SEED-RANK-3, the rung-7 caveat filter, the D-053 dispositions), pattern descriptors (DR-DESC-1)."""

from __future__ import annotations

import copy
import json
from decimal import Decimal

import pytest

from climrr import itemseeds as sd
from climrr import litgroups as lgr
from climrr import pattern_descriptors as pd
from climrr import synthpackets as spk
from climrr import table_patterns as tp
from climrr.checksums import sha256_file
from climrr.manifest import MANIFEST_PATH, load_entry

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
    assert [g["group_id"] for g in pg] == ["LG-a-driver-001"]
    assert ex == [{"group_id": "LG-a-caveat-002", "statement_type": "caveat", "claim_about": "method_or_data",
                   "reason": "caveat_claim_about:method_or_data"}]                                   # v3: caveats filtered by claim
    assert [m["statement_id"] for m in pg[0]["members"]] == ["A", "B"] and pg[0]["strength_in_packet"] == "multi_source_supported"
    assert spk.packet_groups(1, groups, by, basis) == ([], [])


def test_dr_seed_rank_3_roles_exclusions_and_order():
    groups = [_g("LG-d-01", "driver", ["A"], "hazard_change_mechanism"),
              _g("LG-d-02", "mechanism", ["B"], "hazard_change_mechanism"),
              _g("LG-d-03", "driver", ["C"], "hazard_definition_or_measurement"),
              _g("LG-d-04", "driver", ["D"], "impact_or_exposure"),
              _g("LG-d-05", "consensus", ["E"], "method_or_data"),
              _g("LG-d-06", "driver", ["F"], "other"),
              _g("LG-d-07", "driver", ["G"], "not_a_value"),
              _g("LG-d-08", "driver", ["H", "I"], "hazard_change_mechanism", "group", "multi_source_supported"),
              _g("LG-d-09", "driver", ["K"], "hazard_change_mechanism"),
              _g("LG-c-01", "caveat", ["J"], "hazard_change_mechanism")]
    by = {k: _rec(k, str(n)) for n, k in enumerate("ABCDEFGHIJK", 1)}
    basis = {"A": "us_national", "B": "us_subregion", "C": "global", "D": "state", "E": "state", "F": "state", "G": "state",
             "H": "global", "I": "global", "J": "state", "K": "nca_region"}
    pg, ex = spk.packet_groups(3, groups, by, basis)
    # place-named first (even single-source), then strength (multi over single), then relevance class, papers, id
    assert [(g["group_id"], g["role"]) for g in pg] == [("LG-d-09", "driver"), ("LG-d-08", "driver"), ("LG-d-02", "driver"),
                                                       ("LG-d-01", "driver"), ("LG-d-03", "context")]
    assert {(x["group_id"], x["reason"]) for x in ex} == {
        ("LG-d-04", "claim_about:impact_or_exposure"), ("LG-d-05", "claim_about:method_or_data"), ("LG-d-06", "claim_about:other"),
        ("LG-d-07", "claim_about:not_a_value"), ("LG-c-01", "caveat_outside_rung_7")}
    pg7, ex7 = spk.packet_groups(7, groups, by, basis)
    assert [g["group_id"] for g in pg7][-1] == "LG-c-01" and "LG-c-01" not in {x["group_id"] for x in ex7}
    geo = {"B": {"class": "us_subregion", "qualifier": "southeastern"}}
    pgq, _ = spk.packet_groups(3, groups, by, basis, geo)
    assert pgq[2]["members"][0]["region_qualifier"] == "southeastern"                        # the qualifier is carried
    assert spk._model_group(pgq[2])["members"][0]["region_qualifier"] == "southeastern"
    assert "region_qualifier" not in spk._model_group(pgq[0])["members"][0]


def test_dispositions_exclude_relabel_and_keep_caveats_out_of_rung_7():
    groups = [_g("LG-d-01", "driver", ["A"], "hazard_change_mechanism"),
              _g("LG-d-02", "driver", ["B"], "hazard_change_mechanism"),
              _g("LG-d-03", "driver", ["C"], "impact_or_exposure"),
              _g("LG-c-01", "caveat", ["D"], "hazard_change_mechanism"),
              _g("LG-c-02", "caveat", ["E"], "hazard_definition_or_measurement")]
    for g in groups:
        g["arm"] = "extreme_heat_v1"
    disp = {"LG-d-01": {"disposition": "not_about_family", "kind": "not_about_family", "arg": None},
            "LG-d-02": {"disposition": "reject", "kind": "reject", "arg": None},
            "LG-d-03": {"disposition": "relabel:hazard_change_mechanism", "kind": "relabel", "arg": "hazard_change_mechanism"},
            "LG-c-01": {"disposition": "exclude_from_rung7", "kind": "exclude_from_rung7", "arg": None}}
    applied = lgr.apply_dispositions(groups, disp)
    assert groups[2]["claim_about"] == "impact_or_exposure"                                  # the input is not changed
    by = {k: _rec(k, str(n)) for n, k in enumerate("ABCDE", 1)}
    basis = {k: "us_national" for k in by}
    pg, ex = spk.packet_groups(7, applied, by, basis)
    assert [(g["group_id"], g["role"], g["claim_about_source"]) for g in pg] == [
        ("LG-d-03", "driver", "reviewer"), ("LG-c-02", "caveat", "agent")]
    assert {(x["group_id"], x["reason"]) for x in ex} == {
        ("LG-d-01", "disposition:not_about_family"), ("LG-d-02", "disposition:reject"), ("LG-c-01", "disposition:exclude_from_rung7")}


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
    assert pk["model_view"]["groups"][0]["role"] == "driver" and pk["excluded_groups"] == [] and pk["rank_rule"] == "DR-SEED-RANK-3"
    d = pk["model_view"]["patterns"][0]["allowed_descriptors"]
    assert d["magnitude_class"] == "roughly doubling" and d["anchor_pair"] == "from about 20 to about 48 days"
    assert pk["checks_input"]["allowed_descriptors"] == pd.phrases(d) and {"20", "48"} <= set(pk["checks_input"]["allowed_numbers"])
    assert "19.7" in pk["checks_input"]["exact_values"] and "48.464632388875803" in pk["checks_input"]["exact_values"]
    assert all("." in x for x in pk["checks_input"]["exact_values"]) and pk["descriptor_rule"] == "DR-DESC-1"


# --- descriptors (DR-DESC-1) ----------------------------------------------------------------------------


RULES = pd.load_rules()


def test_the_descriptor_rules_are_pinned_in_the_manifest():
    entry = load_entry("descriptor_rules_v1.yaml", MANIFEST_PATH)
    assert entry["path"] == "data/metadata/benchmark/descriptor_rules_v1.yaml" and entry["decision_ref"] == "D-055"
    assert sha256_file(pd.RULES_PATH) == entry["sha256"] == RULES["sha256"] and RULES["rule"] == "DR-DESC-1"


@pytest.mark.parametrize("ratio,want", [("1.0", "a slight increase"), ("1.2499", "a slight increase"),
                                        ("1.25", "a moderate increase (about half again as many)"), ("1.75", "roughly doubling"),
                                        ("2.4999", "roughly doubling"), ("2.5", "roughly tripling"), ("3.5", "roughly tripling"),
                                        ("3.5001", "more than tripling"), ("40", "more than tripling")])
def test_magnitude_class_thresholds(ratio, want):
    assert pd.magnitude_class(Decimal(ratio), "increase", RULES) == want


def test_no_magnitude_class_for_a_decrease():
    assert pd.magnitude_class(Decimal("0.5"), "decrease", RULES) is None


def _single(mf, mt, direction="increase", rm=None, horizon="mid", window="2045-2054"):
    p = copy.deepcopy(EX["TP1-00009"])
    p.update(direction=direction, horizon=horizon, horizon_window=window, relative_magnitude=rm,
             computed_value_or_range=dict(p["computed_value_or_range"], mean_from=mf, mean_to=mt))
    return p


def test_descriptors_of_a_single_place_pattern():
    d = pd.descriptors(_single("15.783252490397672", "44.933818281416101"), RULES)
    assert d["direction"] == "increase" and d["magnitude_class"] == "roughly tripling"
    assert d["anchor_pair"] == "from about 16 to about 45 days" and d["anchors"] == ["about 16 days", "about 45 days"]
    assert d["horizon"] == "by mid-century (2045–2054)" and d["scenario"] == "under RCP8.5, one high-emissions scenario"
    assert d["quantity"] == "days with a dangerous heat index (above 95 °F)" and d["tercile"] is None
    e = pd.descriptors(_single("0.2027", "11.19", horizon="end", window="2085-2094",
                               rm={"class": "small", "definition": "small = lower tercile"}), RULES)
    assert e["magnitude_class"] == "from rare or no such days to about 11 days" and e["horizon"] == "by the end of the century (2085–2094)"
    assert e["tercile"].startswith("small relative to other U.S. states (lower tercile;") and "not an absolute threshold" in e["tercile"]
    assert pd.descriptors(_single("0.04", "0.82"), RULES)["anchors"] == ["about 0 days", "about 1 day"]


def test_descriptors_of_a_regional_contrast():
    p = copy.deepcopy(EX["TP1-00009"])
    p.update(pattern_kind="regional_contrast", computed_value_or_range={"value": None, "regions_ordered": [
        {"name": "Southeast", "rank": 1, "value": "26.97"}, {"name": "Alaska", "rank": 2, "value": "0.0085"},
        {"name": "Northwest", "rank": None, "value": None, "reason": "zero_baseline"}]})
    d = pd.descriptors(p, RULES)
    assert d["ranking_largest_first"] == ["Southeast", "Alaska"] and d["not_ranked"] == ["Northwest"]
    assert d["largest"] == "the largest increase: Southeast" and d["smallest"] == "the smallest increase: Alaska"
    assert d["magnitude_class"] is None and d["anchor_pair"] is None and "regional contrast" in d["magnitude_note"]
    assert "Southeast" in pd.phrases(d) and "the smallest increase: Alaska" in pd.phrases(d)


# --- dispositions (D-053) --------------------------------------------------------------------------------


def test_the_dispositions_are_pinned_and_read_as_proposed():
    entry = load_entry("group_dispositions_v1.csv", MANIFEST_PATH)
    assert entry["decision_ref"] == "D-053" and sha256_file(lgr.DISPOSITIONS_PATH) == entry["sha256"]
    assert entry["sha256"] == "71f0777727be7beba483cd00cb33c6677ed86c0213ecc26cc081940273d40b82"
    disp = lgr.load_dispositions()
    assert len(disp) == 107 and all(d["source"] == "proposed" for d in disp.values())
    assert lgr.disposition_counts(disp) == {
        "accept": 44, "exclude_from_rung7": 40, "merge_with:LG-extreme_heat_v1-mechanism-c1-021": 2, "not_about_family": 11,
        "reject": 3, "relabel:hazard_change_mechanism": 1, "relabel:hazard_definition_or_measurement": 1,
        "relabel:impact_or_exposure": 3, "relabel:method_or_data": 2}


def test_parse_disposition():
    assert lgr.parse_disposition("accept") == ("accept", None)
    assert lgr.parse_disposition("relabel:other") == ("relabel", "other")
    assert lgr.parse_disposition("merge_with:LG-x-001") == ("merge_with", "LG-x-001")
    for bad in ("relabel:pattern", "merge_with", "accept:x", "keep"):
        with pytest.raises(ValueError):
            lgr.parse_disposition(bad)


def test_kaiyuan_overrides_the_proposal(tmp_path):
    src = tmp_path / "d.csv"
    src.write_text("group_id,proposed_disposition,reason,kaiyuan_disposition,kaiyuan_note\r\n"
                   "LG-a,accept,ok,reject,not heat\r\nLG-b,reject,off,,\r\n", encoding="utf-8")
    man = tmp_path / "manifest.json"
    man.write_text(json.dumps({"files": [{"filename": "d.csv", "sha256": sha256_file(src)}]}), encoding="utf-8")
    d = lgr.load_dispositions(src, man)
    assert d["LG-a"] == {"disposition": "reject", "kind": "reject", "arg": None, "source": "kaiyuan", "reason": "not heat"}
    assert d["LG-b"]["source"] == "proposed"
    man.write_text(json.dumps({"files": [{"filename": "d.csv", "sha256": "0" * 64}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="differs from its manifest pin"):
        lgr.load_dispositions(src, man)


def _gm(gid, members, strength="single_source_supported"):
    return {"group_id": gid, "arm": "extreme_heat_v1", "kind": "group", "statement_type": "mechanism", "label": gid,
            "claim_about": "hazard_definition_or_measurement", "evidence_strength": strength, "n_members": len(members),
            "member_ids": [m["statement_id"] for m in members], "members": members}


def _mm(sid, paper, role="core_candidate"):
    return {"statement_id": sid, "paper_item_id": paper, "canonical_paper": paper, "evidence_role": role, "passage_type": "own_finding"}


def test_a_merge_unions_members_and_recomputes_strength():
    groups = [_gm("LG-t", [_mm("A", "1"), _mm("B", "1", "background_consensus_candidate")]),
              _gm("LG-s", [_mm("B", "1", "background_consensus_candidate"), _mm("C", "2")])]
    out = lgr.apply_dispositions(groups, {"LG-s": {"disposition": "merge_with:LG-t", "kind": "merge_with", "arg": "LG-t"}})
    t, s_ = out
    assert t["member_ids"] == ["A", "B", "C"] and t["merged_from"] == ["LG-s"] and t["n_members"] == 3
    assert t["evidence_strength"] == "multi_source_supported" and t["evidence_strength_before_merge"] == "single_source_supported"
    assert t["n_independent_core_cited_papers"] == 2 and s_["disposition_exclude"] == "merged_into:LG-t"
    assert groups[0]["member_ids"] == ["A", "B"]
    with pytest.raises(ValueError, match="not in the grouping output"):
        lgr.apply_dispositions(groups, {"LG-x": {"disposition": "accept", "kind": "accept", "arg": None}})
    with pytest.raises(ValueError, match="itself excluded or merged"):
        lgr.apply_dispositions(groups, {"LG-s": {"disposition": "merge_with:LG-t", "kind": "merge_with", "arg": "LG-t"},
                                        "LG-t": {"disposition": "reject", "kind": "reject", "arg": None}})
