# Run record: 20260913T191302Z_local_hierarchy_checks

- **Result**: PASS
- **UTC timestamp**: 2026-09-13T19:13:02.064309+00:00
- **Git commit**: `ad13649f46588899052244cee4a9a3fbc3dbd3e6`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 6
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `data/raw/FullData.csv`
- **Data SHA-256**: `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`
- **Output path**: `artifacts/profiles/hierarchy_checks.json`

## Config snapshot

```json
{
  "data_path": "data/raw/FullData.csv",
  "out_json": "artifacts/profiles/hierarchy_checks.json",
  "out_md": "artifacts/profiles/hierarchy_checks.md",
  "focus_oids": [
    "1",
    "14"
  ],
  "pilot_indices": [
    1,
    2,
    3,
    4,
    44,
    48,
    52,
    106,
    107,
    108,
    109,
    180,
    181,
    187,
    188,
    189,
    190,
    191,
    192,
    193,
    194,
    195,
    201,
    202,
    238,
    240,
    241,
    242,
    243,
    244,
    246,
    247,
    248,
    249,
    250,
    252,
    253,
    254,
    255,
    256,
    262
  ],
  "list_cap": 50
}
```

## Result summary

- `crossmodel_is_unique`: True
- `crossmodel_n_distinct`: 62834
- `n_state_name_pairs`: 3019
- `rows_in_pair_of_OID_1`: 10
- `n_geoid_keys`: 12941
- `each_geoid_one_state_name_pair`: False
- `n_geoid_spanning_multiple_pairs`: 3234
- `NAME_1_is_function_of_geoid`: True
- `NAMELSAD_is_function_of_geoid`: True
- `n_rows_with_empty_state`: 7
- `rows_in_state_of_OID_14`: 2831
