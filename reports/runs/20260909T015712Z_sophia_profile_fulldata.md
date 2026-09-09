# Run record: 20260909T015712Z_sophia_profile_fulldata

- **Result**: PASS
- **UTC timestamp**: 2026-09-09T01:57:12.754480+00:00
- **Git commit**: `2b7345f29efab632ef439a5d6190be37737803d5`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 2
- **Hostname**: sophia-login-02
- **Location**: sophia
- **Python**: 3.13.13 (Linux-5.14.0-611.54.1.el9_7.x86_64-x86_64-with-glibc2.34)
- **pip freeze SHA-256**: `fbe35b7d8d310e991074e6ccc74c4079e7924c7fa0eafd00274d98abc4b211db`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`
- **Data path (repo-relative)**: `data/raw/FullData.csv`
- **Data SHA-256**: `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`
- **Output path**: `fulldata_profile.json`

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
