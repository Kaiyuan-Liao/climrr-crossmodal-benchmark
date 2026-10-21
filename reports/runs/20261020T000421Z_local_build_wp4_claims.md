# Run record: 20261020T000421Z_local_build_wp4_claims

- **Result**: PASS
- **UTC timestamp**: 2026-10-20T00:04:21.240994+00:00
- **Git commit**: `38116a07fbf759f01a0afbdec5eb39a50e2cb66b`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 26
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/literature/wp4_sample.json`
- **Data SHA-256**: `f3cb5d0c3c4e0598860b2dad5a66219a3c252a92a7800d193111dec21fdcea15`
- **Output path**: `artifacts/literature/wp4_claims_summary.json`

## Config snapshot

```json
{
  "corpus_root": "config/local_paths.yaml:litcorpus02_root",
  "spec": "scripts/wp4_extractions.py",
  "spec_sha256": "9a91168ac2a49b3197423f03e82d3c0c1e0cf7ec045cb6e3a72144422de97c9c"
}
```

## Result summary

- `sample_sha256`: f3cb5d0c3c4e0598860b2dad5a66219a3c252a92a7800d193111dec21fdcea15
- `items`: 20
- `claims`: 83
- `items_with_claims`: 19
- `claims_with_any_inferred_dimension`: 9
- `rejected_or_ambiguous`: 68
- `by_terminal_status`: {'claims_extracted': 19, 'no_eligible_claim': 0, 'off_topic': 0, 'ambiguous_only': 1, 'parse_failure': 0}
- `by_scope_status`: {'in_scope_hazard': 19, 'off_topic': 0, 'ambiguous': 1}
- `by_claim_validation_status`: {'single_reader_provisional': 83}
- `by_evidence_tier`: {'C': 83}
- `spans_checked`: 300
