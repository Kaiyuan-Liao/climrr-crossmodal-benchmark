# ClimRR Cross-Modal Benchmark — M5-WP1 Review and Follow-on GUIDANCE Rulings

**Reviewed package:** M5-WP1 — Deterministic negative-case compatibility validation  
**Follow-on work:** M4-WP1b blind second reading; M4-WP2 relevance-guided candidate generation  
**GUIDANCE status:** PASS WITH ACTIONS

> M5-WP1 passes only as machinery validation. Positive-pair work requires an explicit concept ontology, independent literature validation, and a distinction between candidate eligibility and accepted bridge evidence.

---

## Gate status

**PASS WITH ACTIONS**

M5-WP1 **passes as machinery validation only**.

The compatibility engine successfully freezes inputs, evaluates all 81 claim–prototype pairs, records five deterministic judgments with rule IDs and compared values, preserves `compatible / incompatible / not_evaluable`, and exercises a valid synthetic positive path without asserting that the real set must contain zero positives.

The observed zero is structurally unsurprising under the current rules:

- concept has no approved mapping for all 81 pairs;
- climate scenario is unknown for all 27 claims.

Rulings:

1. **P-STATE-1 time correction: authorized**, with versioning and provenance.
2. **Tracked deterministic concept map: authorized in principle**, with family-vs-metric specificity preserved.
3. **Unknown scenario may be tolerated for candidate-bridge eligibility**, but not for unqualified scenario-specific support.
4. **M4-WP1b: authorized.**
5. **M4-WP2 retrieval design: conditionally authorized**, with boundary-aware lexical matching and semantic inspection deferred until WP1b closes.

---

## Current-stage assessment

The important result of M5-WP1 is not that the literature “failed to match.”

It is:

> **The deterministic machinery works, and the current semantic interface is too incomplete to permit real positive pairs.**

The matrix exposed the exact interface gaps:

- concept mapping is absent;
- scenario is unknown on the literature side;
- P-STATE-1 lacks explicit year windows;
- direction cannot be evaluated until concept comparability exists.

That is a successful negative-case machinery validation.

---

## Evidence check

### 1. P-STATE-1 temporal defect

**Correction authorized.**

P-STATE-1 currently stores only `Historical` / `End-Century` without explicit windows. If the same metadata chain directly supports `1995–2004` and `2085–2094`, those windows may be added as a **versioned provenance correction**.

Requirements:

- cite exact dictionary spans;
- inherit the same epistemic status as the underlying interpretation;
- change no ClimRR numeric value;
- log the amendment;
- hash/version the rebuilt prototype.

Do **not** rewrite the frozen M5-WP1 input. The existing M5-WP1 result remains valid for the prototype version it actually used.

### 2. Concept mapping procedure

**Authorized with an important refinement.**

Create a tracked mapping artifact such as:

```text
data/metadata/concept_map.yaml
```

Each entry should include at least:

```text
canonical_id
accepted_surface_terms
source_type
source_reference
source_span
decision_id
date
status
```

A claim concept may match a canonical concept only by exact membership in an approved surface-term set.

However, broad vocabulary must **not** silently map to a narrower metric.

For example:

```text
"heat index" → heatindex_days_above_105F
```

is too strong unless the claim itself states the threshold/metric.

Likewise, `FWI` may identify the **Fire Weather Index family** without specifying a seasonal statistic, average, percentile, or change quantity.

Therefore distinguish:

- **concept family** — e.g. `heat_index`, `fire_weather_index`;
- **specific metric / measure** — e.g. `days_above_105F`, seasonal FWI statistic, percent change.

**COORDINATOR may approve mechanically source-backed lexical aliases** without another GUIDANCE round only when the alias does not broaden, narrow, or reinterpret scientific meaning. Scientific synonymy, hierarchy, threshold interpretation, or family→metric narrowing must return to GUIDANCE or the mentor.

### 3. Scenario rule and bridge eligibility

The proposed relaxation is acceptable only if **bridge-eligible means candidate bridge**, not validated supporting bridge.

A pair may advance for bridge review when:

- concept = `compatible`;
- geography = `compatible`;
- no dimension is `incompatible`;
- time may be `compatible` or `not_evaluable`;
- scenario may be `compatible` or `not_evaluable`;
- direction may be `compatible` or `not_evaluable`.

But a scenario-specific ClimRR prototype cannot receive an unqualified `supporting` relation from a claim whose scenario is unknown.

Unknown scenario/time must remain visible in the final M5 relation, e.g. `related_insufficient` or `uncertain`.

### 4. M4-WP1b

**Authorized.**

Run a blind second reading over all ten WP1 papers.

The second reader/session must not receive:

- prototypes;
- first-reader claims or scope labels;
- M5 compatibility results;
- expected outcomes.

It may receive:

- the ten frozen corpus items;
- extraction rubric/schema;
- evidence-location rules.

Freeze the independent result before comparison/adjudication.

### 5. M4-WP2 retrieval rule

**Directionally approved, with two changes.**

Use:

```text
approved concept terms
+
approved prototype place terms
→ deterministic lexical scan
→ concept-hit AND place-hit filter
→ deduplicate
→ stable LIT-ID ordering
→ first 12
→ freeze
→ semantic inspection later
```

Required changes:

1. **Use boundary-aware lexical matching**, not unrestricted substring matching.
2. **Use only explicitly approved place terms**; do not silently expand `California→CA`, `Oklahoma→OK`, or similar aliases.

Every retrieval hit should record item ID, JSON path, matched term, term class, and exact character span.

---

## Scientific risks

### 1. Family-to-metric collapse

A paper mentioning `heat index` does not necessarily discuss `days above 105°F`.

The ontology must preserve that difference.

### 2. “No contradiction” becoming “support”

A pair with concept/geography compatible but scenario `not_evaluable` is not automatically supporting evidence for a scenario-specific table phenomenon.

### 3. Retrieval becoming semantic logic

M4-WP2 retrieval asks **which papers should be inspected**. M5 decides **what relation an extracted claim has to the table phenomenon**. These must remain separate.

### 4. Geographic lexical hits are only candidate signals

A paper mentioning California is not necessarily about a California phenomenon. Structured claim extraction must establish actual geography.

### 5. Independent-reader contamination

If WP1b sees prototypes, first-pass claims, or M5 results before freezing its own extraction, independence is lost.

### 6. Prototype correction rewriting history

Corrected P-STATE-1 must be a new version; old M5-WP1 inputs remain immutable.

---

## Required actions

1. Record M5-WP1 as **PASS WITH ACTIONS — machinery validation only**.
2. Preserve the original frozen M5-WP1 inputs and matrix unchanged.
3. Correct P-STATE-1 in a new version with exact metadata provenance.
4. Introduce `concept_map.yaml`.
5. Separate concept family from metric specificity where needed.
6. Let COORDINATOR approve only mechanical source-backed lexical aliases.
7. Escalate synonymy/equivalence/hierarchy/specificity decisions.
8. Define separately:
   - `candidate_bridge_eligible`;
   - final M5 relation.
9. Candidate eligibility may tolerate `not_evaluable` time/scenario/direction, but concept and geography must positively match and no dimension may be incompatible.
10. Preserve unknown scenario/time explicitly in the final relation.
11. Execute M4-WP1b blind.
12. Preserve both independent readings plus adjudication.
13. Use boundary-aware lexical matching in M4-WP2.
14. Record exact retrieval hit provenance.
15. Deduplicate before the 12-item cap.
16. Freeze candidate IDs before semantic reading.
17. Do not begin semantic reading of WP2 candidates until WP1b closes without materially invalidating the premise for relevance-guided sampling.

---

## Decisions for Kaiyuan or mentor

| Question | Ruling |
|---|---|
| M5-WP1 gate | **PASS WITH ACTIONS — machinery validation only** |
| P-STATE-1 year-window correction | **Authorized as versioned provenance correction** |
| Rewrite old frozen M5-WP1 inputs | **No** |
| `concept_map.yaml` | **Authorized** |
| Exact source-backed lexical aliases | **COORDINATOR may approve** |
| Scientific synonyms/equivalences | **Require GUIDANCE/mentor** |
| `"heat index"` → threshold-specific metric | **Not by that phrase alone** |
| Concept family vs metric distinction | **Required** |
| Unknown scenario allowed for candidate eligibility | **Yes** |
| Unknown scenario allowed for unqualified scenario-specific support | **No** |
| M4-WP1b | **Authorized** |
| M4-WP2 design | **Conditionally authorized** |
| Unrestricted substring matching | **Rejected** |
| Boundary-aware lexical matching | **Required** |
| First 12 qualifying items by LIT ID | **Approved** |
| WP2 representative of corpus | **No — candidate-generation only** |
| QA generation | **Still not authorized** |

A useful mentor-level question is:

> **Does the intended bridge require literature to match the exact ClimRR metric/scenario, or is support at the broader hazard/concept level sufficient when unmatched dimensions are explicitly disclosed?**

---

## Next bounded objective

Proceed on two tracks.

### Track A — M4-WP1b: blind independent claim validation

Produce:

- independent scope status;
- independent claim set;
- exact evidence spans;
- dimension annotations;
- frozen result before comparison;
- disagreement table;
- adjudicated claim set;
- agreement statistics where meaningful.

### Track B — M4-WP2: relevance-guided candidate-generation infrastructure

Approved refined design:

```text
frozen approved concept surface terms
+
frozen approved prototype place terms
↓
boundary-aware case-insensitive lexical scan
over all decoded JSON string values
↓
qualify iff:
  ≥1 concept hit
  AND
  ≥1 place hit
↓
deduplicate exact-byte duplicates
↓
sort by stable LIT id
↓
take first 12
↓
freeze candidate list
↓
only then inspect semantically
```

Do not begin semantic extraction of the 12 candidates until WP1b is complete and does not materially invalidate the rationale for relevance-guided sampling.

The next positive-case M5 package should use:

- adjudicated literature claims;
- corrected/versioned prototypes;
- approved concept ontology;
- explicit candidate-eligibility logic;
- final relation categories distinct from retrieval.

---

## Acceptance criteria

1. M5-WP1 remains frozen and reproducible at its original input hashes.
2. Its status is machinery validation, not validated bridge evidence.
3. P-STATE-1 correction is versioned rather than replacing old input.
4. Exact metadata spans support the added year windows.
5. `concept_map.yaml` distinguishes family concepts from metric-specific concepts where necessary.
6. Every concept-map entry carries source, span/mentor record, date, and decision provenance.
7. No broad concept term is silently narrowed to a threshold/statistic.
8. COORDINATOR-approved entries are purely lexical/source-backed.
9. Scientific synonym/equivalence additions are separately approved.
10. Candidate eligibility requires concept `compatible`, geography `compatible`, and zero `incompatible` dimensions.
11. `not_evaluable` scenario/time/direction may allow candidacy but remain explicit.
12. Scenario-specific prototypes cannot receive unqualified `supporting` from claims with unknown scenario.
13. WP1b is blind to prototypes, first-pass claims, and M5 results during initial extraction.
14. WP1b freezes its independent result before comparison/adjudication.
15. Disagreements are preserved, not overwritten.
16. M4-WP2 uses boundary-aware lexical matching.
17. Retrieval terms are frozen/versioned.
18. Every lexical hit is auditable to item/path/span.
19. The candidate pool is deduplicated against the frozen corpus identity.
20. The first 12 qualifying unique items are selected by stable ID with no manual replacement.
21. Candidate IDs are frozen before semantic inspection.
22. M4-WP2 is labeled **relevance-guided candidate-generation sample, not representative**.
23. Semantic reading of WP2 waits for WP1b closure.
24. No retrieval hit itself is treated as a semantic bridge.
25. No QA is generated.

---

## Do not do yet

Do not change the frozen M5-WP1 matrix to improve the state prototype.

Do not map broad `heat index` language directly to a threshold-specific metric without threshold evidence.

Do not add UHI→heat index, wildfire smoke→FWI, or drought→FWI mappings based only on scientific relatedness.

Do not treat missing scenario as scenario compatibility.

Do not call a candidate pair `supporting` merely because nothing contradicts it.

Do not use unrestricted substring matching.

Do not manually replace WP2 candidates that look irrelevant.

Do not expose the second reader to first-pass or prototype information before its extraction is frozen.

Do not begin QA.

> **M5-WP1 validated the comparison machinery; the next work must validate the semantic interfaces that make positive comparisons meaningful.**
