"""Query-scope coverage (M4-WP0, ruling §3, actions 4--5).

Compares the pilot's own vocabulary --- the `literature_probe.concept_terms` of
the three prototype records and the names of the four pilot families --- with
the terms of the parsed collection query. **It is named query-scope coverage,
not corpus coverage**, and every result it produces is a statement about the
query:

    The Boolean query explains how the candidate corpus was collected. It does
    not establish what any paper contains or which prototype a paper supports.

Classification
--------------

Each pilot string is compared, **as a whole string**, with every query term:

- `exact_query_term` --- identical to a query term's text, character for
  character;
- `normalized_lexical_match` --- not identical, but `normalize_term` of the two
  is the same string;
- `absent_from_query` --- neither.

There is no substring, word or stem matching: `Heat Index – Summer` is not
`heat index`, and saying it "contains" a query term would be a new rule, not
this one.

The ruling names a fourth category, `inferred_conceptual_relationship`, "if
introduced later". It is **defined here and cannot be emitted**: `classify`
has no code path that returns it, and a test pins that. Introducing it is a
decision for a later package, not a side effect of this one.

A hazard group counts as touched by the pilot when at least one of its terms
is the matched term of an `exact_query_term` or `normalized_lexical_match`.
Every other group is reported as having no pilot counterpart under that rule
--- a fact about which query strings the pilot's strings equal, not a claim
about hazards.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from climrr.litquery import all_terms, normalize_term

EXACT = "exact_query_term"
NORMALIZED = "normalized_lexical_match"
ABSENT = "absent_from_query"
INFERRED = "inferred_conceptual_relationship"

#: Every category the ruling names, in its order.
CATEGORIES = (EXACT, NORMALIZED, ABSENT, INFERRED)
#: The categories this package may emit. INFERRED is defined, unused.
EMITTABLE = (EXACT, NORMALIZED, ABSENT)

_FAMILY_HEADING_RE = re.compile(r"^### Family (\d+) --- (.+?) \(", re.MULTILINE)


def classify(term: str, structure: dict) -> dict:
    """Classify one pilot string against every query term. Never returns INFERRED."""
    terms = all_terms(structure)
    exact = [t["term_id"] for t in terms if t["text"] == term]
    if exact:
        return {"term": term, "classification": EXACT, "matched_term_ids": exact}
    norm = normalize_term(term)
    normalized = [t["term_id"] for t in terms if t["normalized"] == norm]
    if normalized:
        return {"term": term, "classification": NORMALIZED, "matched_term_ids": normalized}
    return {"term": term, "classification": ABSENT, "matched_term_ids": []}


def load_probe_terms(prototypes_dir: Path) -> list[dict]:
    """`record_id` and `literature_probe.concept_terms` of every prototype record."""
    probes = []
    for path in sorted(Path(prototypes_dir).glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        probes.append(
            {
                "record_id": record["record_id"],
                "path": path,
                "concept_terms": list(record["literature_probe"]["concept_terms"]),
            }
        )
    return probes


def load_pilot_families(pilot_subset_md: Path) -> list[dict]:
    """The family names, verbatim, from the `### Family N --- name (` headings."""
    text = Path(pilot_subset_md).read_text(encoding="utf-8")
    return [
        {"family": f"Family {m.group(1)}", "name": m.group(2)}
        for m in _FAMILY_HEADING_RE.finditer(text)
    ]


def _counts(rows: list[dict]) -> dict:
    return {c: sum(r["classification"] == c for r in rows) for c in EMITTABLE}


def coverage(structure: dict, probes: list[dict], families: list[dict]) -> dict:
    """The whole comparison: per prototype, per family, and the unmatched groups."""
    per_prototype = []
    for probe in probes:
        rows = [classify(term, structure) for term in probe["concept_terms"]]
        per_prototype.append(
            {"record_id": probe["record_id"], "rows": rows, "counts": _counts(rows)}
        )
    family_rows = [
        {**fam, **classify(fam["name"], structure)} for fam in families
    ]

    matched = {
        term_id
        for block in [r for p in per_prototype for r in p["rows"]] + family_rows
        for term_id in block["matched_term_ids"]
    }
    groups = []
    for group in structure["hazard_groups"]:
        ids = [t["term_id"] for t in group["terms"]]
        hit = sorted(set(ids) & matched)
        groups.append(
            {
                "group_id": group["group_id"],
                "first_term": group["terms"][0]["text"],
                "n_terms": group["n_terms"],
                "terms": [t["text"] for t in group["terms"]],
                "pilot_matched_term_ids": hit,
                "has_pilot_counterpart": bool(hit),
            }
        )
    context_hits = sorted(
        t["term_id"] for t in structure["context_terms"] if t["term_id"] in matched
    )
    return {
        "categories_defined": list(CATEGORIES),
        "categories_emittable": list(EMITTABLE),
        "per_prototype": per_prototype,
        "families": family_rows,
        "family_counts": _counts(family_rows),
        "hazard_groups": groups,
        "context_terms_matched": context_hits,
    }
