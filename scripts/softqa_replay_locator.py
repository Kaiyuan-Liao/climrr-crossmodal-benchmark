#!/usr/bin/env python3
"""Replay agent v2's passage locator over the Track C run-1 proposals (D-033; Track C run 1 diagnosis).

Run 1 used agent v1, whose re-slice was exact-only. This script loads the
**tracked** agent (v2) and runs its `locate_passage` on every run-1 proposal's
passage, against the paper sections rebuilt from each paper's `prompt_user.txt`
(which stays outside the repository: pass the extracted `softqa_run1.tar.gz`).
Each prompt's SHA-256 is checked against `artifacts/softqa/run1/excluded_files.csv`
before use; untruncated papers must reproduce `paper_chars` and `n_sections`.

Writes `artifacts/softqa/run1_locator_replay_v2.json` (per proposal: recovery
method, span, recovered length and SHA-256 --- never the recovered text), pins it
in the `softqa_run1` diagnostics entry, and regenerates
`docs/SOFTQA_TRACKC_RUN1.md`. No model call; run 1's records are not changed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import softqa_run1 as r1  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted softqa_run1.tar.gz")
    a = ap.parse_args()

    if sha256_file(r1.AGENT) != r1.V2_AGENT_SHA256:
        raise SystemExit("the tracked agent is not v2")
    before = sha256_file(r1.RUN_MANIFEST)
    out = r1.replay(a.src / "softqa" / "run1")
    if r1.manifest_text() != r1.RUN_MANIFEST.read_text(encoding="utf-8") or sha256_file(r1.RUN_MANIFEST) != before:
        raise SystemExit("the ingested run 1 changed during the replay")
    r1.REPLAY_PATH.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    replay_sha = sha256_file(r1.REPLAY_PATH)

    data = json.loads(r1.MANIFEST.read_text(encoding="utf-8"))
    entry = next(d for d in data["diagnostics"] if d["diagnostic_id"] == r1.DIAGNOSTIC_ID)
    entry["locator_replay_v2"] = {"path": r1.repo_rel(r1.REPLAY_PATH), "sha256": replay_sha,
                                  "agent_sha256": r1.V2_AGENT_SHA256, "recovery": out["recovery"]}
    r1.MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    r1.DOC_PATH.write_text(r1.render_doc(), encoding="utf-8")

    summary = {k: out[k] for k in ("n_proposals", "recovery", "v1_to_v2", "recovered_reslice_ok",
                                   "v1_failures_in_truncated_papers", "input_checks")}
    summary["replay_sha256"] = replay_sha
    rec = write_run_record(
        "softqa_replay_locator", result_summary=summary, passed=True,
        data_path=r1.RUN_DIR / "candidates.jsonl", output_path=r1.REPLAY_PATH,
        config_snapshot={"agent_sha256": r1.V2_AGENT_SHA256, "run1_manifest_sha256": before,
                         "sections_from": "prompt_user.txt of the extracted tarball (hash-checked)",
                         "source_tarball_sha256": r1.TARBALL_SHA256},
    )
    print(json.dumps(summary, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
