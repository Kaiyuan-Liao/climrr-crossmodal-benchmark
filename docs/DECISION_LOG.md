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
- **Owner:** Kaiyuan Liao (proposed by COORDINATOR, approved by Kaiyuan
  2026-09-08).
- **Affected files:** `data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf`,
  `data/manifest.json`, `data/README.md`, `CLAUDE.md`.
- **Status:** **decided.** M1 may treat this PDF as authoritative evidence for
  column semantics.

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
- **Status:** decided, **amended by D-007** (parsing and profiling libraries are
  pinned during M1-WP1; the Python minor version stays free). The rest stands.

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
- **Size discrepancy (resolved):** the blueprint stated the CSV was **~48 MB**;
  the actual file is **296,407,423 bytes (~282.7 MiB)**. Kaiyuan's explanation:
  the blueprint figure came from a compressed chat upload of the file. Verified
  fact: row and column counts match the blueprint exactly (62,834 x 275).
  Treated as resolved on that basis; the original acquisition date remains
  unknown.
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
  **Plan correction (2026-09-08):** while assessing this decision against the
  M0 gate it emerged that `docs/PROJECT_PLAN.md` did not carry the blueprint's
  M0 gate criteria; its M0 criteria were corrected to the blueprint text on
  this date. The M1--M5 criteria could not be corrected --- the blueprint's
  text for them was never supplied to the EXECUTOR --- and are now flagged in
  the plan as EXECUTOR-drafted and not authoritative.
- **Owner:** COORDINATOR, approved by Kaiyuan Liao.
- **Affected files:** `.gitignore`, `data/raw/README.md`, `data/README.md`,
  `data/MANIFEST.md`, `data/manifest.json`, `tests/test_manifest.py`,
  `scripts/sophia_bootstrap.sh`, `docs/SOPHIA_RUNBOOK.md`, D-001.
- **Status:** **decided.**

---

## D-006 --- M0 gate accepted by GUIDANCE

- **Date:** 2026-09-08
- **Decision:** GUIDANCE reviewed the M0 gate at commit `b87564b` and accepted
  it as **PASS WITH ACTIONS**. D-005 is accepted as the **permanent** mechanism
  for handling the raw data --- untracked, transferred out of band, pinned by
  SHA-256 --- not as a temporary workaround. **Fail-closed SHA-256 verification
  remains mandatory before any use of the data.**
- **Rationale:** all five charter gate criteria were met on evidence, including
  criterion 5, which an independent cold session tested rather than the
  EXECUTOR asserting. The open question at the gate was whether moving the data
  pin from the commit SHA to the manifest hash was an acceptable mechanism or
  merely an expedient; GUIDANCE settled it as acceptable and permanent. The
  guarantee the criterion protects --- that every host provably holds the same
  bytes --- was demonstrated across two architectures.
- **Alternatives considered:** (a) accept M0 conditionally and revisit the data
  mechanism at M1 --- rejected, it would leave the project's foundational
  storage decision unsettled while work built on top of it. (b) require the
  data back into Git by some route before passing --- rejected, no route
  exists that both fits GitHub's per-file limit and reproduces on Sophia.
- **Consequences:** the fail-closed checks are now a permanent contract, not an
  implementation detail: `scripts/smoke_test.py` and `tests/test_manifest.py`
  must continue to **fail** rather than skip when the file is absent, and
  `CLIMRR_ALLOW_MISSING_RAW=1` must never be set during a gate run. Weakening
  either would void the basis on which this gate passed. Closure actions from
  the review are recorded in `docs/M0_GUIDANCE_GATE_REVIEW.md`.
- **Incidental fix during closure (not a data-handling change).** The
  secrets/paths scanner matched bare substrings, which produced two false
  positives in the charter: the phrase "Task-specific" contains the
  OpenAI-style key prefix, and the charter's own prohibition line listing API
  keys and credentials contains the first credential word as a plural. That
  left the mandatory pre-commit gate red for three consecutive commits.
  Credential patterns now match with boundaries --- a key prefix must begin a
  word and be followed by key material, and a credential word must stand alone
  rather than sit inside a longer one --- case-insensitively. Absolute-path
  patterns are unchanged. The scan passes on the full tracked tree with
  **0 hits and no exemption for `docs/BLUEPRINT.md`**, and the behaviour is
  covered by tests in `tests/test_secrets_scan.py`.

  Fixing this exposed a genuine hole. Each line was lowercased before
  comparison, while the macOS user-path pattern kept its capitalised spelling
  --- so **that pattern could never match**, and the guard's most relevant path
  check for the authoring machine had been dead since it was written. Paths
  are now matched case-sensitively, as they are spelled on disk, and a
  regression test covers it. Re-scanning the full tree after the fix found no
  tracked file that had ever carried such a path, so nothing leaked; the guard
  was simply not guarding.

  Worth recording for whoever maintains this: writing the fix into this log
  tripped the repaired scanner three times, once on the very pattern that had
  been dead. That is the guard behaving correctly, and the prose was reworded
  rather than the guard loosened.

  Per the gate review, this is a scanner change rather than an execution,
  manifest, or data-handling change, so **no Sophia re-run is required**.
- **Owner:** GUIDANCE, approved by Kaiyuan Liao.
- **Affected files:** `docs/M0_GUIDANCE_GATE_REVIEW.md`,
  `reports/milestones/M0_SETUP_REPORT.md`, `docs/PROJECT_STATE.md`,
  `scripts/smoke_test.py`, `tests/test_manifest.py`,
  `scripts/verify_no_secrets_or_paths.py`, `tests/test_secrets_scan.py`, D-005.
- **Status:** **decided.**

---

## D-007 --- Amendment to D-004: pin parsing and profiling libraries during M1-WP1

- **Date:** 2026-09-08
- **Decision:** the library versions that govern CSV parsing and profiling are
  **pinned in `requirements.txt` and recorded in run records during M1-WP1**,
  before the schema/profile artifact is frozen. **The two hosts need not share
  a Python minor version.**
- **Rationale:** D-004 deferred pinning as premature at three dependencies, and
  that held for M0, where every check was a checksum or a count and the two
  hosts agreed exactly despite running Python 3.11 and 3.13. M1 changes the
  stakes: a schema and quality profile depends on how a parser infers types,
  handles nulls and sentinels, and orders distinct values, and those behaviours
  do move between library versions. Pinning the parsing layer before the
  artifact is frozen keeps the profile reproducible. The Python minor version
  is deliberately left free --- forcing it would mean fighting the ALCF base
  module for no demonstrated benefit, and the run-record fingerprint already
  makes any divergence visible.
- **Alternatives considered:** (a) pin nothing until a discrepancy appears ---
  rejected, the discrepancy would surface as an unreproducible artifact after
  it had been built on. (b) force both hosts onto the same Python minor version
  --- rejected, costly on the shared filesystem, discards the site's tuned
  base, and addresses a risk that has not materialised. (c) pin everything
  including transitive dependencies via a lockfile --- deferred, heavier than
  the risk warrants; revisit if the pinned set proves insufficient.
- **Consequences:** M1-WP1 must pin before it freezes its artifact, not after.
  Run records must carry the pinned versions, so `pip freeze` fingerprinting
  stays load-bearing. The known Python skew recorded in the M0 report is
  formally accepted rather than merely tolerated.
- **Owner:** GUIDANCE, approved by Kaiyuan Liao. His written approval is
  recorded in `docs/M0_GUIDANCE_GATE_REVIEW.md`, which confirms that
  environment stabilisation moves into M1-WP1, must be completed before the
  schema/quality profile is frozen as authoritative, and does not require the
  two hosts to share an environment manager --- only that parsing and profiling
  behaviour and the relevant dependency versions be controlled and
  reproducible.
- **Affected files:** `requirements.txt`, `src/climrr/runrecord.py`,
  `docs/M0_GUIDANCE_GATE_REVIEW.md`, M1-WP1.
- **Status:** **decided.** Amends D-004, which otherwise stands.
