# Run record: 20261101T235302Z_local_build_group_partitions

- **Result**: PASS
- **UTC timestamp**: 2026-11-01T23:53:02.843021+00:00
- **Git commit**: `c1bb5e3c323a58077f471cd4aed44ea86c813f10`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 4
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/litstatements/run2/statements_ingested.jsonl`
- **Data SHA-256**: `b775301cbd3387f2228f07830fded009d9111d0ce635624123bc45a9f458eb81`
- **Output path**: `artifacts/litgroups/partitions_v1.jsonl`

## Config snapshot

```json
{
  "version": "litgroups partitions v1",
  "max_partition": 120,
  "family_phrase": {
    "extreme_heat_v1": "the heat index and humid heat",
    "fire_weather_v1": "fire weather and fire danger indices"
  },
  "model_calls": 0
}
```

## Result summary

- `version`: litgroups partitions v1
- `max_partition`: 120
- `partitions`: 11
- `statements`: 747
- `split`: [{'partition_id': 'extreme_heat_v1.mechanism.increase', 'split_by': ['direction=increase'], 'n_statements': 28, 'parent_n_statements': 144}, {'partition_id': 'extreme_heat_v1.mechanism.unspecified', 'split_by': ['direction=unspecified'], 'n_statements': 116, 'parent_n_statements': 144}]
- `sizes`: {'extreme_heat_v1.mechanism.increase': 28, 'extreme_heat_v1.mechanism.unspecified': 116, 'extreme_heat_v1.driver': 118, 'extreme_heat_v1.consensus': 15, 'extreme_heat_v1.caveat': 74, 'extreme_heat_v1.pattern': 65, 'fire_weather_v1.mechanism': 102, 'fire_weather_v1.driver': 106, 'fire_weather_v1.consensus': 11, 'fire_weather_v1.caveat': 66, 'fire_weather_v1.pattern': 46}
- `by_role`: {'background_consensus_candidate': 262, 'cited_candidate': 106, 'core_candidate': 379}
- `partitions_file`: {'path': 'artifacts/litgroups/partitions_v1.jsonl', 'sha256': 'e8d2bb45301244bf84a4c706a8be6ad3ceba4e1cdd4b09670ad46cedcd8e0f8b'}
- `inputs`: {'statements_ingested_sha256': 'b775301cbd3387f2228f07830fded009d9111d0ce635624123bc45a9f458eb81', 'independence_v2_sha256': '6b66417e16e3b6f38932214b1584a261ce36704d4c32dc7fb3bfcd46e6c5a34d', 'exclusions_sha256': '41bb50b7083297d412ad749088fc5ef5345000867e468088650b11621b2dce8f'}
