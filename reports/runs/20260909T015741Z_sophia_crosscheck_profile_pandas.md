# Run record: 20260909T015741Z_sophia_crosscheck_profile_pandas

- **Result**: PASS
- **UTC timestamp**: 2026-09-09T01:57:41.372836+00:00
- **Git commit**: `2b7345f29efab632ef439a5d6190be37737803d5`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 4
- **Hostname**: sophia-login-02
- **Location**: sophia
- **Python**: 3.13.13 (Linux-5.14.0-611.54.1.el9_7.x86_64-x86_64-with-glibc2.34)
- **pip freeze SHA-256**: `fbe35b7d8d310e991074e6ccc74c4079e7924c7fa0eafd00274d98abc4b211db`
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
