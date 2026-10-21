# Run record: 20261020T220725Z_local_wp4_adjudicate

- **Result**: PASS
- **UTC timestamp**: 2026-10-20T22:07:25.383910+00:00
- **Git commit**: `d90595c0d85271e7665ee15b9d14a234a768e1a8`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 26
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/literature/wp4_sample.json`
- **Data SHA-256**: `f3cb5d0c3c4e0598860b2dad5a66219a3c252a92a7800d193111dec21fdcea15`
- **Output path**: `artifacts/literature/wp4_comparison.json`

## Config snapshot

```json
{
  "corpus_root": "config/local_paths.yaml:litcorpus02_root",
  "reader_1": "e0857aa",
  "blind": "c452d7d"
}
```

## Result summary

- `actions`: {'LIT2-000084.json': 'written', 'LIT2-000185.json': 'written', 'LIT2-000203.json': 'written', 'LIT2-000315.json': 'written', 'LIT2-000366.json': 'written', 'LIT2-000470.json': 'written', 'LIT2-000499.json': 'written', 'LIT2-000560.json': 'written', 'LIT2-000662.json': 'written', 'LIT2-000673.json': 'written', 'LIT2-000786.json': 'written', 'LIT2-000803.json': 'written', 'LIT2-000927.json': 'written', 'LIT2-001063.json': 'written', 'LIT2-001075.json': 'written', 'LIT2-001157.json': 'written', 'LIT2-001160.json': 'written', 'LIT2-001236.json': 'written', 'LIT2-001293.json': 'written', 'LIT2-001308.json': 'written', 'comparison': 'written', 'summary': 'written'}
- `spans`: {'reader_1': 300, 'reader_2': 377}
- `counts`: {'aligned_pairs': 50, 'reader_1_only': 33, 'reader_2_only': 35}
- `statuses`: {'independently_confirmed': 3, 'adjudicated_modified': 47, 'single_reader_provisional': 68, 'rejected_on_review': 0}
- `tiers`: {'A': 3, 'B': 47, 'C': 68}
- `unresolved_ties`: ['LIT2-000203-C2']
