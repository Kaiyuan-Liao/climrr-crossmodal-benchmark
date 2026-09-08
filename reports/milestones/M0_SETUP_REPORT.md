# M0 setup report

## 1. Milestone ID and title

**M0 --- Reproducible project foundation.** Work package M0-WP1.

## 2. Date and author

2026-09-08. EXECUTOR (Claude Code, local authoring clone), for Kaiyuan Liao.

Revised the same day after the Sophia evidence returned: sections 5, 9, 10 and
14 now carry that evidence, and no field remains PENDING.

## 3. Objective

Stand up a repository that a future session with no memory of this one can pick
up and reproduce: fixed structure, persistent documentation, pinned
environment, immutable raw data with recorded checksums, a run-record
mechanism, a smoke test, and a verified local/Sophia sync path.

## 4. Scope boundaries

Explicitly **not** done in M0, and the milestone that owns each:

- Interpretation of any column --- **M1**. `docs/DATA_NOTES.md` records the 275
  column names verbatim with no meaning attached.
- Aggregation or phenomenon profiles --- **M2**.
- Literature ingestion or claim extraction --- **M3**. No literature-corpus
  folder was created; `literature/` is gitignored.
- Embeddings, matching, bridging --- **M4**.
- QA construction --- **M5**.

Contact with the CSV was limited to: copy, hash, count rows and columns, list
column names, confirm it opens read-only. Nothing else.

## 5. Inputs

| Input | Value |
| --- | --- |
| Bootstrap commit | `58cb36a` (README + .gitignore), already pushed |
| Source CSV | ClimRR FullData export, provided by Kaiyuan Liao; 296,407,423 bytes |
| Source data dictionary | `ClimRR Metadata and Data Dictionary.pdf`; 667,097 bytes |
| Decisions in force | D-002, D-003, D-004, D-005 (decided); D-001 (superseded by D-005) |
| Sophia pre-check | git 2.52.0; **git-lfs NOT available**; `ssh -T git@github.com` authenticates as Kaiyuan-Liao |
| Sophia evidence | Returned 2026-09-08 by Kaiyuan; run at commit `586f5fd` on `sophia-login-02` |

### Environments (both recorded, D-004)

| | Local (authoring) | Sophia (execution) |
| --- | --- | --- |
| Kind | conda env `climrr` | venv `.venv-sophia` over the ALCF conda base module |
| Python | **3.11.16** | **3.13.13** |
| Platform | macOS-15.3-arm64 | Linux-5.14.0-611.54.1.el9_7.x86_64, glibc 2.34 |
| `pip freeze` SHA-256 | `03f80e726bdca4a3b061fc444d8d7b4282c114886be48f40b05baef708b6e470` | `92a14aed5911b8f1d85b13d397e22328f2546379e17d941c15ef7a398aac13ac` |
| Dependency source | `requirements.txt` | `requirements.txt` (same file) |

**Known limitation, not a blocker: the two environments run different Python
minor versions (3.11 vs 3.13), and their `pip freeze` fingerprints therefore
differ.** This is a consequence of D-004 as designed --- the Sophia venv is
built with `--system-site-packages` over whatever the ALCF base module provides,
which is deliberate (it inherits the site's tuned builds) and not pinned. It
does not affect the M0 result: every M0 check is a checksum, a row count, or a
file read, and all of them produced identical values on both hosts. It becomes
worth revisiting only when numerical output enters the picture --- from M2
onward --- at which point pinning (deferred in D-004) should be reconsidered.

## 6. Method

1. Extended the existing repository in place on `main` (no re-init), keeping
   and extending `README.md` and `.gitignore`.
2. Created the blueprint directory structure and the documentation set.
3. Hashed the source CSV and PDF **before** copying; copied both into
   `data/`; re-hashed the copies and compared.
4. Streamed the CSV once with Python's `csv` reader (`utf-8-sig`) to count data
   rows and columns and to transcribe the header. No value was parsed, typed,
   or coerced; no column was renamed, grouped, or filtered.
5. Wrote `data/manifest.json` (source of truth) and its Markdown mirror.
6. Implemented `src/climrr/` (paths, checksums, run records), the smoke test,
   and the secrets/paths scanner; wrote 31 unit tests against a synthetic
   three-row fixture.
7. Wrote the Sophia bootstrap and pinned-pull scripts and the runbook.
8. Committed in five logical commits, running `pytest` and the secrets scan
   before each.

## 7. Outputs and deliverables

| Path | What |
| --- | --- |
| `README.md`, `CLAUDE.md` | Entry point; operating rules and role boundaries |
| `.gitignore`, `.gitattributes` | Commit prohibitions; `*.csv`/`*.pdf` marked binary (`-text`) |
| `requirements.txt`, `pyproject.toml` | Environment (D-004) |
| `config/project.yaml` | Project constants, no absolute paths |
| `config/local_paths.example.yaml` | Placeholder-only template (`<LOCAL_REPO_ROOT>` etc.) |
| `data/README.md`, `data/MANIFEST.md`, `data/manifest.json` | Immutability policy and manifest |
| `data/raw/README.md` | How the untracked CSV is obtained and verified (D-005) |
| `data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf` | Authoritative metadata (D-002) |
| `data/raw/FullData.csv` | Present and hash-verified locally; **untracked by design** (D-005) |
| `docs/PROJECT_PLAN.md` | M0--M5, gate criteria verbatim; M0 marked active |
| `docs/PROJECT_STATE.md` | One-screen state |
| `docs/DECISION_LOG.md` | D-001 .. D-005 |
| `docs/DATA_NOTES.md` | Three header sections + 275-name inventory, no interpretation |
| `docs/REPORT_TEMPLATE.md` | The 15 report fields |
| `docs/SOPHIA_RUNBOOK.md` | Step-by-step procedure for Kaiyuan |
| `src/climrr/{paths,checksums,runrecord}.py` | Support code |
| `scripts/smoke_test.py` | Read-only verification + run record |
| `scripts/verify_no_secrets_or_paths.py` | Pre-commit scan |
| `scripts/sophia_bootstrap.sh`, `scripts/sophia_pull_pinned.sh` | Sophia execution |
| `tests/` | 31 unit tests |
| `reports/runs/20260908T184521Z_local_smoke_test.{json,md}` | Local run record |

## 8. Evidence

### Source vs. copied hash comparison

```
SOURCE  e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e  FullData.csv
COPY    e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e  data/raw/FullData.csv
        296407423 bytes, both

SOURCE  b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db  ClimRR Metadata and Data Dictionary.pdf
COPY    b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db  data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf
        667097 bytes, both
```

**Identical.** The source was hashed before the copy and the copy re-hashed
after; the CSV was hashed a third time by the smoke test, with the same result.

### Row and column counts

```
rows 62834
cols 275
first column : OID_
last column  : Shape_STLe
```

**Matches the blueprint's stated 62,834 x 275 exactly.** No escalation
condition triggered on counts.

Incidental encoding fact (not an interpretation): the export is UTF-8 with a
byte-order mark preceding the first header name. The BOM is part of the hashed
bytes; it is stripped at read time via `utf-8-sig` and never on disk.

### `git ls-files` summary

40 tracked files: 4 root (README, CLAUDE.md, requirements.txt, pyproject.toml)
+ 2 dotfiles, 2 `config/`, 5 `data/` text + 1 PDF, 6 `docs/`, 4 `src/climrr/`,
4 `scripts/`, 5 `tests/`, 7 `.gitkeep`. **`data/raw/FullData.csv` is not among
them, by design** --- D-005; `data/raw/*.csv` is gitignored.

### Large-blob check --- the CSV never entered history

```
$ git rev-list --objects --all | git cat-file --batch-check='%(objectsize) %(rest)' | sort -n | tail -5
5527 CLAUDE.md
8229 docs/DECISION_LOG.md
11461 docs/DATA_NOTES.md
13379 reports/milestones/M0_SETUP_REPORT.md
667097 data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf

$ git log --all --oneline -- data/raw/FullData.csv
(no output -- the file appears in no commit)
```

The largest object in the entire repository is the 667 KiB data-dictionary PDF,
which is tracked deliberately (D-002). No history rewrite was necessary,
because the CSV commit was withheld rather than made and then removed.

### Repository size, before and after `git gc --prune=now`

```
BEFORE   count: 66   size: 844.00 KiB   in-pack: 0   packs: 0   size-pack: 0 bytes
AFTER    count: 0    size: 0 bytes      in-pack: 66  packs: 1   size-pack: 629.45 KiB
         .git directory: 748K
```

### LFS decision and evidence

**Not using Git LFS**, and not ordinary Git either --- **D-005**, which
supersedes D-001. Two independent constraints:

1. git-lfs is not available on Sophia (confirmed by the pre-check), so an LFS
   pointer would clone as a text stub and the execution clone could not
   reproduce the SHA-256.
2. The file is 296,407,423 bytes; GitHub hard-rejects any single file over
   104,857,600 bytes on push, so ordinary Git was never viable either.

The CSV is therefore untracked and transferred out of band by `scp`, pinned by
its SHA-256 in `data/manifest.json`. No `.gitattributes` `filter=lfs` entry
exists. `*.csv` remains marked `-text` (binary) so that any CSV which ever does
enter the repository cannot be line-ending-normalised.

### Missing-data behaviour (verified, not assumed)

Because the bytes no longer travel with the commit, a silent skip would let a
bare clone report green while verifying nothing. Verified by temporarily
renaming the file:

```
missing, no env var                  -> FAILED tests/test_manifest.py::test_raw_csv_matches_manifest_hash
missing, CLIMRR_ALLOW_MISSING_RAW=1  -> 1 skipped
missing, scripts/smoke_test.py       -> FAIL: raw data file not found (exit code 2)
file restored, scripts/smoke_test.py -> PASS
```

### Secrets-scan output

```
Scanned 40 tracked text file(s); 0 hit(s).
PASS: no absolute paths or credential patterns in tracked files.
```

Run before every commit; zero hits every time.

### `pytest` output

```
...............................                                          [100%]
31 passed in 1.28s
```

### Smoke-test output (local)

```
Reading (read-only): data/raw/FullData.csv
  sha256       : e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e
  bytes        : 296407423
  data rows    : 62834
  columns      : 275
  [OK  ] sha256 / bytes / row_count / column_count  -- all match manifest
PASS
```

## 9. Verification and checks

| Check | Result |
| --- | --- |
| `pytest` (local) | **PASS** --- 34 passed |
| `pytest` (Sophia) | **PASS** --- 31 passed at commit `586f5fd` |
| `scripts/verify_no_secrets_or_paths.py` | **PASS** --- 0 hits |
| `scripts/smoke_test.py` (local) | **PASS** --- all four manifest fields match |
| Source-to-copy byte identity | **PASS** --- hashes identical |
| Row / column counts vs. blueprint | **PASS** --- 62,834 x 275 |
| CSV blob absent from all Git history | **PASS** --- appears in no commit; largest object is the 667 KiB PDF |
| Missing-data behaviour fails loudly | **PASS** --- verified by renaming the file |
| `scripts/smoke_test.py` (Sophia) | **PASS** --- all four manifest fields match on `sophia-login-02` |
| Sophia byte identity | **PASS** --- `e87ac2cd...3bf43e`, 296,407,423 bytes, identical to local and to source |
| Sophia clean working tree | **PASS** --- `git status --porcelain --untracked-files=no` empty |
| Sophia push URL disabled | **PASS** --- `DISABLED` |

## 10. Run records

- `reports/runs/20260908T184521Z_local_smoke_test.{json,md}` --- first local run
- `reports/runs/20260908T185749Z_local_smoke_test.{json,md}` --- re-run after
  the D-005 changes, confirming the file was restored intact after the
  missing-data behaviour test

- `reports/runs/20260908T191426Z_sophia_smoke_test.{json,md}` --- **the Sophia
  evidence run.** Committed verbatim; not edited.

The two local records show `git_dirty: true` because the report and the run
records themselves were still uncommitted when the smoke test ran. The data
hash recorded in each is identical to the manifest and to the source.

### The Sophia record's `git_dirty: true`

The Sophia record also reads `"git_dirty": true`, on a pinned detached-HEAD
checkout that had no tracked modifications. The cause was an **untracked stray
`.log` file** in the working tree, since deleted on Sophia. The record has been
committed **verbatim and unaltered** --- evidence is not edited after the fact
--- so this note is the correction, not a rewrite of the file.

The flag was measuring the wrong thing. `git_dirty()` called
`git status --porcelain`, which reports untracked files as well as tracked
modifications, so any stray log or scratch file beside a checkout made the run
look dirty. The question the field exists to answer is "did the code that ran
differ from the commit?", and an untracked file does not change that answer.

Fixed in `src/climrr/runrecord.py`: `git_dirty()` now passes
`--untracked-files=no` and reports **tracked changes only**, and a new
`untracked_files` integer field counts untracked files separately, so the
information is kept rather than conflated. Both are covered by tests, which
assert the helpers against `git status` directly. Run records written from this
commit onward carry the corrected semantics; the three earlier records do not,
and should be read with that in mind.

### Confirmed Sophia evidence

```
run_id            20260908T191426Z_sophia_smoke_test
git_commit        586f5fdefc433bf08a2dff6e7f1427c3c48801fa
hostname          sophia-login-02
location          sophia
python_version    3.13.13
pip_freeze_sha256 92a14aed5911b8f1d85b13d397e22328f2546379e17d941c15ef7a398aac13ac
data_sha256       e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e
observed_bytes    296407423
observed_row_count    62834
observed_column_count 275
manifest_checks   sha256=ok; bytes=ok; row_count=ok; column_count=ok
passed            true
```

Plus, from the bootstrap output: `pytest` **31 passed**; smoke test **PASS**;
push URL **`DISABLED`**; `git status --porcelain --untracked-files=no` **empty**.

The decisive line is `data_sha256`. The same 64 hex characters were produced by
three independent computations --- on the source file before copying, on the
repository copy locally, and on the file after an `scp` to a different
architecture and operating system. Under D-005 the bytes no longer travel with
the commit, so this is precisely the check that replaces that guarantee, and it
holds.

## 11. Decisions made or invoked

| ID | Subject | Status |
| --- | --- | --- |
| D-001 | CSV storage: ordinary Git, single immutable commit, no LFS | **superseded by D-005** (the no-LFS rationale stands) |
| D-002 | Track the data dictionary PDF as authoritative metadata | **decided** --- approved by Kaiyuan 2026-09-08 |
| D-003 | Single-writer sync; Sophia pull-only with push URL disabled | decided |
| D-004 | `requirements.txt` as single source of truth; conda local, venv on Sophia | decided |
| D-005 | CSV is untracked, transferred out of band, pinned by SHA-256 | **decided** --- COORDINATOR, approved by Kaiyuan |

## 12. Deviations from the work package

1. **The CSV is not committed (Phase C.3, Phase E.1); storage policy changed
   under D-005.** The work package instructs committing
   `data/raw/FullData.csv` as an ordinary Git object. The file is
   296,407,423 bytes (~282.7 MiB); GitHub hard-rejects any single file over
   104,857,600 bytes on push. The package names "the push of the CSV commit to
   GitHub fails or is rejected" as a stop-and-escalate condition; it was
   detected *before* the push rather than after, and the commit was withheld
   rather than made and then removed --- so no history rewrite was needed and
   the blob never entered any commit (evidence in section 8). The COORDINATOR,
   with Kaiyuan's approval, then decided **D-005**: the CSV is untracked,
   transferred out of band by `scp`, and pinned by its SHA-256 in
   `data/manifest.json`. D-005 supersedes D-001.

2. **File-size discrepancy against the blueprint.** The blueprint stated the
   CSV was **~48 MB**. The actual file is **296,407,423 bytes (~282.7 MiB)**,
   roughly **6x larger**. This is the discrepancy that made D-001 unexecutable.
   The blueprint's *shape* figures, by contrast, were exact --- observed
   **62,834 rows x 275 columns** against a stated 62,834 x 275 --- so the table
   is the expected one and nothing was filtered, dropped, or altered to
   reconcile the size. Whether the 48 MB figure referred to a different or
   compressed export is an open question for Kaiyuan (section 13).

3. **Missing-data handling is fail-by-default, not skip-by-default.** Since the
   CSV is no longer carried by the commit, a clone can legitimately lack it ---
   but a silent skip would let a bare clone report a green suite while
   verifying nothing. `tests/test_manifest.py::test_raw_csv_matches_manifest_hash`
   therefore **fails** when the file is absent, and skips only when the
   operator sets `CLIMRR_ALLOW_MISSING_RAW=1` deliberately.
   `scripts/smoke_test.py` exits non-zero. Both behaviours were verified by
   temporarily renaming the file (evidence in section 8).

4. **The secrets scanner exempts itself from its own scan.** It necessarily
   contains the literal patterns it searches for. The exemption is exactly one
   file, its patterns are assembled from fragments to keep the file's own
   source free of real matches, and the file contains no real path or
   credential.

5. **Two extra test files beyond the three required areas.** `tests/test_paths.py`
   covers the local-path loader; the package asked for checksum, manifest, and
   run-record tests. Additive only.

6. **`.gitattributes` also marks `*.pdf` as binary**, not only `*.csv`. Same
   rationale, applied to the other byte-frozen file.

7. **No push was performed.** The EXECUTOR's push was blocked by the local
   permission layer, and the COORDINATOR then directed that Kaiyuan push
   manually. All commits exist locally and are ready.

8. **Absolute paths in the runbook's `scp` command are placeholders.** The
   COORDINATOR supplied the transfer command with literal machine paths and a
   username. Tracked files may not contain those (they trip
   `scripts/verify_no_secrets_or_paths.py`), so the command is recorded with
   `$LOCAL_REPO_ROOT`, `$CLIMRR_REPO_ROOT`, and `<user>` substituted. The shape
   of the command is unchanged. The literal command is given to Kaiyuan
   directly, outside the repository.

## 13. Open questions and blockers

| Item | Owner | Blocks |
| --- | --- | --- |
| **Python version skew** --- local 3.11.16 vs Sophia 3.13.13, different `pip freeze` fingerprints. Immaterial to M0; revisit pinning when numerical output starts in M2. | COORDINATOR | Nothing in M0 |
| **GUIDANCE confirmation** that D-005's out-of-band policy satisfies gate criteria 1 and 4 in spirit | GUIDANCE | Formal gate sign-off |
| **Push** to `origin main` --- to be done manually by Kaiyuan | Kaiyuan | Nothing further; Sophia has already run |
| Acquisition date of the ClimRR export is unknown | Kaiyuan | Provenance completeness |

**Closed since the last revision:** D-002 (data dictionary is authoritative
metadata, not literature; M1 may cite it as evidence). D-005 (untracked,
out-of-band, hash-pinned). The Sophia evidence gap. The blueprint size
discrepancy --- the ~48 MB figure was a compressed-upload artifact, and the
row and column counts matched exactly.

## 14. Gate criteria assessment

> The repository structure, documentation set, and decision log exist and are
> pushed to the private remote.

**PARTIALLY MET.** All of it exists and is committed. The push has not been
performed: it is Kaiyuan's to run manually (deviation 7).

> `data/raw/FullData.csv` is committed, and its SHA-256 matches the value
> recorded in `data/manifest.json`; the copied file is byte-identical to the
> source.

**MET AS AMENDED BY D-005.** The second and third clauses are satisfied and
evidenced: the copy is byte-identical to the source, and the smoke test
confirms the file matches `data/manifest.json`. The first clause ---
*committed* --- is **superseded**: D-005 replaced "committed to Git" with
"transferred out of band and pinned by SHA-256", because a 283 MiB file cannot
be pushed to GitHub at all. The guarantee the criterion was written to secure
--- that every host provably holds the same bytes --- is preserved, and is now
enforced by a check that fails rather than skips when the file is absent.
**GUIDANCE should confirm that this amendment satisfies the gate's intent.**

> `pytest` passes and the secrets/paths scan reports zero hits.

**MET.** Locally 34 passed, 0 hits; on Sophia 31 passed at commit `586f5fd`.
(The local suite gained three tests covering the `git_dirty` fix made after
that commit.)

> `scripts/smoke_test.py` runs locally and produces a run record.

**MET.** PASS, run record at
`reports/runs/20260908T184521Z_local_smoke_test.json`.

> Sophia can clone the pinned commit, build its environment, and reproduce the
> same SHA-256 for the data file, with a clean working tree.

**MET.** Sophia cloned commit `586f5fd`, built the venv over the ALCF conda
base module, received the CSV by `scp` per runbook step 3, and reproduced
`data_sha256: e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`
with 296,407,423 bytes and 62,834 x 275 --- identical to local and to source.
`pytest` 31 passed; smoke test PASS; push URL `DISABLED`;
`git status --porcelain --untracked-files=no` empty. Evidence:
`reports/runs/20260908T191426Z_sophia_smoke_test.json`.

The word "clone" in this criterion is now satisfied in two parts under D-005 ---
the repository by `git clone`, the data by `scp` --- with the hash check
carrying the guarantee across both.

---

### Proposed gate status: **PASS**

All five criteria are MET (criterion 2 as amended by D-005; criterion 1's push
is Kaiyuan's to execute and is the only mechanical step outstanding). Residual
items, none of which the EXECUTOR considers blocking:

**(a) GUIDANCE to confirm the D-005 out-of-band data policy satisfies criteria
1 and 4 in spirit.** D-005 moved the data pin from the commit SHA to the
manifest SHA-256 because a 283 MiB file cannot be pushed to GitHub at all. The
EXECUTOR's position is that the guarantee both criteria were written to secure
--- that every host provably holds the same bytes --- is preserved and was
demonstrated across two architectures. But the mechanism is not the one the
blueprint specified, so the judgement belongs to GUIDANCE, not to the EXECUTOR.

**(b) Python version skew between environments.** Local 3.11.16, Sophia
3.13.13, with different `pip freeze` fingerprints. A consequence of D-004's
deliberate choice to build the Sophia venv with `--system-site-packages` over
the ALCF base module. Immaterial to M0, where every check is a checksum or a
count and all values matched exactly. Worth revisiting when numerical output
begins in M2, at which point the pinning deferred in D-004 should be
reconsidered.

**(c) The blueprint's ~48 MB figure was a compressed-upload artifact.** The
uncompressed file is 296,407,423 bytes. This is resolved, not open: the row and
column counts matched the blueprint **exactly** (62,834 x 275), confirming the
table is the expected one. Nothing was filtered, dropped, or altered to
reconcile the difference. It is recorded because it is what made D-001
unexecutable and forced D-005.

## 15. Next actions

| Action | Owner |
| --- | --- |
| Push the commits to `origin main` manually | Kaiyuan |
| Review the M0 gate; confirm D-005's out-of-band policy satisfies criteria 1, 2 and 4 in spirit | GUIDANCE |
| Reconsider dependency pinning (deferred in D-004) before numerical output begins | COORDINATOR, at M2 |
| Tag `m0-setup` **only after** GUIDANCE accepts the gate | EXECUTOR |
