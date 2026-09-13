# Run record: 20260913T200830Z_local_build_phenomenon_prototypes

- **Result**: PASS
- **UTC timestamp**: 2026-09-13T20:08:30.754281+00:00
- **Git commit**: `248ec9081e9998b246d3648b0be473c4a9f79d13`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `data/raw/FullData.csv`
- **Data SHA-256**: `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`
- **Output path**: `artifacts/phenomena/prototypes`

## Config snapshot

```json
{
  "data_path": "data/raw/FullData.csv",
  "coverage_path": "artifacts/profiles/dictionary_coverage.json",
  "inferred_candidates_path": "data/metadata/inferred_candidates.yaml",
  "out_dir": "artifacts/phenomena/prototypes",
  "schema_version": "p0-prototype",
  "prototypes": [
    "P-CELL-1",
    "P-COUNTY-1",
    "P-STATE-1"
  ],
  "variables": [
    "fwi_summer_hist_to_end85",
    "heatindex_day105_summer_hist_to_end85"
  ],
  "levels": [
    "cell",
    "county",
    "state"
  ]
}
```

## Result summary

- `schema_version`: p0-prototype
- `prototypes`: [{'record_id': 'P-CELL-1', 'level': 'cell', 'identifier': {'Crossmodel': 'R106C361'}, 'variable': 'fwi_summer_hist_to_end85', 'n_cells': '1', 'n_cells_with_value': '1', 'change_value': '6.109189990000000', 'direction': 'increase', 'percentile': '88.5253', 'tercile': 'upper_third', 'assumptions': ['A1', 'A-G0', 'A-DIR1', 'A-DIR2', 'A-H1', 'A-H3', 'A-H5', 'A-M1']}, {'record_id': 'P-COUNTY-1', 'level': 'county', 'identifier': {'State': 'Oklahoma', 'NAME': 'Stephens'}, 'variable': 'fwi_summer_hist_to_end85', 'n_cells': '10', 'n_cells_with_value': '10', 'change_value': '6.083151960000000', 'direction': 'increase', 'percentile': '90.6260', 'tercile': 'upper_third', 'assumptions': ['A1', 'A-G0', 'A-G1', 'A-G2', 'A-G3', 'A-AGG1', 'A-DIR1', 'A-DIR2', 'A-H1', 'A-H3', 'A-H5', 'A-M1']}, {'record_id': 'P-STATE-1', 'level': 'state', 'identifier': {'State': 'California'}, 'variable': 'heatindex_day105_summer_hist_to_end85', 'n_cells': '2831', 'n_cells_with_value': '2827', 'change_value': '13.209951652865228', 'direction': 'increase', 'percentile': '54.0000', 'tercile': 'middle_third', 'assumptions': ['A1', 'A-G0', 'A-G1', 'A-G2', 'A-G3', 'A-AGG1', 'A-DIR1', 'A-M1']}]
- `distribution_sizes`: {'cell:fwi_summer_hist_to_end85': 62834, 'cell:heatindex_day105_summer_hist_to_end85': 62751, 'county:fwi_summer_hist_to_end85': 3019, 'county:heatindex_day105_summer_hist_to_end85': 3018, 'state:fwi_summer_hist_to_end85': 50, 'state:heatindex_day105_summer_hist_to_end85': 50}
- `unlabelled_inferred_values`: none
