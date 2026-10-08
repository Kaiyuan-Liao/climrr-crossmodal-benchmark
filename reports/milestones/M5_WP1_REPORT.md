# M5-WP1 --- Deterministic negative-case compatibility validation (27 claims x 3 prototypes)

**Machinery validation over `single_reader_provisional` claims (D-017).** The
81 rows are validation results, not accepted bridges, and they estimate nothing
about the 1,918-item corpus. Authorized by
[`docs/M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md`](../../docs/M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md).
No QA is generated.

## 1. Milestone ID and title

**M5-WP1 --- Deterministic negative-case compatibility validation.** The first
work package of **M5**. **M1 remains open** (D-014); M4-WP1b (the blind second
reading) is **pending**.

## 2. Objective

Answer two questions on the fixed set of 27 WP1 claims x 3 WP3b prototypes:
does deterministic compatibility machinery behave correctly on every one of the
81 pairs; and does this content-independent sample contain any pair compatible
on all five dimensions (concept, geography, time, scenario, direction)? The
code does not assume the answer to the second (ruling action 14, criterion 18).

**Excluded, and not done:** semantic similarity, embeddings, any model judgement
of a pair, synonym tables, any new concept mapping, reading or searching the
corpus, replacing the WP1 sample, QA.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/m5-wp1`, from `main` at `b3484b4` (state refresh on top of the M4-WP1 merge `0053968`) |
| Phase A --- inputs frozen | `000e71e`; no comparison code exists at that commit |
| Phases B--D --- rules, matrix, tests | `703083b` |
| Clean-head evidence runs | both scripts re-run at `703083b` on a clean tree (`git_dirty: false`); **zero tracked files changed** --- every output reproduced byte for byte |
| This report, `PROJECT_STATE.md`, brief status | the commit after `703083b`; its SHA travels with the hand-back |
| Remote | **not pushed, not merged** (work-package instruction) |

## 4. Data version and checksums

| Object | SHA-256 |
| --- | --- |
| `artifacts/bridges/m5wp1_inputs.json` (the freeze) | `bc22b4fa9344283fd31e9b7ac1f70fa53276d8dd171d6749933a4cf0b6a628cc` |
| `config/geo_disjoint_list.yaml` (G-2 list) | `2bdd67551699f4862b6afb32ae3c7bf1aca1a949c54501faadce241089439994` |
| `artifacts/bridges/m5wp1_matrix.json` | `526ac573f58a027c53b99e90a88fc7b3509c550afe205a9d6f15f74072d4cd02` |
| `artifacts/bridges/m5wp1_matrix.csv` | `cc7139f342e5dc5fe07e3b6583547b173e0cd1c08ca63d4983568de07ade8031` |
| `docs/M5_WP1_COMPATIBILITY.md` | `4b354a089472d3722bdb1bef218a0c92a32352c93a2736ab668b66318f48c7b2` |
| Corpus manifest (`LITCORPUS-00`) | `3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a` |
| `wp1_sample.json` | `5cb81f9585040dd1d73a89ca7062d3c5e0060112f54e08ef4795db96a657b578` |
| `FullData.csv` (from `data/manifest.json`; **not read**) | `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e` |

The freeze pins, per claim, the claim-file SHA-256, the source corpus file
SHA-256 and a record hash (SHA-256 of the canonical JSON of the claim object);
per prototype, the file SHA-256 and the record hash. Every prototype's
`csv_sha256` is checked against the manifest. `scripts/compat_matrix.py`
re-verifies the freeze before reading anything and fails closed. The clean-head
run record `reports/runs/20261008T205424Z_local_compat_matrix.json` carries the
same three output hashes.

## 5. Environment and execution location

conda environment `climrr`, Python 3.11.16, all D-007 pins `matches_pin: true`,
location `local`. Sophia not used; nothing here needs it. The external corpus
was not opened; `FullData.csv` was not read.

*One false start, recorded:* the first freeze run used conda `base` instead of
`climrr` (pins mismatched). Those two run records were deleted, never committed,
and the freeze re-run under `climrr`; the frozen file is deterministic and its
bytes were identical.

## 6. Work completed

**Phase A.** `src/climrr/compat.py` (freeze part) and
`scripts/freeze_m5wp1_inputs.py` write `m5wp1_inputs.json` once and verify on
every later run. Committed before any comparison code existed (`000e71e`).

**Phase B.** `src/climrr/compat.py` (rules part): each side of each dimension is
derived by a named rule that keeps the raw source value; each judgment cites the
comparison rule that decided it. `config/geo_disjoint_list.yaml` is the fixed
G-2 list.

**Phase C.** `scripts/compat_matrix.py` writes `artifacts/bridges/m5wp1_matrix.json`
(81 rows; per row: pair id, claim id, claim type, background-citation flag,
validation status, prototype id, five judgments each with status, rule id,
claim value, prototype value and reason), `m5wp1_matrix.csv`, and the generated
`docs/M5_WP1_COMPATIBILITY.md`. Run record emitted.

**Phase D.** `tests/test_compat.py`: 74 tests, synthetic claims against the real
prototype records, plus shape checks on the real matrix.

**Phase E.** This report; `PROJECT_STATE.md`; `MENTOR_BRIEF.md` status line.

## 7. Deliverables and exact file paths

**New:** `src/climrr/compat.py`; `scripts/freeze_m5wp1_inputs.py`,
`scripts/compat_matrix.py`; `config/geo_disjoint_list.yaml`;
`artifacts/bridges/m5wp1_inputs.json`, `m5wp1_matrix.json`, `m5wp1_matrix.csv`;
**`docs/M5_WP1_COMPATIBILITY.md`**; `tests/test_compat.py`; this report;
run records `reports/runs/20261008T2050*`, `20261008T2053*`, `20261008T2054*`.

**Changed:** `docs/PROJECT_STATE.md`, `docs/MENTOR_BRIEF.md`.

## 8. Methods and rules that affect scientific meaning

All rules are in `compat.RULES` and printed in full in
`docs/M5_WP1_COMPATIBILITY.md`. In short:

1. **U-1.** `unknown` on either side → `not_evaluable`, never `incompatible`.
2. **Concept, C-1.** Claim: the tagged string, lowercased, whitespace collapsed
   (CV-C1), **no mapping**. Prototype: `fwi_seasonal_value` (fire-weather family:
   P-CELL-1, P-COUNTY-1) or `heatindex_days_above_105F` (heat-index family:
   P-STATE-1) (PV-C1). Compatible only if identical under the same
   normalization; otherwise `not_evaluable` / `no_approved_mapping`. **Never
   incompatible.** **Approved mappings: none exist in the repository;**
   `APPROVED_CONCEPT_MAPPINGS` is empty and a test keeps it so.
3. **Geography.** Prototype: level and label --- cell id `R106C361`; `Oklahoma,
   Stephens`; `California` --- with `G.provenance_status` carried
   (`verified_from_dictionary`, `inferred_candidate`, `inferred_candidate`).
   **G-1** compatible only if an `explicit` claim geography equals the label
   exactly, case-insensitively. **G-2** incompatible only if an `explicit` claim
   geography names, as a whole word, a country on the committed list (China,
   India, Tajikistan, Australia) and names no not-disjoint scope (global,
   worldwide, Northwest Atlantic) and no US marker. **G-3** everything else
   `not_evaluable`: a city or village, a different granularity, an `inferred` tag.
4. **Time.** Prototype: year ranges stated in `T.per_role` (PV-T1) --- 1995-2004
   / 2085-2094 for P-CELL-1 and P-COUNTY-1; **none for P-STATE-1**, whose record
   says only "Historical" / "End-Century". Claim: explicit four-digit ranges
   (`YYYY-YYYY`, `YYYY to YYYY`) in an `explicit` frame, hulled if several
   (CV-T1). **T-1** compatible on overlap with the future window. **T-2**
   incompatible only if the claim is a `finding`, its range ends before 2045,
   and the prototype has a future window starting at or after 2045. **T-3**
   otherwise `not_evaluable`. *The choice, documented:* the stricter T-2 the
   work package settled on --- `finding` only, explicit range only, fixed 2045
   cut-off (the earliest future window in the pilot family) --- so a mechanism,
   projection or background claim about a past period is `not_evaluable`, not
   incompatible.
5. **Scenario, S-1.** Both explicit RCP labels: identical → compatible,
   different → incompatible; anything else `not_evaluable`. The comparator takes
   the claim's `scenario` dimension and nothing else; the laboratory-treatment
   field is not named anywhere in the M5 code (tested).
6. **Direction, D-1.** Evaluated only when concept is `compatible`; otherwise
   `not_evaluable` / `concept_not_comparable`. When evaluated, it reads only the
   exact words `increase`, `decrease`, `no change`.

## 9. Results with compact tables or examples

**Per dimension, over 81 pairs:**

| Dimension | compatible | incompatible | not_evaluable |
| --- | ---: | ---: | ---: |
| concept | 0 | 0 | 81 |
| geography | 0 | 39 | 42 |
| time | 0 | 14 | 67 |
| scenario | 0 | 0 | 81 |
| direction | 0 | 0 | 81 |

**Per prototype** (compatible / incompatible / not_evaluable): P-CELL-1 and
P-COUNTY-1 are identical --- geography 0/13/14, time 0/7/20, the other three
0/0/27. P-STATE-1: geography 0/13/14, **time 0/0/27** (no year window in the
record).

- **Pairs compatible on all five dimensions: 0.**
- **Pairs with at least one `incompatible`: 39** (13 claims x 3 prototypes).
  14 of them have two.
- **Which rule produced each `incompatible`:**
  - **G-2, 39 judgments** --- 13 claims, each against all 3 prototypes: China
    (`LIT-000381` C1, C2, C4), Tajikistan (`LIT-000571-C1`), India
    (`LIT-001141` C2--C5), Australia (`LIT-001711` C1--C5).
  - **T-2, 14 judgments** --- 7 `finding` claims x {P-CELL-1, P-COUNTY-1}:
    `LIT-000381` C1, C2 (1992-2015); `LIT-001141` C2, C3 (2001-2021);
    `LIT-001711` C1 (1988-2012), C3 (1999-2006), C5 (1961-1965).
  - **No other rule fired `incompatible`.** C-1, S-1, D-1: zero.
- **Every T-2 judgment falls on a pair G-2 already marks incompatible.** The
  other **42 pairs have no `incompatible` at all**: they fail only by being
  `not_evaluable`.

**Reasons for `not_evaluable`** (full table in the compatibility document):
concept `no_approved_mapping` 81; scenario `claim_value_unknown` 81; direction
`concept_not_comparable` 81; geography `claim_value_unknown` 12,
`claim_geography_not_explicit` 9 (the inferred "Northwest Atlantic" of
`LIT-000191` C1--C3), `named_scope_not_disjoint_from_united_states` 3
(`LIT-001521-C4`, global / worldwide), `no_exact_label_match_and_no_listed_disjoint_place`
18 (villages, a forest plot, a city); time `claim_has_no_explicit_year_range`
39, `claim_value_unknown` 15, `prototype_window_has_no_year_range` 9,
`claim_type_not_finding` 4.

Claim type is visible on every row; the 2 `background_citation` claims give
**6 pairs**, flagged `is_background_citation: true` in the JSON and CSV and
bold in the document's table.

**Bounded conclusion, verbatim from the ruling:** *No fully compatible pair was
found under the current deterministic rules in this fixed provisional pilot
set.*

## 10. Validation performed

| Check | Result |
| --- | --- |
| `pytest` (`climrr` env) | **640 passed** (566 before; 74 new in `tests/test_compat.py`) |
| `scripts/verify_no_secrets_or_paths.py` | **0 hits** --- see field 11 for one hit fixed before the final Phase B--D commit |
| Freeze | `m5wp1_inputs.json` re-verified on every run; tampering with any claim or prototype record hash fails (tested) |
| **Positive path** | `test_the_positive_path_a_fully_matching_claim_is_compatible_on_all_five`: a synthetic claim against the **real** P-COUNTY-1 and P-CELL-1 records comes out `compatible` on all five, by C-1, G-1, T-1, S-1, D-1. **Passes** |
| 81 pairs exactly once | tested against the product of the frozen ids |
| Determinism | the tracked matrix re-derives from the frozen inputs (tested); clean-head re-run changed zero tracked files |
| No expected total | no test asserts the real all-compatible count; `test_summary_counts_an_all_compatible_row_when_one_exists` checks the counter on a fixture where it is 1; the document's conclusion is tested as appearing **iff** the count is zero |
| Firewall | AST test: `compat.py` and `compat_matrix.py` import only stdlib, `yaml` and `climrr` |

## 11. Failures, rejected cases, and known limitations

**What happened.**

- **One scan hit, fixed.** The secrets scan flagged the word "token" in rule
  text (12 lines; a false positive on a credential pattern). My pre-commit check
  piped the scanner through `tail`, which hid its exit status, so the first
  Phase B--D commit went in with the hit. It was reworded ("label", "word"), the
  matrix regenerated, and that unpushed commit amended; `703083b` scans clean.
  Now the pre-commit check reads the scanner's own exit status.

**Known limitations.**

- **Under these rules, zero is structural, not a finding about the reading.**
  With no approved concept mapping, C-1 can match only a claim whose concept
  string *is* a canonical ID such as `fwi_seasonal_value`, which no paper
  states; and with `scenario` `unknown` in 27 of 27 claims, S-1 cannot be
  compatible. **No real claim could have been all-compatible, whatever its
  geography or time.** The machinery is shown to work (positive path on
  fixtures); the real set does not exercise it past concept. This matters for
  M4-WP2 (field 13).
- **P-STATE-1 can never be time-compatible as recorded.** Its `T` field states
  "Historical" / "End-Century" with no years; the windows were taken from the
  record, as the work package says, not imported from the dictionary or from
  the other two prototypes. Even a perfect synthetic claim reaches four of five
  against it (tested). If P-STATE-1 is to be a positive-case target, its record
  needs the years --- a prototype rebuild, outside this package.
- **The year parser is lexical.** `LIT-001711-C1`'s range is a model
  calibration period ("model calibrated on 1988-2012"), not the period the claim
  is about; `LIT-001711-C5` "late 1930s to early 1960s; 1961-1965" contributes
  only 1961-1965. Both T-2 results stand under the rule as written and both
  pairs are already G-2 incompatible.
- **T-2 is stricter on paper than in spirit.** `LIT-000381` C1/C2 (1992-2015)
  and `LIT-001711-C3` (1999-2006) overlap the prototypes' *baseline* decade
  1995-2004; T-2 compares only against the future window, as specified.
- **G-2 is a word match.** "China" anywhere in an explicit geography fires it,
  unless a not-disjoint scope or US marker is also present. A sentence such as
  "exports from China to California" would misfire; no WP1 geography is of that
  form.
- **The claims are single-reader provisional**, read by a model that also built
  the prototypes (M4-WP1 field 11). Nothing here changes that.

## 12. Deviations from the approved plan

Each is a choice where the work package was silent or ambiguous; none decides
any real pair differently from the conservative alternative.

1. **P-STATE-1 has no time window**: `not_evaluable` /
   `prototype_window_has_no_year_range` (9 non-unknown pairs), rather than
   reading "End-Century" as 2085-2094. "From the record" was taken literally.
2. **"Northwest Atlantic" is `not_disjoint`.** The package's parenthetical can
   be read as putting it on the disjoint list. It is an ocean region adjoining
   the US coast and including US waters, so it is not explicitly disjoint from
   the United States. **No real pair depends on it**: every claim naming it is
   tagged `inferred` and stops at G-3 first.
3. **G-1 and G-2 require an `explicit` tag.** "The claim names" was read as
   explicit; `inferred` geography is `not_evaluable`.
4. **C-1 normalizes the prototype ID too.** The package lowercases the claim
   side; without the same step on the prototype side
   `heatindex_days_above_105F` (capital F) could never match anything.
5. **County label rendering** for G-1 is `State, NAME` (`Oklahoma, Stephens`),
   the tuple order the prototype record and its generated sentence use.
6. **"Makes no projection"** in T-2 is `claim_type == finding`; several ranges
   in one frame are hulled.
7. **Rule IDs added**: `U-1` (unknown), `G-3` and `T-3` (the explicit
   "otherwise" cases), and derivation rules `CV-*` / `PV-*`, so every judgment
   and every derived value cites a rule.
8. **D-1's word list** (`increase`, `decrease`, `no change`) is the prototype's
   own direction vocabulary, read exactly; it is not a synonym table and maps no
   claim phrasing onto it.
9. **`geo_disjoint_list.yaml` lives in `config/`**, beside `project.yaml`.

## 13. Open decisions and mentor questions

**M4-WP1b is still pending.** Under criterion 21 this package can therefore
pass **only as machinery validation**.

**Against the ruling's five conditions for a relevance-guided M4-WP2:**

| # | Condition | Status from this evidence |
| ---: | --- | --- |
| i | Deterministic machinery works correctly on all 81 pairs | **Met**, as machinery: all 81 present once, every judgment carries rule and values, positive path exercised on fixtures |
| ii | The content-independent sample yields no fully compatible pair, or too few to exercise the positive case | **Met**: 0 all-compatible, and the positive path is unreachable on real claims under current rules |
| iii | Failure modes visible dimension by dimension | **Met**: per-dimension, per-prototype and per-reason counts in the compatibility document |
| iv | WP0 shows prototype concepts present in collection vocabulary | **Not this package's evidence**; M4-WP0 recorded 1 exact concept-term match and 3 absent (`fire weather` x2, `heat index`) --- for GUIDANCE to weigh |
| v | Second reading does not materially overturn the negative conclusion | **Awaits M4-WP1b** |

**For GUIDANCE and COORDINATOR, a decision this evidence surfaces:** a
relevance-guided M4-WP2 sample, under the **same** rules, will also produce
zero all-compatible pairs --- C-1 has no approved mapping and literature does not
state canonical IDs. Before M4-WP2 can test the positive case on real claims,
someone must decide whether, and by what approved deterministic procedure,
claim concept strings may map to canonical IDs. The EXECUTOR has not proposed
one and may not author one.

**Also open:** whether P-STATE-1's record should carry explicit year windows
(field 11); Q19--Q21 for JL, unchanged.

## 14. Proposed gate status

The ruling's 22 acceptance criteria:

| # | Criterion (abridged) | Status | Evidence |
| ---: | --- | --- | --- |
| 1 | Scenario and experimental condition separated before matrix generation | **MET** | D-017 closure `8a43313`; `scenario` `unknown` 27/27 in the frozen claims |
| 2 | Input identities frozen, 27 claims and 3 prototypes | **MET** | `m5wp1_inputs.json`, `000e71e`; tamper tests |
| 3 | Every claim carries `single_reader_provisional` or later | **MET** | 27/27 in the freeze and on all 81 rows (tested) |
| 4 | All 81 pairs exactly once | **MET** | `test_every_frozen_pair_appears_exactly_once` |
| 5 | Every pair has all five judgments | **MET** | `test_every_row_has_five_judgments…` |
| 6 | Every judgment is compatible / incompatible / not_evaluable | **MET** | same test; `_judgment` asserts it at construction |
| 7 | Every judgment cites a rule ID and both values | **MET** | same test; derivation rule on each side too |
| 8 | `unknown` always `not_evaluable` | **MET** | `test_unknown_never_yields_incompatible` (15 cases) and on the real matrix |
| 9 | Concept mismatch not automatically incompatible | **MET** | C-1 has no incompatible branch; 15 test cases incl. UHI, smoke, drought |
| 10 | Geography incompatibility requires explicit disjointness | **MET** | G-2 committed list; 11 test cases (city, state-vs-county, global, NW Atlantic, Indiana) |
| 11 | Direction not evaluated across non-comparable concepts | **MET** | D-1; 81/81 `concept_not_comparable`; tested |
| 12 | Experimental treatment never in the scenario comparison | **MET** | `test_experimental_condition_cannot_reach_the_scenario_comparison` |
| 13 | Claim type visible | **MET** | every row, JSON, CSV, document |
| 14 | `background_citation` distinguishable | **MET** | `is_background_citation` flag; bold in the table; 6 pairs |
| 15 | No semantic embeddings | **MET** | AST import test |
| 16 | No LLM judges pair compatibility | **MET** | rules only; AST import test |
| 17 | No pair removed as irrelevant | **MET** | 81 = 27 x 3 |
| 18 | Implementation does not assert zero | **MET** | no such test; counter tested at 1 on a fixture; conclusion conditional |
| 19 | If zero, only the bounded conclusion | **MET** | verbatim sentence, nothing broader |
| 20 | No generalization to the 1,918-item corpus | **MET** | stated on the document's first line and here |
| 21 | Second reading completed, or pending → machinery validation only | **MET --- pending**; this package is proposed as **machinery validation only** |
| 22 | No QA generated | **MET** | none |

**Proposed status:** ready for GUIDANCE review as **machinery validation**;
22 criteria met, criterion 21 by the pending branch. The structural-zero
observation (field 11) and the concept-mapping question (field 13) are put to
GUIDANCE with it.

## 15. Proposed next bounded objective

M4-WP1b — blind second reading of the ten papers; then M4-WP2 — relevance-guided candidate sample, retrieval rule to be proposed to GUIDANCE.
