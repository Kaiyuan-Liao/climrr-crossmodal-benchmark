"""NCA5 state -> region map v1 (pilot P1, D-041; GUIDANCE re-anchor ruling 3).

The map is immutable by hash: its SHA-256 is pinned in data/manifest.json, and a
change of bytes fails here. Membership is never edited to improve a pattern; a
corrected map is a new version.
"""

from __future__ import annotations

import json

from climrr import table_patterns as tp
from climrr import templates as td
from climrr.manifest import MANIFEST_PATH, load_entry

NCA = tp.load_nca_map()
TABLE_STATES = [v["label"] for v in td.load_yaml(td.SLOTS_PATH)["location"]["state"]["values"]]

STATES_AND_DC = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
    "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas",
    "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
    "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
}


def test_map_is_pinned_and_unchanged():
    entry = load_entry("nca_regions_v1.yaml", MANIFEST_PATH)
    assert entry["path"] == "data/metadata/geography/nca_regions_v1.yaml"
    assert td.file_sha256(tp.NCA_MAP_PATH) == entry["sha256"]
    assert tp.NCA_MAP_PATH.stat().st_size == entry["bytes"]


def test_required_metadata_present():
    for key in ("region_scheme_id", "region_scheme_name", "region_scheme_version", "source_citation",
                "state_to_region_map", "source_verification"):
        assert NCA.get(key), key
    assert NCA["region_scheme_id"] == "NCA5"
    assert NCA["source_verification"] in ("pending_kaiyuan", "verified_by_kaiyuan")
    assert NCA["source_citation"]["url"].startswith("https://")


def test_fifty_states_and_dc_each_in_exactly_one_known_region():
    mapping = NCA["state_to_region_map"]
    assert set(mapping) == STATES_AND_DC and len(mapping) == 51
    ids = {r["region_id"] for r in NCA["regions"]}
    assert set(mapping.values()) <= ids and len(ids) == 10


def test_every_table_state_maps_to_exactly_one_region():
    mapping = NCA["state_to_region_map"]
    assert len(TABLE_STATES) == 49
    assert all(s in mapping for s in TABLE_STATES)
    assert sorted(STATES_AND_DC - set(TABLE_STATES)) == ["District of Columbia", "Hawaii"]


def test_region_coverage_is_the_covered_states():
    regions = tp.region_members(NCA, TABLE_STATES)
    assert regions["NCA5-HI"]["covered"] == [] and regions["NCA5-CAR"]["members"] == []
    assert regions["NCA5-NE"]["uncovered"] == ["District of Columbia"]
    assert sum(len(r["covered"]) for r in regions.values()) == 49


def test_manifest_records_the_map_without_interpretation():
    entry = load_entry("nca_regions_v1.yaml", MANIFEST_PATH)
    assert "no interpretation assigned" in entry["interpretation_notes"]
    amendments = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["amendments"]
    assert any("nca_regions_v1.yaml" in a["change"] and a["decision_ref"] == "D-041" for a in amendments)
