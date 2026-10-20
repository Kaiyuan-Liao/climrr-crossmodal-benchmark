"""M4-WP4r1: reader 1's claim records on the frozen 20-item sample.

Record-level rules run on the tracked artifacts. The full re-slice against the
LITCORPUS-02 source files runs only where `litcorpus02_root` is configured.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from climrr import litingest
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

LIT = REPO_ROOT / "artifacts" / "literature"
CLAIMS_DIR = LIT / "wp4_claims"
DIMENSIONS = ("concept", "relation_or_direction", "geography", "temporal_frame", "scenario",
              "experimental_condition")
PRIOR = "LIT2-001075"


def _sample() -> dict:
    return json.loads((LIT / "wp4_sample.json").read_text(encoding="utf-8"))


def _records() -> list[dict]:
    return [json.loads((CLAIMS_DIR / f"{s['lit2_id']}.json").read_text(encoding="utf-8"))
            for s in _sample()["selected"]]


def test_one_record_per_sampled_item_and_hashes_carried():
    sample = _sample()
    records = _records()
    assert len(records) == 20
    sample_sha = sha256_file(LIT / "wp4_sample.json")
    for s, r in zip(sample["selected"], records):
        assert r["lit2_id"] == s["lit2_id"] and r["item_id"] == s["item_id"]
        assert r["file_sha256"] == s["sha256"]
        assert r["sample_sha256"] == sample_sha
        assert r["reader"] == "reader_1"


def test_claim_rules():
    for r in _records():
        assert len(r["claims"]) <= 5
        expected = {
            ("in_scope_hazard", True): "claims_extracted",
            ("in_scope_hazard", False): "no_eligible_claim",
            ("off_topic", False): "off_topic",
            ("ambiguous", False): "ambiguous_only",
        }[(r["scope_status"], bool(r["claims"]))]
        assert r["terminal_status"] == expected
        for c in r["claims"]:
            assert c["claim_validation_status"] == "single_reader_provisional"
            assert c["evidence_tier"] == "C"
            assert len(c["claim_text"].split()) <= 40
            assert "role" in c["geography"]
            for d in DIMENSIONS:
                dim = c[d]
                if dim["status"] == "unknown":
                    assert dim["value"] == "unknown" and "support" not in dim
                if dim["status"] == "inferred":
                    assert "support" in dim


def test_prior_exposure_is_recorded_only_on_the_known_item():
    for r in _records():
        if r["lit2_id"] == PRIOR:
            assert r["prior_exposure"] == "LIT-001536 read in M4-WP2; WP2 artifacts not consulted"
        else:
            assert "prior_exposure" not in r


def test_extraction_spec_reads_no_hit_or_wp2_file():
    text = (REPO_ROOT / "scripts" / "wp4_extractions.py").read_text(encoding="utf-8")
    builder = (REPO_ROOT / "scripts" / "build_wp4_claims.py").read_text(encoding="utf-8")
    for src in (text, builder):
        assert "hits.csv" not in src.replace("(`hits.csv`)", "")
        assert "wp2_" not in src and "artifacts/bridges" not in src


def _root() -> Path | None:
    try:
        from climrr.paths import get
        root = Path(get("litcorpus02_root"))
    except Exception:
        return None
    return root if root.is_dir() else None


@pytest.mark.skipif(_root() is None, reason="litcorpus02_root not configured on this machine")
def test_every_span_reslices_from_the_source():
    root = _root()
    n = 0
    for s, r in zip(_sample()["selected"], _records()):
        doc, failure = litingest.read_verified(root / s["rel_path"], s["sha256"])
        assert failure is None
        blocks = [r["scope_evidence"]] + [x["evidence"] for x in r["rejected_or_ambiguous"]]
        for c in r["claims"]:
            blocks.append(c["evidence"])
            blocks += [c[d]["support"] for d in DIMENSIONS if "support" in c[d]]
        blocks += [f["evidence"] for f in r["bibliographic"].values() if isinstance(f, dict) and "evidence" in f]
        for b in blocks:
            litingest.check_span(doc, b)
            n += 1
    assert n == 300
