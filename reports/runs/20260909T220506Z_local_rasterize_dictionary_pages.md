# Run record: 20260909T220506Z_local_rasterize_dictionary_pages

- **Result**: PASS
- **UTC timestamp**: 2026-09-09T22:05:06.602766+00:00
- **Git commit**: `62c91372e5c3283bd611a236fcbdc188200c58c7`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 5
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf`
- **Data SHA-256**: `b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db`
- **Output path**: `artifacts/profiles`

## Config snapshot

```json
{
  "pdf_path": "data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf",
  "out_dir": "artifacts/profiles",
  "dpi": 200,
  "pages": [
    2,
    3,
    4
  ],
  "renderer": "pypdfium2 5.13.0"
}
```

## Result summary

- `pdf_sha256`: b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db
- `pdf_pages`: 19
- `pypdfium2_version`: 5.13.0
- `dpi`: 200
- `pages_rendered`: [2, 3, 4]
- `rendered`: [{'page': 2, 'output_path': 'artifacts/profiles/dictionary_page02.png', 'pixels': '1700x2200', 'bytes': 199691, 'sha256': '297283dc18068cfb4f47ce3fecefc0314ac7b8019de8bcaa9091eeebe069b161', 'uniform_colour': False, 'channel_extrema': [0, 255]}, {'page': 3, 'output_path': 'artifacts/profiles/dictionary_page03.png', 'pixels': '1700x2200', 'bytes': 15888, 'sha256': '11c19fcbe60501f1dd762c1eeb510eb52cd39882d5ac9386fead1a0c2abf9e19', 'uniform_colour': True, 'channel_extrema': [255, 255]}, {'page': 4, 'output_path': 'artifacts/profiles/dictionary_page04.png', 'pixels': '1700x2200', 'bytes': 477998, 'sha256': 'fdce7c699ab843b6f647f9a917cba3cfec30a7a1d46e855594e7b6b882f2524e', 'uniform_colour': False, 'channel_extrema': [0, 255]}]
