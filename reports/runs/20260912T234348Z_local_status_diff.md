# Run record: 20260912T234348Z_local_status_diff

- **Result**: PASS
- **UTC timestamp**: 2026-09-12T23:43:48.468000+00:00
- **Git commit**: `391b442120081824bdde0517baf3c3f41b96a6b9`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 4
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/profiles/dictionary_coverage.json`
- **Data SHA-256**: `fea9e114983768f0277b1151bfba63ad819d75bc4204a3584a758e302c4cc7c4`
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
- `coverage_sha256`: fea9e114983768f0277b1151bfba63ad819d75bc4204a3584a758e302c4cc7c4
- `resolutions_sha256`: 8d8d194638d1e2ac5264ddffbc296b908a1aa406c77467939c9f5c4ed6294ac9
- `resolutions_applied`: 2
- `inferred_candidates_sha256`: 7a1e04147b549a46e59c1c6c1309b4bc71ebc9294f034ce76551ea70051a49d4
- `inferred_candidates_applied`: 20
- `columns_changed`: 20
- `changes`: [{'index': 2, 'column': 'NAME', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-011'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 3, 'column': 'State', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-012'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 4, 'column': 'State_Abbr', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-013'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 44, 'column': 'tempmaxann_hist', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-018'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 48, 'column': 'tempmaxann_rcp85_endc', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-019'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 52, 'column': 'tempmaxann_end85_hist', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-020'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 106, 'column': 'X', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-014'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 107, 'column': 'Y', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-015'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 108, 'column': 'TRACTCE', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-016'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 109, 'column': 'GEOID', 'from': 'structurally_observed_only', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-017'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 189, 'column': 'wildfire_summer_Hist', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-006'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 190, 'column': 'wildfire_summer_Midc', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-007'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 191, 'column': 'wildfire_summer_Endc', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-008'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 192, 'column': 'wildfire_summer_Dmid', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-009'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 193, 'column': 'wildfire_summer_Dend', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-010'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 238, 'column': 'heatindex_HIS_DayMax', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-001'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 244, 'column': 'heatindex_M85_DayMax', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-002'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 250, 'column': 'heatindex_E85_DayMax', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-003'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 256, 'column': 'heatindex_C_M85_DMax', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-004'], 'decision_refs': ['D-011'], 'resolved_section': None}, {'index': 262, 'column': 'heatindex_C_E85_DMax', 'from': 'partially_resolved', 'to': 'inferred_candidate', 'resolution_refs': [], 'inferred_candidate_refs': ['IC-005'], 'decision_refs': ['D-011'], 'resolved_section': None}]
- `baseline_status_counts`: {'structurally_observed_only': 83, 'verified_from_dictionary': 21, 'partially_resolved': 143, 'unresolved': 28}
- `current_status_counts`: {'structurally_observed_only': 76, 'verified_from_dictionary': 21, 'inferred_candidate': 20, 'partially_resolved': 130, 'unresolved': 28}
- `invariant_violations`: none
