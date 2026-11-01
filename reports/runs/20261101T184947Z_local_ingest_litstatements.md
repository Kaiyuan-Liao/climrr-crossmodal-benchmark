# Run record: 20261101T184947Z_local_ingest_litstatements

- **Result**: PASS
- **UTC timestamp**: 2026-11-01T18:49:47.310680+00:00
- **Git commit**: `feac6465b55c8f985f9cf403983ffbea293b40e2`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `litstatements_run2_evidence.tar.gz`
- **Data SHA-256**: `7d9077392ceb961035790a9dc3c89d9a825aabe56bca5ce0184ad674b9ffc414`
- **Output path**: `artifacts/litstatements/run2`

## Config snapshot

```json
{
  "source": "litstatements_run2_evidence.tar.gz (extracted)",
  "source_tarball_sha256": "7d9077392ceb961035790a9dc3c89d9a825aabe56bca5ce0184ad674b9ffc414",
  "excluded": [
    "prompt_user.txt",
    "response.json"
  ],
  "run_executed_on": "Polaris; this record is the local ingest, not the run",
  "model_calls": 0
}
```

## Result summary

- `manifest_sha256`: 6ff23183444ffdde86d5d012fa38c1d2a5a0c49392c5602af35fd49f9dd01f77
- `files_copied_this_run`: 0
- `files_in_manifest`: 252
- `excluded_files`: 486
- `counts`: {'papers': 243, 'statements': 1018, 'deterministic_pass': 485, 'rejected_pre_review': 533, 'rejected_by_check': {'enums_valid': 84, 'passage_length_pass': 7, 'passage_type_pass': 340, 'span_reslice_pass': 129, 'statement_value_pass': 90}, 'papers_with_error': 0, 'parse_errors': 21, 'evidence_roles': {'core_candidate': 379, 'cited_candidate': 106, 'background_consensus_candidate': 262, 'unusable': 271}}
- `independence_fields_available`: {'year': False, 'venue': False, 'authors': False}
- `diagnostic_same_file_sha256`: [['239052352', '257056592']]
- `diagnostic_same_title_section`: [['221671377', '256835585'], ['237554329', '239696378'], ['239052352', '257056592'], ['243767055', '257108685']]
- `parse_error_finish_reasons`: ['length']
- `run1`: {'paper_dirs': 6, 'papers_with_statements': ['134230133', '154007324'], 'papers_with_http_error': ['14300', '154777913', '157247664'], 'papers_prompt_only': ['16316827'], 'generator_version': 'litstatement_agent v1'}
