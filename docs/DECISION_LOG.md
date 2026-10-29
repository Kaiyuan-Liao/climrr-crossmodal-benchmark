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
  `pyproject.toml`, `docs/M0_GUIDANCE_GATE_REVIEW.md`, M1-WP1.

  **Pin set applied 2026-09-08 (M1-WP1 Phase A).** Not a new decision --- this
  is the execution of the one above, recorded here so the frozen profile can be
  traced to an exact stack:

  | Distribution | Pinned version | Why it is in the pin set |
  | --- | --- | --- |
  | `pandas` | `3.0.5` | cross-check reader (Phase C) |
  | `numpy` | `2.4.6` | pandas' array layer; pinned so pandas' behaviour is determined |
  | `pypdf` | `6.18.0` | data-dictionary text extraction (Phase D) |
  | `pyyaml` | `6.0.3` | config loading in `climrr.paths` |
  | `pytest` | `9.1.1` | the check that gates every commit |

  `pypdf` was chosen over `pdfplumber` because it is pure Python with no
  compiled or system dependencies (`pdfplumber` pulls in `pdfminer.six` and
  Pillow), so the same wheel installs on both hosts. Every pinned version
  publishes cp311 and cp313 wheels for macOS arm64 and manylinux_2_28 x86_64;
  Sophia is glibc 2.34, above that floor. Run records now carry a
  `pinned_libraries` field --- name, pinned version, imported `__version__`,
  and a `matches_pin` flag --- and `tests/test_runrecord.py` fails when the
  running environment drifts from this file.
- **Status:** **decided.** Amends D-004, which otherwise stands.

---

## D-008 --- Data provenance of `FullData.csv`, as stated by Kaiyuan

- **Date:** 2026-09-08
- **Decision:** the provenance of `data/raw/FullData.csv` is recorded as
  Kaiyuan's statement below. It is **stated by Kaiyuan, not independently
  verified**, and every use of it downstream must carry that qualification.

  Statement, verbatim as given:

  > For how I get the .csv file, it is shared by my mentor from ALCF through
  > Box, I downloaded it directly as one file. I downloaded it one week ago but
  > it is definitely not the time it was created. I did not do any extra
  > operation over the .csv file, what you see is what it is to me at the first
  > time

- **What this settles.** Three things, all about *handling* rather than about
  content:
  1. **The chain of custody is short and unbroken on this side.** One file, one
     download, no intermediate tooling on Kaiyuan's part. The bytes pinned in
     `data/manifest.json` are the bytes as delivered.
  2. **No transformation was applied downstream of ALCF.** Whatever produced the
     275-column layout --- the join of the eleven dictionary layers, the stem
     prefixes, the truncated names, the duplicated identifier columns --- was
     done **before** the file reached this project. It is therefore a question
     for the mentor and the ClimRR authors, not something recoverable from
     Kaiyuan's steps. This is the standing answer to the *"did you do this?"*
     half of `METADATA_QUESTIONS.md` Q1, Q10 and Q11; the *"who did, and how?"*
     half remains open.
  3. **The download date is not the creation date**, stated explicitly. The
     acquisition date is now approximately known; the export date is not.
- **EXECUTOR annotation, derived and not stated:** "one week ago" relative to
  2026-09-08 puts the download at approximately **2026-09-01**. That is an
  arithmetic reading of a relative phrase, not a date Kaiyuan gave; the exact
  day is still unknown, and `data/manifest.json` therefore keeps
  `acquisition_date: "unknown"` rather than recording a computed guess. If an
  exact date is wanted, Box records it.
- **What this does not settle, and why no column status changed.** The statement
  names no dictionary section for any CSV column-name stem, so it cannot promote
  any column to `verified_from_dictionary`. Metadata status counts are unchanged
  at 21 / 143 / 28 / 83. Establishing that nobody here modified the file is
  evidence about custody; it says nothing about what a column means. Q1's
  substance --- whether the CSV is the eleven dictionary layers joined side by
  side --- is now unambiguously a question for the mentor and the ClimRR authors.
- **Alternatives considered:** (a) treat the statement as verification of
  provenance --- rejected, an unverified recollection is evidence of a kind but
  not verification, and labelling it as such would let a downstream reader
  inherit more confidence than exists. (b) Write the derived date into the
  manifest --- rejected, D-005 and the M0 gate both record the acquisition date
  as unknown deliberately, and a computed approximation is exactly the kind of
  quiet filling-in the charter forbids.
- **Consequences:** Q18 is answered as far as Kaiyuan can answer it and now asks
  the mentor for the export date instead. Q1, Q10 and Q11 keep their substance
  but are re-aimed at the mentor. Any future claim about how this table was
  assembled must cite the mentor or the ClimRR authors, never this entry.
- **Owner:** Kaiyuan Liao (statement); recorded by the EXECUTOR.
- **Affected files:** `docs/DECISION_LOG.md`, `docs/METADATA_QUESTIONS.md`,
  `data/manifest.json` (unchanged, deliberately),
  `reports/milestones/M1_DATA_GROUNDING_REPORT.md`.
- **Status:** **recorded.** Not a decision that constrains implementation ---
  a provenance fact of stated, unverified standing.

---

## D-009 --- GUIDANCE accepts M1-WP1 and authorises M1-WP2

- **Date:** 2026-09-09
- **Decision:** GUIDANCE records **PASS** on work package M1-WP1 at reviewed
  head `fceee7f06883c18b45fccda7da350fd4c6966ee8`, merged to `main` as
  `62c9137`. This is a **work-package pass, not the M1 milestone gate**; M1
  stays open. The review is tracked at
  [`M1_WP1_GUIDANCE_REVIEW.md`](M1_WP1_GUIDANCE_REVIEW.md).

  Four rulings are in force from this date, each answering a question the WP1
  report raised in its field 13:

  1. **The strict `verified_from_dictionary` bar is confirmed and must not be
     loosened.** A column may not reach that status because a stem/suffix
     pattern looks convincing. Only three kinds of evidence can promote a
     stem-to-section mapping: explicit confirmation from the mentor, the data
     owner or the ClimRR authors; an authoritative export/source-generation
     specification; or another authoritative ClimRR artifact that maps full CSV
     names to dictionary sections. GUIDANCE states its preference plainly:
     retain 21 conservative verified columns rather than inflate the set on an
     unconfirmed inference about how the export was built.
  2. **The two EXECUTOR-authored candidate maps are approved as navigation
     only** --- `STEM_SECTION_CANDIDATES` and `NARRATIVE_CANDIDATES` in
     `src/climrr/dictionary.py`. Their permitted role is to make questions
     specific and to guide inspection. They may not serve as evidence, may not
     promote a column, and may not propagate silently into later phenomenon
     extraction or bridge scoring.
  3. **Index 117 `Aggregate_Resilience_Indicator_` stays in the grounded
     inventory and its `-9` stays unlabelled.** The authorised structural
     conclusion is only that the field has zero variation and so cannot carry
     discriminative information in this file. Calling `-9` missing, no-data,
     invalid or suppressed is not authorised without source confirmation, and
     the column is not to be used in later pilot work until its meaning is
     clarified.
  4. **D-008 stays a user-provided provenance statement** and is not upgraded
     into independently verified source provenance.

  **M1-WP2 --- metadata resolution and citable column dictionary --- is
  authorised**, with the nine acceptance criteria quoted in
  `reports/milestones/M1_WP2_REPORT.md` field 14. M2 semantic-schema design and
  M3 phenomenon extraction remain prohibited, along with aggregation, thresholds,
  literature ingestion, retrieval, embeddings, bridges and QA.
- **Rationale:** the review judges the WP1 status distribution --- 21 / 143 / 28
  / 83 --- an honest measurement of the available evidence rather than a
  weakness of the method, and identifies the primary scientific risk as **false
  metadata closure**: promoting plausible structural correspondence into
  authoritative semantics. Every ruling above exists to keep that promotion
  gated behind a named external source.
- **Alternatives considered:** (a) loosen the verified bar so the nine stem
  families inherit their candidate sections --- rejected by GUIDANCE, this is
  exactly the false-closure risk. (b) Drop index 117 as a constant --- rejected,
  removing it would encode an unproven reading of `-9`.
- **Consequences:**
  - A **new status, `owner_confirmed`**, is introduced in WP2 for semantics
    confirmed by the mentor or the data owner. It is kept **distinct from**
    `verified_from_dictionary`, which remains reserved for what the tracked
    dictionary states in its own words. No resolution record can ever produce
    `verified_from_dictionary`; the machinery refuses it.
  - Every WP2 status change must cite a resolution record in
    `data/metadata/resolutions.yaml` and a decision number, and must be visible
    in `scripts/status_diff.py` output against the WP1 baseline.
  - `reports/milestones/M1_DATA_GROUNDING_REPORT.md` is **frozen as the WP1-stage
    record**; current M1 status moves to
    `reports/milestones/M1_WP2_REPORT.md`.
  - The review's risk 4 --- PDF extraction completeness --- is discharged in
    WP2 Phase B. **Finding: page 3 of the 19-page dictionary PDF is blank.**
    Rendered at 200 dpi from the manifest-verified PDF, its pixels are a single
    uniform value across all three channels, and read as an image it is a white
    page: no field table, no field names, no figure, no scanned content, nothing
    bearing on the 275 columns. Its extracted text is two space characters, which
    is the whole of its content. Pages 2 and 4 render fully at the same settings
    and are the control that the renderer is not at fault. No status changes from
    it, and no manual transcription file was needed.
  - The mentor-facing question inventory is restated for a non-specialist reader
    in `docs/MENTOR_BRIEF.md`, in the priority GUIDANCE set: Q1, Q7, Q8, the
    geographic/join-key questions Q10--Q12, the sentinel questions Q17 and Q9,
    export provenance Q18, then Q2--Q6 and Q13--Q16.
- **Owner:** GUIDANCE, approved by Kaiyuan Liao.
- **Affected files:** `docs/M1_WP1_GUIDANCE_REVIEW.md`,
  `docs/DECISION_LOG.md`, `docs/PROJECT_STATE.md`, `docs/DATA_NOTES.md`,
  `docs/MENTOR_BRIEF.md`, `data/metadata/resolutions.yaml`,
  `src/climrr/dictionary.py`, `scripts/dictionary_coverage.py`,
  `scripts/status_diff.py`, `scripts/rasterize_dictionary_pages.py`,
  `reports/milestones/M1_DATA_GROUNDING_REPORT.md`,
  `reports/milestones/M1_WP2_REPORT.md`.
- **Status:** **decided.**

---

## D-010 --- Pilot-subset path with mentor sign-off

- **Date:** 2026-09-12
- **Status:** **decided.** GUIDANCE ruled **PASS WITH ACTIONS** on 2026-09-13
  (`docs/M1_D010_GUIDANCE_RULING.md`) and **Kaiyuan approved it with the ruling
  incorporated**. The ruling's boundaries, which are part of the decision and
  not commentary on it, are recorded separately as **D-011**; read the two
  together, and where they differ the ruling governs. Implemented in M1-WP3.
- **Decision proposed:**
  1. Introduce a status **`inferred_candidate`** for semantics produced by
     reasoning from column names, value patterns and dictionary spans, always
     with **the reasoning and the spans recorded on the column**. It is a fifth
     status, below `owner_confirmed` and `verified_from_dictionary` and
     distinct from both, and it never silently becomes either.
  2. Interpret **only a pilot subset** of columns that way --- not all 275.
  3. Build **2--3 example event records from real rows** for mentor review, with
     **every assumption listed on the record** it depends on.
  4. **Mentor sign-off on an example promotes the columns that example uses to
     `owner_confirmed`**, through an ordinary resolution record naming those
     columns.
  5. **All other columns remain `unresolved`, explicitly and permanently**,
     unless new evidence appears.
- **Rationale.** Two answers from the 2026-09-10 meeting, recorded as R-001 and
  R-002 in `data/metadata/resolutions.yaml`:
  - **R-001: there is no further metadata.** No newer data dictionary, no
    assembly document or script, no release note. Two of the three evidence
    types D-009 accepts for promoting a stem-to-section mapping --- an
    authoritative export specification, and another authoritative ClimRR
    artifact mapping CSV names to dictionary sections --- are therefore
    **unavailable, not merely unobtained**.
  - **R-002: use a reliable subset, reason out the rest, and show examples.**
    A direction for the project, not a semantic for any column.

  D-009's strict bar was set on the premise that authoritative answers would
  arrive and could be waited for. R-001 removes that premise for two of the
  three routes, and the meeting produced **no per-column answer for any of
  Q1--Q18** on the third. Held unchanged, the project's reachable end state is
  21 dictionary-verified columns and no pilot --- which is not what the data
  owner asked for. This entry proposes the narrowest change that respects both:
  inference is permitted, is **named as inference**, is **confined to a subset**,
  and is **promoted only by a human who can actually confirm it**.
- **Alternatives considered:**
  - **(a) Stop M1 with 21 verified columns and no pilot.** Rejected: it
    contradicts the mentor's direction, and it treats the absence of
    documentation as a reason to abandon the dataset rather than to be explicit
    about what is known.
  - **(b) Promote the EXECUTOR candidate maps to `verified_from_dictionary`.**
    **Prohibited by D-009** and not reopened here. The candidate maps stay
    navigation aids. Note what this proposal does *not* do: `inferred_candidate`
    is a new, weaker status, not a relabelling of the candidate maps as
    evidence.
- **Consequences if adopted:**
  - **M1 gate criterion 1 would be evaluated on the pilot subset**, not on all
    275 columns, and the gate would have to say so explicitly.
  - **GUIDANCE must authorise hand-worked example construction ahead of M2.**
    Building event records from real rows is an M2 deliverable; doing it during
    M1 is a deliberate reordering and needs a ruling, not an assumption.
  - A fifth status, its reasoning field, and its promotion path would need to be
    built into `climrr.dictionary` and the resolution schema.
- **Consequence already in force, independent of this entry:** Q0 is closed,
  answered in the negative (R-001). No authoritative artifact is coming.
- **An assumption inside R-002 that is not yet established:** "each row stands
  for one event" is **Kaiyuan's reading** of the mentor's direction, not a
  statement she made in those terms. It is the grain of the whole proposed
  pilot, and it is to be **confirmed with her by presenting examples** --- it is
  not assumed in the meantime, and no work here depends on it.
- **Owner:** COORDINATOR (drafted). **Approved by Kaiyuan Liao 2026-09-13, with
  the GUIDANCE ruling incorporated; GUIDANCE ruled PASS WITH ACTIONS.**
- **Affected files:** `src/climrr/dictionary.py`,
  `data/metadata/inferred_candidates.yaml`, `scripts/dictionary_coverage.py`,
  `scripts/status_diff.py`, `docs/PILOT_SUBSET.md`,
  `reports/milestones/M1_WP3_REPORT.md`. Note what is **not** in that list:
  `data/metadata/resolutions.yaml` is untouched by this decision, because the
  status it introduces may not be reached through a resolution record.

---

## D-011 --- The GUIDANCE ruling on D-010, and the boundaries it sets

- **Date:** 2026-09-13
- **Status:** **decided.** This entry records the ruling itself
  (`docs/M1_D010_GUIDANCE_RULING.md`, gate status **PASS WITH ACTIONS**), placed
  by Kaiyuan and approved by him as project owner. D-010 says what the project
  will do; **D-011 says what it may not do while doing it**, and the limits are
  the substance of the approval rather than caveats attached to it.
- **Decision:**
  1. **`inferred_candidate` is approved, with boundaries.** It means "a reasoned
     interpretation judged plausible enough to test in an example, but not
     established as source truth". Every record carries the column index and
     name, the proposed meaning, any proposed unit/scenario/horizon/season,
     dictionary spans, name evidence, value evidence, explicit reasoning,
     unresolved alternatives, and a statement that it is neither verified nor
     owner-confirmed. **It may not be presented as verified.** A record is
     required per column: membership in an EXECUTOR-authored candidate map is
     not a reason, and the candidate maps remain navigation aids.
  2. **`verified_from_dictionary` is unchanged.** D-009's strict bar is not
     reopened, narrowed or widened by any part of this entry.
  3. **Mentor sign-off promotes only what was explicitly confirmed.** Sign-off
     on an example is a valid route to `owner_confirmed`, but a broad "yes, this
     is the kind of example I want" confirms **nothing** about the field
     semantics embedded in it. A resolution record must distinguish confirmed
     from unconfirmed semantics field by field.
  4. **M1 gate criterion 1 is evaluated on the pilot subset**, not on all 275
     columns. M1 may pass with a small subset whose fields meet the metadata
     requirements while every other column stays explicitly unresolved,
     undocumented and unused. **The scope narrows; the rigour does not.**
  5. **M1-WP3 is authorised**: 2--3 row-centered candidate examples built from
     real rows, ahead of M2 and deliberately out of milestone order, because
     examples are now the instrument required to resolve M1 metadata with the
     data owner. They are **not** canonical M2 phenomenon records.
  6. **"Row = event" remains an assumption under review.** It is Kaiyuan's
     reading of the mentor's direction, not her words, and it is to be confirmed
     by showing her examples. Until then no wording may present a row as an
     observed climate event.
- **Rationale.** The ruling's own: fact, inference and owner confirmation must
  remain explicitly separated, and the five named scientific risks --- AI
  reasoning becoming de facto ground truth, confirmation by impression rather
  than by semantics, a conceptually wrong row grain, cherry-picking
  easy-to-narrate fields, and example construction drifting into M3 --- are each
  answered by one of the boundaries above rather than by intent.
- **Consequences, all of them in force now:**
  - A fifth status exists in `src/climrr/dictionary.py`, settable **only** by a
    record in the new tracked `data/metadata/inferred_candidates.yaml` --- never
    by the dictionary rules, never by the candidate maps, and never by a
    resolution record, which the validator refuses by name.
  - `scripts/status_diff.py` shows every column that gains it, citing the
    IC-record, and fails the run if a column holds the status without one or
    falls into it from a stronger one.
  - Examples are built under `artifacts/examples/`, and their mentor-readable
    prose is **generated from the structured record by template**, so that no
    clause resting on an inferred field can appear without a `[provisional: …]`
    label.
- **What this entry does not authorise**, restated from the ruling because the
  temptation runs the other way: no broad AI labelling of the table, no
  inference for all 275 columns, no promotion on model confidence or naming
  plausibility, no phenomenon extraction, geographic aggregation, salience or
  magnitude criteria, literature ingestion, claim extraction, semantic matching,
  bridge validation or QA generation.
- **Owner:** GUIDANCE. **Approved by Kaiyuan Liao, 2026-09-13.**
- **Affected files:** `docs/M1_D010_GUIDANCE_RULING.md` (the ruling as placed),
  `src/climrr/dictionary.py`, `data/metadata/inferred_candidates.yaml`,
  `scripts/dictionary_coverage.py`, `scripts/status_diff.py`,
  `src/climrr/examples.py`, `scripts/build_examples.py`,
  `docs/PILOT_SUBSET.md`, `docs/MENTOR_EXAMPLES.md`.

---

## D-012 --- The M1-WP3 pre-meeting GUIDANCE review, and the framing it required

- **Date:** 2026-09-13
- **Status:** **decided.** Records the pre-meeting review
  (`docs/M1_WP3_PREMEETING_GUIDANCE_REVIEW.md`, gate status **REVISE**), placed
  by Kaiyuan and taken at reviewed head `c8f4711` on `work/m1-wp3`. The review is
  deliberately bounded: **the scientific design is accepted and the required
  change is to mentor-facing framing and report bookkeeping only.**
- **What GUIDANCE decided, and it is now settled:**
  1. **The 41-column subset is approved.** "Small" is not a percentage
     threshold; what matters is that every added field has a bounded role and
     that the subset does not sprawl across the table. 21 verified, 20 adjacent
     fields with a specific job, 234 untouched, the undocumented families still
     excluded.
  2. **The three-column stem probe stays.** It is the smallest set that tests a
     historical, a projected and a change value under one stem-to-section
     assumption, and one mentor decision on that link clarifies the assumption
     under 101 columns. Removing it "would make the subset numerically smaller
     but scientifically less useful". **Do not shrink the subset to improve the
     percentage.**
  3. **All three standing cautions are approved** --- Fire Weather Index,
     modeled historical baseline, and rendering an empty cell as "no value in
     this file". They are **repository-level rendering rules, not hidden
     semantic interpretations**, and inserting them conditionally does not
     violate the raw / semantics / presentation separation. This answers the
     question M1-WP3's report put to GUIDANCE under criterion 6.
  4. **Criterion 6 is satisfied by the architecture**, and was not satisfied by
     the mentor-facing document as delivered --- see the required action below.
  5. **The stale metadata-hash disclosure is accepted with no scientific rerun.**
     Counts, selected columns and the three examples were unaffected, the
     artifact was regenerated, a regression test now rejects a tracked-metadata
     hash mismatch, and the old artifact was verified to fail it. GUIDANCE calls
     that "the correct remediation".
  6. **The example rows and the IC records are unchanged.**
- **The one required action, and why it was required.** Some **inferred location
  semantics were presented as established fact outside the explicit confirmation
  surface.** `docs/MENTOR_EXAMPLES.md` carried headings reading
  `Stephens County, Oklahoma` and framing reading `Where it is:` while `NAME`,
  `State` and `State_Abbr` are `inferred_candidate` fields whose readings were
  being submitted for confirmation on that very page. The generated field-level
  prose was correct throughout --- every inferred clause wrapped
  `[provisional: ...]`, enforced by the build --- so the defect was precisely
  that **the hand-authored surface bypassed machinery the generated surface
  obeyed**. Asking "is `NAME` a county name?" further down the page does not
  undo the anchoring, and the anchoring matters here because these columns appear
  nowhere in the dictionary, the Census vintage is unknown, and the coordinate
  reference system is unknown.
- **What was changed, in full:**
  - example titles are neutral --- `row OID_ 1, Crossmodel R106C361`;
  - `Where it is:` became `Location-related raw fields: NAME = Stephens, State =
    Oklahoma, ...`, quoting stored strings under a label that claims nothing and
    saying that the four columns' meaning is checklist lines 10--15, unsettled;
  - the location checklist item was **split three ways** --- a structural
    observation (49 distinct non-empty values, 7 blank rows) with nothing to
    confirm, the proposed interpretation, and a question conditional on that
    interpretation --- so that one tick cannot confirm a character count and a
    semantic claim together. This answers the review's "compound confirmation"
    risk. Line numbering moved from 14 lines to 16, and every cross-reference
    with it;
  - a **bounded guard** was added,
    `test_no_unwrapped_location_semantic_in_the_hand_authored_framing`, checking
    the hand-authored surface for a fixed list of geographic words outside
    `[provisional: ...]` wrappers and outside backticked file content, with an
    allow-list for the checklist rows that pose them as questions. A second test
    feeds the rejected heading back through it. As the review allows, this is a
    bounded word check and not natural-language analysis;
  - the WP3 report's branch, head and push state now match the reviewed packet.
- **What was deliberately not changed:** the 41-column subset, the three
  structural selection rules, the three selected rows, the 20 IC records, the
  generated field-level presentation, the three standing cautions, and the
  mentor-confirmation protocol. **No artifact under `artifacts/` was
  regenerated**, and the coverage report and three example records remain
  byte-identical to the reviewed state.
- **Consequence.** The three examples go to the mentor meeting of
  **2026-09-17**. GUIDANCE states no remaining scientific objection once the
  framing is corrected.
- **A standing rule this decision establishes**, beyond the immediate fix: **a
  provisional-labelling discipline enforced only where output is generated is not
  enforced.** Hand-authored framing around generated content is part of the
  mentor-facing surface and is held to the same standard, by a test where a test
  is practical.
- **Owner:** GUIDANCE. **Placed and approved by Kaiyuan Liao, 2026-09-13.**
- **Affected files:** `docs/M1_WP3_PREMEETING_GUIDANCE_REVIEW.md` (the review as
  placed), `docs/MENTOR_EXAMPLES.md`, `reports/milestones/M1_WP3_REPORT.md`,
  `tests/test_examples.py`, `docs/PROJECT_STATE.md`.

---

## D-013 --- The M1-WP3b GUIDANCE ruling: a milestone-order exception, and what it required

- **Date:** 2026-09-13
- **Status:** **decided.** Records the M1-WP3b ruling, gate status **PASS WITH
  ACTIONS**, placed by Kaiyuan and relayed to the EXECUTOR by the COORDINATOR.
- **How this entry was written, and what has since been checked against it.**
  The ruling document `docs/M1_WP3B_GUIDANCE_RULING.md` was **not yet in the
  repository** when this entry was written, so the entry records the decisions
  **as relayed by the COORDINATOR** and reconstructs no criterion text, action
  text or numbering beyond what was relayed. Kaiyuan placed the document on
  **2026-09-13**. It has since been read against this entry. **The substance
  agrees; six discrepancies of attribution and coverage were found, none of them
  a decision recorded here that the ruling does not make.** They are listed in
  `reports/milestones/M1_WP3b_PROTOTYPE_REPORT.md` field 13, **and this entry was
  deliberately not edited to match the ruling** --- an append-only log records
  what was decided when, and a silent correction would destroy the evidence that
  the package was built from a relay.

### 1. The milestone-order exception

**M1-WP3b is admitted as an explicit exception to the milestone order:** early
**M3-style validation** --- phenomenon units, geographic aggregation, a magnitude
field --- carried out **while M1 is still open**. The D-010/D-011 boundaries that
forbid those three inside an M1-WP3 example are not repealed; the exception is
granted to this package, for the purpose of validating the scientific object
before the project builds on it.

**What follows, and is enforced in code and in every generated page:**

- every prototype record carries `"validation_only": true`;
- every record's `description` **opens** with the banner **"Prototype for
  scientific-object validation. Not an accepted phenomenon record."**, and so
  does every page of `docs/PHENOMENON_PROTOTYPES.md` and of
  `docs/GROUP_MEETING_2026-09-14.md`;
- the schema stays versioned `p0-prototype`, so adopting it remains a visible
  act;
- the package stays unmerged and unpushed;
- `reports/milestones/M1_WP3b_PROTOTYPE_REPORT.md` proposes no gate status.

### 2. Criterion 7 --- a percent change may not be averaged

**The ruling found a real defect and it is fixed.** `P-COUNTY-1` reported an
**unweighted mean of `wildfire_summer_Pend`**, a column the dictionary itself
labels "Percent Change". The mean of per-cell percent changes weights a cell
with a near-zero baseline as heavily as one with a large baseline, and it is not
the percent change of the aggregate. The number was reported in `V` and repeated
in the generated description.

**What changed:**

- the mean of `Pend` is gone from `V` and from every generated sentence;
- **every per-cell `Pend` value is kept** in the record, complete;
- the corroboration line is now a **count**: "`wildfire_summer_Pend` is positive
  on 10 of 10 member cells";
- the rule is **general, not a patch on one column.**
  `climrr.phenomenon.aggregate_column` **refuses** any column whose recorded
  dictionary type contains `Percent Change` or `Text ID`, and any column in the
  location family --- `X` and `Y` parse as decimals and their mean would be a
  centroid this project has not defined and could not justify without the
  coordinate reference system it does not know. A refused column reports counts
  of sign, never a mean, and `V.columns_not_averaged` names it and says why;
- tests pin the refusal for a percent-change column, an identifier column and
  every location column, **and** pin that an ordinary quantity column is *not*
  refused --- a guard that refuses everything would be worse than none.

**The standing rule this establishes:** *a column's dictionary type decides what
arithmetic it admits.* Whether the characters parse as a number is not the
question.

### 3. The schema letters --- two conventions, neither settled

The ruling defines **S = scenario, T = temporal horizon, C = compared quantity**,
and asks for a **P = provenance** field. The mentor and Kaiyuan use **S = season,
T = horizon, C = scenario**.

**Decision: the code emits the mentor's letters**, because they are the ones she
has already seen in `docs/MENTOR_EXAMPLES.md` and in the prototypes, and
changing them now would mean changing what she is being asked about. **`P` is
added as an explicit field** --- the per-field status map already existed and is
now named `P` rather than `provenance_statuses`. **Both conventions travel
together** in every record's `P.letter_reading_note`, in the module docstring,
in `docs/PHENOMENON_PROTOTYPES.md`, and here, **for the next GUIDANCE packet to
settle.**

The two agree on `P` and on everything a record carries. They differ on which
letter names the scenario and on whether a letter names the season or the
compared quantity. **No number depends on the choice**, and no code reads a
letter as a key to a meaning.

### 4. Action 10 / criterion 10 --- say what is ranked, and against what

Every `M` field now states:

- **what is ranked**: the **signed** change value. The sign is kept, so a
  decrease ranks below a no-change and a no-change below an increase. PR-1 does
  **not** rank on absolute magnitude. This matters because a unit in the lower
  third may be one with a **large decrease** rather than one where little
  changed, and a reader assuming the other convention would read it backwards;
- **the exact reference population**, assembled from the counts rather than
  asserted --- which key forms a unit, how many keys there are, the inclusion
  test and how many it includes and excludes, how a unit's change value is
  computed, and that units whose label is the empty string are counted.

The same two facts appear inside the generated magnitude clause, so they travel
with the sentence rather than only with the JSON.

`docs/GROUP_MEETING_2026-09-14.md` now names the **`GEOID` column** and the
**`(State, NAME)` label** where it previously wrote "the tract-like id column"
and "county label", and carries the sentence the ruling asked for: **"The `GEOID`
column does not determine the `(State, NAME)` label: 3,234 `GEOID` values appear
under more than one label. What that means is an open question for the data
owner."**

### 5. What did not change

No number in any record changed as a result of this ruling except by the removal
of the `Pend` mean. The three units, the pilot subset, the assumptions register,
the provenance discipline, PR-1's arithmetic, and the standing cautions are all
as M1-WP3b delivered them.

- **Alternatives considered on the letters:** (a) adopt the ruling's letters ---
  rejected, it changes what the mentor has already seen two days before she sees
  it again, for no gain in meaning. (b) emit both sets of letters in every field
  --- rejected, it doubles the surface a reader must hold without deciding
  anything.
- **Alternatives considered on the refused columns:** (a) patch `P-COUNTY-1`
  only --- rejected, the same defect would reappear on any percent-change column
  in any future variable. (b) report min, max and median of a percent change in
  place of the mean --- rejected as re-opening the same argument; a count of
  signs makes no arithmetic claim about the quantity.
- **Consequences:** `V.per_column[...].aggregates` is `None` for a refused column
  rather than absent, so a refusal cannot be mistaken for an oversight. Any
  future variable that reaches for a mean of a percent-change or identifier
  column will fail the build rather than produce a number.
- **Owner:** GUIDANCE. **Placed and approved by Kaiyuan Liao, 2026-09-13**,
  relayed by the COORDINATOR.
- **Affected files:** `src/climrr/phenomenon.py`,
  `scripts/build_phenomenon_prototypes.py`,
  `artifacts/phenomena/prototypes/P-CELL-1.json`,
  `artifacts/phenomena/prototypes/P-COUNTY-1.json`,
  `artifacts/phenomena/prototypes/P-STATE-1.json`,
  `docs/PHENOMENON_PROTOTYPES.md`, `docs/GROUP_MEETING_2026-09-14.md`,
  `reports/milestones/M1_WP3b_PROTOTYPE_REPORT.md`, `docs/PROJECT_STATE.md`,
  `tests/test_phenomenon.py`, `tests/test_group_handout.py`.
  **Not present and outstanding: `docs/M1_WP3B_GUIDANCE_RULING.md`.**

---

## D-013-A1 --- Amendment to D-013, after reading the ruling as placed

- **Date:** 2026-09-13
- **Status:** **decided.** An **amendment**, appended. **D-013 is not rewritten**
  --- the log is append-only, and the entry as written is the evidence that the
  package was built from the COORDINATOR's relay before
  `docs/M1_WP3B_GUIDANCE_RULING.md` was placed. This entry corrects the
  citations, records the ruling's full requirement set, and says which items
  were met when, and which were closed afterwards.

### 1. Citations D-013 gets wrong, corrected

D-013 §4 is headed "Action 10 / criterion 10". One half is right and one is not.

| D-013 says | The ruling says |
| --- | --- |
| "action 10 / criterion 10" for the magnitude requirements | **Acceptance criterion 10** is right: "`M` records reference population, ranking rule, provisional status, and non-use in selection." |
| — | **Required action 10 is not about magnitude.** It reads "Keep the literature probe as a query-field stub only." |
| — | The magnitude reference population is **required action 6**: "Define the magnitude reference population exactly." |
| — | Signed-versus-absolute ranking comes from **evidence check 5**, which is prose and not a numbered action at all. |

**Nothing built on those citations is wrong** --- the work satisfies criterion
10, action 6 and evidence check 5. Only the pointer was wrong.

### 2. Who found the averaged percent change

D-013 §2 says "the ruling found a real defect". **The ruling names no defect.**
It states the general rule twice --- evidence check 3, "Do not average
identifiers, categorical labels, percentages, or quantities for which a mean is
not scientifically interpretable", and acceptance criterion 7, "Means are used
only for meaningfully averageable quantities" --- and never mentions
`P-COUNTY-1`, `wildfire_summer_Pend`, or any specific column.

**The averaged `Pend` was identified by the COORDINATOR, reading the package
against the ruling's general rule.** The fix is unchanged and is correct either
way; the attribution is not.

### 3. The ruling's eleven required actions, and where each stands

D-013 records four, because four is what the relay carried as needing action.
There are eleven.

| # | Required action | Status |
| ---: | --- | --- |
| 1 | Record WP3b as an explicit milestone-order exception | **met** by D-013 §1 |
| 2 | Label every prototype `validation_only` or equivalent | **met** --- `validation_only` plus the banner on every record and page |
| 3 | Preserve raw grouping keys separately from provisional geographic labels | **met as built** --- `G.identifier` holds the stored strings, `G.member_cells` the raw `Crossmodel` keys, and the interpretation of either is `inferred_candidate` carried in `P` |
| 4 | Store source columns, operations, counts, and exact member-row provenance for every aggregate | **met as built** --- complete member lists and complete per-cell values, never a sample |
| 5 | Keep unweighted mean explicitly provisional and non-generalized | **was not met; now met.** Evidence check 3 requires the verbatim label "provisional aggregation rule for representation validation". It now travels beside every `unweighted_mean` in every record, in the generated prose, in `PHENOMENON_PROTOTYPES.md`, in the register and in the handout, with tests |
| 6 | Define the magnitude reference population exactly | **met** --- every `M` carries the definition, assembled from the counts |
| 7 | Ensure magnitude does not drive prototype selection | **met as built** --- the three units are fixed by identity before a value is read, and the records say so |
| 8 | Record the sign convention used for `D` | **met as built** --- A-DIR1, the named change operation, and `D` provisional throughout because the convention is unresolved |
| 9 | Preserve per-field epistemic status through aggregation and templated descriptions | **met as built** --- `derived_status` takes the weakest input status, and the label guard fails the build if a weak value reaches the prose bare |
| 10 | Keep the literature probe as a query-field stub only | **met as built** --- zero retrieval, and the record says so |
| 11 | Maintain an assumptions register with assumption ID, affected fields, rationale, failure mode, verification path, and status | **was not met; now met.** The register had ID, statement, affects, verification path and status. **Rationale** and **failure mode** are now separate columns for all twelve assumptions, with the statement kept as its own column |

**Two of the eleven were gaps** --- 5 and 11 --- and both were closed after the
ruling was read back. The other nine were met by the package as built.

### 4. The ruling's letter set, and what it actually asks of `P`

The ruling's dimensions, verbatim:

> **G** — geography / level; **H** — hazard or climate concept; **S** —
> scenario; **T** — temporal horizon; **C** — compared quantity / change;
> **D** — direction; **M** — magnitude; **V** — supporting numeric evidence and
> operation.
>
> Also preserve **P — provenance / epistemic status**, either explicitly or per
> field.

Three things D-013's letters section does not record:

1. **The ruling writes the order `G, H, S, T, C, D, M, V`**, with `V` last. This
   schema orders them `G H S T C V D M`, with `V` in position six.
2. **The ruling reads `V` as "supporting numeric evidence and operation".** This
   schema reads it as values, and carries the operation inside it --- compatible
   in content, different in emphasis.
3. **The ruling allows `P` "either explicitly or per field".** The per-field
   provenance map **already satisfied it** before D-013 was written. Naming it
   `P` was therefore an improvement in legibility, **not** the closing of a gap,
   and D-013 reads the requirement more strictly than the ruling states it.

**The letter disagreement D-013 records stands and is not resolved here.** The
ruling has no letter for season and this schema has none for the compared
quantity, which lives in `V.change`. The mentor's letters are still what the
code emits, and the next GUIDANCE packet still chooses.

- **Owner:** EXECUTOR, on COORDINATOR instruction. Amends D-013, which stands as
  written.
- **Affected files:** `docs/DECISION_LOG.md`, `src/climrr/phenomenon.py`,
  `scripts/build_phenomenon_prototypes.py`, `docs/PHENOMENON_ASSUMPTIONS.md`,
  `docs/PHENOMENON_PROTOTYPES.md`, `docs/GROUP_MEETING_2026-09-14.md`,
  the three prototype records, `reports/milestones/M1_WP3b_PROTOTYPE_REPORT.md`,
  `tests/test_phenomenon.py`, `tests/test_group_handout.py`.

---

## D-014 --- Proceed on the "our reading" basis, with every provisional status carried through

- **Date:** 2026-09-28
- **Status:** **decided.**
- **Owner:** **Kaiyuan Liao.**
- **Context.** The answer sheet in `docs/MENTOR_EXAMPLES.md` was prepared for
  the mentor one-on-one of 2026-09-17 and carried to the one of 2026-09-24. **At
  neither was it reviewed** (R-003). No line was answered. The group meeting of
  2026-09-14 saw the prototypes and the handout and raised **no material
  objection to the prototype-unit design**; the group is not the data owner and
  its feedback confirms no column semantic (ruling action 12 of
  `docs/M4_WP0_GUIDANCE_RULING.md`). No owner review is available on any
  near date.
- **Decision.** Proceed with the prototype representation **on the "our
  reading" basis**, in order to test what question-answer material could be
  generated from it. **Every `inferred_candidate` and `derived_from_inferred`
  status is carried through to every downstream artifact**, and any QA that is
  ever shown will state that it rests on those statuses.
- **What this is not.** **It promotes nothing.** No column moves; no status is
  upgraded, relabelled or rounded up to "assumed confirmed". It does not
  authorise QA generation --- the M4-WP0 ruling states "QA generation is still
  not authorized", and that stands until a ruling says otherwise.
- **Rationale.** R-002 gave the direction --- use what can be reasonably
  explained, build examples, connect to the literature. No owner review has
  happened in two scheduled attempts, and the project cannot hold M1 and M4
  both closed while waiting for one. Carrying the provisional status everywhere
  is what makes proceeding honest rather than a quiet promotion.
- **Consequence for the M1 gate.** **M1 gate criterion 1 will be evaluated with
  provisional statuses explicitly declared**, not with owner-confirmed ones. The
  gate packet will say so in its first line on that criterion. Whether GUIDANCE
  accepts M1 on that basis is GUIDANCE's call, not this decision's.
- **Alternatives considered.** (a) Wait for the mentor --- rejected by the owner:
  two meetings have passed without a review, and nothing in the schedule
  changes that. (b) Treat the group's lack of objection as confirmation ---
  rejected, and forbidden by ruling action 12. (c) Promote the twenty
  `inferred_candidate` columns on the owner's own authority --- rejected; D-010
  and D-011 reserve `owner_confirmed` for the data owner's explicit answer.
- **Affected files:** `data/metadata/resolutions.yaml` (R-003),
  `artifacts/profiles/dictionary_coverage.json`,
  `artifacts/profiles/status_diff.md`, `docs/MENTOR_BRIEF.md`,
  `docs/PROJECT_STATE.md`, `reports/milestones/M4_WP0_REPORT.md`.

---

## D-015 --- The M4-WP0 GUIDANCE ruling: corpus provenance and inventory, and nothing more

- **Date:** 2026-09-28
- **Status:** **decided.**
- **Owner:** **GUIDANCE**; **approved by Kaiyuan Liao**, who placed
  `docs/M4_WP0_GUIDANCE_RULING.md` in the repository. Gate status: **PASS WITH
  ACTIONS**. The package is named **M4-WP0 --- Literature Corpus Provenance and
  Inventory**, not M1-WP5.
- **What the ruling decides.**
  1. **The collection query is pinned.** `data/metadata/literature_query.txt`,
     byte for byte as received, SHA-256
     `5a7ddf537d343b73fa0887e5f11ffbe3965fd25811f2adfc25cacee66f0ee1e5`, with a
     provenance block in `data/manifest.json` that keeps what the supplier
     reported apart from what the project verified, and writes every unknown
     as `unknown`.
  2. **A deterministic parser.** `climrr.litquery` decomposes the query into its
     Boolean structure, hazard groups and context terms, with character offsets
     back into the source. Lexical normalization only; no reinterpretation. The
     parse is a separate derived artifact,
     `artifacts/literature/query_parsed.json`.
  3. **The comparison is named query-scope coverage**, never corpus coverage.
     It distinguishes `exact_query_term`, `normalized_lexical_match` and
     `absent_from_query`; `inferred_conceptual_relationship` is defined and
     **not used**.
  4. **An external inventory, by byte reads only.** The corpus stays outside the
     repository. Every file gets a stable id, relative path, format, size,
     SHA-256, duplicate group and accessibility status. No content parsing, text
     extraction, rendering, metadata extraction or semantic inspection.
  5. **QA generation is still not authorised.** Nor are paper reading, claim
     extraction, prototype matching, semantic bridges, hazard labels for
     individual papers, retrieval or embeddings.
  6. **The shape of M4-WP1.** A small deterministic literature-ingestion and
     structured-claim pilot of about 6--12 unique papers, drawn **from the
     frozen manifest by rule, independent of prototype relevance**, extracting
     claims **without** deciding whether they match a prototype. Prototype-to-
     claim compatibility begins in M5.
- **What M4-WP0 found that the work package did not anticipate.**
  - **The query's first disjunction holds eleven hazard groups, not ten.** The
    parse is reported as found; nothing was merged to make ten.
  - **`artifacts/literature/` was caught by the `literature/` rule in
    `.gitignore`**, which exists to keep the corpus out. A narrow negation,
    `!artifacts/literature/`, admits the inventory artifacts only; the corpus
    rule is unchanged, and `tests/test_corpus.py` checks that no tracked
    artifact holds the corpus path.
- **Alternatives considered.** On the ignore rule: (a) move the artifacts to a
  directory not named `literature` --- rejected, the work package names the
  path; (b) anchor the corpus rule to `/literature/` --- rejected as a wider
  change than needed.
- **Affected files:** `data/metadata/literature_query.txt`, `data/manifest.json`,
  `data/MANIFEST.md`, `.gitattributes`, `.gitignore`,
  `config/local_paths.example.yaml`, `src/climrr/litquery.py`,
  `src/climrr/queryscope.py`, `src/climrr/corpus.py`,
  `scripts/parse_literature_query.py`, `scripts/query_scope_coverage.py`,
  `scripts/inventory_corpus.py`, `artifacts/literature/*`,
  `docs/LITERATURE_QUERY_SCOPE.md`, `docs/LITERATURE_CORPUS_INVENTORY.md`,
  `docs/METADATA_QUESTIONS.md`, `docs/MENTOR_BRIEF.md`,
  `docs/SOPHIA_RUNBOOK.md`, `reports/milestones/M4_WP0_REPORT.md`,
  `tests/test_litquery.py`, `tests/test_queryscope.py`, `tests/test_corpus.py`.

---

## D-016 --- M4-WP0 reviewed: PASS; the chain merge authorized; M4-WP1 authorized

- **Date:** 2026-09-28
- **Status:** **decided.**
- **Owner:** **GUIDANCE**; **approved by Kaiyuan Liao**, who placed
  `docs/M4_WP0_REVIEW_MERGE_WP1_GUIDANCE_RULING.md` in the repository. Overall
  gate status **PASS WITH ACTIONS**. Reviewed head: **`1e2fd9f`**, pushed to
  `origin/work/m4-wp0`.
- **What the ruling decides.**
  1. **M4-WP0: PASS.** The two disclosed slips --- the scanner hit repaired
     without weakening the scanner, and the mistyped CSV hash caught against
     the file --- do not reopen it.
  2. **Merge strategy.** The linear chain `work/m1-wp2` → `work/m1-wp3` →
     `work/m1-wp3b` → `work/m4-wp0` is merged as **one `--no-ff` merge of
     `work/m4-wp0` into `main`**, after a bookkeeping refresh of the report and
     `PROJECT_STATE.md` to the reviewed head and the real push state. pytest and
     the scanner run on the merge result, and the merge SHA is recorded as the
     new authoritative integrated state.
  3. **The merge does not pass M1.** M1 remains open. D-014 still promotes
     nothing to `owner_confirmed` and turns no `inferred_candidate` into
     verified truth.
  4. **M4-WP1 authorized** as a deterministic **10-paper** ingestion and
     structured-claim pilot:
     - **sample rule:** every 190th stable `LIT` item beginning from
       `LIT-000001`, while preventing the later member of an exact-byte
       duplicate group from appearing as a second unique sample item; the
       sample, the rule and the corpus-manifest SHA are **frozen before any
       sampled file is opened**. The sample is **not statistically
       representative** and must not be described as such;
     - **evidence locations:** item id + corpus-manifest SHA + file SHA-256 +
       JSON key or full JSON path + `char_start` / `char_end` as **zero-based,
       half-open `[start, end)` Unicode code-point offsets against the exact
       JSON string value after JSON decoding and before any normalization**,
       plus the exact evidence text or its hash. No offset is computed after
       lower-casing, whitespace compression, Markdown conversion or sentence
       joining;
     - **negative outcomes are valid:** `off_topic`, `no_eligible_claim`, parse
       failure, ambiguous-only. Off-topic items stay in the result and are not
       replaced. The JSON schema encountered is documented, not assumed;
     - **local-only execution** is approved; no Sophia corpus transfer is
       required now;
     - **no prototype matching**, no prototype-guided reading, no supporting /
       contradicting labels, no embeddings, no corpus-wide search.
  5. **The Wuhan anecdote does not change the sample.** One file that appeared
     off-topic is not a corpus property; changing the sample for it would
     introduce relevance-based selection bias.
  6. **QA generation is still not authorized.** Nor is M5.
- **Affected files:** `docs/M4_WP0_REVIEW_MERGE_WP1_GUIDANCE_RULING.md` (tracked
  as placed), `reports/milestones/M4_WP0_REPORT.md`, `docs/PROJECT_STATE.md`,
  `docs/DECISION_LOG.md`.

## D-017 --- M4-WP1 reviewed: PASS WITH ACTIONS; M5-WP1 authorized as machinery validation

- **Date:** 2026-10-08
- **Status:** **decided.**
- **Owner:** **GUIDANCE**; **approved by Kaiyuan Liao**, who placed
  `docs/M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md` in the repository. Reviewed
  head: **`7ded08e`**, pushed to `origin/work/m4-wp1`.
- **What the ruling decides.**
  1. **M4-WP1: PASS WITH ACTIONS**, as an ingestion and structured-claim
     pilot. All 27 claims are **single-reader provisional** literature claims,
     exact-source anchored, until an independent reading closes that.
  2. **Tracked verbatim excerpts are kept**, under **minimal-evidence-window
     discipline**: retain only the smallest passage needed to support the
     claim or decision; do not track whole sections for convenience; do not
     concatenate large source passages into reports; **hash + offsets remain
     the authoritative locator**; if text must later be removed, the record
     must stay reconstructible from the external corpus and the offsets.
     Replacing excerpts with hash + offsets only is **not** adopted.
  3. **The scope rule is accepted:** `in_scope_hazard` may yield claims;
     `off_topic` is terminal with zero claims; `ambiguous` → `ambiguous_only`
     with zero promoted claims. It validates the pilot rule, not a universal
     ontology of climate-hazard papers.
  4. **`LIT-000571` → `in_scope_hazard` (borderline), accepted.
     `LIT-000761` → `ambiguous_only`, accepted.**
  5. **A second, blind, independent reader is required** over **all ten**
     papers --- not a subsample --- **before** any claim is accepted as M5
     evidence, before any table↔literature pair is accepted as a bridge,
     before "zero compatible pairs" becomes a conclusion about the sample, and
     before any claim becomes QA evidence. It is **not** required before M5
     machinery is implemented. The second reader sees neither the prototypes
     nor the first reader's scope labels or claims during initial extraction;
     a fresh model session without prototype or first-pass context is
     acceptable, followed by explicit adjudication. Planned as **M4-WP1b**.
  6. **Climate scenario and experimental condition are split.** Laboratory
     treatment levels are not climate or emissions scenarios. The two
     `LIT-000191` treatment values move to a new `experimental_condition`
     dimension (`explicit` / `inferred` / `unknown`); after the move,
     **`scenario` is `unknown` for 27/27 WP1 claims.** Every claim also
     carries `claim_validation_status`, with vocabulary
     `single_reader_provisional`, `independently_confirmed`,
     `adjudicated_modified`, `rejected_on_review`; all 27 are
     `single_reader_provisional`.
  7. **M5-WP1 authorized** as **deterministic negative-case compatibility
     machinery validation** on the fixed 27 claims × 3 prototypes = 81 pairs,
     five dimensions each (concept, geography, time, scenario, direction),
     each `compatible` / `incompatible` / `not_evaluable` with rule ID, both
     compared values and a reason. No embeddings, no LLM pair judgement. Its
     outputs are validation results over provisional claims, not accepted
     bridges. The ruling's 22 acceptance criteria govern it.
  8. **A relevance-guided M4-WP2 becomes justified only if** M5-WP1 shows:
     (i) the deterministic machinery works correctly on all 81 pairs; (ii) the
     content-independent sample yields no fully compatible pair, or too few
     positives to exercise the positive case; (iii) failure modes are visible
     dimension by dimension; (iv) WP0 independently shows prototype concepts
     present in collection vocabulary; (v) the second-reader / adjudication
     work does not materially overturn the negative pilot conclusion. It
     would optimize candidate yield, not estimate prevalence, and its
     retrieval rule returns to GUIDANCE after M5-WP1.
  9. **QA generation is still not authorized.**
- **Closure actions done on `work/m4-wp1`** (this entry's commit): schema split
  and validation status in `scripts/wp1_extractions.py` and
  `scripts/build_wp1_claims.py`; records rebuilt --- **all 96 span locators and
  evidence hashes identical to `7ded08e`**, span integrity 96/96 against the
  corpus; pilot document re-rendered; two tests added; report fields 3, 4, 7,
  9, 13, 14 and `PROJECT_STATE.md` refreshed. Merge to `main` is Kaiyuan's.
- **Affected files:** `docs/M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md` (tracked
  as placed), `scripts/wp1_extractions.py`, `scripts/build_wp1_claims.py`,
  `scripts/render_wp1_pilot.py`, `tests/test_wp1_claims.py`,
  `artifacts/literature/wp1_claims/*.json`,
  `artifacts/literature/wp1_claims_summary.json`,
  `docs/LITERATURE_WP1_PILOT.md`, `reports/milestones/M4_WP1_REPORT.md`,
  `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

## D-018 --- M5-WP1 reviewed: PASS WITH ACTIONS, machinery validation only; concept map, P-STATE-1 v2, WP1b and WP2 retrieval authorized

- **Date:** 2026-10-08
- **Status:** **decided.**
- **Owner:** **GUIDANCE**; **approved by Kaiyuan Liao**, who placed
  `docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md` in the repository. Reviewed
  head: **`c1010f0`**; merged into `main` at `55decb3`, scan fix `656044c`.
- **What the ruling decides.**
  1. **M5-WP1: PASS WITH ACTIONS --- machinery validation only.** Its frozen
     inputs and matrix stay unchanged and reproducible at their original
     hashes; the result remains valid for the prototype version it used. It is
     not validated bridge evidence.
  2. **P-STATE-1 year windows: authorized as a versioned provenance
     correction.** Cite exact dictionary spans; inherit the same epistemic
     status as the underlying interpretation; change no ClimRR numeric value;
     log the amendment; hash and version the rebuilt prototype. **Do not
     rewrite the frozen M5-WP1 input.**
  3. **`concept_map.yaml` is authorized**, with family-versus-metric
     specificity preserved. The ruling's rule, verbatim: *"A claim concept may
     match a canonical concept only by exact membership in an approved
     surface-term set."* *"Broad vocabulary must **not** silently map to a
     narrower metric."* Distinguish **concept family** (e.g. `heat_index`,
     `fire_weather_index`) from **specific metric / measure** (e.g.
     `days_above_105F`, a seasonal FWI statistic, percent change).
     `"heat index"` → a threshold-specific metric: **not by that phrase alone.**
  4. **Who may approve a mapping**, verbatim: *"COORDINATOR may approve
     mechanically source-backed lexical aliases without another GUIDANCE round
     only when the alias does not broaden, narrow, or reinterpret scientific
     meaning. Scientific synonymy, hierarchy, threshold interpretation, or
     family→metric narrowing must return to GUIDANCE or the mentor."* No UHI →
     heat index, wildfire smoke → FWI, or drought → FWI mapping on scientific
     relatedness.
  5. **`candidate_bridge_eligible`**, verbatim: a pair may advance for bridge
     review when *"concept = `compatible`; geography = `compatible`; no
     dimension is `incompatible`; time may be `compatible` or `not_evaluable`;
     scenario may be `compatible` or `not_evaluable`; direction may be
     `compatible` or `not_evaluable`."* Candidate eligibility is **candidate
     bridge**, not validated supporting bridge; it is defined separately from
     the final M5 relation.
  6. **Unknown scenario is tolerated for candidacy, never for unqualified
     support**, verbatim: *"a scenario-specific ClimRR prototype cannot receive
     an unqualified `supporting` relation from a claim whose scenario is
     unknown. Unknown scenario/time must remain visible in the final M5
     relation."* Missing scenario is never scenario compatibility; "nothing
     contradicts it" is never `supporting`.
  7. **M4-WP1b authorized: a blind second reading of all ten WP1 papers.** The
     second reader receives the ten frozen items, the extraction
     rubric/schema and the evidence-location rules, and **not** the
     prototypes, first-reader claims or scope labels, M5 results, or expected
     outcomes. Its independent result is frozen before comparison and
     adjudication; both readings and the adjudication are kept; disagreements
     are preserved, not overwritten.
  8. **M4-WP2 retrieval conditionally authorized**: approved concept terms +
     approved prototype place terms → **boundary-aware** lexical scan
     (unrestricted substring matching **rejected**) over all decoded JSON
     string values → qualify iff ≥1 concept hit and ≥1 place hit →
     **deduplicate exact-byte duplicates before the cap** → stable LIT-id order
     → first 12 → **freeze before reading**. **Approved place terms only**: no
     silent `California→CA`, `Oklahoma→OK` or similar. Every hit records item
     id, JSON path, matched term, term class and exact span. No manual
     replacement. Labelled **relevance-guided candidate-generation sample, not
     representative**. A retrieval hit is not a semantic bridge. **Semantic
     reading of WP2 candidates waits until WP1b closes** without materially
     invalidating the premise for relevance-guided sampling.
  9. **QA generation is still not authorized.**
- **Mentor question recorded** (verbatim from the ruling, now first for the
  next one-on-one in `MENTOR_BRIEF.md`): *"Does the intended bridge require
  literature to match the exact ClimRR metric/scenario, or is support at the
  broader hazard/concept level sufficient when unmatched dimensions are
  explicitly disclosed?"*
- **COORDINATOR approvals under item 4, recorded here:** the seed entries of
  `data/metadata/concept_map.yaml` with status `approved_lexical` ---
  `fire_weather_index` (family; "fire weather index", "FWI") and `heat_index`
  (family; "heat index"), each term quoted from a dictionary line. The two
  metric entries (`fwi_seasonal_value`, `heatindex_days_above_105F`) are
  `proposed` with **no** surface terms: no dictionary phrase names either
  statistic, and narrowing to them needs GUIDANCE or the mentor.
- **Affected files:** `docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md` (tracked
  as placed), `docs/DECISION_LOG.md`, `reports/milestones/M5_WP1_REPORT.md`
  (fields 3, 14), `docs/MENTOR_BRIEF.md`, and on `work/m4-wp2-retrieval`:
  `artifacts/phenomena/prototypes/P-STATE-1.v2.json`,
  `data/metadata/concept_map.yaml`, `src/climrr/compat.py`,
  `src/climrr/bridge.py`, the WP2 retrieval artifacts.

## D-019 --- M4-WP1b and M4-WP2 retrieval reviewed: PASS WITH ACTIONS; evidence tiers; C-2 revised; reading of the four candidates authorized

- **Date:** 2026-10-08
- **Status:** **decided.**
- **Owner:** **GUIDANCE**; **approved by Kaiyuan Liao**, who placed
  `docs/M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md` in the repository.
  Reviewed heads: M4-WP1b **`25a86e5`**, M4-WP2 retrieval **`7ddee2c`**; both
  merged into `main` at **`e7da7cc`**.
- **What the ruling decides.**
  1. **M4-WP1b: PASS WITH ACTIONS** --- an independent-reading validation
     package, with contested claims kept explicitly qualified.
  2. **Rule 3 span-limited trimming is approved**: keep only the part of a
     value that both readers support and that an explicit evidence span
     actually states; the surviving fragment stays `explicit` when the cited
     span states it.
  3. **J-1 is approved as a one-off schema-placement override**, with the
     literal rule result preserved. Not a general permission to rescue facts
     whenever adjudication yields `unknown`; a new override needs explicit
     justification.
  4. **`LIT-000381-C3.claim_type` stays `unresolved_tie`.** Any rule that
     depends on claim type treats it as `not_evaluable` until independently
     resolved.
  5. **`LIT-000571` stays scope-contested.** Its five claims remain
     `adjudicated_modified` / scope-contested and **may not serve as
     independently validated M5 evidence**; they may enter diagnostic
     compatibility analysis with that status carried.
  6. **Evidence tiers**: **A** `independently_confirmed` (strongest); **B**
     `adjudicated_modified` (usable for candidate/bridge analysis when the
     adopted value is source-supported, the disagreement preserved, and no
     unresolved issue directly determines the bridge); **C**
     single-reader / contested provisional (diagnostic or candidate use only;
     cannot independently establish an accepted bridge).
  7. **Third reader**: not required for the whole WP1 set; **required** if a
     final accepted bridge depends materially on a scope-contested claim, an
     unresolved tie affecting the bridge, or a single-reader-only semantic
     assertion.
  8. **C-2 revised**: from whole-field exact equality to **boundary-aware
     occurrence of an approved family surface term inside the claim's tagged
     concept field**, using the frozen retrieval matcher; record matched term,
     family id, concept-field span and concept-map provenance. **No new
     synonyms.** `"heat index trends"` → family-level; `"urban heat island"`
     and `"wildfire smoke exposure"` → `not_evaluable`. A family match is never
     metric support.
  9. **M4-WP2 retrieval: PASS, sample size 4**, not 12. The four frozen
     candidate ids and retrieval artifacts stay unchanged; no place-term
     expansion before reading; widening to all US states is a separately
     predeclared WP2b, not part of WP2.
  10. **Reading of the four candidates is authorized**, with the two-reader +
      adjudication structure (reader 1; a blind reader in a fresh session given
      only the four files, the rubric and the location convention; then
      adjudication by the approved WP1b rules), followed by compatibility
      against all three prototypes using **P-STATE-1 v2**, with v1 and the
      frozen M5-WP1 inputs unchanged.
  11. **QA generation is still not authorized.**
- **Open task recorded (cleanup, not a blocker):** repair the baseline-window
  citation chain of **P-CELL-1 / P-COUNTY-1** so that equivalent horizon claims
  cite the same authoritative metadata source as P-STATE-1 v2.
- **Mentor question kept** (verbatim): *"Is a family-level literature bridge
  with disclosed metric/scenario mismatch useful for the intended benchmark,
  or must literature support the exact ClimRR metric and scenario?"* Until it
  is answered, `supporting_qualified` stays analytically separate from
  unqualified `supporting`.
- **Affected files (on `work/m4-wp2-read`):** this log; the ruling, tracked as
  placed; `src/climrr/compat.py` (C-2 revised, tie rule), `src/climrr/wp1b.py`
  and `scripts/wp1b_adjudicate.py` (evidence tiers), the regenerated
  `artifacts/literature/wp1_claims_adjudicated/` (`evidence_tier` added,
  nothing else changed --- tested against `e7da7cc`),
  `docs/LITERATURE_WP1B_ADJUDICATION.md`, `docs/BRIDGE_ELIGIBILITY.md`,
  `reports/milestones/M4_WP1B_REPORT.md` and `M4_WP2_RETRIEVAL_REPORT.md`
  (field 14), `scripts/stage_knowledge.py`, `docs/PROJECT_STATE.md`.

---

## D-020 --- Mentor direction: define concepts from the table units first, then collect papers for them

- **Date:** 2026-10-09 (the one-on-one); recorded 2026-10-19 in M4-WP3.
- **Status:** **decided.**
- **Owner:** **the mentor**, relayed by Kaiyuan Liao.
- **Decision.** Define the literature concepts from the table units first, then
  collect papers for those concepts with the ANL paper-collection tool, rather
  than reading a corpus collected for another purpose. Keep the three units
  (P-CELL-1, P-COUNTY-1, P-STATE-1) for now.
- **Context (the EXECUTOR's, not the mentor's words; no rationale was
  relayed).** The direction followed the M5-WP2 result --- 0 eligible pairs of
  78 --- on LITCORPUS-00, a corpus collected by a hazard query whose scope
  covers one of the pilot concept terms exactly and three not at all.
- **Consequences.** A new, separately versioned concept-first corpus. The legacy
  corpus and every M4-WP0--WP2 artifact are kept unchanged, as method
  validation and negative-case evidence (D-021).
- **Affected files:** this log; `docs/MENTOR_BRIEF.md`.

## D-021 --- Concept-first collection ruling (GUIDANCE): PASS WITH ACTIONS

- **Date:** 2026-10-12
- **Status:** **decided.**
- **Owner:** **GUIDANCE**; placed by Kaiyuan Liao as
  `docs/M4_WP3_CONCEPT_FIRST_GUIDANCE_RULING.md`.
- **What the ruling decides.** The concept-first pivot is the primary path for
  positive-bridge discovery. A **new, separately versioned corpus**, not a
  continuation of LITCORPUS-00. Collection queries use **only tracked
  concept-map family vocabulary** --- no scientific synonyms without
  concept-map governance. **No US place term in collection**; geography
  filtering only after the concept corpus is frozen. Year / venue / authors stay
  **`unknown`**. M4-WP0-style provenance is required. Next package **M4-WP3**.
  **No paper is read before the provenance/yield packet is reviewed.** QA
  generation still not authorized.
- **Consequences.** The earlier corpus history is not rewritten; LITCORPUS-00
  stays the record of what was tried first.
- **Affected files:** this log; the ruling, tracked as placed.

## D-022 --- Source-yield ruling (GUIDANCE): PASS WITH ACTIONS; LITCORPUS-01 frozen as a pilot; R-FWI-1

- **Date:** 2026-10-12
- **Status:** **decided.**
- **Owner:** **GUIDANCE**; placed by Kaiyuan Liao as
  `docs/M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md`.
- **What the ruling decides.**
  1. The shard run is frozen as **`LITCORPUS-01-conceptfirst-v1`** --- a
     provenance/yield pilot, **not** the bridge corpus.
  2. A **larger and/or domain-appropriate source** is authorized, queried with
     the **identical frozen queries**; each source arm separately identified.
  3. The context-free runs are **"collection sensitivity diagnostics"**, never
     a corpus version.
  4. **Retrieval rule R-FWI-1:** bare `fwi` admits a document only with a
     same-document approved disambiguator --- `fire weather`, `fire-weather`,
     `fire weather index`, `fire-weather index`, `canadian forest fire weather
     index`, `canadian fwi` --- same-document, not same-sentence, with both hit
     locations recorded. Longer terms admit directly.
  5. **`FWI` stays in `concept_map.yaml`, unchanged.** R-FWI-1 is retrieval
     governance, not a change to the concept.
  6. LITCORPUS-01 provenance mechanics may proceed. **No reading.**
- **Implemented in M4-WP3** as `climrr.retrieval` (R-FWI-1 v1), documented in
  `docs/BRIDGE_ELIGIBILITY.md` §5. The 705k run applied it with the argument
  `fwi=fire weather|fire-weather`, which is equivalent to the six-term list for
  the frozen fire query (`docs/LITCORPUS02_PROVENANCE.md` §4).
- **Affected files:** this log; the ruling; `src/climrr/retrieval.py`,
  `tests/test_retrieval.py`, `docs/BRIDGE_ELIGIBILITY.md`.

## D-023 --- Source received: `full_705k_v2_filtered.zip`

- **Date:** 2026-10-19
- **Status:** **decided** (a record of receipt).
- **Owner:** **Kaiyuan Liao**.
- **What was received.** `full_705k_v2_filtered.zip`, supplied by **JL** through
  a Google Drive link following the 2026-10-13 mentor meeting. JL's email:
  *"the google drive link that I shared with you have 200K version of filtered
  climate dataset with name full_705k_v2_filtered. This contains actually
  186,346 json files."* **2,283,251,035 bytes**; SHA-256
  **`516baf87049eda6b117f230e23ec52a016301ce482fc4edcd3581a6897baaa94`**;
  **186,346** `.json` files, **7,651,208,072** bytes unpacked. Stored on
  Polaris/Eagle under the path held in the untracked `config/local_paths.yaml`
  at the new key `litcollect_root_polaris`. **Immutable from receipt.**
- **Unknown.** How JL filtered "705k → 186,346" (**Q22**). The provenance of the
  705k parent is JL's, **reported, not verified**.
- **Affected files:** this log; `docs/METADATA_QUESTIONS.md` (Q22);
  `config/local_paths.example.yaml`; `docs/LITCORPUS02_PROVENANCE.md`.

## D-024 --- LITCORPUS-02 frozen

- **Date:** 2026-10-19
- **Status:** **decided.**
- **Owner:** **CONTROL / Kaiyuan Liao**.
- **Decision.** **`LITCORPUS-02-conceptfirst-705k-v1`** is the union of the two
  admitted production arms --- `fire_weather_v1` (495 raw → **448** after
  R-FWI-1) and `extreme_heat_v1` (**861**), overlap 1 --- **1,308 items**,
  produced by the frozen v1 queries and R-FWI-1 over the D-023 source. Each
  item keeps its source basename as item id and receives a frozen `LIT2-NNNNNN`
  in code-point order of that id. LITCORPUS-00 and LITCORPUS-01 are
  **retained, not discarded**.
- **Consequences.** The corpus files stay on Eagle; manifests, ids, hashes and
  hit locations are tracked under `artifacts/literature/litcorpus02/` and
  pinned in `data/manifest.json` (`external_corpora`). The geography preflight
  (100 / 143 place candidates) is frozen and **unread**.
- **Affected files:** this log; `artifacts/literature/litcorpus0{1,2}/`,
  `data/manifest.json`, `docs/LITCORPUS01_SHARD_PILOT.md`,
  `docs/LITCORPUS02_PROVENANCE.md`, `reports/milestones/M4_WP3_REPORT.md`.

## D-025 --- M4-WP3 reviewed: PASS WITH ACTIONS; LITCORPUS-02 the working corpus; five terms governed; WP4 sample and Stage 2a--2c authorized

- **Date:** 2026-10-19
- **Status:** **decided.**
- **Owner:** **GUIDANCE**; placed by Kaiyuan Liao as
  `docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md`. Reviewed head
  **`6b2b5a6`** (pushed, `origin/work/m4-wp3`).
- **What the ruling decides.**
  1. **M4-WP3: PASS WITH ACTIONS.**
  2. **`LITCORPUS-02-conceptfirst-705k-v1` is the working concept-first
     candidate corpus** --- for candidate generation, **not** a representative
     sample of the literature (448 / 861 / 1,308).
  3. **LITCORPUS-01 stays the provenance/yield pilot; its sectionization is
     closed as not required.**
  4. **Q22** (the upstream 705k → 186,346 filter) **stays open**; not a blocker
     for candidate use.
  5. **Five query terms governed** (`source_type: guidance`, `decision_id:
     D-022`, approval under D-025): `fire-weather index`, `canadian forest fire
     weather index`, `canadian fwi` (`fire_weather_index`) and `heat-index`
     (`heat_index`) are **`approved_lexical`** --- collection, retrieval and C-2;
     **`extended heat index`** is **`approved_family_term`** for heat-index
     collection and retrieval only --- not a synonym of heat index, not the
     threshold metric `heatindex_days_above_105F`.
  6. **R-FWI-1 accepted as implemented** (six disambiguators).
  7. **Matcher difference accepted as a disclosed limitation**: the yield change
     is **not** a formal source-effect estimate.
  8. **A 20-paper two-reader pilot (M4-WP4) is authorized** with the rank-based
     10 + 10 rule: ranks 10, 20, …, 100 (fire) and 14, 28, …, 140 (heat) after
     sorting by `LIT2` id and suppressing later exact-byte duplicates for
     sampling only; advance on a missing rank; fire before heat on overlap.
     Frozen before reading; reader 1 → blind reader → freeze → comparison →
     adjudication → evidence tiers → compatibility.
  9. **Stage 2a--2c authorized as diagnostics**: dictionary-described concepts
     only; model proposals are `candidate_surface_form` and inert; literature
     yield never selects units or assigns column meaning.
  10. **Global `.gitattributes` cleanup deferred** to a housekeeping package.
  11. **QA not authorized.**
- **Implementation (M4-WP3 closeout).** `data/metadata/concept_map.yaml` gains
  per-term `additional_surface_terms` (the dictionary-backed
  `accepted_surface_terms` are unchanged); `climrr.conceptmap.c2_terms` feeds C-2
  the dictionary terms plus the `approved_lexical` forms; an
  `approved_family_term` occurrence in a claim concept masks the family-term
  hits it contains, so "extended heat index" is never a C-2 match. Concept-map
  SHA-256 `6ec6b081…3664` → **`27f7a44d…d7b4`**. The frozen M4-WP2 terms and
  M5-WP2 inputs keep their recorded pre-D-025 hashes (tested against the blobs at
  `6b2b5a6`); the M5-WP2 matrix reproduces unchanged under the new C-2 (no
  adjudicated claim contains any of the five terms).
- **Affected files:** this log; the ruling; `data/metadata/concept_map.yaml`,
  `src/climrr/conceptmap.py`, `src/climrr/compat.py`, `tests/test_conceptmap.py`,
  `tests/test_retrieval.py`, `tests/test_wp2_retrieval.py`, `tests/test_m5wp2.py`,
  `tests/_frozen_state.py`; `docs/BRIDGE_ELIGIBILITY.md`,
  `docs/LITCORPUS01_SHARD_PILOT.md`, `docs/LITCORPUS02_PROVENANCE.md`,
  `reports/milestones/M4_WP3_REPORT.md`, `docs/PROJECT_STATE.md`,
  `docs/MENTOR_BRIEF.md`; `scripts/wp4_sample.py`,
  `artifacts/literature/wp4_sample.json`.

## D-026 --- Stage 2a inventory granularity: measure level

- **Date:** 2026-10-20
- **Status:** **decided.**
- **Owner:** **Kaiyuan Liao**, answering the EXECUTOR's escalation during Track
  B Stage 2a (the work package said "one entry per dictionary-described variable
  or metric" without fixing the unit). Recorded by the EXECUTOR; for COORDINATOR
  and GUIDANCE review with `reports/milestones/TRACKB_STAGE2_REPORT.md`.
- **Options put.** (a) **measure level** --- one concept per ClimRR output
  quantity the narrative (pp. 4--12) describes; (b) variable level --- one per
  item of the p. 4 variable list, linked to differently-titled narrative
  sections by an EXECUTOR inference; (c) field level --- one per field-table row
  (~270, scenario variants separate).
- **Decision: (a).** Two quantities the dictionary describes in one passage
  (maximum and minimum daily temperature; HDD and CDD) stay one concept. The heat
  index is split as the dictionary enumerates it, the four thresholds as four
  concepts (p. 12: "the 6 variables"). Methodology sections (Climate Scenarios,
  Downscaled Climate Models, Ensemble Means, Components of the FWI) are
  excluded; the variable lists on pp. 4 and 13 and the field-table rows are not
  separate concepts. Result: **14 concepts, 0 `listed_only`**.
- **What it does not decide.** Nothing about any CSV column; no status moves;
  index 117 stays unlabeled; no family assignment (`family_hint` null).
- **Second owner decision, same session --- scanner exemption.** The delivered
  `survey_driver.py` and `probe_alcf_inference.py` trip the secrets scan's
  credential-word rule 12 times (the env var name, a parameter, the Bearer
  header; no credential value). Editing them would break "do not modify" and
  the pinned SHA-256; CLAUDE.md requires a stop. Kaiyuan chose a **hash-pinned
  allowlist** in `scripts/verify_no_secrets_or_paths.py`: for exactly those two
  paths, and only while each file's SHA-256 equals the pinned value, the
  credential-word rule is not reported; path and key-prefix rules still apply;
  any change makes the exemption lapse. Tested in `tests/test_secrets_scan.py`.
- **Confirmed by the COORDINATOR (2026-10-20, Track B follow-up on `246fccd`):
  both decisions** --- measure-level granularity and the hash-pinned allowlist.
  In the same follow-up the COORDINATOR issued a revised `survey_driver.py`
  (SHA-256 `877fec477c5005f0642e31b558b3a01493d5466680546fc610bc3d05e8797155`,
  replacing `b3292e22…0d3a`): a parenthetical-stripped variant of the dictionary
  name; `%`, `°` and quotes no longer admitted; a concept with no searchable
  candidate or a failed scan gives a `status: "error"` row and the run continues.
  The allowlist is re-pinned to the new hash; the two litcollect scripts join the
  CLAUDE.md run-record exemption list.
- **Tools v2 → v3 for survey run 1 (Track B follow-up, 2026-10-20).** The
  Polaris run first aborted in `run_query.py`'s offsets stage, which is
  O(admitted documents × terms) in Python and took **more than 3 h** for the
  120,050-document context set; no outputs were kept. v3 adds an opt-in
  `--no-hits` flag to `run_query.py` (skip the offsets stage; header-only
  `hits.csv`; `summary.json` gains `hits_recorded`; counts and id sets
  unchanged) and makes `survey_driver.py` pass it. Nothing else changes.
  - `run_query.py`: `a93eeba766f2eb4d487a8a157d2a2d207b41af0482fefdb774886a66c2d57708`
    (v2, the file that produced LITCORPUS-02, recoverable at `38116a0`) →
    **`5f56ee49f0da675f49ef490b506c030b307c693032e8be9097e499cf1c64030d`**.
  - `survey_driver.py`: `877fec477c5005f0642e31b558b3a01493d5466680546fc610bc3d05e8797155`
    → **`e1fb664c98e4ff866bb348c8930bfc1b9243957441b8a19ea0893e0b711af4cd`**.
  The allowlist is re-pinned to the v3 driver; `--no-hits` is tested
  (`tests/test_litcollect_tools.py`, `tests/test_survey_driver.py`). Run 1 was
  executed from untracked copies in the litcollect `scripts/` folder whose
  SHA-256 equal the tracked v3 files; ingested as the diagnostic
  `TRACKB-SURVEY-RUN1` (`docs/CONCEPT_COVERAGE_SURVEY.md`).
- **Affected files:** this log; `scripts/verify_no_secrets_or_paths.py`,
  `tests/test_secrets_scan.py`; `src/climrr/dictconcepts.py`,
  `scripts/build_dictionary_inventory.py`, `data/metadata/dictionary_concepts.yaml`,
  `docs/DICTIONARY_CONCEPTS.md`, `data/manifest.json`, `tests/test_dictconcepts.py`.

## D-027 --- Track A (M4-WP4 / M5-WP4) and Track B (Stage 2 run 1) reviewed: PASS WITH ACTIONS; bounded zero accepted; geography role approved; unit-granularity diagnostic next; family-level run 2 and narrow orthographic normalization authorized

- **Date:** 2026-10-20
- **Status:** **decided.**
- **Owner:** **GUIDANCE**; placed by Kaiyuan Liao as
  `docs/M4_WP4_TRACKB_GUIDANCE_RULING.md` (byte-identical to the delivered
  `CLIMRR_TRACKA_TRACKB_GUIDANCE_RULING_2026-10-20.md`, SHA-256
  `ae4129d3a16c5b4d9b60422b5ef37022b21b441c8d60affc0bf793ffab246402`). Reviewed
  heads **`c0be540`** (`work/m4-wp4-adj`, Track A) and **`2331e19`**
  (`work/trackb-stage2`, Track B), both pushed; base `main` @ `38116a0`.
- **Gate:** **PASS WITH ACTIONS** for both tracks. M4-WP4 passes as the
  20-paper, two-reader semantic-reading/adjudication pilot; M5-WP4 passes as the
  bounded positive-case compatibility experiment (**0 candidate-bridge-eligible
  pairs among 354** deterministic claim--prototype comparisons); Stage 2a--2c run
  1 passes as a diagnostic. Both merges are authorized after this bookkeeping.
- **Bounded statement (A1), verbatim:** "No candidate-bridge-eligible pair was
  found under the current deterministic rules among the adjudicated claims of
  the twenty frozen LITCORPUS-02 place candidates." Do not generalize beyond the
  tested sample.
- **The ruling's decision table, verbatim:**

  | Question | Ruling |
  |---|---|
  | A1 M4-WP4 gate | **PASS WITH ACTIONS** |
  | A1 M5-WP4 gate | **PASS WITH ACTIONS — bounded zero accepted** |
  | Merge Track A | **Authorized after ruling bookkeeping** |
  | A2 geography role enters G-1 | **Approved** |
  | Conservative role on disagreement | **Approved** |
  | `cited_study_area` as study geography | **Approved, evidence tier retained** |
  | `m5wp4.py` layered over frozen `compat.py` | **Approved** |
  | A3 `standardized heat index` | **Prospectively mask from automatic C-2 matching** |
  | Rewrite frozen WP4 matrix | **No** |
  | A4 mixed-continent geography | **Prospectively `not_evaluable` unless wholly disjoint** |
  | A5 next route | **Unit-redesign diagnostic** |
  | Scenario-keyword retrieval as next primary route | **No** |
  | Immediately replace existing prototypes | **No** |
  | B1 Stage 2 run 1 | **PASS as diagnostic** |
  | Merge Track B | **Authorized after ruling bookkeeping** |
  | B2 family-level run 2 | **Authorized** |
  | Model family assignment | **`candidate_family` only** |
  | B3 threshold measures inherently unsearchable | **No** |
  | Add family-level coverage for threshold concepts | **Yes** |
  | B4 deterministic `°`, `>`, `<`, `%` normalization | **Authorized narrowly** |
  | Semantic synonym/paraphrase normalization | **Not authorized** |
  | B5 choose final families now | **Wait for mentor** |
  | Candidate families to discuss | **temperature, precipitation, wind speed, dry-spell/CDD, degree days, FWI, heat index** |
  | QA | **Still not authorized** |

  *One word differs from the ruling:* in the row "Scenario-keyword retrieval as
  next primary route" the ruling's second word is the secrets scan's credential
  word, used in its ordinary sense; it is replaced here by `keyword`, and the
  exact row is in the ruling file (exempt, below). Every other row is verbatim.
- **What the rows mean, as ruled.**
  1. **Geography role (G-R) gates G-1.** A place string alone is insufficient;
     affiliation, citation/person, contextual or data-source geography never
     becomes geographic compatibility.
  2. **Conservative role on disagreement:** the more conservative geography role,
     unless both readers independently support study geography.
  3. **`cited_study_area` is study geography, evidence tier retained:** it may
     satisfy the role gate, but the claim's evidence tier still constrains
     whether it can establish an accepted bridge.
  4. **`m5wp4.py` layered beside frozen `compat.py`:** old freezes preserved;
     prior compatibility code never mutated retroactively.
  5. **Prospective C-2 mask** for `standardized heat index` (with `extended heat
     index` already masked). The ruling's rule: "**A recognized compound concept
     containing an approved family term must mask that inner phrase when the
     compound's equivalence has not been explicitly approved.**" The frozen
     M5-WP4 matrix is not rewritten.
  6. **Prospective G-2 revision:** `incompatible` only when the entire explicit
     geography is wholly disjoint from the prototype; a mixture of disjoint and
     potentially relevant regions → `not_evaluable`; a broad region containing
     the prototype but not resolving to the required granularity →
     `not_evaluable`; exact supported geography → G-1/G-R. Documented now;
     implemented in a later package; WP4 not rerun for it.
  7. **Next route: a constrained unit-granularity redesign diagnostic** (Track
     A-next); retrieval that requires an RCP/SSP scenario term is not the
     primary next experiment;
     P-CELL-1, P-COUNTY-1 and P-STATE-1 v2 stay as controls.
  8. **Stage 2 run 1: PASS as diagnostic.** **Family-level run 2 authorized**;
     every model family assignment stored only as `status: candidate_family`.
  9. **Threshold measures are not "inherently unsearchable".** The supported
     sentence (B3), verbatim: "**Under the current run-1 candidate terms and
     matcher representation, the threshold-specific heat-index measures have
     effectively no direct lexical footprint in this source.**" Measure-level
     coverage is kept; family coverage is added alongside and never attributed to
     a threshold measure.
  10. **Narrow orthographic normalization authorized (B4):** `>` → above, `<` →
      below, `°F` / `° F` → degrees F, `°C` / `° C` → degrees C, `%` → percent.
      Original model term retained; normalized form stored separately; transform
      rule ids recorded; table frozen before run 2; **no semantic normalization**
      (no paraphrase, stemming, abbreviation expansion, synonym inference).
  11. **Seven discussion families carried to the mentor** --- temperature,
      precipitation, wind speed, consecutive dry days / dry spell, degree days,
      Fire Weather Index, heat index --- as **discussion candidates only**: not
      approved, and **not ranked by coverage**. Heat-index thresholds remain
      measures within the heat-index family.
  12. **QA not authorized.**
- **Owner-confirmed fact (Kaiyuan Liao, 2026-10-20) --- blind-session
  isolation for M4-WP4.** The blind reading (M4-WP4r2, `c452d7d`) ran in a
  **fresh session on `main` @ `38116a0`**, given **only the blind prompt text**,
  and **the prompt forbade opening any other file**. Recorded as an owner
  confirmation of what the session was given; the artifacts alone show only that
  the blind tree held no reader-1 output (`M4_WP4_REPORT.md`, criterion 16).
- **Owner decision (Kaiyuan Liao, 2026-10-20) --- scanner exemption for the
  ruling.** The tracked ruling uses the scan's credential word five times
  (no credential is involved) and must stay byte-identical to the delivered file.
  Kaiyuan chose to add it to the D-026 hash-pinned `WORD_EXEMPTIONS` in
  `scripts/verify_no_secrets_or_paths.py` (SHA-256 `ae4129d3…6402`): only the
  credential-word rule is suppressed, only while the hash matches; the path and
  key-prefix rules still apply. This log is **not** exempt (the one table row is
  reworded instead). Tested in `tests/test_secrets_scan.py`.
- **Provenance gap closed as `unknown` (ruling action 22):** the Polaris Python
  patch version for survey run 1 was not recorded and was not supplied; it is
  recorded as `unknown` (`docs/CONCEPT_COVERAGE_SURVEY.md`, the
  `TRACKB-SURVEY-RUN1` entry in `data/manifest.json`).
- **Implementation (this bookkeeping, two branches).** Track B
  (`work/trackb-stage2`): this entry; the ruling; `KNOWLEDGE_FILES`;
  `data/metadata/litcollect/normalization_table_v1.yaml` (N-1 … N-7, frozen,
  pinned in `data/manifest.json`) with `src/climrr/termnorm.py` and
  `tests/test_normalization_table.py` --- **the driver is unchanged**;
  `docs/CONCEPT_COVERAGE_SURVEY.md` (regenerated);
  `reports/milestones/TRACKB_STAGE2_REPORT.md` fields 14--15;
  `docs/MENTOR_BRIEF.md`. Track A (`work/m4-wp4-adj`): `M4_WP4_REPORT.md` and
  `M5_WP4_REPORT.md` fields 14--15; `docs/BRIDGE_ELIGIBILITY.md` (G-R, `cited_study_area`,
  prospective C-2 mask list and G-2 semantics); `docs/M5_WP4_COMPATIBILITY.md`
  (bounded statement). Next diagnostics (ruling actions 12, 13, 16) **not started**.
- **What it does not decide.** No M1 status changes; index 117 stays
  unlabeled; the frozen M5-WP4 matrix and `compat.py` are unchanged; no
  candidate family is approved; Q22 stays open; no QA.

## D-028 --- Track B Stage 2 run 2 reviewed: PASS WITH ACTIONS (diagnostic only); three-level coverage reporting standing; Track A-next at the governed concept-map family level; Track B paused

- **Date:** 2026-10-21
- **Status:** **decided.**
- **Owner:** **GUIDANCE**; placed by Kaiyuan Liao as
  `docs/TRACKB_STAGE2_RUN2_GUIDANCE_RULING.md` (byte-identical to the delivered
  `CLIMRR_TRACKB_STAGE2_RUN2_GUIDANCE_RULING_2026-10-21.md`, SHA-256
  `9a6a3dc452ee273244eb2ce85d90a83549d5c7efe2ee5c1e1fad0d31fb7b58b0`). Reviewed
  head **`ea2f2ea`** (`work/trackb-run2`); base `main` @ `d7032de`.
- **Gate:** **PASS WITH ACTIONS.** Run 2 is accepted as **"TRACKB-SURVEY-RUN2 —
  family-level diagnostic coverage survey"**; it must never be described as
  ontology generation. **Merge of `work/trackb-run2` is authorized** after this
  bookkeeping; Kaiyuan performs it.
- **The ruling's decision table, verbatim:**

  | Question | Ruling |
  |---|---|
  | R1 Stage 2 run 2 | **PASS WITH ACTIONS — diagnostic accepted** |
  | Merge `work/trackb-run2` | **Authorized after ruling bookkeeping** |
  | R2 three-level coverage reporting | **Approved as standing reporting structure** |
  | Level 1 | **Dictionary-measure diagnostic coverage** |
  | Level 2 | **Governed concept-map family coverage** |
  | Level 3 | **Model-proposed candidate-family diagnostic coverage** |
  | Rank concepts using model-family counts | **No** |
  | Use model-family counts for unit selection | **No** |
  | R3 redesigned units at threshold level | **No, not as primary redesign** |
  | R3 redesigned units at model-family level | **No** |
  | R3 redesigned units at concept-map family level | **Yes** |
  | Immediate redesign families | **`fire_weather_index`, `heat_index`** |
  | Automatically govern the other five discussion families | **No** |
  | R4 additional Track B run before mentor meeting | **No — pause** |
  | Concept-map changes now | **No** |
  | QA | **Still not authorized** |

- **What the rows mean, as ruled.**
  1. **Three-level coverage reporting is the standing presentation:** Level 1
     dictionary-measure diagnostic coverage; Level 2 governed concept-map family
     coverage (only terms accepted through concept-map governance); Level 3
     model-proposed candidate-family diagnostic coverage (never family
     prevalence, approved family coverage, benchmark relevance, or evidence for
     unit selection). The levels are **never ranked or combined**, and Level-2 or
     Level-3 coverage is **never attributed to a Level-1 threshold measure**. A
     Level-1 zero means no direct lexical match under the current measure
     representation and search rules, not that no relevant literature exists.
  2. **Track A-next redesign semantic level = governed concept-map family.**
     Immediate candidates `fire_weather_index` and `heat_index`; the specific
     metric and scenario are kept as provenance (`metric_status:
     provenance_specific_measure`, `scenario_role: provenance`); geography a
     `deterministic_supported_aggregate`. Current exact prototypes remain
     controls. Recorded in `docs/BRIDGE_ELIGIBILITY.md` §9.
  3. **Not approved unit families:** `fire_risk`, `fire_danger`, `hydrology`,
     temperature-for-degree-days, `extreme_heat_days`, `heat_wave_days`. **No
     concept-map change**; all 14 run-2 assignments stay `candidate_family`. The
     five ungoverned discussion families (temperature, precipitation, wind speed,
     dry spell, degree days) get **no units until a separate governance
     decision**.
  4. **Normalization machinery accepted.** N-1 … N-7 firing zero times is
     acceptable: predeclared, frozen, tested, inert when unnecessary.
  5. **Track B paused** after the merge until mentor feedback (2026-10-22); **no
     run 3** and no further family-vocabulary survey. Reopens only via a
     **governance package** (mentor approves a new family for redesign; GUIDANCE
     needs vocabulary evidence to govern an ungoverned family; or a redesigned
     unit requires a new concept-map family).
  6. **QA not authorized.**
- **Run-2 execution provenance (ruling actions 13--14).** Login node and conda
  environment appear in no run-2 output; recorded as **`owner_confirmed`**
  (Kaiyuan Liao), not run-derived: `polaris-login-01`, `module conda/2026-10-01`
  + conda env `globus_env`. **Python patch version: `unknown`** --- not recorded,
  not supplied, and run 1's is not copied. `RUN_FACTS` in
  `src/climrr/coveragesurvey_run2.py` and the `TRACKB-SURVEY-RUN2` entry in
  `data/manifest.json` amended; no hash changed.
- **Mentor key question (2026-10-22), verbatim from the ruling:** "Should a
  benchmark unit represent the exact ClimRR metric, or is a governed
  family-level quantity such as heat index / Fire Weather Index an acceptable
  table-side semantic object when the exact measure and scenario remain
  preserved as provenance?" --- question 1 in `docs/MENTOR_BRIEF.md`.
- **Implementation (this bookkeeping, `work/trackb-run2`):** this entry; the
  ruling and `KNOWLEDGE_FILES`; `src/climrr/coveragesurvey_run2.py` and
  `docs/CONCEPT_COVERAGE_SURVEY.md` (regenerated: the three levels named as
  ruled, the standing rule, the Level-1-zero sentence, owner-confirmed host and
  environment); `data/manifest.json` (amendment);
  `reports/milestones/TRACKB_STAGE2_REPORT.md` fields 14--15;
  `docs/BRIDGE_ELIGIBILITY.md` §9; `docs/MENTOR_BRIEF.md`;
  `docs/PROJECT_STATE.md`; `tests/test_survey_run2.py`. Run 1 and run 2
  manifests, driver v4, prompt F and normalization-table hashes unchanged.
- **What it does not decide.** No M1 status changes; index 117 stays
  unlabeled; no candidate family is approved; no unit schema or code is defined;
  Q22 stays open; no QA.

## D-029 --- Mentor direction 2026-10-22: soft-constrained QA

- **Date:** 2026-10-22 (mentor one-on-one); recorded 2026-10-27.
- **Status:** **decided.**
- **Owner:** **the mentor**, relayed by Kaiyuan Liao. Owner-relayed facts,
  recorded in Kaiyuan's words in `docs/MENTOR_BRIEF.md` (meeting log,
  2026-10-22). Mentor-directed: it takes precedence over earlier GUIDANCE "do
  not do yet" items it touches; GUIDANCE is informed and asked for guardrails,
  not approval.
- **Mentor's direction, verbatim as relayed:** "right now we hardly find solid
  links; soften the rules or involve semantic understanding like an LLM agent to
  get soft-constrained QAs; as long as the original resources from both the
  table side and the paper side are recorded, someone can manually check the
  quality of the QA with that recorded information."
- **Decision.** Semantic matching by an LLM agent is permitted for linking
  table-side objects to paper passages and for drafting example QA pairs, under
  three conditions:
  - **(a) Exact provenance on every candidate.** Table side: unit or filled
    template, columns, rows/cells, scenario, period, computed value. Paper side:
    item id, file SHA-256, JSON path, `[start,end)` span, verbatim passage.
  - **(b) `llm_candidate` until checked and reviewed.** Every LLM output has
    status `llm_candidate` until it passes a deterministic consistency check
    (the span re-slices to the passage; concept and place terms are located;
    the place role is recorded) **and** a human review.
  - **(c) No LLM output enters governed state.** Nothing an LLM produces enters
    the concept map, column statuses, or compatibility rules.
- **Supersession (scoped).** For **the two new tracks only** (Track C, D-030;
  Track D, D-031), this supersedes the earlier rule that compatibility is
  decided by deterministic rules alone. The deterministic matrix machinery
  (C/G/T/S/D) is **retained as a recorded attribute of each candidate, not as
  the gate**. Elsewhere the deterministic rules stand unchanged.
- **Mentor answers recorded (2026-10-22 list):** Q1 "good" --- family-level
  table-side object accepted, exact metric and scenario as provenance; Q2
  "good" --- state / multi-state / climate-region accepted as table-side
  geography; Q3 "good" --- cross-location comparison accepted as a question
  type. **Q4 open** (not discussed).
- **Rationale.** The mentor's direction: the strict deterministic gate yields
  hardly any solid links (0 of 78, M5-WP2; 0 of 354, M5-WP4); quality is to be
  assured instead by recording both sources exactly so that a person can check
  each QA.
- **Alternatives considered.** Keep deterministic rules as the sole acceptance
  gate --- set aside by the mentor's direction for Tracks C and D.
- **Consequences.** A new candidate status `llm_candidate` and its check and
  review steps (`docs/BRIDGE_ELIGIBILITY.md` §10). Track A-next and Track B stay
  GUIDANCE-authorized but are deprioritized behind Tracks C and D. **This entry
  generates no QA, changes no column status, leaves index 117 unlabeled and
  leaves `concept_map.yaml` unchanged.** The answers name no column; no
  `resolutions.yaml` record.
- **Affected files:** `docs/DECISION_LOG.md`, `docs/MENTOR_BRIEF.md`,
  `docs/PROJECT_STATE.md`, `docs/BRIDGE_ELIGIBILITY.md` §10.

## D-030 --- Track C: LLM-assisted grouping over the LITCORPUS-02 place candidates

- **Date:** 2026-10-22 (mentor direction); recorded 2026-10-27.
- **Status:** **decided; design pending.**
- **Owner:** **mentor direction**, relayed by Kaiyuan Liao.
- **Decision.**
  - **Inputs:** the frozen 100 + 143 place-candidate papers (full text from the
    frozen index); the three units and their family-level descriptions; the QA
    types --- pattern → explanation; claim → region identification;
    cross-source validation; compound-risk reasoning; regional contrast;
    cross-location comparison (per mentor Q3, D-029).
  - **Output per paper:** groups (passage → unit → QA type → one example QA
    pair → rationale), each with status `llm_candidate`, carrying the D-029
    provenance and passing the D-029 deterministic check.
  - **Model:** ALCF inference endpoint (Metis `gpt-oss-120b` unless changed).
  - **Execution:** on Polaris; restartable; outputs inspectable mid-run.
- **Rationale.** One of the two directions the mentor asked the project to try
  (D-029).
- **Alternatives considered.** None recorded; mentor-directed.
- **Consequences.** Design, code and run are later work packages; nothing is
  built or run under this entry. Every output is governed by D-029.
- **Affected files:** `docs/DECISION_LOG.md`, `docs/PROJECT_STATE.md`,
  `docs/MENTOR_BRIEF.md`.

## D-031 --- Track D: table-grounded question templates

- **Date:** 2026-10-22 (mentor direction); recorded 2026-10-27.
- **Status:** **decided; design pending.**
- **Owner:** **mentor direction**, relayed by Kaiyuan Liao.
- **Decision.** Mimic the slot-template mechanism of the reference repository
  (D-032), grounded in the table. Slots:
  - `[CONCEPT]` --- dictionary concept families; multi-concept templates
    allowed;
  - `[LOCATION]` --- table-supported state / county labels;
  - `[PERIOD]` --- historical / mid-century / end-century windows as the
    dictionary defines them;
  - `[SCENARIO]` --- RCP4.5 / RCP8.5;
  - `[SEASON]`;
  - `[STATISTIC]`.

  A filled template is a question whose answer is **computed deterministically
  from the table**; its slots generate the literature query; retrieved passages
  are linked by the Track C agent (D-030) under D-029. Phenomenon units are not
  required as a separate object in this track; the frozen three remain as
  controls and provenance examples.
- **Standing constraint retained.** A slot may draw only on columns with status
  `verified_from_dictionary` (or a logged resolution).
- **Rationale.** The second of the two directions the mentor asked the project
  to try (D-029).
- **Alternatives considered.** None recorded; mentor-directed.
- **Consequences.** Design and code are later work packages; no template is
  written or filled under this entry.
- **Affected files:** `docs/DECISION_LOG.md`, `docs/PROJECT_STATE.md`,
  `docs/MENTOR_BRIEF.md`.

## D-032 --- External reference recorded: `LLM_Eval-main.zip`

- **Date:** supplied by the mentor 2026-10-22; hash computed 2026-10-27.
- **Status:** **decided.**
- **Owner:** Kaiyuan Liao (record); the mentor supplied the archive.
- **Decision.** Record `LLM_Eval-main.zip` (WildfireGPT case-study question
  templates and literature-review prompt pipeline; author per file header
  Yangxinyu Xie) as an external reference.
  - **Zip SHA-256:**
    `a88a9f0df284213769b8e65abd69c2c0e8c5f7dec0d46c0d2121338e7ad2938f`
    (computed by Kaiyuan on the Mac, 2026-10-27; two downloaded copies,
    identical hash).
  - **Contents** (for the record, from inspection of the archive, not copied
    into the repo): `templates.py`, `infrastructure.py`, `prompt.py`,
    `prompt.yml`, `search.py`, `index.py`, `embedding.py`, `utils.py`,
    `README.md`, `WildfireGPT Case Study Questions.md`, `pyproject.toml`.
  - **Taken from it:** the template/slot mechanism (`templates.py`,
    `infrastructure.py`); the question categories (fact-based / recommendation
    / hybrid; data analysis / literature review / both); the case-study
    question table.
  - **Not taken:** its random slot filling, its embedding retrieval, its
    news-style answer generation.
- **Rationale.** Track D (D-031) mimics its slot mechanism; the source must be
  pinned.
- **Alternatives considered.** None.
- **Consequences.** **Nothing from the zip is stored in the repository** except
  this record and the `docs/REFERENCES.md` entry.
- **Affected files:** `docs/DECISION_LOG.md`, `docs/REFERENCES.md`,
  `scripts/stage_knowledge.py` (`KNOWLEDGE_FILES`).

## D-033 --- Track C / Track D soft-QA guardrails: PASS WITH ACTIONS (guardrail update)

- **Date:** 2026-10-27 (GUIDANCE ruling); recorded 2026-10-27.
- **Status:** **decided.**
- **Owner:** **GUIDANCE**, placed by Kaiyuan Liao. Ruling tracked verbatim as
  [`docs/TRACKC_TRACKD_SOFT_QA_GUARDRAILS_RULING.md`](TRACKC_TRACKD_SOFT_QA_GUARDRAILS_RULING.md)
  (SHA-256 `1d1b3bb8…7d39`), on `KNOWLEDGE_FILES`. GUIDANCE was notified of the
  mentor direction (D-029--D-031) on 2026-10-27 and returned this ruling the
  same day.
- **Gate status:** **PASS WITH ACTIONS --- guardrail update only.** It refines
  D-029 for Tracks C (D-030) and D (D-031); it supersedes nothing outside them.
- **Validity chain (verbatim):** "candidate generation → deterministic
  provenance/consistency checks → human semantic review → accepted QA" --- not
  "deterministic compatibility → QA".
- **Decision table (verbatim from the ruling):**

  | Question | Ruling |
  |---|---|
  | One human reviewer enough by default? | **Yes, after deterministic pre-checks** |
  | Two reviewers for every QA? | **No** |
  | Mandatory second reviewer for ambiguous/high-risk cases? | **Yes** |
  | Human reviewer blind to QA itself? | **No** |
  | Human reviewer initially blind to agent confidence/rationale? | **Yes, preferred** |
  | Deterministic checks before human review? | **Required** |
  | Agent may see unit definitions? | **Yes** |
  | Agent may see computed table values during proposal? | **No** |
  | Reveal values after candidate structure freezes? | **Yes** |
  | Agent may generate final authoritative numeric answer? | **No; deterministic computation should** |
  | Unverified column allowed as query-only term? | **No** |
  | Multi-concept QA allowed? | **Yes, if every semantic slot is authorized** |
  | C/G/T/S/D still recorded? | **Yes** |
  | C/G/T/S/D remain acceptance gate? | **No** |
  | LLM output may modify concept map or column status? | **No** |

- **Review.** **One independent human reviewer** after the deterministic
  pre-checks is sufficient for ordinary candidates; the reviewer is not the
  generating agent or process. A **second reviewer** is mandatory for the
  ruling's ten listed high-risk cases (first reviewer `ambiguous`; soft/related
  concept relation; geography beyond explicit study area; multi-concept;
  cross-location comparison with differing granularity; material scenario or
  time mismatch; derived statistic; background/cited passage; reviewer-requested
  escalation). **Disagreement → `needs_adjudication`**, resolved by a third,
  adjudicating reviewer. Failure of any mandatory mechanical check →
  `rejected_pre_review`, never "send to a human and see". Evidence first; agent
  confidence and rationale last. Protocol: `docs/SOFTQA_REVIEW_PROTOCOL.md`.
- **Agent visibility.** **Definitions only** during proposal: unit definitions,
  family descriptions, permitted QA types, the paper, the provenance schema.
  **Never** computed table values, derived answers, target answer direction, or
  prior accepted/rejected answers for the same paper. Values are populated by
  deterministic code only after the candidate structure is frozen; the
  authoritative answer comes from deterministic computation.
- **Variable governance.** **No unverified column, even as a query term ---
  "query-only use is still semantic use."** Every semantic, retrieval, answer
  and comparison slot uses an authorized/verified field; a useful unresolved
  variable first goes through metadata/concept governance.
- **Audit.** C/G/T/S/D judgments are **retained on every candidate for audit,
  not as a gate**; unmatched dimensions recorded explicitly; no LLM output alters
  concept-map status, column status or compatibility rules.
- **Status lifecycle:** `llm_candidate → deterministic_pass → human_review →
  accepted`, with side exits `rejected_pre_review`, `needs_second_review`,
  `needs_adjudication`, `rejected_human`, `accepted_after_edit`. A candidate is
  benchmark-valid only at `accepted` or `accepted_after_edit` with the final
  edited QA frozen.
- **Implementation (this package, `work/meeting-2026-10-22`, pre-run):**
  `data/metadata/softqa/candidate_schema_v1.json` (JSON Schema) and
  `src/climrr/softqa.py` (loader, validator, Track C mapper);
  `docs/SOFTQA_REVIEW_PROTOCOL.md`, `data/metadata/softqa/review_form_v1.yaml`,
  `scripts/softqa_review_view.py`; Track C inputs `units_definitions_v1.json`,
  `qa_types_v1.json`, `trackc_candidates_v1.json`; the agent tracked as
  `scripts/litcollect/softqa_agent.py` (byte-identical, SHA-256 `159e2c5c…397c`;
  scanner word exemption; run-record exemption); all hash-pinned in
  `data/manifest.json`; `docs/BRIDGE_ELIGIBILITY.md` §10.
- **What it does not decide.** No model call is made and no QA generated under
  this entry; no column status, concept-map entry or compatibility rule changes;
  index 117 stays unlabeled. Track D design is pending.
- **Affected files:** `docs/DECISION_LOG.md`,
  `docs/TRACKC_TRACKD_SOFT_QA_GUARDRAILS_RULING.md`, `docs/PROJECT_STATE.md`,
  `docs/BRIDGE_ELIGIBILITY.md`, `docs/SOFTQA_REVIEW_PROTOCOL.md`,
  `scripts/stage_knowledge.py` (`KNOWLEDGE_FILES`), `data/manifest.json`,
  `CLAUDE.md` (run-record exemption list).
- **Addendum (COORDINATOR, 2026-10-27, before the Track C run; on `12145e0`).**
  Decisions on the items the pre-run report (field 9) put to the COORDINATOR:
  1. **Term location anywhere in the paper is accepted as a pre-check.** The
     agent's paper-wide, first-occurrence location of concept and place terms
     stands as the deterministic check; whether the occurrence is semantically
     adequate (e.g. `stephens` as a surname, bare `FWI` as another index) is the
     reviewer's judgment.
  2. **P-CELL-1 and P-COUNTY-1 candidates may be proposed and reviewed but cannot
     reach `accepted` (or `accepted_after_edit`) until the FWI column meanings
     are owner-confirmed.** Their `wildfire_summer_*` columns are
     `inferred_candidate` (IC-006, IC-008, IC-010); the question goes to the
     mentor as the first item in `docs/MENTOR_BRIEF.md`. P-STATE-1 (verified
     heat-index columns), F-FWI and F-HEAT are not affected by this rule.
  3. **The Polaris invocation in `src/climrr/softqa.py`'s docstring is fine**;
     the agent stays byte-identical.
  4. **P-STATE-1's definition names its metric**: "number of summer days with
     daily maximum heat index above 105 °F" --- the threshold is the metric's
     name, so it is allowed; still no computed value and no direction.
     `units_definitions_v1.json` re-pinned (`61e4c7fe…7c82` → `0cf496a1…282e`);
     the no-digits test allows that threshold string only.

  Affected files: `data/metadata/softqa/units_definitions_v1.json`,
  `data/manifest.json` (entry and amendment), `tests/test_softqa.py`,
  `docs/BRIDGE_ELIGIBILITY.md` §10, `docs/MENTOR_BRIEF.md`,
  `docs/PROJECT_STATE.md`, `reports/milestones/TRACKC_SOFTQA_REPORT.md`.

## D-034 --- Track D v1 design: owner decisions on state geography and heat-index metrics

- **Date:** 2026-10-28.
- **Status:** **decided (owner), with one conflict escalated to the COORDINATOR.**
- **Owner:** Kaiyuan Liao, asked by the EXECUTOR during the Track D v1 work
  package (D-031, D-033) before any template was filled.
- **Context.** The work package's Phase C says an answer is `not_computable` when
  a slot is only `inferred_candidate`. `State` (index 3) is `inferred_candidate`
  (IC-012), as is `NAME` (IC-011); only `Crossmodel` is verified. Read literally,
  the rule blocks every state-level answer, P-STATE-1 included, yet the package
  also asks for state-level enumeration and a P-STATE-1 reproduction. The
  `heat_index` family is realized by four verified threshold metrics
  (Day95 / 105 / 115 / 125; historical, mid-century RCP8.5 and end-century RCP8.5);
  the package names none.
- **Decision.**
  1. **State (and county) locations are computed and tagged provisional.** The
     location slot carries `inferred_candidate (IC-012)` (state) or `our_reading`
     (county, IC-011 + IC-012, A-G1 / A-G3); the answer carries
     `provisional: true` with the reason, as P-STATE-1 already does. The **concept**
     gate is unchanged: a concept column that is not `verified_from_dictionary` or
     `owner_confirmed` blocks the answer (`blocked_inferred_columns`) --- so every
     FWI question is blocked (IC-006..IC-010).
  2. **All four heat-index thresholds are enumerated.** Each is a verified column
     set; the threshold is named in the question text as the metric's name (D-033
     addendum, item 4) and is never a retrieval term. The metric-level concept-map
     entry `heatindex_days_above_105F` stays `proposed`.
- **Escalated.** Decision 1 departs from the literal Phase-C rule and from D-033's
  "no unverified column, even as a query term" as applied to a geography column
  (a state label is a query term under RT-1). Put to the COORDINATOR in
  `reports/milestones/TRACKD_TEMPLATES_REPORT.md` field 9.
- **Derivation rules recorded** (in `data/metadata/templates/slots_v1.yaml`):
  DR-TD-001 baseline value, DR-TD-002 future value, DR-TD-003 absolute change and
  DR-TD-005 direction reuse the prototype arithmetic (`src/climrr/phenomenon.py`);
  **new:** DR-TD-004 percent change of the aggregate (zero denominator →
  `not_computable`; never a mean of per-cell percent changes), DR-TD-006 signed
  comparison, DR-TD-007 extremum over states (ties listed).
- **Alternatives considered.** Block all state answers (literal rule) --- leaves
  48 cell/county answers only and makes P-STATE-1 reproducible in audit mode
  only; stop and escalate before building --- set aside by the owner.
- **Consequences.** 3,138 of 3,186 computed answers are provisional. No column
  status, concept-map entry or compatibility rule changes; no QA is accepted.
- **Affected files:** `data/metadata/templates/slots_v1.yaml`,
  `data/metadata/templates/templates_v1.yaml`, `src/climrr/templates.py`,
  `docs/TEMPLATE_QUESTIONS_V1.md`, `docs/PROJECT_STATE.md`,
  `reports/milestones/TRACKD_TEMPLATES_REPORT.md`.

## D-035 --- Benchmark use case: closed-book evaluation

- **Date:** 2026-10-29 (mentor meeting).
- **Status:** **decided.**
- **Owner:** **the mentor**, relayed by Kaiyuan Liao (owner-relayed, Kaiyuan's
  words; `docs/MENTOR_BRIEF.md`, meeting log 2026-10-29).
- **Mentor's use case, as relayed:** the benchmark question is given directly to
  an LLM; the model answers from what it already knows; it receives **no table
  and no papers**. Questions tied to "this paper" or "this table" are therefore
  meaningless; general patterns are to be extracted from both sources and built
  into open-ended QA.
- **Decision.** Closed-book evaluation: the model under test receives only the
  question. Questions must be answerable from general climate-science knowledge;
  they never name the table, a cell, a paper, or "according to …". The two
  sources supply the **answer key and its provenance**, not the question's
  subject.
- **Rationale.** The mentor's stated use case.
- **Alternatives considered.** Open-book (table and/or passage supplied with the
  question) --- not the mentor's use case.
- **Consequences.** Every question form that names a source or a cell is out of
  scope as question content (D-036, D-039). No QA is generated here.
- **Affected files:** `docs/DECISION_LOG.md`, `docs/MENTOR_BRIEF.md`,
  `docs/BENCHMARK_REDESIGN_2026-10-29.md`, `docs/PROJECT_STATE.md`.

## D-036 --- Pivot to pattern-level open-ended QA

- **Date:** 2026-10-29.
- **Status:** **decided.**
- **Owner:** **mentor direction**, relayed by Kaiyuan Liao.
- **Context.** The four soft-QA examples shown 2026-10-28 were judged by the
  mentor "not the type of question we want to build": all too specific to
  concrete numbers and details of the table and the papers.
- **Decision.**
  - Items are built from **general patterns**.
  - **Table side:** patterns derived deterministically at state / multi-state /
    climate-region level (direction, magnitude class, seasonal and regional
    contrasts, ranking, scenario and horizon), with column / row / rule
    provenance.
  - **Literature side:** statements (mechanisms, drivers, consensus, caveats)
    extracted semantically and **aggregated across papers** --- a statement
    supported by one paper is a citation, not a pattern --- with paper id +
    verbatim span provenance.
  - **Division of labour:** semantic understanding (LLM agents) does extraction
    and synthesis; deterministic code guarantees that every table-side fact in
    an answer key is exactly what the table shows; human review (Kaiyuan, then
    the mentor) decides acceptance.
  - **Claim-level compatibility (C/G/T/S/D) is retired as a gate** and kept only
    as audit metadata where a literature statement is tied to a specific table
    pattern (`docs/BRIDGE_ELIGIBILITY.md` §11).
  - The four 2026-10-28 examples are recorded as
    `rejected_by_mentor: too specific`. *Their candidate ids were not supplied
    with the work package; they are recorded as a set until named.*
  - **Ids attached (pilot P1, 2026-10-29, COORDINATOR):** `C-247866001-01`;
    `C-199098498-02` (with -01 / -03); `C-226260658-01`; `C-53050065-03`. As
    given. **Not all are in `softqa_run1`:** run 1 holds `C-247866001-01`,
    `C-199098498-01`, `C-199098498-02`, `C-226260658-01` and `C-53050065-01`
    only --- paper 199098498 has two candidates and paper 53050065 one, so
    `C-199098498-03` and `C-53050065-03` do not exist there. Flagged to the
    COORDINATOR; no id was substituted.
- **Rationale.** Follows from D-035: a closed-book model cannot answer
  cell-specific or paper-specific questions.
- **Alternatives considered.** Continue cell/claim-level soft QA (Tracks C, D as
  run) --- rejected by the mentor.
- **Consequences.** Design in `docs/BENCHMARK_REDESIGN_2026-10-29.md`. No column
  status, concept-map entry or governed family changes. No QA generated.
- **Affected files:** `docs/DECISION_LOG.md`, `docs/MENTOR_BRIEF.md`,
  `docs/BENCHMARK_REDESIGN_2026-10-29.md`, `docs/BRIDGE_ELIGIBILITY.md` §11,
  `docs/PROJECT_STATE.md`.

## D-037 --- Item schema adopts the ENSURE use-case fields

- **Date:** 2026-10-29.
- **Status:** **decided.**
- **Owner:** Kaiyuan Liao and the COORDINATOR, on the mentor-supplied sheet
  (D-040).
- **Decision.** Each benchmark item carries:
  `use_case` (the hazard-projection ladder, D-038); `prompt` (open-ended, no
  source named); `reasoning_modalities` (`Hazard` / `Text` / `Hazard + Text`);
  `key_relationships`; `evidence_needed`; `capability_tested`;
  `desired_output_characteristics`; `reference_answer` (the sheet's
  "illustrative output": table pattern + literature mechanism in plain
  language); `rubric` (required elements with weights: direction, magnitude
  class, region, mechanism, scenario/horizon handling, no-overclaim);
  `guardrails` (item-specific, e.g. "RCP8.5 is one high-emissions scenario";
  "modeled baseline, not observation"; "FWI is fire weather danger, not fire
  occurrence"); `provenance` (table: columns, row-selection rule, derivation
  rule id, computed values; literature: paper ids, SHA-256, spans, aggregation
  count); `review` (the D-033 lifecycle reused:
  `llm_candidate → deterministic_pass → human_review → accepted`, with
  `rejected_*` exits).
- **Owner defaults stated 2026-10-29 (Kaiyuan):** answers are free text graded
  against a reference, not multiple choice; scenario names may appear if the
  relationship is kept correct ("RCP8.5 is one case of a high-emissions
  scenario"); no QA quota --- generate, sample representatives for human review,
  design filters from feedback.
- **Not mapped.** The sheet's column *What ENSURE Is Doing* has no D-037 field;
  flagged in the design document §6, not added.
- **Rationale.** Aligns the benchmark item with the mentor's ENSURE use-case
  format.
- **Alternatives considered.** Keep `candidate_schema_v1.json` as the item
  record --- it is a claim-level soft-link record, not a closed-book item.
- **Consequences.** A machine schema for D-037 is a later package; none is
  written here. Worked illustrative item in the design document §2.1.
- **Affected files:** `docs/DECISION_LOG.md`,
  `docs/BENCHMARK_REDESIGN_2026-10-29.md`.

## D-038 --- Hazard-projection use-case ladder v1

- **Date:** 2026-10-29.
- **Status:** **proposed** (COORDINATOR proposal, for mentor confirmation).
- **Owner:** the COORDINATOR; confirmation by the mentor.
- **Proposal.**
  1. Hazard pattern identification (Hazard);
  2. Hazard mechanism (Text);
  3. Pattern + mechanism (Hazard + Text);
  4. Regional comparison (Hazard, + Text);
  5. Projection--literature consistency (Hazard + Text);
  6. Compound hazards: fire weather and extreme heat (Hazard + Text);
  7. Scenario and uncertainty (Text; Hazard only where the table has the
     scenario --- for our families only RCP8.5 exists);
  8. Exposure implications (Text; guardrail: hazard ≠ exposure ≠ risk).
- **Rationale.** Mirrors the ENSURE sheet's capability ladder (D-040) for the
  hazard-projection modalities this project has; infrastructure and graph
  modalities are out of scope.
- **Alternatives considered.** Adopt the ten ENSURE use cases as-is --- eight of
  ten need infrastructure or graph data the project does not have.
- **Consequences.** Rung assignment is a field (`use_case`, D-037); nothing is
  generated under this entry.
- **Affected files:** `docs/DECISION_LOG.md`,
  `docs/BENCHMARK_REDESIGN_2026-10-29.md`, `docs/MENTOR_BRIEF.md`.

## D-039 --- Re-purposing of tracks

- **Date:** 2026-10-29.
- **Status:** **decided.**
- **Owner:** Kaiyuan Liao and the COORDINATOR, following D-035/D-036.
- **Decision.**
  - **Track D** machinery (slots, templates, deterministic answers) becomes the
    **table-pattern extractor** at state / region level. Cell-level outputs are
    retained only as provenance, never as question content.
  - **Track C** machinery (agent + pre-check + schema) becomes the
    **literature-statement extractor**: prompt rewritten to extract general
    statements (mechanism / driver / consensus / caveat, with region and
    scenario if stated), each with a verbatim span; statements are then
    clustered across papers.
  - The frozen place-candidate set (243) and LITCORPUS-02 (1,308) remain the
    corpus; the three prototype units remain controls / provenance examples.
  - **Track A-next and Track B are closed as superseded**; their outputs remain
    evidence.
  - **GUIDANCE is notified** that the charter's "bridge" (BLUEPRINT §M5) is
    redefined at pattern level.
- **Rationale.** Re-uses the provenance-carrying machinery already built for the
  new pattern-level pipeline.
- **Alternatives considered.** Rebuild from scratch --- discards tested
  provenance machinery.
- **Consequences.** No code changes under this entry; the rewritten agent prompt
  and pattern extractor are later packages. `docs/BLUEPRINT.md` is not edited
  here; the bridge redefinition is put to GUIDANCE (design document §6).
- **Affected files:** `docs/DECISION_LOG.md`, `docs/PROJECT_STATE.md`,
  `docs/BENCHMARK_REDESIGN_2026-10-29.md`.

## D-040 --- External reference recorded: `ENSURE_Prompt Use Cases_v3.xlsx`

- **Date:** supplied by the mentor 2026-10-29; hash computed 2026-10-29.
- **Status:** **decided.**
- **Owner:** Kaiyuan Liao (record); the mentor supplied the file.
- **Decision.** Record the spreadsheet as an external reference.
  - **File name as received:** `ENSURE_Prompt Use Cases_v3.xlsx` (with a space;
    the work package wrote `ENSURE_Prompt_Use_Cases_v3.xlsx`).
  - **SHA-256:**
    `d3471bfc19294c1872b50add2d1f9e3b1c92d3e985a4b2af0c889ee6f754dee2`
    (computed by the EXECUTOR on the Mac, 2026-10-29; 15,420 bytes).
  - **Contents:** one sheet, ten use cases (Infrastructure Identification …
    Resilience Decision Support); use-case names and column headers in
    `docs/REFERENCES.md`.
  - **Taken from it:** the item fields, per D-037; the idea of a capability
    ladder (D-038).
  - **Out of scope:** the infrastructure and graph modalities.
- **Rationale.** The item schema derives from it; the source must be pinned.
- **Alternatives considered.** None.
- **Consequences.** **Nothing from the file is stored in the repository** except
  this record and the `docs/REFERENCES.md` entry.
- **Affected files:** `docs/DECISION_LOG.md`, `docs/REFERENCES.md`.

## D-041 --- Benchmark objective re-anchored: GUIDANCE PASS WITH ACTIONS; pilot authorized

- **Date:** 2026-10-29.
- **Status:** **decided** (GUIDANCE ruling).
- **Owner:** **GUIDANCE**; ruling tracked verbatim as
  [`BENCHMARK_REANCHOR_GUIDANCE_RULING.md`](BENCHMARK_REANCHOR_GUIDANCE_RULING.md)
  (SHA-256 `b72f045376c3859d5858d51b15a04bdc892bd61dc7dd0be940e7b4f46030dc8d`).
- **Gate status:** **PASS WITH ACTIONS --- benchmark objective re-anchored.** The
  mentor direction of 2026-10-22 / 2026-10-29 **supersedes the previous soft-QA
  objective** (D-029; ruling action 1). The validity question is: *can a question
  be answered from general climate-science knowledge, without exposing the table
  or literature, while its reference answer remains fully grounded in
  deterministic table patterns and auditable literature evidence?*
- **The ruling's decision table, verbatim:**

| Question | Ruling |
|---|---|
| Proposed benchmark-valid gate sufficient? | **Yes, with source-independent answerability and evidence-strength additions** |
| Prompt may name the data/papers? | **No** |
| Exact hidden values required for answer? | **Generally no** |
| Table facts deterministic? | **Required** |
| Literature mechanisms provenance-backed? | **Required** |
| Human acceptance? | **Required** |
| Pilot review by Kaiyuan + mentor? | **Yes** |
| Single-source literature statement allowed? | **Yes, if explicitly marked and not framed as consensus** |
| Core mechanism from one ordinary paper? | **Prefer no** |
| One review/synthesis source sufficient for a core mechanism? | **Yes, if clearly a synthesis** |
| NCA climate regions acceptable? | **Yes** |
| State→region map tracked/cited/versioned? | **Required** |
| Ad hoc region membership allowed? | **No** |
| Additional schema guardrails? | **Yes — answerability, evidence strength, scope, grading tolerance, leakage, robustness** |
| Relative terciles allowed? | **Yes, as disclosed relative descriptors** |
| Treat “large” as absolute threshold? | **No** |
| Store underlying value/range alongside tercile? | **Required** |
| Use tercile as sole correctness target? | **No** |
| ~10-item pilot now? | **Authorized** |
| QA generation generally unrestricted? | **No — pilot only under this gate** |

- **The six validity conditions** (all required; ruling §1):
  - **A. Source-independent prompt** --- names no table, no paper, no hidden
    row/column identifier, no obscure exact value; reasonably answerable from
    general climate-science knowledge; `source_independent_answerability`
    `yes | borderline | no`, only `yes` valid.
  - **B. Deterministic table-side reference facts** --- approved columns,
    explicit aggregation rule, recorded rows/states/regions, period, scenario,
    season, statistic, computed value/range/rank, code/rule version; no LLM
    inference creates a table fact.
  - **C. Provenance-backed literature statements** --- paper ids, hashes, exact
    passages, extracted statement, evidence-strength designation.
  - **D. Explicit evidence strength** --- `multi_source_supported`,
    `review_supported`, `single_source_supported` (and caveat), never presented
    with equal epistemic strength.
  - **E. Reference-answer decomposition** --- `table_pattern`,
    `literature_interpretation`, integrated answer stored separately; a table
    pattern is not a mechanism.
  - **F. Human acceptance** --- Kaiyuan review, mentor review, final frozen
    prompt / reference / rubric; mentor acceptance required for every pilot item.
- **Standing rules.**
  - **Single-source statements:** core mechanism / consensus claims need ≥ 2
    independent sources or one explicit review/synthesis; single-source
    statements only when labeled `single_source_supported` and conservatively
    framed, never as consensus. Two papers citing the same study are not
    automatically independent.
  - **Regions:** one cited, version-pinned scheme --- NCA regions --- with a
    tracked deterministic state → region map (`region_scheme_id`,
    `region_scheme_name`, `region_scheme_version`, `source_citation`,
    `state_to_region_map`, `map_sha256`), fixed before inspecting outcomes;
    membership never hand-edited; other state sets are `multi_state_set`, never
    "climate regions".
  - **Terciles:** relative terciles are a disclosed relative descriptor among
    U.S. states under the same family / season / horizon / scenario --- never an
    absolute threshold, never the sole answer key; direction, value/range and
    relative class stored separately; not used for a small population, many
    ties, a degenerate distribution, weighting-sensitive grouping, or missing
    states that move the cut points.
  - C/G/T/S/D is kept as audit metadata only, never the validity gate.
- **Pilot:** a ~10-item pilot is **authorized** under this gate; QA generation is
  otherwise not unrestricted.
- **Field mapping (this package):** the ENSURE sheet column *What ENSURE Is Doing*
  (D-040) maps to item field **`system_task`** (resolves design §6 item 10).
- **Consequences (pilot P1, this package):** item schema v2
  (`data/metadata/benchmark/item_schema_v2.json`) and validator
  (`src/climrr/benchmark_items.py`); NCA5 map
  (`data/metadata/geography/nca_regions_v1.yaml`, pinned; **source verification
  pending Kaiyuan** --- the NCA5 site did not resolve from the EXECUTOR's
  machine); deterministic table-pattern extractor
  (`scripts/extract_table_patterns.py`, rules DR-PT-001..008); literature-statement
  agent (`scripts/litcollect/litstatement_agent.py`, not run). No item generated,
  no model call; no column status, concept-map entry or compatibility rule
  changed. Report `reports/milestones/PILOT_BENCHMARK_REPORT.md`.
- **Affected files:** `docs/DECISION_LOG.md`,
  `docs/BENCHMARK_REANCHOR_GUIDANCE_RULING.md`, `scripts/stage_knowledge.py`,
  `docs/BENCHMARK_REDESIGN_2026-10-29.md`, `docs/PROJECT_STATE.md`.

## D-042 --- Per-cell percent-change columns are not averaged in table patterns

- **Date:** 2026-10-29.
- **Status:** **decided** (owner); **for COORDINATOR / GUIDANCE confirmation.**
- **Owner:** Kaiyuan Liao, on the EXECUTOR's escalation during pilot P1.
- **Context.** The pilot P1 work package asked for state / NCA-region aggregates
  as a cell mean, including the verified FWI percent-change columns 180--202
  (Pmid / Pend, four seasons). The M1-WP3b GUIDANCE ruling (evidence check 3)
  says: "Do not average identifiers, categorical labels, percentages, or
  quantities for which a mean is not scientifically interpretable." Track D v1
  excluded these columns for the same reason.
- **Decision.** For the per-cell percent-change columns, **no central value** is
  computed at state or region level (DR-PT-006): the pattern is the cells' sign
  counts, the majority direction and the min--max over cells. Hence no rank, no
  tercile and no largest-change season for them; each skip is recorded with its
  reason. The heat-index and FWI-summer-value `percent_change` is unaffected: it
  is DR-TD-004, a ratio of mean change to mean baseline, not a mean of
  percentages.
- **Alternatives considered.** A cell median as central value (a new rule; bends
  the ruling's intent); the cell mean as the work package wrote (would override
  M1-WP3b without GUIDANCE).
- **Affected files:** `src/climrr/table_patterns.py`, `docs/TABLE_PATTERNS_V1.md`,
  `reports/milestones/PILOT_BENCHMARK_REPORT.md`.

