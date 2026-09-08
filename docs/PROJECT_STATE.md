# Project state

Single screen. Update it at the end of every work package.

| | |
| --- | --- |
| **Current milestone** | M0 --- reproducible project foundation |
| **Active task** | M0-WP1 (repository foundation, data placement, Sophia runbook) |
| **Latest accepted commit** | none yet --- M0 gate not passed |
| **Next review event** | M0 gate, after Sophia evidence returns |

## Completed outputs

- Repository skeleton, `CLAUDE.md`, plan / state / decision log / data notes /
  report template.
- `src/climrr/` (paths, checksums, run records), `scripts/smoke_test.py`,
  `scripts/verify_no_secrets_or_paths.py`, `tests/`.
- `data/raw/FullData.csv` copied byte-identically from source
  (62,834 rows x 275 columns) and `data/metadata/` data dictionary, both
  recorded in `data/manifest.json`.
- Sophia bootstrap / pinned-pull scripts and `docs/SOPHIA_RUNBOOK.md`.
- `reports/milestones/M0_SETUP_REPORT.md`.

## Blockers

- **D-005 --- raw CSV exceeds the GitHub 100 MiB per-file limit.** The file is
  296,407,423 bytes. D-001 (ordinary Git, no LFS) cannot be executed against
  GitHub as written. Awaiting Kaiyuan's decision. See `DECISION_LOG.md`.
- **D-002 --- pending Kaiyuan's confirmation** that the ClimRR data dictionary
  PDF is tracked under `data/metadata/` as authoritative metadata.
- Sophia evidence (byte-identity of the pulled data file, clean working tree)
  is **PENDING** --- requires Kaiyuan to run `docs/SOPHIA_RUNBOOK.md`; the
  EXECUTOR cannot reach Sophia because it requires MFA.

## Links

- Plan and gate criteria: [PROJECT_PLAN.md](PROJECT_PLAN.md)
- Decisions: [DECISION_LOG.md](DECISION_LOG.md)
- Data facts and column inventory: [DATA_NOTES.md](DATA_NOTES.md)
- Sophia procedure: [SOPHIA_RUNBOOK.md](SOPHIA_RUNBOOK.md)
- Active milestone report: [../reports/milestones/M0_SETUP_REPORT.md](../reports/milestones/M0_SETUP_REPORT.md)
- Operating rules: [../CLAUDE.md](../CLAUDE.md)
