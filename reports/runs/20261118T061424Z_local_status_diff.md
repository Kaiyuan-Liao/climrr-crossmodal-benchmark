# Run record: 20261118T061424Z_local_status_diff

- **Result**: PASS
- **UTC timestamp**: 2026-11-18T06:14:24.118305+00:00
- **Git commit**: `69b3a22b88d0dad2a9b4ecdd038d41062732b9ae`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/profiles/dictionary_coverage.json`
- **Data SHA-256**: `4c633302c48768c82e78e6b7a8a80ab68266d31161bd8816acf7bfc52bcd8e27`
- **Output path**: `artifacts/profiles/status_diff.md`

## Config snapshot

```json
{
  "coverage_path": "artifacts/profiles/dictionary_coverage.json",
  "out_path": "artifacts/profiles/status_diff.md"
}
```

## Result summary

- `coverage_path`: artifacts/profiles/dictionary_coverage.json
- `coverage_sha256`: 4c633302c48768c82e78e6b7a8a80ab68266d31161bd8816acf7bfc52bcd8e27
- `resolutions_sha256`: d86e1cd4e92ab51562ec251c98652d135280a52642012f6c94f3e2d02595869a
- `resolutions_applied`: 8
- `inferred_candidates_sha256`: 62cd7a2d58a7657002bc668820b3ac9a25381fa6229ae30f195bd6aa5a0554d3
- `inferred_candidates_applied`: 20
- `columns_changed`: 20
- `changes`: [{'index': 2, 'column': 'NAME', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-011'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 3, 'column': 'State', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-012'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 4, 'column': 'State_Abbr', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-013'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 44, 'column': 'tempmaxann_hist', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-018'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 48, 'column': 'tempmaxann_rcp85_endc', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-019'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 52, 'column': 'tempmaxann_end85_hist', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-020'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 106, 'column': 'X', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-014'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 107, 'column': 'Y', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-015'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 108, 'column': 'TRACTCE', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-016'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 109, 'column': 'GEOID', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-017'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 189, 'column': 'wildfire_summer_Hist', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-006'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 190, 'column': 'wildfire_summer_Midc', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-007'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 191, 'column': 'wildfire_summer_Endc', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-008'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 192, 'column': 'wildfire_summer_Dmid', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-009'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 193, 'column': 'wildfire_summer_Dend', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-010'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 238, 'column': 'heatindex_HIS_DayMax', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-001'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 244, 'column': 'heatindex_M85_DayMax', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-002'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 250, 'column': 'heatindex_E85_DayMax', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-003'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 256, 'column': 'heatindex_C_M85_DMax', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-004'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 262, 'column': 'heatindex_C_E85_DMax', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-005'], 'decision_refs': ['D-011'], 'resolved_section': None}]
- `baseline_status_counts`: {'structurally_observed_only': 83, 'verified_from_dictionary': 21, 'partially_resolved': 143, 'unresolved': 28}
- `current_status_counts`: {'structurally_observed_only': 76, 'verified_from_dictionary': 21, 'inferred_candidate': 20, 'partially_resolved': 130, 'unresolved': 28}
- `invariant_violations`: none
