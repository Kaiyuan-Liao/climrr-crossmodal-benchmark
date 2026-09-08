# Sophia runbook --- M0 verification

**Who runs this:** Kaiyuan Liao. Sophia requires MFA, so the EXECUTOR cannot
reach it. The EXECUTOR prepares the scripts; you run them and paste the output
back into the COORDINATOR chat.

**Where:** `sophia-login-02`. Login nodes are sufficient for M0 --- these are
checksum, test, and read-only checks. **No compute job is needed.**

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

## 3. Bootstrap (first time only)

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

## 4. Subsequent runs --- move to a new pinned commit

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

## 5. What to check before pasting results back

The M0 gate turns on four things:

| Check | Expected |
| --- | --- |
| Push URL | `DISABLED` |
| `git status --porcelain` | **empty** (clean working tree) |
| `pytest` | all tests pass |
| `scripts/smoke_test.py` | prints `PASS`, and the SHA-256 it reports for `data/raw/FullData.csv` equals the value in `data/manifest.json` |

The decisive one is the **SHA-256 byte-identity check**: the hash computed on
Sophia must equal the hash recorded on the authoring machine, character for
character. If it differs, **stop and report it** --- do not re-copy, re-clone,
or "fix" anything.

---

## 6. What to copy back

Copy back **only** the run records, and only the Sophia ones:

```bash
ls -1t "$CLIMRR_REPO_ROOT"/reports/runs/*sophia*.json \
       "$CLIMRR_REPO_ROOT"/reports/runs/*sophia*.md
```

These are a few kilobytes each. Copy them to the local authoring machine (they
are committed from there, never pushed from Sophia --- decision D-003).

**Do not copy back:** data files, environment directories, `pip freeze` output,
`config/local_paths.yaml`, or anything large. Large outputs stay on Eagle.

---

## 7. Where to paste the output

Paste into the COORDINATOR chat:

1. the full terminal output of `scripts/sophia_bootstrap.sh` (or of step 4);
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
- **`git checkout` fails on the data file** --- report the error verbatim. Do
  not run `git checkout --force`.
