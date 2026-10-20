# Run record: 20261020T224151Z_local_ingest_survey_run1

- **Result**: PASS
- **UTC timestamp**: 2026-10-20T22:41:51.287161+00:00
- **Git commit**: `9d2da14a0d983dcbe5d22c5cf1026324271d7612`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 127
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `survey_run1.tar.gz`
- **Data SHA-256**: `edd68196834d54fae7cd0073dcb6d389a55452caf90f23d6fc838e160c7a2739`
- **Output path**: `artifacts/literature/survey/run1`

## Config snapshot

```json
{
  "source": "survey_run1.tar.gz",
  "tools_sha256": {
    "run_query.py": "5f56ee49f0da675f49ef490b506c030b307c693032e8be9097e499cf1c64030d",
    "survey_driver.py": "e1fb664c98e4ff866bb348c8930bfc1b9243957441b8a19ea0893e0b711af4cd"
  },
  "run_executed_on": "Polaris (polaris-login-01); this record is the local ingest, not the run",
  "excluded": "_duckdb_tmp directories; header-only topical/hits.csv"
}
```

## Result summary

- `n_rows`: 14
- `n_ok`: 12
- `n_error`: 2
- `n_files_ingested`: 122
- `total_bytes`: 12237164
- `manifest_sha256`: 74ba7d7c72e7920ac16e1cc7c49ab2543add316df37baf60ff3b52c10c2d125d
- `header_only_hits_not_copied`: 12
- `duckdb_tmp_dirs_removed`: 0
- `doc_sha256`: 34bd705fef941cd6bda2c3cb891bebf021a26f34047ba0c97a9d203e230ac625
- `counts`: {'DC-001': [124420, 88245, 'ok'], 'DC-002': [123948, 88021, 'ok'], 'DC-003': [84926, 61190, 'ok'], 'DC-004': [27498, 17394, 'ok'], 'DC-005': [6981, 4946, 'ok'], 'DC-006': [3076, 2638, 'ok'], 'DC-007': [548, 395, 'ok'], 'DC-008': [551, 396, 'ok'], 'DC-009': [0, 0, 'ok'], 'DC-010': [1, 1, 'ok'], 'DC-011': [None, None, 'error'], 'DC-012': [0, 0, 'ok'], 'DC-013': [None, None, 'error'], 'DC-014': [2, 2, 'ok']}
- `label`: diagnostic coverage count, not prevalence
