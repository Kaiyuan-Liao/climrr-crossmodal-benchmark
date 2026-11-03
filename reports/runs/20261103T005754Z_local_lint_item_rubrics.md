# Run record: 20261103T005754Z_local_lint_item_rubrics

- **Result**: PASS
- **UTC timestamp**: 2026-11-03T00:57:54.041948+00:00
- **Git commit**: `6ca9a93ec563fd02e52d8c72c4f23efd53ac9daf`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 2
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/items/run2/manifest.json`
- **Data SHA-256**: `c9c6bc9bc1a4f19d94e7a5e9c9514c34c9a3ad18b60dc97a11b87df2b84d60e9`
- **Output path**: `artifacts/benchmark/items/run2/rubric_lint_v1.json`

## Config snapshot

```json
{
  "version": "rubric_lint v1",
  "rules": {
    "generation_constraint": "a rubric line that is a generation constraint, not a grading criterion (pattern: allowed descriptors|allowed_numbers|decimal number|exact values are not required|multi.source supported|cite a|not in the packet|not provided in the packet, case-insensitive)",
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

- `lint_sha256`: 5b5cf722f54ad8bc7f790a6591f467f69c3cb963e6d26cec9529835e1d7d8d31
- `totals`: {'generation_constraint': 16, 'required_single_source_only': 1, 'hedge_strength_mismatch': 6, 'rung1_prompt_mechanism': 1, 'required_tercile': 1, 'all': 25}
- `per_item`: {'BI-P2B-0001': {'n_flags': 2, 'generation_constraint': 2}, 'BI-P2B-0002': {'n_flags': 3, 'generation_constraint': 1, 'rung1_prompt_mechanism': 1, 'required_tercile': 1}, 'BI-P2B-0003': {'n_flags': 2, 'generation_constraint': 1, 'hedge_strength_mismatch': 1}, 'BI-P2B-0004': {'n_flags': 4, 'generation_constraint': 2, 'hedge_strength_mismatch': 2}, 'BI-P2B-0005': {'n_flags': 2, 'generation_constraint': 2}, 'BI-P2B-0006': {'n_flags': 2, 'generation_constraint': 1, 'hedge_strength_mismatch': 1}, 'BI-P2B-0007': {'n_flags': 1, 'required_single_source_only': 1}, 'BI-P2B-0008': {'n_flags': 7, 'generation_constraint': 5, 'hedge_strength_mismatch': 2}, 'BI-P2B-0009': {'n_flags': 1, 'generation_constraint': 1}, 'BI-P2B-0010': {'n_flags': 1, 'generation_constraint': 1}}
