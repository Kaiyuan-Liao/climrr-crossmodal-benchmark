# Track C --- soft-QA candidate schema, review protocol and agent (pre-run)

Authorized by the GUIDANCE guardrail ruling of 2026-10-27,
[`docs/TRACKC_TRACKD_SOFT_QA_GUARDRAILS_RULING.md`](../../docs/TRACKC_TRACKD_SOFT_QA_GUARDRAILS_RULING.md)
(**D-033**), under the mentor direction D-029 / D-030. **No model call was made.
No QA was generated. No column status, concept-map entry or compatibility rule
changed; index 117 stays unlabeled.** Fields 10--15 wait for the Polaris run.

## 1. Milestone ID and title

**Track C pre-run --- soft-QA candidate schema v1, review protocol v1, Track C
inputs, agent tracked.** Track D: design pending. M1 remains open (D-014).

## 2. Objective

Freeze, **before any generation run**, (a) the soft-QA candidate record schema
the ruling defines; (b) the human-review protocol, reviewer form and an
evidence-first reviewer view; (c) the Track C agent's inputs --- unit
definitions without values, the six candidate QA types, the 100 + 143 paper
list; and (d) track the delivered agent byte-identical, tested against a mock
endpoint. **Excluded:** running the agent, generating or reviewing any QA,
computing any table-side value, Track D design, merging, pushing.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/meeting-2026-10-22`, from head `9e16391` |
| **Freeze commit** | **`4fb887f`** --- schema, protocol, form, view, inputs, agent, tests, D-033, manifest pins. **Schema v1 and protocol v1 are frozen at `4fb887f`.** |
| Report commit | `12145e0` (this report, fields 1--9, and the `PROJECT_STATE.md` refresh) |
| Follow-up commit | the commit carrying the COORDINATOR's decisions (D-033 addendum) and the re-pinned units file (head SHA reported to the COORDINATOR). The schema, protocol, QA types, candidate list and agent are unchanged since `4fb887f` |
| Run-1 ingest commit | the commit carrying run 1's ingest, review batch 01, agent v2 and the FWI hold (head SHA reported to the COORDINATOR); fields 10--15 below |
| Remote | **not pushed, not merged** |

## 4. Data version and checksums

| Object | SHA-256 | Bytes | Notes |
| --- | --- | --- | --- |
| `docs/TRACKC_TRACKD_SOFT_QA_GUARDRAILS_RULING.md` | `1d1b3bb8faebb3fd477624b54eca643ec641caec66740c02464a8a1f31937d39` | | verbatim copy; equals the delivered file |
| **`data/metadata/softqa/candidate_schema_v1.json`** | **`6a62e3e10fde1ce2aa10b1b4c1baa8be14c7815afaa0f8e97349e02d47414d0b`** | 19,876 | pinned in `data/manifest.json`; `-text` |
| **`data/metadata/softqa/units_definitions_v1.json`** | **`0cf496a1854933cf96ebc9ef06c59ba29a15691bba574d87dd760f70019f282e`** | 3,650 | pinned; `-text`; UTF-8 (°). **Re-pinned in the follow-up** (P-STATE-1 names its metric); was `61e4c7fe…7c82`, 3,651 bytes, at `4fb887f` |
| **`data/metadata/softqa/qa_types_v1.json`** | **`bc425268fc9fc56a5727b80286a8402fb011c1a2817f4d880c2e7206df3e567d`** | 2,261 | pinned; `-text` |
| **`data/metadata/softqa/trackc_candidates_v1.json`** | **`6fb9c911acb07f4798fea90332be389a9327351174038167849a02daff23c943`** | 13,036 | pinned; `-text`; 243 records |
| `data/metadata/softqa/review_form_v1.yaml` | `804bd3c0f8344f24b3126cff4a1fe916ad0538c0c034cb289b1c9f1ad2eb3790` | 1,781 | pinned; `-text` |
| **`scripts/litcollect/softqa_agent.py`** (as tracked) | **`159e2c5c4f00608da37b1bc85556fecfd82dbd2e1a5abfd10c59a2e46061397c`** | 18,552 | byte-identical to the delivered file (work package hash); scanner word exemption pinned to it |
| `docs/SOFTQA_REVIEW_PROTOCOL.md` | `ab54f305fce942d092d486146c1779d82e0477cc9043f6e19450a04d61087a72` | | |
| **`scripts/litcollect/softqa_agent.py` v2** (run-1 ingest commit) | **`25a79a5b8bebbb67c8e080b05d08b736ee40ea62fbe3fc891d86cfab22f63b9c`** | | byte-identical to the delivered v2; scanner exemption re-pinned; v1 `159e2c5c…397c` ran run 1 |
| `docs/SOFTQA_REVIEW_PROTOCOL.md` (run-1 ingest commit) | `1fff24129b0f5db296b13f06a7ecf09049fa4ee097700ca2f539f6ecab089023` | | §3 v2 locator note and §11 FWI hold added (*implementation*); ruling text unchanged |
| **run 1 `artifacts/softqa/run1/manifest.csv`** | **`c0c193695023d08435e4fed0451f4ef445aa429f68bb43780ab638bd5b26b3d9`** | 3,789,681 (248 files) | `data/manifest.json` → `diagnostics` / `softqa_run1` |
| `softqa_run1.tar.gz` (delivered) | `8a0e444996cc09a87c848aa9013e228d39a3f831e7a701519eb7db41f3654e3e` | | not stored |
| `artifacts/softqa/run1_locator_replay_v2.json` | `33bc04949b8e24d11e48c128725b4a8e5d376cc16d62295afb672f5be7056898` | | pinned in the `softqa_run1` entry |
| **`artifacts/softqa/review_batch_01.json`** | **`1086991e25306ee19b7ba29102123fe516f670edd6524e8b1970102a7058f9c8`** | | `data/manifest.json` → `files`; 11 records |
| `fire_weather_v1_place_candidates.txt` (read) | `122ee177f45dd98ecb76765a7ce0e8c543261694c5e991380ab94139d756a149` | | equals `place_candidates.json`; checked by the freeze script |
| `extreme_heat_v1_place_candidates.txt` (read) | `eb28845e43bbd63875a8ac7b25f64fef9aabb07abde69a7ae75e14bb689c623c` | | idem |

`data/raw/FullData.csv` was not read by this package (no table value is
computed); its manifest hash test passed in the gate run.

## 5. Environment and execution location

| | |
| --- | --- |
| Host | local (Mac), location label `local` |
| Python | 3.11.16, conda env `climrr` (the README's environment); pins satisfied |
| pip freeze | `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51` |
| duckdb | 1.5.4 (agent tests) |
| Run record | `reports/runs/20261027T234505Z_local_freeze_trackc_candidates.{json,md}` --- **`git_dirty: true`** (the freeze ran before the freeze commit; the output equals the committed file, tested) |

A first freeze run used the conda **base** interpreter by mistake (pandas
2.1.4); its run record was deleted before any commit and the freeze re-run in
`climrr`, producing a byte-identical file.

## 6. Work completed

- **Phase A.** Ruling tracked and added to `KNOWLEDGE_FILES`; `PROJECT_STATE.md`
  GUIDANCE dates filled (notice 2026-10-27, ruling 2026-10-27); **D-033** logged
  (decision table verbatim, validity chain, review counts, visibility,
  "query-only use is still semantic use", C/G/T/S/D audit-not-gate, lifecycle).
- **Phase B.** `candidate_schema_v1.json` (JSON Schema 2020-12) and
  `src/climrr/softqa.py`: `load_schema`, `schema_errors` (built-in validator for
  the subset of JSON Schema used), `consistency_errors` (lifecycle rules),
  `validate`, `map_trackc`, `map_and_validate_jsonl`.
- **Phase C.** `docs/SOFTQA_REVIEW_PROTOCOL.md` (ruling text verbatim, EXECUTOR
  additions marked *implementation*); `review_form_v1.yaml`;
  `scripts/softqa_review_view.py`.
- **Phase D.** The three input files, the candidate list built by
  `scripts/freeze_trackc_candidates.py`; all hash-pinned.
- **Phase E.** Agent copied unchanged; scanner exemption; run-record exemption
  in `CLAUDE.md`; 13 end-to-end tests against a mock endpoint.
- **Phase F.** `BRIDGE_ELIGIBILITY.md` §10; `PROJECT_STATE.md`; this report.

## 7. Deliverables and exact file paths

`docs/TRACKC_TRACKD_SOFT_QA_GUARDRAILS_RULING.md`, `docs/SOFTQA_REVIEW_PROTOCOL.md`,
`docs/DECISION_LOG.md` (D-033), `docs/BRIDGE_ELIGIBILITY.md` (§10),
`docs/PROJECT_STATE.md`, `data/metadata/softqa/{candidate_schema_v1.json,
review_form_v1.yaml, units_definitions_v1.json, qa_types_v1.json,
trackc_candidates_v1.json}`, `data/manifest.json` (5 entries + 1 amendment),
`.gitattributes`, `src/climrr/softqa.py`, `scripts/softqa_review_view.py`,
`scripts/freeze_trackc_candidates.py`, `scripts/litcollect/softqa_agent.py`,
`scripts/verify_no_secrets_or_paths.py`, `scripts/stage_knowledge.py`,
`CLAUDE.md`, `tests/test_softqa.py`, `tests/test_softqa_agent.py`,
`tests/test_secrets_scan.py`, the run record in §5, this report.

## 8. Methods and rules that affect scientific meaning

No data rule was applied: nothing was filtered, aggregated, converted or
renamed, and no table value was read. The rules below shape what the agent and
the reviewer will see, and are put to the COORDINATOR.

1. **Unit definitions carry no computed number and no direction** (tested:
   only years, `R106C361`, `RCP8.5`, unit ids, version labels and the P-STATE-1
   threshold `105 °F` contain digits; none of *value / increase / decrease /
   change by*). Every FWI definition says "not
   fire occurrence"; every historical window is "modeled historical baseline".
2. **P-STATE-1 names its metric** (follow-up, COORDINATOR): "The number of
   summer days with daily maximum heat index above 105 °F, over the ClimRR rows
   labelled State California, comparing the modeled historical baseline
   1995-2004 with the modeled end-century decade 2085-2094 under RCP8.5." The
   threshold is the metric's name and is allowed; no computed value, no
   direction. *At `4fb887f` the definition was family-level only ("the summer
   heat index, with the exact ClimRR metric kept as provenance"), which risked
   links to heat-index passages not about threshold days; superseded.*
3. **Family surface terms** = the concept map's `approved_lexical` terms (FWI:
   5; heat index: 2), `extended heat index` excluded (tested against
   `concept_map.yaml`). Place terms: `oklahoma`, `stephens` (P-COUNTY-1),
   `california` (P-STATE-1), none for P-CELL-1, F-FWI, F-HEAT.
4. **QA-type descriptions are EXECUTOR-worded** from Kaiyuan's type names,
   except `cross_location_comparison` (the work package's sentence). All six
   are marked "candidate QA type, not yet validated".
5. **Judgment vocabulary `yes / no / unclear`** for checklist items 1--9 and
   `adjudication_status ∈ {not_required, pending, resolved}` are EXECUTOR
   choices; the ruling names the judgments, not their values.

## 9. Results with compact tables or examples

**Schema.** 7 groups / 76 fields, exactly the ruling's (tested group by group,
in order). `status` = the 9-value lifecycle. `table_values_visible_to_generator`
and `answer_visible_to_generator` are the constant `false`; a record with
either `true` fails validation. Table-side and human-review fields are all
nullable.

**Inputs.**

| File | Content |
| --- | --- |
| units | P-CELL-1, P-COUNTY-1, P-STATE-1 (v2), F-FWI, F-HEAT |
| QA types | 6 candidates, none validated |
| candidates | 243 = `fire_weather_v1` 100 + `extreme_heat_v1` 143; no item in both arms; list order |

**The 20 already-read papers stay in** (M4-WP4 sample; listed in
`data/manifest.json` → `trackc_candidates_v1.json` → `already_read_m4_wp4`):
fire `LIT2-000185, 000366, 000499, 000560, 000673, 000786, 001063, 001157,
001236, 001308`; heat `LIT2-000084, 000203, 000315, 000470, 000662, 000803,
000927, 001075, 001160, 001293`. `LIT2-001075` is also LITCORPUS-00
`LIT-001536`, read in M4-WP2.

**Agent behaviour under test (mock endpoint, synthetic index, tracked inputs).**

| Case | Status |
| --- | --- |
| exact passage, P-COUNTY-1, `same`, paper names Oklahoma | `deterministic_pass`, span `[start,end)` exact |
| fabricated passage | `rejected_pre_review`, `span_reslice_pass` false |
| unknown unit id / unknown QA type | `rejected_pre_review` |
| P-COUNTY-1 `same`, paper without oklahoma/stephens | `rejected_pre_review` |
| P-COUNTY-1 `different`, paper's own place `study_area` / `affiliation` | pass / reject |
| F-FWI (no place terms), `unknown` | `deterministic_pass` |
| units file with a `value` field | refused at startup, no model call |
| restart | finished paper skipped, its `result.json` unchanged |
| `candidates.jsonl` → schema | 8 / 8 map and validate |

**Polaris invocation** (also in `src/climrr/softqa.py`):

```bash
cd "$LITCOLLECT_ROOT_POLARIS"
PYTHONPATH="$CLIMRR_REPO/src" python "$CLIMRR_REPO/scripts/litcollect/softqa_agent.py" \
    --candidates "$CLIMRR_REPO/data/metadata/softqa/trackc_candidates_v1.json" \
    --units "$CLIMRR_REPO/data/metadata/softqa/units_definitions_v1.json" \
    --qa-types "$CLIMRR_REPO/data/metadata/softqa/qa_types_v1.json" \
    --index index/full_705k_v2_filtered --out softqa/run1 \
    --source-commit "$(git -C "$CLIMRR_REPO" rev-parse HEAD)"
```

**COORDINATOR decisions (2026-10-27, follow-up; D-033 addendum)** on the items
below:

- **(a) accepted:** concept/place term location anywhere in the paper stands as
  the pre-check; semantic adequacy of the occurrence is the reviewer's judgment.
- **(b) decided:** P-CELL-1 and P-COUNTY-1 candidates may be proposed and
  reviewed but **cannot reach `accepted` / `accepted_after_edit` until the FWI
  column meanings (IC-006, IC-008, IC-010) are owner-confirmed** --- now the
  first question in `docs/MENTOR_BRIEF.md`.
- **(e) accepted:** the invocation in `src/climrr/softqa.py`'s docstring is fine.
- **P-STATE-1's definition** now names its metric (field 8, item 2).
- (c), (d), (f), (g): no decision recorded; they stand as disclosed.

**As found before the run (pre-decision wording kept for the record):**

- **(a) Term location is paper-wide.** The agent locates concept and place
  terms anywhere in the paper; the earlier §10 wording said "in the passage".
  With `stephens` (a common surname, D-027) and case-insensitive bare `FWI`
  (R-FWI-1; "fractional water index" in M4-WP2), a `same` candidate can pass the
  place or concept check on an unrelated occurrence. §10 now states what the
  agent does and flags the difference.
- **(b) Verified-columns check vs the FWI units.** P-CELL-1 and P-COUNTY-1 rest
  on `wildfire_summer_*` columns that are `inferred_candidate` (D-014). The
  ruling authorizes the three unit definitions for Track C, but its criterion 5
  ("all table columns are authorized for their semantic role") will make
  `verified_columns_only` false for them at the table stage unless that
  authorization is recorded as covering them.
- **(c) The agent's re-slice is against the index section text**, which
  `build_index.py` stores exactly as decoded from the source JSON. The table
  stage should re-slice once more against the source file itself.
- **(d) "Exactly the ruling's field groups"**: kept field for field; two
  supplementary top-level blocks were added outside them --- `agent_record`
  (the agent's output verbatim, which holds the example question and confidence
  the review order needs and keeps the LLM proposal separate from the frozen
  final QA, criterion 33) and `mapping` (pending stages; refused agent values).
- **(e) "Document the Polaris invocation in the module docstring"** conflicts
  with "copy unchanged": it is in `src/climrr/softqa.py` and the test module.
- **(f) The review view writes a run record per view** (the CLAUDE.md rule; it
  also evidences whether the rationale was shown). Many views mean many records.
- **(g) Built-in validator.** `jsonschema` is not a pinned dependency, so
  `softqa.py` validates without it; its two cross-check tests skip in the
  pinned env and pass where `jsonschema` is installed (conda base, 4.19.2).

## 10. Validation performed

**Run 1 (agent v1, Polaris, 2026-10-28 03:27:59--03:40:48 Z, at `95e1ec8`).** Ingest:
`scripts/ingest_softqa_run1.py`; record
`reports/runs/20261028T041213Z_local_ingest_softqa_run1.{json,md}`. Generated doc:
[`docs/SOFTQA_TRACKC_RUN1.md`](../../docs/SOFTQA_TRACKC_RUN1.md).

| Check | Result |
| --- | --- |
| tarball SHA-256 | `8a0e4449…3e3e`, matches the work package |
| log START line | `candidates=243 units=5 qa_types=6 model=gpt-oss-120b units_sha=5bb486ef6428 qa_sha=f0d0f07bf0fd system_sha=f2e493e179aa index=fbb4affb7162` --- every pin recomputed |
| units hash | **as loaded** `5bb486ef642825f318a60b47c2a9ed093c5d5b6ad8160169e4f72e7f500b1b92` = SHA-256 of `json.dumps(units, sort_keys=True)` of the tracked file; **file** `0cf496a1…282e`. The agent hashes the canonical dump, so the two differ by construction; both recorded |
| QA-types hash | as loaded `f0d0f07bf0fdefccc78e4778a5721b49fa8bbed8c0e2686fa952155a7e187e75`; file `bc425268…567d` |
| system prompt | `f2e493e179aa3619c8389e5c1756cce8f9a13693ddd586eae59138de33ee54f5` = v1's `SYSTEM_PROMPT` (every record) |
| index | `fbb4affb…7a94` = LITCORPUS-02 content identity |
| source commit | `95e1ec851f2ac703654df52ac1ccc9c3d777fcd7` on all 193 records |
| logs | `agent.log` = `reports/softqa_run1.log`, byte-identical; 243 paper lines + START + DONE |
| re-derivation | `candidates.jsonl` and `summary.json` rebuilt from the 243 `result.json` (agent's own aggregation) --- equal; DONE totals equal |
| paper set | 243 directories = `trackc_candidates_v1.json` |
| schema mapping | **193 / 193** map onto `candidate_schema_v1.json` and validate (`candidates_schema.jsonl`); table-side and human-review null with stage named |
| not copied | 486 files (`prompt_user.txt`, `response.json` × 243) --- SHA-256 in `excluded_files.csv` |
| rerun | ingest → replay → freeze re-run from scratch: byte-identical outputs |

**Locator replay** (`scripts/softqa_replay_locator.py`, record
`reports/runs/20261028T041215Z_local_softqa_replay_locator.{json,md}`): agent v2's
`locate_passage` over all 193 proposals, sections rebuilt from `prompt_user.txt`
(243 prompt hashes matched; 222 untruncated papers reproduce `paper_chars` and
`n_sections`; the 16 untruncated papers held locally also equal their source JSON
section for section --- scratch check, not in the script). **117 exact (= v1's
passes), 8 normalized, 34 prefix_anchor, 34 not found**; 159 / 159 recovered spans
re-slice to their text.

**Gate (run-1 ingest commit).** `pytest` **1117 passed, 2 skipped** (the
`jsonschema` cross-checks, 9g) in conda `climrr`, Python 3.11.16, raw-data hash
test included; `verify_no_secrets_or_paths.py` 0 hits. Tests added: agent v2
(locator cases, passage type, > 3 groups, prompt hash, replay on the synthetic
run), run-1 ingest/counts/replay/batch, FWI hold.

## 11. Failures, rejected cases, and known limitations

| Run 1 | n |
| --- | --- |
| papers / proposals | 243 / 193 |
| papers with 0 proposals | **68** (1: 158, 2: 16, 3: 1) |
| `deterministic_pass` / `rejected_pre_review` | 103 / 90 |
| rejected on span re-slice (incl. combinations) | 76 |
| rejected on concept location (incl. combinations) | 9 |
| rejected on place location (incl. combinations) | **10** |
| advisory `question_has_no_table_number` false | 16 pass, 25 rejected |
| truncated papers / parse errors | 21 / 0 |

**Diagnosis of the 76 re-slice failures (replay):** 8 typographic variants
(U+2011 in all 8; curly quotes in 1; no U+202F found), 34 altered tails recovered
by prefix anchoring (≥ 0.6 word overlap), 34 not found in the text the model
saw. 11 of the 76 are in truncated papers, replayed against the 90,000 characters
shown (the model saw no more).

**Three work-package figures differ from the data** (recorded as computed, not
adjusted): (i) papers with 0 proposals **68**, not 50 (158×1 + 16×2 + 1×3 = 193);
(ii) place-check failures **10** incl. combinations, not 9 (8 alone, 1 with
concept, 1 with span); (iii) "42 altered tail" --- the replay gives **34**
prefix-anchor recoveries; 42 is the total recoverable (8 + 34). 8 + 34 + 34 = 76.

**Known limitations.** (a) 5 proposed passages exceed the prompt's 700
characters (737--797; one `deterministic_pass`, `C-239033445-01`): kept verbatim,
flagged against the minimal-window premise of the ingest. (b) v2's prefix anchor
measures overlap over the recovered sentence, so a genuine sentence followed by
an appended foreign one is recovered as the first sentence alone (tested,
documented); the reviewer sees both texts. (c) Replay `section_idx` is the
ordinal among string sections, not the index's. (d) The `question_has_no_table_number`
flag is crude (fires on thresholds quoted from the paper). (e) Run-1 host
login node and Python version not recorded in the outputs (`unknown`).

## 12. Deviations from the approved plan

- **9d--9g** still pending COORDINATOR review (unchanged).
- **`hold_owner_confirmation` is a gate result, not a schema status**: schema
  v1 is frozen, its `status` enum has no such value; `acceptance_gate` returns it
  and `validate` refuses an accepted record on a held unit (protocol §11). The
  unit-id hold is unconditional in code; lifting it needs a logged decision.
- **Review view extended** (batch input, v2 `passage_recovery` /
  `passage_as_proposed`, acceptance-gate line in section 2); **mapper v2** maps
  v2's `passage_type` to `claim_or_passage_type` (v1 records unchanged in
  content; mapper label now `softqa.map_trackc v2`).
- Diagnostic id spelled `softqa_run1` as the work package names it (Track B uses
  `TRACKB-SURVEY-RUN1`).
- Reviewer forms prepared with `candidate_id` and `reviewer_role: reviewer_1`
  only; not hash-pinned (they will be filled).

## 13. Open decisions and mentor questions

- **COORDINATOR:** the three work-package count discrepancies (field 11); the 5
  over-window passages; whether F-FWI candidates fall under the FWI hold before
  the table stage records their columns (now: checked by column ids only); 9d--9g.
- **Mentor:** FWI column confirmation (brief question 0) --- gates acceptance of
  `C-245473445-01` (P-COUNTY-1) and `C-247866001-01` (P-CELL-1); QA types to
  keep; reviewer.

## 14. Proposed gate status

**Run 1: diagnostic and candidate pool --- ingested and verified; no gate
proposed for QA** (nothing reviewed, nothing accepted). Run 2 pending.

## 15. Proposed next bounded objective

1. **Reviewer 1 (Kaiyuan) reviews batch 01** (11 candidates,
   `artifacts/softqa/review_batch_01.json`, forms in
   `artifacts/softqa/review_batch_01_forms/`), evidence first, rationale after.
2. **Run 2 on Polaris with agent v2** at the pinned commit of this package:

```bash
cd "$LITCOLLECT_ROOT_POLARIS"
PYTHONPATH="$CLIMRR_REPO/src" python "$CLIMRR_REPO/scripts/litcollect/softqa_agent.py" \
    --candidates "$CLIMRR_REPO/data/metadata/softqa/trackc_candidates_v1.json" \
    --units "$CLIMRR_REPO/data/metadata/softqa/units_definitions_v1.json" \
    --qa-types "$CLIMRR_REPO/data/metadata/softqa/qa_types_v1.json" \
    --index index/full_705k_v2_filtered --out softqa/run2 \
    --source-commit "$(git -C "$CLIMRR_REPO" rev-parse HEAD)"
```

   Expected START pins: `units_sha=5bb486ef6428 qa_sha=f0d0f07bf0fd
   system_sha=a44181ee2344 index=fbb4affb7162`.
3. After the review disposition: table-side values for the reviewed structure
   (D-033 §3), next package. Track D design.
