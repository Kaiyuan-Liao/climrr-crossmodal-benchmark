# Run record: 20260912T231319Z_local_check_objectid_pair

- **Result**: PASS
- **UTC timestamp**: 2026-09-12T23:13:19.656036+00:00
- **Git commit**: `53421f00668c26130e1b33828f87b4a0190815b4`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 11
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `data/raw/FullData.csv`
- **Data SHA-256**: `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`
- **Output path**: `None`

## Config snapshot

```json
{
  "data_path": "data/raw/FullData.csv",
  "left_index": 235,
  "right_index": 236,
  "comparison": "raw string equality; no stripping, no numeric coercion"
}
```

## Result summary

- `data_sha256`: e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e
- `question`: Q11.4
- `left_index`: 235
- `left_column`: OBJECTID_12
- `right_index`: 236
- `right_column`: OBJECTID_12_13
- `n_rows`: 62834
- `n_equal_as_text`: 83
- `n_differing`: 62751
- `n_both_empty`: 83
- `n_only_left_empty`: 0
- `n_only_right_empty`: 0
- `n_left_empty`: 83
- `n_right_empty`: 83
- `empty_row_sets_identical`: True
- `n_distinct_left`: 62752
- `n_distinct_right`: 62752
- `value_sets_identical`: False
- `n_values_only_in_left`: 703
- `n_values_only_in_right`: 703
- `differing_examples`: [{'row': 1, 'left': '21362', 'right': '11303'}, {'row': 2, 'left': '17850', 'right': '21096'}, {'row': 3, 'left': '41026', 'right': '43944'}, {'row': 4, 'left': '14960', 'right': '52545'}, {'row': 5, 'left': '12452', 'right': '24125'}]
- `columns_identical_as_text`: False
