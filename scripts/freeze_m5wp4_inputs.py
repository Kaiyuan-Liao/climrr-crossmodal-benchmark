#!/usr/bin/env python3
"""M5-WP4 step 1: freeze the inputs of the LITCORPUS-02 positive-case run before the matrix is written.

Writes `artifacts/bridges/m5wp4_inputs.json` once: every adjudicated WP4 claim
(all tiers, tier carried) with file and record hashes; P-CELL-1, P-COUNTY-1 and
**P-STATE-1 v2**; the concept-map (D-025), G-2-list, compatibility-rule and R-FWI-1
versions; and the hashes of the untouched M5-WP1 / M5-WP2 freezes. A later run
verifies and fails on any difference.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import m5wp4  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    current = m5wp4.build_inputs()
    if m5wp4.INPUTS_PATH.exists():
        try:
            m5wp4.verify_inputs()
        except m5wp4.FreezeError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1
        action = "verified"
    else:
        m5wp4.INPUTS_PATH.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        action = "written"
    sha = sha256_file(m5wp4.INPUTS_PATH)
    print(f"  {action}: {current['n_claims']} claims x {current['n_prototypes']} prototypes = {current['n_pairs']} pairs; sha256 {sha}")
    rec = write_run_record("freeze_m5wp4_inputs", result_summary={"action": action, "sha256": sha,
                                                                   "n_pairs": current["n_pairs"]},
                           passed=True, data_path=m5wp4.ADJ_DIR / "adjudication_summary.json",
                           output_path=m5wp4.INPUTS_PATH, config_snapshot={"prototypes": list(m5wp4.PROTOTYPE_FILES)})
    print(f"Run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
