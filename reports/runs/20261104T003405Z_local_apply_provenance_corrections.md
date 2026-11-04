# Run record: 20261104T003405Z_local_apply_provenance_corrections

- **Result**: PASS
- **UTC timestamp**: 2026-11-04T00:34:05.189129+00:00
- **Git commit**: `421463a2bd47b5a3efd40a5b4356d8f579d7567f`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `data/metadata/benchmark/provenance_corrections_v1a.yaml`
- **Data SHA-256**: `d56cbe5e0c4feaffd8398126953c8437416967b2fbc382d5da907e88081ebd93`
- **Output path**: `artifacts/litstatements/corrections/provenance_corrections_v1a_applied.json`

## Config snapshot

```json
{
  "corrections": "data/metadata/benchmark/provenance_corrections_v1a.yaml",
  "items_index_sha256": "b583ca3e36e793b5901fe843c9cc8dc50d91a9b9691301e12c1d24e7cd16c804",
  "statements_ingested_sha256": "b775301cbd3387f2228f07830fded009d9111d0ce635624123bc45a9f458eb81",
  "groups_enriched_sha256": "924a7b0d386541c698c9f4c9ba8d83e7fee41da240a0534a9fe31d6ab519a70a",
  "support_map_v3_sha256": "933298f7a277bee895052da67b26a1be982138449777cc4cc4bb2c1469a8da9a",
  "corpus_root_keys": [
    "literature_corpus_root",
    "litcorpus02_root"
  ],
  "model_calls": 0
}
```

## Result summary

- `applied_sha256`: f6075dfd5c5a9a1a71f926e9faa5b8ab892faf34824aed317af5a04936205862
- `corrections_sha256`: d56cbe5e0c4feaffd8398126953c8437416967b2fbc382d5da907e88081ebd93
- `reslices`: {'LS-199098498-04': {'reslice': 'exact', 'span_start': 4602, 'span_end': 5001, 'occurrences': 1, 'verified_on': 'polaris, 2026-11-03, Kaiyuan'}}
- `groups`: {'LG-extreme_heat_v1-driver-c1-008': {'before': 'multi_source_supported', 'after': 'multi_source_supported', 'stays_multi_source': True, 'core_cited_papers_after': ['158091651', '199098498', '5838629']}}
- `corrected_statements`: {'LS-199098498-04': 'Citing Schoof et al. (2019), the paper reports that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat.'}
- `group_label_overrides`: {'LG-extreme_heat_v1-driver-c1-008': 'Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat'}
- `items_with_corrections_applied`: ['BI-P2B-0003', 'BI-P2B-0004', 'BI-P2B-0005', 'BI-P2B-0006', 'BI-P2B-0007', 'BI-P2B-0008', 'BI-P2B-0009', 'BI-P2B-0010']
- `files_modified`: 0
