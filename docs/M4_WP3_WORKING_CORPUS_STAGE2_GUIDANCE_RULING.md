# ClimRR Cross-Modal Benchmark — M4-WP3 Working-Corpus, Sampling, and Stage-2 GUIDANCE Ruling

**Decision context:** M4-WP3 concept-first corpus provenance/source-yield review  
**Reviewed package:** `work/m4-wp3` @ `6b2b5a6`  
**Working corpus candidate:** `LITCORPUS-02-conceptfirst-705k-v1`  
**Follow-on work:** 20-paper two-reader candidate-reading pilot + dictionary-grounded concept coverage diagnostics  
**GUIDANCE status:** PASS WITH ACTIONS

> This ruling promotes LITCORPUS-02 to the working concept-first candidate corpus, preserves LITCORPUS-01 as the provenance/yield pilot, refines concept-map governance for five query terms, authorizes a deterministic 10+10 two-reader reading sample, and authorizes the dictionary-grounded Stage 2a–2c concept survey strictly as diagnostics. No QA is authorized.

---

## Gate status

**PASS WITH ACTIONS**

M4-WP3 **passes as the concept-first provenance/source-yield gate**.

Rulings:

1. **Accept `LITCORPUS-02-conceptfirst-705k-v1` as the working concept-first corpus.**
2. **Keep `LITCORPUS-01-conceptfirst-v1` as the documented source/yield pilot; sectionization is no longer required.**
3. **Approve the next two-reader reading package, with a refined deterministic 10+10 sampling rule.**
4. **Authorize Stage 2a–2c — dictionary-grounded concept inventory, candidate surface forms, and yield survey — strictly as diagnostics.**
5. **Approve concept-map governance updates for the five query terms, while distinguishing direct lexical aliases from broader family-level collection terms.**
6. **Global `.gitattributes` cleanup may wait for a housekeeping package.**
7. **No QA is authorized.**

Before merge, refresh the milestone report and project state to the actual reviewed head `6b2b5a6` and pushed status.

---

## Current-stage assessment

The source-expansion experiment worked as intended:

> **same concepts + same frozen queries + different source → substantially different candidate yield.**

The larger source contains 186,346 JSON files, 1,658,731 string sections, 184,268 distinct SHA-256 values, and 2,078 redundant exact-byte copies.

The upstream rule filtering the reported 705k parent to 186,346 files remains unknown and stays open as Q22.

Admitted arms:

- fire weather: 495 raw → **448 admitted** after R-FWI-1;
- extreme heat: **861**;
- overlap: 1;
- union: **1,308**.

Geography preflight produced:

- **100 fire-weather candidates**;
- **143 extreme-heat candidates**.

These remain lexical candidates only. The role of `California`, `Oklahoma`, or `Stephens` must be established during semantic reading.

LITCORPUS-02 is suitable as a **working candidate-generation corpus**, but not as a representative sample of climate literature.

---

## Evidence check

### 1. Q1 — Promote LITCORPUS-02; retire sectionization of LITCORPUS-01

**Approved.**

Use:

> **`LITCORPUS-02-conceptfirst-705k-v1` = working concept-first corpus**

Keep:

> **`LITCORPUS-01-conceptfirst-v1` = provenance/yield pilot**

LITCORPUS-01 sectionization is **not required**. Record the deferment explicitly rather than leaving it unfinished.

### 2. Q2 — Five concept-map terms

Five terms:

- `fire-weather index`
- `canadian forest fire weather index`
- `canadian fwi`
- `heat-index`
- `extended heat index`

Approve the first four as ordinary family lexical forms, with GUIDANCE provenance:

```text
source_type: guidance
decision_id: D-022
status: approved_lexical
```

They may participate in collection, retrieval, and C-2 family-level claim matching.

Treat `extended heat index` differently. Approve it for:

> **heat-index-family collection and retrieval**

but not as a strict synonym for ordinary heat index or for the threshold metric `heatindex_days_above_105F`.

Suggested governance:

```text
canonical_id: heat_index
term: extended heat index
status: approved_family_term
usage:
  - collection
  - retrieval
source_type: guidance
decision_id: D-022
```

### 3. R-FWI-1

**Accepted as implemented.**

The repository should continue preserving the canonical six-disambiguator rule.

Keep the separation:

- `FWI` stays in the concept map;
- R-FWI-1 governs retrieval;
- C-2 governs family-level claim matching;
- neither establishes metric-level compatibility.

### 4. Matcher difference

**Accepted as a disclosed limitation.**

The shard run used concatenated-document matching; the 705k source uses per-section matching.

Do not interpret the yield change as a formal source-effect estimate because source size, composition, filtering, and matcher granularity differ.

### 5. Upstream 705k filtering

**Keep Q22 open.**

This uncertainty prevents corpus-representativeness claims but does not block candidate use.

### 6. Q3 — 10+10 reading sample

**Authorize a 20-paper two-reader pilot.**

Use:

- 10 fire-weather place candidates;
- 10 extreme-heat place candidates.

Sampling must use **candidate rank after sorting by frozen `LIT2` ID**, not numeric divisibility of IDs.

Fire-weather:

```text
ranks 10,20,30,...,100
```

Extreme heat:

```text
ranks 14,28,42,...,140
```

Before ranking for sampling:

1. start from the frozen arm candidate list;
2. sort ascending by `LIT2` ID;
3. remove later members of exact-byte duplicate groups for sampling only;
4. assign ranks 1…N.

If a selected rank is unavailable because of duplicate suppression, advance to the next higher unused rank.

If one item would enter both arm samples, retain it in the arm encountered first under a predeclared arm order and advance the other arm. Recommended order:

```text
fire_weather
extreme_heat
```

Freeze the sample before any paper is read.

---

## Scientific risks

### 1. Unknown source filter

LITCORPUS-02 is appropriate for candidate discovery, not prevalence estimates.

### 2. Selecting concepts by literature coverage

Stage 2 may help prioritize **what to pilot next**, but literature yield must not determine whether a table concept is scientifically valid.

### 3. LLM-proposed surface forms

Model-generated terms can silently broaden meaning. All proposals remain inert until separately approved.

### 4. Broad concepts dominate yield

Higher literature counts do not imply a better benchmark concept.

### 5. Place filtering is noisy

The 100/143 counts are lexical intersections, not confirmed study geographies.

### 6. Duplicate papers are not independent evidence

Exact-byte copies preserve provenance but must not be sampled as separate evidence.

---

## Required actions

1. Record **M4-WP3 PASS WITH ACTIONS**.
2. Promote `LITCORPUS-02-conceptfirst-705k-v1` as the working candidate corpus.
3. Keep LITCORPUS-01 frozen as the source/yield pilot.
4. Explicitly close LITCORPUS-01 sectionization as not required.
5. Keep Q22 open.
6. Update the five query terms with explicit GUIDANCE governance.
7. Preserve collection-vocabulary vs family-C-2 vs metric-level distinctions.
8. Freeze the 20-paper sampling procedure before reading.
9. Produce exactly 10 unique items per arm.
10. Suppress later exact-byte duplicates for sampling only.
11. Preserve duplicate identities in corpus provenance.
12. Apply the existing reader-1 → blind-reader → freeze → adjudication → evidence-tier protocol.
13. For every sampled paper record whether concept and place hits are substantive or incidental.
14. Do not prefill claims from retrieval hits.
15. Run compatibility only after adjudication.
16. Refresh M4-WP3 bookkeeping to reviewed head `6b2b5a6`.
17. Defer global `.gitattributes` cleanup to housekeeping.

---

## Decisions for Kaiyuan or mentor

| Question | Ruling |
|---|---|
| M4-WP3 gate | **PASS WITH ACTIONS** |
| LITCORPUS-02 working corpus | **Approved** |
| LITCORPUS-01 retained | **Yes — provenance/yield pilot** |
| LITCORPUS-01 sectionization | **Not required** |
| Q22 unknown source filter | **Keep open; not a candidate-use blocker** |
| `fire-weather index` | **Approve as family lexical form** |
| `canadian forest fire weather index` | **Approve as family lexical form** |
| `canadian fwi` | **Approve as family lexical form** |
| `heat-index` | **Approve as family lexical form** |
| `extended heat index` | **Approve for heat-index-family collection/retrieval; not strict metric equivalence** |
| 20-paper reading pilot | **Approved — 10 + 10** |
| Every-k sampling | **Approved with explicit rank/duplicate/overlap rule** |
| Read all 243 place candidates now | **No** |
| Stage 2a dictionary concept inventory | **Authorized diagnostic** |
| Stage 2b LLM surface-form proposals | **Authorized, candidate-only** |
| Stage 2c literature yield survey | **Authorized diagnostic** |
| Stage 2 automatically approves families/units | **No** |
| Inventory limited to dictionary-described concepts | **Yes** |
| Global `.gitattributes` cleanup now | **May wait for housekeeping** |
| QA | **Still not authorized** |

---

## Next bounded objective

Proceed with **two bounded work streams**.

### Track A — M4-WP4: 20-paper concept/place candidate reading pilot

Freeze:

- 10 fire-weather place candidates;
- 10 extreme-heat place candidates.

Apply:

```text
reader 1
→ blind reader
→ freeze
→ comparison
→ adjudication
→ compatibility
```

For each paper classify:

**Concept-hit precision**
- substantive concept use;
- incidental mention;
- ambiguous acronym/other collision.

**Place-hit precision**
- study area / phenomenon geography;
- contextual geography;
- institution / affiliation;
- citation / surname / person;
- other incidental use.

Only structured claims enter compatibility.

Compare adjudicated claims against:

- P-CELL-1;
- P-COUNTY-1;
- P-STATE-1 v2.

### Track B — Dictionary-grounded concept coverage survey

**Authorize Stage 2a–2c as diagnostics.**

#### 2a. Dictionary concept inventory

Inventory only **dictionary-described concepts/metrics**.

Store:

- stable concept inventory ID;
- dictionary name/title;
- exact passage;
- page/line provenance;
- units when explicit;
- metric/threshold when explicit;
- scenario/horizon only when explicit.

Do not infer CSV-column meaning from headers. Existing M1 statuses remain unchanged. Index 117 remains unlabeled.

#### 2b. Candidate surface forms

A model may propose terms, but every proposal must be:

```text
status: candidate_surface_form
```

and record:

- model ID;
- endpoint/version if available;
- prompt text/hash;
- date;
- source dictionary concept ID;
- proposed term;
- optional rationale.

These terms must not automatically enter the concept map, production queries, C-2, or compatibility.

#### 2c. Diagnostic yield survey

For each dictionary concept, compute deterministic counts over the frozen LITCORPUS-02 source index.

Suggested output:

```text
concept_id
dictionary_name
dictionary_span
candidate_surface_forms
topical_only_count
context_filtered_count
notes
```

The ranking is exploratory only.

Stage 2 may answer:

> **Which dictionary-grounded concepts appear to have enough literature coverage to justify deeper pilot design?**

It may not answer:

> Which unresolved CSV columns mean what?

or:

> Which table concepts are scientifically valid?

---

## Acceptance criteria

The next package is ready for GUIDANCE review when:

1. M4-WP3 bookkeeping reflects reviewed head `6b2b5a6` and pushed state.
2. LITCORPUS-02 is recorded as the working candidate corpus.
3. LITCORPUS-01 remains preserved as a provenance/yield pilot.
4. LITCORPUS-01 sectionization is explicitly closed as unnecessary.
5. Q22 remains visible and unresolved.
6. The five query terms receive explicit GUIDANCE governance.
7. `extended heat index` is not treated as the threshold-specific ClimRR metric.
8. The 20-paper sample rule is frozen before reading.
9. Sampling uses frozen candidate lists sorted by `LIT2` ID.
10. Exact-byte duplicate copies cannot both enter the sample.
11. Duplicate replacement is deterministic.
12. Cross-arm overlap handling is deterministic.
13. Exactly 10 unique items per arm are selected.
14. No manual relevance replacement occurs.
15. Reader 1 receives no prefilled claim semantics from retrieval hits.
16. Blind reader receives no hit locations, prototypes, reader-1 output, or expected bridge result.
17. Blind reading is frozen before comparison.
18. Adjudication preserves disagreements and evidence tiers.
19. Concept-hit precision is classified separately from place-hit precision.
20. Every promoted claim has exact source evidence.
21. Compatibility runs only after adjudication.
22. No lexical retrieval hit is treated as a bridge.
23. Stage 2a contains only dictionary-described concepts/metrics.
24. Stage 2a does not change existing column statuses.
25. Index 117 remains unlabeled.
26. Stage 2b outputs are explicitly `candidate_surface_form`.
27. Stage 2b records model and prompt provenance.
28. Stage 2b vocabulary never enters production automatically.
29. Stage 2c is deterministic and restartable.
30. Stage 2c counts are labeled diagnostics, not literature-prevalence estimates.
31. Literature yield does not automatically determine unit selection.
32. Scoped `.gitattributes` protections remain sufficient until repository-wide cleanup.
33. No QA is generated.

---

## Do not do yet

Do not read all 100 fire-weather or 143 extreme-heat place candidates.

Do not choose candidates based on promising hit snippets.

Do not treat 448 vs. 861 as prevalence of the two concepts.

Do not resolve Q22 by inference.

Do not use literature coverage to assign semantics to unresolved CSV columns.

Do not promote model-generated vocabulary directly into the concept map.

Do not let an LLM-generated synonym redefine a dictionary concept.

Do not automatically turn the highest-yield dictionary concepts into benchmark units.

Do not discard low-yield table concepts solely because literature coverage is sparse.

Do not treat `extended heat index` as equivalent to `days above 105°F`.

Do not count exact-byte duplicate papers as independent evidence.

Do not begin QA.

The project can now run two complementary tests without conflating them:

> **Track A asks whether the current concept-first retrieval pipeline actually yields usable table↔literature bridges.**

> **Track B asks which other dictionary-grounded table concepts have enough literature coverage to merit future unit design.**

That separation preserves the mentor's:

> **table concept → literature**

direction while still using literature coverage intelligently to prioritize what should be investigated next.
