#!/usr/bin/env python3
"""M4-WP4: freeze the 10 + 10 place-candidate sample (D-025) before any paper is opened.

Writes `artifacts/literature/wp4_sample.json` and `wp4_sample_fetch.txt` once
and records the sample in `data/manifest.json`; a later run verifies and fails
on any difference. See `climrr.wp4sample`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import wp4sample  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

DATA_MANIFEST = REPO_ROOT / "data" / "manifest.json"
KEY = "wp4_sample"


def main() -> int:
    try:
        if wp4sample.SAMPLE_PATH.exists():
            wp4sample.verify()
            action = "verified"
        else:
            wp4sample.write()
            action = "written"
    except wp4sample.SampleError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    sha = sha256_file(wp4sample.SAMPLE_PATH)
    doc = json.loads(wp4sample.SAMPLE_PATH.read_text(encoding="utf-8"))

    data = json.loads(DATA_MANIFEST.read_text(encoding="utf-8"))
    entry = {"path": repo_relative(wp4sample.SAMPLE_PATH), "wp4_sample_sha256": sha,
             "fetch_list_path": repo_relative(wp4sample.FETCH_PATH),
             "fetch_list_sha256": sha256_file(wp4sample.FETCH_PATH),
             "n_selected": doc["n_selected"], "corpus_id": doc["corpus_id"], "decision_ref": "D-025",
             "statement": "frozen before reading"}
    l2 = next(c for c in data["external_corpora"] if c["corpus_id"] == doc["corpus_id"])
    if KEY in l2 and l2[KEY]["wp4_sample_sha256"] != sha:
        print("FAIL: data/manifest.json records a different wp4_sample_sha256", file=sys.stderr)
        return 1
    l2[KEY] = entry
    DATA_MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for s in doc["selected"]:
        adv = f"  (advanced from {s['target_rank']}: {'; '.join(s['advance_reasons'])})" if s["advanced"] else ""
        print(f"  {s['arm']:16} rank {s['rank']:3}  {s['lit2_id']}  {s['item_id']:>10}  {s['sha256'][:12]}{adv}")
    print(f"  {action}: {doc['n_selected']} items; wp4_sample_sha256 {sha}")
    rec = write_run_record("wp4_sample", result_summary={"action": action, "wp4_sample_sha256": sha,
                                                          "n_selected": doc["n_selected"],
                                                          "suppressed": {a: v["n_suppressed"] for a, v in doc["arms"].items()}},
                           passed=True, data_path=wp4sample.L2 / "place_candidates" / "place_candidates.json",
                           output_path=wp4sample.SAMPLE_PATH, config_snapshot={"arms": list(wp4sample.ARMS),
                                                                               "step": wp4sample.STEP})
    print(f"Run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
