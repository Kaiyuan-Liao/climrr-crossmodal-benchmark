"""The prototype phenomenon schema: provenance, arithmetic and the label guard.

These tests exist because the prototypes make claims the M1-WP3 examples were
forbidden to make --- a county, a mean, a magnitude --- and the only thing
keeping those claims honest is that every derived field carries the weakest
status of its inputs and that the generated prose shows a weak value only inside
a label. Both are pinned here in both directions.

Nothing here reads the real table.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from climrr.dictionary import INFERRED_CANDIDATE, VERIFIED_FROM_DICTIONARY
from climrr.examples import FROM_DICTIONARY, FROM_INFERENCE, FROM_NOWHERE
from climrr.phenomenon import (
    ASSUMPTIONS,
    DERIVED_FROM_INFERRED,
    DERIVED_FROM_VERIFIED,
    DERIVED_DECIMAL_PLACES,
    IC_ASSUMPTIONS,
    LEVELS,
    PROVISIONAL_RULE,
    UNKNOWN,
    PhenomenonError,
    apply_pr1,
    assumption,
    assumptions_for,
    build_record,
    columns_used,
    derived_status,
    direction_of,
    distribution_summary,
    dstr,
    mean_from_total,
    quantise_derived,
    role_of,
    tercile_of,
    unlabelled_inferred_text,
    unweighted_mean,
    variable_of,
    weakest,
)

FWI = variable_of("fwi_summer_hist_to_end85")
HEAT = variable_of("heatindex_day105_summer_hist_to_end85")

#: The two fire-weather value columns are `inferred_candidate`; the
#: percent-change column beside them is verified. That asymmetry is the whole
#: point of the FWI prototypes and these fixtures reproduce it exactly.
FWI_SEMANTICS = {
    189: ("wildfire_summer_Hist", INFERRED_CANDIDATE, FROM_INFERENCE),
    191: ("wildfire_summer_Endc", INFERRED_CANDIDATE, FROM_INFERENCE),
    193: ("wildfire_summer_Dend", INFERRED_CANDIDATE, FROM_INFERENCE),
    195: ("wildfire_summer_Pend", VERIFIED_FROM_DICTIONARY, FROM_DICTIONARY),
}

HEAT_SEMANTICS = {
    241: ("heatindex_HIS_Day105", VERIFIED_FROM_DICTIONARY, FROM_DICTIONARY),
    253: ("heatindex_E85_Day105", VERIFIED_FROM_DICTIONARY, FROM_DICTIONARY),
}


def _semantics(spec):
    entries = {}
    for index, (column, status, provenance) in spec.items():
        def attribute(value):
            return {"value": value, "provenance": provenance}

        entries[index] = {
            "index": index,
            "column": column,
            "status": status,
            # Deliberately free of the words that appear in the column names:
            # the guard masks code spans, and a fixture that smuggled "summer"
            # into a meaning would test the cascade rather than the rule.
            "meaning": attribute(f"the quantity held at index {index}"),
            "unit": attribute(f"the unit at index {index}"),
            "scenario": attribute("RCP8.5"),
            "horizon": attribute("End-Century"),
            "season": attribute("summer"),
            "rests_on": {"kind": "test fixture"},
        }
    return entries


def _member(crossmodel, values):
    return {"crossmodel": crossmodel, "values": dict(values)}


def _fwi_member(crossmodel, hist, endc, dend, pend):
    return _member(crossmodel, {189: hist, 191: endc, 193: dend, 195: pend})


def _build(level, identifier, members, variable, spec, distribution=None):
    values = distribution or [Decimal("-1"), Decimal("0"), Decimal("5"), Decimal("99")]
    return build_record(
        record_id=f"T-{level.upper()}",
        level=level,
        identifier=identifier,
        members=members,
        variable=variable,
        semantics_by_index=_semantics(spec),
        sorted_change_values=sorted(values),
        distribution_membership={"n_units": str(len(values))},
        built_from_commit="0" * 40,
        csv_sha256="f" * 64,
        assumption_ids=["A1", "A-G0"],
    )


# --- provenance ---------------------------------------------------------------


def test_weakest_returns_the_weakest_input_status():
    assert weakest([VERIFIED_FROM_DICTIONARY, VERIFIED_FROM_DICTIONARY]) == (
        VERIFIED_FROM_DICTIONARY
    )
    assert weakest([VERIFIED_FROM_DICTIONARY, INFERRED_CANDIDATE]) == INFERRED_CANDIDATE
    assert weakest([INFERRED_CANDIDATE, UNKNOWN]) == UNKNOWN


def test_a_derived_field_is_never_stronger_than_its_weakest_input():
    assert derived_status([VERIFIED_FROM_DICTIONARY]) == DERIVED_FROM_VERIFIED
    assert derived_status([VERIFIED_FROM_DICTIONARY, INFERRED_CANDIDATE]) == (
        DERIVED_FROM_INFERRED
    )
    assert derived_status([DERIVED_FROM_INFERRED]) == DERIVED_FROM_INFERRED


def test_an_unrecognised_status_raises_rather_than_being_ranked():
    with pytest.raises(PhenomenonError, match="unknown status"):
        weakest(["probably_fine"])


# --- arithmetic ---------------------------------------------------------------


def test_a_mean_is_rounded_to_the_precision_the_file_stores():
    mean = unweighted_mean([Decimal("1"), Decimal("2")])
    assert str(mean) == "1." + "5" + "0" * (DERIVED_DECIMAL_PLACES - 1)


def test_a_streamed_mean_and_a_recomputed_mean_are_the_same_digits():
    """The property PR-1 depends on: a unit must rank consistently against itself."""
    values = [Decimal("25.080200200000000"), Decimal("31.189300540000001"), Decimal("0.5")]
    streamed = mean_from_total(sum(values, Decimal(0)), len(values))
    assert streamed == unweighted_mean(values)


def test_quantise_derived_rounds_half_to_even_and_never_prints_an_exponent():
    assert dstr(quantise_derived(Decimal("0." + "0" * 15 + "5"))) == "0." + "0" * 15
    assert dstr(quantise_derived(Decimal("0." + "0" * 14 + "15"))) == "0." + "0" * 14 + "2"
    # str(Decimal) would give "0E-15" here, which is correct and unreadable.
    assert str(quantise_derived(Decimal("0"))) == "0E-15"


def test_direction_of_reads_only_the_sign():
    assert direction_of(Decimal("0.000000000000001")) == "increase"
    assert direction_of(Decimal("-0.000000000000001")) == "decrease"
    assert direction_of(Decimal("0")) == "no_change"


# --- PR-1 ---------------------------------------------------------------------


def test_tercile_boundaries_fall_where_the_rule_says():
    assert tercile_of(Decimal("0")) == "lower_third"
    assert tercile_of(Decimal("33.3")) == "lower_third"
    assert tercile_of(Decimal("33.4")) == "middle_third"
    assert tercile_of(Decimal("66.6")) == "middle_third"
    assert tercile_of(Decimal("66.7")) == "upper_third"
    assert tercile_of(Decimal("100")) == "upper_third"


def test_pr1_counts_strictly_below_and_reports_ties_separately():
    values = [Decimal(n) for n in (1, 2, 2, 2, 10)]
    result = apply_pr1(Decimal(2), sorted(values))
    assert result["n_units_at_this_level"] == "5"
    assert result["n_units_strictly_below"] == "1"
    assert result["n_units_equal"] == "3"
    assert result["percentile"] == "20.0000"
    assert result["tercile"] == "lower_third"


def test_pr1_says_in_its_own_text_that_it_is_not_a_threshold():
    result = apply_pr1(Decimal(1), [Decimal(0), Decimal(1)])
    assert result["is_a_scientific_threshold"] == "no"
    assert "placeholder" in result["rule_statement"]
    assert result["provenance_status"] == PROVISIONAL_RULE


def test_pr1_refuses_an_empty_distribution():
    with pytest.raises(PhenomenonError, match="non-empty distribution"):
        apply_pr1(Decimal(1), [])


def test_distribution_summary_uses_nearest_rank():
    values = [Decimal(n) for n in range(1, 11)]
    summary = distribution_summary(values)
    assert (summary["n"], summary["min"], summary["max"]) == ("10", "1", "10")
    assert (summary["q1"], summary["median"], summary["q3"]) == ("3", "5", "8")
    assert "nearest-rank" in summary["quantile_method"]


# --- records ------------------------------------------------------------------


def test_a_cell_record_carries_the_raw_values_and_no_aggregate():
    record = _build(
        "cell",
        {"Crossmodel": "R1C1"},
        [_fwi_member("R1C1", "25.080200200000000", "31.189300540000001", "6.109189990000000", "24.358664999999998")],
        FWI,
        FWI_SEMANTICS,
    )
    assert record["V"]["kind"] == "raw_values_of_one_cell"
    assert record["G"]["n_cells"] == "1"
    assert record["G"]["provenance_status"] == VERIFIED_FROM_DICTIONARY
    assert record["D"]["direction"] == "increase"
    # The change column is inferred, so the direction is derived from an
    # inference even though the cell identifier is verified.
    assert record["D"]["provenance_status"] == DERIVED_FROM_INFERRED
    # The verified percent-change column corroborates and says so.
    assert record["D"]["corroborating"]["provenance_status"] == DERIVED_FROM_VERIFIED
    assert record["D"]["corroborating"]["agrees_with_change_column"] == "True"


def test_a_county_record_lists_every_member_and_aggregates_over_them():
    members = [
        _fwi_member("R1C1", "10.000000000000000", "12.000000000000000", "2.000000000000000", "20.000000000000000"),
        _fwi_member("R1C2", "20.000000000000000", "26.000000000000000", "6.000000000000000", "30.000000000000000"),
    ]
    record = _build(
        "county", {"State": "Oklahoma", "NAME": "Stephens"}, members, FWI, FWI_SEMANTICS
    )
    assert record["G"]["member_cells"] == ["R1C1", "R1C2"]
    assert record["G"]["n_cells"] == record["G"]["n_cells_with_value"] == "2"
    assert record["G"]["provenance_status"] == INFERRED_CANDIDATE
    assert record["V"]["kind"] == "aggregate_over_member_cells"
    change = record["V"]["change"]
    assert change["per_cell_change_values"] == [
        "2." + "0" * DERIVED_DECIMAL_PLACES,
        "6." + "0" * DERIVED_DECIMAL_PLACES,
    ]
    assert change["value"] == "4." + "0" * DERIVED_DECIMAL_PLACES
    baseline = record["V"]["per_column"][0]
    assert baseline["per_cell_raw_values"] == [
        "10." + "0" * DERIVED_DECIMAL_PLACES,
        "20." + "0" * DERIVED_DECIMAL_PLACES,
    ]
    assert baseline["aggregates"]["min"] == "10." + "0" * DERIVED_DECIMAL_PLACES
    assert baseline["aggregates"]["max"] == "20." + "0" * DERIVED_DECIMAL_PLACES
    assert baseline["aggregates"]["count"] == "2"


def test_a_cell_with_a_blank_is_excluded_from_the_mean_and_counted():
    members = [
        _fwi_member("R1C1", "10.000000000000000", "12.000000000000000", "2.000000000000000", "20.000000000000000"),
        _fwi_member("R1C2", "", "", "", ""),
    ]
    record = _build(
        "county", {"State": "Oklahoma", "NAME": "Stephens"}, members, FWI, FWI_SEMANTICS
    )
    assert record["G"]["n_cells"] == "2"
    assert record["G"]["n_cells_with_value"] == "1"
    assert record["G"]["n_cells_empty"] == "1"
    assert record["V"]["n"] == "1"
    assert any(caution["id"] == "C-blank" for caution in record["cautions"])
    assert "not** a zero" in record["description"]


def test_a_heat_index_record_computes_the_change_from_two_verified_columns():
    members = [_member("R1C1", {241: "1.000000000000000", 253: "36.000000000000000"})]
    record = _build("cell", {"Crossmodel": "R1C1"}, members, HEAT, HEAT_SEMANTICS)
    assert record["V"]["change"]["operation"] == "difference_of_horizon_values"
    assert record["D"]["change_value"] == "35." + "0" * DERIVED_DECIMAL_PLACES
    assert record["D"]["provenance_status"] == DERIVED_FROM_VERIFIED
    assert record["D"]["corroborating"] is None


def test_an_empty_unit_is_a_finding_not_an_empty_record():
    with pytest.raises(PhenomenonError, match="no member rows"):
        _build("county", {"State": "X", "NAME": "Y"}, [], FWI, FWI_SEMANTICS)


def test_a_cell_unit_with_two_members_is_refused():
    """`Crossmodel` was measured unique, so two members at cell level is a defect."""
    members = [
        _fwi_member("R1C1", "10.000000000000000", "12.000000000000000", "2.000000000000000", "20.000000000000000"),
        _fwi_member("R1C1", "10.000000000000000", "12.000000000000000", "2.000000000000000", "20.000000000000000"),
    ]
    with pytest.raises(PhenomenonError, match="cell-level unit has 2 members"):
        _build("cell", {"Crossmodel": "R1C1"}, members, FWI, FWI_SEMANTICS)


def test_a_unit_whose_every_member_is_blank_is_a_finding():
    members = [_fwi_member("R1C1", "", "", "", "")]
    with pytest.raises(PhenomenonError, match="no member cell has a value"):
        _build("county", {"State": "X", "NAME": "Y"}, members, FWI, FWI_SEMANTICS)


# --- the generated description ------------------------------------------------


def test_the_description_labels_every_inferred_clause_and_the_guard_agrees():
    record = _build(
        "cell",
        {"Crossmodel": "R1C1"},
        [_fwi_member("R1C1", "25.080200200000000", "31.189300540000001", "6.109189990000000", "24.358664999999998")],
        FWI,
        FWI_SEMANTICS,
    )
    assert unlabelled_inferred_text(record) == []
    assert "[provisional: the quantity held at index 189]" in record["description"]
    assert "[provisional rule PR-1: " in record["description"]


def test_the_guard_catches_a_weak_value_that_escapes_its_label():
    record = _build(
        "cell",
        {"Crossmodel": "R1C1"},
        [_fwi_member("R1C1", "25.080200200000000", "31.189300540000001", "6.109189990000000", "24.358664999999998")],
        FWI,
        FWI_SEMANTICS,
    )
    record["description"] = record["description"].replace(
        "[provisional: the quantity held at index 189]", "the quantity held at index 189"
    )
    offences = unlabelled_inferred_text(record)
    assert [field for field, _text in offences] == ["H.baseline.meaning"]


def test_a_raw_value_is_shown_plainly_and_a_derived_one_is_not():
    """At cell level the change value *is* a raw string, and both must hold."""
    record = _build(
        "cell",
        {"Crossmodel": "R1C1"},
        [_fwi_member("R1C1", "25.080200200000000", "31.189300540000001", "6.109189990000000", "24.358664999999998")],
        FWI,
        FWI_SEMANTICS,
    )
    assert "`wildfire_summer_Dend` 6.109189990000000;" in record["description"]
    assert "[provisional: 6.109189990000000]" in record["description"]
    assert unlabelled_inferred_text(record) == []


def test_a_fire_weather_record_always_carries_the_index_caution():
    record = _build(
        "cell",
        {"Crossmodel": "R1C1"},
        [_fwi_member("R1C1", "25.080200200000000", "31.189300540000001", "6.109189990000000", "24.358664999999998")],
        FWI,
        FWI_SEMANTICS,
    )
    assert any(caution["id"] == "C-fire_weather" for caution in record["cautions"])
    assert "It is not a wildfire" in record["description"]


def test_an_aggregate_record_says_it_groups_rows_by_an_inferred_label():
    """M1-WP3's location caution ends "no part of this pilot groups rows by any of
    them". That sentence was true there and is false here, so it must not be
    carried across unchanged."""
    record = _build(
        "county",
        {"State": "Oklahoma", "NAME": "Stephens"},
        [_fwi_member("R1C1", "10.000000000000000", "12.000000000000000", "2.000000000000000", "20.000000000000000")],
        FWI,
        FWI_SEMANTICS,
    )
    assert any(caution["id"] == "C-location-grouping" for caution in record["cautions"])
    assert "no part of this pilot groups rows" not in record["description"]
    assert "This prototype groups rows by those labels" in record["description"]


def test_a_cell_record_does_not_claim_to_group_anything():
    record = _build(
        "cell",
        {"Crossmodel": "R1C1"},
        [_fwi_member("R1C1", "25.080200200000000", "31.189300540000001", "6.109189990000000", "24.358664999999998")],
        FWI,
        FWI_SEMANTICS,
    )
    assert not any(
        caution["id"] == "C-location-grouping" for caution in record["cautions"]
    )


def test_a_square_bracket_in_a_semantic_value_stops_the_build():
    spec = dict(FWI_SEMANTICS)
    semantics = _semantics(spec)
    semantics[189]["meaning"] = {"value": "a [bracketed] claim", "provenance": FROM_INFERENCE}
    with pytest.raises(PhenomenonError, match="square bracket"):
        build_record(
            record_id="T",
            level="cell",
            identifier={"Crossmodel": "R1C1"},
            members=[_fwi_member("R1C1", "25.080200200000000", "31.189300540000001", "6.109189990000000", "24.358664999999998")],
            variable=FWI,
            semantics_by_index=semantics,
            sorted_change_values=[Decimal(1)],
            distribution_membership={},
            built_from_commit="0" * 40,
            csv_sha256="f" * 64,
            assumption_ids=["A1"],
        )


def test_an_attribute_with_no_value_is_rendered_as_no_value_in_this_file():
    semantics = _semantics(FWI_SEMANTICS)
    semantics[189]["unit"] = {"value": None, "provenance": FROM_NOWHERE}
    record = build_record(
        record_id="T",
        level="cell",
        identifier={"Crossmodel": "R1C1"},
        members=[_fwi_member("R1C1", "25.080200200000000", "31.189300540000001", "6.109189990000000", "24.358664999999998")],
        variable=FWI,
        semantics_by_index=semantics,
        sorted_change_values=[Decimal(1)],
        distribution_membership={},
        built_from_commit="0" * 40,
        csv_sha256="f" * 64,
        assumption_ids=["A1"],
    )
    assert "Unit or type: no value in this file." in record["description"]


# --- the literature probe -----------------------------------------------------


def test_the_probe_states_that_nothing_was_retrieved():
    record = _build(
        "county",
        {"State": "Oklahoma", "NAME": "Stephens"},
        [_fwi_member("R1C1", "10.000000000000000", "12.000000000000000", "2.000000000000000", "20.000000000000000")],
        FWI,
        FWI_SEMANTICS,
    )
    probe = record["literature_probe"]
    assert probe["retrieval_performed"] == "no"
    assert probe["direction_term"] == record["D"]["direction"]
    assert [term["term"] for term in probe["place_terms"]] == ["Oklahoma", "Stephens"]
    assert all(term["status"] == INFERRED_CANDIDATE for term in probe["place_terms"])
    assert probe["query_sentence"].startswith("increase in fire weather index in ")


def test_a_cell_level_probe_records_that_it_has_no_usable_place_term():
    record = _build(
        "cell",
        {"Crossmodel": "R1C1"},
        [_fwi_member("R1C1", "25.080200200000000", "31.189300540000001", "6.109189990000000", "24.358664999999998")],
        FWI,
        FWI_SEMANTICS,
    )
    assert "no usable place term" in record["literature_probe"]["place_terms_note"]


# --- the assumptions register -------------------------------------------------


def test_every_assumption_id_is_unique_and_resolvable():
    ids = [item["id"] for item in ASSUMPTIONS]
    assert len(ids) == len(set(ids))
    for item_id in ids:
        assert assumption(item_id)["id"] == item_id


def test_assumptions_for_adds_the_aggregation_entries_only_above_cell_level():
    cell = assumptions_for(level="cell", variable=FWI, ic_ids=["IC-006"])
    county = assumptions_for(level="county", variable=FWI, ic_ids=["IC-006"])
    assert "A-G1" not in cell and "A-AGG1" not in cell
    assert {"A-G1", "A-G2", "A-G3", "A-AGG1"} <= set(county)
    assert cell[0] == "A1" and cell[-1] == "A-M1"


def test_assumptions_for_maps_each_inferred_candidate_record_to_its_entry():
    ids = assumptions_for(level="cell", variable=FWI, ic_ids=["IC-006", "IC-008", "IC-010"])
    assert {"A-H1", "A-H3", "A-H5"} <= set(ids)


def test_a_variable_with_no_corroborating_column_does_not_claim_one():
    assert "A-DIR2" not in assumptions_for(level="state", variable=HEAT, ic_ids=[])


def test_an_inferred_candidate_with_no_register_entry_stops_the_build():
    """`IC-007` maps to `A-H2`, which no record uses and the register does not hold."""
    assert IC_ASSUMPTIONS["IC-007"] == "A-H2"
    with pytest.raises(PhenomenonError, match="A-H2"):
        assumptions_for(level="cell", variable=FWI, ic_ids=["IC-007"])


def test_an_unknown_inferred_candidate_is_refused_by_name():
    with pytest.raises(PhenomenonError, match="IC-999"):
        assumptions_for(level="cell", variable=FWI, ic_ids=["IC-999"])


# --- shape --------------------------------------------------------------------


def test_the_variables_only_name_columns_that_have_a_role():
    for variable in (FWI, HEAT):
        for index in columns_used(variable):
            assert role_of(variable, index) in {
                "baseline",
                "future",
                "change",
                "corroborating_change",
            }


def test_an_unknown_level_is_refused():
    with pytest.raises(PhenomenonError, match="not one of"):
        _build("region", {"State": "X"}, [_member("R1C1", {241: "1", 253: "2"})], HEAT,
               HEAT_SEMANTICS)
    assert LEVELS == ("cell", "county", "state")


def test_an_identifier_that_is_entirely_code_is_still_required_to_be_labelled():
    """`California` masks to nothing, so only the exact wrapped-form check applies."""
    record = _build(
        "state",
        {"State": "California"},
        [_member("R1C1", {241: "1.000000000000000", 253: "36.000000000000000"})],
        HEAT,
        HEAT_SEMANTICS,
    )
    assert "identified by [provisional: `California`]" in record["description"]
    assert unlabelled_inferred_text(record) == []
    record["description"] = record["description"].replace(
        "[provisional: `California`]", "`California`"
    )
    assert [field for field, _text in unlabelled_inferred_text(record)] == ["G.identifier"]
