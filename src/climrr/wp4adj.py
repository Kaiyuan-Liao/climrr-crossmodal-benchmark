"""M4-WP4r3 Phase A: compare reader 1 and the blind reader on the twenty, then adjudicate.

Reuses the WP1b machinery unchanged --- `climrr.wp1b.align`,
`mechanical_diff`, `resolve_pair` (rules 2--3, span-limited trimming as
approved by D-019), `adjudicate_scope`, `statistics`, `evidence_tier` --- and
`climrr.wp2adj.norm_path`. Adds only what differs here:

* the inputs and their pins (`wp4_claims/`, reader 1 at `e0857aa`, keyed by
  LIT2 id; `wp4_blind/`, the blind reader at `c452d7d`, keyed by corpus
  basename and mapped to LIT2 ids through the frozen `wp4_sample.json`);
* an adapter for both WP4 schemas: reader 1's dimensions carry `status` and
  `support`, the blind reader's `tag` and `support_span`; both record a
  `geography.role` --- free text for reader 1, an object `{value, tag,
  support_span}` for the blind reader;
* **the geography role**, compared alongside geography (the work package asks
  for "geography + role"). Each reader's role is put into one of the classes in
  `ROLE_CLASSES` by `role_class`, a fixed lookup of the recorded strings that
  fails on any string it does not list. The adopted role is decided by
  `resolve_role` (rule 3-role, the "more conservative value": see there).

No paper is re-read for meaning; the corpus is opened only to re-slice spans.
"""

from __future__ import annotations

import json
from pathlib import Path

from climrr import wp1b
from climrr.checksums import sha256_file
from climrr.litingest import read_verified
from climrr.paths import REPO_ROOT
from climrr.wp2adj import norm_path

LIT = REPO_ROOT / "artifacts" / "literature"
R1_DIR = LIT / "wp4_claims"
R1_SUMMARY = LIT / "wp4_claims_summary.json"
R2_DIR = LIT / "wp4_blind"
R2_SUMMARY = R2_DIR / "wp4_blind_summary.json"
SAMPLE = LIT / "wp4_sample.json"
HIT_CLASSIFICATION = LIT / "wp4_hit_classification.json"
COMPARISON_PATH = LIT / "wp4_comparison.json"
ADJ_DIR = LIT / "wp4_claims_adjudicated"
ADJ_SUMMARY_PATH = ADJ_DIR / "adjudication_summary.json"
DOC_PATH = REPO_ROOT / "docs" / "LITERATURE_WP4_ADJUDICATION.md"
ROOT_KEY = "litcorpus02_root"

READER_1_COMMIT = "e0857aa"
BLIND_COMMIT = "c452d7d"
ADJUDICATOR = "reader 1 (the EXECUTOR, prototype-exposed)"
PRIOR_EXPOSURE_ITEM = "LIT2-001075"
PRIOR_EXPOSURE_NOTE = (
    "LIT2-001075 (item 272852900) is LITCORPUS-00 LIT-001536, read twice in M4-WP2. Reader 1 --- also the "
    "adjudicator --- had read it before (its record carries prior_exposure). The blind reader was a fresh session "
    "and was not told of the earlier reading; its record carries no exposure note. Neither reader's WP4 record "
    "was produced from a WP2 artifact.")
REPRESENTATIVENESS = ("deterministic rank sample of lexical place candidates from LITCORPUS-02; "
                      "not representative of the corpus or the literature")

#: Both readings as committed: reader 1 at `e0857aa` (unchanged at `72617da`),
#: the blind reader at `c452d7d`; plus the frozen sample that maps one to the
#: other. A comparison is only meaningful against these exact bytes.
FROZEN_INPUT_SHA256 = {
    "artifacts/literature/wp4_claims/LIT2-000084.json": "64a13830e8993e988dcbc5afd9e5e195d95c7f2581c850166ec699ec0d247879",
    "artifacts/literature/wp4_claims/LIT2-000185.json": "d8b8692cae6c415bd5e7cb66d87314f880f211f7dd3e22d578633f5f8e441431",
    "artifacts/literature/wp4_claims/LIT2-000203.json": "8fe53b585cd70f8f80f4cbda9aad02c50bb4ddd4b0aa555a12333091b48ea9d5",
    "artifacts/literature/wp4_claims/LIT2-000315.json": "d299b7f7fe33ea807272aa14d5704cead2f7c328a0ed27086161d7a170b49814",
    "artifacts/literature/wp4_claims/LIT2-000366.json": "7a2861a13d64030f06d14cc5a2b6de0cef82deac026169eed3b388dfb62fdb3e",
    "artifacts/literature/wp4_claims/LIT2-000470.json": "e2b34c8c3f8e746e8e06a34379dcce9f3f60fdd21f277b266210f11670862c7e",
    "artifacts/literature/wp4_claims/LIT2-000499.json": "1303de7952a4e78144e844e8e6e879cf57f1abde27cba6d85dd3e8ff65be57c1",
    "artifacts/literature/wp4_claims/LIT2-000560.json": "ed522d4aed9b0dfd0bc119d3931084684b35444b7dc30fff566176ca05a99266",
    "artifacts/literature/wp4_claims/LIT2-000662.json": "cd6afe4b16a4f37356e466147d87f28b3515afc0227845da4e12ad160a8b609b",
    "artifacts/literature/wp4_claims/LIT2-000673.json": "e8616059ccb8ac52c2755567c8ea62f7548754e09485260d9696e9ad6ffe29f3",
    "artifacts/literature/wp4_claims/LIT2-000786.json": "49e59f868e90cc44fcfddefe34c2c2e99a222a8b02344bc97f1e9a2df201a6cc",
    "artifacts/literature/wp4_claims/LIT2-000803.json": "f3227011433a01ca4389cae293870a0087c08a3af1256981ae1b9b50d547c898",
    "artifacts/literature/wp4_claims/LIT2-000927.json": "81442b2ceab5a9224bf31bb0c1e977c9fd38db3accfb01f26314f88763645e35",
    "artifacts/literature/wp4_claims/LIT2-001063.json": "150de4503b214e209fe714eccbb45e4467aa0d37991d1d895e7144bfbf92a088",
    "artifacts/literature/wp4_claims/LIT2-001075.json": "f28bf702f0a614000b9821fda0f8e2cb3680e62f12f29c0cd6872b8b75fe5935",
    "artifacts/literature/wp4_claims/LIT2-001157.json": "91a33f608c6ad2954d6ca5c9f59f5df7abeedc611c555e448f867fac6911ebaf",
    "artifacts/literature/wp4_claims/LIT2-001160.json": "8df462946c0c038efaf842e63a1fb7a2a6373ef4aff2b0788b8c8931be1e369e",
    "artifacts/literature/wp4_claims/LIT2-001236.json": "482817f10479b04b6b0ff92bb85b5fb339de8b2e5fc54e175ba6d9f1da036829",
    "artifacts/literature/wp4_claims/LIT2-001293.json": "453d0ff6ed582cebd16596d3aed705823f9d54f6544a4908c861eb87390dc885",
    "artifacts/literature/wp4_claims/LIT2-001308.json": "1a2c46ce9f554821d53979968011da9cbc5efb68a0e2f09f7ce2e01a3c2564d9",
    "artifacts/literature/wp4_claims_summary.json": "e062f05086185ef2616fe5c47ca8fe4d294e389055b4725160737a9a364c9b02",
    "artifacts/literature/wp4_blind/154971876.json": "c8b1dcb3532c6f4deaf9161ec1c61a86060b818aec2e29c3ebb53ea0baa99a44",
    "artifacts/literature/wp4_blind/208499235.json": "eb9e032dd0e4192fdbd552adca73fe378d5c20e64c1faa5787b25c528adde582",
    "artifacts/literature/wp4_blind/211267687.json": "80226454a10eeb229bc4916ed81c779507e1796aa4243757da0fdd83a5047813",
    "artifacts/literature/wp4_blind/225397451.json": "ab4b7cbe16facdb8a2c151ccbc2b818a18c24e8be687ac654497678b6f86416d",
    "artifacts/literature/wp4_blind/229495849.json": "60d48520c517c3bd3d3078c7e8e453cf44c70217ca71698a35d8f7415d30d207",
    "artifacts/literature/wp4_blind/237371886.json": "2ec1e975d79f9f0b9dfd439495daa8456434136728348ff70583e88224820912",
    "artifacts/literature/wp4_blind/238725720.json": "17d4b8cb95e98c2c23bf7b1be8602bce097f73f8add4ab033c70f443000d662f",
    "artifacts/literature/wp4_blind/244714495.json": "f676559dc2881c4e69eb51ef99ae35fe9a34f3f212e38af7c17073e0b64a06b9",
    "artifacts/literature/wp4_blind/250039675.json": "130b718bcb08b7f72c8e895067958f4dd4311bcea6b02b577ec7aad6e6d8f4f6",
    "artifacts/literature/wp4_blind/250541813.json": "6982d23756b43963f3d03e83c78b50c0f110b52bb3d088d26c7dba9fdbf3bfcd",
    "artifacts/literature/wp4_blind/257108685.json": "5ba25d25af8ab9c5278116fc8c692e9f088b5d13fb376a3ee9b6a225b517dff1",
    "artifacts/literature/wp4_blind/257854681.json": "bd056d758883d464f8d96792c976bcae0a9eca9bf07fe3cd00dbde893c909230",
    "artifacts/literature/wp4_blind/266658220.json": "66c29c3b3c14cd10b5fb25f3297368a2983db948bb91ca2c756c5265014eadfe",
    "artifacts/literature/wp4_blind/272211804.json": "f523c8d9b8256e44f01097c34e2829ae5c33a88d6c70e68841a86167a21e7078",
    "artifacts/literature/wp4_blind/272852900.json": "6ccc22ec036c1c5d1a2c21a50c77147e71d98cbf8171f559a71d09738763d2f5",
    "artifacts/literature/wp4_blind/52918429.json": "394d54a03a2447404a212689bc9090d9a4c5b68e752a7010ae66f6bad3a8dff7",
    "artifacts/literature/wp4_blind/53109236.json": "53926b6ab7c3ca5ebf5cf93e2ece830c43e3029e775de33009d67ed820ec85bf",
    "artifacts/literature/wp4_blind/59342086.json": "4a0859a9a75cdb34f93ad35a7d57bf7d74bb371a8523eb802ab21c6e9e5baace",
    "artifacts/literature/wp4_blind/88523156.json": "1389a381b80c277db18be779cea54a1f2cf8d1f5c7405119e51ed826e8366273",
    "artifacts/literature/wp4_blind/999274.json": "b5278b9aa8ff548bbc2269cc918c825282de64bdef14c796db7eb33167af94da",
    "artifacts/literature/wp4_blind/wp4_blind_summary.json": "6eee6f79ad2ec6648fca6f01998f33c9f56a202f88b4a0816c0fb78d782fdccb",
    "artifacts/literature/wp4_sample.json": "f3cb5d0c3c4e0598860b2dad5a66219a3c252a92a7800d193111dec21fdcea15",
}

#: Read only to carry the hit-precision tables beside the adjudication; not an input to any rule.
HIT_CLASSIFICATION_SHA256 = "001d76c9ed3a3202969fd8968315b1a3d98ca661fed00af697f7fed8b7c30cc0"


# --- inputs ---------------------------------------------------------------------


def verify_inputs() -> dict:
    observed = {}
    for rel, expected in FROZEN_INPUT_SHA256.items():
        got = sha256_file(REPO_ROOT / rel)
        if got != expected:
            raise wp1b.AdjudicationError(f"{rel}: SHA-256 {got} != frozen {expected}")
        observed[rel] = got
    for d in (R1_DIR, R2_DIR):
        extra = {str(p.relative_to(REPO_ROOT)) for p in d.glob("*.json")} - set(FROZEN_INPUT_SHA256)
        if extra:
            raise wp1b.AdjudicationError(f"unpinned file(s) in a frozen reading: {sorted(extra)}")
    if sha256_file(HIT_CLASSIFICATION) != HIT_CLASSIFICATION_SHA256:
        raise wp1b.AdjudicationError("wp4_hit_classification.json differs from its committed bytes")
    return observed


def sample_items() -> list[dict]:
    """The twenty frozen items, in LIT2-id order."""
    sel = json.loads(SAMPLE.read_text(encoding="utf-8"))["selected"]
    return sorted(sel, key=lambda s: s["lit2_id"])


def lit2_ids() -> list[str]:
    return [s["lit2_id"] for s in sample_items()]


def load_r1() -> dict:
    return {i: json.loads((R1_DIR / f"{i}.json").read_text(encoding="utf-8")) for i in lit2_ids()}


def load_r2() -> dict:
    """Blind records keyed by LIT2 id (basename -> id through the frozen sample)."""
    b2i = {s["rel_path"].rsplit("/", 1)[1]: s["lit2_id"] for s in sample_items()}
    out = {}
    for p in sorted(R2_DIR.glob("*.json")):
        if p.name == R2_SUMMARY.name:
            continue
        rec = json.loads(p.read_text(encoding="utf-8"))
        if rec["source_basename"] != p.name:
            raise wp1b.AdjudicationError(f"{p.name}: source_basename {rec['source_basename']!r}")
        out[b2i[p.name]] = rec
    if set(out) != set(lit2_ids()):
        raise wp1b.AdjudicationError("the blind reading does not cover exactly the twenty sampled items")
    return out


# --- normalised views -----------------------------------------------------------


def _span(s: dict) -> dict:
    return {"json_path": norm_path(s["json_path"]), "char_start": s["char_start"], "char_end": s["char_end"],
            "evidence_text": s["evidence_text"]}


def _dim(d: dict, reader: int) -> dict:
    sup = d.get("support") if reader == 1 else d.get("support_span")
    out = {"value": d["value"], "tag": d["status"] if reader == 1 else d["tag"]}
    if sup:
        out["support"] = _span(sup)
    return out


def role_of(c: dict, reader: int) -> dict:
    """The recorded geography role, normalised: {value, tag, support?, class}."""
    r = c["geography"].get("role")
    if reader == 1:
        value, tag, sup = (r if r is not None else "unknown"), None, None
    else:
        r = r or {"value": "unknown", "tag": "unknown"}
        value, tag, sup = r["value"], r["tag"], r.get("support_span")
    out = {"value": value, "tag": tag, "class": role_class(value)}
    if sup:
        out["support"] = _span(sup)
    return out


def claims_of(rec: dict, reader: int) -> list[dict]:
    out = []
    for c in rec["claims"]:
        v = {"claim_id": c["claim_id"], "text": c["claim_text"] if reader == 1 else c["restatement"],
             "claim_type": c["claim_type"], "evidence": _span(c["evidence"])}
        for d in wp1b.DIMENSIONS:
            v[d] = _dim(c[d], reader)
        v["geography_role"] = role_of(c, reader)
        out.append(v)
    return out


def scope_of(rec: dict) -> tuple[str, str]:
    return rec["scope_status"], rec["scope_reason"]


def rejected_of(rec: dict, reader: int) -> list[dict]:
    if reader == 1:
        return [{"id": r["candidate_id"], "span": _span(r["evidence"]), "reason": r["reason"]}
                for r in rec["rejected_or_ambiguous"]]
    return [{"id": f"rejected[{i}]", "span": _span(r), "reason": r["reason"]}
            for i, r in enumerate(rec["rejected_or_ambiguous"])]


def verify_all_spans(corpus_root: Path, r1: dict, r2: dict) -> dict:
    """Re-slice every span of both readings from hash-verified sources. Fail closed."""
    counts = {"reader_1": 0, "reader_2": 0}
    for s in sample_items():
        iid = s["lit2_id"]
        doc, err = read_verified(Path(corpus_root) / s["rel_path"], s["sha256"])
        if err:
            raise wp1b.AdjudicationError(f"{iid}: {err}")
        for label, rec in (("reader_1", r1[iid]), ("reader_2", r2[iid])):
            for where, span in wp1b.iter_spans(rec):
                try:
                    wp1b.check_one_span(doc, {**span, "json_path": norm_path(span["json_path"])})
                except Exception as exc:  # noqa: BLE001 --- any failure is a stop condition
                    raise wp1b.AdjudicationError(f"{label} {iid}{where}: span fails to re-slice: {exc}") from exc
                counts[label] += 1
    return counts


# --- geography role ---------------------------------------------------------------

#: Role classes. `study_area` is the paper's own study / phenomenon geography;
#: `cited_study_area` the area of a cited study whose finding the claim restates
#: (the phenomenon geography of a background claim). Every other class says the
#: place is not the claim's study geography.
ROLE_CLASSES = ("study_area", "cited_study_area", "contextual", "data_source", "affiliation", "citation_or_person",
                "other", "unknown")
#: Classes whose place is the claim's study / phenomenon geography (G-R, m5wp4).
STUDY_ROLE_CLASSES = ("study_area", "cited_study_area")

#: Conservative order for rule 3-role: the class that grants a bridge least wins.
#: `unknown` beats a value (as rule 3a); any non-study class beats both study
#: classes; `cited_study_area` beats `study_area`. The order among the non-study
#: classes only picks a label --- none of them can reach G-1.
ROLE_CONSERVATIVE_ORDER = ("unknown", "citation_or_person", "affiliation", "other", "data_source", "contextual",
                           "cited_study_area", "study_area")

#: Every role string either reader recorded, mapped to a class. A string not
#: listed here fails the run (the mapping is a lookup, not a guess).
ROLE_CLASS_OF = {
    # blind reader: the rubric's categories (reader 1 also wrote "study area")
    "study area": "study_area",
    "contextual mention": "contextual",
    "data source": "data_source",
    "other": "other",
    "unknown": "unknown",
}


def role_class(value: str) -> str:
    """Class of a recorded role string; reader 1's free-text roles by `ROLE_CLASS_OF_R1`."""
    if value in ROLE_CLASS_OF:
        return ROLE_CLASS_OF[value]
    from climrr.wp4_judgements import ROLE_CLASS_OF_R1
    if value in ROLE_CLASS_OF_R1:
        cls = ROLE_CLASS_OF_R1[value]
        if cls not in ROLE_CLASSES:
            raise wp1b.AdjudicationError(f"role class {cls!r} for {value!r} is not in the vocabulary")
        return cls
    raise wp1b.AdjudicationError(f"geography role {value!r} has no recorded class")


def resolve_role(r1: dict, r2: dict, adopted_geography: dict | None) -> dict:
    """Rule 3-role on an aligned pair: classes agree -> agree; else the more conservative class.

    If the adopted geography is `unknown`, the role is `unknown` whatever the
    readers recorded (a role of no place). The adopted role keeps the winning
    reader's string and support; both readers' roles are recorded.
    """
    both = {"reader_1": r1, "reader_2": r2}
    if adopted_geography is not None and adopted_geography.get("tag") == "unknown":
        return {"agree": r1["class"] == r2["class"] == "unknown", "rule": "3-role: geography adopted unknown; role unknown",
                "adopted": {"value": "unknown", "class": "unknown"}, **both}
    if r1["class"] == r2["class"]:
        return {"agree": True, "rule": "3-role: same role class", "adopted": r1, **both}
    win = min((r1, r2), key=lambda r: ROLE_CONSERVATIVE_ORDER.index(r["class"]))
    who = "reader_1" if win is r1 else "reader_2"
    return {"agree": False, "rule": f"3-role: classes differ; more conservative class adopted ({who})",
            "adopted": win, **both}
