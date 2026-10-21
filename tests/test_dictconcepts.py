"""Track B Stage 2a --- the dictionary concept inventory (D-025, D-026).

Every passage re-slices from its page; ids are unique and contiguous;
`family_hint` is always null; `verified_columns` stays inside the verified set;
the file is pinned in the manifest and rebuilds byte for byte; and no column
status moves.
"""

from __future__ import annotations

import json
import re

import pytest
import yaml

from climrr import dictconcepts as dc
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

PDF = REPO_ROOT / "data" / "metadata" / "ClimRR_Metadata_and_Data_Dictionary.pdf"
INV = REPO_ROOT / "data" / "metadata" / "dictionary_concepts.yaml"
DOC = REPO_ROOT / "docs" / "DICTIONARY_CONCEPTS.md"
MANIFEST = REPO_ROOT / "data" / "manifest.json"
COVERAGE = REPO_ROOT / "artifacts" / "profiles" / "dictionary_coverage.json"
RESOLUTIONS = REPO_ROOT / "data" / "metadata" / "resolutions.yaml"


@pytest.fixture(scope="module")
def inv():
    return yaml.safe_load(INV.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def pages():
    pytest.importorskip("pypdf")
    return dc.extract_pages(PDF)


def test_header_records_source_and_extractor(inv):
    import pypdf

    assert inv["source_pdf_sha256"] == sha256_file(PDF)
    assert inv["extractor"] == f"pypdf {pypdf.__version__}" == "pypdf 6.18.0"
    assert inv["statement"] == dc.STATEMENT


def test_page_texts_are_the_ones_the_spans_index(inv, pages):
    assert inv["page_text_sha256"]
    for page, digest in inv["page_text_sha256"].items():
        assert dc.sha256_text(pages[page - 1]) == digest, page


def test_every_passage_reslices_from_its_page(inv, pages):
    for c in inv["concepts"]:
        if c["status"] == "listed_only":
            assert c["passage"] is None and c["char_span"] is None
            continue
        s, e = c["char_span"]
        assert 0 <= s < e <= len(pages[c["page"] - 1])
        assert pages[c["page"] - 1][s:e] == c["passage"], c["id"]


def test_every_name_reslices_from_its_page(inv, pages):
    for c in inv["concepts"]:
        s, e = c["name_source"]["char_span"]
        assert pages[c["name_source"]["page"] - 1][s:e] == c["name"], c["id"]


def test_units_threshold_and_scenario_are_verbatim_from_passage_or_name(inv):
    for c in inv["concepts"]:
        for key in ("units", "metric_or_threshold", "scenario_or_horizon"):
            v = c[key]
            if v is not None:
                assert v in (c["passage"] or "") or v in c["name"], (c["id"], key)


def test_ids_unique_contiguous_and_in_order(inv):
    ids = [c["id"] for c in inv["concepts"]]
    assert ids == [f"DC-{n:03d}" for n in range(1, len(ids) + 1)]


def test_family_hint_is_always_null(inv):
    assert all(c["family_hint"] is None for c in inv["concepts"])


def test_status_vocabulary(inv):
    for c in inv["concepts"]:
        assert c["status"] in ("dictionary_described", "listed_only")
        assert (c["passage"] is None) is (c["status"] == "listed_only")


def test_verified_columns_are_a_subset_of_the_verified_set(inv):
    verified = {
        c["index"] for c in json.loads(COVERAGE.read_text(encoding="utf-8"))["columns"]
        if c["status"] == "verified_from_dictionary"
    }
    assert len(verified) == 21
    for c in inv["concepts"]:
        assert set(c["verified_columns"]) <= verified


def test_verified_columns_rule_needs_a_citing_resolution_record():
    # No verified column references a resolution record today, so nothing qualifies ...
    assert all(not texts for texts in dc.load_verified(COVERAGE, RESOLUTIONS).values())
    # ... and the rule admits a column only when a record it references quotes the passage.
    passage = "Summer seasonal max\nheat index"
    assert dc.verified_columns_for(passage, {240: ["quotes Summer seasonal max heat index here"], 241: ["other"]}) == [240]
    assert dc.verified_columns_for(passage, {240: []}) == []


def test_measure_level_inventory_is_the_expected_fourteen(inv):
    """D-026: the narrative's output quantities, heat index split per its own enumeration."""
    names = [c["name"] for c in inv["concepts"]]
    assert names[:10] == [
        "Temperature (Annual)", "Temperature (Seasonal)", "Precipitation", "Wind Speed",
        "Consecutive Days with No Precipitation", "Degree Days (HDD/CDD)", "Fire Weather Index",
        "Calculating FWI Classes", "Summer daily maximum heat index", "Summer seasonal maximum heat index",
    ]
    assert [c["metric_or_threshold"] for c in inv["concepts"][10:]] == [
        "above 95 F", "above 105 F", "above 115 F", "above 125 F",
    ]
    assert sum(c["status"] == "listed_only" for c in inv["concepts"]) == 0


def test_no_csv_column_name_is_read():
    """The rules read the PDF only: no CSV header, coverage stem or column name appears in them."""
    src = (REPO_ROOT / "src" / "climrr" / "dictconcepts.py").read_text(encoding="utf-8")
    assert "FullData" not in src and "heatindex_" not in src and "wildfire_" not in src


def test_rebuild_is_byte_identical(inv, pages):
    concepts = dc.build_concepts(pages, dc.load_verified(COVERAGE, RESOLUTIONS))
    header = {k: v for k, v in inv.items() if k != "concepts"}
    assert dc.render_yaml(concepts, header=header) == INV.read_text(encoding="utf-8")


def test_inventory_and_clause_are_pinned_in_the_manifest():
    files = {f["path"]: f for f in json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]}
    for rel in ("data/metadata/dictionary_concepts.yaml", "data/metadata/litcollect/survey_context_clause_v1.txt"):
        assert files[rel]["sha256"] == sha256_file(REPO_ROOT / rel), rel
        assert files[rel]["bytes"] == (REPO_ROOT / rel).stat().st_size


def test_generated_doc_matches_the_inventory(inv):
    text = DOC.read_text(encoding="utf-8")
    assert dc.STATEMENT in text
    assert f"`{sha256_file(INV)}`" in text
    assert re.search(rf"\| Concepts \| \*\*{len(inv['concepts'])}\*\* \|", text)


def test_column_statuses_and_index_117_unchanged():
    """Stage 2a moves no status (criterion 24) and leaves index 117 unlabeled (criterion 25)."""
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    assert cov["status_counts"] == {
        "structurally_observed_only": 76, "verified_from_dictionary": 21,
        "inferred_candidate": 20, "partially_resolved": 130, "unresolved": 28,
    }
    inv_text = INV.read_text(encoding="utf-8")
    assert "117" not in re.sub(r"index 117 remains unlabeled", "", inv_text)
