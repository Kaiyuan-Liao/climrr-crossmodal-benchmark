#!/usr/bin/env python3
"""Pilot P2b-ingest-items Phase A: ingest synthesis run 2 (litsynth_agent v3.2, Polaris, Sophia vLLM; D-055b, D-056).

Takes `litsynth_runs012_evidence.tar.gz` extracted outside the repository. Verifies it against every fact the work
package states (hashes; agent, system-prompt and format-corrective-template SHA-256; 10 items, 10 deterministic_pass,
0 leakage flags; the format corrective turn on 0001, 0002, 0006, 0008, 0009, 0010; the recovered HTTP retries;
endpoint and budget; every packet equal to packets v3a at the source commit `1f175da`; the logs) and fails on any
difference. Re-assembles each item from its raw response with the pinned agent and re-runs post-checks v2.2 against
its v3a packet: both must equal the recorded results (`checks_reproduced`). Copies the run files into
`artifacts/benchmark/items/run2/` (the two superseded runs' logs and summaries under `superseded/`; prompts and raw
responses: SHA-256 in `manifest.json` only), writes `items/<item_id>.json` with `review.status: human_review` (D-033
lifecycle), each validated against item schema v2, and `manifest.json`. Rules: `src/climrr/litsynth_run2.py`.

Rerunnable: every copy must be byte-identical, and an existing manifest keeps its `ingested_at`.
No model call, no table value.

    python scripts/ingest_litsynth.py --src <extracted tarball> --tarball <litsynth_runs012_evidence.tar.gz>
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
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted litsynth_runs012_evidence.tar.gz")
    ap.add_argument("--tarball", type=Path, help="the tarball itself, checked against its SHA-256")
    a = ap.parse_args()

    if a.tarball and sha256_file(a.tarball) != s2.TARBALL_SHA256:
        raise SystemExit(f"{a.tarball.name} is not the delivered tarball {s2.TARBALL_SHA256}")
    facts = s2.verify_source(a.src)
    items = s2.read_item_files(a.src)
    reproduced = s2.reproduce_checks(items)
    copied = s2.copy_run(a.src)

    previous = json.loads(s2.MANIFEST_PATH.read_text(encoding="utf-8")) if s2.MANIFEST_PATH.exists() else {}
    at = previous.get("ingested_at") or s2.now_utc()
    written = s2.write_items(items, at)
    man = s2.manifest(facts, reproduced, written, s2.excluded_files(a.src), at)
    r2.write_json(s2.MANIFEST_PATH, man)

    result = {"manifest_sha256": sha256_file(s2.MANIFEST_PATH), "files_copied_this_run": copied, "files_in_manifest": len(man["files"]),
              "excluded_files": len(man["excluded_files"]), "counts": man["counts"], "checks_reproduced": man["checks_reproduced"],
              "format_corrective_items": man["format_corrective_items"], "http_retries_recovered": man["http_retries_recovered"],
              "items": [{k: x[k] for k in ("item_id", "sha256", "status")} for x in written]}
    rec = write_run_record(
        "ingest_litsynth", result_summary=result, passed=True, data_path=a.tarball, output_path=s2.ART,
        data_sha256=None if a.tarball else s2.TARBALL_SHA256,
        config_snapshot={"source": f"{s2.TARBALL_NAME} (extracted)", "source_tarball_sha256": s2.TARBALL_SHA256,
                         "packets": f"synthpackets v3a at {s2.SOURCE_COMMIT}", "check_version": reproduced["check_version"],
                         "run_executed_on": "Polaris; this record is the local ingest, not the run", "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
