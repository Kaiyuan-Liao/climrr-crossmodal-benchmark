"""Grouping run 2 ingest, synthesis packets and the groups review CSV (pilot P2b-ingest; D-051, D-052).

Checks the ingested copy, not the delivered tarball (which stays outside the repository): every
manifest hash; the run facts (23 chunks, 15 corrective turns, 12 passed first time, three on a second
attempt with identical configuration); 239 groups and 155 singletons covering the 747 statements once;
`groups_enriched.jsonl` and its summary re-derived from tracked inputs; the ten packets against their
manifest and DR-SEED-RANK-2; the tracked GROUPS CSV rebuilt from the tracked files.
"""

from __future__ import annotations

import json

import pytest

from climrr import itemseeds as sd
from climrr import litgeo as lg
from climrr import litgroups as lgr
from climrr import litgroups_run2 as g2
from climrr import litindependence as li
from climrr import litstatements_run2 as r2
from climrr import p2b_review as rv
from climrr import synthpackets as spk
from climrr.checksums import sha256_file

MAN = json.loads(g2.MANIFEST_PATH.read_text(encoding="utf-8"))
SUMM = json.loads(g2.ENRICHED_SUMMARY_PATH.read_text(encoding="utf-8"))
PM = json.loads((spk.PACKETS_DIR / "manifest.json").read_text(encoding="utf-8"))


def _jsonl(path):
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


@pytest.fixture(scope="module")
def enriched():
    return _jsonl(g2.ENRICHED_PATH)


@pytest.fixture(scope="module")
def packets():
    return [json.loads((spk.PACKETS_DIR / f"{x['packet_id']}.json").read_text(encoding="utf-8")) for x in PM["packets"]]


def test_every_manifest_file_matches_its_hash():
    assert MAN["tarball"]["sha256"] == g2.TARBALL_SHA256 and MAN["decision"] == "D-052"
    for f in MAN["files"] + MAN["derived_files"]:
        p = g2.ART / f["path"]
        assert sha256_file(p) == f["sha256"] and p.stat().st_size == f["bytes"], f["path"]
    chunks = [f["path"] for f in MAN["files"] if f["path"].startswith("chunks/")]
    assert len(chunks) == 23 + 3
    assert sorted(c for c in chunks if c.endswith(".failed_attempt1.json")) == [
        f"chunks/{c}.failed_attempt1.json" for c in g2.SECOND_ATTEMPT_CHUNKS]
    assert {f["path"].rsplit("/", 1)[1] for f in MAN["excluded_files"]} == set(g2.EXCLUDED_NAMES)
    assert len(MAN["excluded_files"]) == 23 + 23 + 15 + 15
    assert not [p for p in g2.ART.rglob("*") if p.name in g2.EXCLUDED_NAMES]
    assert sha256_file(g2.ART / "groups.jsonl") == g2.GROUPS_SHA256
    assert sha256_file(g2.ART / "summary.json") == g2.SUMMARY_SHA256
    assert (g2.ART / "agent.log").read_bytes() == (g2.ART / "litgroups_run2.log").read_bytes()


def test_run_facts():
    assert MAN["counts"] == g2.RUN_FACTS
    assert MAN["budget"] == {"reasoning_effort": "low", "max_tokens": 16000, "chunk_size": 40, "temperature": 0}
    assert MAN["generator"]["agent_sha256"] == sha256_file(g2.REPO_ROOT / g2.AGENT_REL) == g2.AGENT_SHA256
    assert MAN["source_commit"].startswith("7676e53")
    assert MAN["partitions"]["sha256"] == sha256_file(lgr.PARTITIONS_PATH)
    assert len(MAN["corrective_chunks"]) == 15 and len(MAN["corrective_passed_first_attempt"]) == 12
    second = MAN["second_attempt_chunks"]
    assert tuple(x["chunk_id"] for x in second) == g2.SECOND_ATTEMPT_CHUNKS
    for x in second:
        assert x["same_configuration"] and x["first_attempt"]["status"] == "deterministic_fail"
        assert x["first_attempt"]["failed"] == ["ids_exactly_once_pass"] and x["second_attempt"]["status"] == "deterministic_pass"
    assert MAN["superseded_runs"][0]["run"] == "run1" and MAN["superseded_runs"][0]["reason"] == "budget"
    assert MAN["superseded_runs"][0]["observed"]["partitions_pass"] == 2
    assert not (g2.ART.parent / "run1").exists()
    for c in g2.SECOND_ATTEMPT_CHUNKS:
        final = json.loads((g2.CHUNKS_DIR / f"{c}.json").read_text(encoding="utf-8"))
        assert final["status"] == "deterministic_pass" and final["endpoint_label"] == "sophia_vllm"


def test_groups_cover_every_statement_once(enriched):
    assert len(enriched) == 239 + 155
    assert sum(not g["is_singleton"] for g in enriched) == 239
    assert sum(not g["is_singleton"] and g["n_members"] == 1 for g in enriched) == SUMM["groups_with_one_member"] == 105
    ids = [m["statement_id"] for g in enriched for m in g["members"]]
    assert len(ids) == len(set(ids)) == 747
    for g in enriched:
        assert [m["statement_id"] for m in g["members"]] == g["member_ids"]
        assert all(m["statement_id"].startswith(f"LS-{m['paper_item_id']}-") for m in g["members"])
        assert g["is_singleton"] == (g["kind"] == "singleton") and (len(g["members"]) == 1 or not g["is_singleton"])
        assert (len(g["members"]) == 1) == bool(g["checks"].get("single_member") or g["is_singleton"])
        assert g["partition"] == g["partition_id"] and g["chunk"] == g["chunk_id"] and g["claim_about"]
        assert g["n_independent_papers"] <= g["n_papers"] <= g["n_members"]
        assert g["region_classes"] == [c for c in lg.CLASSES if c in g["region_class_counts"]]


def test_enrichment_and_summary_rederive(enriched):
    records = sd.read_jsonl(r2.INGESTED_PATH)
    indep = json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    again = g2.enrich(lgr.read_groups(g2.ART / "groups.jsonl"), lgr.read_groups(lgr.PARTITIONS_PATH), records, indep,
                      lg.Gazetteer(sd.nca_map()))
    assert again == enriched
    assert g2.summarise(enriched) == SUMM
    assert SUMM["labels_with_digit_not_in_members"] == []
    assert sum(SUMM["multi_source_mechanism_groups_by_arm"].values()) == sum(
        not g["is_singleton"] and g["claim_about"] == "hazard_change_mechanism" and g["evidence_strength"] == "multi_source_supported"
        for g in enriched)


def test_strength_follows_the_definitions(enriched):
    for g in enriched:
        cc = {m["canonical_paper"] for m in g["members"] if m["evidence_role"] in ("core_candidate", "cited_candidate")}
        if g["evidence_strength"] == "multi_source_supported":
            assert len(cc) >= 2
        elif g["evidence_strength"] == "review_supported":
            assert len(cc) < 2 and any(m["passage_type"] == "review_synthesis" for m in g["members"])
        elif g["evidence_strength"] == "single_source_supported":
            assert len(cc) == 1
        else:
            assert g["evidence_strength"] == "background_only" and not cc


def test_packets_match_their_manifest_and_the_rank_rule(packets, enriched):
    assert [x["item_id"] for x in PM["packets"]] == [f"BI-P2B-{i:04d}" for i in range(1, 11)]
    assert PM["inputs_sha256"]["groups"] == sha256_file(g2.ENRICHED_PATH)
    assert PM["inputs_sha256"]["group_dispositions"] == sha256_file(lgr.DISPOSITIONS_PATH)
    assert PM["version"] == "synthpackets v3b" and PM["dispositions"]["dispositions_version"] == "group_dispositions_v1a"
    assert PM["undisposed_candidates"] == [] and all(x["excluded_no_disposition"] == 0 for x in PM["packets"])   # D-053a
    disp = lgr.load_dispositions()
    by_id = {g["group_id"]: g for g in enriched}
    for x, pk in zip(PM["packets"], packets):
        assert sha256_file(spk.PACKETS_DIR / f"{x['packet_id']}.json") == x["sha256"]
        assert pk["item_id"] == x["item_id"] and pk["descriptor_rule"] == "DR-DESC-1"
        assert (pk["version"], pk["rank_rule"]) == (("synthpackets v3b", "DR-SEED-RANK-3a") if pk["use_case_level"] == 7
                                                    else ("synthpackets v3a", "DR-SEED-RANK-3"))     # D-054a: rung 7 only
        assert pk["model_view"]["patterns"][0]["allowed_descriptors"]["direction"] == "increase"
        gs = pk["provenance"]["groups"]
        roles = [g["role"] for g in gs]
        if pk["use_case_level"] == 1:
            assert gs == [] and pk["excluded_groups"] == []
            continue
        assert roles.count("driver") <= 10 and roles.count("context") <= 4 and roles.count("caveat") <= 4
        assert ("caveat" in roles) == (pk["use_case_level"] == 7)
        for g in gs:
            assert g["group_id"] in by_id
            d = disp.get(g["group_id"])
            assert d is not None                                                            # D-053a
            assert g["claim_about"] == (d["arg"] if d and d["kind"] == "relabel" else by_id[g["group_id"]]["claim_about"])
            assert not (d and d["kind"] in ("not_about_family", "reject", "merge_with"))     # D-053
            if g["role"] == "driver":
                assert g["claim_about"] == "hazard_change_mechanism"
            if g["role"] == "context":
                assert g["claim_about"] == "hazard_definition_or_measurement"
            if g["role"] == "caveat":                                                       # D-054, D-054a
                assert g["claim_about"] in spk.CAVEAT_CLAIMS and not (d and d["kind"] == "exclude_from_rung7")
                assert g["statement_type"] == "caveat" and (g.get("scenario_slot") or by_id[g["group_id"]]["statement_type"] == "caveat")
        for role in ("driver", "context", "caveat"):
            keys = [(not g.get("scenario_slot"), *spk.rank_key(g)) for g in gs if g["role"] == role]
            assert keys == sorted(keys)
        for mg in pk["model_view"]["groups"]:
            assert all(len(m["passage"]) <= spk.MAX_PASSAGE for m in mg["members"])
        assert all(e["reason"] for e in pk["excluded_groups"])
    assert [pk["use_case_level"] for pk in packets] == [1, 1, 3, 3, 3, 3, 4, 4, 4, 7]


def test_groups_csv_rebuilds_from_tracked_files():
    man, summ, enriched, packets, pm = rv.inputs()
    rows = rv.group_rows(enriched)
    assert rv.groups_csv(rows) == rv.GROUPS_CSV_PATH.read_text(encoding="utf-8")
    assert len(rows) - 1 == 239 and rows[0][-2:] == ["kaiyuan_disposition", "note"]
    assert len(rv.singleton_rows(enriched)) - 1 == 155
    assert len(rv.packet_rows(packets)) - 1 == sum(len(pk["provenance"]["groups"]) for pk in packets)
