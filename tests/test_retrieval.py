"""R-FWI-1 v1 (D-022): bare `FWI` needs a same-document fire-weather disambiguator.

The five cases from the work package, plus same-document (not same-section)
semantics, auditable locations, and the guarantee that `concept_map.yaml` is
unchanged.
"""

from __future__ import annotations

import importlib.util
import re

import pytest

from climrr import retrieval as r
from climrr.checksums import sha256_file
from climrr.conceptmap import CONCEPT_MAP_PATH
from climrr.paths import REPO_ROOT

#: `data/metadata/concept_map.yaml` after D-025 (additional_surface_terms); was 6ec6b081... (D-018).
CONCEPT_MAP_SHA256 = "27f7a44deabf24c244f1222c28d17c5c43fd86b9c017d4634bf0eef00931d7b4"

RULING = REPO_ROOT / "docs" / "M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md"
FIRE_QUERY = REPO_ROOT / "artifacts" / "literature" / "litcorpus01" / "queries" / "fire_weather_v1_query.txt"


def _one(text: str) -> dict:
    return r.evaluate([("body", text)])


def test_bare_fwi_alone_is_not_admitted():
    d = _one("FWI increased over the period.")
    assert d["eligible"] is False and d["basis"] == r.BASIS_BARE_ONLY
    assert d["bare_term_hit"]["matched_text"] == "FWI" and d["disambiguator_hit"] is None


def test_fire_weather_index_spelled_out_is_admitted():
    d = _one("The Fire Weather Index (FWI) rises.")
    assert d["eligible"] is True and d["basis"] == r.BASIS_DIRECT
    assert d["direct_term_hit"]["matched_text"] == "Fire Weather Index"


def test_canadian_fwi_is_a_longer_term_and_directly_eligible():
    d = _one("Canadian FWI values were computed.")
    assert d["eligible"] is True and d["basis"] == r.BASIS_DIRECT
    assert d["direct_term_hit"]["term"] == "canadian fwi"


def test_full_waveform_inversion_is_not_admitted():
    d = _one("We apply full waveform inversion (FWI) to seismic data.")
    assert d["eligible"] is False and d["basis"] == r.BASIS_BARE_ONLY


def test_fwis_is_no_match():
    d = _one("Several FWIs were compared.")
    assert d["eligible"] is False and d["basis"] == r.BASIS_NONE
    assert d["bare_term_hit"] is None


def test_same_document_not_same_section_and_both_locations_recorded():
    secs = [("title", "Fire weather in a changing climate"), ("abstract", "x"), ("methods", "Daily FWI was taken.")]
    d = r.evaluate(secs)
    assert d["eligible"] is True and d["basis"] == r.BASIS_DISAMBIGUATED
    b, m = d["bare_term_hit"], d["disambiguator_hit"]
    assert (b["section_key"], b["section_idx"]) == ("methods", 2)
    assert (m["section_key"], m["section_idx"], m["term"]) == ("title", 0, "fire weather")
    for hit in (b, m):
        assert secs[hit["section_idx"]][1][hit["char_start"]:hit["char_end"]] == hit["matched_text"]


def test_hyphenated_disambiguator_counts_and_non_strings_are_ignored():
    d = r.evaluate(r.flat_sections({"a": "fire-weather conditions", "n": 3, "b": "FWI"}))
    assert d["eligible"] is True and d["disambiguator_hit"]["term"] == "fire-weather"


def test_offsets_are_code_points_on_the_unnormalized_string():
    text = "Résumé — Québec: Fire Weather Index"
    d = _one(text)
    h = d["direct_term_hit"]
    assert text[h["char_start"]:h["char_end"]] == "Fire Weather Index"
    assert h["char_start"] == text.index("Fire")


def test_the_rule_is_versioned_and_tied_to_its_decision():
    assert (r.RULE_ID, r.RULE_VERSION, r.DECISION_ID) == ("R-FWI-1", "v1", "D-022")
    assert all(x in r.RULE_TEXT for x in ("R-FWI-1 v1", "D-022", "Same-document"))


def test_disambiguators_are_exactly_the_rulings_list():
    text = RULING.read_text(encoding="utf-8")
    block = text.split("Approved disambiguators:", 1)[1].split("The longer terms", 1)[0]
    listed = re.findall(r"^- `([^`]+)`;?", block, re.MULTILINE)
    assert tuple(listed) == r.DISAMBIGUATORS


def test_topical_terms_are_the_frozen_query_group():
    pytest.importorskip("duckdb")  # run_query.py imports it; scripts/litcollect/requirements.txt
    spec = importlib.util.spec_from_file_location("rq", REPO_ROOT / "scripts" / "litcollect" / "run_query.py")
    rq = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rq)
    groups = rq.parse(FIRE_QUERY.read_text(encoding="utf-8"))
    assert tuple(groups[0]) == r.FIRE_WEATHER_TOPICAL_TERMS_V1


def test_concept_map_is_unchanged_and_fwi_stays_in_it():
    assert sha256_file(CONCEPT_MAP_PATH) == CONCEPT_MAP_SHA256
    from climrr import conceptmap
    fwi = next(e for e in conceptmap.load() if e["canonical_id"] == "fire_weather_index")
    assert fwi["accepted_surface_terms"] == ["fire weather index", "FWI"]
