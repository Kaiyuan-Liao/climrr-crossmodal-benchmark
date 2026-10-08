# M4-WP1b --- blind second reading: comparison and adjudication (Track A)

**Track A of the D-018 follow-on ruling.** A blind second reader read the ten
M4-WP1 papers and froze its result (`87bce48`) before anything was compared.
This package compares that reading with the first pass, preserves every
disagreement, and adjudicates by rule. **The adjudicator is the WP1 EXECUTOR
--- reader 1 itself, prototype-exposed.** Authorized by
[`docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md`](../../docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md)
(Track A; actions 11--12; criteria 13--15). No QA is generated.

## 1. Milestone ID and title

**M4-WP1b --- blind independent claim validation: comparison of two readings
and adjudication.** M4 (literature). **M1 remains open** (D-014). M4-WP2's
retrieval half is frozen and unread; its reading waits on this package.

## 2. Objective

Compare the first-pass reading (`wp1_claims`, 27 claims) with the blind reading
(`wp1b_blind`, 21 claims) item by item --- scope, then claims aligned by
evidence span, then dimension by dimension --- report descriptive agreement,
and produce an adjudicated claim set by the work package's rules, so that
GUIDANCE can decide whether the premise for relevance-guided sampling stands.

**Excluded, and not done:** editing either reading; re-reading any paper to
break a tie; reading any M4-WP2 candidate; applying eligibility or relations
to any claim; QA.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/m4-wp1b-adj`, from `work/m4-wp2-retrieval` at **`7ddee2c`** (contains the blind records at `87bce48` and the first-pass claims) |
| Phases A--D (code, tests, comparison, adjudicated set, document, first two run records) | **`0706679`** |
| Clean-head verification run | `reports/runs/20261008T222421Z_local_wp1b_adjudicate.*` at `0706679`, `git_dirty: false`; every artifact `verified` |
| This report, `PROJECT_STATE.md`, the verification run record | the commit after `0706679`; its SHA travels with the hand-back |
| Remote | **not pushed, not merged** |

## 4. Data version and checksums

**Inputs (pinned in `climrr.wp1b.FROZEN_INPUT_SHA256`, tested):**

| Object | SHA-256 |
| --- | --- |
| `artifacts/literature/wp1_claims/` (10 records) + `wp1_claims_summary.json` | per file in the test; summary `fb913fe4…cdde` |
| `artifacts/literature/wp1b_blind/` (10 records) + `wp1b_blind_summary.json` | per file in the test; summary `e732867f…7ff63`; **each equal to its blob at `87bce48`** (test) |
| `artifacts/literature/wp1_sample.json` | `5cb81f9585040dd1d73a89ca7062d3c5e0060112f54e08ef4795db96a657b578` |
| Ten corpus files | each verified against its `wp1_sample.json` SHA-256 before decoding (fail closed) |

**Outputs:**

| Object | SHA-256 |
| --- | --- |
| `artifacts/literature/wp1b_comparison.json` | `436657cf5dfafd7a074d08d2e78272c1ef75a524a3767918221f4aaacaf0f5ab` |
| `artifacts/literature/wp1_claims_adjudicated/adjudication_summary.json` | `f7c2f55bc8049dd8624ec67d7d41bb573c46bd252acf4d4c54295b10e970c1fa` |
| `artifacts/literature/wp1_claims_adjudicated/LIT-*.json` (10) | listed in the run record |
| `docs/LITERATURE_WP1B_ADJUDICATION.md` | `177fc0e47fdc382269d2744e32cd04ae174ece6f989a7b482b8522f64d75bf23` |

`FullData.csv` was not read.

## 5. Environment and execution location

conda environment `climrr`, Python 3.11.16, location `local`; D-007 pins
matched (`test_repo_requirements_pins_are_all_satisfied` passes). The ten
corpus files were read from `literature_corpus_root` in the untracked config.
Sophia not used.

## 6. Work completed

**Inputs.** Both readings pinned by hash; a test fails on any changed byte, on
an unpinned file in either directory, and if a blind record differs from its
blob at `87bce48`. Every span of both readings --- 96 reader-1, 85 reader-2
--- re-sliced from the hash-verified decoded source: **0 failures** (the stop
condition did not fire).

**Phase A.** Ten-row scope table with both readers' scopes and reasons quoted.

**Phase B.** Claims aligned by evidence span: same normalised `json_path`
(reader 2's raw keys mapped to `$`-paths) and overlapping `[start, end)`,
one-to-one or the run fails. For each aligned pair, all seven dimensions
compared: tag and value mechanically; where values differ textually, a recorded
content judgement (`climrr/wp1b_judgements.py`). Unaligned claims checked
against the other reader's rejected passages.

**Phase C.** Descriptive statistics.

**Phase D.** Rules 1--5 applied in order by `climrr.wp1b`; it refuses a
judgement that contradicts a rule. Adjudicated records written to a new
directory; originals untouched.

**Phase E.** This report; `PROJECT_STATE.md`;
`docs/LITERATURE_WP1B_ADJUDICATION.md` added to `KNOWLEDGE_FILES`.

## 7. Deliverables and exact file paths

**New:** `src/climrr/wp1b.py`, `src/climrr/wp1b_judgements.py`,
`scripts/wp1b_adjudicate.py`, `tests/test_wp1b.py`,
`artifacts/literature/wp1b_comparison.json`,
`artifacts/literature/wp1_claims_adjudicated/` (10 records +
`adjudication_summary.json`), `docs/LITERATURE_WP1B_ADJUDICATION.md`
(generated), this report, run records
`reports/runs/20261008T222205Z_*`, `20261008T222227Z_*` (writing runs) and
`20261008T222421Z_*` (clean-head verification).

**Changed:** `scripts/stage_knowledge.py` (one entry), `docs/PROJECT_STATE.md`.

## 8. Methods and rules that affect scientific meaning

1. **Alignment** by evidence-span overlap only; no text similarity.
2. **Rule 1 (scope):** agree → adopt; `in_scope_hazard` vs `ambiguous` →
   `in_scope_hazard (contested)`, every claim `adjudicated_modified` with
   "scope contested by blind reader"; `off_topic` vs anything else →
   `ambiguous`, zero promoted claims.
3. **Rule 2:** aligned, same tag and judged same content on every dimension →
   `independently_confirmed`; reader-1 text kept; both spans cited.
4. **Rule 3** (operationalised here --- see field 12): unknown beats a value
   (3a); explicit vs inferred → explicit only where the explicit reader's cited
   span actually states the adopted value (3b); same tag, different content →
   the part both readers support **and the cited span states**, never the union
   (3c). `claim_type` has no conservative order, so a difference there is an
   `unresolved_tie`.
5. **Rule 4:** reader-1-only → `single_reader_provisional`,
   `not_independently_found`; reader-2-only → added as
   `single_reader_provisional`, `blind_reader_only` (`LIT-…-B<n>`).
6. **Rule 5:** no claim deleted; every first-pass claim keeps its id and every
   original field (tested); `first_pass_claim_validation_status` is kept beside
   the new status; `adopted_dimensions` sit beside the unchanged claim text.
7. **One post-rule override, J-1** (field 11): the wildfire-smoke exposure
   regimen.

## 9. Results with compact tables or examples

**Scope --- agreement 6/10.** The expected pattern is **confirmed, with one
addition**: the readers agree on the five papers both put in scope, and also
on `LIT-000761` (both `ambiguous`). Every disagreement is reader 1
`in_scope`/`off_topic` against reader 2 `ambiguous`.

| Item | Reader 1 | Reader 2 | Adopted |
| --- | --- | --- | --- |
| `LIT-000001` | off_topic | ambiguous | ambiguous (R1c) |
| `LIT-000191` | in_scope_hazard | in_scope_hazard | in_scope_hazard |
| `LIT-000381` | in_scope_hazard | in_scope_hazard | in_scope_hazard |
| `LIT-000571` | in_scope_hazard | **ambiguous** | **in_scope_hazard (contested)** (R1b) |
| `LIT-000761` | ambiguous | ambiguous | ambiguous |
| `LIT-000951` | off_topic | ambiguous | ambiguous (R1c) |
| `LIT-001141` | in_scope_hazard | in_scope_hazard | in_scope_hazard |
| `LIT-001331` | off_topic | ambiguous | ambiguous (R1c) |
| `LIT-001521` | in_scope_hazard | in_scope_hazard | in_scope_hazard |
| `LIT-001711` | in_scope_hazard | in_scope_hazard | in_scope_hazard |

**Alignment:** **19 aligned pairs; 8 reader-1-only; 2 reader-2-only.**
Reader-1-only: the five `LIT-000571` claims (reader 2 extracted none and had
**rejected** the passages under two of them), `LIT-001141-C4`, `-C5`,
`LIT-001711-C5`. Reader-2-only: `LIT-001141` health/economy background (cited)
and `LIT-001711` "dry for 32% of all years" --- **a passage reader 1 had
considered and rejected** as hard to reconcile with the results.

**Agreement (descriptive; n is small, nothing inferential):**

| Measure | Value |
| --- | --- |
| Reader-1 claims aligned | 19 / 27 (19 / 22 on the five shared in-scope items) |
| Reader-2 claims aligned | 19 / 21 |
| Per-item claim-count agreement | 8 / 10 (equal counts ≠ same claims) |
| Exact agreement per dimension over 19 pairs | concept 16, relation 16, **geography 5**, temporal 12, scenario **19**, experimental_condition 13, claim_type 18 |

Geography disagrees most, almost entirely on the **tag**: reader 1 calls a
place explicit when a support span names it; reader 2 calls the same link
inferred.

**Statuses:**

| Status | All 29 | First-pass 27 |
| --- | ---: | ---: |
| `independently_confirmed` | **1** | 1 |
| `adjudicated_modified` | **23** | 23 |
| `single_reader_provisional` | **5** | 3 |
| `rejected_on_review` | **0** | 0 |

The one confirmed claim is `LIT-001141-C1` (Bangalore April UHI-event LST
+0.34 vs +0.14 °C/yr). Of the 23 modified, 5 are `LIT-000571` (contested
scope); the other 18 differ on at least one dimension --- most often only a
geography or temporal tag, or a value trimmed to what its span states.
**One unresolved tie:** `LIT-000381-C3`, `claim_type` (mechanism vs finding).

## 10. Validation performed

| Check | Result |
| --- | --- |
| `pytest` (`climrr` env) | **733 passed** (703 before; 30 new in `tests/test_wp1b.py`) |
| `scripts/verify_no_secrets_or_paths.py` | **0 hits**, run after staging, exit status read |
| Input pins | all 23 files equal their pins; blind records equal their `87bce48` blobs; tamper test fails as intended |
| Span integrity | 96 + 85 spans re-slice from verified sources (runs, and a test that **ran, not skipped**) |
| Rules | synthetic tests: identical → confirmed; unjudged textual difference refused; unknown beats a value; explicit-vs-inferred needs the span check and a matching tag; kept-explicit must cite the explicit reader; tie; override needs id and reason and keeps the rule result; many-to-one alignment refused |
| Reproduction | every recorded alignment and decision re-derives from the frozen readings and judgements (no corpus needed); clean-head rerun `verified` every artifact byte for byte |
| Preservation | every first-pass claim keeps its id and every original field; nothing else in any record changed |

## 11. Failures, rejected cases, and known limitations

- **The adjudicator is not independent.** It is the WP1 EXECUTOR: it read and
  built the prototypes and wrote reader 1. Every judgement is recorded with its
  reason, and the rules constrain it, but on the **contested items** ---
  `LIT-000571`'s scope, the `LIT-000381-C3` tie, override J-1, and the three
  `off_topic`→`ambiguous` scope changes --- **GUIDANCE may require a third
  party.**
- **The blind reader's disclosures, verbatim:** "Only the
  literature_corpus_root key of config/local_paths.yaml and the ten listed
  corpus files were opened by the reader." "The agent harness placed the
  repository CLAUDE.md and a git-status snapshot (branch, recent commit
  subjects) into context before the task began; no other repository file was
  opened." "pytest and scripts/verify_no_secrets_or_paths.py were executed
  (required before commit by repository rules) with only their summary lines
  inspected." "No run record was written: the records were produced by a
  scratch script outside the repository, and reading climrr.runrecord to call
  it would have broken the blind protocol." "Scenario dimension is 'unknown'
  for every claim…". **What that exposure contained:** `CLAUDE.md` names the
  `wildfire*` = Fire Weather Index caution and `*_hist` columns; the commit
  subjects named "27 claims and 3 prototypes (81 pairs)". No claim text,
  scope label or prototype value was in it. It could only have biased the
  reader **toward** pilot concepts, and the blind reading contains none.
- **Override J-1.** Both readers recorded the 16-week smoke-exposure regimen
  from the same sentence, reader 1 under `temporal_frame`, reader 2 under
  `experimental_condition`. Rule 3a applied literally makes both `unknown` and
  loses a fact both found. The adjudicator kept it in `experimental_condition`
  (D-017's placement for treatments); the literal rule result is recorded
  beside it.
- **"Same content" is a judgement.** In several pairs the readers put the
  driver in different dimensions (concept vs relation; exposure vs response).
  These were judged the same proposition; each such judgement is in the
  disagreement table with its note.
- **All five `LIT-000571` claims rest on one reader**, and the blind reader
  explicitly rejected the passages under two of them (C2, C4); the rule still yields
  `adjudicated_modified`, not `rejected_on_review`, because the scope is
  contested rather than off-topic.
- **First-pass inconsistencies remain inside the paper, not the readings:**
  both readers independently flagged the `LIT-001141` rate discrepancy (0.34/0.14
  vs 0.247/0.056 °C/yr) and the `LIT-001521` up/down split.
- **n is tiny.** Ten items, 19 pairs: the statistics describe these two
  readings and nothing more.

## 12. Deviations from the approved plan

1. **Rule 3's "more conservative value" was operationalised as span-limited
   trimming.** Where the explicit reader's span states *part* of its value
   (e.g. "an old-growth subtropical forest in southern China" for a value that
   adds "Dinghushan, Guangdong"), the adjudicator kept **explicit** for the
   part the span states rather than switching the whole value to the other
   reader's **inferred** one. Both readers' full values are kept. The work
   package's wording admits either reading; this one asserts less.
2. **`claim_type` differences are ties**, since the rules give no
   conservative order between types.
3. **Override J-1** (field 11) --- the one place judgement replaced a rule
   result.
4. **Blind-only claims take ids `LIT-…-B<n>`**, `n` the blind claim number,
   so each traces to its source.
5. **Two writing run records exist** (the document was re-rendered once to fix
   a sentence before commit; the JSON artifacts were `verified`, not
   rewritten), plus the clean-head verification run.

## 13. Open decisions and mentor questions

**Field 13 --- does the second reading materially invalidate the premise for
relevance-guided sampling? No.** Evidence: a boundary-aware lexical screen of
every recorded text of all 48 claims (both readers) for the frozen pilot
concept terms (`fire weather index`, `FWI`, `heat index`), the WP2 place terms
(`Oklahoma`, `Stephens`, `California`) plus `United States`, `USA`, `U.S.`,
and any non-`unknown` scenario flags **0 claims in either reading**; the two
reader-2-only claims (Bangalore health/economy background; Fortescue Marsh dry
years) carry **no US geography, no emissions scenario and no pilot concept**,
and `scenario` is `unknown` in **48 of 48** claims. The disagreements the
blind reader introduced are about scope breadth (`ambiguous` where reader 1
said `off_topic`) and dimension tags --- not about whether a random sample
yields pilot-relevant claims, which neither reader found.

| Item | Owner | Why it matters |
| --- | --- | --- |
| Third-party adjudication for contested items (`LIT-000571` scope; `LIT-000381-C3` tie; J-1; three R1c scope changes) | GUIDANCE | the adjudicator is reader 1 |
| Accept rule 3's span-limited operationalisation (field 12.1) | GUIDANCE | decides whether the trimmed geography and temporal values (rules 3b/3c in the disagreement table) stand |
| Whether `adjudicated_modified` claims are usable M5 evidence or only `independently_confirmed` ones (1 claim) | GUIDANCE | the next positive-case M5 package depends on it |
| Pool of 4 < 12 (from M4-WP2 retrieval) | GUIDANCE | WP2 reading is next |

## 14. Proposed gate status

| # | Criterion (D-018) | Status | Evidence |
| ---: | --- | --- | --- |
| 13 | WP1b is blind to prototypes, first-pass claims, and M5 results during initial extraction | **MET, with disclosed incidental exposure** | blind records at `87bce48`; disclosures quoted in field 11 (CLAUDE.md, commit subjects); no claim text, scope label or prototype value exposed |
| 14 | WP1b freezes its independent result before comparison/adjudication | **MET** | `87bce48` precedes this branch; records byte-equal to their `87bce48` blobs (test) |
| 15 | Disagreements are preserved, not overwritten | **MET** | comparison artifact and every adjudicated record keep both readers' values; first-pass fields unchanged (test) |
| Action 11 | Execute M4-WP1b blind | **MET** | as 13--14 |
| Action 12 | Preserve both independent readings plus adjudication | **MET** | originals pinned and untouched; adjudication in a new directory |

**Proposed status:** ready for GUIDANCE review --- M4-WP1b complete, with the
adjudicator's non-independence and the contested items put to GUIDANCE, and
the field-13 finding that the premise for relevance-guided sampling stands.

**GUIDANCE outcome (D-019, `docs/M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md`):
PASS WITH ACTIONS**, reviewed at `25a86e5`, merged at `e7da7cc`. Rule 3
span-limited trimming approved; J-1 approved as a one-off; `LIT-000381-C3`
stays `unresolved_tie`; `LIT-000571` stays scope-contested; evidence tiers A/B/C
introduced (added to the adjudicated records on `work/m4-wp2-read`: A 1, B 18,
C 10); a third reader only if an accepted bridge depends on contested material.

## 15. Proposed next bounded objective

M4-WP2 reading of the 4 frozen candidates, pending GUIDANCE ruling on pool size.
