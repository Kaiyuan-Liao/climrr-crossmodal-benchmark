#!/usr/bin/env python3
"""Work package P3c, section A: ingest synthesis run 5 (litsynth_agent v4.1, packets v4b) and polish run 2 (litpolish_agent v1.1).

Takes `litsynth_run5_polish_run2_evidence.tar.gz` extracted outside the repository. Verifies it against every fact the work
package states and fails on any difference (`climrr.litsynth_run5.verify_source`). Re-assembles every item and the superseded
first attempt of BI-P3-0007 from its raw response with the pinned v4.1 agent and re-runs post-checks v3.1 against packets v4b
at the source commit `f6f7543`; re-extracts every rewrite with the pinned v1.1 polish agent and re-runs polish checks v2
(`checks_reproduced`, both runs). Copies the run files into `artifacts/benchmark/items/run5/` and
`artifacts/benchmark/polish/run2/` (prompts, raw responses and per-item files: SHA-256 in the manifests only), the superseded
attempt into `items/run5/superseded/`, writes `items/<item_id>.json` (seven items in human_review, each with its
display_source) and both `manifest.json`. Prints, per polish-rejected item, the reasons verbatim and the rewrite next to the
original.

Rerunnable: every copy must be byte-identical, and an existing manifest keeps its `ingested_at`.
No model call, no table value.

    python scripts/ingest_litsynth_run5.py --src <extracted tarball> --tarball <litsynth_run5_polish_run2_evidence.tar.gz>
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
from climrr import litsynth_run5 as s5  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted litsynth_run5_polish_run2_evidence.tar.gz")
    ap.add_argument("--tarball", type=Path, help="the tarball itself, checked against its SHA-256")
    a = ap.parse_args()

    if a.tarball and sha256_file(a.tarball) != s5.TARBALL_SHA256:
        raise SystemExit(f"{a.tarball.name} is not the delivered tarball {s5.TARBALL_SHA256}")
    facts = s5.verify_source(a.src)
    items = s5.read_item_files(a.src)
    reproduced = s5.reproduce_synthesis(items, s5.read_attempt(a.src))
    p_reproduced = s5.reproduce_polish(a.src, items)
    copied = s5.copy_runs(a.src)

    previous = json.loads(s5.MANIFEST_PATH.read_text(encoding="utf-8")) if s5.MANIFEST_PATH.exists() else {}
    at = previous.get("ingested_at") or s2.now_utc()
    written = s5.write_items(a.src, items, at)
    r2.write_json(s5.MANIFEST_PATH, s5.manifest(facts, reproduced, written, a.src, at))
    r2.write_json(s5.POLISH_MANIFEST_PATH, s5.polish_manifest(facts, p_reproduced, a.src, at))

    recs = {r["item_id"]: r for r in s2.read_items(s5.POLISH_ART / "polished.jsonl")}
    rejected = [{"item_id": i, "reasons": r["reasons"],
                 "texts": {f: {"original": r["pre_polish"][f], "polished": r["polished"][f]} for f in ("prompt", "answer")},
                 "prompt_unchanged_by_polisher": r["pre_polish"]["prompt"] == r["polished"]["prompt"]}
                for i, r in sorted(recs.items()) if r["status"] != "polished"]
    result = {"manifest_sha256": sha256_file(s5.MANIFEST_PATH), "polish_manifest_sha256": sha256_file(s5.POLISH_MANIFEST_PATH),
              "files_copied_this_run": copied, "counts": dict(s5.RUN_FACTS), "polish_counts": dict(s5.POLISH_FACTS),
              "checks_reproduced": {"synthesis": reproduced["checks_reproduced"], "polish": p_reproduced["checks_reproduced"]},
              "items": [{k: x[k] for k in ("item_id", "sha256", "status", "display_source", "history")} for x in written],
              "superseded_attempt": reproduced["superseded_attempt"], "pre_run": {k: facts["log"][k] for k in
                                                                                ("pre_run_auth_failures", "pre_run_auth_failed_seeds")},
              "polish_rejected": rejected,
              "prompts_changed_by_polisher": sorted(i for i, r in recs.items() if r["pre_polish"]["prompt"] != r["polished"]["prompt"])}
    rec = write_run_record(
        "ingest_litsynth_run5", result_summary=result, passed=True, data_path=a.tarball, output_path=s5.ART,
        data_sha256=None if a.tarball else s5.TARBALL_SHA256,
        config_snapshot={"source": f"{s5.TARBALL_NAME} (extracted)", "source_tarball_sha256": s5.TARBALL_SHA256,
                         "packets": f"synthpackets v4b at {s5.SOURCE_COMMIT}", "synthesis_check_version": reproduced["check_version"],
                         "polish_check_version": p_reproduced["check_version"],
                         "run_executed_on": "Polaris; this record is the local ingest, not the runs", "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
