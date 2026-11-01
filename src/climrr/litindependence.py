"""Paper independence v2 (DR-LIT-IND-1 v2, D-046) and the cluster strengths it implies (pilot P2b-prep).

**DR-LIT-IND-1 v2** (COORDINATOR ruling 2026-11-01): two papers with an identical
`paper_sha256` are **one paper** (basis `same_paper_sha256`); two papers whose title
sections are identical after normalization --- lowercase, every run of punctuation /
whitespace collapsed to one space --- are a `possible_duplicate` and **counted as one**
(basis `possible_duplicate_title`); otherwise they are independent with basis
`assumed_independent_distinct_ids` (the corpus index has no author field). The relation
is closed transitively: each paper gets a `canonical_id` (the smallest item id of its
group), and the number of independent papers in a set is the number of distinct
canonical ids.

The title is read from each paper's `[SECTION: title]` in the run-2 `prompt_user.txt`,
which ingest did not copy (D-044); `scripts/build_independence_v2.py` reads it from the
delivered tarball, checked against its pinned SHA-256, and writes only hashes and groups to
`artifacts/litstatements/run2/independence_v2.json`.

`clusters_v1b`: the v1 clusters (DR-LIT-AGG-1 v2, same members, same ids) with
`n_independent_papers`, `n_independent_core_cited_papers` and `evidence_strength`
recomputed under v2. Clusters v1 are a lexical baseline kept as diagnostic evidence
(D-048); v1b is what the v2 seeds rank by.

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter

from climrr import litaggregate as la
from climrr import litstatements_run2 as r2
from climrr.checksums import sha256_file

VERSION = "litindependence v1"
RULE_ID = "DR-LIT-IND-1 v2"
DECISION = "D-046"
INDEPENDENCE_PATH = r2.ART / "independence_v2.json"
CLUSTERS_V1B_PATH = r2.ART / "clusters_v1b.jsonl"
CLUSTERS_V1B_SUMMARY_PATH = r2.ART / "clusters_v1b_summary.json"
BASES = ("same_paper_sha256", "possible_duplicate_title", "assumed_independent_distinct_ids")
RULE_TEXT = ("DR-LIT-IND-1 v2 (D-046): identical paper_sha256 -> one paper; identical normalized title (lowercase, "
             "punctuation/whitespace collapsed) -> possible_duplicate, counted as one; otherwise "
             "assumed_independent_distinct_ids. Closed transitively; canonical_id = smallest item id of the group.")

_PUNCT_WS = re.compile(r"[\W_]+")


def normalize_title(title: str) -> str:
    """Lowercase; every run of punctuation / whitespace (Unicode non-word characters and '_') -> one space."""
    return " ".join(_PUNCT_WS.sub(" ", title.lower()).split())


def _groups(papers: list[dict], key: str) -> list[list[str]]:
    g: dict[str, list[str]] = {}
    for p in papers:
        if p.get(key):
            g.setdefault(p[key], []).append(p["item_id"])
    return sorted(sorted(v) for v in g.values() if len(v) > 1)


def build(papers: list[dict]) -> dict:
    """`papers`: [{item_id, paper_sha256, title (str | None)}] -> the independence_v2 record (titles kept as hashes)."""
    rows = []
    for p in sorted(papers, key=lambda x: x["item_id"]):
        t = normalize_title(p["title"]) if p.get("title") else None
        rows.append({"item_id": p["item_id"], "paper_sha256": p["paper_sha256"], "title_section_present": p.get("title") is not None,
                     "title_normalized_v2_sha256": hashlib.sha256(t.encode("utf-8")).hexdigest() if t else None})
    same_sha, same_title = _groups(rows, "paper_sha256"), _groups(rows, "title_normalized_v2_sha256")
    canon = {r["item_id"]: r["item_id"] for r in rows}

    def find(x):
        while canon[x] != x:
            x = canon[x]
        return x

    for g in same_sha + same_title:
        roots = sorted({find(i) for i in g})
        for r in roots[1:]:
            canon[r] = roots[0]
    in_sha = {i for g in same_sha for i in g}
    in_title = {i for g in same_title for i in g}
    for r in rows:
        r["canonical_id"] = find(r["item_id"])
        r["basis"] = ("same_paper_sha256" if r["item_id"] in in_sha else
                      "possible_duplicate_title" if r["item_id"] in in_title else "assumed_independent_distinct_ids")
    canon_groups = Counter(r["canonical_id"] for r in rows)
    return {"rule_id": RULE_ID, "decision": DECISION, "rule": RULE_TEXT, "version": VERSION,
            "title_normalization": "lowercase; [\\W_]+ -> ' '; strip", "author_check": "unavailable",
            "papers_n": len(rows), "canonical_papers_n": len(canon_groups),
            "n_title_section_present": sum(r["title_section_present"] for r in rows),
            "same_paper_sha256_groups": same_sha, "possible_duplicate_title_groups": same_title,
            "merged_groups": sorted(sorted(i for i in canon if find(i) == c) for c, n in canon_groups.items() if n > 1),
            "by_basis": {b: sum(r["basis"] == b for r in rows) for b in BASES},
            "papers": rows}


def canonical_map(indep: dict) -> dict:
    return {p["item_id"]: p["canonical_id"] for p in indep["papers"]}


def independent(a: str, b: str, indep: dict) -> tuple[bool, str]:
    """DR-LIT-IND-1 v2 for two paper ids: (independent, basis)."""
    if a == b:
        return False, "same_id"
    by = {p["item_id"]: p for p in indep["papers"]}
    pa, pb = by[a], by[b]
    if pa["canonical_id"] != pb["canonical_id"]:
        return True, "assumed_independent_distinct_ids"
    if pa["paper_sha256"] == pb["paper_sha256"]:
        return False, "same_paper_sha256"
    return False, "possible_duplicate_title"


def n_independent(ids, canon: dict) -> int:
    """Distinct canonical papers among `ids` (an id absent from the map counts as itself)."""
    return len({canon.get(i, i) for i in ids})


# --- clusters v1b -----------------------------------------------------------------------------


def strength_v2(members: list[dict], canon: dict) -> str:
    """D-045 evidence strength with D-046 independence; `members` carry evidence_role, paper_item_id, passage_type."""
    cc = {m["paper_item_id"] for m in members if m["evidence_role"] in la.CORE_OR_CITED}
    if n_independent(cc, canon) >= 2:
        return "multi_source_supported"
    if any(m.get("passage_type") == "review_synthesis" for m in members):
        return "review_supported"
    if cc:
        return "single_source_supported"
    return "background_only"


def clusters_v1b(clusters: list[dict], indep: dict) -> list[dict]:
    canon = canonical_map(indep)
    out = []
    for c in clusters:
        cc = {m["paper_item_id"] for m in c["members"] if m["evidence_role"] in la.CORE_OR_CITED}
        d = dict(c)
        d.update({
            "independence_rule": RULE_ID, "independence_basis": "D-046: canonical paper ids (same sha256 / normalized title merged)",
            "n_independent_papers": n_independent(c["papers"], canon),
            "n_independent_core_cited_papers": n_independent(cc, canon),
            "evidence_strength": strength_v2(c["members"], canon),
            "evidence_strength_v1": c["evidence_strength"],
            "n_independent_papers_v1": c["n_independent_papers"],
            "canonical_papers": sorted({canon.get(p, p) for p in c["papers"]}),
        })
        d.pop("multi_source_relies_on_diagnostic_pair", None)
        out.append(d)
    return out


def summarise_v1b(v1b: list[dict], indep: dict) -> dict:
    changed = [c for c in v1b if c["evidence_strength"] != c["evidence_strength_v1"]]
    return {"version": VERSION, "rule": RULE_ID, "decision": DECISION,
            "inputs": {"clusters_v1": {"path": "artifacts/litstatements/run2/clusters_v1.jsonl", "sha256": sha256_file(la.CLUSTERS_PATH)},
                       "independence_v2": {"path": "artifacts/litstatements/run2/independence_v2.json", "sha256": sha256_file(INDEPENDENCE_PATH)}},
            "clusters_file": {"path": "artifacts/litstatements/run2/clusters_v1b.jsonl", "sha256": sha256_file(CLUSTERS_V1B_PATH)},
            "clusters": len(v1b), "members_unchanged": True,
            "by_strength": {s: sum(c["evidence_strength"] == s for c in v1b) for s in la.STRENGTHS},
            "by_strength_v1": {s: sum(c["evidence_strength_v1"] == s for c in v1b) for s in la.STRENGTHS},
            "strength_changed": [{"cluster_id": c["cluster_id"], "v1": c["evidence_strength_v1"], "v1b": c["evidence_strength"],
                                  "papers": c["papers"], "canonical_papers": c["canonical_papers"]} for c in changed],
            "multi_source_supported": [c["cluster_id"] for c in v1b if c["evidence_strength"] == "multi_source_supported"],
            "merged_paper_groups": indep["merged_groups"]}
