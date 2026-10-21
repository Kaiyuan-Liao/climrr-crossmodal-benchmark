# Track B / Stage 2 --- dictionary-grounded concept coverage survey (diagnostic)

Authorized by [`docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md`](../../docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md)
(D-025, Track B, Stage 2a--2c **as diagnostics**; criteria 23--31). **No paper
was read. No QA. Nothing here changes `concept_map.yaml`, any column status, or
index 117.**

## 1. Milestone ID and title

**Track B / Stage 2a --- dictionary concept inventory + survey tooling; Stage
2b/2c --- survey run 1, executed by Kaiyuan on Polaris and ingested here as a
diagnostic** (follow-up: v3 tools tracked; run 1 ingested; coverage doc). M1
remains open (D-014). Track A (M4-WP4) runs separately.

## 2. Objective

Build a stable, verbatim inventory of the concepts the ClimRR data dictionary
describes (2a); track the survey context clause and the 2b/2c tooling with
tests, so that the Polaris run uses pinned, checked inputs. **Excluded:** any
CSV-column interpretation, any status change, family assignment, concept-map
change, reading, QA, and running 2b/2c here (the ALCF endpoint and the index are
on Polaris).

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/trackb-stage2`, from `main` at **`38116a0`** (clean tree; `work/m4-wp4-*` untouched) |
| Package commit | the commit carrying this report (single commit; head SHA reported to the COORDINATOR) |
| Remote | **not pushed, not merged** (as the work package directs) |

## 4. Data version and checksums

| Object | SHA-256 | Notes |
| --- | --- | --- |
| `data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf` (read) | `b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db` | verified against the manifest before extraction (D-002) |
| **`data/metadata/dictionary_concepts.yaml`** (new) | **`288d08c5b92a32dbc5329834ceffc6a7ebc746d02479308431407cfddd81d064`** | byte-deterministic; pinned in `data/manifest.json`; `-text` |
| **`data/metadata/litcollect/survey_context_clause_v1.txt`** (new) | **`fec9b5ca97f18e6e409a4b6e10b50faf5ab3c5404a33381eb8e67e9debc3626f`** | 403 bytes; pinned in `data/manifest.json`; `-text` |
| `trackb_scripts.tar.gz` (delivered, read) | `8c3f75fea90c66bdb9461e342afe429ec7aab48ae0bb545804a9582ee7c20f59` | matches the work package |
| **`scripts/litcollect/survey_driver.py`** (as tracked) | **`877fec477c5005f0642e31b558b3a01493d5466680546fc610bc3d05e8797155`** | the COORDINATOR's revised driver (follow-up on `246fccd`), byte-identical to the delivered file; replaces the tarball member `b3292e22…0d3a` |
| **`scripts/litcollect/survey_driver.py` v3** (as tracked, follow-up) | **`e1fb664c98e4ff866bb348c8930bfc1b9243957441b8a19ea0893e0b711af4cd`** | the driver run 1 executed; passes `--no-hits` (D-026) |
| **`scripts/litcollect/run_query.py` v3** (as tracked, follow-up) | **`5f56ee49f0da675f49ef490b506c030b307c693032e8be9097e499cf1c64030d`** | v2 `a93eeba7…7708` (LITCORPUS-02, at `38116a0`) + opt-in `--no-hits` |
| `survey_run1.tar.gz` (delivered, read) | `edd68196834d54fae7cd0073dcb6d389a55452caf90f23d6fc838e160c7a2739` | extracted outside the repo; both script members equal the v3 hashes |
| **`artifacts/literature/survey/run1/manifest.csv`** (new) | **`74ba7d7c72e7920ac16e1cc7c49ab2543add316df37baf60ff3b52c10c2d125d`** | 122 files, 12,237,164 bytes; pinned in `data/manifest.json` → `diagnostics` |
| `scripts/litcollect/probe_alcf_inference.py` (as tracked) | `79181c48981c709b49b90d78fc8aaddffaf12d2f1bb0591b9a9daa3aad438c66` | byte-identical to the tarball member |

`data/raw/FullData.csv` was verified by `pytest` (hash gate) and **not read** by
any Stage 2a code.

## 5. Environment and execution location

Local (`location: local`), conda env `climrr`, Python 3.11.16, macOS arm64,
pinned D-007 libraries (pypdf 6.18.0, PyYAML 6.0.3); DuckDB 1.5.4 for the
synthetic-index tests. Run record:
`reports/runs/20261020T175937Z_local_build_dictionary_inventory.{json,md}`.
**Sophia not involved.**

**Survey run 1 (2b/2c) --- Polaris**, executed by Kaiyuan: login node
`polaris-login-01`; `module load conda/2026-10-01` + conda env `globus_env`;
Python 3.11.x (**patch version not recorded** in any run output --- the work
package said to take it from `_context/summary.json`, which records DuckDB only);
DuckDB **1.5.4** (`_context/summary.json`); model `gpt-oss-120b` on Metis via
`https://inference-api.alcf.anl.gov/resource_server/metis/api/v1`;
**2026-10-20T21:54:34Z → 22:09:18Z** (`survey.log`). Index identity
`fbb4affb…7a94` (LITCORPUS-02 source index, 186,346 documents); inventory
`288d08c5…d064`; context clause `fec9b5ca…626f`, matching **120,050** documents.
**Executed from untracked copies in the litcollect `scripts/` folder whose SHA-256
equal the tracked v3 files**, after an aborted first attempt (offsets stage; no
outputs kept). Local ingest run record:
`reports/runs/20261020T224151Z_local_ingest_survey_run1.{json,md}`.

## 6. Work completed

- **Phase A --- 2a.** Escalated the one undefined point --- the unit of "one
  entry per dictionary-described variable or metric" --- to Kaiyuan with three
  options; **measure level** chosen (**D-026**). Built `src/climrr/dictconcepts.py`
  (rules) and `scripts/build_dictionary_inventory.py` (manifest check → pypdf
  page-by-page extraction → YAML + generated doc → run record).
- **Phase B.** Wrote the survey context clause v1 exactly as specified (plus a
  trailing LF), hash-pinned it, recorded it in `docs/LITCORPUS02_PROVENANCE.md`
  §12 as "survey context clause v1 (diagnostic)". Verified it equals the v1
  production context group minus exactly the five family terms.
- **Phase C.** Copied `survey_driver.py` and `probe_alcf_inference.py` unmodified;
  tests against a local mock chat-completions server and a synthetic
  `build_index.py` index; governance text in `docs/BRIDGE_ELIGIBILITY.md` §7.
- **Phase D.** This report; `docs/PROJECT_STATE.md` (two tracks open);
  `docs/DECISION_LOG.md` D-026.
- **Follow-up (survey run 1).** Phase A: v3 `run_query.py` / `survey_driver.py`
  tracked (hashes verified), allowlist re-pinned, `--no-hits` tested, v2 → v3 in
  D-026. Phase B: run 1 verified and ingested as diagnostic `TRACKB-SURVEY-RUN1`.
  Phase C: `docs/CONCEPT_COVERAGE_SURVEY.md` generated from the rows. Phase D:
  this report, `PROJECT_STATE.md`, `MENTOR_BRIEF.md`, `KNOWLEDGE_FILES`.

## 7. Deliverables and exact file paths

`src/climrr/dictconcepts.py` · `scripts/build_dictionary_inventory.py` ·
`data/metadata/dictionary_concepts.yaml` · `docs/DICTIONARY_CONCEPTS.md` ·
`data/metadata/litcollect/survey_context_clause_v1.txt` ·
`scripts/litcollect/survey_driver.py` · `scripts/litcollect/probe_alcf_inference.py` ·
`tests/test_dictconcepts.py` · `tests/test_survey_driver.py` ·
**follow-up:** `scripts/litcollect/run_query.py` + `survey_driver.py` (v3) ·
`src/climrr/coveragesurvey.py` · `scripts/ingest_survey_run1.py` ·
`artifacts/literature/survey/run1/` (+ `manifest.csv`) ·
`artifacts/literature/survey/survey_run1.log` · `docs/CONCEPT_COVERAGE_SURVEY.md` ·
`tests/test_survey_run1.py` · edits to `tests/test_litcollect_tools.py`,
`tests/test_survey_driver.py`, `scripts/stage_knowledge.py`, `docs/MENTOR_BRIEF.md`,
`.gitattributes` ·
`reports/runs/20261020T224151Z_local_ingest_survey_run1.{json,md}` ·
`reports/runs/20261020T175937Z_local_build_dictionary_inventory.{json,md}` ·
edits: `data/manifest.json` (two `files` entries + amendment), `.gitattributes`,
`scripts/verify_no_secrets_or_paths.py` + `tests/test_secrets_scan.py` (exemption),
`docs/LITCORPUS02_PROVENANCE.md`, `docs/BRIDGE_ELIGIBILITY.md`,
`docs/DECISION_LOG.md`, `docs/PROJECT_STATE.md`, this report.

## 8. Methods and rules that affect scientific meaning

- **Unit of inventory (D-026, owner decision).** One concept per ClimRR output
  quantity the narrative (pp. 4--12) describes. Max+min daily temperature and
  HDD+CDD stay one concept each (described in one passage). Heat index split per
  the dictionary's enumeration; four thresholds = four concepts. Methodology
  sections, the pp. 4/13 variable lists and field-table rows are not concepts.
- **Names** are the dictionary's heading or enumerated label, verbatim, with
  their own page/span. Two documented choices: the seasonal-average FWI takes
  the section heading "Fire Weather Index" (its sub-heading "Calculating Seasonal
  Averages" names a procedure); the threshold concepts take the p. 18 field-table
  wording, since the narrative label covers all four.
- **Passages** are EXECUTOR-chosen minimal windows, located by anchors, stored as
  exact page slices. The threshold concepts share p. 11 item 3, cut mid-sentence
  by the page break.
- **Units / threshold / scenario** only when stated inside the passage (or, for
  thresholds, the name). Consequence: temperature units (field tables only) and
  the heat-index periods (p. 12, outside the windows) are null.
- **`verified_columns`** applied literally: verified **and** cited by a
  resolution record → all empty (no verified column references one; rule 1 of
  `resolutions.yaml` forbids a record from assigning that status).
- **No filtering, aggregation, unit conversion, coercion or renaming of any data.**
  No CSV column name is read.

## 9. Results with compact tables or examples

**14 concepts; 0 `listed_only`; 14 `dictionary_described`; `family_hint` 0
non-null; `verified_columns` 0 non-empty.** Ten-line sample:

```
DC-001  p6   Temperature (Annual)                    units —       threshold —
DC-003  p7   Precipitation                           units inches
DC-004  p7   Wind Speed                              units mph
DC-005  p8   Consecutive Days with No Precipitation  threshold "the total daily \nprecipitation quantity equaled zero"
DC-006  p8   Degree Days (HDD/CDD)                   threshold "65°F (18.33°C)"
DC-007  p10  Fire Weather Index                      "Argonne calculated the average daily FWI value by season …"
DC-008  p10  Calculating FWI Classes                 threshold "95th percentile"; scenario "historical, mid-century RCP8.5, and end-of-century RCP8.5"
DC-009  p11  Summer daily maximum heat index         "1. Summer daily maximum heat index: this output is calculated by …"
DC-010  p11  Summer seasonal maximum heat index      "2. Summer seasonal maximum heat index: this measure finds …"
DC-012  p11  Number of Summer days with daily max heat index above 105 F   threshold "above 105 F"
```

Full table: `docs/DICTIONARY_CONCEPTS.md`.

**Revised driver (`877fec47…7155`) on this inventory --- what reaches the query from the name:**

| Concepts | Stored name | First candidate |
| --- | --- | --- |
| DC-003, 004, 005, 007, 008, 009, 010 | kept | the name |
| DC-001, 002 | dropped (parentheses) | stripped variant **`temperature`** (both) |
| DC-006 | dropped (parentheses) | stripped variant **`degree days`** |
| DC-011--014 | dropped ("more than 6 words") | **none** --- model terms only; no model term → `status: "error"` row |

**Stage 2b/2c --- survey run 1 (EXECUTED, diagnostic).** 14 rows: **12 `ok`, 2
`error`**. Counts are **diagnostic coverage counts, not prevalence**; terms are
`candidate_surface_form`, inert. Full table, per-term counts and findings:
[`docs/CONCEPT_COVERAGE_SURVEY.md`](../../docs/CONCEPT_COVERAGE_SURVEY.md) (generated from the rows).

| Concept | Topical-only | Context-filtered | Status |
| --- | --- | --- | --- |
| DC-001 | 124,420 | 88,245 | ok |
| DC-002 | 123,948 | 88,021 | ok |
| DC-003 | 84,926 | 61,190 | ok |
| DC-004 | 27,498 | 17,394 | ok |
| DC-005 | 6,981 | 4,946 | ok |
| DC-006 | 3,076 | 2,638 | ok |
| DC-007 | 548 | 395 | ok |
| DC-008 | 551 | 396 | ok |
| DC-009 | 0 | 0 | ok |
| DC-010 | 1 | 1 | ok |
| DC-011 | --- | --- | error (no searchable phrase) |
| DC-012 | 0 | 0 | ok |
| DC-013 | --- | --- | error (no searchable phrase) |
| DC-014 | 2 | 2 | ok |

Findings, computed: **(a)** DC-007's 548 topical ids **are** the 548 of the
LITCORPUS-02 fire-weather topical-only diagnostic (set equality, not just the
count) --- consistency check passed. **(b)** DC-001/002/003: the bare word is
99.6 / 100.0 / 99.9 % of the topical count. **(c)** heat-index measures DC-009--014:
0, 1, ---, 0, ---, 2; every DC-011/013 model proposal contained `°` or `>`.
**(d)** heat-index family group 1,082 (`heat index` alone 1,080) vs measure-level
maximum 2.

## 10. Validation performed

- `pytest`: **906 passed** (894 at `9d2da14` + 12): `--no-hits` writes a
  header-only `hits.csv`, sets `hits_recorded: false`, and leaves ids, raw ids,
  `disambiguation.csv` and every count identical to a run without the flag
  (`test_litcollect_tools.py`); the v3 driver passes it, so `_context` and topical
  `hits.csv` are header-only (`test_survey_driver.py`); `test_survey_run1.py` (10):
  the copy equals `manifest.csv`, which is pinned under `diagnostics` and not in
  `external_corpora`; no `_duckdb_tmp`, no `topical/hits.csv`; every row
  re-verifies against its id files and equals `survey_table.csv`; pins of
  inventory, clause, index and v3 tools; DC-007 set equality; the heat figures;
  error rows are sanitizer drops with `model_parse_error: null`; the doc
  regenerates byte for byte; no candidate reaches `concept_map.yaml`.
- Before copying, `verify_source` checked both delivered scripts against the
  tracked v3 hashes, that each of the 12 `topical/hits.csv` is header-only, and
  that `reports/survey_run1.log` is byte-identical to `survey/run1/survey.log`.
- `scripts/verify_no_secrets_or_paths.py` with every new file staged: **zero hits**.
  The run files hold no absolute path (index path is relative,
  `index/full_705k_v2_filtered`) and no credential; the credential word occurs only inside
  the model `usage` field names (`completion_…s`, `reasoning_…s`), which the
  boundary-anchored rule does not match.
- Pre-existing pins unchanged: `concept_map.yaml`, the M5-WP2 matrix, the
  LITCORPUS-02 records; the D-026 allowlist re-pinned to the v3 driver only.

## 11. Failures, rejected cases, and known limitations

**Deviations in the run itself (survey run 1):**

- **Untracked-copy execution.** The run executed from untracked copies in the
  litcollect `scripts/` folder whose SHA-256 equal the tracked v3 files --- not
  from a pinned checkout of this repository. The equality is the only link.
- **Aborted first attempt.** The first attempt stalled in `run_query.py`'s offsets
  stage (O(admitted documents × terms) in Python; >3 h for the 120,050-document
  context set); no outputs kept. Hence v3 (`--no-hits`, D-026).
- **Sanitizer-driven error rows.** DC-011 and DC-013 are `error` because every
  proposed phrase contained `°` or `>` (and the stored names exceed six words):
  "no searchable phrase exists", not a model failure. DC-012 / DC-014 survived on
  4 and 1 phrases. The four threshold concepts share one passage, so their
  vocabulary is the model's alone (§9, Stage 2a).
- **Run-record label `local`.** The driver writes no run record (exempt, D-026);
  the only run record is the **local** ingest
  (`20261020T224151Z_local_ingest_survey_run1`), whose host, Python and
  `pip freeze` are this laptop's, not Polaris's. The Polaris run is evidenced by
  `survey.log`, `row.json`, `candidates.json`, `summary.json` and
  `survey_table.csv`.

**Limitations:** no hit offsets for any run-1 document (`--no-hits`); Python patch
version on Polaris unrecorded; R-FWI-1 not applied (bare `fwi` in DC-007/008);
no place filter; `temperature` (DC-001/002) and `precipitation` (DC-003) dominate
their rows; `cdd` is shared by DC-005 and DC-006; `mat` is a 3-letter candidate.

## 12. Deviations from the approved plan

- **Stage 2a** (unchanged): granularity escalated (D-026); `name_source` added;
  trailing LF on the clause; hash-pinned scanner allowlist (D-026).
- **Follow-up --- EXECUTOR choices, for review:**
  - Ingest done by a tracked script (`scripts/ingest_survey_run1.py` +
    `src/climrr/coveragesurvey.py`) that writes a run record, as CLAUDE.md
    requires of every script; it verifies before copying and is rerunnable
    (an existing copy must be byte-identical).
  - **`_context/hits.csv` was kept.** It is header-only too, but the work package
    excludes only the `topical/hits.csv` files; it is 79 bytes and in the manifest.
  - **Finding (d) wording corrected.** The work package says "the family term
    `heat index` alone matches 1,082"; the LITCORPUS-02 diagnostic records
    **1,080** for `heat index` alone and **1,082** for the family group (`heat
    index` | `heat-index` | `extended heat index`). The doc states both. The
    conclusion (two to three orders of magnitude) is unchanged.
  - **Finding (c) wording.** "return 0--2" applies to the four `ok` rows; the two
    `error` rows have no count. The doc says so.
  - The run log is stored as `artifacts/literature/survey/survey_run1.log` (beside
    `run1/`), byte-identical to `run1/survey.log`.
  - `survey_table.csv` is kept as delivered (sorted by count, errors last); the doc
    sorts by concept id.
  - Report fields 1, 4, 5 and 7 were updated alongside 9--15, as they named the
    pre-run state.

## 13. Open decisions and mentor questions

| Item | Owner | Blocks |
| --- | --- | --- |
| **(Q-a)** *answered (D-027): authorized, `candidate_family` only* --- report coverage at both levels — authorize a run-2 prompt variant that asks for the *family* name of the quantity (one row per dictionary concept, same provenance, labelled diagnostic)? | GUIDANCE | any run 2 |
| **(Q-b)** *answered (D-027): no; family coverage alongside, never attributed to a measure* --- treat threshold measures as lexically unsearchable and survey them only at family level? | GUIDANCE | interpretation of DC-011--014 |
| **(Q-c)** *answered (D-027): narrowly authorized, N-1 … N-7* --- may the sanitizer accept `°`, `>` and `%` by normalizing to words (`degrees f`, `above`, `percent`) — or is any transformation of a model term out of bounds? | GUIDANCE | a sanitizer change |
| D-026 v2 → v3 tools and the re-pinned allowlist | COORDINATOR / GUIDANCE review | --- |
| Bare `temperature` for DC-001/002 --- accepted for the diagnostic run? (now shown to be 99.6--100 % of those rows) | COORDINATOR | interpretation of two rows |
| Python patch version on Polaris --- *closed as `unknown` (ruling action 22, D-027); not supplied* | Kaiyuan | nothing; provenance completeness |
| Q22 (705k filter) stays open | JL | nothing here |

## 14. Gate status

**GUIDANCE: PASS as diagnostic (D-027, 2026-10-20)** --- Stage 2a complete;
Stage 2b/2c run 1 accepted as exploratory coverage evidence. Reviewed head
**`2331e19`** (pushed, `origin/work/trackb-stage2`). Merge authorized after the
ruling bookkeeping (this commit); Kaiyuan performs the merge. Ruling:
[`docs/M4_WP4_TRACKB_GUIDANCE_RULING.md`](../../docs/M4_WP4_TRACKB_GUIDANCE_RULING.md).

As proposed for review:

| Criterion (D-025 ruling, verbatim) | Status | Evidence |
| --- | --- | --- |
| 23. Stage 2a contains only dictionary-described concepts/metrics. | **MET** | page-sliced passages; `test_dictconcepts.py` |
| 24. Stage 2a does not change existing column statuses. | **MET** | status counts 21/20/130/28/76 unchanged (test) |
| 25. Index 117 remains unlabeled. | **MET** | not referenced (test) |
| 26. Stage 2b outputs are explicitly `candidate_surface_form`. | **MET** | all 14 `candidates.json` (`test_survey_run1.py`) |
| 27. Stage 2b records model and prompt provenance. | **MET** | model, endpoint, date, prompt SHA-256 re-checked per concept |
| 28. Stage 2b vocabulary never enters production automatically. | **MET** | `concept_map.yaml` unchanged; no code reads survey terms (test) |
| 29. Stage 2c is deterministic and restartable. | **MET** | restart test; run 1 counts re-derive from its id files |
| 30. Stage 2c counts are labeled diagnostics, not literature-prevalence estimates. | **MET** | `row.json` label; every count column in the doc labelled |
| 31. Literature yield does not automatically determine unit selection. | **MET** | no code reads survey output for selection; questions put to GUIDANCE |
| 33. No QA is generated. | **MET** | none |

**Proposed: Stage 2a COMPLETE; Stage 2b/2c run 1 EXECUTED AND INGESTED (diagnostic), for GUIDANCE review.**

## 15. Next bounded objective

**Stage 2 run 2, family level (authorized, D-027) --- pending the driver
update.** For all 14 measure concepts: preserve run-1 measure identity; request
a `candidate_family` (stored only as `status: candidate_family`, with
`dictionary_concept_id`, `dictionary_passage`, `model_id`, `prompt_sha256`,
`candidate_family`, `candidate_family_surface_forms`, `date`, `status`); apply
only the frozen orthographic table
(`data/metadata/litcollect/normalization_table_v1.yaml`, SHA-256
`80a5e0e386dfe8a984e1a5ba2ace781d15601f9b0723b75d238b6de5d1226e03`, N-1 … N-7;
originals retained); topical-only and context-filtered counts; measure-level and
family-level coverage side by side, **run 1 unchanged**. Not started; the driver
is unchanged in the bookkeeping package.

For the driver update, observed while testing the table (not acted on): of the
29 run-1 model terms dropped as "not a plain lowercase phrase", the table makes
**26** plain (3 keep their parentheses); only **7** of those 26 have six words or
fewer, so the driver's unchanged "more than 6 words" rule would still drop 19.
