# ClimRR Cross-Modal Benchmark — M4-WP1 Review and M5-WP1 GUIDANCE Ruling

**Milestone context:** M4 literature-ingestion pilot complete; M5 machinery validation next  
**Reviewed package:** M4-WP1 — Deterministic 10-paper ingestion and structured-claim pilot  
**Next work package:** M5-WP1 — Deterministic negative-case compatibility validation  
**GUIDANCE status:** PASS WITH ACTIONS

> This ruling distinguishes two thresholds: M4-WP1 is sufficient to produce **provisional structured claims** for compatibility-machinery validation, but not yet sufficient to treat those claims as independently validated literature evidence. M5-WP1 is authorized only as deterministic compatibility validation on the fixed provisional set.

---

## Gate status

**PASS WITH ACTIONS**

M4-WP1 **passes as an ingestion and structured-claim pilot**.

All 27 extracted claims remain **single-reader provisional literature claims** until the independent-review action below is closed.

M5-WP1 is authorized as **deterministic compatibility-mechanism validation** on the fixed **27 claims × 3 prototypes** set.

However:

> **M5-WP1 may use the current claims to test compatibility machinery, but its outputs are validation results over provisional claims—not accepted semantic bridges and not definitive evidence that the corpus contains zero bridges.**

One schema correction is required before matrix generation: experimental laboratory treatments currently stored under `scenario` must move to an `experimental_condition` or equivalent field. They are not climate/emissions scenarios.

After that correction:

> **climate scenario = `unknown` for all 27 WP1 claims.**

---

## Current-stage assessment

M4-WP1 substantially succeeded at its intended purpose.

The sample was frozen before content inspection and remained content-independent. The workflow produced heterogeneous outcomes rather than forcing relevance:

- 6 items with claims;
- 27 claims total;
- 3 off-topic items;
- 1 ambiguous-only item;
- 22 rejected or ambiguous passages retained.

The JSON source structure was genuinely irregular:

- all ten files were flat JSON objects;
- all values were strings;
- 45 distinct keys appeared;
- no two files shared the same key sequence.

The strongest part of WP1 is the provenance chain:

- 96 source spans;
- all re-sliced from the verified decoded source;
- all matched exactly;
- evidence hashes preserved;
- offsets computed on unnormalized Unicode code points.

The main residual limitation is epistemic rather than computational:

- one language-model EXECUTOR performed the reading;
- that same EXECUTOR had prior exposure to the ClimRR prototype work;
- the code firewall prevents direct consultation but cannot erase prior exposure.

This does **not** invalidate WP1 as a workflow pilot. It constrains how M5 may use the claims scientifically.

---

## Evidence check

### 1. Tracked verbatim excerpts

**Acceptable, with minimization rules.**

Do **not** replace all evidence text with hash + offsets only.

Short verbatim excerpts provide audit value because they let a reviewer inspect whether:

- a claim faithfully represents the paper;
- hedging was preserved;
- a dimension tagged `explicit` is actually stated;
- a scope judgment is defensible.

Ruling:

> **Keep short evidence excerpts, but treat them as minimal evidence windows—not as a second literature corpus.**

Going forward:

- retain only the smallest passage needed to support the claim or decision;
- do not track whole sections merely for convenience;
- do not concatenate large source passages into reports;
- preserve hash + offsets as the authoritative locator;
- if repository policy later requires text removal, the record must remain reconstructible from the external corpus and offsets.

### 2. Scope rule and the two judgment calls

**Approved.**

The scope rule is conservative and appropriate:

- `in_scope_hazard` → may yield claims;
- `off_topic` → terminal, zero claims;
- `ambiguous` → `ambiguous_only`, zero promoted claims.

Specific rulings:

- **`LIT-000571`: accept `in_scope_hazard (borderline)`**.
- **`LIT-000761`: accept `ambiguous_only`**.

These decisions validate the pilot rule, not a universal ontology of climate-hazard papers.

### 3. Second independent reader

**Required before these claims become accepted M5 evidence, but not required before M5-WP1 machinery is implemented.**

M5-WP1 may proceed now using a status such as:

```text
claim_validation_status: single_reader_provisional
```

Before any table↔literature pair is accepted as an M5 bridge, before “zero compatible pairs” becomes a scientific conclusion about the literature sample, or before these claims become QA evidence, a second independent reading must occur.

Use a **blind second pass over all ten papers**, not a subsample.

The second reader should:

- start from the same ten frozen corpus items;
- use the extraction rubric;
- not see the ClimRR prototypes;
- not see the first reader's scope labels or claims during initial extraction;
- independently assign scope;
- independently extract claims and dimensions;
- preserve exact evidence.

Then compare and adjudicate:

- scope;
- claim inclusion;
- claim type;
- concept;
- geography;
- temporal frame;
- climate scenario / experimental condition;
- direction.

A human reader is ideal but not mandatory for this bounded validation. A genuinely fresh model/session without prototype or first-pass context is acceptable as the second extraction pass, followed by explicit adjudication.

### 4. Scenario schema

**Must be corrected before M5-WP1.**

The two explicit values in `LIT-000191` are experimental temperature / CO₂ treatments, not climate scenarios.

Use separate fields such as:

```text
scenario
experimental_condition
```

For the fixed WP1 set, after migration:

> **climate scenario = `unknown` for 27/27 claims.**

### 5. Proposed deterministic M5 matrix

**Authorized, with conservative compatibility semantics.**

Produce a full **27 × 3 = 81 pair** matrix.

For every dimension:

- `compatible` = compatibility established by an explicit deterministic rule;
- `incompatible` = explicit values establish contradiction/disjointness under a deterministic rule;
- `not_evaluable` = unknown, different granularity, related-but-not-equivalent concept, or no approved deterministic mapping.

Do **not** equate “different” with `incompatible`.

---

## Scientific risks

### 1. Negative-case overclaiming

If the matrix yields zero all-compatible pairs, report only:

> **No fully compatible pair was found under the current deterministic rules in this fixed provisional pilot set.**

Do not generalize that to the full corpus.

### 2. Unknown dimensions acting like negative evidence

`unknown` must never be treated as incompatible.

After schema correction, all 27 claims have climate scenario `unknown`, so scenario becomes `not_evaluable`.

### 3. Concept matching becoming disguised semantic similarity

Do not invent hand-authored synonym mappings simply to produce matches.

Use only exact canonical IDs or previously approved deterministic mappings. Otherwise use `not_evaluable`.

### 4. Direction compared across different quantities

Direction is meaningful only when the underlying quantity/concept is already comparable.

Otherwise:

```text
direction = not_evaluable
```

### 5. Background citations becoming primary evidence

Keep `background_citation` visibly distinct from primary findings, projections, and mechanisms.

### 6. Relevance-guided sampling becoming cherry-picking

If the deterministic pilot yields no bridges, do not manually browse until something fits.

A later relevance-guided sample must still be predeclared and reproducible.

---

## Required actions

Before freezing M4-WP1:

1. Accept M4-WP1 as **PASS WITH ACTIONS**.
2. Preserve all 27 claims as single-reader, provisional, exact-source anchored.
3. Keep tracked evidence excerpts with minimal-evidence-window discipline.
4. Record the accepted scope rule.
5. Record GUIDANCE acceptance of `LIT-000571` and `LIT-000761` classifications.
6. Split experimental treatments from climate scenario before M5.
7. Add claim-level validation status such as:
   - `single_reader_provisional`;
   - `independently_confirmed`;
   - `adjudicated_modified`;
   - `rejected_on_review`.
8. Plan a blind second extraction pass over all ten papers.
9. Refresh WP1 repository bookkeeping before eventual merge so the pushed review head `7ded08e` is reflected accurately.

For M5-WP1:

10. Freeze all 27 claim identities and all three prototype identities.
11. Produce all **81 pairs**.
12. Score:
    - concept;
    - geography;
    - temporal compatibility;
    - climate scenario;
    - direction.
13. For every dimension record:
    - status;
    - deterministic rule ID;
    - claim-side value;
    - prototype-side value;
    - machine-readable reason.
14. Do not encode the expected zero result into tests.

---

## Decisions for Kaiyuan or mentor

| Question | Ruling |
|---|---|
| M4-WP1 gate | **PASS WITH ACTIONS** |
| Track short verbatim evidence | **Yes, minimized and source-anchored** |
| Replace excerpts with hash+offset only | **No** |
| Claims only from `in_scope_hazard` | **Approved** |
| `ambiguous` yields no promoted claims | **Approved** |
| `LIT-000571` | **Accept `in_scope_hazard (borderline)`** |
| `LIT-000761` | **Accept `ambiguous_only`** |
| Independent second reader | **Required before accepted M5 evidence; not before machinery implementation** |
| Experimental treatments under climate `scenario` | **Not acceptable; split field before M5** |
| M5-WP1 27×3 deterministic matrix | **Authorized** |
| Semantic similarity / LLM pair judgment | **Not authorized in M5-WP1** |
| QA generation | **Not authorized** |

The independent reader is needed because the remaining uncertainty is semantic judgment, not source localization.

---

## Next bounded objective

**Authorize M5-WP1 — Deterministic negative-case compatibility validation.**

### Inputs

- fixed 27 WP1 claims;
- fixed three WP3b prototypes;
- claim-level provisional validation status retained.

### Output

Full:

```text
27 × 3 = 81 pair matrix
```

Each pair receives five judgments:

- concept;
- geography;
- time;
- scenario;
- direction.

Each dimension must be one of:

- `compatible`;
- `incompatible`;
- `not_evaluable`.

Each judgment preserves:

- rule ID;
- claim-side value;
- prototype-side value;
- reason.

### When relevance-guided M4-WP2 becomes justified

A relevance-guided follow-up becomes scientifically justified if M5-WP1 shows:

1. deterministic compatibility machinery works correctly on all 81 pairs;
2. the content-independent WP1 sample yields no fully compatible pair, or too few positives to exercise the positive case;
3. failure modes are visible dimension-by-dimension;
4. WP0 independently shows that some prototype concepts were present in corpus collection vocabulary, such as `heat index` and `fire weather`;
5. independent second-reader/adjudication work does not materially overturn the negative pilot conclusion.

At that point, M4-WP2 may optimize **candidate yield**, not estimate corpus prevalence.

A suitable design is:

```text
frozen prototype-derived query terms
→ deterministic lexical search over frozen corpus
→ predeclared filter/ranking rules
→ frozen candidate sample
```

The package must state:

> **This is a relevance-guided candidate-generation sample, not a representative corpus sample.**

The concrete M4-WP2 retrieval rule should return to GUIDANCE after M5-WP1.

---

## Acceptance criteria

M5-WP1 is ready for GUIDANCE review when:

1. Climate scenario and experimental condition are separated before matrix generation.
2. Input identities are frozen for all 27 claims and all three prototypes.
3. Every claim carries `single_reader_provisional` or a later independent-review status.
4. All **81** pairs appear exactly once.
5. Every pair contains all five dimension judgments.
6. Every judgment is one of `compatible`, `incompatible`, `not_evaluable`.
7. Every judgment cites a deterministic rule ID and both compared values.
8. `unknown` always produces `not_evaluable`, never `incompatible`.
9. Concept mismatch is not automatically incompatible.
10. Geography incompatibility requires explicit disjointness.
11. Direction is not evaluated across non-comparable concepts.
12. Experimental treatment never participates in climate-scenario comparison.
13. Claim type remains visible.
14. `background_citation` remains distinguishable from primary findings.
15. No semantic embeddings are computed.
16. No LLM judges pair compatibility.
17. No pair is removed because it appears irrelevant.
18. The implementation does not assert that fully compatible pairs must equal zero.
19. If zero are observed, report only the bounded negative-case conclusion.
20. Do not generalize the result to the full 1,918-item corpus.
21. Independent second reading is either completed before gate review or explicitly pending; if pending, M5-WP1 may pass only as **machinery validation**.
22. No QA is generated.

---

## Do not do yet

Do not treat the 27 claims as independently validated literature truth.

Do not treat `not_evaluable` as incompatibility.

Do not map:

- UHI → heat index;
- wildfire smoke → FWI;
- drought → fire weather;

merely because they are scientifically related.

Do not use an LLM to rescue concept mismatches in M5-WP1.

Do not manually search the corpus for papers likely to match the prototypes yet.

Do not replace the deterministic WP1 sample.

Do not estimate corpus-wide bridge prevalence from ten papers.

Do not authorize a general relevance-ranking pipeline until the negative-case compatibility package has been reviewed.

Do not begin QA generation.

The evidence sequence should remain:

> **single-reader claims → deterministic compatibility machinery → independent claim validation / adjudication → relevance-guided candidate sampling → positive / negative bridge validation → QA**
