#!/usr/bin/env python3
"""M4-WP0 Phase C: the literature collection query, parsed deterministically.

Reads `data/metadata/literature_query.txt` --- **after** verifying its SHA-256
against `data/manifest.json` --- and writes
`artifacts/literature/query_parsed.json`: the Boolean structure, the hazard
groups in source order with positional ids only, the context terms, per term
its exact text, quoting, character offsets into the source file and normalized
form, the round-trip check, and the three absence rules with their results.

The artifact is derived and pinned to the source query's SHA-256. It contains
no timestamp, so re-running on the same bytes reproduces it byte for byte.

Everything here is about **the query**. It says how the candidate corpus was
collected; it says nothing about what any paper contains.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litquery  # noqa: E402
from climrr.manifest import verify_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

QUERY_PATH = REPO_ROOT / "data" / "metadata" / "literature_query.txt"
OUT_PATH = REPO_ROOT / "artifacts" / "literature" / "query_parsed.json"

SCOPE_NOTE = (
    "The Boolean query explains how the candidate corpus was collected. It does "
    "not establish what any paper contains or which prototype a paper supports."
)


def build(query_path: Path, verified: dict) -> dict:
    source = query_path.read_bytes().decode("utf-8")
    structure = litquery.extract_structure(source)
    checks = litquery.absence_checks(structure)
    n_terms = len(litquery.all_terms(structure))
    return {
        "artifact": "parsed literature collection query",
        "kind": "derived artifact --- regenerate with scripts/parse_literature_query.py; never edit",
        "parser_version": litquery.PARSER_VERSION,
        "source_path": repo_relative(query_path),
        "source_sha256": verified["sha256"],
        "source_bytes": verified["bytes"],
        "source_encoding": "utf-8",
        "offsets": "0-based character offsets into the decoded source; [start, end) half-open",
        "normalization": (
            "curly quotes to straight, lower case, runs of whitespace to one space, "
            "trimmed; hyphens kept; nothing else changed"
        ),
        "group_ids": (
            "positional only, HG-01.. in source order. No group is named: a name "
            "would be a reading of its terms"
        ),
        "scope_note": SCOPE_NOTE,
        "round_trip": {
            "rule": (
                "render(parse(source)) equals the source after removing whitespace "
                "outside quoted phrases (whitespace inside a phrase must match exactly)"
            ),
            "passed": litquery.round_trips(source),
        },
        "counts": {
            "n_hazard_groups": len(structure["hazard_groups"]),
            "n_hazard_terms": sum(g["n_terms"] for g in structure["hazard_groups"]),
            "n_context_terms": len(structure["context_terms"]),
            "n_terms": n_terms,
            "n_quoted": sum(t["quoted"] for t in litquery.all_terms(structure)),
            "n_bare": sum(not t["quoted"] for t in litquery.all_terms(structure)),
        },
        **structure,
        "absence_checks": checks,
        "absence_checks_scope": (
            "Each rule is checked against the query's terms and nothing else. "
            "'No place name' is verified only against the lists in the rules."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", type=Path, default=QUERY_PATH)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args()

    verified = verify_file(args.query)
    try:
        parsed = build(args.query, verified)
    except (litquery.QueryParseError, litquery.QueryShapeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    counts = parsed["counts"]
    passed = parsed["round_trip"]["passed"]
    print(f"  query           : {repo_relative(args.query)} sha256 {verified['sha256']}")
    print(f"  structure       : {parsed['boolean_structure']}")
    print(f"  terms           : {counts['n_terms']} ({counts['n_quoted']} quoted, {counts['n_bare']} bare)")
    print(f"  round trip      : {'ok' if passed else 'FAILED'}")
    for check in parsed["absence_checks"]:
        print(f"  {check['rule_id']:<22}: {check['result']} ({check['n_hits']} hit(s) in {check['n_terms_checked']} terms)")
    print(f"  wrote           : {repo_relative(args.out)}")

    record_path = write_run_record(
        "parse_literature_query",
        result_summary={
            "parser_version": litquery.PARSER_VERSION,
            "boolean_structure": parsed["boolean_structure"],
            **counts,
            "round_trip_passed": passed,
            "absence_checks": {c["rule_id"]: c["result"] for c in parsed["absence_checks"]},
        },
        passed=passed,
        data_path=args.query,
        data_sha256=verified["sha256"],
        output_path=args.out,
        config_snapshot={"query_path": repo_relative(args.query), "out_path": repo_relative(args.out)},
    )
    print(f"Run record: {repo_relative(record_path)}")
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
