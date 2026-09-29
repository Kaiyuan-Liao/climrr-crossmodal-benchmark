# Run record: 20260929T051714Z_local_sample_corpus

- **Result**: PASS
- **UTC timestamp**: 2026-09-29T05:17:14.520772+00:00
- **Git commit**: `5ebb3305a42c9d5a5261a5d99a13223d652b151a`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 7
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/literature/corpus_manifest.json`
- **Data SHA-256**: `3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a`
- **Output path**: `artifacts/literature/wp1_sample.json`

## Config snapshot

```json
{
  "rule": "Every 190th LIT item by numeric id, starting at LIT-000001 (LIT-000001, LIT-000191, LIT-000381, ...), ten items. If a selected item is the later member of an exact-byte duplicate group, skip to the next id and record the skip; later positions stay on the 190-step grid. Derived from the frozen corpus manifest alone; no file is opened."
}
```

## Result summary

- `item_ids`: ['LIT-000001', 'LIT-000191', 'LIT-000381', 'LIT-000571', 'LIT-000761', 'LIT-000951', 'LIT-001141', 'LIT-001331', 'LIT-001521', 'LIT-001711']
- `skips`: none
- `sample_sha256`: 5cb81f9585040dd1d73a89ca7062d3c5e0060112f54e08ef4795db96a657b578
