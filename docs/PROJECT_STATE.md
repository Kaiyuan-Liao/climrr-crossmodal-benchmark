# Project state

Single screen. Update it at the end of every work package.

| | |
| --- | --- |
| **Current milestone** | M0 --- reproducible project foundation |
| **Active task** | M0-WP1 --- **complete**, awaiting gate review |
| **Latest accepted commit** | `685c2b1` --- M0-WP1 close (followed by two bookkeeping commits: this SHA pointer, and a push-status correction) |
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

- **Two commits unpushed** (`685c2b1`, `a0dc4db`). `origin/main` is at
  `586f5fd`, which is the commit Sophia cloned and verified, so the gate
  evidence is already on the remote. Kaiyuan pushes the remainder manually.
- **GUIDANCE to confirm** that D-005's out-of-band transfer is an acceptable
  mechanism for pinning the raw data. Byte identity itself is met and proven
  across two architectures; the mechanism is the open question.
- **Blueprint M1--M5 gate criteria were never supplied to the EXECUTOR.** Those
  in `PROJECT_PLAN.md` are EXECUTOR-drafted and flagged as not authoritative.
  Supply the blueprint text before M1 opens.
- **Gate criterion 5 is self-assessed**, not independently tested. Handing a
  fresh session only this repository, to see whether it reaches the right next
  action cold, is recommended before the `m0-setup` tag.
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
- **Report restructured** onto the blueprint's 15 fields, and the M0 gate
  assessed against the blueprint's five criteria (quoted verbatim). All five
  MET; proposed status **PASS**.
- **`PROJECT_PLAN.md` M0 criteria corrected** to the blueprint text;
  `REPORT_TEMPLATE.md` corrected to the blueprint's 15 field names.
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
