# Run record: 20261101T235300Z_local_build_independence_v2

- **Result**: PASS
- **UTC timestamp**: 2026-11-01T23:53:00.512681+00:00
- **Git commit**: `c1bb5e3c323a58077f471cd4aed44ea86c813f10`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `litstatements_run2_evidence.tar.gz`
- **Data SHA-256**: `7d9077392ceb961035790a9dc3c89d9a825aabe56bca5ce0184ad674b9ffc414`
- **Output path**: `artifacts/litstatements/run2/independence_v2.json`

## Config snapshot

```json
{
  "rule": "DR-LIT-IND-1 v2",
  "decision": "D-046",
  "version": "litindependence v1",
  "title_normalization": "lowercase; [\\W_]+ -> ' '; strip",
  "tarball_sha256": "7d9077392ceb961035790a9dc3c89d9a825aabe56bca5ce0184ad674b9ffc414",
  "kept_from_prompt_user": "title section only, as a hash",
  "model_calls": 0
}
```

## Result summary

- `papers_n`: 243
- `canonical_papers_n`: 239
- `n_title_section_present`: 222
- `same_paper_sha256_groups`: [['239052352', '257056592']]
- `possible_duplicate_title_groups`: [['221671377', '256835585'], ['237554329', '239696378'], ['239052352', '257056592'], ['243767055', '257108685']]
- `merged_groups`: [['221671377', '256835585'], ['237554329', '239696378'], ['239052352', '257056592'], ['243767055', '257108685']]
- `by_basis`: {'same_paper_sha256': 2, 'possible_duplicate_title': 6, 'assumed_independent_distinct_ids': 235}
- `independence_v2_sha256`: 6b66417e16e3b6f38932214b1584a261ce36704d4c32dc7fb3bfcd46e6c5a34d
