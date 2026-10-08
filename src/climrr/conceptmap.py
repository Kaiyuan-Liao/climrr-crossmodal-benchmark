"""D-018: the concept map, its validator, and the boundary-aware term matcher.

`data/metadata/concept_map.yaml` names canonical concepts at two levels ---
`family` and `metric` --- and the exact surface terms that name them. The
validator refuses any entry the ruling does not allow: a metric with terms but
no GUIDANCE or mentor source; a family term not quoted from a cited dictionary
line. Only `approved_lexical` entries ever match anything.

**The boundary rule**, used here and by the M4-WP2 retrieval scan: a term
matches at `[start, end)` in a string when the characters equal the term
case-insensitively (Python `re.IGNORECASE`, no normalization, so offsets stay
code points on the unnormalized string) **and** the code point before `start`
and the code point at `end`, where they exist, are not *word code points*. A
word code point is one whose Unicode general category is a letter (`L*`), a
number (`N*`) or a combining mark (`M*`) --- a mark would modify the matched
letter. Consequences: "FWI" does not match "FWIs" or "FWI2"; it matches "FWI,"
"(FWI)" "FWI-based" and "FWI_x"; "heat index" does not match "heat-index" or
"heat  index" (internal characters are matched exactly).
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import yaml

from climrr.paths import REPO_ROOT

CONCEPT_MAP_PATH = REPO_ROOT / "data" / "metadata" / "concept_map.yaml"
DICTIONARY_TEXT_PATH = REPO_ROOT / "data" / "metadata" / "dictionary_extracted.txt"

BOUNDARY_RULE = (
    "A term matches at [start, end) in a string when the characters equal the term case-insensitively "
    "(Python re.IGNORECASE; no normalization, so offsets are code points on the unnormalized string) and the "
    "code point before start and the code point at end, where they exist, are not letters, numbers or "
    "combining marks (Unicode general categories L*, N*, M*). So 'FWI' does not match 'FWIs' or 'FWI2' and "
    "does match 'FWI,', '(FWI)', 'FWI-based' and 'FWI_x'; 'heat index' does not match 'heat-index' or "
    "'heat  index'."
)

LEVELS = ("family", "metric")
SOURCE_TYPES = ("dictionary", "mentor", "guidance")
ENTRY_STATUSES = ("approved_lexical", "proposed")
REQUIRED = ("canonical_id", "level", "accepted_surface_terms", "source_type", "source_reference",
            "source_span", "decision_id", "date", "status", "approved_by")


class ConceptMapError(ValueError):
    """An entry the D-018 rules do not allow."""


def is_word_code_point(ch: str) -> bool:
    return unicodedata.category(ch)[0] in ("L", "N", "M")


def find_term(term: str, text: str) -> list[tuple[int, int]]:
    """Every boundary-aware, case-insensitive occurrence of `term` in `text`, as `[start, end)`."""
    out = []
    for m in re.finditer(re.escape(term), text, re.IGNORECASE):
        s, e = m.span()
        if s > 0 and is_word_code_point(text[s - 1]):
            continue
        if e < len(text) and is_word_code_point(text[e]):
            continue
        out.append((s, e))
    return out


def normalize_concept(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def validate(data: dict, dictionary_lines: list[str]) -> list[dict]:
    entries = data["entries"]
    ids = [e.get("canonical_id") for e in entries]
    if len(set(ids)) != len(ids):
        raise ConceptMapError("duplicate canonical_id")
    families = {e["canonical_id"] for e in entries if e.get("level") == "family"}
    seen_terms: dict[str, str] = {}
    for e in entries:
        cid = e.get("canonical_id")
        missing = [k for k in REQUIRED if k not in e]
        if missing:
            raise ConceptMapError(f"{cid}: missing {missing}")
        if e["level"] not in LEVELS or e["source_type"] not in SOURCE_TYPES or e["status"] not in ENTRY_STATUSES:
            raise ConceptMapError(f"{cid}: level, source_type or status outside the vocabulary")
        terms = e["accepted_surface_terms"]
        if e["level"] == "metric":
            if e.get("parent_family") not in families:
                raise ConceptMapError(f"{cid}: a metric must name an existing parent_family")
            if terms and e["source_type"] not in ("guidance", "mentor"):
                raise ConceptMapError(f"{cid}: a metric with surface terms needs a guidance or mentor source")
        else:
            if "parent_family" in e:
                raise ConceptMapError(f"{cid}: a family has no parent_family")
            if terms and e["source_type"] != "dictionary":
                raise ConceptMapError(f"{cid}: family terms must be dictionary-backed")
            for t in terms:
                lines = [dictionary_lines[n - 1] for n in e["source_span"] if 0 < n <= len(dictionary_lines)]
                if not any(find_term(t, line) for line in lines):
                    raise ConceptMapError(f"{cid}: term {t!r} is not on any cited dictionary line")
        if e["status"] == "approved_lexical" and (not e["approved_by"] or e["approved_by"] == "none"):
            raise ConceptMapError(f"{cid}: approved_lexical without approved_by")
        for t in terms:
            key = normalize_concept(t)
            if key in seen_terms:
                raise ConceptMapError(f"{cid}: term {t!r} already belongs to {seen_terms[key]}")
            seen_terms[key] = cid
    return entries


def load(path: Path | None = None, dictionary_path: Path | None = None) -> list[dict]:
    data = yaml.safe_load((path or CONCEPT_MAP_PATH).read_text(encoding="utf-8"))
    lines = (dictionary_path or DICTIONARY_TEXT_PATH).read_text(encoding="utf-8").splitlines()
    return validate(data, lines)


def approved_family_terms(entries: list[dict]) -> dict[str, str]:
    """Normalized surface term -> family canonical id, `approved_lexical` families only."""
    return {normalize_concept(t): e["canonical_id"] for e in entries
            if e["level"] == "family" and e["status"] == "approved_lexical" for t in e["accepted_surface_terms"]}


def family_of(canonical_id: str, entries: list[dict]) -> str | None:
    for e in entries:
        if e["canonical_id"] == canonical_id:
            return canonical_id if e["level"] == "family" else e.get("parent_family")
    return None
