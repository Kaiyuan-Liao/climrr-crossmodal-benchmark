# Run record: 20260929T052600Z_local_build_wp1_claims

- **Result**: PASS
- **UTC timestamp**: 2026-09-29T05:26:00.084424+00:00
- **Git commit**: `6f9006cab69583d8a45b7a285d4d2be4ba3d6a2e`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 22
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/literature/wp1_sample.json`
- **Data SHA-256**: `5cb81f9585040dd1d73a89ca7062d3c5e0060112f54e08ef4795db96a657b578`
- **Output path**: `artifacts/literature/wp1_claims_summary.json`

## Config snapshot

```json
{
  "corpus_root": "config/local_paths.yaml:literature_corpus_root",
  "spec": "scripts/wp1_extractions.py",
  "spec_sha256": "cf4c700266592d3897158804cabc69b640e04ccbaf1dc8c750734b6f579b5685"
}
```

## Result summary

- `sample_sha256`: 5cb81f9585040dd1d73a89ca7062d3c5e0060112f54e08ef4795db96a657b578
- `items`: 10
- `claims`: 27
- `claims_with_any_inferred_dimension`: 3
- `rejected_or_ambiguous`: 22
- `by_terminal_status`: {'claims_extracted': 6, 'no_eligible_claim': 0, 'off_topic': 3, 'parse_failure': 0, 'ambiguous_only': 1}
- `by_scope_status`: {'in_scope_hazard': 6, 'off_topic': 3, 'ambiguous': 1}
- `spans_checked`: 96
