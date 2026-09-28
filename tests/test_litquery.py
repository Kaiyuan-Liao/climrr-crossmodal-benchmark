"""The collection-query parser: structure, offsets, round trip, absence rules.

The parser's whole value is that it is mechanical. These tests pin that it
reproduces the source, that every offset points at the text it claims to, that
anything outside its small grammar is refused with an offset rather than
guessed at, and that the absence rules report what they find.
"""

from __future__ import annotations

import json

import pytest

from climrr import litquery
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

QUERY = REPO_ROOT / "data" / "metadata" / "literature_query.txt"
PARSED = REPO_ROOT / "artifacts" / "literature" / "query_parsed.json"

SMALL = '(\n  ("heat wave" OR heatwave)\n  OR\n  (flood OR "flash flood")\n)\nAND\n(\n  climate OR "public health"\n)\n'


@pytest.fixture(scope="module")
def source() -> str:
    return QUERY.read_bytes().decode("utf-8")


@pytest.fixture(scope="module")
def structure(source) -> dict:
    return litquery.extract_structure(source)


# --- the real query ---------------------------------------------------------


def test_the_pinned_query_matches_its_manifest_entry():
    manifest = json.loads((REPO_ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))
    entry = next(f for f in manifest["files"] if f["filename"] == "literature_query.txt")
    assert sha256_file(QUERY) == entry["sha256"]
    assert QUERY.stat().st_size == entry["bytes"]
    for unknown in ("platform_or_database", "execution_date", "export_date", "folder_is_complete_result_set"):
        assert entry["provenance"][unknown] == "unknown"


def test_the_real_query_round_trips(source):
    assert litquery.round_trips(source)


def test_the_real_query_has_the_observed_shape(structure):
    # Eleven, not ten: the work package said ten; the parse is reported as found.
    assert len(structure["hazard_groups"]) == 11
    assert [g["n_terms"] for g in structure["hazard_groups"]] == [13, 10, 12, 6, 7, 4, 10, 8, 5, 2, 3]
    assert len(structure["context_terms"]) == 22
    assert structure["hazard_groups"][0]["terms"][0]["text"] == "extreme heat"
    assert structure["context_terms"][-1]["text"] == "sustainability"


def test_every_offset_points_at_its_text(source, structure):
    for term in litquery.all_terms(structure):
        start, end = term["text_offsets"]
        assert source[start:end] == term["text"]
        tstart, tend = term["lexeme_offsets"]
        lexeme = source[tstart:tend]
        assert lexeme == (f'"{term["text"]}"' if term["quoted"] else term["text"])
    for group in structure["hazard_groups"]:
        start, end = group["group_offsets"]
        assert source[start] == "(" and source[end - 1] == ")"


def test_normalized_forms_are_lower_case_single_spaced_and_keep_hyphens(structure):
    by_text = {t["text"]: t["normalized"] for t in litquery.all_terms(structure)}
    assert by_text["wet-bulb temperature"] == "wet-bulb temperature"
    assert by_text["CO2 fertilization"] == "co2 fertilization"
    assert litquery.normalize_term("  “Heat   Wave” ") == '"heat wave"'


def test_the_tracked_parse_is_current(source, structure):
    parsed = json.loads(PARSED.read_text(encoding="utf-8"))
    assert parsed["source_sha256"] == sha256_file(QUERY)
    assert parsed["hazard_groups"] == structure["hazard_groups"]
    assert parsed["context_terms"] == structure["context_terms"]
    assert parsed["round_trip"]["passed"] is True


def test_the_three_absence_rules_find_nothing_in_the_real_query(structure):
    results = litquery.absence_checks(structure)
    assert [r["rule_id"] for r in results] == [
        "AR-1-scenario-horizon",
        "AR-2-us-state",
        "AR-3-geographic-unit",
    ]
    for r in results:
        assert r["n_terms_checked"] == 102
        assert r["result"] == "absent" and r["hits"] == []


# --- the grammar, on small inputs --------------------------------------------


def test_a_small_query_round_trips_and_keeps_quoted_whitespace():
    assert litquery.round_trips(SMALL)
    s = litquery.extract_structure(SMALL)
    assert [t["text"] for t in s["hazard_groups"][0]["terms"]] == ["heat wave", "heatwave"]
    assert [t["quoted"] for t in s["hazard_groups"][0]["terms"]] == [True, False]


def test_round_trip_distinguishes_a_phrase_from_the_joined_word():
    assert litquery.strip_unquoted_whitespace('"heat wave" OR x') != litquery.strip_unquoted_whitespace("heatwave OR x")


@pytest.mark.parametrize(
    "text, offset",
    [
        ('(a OR "b', 6),  # unterminated quote
        ("(a OR b", 7),  # missing ")"
        ("a OR b AND c", 7),  # mixed operators, no parentheses
        ("a OR NOT b", 5),  # unsupported operator
        ("a OR b*", 6),  # wildcard
        ("a OR b)", 6),  # trailing text
    ],
)
def test_text_outside_the_grammar_is_refused_with_an_offset(text, offset):
    with pytest.raises(litquery.QueryParseError) as err:
        litquery.parse(text)
    assert err.value.offset == offset


def test_a_lower_case_operator_is_a_term_not_an_operator():
    # "or" is read as a bare term, so "a or b" is three terms with no operator
    # between them --- refused at the second one, never silently read as OR.
    assert [t.kind for t in litquery.lex("a or b")] == ["TERM", "TERM", "TERM"]
    with pytest.raises(litquery.QueryParseError) as err:
        litquery.parse("a or b")
    assert err.value.offset == 2


def test_a_different_top_level_shape_is_refused():
    with pytest.raises(litquery.QueryShapeError):
        litquery.extract_structure("(a OR b) OR (c OR d)")
    with pytest.raises(litquery.QueryShapeError):
        litquery.extract_structure("((a OR b) OR (c OR d)) AND ((e OR f) OR g)")


# --- absence rules ----------------------------------------------------------


@pytest.mark.parametrize(
    "term, rule",
    [
        ("RCP8.5 projection", "AR-1-scenario-horizon"),
        ("end-century heat", "AR-1-scenario-horizon"),
        ("heat in 2050", "AR-1-scenario-horizon"),
        ("california drought", "AR-2-us-state"),
        ("new york flooding", "AR-2-us-state"),
        ("TX heat", "AR-2-us-state"),
        ("county heat", "AR-3-geographic-unit"),
        ("USA drought", "AR-3-geographic-unit"),
        ("United States wildfire", "AR-3-geographic-unit"),
    ],
)
def test_each_absence_rule_fires_on_a_term_it_names(term, rule):
    s = litquery.extract_structure(f'(("{term}") OR (x)) AND (climate)')
    results = {r["rule_id"]: r for r in litquery.absence_checks(s)}
    assert results[rule]["result"] == "present"
    assert results[rule]["hits"][0]["text"] == term


def test_state_names_and_codes_match_whole_words_only():
    s = litquery.extract_structure('(("tornado" OR "inundation" OR "co2") OR (x)) AND (climate)')
    results = {r["rule_id"]: r for r in litquery.absence_checks(s)}
    # "co2" is not the word "co"; "inundation" does not contain the word "in".
    assert results["AR-2-us-state"]["result"] == "absent"
