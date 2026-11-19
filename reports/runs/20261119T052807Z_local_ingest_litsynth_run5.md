# Run record: 20261119T052807Z_local_ingest_litsynth_run5

- **Result**: PASS
- **UTC timestamp**: 2026-11-19T05:28:07.822483+00:00
- **Git commit**: `ab42cfd7cb793c241ad0c9941f5b295847bbf047`
- **Working tree dirty (tracked files)**: False
- **Untracked files present**: 0
- **Hostname**: ryous-MacBook-Pro-2.local
- **Location**: local
- **Python**: 3.11.16 (macOS-15.3-arm64-arm-64bit)
- **pip freeze SHA-256**: `d9af804d5018f7022ae9f4db0bb83a8d57104d2ff6ff5676d912d896f952bf51`
- **Pinned libraries (D-007)**: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`, `pypdfium2==5.13.0`
- **Data path (repo-relative)**: `litsynth_run5_polish_run2_evidence.tar.gz`
- **Data SHA-256**: `e092875e21152f262e0a903e6e2dde41254782e6053dacb07385696c523acc4b`
- **Output path**: `artifacts/benchmark/items/run5`

## Config snapshot

```json
{
  "source": "litsynth_run5_polish_run2_evidence.tar.gz (extracted)",
  "source_tarball_sha256": "e092875e21152f262e0a903e6e2dde41254782e6053dacb07385696c523acc4b",
  "packets": "synthpackets v4b at f6f7543c6b6bc225c6a635c84018a36074837cc1",
  "synthesis_check_version": "synthesis_post_checks v3.1",
  "polish_check_version": "polish_checks v2",
  "run_executed_on": "Polaris; this record is the local ingest, not the runs",
  "model_calls": 0
}
```

## Result summary

- `manifest_sha256`: 52a4cb57e43d3ce73fa8719320cd66dbb1a17468c54bdd6a435c90acb907936c
- `polish_manifest_sha256`: 0769478fa617e17539eebddeb0d320a73cc96892cf64587111274ae97bc3a6b7
- `files_copied_this_run`: 0
- `counts`: {'items': 7, 'deterministic_pass': 7, 'deterministic_fail': 0, 'leakage_flags': 0, 'corrective_retry_used': 0, 'format_corrective_used': 2, 'format_corrective_pass': 2, 'superseded_attempts': 1, 'pre_run_auth_failures': 2, 'restarts': 2}
- `polish_counts`: {'items': 7, 'polished': 5, 'polish_rejected': 2, 'polish_parse_failed': 0, 'reasons_by_kind': {'descriptor': 1, 'hedges': 1, 'length': 1}, 'skipped_not_deterministic_pass': []}
- `checks_reproduced`: {'synthesis': True, 'polish': True}
- `items`: [{'item_id': 'BI-P3-0001', 'sha256': '8bfbc78982c737a805d794a224f92fbf8ebca898d8c565b21e7291a6b7f122af', 'status': 'human_review', 'display_source': 'original', 'history': ['deterministic_pass', 'polish', 'human_review']}, {'item_id': 'BI-P3-0002', 'sha256': 'a12e2d264960a3eea30a7ae156a59e74267c57f0553df04837ca5d747ab8bec7', 'status': 'human_review', 'display_source': 'polished', 'history': ['deterministic_pass', 'polish', 'human_review']}, {'item_id': 'BI-P3-0003', 'sha256': '466385a2f0a23baeb83c9ff4593bb4d1e7599d6f3d3050c7d3639e4cbf0e5b90', 'status': 'human_review', 'display_source': 'polished', 'history': ['deterministic_pass', 'polish', 'human_review']}, {'item_id': 'BI-P3-0004', 'sha256': 'f69dc285119373e21c5e5af43f1c5c860674ac5a28aa95a16428f075d982cba6', 'status': 'human_review', 'display_source': 'polished', 'history': ['deterministic_pass', 'polish', 'human_review']}, {'item_id': 'BI-P3-0005', 'sha256': '40252c145fe7d1be0e5dcb031099d641d02403713a902b8bef1ce4d8824b7c1e', 'status': 'human_review', 'display_source': 'polished', 'history': ['deterministic_pass', 'polish', 'human_review']}, {'item_id': 'BI-P3-0007', 'sha256': '3c8d03c39e0e6068931b17c37e1a5ae5f84ad6dbd01ab446aa974b1338c08059', 'status': 'human_review', 'display_source': 'polished', 'history': ['deterministic_pass', 'polish', 'human_review']}, {'item_id': 'BI-P3-0008', 'sha256': '40bd18a4ebd6dab1fadbd738ae0440a443aca8d1ed6d5c462a99579c922ef351', 'status': 'human_review', 'display_source': 'original', 'history': ['deterministic_pass', 'polish', 'human_review']}]
- `superseded_attempt`: {'item_id': 'BI-P3-0007', 'pass': False, 'reasons': ['rubric.optional_points: exact_value_in_graded_text 31.4 (exact values belong to provenance)', 'rubric.optional_points: exact_value_in_graded_text 33.6 (exact values belong to provenance)', "literature_interpretation: fire-weather wording (an FWI is never fire occurrence): 'fires' in graded text"], 'first_check_reasons': None}
- `pre_run`: {'pre_run_auth_failures': 2, 'pre_run_auth_failed_seeds': ['SD2-TP1-00071', 'SD2-TP1-00271']}
- `polish_rejected`: [{'item_id': 'BI-P3-0001', 'reasons': ["answer: hedges differ (original ['show', 'shows'], polished ['show'])", "answer: descriptor phrase lost: comparison with other states: moderate (original ['a change similar to most states'])"], 'texts': {'prompt': {'original': 'How are dangerous heat‑index days projected to change in California during summer by mid-century under a high‑emissions future, and what physical mechanisms drive this change?', 'polished': 'How are dangerous heat‑index days projected to change in California during summer by mid-century under a high‑emissions future, and what physical mechanisms drive this change?'}, 'answer': {'original': 'In California during summer, dangerous heat‑index days are projected to show a moderate increase by mid-century under a high‑emissions future, a change similar to most states. Research shows that large‑scale warming, global warming‑driven heat‑wave intensification, and an intensified urban heat island effect at night are the main physical mechanisms behind this increase.', 'polished': 'In California during summer, dangerous heat‑index days are projected to show a moderate increase by mid-century under a high‑emissions future. This is a similar change to most states. Large‑scale warming drives the increase. Global warming‑driven heat‑wave intensification also contributes. An intensified urban heat island effect at night adds to the rise.'}}, 'prompt_unchanged_by_polisher': True}, {'item_id': 'BI-P3-0008', 'reasons': ['answer: length ratio 1.23 outside 0.6-1.2'], 'texts': {'prompt': {'original': 'How is fire‑weather danger projected to change in summer in Minnesota by late this century under a high‑emissions future, and what physical drivers are expected to cause this change?', 'polished': 'How is fire‑weather danger projected to change in summer in Minnesota by late this century under a high‑emissions future, and what physical drivers are expected to cause this change?'}, 'answer': {'original': 'In summer, fire‑weather danger in Minnesota is projected to show a slight increase, a change similar to most states, by late this century under a high‑emissions future. Research shows that higher temperatures and increased aridity dry fuels, creating more extreme fire‑weather conditions.', 'polished': 'In summer, fire‑weather danger in Minnesota is projected to show a slight increase. This is a change similar to most states. The increase occurs by late this century under a high‑emissions future. Research shows that higher temperatures dry fuels. Research shows that increased aridity also dries fuels. These conditions create more extreme fire‑weather.'}}, 'prompt_unchanged_by_polisher': True}]
- `prompts_changed_by_polisher`: []
