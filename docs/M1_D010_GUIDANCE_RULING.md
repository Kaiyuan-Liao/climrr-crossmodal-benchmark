# ClimRR Cross-Modal Benchmark — D-010 / M1-WP3 GUIDANCE Ruling

**Milestone:** M1 — Data Grounding and Metadata Audit  
**Decision scope:** D-010 / M1 resolution-path revision  
**GUIDANCE status:** PASS WITH ACTIONS  
**Authorized next work:** M1-WP3 — Pilot-subset semantic validation through 2–3 row-centered candidate examples

> This ruling adapts the M1 resolution path after the 2026-09-10 mentor meeting. It does **not** weaken the definition of `verified_from_dictionary`, and it does **not** authorize M2/M3 scientific work, literature processing, semantic bridges, or QA generation.

---

## Gate status

**PASS WITH ACTIONS**

The direction of D-010 is approved, with one refinement: `inferred_candidate` may be introduced as an explicitly provisional semantic status, and bounded example construction may begin, but **mentor review must validate the specific interpretations embodied in an example before any participating field becomes `owner_confirmed`**.

This does **not** reopen D-009's strict definition of `verified_from_dictionary`.

```text
verified_from_dictionary
        ≠
owner_confirmed
        ≠
inferred_candidate
```

---

## Current-stage assessment

The premise behind the original M1-WP2 resolution strategy has materially changed.

D-009 assumed unresolved semantics might later be settled by mentor/data-owner confirmation, an export/source-generation specification, or another authoritative ClimRR mapping artifact. The 2026-09-10 mentor meeting established that no fuller dictionary, assembly document/script, release note, or equivalent authoritative mapping exists, and produced no per-column answers to Q1–Q18.

Instead, the project direction changed: use a reliable or reasonably explainable subset, reason about unclear columns carefully, construct examples, and bring those examples back for review.

The M1 problem is now:

> **How can the project build a scientifically auditable pilot from a deliberately small subset when some field semantics can only be reasoned about, then use concrete examples to obtain owner validation?**

This is acceptable provided fact, inference, and owner confirmation remain explicitly separated.

---

## Evidence check

### 1. `inferred_candidate`

**Approved, with strict boundaries.**

`inferred_candidate` means:

> **A reasoned interpretation judged plausible enough to test in an example, but not established as source truth.**

Each record must carry:

- exact column index and name;
- exact raw value(s) used;
- proposed semantic interpretation;
- proposed unit, scenario, horizon, season, etc. only where inferred;
- relevant dictionary spans;
- column-name evidence;
- value-pattern evidence where relevant;
- explicit reasoning;
- unresolved alternatives or ambiguities;
- provenance status = `inferred_candidate`;
- an explicit statement that it is not verified or owner-confirmed.

The existing candidate maps remain navigation aids only. An `inferred_candidate` requires a **column-specific reasoning record**, not merely membership in an EXECUTOR-authored mapping.

### 2. Mentor sign-off on concrete examples

**Approved as a valid form of owner confirmation, with semantic granularity.**

Mentor/data-owner confirmation is an accepted authoritative route under D-009. Concrete examples are a strong way to obtain it because the mentor sees the interpretation in context.

However:

> **Mentor sign-off promotes only the specific semantic interpretations that are clearly confirmed.**

A broad response such as “Yes, this is the kind of example I want” must not automatically confirm every embedded field assumption.

Resolution records should distinguish confirmed from unconfirmed semantics explicitly.

### 3. M1 gate criterion 1 on the pilot subset

**Approved.**

M1 criterion 1 should be evaluated on **every field selected for the pilot**, not on all 275 columns.

M1 may eventually pass with a small pilot subset whose fields satisfy the metadata requirements while all other columns remain explicitly unresolved / undocumented / unused.

The scope may narrow; the rigor for the selected subset must not.

### 4. Early hand-worked examples

**Approved as bounded M1-WP3 validation work.**

This is a deliberate early use of an M2-style artifact, justified because examples are now the instrument required to resolve M1 metadata with the owner.

These are not canonical M2 phenomenon records. They are:

> **row-centered candidate event prototypes for semantic validation**

until the mentor confirms both the row/event grain and the relevant field interpretations.

“Row = event” remains an assumption under review.

---

## Scientific risks

### 1. AI reasoning becoming de facto ground truth

AI may formulate candidate semantics from available evidence; it may not convert ambiguity into fact. `inferred_candidate` must remain visibly weaker than `owner_confirmed` and `verified_from_dictionary`.

### 2. Confirmation by impression rather than semantics

Broad mentor approval could be over-read. The project must record **what exactly was confirmed**.

### 3. “Row = event” may be conceptually wrong

The exact scientific meaning of a CSV row as an “event” is not yet established. Until confirmed, avoid wording that implies an observed climate event.

### 4. Cherry-picking easy-to-narrate fields

Pilot fields should be selected because they are scientifically relevant, sufficiently interpretable, provenance-aware, and compatible with later literature matching—not merely because they are easy to narrate.

### 5. Example construction drifting into M3

The example step must not begin climate phenomenon mining, aggregation, salience/magnitude threshold design, or benchmark-ready claim construction.

---

## Required actions

1. **Approve D-010 with this ruling incorporated.**
2. Add `inferred_candidate` as a distinct provisional status below `verified_from_dictionary` and `owner_confirmed`.
3. Require every `inferred_candidate` to include evidence, reasoning, explicit assumptions, and unresolved alternatives.
4. **Keep `verified_from_dictionary` unchanged.**
5. Define mentor promotion at the level of **specific confirmed semantics**, not blanket example approval.
6. Build only **2–3 row-centered candidate examples** for mentor review.
7. Keep the pilot subset deliberately small.
8. Preserve all non-selected columns in their existing unresolved/undocumented state.

Do not expend effort trying to solve all 275 columns.

---

## Decisions for Kaiyuan or mentor

### GUIDANCE rulings

| Question | Ruling |
|---|---|
| `inferred_candidate` acceptable? | **Yes** |
| Can it be presented as verified? | **No** |
| Mentor sign-off on examples as owner confirmation? | **Yes, only for semantics explicitly confirmed** |
| M1 criterion 1 on pilot subset only? | **Yes** |
| Must all 275 columns be resolved? | **No** |
| Early example construction during M1? | **Yes, as bounded M1-WP3** |
| Is “row = event” established now? | **No — assumption pending mentor confirmation** |

### Kaiyuan

At the next mentor review, preserve feedback as accurately as possible and distinguish explicit confirmation, correction, broad approval, and unanswered assumptions.

### Mentor

The next mentor interaction should primarily answer through the examples:

1. **Is one CSV row the correct unit for what she means by an “event”?**
2. **Are the selected field interpretations correct?**
3. **Which assumptions in each example does she endorse or reject?**
4. **Are these the kinds of table-side records she expects to connect to literature?**

There is no need to re-present all Q1–Q18 abstractly unless an example exposes one of them as necessary.

---

## Next bounded objective

**Authorize M1-WP3 — Pilot-subset semantic validation through 2–3 row-centered candidate examples.**

The goal is **not** to discover climate phenomena yet. The goal is to test whether a small set of table fields can be converted into scientifically understandable, provenance-preserving records that the mentor recognizes as the intended basis for later literature connection.

### Each example may contain

**Provenance**
- CSV SHA-256;
- exact row index / stable row identifier;
- exact column indices and names;
- raw values exactly as read.

**Semantic fields**
- proposed field meaning;
- unit, season, time horizon, scenario where supported or inferred;
- provenance status for each interpretation: `verified_from_dictionary`, `owner_confirmed`, or `inferred_candidate`.

**Reasoning**
- dictionary spans used;
- naming-pattern evidence;
- value-pattern evidence where relevant;
- concise rationale for each inferred interpretation.

**Assumptions**
- whether one row is the intended “event” unit;
- any stem-to-section mapping used;
- any inferred unit/scenario/horizon;
- any geographic interpretation not established.

**Presentation**
- a concise mentor-readable candidate event description generated **from the structured record**;
- any description depending on inferred semantics must be visibly labeled provisional.

### Each example may not contain

- geographic aggregation across rows;
- county/state/region aggregation;
- magnitude or salience thresholds;
- selection of “interesting” climate changes using new quantitative criteria;
- unsupported sentinel/missing-value interpretations;
- literature passages or claims;
- embeddings;
- semantic bridge scores;
- table-to-paper links;
- QA questions;
- wildfire-occurrence claims inferred from Fire Weather Index;
- treatment of modeled historical values as observations.

---

## Acceptance criteria

M1-WP3 is ready for review when:

1. A **small, explicit pilot subset** is selected with a rationale based on scientific relevance and interpretability.
2. Every selected field has one of `verified_from_dictionary`, `owner_confirmed`, or `inferred_candidate`.
3. Every `inferred_candidate` includes exact supporting evidence, reasoning, explicit assumptions, and unresolved alternatives where applicable.
4. Exactly **2–3 real-row prototype records** are produced.
5. Every record preserves complete provenance back to raw row/column values.
6. Raw facts, interpreted semantics, and natural-language presentation are clearly separated.
7. “One row = one event” is presented as an **assumption under review**, not as an established dataset fact.
8. No aggregation, thresholding, phenomenon mining, literature processing, bridge construction, or QA generation occurs.
9. The examples are compact enough for mentor review and designed to elicit **specific corrections or confirmations**.
10. After mentor feedback, every promotion to `owner_confirmed` can be tied to a resolution record stating exactly what was confirmed.
11. The resulting evidence is sufficient to judge whether the pilot fields satisfy the original M1 metadata requirements: meaning, unit where applicable, time horizon, scenario, missing-value policy, and provenance status.

If those conditions hold for the selected pilot subset, M1 may then be brought to its milestone gate even while most of the 275 columns remain explicitly unresolved.

---

## Do not do yet

Do not treat D-010 as permission to broadly AI-label the table.

Do not infer semantics for all 275 columns.

Do not promote `inferred_candidate` based on model confidence, consistency, naming plausibility, or value-pattern plausibility alone.

Do not call a row a confirmed “event” until the mentor validates that grain.

Do not start M2 canonical-schema design beyond the minimum fields needed to represent these temporary examples.

Do not begin deterministic phenomenon extraction, geographic aggregation, salience/magnitude criteria, humid-heat/FWI pilot mining, literature ingestion, literature claim extraction, semantic matching, bridge validation, or QA generation.

The bounded purpose of the next work is:

> **Use a few transparent examples to turn abstract metadata ambiguity into specific mentor-confirmable decisions.**
