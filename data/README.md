# `data/` --- immutable inputs

## Contents

| Path | What it is |
| --- | --- |
| `raw/FullData.csv` | The ClimRR FullData export. Primary data. **Untracked** --- obtained out of band, verified by manifest hash (D-005). See [`raw/README.md`](raw/README.md). |
| `metadata/ClimRR_Metadata_and_Data_Dictionary.pdf` | Authoritative ClimRR data dictionary. Provenance, **not** literature corpus (see decision D-002). |
| `manifest.json` | Machine-readable manifest. Source of truth for hashes and counts. |
| `MANIFEST.md` | Human-readable mirror of the manifest. |

## These files are immutable

Everything under `data/` is **write-once and byte-frozen**. It is committed
once and never rewritten.

- Never modify a file under `data/raw/` in place.
- Never write a "cleaned", "fixed", or "normalised" copy into `data/`. Derived
  data belongs in `artifacts/` or in scratch space outside the repository.
- Open these files read-only. With pandas, read `dtype=str` so nothing is
  coerced --- Census identifiers in particular are strings with leading zeros
  and become wrong the moment they are parsed as integers.
- `scripts/smoke_test.py` writes nothing here. Neither may anything else.

`.gitattributes` marks `*.csv` and `*.pdf` as `-text` (binary), so Git cannot
apply line-ending normalisation and silently change the bytes.

`tests/test_manifest.py` asserts that the SHA-256 of `data/raw/FullData.csv`
equals the value in `manifest.json`. If that test ever fails, the file has been
altered: **escalate**. Do not update the manifest to match.

## Storage policy

Per decision **D-005**, which supersedes D-001: the CSV is **not tracked in
Git**. At 296,407,423 bytes it exceeds GitHub's 100 MiB per-file limit, and Git
LFS is unavailable on Sophia. It is transferred out of band by `scp` and pinned
by its SHA-256 in `manifest.json`.

Because the bytes no longer travel with the commit, verification is not
optional. `scripts/smoke_test.py` and `tests/test_manifest.py` **fail** when the
file is missing --- they do not quietly skip --- unless
`CLIMRR_ALLOW_MISSING_RAW=1` is set deliberately. A green test run on a clone
that never saw the data would be worse than a red one.

The data-dictionary PDF remains tracked in ordinary Git (D-002).

## No interpretation

Column meanings are not established. `docs/DATA_NOTES.md` holds the column-name
inventory with **no interpretation assigned**; assigning meaning is the M1
milestone and requires the data dictionary as evidence.
