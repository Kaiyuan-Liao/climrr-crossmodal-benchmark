#!/usr/bin/env python3
"""M4-WP1 Phase C: build the per-item claim records, and check every span.

Reads the frozen sample (`artifacts/literature/wp1_sample.json`), verifies each
sampled file's SHA-256 against the frozen corpus manifest (fail closed), decodes
it, and turns the EXECUTOR's reading in `scripts/wp1_extractions.py` into
`artifacts/literature/wp1_claims/<item_id>.json`, plus a summary.

**The build fails** if any quoted span is not found in the decoded source, if a
slice of the source with the computed `[start, end)` span does not reproduce
the evidence text exactly, if an evidence hash does not match, if a dimension
is `inferred` without a support span or `unknown` with a value, if a claim text
exceeds 40 words, or if a terminal status contradicts the scope and the claim
count. Offsets are zero-based, half-open Unicode code-point offsets into the
JSON string value after decoding and before any normalization (D-016).

This script reads the sample, the corpus manifest, the ten sampled files and
the extraction spec. It reads no prototype, no pilot-family document and no
collection query.
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
import wp1_extractions as spec  # noqa: E402

LIT = REPO_ROOT / "artifacts" / "literature"
SAMPLE = LIT / "wp1_sample.json"
MANIFEST = LIT / "corpus_manifest.json"
SCHEMA = LIT / "wp1_schema_observed.json"
OUT_DIR = LIT / "wp1_claims"
SUMMARY = LIT / "wp1_claims_summary.json"

SCOPES = ("in_scope_hazard", "off_topic", "ambiguous")
TERMINALS = ("claims_extracted", "no_eligible_claim", "off_topic", "parse_failure", "ambiguous_only")
CLAIM_TYPES = ("finding", "projection", "mechanism", "recommendation", "background_citation")
STATUSES = ("explicit", "inferred", "unknown")
DIMENSIONS = ("concept", "relation_or_direction", "geography", "temporal_frame", "scenario")
MAX_WORDS = 40


class BuildError(RuntimeError):
    pass


def evidence(doc: object, e: dict) -> dict:
    block = litingest.locate(doc, e["json_path"], e["text"], e.get("occurrence", 1))
    litingest.check_span(doc, block)
    if e.get("occurrence", 1) != 1:
        block["occurrence"] = e["occurrence"]
    return block


def dimension(doc: object, d: dict, where: str) -> dict:
    status = d["status"]
    if status not in STATUSES:
        raise BuildError(f"{where}: status {status!r}")
    if status == "unknown" and (d["value"] != "unknown" or d["support"] is not None):
        raise BuildError(f"{where}: unknown must have value 'unknown' and no support")
    if status == "inferred" and d["support"] is None:
        raise BuildError(f"{where}: inferred requires a support span")
    out = {"value": d["value"], "status": status}
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


def build_item(item: dict, doc: object, s: dict, manifest_sha: str, sample_sha: str) -> dict:
    iid = item["item_id"]
    record = {
        "item_id": iid,
        "file_sha256": item["sha256"],
        "corpus_manifest_sha256": manifest_sha,
        "sample_sha256": sample_sha,
        "offset_convention": litingest.OFFSET_CONVENTION,
        "extraction": {"method": spec.EXTRACTION_METHOD, "date": spec.EXTRACTION_DATE, "read_completely": True},
    }
    if doc is None or not isinstance(doc, dict):
        record.update(parse_status="parse_failure", terminal_status="parse_failure", claims=[])
        return record
    if s["scope_status"] not in SCOPES or s["terminal_status"] not in TERMINALS:
        raise BuildError(f"{iid}: scope or terminal status out of vocabulary")

    claims = []
    for n, c in enumerate(s["claims"], start=1):
        where = f"{iid}-C{n}"
        if c["claim_type"] not in CLAIM_TYPES:
            raise BuildError(f"{where}: claim_type {c['claim_type']!r}")
        if len(c["claim_text"].split()) > MAX_WORDS:
            raise BuildError(f"{where}: claim_text over {MAX_WORDS} words")
        claim = {"claim_id": where, "claim_text": c["claim_text"], "claim_type": c["claim_type"]}
        for dim in DIMENSIONS:
            claim[dim] = dimension(doc, c[dim], f"{where}.{dim}")
        claim["evidence"] = evidence(doc, c["evidence"])
        claim["notes"] = c.get("notes")
        claims.append(claim)

    expected = {
        ("in_scope_hazard", True): "claims_extracted",
        ("in_scope_hazard", False): "no_eligible_claim",
        ("off_topic", False): "off_topic",
        ("ambiguous", False): "ambiguous_only",
    }.get((s["scope_status"], bool(claims)))
    if expected != s["terminal_status"]:
        raise BuildError(f"{iid}: terminal {s['terminal_status']!r} contradicts scope/claims (expected {expected!r})")

    rejected = [
        {"candidate_id": f"{iid}-R{n}", "evidence": evidence(doc, r["evidence"]), "reason": r["reason"]}
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
    blocks = []
    if record["parse_status"] != "parsed":
        return 0
    blocks.append(record["scope_evidence"])
    for c in record["claims"]:
        blocks.append(c["evidence"])
        blocks += [c[d]["support"] for d in DIMENSIONS if "support" in c[d]]
    blocks += [r["evidence"] for r in record["rejected_or_ambiguous"]]
    blocks += [f["evidence"] for f in record["bibliographic"].values() if isinstance(f, dict) and "evidence" in f]
    for b in blocks:
        litingest.check_span(doc, b)
    return len(blocks)


def main() -> int:
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    sample_sha = sha256_file(SAMPLE)
    manifest_sha = sha256_file(MANIFEST)
    if manifest_sha != sample["corpus_manifest_sha256"]:
        print("FAIL: corpus manifest changed since the sample was frozen", file=sys.stderr)
        return 1
    if set(spec.ITEMS) != set(sample["item_ids"]):
        print("FAIL: the extraction spec does not cover exactly the frozen sample", file=sys.stderr)
        return 1
    root = Path(get_local_path("literature_corpus_root"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows, n_spans = [], 0
    try:
        for item in sample["items"]:
            doc, failure = litingest.read_verified(root / item["relative_path"], item["sha256"])
            record = build_item(item, doc, spec.ITEMS[item["item_id"]], manifest_sha, sample_sha)
            if failure:
                record["parse_failure"] = failure
            n_spans += verify_record(record, doc)
            (OUT_DIR / f"{item['item_id']}.json").write_text(
                json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            claims = record.get("claims", [])
            rows.append({
                "item_id": item["item_id"],
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

    summary = {
        "artifact": "M4-WP1 claim extraction summary",
        "sample_sha256": sample_sha,
        "corpus_manifest_sha256": manifest_sha,
        "schema_observed_sha256": sha256_file(SCHEMA),
        "extraction_method": spec.EXTRACTION_METHOD,
        "extraction_date": spec.EXTRACTION_DATE,
        "representativeness": sample["representativeness"],
        "span_integrity_check": {"spans_checked": n_spans, "result": "passed"},
        "totals": {
            "items": len(rows),
            "claims": sum(r["n_claims"] for r in rows),
            "claims_with_any_inferred_dimension": sum(r["n_claims_with_inferred_dimension"] for r in rows),
            "rejected_or_ambiguous": sum(r["n_rejected_or_ambiguous"] for r in rows),
            "by_terminal_status": {t: sum(r["terminal_status"] == t for r in rows) for t in TERMINALS},
            "by_scope_status": {s: sum(r["scope_status"] == s for r in rows) for s in SCOPES},
        },
        "items": rows,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for r in rows:
        print(f"  {r['item_id']}  {r['scope_status']:<16} {r['terminal_status']:<17} claims={r['n_claims']} inferred={r['n_claims_with_inferred_dimension']}")
    print(f"  totals: {summary['totals']}")
    print(f"  span integrity: {n_spans} spans checked, all passed")
    record = write_run_record(
        "build_wp1_claims",
        result_summary={"sample_sha256": sample_sha, **summary["totals"], "spans_checked": n_spans},
        passed=True,
        data_path=SAMPLE,
        data_sha256=sample_sha,
        output_path=SUMMARY,
        config_snapshot={"corpus_root": "config/local_paths.yaml:literature_corpus_root",
                         "spec": "scripts/wp1_extractions.py",
                         "spec_sha256": sha256_file(REPO_ROOT / "scripts" / "wp1_extractions.py")},
    )
    print(f"Run record: {repo_relative(record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
