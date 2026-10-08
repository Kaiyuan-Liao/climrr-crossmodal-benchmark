"""M5-WP1: deterministic compatibility between WP1 claims and WP3b prototypes.

Authorized by `docs/M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md` (D-017) as
**machinery validation** over single-reader provisional claims. Nothing here
computes similarity, embeds text, or asks a model anything: a dimension is
`compatible` or `incompatible` only when a named rule below says so, and
`not_evaluable` otherwise.

Phase A freezes the inputs: every claim and prototype the matrix reads is
pinned by a hash of its file and a hash of its record. Phase B derives each
side's comparison values by named rules and compares them by named rules.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT, repo_relative

LIT = REPO_ROOT / "artifacts" / "literature"
CLAIMS_DIR = LIT / "wp1_claims"
SAMPLE_PATH = LIT / "wp1_sample.json"
CORPUS_MANIFEST_PATH = LIT / "corpus_manifest.json"
PROTOTYPES_DIR = REPO_ROOT / "artifacts" / "phenomena" / "prototypes"
PROTOTYPE_IDS = ("P-CELL-1", "P-COUNTY-1", "P-STATE-1")
DATA_MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"
BRIDGES = REPO_ROOT / "artifacts" / "bridges"
INPUTS_PATH = BRIDGES / "m5wp1_inputs.json"

RECORD_HASH_CONVENTION = (
    "SHA-256 of the UTF-8 bytes of json.dumps(record, sort_keys=True, ensure_ascii=False, "
    "separators=(',', ':'))"
)


class FreezeError(Exception):
    """A frozen input no longer matches its pin. A defect to escalate, never to update."""


def record_sha256(record: object) -> str:
    text = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def claim_file(item_id: str) -> Path:
    return CLAIMS_DIR / f"{item_id}.json"


def prototype_file(prototype_id: str) -> Path:
    return PROTOTYPES_DIR / f"{prototype_id}.json"


def build_inputs() -> dict:
    """Describe the current inputs: every claim and prototype, with its pins."""
    sample = _load(SAMPLE_PATH)
    data_manifest = _load(DATA_MANIFEST_PATH)
    csv_sha = next(f["sha256"] for f in data_manifest["files"] if f["filename"] == "FullData.csv")
    corpus = next(c for c in data_manifest["external_corpora"] if c["corpus_id"] == "LITCORPUS-00")
    corpus_sha = sha256_file(CORPUS_MANIFEST_PATH)
    if corpus_sha != corpus["inventory_manifest_sha256"]:
        raise FreezeError("corpus manifest bytes differ from data/manifest.json")

    claims = []
    for item_id in sample["item_ids"]:
        path = claim_file(item_id)
        rec = _load(path)
        if rec["corpus_manifest_sha256"] != corpus_sha:
            raise FreezeError(f"{item_id}: claim record tied to a different corpus manifest")
        for c in rec["claims"]:
            claims.append({
                "claim_id": c["claim_id"],
                "item_id": item_id,
                "claim_type": c["claim_type"],
                "claim_validation_status": c["claim_validation_status"],
                "claim_file": repo_relative(path),
                "claim_file_sha256": sha256_file(path),
                "source_corpus_file_sha256": rec["file_sha256"],
                "claim_record_sha256": record_sha256(c),
            })

    prototypes = []
    for pid in PROTOTYPE_IDS:
        path = prototype_file(pid)
        rec = _load(path)
        if rec["csv_sha256"] != csv_sha:
            raise FreezeError(f"{pid}: built from CSV bytes other than the manifest's")
        prototypes.append({
            "prototype_id": pid,
            "prototype_file": repo_relative(path),
            "prototype_file_sha256": sha256_file(path),
            "prototype_record_sha256": record_sha256(rec),
            "schema_version": rec["schema_version"],
            "validation_only": rec["validation_only"],
            "built_from_commit": rec["built_from_commit"],
        })

    return {
        "package": "M5-WP1",
        "authorized_by": "docs/M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md (D-017)",
        "record_hash_convention": RECORD_HASH_CONVENTION,
        "corpus_manifest_sha256": corpus_sha,
        "wp1_sample_sha256": sha256_file(SAMPLE_PATH),
        "csv_sha256": csv_sha,
        "csv_sha256_source": "data/manifest.json (FullData.csv); the CSV itself is not read by M5-WP1",
        "n_claims": len(claims),
        "n_prototypes": len(prototypes),
        "n_pairs": len(claims) * len(prototypes),
        "claims": claims,
        "prototypes": prototypes,
    }


def verify_inputs(frozen: dict | None = None) -> dict:
    """Fail closed unless every pinned input is byte- and record-identical to the freeze."""
    frozen = frozen if frozen is not None else _load(INPUTS_PATH)
    current = build_inputs()
    if current != frozen:
        diffs = []
        for key in sorted(set(frozen) | set(current)):
            if frozen.get(key) != current.get(key):
                diffs.append(key)
        raise FreezeError(f"M5-WP1 inputs differ from the freeze in: {', '.join(diffs)}")
    return frozen


# =============================================================================
# Phase B: canonical values and rules
# =============================================================================
#
# Each side of each dimension is derived by a named rule (CV-* for the claim,
# PV-* for the prototype) and keeps the raw source value beside the derived
# one. Each judgment cites the comparison rule that decided it. A rule that is
# silent leaves the dimension `not_evaluable`; nothing falls through to
# `incompatible`.

STATUSES = ("compatible", "incompatible", "not_evaluable")
DIMENSIONS = ("concept", "geography", "time", "scenario", "direction")
GEO_LIST_PATH = REPO_ROOT / "config" / "geo_disjoint_list.yaml"

#: The pilot-family canonical concept IDs, keyed by the prototype's `H.family_key`.
PROTOTYPE_CONCEPT_IDS = {
    "fire_weather": "fwi_seasonal_value",
    "heat_index": "heatindex_days_above_105F",
}

#: Approved claim-concept -> canonical-ID mappings. **None exist in the
#: repository**: no ruling or decision has approved one, and this package may
#: not author one. The table is kept, empty, so that the rule reads it.
APPROVED_CONCEPT_MAPPINGS: dict[str, str] = {}

#: T-2's cut-off: the start of the earliest future window in the pilot family
#: (2045-2054). A `finding` whose explicit year range ends before it is about a
#: period the prototype's projection does not cover.
T2_CUTOFF_YEAR = 2045

#: The only direction words D-1 reads. No synonym is mapped onto them.
DIRECTION_TOKENS = ("increase", "decrease", "no change")

RULES = {
    # derivation rules, claim side
    "CV-C1": "claim concept: the tagged value, lowercased, runs of whitespace collapsed to one space, stripped; no mapping",
    "CV-G1": "claim geography: the tagged value and its tag, casefolded and whitespace-collapsed for comparison",
    "CV-T1": "claim time: every explicit four-digit year range `YYYY-YYYY`, `YYYY–YYYY` or `YYYY to YYYY` in an `explicit` temporal frame; several ranges are combined into their hull [min start, max end]",
    "CV-S1": "claim scenario: an RCP pathway label `RCP<d.d>` in an `explicit` scenario value",
    "CV-D1": "claim direction: the tagged value, lowercased and whitespace-collapsed, read only if it equals one of the direction words exactly",
    # derivation rules, prototype side
    "PV-C1": "prototype concept: the canonical ID for the record's `H.family_key` (fire_weather -> fwi_seasonal_value; heat_index -> heatindex_days_above_105F)",
    "PV-G1": "prototype geography: `G.level` and the label built from `G.identifier` --- the `Crossmodel` id; `State, NAME`; or `State` --- with `G.provenance_status` carried",
    "PV-T1": "prototype time: the four-digit year ranges stated in `T.per_role.baseline.value` and `T.per_role.future.value`; a role whose value states no range has no window",
    "PV-S1": "prototype scenario: the RCP label in `C.per_role.future.value`",
    "PV-D1": "prototype direction: `D.direction`",
    # comparison rules
    "U-1": "`unknown` on either side -> not_evaluable, never incompatible",
    "C-1": "concept: compatible only if the claim's normalized concept (or an approved mapping of it) is identical to the prototype's canonical ID under the same normalization; otherwise not_evaluable (no_approved_mapping). Never incompatible",
    "G-1": "geography: compatible only if the claim's `explicit` geography equals the prototype label exactly, case-insensitively, at the prototype's level (`State`; `State, NAME`; cell id)",
    "G-2": "geography: incompatible only if the claim's `explicit` geography names, as a whole word, a place on the committed `disjoint_from_united_states` list, and names no `not_disjoint` place and no US marker",
    "G-3": "geography: otherwise not_evaluable --- different granularity, an inferred tag, a place not on the list, or a not-disjoint scope",
    "T-1": "time: compatible if the claim's explicit year range overlaps the prototype's future window",
    "T-2": "time: incompatible only if the claim is a `finding`, its explicit year range ends before 2045 (T2_CUTOFF_YEAR), and the prototype has a future window starting at or after 2045",
    "T-3": "time: otherwise not_evaluable",
    "S-1": "scenario: both sides an explicit RCP label: identical -> compatible, different -> incompatible; any other case not_evaluable. Reads the climate-scenario dimension only",
    "D-1": "direction: evaluated only if concept is compatible; then both a direction word: equal -> compatible, different -> incompatible; otherwise not_evaluable",
}

_WS = re.compile(r"\s+")
_YEAR_RANGE = re.compile(r"\b(\d{4})\s*(?:-|–|—|to)\s*(\d{4})\b")
_RCP = re.compile(r"\bRCP\s*(\d(?:\.\d)?)\b", re.IGNORECASE)


def _norm(text: str) -> str:
    return _WS.sub(" ", text).strip().lower()


def year_ranges(text: str) -> list[tuple[int, int]]:
    """Every explicit four-digit year range in `text`, in order. `1930s` is not a year."""
    out = []
    for a, b in _YEAR_RANGE.findall(text):
        start, end = int(a), int(b)
        if start <= end:
            out.append((start, end))
    return out


def _rcp(text: str) -> str | None:
    m = _RCP.search(text)
    return f"RCP{m.group(1)}" if m else None


def _whole_word(term: str, text: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text, re.IGNORECASE) is not None


def load_geo_list(path: Path | None = None) -> dict:
    data = yaml.safe_load((path or GEO_LIST_PATH).read_text(encoding="utf-8"))
    return {
        "disjoint": list(data["disjoint_from_united_states"]),
        "not_disjoint": [e["term"] for e in data["not_disjoint"]],
        "us_markers": list(data["us_markers"]),
    }


def _is_unknown(dim: dict) -> bool:
    return dim.get("status") == "unknown" or dim.get("value") in (None, "unknown")


def _judgment(dimension: str, status: str, rule_id: str, claim_value: dict, prototype_value: dict,
              reason: str) -> dict:
    assert status in STATUSES and rule_id in RULES
    return {"dimension": dimension, "status": status, "rule_id": rule_id,
            "claim_value": claim_value, "prototype_value": prototype_value, "reason": reason}


# --- prototype side -----------------------------------------------------------


def prototype_values(proto: dict) -> dict:
    """Derive every prototype-side comparison value, each with its rule and raw source."""
    family = proto["H"]["family_key"]
    g = proto["G"]
    ident = g["identifier"]
    if g["level"] == "cell":
        label = ident["Crossmodel"]
    elif g["level"] == "county":
        label = f"{ident['State']}, {ident['NAME']}"
    elif g["level"] == "state":
        label = ident["State"]
    else:
        raise ValueError(f"unknown prototype level {g['level']!r}")
    t = proto["T"]["per_role"]
    base_raw, fut_raw = t["baseline"]["value"], t["future"]["value"]
    base_r, fut_r = year_ranges(base_raw), year_ranges(fut_raw)
    c_raw = proto["C"]["per_role"]["future"]["value"]
    return {
        "concept": {"raw": {"H.family_key": family, "H.family": proto["H"]["family"]},
                    "canonical": PROTOTYPE_CONCEPT_IDS.get(family), "derivation_rule": "PV-C1",
                    "provenance_status": proto["H"]["provenance_status"]},
        "geography": {"raw": ident, "level": g["level"], "label": label, "derivation_rule": "PV-G1",
                      "provenance_status": g["provenance_status"]},
        "time": {"raw": {"baseline": base_raw, "future": fut_raw},
                 "baseline": list(base_r[0]) if len(base_r) == 1 else None,
                 "future": list(fut_r[0]) if len(fut_r) == 1 else None,
                 "derivation_rule": "PV-T1", "provenance_status": proto["T"]["status"]},
        "scenario": {"raw": c_raw, "canonical": _rcp(c_raw) if c_raw else None, "derivation_rule": "PV-S1",
                     "provenance_status": proto["C"]["per_role"]["future"]["status"]},
        "direction": {"raw": proto["D"]["direction"], "canonical": proto["D"]["direction"]
                      if proto["D"]["direction"] in DIRECTION_TOKENS else None, "derivation_rule": "PV-D1",
                      "provenance_status": proto["D"].get("provenance_status", "unknown")},
    }


# --- the five comparators -------------------------------------------------------


def compare_concept(concept: dict, pv: dict) -> dict:
    cv = {"raw": concept.get("value"), "tag": concept.get("status"), "derivation_rule": "CV-C1"}
    if _is_unknown(concept):
        return _judgment("concept", "not_evaluable", "U-1", {**cv, "normalized": None}, pv, "claim_value_unknown")
    if pv["canonical"] is None:
        return _judgment("concept", "not_evaluable", "U-1", {**cv, "normalized": _norm(cv["raw"])}, pv,
                         "prototype_value_unknown")
    claim_id = _norm(cv["raw"])
    mapped = APPROVED_CONCEPT_MAPPINGS.get(claim_id, claim_id)
    cv = {**cv, "normalized": claim_id, "mapped": mapped if mapped != claim_id else None}
    if _norm(mapped) == _norm(pv["canonical"]):
        return _judgment("concept", "compatible", "C-1", cv, pv, "identical_canonical_id")
    return _judgment("concept", "not_evaluable", "C-1", cv, pv, "no_approved_mapping")


def compare_geography(geography: dict, pv: dict, geo_list: dict) -> dict:
    cv = {"raw": geography.get("value"), "tag": geography.get("status"), "derivation_rule": "CV-G1"}
    if _is_unknown(geography):
        return _judgment("geography", "not_evaluable", "U-1", cv, pv, "claim_value_unknown")
    if geography.get("status") != "explicit":
        return _judgment("geography", "not_evaluable", "G-3", cv, pv, "claim_geography_not_explicit")
    text = cv["raw"]
    if _norm(text) == _norm(pv["label"]):
        return _judgment("geography", "compatible", "G-1", cv, pv, f"same_{pv['level']}_label")
    if any(_whole_word(t, text) for t in geo_list["us_markers"]):
        return _judgment("geography", "not_evaluable", "G-3", cv, pv, "names_the_united_states_not_the_label")
    nd = [t for t in geo_list["not_disjoint"] if _whole_word(t, text)]
    if nd:
        return _judgment("geography", "not_evaluable", "G-3", {**cv, "matched_term": nd[0]}, pv,
                         "named_scope_not_disjoint_from_united_states")
    dj = [t for t in geo_list["disjoint"] if _whole_word(t, text)]
    if dj:
        return _judgment("geography", "incompatible", "G-2", {**cv, "matched_term": dj[0]}, pv,
                         "explicit_place_outside_united_states")
    return _judgment("geography", "not_evaluable", "G-3", cv, pv,
                     "no_exact_label_match_and_no_listed_disjoint_place")


def compare_time(temporal: dict, claim_type: str, pv: dict) -> dict:
    cv = {"raw": temporal.get("value"), "tag": temporal.get("status"), "claim_type": claim_type,
          "derivation_rule": "CV-T1"}
    if _is_unknown(temporal):
        return _judgment("time", "not_evaluable", "U-1", {**cv, "range": None}, pv, "claim_value_unknown")
    ranges = year_ranges(cv["raw"]) if temporal.get("status") == "explicit" else []
    rng = [min(a for a, _ in ranges), max(b for _, b in ranges)] if ranges else None
    cv = {**cv, "range": rng}
    if rng is None:
        return _judgment("time", "not_evaluable", "T-3", cv, pv, "claim_has_no_explicit_year_range")
    fut = pv["future"]
    if fut is None:
        return _judgment("time", "not_evaluable", "T-3", cv, pv, "prototype_window_has_no_year_range")
    if rng[0] <= fut[1] and fut[0] <= rng[1]:
        return _judgment("time", "compatible", "T-1", cv, pv, "overlaps_prototype_future_window")
    if claim_type == "finding" and rng[1] < T2_CUTOFF_YEAR and fut[0] >= T2_CUTOFF_YEAR:
        return _judgment("time", "incompatible", "T-2", cv, pv, "historical_finding_ends_before_2045")
    reason = "claim_type_not_finding" if claim_type != "finding" else "range_not_entirely_before_2045"
    return _judgment("time", "not_evaluable", "T-3", cv, pv, reason)


def compare_scenario(scenario: dict, pv: dict) -> dict:
    """Climate scenario only. Takes the claim's `scenario` dimension and nothing else."""
    cv = {"raw": scenario.get("value"), "tag": scenario.get("status"), "derivation_rule": "CV-S1"}
    if _is_unknown(scenario):
        return _judgment("scenario", "not_evaluable", "U-1", {**cv, "canonical": None}, pv, "claim_value_unknown")
    if pv["canonical"] is None:
        return _judgment("scenario", "not_evaluable", "U-1", {**cv, "canonical": None}, pv,
                         "prototype_value_unknown")
    tok = _rcp(cv["raw"]) if scenario.get("status") == "explicit" else None
    cv = {**cv, "canonical": tok}
    if tok is None:
        return _judgment("scenario", "not_evaluable", "S-1", cv, pv, "claim_scenario_not_an_explicit_rcp")
    if tok == pv["canonical"]:
        return _judgment("scenario", "compatible", "S-1", cv, pv, "identical_rcp")
    return _judgment("scenario", "incompatible", "S-1", cv, pv, "different_rcp")


def compare_direction(direction: dict, concept_status: str, pv: dict) -> dict:
    cv = {"raw": direction.get("value"), "tag": direction.get("status"), "derivation_rule": "CV-D1"}
    if concept_status != "compatible":
        return _judgment("direction", "not_evaluable", "D-1", {**cv, "canonical": None}, pv,
                         "concept_not_comparable")
    if _is_unknown(direction):
        return _judgment("direction", "not_evaluable", "U-1", {**cv, "canonical": None}, pv, "claim_value_unknown")
    tok = _norm(cv["raw"])
    tok = tok if tok in DIRECTION_TOKENS else None
    cv = {**cv, "canonical": tok}
    if tok is None or pv["canonical"] is None:
        return _judgment("direction", "not_evaluable", "D-1", cv, pv, "direction_not_a_listed_word")
    if tok == pv["canonical"]:
        return _judgment("direction", "compatible", "D-1", cv, pv, "same_direction")
    return _judgment("direction", "incompatible", "D-1", cv, pv, "opposite_or_different_direction")


# --- pairs and the matrix -------------------------------------------------------


def evaluate_pair(claim: dict, proto: dict, geo_list: dict) -> dict:
    pv = prototype_values(proto)
    concept = compare_concept(claim["concept"], pv["concept"])
    judgments = {
        "concept": concept,
        "geography": compare_geography(claim["geography"], pv["geography"], geo_list),
        "time": compare_time(claim["temporal_frame"], claim["claim_type"], pv["time"]),
        "scenario": compare_scenario(claim["scenario"], pv["scenario"]),
        "direction": compare_direction(claim["relation_or_direction"], concept["status"], pv["direction"]),
    }
    statuses = [judgments[d]["status"] for d in DIMENSIONS]
    return {
        "pair_id": f"{claim['claim_id']}__{proto['record_id']}",
        "claim_id": claim["claim_id"],
        "claim_type": claim["claim_type"],
        "is_background_citation": claim["claim_type"] == "background_citation",
        "claim_validation_status": claim["claim_validation_status"],
        "prototype_id": proto["record_id"],
        "prototype_validation_only": proto["validation_only"],
        "judgments": judgments,
        "all_compatible": all(s == "compatible" for s in statuses),
        "n_incompatible": statuses.count("incompatible"),
    }


def load_frozen_claims_and_prototypes(frozen: dict) -> tuple[list[dict], list[dict]]:
    """The claims and prototypes the freeze names, in its order. Call after `verify_inputs`."""
    by_item: dict[str, dict] = {}
    claims = []
    for c in frozen["claims"]:
        rec = by_item.setdefault(c["item_id"], _load(REPO_ROOT / c["claim_file"]))
        claims.append(next(x for x in rec["claims"] if x["claim_id"] == c["claim_id"]))
    protos = [_load(REPO_ROOT / p["prototype_file"]) for p in frozen["prototypes"]]
    return claims, protos


def build_matrix(claims: list[dict], protos: list[dict], geo_list: dict) -> list[dict]:
    """Every claim against every prototype, once each, nothing dropped."""
    return [evaluate_pair(c, p, geo_list) for c in claims for p in protos]


def summarize(rows: list[dict]) -> dict:
    """Counts computed from the rows. Nothing here expects any particular total."""
    per_dim = {d: {s: 0 for s in STATUSES} for d in DIMENSIONS}
    per_proto: dict[str, dict] = {}
    incompat_rules: dict[str, int] = {}
    for r in rows:
        pp = per_proto.setdefault(r["prototype_id"], {d: {s: 0 for s in STATUSES} for d in DIMENSIONS})
        for d in DIMENSIONS:
            j = r["judgments"][d]
            per_dim[d][j["status"]] += 1
            pp[d][j["status"]] += 1
            if j["status"] == "incompatible":
                incompat_rules[j["rule_id"]] = incompat_rules.get(j["rule_id"], 0) + 1
    return {
        "n_pairs": len(rows),
        "per_dimension": per_dim,
        "per_prototype": per_proto,
        "n_all_compatible": sum(r["all_compatible"] for r in rows),
        "all_compatible_pair_ids": [r["pair_id"] for r in rows if r["all_compatible"]],
        "n_pairs_with_any_incompatible": sum(r["n_incompatible"] > 0 for r in rows),
        "incompatible_by_rule": dict(sorted(incompat_rules.items())),
        "n_background_citation_pairs": sum(r["is_background_citation"] for r in rows),
    }
