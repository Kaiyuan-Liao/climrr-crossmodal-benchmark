# Run record: 20261008T230010Z_local_wp1b_adjudicate

- **Result**: PASS
- **UTC timestamp**: 2026-10-08T23:00:10.344430+00:00
- **Git commit**: `e7da7cc864f57518de00091895d3e233d1d3499b`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 16
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

- `actions`: {'comparison': 'verified', 'summary': 'written', 'LIT-000001.json': 'written', 'LIT-000191.json': 'written', 'LIT-000381.json': 'written', 'LIT-000571.json': 'written', 'LIT-000761.json': 'written', 'LIT-000951.json': 'written', 'LIT-001141.json': 'written', 'LIT-001331.json': 'written', 'LIT-001521.json': 'written', 'LIT-001711.json': 'written'}
- `sha256`: {'artifacts/literature/wp1b_comparison.json': '436657cf5dfafd7a074d08d2e78272c1ef75a524a3767918221f4aaacaf0f5ab', 'artifacts/literature/wp1_claims_adjudicated/adjudication_summary.json': '62b52faacb012ce1099d002a0b3d4261252aa560f708874164a24a41d16dcb64', 'docs/LITERATURE_WP1B_ADJUDICATION.md': '9e28ec1ae2c2e70f47b2d48d84001a7b2a9325472b4c1b8ce3836642b3cae693', 'artifacts/literature/wp1_claims_adjudicated/LIT-000001.json': 'aea24931dddee2e08212c4193a4f3fecba18e802bd34b95730eb8eb20bbf3ee1', 'artifacts/literature/wp1_claims_adjudicated/LIT-000191.json': 'a14a6b52e4f79ab0c278fcffb4034be62a416c52b4054c14ae52670246524706', 'artifacts/literature/wp1_claims_adjudicated/LIT-000381.json': '141f118adfd830f32ce74b9c677395111e7e5fea9ab4b6dd7c97c84b4978ec1f', 'artifacts/literature/wp1_claims_adjudicated/LIT-000571.json': '30aca29ea92de178fa32951c33b9735dba4d17b02d4fca6fc927adc46974a5dc', 'artifacts/literature/wp1_claims_adjudicated/LIT-000761.json': '196c03a9e1ba20c11103f9a20277d9e01173ded20e35664a959a4380ca90da29', 'artifacts/literature/wp1_claims_adjudicated/LIT-000951.json': '45263d88e3b381ca5eef91ce5bec104b19fef8aa4a78602442de6b75143b4c17', 'artifacts/literature/wp1_claims_adjudicated/LIT-001141.json': '2a6833c6706461047160cc4666a50d2847f339a5e94fe3d89f9d97a619fb2dac', 'artifacts/literature/wp1_claims_adjudicated/LIT-001331.json': '65c5cd2bfdea09419f212a8e7264d973caa52d5f5384f8680ddb341142ead67f', 'artifacts/literature/wp1_claims_adjudicated/LIT-001521.json': 'e7761a9710404c237e0e8e484bb8c0eac5bee6195e19767078031b27b6a4b581', 'artifacts/literature/wp1_claims_adjudicated/LIT-001711.json': 'aa215810b9166961b73eb17197b3671c5fe2b3ce64d4671e19477075067b3b79'}
- `span_counts`: {'reader_1': 96, 'reader_2': 85}
- `phase_b_counts`: {'aligned_pairs': 19, 'reader_1_only': 8, 'reader_2_only': 2}
- `status_counts`: {'independently_confirmed': 1, 'adjudicated_modified': 23, 'single_reader_provisional': 5, 'rejected_on_review': 0}
- `scope_agreement`: {'agree': 6, 'n': 10}
- `field_13_answer`: The blind reader found no claim with US geography, an emissions scenario, or a pilot concept term that reader 1 missed.
