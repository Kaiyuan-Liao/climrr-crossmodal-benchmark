"""D-018: candidate-bridge eligibility, and the final M5 relation vocabulary.

Two separate things, kept separate (ruling, "Scientific risks" 3):

- **`candidate_bridge_eligible`** decides whether a compatibility row may be
  *reviewed* as a candidate bridge. It is not a relation and asserts nothing
  about support.
- **The final relation** is what a reviewed pair is eventually labelled. It is
  defined here and checked here, and **assigned nowhere yet**: no package has
  authorized applying it.

Both read a row as `climrr.compat.evaluate_pair` writes it.
"""

from __future__ import annotations

from climrr.compat import DIMENSIONS, FAMILY_LEVEL

#: Concept statuses that count as a positive concept match for candidacy.
CONCEPT_POSITIVE = ("compatible", FAMILY_LEVEL)
#: Dimensions whose `not_evaluable` candidacy tolerates (D-018, item 5).
TOLERATED_NOT_EVALUABLE = ("time", "scenario", "direction")

RELATIONS = {
    "supporting": "eligible; concept `compatible` at metric level; time, scenario and direction all `compatible`",
    "supporting_qualified": "eligible, but concept is family-level or any of time / scenario / direction is "
                            "`not_evaluable`; the unmatched dimensions travel with it. **Mandatory instead of "
                            "`supporting` whenever scenario is unknown against a scenario-specific prototype**",
    "contradicting": "concept positive and geography `compatible`, and the only `incompatible` dimension is "
                     "direction",
    "related_insufficient": "related, but not enough is established to support or contradict",
    "uncertain": "the reviewer cannot decide",
}


class RelationError(ValueError):
    """A relation the row's judgments do not permit."""


def candidate_bridge_eligible(pair: dict) -> tuple[bool, list[str]]:
    """(eligible, the dimensions that were `not_evaluable`).

    Eligible iff concept is `compatible` or `compatible_at_family_level`,
    geography is `compatible`, and no dimension is `incompatible`. The
    `not_evaluable` dimensions are returned either way so they travel with the
    pair and cannot be dropped silently.
    """
    st = {d: pair["judgments"][d]["status"] for d in DIMENSIONS}
    not_evaluable = [d for d in DIMENSIONS if st[d] == "not_evaluable"]
    eligible = (st["concept"] in CONCEPT_POSITIVE
                and st["geography"] == "compatible"
                and "incompatible" not in st.values())
    return eligible, not_evaluable


def permitted_relations(pair: dict) -> tuple[str, ...]:
    st = {d: pair["judgments"][d]["status"] for d in DIMENSIONS}
    eligible, not_evaluable = candidate_bridge_eligible(pair)
    out = []
    if eligible:
        qualified = st["concept"] == FAMILY_LEVEL or any(d in not_evaluable for d in TOLERATED_NOT_EVALUABLE)
        out.append("supporting_qualified" if qualified else "supporting")
    incompatible = [d for d in DIMENSIONS if st[d] == "incompatible"]
    if st["concept"] in CONCEPT_POSITIVE and st["geography"] == "compatible" and incompatible == ["direction"]:
        out.append("contradicting")
    out += ["related_insufficient", "uncertain"]
    return tuple(out)


def check_relation(pair: dict, relation: str) -> str:
    """Return `relation` if the row permits it; raise otherwise."""
    if relation not in RELATIONS:
        raise RelationError(f"unknown relation {relation!r}")
    if relation not in permitted_relations(pair):
        raise RelationError(f"{relation!r} is not permitted for {pair.get('pair_id')}: "
                            f"{ {d: pair['judgments'][d]['status'] for d in DIMENSIONS} }")
    return relation
