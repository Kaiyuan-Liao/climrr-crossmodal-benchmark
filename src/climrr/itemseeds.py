"""Item seeds: deterministic pairing of table patterns with literature-statement clusters (pilot P2a; DR-SEED-1, D-045).

A seed is one table pattern (`artifacts/benchmark/table_patterns_v1.jsonl`, single,
seasonal contrast or regional contrast) plus the clusters (`clusters_v1.jsonl`,
DR-LIT-AGG-1 v2) that could explain it. **DR-SEED-1**:

- *family*: heat_index <-> arm `extreme_heat_v1`; fire_weather_index <-> `fire_weather_v1`;
- *direction*: the cluster's direction equals the pattern's, or is `unspecified` (a
  `mixed` pattern therefore pairs only with `unspecified` clusters);
- *geography*: a cluster is `geography_relevant` if any member's `region` string names the
  pattern's place or the scope is global / national, else `geography_other` (still
  listed). A string names a place when, after removing periods, lowercasing and
  replacing every other character outside [a-z0-9] by a space, it contains the place
  name as whole words. The places: a state pattern's state and its NCA5 region name
  (`nca_regions_v1.yaml`); a region pattern's region name; a regional contrast's covered
  region names; for every pattern "United States", "US", "CONUS", "contiguous". The control
  cell names no state (its pattern record carries none). The first basis that matches is
  recorded (`state` > `nca_region` > `us_term` > `scope`);
- *rank* per seed: evidence strength (multi > review > single > background), relevant
  before other, more independent papers first; then (EXECUTOR tie-break) more
  statements, then cluster id.

`use_case_level` (D-038 rungs; ladder `proposed`), first that applies: a regional
contrast with >= 1 paired cluster -> 4; >= 1 mechanism / driver cluster -> 3; >= 1 caveat
cluster naming a scenario -> 7; else 1. All levels that apply are listed too.
Each seed's `clusters[]` gives the full reference (rank, type, relevance, basis, strength,
independent papers) for its top 20 clusters; `paired_cluster_ids` lists every paired
cluster in rank order. `eligibility_relies_on_diagnostic_pair` marks a seed whose every
qualifying cluster is multi-source only through a pair of papers the independence
diagnostics link (equal file hash or title); `eligible_for_pilot_excluding_diagnostic_pairs`
is the eligibility without such clusters. Neither changes DR-SEED-1.
`acceptance_blockers[]` copies the pattern's `acceptance_blocked_by` (inferred_candidate FWI
columns, IC-006..IC-010) and its provisional-State reason (IC-012). **Eligible for the
pilot**: the pattern is not `acceptance_blocked`, it is computed (EXECUTOR: a
`not_computable` pattern has no value), and >= 1 `multi_source_supported` mechanism / driver
cluster is geography_relevant. The provisional State label is carried as a blocker but
does not by itself remove eligibility (D-034).

**Seed order** (EXECUTOR-defined; the work package ranks clusters, not seeds): more
eligible clusters first, then the rank keys of the top three clusters, then pattern id.

No model call, no table value computed here (values are copied from the pattern).
"""

from __future__ import annotations

import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

import yaml

from climrr import litaggregate as la
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

VERSION = "itemseeds v1"
RULE_ID = "DR-SEED-1"
PATTERNS_PATH = REPO_ROOT / "artifacts" / "benchmark" / "table_patterns_v1.jsonl"
PATTERNS_SHA256 = "ed3c2154818fc363e982b17e0dcb9bb1a2d2ca25e18de97fda6d353974bbf3b0"
NCA_MAP_PATH = REPO_ROOT / "data" / "metadata" / "geography" / "nca_regions_v1.yaml"
NCA_MAP_SHA256 = "3141b12201cd5a8d25789182688e69ed3792f4fa56ca667994247c82bf949a41"
SEEDS_PATH = REPO_ROOT / "artifacts" / "benchmark" / "item_seeds_v1.jsonl"
SUMMARY_PATH = REPO_ROOT / "artifacts" / "benchmark" / "item_seeds_v1_summary.json"

FAMILY_ARM = {"heat_index": "extreme_heat_v1", "fire_weather_index": "fire_weather_v1"}
US_TERMS = ("united states", "us", "conus", "contiguous")
RELEVANT_SCOPES = ("global", "national")
STRENGTH_ORDER = {s: i for i, s in enumerate(la.STRENGTHS)}
EXPLAINING = ("mechanism", "driver")
TOP_REFS = 20  # clusters[] carries the full reference for the top 20; paired_cluster_ids lists every paired cluster
LEVELS = {1: "hazard pattern identification", 3: "pattern + mechanism", 4: "regional comparison",
          7: "scenario and uncertainty"}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]


def nca_map() -> dict:
    d = yaml.safe_load(NCA_MAP_PATH.read_text(encoding="utf-8"))
    return {"region_name": {r["region_id"]: r["name"] for r in d["regions"]}, "state_region": d["state_to_region_map"]}


def place_norm(s: str) -> str:
    return " " + " ".join(re.sub(r"[^a-z0-9]+", " ", s.replace(".", "").lower()).split()) + " "


def pattern_places(p: dict, nca: dict) -> dict:
    """{'state': [...], 'nca_region': [...]} --- the names a region string may match (DR-SEED-1)."""
    gt, geo = p["geography_type"], p["geography"]
    if p["pattern_kind"] == "regional_contrast":
        return {"state": [], "nca_region": sorted({r["name"] for r in p["computed_value_or_range"]["regions_ordered"]})}
    if gt == "state":
        rid = nca["state_region"].get(geo)
        return {"state": [geo], "nca_region": [nca["region_name"][rid]] if rid else []}
    if gt == "nca_region":
        return {"state": [], "nca_region": [nca["region_name"][geo]]}
    return {"state": [], "nca_region": []}


def geography_match(cluster: dict, places: dict) -> tuple[str, str | None]:
    """('geography_relevant' | 'geography_other', basis)."""
    regions = [place_norm(m["region"]) for m in cluster["members"] if m.get("region")]
    for kind in ("state", "nca_region"):
        for name in places[kind]:
            if any(place_norm(name) in r for r in regions):
                return "geography_relevant", f"{kind}:{name}"
    for t in US_TERMS:
        if any(f" {t} " in r for r in regions):
            return "geography_relevant", f"us_term:{t}"
    for sc in RELEVANT_SCOPES:
        if any(m.get("region_scope") == sc for m in cluster["members"]):
            return "geography_relevant", f"scope:{sc}"
    return "geography_other", None


def cluster_key(c: dict, relevance: str) -> tuple:
    return (STRENGTH_ORDER[c["evidence_strength"]], 0 if relevance == "geography_relevant" else 1,
            -c["n_independent_papers"], -c["n_statements"], c["cluster_id"])


def caveat_on_scenario(c: dict) -> bool:
    return c["statement_type"] == "caveat" and bool(c["scenarios_named"])


def levels(p: dict, paired: list[dict]) -> list[int]:
    out = []
    if p["pattern_kind"] == "regional_contrast" and paired:
        out.append(4)
    if any(c["statement_type"] in EXPLAINING for c in paired):
        out.append(3)
    if any(caveat_on_scenario(c) for c in paired):
        out.append(7)
    return out or [1]


def blockers(p: dict) -> list[dict]:
    out = [{"blocker": ic, "kind": "inferred_candidate_fwi_column", "blocks_eligibility": True}
           for ic in p.get("acceptance_blocked_by") or []]
    out += [{"blocker": "IC-012", "kind": "provisional_state_label", "blocks_eligibility": False, "reason": r}
            for r in p.get("provisional_reasons") or [] if "IC-012" in r]
    return out


def summary_line(p: dict) -> str:
    v = p["computed_value_or_range"]
    geo = p["geography"]
    val = v.get("value")
    rng = v.get("range")
    parts = [f"{p['pattern_id']} {p['pattern_kind']} {p['family']} {p['metric']}", f"{p['geography_type']} {geo}",
             f"{p['season']} {p['horizon']} ({p['horizon_window']}) {p['scenario']}", f"{p['statistic']}: {p['direction']}"]
    if val is not None:
        parts.append(f"value {val} {v.get('unit', '')}".rstrip())
    if rng:
        parts.append(f"range {rng['min']}..{rng['max']} over {rng['over']}")
    if p["pattern_kind"] == "regional_contrast":
        parts.append("order " + " > ".join(r["name"] for r in v["regions_ordered"]))
    return "; ".join(parts)


class Pairing:
    def __init__(self, clusters: list[dict], nca: dict):
        self.clusters, self.nca = clusters, nca
        self.by_id = {c["cluster_id"]: c for c in clusters}
        self.relied = {c["cluster_id"] for c in clusters if c["multi_source_relies_on_diagnostic_pair"]}

    @lru_cache(maxsize=None)
    def ranked(self, arm: str, direction: str, places_key: tuple) -> tuple:
        places = {"state": list(places_key[0]), "nca_region": list(places_key[1])}
        rows = []
        for c in self.clusters:
            if c["arm"] != arm or c["direction"] not in (direction, "unspecified"):
                continue
            rel, basis = geography_match(c, places)
            rows.append((cluster_key(c, rel), c["cluster_id"], rel, basis))
        rows.sort()
        return tuple(rows)

    def seed(self, p: dict) -> dict:
        places = pattern_places(p, self.nca)
        rows = self.ranked(FAMILY_ARM[p["family"]], p["direction"], (tuple(places["state"]), tuple(places["nca_region"])))
        paired = [self.by_id[cid] for _, cid, _, _ in rows]
        refs = [{"cluster_id": cid, "rank": i, "statement_type": self.by_id[cid]["statement_type"], "relevance": rel,
                 "geography_match": basis, "evidence_strength": self.by_id[cid]["evidence_strength"],
                 "n_independent_papers": self.by_id[cid]["n_independent_papers"]}
                for i, (_, cid, rel, basis) in enumerate(rows, 1)]
        qualifying = [r["cluster_id"] for r in refs if r["evidence_strength"] == "multi_source_supported"
                      and r["statement_type"] in EXPLAINING and r["relevance"] == "geography_relevant"]
        basis_counts = Counter((r["geography_match"] or "none").split(":")[0] for r in refs)
        computed = p.get("status", "computed") == "computed"
        lv = levels(p, paired)
        eligible = (not p["acceptance_blocked"]) and computed and bool(qualifying)
        return {
            "seed_id": f"SD1-{p['pattern_id']}", "rule": RULE_ID, "version": VERSION,
            "use_case_level": lv[0], "use_case_levels_applicable": lv, "use_case_level_name": LEVELS[lv[0]],
            "family": p["family"], "arm": FAMILY_ARM[p["family"]], "pattern_kind": p["pattern_kind"],
            "geography_type": p["geography_type"], "geography": p["geography"], "places_matched_against": places,
            "season": p["season"], "horizon": p["horizon"], "horizon_window": p["horizon_window"], "scenario": p["scenario"],
            "statistic": p["statistic"], "direction": p["direction"], "pattern_summary": summary_line(p),
            "pattern": p, "n_clusters_paired": len(refs),
            "n_geography_relevant": sum(r["relevance"] == "geography_relevant" for r in refs),
            "geography_match_basis_counts": dict(sorted(basis_counts.items())),
            "clusters": refs[:TOP_REFS], "paired_cluster_ids": [r["cluster_id"] for r in refs], "eligible_clusters": qualifying,
            "acceptance_blockers": blockers(p), "acceptance_blocked": p["acceptance_blocked"], "pattern_computed": computed,
            "eligible_for_pilot": eligible,
            "eligibility_relies_on_diagnostic_pair": eligible and all(cid in self.relied for cid in qualifying),
            "eligible_for_pilot_excluding_diagnostic_pairs": eligible and any(cid not in self.relied for cid in qualifying),
            "seed_rank_key": None,
        }


def seed_order_key(s: dict, by_id: dict) -> tuple:
    top = tuple(cluster_key(by_id[r["cluster_id"]], r["relevance"])[:4] for r in s["clusters"][:3])
    return (-len(s["eligible_clusters"]), top, s["pattern"]["pattern_id"])


def build(patterns: list[dict], clusters: list[dict], nca: dict) -> list[dict]:
    pr = Pairing(clusters, nca)
    seeds = [pr.seed(p) for p in patterns]
    order = sorted(range(len(seeds)), key=lambda i: seed_order_key(seeds[i], pr.by_id))
    for rank, i in enumerate(order, 1):
        seeds[i]["seed_rank_key"] = rank
    return seeds


def match_audit(clusters: list[dict], nca: dict) -> dict:
    """Every distinct member region string a DR-SEED-1 place name or US term matches, and the clusters that are
    relevant to a pattern only through a global / national scope (no US place named by any member)."""
    names = sorted(set(nca["state_region"]) | set(nca["region_name"].values()))
    regions = sorted({m["region"] for c in clusters for m in c["members"] if m.get("region")})
    by_name = {n: [r for r in regions if place_norm(n) in place_norm(r)] for n in names}
    by_term = {t: [r for r in regions if f" {t} " in place_norm(r)] for t in US_TERMS}
    us_named = {r for v in list(by_name.values()) + list(by_term.values()) for r in v}
    scope_only = [c for c in clusters if not any(m.get("region") in us_named for m in c["members"])
                  and any(m.get("region_scope") in RELEVANT_SCOPES for m in c["members"])]
    return {"place_names": {n: v for n, v in by_name.items() if v}, "us_terms": by_term,
            "scope_only_clusters": len(scope_only),
            "scope_only_by_strength": dict(sorted(Counter(c["evidence_strength"] for c in scope_only).items())),
            "scope_only_multi_source": sorted(c["cluster_id"] for c in scope_only if c["evidence_strength"] == "multi_source_supported")}


def summarise(seeds: list[dict], clusters: list[dict], nca: dict | None = None) -> dict:
    elig = [s for s in seeds if s["eligible_for_pilot"]]
    fwi = [s for s in seeds if s["family"] == "fire_weather_index"]
    rel_basis = Counter()
    for s in seeds:
        rel_basis.update(s["geography_match_basis_counts"])
    return {
        "version": VERSION, "rule": RULE_ID,
        "inputs": {"table_patterns": {"path": "artifacts/benchmark/table_patterns_v1.jsonl", "sha256": PATTERNS_SHA256},
                   "clusters": {"path": "artifacts/litstatements/run2/clusters_v1.jsonl", "sha256": sha256_file(la.CLUSTERS_PATH)},
                   "nca_map": {"path": "data/metadata/geography/nca_regions_v1.yaml", "sha256": NCA_MAP_SHA256}},
        "seeds_file": {"path": "artifacts/benchmark/item_seeds_v1.jsonl", "sha256": sha256_file(SEEDS_PATH), "gitignored": True},
        "seeds": len(seeds), "eligible": len(elig),
        "eligible_without_diagnostic_pair": sum(s["eligible_for_pilot_excluding_diagnostic_pairs"] for s in elig),
        "eligible_not_computable_excluded": sum((not s["pattern_computed"]) and (not s["acceptance_blocked"]) and bool(s["eligible_clusters"]) for s in seeds),
        "by_level": dict(sorted(Counter(s["use_case_level"] for s in seeds).items())),
        "levels_applicable": dict(sorted(Counter(lv for s in seeds for lv in s["use_case_levels_applicable"]).items())),
        "eligible_by_level": dict(sorted(Counter(s["use_case_level"] for s in elig).items())),
        "by_family": dict(sorted(Counter(s["family"] for s in seeds).items())),
        "eligible_by_family": dict(sorted(Counter(s["family"] for s in elig).items())),
        "by_kind": dict(sorted(Counter(s["pattern_kind"] for s in seeds).items())),
        "eligible_by_kind": dict(sorted(Counter(s["pattern_kind"] for s in elig).items())),
        "eligible_by_geography_type": dict(sorted(Counter(s["geography_type"] for s in elig).items())),
        "fwi": {"seeds": len(fwi), "acceptance_blocked": sum(s["acceptance_blocked"] for s in fwi),
                "not_blocked": sum(not s["acceptance_blocked"] for s in fwi), "eligible": sum(s["eligible_for_pilot"] for s in fwi)},
        "eligible_cluster_ids": dict(sorted(Counter(c for s in elig for c in s["eligible_clusters"]).items())),
        "geography_match_basis_counts": dict(sorted(rel_basis.items())),
        "multi_source_explaining_clusters": [c["cluster_id"] for c in clusters if c["evidence_strength"] == "multi_source_supported"
                                             and c["statement_type"] in EXPLAINING],
        "geography_match_audit": match_audit(clusters, nca or nca_map()),
        "top_eligible": [top_entry(s, clusters) for s in sorted(elig, key=lambda s: s["seed_rank_key"])[:10]],
    }


def top_entry(s: dict, clusters: list[dict]) -> dict:
    by_id = {c["cluster_id"]: c for c in clusters}
    return {"seed_id": s["seed_id"], "seed_rank_key": s["seed_rank_key"], "use_case_level": s["use_case_level"],
            "pattern_summary": s["pattern_summary"], "acceptance_blockers": [b["blocker"] for b in s["acceptance_blockers"]],
            "eligibility_relies_on_diagnostic_pair": s["eligibility_relies_on_diagnostic_pair"],
            "top_clusters": [{"cluster_id": r["cluster_id"], "rank": r["rank"], "evidence_strength": r["evidence_strength"],
                              "relevance": r["relevance"], "geography_match": r["geography_match"],
                              "n_papers": by_id[r["cluster_id"]]["n_papers"],
                              "representative": by_id[r["cluster_id"]]["representative_statement"]["statement"]}
                             for r in s["clusters"][:3]]}
