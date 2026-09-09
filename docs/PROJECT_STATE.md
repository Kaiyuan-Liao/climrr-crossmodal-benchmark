# Project state

One screen. **Refresh this file at the end of every work package.** A stale
state file is worse than a thin one: the M0 cold-resume trial showed a fresh
session reasoning correctly from out-of-date facts and repeating them.

| | |
| --- | --- |
| **Current milestone** | **M1 --- data grounding and metadata audit** |
| **Active task** | **M1-WP1 complete on branch `work/m1-profile`** --- awaiting GUIDANCE WP1 review |
| **Latest accepted commit** | `c08de42` --- M0 closure. M1-WP1 work is on a branch and **not merged** |
| **M1-WP1 branch head** | `92ae2dc` plus the report commit that follows it |
| **M0 gate** | **PASSED --- PASS WITH ACTIONS**, GUIDANCE, at commit `b87564b` (D-006) |
| **Tag `m0-setup`** | to be applied by Kaiyuan |
| **Next review event** | **GUIDANCE review of M1-WP1** against the nine acceptance criteria in `M0_GUIDANCE_GATE_REVIEW.md` |
| **Blockers** | **none.** One acceptance item is outstanding: the Sophia reproduction, which only Kaiyuan can run |

## Where things stand

- **M1-WP1 is complete and reported.** See
  [`../reports/milestones/M1_DATA_GROUNDING_REPORT.md`](../reports/milestones/M1_DATA_GROUNDING_REPORT.md).
  Eight in-repo runs, all PASS; `pytest` 193 passed; secrets/paths scan 0 hits.
- **Profile content hash:**
  `772991c7c9adf475c2ca51806998494595d445725d6d3b7d5046752074fcba9c`.
  This is the value Sophia must reproduce. It covers every computed fact and
  rule constant and excludes hostname, Python version, pinned versions and the
  commit, so it is comparable across the two hosts' different Python versions.
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
- **D-005/D-006 hold.** Every one of the eight runs verified the CSV SHA-256
  against the manifest before reading, fail-closed, and the Phase D runs also
  verified the PDF. `CLIMRR_ALLOW_MISSING_RAW=1` was never set.
- Decisions D-002 .. D-007 decided; D-001 superseded by D-005; D-004 amended by
  D-007. **No new decision was made in M1-WP1** --- the pin set is a dated note
  under D-007, not a new entry.
- `origin/main` is at `586f5fd`; everything since is local. The EXECUTOR does
  not push (D-003), and `work/m1-profile` is neither pushed nor merged.

## Outstanding

- **Sophia reproduction of the profile content hash.** Runbook section 5b is
  written and its commands were tested locally, including with output directed
  outside the repo. Only Kaiyuan can run it. This is the one open acceptance
  item.
- **18 metadata questions** in [`METADATA_QUESTIONS.md`](METADATA_QUESTIONS.md),
  with an ownership table. Q1 (is the CSV eleven layers joined side by side?),
  Q7 (the 56 undocumented `precipdaily_*` columns), Q8 (the 30 FWI-class
  columns) and Q17 (is any flagged value a fill code?) block downstream *use* of
  the columns they name --- not this work package.
- **Three questions for GUIDANCE** in report field 13: whether the
  `verified_from_dictionary` bar is set correctly, whether the two
  EXECUTOR-authored candidate maps are acceptable, and whether index 117
  (`-9` on all 62,834 rows) may be excluded from downstream use.
- **Acquisition date** of the ClimRR export remains unknown and was not guessed.

## Next

Await the GUIDANCE M1-WP1 review and Kaiyuan's Sophia run. The proposed next
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
- Decisions: [DECISION_LOG.md](DECISION_LOG.md)
- Data facts, dictionary-verified semantics, open questions: [DATA_NOTES.md](DATA_NOTES.md)
- Mentor-facing question inventory: [METADATA_QUESTIONS.md](METADATA_QUESTIONS.md)
- Sophia procedure, including M1-WP1 reproduction: [SOPHIA_RUNBOOK.md](SOPHIA_RUNBOOK.md)
- M0 report (accepted): [../reports/milestones/M0_SETUP_REPORT.md](../reports/milestones/M0_SETUP_REPORT.md)
- M1-WP1 report: [../reports/milestones/M1_DATA_GROUNDING_REPORT.md](../reports/milestones/M1_DATA_GROUNDING_REPORT.md)
- M0 gate review and the nine M1-WP1 acceptance criteria: [M0_GUIDANCE_GATE_REVIEW.md](M0_GUIDANCE_GATE_REVIEW.md)
- Operating rules: [../CLAUDE.md](../CLAUDE.md)
