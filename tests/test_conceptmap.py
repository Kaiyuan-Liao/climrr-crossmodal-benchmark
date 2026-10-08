"""D-018: concept map validation, the boundary rule, and rule C-2."""

from __future__ import annotations

import copy
import json

import pytest
import yaml

from climrr import compat, conceptmap

DICT_LINES = conceptmap.DICTIONARY_TEXT_PATH.read_text(encoding="utf-8").splitlines()
RAW = yaml.safe_load(conceptmap.CONCEPT_MAP_PATH.read_text(encoding="utf-8"))
ENTRIES = conceptmap.load()


def _entry(cid):
    return next(e for e in RAW["entries"] if e["canonical_id"] == cid)


def test_the_tracked_map_validates_and_holds_only_the_four_seed_entries():
    by_id = {e["canonical_id"]: (e["level"], e["status"], e["accepted_surface_terms"]) for e in ENTRIES}
    assert by_id == {
        "fire_weather_index": ("family", "approved_lexical", ["fire weather index", "FWI"]),
        "heat_index": ("family", "approved_lexical", ["heat index"]),
        "fwi_seasonal_value": ("metric", "proposed", []),
        "heatindex_days_above_105F": ("metric", "proposed", []),
    }


def test_a_metric_with_surface_terms_needs_a_guidance_or_mentor_source():
    data = copy.deepcopy(RAW)
    m = next(e for e in data["entries"] if e["canonical_id"] == "heatindex_days_above_105F")
    m["accepted_surface_terms"] = ["days above 105 F"]
    with pytest.raises(conceptmap.ConceptMapError, match="guidance or mentor"):
        conceptmap.validate(data, DICT_LINES)
    m["source_type"] = "guidance"
    conceptmap.validate(data, DICT_LINES)  # allowed once GUIDANCE is the source


def test_a_family_term_must_be_on_a_cited_dictionary_line():
    data = copy.deepcopy(RAW)
    fam = next(e for e in data["entries"] if e["canonical_id"] == "heat_index")
    fam["accepted_surface_terms"].append("urban heat island")
    with pytest.raises(conceptmap.ConceptMapError, match="not on any cited dictionary line"):
        conceptmap.validate(data, DICT_LINES)


def test_a_term_cannot_belong_to_two_entries_and_approval_needs_an_approver():
    data = copy.deepcopy(RAW)
    data["entries"][1]["accepted_surface_terms"].append("FWI")
    with pytest.raises(conceptmap.ConceptMapError):
        conceptmap.validate(data, DICT_LINES)
    data = copy.deepcopy(RAW)
    data["entries"][0]["approved_by"] = "none"
    with pytest.raises(conceptmap.ConceptMapError, match="approved_by"):
        conceptmap.validate(data, DICT_LINES)


@pytest.mark.parametrize("text,term,spans", [
    ("the FWI rose", "FWI", [(4, 7)]),
    ("(FWI)", "FWI", [(1, 4)]),
    ("FWI-based, fwi.", "FWI", [(0, 3), (11, 14)]),
    ("FWIs", "FWI", []),               # trailing letter: not a match
    ("FWI2", "FWI", []),               # trailing digit: not a match
    ("xFWI", "FWI", []),
    ("FWÍ", "FWI", []),                # different code point
    ("FWÍ", "FWI", []),          # a combining mark modifies the last letter
    ("FWI_x", "FWI", [(0, 3)]),        # underscore is neither letter nor digit
    ("Heat Index", "heat index", [(0, 10)]),
    ("heat-index", "heat index", []),
    ("heat  index", "heat index", []),
    ("🌊California", "California", [(1, 11)]),  # code points, not UTF-16 units
    ("Californian", "California", []),
])
def test_the_boundary_rule(text, term, spans):
    assert conceptmap.find_term(term, text) == spans
    for s, e in spans:
        assert text[s:e].casefold() == term.casefold()


# --- C-2 ----------------------------------------------------------------------

PROTOS = {pid: json.loads(compat.prototype_file(pid).read_text(encoding="utf-8")) for pid in compat.PROTOTYPE_IDS}
GEO = compat.load_geo_list()


def _claim(concept, direction="increase"):
    d = lambda v: {"value": v, "status": "explicit"}  # noqa: E731
    return {"claim_id": "SYN", "claim_type": "projection", "claim_validation_status": "single_reader_provisional",
            "concept": d(concept), "relation_or_direction": d(direction), "geography": d("California"),
            "temporal_frame": d("2085-2094"), "scenario": d("RCP8.5")}


@pytest.mark.parametrize("concept,pid", [("Heat Index", "P-STATE-1"), ("fwi", "P-CELL-1"),
                                         ("fire  weather index", "P-COUNTY-1")])
def test_c2_gives_family_level_never_compatible_and_direction_stays_closed(concept, pid):
    row = compat.evaluate_pair(_claim(concept), PROTOS[pid], GEO, ENTRIES)
    j = row["judgments"]["concept"]
    assert (j["status"], j["rule_id"]) == (compat.FAMILY_LEVEL, "C-2")
    assert row["judgments"]["direction"]["status"] == "not_evaluable"
    assert not row["all_compatible"]


@pytest.mark.parametrize("concept", ["heat index trends", "extreme heat index days", "days above 105F",
                                     "urban heat island", "wildfire smoke", "drought"])
def test_c2_is_exact_membership_not_containment(concept):
    j = compat.evaluate_pair(_claim(concept), PROTOS["P-STATE-1"], GEO, ENTRIES)["judgments"]["concept"]
    assert j["status"] == "not_evaluable"


def test_a_family_term_of_another_family_is_not_evaluable():
    j = compat.evaluate_pair(_claim("FWI"), PROTOS["P-STATE-1"], GEO, ENTRIES)["judgments"]["concept"]
    assert (j["status"], j["rule_id"], j["reason"]) == ("not_evaluable", "C-2", "approved_term_of_another_family")


def test_without_a_concept_map_the_m5wp1_rules_are_unchanged():
    j = compat.evaluate_pair(_claim("heat index"), PROTOS["P-STATE-1"], GEO)["judgments"]["concept"]
    assert (j["status"], j["rule_id"]) == ("not_evaluable", "C-1")
    assert "C-2" not in compat.RULES and compat.FAMILY_LEVEL not in compat.STATUSES
