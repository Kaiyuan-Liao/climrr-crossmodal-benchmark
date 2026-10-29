# ClimRR Cross-Modal Benchmark — Benchmark Objective Re-Anchor GUIDANCE Ruling

**Decision context:** Mentor direction of 2026-10-29 redefining the benchmark objective  
**Date:** 2026-10-29  
**Applies to:** general-knowledge climate QA benchmark construction using table patterns + literature evidence  
**GUIDANCE status:** PASS WITH ACTIONS

> The benchmark is no longer centered on reconstructing a hidden table/paper linkage. It should test whether an LLM can answer general climate-science questions from prior knowledge, while the hidden table and literature corpus provide a fully auditable reference answer and provenance trail.

---

## Gate status

**PASS WITH ACTIONS — benchmark objective re-anchored**

The mentor's 2026-10-29 direction supersedes the previous soft-QA framing.

The benchmark-validity question is now:

> **Can a question be answered from general climate-science knowledge, without exposing the table or literature, while its reference answer remains fully grounded in deterministic table patterns and auditable literature evidence?**

Rulings:

1. **Benchmark-valid item gate:** accept the proposed direction, with an explicit **source-independent answerability** requirement.
2. **Single-source literature statements:** allowed only when explicitly marked as single-source and not presented as consensus.
3. **Above-state geography:** use a single, cited, version-pinned climate-region scheme; NCA regions are acceptable with a deterministic tracked state→region map.
4. **Schema guardrails:** add source-independent answerability, evidence strength, consensus status, reference-answer decomposition, grading tolerance, leakage checks, and robustness fields.
5. **Magnitude classes:** relative terciles are acceptable only as disclosed relative descriptors, never as absolute thresholds or the sole answer key.

A ~10-item pilot is authorized.

---

## Current-stage assessment

The previous item design was too close to:

> paper fact + table value → specific cross-modal question.

The new design should be:

> **general climate-science question → reference answer assembled from independently auditable table patterns + literature-backed mechanisms/interpretations.**

The hidden evidence serves three roles:

- **table:** empirical pattern, direction, ranking, contrast, horizon, scenario;
- **literature:** mechanisms, drivers, caveats, scientific interpretation;
- **human review:** whether the item is fair, general enough, and answerable without source access.

The prompt itself should not reveal that it came from ClimRR or the literature corpus.

A good item may look like:

> “Why might fire-weather risk increase more strongly in some western U.S. regions later this century, and what broad spatial pattern would you expect?”

rather than:

> “According to this table, California's FWI changes from X to Y…”

The first tests climate reasoning. The second tests hidden-source access.

---

## Evidence check

### 1. Re-anchored benchmark-validity gate

A benchmark-valid item should require all six conditions below.

#### A. Source-independent prompt

The prompt must:

- name no table;
- name no paper;
- require no hidden row/column identifier;
- require no obscure exact value only available in the source;
- be reasonably answerable by a capable LLM from general climate-science knowledge.

Add:

```text
source_independent_answerability:
  yes | borderline | no
```

Only `yes` can be benchmark-valid.

#### B. Deterministic table-side reference facts

Every table-side fact in the reference answer must trace to:

- approved columns;
- explicit aggregation rule;
- recorded rows/states/regions;
- period;
- scenario;
- season;
- statistic;
- computed value/range/rank;
- code/rule version.

No LLM inference may create the table-side fact.

#### C. Provenance-backed literature statements

Every mechanism, driver, consensus statement, or caveat must point to:

- paper IDs;
- hashes;
- exact passages;
- extracted statement;
- evidence-strength designation.

#### D. Explicit evidence strength

Use labels such as:

```text
multi_source_supported
single_source_supported
background_consensus
caveat
```

Do not present them with equal epistemic strength.

#### E. Reference-answer decomposition

Store separately:

```text
table_pattern:
  ...

literature_interpretation:
  ...

integrated_reference_answer:
  ...
```

A deterministic table pattern is not itself a mechanism.

#### F. Human acceptance

For the pilot, a valid item requires:

- Kaiyuan review;
- mentor review;
- final frozen prompt/reference/rubric after edits.

Mentor acceptance is required for every pilot item.

---

### 2. Single-source literature statements

**Allowed, with restrictions.**

A single-source statement may appear if:

- marked `single_source_supported`;
- not phrased as consensus;
- not required as an obscure niche fact unless the prompt genuinely calls for it;
- preferably used as a caveat, example, or secondary explanation.

For a core mechanism sentence, prefer:

> **≥2 independent papers**

or one explicit review/synthesis source.

Standing rule:

> **Core mechanism/consensus claims: ≥2 independent sources, or one explicit review/synthesis source. Single-source statements may appear only when labeled and conservatively framed.**

Two papers citing the same underlying study do not automatically count as independent evidence.

---

### 3. Above-state region definition

**NCA climate regions are acceptable.**

Use one regionalization scheme for the pilot.

Required metadata:

```text
region_scheme_id
region_scheme_name
region_scheme_version
source_citation
state_to_region_map
map_sha256
```

The map must be:

- repository-tracked;
- version-pinned;
- deterministic;
- sourced from an authoritative NCA artifact;
- fixed before inspecting desirable benchmark outcomes.

Do not hand-edit regional membership to improve patterns.

For multi-state sets that are not official regions, record:

```text
geography_type: multi_state_set
```

Do not call them climate regions.

---

### 4. Additional item-schema guardrails

#### Benchmark intent

```text
capability_tested
use_case_level
source_independent_answerability
expected_knowledge_level
```

Suggested knowledge levels:

```text
general_climate_science
specialist_climate_science
```

Avoid items requiring recall of an obscure study.

#### Evidence decomposition

```text
reference_components:
  table_patterns: [...]
  literature_mechanisms: [...]
  literature_caveats: [...]
```

#### Literature evidence strength

```text
evidence_strength:
  multi_source_supported
  review_supported
  single_source_supported
```

Also add:

```text
source_independence_note
```

#### Generalization guardrail

Add:

```text
reference_scope
```

Examples:

```text
this_table_pattern_only
regional_climate_expectation
broad_consensus
single_study_observation
```

#### Grading tolerance

Add:

```text
required_points
acceptable_variants
optional_points
disallowed_claims
fatal_errors
```

#### Source leakage check

Add:

```text
source_leakage_check
```

Check that the prompt does not mention:

- ClimRR;
- row/column names;
- paper titles/authors;
- hidden exact source values;
- “according to the dataset/paper”.

#### Pattern robustness

Add:

```text
pattern_support_n
pattern_robustness
```

Examples:

```text
all_states_same_direction
majority_same_direction
mixed
```

---

### 5. Magnitude-class rule

Do **not** use tercile classes as the primary scientific magnitude claim.

Relative terciles:

```text
small
moderate
large
```

are acceptable only if explicitly defined as relative to a comparison population.

Example:

```text
magnitude_class: large
magnitude_definition:
  upper tercile among U.S. states for
  family=X, season=Y, horizon=Z, scenario=S
```

Do not write:

> “California experiences a large increase”

without qualification.

Prefer:

> “California is in the upper third of states for the projected increase…”

or:

> “The increase is relatively large compared with other U.S. states under the same season, horizon, and scenario.”

For the pilot, store all three:

```text
direction
computed_value_or_range
relative_rank_or_tercile
```

Do not use terciles when:

- comparison population is small;
- many states tie;
- the distribution is degenerate;
- weighting choices materially change the grouping;
- missing states materially change cut points.

In those cases, use direction + computed range/rank.

Standing ruling:

> **Relative terciles are acceptable as a disclosed relative descriptor—not as an absolute magnitude threshold and not as the sole answer key.**

---

## Scientific risks

1. **Testing hidden-source recall instead of general knowledge.** Questions must remain answerable without the hidden sources.
2. **Reference answer becoming more specific than the prompt warrants.** Do not require exact values unless asked.
3. **Table pattern mistaken for consensus.** A ClimRR pattern is not automatically universal climate knowledge.
4. **Synthetic consensus from literature aggregation.** Two papers are not automatically consensus.
5. **Relative magnitude sounding absolute.** Prefer “upper-third” or “relatively larger.”
6. **Benchmark trivia.** Avoid paper-specific wording and obscure numerical facts.

---

## Required actions

1. Record the 2026-10-22 / 2026-10-29 mentor direction as superseding the previous soft-QA objective.
2. Rewrite benchmark validity around source-independent answerability, deterministic table evidence, literature-supported interpretation, and human acceptance.
3. Add `source_independent_answerability`.
4. Add decomposed reference-answer components.
5. Add literature evidence-strength classification.
6. Require ≥2 independent sources or a review/synthesis for core mechanism/consensus claims.
7. Allow single-source statements only when explicitly labeled.
8. Adopt one pinned NCA regionalization for the pilot.
9. Track the authoritative state→region map and SHA.
10. Distinguish official climate regions from arbitrary multi-state sets.
11. Add grading fields: required points, acceptable variants, optional points, disallowed claims, fatal errors.
12. Add a source-leakage check.
13. Add pattern-support/robustness fields.
14. Preserve C/G/T/S/D only as audit metadata.
15. Keep table-pattern extraction deterministic.
16. Keep literature-statement extraction semantic but fully span-provenanced.
17. Require Kaiyuan + mentor acceptance for all ~10 pilot items.
18. Store direction, numeric range/value, and relative magnitude separately.
19. If using terciles, define them explicitly as relative U.S.-state terciles under the same family/season/horizon/scenario.
20. Never present terciles as absolute scientific thresholds.

---

## Decisions for Kaiyuan or mentor

| Question | Ruling |
|---|---|
| Proposed benchmark-valid gate sufficient? | **Yes, with source-independent answerability and evidence-strength additions** |
| Prompt may name the data/papers? | **No** |
| Exact hidden values required for answer? | **Generally no** |
| Table facts deterministic? | **Required** |
| Literature mechanisms provenance-backed? | **Required** |
| Human acceptance? | **Required** |
| Pilot review by Kaiyuan + mentor? | **Yes** |
| Single-source literature statement allowed? | **Yes, if explicitly marked and not framed as consensus** |
| Core mechanism from one ordinary paper? | **Prefer no** |
| One review/synthesis source sufficient for a core mechanism? | **Yes, if clearly a synthesis** |
| NCA climate regions acceptable? | **Yes** |
| State→region map tracked/cited/versioned? | **Required** |
| Ad hoc region membership allowed? | **No** |
| Additional schema guardrails? | **Yes — answerability, evidence strength, scope, grading tolerance, leakage, robustness** |
| Relative terciles allowed? | **Yes, as disclosed relative descriptors** |
| Treat “large” as absolute threshold? | **No** |
| Store underlying value/range alongside tercile? | **Required** |
| Use tercile as sole correctness target? | **No** |
| ~10-item pilot now? | **Authorized** |
| QA generation generally unrestricted? | **No — pilot only under this gate** |

---

## Next bounded objective

Proceed with:

> **Benchmark Objective Pilot — ~10 General-Knowledge Climate QA Items**

The pilot should span the proposed use-case ladder where evidence allows:

1. hazard-pattern identification;
2. mechanism;
3. pattern + mechanism;
4. regional comparison;
5. projection–literature consistency;
6. compound hazards;
7. scenario / uncertainty;
8. exposure implications.

No quota is required.

Prefer distinct reasoning modes over forcing one item per category.

### Table side

For each candidate, extract state / multi-state / NCA-region patterns deterministically and record:

- concept family;
- season;
- horizon;
- scenario;
- statistic;
- direction;
- numeric range/value;
- rank;
- relative magnitude class if used;
- pattern support.

### Literature side

Aggregate statements into:

```text
mechanism
drivers
consensus
caveats
```

with each sentence tagged by evidence strength and paper provenance.

Do not synthesize multi-paper statements without preserving which paper supports which clause.

### Item construction

Use:

```text
prompt
reasoning_modalities
relationships
evidence_needed
capability_tested
desired_output
reference_answer
rubric
guardrails
provenance
review_status
```

plus the additional fields in this ruling.

The prompt must stand alone as a normal climate-science question.

---

## Acceptance criteria

An item is benchmark-valid in the pilot only if:

1. The prompt names no hidden source.
2. The prompt is answerable without access to the table or papers.
3. It does not require obscure hidden exact values.
4. All table-side factual claims are deterministic.
5. All table columns used are authorized.
6. Table aggregation rules are frozen.
7. Geography scheme is pinned.
8. Every literature-derived sentence has exact provenance.
9. Core mechanisms have ≥2 independent sources or a synthesis source.
10. Single-source statements are labeled.
11. Evidence strength is explicit.
12. Table pattern and literature interpretation are stored separately.
13. Integrated reference answer does not overstate either.
14. Scenario relations are scientifically correct.
15. RCP8.5 may be described as a high-emissions scenario, not as the only future.
16. Relative magnitude labels are explicitly comparative.
17. Underlying computed values/ranges are retained.
18. Tercile categories are not treated as physical thresholds.
19. Prompt contains no source leakage.
20. Required rubric points are general-knowledge appropriate.
21. Acceptable answer variants are listed.
22. Fatal scientific errors are listed.
23. C/G/T/S/D audit metadata is retained.
24. Kaiyuan accepts the item.
25. Mentor accepts the item.
26. Final prompt/reference/rubric are frozen.
27. No item is accepted solely because an LLM generated it.

---

## Do not do yet

Do not ask questions whose correct answer depends on seeing hidden ClimRR values.

Do not mention “according to ClimRR,” “according to the paper,” or source identifiers in the prompt.

Do not require exact decimal values unless the mentor explicitly changes the use case.

Do not present a table-derived pattern as universal climate consensus.

Do not turn two aligned papers into “scientific consensus” without checking independence.

Do not treat a single paper's mechanism as general knowledge unless clearly labeled.

Do not invent climate regions.

Do not use ad hoc state groupings and call them NCA regions.

Do not call an upper-tercile result simply “large” without saying it is relative.

Do not use relative terciles as the only reference truth.

Do not revive strict claim-level C/G/T/S/D eligibility as the benchmark-validity gate.

Do not remove C/G/T/S/D from provenance.

The benchmark should now test:

> **whether an LLM knows and can reason about robust climate patterns, mechanisms, regional contrasts, and uncertainties that are independently supported by the table and scientific literature — without ever seeing those hidden sources.**

That is the objective for judging the ~10-item mentor pilot.
