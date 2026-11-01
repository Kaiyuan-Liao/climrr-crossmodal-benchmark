"""Item seeds --- `src/climrr/itemseeds.py`, DR-SEED-1 (pilot P2a Phase C; D-045); review workbook and doc (Phases D, F).

Pairing rules on synthetic clusters and patterns; then the full seeds, rebuilt from the
pinned table patterns and the tracked clusters, must hash to the pin in the summary (the
seeds file and the patterns file are gitignored: absent, the test fails unless
`CLIMRR_ALLOW_MISSING_RAW=1`). The SEEDS CSV and `docs/LITSTATEMENTS_RUN2.md` must equal a
re-render; the stdlib xlsx writer must write a valid, deterministic workbook.
"""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from xml.dom import minidom

import pytest

from climrr import itemseeds as sd
from climrr import litaggregate as la
from climrr import p2a_review as rv
from climrr.checksums import sha256_file
from climrr.xlsxlite import write_xlsx

SUMMARY = json.loads(sd.SUMMARY_PATH.read_text(encoding="utf-8"))
NCA = sd.nca_map()


def _cluster(cid, *, arm="extreme_heat_v1", stype="driver", direction="increase", strength="multi_source_supported",
             regions=(("unknown", "unknown"),), n_ind=2, n=2, scenarios=()):
    return {"cluster_id": cid, "arm": arm, "statement_type": stype, "direction": direction, "evidence_strength": strength,
            "n_independent_papers": n_ind, "n_statements": n, "scenarios_named": list(scenarios),
            "multi_source_relies_on_diagnostic_pair": False,
            "members": [{"region": r, "region_scope": s} for r, s in regions]}


def _pattern(pid="TP1-99999", *, family="heat_index", gt="state", geo="Florida", direction="increase", kind="single",
             blocked=False, status="computed"):
    return {"pattern_id": pid, "pattern_kind": kind, "family": family, "metric": "m", "geography_type": gt, "geography": geo,
            "season": "summer", "horizon": "mid", "horizon_window": "2045-2054", "scenario": "RCP8.5", "statistic": "direction",
            "direction": direction, "status": status, "acceptance_blocked": blocked,
            "acceptance_blocked_by": ["IC-006"] if blocked else [],
            "provisional_reasons": ["location_inferred_candidate: State label IC-012 (A-G1, A-G3; D-034)"],
            "computed_value_or_range": {"value": "1", "unit": "days"}}


@pytest.mark.parametrize("region,scope,places,expected", [
    ("Florida", "subnational", {"state": ["Florida"], "nca_region": ["Southeast"]}, ("geography_relevant", "state:Florida")),
    ("Southeast United States", "subnational", {"state": ["Florida"], "nca_region": ["Southeast"]},
     ("geography_relevant", "nca_region:Southeast")),
    ("Western U.S.", "subnational", {"state": [], "nca_region": []}, ("geography_relevant", "us_term:us")),
    ("CONUS", "continental", {"state": [], "nca_region": []}, ("geography_relevant", "us_term:conus")),
    ("Greece", "national", {"state": ["Florida"], "nca_region": []}, ("geography_relevant", "scope:national")),
    ("Greece", "subnational", {"state": ["Florida"], "nca_region": []}, ("geography_other", None)),
    ("southeastern Brazil", "subnational", {"state": [], "nca_region": ["Southeast"]}, ("geography_other", None)),
    ("Campus grounds", "local", {"state": [], "nca_region": []}, ("geography_other", None)),   # "us" only as a whole word
])
def test_geography_match(region, scope, places, expected):
    assert sd.geography_match(_cluster("c", regions=((region, scope),)), places) == expected


def test_places_for_each_pattern_kind():
    assert sd.pattern_places(_pattern(), NCA) == {"state": ["Florida"], "nca_region": ["Southeast"]}
    assert sd.pattern_places(_pattern(gt="nca_region", geo="NCA5-SW"), NCA) == {"state": [], "nca_region": ["Southwest"]}
    assert sd.pattern_places(_pattern(gt="cell_control", geo="R106C361"), NCA) == {"state": [], "nca_region": []}
    rc = _pattern(gt="nca_region", geo="all_covered_nca5_regions", kind="regional_contrast")
    rc["computed_value_or_range"] = {"regions_ordered": [{"name": "Alaska"}, {"name": "Midwest"}]}
    assert sd.pattern_places(rc, NCA) == {"state": [], "nca_region": ["Alaska", "Midwest"]}


def test_pairing_family_direction_rank_and_eligibility():
    clusters = [_cluster("LC-a", regions=(("Greece", "subnational"),)),                        # multi, other
                _cluster("LC-b", direction="unspecified", regions=(("Florida", "local"),)),     # multi, relevant
                _cluster("LC-c", direction="decrease", regions=(("Florida", "local"),)),        # wrong direction
                _cluster("LC-d", arm="fire_weather_v1"),                                        # wrong family
                _cluster("LC-e", stype="caveat", strength="single_source_supported", scenarios=("RCP8.5",), n_ind=1, n=1),
                _cluster("LC-f", stype="mechanism", strength="review_supported", n_ind=1, n=1)]
    (s,) = sd.build([_pattern()], clusters, NCA)
    assert [r["cluster_id"] for r in s["clusters"]] == ["LC-b", "LC-a", "LC-f", "LC-e"]
    assert s["paired_cluster_ids"] == ["LC-b", "LC-a", "LC-f", "LC-e"] and s["eligible_clusters"] == ["LC-b"]
    assert s["eligible_for_pilot"] and s["use_case_levels_applicable"] == [3, 7] and s["use_case_level"] == 3
    assert [b["blocker"] for b in s["acceptance_blockers"]] == ["IC-012"]


def test_a_mixed_pattern_pairs_only_with_unspecified_clusters():
    clusters = [_cluster("LC-i"), _cluster("LC-u", direction="unspecified")]
    (s,) = sd.build([_pattern(direction="mixed")], clusters, NCA)
    assert s["paired_cluster_ids"] == ["LC-u"]


def test_blocked_and_not_computable_patterns_are_not_eligible():
    clusters = [_cluster("LC-b", regions=(("Florida", "local"),))]
    blocked, nc = sd.build([_pattern("TP1-1", blocked=True), _pattern("TP1-2", status="not_computable")], clusters, NCA)
    assert not blocked["eligible_for_pilot"] and blocked["acceptance_blockers"][0] == \
        {"blocker": "IC-006", "kind": "inferred_candidate_fwi_column", "blocks_eligibility": True}
    assert not nc["eligible_for_pilot"] and nc["eligible_clusters"] == ["LC-b"]


def test_levels():
    rc = _pattern(kind="regional_contrast")
    assert sd.levels(rc, [_cluster("x", stype="pattern")]) == [4]
    assert sd.levels(_pattern(), []) == [1]
    assert sd.levels(_pattern(), [_cluster("x", stype="caveat", scenarios=("RCP8.5",))]) == [7]
    assert sd.levels(_pattern(), [_cluster("x", stype="caveat")]) == [1]


# --- the full seeds ------------------------------------------------------------------------------------


def _need(path, what):
    if not path.is_file():
        if os.environ.get("CLIMRR_ALLOW_MISSING_RAW") == "1":
            pytest.skip(f"{what} absent and CLIMRR_ALLOW_MISSING_RAW=1 is set")
        pytest.fail(f"{what} is absent (gitignored); regenerate it, or set CLIMRR_ALLOW_MISSING_RAW=1 for code-only work")


@pytest.fixture(scope="module")
def seeds():
    _need(sd.PATTERNS_PATH, "artifacts/benchmark/table_patterns_v1.jsonl")
    assert sha256_file(sd.PATTERNS_PATH) == sd.PATTERNS_SHA256
    clusters = sd.read_jsonl(la.CLUSTERS_PATH)
    return sd.build(sd.read_jsonl(sd.PATTERNS_PATH), clusters, NCA), clusters


def test_full_seeds_rebuild_to_the_pin(seeds):
    built, clusters = seeds
    h = hashlib.sha256()
    for s in built:
        h.update((json.dumps(s, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
    assert h.hexdigest() == SUMMARY["seeds_file"]["sha256"]
    if sd.SEEDS_PATH.is_file():  # the summary hashes the file on disk
        assert sha256_file(sd.SEEDS_PATH) == SUMMARY["seeds_file"]["sha256"]
        assert json.loads(json.dumps(sd.summarise(built, clusters, NCA))) == SUMMARY


def test_summary_counts(seeds):
    built, _ = seeds
    elig = [s for s in built if s["eligible_for_pilot"]]
    assert (len(built), len(elig)) == (SUMMARY["seeds"], SUMMARY["eligible"]) == (2812, 1316)
    assert SUMMARY["eligible_without_diagnostic_pair"] == 24
    assert SUMMARY["fwi"] == {"seeds": 1404, "acceptance_blocked": 352, "not_blocked": 1052, "eligible": 0}
    assert all(not s["acceptance_blocked"] and s["pattern_computed"] for s in elig)
    assert all(s["seed_id"] == f"SD1-{s['pattern']['pattern_id']}" for s in built)
    assert sorted(s["seed_rank_key"] for s in built) == list(range(1, len(built) + 1))
    assert [t["seed_id"] for t in SUMMARY["top_eligible"]] == \
        [s["seed_id"] for s in sorted(elig, key=lambda s: s["seed_rank_key"])[:10]]


def test_seeds_csv_is_the_seeds_sheet(seeds):
    built, clusters = seeds
    rows = rv.seed_rows(built, {c["cluster_id"]: c for c in clusters})
    assert rv.SEEDS_CSV_PATH.read_text(encoding="utf-8") == rv.seeds_csv(rows)
    assert len(rows) - 1 == SUMMARY["eligible"] and rows[0][:3] == ["seed_rank", "seed_id", "use_case_level"]


def test_generated_doc_is_current():
    assert rv.DOC_PATH.read_text(encoding="utf-8") == rv.render_doc(*rv.doc_inputs())


def test_xlsx_writer_is_valid_and_deterministic(tmp_path):
    sheets = [("A", [["h1", "h2"], ["x & <y>", 3], [None, True]], [10, 20]), ("B", [["only"]], None)]
    a, b = tmp_path / "a.xlsx", tmp_path / "b.xlsx"
    write_xlsx(a, sheets)
    write_xlsx(b, sheets)
    assert a.read_bytes() == b.read_bytes()
    with zipfile.ZipFile(a) as z:
        assert z.testzip() is None
        for n in z.namelist():
            minidom.parseString(z.read(n))
        sheet = z.read("xl/worksheets/sheet1.xml").decode()
        assert "x &amp; &lt;y&gt;" in sheet and "<v>3</v>" in sheet and 'state="frozen"' in sheet
        assert 'name="B"' in z.read("xl/workbook.xml").decode()
    with pytest.raises(ValueError):
        write_xlsx(tmp_path / "c.xlsx", [("S", [["a"]], None), ("S", [["b"]], None)])
