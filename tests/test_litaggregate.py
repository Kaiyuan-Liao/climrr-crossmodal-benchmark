"""Deterministic aggregation --- `src/climrr/litaggregate.py`, DR-LIT-AGG-1 v2 (pilot P2a Phase B; D-045).

Term, lemmatizer and direction rules on fixed strings; evidence strength on synthetic
members; then the tracked outputs: `clusters_v1.jsonl`, its summary and the two generated
frequency files are re-derived from `statements_ingested.jsonl` byte for byte, every
entering statement sits in exactly one homogeneous cluster, and the replay of the first
rule shows its degeneracy.
"""

from __future__ import annotations

import json

import pytest

from climrr import litaggregate as la
from climrr import litstatements_run2 as r2
from climrr.checksums import sha256_file

SUMMARY = json.loads(la.SUMMARY_PATH.read_text(encoding="utf-8"))
META = json.loads(r2.PAPERS_META_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def prepared():
    records = [json.loads(ln) for ln in r2.INGESTED_PATH.read_text(encoding="utf-8").splitlines()]
    return la.Prepared(records)


@pytest.fixture(scope="module")
def clusters():
    return [json.loads(ln) for ln in la.CLUSTERS_PATH.read_text(encoding="utf-8").splitlines()]


# --- rules on fixed strings -------------------------------------------------------------------------


@pytest.mark.parametrize("w,out", [("warming", "warm"), ("rising", "ris"), ("king", "king"), ("increased", "increas"),
                                   ("bed", "bed"), ("fuels", "fuel"), ("grass", "grass"), ("gas", "gas"), ("index", "index")])
def test_lemmatizer(w, out):
    assert la.lemma(w) == out


def test_tokens_and_bigrams():
    stop = la.stopwords()
    assert la.content_seq("The vapor-pressure deficit, in 2050, is a key driver of fire!", stop) == \
        ["vapor", "pressure", "deficit", "key", "driver", "fire"]
    g = la.grams("Low relative humidity dries fuels", stop)
    assert {"relative humidity", "humidity drie", "fuel", "low relative"} <= g and "low" in g


def test_stopwords_are_strings_and_keep_us():
    stop = la.stopwords()
    assert all(isinstance(w, str) for w in stop) and {"no", "on", "off"} <= stop and "us" not in stop


@pytest.mark.parametrize("text,d", [
    ("Heat index days increase under warming.", "increase"),
    ("Extreme fire weather becomes more frequent.", "increase"),
    ("Fuel moisture declines in late summer.", "decrease"),
    ("Fires are less frequent in wet years.", "decrease"),
    ("Lower humidity raises the heat index and higher wind spreads fire.", "unspecified"),  # both lists
    ("The heat index combines temperature and humidity.", "unspecified"),
    ("Increasingly hot nights.", "unspecified"),                                              # whole words only
])
def test_direction(text, d):
    assert la.direction(text, la.direction_lexicon())[0] == d


def test_cosine_and_jaccard():
    a, b = {"x": 1.0, "y": 2.0}, {"y": 2.0, "z": 1.0}
    assert la.cosine(a, b) == pytest.approx(4 / 5)
    assert la.jaccard(a, b) == pytest.approx(1 / 3) and la.cosine({}, a) == 0.0


def test_union_find_is_transitive_and_ordered():
    groups = la.union_find(["c", "a", "b", "d"], lambda x, y: {x, y} in ({"a", "b"}, {"b", "c"}))
    assert groups == [["a", "b", "c"], ["d"]]


def _m(paper, role, ptype="own_finding"):
    return {"paper_item_id": paper, "evidence_role": role, "proposal": {"passage_type": ptype}}


@pytest.mark.parametrize("members,strength", [
    ([_m("1", "core_candidate"), _m("2", "cited_candidate", "cited_finding")], "multi_source_supported"),
    ([_m("1", "core_candidate"), _m("1", "core_candidate")], "single_source_supported"),
    ([_m("1", "core_candidate", "review_synthesis")], "review_supported"),
    ([_m("1", "core_candidate"), _m("2", "background_consensus_candidate", "background")], "single_source_supported"),
    ([_m("1", "background_consensus_candidate", "background"), _m("2", "background_consensus_candidate", "background")],
     "background_only"),
])
def test_evidence_strength(members, strength):
    assert la.evidence_strength(members) == strength


# --- the tracked outputs -------------------------------------------------------------------------------


def test_lexicon_files_are_pinned_in_the_summary():
    for v in SUMMARY["lexicons"].values():
        assert sha256_file(la.REPO_ROOT / v["path"]) == v["sha256"], v["path"]
    assert sha256_file(la.CLUSTERS_PATH) == SUMMARY["clusters_file"]["sha256"]
    assert SUMMARY["inputs"]["statements_ingested"]["sha256"] == sha256_file(r2.INGESTED_PATH)


def test_generated_frequency_files_rederive(prepared):
    sha = sha256_file(r2.INGESTED_PATH)
    lex = la.concept_lexicon(prepared.ent, prepared.stop)
    assert la.CONCEPT_LEXICON.read_text(encoding="utf-8") == la.render_concept_lexicon(lex, sha)
    assert la.DF_DROPPED.read_text(encoding="utf-8") == la.render_df_dropped(prepared, sha)
    assert all(len(lex[a]["tokens"]) == la.LEXICON_TOP for a in la.ARMS)
    assert "used_for_merging: false" in la.CONCEPT_LEXICON.read_text(encoding="utf-8")


def test_clusters_and_summary_rederive(prepared, clusters):
    rebuilt = la.cluster_records(prepared, la.clusters_at(prepared), META)
    assert [json.dumps(c, ensure_ascii=False, sort_keys=True) for c in rebuilt] == \
        [json.dumps(c, ensure_ascii=False, sort_keys=True) for c in clusters]
    lex = la.concept_lexicon(prepared.ent, prepared.stop)
    assert json.loads(json.dumps(la.summarise(clusters, prepared, META, lex))) == SUMMARY


def test_every_entering_statement_is_in_one_homogeneous_cluster(prepared, clusters):
    seen = [m for c in clusters for m in c["member_statement_ids"]]
    assert sorted(seen) == sorted(prepared.by_id) and len(seen) == len(set(seen)) == 747
    for c in clusters:
        ms = [prepared.by_id[i] for i in c["member_statement_ids"]]
        assert {m["arm"] for m in ms} == {c["arm"]} and {m["proposal"]["statement_type"] for m in ms} == {c["statement_type"]}
        assert {prepared.direction[i] for i in c["member_statement_ids"]} == {c["direction"]}
        assert c["representative_statement"]["statement_id"] in c["member_statement_ids"]
        assert c["representative_statement"]["statement"] == prepared.by_id[c["representative_statement"]["statement_id"]]["proposal"]["statement"]
        assert c["n_statements"] == len(ms) and c["n_papers"] == len({m["paper_item_id"] for m in ms})
        assert c["evidence_strength"] == la.evidence_strength(ms)


def test_only_the_three_entering_roles_enter(prepared):
    assert {r["evidence_role"] for r in prepared.ent} == set(la.ENTERING_ROLES)
    assert SUMMARY["entering_by_role"] == {"core_candidate": 379, "cited_candidate": 106, "background_consensus_candidate": 262}


def test_cluster_ids_are_numbered_within_arm_and_type(clusters):
    for c in clusters:
        assert c["cluster_id"].startswith(f"LC-{c['arm']}-{c['statement_type']}-")
    assert len({c["cluster_id"] for c in clusters}) == len(clusters)


def test_v2_counts_and_no_large_cluster():
    assert (SUMMARY["clusters"], SUMMARY["singletons"]) == (731, 721)
    assert SUMMARY["by_strength"] == {"multi_source_supported": 3, "review_supported": 24, "single_source_supported": 455,
                                      "background_only": 249}
    assert all(r["clusters_over_25"] == 0 for r in SUMMARY["sensitivity"])
    assert [r["threshold"] for r in SUMMARY["sensitivity"]] == list(la.GRID) * 2
    assert SUMMARY["multi_source_relies_on_diagnostic_pair"] == ["LC-extreme_heat_v1-driver-071"]


def test_the_first_rule_degenerates():
    merged = [r for r in SUMMARY["rule_v1_degeneracy"] if r["concept_lexicon_merge"]]
    assert len({(r["clusters"], r["largest"]) for r in merged}) == 1           # the threshold does not matter
    assert merged[0]["largest"] > 100 and merged[0]["clusters"] < 60


def test_df_filter_drops_the_topic_words():
    assert {"heat", "temperature", "index", "heat index", "humidity"} <= set(SUMMARY["df_dropped"]["extreme_heat_v1"])
    assert {"fire", "weather", "fire weather", "danger"} <= set(SUMMARY["df_dropped"]["fire_weather_v1"])
