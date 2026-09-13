# M1-WP3 report --- Pilot-subset semantic validation through row-centered candidate examples

## 1. Milestone ID and title

**M1 --- Data grounding and metadata audit.** Work package **M1-WP3**:
pilot-subset semantic validation through row-centered candidate examples.

A **work-package** report, not the M1 milestone gate. It is the third in M1:
WP1 catalogued the 275 columns against the dictionary, WP2 built the resolution
machinery and recorded the 2026-09-10 mentor meeting, and WP3 turns the
ambiguity that meeting left into specific, mentor-confirmable decisions.

Authorised by the GUIDANCE ruling of 2026-09-13
(`docs/M1_D010_GUIDANCE_RULING.md`, **PASS WITH ACTIONS**), approved by Kaiyuan
Liao with the ruling incorporated, and recorded as **D-010** (decided) and
**D-011** (the ruling and its boundaries).

## 2. Objective

Select a small pilot subset of columns; give every selected column one of
`verified_from_dictionary`, `owner_confirmed` or `inferred_candidate` with a
column-specific reasoning record where the last applies; and build three example
records from real rows that the mentor can confirm or correct field by field.

**Explicitly excluded, and none of it was done.** No phenomenon discovery. No
aggregation of any kind, geographic or otherwise. No thresholds. No selection of
rows by magnitude or salience. No literature ingestion, claim extraction,
embeddings, semantic bridges, table-to-paper links or QA generation. No reading
of a Fire Weather Index as a fire. No treating of a modeled historical baseline
as an observation. No interpretation of any column outside the 41 selected.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/m1-wp3`, created from `work/m1-wp2` |
| Head at report time | `b2f63ac59eb056057622a1d228265f3daa6c54ff` |
| Remote | **Not pushed.** The work package says do not merge or push; `origin/work/m1-wp2` stands at `53421f0` and `main` carries the WP1 merge |
| Commits in this package | 4, one per phase group: Phase A, Phases B–D, Phase E, Phase F |

## 4. Data version and checksums

| File | SHA-256 | Bytes | Shape | Storage |
| --- | --- | ---: | --- | --- |
| `data/raw/FullData.csv` | `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e` | 296,407,423 | 62,834 rows × 275 columns | Untracked, out of band, pinned by manifest hash (D-005) |
| `data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf` | `b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db` | 667,097 | 19 pages | Tracked (D-002) |
| `data/metadata/inferred_candidates.yaml` | `62cd7a2d58a7657002bc668820b3ac9a25381fa6229ae30f195bd6aa5a0554d3` | — | 20 records | Tracked, new in this package |

**The manifest hash was verified before every read, fail-closed, in every run.**
`CLIMRR_ALLOW_MISSING_RAW=1` was never set. No file under `data/raw/` was
modified, copied, or written back to. `scripts/build_examples.py` additionally
refuses to run if the coverage report it reads was built from different CSV
bytes than the ones it just verified.

Example records, each carrying the CSV SHA-256 in its own `provenance` block:

| File | SHA-256 |
| --- | --- |
| `artifacts/examples/example_1.json` | `6dca3695ccd00a1f8929a683506e054eed92c9d4aa542402013dbb37166269c7` |
| `artifacts/examples/example_14.json` | `e96f63996b463059c6b5bc7711553648c3c84565fba9625dbb678a1a675eb37f` |
| `artifacts/examples/example_148.json` | `36398e2c6549843c5afac45ab86bf706a305b160d582d9d07b3473c9aa5f29d8` |

## 5. Environment and execution location

| | |
| --- | --- |
| Location label | `local` (every run record) |
| Python | 3.11.16 |
| Platform | macOS-15.3-arm64-arm-64bit |
| Pinned libraries (D-007) | `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0` --- all `matches_pin: true` |
| Sophia | **Not run.** Nothing in this package needs it, and the D-007 note stands: Sophia must re-run `pip install -r requirements.txt` before its next pinned checkout, because `pypdfium2` joined the pin set in WP2 |

Run records written by this package, all `passed: true`:
`reports/runs/20260912T234343Z_local_dictionary_coverage.*`,
`20260912T234348Z_local_status_diff.*`, and four
`*_local_build_examples.*` records across the phases.

## 6. Work completed

**Phase A --- the status and its schema.** `inferred_candidate` was added to
`src/climrr/dictionary.py` as a status strictly below `owner_confirmed` and
`verified_from_dictionary`. It is settable **only** by a record in the new
tracked `data/metadata/inferred_candidates.yaml`: the dictionary rules never
emit it, the EXECUTOR candidate maps cannot produce it, and `validate_resolution`
refuses it by name so no resolution record can assign it either. It is applied
**after** the resolutions and still refuses to overwrite a stronger status; a
record aimed at such a column is reported as blocked rather than applied or
dropped. `scripts/dictionary_coverage.py` loads and hashes the new file;
`scripts/status_diff.py` shows every column that gains the status, citing its
IC-record, and enforces two new invariants about it.

The record schema is validated strictly --- an unknown key raises rather than
being ignored --- and two refusals carry the ruling rather than the schema: **a
record with no dictionary spans is refused, and so is one with no reasoning.**

**Phase B --- the subset.** 41 columns in four families, 20 of them carrying an
IC-record. Rationale, per-family, and the exclusions with their reasons are in
`docs/PILOT_SUBSET.md`.

**Phase C --- three rows, structurally.** Three selection rules, none of which
mentions the size of any value. Evaluated in one streaming pass over the CSV,
every value read as a string.

**Phase D --- the records.** `src/climrr/examples.py` and
`scripts/build_examples.py` produce one JSON record per row with five blocks in
the fixed order. The mentor-readable prose in block 5 is **generated from block 3
by template**; every clause resting on an inferred attribute is wrapped
`[provisional: ...]`, and the builder fails the run if one is not.

**Phase E --- the review document.** `docs/MENTOR_EXAMPLES.md`, one page per
example, each with a numbered checklist whose first line is the row-grain
assumption. `docs/MENTOR_BRIEF.md` rewritten to lead with the examples.

## 7. Deliverables and exact file paths

| Path | What it is |
| --- | --- |
| `data/metadata/inferred_candidates.yaml` | **New.** 20 column-specific reasoning records, 52 dictionary spans |
| `src/climrr/dictionary.py` | Modified: `INFERRED_CANDIDATE`, the record schema, its validator and loader, `apply_inferred_candidates` |
| `src/climrr/examples.py` | **New.** The pilot subset as data, the selection rules, the semantics builder, the presentation template |
| `scripts/build_examples.py` | **New.** Phases C and D end to end, with a run record |
| `scripts/dictionary_coverage.py` | Modified: loads, hashes and applies the IC records |
| `scripts/status_diff.py` | Modified: shows and polices the new status |
| `artifacts/examples/example_1.json`, `example_14.json`, `example_148.json` | **New.** The three records |
| `artifacts/profiles/dictionary_coverage.json` | Regenerated: 20 columns moved |
| `artifacts/profiles/status_diff.md` | Regenerated |
| `docs/PILOT_SUBSET.md` | **New.** The subset, the rationale, the exclusions |
| `docs/MENTOR_EXAMPLES.md` | **New.** The mentor review document |
| `docs/MENTOR_BRIEF.md` | Rewritten to lead with the examples |
| `docs/DECISION_LOG.md` | D-010 → decided; **D-011** appended |
| `docs/M1_D010_GUIDANCE_RULING.md` | The ruling as placed by Kaiyuan, now tracked |
| `docs/PROJECT_STATE.md` | Refreshed |
| `tests/test_inferred_candidates.py` | **New.** 54 tests |
| `tests/test_examples.py` | **New.** 37 tests |
| `tests/test_status_diff.py` | Extended with 6 tests for the new invariants |
| `reports/milestones/M1_WP3_REPORT.md` | This file |

## 8. Methods and rules that affect scientific meaning

**No filtering, aggregation, unit conversion, type coercion, renaming,
imputation or exclusion was applied to any data value.** Every value in every
example record is the raw string as read, empty string preserved, and the test
`test_the_raw_block_round_trips_to_the_csv` reads the three rows back out of the
file and compares them cell by cell.

Four rules that do bear on scientific meaning, stated plainly:

1. **Twenty columns were given a meaning the dictionary does not state.** That is
   the point of the package and it is why the status is named `inferred_candidate`
   and carries the words "not verified, not owner-confirmed" in every record.
   Nothing was promoted to `owner_confirmed`; the count there is still 0.
2. **Semantic attributes for verified columns are the dictionary's own literal
   markers**, not paraphrases --- the same `UNIT_MARKERS` and scenario markers
   `climrr.dictionary` used to decide the column was verified. The scenario
   markers were split into pathway (`RCP4.5`, `RCP8.5`) and horizon
   (`Historical`, `Mid-Century`, `End-Century`) so a record can state them
   separately, as the M1 metadata requirements ask. Nothing was added to either
   set. The rendered label reads "unit or type" rather than "unit", because the
   dictionary's markers mix the two and calling a type a unit would invent a
   distinction the source does not make.
3. **Row selection is structural.** Each rule tests only whether cells are
   populated, and `test_every_selection_rule_is_structural` asserts that no
   rule's text contains a magnitude word.
4. **Blanks are rendered "no value in this file"** --- never `0`, never
   "missing", never "N/A". A test asserts that no digit appears where the file
   holds nothing.

## 9. Results with compact tables or examples

### Pilot subset counts by status

| Status | Count | Note |
| --- | ---: | --- |
| `verified_from_dictionary` | **21** | Every verified column in the file |
| `owner_confirmed` | **0** | Nothing confirmed yet; that is what the examples are for |
| `inferred_candidate` | **20** | One IC-record each |
| **Total selected** | **41** | of 275 |
| Not selected | 234 | Untouched, at their WP1 baseline status |

### Whole-table status counts

| Status | WP1 baseline | Now | Change |
| --- | ---: | ---: | ---: |
| `verified_from_dictionary` | 21 | 21 | 0 |
| `owner_confirmed` | 0 | 0 | 0 |
| `inferred_candidate` | 0 | 20 | **+20** |
| `partially_resolved` | 143 | 130 | −13 |
| `unresolved` | 28 | 28 | 0 |
| `structurally_observed_only` | 83 | 76 | −7 |
| **Total** | **275** | **275** | |

### The three rows and their selection rules

| Rule | `OID_` | `Crossmodel` | Row ordinal | Where | Blank pilot columns | Rule |
| --- | --- | --- | ---: | --- | ---: | --- |
| **R-A** | `1` | `R106C361` | 0 | `Stephens`, Oklahoma, `GEOID` `40137000902` | 0 | first row non-empty on every selected pilot column |
| **R-B** | `14` | `R107C232` | 13 | `San Bernardino`, California, `GEOID` `06071010300` | 0 | first such row whose `GEOID` begins with `0` |
| **R-C** | `148` | `R105C198` | 147 | `Ventura`, California, `GEOID` `06111990100` | **17** | first row empty on at least one selected pilot column |

**IC-record count: 20** (IC-001 … IC-020), carrying **52 dictionary spans**,
every one of which is checked against the tracked extracted text verbatim by
`test_every_tracked_span_quotes_the_extracted_text_verbatim`. Distribution:
5 heat-index (Q14), 5 fire-weather (Q13), 7 location (Q10, Q16), 3 stem-probe
(Q1). **23 enumerated assumptions per example record**, A1 first.

### `scripts/status_diff.py` summary

```
  resolution records applied: 2
  IC records applied        : 20
  columns changed           : 20 of 275
    inferred_candidate          :    0 ->   20 (+20)
    partially_resolved          :  143 ->  130 (-13)
    structurally_observed_only  :   83 ->   76  (-7)
    unresolved                  :   28 ->   28  (+0)
    verified_from_dictionary    :   21 ->   21  (+0)
```

All 20 changes cite an IC-record and D-011. **No column reached
`verified_from_dictionary` through a record, none fell from it, and no record
was blocked** --- nothing in the subset needed reasoning where the dictionary
already speaks. 0 invariant violations.

## 10. Validation performed

| Check | Result |
| --- | --- |
| `pytest` | **360 passed**, 0 failed. 91 of them new in this package |
| `python scripts/verify_no_secrets_or_paths.py` | **152 tracked files scanned, 0 hits** |
| `python scripts/dictionary_coverage.py` | PASS. 275 columns, 20 IC records applied, 0 blocked, 0 statuses without a span |
| `python scripts/status_diff.py` | PASS. 20 changes, 0 invariant violations |
| `python scripts/build_examples.py` | PASS. 3 records, 0 unlabelled inferred values |
| Manifest verification | Verified before every read, fail-closed, in every run |
| Cross-host reproduction | **Not run** --- nothing here requires Sophia |

Checks worth naming individually, because they test the ruling rather than the
code:

- **`test_no_inferred_value_reaches_the_mentor_unlabelled`** --- for every
  inferred attribute of every column, the value appears in that column's own
  presentation line only inside a `[provisional: ...]` label.
- **`test_a_verified_column_is_never_labelled_provisional`** --- the converse.
  Attaching the label to a quotation would devalue both.
- **`test_changing_an_ic_record_changes_the_presentation`** --- edits IC-001's
  proposed unit to "degrees Celsius" and asserts the prose follows. The
  reasoning is what the text is generated from, not decoration beside it.
- **`test_the_raw_block_round_trips_to_the_csv`** --- reopens the file and
  compares all three rows cell by cell against the records.
- **`test_a_blank_is_rendered_as_no_value_and_never_as_a_number`**.
- **`test_fire_vocabulary_appears_only_inside_a_denial`** --- "burned area" and
  "ignition" may appear in a record only within a sentence that denies them.
- **`test_the_presentation_uses_no_magnitude_adjective`** --- 19 words banned.
- Eight tests holding `docs/MENTOR_EXAMPLES.md` to the JSON records.

## 11. Failures, rejected cases, and known limitations

**Two defects were found by the checks and fixed.**

1. **The provisional-label check was wrong the first time it ran.** It counted
   value occurrences across the whole document, so `RCP8.5` --- inferred for
   `heatindex_M85_DayMax`, and stated verbatim by the dictionary for
   `heatindex_M85_Day95` --- was reported as an unlabelled inference. The check
   is now scoped to a column's own presentation line, where every clause
   describes one column and no such ambiguity exists. The build failed loudly
   rather than emitting a record, which is the behaviour intended.
2. **Two county names in the mentor document were guessed rather than read.**
   The draft said `Comanche` and `Monterey`; the rows hold `Stephens` and
   `San Bernardino`. Caught by the drift test written immediately afterwards,
   before the document was committed. A wrong fact in that document is the worst
   kind in this repository --- it would put a false number in front of the one
   person who could correct it --- so the test now checks the hand-written
   location line against the row's own bytes.

**Known limitations, none of them hidden:**

- **20 columns now carry a meaning nobody has confirmed.** That is the design
  and it is why the status is named as it is, but the number should be read as
  "20 open questions made specific", not "20 columns understood".
- **The stem-to-section link (Q1) is one inference carrying 101 columns.** Three
  of them are in the pilot. If the mentor rejects the link, IC-018 through
  IC-020 fall and so does every column in indices 5–105.
- **The Census vintage and the coordinate reference system are unknown**, and
  nothing in this package narrows either. Both are stated in the records, in
  `PILOT_SUBSET.md`, and in the mentor checklist.
- **"Seasonal value" in the FWI table is genuinely ambiguous** between the
  seasonal average (lines 346–352) and the seasonal 95th percentile (line 357
  onward). IC-006 proposes the former and records the alternative as unresolved
  rather than choosing quietly.
- **The direction of every subtraction is unresolved.** Five records
  (IC-004, IC-005, IC-009, IC-010, IC-020) note that the dictionary states the
  endpoints of a change and never the order of the operation.
- **`test_the_raw_block_round_trips_to_the_csv` skips when the raw CSV is
  absent**, which a fresh clone will be (D-005). It is not skipped on a gate run.
- **The three examples share one set of 41 columns**, so they test presentation
  --- completeness, leading zeros, blanks --- rather than breadth of semantics.
  Breadth was deliberately traded away; the ruling asked for a small subset.

## 12. Deviations from the approved plan

**One, minor, and it concerns layout rather than content.**

The work package asks that `docs/MENTOR_EXAMPLES.md` carry, per page, "the
presentation text; a compact table of the raw values used with their status;
then a numbered checklist", and that the whole document stay **under three
screens** and be answerable in ten minutes. With 41 columns × 3 examples those
two requirements pull against each other: the full presentation text and raw
tables run to about 350 lines.

Both are satisfied by folding the raw table and the generated prose of each page
into an HTML `<details>` block. Everything the package asks for is present and
complete; **169 of the document's 522 lines are visible when folded**, which is
about two screens, and the checklists --- the part the mentor actually answers
--- are never folded. The checklists on pages 2 and 3 carry only the lines
specific to those rows plus the mandatory A1, and point back to page 1's
fourteen lines rather than asking the same questions three times.

Nothing else departs from the work package. The optional single stem-family
column was taken up, as the package permits, at its suggested three columns
(`tempmaxann_hist` with `rcp85_endc` and `end85_hist`) and no more.

## 13. Open decisions and mentor questions

### For GUIDANCE

1. **Is the subset small enough?** 41 of 275 columns --- 15% --- in four
   families, with 20 IC-records. The judgement asked for is whether that is
   "deliberately small" in the sense the ruling intends, or whether the pilot
   should have stopped at two families. The shape of the selection is that it
   contains **every** `verified_from_dictionary` column in the file and then the
   minimum needed to make those readable; the four families were chosen for
   scientific relevance, interpretability, provenance awareness and
   literature-compatibility rather than for ease of narration, and
   `PILOT_SUBSET.md` argues each. The stem-probe family is the one that could be
   cut: it exists only to make Q1 concrete and adds no columns an example needs.

2. **Does the presentation templating meet criterion 6** --- "raw facts,
   interpreted semantics, and natural-language presentation are clearly
   separated"? The claim is that it does, and mechanically rather than by
   convention: block 5 is a pure function of blocks 3 and 4; every clause from
   an `inferred` attribute is wrapped by a single helper; the builder fails the
   run if any is not, and a test asserts it independently. The specific thing
   for GUIDANCE to judge is the **caution mechanism** --- three standing
   sentences (Fire Weather Index, modeled historical baseline, empty cell) that
   fire only when an entry in that record triggers them and that each record
   which entries did. They are the only sentences in the output not derived from
   a single column's semantics entry, and they exist because the repository's
   rules require the FWI wording on every mention. Whether that counts as
   template output or as authored prose is the open question.

### For the mentor (through the examples, per the ruling)

The fourteen checklist lines of `docs/MENTOR_EXAMPLES.md`, of which four matter
most: is one row one "event"; does `tempmaxann` denote "Temperature Maximum -
Annual" (101 columns); which Census vintage; and is this the shape of record she
expects to connect to literature.

### For Kaiyuan

Preserve the mentor's feedback accurately and **distinguish explicit
confirmation from correction, from broad approval, and from an unanswered
assumption** --- the ruling asks for exactly that, and WP4 cannot promote
anything without it.

### Still blocked

Q7 (56 `precipdaily_*` columns), Q8 (30 FWI-class columns), Q9 (7
socioeconomic columns, and `-9` at index 117), Q11, Q12, Q15, Q17, Q18 ---
untouched by this package and still blocking downstream use of the columns they
name.

## 14. Proposed gate status

**This is a work-package report; the M1 gate is not proposed here.** The
ruling's eleven acceptance criteria for M1-WP3, one line each:

| # | Criterion | Status | Evidence |
| ---: | --- | --- | --- |
| 1 | A small, explicit pilot subset with a rationale based on scientific relevance and interpretability | **MET** | 41 of 275 columns, four families, per-family rationale and exclusions in `docs/PILOT_SUBSET.md` |
| 2 | Every selected field has one of the three statuses | **MET** | 21 / 0 / 20; `test_every_selected_column_carries_one_of_the_three_allowed_statuses` |
| 3 | Every `inferred_candidate` includes evidence, reasoning, explicit assumptions and unresolved alternatives | **MET** | 20 records, 52 verbatim-checked spans; a record missing spans or reasoning is refused by the validator, with tests |
| 4 | Exactly 2–3 real-row prototype records | **MET** | 3, at `artifacts/examples/` |
| 5 | Every record preserves complete provenance back to raw row and column values | **MET** | `provenance` carries the CSV SHA-256, `OID_`, `Crossmodel` and the row ordinal; `test_the_raw_block_round_trips_to_the_csv` compares cell by cell |
| 6 | Raw facts, interpreted semantics and natural-language presentation clearly separated | **MET, with one judgement for GUIDANCE** | Three blocks; prose generated by template; unlabelled-inference check fails the build. The caution mechanism is put to GUIDANCE in field 13 |
| 7 | "One row = one event" presented as an assumption under review | **MET** | A1 in every record, first line of every checklist, stated in the brief and in D-011 |
| 8 | No aggregation, thresholding, phenomenon mining, literature processing, bridge construction or QA generation | **MET** | Field 8; the selection rules are structural and a test asserts it |
| 9 | Compact enough for mentor review, designed to elicit specific corrections | **MET** | ~2 screens folded, 14 numbered lines, each answerable confirm / correct / don't know |
| 10 | After mentor feedback, every promotion to `owner_confirmed` can be tied to a resolution record stating exactly what was confirmed | **PENDING --- mentor review.** The machinery is in place and inert: resolution records reach columns only by naming them, `inferred_candidate` can never become `verified_from_dictionary`, and the checklist is per-interpretation so an answer lands on named columns | |
| 11 | The evidence suffices to judge whether the pilot fields meet the M1 metadata requirements | **PENDING --- mentor review** for the 20 inferred columns; **MET** for the 21 verified. Meaning, unit or type, horizon, scenario, missing-value policy and provenance status are recorded per column in every record | |

**Proposed work-package status: ready for GUIDANCE review.** Criteria 10 and 11
are PENDING by construction --- they cannot close before the mentor has seen the
examples, which is what the package produced.

Against the four M1 **milestone** gate criteria in `docs/PROJECT_PLAN.md`,
evaluated on the pilot subset as D-011 permits:

> 1. "Every field selected for the pilot has a documented meaning, unit, time horizon, scenario, missing-value policy, and provenance status."

**MET for the 21 verified columns; PENDING mentor confirmation for the 20
inferred.** All 41 carry all six attributes, with the provenance of each
recorded as `dictionary`, `inferred` or `unknown`. The `unknown` values are
findings, not gaps left blank.

> 2. "No unresolved identifier or sentinel-value issue can silently corrupt the pilot."

**MET.** Identifiers are read and kept as text, and R-B exists to demonstrate a
leading zero surviving into the mentor's view. No sentinel is interpreted: index
117's `-9` is excluded from the subset under D-009 ruling 3, and the two
`0.000000000000000` values in index 191 are recorded as an open question (Q17)
with no example selected on their account.

> 3. "The report clearly distinguishes verified facts from hypotheses."

**MET**, and enforced rather than asserted: `verified_from_dictionary` and
`inferred_candidate` are different statuses, no record can convert one into the
other, and every hypothesis is wrapped `[provisional: ...]` in the text the
mentor reads.

> 4. "The mentor-facing metadata questions are specific and actionable."

**MET.** They are now attached to named columns with raw values beside them.

## 15. Proposed next bounded objective

**M1-WP4 --- apply the mentor's feedback on the three examples; promote
explicitly confirmed semantics to `owner_confirmed` through resolution records
that state exactly what was confirmed for exactly which columns; then assemble
the M1 milestone gate packet.**

Nothing is promoted on broad approval. An answer that confirms the approach
without confirming a field reading is recorded as approval of the approach; a
correction rewrites the IC-record and leaves the column unconfirmed; a "don't
know" leaves both alone and keeps the column out of scientific use.
