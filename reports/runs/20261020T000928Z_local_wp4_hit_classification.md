# Run record: 20261020T000928Z_local_wp4_hit_classification

- **Result**: PASS
- **UTC timestamp**: 2026-10-20T00:09:28.558046+00:00
- **Git commit**: `e0857aaefa35678cc84026e9e5e1b1998bf7ef8c`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 3
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/literature/wp4_sample.json`
- **Data SHA-256**: `f3cb5d0c3c4e0598860b2dad5a66219a3c252a92a7800d193111dec21fdcea15`
- **Output path**: `artifacts/literature/wp4_hit_classification.json`

## Config snapshot

```json
{
  "corpus_root": "config/local_paths.yaml:litcorpus02_root",
  "inputs": {
    "artifacts/literature/wp4_sample.json": "f3cb5d0c3c4e0598860b2dad5a66219a3c252a92a7800d193111dec21fdcea15",
    "artifacts/literature/litcorpus02/evidence/runs/fire_weather_v1/hits.csv": "9fd398dcd37914610cbe753f013d3d77c005595c8fdb9140519ad56b47d4a834",
    "artifacts/literature/litcorpus02/evidence/runs/extreme_heat_v1/hits.csv": "feb4342ced02d3df6ce2a08d1d004faa63c782c72709bc81c2524a3cfc3d5ecc",
    "artifacts/literature/litcorpus02/place_candidates/candidate_hits.csv": "c33aa60c2f9d8290674bfa0e51c6c03bf72b0c25c7760615e4a6802f113153c1",
    "scripts/wp4_hit_judgements.py": "c089f50b5476f0407dfa8d737bffcf94501adf71aaa30d317daacecbd0587f5a",
    "artifacts/literature/wp4_claims_summary.json": "e062f05086185ef2616fe5c47ca8fe4d294e389055b4725160737a9a364c9b02"
  }
}
```

## Result summary

- `items`: 20
- `item_term_pairs`: {'concept': 29, 'place': 23}
- `frozen_first_hit_rows`: 81
- `occurrences`: 205
- `concept_pairs_by_primary_class`: {'substantive_concept_use': 8, 'incidental_mention': 20, 'ambiguous_acronym_or_collision': 1}
- `place_pairs_by_primary_class`: {'study_area_or_phenomenon_geography': 10, 'contextual_geography': 10, 'institution_or_affiliation': 2, 'citation_surname_or_person': 1, 'other_incidental': 0}
- `concept_occurrences_by_class`: {'substantive_concept_use': 55, 'incidental_mention': 40, 'ambiguous_acronym_or_collision': 4}
- `place_occurrences_by_class`: {'study_area_or_phenomenon_geography': 65, 'contextual_geography': 24, 'institution_or_affiliation': 5, 'citation_surname_or_person': 6, 'other_incidental': 6}
- `items_by_concept_class`: {'substantive_concept_use': 6, 'incidental_mention': 13, 'ambiguous_acronym_or_collision': 1}
- `items_by_place_class`: {'study_area_or_phenomenon_geography': 8, 'contextual_geography': 10, 'institution_or_affiliation': 2, 'citation_surname_or_person': 0, 'other_incidental': 0}
- `place_pairs_by_term`: {'california': {'study_area_or_phenomenon_geography': 8, 'contextual_geography': 10, 'institution_or_affiliation': 2, 'citation_surname_or_person': 0, 'other_incidental': 0}, 'oklahoma': {'study_area_or_phenomenon_geography': 2, 'contextual_geography': 0, 'institution_or_affiliation': 0, 'citation_surname_or_person': 0, 'other_incidental': 0}, 'stephens': {'study_area_or_phenomenon_geography': 0, 'contextual_geography': 0, 'institution_or_affiliation': 0, 'citation_surname_or_person': 1, 'other_incidental': 0}}
