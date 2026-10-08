# M4-WP2 --- semantic inspection of the four frozen candidates (Phase 1: reader 1)

**Fields 1--9 describe Phase 1** (reader 1's reading, the hit classification,
the D-019 bookkeeping), written at `258536a`. **Fields 10--15 close the
package** after Phase 2 (the blind reading, `939111e`, run in a separate
session that saw none of reader 1's outputs) and Phase 3 (adjudication); the
compatibility run (Phase 4) is reported in
[`M5_WP2_REPORT.md`](M5_WP2_REPORT.md). The four items are a
**relevance-guided candidate sample, not representative.** Authorized by
[`docs/M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md`](../../docs/M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md)
(D-019). No QA is generated.

## 1. Milestone ID and title

**M4-WP2 --- semantic inspection of the four frozen relevance-guided
candidates (M4-WP2r1: Phase 1, reader 1; plus D-019 bookkeeping).** M4
(literature). **M1 remains open** (D-014).

## 2. Objective

Read exactly `LIT-000166`, `LIT-000519`, `LIT-001501`, `LIT-001536` under the
WP1 rubric unchanged; record claims with exact spans before looking at any
retrieval hit location; then classify every hit as substantive or incidental;
and carry out the ruling's bookkeeping (D-019, evidence tiers, C-2 revision,
report field 14s, state, knowledge list).

**Excluded, and not done:** the blind second reading; adjudication; any
compatibility run (no claim has been compared with any prototype); any new
surface term or synonym; any change to the frozen candidates or retrieval
artifacts; QA.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/m4-wp2-read`, from `main` at **`e7da7cc`** |
| Phase A --- D-019 bookkeeping | `410a7d0` |
| Phases B--D --- reader 1, hits, documents | **`258536a`** (on `work/m4-wp2-read`) |
| Phase 2 --- blind reading (separate session) | **`939111e`** (on `work/m4-wp2-blind`) |
| Phase 3 --- adjudication; M5-WP2 inputs frozen | **`59880d7`** (on `work/m4-wp2-adj`, after merging `939111e` at `ab80335`) |
| Phase 4, mentor report, fields 10--15, state | the commit after `59880d7`; its SHA travels with the hand-back |
| Remote | **not pushed, not merged** |

## 4. Data version and checksums

| Object | SHA-256 |
| --- | --- |
| `LIT-000166` = `14300.json` | `d63010c65b1955f330d76d9bf6c51e4114248a3e261af1b5160d40095a5fb594` |
| `LIT-000519` = `221115000.json` | `ea74ebe3a9f45917c4c5dce172a912f3951e638201e66c0e1cec87b963827f18` |
| `LIT-001501` = `270320300.json` | `d6ffb5e77697c932a4983dbb74a7d63cb4fccec955f0e12be51a63b2a2269c4b` |
| `LIT-001536` = `272852900.json` | `18b1fe556b697e2a97c609744268f89d88949401e1c905f1f91233362bd28ab3` |
| `artifacts/literature/wp2_candidates.json` (frozen, **unchanged**) | `e155e70e338ffb67f8c881a8a3fdb794e28c0f048c43afc10b0a723135ec8d9c` |
| Corpus manifest (`LITCORPUS-00`) | `3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a` |
| `data/metadata/concept_map.yaml` (**unchanged**) | `6ec6b081658e82b5fba4171bcd3135f69ce71710a7a515f32cac83404ebd3664` |

Each candidate file was verified against the manifest before decoding (fail
closed), at reading and at every build. Output hashes are in the run records
(`build_wp2_claims`, `wp2_hit_classification`). `FullData.csv` was not read.

## 5. Environment and execution location

conda environment `climrr`, Python 3.11.16, location `local`; D-007 pins
matched. Corpus read from `literature_corpus_root` in the untracked config.
Sophia not used.

## 6. Work completed

**Phase A (bookkeeping).** D-019 in `DECISION_LOG.md`; the ruling tracked as
placed and added to `KNOWLEDGE_FILES`; field 14 of the M4-WP1b and M4-WP2
retrieval reports records the GUIDANCE outcome. **Evidence tiers**:
`climrr.wp1b.evidence_tier`; the WP1 adjudicated records regenerated with
`evidence_tier` (A 1, B 18, C 10) --- a test proves nothing else changed since
`e7da7cc`; documented in `docs/BRIDGE_ELIGIBILITY.md` §3. **Claim-type ties**:
`compare_time` returns `not_evaluable` (`claim_type_unresolved_tie`) instead of
applying T-2 to an `unresolved_tie`. **C-2 revised** (`compat.compare_concept`,
`compat.family_term_hits`): boundary-aware occurrence of an approved
family term inside the concept value, using `climrr.conceptmap.find_term`
(tested to be the function the retrieval scan calls), recording family,
surface term, `[start, end)`, entry and decision id. Required cases tested:
`"heat index trends"` → family match; `"urban heat island"`, `"wildfire smoke
exposure"` → `not_evaluable`; `"FWIs"` → no match.

**Phase B (reading).** Each candidate verified and read completely. The
reading is data in `scripts/wp2_extractions.py`; `scripts/build_wp2_claims.py`
runs it through **the WP1 builder unchanged** (`build_wp1_claims.build_item`,
`verify_record`) --- exact-search spans, re-slicing, rubric checks --- and adds
`evidence_tier: C`. **The hit list was not opened until all four records were
built.**

**Phase C (hits).** `scripts/wp2_hit_classification.py`: every one of the 61
frozen hits re-sliced from source and classified with a reason; overlap with
promoted claims **computed** from spans.

**Phase D.** `docs/LITERATURE_WP2_READING.md` (generated by
`scripts/render_wp2_reading.py`), this report, `PROJECT_STATE.md`.

Checks so far: `pytest` **753 passed** (`climrr` env); every span (63) and
every hit (61) re-slices from the verified source (tests ran, not skipped);
secrets/paths scan 0 hits at each commit.

## 7. Deliverables and exact file paths

**New:** `scripts/wp2_extractions.py`, `scripts/build_wp2_claims.py`,
`scripts/wp2_hit_classification.py`, `scripts/render_wp2_reading.py`,
`artifacts/literature/wp2_claims/LIT-000166.json`, `LIT-000519.json`,
`LIT-001501.json`, `LIT-001536.json`, `wp2_claims_summary.json`,
`artifacts/literature/wp2_hit_classification.json`,
`docs/LITERATURE_WP2_READING.md`,
`docs/M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md` (tracked as placed),
`tests/test_wp2_claims.py`, this report, run records `reports/runs/20261008T2256*`
to `2300*`.

**Changed:** `src/climrr/compat.py`, `src/climrr/wp1b.py`,
`scripts/wp1b_adjudicate.py`, `artifacts/literature/wp1_claims_adjudicated/`
(`evidence_tier` added), `docs/LITERATURE_WP1B_ADJUDICATION.md` (tier line),
`docs/BRIDGE_ELIGIBILITY.md`, `docs/DECISION_LOG.md`, `docs/PROJECT_STATE.md`,
`reports/milestones/M4_WP1B_REPORT.md` and `M4_WP2_RETRIEVAL_REPORT.md` (field
14), `scripts/stage_knowledge.py`, `tests/test_conceptmap.py`,
`tests/test_wp1b.py`.

## 8. Methods and rules that affect scientific meaning

1. **The WP1 rubric, unchanged** (D-016, D-017): scope rule; claims 0--5;
   six dimensions each `explicit` / `inferred` (with support span) /
   `unknown`; `scenario` is a climate/emissions scenario only; experimental
   treatments in `experimental_condition`; exact-search code-point spans on the
   unnormalized string.
2. **Selection under the cap**: the paper's own findings first, then
   background framing the hazard the paper examines. Passages not promoted are
   kept with reasons (17).
3. **No dimension was filled from a hit.** Geography and concept values come
   from the claim's own span or a quoted support span.
4. **Hit classes** (Phase C): `substantive` --- the passage states something
   about the concept or place and the paper treats it (studies, analyses, or
   reviews it beyond a list entry); `incidental` --- surname, citation or
   reference entry, instrument-network name, list entry, passing mention, or a
   different referent under the same letters.
5. **Evidence tiers** (D-019) and **revised C-2** (field 6). C-2 now uses the
   frozen matcher's exact internal whitespace: a double space no longer
   matches, as it did under whole-field equality (field 11).

## 9. Results with compact tables or examples

| Item | Paper (as read) | Scope | Terminal | Claims | Hits | Substantive | Incidental |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| `LIT-000166` | SPITFIRE: global process-based fire regime model | in_scope_hazard | claims_extracted | 5 | 2 | 0 | 2 |
| `LIT-000519` | Daily Fire Hazard Index, Sardinia | in_scope_hazard | claims_extracted | 5 | 14 | 8 | 6 |
| `LIT-001501` | 2017-18 precipitation whiplash and wildfires, Southern Great Plains | in_scope_hazard | claims_extracted | 5 | 33 | 8 | 25 |
| `LIT-001536` | Summer heat exposure at US prisons | in_scope_hazard | claims_extracted | 5 | 12 | 10 | 2 |
| **Total** | | | | **20** | **61** | **26** | **35** |

**What the hits turned out to be:**

- **`Stephens` (`LIT-000166`) is an author surname** ("Stephens and Finney,
  2002") --- the paper's only place hit. Its one concept hit is the Fire
  Weather Index named in a list of indices the model does not use. **Both hits
  incidental.**
- **`California` is never an affiliation** in these four. In `LIT-000519` it is
  a passing mention of where the method's predecessor was validated; in
  `LIT-001501` it is always another region studied by others or a reference
  entry; in `LIT-001536` it is a study state in 8 of 9 hits (one is a citation
  author, "State of California, 2021").
- **All 11 `FWI` hits in `LIT-001501` are the Oklahoma Mesonet *fractional water
  index* (soil moisture), not the Fire Weather Index.** The paper qualified
  through letters that name something else.
- **`LIT-000519` is the only item whose concept hits are substantive** (8 of
  13): its introduction reviews the Fire Weather Index System; its own
  analysis concerns a different index (DFHI).
- `heat index` (`LIT-001536`): a single cited aside on why the paper uses air
  temperature; incidental.
- 3 hits fall inside a promoted claim's evidence: `FWI` in `LIT-000519-C5`,
  `Oklahoma` in `LIT-001501-C4`, `California` in `LIT-001536-C1`.

**Screens over the 20 claims** (deterministic, `render_wp2_reading.py`):

| Screen | Claims |
| --- | --- |
| Geography names a US place | **11** --- 5 `explicit` (`LIT-000166-C4` west coast of the USA; `LIT-001501-C4` Dewey County, NW Oklahoma; `LIT-001501-C5` the SGP; `LIT-001536-C1` California, Arizona, Nevada; `LIT-001536-C2` 44 states and DC), 6 `inferred` |
| …of which name a prototype place term | `Oklahoma`: `LIT-001501-C2` (inferred), `-C4` (explicit); `California`: `LIT-001536-C1` (explicit); `Stephens`: none |
| Approved pilot family term in the concept field (revised C-2 search) | **1** --- `LIT-000519-C5`, "FWI" (Fire Weather Index, a cited background claim with geography `unknown`) |
| Named climate/emissions scenario | **0** |

No compatibility judgement has been made; whether any of these pairs with a
prototype is Phase 4's question.

## 10. Validation performed

| Check | Result |
| --- | --- |
| `pytest` (`climrr` env) | **784 passed** at the final commit (753 at `258536a`) |
| `scripts/verify_no_secrets_or_paths.py` | **0 hits**, after staging, at every commit |
| Both readings pinned | reader-1 files equal their `258536a` blobs, blind files their `939111e` blobs (tests) |
| Span integrity | **63** reader-1 and **66** blind spans re-slice from the hash-verified sources; 0 failures (test ran, not skipped) |
| Hits | all 61 re-slice; each classified once |
| Adjudication | every alignment and decision re-derives from the frozen readings and recorded judgements; **no override used** (test) |
| Preservation | every reader-1 claim keeps its id and every original field (test) |

## 11. Failures, rejected cases, and known limitations

- **The adjudicator is reader 1** (the prototype-exposed EXECUTOR), as in
  WP1b. No contested scope arose (4/4 agreement) and no override was used, but
  the 7 `adjudicated_modified` decisions are reader 1's judgements.
- **Reader 1 knew the retrieval terms and hit counts** (not locations) before
  reading; the blind reader knew none of them. Reader 1 promoted the one
  pilot-term claim (`LIT-000519-C5`, "FWI" background); **the blind reader did
  not** --- so it is single-reader, tier C.
- **13 of 26 adjudicated claims are single-reader** (7 reader-1-only, 6
  blind-only): the two readers chose different claims under the five-claim cap
  more often than in WP1b (13 aligned of 20 / 19).
- **The blind session's isolation cannot be verified from its artifacts.** Its
  branch never held reader 1's outputs, but its base (`e7da7cc`) holds the hit
  list and the prototypes, and its summary has no protocol disclosure (WP1b's
  did). Criterion 6 is therefore put to Kaiyuan, who ran it.
- **The blind reader's schema differed from WP1b's** (dimension `status`,
  `support_span`, a scope object, `$["key"]` paths). An adapter normalised it;
  nothing in the blind records was edited.
- One reader-1 build failed once on a stored combining accent; fixed by quoting
  the stored code points (Phase 1).
- **n is four.** Agreement figures describe these readings only.

## 12. Deviations from the approved plan

1. Phase B (reading) preceded the Phase A code in WP2r1, so the bookkeeping
   could not reach the reading.
2. C-2 now matches internal whitespace exactly (the frozen matcher's rule); a
   double space no longer matches as under whole-field equality.
3. Blind-only claims take ids `LIT-…-B<n>` (as in WP1b).
4. Each reader-1 claim keeps its first-pass tier as
   `first_pass_evidence_tier` beside the adjudicated `evidence_tier`.

## 13. Open decisions and mentor questions

| Item | Owner | Why it matters |
| --- | --- | --- |
| What the WP2 blind session was given and opened (criterion 6) | Kaiyuan | the blind record carries no protocol disclosure, unlike WP1b's |
| Family-level match with disclosed metric/scenario gaps --- useful, or exact match required? | mentor | decides whether a `supporting_qualified` link could ever be used |
| Zero eligible pairs: widen place terms to all US states (a predeclared WP2b), or change the unit to a region papers name | mentor / GUIDANCE | the next relevance-guided experiment |
| Extend the G-2 disjoint list (Sardinia, European countries, the Sahel are now `not_evaluable`) | GUIDANCE | affects only `incompatible` vs `not_evaluable`, never eligibility |
| P-CELL-1/P-COUNTY-1 baseline citations (D-019 cleanup) | COORDINATOR | provenance consistency |

## 14. Proposed gate status

D-019 acceptance criteria (Phase 1 criteria 1--5 and 12--17 were evidenced at
`258536a`, fields 6--9):

| # | Criterion (abridged) | Status | Evidence |
| ---: | --- | --- | --- |
| 6 | Blind reader received no hit locations, prototypes, first reading or M5 results | **PARTLY VERIFIABLE** | reader 1's outputs were never on the blind branch (`work/m4-wp2-blind` branches from `e7da7cc`, which lacks them). But that base **does** contain the hit list (`wp2_candidates.json`) and the prototypes, and the blind summary records **no disclosure** of what the session was given or opened. Confirmation needed from Kaiyuan, who ran it |
| 7 | Blind reading frozen before comparison | **MET** | `939111e` precedes `ab80335`; blind files equal their `939111e` blobs (test) |
| 8 | Adjudication preserves both readings and every disagreement | **MET** | `wp2_comparison.json`; adjudicated records carry both values; originals untouched |
| 9 | Rule 3 span-limited interpretation | **MET** | every 3c adoption is the span-stated common part (`LITERATURE_WP2_ADJUDICATION.md`) |
| 10 | J-1 not generalised; new overrides justified | **MET** | no override used; the script refuses one |
| 11 | Ties stay unresolved | **MET (none arose)** | claim types agreed on all 13 pairs |
| 12 | Every final claim carries a tier | **MET** | A 6, B 7, C 13 |
| 13--16 | C-2: approved terms only, boundary-aware in the concept field, term and span recorded, no synonyms | **MET** | `M5_WP2_COMPATIBILITY.md` (the one C-2 match records "FWI" [0, 3), `fire_weather_index`, D-018) |
| 17 | Metric-level distinct from family-level | **MET** | 0 metric-level, 2 family-level judgments |
| 18 | All adjudicated claims × all three prototypes | **MET** | 26 × 3 = 78 pairs, each once (test) |
| 19 | P-STATE-1 v2 used; old M5-WP1 freeze untouched | **MET** | `m5wp2_inputs.json` names v2 and pins the M5-WP1 hashes (test) |
| 20 | Unknown scenario stays `not_evaluable` | **MET** | scenario `not_evaluable` 78/78 |
| 21 | Family-level concept cannot yield `supporting` | **MET** | relation tests |
| 22 | Contested / single-reader claim cannot alone establish a bridge | **MET** | no eligible pair; the two concept-positive pairs are tier C and carry the tier |
| 23 | Eligibility and relation separate outputs | **MET** | separate fields in every row |
| 24 | No widening inside this package if no bridge emerges | **MET** | sample stays 4; widening is a question in the mentor report |
| 25 | No QA | **MET** | none |

**Proposed status:** ready for GUIDANCE review --- M4-WP2 complete (two
readings, adjudication) with the adjudicator's non-independence disclosed;
compatibility result in `M5_WP2_REPORT.md`.

## 15. Proposed next bounded objective

Take the mentor's answers (family-level usefulness; widen places or change the
unit) and, only then, predeclare a WP2b retrieval experiment with its place
terms and prototype-selection rule fixed before any reading.
