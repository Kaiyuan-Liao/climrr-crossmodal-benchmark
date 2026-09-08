# CLAUDE.md --- operating rules for this repository

Read this file, then `docs/PROJECT_STATE.md`, then the active milestone report
in `reports/milestones/`, **before doing any work.** `PROJECT_STATE.md` tells
you which milestone is active and what is blocked; the milestone report tells
you what has already been established as evidence. Work started without
reading both will duplicate or contradict prior decisions.

## Roles

| Role | Who | Authority |
| --- | --- | --- |
| **GUIDANCE** | Separate review chat | Reviews milestone gates. Judges scientific soundness. Does not write code. |
| **COORDINATOR** | Separate planning chat | Decomposes milestones into work packages, sets scope, drafts decisions. Does not write code. |
| **EXECUTOR** | Claude Code in this repo | Implements the work package as written, runs checks, produces evidence, commits and pushes. |
| **Kaiyuan Liao** | Project owner | Final authority on every scientific and scope decision. Runs anything that requires Sophia access. |

The EXECUTOR does **not** change scope, invent scientific definitions, or
resolve an open decision by picking a plausible answer. When a work package is
silent on something that changes the scientific meaning of the output: stop,
state the missing decision precisely, and escalate to the COORDINATOR and
Kaiyuan. Do not improvise and note it later.

## Raw data is immutable

`data/raw/` is write-once. Committed data files are byte-frozen and their
SHA-256 values are recorded in `data/manifest.json`.

- Never modify a file under `data/raw/` in place.
- Never write a "cleaned", "fixed", or "normalised" copy back into `data/`.
  Derived data goes to `artifacts/` or to scratch space outside the repo.
- Open raw files read-only. If you use pandas, read with `dtype=str` so that
  nothing is silently coerced.
- If a recomputed hash ever differs from the manifest, that is a **defect to
  escalate**, not a manifest to update.

## Do not invent data semantics

No column may be renamed, grouped, filtered, unit-converted, or described in
prose until the milestone that authorises interpretation (M1) says so, and then
only with the data dictionary in `data/metadata/` as evidence. Column names go
into the inventory in `docs/DATA_NOTES.md` verbatim --- including truncations
and duplicates --- with no meaning attached.

### Three non-negotiable data cautions (they apply even before M1)

1. **Historical fields are modeled baselines, not observations.** Anything
   named `*_hist` is model output for a historical period. Never describe it as
   measured, observed, or recorded.
2. **`wildfire*` columns are a Fire Weather Index, never wildfire occurrence.**
   FWI is a meteorological fire-danger index. It does not mean a fire happened,
   burned area, ignition probability, or fire risk to a structure. Any question
   or claim that reads an FWI value as an actual fire is wrong.
3. **GEOID and other Census identifiers are strings with leading zeros.**
   Read them as text and keep them as text. Coercing them to integers destroys
   real identifiers and silently corrupts every join.

## Required checks before every commit

Both must pass, every time, with no exceptions:

```bash
pytest
python scripts/verify_no_secrets_or_paths.py
```

The scan must report **zero hits**. Resolve any hit with a placeholder in the
tracked file and the real value in untracked `config/local_paths.yaml`.

## Commit prohibitions

Never commit:

- secrets or credentials of any kind (keys, `.pem`, `.env`);
- absolute machine paths in tracked files --- use `<PLACEHOLDER>` in
  `config/local_paths.example.yaml`, real values only in the gitignored
  `config/local_paths.yaml`;
- literature PDFs or any literature corpus (`literature/` is gitignored; the
  metadata data dictionary under `data/metadata/` is *not* literature);
- large or regenerable outputs (`*.npy`, `*.npz`, `*.parquet`, `*.pkl`,
  `outputs/`, `artifacts/**/large/`);
- environment directories (`.venv*`, `__pycache__`).

## Sync policy: local authoring, Sophia execution

Single-writer model. This local clone is the **only** clone that commits and
pushes.

- The Sophia clone at the configured Eagle path is **pull-only**, by policy and
  by a disabled push URL (`git remote set-url --push origin DISABLED`), even
  though its SSH key has write access.
- Sophia checks out **pinned commit SHAs**, never a moving branch.
- Large outputs stay on Eagle. Only small evidence --- run records, small
  reports --- is copied back and committed from the local clone.
- Sophia requires MFA and cannot be driven by an agent. Prepare scripts and a
  runbook; Kaiyuan executes them and pastes the output back.
  See `docs/SOPHIA_RUNBOOK.md`.

## Run records are mandatory

Every script in this repo calls `climrr.runrecord.write_run_record` and emits a
JSON + Markdown pair under `reports/runs/`. A result with no run record is not
evidence. The record captures the commit SHA, whether the tree was dirty, the
host and location label, the Python version, a `pip freeze` fingerprint, the
config snapshot, and the SHA-256 of the data actually read.

## When to stop

Stop and escalate --- do not improvise --- if:

- a data hash changes between reads, or a copy does not match its source;
- observed row or column counts differ from the manifest (report the actual
  numbers; do not "fix" anything);
- a push is rejected;
- a tracked file trips the secrets/paths scan and no placeholder resolves it;
- you find yourself about to interpret, rename, or filter a column.
