# Project state

One screen. **Refresh this file at the end of every work package.** A stale
state file is worse than a thin one: the M0 cold-resume trial showed a fresh
session reasoning correctly from out-of-date facts and repeating them.

| | |
| --- | --- |
| **Current milestone** | **M1 --- data grounding and metadata audit** |
| **Active task** | **M1-WP1 complete, all nine acceptance criteria met** --- awaiting GUIDANCE WP1 review |
| **Latest accepted commit** | `c08de42` --- M0 closure. M1-WP1 work is on a branch and **not merged** |
| **Sophia-verified commit** | `2b7345f` --- the pinned commit the cross-host reproduction ran at |
| **Branch** | `work/m1-profile`, pushed to `origin` as a branch by Kaiyuan; `origin/main` untouched at `586f5fd` |
| **M0 gate** | **PASSED --- PASS WITH ACTIONS**, GUIDANCE, at commit `b87564b` (D-006) |
| **Tag `m0-setup`** | to be applied by Kaiyuan |
| **Next review event** | **GUIDANCE review of M1-WP1** against the nine acceptance criteria in `M0_GUIDANCE_GATE_REVIEW.md` |
| **Blockers** | **none, and nothing outstanding.** The Sophia reproduction is done and the hashes match |

## Where things stand

- **M1-WP1 is complete and reported.** See
  [`../reports/milestones/M1_DATA_GROUNDING_REPORT.md`](../reports/milestones/M1_DATA_GROUNDING_REPORT.md).
  Seventeen run records --- 14 local, 3 Sophia --- all PASS; `pytest` 198 passed;
  secrets/paths scan 0 hits.
- **Cross-host reproduction is DONE and the hashes are identical.** Sophia, on
  Python 3.13.13 and glibc 2.34, at pinned commit `2b7345f` with a clean tree,
  produced the profile content hash
  `772991c7c9adf475c2ca51806998494595d445725d6d3b7d5046752074fcba9c` ---
  character for character the local value from Python 3.11.16 on macOS arm64.
  Every structural count matches, the cross-check agrees 275/275 with 0
  disagreements under pandas 3.0.5 / numpy 2.4.6, and all five `matches_pin`
  flags are true on both hosts. On Sophia `numpy==2.4.6` came from the ALCF base
  module through the venv's `--system-site-packages` rather than being
  reinstalled; the pin is met and what ran was 2.4.6.
- **All 275 columns are profiled**, read entirely as text: 62,834 x 275, **no
  duplicate column names**, no ragged rows, 248 all-decimal columns, 7
  all-integer, 2 carrying leading zeros (`TRACTCE` 29,467 values, `GEOID`
  19,074), 5 constant, 24 with a candidate-sentinel value. **A pandas re-read
  agrees on 275 of 275 columns, 0 disagreements.**
- **Metadata status of the 275 columns: 21 `verified_from_dictionary`, 143
  `partially_resolved`, 28 `unresolved`, 83 `structurally_observed_only`.**
  The low verified count is a property of the dictionary, not of the method ---
  it names its fields by suffix inside a per-variable section (`HIST`,
  `RCP45_MIDC`) while the CSV writes stem plus suffix (`tempmaxann_rcp45_midc`),
  and it never states that a stem denotes a section. **The EXECUTOR did not
  resolve that by inference**; it is question Q1 to Kaiyuan and would move 101
  columns.
- **D-007 is executed.** `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`,
  `pyyaml==6.0.3`, `pytest==9.1.1` are pinned in `requirements.txt`, recorded in
  every run record's new `pinned_libraries` field, and a test fails if the
  running environment drifts. Local Python 3.11.16, Sophia 3.13.13 --- the skew
  stays, deliberately.
- **D-005/D-006 hold.** Every run verified the manifest SHA-256 before reading,
  fail-closed --- fourteen runs for the CSV and six for the PDF, on both hosts.
  `CLIMRR_ALLOW_MISSING_RAW=1` was never set.
- **D-008 records Kaiyuan's provenance statement**, tagged *stated, not
  independently verified*: one file from ALCF via Box, downloaded directly about
  a week before 2026-09-08, no operation applied afterwards, and the download is
  explicitly not the creation time. It settles custody, not content ---
  **no column status changed**, and `data/manifest.json` still records
  `acquisition_date: "unknown"`.
- Decisions D-002 .. D-008 decided or recorded; D-001 superseded by D-005; D-004
  amended by D-007. The D-007 pin set is a dated note, not a new entry.
- `origin/main` is at `586f5fd`. `work/m1-profile` was pushed by Kaiyuan so
  Sophia could check out the pinned commit; `main` is untouched and nothing is
  merged. The EXECUTOR still does not push (D-003).
- **Runbook defect found in practice and fixed:** after Sophia run records are
  copied back and committed, the next pinned pull aborts because the untracked
  copies would be overwritten. `sophia_pull_pinned.sh` now explains the collision
  and prints the exact `rm` command without deleting anything; runbook section 7
  makes deleting the copies a required step.

## Outstanding

- **Nothing is outstanding for Kaiyuan.** The Sophia run is done and D-008 is
  recorded.
- **18 metadata questions** in [`METADATA_QUESTIONS.md`](METADATA_QUESTIONS.md),
  **all of them now for the mentor or the ClimRR authors** --- D-008 closed the
  Kaiyuan-side half of Q1, Q10, Q11 and Q18. Q1 (is the CSV eleven layers joined
  side by side?), Q7 (the 56 undocumented `precipdaily_*` columns), Q8 (the 30
  FWI-class columns) and Q17 (is any flagged value a fill code?) block downstream
  *use* of the columns they name --- not this work package.
- **Three questions for GUIDANCE** in report field 13: whether the
  `verified_from_dictionary` bar is set correctly, whether the two
  EXECUTOR-authored candidate maps are acceptable, and whether index 117
  (`-9` on all 62,834 rows) may be excluded from downstream use.
- **Export date** of the ClimRR file remains unknown and was not guessed. The
  download date is now approximately known (D-008); the export date is Q18, for
  the mentor.

## Next

Await the GUIDANCE M1-WP1 review. The proposed next
bounded objective is **M1-WP2 --- resolve the metadata inventory into a citable
column dictionary**: record each answer to Q1--Q18 as a dated decision with its
source, re-run the coverage with the confirmed stem-to-section map promoted from
EXECUTOR candidate to owner-confirmed evidence, and produce a per-column table
in which every column is either resolved with a citation or listed as
permanently undocumented.

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
- M1-WP1 report: [../reports/milestones/M1_DATA_GROUNDING_REPORT.md](../reports/milestones/M1_DATA_GROUNDING_REPORT.md)
- M0 gate review and the nine M1-WP1 acceptance criteria: [M0_GUIDANCE_GATE_REVIEW.md](M0_GUIDANCE_GATE_REVIEW.md)
- Operating rules: [../CLAUDE.md](../CLAUDE.md)
