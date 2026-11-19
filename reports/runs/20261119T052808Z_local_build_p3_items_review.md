# Run record: 20261119T052808Z_local_build_p3_items_review

- **Result**: PASS
- **UTC timestamp**: 2026-11-19T05:28:08.789151+00:00
- **Git commit**: `ab42cfd7cb793c241ad0c9941f5b295847bbf047`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 4
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/items/run5/manifest.json`
- **Data SHA-256**: `52a4cb57e43d3ce73fa8719320cd66dbb1a17468c54bdd6a435c90acb907936c`
- **Output path**: `artifacts/benchmark/review/P3_items_review_v1.csv`

## Config snapshot

```json
{
  "packets_manifest_sha256": "598b2744c7fbde5aeaf4cdc3c0bc9465134e41d35e08f11ce19441eb3cf5bfad",
  "items_manifest_sha256": "52a4cb57e43d3ce73fa8719320cd66dbb1a17468c54bdd6a435c90acb907936c",
  "model_calls": 0,
  "items_modified": 0
}
```

## Result summary

- `csv_sha256`: c6a066030513faeabe7de70a8f0e89c188667ae479ae29a5b2bb30690a824097
- `flags_sha256`: 9a84f1217e2121041bbe19882e63d216be6929f18ad3123ab1be70971c241408
- `xlsx_sha256`: 38abd90720970abcaa680d57af2e4eff553e6280e074d68067bfe52620faf5de
- `counts_by_source`: {'work_package': 2, 'post_check_report': 0, 'rubric_lint': 4, 'executor_reading': 15}
- `context_driver_report_hits`: {'BI-P3-0001': 0, 'BI-P3-0002': 0, 'BI-P3-0003': 0, 'BI-P3-0004': 0, 'BI-P3-0005': 0, 'BI-P3-0007': 0, 'BI-P3-0008': 0}
- `regional_contrast_report_hits`: {'BI-P3-0001': 0, 'BI-P3-0002': 0, 'BI-P3-0003': 0, 'BI-P3-0004': 0, 'BI-P3-0005': 0, 'BI-P3-0007': 0, 'BI-P3-0008': 0}
- `rubric_lint`: {'version': 'rubric_lint v1a', 'totals': {'generation_constraint': 4, 'required_single_source_only': 0, 'hedge_strength_mismatch': 0, 'rung1_prompt_mechanism': 0, 'required_tercile': 0, 'all': 4}}
- `coordinator_proposed`: {'BI-P3-0005': 'How are dangerous heat-index days in summer projected to change by mid-century under a high-emissions future, how do the changes differ across U.S. regions, and what drives them?'}
- `flags_per_item`: {'BI-P3-0001': ['LINT-0001-1', 'EX-6.1'], 'BI-P3-0004': ['EX-2.2', 'EX-6.2', 'EX-6.4'], 'BI-P3-0003': ['LINT-0003-1', 'EX-1.2', 'EX-3.1', 'EX-4.1', 'EX-6.5'], 'BI-P3-0002': ['LINT-0002-1', 'EX-1.1', 'EX-2.1', 'EX-6.3'], 'BI-P3-0005': ['WP-C1', 'EX-1.3'], 'BI-P3-0007': ['WP-C3', 'LINT-0007-1', 'EX-1.4', 'EX-5.1', 'EX-5.2'], 'BI-P3-0008': []}
