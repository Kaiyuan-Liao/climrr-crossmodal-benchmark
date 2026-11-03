#!/usr/bin/env python3
"""Mentor-export package Phase A: ingest synthesis run 3 (litsynth_agent v3.2, one packet, BI-P2B-0010; D-056, D-054a).

Takes `litsynth_run3_evidence.tar.gz` extracted outside the repository. Verifies it against every fact the work package
states (hashes; agent, system-prompt and format-corrective-template SHA-256; 1 item, `deterministic_pass`, no leakage
flag, no corrective turn; endpoint and budget; the packet equal to packets v3b at the source commit `157c96c`; the log)
and fails on any difference. Re-assembles the item from its raw response with the pinned agent and re-runs post-checks
v2.2 against its v3b packet (`checks_reproduced`). Copies the run files into `artifacts/benchmark/items/run3/` (prompt
and raw response: SHA-256 in `manifest.json` only), writes `items/BI-P2B-0010.json` with `review.status: human_review`,
validated against item schema v2, `manifest.json`, and the items index `artifacts/benchmark/items/index.json` (0010 now
points to run 3; the run-2 version is `superseded_by_run3`). Rules: `src/climrr/litsynth_run3.py`.

Rerunnable: every copy must be byte-identical, and an existing manifest keeps its `ingested_at`.
No model call, no table value.

    python scripts/ingest_litsynth_run3.py --src <extracted tarball> --tarball <litsynth_run3_evidence.tar.gz>
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
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted litsynth_run3_evidence.tar.gz")
    ap.add_argument("--tarball", type=Path, help="the tarball itself, checked against its SHA-256")
    a = ap.parse_args()

    if a.tarball and sha256_file(a.tarball) != s3.TARBALL_SHA256:
        raise SystemExit(f"{a.tarball.name} is not the delivered tarball {s3.TARBALL_SHA256}")
    facts = s3.verify_source(a.src)
    items = s3.read_item_files(a.src)
    reproduced = s2.reproduce_checks(items, commit=s3.SOURCE_COMMIT)
    copied = s3.copy_run(a.src)

    previous = json.loads(s3.MANIFEST_PATH.read_text(encoding="utf-8")) if s3.MANIFEST_PATH.exists() else {}
    at = previous.get("ingested_at") or s2.now_utc()
    written = s3.write_items(items, at)
    man = s3.manifest(facts, reproduced, written, s3.excluded_files(a.src), at)
    r2.write_json(s3.MANIFEST_PATH, man)
    r2.write_json(s3.INDEX_PATH, s3.index())

    idx = json.loads(s3.INDEX_PATH.read_text(encoding="utf-8"))
    result = {"manifest_sha256": sha256_file(s3.MANIFEST_PATH), "index_sha256": sha256_file(s3.INDEX_PATH),
              "files_copied_this_run": copied, "files_in_manifest": len(man["files"]), "excluded_files": len(man["excluded_files"]),
              "counts": man["counts"], "checks_reproduced": man["checks_reproduced"], "index_counts": idx["counts"],
              "items": [{k: x[k] for k in ("item_id", "sha256", "status")} for x in written],
              "superseded": [{"item_id": x["item_id"], "run": v["run"], "index_status": v["index_status"]}
                             for x in idx["items"] for v in x["versions"] if v["index_status"] != "current"]}
    rec = write_run_record(
        "ingest_litsynth_run3", result_summary=result, passed=True, data_path=a.tarball, output_path=s3.ART,
        data_sha256=None if a.tarball else s3.TARBALL_SHA256,
        config_snapshot={"source": f"{s3.TARBALL_NAME} (extracted)", "source_tarball_sha256": s3.TARBALL_SHA256,
                         "packets": f"synthpackets v3b at {s3.SOURCE_COMMIT}", "check_version": reproduced["check_version"],
                         "run_executed_on": "Polaris; this record is the local ingest, not the run", "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
