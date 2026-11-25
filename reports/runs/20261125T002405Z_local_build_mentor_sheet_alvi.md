# Run record: 20261125T002405Z_local_build_mentor_sheet_alvi

- **Result**: PASS
- **UTC timestamp**: 2026-11-25T00:24:05.951141+00:00
- **Git commit**: `d27392e32dc513f257278b957dbcec94bb7fa376`
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
- `md_sha256`: abf1adc5c7d758f9013574cdaeb7e4165dc28ab0cc325e22bb87e59bd3324465
- `xlsx_sha256`: 2685a089297c045a0ce3a2f6558ca34191b17c1c4745d3856d5810ec91b6e886
- `edits_sha256`: 46b1c3c7d6a534a0afd3af6b4c04b58c231966a997d4ac0437b62712243ed936
- `checks_sha256`: 99c3da69bd5362c3ebdbf1fe2ec25fbb3269a990270590a26f3c664b859363db
- `leakage_failures`: 0
- `post_check_failures`: 0
- `items_failing`: []
- `notes_sha256`: 502cff8ce481a4087c88687e347113bdf9179b8696447353c24a3fc2677399f2
