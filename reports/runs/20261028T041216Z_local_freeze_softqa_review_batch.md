# Run record: 20261028T041216Z_local_freeze_softqa_review_batch

- **Result**: PASS
- **UTC timestamp**: 2026-10-28T04:12:16.817280+00:00
- **Git commit**: `95e1ec851f2ac703654df52ac1ccc9c3d777fcd7`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 273
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/softqa/run1/candidates_schema.jsonl`
- **Data SHA-256**: `2536131cb1431a53a6b224e4dd7b03586985935cadb5f063e2cdb5bb14170a73`
- **Output path**: `artifacts/softqa/review_batch_01.json`

## Config snapshot

```json
{
  "triage_rule": "status deterministic_pass AND proposal.concept_relation == 'direct' AND proposal.paper_geography_role in {study_area, cited_study_area} AND len(proposal.unmatched_dimensions) <= 2",
  "reviewer_1": "Kaiyuan Liao"
}
```

## Result summary

- `batch_id`: review_batch_01
- `n_candidates`: 11
- `candidate_ids`: ['C-199098498-01', 'C-226260658-01', 'C-236782701-01', 'C-245473445-01', 'C-247623438-01', 'C-247866001-01', 'C-247866001-02', 'C-253196482-01', 'C-254679818-01', 'C-4238342-01', 'C-5882914-01']
- `sha256`: 1086991e25306ee19b7ba29102123fe516f670edd6524e8b1970102a7058f9c8
- `forms_prepared`: 11
- `acceptance_gate`: {'C-199098498-01': 'clear', 'C-226260658-01': 'clear', 'C-236782701-01': 'clear', 'C-245473445-01': 'hold_owner_confirmation', 'C-247623438-01': 'clear', 'C-247866001-01': 'hold_owner_confirmation', 'C-247866001-02': 'clear', 'C-253196482-01': 'clear', 'C-254679818-01': 'clear', 'C-4238342-01': 'clear', 'C-5882914-01': 'clear'}
