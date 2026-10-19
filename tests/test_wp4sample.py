"""M4-WP4 sample (D-025): the frozen 10 + 10 equals a rebuild, and the rank rule behaves as written.

Nothing here opens a corpus file.
"""

from __future__ import annotations

import json

import pytest

from climrr import wp4sample as w
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

SAMPLE = json.loads(w.SAMPLE_PATH.read_text(encoding="utf-8"))
WP4_SAMPLE_SHA256 = "f3cb5d0c3c4e0598860b2dad5a66219a3c252a92a7800d193111dec21fdcea15"


def test_the_frozen_sample_equals_a_rebuild_and_is_pinned():
    w.verify()
    assert sha256_file(w.SAMPLE_PATH) == WP4_SAMPLE_SHA256
    data = json.loads((REPO_ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))
    l2 = next(c for c in data["external_corpora"] if c["corpus_id"] == SAMPLE["corpus_id"])
    assert l2["wp4_sample"]["wp4_sample_sha256"] == WP4_SAMPLE_SHA256
    assert l2["wp4_sample"]["fetch_list_sha256"] == sha256_file(w.FETCH_PATH)


def test_ten_unique_items_per_arm_twenty_overall_at_the_rule_ranks():
    sel = SAMPLE["selected"]
    assert len(sel) == 20 == len({s["item_id"] for s in sel})
    for arm, step in w.STEP.items():
        mine = [s for s in sel if s["arm"] == arm]
        assert len(mine) == 10
        assert [s["target_rank"] for s in mine] == list(range(step, step * 10 + 1, step))
        ranked = SAMPLE["arms"][arm]["ranked_candidates"]
        for s in mine:
            assert ranked[s["rank"] - 1]["item_id"] == s["item_id"]
    assert not any(s["advanced"] for s in sel)        # this data needed no advance
    assert w.FETCH_PATH.read_text(encoding="utf-8").splitlines() == [s["rel_path"] for s in sel]


def test_ranking_is_by_lit2_after_duplicate_suppression():
    a = SAMPLE["arms"]
    assert (a["fire_weather_v1"]["n_candidates"], a["fire_weather_v1"]["n_suppressed"]) == (100, 0)
    assert (a["extreme_heat_v1"]["n_candidates"], a["extreme_heat_v1"]["n_suppressed"]) == (143, 1)
    sup = a["extreme_heat_v1"]["suppressions"][0]
    assert (sup["item_id"], sup["duplicate_of_item_id"]) == ("257056592", "239052352")
    for arm in w.ARMS:
        r = a[arm]["ranked_candidates"]
        assert [x["lit2_id"] for x in r] == sorted(x["lit2_id"] for x in r)
        assert [x["rank"] for x in r] == list(range(1, len(r) + 1))
        assert len({x["sha256"] for x in r}) == len(r)              # no two exact-byte copies can be sampled


def _cands(n, prefix="x"):
    return [{"rank": k, "item_id": f"{prefix}{k}", "lit2_id": f"LIT2-{k:06d}", "rel_path": "", "sha256": f"{prefix}{k}"}
            for k in range(1, n + 1)]


def test_overlap_keeps_fire_and_advances_heat(monkeypatch):
    fire, heat = _cands(100, "i"), _cands(140, "h")
    heat[13] = {**heat[13], "item_id": "i10"}                     # heat rank 14 is fire's rank-10 item
    got = w.select({"fire_weather_v1": fire, "extreme_heat_v1": heat})
    h = got["extreme_heat_v1"]
    assert (h[0]["rank"], h[0]["advanced"]) == (15, True) and "earlier arm" in h[0]["advance_reasons"][0]
    assert [p["rank"] for p in h[1:]] == list(range(28, 141, 14))


def test_a_missing_rank_advances_and_an_unsatisfiable_one_fails_closed():
    with pytest.raises(w.SampleError, match="cannot be satisfied"):
        w.select({"fire_weather_v1": _cands(99), "extreme_heat_v1": _cands(140, "h")})
    fire, heat = _cands(100), _cands(142, "h")
    heat[139] = {**heat[139], "item_id": "x100"}                   # rank 140 taken by fire -> 141
    assert w.select({"fire_weather_v1": fire, "extreme_heat_v1": heat})["extreme_heat_v1"][-1]["rank"] == 141


def test_a_changed_input_fails_closed(monkeypatch):
    k = next(iter(w.INPUT_SHA256))
    monkeypatch.setitem(w.INPUT_SHA256, k, "0" * 64)
    with pytest.raises(w.SampleError, match="differs from the committed"):
        w.build()


def test_selection_never_reads_a_corpus_file_or_a_hit_location():
    src = (REPO_ROOT / "src" / "climrr" / "wp4sample.py").read_text(encoding="utf-8")
    for banned in ("local_paths", "litcollect_root", "hits.csv", "first_hits", "candidate_hits", "section_key"):
        assert banned not in src
