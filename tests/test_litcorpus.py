"""M4-WP3: the frozen LITCORPUS-01 / LITCORPUS-02 records agree with their evidence and with each other.

Nothing here opens a paper; the corpus files are on Eagle. Every check reads
tracked manifests, id lists, hash lists and hit locations only.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from climrr import litcorpus as lc
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

L1, L2, PL = lc.L1_DIR, lc.L2_DIR, lc.PLACE_DIR
E = L2 / "evidence"


def _ids(p: Path) -> list[str]:
    return lc.read_ids(p)


def _csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


# --- evidence integrity ----------------------------------------------------------------

#: tracked copy -> path in 705k_stage1_hashes.txt (copied unredacted)
STAGE1_COPIES = {
    **{E / "queries" / f"{q}_query.txt": f"queries/{q}_query.txt" for q in (*lc.PRODUCTION, *lc.DIAGNOSTIC)},
    **{E / "runs" / q / "ids.txt": f"runs/705k/{q}/ids.txt" for q in (*lc.PRODUCTION, *lc.DIAGNOSTIC)},
    **{E / "runs" / q / "hits.csv": f"runs/705k/{q}/hits.csv" for q in lc.PRODUCTION},
    PL / "places_approved_query.txt": "queries/places_approved_query.txt",
    PL / "summary.json": "runs/705k/places_approved/summary.json",
    PL / "ids.txt": "runs/705k/places_approved/ids.txt",
    PL / "fire_weather_v1_place_candidates.txt": "runs/705k/fire_weather_v1_place_candidates.txt",
    PL / "extreme_heat_v1_place_candidates.txt": "runs/705k/extreme_heat_v1_place_candidates.txt",
}


def test_unredacted_copies_match_the_stage1_hash_list():
    h = lc.read_hash_list(E / "705k_stage1_hashes.txt")
    assert {str(p): sha256_file(p) for p in STAGE1_COPIES} == {str(p): h[k] for p, k in STAGE1_COPIES.items()}


def test_query_files_are_byte_identical_across_the_two_sources_and_match_their_hashes():
    qh = lc.read_hash_list(L1 / "evidence" / "query_hashes_v1.txt")
    assert len(qh) == 6
    for rel, digest in qh.items():
        assert sha256_file(L1 / rel) == digest
    for q in (*lc.PRODUCTION, *lc.DIAGNOSTIC):
        assert (E / "queries" / f"{q}_query.txt").read_bytes() == (L1 / "queries" / f"{q}_query.txt").read_bytes()
        assert _json(E / "runs" / q / "summary.json")["query_sha256"] == qh[f"queries/{q}_query.txt"]


def test_redacted_files_match_their_record_and_carry_no_absolute_path():
    for d in (L1, L2):
        for rel, rec in _json(d / "redactions.json")["files"].items():
            assert sha256_file(REPO_ROOT / rel) == rec["redacted_sha256"]
    for p in [*L1.rglob("*"), *L2.rglob("*")]:
        if p.is_file():
            text = p.read_text(encoding="utf-8")
            assert "/eagl" + "e/" not in text and "/User" + "s/" not in text and "/hom" + "e/" not in text, p


# --- LITCORPUS-01 ----------------------------------------------------------------------


def test_litcorpus01_yields_ids_and_hashes():
    m = _json(L1 / "litcorpus01_manifest.json")
    assert m["corpus_id"] == "LITCORPUS-01-conceptfirst-v1"
    y = m["yields"]
    assert [y[q]["count"] for q in (*lc.PRODUCTION, *lc.DIAGNOSTIC)] == [4, 10, 13, 11]
    assert y["cross_arm_overlap"] == [] and y["unique_production_items"] == 14
    assert m["source"]["shard_bytes"] == 1073892084 and m["source"]["records"] == 54081
    assert "reported by the collection-tool team" in m["source"]["records_provenance"]
    assert m["collection_tool"]["araiadoc_commit"] == "f9d3c6bbf1183bc16040a280a33b5ac9f5a20f23"
    raw = lc.read_hash_list(L1 / "evidence" / "litcorpus01_raw_hashes.txt")
    rows = _csv(L1 / "litcorpus01_manifest.csv")
    assert all(raw[r["rel_path"]] == r["sha256"] for r in rows)
    for q in lc.PRODUCTION:
        assert sorted(r["item_id"] for r in rows if r["arm"] == q) == sorted(_ids(L1 / "ids" / f"{q}_ids.txt"))
    assert sha256_file(L1 / "litcorpus01_manifest.csv") == m["manifest"]["production_csv_sha256"]


def test_litcorpus01_collision_evidence_and_roles():
    m = _json(L1 / "litcorpus01_manifest.json")
    c = m["fwi_collision_evidence"]
    assert len(c["documents"]) == 10 and c["in_fire_weather_v1_arm"] == ["232342359", "257970033"]
    roles = {q: v["role"] for q, v in m["queries"].items()}
    assert sum(r.startswith("production") for r in roles.values()) == 2
    assert sum(r.startswith("collection sensitivity diagnostic") for r in roles.values()) == 2
    assert sum(r == "unused / not executed as corpus-defining query" for r in roles.values()) == 2
    assert m["rfwi1_retroactive"]["status"].startswith("pending")
    assert m["metadata"] == {"year": "unknown", "venue": "unknown", "authors": "unknown"}


# --- LITCORPUS-02 ----------------------------------------------------------------------


def test_litcorpus02_yields_as_frozen():
    m = _json(L2 / "litcorpus02_manifest.json")
    y = m["yields"]
    assert (y["fire_weather_v1"]["raw_count"], y["fire_weather_v1"]["admitted_count"],
            y["fire_weather_v1"]["excluded_by_rfwi1"]) == (495, 448, 47)
    assert (y["extreme_heat_v1"]["raw_count"], y["extreme_heat_v1"]["admitted_count"]) == (861, 861)
    assert (y["fire_weather_diag_topical_only"]["raw_count"], y["fire_weather_diag_topical_only"]["admitted_count"]) == (548, 473)
    assert y["extreme_heat_diag_topical_only"]["admitted_count"] == 1082
    s = m["source"]
    assert (s["files"], s["unpacked_bytes"], s["directories"]) == (186346, 7651208072, 100)
    assert s["zip_sha256"] == "516baf87049eda6b117f230e23ec52a016301ce482fc4edcd3581a6897baaa94"
    i = m["index"]
    assert (i["parse_failures"], i["section_rows"], i["distinct_sha256"]) == (0, 1658731, 184268)
    assert i["exact_byte_redundant_copies_in_source"] == 2078
    assert m["queries_byte_identical_to_litcorpus01"] is True
    assert m["metadata"] == {"year": "unknown", "venue": "unknown", "authors": "unknown"}


def test_arm_manifests_lit2_ids_and_hashes():
    m = _json(L2 / "litcorpus02_manifest.json")
    arms = {q: _csv(L2 / f"{q}_manifest.csv") for q in lc.PRODUCTION}
    for q, rows in arms.items():
        assert [r["item_id"] for r in rows] == _ids(E / "runs" / q / "ids.txt")
        assert list(rows[0]) == ["item_id", "lit2_id", "arm", "rel_path", "sha256"]
        assert sha256_file(L2 / f"{q}_manifest.csv") == m["manifests"][f"{q}_manifest.csv"]
    union = _csv(L2 / "lit2_ids.csv")
    assert len(union) == 448 + 861 - 1 == m["stable_ids"]["n"]
    assert [r["item_id"] for r in union] == sorted(r["item_id"] for r in union)          # code-point order
    assert [r["lit2_id"] for r in union] == [f"LIT2-{i:06d}" for i in range(1, len(union) + 1)]
    lit2 = {r["item_id"]: r["lit2_id"] for r in union}
    assert all(r["lit2_id"] == lit2[r["item_id"]] for rows in arms.values() for r in rows)


def test_overlaps_duplicates_and_legacy():
    o = _json(L2 / "overlaps.json")
    assert [x["item_id"] for x in o["cross_arm_overlap"]] == ["270275181"]
    assert o["redundant_copies"] == {"fire_weather_v1": 5, "extreme_heat_v1": 5, "union": 10}
    assert o["litcorpus00_in_source"] == {"present": 1918, "of": 1918}
    lo = o["litcorpus00_overlap"]
    assert [x["litcorpus00_item_id"] for x in lo["fire_weather_v1"]] == ["LIT-000166", "LIT-000519", "LIT-000792", "LIT-001815"]
    assert len(lo["extreme_heat_v1"]) == 10
    assert all(x["sha256_equal_to_litcorpus00"] for v in lo.values() for x in v)
    legacy = {r["item_id"]: r for r in _csv(lc.LEGACY_MANIFEST_CSV)}
    assert all(legacy[x["litcorpus00_item_id"]]["basename"] == f"{x['item_id']}.json" for v in lo.values() for x in v)
    assert o["context_clause_removes"] == {"fire_weather_v1": 53, "extreme_heat_v1": 221}
    assert o["production_within_diagnostic"] == {"fire_weather_v1": 448, "extreme_heat_v1": 861}


def test_rfwi1_evidence_supports_every_decision():
    rows = _csv(L2 / "rfwi1_fire_weather_v1.csv")
    assert len(rows) == 495
    admitted = {r["item_id"] for r in rows if r["admitted"] == "1"}
    assert admitted == set(_ids(E / "runs" / "fire_weather_v1" / "ids.txt"))
    for r in rows:
        if r["rfwi1_basis"] == "bare_fwi_with_same_document_disambiguator":
            assert r["bare_term"] == "fwi" and r["disambiguator_term"] in ("fire weather", "fire-weather")
            assert r["bare_char_start"] and r["disambiguator_char_start"] and not r["direct_term"]
        elif r["rfwi1_basis"] == "direct_topical_term":
            assert r["direct_term"] and r["direct_term"] != "fwi"
        else:
            assert r["admitted"] == "0" and r["disambiguator_found"] == "0"
    counts = {}
    for r in rows:
        counts[r["rfwi1_basis"]] = counts.get(r["rfwi1_basis"], 0) + 1
    assert counts == {"direct_topical_term": 444, "bare_fwi_with_same_document_disambiguator": 4,
                      "bare_fwi_without_disambiguator": 47}


# --- place candidates ------------------------------------------------------------------


def test_place_candidates_are_the_frozen_intersections():
    p = _json(PL / "place_candidates.json")
    places = set(_ids(PL / "ids.txt"))
    assert p["source_documents_matched"] == len(places) == 16457
    want = {"fire_weather_v1": (100, {"oklahoma": 3, "stephens": 10, "california": 96}),
            "extreme_heat_v1": (143, {"oklahoma": 13, "stephens": 3, "california": 136})}
    first = _csv(PL / "first_hits.csv")
    for q, (n, per_term) in want.items():
        cands = _ids(PL / f"{q}_place_candidates.txt")
        assert cands == sorted(set(_ids(E / "runs" / q / "ids.txt")) & places)
        assert (p["arms"][q]["candidates"], p["arms"][q]["per_term"]) == (n, per_term)
        assert {(r["item_id"], r["term"]) for r in first if r["arm"] == q} == {
            (r["item_id"], r["term"]) for r in _csv(PL / "candidate_hits.csv") if r["arm"] == q}
    assert p["statement"] == lc.PLACE_STATEMENT and p["frozen_before_reading"] is True
    assert p["query_text"] == "( oklahoma OR stephens OR california )"


# --- data/manifest.json ----------------------------------------------------------------


def test_external_corpora_entries_pin_the_frozen_manifests():
    data = _json(REPO_ROOT / "data" / "manifest.json")
    by = {c["corpus_id"]: c for c in data["external_corpora"]}
    assert {"LITCORPUS-00", lc.L1_ID, lc.L2_ID} <= set(by)
    assert by["LITCORPUS-00"]["inventory_manifest_sha256"] == "3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a"
    e1, e2 = by[lc.L1_ID], by[lc.L2_ID]
    assert sha256_file(REPO_ROOT / e1["manifest_path"]) == e1["manifest_sha256"]
    assert sha256_file(REPO_ROOT / e1["summary_path"]) == e1["summary_sha256"]
    assert sha256_file(REPO_ROOT / e2["summary_path"]) == e2["summary_sha256"]
    for path, digest in e2["arm_manifests"].items():
        assert sha256_file(REPO_ROOT / path) == digest
    assert e1["tracked_in_git"] is False and e2["tracked_in_git"] is False


def test_git_never_rewrites_the_frozen_records():
    """`* text=auto` in .gitattributes outranks `*.csv -text`; the CRLF evidence CSVs need an explicit `-text`."""
    import subprocess
    probes = [E / "runs" / "fire_weather_v1" / "hits.csv", L1 / "litcorpus01_manifest.csv", PL / "first_hits.csv"]
    out = subprocess.run(["git", "check-attr", "text", "--", *map(str, probes)], cwd=REPO_ROOT,
                         capture_output=True, text=True, check=True).stdout
    assert out.count(": text: unset") == len(probes), out
