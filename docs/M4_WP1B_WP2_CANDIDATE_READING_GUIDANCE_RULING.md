# ClimRR Cross-Modal Benchmark — M4-WP1b / M4-WP2 Review and Candidate-Reading GUIDANCE Ruling

**Milestone context:** Independent-reading validation complete; relevance-guided candidate retrieval complete  
**Reviewed packages:** M4-WP1b — blind second reading and adjudication; M4-WP2 — retrieval half  
**Next work package:** semantic inspection of the four frozen WP2 candidates, followed by bounded positive-case compatibility validation  
**GUIDANCE status:** PASS WITH ACTIONS

> This ruling accepts the independent-reading and retrieval tracks, preserves contested evidence explicitly, revises C-2 to boundary-aware lexical family matching inside the tagged concept field, and authorizes semantic reading of exactly four frozen candidates. No QA is authorized.

---

## Gate status

**PASS WITH ACTIONS**

Both tracks have reached the point needed to proceed.

1. **M4-WP1b passes as an independent-reading validation package, with contested claims still explicitly qualified.**
2. **M4-WP2 retrieval passes as a frozen candidate-generation package.**
3. **The four-item candidate pool is accepted as the WP2 sample. Do not widen it merely to reach 12.**
4. **Semantic reading of the four frozen candidates is authorized**, using the same two-reader + adjudication structure.
5. **Compatibility evaluation against the three prototypes is authorized after adjudication**, using P-STATE-1 v2.
6. **C-2 should be revised:** exact whole-field equality is too restrictive. Use boundary-aware occurrence of an approved concept-family surface term inside the claim's tagged concept field. This remains lexical—not semantic—matching.
7. **No QA is authorized.**

The independent second reading materially supports the premise for relevance-guided sampling: neither reader found a pilot concept, U.S. geography, or named emissions scenario among the original random-sample claims. The disagreements were mainly about scope breadth and dimension annotation, not hidden pilot-relevant claims.

---

## Current-stage assessment

Track A accomplished the important purpose of WP1b.

The second reader produced 21 claims independently, with 85 exact source spans, before comparison.

Scope agreement was only 6/10, but the pattern is informative:

- the blind reader was consistently more conservative;
- disagreements tended to move `off_topic` or borderline `in_scope` cases to `ambiguous`;
- the blind reader did not uncover a new set of pilot-relevant claims.

The two readings aligned on 19 claims:

- 8 first-reader-only;
- 2 blind-reader-only.

Geography tagging was the largest disagreement dimension, which shows that the second pass did substantive work rather than simply reproducing reader 1.

Most importantly for WP2, the combined 48 claims from both readings still contain:

- zero frozen pilot concept terms;
- zero WP2/U.S. place terms relevant to the pilot;
- zero named climate/emissions scenarios.

That supports relevance-guided retrieval.

Track B also behaved correctly.

The authorized retrieval rules were applied without loosening the vocabulary merely to manufacture a target sample size.

Only four corpus items satisfy both:

- an approved concept-family term;
- one of the actual prototype place terms.

Therefore:

> **4 is the scientifically correct sample size under this retrieval definition.**

---

## Evidence check

### 1. Rule 3 span-limited adjudication

**Approved.**

The implementation:

> keep only the portion of a value that both readers support and that an explicit evidence span actually states

is a good operationalization of “more conservative value.”

For example, retaining:

```text
old-growth subtropical forest in southern China
```

as `explicit`

is preferable to keeping unsupported additional specificity.

The adopted value may remain `explicit` when the adopted fragment is directly stated by the cited span.

There is no need to demote the surviving supported fragment to `inferred` merely because another reader inferred a more specific location.

**Ruling:** Rule 3b/3c span-limited trimming is accepted.

### 2. Override J-1 — 16-week wildfire-smoke exposure

**Approved as a narrow schema-placement override.**

Both readers independently captured the same factual experimental regimen.

Their disagreement was where to store it:

- reader 1: temporal frame;
- blind reader: experimental condition.

Applying “unknown beats a value” literally would discard information that both readers actually found.

Moving:

```text
simulated wildfire smoke versus filtered air,
2 h/day, 5 days/week, 16 weeks
```

to `experimental_condition` is scientifically cleaner and consistent with the prior separation between experimental conditions and climate scenarios.

The literal rule result is also preserved alongside the override.

**Ruling:** J-1 stands.

Do not generalize J-1 into a broad permission to rescue facts whenever adjudication produces `unknown`.

### 3. `LIT-000381-C3` claim-type tie

**Keep `unresolved_tie`.**

Do not choose `mechanism` or `finding` merely to complete the record.

The proposition itself remains usable where a downstream rule does not depend on claim type.

Any rule that depends on claim type should treat this aspect as:

```text
not_evaluable
```

until independently resolved.

### 4. `LIT-000571` contested scope

Keep the contested status visible.

The blind reader classified it `ambiguous`, while reader 1 classified it `in_scope_hazard`.

All five promoted claims come from reader 1, and the blind reader explicitly rejected passages underlying some of them.

Ruling:

> retain these claims as `adjudicated_modified` / scope-contested artifacts, but do **not** let them serve as independently validated M5 evidence.

They may participate in diagnostic compatibility analysis if their contested status is carried.

A third reader is **not required for the entire WP1b set**.

A third-party or additional independent adjudication **is required if a future accepted bridge depends materially on one of these contested claims.**

### 5. Are `adjudicated_modified` claims usable in M5?

**Yes, with tiered evidence status.**

Do not restrict M5 to the single `independently_confirmed` claim.

Use practical evidence tiers:

#### Tier A — independently confirmed

Strongest evidence.

#### Tier B — adjudicated modified

Usable for candidate/bridge analysis when:

- the adopted value is source-supported;
- the disagreement is preserved;
- no unresolved issue directly determines the bridge.

#### Tier C — single-reader / contested provisional

Diagnostic or candidate use only.

Cannot independently establish an accepted bridge.

This is more faithful to the WP1b evidence than a binary “confirmed vs unusable” rule.

### 6. C-2 concept-family matching

**Revise C-2.**

Current C-2 requires the entire normalized claim concept value to equal an approved surface term.

That is too brittle for structured values such as:

```text
heat index trends
```

or:

```text
seasonal Fire Weather Index
```

even when an approved concept-family term occurs explicitly inside the field.

However, do **not** introduce semantic containment.

Use the same approved **boundary-aware lexical matcher** already validated for retrieval.

Revised C-2:

> If C-1 metric matching fails, search the claim's tagged concept value for an **approved surface term belonging to the prototype's concept family**, using the frozen boundary-aware matcher. If found, return `compatible_at_family_level`.

Record:

- matched canonical family;
- approved surface term;
- `[start,end)` within the concept value;
- concept-map entry / decision ID.

Examples:

```text
"heat index trends"
```

contains approved:

```text
"heat index"
```

→ family-level compatible.

```text
"urban heat island"
```

contains no approved heat-index term

→ `not_evaluable`.

```text
"wildfire smoke exposure"
```

contains neither `FWI` nor `fire weather index`

→ `not_evaluable`.

This remains lexical mapping, not scientific synonymy.

### 7. P-STATE-1 v2

**Accepted for future work, with a provenance note.**

The v2 correction is properly versioned and leaves the frozen M5-WP1 artifacts unchanged.

The disclosed issue that P-CELL-1/P-COUNTY-1 have a thinner baseline citation chain does not invalidate P-STATE-1 v2.

However, the project should eventually repair that provenance inconsistency so equivalent horizon claims cite the same authoritative metadata source.

This is cleanup, not a blocker for WP2 reading.

### 8. Four candidates versus widening to all U.S. states

**Choose option (i): read the four now.**

Do not widen geography merely to make the sample larger.

The current retrieval question is:

> Which papers lexically mention one of our approved pilot concept families **and** one of the geographic terms of our actual three prototypes?

Under that question, the four candidates are:

```text
LIT-000166
LIT-000519
LIT-001501
LIT-001536
```

Expanding to all U.S. states changes the scientific question.

That could later become a separately predeclared:

> **M4-WP2b / prototype-expansion experiment**

but should not be mixed into this WP2 package.

---

## Scientific risks

### 1. Treating adjudication as independence

The second reading was independent, but the adjudicator is reader 1 / the prototype-exposed EXECUTOR.

That limits independence for contested cases.

This is why evidence tiers must remain visible.

### 2. Family lexical match being mistaken for metric support

Even with revised C-2:

```text
heat index trends
```

may match the `heat_index` family.

It does **not** establish:

```text
days above 105°F
```

Metric-level support remains separate.

### 3. Retrieval lexical hits may be incidental

`California` may be an affiliation.

`Stephens` may be a surname.

A lexical hit is only a reason to inspect the paper.

It is not semantic evidence.

### 4. Four-item sample is intentionally relevance-selected

The four papers were selected because their raw text contains relevant concept/place vocabulary.

Therefore bridge yield from these four cannot estimate corpus prevalence.

### 5. Building prototypes after seeing retrieved literature

If the project later scans all U.S. states and then builds matching ClimRR prototypes after seeing the literature, benchmark construction can become circular.

Any WP2b expansion must define prototype-selection rules before semantic reading.

### 6. `supporting_qualified` must remain genuinely qualified

A family-level match with unknown scenario/time cannot be presented as validating the exact RCP-conditioned ClimRR metric.

---

## Required actions

1. Record **M4-WP1b PASS WITH ACTIONS**.

2. Accept Rule 3's span-limited conservative-value implementation.

3. Accept J-1 as a one-off schema-placement correction with the literal rule result preserved.

4. Preserve `LIT-000381-C3.claim_type = unresolved_tie`.

5. Preserve `LIT-000571` as scope-contested.

6. Introduce or document evidence tiers:
   - independently confirmed;
   - adjudicated modified;
   - single-reader / contested provisional.

7. Do not require third-party adjudication for every WP1 claim.

8. Require additional independent adjudication if a final accepted bridge depends materially on:
   - a scope-contested claim;
   - an unresolved tie affecting the bridge;
   - a single-reader-only semantic assertion.

9. Revise C-2 from whole-field exact equality to **boundary-aware occurrence of an approved family surface term within the claim's tagged concept field**.

10. Preserve:
    - matched term;
    - family ID;
    - concept-field span;
    - concept-map provenance.

11. Do not add new synonyms to accomplish this revision.

12. Record **M4-WP2 retrieval PASS** with sample size **4**, not 12.

13. Keep the four frozen candidate IDs and retrieval artifacts unchanged.

14. Do not expand place terms before reading the four.

15. Use P-STATE-1 v2 in the forthcoming compatibility run.

16. Preserve all v1/frozen M5-WP1 inputs unchanged.

17. Add a later provenance-cleanup task for the baseline-window citation chain of P-CELL-1/P-COUNTY-1.

---

## Decisions for Kaiyuan or mentor

| Question | Ruling |
|---|---|
| WP1b gate | **PASS WITH ACTIONS** |
| Rule 3 span-limited trimming | **Approved** |
| Keep supported trimmed value `explicit` | **Yes, when cited span explicitly states it** |
| J-1 experimental-condition override | **Approved as narrow exception** |
| `LIT-000381-C3` type | **Keep `unresolved_tie`** |
| `LIT-000571` scope | **Keep contested** |
| Third reader for all WP1 claims | **Not required** |
| Third reader if accepted bridge relies on contested claim | **Required** |
| `adjudicated_modified` claims usable in M5 | **Yes, with evidence tier retained** |
| C-2 whole-field exact equality | **Revise** |
| C-2 boundary-aware approved-term occurrence | **Approved** |
| WP2 pool of 4 | **Accept all 4 as the sample** |
| Widen to all U.S. states now | **No** |
| Possible WP2b later | **Yes, only as separately predeclared expansion** |
| Read the four frozen candidates | **Authorized** |
| Blind second pass on those four | **Required** |
| Compatibility against 3 prototypes | **Authorized after adjudication** |
| Use P-STATE-1 v2 | **Yes** |
| QA generation | **Still not authorized** |

The existing mentor question remains important:

> **Is a family-level literature bridge with disclosed metric/scenario mismatch useful for the intended benchmark, or must literature support the exact ClimRR metric and scenario?**

Until that is resolved, `supporting_qualified` should remain analytically separate from unqualified `supporting`.

---

## Next bounded objective

Authorize **M4-WP2 — Semantic inspection of the four frozen relevance-guided candidates**, followed by a bounded positive-case M5 compatibility test.

### Phase 1 — first reader

Read exactly:

```text
LIT-000166
LIT-000519
LIT-001501
LIT-001536
```

Do not replace any item.

Apply the same WP1 extraction rubric:

- scope;
- terminal status;
- structured claims;
- concept;
- geography;
- temporal frame;
- climate scenario;
- experimental condition;
- direction/relation;
- claim type;
- exact source spans;
- rejected/ambiguous passages.

Because these papers were relevance-selected, record separately:

- which retrieval hits were scientifically substantive;
- which were incidental;
- whether the hit term occurred in a promoted claim.

Do **not** allow the retrieval hit to pre-fill claim fields.

### Phase 2 — blind second reader

Use a fresh session.

Provide only:

- the four frozen files;
- extraction rubric;
- source-location convention.

Do not provide:

- retrieval terms or hit locations;
- prototypes;
- reader-1 results;
- compatibility rules;
- expected positive result.

Freeze the blind reading before comparison.

### Phase 3 — adjudication

Apply the approved WP1b rules.

Preserve:

- both readings;
- disagreements;
- evidence tier;
- contested statuses.

Any positive bridge that ultimately depends on a contested adjudication remains provisional until independently resolved.

### Phase 4 — compatibility

Freeze:

- adjudicated WP2 claim set;
- P-CELL-1;
- P-COUNTY-1;
- **P-STATE-1 v2**;
- concept-map version;
- compatibility-rule version.

Run every adjudicated WP2 claim against all three prototypes.

Use revised C-2.

Compute:

- five dimension judgments;
- `candidate_bridge_eligible`;
- final provisional relation category.

A candidate may be eligible when:

- concept = metric-compatible **or** family-level compatible;
- geography = compatible;
- no dimension is incompatible.

But final relation must distinguish at least:

- `supporting`;
- `supporting_qualified` / related-insufficient as appropriate;
- contradictory;
- incompatible;
- uncertain.

No QA.

---

## Acceptance criteria

The WP2 semantic package is ready for GUIDANCE review when:

1. Exactly the four frozen candidates are read.

2. No candidate is substituted or manually added.

3. Reader 1 does not treat retrieval hits as claim truth.

4. Every promoted claim has exact source evidence.

5. Retrieval hits are classified after reading as substantive or incidental.

6. The blind reader receives no retrieval-term locations, prototypes, first reading, or M5 results.

7. The blind second reading is frozen before comparison.

8. Adjudication preserves both readings and every disagreement.

9. Rule 3 uses the approved span-limited conservative interpretation.

10. J-1 remains limited to its already approved circumstance; new overrides require explicit justification.

11. Unresolved claim-type ties remain unresolved unless new independent evidence resolves them.

12. Every final claim carries an evidence-validation tier.

13. C-2 uses only approved concept-map surface terms.

14. C-2 matches using boundary-aware occurrence inside the tagged concept field.

15. C-2 records the exact matched surface term and span.

16. No synonym or ontology expansion occurs during WP2.

17. Metric-level compatibility remains distinct from family-level compatibility.

18. All adjudicated claims are compared with all three prototypes.

19. P-STATE-1 v2 is used; the old M5-WP1 freeze remains untouched.

20. Unknown scenario remains `not_evaluable`.

21. Family-level concept compatibility cannot yield unqualified `supporting`.

22. A scope-contested/single-reader-only claim cannot by itself establish an accepted bridge.

23. Candidate eligibility and final semantic relation remain separate outputs.

24. If no candidate bridge emerges, report that result without widening the four-item sample inside the same package.

25. No QA is generated.

---

## Do not do yet

Do not widen to all U.S. state names merely because four feels small.

Do not build a new ClimRR state prototype after seeing which states occur in the retrieved papers.

Do not redefine the WP2 candidate pool after semantic reading.

Do not allow `"heat index trends"` to become metric-level `days_above_105F` compatibility.

Do not map UHI to heat index or wildfire smoke to FWI.

Do not let a retrieval hit populate claim geography automatically.

Do not upgrade `adjudicated_modified` to `independently_confirmed`.

Do not resolve `LIT-000381-C3` claim type by preference.

Do not use the five contested `LIT-000571` claims as definitive literature evidence without further independent resolution.

Do not interpret a positive candidate-eligibility result as automatically `supporting`.

Do not begin QA.

The next experiment is deliberately focused:

> **Read the four papers that the predeclared lexical retrieval system actually found, independently extract what they say, and determine whether any real claim can survive the full provenance-preserving bridge pipeline.**

If those four yield no eligible pair, that will be the appropriate point to design a separate WP2b expansion rather than changing the retrieval definition mid-experiment.
