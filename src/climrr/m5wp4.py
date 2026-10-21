"""M5-WP4: the positive-case compatibility run on LITCORPUS-02 --- adjudicated WP4 claims x three prototypes.

Authorized by D-025 (`docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md`,
Track A: "compatibility only after adjudication"). Reuses
`climrr.compat.evaluate_pair` unchanged in its rules --- C-1 / C-2 (D-025 term
set: `approved_lexical` forms participate, `approved_family_term` excluded and
masking, i.e. the "extended heat index" mask), G-2 / G-3, T-1 / T-2 / T-3, S-1,
D-1, U-1 --- and `climrr.m5wp2.effective_claim` / `assign_relation` (relation
definitions as in M5-WP2). Adds only:

* the frozen inputs (`artifacts/bridges/m5wp4_inputs.json`);
* **G-R, the geography role** (work package: "compare the claim's geography
  string **and role** against the prototype label"). The adjudicated role class
  travels with the claim. A place whose role is affiliation / person / citation
  is `not_evaluable`, never compatible and never incompatible; an exact G-1
  label match counts as `compatible` only when the role class is study
  geography (`study_area`, or `cited_study_area` for a restated cited finding);
  otherwise `not_evaluable`;
* a granularity reason on G-3: a state name against a county prototype of that
  state (`Oklahoma` vs `Oklahoma, Stephens`) is `different_granularity`;
* **the standardized-heat-index flag**: a C-2 `heat index` hit lying inside
  "standardized heat index" is kept (no mask, as the package orders) and flagged
  `possible_collision: standardized heat index`.

`compat.py` is not edited: the frozen M5-WP2 inputs pin its hash.
"""

from __future__ import annotations

import csv
import io
import json

from climrr import bridge, compat, conceptmap, m5wp2, retrieval
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT, repo_relative
from climrr.wp4adj import STUDY_ROLE_CLASSES

ADJ_DIR = REPO_ROOT / "artifacts" / "literature" / "wp4_claims_adjudicated"
PROTO_DIR = m5wp2.PROTO_DIR
PROTOTYPE_FILES = m5wp2.PROTOTYPE_FILES
BRIDGES = REPO_ROOT / "artifacts" / "bridges"
INPUTS_PATH = BRIDGES / "m5wp4_inputs.json"
MATRIX_JSON = BRIDGES / "m5wp4_matrix.json"
MATRIX_CSV = BRIDGES / "m5wp4_matrix.csv"
EXPECTED_CONCEPT_MAP_PREFIX = "27f7a44d"

NON_LOCATIONAL_ROLES = ("affiliation", "citation_or_person")
SHI = "standardized heat index"
COLLISION_FLAG = f"possible_collision: {SHI}"

M5WP4_RULES = {
    "G-R": ("geography role (M5-WP4): the claim's adjudicated geography role class travels with the claim. Role class "
            "affiliation or citation_or_person -> not_evaluable (role not study geography), whatever the place; an exact "
            "G-1 label match is `compatible` only if the role class is study_area or cited_study_area, otherwise "
            "not_evaluable (role not study geography). Never incompatible"),
    "G-3-granularity": ("reason refinement of G-3 (M5-WP4): an explicit claim geography equal to the State of a county "
                        "prototype is not_evaluable with reason different_granularity_state_vs_county"),
    "C-2-flag": (f"concept flag (M5-WP4): a C-2 hit for 'heat index' lying inside an occurrence of '{SHI}' in the concept "
                 f"value keeps its C-2 status and is flagged '{COLLISION_FLAG}' for GUIDANCE; no mask is applied"),
}
TIER_C_SENTENCE = m5wp2.TIER_C_SENTENCE
BOUNDED_SENTENCE = ("No candidate-bridge-eligible pair was found under the current deterministic rules among the "
                    "adjudicated claims of the twenty frozen LITCORPUS-02 place candidates.")


class FreezeError(Exception):
    pass


def _load(p) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def rule_version() -> dict:
    return {"compat_py_sha256": sha256_file(REPO_ROOT / "src" / "climrr" / "compat.py"),
            "rules_record_sha256": compat.record_sha256(compat.ALL_RULES),
            "m5wp4_rules_record_sha256": compat.record_sha256(M5WP4_RULES),
            "relation_rules_record_sha256": compat.record_sha256(m5wp2.RELATION_RULES)}


def rfwi1_version() -> dict:
    return {"rule": retrieval.RULE_ID, "version": retrieval.RULE_VERSION, "decision_id": retrieval.DECISION_ID,
            "rule_text_sha256": compat.record_sha256(retrieval.RULE_TEXT),
            "use_here": "recorded only: R-FWI-1 governs retrieval, not claim compatibility (D-025)"}


def build_inputs() -> dict:
    claims = []
    for p in sorted(ADJ_DIR.glob("LIT2-*.json")):
        rec = _load(p)
        for c in rec["claims"]:
            claims.append({"claim_id": c["claim_id"], "item_id": rec["lit2_id"], "claim_type": c["claim_type"],
                           "claim_validation_status": c["claim_validation_status"], "evidence_tier": c["evidence_tier"],
                           "origin": c.get("origin", "reader_1"), "scope": rec["scope_adjudication"]["adopted"],
                           "claim_file": repo_relative(p), "claim_file_sha256": sha256_file(p),
                           "claim_record_sha256": compat.record_sha256(c)})
    protos = []
    for f in PROTOTYPE_FILES:
        p = PROTO_DIR / f
        rec = _load(p)
        protos.append({"prototype_id": rec["record_id"], "version": rec.get("version", 1), "prototype_file": repo_relative(p),
                       "prototype_file_sha256": sha256_file(p), "prototype_record_sha256": compat.record_sha256(rec)})
    cm_sha = sha256_file(conceptmap.CONCEPT_MAP_PATH)
    if not cm_sha.startswith(EXPECTED_CONCEPT_MAP_PREFIX):
        raise FreezeError(f"concept map {cm_sha} is not the D-025 map {EXPECTED_CONCEPT_MAP_PREFIX}…")
    return {
        "package": "M5-WP4 (positive-case compatibility run, LITCORPUS-02)",
        "authorized_by": "docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md (D-025), Track A; work package M4-WP4r3 Phase B",
        "record_hash_convention": compat.RECORD_HASH_CONVENTION,
        "adjudication_summary_sha256": sha256_file(ADJ_DIR / "adjudication_summary.json"),
        "concept_map_sha256": cm_sha,
        "geo_list_sha256": sha256_file(compat.GEO_LIST_PATH),
        "compat_rule_version": rule_version(),
        "r_fwi_1_version": rfwi1_version(),
        "n_claims": len(claims), "n_prototypes": len(protos), "n_pairs": len(claims) * len(protos),
        "claims": claims, "prototypes": protos,
        "untouched": {"m5wp2_inputs.json": sha256_file(BRIDGES / "m5wp2_inputs.json"),
                      "m5wp2_matrix.json": sha256_file(BRIDGES / "m5wp2_matrix.json"),
                      "m5wp1_inputs.json": sha256_file(BRIDGES / "m5wp1_inputs.json"),
                      "m5wp1_matrix.json": sha256_file(BRIDGES / "m5wp1_matrix.json")},
    }


def verify_inputs(frozen: dict | None = None) -> dict:
    frozen = frozen if frozen is not None else _load(INPUTS_PATH)
    current = build_inputs()
    if current != frozen:
        diffs = [k for k in sorted(set(frozen) | set(current)) if frozen.get(k) != current.get(k)]
        raise FreezeError(f"M5-WP4 inputs differ from the freeze in: {', '.join(diffs)}")
    return frozen


def effective_claim(c: dict) -> dict:
    """`m5wp2.effective_claim` plus the adjudicated geography role (value and class)."""
    e = m5wp2.effective_claim(c)
    role = c["adjudication"]["geography_role"]["adopted"]
    e["geography"] = {**e["geography"], "role": role["value"], "role_class": role["class"]}
    return e


def _g(status: str, rule_id: str, cv: dict, pv: dict, reason: str) -> dict:
    assert status in compat.STATUSES and (rule_id in compat.ALL_RULES or rule_id in M5WP4_RULES)
    return {"dimension": "geography", "status": status, "rule_id": rule_id, "claim_value": cv, "prototype_value": pv,
            "reason": reason}


def compare_geography(geography: dict, pv: dict, geo_list: dict) -> dict:
    """compat.compare_geography (G-1/G-2/G-3/U-1) with the role gate G-R and the granularity reason."""
    base = compat.compare_geography(geography, pv, geo_list)
    cls = geography.get("role_class", "unknown")
    cv = {**base["claim_value"], "role": geography.get("role"), "role_class": cls}
    if base["rule_id"] == "U-1":
        return {**base, "claim_value": cv}
    if cls in NON_LOCATIONAL_ROLES:
        return _g("not_evaluable", "G-R", cv, pv, f"role_not_study_geography ({cls})")
    if base["status"] == "compatible":
        if cls in STUDY_ROLE_CLASSES:
            return {**base, "claim_value": cv, "reason": f"{base['reason']}; role {cls}"}
        return _g("not_evaluable", "G-R", cv, pv, f"role_not_study_geography ({cls})")
    if (base["reason"] == "no_exact_label_match_and_no_listed_disjoint_place" and pv["level"] == "county"
            and compat._norm(str(geography.get("value"))) == compat._norm(pv["raw"]["State"])):
        return _g("not_evaluable", "G-3-granularity", cv, pv, "different_granularity_state_vs_county")
    return {**base, "claim_value": cv}


def shi_collisions(concept_value: str, hits: list[dict]) -> list[dict]:
    """The C-2 `heat index` hits that lie inside an occurrence of 'standardized heat index'."""
    spans = conceptmap.find_term(SHI, concept_value or "")
    return [h for h in hits if h["surface_term"] == "heat index"
            and any(s <= h["char_start"] and h["char_end"] <= e for s, e in spans)]


def evaluate_pair(eff: dict, proto: dict, geo: dict, cmap: list[dict]) -> dict:
    row = compat.evaluate_pair(eff, proto, geo, cmap)
    pv = compat.prototype_values(proto)
    row["judgments"]["geography"] = compare_geography(eff["geography"], pv["geography"], geo)
    statuses = [row["judgments"][d]["status"] for d in compat.DIMENSIONS]
    row["all_compatible"] = all(s == "compatible" for s in statuses)
    row["n_incompatible"] = statuses.count("incompatible")
    cj = row["judgments"]["concept"]
    coll = shi_collisions(cj["claim_value"].get("raw"), cj["claim_value"].get("all_family_term_hits", []))
    row["flags"] = []
    if coll:
        cj["possible_collision"] = {"flag": COLLISION_FLAG, "rule_id": "C-2-flag", "hits": coll}
        row["flags"].append(COLLISION_FLAG)
    return row


def run(frozen: dict) -> list[dict]:
    geo = compat.load_geo_list()
    cmap = conceptmap.load()
    protos = [_load(REPO_ROOT / p["prototype_file"]) for p in frozen["prototypes"]]
    recs: dict[str, dict] = {}
    rows = []
    for meta in frozen["claims"]:
        rec = recs.setdefault(meta["claim_file"], _load(REPO_ROOT / meta["claim_file"]))
        c = next(x for x in rec["claims"] if x["claim_id"] == meta["claim_id"])
        eff = effective_claim(c)
        for proto in protos:
            row = evaluate_pair(eff, proto, geo, cmap)
            eligible, ne = bridge.candidate_bridge_eligible(row)
            rel, why = m5wp2.assign_relation(row)
            row.update(item_id=meta["item_id"], evidence_tier=meta["evidence_tier"], origin=meta["origin"], scope=meta["scope"],
                       prototype_version=proto.get("version", 1), adopted_dimensions_applied=eff["adopted_dimensions_applied"],
                       claim_text=c["claim_text"], evidence=c["evidence"],
                       candidate_bridge_eligible=eligible, not_evaluable_dimensions=ne,
                       provisional_relation=rel, relation_rule=why)
            rows.append(row)
    return rows


def summarize(rows: list[dict]) -> dict:
    base = compat.summarize(rows)
    base["n_candidate_bridge_eligible"] = sum(r["candidate_bridge_eligible"] for r in rows)
    base["eligible_pair_ids"] = [r["pair_id"] for r in rows if r["candidate_bridge_eligible"]]
    base["relations"] = {k: sum(r["provisional_relation"] == k for r in rows) for k in m5wp2.RELATION_ORDER}
    base["by_tier"] = {t: sum(r["evidence_tier"] == t for r in rows) for t in ("A", "B", "C")}
    base["concept_positive_pair_ids"] = [r["pair_id"] for r in rows if r["judgments"]["concept"]["status"] in bridge.CONCEPT_POSITIVE]
    base["geography_compatible_pair_ids"] = [r["pair_id"] for r in rows if r["judgments"]["geography"]["status"] == "compatible"]
    base["geography_role_gated_pair_ids"] = [r["pair_id"] for r in rows if r["judgments"]["geography"]["rule_id"] == "G-R"]
    base["possible_collision_pair_ids"] = [r["pair_id"] for r in rows if COLLISION_FLAG in r["flags"]]
    return base


def to_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["pair_id", "claim_id", "item_id", "prototype_id", "prototype_version", "evidence_tier", "origin", "claim_type",
                *[f"{d}_status" for d in compat.DIMENSIONS], *[f"{d}_rule" for d in compat.DIMENSIONS],
                "geography_role_class", "candidate_bridge_eligible", "not_evaluable_dimensions", "provisional_relation", "flags"])
    for r in rows:
        j = r["judgments"]
        w.writerow([r["pair_id"], r["claim_id"], r["item_id"], r["prototype_id"], r["prototype_version"], r["evidence_tier"],
                    r["origin"], r["claim_type"], *[j[d]["status"] for d in compat.DIMENSIONS],
                    *[j[d]["rule_id"] for d in compat.DIMENSIONS], j["geography"]["claim_value"].get("role_class"),
                    r["candidate_bridge_eligible"], ";".join(r["not_evaluable_dimensions"]), r["provisional_relation"],
                    ";".join(r["flags"])])
    return buf.getvalue()
