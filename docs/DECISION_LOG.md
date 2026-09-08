# Decision log

Append-only. Every entry carries: date, decision, rationale, alternatives,
consequences, owner, affected files, status. A decision marked **proposed** is
not yet in force and must not be relied on by downstream work.

---

## D-001 --- Raw CSV storage policy: ordinary Git, single immutable commit

- **Date:** 2026-09-08
- **Decision:** Commit `data/raw/FullData.csv` as an ordinary Git object in a
  single dedicated commit. Do **not** use Git LFS.
- **Rationale:** git-lfs is not available on Sophia (confirmed by pre-check).
  An LFS pointer file would clone as a text stub rather than the real bytes, so
  the execution clone could not reproduce the SHA-256 and the M0 byte-identity
  gate would fail. Ordinary Git guarantees the bytes travel with the commit.
- **Alternatives considered:** (a) Git LFS --- rejected, unavailable on the
  execution host. (b) Keep the CSV outside Git and sync it out of band ---
  rejected, breaks single-commit reproducibility and the pinned-SHA model.
- **Consequences:** Repository size grows permanently by the file size; the
  blob can never be rewritten without rewriting history. `.gitattributes` must
  mark `*.csv` as `-text` so no line-ending normalisation can alter the bytes.
- **Owner:** COORDINATOR, approved by Kaiyuan Liao.
- **Affected files:** `data/raw/FullData.csv`, `.gitattributes`,
  `data/manifest.json`, `data/README.md`, `tests/test_manifest.py`.
- **Status:** decided --- but see **D-005**, which blocks its execution against
  GitHub.

---

## D-002 --- Track the ClimRR data dictionary as authoritative metadata

- **Date:** 2026-09-08
- **Decision:** Track `ClimRR Metadata and Data Dictionary.pdf` in the
  repository under `data/metadata/` (filesystem-safe name
  `ClimRR_Metadata_and_Data_Dictionary.pdf`) as **authoritative metadata**, not
  as part of the literature corpus.
- **Rationale:** It is the definitive description of the columns in
  `FullData.csv` and is required evidence for M1 interpretation. The blanket
  prohibition on committing literature PDFs targets the independently collected
  scientific corpus; a data dictionary that ships with the data is provenance,
  not literature. Versioning it with the data keeps interpretation auditable.
- **Alternatives considered:** (a) Keep it outside the repo and reference it by
  path --- rejected, the reference would break and M1 evidence would not be
  reproducible. (b) Treat it as literature under the gitignored `literature/`
  --- rejected, conflates provenance with corpus and hides the evidence M1
  depends on.
- **Consequences:** ~651 KiB tracked permanently. The literature-PDF
  prohibition must be stated in `CLAUDE.md` with this explicit exception, or a
  future session will delete the file for policy reasons.
- **Owner:** Kaiyuan Liao (proposed by COORDINATOR).
- **Affected files:** `data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf`,
  `data/manifest.json`, `data/README.md`, `CLAUDE.md`.
- **Status:** **proposed** --- awaiting Kaiyuan's confirmation.

---

## D-003 --- Single-writer sync model

- **Date:** 2026-09-08
- **Decision:** The local authoring clone is the only clone that commits and
  pushes. The Sophia clone pulls **pinned commit SHAs** only and has its push
  URL disabled. Large outputs stay on Eagle; only small evidence (run records,
  short reports) is copied back and committed locally.
- **Rationale:** Two writers against one branch produces divergent history and
  makes "which commit produced this evidence?" unanswerable. Sophia's SSH key
  has write access, so policy alone is not enough --- the push URL is disabled
  mechanically so an accidental push cannot succeed.
- **Alternatives considered:** (a) Bidirectional push with branch discipline
  --- rejected, relies on human care under MFA-gated interactive sessions.
  (b) Sophia pushes evidence to its own branch --- rejected, adds merge burden
  for a few kilobytes of run records.
- **Consequences:** Every Sophia result must be transported back by hand and
  committed locally. The runbook must name exactly which files to copy.
- **Owner:** COORDINATOR, approved by Kaiyuan Liao.
- **Affected files:** `scripts/sophia_bootstrap.sh`,
  `scripts/sophia_pull_pinned.sh`, `docs/SOPHIA_RUNBOOK.md`, `CLAUDE.md`,
  `config/project.yaml`.
- **Status:** decided.

---

## D-004 --- Environment policy

- **Date:** 2026-09-08
- **Decision:** `requirements.txt` is the single source of truth for Python
  dependencies. Locally, a conda env named `climrr` (Python 3.11) with
  `pip install -r requirements.txt`. On Sophia, a `venv` created with
  `--system-site-packages` over the ALCF `conda` base module, at
  `$REPO/.venv-sophia`, with the same `pip install -r requirements.txt`.
- **Rationale:** One dependency list keeps the two environments comparable, and
  the `pip freeze` SHA-256 in each run record makes any drift visible. A venv
  over the ALCF base module inherits the site's optimised builds rather than
  fighting them, while keeping project packages isolated and writable.
- **Alternatives considered:** (a) conda env on Sophia too --- rejected, slower
  to build on a shared filesystem and discards the site's tuned base.
  (b) A pinned lockfile --- deferred; premature at three dependencies, and the
  `pip freeze` fingerprint already detects drift.
- **Consequences:** Dependencies are unpinned, so environments can drift over
  time; the run-record fingerprint is the detector. Pin later if drift bites.
- **Owner:** COORDINATOR, approved by Kaiyuan Liao.
- **Affected files:** `requirements.txt`, `pyproject.toml`,
  `scripts/sophia_bootstrap.sh`, `src/climrr/runrecord.py`,
  `config/project.yaml`.
- **Status:** decided.

---

## D-005 --- Raw CSV exceeds the GitHub per-file size limit (escalated)

- **Date:** 2026-09-08
- **Decision:** **None yet --- escalated to Kaiyuan Liao.**
- **Situation:** `data/raw/FullData.csv` is **296,407,423 bytes (~282.7 MiB)**.
  GitHub hard-rejects any single file over **100 MiB (104,857,600 bytes)** on
  push, independent of repository size. D-001 as written therefore cannot be
  executed against this remote: the CSV commit will be rejected. This is the
  escalation condition named in the work package ("the push of the CSV commit
  to GitHub fails or is rejected"), detected before the push rather than after.
- **Rationale for escalating rather than choosing:** every available option
  changes either the storage policy (D-001), the byte-identity gate, or the
  single-source-of-truth model. Each is a scope or scientific-reproducibility
  decision the EXECUTOR is not authorised to make.
- **Alternatives to be decided between:**
  - (a) **Git LFS on GitHub anyway.** Restores the push, but git-lfs is absent
    on Sophia, so the execution clone would receive a pointer stub and could
    not reproduce the SHA-256 --- this is exactly what D-001 rejected. Would
    require installing git-lfs on Sophia (user-local binary is feasible) or
    accepting a manual byte transfer.
  - (b) **Keep the CSV out of Git; transport it out of band** (Globus / `scp`
    to Eagle) and gate on the manifest SHA-256 at both ends. Preserves byte
    identity and keeps the repo small; costs the "bytes travel with the commit"
    property, so the data is no longer pinned by the commit SHA alone.
  - (c) **Split the CSV into <100 MiB parts, commit the parts, reassemble on
    read**, with the manifest hashing both the parts and the reassembled whole.
    Keeps everything in ordinary Git and reproducible on Sophia; costs a
    reassembly step and stores ~283 MiB in history permanently.
  - (d) **Commit a documented subset or column-pruned extract.** Rejected by
    the EXECUTOR as out of scope --- it would mean filtering columns, which
    M0 explicitly forbids. Listed only for completeness.
- **Consequences:** M0 cannot close until this is decided. The file is staged
  locally and hash-verified; everything except the CSV commit has been pushed.
- **Owner:** Kaiyuan Liao, with COORDINATOR.
- **Affected files:** `data/raw/FullData.csv`, `.gitattributes`,
  `data/manifest.json`, `data/README.md`, `tests/test_manifest.py`,
  `docs/SOPHIA_RUNBOOK.md`, D-001.
- **Status:** **escalated --- blocking the M0 gate.**
