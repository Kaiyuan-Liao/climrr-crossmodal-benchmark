"""M4-WP2 Phase 3: compare reader 1 and the blind reader on the four candidates, then adjudicate.

Reuses the WP1b machinery unchanged --- `climrr.wp1b.align`,
`mechanical_diff`, `resolve_pair` (rules 2--3, span-limited trimming as
approved by D-019), `adjudicate_scope`, `statistics`, `evidence_tier` --- and
adds only what differs here:

* the inputs and their pins (`wp2_claims/`, reader 1 at `258536a`;
  `wp2_blind/`, the blind reader at `939111e`);
* an adapter for the blind reader's schema, which is not the WP1b blind
  schema: dimensions carry `status` and `support_span`; scope is an object
  `{value, reason, quoted_span}`; rejected passages carry `span`; paths are
  written `$["key"]`. Every path is normalised to the `$.key` form
  `climrr.litingest.child_path` writes.

No paper is re-read for meaning; the corpus is opened only to re-slice spans.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from climrr import wp1b
from climrr.checksums import sha256_file
from climrr.litingest import child_path, read_verified
from climrr.paths import REPO_ROOT

LIT = REPO_ROOT / "artifacts" / "literature"
R1_DIR = LIT / "wp2_claims"
R2_DIR = LIT / "wp2_blind"
R2_SUMMARY = R2_DIR / "wp2_blind_summary.json"
MANIFEST = LIT / "corpus_manifest.json"
CANDIDATES = LIT / "wp2_candidates.json"
COMPARISON_PATH = LIT / "wp2_comparison.json"
ADJ_DIR = LIT / "wp2_claims_adjudicated"
ADJ_SUMMARY_PATH = ADJ_DIR / "adjudication_summary.json"
DOC_PATH = REPO_ROOT / "docs" / "LITERATURE_WP2_ADJUDICATION.md"

READER_1_COMMIT = "258536a"
BLIND_COMMIT = "939111e"

FROZEN_INPUT_SHA256 = {
    "artifacts/literature/wp2_claims/LIT-000166.json": "fc110c8a3be78c2c67ca2e4a5a70087e82fad92471704de9f4b8c1843e81448c",
    "artifacts/literature/wp2_claims/LIT-000519.json": "c37b16ef6c88f7c85f987b3976a39f179c40ccd094981c5824931424011f9a8a",
    "artifacts/literature/wp2_claims/LIT-001501.json": "53d09ef8081ebb92eb1efaec024f49ee25f8290c15f85e19245ce6358c88f218",
    "artifacts/literature/wp2_claims/LIT-001536.json": "4a62e727d2a381b342a6f179dbf4a3887a2cb9e3fbb1a9111a29a8f09c14c9f2",
    "artifacts/literature/wp2_claims/wp2_claims_summary.json": "8a710cb706da10c95d4eb90b8bf29b59efceba8a6f8d21f9aab712fef1636571",
    "artifacts/literature/wp2_blind/14300.json": "33b9bdbd63a6e96706c20f737fbd2090b7eae44c00d07d997fefe4ee202ee8d1",
    "artifacts/literature/wp2_blind/221115000.json": "2cf141a23e8391ec9d7c52170779d5b2577d9c687da663737bc5cf71fe58ea9b",
    "artifacts/literature/wp2_blind/270320300.json": "4307a80ff8ab19f1a2abb03366babf6738870fcdca2639cec234414e9bdea802",
    "artifacts/literature/wp2_blind/272852900.json": "280389a67916530124aee3f9204f81f1fba6474051aaacf3f8cd8894591c0f02",
    "artifacts/literature/wp2_blind/wp2_blind_summary.json": "53f59defd019c8ce23d086874d7424522b2742c62b0c3d2813b1c91005df9873",
    "artifacts/literature/wp2_candidates.json": "e155e70e338ffb67f8c881a8a3fdb794e28c0f048c43afc10b0a723135ec8d9c",
}

_BRACKET = re.compile(r'^\$\[("(?:[^"\\]|\\.)*")\]$')


def norm_path(p: str) -> str:
    """`$["abstract"]` / `$.abstract` / raw key -> the canonical `child_path` form."""
    m = _BRACKET.match(p)
    if m:
        return child_path("$", json.loads(m.group(1)))
    if p.startswith("$."):
        return child_path("$", p[2:])
    if p.startswith("$"):
        return p
    return child_path("$", p)


def verify_inputs() -> dict:
    observed = {}
    for rel, expected in FROZEN_INPUT_SHA256.items():
        got = sha256_file(REPO_ROOT / rel)
        if got != expected:
            raise wp1b.AdjudicationError(f"{rel}: SHA-256 {got} != frozen {expected}")
        observed[rel] = got
    for d in (R1_DIR, R2_DIR):
        extra = {str(p.relative_to(REPO_ROOT)) for p in d.glob("*.json")} - set(FROZEN_INPUT_SHA256)
        if extra:
            raise wp1b.AdjudicationError(f"unpinned file(s) in a frozen reading: {sorted(extra)}")
    return observed


def manifest_entries() -> dict:
    return {e["item_id"]: e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]}


def candidate_ids() -> list[str]:
    return json.loads(CANDIDATES.read_text(encoding="utf-8"))["candidate_ids"]


def load_r1() -> dict:
    return {iid: json.loads((R1_DIR / f"{iid}.json").read_text(encoding="utf-8")) for iid in candidate_ids()}


def load_r2() -> dict:
    """Blind records keyed by LIT id (basename -> id through the frozen manifest)."""
    ents = manifest_entries()
    b2i = {ents[i]["relative_path"]: i for i in candidate_ids()}
    out = {}
    for p in sorted(R2_DIR.glob("*.json")):
        if p.name == R2_SUMMARY.name:
            continue
        out[b2i[p.name]] = json.loads(p.read_text(encoding="utf-8"))
    if set(out) != set(candidate_ids()):
        raise wp1b.AdjudicationError("the blind reading does not cover exactly the four candidates")
    return out


def _span(s: dict) -> dict:
    return {"json_path": norm_path(s["json_path"]), "char_start": s["char_start"], "char_end": s["char_end"],
            "evidence_text": s["evidence_text"]}


def _dim(d: dict, reader: int) -> dict:
    sup = d.get("support") if reader == 1 else d.get("support_span")
    out = {"value": d["value"], "tag": d["status"]}
    if sup:
        out["support"] = _span(sup)
    return out


def claims_of(rec: dict, reader: int) -> list[dict]:
    out = []
    for c in rec["claims"]:
        v = {"claim_id": c["claim_id"], "text": c["claim_text"] if reader == 1 else c["restatement"],
             "claim_type": c["claim_type"], "evidence": _span(c["evidence"])}
        for d in wp1b.DIMENSIONS:
            v[d] = _dim(c[d], reader)
        out.append(v)
    return out


def scope_of(rec: dict, reader: int) -> tuple[str, str]:
    if reader == 1:
        return rec["scope_status"], rec["scope_reason"]
    return rec["scope_status"]["value"], rec["scope_status"]["reason"]


def rejected_of(rec: dict, reader: int) -> list[dict]:
    if reader == 1:
        return [{"id": r["candidate_id"], "span": _span(r["evidence"]), "reason": r["reason"]}
                for r in rec["rejected_or_ambiguous"]]
    return [{"id": f"rejected[{i}]", "span": _span(r["span"]), "reason": r["reason"]}
            for i, r in enumerate(rec["rejected_or_ambiguous"])]


def verify_all_spans(corpus_root: Path, r1: dict, r2: dict) -> dict:
    ents = manifest_entries()
    counts = {"reader_1": 0, "reader_2": 0}
    for iid in candidate_ids():
        e = ents[iid]
        doc, err = read_verified(Path(corpus_root) / e["relative_path"], e["sha256"])
        if err:
            raise wp1b.AdjudicationError(f"{iid}: {err}")
        for label, rec in (("reader_1", r1[iid]), ("reader_2", r2[iid])):
            for where, span in wp1b.iter_spans(rec):
                try:
                    wp1b.check_one_span(doc, {**span, "json_path": norm_path(span["json_path"])})
                except Exception as exc:  # noqa: BLE001 --- any failure is a stop condition
                    raise wp1b.AdjudicationError(f"{label} {iid}{where}: span fails to re-slice: {exc}") from exc
                counts[label] += 1
    return counts
