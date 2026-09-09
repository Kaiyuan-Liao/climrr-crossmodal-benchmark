# Run record: 20260909T013248Z_local_dictionary_coverage

- **Result**: PASS
- **UTC timestamp**: 2026-09-09T01:32:48.123152+00:00
- **Git commit**: `f60da2f6ed4d4f9530a1ce415cc15e8f65e11792`
- **Working tree dirty (tracked files)**: False
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
- `extracted_text_sha256`: 29d5f6459a617ab8238d48d180e85cc79df5aef5dbbabb58f1e74cb07158b7f7
- `extractor`: pypdf 6.18.0
- `dictionary_sections_parsed`: 11
- `status_verified_from_dictionary`: 21
- `status_partially_resolved`: 143
- `status_unresolved`: 28
- `status_structurally_observed_only`: 83
- `match_rule_counts`: {'none': 83, 'exact_name': 31, 'prefix_or_stem': 85, 'manual_candidate': 48, 'case_insensitive': 28}
- `statuses_without_span`: none
