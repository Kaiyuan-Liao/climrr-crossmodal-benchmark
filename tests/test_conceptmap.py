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
                                         ("fire weather index", "P-COUNTY-1")])
def test_c2_gives_family_level_never_compatible_and_direction_stays_closed(concept, pid):
    row = compat.evaluate_pair(_claim(concept), PROTOS[pid], GEO, ENTRIES)
    j = row["judgments"]["concept"]
    assert (j["status"], j["rule_id"]) == (compat.FAMILY_LEVEL, "C-2")
    assert row["judgments"]["direction"]["status"] == "not_evaluable"
    assert not row["all_compatible"]


@pytest.mark.parametrize("concept,term,span", [("heat index trends", "heat index", (0, 10)),
                                               ("extreme heat index days", "heat index", (8, 18)),
                                               ("trends in the (heat index)", "heat index", (15, 25))])
def test_revised_c2_matches_a_family_term_occurring_inside_the_concept_field(concept, term, span):
    """D-019: boundary-aware occurrence, recorded with family, term, span and decision id."""
    j = compat.evaluate_pair(_claim(concept), PROTOS["P-STATE-1"], GEO, ENTRIES)["judgments"]["concept"]
    assert (j["status"], j["rule_id"]) == (compat.FAMILY_LEVEL, "C-2")
    m = j["claim_value"]["family_match"]
    assert (m["family"], m["surface_term"], (m["char_start"], m["char_end"])) == ("heat_index", term, span)
    assert concept[m["char_start"]:m["char_end"]] == m["matched_text"]
    assert m["concept_map_decision_id"] == "D-018" and m["concept_map_entry"] == "heat_index"


@pytest.mark.parametrize("concept,pid", [("urban heat island", "P-STATE-1"), ("wildfire smoke exposure", "P-CELL-1"),
                                         ("wildfire smoke exposure", "P-COUNTY-1"), ("days above 105F", "P-STATE-1"),
                                         ("drought", "P-CELL-1"), ("heat-index trends", "P-STATE-1"),
                                         ("FWIs over time", "P-CELL-1"), ("FWI2", "P-COUNTY-1"),
                                         ("fire  weather index", "P-COUNTY-1")])
def test_revised_c2_does_not_match_without_an_approved_term_at_a_boundary(concept, pid):
    """No synonymy (UHI, smoke, drought), and the boundary rule holds ('FWIs', 'FWI2', 'heat-index'; internal
    whitespace is matched exactly, so a double space no longer matches as it did under exact-membership C-2)."""
    j = compat.evaluate_pair(_claim(concept), PROTOS[pid], GEO, ENTRIES)["judgments"]["concept"]
    assert j["status"] == "not_evaluable"
    assert "family_match" not in j["claim_value"]


def test_revised_c2_uses_the_frozen_retrieval_matcher(monkeypatch):
    """C-2 and the M4-WP2 scan call the same function, `climrr.conceptmap.find_term`."""
    from climrr import conceptmap, wp2retrieve
    assert wp2retrieve.conceptmap is conceptmap
    calls = []
    real = conceptmap.find_term
    monkeypatch.setattr(conceptmap, "find_term", lambda t, s: calls.append(t) or real(t, s))
    compat.family_term_hits("heat index trends", ENTRIES)
    assert set(calls) == {"fire weather index", "FWI", "heat index"}


def test_revised_c2_family_match_never_reaches_compatible_or_supporting_direction():
    row = compat.evaluate_pair(_claim("seasonal Fire Weather Index", "increase"), PROTOS["P-CELL-1"], GEO, ENTRIES)
    assert row["judgments"]["concept"]["status"] == compat.FAMILY_LEVEL
    assert row["judgments"]["direction"]["status"] == "not_evaluable"
    assert not row["all_compatible"]


def test_an_unresolved_claim_type_tie_makes_the_claim_type_rule_not_evaluable():
    pv = compat.prototype_values(PROTOS["P-CELL-1"])["time"]
    hist = {"value": "1990-2000", "status": "explicit"}
    assert compat.compare_time(hist, "finding", pv)["status"] == "incompatible"
    j = compat.compare_time(hist, compat.UNRESOLVED_TIE, pv)
    assert (j["status"], j["reason"]) == ("not_evaluable", "claim_type_unresolved_tie")


def test_a_family_term_of_another_family_is_not_evaluable():
    j = compat.evaluate_pair(_claim("FWI"), PROTOS["P-STATE-1"], GEO, ENTRIES)["judgments"]["concept"]
    assert (j["status"], j["rule_id"], j["reason"]) == ("not_evaluable", "C-2", "approved_term_of_another_family")


def test_without_a_concept_map_the_m5wp1_rules_are_unchanged():
    j = compat.evaluate_pair(_claim("heat index"), PROTOS["P-STATE-1"], GEO)["judgments"]["concept"]
    assert (j["status"], j["rule_id"]) == ("not_evaluable", "C-1")
    assert "C-2" not in compat.RULES and compat.FAMILY_LEVEL not in compat.STATUSES
