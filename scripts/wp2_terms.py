#!/usr/bin/env python3
"""M4-WP2 retrieval, step 1: freeze the term list (`artifacts/literature/wp2_terms.json`).

Concept terms come from the `approved_lexical` entries of the concept map;
place terms are the exact State / NAME labels of the state- and county-level
prototypes. Written once; every later run verifies and fails on any change.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import wp2retrieve  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    terms = wp2retrieve.build_terms()
    try:
        action = wp2retrieve.write_or_verify(wp2retrieve.TERMS_PATH, terms)
    except wp2retrieve.RetrievalError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    sha = sha256_file(wp2retrieve.TERMS_PATH)
    for t in terms["terms"]:
        print(f"  {t['term_id']}  {t['term_class']:<8} {t['term']}")
    print(f"  {action}: {repo_relative(wp2retrieve.TERMS_PATH)} sha256={sha}")
    record = write_run_record(
        "wp2_terms",
        result_summary={"action": action, "terms_sha256": sha, "n_terms": len(terms["terms"]),
                        "terms": [[t["term_id"], t["term_class"], t["term"]] for t in terms["terms"]]},
        passed=True,
        data_path=REPO_ROOT / "data" / "metadata" / "concept_map.yaml",
        output_path=wp2retrieve.TERMS_PATH,
        config_snapshot={"place_prototypes": list(wp2retrieve.PLACE_PROTOTYPES)},
    )
    print(f"Run record: {repo_relative(record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
