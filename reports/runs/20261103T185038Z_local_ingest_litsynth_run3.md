# Run record: 20261103T185038Z_local_ingest_litsynth_run3

- **Result**: PASS
- **UTC timestamp**: 2026-11-03T18:50:38.156444+00:00
- **Git commit**: `37c703714c7a8fc52b9e2b64e10890c54bd72ee6`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `litsynth_run3_evidence.tar.gz`
- **Data SHA-256**: `10dc8a43c7fafcab5b53a097304c5f563ca4bcbbac574cf47efce5071f8ddc54`
- **Output path**: `artifacts/benchmark/items/run3`

## Config snapshot

```json
{
  "source": "litsynth_run3_evidence.tar.gz (extracted)",
  "source_tarball_sha256": "10dc8a43c7fafcab5b53a097304c5f563ca4bcbbac574cf47efce5071f8ddc54",
  "packets": "synthpackets v3b at 157c96cffbe28b95554210efb0e8d455f62dba43",
  "check_version": "synthesis_post_checks v2.2",
  "run_executed_on": "Polaris; this record is the local ingest, not the run",
  "model_calls": 0
}
```

## Result summary

- `manifest_sha256`: edb48bfc7d873afe71c75fa251d71981e4508117c5c9f9cf4993d8f53b89916f
- `index_sha256`: b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804
- `files_copied_this_run`: 0
- `files_in_manifest`: 3
- `excluded_files`: 2
- `counts`: {'items': 1, 'deterministic_pass': 1, 'deterministic_fail': 0, 'leakage_flags': 0, 'corrective_retry_used': 0, 'format_corrective_used': 0, 'format_corrective_pass': 0}
- `checks_reproduced`: True
- `index_counts`: {'items': 10, 'current_by_run': {'run2': 9, 'run3': 1}, 'superseded': 1}
- `items`: [{'item_id': 'BI-P2B-0010', 'sha256': '421ad1069533835a8af69abedd21529d7b503173901ef7b89b70baf793ff55de', 'status': 'human_review'}]
- `superseded`: [{'item_id': 'BI-P2B-0010', 'run': 'run2', 'index_status': 'superseded_by_run3'}]
