# Run record: 20261103T005754Z_local_build_p2b_items_review

- **Result**: PASS
- **UTC timestamp**: 2026-11-03T00:57:54.640399+00:00
- **Git commit**: `6ca9a93ec563fd02e52d8c72c4f23efd53ac9daf`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 4
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/items/run2/manifest.json`
- **Data SHA-256**: `c9c6bc9bc1a4f19d94e7a5e9c9514c34c9a3ad18b60dc97a11b87df2b84d60e9`
- **Output path**: `artifacts/benchmark/review/P2b_items_review_v1.xlsx`

## Config snapshot

```json
{
  "items_manifest_sha256": "c9c6bc9bc1a4f19d94e7a5e9c9514c34c9a3ad18b60dc97a11b87df2b84d60e9",
  "lint_sha256": "5b5cf722f54ad8bc7f790a6591f467f69c3cb963e6d26cec9529835e1d7d8d31",
  "coordinator_notes": "artifacts/benchmark/review/P2b_items_coordinator_notes_v1.csv",
  "packets": "synthpackets v3a at 1f175dac7801b3d27ca7ed1961debe88e22b4dc6",
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

- `sheets`: {'OVERVIEW': 25, 'ITEMS': 10, 'PROVENANCE': 10, 'GROUPS_CITED': 4, 'LINT': 25, 'Legend': 13}
- `workbook_sha256`: b329f9efc88fb8e639ee2e29f27993bf160fccd55937b7ca7046acfb545c08b8
- `items_csv_sha256`: ebcb856b21eddf02e69a2d51a32d689fe2988b1ea77130abfffc47c4c505eb73
- `coordinator_notes_sha256`: 1f4f72c39af8b73ed926dfe889c1784a6229afb11e7f7f7bca0e814ee1e849ea
