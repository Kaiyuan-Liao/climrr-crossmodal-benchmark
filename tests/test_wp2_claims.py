"""M4-WP2 Phase 1: reader 1's records for the four frozen candidates, and the hit classification."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

from climrr import litingest
from climrr.paths import REPO_ROOT

LIT = REPO_ROOT / "artifacts" / "literature"
CLAIMS_DIR = LIT / "wp2_claims"
DIMS = ("concept", "relation_or_direction", "geography", "temporal_frame", "scenario", "experimental_condition")


def _records() -> dict:
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(CLAIMS_DIR.glob("LIT-*.json"))}


def _hits() -> dict:
    return json.loads((LIT / "wp2_hit_classification.json").read_text(encoding="utf-8"))


def test_exactly_the_four_frozen_candidates_are_read():
    cand = json.loads((LIT / "wp2_candidates.json").read_text(encoding="utf-8"))
    assert list(_records()) == cand["candidate_ids"] == ["LIT-000166", "LIT-000519", "LIT-001501", "LIT-001536"]


def test_every_claim_is_single_reader_tier_c_with_a_full_rubric():
    for r in _records().values():
        assert r["representativeness"] == "relevance-guided candidate sample, not representative"
        assert 0 <= len(r["claims"]) <= 5
        for c in r["claims"]:
            assert c["claim_validation_status"] == "single_reader_provisional"
            assert c["evidence_tier"] == "C"
            for d in DIMS:
                assert c[d]["status"] in ("explicit", "inferred", "unknown")
                if c[d]["status"] == "inferred":
                    assert "support" in c[d]
                if c[d]["status"] == "unknown":
                    assert c[d]["value"] == "unknown"
            assert len(c["claim_text"].split()) <= 40


def test_no_claim_names_a_scenario_or_a_prototype_relation():
    banned = re.compile(r"support(s|ing)? the prototype|P-CELL|P-COUNTY|P-STATE|compatib", re.IGNORECASE)
    for r in _records().values():
        assert not banned.search(json.dumps(r, ensure_ascii=False))
        assert all(c["scenario"]["value"] == "unknown" for c in r["claims"])


@pytest.mark.skipif(not (REPO_ROOT / "config" / "local_paths.yaml").is_file(),
                    reason="external corpus not configured on this host")
def test_every_span_and_every_hit_re_slices_from_the_verified_source():
    from climrr.paths import load_local_paths

    root = load_local_paths().get("literature_corpus_root")
    if not root or str(root).startswith("<") or not Path(root).is_dir():
        pytest.skip("literature_corpus_root not available on this host")
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import build_wp1_claims as bw
    entries = {e["item_id"]: e for e in json.loads((LIT / "corpus_manifest.json").read_text(encoding="utf-8"))["entries"]}
    hits = {i["item_id"]: i for i in _hits()["items"]}
    n = 0
    for iid, r in _records().items():
        doc, err = litingest.read_verified(Path(root) / entries[iid]["relative_path"], entries[iid]["sha256"])
        assert err is None
        n += bw.verify_record(r, doc)
        for h in hits[iid]["hits"]:
            assert litingest.resolve(doc, h["json_path"])[h["char_start"]:h["char_end"]] == h["matched_text"]
    assert n == 63


def test_every_frozen_hit_is_classified_exactly_once():
    cand = json.loads((LIT / "wp2_candidates.json").read_text(encoding="utf-8"))
    frozen = {(c["item_id"], h["json_path"], h["char_start"]) for c in cand["candidates"] for h in c["hits"]}
    classified = [(i["item_id"], h["json_path"], h["char_start"]) for i in _hits()["items"] for h in i["hits"]]
    assert len(classified) == len(set(classified)) == len(frozen) == 61
    assert set(classified) == frozen
    for i in _hits()["items"]:
        for h in i["hits"]:
            assert h["classification"] in ("substantive", "incidental") and h["reason"]


def test_hit_totals_and_the_different_referent_cases():
    h = _hits()
    assert h["totals"]["substantive"] == 26 and h["totals"]["incidental"] == 35
    by = {i["item_id"]: i for i in h["items"]}
    fwi_1501 = [x for x in by["LIT-001501"]["hits"] if x["term"] == "FWI"]
    assert len(fwi_1501) == 11 and all(not x["referent_matches_term"] and x["classification"] == "incidental" for x in fwi_1501)
    stephens = [x for x in by["LIT-000166"]["hits"] if x["term"] == "Stephens"]
    assert len(stephens) == 1 and stephens[0]["classification"] == "incidental"


def test_promoted_evidence_overlap_is_computed_from_spans():
    recs = _records()
    for i in _hits()["items"]:
        for h in i["hits"]:
            expect = [c["claim_id"] for c in recs[i["item_id"]]["claims"]
                      if c["evidence"]["json_path"] == h["json_path"]
                      and c["evidence"]["char_start"] <= h["char_start"] and h["char_end"] <= c["evidence"]["char_end"]]
            assert h["in_promoted_claim_evidence"] == expect


def test_no_fractional_water_index_reaches_a_concept_field():
    """In LIT-001501 'FWI' is a soil-moisture index; revised C-2 would match the letters, so none is promoted."""
    for c in _records()["LIT-001501"]["claims"]:
        assert "FWI" not in c["concept"]["value"] and "fractional water" not in c["concept"]["value"].lower()
