#!/usr/bin/env python3
"""M4-WP4r1 Phase B: build reader 1's per-item claim records, and check every span.

Reads the frozen sample (`artifacts/literature/wp4_sample.json`), verifies it
against `data/manifest.json` and every sampled file against the sample's
SHA-256 (fail closed, all twenty before any decode), decodes each file, and
turns reader 1's reading in `scripts/wp4_extractions.py` into
`artifacts/literature/wp4_claims/<LIT2 id>.json`, plus a summary.

The build fails if any quoted span is not found in the decoded source, if a
slice with the computed `[start, end)` does not reproduce the text, if a
dimension is `inferred` without a support span or `unknown` with a value, if a
geography has no role, if a claim exceeds 40 words or an item 5 claims, or if a
terminal status contradicts the scope and claim count. Every claim is
`single_reader_provisional`, evidence tier `C`.

`--check` builds and verifies in memory and writes nothing (used while reading;
items not yet in the spec are reported as pending).

This script reads the sample, the data manifest, the twenty sampled files and
the extraction spec. It reads no hit file, no place-hit location, no prototype
and no WP2 artifact.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from climrr import litingest  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import get as get_local_path  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
import wp4_extractions as spec  # noqa: E402
from wp4_verify_sample import manifest_entry  # noqa: E402

LIT = REPO_ROOT / "artifacts" / "literature"
SAMPLE = LIT / "wp4_sample.json"
OUT_DIR = LIT / "wp4_claims"
SUMMARY = LIT / "wp4_claims_summary.json"
ROOT_KEY = "litcorpus02_root"

SCOPES = ("in_scope_hazard", "off_topic", "ambiguous")
TERMINALS = ("claims_extracted", "no_eligible_claim", "off_topic", "ambiguous_only", "parse_failure")
CLAIM_TYPES = ("finding", "projection", "mechanism", "recommendation", "background_citation")
STATUSES = ("explicit", "inferred", "unknown")
DIMENSIONS = ("concept", "relation_or_direction", "geography", "temporal_frame", "scenario",
              "experimental_condition")
CLAIM_VALIDATION_STATUS = "single_reader_provisional"
EVIDENCE_TIER = "C"
READER = "reader_1"
MAX_WORDS = 40
MAX_CLAIMS = 5


class BuildError(RuntimeError):
    pass


def evidence(doc: object, e: dict) -> dict:
    block = litingest.locate(doc, e["json_path"], e["text"], e.get("occurrence", 1))
    litingest.check_span(doc, block)
    if e.get("occurrence", 1) != 1:
        block["occurrence"] = e["occurrence"]
    return block


def dimension(doc: object, d: dict, where: str, geography: bool = False) -> dict:
    status = d["status"]
    if status not in STATUSES:
        raise BuildError(f"{where}: status {status!r}")
    if status == "unknown" and (d["value"] != "unknown" or d["support"] is not None):
        raise BuildError(f"{where}: unknown must have value 'unknown' and no support")
    if status == "inferred" and d["support"] is None:
        raise BuildError(f"{where}: inferred requires a support span")
    out = {"value": d["value"], "status": status}
    if geography:
        if not d.get("role"):
            raise BuildError(f"{where}: geography requires a role")
        if status == "unknown" and d["role"] != "unknown":
            raise BuildError(f"{where}: unknown geography must have role 'unknown'")
        out["role"] = d["role"]
    if d["support"] is not None:
        out["support"] = evidence(doc, d["support"])
    return out


def bibliographic(doc: dict, b: dict) -> dict:
    out = {}
    for field in ("title", "authors", "year", "venue"):
        src = b.get(field)
        if src is None:
            out[field] = {"value": "unknown", "status": "unknown"}
        elif isinstance(src, str):
            if not src.startswith("$.") or src[2:] not in doc:
                raise BuildError(f"bibliographic {field}: {src} not present")
            out[field] = {"value": doc[src[2:]], "status": "as_stored", "json_path": src}
        else:
            path, text = src
            block = evidence(doc, {"json_path": path, "text": text})
            out[field] = {"value": text, "status": "recovered_from_other_field", "evidence": block}
    if b.get("note"):
        out["note"] = b["note"]
    return out


def build_item(item: dict, doc: object, s: dict, sample_sha: str) -> dict:
    lid = item["lit2_id"]
    record = {
        "lit2_id": lid,
        "item_id": item["item_id"],
        "arm": item["arm"],
        "rank": item["rank"],
        "rel_path": item["rel_path"],
        "file_sha256": item["sha256"],
        "sample_sha256": sample_sha,
        "corpus_id": "LITCORPUS-02-conceptfirst-705k-v1",
        "reader": READER,
        "offset_convention": litingest.OFFSET_CONVENTION,
        "extraction": {"method": spec.EXTRACTION_METHOD, "date": spec.EXTRACTION_DATE, "read_completely": True},
    }
    if lid in spec.PRIOR_EXPOSURE:
        record["prior_exposure"] = spec.PRIOR_EXPOSURE[lid]
    if doc is None or not isinstance(doc, dict):
        record.update(parse_status="parse_failure", terminal_status="parse_failure", claims=[],
                      rejected_or_ambiguous=[])
        return record
    if s["scope_status"] not in SCOPES or s["terminal_status"] not in TERMINALS:
        raise BuildError(f"{lid}: scope or terminal status out of vocabulary")
    if len(s["claims"]) > MAX_CLAIMS:
        raise BuildError(f"{lid}: more than {MAX_CLAIMS} claims")

    claims = []
    for n, c in enumerate(s["claims"], start=1):
        where = f"{lid}-C{n}"
        if c["claim_type"] not in CLAIM_TYPES:
            raise BuildError(f"{where}: claim_type {c['claim_type']!r}")
        if len(c["claim_text"].split()) > MAX_WORDS:
            raise BuildError(f"{where}: claim_text over {MAX_WORDS} words")
        claim = {"claim_id": where, "claim_text": c["claim_text"], "claim_type": c["claim_type"]}
        for dim in DIMENSIONS:
            claim[dim] = dimension(doc, c[dim], f"{where}.{dim}", geography=(dim == "geography"))
        claim["evidence"] = evidence(doc, c["evidence"])
        claim["claim_validation_status"] = CLAIM_VALIDATION_STATUS
        claim["evidence_tier"] = EVIDENCE_TIER
        claim["notes"] = c.get("notes")
        claims.append(claim)

    expected = {
        ("in_scope_hazard", True): "claims_extracted",
        ("in_scope_hazard", False): "no_eligible_claim",
        ("off_topic", False): "off_topic",
        ("ambiguous", False): "ambiguous_only",
    }.get((s["scope_status"], bool(claims)))
    if expected != s["terminal_status"]:
        raise BuildError(f"{lid}: terminal {s['terminal_status']!r} contradicts scope/claims (expected {expected!r})")

    rejected = [
        {"candidate_id": f"{lid}-R{n}", "evidence": evidence(doc, r["evidence"]), "reason": r["reason"]}
        for n, r in enumerate(s["rejected_or_ambiguous"], start=1)
    ]
    record.update(
        parse_status="parsed",
        observed_keys=list(doc),
        bibliographic=bibliographic(doc, s["bibliographic"]),
        scope_status=s["scope_status"],
        scope_reason=s["scope_reason"],
        scope_evidence=evidence(doc, s["scope_evidence"]),
        claims=claims,
        rejected_or_ambiguous=rejected,
        terminal_status=s["terminal_status"],
        notes=s.get("notes"),
    )
    return record


def verify_record(record: dict, doc: object) -> int:
    """Re-check every span in a finished record against the source. Returns span count."""
    if record["parse_status"] != "parsed":
        return 0
    blocks = [record["scope_evidence"]]
    for c in record["claims"]:
        blocks.append(c["evidence"])
        blocks += [c[d]["support"] for d in DIMENSIONS if "support" in c[d]]
    blocks += [r["evidence"] for r in record["rejected_or_ambiguous"]]
    blocks += [f["evidence"] for f in record["bibliographic"].values() if isinstance(f, dict) and "evidence" in f]
    for b in blocks:
        litingest.check_span(doc, b)
    return len(blocks)


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    sample_sha = sha256_file(SAMPLE)
    if sample_sha != manifest_entry()["wp4_sample_sha256"]:
        print("FAIL: wp4_sample.json does not match data/manifest.json", file=sys.stderr)
        return 1
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    selected = sample["selected"]
    ids = [s["lit2_id"] for s in selected]
    if set(spec.ITEMS) - set(ids):
        print(f"FAIL: spec items outside the sample: {sorted(set(spec.ITEMS) - set(ids))}", file=sys.stderr)
        return 1
    pending = [i for i in ids if i not in spec.ITEMS]
    if pending and not check_only:
        print(f"FAIL: the extraction spec does not cover the sample; pending {pending}", file=sys.stderr)
        return 1
    root = Path(get_local_path(ROOT_KEY))

    try:
        # All twenty hashes first; nothing is decoded until every one matches.
        for item in selected:
            observed = sha256_file(root / item["rel_path"])
            if observed != item["sha256"]:
                raise litingest.IntegrityError(f"{item['lit2_id']}: SHA-256 {observed} != sample {item['sha256']}")
        rows, records, n_spans = [], {}, 0
        for item in selected:
            if item["lit2_id"] in pending:
                continue
            doc, failure = litingest.read_verified(root / item["rel_path"], item["sha256"])
            record = build_item(item, doc, spec.ITEMS[item["lit2_id"]], sample_sha)
            if failure:
                record["parse_failure"] = failure
            n_spans += verify_record(record, doc)
            records[item["lit2_id"]] = record
            claims = record.get("claims", [])
            rows.append({
                "lit2_id": item["lit2_id"],
                "item_id": item["item_id"],
                "arm": item["arm"],
                "scope_status": record.get("scope_status"),
                "terminal_status": record["terminal_status"],
                "n_claims": len(claims),
                "n_claims_with_inferred_dimension": sum(
                    any(c[d]["status"] == "inferred" for d in DIMENSIONS) for c in claims
                ),
                "n_rejected_or_ambiguous": len(record.get("rejected_or_ambiguous", [])),
            })
    except (BuildError, litingest.IntegrityError, KeyError, IndexError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    for r in rows:
        print(f"  {r['lit2_id']}  {r['arm']:<16} {r['scope_status']:<16} {r['terminal_status']:<17} "
              f"claims={r['n_claims']} inferred={r['n_claims_with_inferred_dimension']} rejected={r['n_rejected_or_ambiguous']}")
    print(f"  span integrity: {n_spans} spans checked, all passed")
    if check_only:
        print(f"  --check: nothing written; pending {len(pending)}: {pending}")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for lid, record in records.items():
        (OUT_DIR / f"{lid}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    totals = {
        "items": len(rows),
        "claims": sum(r["n_claims"] for r in rows),
        "items_with_claims": sum(r["n_claims"] > 0 for r in rows),
        "claims_with_any_inferred_dimension": sum(r["n_claims_with_inferred_dimension"] for r in rows),
        "rejected_or_ambiguous": sum(r["n_rejected_or_ambiguous"] for r in rows),
        "by_terminal_status": {t: sum(r["terminal_status"] == t for r in rows) for t in TERMINALS},
        "by_scope_status": {s: sum(r["scope_status"] == s for r in rows) for s in SCOPES},
        "by_claim_validation_status": {CLAIM_VALIDATION_STATUS: sum(r["n_claims"] for r in rows)},
        "by_evidence_tier": {EVIDENCE_TIER: sum(r["n_claims"] for r in rows)},
    }
    summary = {
        "artifact": "M4-WP4 reader-1 claim extraction summary",
        "reader": READER,
        "sample_sha256": sample_sha,
        "corpus_id": "LITCORPUS-02-conceptfirst-705k-v1",
        "extraction_method": spec.EXTRACTION_METHOD,
        "extraction_date": spec.EXTRACTION_DATE,
        "representativeness": ("deterministic rank sample of lexical place candidates from LITCORPUS-02; "
                               "not representative of the corpus or the literature"),
        "prior_exposure": spec.PRIOR_EXPOSURE,
        "span_integrity_check": {"spans_checked": n_spans, "result": "passed"},
        "totals": totals,
        "items": rows,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  totals: {totals}")
    record = write_run_record(
        "build_wp4_claims",
        result_summary={"sample_sha256": sample_sha, **totals, "spans_checked": n_spans},
        passed=True,
        data_path=SAMPLE,
        data_sha256=sample_sha,
        output_path=SUMMARY,
        config_snapshot={"corpus_root": f"config/local_paths.yaml:{ROOT_KEY}",
                         "spec": "scripts/wp4_extractions.py",
                         "spec_sha256": sha256_file(REPO_ROOT / "scripts" / "wp4_extractions.py")},
    )
    print(f"Run record: {repo_relative(record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
