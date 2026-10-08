# Bridge eligibility and the final M5 relation

**Defined, tested, and not yet applied to any real pair.** Authorized by D-018
(`docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md`). Code:
`src/climrr/bridge.py`; tests: `tests/test_bridge.py`.

The ruling keeps two questions apart, and so does the code:

1. **May this pair be reviewed as a candidate bridge?** → `candidate_bridge_eligible`
2. **What is the pair, once reviewed?** → the final relation

A candidate is **not** a validated bridge, and a pair that nothing contradicts
is **not** thereby `supporting`.

## 1. `candidate_bridge_eligible(pair)`

Reads a compatibility row (five judgments, as `climrr.compat.evaluate_pair`
writes them) and returns `(eligible, not_evaluable_dimensions)`.

A pair is **eligible** iff all three hold:

| Condition | Statuses that satisfy it |
| --- | --- |
| concept matches | `compatible` (C-1, metric level) or `compatible_at_family_level` (C-2) |
| geography matches | `compatible` |
| nothing conflicts | no dimension is `incompatible` |

Time, scenario and direction may each be `compatible` or `not_evaluable`. The
`not_evaluable` dimensions come back with the result **whether or not the pair
is eligible**, so they travel with it and cannot be dropped.

## 2. The final relation (closed vocabulary)

| Relation | Permitted when |
| --- | --- |
| `supporting` | eligible; concept `compatible` at **metric** level; time, scenario **and** direction all `compatible` |
| `supporting_qualified` | eligible, but concept is family-level **or** any of time / scenario / direction is `not_evaluable`. The unmatched dimensions are carried with it |
| `contradicting` | concept positive, geography `compatible`, and the **only** `incompatible` dimension is direction |
| `related_insufficient` | always available: related, but not enough established |
| `uncertain` | always available: the reviewer cannot decide |

`check_relation(pair, relation)` raises on any relation the row does not
permit.

**Consequences, each tested:**

- **Unknown scenario against a scenario-specific prototype can never be
  `supporting`.** Every ClimRR prototype in the pilot is scenario-specific
  (RCP8.5), and every WP1 claim's scenario is `unknown`; such a pair can at best
  be `supporting_qualified`. The ruling: *"a scenario-specific ClimRR prototype
  cannot receive an unqualified `supporting` relation from a claim whose
  scenario is unknown."*
- **A family-level concept match can never be `supporting`.** A paper about the
  heat index is not, by that phrase, about days above 105°F (D-018, item 3).
- **Missing scenario is not scenario compatibility.** `not_evaluable` stays
  `not_evaluable` from the matrix through to the relation.

## 3. What decides the relation itself

Nothing yet. Choosing between the permitted relations for a real pair is
semantic review of an adjudicated claim, which waits for M4-WP1b and a later
M5 package. The mentor question now leading `MENTOR_BRIEF.md` --- exact
metric/scenario match, or disclosed family-level support --- decides whether
`supporting_qualified` is a bridge the benchmark will use.
