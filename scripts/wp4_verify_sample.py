#!/usr/bin/env python3
"""M4-WP4r1 Phase A: verify the frozen sample and all 20 fetched files before any is decoded.

1. `artifacts/literature/wp4_sample.json` must hash to `wp4_sample_sha256` in
   `data/manifest.json`, and its `selected` list to `selected_sha256`.
2. For each of the 20 selected items, `<litcorpus02_root>/<rel_path>` must
   exist and hash to the sample's `sha256`. **All 20 must match before any
   file is decoded**; this script hashes bytes only and decodes nothing.

Fails closed: any mismatch, missing file or missing key exits non-zero and the
run record says `passed: false`. Reads only the `litcorpus02_root` key of
`config/local_paths.yaml`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import get as get_local_path  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

import hashlib  # noqa: E402

SAMPLE = REPO_ROOT / "artifacts" / "literature" / "wp4_sample.json"
DATA_MANIFEST = REPO_ROOT / "data" / "manifest.json"
ROOT_KEY = "litcorpus02_root"


def manifest_entry() -> dict:
    manifest = json.loads(DATA_MANIFEST.read_text(encoding="utf-8"))
    found = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "wp4_sample" and isinstance(v, dict):
                    found.append(v)
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(manifest)
    if len(found) != 1:
        raise RuntimeError(f"expected one wp4_sample entry in data/manifest.json, found {len(found)}")
    return found[0]


def main() -> int:
    rows: list[dict] = []
    failures: list[str] = []
    entry = manifest_entry()
    sample_sha = sha256_file(SAMPLE)
    if sample_sha != entry["wp4_sample_sha256"]:
        failures.append(f"wp4_sample.json SHA-256 {sample_sha} != manifest {entry['wp4_sample_sha256']}")
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    selected = sample["selected"]
    sel_sha = hashlib.sha256(
        json.dumps(selected, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    if sel_sha != sample["selected_sha256"]:
        failures.append(f"selected_sha256 {sel_sha} != recorded {sample['selected_sha256']}")
    if len(selected) != 20 or len({s["lit2_id"] for s in selected}) != 20:
        failures.append("sample does not hold 20 distinct items")

    if not failures:
        root = Path(get_local_path(ROOT_KEY))
        for s in selected:
            path = root / s["rel_path"]
            observed = sha256_file(path) if path.is_file() else None
            ok = observed == s["sha256"]
            rows.append({"lit2_id": s["lit2_id"], "item_id": s["item_id"], "arm": s["arm"],
                         "rel_path": s["rel_path"], "expected_sha256": s["sha256"],
                         "observed_sha256": observed, "match": ok})
            if not ok:
                failures.append(f"{s['lit2_id']} {s['rel_path']}: {'missing' if observed is None else 'SHA-256 ' + observed}")

    passed = not failures
    for r in rows:
        print(f"  {r['lit2_id']}  {r['arm']:<16} {r['rel_path']:<22} {'OK' if r['match'] else 'MISMATCH'}")
    for f in failures:
        print(f"FAIL: {f}", file=sys.stderr)
    print(f"  {sum(r['match'] for r in rows)}/{len(selected)} files match; sample {'verified' if passed else 'NOT verified'}")
    record = write_run_record(
        "wp4_verify_sample",
        result_summary={
            "wp4_sample_sha256": sample_sha,
            "manifest_wp4_sample_sha256": entry["wp4_sample_sha256"],
            "selected_sha256": sel_sha,
            "n_selected": len(selected),
            "n_files_matched": sum(r["match"] for r in rows),
            "files": rows,
            "failures": failures,
            "decoded_any_file": False,
        },
        passed=passed,
        data_path=SAMPLE,
        data_sha256=sample_sha,
        config_snapshot={"corpus_root": f"config/local_paths.yaml:{ROOT_KEY}"},
    )
    print(f"Run record: {repo_relative(record)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
