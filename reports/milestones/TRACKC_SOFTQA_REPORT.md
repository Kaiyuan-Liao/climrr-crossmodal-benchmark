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

**PENDING --- the Polaris run.** Pre-run gate at `4fb887f`: `pytest` 1056
passed, 2 skipped (the `jsonschema` cross-checks, see 9g) in conda `climrr`;
`verify_no_secrets_or_paths.py` 0 hits over 902 tracked files. Expected after
the run: `agent.log` START line pins (units / QA-types / system-prompt / index
hashes), every `candidates.jsonl` record mapped and validated.

## 11. Failures, rejected cases, and known limitations

**PENDING --- the Polaris run** (counts of `rejected_pre_review` by reason,
truncated papers, parse errors). Known before the run: 9a--9c.

## 12. Deviations from the approved plan

**PENDING --- COORDINATOR review of 9d--9g** (supplementary schema blocks;
invocation location; run record per view; built-in validator).

## 13. Open decisions and mentor questions

9a, 9b and 9e decided by the COORDINATOR (field 9). **PENDING --- the mentor:
confirmation of the FWI columns (brief question 0; gates `accepted` for
P-CELL-1 / P-COUNTY-1), which QA types to keep and the reviewer** (item A).

## 14. Proposed gate status

**PENDING --- after the run and its ingest.**

## 15. Proposed next bounded objective

**PENDING --- after the run.** Expected: Kaiyuan runs the agent on Polaris at a
pinned commit; ingest `softqa/run1`; first-reviewer pass on a predeclared
sample under the protocol; Track D design.
