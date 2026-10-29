# Pilot P1 --- item schema v2, NCA regions, table-pattern extractor, literature-statement agent

Authorized by the GUIDANCE re-anchor ruling of 2026-10-29
([`docs/BENCHMARK_REANCHOR_GUIDANCE_RULING.md`](../../docs/BENCHMARK_REANCHOR_GUIDANCE_RULING.md);
**D-041**, PASS WITH ACTIONS) and D-035--D-040; one owner decision taken during
the package is recorded as **D-042**. **No model call. No item generated. No QA
accepted.** No column status, concept-map entry or compatibility rule changed.
Fields 1--9.

## 1. Milestone ID and title

**Pilot P1 --- infrastructure for the ~10-item closed-book pilot:** item schema
v2 and its validator, the NCA5 state → region map, the deterministic
table-pattern extractor, and the literature-statement agent (built, not run). M1
remains open (D-014). The pilot items themselves are P2.

## 2. Objective

(A) Bookkeeping: track the ruling; log D-041; attach the four rejected example
ids to D-036; commit the two stray run records; map *What ENSURE Is Doing* →
`system_task`. (B) Item schema v2 with the ruling's guardrails, a validator and
a leakage check. (C) A cited, pinned NCA5 state → region map. (D) Deterministic
table patterns at state / NCA-region level with direction, value/range, rank,
guarded relative terciles, support, robustness and full provenance; seasonal and
regional contrasts; a generated doc. (E) A literature-statement agent derived
from Track C agent v2, tested against a mock server. (F) Docs, state, this report.
**Excluded:** any model call, generating items, column-status / concept-map /
compatibility changes, merging, pushing.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/meeting-2026-10-22`, from head `98c2ab5` |
| Phase A commit | `ebd6c33`: the ruling, `KNOWLEDGE_FILES`, D-041, D-042, the D-036 id note, the two stray run records |
| **Build commit** | **`8f06d2b`**: schema, map, manifest pins, modules, scripts, tests, generated outputs and doc |
| **Evidence run** | `scripts/extract_table_patterns.py` at `8f06d2b`, **`git_dirty: false`, 0 untracked**: `reports/runs/20261029T221115Z_local_extract_table_patterns.{json,md}`. No tracked file changed: the committed outputs are byte-identical |
| Report commit | the commit carrying this report, the run record, the redesign doc and `PROJECT_STATE.md` (head SHA reported to the COORDINATOR) |
| Remote | **not pushed, not merged** |

## 4. Data version and checksums

| Object | SHA-256 | Bytes | Notes |
| --- | --- | --- | --- |
| `data/raw/FullData.csv` (read) | `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e` | 296,407,423 | manifest check before the read; 62,834 rows |
| `docs/BENCHMARK_REANCHOR_GUIDANCE_RULING.md` | `b72f045376c3859d5858d51b15a04bdc892bd61dc7dd0be940e7b4f46030dc8d` | 16,249 | byte-identical to the delivered file |
| **`data/metadata/benchmark/item_schema_v2.json`** | **`765631f16eeea5dadce1d9d3458942b15d8272531a2516a08ce7210f7ec852a7`** | 10,958 | pinned in `data/manifest.json` |
| **`data/metadata/geography/nca_regions_v1.yaml`** | **`3141b12201cd5a8d25789182688e69ed3792f4fa56ca667994247c82bf949a41`** | 4,721 | pinned in `data/manifest.json`; test fails on any byte change |
| **`artifacts/benchmark/table_patterns_v1.jsonl`** | **`ed3c2154818fc363e982b17e0dcb9bb1a2d2ca25e18de97fda6d353974bbf3b0`** | 6,773,361 | **gitignored** (regenerable), pinned in the summary; 2,812 records |
| `artifacts/benchmark/table_patterns_v1_summary.json` | `fbec4c94298c9feda9c52705eba3c020ccaf36d1b08df659b30a56879f6f3b03` | 6,997 | tracked |
| `artifacts/benchmark/table_patterns_v1_examples.jsonl` | `c51707dc943443de38c44ac3123cc712910b5bad6c7a22df249d44c7767dc00c` | 26,709 | tracked; the doc's ten examples |
| `docs/TABLE_PATTERNS_V1.md` (generated) | `7b4cc46d5a7308a9c4356aea7351ed8a896a04991bc350dd49ef5473dda0b1e4` | 16,939 | test: equals a re-render |
| **`scripts/litcollect/litstatement_agent.py`** | **`42efdafd9d956fccff9697793048988b03bac85acbaad9c6e0634df0f17114d9`** | | pinned in its test; system prompt SHA-256 **`998640ac2cfb53e5f8135a14a1d86686477c45dfa30d7e664b4960967e138cc8`** |

Read and unchanged: `slots_v1.yaml` (`d40f835e…7e10`), `dictionary_coverage.json`
(`2547e8df…a4ce4`), `dictionary_extracted.txt`, `concept_map.yaml`,
`softqa_agent.py` v2 (`25a79a5b…b9c`, imported by the new agent), the P-STATE-1
v2 record, `questions_v1.jsonl` (Track D, cross-check).

## 5. Environment and execution location

| | |
| --- | --- |
| Host | local (Mac), location label `local` |
| Python | 3.11.16, conda env `climrr` |
| Model calls / retrieval runs | **0 / 0** (recorded in the run record) |
| Network | one attempted read of `nca2023.globalchange.gov` for the NCA5 regional definition: **the host did not resolve** (`getaddrinfo ENOTFOUND`); nothing was fetched |

## 6. Work completed

- **Phase A.** Ruling copied byte-identical and added to `KNOWLEDGE_FILES` and to
  PROJECT_STATE's Knowledge files (test). **D-041**: gate status, the decision
  table verbatim, conditions A--F, the standing rules, pilot authorized,
  `system_task` mapping. **D-036 note**: the four ids as given. Two of them, `C-199098498-03` and
  `C-53050065-03`, **do not exist in `softqa_run1`**: paper 199098498 has only
  -01/-02, and paper 53050065 has only -01. Flagged; nothing was substituted. The stray
  `softqa_review_view` run records of 2026-10-28 are committed.
- **Phase B --- schema v2.** Every work-package field, named exactly
  (`clmrr_named` as written), grouped as the ruling's `reference_components`. The
  validator (`benchmark_items.py`) uses the soft-QA JSON-Schema subset with local
  `$ref` resolution. Its rules go beyond the schema: the leakage check recomputes
  to the stored one; `multi_source_supported` needs ≥ 2 distinct papers;
  `review_supported` needs a support marked as a review; `single_source_supported`
  cites exactly one paper and is never consensus; spans match their passages;
  a tercile definition says "relative" and "tercile"; an accepted status needs
  both dispositions and a frozen final. `validity()` returns A--F. **Leakage
  check:** ClimRR (any spelling); column names as whole words (names from the
  coverage report, whose data hash is the manifest's; the manifest itself has
  no names); generic `NAME` / `State` / `X` / `Y` are not checked; cell ids
  `R…C…`; corpus ids `LIT-` / `LIT2-`; proxies "et al." and a year in
  parentheses, flagged `review:`; decimals and percentages; "according to" /
  "this table / dataset / paper / study". All 2,812 extracted patterns
  validate against `$defs/table_pattern`.
- **Phase C --- NCA5 map.** 10 regions (NCA5 chapters 21--30), 50 states + DC each
  in exactly one region, **written from the EXECUTOR's knowledge** because the
  NCA5 site did not resolve; marked **`source_verification: pending_kaiyuan`**.
  The file names the exact artifact to check (each regional chapter's opening or
  the Front Matter regional map, doi:10.7930/NCA5.2023) and the border states
  to look at. It was pinned in the manifest **before** any pattern was computed.
  The table's 49 State labels all map; **DC and Hawaii are not in the table**;
  the Hawai'i/USAPI and U.S. Caribbean regions have no coverage.
- **Phase D --- extractor.** Reuses Track D's slots, metrics, state list, control
  cell and arithmetic (DR-TD-003/004/005). New rules DR-PT-001..008 (field 8).
  One pass over the table (≈5 s). Families: heat index, the four verified
  thresholds (DayMax is `inferred_candidate`, not used); FWI summer value
  (`inferred_candidate`, every pattern `acceptance_blocked`); FWI per-cell
  percent-change Pmid/Pend for four seasons (verified; `scenario:
  unstated_in_dictionary`). Horizons mid/end; RCP8.5 where stated. **Cross-checks:**
  California, 105 °F, end-century, absolute change = `13.209951652865228` =
  frozen P-STATE-1; **all 1,094 computable state-level Track D answers**
  (heat index, historical baseline, three statistics) are reproduced exactly
  (test, against the hash-pinned `questions_v1.jsonl`).
- **Phase E --- statement agent.** `litstatement_agent.py` takes the endpoint call,
  the reasoning-field fallback and the exact → normalized → prefix_anchor
  locator **by import** from pinned `softqa_agent.py` v2, so it is the same code.
  The new system prompt is stored verbatim and its hash is recorded. No units input. Pre-check: re-slice
  with recovery recorded; ≤ 700 chars; `background` rejected; no digit-heavy
  statement unless `specific_result` (years, RCP/SSP/CMIP names and ordinals
  excepted; a single threshold number allowed); `elsewhere_in_paper`
  scenario/time quotes must re-slice exactly or become `unsupported`; enums and
  completeness. Statements past eight are recorded and flagged. Restartable;
  `result.json` per paper, `statements.jsonl`, `summary.json`, `agent.log`. 19
  mock-server tests. The Polaris invocation is in `src/climrr/litstatements.py`.
  The ALCF credential variable name is assembled from fragments, so the
  secrets scan needs no new exemption. `CLAUDE.md` lists the agent's run evidence.
- **Phase F.** Redesign doc §2 → schema v2, §6 annotated with what the ruling
  answered; PROJECT_STATE; this report.

## 7. Deliverables and exact file paths

- `docs/BENCHMARK_REANCHOR_GUIDANCE_RULING.md`; `docs/DECISION_LOG.md` (D-036 note, D-041, D-042)
- `data/metadata/benchmark/item_schema_v2.json`; `src/climrr/benchmark_items.py`
- `data/metadata/geography/nca_regions_v1.yaml`; `data/manifest.json` (two entries, one amendment); `.gitattributes`
- `src/climrr/table_patterns.py`; `scripts/extract_table_patterns.py`;
  `artifacts/benchmark/table_patterns_v1_summary.json`, `…_examples.jsonl`
  (`table_patterns_v1.jsonl` gitignored, pinned); `docs/TABLE_PATTERNS_V1.md`
- `scripts/litcollect/litstatement_agent.py`; `src/climrr/litstatements.py`
- Tests: `tests/test_benchmark_items.py`, `tests/test_nca_regions.py`,
  `tests/test_table_patterns.py`, `tests/test_litstatement_agent.py`,
  `tests/test_stage_knowledge.py` (one test added)
- `scripts/stage_knowledge.py`, `CLAUDE.md`, `.gitignore`,
  `docs/BENCHMARK_REDESIGN_2026-10-29.md`, `docs/PROJECT_STATE.md`
- Run records: `reports/runs/20261029T221115Z_local_extract_table_patterns.{json,md}`;
  `reports/runs/20261028T042658Z_local_softqa_review_view.{json,md}`

## 8. Methods and rules that affect scientific meaning

| Rule | What it does |
| --- | --- |
| DR-TD-003 / 004 / 005 (Track D, reused) | absolute change = mean of per-cell change (FWI summer: the Dmid/Dend column; heat index: future − historical); percent change = 100 × mean change / mean baseline (zero baseline → `not_computable`); direction = sign of mean change |
| **DR-PT-001** state | unweighted mean over the rows sharing a State label (IC-012, provisional; D-034); empty cells skipped and counted |
| **DR-PT-002** NCA region | unweighted mean over **every cell** in the region's covered states (a state with more cells weighs more); range = min--max of member states' values |
| **DR-PT-003** robustness | share of member units (cells for a state, states for a region) whose own direction equals the aggregate's: all → `all_states_same_direction`, > ½ → `majority_same_direction`, else `mixed`. The enum names states; `robustness_unit` says which unit was counted |
| **DR-PT-004** rank | descending signed value within geography type; competition ranking |
| **DR-PT-005** relative tercile | states only, by signed value; bottom ⌊n/3⌋ `small`, top ⌊n/3⌋ `large`; skipped for population < 15, < 3 distinct values, a tie at a cut, or **any** missing state. Missing states at either end always shift the cut by position, so "missing states change cut points" is read as "any missing". The definition string says relative / not an absolute threshold |
| **DR-PT-006** percent-change columns | **no central value** (D-042; M1-WP3b): majority sign of cells, sign counts, cell min--max |
| **DR-PT-007 / 008** contrasts | seasonal: per-season majority direction and share of cells increasing (no largest-change season); regional: covered regions ordered by DR-PT-004, or listed by majority direction |
| Geography | regions from the pinned NCA5 map; no `multi_state_set` defined in v1 |

Not applied: no unit conversion, no column renamed or reinterpreted, no
weighting alternative. The ruling's "weighting choices materially change the
grouping" guard is **not tested**: one rule per geography. That is a limitation.

## 9. Results with compact tables or examples

**Counts.** 2,812 patterns: 2,668 single, 116 seasonal contrasts, 28 regional
contrasts. Computed 2,720; `not_computable` 92, all zero baselines for heat-index
percent change. `verified` 2,460; `inferred_candidate` 352, all
`acceptance_blocked` (FWI summer value).

| Family | Geography | direction | absolute_change | percent_change | seasonal_contrast |
| --- | --- | --- | --- | --- | --- |
| heat_index | nca_region | 64 | 72 | 72 | --- |
| heat_index | state | 392 | 392 | 392 | --- |
| heat_index | cell_control | 8 | 8 | 8 | --- |
| fire_weather_index | nca_region | 88 | 18 | 82 | 16 |
| fire_weather_index | state | 490 | 98 | 490 | 98 |
| fire_weather_index | cell_control | 10 | 2 | 10 | 2 |

(NCA-region counts include the 28 regional-contrast records. FWI
`percent_change` covers the summer value's ratio of means and the
percent-change columns' range-only records.)

**Terciles.** 686 state patterns carry one. Of the 20 ranked state groups,
6 skipped it, all for **`missing_states_change_cut_points`**: heat-index
`percent_change` at 105 / 115 / 125 °F for both horizons, with 4 / 18 / 19 states
having a zero baseline. Never applied to regions (population under 15), to
`direction`, or to the percent-change columns (no central value).

**Ten example patterns** (first by id; heat index, days above 95 °F, summer,
mid-century 2045--2054, RCP8.5, `direction`):

| Id | Geography | Direction | Mean change (days) | Range | Support | Robustness |
| --- | --- | --- | --- | --- | --- | --- |
| TP1-00001 | NCA5-AK Alaska | increase | 0.0085 | cells −0.033 .. 0.533 | 1 state | all 1/1 |
| TP1-00002 | NCA5-MW Midwest | increase | 9.04 | cells 0 .. 23.27 | 8 states | all 8/8 |
| TP1-00003 | NCA5-NE Northeast | increase | 3.19 | cells 0 .. 19.07 | 12 states | all 12/12 |
| TP1-00004 | NCA5-NGP N. Great Plains | increase | 7.28 | cells 0 .. 21.03 | 5 states | all 5/5 |
| TP1-00005 | NCA5-NW Northwest | increase | 2.74 | cells −0.067 .. 16.90 | 3 states | all 3/3 |
| TP1-00006 | NCA5-SE Southeast | increase | 26.97 | cells 0 .. 50.50 | 11 states | all 11/11 |
| TP1-00007 | NCA5-SGP S. Great Plains | increase | 25.32 | cells 0.233 .. 48.90 | 3 states | all 3/3 |
| TP1-00008 | NCA5-SW Southwest | increase | 7.12 | cells 0 .. 34.33 | 6 states | all 6/6 |
| TP1-00009 | state Alabama | increase | 28.79 | cells 11.10 .. 43.53 | 934 cells | all 934/934 |
| TP1-00010 | state Alaska | increase | 0.0085 | cells −0.033 .. 0.533 | 10,097 cells | **mixed** 1,211/10,097 |

TP1-00010 shows why robustness is stored. Alaska's mean is a positive 0.0085
days, so DR-TD-005 calls it an increase, but most cells do not change. A
reference answer must not call that an increase without the robustness. Full
provenance for each example is in `docs/TABLE_PATTERNS_V1.md`.

**Regional contrast example** (heat index, > 105 °F, end-century, absolute
change, days): S. Great Plains 43.37 > Southeast 41.01 > Midwest 14.50 >
Southwest 6.48 > N. Great Plains 6.33 > Northeast 3.91 > Northwest 1.90 >
Alaska 0.001.

**Validation.** `pytest`: **1,231 tests collected; 1,229 passed, 2 skipped** (the
two pre-existing skips); the four new test files and `test_stage_knowledge.py` hold
98 of them. Secrets
and paths scan: **0 hits**.

**Escalations.** (1) **NCA map source verification**: Kaiyuan, against the
artifact named in the file. (2) **D-042** needs COORDINATOR / GUIDANCE
confirmation. (3) Two rejected-example ids are not in `softqa_run1`. (4) The
robustness enum names states but is also used with cells as the unit (DR-PT-003).
(5) The tercile weighting guard is not tested (field 8).
