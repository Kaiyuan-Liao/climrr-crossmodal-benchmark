# Run record: 20261118T061431Z_local_dictionary_coverage

- **Result**: PASS
- **UTC timestamp**: 2026-11-18T06:14:31.656929+00:00
- **Git commit**: `69b3a22b88d0dad2a9b4ecdd038d41062732b9ae`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 8
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf`
- **Data SHA-256**: `b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db`
- **Output path**: `artifacts/profiles/dictionary_coverage.json`

## Config snapshot

```json
{
  "data_path": "data/raw/FullData.csv",
  "pdf_path": "data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf",
  "extracted_text_path": "data/metadata/dictionary_extracted.txt",
  "resolutions_path": "data/metadata/resolutions.yaml",
  "inferred_candidates_path": "data/metadata/inferred_candidates.yaml"
}
```

## Result summary

- `columns_classified`: 275
- `source_pdf_sha256`: b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db
- `extracted_text_sha256`: 1d0fae06c6a5a9714fe890936d002cd0ac84829262465d4930d04acb400553da
- `extractor`: pypdf 6.18.0
- `dictionary_sections_parsed`: 11
- `resolutions_sha256`: d86e1cd4e92ab51562ec251c98652d135280a52642012f6c94f3e2d02595869a
- `resolutions_applied`: 8
- `inferred_candidates_sha256`: 62cd7a2d58a7657002bc668820b3ac9a25381fa6229ae30f195bd6aa5a0554d3
- `inferred_candidates_read`: 20
- `inferred_candidates_blocked`: none
- `status_verified_from_dictionary`: 21
- `status_owner_confirmed`: 0
- `status_inferred_candidate`: 20
- `status_partially_resolved`: 130
- `status_unresolved`: 28
- `status_structurally_observed_only`: 76
- `baseline_status_verified_from_dictionary`: 21
- `baseline_status_owner_confirmed`: 0
- `baseline_status_inferred_candidate`: 0
- `baseline_status_partially_resolved`: 143
- `baseline_status_unresolved`: 28
- `baseline_status_structurally_observed_only`: 83
- `match_rule_counts`: {'none': 83, 'exact_name': 31, 'prefix_or_stem': 85, 'manual_candidate': 48, 'case_insensitive': 28}
- `statuses_without_span`: none
