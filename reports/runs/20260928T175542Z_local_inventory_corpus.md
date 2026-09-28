# Run record: 20260928T175542Z_local_inventory_corpus

- **Result**: PASS
- **UTC timestamp**: 2026-09-28T17:55:42.203472+00:00
- **Git commit**: `e359b26c0b2f4708627420eae03e393f815485c4`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 19
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/literature/corpus_manifest.json`
- **Data SHA-256**: `3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a`
- **Output path**: `artifacts/literature/corpus_manifest.json`

## Config snapshot

```json
{
  "corpus_root": "config/local_paths.yaml:literature_corpus_root",
  "root_basename": "00"
}
```

## Result summary

- `mode`: verify
- `corpus_id`: LITCORPUS-00
- `n_files`: 1918
- `by_accessibility`: {'ok': 1918}
- `by_extension`: {'.json': 1918}
- `total_bytes`: 78798270
- `n_zero_byte`: 0
- `n_duplicate_groups`: 1
- `n_items_in_duplicate_groups`: 2
- `manifest_sha256`: 3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a
- `manifest_csv_sha256`: de795d7cd2ad0294dc4b8d0457a1707b7b37946b9c141b4ffe8a0d4f2e44a638
- `content_identity_sha256`: e217076f0f155a12f0954313059fba14904826658676e504e8cbb4c042e71f5e
- `inventory_utc`: 2026-09-28T17:55:35Z
- `read_policy`: Byte-level reads only, for SHA-256 and size. No file is decoded, parsed, rendered or inspected; no filename is read for meaning. Symlinks are not followed; archives are not expanded.
