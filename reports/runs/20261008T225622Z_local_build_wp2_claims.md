# Run record: 20261008T225622Z_local_build_wp2_claims

- **Result**: PASS
- **UTC timestamp**: 2026-10-08T22:56:22.194643+00:00
- **Git commit**: `e7da7cc864f57518de00091895d3e233d1d3499b`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 10
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/literature/wp2_candidates.json`
- **Data SHA-256**: `e155e70e338ffb67f8c881a8a3fdb794e28c0f048c43afc10b0a723135ec8d9c`
- **Output path**: `artifacts/literature/wp2_claims/wp2_claims_summary.json`

## Config snapshot

```json
{
  "corpus_root": "config/local_paths.yaml:literature_corpus_root",
  "spec": "scripts/wp2_extractions.py",
  "spec_sha256": "b9b38c18b1d6159e04c6f1ad04b4bc62a00601c274d04ee59aa72c31e09716f6"
}
```

## Result summary

- `actions`: {'LIT-000166': 'verified', 'LIT-000519': 'verified', 'LIT-001501': 'written', 'LIT-001536': 'written', 'summary': 'written'}
- `items`: 4
- `claims`: 20
- `rejected_or_ambiguous`: 17
- `spans_checked`: 63
