"""Retrieval governance rules (M4-WP3). Currently one rule: **R-FWI-1 v1** (D-022).

This module **retrieves; it does not read.** It decides whether a document may
enter the fire-weather candidate corpus from where approved terms occur, and
nothing else. It stores no decoded text except the exact characters each hit
matched.

**R-FWI-1 v1** (GUIDANCE source-yield ruling, 2026-10-12, recorded as D-022;
`docs/M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md`, evidence check 5 and 6):

- The bare acronym `fwi` admits a document to the fire-weather arm **only when
  the same document** also contains an approved fire-weather disambiguator:
  `fire weather`, `fire-weather`, `fire weather index`, `fire-weather index`,
  `canadian forest fire weather index`, `canadian fwi`.
- Same-document, **not** same-sentence or same-section.
- A longer topical term (`fire weather index`, `fire-weather index`,
  `canadian forest fire weather index`, `canadian fwi`) admits directly; it
  disambiguates itself.
- Both hit locations --- the bare term's and the disambiguator's --- are
  returned, so every decision is auditable.

This is a **retrieval policy, not a scientific change to the concept.** `FWI`
stays an accepted surface term of `fire_weather_index` in
`data/metadata/concept_map.yaml`, unchanged; a test pins that file's hash. An
admitted document is a retrieval hit, never a claim or a bridge: claim
extraction still decides whether a text concerns the ClimRR FWI metric.

Matching uses the frozen boundary-aware matcher, `climrr.conceptmap.find_term`
(the same function as the M4-WP2 retrieval scan and rule C-2). It differs from
the DuckDB `\\b` matcher the external collection runs used in two edge cases,
both disclosed in `docs/BRIDGE_ELIGIBILITY.md`: an underscore is a boundary
here and a word character there, and a non-ASCII letter next to the term is a
word character here and a boundary there.
"""

from __future__ import annotations

from typing import Iterable

from climrr.conceptmap import find_term

RULE_ID = "R-FWI-1"
RULE_VERSION = "v1"
DECISION_ID = "D-022"
RULE_SOURCE = "docs/M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md"

BARE_TERM = "fwi"

#: The six approved disambiguators, in the ruling's order.
DISAMBIGUATORS = (
    "fire weather",
    "fire-weather",
    "fire weather index",
    "fire-weather index",
    "canadian forest fire weather index",
    "canadian fwi",
)

#: The topical group of the frozen production query `fire_weather_v1_query.txt`
#: (SHA-256 73c13461...), in query order. `fwi` is the only bare acronym.
FIRE_WEATHER_TOPICAL_TERMS_V1 = (
    "fire weather index",
    "fire-weather index",
    "fwi",
    "canadian forest fire weather index",
    "canadian fwi",
)

DIRECT_TERMS = tuple(t for t in FIRE_WEATHER_TOPICAL_TERMS_V1 if t != BARE_TERM)

RULE_TEXT = (
    "R-FWI-1 v1 (D-022): a document is fire-weather retrieval-eligible iff some string section contains a "
    "topical term other than bare 'fwi' (fire weather index, fire-weather index, canadian forest fire weather "
    "index, canadian fwi), or some section contains bare 'fwi' and some section of the same document contains an "
    "approved disambiguator (fire weather, fire-weather, fire weather index, fire-weather index, canadian forest "
    "fire weather index, canadian fwi). Same-document, not same-sentence. Matching: climrr.conceptmap.find_term "
    "(case-insensitive, boundary-aware, no normalization). The first bare-term hit and the first disambiguator hit "
    "(document order) are both recorded as section key, section index and [start, end)."
)

#: Decision bases, closed vocabulary.
BASIS_DIRECT = "direct_topical_term"
BASIS_DISAMBIGUATED = "bare_fwi_with_same_document_disambiguator"
BASIS_BARE_ONLY = "bare_fwi_without_disambiguator"
BASIS_NONE = "no_topical_term"


def first_hit(term: str, sections: list[tuple[str, str]]) -> dict | None:
    """The first occurrence of `term` in document order, as an auditable location."""
    for idx, (key, text) in enumerate(sections):
        spans = find_term(term, text)
        if spans:
            s, e = spans[0]
            return {"term": term, "section_key": key, "section_idx": idx,
                    "char_start": s, "char_end": e, "matched_text": text[s:e]}
    return None


def _earliest(hits: Iterable[dict | None]) -> dict | None:
    present = [h for h in hits if h is not None]
    return min(present, key=lambda h: (h["section_idx"], h["char_start"], -h["char_end"])) if present else None


def evaluate(sections: Iterable[tuple[str, str]]) -> dict:
    """Apply R-FWI-1 v1 to one document, given as `(section_key, string_value)` pairs in document order.

    Returns the decision, its basis, and the hit locations it rests on.
    """
    secs = [(str(k), v) for k, v in sections if isinstance(v, str)]
    direct = _earliest(first_hit(t, secs) for t in DIRECT_TERMS)
    bare = first_hit(BARE_TERM, secs)
    disambiguator = _earliest(first_hit(t, secs) for t in DISAMBIGUATORS)
    if direct is not None:
        eligible, basis = True, BASIS_DIRECT
    elif bare is not None and disambiguator is not None:
        eligible, basis = True, BASIS_DISAMBIGUATED
    elif bare is not None:
        eligible, basis = False, BASIS_BARE_ONLY
    else:
        eligible, basis = False, BASIS_NONE
    return {
        "rule_id": RULE_ID,
        "rule_version": RULE_VERSION,
        "decision_id": DECISION_ID,
        "eligible": eligible,
        "basis": basis,
        "direct_term_hit": direct,
        "bare_term_hit": bare,
        "disambiguator_hit": disambiguator,
    }


def flat_sections(doc: object) -> list[tuple[str, str]]:
    """The `(key, value)` string sections of a flat JSON object, in file order; non-strings dropped."""
    if not isinstance(doc, dict):
        return []
    return [(k, v) for k, v in doc.items() if isinstance(v, str)]
