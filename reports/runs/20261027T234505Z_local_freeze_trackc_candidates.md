# Run record: 20261027T234505Z_local_freeze_trackc_candidates

- **Result**: PASS
- **UTC timestamp**: 2026-10-27T23:45:05.011094+00:00
- **Git commit**: `9e163917eb061860c3cdf0b52e337ff8d426df63`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 13
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/literature/litcorpus02/place_candidates/place_candidates.json`
- **Data SHA-256**: `57118bdb28d4f58a0ab6246c45476ce7ae665585c2866bb7d423565ef1b56a35`
- **Output path**: `data/metadata/softqa/trackc_candidates_v1.json`

## Config snapshot

```json
{
  "input_sha256": {
    "artifacts/literature/litcorpus02/place_candidates/fire_weather_v1_place_candidates.txt": "122ee177f45dd98ecb76765a7ce0e8c543261694c5e991380ab94139d756a149",
    "artifacts/literature/litcorpus02/place_candidates/extreme_heat_v1_place_candidates.txt": "eb28845e43bbd63875a8ac7b25f64fef9aabb07abde69a7ae75e14bb689c623c",
    "artifacts/literature/wp4_sample.json": "f3cb5d0c3c4e0598860b2dad5a66219a3c252a92a7800d193111dec21fdcea15"
  },
  "already_read": [
    {
      "item_id": "208499235",
      "lit2_id": "LIT2-000185",
      "arm": "fire_weather_v1"
    },
    {
      "item_id": "229495849",
      "lit2_id": "LIT2-000366",
      "arm": "fire_weather_v1"
    },
    {
      "item_id": "238725720",
      "lit2_id": "LIT2-000499",
      "arm": "fire_weather_v1"
    },
    {
      "item_id": "244714495",
      "lit2_id": "LIT2-000560",
      "arm": "fire_weather_v1"
    },
    {
      "item_id": "250541813",
      "lit2_id": "LIT2-000673",
      "arm": "fire_weather_v1"
    },
    {
      "item_id": "257108685",
      "lit2_id": "LIT2-000786",
      "arm": "fire_weather_v1"
    },
    {
      "item_id": "272211804",
      "lit2_id": "LIT2-001063",
      "arm": "fire_weather_v1"
    },
    {
      "item_id": "52918429",
      "lit2_id": "LIT2-001157",
      "arm": "fire_weather_v1"
    },
    {
      "item_id": "59342086",
      "lit2_id": "LIT2-001236",
      "arm": "fire_weather_v1"
    },
    {
      "item_id": "999274",
      "lit2_id": "LIT2-001308",
      "arm": "fire_weather_v1"
    },
    {
      "item_id": "154971876",
      "lit2_id": "LIT2-000084",
      "arm": "extreme_heat_v1"
    },
    {
      "item_id": "211267687",
      "lit2_id": "LIT2-000203",
      "arm": "extreme_heat_v1"
    },
    {
      "item_id": "225397451",
      "lit2_id": "LIT2-000315",
      "arm": "extreme_heat_v1"
    },
    {
      "item_id": "237371886",
      "lit2_id": "LIT2-000470",
      "arm": "extreme_heat_v1"
    },
    {
      "item_id": "250039675",
      "lit2_id": "LIT2-000662",
      "arm": "extreme_heat_v1"
    },
    {
      "item_id": "257854681",
      "lit2_id": "LIT2-000803",
      "arm": "extreme_heat_v1"
    },
    {
      "item_id": "266658220",
      "lit2_id": "LIT2-000927",
      "arm": "extreme_heat_v1"
    },
    {
      "item_id": "272852900",
      "lit2_id": "LIT2-001075",
      "arm": "extreme_heat_v1"
    },
    {
      "item_id": "53109236",
      "lit2_id": "LIT2-001160",
      "arm": "extreme_heat_v1"
    },
    {
      "item_id": "88523156",
      "lit2_id": "LIT2-001293",
      "arm": "extreme_heat_v1"
    }
  ]
}
```

## Result summary

- `n_candidates`: 243
- `per_arm`: {'fire_weather_v1': 100, 'extreme_heat_v1': 143}
- `n_already_read`: 20
- `output_sha256`: 6fb9c911acb07f4798fea90332be389a9327351174038167849a02daff23c943
