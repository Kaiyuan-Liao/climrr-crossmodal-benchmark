# ClimRR Cross-Modal Benchmark — M4-WP0 GUIDANCE Ruling

**Milestone:** M4 — Literature Ingestion and Structured Claim Pilot  
**Work package:** M4-WP0 — Literature Corpus Provenance and Inventory  
**GUIDANCE status:** PASS WITH ACTIONS  
**Scope:** Provenance and inventory preflight only; no paper-level semantic work

> This ruling authorizes a bounded corpus-provenance preflight. It does **not** authorize paper reading, claim extraction, prototype matching, semantic bridges, or QA generation.

---

## Gate status

**PASS WITH ACTIONS**

Items **(1)–(4)** are authorized as a bounded **corpus-provenance preflight**.

The package should be named **M4-WP0 — Literature Corpus Provenance and Inventory**, rather than M1-WP5.

This work prepares the external evidence source for later M4 processing but is **not yet M4 claim work**, because no paper is opened, parsed, retrieved, or interpreted.

One boundary remains unchanged:

> **QA generation is still not authorized.**

---

## Current-stage assessment

The project now has two independently created sources whose provenance must be understood before they are connected:

- the ClimRR-side prototype representation;
- the externally collected literature corpus.

The supplied Boolean query answers an important provenance question: **what the corpus was actually collected for**.

Its hazard-scoped structure and generic context terms are useful findings about **collection scope**, but they are not evidence about the content of any individual paper.

Therefore:

> **The Boolean query explains how the candidate corpus was collected. It does not establish what any paper contains or which prototype a paper supports.**

This is the correct moment for a provenance/inventory package before M4 begins opening documents.

---

## Evidence check

### 1. Pin the exact Boolean query

**Authorized.**

Store the original query exactly as supplied.

Record alongside it:

- exact query text;
- SHA-256;
- person/source who supplied it;
- stated collector, if known;
- platform/database where it was executed, if known;
- execution date, if known;
- export / collection date, if known;
- unknown fields explicitly as `unknown`;
- date the project received the query;
- provenance statement distinguishing reported facts from independently verified facts.

Any normalized version used for parsing must be stored separately as a **derived artifact**.

### 2. Deterministic query parsing

**Authorized.**

The parser may decompose the Boolean expression into:

- hazard-term groups;
- generic context terms;
- Boolean structure;
- conjunction / disjunction structure;
- quoted phrases versus unquoted terms.

The parsed representation must retain pointers back to the exact source query text.

Deterministic lexical normalization is allowed. Scientific reinterpretation is not.

### 3. Query-to-prototype comparison

**Authorized, with careful naming.**

Call this **query-scope coverage**, not corpus coverage.

It may identify:

- prototype concepts explicitly present in the query;
- hazard groups in the query that the pilot currently ignores;
- geographic/scenario/horizon dimensions absent from the query.

It may **not** conclude that a particular paper contains relevant evidence, that the corpus adequately covers a phenomenon, or that individual papers lack dimensions absent from the query.

### 4. Read-only external corpus inventory

**Authorized.**

Keep the literature corpus external. No papers should be copied into the repository.

Recommended manifest fields:

- stable corpus item ID;
- relative path from configured corpus root;
- basename;
- extension / format;
- byte size;
- SHA-256;
- duplicate-hash group, if any;
- inventory timestamp;
- corpus-root config reference;
- accessibility status.

Computing SHA-256 necessarily reads raw file bytes. Therefore the correct boundary is:

> **No document content parsing, text extraction, PDF rendering, metadata extraction, or semantic inspection. Byte-level access for hashing and inventory operations only.**

---

## Scientific risks

### 1. Query coverage being mistaken for evidence coverage

A query containing `"heat index"` proves only that the collection process allowed results matching that search expression.

It does not establish that the corpus contains supporting heat-index evidence.

### 2. Missing query dimensions being overinterpreted

The absence of geography, RCP scenario, or temporal-horizon terms is a finding about collection design, not about individual paper contents.

### 3. Hazard groups are not per-paper labels

Because no keyword-to-paper mapping file exists, do not assign papers to hazard groups based only on the collection query.

### 4. Duplicate corpus items

Exact-byte duplicates could inflate later sampling or apparent evidence volume. Identify them now, but do not delete them.

### 5. Prototype-first confirmation bias

Later literature work must extract what papers actually claim before M5 decides whether those claims support, contradict, or merely relate to table-side phenomena.

---

## Required actions

1. Create **M4-WP0 — Literature Corpus Provenance and Inventory**.

2. Track the supplied Boolean query as an immutable provenance artifact with exact text, hash, reported source, and known/unknown execution metadata.

3. Create a separate deterministic parsed-query artifact.

4. Name the prototype comparison **query-scope coverage**.

5. Distinguish at least:
   - exact query-term match;
   - deterministic normalized lexical match;
   - absent from query;
   - inferred conceptual relationship, if introduced later.

6. Inventory every corpus file without semantic inspection.

7. Permit raw-byte reads only for hashing, size, and format/path inventory.

8. Detect exact-byte duplicates through SHA-256 but do not remove files.

9. Keep all corpus documents external.

10. Store only manifests, hashes, config references, provenance records, and compact summaries in the repository.

11. Record the mentor-answer-sheet outcome independently:
    - exact responses if obtained;
    - otherwise `no review occurred`, with no status promotion.

12. Do **not** interpret light group-meeting feedback as owner confirmation of field semantics.

---

## Decisions for Kaiyuan or mentor

| Proposed component                                 | Ruling                                          |
| -------------------------------------------------- | ----------------------------------------------- |
| Pin exact collection query                         | **Authorized**                                  |
| Hash and provenance record                         | **Authorized**                                  |
| Deterministic Boolean parsing                      | **Authorized**                                  |
| Query vs. prototype concept comparison             | **Authorized as query-scope coverage**          |
| Identify pilot-ignored hazard groups               | **Authorized**                                  |
| Record absence of geo/scenario/horizon constraints | **Authorized if parser confirms it**            |
| External-folder inventory                          | **Authorized**                                  |
| SHA-256 of corpus files                            | **Authorized via byte-level reads only**        |
| Open/read PDFs                                     | **Not authorized yet**                          |
| Parse document metadata/text                       | **Not authorized in WP0**                       |
| Assign hazard label to individual paper            | **Not authorized without paper-level evidence** |
| Literature retrieval/search                        | **Not authorized in WP0**                       |
| QA generation                                      | **Not authorized**                              |

The September 14 group feedback may be recorded conservatively as:

> **No material objection to the prototype-unit design was raised.**

Do not upgrade that into scientific validation unless stronger feedback was actually given.

---

## Next bounded objective

After M4-WP0 passes, the first actual literature step should be:

**M4-WP1 — Small, deterministic literature-ingestion and structured-claim pilot.**

It should **not** begin by searching the corpus for the existing prototypes.

Instead, select a **small deterministic sample from the frozen corpus manifest** and ask:

> **Can we reproducibly turn these papers into source-grounded literature claims with exact evidence locations?**

A suitable first pilot is approximately **6–12 unique papers**, small enough for complete inspection.

Selection should be deterministic and independent of whether papers appear likely to support a prototype.

For each selected paper, M4-WP1 should produce:

- stable paper ID linked to the WP0 manifest;
- file SHA-256;
- parse status;
- title / authors / year only if actually recoverable;
- exact evidence locations;
- a small set of structured claims;
- concept / hazard represented by each claim;
- geography explicitly stated;
- scenario / time explicitly stated;
- claim direction / type;
- explicit vs. inferred status;
- extraction confidence as workflow metadata only;
- rejected / ambiguous passages.

Crucially:

> **M4-WP1 extracts claims from papers without deciding whether they match a ClimRR prototype.**

Prototype-to-claim compatibility begins later, in M5.

---

## Acceptance criteria

M4-WP0 is ready for review when:

1. The exact original query is stored unchanged and hash-pinned.
2. Query provenance explicitly distinguishes known facts from `unknown`.
3. The parsed-query representation is reproducible from the exact source query.
4. Hazard groups and context terms are deterministically represented.
5. The query-scope table clearly separates prototype concepts explicitly represented in the query, query hazard groups outside the pilot, and dimensions absent from the query.
6. No query-level observation is described as evidence about individual papers.
7. Every corpus file receives a stable manifest entry.
8. Every manifest entry contains at least relative path, format, bytes, and SHA-256.
9. Exact-byte duplicate groups are identifiable.
10. No corpus document is copied into Git.
11. No document text, PDF page, abstract, metadata, or claim is semantically inspected.
12. Raw-file reads are limited to provenance/inventory operations such as hashing.
13. The corpus manifest is reproducible against the configured external corpus root.
14. No individual paper receives a hazard-group assignment from the Boolean query alone.
15. The package explicitly records absence of geographic/scenario/horizon query constraints if deterministic parsing confirms it.
16. The inventory design provides stable IDs and hashes suitable for a later bounded M4-WP1 sample.
17. The mentor-review outcome is recorded without inventing confirmation.
18. Nothing in WP0 performs or claims claim extraction, prototype matching, semantic bridging, or QA generation.

---

## Do not do yet

Do not open papers for scientific reading.

Do not extract titles or abstracts merely because a PDF library makes them easy to access.

Do not run OCR.

Do not parse full text.

Do not search the corpus for `heat index`, `FWI`, or prototype geography.

Do not assign papers to hazard groups based on filenames or the collection query.

Do not calculate corpus relevance to a prototype.

Do not generate embeddings.

Do not create table-to-paper pairs.

Do not extract supporting or contradictory claims.

Do not start M5 bridge scoring.

Do not generate benchmark QA yet.

The evidence chain should remain:

> **corpus provenance → bounded paper ingestion → structured claims → validated semantic bridges → QA**

That ordering preserves the project rule:

> **establish a defensible semantic relationship before generating questions.**
