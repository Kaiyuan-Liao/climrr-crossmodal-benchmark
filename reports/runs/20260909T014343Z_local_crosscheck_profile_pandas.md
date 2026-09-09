# Run record: 20260909T014343Z_local_crosscheck_profile_pandas

- **Result**: PASS
- **UTC timestamp**: 2026-09-09T01:43:43.036887+00:00
- **Git commit**: `b0599f1d70009232a9c241a61f523662e306532a`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 11
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `51f0a549d43e2a4c182b58464b468516c5d1ada92382dde4f081c55dcd669030`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`
- **Data path (repo-relative)**: `data/raw/FullData.csv`
- **Data SHA-256**: `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`
- **Output path**: `crosscheck_pandas.json`

## Config snapshot

```json
{
  "data_path": "data/raw/FullData.csv",
  "manifest_path": "data/manifest.json",
  "pandas_read_options": {
    "dtype": "str",
    "keep_default_na": false,
    "na_filter": false,
    "encoding": "utf-8-sig"
  }
}
```

## Result summary

- `stdlib_profile_content_hash`: 772991c7c9adf475c2ca51806998494595d445725d6d3b7d5046752074fcba9c
- `pandas_version`: 3.0.5
- `numpy_version`: 2.4.6
- `table_level_agreement`: all agree
- `n_columns_compared`: 275
- `n_columns_agree`: 275
- `n_columns_disagree`: 0
- `disagreeing_columns`: none
