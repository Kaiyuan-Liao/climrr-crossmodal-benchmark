# Run record: 20261008T231442Z_local_wp2_adjudicate

- **Result**: PASS
- **UTC timestamp**: 2026-10-08T23:14:42.708679+00:00
- **Git commit**: `ab8033517f8bd323c4f2e3169000a03d209e9227`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 12
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/literature/wp2_candidates.json`
- **Data SHA-256**: `e155e70e338ffb67f8c881a8a3fdb794e28c0f048c43afc10b0a723135ec8d9c`
- **Output path**: `artifacts/literature/wp2_comparison.json`

## Config snapshot

```json
{
  "corpus_root": "config/local_paths.yaml:literature_corpus_root",
  "reader_1": "258536a",
  "blind": "939111e"
}
```

## Result summary

- `actions`: {'LIT-000166.json': 'written', 'LIT-000519.json': 'written', 'LIT-001501.json': 'written', 'LIT-001536.json': 'written', 'comparison': 'written', 'summary': 'written'}
- `spans`: {'reader_1': 63, 'reader_2': 66}
- `counts`: {'aligned_pairs': 13, 'reader_1_only': 7, 'reader_2_only': 6}
- `statuses`: {'independently_confirmed': 6, 'adjudicated_modified': 7, 'single_reader_provisional': 13, 'rejected_on_review': 0}
- `tiers`: {'A': 6, 'B': 7, 'C': 13}
