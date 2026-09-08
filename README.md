# ClimRR Cross-Modal Benchmark

Cross-modal QA benchmark built from a ClimRR climate-projection table and an
independently collected scientific-literature corpus.

**Status: M0 --- reproducible project foundation.** See
[`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md) for what is done, what is
blocked, and what happens next.

## Start here

If you are an agent or a new collaborator, read in this order:

1. [`CLAUDE.md`](CLAUDE.md) --- operating rules, roles, and the things that
   must never happen.
2. [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md) --- one screen: current
   milestone, blockers, next review.
3. The active milestone report in [`reports/milestones/`](reports/milestones/).

## Layout

```
config/     project constants; local_paths.example.yaml (real paths are untracked)
data/       metadata + manifest (write-once); raw/ CSV is untracked (D-005)
docs/       plan, state, decisions, data notes, report template, Sophia runbook
src/climrr/ paths, checksums, run records
scripts/    smoke test, secrets/paths scan, Sophia bootstrap and pinned pull
tests/      unit tests (synthetic fixtures; never the real data file)
reports/    milestones/ and runs/ (every script emits a run record)
artifacts/  derived outputs: profiles, phenomena, claims, bridges
```

## Setup

```bash
conda create -n climrr python=3.11
conda activate climrr
pip install -r requirements.txt
cp config/local_paths.example.yaml config/local_paths.yaml   # then edit
```

`data/raw/FullData.csv` is **not in this repository** --- at ~283 MiB it exceeds
GitHub's per-file limit, so it is transferred out of band and pinned by its
SHA-256 in `data/manifest.json` (decision D-005). Put it at
`data/raw/FullData.csv`, then run `python scripts/smoke_test.py` and require
`PASS`. See [`data/raw/README.md`](data/raw/README.md).

On Sophia, follow [`docs/SOPHIA_RUNBOOK.md`](docs/SOPHIA_RUNBOOK.md) instead.

## Checks (required before every commit)

```bash
pytest
python scripts/verify_no_secrets_or_paths.py
python scripts/smoke_test.py
```

## Three cautions that constrain everything downstream

1. Historical (`*_hist`) fields are **modeled baselines**, not observations.
2. `wildfire*` columns are a **Fire Weather Index** --- never wildfire
   occurrence, burned area, or ignition.
3. GEOID and other Census identifiers are **strings with leading zeros**. Read
   them as text.

No column in `data/raw/FullData.csv` has an assigned meaning yet.
[`docs/DATA_NOTES.md`](docs/DATA_NOTES.md) records column *names* only;
interpretation is the M1 milestone.
