# Project state

One screen. **Refresh this file at the end of every work package.** A stale
state file is worse than a thin one: the M0 cold-resume trial showed a fresh
session reasoning correctly from out-of-date facts and repeating them.

| | |
| --- | --- |
| **Current milestone** | **M1 --- data grounding and metadata audit** |
| **Active task** | **M1-WP1** --- work package pending from COORDINATOR |
| **Latest accepted commit** | `c08de42` --- M0 closure (this file's pointer is written in the bookkeeping commit that follows it, since a commit cannot contain its own hash) |
| **M0 gate** | **PASSED --- PASS WITH ACTIONS**, GUIDANCE, at commit `b87564b` (D-006) |
| **Tag `m0-setup`** | to be applied by Kaiyuan --- **not present in this clone or on the remote** as of this commit |
| **Next review event** | M1 gate review by GUIDANCE, after M1-WP1 |
| **Blockers** | **none** |

## Where things stand

- **M0 is closed.** All five charter gate criteria met on evidence, including
  criterion 5, tested by an independent cold session rather than asserted.
  GUIDANCE accepted the gate as PASS WITH ACTIONS; closure actions are done.
  See [`../reports/milestones/M0_SETUP_REPORT.md`](../reports/milestones/M0_SETUP_REPORT.md).
- **D-005 is permanent** (D-006), not a workaround: the raw CSV stays
  untracked, moves out of band, and is pinned by SHA-256 in
  `data/manifest.json`. **Fail-closed verification before any data use is
  mandatory** --- the checks must fail rather than skip when the file is
  absent, and `CLIMRR_ALLOW_MISSING_RAW=1` must never be set during a gate run.
- Raw data verified byte-identical on both hosts: `e87ac2cd…3bf43e`,
  296,407,423 bytes, 62,834 x 275.
- [`BLUEPRINT.md`](BLUEPRINT.md) is the charter; [`PROJECT_PLAN.md`](PROJECT_PLAN.md)
  carries all six objectives and gate-criteria sets verbatim from it.
- `origin/main` is at `586f5fd`; later commits are local. The EXECUTOR does not
  push (D-003).
- Decisions D-002 .. D-007 decided; D-001 superseded by D-005; D-004 amended by
  D-007.

## Residual items (none blocking)

- **Pin the parsing and profiling libraries during M1-WP1** (D-007), in
  `requirements.txt` and in run records, **before** the schema/profile artifact
  is frozen. The two hosts need not share a Python minor version.
- **Acquisition date** of the ClimRR export is unknown and was not guessed.

## Next

M1-WP1: reproducible schema and quality profile of `FullData.csv` --- a
machine-readable per-column profile with identifiers read as strings and **no
interpretation**, plus an inventory of metadata questions checked against the
tracked data dictionary. Awaiting the work package from COORDINATOR.

## Links

- Charter: [BLUEPRINT.md](BLUEPRINT.md)
- Plan and gate criteria: [PROJECT_PLAN.md](PROJECT_PLAN.md)
- Decisions: [DECISION_LOG.md](DECISION_LOG.md)
- Data facts and column inventory: [DATA_NOTES.md](DATA_NOTES.md)
- Sophia procedure: [SOPHIA_RUNBOOK.md](SOPHIA_RUNBOOK.md)
- M0 report (accepted): [../reports/milestones/M0_SETUP_REPORT.md](../reports/milestones/M0_SETUP_REPORT.md)
- Operating rules: [../CLAUDE.md](../CLAUDE.md)
