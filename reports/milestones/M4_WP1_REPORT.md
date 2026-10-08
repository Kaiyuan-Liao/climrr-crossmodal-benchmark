# M4-WP1 --- Deterministic 10-paper ingestion and structured-claim pilot

**Ten items, deterministically sampled, for workflow validation; not
representative of the corpus.** Authorised by
[`docs/M4_WP0_REVIEW_MERGE_WP1_GUIDANCE_RULING.md`](../../docs/M4_WP0_REVIEW_MERGE_WP1_GUIDANCE_RULING.md)
(D-016). No claim is related to a ClimRR prototype, and no QA is generated.

## 1. Milestone ID and title

**M4-WP1 --- Deterministic 10-paper ingestion and structured-claim pilot.** The
second work package of **M4, Literature Ingestion and Structured Claim Pilot**.
**M1 remains open** (D-014, D-016).

## 2. Objective

Answer one question: can the project reproducibly inspect a frozen,
content-independent sample of corpus items and turn what those papers actually
state into structured claims with exact source locations --- and return no
claim when that is the honest result?

**Explicitly excluded, and not done:** replacing an off-topic item; stratifying
the sample; estimating relevance from ten items; reading or searching any of
the other 1,908 files; embeddings; ranking; relating any claim to a prototype;
labelling any claim supporting or contradicting; M5; QA.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/m4-wp1`, from `main` at `5ebb330` (the post-merge state refresh on top of `6f24b78`) |
| Phase A --- sample frozen | `6f9006c`, committed 05:17:40Z; **the first corpus file was opened at 05:18:25Z** (the Phase B schema run) |
| Phases B--D | `d728df6` |
| Evidence runs | all four WP1 scripts re-run at `d728df6` on a clean tree; every tracked output reproduced byte for byte |
| This report, `PROJECT_STATE.md`, brief status | `7ded08e` --- **the reviewed head** |
| Remote | **`7ded08e` pushed to `origin/work/m4-wp1`** and reviewed there by GUIDANCE (D-017). **Not merged** |
| D-017 closure (schema split, validation status, bookkeeping) | the commit after `7ded08e`; its SHA travels with the hand-back. **Not pushed**; merge to `main` is Kaiyuan's |

## 4. Data version and checksums

| Object | SHA-256 |
| --- | --- |
| Corpus manifest (`LITCORPUS-00` identity) | `3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a` |
| `artifacts/literature/wp1_sample.json` | `5cb81f9585040dd1d73a89ca7062d3c5e0060112f54e08ef4795db96a657b578` |
| `artifacts/literature/wp1_schema_observed.json` | `a7787ec74537cb19971d690ccc8ee592c0b7ba30cc63bc271af9f6ce7dd94fe9` |
| `artifacts/literature/wp1_claims_summary.json` | `fb913fe4242355af17794b1218ab30b88d0abe84ce53f5c89cf71a18c1f9cdde` (D-017 rebuild; `121b22d9…` at `7ded08e`) |
| `scripts/wp1_extractions.py` (the reading, as data) | `9b1bf6fedd8271ba54af0648ba5ecf32cccda50d530c556ea84a97d64c99b9a2` (D-017 split; `cf4c7002…` at `7ded08e`) |
| `docs/LITERATURE_WP1_PILOT.md` | `398d32866196bd9ff48c5d82e1eedc890608682ed8e88a09467cafca0d9c4a0e` (D-017 re-render; `846ff2b8…` at `7ded08e`) |

Each of the ten sampled files was verified against its manifest SHA-256 before
it was decoded, on every run (fail closed); the per-file hashes are in
`wp1_sample.json` and in each claim record. The corpus stays external.
`data/raw/FullData.csv` was not read.

## 5. Environment and execution location

conda environment `climrr`, Python 3.11.16, macOS-15.3-arm64, `pip freeze`
SHA-256 `8d8e9add…c4`, all six D-007 pins `matches_pin: true`, location
`local`. Sophia not used; D-016 approves local-only execution.

## 6. Work completed

**Phase A.** `src/climrr/litsample.py` and `scripts/sample_corpus.py` derive
the sample from the frozen manifest alone --- ids and duplicate groups, no file
opened --- and write `wp1_sample.json` with the manifest SHA-256, the rule and
the ten ids. Two runs gave the same ids. Committed **before** Phase B.

**Phase B.** `scripts/wp1_schema.py` verifies, decodes and describes each file
--- types, key order, string lengths in code points, nesting --- recording no
string content. Its run record cites the sample's SHA-256.

**Phase C.** The EXECUTOR read all ten files completely, key by key, and
recorded the reading as data in `scripts/wp1_extractions.py`: scope judgement,
bibliographic fields, claims with tagged dimensions, and rejected or ambiguous
passages, each as **exact quoted text**. `scripts/build_wp1_claims.py` locates
every quote in the decoded source, computes the code-point span, slices the
source with it, compares and hashes, and writes
`artifacts/literature/wp1_claims/<item_id>.json`. `src/climrr/litingest.py`
holds the verified read, the structure description and the span functions.

**Phase D.** `scripts/render_wp1_pilot.py` generates
`docs/LITERATURE_WP1_PILOT.md` from the records; this report; state and brief.

## 7. Deliverables and exact file paths

**New:** `src/climrr/litsample.py`, `src/climrr/litingest.py`;
`scripts/sample_corpus.py`, `scripts/wp1_schema.py`,
`scripts/wp1_extractions.py`, `scripts/build_wp1_claims.py`,
`scripts/render_wp1_pilot.py`; `artifacts/literature/wp1_sample.json`,
`artifacts/literature/wp1_schema_observed.json`,
`artifacts/literature/wp1_claims/LIT-000001.json` … `LIT-001711.json` (ten),
`artifacts/literature/wp1_claims_summary.json`;
`docs/LITERATURE_WP1_PILOT.md`; `tests/test_litsample.py`,
`tests/test_wp1_claims.py`; this report; run records `reports/runs/20260929T*`.

**Changed:** `docs/PROJECT_STATE.md`, `docs/MENTOR_BRIEF.md`.

**GUIDANCE ruling on this package:**
[`docs/M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md`](../../docs/M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md)
(D-017, PASS WITH ACTIONS). **Changed at D-017 closure:**
`scripts/wp1_extractions.py`, `scripts/build_wp1_claims.py`,
`scripts/render_wp1_pilot.py`, `tests/test_wp1_claims.py`, the six
`claims_extracted` records, `wp1_claims_summary.json`,
`docs/LITERATURE_WP1_PILOT.md`, `docs/DECISION_LOG.md`, this report;
run records `reports/runs/20261008T*`.

## 8. Methods and rules that affect scientific meaning

**No rule was applied to any ClimRR column.** The rules below decide what the
claim records say.

1. **Sample.** Every 190th `LIT` id from `LIT-000001`; a selected item that is
   the later member of an exact-byte duplicate group is skipped to the next id
   and the skip recorded, and later positions stay on the 190-step grid. No
   skip occurred: the one duplicate pair (`LIT-001483/001484`) is not on the
   grid.
2. **Who read.** **Manual reading by the EXECUTOR on 2026-09-29.** The
   EXECUTOR is Claude Code (model `claude-opus-5-5`) --- itself a language
   model, reading in this session. There was **no separate LLM API call, no
   extraction pipeline, no embedding, no model service.** Every file was read
   completely.
3. **Scope.** `in_scope_hazard` when the paper itself discusses a climate or
   weather hazard or its impacts, judged from its own text; `off_topic` when it
   does not; `ambiguous` when hazard language is present but the paper does not
   examine a hazard or its impacts. One-sentence reason plus a quoted span.
4. **Claims only for `in_scope_hazard` items**, 0--5 each; a claim text is a
   faithful restatement of at most 40 words. `off_topic` → terminal `off_topic`;
   `ambiguous` → terminal `ambiguous_only`; in scope with no claim →
   `no_eligible_claim`. The builder refuses any other combination.
5. **Dimensions** --- concept, relation or direction, geography, temporal
   frame, scenario, and (from D-017) experimental condition --- each tagged `explicit` (the paper says it, in the claim
   span or a quoted `support` span), `inferred` (the extractor linked it; a
   support span is mandatory) or `unknown` (value exactly `unknown`). Nothing is
   filled from general knowledge, filenames, the query or the prototypes.
   **`scenario` means a climate or emissions scenario only**; laboratory
   treatment levels go in `experimental_condition` (D-017).
6. **Claim types:** `finding`, `projection`, `mechanism`, `recommendation`,
   `background_citation`. Hedging (`suggest`, `likely`, `might`) is kept in the
   relation value, not removed.
7. **Evidence.** Item id, file SHA-256, corpus-manifest SHA-256, JSON path,
   `char_start`/`char_end` --- **zero-based, half-open `[start, end)` Unicode
   code-point offsets into the JSON string value after decoding and before any
   normalization** --- the verbatim evidence text, and its SHA-256. Offsets are
   computed by exact search, never typed. Where a field repeats a passage, the
   first occurrence is used and the record says so.
8. **Bibliographic fields** only when a field with that content exists:
   `as_stored` from `$.title`; `recovered_from_other_field` with a span where
   another field holds a citation (`LIT-001141`); otherwise `unknown`. Stray
   page headers inside body text are noted, not recorded as bibliography. A
   title field holding a non-title is recorded as stored and noted.
9. **Rejected or ambiguous passages** are kept with span and reason.
10. **Claim validation status** (D-017). Every claim carries
    `claim_validation_status` from `single_reader_provisional`,
    `independently_confirmed`, `adjudicated_modified`, `rejected_on_review`.
    WP1 writes only `single_reader_provisional`; only an independent-review
    package may set another value.

## 9. Results with compact tables or examples

**Sample:** `LIT-000001`, `000191`, `000381`, `000571`, `000761`, `000951`,
`001141`, `001331`, `001521`, `001711`. No duplicate skip.

**Schema:** 10 of 10 decoded as JSON objects; all **flat**; all 86 top-level
values are strings. Keys are lower-cased section headings; **all ten key
sequences differ, so there is no majority structure and all ten deviate.** Union:
45 distinct keys --- `abstract` in 10, `title` 9, `introduction` 8,
`conclusion` 6, `discussion` 5, `results` 4, `methods` 3, three more keys in
two files each, and 35 keys in one file each.

| Item | Scope | Terminal status | Claims | Inferred-dim claims | Rejected / ambiguous |
| --- | --- | --- | ---: | ---: | ---: |
| `LIT-000001` | off_topic | off_topic | 0 | 0 | 2 |
| `LIT-000191` | in_scope_hazard | claims_extracted | 4 | 3 | 3 |
| `LIT-000381` | in_scope_hazard | claims_extracted | 4 | 0 | 2 |
| `LIT-000571` | in_scope_hazard (borderline) | claims_extracted | 5 | 0 | 2 |
| `LIT-000761` | ambiguous | ambiguous_only | 0 | 0 | 3 |
| `LIT-000951` | off_topic | off_topic | 0 | 0 | 1 |
| `LIT-001141` | in_scope_hazard | claims_extracted | 5 | 0 | 3 |
| `LIT-001331` | off_topic | off_topic | 0 | 0 | 1 |
| `LIT-001521` | in_scope_hazard | claims_extracted | 4 | 0 | 2 |
| `LIT-001711` | in_scope_hazard | claims_extracted | 5 | 0 | 3 |
| **Total** | | | **27** | **3** | **22** |

By type: 20 findings, 3 mechanisms, 2 projections, 2 background citations. Every
claim, with its span, is in `docs/LITERATURE_WP1_PILOT.md`. **After the D-017 split, `scenario` is `unknown` in
27 of 27 claims**; the two treatment-level values of `LIT-000191` (C1, C2) are
`explicit` under `experimental_condition`, unchanged. (At `7ded08e` they sat
under `scenario`, which read 25 of 27 `unknown`.) All 27 claims are
`single_reader_provisional`. The three `inferred` dimensions are all the
geography of `LIT-000191`'s laboratory findings, linked to "Northwest Atlantic"
through the title.

**Span integrity:** 96 spans (claim evidence, dimension supports, scope
evidence, rejected passages, recovered bibliography), every one re-sliced from
the verified decoded source and matched exactly; hashes match.

## 10. Validation performed

| Check | Result |
| --- | --- |
| `pytest` (`climrr` env) | **563 passed** (539 before; 24 new) |
| `scripts/verify_no_secrets_or_paths.py` | **0 hits** |
| Sample re-derivation from manifest and rule | same ten ids, twice, and in the test |
| Sample committed before first file opened | `6f9006c` at 05:17:40Z; first open 05:18:25Z |
| Span integrity | 96/96, in the build and again in `test_every_span_re_slices_from_the_verified_source` |
| Clean-head reproduction | all WP1 outputs byte-identical at `d728df6` |
| Firewall | test: no WP1 script or module references prototypes, pilot families or the query |
| **D-017 closure** | `pytest` **565 passed** (2 new: validation status; scenario/experimental split); scanner **0 hits**; rebuild at closure: **96/96 spans, every locator and evidence hash identical to `7ded08e`**; `test_every_span_re_slices_from_the_verified_source` ran against the corpus, not skipped |

## 11. Failures, rejected cases, and known limitations

**What was hard.**

- **Irregular schema.** Keys are section headings, not a schema: ten files,
  ten key sequences. `title` is missing once, and twice holds a non-title (a
  journal name; a repeated page header). One `abstract` is a citation string.
  Nothing downstream can assume a key exists; the records cite paths as found.
- **Offset pitfalls.** "Ishkāshim" is stored as `a` + U+0304 (two code
  points); a precomposed `ā` in the quote failed to match, and the build
  stopped. That is the check working. Code-point offsets differ from UTF-16
  (the `🌊` test) and from bytes. Offsets were never typed; exact search on the
  unnormalized string computes them.
- **Repeated passages.** Three files repeat whole passages inside a field, so a
  quote can match twice. The first occurrence is used and recorded.
- **The papers disagree with themselves.** `LIT-001141` gives 0.34/0.14 °C per
  year in its conclusion and 0.247/0.056 in its results (both kept, both noted);
  `LIT-001521` states the up/down split of its 2,862 genes both ways (kept as
  ambiguous, only the total used); `LIT-001711`'s "dry 32 % of all years" is
  hard to reconcile with "68 % of years ended with no surface water" (kept as
  ambiguous).
- **Scope is a judgement.** `LIT-000571` (irrigation ethnography that discusses
  water scarcity and mass-movement hazards) was ruled in scope; `LIT-000761`
  (fluxes in a permanently arid forest) ambiguous. A different reader could
  swap them.
- **"Scenario" was overloaded.** For `LIT-000191` the scenario dimension held
  experimental treatment levels the paper calls representative of past, present
  and future conditions --- not an emissions scenario. **Resolved by D-017**:
  they now sit under `experimental_condition`. No claim in the pilot states an
  emissions scenario.

**Known limitations.**

- **One reader, and the reader is a model.** The reading is the EXECUTOR's,
  once. There is no second reader and no agreement measure.
- **The reader built the prototypes.** The code firewall guarantees no
  prototype, family or query was *consulted*; it cannot remove the EXECUTOR's
  prior exposure to them. Disclosed rather than claimed away.
- **Verbatim excerpts now sit in the repository.** Evidence text is required
  verbatim, so 96 short quotations from ten papers are tracked. WP0 kept every
  byte of the corpus out; this is the first package that brings excerpts in.
- **Ten items estimate nothing** about the corpus.

## 12. Deviations from the approved plan

1. **Scope rule for claims.** The work package lists `off_topic` and
   `ambiguous_only` as terminal outcomes but does not say whether an off-topic
   paper may still yield claims. Claims were extracted **only** for
   `in_scope_hazard` items; the other passages went to `rejected_or_ambiguous`.
2. **"Majority structure"** was defined as a key sequence shared by more than
   half of the files; none is, so all ten deviate.
3. **`explicit` via a support span.** A dimension the paper states elsewhere
   than in the claim span --- the study site, the study period --- is tagged
   `explicit` with the quoted support span, not `inferred`.
4. **The reading is stored as a tracked Python data file**
   (`scripts/wp1_extractions.py`), built into the JSON records by script, so
   that no offset is ever typed.
5. **24 tests**, not a fixed list: the package named four kinds; the suite adds
   code-point, combining-character, no-normalization and firewall tests.

## 13. Open decisions and mentor questions

Decided by GUIDANCE in D-017:

| Item | Ruling |
| --- | --- |
| Scope calls `LIT-000571` (in, borderline) and `LIT-000761` (ambiguous) | **accepted** |
| "Claims only for in-scope items"; "ambiguous yields no claim" | **accepted** |
| Tracked verbatim excerpts | **kept**, under minimal-evidence-window discipline; hash + offsets authoritative |
| Experimental treatment vs. scenario | **split**; done at closure; `scenario` `unknown` 27/27 |
| Second, independent reader | **required before any claim is accepted M5 evidence**; not before M5 machinery |

Still open:

| Item | Owner | Why it matters |
| --- | --- | --- |
| **Second-reader pass, planned as M4-WP1b**: blind, all ten papers, no prototypes, no first-pass labels or claims during extraction; then adjudication of scope, inclusion, type and every dimension | COORDINATOR to scope; Kaiyuan | until it closes, all 27 claims stay `single_reader_provisional` and M5-WP1 can pass only as machinery validation |
| Q19–Q21 (collection platform, dates, completeness) | JL | unchanged |

## 14. Proposed gate status

The ruling's 20 acceptance criteria, one line each:

| # | Criterion (abridged) | Status | Evidence |
| ---: | --- | --- | --- |
| 1 | 10 IDs frozen before content inspection | **MET** | `6f9006c` 05:17:40Z; first open 05:18:25Z |
| 2 | Selection reproducible from the frozen manifest and rule alone | **MET** | `test_the_frozen_sample_is_re_derived…` |
| 3 | No title, filename, topic, prototype or content influences selection | **MET** | the rule reads ids and duplicate groups only |
| 4 | Exact-byte duplicates cannot appear twice | **MET** | rule + tests; none on the grid |
| 5 | All 10 items get a terminal status | **MET** | 6 claims_extracted, 3 off_topic, 1 ambiguous_only |
| 6 | JSON schema documented, not assumed | **MET** | `wp1_schema_observed.json`; no majority structure |
| 7 | Every claim traceable to id, file SHA, JSON path, `[start,end)` | **MET** | all 27 claims |
| 8 | Offsets defined against the unnormalized decoded string | **MET** | `OFFSET_CONVENTION` in every block |
| 9 | Span integrity mechanically checked | **MET** | 96/96, build and test |
| 10 | Zero claims is a valid result | **MET** | 4 items with 0 claims |
| 11 | Off-topic papers remain, not replaced | **MET** | 3 off_topic kept |
| 12 | Bibliographic metadata only when present | **MET** | `as_stored`, `recovered_from_other_field`, `unknown` |
| 13 | Unstated dimensions are `unknown` | **MET** | e.g. scenario `unknown` in 27 of 27 claims after the D-017 split |
| 14 | Explicit distinguished from inferred | **MET** | 3 inferred, each with a support span |
| 15 | No claim labelled supporting or contradicting a prototype | **MET** | test |
| 16 | No prototype guides reading or passage selection | **MET, with a disclosed limitation** | code firewall tested; the reader's prior exposure cannot be removed (field 11) |
| 17 | Rejected and ambiguous passages preserved | **MET** | 22 kept |
| 18 | No embeddings, semantic retrieval or corpus-wide search | **MET** | ten files opened, nothing else |
| 19 | Described as an ingestion / claim-extraction pilot, not an estimate | **MET** | stated once in the pilot document, tested |
| 20 | All outputs tied to the WP0 manifest identity | **MET** | `3281aa72…` in sample and every record |

**Proposed status (at `7ded08e`):** ready for GUIDANCE review; 20 criteria met,
criterion 16 with a disclosed limitation.

**GUIDANCE status: PASS WITH ACTIONS** (D-017), on the reviewed head
`7ded08e`. The 27 claims are accepted as **single-reader provisional**
structured claims for compatibility-machinery validation, not as independently
validated literature evidence. The closure actions (schema split, claim
validation status, D-017, bookkeeping) are done in the commit after `7ded08e`;
the second-reader pass is planned as M4-WP1b (field 13).

## 15. Proposed next bounded objective

**M5-WP1 --- compatibility check between the WP1 claims and the three
prototypes, on this fixed set, to be designed by COORDINATOR after GUIDANCE
review.** *(Proposed at `7ded08e`.)* **Authorized by D-017** as deterministic
negative-case compatibility machinery validation, 27 × 3 = 81 pairs, under the
ruling's 22 acceptance criteria.
