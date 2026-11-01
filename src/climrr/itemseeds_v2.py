"""Item seeds v2: table patterns paired with geography-relevant literature statements (DR-SEED-1 v2; D-046--D-048).

Changes from v1 (`itemseeds.py`, D-045), by the COORDINATOR rulings of 2026-11-01:

- **Geography** (D-047): each statement is classified by `litgeo.classify` and is relevant to
  a pattern by `litgeo.relevance` --- a scope alone is relevant only when `global`; a
  non-U.S. national scope no longer makes a statement relevant.
- **Eligibility** (D-048): the pattern is not `acceptance_blocked`, it is computed, and >= 1
  geography-relevant **mechanism / driver statement of any strength** pairs with it.
  Strength ranks, it does not gate. Statements, not clusters, carry eligibility: clusters
  v1 are a lexical baseline kept as diagnostic evidence; grouping for the pilot is
  agent-proposed (`litgroup_agent.py`) and human-checked.
- **Strength** is the statement's v1b cluster strength (`clusters_v1b.jsonl`: the v1 members
  with D-046 independence).

Kept from DR-SEED-1: family pairing (heat_index <-> `extreme_heat_v1`, fire_weather_index <->
`fire_weather_v1`); direction pairing (the statement's lexical direction, DR-LIT-AGG-1 v2 step 1,
equals the pattern's or is `unspecified`); the entering statements (core / cited /
background_consensus candidates); the IC-012 provisional State label carried as a
non-blocking blocker (D-034); a `not_computable` pattern is not eligible.

**EXECUTOR choices (recorded for COORDINATOR confirmation):**

- *Statement rank within a seed*: cluster strength (multi > review > single > background),
  relevance basis (state > nca_region > us_national > global), role (core > cited >
  background), statement id.
- *Seed rank*: best strength among the relevant mechanism / driver statements; then more such
  statements matched by state or NCA region name; then more independent (D-046) papers with
  core / cited relevant mechanism / driver statements; then more relevant mechanism / driver
  statements; then pattern id. Ineligible seeds follow all eligible ones.
- *Levels* (D-038 rungs, ladder `proposed`): 4 if a regional contrast has a relevant
  mechanism / driver statement; 3 if any pattern has one; 7 if a relevant caveat statement
  names a scenario; and 1 for every computed pattern (pattern identification needs no
  literature). `use_case_level` is the first that applies. v1 listed 1 only as a fallback.
- An NCA5-region pattern matches region names only (not its member states' names), as in v1.

No model call, no table value computed here (values are copied from the pattern).
"""

from __future__ import annotations

from collections import Counter

from climrr import itemseeds as sd
from climrr import litaggregate as la
from climrr import litgeo as lg
from climrr import litindependence as li
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

VERSION = "itemseeds v2"
RULE_ID = "DR-SEED-1 v2"
DECISIONS = ("D-046", "D-047", "D-048")
SEEDS_PATH = REPO_ROOT / "artifacts" / "benchmark" / "item_seeds_v2.jsonl"
SUMMARY_PATH = REPO_ROOT / "artifacts" / "benchmark" / "item_seeds_v2_summary.json"
REGION_CSV_PATH = la.r2.ART / "region_strings_v1.csv"
ROLE_ORDER = {r: i for i, r in enumerate(la.ENTERING_ROLES)}
BASIS_RANK = {b: i for i, b in enumerate(lg.BASIS_ORDER)}
ROLE_SHORT = {"core_candidate": "core", "cited_candidate": "cited", "background_consensus_candidate": "background"}
EXPLAINING = sd.EXPLAINING
TOP_STATEMENTS = 30


def statement_table(records: list[dict], clusters_v1b: list[dict], indep: dict, gz: lg.Gazetteer) -> list[dict]:
    """One row per entering statement: geography, direction, cluster and its v1b strength."""
    p = la.Prepared(records)
    canon = li.canonical_map(indep)
    cl_of = {m["statement_id"]: c for c in clusters_v1b for m in c["members"]}
    rows = []
    for r in p.ent:
        sid, pr = r["statement_id"], r["proposal"]
        c = cl_of[sid]
        rows.append({"statement_id": sid, "arm": r["arm"], "statement_type": pr["statement_type"],
                     "evidence_role": r["evidence_role"], "role": ROLE_SHORT[r["evidence_role"]],
                     "paper_item_id": r["paper_item_id"], "canonical_paper": canon.get(r["paper_item_id"], r["paper_item_id"]),
                     "direction": p.direction[sid], "statement": pr["statement"], "region": pr.get("region"),
                     "region_scope": pr.get("region_scope"), "scenario": r["scenario"]["value"],
                     "passage_type": pr.get("passage_type"), "geo": lg.classify(pr.get("region"), pr.get("region_scope"), gz),
                     "cluster_id": c["cluster_id"], "cluster_strength": c["evidence_strength"]})
    return rows


def _brief(row: dict, basis: str) -> dict:
    return {"statement_id": row["statement_id"], "statement_type": row["statement_type"], "role": row["role"], "basis": basis,
            "cluster_strength": row["cluster_strength"], "scenario": row["scenario"], "statement": row["statement"]}


def scenario_named(row: dict) -> bool:
    return row["scenario"] not in la.UNNAMED and row["scenario"] is not None


def statement_key(row: dict, basis: str) -> tuple:
    return (sd.STRENGTH_ORDER[row["cluster_strength"]], BASIS_RANK[basis], ROLE_ORDER[row["evidence_role"]], row["statement_id"])


class Pairing:
    def __init__(self, rows: list[dict], clusters_v1b: list[dict], nca: dict, canon: dict):
        self.rows, self.nca, self.canon = rows, nca, canon
        self.clusters = {c["cluster_id"]: c for c in clusters_v1b}
        self.by_arm: dict[str, list[dict]] = {}
        for r in rows:
            self.by_arm.setdefault(r["arm"], []).append(r)

    def seed(self, p: dict) -> dict:
        places = sd.pattern_places(p, self.nca)
        rel = []
        for r in self.by_arm.get(sd.FAMILY_ARM[p["family"]], []):
            if r["direction"] not in (p["direction"], "unspecified"):
                continue
            basis = lg.relevance(r["geo"], places)
            if basis:
                rel.append((statement_key(r, basis), r, basis))
        rel.sort(key=lambda x: x[0])
        expl = [(k, r, b) for k, r, b in rel if r["statement_type"] in EXPLAINING]
        cav = [r for _, r, _ in rel if r["statement_type"] == "caveat" and scenario_named(r)]
        computed = p.get("status", "computed") == "computed"
        lv = ([4] if p["pattern_kind"] == "regional_contrast" and expl else []) + ([3] if expl else []) + \
             ([7] if cav else []) + [1]
        eligible = (not p["acceptance_blocked"]) and computed and bool(expl)
        cc_papers = {r["canonical_paper"] for _, r, _ in expl if r["evidence_role"] in la.CORE_OR_CITED}
        cl_ids = []
        for _, r, _ in rel:
            if r["cluster_id"] not in cl_ids:
                cl_ids.append(r["cluster_id"])
        return {
            "seed_id": f"SD2-{p['pattern_id']}", "rule": RULE_ID, "version": VERSION, "decisions": list(DECISIONS),
            "use_case_level": lv[0], "use_case_levels_applicable": lv, "use_case_level_name": sd.LEVELS[lv[0]],
            "family": p["family"], "arm": sd.FAMILY_ARM[p["family"]], "pattern_kind": p["pattern_kind"],
            "geography_type": p["geography_type"], "geography": p["geography"], "places_matched_against": places,
            "metric": p["metric"], "season": p["season"], "horizon": p["horizon"], "horizon_window": p["horizon_window"],
            "scenario": p["scenario"], "statistic": p["statistic"], "direction": p["direction"],
            "has_relative_tercile": bool(p.get("relative_magnitude")),
            "pattern_summary": sd.summary_line(p), "pattern": p,
            "n_relevant_statements": len(rel),
            "n_relevant_by_role": {k: sum(r["role"] == k for _, r, _ in rel) for k in ("core", "cited", "background")},
            "n_relevant_by_basis": {b: sum(x == b for _, _, x in rel) for b in lg.BASIS_ORDER},
            "n_relevant_explaining": len(expl),
            "n_relevant_explaining_by_role": {k: sum(r["role"] == k for _, r, _ in expl) for k in ("core", "cited", "background")},
            "n_relevant_explaining_specific": sum(b in ("state", "nca_region") for _, _, b in expl),
            "n_independent_papers_explaining_core_cited": len(cc_papers),
            "best_explaining_strength": expl[0][1]["cluster_strength"] if expl else None,
            "n_relevant_scenario_caveats": len(cav),
            "relevant_statements": [{"statement_id": r["statement_id"], "statement_type": r["statement_type"], "role": r["role"],
                                     "basis": b, "classification": r["geo"]["classification"], "cluster_id": r["cluster_id"],
                                     "cluster_strength": r["cluster_strength"], "paper_item_id": r["paper_item_id"],
                                     "statement": r["statement"]} for _, r, b in rel[:TOP_STATEMENTS]],
            "relevant_statement_ids": [r["statement_id"] for _, r, _ in rel],
            "top_explaining": [_brief(r, b) for _, r, b in expl[:3]],
            "top_explaining_named_place": [_brief(r, b) for _, r, b in expl if b in ("state", "nca_region")][:3],
            "top_scenario_caveats": [_brief(r, b) for _, r, b in rel if r["statement_type"] == "caveat" and scenario_named(r)][:3],
            "relevant_cluster_ids_v1b": cl_ids,
            "acceptance_blockers": sd.blockers(p), "acceptance_blocked": p["acceptance_blocked"], "pattern_computed": computed,
            "eligible_for_pilot": eligible, "seed_rank_key": None,
        }


def seed_order_key(s: dict) -> tuple:
    if not s["eligible_for_pilot"]:
        return (1, 99, 0, 0, 0, s["pattern"]["pattern_id"])
    return (0, sd.STRENGTH_ORDER[s["best_explaining_strength"]], -s["n_relevant_explaining_specific"],
            -s["n_independent_papers_explaining_core_cited"], -s["n_relevant_explaining"], s["pattern"]["pattern_id"])


def build(patterns: list[dict], rows: list[dict], clusters_v1b: list[dict], nca: dict, indep: dict) -> list[dict]:
    pr = Pairing(rows, clusters_v1b, nca, li.canonical_map(indep))
    seeds = [pr.seed(p) for p in patterns]
    for rank, i in enumerate(sorted(range(len(seeds)), key=lambda i: seed_order_key(seeds[i])), 1):
        seeds[i]["seed_rank_key"] = rank
    return seeds


# --- summary ---------------------------------------------------------------------------------


def _state_of(s: dict) -> str:
    return s["geography"] if s["geography_type"] == "state" else f"{s['geography_type']}:{s['geography']}"


def statement_geography(rows: list[dict], seeds: list[dict]) -> dict:
    relevant_any = {sid for s in seeds for sid in s["relevant_statement_ids"]}
    table = []
    for arm in la.ARMS:
        for t in la.STATEMENT_TYPES:
            rs = [r for r in rows if r["arm"] == arm and r["statement_type"] == t]
            cls = Counter(r["geo"]["class"] for r in rs)
            table.append({"arm": arm, "statement_type": t, "entering": len(rs),
                          **{c: cls.get(c, 0) for c in lg.CLASSES},
                          "us_relevant_distinct": sum(r["geo"]["class"] in ("us_national", "state", "nca") for r in rs),
                          "relevant_to_some_pattern": sum(r["statement_id"] in relevant_any for r in rs)})
    named = [r for r in rows if r["geo"]["class"] in ("state", "nca")]
    return {
        "entering_statements": len(rows),
        "by_class": {c: sum(r["geo"]["class"] == c for r in rows) for c in lg.CLASSES},
        "named_state_or_nca_region": len(named),
        "named_state_or_nca_region_by_role": dict(sorted(Counter(r["role"] for r in named).items())),
        "relevant_to_at_least_one_pattern": len(relevant_any),
        "relevant_to_at_least_one_state_or_region_pattern": len({sid for s in seeds if s["geography_type"] in ("state", "nca_region")
                                                                 for sid in s["relevant_statement_ids"]}),
        "states_named": dict(sorted(Counter(st for r in rows for st in r["geo"]["states"]).items())),
        "nca_regions_named": dict(sorted(Counter(n for r in rows for n in r["geo"]["nca_regions"]).items())),
        "us_gazetteer_string_but_subnational_or_local": sum(bool(r["geo"]["us_gazetteer_in_string"]) and r["region_scope"] in ("subnational", "local")
                                                            and r["geo"]["class"] == "other" for r in rows),
        "by_arm_type": table,
    }


def summarise(seeds: list[dict], rows: list[dict], region_rows: list[dict], v1_summary: dict | None = None) -> dict:
    elig = [s for s in seeds if s["eligible_for_pilot"]]
    hi = [s for s in elig if s["family"] == "heat_index"]
    cls_strings = Counter(r["class"] for r in region_rows)
    return {
        "version": VERSION, "rule": RULE_ID, "decisions": list(DECISIONS),
        "inputs": {"table_patterns": {"path": "artifacts/benchmark/table_patterns_v1.jsonl", "sha256": sd.PATTERNS_SHA256},
                   "statements_ingested": {"path": "artifacts/litstatements/run2/statements_ingested.jsonl", "sha256": sha256_file(la.r2.INGESTED_PATH)},
                   "clusters_v1b": {"path": "artifacts/litstatements/run2/clusters_v1b.jsonl", "sha256": sha256_file(li.CLUSTERS_V1B_PATH)},
                   "independence_v2": {"path": "artifacts/litstatements/run2/independence_v2.json", "sha256": sha256_file(li.INDEPENDENCE_PATH)},
                   "nca_map": {"path": "data/metadata/geography/nca_regions_v1.yaml", "sha256": sd.NCA_MAP_SHA256},
                   "exclusions": {"path": "data/metadata/geography/region_match_exclusions_v1.yaml", "sha256": sha256_file(lg.EXCLUSIONS_PATH)}},
        "seeds_file": {"path": "artifacts/benchmark/item_seeds_v2.jsonl", "sha256": sha256_file(SEEDS_PATH), "gitignored": True},
        "region_strings_file": {"path": "artifacts/litstatements/run2/region_strings_v1.csv", "sha256": sha256_file(REGION_CSV_PATH),
                                "rows_region_x_scope": len(region_rows), "distinct_region_strings": len({r["region"] for r in region_rows})},
        "region_string_classification": {
            "rows_by_class": {c: cls_strings.get(c, 0) for c in lg.CLASSES},
            "distinct_strings_by_class": {c: len({r["region"] for r in region_rows if r["class"] == c}) for c in lg.CLASSES},
            "statements_by_class": {c: sum(r["count"] for r in region_rows if r["class"] == c) for c in lg.CLASSES},
            "other_examples": [r["region"] for r in sorted((r for r in region_rows if r["class"] == "other"),
                                                           key=lambda r: (-r["count"], r["region"]))][:10]},
        "statement_geography": statement_geography(rows, seeds),
        "seeds": len(seeds), "eligible": len(elig),
        "eligible_v1": (v1_summary or {}).get("eligible"),
        "eligible_by_family": dict(sorted(Counter(s["family"] for s in elig).items())),
        "eligible_by_level": dict(sorted(Counter(s["use_case_level"] for s in elig).items())),
        "eligible_levels_applicable": dict(sorted(Counter(lv for s in elig for lv in s["use_case_levels_applicable"]).items())),
        "eligible_by_kind": dict(sorted(Counter(s["pattern_kind"] for s in elig).items())),
        "eligible_by_geography_type": dict(sorted(Counter(s["geography_type"] for s in elig).items())),
        "eligible_by_best_strength": dict(sorted(Counter(s["best_explaining_strength"] for s in elig).items())),
        "eligible_heat_index_by_level": dict(sorted(Counter(s["use_case_level"] for s in hi).items())),
        "eligible_heat_index_by_state": dict(sorted(Counter(_state_of(s) for s in hi).items())),
        "eligible_fwi_by_state": dict(sorted(Counter(_state_of(s) for s in elig if s["family"] == "fire_weather_index").items())),
        "eligible_heat_index_with_specific_match": sum(s["n_relevant_explaining_specific"] > 0 for s in hi),
        "fwi": {"seeds": sum(s["family"] == "fire_weather_index" for s in seeds),
                "acceptance_blocked": sum(s["acceptance_blocked"] for s in seeds if s["family"] == "fire_weather_index"),
                "eligible": sum(s["family"] == "fire_weather_index" for s in elig)},
        "not_computable_excluded": sum((not s["pattern_computed"]) and (not s["acceptance_blocked"]) and s["n_relevant_explaining"] > 0 for s in seeds),
        "top_eligible": [{"seed_id": s["seed_id"], "seed_rank_key": s["seed_rank_key"], "use_case_level": s["use_case_level"],
                          "pattern_summary": s["pattern_summary"], "best_explaining_strength": s["best_explaining_strength"],
                          "n_relevant_explaining": s["n_relevant_explaining"],
                          "n_relevant_explaining_specific": s["n_relevant_explaining_specific"],
                          "top_statements": [x["statement"] for x in s["relevant_statements"]
                                             if x["statement_type"] in EXPLAINING][:3]}
                         for s in sorted(elig, key=lambda s: s["seed_rank_key"])[:10]],
    }
