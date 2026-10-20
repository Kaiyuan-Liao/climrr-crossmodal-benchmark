# M4-WP4 --- 20-paper concept/place candidate reading pilot

**Status: Phase 1 (reader 1) complete. Blind reading, comparison, adjudication,
evidence tiers and compatibility PENDING.** Branch `work/m4-wp4-read`, not pushed,
not merged. The blind reader runs next in a fresh session on `main` and must not
see this branch.

---

## 1. Milestone ID and title

M4-WP4 (reading package M4-WP4r1) --- first reading of the frozen 20-paper
LITCORPUS-02 candidate sample by reader 1, with concept-hit and place-hit precision
classified after reading. Authorized by
[`docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md`](../../docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md)
(D-025, Track A; required actions 8--15, acceptance criteria 8--22).

## 2. Objective

Read the 20 frozen candidates (10 fire weather, 10 extreme heat) with the unchanged
WP1/WP2 rubric; record scope, terminal status and up to five claims per item with
exact evidence spans; then, only after the reading is frozen, classify every matched
concept term and place term as the ruling's precision categories.

**Excluded:** the blind second reading, comparison, adjudication and evidence-tier
assignment beyond `C`; compatibility with P-CELL-1, P-COUNTY-1, P-STATE-1 v2; any
use of a retrieval hit as a bridge; QA; Stage 2a--2c. The sample is a
**deterministic rank sample of lexical place candidates from LITCORPUS-02; not
representative of the corpus or the literature.**

## 3. Repository commit SHA

- Base: `main` at `38116a0` (merge of M4-WP3).
- **`e0857aa`** --- Phases A--B: sample verified, reader-1 records. Committed
  **before any `hits.csv` or place-hit location was opened.**
- Phase C--D commit (hit classification, claim screens, reading document, this
  report, project state): the head of `work/m4-wp4-read` reported with this package.
- Remote: nothing pushed (package instruction).

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
| `artifacts/literature/wp4_claim_screens.json` | `4fec0b51…aa92` | output |

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

PENDING --- whole-package validation after blind reading and adjudication. Phase-1
checks run on this branch: `python -m pytest -q` 856 passed at `e0857aa` and 858
passed before the Phase C--D commit (two tests added); `python scripts/verify_no_secrets_or_paths.py`
0 hits both times; 300/300 spans re-sliced (builder and `tests/test_wp4_claims.py`); 81/81 frozen
first hits reproduced.

## 11. Failures, rejected cases, and known limitations

**Prior exposure (required note).** `LIT2-001075` (item `272852900`) is
LITCORPUS-00 `LIT-001536`, already read twice in M4-WP2. Reader 1 is therefore not
naive to it. It was re-read from its source bytes; no WP2 artifact, WP2 document,
M5-WP2 document or bridge file was opened in this package. The item's record carries
`prior_exposure`; the blind reader's view of it is the cleaner one.

Phase-1 limitations (the rest PENDING after adjudication):
- One reader; every claim tier `C`. Scope is borderline for 000673 (aerosol forecast
  model), 001236 (IoT interoperability), 001293 (statistics method) and 000803
  (`ambiguous`).
- Several source files are damaged (truncated sentences, merged section keys,
  plot-marker residue, repeated passages, a `$` in place of `~` in 001160); recorded in
  item notes, never repaired.
- `LIT2-001308-C4` (FWI projection to 2040) rests on a truncated sentence; its concept
  link is `inferred`.
- 000662's `heat index` class (`incidental`) is a close call.

## 12. Deviations from the approved plan

PENDING --- final list after adjudication. Phase-1 deviations so far:
1. De-duplicated reading view for repeated text (a reading aid; all quotes verified
   on the raw string).
2. `geography.role` added to the record (asked for by the package, absent from the
   WP1 schema).
3. `litcorpus02_root` placeholder added to `config/local_paths.example.yaml` (the key
   existed only in the untracked config).
4. A claim-screen script added to produce the screen counts the package asks to
   report.
5. Phases A--B committed separately (`e0857aa`) before Phase C, to evidence the order.
6. Two run records first produced with an interpreter that fails the D-007 pins were
   deleted (never committed) and the scripts re-run in env `climrr`.

## 13. Open decisions and mentor questions

PENDING --- after adjudication. Raised by Phase 1 for GUIDANCE:
- **C-2 matches "standardized heat index".** The screen counts `LIT2-001160-C4` as a
  heat-index-family concept although SHI is a different index; the family matcher is
  lexical. Whether a mask (like `extended heat index`) is needed is a governance
  decision, not reader 1's.
- Whether `background_citation` claims (19) are eligible for compatibility.
- Whether the primary-class rule (most substantive occurrence wins) is the intended
  item-level summary.

## 14. Proposed gate status

PENDING --- after blind reading, comparison, adjudication and compatibility
(acceptance criteria 16--22 cannot be judged yet).

## 15. Proposed next bounded objective

PENDING. Next step as already authorized by D-025: the blind reading of the same 20
items in a fresh session on `main`, without this branch, the hit files, the
prototypes or this report.
