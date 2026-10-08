"""M5-WP1: deterministic compatibility between WP1 claims and WP3b prototypes.

Authorized by `docs/M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md` (D-017) as
**machinery validation** over single-reader provisional claims. Nothing here
computes similarity, embeds text, or asks a model anything: a dimension is
`compatible` or `incompatible` only when a named rule below says so, and
`not_evaluable` otherwise.

This first part freezes the inputs (Phase A): every claim and prototype the
matrix reads is pinned by a hash of its file and a hash of its record.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT, repo_relative

LIT = REPO_ROOT / "artifacts" / "literature"
CLAIMS_DIR = LIT / "wp1_claims"
SAMPLE_PATH = LIT / "wp1_sample.json"
CORPUS_MANIFEST_PATH = LIT / "corpus_manifest.json"
PROTOTYPES_DIR = REPO_ROOT / "artifacts" / "phenomena" / "prototypes"
PROTOTYPE_IDS = ("P-CELL-1", "P-COUNTY-1", "P-STATE-1")
DATA_MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"
BRIDGES = REPO_ROOT / "artifacts" / "bridges"
INPUTS_PATH = BRIDGES / "m5wp1_inputs.json"

RECORD_HASH_CONVENTION = (
    "SHA-256 of the UTF-8 bytes of json.dumps(record, sort_keys=True, ensure_ascii=False, "
    "separators=(',', ':'))"
)


class FreezeError(Exception):
    """A frozen input no longer matches its pin. A defect to escalate, never to update."""


def record_sha256(record: object) -> str:
    text = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def claim_file(item_id: str) -> Path:
    return CLAIMS_DIR / f"{item_id}.json"


def prototype_file(prototype_id: str) -> Path:
    return PROTOTYPES_DIR / f"{prototype_id}.json"


def build_inputs() -> dict:
    """Describe the current inputs: every claim and prototype, with its pins."""
    sample = _load(SAMPLE_PATH)
    data_manifest = _load(DATA_MANIFEST_PATH)
    csv_sha = next(f["sha256"] for f in data_manifest["files"] if f["filename"] == "FullData.csv")
    corpus = next(c for c in data_manifest["external_corpora"] if c["corpus_id"] == "LITCORPUS-00")
    corpus_sha = sha256_file(CORPUS_MANIFEST_PATH)
    if corpus_sha != corpus["inventory_manifest_sha256"]:
        raise FreezeError("corpus manifest bytes differ from data/manifest.json")

    claims = []
    for item_id in sample["item_ids"]:
        path = claim_file(item_id)
        rec = _load(path)
        if rec["corpus_manifest_sha256"] != corpus_sha:
            raise FreezeError(f"{item_id}: claim record tied to a different corpus manifest")
        for c in rec["claims"]:
            claims.append({
                "claim_id": c["claim_id"],
                "item_id": item_id,
                "claim_type": c["claim_type"],
                "claim_validation_status": c["claim_validation_status"],
                "claim_file": repo_relative(path),
                "claim_file_sha256": sha256_file(path),
                "source_corpus_file_sha256": rec["file_sha256"],
                "claim_record_sha256": record_sha256(c),
            })

    prototypes = []
    for pid in PROTOTYPE_IDS:
        path = prototype_file(pid)
        rec = _load(path)
        if rec["csv_sha256"] != csv_sha:
            raise FreezeError(f"{pid}: built from CSV bytes other than the manifest's")
        prototypes.append({
            "prototype_id": pid,
            "prototype_file": repo_relative(path),
            "prototype_file_sha256": sha256_file(path),
            "prototype_record_sha256": record_sha256(rec),
            "schema_version": rec["schema_version"],
            "validation_only": rec["validation_only"],
            "built_from_commit": rec["built_from_commit"],
        })

    return {
        "package": "M5-WP1",
        "authorized_by": "docs/M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md (D-017)",
        "record_hash_convention": RECORD_HASH_CONVENTION,
        "corpus_manifest_sha256": corpus_sha,
        "wp1_sample_sha256": sha256_file(SAMPLE_PATH),
        "csv_sha256": csv_sha,
        "csv_sha256_source": "data/manifest.json (FullData.csv); the CSV itself is not read by M5-WP1",
        "n_claims": len(claims),
        "n_prototypes": len(prototypes),
        "n_pairs": len(claims) * len(prototypes),
        "claims": claims,
        "prototypes": prototypes,
    }


def verify_inputs(frozen: dict | None = None) -> dict:
    """Fail closed unless every pinned input is byte- and record-identical to the freeze."""
    frozen = frozen if frozen is not None else _load(INPUTS_PATH)
    current = build_inputs()
    if current != frozen:
        diffs = []
        for key in sorted(set(frozen) | set(current)):
            if frozen.get(key) != current.get(key):
                diffs.append(key)
        raise FreezeError(f"M5-WP1 inputs differ from the freeze in: {', '.join(diffs)}")
    return frozen
