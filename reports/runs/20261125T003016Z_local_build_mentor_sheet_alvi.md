# Run record: 20261125T003016Z_local_build_mentor_sheet_alvi

- **Result**: PASS
- **UTC timestamp**: 2026-11-25T00:30:16.331020+00:00
- **Git commit**: `5df121ec41e8da20ab0dea0c6323adcf87fa6a51`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
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
- `display_source`: {'BI-P5-0001': {'base': 'original', 'sheet': 'coordinator_edit'}, 'BI-P5-0002': {'base': 'polished', 'sheet': 'coordinator_edit'}, 'BI-P5-0004': {'base': 'original', 'sheet': 'original'}, 'BI-P5-0006': {'base': 'original', 'sheet': 'original'}, 'BI-P5-0007': {'base': 'original', 'sheet': 'coordinator_edit'}, 'BI-P5-0008': {'base': 'original', 'sheet': 'original'}}
- `md_sha256`: 454ba2cb81c96b77005cbb4f6587a3f7ce6c07592081f16c9ce5d3b73a586d46
- `xlsx_sha256`: 8422e86141bacf906a1e575ba0a578bbd928e3613ef5b60f1ca667ed6a761318
- `edits_sha256`: 46b1c3c7d6a534a0afd3af6b4c04b58c231966a997d4ac0437b62712243ed936
- `checks_sha256`: 99c3da69bd5362c3ebdbf1fe2ec25fbb3269a990270590a26f3c664b859363db
- `leakage_failures`: 0
- `post_check_failures`: 0
- `items_failing`: []
- `notes_sha256`: 502cff8ce481a4087c88687e347113bdf9179b8696447353c24a3fc2677399f2
