#!/usr/bin/env python3
"""M4-WP1 Phase A: freeze the ten-item sample before any corpus file is opened.

Reads `artifacts/literature/corpus_manifest.json`, verifies its SHA-256 against
the corpus identity in `data/manifest.json` (fail closed), applies the rule in
`climrr.litsample`, and writes `artifacts/literature/wp1_sample.json`. Opens no
corpus file. The artifact has no timestamp, so a re-run reproduces it byte for
byte --- and if it already exists, the re-run must reproduce it or fail.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litsample  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

CORPUS_MANIFEST = REPO_ROOT / "artifacts" / "literature" / "corpus_manifest.json"
DATA_MANIFEST = REPO_ROOT / "data" / "manifest.json"
OUT = REPO_ROOT / "artifacts" / "literature" / "wp1_sample.json"


def build() -> dict:
    pinned = next(
        c for c in json.loads(DATA_MANIFEST.read_text(encoding="utf-8"))["external_corpora"]
        if c["corpus_id"] == "LITCORPUS-00"
    )
    observed = sha256_file(CORPUS_MANIFEST)
    if observed != pinned["inventory_manifest_sha256"]:
        raise RuntimeError(
            f"corpus manifest SHA-256 {observed} does not match the pinned "
            f"{pinned['inventory_manifest_sha256']}. Stop and escalate."
        )
    manifest = json.loads(CORPUS_MANIFEST.read_text(encoding="utf-8"))
    drawn = litsample.draw(manifest["entries"])
    by_id = {e["item_id"]: e for e in manifest["entries"]}
    return {
        "artifact": "M4-WP1 deterministic sample",
        "decision_ref": "D-016",
        "corpus_id": manifest["corpus_id"],
        "corpus_manifest_path": repo_relative(CORPUS_MANIFEST),
        "corpus_manifest_sha256": observed,
        "rule": litsample.RULE_TEXT,
        "sample_size": litsample.SAMPLE_SIZE,
        "step": litsample.STEP,
        "item_ids": drawn["item_ids"],
        "skips": drawn["skips"],
        "items": [
            {k: by_id[i][k] for k in ("item_id", "relative_path", "bytes", "sha256", "duplicate_group")}
            for i in drawn["item_ids"]
        ],
        "representativeness": (
            "Ten items, deterministically sampled, for workflow validation; not "
            "representative of the corpus."
        ),
        "frozen_before_content_inspection": True,
    }


def main() -> int:
    sample = build()
    text = json.dumps(sample, indent=2, ensure_ascii=False) + "\n"
    if OUT.is_file() and OUT.read_text(encoding="utf-8") != text:
        print("FAIL: the rule no longer reproduces the frozen sample. Stop and escalate.", file=sys.stderr)
        return 1
    OUT.write_text(text, encoding="utf-8")
    print(f"  ids   : {', '.join(sample['item_ids'])}")
    print(f"  skips : {sample['skips'] or 'none'}")
    print(f"  wrote : {repo_relative(OUT)} sha256 {sha256_file(OUT)}")
    record = write_run_record(
        "sample_corpus",
        result_summary={"item_ids": sample["item_ids"], "skips": sample["skips"] or "none",
                        "sample_sha256": sha256_file(OUT)},
        passed=True,
        data_path=CORPUS_MANIFEST,
        data_sha256=sample["corpus_manifest_sha256"],
        output_path=OUT,
        config_snapshot={"rule": litsample.RULE_TEXT},
    )
    print(f"Run record: {repo_relative(record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
