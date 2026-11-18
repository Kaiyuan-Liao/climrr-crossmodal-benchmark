#!/usr/bin/env python3
"""Work package P3b, section A: ingest synthesis run 4 (litsynth_agent v4, packets v4a) and polish run 1 (litpolish_agent v1).

Takes `litsynth_run4_polish_run1_evidence.tar.gz` extracted outside the repository. Verifies it against every fact the work
package states and fails on any difference (`climrr.litsynth_run4.verify_source`). Re-assembles every item from its raw
response with the pinned v4 agent and re-runs post-checks v3 against packets v4a at the source commit `2601920`; re-extracts
every rewrite with the pinned v1 polish agent and re-runs polish checks v1a (`checks_reproduced`, both runs). Replays polish
checks v2 on the run-1 rewrites as a diagnostic (no status changed). Copies the run files into
`artifacts/benchmark/items/run4/` and `artifacts/benchmark/polish/run1/` (prompts, raw responses and per-item files: SHA-256
in the manifests only), writes `items/<item_id>.json` (six items in human_review, BI-P3-0007 rejected_pre_review) and both
`manifest.json`. Prints, per polished item, the rejection reasons verbatim and the original next to the rewrite.

Rerunnable: every copy must be byte-identical, and an existing manifest keeps its `ingested_at`.
No model call, no table value.

    python scripts/ingest_litsynth_run4.py --src <extracted tarball> --tarball <litsynth_run4_polish_run1_evidence.tar.gz>
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
from climrr import litsynth_run4 as s4  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted litsynth_run4_polish_run1_evidence.tar.gz")
    ap.add_argument("--tarball", type=Path, help="the tarball itself, checked against its SHA-256")
    a = ap.parse_args()

    if a.tarball and sha256_file(a.tarball) != s4.TARBALL_SHA256:
        raise SystemExit(f"{a.tarball.name} is not the delivered tarball {s4.TARBALL_SHA256}")
    facts = s4.verify_source(a.src)
    items = s4.read_item_files(a.src)
    reproduced = s4.reproduce_synthesis(items)
    p_reproduced = s4.reproduce_polish(a.src)
    replay = s4.replay_polish_v2(a.src)
    copied = s4.copy_runs(a.src)

    previous = json.loads(s4.MANIFEST_PATH.read_text(encoding="utf-8")) if s4.MANIFEST_PATH.exists() else {}
    at = previous.get("ingested_at") or s2.now_utc()
    written = s4.write_items(a.src, items, at)
    r2.write_json(s4.MANIFEST_PATH, s4.manifest(facts, reproduced, written, a.src, at))
    r2.write_json(s4.POLISH_MANIFEST_PATH, s4.polish_manifest(facts, p_reproduced, replay, a.src, at))

    recs = {r["item_id"]: r for r in s2.read_items(s4.POLISH_ART / "polished.jsonl")}
    v2 = {x["item_id"]: x for x in replay["items"]}
    polish = [{"item_id": i, "status": r["status"], "reasons_v1a": r["reasons"],
               "texts": {f: {"original": r["pre_polish"][f], "polished": r["polished"][f]} for f in ("prompt", "answer")},
               "prompt_unchanged_by_polisher": r["pre_polish"]["prompt"] == r["polished"]["prompt"],
               "replay_v2": {"pass": v2[i]["pass"], "reasons": v2[i]["reasons"]}} for i, r in sorted(recs.items())]
    result = {"manifest_sha256": sha256_file(s4.MANIFEST_PATH), "polish_manifest_sha256": sha256_file(s4.POLISH_MANIFEST_PATH),
              "files_copied_this_run": copied, "counts": dict(s4.RUN_FACTS), "polish_counts": dict(s4.POLISH_FACTS),
              "checks_reproduced": {"synthesis": reproduced["checks_reproduced"], "polish": p_reproduced["checks_reproduced"]},
              "items": [{k: x[k] for k in ("item_id", "sha256", "status", "history")} for x in written],
              "rejected_pre_review": s4.REJECTED, "polish": polish}
    rec = write_run_record(
        "ingest_litsynth_run4", result_summary=result, passed=True, data_path=a.tarball, output_path=s4.ART,
        data_sha256=None if a.tarball else s4.TARBALL_SHA256,
        config_snapshot={"source": f"{s4.TARBALL_NAME} (extracted)", "source_tarball_sha256": s4.TARBALL_SHA256,
                         "packets": f"synthpackets v4a at {s4.SOURCE_COMMIT}", "synthesis_check_version": reproduced["check_version"],
                         "polish_check_version": p_reproduced["check_version"], "polish_replay_check_version": replay["check_version"],
                         "run_executed_on": "Polaris; this record is the local ingest, not the runs", "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
