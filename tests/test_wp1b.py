"""M4-WP1b-adj: frozen inputs, adjudication rules, and the adjudicated claim set."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from climrr import wp1b as w
from climrr.paths import REPO_ROOT
from climrr.wp1b_judgements import PAIR_JUDGEMENTS


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _comparison() -> dict:
    return _load(w.COMPARISON_PATH)


def _adjudicated() -> dict:
    return {p.stem: _load(p) for p in sorted(w.ADJ_DIR.glob("LIT-*.json"))}


# --- frozen inputs ------------------------------------------------------------------


def test_both_input_sets_match_their_committed_hashes():
    observed = w.verify_inputs()
    assert observed == w.FROZEN_INPUT_SHA256
    assert sum(1 for k in observed if "/wp1_claims/" in k) == 10
    assert sum(1 for k in observed if "/wp1b_blind/" in k) == 11


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required")
def test_the_blind_pins_equal_the_bytes_frozen_at_the_blind_commit():
    for rel, sha in w.FROZEN_INPUT_SHA256.items():
        if "/wp1b_blind/" not in rel:
            continue
        blob = subprocess.run(["git", "show", f"{w.BLIND_COMMIT}:{rel}"], cwd=REPO_ROOT,
                              capture_output=True, check=True).stdout
        assert hashlib.sha256(blob).hexdigest() == sha, rel


def test_a_changed_pin_fails_verification(monkeypatch):
    pins = dict(w.FROZEN_INPUT_SHA256)
    pins["artifacts/literature/wp1b_blind/54542600.json"] = "0" * 64
    monkeypatch.setattr(w, "FROZEN_INPUT_SHA256", pins)
    with pytest.raises(w.AdjudicationError):
        w.verify_inputs()


def test_the_comparison_records_the_input_hashes_and_the_blind_disclosures_verbatim():
    c = _comparison()
    assert c["inputs"]["sha256"] == w.FROZEN_INPUT_SHA256
    assert c["reader_2_disclosed_deviations_verbatim"] == w.load_r2_summary()["protocol_notes"]


@pytest.mark.skipif(not (REPO_ROOT / "config" / "local_paths.yaml").is_file(),
                    reason="external corpus not configured on this host")
def test_every_span_of_both_readings_re_slices():
    from climrr.paths import load_local_paths

    root = load_local_paths().get("literature_corpus_root")
    if not root or str(root).startswith("<") or not Path(root).is_dir():
        pytest.skip("literature_corpus_root not available on this host")
    s = w.load_sample()
    counts = w.verify_all_spans(Path(root), s, w.load_r1(), w.load_r2(s))
    assert counts == {"reader_1": 96, "reader_2": 85}


# --- scope rule ---------------------------------------------------------------------


@pytest.mark.parametrize("s1,s2,adopted", [
    ("in_scope_hazard", "in_scope_hazard", "in_scope_hazard"),
    ("ambiguous", "ambiguous", "ambiguous"),
    ("in_scope_hazard", "ambiguous", w.CONTESTED),
    ("ambiguous", "in_scope_hazard", w.CONTESTED),
    ("off_topic", "ambiguous", "ambiguous"),
    ("in_scope_hazard", "off_topic", "ambiguous"),
])
def test_scope_rule(s1, s2, adopted):
    assert w.adjudicate_scope(s1, s2)[0] == adopted


# --- rules 2-3 on synthetic pairs ----------------------------------------------------


def _claim(cid: str, **dims) -> dict:
    ev = {"json_path": "$.abstract", "char_start": 0, "char_end": 10, "evidence_text": "x" * 10}
    c = {"claim_id": cid, "text": "t", "claim_type": "finding", "evidence": ev}
    for d in w.DIMENSIONS:
        c[d] = {"value": "unknown", "tag": "unknown"}
    c.update(dims)
    return c


def _sup():
    return {"json_path": "$.title", "char_start": 0, "char_end": 3, "evidence_text": "abc"}


def test_identical_claims_are_independently_confirmed():
    a = _claim("A", concept={"value": "heat", "tag": "explicit"})
    b = _claim("B", concept={"value": "Heat ", "tag": "explicit"})
    assert w.resolve_pair(a, b, {})["status"] == "independently_confirmed"


def test_textual_difference_without_a_judgement_is_refused():
    a = _claim("A", concept={"value": "heat", "tag": "explicit"})
    b = _claim("B", concept={"value": "hot days", "tag": "explicit"})
    with pytest.raises(w.AdjudicationError):
        w.resolve_pair(a, b, {})


def test_judged_same_content_and_tag_is_still_confirmed():
    a = _claim("A", concept={"value": "heat", "tag": "explicit"})
    b = _claim("B", concept={"value": "hot", "tag": "explicit"})
    assert w.resolve_pair(a, b, {"concept": {"content": "same"}})["status"] == "independently_confirmed"


def test_unknown_beats_a_value():
    a = _claim("A", geography={"value": "coastal", "tag": "explicit"})
    b = _claim("B")
    r = w.resolve_pair(a, b, {"geography": {"content": "differs"}})
    assert r["status"] == "adjudicated_modified"
    assert r["decisions"]["geography"]["adopted"] == {"value": "unknown", "tag": "unknown"}


def test_explicit_vs_inferred_requires_the_span_check():
    a = _claim("A", geography={"value": "X", "tag": "explicit", "support": _sup()})
    b = _claim("B", geography={"value": "X", "tag": "inferred", "support": _sup()})
    with pytest.raises(w.AdjudicationError):
        w.resolve_pair(a, b, {"geography": {"content": "same"}})
    ok = w.resolve_pair(a, b, {"geography": {"content": "same", "explicit_span_states": False,
                                             "adopted": {"value": "X", "tag": "inferred", "support_from": "r2"}}})
    assert ok["decisions"]["geography"]["adopted"]["tag"] == "inferred"
    with pytest.raises(w.AdjudicationError):  # tag contradicting the check
        w.resolve_pair(a, b, {"geography": {"content": "same", "explicit_span_states": False,
                                            "adopted": {"value": "X", "tag": "explicit", "support_from": "r1"}}})


def test_kept_explicit_must_cite_the_explicit_readers_span():
    a = _claim("A", geography={"value": "X", "tag": "explicit", "support": _sup()})
    b = _claim("B", geography={"value": "X", "tag": "inferred", "support": _sup()})
    with pytest.raises(w.AdjudicationError):
        w.resolve_pair(a, b, {"geography": {"content": "same", "explicit_span_states": True,
                                            "adopted": {"value": "X", "tag": "explicit", "support_from": "r2"}}})


def test_claim_type_difference_can_be_an_unresolved_tie():
    a, b = _claim("A"), _claim("B")
    b["claim_type"] = "mechanism"
    r = w.resolve_pair(a, b, {"claim_type": {"content": "differs", "adopted": "unresolved_tie"}})
    assert r["status"] == "adjudicated_modified" and r["unresolved_ties"] == ["claim_type"]


def test_an_override_needs_an_id_and_a_reason_and_keeps_the_rule_result():
    a = _claim("A")
    b = _claim("B", experimental_condition={"value": "16 wk", "tag": "explicit", "support": _sup()})
    ov = {"adopted": {"value": "16 wk", "tag": "explicit", "support_from": "r2"}}
    with pytest.raises(w.AdjudicationError):
        w.resolve_pair(a, b, {"experimental_condition": {"content": "differs", "override": ov}})
    ov.update(judgement_id="J-x", reason="r")
    r = w.resolve_pair(a, b, {"experimental_condition": {"content": "differs", "override": ov}})
    d = r["decisions"]["experimental_condition"]
    assert d["rule_result"] == {"value": "unknown", "tag": "unknown"} and d["adopted"]["value"] == "16 wk"


def test_alignment_refuses_many_to_one_overlap():
    a = _claim("A")
    b1, b2 = _claim("B1"), _claim("B2")
    with pytest.raises(w.AdjudicationError):
        w.align([a], [b1, b2])


def test_reader_2_raw_keys_normalise_to_reader_1_paths():
    assert w.norm_path("juvenile experiments") == '$["juvenile experiments"]'
    assert w.norm_path("abstract") == "$.abstract"
    assert w.norm_path("$.abstract") == "$.abstract"


# --- the real comparison --------------------------------------------------------------


def test_every_recorded_decision_reproduces_from_the_frozen_readings_and_judgements():
    s = w.load_sample()
    r1, r2 = w.load_r1(), w.load_r2(s)
    c = _comparison()
    n_pairs = 0
    for it in c["phase_b_alignment"]:
        pairs, only1, only2 = w.align(w.claims_of(r1[it["item_id"]], 1), w.claims_of(r2[it["item_id"]], 2))
        assert [(a["claim_id"], b["claim_id"]) for a, b, _ in pairs] == \
               [(p["reader_1_claim_id"], p["reader_2_claim_id"]) for p in it["pairs"]]
        assert [a["claim_id"] for a in only1] == [x["claim_id"] for x in it["reader_1_only"]]
        assert [b["claim_id"] for b in only2] == [x["claim_id"] for x in it["reader_2_only"]]
        for (a, b, _), rec in zip(pairs, it["pairs"]):
            res = w.resolve_pair(a, b, PAIR_JUDGEMENTS[a["claim_id"]])
            assert res["status"] == rec["status"] and res["decisions"] == rec["decisions"]
            n_pairs += 1
    assert n_pairs == len(PAIR_JUDGEMENTS) == 19


def test_phase_counts():
    c = _comparison()
    assert c["phase_b_counts"] == {"aligned_pairs": 19, "reader_1_only": 8, "reader_2_only": 2}
    assert c["phase_c_statistics"]["scope_agreement"] == {"agree": 6, "n": 10}
    assert "not inferential" in c["phase_c_statistics"]["caveat"] or "no inferential" in c["phase_c_statistics"]["caveat"]


# --- the adjudicated set ---------------------------------------------------------------


ADDED_KEYS = {"first_pass_claim_validation_status", "adjudication", "claim_validation_status"}


def test_every_first_pass_claim_keeps_its_id_and_content_and_gains_a_status():
    r1, adj = w.load_r1(), _adjudicated()
    assert set(adj) == set(r1)
    for iid, rec in r1.items():
        by_id = {c["claim_id"]: c for c in adj[iid]["claims"]}
        for c in rec["claims"]:
            a = by_id[c["claim_id"]]
            assert a["first_pass_claim_validation_status"] == c["claim_validation_status"]
            assert a["claim_validation_status"] in w.STATUSES
            assert {k: v for k, v in a.items() if k not in ADDED_KEYS} == \
                   {k: v for k, v in c.items() if k != "claim_validation_status"}
        # nothing else in the record removed or changed
        stripped = copy.deepcopy(adj[iid])
        for k in ("scope_adjudication", "adjudication_provenance"):
            stripped.pop(k)
        stripped["claims"] = [x for x in stripped["claims"] if x.get("origin") != "blind_reader"]
        assert {k: v for k, v in stripped.items() if k != "claims"} == {k: v for k, v in rec.items() if k != "claims"}


def test_contested_scope_claims_carry_the_note_and_status():
    rec = _adjudicated()["LIT-000571"]
    assert rec["scope_adjudication"]["adopted"] == w.CONTESTED
    for c in rec["claims"]:
        assert c["claim_validation_status"] == "adjudicated_modified"
        assert w.CONTESTED_NOTE in c["adjudication"]["notes"]


def test_blind_only_claims_are_new_provisional_candidates():
    new = [c for r in _adjudicated().values() for c in r["claims"] if c.get("origin") == "blind_reader"]
    assert sorted(c["claim_id"] for c in new) == ["LIT-001141-B4", "LIT-001711-B3"]
    for c in new:
        assert c["claim_validation_status"] == "single_reader_provisional"
        assert c["adjudication"]["flags"] == ["blind_reader_only"]


def test_status_counts():
    s = _load(w.ADJ_SUMMARY_PATH)
    assert s["status_counts"] == {"independently_confirmed": 1, "adjudicated_modified": 23,
                                  "single_reader_provisional": 5, "rejected_on_review": 0}
    assert s["n_claims_total"] == 29
    assert sum(s["status_counts_first_pass_claims_only"].values()) == 27


def test_no_claim_is_promoted_on_an_item_whose_adopted_scope_is_ambiguous():
    for r in _adjudicated().values():
        if r["scope_adjudication"]["adopted"] == "ambiguous":
            assert all(c["claim_validation_status"] == "rejected_on_review" for c in r["claims"])


def test_the_adjudicated_records_carry_no_prototype_label():
    import re
    banned = re.compile(r"support(s|ing)? the prototype|P-CELL|P-COUNTY|P-STATE|compatib", re.IGNORECASE)
    for r in _adjudicated().values():
        assert not banned.search(json.dumps(r, ensure_ascii=False))


def test_the_adjudication_document_is_in_the_knowledge_list():
    import importlib.util
    spec = importlib.util.spec_from_file_location("sk", REPO_ROOT / "scripts" / "stage_knowledge.py")
    sk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sk)
    assert "docs/LITERATURE_WP1B_ADJUDICATION.md" in sk.KNOWLEDGE_FILES
