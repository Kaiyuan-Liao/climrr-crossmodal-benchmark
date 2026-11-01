# Run record: 20261101T184950Z_local_build_item_seeds

- **Result**: PASS
- **UTC timestamp**: 2026-11-01T18:49:50.920428+00:00
- **Git commit**: `feac6465b55c8f985f9cf403983ffbea293b40e2`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 4
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/table_patterns_v1.jsonl`
- **Data SHA-256**: `ed3c2154818fc363e982b17e0dcb9bb1a2d2ca25e18de97fda6d353974bbf3b0`
- **Output path**: `artifacts/benchmark/item_seeds_v1.jsonl`

## Config snapshot

```json
{
  "rule": "DR-SEED-1",
  "version": "itemseeds v1",
  "clusters_sha256": "11bc074c6ef0a04a953e18e90febc1cfaef2d6bb9b9b7ebb5cfb7b79dfed556a",
  "nca_map_sha256": "3141b12201cd5a8d25789182688e69ed3792f4fa56ca667994247c82bf949a41",
  "model_calls": 0
}
```

## Result summary

- `seeds`: 2812
- `eligible`: 1316
- `eligible_without_diagnostic_pair`: 24
- `eligible_not_computable_excluded`: 92
- `by_level`: {3: 2784, 4: 28}
- `eligible_by_level`: {3: 1300, 4: 16}
- `levels_applicable`: {3: 2812, 4: 28, 7: 2812}
- `by_family`: {'fire_weather_index': 1404, 'heat_index': 1408}
- `eligible_by_family`: {'heat_index': 1316}
- `fwi`: {'seeds': 1404, 'acceptance_blocked': 352, 'not_blocked': 1052, 'eligible': 0}
- `eligible_cluster_ids`: {'LC-extreme_heat_v1-driver-006': 24, 'LC-extreme_heat_v1-driver-071': 1316}
- `seeds_sha256`: 3764eba645c84008453678b236e610a7ee2dff105404946c92e90ae3093beb32
- `summary_sha256`: c274c66022abfcfb3fc3e6a7210e6a25ce1340955e2258d95de579e70413ce53
