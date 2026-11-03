# Run record: 20261103T232846Z_local_build_mentor_pilot_items

- **Result**: PASS
- **UTC timestamp**: 2026-11-03T23:28:46.645788+00:00
- **Git commit**: `7825fcfc487608224fbaac5c406b62f8f61c2bc4`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 4
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/items/index.json`
- **Data SHA-256**: `b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804`
- **Output path**: `artifacts/benchmark/review/MENTOR_PILOT_ITEMS_2026-11-05.md`

## Config snapshot

```json
{
  "items_index_sha256": "b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804",
  "coordinator_edits_v2_sha256": "a1b011d4179c9c57eb3a05911e15b6264a84bde6726c43a9c673faf729c19ebf",
  "support_map_v2_sha256": "bde0db83e8704e70b20c1960e18c04aa12b21393e516580d64ef1c537982fd3d",
  "statements_sha256": "26ba676c004adb0bdb7018b0e748b30f0d8eee0225c968e48786fecb2742a15f",
  "corrections_sha256": "ea981346b7fa271da1ee2ecadce125b9502cbac2caee31d74b653653c06282f1",
  "corrections_applied_sha256": "9bbd39d924ab3314929b6fc54c2d67244ebfc76efe1d4ddf61ede85491d5e3c5",
  "descriptor_rules_v2_sha256": "1e5554150b160f994009167d99f4a4afe79645cc55b26829e916c47777ce2ab7",
  "table_patterns_sha256": "ed3c2154818fc363e982b17e0dcb9bb1a2d2ca25e18de97fda6d353974bbf3b0",
  "passage_max_chars": 700,
  "model_calls": 0
}
```

## Result summary

- `md_sha256`: 8362d765d8292f29aa8a6fd2a3d463d730c93dfe9b319ae3894776ea0766da22
- `xlsx_sha256`: 0a9df82ea70ed81fa883064dbdb41b4fc6d1c9a97b1a43e352b92b589649af1e
- `checks_sha256`: f1c883cf3588e4e608d82ea880c4394b68e80aff98df27b70756c103da090d25
- `rows`: 5
- `items`: ['BI-P2B-0001', 'BI-P2B-0003', 'BI-P2B-0006', 'BI-P2B-0007', 'BI-P2B-0010']
- `leakage_v2_3_hits`: []
- `clause_verdicts`: {'guardrail': 2, 'partially_supported': 5, 'supported': 17, 'supported_by_uncited_packet_group': 3}
- `not_fully_supported`: {'partially_supported': [{'item_id': 'BI-P2B-0003', 'clause': 'Warming is the main driver'}, {'item_id': 'BI-P2B-0003', 'clause': 'One study suggests that land–atmosphere feedbacks appear to be a stronger factor in sustaining heat waves in the Southwest.'}, {'item_id': 'BI-P2B-0010', 'clause': 'Warming is the main driver'}, {'item_id': 'BI-P2B-0010', 'clause': 'The change is scenario-dependent'}, {'item_id': 'BI-P2B-0010', 'clause': 'one study of the eastern United States reports heat-wave duration almost one day longer under RCP8.5 than under the moderate RCP4.5 scenario.'}], 'supported_by_uncited_packet_group': [{'item_id': 'BI-P2B-0003', 'clause': 'global warming is expected to increase the frequency, intensity and duration of heat waves'}, {'item_id': 'BI-P2B-0006', 'clause': 'Because the heat index combines temperature and humidity'}, {'item_id': 'BI-P2B-0007', 'clause': 'global warming is expected to raise heat-wave frequency, intensity and duration'}]}
- `reslices`: {'LS-199098498-04': 'pending_polaris'}
- `descriptors_v2_changed`: {'BI-P2B-0006': ['anchor_pair', 'magnitude_class', 'magnitude_note'], 'BI-P2B-0007': ['negligible_regions', 'smallest']}
