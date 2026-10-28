# Run record: 20261028T041215Z_local_softqa_replay_locator

- **Result**: PASS
- **UTC timestamp**: 2026-10-28T04:12:15.756298+00:00
- **Git commit**: `95e1ec851f2ac703654df52ac1ccc9c3d777fcd7`
- **Working tree dirty (tracked files)**: True
- **Untracked files present**: 271
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `artifacts/softqa/run1/candidates.jsonl`
- **Data SHA-256**: `efed98e5bc485523ef6bee3b55489ef3e7e3a912936b1ace590d57c7c3628f84`
- **Output path**: `artifacts/softqa/run1_locator_replay_v2.json`

## Config snapshot

```json
{
  "agent_sha256": "25a79a5b8bebbb67c8e080b05d08b736ee40ea62fbe3fc891d86cfab22f63b9c",
  "run1_manifest_sha256": "c0c193695023d08435e4fed0451f4ef445aa429f68bb43780ab638bd5b26b3d9",
  "sections_from": "prompt_user.txt of the extracted tarball (hash-checked)",
  "source_tarball_sha256": "8a0e444996cc09a87c848aa9013e228d39a3f831e7a701519eb7db41f3654e3e"
}
```

## Result summary

- `n_proposals`: 193
- `recovery`: {'exact': 117, 'normalized': 8, 'prefix_anchor': 34, 'not_found': 34}
- `v1_to_v2`: {'v1_fail->normalized': 8, 'v1_fail->not_found': 34, 'v1_fail->prefix_anchor': 34, 'v1_pass->exact': 117}
- `recovered_reslice_ok`: 159
- `v1_failures_in_truncated_papers`: 11
- `input_checks`: {'prompt_sha256_match': 243, 'untruncated_reproduce_paper_chars_and_n_sections': 222, 'truncated': 21}
- `replay_sha256`: 33bc04949b8e24d11e48c128725b4a8e5d376cc16d62295afb672f5be7056898
