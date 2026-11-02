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
