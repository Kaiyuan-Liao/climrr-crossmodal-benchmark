# Run record: 20260928T175016Z_local_parse_literature_query

- **Result**: PASS
- **UTC timestamp**: 2026-09-28T17:50:16.723043+00:00
- **Git commit**: `e359b26c0b2f4708627420eae03e393f815485c4`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 6
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `data/metadata/literature_query.txt`
- **Data SHA-256**: `5a7ddf537d343b73fa0887e5f11ffbe3965fd25811f2adfc25cacee66f0ee1e5`
- **Output path**: `artifacts/literature/query_parsed.json`

## Config snapshot

```json
{
  "query_path": "data/metadata/literature_query.txt",
  "out_path": "artifacts/literature/query_parsed.json"
}
```

## Result summary

- `parser_version`: litquery-1
- `boolean_structure`: AND( OR(hazard groups HG-01..HG-11), OR(context terms CT-01..CT-22) )
- `n_hazard_groups`: 11
- `n_hazard_terms`: 80
- `n_context_terms`: 22
- `n_terms`: 102
- `n_quoted`: 64
- `n_bare`: 38
- `round_trip_passed`: True
- `absence_checks`: {'AR-1-scenario-horizon': 'absent', 'AR-2-us-state': 'absent', 'AR-3-geographic-unit': 'absent'}
