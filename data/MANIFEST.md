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

### `literature_query.txt`

| Field | Value |
| --- | --- |
| Path | `data/metadata/literature_query.txt` |
| Role | literature collection query --- provenance record for the external literature corpus (not literature, not data) |
| SHA-256 | `5a7ddf537d343b73fa0887e5f11ffbe3965fd25811f2adfc25cacee66f0ee1e5` |
| Byte size | 2,292 |
| Row count | n/a (not tabular) |
| Column count | n/a (not tabular) |
| Source description | Boolean search query supplied by JL to Kaiyuan Liao, together with the literature corpus folder |
| Received by the project | 2026-09-28 |
| Stated collector | JL (stated by the supplier) |
| Platform / database | unknown (Q19) |
| Execution date | unknown (Q20) |
| Export date | unknown (Q20) |
| Folder is the complete result set | unknown (Q21) |
| Tracked in Git | yes, pinned `-text` in `.gitattributes` |
| Storage policy | tracked in ordinary Git as an immutable object, byte for byte as received (M4-WP0, **D-015**) |
| Interpretation notes | none; the deterministic parse is a separate derived artifact, `artifacts/literature/query_parsed.json` |

**Reported, not verified:** that JL supplied this as the query the corpus was
collected with, and that JL collected the corpus. **Verified:** the bytes and
their SHA-256, identical to the file as received; and that the text parses
deterministically. **Not verified:** that this query is the one actually
executed, where, and when; and whether the folder is the whole result set.

## External corpora (not in the repository)

### `LITCORPUS-00` --- the literature corpus

Never tracked, never copied in. Its path lives only in the untracked
`config/local_paths.yaml` under `literature_corpus_root`. It is pinned by the
SHA-256 of its **inventory manifest**, which is tracked; the values below are
mirrored from `manifest.json`'s `external_corpora` block, which is authoritative
and is rewritten by `scripts/inventory_corpus.py`.

| Field | Value |
| --- | --- |
| Inventory manifest | `artifacts/literature/corpus_manifest.json` (+ `.csv`) |
| Inventory manifest SHA-256 | `3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a` |
| Content identity SHA-256 | `e217076f0f155a12f0954313059fba14904826658676e504e8cbb4c042e71f5e` |
| Files | 1,918 |
| Total bytes | 78,798,270 |
| Received by the project | 2026-09-28, from JL, with `literature_query.txt` |
| Decision | **D-015** |

See [`../docs/LITERATURE_CORPUS_INVENTORY.md`](../docs/LITERATURE_CORPUS_INVENTORY.md).

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
