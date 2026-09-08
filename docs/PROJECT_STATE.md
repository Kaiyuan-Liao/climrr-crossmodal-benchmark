# Project state

Single screen. Update it at the end of every work package.

| | |
| --- | --- |
| **Current milestone** | M0 --- reproducible project foundation |
| **Active task** | M0-WP1 --- **complete**, awaiting gate review |
| **Latest accepted commit** | the M0-WP1 close commit --- SHA recorded in the follow-up commit below |
| **Next review event** | **M0 gate review by GUIDANCE** |
| **Proposed gate status** | **PASS** --- see report section 14 |

## Completed outputs

- Repository skeleton, `CLAUDE.md`, plan / state / decision log / data notes /
  report template.
- `src/climrr/` (paths, checksums, run records), `scripts/smoke_test.py`,
  `scripts/verify_no_secrets_or_paths.py`, `tests/`.
- `data/raw/FullData.csv` copied byte-identically from source
  (62,834 rows x 275 columns) and hash-pinned in `data/manifest.json`. It is
  **untracked** by decision D-005 and moves out of band. The `data/metadata/`
  data dictionary is tracked and hashed.
- Sophia bootstrap / pinned-pull scripts and `docs/SOPHIA_RUNBOOK.md`.
- **Sophia evidence returned and committed**: at commit `586f5fd` on
  `sophia-login-02`, the same SHA-256 `e87ac2cd...3bf43e` and 296,407,423 bytes
  were reproduced, with 31 tests passing, the smoke test PASS, the push URL
  `DISABLED`, and a clean tracked working tree.
  (`reports/runs/20260908T191426Z_sophia_smoke_test.json`)
- `reports/milestones/M0_SETUP_REPORT.md` --- all 15 fields complete, nothing
  PENDING.

## Blockers

None blocking. Residual items carried into the gate review:

- **Push to `origin main` not yet done.** Commits are ready locally; Kaiyuan
  pushes manually. Not blocking --- Sophia has already run.
- **GUIDANCE to confirm** that D-005's out-of-band data policy satisfies gate
  criteria 1 and 4 in spirit.
- **Python version skew**: local 3.11.16 vs Sophia 3.13.13, different
  `pip freeze` fingerprints. A known limitation of D-004, immaterial to M0
  where every check is a checksum or a count. Revisit pinning at M2.

## Resolved since last update

- **D-005 decided** (supersedes D-001): the raw CSV is untracked and
  transferred out of band, pinned by SHA-256. History verified never to have
  contained the blob; repository is 643 KiB packed.
- **D-002 decided**: the ClimRR data dictionary is tracked under
  `data/metadata/` as authoritative metadata, not literature. M1 may cite it as
  evidence for column semantics.
- **Sophia byte identity confirmed** across two architectures --- the gap that
  D-005 opened by moving the data pin off the commit is now closed by evidence.
- **Blueprint size discrepancy resolved**: the ~48 MB figure was a
  compressed-upload artifact; row and column counts matched exactly.
- **`git_dirty` semantics fixed** in `src/climrr/runrecord.py`: it now reports
  tracked changes only, with untracked files counted separately. The Sophia
  record's `dirty=True` came from an untracked stray `.log` file, since deleted
  on Sophia; the record is committed verbatim and the report carries the
  explanation.

## Links

- Plan and gate criteria: [PROJECT_PLAN.md](PROJECT_PLAN.md)
- Decisions: [DECISION_LOG.md](DECISION_LOG.md)
- Data facts and column inventory: [DATA_NOTES.md](DATA_NOTES.md)
- Sophia procedure: [SOPHIA_RUNBOOK.md](SOPHIA_RUNBOOK.md)
- Active milestone report: [../reports/milestones/M0_SETUP_REPORT.md](../reports/milestones/M0_SETUP_REPORT.md)
- Operating rules: [../CLAUDE.md](../CLAUDE.md)
