# Track D v1 --- table-grounded question templates (design + dry run)

Authorized by the mentor direction D-031 (2026-10-22) and the GUIDANCE guardrails
of 2026-10-27 (**D-033**), with owner decisions recorded as **D-034**. **No model
call. No corpus retrieval run. No QA accepted.** No column status, concept-map
entry or compatibility rule changed; index 117 stays unlabeled. Fields 1--9.

## 1. Milestone ID and title

**Track D v1 --- table-grounded question templates: slot vocabularies, 18
templates, generator with deterministic answers, dry run.** M1 remains open
(D-014). Track C run 2 is still pending.

## 2. Objective

(A) Slot vocabularies drawn only from authorized sources, each value carrying a
source and an authorization. (B) Fifteen to twenty templates on the WildfireGPT
mechanism (D-032). (C) Exhaustive enumeration of the `table_only` templates,
with answers computed from `FullData.csv` after the manifest check, and the
three prototypes reproduced. (D) A generated doc, the state refresh and this
report. **Excluded:** retrieval, model calls, linking passages, accepting any QA,
changing any status, merging, pushing.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/meeting-2026-10-22`, from head `7f49264` |
| **Build commit** | **`7995cc3`**: slots, templates, module, script, tests, generated outputs and doc |
| **Evidence run** | `scripts/generate_template_questions.py` at `7995cc3`, **`git_dirty: false`**: `reports/runs/20261028T183729Z_local_generate_template_questions.{json,md}`. The outputs are byte-identical to the committed ones (no tracked file changed) |
| Report commit | the commit carrying this report, the run record, D-034, `REFERENCES.md` and `PROJECT_STATE.md` (head SHA reported to the COORDINATOR) |
| Remote | **not pushed, not merged** |

## 4. Data version and checksums

| Object | SHA-256 | Bytes | Notes |
| --- | --- | --- | --- |
| `data/raw/FullData.csv` (read) | `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e` | 296,407,423 | manifest check passed before the read; 62,834 rows |
| **`data/metadata/templates/slots_v1.yaml`** | **`d40f835e969cc0dac0ed7de3affd1ce4ef26152a56252f042b7dbdf889b47e10`** | 34,439 | |
| **`data/metadata/templates/templates_v1.yaml`** | **`5eb50916840cb21227845c255c95728807ec33fc74c9e258d889c0d7c8aa00f9`** | 17,621 | |
| **`artifacts/templates/questions_v1.jsonl`** | **`28fcb3c322db649bfd2438a67a930f6c0ed06a28db6ca5b40041bfd9c1d7b100`** | 14,099,943 | **gitignored** (field 9, item 4); pinned in the summary; 5,217 records |
| `artifacts/templates/questions_v1_sample.jsonl` | `11cdf1f2c232f14b0bbc3a86748f4ca7d9f2d4e8d854f8eaed7f726ea5c6fa4f` | 55,673 | tracked; 21 records (first of each `table_only` template + the doc examples) |
| `artifacts/templates/questions_v1_summary.json` | `9549076368510aadb3dfa4245ee380ed42253278bcf6a701f3b01fd8e0370ad7` | 2,736 | counts and the questions-file pin |
| `artifacts/templates/prototype_reproduction_v1.json` | `f17d932b7173123eec742c90bc65a5222d61a2704e58e9fef472849fcab63168` | 4,296 | |
| `docs/TEMPLATE_QUESTIONS_V1.md` (generated) | `080f9796be513e9f2884e3537909c23b49ec7d720d313eed9f50a5a76541e7ea` | 28,349 | test: equals a re-render from the tracked files |
| `LLM_Eval-main.zip` (read, not stored) | `a88a9f0df284213769b8e65abd69c2c0e8c5f7dec0d46c0d2121338e7ad2938f` | 23,271 | matches D-032 |

Read and unchanged: `concept_map.yaml`, `dictionary_extracted.txt`,
`artifacts/profiles/dictionary_coverage.json`, `inferred_candidates.yaml`,
`qa_types_v1.json`, the three prototype records (their hashes are recorded in the
reproduction file).

## 5. Environment and execution location

| | |
| --- | --- |
| Host | local (Mac), location label `local` |
| Python | 3.11.16, conda env `climrr`; pins satisfied |
| pip freeze | `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51` (same as Track C) |
| Model calls / retrieval runs | **0 / 0** (recorded in the run record's config snapshot) |

Development runs used the conda **base** interpreter by mistake. Their run
records were deleted before any commit, and the generator was re-run in
`climrr`, which produced byte-identical outputs.

## 6. Work completed

- **Phase A --- slots.** Concept: `fire_weather_index`, whose summer value and
  difference columns 189--193 are `inferred_candidate` (IC-006..IC-010) and so
  carry the work package's refusal note, and `heat_index`, with four verified
  threshold metrics. Each concept lists its concept-map surface forms. The
  exclusions are listed visibly: FWI autumn, spring and winter (`partially_resolved`);
  heat-index DayMax (IC), SeaMax and change columns; verified `Pmid`/`Pend` not
  used; and six ungoverned dictionary concepts. Location: cell `R106C361`
  (verified); county `Stephens, Oklahoma` (`our_reading`); 49 state labels with
  row counts (`inferred_candidate`, IC-012), with the 7 empty-label rows excluded.
  Period, scenario and season are quoted from cited dictionary lines. Statistics
  use rules DR-TD-001..007.
- **Phase B --- templates.** 18 templates: 11 `table_only`, plus 7 that need a
  linked passage (6 `table_plus_paper`, plus 1 `comparison`, which is Q3).
  They cover direction, absolute and percent change, baseline, future, two
  scenarios, two places, two periods, multi-concept, claim-to-region (largest
  and smallest), pattern→explanation, cross-source validation, cross-location
  comparison, regional contrast, compound risk and a recommendation-seeking
  template. Retrieval rule RT-1 applies to all of them.
- **Phase C --- generator.** One manifest-checked scan of the table, exhaustive
  enumeration (no randomness) and the prototype arithmetic. The concept gate
  lives in one function (`concept_block_reason`), and audit mode is used only
  for the prototype reproduction.
- **Phase D --- docs.** The generated doc, `REFERENCES.md`, D-034, `PROJECT_STATE.md`
  and this report.

## 7. Deliverables and exact file paths

`data/metadata/templates/slots_v1.yaml`, `data/metadata/templates/templates_v1.yaml`,
`src/climrr/templates.py`, `scripts/generate_template_questions.py`,
`tests/test_templates.py` (29 tests), `artifacts/templates/questions_v1.jsonl`
(gitignored), `questions_v1_sample.jsonl`, `questions_v1_summary.json`,
`prototype_reproduction_v1.json`, `docs/TEMPLATE_QUESTIONS_V1.md`,
`docs/REFERENCES.md` (Track D v1 table), `docs/DECISION_LOG.md` (D-034),
`docs/PROJECT_STATE.md`, this report, and the run record.

## 8. Methods and rules that affect scientific meaning

1. **Concept gate.** A concept column is read for an answer only if it is
   `verified_from_dictionary` or `owner_confirmed`. Otherwise the question is
   `blocked_inferred_columns`: no answer, `retrieval_authorized: false`,
   `usable_for: []`. This blocks every FWI question.
2. **Locations are named row sets** (A-G3), never geometries. State and county
   answers are computed and tagged `provisional` (D-034). A cell answer is not
   provisional.
3. **Arithmetic reused from the prototypes.** Decimal arithmetic on the raw
   strings, rounded to 15 places half-to-even. The change is computed per cell
   and then averaged, unweighted. FWI uses its difference column (A-DIR2); heat
   index uses future minus baseline (A-DIR1). The ruling's verbatim label
   travels with every county- or state-level mean.
4. **New rules.**
   - DR-TD-004: percent change of the aggregate, 100 × mean change / mean
     `[PERIOD_FROM]`, over the same cells. A zero denominator gives
     `not_computable`. It is never a mean of per-cell percent changes.
   - DR-TD-006: signed comparison, so a decrease counts as smaller.
   - DR-TD-007: extremum over the 49 states, with ties listed and
     non-computable states excluded and counted.
5. **Empty cells are excluded, never read as zero.** Statistics use the cells
   that are non-empty on every column the question reads.
6. **RT-1 retrieval terms** are the concept surface forms, a state label, the
   scenario tokens and future-period words. They never include a threshold, a
   statistic or season word, a cell id, the county NAME, or an ungoverned term.
7. **Enumeration caps.** TD-T07 pairs California (P-STATE-1's state) with each
   other state; TD-T09 pairs FWI with each heat-index metric; `min_cells` = 1.

## 9. Results with compact tables or examples

**Counts.** 18 templates (11 `table_only`). **5,217 filled questions:
3,186 `computed`, 498 `not_computable`, 1,533 `blocked_inferred_columns`.**

| By | computed | not_computable | blocked |
| --- | --- | --- | --- |
| `heat_index` | 3,186 | 498 | 0 |
| `fire_weather_index` | 0 | 0 | 921 |
| FWI + heat index (TD-T09) | 0 | 0 | 612 |
| cell (1) | 48 | 12 | 27 |
| county (1) | 48 | 12 | 27 |
| state (49) | 3,042 | 474 | 1,467 |
| all states (TD-T10/T11) | 48 | 0 | 12 |

Not computable: **408** `no_column_realizes_scenario` (TD-T06, RCP4.5) and
**90** `zero_baseline` (TD-T03). 3,138 of the 3,186 computed answers are
provisional (every state and county answer).

**Prototype reproduction (test): all equal.**

| Prototype | Filled template | Baseline | Future | Change | Direction | In questions |
| --- | --- | --- | --- | --- | --- | --- |
| P-CELL-1 | TD1-T02-00002 | 25.080200200000000 | 31.189300540000001 | 6.109189990000000 | increase | blocked (audit-mode values only) |
| P-COUNTY-1 | TD1-T02-00005 | 25.784530258000000 | 31.867660141000000 | 6.083151960000000 | increase | blocked (audit-mode values only) |
| P-STATE-1 v2 | TD1-T02-00326 | 2.152729629062611 | 15.362681281927839 | **13.209951652865228** | increase | **computed, equal** |

**Three examples, one per statistic:**

- `TD1-T01-00154`, **direction**: "Under RCP8.5, does the number of days with
  daily max heat index above 95 F in summer (June, July, August) in grid cell
  R106C361 increase or decrease between the modeled historical period
  (1995-2004) and mid-century (2045-2054)?" → **increase**. DR-TD-005; columns
  240/246, both verified; change 23.133334480000002; not provisional.
- `TD1-T02-00326`, **absolute change**: P-STATE-1 as a template, heat-index
  days above 105 F, California, historical → end-of-century, RCP8.5 →
  **13.209951652865228 days**. DR-TD-003; 2,827 of 2,831 cells used;
  provisional (IC-012; provisional aggregation rule).
- `TD1-T03-00154`, **percent change**: the same cell and metric as T01-00154 →
  **58.123956169751619 percent**. DR-TD-004; 100 × 23.133334480000002 /
  39.799999870000001.

**Slots that are `inferred_candidate` or `our_reading`.**
- `inferred_candidate`: the FWI concept, its metric and columns 189--193
  (IC-006..IC-010), so its answers are blocked; and every state location
  (`State`, IC-012), so its answers are computed and provisional.
- `our_reading`: the county location (`(State, NAME)`, IC-011 + IC-012) and
  every statistic rule DR-TD-001..007.

**Gate.** `pytest`: **1146 passed, 2 skipped** (29 new in
`tests/test_templates.py`). `verify_no_secrets_or_paths.py`: **0 hits**.

**For the COORDINATOR / GUIDANCE (decisions, not improvised):**
1. **State geography (D-034).** `State` is `inferred_candidate`. The owner chose
   to compute state answers and tag them provisional, against the literal
   Phase-C rule. Does that stand? Does D-033's "no unverified column, even as a
   query term" also exclude a state label as a query term?
2. **Verified FWI percent-change columns** (`wildfire_summer_Pmid`/`Pend`,
   194/195) are not used. Their field entries state no scenario, and a
   per-cell percent change may not be averaged. Should a cell-level FWI percent
   change from them be allowed?
3. **RCP4.5** is realized by no governed column, so TD-T06 is not computable.
   Should it be kept as a placeholder or dropped?
4. **Deviation: `questions_v1.jsonl` is gitignored** (14 MB, regenerable;
   CLAUDE.md "never commit large or regenerable outputs") and pinned by SHA-256,
   as D-005 does for the raw table. A 21-record sample is tracked. The
   full-file test fails when the file is absent unless `CLIMRR_ALLOW_MISSING_RAW=1`
   is set. Alternative: commit it (it would be 7× the largest tracked file).
5. **QA-type fit.** TD-T06 (scenario contrast), TD-T08 (temporal contrast) and
   TD-T18 (recommendation) have no exact QA type. The nearest type is recorded
   with a note for the mentor.
