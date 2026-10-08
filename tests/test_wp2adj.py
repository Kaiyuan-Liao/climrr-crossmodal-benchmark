"""M4-WP2 Phase 3: frozen readings, adjudication by the WP1b rules, and the adjudicated set."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from climrr import wp1b, wp2adj
from climrr.paths import REPO_ROOT
from climrr.wp2_judgements import PAIR_JUDGEMENTS


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _adj() -> dict:
    return {p.stem: _load(p) for p in sorted(wp2adj.ADJ_DIR.glob("LIT-*.json"))}


def test_both_readings_match_their_pins():
    assert wp2adj.verify_inputs() == wp2adj.FROZEN_INPUT_SHA256


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required")
@pytest.mark.parametrize("prefix,commit", [("artifacts/literature/wp2_blind/", wp2adj.BLIND_COMMIT),
                                           ("artifacts/literature/wp2_claims/", wp2adj.READER_1_COMMIT)])
def test_the_pins_equal_the_bytes_at_the_freezing_commits(prefix, commit):
    for rel, sha in wp2adj.FROZEN_INPUT_SHA256.items():
        if rel.startswith(prefix):
            blob = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=REPO_ROOT, capture_output=True, check=True).stdout
            assert hashlib.sha256(blob).hexdigest() == sha, rel


@pytest.mark.parametrize("raw,canon", [('$["abstract"]', "$.abstract"), ('$["data and methods"]', '$["data and methods"]'),
                                       ("$.results", "$.results"), ("discussion", "$.discussion")])
def test_paths_normalise_to_one_form(raw, canon):
    assert wp2adj.norm_path(raw) == canon


@pytest.mark.skipif(not (REPO_ROOT / "config" / "local_paths.yaml").is_file(), reason="corpus not configured")
def test_every_span_of_both_readings_re_slices():
    from climrr.paths import load_local_paths
    root = load_local_paths().get("literature_corpus_root")
    if not root or str(root).startswith("<") or not Path(root).is_dir():
        pytest.skip("literature_corpus_root not available")
    assert wp2adj.verify_all_spans(Path(root), wp2adj.load_r1(), wp2adj.load_r2()) == {"reader_1": 63, "reader_2": 66}


def test_every_decision_reproduces_and_no_override_is_used():
    r1, r2 = wp2adj.load_r1(), wp2adj.load_r2()
    cmp = _load(wp2adj.COMPARISON_PATH)
    n = 0
    for it in cmp["phase_b_alignment"]:
        pairs, o1, o2 = wp1b.align(wp2adj.claims_of(r1[it["item_id"]], 1), wp2adj.claims_of(r2[it["item_id"]], 2))
        assert [(a["claim_id"], b["claim_id"]) for a, b, _ in pairs] == [(p["reader_1_claim_id"], p["reader_2_claim_id"]) for p in it["pairs"]]
        assert [a["claim_id"] for a in o1] == [x["claim_id"] for x in it["reader_1_only"]]
        assert [b["claim_id"] for b in o2] == [x["claim_id"] for x in it["reader_2_only"]]
        for (a, b, _), rec in zip(pairs, it["pairs"]):
            res = wp1b.resolve_pair(a, b, PAIR_JUDGEMENTS[a["claim_id"]])
            assert res["status"] == rec["status"] and res["decisions"] == rec["decisions"] and res["overrides"] == []
            n += 1
    assert n == len(PAIR_JUDGEMENTS) == 13
    assert cmp["phase_b_counts"] == {"aligned_pairs": 13, "reader_1_only": 7, "reader_2_only": 6}


def test_status_and_tier_counts():
    s = _load(wp2adj.ADJ_SUMMARY_PATH)
    assert s["status_counts"] == {"independently_confirmed": 6, "adjudicated_modified": 7,
                                  "single_reader_provisional": 13, "rejected_on_review": 0}
    assert s["evidence_tier_counts"] == {"A": 6, "B": 7, "C": 13}
    for r in _adj().values():
        for c in r["claims"]:
            assert c["evidence_tier"] == wp1b.evidence_tier(c["claim_validation_status"], False)


ADDED = {"first_pass_claim_validation_status", "first_pass_evidence_tier", "adjudication",
         "claim_validation_status", "evidence_tier"}


def test_every_reader_1_claim_keeps_its_id_and_content():
    r1, adj = wp2adj.load_r1(), _adj()
    for iid, rec in r1.items():
        by = {c["claim_id"]: c for c in adj[iid]["claims"]}
        for c in rec["claims"]:
            a = by[c["claim_id"]]
            assert a["first_pass_evidence_tier"] == c["evidence_tier"] == "C"
            assert {k: v for k, v in a.items() if k not in ADDED} == {k: v for k, v in c.items() if k not in ADDED}


def test_blind_only_claims_are_tier_c_candidates():
    new = [c for r in _adj().values() for c in r["claims"] if c.get("origin") == "blind_reader"]
    assert len(new) == 6 and all(c["evidence_tier"] == "C" and c["adjudication"]["flags"] == ["blind_reader_only"] for c in new)
