# Track B / Stage 2 --- dictionary-grounded concept coverage survey (diagnostic)

Authorized by [`docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md`](../../docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md)
(D-025, Track B, Stage 2a--2c **as diagnostics**; criteria 23--31); run 2 by
[`docs/M4_WP4_TRACKB_GUIDANCE_RULING.md`](../../docs/M4_WP4_TRACKB_GUIDANCE_RULING.md)
(D-027, B2--B4). **No paper was read. No QA. Nothing here changes `concept_map.yaml`, any column status, or
index 117.**

## 1. Milestone ID and title

**Track B / Stage 2a --- dictionary concept inventory + survey tooling; Stage
2b/2c --- survey run 1, executed by Kaiyuan on Polaris and ingested here as a
diagnostic** (follow-up: v3 tools tracked; run 1 ingested; coverage doc).
**Stage 2 run 2 (family level, D-027 B2--B4) --- driver v4; executed by Kaiyuan
on Polaris 2026-10-21 and ingested here as diagnostic `TRACKB-SURVEY-RUN2`.** M1
remains open (D-014). Track A (M4-WP4) runs separately.

## 2. Objective

Build a stable, verbatim inventory of the concepts the ClimRR data dictionary
describes (2a); track the survey context clause and the 2b/2c tooling with
tests, so that the Polaris run uses pinned, checked inputs. **Excluded:** any
CSV-column interpretation, any status change, family assignment, concept-map
change, reading, QA, and running 2b/2c here (the ALCF endpoint and the index are
on Polaris).

**Run 2:** for each of the 14 measures, ask the model for a broader
`candidate_family` and its surface forms, normalize them under the frozen
orthographic table only, count topical-only and context-filtered documents over
the family forms, and report family coverage **beside** the unchanged run-1
measure coverage. **Excluded:** approving any family, attributing family
coverage to a measure, any change to run 1, the concept map, C-2,
compatibility, unit design or QA.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/trackb-stage2`, from `main` at **`38116a0`** (clean tree; `work/m4-wp4-*` untouched) |
| Package commit | the commit carrying this report (single commit; head SHA reported to the COORDINATOR) |
| Remote | **not pushed, not merged** (as the work package directs) |
| **Run 2** | `work/trackb-run2` from `main` at **`d7032de`**: `1efdb47` (knowledge list), `3ccb4ba` (driver v4), then the ingest commit carrying this report version; **not pushed, not merged** |

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
| **`scripts/litcollect/survey_driver.py` v4** (run 2) | **`f929ab6a366987d29e5565fe9fa9f80b47cb1c57d19e01ff3af5affdd99baf9f`** | tracked at `3ccb4ba`; equals `driver_sha256` in all 14 run-2 rows |
| prompt variant F (`PROMPT_F`, the template) | `7097c86ccbb694fe34fa5f4dc51ed087594295e3c37ddd97c56ab94702a97931` | equals `prompt_template_sha256` in all 14 rows |
| `data/metadata/litcollect/normalization_table_v1.yaml` | `80a5e0e386dfe8a984e1a5ba2ace781d15601f9b0723b75d238b6de5d1226e03` | frozen (D-027); equals every row's `normalization_table_sha256` |
| `survey_run2.tar.gz` (delivered, read) | `8f92e3c328e642ef142fc1e77edb7721926518e7d70087bd7503ade7a03bf85a` | matches the work package; extracted outside the repo |
| **`artifacts/literature/survey/run2/manifest.csv`** (new) | **`1182deea5d2ec6ed992e9415a6e6d7b8bcadd78e09da22ab9cb86fab2887c363`** | 132 files, 19,106,195 bytes; pinned in `data/manifest.json` → `diagnostics` (`TRACKB-SURVEY-RUN2`) |
| `artifacts/literature/survey/run1/manifest.csv` (unchanged) | `74ba7d7c72e7920ac16e1cc7c49ab2543add316df37baf60ff3b52c10c2d125d` | run 1 untouched (test) |
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

**Survey run 2 --- Polaris**, executed by Kaiyuan: **2026-10-21T20:02:05Z →
20:18:28Z** (`survey.log`), `--mode family`, model `gpt-oss-120b` on the same
Metis endpoint; DuckDB **1.5.4**; the log's START line carries `driver_sha
f929ab6a3669`, `prompt_f_sha 7097c86ccbb6`, `norm_table_sha 80a5e0e386df`,
`inventory_sha 288d08c5b92a`, `context_sha fec9b5ca97f1`, `index_identity
fbb4affb7162`, `run1_rows=14`; context clause **120,050** documents (id set equal
to run 1's). **Login node, conda environment and Python version are not recorded
in any run-2 output** and were not stated; recorded as such. Local ingest run
record: `reports/runs/20261021T202937Z_local_ingest_survey_run2.{json,md}`.

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
- **Run 2 (D-027 B2--B4).** Driver v4 (`3ccb4ba`, method in §8). Kaiyuan ran it
  on Polaris. Ingest: tarball hash checked; log START line verified against the
  pins; every row re-verified (pins, `candidate_family` status, counts re-derived
  from the id files, context id set = run 1's, measure counts and run-1 row
  SHA-256 = the **ingested** run-1 rows, `survey_table.csv` = the rows); copied to
  `artifacts/literature/survey/run2/` without the 14 header-only
  `topical/hits.csv`; `manifest.csv` pinned under `diagnostics`; run 1 checked
  byte-unchanged before and after. `docs/CONCEPT_COVERAGE_SURVEY.md` regenerated
  with the run-2 section (side-by-side table, per-term counts, normalization
  record, findings 1--5 computed). `MENTOR_BRIEF.md`, `PROJECT_STATE.md`, this
  report.

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
**Run 2:** `scripts/litcollect/survey_driver.py` v4 · `tests/test_survey_driver_v4.py`
(at `3ccb4ba`) · `src/climrr/coveragesurvey_run2.py` · `scripts/ingest_survey_run2.py` ·
`tests/test_survey_run2.py` · `artifacts/literature/survey/run2/` (+ `manifest.csv`) ·
`artifacts/literature/survey/survey_run2.log` ·
`reports/runs/20261021T202937Z_local_ingest_survey_run2.{json,md}` · edits:
`src/climrr/coveragesurvey.py` (`render_doc` takes the run-2 section),
`scripts/ingest_survey_run1.py` (regenerates the two-run doc once run 2 exists),
`tests/test_survey_run1.py` (doc test), `data/manifest.json`, `.gitattributes`
(comment), `docs/CONCEPT_COVERAGE_SURVEY.md`, `docs/MENTOR_BRIEF.md`,
`docs/PROJECT_STATE.md`, this report.

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

**Run 2 --- driver v4 (`f929ab6a…af9f`).** `--mode measure` (default) is v3: on the synthetic corpus its
outputs are **byte-identical** to v3's (recovered from git at `d7032de`,
`e1fb664c…f4cd`) for the same inputs, under a frozen clock, restart included.
`--mode family`: prompt F per concept; `family.json` with exactly the ruling's
fields plus `model_raw_response_excerpt` and `parse_error`, `status:
candidate_family`; every model form normalized under the frozen table, then
sanitized, each recorded with `original`, `normalized`, `rules_applied`,
`searched` (plus `search_term`, `reason`); topical-only and context-filtered
counts over the family forms; `row.json` carries the run-1 measure identity and
counts copied from `--run1` (row SHA-256 recorded) beside the family counts,
labelled *"diagnostic — family coverage is not attributable to the measure"*;
`survey_table.csv` side by side, sorted by concept id. Restart, error rows and
logging as v3.

**Fail-closed checks added.** The cached `_context` id set is reused only if its
`summary.json` records the same context-clause SHA-256 and index identity and
`ids.txt` holds `admitted_count` ids (missing in v3; both modes). Family mode
refuses to start unless every run-1 row exists and matches this run's concept
id, dictionary name, inventory, context clause and index identity --- so measure
and family counts are always over the same index and clause.

**Run-2 ingest.** Verified before copying (see §6); the doc's run-2 statements
are computed from the ingested rows, the LITCORPUS-02 diagnostics
(`fire_weather_diag_topical_only`, `extreme_heat_diag_topical_only`) and
`concept_map.yaml` --- none is typed in. Three coverage levels are kept apart in
every table: measure-level (run 1), concept-map family terms (LITCORPUS-02
diagnostics), model-proposed family forms (run 2).

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

**Stage 2 run 2 (EXECUTED, family level, diagnostic).** 14 rows, all `ok`; every
`candidate_family` a model hypothesis, `status: candidate_family`. Measure =
run 1, copied unchanged; family counts labelled *"diagnostic — family coverage
is not attributable to the measure"*. Topical-only / context-filtered:

| Concept | Measure (run 1) | `candidate_family` | Family |
| --- | --- | --- | --- |
| DC-001 Temperature (Annual) | 124,420 / 88,245 | `temperature` | 123,948 / 88,021 |
| DC-002 Temperature (Seasonal) | 123,948 / 88,021 | `temperature` | 123,948 / 88,021 |
| DC-003 Precipitation | 84,926 / 61,190 | `hydrology` | 124,314 / 84,437 |
| DC-004 Wind Speed | 27,498 / 17,394 | `wind` | 58,320 / 38,833 |
| DC-005 Consecutive Days with No Precipitation | 6,981 / 4,946 | `dry_spell` | 7,351 / 5,267 |
| DC-006 Degree Days (HDD/CDD) | 3,076 / 2,638 | `temperature` | 143,266 / 101,847 |
| DC-007 Fire Weather Index | 548 / 395 | `fire_risk` | 4,465 / 3,044 |
| DC-008 Calculating FWI Classes | 551 / 396 | `fire_danger` | 4,323 / 2,942 |
| DC-009 Summer daily maximum heat index | 0 / 0 | `heat_index` | 15,749 / 11,719 |
| DC-010 Summer seasonal maximum heat index | 1 / 1 | `heat_index` | 15,731 / 11,704 |
| DC-011 … above 95 F | --- / --- | `extreme_heat_days` | 3,335 / 2,985 |
| DC-012 … above 105 F | 0 / 0 | `extreme_heat_days` | 2,681 / 2,397 |
| DC-013 … above 115 F | --- / --- | `heat_wave_days` | 3,347 / 2,996 |
| DC-014 … above 125 F | 2 / 2 | `extreme_heat_days` | 2,686 / 2,402 |

**Forms and normalization:** prompt F asked for up to 8 forms; the model returned
8 for every concept --- **112 forms, 112 searched, 0 recorded over the 10-term
cap, 0 dropped. No normalization rule fired** (every `rules_applied` is empty;
no form contained `>`, `<`, `°` or `%`). Per-term counts for every searched form:
[`docs/CONCEPT_COVERAGE_SURVEY.md`](../../docs/CONCEPT_COVERAGE_SURVEY.md), run-2
section. Findings 1--5 there; the three-level finding is §13.

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

**Run 2:** Driver v4 tests (at `3ccb4ba`): `tests/test_survey_driver_v4.py` (mock server, synthetic index):
byte-identity with v3 (mutation-checked: perturbing one measure field fails
it); JSON-object parsing, reasoning fallback, last object wins; `status:
candidate_family`; normalization recorded (`days with heat index above 95°f`
searched as `days with heat index above 95 degrees f`, `N-3`, original kept;
`100%` → `100 percent`, `N-7`); 6/10 limits; side-by-side counts and table;
restart; error row with the measure kept; `--normalize` in measure mode; the
three context-cache mismatches in both modes; run-1 mismatch; tampered table.
`coveragesurvey.verify_source` now checks the v3 tools as committed at
`2331e19`, since the working-tree driver is v4. Scanner allowlist re-pinned to
the v4 hash.

`tests/test_survey_run2.py` (11): run 1 untouched (run-1 `manifest.csv` =
`74ba7d7c…125d`, its copy re-hashes); run-2 copy = its `manifest.csv`, pinned under
`diagnostics` not `external_corpora`; no `topical/hits.csv` copied (14 listed);
log START fields; every row re-verifies and equals the side-by-side table;
every family `candidate_family`; 112 / 112 / 0 / 0 forms, no rule fired; each
computed statement (findings 1--5); doc regenerates byte for byte; no candidate
family enters `concept_map.yaml`. `verify_run` mutation-checked outside the repo:
a changed family count, measure count, run-1 row SHA-256 or
`candidate_family_status` each fails it. Full suite: **1019 passed** (0 skipped, raw-data hash gate active).
Scanner: **0 hits** (885 tracked text files, every new file staged).

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

**Run 2:** (i) login node, conda environment and Python version not recorded in
any run-2 output; (ii) **no normalization rule fired**, so N-1 … N-7 were
exercised only by the tests, never on real output; (iii) prompt F asked for at
most 8 forms, so the 10-term cap never bound; (iv) no hit offsets
(`--no-hits`); (v) several families are much broader than their measure
(findings 2--4) --- their counts describe the proposed forms, not the measure;
(vi) DC-001's family count (123,948) is below its run-1 measure count (124,420):
the run-1 terms included `mat` and others not proposed in run 2; (vii) no place
filter; R-FWI-1 not relevant (no bare `fwi` among the family forms).

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

**Run-2 driver (v4) --- choices the work package left open, disclosed for the COORDINATOR:**

1. **Normalization in measure mode is opt-in (`--normalize`).** The package asks
   both that measure mode reproduce v3 *exactly* and that normalization apply in
   measure mode; with normalization always on, measure outputs could not be
   byte-identical (`95°f` would become searchable). Default = v3; `--normalize`
   applies the table, with the same records and limits as family mode. Run 2
   does not run measure mode, so no run-2 count depends on this.
2. **Word limits: 10 for a form a rule changed, 6 otherwise** (as directed; the
   ruling sets no limit), recorded in each `row.json` as
   `sanitizer_word_limits`. Effect, observed on the run-1 terms: of the 26
   dropped terms the table makes plain, **all 26** pass at 10 words, against 7
   at 6. Dictionary names are not normalized (not model-proposed).
3. **The 60-character bound** is unchanged but, in the v4 path only, a form over
   it is reported as "longer than 60 characters" rather than "not a plain
   lowercase phrase"; forms past the 10-term cap are recorded, not silently cut.
4. **Reply parsing:** the *last* JSON object with a `candidate_family` key in the
   content or reasoning field is taken (a reasoning field may hold drafts). The
   family name is stored as returned, never edited; the forms are what is searched.
5. **Polaris invocation keeps run 1's relative paths.** The package says
   `PYTHONPATH=src`; the docstring runs from `$LITCOLLECT_ROOT_POLARIS` with
   `PYTHONPATH="$CLIMRR_REPO/src"`, so `index/…` and `survey/run2` stay relative
   and no absolute Eagle path lands in any `summary.json` or the log (run 1's
   convention, and what the scanner needs at ingest). `$CLIMRR_REPO` must be a
   checkout of the pinned commit, so the branch has to reach Polaris first.

**Run-2 ingest --- EXECUTOR choices and corrections, for review:**

- **Statement (2), heat index.** The work package attributes `apparent
  temperature`, `heat stress`, `humid heat` (15,749) to "the heat-index
  measures". That is DC-009's list; **DC-010's `heat_index` forms do not include
  `humid heat`** (15,731; it has `heat stress index` instead). Stated per concept.
- **Statement (3), "excluded from production vocabulary".** None of `wildfire
  risk`, `fire hazard`, `fire danger`, `fire risk` is a `concept_map.yaml` term,
  and D-021 (2026-10-12) restricts collection to approved concept-map family
  vocabulary. But **`fire danger` does occur in the frozen v1 fire query --- in
  its context group**, not as a topical term (and is removed from the survey
  context clause). The doc says this rather than "excluded" without
  qualification.
- **Statement (4), "hot days", "warm days".** `hot days` (2,333) is a form in all
  four threshold rows; **`warm days` (854) only in DC-011 and DC-013**.
- **Statement (5), level 2.** "fire weather index 548" is the LITCORPUS-02 fire
  diagnostic's **family group** (five approved terms) before R-FWI-1 (473 after;
  `fire weather index` alone 462); "heat index 1,080" is the term alone (group
  1,082). The doc gives both.
- **Mentor brief, concept-map counts.** Only two of the seven discussion
  families have a concept-map entry (`fire_weather_index`, `heat_index`); the
  other five have no concept-map term and so no concept-map count. The brief
  says so and keeps their run-1 measure counts, labelled; it shows no
  model-family total.
- `scripts/ingest_survey_run1.py` now regenerates the two-run doc once run 2 is
  ingested (otherwise a rerun would drop the run-2 section); run-1 output and
  copy unchanged. `render_doc` without a run-2 section is byte-identical to before
  (checked).
- Run-2 `RUN_FACTS` records host / environment / Python as not recorded, rather
  than copying run 1's.
- `_context/hits.csv` kept (header-only, 79 bytes), as in run 1.

## 13. Open decisions and mentor questions

**Finding of run 2 --- three coverage levels are distinguishable** (computed,
`docs/CONCEPT_COVERAGE_SURVEY.md`, finding 5):

| Level | Searched | Documents (topical-only) |
| --- | --- | --- |
| Measure-level phrases (run 1) | the measure's own wording; heat-index measures DC-009--014 | **0--2** |
| Concept-map family terms (LITCORPUS-02 diagnostics) | approved terms of the only two concept-map families | fire weather index group **548** (473 after R-FWI-1); `heat index` **1,080** (group 1,082) |
| Model-proposed broad families (run 2) | `candidate_family` forms | **2,681 -- 143,266** |

Only the middle level rests on governed vocabulary. The third is a model
hypothesis, often broader than the dictionary concept (precipitation →
`hydrology` with `moisture`, `water cycle`; degree days → `temperature` with
`heat`, `cold`, `warming`; FWI → `fire_risk` / `fire_danger` from non-concept-map
terms; thresholds → `extreme_heat_days` / `heat_wave_days` resting on `hot days`).
**No family count is attributed to a measure.**

| Item | Owner | Blocks |
| --- | --- | --- |
| Does GUIDANCE accept run 2 as diagnostic, and the three-level reading as the way to report coverage? | GUIDANCE | any use of run-2 counts |
| Should any `candidate_family` be considered for concept-map governance (none is proposed here)? | GUIDANCE / Kaiyuan | nothing now |
| The statement (2)--(5) corrections in §12 | COORDINATOR | the wording of the brief |
*Carried from run 1:*

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

**Run 2 --- as proposed for review** (D-027 acceptance criteria, verbatim):

| Criterion (D-027 ruling, verbatim) | Status | Evidence |
| --- | --- | --- |
| 15. Stage-2 run 2 preserves run 1 unchanged. | **MET** | run-1 `manifest.csv` `74ba7d7c…125d` unchanged; copy re-hashes (`test_survey_run2.py`, `test_survey_run1.py`) |
| 16. Every proposed family is `candidate_family`. | **MET** | 14/14 `family.json` and rows (test) |
| 17. Candidate-family provenance includes model/prompt/date. | **MET** | `model_id`, `endpoint`, `prompt_sha256` (= `prompt.txt`), `date` in every `family.json` |
| 18. Original model-proposed forms are retained. | **MET** | `original` per form, 112/112 |
| 19. Normalized forms carry deterministic transform-rule provenance. | **MET (vacuous on this run)** | `rules_applied` per form; **no rule fired** (all empty) |
| 20. Only `>`, `<`, degree notation, and `%` receive authorized normalization. | **MET** | frozen table `80a5e0e3…6e03`, hash-verified; 0 forms changed |
| 21. No semantic synonym generation occurs during normalization. | **MET** | normalized == original for all 112 |
| 22. Threshold-measure coverage remains separately reported. | **MET** | measure columns copied from run 1 beside family columns |
| 23. Family coverage is not attributed to a threshold measure. | **MET** | label on every row; doc finding 4 |
| 24. The seven discussion families are not automatically approved as benchmark families. | **MET** | mentor brief: discussion candidates, concept-map counts only |
| 27. No M1 column status changes. | **MET** | none |
| 28. Index 117 remains unlabeled. | **MET** | not referenced |
| 29. No QA is generated. | **MET** | none |

**Proposed: Stage 2 run 2 EXECUTED AND INGESTED (diagnostic), for GUIDANCE review.**

## 15. Next bounded objective

**GUIDANCE review of Stage 2 run 2** (diagnostic), on `work/trackb-run2` at the
head commit reported to the COORDINATOR (not pushed, not merged; Kaiyuan pushes
for review and performs any merge). For review: §9 (side by side), §13 (the
three-level finding), §12 (the driver choices and the statement corrections),
§14 (criteria 15--24, 27--29). **QA not authorized.** Nothing touches
`concept_map.yaml`, M1 statuses, index 117, production queries, C-2 or
compatibility; no `candidate_family` is proposed for governance.
