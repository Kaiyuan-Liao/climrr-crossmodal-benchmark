# ClimRR Cross-Modal Benchmark — Track C / Track D Soft-QA Guardrails

**Decision context:** Mentor direction of 2026-10-22 superseding parts of the earlier strict-compatibility ruling set  
**Date:** 2026-10-27  
**Applies to:** Track C agent-based paper grouping and Track D table-grounded QA templates  
**GUIDANCE status:** PASS WITH ACTIONS — guardrail update only

> The mentor direction changes the project from using deterministic compatibility as the acceptance gate to using provenance-preserving soft candidate generation, deterministic consistency checks, and human semantic review. C/G/T/S/D remain recorded for audit but no longer serve as the sole hard acceptance gate. No LLM output may alter concept-map status, column status, or deterministic compatibility rules.

---

## Gate status

**PASS WITH ACTIONS — guardrail update only**

The mentor direction of **2026-10-22** legitimately changes the project from:

> deterministic compatibility as the acceptance gate

to:

> **provenance-preserving soft candidate generation + deterministic consistency checks + human validation**

Do not preserve the old M5 acceptance logic as the main bottleneck.

Keep C/G/T/S/D as audit dimensions, but not as a hard pass/fail gate.

The four requested guardrail rulings are:

1. **Minimum human review:** one independent human reviewer is sufficient for ordinary acceptance **if deterministic checks pass first**; a second reviewer is required for ambiguous/high-risk cases.
2. **Candidate record:** add provenance-of-input, reviewer-disposition, answer-derivation, and soft-link-rationale fields.
3. **Agent access to unit values:** **definitions only during proposal; computed values withheld.** Values may be revealed only after candidate link/template structure is frozen and the deterministic answer is generated.
4. **Multi-concept template using verified + unverified variables:** **No.** Every variable affecting retrieval semantics or question meaning must come from the verified/authorized set, even when it is not used numerically in the answer.

---

## Current-stage assessment

The mentor's direction changes the benchmark-construction objective.

Previously, the project asked:

> **Can we prove a strict semantic bridge before generating QA?**

The new direction is closer to:

> **Can an agent propose plausible cross-modal QA candidates, provided every candidate is fully auditable to both original resources and a human can judge its quality?**

That is a valid construction strategy, but it requires a different validity model.

The new validity chain should be:

> **candidate generation → deterministic provenance/consistency checks → human semantic review → accepted QA**

not:

> deterministic compatibility → QA

The strongest protections are now:

- exact source fidelity;
- provenance completeness;
- separation between proposal and answer computation;
- explicit recording of unresolved semantic mismatches;
- human review.

The mentor-approved directions are retained:

- family-level table-side object with metric/scenario as provenance;
- state / multi-state / climate-region geography;
- cross-location comparison as a possible QA type.

The five ungoverned families remain open.

Tracks A-next and B are deprioritized, not cancelled.

The three existing frozen units remain controls.

---

## Evidence check

### 1. Minimum human-review protocol

Use a **one-reviewer default with mandatory escalation**.

Two full human reviewers for every generated QA are not required if deterministic consistency checks are strong.

#### Deterministic prerequisites before human review

A candidate must first pass:

- paper item ID check;
- paper SHA-256 check;
- JSON path check;
- evidence-span exact re-slice;
- table data SHA check;
- table row/cell/column identity check;
- table-side value recomputation;
- concept term location check;
- place term location check;
- place-role recording;
- template-slot validation;
- deterministic answer recomputation;
- verified/authorized-column check;
- completeness of required provenance fields.

Failure on any mandatory mechanical check means:

```text
status = rejected_pre_review
```

not “send to a human and see.”

#### Reviewer count

For ordinary candidates:

> **1 independent human reviewer is sufficient for acceptance.**

The reviewer must not be the same agent/process that generated the candidate.

The reviewer does **not** need to be blind to the QA itself.

However, the reviewer should inspect the evidence **before seeing agent confidence or self-justification**.

Recommended review order:

1. paper passage;
2. table provenance and deterministic values;
3. QA pair;
4. candidate semantic annotations;
5. agent rationale/confidence last.

#### Mandatory second reviewer

Require a second human reviewer when any of the following applies:

- first reviewer selects `ambiguous`;
- concept relation is soft/related rather than direct;
- geography requires interpretation beyond explicit study area;
- multi-concept QA;
- cross-location comparison with differing spatial granularity;
- scenario mismatch materially affects interpretation;
- time mismatch materially affects interpretation;
- answer depends on a derived statistic rather than a directly reported field;
- paper passage is a background/cited claim rather than the paper's own result;
- first reviewer requests escalation.

Second review should be independent of reviewer 1's disposition where practical.

If reviewers disagree:

```text
status = needs_adjudication
```

A third/adjudicating reviewer resolves the candidate.

#### Human-review checklist

Require explicit judgments for:

- **Paper fidelity** — does the passage actually state the paper-side fact?
- **Table fidelity** — is the table-side fact exactly supported by the recorded cells/computation?
- **Concept validity** — are the two sides sufficiently related for the QA type?
- **Geography validity** — are both locations represented accurately?
- **Temporal validity** — is the wording valid given the periods?
- **Scenario validity** — is scenario mismatch disclosed rather than silently equated?
- **Question validity** — is the question answerable from the recorded evidence?
- **Answer validity** — is the proposed answer correct?
- **No overclaim** — does the QA avoid implying stronger equivalence or causation than supported?
- **Overall disposition** — `accept`, `accept_with_edit`, `ambiguous`, `reject`.

A candidate counts as valid only after:

```text
human_status = accepted
```

or:

```text
human_status = accepted_after_edit
```

with the final edited QA frozen.

---

### 2. Candidate-record fields

Add the fields below to the soft-QA candidate schema.

#### Candidate identity

```text
candidate_id
track
generator_version
generator_model
prompt_hash
generation_timestamp
source_commit
```

#### Paper-side provenance

```text
paper_item_id
paper_sha256
json_path
span_start
span_end
verbatim_passage
claim_or_passage_type
paper_geography
paper_geography_role
paper_time
paper_scenario
paper_concept
```

#### Table-side provenance

```text
unit_id_or_template_id
table_data_sha256
row_ids
column_ids
column_statuses
raw_cell_values
derived_value
derivation_rule_id
concept_family
metric
location
period
scenario
season
statistic
```

#### Soft-link record

```text
qa_type
link_rationale
concept_relation
geography_relation
time_relation
scenario_relation
direction_relation
c_g_t_s_d_audit
unmatched_dimensions
assumptions
```

#### Leakage / generation controls

```text
table_values_visible_to_generator: false
answer_visible_to_generator: false
retrieval_terms
retrieval_source
```

#### Deterministic validation

```text
span_reslice_pass
table_recompute_pass
concept_location_pass
place_location_pass
place_role_recorded
slot_validation_pass
verified_columns_only
pre_review_status
```

#### Human review

```text
reviewer_1_id
reviewer_1_date
paper_fidelity
table_fidelity
concept_validity
geography_validity
temporal_validity
scenario_validity
question_validity
answer_validity
overclaim_check
reviewer_1_disposition

requires_second_review
reviewer_2_id
reviewer_2_disposition
adjudication_status

final_status
final_question
final_answer
edit_history
```

#### Recommended status lifecycle

```text
llm_candidate
→ deterministic_pass
→ human_review
→ accepted
```

Side exits:

```text
rejected_pre_review
needs_second_review
needs_adjudication
rejected_human
accepted_after_edit
```

This is preferable to a single binary validity field.

---

### 3. Agent visibility of unit values

**Definitions only during proposal. Computed values withheld.**

Track C may receive:

- the three unit definitions;
- family-level descriptions;
- allowed QA types;
- source paper;
- provenance schema.

Track C should **not** receive:

- computed table values;
- derived answer values;
- target answer direction;
- previous accepted/rejected answers for the same paper.

Rationale:

If the agent sees table values while deciding which passage to link, it can preferentially choose passages that create an attractive answer.

That introduces post-hoc steering.

The candidate structure should therefore be frozen first.

Only after that may deterministic code populate:

- table-side values;
- derived statistics;
- final answer components.

The authoritative numeric/categorical answer should come from deterministic computation whenever possible, not from the LLM.

---

### 4. Multi-concept templates and unverified variables

**Do not allow verified + unverified mixing.**

Every field that affects:

- retrieval semantics;
- question wording;
- concept interpretation;
- answer computation;
- comparison logic;

must be verified or otherwise explicitly authorized for that semantic role.

An unverified field cannot be used merely as a “query-only” concept.

Reason:

Using an unverified field as a retrieval term already assigns it semantic authority.

Therefore:

> **query-only use is still semantic use.**

If an unverified variable appears useful, it must first go through the existing metadata/concept-governance path.

---

## Scientific risks

### 1. “Soft” becoming unconstrained

The correct interpretation is:

> **semantic compatibility may be judged by a human rather than a deterministic gate, but every factual component still requires exact provenance.**

### 2. Reviewer anchoring

Agent confidence/rationale should be hidden until after evidence-first review.

### 3. Table values steering candidate discovery

Track C must not see computed unit values during proposal.

### 4. Unverified variables contaminating semantics

Even query-only use can silently promote an unverified interpretation.

### 5. LLM-generated answer leakage

The agent may propose semantic structure, but deterministic table computation should provide authoritative numeric/categorical answers whenever possible.

### 6. Human review becoming superficial

A reviewer must inspect both source sides, not only the final QA wording.

---

## Required actions

### Human-review protocol

1. Add a deterministic `pre_review_check` stage.
2. Only candidates passing it reach human review.
3. One independent human reviewer is sufficient by default.
4. Add mandatory second review for ambiguous/high-risk cases.
5. Add adjudication for reviewer disagreement.
6. Hide agent confidence/rationale until after evidence-first judgment.
7. Freeze the final edited QA after review.

### Agent visibility

8. Track C receives unit definitions, family descriptions, permitted QA types, paper content, and provenance schema.
9. Track C does **not** receive computed table values, derived answer, target answer direction, or prior accepted/rejected answers for the same paper.
10. After candidate structure is frozen, deterministic table computation may populate the answer side.

### Variable governance

11. Every semantic/retrieval/answer/comparison slot must use an authorized/verified field.
12. No unverified field may be used only as a query term.
13. Useful unresolved variables must first pass metadata/concept governance.

### Audit preservation

14. Keep C/G/T/S/D judgments on every candidate.
15. Do not use them as the sole acceptance gate.
16. Record unmatched dimensions explicitly.
17. Preserve all source spans and raw table values needed for manual inspection.
18. No LLM output may alter concept-map status, column status, or deterministic compatibility rules.

---

## Decisions for Kaiyuan or mentor

| Question | Ruling |
|---|---|
| One human reviewer enough by default? | **Yes, after deterministic pre-checks** |
| Two reviewers for every QA? | **No** |
| Mandatory second reviewer for ambiguous/high-risk cases? | **Yes** |
| Human reviewer blind to QA itself? | **No** |
| Human reviewer initially blind to agent confidence/rationale? | **Yes, preferred** |
| Deterministic checks before human review? | **Required** |
| Agent may see unit definitions? | **Yes** |
| Agent may see computed table values during proposal? | **No** |
| Reveal values after candidate structure freezes? | **Yes** |
| Agent may generate final authoritative numeric answer? | **No; deterministic computation should** |
| Unverified column allowed as query-only term? | **No** |
| Multi-concept QA allowed? | **Yes, if every semantic slot is authorized** |
| C/G/T/S/D still recorded? | **Yes** |
| C/G/T/S/D remain acceptance gate? | **No** |
| LLM output may modify concept map or column status? | **No** |

---

## Next bounded objective

Before large-scale Track C or Track D generation, define and freeze:

> **Soft-QA Candidate Schema + Review Protocol**

### Track C

Track C may:

- read each frozen place-candidate paper in full;
- receive the three unit definitions and family-level descriptions;
- receive permitted QA types;
- propose passage → linked unit → QA type → one example QA pair.

Track C must not see computed table values during proposal.

### Track D

Track D may define table-grounded templates with slots such as:

```text
concept
multi_concept
location
period
scenario
season
statistic
```

Requirements:

- every slot value comes only from verified/authorized semantics;
- deterministic table computation produces the answer;
- template slots may drive corpus retrieval;
- Track C-style agent may link passages afterward;
- a separate unit object is not required if the template itself carries complete table provenance.

The mentor-approved cross-location comparison can be represented as a candidate QA type, provided both table and paper facts are independently attested and location semantics are explicit.

---

## Acceptance criteria

Before a Track C/D candidate can count as a valid benchmark QA:

1. Every candidate begins as `llm_candidate`.
2. Paper SHA is pinned.
3. Paper evidence span re-slices exactly.
4. Table-data SHA is pinned.
5. All table columns are authorized for their semantic role.
6. Raw table cells are recorded.
7. Derived table values are reproducible.
8. Derivation rule is versioned.
9. Generator did not see table answer/value during proposal.
10. Generator input provenance is recorded.
11. Concept term is locatable in the relevant source.
12. Place term is locatable where required.
13. Place role is recorded.
14. C/G/T/S/D judgments are retained for audit.
15. C/G/T/S/D are not silently converted back into a hard acceptance gate.
16. Unmatched dimensions are explicitly disclosed.
17. No model output modifies concept-map status.
18. No model output modifies column status.
19. Deterministic checks pass before human review.
20. At least one independent human reviewer approves ordinary candidates.
21. High-risk/ambiguous candidates receive a second review.
22. Reviewer examines evidence before agent confidence/rationale.
23. Paper fidelity is explicitly judged.
24. Table fidelity is explicitly judged.
25. Concept validity is explicitly judged.
26. Geography validity is explicitly judged.
27. Temporal validity is explicitly judged.
28. Scenario validity is explicitly judged.
29. Question validity is explicitly judged.
30. Answer validity is explicitly judged.
31. Overclaim is explicitly checked.
32. Reviewer edits are preserved in edit history.
33. Final accepted QA is frozen separately from the original LLM proposal.
34. No QA becomes benchmark-valid solely because the LLM proposed it.

---

## Do not do yet

Do not let Track C see computed unit values during link proposal.

Do not let the agent optimize for an attractive table answer.

Do not allow an unverified column into a multi-concept question merely because it is “retrieval only.”

Do not use agent confidence as a substitute for human review.

Do not allow a reviewer to approve only from the final QA without inspecting both source records.

Do not discard C/G/T/S/D; they remain important audit evidence.

Do not interpret “soft-constrained” as “unconstrained.”

Do not let model-proposed links alter the concept map, column statuses, or deterministic compatibility rules.

Do not make the final answer an LLM-authored numerical fact when the answer can be computed from the table.

The mentor's direction changes **where judgment happens**, not the requirement for traceability:

> **LLM proposes the semantic connection; deterministic code verifies the source mechanics; humans decide whether the cross-modal QA is scientifically acceptable.**

That is the guardrail model for Tracks C and D.
