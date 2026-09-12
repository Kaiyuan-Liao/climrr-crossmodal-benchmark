# Project state

One screen. **Refresh this file at the end of every work package.** A stale
state file is worse than a thin one: the M0 cold-resume trial showed a fresh
session reasoning correctly from out-of-date facts and repeating them.

| | |
| --- | --- |
| **Current milestone** | **M1 --- data grounding and metadata audit** |
| **Active task** | **M1-WP2 complete as issued.** WP2a built the machinery; WP2b recorded the 2026-09-10 meeting. **Nothing is in progress** --- the project is waiting on a decision |
| **Latest accepted commit** | `62c9137` --- the merge of M1-WP1 into `main`, accepted by GUIDANCE at reviewed head `fceee7f` (D-009) |
| **Sophia-verified commit** | `2b7345f` --- the pinned commit the cross-host reproduction ran at |
| **Branch** | `work/m1-wp2`. **Pushed by Kaiyuan**; `origin/work/m1-wp2` is at `53421f0`, and the WP2b commit is local until he pushes it. `main` carries the WP1 merge. The EXECUTOR does not push (D-003) |
| **M0 gate** | **PASSED --- PASS WITH ACTIONS**, GUIDANCE, at commit `b87564b` (D-006) |
| **M1-WP1 review** | **PASS**, GUIDANCE, at reviewed head `fceee7f` (D-009). A work-package pass, **not** the M1 milestone gate |
| **Tag `m0-setup`** | to be applied by Kaiyuan |
| **Next review event** | **GUIDANCE ruling on D-010**, and with it the review of M1-WP2 against the nine acceptance criteria in `M1_WP1_GUIDANCE_REVIEW.md` |
| **Blockers** | **M1 is blocked on the GUIDANCE ruling on D-010.** The mentor answers M1 was waiting for **are not coming** (R-001, 2026-09-10), and no further EXECUTOR work is authorised until D-010 is ruled on |

## Where things stand

- **The 2026-09-10 mentor meeting changed the problem, not the data.** Two
  answers, both recorded in `data/metadata/resolutions.yaml`, both changing no
  column:
  - **R-001 --- there is no further documentation.** No newer data dictionary,
    no assembly document or script, no release note. **Q0 is closed, answered in
    the negative.** Two of the three evidence types D-009 accepts for promoting
    a stem-to-section mapping are therefore **unavailable, not merely
    unobtained**.
  - **R-002 --- a direction, not a semantic.** Use the fields that are reliable
    or reasonably explainable, let reasoning fill in the rest, treat each row as
    one event, connect events to the literature, show examples. **No per-column
    answer was given for any of Q1--Q18.**

  Both statements are Kaiyuan's paraphrase relayed 2026-09-12 and are marked as
  paraphrase, not verbatim.
- **D-010 is PROPOSED and nothing in it is implemented.** It would add a fifth
  status `inferred_candidate` for semantics reached by recorded reasoning,
  confine interpretation to a pilot subset, build 2--3 example event records from
  real rows with every assumption listed, and make **mentor sign-off on an
  example** the thing that promotes the columns it uses. **It awaits a GUIDANCE
  ruling and Kaiyuan's approval.** No `inferred_candidate` status exists in the
  code, no column was interpreted, no subset was chosen, no example was built.
- **"Each row = one event" is Kaiyuan's reading, not the mentor's words.** It is
  the grain the whole proposed pilot rests on and it is **still to be confirmed
  with her, by showing examples**. Nothing depends on it yet.
- **Metadata status is unchanged at 21 / 143 / 28 / 83** and `resolution_refs`
  is empty on all 275 columns. Two resolution records are applied and move
  nothing; `status_diff.py` reports 0 changes and 0 invariant violations.
- **One question was answered without the mentor. Q11.4: indices 235 and 236 are
  not the same column.** `OBJECTID_12` and `OBJECTID_12_13` are equal in 83 of
  62,834 rows, and those 83 are exactly the rows where both are empty; they
  differ in all 62,751 populated rows. Their empty-row sets are identical, each
  holds 62,752 distinct values, and **703 values occur in one and not the
  other** --- so not a duplicate and not a reordering. It removes a candidate
  explanation rather than supplying one; the rest of Q11 stays open.
- **Four GUIDANCE rulings from D-009 remain in force.** Strict
  `verified_from_dictionary` bar; candidate maps for navigation only; index 117
  kept with `-9` unlabelled; D-008 stated, not verified. D-010 would loosen the
  premise of the first, which is exactly why it needs a ruling rather than an
  assumption.
- **The resolution machinery works and stays inert.** `resolutions.yaml` holds
  R-001 and R-002; `status_baseline_wp1` and `resolution_refs` carry the audit
  trail; `owner_confirmed` exists and **no record can ever produce
  `verified_from_dictionary`**. WP2b added `effect: null` for an answer that
  changes nothing and `statement_fidelity` to mark a paraphrase as one.
- **Page 3 of the dictionary PDF is blank** (WP2a) --- no table, no field names,
  nothing bearing on the 275 columns.
- **`pypdfium2==5.13.0` is in the D-007 pin set.** **Sophia must re-run
  `pip install -r requirements.txt`** before its next pinned checkout.
- **All 275 columns are profiled** and the WP1 cross-host reproduction stands:
  profile content hash
  `772991c7c9adf475c2ca51806998494595d445725d6d3b7d5046752074fcba9c` on both
  hosts, 275/275 agreement on the pandas cross-check.
- **D-005/D-006/D-007 hold.** Every run verified the manifest SHA-256 before
  reading, fail-closed. `CLIMRR_ALLOW_MISSING_RAW=1` was never set.

## Outstanding

- **For GUIDANCE: rule on D-010.** Two authorisations are needed, not one --- the
  `inferred_candidate` status itself, and **hand-worked example construction
  ahead of M2**, since building event records from real rows is an M2
  deliverable and doing it during M1 is a deliberate reordering. **Everything
  else in M1 is waiting on this.**
- **For Kaiyuan:** approve or reject D-010 as project owner; and, once examples
  exist, **confirm with the mentor that one row = one event**. Also the Sophia
  reinstall above.
- **Q1--Q18 are marked "mentor: no answer available"** in
  [`METADATA_QUESTIONS.md`](METADATA_QUESTIONS.md), with the resolution path
  pending D-010. Q0 is closed; Q11.4 is answered from the bytes. Q1, Q7, Q8 and
  Q17 still block downstream *use* of the columns they name.
- **Export date** of the ClimRR file remains unknown and was not guessed (Q18) ---
  and R-001 means no release note exists to settle it.

## Next

**Nothing until GUIDANCE rules on D-010.** If it is granted: build 2--3 example
event records from real rows, each listing every assumption and naming the
columns it uses, for Kaiyuan to put in front of the mentor; her sign-off becomes
an ordinary resolution record naming those columns. If it is refused: close M1
with the 21 dictionary-verified columns and an explicit, permanent record of the
other 254 as undocumented.

Still not authorised: phenomenon extraction, aggregation for scientific claims,
thresholds, literature work, embeddings, bridges, QA --- **and, until D-010 is
ruled on, any interpretation of a column.**

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
