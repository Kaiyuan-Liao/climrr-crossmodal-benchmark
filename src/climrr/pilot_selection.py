"""Pilot seed selection v1 (pilot P2b-fix; D-050): the ten seeds Kaiyuan chose from the shortlist.

`data/metadata/benchmark/pilot_selection_v1.yaml` is pinned by SHA-256 in `data/manifest.json`.
`load` reads it only when its bytes match the pin, and `check` holds it to the shortlist it was
chosen from: the shortlist's bytes match the hash the file records; every selected seed is on the
shortlist at the rung named; selected, excluded and unlisted seeds are disjoint and together are
the whole shortlist; the order runs 1..n.

No model call, no table value.
"""

from __future__ import annotations

import csv
from pathlib import Path

import yaml

from climrr.checksums import sha256_file
from climrr.manifest import MANIFEST_PATH, load_entry
from climrr.paths import REPO_ROOT

SELECTION_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "pilot_selection_v1.yaml"
EXCLUSION_REASONS = ("duplicate_quantity", "percent_change_near_zero_baseline")


def pinned_sha256(path: Path = SELECTION_PATH, manifest_path: Path = MANIFEST_PATH) -> str:
    return load_entry(Path(path).name, manifest_path)["sha256"]


def load(path: Path = SELECTION_PATH, manifest_path: Path = MANIFEST_PATH) -> dict:
    path = Path(path)
    pin = pinned_sha256(path, manifest_path)
    if sha256_file(path) != pin:
        raise ValueError(f"{path.name} differs from its manifest pin {pin}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def check(sel: dict, shortlist_path: Path | None = None) -> list[str]:
    """Problems with `sel` against the shortlist (empty when it holds)."""
    sl_path = Path(shortlist_path) if shortlist_path else REPO_ROOT / sel["shortlist"]["path"]
    errs = []
    if sha256_file(sl_path) != sel["shortlist"]["sha256"]:
        errs.append(f"shortlist {sl_path.name} differs from the hash the selection records")
    level = {r["seed_id"]: int(r["level"]) for r in csv.DictReader(open(sl_path, encoding="utf-8"))}
    chosen = [x["seed_id"] for x in sel["selected"]]
    if [x["order"] for x in sel["selected"]] != list(range(1, len(chosen) + 1)):
        errs.append("selection order is not 1..n")
    for x in sel["selected"]:
        if x["seed_id"] not in level:
            errs.append(f"{x['seed_id']} is not on the shortlist")
        elif level[x["seed_id"]] != x["rung"]:
            errs.append(f"{x['seed_id']}: rung {x['rung']} but shortlist level {level[x['seed_id']]}")
    excluded = [x["seed_id"] for x in sel.get("excluded_from_shortlist") or []]
    errs += [f"{x['seed_id']}: unknown exclusion reason {x['reason']}" for x in sel.get("excluded_from_shortlist") or []
             if x["reason"] not in EXCLUSION_REASONS]
    unlisted = list(sel.get("not_selected_no_reason_recorded") or [])
    every = chosen + excluded + unlisted
    if len(every) != len(set(every)):
        errs.append("a seed is listed more than once")
    if set(every) != set(level):
        errs.append(f"selection does not cover the shortlist exactly: missing {sorted(set(level) - set(every))}, "
                    f"extra {sorted(set(every) - set(level))}")
    return errs


def selected(sel: dict) -> list[dict]:
    """[{order, seed_id, rung, reason}] in item order."""
    return sorted(sel["selected"], key=lambda x: x["order"])


# --- selection v2 (work package P3a; D-059, D-060, D-061, D-064) -------------------------------------------------

SELECTION_V2_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "pilot_selection_v2.yaml"
V2_SOURCES = ("heat_shortlist", "fwi_shortlist")


def check_v2(sel: dict, seeds: dict) -> list[str]:
    """Problems with selection v2 (empty when it holds). `seeds`: {seed_id: v3 seed} of `item_seeds_v3.jsonl`. The
    source shortlists match the hashes the file records; a heat seed is on the v1 shortlist at the rung named; the
    fire-weather seeds are exactly the rule's picks (`pilot_shortlist.fwi_select`), in order, at rung 3; every seed is
    eligible in seeds v3 with the rung applicable; order 1..n with item ids BI-P3-<nnnn>; no seed twice."""
    from climrr import pilot_shortlist as ps

    errs = []
    for k in V2_SOURCES:
        if sha256_file(REPO_ROOT / sel["sources"][k]["path"]) != sel["sources"][k]["sha256"]:
            errs.append(f"{k} {sel['sources'][k]['path']} differs from the hash the selection records")
    level = {r["seed_id"]: int(r["level"]) for r in csv.DictReader(open(REPO_ROOT / sel["sources"]["heat_shortlist"]["path"],
                                                                         encoding="utf-8"))}
    xs = sorted(sel["selected"], key=lambda x: x["order"])
    if [x["order"] for x in xs] != list(range(1, len(xs) + 1)):
        errs.append("selection order is not 1..n")
    if [x["item_id"] for x in xs] != [f"BI-P3-{x['order']:04d}" for x in xs]:
        errs.append("item ids are not BI-P3-<order>")
    ids = [x["seed_id"] for x in xs]
    if len(ids) != len(set(ids)):
        errs.append("a seed is selected more than once")
    for x in xs:
        s = seeds.get(x["seed_id"])
        if x["source"] not in V2_SOURCES:
            errs.append(f"{x['seed_id']}: unknown source {x['source']}")
        if s is None:
            errs.append(f"{x['seed_id']}: not in item seeds v3")
            continue
        if not s["eligible_for_pilot"]:
            errs.append(f"{x['seed_id']}: not eligible in item seeds v3")
        if x["rung"] not in s["use_case_levels_applicable"]:
            errs.append(f"{x['seed_id']}: rung {x['rung']} not applicable in item seeds v3")
        if x["source"] == "heat_shortlist" and level.get(x["seed_id"]) != x["rung"]:
            errs.append(f"{x['seed_id']}: rung {x['rung']} but heat shortlist level {level.get(x['seed_id'])}")
    fwi = [x["seed_id"] for x in xs if x["source"] == "fwi_shortlist"]
    rule = [s["seed_id"] for s in ps.fwi_select(list(seeds.values()))]
    if fwi != rule:
        errs.append(f"fire-weather seeds {fwi} are not the shortlist rule's picks {rule}")
    errs += [f"{x['seed_id']}: a fire-weather seed must be at rung 3" for x in xs if x["source"] == "fwi_shortlist" and x["rung"] != 3]
    return errs


def threshold_conflicts(sel: dict, seeds: dict) -> list[dict]:
    """D-060 "one threshold per place per item set": heat-index seeds of the same place (state, region or the NCA5 region
    set) with different thresholds; graded text names no threshold, so their questions can read the same. Reported, not
    refused."""
    from climrr import synthpackets as spk

    by: dict = {}
    for x in sorted(sel["selected"], key=lambda x: x["order"]):
        s = seeds[x["seed_id"]]
        if s["family"] != "heat_index":
            continue
        by.setdefault(s["geography"], []).append((x["item_id"], x["seed_id"], spk.threshold(s["pattern"]), s["horizon"]))
    return [{"place": k, "items": [{"item_id": i, "seed_id": sid, "threshold_F": t, "horizon": h} for i, sid, t, h in v]}
            for k, v in sorted(by.items()) if len({t for _, _, t, _ in v}) > 1]
