# Run record: 20260909T014309Z_local_dictionary_coverage

- **Result**: PASS
- **UTC timestamp**: 2026-09-09T01:43:09.022602+00:00
- **Git commit**: `b0599f1d70009232a9c241a61f523662e306532a`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 7
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `51f0a549d43e2a4c182b58464b468516c5d1ada92382dde4f081c55dcd669030`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`
- **Data path (repo-relative)**: `data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf`
- **Data SHA-256**: `b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db`
- **Output path**: `artifacts/profiles/dictionary_coverage.json`

## Config snapshot

```json
{
  "data_path": "data/raw/FullData.csv",
  "pdf_path": "data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf",
  "extracted_text_path": "data/metadata/dictionary_extracted.txt"
}
```

## Result summary

- `columns_classified`: 275
- `source_pdf_sha256`: b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db
- `extracted_text_sha256`: 1d0fae06c6a5a9714fe890936d002cd0ac84829262465d4930d04acb400553da
- `extractor`: pypdf 6.18.0
- `dictionary_sections_parsed`: 11
- `status_verified_from_dictionary`: 21
- `status_partially_resolved`: 143
- `status_unresolved`: 28
- `status_structurally_observed_only`: 83
- `match_rule_counts`: {'none': 83, 'exact_name': 31, 'prefix_or_stem': 85, 'manual_candidate': 48, 'case_insensitive': 28}
- `statuses_without_span`: none
