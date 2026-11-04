# Run record: 20261104T003406Z_local_build_p2b_items_review_v3

- **Result**: PASS
- **UTC timestamp**: 2026-11-04T00:34:06.089487+00:00
- **Git commit**: `421463a2bd47b5a3efd40a5b4356d8f579d7567f`
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
  "coordinator_edits_v3_sha256": "dba28d141d0c0e1d6e8007ddf54c4f88ecad562759d7316ad12a8d55fc3d943d",
  "corrections_applied_sha256": "f6075dfd5c5a9a1a71f926e9faa5b8ab892faf34824aed317af5a04936205862",
  "coordinator_notes": "artifacts/benchmark/review/P2b_items_coordinator_notes_v1.csv",
  "model_calls": 0
}
```

## Result summary

- `sheets`: {'OVERVIEW': 31, 'ITEMS': 10, 'PROVENANCE': 10, 'GROUPS_CITED': 5, 'LINT': 31, 'Legend': 16}
- `workbook_sha256`: f42a0427408c13adb76c097c058cb90d69dab2f163a939b8dce7be962312354f
- `items_csv_sha256`: dcb4771d5d2a3bab3990ab6edfee56ad135bdada3ae0eddfd9632472f2aaebe4
- `edited_items`: ['BI-P2B-0001', 'BI-P2B-0003', 'BI-P2B-0006', 'BI-P2B-0007', 'BI-P2B-0010']
- `edit_origin`: ['coordinator_proposed_v3']
- `coordinator_notes_sha256`: 1f4f72c39af8b73ed926dfe889c1784a6229afb11e7f7f7bca0e814ee1e849ea
