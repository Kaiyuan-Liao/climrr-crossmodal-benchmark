# M0 setup report

## 1. Milestone ID and title

**M0 --- Reproducible project foundation.** Work package M0-WP1.

Author: EXECUTOR (Claude Code, local authoring clone), for Kaiyuan Liao.
Date: 2026-09-08. Revised the same day after the Sophia evidence returned, and
again to restructure onto the blueprint's 15 report fields and its five M0 gate
criteria.

---

## 2. Objective

Stand up a repository that a future session with no memory of this one can pick
up and reproduce: fixed structure, persistent documentation, pinned
environment, immutable raw data with recorded checksums, a run-record
mechanism, a smoke test, and a verified local/Sophia sync path.

**Explicitly excluded from M0**, with the milestone that owns each:

| Excluded | Owner |
| --- | --- |
| Interpretation of any column | M1 |
| Canonical semantic representation | M2 |
| Table-derived phenomenon discovery and geographic aggregation | M3 |
| Literature ingestion and claim extraction | M4 |
| Semantic bridge discovery and validation, including embeddings and matching | M5 |
| QA construction | **not in current scope** --- deferred until after M5 passes |

Contact with the CSV was limited to: copy, hash, count rows and columns, list
column names, confirm it opens read-only. Nothing else. No literature-corpus
folder was created; `literature/` is gitignored.

---

## 3. Repository commit SHA

| | |
| --- | --- |
| Bootstrap commit (pre-existing) | `58cb36a` |
| **M0-WP1 close commit** | **`685c2b1`** |
| Commit Sophia cloned and verified | `586f5fd` |
| `origin/main` | `586f5fd` (pushed by Kaiyuan; reflog: "update by push") |
| Unpushed local commits | `685c2b1`, `a0dc4db`, `fc12eba`, and this revision |

The EXECUTOR does not push (D-003 single-writer model, plus explicit
instruction). Everything the Sophia evidence depended on is on the remote at
`586f5fd`; the later commits are report and bookkeeping changes.

---

## 4. Data version and checksums

| | `FullData.csv` | `ClimRR_Metadata_and_Data_Dictionary.pdf` |
| --- | --- | --- |
| Path | `data/raw/FullData.csv` | `data/metadata/…` |
| SHA-256 | `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e` | `b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db` |
| Bytes | 296,407,423 | 667,097 |
| Shape | 62,834 data rows x 275 columns | n/a |
| Tracked in Git | **no** (gitignored, D-005) | yes (D-002) |
| Storage policy | out of band by `scp`, pinned by SHA-256 | ordinary Git, immutable |
| Source | ClimRR FullData export, provided by Kaiyuan Liao | same |
| Acquisition date | **unknown** (not guessed) | unknown |
| Interpretation | none assigned; see `docs/DATA_NOTES.md` (M1) | --- |

### Source vs. copy vs. Sophia

```
SOURCE (before copy)   e87ac2cd…3bf43e   296407423   FullData.csv
LOCAL COPY             e87ac2cd…3bf43e   296407423   data/raw/FullData.csv
SOPHIA (after scp)     e87ac2cd…3bf43e   296407423   data/raw/FullData.csv

SOURCE                 b28dff7c…23db     667097      ClimRR Metadata and Data Dictionary.pdf
LOCAL COPY             b28dff7c…23db     667097      data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf
```

Four independent computations of the CSV hash --- source before copying, local
copy, smoke test, and Sophia after transfer to a different architecture and
operating system --- produced the same 64 characters.

**Storage policy (D-005, supersedes D-001).** Not Git LFS: git-lfs is
unavailable on Sophia, where a pointer would clone as a stub. Not ordinary Git
either: 296,407,423 bytes exceeds GitHub's 104,857,600-byte per-file limit. The
file is therefore untracked and pinned by the manifest hash.
`.gitattributes` still marks `*.csv` as `-text` so any CSV that ever does enter
the repository cannot be line-ending-normalised.

---

## 5. Environment and execution location

| | Local (authoring) | Sophia (execution) |
| --- | --- | --- |
| Location label in run records | `local` | `sophia` |
| Host | macOS-15.3-arm64 | `sophia-login-02`, Linux-5.14.0-611.54.1.el9_7.x86_64, glibc 2.34 |
| Kind | conda env `climrr` | venv `.venv-sophia`, `--system-site-packages` over the ALCF conda base module |
| Python | **3.11.16** | **3.13.13** |
| `pip freeze` SHA-256 | `03f80e726bdca4a3b061fc444d8d7b4282c114886be48f40b05baef708b6e470` | `92a14aed5911b8f1d85b13d397e22328f2546379e17d941c15ef7a398aac13ac` |
| Dependency source | `requirements.txt` | `requirements.txt` (same file) |
| Push capability | full | `DISABLED` (D-003) |

Sophia pre-check: git 2.52.0; **git-lfs NOT available**; `ssh -T git@github.com`
authenticates as Kaiyuan-Liao. Login nodes suffice for M0 --- every check is a
checksum or a read; no compute job was needed.

The Python version difference is a known limitation, recorded in field 11.

---

## 6. Work completed

1. Extended the existing repository in place on `main` (no re-init), keeping and
   extending `README.md` and `.gitignore`.
2. Created the blueprint directory structure and the documentation set.
3. Hashed the source CSV and PDF **before** copying; copied both into `data/`;
   re-hashed the copies and compared.
4. Streamed the CSV once with Python's `csv` reader (`utf-8-sig`) to count data
   rows and columns and transcribe the header.
5. Wrote `data/manifest.json` (machine-readable source of truth) and its
   Markdown mirror.
6. Implemented `src/climrr/` (paths, checksums, run records), the smoke test,
   and the secrets/paths scanner; wrote unit tests against a synthetic
   three-row fixture.
7. Wrote the Sophia bootstrap and pinned-pull scripts and the runbook; Kaiyuan
   executed them and returned the evidence.
8. Corrected `git_dirty` semantics after the Sophia record exposed a false
   positive (field 11).
9. Committed in small logical commits, running `pytest` and the secrets scan
   before each.

---

## 7. Deliverables and exact file paths

| Path | What |
| --- | --- |
| `README.md` | Entry point and reading order |
| `CLAUDE.md` | Operating rules, roles, data cautions, commit prohibitions |
| `.gitignore` | Commit prohibitions incl. `data/raw/*.csv`, `literature/` |
| `.gitattributes` | `*.csv`, `*.pdf` marked `-text` (binary) |
| `requirements.txt`, `pyproject.toml` | Environment (D-004) |
| `config/project.yaml` | Project constants, no absolute paths |
| `config/local_paths.example.yaml` | Placeholder-only template |
| `data/README.md` | Immutability and storage policy |
| `data/MANIFEST.md` | Human-readable manifest |
| `data/manifest.json` | Machine-readable manifest (source of truth) |
| `data/raw/README.md` | How the untracked CSV is obtained and verified |
| `data/raw/FullData.csv` | Present, hash-verified, **untracked by design** |
| `data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf` | Authoritative metadata (D-002) |
| `docs/BLUEPRINT.md` | **Project charter** --- authoritative source for milestones, roles, and report structure (placed by Kaiyuan) |
| `docs/PROJECT_PLAN.md` | M0--M5 objectives and gate criteria, verbatim from the blueprint |
| `docs/PROJECT_STATE.md` | One-screen state |
| `docs/DECISION_LOG.md` | D-001 .. D-005 |
| `docs/DATA_NOTES.md` | Three header sections + 275-name inventory |
| `docs/REPORT_TEMPLATE.md` | The 15 report fields |
| `docs/SOPHIA_RUNBOOK.md` | Step-by-step procedure for Kaiyuan |
| `src/climrr/paths.py` | Local path config loader |
| `src/climrr/checksums.py` | Streaming SHA-256 and byte size |
| `src/climrr/runrecord.py` | Run-record writer |
| `scripts/smoke_test.py` | Read-only verification + run record |
| `scripts/verify_no_secrets_or_paths.py` | Pre-commit scan |
| `scripts/sophia_bootstrap.sh` | Sophia clone, venv, data check, tests |
| `scripts/sophia_pull_pinned.sh` | Sophia pinned checkout, refuses if dirty |
| `tests/conftest.py`, `test_checksums.py`, `test_manifest.py`, `test_paths.py`, `test_runrecord.py` | Unit tests |
| `reports/runs/20260908T184521Z_local_smoke_test.{json,md}` | Local run record |
| `reports/runs/20260908T185749Z_local_smoke_test.{json,md}` | Local re-run after D-005 |
| `reports/runs/20260908T191426Z_sophia_smoke_test.{json,md}` | **Sophia evidence**, committed verbatim |
| `reports/milestones/M0_SETUP_REPORT.md` | This report |

---

## 8. Methods and rules that affect scientific meaning

**No rule affecting scientific meaning was applied in M0.**

The only operations performed on the data were: copying the file, computing
SHA-256 and byte size, counting rows and columns, and transcribing the header
row. No column was renamed, grouped, filtered, excluded, reordered,
unit-converted, imputed, or type-coerced; no value was parsed or typed; no
aggregation was performed; no row was dropped. Column names are recorded
verbatim in `docs/DATA_NOTES.md` under a heading stating that no interpretation
is assigned. Interpretation is the M1 objective and requires the tracked data
dictionary as evidence.

Two reading conventions were adopted, neither of which changes meaning:

- The CSV is read with `encoding="utf-8-sig"`. **The file carries a UTF-8
  byte-order mark before the first header name** (`OID_`). The BOM is part of
  the hashed bytes and is stripped **at read time only**, never on disk ---
  otherwise it would be absorbed into the first column's name. This is an
  observation about the file's encoding, not an interpretation of its content.
- Where pandas is used, `dtype=str` is required, so that Census identifiers
  keep their leading zeros. No such read was performed in M0; the rule is
  recorded in `CLAUDE.md` for the milestones that will.

Three cautions are recorded in `CLAUDE.md` and `docs/DATA_NOTES.md` as
constraints on future work. They are prohibitions carried forward, not
interpretations applied here: historical (`*_hist`) fields are modeled
baselines rather than observations; `wildfire*` columns are a Fire Weather
Index and never wildfire occurrence; Census identifiers are strings with
leading zeros.

---

## 9. Results with compact tables or examples

### Shape

| Measure | Blueprint | Observed | Match |
| --- | --- | --- | --- |
| Data rows (header excluded) | 62,834 | **62,834** | yes |
| Columns | 275 | **275** | yes |
| File size | figure in the charter is a compressed-upload artifact, not the file size | **296,407,423 bytes** | n/a --- resolved, see field 12 |

```
first column : OID_
last column  : Shape_STLe
duplicate column names : none
truncated names        : none altered; all recorded verbatim
```

### Column-name inventory

All 275 names transcribed in file order to `docs/DATA_NOTES.md`, ordinal index
plus exact name, under the heading "names only, no interpretation assigned".

### Repository composition

40 tracked files: 4 root, 2 dotfiles, 2 `config/`, 5 `data/` text + 1 PDF,
6 `docs/`, 4 `src/climrr/`, 4 `scripts/`, 5 `tests/`, 7 `.gitkeep`.
`data/raw/FullData.csv` is deliberately absent.

### Large-blob check --- the CSV never entered history

```
$ git rev-list --objects --all | git cat-file --batch-check='%(objectsize) %(rest)' | sort -n | tail -5
5527    CLAUDE.md
8229    docs/DECISION_LOG.md
11461   docs/DATA_NOTES.md
13379   reports/milestones/M0_SETUP_REPORT.md
667097  data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf

$ git log --all --oneline -- data/raw/FullData.csv
(no output -- the file appears in no commit)
```

The largest object in the repository is the 667 KiB data-dictionary PDF,
tracked deliberately under D-002. No history rewrite was needed: the CSV commit
was withheld rather than made and then removed.

### Repository size

```
BEFORE gc   count: 66   size: 844.00 KiB   in-pack: 0    packs: 0   size-pack: 0 bytes
AFTER  gc   count: 0    size: 0 bytes      in-pack: 66   packs: 1   size-pack: 629.45 KiB
            .git directory: 748K
```

### Sophia run record (verbatim extract)

```
run_id                20260908T191426Z_sophia_smoke_test
git_commit            586f5fdefc433bf08a2dff6e7f1427c3c48801fa
hostname              sophia-login-02
location              sophia
python_version        3.13.13
pip_freeze_sha256     92a14aed5911b8f1d85b13d397e22328f2546379e17d941c15ef7a398aac13ac
data_sha256           e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e
observed_bytes        296407423
observed_row_count    62834
observed_column_count 275
manifest_checks       sha256=ok; bytes=ok; row_count=ok; column_count=ok
passed                true
```

Plus, from the bootstrap output: `pytest` **31 passed**; smoke test **PASS**;
push URL **`DISABLED`**; `git status --porcelain --untracked-files=no` **empty**.

---

## 10. Validation performed

| Check | Result |
| --- | --- |
| `pytest` (local) | **PASS** --- 34 passed |
| `pytest` (Sophia) | **PASS** --- 31 passed at `586f5fd` |
| `scripts/verify_no_secrets_or_paths.py` | **PASS** --- 45 tracked text files, 0 hits |
| `scripts/smoke_test.py` (local) | **PASS** --- all four manifest fields match |
| `scripts/smoke_test.py` (Sophia) | **PASS** --- all four manifest fields match |
| Source-to-copy byte identity | **PASS** --- hashes identical |
| Local-to-Sophia byte identity | **PASS** --- hashes identical across architectures |
| Row / column counts vs. blueprint | **PASS** --- 62,834 x 275 |
| CSV blob absent from all Git history | **PASS** |
| Sophia clean working tree | **PASS** --- `--untracked-files=no` empty |
| Sophia push URL disabled | **PASS** --- `DISABLED` |
| Missing-data behaviour fails loudly | **PASS** --- verified by renaming the file |

### Secrets scan

```
Scanned 45 tracked text file(s); 0 hit(s).
PASS: no absolute paths or credential patterns in tracked files.
```

Run before every commit; zero hits every time. Seven patterns are covered:
three absolute-path roots (macOS user, ALCF Eagle, Linux home), two API-key
prefixes (OpenAI-style, GitHub personal access), and two credential-bearing
words. The literal patterns are listed only in the scanner itself, which is
exempt from its own scan --- writing them into this report made the scan fail,
which is the scanner behaving correctly.

### Missing-data behaviour, verified rather than assumed

Because D-005 means the bytes no longer travel with the commit, a silent skip
would let a bare clone report green while verifying nothing. Verified by
temporarily renaming the file:

```
missing, no env var                  -> FAILED tests/test_manifest.py::test_raw_csv_matches_manifest_hash
missing, CLIMRR_ALLOW_MISSING_RAW=1  -> 1 skipped
missing, scripts/smoke_test.py       -> FAIL: raw data file not found (exit 2)
file restored, scripts/smoke_test.py -> PASS
```

`scripts/sophia_bootstrap.sh` exits 3 if the CSV is absent and 4 on a hash
mismatch, printing both hashes.

### Run records backing the above

- `reports/runs/20260908T184521Z_local_smoke_test.{json,md}`
- `reports/runs/20260908T185749Z_local_smoke_test.{json,md}`
- `reports/runs/20260908T191426Z_sophia_smoke_test.{json,md}`

---

## 11. Failures, rejected cases, and known limitations

### Failure found and fixed: `git_dirty` counted untracked files

The Sophia record reads `"git_dirty": true` on a pinned detached-HEAD checkout
with no tracked modifications. The cause was an **untracked stray `.log` file**,
since deleted on Sophia.

The flag was measuring the wrong thing. `git_dirty()` called
`git status --porcelain`, which reports untracked files alongside tracked
modifications, so any stray log or scratch file made a run look dirty. The
question the field exists to answer is "did the code that ran differ from the
commit?", and an untracked file does not change that answer.

Fixed in `src/climrr/runrecord.py`: `git_dirty()` now passes
`--untracked-files=no` and reports tracked changes only; a new
`untracked_files` integer counts untracked files separately, keeping the
information rather than conflating it. Three tests assert both helpers against
`git status` directly.

**The Sophia record was committed verbatim and unaltered** --- evidence is not
edited after the fact. Records written from `685c2b1` onward carry the
corrected semantics; the three earlier records do not, and should be read with
that in mind.

### Rejected approaches

| Rejected | Why |
| --- | --- |
| Git LFS for the CSV | git-lfs unavailable on Sophia; a pointer stub would break byte identity (D-001, upheld by D-005) |
| Ordinary Git commit of the CSV | 296,407,423 bytes exceeds GitHub's 104,857,600-byte per-file limit |
| Splitting the CSV into <100 MiB parts | Keeps bytes pinned to the commit but puts ~283 MiB in history permanently and adds a reassembly step to every read |
| Committing a subset or column-pruned extract | Would mean filtering columns, which M0 forbids. Rejected outright |
| Skipping the manifest test when the CSV is absent | A green suite on a clone that never received the data is worse than a red one |

### Known limitations

1. **Python version skew.** Local 3.11.16 vs Sophia 3.13.13, with different
   `pip freeze` fingerprints. A consequence of D-004's deliberate choice to
   build the Sophia venv with `--system-site-packages` over the ALCF base
   module. Immaterial to M0 --- every check is a checksum or a count, and all
   values matched exactly on both hosts. Material from M2, when numerical
   output begins.
2. **Dependencies are unpinned.** D-004 deferred a lockfile at three
   dependencies; the `pip freeze` fingerprint in each run record is the drift
   detector, not a preventer.
3. **The secrets scanner exempts itself** from its own scan, since it
   necessarily contains the patterns it searches for. Exactly one file; its
   patterns are assembled from fragments so its own source contains no literal
   match; it holds no real path or credential.
4. **Acquisition date of the ClimRR export is unknown** and was not guessed.

---

## 12. Deviations from the approved plan

1. **The CSV is not committed (Phase C.3, Phase E.1); storage policy changed
   under D-005.** The work package instructed committing the CSV as an ordinary
   Git object. At 296,407,423 bytes that push would have been rejected by
   GitHub. The package names a rejected push as a stop-and-escalate condition;
   it was detected *before* the push, and the commit was withheld rather than
   made and removed --- so no history rewrite was needed and the blob never
   entered any commit. The COORDINATOR, with Kaiyuan's approval, then decided
   D-005: untracked, transferred out of band, pinned by SHA-256.

2. **File size differed from the figure recorded in the charter.** The file is
   **296,407,423 bytes**. Resolved: Kaiyuan's explanation is that the charter's
   figure came from a compressed chat upload and never described the file on
   disk. Row and column counts matched exactly, confirming the table is the
   expected one; nothing was filtered or altered to reconcile the difference.

3. **Missing-data handling is fail-by-default, not skip-by-default.** Added
   because D-005 makes an absent CSV a legitimate clone state, and a silent
   skip would hide it. `CLIMRR_ALLOW_MISSING_RAW=1` is the deliberate opt-out.

4. **Two extra test files beyond the three required areas.**
   `tests/test_paths.py` covers the local-path loader; additive only.

5. **`.gitattributes` also marks `*.pdf` as binary**, not only `*.csv`.

6. **No push was performed by the EXECUTOR.** Its push was blocked by the local
   permission layer; the COORDINATOR directed that Kaiyuan push manually, which
   he did (`origin/main` at `586f5fd`).

7. **The runbook's `scp` command uses placeholders.** The COORDINATOR supplied
   it with literal machine paths and a username; tracked files may not contain
   those without failing the secrets scan. The command's shape is unchanged and
   the literal version was given to Kaiyuan outside the repository.

8. **`docs/PROJECT_PLAN.md` did not carry the blueprint's objectives and gate
   criteria.** Phase A.3 required them verbatim, but the blueprint was not
   available to the EXECUTOR at the time, which drafted from the work package's
   summary. Kaiyuan has since placed the charter at `docs/BLUEPRINT.md`, and
   **all six objectives and all six gate-criteria sets were corrected from
   `docs/BLUEPRINT.md` (section 8) and verified byte-identical to it.** The plan
   now states that it must not diverge from the blueprint without a logged
   decision; `CLAUDE.md` carries the same rule.

9. **`docs/REPORT_TEMPLATE.md` did not carry the blueprint's 15 field names**,
   for the same reason. **Corrected from `docs/BLUEPRINT.md` (section 9) and
   verified to match exactly**, and this report restructured onto it.

---

## 13. Open decisions and mentor questions

| Item | Owner | Blocks |
| --- | --- | --- |
| **GUIDANCE to confirm that D-005's out-of-band data policy is an acceptable mechanism** for keeping the raw data pinned. The gate criteria concern byte identity, which is met and demonstrated across two architectures; but the mechanism is not the one the blueprint envisaged, and that judgement is GUIDANCE's, not the EXECUTOR's. | GUIDANCE | Formal gate sign-off |
| **Push** of `685c2b1`, `a0dc4db`, `fc12eba` and this revision. Everything the gate evidence depends on is already on `origin/main` at `586f5fd`. | Kaiyuan | Nothing |
| **Tag `m0-setup`** --- only after GUIDANCE accepts the gate. | EXECUTOR | Nothing |
| **Dependency pinning** (deferred in D-004) should be reconsidered before numerical output begins. | COORDINATOR | Nothing until M2 |
| **Acquisition date** of the ClimRR export is unknown and was not guessed. | Kaiyuan | Provenance completeness |

**Closed:** D-002 (data dictionary is authoritative metadata, not literature ---
approved by Kaiyuan). D-005 (untracked, out-of-band, hash-pinned). The Sophia
evidence gap. The file-size discrepancy.

---

## 14. Proposed gate status

Criteria quoted verbatim from `docs/PROJECT_PLAN.md`.

> **1. the raw CSV is byte-identical locally and on Sophia**

**MET.** `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`,
296,407,423 bytes, on both hosts --- and identical to the source before
copying. Computed four times independently, including once on a different
architecture and operating system after transfer. The criterion concerns bytes;
D-005 changed only how those bytes travel, not whether they are identical.
Evidence: fields 4, 9, 10.

> **2. the repository can be cleanly cloned or pulled in both environments**

**MET.** Sophia cloned `586f5fd` from the remote, checked it out detached, and
reported `git status --porcelain --untracked-files=no` empty. Locally the
working tree is clean. `scripts/sophia_pull_pinned.sh` refuses to check out
over local changes rather than discarding them. Evidence: fields 5, 9, 10.

> **3. no secrets or machine-specific paths are tracked**

**MET.** `scripts/verify_no_secrets_or_paths.py` reports 0 hits across 45
tracked text files, and is run before every commit. Real paths live only in the
gitignored `config/local_paths.yaml`; the tracked template carries
`<PLACEHOLDER>` markers; Sophia's config is generated at run time from
environment variables. Run records store repo-relative paths only. Evidence:
field 10.

> **4. a run can be tied to a precise commit, configuration, environment, and data checksum**

**MET.** Every script calls `write_run_record`, which captures commit SHA,
tracked-dirty flag, untracked count, hostname, location label, Python version,
platform, `pip freeze` SHA-256, config snapshot, data path and data SHA-256,
output path, and pass/fail. The Sophia record ties its result to commit
`586f5fd`, a named host, Python 3.13.13, a specific dependency fingerprint, and
the exact data hash. Evidence: fields 9, 10.

> **5. project state and role instructions are sufficient for a new coding-agent session to resume safely**

**MET --- tested 2026-09-08 by an independent cold session.** Kaiyuan ran the
cold-resume trial this report previously recommended: a fresh session, given
only the repository and no conversational context, correctly identified the
project, the M0 status and pending gate, the escalation rule, all three data
cautions, the prohibition on writing into `data/`, and `data/manifest.json` as
the first file to check. The criterion is therefore satisfied by evidence
rather than by the EXECUTOR's assessment of its own material.

**One finding from the trial, acted on.** The fresh session repeated stale
facts from `docs/PROJECT_STATE.md` --- an unpushed-commit list that no longer
matched the remote, and the M1--M5 gate-criteria gap that
`docs/BLUEPRINT.md` had already closed. It reasoned correctly from the file it
was given; the file was out of date. That is the failure mode this criterion
exists to catch, and it is a sharper result than a clean pass: a resumable
repository depends on the state file being refreshed at the end of every work
package, not merely on its existing. `docs/PROJECT_STATE.md` has been rewritten
to current truth, and refreshing it is already a standing requirement in that
file's own header.

### Proposed gate status: **PASS**

All five criteria are MET, each on evidence rather than assertion --- including
criterion 5, which was the last to rest on self-assessment and has now been
tested by an independent cold session.

**GUIDANCE decision: PASS WITH ACTIONS** (`docs/M0_GUIDANCE_GATE_REVIEW.md`);
closure actions completed in this commit. Reviewed at commit `b87564b`.
Recorded as D-006, with D-007 amending D-004 on dependency pinning.

> **Note --- `docs/M0_GUIDANCE_GATE_REVIEW.md` is not yet in the repository.**
> The citation above is to a file Kaiyuan has still to place. It is therefore
> also absent from field 7, and this report is **not frozen**, because adding
> the deliverable and the freeze line is one edit still outstanding. Listing a
> file that is not there would make this report assert evidence that does not
> exist, which is the failure this project is built to prevent.

---

## 15. Proposed next bounded objective

**M1-WP1 --- reproducible schema and quality profile of `FullData.csv`:** a
machine-readable per-column profile (dtype as read, null count, distinct count,
min/max for numerics, example values; identifiers read as strings; no
interpretation) plus an inventory of metadata questions checked against the
tracked data dictionary.
