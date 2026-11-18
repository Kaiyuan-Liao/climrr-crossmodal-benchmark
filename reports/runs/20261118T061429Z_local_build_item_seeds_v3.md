# Run record: 20261118T061429Z_local_build_item_seeds_v3

- **Result**: PASS
- **UTC timestamp**: 2026-11-18T06:14:29.703140+00:00
- **Git commit**: `69b3a22b88d0dad2a9b4ecdd038d41062732b9ae`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 4
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/item_seeds_v2.jsonl`
- **Data SHA-256**: `3123dd3463f23555601d1e64edc172e2977e2fc6df3adbb08a74b5df41be9d50`
- **Output path**: `artifacts/benchmark/item_seeds_v3.jsonl`

## Config snapshot

```json
{
  "rule": "DR-SEED-1 v3",
  "decisions": [
    "D-059",
    "D-061",
    "D-064"
  ],
  "version": "itemseeds v3",
  "retired_levels": {
    "1": "D-059",
    "7": "D-061"
  },
  "resolutions_sha256": "d86e1cd4e92ab51562ec251c98652d135280a52642012f6c94f3e2d02595869a",
  "seeds_v2_sha256": "3123dd3463f23555601d1e64edc172e2977e2fc6df3adbb08a74b5df41be9d50",
  "working_assumptions": [
    "WA-FWI-PCT-SCENARIO",
    "WA-FWI-SUMMER",
    "WA-NAME-LABEL",
    "WA-STATE-LABEL",
    "WA-UNWEIGHTED-MEAN"
  ],
  "fwi_shortlist_version": "pilot_shortlist fwi v1",
  "model_calls": 0
}
```

## Result summary

- `seeds`: 2812
- `eligible`: 2720
- `eligible_v2`: 2368
- `eligible_by_family`: {'fire_weather_index': 1404, 'heat_index': 1316}
- `eligible_by_level`: {'3': 2692, '4': 28}
- `became_eligible`: 352
- `became_ineligible`: 0
- `fwi`: {'seeds': 1404, 'acceptance_blocked_v2': 352, 'acceptance_blocked_v3': 0, 'eligible': 1404, 'eligible_fwi_summer_seasonal_value': 352}
- `heat_index`: {'seeds': 1408, 'eligible': 1316}
- `eligible_by_working_assumption`: {'WA-FWI-PCT-SCENARIO': 1052, 'WA-FWI-SUMMER': 352, 'WA-STATE-LABEL': 2676, 'WA-UNWEIGHTED-MEAN': 1642}
- `blockers_replaced`: {'IC-006 -> WA-FWI-SUMMER': 352, 'IC-007 -> WA-FWI-SUMMER': 352, 'IC-008 -> WA-FWI-SUMMER': 352, 'IC-009 -> WA-FWI-SUMMER': 352, 'IC-010 -> WA-FWI-SUMMER': 352, 'IC-012 -> WA-STATE-LABEL': 2764}
- `blockers_remaining`: {}
- `fwi_shortlist`: {'version': 'pilot_shortlist fwi v1', 'path': 'artifacts/benchmark/pilot_shortlist_fwi_v1.csv', 'sha256': 'd16b540c73fa5975a7ce896327be66ae5e97a903c38e833af440b96599205920', 'rule': {'metric': 'fwi_summer_seasonal_value', 'statistic': 'absolute_change', 'horizons': ['mid', 'end'], 'geography_type': 'state', 'distinct_states': True, 'level': 3}, 'candidates': {'mid': 49, 'end': 49}, 'picks': [{'seed_id': 'SD2-TP1-01463', 'state': 'California', 'horizon': 'mid', 'seed_rank_key': 26, 'pattern_id': 'TP1-01463'}, {'seed_id': 'SD2-TP1-01654', 'state': 'Minnesota', 'horizon': 'end', 'seed_rank_key': 162, 'pattern_id': 'TP1-01654'}]}
- `seeds_sha256`: 04602e1bce5bc205ab6ae0d179f866ce894cfc517be62f2039fdc9c393f9d8a5
- `summary_sha256`: 255c182d0023e4811ee52e52d0ec0e172b38fef99c205edab0abbe82c2a1b13c
