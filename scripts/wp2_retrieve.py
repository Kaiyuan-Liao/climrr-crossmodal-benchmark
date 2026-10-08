#!/usr/bin/env python3
"""M4-WP2 retrieval, step 2: scan the corpus with the frozen terms and freeze 12 candidates.

Writes `artifacts/literature/wp2_qualifying_pool.json` (every qualifying id,
with hit counts, so the cap's effect is visible) and
`artifacts/literature/wp2_candidates.json` (the first 12, with every hit's item
id, JSON path, term, term class and code-point span). **Prints ids and counts
only**: no decoded text reaches the terminal or a file except each hit's exact
matched characters. Written once; a later run verifies and fails on any change.

**This retrieves; it does not read.** Semantic inspection of the candidates
waits for M4-WP1b (D-018).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import wp2retrieve  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import get as get_local_path  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    terms = json.loads(wp2retrieve.TERMS_PATH.read_text(encoding="utf-8"))
    if terms != wp2retrieve.build_terms():
        print("FAIL: wp2_terms.json differs from a rebuild of the concept map and prototypes", file=sys.stderr)
        return 1
    root = Path(get_local_path("literature_corpus_root"))
    try:
        pool, cands = wp2retrieve.run(root, terms)
        a_pool = wp2retrieve.write_or_verify(wp2retrieve.POOL_PATH, pool)
        cands["qualifying_pool_sha256"] = sha256_file(wp2retrieve.POOL_PATH)
        a_cand = wp2retrieve.write_or_verify(wp2retrieve.CANDIDATES_PATH, cands)
    except Exception as exc:  # integrity, decode, or freeze failure: fail closed
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"  scanned {pool['n_items_scanned']}; parse failures {pool['n_parse_failures']}; "
          f"with concept hit {pool['n_with_concept_hit']}; with place hit {pool['n_with_place_hit']}")
    print(f"  qualifying before dedupe {pool['n_qualifying_before_dedupe']}; removed as duplicates "
          f"{pool['removed_as_later_duplicates']}; pool {pool['n_qualifying_pool']}; candidates {cands['n_candidates']}")
    for c in cands["candidates"]:
        print(f"  {c['item_id']}  concept={c['concept_hits']:<4} place={c['place_hits']:<4} {c['by_term']}")
    shas = {p.name: sha256_file(p) for p in (wp2retrieve.TERMS_PATH, wp2retrieve.POOL_PATH, wp2retrieve.CANDIDATES_PATH)}
    for k, v in shas.items():
        print(f"  {k} sha256={v}")
    short = cands["n_candidates"] < wp2retrieve.CAP
    record = write_run_record(
        "wp2_retrieve",
        result_summary={"actions": {"pool": a_pool, "candidates": a_cand}, "sha256": shas,
                        "n_items_scanned": pool["n_items_scanned"], "n_parse_failures": pool["n_parse_failures"],
                        "n_qualifying_before_dedupe": pool["n_qualifying_before_dedupe"],
                        "removed_as_later_duplicates": pool["removed_as_later_duplicates"],
                        "n_qualifying_pool": pool["n_qualifying_pool"], "candidate_ids": cands["candidate_ids"],
                        "pool_short_of_cap": short},
        passed=True,
        data_path=wp2retrieve.CORPUS_MANIFEST_PATH,
        output_path=wp2retrieve.CANDIDATES_PATH,
        config_snapshot={"corpus_root": "config/local_paths.yaml:literature_corpus_root",
                         "terms_sha256": shas["wp2_terms.json"], "cap": wp2retrieve.CAP},
    )
    print(f"Run record: {repo_relative(record)}")
    if short:
        print(f"NOTE: the pool holds fewer than {wp2retrieve.CAP} items; terms were not loosened. Report it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
