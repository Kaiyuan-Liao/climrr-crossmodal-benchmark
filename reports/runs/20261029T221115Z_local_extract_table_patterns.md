# Run record: 20261029T221115Z_local_extract_table_patterns

- **Result**: PASS
- **UTC timestamp**: 2026-10-29T22:11:15.375558+00:00
- **Git commit**: `8f06d2b3b5f56199fd74eff2fe7c3069eb319590`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `data/raw/FullData.csv`
- **Data SHA-256**: `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`
- **Output path**: `artifacts/benchmark/table_patterns_v1.jsonl`

## Config snapshot

```json
{
  "slots_sha256": "d40f835e969cc0dac0ed7de3affd1ce4ef26152a56252f042b7dbdf889b47e10",
  "nca_map_sha256": "3141b12201cd5a8d25789182688e69ed3792f4fa56ca667994247c82bf949a41",
  "coverage_sha256": "2547e8df4ba809c67e7afe386739d905c4573d6b4f0478d8aeef4807135a4ce4",
  "dictionary_text_sha256": "1d0fae06c6a5a9714fe890936d002cd0ac84829262465d4930d04acb400553da",
  "code_version": "table_patterns v1 (src/climrr/table_patterns.py sha256 c5948f7e0ef85b73)",
  "model_calls": 0
}
```

## Result summary

- `schema_version`: table-patterns-v1
- `n_patterns`: 2812
- `by_kind`: {'regional_contrast': 28, 'seasonal_contrast': 116, 'single': 2668}
- `by_family`: {'fire_weather_index': 1404, 'heat_index': 1408}
- `by_geography_type`: {'cell_control': 48, 'nca_region': 412, 'state': 2352}
- `by_statistic`: {'absolute_change': 590, 'direction': 1052, 'percent_change': 1054, 'seasonal_contrast': 116}
- `by_family_geography_statistic`: {'fire_weather_index|cell_control|absolute_change': 2, 'fire_weather_index|cell_control|direction': 10, 'fire_weather_index|cell_control|percent_change': 10, 'fire_weather_index|cell_control|seasonal_contrast': 2, 'fire_weather_index|nca_region|absolute_change': 18, 'fire_weather_index|nca_region|direction': 88, 'fire_weather_index|nca_region|percent_change': 82, 'fire_weather_index|nca_region|seasonal_contrast': 16, 'fire_weather_index|state|absolute_change': 98, 'fire_weather_index|state|direction': 490, 'fire_weather_index|state|percent_change': 490, 'fire_weather_index|state|seasonal_contrast': 98, 'heat_index|cell_control|absolute_change': 8, 'heat_index|cell_control|direction': 8, 'heat_index|cell_control|percent_change': 8, 'heat_index|nca_region|absolute_change': 72, 'heat_index|nca_region|direction': 64, 'heat_index|nca_region|percent_change': 72, 'heat_index|state|absolute_change': 392, 'heat_index|state|direction': 392, 'heat_index|state|percent_change': 392}
- `by_status`: {'computed': 2720, 'not_computable': 92}
- `by_authorization`: {'inferred_candidate': 352, 'verified': 2460}
- `n_acceptance_blocked`: 352
- `n_with_relative_tercile`: 686
- `tercile_groups_skipped`: 6
- `tercile_groups_skipped_by_reason`: {'missing_states_change_cut_points': 6}
- `n_single_state_patterns_without_tercile`: 1568
- `table_states`: ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
- `nca_states_not_in_table`: ['District of Columbia', 'Hawaii']
- `table_states_not_in_nca_map`: []
- `table_data_sha256`: e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e
- `patterns_file`: {'path': 'artifacts/benchmark/table_patterns_v1.jsonl', 'sha256': 'ed3c2154818fc363e982b17e0dcb9bb1a2d2ca25e18de97fda6d353974bbf3b0', 'bytes': 6773361, 'n_records': 2812}
- `nca_map_sha256`: 3141b12201cd5a8d25789182688e69ed3792f4fa56ca667994247c82bf949a41
- `code_version`: table_patterns v1 (src/climrr/table_patterns.py sha256 c5948f7e0ef85b73)
- `outputs`: {'data/metadata/templates/slots_v1.yaml': 'd40f835e969cc0dac0ed7de3affd1ce4ef26152a56252f042b7dbdf889b47e10', 'data/metadata/geography/nca_regions_v1.yaml': '3141b12201cd5a8d25789182688e69ed3792f4fa56ca667994247c82bf949a41', 'artifacts/profiles/dictionary_coverage.json': '2547e8df4ba809c67e7afe386739d905c4573d6b4f0478d8aeef4807135a4ce4', 'artifacts/benchmark/table_patterns_v1.jsonl': 'ed3c2154818fc363e982b17e0dcb9bb1a2d2ca25e18de97fda6d353974bbf3b0', 'artifacts/benchmark/table_patterns_v1_summary.json': 'fbec4c94298c9feda9c52705eba3c020ccaf36d1b08df659b30a56879f6f3b03', 'artifacts/benchmark/table_patterns_v1_examples.jsonl': 'c51707dc943443de38c44ac3123cc712910b5bad6c7a22df249d44c7767dc00c'}
