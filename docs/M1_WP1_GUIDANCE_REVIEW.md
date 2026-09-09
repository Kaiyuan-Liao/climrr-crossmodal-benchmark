# ClimRR Cross-Modal Benchmark — M1-WP1 GUIDANCE Review

**Milestone:** M1 — Data Grounding and Metadata Audit  
**Work package:** M1-WP1 — Semantics-neutral schema and quality profile + metadata-status inventory  
**GUIDANCE decision:** PASS  
**Review scope:** Work-package review only; **M1 milestone gate is not yet passed**  
**Reviewed branch:** `work/m1-profile`  
**Reviewed head:** `fceee7f06883c18b45fccda7da350fd4c6966ee8`

> This review accepts M1-WP1 and authorizes M1-WP2 only. It does **not** authorize M2 semantic-representation work, M3 phenomenon extraction, literature processing, bridge matching, or QA generation.

---

## Gate status

**PASS**

M1-WP1 is accepted as complete.

This is a **work-package pass, not the M1 milestone gate**. The packet provides sufficient evidence that all nine WP1 acceptance criteria are met, while correctly leaving unresolved metadata unresolved rather than converting plausible mappings into facts.

The branch `work/m1-profile` may therefore be merged into the authoritative project state following the normal single-writer workflow. M1 remains active.

---

## Current-stage assessment

WP1 has achieved what it was intended to achieve: the project now knows what is structurally present across all 275 columns, what the tracked ClimRR dictionary directly supports, and which column semantics still require mentor or ClimRR-author input.

The reproducibility evidence is strong:

- the raw CSV is manifest-pinned;
- the parsing/profiling stack was pinned under D-007 before the artifact was frozen;
- local Python 3.11 / arm64 and Sophia Python 3.13 / x86_64 independently produced the same profile-content hash;
- the pandas cross-check agreed for all 275 columns;
- fail-closed manifest verification remained in force before reads;
- computed structural facts were kept separate from scientific interpretation.

Current metadata-status counts:

| Status                       | Columns |
| ---------------------------- | ------: |
| `verified_from_dictionary`   |      21 |
| `partially_resolved`         |     143 |
| `unresolved`                 |      28 |
| `structurally_observed_only` |      83 |
| **Total**                    | **275** |

This distribution is an honest measurement of the available evidence, not a weakness in WP1.

---

## Evidence check

### 1. `verified_from_dictionary` bar

**Decision: confirm the strict bar. Do not loosen it.**

The dictionary organizes many variables as a section title plus suffix-only field name, while the CSV often uses stem plus suffix. A field such as `tempmaxann_rcp45_midc` may be structurally consistent with the “Temperature Maximum – Annual” section plus `RCP45_MIDC`, but the dictionary does not state that the CSV stem identifies that section.

Therefore, a column must **not** become `verified_from_dictionary` merely because a stem/suffix pattern looks convincing.

Evidence sufficient to promote such a mapping includes:

1. explicit confirmation from the mentor, data owner, or ClimRR authors;
2. an authoritative export/source-generation specification;
3. another authoritative ClimRR artifact explicitly mapping full CSV names to dictionary sections.

Pattern consistency alone is suitable for a **candidate mapping**, not verified truth.

**GUIDANCE preference:** retain 21 conservative verified columns rather than inflate the verified set using an unconfirmed export-structure inference.

### 2. EXECUTOR-authored candidate maps

**Decision: acceptable. Keep them with their current boundaries.**

Their allowed role is:

> **Candidate maps may guide questions and inspection; they may not serve as evidence.**

They must remain explicitly labeled as candidates, separate from authoritative mappings, unable to promote a column to verified status, and prohibited from silently propagating into later phenomenon extraction or bridge scoring.

### 3. Index 117 — `Aggregate_Resilience_Indicator_ = -9`

**Decision: do not infer sentinel meaning and do not delete the column now.**

Deterministic fact:

```text
Index 117: Aggregate_Resilience_Indicator_
Value: -9
Rows carrying it: 62,834 / 62,834
```

Authorized structural conclusion: the field has zero variation and cannot contribute discriminative information in this file.

Not authorized: claiming `-9` means missing, no-data, invalid, suppressed, or any other semantic category.

Therefore:

- do not label `-9` as a sentinel without source confirmation;
- do not physically remove index 117 from the grounded inventory;
- do not use it in later scientific pilot work unless its meaning is clarified.

### 4. WP1 acceptance criteria

The nine WP1 acceptance criteria are accepted as met:

1. Dataset identity explicit.
2. Profiling reproducible.
3. All 275 columns accounted for.
4. Identifiers protected from destructive coercion.
5. Computed properties separated from interpretation.
6. Metadata status evidence-based.
7. Sentinels and missingness not guessed.
8. Metadata-question inventory specific and actionable.
9. Charter cautions enforced.

M1 itself remains open.

---

## Scientific risks

### 1. False metadata closure

The primary risk is promoting plausible but unverified structural correspondences into authoritative semantics. Q1 affects many columns, and the stem-to-section mapping must remain provisional until authoritative confirmation.

### 2. Treating dictionary defects as extraction problems

Q2–Q4 identify genuine source-document issues such as blank or contradictory descriptions. These must not be “repaired” using naming patterns and then treated as source truth.

### 3. Upstream joined-data provenance

Important families remain inadequately described, including `precipdaily_*`, FWI-class fields, geography/Census fields, and socioeconomic/resilience fields. Their provenance matters for future aggregation and literature matching.

### 4. PDF extraction completeness

One page of the 19-page metadata PDF yielded no extracted text. This does not block WP1, but before the **M1 milestone gate**, the project should confirm that the text-empty page contains no metadata relevant to the 275-column inventory.

---

## Required actions

1. **Merge the accepted M1-WP1 branch** using the established single-writer workflow and refresh `PROJECT_STATE.md`.
2. **Preserve the strict verification rule.**
3. **Retain the two candidate maps** as non-authoritative aids only.
4. **Keep index 117 in the grounded inventory** and do not call `-9` a sentinel without evidence.
5. **Resolve the PDF-extraction completeness issue during M1-WP2.**
6. **Preserve D-008 as a user-provided provenance statement** rather than upgrading it into independently verified source provenance.

---

## Decisions for Kaiyuan or mentor

### GUIDANCE decisions now closed

| Question                                           | GUIDANCE decision                                     |
| -------------------------------------------------- | ----------------------------------------------------- |
| Strict `verified_from_dictionary` bar              | **Approved**                                          |
| Looser stem-to-section verification                | **Not authorized without authoritative evidence**     |
| EXECUTOR candidate maps                            | **Approved for question formulation/navigation only** |
| Candidate maps as semantic evidence                | **Not allowed**                                       |
| Index 117 `-9` as sentinel                         | **Not established**                                   |
| Remove index 117 now                               | **No**                                                |
| Use index 117 in later pilot without clarification | **No**                                                |

### Mentor / ClimRR-author priorities

Recommended priority:

1. Q1 — stem-to-section mapping
2. Q7 — `precipdaily_*` family
3. Q8 — FWI-class fields
4. geographic / join-key questions
5. sentinel / fill-code semantics
6. export provenance
7. remaining dictionary defects, spelling mismatches, units, and missingness questions

For Q1, confirmation should identify the **actual mapping**, not merely state that the candidate “looks right.”

---

## Next bounded objective

**Authorize M1-WP2 — Metadata resolution and citable column dictionary.**

The objective is to convert the current evidence inventory into the most complete **source-backed per-column semantic dictionary possible** using mentor answers, ClimRR-author clarification, authoritative project artifacts, and the tracked data dictionary.

Resolution path:

```text
current status
    ↓
specific external answer / authoritative evidence
    ↓
logged source and decision
    ↓
updated per-column status
```

WP2 is **not required to force all 275 columns into verified status**. A field may legitimately remain resolved, partially resolved, unresolved, or permanently undocumented if that state is explicit and traceable.

---

## Acceptance criteria

M1-WP2 will be ready for GUIDANCE review when:

1. Every status change from the WP1 baseline is tied to a specific authoritative answer/source, date, and provenance record.
2. The Q1 stem-to-section mapping is confirmed, corrected, or explicitly left unverified.
3. Q2–Q4 remain documented as dictionary defects until authoritative correction exists.
4. High-impact undocumented families relevant to later pilot planning are resolved or explicitly unresolved.
5. Geographic fields needed for later aggregation have evidence-backed definitions.
6. Sentinel/fill-code semantics are evidence-backed; candidate sentinels remain distinct from confirmed missing-value rules.
7. The known text-empty PDF page is checked for extraction completeness.
8. The per-column dictionary continues to distinguish deterministic structural facts, dictionary-verified facts, mentor/owner-confirmed facts, and unresolved fields.
9. The WP2 report identifies which fields are sufficiently grounded to be considered for later pilot selection, without yet extracting phenomena.

At that point GUIDANCE can determine whether M1 is ready for its milestone gate or needs one small final metadata-resolution package.

---

## Do not do yet

Do **not** begin M2 semantic-schema design or M3 phenomenon extraction.

Specifically, do not yet:

- aggregate grid cells into counties, states, or regions;
- calculate climate-change phenomena;
- define magnitude or salience thresholds;
- construct humid-heat or FWI phenomenon records;
- treat `-9` or other candidate sentinel values as missing without evidence;
- use EXECUTOR candidate maps as scientific truth;
- ingest the external literature corpus;
- retrieve literature passages;
- create embeddings;
- generate or score semantic bridges;
- design or generate QA.

The immediate task remains:

> **Resolve and provenance-track the metadata needed to finish M1.**
