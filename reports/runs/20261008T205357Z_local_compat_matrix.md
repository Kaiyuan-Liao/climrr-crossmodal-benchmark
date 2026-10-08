# Run record: 20261008T205357Z_local_compat_matrix

- **Result**: PASS
- **UTC timestamp**: 2026-10-08T20:53:57.283292+00:00
- **Git commit**: `16dbb4322063f170686ecaf2252cbfa33dfbeca8`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 2
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/bridges/m5wp1_inputs.json`
- **Data SHA-256**: `bc22b4fa9344283fd31e9b7ac1f70fa53276d8dd171d6749933a4cf0b6a628cc`
- **Output path**: `artifacts/bridges/m5wp1_matrix.json`

## Config snapshot

```json
{
  "geo_disjoint_list": "config/geo_disjoint_list.yaml",
  "geo_disjoint_list_sha256": "2bdd67551699f4862b6afb32ae3c7bf1aca1a949c54501faadce241089439994",
  "t2_cutoff_year": 2045,
  "approved_concept_mappings": {}
}
```

## Result summary

- `n_pairs`: 81
- `n_all_compatible`: 0
- `n_pairs_with_any_incompatible`: 39
- `incompatible_by_rule`: {'G-2': 39, 'T-2': 14}
- `per_dimension`: {'concept': {'compatible': 0, 'incompatible': 0, 'not_evaluable': 81}, 'geography': {'compatible': 0, 'incompatible': 39, 'not_evaluable': 42}, 'time': {'compatible': 0, 'incompatible': 14, 'not_evaluable': 67}, 'scenario': {'compatible': 0, 'incompatible': 0, 'not_evaluable': 81}, 'direction': {'compatible': 0, 'incompatible': 0, 'not_evaluable': 81}}
- `matrix_json_sha256`: 526ac573f58a027c53b99e90a88fc7b3509c550afe205a9d6f15f74072d4cd02
- `matrix_csv_sha256`: cc7139f342e5dc5fe07e3b6583547b173e0cd1c08ca63d4983568de07ade8031
- `doc_sha256`: 4b354a089472d3722bdb1bef218a0c92a32352c93a2736ab668b66318f48c7b2
- `stop_all_compatible_found`: False
