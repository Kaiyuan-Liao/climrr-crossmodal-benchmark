# Run record: 20261103T185040Z_local_build_mentor_pilot_items

- **Result**: PASS
- **UTC timestamp**: 2026-11-03T18:50:40.563637+00:00
- **Git commit**: `37c703714c7a8fc52b9e2b64e10890c54bd72ee6`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 8
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/items/index.json`
- **Data SHA-256**: `b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804`
- **Output path**: `artifacts/benchmark/review/MENTOR_PILOT_ITEMS_2026-11-05.md`

## Config snapshot

```json
{
  "items_index_sha256": "b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804",
  "coordinator_edits_sha256": "98bae42677f5cc5727527f865657c53e3bcfae2b2c3a4e183a1126b2c4efff86",
  "support_map_sha256": "e3638e13eb4d12dc4f3aa6338d36edebfb1e7cdefd7cf5c6f9eee6d59c3bb291",
  "statements_sha256": "26ba676c004adb0bdb7018b0e748b30f0d8eee0225c968e48786fecb2742a15f",
  "table_patterns_sha256": "ed3c2154818fc363e982b17e0dcb9bb1a2d2ca25e18de97fda6d353974bbf3b0",
  "passage_max_chars": 700,
  "model_calls": 0
}
```

## Result summary

- `md_sha256`: 8420ec304e9bd8232282581e09ebf3af214ae5a857afe58d0c44d1990244b5fb
- `xlsx_sha256`: ad2c7424ab014dd9b3093e7b60e6d8fbaeb6b1d76de5cb239204de025e848f79
- `rows`: 5
- `items`: ['BI-P2B-0001', 'BI-P2B-0003', 'BI-P2B-0006', 'BI-P2B-0007', 'BI-P2B-0010']
- `clause_verdicts`: {'guardrail': 2, 'not_supported_by_verbatim_passage': 2, 'partially_supported': 6, 'supported': 11, 'supported_by_uncited_packet_group': 1}
- `not_fully_supported`: {'not_supported_by_verbatim_passage': ['BI-P2B-0003', 'BI-P2B-0007'], 'partially_supported': ['BI-P2B-0003', 'BI-P2B-0003', 'BI-P2B-0006', 'BI-P2B-0007', 'BI-P2B-0010', 'BI-P2B-0010'], 'supported_by_uncited_packet_group': ['BI-P2B-0006']}
