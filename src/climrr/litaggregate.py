"""Deterministic cross-paper aggregation of literature statements (pilot P2a; DR-LIT-AGG-1 v2, D-045).

Input: the run-2 statements with their evidence roles
(`artifacts/litstatements/run2/statements_ingested.jsonl`, `litstatements_run2.py`). Only
`core_candidate`, `cited_candidate` and `background_consensus_candidate` statements enter.

**DR-LIT-AGG-1 v2** (COORDINATOR ruling 2026-11-01; deliberately conservative and lexical):

1. *Partition*: arm x statement_type x direction. Direction is lexical
   (`data/metadata/litstatements/direction_lexicon_v1.yaml`): a term from one list and none
   from the other, else `unspecified`.
2. *Tokens*: the statement lowercased, every character outside [a-z0-9] a space; words in
   `stopwords_v1.yaml`, one-character words and all-digit words dropped; the crude
   lemmatizer applied to each remaining word, once, first rule that fits: ends in `ing` and
   longer than 5 characters -> drop `ing`; ends in `ed` and longer than 4 -> drop `ed`; ends in
   `s` but not `ss` and longer than 3 -> drop `s`. Content unigrams, and bigrams of tokens
   adjacent after the removal.
3. *Document-frequency filter*: within an arm, a unigram or bigram in more than 15 % of
   that arm's entering statements is dropped (generated list `df_filter_dropped_v1.yaml`).
4. *Similarity*: cosine of binary vectors weighted by IDF = ln(N / df) over the arm's
   entering statements (N statements, df statements containing the term).
5. *Clustering*: union-find within a partition at cosine >= 0.30. No concept-lexicon merge:
   `concept_lexicon_v1.yaml` (the 60 most frequent content unigrams per arm, with their
   document frequencies) is a frequency table only.

The first rule (v1: Jaccard >= 0.35 on unigrams, plus a merge on >= 2 shared concept-lexicon
tokens) is replayed by `rule_v1_grid` only to document its degeneracy.

A cluster's **evidence strength**: `multi_source_supported` --- >= 2 independent papers
(DR-LIT-IND-1) contribute core or cited statements; else `review_supported` --- a member's
passage is a review_synthesis; else `single_source_supported` --- one paper contributes core
or cited statements (others may add background passages); else `background_only`. The
**representative statement** is the member with the highest mean v2 similarity to the other
members (ties -> lowest id); it is a verbatim member statement --- code writes no paraphrase.
Semantic merging of paraphrases is P2b (agent-proposed, human-checked), never code.

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import itertools
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from climrr import litstatements_run2 as r2
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

VERSION = "litaggregate v1"
RULE_ID = "DR-LIT-AGG-1 v2"
META_DIR = REPO_ROOT / "data" / "metadata" / "litstatements"
DIRECTION_LEXICON = META_DIR / "direction_lexicon_v1.yaml"
STOPWORDS = META_DIR / "stopwords_v1.yaml"
CONCEPT_LEXICON = META_DIR / "concept_lexicon_v1.yaml"
DF_DROPPED = META_DIR / "df_filter_dropped_v1.yaml"
CLUSTERS_PATH = r2.ART / "clusters_v1.jsonl"
SUMMARY_PATH = r2.ART / "clusters_v1_summary.json"

THRESHOLD = 0.30
GRID = (0.20, 0.25, 0.30, 0.35, 0.40, 0.50)
LARGE_CLUSTER = 25
DF_MAX_SHARE = 0.15
LEXICON_TOP = 60
V1_THRESHOLD, V1_GRID, V1_LEXICON_SHARED = 0.35, (0.25, 0.35, 0.45), 2

ARMS = ("extreme_heat_v1", "fire_weather_v1")
ARM_FAMILY = {"extreme_heat_v1": "heat_index", "fire_weather_v1": "fire_weather_index"}
STATEMENT_TYPES = ("mechanism", "driver", "consensus", "caveat", "pattern")
DIRECTIONS = ("increase", "decrease", "unspecified")
ENTERING_ROLES = ("core_candidate", "cited_candidate", "background_consensus_candidate")
CORE_OR_CITED = ("core_candidate", "cited_candidate")
STRENGTHS = ("multi_source_supported", "review_supported", "single_source_supported", "background_only")
UNNAMED = ("", "unknown", "unsupported")


# --- tokens -------------------------------------------------------------------------------------


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def stopwords() -> frozenset:
    return frozenset(load_yaml(STOPWORDS)["words"])


def direction_lexicon() -> dict:
    d = load_yaml(DIRECTION_LEXICON)
    return {"increase": tuple(d["increase"]), "decrease": tuple(d["decrease"])}


def words(text: str) -> list[str]:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).split()


def lemma(w: str) -> str:
    if len(w) > 5 and w.endswith("ing"):
        return w[:-3]
    if len(w) > 4 and w.endswith("ed"):
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def content_seq(text: str, stop: frozenset) -> list[str]:
    return [lemma(w) for w in words(text) if w not in stop and len(w) > 1 and not w.isdigit()]


def grams(text: str, stop: frozenset) -> frozenset:
    s = content_seq(text, stop)
    return frozenset(s) | frozenset(f"{a} {b}" for a, b in zip(s, s[1:]))


def direction(text: str, lex: dict) -> tuple[str, list[str]]:
    """(direction, the lexicon terms found), DR-LIT-AGG-1 v2 step 1."""
    padded = " " + " ".join(words(text)) + " "
    found = {d: [t for t in lex[d] if f" {t} " in padded] for d in ("increase", "decrease")}
    terms = sorted(found["increase"] + found["decrease"])
    if found["increase"] and not found["decrease"]:
        return "increase", terms
    if found["decrease"] and not found["increase"]:
        return "decrease", terms
    return "unspecified", terms


# --- inputs -------------------------------------------------------------------------------------


def entering(records: list[dict]) -> list[dict]:
    return sorted((r for r in records if r["evidence_role"] in ENTERING_ROLES), key=lambda r: r["statement_id"])


def concept_lexicon(ent: list[dict], stop: frozenset) -> dict:
    """The LEXICON_TOP most frequent content unigrams per arm, by document frequency (ties: alphabetical)."""
    out = {}
    for arm in ARMS:
        rs = [r for r in ent if r["arm"] == arm]
        df = Counter(t for r in rs for t in set(content_seq(r["proposal"]["statement"], stop)))
        out[arm] = {"n_statements": len(rs), "tokens": sorted(df.items(), key=lambda x: (-x[1], x[0]))[:LEXICON_TOP]}
    return out


def df_filter(ent: list[dict], stop: frozenset) -> tuple[dict, dict]:
    """(dropped per arm: {gram: df}, idf per arm: {gram: ln(N/df)} for the kept grams)."""
    dropped, idf = {}, {}
    for arm in ARMS:
        rs = [r for r in ent if r["arm"] == arm]
        n = len(rs)
        df = Counter(g for r in rs for g in grams(r["proposal"]["statement"], stop))
        dropped[arm] = {g: c for g, c in df.items() if c / n > DF_MAX_SHARE}
        idf[arm] = {g: math.log(n / c) for g, c in df.items() if g not in dropped[arm]}
    return dropped, idf


def cosine(a: dict, b: dict) -> float:
    num = sum(a[g] * b[g] for g in sorted(a.keys() & b.keys()))
    da = math.sqrt(sum(a[g] ** 2 for g in sorted(a)))
    db = math.sqrt(sum(b[g] ** 2 for g in sorted(b)))
    return num / (da * db) if da and db else 0.0


def jaccard(a, b) -> float:
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


class Prepared:
    """Everything the clustering needs, computed once from the ingested records."""

    def __init__(self, records: list[dict]):
        self.stop, self.lex = stopwords(), direction_lexicon()
        self.ent = entering(records)
        self.by_id = {r["statement_id"]: r for r in self.ent}
        self.dropped, self.idf = df_filter(self.ent, self.stop)
        self.vec, self.direction, self.direction_terms = {}, {}, {}
        for r in self.ent:
            sid, text = r["statement_id"], r["proposal"]["statement"]
            self.vec[sid] = {g: self.idf[r["arm"]][g] for g in grams(text, self.stop) if g in self.idf[r["arm"]]}
            self.direction[sid], self.direction_terms[sid] = direction(text, self.lex)
        self.partitions = defaultdict(list)
        for r in self.ent:
            self.partitions[(r["arm"], r["proposal"]["statement_type"], self.direction[r["statement_id"]])].append(r["statement_id"])

    def sim(self, measure: str, a: str, b: str) -> float:
        if measure == "cosine":
            return cosine(self.vec[a], self.vec[b])
        return jaccard(self.vec[a], self.vec[b])  # Jaccard on the same filtered grams, for comparison


def union_find(ids: list[str], linked) -> list[list[str]]:
    parent = {i: i for i in ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in itertools.combinations(ids, 2):
        if linked(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
    groups = defaultdict(list)
    for i in ids:
        groups[find(i)].append(i)
    return sorted((sorted(g) for g in groups.values()), key=lambda g: g[0])


def clusters_at(p: Prepared, measure: str = "cosine", threshold: float = THRESHOLD) -> list[tuple[tuple, list[str]]]:
    out = []
    for key in sorted(p.partitions, key=_partition_order):
        for g in union_find(sorted(p.partitions[key]), lambda a, b: p.sim(measure, a, b) >= threshold):
            out.append((key, g))
    return out


def _partition_order(key):
    arm, stype, d = key
    return (ARMS.index(arm), STATEMENT_TYPES.index(stype), DIRECTIONS.index(d))


# --- evidence strength and cluster records ----------------------------------------------------------


def _core_cited_papers(members: list[dict]) -> list[str]:
    return sorted({m["paper_item_id"] for m in members if m["evidence_role"] in CORE_OR_CITED})


def evidence_strength(members: list[dict], meta_by_id: dict | None = None) -> str:
    if r2.n_independent(_core_cited_papers(members), meta_by_id) >= 2:
        return "multi_source_supported"
    if any(m["proposal"].get("passage_type") == "review_synthesis" for m in members):
        return "review_supported"
    if _core_cited_papers(members):
        return "single_source_supported"
    return "background_only"


def representative(p: Prepared, ids: list[str]) -> tuple[str, float | None]:
    if len(ids) == 1:
        return ids[0], None
    means = {i: sum(p.sim("cosine", i, j) for j in ids if j != i) / (len(ids) - 1) for i in ids}
    best = max(means.values())
    return min(i for i in ids if means[i] == best), round(best, 6)


def _diagnostic_groups(meta: dict) -> dict:
    """Paper id -> a canonical id, merging the papers the two independence diagnostics pair."""
    canon = {}
    for g in meta["diagnostic_same_file_sha256"] + meta["diagnostic_same_title_section"]:
        root = min(canon.get(i, i) for i in g)
        for i in g:
            canon[i] = min(canon.get(i, i), root)
    return canon


def cluster_records(p: Prepared, groups, meta: dict) -> list[dict]:
    meta_by_id = {x["item_id"]: x for x in meta["papers"]}
    canon = _diagnostic_groups(meta)
    numbering = Counter()
    out = []
    for (arm, stype, d), ids in groups:
        numbering[(arm, stype)] += 1
        members = [p.by_id[i] for i in ids]
        papers = sorted({m["paper_item_id"] for m in members})
        cc = _core_cited_papers(members)
        strength = evidence_strength(members, meta_by_id)
        rep_id, rep_sim = representative(p, ids)
        flagged = [sorted(g) for g in meta["diagnostic_same_file_sha256"] + meta["diagnostic_same_title_section"]
                   if len(set(g) & set(papers)) > 1]
        out.append({
            "cluster_id": f"LC-{arm}-{stype}-{numbering[(arm, stype)]:03d}",
            "rule": RULE_ID, "threshold": THRESHOLD, "arm": arm, "family": ARM_FAMILY[arm],
            "statement_type": stype, "direction": d,
            "member_statement_ids": ids, "n_statements": len(ids), "n_papers": len(papers), "papers": papers,
            "n_independent_papers": r2.n_independent(papers, meta_by_id),
            "n_independent_core_cited_papers": r2.n_independent(cc, meta_by_id),
            "independence_basis": meta["independence_basis"],
            "evidence_strength": strength,
            "role_counts": dict(sorted(Counter(m["evidence_role"] for m in members).items())),
            "region_scopes": dict(sorted(Counter(str(m["proposal"].get("region_scope")) for m in members).items())),
            "regions_named": sorted({m["proposal"].get("region") for m in members} - set(UNNAMED) - {None}),
            "scenarios_named": sorted({m["scenario"]["value"] for m in members} - set(UNNAMED) - {None}),
            "representative_statement": {"statement_id": rep_id, "statement": p.by_id[rep_id]["proposal"]["statement"],
                                         "paper_item_id": p.by_id[rep_id]["paper_item_id"], "mean_similarity": rep_sim},
            "diagnostic_pairs_in_cluster": flagged,
            "multi_source_relies_on_diagnostic_pair": strength == "multi_source_supported" and len({canon.get(i, i) for i in cc}) < 2,
            "members": [_member(p, m) for m in members],
        })
    return out


def _member(p: Prepared, m: dict) -> dict:
    ev = m["evidence"] or {}
    return {"statement_id": m["statement_id"], "paper_item_id": m["paper_item_id"], "paper_sha256": m["paper_sha256"],
            "json_path": ev.get("json_path"), "section_idx": ev.get("section_idx"), "span_start": ev.get("span_start"),
            "span_end": ev.get("span_end"), "recovery": m["recovery"], "passage_type": m["proposal"].get("passage_type"),
            "evidence_role": m["evidence_role"], "statement": m["proposal"]["statement"],
            "verbatim_passage": m["verbatim_passage"], "region": m["proposal"].get("region"),
            "region_scope": m["proposal"].get("region_scope"), "scenario": m["scenario"]["value"], "time": m["time"]["value"],
            "generality": m["proposal"].get("generality"), "confidence": m["proposal"].get("confidence"),
            "direction_terms": p.direction_terms[m["statement_id"]]}


# --- sensitivity -------------------------------------------------------------------------------------


def grid_row(p: Prepared, measure: str, threshold: float, meta_by_id: dict) -> dict:
    groups = clusters_at(p, measure, threshold)
    sizes = sorted((len(g) for _, g in groups), reverse=True)
    multi = sum(evidence_strength([p.by_id[i] for i in g], meta_by_id) == "multi_source_supported" for _, g in groups)
    return {"measure": measure, "threshold": threshold, "clusters": len(groups), "singletons": sizes.count(1),
            "multi_source_clusters": multi, "largest": sizes[0], "clusters_over_25": sum(s > LARGE_CLUSTER for s in sizes)}


def sensitivity(p: Prepared, meta_by_id: dict) -> list[dict]:
    return [grid_row(p, m, t, meta_by_id) for m in ("cosine", "jaccard") for t in GRID]


def rule_v1_grid(p: Prepared, lexicon: dict, meta_by_id: dict) -> list[dict]:
    """The first DR-LIT-AGG-1 (Jaccard on unigrams + merge on >= 2 shared concept-lexicon tokens), replayed."""
    lex = {arm: {t for t, _ in lexicon[arm]["tokens"]} for arm in ARMS}
    uni = {sid: frozenset(content_seq(r["proposal"]["statement"], p.stop)) for sid, r in p.by_id.items()}
    rows = []
    for th, use_lex in ((t, u) for t in V1_GRID for u in (True, False)):
        sizes, multi = [], 0
        for key in sorted(p.partitions, key=_partition_order):
            arm = key[0]
            linked = lambda a, b: jaccard(uni[a], uni[b]) >= th or (use_lex and len(uni[a] & uni[b] & lex[arm]) >= V1_LEXICON_SHARED)  # noqa: E731
            for g in union_find(sorted(p.partitions[key]), linked):
                sizes.append(len(g))
                multi += evidence_strength([p.by_id[i] for i in g], meta_by_id) == "multi_source_supported"
        sizes.sort(reverse=True)
        rows.append({"threshold": th, "concept_lexicon_merge": use_lex, "clusters": len(sizes), "singletons": sizes.count(1),
                     "multi_source_clusters": multi, "largest": sizes[0], "five_largest": sizes[:5]})
    return rows


# --- summary ---------------------------------------------------------------------------------------


def summarise(clusters: list[dict], p: Prepared, meta: dict, lexicon: dict) -> dict:
    meta_by_id = {x["item_id"]: x for x in meta["papers"]}
    by = Counter((c["arm"], c["statement_type"], c["evidence_strength"]) for c in clusters)
    table = [{"arm": a, "statement_type": t, **{s: by.get((a, t, s), 0) for s in STRENGTHS}}
             for a in ARMS for t in STATEMENT_TYPES]
    largest = sorted(clusters, key=lambda c: (-c["n_statements"], -c["n_papers"], c["cluster_id"]))[:10]
    return {
        "version": VERSION, "rule": RULE_ID, "threshold": THRESHOLD, "df_max_share": DF_MAX_SHARE,
        "inputs": {"statements_ingested": {"path": "artifacts/litstatements/run2/statements_ingested.jsonl",
                                           "sha256": sha256_file(r2.INGESTED_PATH)},
                   "papers_meta": {"path": "artifacts/litstatements/run2/papers_meta.json", "sha256": sha256_file(r2.PAPERS_META_PATH)}},
        "lexicons": {name: {"path": path.relative_to(REPO_ROOT).as_posix(), "sha256": sha256_file(path)}
                     for name, path in (("direction_lexicon", DIRECTION_LEXICON), ("stopwords", STOPWORDS),
                                        ("concept_lexicon", CONCEPT_LEXICON), ("df_filter_dropped", DF_DROPPED))},
        "clusters_file": {"path": "artifacts/litstatements/run2/clusters_v1.jsonl", "sha256": sha256_file(CLUSTERS_PATH)},
        "entering_statements": len(p.ent),
        "entering_by_arm": {a: sum(r["arm"] == a for r in p.ent) for a in ARMS},
        "entering_by_role": {k: sum(r["evidence_role"] == k for r in p.ent) for k in ENTERING_ROLES},
        "partitions": [{"arm": k[0], "statement_type": k[1], "direction": k[2], "n_statements": len(v)}
                       for k, v in sorted(p.partitions.items(), key=lambda kv: _partition_order(kv[0]))],
        "df_dropped": {a: dict(sorted(p.dropped[a].items(), key=lambda x: (-x[1], x[0]))) for a in ARMS},
        "clusters": len(clusters),
        "singletons": sum(c["n_statements"] == 1 for c in clusters),
        "by_strength": {s: sum(c["evidence_strength"] == s for c in clusters) for s in STRENGTHS},
        "multi_source_supported": sum(c["evidence_strength"] == "multi_source_supported" for c in clusters),
        "multi_source_relies_on_diagnostic_pair": [c["cluster_id"] for c in clusters if c["multi_source_relies_on_diagnostic_pair"]],
        "by_arm_type_strength": table,
        "largest": [{"cluster_id": c["cluster_id"], "n_statements": c["n_statements"], "n_papers": c["n_papers"],
                     "n_independent_papers": c["n_independent_papers"], "evidence_strength": c["evidence_strength"],
                     "direction": c["direction"], "representative": c["representative_statement"]["statement"],
                     "representative_id": c["representative_statement"]["statement_id"]} for c in largest],
        "sensitivity": sensitivity(p, meta_by_id),
        "rule_v1_degeneracy": rule_v1_grid(p, lexicon, meta_by_id),
    }


# --- generated lexicon files ---------------------------------------------------------------------------


def _q(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def render_concept_lexicon(lexicon: dict, ingested_sha: str) -> str:
    lines = ["# Concept lexicon v1 --- GENERATED by scripts/aggregate_litstatements.py (pilot P2a; D-045). Do not edit.",
             "#",
             "# A frequency fact about the run-2 statements, not a meaning assignment: for each arm, the",
             f"# {LEXICON_TOP} most frequent content unigrams (DR-LIT-AGG-1 v2 step 2 tokens) over the arm's entering",
             "# statements (core / cited / background_consensus candidates), with their document frequency",
             "# (statements containing the term); ties broken alphabetically. NOT used for merging (v2 dropped the",
             "# concept-lexicon merge of the first rule).",
             "",
             "version: concept_lexicon_v1",
             "used_for_merging: false",
             f"built_from: {_q('artifacts/litstatements/run2/statements_ingested.jsonl')}",
             f"built_from_sha256: {ingested_sha}",
             "count: document_frequency",
             "arms:"]
    for arm in ARMS:
        lines += [f"  {arm}:", f"    n_statements: {lexicon[arm]['n_statements']}", "    tokens:"]
        lines += [f"      - {{term: {_q(t)}, count: {c}}}" for t, c in lexicon[arm]["tokens"]]
    return "\n".join(lines) + "\n"


def render_df_dropped(p: Prepared, ingested_sha: str) -> str:
    lines = ["# Document-frequency filter, dropped grams v1 --- GENERATED by scripts/aggregate_litstatements.py",
             "# (pilot P2a; DR-LIT-AGG-1 v2 step 3; D-045). Do not edit.",
             "#",
             f"# Within each arm, every content unigram or bigram in more than {DF_MAX_SHARE:.0%} of the arm's entering",
             "# statements, with its document frequency and share. These grams carry no weight in the similarity.",
             "",
             "version: df_filter_dropped_v1",
             f"df_max_share: {DF_MAX_SHARE}",
             f"built_from: {_q('artifacts/litstatements/run2/statements_ingested.jsonl')}",
             f"built_from_sha256: {ingested_sha}",
             "arms:"]
    for arm in ARMS:
        n = sum(r["arm"] == arm for r in p.ent)
        lines += [f"  {arm}:", f"    n_statements: {n}", "    dropped:"]
        lines += [f"      - {{gram: {_q(g)}, df: {c}, share: {c / n:.4f}}}"
                  for g, c in sorted(p.dropped[arm].items(), key=lambda x: (-x[1], x[0]))]
    return "\n".join(lines) + "\n"
