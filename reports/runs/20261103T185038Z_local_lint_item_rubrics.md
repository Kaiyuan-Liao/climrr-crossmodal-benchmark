# Run record: 20261103T185038Z_local_lint_item_rubrics

- **Result**: PASS
- **UTC timestamp**: 2026-11-03T18:50:38.852254+00:00
- **Git commit**: `37c703714c7a8fc52b9e2b64e10890c54bd72ee6`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 2
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/items/index.json`
- **Data SHA-256**: `b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804`
- **Output path**: `artifacts/benchmark/items/rubric_lint_v1a.json`

## Config snapshot

```json
{
  "version": "rubric_lint v1a",
  "rules": {
    "generation_constraint": "a rubric line that is a generation constraint, not a grading criterion (pattern: allowed descriptors|allowed[ _]numbers|decimal number|exact (?:numeric )?values are not required|multi.source supported|cite a|not in the packet|not provided in the packet, case-insensitive)",
    "required_single_source_only": "a required point whose source ids are only single_source_supported groups",
    "hedge_strength_mismatch": "a literature sentence tagged only with multi_source_supported groups that says 'one study' / 'a single study'",
    "rung1_prompt_mechanism": "a rung-1 prompt that asks about a driver, mechanism or cause",
    "required_tercile": "a required point that names a tercile"
  },
  "model_calls": 0,
  "items_modified": 0
}
```

## Result summary

- `lint_sha256`: 183bcdd057ef0fcdc6e6aba1841a307eaa1d44c9444f7b33d542d24fd9e3de33
- `version`: rubric_lint v1a
- `totals`: {'generation_constraint': 18, 'required_single_source_only': 2, 'hedge_strength_mismatch': 9, 'rung1_prompt_mechanism': 1, 'required_tercile': 1, 'all': 31}
- `per_item`: {'BI-P2B-0001': {'n_flags': 2, 'generation_constraint': 2}, 'BI-P2B-0002': {'n_flags': 3, 'generation_constraint': 1, 'rung1_prompt_mechanism': 1, 'required_tercile': 1}, 'BI-P2B-0003': {'n_flags': 2, 'generation_constraint': 1, 'hedge_strength_mismatch': 1}, 'BI-P2B-0004': {'n_flags': 4, 'generation_constraint': 2, 'hedge_strength_mismatch': 2}, 'BI-P2B-0005': {'n_flags': 2, 'generation_constraint': 2}, 'BI-P2B-0006': {'n_flags': 2, 'generation_constraint': 1, 'hedge_strength_mismatch': 1}, 'BI-P2B-0007': {'n_flags': 3, 'generation_constraint': 2, 'required_single_source_only': 1}, 'BI-P2B-0008': {'n_flags': 7, 'generation_constraint': 5, 'hedge_strength_mismatch': 2}, 'BI-P2B-0009': {'n_flags': 1, 'generation_constraint': 1}, 'BI-P2B-0010': {'n_flags': 5, 'generation_constraint': 1, 'required_single_source_only': 1, 'hedge_strength_mismatch': 3}}
