# ClimRR Cross-Modal Benchmark — Track A / Track B GUIDANCE Ruling

**Decision context:** Review of M4-WP4 / M5-WP4 and Stage 2a–2c run 1  
**Date:** 2026-10-20  
**Track A reviewed head:** `work/m4-wp4-adj` @ `c0be540`  
**Track B reviewed head:** `work/trackb-stage2` @ `2331e19`  
**Base:** `main` @ `38116a0`  
**GUIDANCE status:** PASS WITH ACTIONS

> This ruling accepts the bounded zero-result from the 20-paper compatibility pilot, approves the geography-role layer, prospectively masks `standardized heat index`, prospectively fixes mixed-region geography handling, prioritizes a table-unit granularity redesign diagnostic over further scenario-token retrieval, and authorizes a family-level Stage-2 diagnostic run 2. No QA is authorized.

---

## Gate status

**PASS WITH ACTIONS**

Both tracks pass their bounded objectives.

### Track A

- **M4-WP4 passes** as the 20-paper, two-reader semantic-reading/adjudication pilot.
- **M5-WP4 passes** as the bounded positive-case compatibility experiment.
- Accepted result: **0 candidate-bridge-eligible pairs among 354 deterministic claim–prototype comparisons**.
- Merge of `work/m4-wp4-adj` is authorized after the decisions below are documented and bookkeeping reflects reviewed head `c0be540`.

### Track B

- **Stage 2a–2c run 1 passes as a diagnostic.**
- Merge of `work/trackb-stage2` is authorized after the rulings below are recorded.
- A **family-level diagnostic run 2 is authorized**.

### Main scientific conclusion

The repeated zero is no longer best interpreted as a corpus-retrieval failure.

The evidence now supports:

> **The current table-side prototypes are expressed at finer metric, geography, and scenario granularity than scientific papers usually state.**

Therefore the next primary experiment should be a **table-unit representation/granularity redesign diagnostic**, while keeping the current prototypes as negative controls.

---

## Current-stage assessment

### Track A

The 20-paper pipeline was deterministic and properly staged:

- sample frozen before reading;
- reader 1 read before hit locations were opened;
- blind second reader independent;
- adjudication after both readings were frozen;
- exact evidence spans verified.

Adjudicated set:

- **118 claims**
- Tier A: **3**
- Tier B: **47**
- Tier C: **68**

Compatibility:

```text
118 claims × 3 prototypes = 354 pairs
```

Results:

- concept: 0 metric-compatible, 12 family-level;
- geography: 2 compatible;
- time: 0 compatible;
- scenario: 0 compatible;
- direction: 0 compatible;
- candidate-bridge-eligible: **0**.

The key result is:

> **positive concept evidence and positive geography evidence occur, but not together in one claim at the exact current prototype granularity.**

### Track B

Stage 2a remains dictionary-grounded and does not change M1 status.

Run 1 shows a large family-vs-measure coverage difference:

- temperature: ~124k matches;
- precipitation: ~85k;
- wind speed: ~27k;
- consecutive dry days: ~7k;
- degree days: ~3k;
- Fire Weather Index: ~548;
- threshold-specific heat-index measures: approximately 0–2 under the current lexical representation.

This supports a family-level diagnostic run 2, but does not prove threshold measures are absent from the literature.

---

## Evidence check

### 1. A1 — Accept Track A result and merge

**Approved.**

Use the bounded statement:

> **No candidate-bridge-eligible pair was found under the current deterministic rules among the adjudicated claims of the twenty frozen LITCORPUS-02 place candidates.**

Do not generalize beyond the tested sample.

---

### 2. A2 — Geography-role rulings

#### Geography role enters G-1

**Approved.**

A place string alone is insufficient.

Affiliation, citation/person, contextual geography, or data-source geography must not become geographic compatibility.

#### Conservative role on disagreement

**Approved.**

Use the more conservative geography role unless both readers independently support study geography.

#### `cited_study_area`

**Approved as study geography, with evidence-tier qualification.**

It may satisfy the role gate, but the claim's evidence tier still constrains whether it can establish an accepted bridge.

#### `m5wp4.py` beside frozen `compat.py`

**Approved.**

Preserve old freezes. Do not retroactively mutate prior compatibility code.

---

### 3. A3 — `standardized heat index`

**Add a prospective mask.**

Flag-only is no longer sufficient.

The phrase:

```text
standardized heat index
```

contains:

```text
heat index
```

but there is no approved equivalence between Standardized Heat Index and the ClimRR heat-index family.

Prospective rule:

> **A recognized compound concept containing an approved family term must mask that inner phrase when the compound's equivalence has not been explicitly approved.**

Add `standardized heat index` to the future C-2 mask list.

Do not rewrite the frozen M5-WP4 matrix.

---

### 4. A4 — Mixed-continent G-2 behavior

**Revise G-2 prospectively.**

G-2 may return `incompatible` only when the entire explicit geography is wholly disjoint from the prototype.

For multi-region claims:

- all listed regions disjoint → `incompatible`;
- mixture of disjoint and potentially relevant regions → `not_evaluable`;
- broad region containing the prototype but not resolving to required granularity → `not_evaluable`;
- exact supported geography → G-1/G-R.

Do not rewrite M5-WP4.

---

### 5. A5 — Interpretation of the repeated zero

Choose **a constrained unit-redesign diagnostic**.

Do not make scenario-token retrieval the next primary route.

The next question is:

> **Can table-side units be represented at concept and geography granularity that scientific literature actually states, while remaining deterministically grounded in ClimRR?**

Investigate:

- family-level concept rather than threshold-specific metric;
- state / multi-state / climate-region geography where deterministic aggregation is defensible;
- scenario retained as table provenance but not automatically required for candidate eligibility;
- time represented only at the granularity both sources support.

Keep:

- P-CELL-1
- P-COUNTY-1
- P-STATE-1 v2

as controls.

---

### 6. B1 — Accept Stage 2 run 1 and merge

**Approved as diagnostic.**

Stage 2a is complete.

Stage 2b/2c run 1 is accepted as exploratory coverage evidence.

Merge is authorized after recording the rulings below.

---

### 7. B2 — Family-level run 2

**Authorized.**

For every dictionary-described measure, request a broader scientific family.

Store only as:

```text
status: candidate_family
```

Record:

```text
dictionary_concept_id
dictionary_passage
model_id
prompt_sha256
candidate_family
candidate_family_surface_forms
date
status
```

No candidate family becomes production vocabulary, ontology, C-2 input, compatibility logic, or unit design without later approval.

---

### 8. B3 — Threshold measures

Do **not** label them inherently `lexically_unsearchable`.

Supported conclusion:

> **Under the current run-1 candidate terms and matcher representation, the threshold-specific heat-index measures have effectively no direct lexical footprint in this source.**

Keep their measure-level coverage.

Add family-level coverage alongside it.

Do not attribute heat-index family coverage to an individual threshold measure.

---

### 9. B4 — Sanitizer normalization

**Authorize narrow deterministic orthographic normalization.**

Allowed:

```text
>    → above
<    → below
°F   → degrees F
° F  → degrees F
°C   → degrees C
° C  → degrees C
%    → percent
```

Requirements:

- retain original model term;
- store normalized form separately;
- record transform rule IDs;
- freeze normalization table before run 2;
- no semantic paraphrasing, stemming, abbreviation expansion, or synonym inference.

---

### 10. B5 — Candidate families for mentor discussion

Do not approve final new unit families before the mentor discussion.

Carry these as **discussion candidates only**:

- temperature;
- precipitation;
- wind speed;
- consecutive dry days / dry spell;
- degree days;
- Fire Weather Index;
- heat index.

The heat-index thresholds remain measures within the heat-index family.

Do not rank these seven solely by raw literature coverage.

---

## Scientific risks

### 1. Overlearning from negative experiments

The repeated zero is a benchmark-design diagnosis, not proof that cross-modal bridges are impossible.

### 2. Relaxing requirements until something passes

Any redesigned unit must be scientifically defined and frozen before literature compatibility is tested.

### 3. Circular redesign from already-read papers

Do not design new units around one particular WP4 paper.

Use aggregate patterns, not individual hits.

### 4. Scenario tolerance is not scenario agreement

Missing scenario may allow broader relatedness, but does not support the RCP8.5-specific component.

### 5. Family coverage can hide metric mismatch

Always report family and measure coverage separately.

### 6. LLM-generated ontology risk

Run-2 family assignments remain hypotheses.

### 7. Geography hierarchy risk

State, county, national, climate-region, and multi-region geographies need explicit containment/granularity rules before evaluation.

---

## Required actions

### Track A

1. Record **M4-WP4 PASS WITH ACTIONS**.
2. Record **M5-WP4 PASS WITH ACTIONS**.
3. Preserve the frozen 354-pair matrix unchanged.
4. Approve G-R geography-role gating.
5. Approve conservative role adjudication.
6. Approve `cited_study_area` as study geography, evidence tier retained.
7. Preserve `m5wp4.py` as the WP4 semantic-rule layer.
8. Add `standardized heat index` to the prospective C-2 mask list.
9. Amend prospective G-2 so mixed-region lists are not incompatible unless wholly disjoint.
10. Do not rerun WP4 only to apply these prospective changes.
11. Merge Track A after documenting the rulings.
12. Open a bounded **unit-granularity redesign diagnostic**.
13. Do not use scenario-token retrieval as the next primary experiment.

### Track B

14. Record **Stage 2 run 1 PASS as diagnostic**.
15. Merge Track B after documenting the rulings.
16. Authorize family-level run 2.
17. Store model family assignments only as `candidate_family`.
18. Preserve measure-level run-1 results.
19. Add family-level coverage alongside measure-level coverage.
20. Add only the approved deterministic normalizations.
21. Preserve original and normalized strings separately.
22. Record Polaris Python patch version if recoverable; otherwise mark `unknown`.
23. Carry the seven candidate families to the mentor as discussion candidates only.

---

## Decisions for Kaiyuan or mentor

| Question | Ruling |
|---|---|
| A1 M4-WP4 gate | **PASS WITH ACTIONS** |
| A1 M5-WP4 gate | **PASS WITH ACTIONS — bounded zero accepted** |
| Merge Track A | **Authorized after ruling bookkeeping** |
| A2 geography role enters G-1 | **Approved** |
| Conservative role on disagreement | **Approved** |
| `cited_study_area` as study geography | **Approved, evidence tier retained** |
| `m5wp4.py` layered over frozen `compat.py` | **Approved** |
| A3 `standardized heat index` | **Prospectively mask from automatic C-2 matching** |
| Rewrite frozen WP4 matrix | **No** |
| A4 mixed-continent geography | **Prospectively `not_evaluable` unless wholly disjoint** |
| A5 next route | **Unit-redesign diagnostic** |
| Scenario-token retrieval as next primary route | **No** |
| Immediately replace existing prototypes | **No** |
| B1 Stage 2 run 1 | **PASS as diagnostic** |
| Merge Track B | **Authorized after ruling bookkeeping** |
| B2 family-level run 2 | **Authorized** |
| Model family assignment | **`candidate_family` only** |
| B3 threshold measures inherently unsearchable | **No** |
| Add family-level coverage for threshold concepts | **Yes** |
| B4 deterministic `°`, `>`, `<`, `%` normalization | **Authorized narrowly** |
| Semantic synonym/paraphrase normalization | **Not authorized** |
| B5 choose final families now | **Wait for mentor** |
| Candidate families to discuss | **temperature, precipitation, wind speed, dry-spell/CDD, degree days, FWI, heat index** |
| QA | **Still not authorized** |

---

## Next bounded objective

Proceed with two follow-ups, with **unit redesign taking priority over further positive-bridge retrieval**.

### Track A-next — Unit-Granularity Diagnostic

Do **not** build production benchmark units yet.

Keep current controls:

```text
P-CELL-1
P-COUNTY-1
P-STATE-1 v2
```

Test alternative representations such as:

- family-level FWI phenomenon;
- family-level heat-index phenomenon;
- geography at deterministic state or broader supported aggregation;
- scenario retained in provenance but not required for candidate eligibility;
- time represented only at supported granularity.

Before any compatibility test:

1. define the new unit schema;
2. define deterministic table aggregation;
3. freeze unit identities;
4. define geography hierarchy/containment rules;
5. distinguish:
   - exact metric support;
   - family-level support;
   - scenario-specific support;
   - scenario-unspecified support.

Purpose:

> **Test whether bridge feasibility changes when representation granularity is aligned—not to force positive pairs.**

### Track B-next — Stage 2 Family-Level Diagnostic Run 2

For all 14 dictionary measure concepts:

1. preserve run-1 measure identity;
2. request a `candidate_family`;
3. generate candidate family-level search forms;
4. apply only pinned orthographic normalization;
5. run topical-only counts;
6. run context-filtered counts;
7. report measure-level and family-level coverage side by side.

Example:

```text
measure:
  Number of Summer days with daily max heat index above 105 F

measure_coverage:
  0

candidate_family:
  heat_index

family_coverage:
  <diagnostic count>
```

Do not reinterpret family coverage as threshold-measure coverage.

---

## Acceptance criteria

The next GUIDANCE package is ready when:

1. Track A and Track B merge bookkeeping reflects the reviewed pushed heads.
2. Frozen M5-WP4 outputs remain byte-identical.
3. Prospective `standardized heat index` masking is documented without rewriting WP4.
4. Prospective mixed-region G-2 semantics are documented without rewriting WP4.
5. Geography-role semantics remain explicit.
6. Evidence tiers continue to constrain accepted bridges.
7. Unit redesign does not use a particular read paper to choose geography or metric.
8. Current prototypes remain as controls.
9. Redesigned units are table-grounded before literature comparison.
10. Family vs metric semantics are explicit.
11. Scenario unknown is not called scenario-compatible.
12. Scenario-specific and scenario-tolerant relations remain distinguishable.
13. Geographic aggregation/containment is declared before evaluation.
14. No similarity model or LLM decides final compatibility.
15. Stage-2 run 2 preserves run 1 unchanged.
16. Every proposed family is `candidate_family`.
17. Candidate-family provenance includes model/prompt/date.
18. Original model-proposed forms are retained.
19. Normalized forms carry deterministic transform-rule provenance.
20. Only `>`, `<`, degree notation, and `%` receive authorized normalization.
21. No semantic synonym generation occurs during normalization.
22. Threshold-measure coverage remains separately reported.
23. Family coverage is not attributed to a threshold measure.
24. The seven discussion families are not automatically approved as benchmark families.
25. Mentor feedback is recorded separately from diagnostic yield.
26. Q22 remains open unless JL answers it.
27. No M1 column status changes.
28. Index 117 remains unlabeled.
29. No QA is generated.

---

## Do not do yet

Do not run another large literature retrieval requiring an RCP/SSP token as the primary next experiment.

Do not loosen geography matching until a positive pair appears.

Do not convert `San Diego County` into `California` through ad hoc containment.

Do not rewrite P-STATE-1 around one of the papers already read.

Do not interpret `standardized heat index` as ordinary heat index merely because the phrase contains `heat index`.

Do not call a mixed global-region claim geographically incompatible with California only because one listed region is disjoint.

Do not replace threshold measures with family concepts in the dictionary inventory.

Do not say threshold-specific heat-index measures have “no literature”; current evidence is only **no/near-zero lexical retrieval under the current measure-level representation**.

Do not use model-generated family assignments as ontology truth.

Do not select the seven candidate families solely from coverage counts.

Do not start QA.

The evidence now supports a change in **what to test next**, not a relaxation of evidence standards:

> **Corpus retrieval is no longer the main bottleneck. The next hypothesis is that the current table units are expressed at finer metric/geographic/scenario granularity than scientific papers normally state.**

The next experiment should test that representation hypothesis explicitly while keeping the current three prototypes as negative controls.
