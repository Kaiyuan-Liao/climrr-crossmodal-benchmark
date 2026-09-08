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
| Decisions in force | D-001, D-003, D-004 (decided); D-002 (proposed); D-005 (escalated) |
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
| `data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf` | Authoritative metadata (D-002) |
| `data/raw/FullData.csv` | Present and hash-verified locally; **not yet committed** (D-005) |
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

39 tracked files: 4 root (README, CLAUDE.md, requirements.txt, pyproject.toml)
+ 2 dotfiles, 2 `config/`, 4 `data/` text + 1 PDF, 6 `docs/`, 4 `src/climrr/`,
4 `scripts/`, 5 `tests/`, 7 `.gitkeep`. **`data/raw/FullData.csv` is not among
them** --- see D-005.

### LFS decision and evidence

**Not using Git LFS** (D-001). Evidence: the Sophia pre-check confirmed
git-lfs is not available there. An LFS pointer would clone as a text stub, so
the execution clone could not reproduce the SHA-256 and the M0 byte-identity
gate would fail. No `.gitattributes` `filter=lfs` entry exists; `*.csv` is
marked `-text` (binary) so line-ending normalisation can never alter the bytes.

### Secrets-scan output

```
Scanned 37 tracked text file(s); 0 hit(s).
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
| `scripts/smoke_test.py` (Sophia) | **PENDING --- awaiting Kaiyuan's Sophia run** |
| Sophia clean working tree | **PENDING --- awaiting Kaiyuan's Sophia run** |

## 10. Run records

- `reports/runs/20260908T184521Z_local_smoke_test.json`
- `reports/runs/20260908T184521Z_local_smoke_test.md`

The record shows `git_dirty: true` because the report and run record were still
uncommitted when the smoke test ran. The data hash it recorded is identical to
the manifest and to the source.

Sophia run record: **PENDING --- awaiting Kaiyuan's Sophia run.** Expected
evidence: `reports/runs/<timestamp>_sophia_smoke_test.json` and `.md`, showing
`location: sophia`, `passed: true`, and
`data_sha256: e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`.

## 11. Decisions made or invoked

| ID | Subject | Status |
| --- | --- | --- |
| D-001 | CSV storage: ordinary Git, single immutable commit, no LFS | decided (blocked by D-005) |
| D-002 | Track the data dictionary PDF as authoritative metadata | **proposed --- awaiting Kaiyuan** |
| D-003 | Single-writer sync; Sophia pull-only with push URL disabled | decided |
| D-004 | `requirements.txt` as single source of truth; conda local, venv on Sophia | decided |
| D-005 | CSV exceeds GitHub's per-file size limit | **escalated --- blocking** |

## 12. Deviations from the work package

1. **The CSV commit was not made (Phase C.3, Phase E.1).** The work package
   instructs committing `data/raw/FullData.csv` as an ordinary Git object. The
   file is 296,407,423 bytes (~282.7 MiB); GitHub hard-rejects any single file
   over 100 MiB on push. The package names "the push of the CSV commit to
   GitHub fails or is rejected" as a stop-and-escalate condition; that
   condition was detected *before* the push rather than after. Creating the
   commit first would have written a ~283 MiB blob into local history that
   could only be removed by rewriting history, so the commit was withheld and
   the situation escalated as **D-005**. Everything that *describes* the file
   --- manifest, hashes, counts, immutability policy, the assertion test ---
   is committed. The file is present and hash-verified in the working tree.

2. **`tests/test_manifest.py`'s real-data assertion is skipped when the CSV is
   absent.** Required so that a clone without the CSV (the current state of the
   remote, and of Sophia until D-005 resolves) can still run a green test
   suite. When the file is present, as locally, the assertion runs and passes.

3. **The secrets scanner exempts itself from its own scan.** It necessarily
   contains the literal patterns it searches for. The exemption is exactly one
   file, its patterns are assembled from fragments to keep the file's own
   source free of real matches, and the file contains no real path or
   credential.

4. **Two extra test files beyond the three required areas.** `tests/test_paths.py`
   covers the local-path loader; the package asked for checksum, manifest, and
   run-record tests. Additive only.

5. **`.gitattributes` also marks `*.pdf` as binary**, not only `*.csv`. Same
   rationale, applied to the other byte-frozen file.

6. **The push to `origin main` has not yet been executed.** The push command
   was blocked by the local permission layer and needs Kaiyuan's approval. All
   five commits exist locally and are ready to push.

## 13. Open questions and blockers

| Item | Owner | Blocks |
| --- | --- | --- |
| **D-005** --- how to store a 283 MiB file given GitHub's 100 MiB limit. Options in the decision log: LFS (needs git-lfs on Sophia), out-of-band transfer with hash gating, or split-and-reassemble. A subset or column-pruned extract was rejected by the EXECUTOR as out of M0 scope. | Kaiyuan + COORDINATOR | The M0 gate |
| **D-002** --- confirm the data dictionary PDF is tracked as authoritative metadata rather than literature | Kaiyuan | Nothing yet; M1 depends on it |
| **Sophia evidence** --- byte-identity and clean-pull verification | Kaiyuan | The M0 gate |
| **Push approval** for `origin main` | Kaiyuan | Sophia cannot clone until pushed |
| Acquisition date of the ClimRR export is unknown | Kaiyuan | Provenance completeness |

## 14. Gate criteria assessment

> The repository structure, documentation set, and decision log exist and are
> pushed to the private remote.

**PARTIALLY MET.** All of it exists and is committed (commits `e2db0bf`,
`9262e71`, `219753f`, `764e1ce`). The push awaits approval (deviation 6).

> `data/raw/FullData.csv` is committed, and its SHA-256 matches the value
> recorded in `data/manifest.json`; the copied file is byte-identical to the
> source.

**NOT MET --- blocked by D-005.** The second and third clauses are satisfied
and evidenced: the copy is byte-identical to the source, and the smoke test
confirms the file matches the manifest. The first clause --- *committed* ---
cannot be satisfied under D-001 as written, because the resulting push would be
rejected by GitHub.

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
plus empty `git status --porcelain` output and a push URL of `DISABLED`. Note
that this criterion also depends on D-005: until the CSV reaches the remote by
some route, Sophia has nothing to hash.

## 15. Next actions

| Action | Owner |
| --- | --- |
| Decide **D-005** (CSV storage route given the 100 MiB limit) | Kaiyuan + COORDINATOR |
| Confirm or reject **D-002** | Kaiyuan |
| Approve and execute the push of the five commits to `origin main` | Kaiyuan |
| Implement the chosen D-005 route; re-run the checks; update the manifest policy field | EXECUTOR |
| Run `docs/SOPHIA_RUNBOOK.md` on `sophia-login-02` and paste back the output | Kaiyuan |
| Fill the two PENDING fields, commit the returned Sophia run records | EXECUTOR |
| Tag `m0-setup` **only after** GUIDANCE accepts the gate | EXECUTOR |
