# Sophia runbook --- M0 verification and M1-WP1 reproduction

**Who runs this:** Kaiyuan Liao. Sophia requires MFA, so the EXECUTOR cannot
reach it. The EXECUTOR prepares the scripts; you run them and paste the output
back into the COORDINATOR chat.

**Where:** `sophia-login-02`. Login nodes are sufficient for everything here ---
M0 is checksum, test and read-only checks, and the M1-WP1 profile is a single
read-only pass over the table taking about half a minute. **No compute job is
needed.**

**What this clone is:** a **pull-only** execution clone. It is pull-only both by
policy (decision D-003) and mechanically: the scripts run
`git remote set-url --push origin DISABLED` after cloning, so an accidental
push cannot succeed even though this host's SSH key has write access to the
remote. GitHub SSH from Sophia is already working and authenticates as
`Kaiyuan-Liao`; no deploy key is needed.

---

## 0. Before you start

You need the **pinned commit SHA** from the COORDINATOR. Everything below is
pinned to that exact commit --- never to a branch name.

```bash
export CLIMRR_COMMIT=<pinned-commit-sha>
```

---

## 1. Start a screen session

Long-running work lives in a named screen so a dropped connection does not kill
it.

```bash
screen -S climrr
```

Detach with `Ctrl-a` then `d`. Reattach later with `screen -r climrr`.

---

## 2. Set the machine-specific paths

These are environment variables, deliberately: no absolute path for this
machine is stored in the repository.

```bash
export CLIMRR_REPO_ROOT=<absolute path for the execution clone on Eagle>
export CLIMRR_SCRATCH_DIR=<absolute scratch path on Eagle>
```

Use the Eagle project path agreed with the COORDINATOR for `CLIMRR_REPO_ROOT`.

---

## 3. Transfer the raw CSV (out of band --- decision D-005)

`data/raw/FullData.csv` is **not in the repository**. At ~283 MiB it exceeds
GitHub's 100 MiB per-file limit, so it is copied directly, host to host, and
verified by hash. Cloning alone will not give you the data.

From the **local authoring machine** (not from Sophia):

```bash
scp "$LOCAL_REPO_ROOT/data/raw/FullData.csv" \
    <user>@sophia.alcf.anl.gov:"$CLIMRR_REPO_ROOT/data/raw/"
```

Substitute your own absolute paths and username; they are deliberately not
recorded in this repository. `$CLIMRR_REPO_ROOT` is the execution-clone path
from step 2, and the destination directory exists only after step 4 has cloned
the repo --- so either run the bootstrap first, or `mkdir -p` the directory.

Then, **on Sophia**, verify the bytes survived the transfer:

```bash
sha256sum "$CLIMRR_REPO_ROOT/data/raw/FullData.csv"
```

Expected, exactly:

```
e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e
```

and a size of `296407423` bytes (`stat -c %s`). Compare against the
`FullData.csv` entry in `data/manifest.json`.

**If the hash differs, stop.** Do not re-run anything downstream. Report the
hash you got. A truncated or corrupted transfer that goes unnoticed would
silently invalidate every result built on it.

---

## 4. Bootstrap (first time only)

```bash
bash scripts/sophia_bootstrap.sh "$CLIMRR_COMMIT"
```

If you do not yet have the repo on Sophia, clone it once by hand first, then
run the script from inside it --- the script is idempotent and will fetch,
disable the push URL, check out the pinned commit, and continue.

The script will:

1. clone or fetch the repository;
2. **disable the push URL** and print it (expect `DISABLED`);
3. check out the pinned commit in detached HEAD;
4. `module use /soft/modulefiles; module load conda; conda activate base`, then
   build `$CLIMRR_REPO_ROOT/.venv-sophia` with `--system-site-packages` and
   `pip install -r requirements.txt`;
5. generate `config/local_paths.yaml` from the tracked example, substituting
   your environment variables at run time (this file is gitignored);
6. run `pytest`;
7. run `scripts/smoke_test.py`;
8. print `git status` and the run-record paths.

---

## 5. Subsequent runs --- move to a new pinned commit

```bash
export CLIMRR_COMMIT=<new-pinned-commit-sha>
bash scripts/sophia_pull_pinned.sh "$CLIMRR_COMMIT"
source "$CLIMRR_REPO_ROOT/.venv-sophia/bin/activate"
cd "$CLIMRR_REPO_ROOT"
python -m pytest -q
python scripts/smoke_test.py
```

`sophia_pull_pinned.sh` **refuses to run** if the working tree has local
changes. That refusal is a signal, not an obstacle: this clone should never
have local changes. Report it rather than forcing past it.

---

## 5b. M1-WP1 reproduction --- the profile content hash

**What this establishes.** The M1-WP1 acceptance evidence is a single equality:
the **profile content hash** computed on Sophia must equal the one computed on
the authoring machine. That hash covers every computed fact and every rule
constant in the profile, with the `environment` block removed --- so it is
deliberately blind to hostname, Python version, pinned library versions and the
commit, and sensitive to any difference in what was actually computed from the
bytes.

Expected value, from the local run:

```text
772991c7c9adf475c2ca51806998494595d445725d6d3b7d5046752074fcba9c
```

**Outputs go to scratch, not into the clone.** Every command below writes to
`$CLIMRR_SCRATCH_DIR`, so the tracked `artifacts/profiles/` files are left
untouched and the working tree stays clean --- which matters, because
`sophia_pull_pinned.sh` refuses to run against a dirty tree and would otherwise
block the next pinned checkout. Only the run records, which land as new
untracked files under `reports/runs/`, come back.

### Steps

```bash
export CLIMRR_COMMIT=<pinned-commit-sha>
export CLIMRR_REPO_ROOT=<absolute path of the execution clone>
export CLIMRR_SCRATCH_DIR=<absolute scratch path>

bash "$CLIMRR_REPO_ROOT/scripts/sophia_pull_pinned.sh" "$CLIMRR_COMMIT"
source "$CLIMRR_REPO_ROOT/.venv-sophia/bin/activate"
cd "$CLIMRR_REPO_ROOT"
```

**1. Reinstall the pinned requirements into the existing venv (D-007).** The
versions are now exact, so this is what makes the two hosts comparable.

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

`pytest` includes a check that the running environment matches
`requirements.txt` exactly. If it fails, stop and paste the failure: the profile
below would be produced by a different stack than the one the decision pins.

**2. Verify the raw data, as always (D-005/D-006, fail closed).**

```bash
python scripts/smoke_test.py
```

**3. Profile the table.**

```bash
mkdir -p "$CLIMRR_SCRATCH_DIR/profiles"
python scripts/profile_fulldata.py --out-dir "$CLIMRR_SCRATCH_DIR/profiles"
```

This prints the manifest check, the structural counts, and a line reading
`PROFILE CONTENT HASH: ...`. Roughly half a minute and about 1.5 GB of memory;
a login node is sufficient.

**4. Cross-check with pinned pandas.**

```bash
python scripts/crosscheck_profile_pandas.py \
    --profile "$CLIMRR_SCRATCH_DIR/profiles/fulldata_profile.json" \
    --out "$CLIMRR_SCRATCH_DIR/profiles/crosscheck_pandas.json"
```

**5. Print the content hash again, on its own.**

```bash
python -c "
import json, os, sys
sys.path.insert(0, 'src')
from climrr.profile import profile_content_hash
path = os.path.join(os.environ['CLIMRR_SCRATCH_DIR'], 'profiles', 'fulldata_profile.json')
print(profile_content_hash(json.load(open(path))))
"
```

**6. Optional --- reproduce the dictionary extraction.** This checks that the
pinned `pypdf` produces identical text on both hosts. The extracted file's
header records the time of extraction, so the *files* never match byte for byte;
compare the body from the first page marker onward.

```bash
python scripts/extract_dictionary_text.py \
    --out "$CLIMRR_SCRATCH_DIR/dictionary_extracted.txt"

diff <(sed -n '/^=== PAGE 1 ===/,$p' "$CLIMRR_SCRATCH_DIR/dictionary_extracted.txt") \
     <(sed -n '/^=== PAGE 1 ===/,$p' data/metadata/dictionary_extracted.txt) \
  && echo "dictionary text identical"

python scripts/dictionary_coverage.py \
    --text "$CLIMRR_SCRATCH_DIR/dictionary_extracted.txt" \
    --out "$CLIMRR_SCRATCH_DIR/profiles/dictionary_coverage.json"
```

### What must hold

| Check | Expected |
| --- | --- |
| `git status --porcelain --untracked-files=no` | **empty**, before and after |
| `pytest` | all pass, including the pinned-requirements check |
| `scripts/smoke_test.py` | `PASS`, SHA-256 equal to `data/manifest.json` |
| `scripts/profile_fulldata.py` | `PASS`, and 62,834 rows x 275 columns |
| **Profile content hash** | **equal to the local value quoted above, character for character** |
| `scripts/crosscheck_profile_pandas.py` | `PASS`, 275 of 275 columns agree, 0 disagreements |
| Run-record `pinned_libraries` | every entry `matches_pin: true` |
| Optional: dictionary text body | identical; status counts 21 / 143 / 28 / 83 |

**If the content hashes differ, stop.** Do not re-run, re-copy, or adjust
anything. Paste both hashes, the two run records, and the `pinned_libraries`
block from each. A difference means the two hosts computed different facts from
bytes that are provably identical, which is a defect to escalate --- and finding
it is precisely what this step exists for.

### What to copy back

The M1-WP1 run records only, a few kilobytes each:

```bash
ls -1t "$CLIMRR_REPO_ROOT"/reports/runs/*sophia_profile_fulldata.* \
       "$CLIMRR_REPO_ROOT"/reports/runs/*sophia_crosscheck_profile_pandas.*
```

Everything under `$CLIMRR_SCRATCH_DIR` stays on Eagle.

---

## 6. What to check before pasting results back

The M0 gate turns on four things:

| Check | Expected |
| --- | --- |
| Push URL | `DISABLED` |
| `git status --porcelain` | **empty** (clean working tree) |
| `pytest` | all tests pass |
| Raw CSV present | `data/raw/FullData.csv` exists (it is **not** cloned --- step 3 puts it there) |
| `scripts/smoke_test.py` | prints `PASS`, and the SHA-256 it reports for `data/raw/FullData.csv` equals the value in `data/manifest.json` |

The decisive one is the **SHA-256 byte-identity check**: the hash computed on
Sophia must equal the hash recorded on the authoring machine, character for
character. If it differs, **stop and report it** --- do not re-copy, re-clone,
or "fix" anything.

---

## 7. What to copy back

Copy back **only** the run records, and only the Sophia ones:

```bash
ls -1t "$CLIMRR_REPO_ROOT"/reports/runs/*sophia*.json \
       "$CLIMRR_REPO_ROOT"/reports/runs/*sophia*.md
```

These are a few kilobytes each. Copy them to the local authoring machine (they
are committed from there, never pushed from Sophia --- decision D-003).

**Do not copy back:** data files, environment directories, `pip freeze` output,
`config/local_paths.yaml`, or anything large. Large outputs stay on Eagle.

### Then delete the Sophia copies --- this step is not optional

**After** you have confirmed the records arrived on the authoring machine, delete
them here:

```bash
rm -f "$CLIMRR_REPO_ROOT"/reports/runs/*sophia*.json \
      "$CLIMRR_REPO_ROOT"/reports/runs/*sophia*.md
```

Leaving them causes a failure one step later, and it is not obvious when it
happens. A run record generated here is **untracked** in this clone. Once it has
been committed from the authoring clone it becomes **tracked** in the next pinned
commit --- so the next `sophia_pull_pinned.sh` would have to overwrite an
untracked file, and git refuses:

```text
error: The following untracked working tree files would be overwritten by checkout:
        reports/runs/20260909T015712Z_sophia_profile_fulldata.json
```

That refusal is correct and the script does not override it. It does explain it:
it names each colliding file, says whether the pinned commit already carries the
identical bytes --- which it does if the file is one you copied back unchanged ---
and prints the exact `rm` command. **It never deletes anything itself.** If it
reports a file as *differing* rather than identical, do not delete that file:
copy it somewhere safe and report the difference, because it means this clone
holds a record that is not the one that was committed.

Deleting the copies loses nothing. The bytes live in the repository from the
commit onward, and the checkout restores them.

---

## 8. Where to paste the output

Paste into the COORDINATOR chat:

1. the full terminal output of `scripts/sophia_bootstrap.sh` (or of step 5);
2. the contents of the Sophia run-record `.md` file;
3. the exact `git status --porcelain` output (state explicitly if it was empty);
4. the pinned commit SHA you checked out.

The EXECUTOR then fills the two **PENDING** fields in
`reports/milestones/M0_SETUP_REPORT.md` --- Sophia byte-identity and Sophia
clean pull --- and commits the returned run records from the local clone.

---

## Troubleshooting

- **`module: command not found`** --- you are not on a login node with the
  module system available. Confirm you are on `sophia-login-02`.
- **`pip install` is slow** --- expected on a shared filesystem; this is why
  you are inside `screen`.
- **The smoke test reports a hash mismatch** --- stop. This is the escalation
  condition. Paste the reported hash and the expected one; change nothing.
- **The bootstrap stops with "raw CSV not found" or a hash mismatch** ---
  expected if step 3 was skipped or the transfer was incomplete. Re-run the
  `scp` and re-check `sha256sum` before anything else. Never set
  `CLIMRR_ALLOW_MISSING_RAW=1` to get past it during a gate run: that flag
  exists for deliberate code-only work, and using it here would produce a green
  run that verified nothing.
- **`git checkout` fails on the data file** --- report the error verbatim. Do
  not run `git checkout --force`.
