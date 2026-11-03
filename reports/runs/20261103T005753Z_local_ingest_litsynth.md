# Run record: 20261103T005753Z_local_ingest_litsynth

- **Result**: PASS
- **UTC timestamp**: 2026-11-03T00:57:53.326158+00:00
- **Git commit**: `6ca9a93ec563fd02e52d8c72c4f23efd53ac9daf`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `litsynth_runs012_evidence.tar.gz`
- **Data SHA-256**: `00c909340bd08d61331e1eb6515da0b2bf375627b63d7491456c740949ebaac1`
- **Output path**: `artifacts/benchmark/items/run2`

## Config snapshot

```json
{
  "source": "litsynth_runs012_evidence.tar.gz (extracted)",
  "source_tarball_sha256": "00c909340bd08d61331e1eb6515da0b2bf375627b63d7491456c740949ebaac1",
  "packets": "synthpackets v3a at 1f175dac7801b3d27ca7ed1961debe88e22b4dc6",
  "check_version": "synthesis_post_checks v2.2",
  "run_executed_on": "Polaris; this record is the local ingest, not the run",
  "model_calls": 0
}
```

## Result summary

- `manifest_sha256`: c9c6bc9bc1a4f19d94e7a5e9c9514c34c9a3ad18b60dc97a11b87df2b84d60e9
- `files_copied_this_run`: 0
- `files_in_manifest`: 8
- `excluded_files`: 32
- `counts`: {'items': 10, 'deterministic_pass': 10, 'deterministic_fail': 0, 'leakage_flags': 0, 'corrective_retry_used': 0, 'format_corrective_used': 6, 'format_corrective_pass': 6}
- `checks_reproduced`: True
- `format_corrective_items`: ['BI-P2B-0001', 'BI-P2B-0002', 'BI-P2B-0006', 'BI-P2B-0008', 'BI-P2B-0009', 'BI-P2B-0010']
- `http_retries_recovered`: [{'seed_id': 'SD2-TP1-00069', 'reason': 'RemoteDisconnected: Remote end closed connection without res'}, {'seed_id': 'SD2-TP1-02787', 'reason': 'HTTP 502 <html>'}]
- `items`: [{'item_id': 'BI-P2B-0001', 'sha256': '03b49f1a72ac694d852fe680ca5cd7cb01ff8bd77b2c28d38225c935b791d9e7', 'status': 'human_review'}, {'item_id': 'BI-P2B-0002', 'sha256': 'e2330ede9d52a948af5ca4d668da6b436ac152a661d29a67ec62076e0c628811', 'status': 'human_review'}, {'item_id': 'BI-P2B-0003', 'sha256': '825532bcb130438f1796a57da14336128534be130ac4fa6342a33c9e1eb8e740', 'status': 'human_review'}, {'item_id': 'BI-P2B-0004', 'sha256': 'b4eecd80826d617e44e0753898a6c8cbe4cfb56232db825bbf7afff943c875f1', 'status': 'human_review'}, {'item_id': 'BI-P2B-0005', 'sha256': '31d4d4ddd466404b2c7916846f3a24db87301aae2e239291c45d85cfe012f591', 'status': 'human_review'}, {'item_id': 'BI-P2B-0006', 'sha256': '78f1d9309ab6ecee03582a1591d321840b8e1d03851eb345f62cca0751fc13be', 'status': 'human_review'}, {'item_id': 'BI-P2B-0007', 'sha256': '9a35b197dd323c27d1afd106ae508c6f9000ca58aa425cffc74382778c0154be', 'status': 'human_review'}, {'item_id': 'BI-P2B-0008', 'sha256': '7a378fd3ef29de6a14aff7348617aa4ace5981a7b7a082ac3fbff61b02cc7144', 'status': 'human_review'}, {'item_id': 'BI-P2B-0009', 'sha256': '28f33d49cc1747ee47b78caba64c3aa8609dca35a482d092d84f2051a1c912b8', 'status': 'human_review'}, {'item_id': 'BI-P2B-0010', 'sha256': '11c4139cd03061f23cbee949880a9966db1f1d8592ff74197da3180382555853', 'status': 'human_review'}]
