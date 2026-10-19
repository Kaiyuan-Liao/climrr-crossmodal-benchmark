# ClimRR Cross-Modal Benchmark — Concept-First Literature Collection GUIDANCE Ruling

**Decision context:** Mentor direction dated 2026-10-09  
**Strategic change:** Shift positive-bridge literature discovery from a legacy hazard corpus to concept-first collection derived from table-side semantic units  
**Proposed source:** S2ORC shard via ANL araiadoc  
**Initial concept domains:** fire_weather, extreme_heat  
**GUIDANCE status:** PASS WITH ACTIONS

> This ruling authorizes the concept-first literature collection strategy as the primary path for positive bridge discovery. The legacy corpus remains preserved as methodological and negative-case evidence. No semantic reading of the new corpus is authorized until provenance, yield, and frozen candidate identities are reviewed.

---

## Gate status

**PASS WITH ACTIONS**

The mentor-directed pivot is scientifically preferable to continuing to rely on the earlier literature corpus as the primary source for positive bridge discovery.

The new S2ORC/araiadoc collection is authorized as a **separately versioned concept-first literature corpus**, subject to the provenance and scope constraints below.

The governing principle is:

> **Define the table-side concept first, collect literature for that concept second, then apply geography and compatibility constraints downstream.**

The earlier M4-WP0/WP1/WP2 corpus work remains valid and must be preserved as ingestion-method validation, negative-case evidence, reader-disagreement evidence, compatibility-machinery validation, and evidence motivating the concept-first pivot.

Do **not** rewrite the project history as if the new corpus had always been the intended source.

---

## Current-stage assessment

This pivot resolves the largest remaining design tension in the literature pipeline.

The previous work established that ingestion and exact-source claim extraction are reproducible; independent reading produces meaningful semantic disagreement; deterministic compatibility machinery works; legacy/content-independent sampling has poor positive-bridge yield; and concept/geography need explicit treatment rather than recovery through semantic similarity.

The mentor's direction gives the literature pipeline a cleaner causal order:

1. table-side concept definition;
2. concept-driven literature collection;
3. geography-based candidate filtering;
4. two-reader claim extraction;
5. deterministic bridge compatibility.

Keeping U.S. place terms **out of the collection query** is preferable because it preserves a useful separation between concept coverage, geographic coverage, and semantic bridge compatibility.

---

## Evidence check

### 1. Two family-level collection domains

**Authorized.**

The initial domains:

- `fire_weather`
- `extreme_heat`

are aligned with the two current pilot concept families.

Collection queries must use only **approved family-level vocabulary** from the tracked concept map.

Examples of acceptable query vocabulary include approved terms such as:

```text
fire weather index
FWI
heat index
```

Do not silently add scientifically related terminology such as wildfire, wildfire smoke, urban heat island, heat wave, apparent temperature, or drought-fire risk unless separately authorized through concept-map governance.

### 2. Boundary-aware whole-word matching

**Approved.**

Use boundary-aware lexical semantics where araiadoc permits them.

Record the actual araiadoc/S2ORC query semantics explicitly. If they differ from the repository matcher, preserve the difference rather than claiming equivalence.

### 3. No geography in collection query

**Approved and preferred.**

Do not include U.S. state, county, or prototype-place terms in initial collection.

Collection defines the **concept corpus**. Geography filtering occurs only after that corpus is frozen.

### 4. New corpus provenance

Treat the new source using an M4-WP0-style provenance package.

At minimum record:

- distinct corpus ID/version;
- S2ORC shard identity;
- shard record count;
- araiadoc version / commit / environment if knowable;
- exact `fire_weather` query;
- exact `extreme_heat` query;
- SHA-256 of each query;
- execution date/time;
- execution host/location;
- output counts;
- output format;
- duplicate policy;
- external corpus root;
- manifest identity/hash;
- per-item stable project IDs;
- per-item hashes where feasible;
- query/domain membership;
- known source limitations.

### 5. Missing year / venue / author metadata

**Acceptable as a source limitation.**

Keep:

```text
year: unknown
venue: unknown
authors: unknown
```

unless a later authorized rule recovers reliable metadata directly from the stored source record.

Do not reconstruct these fields from general knowledge or web sources during this phase.

---

## Scientific risks

### 1. Concept-first collection can create confirmation bias

The new corpus is intentionally enriched for pilot concepts.

That is appropriate for **candidate generation**, but not for estimating prevalence, representativeness, or unbiased bridge yield.

Every package should state:

> **Concept-guided candidate corpus; not representative of the broader scientific literature or the full S2ORC shard.**

### 2. Family-level vocabulary may be narrow

Approved vocabulary may miss relevant papers using alternative terminology.

That is acceptable initially. Recall expansion should happen only through explicit concept-map decisions.

### 3. Biomedical shard skew

The S2ORC shard is reportedly biomedicine-heavy.

Record that as a source-composition limitation. Do not interpret arm yield as representative of the literature generally.

### 4. Cross-domain duplicate papers

A paper may match both query arms.

Preserve one stable document identity plus membership in both arms and matched terms. Do not count it as two independent papers.

### 5. Collection hit ≠ claim concept

A record entering because it contains `FWI` does not establish that a promoted claim is about Fire Weather Index.

A lexical hit remains only a reason to inspect an item.

### 6. New strategy must not erase old evidence

Preserve the original literature corpus and all prior experiments.

---

## Required actions

1. Log the mentor direction as a scientific decision dated **2026-10-09**.
2. Explicitly record the strategy shift from legacy hazard-corpus exploration to concept-first collection based on table-side semantic units.
3. Assign the new corpus a distinct immutable corpus ID/version.
4. Keep old corpus manifests and experiments unchanged.
5. Pin separately the `fire_weather` and `extreme_heat` collection queries.
6. Record the exact concept-map version used to construct each query.
7. Record araiadoc execution provenance.
8. Record the exact S2ORC shard identity and the reported **54,081-record** source size.
9. Keep collected documents external on Eagle.
10. Commit only provenance, manifests, hashes, compact statistics, configuration, and query definitions.
11. Detect duplicates across query arms by stable content identity.
12. Preserve query/domain membership separately from claim labels.
13. Do not apply U.S. place filtering during collection.
14. Apply approved place filtering only after the concept corpus has been frozen.
15. Freeze candidate IDs before semantic reading.
16. Reuse the two-reader extraction protocol.
17. Preserve evidence-validation tiers.
18. Reuse deterministic compatibility machinery only after adjudication.
19. Keep missing S2ORC metadata explicitly `unknown`.
20. Return the provenance/yield packet to GUIDANCE **before any new paper is semantically read**.

---

## Decisions for Kaiyuan or mentor

| Question | Ruling |
|---|---|
| Pivot to concept-first collection | **Approved** |
| Treat new source as continuation of old corpus | **No; use a new corpus/version** |
| Initial domains `fire_weather`, `extreme_heat` | **Approved** |
| Family-level vocabulary only | **Required** |
| Add scientific synonyms during collection | **Not without approval** |
| Boundary-aware matching | **Approved** |
| Include U.S. geography in collection query | **No** |
| Apply geography after concept collection | **Approved** |
| External storage on Eagle | **Approved** |
| M4-WP0-style provenance/inventory | **Required** |
| Missing year/venue/author | **Record as `unknown` limitation** |
| Two-reader extraction | **Required** |
| Reuse compatibility machinery | **Approved** |
| Read papers before provenance/yield review | **No** |
| QA generation | **Still not authorized** |

A useful mentor question for later is:

> **Should future vocabulary expansion prioritize recall within the same concept family, or remain deliberately narrow until positive bridges are demonstrated with the current approved vocabulary?**

---

## Next bounded objective

The next package should be:

**M4-WP3 — Concept-First Literature Corpus Provenance and Yield Review**

It should contain two frozen collection arms.

### Arm A — fire weather

Record:

- approved concept-map version;
- exact araiadoc query;
- query SHA-256;
- S2ORC shard identity;
- raw match count;
- unique-item count;
- duplicate count;
- output format;
- output manifest;
- corpus/manifest hash.

### Arm B — extreme heat

Record the same fields.

### Cross-arm summary

Report:

- overlap between arms;
- total unique documents;
- per-term hit counts if deterministically available;
- formats;
- malformed/failed records;
- total bytes;
- duplicate groups;
- missing-metadata limitation;
- source-domain-skew limitation.

Then, **without semantic reading**, apply the existing approved place-term filter and report:

- number of concept-corpus items with approved pilot geography hits;
- per-prototype place-term counts;
- frozen candidate IDs;
- exact lexical hit locations.

Stop there and return to GUIDANCE.

---

## Acceptance criteria

The concept-first provenance package is ready when:

1. The mentor-direction decision is logged.
2. The new corpus has a distinct immutable identity.
3. Both exact collection queries are preserved.
4. Each query is hash-pinned.
5. Query vocabulary is traceable to the approved concept map.
6. No unapproved synonym appears in either query.
7. The S2ORC shard is uniquely identified.
8. The stated **54,081-record** source count is recorded with provenance.
9. araiadoc execution environment/version is recorded where knowable.
10. Unknown collection metadata remains explicitly `unknown`.
11. Raw yield is reported separately for each concept family.
12. Cross-domain duplicate records are identifiable.
13. Corpus files remain external on Eagle.
14. No bulk corpus text is committed to Git.
15. A deterministic hashed manifest exists.
16. Every collected item has a stable project ID.
17. Query/domain membership is preserved.
18. Missing year/venue/author is documented as a source limitation.
19. No semantic claim extraction occurs.
20. No place term participates in initial collection.
21. Geography filtering occurs only after the concept corpus is frozen.
22. Geography filtering uses only currently approved place vocabulary.
23. Candidate IDs are frozen before semantic inspection.
24. Collection/retrieval hits are not described as claims or bridges.
25. No QA is generated.

---

## Do not do yet

Do not semantically read the newly collected papers before the provenance/yield packet is reviewed.

Do not broaden collection terms because one arm has disappointing yield.

Do not add UHI, wildfire smoke, drought, generic wildfire, or generic heat-wave terminology unless concept ontology separately authorizes them.

Do not include U.S. states in the initial S2ORC query.

Do not reconstruct missing author/year/venue metadata from external web sources.

Do not infer corpus representativeness from collection yield.

Do not discard or overwrite old literature-corpus experiments.

Do not build QA.

The new primary positive-bridge path should be:

> **table concept → concept-defined literature corpus → geography filtering → independent claim extraction → deterministic bridge validation**

That ordering is better aligned with the benchmark's scientific objective and should now govern positive bridge discovery.
