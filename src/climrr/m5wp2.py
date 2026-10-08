"""M5-WP2: the positive-case compatibility run --- adjudicated WP2 claims x three prototypes.

Authorized by D-019 (`docs/M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md`,
Phase 4). Reuses `climrr.compat.evaluate_pair` unchanged in its rules (revised
C-2 via the concept map; G-1/G-2/G-3; T-1/T-2/T-3; S-1; D-1; U-1) and
`climrr.bridge.candidate_bridge_eligible`. Adds only:

* the frozen inputs (`artifacts/bridges/m5wp2_inputs.json`): every adjudicated
  WP2 claim of every tier, P-CELL-1, P-COUNTY-1, **P-STATE-1 v2**, the concept
  map, the G-2 list and the compatibility-rule version;
* the **effective claim**: an adjudicated record with `adopted_dimensions`
  substituted for the differing dimensions (D-019 rule 3);
* the provisional relation, by the work package's precedence (`assign_relation`).

The frozen M5-WP1 inputs and matrix are not read or touched.
"""

from __future__ import annotations

import copy
import csv
import io
import json

from climrr import bridge, compat, conceptmap
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT, repo_relative

ADJ_DIR = REPO_ROOT / "artifacts" / "literature" / "wp2_claims_adjudicated"
PROTO_DIR = REPO_ROOT / "artifacts" / "phenomena" / "prototypes"
PROTOTYPE_FILES = ("P-CELL-1.json", "P-COUNTY-1.json", "P-STATE-1.v2.json")
BRIDGES = REPO_ROOT / "artifacts" / "bridges"
INPUTS_PATH = BRIDGES / "m5wp2_inputs.json"
MATRIX_JSON = BRIDGES / "m5wp2_matrix.json"
MATRIX_CSV = BRIDGES / "m5wp2_matrix.csv"
COMPAT_SRC = REPO_ROOT / "src" / "climrr" / "compat.py"

RELATION_ORDER = ("supporting", "supporting_qualified", "contradicting", "related_insufficient", "uncertain",
                  "incompatible")
RELATION_RULES = {
    "contradicting": "concept positive (metric or family) and geography compatible, and direction is the only incompatible dimension",
    "incompatible": "any dimension incompatible (and not contradicting)",
    "supporting": "eligible; concept metric-compatible; scenario, time and direction all compatible",
    "supporting_qualified": "eligible; direction compatible or not_evaluable; family-level concept or scenario/time not_evaluable",
    "related_insufficient": "concept positive (metric or family), not eligible (geography not compatible), nothing incompatible",
    "uncertain": "otherwise",
}
TIER_C_SENTENCE = ("A tier-C (single-reader or scope-contested) claim cannot establish an accepted bridge without "
                   "further independent resolution.")
BOUNDED_SENTENCE = ("No candidate-bridge-eligible pair was found under the current deterministic rules among the "
                    "adjudicated claims of the four frozen relevance-guided candidates.")


class FreezeError(Exception):
    pass


def _load(p) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def rule_version() -> dict:
    return {"compat_py_sha256": sha256_file(COMPAT_SRC), "rules_record_sha256": compat.record_sha256(compat.ALL_RULES),
            "relation_rules_record_sha256": compat.record_sha256(RELATION_RULES)}


def build_inputs() -> dict:
    claims = []
    for p in sorted(ADJ_DIR.glob("LIT-*.json")):
        rec = _load(p)
        for c in rec["claims"]:
            claims.append({"claim_id": c["claim_id"], "item_id": rec["item_id"], "claim_type": c["claim_type"],
                           "claim_validation_status": c["claim_validation_status"], "evidence_tier": c["evidence_tier"],
                           "scope": rec["scope_adjudication"]["adopted"], "claim_file": repo_relative(p),
                           "claim_file_sha256": sha256_file(p), "claim_record_sha256": compat.record_sha256(c)})
    protos = []
    for f in PROTOTYPE_FILES:
        p = PROTO_DIR / f
        rec = _load(p)
        protos.append({"prototype_id": rec["record_id"], "version": rec.get("version", 1), "prototype_file": repo_relative(p),
                       "prototype_file_sha256": sha256_file(p), "prototype_record_sha256": compat.record_sha256(rec)})
    return {
        "package": "M5-WP2 (positive-case compatibility run)",
        "authorized_by": "docs/M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md (D-019), Phase 4",
        "record_hash_convention": compat.RECORD_HASH_CONVENTION,
        "adjudication_summary_sha256": sha256_file(ADJ_DIR / "adjudication_summary.json"),
        "concept_map_sha256": sha256_file(conceptmap.CONCEPT_MAP_PATH),
        "geo_list_sha256": sha256_file(compat.GEO_LIST_PATH),
        "compat_rule_version": rule_version(),
        "n_claims": len(claims), "n_prototypes": len(protos), "n_pairs": len(claims) * len(protos),
        "claims": claims, "prototypes": protos,
        "untouched": {"m5wp1_inputs.json": sha256_file(BRIDGES / "m5wp1_inputs.json"),
                      "m5wp1_matrix.json": sha256_file(BRIDGES / "m5wp1_matrix.json"),
                      "P-STATE-1.json (v1)": sha256_file(PROTO_DIR / "P-STATE-1.json")},
    }


def verify_inputs(frozen: dict | None = None) -> dict:
    frozen = frozen if frozen is not None else _load(INPUTS_PATH)
    current = build_inputs()
    if current != frozen:
        diffs = [k for k in sorted(set(frozen) | set(current)) if frozen.get(k) != current.get(k)]
        raise FreezeError(f"M5-WP2 inputs differ from the freeze in: {', '.join(diffs)}")
    return frozen


def effective_claim(c: dict) -> dict:
    """The adjudicated claim with each adopted dimension substituted (D-019 rule 3)."""
    e = copy.deepcopy(c)
    adopted = c.get("adjudication", {}).get("adopted_dimensions", {})
    for d, v in adopted.items():
        if d == "claim_type":
            e["claim_type"] = v
            continue
        nd = {"value": v["value"], "status": v["tag"]}
        if "support" in v:
            nd["support"] = v["support"]
        e[d] = nd
    e["adopted_dimensions_applied"] = sorted(adopted)
    return e


def assign_relation(row: dict) -> tuple[str, str]:
    st = {d: row["judgments"][d]["status"] for d in compat.DIMENSIONS}
    concept_pos = st["concept"] in bridge.CONCEPT_POSITIVE
    incompatible = [d for d in compat.DIMENSIONS if st[d] == "incompatible"]
    eligible, _ = bridge.candidate_bridge_eligible(row)
    if concept_pos and st["geography"] == "compatible" and incompatible == ["direction"]:
        rel = "contradicting"
    elif incompatible:
        rel = "incompatible"
    elif eligible and st["concept"] == "compatible" and all(st[d] == "compatible" for d in ("scenario", "time", "direction")):
        rel = "supporting"
    elif eligible and st["direction"] in ("compatible", "not_evaluable") and (
            st["concept"] == compat.FAMILY_LEVEL or "not_evaluable" in (st["scenario"], st["time"])):
        rel = "supporting_qualified"
    elif concept_pos and not eligible:
        rel = "related_insufficient"
    else:
        rel = "uncertain"
    if rel != "incompatible":
        bridge.check_relation(row, rel)  # the D-018 vocabulary must permit it
    return rel, RELATION_RULES[rel]


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
            row = compat.evaluate_pair(eff, proto, geo, cmap)
            eligible, ne = bridge.candidate_bridge_eligible(row)
            rel, why = assign_relation(row)
            row.update(item_id=meta["item_id"], evidence_tier=meta["evidence_tier"], scope=meta["scope"],
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
    base["relations"] = {k: sum(r["provisional_relation"] == k for r in rows) for k in RELATION_ORDER}
    base["by_tier"] = {t: sum(r["evidence_tier"] == t for r in rows) for t in ("A", "B", "C")}
    base["concept_positive_pair_ids"] = [r["pair_id"] for r in rows if r["judgments"]["concept"]["status"] in bridge.CONCEPT_POSITIVE]
    base["geography_compatible_pair_ids"] = [r["pair_id"] for r in rows if r["judgments"]["geography"]["status"] == "compatible"]
    return base


def to_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["pair_id", "claim_id", "item_id", "prototype_id", "prototype_version", "evidence_tier", "claim_type",
                *[f"{d}_status" for d in compat.DIMENSIONS], *[f"{d}_rule" for d in compat.DIMENSIONS],
                "candidate_bridge_eligible", "not_evaluable_dimensions", "provisional_relation"])
    for r in rows:
        j = r["judgments"]
        w.writerow([r["pair_id"], r["claim_id"], r["item_id"], r["prototype_id"], r["prototype_version"], r["evidence_tier"],
                    r["claim_type"], *[j[d]["status"] for d in compat.DIMENSIONS], *[j[d]["rule_id"] for d in compat.DIMENSIONS],
                    r["candidate_bridge_eligible"], ";".join(r["not_evaluable_dimensions"]), r["provisional_relation"]])
    return buf.getvalue()
