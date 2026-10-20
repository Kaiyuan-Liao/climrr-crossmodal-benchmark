# Track B / Stage 2 --- dictionary-grounded concept coverage survey (diagnostic)

Authorized by [`docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md`](../../docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md)
(D-025, Track B, Stage 2a--2c **as diagnostics**; criteria 23--31). **No paper
was read. No QA. Nothing here changes `concept_map.yaml`, any column status, or
index 117.**

## 1. Milestone ID and title

**Track B / Stage 2a --- dictionary concept inventory + survey tooling.** Stage
2b/2c (candidate surface forms; yield survey) are **to be executed by Kaiyuan on
Polaris with the pinned driver; results arrive as `survey_table.csv` +
per-concept folders.** M1 remains open (D-014). Track A (M4-WP4) runs separately.

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
| **`scripts/litcollect/survey_driver.py`** (as tracked) | **`b3292e22f067f6f2388e1233ec17b521c753d6d955e54b67751798c98f340d3a`** | byte-identical to the tarball member; matches the work package |
| `scripts/litcollect/probe_alcf_inference.py` (as tracked) | `79181c48981c709b49b90d78fc8aaddffaf12d2f1bb0591b9a9daa3aad438c66` | byte-identical to the tarball member |

`data/raw/FullData.csv` was verified by `pytest` (hash gate) and **not read** by
any Stage 2a code.

## 5. Environment and execution location

Local (`location: local`), conda env `climrr`, Python 3.11.16, macOS arm64,
pinned D-007 libraries (pypdf 6.18.0, PyYAML 6.0.3); DuckDB 1.5.4 for the
synthetic-index tests. Run record:
`reports/runs/20261020T175937Z_local_build_dictionary_inventory.{json,md}`.
**Sophia not involved; Polaris not involved yet** (2b/2c pending).

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

## 7. Deliverables and exact file paths

`src/climrr/dictconcepts.py` · `scripts/build_dictionary_inventory.py` ·
`data/metadata/dictionary_concepts.yaml` · `docs/DICTIONARY_CONCEPTS.md` ·
`data/metadata/litcollect/survey_context_clause_v1.txt` ·
`scripts/litcollect/survey_driver.py` · `scripts/litcollect/probe_alcf_inference.py` ·
`tests/test_dictconcepts.py` · `tests/test_survey_driver.py` ·
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

**Driver behaviour on this inventory (observed, logic unchanged):**

| Concepts | Dictionary name through the sanitizer |
| --- | --- |
| DC-003, 004, 005, 007, 008, 009, 010 | **kept** as the first candidate |
| DC-001, 002, 006 | **dropped** --- "not a plain lowercase phrase" (parentheses) |
| DC-011--014 | **dropped** --- "more than 6 words" |

Stage 2b/2c: **PENDING --- Kaiyuan, Polaris**: `survey_table.csv` plus
`<out>/DC-NNN/` (prompt, response, candidates, topical run, row) and `survey.log`.

## 10. Validation performed

- `pytest`: **883 passed** (851 before + 16 `test_dictconcepts.py` + 13
  `test_survey_driver.py` + 3 `test_secrets_scan.py`). The new tests cover: re-slicing of passages and names
  from the page text (hash-checked); verbatim units/threshold/scenario; ids
  unique and contiguous; `family_hint` null; `verified_columns` ⊂ the 21
  verified; manifest pin; byte-identical rebuild; status counts unchanged. For
  the driver: reasoning-field fallback; sanitizer (non-plain, >6 words,
  duplicates, cap 10); dictionary name first; restart skips completed concepts;
  `context_filtered_count == |topical ∩ context|`; every `candidates.json`
  `candidate_surface_form` with model, endpoint, prompt SHA-256 and date; tool
  pins.
- `scripts/verify_no_secrets_or_paths.py`, run with every new file staged (the scan
  reads only tracked/staged files): **zero hits** --- after the hash-pinned
  exemption below; before it, 12 credential-word hits in the two delivered tools
  and 1 in my test (fixed with string fragments).

## 11. Failures, rejected cases, and known limitations

- **7 of 14 dictionary names never reach the query** (table above). The four
  threshold concepts also share one passage, so the name is the only thing in
  the prompt that tells them apart --- and it is dropped. Their candidate sets
  will rest on the model alone.
- **A concept whose candidates are all dropped aborts the run.** With no kept
  term the driver writes `(  )`; `run_query.parse` refuses it; the driver does
  not catch the `RuntimeError`. Possible on a model error for DC-001/002/006/
  011--014. A rerun resumes after the completed concepts but repeats the failing one.
- **`\b` and trailing `%` / `°`.** The sanitizer admits `%` and `°`, but
  `run_query.py` wraps every term in `\b…\b`, so a term ending in one of them
  almost never matches.
- **No run record from the driver or the probe.** Both are outside the CLAUDE.md
  run-record exemption list (M4-WP3) and must not be modified here; their
  `survey.log`, `row.json` and `probe_alcf_inference.json` are the evidence.
- Passage windows are EXECUTOR choices (verbatim, but the start and end are judgement).

## 12. Deviations from the approved plan

- **Escalation, not improvisation:** the granularity was put to Kaiyuan before
  any inventory was written (D-026).
- The inventory adds a `name_source` field (page + span of the name) beyond the
  work package's schema, so names are checkable like passages.
- The context clause file ends with a trailing LF (as the frozen query files do).
- **Scanner exemption (owner decision, D-026).** The two delivered tools trip the
  credential-word rule 12 times (the access env var names, a
  parameter, the Bearer header --- no value). CLAUDE.md requires a stop; escalated to
  Kaiyuan, who chose a **hash-pinned allowlist** in `verify_no_secrets_or_paths.py`:
  those two paths only, the credential-word rule only, and only while each file's
  SHA-256 equals the pinned value. A governance change to the guard, for
  COORDINATOR/GUIDANCE review.
- Report fields 10--15 completed, since the template forbids omitting fields.

## 13. Open decisions and mentor questions

| Item | Owner | Blocks |
| --- | --- | --- |
| Confirm D-026 (measure level) | COORDINATOR / GUIDANCE | the frozen ids |
| Confirm the hash-pinned scanner exemption (D-026) | COORDINATOR / GUIDANCE | nothing now; a revised driver needs a new pin |
| Driver: dropped names and empty-candidate abort --- accept, or issue a revised driver before the Polaris run | COORDINATOR | the Stage 2b/2c run |
| Extend the run-record exemption to `survey_driver.py` and `probe_alcf_inference.py` | COORDINATOR | nothing now |
| Q22 (705k filter) stays open | JL | nothing here |

## 14. Proposed gate status

| Criterion (D-025 ruling, verbatim) | Status | Evidence |
| --- | --- | --- |
| 23. Stage 2a contains only dictionary-described concepts/metrics. | **MET** | every entry has a page-sliced passage; `tests/test_dictconcepts.py` |
| 24. Stage 2a does not change existing column statuses. | **MET** | status counts 21/20/130/28/76 unchanged (test) |
| 25. Index 117 remains unlabeled. | **MET** | not referenced (test); statement in YAML and doc |
| 26. Stage 2b outputs are explicitly `candidate_surface_form`. | **MET (tooling)** | driver + test; real run PENDING |
| 27. Stage 2b records model and prompt provenance. | **MET (tooling)** | test; real run PENDING |
| 28. Stage 2b vocabulary never enters production automatically. | **MET** | `BRIDGE_ELIGIBILITY.md` §7; test |
| 29. Stage 2c is deterministic and restartable. | **MET (tooling)** | restart test; caveat §11 (abort on empty candidates) |
| 30. Stage 2c counts are labeled diagnostics, not literature-prevalence estimates. | **MET (tooling)** | `row.json` label (test); docs |
| 31. Literature yield does not automatically determine unit selection. | **MET** | no code reads survey output |
| 33. No QA is generated. | **MET** | none |

**Proposed: Stage 2a COMPLETE; Stage 2b/2c READY TO RUN, subject to the
COORDINATOR's call on the §11 driver behaviour.**

## 15. Proposed next bounded objective

Kaiyuan runs `survey_driver.py` (pinned SHA-256 `b3292e22…0d3a`) on Polaris over
the frozen LITCORPUS-02 source index with `dictionary_concepts.yaml` and
`survey_context_clause_v1.txt`, and returns `survey_table.csv` and the 14
per-concept folders for a diagnostic review.
