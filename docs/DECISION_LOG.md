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
