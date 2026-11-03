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

---

# Pilot P2a --- literature-statement run 2, cross-paper aggregation, item seeds

Authorized by D-041 (pilot of ~10 items) and D-036 / D-039 (statements aggregated
across papers; single source only if labelled). Decisions taken in the package:
**D-044** (run 2 is the pilot's literature-statement evidence) and **D-045**
(aggregation and seeding rules v1; the aggregation rule revised by the COORDINATOR
ruling of 2026-11-01 after the first rule degenerated). **No model call. No item
generated. Nothing accepted.** No column status, concept-map entry or compatibility
rule changed. Fields 10--15.

## 10. Commits and evidence runs

| | |
| --- | --- |
| Branch | `work/meeting-2026-10-22`, from head `7919bbf` |
| **Build commit** | **`feac646`**: modules, scripts, tests, lexicons, the ingested run, clusters, seed summary, SEEDS CSV, doc, D-044, D-045, state |
| **Evidence runs** | at `feac646`, **`git_dirty: false`** (untracked = the preceding records of the same sequence): `reports/runs/20261101T184947Z_local_ingest_litstatements`, `…184949Z_local_aggregate_litstatements`, `…184950Z_local_build_item_seeds`, `…184951Z_local_build_p2a_review` (`.json` / `.md`). Every tracked output byte-identical; the gitignored seeds file and workbook too |
| Report commit | the commit carrying this section, the run records and `PROJECT_STATE.md` |
| Remote | **not pushed, not merged** |

## 11. Data and checksums

| Object | SHA-256 | Notes |
| --- | --- | --- |
| `litstatements_run2_evidence.tar.gz` (read, outside the repo) | `7d9077392ceb961035790a9dc3c89d9a825aabe56bca5ce0184ad674b9ffc414` | equals the work package |
| run-2 `statements.jsonl` / `summary.json` | `26ba676c…2a15f` / `4da75e2d…a9cf9a78` | equal the work package; `statements.jsonl` re-derived from the 243 `result.json` |
| **`artifacts/litstatements/run2/manifest.json`** | **`6ff23183444ffdde86d5d012fa38c1d2a5a0c49392c5602af35fd49f9dd01f77`** | every ingested file's SHA-256; 486 excluded files hashed |
| `statements_ingested.jsonl` | `b775301cbd3387f2228f07830fded009d9111d0ce635624123bc45a9f458eb81` | 1,018 records, ids `LS-<item_id>-<nn>`, evidence roles |
| **`clusters_v1.jsonl`** | **`11bc074c6ef0a04a953e18e90febc1cfaef2d6bb9b9b7ebb5cfb7b79dfed556a`** | 731 clusters |
| `clusters_v1_summary.json` | `cf5c7cea1a880c44ec194749a4742a74bf65456a19c71516f757431e4d039e7a` | |
| `direction_lexicon_v1.yaml` / `stopwords_v1.yaml` | `745526dc9f6e8ea4397192a390efc2a394524a25cdcc4dd461143989be0235fd` / `dfbe6668d7d8c918e5827faac6562881ddb4284583b487ccdfa3e88d9b5bfb99` | hand-written |
| `concept_lexicon_v1.yaml` / `df_filter_dropped_v1.yaml` | `c131fb56543eb9e5ca9854ae93e8eb09daad4c7eca239f416d70169917318963` / `e0e89fa270edc7c2628fbc5d8886c7bad5cfd3b66f7db89f364bb70d1796d469` | generated; test re-derives |
| **`item_seeds_v1.jsonl`** | **`3764eba645c84008453678b236e610a7ee2dff105404946c92e90ae3093beb32`** | **gitignored** (58 MB), pinned in `item_seeds_v1_summary.json` (`c274c66022abfcfb3fc3e6a7210e6a25ce1340955e2258d95de579e70413ce53`) |
| `P2a_seeds_v1.csv` (tracked) / workbook (gitignored) | `a4adae65c2ab7f55fed79d61ad10830b900599d6e433afe61977fa277f898055` / `503cb32cb75e60c2d2eae01e8a932775631ee9f2e5357ee64b7850266a0ec096` | |
| `docs/LITSTATEMENTS_RUN2.md` (generated) | `7061075af0024545cf8a9569627565f0f4ef87f45e48af203eca866e59fa34dc` | test: equals a re-render |
| **`litstatement_agent.py` v3** | **`fd0e1dc391d46c691ab3b0b0d0190ba009f47a6e69e0eb6f0ececec441b6a9ea`** | pinned in its test; system prompt unchanged `fbedadd2…cb01fff`; **not run** |

Read and unchanged: `table_patterns_v1.jsonl` (`ed3c2154…f3b0`), `nca_regions_v1.yaml`
(`3141b122…9a41`), `softqa_agent.py` v2.

## 12. Work completed

- **Phase A --- ingest.** Every run-2 fact the work package states reproduced from the
  files (243 papers; 1,018 statements; 485 / 533; the five per-check counts; 0 errors;
  endpoint on all 243; agent and prompt hashes; source commit; both logs identical).
  Copied byte-identical; `prompt_user.txt` / `response.json` hashed, not copied.
  Roles: **core 379, cited 106, background-consensus 262, unusable 271.** Run 1 recorded
  as superseded (6 paper directories: 2 with statements, 3 HTTP errors, 1 prompt only).
  Independence metadata: the corpus index has **no author, year or venue field**.
- **Phase B --- aggregation.** The work package's rule degenerated (54 clusters at
  every threshold, largest 114); the EXECUTOR stopped and escalated; **DR-LIT-AGG-1 v2**
  implemented per the COORDINATOR ruling.
- **Phase C --- seeds.** DR-SEED-1 over all 2,812 patterns; geography-match audit.
- **Phase D --- review.** Workbook (OVERVIEW, SEEDS 1,316 rows, CLUSTERS 27, STATEMENTS
  1,018, PARSE_ERRORS 21, Legend) written by a stdlib writer (`src/climrr/xlsxlite.py`;
  no dependency added; checked to open in openpyxl outside the project environment).
- **Phase E --- agent v3.** `raw_response`, `raw_reasoning` (fallback only),
  lengths, `content_fallback`, `finish_reason` in every `result.json`; 3 new tests.
- **Phase F.** D-044, D-045, the generated doc, `KNOWLEDGE_FILES`, state, this section.

## 13. Methods and rules that affect scientific meaning

| Rule | What it does |
| --- | --- |
| Evidence roles (D-044) | core = pass + own_finding / own_projection / review_synthesis; cited = pass + cited_finding; background-consensus = rejected only for a background passage that re-sliced; else unusable |
| **DR-LIT-IND-1** | distinct ids + no shared author surname/initial; authors absent -> `assumed_independent_distinct_ids`. Equal-hash / equal-title pairs recorded as diagnostics, not used |
| **DR-LIT-AGG-1 v2** | arm x type x lexical direction; unigrams + bigrams; per-arm DF filter > 15 %; IDF cosine; union-find at 0.30; no lexicon merge |
| Evidence strength | multi (>= 2 independent papers with core/cited) > review (review_synthesis member) > single (one core/cited paper) > background_only |
| **DR-SEED-1** | family and direction (or `unspecified`) match; geography relevant by place name, U.S. term, or global/national scope; rank by strength, relevance, independent papers; eligible = not blocked + >= 1 relevant multi-source mechanism/driver cluster |

EXECUTOR choices inside these rules (listed in D-045 for confirmation): inflected
direction forms, both-lists -> `unspecified`; representative by cosine (the work
package said Jaccard); periods removed before place matching; rank tie-breaks;
`use_case_level` precedence 4 > 3 > 7 > 1; `not_computable` patterns not eligible; the
seed order.

## 14. Results

**Clusters (v2, cosine 0.30).** 747 statements enter; **731 clusters, 721 singletons**:
multi-source **3**, review 24, single 455, background-only 249. Multi-source:
`LC-extreme_heat_v1-driver-006` (heat index and acute kidney injury; Florida),
`LC-extreme_heat_v1-consensus-010` (Daymet represents station heat index; two cited
findings), `LC-extreme_heat_v1-driver-071` (Malaysian pan evaporation --- **the two
papers are one byte-identical file**). No FWI cluster is multi-source.

| measure | 0.20 | 0.25 | **0.30** | 0.35 | 0.40 | 0.50 |
| --- | --- | --- | --- | --- | --- | --- |
| cosine: clusters / singletons / multi / largest | 699 / 674 / 10 / 17 | 722 / 712 / 3 / 14 | 731 / 721 / 3 / 6 | 735 / 725 / 2 / 4 | 737 / 729 / 2 / 4 | 744 / 741 / 1 / 2 |
| jaccard: clusters / singletons / multi / largest | 706 / 690 / 6 / 20 | 721 / 708 / 3 / 13 | 733 / 723 / 2 / 4 | 737 / 729 / 2 / 4 | 741 / 736 / 2 / 3 | 745 / 743 / 1 / 2 |

No cluster exceeds 25 statements at any threshold. Arm x type x strength and the ten
largest clusters: `docs/LITSTATEMENTS_RUN2.md` §4.

**Seeds.** 2,812 (heat 1,408, FWI 1,404). Levels (first that applies): 3: 2,784; 4: 28.
**Eligible under DR-SEED-1 as written: 1,316** (all heat index; 1,300 level 3, 16 level 4)
--- but **1,292 only through `driver-071`**, relevant to every heat pattern by its
"national" (Malaysia) scope; **24 eligible without it** (the Florida state heat-index
patterns, through `driver-006`). FWI: 352 acceptance-blocked, 1,052 not blocked, **0
eligible** (no multi-source FWI cluster). 92 `not_computable` patterns kept out. The
ten highest-ranked eligible seeds are all Florida heat-index patterns (`TP1-00017`,
`-00075`, `-00133`, `-00191`, `-00249`, `-00307`, `-00365`, `-00423`, `-00481`,
`-00539`), each with the same three clusters; listed in full in the doc §5.

**Parse errors.** 21, all `finish_reason: length` at 3,500 completion tokens.

**Validation.** `pytest`: **1,319 tests collected; 1,317 passed, 2 skipped** (the two
pre-existing skips); new or changed test files: `test_litstatements_run2.py` (23),
`test_litaggregate.py` (34), `test_itemseeds.py` (18), `test_litstatement_agent.py`
(32). Secrets and paths scan: **0 hits**.

## 15. Escalations and limitations

1. **First aggregation rule degenerate** --- resolved by the COORDINATOR ruling
   (DR-LIT-AGG-1 v2), logged in D-045 and the doc.
2. **Duplicate paper counted as two independent sources** (239052352 = 257056592,
   byte-identical): DR-LIT-IND-1 as written calls them independent; the cluster it makes
   multi-source supplies 1,292 of the 1,316 eligible seeds. **For the COORDINATOR.**
3. **Non-U.S. national scope is U.S.-relevant** under DR-SEED-1 (191 clusters are relevant
   only by scope); name matching has no gazetteer ("Sierra Nevada" -> Nevada, "Brazil and
   Southeast Asia" -> Southeast). **For the COORDINATOR.**
4. **The eligible clusters are weak for the ladder**: a health-outcome association, a
   dataset-validation statement (two cited findings, possibly one cited study), the
   duplicate. With fewer than 10 sound multi-source seeds, the pilot will need
   single-source clusters labelled as such (GUIDANCE ruling) or P2b semantic merges.
5. **Parse errors** are truncations at the `--max-tokens` cap; a re-run would need a larger cap
   (not authorized, D-044). The work package's limitation "no raw text for
   parse errors" holds for `result.json` only: `response.json` has it.
6. Some extreme-heat statements concern the Thornthwaite heat index (a PET parameter),
   not humid heat; lexical rules cannot separate them.

---

# Pilot P2b --- literature grouping (run 2 ingest), synthesis packets, groups review

Authorized by D-041, D-048--D-051; decision taken in the package: **D-052** (run 2 is the pilot's literature
grouping). **No model call in this package. No item generated. Nothing accepted.** No column status, concept-map
entry or compatibility rule changed. Design: [`docs/PILOT_P2B_DESIGN.md`](../../docs/PILOT_P2B_DESIGN.md) section 10.
Fields 16--19.

## 16. Commits and evidence runs

| | |
| --- | --- |
| Branch | `work/meeting-2026-10-22`, from head `7676e53` |
| **Build commit** | **`7a8b46b`**: modules, scripts, tests, the ingested run, enriched groups, packets, GROUPS CSV, D-052, design section 10, this section, state |
| **Evidence runs** | at `7a8b46b`, **`git_dirty: false`**: `reports/runs/20261102T180915Z_local_ingest_litgroups`, `…180916Z_local_build_synth_packets`, `…180916Z_local_build_p2b_groups_review` (`.json` / `.md`). Every tracked output byte-identical; the gitignored workbook too (`a5395e11…c3ff`) |
| Report commit | the commit carrying the run records and this table |
| Remote | **pushed** (the Eagle clone must fetch the packets); not merged |

## 17. Data and checksums

| Object | SHA-256 | Notes |
| --- | --- | --- |
| `litgroups_run2_evidence.tar.gz` (read, outside the repo) | `a90ad7f011424db37082ea692b1987c9a7697d399ef20c1737afa8535374e2eb` | equals the work package |
| run-2 `groups.jsonl` / `summary.json` | `fc5ceea5…b4ce` / `0253c687…c5` | equal the work package; `groups.jsonl` re-derived from the 23 chunk results |
| `litgroup_agent.py` v3 | `e094aa5c…d845f4` | equal at `7676e53` and at the build commit |
| **`artifacts/litgroups/run2/manifest.json`** | **`36931849a2de42d9931bbd491b2fc95ba0c71ba9ac0b3b0aa42be54b0bda80d0`** | 31 ingested files, 2 derived, 76 excluded (hashed) |
| `groups_enriched.jsonl` / summary | `924a7b0d…a70a` / `a7d48b97…1d` | 394 records |
| **`artifacts/benchmark/synth_packets/manifest.json`** | **`80af2d0dbe3c9601f06246c621d430ae4c7b1f7e4318fbecdec8e7d5558611c1`** | ten packets with their SHA-256 |
| `P2b_groups_v1.csv` (tracked) | `0c635250c127fb0de36d5abb85ce1f616bfeff889f44cd0c86b7b0b384e24084` | the GROUPS sheet |

## 18. Results

**Run 2.** 11 partitions, 23 chunks, **23 pass**, all `finish_reason=stop`; 15 corrective turns (12 passed on the
first invocation; `extreme_heat_v1.driver.c1`, `.driver.c2`, `fire_weather_v1.mechanism.c2` passed on a second attempt,
same configuration); **239 groups, 155 singletons, 747 statements once**; 0 label-digit and 0 `claim_about` fails.
105 of the 239 groups have one member.

**Groups by arm x claim_about** (multi / review / single / background):

| arm | hazard_change_mechanism | hazard_definition_or_measurement | impact_or_exposure | method_or_data | other |
| --- | --- | --- | --- | --- | --- |
| extreme heat | 15 / 0 / 17 / 4 | 6 / 1 / 15 / 9 | 15 / 3 / 32 / 3 | 8 / 2 / 10 / 5 | 0 / 1 / 3 / 2 |
| fire weather | 20 / 0 / 22 / 3 | 10 / 0 / 9 / 7 | 1 / 0 / 3 / 0 | 4 / 0 / 7 / 2 | --- |

**Packets** (DR-SEED-RANK-2; driver / context / caveat; multi-source among them; excluded):

| item | seed | rung | groups | multi | excluded |
| --- | --- | --- | --- | --- | --- |
| BI-P2B-0001 | SD2-TP1-00018 | 1 | 0 / 0 / 0 | 0 | 0 |
| BI-P2B-0002 | SD2-TP1-00069 | 1 | 0 / 0 / 0 | 0 | 0 |
| BI-P2B-0003 | SD2-TP1-00071 | 3 | 10 / 4 / 0 | 5 | 47 |
| BI-P2B-0004 | SD2-TP1-00271 | 3 | 10 / 4 / 0 | 4 | 41 |
| BI-P2B-0005 | SD2-TP1-00460 | 3 | 10 / 4 / 0 | 4 | 44 |
| BI-P2B-0006 | SD2-TP1-00589 | 3 | 10 / 4 / 0 | 4 | 43 |
| BI-P2B-0007 | SD2-TP1-02785 | 4 | 10 / 4 / 0 | 4 | 40 |
| BI-P2B-0008 | SD2-TP1-02787 | 4 | 10 / 4 / 0 | 4 | 40 |
| BI-P2B-0009 | SD2-TP1-02789 | 4 | 10 / 4 / 0 | 4 | 40 |
| BI-P2B-0010 | SD2-TP1-00075 | 7 | 10 / 4 / 4 | 4 | 40 |

**Validation.** `pytest`: **1,447 passed, 2 skipped** (the two pre-existing skips); new test file
`tests/test_litgroups_run2.py` (7). Secrets and paths scan: **0 hits**.

## 19. Escalations and limitations

1. **Claim tags in the heat packets.** Fire statements from the heat arm tagged `hazard_change_mechanism` lead the
   drivers of heat-index packets ("Prolonged heat increases fire or wildfire risk"; a Rocky Mountains large-fire
   experiment; "drought and high temperatures increase wildfire risk"). The tag is the agent's (D-049); the human check
   decides. **For Kaiyuan before or alongside the synthesis run.**
2. **Relevance before strength** (DR-SEED-RANK-2): single-source `us_subregion` statements rank above national
   multi-source groups for Northeast and Southeast patterns (P2b-fix open point d).
3. **Little variation across seeds**: packets 0004--0010 carry nearly the same driver groups.
4. **105 one-member labelled groups**; no cross-chunk merging by code (D-051, D-052).
5. **Packet file names** stay `PK-<seed_id>.json` (the pinned synthesis agent reads them); item ids `BI-P2B-<nnnn>`
   are in the packets and the manifest.

# Pilot P2b-ingest-items --- synthesis runs 0--2, the ten pilot items, review workbook, rung-7 packet fix

Authorized by D-041 and the COORDINATOR work package P2b-ingest-items; decisions taken in the package: **D-056**
(synthesis run 2 is the pilot item set) and **D-054a** (DR-SEED-RANK-3a). **No model call in this package. Ten items
exist, all in `human_review`; nothing accepted.** No column status, concept-map entry or compatibility rule changed.
Design: [`docs/PILOT_P2B_DESIGN.md`](../../docs/PILOT_P2B_DESIGN.md) section 14. Fields 20--25 (the template's fields
10--15 for this package).

## 20. Commits and evidence runs

| | |
| --- | --- |
| Branch | `work/meeting-2026-10-22`, from head `1f175da` |
| **Build commit** | **`6ca9a93`**: modules, scripts, tests, the ingested run, lint report, ITEMS CSV, COORDINATOR notes, packets v3b, D-056, D-054a, design section 14, this section, state, mentor brief |
| **Evidence runs** | at `6ca9a93`, **`git_dirty: false`**: `reports/runs/20261103T005753Z_local_ingest_litsynth`, `…005754Z_local_lint_item_rubrics`, `…005754Z_local_build_p2b_items_review`, `…005755Z_local_build_synth_packets` (`.json` / `.md`). Every tracked output byte-identical (`changed_packets: []`); the gitignored workbook too (`b329f9ef…08b8`) |
| Report commit | the commit carrying the run records and the filled SHAs |
| Remote | **pushed** (the Eagle clone needs packets v3b for run 3); not merged |

## 21. Data and checksums

| Object | SHA-256 | Notes |
| --- | --- | --- |
| `litsynth_runs012_evidence.tar.gz` (read, outside the repo) | `00c909340bd08d61331e1eb6515da0b2bf375627b63d7491456c740949ebaac1` | equals the work package |
| run-2 `items.jsonl` / `summary.json` | `b0e0c60f…308bb8` / `89083141…89b0cc` | equal the work package; `items.jsonl` = the ten per-item files |
| `litsynth_agent.py` v3.2 | `f5778fbf…4b8b5e` | equal at `1f175da` and at the build commit; system prompt `9c79f452…5715`, format-corrective template `919f52cb…6d20` |
| packets v3a (what run 2 read) | manifest `86b02cd0…b84c` | read from Git at `1f175da`; every item's packet SHA-256 equal |
| **`artifacts/benchmark/items/run2/manifest.json`** | **`c9c6bc9bc1a4f19d94e7a5e9c9514c34c9a3ad18b60dc97a11b87df2b84d60e9`** | 8 copied files, 10 ingested items, 32 excluded (hashed) |
| `rubric_lint_v1.json` | `5b5cf722f54ad8bc7f790a6591f467f69c3cb963e6d26cec9529835e1d7d8d31` | report only |
| `P2b_items_review_v1.csv` (tracked) | `ebcb856b21eddf02e69a2d51a32d689fe2988b1ea77130abfffc47c4c505eb73` | the ITEMS sheet |
| `P2b_items_coordinator_notes_v1.csv` | `1f4f72c39af8b73ed926dfe889c1784a6229afb11e7f7f7bca0e814ee1e849ea` | byte-identical copy of the delivered notes |
| **packets v3b `manifest.json`** | **`09ca030a5e4de913b1a6efb29943c84754de796a4a3987f300e72083e7f172c7`** | `PK-SD2-TP1-00075.json` `9ec338d6…79ee`; nine packets byte-identical to v3a |

## 22. Work completed

Phase A: run 2 verified and ingested; post-checks v2.2 reproduced; the ten items moved to `human_review`. Phase B: rubric
lint v1 (report only). Phase C: item review workbook and ITEMS CSV with the COORDINATOR notes. Phase D: DR-SEED-RANK-3a
and the rung-7 packet instruction; packets v3b. Phase E: D-056, D-054a, design section 14, state, mentor brief, this
section.

## 23. Methods and rules that affect scientific meaning

- **D-056**: the ten items are the pilot set; edits are human and go to `review.final_frozen`; the agent is frozen at
  v3.2. The lifecycle step changes `review.status` and appends one history event; nothing in the item's content changes.
- **D-054a** (DR-SEED-RANK-3a): at rung 7 the caveat slots take scenario-naming groups of any type first. EXECUTOR readings
  for confirmation: matched over the members the packet carries; the group takes a caveat slot instead of a driver slot;
  carried as `statement_type: caveat` because schema v2 has no `pattern` literature type (D-054a, recorded).
- **Rubric lint v1**: five rules (D-056 implementation); flags are a checklist, not edits.

## 24. Results

**The ten pilot items** (all `deterministic_pass` in run 2, now `human_review`; heat index, summer, RCP8.5):

| item | seed | rung | place | quantity | horizon | literature sentences | format turn | lint flags | COORDINATOR | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BI-P2B-0001 | SD2-TP1-00018 | 1 | Georgia | days > 95 °F | mid | 0 | yes | 2 | accept_with_edits | human_review |
| BI-P2B-0002 | SD2-TP1-00069 | 1 | Arizona | days > 95 °F | mid | 0 | yes | 3 | accept_with_edits | human_review |
| BI-P2B-0003 | SD2-TP1-00071 | 3 | California | days > 95 °F | mid | 3 | no | 2 | accept_with_edits | human_review |
| BI-P2B-0004 | SD2-TP1-00271 | 3 | New York | days > 95 °F | end | 2 | no | 4 | accept_with_edits | human_review |
| BI-P2B-0005 | SD2-TP1-00460 | 3 | Washington | days > 105 °F | mid | 1 | no | 2 | accept_with_edits | human_review |
| BI-P2B-0006 | SD2-TP1-00589 | 3 | Alabama | days > 105 °F | end | 4 | yes | 2 | accept_with_edits | human_review |
| BI-P2B-0007 | SD2-TP1-02785 | 4 | NCA5 regions | days > 95 °F | mid | 3 | no | 1 | accept_with_edits | human_review |
| BI-P2B-0008 | SD2-TP1-02787 | 4 | NCA5 regions | days > 95 °F | end | 2 | yes | 7 | accept_with_edits | human_review |
| BI-P2B-0009 | SD2-TP1-02789 | 4 | NCA5 regions | days > 105 °F | mid | 2 | yes | 1 | accept_with_edits | human_review |
| BI-P2B-0010 | SD2-TP1-00075 | 7 | Florida | days > 95 °F | mid | 4 | yes | 1 | **regenerate** (run 3) | human_review |

**Lint totals:** generation_constraint 16, hedge_strength_mismatch 6, required_single_source_only 1, rung1_prompt_mechanism
1, required_tercile 1 (25). **Rung-7 packet v3b caveat slots:** `LG-extreme_heat_v1-pattern-c2-003` (single-source in the
packet), `…-caveat-c1-026` (review), `…-caveat-c1-024` (single).

**Validation.** `pytest`: **1,498 passed, 2 skipped** (the two pre-existing skips); new `tests/test_litsynth_run2.py` (8),
three new tests in `tests/test_synthpackets.py`, one in `tests/test_litsynth_agent.py`; v3a pins in
`tests/test_litgroups_run2.py` and `tests/test_litsynth_agent.py` moved to v3b. Secrets and paths scan: **0 hits**.

## 25. Escalations and limitations

1. **0010 is not yet a rung-7 item**: run 3 (one packet, v3b) is needed; its prompt and reference depend on the model
   using the scenario caveat, which is single-source in this packet (one paper) and must be hedged.
2. **Workbook vocabulary vs schema v2**: accept_with_edits / regenerate are not schema dispositions; mapping deferred.
3. **Lint coverage**: the literal generation-constraint pattern misses two 0007 lines; the COORDINATOR notes carry them.
4. **Hedging**: six literature sentences hedge multi-source groups as "one study" (0003, 0004, 0006, 0008); the
   COORDINATOR notes accept one of them (0004, `…-driver-c1-008`).
5. **Two HTTP retries** in run 2, not one; both recovered on the second attempt.
6. FWI column confirmation remains open (no FWI item in the pilot).

# Mentor export --- synthesis run 3, items index, post-checks v2.3, lint v1a, workbook v2, mentor sheet

COORDINATOR work package "Mentor review export: five pilot items" (2026-11-03). **No model call. No item accepted,
nothing frozen**; the COORDINATOR texts are recorded as proposals for Kaiyuan. No new decision: run 3 is the
regeneration D-056 / D-054a set up. Fields 26--31.

## 26. Commits and evidence runs

| | |
| --- | --- |
| Branch | `work/meeting-2026-10-22`, from head `157c96c` |
| **Build commit** | **`37c7037`**: modules, scripts, tests, the ingested run 3, the index, the reports, the workbook v2 CSV, the COORDINATOR edits, the support map, the mentor `.md`, state and this section |
| **Evidence runs** | at `37c7037`, **`git_dirty: false`**: `reports/runs/20261103T185038Z_local_ingest_litsynth_run3`, `…185038Z_local_lint_item_rubrics`, `…185039Z_local_recheck_items_v2_3`, `…185039Z_local_build_p2b_items_review_v2`, `…185040Z_local_build_mentor_pilot_items` (`.json` / `.md`). Every tracked output byte-identical; the gitignored workbooks too (v2 `94d6cf5b…a9ee`, mentor `ad2c7424…8f79`) |
| Remote | **not pushed** (the Wednesday freeze package pushes) |

## 27. Data and checksums

| Object | SHA-256 | Notes |
| --- | --- | --- |
| `litsynth_run3_evidence.tar.gz` (read, outside the repo) | `10dc8a43c7fafcab5b53a097304c5f563ca4bcbbac574cf47efce5071f8ddc54` | equals the work package |
| run-3 `items.jsonl` / `summary.json` | `792eebe9…f896` / `17c7138f…2a2a` | `items.jsonl` equals the work package; = the per-item file |
| packets v3b (what run 3 read) | manifest `09ca030a…72c7`; `PK-SD2-TP1-00075.json` `9ec338d6…79ee` | read from Git at `157c96c` |
| **`artifacts/benchmark/items/run3/manifest.json`** | **`edb48bfc7d873afe71c75fa251d71981e4508117c5c9f9cf4993d8f53b89916f`** | 3 copied files, 1 item, 2 excluded (hashed) |
| `items/run3/items/BI-P2B-0010.json` | `421ad1069533835a8af69abedd21529d7b503173901ef7b89b70baf793ff55de` | human_review |
| `artifacts/benchmark/items/index.json` | `b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804` | 10 items; 1 superseded |
| `post_checks_v2_3_report.json` | `970f22396e2739597f8ac28011e42c0744bf883809e052853b2efa6183688539` | report only |
| `rubric_lint_v1a.json` | `183bcdd057ef0fcdc6e6aba1841a307eaa1d44c9444f7b33d542d24fd9e3de33` | report only; v1 unchanged (`5b5cf722…8d31`) |
| `P2b_items_review_v2.csv` (tracked) | `d5e5b7497e604af55cb6ea238982b4ec9aed64b74bd7a7176e8548629278cf46` | ITEMS sheet of the v2 workbook |
| `P2b_coordinator_edits_2026-11-03.yaml` | `98bae42677f5cc5727527f865657c53e3bcfae2b2c3a4e183a1126b2c4efff86` | section D verbatim; pinned |
| `P2b_mentor_support_map_v1.yaml` | `e3638e13eb4d12dc4f3aa6338d36edebfb1e7cdefd7cf5c6f9eee6d59c3bb291` | EXECUTOR reading |
| **`MENTOR_PILOT_ITEMS_2026-11-05.md`** | **`8420ec304e9bd8232282581e09ebf3af214ae5a857afe58d0c44d1990244b5fb`** | same content as the gitignored `.xlsx` |

## 28. Methods and readings for the COORDINATOR

- **Items index** (new; the package names one, none existed): `artifacts/benchmark/items/index.json`, per item every
  ingested version with `index_status` `current` / `superseded_by_<run>`; no run-2 file changes.
- **Post-checks v2.3 is opt-in.** `synthesis_post_checks` at its default is still v2.2, because the frozen agent v3.2 calls
  it and runs 2 and 3 are reproduced with it. v2.3 adds the two patterns, matched case-insensitively ("The model shows"),
  on the prompt and the reference texts, the scope v2.2 checks. A match inside an earlier match is flagged once.
- **Lint v1a** replaces `allowed_numbers` with `allowed[ _]numbers` and `exact values are not required` with
  `exact (?:numeric )?values are not required`.
- **Workbook v2 is a new file**: the v1 workbook was open in Excel (lock file present) when this package ran. `edit_origin`
  sits after `edited_reference_integrated`.
- **Mentor sheet.** Column 1 holds `#` and the item id (one column, so six columns match the six widths). The table side
  is generated from the item's table pattern and the dictionary's period sentence (lines 101--102); the regional item's
  per-region means and cells come from `table_patterns_v1.jsonl` (pinned). Paper side and passages: the groups and member
  statements in the support map, checked against the packet and the item's citations; passages verbatim from
  `statements.jsonl` (none exceeds 700 characters). **One addition beyond the specification:** under the
  `LS-199098498-04` passage, a bracketed provenance note quoting the extraction agent's unverified continuation
  (`passage_as_proposed`). Without it, the mentor would see a passage that does not contain the claim it is cited for.
  Kaiyuan may drop it.

## 29. Results

**Run 3.** 1 item (BI-P2B-0010, rung 7), `deterministic_pass` on the first turn, 0 leakage flags, no HTTP retry; post-checks
v2.2 reproduced. Its five literature sentences cite `…-driver-c1-008`, `…-driver-c2-001`, `…-mechanism-c1-024`,
`…-mechanism-c2-003` and the scenario caveat `…-pattern-c2-003`, all hedged "One study ...". Lint v1a: 5 flags (3
`hedge_strength_mismatch` on multi-source groups, 1 `required_single_source_only` on the scenario-contrast point, 1
generation constraint).

**Post-checks v2.3** (report only; v2.2 still passes on all ten): BI-P2B-0002 "The modeled projection shows"; 0003 "The
model shows"; 0004 "The model shows"; 0005 "The projection shows" (table sentence) and "The model projects"; 0007 "The
modeled projection shows"; 0008 "The projection shows" (table sentence). 0001, 0006, 0009 and 0010 (run 3) have no hit;
the superseded run-2 0010 has none either.

**Lint v1a:** 31 flags (generation_constraint 18, hedge_strength_mismatch 9, required_single_source_only 2,
rung1_prompt_mechanism 1, required_tercile 1); against v1, the only run-2 change is 0007 +2 (the two lines D-056 recorded).

**Sentence-support check of the COORDINATOR texts** (support map; 22 clauses: 11 supported, 2 guardrails, 6 partially
supported, 2 not supported by a verbatim passage, 1 supported only by an uncited packet group):

| item | clause | verdict | why |
| --- | --- | --- | --- |
| 0003 | "The main driver is large-scale warming rather than changes in regional atmospheric circulation" | **not supported by a verbatim passage** | only `LS-199098498-04`'s paraphrase; its recorded passage (prefix anchor) is "Identifying the climatological processes responsible … is beyond the scope of this study."; the claim, a citation of Schoof et al. (2019), is in the agent's unverified `passage_as_proposed` only; one paper, though the group counts 4 |
| 0003 | "land–atmosphere feedbacks that sustain heat waves in the Southwest add to it" | partially | `LS-158091651-01`: "a stronger factor for heat wave maintenance at southern latitudes", a forecast model "misrepresent[s]" them over the Southwest; a forecast-skill result, nothing on the projected change |
| 0003 | "one study suggests that night-time intensification of the urban heat island under calm, clear conditions contributes locally" | partially | UHI "most noticeable at night … calm conditions and clear skies" (background); intensification during a heat wave in a second paper (no night); no contribution to the change stated; the table quantity is the daily *maximum* heat index |
| 0006 | "The rise is driven primarily by large-scale warming, which increases the frequency, intensity and duration of heat waves." | partially | warming -> heat waves: `…-driver-c2-001` (4 papers); "primarily" rests on `LS-199098498-04` (as above) |
| 0006 | "Because the heat index combines temperature and humidity" | uncited packet group | `…-mechanism-c1-021` (context, review-supported, 11 papers) is in the packet, not cited by the item |
| 0007 | "… increase in every NCA5 climate region, with the largest increase in the Southeast and the smallest in Alaska." | partially | largest / smallest supported; the table covers 8 of 10 NCA5 regions (no U.S. Caribbean, no Hawai'i / USAPI); Alaska +0.0085 days |
| 0007 | "The increases are driven by large-scale warming" | **not supported by a verbatim passage** | `LS-199098498-04` only; `…-driver-c2-001` is in the packet but not cited |
| 0010 | "The main driver is large-scale warming, which raises heat-wave frequency, intensity and duration" | partially | as 0006 |
| 0010 | "The size of the change depends on the emissions pathway" | partially | generalises one study's heat-wave *duration* result (eastern United States) to the size of the change |

The three clauses the package names: **"rather than changes in regional atmospheric circulation"**: not supported by a
verbatim passage (above). **"stronger factor … at southern latitudes"** (0007): verbatim in `LS-158091651-01` ("appear
to be a stronger factor for heat wave maintenance at southern latitudes"), one paper, unhedged in the text, a
forecast-skill finding. **"about one day longer"** (0010): verbatim in `LS-5882914-02` ("almost 1 day longer than under
the RCP4.5 scenario"), single study, heat-wave duration, eastern United States. Further notes (supported clauses): 0006
"more than tripling" is the descriptor for a ratio of about 33 (1.4 -> 45.2 days); 0010 "no moderate-scenario projection
… in the table used here" is true (no RCP4.5 heat-index column in the dictionary), but "in the table" trips the existing
source-phrase check.

**Validation.** `pytest`: **1,510 passed, 2 skipped** (the two pre-existing skips); new `tests/test_litsynth_run3.py` (12); `tests/test_litsynth_run2.py` lint rebuild pinned to v1. Secrets and paths scan: **0 hits**.

## 30. Escalations

1. **`LS-199098498-04` is the only support for "large-scale warming is the main / primary driver"** (0003, 0006, 0007,
   0010): its recorded passage does not contain the claim. Options are Kaiyuan's or the COORDINATOR's: verify the
   continuation against the paper text on Polaris (not on this machine), or cite `…-driver-c2-001` and drop "main /
   primarily / rather than circulation".
2. **Group `…-driver-c1-008`** is labelled "Observed increase in heat-wave and drought frequency" but its members are
   heterogeneous (large-scale warming, land–atmosphere feedbacks, ozone stagnation, California droughts); its
   multi-source count does not back any single claim drawn from it.
3. 0007 "every NCA5 climate region"; 0010 "in the table used here" (a leakage phrase); 0006 "more than tripling" for about
   33-fold.

## 31. Limitations

Nothing is frozen; `final_frozen` is null for every item. The support map is one reader's judgement (EXECUTOR). FWI
column confirmation remains open (no FWI item in the pilot).

# Mentor sheet v2 --- provenance correction LS-199098498-04, DR-DESC-1 v2, edited answers v2

COORDINATOR work package "Mentor sheet v2" (2026-11-03). **No model call. Nothing frozen.** Decisions D-057, D-055c.

## 32. Commits and evidence runs

| | |
| --- | --- |
| Branch | `work/meeting-2026-10-22`, from head `ffafe31` |
| **Build commit** | **`7825fcf`**: corrections v1, descriptor rules v2, manifest, modules, scripts, tests, the edits v2, the support map v2, the overlay record, the workbook v3 CSV, the mentor `.md` and checks, docs |
| **Evidence runs** | at `7825fcf`, **`git_dirty: false`**: `reports/runs/20261103T232845Z_local_apply_provenance_corrections`, `…232845Z_local_build_p2b_items_review_v3`, `…232846Z_local_build_mentor_pilot_items`; every tracked output byte-identical to the build |
| Remote | pushed at the end of the package (authorized) |

## 33. Data and checksums

| Object | SHA-256 | Notes |
| --- | --- | --- |
| **`data/metadata/benchmark/provenance_corrections_v1.yaml`** | **`ea981346b7fa271da1ee2ecadce125b9502cbac2caee31d74b653653c06282f1`** | manifest-pinned; one record, `LS-199098498-04` |
| **`data/metadata/benchmark/descriptor_rules_v2.yaml`** | **`1e5554150b160f994009167d99f4a4afe79645cc55b26829e916c47777ce2ab7`** | manifest-pinned; v1 `5c2090a7…4650` unchanged |
| `artifacts/litstatements/corrections/provenance_corrections_v1_applied.json` | `9bbd39d924ab3314929b6fc54c2d67244ebfc76efe1d4ddf61ede85491d5e3c5` | overlay record; 0 files modified |
| `P2b_coordinator_edits_2026-11-03_v2.yaml` | `a1b011d4179c9c57eb3a05911e15b6264a84bde6726c43a9c673faf729c19ebf` | section C verbatim; pinned |
| `P2b_mentor_support_map_v2.yaml` | `bde0db83e8704e70b20c1960e18c04aa12b21393e516580d64ef1c537982fd3d` | EXECUTOR reading |
| `P2b_items_review_v3.csv` (tracked) | `39346e18b454c6586e758a9b78ffda1e7c5da73a8c80483e405a6361ef64fac3` | ITEMS sheet of the v3 workbook (`.xlsx` gitignored) |
| `MENTOR_PILOT_ITEMS_2026-11-05_v2_checks.json` | `f1c883cf3588e4e608d82ea880c4394b68e80aff98df27b70756c103da090d25` | leakage v2.3, verdicts, descriptors v2 |
| **`MENTOR_PILOT_ITEMS_2026-11-05.md`** | **`8362d765d8292f29aa8a6fd2a3d463d730c93dfe9b319ae3894776ea0766da22`** | v2; same content as the gitignored `.xlsx`; v1 (`8420ec30…b5fb`) stays in Git at `37c7037` |

## 34. Methods and readings for the COORDINATOR

- **Re-slice: `pending_polaris`.** The run-2 local paper copy holds only the agent's passages, and neither configured
  corpus root on this machine holds `98/199098498.json`. `reslice_correction` reads the raw paper JSON, checks its SHA-256
  against the recorded `945df7b9…5218`, and finds the corrected passage exactly (offsets in the section string, as the
  index and the agent's `evidence` count them); it also confirms the original span. The Polaris one-liner is in
  `PILOT_P2B_DESIGN.md` section 15.
- **`provenance_corrections_applied` is an overlay, not an item edit.** The item files are pinned by their run manifests
  and the items index; rewriting them would break the ingest evidence. The record is in the overlay file;
  `p2b_mentor_v2.item_with_corrections` returns the overlaid item. For confirmation.
- **The original passage type was already `cited_finding`** (role `cited_candidate`), so the correction changes the
  passage, not the strength inputs.
- **Workbook v3 is a new file**; v2 (built with the v1 texts) is kept as built, as v1 was. Questions for items 1, 2, 3, 5
  are the v1 questions (the work package gives none); item 1 is v1 in full.
- **Sentence support.** The v2 edits cite `…-driver-c2-001` for 0003 and 0007 and `…-mechanism-c1-021` for 0006 --- packet
  groups the generated items do not cite; the paper side lists them, marked "cited by the edited answer, not by the
  generated item" (`added_by_edit` in the support map). The bracketed continuation note of v1 is removed.
- **DR-DESC-1 v2 readings** (D-055c): v2 class before v1's low-baseline phrase; increase only; `round(value, 1)`.

## 35. Results

**Correction.** `LS-199098498-04` overlaid; reslice **`pending_polaris`**. `…-driver-c1-008`: `multi_source_supported`
before and after --- group file (3 core / cited papers of 4: 158091651, 199098498, 5838629) and all eight packets (0003,
0007--0009: 3 papers; 0004--0006, 0010: 2 cited papers, 199098498 and 5838629). Items with `provenance_corrections_applied:
[LS-199098498-04]`: **0003--0010**.

**Descriptors v2.** 0006: `magnitude_class` "rising from rare to common", `anchor_pair` "from about 1 day to about 45
days" (baseline 1.351 -> 45.239 days, ratio 33.5). 0007: `negligible_regions: [Alaska]` (+0.0085 days), `smallest`
"essentially no change: Alaska", `largest` "the largest increase: Southeast". 0001, 0003, 0010 unchanged from v1.

**Leakage v2.3 on the v2 texts:** 0 hits (10 texts).

**Sentence-support check v2** (27 clauses: 17 supported, 2 guardrails, 5 partially supported, 3 supported by a packet group
the generated item does not cite, **0 not supported by a verbatim passage**; 8 clauses --- 6 supported, 2 partially --- rest
on the corrected passage and so on the Polaris re-slice):

| item | clause | verdict | why |
| --- | --- | --- | --- |
| 0003 | "Warming is the main driver" | partially | warming as a driver: `…-driver-c2-001` + the corrected passage; "main" rests on one paper relaying a cited finding, unhedged in this lead clause (hedged in the next) |
| 0003 | "One study suggests that land–atmosphere feedbacks appear to be a stronger factor in sustaining heat waves in the Southwest." | partially | the passage says "at southern latitudes"; the Southwest is where the forecast model *misrepresents* the feedbacks; forecast-skill finding |
| 0010 | "Warming is the main driver" | partially | as 0003 |
| 0010 | "The change is scenario-dependent" | partially | generalises one study's heat-wave duration result to the table quantity |
| 0010 | "one study of the eastern United States reports heat-wave duration almost one day longer …" | partially | duration result verbatim; "eastern United States" is the extraction agent's region tag, not in the passage |
| 0003 | "global warming is expected to increase the frequency, intensity and duration of heat waves" | uncited packet group | `…-driver-c2-001`; full clause = `LS-14006228-04` (review) |
| 0006 | "Because the heat index combines temperature and humidity" | uncited packet group | `…-mechanism-c1-021` (definition; two background passages) |
| 0007 | "global warming is expected to raise heat-wave frequency, intensity and duration" | uncited packet group | `…-driver-c2-001` |

The two v1 "not supported by a verbatim passage" clauses are gone (the corrected passage states the claim, hedged and
attributed); the urban-heat-island clauses (partial in v1) are removed; 0007 "every NCA5 climate region" and 0010 "in
the table used here" are fixed.

**Validation.** `pytest`: **1,524 passed, 2 skipped** (the two pre-existing skips); new `tests/test_mentor_v2.py` (14); `tests/test_litsynth_run3.py` v1 mentor test now compares with the v1 `.md` at `37c7037`. Secrets and paths scan: 0 hits.

## 36. Escalations

1. **Re-slice pending on Polaris** (one line, `PILOT_P2B_DESIGN.md` section 15). Until it returns `exact`, eight clauses (six
   supported) rest on a passage verified by grep, not by offsets.
2. **Five clauses partially supported** (table above), for Kaiyuan before Thursday: in particular "Warming is the main
   driver" (0003, 0010) states unhedged what one paper relays, and 0003's "in the Southwest" is not what the passage says.
3. **`…-driver-c1-008` multi-source by rule, not by claim** (escalation 2 of section 30 stands): in four packets it is two
   cited papers saying different things.
4. **DR-DESC-1 v2 edge case**: "baseline < 2 days" alone labels a small change from a small baseline "rising from rare
   to common" (D-055c); no pilot item has one.

## 37. Limitations

Nothing is frozen; `final_frozen` is null for every item; the packets are v1-descriptor packets. The support map v2 is one
reader's judgement (EXECUTOR).
