"""M4-WP4r3 Phase A: frozen inputs, the role rule, and the adjudicated set.

Checks the tracked artifacts against the frozen readings; the span re-slice
against the LITCORPUS-02 sources runs only where `litcorpus02_root` is
configured. Nothing here asserts how many claims a rule ought to produce
beyond what the committed comparison records.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from climrr import wp1b, wp4adj
from climrr.litingest import evidence_sha256
from climrr.paths import REPO_ROOT
from climrr.wp4_judgements import PAIR_JUDGEMENTS, ROLE_CLASS_OF_R1


def _committed_sha256(rel: str, commit: str) -> str:
    blob = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=REPO_ROOT, capture_output=True, check=True).stdout
    return hashlib.sha256(blob).hexdigest()


def test_frozen_inputs_match_their_pins():
    assert wp4adj.verify_inputs() == wp4adj.FROZEN_INPUT_SHA256


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required")
def test_pins_equal_the_committed_readings():
    for rel, sha in wp4adj.FROZEN_INPUT_SHA256.items():
        commit = wp4adj.BLIND_COMMIT if "/wp4_blind/" in rel else wp4adj.READER_1_COMMIT
        assert _committed_sha256(rel, commit) == sha, rel


def test_blind_records_map_onto_the_twenty_ids():
    r2 = wp4adj.load_r2()
    assert sorted(r2) == wp4adj.lit2_ids() and len(r2) == 20


def test_every_recorded_role_has_a_class():
    for rec in wp4adj.load_r1().values():
        for c in rec["claims"]:
            assert c["geography"]["role"] in ROLE_CLASS_OF_R1
    for rec in wp4adj.load_r2().values():
        for c in wp4adj.claims_of(rec, 2):
            assert c["geography_role"]["class"] in wp4adj.ROLE_CLASSES
    with pytest.raises(wp1b.AdjudicationError):
        wp4adj.role_class("a role nobody recorded")


def _r(cls: str) -> dict:
    return {"value": cls, "class": cls}


@pytest.mark.parametrize("a,b,adopted,agree", [
    ("study_area", "study_area", "study_area", True),
    ("study_area", "contextual", "contextual", False),
    ("cited_study_area", "study_area", "cited_study_area", False),
    ("data_source", "study_area", "data_source", False),
    ("study_area", "unknown", "unknown", False),
    ("citation_or_person", "study_area", "citation_or_person", False),
])
def test_role_rule_takes_the_more_conservative_class(a, b, adopted, agree):
    res = wp4adj.resolve_role(_r(a), _r(b), {"value": "X", "tag": "explicit"})
    assert res["adopted"]["class"] == adopted and res["agree"] is agree


def test_role_is_unknown_when_geography_is_adopted_unknown():
    res = wp4adj.resolve_role(_r("study_area"), _r("study_area"), {"value": "unknown", "tag": "unknown"})
    assert res["adopted"]["class"] == "unknown"


def _comparison() -> dict:
    return json.loads(wp4adj.COMPARISON_PATH.read_text(encoding="utf-8"))


def test_alignment_reproduces_and_every_judgement_is_used():
    r1, r2 = wp4adj.load_r1(), wp4adj.load_r2()
    n = {"aligned_pairs": 0, "reader_1_only": 0, "reader_2_only": 0}
    seen = set()
    for iid in wp4adj.lit2_ids():
        pairs, o1, o2 = wp1b.align(wp4adj.claims_of(r1[iid], 1), wp4adj.claims_of(r2[iid], 2))
        n["aligned_pairs"] += len(pairs)
        n["reader_1_only"] += len(o1)
        n["reader_2_only"] += len(o2)
        seen |= {a["claim_id"] for a, _, _ in pairs}
    assert n == _comparison()["phase_b_counts"]
    assert seen == set(PAIR_JUDGEMENTS)


def _adjudicated() -> dict:
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(wp4adj.ADJ_DIR.glob("LIT2-*.json"))}


def test_nothing_deleted_and_reader_1_text_untouched():
    r1, adj = wp4adj.load_r1(), _adjudicated()
    assert sorted(adj) == wp4adj.lit2_ids()
    for iid, rec in r1.items():
        a = {c["claim_id"]: c for c in adj[iid]["claims"]}
        for c in rec["claims"]:
            got = a[c["claim_id"]]
            for k in ("claim_text", "claim_type", "evidence", *wp1b.DIMENSIONS):
                assert got[k] == c[k], (c["claim_id"], k)
        blind_only = [c for c in adj[iid]["claims"] if c.get("origin") == "blind_reader"]
        assert len(a) == len(rec["claims"]) + len(blind_only)


def test_statuses_tiers_and_flags_are_consistent():
    summ = json.loads(wp4adj.ADJ_SUMMARY_PATH.read_text(encoding="utf-8"))
    tiers = {"A": 0, "B": 0, "C": 0}
    for rec in _adjudicated().values():
        contested = rec["scope_adjudication"]["adopted"] == wp1b.CONTESTED
        for c in rec["claims"]:
            assert c["evidence_tier"] == wp1b.evidence_tier(c["claim_validation_status"], contested)
            tiers[c["evidence_tier"]] += 1
            flags = c["adjudication"]["flags"]
            if c["claim_validation_status"] == "single_reader_provisional":
                assert ("blind_reader_only" in flags) == (c.get("origin") == "blind_reader")
                assert ("not_independently_found" in flags) == (c.get("origin") != "blind_reader")
            assert "class" in c["adjudication"]["geography_role"]["adopted"]
    assert tiers == summ["evidence_tier_counts"]
    assert summ["overrides_used"] == []


def test_every_promoted_claim_carries_exact_evidence():
    for rec in _adjudicated().values():
        for c in rec["claims"]:
            ev = c["evidence"]
            assert ev["evidence_sha256"] == evidence_sha256(ev["evidence_text"])
            assert 0 <= ev["char_start"] < ev["char_end"]


def test_prior_exposure_is_recorded():
    cmp = _comparison()
    assert cmp["prior_exposure"]["item"] == "LIT2-001075"
    assert cmp["prior_exposure"]["reader_1_record_field"]
    assert cmp["prior_exposure"]["reader_2_record_field"] is None
    assert "prior_exposure_note" in _adjudicated()["LIT2-001075"]["adjudication_provenance"]
    assert cmp["adjudicator"].startswith("reader 1")


def _corpus_root() -> Path | None:
    try:
        from climrr.paths import get
        root = Path(get(wp4adj.ROOT_KEY))
    except Exception:  # noqa: BLE001
        return None
    return root if root.is_dir() else None


@pytest.mark.skipif(_corpus_root() is None, reason="litcorpus02_root not configured")
def test_every_span_of_both_readings_re_slices():
    counts = wp4adj.verify_all_spans(_corpus_root(), wp4adj.load_r1(), wp4adj.load_r2())
    assert counts == {k: v for k, v in _comparison()["span_verification"].items() if k != "failures"}
