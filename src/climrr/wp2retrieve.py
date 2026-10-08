"""M4-WP2 retrieval (D-018): frozen terms -> boundary-aware scan -> frozen candidates.

This module **retrieves; it does not read.** It decides which corpus items a
later package should inspect, by where approved terms occur, and nothing else.
It stores no decoded text except the exact characters each hit matched.

The rule, in order (D-018, item 8):

1. Terms: every accepted surface term of an `approved_lexical` entry in
   `data/metadata/concept_map.yaml` (class `concept`), and the exact `State` /
   `NAME` label strings of the prototypes' state- and county-level `G`
   identifiers (class `place`). No alias, no postal code.
2. Scan every manifest item, hash-verified, decoded as JSON; every **string
   value** at any depth (object keys are not scanned) with
   `climrr.conceptmap.find_term` --- case-insensitive, boundary-aware.
3. Qualify iff >= 1 concept hit and >= 1 place hit.
4. Drop the later member(s) of every exact-byte duplicate group, keeping the
   lowest LIT id --- **before** the cap.
5. Sort by LIT id; take the first 12.
"""

from __future__ import annotations

import json
from pathlib import Path

from climrr import conceptmap, litingest
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT, repo_relative

LIT = REPO_ROOT / "artifacts" / "literature"
TERMS_PATH = LIT / "wp2_terms.json"
POOL_PATH = LIT / "wp2_qualifying_pool.json"
CANDIDATES_PATH = LIT / "wp2_candidates.json"
CORPUS_MANIFEST_PATH = LIT / "corpus_manifest.json"
PROTOTYPES_DIR = REPO_ROOT / "artifacts" / "phenomena" / "prototypes"
PLACE_PROTOTYPES = ("P-COUNTY-1", "P-STATE-1")
CAP = 12

STATEMENT = "Relevance-guided candidate-generation sample, not representative."
NOT_READ = "No candidate has been read; semantic inspection waits for M4-WP1b (D-018)."
RULE = (
    "Scan every corpus-manifest item (SHA-256 verified, decoded as JSON); in every string value at any depth "
    "(object keys not scanned), find every frozen term case-insensitively where the code points immediately "
    "before and after the match, if any, are not letters, numbers or combining marks (Unicode categories L*, "
    "N*, M*). Qualify iff >= 1 concept-term hit and >= 1 place-term hit. Remove the later member(s) of every "
    "exact-byte duplicate group (keep the lowest LIT id) before the cap. Sort by LIT id; take the first 12. "
    "No manual replacement."
)


class RetrievalError(RuntimeError):
    """A frozen retrieval artifact no longer matches a rebuild."""


# --- terms ----------------------------------------------------------------------


def build_terms() -> dict:
    entries = conceptmap.load()
    terms = []
    for e in entries:
        if e["status"] != "approved_lexical":
            continue
        for t in e["accepted_surface_terms"]:
            terms.append({"term": t, "term_class": "concept", "canonical_id": e["canonical_id"],
                          "level": e["level"], "source": "data/metadata/concept_map.yaml"})
    for pid in PLACE_PROTOTYPES:
        rec = json.loads((PROTOTYPES_DIR / f"{pid}.json").read_text(encoding="utf-8"))
        g = rec["G"]
        for col in ("State", "NAME"):
            if col in g["identifier"] and not any(x["term"] == g["identifier"][col] for x in terms):
                terms.append({"term": g["identifier"][col], "term_class": "place", "source_prototype": pid,
                              "identifier_column": col, "level": g["level"],
                              "provenance_status": g["provenance_status"]})
    for i, t in enumerate(terms, 1):
        t["term_id"] = f"WP2-T{i:02d}"
    return {
        "package": "M4-WP2 retrieval",
        "authorized_by": "docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md (D-018)",
        "concept_map_sha256": sha256_file(conceptmap.CONCEPT_MAP_PATH),
        "place_terms_rule": "the exact State / NAME label strings of the state- and county-level prototype "
                            "identifiers; no aliases, no postal codes (D-018)",
        "boundary_rule": conceptmap.BOUNDARY_RULE,
        "terms": [{k: t[k] for k in ("term_id", "term", "term_class", *sorted(set(t) - {"term_id", "term", "term_class"}))}
                  for t in terms],
    }


# --- scan -----------------------------------------------------------------------


def string_values(doc: object, path: str = "$"):
    """(json_path, string) for every string value at any depth; keys are not values."""
    if isinstance(doc, str):
        yield path, doc
    elif isinstance(doc, dict):
        for k, v in doc.items():
            yield from string_values(v, litingest.child_path(path, k))
    elif isinstance(doc, list):
        for i, v in enumerate(doc):
            yield from string_values(v, litingest.child_path(path, i))


def scan_doc(item_id: str, doc: object, terms: list[dict]) -> list[dict]:
    hits = []
    for json_path, text in string_values(doc):
        for t in terms:
            for s, e in conceptmap.find_term(t["term"], text):
                hits.append({"item_id": item_id, "json_path": json_path, "term_id": t["term_id"],
                             "term": t["term"], "term_class": t["term_class"], "char_start": s, "char_end": e,
                             "matched_text": text[s:e]})
    return hits


def counts(hits: list[dict], terms: list[dict]) -> dict:
    return {
        "concept_hits": sum(h["term_class"] == "concept" for h in hits),
        "place_hits": sum(h["term_class"] == "place" for h in hits),
        "by_term": {t["term_id"]: sum(h["term_id"] == t["term_id"] for h in hits) for t in terms},
    }


def later_duplicates(entries: list[dict]) -> set[str]:
    groups: dict[str, list[str]] = {}
    for e in entries:
        if e.get("duplicate_group"):
            groups.setdefault(e["duplicate_group"], []).append(e["item_id"])
    return {i for ids in groups.values() for i in sorted(ids)[1:]}


def select(qualifying: list[str], entries: list[dict], cap: int = CAP) -> tuple[list[str], list[str]]:
    """(the first `cap` after dedupe, the ids dedupe removed)."""
    later = later_duplicates(entries)
    removed = sorted(i for i in qualifying if i in later)
    pool = sorted(i for i in qualifying if i not in later)
    return pool[:cap], removed


def run(corpus_root: Path, terms_doc: dict) -> tuple[dict, dict]:
    """Scan the whole corpus. Returns (pool artifact, candidates artifact)."""
    manifest = json.loads(CORPUS_MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = manifest["entries"]
    terms = terms_doc["terms"]
    per_item: dict[str, dict] = {}
    hits_by_item: dict[str, list[dict]] = {}
    parse_failures = []
    for e in entries:
        doc, failure = litingest.read_verified(Path(corpus_root) / e["relative_path"], e["sha256"])
        if failure is not None:
            parse_failures.append({"item_id": e["item_id"], "reason": failure})
            continue
        hits = scan_doc(e["item_id"], doc, terms)
        per_item[e["item_id"]] = counts(hits, terms)
        hits_by_item[e["item_id"]] = hits
    qualifying = sorted(i for i, c in per_item.items() if c["concept_hits"] and c["place_hits"])
    chosen, removed = select(qualifying, entries)
    pool_ids = [i for i in qualifying if i not in removed]
    common = {
        "package": "M4-WP2 retrieval",
        "statement": STATEMENT,
        "not_read": NOT_READ,
        "rule": RULE,
        "cap": CAP,
        "terms_sha256": sha256_file(TERMS_PATH),
        "corpus_manifest_sha256": sha256_file(CORPUS_MANIFEST_PATH),
        "corpus_content_identity_sha256": manifest["content_identity_sha256"],
    }
    pool = {
        **common,
        "n_items_scanned": len(entries),
        "n_parse_failures": len(parse_failures),
        "parse_failures": parse_failures,
        "n_with_concept_hit": sum(1 for c in per_item.values() if c["concept_hits"]),
        "n_with_place_hit": sum(1 for c in per_item.values() if c["place_hits"]),
        "n_qualifying_before_dedupe": len(qualifying),
        "removed_as_later_duplicates": removed,
        "n_qualifying_pool": len(pool_ids),
        "pool": [{"item_id": i, **per_item[i]} for i in pool_ids],
    }
    candidates = {
        **common,
        "n_qualifying_pool": len(pool_ids),
        "n_candidates": len(chosen),
        "candidate_ids": chosen,
        "candidates": [{"item_id": i, **per_item[i], "hits": hits_by_item[i]} for i in chosen],
    }
    return pool, candidates


def write_or_verify(path: Path, obj: dict) -> str:
    """Write a frozen artifact once; afterwards fail unless a rebuild is identical."""
    text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise RetrievalError(f"{repo_relative(path)} differs from a rebuild; frozen artifacts are not refreshed")
        return "verified"
    path.write_text(text, encoding="utf-8")
    return "written"
