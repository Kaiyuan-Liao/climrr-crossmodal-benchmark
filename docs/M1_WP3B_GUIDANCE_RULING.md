# ClimRR Cross-Modal Benchmark — M1-WP3b GUIDANCE Ruling

**Milestone:** M1 — Data Grounding and Metadata Audit  
**Work package:** M1-WP3b — Three phenomenon-unit prototypes for scientific-object validation  
**GUIDANCE status:** PASS WITH ACTIONS  
**Scope:** Bounded early M3-style validation while M1 remains open

> This ruling authorizes exactly three validation-only prototype phenomenon units. It does **not** pass M1, start M3 formally, authorize general phenomenon extraction, or permit literature retrieval, bridge construction, or QA generation.

---

## Gate status

**PASS WITH ACTIONS**

M1-WP3b is authorized as a **bounded early M3-style validation package**.

The three outputs are **prototype phenomenon units**, not accepted M3 phenomena and not evidence that M1 has passed.

County/state aggregation, provisional magnitude, and a literature-probe stub are permitted only under the constraints below.

---

## Current-stage assessment

The project has reached the point where metadata review alone is no longer sufficient to test whether the intended table-side scientific object is coherent.

WP3b asks:

> **If these semantics are approximately right, what would the actual table-side scientific unit look like at cell, county, and state scale?**

This can expose conceptual problems that metadata review cannot, including whether geography, aggregation, provenance, and the proposed dimensions `G, H, S, T, C, D, M, V` form a usable object for later literature connection.

The outputs must remain explicitly labeled **validation prototypes**.

---

## Evidence check

### 1. Deterministic hierarchy checks

**Authorized.**

Allowed computed facts include:

- `Crossmodel` uniqueness;
- rows per `(State, NAME)`;
- rows per `GEOID`;
- member-row lists for aggregate prototypes.

Keep computed grouping facts separate from semantic interpretations of geography.

### 2. Prototype phenomenon schema

**Authorized.**

Use:

- **G** — geography / level
- **H** — hazard or climate concept
- **S** — scenario
- **T** — temporal horizon
- **C** — compared quantity / change
- **D** — direction
- **M** — magnitude
- **V** — supporting numeric evidence and operation

Also preserve **P — provenance / epistemic status**, either explicitly or per field.

Every component must distinguish computed, `verified_from_dictionary`, `owner_confirmed`, `inferred_candidate`, and prototype-only assumptions.

### 3. County/state aggregation

**Authorized only as prototype methodology.**

An unweighted mean is acceptable for these three prototypes only if labeled:

> **provisional aggregation rule for representation validation**

For every aggregate quantity record:

- level;
- member identifiers;
- `n_members`;
- `n_nonempty`;
- `n_empty`;
- source field;
- operation;
- exclusions;
- provisional equal-weighting assumption.

Do not average identifiers, categorical labels, percentages, or quantities for which a mean is not scientifically interpretable.

### 4. Direction `D`

**Authorized.**

Record the exact subtraction/sign convention and what positive/negative mean.

If subtraction order remains unresolved, `D` must remain provisional.

### 5. Magnitude `M`

**Authorized as prototype-only.**

The percentile-rank rule must record:

- reference population;
- signed vs. absolute-change ranking;
- exact rule;
- explicit provisional status.

Magnitude must **not** be used to select the three prototypes.

### 6. Literature-probe stub

**Authorized.**

It may list query-forming fields only.

No searching, retrieval, ranking, embeddings, claim extraction, paper suggestion, or semantic matching is authorized.

---

## Scientific risks

### 1. Prototype becoming de facto truth

Every prototype must state prominently:

> **Prototype for scientific-object validation. Not an accepted phenomenon record.**

### 2. Aggregation hiding coverage

County/state prototypes must report member provenance and coverage counts.

### 3. Geographic labels may still be inferred

Raw grouping keys and interpreted geography labels must remain separate.

### 4. Percentile magnitude can imply false importance

Percentile rank is relative, not intrinsic scientific significance. Prefer neutral percentile wording.

### 5. Spatial levels may not be equivalent

Cell-, county-, and state-level records should test whether meaning survives changes in spatial support, not assume it.

### 6. Literature-probe fields can smuggle in unsupported semantics

Only fields already present in the prototype may enter the query stub.

---

## Required actions

1. Record WP3b as an explicit milestone-order exception: early M3-style validation while M1 remains open.
2. Label every prototype `validation_only` or equivalent.
3. Preserve raw grouping keys separately from provisional geographic labels.
4. Store source columns, operations, counts, and exact member-row provenance for every aggregate.
5. Keep unweighted mean explicitly provisional and non-generalized.
6. Define the magnitude reference population exactly.
7. Ensure magnitude does not drive prototype selection.
8. Record the sign convention used for `D`.
9. Preserve per-field epistemic status through aggregation and templated descriptions.
10. Keep the literature probe as a query-field stub only.
11. Maintain an assumptions register with assumption ID, affected fields, rationale, failure mode, verification path, and status.

---

## Decisions for Kaiyuan or mentor

| Proposed component             | Ruling                                       |
| ------------------------------ | -------------------------------------------- |
| Deterministic hierarchy checks | **Authorized**                               |
| Prototype phenomenon schema    | **Authorized**                               |
| Cell-level prototype           | **Authorized**                               |
| County-level prototype         | **Authorized provisionally**                 |
| State-level prototype          | **Authorized provisionally**                 |
| Unweighted mean                | **Prototype-only and provisional**           |
| Direction from sign            | **Authorized with explicit convention**      |
| Percentile-rank magnitude      | **Prototype-only; cannot select prototypes** |
| Literature-query stub          | **Authorized; zero retrieval**               |
| Three prototypes only          | **Keep this limit**                          |
| General phenomenon extraction  | **Not authorized**                           |

For expert review, the main question is:

> **Is this the right scientific unit for connecting ClimRR table evidence to literature, and what is wrong or missing in its structure?**

---

## Next bounded objective

**Authorize M1-WP3b — Three phenomenon-unit prototypes for scientific-object validation.**

Produce exactly:

1. one cell-level prototype;
2. one county-level prototype;
3. one state-level prototype.

All three must use only the existing WP3 pilot subset.

The package should answer:

> **Can one transparent, provenance-preserving representation express a table-derived climate phenomenon at multiple spatial levels well enough for experts to judge whether it is suitable for later literature connection?**

After expert feedback, return to GUIDANCE before any general extractor or literature work.

---

## Acceptance criteria

M1-WP3b is ready for review when:

1. Exactly three prototypes exist: cell, county, state.
2. Selection does not use magnitude, percentile, salience, or literature availability.
3. Every prototype is reproducible from the manifest-pinned CSV.
4. Every numeric value is traceable to source columns, rows, and computation.
5. County/state prototypes list complete member-cell provenance.
6. Aggregation reports `n_members`, `n_nonempty`, `n_empty`, operation, and provisional status.
7. Means are used only for meaningfully averageable quantities.
8. Geography separates raw grouping keys from provisional semantic labels.
9. `D` records its sign/subtraction convention and uncertainty.
10. `M` records reference population, ranking rule, provisional status, and non-use in selection.
11. Every semantic component carries provenance / epistemic status.
12. Natural-language descriptions preserve provisionality.
13. FWI remains Fire Weather Index, not wildfire occurrence.
14. Historical ClimRR values remain modeled baselines, not observations.
15. The literature probe performs zero literature access.
16. The assumptions register covers row/event grain, geography, hierarchy, aggregation, missing values, change direction, magnitude, and inferred semantics.
17. Nothing claims these are accepted M3 phenomena.
18. The output is compact enough for expert review.

---

## Do not do yet

Do not build a general phenomenon extractor.

Do not run this over all counties, states, rows, hazards, or fields.

Do not rank or select “interesting” regions.

Do not optimize magnitude bins.

Do not adopt unweighted mean as the project-wide aggregation method.

Do not introduce weighted aggregation or uncertainty propagation yet.

Do not search for papers.

Do not ingest the literature corpus.

Do not create embeddings.

Do not extract literature claims.

Do not generate candidate bridges.

Do not generate QA.

Do not let these prototypes bypass unfinished M1 confirmation work.

> **Build three transparent phenomenon-unit prototypes so experts can judge whether the object intended for later literature connection is scientifically coherent before a general pipeline is built.**
