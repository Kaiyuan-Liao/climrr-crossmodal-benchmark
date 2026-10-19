#!/usr/bin/env python3
"""M4-WP3: freeze LITCORPUS-01 and LITCORPUS-02 records from the collection evidence bundle.

Usage:
    python scripts/freeze_litcorpus.py --evidence-tarball <path to litcorpus02_evidence.tar.gz>

The tarball is hashed, extracted to a temporary directory outside the repo, and
read; nothing in it is a paper. Writes `artifacts/literature/litcorpus01/`,
`artifacts/literature/litcorpus02/` (including `place_candidates/`) and the two
`external_corpora` entries in `data/manifest.json`. See `climrr.litcorpus`.
"""

from __future__ import annotations

import argparse
import json
import sys
import tarfile
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litcorpus  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

DATA_MANIFEST = REPO_ROOT / "data" / "manifest.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-tarball", type=Path, required=True)
    args = parser.parse_args(argv)
    tarball_sha = sha256_file(args.evidence_tarball)

    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(args.evidence_tarball, "r:gz") as tf:
            tf.extractall(tmp, filter="data")
        ev = Path(tmp)
        try:
            l1 = litcorpus.freeze_litcorpus01(ev)
            l2 = litcorpus.freeze_litcorpus02(ev)
        except litcorpus.FreezeError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1

    data = json.loads(DATA_MANIFEST.read_text(encoding="utf-8"))
    keep = [c for c in data["external_corpora"] if c["corpus_id"] not in (litcorpus.L1_ID, litcorpus.L2_ID)]
    data["external_corpora"] = keep + litcorpus.external_corpus_entries(l1, l2)
    DATA_MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    y1, y2 = l1["yields"], l2["yields"]
    print(f"  {litcorpus.L1_ID}: fire {y1['fire_weather_v1']['count']}, heat {y1['extreme_heat_v1']['count']}")
    print(f"  {litcorpus.L2_ID}: fire {y2['fire_weather_v1']['raw_count']} -> {y2['fire_weather_v1']['admitted_count']}, "
          f"heat {y2['extreme_heat_v1']['admitted_count']}; union {l2['stable_ids']['n']}")
    rec = write_run_record(
        "freeze_litcorpus",
        result_summary={"litcorpus01_items": y1["unique_production_items"], "litcorpus02_items": l2["stable_ids"]["n"],
                        "place_candidates": {q: a["candidates"] for q, a in l2["place_candidates"]["arms"].items()},
                        "litcorpus02_manifest_sha256": sha256_file(litcorpus.L2_DIR / "litcorpus02_manifest.json"),
                        "litcorpus01_manifest_sha256": l1["manifest"]["production_csv_sha256"]},
        passed=True, data_path=args.evidence_tarball, data_sha256=tarball_sha,
        output_path=litcorpus.L2_DIR, config_snapshot={"evidence_tarball": args.evidence_tarball.name},
    )
    print(f"Run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
