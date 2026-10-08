# Run record: 20261008T214521Z_local_wp2_retrieve

- **Result**: PASS
- **UTC timestamp**: 2026-10-08T21:45:21.150441+00:00
- **Git commit**: `6080cc385d867e22382739d827fe17ea0135462a`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 7
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/literature/corpus_manifest.json`
- **Data SHA-256**: `3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a`
- **Output path**: `artifacts/literature/wp2_candidates.json`

## Config snapshot

```json
{
  "corpus_root": "config/local_paths.yaml:literature_corpus_root",
  "terms_sha256": "3d0b1513478b8096a4507f454df1ab5b22928b25fd3354d096961198a1e7d02c",
  "cap": 12
}
```

## Result summary

- `actions`: {'pool': 'written', 'candidates': 'written'}
- `sha256`: {'wp2_terms.json': '3d0b1513478b8096a4507f454df1ab5b22928b25fd3354d096961198a1e7d02c', 'wp2_qualifying_pool.json': '8f097f7adfab4fc5987061aefb0d31b37f12c9fcc1fba8721b6e96316048a3f0', 'wp2_candidates.json': 'e155e70e338ffb67f8c881a8a3fdb794e28c0f048c43afc10b0a723135ec8d9c'}
- `n_items_scanned`: 1918
- `n_parse_failures`: 0
- `n_qualifying_before_dedupe`: 4
- `removed_as_later_duplicates`: []
- `n_qualifying_pool`: 4
- `candidate_ids`: ['LIT-000166', 'LIT-000519', 'LIT-001501', 'LIT-001536']
- `pool_short_of_cap`: True
