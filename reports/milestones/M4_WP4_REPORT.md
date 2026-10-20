# M4-WP4 --- 20-paper concept/place candidate reading pilot

**Status: reading, blind reading, comparison, adjudication and compatibility
complete (M4-WP4r1 + r2 + r3). Ready for GUIDANCE review.** Branch
`work/m4-wp4-adj` (from `work/m4-wp4-read` at `72617da`, blind branch `c452d7d`
merged at `d90595c`); not pushed, not merged. Compatibility is reported
separately in [`M5_WP4_REPORT.md`](M5_WP4_REPORT.md).

---

## 1. Milestone ID and title

M4-WP4 --- the frozen 20-paper LITCORPUS-02 candidate sample read by reader 1
(M4-WP4r1, with concept-hit and place-hit precision classified after reading), read
blind by a second reader (M4-WP4r2), then compared and adjudicated (M4-WP4r3
Phase A). Fields 1--9 describe r1; fields 10--15 cover the whole package.
Authorized by
[`docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md`](../../docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md)
(D-025, Track A; required actions 8--15, acceptance criteria 8--22).

## 2. Objective

Read the 20 frozen candidates (10 fire weather, 10 extreme heat) with the unchanged
WP1/WP2 rubric; record scope, terminal status and up to five claims per item with
exact evidence spans; then, only after the reading is frozen, classify every matched
concept term and place term as the ruling's precision categories.

r3 Phase A: compare the two frozen readings by the D-019 / WP1b rules, unchanged,
and adjudicate, with evidence tiers; carry the hit-precision tables alongside.
Compatibility (r3 Phase B) is reported in `M5_WP4_REPORT.md`.

**Excluded:** any use of a retrieval hit as a bridge; re-reading a paper to break a
tie; QA; Stage 2a--2c. The sample is a
**deterministic rank sample of lexical place candidates from LITCORPUS-02; not
representative of the corpus or the literature.**

## 3. Repository commit SHA

- Base: `main` at `38116a0` (merge of M4-WP3).
- **`e0857aa`** --- Phases A--B: sample verified, reader-1 records. Committed
  **before any `hits.csv` or place-hit location was opened.**
- **`72617da`** --- Phase C--D (hit classification, claim screens, reading document).
- **`c452d7d`** --- the blind reading (M4-WP4r2), on its own branch from `38116a0`;
  merged into `work/m4-wp4-adj` at **`d90595c`** (`--no-ff`).
- **`90d55fc`** --- the secrets/paths-scan fix (field 12, deviation 7).
- **`6c856e2`** --- M4-WP4r3 Phase A: comparison and adjudication.
- `220ca84` / `8436c25` --- M5-WP4 freeze and matrix (see `M5_WP4_REPORT.md`).
- The Phase C commit (this report's fields 10--15, M5-WP4 report, state, brief):
  the head of `work/m4-wp4-adj` handed back with this package.
- Remote: nothing pushed, nothing merged (package instruction).

## 4. Data version and checksums

| File | SHA-256 | Note |
| --- | --- | --- |
| `artifacts/literature/wp4_sample.json` | `f3cb5d0c…dcea15` | equals `wp4_sample_sha256` in `data/manifest.json`; `selected_sha256` `dff4e412…0cff` re-verified |
| 20 sampled source files `<litcorpus02_root>/<rel_path>` | as listed in the sample | all 20 matched before any decode (run record `20261020T000420Z_local_wp4_verify_sample`) |
| `artifacts/literature/litcorpus02/evidence/runs/fire_weather_v1/hits.csv` | `9fd398dc…a834` | read in Phase C only |
| `artifacts/literature/litcorpus02/evidence/runs/extreme_heat_v1/hits.csv` | `feb4342c…5ecc` | read in Phase C only |
| `artifacts/literature/litcorpus02/place_candidates/candidate_hits.csv` | `c33aa60c…53c1` | read in Phase C only |
| `data/metadata/concept_map.yaml` | `27f7a44d…d7b4` | read by the claim screen only; unchanged |
| `artifacts/literature/wp4_claims_summary.json` | `e062f050…9b02` | output |
| `artifacts/literature/wp4_hit_classification.json` | `001d76c9…c30cc0` | output |
| `artifacts/literature/wp4_claim_screens.json` | `125a566d…b321` | output; `4fec0b51…aa92` at `72617da`, one docstring line reworded at `90d55fc` (field 12) |
| 20 + 1 blind records `artifacts/literature/wp4_blind/` | pinned in `climrr.wp4adj.FROZEN_INPUT_SHA256` | equal their `c452d7d` blobs (test) |
| `artifacts/literature/wp4_comparison.json`, `wp4_claims_adjudicated/` | run record `reports/runs/20261020T220725Z_local_wp4_adjudicate.json` | outputs; a second run (`…T220931Z`) verified byte equality |

Source files are external (gitignored corpus, D-015/D-023), opened read-only, never
copied into the repository. `data/raw/FullData.csv` was not read.

## 5. Environment and execution location

Local macOS (`macOS-15.3-arm64`), conda env `climrr`, Python 3.11.16, every D-007 pin
matched; `pip freeze` SHA-256 `d9af804d…52bf51`; location label `local`. All run
records under `reports/runs/20261020T00*` were produced in this env. (Two earlier
run records produced by mistake with the base interpreter, which does not match the
pins, were deleted before any commit and the scripts re-run --- see field 12.)

## 6. Work completed

**Phase A --- verify before opening.** `scripts/wp4_verify_sample.py` checked the
sample against the manifest, re-derived `selected_sha256`, read only the
`litcorpus02_root` key, and hashed all 20 files (20/20 match) without decoding any.
`LIT2-001075` (`272852900`) = LITCORPUS-00 `LIT-001536`, read in M4-WP2: its record
carries `prior_exposure: "LIT-001536 read in M4-WP2; WP2 artifacts not consulted"`.
No file under `artifacts/literature/wp2_*`, `docs/LITERATURE_WP2_*`,
`docs/M5_WP2_*` or `artifacts/bridges/` was opened.

**Phase B --- reading.** Reader 1 (the EXECUTOR) read every file completely, key by
key; for files whose stored text repeats whole passages two or three times, reading
used a de-duplicated view (each distinct sentence once), and every quotation was then
matched against the raw decoded string. The reading is data in
`scripts/wp4_extractions.py`; `scripts/build_wp4_claims.py` locates each quote by
exact search, computes code-point offsets, re-slices and fails on any difference
(300 spans, all exact). Records: `artifacts/literature/wp4_claims/<LIT2 id>.json`.

**Phase C --- hit precision, after reading.** `scripts/wp4_hit_classification.py`
took the group-0 (concept) rows of both arms' `hits.csv` and all place rows of
`candidate_hits.csv` for the 20 items (81 frozen first-hit rows), verified each is
reproduced exactly, found **all** occurrences with the collection matcher
(205), and applied reader 1's classes from `scripts/wp4_hit_judgements.py` (default
per item-term pair, per-occurrence overrides), recording whether each occurrence
falls inside a promoted claim's evidence or support span. Group-1 context terms were
not classified.

**Claim screens.** `scripts/wp4_claim_screens.py`: US place in `geography`; an
approved C-2 family term in `concept` (project boundary rule, `approved_family_term`
masks); named scenario. Descriptive only --- no prototype was read and no
compatibility was run.

**Phase D.** `scripts/render_wp4_reading.py` generated
[`docs/LITERATURE_WP4_READING.md`](../../docs/LITERATURE_WP4_READING.md) from the
records. Checks: `pytest` and the secrets/paths scan (field 10).

## 7. Deliverables and exact file paths

- `scripts/wp4_verify_sample.py`, `scripts/wp4_extractions.py`, `scripts/build_wp4_claims.py`
- `artifacts/literature/wp4_claims/LIT2-*.json` (20), `artifacts/literature/wp4_claims_summary.json`
- `scripts/wp4_hit_judgements.py`, `scripts/wp4_hit_classification.py`, `artifacts/literature/wp4_hit_classification.json`
- `scripts/wp4_claim_screens.py`, `artifacts/literature/wp4_claim_screens.json`
- `scripts/render_wp4_reading.py`, `docs/LITERATURE_WP4_READING.md`
- `tests/test_wp4_claims.py`
- `config/local_paths.example.yaml` (placeholder `litcorpus02_root: <LITCORPUS02_ROOT>`)
- Run records: `reports/runs/20261020T000420Z_local_wp4_verify_sample.*`,
  `…T000421Z_local_build_wp4_claims.*`, `…T000928Z_local_wp4_hit_classification.*`,
  `…T001021Z_local_wp4_claim_screens.*`, `…T001204Z_local_render_wp4_reading.*`
- This report; `docs/PROJECT_STATE.md` refreshed.
- **M4-WP4r3 Phase A:** `src/climrr/wp4adj.py`, `src/climrr/wp4_judgements.py`,
  `scripts/wp4_adjudicate.py`, `tests/test_wp4adj.py`;
  `artifacts/literature/wp4_comparison.json`, `artifacts/literature/wp4_claims_adjudicated/`
  (20 records + `adjudication_summary.json`),
  [`docs/LITERATURE_WP4_ADJUDICATION.md`](../../docs/LITERATURE_WP4_ADJUDICATION.md);
  run records `20261020T220725Z_*`, `20261020T220931Z_*` (`wp4_adjudicate`).

## 8. Methods and rules that affect scientific meaning

- **Rubric unchanged** from WP1/WP2: `explicit` / `inferred` (with quoted support) /
  `unknown`; nothing from general knowledge; `scenario` = emissions or climate
  scenario only, treatment and model-experiment settings under
  `experimental_condition` (D-017); ≤ 5 claims, ≤ 40 words; first occurrence when a
  passage repeats.
- **Added: `geography.role`** --- the role the place plays for that claim (study
  area, validation area, cited study's area, background context, ...), as the
  package asks. Free text; not a controlled vocabulary.
- **Background citations kept as claims** (`claim_type: background_citation`), as in
  WP1. 19 of the 83 claims are of that type; they restate cited work, not the
  paper's own evidence.
- **Hit classes:** concept --- `substantive_concept_use` / `incidental_mention` /
  `ambiguous_acronym_or_collision`; place --- `study_area_or_phenomenon_geography` /
  `contextual_geography` / `institution_or_affiliation` / `citation_surname_or_person` /
  `other_incidental`. A pair's **primary class** is the most substantive class among
  its occurrences (vocabulary order); an item's class is its most substantive pair.
  This rule is reader 1's convention, stated in the artifact.
- **Matcher** for all-occurrence search = the collection matcher (`\bterm\b`,
  case-insensitive, per section). It does not match "Stephenson" or "Stephan".
- No data column was read, renamed, filtered or interpreted.

## 9. Results with compact tables or examples

**Per item** (concept / place = item's most substantive hit class):

| LIT2 | Arm | Scope | Terminal | Claims | Concept hit | Place hit |
| --- | --- | --- | --- | ---: | --- | --- |
| 000185 | fire | in_scope_hazard | claims_extracted | 5 | incidental | study area |
| 000366 | fire | in_scope_hazard | claims_extracted | 3 | incidental | **institution** (UC Irvine) |
| 000499 | fire | in_scope_hazard | claims_extracted | 5 | incidental | contextual |
| 000560 | fire | in_scope_hazard | claims_extracted | 2 | incidental | contextual |
| 000673 | fire | in_scope_hazard | claims_extracted | 4 | incidental | **institution** (Palmdale flight base) |
| 000786 | fire | in_scope_hazard | claims_extracted | 5 | incidental | study area (+ `stephens` = surname) |
| 001063 | fire | in_scope_hazard | claims_extracted | 5 | incidental | study area |
| 001157 | fire | in_scope_hazard | claims_extracted | 5 | incidental | contextual |
| 001236 | fire | in_scope_hazard | claims_extracted | 3 | **substantive** | contextual |
| 001308 | fire | in_scope_hazard | claims_extracted | 4 | **substantive** | study area |
| 000084 | heat | in_scope_hazard | claims_extracted | 5 | **substantive** | study area (CA, OK) |
| 000203 | heat | in_scope_hazard | claims_extracted | 3 | incidental | contextual |
| 000315 | heat | in_scope_hazard | claims_extracted | 5 | incidental | contextual |
| 000470 | heat | in_scope_hazard | claims_extracted | 5 | **substantive** | contextual |
| 000662 | heat | in_scope_hazard | claims_extracted | 5 | incidental | contextual |
| 000803 | heat | **ambiguous** | ambiguous_only | 0 | **substantive** | contextual |
| 000927 | heat | in_scope_hazard | claims_extracted | 5 | incidental | contextual |
| 001075 | heat | in_scope_hazard | claims_extracted | 5 | incidental | study area (CA, OK) |
| 001160 | heat | in_scope_hazard | claims_extracted | 5 | **collision** (SHI) | study area |
| 001293 | heat | in_scope_hazard | claims_extracted | 4 | **substantive** | study area |

**Totals.** 83 claims; 19 items with ≥ 1 claim (1 `ambiguous_only`); 9 claims carry an
`inferred` dimension; 68 rejected/ambiguous passages kept. Claim types: 59 finding,
19 background_citation, 3 recommendation, 1 projection, 1 mechanism.

| | Fire weather | Extreme heat | All |
| --- | ---: | ---: | ---: |
| items whose concept hit is substantive | 2 | 4 | **6** |
| items whose concept hit is a collision | 0 | 1 | 1 |
| items whose place hit is study-area geography | 4 | 4 | **8** |
| items with both | 1 (001308) | 2 (000084, 001293) | 3 |

**Place terms** (item-term pairs by primary class): `california` 23 pairs --- 8 study
area, 10 contextual, 2 institution/affiliation, 0 citation; `oklahoma` 2 --- both
study area (000084 Southern Great Plains; 001075 state ranking); `stephens` 1 ---
citation surname ("Stephens and Moghaddas 2005", 000786). "California" is an
**affiliation/institution** in 2 items (University of California at Irvine as data
provider; Armstrong Flight Research Center in Palmdale) and inside a citation in 3
occurrences (a reference-list title stored twice in 000203; "State of California, 2021"
in 001075). "Stephenson, 2002"
(001293) and "Stephan, 2008" (001075) are not hits under the matcher.

**Concept terms.** 29 pairs: 8 substantive, 20 incidental, 1 collision. Every bare
`fwi` hit in this sample is the fire weather index (no non-fire FWI). The one
collision: all four `heat index` hits in 001160 are inside "standardized heat index
(SHI)" or "Excess heat index", different indices.

**Screens (83 claims).** US geography **42** (41 explicit, 1 inferred; 26 findings,
12 background citations). Approved pilot family term in the `concept` field **8**
(4 fire weather index, 4 heat index), of which **1 is the SHI collision**
(`LIT2-001160-C4`) and 4 are background citations; pilot term **and** US geography 5.
Scenario not `unknown` 2 (both 000203, described not named); **named scenario 0**.

## 10. Validation performed

| Check | Result |
| --- | --- |
| Frozen inputs | both readings and the sample pinned by SHA-256 (`climrr.wp4adj.FROZEN_INPUT_SHA256`, 43 files); a test checks each pin against its committed blob (reader 1 `e0857aa`, blind `c452d7d`) |
| Span integrity | **300** reader-1 and **377** reader-2 spans re-sliced from the hash-verified sources, **0 failures** (stop condition not met); re-checked by test where the corpus is configured |
| Alignment | one-to-one on all 20 items (the run fails on any many-to-one overlap); counts re-derived by test; every recorded judgement used, none for a pair that did not align |
| Rules | `wp1b.resolve_pair` validates each judgement against rules 3a--3c (a judgement that contradicts the rule fails the run); **no override**; 1 `unresolved_tie` |
| Nothing deleted | every reader-1 claim kept with its text, type, evidence and dimensions unchanged; blind-only claims added (test) |
| Evidence | every adjudicated claim carries an exact evidence span with `evidence_sha256` (test) |
| Reproduction | a second `wp4_adjudicate.py` run verified the comparison, the 21 adjudicated files and the document byte for byte |
| `pytest` / scan | **895 passed**; scan **0 hits** (after `90d55fc`, field 12) |

## 11. Failures, rejected cases, and known limitations

**Prior exposure.** `LIT2-001075` = LITCORPUS-00 `LIT-001536`, read twice in M4-WP2.
Reader 1 --- **also the adjudicator** --- had read it before; its record says so. The
blind reader was a fresh session and was not told; its record carries no exposure
note. Its 7 adjudicated claims (3 aligned, tier B) are recorded with that note.

**The adjudicator is reader 1** (prototype-exposed). Every judgement is recorded in
`src/climrr/wp4_judgements.py` and checked against the rules; none needed a paper
re-read. GUIDANCE may want a third party for the tier-B adoptions.

**Agreement is modest and concentrated on tags** (descriptive; n = 20 items, 50 pairs):
geography tag 27/50, temporal-frame tag 19/50 --- mostly reader 1 `explicit` with a
support span from another sentence where the blind reader wrote `inferred` from the
same span. Rule 3b kept `explicit` only where reader 1's span states the adopted
value (51 dimension decisions); 11 times it did not, and the tag became `inferred`.

**33 reader-1 and 35 blind claims found by one reader only** (tier C). In 9 items
both readers recorded the five-claim maximum and still chose partly different
passages. 9 reader-1-only claims fall on a passage the blind reader considered and
did not promote, and 6 blind-only claims on a passage reader 1 had set aside; both
are recorded on the claim.

**Hit precision vs the blind role.** Of 23 place-term pairs, the blind reader recorded
a claim naming the place in 6: 5 agree with reader 1's place-hit class, 1 disagrees
(`LIT2-001308` `california`: reader 1 study area through "San Diego County,
California"; the only blind claim naming "California" is a background citation,
contextual). 17 not comparable --- the blind reader recorded no claim naming the
place, as for both affiliation items and the `stephens` surname.

**Other limitations.** n = 20, a deterministic place-candidate sample, not
representative. Role vocabularies differed (free text vs the rubric's categories);
the mapping of reader 1's 42 role strings to classes is the adjudicator's
(`ROLE_CLASS_OF_R1`), recorded and tested for coverage.

## 12. Deviations from the approved plan

1--6. As listed at Phase 1 (de-duplicated reading view; `geography.role` added; config
   placeholder; claim-screen script; separate Phase A--B commit; two run records with
   the wrong interpreter deleted before commit).
7. **Secrets/paths scan fix** (`90d55fc`). The scan failed with 2 hits at `72617da`
   (reported there as 0): a standalone credential-class word in the
   `wp4_claim_screens.py` docstring, which the script embeds in
   `wp4_claim_screens.json`. Reworded ("place-term list") and regenerated; only that
   line changed, every count identical; JSON SHA-256 `4fec0b51…` → `125a566d…`.
8. **Rule 3-role** (new, needed because the package asks for geography *and role*):
   roles are compared by class; on disagreement the more conservative class is
   adopted (`unknown` > citation/person > affiliation > other > data source >
   contextual > cited study area > study area), and the pair becomes
   `adjudicated_modified`. This made **1** pair tier B instead of A
   (`LIT2-000786-C3`, role only). The order is the adjudicator's reading of "more
   conservative" for role; GUIDANCE should confirm it.
9. **A role class `cited_study_area`** for the area of a cited study whose finding a
   background claim restates; it counts as study geography for G-1 (M5-WP4). Not a
   decision on whether background citations may bridge (field 13).
10. Single-reader claims keep their reader's role and class (rule 4 analogue).

## 13. Open decisions and mentor questions

For GUIDANCE:
- **Criterion 16 (blind isolation) is only partly verifiable from artifacts.** The
  blind branch (`c452d7d`, from `38116a0`) never held reader 1's output (checked:
  no `wp4_claims`, `wp4_hit_*`, reading document or report in its tree), but its base
  tree holds the hit files and the prototypes, and its summary carries no protocol
  disclosure --- the M4-WP2 criterion-6 situation. **Put to Kaiyuan** to confirm what
  the blind session was given.
- Rule 3-role's conservative order and the `cited_study_area` class (field 12, 8--9).
- `LIT2-000203-C2` claim_type tie (background_citation vs projection): kept as
  `unresolved_tie`; it needs a re-read or a third reader, not authorized here.
- Whether `background_citation` claims may be bridge-eligible (from Phase 1), and the
  "standardized heat index" collision (see `M5_WP4_REPORT.md`).

## 14. Proposed gate status

Against the D-025 acceptance criteria 15--22:

| # | Criterion | Status |
| --- | --- | --- |
| 15 | Reader 1 receives no prefilled claim semantics from retrieval hits | **MET** --- reading frozen at `e0857aa` before any hit file was opened |
| 16 | Blind reader receives no hit locations, prototypes, reader-1 output, expected bridge result | **PARTLY VERIFIABLE** --- no reader-1 output in the blind tree; hit files and prototypes present in its base; put to Kaiyuan |
| 17 | Blind reading frozen before comparison | **MET** --- `c452d7d` committed before the merge `d90595c`; pins tested |
| 18 | Adjudication preserves disagreements and evidence tiers | **MET** --- both values and the rule recorded per dimension and role; tiers A 3, B 47, C 68; nothing deleted |
| 19 | Concept-hit precision classified separately from place-hit precision | **MET** --- separate vocabularies and item classes, carried in the adjudication document |
| 20 | Every promoted claim has exact source evidence | **MET** --- 677 spans re-sliced; every adjudicated claim's `evidence_sha256` checked |
| 21 | Compatibility runs only after adjudication | **MET** --- adjudication `6c856e2`, freeze `220ca84`, matrix `8436c25` |
| 22 | No lexical retrieval hit is treated as a bridge | **MET** --- only structured claims entered the matrix; 0 eligible pairs |

**Proposed status:** ready for GUIDANCE review, with criterion 16 pending Kaiyuan's
confirmation.

## 15. Proposed next bounded objective

GUIDANCE review of M4-WP4 and M5-WP4 together. If accepted, the next decisions are
the mentor's (family-level usefulness; place widening or a different unit) and
GUIDANCE's (SHI collision; background-citation eligibility; rule 3-role). Stage
2a--2c remains authorized and not started.
