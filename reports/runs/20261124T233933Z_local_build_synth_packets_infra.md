# Run record: 20261124T233933Z_local_build_synth_packets_infra

- **Result**: PASS
- **UTC timestamp**: 2026-11-24T23:39:33.982012+00:00
- **Git commit**: `ca6f56f48bef2a2d8758bd44e362e7dc8a9ffd0d`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/synth_packets_infra_v1a/manifest.json`
- **Data SHA-256**: `829d80cfa3fdff217ddc19a2f2b8ffc97bf7b41cc7f1f869ecfa0daaf37e5bf2`
- **Output path**: `artifacts/benchmark/synth_packets_infra_v1b/manifest.json`

## Config snapshot

```json
{
  "version": "synthpackets infra v1b",
  "decision": "D-075a",
  "variant": "v1b",
  "answer_shape": "rung8_v2",
  "model_calls": 0
}
```

## Result summary

- `packets`: [{'item_id': 'BI-P5-0001', 'packet_id': 'PK-SD8-TP1-00111-energy', 'family': 'heat_index', 'asset_class': 'energy', 'state': 'Virginia', 'answer_shape': 'rung8_v2', 'asset_class_short_forms': ['the grid', 'power systems'], 'bridge_clause_required': False, 'sha256': '5ee73ad5c1618606faea44383a586a92d6525a9e8de438cd2dc9573e6904a025'}, {'item_id': 'BI-P5-0002', 'packet_id': 'PK-SD8-TP1-00069-transportation_systems', 'family': 'heat_index', 'asset_class': 'transportation_systems', 'state': 'Arizona', 'answer_shape': 'rung8_v2', 'asset_class_short_forms': ['roads and rail'], 'bridge_clause_required': False, 'sha256': '8bd43e0f45ff11ef4bd973f6e46899003c2cb09d0f8e5e430228d63b9119e192'}, {'item_id': 'BI-P5-0003', 'packet_id': 'PK-SD8-TP1-00071-water_and_wastewater', 'family': 'heat_index', 'asset_class': 'water_and_wastewater', 'state': 'California', 'answer_shape': 'rung8_v2', 'asset_class_short_forms': ['water systems'], 'bridge_clause_required': False, 'sha256': '4c6e3847b8f1983a45c1529b1aad51c0b43a3c85c9fe587416e3dce7bb772b5c'}, {'item_id': 'BI-P5-0004', 'packet_id': 'PK-SD8-TP1-00071-healthcare_and_public_health', 'family': 'heat_index', 'asset_class': 'healthcare_and_public_health', 'state': 'California', 'answer_shape': 'rung8_v2', 'asset_class_short_forms': ['hospitals and emergency services', 'hospitals'], 'bridge_clause_required': False, 'sha256': 'f304a5f1bd21355ef17c7786c32d39bd8fa7bdb9738462400320f52af1632c93'}, {'item_id': 'BI-P5-0005', 'packet_id': 'PK-SD8-TP1-01463-energy', 'family': 'fire_weather_index', 'asset_class': 'energy', 'state': 'California', 'answer_shape': 'rung8_v2', 'asset_class_short_forms': ['the grid', 'power systems'], 'bridge_clause_required': True, 'sha256': 'bf3c9aea49532108680b1c3c449624555e6625f9e836fff3c2e1679bbe675b3a'}, {'item_id': 'BI-P5-0006', 'packet_id': 'PK-SD8-TP1-01463-transportation_systems', 'family': 'fire_weather_index', 'asset_class': 'transportation_systems', 'state': 'California', 'answer_shape': 'rung8_v2', 'asset_class_short_forms': ['roads and rail'], 'bridge_clause_required': True, 'sha256': 'a688d1d6efde36da6c57e62fcd2d42f12c8ee9b1303bb079640811d021557817'}, {'item_id': 'BI-P5-0007', 'packet_id': 'PK-SD8-TP1-01463-emergency_services', 'family': 'fire_weather_index', 'asset_class': 'emergency_services', 'state': 'California', 'answer_shape': 'rung8_v2', 'asset_class_short_forms': ['emergency responders'], 'bridge_clause_required': False, 'sha256': '9f88f3cdd55e6cf10b7cbd86f9dd8d4c1f3c37e0f7f2bce95618f8ff7bc87a56'}, {'item_id': 'BI-P5-0008', 'packet_id': 'PK-SD8-TP1-01463-communications', 'family': 'fire_weather_index', 'asset_class': 'communications', 'state': 'California', 'answer_shape': 'rung8_v2', 'asset_class_short_forms': ['communications networks'], 'bridge_clause_required': False, 'sha256': 'b43bd1c45b9c9616fe220069fd5eee4bbcefb5799fd10693cc87f16fa9273aef'}]
- `built_from_manifest_sha256`: 829d80cfa3fdff217ddc19a2f2b8ffc97bf7b41cc7f1f869ecfa0daaf37e5bf2
- `asset_short_forms_sha256`: de28eaa2d65759d7c09c2e95e8388b17f477f7c0f6d21aa72bcc3681055c444d
- `manifest_sha256`: b4cbbdb308ab90b5cd68a761009d88431315099aa9bb31acb9bd496061736a3e
