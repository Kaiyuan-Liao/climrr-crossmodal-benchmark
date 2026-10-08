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
