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
| concept matches | `compatible` (C-1, metric level) or `compatible_at_family_level` (C-2, revised by D-019 --- see below) |
| geography matches | `compatible` |
| nothing conflicts | no dimension is `incompatible` |

Time, scenario and direction may each be `compatible` or `not_evaluable`. The
`not_evaluable` dimensions come back with the result **whether or not the pair
is eligible**, so they travel with it and cannot be dropped.

**C-2 as revised by D-019.** When C-1 fails, the claim's tagged `concept`
value is searched with the frozen boundary-aware matcher
(`climrr.conceptmap.find_term`, the same function the M4-WP2 retrieval scan
used) for the accepted surface terms of the prototype concept's family
(`approved_lexical` entries only). A hit gives `compatible_at_family_level`
and records the family, the surface term, its `[start, end)` within the
concept value, and the concept-map entry and decision id. No new surface
terms: `"heat index trends"` matches `heat_index`; `"urban heat island"`,
`"wildfire smoke exposure"` and `"FWIs"` do not. This is lexical occurrence,
not synonymy, and a family match is never metric compatibility.

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

## 3. Evidence tiers (D-019)

Every adjudicated claim carries `evidence_tier`. The tier qualifies what a
claim can do in M5; it does not change the compatibility rules.

| Tier | Claims | What it can do |
| --- | --- | --- |
| **A** | `independently_confirmed` | strongest evidence |
| **B** | `adjudicated_modified` (scope not contested) | usable for candidate/bridge analysis when the adopted value is source-supported, the disagreement is preserved, and no unresolved issue directly determines the bridge |
| **C** | `single_reader_provisional`, or any claim on a scope-contested item | diagnostic or candidate use only; **cannot independently establish an accepted bridge** |

WP1 adjudicated set: **A 1, B 18, C 10** (`artifacts/literature/wp1_claims_adjudicated/`).
WP2 reader-1 claims are all **C** until their blind reading and adjudication.

**Claim-type rules and ties.** A rule that depends on claim type treats
`unresolved_tie` as `not_evaluable` (D-019). Today that is T-2 (a historical
`finding` ending before 2045): `compare_time` returns `not_evaluable` with
reason `claim_type_unresolved_tie`. The proposition itself stays usable where
no rule depends on its type (`LIT-000381-C3`).

**Third reader.** Not required for the whole WP1 set. **Required** if a final
accepted bridge depends materially on a scope-contested claim, an unresolved
tie that affects the bridge, or a single-reader-only semantic assertion.

## 4. What decides the relation itself

Nothing yet. Choosing between the permitted relations for a real pair is
semantic review of an adjudicated claim, which waits for the M4-WP2 blind reading,
adjudication and Phase 4 compatibility run (D-019), and a later
M5 package. The mentor question now leading `MENTOR_BRIEF.md` --- exact
metric/scenario match, or disclosed family-level support --- decides whether
`supporting_qualified` is a bridge the benchmark will use.
