# Run record: 20261020T221017Z_local_wp4_claim_screens

- **Result**: PASS
- **UTC timestamp**: 2026-10-20T22:10:17.213750+00:00
- **Git commit**: `d90595c0d85271e7665ee15b9d14a234a768e1a8`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 32
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/literature/wp4_sample.json`
- **Data SHA-256**: `f3cb5d0c3c4e0598860b2dad5a66219a3c252a92a7800d193111dec21fdcea15`
- **Output path**: `artifacts/literature/wp4_claim_screens.json`

## Config snapshot

```json
{
  "inputs": {
    "artifacts/literature/wp4_sample.json": "f3cb5d0c3c4e0598860b2dad5a66219a3c252a92a7800d193111dec21fdcea15",
    "artifacts/literature/wp4_claims_summary.json": "e062f05086185ef2616fe5c47ca8fe4d294e389055b4725160737a9a364c9b02",
    "data/metadata/concept_map.yaml": "27f7a44deabf24c244f1222c28d17c5c43fd86b9c017d4634bf0eef00931d7b4"
  }
}
```

## Result summary

- `claims`: 83
- `us_geography`: 42
- `us_geography_explicit`: 41
- `us_geography_inferred`: 1
- `us_geography_by_type`: {'background_citation': 12, 'finding': 26, 'mechanism': 1, 'projection': 1, 'recommendation': 2}
- `pilot_family_term_in_concept`: 8
- `pilot_family_term_in_concept_by_family`: {'fire_weather_index': 4, 'heat_index': 4}
- `pilot_family_term_and_us_geography`: 5
- `scenario_not_unknown`: 2
- `scenario_named`: 0
