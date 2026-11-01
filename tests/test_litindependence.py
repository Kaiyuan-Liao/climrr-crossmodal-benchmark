"""Paper independence v2 (DR-LIT-IND-1 v2, D-046) and clusters v1b (pilot P2b-prep)."""

from __future__ import annotations

import json

from climrr import litaggregate as la
from climrr import litindependence as li
from climrr.checksums import sha256_file

PAPERS = [{"item_id": "1", "paper_sha256": "a" * 64, "title": "Heat, Humidity & Health"},
          {"item_id": "2", "paper_sha256": "a" * 64, "title": None},                       # same file as 1
          {"item_id": "3", "paper_sha256": "b" * 64, "title": "heat humidity health"},     # same normalized title as 1
          {"item_id": "4", "paper_sha256": "c" * 64, "title": "Fire weather"},
          {"item_id": "5", "paper_sha256": "d" * 64, "title": None}]


def test_title_normalization_collapses_case_punctuation_and_whitespace():
    assert li.normalize_title("  Heat,  Humidity &\tHealth: a_review ") == "heat humidity health a review"
    assert li.normalize_title("PM2.5 and O3") == "pm2 5 and o3"


def test_groups_canonical_ids_and_bases():
    ind = li.build(PAPERS)
    by = {p["item_id"]: p for p in ind["papers"]}
    assert ind["same_paper_sha256_groups"] == [["1", "2"]]
    assert ind["possible_duplicate_title_groups"] == [["1", "3"]]
    assert ind["merged_groups"] == [["1", "2", "3"]]                  # closed transitively
    assert {i: by[i]["canonical_id"] for i in by} == {"1": "1", "2": "1", "3": "1", "4": "4", "5": "5"}
    assert [by[i]["basis"] for i in "12345"] == ["same_paper_sha256", "same_paper_sha256", "possible_duplicate_title",
                                                 "assumed_independent_distinct_ids", "assumed_independent_distinct_ids"]
    assert ind["canonical_papers_n"] == 3 and "title" not in by["1"]   # titles are kept as hashes only


def test_pairwise_independence_and_counting():
    ind = li.build(PAPERS)
    assert li.independent("1", "2", ind) == (False, "same_paper_sha256")
    assert li.independent("2", "3", ind) == (False, "possible_duplicate_title")
    assert li.independent("1", "4", ind) == (True, "assumed_independent_distinct_ids")
    canon = li.canonical_map(ind)
    assert li.n_independent(["1", "2", "3"], canon) == 1 and li.n_independent(["1", "4", "5"], canon) == 3


def test_strength_v2_counts_canonical_papers():
    canon = li.canonical_map(li.build(PAPERS))
    m = lambda p, role="core_candidate", pt="own_finding": {"paper_item_id": p, "evidence_role": role, "passage_type": pt}  # noqa: E731
    assert li.strength_v2([m("1"), m("2")], canon) == "single_source_supported"
    assert li.strength_v2([m("1"), m("4")], canon) == "multi_source_supported"
    assert li.strength_v2([m("1"), m("2", pt="review_synthesis")], canon) == "review_supported"
    assert li.strength_v2([m("4", "background_consensus_candidate", "background")], canon) == "background_only"


def test_the_frozen_independence_file():
    ind = json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    assert (ind["papers_n"], ind["canonical_papers_n"], ind["rule_id"], ind["decision"]) == (243, 239, "DR-LIT-IND-1 v2", "D-046")
    assert ind["same_paper_sha256_groups"] == [["239052352", "257056592"]]
    assert ind["merged_groups"] == [["221671377", "256835585"], ["237554329", "239696378"], ["239052352", "257056592"],
                                    ["243767055", "257108685"]]
    assert ind["by_basis"] == {"same_paper_sha256": 2, "possible_duplicate_title": 6, "assumed_independent_distinct_ids": 235}


def test_clusters_v1b_keep_members_and_recount_strength():
    v1 = [json.loads(x) for x in la.CLUSTERS_PATH.read_text(encoding="utf-8").splitlines()]
    v1b = [json.loads(x) for x in li.CLUSTERS_V1B_PATH.read_text(encoding="utf-8").splitlines()]
    assert [c["cluster_id"] for c in v1b] == [c["cluster_id"] for c in v1]
    assert all(a["member_statement_ids"] == b["member_statement_ids"] for a, b in zip(v1, v1b))
    s = json.loads(li.CLUSTERS_V1B_SUMMARY_PATH.read_text(encoding="utf-8"))
    assert s["by_strength"] == {"multi_source_supported": 2, "review_supported": 24, "single_source_supported": 456, "background_only": 249}
    assert [c["cluster_id"] for c in s["strength_changed"]] == ["LC-extreme_heat_v1-driver-071"]   # the byte-identical pair
    assert s["clusters_file"]["sha256"] == sha256_file(li.CLUSTERS_V1B_PATH)
