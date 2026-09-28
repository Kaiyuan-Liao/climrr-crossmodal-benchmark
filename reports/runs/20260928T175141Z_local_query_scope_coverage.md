# Run record: 20260928T175141Z_local_query_scope_coverage

- **Result**: PASS
- **UTC timestamp**: 2026-09-28T17:51:41.091143+00:00
- **Git commit**: `e359b26c0b2f4708627420eae03e393f815485c4`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 9
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `data/metadata/literature_query.txt`
- **Data SHA-256**: `5a7ddf537d343b73fa0887e5f11ffbe3965fd25811f2adfc25cacee66f0ee1e5`
- **Output path**: `artifacts/literature/query_scope_coverage.json`

## Config snapshot

```json
{
  "collection query (pinned)": "data/metadata/literature_query.txt",
  "parsed query (derived)": "artifacts/literature/query_parsed.json",
  "prototype P-CELL-1": "artifacts/phenomena/prototypes/P-CELL-1.json",
  "prototype P-COUNTY-1": "artifacts/phenomena/prototypes/P-COUNTY-1.json",
  "prototype P-STATE-1": "artifacts/phenomena/prototypes/P-STATE-1.json",
  "pilot families": "docs/PILOT_SUBSET.md"
}
```

## Result summary

- `per_prototype_counts`: {'P-CELL-1': {'exact_query_term': 1, 'normalized_lexical_match': 0, 'absent_from_query': 3}, 'P-COUNTY-1': {'exact_query_term': 1, 'normalized_lexical_match': 0, 'absent_from_query': 3}, 'P-STATE-1': {'exact_query_term': 1, 'normalized_lexical_match': 0, 'absent_from_query': 3}}
- `family_counts`: {'exact_query_term': 0, 'normalized_lexical_match': 0, 'absent_from_query': 4}
- `hazard_groups_without_pilot_counterpart`: ['HG-02', 'HG-03', 'HG-04', 'HG-06', 'HG-07', 'HG-08', 'HG-09', 'HG-10', 'HG-11']
- `context_terms_matched`: []
- `categories_emitted`: ['absent_from_query', 'exact_query_term']
