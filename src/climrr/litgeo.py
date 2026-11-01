"""Geography of literature statements v2 (DR-SEED-1 v2 geography, D-047; pilot P2b-prep).

Each statement's `region` string and `region_scope` (as the extraction model proposed
them) get one **classification**, by the COORDINATOR ruling of 2026-11-01:

- scope `global` -> `global` (the scope alone is relevant only for global);
- scope `national` / `continental` -> `us_national` only if the string matches the U.S.
  gazetteer as a whole phrase (United States, U.S., US, USA, CONUS, contiguous / continental
  United States, North America), else `other`;
- scope `subnational` / `local` -> `state:<name>` / `nca:<name>` (several joined by `|`)
  only if the string contains a state name (`nca_regions_v1.yaml` State labels) or an NCA5
  region name as a whole phrase, after masking the phrases of
  `region_match_exclusions_v1.yaml` that block that name; else `other`;
- a region string that is empty / `unknown` / `unsupported`, or scope `unknown`, -> `unknown`.

Matching normalizes both sides: periods removed ("U.S." = "US"), lowercase, every other
character outside [a-z0-9] a space, whitespace collapsed; a phrase matches when it occurs
between word boundaries. The rule that fired is recorded with every classification.

**Relevance to a table pattern** (D-047): `global` and `us_national` statements are relevant
to every U.S. pattern; `state:<s>` to a state pattern for <s>; `nca:<r>` to a pattern whose
places (`itemseeds.pattern_places`: a state's NCA5 region, an NCA5-region pattern's region,
a regional contrast's covered regions) include <r>. Basis recorded, most specific first:
`state` > `nca_region` > `us_national` > `global`.

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from climrr.paths import REPO_ROOT

VERSION = "litgeo v1"
RULE_ID = "DR-SEED-1 v2 geography"
DECISION = "D-047"
EXCLUSIONS_PATH = REPO_ROOT / "data" / "metadata" / "geography" / "region_match_exclusions_v1.yaml"
#: Longest first; "U.S." and "US" normalize alike, so a match is reported as "US".
US_GAZETTEER = ("contiguous United States", "continental United States", "United States", "North America",
                "USA", "CONUS", "US", "U.S.")
UNNAMED = ("", "unknown", "unsupported")
CLASSES = ("us_national", "state", "nca", "global", "other", "unknown")
BASIS_ORDER = ("state", "nca_region", "us_national", "global")


def norm(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s.replace(".", "").lower()).split())


def contains(haystack_norm: str, phrase: str) -> bool:
    p = norm(phrase)
    return bool(p) and f" {p} " in f" {haystack_norm} "


def load_exclusions(path: Path = EXCLUSIONS_PATH) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


class Gazetteer:
    """State and NCA5 region names, the U.S. gazetteer and the exclusions, ready to match."""

    def __init__(self, nca: dict, exclusions: dict | None = None):
        ex = exclusions if exclusions is not None else load_exclusions()
        self.states = sorted(nca["state_region"])
        self.regions = sorted(nca["region_name"].values())
        self.state_region = {s: nca["region_name"][r] for s, r in nca["state_region"].items()}
        self.blocking = defaultdict(list)  # name -> normalized phrases masked before matching it
        for e in ex.get("exclusions") or []:
            for name in e["blocks"]:
                self.blocking[name].append(norm(e["phrase"]))
        self.ambiguous = {norm(a["string"]): a for a in ex.get("ambiguous") or []}

    def names_in(self, region: str) -> tuple[list[str], list[str], list[str]]:
        """(states, nca regions, exclusion phrases that masked a would-be match) whole-phrase in `region`."""
        r = norm(region)
        states, regions, masked = [], [], []
        for kind, names, out in (("state", self.states, states), ("nca", self.regions, regions)):
            for n in names:
                if not contains(r, n):
                    continue
                s = f" {r} "
                for ph in self.blocking.get(n, []):
                    s = s.replace(f" {ph} ", " ")
                if contains(s.strip(), n):
                    out.append(n)
                else:
                    masked += [ph for ph in self.blocking[n] if contains(r, ph)]
        return states, regions, sorted(set(masked))

    def us_term(self, region: str) -> str | None:
        r = norm(region)
        return next((t for t in US_GAZETTEER if contains(r, t)), None)


def classify(region: str | None, scope: str | None, gz: Gazetteer) -> dict:
    """{classification, class, states, nca_regions, rule, us_gazetteer_in_string, masked_by, ambiguous}."""
    region = region or ""
    term = gz.us_term(region)
    states, regions, masked = gz.names_in(region) if region.strip().lower() not in UNNAMED else ([], [], [])
    out = {"us_gazetteer_in_string": term, "masked_by": masked,
           "ambiguous": gz.ambiguous.get(norm(region), {}).get("may_be")}
    if scope == "global":
        cls, labels, rule = "global", [], "scope_global"
    elif region.strip().lower() in UNNAMED:
        cls, labels, rule = "unknown", [], "region_unnamed"
    elif scope in ("national", "continental"):
        cls, labels, rule = ("us_national", [], f"us_gazetteer:{term}") if term else ("other", [], f"{scope}_no_us_gazetteer")
    elif scope in ("subnational", "local"):
        labels = [f"state:{s}" for s in states] + [f"nca:{n}" for n in regions]
        if labels:
            cls, rule = labels[0].split(":")[0], "whole_phrase:" + "|".join(states + regions)
        else:
            cls, rule = "other", f"{scope}_no_state_or_nca_name" + (f" (masked by {', '.join(masked)})" if masked else "")
    else:
        cls, labels, rule = "unknown", [], f"scope_{scope}"
    if cls in ("state", "nca"):
        out.update(states=states, nca_regions=regions, classification="|".join(labels))
    else:
        out.update(states=[], nca_regions=[], classification=cls)
    out.update({"class": cls, "rule": rule})
    return out


def relevance(geo: dict, places: dict) -> str | None:
    """The basis on which a classified statement is relevant to a pattern's places, or None."""
    if any(s in geo["states"] for s in places["state"]):
        return "state"
    if any(n in geo["nca_regions"] for n in places["nca_region"]):
        return "nca_region"
    if geo["class"] == "us_national":
        return "us_national"
    if geo["class"] == "global":
        return "global"
    return None


def region_rows(statements: list[dict], gz: Gazetteer) -> list[dict]:
    """One row per distinct (region string, scope) over `statements` (ingested records): the inspection CSV."""
    by = defaultdict(list)
    for s in statements:
        by[(s["proposal"].get("region") or "", s["proposal"].get("region_scope") or "")].append(s)
    totals = Counter(s["proposal"].get("region") or "" for s in statements)
    rows = []
    for (region, scope), ss in sorted(by.items(), key=lambda kv: (-totals[kv[0][0]], kv[0][0], kv[0][1])):
        g = classify(region, scope, gz)
        roles = Counter(s["evidence_role"] for s in ss)
        rows.append({"region": region, "region_scope": scope, "count": len(ss), "region_count_all_scopes": totals[region],
                     "scopes_of_region": ";".join(f"{sc}:{n}" for (r, sc), n in sorted(
                         ((k, len(v)) for k, v in by.items() if k[0] == region), key=lambda x: (-x[1], x[0][1]))),
                     "classification": g["classification"], "class": g["class"], "rule": g["rule"],
                     "us_gazetteer_in_string": g["us_gazetteer_in_string"] or "",
                     "masked_by": ";".join(g["masked_by"]), "ambiguous": g["ambiguous"] or "",
                     "core": roles.get("core_candidate", 0), "cited": roles.get("cited_candidate", 0),
                     "background": roles.get("background_consensus_candidate", 0),
                     "statement_ids": ";".join(sorted(s["statement_id"] for s in ss))})
    return rows


CSV_COLUMNS = ("region", "region_scope", "count", "region_count_all_scopes", "scopes_of_region", "classification", "class",
               "rule", "us_gazetteer_in_string", "masked_by", "ambiguous", "core", "cited", "background", "statement_ids")
