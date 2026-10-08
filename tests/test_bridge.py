"""D-018: candidate eligibility and the final relation vocabulary, on synthetic rows."""

from __future__ import annotations

import itertools

import pytest

from climrr import bridge
from climrr.compat import DIMENSIONS, FAMILY_LEVEL


def _row(**st):
    base = {d: "compatible" for d in DIMENSIONS}
    base.update(st)
    return {"pair_id": "SYN", "judgments": {d: {"status": s} for d, s in base.items()}}


def test_a_fully_compatible_row_is_eligible_and_may_be_supporting():
    assert bridge.candidate_bridge_eligible(_row()) == (True, [])
    assert bridge.check_relation(_row(), "supporting") == "supporting"


def test_scenario_unknown_is_eligible_but_never_supporting():
    row = _row(scenario="not_evaluable")
    assert bridge.candidate_bridge_eligible(row) == (True, ["scenario"])
    with pytest.raises(bridge.RelationError):
        bridge.check_relation(row, "supporting")
    assert bridge.check_relation(row, "supporting_qualified") == "supporting_qualified"


@pytest.mark.parametrize("concept", ["compatible", FAMILY_LEVEL])
@pytest.mark.parametrize("time,direction", list(itertools.product(["compatible", "not_evaluable"], repeat=2)))
def test_no_eligible_row_with_unknown_scenario_can_ever_be_supporting(concept, time, direction):
    row = _row(concept=concept, time=time, direction=direction, scenario="not_evaluable")
    assert bridge.candidate_bridge_eligible(row)[0]
    assert "supporting" not in bridge.permitted_relations(row)


def test_a_family_level_concept_is_eligible_but_only_qualified():
    row = _row(concept=FAMILY_LEVEL, direction="not_evaluable")
    assert bridge.candidate_bridge_eligible(row) == (True, ["direction"])
    assert "supporting" not in bridge.permitted_relations(row)


@pytest.mark.parametrize("st", [
    {"concept": "not_evaluable"},
    {"geography": "not_evaluable"},
    {"time": "incompatible"},
    {"scenario": "incompatible"},
    {"geography": "incompatible"},
])
def test_ineligible_rows(st):
    row = _row(**st)
    assert not bridge.candidate_bridge_eligible(row)[0]
    assert not {"supporting", "supporting_qualified"} & set(bridge.permitted_relations(row))


def test_not_evaluable_dimensions_travel_with_the_pair_whether_or_not_eligible():
    assert bridge.candidate_bridge_eligible(_row(concept="not_evaluable", time="not_evaluable"))[1] == [
        "concept", "time"]


def test_contradicting_only_on_a_direction_conflict_with_concept_and_place_matched():
    assert "contradicting" in bridge.permitted_relations(_row(direction="incompatible"))
    assert "contradicting" not in bridge.permitted_relations(_row(direction="incompatible", time="incompatible"))
    assert "contradicting" not in bridge.permitted_relations(_row(direction="incompatible", concept="not_evaluable"))


def test_the_vocabulary_is_closed():
    assert set(bridge.RELATIONS) == {"supporting", "supporting_qualified", "contradicting",
                                     "related_insufficient", "uncertain"}
    with pytest.raises(bridge.RelationError):
        bridge.check_relation(_row(), "partially_supporting")
