# M0 setup report

## 1. Milestone ID and title

**M0 --- Reproducible project foundation.** Work package M0-WP1.

## 2. Date and author

2026-09-08. EXECUTOR (Claude Code, local authoring clone), for Kaiyuan Liao.

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
| Local environment | conda env `climrr`, Python 3.11.16 |

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
| `pytest` | **PASS** --- 31 passed |
| `scripts/verify_no_secrets_or_paths.py` | **PASS** --- 0 hits |
| `scripts/smoke_test.py` (local) | **PASS** --- all four manifest fields match |
| Source-to-copy byte identity | **PASS** --- hashes identical |
| Row / column counts vs. blueprint | **PASS** --- 62,834 x 275 |
| CSV blob absent from all Git history | **PASS** --- appears in no commit; largest object is the 667 KiB PDF |
| Missing-data behaviour fails loudly | **PASS** --- verified by renaming the file |
| `scripts/smoke_test.py` (Sophia) | **PENDING --- awaiting Kaiyuan's Sophia run** |
| Sophia clean working tree | **PENDING --- awaiting Kaiyuan's Sophia run** |

## 10. Run records

- `reports/runs/20260908T184521Z_local_smoke_test.{json,md}` --- first local run
- `reports/runs/20260908T185749Z_local_smoke_test.{json,md}` --- re-run after
  the D-005 changes, confirming the file was restored intact after the
  missing-data behaviour test

Both show `git_dirty: true`, because the report and the run records themselves
were still uncommitted when the smoke test ran. The data hash recorded in each
is identical to the manifest and to the source.

Sophia run record: **PENDING --- awaiting Kaiyuan's Sophia run.** Expected
evidence: `reports/runs/<timestamp>_sophia_smoke_test.json` and `.md`, showing
`location: sophia`, `passed: true`, and
`data_sha256: e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`.

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
| **Blueprint size discrepancy** --- the blueprint says ~48 MB, the file is 296,407,423 bytes (~6x). Row and column counts match exactly (62,834 x 275), so the table is the expected one. Did the 48 MB figure refer to a compressed or different export? | Kaiyuan | Provenance completeness; nothing technical |
| **Push** of the six commits to `origin main` --- to be done manually by Kaiyuan | Kaiyuan | Sophia cannot clone until pushed |
| **Sophia evidence** --- transfer the CSV by `scp`, verify the hash, run the bootstrap, return the run records | Kaiyuan | The M0 gate |
| Acquisition date of the ClimRR export is unknown | Kaiyuan | Provenance completeness |

**D-002 is closed** (decided: the data dictionary is authoritative metadata,
not literature; M1 may cite it as evidence). **D-005 is closed** (decided:
untracked, out-of-band, hash-pinned). Neither blocks.

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

**MET.** 31 passed; 0 hits.

> `scripts/smoke_test.py` runs locally and produces a run record.

**MET.** PASS, run record at
`reports/runs/20260908T184521Z_local_smoke_test.json`.

> Sophia can clone the pinned commit, build its environment, and reproduce the
> same SHA-256 for the data file, with a clean working tree.

**PENDING --- awaiting Kaiyuan's Sophia run.** Expected evidence: the Sophia
run record showing `location: sophia`, `passed: true`, and
`data_sha256: e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`;
plus empty `git status --porcelain` output and a push URL of `DISABLED`. Under
D-005 the clone no longer carries the data, so the runbook's `scp` step (step 3)
must precede the bootstrap; `scripts/sophia_bootstrap.sh` exits 3 if the file is
absent and exits 4 on a hash mismatch, printing both hashes.

## 15. Next actions

| Action | Owner |
| --- | --- |
| Push the commits to `origin main` manually | Kaiyuan |
| Resolve the blueprint's ~48 MB vs. 283 MiB size discrepancy | Kaiyuan |
| `scp` the CSV to Sophia and verify `sha256sum` against the manifest (runbook step 3) | Kaiyuan |
| Run the bootstrap on `sophia-login-02` inside `screen -S climrr`; paste back the output and the Sophia run records | Kaiyuan |
| Confirm the D-005 amendment satisfies gate criterion 2's intent | GUIDANCE |
| Fill the two PENDING fields; commit the returned Sophia run records | EXECUTOR |
| Tag `m0-setup` **only after** GUIDANCE accepts the gate | EXECUTOR |
