"""M4-WP4 sample: 10 + 10 place candidates by the D-025 rank rule, frozen before any paper is opened.

**This module selects; it does not read.** Its only inputs are the frozen
place-candidate id lists and the LITCORPUS-02 arm manifests (item id, LIT2 id,
rel_path, SHA-256). No corpus file is fetched or opened, and no hit location,
section key or snippet is consulted: selection depends on LIT2 order, exact-byte
identity and rank alone, so no relevance judgement can enter it.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

LIT = REPO_ROOT / "artifacts" / "literature"
L2 = LIT / "litcorpus02"
SAMPLE_PATH = LIT / "wp4_sample.json"
FETCH_PATH = LIT / "wp4_sample_fetch.txt"

ARMS = ("fire_weather_v1", "extreme_heat_v1")  # predeclared arm order: fire first
STEP = {"fire_weather_v1": 10, "extreme_heat_v1": 14}
PER_ARM = 10

#: Committed SHA-256 of every input (place_candidates.json / litcorpus02_manifest.json at 85ed69a).
INPUT_SHA256 = {
    "artifacts/literature/litcorpus02/place_candidates/fire_weather_v1_place_candidates.txt":
        "122ee177f45dd98ecb76765a7ce0e8c543261694c5e991380ab94139d756a149",
    "artifacts/literature/litcorpus02/place_candidates/extreme_heat_v1_place_candidates.txt":
        "eb28845e43bbd63875a8ac7b25f64fef9aabb07abde69a7ae75e14bb689c623c",
    "artifacts/literature/litcorpus02/fire_weather_v1_manifest.csv":
        "e0943c668f9fb2442385edd87e93fdaf2c27d3f297191292e40f86488dffedc4",
    "artifacts/literature/litcorpus02/extreme_heat_v1_manifest.csv":
        "5de3e7aef402f0beed606f50ee61c210c84f4a2c838eea66e26535402a43da2d",
}

RULE = (
    "D-025 (docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md, evidence check 6). Per arm, in the order "
    "fire_weather_v1 then extreme_heat_v1: (1) start from the frozen place-candidate list; (2) sort ascending by "
    "LIT2 id (code-point order of the 'LIT2-NNNNNN' string); (3) remove later members of exact-byte duplicate "
    "groups (same SHA-256 within the arm) for sampling only, recording each suppression; (4) assign ranks 1..N; "
    "(5) select ranks 10,20,...,100 (fire_weather_v1) and 14,28,...,140 (extreme_heat_v1). If a selected rank does "
    "not exist after suppression, or is already used, advance to the next higher unused rank. If an item selected "
    "for extreme_heat_v1 is already in the fire_weather_v1 sample, keep it in fire_weather_v1 and advance "
    "extreme_heat_v1 to the next higher unused rank. Exactly 10 unique items per arm; 20 distinct items overall. "
    "No manual replacement; no file is opened."
)


class SampleError(RuntimeError):
    """An input differs from its committed hash, or the rule cannot be satisfied."""


def _rel(p: Path) -> str:
    return p.relative_to(REPO_ROOT).as_posix()


def verify_inputs() -> dict[str, str]:
    for rel, want in INPUT_SHA256.items():
        got = sha256_file(REPO_ROOT / rel)
        if got != want:
            raise SampleError(f"{rel}: SHA-256 {got} differs from the committed {want}")
    return dict(INPUT_SHA256)


def ranked(arm: str) -> tuple[list[dict], list[dict]]:
    """(ranked candidates after suppression, suppressions) for one arm."""
    with (L2 / f"{arm}_manifest.csv").open(encoding="utf-8", newline="") as f:
        man = {r["item_id"]: r for r in csv.DictReader(f)}
    ids = [x.strip() for x in (L2 / "place_candidates" / f"{arm}_place_candidates.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
    missing = [i for i in ids if i not in man]
    if missing:
        raise SampleError(f"{arm}: candidates not in the arm manifest: {missing}")
    rows = sorted((man[i] for i in ids), key=lambda r: r["lit2_id"])
    kept, suppressed, first = [], [], {}
    for r in rows:
        if r["sha256"] in first:
            suppressed.append({"item_id": r["item_id"], "lit2_id": r["lit2_id"], "sha256": r["sha256"],
                               "duplicate_of_item_id": first[r["sha256"]]["item_id"],
                               "duplicate_of_lit2_id": first[r["sha256"]]["lit2_id"],
                               "note": "later member of an exact-byte duplicate group; suppressed for sampling only"})
        else:
            first[r["sha256"]] = r
            kept.append(r)
    return ([{"rank": k, "item_id": r["item_id"], "lit2_id": r["lit2_id"], "rel_path": r["rel_path"],
              "sha256": r["sha256"]} for k, r in enumerate(kept, 1)], suppressed)


def select(ranked_by_arm: dict[str, list[dict]]) -> dict[str, list[dict]]:
    chosen: dict[str, list[dict]] = {}
    taken: set[str] = set()
    for arm in ARMS:
        cands = ranked_by_arm[arm]
        used: set[int] = set()
        picks = []
        for target in range(STEP[arm], STEP[arm] * PER_ARM + 1, STEP[arm]):
            r, reasons = target, []
            while True:
                if r > len(cands):
                    raise SampleError(f"{arm}: target rank {target} cannot be satisfied (N = {len(cands)})")
                item = cands[r - 1]
                if r in used:
                    reasons.append(f"rank {r} already used")
                elif item["item_id"] in taken:
                    reasons.append(f"rank {r} ({item['item_id']}) already in an earlier arm's sample")
                else:
                    break
                r += 1
            used.add(r)
            taken.add(item["item_id"])
            picks.append({**item, "arm": arm, "target_rank": target, "advanced": r != target,
                          "advance_reasons": reasons})
        chosen[arm] = picks
    return chosen


def build() -> dict:
    inputs = verify_inputs()
    per_arm, ranked_by_arm = {}, {}
    for arm in ARMS:
        ranks, sup = ranked(arm)
        ranked_by_arm[arm] = ranks
        per_arm[arm] = {"n_candidates": len(ranks) + len(sup), "n_suppressed": len(sup), "n_ranked": len(ranks),
                        "suppressions": sup, "ranked_candidates": ranks}
    chosen = select(ranked_by_arm)
    selected = [{k: p[k] for k in ("item_id", "lit2_id", "arm", "rank", "target_rank", "advanced",
                                   "advance_reasons", "rel_path", "sha256")} for arm in ARMS for p in chosen[arm]]
    if len({s["item_id"] for s in selected}) != len(ARMS) * PER_ARM:
        raise SampleError("the sample is not 20 distinct items")
    return {
        "package": "M4-WP4 (20-paper two-reader candidate-reading pilot)",
        "authorized_by": "docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md (D-025)",
        "corpus_id": "LITCORPUS-02-conceptfirst-705k-v1",
        "rule": RULE,
        "statement": "Deterministic candidate sample frozen before reading; relevance-guided by concept and place "
                     "terms, not representative. No file has been fetched or opened.",
        "input_sha256": inputs,
        "arms": per_arm,
        "selected": selected,
        "n_selected": len(selected),
        "selected_sha256": hashlib.sha256(json.dumps(selected, sort_keys=True, ensure_ascii=False)
                                          .encode("utf-8")).hexdigest(),
        "selected_sha256_rule": "SHA-256 of json.dumps(selected, sort_keys=True, ensure_ascii=False), UTF-8. "
                                "The file's own SHA-256 (wp4_sample_sha256) is recorded in data/manifest.json.",
    }


def write() -> dict:
    doc = build()
    SAMPLE_PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    FETCH_PATH.write_text("".join(f"{s['rel_path']}\n" for s in doc["selected"]), encoding="utf-8")
    return doc


def verify() -> None:
    """The frozen sample equals a rebuild from the hash-verified inputs."""
    if json.loads(SAMPLE_PATH.read_text(encoding="utf-8")) != build():
        raise SampleError("artifacts/literature/wp4_sample.json differs from a rebuild")
    want = "".join(f"{s['rel_path']}\n" for s in build()["selected"])
    if FETCH_PATH.read_text(encoding="utf-8") != want:
        raise SampleError("wp4_sample_fetch.txt differs from the sample")
