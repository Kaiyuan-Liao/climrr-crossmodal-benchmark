"""M4-WP1: offsets, span integrity, record rules, and the prototype/query firewall.

The offset tests use synthetic strings with combining characters and astral-plane
characters, because those are exactly where code-point, UTF-16 and byte offsets
disagree. The record tests run on the tracked artifacts. The full re-slice
against the corpus runs only where the external corpus is configured.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

from climrr import litingest
from climrr.paths import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

LIT = REPO_ROOT / "artifacts" / "literature"
CLAIMS_DIR = LIT / "wp1_claims"
DIMENSIONS = ("concept", "relation_or_direction", "geography", "temporal_frame", "scenario")


def _records() -> list[dict]:
    sample = json.loads((LIT / "wp1_sample.json").read_text(encoding="utf-8"))
    return [json.loads((CLAIMS_DIR / f"{i}.json").read_text(encoding="utf-8")) for i in sample["item_ids"]]


# --- offsets ------------------------------------------------------------------


def test_offsets_are_code_points_on_the_unnormalized_string():
    # "Ishka" + U+0304 COMBINING MACRON + "shim", then an astral-plane character.
    value = "at Ishkāshim  and 🌊 Voss"
    doc = {"s": value}
    e = litingest.locate(doc, "$.s", "Ishkāshim")
    assert (e["char_start"], e["char_end"]) == (3, 13)  # the macron is its own code point
    litingest.check_span(doc, e)
    wave = litingest.locate(doc, "$.s", "🌊 Voss")
    assert value[wave["char_start"]:wave["char_end"]] == "🌊 Voss"
    assert wave["char_end"] - wave["char_start"] == 6  # one code point, not two UTF-16 units


def test_a_precomposed_letter_does_not_match_a_decomposed_source():
    doc = {"s": "Ishkāshim"}
    with pytest.raises(litingest.IntegrityError):
        litingest.locate(doc, "$.s", "Ishkāshim")


def test_no_normalization_happens_before_offsets():
    doc = {"s": "Two  spaces and CASE"}
    with pytest.raises(litingest.IntegrityError):
        litingest.locate(doc, "$.s", "two spaces")
    e = litingest.locate(doc, "$.s", "Two  spaces")
    assert (e["char_start"], e["char_end"]) == (0, 11)


def test_check_span_rejects_a_wrong_slice_and_a_wrong_hash():
    doc = {"s": "alpha beta gamma"}
    e = litingest.locate(doc, "$.s", "beta")
    with pytest.raises(litingest.IntegrityError):
        litingest.check_span(doc, {**e, "char_start": e["char_start"] + 1})
    with pytest.raises(litingest.IntegrityError):
        litingest.check_span(doc, {**e, "evidence_sha256": "0" * 64})


def test_paths_resolve_quoted_keys_and_indices():
    doc = {"a key's name": "x", "plain": ["y", {"deep": "z"}]}
    assert litingest.resolve(doc, litingest.child_path("$", "a key's name")) == "x"
    assert litingest.resolve(doc, "$.plain[1].deep") == "z"


def test_read_verified_fails_closed_and_reports_parse_failure(tmp_path):
    good = tmp_path / "g.json"
    good.write_bytes(b'{"title": "t"}')
    bad = tmp_path / "b.json"
    bad.write_bytes(b"{not json")
    from climrr.checksums import sha256_file

    with pytest.raises(litingest.IntegrityError):
        litingest.read_verified(good, "0" * 64)
    assert litingest.read_verified(good, sha256_file(good)) == ({"title": "t"}, None)
    doc, failure = litingest.read_verified(bad, sha256_file(bad))
    assert doc is None and failure.startswith("not valid JSON")


# --- the tracked records -----------------------------------------------------


def test_every_sampled_item_has_a_terminal_record_tied_to_the_manifest():
    sample = json.loads((LIT / "wp1_sample.json").read_text(encoding="utf-8"))
    from climrr.checksums import sha256_file

    sample_sha = sha256_file(LIT / "wp1_sample.json")
    records = _records()
    assert [r["item_id"] for r in records] == sample["item_ids"]
    for r in records:
        assert r["corpus_manifest_sha256"] == sample["corpus_manifest_sha256"]
        assert r["sample_sha256"] == sample_sha
        assert r["terminal_status"] in ("claims_extracted", "no_eligible_claim", "off_topic", "parse_failure", "ambiguous_only")


def test_terminal_status_agrees_with_scope_and_claim_count():
    for r in _records():
        n = len(r["claims"])
        expected = {
            ("in_scope_hazard", True): "claims_extracted",
            ("in_scope_hazard", False): "no_eligible_claim",
            ("off_topic", False): "off_topic",
            ("ambiguous", False): "ambiguous_only",
        }[(r["scope_status"], n > 0)]
        assert r["terminal_status"] == expected, r["item_id"]


def _blocks(r: dict) -> list[dict]:
    out = [r["scope_evidence"]] + [x["evidence"] for x in r["rejected_or_ambiguous"]]
    for c in r["claims"]:
        out.append(c["evidence"])
        out += [c[d]["support"] for d in DIMENSIONS if "support" in c[d]]
    out += [f["evidence"] for f in r["bibliographic"].values() if isinstance(f, dict) and "evidence" in f]
    return out


def test_every_span_is_internally_consistent():
    n = 0
    for r in _records():
        for b in _blocks(r):
            assert b["char_end"] - b["char_start"] == len(b["evidence_text"])
            assert b["evidence_sha256"] == hashlib.sha256(b["evidence_text"].encode("utf-8")).hexdigest()
            assert b["offset_convention"] == litingest.OFFSET_CONVENTION
            n += 1
    assert n == 96


def test_dimension_rules_hold_in_every_claim():
    for r in _records():
        for c in r["claims"]:
            assert len(c["claim_text"].split()) <= 40
            assert c["claim_type"] in ("finding", "projection", "mechanism", "recommendation", "background_citation")
            for d in DIMENSIONS:
                dim = c[d]
                assert dim["status"] in ("explicit", "inferred", "unknown")
                if dim["status"] == "unknown":
                    assert dim["value"] == "unknown" and "support" not in dim
                if dim["status"] == "inferred":
                    assert "support" in dim


def test_no_claim_is_labelled_against_a_prototype():
    banned = re.compile(r"support(s|ing)? the prototype|contradict|P-CELL|P-COUNTY|P-STATE|compatib", re.IGNORECASE)
    for r in _records():
        text = json.dumps(r, ensure_ascii=False)
        assert not banned.search(text), r["item_id"]


@pytest.mark.skipif(
    not (REPO_ROOT / "config" / "local_paths.yaml").is_file(),
    reason="external corpus not configured on this host",
)
def test_every_span_re_slices_from_the_verified_source():
    from climrr.paths import load_local_paths

    root = load_local_paths().get("literature_corpus_root")
    if not root or str(root).startswith("<") or not Path(root).is_dir():
        pytest.skip("literature_corpus_root not available on this host")
    sample = json.loads((LIT / "wp1_sample.json").read_text(encoding="utf-8"))
    by_id = {i["item_id"]: i for i in sample["items"]}
    for r in _records():
        item = by_id[r["item_id"]]
        doc, failure = litingest.read_verified(Path(root) / item["relative_path"], item["sha256"])
        assert failure is None
        for b in _blocks(r):
            litingest.check_span(doc, b)


# --- the firewall: WP1 reads no prototype and no query -------------------------


@pytest.mark.parametrize("path", [
    "scripts/build_wp1_claims.py",
    "scripts/wp1_extractions.py",
    "scripts/wp1_schema.py",
    "scripts/sample_corpus.py",
    "src/climrr/litingest.py",
    "src/climrr/litsample.py",
])
def test_wp1_code_reads_no_prototype_family_or_query(path):
    text = (REPO_ROOT / path).read_text(encoding="utf-8")
    for forbidden in ("phenomena/prototypes", "\"prototypes\"", "PILOT_SUBSET", "literature_query",
                      "query_parsed", "query_scope", "queryscope", "litquery", "import phenomenon"):
        assert forbidden not in text, (path, forbidden)


def test_the_schema_artifact_records_structure_only():
    schema = json.loads((LIT / "wp1_schema_observed.json").read_text(encoding="utf-8"))
    assert schema["n_parsed"] == 10 and schema["n_parse_failure"] == 0
    assert schema["top_level_value_types"] == {"string": 86}
    assert schema["majority_top_level_key_sequence"] is None
    assert schema["n_distinct_top_level_key_sequences"] == 10

    def walk(node):
        assert set(node) <= {"path", "type", "length_code_points", "keys", "children", "length",
                             "element_types", "object_element_keysets", "elements"}
        for child in node.get("children", []) + node.get("elements", []):
            walk(child)

    for item in schema["items"]:
        walk(item["structure"])


def test_the_pilot_document_states_its_limits_once_and_is_current():
    import render_wp1_pilot

    text = (REPO_ROOT / "docs" / "LITERATURE_WP1_PILOT.md").read_text(encoding="utf-8")
    phrase = "ten items, deterministically sampled, for workflow validation; not representative of the corpus."
    assert text.lower().count(phrase) == 1
    assert text == render_wp1_pilot.render()
