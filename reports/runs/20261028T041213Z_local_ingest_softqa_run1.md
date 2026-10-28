# Run record: 20261028T041213Z_local_ingest_softqa_run1

- **Result**: PASS
- **UTC timestamp**: 2026-10-28T04:12:13.946842+00:00
- **Git commit**: `95e1ec851f2ac703654df52ac1ccc9c3d777fcd7`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 269
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `softqa_run1.tar.gz`
- **Data SHA-256**: `8a0e444996cc09a87c848aa9013e228d39a3f831e7a701519eb7db41f3654e3e`
- **Output path**: `artifacts/softqa/run1`

## Config snapshot

```json
{
  "source": "softqa_run1.tar.gz",
  "source_tarball_sha256": "8a0e444996cc09a87c848aa9013e228d39a3f831e7a701519eb7db41f3654e3e",
  "excluded": [
    "prompt_user.txt",
    "response.json"
  ],
  "run_executed_on": "Polaris; this record is the local ingest, not the run"
}
```

## Result summary

- `n_files_ingested`: 248
- `files_copied_from_source`: 246
- `total_bytes`: 3789681
- `manifest_sha256`: c0c193695023d08435e4fed0451f4ef445aa429f68bb43780ab638bd5b26b3d9
- `excluded_files`: 486
- `schema_records_validated`: 193
- `log_start`: {'candidates': '243', 'units': '5', 'qa_types': '6', 'model': 'gpt-oss-120b', 'units_sha': '5bb486ef6428', 'qa_sha': 'f0d0f07bf0fd', 'system_sha': 'f2e493e179aa', 'index': 'fbb4affb7162'}
- `counts`: {'papers': 243, 'groups': 193, 'papers_with_zero_groups': 68, 'deterministic_pass': 103, 'rejected_pre_review': 90, 'rejection_reason_counts_incl_combos': {'span_reslice_pass': 76, 'concept_location_pass': 9, 'place_location_pass': 10}}
- `triage`: ['C-199098498-01', 'C-226260658-01', 'C-236782701-01', 'C-245473445-01', 'C-247623438-01', 'C-247866001-01', 'C-247866001-02', 'C-253196482-01', 'C-254679818-01', 'C-4238342-01', 'C-5882914-01']
- `copy_recheck_candidates`: 193
- `doc_sha256`: 541da3ce059cca4c4b0ce5ed33879a6d8a0ee82bbdb64b19eb54cef2023783ce
