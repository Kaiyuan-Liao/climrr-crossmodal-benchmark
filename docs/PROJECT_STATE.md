# Project state

One screen. **Refresh this file at the end of every work package.** A stale
state file is worse than a thin one: the M0 cold-resume trial showed a fresh
session reasoning correctly from out-of-date facts and repeating them.

| | |
| --- | --- |
| **Current milestone** | **M1 --- data grounding and metadata audit** |
| **Active task** | **M1-WP2 --- metadata resolution and citable column dictionary.** WP2a (machinery, page-3 check, mentor brief) in progress; **WP2b awaits mentor answers** |
| **Latest accepted commit** | `62c9137` --- the merge of M1-WP1 into `main`, accepted by GUIDANCE at reviewed head `fceee7f` (D-009) |
| **Sophia-verified commit** | `2b7345f` --- the pinned commit the cross-host reproduction ran at |
| **Branch** | `work/m1-wp2`, local only and **not pushed**; `main` carries the WP1 merge |
| **M0 gate** | **PASSED --- PASS WITH ACTIONS**, GUIDANCE, at commit `b87564b` (D-006) |
| **M1-WP1 review** | **PASS**, GUIDANCE, at reviewed head `fceee7f` (D-009). A work-package pass, **not** the M1 milestone gate |
| **Tag `m0-setup`** | to be applied by Kaiyuan |
| **Next review event** | **GUIDANCE review of M1-WP2** against the nine acceptance criteria in `M1_WP1_GUIDANCE_REVIEW.md` |
| **Blockers** | **M1-WP2b is blocked on mentor answers.** Nothing else. The questions are in `MENTOR_BRIEF.md` for the meeting on **2026-09-10** |

## Where things stand

- **M1-WP1 is accepted and merged.** GUIDANCE recorded PASS at reviewed head
  `fceee7f`; the merge commit on `main` is `62c9137`. The acceptance and its
  four standing rulings are D-009. The WP1 report
  [`../reports/milestones/M1_DATA_GROUNDING_REPORT.md`](../reports/milestones/M1_DATA_GROUNDING_REPORT.md)
  is **frozen as the WP1-stage record**; current M1 status is in
  [`../reports/milestones/M1_WP2_REPORT.md`](../reports/milestones/M1_WP2_REPORT.md).
- **Four GUIDANCE rulings are in force (D-009).** The strict
  `verified_from_dictionary` bar is confirmed and must not be loosened; the two
  EXECUTOR candidate maps are approved for navigation and question-writing only
  and can never promote a column; index 117 stays in the inventory with its `-9`
  unlabelled; D-008 stays a stated, unverified provenance statement.
- **M1-WP2 is split.** **WP2a --- this package --- builds the machinery and the
  documents and changes no column status**, because no answer exists yet.
  **WP2b applies mentor answers as they arrive**, one commit per meeting.
- **The resolution machinery exists and is inert.**
  `data/metadata/resolutions.yaml` is tracked and empty;
  `src/climrr/dictionary.py` applies resolution records on top of the dictionary
  rules; `scripts/status_diff.py` prints every change against the WP1 baseline
  with the R-record and D-number responsible. A **new status `owner_confirmed`**
  exists for mentor/owner-confirmed semantics, deliberately distinct from
  `verified_from_dictionary`, **which no resolution record can ever produce.**
  A record promotes a column only if it names the column indices or a stem-to-section
  map explicitly; matching an answer to columns by pattern is refused.
- **Metadata status is unchanged at 21 / 143 / 28 / 83** ---
  `verified_from_dictionary` / `partially_resolved` / `unresolved` /
  `structurally_observed_only` --- and `resolution_refs` is empty on all 275
  columns. That is the intended WP2a outcome, not a shortfall.
- **The PDF-completeness action is discharged. Page 3 is blank.** Rendered at
  200 dpi it is a uniform white page --- no table, no field names, no figure ---
  between the contents on page 2 and the narrative on page 4, which both render
  fully as a control. See `DATA_NOTES.md` §1 and D-009.
- **`pypdfium2==5.13.0` joins the D-007 pin set** for that rendering. **Sophia
  must re-run `pip install -r requirements.txt`** before its next pinned
  checkout, or run records will carry `matches_pin: false` and
  `tests/test_runrecord.py` will fail --- by design.
- **`docs/MENTOR_BRIEF.md` is the meeting document.** Plain language, under two
  screens, questions in the GUIDANCE priority order, with an empty answers table
  and meeting log that WP2b fills in.
- **All 275 columns are profiled** and the cross-host reproduction stands: the
  profile content hash
  `772991c7c9adf475c2ca51806998494595d445725d6d3b7d5046752074fcba9c` was produced
  identically on local Python 3.11.16 / macOS arm64 and Sophia Python 3.13.13 /
  x86_64, with 275/275 agreement on the pandas cross-check.
- **D-005/D-006/D-007 hold.** Every run verifies the manifest SHA-256 before
  reading, fail-closed. `CLIMRR_ALLOW_MISSING_RAW=1` was never set.
- The EXECUTOR still does not push (D-003).

## Outstanding

- **For Kaiyuan: bring `MENTOR_BRIEF.md` to the mentor meeting on 2026-09-10**
  and paste the answers back to the COORDINATOR afterwards. That is the only
  thing standing between WP2a and WP2b.
- **For Sophia, before the next pinned checkout:** re-run
  `pip install -r requirements.txt` so `pypdfium2==5.13.0` is present.
- **18 metadata questions** in [`METADATA_QUESTIONS.md`](METADATA_QUESTIONS.md),
  all for the mentor or the ClimRR authors. GUIDANCE's priority order is Q1, Q7,
  Q8, the geographic/join-key questions Q10--Q12, the sentinel questions Q17 and
  Q9, export provenance Q18, then Q2--Q6 and Q13--Q16. Q1, Q7, Q8 and Q17 block
  downstream *use* of the columns they name.
- **Export date** of the ClimRR file remains unknown and was not guessed (Q18).

## Next

**M1-WP2b --- apply the mentor answers from the 2026-09-10 meeting.** For each
answer: one R-record in `data/metadata/resolutions.yaml`, one decision-log entry,
a regenerated `dictionary_coverage.json`, and a `status_diff.py` run showing
exactly which columns moved and on whose authority. Answers that name no columns
and no stem map change nothing, by construction.

Still not authorised: phenomenon extraction, aggregation for scientific claims,
thresholds, literature work, embeddings, bridges, QA.

## Links

- Charter: [BLUEPRINT.md](BLUEPRINT.md)
- Plan and gate criteria: [PROJECT_PLAN.md](PROJECT_PLAN.md)
- Decisions, including D-008 provenance: [DECISION_LOG.md](DECISION_LOG.md)
- Data facts, dictionary-verified semantics, open questions: [DATA_NOTES.md](DATA_NOTES.md)
- Mentor-facing question inventory: [METADATA_QUESTIONS.md](METADATA_QUESTIONS.md)
- Sophia procedure, including M1-WP1 reproduction: [SOPHIA_RUNBOOK.md](SOPHIA_RUNBOOK.md)
- M0 report (accepted): [../reports/milestones/M0_SETUP_REPORT.md](../reports/milestones/M0_SETUP_REPORT.md)
- M1-WP1 report, frozen at the WP1 stage: [../reports/milestones/M1_DATA_GROUNDING_REPORT.md](../reports/milestones/M1_DATA_GROUNDING_REPORT.md)
- M1-WP2 report, current M1 status: [../reports/milestones/M1_WP2_REPORT.md](../reports/milestones/M1_WP2_REPORT.md)
- M1-WP1 GUIDANCE review: [M1_WP1_GUIDANCE_REVIEW.md](M1_WP1_GUIDANCE_REVIEW.md)
- Mentor meeting document: [MENTOR_BRIEF.md](MENTOR_BRIEF.md)
- M0 gate review and the nine M1-WP1 acceptance criteria: [M0_GUIDANCE_GATE_REVIEW.md](M0_GUIDANCE_GATE_REVIEW.md)
- Operating rules: [../CLAUDE.md](../CLAUDE.md)
