# Run record: 20260908T201345Z_local_profile_fulldata

- **Result**: PASS
- **UTC timestamp**: 2026-09-08T20:13:45.365064+00:00
- **Git commit**: `95407053e92a0e2cd0f254747ef2680f93a5067e`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 5
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `51f0a549d43e2a4c182b58464b468516c5d1ada92382dde4f081c55dcd669030`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`
- **Data path (repo-relative)**: `data/raw/FullData.csv`
- **Data SHA-256**: `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`
- **Output path**: `artifacts/profiles/fulldata_profile.json`

## Config snapshot

```json
{
  "data_path": "data/raw/FullData.csv",
  "manifest_path": "data/manifest.json",
  "sentinel_min_rate": 0.005,
  "decimal_regex": "^[+-]?(?:[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+)(?:[eE][+-]?[0-9]+)?$",
  "profile_version": 1
}
```

## Result summary

- `profile_content_hash`: 772991c7c9adf475c2ca51806998494595d445725d6d3b7d5046752074fcba9c
- `n_rows`: 62834
- `n_columns`: 275
- `duplicate_column_names`: none
- `rows_with_unexpected_width`: 0
- `all_decimal_columns`: 248
- `all_integer_columns`: 7
- `columns_with_leading_zero_values`: 2
- `constant_columns`: 5
- `looks_unique_columns`: 20
- `columns_with_any_empty`: 105
- `columns_with_candidate_sentinels`: 24
- `pin_drift`: none
