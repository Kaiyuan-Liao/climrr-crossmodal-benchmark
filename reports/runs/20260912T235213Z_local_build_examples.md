# Run record: 20260912T235213Z_local_build_examples

- **Result**: PASS
- **UTC timestamp**: 2026-09-12T23:52:13.623589+00:00
- **Git commit**: `ccd512bec07ee26cdb7dadd7c047a0141bfb02c4`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 8
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `data/raw/FullData.csv`
- **Data SHA-256**: `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`
- **Output path**: `artifacts/examples`

## Config snapshot

```json
{
  "data_path": "data/raw/FullData.csv",
  "coverage_path": "artifacts/profiles/dictionary_coverage.json",
  "inferred_candidates_path": "data/metadata/inferred_candidates.yaml",
  "out_dir": "artifacts/examples",
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
  "selection_rules": [
    "R-A",
    "R-B",
    "R-C"
  ]
}
```

## Result summary

- `pilot_columns`: 41
- `pilot_status_counts`: {'verified_from_dictionary': 21, 'inferred_candidate': 20}
- `inferred_candidate_records`: 20
- `examples_written`: 3
- `examples`: [{'rule': 'R-A', 'OID_': '1', 'Crossmodel': 'R106C361', 'row_ordinal': 0, 'GEOID': '40137000902', 'blank_pilot_columns': 0, 'inferred_columns_used': 20, 'assumptions': 23, 'path': 'artifacts/examples/example_1.json'}, {'rule': 'R-B', 'OID_': '14', 'Crossmodel': 'R107C232', 'row_ordinal': 13, 'GEOID': '06071010300', 'blank_pilot_columns': 0, 'inferred_columns_used': 20, 'assumptions': 23, 'path': 'artifacts/examples/example_14.json'}, {'rule': 'R-C', 'OID_': '148', 'Crossmodel': 'R105C198', 'row_ordinal': 147, 'GEOID': '06111990100', 'blank_pilot_columns': 17, 'inferred_columns_used': 20, 'assumptions': 23, 'path': 'artifacts/examples/example_148.json'}]
- `unlabelled_inferred_values`: none
