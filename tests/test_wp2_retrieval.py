"""M4-WP2 retrieval (D-018): frozen terms, the selection rule, and the no-reading boundary."""

from __future__ import annotations

import json

from climrr import wp2retrieve


def _terms() -> dict:
    return json.loads(wp2retrieve.TERMS_PATH.read_text(encoding="utf-8"))


def test_the_frozen_terms_equal_a_rebuild():
    assert wp2retrieve.build_terms() == _terms()


def test_terms_are_approved_concept_terms_and_the_three_exact_place_labels_only():
    t = [(x["term_class"], x["term"]) for x in _terms()["terms"]]
    assert t == [("concept", "fire weather index"), ("concept", "FWI"), ("concept", "heat index"),
                 ("place", "Oklahoma"), ("place", "Stephens"), ("place", "California")]


# --- the frozen pool and candidates ---------------------------------------------

import pytest  # noqa: E402

POOL = json.loads(wp2retrieve.POOL_PATH.read_text(encoding="utf-8"))
CANDS = json.loads(wp2retrieve.CANDIDATES_PATH.read_text(encoding="utf-8"))
MANIFEST = json.loads(wp2retrieve.CORPUS_MANIFEST_PATH.read_text(encoding="utf-8"))


def test_the_candidates_re_derive_from_the_pool_the_manifest_and_the_rule():
    qualifying = [p["item_id"] for p in POOL["pool"]] + POOL["removed_as_later_duplicates"]
    chosen, removed = wp2retrieve.select(sorted(qualifying), MANIFEST["entries"])
    assert chosen == CANDS["candidate_ids"]
    assert removed == POOL["removed_as_later_duplicates"]
    assert CANDS["candidate_ids"] == sorted(CANDS["candidate_ids"])
    assert len(CANDS["candidate_ids"]) == min(wp2retrieve.CAP, POOL["n_qualifying_pool"])


def test_every_pool_item_qualifies_and_every_candidate_carries_its_hits():
    for p in POOL["pool"]:
        assert p["concept_hits"] >= 1 and p["place_hits"] >= 1
    for c in CANDS["candidates"]:
        assert sum(h["term_class"] == "concept" for h in c["hits"]) == c["concept_hits"]
        assert sum(h["term_class"] == "place" for h in c["hits"]) == c["place_hits"]


def test_artifacts_are_tied_to_the_frozen_terms_and_corpus():
    from climrr.checksums import sha256_file
    for a in (POOL, CANDS):
        assert a["terms_sha256"] == sha256_file(wp2retrieve.TERMS_PATH)
        assert a["corpus_manifest_sha256"] == sha256_file(wp2retrieve.CORPUS_MANIFEST_PATH)
        assert a["statement"] == "Relevance-guided candidate-generation sample, not representative."
    assert CANDS["qualifying_pool_sha256"] == sha256_file(wp2retrieve.POOL_PATH)


def test_no_decoded_text_is_stored_beyond_each_hit_s_matched_characters():
    terms = {t["term_id"]: t["term"] for t in json.loads(wp2retrieve.TERMS_PATH.read_text(encoding="utf-8"))["terms"]}
    for c in CANDS["candidates"]:
        for h in c["hits"]:
            assert set(h) == {"item_id", "json_path", "term_id", "term", "term_class", "char_start", "char_end",
                              "matched_text"}
            assert h["matched_text"].casefold() == terms[h["term_id"]].casefold()
            assert h["char_end"] - h["char_start"] == len(h["matched_text"])


def test_the_dedupe_drops_the_later_duplicate_before_the_cap():
    entries = [{"item_id": f"LIT-{i:06d}", "duplicate_group": "D" if i in (3, 4) else None} for i in range(1, 20)]
    q = [f"LIT-{i:06d}" for i in range(1, 20)]
    chosen, removed = wp2retrieve.select(q, entries)
    assert removed == ["LIT-000004"] and "LIT-000003" in chosen and len(chosen) == 12
    assert chosen[-1] == "LIT-000013"  # the cap reaches one further because of the dedupe


def test_a_full_rescan_reproduces_the_frozen_artifacts():
    from pathlib import Path

    from climrr.paths import load_local_paths
    root = load_local_paths().get("literature_corpus_root")
    if not root or str(root).startswith("<") or not Path(root).is_dir():
        pytest.skip("literature_corpus_root not available on this host")
    pool, cands = wp2retrieve.run(Path(root), json.loads(wp2retrieve.TERMS_PATH.read_text(encoding="utf-8")))
    cands["qualifying_pool_sha256"] = wp2retrieve.sha256_file(wp2retrieve.POOL_PATH)
    assert pool == POOL and cands == CANDS


def test_the_candidates_document_agrees_with_the_artifacts_and_states_its_limits():
    from climrr.checksums import sha256_file
    from climrr.paths import REPO_ROOT
    doc = (REPO_ROOT / "docs" / "LITERATURE_WP2_CANDIDATES.md").read_text(encoding="utf-8")
    assert "Relevance-guided candidate-generation sample, not representative." in doc
    assert "No candidate has been read; semantic inspection waits for M4-WP1b (D-018)." in doc
    for c in CANDS["candidates"]:
        assert f"| `{c['item_id']}` | {c['concept_hits']} | {c['place_hits']} |" in doc
    for p in (wp2retrieve.TERMS_PATH, wp2retrieve.POOL_PATH, wp2retrieve.CANDIDATES_PATH):
        assert sha256_file(p) in doc
    assert f"| **Qualifying pool** | **{POOL['n_qualifying_pool']}** |" in doc
