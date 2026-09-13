# Project state

One screen. **Refresh this file at the end of every work package.** A stale
state file is worse than a thin one: the M0 cold-resume trial showed a fresh
session reasoning correctly from out-of-date facts and repeating them.

| | |
| --- | --- |
| **Current milestone** | **M1 --- data grounding and metadata audit** |
| **Active task** | **M1-WP3 complete, pre-meeting reviewed, and revised.** **M1-WP3b --- a prototype package --- is built on the unmerged, unpushed branch `work/m1-wp3b`.** The project is waiting on **the group, 2026-09-14**, **the mentor, 2026-09-17**, and **a GUIDANCE ruling on WP3b** |
| **Latest accepted commit** | `62c9137` --- the merge of M1-WP1 into `main`, accepted by GUIDANCE at reviewed head `fceee7f` (D-009) |
| **Sophia-verified commit** | `2b7345f` --- the pinned commit the cross-host reproduction ran at |
| **Branch** | `work/m1-wp3`, from `work/m1-wp2`. **Pushed by Kaiyuan, not merged.** `origin/work/m1-wp3` was at `c8f4711` when GUIDANCE took the pre-meeting review; the revision commit after it is local until he pushes again. The EXECUTOR does not push (D-003) |
| **M1-WP3b branch** | **`work/m1-wp3b`, from `work/m1-wp3` at `ad13649`. Not merged, not pushed** --- the work package forbids both, and `origin` has no such branch. Four commits: Phase A, Phases B–D, Phase E, the post-ruling fixes (D-013) |
| **M0 gate** | **PASSED --- PASS WITH ACTIONS**, GUIDANCE, at commit `b87564b` (D-006) |
| **M1-WP1 review** | **PASS**, GUIDANCE, at reviewed head `fceee7f` (D-009). A work-package pass, **not** the M1 milestone gate |
| **D-010 ruling** | **PASS WITH ACTIONS**, GUIDANCE, 2026-09-13. **D-010 decided; D-011 records the ruling and its boundaries.** Both approved by Kaiyuan |
| **M1-WP3 pre-meeting review** | **REVISE --- framing only**, GUIDANCE, 2026-09-13, at reviewed head `c8f4711` (D-012). The scientific design is **accepted**: subset, rows, IC records, generated presentation, cautions and mentor protocol all approved unchanged. The required framing revision **is done** |
| **M1-WP3b ruling** | **PASS WITH ACTIONS**, GUIDANCE, 2026-09-13, recorded as **D-013**. M1-WP3b is admitted as an explicit **milestone-order exception** --- early M3-style validation while M1 is still open. **The four required changes are applied.** Nothing in the package is milestone evidence; every record carries `validation_only` and the banner "Prototype for scientific-object validation. Not an accepted phenomenon record.", and its report proposes no gate status |
| **The ruling as placed** | **`docs/M1_WP3B_GUIDANCE_RULING.md` is in the repository**, placed by Kaiyuan 2026-09-13 --- **after** D-013 was written from the COORDINATOR's relay. It has been read back against D-013: **the substance agrees, and six discrepancies of attribution and coverage were found**, two of them real gaps against required actions 5 and 11. They are listed in the WP3b report, field 13; **neither document was edited to resolve them** |
| **Next review event** | **The mentor**, on `docs/MENTOR_EXAMPLES.md` --- the group meeting 2026-09-14 and the one-on-one **2026-09-17**, which is the one GUIDANCE names for the examples. GUIDANCE states no remaining scientific objection |
| **Blockers** | **M1 is blocked on mentor answers to the three examples.** M1-WP3b is blocked on nothing --- it is complete as a prototype and inert; what it *produces* is blocked on the GUIDANCE ruling and on the group's answer to what a phenomenon's unit should be |

## Where things stand

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
- **`docs/MENTOR_EXAMPLES.md` is what goes to the meeting.** Sixteen numbered
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

- **For the mentor, through the examples:** is one row one "event"; does the
  stem `tempmaxann` denote "Temperature Maximum - Annual" (**101 columns** turn
  on it); which Census vintage are `GEOID` and `TRACTCE`; and is this the shape
  of record she expects to connect to literature.
- **Two required actions of the WP3b ruling are not met**, found by reading the
  ruling back against D-013. Action 5 asks that an unweighted mean be labelled
  **"provisional aggregation rule for representation validation"** verbatim; the
  records label it `unweighted_mean` with A-AGG1 and A-G2. Action 11 asks the
  assumptions register to carry a **failure mode** per assumption; it has no such
  column. Both are listed in the WP3b report, field 13, and **neither was fixed
  in the verification pass** --- the instruction was to list rather than edit.
- **For the group, 2026-09-14:** `docs/GROUP_MEETING_2026-09-14.md` --- the three
  prototypes, the question types they could and could not support, and **five
  questions**, of which the first two matter most: what the unit of a phenomenon
  should be, and what replaces PR-1.
- **For Kaiyuan:** take `docs/MENTOR_EXAMPLES.md` to the 2026-09-14 group
  meeting and the **2026-09-17** one-on-one, and **preserve the answers
  distinguishing
  explicit confirmation from correction, from broad approval, and from an
  unanswered assumption** --- WP4 cannot promote anything without that
  distinction. Also push the branch, and the Sophia reinstall above.
- **For GUIDANCE: nothing outstanding on M1-WP3.** Both judgements field 13 of
  the report asked for were ruled on in the pre-meeting review and are recorded
  as D-012 --- **41 columns approved, the stem probe kept, the three cautions
  approved as repository-level rendering rules, criterion 6 met by the
  architecture, the hash disclosure accepted with no rerun.** The next GUIDANCE
  event is the M1 milestone gate, after WP4.
- **Q7, Q8, Q9, Q11, Q12, Q15, Q17, Q18 are untouched by WP3** and still block
  downstream use of the columns they name. Q0 is closed; Q11.4 is answered from
  the bytes; Q1, Q10, Q13 and Q14 are now asked concretely through the examples.
- **Export date** of the ClimRR file remains unknown and was not guessed (Q18).

## Next

**Nothing until the mentor answers.** Then **M1-WP4**: apply her feedback,
promote **only explicitly confirmed** semantics to `owner_confirmed` through
resolution records naming exactly which columns and exactly what was confirmed,
and assemble the M1 milestone gate packet. A broad "yes, this is what I want" is
recorded as approval of the approach and promotes nothing.

Still not authorised by any ruling: phenomenon extraction, aggregation for
scientific claims, thresholds, literature work, embeddings, bridges, QA --- and
any interpretation of a column outside the 41 in the pilot subset. **M1-WP3b
crosses the first three of those deliberately, on the owner's decision and
ahead of a ruling, which is why it is unmerged, unpushed, versioned
`p0-prototype`, and offered as no milestone's evidence.** Nothing outside the
41 columns was interpreted.

## Links

- Charter: [BLUEPRINT.md](BLUEPRINT.md)
- Plan and gate criteria: [PROJECT_PLAN.md](PROJECT_PLAN.md)
- Decisions, including D-010, D-011, D-012 and **D-013**: [DECISION_LOG.md](DECISION_LOG.md)
- The ruling that authorised WP3: [M1_D010_GUIDANCE_RULING.md](M1_D010_GUIDANCE_RULING.md)
- The pre-meeting review of WP3 (**REVISE**, framing only): [M1_WP3_PREMEETING_GUIDANCE_REVIEW.md](M1_WP3_PREMEETING_GUIDANCE_REVIEW.md)
- The pilot subset, its rationale and its exclusions: [PILOT_SUBSET.md](PILOT_SUBSET.md)
- **What goes to the mentor:** [MENTOR_EXAMPLES.md](MENTOR_EXAMPLES.md)
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
- Operating rules: [../CLAUDE.md](../CLAUDE.md)
