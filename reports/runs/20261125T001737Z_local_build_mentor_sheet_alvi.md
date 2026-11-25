# Run record: 20261125T001737Z_local_build_mentor_sheet_alvi

- **Result**: PASS
- **UTC timestamp**: 2026-11-25T00:17:37.729290+00:00
- **Git commit**: `2b2334f9e78d519a18775d0d5d5e261ad7465382`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 2
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/synth_packets_infra_v1b/manifest.json`
- **Data SHA-256**: `b4cbbdb308ab90b5cd68a761009d88431315099aa9bb31acb9bd496061736a3e`
- **Output path**: `artifacts/benchmark/review/ALVI_SAMPLE_ITEMS_2026-11-25.md`

## Config snapshot

```json
{
  "audience": "alvi",
  "packets_manifest_sha256": "b4cbbdb308ab90b5cd68a761009d88431315099aa9bb31acb9bd496061736a3e",
  "items_manifest_sha256": "77be2faee83575cfaa69754676d1749ee56d8adde4e8373fb6d5183c9f996fbf",
  "items_dir": "artifacts/benchmark/items/infra_run2",
  "sheet": "2026-11-25",
  "edits": "artifacts/benchmark/review/P5_display_edits_v1.yaml",
  "model_calls": 0
}
```

## Result summary

- `audience`: alvi
- `rows`: 6
- `order`: ['BI-P5-0001', 'BI-P5-0002', 'BI-P5-0004', 'BI-P5-0006', 'BI-P5-0007', 'BI-P5-0008']
- `display_source`: {'BI-P5-0001': {'base': 'original', 'sheet': 'coordinator_edit'}, 'BI-P5-0002': {'base': 'polished', 'sheet': 'coordinator_edit'}, 'BI-P5-0004': {'base': 'original', 'sheet': 'coordinator_edit'}, 'BI-P5-0006': {'base': 'original', 'sheet': 'original'}, 'BI-P5-0007': {'base': 'original', 'sheet': 'coordinator_edit'}, 'BI-P5-0008': {'base': 'original', 'sheet': 'original'}}
- `md_sha256`: 0bf132b41e6b2ff0de5e9d16fb821b64a95c65fe75d42b7a018d5bcd90dab2fe
- `xlsx_sha256`: e9e04896e6d523028995bd1ed29999b995b92f691fc35dd2200c4d01190c00e7
- `edits_sha256`: a44e89307d6f877c7480e6da164995702878f45123690f535c41b1572c44bb8e
- `checks_sha256`: 00433bcf03f27cc2b5720bfab96149fe15d36e508569a9fe3b72d70b6f216287
- `leakage_failures`: 0
- `post_check_failures`: 3
- `items_failing`: ['BI-P5-0001', 'BI-P5-0002', 'BI-P5-0004']
- `failures_with_closing_clause_reverted`: 0
- `notes_sha256`: aa312849ccc2c832054794a8cacab75de39af935132b5f781b34b4adae878441
