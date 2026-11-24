# Run record: 20261124T000938Z_local_build_synth_packets_v5

- **Result**: PASS
- **UTC timestamp**: 2026-11-24T00:09:38.945679+00:00
- **Git commit**: `033c95c073efa4d6a78c5408388a89948053d38c`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/benchmark/synth_packets_v4b/manifest.json`
- **Data SHA-256**: `598b2744c7fbde5aeaf4cdc3c0bc9465134e41d35e08f11ce19441eb3cf5bfad`
- **Output path**: `artifacts/benchmark/synth_packets_v5/manifest.json`

## Config snapshot

```json
{
  "version": "synthpackets v5",
  "decision": "D-069",
  "base": "synthpackets v4b",
  "question_forms": "data/metadata/benchmark/question_forms_v1.yaml",
  "question_forms_sha256": "d123b381f6807a9b8d6cc9b6b901a86e8c48dfe617cb1f26ff9c6be9fdd4c910",
  "max_share": 0.3,
  "model_calls": 0
}
```

## Result summary

- `packets`: [{'packet_id': 'PK-SD2-TP1-00071', 'item_id': 'BI-P3-0001', 'needs_general_clause': False, 'sha256': '330be30a7bd7ee9ae39d6b27e05930ec29197fd2008ef8dc6aa9e8771500a03c', 'question_form': 'QF-01'}, {'packet_id': 'PK-SD2-TP1-00271', 'item_id': 'BI-P3-0002', 'needs_general_clause': True, 'sha256': '8c95b132dc4b9609d173cd316824520e71e6030b53cd429271d3f37a6d6b36d4', 'question_form': 'QF-02'}, {'packet_id': 'PK-SD2-TP1-00460', 'item_id': 'BI-P3-0003', 'needs_general_clause': True, 'sha256': '57307c965815602c1784a75ccd3024c03e5ce7a37694d4d672776e53231ae41a', 'question_form': 'QF-03'}, {'packet_id': 'PK-SD2-TP1-00589', 'item_id': 'BI-P3-0004', 'needs_general_clause': True, 'sha256': '4f39dfdc4dc20d3b3416823979b3071de5df12fa8716930c5767b5223d38623d', 'question_form': 'QF-05'}, {'packet_id': 'PK-SD2-TP1-02785', 'item_id': 'BI-P3-0005', 'needs_general_clause': False, 'sha256': 'a2458adb1ea2312a078948d652686e46f9c4839ceb94ee529e6c3096df7eca96', 'question_form': 'QF-04'}, {'packet_id': 'PK-SD2-TP1-01463', 'item_id': 'BI-P3-0007', 'needs_general_clause': False, 'sha256': '3761927761d8ceed71d8353e005908df9e46069b17b48f73a7b27ad5e3340824', 'question_form': 'QF-06'}, {'packet_id': 'PK-SD2-TP1-01654', 'item_id': 'BI-P3-0008', 'needs_general_clause': False, 'sha256': '7dd2cee978b229c4ef21dbdb9bb1f6e058bf0948b6f8337f95ee1a78647008fa', 'question_form': 'QF-07'}]
- `classes_by_item`: {'BI-P3-0001': ['state', 'nca', 'us_subregion', 'us_national', 'global'], 'BI-P3-0002': ['us_subregion', 'us_national', 'global'], 'BI-P3-0003': ['us_subregion', 'us_national', 'global'], 'BI-P3-0004': ['us_subregion', 'us_national', 'global'], 'BI-P3-0005': ['nca', 'us_subregion', 'us_national', 'global'], 'BI-P3-0007': ['state', 'us_subregion'], 'BI-P3-0008': ['state', 'us_subregion', 'us_national', 'global']}
- `place_specific_class_from_minority_of_cited`: 5
- `diversity_skeletons`: {'pass': True, 'largest_share': 0.143}
- `diversity_baseline_run5`: {'pass': False, 'largest_share': 0.429}
- `manifest_sha256`: 1f92c194411ea12152c6659058633bf250812bdb234328fa8f39fb81dd8ea0fd
