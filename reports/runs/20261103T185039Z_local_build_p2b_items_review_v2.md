# Run record: 20261103T185039Z_local_build_p2b_items_review_v2

- **Result**: PASS
- **UTC timestamp**: 2026-11-03T18:50:39.878950+00:00
- **Git commit**: `37c703714c7a8fc52b9e2b64e10890c54bd72ee6`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 6
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/items/index.json`
- **Data SHA-256**: `b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804`
- **Output path**: `artifacts/benchmark/review/P2b_items_review_v2.xlsx`

## Config snapshot

```json
{
  "items_index_sha256": "b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804",
  "lint_sha256": "183bcdd057ef0fcdc6e6aba1841a307eaa1d44c9444f7b33d542d24fd9e3de33",
  "coordinator_edits_sha256": "98bae42677f5cc5727527f865657c53e3bcfae2b2c3a4e183a1126b2c4efff86",
  "coordinator_notes": "artifacts/benchmark/review/P2b_items_coordinator_notes_v1.csv",
  "kaiyuan_dispositions": [
    "accept",
    "accept_with_edits",
    "reject",
    "regenerate"
  ],
  "model_calls": 0
}
```

## Result summary

- `sheets`: {'OVERVIEW': 29, 'ITEMS': 10, 'PROVENANCE': 10, 'GROUPS_CITED': 5, 'LINT': 31, 'Legend': 15}
- `workbook_sha256`: 94d6cf5bb2bc1e01752a2e94ab97a35db2a19097281236a6545e4c663005a9ee
- `items_csv_sha256`: d5e5b7497e604af55cb6ea238982b4ec9aed64b74bd7a7176e8548629278cf46
- `current_runs`: {'BI-P2B-0001': 'run2', 'BI-P2B-0002': 'run2', 'BI-P2B-0003': 'run2', 'BI-P2B-0004': 'run2', 'BI-P2B-0005': 'run2', 'BI-P2B-0006': 'run2', 'BI-P2B-0007': 'run2', 'BI-P2B-0008': 'run2', 'BI-P2B-0009': 'run2', 'BI-P2B-0010': 'run3'}
- `edited_items`: ['BI-P2B-0001', 'BI-P2B-0003', 'BI-P2B-0006', 'BI-P2B-0007', 'BI-P2B-0010']
- `coordinator_notes_sha256`: 1f4f72c39af8b73ed926dfe889c1784a6229afb11e7f7f7bca0e814ee1e849ea
