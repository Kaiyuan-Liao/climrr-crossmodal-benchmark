#!/usr/bin/env python3
"""M5-WP1 Phase A: freeze the 27 claims and 3 prototypes the matrix will read.

Writes `artifacts/bridges/m5wp1_inputs.json` on the first run. Every later run
**verifies** instead of rewriting, and fails if any claim file, claim record,
prototype file or prototype record has changed --- a changed input is a defect
to escalate, not a freeze to refresh.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import compat  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    if compat.INPUTS_PATH.exists():
        try:
            frozen = compat.verify_inputs()
        except compat.FreezeError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1
        action = "verified"
    else:
        frozen = compat.build_inputs()
        compat.BRIDGES.mkdir(parents=True, exist_ok=True)
        compat.INPUTS_PATH.write_text(json.dumps(frozen, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        action = "written"
    sha = sha256_file(compat.INPUTS_PATH)
    print(f"  {action}: {repo_relative(compat.INPUTS_PATH)}  sha256={sha}")
    print(f"  claims={frozen['n_claims']} prototypes={frozen['n_prototypes']} pairs={frozen['n_pairs']}")
    record = write_run_record(
        "freeze_m5wp1_inputs",
        result_summary={"action": action, "inputs_sha256": sha, "n_claims": frozen["n_claims"],
                        "n_prototypes": frozen["n_prototypes"], "n_pairs": frozen["n_pairs"],
                        "corpus_manifest_sha256": frozen["corpus_manifest_sha256"],
                        "csv_sha256": frozen["csv_sha256"]},
        passed=True,
        data_path=compat.INPUTS_PATH,
        data_sha256=sha,
        output_path=compat.INPUTS_PATH,
        config_snapshot={"prototype_ids": list(compat.PROTOTYPE_IDS)},
    )
    print(f"Run record: {repo_relative(record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
