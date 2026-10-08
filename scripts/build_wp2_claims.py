#!/usr/bin/env python3
"""M4-WP2 Phase 1: build reader 1's claim records for the four frozen candidates.

Reuses `build_wp1_claims.build_item` and `verify_record` unchanged --- the same
rubric checks, the same exact-search span location and re-slicing, the same
terminal-status rule --- with `scripts/wp2_extractions.py` as the spec. The four
item ids must equal `candidate_ids` in the frozen `wp2_candidates.json` (only
that key is read); each file is verified against the frozen corpus manifest
before decoding (fail closed).

Adds to every claim `evidence_tier: "C"` (single reader, D-019) and writes
`artifacts/literature/wp2_claims/<item_id>.json` plus a summary. Written once;
a later run verifies byte equality and fails on any change.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_wp1_claims as bw  # noqa: E402
import wp2_extractions as spec  # noqa: E402
from climrr import litingest  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import get as get_local_path  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

LIT = REPO_ROOT / "artifacts" / "literature"
CANDIDATES = LIT / "wp2_candidates.json"
MANIFEST = LIT / "corpus_manifest.json"
OUT_DIR = LIT / "wp2_claims"
SUMMARY = OUT_DIR / "wp2_claims_summary.json"
REPRESENTATIVENESS = "relevance-guided candidate sample, not representative"


def write_or_verify(path: Path, obj: dict) -> str:
    text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise bw.BuildError(f"{repo_relative(path)} differs from a rebuild; reader-1 records are frozen")
        return "verified"
    path.write_text(text, encoding="utf-8")
    return "written"


def main() -> int:
    candidate_ids = json.loads(CANDIDATES.read_text(encoding="utf-8"))["candidate_ids"]
    if list(spec.ITEM_IDS) != list(candidate_ids) or set(spec.ITEMS) != set(candidate_ids):
        print("FAIL: the reading does not cover exactly the frozen candidates", file=sys.stderr)
        return 1
    cand_sha = sha256_file(CANDIDATES)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_sha = sha256_file(MANIFEST)
    entries = {e["item_id"]: e for e in manifest["entries"]}
    root = Path(get_local_path("literature_corpus_root"))
    bw.spec = spec  # the WP1 builder reads EXTRACTION_METHOD / EXTRACTION_DATE from `spec`
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows, n_spans, actions = [], 0, {}
    try:
        for iid in candidate_ids:
            item = entries[iid]
            doc, failure = litingest.read_verified(root / item["relative_path"], item["sha256"])
            record = bw.build_item(item, doc, spec.ITEMS[iid], manifest_sha, cand_sha)
            if failure:
                record["parse_failure"] = failure
            record["candidates_sha256"] = record.pop("sample_sha256")
            record["representativeness"] = REPRESENTATIVENESS
            record["reader"] = "reader 1 (the EXECUTOR, prototype-exposed)"
            for c in record.get("claims", []):
                c["evidence_tier"] = "C"
            n_spans += bw.verify_record(record, doc)
            actions[iid] = write_or_verify(OUT_DIR / f"{iid}.json", record)
            claims = record.get("claims", [])
            rows.append({"item_id": iid, "scope_status": record.get("scope_status"),
                         "terminal_status": record["terminal_status"], "n_claims": len(claims),
                         "n_claims_with_inferred_dimension": sum(any(c[d]["status"] == "inferred" for d in bw.DIMENSIONS) for c in claims),
                         "n_rejected_or_ambiguous": len(record.get("rejected_or_ambiguous", []))})
    except (bw.BuildError, litingest.IntegrityError, KeyError, IndexError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    summary = {
        "artifact": "M4-WP2 Phase 1 claim extraction summary (reader 1)",
        "candidates_sha256": cand_sha,
        "corpus_manifest_sha256": manifest_sha,
        "extraction_method": spec.EXTRACTION_METHOD,
        "extraction_date": spec.EXTRACTION_DATE,
        "representativeness": REPRESENTATIVENESS,
        "span_integrity_check": {"spans_checked": n_spans, "result": "passed"},
        "claim_validation_status": "single_reader_provisional (all)",
        "evidence_tier": "C (all)",
        "totals": {"items": len(rows), "claims": sum(r["n_claims"] for r in rows),
                   "rejected_or_ambiguous": sum(r["n_rejected_or_ambiguous"] for r in rows)},
        "items": rows,
    }
    actions["summary"] = write_or_verify(SUMMARY, summary)
    for r in rows:
        print(f"  {r['item_id']}  {r['scope_status']:<16} {r['terminal_status']:<17} claims={r['n_claims']} inferred={r['n_claims_with_inferred_dimension']}")
    print(f"  span integrity: {n_spans} spans checked, all passed; {actions}")
    rec = write_run_record(
        "build_wp2_claims",
        result_summary={"actions": actions, **summary["totals"], "spans_checked": n_spans},
        passed=True, data_path=CANDIDATES, output_path=SUMMARY,
        config_snapshot={"corpus_root": "config/local_paths.yaml:literature_corpus_root",
                         "spec": "scripts/wp2_extractions.py",
                         "spec_sha256": sha256_file(REPO_ROOT / "scripts" / "wp2_extractions.py")},
    )
    print(f"Run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
