# Project state

One screen. **Refresh this file at the end of every work package.** A stale
state file is worse than a thin one: the M0 cold-resume trial showed a fresh
session reasoning correctly from out-of-date facts and repeating them.

| | |
| --- | --- |
| **Current milestone** | M0 --- reproducible project foundation |
| **Active task** | M0-WP1 --- complete, awaiting gate review |
| **Latest work-package commit** | `c91e30d` (this file's pointer is written in the bookkeeping commit that follows it, since a commit cannot contain its own hash) |
| **Proposed gate status** | **PASS** --- all five criteria MET on evidence |
| **Next review event** | **M0 gate review by GUIDANCE** |
| **Blockers** | **none** |

## Where things stand

- [`docs/BLUEPRINT.md`](BLUEPRINT.md) is in the repository and is the project
  charter. [`PROJECT_PLAN.md`](PROJECT_PLAN.md) carries all six milestone
  objectives and gate-criteria sets verbatim from it (verified byte-identical);
  [`REPORT_TEMPLATE.md`](REPORT_TEMPLATE.md) matches blueprint section 9. The
  M1--M5 criteria gap is **resolved**.
- Raw data verified byte-identical on both hosts:
  `e87ac2cd…3bf43e`, 296,407,423 bytes, 62,834 x 275. Untracked by D-005 and
  transferred out of band; pinned by `data/manifest.json`.
- All five M0 gate criteria MET, including criterion 5, tested 2026-09-08 by an
  independent cold session.
- `origin/main` is at `586f5fd`. Later commits are local; the EXECUTOR does not
  push (D-003), and every piece of gate evidence is already on the remote.
- Decisions D-002, D-003, D-004, D-005 decided; D-001 superseded by D-005.

## Residual items (none blocking)

- **GUIDANCE to confirm** that D-005's out-of-band transfer is an acceptable
  mechanism for pinning the raw data. Byte identity is met and proven across
  two architectures; the mechanism is the open question.
- **Python version skew**: local 3.11.16 vs Sophia 3.13.13, different
  `pip freeze` fingerprints. Immaterial to M0, where every check is a checksum
  or a count. Revisit pinning at M2, when numerical output begins.
- **Acquisition date** of the ClimRR export is unknown and was not guessed.

## Next

M0 gate review by GUIDANCE. Do **not** tag `m0-setup` until the gate passes.
Proposed next objective is in field 15 of the M0 report.

## Links

- Charter: [BLUEPRINT.md](BLUEPRINT.md)
- Plan and gate criteria: [PROJECT_PLAN.md](PROJECT_PLAN.md)
- Decisions: [DECISION_LOG.md](DECISION_LOG.md)
- Data facts and column inventory: [DATA_NOTES.md](DATA_NOTES.md)
- Sophia procedure: [SOPHIA_RUNBOOK.md](SOPHIA_RUNBOOK.md)
- Active milestone report: [../reports/milestones/M0_SETUP_REPORT.md](../reports/milestones/M0_SETUP_REPORT.md)
- Operating rules: [../CLAUDE.md](../CLAUDE.md)
