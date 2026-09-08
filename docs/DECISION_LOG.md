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
- **Status:** **superseded by D-005.** The no-LFS half of this decision stands
  and its rationale is unchanged. The "ordinary Git, single immutable commit"
  half was not executable against GitHub: the file exceeds the 100 MiB
  per-file limit. D-005 replaces it with an out-of-band transfer pinned by the
  same SHA-256.

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

## D-005 --- Raw CSV is untracked and transferred out of band (supersedes D-001)

- **Date:** 2026-09-08
- **Decision:** `data/raw/FullData.csv` is **not tracked in Git**. It is
  transferred to Sophia manually by `scp` and pinned by its SHA-256 in
  `data/manifest.json`. `data/raw/*.csv` is gitignored; `data/raw/.gitkeep` and
  `data/raw/README.md` are tracked in its place. The data-dictionary PDF remains
  tracked (D-002).
- **Rationale:** the file is **296,407,423 bytes (~282.7 MiB)**. GitHub
  hard-rejects any single file over **100 MiB (104,857,600 bytes)** on push,
  independent of repository size, so D-001's "ordinary Git, single immutable
  commit" could never have been pushed. Git LFS was rejected for the reason
  D-001 already gave: git-lfs is unavailable on Sophia, so the execution clone
  would receive a pointer stub and could not reproduce the hash. An out-of-band
  transfer keeps the byte-identity guarantee --- it simply moves the pin from
  the commit SHA to the manifest hash --- while keeping the repository small
  and clonable.
- **Size discrepancy (logged):** the blueprint stated the CSV was **~48 MB**.
  The actual file is **296,407,423 bytes (~282.7 MiB)**, roughly 6x larger.
  The blueprint's row and column counts, by contrast, were exact: 62,834 x 275
  observed, 62,834 x 275 stated. The discrepancy is therefore in the recorded
  file size only, not in the shape of the table, and no data was filtered or
  altered to reconcile it. Whether the blueprint figure referred to a different
  export is an open question for Kaiyuan.
- **Alternatives considered:** (a) **Git LFS with a user-local git-lfs binary on
  Sophia** --- rejected, reintroduces the dependency D-001 removed and blocks
  M0 on a second host-configuration task. (b) **Split into <100 MiB parts and
  reassemble on read** --- rejected, keeps the bytes pinned to the commit but
  puts ~283 MiB in history permanently and adds a reassembly step to every
  read. (c) **Commit a subset or column-pruned extract** --- rejected outright:
  it would mean filtering columns, which M0 forbids.
- **Consequences:** the bytes no longer travel with the commit, so a pinned
  commit SHA alone no longer determines the data. **Every host must verify the
  hash before the data is used** --- this is why `scripts/smoke_test.py` and
  `tests/test_manifest.py` now *fail* rather than skip when the file is absent,
  unless `CLIMRR_ALLOW_MISSING_RAW=1` is set deliberately. Adding a host to the
  project now requires a manual transfer step, documented in the runbook.
- **Owner:** COORDINATOR, approved by Kaiyuan Liao.
- **Affected files:** `.gitignore`, `data/raw/README.md`, `data/README.md`,
  `data/MANIFEST.md`, `data/manifest.json`, `tests/test_manifest.py`,
  `scripts/sophia_bootstrap.sh`, `docs/SOPHIA_RUNBOOK.md`, D-001.
- **Status:** **decided.**
