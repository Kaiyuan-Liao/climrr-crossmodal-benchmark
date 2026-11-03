#!/usr/bin/env python3
"""Rubric lint over the pilot items (report only; D-056): v1 over the ten synthesis run-2 items, v1a over the current items.

`--version v1a` (default; mentor-export package): the current version of every pilot item from the items index
(`artifacts/benchmark/items/index.json`; run 2 for 0001--0009, run 3 for 0010), each checked against its index hash, with
the group strengths of the packet each was built from (read at the item's own source commit). Writes
`artifacts/benchmark/items/rubric_lint_v1a.json`. `--version v1` rebuilds the P2b-ingest-items report
`artifacts/benchmark/items/run2/rubric_lint_v1.json` over the run-2 items (packets v3a at the run's source commit).
Per item and rubric list the flagged lines, counts per item, totals. **No item is modified**; the flags are the
reviewer's checklist in the item review workbook. Rules: `src/climrr/rubric_lint.py`. No model call, no table value.

    python scripts/lint_item_rubrics.py [--version v1a|v1]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import litsynth_run2 as s2  # noqa: E402
from climrr import litsynth_run3 as s3  # noqa: E402
from climrr import rubric_lint as rl  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

OUT_PATHS = {"v1": s2.ART / "rubric_lint_v1.json", "v1a": s3.ITEMS_ROOT / "rubric_lint_v1a.json"}


def _v1_items() -> tuple[list[dict], dict, dict, Path]:
    man = json.loads(s2.MANIFEST_PATH.read_text(encoding="utf-8"))
    items, strengths = [], {}
    for x in man["items_ingested"]:
        path = s2.ART / x["path"]
        if sha256_file(path) != x["sha256"]:
            raise SystemExit(f"{x['path']} differs from the hash in the items manifest")
        it = json.loads(path.read_text(encoding="utf-8"))
        items.append(it)
        strengths[it["item_id"]] = s2.packet_at_source(it["review"]["history"][0]["seed_id"])[0]["checks_input"]["group_strength"]
    inputs = {"items_manifest_sha256": sha256_file(s2.MANIFEST_PATH), "packets": f"synthpackets v3a at {s2.SOURCE_COMMIT}"}
    return items, strengths, inputs, s2.MANIFEST_PATH


def _v1a_items() -> tuple[list[dict], dict, dict, Path]:
    items = s3.current_items()
    strengths = {it["item_id"]: s2.packet_for_item(it)["checks_input"]["group_strength"] for it in items}
    inputs = {"items_index_sha256": sha256_file(s3.INDEX_PATH),
              "packets": "each item's packet at its own source commit (v3a at 1f175da for 0001-0009, v3b at 157c96c for 0010)"}
    return items, strengths, inputs, s3.INDEX_PATH


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", choices=sorted(OUT_PATHS), default="v1a")
    a = ap.parse_args()
    version = {"v1": rl.VERSION_V1, "v1a": rl.VERSION}[a.version]
    out_path = OUT_PATHS[a.version]

    items, strengths, inputs, data_path = _v1_items() if a.version == "v1" else _v1a_items()
    before = {it["item_id"]: json.dumps(it, sort_keys=True) for it in items}
    report = rl.lint(items, strengths, version)
    report["inputs"] = inputs
    r2.write_json(out_path, report)
    again = _v1_items()[0] if a.version == "v1" else s3.current_items()
    if any(json.dumps(it, sort_keys=True) != before[it["item_id"]] for it in again):
        raise SystemExit("an item file changed during the lint")

    result = {"lint_sha256": sha256_file(out_path), "version": version, "totals": report["totals"],
              "per_item": {x["item_id"]: {"n_flags": x["n_flags"], **{r: n for r, n in x["counts"].items() if n}} for x in report["items"]}}
    rec = write_run_record("lint_item_rubrics", result_summary=result, passed=True, data_path=data_path, output_path=out_path,
                           config_snapshot={"version": version, "rules": rl.rules(version), "model_calls": 0, "items_modified": 0})
    print(json.dumps(result, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
