# Run record: 20261008T192352Z_local_build_wp1_claims

- **Result**: PASS
- **UTC timestamp**: 2026-10-08T19:23:52.002335+00:00
- **Git commit**: `7ded08e03448b52d4d826f9ed2cfbaa92f5cc140`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 1
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
  "spec_sha256": "9b1bf6fedd8271ba54af0648ba5ecf32cccda50d530c556ea84a97d64c99b9a2"
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
- `by_claim_validation_status`: {'single_reader_provisional': 27, 'independently_confirmed': 0, 'adjudicated_modified': 0, 'rejected_on_review': 0}
- `spans_checked`: 96
