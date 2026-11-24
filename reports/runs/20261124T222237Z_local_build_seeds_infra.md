# Run record: 20261124T222237Z_local_build_seeds_infra

- **Result**: PASS
- **UTC timestamp**: 2026-11-24T22:22:37.624949+00:00
- **Git commit**: `b443b3d9c57be6668b4e13e9073fb39d02e8e7cf`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `data/metadata/benchmark/group_dispositions_infra_v1.csv`
- **Data SHA-256**: `9b94e028bc571d9d84e6714ef1264bf2e087ea405d6561bfcdbd6d333c601bef`
- **Output path**: `artifacts/benchmark/item_seeds_infra_v1a.jsonl`

## Config snapshot

```json
{
  "rule": "DR-SEED-INFRA-1",
  "table_setting": {
    "heat_index": {
      "metric": "heatindex_days_above_95F",
      "statistic": "absolute_change",
      "horizon": "mid"
    },
    "fire_weather_index": {
      "metric": "fwi_summer_seasonal_value",
      "statistic": "absolute_change",
      "horizon": "mid"
    }
  },
  "pilot_cells": [
    [
      "heat_index",
      "energy"
    ],
    [
      "heat_index",
      "transportation_systems"
    ],
    [
      "heat_index",
      "water_and_wastewater"
    ],
    [
      "heat_index",
      "healthcare_and_public_health"
    ],
    [
      "fire_weather_index",
      "energy"
    ],
    [
      "fire_weather_index",
      "transportation_systems"
    ],
    [
      "fire_weather_index",
      "emergency_services"
    ],
    [
      "fire_weather_index",
      "communications"
    ]
  ],
  "fallback_state": "California",
  "geography": "litgeo v2",
  "model_calls": 0,
  "dispositions": "data/metadata/benchmark/group_dispositions_infra_v1.csv"
}
```

## Result summary

- `version`: seeds_infra v1a
- `rule`: DR-SEED-INFRA-1
- `decision`: D-075
- `seeds`: 686
- `by_family_class`: {'fire_weather_index|communications': 49, 'fire_weather_index|dams': 49, 'fire_weather_index|emergency_services': 49, 'fire_weather_index|energy': 49, 'fire_weather_index|healthcare_and_public_health': 49, 'fire_weather_index|transportation_systems': 49, 'fire_weather_index|water_and_wastewater': 49, 'heat_index|commercial_facilities': 49, 'heat_index|emergency_services': 49, 'heat_index|energy': 49, 'heat_index|healthcare_and_public_health': 49, 'heat_index|other': 49, 'heat_index|transportation_systems': 49, 'heat_index|water_and_wastewater': 49}
- `by_best_relevance`: {'general': 294, 'place_named': 8, 'us': 384}
- `seeds_file`: {'path': 'artifacts/benchmark/item_seeds_infra_v1a.jsonl', 'sha256': '0bd723a092c02eff84bb00e3b733baba1396787cdd8b5991b97b296c2037ea2a'}
- `selection_file`: {'path': 'artifacts/benchmark/pilot_selection_infra_v1a.yaml', 'sha256': '316a93f9d197d35756ef0c81a7a1e9f683978f59ce512615d93f0963134f9212'}
- `review_state`: impact_groups_reviewed
- `selected`: [{'order': 1, 'item_id': 'BI-P5-0001', 'family': 'heat_index', 'asset_class': 'energy', 'state': 'Virginia', 'state_basis': 'largest table change among states with a place-named impact statement', 'candidate_states': ['California', 'Virginia'], 'table_change': 12.461513001092198, 'place_named_impact_evidence': 'place_named_impact_statement', 'seed_id': 'SD8-TP1-00111-energy', 'question_form_id': 'QF-08', 'needs_general_clause': False}, {'order': 2, 'item_id': 'BI-P5-0002', 'family': 'heat_index', 'asset_class': 'transportation_systems', 'state': 'Arizona', 'state_basis': 'largest table change among states with a place-named impact statement', 'candidate_states': ['Arizona'], 'table_change': 10.271200803886398, 'place_named_impact_evidence': 'place_named_impact_statement', 'seed_id': 'SD8-TP1-00069-transportation_systems', 'question_form_id': 'QF-09', 'needs_general_clause': False}, {'order': 3, 'item_id': 'BI-P5-0003', 'family': 'heat_index', 'asset_class': 'water_and_wastewater', 'state': 'California', 'state_basis': 'fallback: no state with a place-named impact statement of this class', 'candidate_states': [], 'table_change': 8.983409978493102, 'place_named_impact_evidence': 'none', 'seed_id': 'SD8-TP1-00071-water_and_wastewater', 'question_form_id': 'QF-10', 'needs_general_clause': True}, {'order': 4, 'item_id': 'BI-P5-0004', 'family': 'heat_index', 'asset_class': 'healthcare_and_public_health', 'state': 'California', 'state_basis': 'fallback: no state with a place-named impact statement of this class', 'candidate_states': [], 'table_change': 8.983409978493102, 'place_named_impact_evidence': 'none', 'seed_id': 'SD8-TP1-00071-healthcare_and_public_health', 'question_form_id': 'QF-08', 'needs_general_clause': True}, {'order': 5, 'item_id': 'BI-P5-0005', 'family': 'fire_weather_index', 'asset_class': 'energy', 'state': 'California', 'state_basis': 'fallback: no state with a place-named impact statement of this class', 'candidate_states': [], 'table_change': 2.245804468117273, 'place_named_impact_evidence': 'none', 'seed_id': 'SD8-TP1-01463-energy', 'question_form_id': 'QF-09', 'needs_general_clause': True}, {'order': 6, 'item_id': 'BI-P5-0006', 'family': 'fire_weather_index', 'asset_class': 'transportation_systems', 'state': 'California', 'state_basis': 'fallback: no state with a place-named impact statement of this class', 'candidate_states': [], 'table_change': 2.245804468117273, 'place_named_impact_evidence': 'none', 'seed_id': 'SD8-TP1-01463-transportation_systems', 'question_form_id': 'QF-10', 'needs_general_clause': True}, {'order': 7, 'item_id': 'BI-P5-0007', 'family': 'fire_weather_index', 'asset_class': 'emergency_services', 'state': 'California', 'state_basis': 'fallback: no state with a place-named impact statement of this class', 'candidate_states': [], 'table_change': 2.245804468117273, 'place_named_impact_evidence': 'none', 'seed_id': 'SD8-TP1-01463-emergency_services', 'question_form_id': 'QF-08', 'needs_general_clause': True}, {'order': 8, 'item_id': 'BI-P5-0008', 'family': 'fire_weather_index', 'asset_class': 'communications', 'state': 'California', 'state_basis': 'fallback: no state with a place-named impact statement of this class', 'candidate_states': [], 'table_change': 2.245804468117273, 'place_named_impact_evidence': 'none', 'seed_id': 'SD8-TP1-01463-communications', 'question_form_id': 'QF-09', 'needs_general_clause': True}]
- `missing`: []
- `inputs`: {'item_seeds_v3': '04602e1bce5bc205ab6ae0d179f866ce894cfc517be62f2039fdc9c393f9d8a5', 'statements_ingested': '869b0592e72ec22b7617a3fbe6ae3005df762b4817f7609e41c96a8559cbca4b', 'independence_v2': 'b0a2fa3f3bd9998597c4681100586abf555ce295283984f102222030bd2fb602', 'groups': 'f61bf4f557c0f5fbdfec2779fc578b01e84bdc6edfca80c4b633d25f841045ce', 'question_forms_v2': '520aafa0804b5308be7e9e59b8316d9fbe0d8b60b335da4a0414ed0a17ab283e', 'dispositions': '9b94e028bc571d9d84e6714ef1264bf2e087ea405d6561bfcdbd6d333c601bef', 'groups_dispositioned': 'd92cd95ff9dcc669a4f19355d22ac556c8211a587bc7155b5fb6fea42ff091ce'}
- `decision_dispositions`: D-078
- `dispositions_log`: {'path': 'artifacts/litgroups/infra_run1/dispositions_v1_applied.json', 'sha256': '6c371c35f842d82c09716e11bf17651b6249ebef2223dea17042a650ae868624'}
