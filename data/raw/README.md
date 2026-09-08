# `data/raw/` --- untracked, out-of-band, hash-pinned

`FullData.csv` is **not tracked by Git** (decision **D-005**, which supersedes
D-001). `data/raw/*.csv` is gitignored. A fresh clone of this repository will
not contain the file, and that is correct.

## Why

The file is **296,407,423 bytes (~282.7 MiB)**. GitHub hard-rejects any single
file over 100 MiB on push, so it cannot be committed as an ordinary Git object.
Git LFS was rejected because git-lfs is unavailable on the Sophia execution
host, where an LFS pointer would clone as a text stub and break the
byte-identity gate.

## What replaces the commit

The bytes are pinned by **SHA-256 in `data/manifest.json`**, not by a commit
SHA. The guarantee is unchanged in strength but different in mechanism: the
commit no longer carries the bytes, so every host must prove it holds the same
bytes before any work is trusted.

```
FullData.csv
  sha256  e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e
  bytes   296407423
  shape   62,834 data rows x 275 columns
```

## How to obtain it

- **Locally:** copy it from the original ClimRR export supplied by Kaiyuan
  Liao, into `data/raw/FullData.csv`.
- **On Sophia:** transferred by `scp` from the authoring machine. See the
  transfer step in [`../../docs/SOPHIA_RUNBOOK.md`](../../docs/SOPHIA_RUNBOOK.md).

Then verify, from the repository root:

```bash
python scripts/smoke_test.py
```

It must print `PASS`. If the hash differs, **stop and escalate** --- do not
re-copy, and do not update the manifest to match.

## Immutability still applies

The file is write-once. Never modify it in place, never write a cleaned copy
into `data/`, and always open it read-only (`dtype=str` with pandas, so that
Census identifiers keep their leading zeros). Derived data belongs in
`artifacts/` or in scratch space outside the repository.
