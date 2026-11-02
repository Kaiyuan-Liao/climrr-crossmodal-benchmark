# Run record: 20261102T002559Z_local_build_region_strings_v2

- **Result**: PASS
- **UTC timestamp**: 2026-11-02T00:25:59.291758+00:00
- **Git commit**: `1dd1b191e63a4a579bd23f9d5153a4ac5f8631d1`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/litstatements/run2/statements_ingested.jsonl`
- **Data SHA-256**: `b775301cbd3387f2228f07830fded009d9111d0ce635624123bc45a9f458eb81`
- **Output path**: `artifacts/litstatements/run2/region_strings_v2.csv`

## Config snapshot

```json
{
  "geo_version": "litgeo v2",
  "rule": "DR-SEED-1 v2 geography (D-047a)",
  "us_names": [
    "contiguous United States",
    "continental United States",
    "conterminous United States",
    "United States",
    "lower 48",
    "USA",
    "CONUS",
    "US",
    "U.S."
  ],
  "national_extent": [
    "conterminous",
    "contiguous",
    "continental",
    "entire",
    "mainland",
    "whole"
  ],
  "directional": [
    "central",
    "east",
    "eastern",
    "interior",
    "midwest",
    "midwestern",
    "north",
    "northeast",
    "northeastern",
    "northern",
    "northwest",
    "northwestern",
    "south",
    "southeast",
    "southeastern",
    "southern",
    "southwest",
    "southwestern",
    "upper",
    "west",
    "western"
  ],
  "regional": [
    "appalachia",
    "appalachian",
    "basin",
    "basins",
    "coast",
    "coastal",
    "coasts",
    "desert",
    "deserts",
    "ecoregion",
    "ecoregions",
    "gulf",
    "lakes",
    "mountain",
    "mountains",
    "plains",
    "region",
    "regional",
    "regions",
    "rockies",
    "rocky",
    "valley",
    "valleys"
  ],
  "exclusions_sha256": "41bb50b7083297d412ad749088fc5ef5345000867e468088650b11621b2dce8f",
  "model_calls": 0
}
```

## Result summary

- `version`: litgeo v2
- `rule`: DR-SEED-1 v2 geography (D-047a)
- `decisions`: D-047, D-047a
- `inputs`: {'statements_ingested_sha256': 'b775301cbd3387f2228f07830fded009d9111d0ce635624123bc45a9f458eb81', 'nca_map_sha256': '3141b12201cd5a8d25789182688e69ed3792f4fa56ca667994247c82bf949a41', 'exclusions_sha256': '41bb50b7083297d412ad749088fc5ef5345000867e468088650b11621b2dce8f'}
- `region_strings_file`: {'path': 'artifacts/litstatements/run2/region_strings_v2.csv', 'sha256': '44c84bb3e48c54b836a88f18ddecab5d7b22e179eb2b377df2438c1907c45635', 'rows_region_x_scope': 147, 'distinct_region_strings': 133}
- `entering_statements`: 747
- `statements_by_class`: {'us_national': 81, 'us_subregion': 46, 'state': 119, 'nca': 5, 'global': 118, 'other': 178, 'unknown': 200}
- `rows_by_class`: {'us_national': 13, 'us_subregion': 15, 'state': 27, 'nca': 5, 'global': 6, 'other': 78, 'unknown': 3}
- `distinct_strings_by_class`: {'us_national': 10, 'us_subregion': 13, 'state': 27, 'nca': 5, 'global': 6, 'other': 71, 'unknown': 2}
- `us_subregion_qualifiers`: {'dry ecoregions': 1, 'eastern': 5, 'northeastern and midwestern': 1, 'northern and central rocky mountains': 1, 'seasonally dry coniferous forests of the western': 1, 'southeastern': 16, 'southern': 1, 'southern southwestern and central': 1, 'upper midwestern': 1, 'western': 18}
- `d047_drops`: {'dropped_under_v1': 50, 'recovered_under_v2': 50, 'recovered_by_class': {'us_national': 13, 'us_subregion': 37}, 'not_recovered': [], 'transitions_v1_to_v2': {'other->us_national': 13, 'other->us_subregion': 37, 'us_national->us_subregion': 9}}
