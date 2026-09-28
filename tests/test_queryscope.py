"""Query-scope coverage: three categories emitted, a fourth defined and unreachable."""

from __future__ import annotations

import json

import pytest

from climrr import litquery, queryscope
from climrr.paths import REPO_ROOT

SMALL = '(("heat index" OR "Fire Weather") OR (flood)) AND (climate)'


@pytest.fixture(scope="module")
def small():
    return litquery.extract_structure(SMALL)


def test_exact_normalized_and_absent(small):
    assert queryscope.classify("heat index", small)["classification"] == queryscope.EXACT
    assert queryscope.classify("heat index", small)["matched_term_ids"] == ["HG-01.T01"]
    # differs only in case and spacing from a query term
    assert queryscope.classify("fire  weather", small)["classification"] == queryscope.NORMALIZED
    assert queryscope.classify("Heat Index", small)["classification"] == queryscope.NORMALIZED
    assert queryscope.classify("fire weather index", small)["classification"] == queryscope.ABSENT


def test_whole_string_only_no_substring_matching(small):
    assert queryscope.classify("Heat Index – Summer", small)["classification"] == queryscope.ABSENT
    assert queryscope.classify("flooding", small)["classification"] == queryscope.ABSENT


def test_the_inferred_category_is_defined_but_cannot_be_emitted(small):
    assert queryscope.INFERRED in queryscope.CATEGORIES
    assert queryscope.INFERRED not in queryscope.EMITTABLE
    for probe in ["heat index", "fire weather", "humid heat", "FWI", "hot days", "", "HEAT INDEX"]:
        assert queryscope.classify(probe, small)["classification"] in queryscope.EMITTABLE
    import ast
    import inspect
    import textwrap

    body = ast.parse(textwrap.dedent(inspect.getsource(queryscope.classify))).body[0].body[1:]
    names = {n.id for stmt in body for n in ast.walk(stmt) if isinstance(n, ast.Name)}
    consts = {n.value for stmt in body for n in ast.walk(stmt) if isinstance(n, ast.Constant)}
    assert "INFERRED" not in names and queryscope.INFERRED not in consts


def test_groups_without_a_pilot_counterpart(small):
    probes = [{"record_id": "P-X", "path": None, "concept_terms": ["heat index"]}]
    cov = queryscope.coverage(small, probes, [])
    assert [g["has_pilot_counterpart"] for g in cov["hazard_groups"]] == [True, False]


def test_the_real_pilot_inputs_are_found():
    probes = queryscope.load_probe_terms(REPO_ROOT / "artifacts" / "phenomena" / "prototypes")
    families = queryscope.load_pilot_families(REPO_ROOT / "docs" / "PILOT_SUBSET.md")
    assert [p["record_id"] for p in probes] == ["P-CELL-1", "P-COUNTY-1", "P-STATE-1"]
    assert [f["name"] for f in families] == [
        "Heat Index – Summer",
        "Fire Weather Index - Averages",
        "Location anchor",
        "Stem-assumption probe",
    ]


def test_the_tracked_coverage_artifact_matches_a_fresh_computation():
    query = REPO_ROOT / "data" / "metadata" / "literature_query.txt"
    structure = litquery.extract_structure(query.read_bytes().decode("utf-8"))
    probes = queryscope.load_probe_terms(REPO_ROOT / "artifacts" / "phenomena" / "prototypes")
    families = queryscope.load_pilot_families(REPO_ROOT / "docs" / "PILOT_SUBSET.md")
    fresh = queryscope.coverage(structure, probes, families)
    tracked = json.loads(
        (REPO_ROOT / "artifacts" / "literature" / "query_scope_coverage.json").read_text(encoding="utf-8")
    )
    assert tracked["coverage"] == fresh
    for proto in fresh["per_prototype"]:
        assert proto["counts"] == {queryscope.EXACT: 1, queryscope.NORMALIZED: 0, queryscope.ABSENT: 3}
    assert fresh["family_counts"][queryscope.ABSENT] == 4
    assert sum(not g["has_pilot_counterpart"] for g in fresh["hazard_groups"]) == 9


def test_the_scope_document_carries_the_ruling_sentence_verbatim():
    text = (REPO_ROOT / "docs" / "LITERATURE_QUERY_SCOPE.md").read_text(encoding="utf-8")
    assert (
        "The Boolean query explains how the candidate corpus was collected. It does not "
        "establish what any paper contains or which prototype a paper supports."
    ) in text
    assert "corpus coverage" in text  # named only to say this is not it
    assert "query-scope coverage" in text
