#!/usr/bin/env python3
"""M4-WP3 Phase B: apply R-FWI-1 v1 retroactively to the LITCORPUS-01 fire-weather arm (4 records).

**For Kaiyuan to run on Polaris**; the four raw records are on Eagle only. Lexical
only: each record is SHA-256-verified against
`artifacts/literature/litcorpus01/evidence/litcorpus01_raw_hashes.txt`, decoded as
JSON, and every string value at any depth (keys are not scanned) is passed to
`climrr.retrieval.evaluate`. Nothing is read for meaning; the output keeps only
hit locations and the matched characters.

Usage (from a checkout of the pinned commit):
    python scripts/litcollect/apply_rfwi1_litcorpus01.py --raw-parent <dir holding raw/fire_weather_v1/>

Writes `artifacts/literature/litcorpus01/rfwi1_retroactive.json` and a run record.
Fails, writing nothing, on any hash mismatch or missing record.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import retrieval  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.litcorpus import L1_DIR, read_hash_list  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.wp2retrieve import string_values  # noqa: E402

ARM = "fire_weather_v1"
OUT = L1_DIR / "rfwi1_retroactive.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-parent", type=Path, required=True)
    args = parser.parse_args(argv)
    hashes = {rel: d for rel, d in read_hash_list(L1_DIR / "evidence" / "litcorpus01_raw_hashes.txt").items()
              if rel.split("/")[1] == ARM}
    results = []
    for rel, expected in sorted(hashes.items()):
        path = args.raw_parent / rel
        if not path.is_file():
            print(f"FAIL: missing {rel}", file=sys.stderr)
            return 1
        actual = sha256_file(path)
        if actual != expected:
            print(f"FAIL: {rel} SHA-256 {actual} != {expected}", file=sys.stderr)
            return 1
        doc = json.loads(path.read_bytes().decode("utf-8"))
        decision = retrieval.evaluate(string_values(doc))
        results.append({"item_id": path.stem, "rel_path": rel, "sha256": actual, **decision})
    admitted = [r["item_id"] for r in results if r["eligible"]]
    out = {"corpus_id": "LITCORPUS-01-conceptfirst-v1", "arm": ARM, "rule": retrieval.RULE_TEXT,
           "section_key_note": "section_key is the JSON path of the string value",
           "n_records": len(results), "admitted_count": len(admitted), "admitted": admitted, "records": results}
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  R-FWI-1 v1 over {len(results)} records: {len(admitted)} admitted {admitted}")
    rec = write_run_record("apply_rfwi1_litcorpus01", result_summary={"admitted_count": len(admitted),
                                                                      "admitted": admitted},
                           passed=True, data_path=L1_DIR / "evidence" / "litcorpus01_raw_hashes.txt",
                           output_path=OUT, config_snapshot={"arm": ARM, "rule": f"{retrieval.RULE_ID} {retrieval.RULE_VERSION}"})
    print(f"Run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
