# ClimRR Cross-Modal Benchmark — M4-WP3 Source-Yield and FWI Disambiguation GUIDANCE Ruling

**Decision context:** Concept-first collection yield review, 2026-10-12  
**Current corpus:** `LITCORPUS-01-conceptfirst-v1`  
**Source:** S2ORC v1 shard via ANL araiadoc  
**Primary issue:** source coverage + acronym ambiguity, not ontology failure  
**GUIDANCE status:** PASS WITH ACTIONS

> This ruling preserves the current concept-first run as a documented provenance/yield pilot, authorizes a better-targeted S2ORC source request with the same frozen queries, and introduces a retrieval-only disambiguation rule for bare `FWI` without changing the scientific concept map.

---

## Gate status

**PASS WITH ACTIONS**

The concept-first collection strategy remains approved.

The current S2ORC run should be treated as a successful **provenance/yield pilot**, but **not as the final positive-bridge corpus**, because the fire-weather arm is too small and the shard is strongly source-skewed for the intended domain.

Rulings:

1. **Authorize requesting a larger and/or atmospheric/geoscience-oriented S2ORC source** from the ANL data owner/tool team.
2. **Proceed now with M4-WP3 provenance mechanics on the frozen 14-paper v1 output**: sectionization, hashed inventory, and the predeclared place-term filter are authorized. Do not wait for the larger source.
3. **Keep the context-free runs as diagnostics only**, not corpus versions.
4. **Do not delete `FWI` from the concept map**, but change its collection/retrieval governance: bare `FWI` should no longer independently admit a document into the fire-weather candidate corpus in heterogeneous general-science sources.
5. **Require same-document fire-weather disambiguation for bare `FWI`**, as specified below.
6. **No semantic paper reading is authorized yet.**

The present collection should remain frozen as:

> **LITCORPUS-01-conceptfirst-v1**

and preserved as the documented first concept-first run.

---

## Current-stage assessment

The evidence points to a source-domain problem rather than a failure of the concept-first strategy.

The two production arms returned:

- fire weather: **4 papers**;
- extreme heat: **10 papers**.

The context-free diagnostic runs returned:

- fire weather: **13**;
- extreme heat: **11**.

Dropping the climate/projection precision clause therefore does not reveal a large hidden pool.

The fire-weather result is even more constrained because bare `FWI` is highly polysemous in this heterogeneous source:

- 13 bare-`fwi` diagnostic hits;
- only 3 contain `fire weather`;
- the remaining 10 are unrelated expansions/usages such as:
  - full waveform inversion;
  - Forest Watch Indonesia;
  - fatal work injuries;
  - other acronym collisions.

Two of those collisions survive into the current 4-paper production arm.

Therefore the present fire-weather arm contains **at most two plausible Fire Weather Index papers before semantic reading**.

That is not a reason to widen the scientific concept map.

It is evidence that:

> **the retrieval layer needs acronym disambiguation, and the source shard needs better topical coverage.**

The extreme-heat arm is less problematic lexically, but a 10-paper output from a biomedical-heavy shard still provides too little basis for building the positive bridge corpus.

---

## Evidence check

### 1. Production queries and precision context clause

**Accepted.**

The production queries remain concept-first because the topical side is restricted to approved family vocabulary.

Using terms such as:

- `climate change`;
- `RCP`;
- `SSP`;
- `CMIP`;
- `downscaled`;
- `end of century`;
- `future climate`;

as an **AND-ed precision/context clause** is acceptable.

For the heat arm, using:

- `public health`;
- `heat wave`;
- `heatwave`;

only as context filters is also acceptable because those terms do not independently qualify an item for the `extreme_heat` concept corpus.

The distinction must remain explicit:

> **topical term determines concept membership; context term only constrains precision.**

Do not later treat a context-clause term as an approved concept alias.

### 2. Broader unused draft queries

**Correctly handled.**

Preserving and hash-pinning the collection team's broader draft queries while leaving them unused is good provenance practice.

Keep them labeled:

> `unused / not executed as corpus-defining query`

They must not enter corpus identity.

### 3. Context-free diagnostics

**Remain diagnostics only.**

The context-free runs are useful for:

- sensitivity analysis;
- showing how much the precision clause removes;
- exposing acronym collisions.

They do **not** define another literature corpus.

Do not assign them a `LITCORPUS-*` identity.

Call them:

> **collection sensitivity diagnostics**

and keep their hashes/results attached to the v1 provenance package.

### 4. Request for a better S2ORC source

**Authorized.**

Request one or more larger or better-targeted S2ORC shards emphasizing, where available:

- atmospheric science;
- climate science;
- meteorology;
- geoscience;
- environmental science;
- hazards / fire-weather literature.

Use the **same frozen production queries** and the same provenance protocol first.

Also run the same topical-only diagnostic queries where computationally reasonable so source coverage can be compared directly.

Do not modify vocabulary between shards before seeing comparable yields.

This creates the clean comparison:

> **How much does source composition, holding query semantics fixed, affect candidate yield?**

### 5. `FWI` governance

This requires a distinction between:

- ontology membership;
- retrieval eligibility.

`FWI` remains a legitimate dictionary-backed lexical alias for the **Fire Weather Index** concept family.

Therefore:

> **Do not remove `FWI` from `concept_map.yaml`.**

However, its empirical ambiguity means it should not remain an unconditional corpus-retrieval trigger in heterogeneous scientific text.

Approved retrieval rule:

> **Bare `FWI` is fire-weather retrieval-eligible only when the same document also contains an approved fire-weather disambiguator.**

Approved disambiguators:

- `fire weather`;
- `fire-weather`;
- `fire weather index`;
- `fire-weather index`;
- `canadian forest fire weather index`;
- `canadian fwi`.

The longer terms already disambiguate themselves.

Examples:

```text
"FWI increased..."
```

alone → does **not** qualify.

```text
"Fire Weather Index (FWI)..."
```

→ qualifies.

```text
"Canadian FWI..."
```

→ qualifies.

```text
"full waveform inversion (FWI)..."
```

→ does not qualify.

This is a **retrieval policy**, not a scientific change to the canonical concept.

### 6. Same-document versus same-span requirement

Use **same-document co-occurrence**, not same-sentence or same-section co-occurrence, for the first version of the disambiguation policy.

A stricter sentence-level requirement could create unnecessary false negatives when a paper defines FWI once and uses the acronym later.

Record both hit locations so the disambiguation remains auditable.

---

## Scientific risks

### 1. Source selection becoming post-hoc cherry-picking

Moving to a better domain source is justified because the current shard mismatch is already documented.

But do not inspect candidate content and repeatedly request sources until positive bridges appear.

The next source request should be defined by **disciplinary coverage**, not desired bridge outcome.

### 2. `FWI` collision policy becoming hidden semantic inference

The new rule is lexical disambiguation only.

It does not establish that a promoted claim actually concerns the ClimRR FWI metric.

Claim extraction still decides that later.

### 3. Query-context clause creating hidden sampling bias

The production corpus is enriched not only by concept vocabulary but also by climate/projection context.

That is acceptable, but it must remain part of the corpus definition.

Do not compare its yield with an unconstrained source as if only the source changed.

### 4. Biomedical skew contaminating interpretation

The approximate PubMed/arXiv composition is useful context but should be reported as supplied by the collection-tool team unless independently computed by this project.

### 5. Tiny v1 arms encouraging premature reading

Four and ten papers are enough to test provenance mechanics.

They are not enough reason to begin positive benchmark construction before the source-selection question is resolved.

### 6. Overcorrecting FWI

Do not eliminate bare `FWI` from the ontology merely because retrieval is noisy.

Acronym ambiguity is a retrieval problem, not proof that the alias is scientifically invalid.

---

## Required actions

1. Freeze the current outputs as **LITCORPUS-01-conceptfirst-v1**.

2. Preserve the exact six query files and their SHA-256 hashes.

3. Log the mentor direction dated **2026-10-09**.

4. Record the current source as the first concept-first source trial, including:
   - shard filename;
   - bytes;
   - 54,081 records;
   - araiadoc commit;
   - DuckDB matching semantics;
   - execution location/date;
   - thread/memory configuration.

5. Record the source-domain profile as **reported by the tool team** if it was not independently computed by this project.

6. Keep production and diagnostic query outputs clearly separate.

7. Preserve the 10 documented bare-`FWI` collisions as evidence motivating retrieval disambiguation.

8. Update retrieval governance so bare `FWI` requires same-document approved fire-weather disambiguation.

9. Do not alter the canonical `FWI` concept-map alias itself.

10. Apply the revised FWI retrieval rule consistently to:
    - this concept-first v1 source;
    - the legacy source if it is re-queried;
    - all future S2ORC sources.

11. Request a larger/domain-appropriate S2ORC source with the **same frozen queries**.

12. Keep each new shard/source arm separately identified before any combined corpus is created.

13. Proceed with v1:
    - sectionization;
    - external storage;
    - hashed inventory;
    - stable IDs;
    - cross-arm deduplication;
    - approved place-term filtering.

14. Freeze any geography-filter candidate list, but **do not semantically read it yet**.

15. Return the full M4-WP3 packet plus requested-source status before reading papers.

---

## Decisions for Kaiyuan or mentor

| Question | Ruling |
|---|---|
| Request larger / non-biomedical S2ORC source | **Authorized** |
| Prefer atmospheric/geoscience/environmental coverage | **Yes** |
| Change queries for new source | **No; first use identical frozen queries** |
| Run diagnostics on new source | **Yes, if feasible** |
| Freeze current 14-paper output | **Yes — `LITCORPUS-01-conceptfirst-v1`** |
| Proceed with v1 provenance machinery now | **Yes** |
| Semantically read v1 papers now | **No** |
| Context-free sets as corpus versions | **No; diagnostics only** |
| Remove `FWI` from concept map | **No** |
| Bare `FWI` as unconditional retrieval term | **No** |
| Bare `FWI` + same-document fire-weather disambiguator | **Approved** |
| Require same-sentence disambiguation | **No; same-document is sufficient for retrieval** |
| Broaden concept vocabulary now | **No** |
| QA generation | **Still not authorized** |

For the October 15 mentor meeting, a concise framing is:

> **The concept-first strategy worked operationally, but the first S2ORC shard is source-limited: heat yields 10 papers, fire weather yields 4, and bare FWI is highly ambiguous. We are holding the ontology fixed, adding retrieval disambiguation for the acronym, and requesting a more domain-appropriate source with identical queries.**

That distinguishes computed evidence from the planned response.

---

## Next bounded objective

Proceed with:

**M4-WP3 — Concept-First Corpus Provenance, Disambiguation, and Source-Yield Review**

It should have two components.

### A. Finalize `LITCORPUS-01-conceptfirst-v1` provenance

For each production arm report:

- query file/hash;
- source shard;
- araiadoc commit;
- matcher semantics;
- raw returned count;
- post-FWI-disambiguation count where applicable;
- unique count;
- cross-arm duplicate count;
- bytes / format;
- manifest hash;
- stable item IDs.

Also include diagnostic sensitivity:

- production yield;
- topical-only diagnostic yield;
- difference;
- documented collision categories.

### B. Source-expansion request / comparison plan

Record:

- requested source characteristics;
- request date;
- recipient/team;
- whether one or multiple shards will be supplied;
- requirement that frozen v1 queries be reused unchanged;
- planned per-source yield comparison.

### C. Geography-filter preflight

After the v1 corpus is frozen:

- run only the already approved place terms;
- record lexical hits and spans;
- freeze candidate IDs;
- do not read them semantically.

If a larger source arrives before WP3 closes, it may be inventoried as a second source arm in the same package **only if the same frozen query/provenance protocol is used**. Otherwise, treat it as M4-WP3b.

---

## Acceptance criteria

M4-WP3 is ready for GUIDANCE review when:

1. `LITCORPUS-01-conceptfirst-v1` has a stable corpus identity.

2. Both production query hashes are pinned.

3. Both diagnostic query hashes are pinned and labeled diagnostic-only.

4. Unused broader queries are preserved but clearly marked non-executed / non-corpus-defining.

5. S2ORC shard identity, bytes, and record count are recorded.

6. araiadoc commit and execution configuration are recorded.

7. Production yield is separately reported for both families.

8. Diagnostic yield is separately reported.

9. Diagnostic results are not assigned corpus identity.

10. `FWI` collision evidence is preserved.

11. The revised bare-`FWI` disambiguation rule is versioned and deterministic.

12. Bare `FWI` alone cannot admit a document.

13. Longer unambiguous fire-weather terms remain directly eligible.

14. Same-document disambiguator hits are stored with exact source locations.

15. No change is made to the scientific concept-map identity of `FWI`.

16. Current outputs remain external to Git except manifests/provenance/small evidence.

17. Every v1 document receives a stable ID/hash.

18. Cross-arm duplicates are identifiable.

19. Missing year/venue/author remain explicit `unknown`.

20. Source-domain skew is documented.

21. A request for better domain coverage is recorded.

22. New-source collection is specified to reuse the same frozen production queries initially.

23. Geography filtering occurs only after corpus freeze.

24. Any geography-filter candidate list is frozen before semantic reading.

25. No semantic claim extraction or QA occurs.

---

## Do not do yet

Do not widen the scientific vocabulary to compensate for low source yield.

Do not remove `FWI` from the ontology.

Do not allow bare `FWI` alone to define fire-weather retrieval in heterogeneous corpora.

Do not promote the topical-only diagnostic sets into corpus versions.

Do not merge diagnostic and production yields.

Do not add U.S. geography to collection queries.

Do not semantically inspect the 14 current papers merely because the set is small.

Do not repeatedly change source/query combinations until a positive match appears.

Do not infer that fire-weather literature is rare based on this shard.

Do not infer that extreme-heat literature is predominantly biomedical based on this shard.

Do not discard `LITCORPUS-01` when a better source arrives.

Do not begin QA.

The next scientific comparison should hold the **concept definition and query fixed** while changing the **source coverage**:

> **same concept → same query → different literature source → compare yield**

That will tell us whether the bottleneck is truly source coverage before changing anything about the benchmark's semantic definition.
