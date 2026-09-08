# Data manifest

Human-readable mirror of [`manifest.json`](manifest.json). `manifest.json` is
the machine-readable source of truth that `scripts/smoke_test.py` and
`tests/test_manifest.py` check against; this file must be kept in step with it.

Generated (UTC): 2026-09-08T18:39:29Z
Row counts exclude the header line.

### `FullData.csv`

| Field | Value |
| --- | --- |
| Path | `data/raw/FullData.csv` |
| Role | raw primary data |
| SHA-256 | `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e` |
| Byte size | 296,407,423 |
| Row count | 62834 |
| Column count | 275 |
| Source description | ClimRR FullData export, provided by Kaiyuan Liao |
| Acquisition date | unknown |
| Tracked in Git | **no** (gitignored) |
| Storage policy | untracked; transferred out of band (scp) and pinned by the SHA-256 above -- see DECISION_LOG **D-005**, which supersedes D-001 |
| Interpretation notes | no interpretation assigned; see docs/DATA_NOTES.md (M1) |
### `ClimRR_Metadata_and_Data_Dictionary.pdf`

| Field | Value |
| --- | --- |
| Path | `data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf` |
| Role | authoritative metadata / data dictionary (not literature corpus) |
| SHA-256 | `b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db` |
| Byte size | 667,097 |
| Row count | n/a (not tabular) |
| Column count | n/a (not tabular) |
| Source description | ClimRR FullData export, provided by Kaiyuan Liao |
| Acquisition date | unknown |
| Tracked in Git | yes |
| Storage policy | tracked in ordinary Git as an immutable object (D-002) |
| Interpretation notes | no interpretation assigned; see docs/DATA_NOTES.md (M1) |

## Immutability

`FullData.csv` is **not tracked by Git** (D-005). It arrives out of band and its
bytes are pinned solely by the SHA-256 above, so every host must verify it
before use: run `python scripts/smoke_test.py` and require `PASS`. See
[`raw/README.md`](raw/README.md).

Both files are byte-immutable. They are committed once and never rewritten. If
a recomputed SHA-256 ever differs from the value above, that is a defect to be
escalated -- not a manifest to be updated.

`.gitattributes` marks `*.csv` and `*.pdf` as `-text` (binary). The PDF is
tracked, so this actively protects it; the rule is kept for `*.csv` so that any
CSV that ever does enter the repository cannot be normalised.
