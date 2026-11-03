"""Pattern-level descriptors (DR-DESC-1; pilot P2b-final-prep; D-055).

For each table pattern of a seed packet, `descriptors` returns the words the graded text of an item may use:
direction word, magnitude class from mean_to / mean_from, the low-baseline phrase, a coarse anchor pair, the
relative-tercile descriptor (D-041), for a regional contrast the ranking with "largest / smallest" words, and the
horizon, scenario and quantity phrases. Rules and thresholds: `data/metadata/benchmark/descriptor_rules_v1.yaml`,
read only when its bytes match the manifest pin.

**v2** (`descriptor_rules_v2.yaml`, D-055c) adds, when the rules carry them, the "rising from rare to common" class
(an increase with ratio > 10 or a baseline below 2 days; its own anchor pair) and `negligible_regions` for a regional
contrast (a region whose change rounds to 0.0 days; `smallest` then says "essentially no change"). With v1 rules the
output is v1's, unchanged: the seed packets stay v1 (frozen for the pilot); v2 serves the edited texts and the mentor
sheet.

`phrases` flattens a descriptor record into the strings the post-checks accept (`checks_input.allowed_descriptors`).

No model call; no table value computed beyond the ratio of two values the pattern stores.
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

import yaml

from climrr.checksums import sha256_file
from climrr.manifest import MANIFEST_PATH, load_entry
from climrr.paths import REPO_ROOT

RULES_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "descriptor_rules_v1.yaml"
RULES_V2_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "descriptor_rules_v2.yaml"
_THRESHOLD = re.compile(r"above (\d+) F\b")


def load_rules(path: Path = RULES_PATH, manifest_path: Path = MANIFEST_PATH) -> dict:
    path = Path(path)
    pin = load_entry(path.name, manifest_path)["sha256"]
    if sha256_file(path) != pin:
        raise ValueError(f"{path.name} differs from its manifest pin {pin}")
    return dict(yaml.safe_load(path.read_text(encoding="utf-8")), sha256=pin)


def magnitude_class(ratio: Decimal, direction: str, rules: dict) -> str | None:
    """The first class whose [lower, upper) holds `ratio` (upper inclusive where marked); an increase only."""
    if direction != "increase":
        return None
    for c in rules["magnitude"]["classes"]:
        lo = Decimal(str(c["lower"])) if "lower" in c else None
        hi = Decimal(str(c["upper"])) if "upper" in c else None
        if (lo is None or ratio >= lo) and (hi is None or ratio < hi or (c.get("inclusive_upper") and ratio == hi)):
            return c["increase"]
    return None


def anchor(v: str) -> int:
    return round(float(v))


def _unit(n: int, unit: str, rules: dict) -> str:
    return unit[:-1] if unit.endswith("s") and n == rules["anchor"]["unit_singular_at"] else unit


def _rare_end(n: int, unit: str, r2: dict, rules: dict) -> str:
    return r2["end_zero"] if n == 0 else r2["end"].format(n=n, unit=_unit(n, unit, rules)).strip()


def rare_to_common(mf: str, mt: str, direction: str, rules: dict) -> bool:
    """v2: an increase with mean_to / mean_from > the ratio bound, or a baseline below the day bound."""
    r2 = rules["magnitude"].get("rare_to_common")
    if not r2 or direction != "increase":
        return False
    a, b = Decimal(mf), Decimal(mt)
    return a < Decimal(str(r2["baseline_below"])) or (a > 0 and b / a > Decimal(str(r2["ratio_above"])))


def negligible(value: str, rules: dict) -> bool:
    n = rules["regional"].get("negligible")
    return bool(n) and round(float(value), n["decimals"]) == n["rounds_to"]


def descriptors(p: dict, rules: dict) -> dict:
    """The DR-DESC-1 descriptor record for pattern `p`."""
    v = p["computed_value_or_range"]
    window = p["horizon_window"].replace("-", rules["horizon"]["window_dash"])
    out = {"pattern_id": p["pattern_id"], "rule": rules["rule"], "rules_sha256": rules["sha256"],
           "direction": rules["direction_words"].get(p["direction"], p["direction"]),
           "horizon": rules["horizon"][p["horizon"]].format(window=window) if p["horizon"] in rules["horizon"] else None,
           "scenario": rules["scenario"].get(p["scenario"]), "quantity": None,
           "magnitude_class": None, "magnitude_note": None, "magnitude_also_allowed": [], "anchor_pair": None, "anchors": [], "tercile": None}
    t = _THRESHOLD.search(p.get("metric_wording") or "")
    if p["metric"].startswith("heatindex_days") and t:
        out["quantity"] = rules["quantity"]["heatindex_days"].format(threshold=t.group(1))
    if p["pattern_kind"] == "regional_contrast":
        ranked = [r for r in v["regions_ordered"] if r.get("value") is not None]
        names = [r["name"] for r in ranked]
        out.update(ranking_largest_first=names, not_ranked=[r["name"] for r in v["regions_ordered"] if r.get("value") is None],
                   largest=rules["regional"]["largest"].format(direction=out["direction"], region=names[0]) if names else None,
                   smallest=rules["regional"]["smallest"].format(direction=out["direction"], region=names[-1]) if names else None,
                   magnitude_note="no magnitude class: a regional contrast stores no baseline mean")
        if rules["regional"].get("negligible"):
            neg = [r["name"] for r in ranked if negligible(r["value"], rules)]
            out["negligible_regions"] = neg
            if neg:
                out["smallest"] = rules["regional"]["negligible"]["smallest"].format(regions=", ".join(neg))
        return out
    mf, mt = v.get("mean_from"), v.get("mean_to")
    if mf is not None and mt is not None:
        unit = "days" if p["metric"].startswith("heatindex_days") else (v.get("unit") or "")
        a, b = anchor(mf), anchor(mt)
        out["anchor_pair"] = rules["anchor"]["pair"].format(**{"from": a, "to": b, "unit": _unit(b, unit, rules)}).strip()
        out["anchors"] = [rules["anchor"]["single"].format(n=n, unit=_unit(n, unit, rules)).strip() for n in (a, b)]
        if rare_to_common(mf, mt, p["direction"], rules):
            r2 = rules["magnitude"]["rare_to_common"]
            out["magnitude_class"] = r2["class"]
            out["anchor_pair"] = r2["pair"].format(**{"from": _rare_end(a, unit, r2, rules), "to": _rare_end(b, unit, r2, rules)})
            out["anchors"] = [_rare_end(n, unit, r2, rules) for n in (a, b)]
            out["magnitude_note"] = (f"rising from rare to common (D-055c): ratio {Decimal(mt) / Decimal(mf):.1f}" if Decimal(mf) > 0
                                     else "rising from rare to common (D-055c): baseline 0") + f", baseline {float(mf):.1f} days"
        elif Decimal(mf) < Decimal(str(rules["magnitude"]["low_baseline"]["below"])):
            out["magnitude_class"] = rules["magnitude"]["low_baseline"]["phrase"].format(future_anchor=out["anchors"][1])
            out["magnitude_note"] = "baseline mean below 1 day per season: low-baseline phrase, no ratio class"
        else:
            out["magnitude_class"] = magnitude_class(Decimal(mt) / Decimal(mf), p["direction"], rules)
            if out["magnitude_class"] is None:
                out["magnitude_note"] = f"no magnitude class for direction {p['direction']}"
            else:
                c = next(c for c in rules["magnitude"]["classes"] if c.get(p["direction"]) == out["magnitude_class"])
                out["magnitude_also_allowed"] = list(c.get("also_allowed") or [])
    else:
        out["magnitude_note"] = "no magnitude class: the pattern stores no baseline and future mean"
    rm = p.get("relative_magnitude")
    if rm:
        out["tercile"] = rules["tercile"]["phrase"].format(**{"class": rm["class"], "tercile": rules["tercile"]["words"][rm["class"]]})
    return out


def phrases(d: dict) -> list[str]:
    """Every string of descriptor record `d` the graded text may copy."""
    keys = ("direction", "horizon", "scenario", "quantity", "magnitude_class", "anchor_pair", "tercile", "largest", "smallest")
    out = [d[k] for k in keys if d.get(k)] + list(d.get("anchors") or []) + list(d.get("magnitude_also_allowed") or [])
    out += list(d.get("ranking_largest_first") or [])
    return list(dict.fromkeys(out))
