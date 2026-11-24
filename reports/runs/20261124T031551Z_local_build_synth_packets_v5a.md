# Run record: 20261124T031551Z_local_build_synth_packets_v5a

- **Result**: PASS
- **UTC timestamp**: 2026-11-24T03:15:51.483156+00:00
- **Git commit**: `e44a343597eb373ffa4d28cbad7fc34e7a87e64d`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/synth_packets_v5/manifest.json`
- **Data SHA-256**: `1f92c194411ea12152c6659058633bf250812bdb234328fa8f39fb81dd8ea0fd`
- **Output path**: `artifacts/benchmark/synth_packets_v5a/manifest.json`

## Config snapshot

```json
{
  "version": "synthpackets v5a",
  "decision": "D-069a",
  "base": "synthpackets v5",
  "plain_language": "data/metadata/benchmark/plain_language_v1b.yaml",
  "plain_language_sha256": "60598527bf21a9dbc5a68e31cb60ec76d75b95d5ede7411181c323f56832b140",
  "question_forms_sha256": "d123b381f6807a9b8d6cc9b6b901a86e8c48dfe617cb1f26ff9c6be9fdd4c910",
  "model_calls": 0
}
```

## Result summary

- `packets`: [{'packet_id': 'PK-SD2-TP1-00071', 'item_id': 'BI-P3-0001', 'needs_general_clause': False, 'classes_present': ['state', 'us_subregion', 'us_national', 'global', 'mixed'], 'sha256': '46091f48258f7d66e99475f320eb136d7ef2c4dc1540bbf81fefe3b49142e1b5'}, {'packet_id': 'PK-SD2-TP1-00271', 'item_id': 'BI-P3-0002', 'needs_general_clause': True, 'classes_present': ['us_subregion', 'us_national', 'global'], 'sha256': 'd5cca354c6b215f3f5606bbeae55f632dc93a1cc3f7c5fa67e9cf3a9c1659552'}, {'packet_id': 'PK-SD2-TP1-00460', 'item_id': 'BI-P3-0003', 'needs_general_clause': True, 'classes_present': ['us_subregion', 'us_national', 'global'], 'sha256': 'fdd8b709a7ffd3233be4dfcfca3b70f29db2c50e16dc3d31c41fcd8bad6ef8d0'}, {'packet_id': 'PK-SD2-TP1-00589', 'item_id': 'BI-P3-0004', 'needs_general_clause': True, 'classes_present': ['us_subregion', 'us_national', 'global'], 'sha256': 'f5947edc25a3615e1cf02704aaccf02389eaab09e3a925275557d4b6f4b6fda0'}, {'packet_id': 'PK-SD2-TP1-02785', 'item_id': 'BI-P3-0005', 'needs_general_clause': True, 'classes_present': ['us_subregion', 'us_national', 'global'], 'sha256': '6a3637d700b21aec5c38ea4dff6f2316a7c48a5f6f656bd1f5ed82b6ba2be297'}, {'packet_id': 'PK-SD2-TP1-01463', 'item_id': 'BI-P3-0007', 'needs_general_clause': False, 'classes_present': ['state', 'us_subregion', 'global', 'mixed'], 'sha256': '2deb6ddad4963568ad59e703313c83393bdda45cf01aa1788a01a028fc48c3d6'}, {'packet_id': 'PK-SD2-TP1-01654', 'item_id': 'BI-P3-0008', 'needs_general_clause': False, 'classes_present': ['state', 'us_subregion', 'global', 'mixed'], 'sha256': '7d5f87c52e7e2b6db3aec07a40385cf0b098b318a375f0034f9a24d95a153e01'}]
- `groups_changed_from_v5`: 11
- `v5_minority_cases`: [{'item_id': 'BI-P3-0001', 'group_id': 'LG-extreme_heat_v1-driver-c1-008', 'v5': 'Research on the Southwest shows', 'v5a': 'Research on the United States shows', 'clause': ', including work on the Southwest'}, {'item_id': 'BI-P3-0005', 'group_id': 'LG-extreme_heat_v1-driver-c1-008', 'v5': 'Research on the Southwest shows', 'v5a': 'Research on the United States shows', 'clause': ', including work on the Southwest'}, {'item_id': 'BI-P3-0007', 'group_id': 'LG-fire_weather_v1-mechanism-c1-003', 'v5': 'Research on California shows', 'v5a': 'In general, research shows', 'clause': ', including work on California'}, {'item_id': 'BI-P3-0007', 'group_id': 'LG-fire_weather_v1-driver-c1-002', 'v5': 'Research on California shows', 'v5a': 'In general, research shows', 'clause': ', including work on California'}, {'item_id': 'BI-P3-0007', 'group_id': 'LG-fire_weather_v1-driver-c1-005', 'v5': 'Research on California shows', 'v5a': 'In general, research shows', 'clause': ', including work on California'}]
- `needs_general_clause_v5`: {'BI-P3-0001': False, 'BI-P3-0002': True, 'BI-P3-0003': True, 'BI-P3-0004': True, 'BI-P3-0005': False, 'BI-P3-0007': False, 'BI-P3-0008': False}
- `needs_general_clause_v5a`: {'BI-P3-0001': False, 'BI-P3-0002': True, 'BI-P3-0003': True, 'BI-P3-0004': True, 'BI-P3-0005': True, 'BI-P3-0007': False, 'BI-P3-0008': False}
- `manifest_sha256`: 30c46fa15ee60a75817fd879fa7a2321ac91e472412100a6fbc53cb861c67de3
