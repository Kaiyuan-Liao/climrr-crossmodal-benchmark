"""Geography of literature statements (DR-SEED-1 v2 geography, D-047, amended by D-047a; pilot P2b).

Two rule versions; `Gazetteer(..., version=)` picks one. **v1** (D-047) is kept byte-for-byte so the
P2b-prep artifacts it produced (`region_strings_v1.csv`, `item_seeds_v2.jsonl`, `partitions_v1.jsonl`)
stay reproducible; **v2** (D-047a) is the default and is what the synthesis packets use.

**v1.** Each statement's `region` string and `region_scope` (as the extraction model proposed
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

**v2** (D-047a, COORDINATOR ruling 2026-11-01, second set). A region string that **names the United
States** (`US_NAMES`: United States, U.S., US, USA, contiguous / continental / conterminous United States,
CONUS, lower 48 --- not "North America") is U.S.-wide **regardless of scope**:

- with a **directional or regional qualifier** -> `us_subregion`, the qualifier recorded. The string minus
  every U.S. name and the national-extent words (`NATIONAL_EXTENT`), function words trimmed from its ends,
  is the qualifier when it holds a word of `DIRECTIONAL` or `REGIONAL` ("southeastern United States" ->
  "southeastern"; "dry ecoregions of the United States" -> "dry ecoregions"). No qualifier-to-state or
  -to-region mapping;
- otherwise -> `us_national` (a remainder with no such word, e.g. other countries in a multi-country string,
  or a city: "Houston, TX, USA", stays `us_national`).

Order (EXECUTOR): under a subnational / local scope a whole-phrase state / NCA5 name still wins (v1 rule,
unchanged: "north-central Minnesota, USA" -> `state:Minnesota`); then a U.S. name; then the v1 rules
(scope `global`; unnamed; "North America" under a national / continental scope -> `us_national`; else
`other` / `unknown`). Relevance: `us_subregion` is relevant to every U.S. pattern; basis order `state` >
`nca_region` > `us_subregion` > `us_national` > `global`.

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from climrr.paths import REPO_ROOT

VERSION = "litgeo v2"
VERSION_V1 = "litgeo v1"
RULE_ID = "DR-SEED-1 v2 geography (D-047a)"
DECISION = "D-047, D-047a"
EXCLUSIONS_PATH = REPO_ROOT / "data" / "metadata" / "geography" / "region_match_exclusions_v1.yaml"
#: v1 (D-047) gazetteer. Longest first; "U.S." and "US" normalize alike, so a match is reported as "US".
US_GAZETTEER = ("contiguous United States", "continental United States", "United States", "North America",
                "USA", "CONUS", "US", "U.S.")
UNNAMED = ("", "unknown", "unsupported")
CLASSES_V1 = ("us_national", "state", "nca", "global", "other", "unknown")
BASIS_ORDER_V1 = ("state", "nca_region", "us_national", "global")
CLASSES = ("us_national", "us_subregion", "state", "nca", "global", "other", "unknown")
BASIS_ORDER = ("state", "nca_region", "us_subregion", "us_national", "global")
#: v2 (D-047a): strings that name the United States, longest first ("U.S." and "US" normalize alike).
US_NAMES = ("contiguous United States", "continental United States", "conterminous United States", "United States",
            "lower 48", "USA", "CONUS", "US", "U.S.")
#: Words that state the national extent, not a part of it; dropped before the qualifier is read.
NATIONAL_EXTENT = frozenset("contiguous continental conterminous entire whole mainland".split())
#: A remainder is a qualifier when it holds one of these words (normalized).
DIRECTIONAL = frozenset("""north south east west northern southern eastern western northeast northeastern northwest
northwestern southeast southeastern southwest southwestern central midwest midwestern upper interior""".split())
REGIONAL = frozenset("""region regions regional ecoregion ecoregions coast coasts coastal gulf plains mountain mountains
rockies rocky basin basins valley valleys desert deserts lakes appalachia appalachian""".split())
_EDGE_WORDS = frozenset("the of in and or across over within throughout parts part".split())


def norm(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s.replace(".", "").lower()).split())


def contains(haystack_norm: str, phrase: str) -> bool:
    p = norm(phrase)
    return bool(p) and f" {p} " in f" {haystack_norm} "


def load_exclusions(path: Path = EXCLUSIONS_PATH) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


class Gazetteer:
    """State and NCA5 region names, the U.S. gazetteer and the exclusions, ready to match."""

    def __init__(self, nca: dict, exclusions: dict | None = None, version: str = "v2"):
        if version not in ("v1", "v2"):
            raise ValueError(f"unknown geography rule version {version!r}")
        self.version = version
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


def us_name(region: str) -> str | None:
    """v2: the first `US_NAMES` phrase in `region` (whole phrase), or None."""
    r = norm(region)
    return next((t for t in US_NAMES if contains(r, t)), None)


def us_qualifier(region: str) -> str | None:
    """v2: the directional / regional qualifier of a string that names the United States, or None (module docstring)."""
    s = f" {norm(region)} "
    for t in US_NAMES:
        p = norm(t)
        while f" {p} " in s:
            s = s.replace(f" {p} ", " ")
    words = [w for w in s.split() if w not in NATIONAL_EXTENT]
    while words and words[0] in _EDGE_WORDS:
        words.pop(0)
    while words and words[-1] in _EDGE_WORDS:
        words.pop()
    return " ".join(words) if any(w in DIRECTIONAL or w in REGIONAL for w in words) else None


def classify(region: str | None, scope: str | None, gz: Gazetteer) -> dict:
    """{classification, class, states, nca_regions, rule, us_gazetteer_in_string, masked_by, ambiguous} (+ `qualifier` in v2)."""
    if gz.version == "v2":
        return _classify_v2(region, scope, gz)
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


def _classify_v2(region: str | None, scope: str | None, gz: Gazetteer) -> dict:
    region = region or ""
    unnamed = region.strip().lower() in UNNAMED
    term = us_name(region)
    states, regions, masked = gz.names_in(region) if not unnamed else ([], [], [])
    out = {"us_gazetteer_in_string": term, "masked_by": masked,
           "ambiguous": gz.ambiguous.get(norm(region), {}).get("may_be"), "qualifier": None}
    labels = [f"state:{s}" for s in states] + [f"nca:{n}" for n in regions]
    if scope in ("subnational", "local") and labels:
        cls, rule = labels[0].split(":")[0], "whole_phrase:" + "|".join(states + regions)
    elif term:
        q = us_qualifier(region)
        cls, rule = ("us_subregion", f"us_name:{term} +qualifier") if q else ("us_national", f"us_name:{term}")
        out["qualifier"] = q
    elif scope == "global":
        cls, rule = "global", "scope_global"
    elif unnamed:
        cls, rule = "unknown", "region_unnamed"
    elif scope in ("national", "continental"):
        na = contains(norm(region), "North America")
        cls, rule = ("us_national", "us_gazetteer:North America") if na else ("other", f"{scope}_no_us_gazetteer")
        out["us_gazetteer_in_string"] = "North America" if na else None
    elif scope in ("subnational", "local"):
        cls, rule = "other", f"{scope}_no_state_or_nca_name" + (f" (masked by {', '.join(masked)})" if masked else "")
    else:
        cls, rule = "unknown", f"scope_{scope}"
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
    if geo["class"] == "us_subregion":
        return "us_subregion"
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
CSV_COLUMNS_V2 = ("region", "region_scope", "count", "region_count_all_scopes", "scopes_of_region", "classification", "class",
                  "qualifier", "rule", "classification_v1", "class_v1", "us_gazetteer_in_string", "masked_by", "ambiguous",
                  "core", "cited", "background", "statement_ids")


def region_rows_v2(statements: list[dict], gz: Gazetteer, gz_v1: Gazetteer) -> list[dict]:
    """`region_rows` under v2 (`gz`), with the qualifier and the v1 classification beside it (`region_strings_v2.csv`)."""
    rows = region_rows(statements, gz)
    for r in rows:
        g = classify(r["region"], r["region_scope"], gz)
        g1 = classify(r["region"], r["region_scope"], gz_v1)
        r.update(qualifier=g["qualifier"] or "", classification_v1=g1["classification"], class_v1=g1["class"])
    return rows


def recovered_d047a(statements: list[dict], gz: Gazetteer, gz_v1: Gazetteer) -> dict:
    """The D-047 drops (v1 `other`, a U.S. gazetteer string, subnational / local scope) and what v2 makes of them."""
    dropped, moved = [], Counter()
    for s in statements:
        pr = s["proposal"]
        g1 = classify(pr.get("region"), pr.get("region_scope"), gz_v1)
        g2 = classify(pr.get("region"), pr.get("region_scope"), gz)
        moved[(g1["class"], g2["class"])] += 1
        if g1["class"] == "other" and g1["us_gazetteer_in_string"] and pr.get("region_scope") in ("subnational", "local"):
            dropped.append((s["statement_id"], g2["class"]))
    rec = [sid for sid, c in dropped if c in ("us_national", "us_subregion", "state", "nca")]
    return {"dropped_under_v1": len(dropped), "recovered_under_v2": len(rec),
            "recovered_by_class": dict(sorted(Counter(c for _, c in dropped if c in ("us_national", "us_subregion", "state", "nca")).items())),
            "not_recovered": sorted(sid for sid, c in dropped if sid not in set(rec)),
            "transitions_v1_to_v2": {f"{a}->{b}": n for (a, b), n in sorted(moved.items()) if a != b}}
