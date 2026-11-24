# Run record: 20261124T181709Z_local_build_synth_packets_infra

- **Result**: PASS
- **UTC timestamp**: 2026-11-24T18:17:09.265019+00:00
- **Git commit**: `79ceca873fe5cfcfb0a07b106183a2a1fd5490cb`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 4
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/pilot_selection_infra_v1.yaml`
- **Data SHA-256**: `0f42385ab51377637e523ed0e1323789690807e0c32f9cf744d2820ba26ae9e6`
- **Output path**: `artifacts/benchmark/synth_packets_infra_v1/manifest.json`

## Config snapshot

```json
{
  "version": "synthpackets infra v1",
  "decision": "D-076",
  "max_impact_groups": 10,
  "asset_class_phrase": {
    "energy": "energy systems",
    "transportation_systems": "transportation systems",
    "water_and_wastewater": "water and wastewater systems",
    "healthcare_and_public_health": "healthcare and public health systems",
    "emergency_services": "emergency services",
    "communications": "communications systems"
  },
  "model_calls": 0
}
```

## Result summary

- `packets`: [{'item_id': 'BI-P5-0001', 'packet_id': 'PK-SD8-TP1-00111-energy', 'family': 'heat_index', 'asset_class': 'energy', 'state': 'Virginia', 'question_form': 'QF-08', 'needs_general_clause': False, 'place_named_impact_evidence': 'place_named_impact_statement', 'excluded_groups': 62, 'sha256': '2342bcde080a9000f882e4ccb454b1acc06da7f83ab71491223392c0d9368851', 'impact_groups': 10, 'driver_groups': 8}, {'item_id': 'BI-P5-0002', 'packet_id': 'PK-SD8-TP1-00069-transportation_systems', 'family': 'heat_index', 'asset_class': 'transportation_systems', 'state': 'Arizona', 'question_form': 'QF-09', 'needs_general_clause': True, 'place_named_impact_evidence': 'place_named_impact_statement', 'excluded_groups': 46, 'sha256': 'b19f166744e25ebc4240ac03ebd58c424e0ee444b7fa466b699c29574bed2b27', 'impact_groups': 7, 'driver_groups': 8}, {'item_id': 'BI-P5-0003', 'packet_id': 'PK-SD8-TP1-00071-water_and_wastewater', 'family': 'heat_index', 'asset_class': 'water_and_wastewater', 'state': 'California', 'question_form': 'QF-10', 'needs_general_clause': True, 'place_named_impact_evidence': 'none', 'excluded_groups': 53, 'sha256': '82f08c67d2dfc044026b07b989cbad3bf23abe2722e71a15a3e38c766c32baae', 'impact_groups': 4, 'driver_groups': 8}, {'item_id': 'BI-P5-0004', 'packet_id': 'PK-SD8-TP1-00069-healthcare_and_public_health', 'family': 'heat_index', 'asset_class': 'healthcare_and_public_health', 'state': 'Arizona', 'question_form': 'QF-08', 'needs_general_clause': False, 'place_named_impact_evidence': 'place_named_impact_statement', 'excluded_groups': 46, 'sha256': '63c0fc0234b7ca640cab612aab879e47b9db940ed2cf854b67516e75012f28fa', 'impact_groups': 8, 'driver_groups': 8}, {'item_id': 'BI-P5-0005', 'packet_id': 'PK-SD8-TP1-01461-energy', 'family': 'fire_weather_index', 'asset_class': 'energy', 'state': 'Arizona', 'question_form': 'QF-09', 'needs_general_clause': False, 'place_named_impact_evidence': 'place_named_impact_statement', 'excluded_groups': 36, 'sha256': '4ffca91c33b2c2243e9999316b2c0f38a8401a34a6c7efb21ec6f8a11cc1c4a5', 'impact_groups': 10, 'driver_groups': 6}, {'item_id': 'BI-P5-0006', 'packet_id': 'PK-SD8-TP1-01463-transportation_systems', 'family': 'fire_weather_index', 'asset_class': 'transportation_systems', 'state': 'California', 'question_form': 'QF-10', 'needs_general_clause': False, 'place_named_impact_evidence': 'place_named_impact_statement', 'excluded_groups': 37, 'sha256': '03aa9a07205f6b156de33f17145042024a539415d7f9694d56dba707e1c68790', 'impact_groups': 7, 'driver_groups': 8}, {'item_id': 'BI-P5-0008', 'packet_id': 'PK-SD8-TP1-01463-communications', 'family': 'fire_weather_index', 'asset_class': 'communications', 'state': 'California', 'question_form': 'QF-08', 'needs_general_clause': False, 'place_named_impact_evidence': 'none', 'excluded_groups': 37, 'sha256': 'a6fa8401a54cc8112f95bc03a98a1a334f23e10f09adbebce6be21113368fb32', 'impact_groups': 1, 'driver_groups': 8}]
- `missing_cells`: [{'item_id': 'BI-P5-0007', 'family': 'fire_weather_index', 'asset_class': 'emergency_services', 'state': 'California', 'reason': 'no seed (no usable impact group of this family and class)'}]
- `manifest_sha256`: 1aba0b10b91062b36d416a84d68320157e9b18d0a407969f12b1c4c695972eeb
