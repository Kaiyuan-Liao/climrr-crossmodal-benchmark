# Project state

Single screen. Update it at the end of every work package.

| | |
| --- | --- |
| **Current milestone** | M0 --- reproducible project foundation |
| **Active task** | M0-WP1 (repository foundation, data placement, Sophia runbook) |
| **Latest accepted commit** | none yet --- M0 gate not passed; six commits pending push |
| **Next review event** | M0 gate, after Sophia evidence returns |

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
- `reports/milestones/M0_SETUP_REPORT.md`.

## Blockers

- **Push to `origin main` not yet done.** Six commits are ready locally; the
  EXECUTOR's push was blocked by the local permission layer, and Kaiyuan will
  push manually. Sophia cannot clone until this lands.
- Sophia evidence (byte-identity of the pulled data file, clean working tree)
  is **PENDING** --- requires Kaiyuan to run `docs/SOPHIA_RUNBOOK.md`; the
  EXECUTOR cannot reach Sophia because it requires MFA.

## Resolved since last update

- **D-005 decided** (supersedes D-001): the raw CSV is untracked and
  transferred out of band, pinned by SHA-256. History verified never to have
  contained the blob; repository is 643 KiB packed.
- **D-002 decided**: the ClimRR data dictionary is tracked under
  `data/metadata/` as authoritative metadata, not literature. M1 may cite it as
  evidence for column semantics.

## Links

- Plan and gate criteria: [PROJECT_PLAN.md](PROJECT_PLAN.md)
- Decisions: [DECISION_LOG.md](DECISION_LOG.md)
- Data facts and column inventory: [DATA_NOTES.md](DATA_NOTES.md)
- Sophia procedure: [SOPHIA_RUNBOOK.md](SOPHIA_RUNBOOK.md)
- Active milestone report: [../reports/milestones/M0_SETUP_REPORT.md](../reports/milestones/M0_SETUP_REPORT.md)
- Operating rules: [../CLAUDE.md](../CLAUDE.md)
