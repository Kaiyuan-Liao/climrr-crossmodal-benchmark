# Run record: 20261103T232845Z_local_build_p2b_items_review_v3

- **Result**: PASS
- **UTC timestamp**: 2026-11-03T23:28:45.890551+00:00
- **Git commit**: `7825fcfc487608224fbaac5c406b62f8f61c2bc4`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 2
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/items/index.json`
- **Data SHA-256**: `b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804`
- **Output path**: `artifacts/benchmark/review/P2b_items_review_v3.xlsx`

## Config snapshot

```json
{
  "items_index_sha256": "b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804",
  "lint_sha256": "183bcdd057ef0fcdc6e6aba1841a307eaa1d44c9444f7b33d542d24fd9e3de33",
  "coordinator_edits_v2_sha256": "a1b011d4179c9c57eb3a05911e15b6264a84bde6726c43a9c673faf729c19ebf",
  "corrections_applied_sha256": "9bbd39d924ab3314929b6fc54c2d67244ebfc76efe1d4ddf61ede85491d5e3c5",
  "coordinator_notes": "artifacts/benchmark/review/P2b_items_coordinator_notes_v1.csv",
  "model_calls": 0
}
```

## Result summary

- `sheets`: {'OVERVIEW': 30, 'ITEMS': 10, 'PROVENANCE': 10, 'GROUPS_CITED': 5, 'LINT': 31, 'Legend': 16}
- `workbook_sha256`: b0276c5401a988fa22e99e57abe3406f01e7a5e72304f507921a2d52a77ba3ba
- `items_csv_sha256`: 39346e18b454c6586e758a9b78ffda1e7c5da73a8c80483e405a6361ef64fac3
- `edited_items`: ['BI-P2B-0001', 'BI-P2B-0003', 'BI-P2B-0006', 'BI-P2B-0007', 'BI-P2B-0010']
- `edit_origin`: ['coordinator_proposed_v2']
- `coordinator_notes_sha256`: 1f4f72c39af8b73ed926dfe889c1784a6229afb11e7f7f7bca0e814ee1e849ea
