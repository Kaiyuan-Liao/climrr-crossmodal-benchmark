# Run record: 20260912T231209Z_local_dictionary_coverage

- **Result**: PASS
- **UTC timestamp**: 2026-09-12T23:12:09.960000+00:00
- **Git commit**: `53421f00668c26130e1b33828f87b4a0190815b4`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
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
  "resolutions_path": "data/metadata/resolutions.yaml"
}
```

## Result summary

- `columns_classified`: 275
- `source_pdf_sha256`: b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db
- `extracted_text_sha256`: 1d0fae06c6a5a9714fe890936d002cd0ac84829262465d4930d04acb400553da
- `extractor`: pypdf 6.18.0
- `dictionary_sections_parsed`: 11
- `resolutions_sha256`: 8d8d194638d1e2ac5264ddffbc296b908a1aa406c77467939c9f5c4ed6294ac9
- `resolutions_applied`: 2
- `status_verified_from_dictionary`: 21
- `status_owner_confirmed`: 0
- `status_partially_resolved`: 143
- `status_unresolved`: 28
- `status_structurally_observed_only`: 83
- `baseline_status_verified_from_dictionary`: 21
- `baseline_status_owner_confirmed`: 0
- `baseline_status_partially_resolved`: 143
- `baseline_status_unresolved`: 28
- `baseline_status_structurally_observed_only`: 83
- `match_rule_counts`: {'none': 83, 'exact_name': 31, 'prefix_or_stem': 85, 'manual_candidate': 48, 'case_insensitive': 28}
- `statuses_without_span`: none
