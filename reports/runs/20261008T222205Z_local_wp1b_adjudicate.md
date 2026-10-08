# Run record: 20261008T222205Z_local_wp1b_adjudicate

- **Result**: PASS
- **UTC timestamp**: 2026-10-08T22:22:05.290297+00:00
- **Git commit**: `7ddee2cb62d8675697fcbb373841755e1c48be82`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 18
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/literature/wp1_sample.json`
- **Data SHA-256**: `5cb81f9585040dd1d73a89ca7062d3c5e0060112f54e08ef4795db96a657b578`
- **Output path**: `artifacts/literature/wp1b_comparison.json`

## Config snapshot

```json
{
  "corpus_root": "config/local_paths.yaml:literature_corpus_root",
  "frozen_inputs": 23,
  "blind_commit": "87bce48"
}
```

## Result summary

- `actions`: {'comparison': 'written', 'summary': 'written', 'LIT-000001.json': 'written', 'LIT-000191.json': 'written', 'LIT-000381.json': 'written', 'LIT-000571.json': 'written', 'LIT-000761.json': 'written', 'LIT-000951.json': 'written', 'LIT-001141.json': 'written', 'LIT-001331.json': 'written', 'LIT-001521.json': 'written', 'LIT-001711.json': 'written'}
- `sha256`: {'artifacts/literature/wp1b_comparison.json': '436657cf5dfafd7a074d08d2e78272c1ef75a524a3767918221f4aaacaf0f5ab', 'artifacts/literature/wp1_claims_adjudicated/adjudication_summary.json': 'f7c2f55bc8049dd8624ec67d7d41bb573c46bd252acf4d4c54295b10e970c1fa', 'docs/LITERATURE_WP1B_ADJUDICATION.md': '15c097b426931dfb037ea61d668efa2bd67de24820d88e490b09f9cc9478cdb1', 'artifacts/literature/wp1_claims_adjudicated/LIT-000001.json': 'aea24931dddee2e08212c4193a4f3fecba18e802bd34b95730eb8eb20bbf3ee1', 'artifacts/literature/wp1_claims_adjudicated/LIT-000191.json': '0e82d37d7c1acec3369970139268a34fa464a05b6565cdf54d9cbb509f4504e6', 'artifacts/literature/wp1_claims_adjudicated/LIT-000381.json': '986106940a0ee9ed14554057cc0f63a64593d3c60ddddae37fa7f7e9acb9ec2f', 'artifacts/literature/wp1_claims_adjudicated/LIT-000571.json': 'd1a58afdb33b0f04a0cc90a41c3c83d2fb2f346f992d6b6e89a883d5191432fe', 'artifacts/literature/wp1_claims_adjudicated/LIT-000761.json': '196c03a9e1ba20c11103f9a20277d9e01173ded20e35664a959a4380ca90da29', 'artifacts/literature/wp1_claims_adjudicated/LIT-000951.json': '45263d88e3b381ca5eef91ce5bec104b19fef8aa4a78602442de6b75143b4c17', 'artifacts/literature/wp1_claims_adjudicated/LIT-001141.json': '0997fad51df7fba4b6da48b86314157f38efc00065bf62961835d95474010db0', 'artifacts/literature/wp1_claims_adjudicated/LIT-001331.json': '65c5cd2bfdea09419f212a8e7264d973caa52d5f5384f8680ddb341142ead67f', 'artifacts/literature/wp1_claims_adjudicated/LIT-001521.json': '979cc06ec10aa239649cc7004c298e38fee85f7dddec716858b6cf6762b2054f', 'artifacts/literature/wp1_claims_adjudicated/LIT-001711.json': '7979a2ea0cf571f567a558588e3cc79ba15c9c13e66a5fcb6de461da7a64853c'}
- `span_counts`: {'reader_1': 96, 'reader_2': 85}
- `phase_b_counts`: {'aligned_pairs': 19, 'reader_1_only': 8, 'reader_2_only': 2}
- `status_counts`: {'independently_confirmed': 1, 'adjudicated_modified': 23, 'single_reader_provisional': 5, 'rejected_on_review': 0}
- `scope_agreement`: {'agree': 6, 'n': 10}
- `field_13_answer`: The blind reader found no claim with US geography, an emissions scenario, or a pilot concept term that reader 1 missed.
