#!/usr/bin/env python3
"""Work package P5d, section A: ingest infra synthesis runs 1 -- 2 and polish infra runs 1 -- 2 (D-079, D-080).

Takes `infra_synth_runs12_evidence.tar.gz` extracted outside the repository. Verifies it against every fact the work
package states and fails on any difference (`climrr.litsynth_infra_run2.verify_source`). Re-assembles every item and
superseded attempt from its raw response with the pinned agent (v5.4 at `bf69970` for run 2, v5.3 at `b860658` for run 1)
and re-runs its post-checks (v3.5 / packets v1b; v3.4 / packets v1a); re-extracts every rewrite with the pinned polish agent
v1.1 and re-runs polish checks v2 (`checks_reproduced`). Applies the D-079 display rule (post-checks v3.5 re-run on each
polished text). Copies the run files into `artifacts/benchmark/items/infra_run2/` (the three first attempts into
`superseded/`), `artifacts/benchmark/polish/infra_run2/`, and the superseded run 1 into `items/infra_run1/` and
`polish/infra_run1/` (prompts, raw responses and per-item files: SHA-256 in the manifests only); writes `items/<item_id>.json`
(six in human_review with display_source and display_recheck; BI-P5-0003 and 0005 rejected_pre_review, redraws 2) and the
four manifests, including the run-1 regression fixture (its two passing items under post-checks v3.5).

Rerunnable: every copy must be byte-identical, and an existing manifest keeps its `ingested_at`.
No model call, no table value.

    python scripts/ingest_litsynth_infra_run2.py --src <extracted tarball> --tarball <infra_synth_runs12_evidence.tar.gz>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import litsynth_infra_run2 as ir  # noqa: E402
from climrr import litsynth_run2 as s2  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted infra_synth_runs12_evidence.tar.gz")
    ap.add_argument("--tarball", type=Path, help="the tarball itself, checked against its SHA-256")
    a = ap.parse_args()

    if a.tarball and sha256_file(a.tarball) != ir.TARBALL_SHA256:
        raise SystemExit(f"{a.tarball.name} is not the delivered tarball {ir.TARBALL_SHA256}")
    facts = ir.verify_source(a.src)
    items, items1 = ir.read_item_files(a.src), ir.read_item_files(a.src, 1)
    reproduced = ir.reproduce_synthesis(items, ir.read_attempts(a.src), items1)
    p_reproduced = ir.reproduce_polish(a.src, [it for it in items if it["item_id"] in ir.PASSING],
                                       [it for it in items1 if it["item_id"] in ir.RUN1_PASSING])
    regression = ir.run1_regression(items1)
    copied = ir.copy_runs(a.src)

    previous = json.loads(ir.MANIFEST_PATH.read_text(encoding="utf-8")) if ir.MANIFEST_PATH.exists() else {}
    at = previous.get("ingested_at") or s2.now_utc()
    written = ir.write_items(a.src, items, at)
    r2.write_json(ir.MANIFEST_PATH, ir.manifest(facts, reproduced, written, regression, a.src, at))
    r2.write_json(ir.POLISH_MANIFEST_PATH, ir.polish_manifest(facts, p_reproduced, written, a.src, at))
    r2.write_json(ir.MANIFEST1_PATH, ir.run1_manifest(facts, reproduced, regression, a.src, at))
    r2.write_json(ir.POLISH_MANIFEST1_PATH, ir.run1_polish_manifest(p_reproduced, a.src, at))

    result = {"manifest_sha256": sha256_file(ir.MANIFEST_PATH), "polish_manifest_sha256": sha256_file(ir.POLISH_MANIFEST_PATH),
              "run1_manifest_sha256": sha256_file(ir.MANIFEST1_PATH),
              "run1_polish_manifest_sha256": sha256_file(ir.POLISH_MANIFEST1_PATH),
              "files_copied_this_run": copied, "counts": dict(ir.RUN_FACTS), "polish_counts": dict(ir.POLISH_FACTS),
              "checks_reproduced": {"synthesis": reproduced["checks_reproduced"], "polish": p_reproduced["checks_reproduced"]},
              "items": [{k: x[k] for k in ("item_id", "sha256", "status", "display_source", "display_recheck", "redraws") if k in x}
                        for x in written],
              "superseded_attempts": {k: v["reasons"] for k, v in reproduced["superseded_attempts"].items()},
              "run1_regression": [{k: x[k] for k in ("item_id", "pass", "reasons")} | {"budget_within": x["budget"]["within"],
                                                                                     "budget_enforced": x["budget"]["enforced"]}
                                  for x in regression]}
    rec = write_run_record(
        "ingest_litsynth_infra_run2", result_summary=result, passed=True, data_path=a.tarball, output_path=ir.ART,
        data_sha256=None if a.tarball else ir.TARBALL_SHA256,
        config_snapshot={"source": f"{ir.TARBALL_NAME} (extracted)", "source_tarball_sha256": ir.TARBALL_SHA256,
                         "packets": f"synthpackets infra v1b at {ir.SOURCE_COMMIT}; run 1: v1a at {ir.RUN1_SOURCE_COMMIT}",
                         "synthesis_check_version": ir.CHECK_VERSION, "display_rule": ir.DISPLAY_RULE,
                         "polish_check_version": p_reproduced["check_version"],
                         "run_executed_on": "Polaris; this record is the local ingest, not the runs", "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
