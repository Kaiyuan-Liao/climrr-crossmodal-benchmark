#!/usr/bin/env python3
"""Pilot P2b-ingest-items Phase B: rubric lint v1 over the ten synthesis run-2 items (report only; D-056).

Reads the ingested items (`artifacts/benchmark/items/run2/items/<item_id>.json`, each checked against
`manifest.json`) and, for the group strengths, the packet each was built from (packets v3a at the run's source
commit). Writes `artifacts/benchmark/items/run2/rubric_lint_v1.json`: per item and rubric list the flagged lines,
counts per item, totals. **No item is modified**; the flags are the reviewer's checklist in the item review workbook.
Rules: `src/climrr/rubric_lint.py`. No model call, no table value.

    python scripts/lint_item_rubrics.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import litsynth_run2 as s2  # noqa: E402
from climrr import rubric_lint as rl  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

OUT_PATH = s2.ART / "rubric_lint_v1.json"


def main() -> int:
    man = json.loads(s2.MANIFEST_PATH.read_text(encoding="utf-8"))
    items, strengths = [], {}
    for x in man["items_ingested"]:
        path = s2.ART / x["path"]
        if sha256_file(path) != x["sha256"]:
            raise SystemExit(f"{x['path']} differs from the hash in the items manifest")
        it = json.loads(path.read_text(encoding="utf-8"))
        items.append(it)
        strengths[it["item_id"]] = s2.packet_at_source(it["review"]["history"][0]["seed_id"])[0]["checks_input"]["group_strength"]
    before = {x["item_id"]: x["sha256"] for x in man["items_ingested"]}
    report = rl.lint(items, strengths)
    report["inputs"] = {"items_manifest_sha256": sha256_file(s2.MANIFEST_PATH), "packets": f"synthpackets v3a at {s2.SOURCE_COMMIT}"}
    r2.write_json(OUT_PATH, report)
    if any(sha256_file(s2.ART / x["path"]) != before[x["item_id"]] for x in man["items_ingested"]):
        raise SystemExit("an item file changed during the lint")

    result = {"lint_sha256": sha256_file(OUT_PATH), "totals": report["totals"],
              "per_item": {x["item_id"]: {"n_flags": x["n_flags"], **{r: n for r, n in x["counts"].items() if n}} for x in report["items"]}}
    rec = write_run_record("lint_item_rubrics", result_summary=result, passed=True, data_path=s2.MANIFEST_PATH, output_path=OUT_PATH,
                           config_snapshot={"version": rl.VERSION, "rules": rl.RULES, "model_calls": 0, "items_modified": 0})
    print(json.dumps(result, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
