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

**v3** (`descriptor_rules_v3.yaml`, D-060, D-061; work package P3a) removes the RCP label, the threshold and the years
from every phrase: horizon "by mid-century" / "by late this century", scenario "under a high-emissions future", the
quantity from `plain_language_v1.yaml` by family (no threshold), and the anchor pair ending with the season unit ("from
about 16 to about 45 days a summer"). The day-count rules (rare to common, low baseline, anchors) apply only to the
rules' `day_count_families`; another family (fire weather: an index value) gets the ratio classes only. A pattern whose
scenario the dictionary leaves unstated takes the scenario of the owner-authorized working assumption the rules name
(D-064), recorded in `scenario_working_assumption`. With v1 or v2 rules the output is unchanged. The seed packets v4
carry v3 descriptors.

**v4** (`descriptor_rules_v4.yaml`, D-066; work package P3b) keeps v3's phrases and adds, per record, the `forms` the
graded text may use interchangeably: `magnitude_forms` for the magnitude class ("a slight increase", "increase slightly",
...), and the relative tercile as a comparison with other states (`tercile_class`, `tercile_forms`; `tercile` is None ---
"tercile" is never written). The rare rule changes: "rising from rare to common" only for a baseline below 2 days and a
future of at least 10 days; a baseline below 2 days with a future below 10 days is "remaining rare" (anchor "from
essentially none to about 1 day a summer"). `descriptors` dispatches to `descriptors_v4` on v4 rules; v1 -- v3 output is
unchanged.

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
RULES_V3_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "descriptor_rules_v3.yaml"
RULES_V4_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "descriptor_rules_v4.yaml"
V4 = "descriptor_rules_v4"
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


def _per_season(p: dict, rules: dict) -> str:
    """v3: the season unit the anchor pair ends with ("a summer"); empty for v1 / v2 rules and an unlisted season."""
    return (rules["anchor"].get("per_season") or {}).get(p.get("season"), "")


def _day_count(p: dict, rules: dict) -> bool:
    """v3: whether the day-count rules apply to the pattern's family (always, for v1 / v2 rules)."""
    return "day_count_families" not in rules or p.get("family") in rules["day_count_families"]


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


def descriptors(p: dict, rules: dict, plain: dict | None = None) -> dict:
    """The DR-DESC-1 descriptor record for pattern `p`. `plain`: the plain-language phrases v3 rules take the quantity
    from (default: the pinned `plain_language_v1.yaml`); unused with v1 / v2 rules. v4 rules: `descriptors_v4`."""
    if rules.get("version") == V4:
        return descriptors_v4(p, rules, plain)
    v = p["computed_value_or_range"]
    window = p["horizon_window"].replace("-", rules["horizon"].get("window_dash", "-"))   # v3 phrases carry no window
    out = {"pattern_id": p["pattern_id"], "rule": rules["rule"], "rules_sha256": rules["sha256"],
           "direction": rules["direction_words"].get(p["direction"], p["direction"]),
           "horizon": rules["horizon"][p["horizon"]].format(window=window) if p["horizon"] in ("mid", "end") and p["horizon"] in rules["horizon"] else None,
           "scenario": rules["scenario"].get(p["scenario"]), "quantity": None,
           "magnitude_class": None, "magnitude_note": None, "magnitude_also_allowed": [], "anchor_pair": None, "anchors": [], "tercile": None}
    wa = (rules.get("scenario_working_assumption") or {}).get(p["scenario"])
    if out["scenario"] is None and wa:
        out["scenario"] = rules["scenario"].get(wa["scenario"])
        out["scenario_working_assumption"] = {"assumed": wa["scenario"], "resolution": wa["resolution"]}
    t = _THRESHOLD.search(p.get("metric_wording") or "")
    if rules.get("quantity_source"):
        from climrr import plain_language
        out["quantity"] = plain_language.quantity(p["family"], plain)
    elif p["metric"].startswith("heatindex_days") and t:
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
    if mf is not None and mt is not None and not _day_count(p, rules):
        if Decimal(mf) > 0:
            out["magnitude_class"] = magnitude_class(Decimal(mt) / Decimal(mf), p["direction"], rules)
        out["magnitude_note"] = ("not a day count: ratio classes only, no anchors (DR-DESC-1 v3)" if out["magnitude_class"]
                                 else f"not a day count: no magnitude class for direction {p['direction']} or a baseline <= 0")
        if out["magnitude_class"]:
            c = next(c for c in rules["magnitude"]["classes"] if c.get(p["direction"]) == out["magnitude_class"])
            out["magnitude_also_allowed"] = list(c.get("also_allowed") or [])
    elif mf is not None and mt is not None:
        unit = "days" if p["metric"].startswith("heatindex_days") else (v.get("unit") or "")
        a, b = anchor(mf), anchor(mt)
        out["anchor_pair"] = rules["anchor"]["pair"].format(**{"from": a, "to": b, "unit": _unit(b, unit, rules),
                                                               "per_season": _per_season(p, rules)}).strip()
        out["anchors"] = [rules["anchor"]["single"].format(n=n, unit=_unit(n, unit, rules)).strip() for n in (a, b)]
        if rare_to_common(mf, mt, p["direction"], rules):
            r2 = rules["magnitude"]["rare_to_common"]
            out["magnitude_class"] = r2["class"]
            out["anchor_pair"] = r2["pair"].format(**{"from": _rare_end(a, unit, r2, rules), "to": _rare_end(b, unit, r2, rules),
                                                      "per_season": _per_season(p, rules)}).strip()
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
    """Every string of descriptor record `d` the graded text may copy (v4: also every magnitude and tercile form)."""
    keys = ("direction", "horizon", "scenario", "quantity", "magnitude_class", "anchor_pair", "tercile", "largest", "smallest")
    out = [d[k] for k in keys if d.get(k)] + list(d.get("anchors") or []) + list(d.get("magnitude_also_allowed") or [])
    out += list(d.get("magnitude_forms") or []) + list(d.get("tercile_forms") or [])
    out += list(d.get("ranking_largest_first") or [])
    return list(dict.fromkeys(out))


# --- v4 (DR-DESC-1 v4, D-066; work package P3b) ------------------------------------------------------------------


def _class_record(ratio: Decimal, direction: str, rules: dict) -> dict | None:
    name = magnitude_class(ratio, direction, rules)
    return next(c for c in rules["magnitude"]["classes"] if c.get(direction) == name) if name else None


def rare_class(mf: str, mt: str, direction: str, rules: dict) -> str | None:
    """v4: "rare_to_common" (baseline < 2 days and future >= 10 days), "remaining_rare" (baseline < 2 days and future
    < 10 days), or None; an increase only."""
    m = rules["magnitude"]
    if direction != "increase":
        return None
    a, b = Decimal(mf), Decimal(mt)
    rc, rr = m["rare_to_common"], m["remaining_rare"]
    if a < Decimal(str(rc["baseline_below"])) and b >= Decimal(str(rc["future_at_least"])):
        return "rare_to_common"
    if a < Decimal(str(rr["baseline_below"])) and b < Decimal(str(rr["future_below"])):
        return "remaining_rare"
    return None


def descriptors_v4(p: dict, rules: dict, plain: dict | None = None) -> dict:
    """The DR-DESC-1 v4 record: v3's fields, with `magnitude_forms`, `tercile_class` and `tercile_forms`; `tercile` and
    `magnitude_also_allowed` stay empty (the forms replace them)."""
    from climrr import plain_language

    v = p["computed_value_or_range"]
    out = {"pattern_id": p["pattern_id"], "rule": rules["rule"], "rules_sha256": rules["sha256"],
           "direction": rules["direction_words"].get(p["direction"], p["direction"]),
           "horizon": rules["horizon"].get(p["horizon"]), "scenario": rules["scenario"].get(p["scenario"]),
           "quantity": plain_language.quantity(p["family"], plain),
           "magnitude_class": None, "magnitude_forms": [], "magnitude_note": None, "magnitude_also_allowed": [],
           "anchor_pair": None, "anchors": [], "tercile": None, "tercile_class": None, "tercile_forms": []}
    wa = (rules.get("scenario_working_assumption") or {}).get(p["scenario"])
    if out["scenario"] is None and wa:
        out["scenario"] = rules["scenario"].get(wa["scenario"])
        out["scenario_working_assumption"] = {"assumed": wa["scenario"], "resolution": wa["resolution"]}
    if p["pattern_kind"] == "regional_contrast":
        ranked = [r for r in v["regions_ordered"] if r.get("value") is not None]
        names = [r["name"] for r in ranked]
        neg = [r["name"] for r in ranked if negligible(r["value"], rules)]
        out.update(ranking_largest_first=names, not_ranked=[r["name"] for r in v["regions_ordered"] if r.get("value") is None],
                   largest=rules["regional"]["largest"].format(direction=out["direction"], region=names[0]) if names else None,
                   smallest=rules["regional"]["smallest"].format(direction=out["direction"], region=names[-1]) if names else None,
                   negligible_regions=neg, magnitude_note="no magnitude class: a regional contrast stores no baseline mean")
        if neg:
            out["smallest"] = rules["regional"]["negligible"]["smallest"].format(regions=", ".join(neg))
        return out
    mf, mt = v.get("mean_from"), v.get("mean_to")
    if mf is None or mt is None:
        out["magnitude_note"] = "no magnitude class: the pattern stores no baseline and future mean"
    elif not _day_count(p, rules):
        c = _class_record(Decimal(mt) / Decimal(mf), p["direction"], rules) if Decimal(mf) > 0 else None
        if c:
            out["magnitude_class"], out["magnitude_forms"] = c[p["direction"]], list(c["forms"])
            out["magnitude_note"] = "not a day count: ratio classes only, no anchors (DR-DESC-1 v4)"
        else:
            out["magnitude_note"] = f"not a day count: no magnitude class for direction {p['direction']} or a baseline <= 0"
    else:
        unit = "days" if p["metric"].startswith("heatindex_days") else (v.get("unit") or "")
        a, b = anchor(mf), anchor(mt)
        rare = rare_class(mf, mt, p["direction"], rules)
        if rare:
            r = rules["magnitude"][rare]
            ends = rules["magnitude"]["rare_to_common"]                 # both rare classes render their ends alike
            out["magnitude_class"], out["magnitude_forms"] = r["class"], list(r["forms"])
            out["anchor_pair"] = r["pair"].format(**{"from": _rare_end(a, unit, ends, rules), "to": _rare_end(b, unit, ends, rules),
                                                     "per_season": _per_season(p, rules)}).strip()
            out["anchors"] = [_rare_end(n, unit, ends, rules) for n in (a, b)]
            out["magnitude_note"] = (f"{r['class']} (DR-DESC-1 v4): baseline {float(mf):.1f} days, future {float(mt):.1f} days")
        else:
            out["anchor_pair"] = rules["anchor"]["pair"].format(**{"from": a, "to": b, "unit": _unit(b, unit, rules),
                                                                   "per_season": _per_season(p, rules)}).strip()
            out["anchors"] = [rules["anchor"]["single"].format(n=n, unit=_unit(n, unit, rules)).strip() for n in (a, b)]
            c = _class_record(Decimal(mt) / Decimal(mf), p["direction"], rules) if Decimal(mf) > 0 else None
            if c:
                out["magnitude_class"], out["magnitude_forms"] = c[p["direction"]], list(c["forms"])
            else:
                out["magnitude_note"] = f"no magnitude class for direction {p['direction']}"
    rm = p.get("relative_magnitude")
    if rm:
        out["tercile_class"] = rm["class"]
        out["tercile_forms"] = list(rules["tercile"]["forms"][rm["class"]])
    return out
