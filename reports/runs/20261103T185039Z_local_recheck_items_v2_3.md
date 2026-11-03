# Run record: 20261103T185039Z_local_recheck_items_v2_3

- **Result**: PASS
- **UTC timestamp**: 2026-11-03T18:50:39.390835+00:00
- **Git commit**: `37c703714c7a8fc52b9e2b64e10890c54bd72ee6`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 4
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/items/index.json`
- **Data SHA-256**: `b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804`
- **Output path**: `artifacts/benchmark/items/post_checks_v2_3_report.json`

## Config snapshot

```json
{
  "check_version": "synthesis_post_checks v2.3",
  "patterns": [
    "\\b(the|this|our) (model|projection|modeled projection|data|dataset|table) (shows?|indicates?|projects?|suggests?)\\b",
    "\\bmodeled projection shows\\b"
  ],
  "report_only": true,
  "items_modified": 0,
  "model_calls": 0
}
```

## Result summary

- `report_sha256`: 970f22396e2739597f8ac28011e42c0744bf883809e052853b2efa6183688539
- `items_hit`: ['BI-P2B-0002', 'BI-P2B-0003', 'BI-P2B-0004', 'BI-P2B-0005', 'BI-P2B-0007', 'BI-P2B-0008']
- `hits`: {'BI-P2B-0002': ['integrated leakage: source phrase (v2.3): The modeled projection shows'], 'BI-P2B-0003': ['integrated leakage: source phrase (v2.3): The model shows'], 'BI-P2B-0004': ['integrated leakage: source phrase (v2.3): The model shows'], 'BI-P2B-0005': ['table_pattern leakage: source phrase (v2.3): The projection shows', 'integrated leakage: source phrase (v2.3): The model projects'], 'BI-P2B-0007': ['integrated leakage: source phrase (v2.3): The modeled projection shows'], 'BI-P2B-0008': ['table_pattern leakage: source phrase (v2.3): The projection shows']}
- `superseded_hits`: {}
- `coordinator_proposed_hits`: {'BI-P2B-0010': ['source phrase: in the table']}
