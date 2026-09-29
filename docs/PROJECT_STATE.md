# Project state

One screen. **Refresh this file at the end of every work package.** A stale
state file is worse than a thin one: the M0 cold-resume trial showed a fresh
session reasoning correctly from out-of-date facts and repeating them.

| | |
| --- | --- |
| **Current milestones** | **M1 --- data grounding and metadata audit: open.** Criterion 1 will be evaluated on **provisional statuses, explicitly declared** (D-014). **M4 --- literature ingestion and structured claim pilot:** M4-WP0 PASS (D-016); **M4-WP1 complete**, awaiting GUIDANCE review |
| **Active task** | **M4-WP1 --- deterministic 10-paper ingestion and structured-claim pilot: complete** on the unmerged, unpushed branch `work/m4-wp1` (from `main` at `5ebb330`). Report: `reports/milestones/M4_WP1_REPORT.md` --- 20 criteria proposed MET, criterion 16 with a disclosed limitation. **Next: GUIDANCE review of M4-WP1** |
| **Latest accepted commit** | **`6f24b78`** --- the `--no-ff` merge of the M4-WP0 chain (M1-WP2, M1-WP3, M1-WP3b, M4-WP0) into `main`, accepted by GUIDANCE with M4-WP0 reviewed at `1e2fd9f` (D-016); its second parent is the chain head `e4a9de0`. **The authoritative integrated state.** It does **not** pass M1. Previous: `62c9137` (M1-WP1, D-009) |
| **Tooling on `main`** | `d68ba15` --- merge of `work/knowledge-staging` (`c13a3d4`, `scripts/stage_knowledge.py`) on top of `6f24b78`. **No scientific content**; not a GUIDANCE-accepted package, and not an accepted scientific state |
| **Sophia-verified commit** | `2b7345f` --- the pinned commit the cross-host reproduction ran at. The literature corpus is **not** on Sophia (runbook §8b) |
| **Branch lineage** | M1-WP2 → M1-WP3 → M1-WP3b → M4-WP0 merged into `main` at `6f24b78`; tooling at `d68ba15`; state refresh `5ebb330`. **`work/m4-wp1`** branches from `5ebb330`: `6f9006c` (Phase A, sample frozen), `d728df6` (Phases B--D), then the report commit. **Not pushed, not merged** |
| **M4-WP0 commits** | `52a994a` (Phases A–E); **`1e2fd9f`** (report and state --- **the reviewed head**); then `e4a9de0`, the D-016 pre-merge bookkeeping |
| **M4-WP1 sample** | `LIT-000001, 000191, 000381, 000571, 000761, 000951, 001141, 001331, 001521, 001711` --- every 190th id; no duplicate skip; `wp1_sample.json` SHA-256 `5cb81f95…`, committed before any file was opened |
| **Prototypes built from** | `56eb10d` --- unchanged since M1-WP3b; no record rebuilt |
| **M0 gate** | **PASSED --- PASS WITH ACTIONS**, GUIDANCE, at commit `b87564b` (D-006) |
| **Rulings in force** | D-009 (M1-WP1 PASS), D-011 (D-010 ruling), D-012 (M1-WP3 pre-meeting, REVISE --- framing only, done), D-013 + D-013-A1 (M1-WP3b PASS WITH ACTIONS), **D-015 (M4-WP0 PASS WITH ACTIONS)**, **D-016 (M4-WP0 PASS; merge authorized; M4-WP1 authorized; overall PASS WITH ACTIONS)** |
| **Owner decisions since** | **D-014** (Kaiyuan, 2026-09-28): proceed on the "our reading" basis to test what QA could be generated; every `inferred_candidate` and `derived_from_inferred` status carried through; **promotes nothing, and does not authorise QA generation** |
| **Meetings since the last refresh** | **Group 2026-09-14:** "No material objection to the prototype-unit design was raised." --- not validation, no semantic confirmed. **Mentor 2026-09-17 and 2026-09-24:** **no review of the answer sheet occurred** (R-003); nothing promoted |
| **Blockers** | **M1** promotion of any column: blocked on the mentor, who has not reviewed the sheet. **M1 remains open.** **M5**: blocked on the GUIDANCE review of M4-WP1. **QA generation: not authorised by any ruling** |

## Where things stand --- M4-WP1 (2026-09-29)

- **Ten corpus items were sampled by rule, frozen, and then read in full.** The
  sample reads only ids and duplicate groups from the frozen manifest; it was
  committed (`6f9006c`, 05:17:40Z) before the first file was opened (05:18:25Z).
  **Ten items, deterministically sampled, for workflow validation; not
  representative of the corpus.**
- **The JSON has no shared schema.** Every file is a flat object of strings
  whose keys are section headings; all ten key sequences differ. `title` is
  missing once and holds a non-title twice (a journal name; a page header).
- **Outcome:** 6 `in_scope_hazard` → `claims_extracted` (27 claims), 3
  `off_topic`, 1 `ambiguous_only`. 3 claims carry an `inferred` dimension, each
  with its support span. 22 rejected or ambiguous passages are kept. Scenario is
  `unknown` in 25 of 27 claims; no claim states an emissions scenario.
- **Every one of 96 evidence spans re-slices exactly** from the decoded source:
  zero-based, half-open `[start, end)` code-point offsets on the unnormalized
  string, computed by exact search, never typed. A combining macron in a place
  name stopped the build once --- the check working.
- **The reading is the EXECUTOR's, once**, and the EXECUTOR is a language model
  that had built the prototypes. The code reads no prototype, family or query
  (tested); the reader's prior exposure is disclosed, not claimed away. For
  GUIDANCE: whether a second, independent reader is needed before M5, and
  whether tracked verbatim excerpts (96 short quotations) are acceptable.
- Documents: [LITERATURE_WP1_PILOT.md](LITERATURE_WP1_PILOT.md),
  [../reports/milestones/M4_WP1_REPORT.md](../reports/milestones/M4_WP1_REPORT.md).

## Where things stand --- M4-WP0 (2026-09-28)

- **The literature corpus has arrived and is pinned, unopened.** JL supplied a
  folder (`00`) of **1,918 `.json` files, 78,798,270 bytes**, and the Boolean
  query it was collected with. The folder stays external, at
  `literature_corpus_root` in the untracked config. Every file was read as raw
  bytes for SHA-256 and size and **for nothing else** --- one `rb`-only reader,
  with runtime and AST tests that nothing decodes or parses. **0 zero-byte files;
  1 exact-duplicate pair** (`LIT-001483`, `LIT-001484`), identified, not removed.
  Ids `LIT-000001`… are frozen; a re-run verifies and fails on any change.
- **The corpus identity for later packages** is the SHA-256 of
  `artifacts/literature/corpus_manifest.json`,
  **`3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a`**,
  recorded in `data/manifest.json` under `external_corpora` with a
  timestamp-free content identity beside it.
- **The query is pinned**: `data/metadata/literature_query.txt`, SHA-256
  **`5a7ddf53…e1e5`**, 2,292 bytes, byte for byte as received. Platform,
  execution date, export date and completeness are **`unknown`** --- Q19–Q21,
  for JL, not the mentor.
- **The query has eleven hazard groups, not ten** as the work package said ---
  reported as found. 80 hazard terms, 22 context terms. **It carries no
  scenario, horizon, US state, postal code, county, tract or USA term** (three
  absence rules, 0 hits) --- verified only against those lists, and a finding
  about the query, not about any paper.
- **Query-scope coverage, not corpus coverage.** Each prototype's concept terms:
  **1 exact, 0 normalized, 3 absent** (`fire weather`, `fire weather`,
  `heat index`). All four family names absent. **9 of 11 query hazard groups
  have no pilot counterpart.** `inferred_conceptual_relationship` is defined and
  cannot be emitted.
- **Kaiyuan opened one file before the inventory**; it appeared off-topic (urban
  surface water, Wuhan). An observation from one file, not a corpus property ---
  M4-WP1's sample should expect off-topic items.
- **`!artifacts/literature/` was added to `.gitignore`**, because the corpus
  rule `literature/` caught the path the work package names. The corpus rule is
  unchanged.

## Where things stand --- M1 (carried forward; unchanged by M4-WP0 except as marked)

- **The M1 problem changed shape and the project followed it.** R-001 (2026-09-10)
  established that **no further documentation exists** --- no newer dictionary,
  no assembly document, no release note --- and R-002 gave a direction rather
  than any per-column answer. D-010, now decided, is the response: interpret a
  small subset, name the inference as inference, and let the data owner confirm
  it on worked examples.
- **A fifth status exists and twenty columns hold it.** `inferred_candidate` is
  **strictly below** `owner_confirmed` and `verified_from_dictionary` and is
  settable **only** by a column-specific record in the new tracked
  `data/metadata/inferred_candidates.yaml`. The dictionary rules never emit it,
  the EXECUTOR candidate maps cannot produce it, and `validate_resolution`
  refuses it by name --- **a resolution record can never assign it**, and it can
  never overwrite a stronger status. A record with no dictionary spans, or with
  no reasoning, is refused.
- **Status counts are now 21 / 0 / 20 / 130 / 28 / 76** --- verified,
  owner-confirmed, inferred, partially resolved, unresolved, structurally
  observed only. `status_diff.py` attributes all 20 changes to an IC-record and
  D-011, with 0 invariant violations. **Nothing reached `owner_confirmed`; the
  count there is still zero and stays there until the mentor answers.**
- **The pilot subset is 41 of 275 columns** in four families --- heat index (Q14),
  summer fire weather (Q13), a location anchor (Q10), and three `tempmaxann`
  columns that make the Q1 stem assumption concrete. It contains **every**
  `verified_from_dictionary` column in the file and then the minimum needed to
  make those readable. **The other 234 columns are untouched**, at their WP1
  baseline. See `docs/PILOT_SUBSET.md` for the rationale and the exclusions.
- **Three example records are built and ready for the mentor**, from rows 0, 13
  and 147, picked by rules that look only at whether cells are populated ---
  never at how large a value is. Each keeps raw bytes, recorded semantics and
  generated prose in three layers; the prose is produced **by template** from the
  semantics, and every clause resting on an inference is wrapped
  `[provisional: ...]`, with the build failing if one is not.
- **The answer sheet was not reviewed** at the one-on-ones of 2026-09-17 or
  2026-09-24 (R-003, *new*). It remains outstanding. **`docs/MENTOR_EXAMPLES.md`
  is what goes to the mentor, and to nothing else.** Sixteen numbered
  lines --- fifteen answerable confirm / correct / don't know in ten minutes, and
  line 13 a stated observation with nothing to confirm --- behind a printable
  answer sheet. `MENTOR_BRIEF.md` leads with it and demotes the Q1--Q18 table
  beneath.
- **The pre-meeting review (D-012) found one real defect and it is fixed.** Some
  **inferred location semantics were stated as fact outside the confirmation
  surface**: headings read `Stephens County, Oklahoma` and framing read
  `Where it is:`, while `NAME`, `State` and `State_Abbr` are themselves
  `inferred_candidate`. The generated prose was correct throughout --- the
  **hand-authored framing around it was not**. Titles are now neutral, the
  location line quotes the stored strings under a label that claims nothing, and
  the location checklist item is **split three ways** so one tick cannot confirm
  a character count and a semantic claim together. A bounded guard,
  `test_no_unwrapped_location_semantic_in_the_hand_authored_framing`, now checks
  the hand-authored surface and a second test feeds the rejected heading back
  through it. **The standing rule this establishes: a labelling discipline
  enforced only where output is generated is not enforced.**
- **M1-WP3b built three prototype phenomenon units, and the ruling admitted them
  as validation objects and nothing more.** Every record carries
  `validation_only` and opens with **"Prototype for scientific-object
  validation. Not an accepted phenomenon record."** Schema version
  `p0-prototype`, not `v1`. One grid cell (`R106C361`), one
  county-shaped row set (`Oklahoma` / `Stephens`, 10 rows), one state-shaped row
  set (`California`, 2,831 rows of which 2,827 carry a value). Every derived
  field takes the **weakest** status of its inputs, with the consequence that
  **no field in any of the three reaches `derived_from_verified`**. Every
  operation, assumption and provisional rule is named in the record that uses
  it. Nothing is merged, nothing is pushed, nothing is milestone evidence.
- **Phase A measured two things that decide what "county-level" can mean.**
  `Crossmodel` is **unique** --- 62,834 distinct over 62,834 rows. And **`GEOID`
  does not determine `(State, NAME)`**: 3,234 of 12,941 values appear against
  more than one pair. The consequence is procedural and is now a repository
  rule: **no row set in this project may be keyed on `GEOID`**, and none is. A
  county here is the set of rows sharing a `(State, NAME)` label (A-G3,
  computed), and nothing else.
- **A column's dictionary type decides what arithmetic it admits.** The ruling
  found that `P-COUNTY-1` was reporting an **unweighted mean of
  `wildfire_summer_Pend`**, a column the dictionary itself labels "Percent
  Change". The mean is gone; the ten per-cell values are kept; the corroboration
  is now a count --- *positive on 10 of 10 member cells*. The fix is general:
  `aggregate_column` **refuses** any column typed `Percent Change` or `Text ID`
  and any location column, with tests in both directions. **The standing rule:
  whether the characters parse as a number is not the question.**
- **The magnitude field is a placeholder and says so everywhere it appears.**
  `provisional_rule PR-1` ranks a unit's change value against every unit at the
  same level and reports a tercile. It is not a threshold, rests on no
  literature, and is wrapped in its own distinct mark --- `[provisional rule
  PR-1: ...]` --- so a reader can tell a provisional *value* from a placeholder
  *rule*. It ranks on the **signed** change value, not on absolute magnitude ---
  a unit in the lower third may be one with a large **decrease** --- and every
  `M` field now says so and carries the exact reference-population definition.
  **Wherever a percentile is reported, the population's composition is stated
  with it** --- "of 50 `State`-label groups: 49 named labels plus one
  empty-label group (7 rows with a value)", "of 3,019 `(State, NAME)` label
  groups: 3,018 named labels plus one empty-label group", "of 62,834
  `Crossmodel`-key groups: all named, no empty-label group". **"Group", not
  "county" or "state"**: at those levels a unit is a set of rows sharing a
  label, and calling it a county would assert the reading A-G1 is still asking
  the mentor to confirm.
- **Every unweighted mean carries the ruling's own label for it.**
  **"Provisional aggregation rule for representation validation"** --- the
  ruling's words, quoted, not paraphrased --- travels beside the number in the
  record, in the generated sentence, in both generated documents and in the
  handout, with a test that a cell-level record, which averages nothing, does
  **not** carry it. The mean is acceptable for these three prototypes on that
  condition and is **not** the project's aggregation method.
- **The assumptions register says what breaks.** Every one of the **thirteen**
  assumptions carries a **rationale** and a **failure mode** --- what goes
  wrong downstream if it is false --- as columns separate from the statement.
  The sharpest: if cells are not equal in area, every aggregate is biased by an
  unknown amount in an unknown direction, **and none of the numbers would look
  wrong**. Ten are flagged as worth putting to the mentor on 2026-09-17.
- **A-M2 is the newest, and it is a choice nobody has made.** PR-1's reference
  population **includes empty-label groups**: the 7 rows with no `State` form
  one group of the 50 ranked at state level and one of the 3,019 at county
  level. Counting them asserts nothing; excluding them would assert that those
  rows are not a place, and what they are is Q16, open. At state level one group
  is 2% of the population --- enough to move a tercile boundary.
- **Two conventions for the schema letters exist and neither is settled.** The
  mentor and Kaiyuan use S = season, T = horizon, C = scenario; the WP3b ruling
  uses S = scenario, T = temporal horizon, C = compared quantity. **The code
  emits the mentor's**, because they are what she has already seen. `P`, the
  per-field provenance map, is now an explicit field and both conventions agree
  on it. D-013 records the pair for the next GUIDANCE packet. **No number
  depends on the choice.**
- **The literature probe is a design stub and nothing was retrieved.** It
  already yields one finding: **at cell level there is no usable place term.**
  A grid-cell id is not a phrase any paper contains.
- **One M1-WP3 sentence stopped being true and was not carried across.** The
  location caution there ends "no part of this pilot groups rows by any of
  them". WP3b groups rows by `State` and `NAME` deliberately, so its records
  carry their own caution saying so, and a test refuses the old sentence in a
  WP3b record. **The M1-WP3 records are unchanged and their caution remains
  true of them.**
- **"Each row = one event" is still an assumption.** It is line 1 of every
  checklist and A1 of every record. Nothing treats it as settled.
- **Four GUIDANCE rulings from D-009 remain in force**, none of them reopened:
  the strict `verified_from_dictionary` bar; candidate maps for navigation only;
  index 117 kept with `-9` unlabelled; D-008 stated, not verified.
- **`pypdfium2==5.13.0` is in the D-007 pin set.** **Sophia must re-run
  `pip install -r requirements.txt`** before its next pinned checkout.
- **D-005/D-006/D-007 hold.** Every run verified the manifest SHA-256 before
  reading, fail-closed. `CLIMRR_ALLOW_MISSING_RAW=1` was never set. WP3 added
  one more guard: `build_examples.py` refuses to run if the coverage report it
  reads was built from different CSV bytes than the ones it just verified.

## Outstanding

- **For GUIDANCE: review M4-WP1** (`reports/milestones/M4_WP1_REPORT.md`; field 13
  lists five decisions --- the two borderline scope calls, the claims-only-in-scope
  rule, a second reader, tracked excerpts, and the overloaded scenario dimension).
- **For GUIDANCE, still open from WP3b:** the S/T/C letter convention (D-013, D-013-A1), and --- at the
  M1 gate --- whether criterion 1 may pass on declared provisional statuses
  (D-014).
- **For JL, the collection scientist:** Q19 (platform / database, fields
  searched), Q20 (execution and export dates), Q21 (is the folder the complete
  result set).
- **For the mentor, through the examples --- still unanswered:** is one row one
  "event"; does the stem `tempmaxann` denote "Temperature Maximum - Annual"
  (**101 columns** turn on it); which Census vintage are `GEOID` and `TRACTCE`;
  and is this the shape of record to connect to literature.
- **Pending choice: exclude empty-label groups from PR-1 populations (A-M2).**
  It was to be decided after a mentor answer on Q16; **no answer came**. PR-1
  still counts them and every record says so.
- **For Kaiyuan:** push `work/m4-wp1` when ready (the EXECUTOR does not),
  and the Sophia `pip install -r requirements.txt` reinstall (`pypdfium2` pin).
- **Q7, Q8, Q9, Q11, Q12, Q15, Q17, Q18** still block downstream use of the
  columns they name. **Export date** of the ClimRR file remains unknown (Q18).

## Next

**GUIDANCE reviews M4-WP1.** If it passes: **M5-WP1 --- compatibility check
between the WP1 claims and the three prototypes, on this fixed set, to be
designed by COORDINATOR after GUIDANCE review.**

Still not authorised by any ruling: **QA generation**; semantic bridges beyond
what M5-WP1 is designed to test; embeddings; corpus-wide search; hazard labels
for papers outside the sample; any interpretation of a ClimRR column outside the
41 in the pilot subset. **D-014 changes none of that.**

## Links

- Charter: [BLUEPRINT.md](BLUEPRINT.md)
- Plan and gate criteria: [PROJECT_PLAN.md](PROJECT_PLAN.md)
- Decisions, including D-010 to D-013-A1 and **D-014, D-015, D-016**: [DECISION_LOG.md](DECISION_LOG.md)
- The ruling that authorised WP3: [M1_D010_GUIDANCE_RULING.md](M1_D010_GUIDANCE_RULING.md)
- The pre-meeting review of WP3 (**REVISE**, framing only): [M1_WP3_PREMEETING_GUIDANCE_REVIEW.md](M1_WP3_PREMEETING_GUIDANCE_REVIEW.md)
- The pilot subset, its rationale and its exclusions: [PILOT_SUBSET.md](PILOT_SUBSET.md)
- **What goes to the mentor one-on-one, 2026-09-17:** [MENTOR_EXAMPLES.md](MENTOR_EXAMPLES.md)
- **What goes to the group, 2026-09-14:** [GROUP_MEETING_2026-09-14.md](GROUP_MEETING_2026-09-14.md)
- **The ruling on M1-WP3b (PASS WITH ACTIONS):** [M1_WP3B_GUIDANCE_RULING.md](M1_WP3B_GUIDANCE_RULING.md)
- **M1-WP3b, prototype and unmerged:** [PHENOMENON_PROTOTYPES.md](PHENOMENON_PROTOTYPES.md),
  [PHENOMENON_ASSUMPTIONS.md](PHENOMENON_ASSUMPTIONS.md),
  [GROUP_MEETING_2026-09-14.md](GROUP_MEETING_2026-09-14.md),
  [../reports/milestones/M1_WP3b_PROTOTYPE_REPORT.md](../reports/milestones/M1_WP3b_PROTOTYPE_REPORT.md)
- Structural facts the prototypes rest on: [../artifacts/profiles/hierarchy_checks.md](../artifacts/profiles/hierarchy_checks.md)
- Data facts, dictionary-verified semantics, open questions: [DATA_NOTES.md](DATA_NOTES.md)
- Mentor-facing question inventory: [METADATA_QUESTIONS.md](METADATA_QUESTIONS.md)
- Per-column reasoning for every inferred candidate: [../data/metadata/inferred_candidates.yaml](../data/metadata/inferred_candidates.yaml)
- Sophia procedure, including M1-WP1 reproduction: [SOPHIA_RUNBOOK.md](SOPHIA_RUNBOOK.md)
- M0 report (accepted): [../reports/milestones/M0_SETUP_REPORT.md](../reports/milestones/M0_SETUP_REPORT.md)
- M1-WP1 report, frozen at the WP1 stage: [../reports/milestones/M1_DATA_GROUNDING_REPORT.md](../reports/milestones/M1_DATA_GROUNDING_REPORT.md)
- M1-WP2 report: [../reports/milestones/M1_WP2_REPORT.md](../reports/milestones/M1_WP2_REPORT.md)
- **M1-WP3 report, current M1 status:** [../reports/milestones/M1_WP3_REPORT.md](../reports/milestones/M1_WP3_REPORT.md)
- M1-WP1 GUIDANCE review: [M1_WP1_GUIDANCE_REVIEW.md](M1_WP1_GUIDANCE_REVIEW.md)
- Mentor meeting document: [MENTOR_BRIEF.md](MENTOR_BRIEF.md)
- **M4-WP0 ruling (PASS WITH ACTIONS):** [M4_WP0_GUIDANCE_RULING.md](M4_WP0_GUIDANCE_RULING.md)
- **M4-WP0 review, merge authorization and M4-WP1 ruling (WP0 PASS):** [M4_WP0_REVIEW_MERGE_WP1_GUIDANCE_RULING.md](M4_WP0_REVIEW_MERGE_WP1_GUIDANCE_RULING.md)
- **M4-WP0 report:** [../reports/milestones/M4_WP0_REPORT.md](../reports/milestones/M4_WP0_REPORT.md)
- **M4-WP1 report:** [../reports/milestones/M4_WP1_REPORT.md](../reports/milestones/M4_WP1_REPORT.md); **pilot claims:** [LITERATURE_WP1_PILOT.md](LITERATURE_WP1_PILOT.md)
- **Query scope:** [LITERATURE_QUERY_SCOPE.md](LITERATURE_QUERY_SCOPE.md); **corpus inventory:** [LITERATURE_CORPUS_INVENTORY.md](LITERATURE_CORPUS_INVENTORY.md)
- The pinned query and the corpus identity: [../data/MANIFEST.md](../data/MANIFEST.md)
- Operating rules: [../CLAUDE.md](../CLAUDE.md)
