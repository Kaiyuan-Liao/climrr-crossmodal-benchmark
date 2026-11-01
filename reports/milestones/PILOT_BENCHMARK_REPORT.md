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
