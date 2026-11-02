# Run record: 20261102T180916Z_local_build_p2b_groups_review

- **Result**: PASS
- **UTC timestamp**: 2026-11-02T18:09:16.638254+00:00
- **Git commit**: `7a8b46b5c7cc9cd37824b315ee71c8a3685c9708`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 4
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/litgroups/run2/groups_enriched.jsonl`
- **Data SHA-256**: `924a7b0d386541c698c9f4c9ba8d83e7fee41da240a0534a9fe31d6ab519a70a`
- **Output path**: `artifacts/benchmark/review/P2b_groups_v1.xlsx`

## Config snapshot

```json
{
  "run2_manifest_sha256": "36931849a2de42d9931bbd491b2fc95ba0c71ba9ac0b3b0aa42be54b0bda80d0",
  "packet_manifest_sha256": "80af2d0dbe3c9601f06246c621d430ae4c7b1f7e4318fbecdec8e7d5558611c1",
  "dispositions": [
    "accept_group",
    "split",
    "merge_with",
    "mislabelled_claim_about",
    "reject"
  ],
  "model_calls": 0
}
```

## Result summary

- `sheets`: {'OVERVIEW': 32, 'GROUPS': 239, 'SINGLETONS': 155, 'PACKETS': 116, 'Legend': 10}
- `workbook_sha256`: a5395e11345da88b12d66f280edfb06eecdb1ea3c8a19c776048d1e1cfa8c3ff
- `groups_csv_sha256`: 0c635250c127fb0de36d5abb85ce1f616bfeff889f44cd0c86b7b0b384e24084
