"""Pilot P1 --- deterministic table-pattern extractor (D-039, D-041; GUIDANCE re-anchor ruling 2026-10-29).

Track D's machinery re-purposed (D-039): the governed metrics, their columns, the
State labels and the control cell come from `data/metadata/templates/slots_v1.yaml`
through `climrr.templates`; the statistics are Track D's rules DR-TD-003 (absolute
change), DR-TD-004 (percent change, a ratio of means) and DR-TD-005 (direction),
on the prototypes' arithmetic (Decimal from the raw strings, every derived value
rounded to 15 places half-to-even). No model is called; every table-side fact a
benchmark item may state is one of these records.

A **pattern** is one statistic for one (family, metric, season, horizon,
scenario) at one geography --- a State label, an NCA5 region
(`data/metadata/geography/nca_regions_v1.yaml`, pinned in the manifest) or the
P-CELL-1 control cell --- with its direction, its computed value or range, its
rank, a relative tercile where the guards allow one, its support and robustness,
and full provenance. Seasonal and regional contrasts are patterns of their own.

Rules added here (versioned; each record names the ones it used):

- **DR-PT-001** state aggregate: the unweighted mean over the rows sharing a
  State label (A-G1, A-G3, A-AGG1); cells empty on a column read are skipped and
  counted.
- **DR-PT-002** NCA-region aggregate: the unweighted mean over every row whose
  State label maps to the region --- each cell counts once, so a state with more
  cells weighs more; the region's range is min--max of its member states' values.
- **DR-PT-003** robustness: the share of member units (cells for a state, states
  for a region) whose own direction equals the aggregate's;
  `all_states_same_direction` at 1, `majority_same_direction` above 1/2, `mixed`
  otherwise. The enum names states (ruling 4); `robustness_unit` says which unit.
- **DR-PT-004** rank: descending signed value among the geographies of the same
  type; competition ranking (ties share a rank).
- **DR-PT-005** relative tercile among the U.S. State labels (ruling 5): sorted by
  signed value, the bottom ⌊n/3⌋ are `small`, the top ⌊n/3⌋ `large`, the rest
  `moderate`; **skipped** --- reason recorded --- when the population is under 15,
  fewer than three distinct values (degenerate), a tie straddles a cut, or any
  enumerated state is missing (placing the missing states at either end moves a
  cut). A disclosed relative descriptor, never an absolute threshold.
- **DR-PT-006** per-cell percent-change columns (FWI Pmid / Pend, all four
  seasons, verified): **no central value** --- a percentage is not averaged
  (M1-WP3b evidence check 3; owner decision 2026-10-29) --- so the pattern is the
  cells' sign counts, the majority direction and the min--max over cells; no rank,
  no tercile, no largest-change season.
- **DR-PT-007** seasonal contrast (per geography and horizon, the four seasons of
  DR-PT-006): per-season majority direction and share of cells increasing.
- **DR-PT-008** regional contrast: the NCA regions ordered by DR-PT-004 (value
  metrics) or listed with their DR-PT-006 majority direction (percent-change
  columns).

Column governance is unchanged. The FWI summer value / difference columns are
`inferred_candidate` (IC-006..IC-010): their patterns are computed --- the work
package carries the authorization --- and every one is `acceptance_blocked` until
owner confirmation. `State` is `inferred_candidate` (IC-012): every state and
region pattern is provisional (D-034). The FWI percent-change columns state no
scenario in the dictionary: `scenario: unstated_in_dictionary`.
"""

from __future__ import annotations

import csv
import hashlib
import json
from decimal import Decimal, localcontext
from pathlib import Path

import yaml

from climrr import templates as td
from climrr.paths import REPO_ROOT
from climrr.phenomenon import (
    PRECISION,
    PROVISIONAL_AGGREGATION_LABEL,
    direction_of,
    dstr,
    mean_from_total,
    quantise_derived,
    to_decimal,
)

VERSION = "table_patterns v1"
MODULE_PATH = Path(__file__).resolve()
NCA_MAP_PATH = REPO_ROOT / "data" / "metadata" / "geography" / "nca_regions_v1.yaml"
OUT_DIR = REPO_ROOT / "artifacts" / "benchmark"
PATTERNS_PATH = OUT_DIR / "table_patterns_v1.jsonl"
SUMMARY_PATH = OUT_DIR / "table_patterns_v1_summary.json"
EXAMPLES_PATH = OUT_DIR / "table_patterns_v1_examples.jsonl"
DOC_PATH = REPO_ROOT / "docs" / "TABLE_PATTERNS_V1.md"

TERCILE_MIN_POPULATION = 15
TERCILE_CLASSES = ("small", "moderate", "large")
HORIZONS = {"mid": {"period": "mid_century", "window": "2045-2054"},
            "end": {"period": "end_century", "window": "2085-2094"}}
GEOGRAPHY_ORDER = ("nca_region", "state", "cell_control")
UNSTATED = "unstated_in_dictionary"
IC_BLOCKING = {"fire_weather_index": ["IC-006", "IC-007", "IC-008", "IC-009", "IC-010"]}

#: The verified FWI percent-change columns (dictionary lines quoted verbatim; a
#: test checks each against dictionary_extracted.txt and the coverage report).
PERCENT_COLUMNS = {
    "autumn": {"mid": (180, "wildfire_autumn_Pmid", 652), "end": (181, "wildfire_autumn_Pend", 653)},
    "spring": {"mid": (187, "wildfire_spring_Pmid", 659), "end": (188, "wildfire_spring_Pend", 660)},
    "summer": {"mid": (194, "wildfire_summer_Pmid", 666), "end": (195, "wildfire_summer_Pend", 667)},
    "winter": {"mid": (201, "wildfire_winter_Pmid", 673), "end": (202, "wildfire_winter_Pend", 674)},
}
PERCENT_QUOTE = {"mid": "Percent Change between Mid-Century and Historical",
                 "end": "Percent Change between End-Century and Historical"}

NO_CENTRAL_VALUE = ("no_admissible_central_value: per-cell percentages are not averaged "
                    "(M1-WP3b evidence check 3; owner decision 2026-10-29)")


class PatternError(RuntimeError):
    """An input does not support the extraction. Never patched."""


# --- inputs ----------------------------------------------------------------------


def code_version() -> str:
    return f"{VERSION} (src/climrr/table_patterns.py sha256 {td.file_sha256(MODULE_PATH)[:16]})"


def load_nca_map(path: Path | str = NCA_MAP_PATH) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    region_ids = [r["region_id"] for r in data["regions"]]
    bad = {s: r for s, r in data["state_to_region_map"].items() if r not in region_ids}
    if bad:
        raise PatternError(f"states mapped to unknown regions: {bad}")
    return data


def region_members(nca: dict, table_states: list[str]) -> dict[str, dict]:
    """region_id -> {name, members (all), covered (in the table), uncovered}."""
    out = {}
    for r in nca["regions"]:
        members = sorted(s for s, rid in nca["state_to_region_map"].items() if rid == r["region_id"])
        out[r["region_id"]] = {"name": r["name"], "members": members,
                               "covered": [s for s in members if s in table_states],
                               "uncovered": [s for s in members if s not in table_states]}
    return out


def metric_specs(slots: dict, coverage: dict[int, dict]) -> list[dict]:
    """Every metric a pattern is computed for, in enumeration order: the heat-index
    thresholds and the FWI summer value (from slots_v1), then the FWI percent-change
    columns by season. Columns that are not verified are carried with their status."""
    specs = []
    for entry in td.governed_metrics(slots):
        fam, met = entry["family"], entry["metric"]
        cols = {p: _col(c) for p, c in met["period_columns"].items()}
        change = {h: _col(met["change_columns"][f"historical->{v['period']}"])
                  if f"historical->{v['period']}" in (met.get("change_columns") or {}) else None
                  for h, v in HORIZONS.items()}
        specs.append({"family": fam["id"], "metric_id": met["metric_id"], "wording": met["wording"],
                      "kind": "value", "season": met["season"], "unit": met["unit"], "scenario": "RCP8.5",
                      "baseline": cols["historical"],
                      "future": {h: cols[v["period"]] for h, v in HORIZONS.items()},
                      "change": change})
    for season, by_h in PERCENT_COLUMNS.items():
        cols = {}
        for h, (index, column, line) in by_h.items():
            status = coverage[index]["status"]
            if coverage[index]["column"] != column:
                raise PatternError(f"column {index} is {coverage[index]['column']!r}, not {column!r}")
            cols[h] = {"index": index, "column": column, "status": status,
                       "source": {"kind": "dictionary_line", "line": line,
                                  "quote": f"Wildfire_{season}_P{h} {PERCENT_QUOTE[h]}"}}
        specs.append({"family": "fire_weather_index", "metric_id": f"fwi_{season}_percent_change_column",
                      "wording": f"{season} Fire Weather Index (FWI) percent change per cell", "kind": "percent_column",
                      "season": season, "unit": "percent", "scenario": UNSTATED, "percent": cols})
    # The work package's family order: heat index, then fire weather.
    specs.sort(key=lambda s: (s["family"] != "heat_index",))
    for s in specs:
        s["columns"] = _spec_columns(s)
        s["authorization"] = ("verified" if all(c["status"] in td.COMPUTABLE_COLUMN_STATUSES for c in s["columns"])
                              else "inferred_candidate")
    return specs


def _col(c: dict) -> dict:
    return {"index": c["index"], "column": c["column"], "status": c["status"], "source": c["source"]}


def _spec_columns(spec: dict) -> list[dict]:
    if spec["kind"] == "percent_column":
        return list(spec["percent"].values())
    cols = [spec["baseline"], *spec["future"].values(), *[c for c in spec["change"].values() if c]]
    return sorted(cols, key=lambda c: c["index"])


def horizon_columns(spec: dict, horizon: str) -> list[dict]:
    if spec["kind"] == "percent_column":
        return [spec["percent"][horizon]]
    cols = [spec["baseline"], spec["future"][horizon]]
    if spec["change"][horizon]:
        cols.append(spec["change"][horizon])
    return cols


# --- the table scan --------------------------------------------------------------


def _new_acc() -> dict:
    return {"rows": 0, "n": 0, "n_empty": 0, "sum_from": Decimal(0), "sum_to": Decimal(0), "sum_change": Decimal(0),
            "dirs": {"increase": 0, "decrease": 0, "no_change": 0}, "min": None, "max": None}


def _add(acc: dict, v_from, v_to, change: Decimal, extreme: Decimal) -> None:
    acc["n"] += 1
    if v_from is not None:
        acc["sum_from"] += v_from
        acc["sum_to"] += v_to
    acc["sum_change"] += change
    acc["dirs"][direction_of(change)] += 1
    acc["min"] = extreme if acc["min"] is None or extreme < acc["min"] else acc["min"]
    acc["max"] = extreme if acc["max"] is None or extreme > acc["max"] else acc["max"]


def scan(path: Path | str, specs: list[dict], states: list[str], control_cell: str) -> dict:
    """One pass: per (geography key, metric, horizon) the sums, sign counts and
    cell extremes the patterns need. Text in; only value columns become Decimal."""
    expected = {td.CROSSMODEL_INDEX: "Crossmodel", td.STATE_INDEX: "State"}
    for s in specs:
        for c in s["columns"]:
            expected[c["index"]] = c["column"]
    accs: dict = {}
    cells: dict = {}
    n_rows = 0
    state_set = set(states)
    with Path(path).open("r", encoding=td.ENCODING, newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        for index, name in expected.items():
            if index >= len(header) or header[index] != name:
                raise PatternError(f"table column {index} is not {name!r}")
        for row in reader:
            n_rows += 1
            keys = []
            if row[td.STATE_INDEX] in state_set:
                keys.append(("state", row[td.STATE_INDEX]))
            if row[td.CROSSMODEL_INDEX] == control_cell:
                keys.append(("cell_control", control_cell))
            if not keys:
                continue
            for key in keys:
                c = cells.setdefault(key, {"rows": 0, "sha": hashlib.sha256()})
                c["rows"] += 1
                c["sha"].update(row[td.CROSSMODEL_INDEX].encode("utf-8") + b"\n")
            for s in specs:
                for h in HORIZONS:
                    measured = _cell_change(s, h, row)
                    for key in keys:
                        acc = accs.setdefault((key, s["metric_id"], h), _new_acc())
                        acc["rows"] += 1
                        if measured is None:
                            acc["n_empty"] += 1
                        else:
                            _add(acc, *measured)
    for c in cells.values():
        c["cells_sha256"] = c.pop("sha").hexdigest()
    return {"n_rows": n_rows, "accs": accs, "cells": cells}


def _cell_change(spec: dict, horizon: str, row: list[str]):
    """(from, to, change, extreme) for one cell, or None if a column read is empty.
    `extreme` is what the cell range is taken over: the change (value metrics) or
    the cell's percent change (percent-change columns)."""
    if spec["kind"] == "percent_column":
        col = spec["percent"][horizon]
        raw = row[col["index"]]
        if raw == "":
            return None
        pct = to_decimal(raw, index=col["index"])
        return None, None, pct, pct
    base, fut, chg = spec["baseline"], spec["future"][horizon], spec["change"][horizon]
    raws = [row[base["index"]], row[fut["index"]]] + ([row[chg["index"]]] if chg else [])
    if "" in raws:
        return None
    v_from = to_decimal(raws[0], index=base["index"])
    v_to = to_decimal(raws[1], index=fut["index"])
    change = quantise_derived(to_decimal(raws[2], index=chg["index"]) if chg else v_to - v_from)
    return v_from, v_to, change, change


# --- statistics --------------------------------------------------------------------


def _merge(accs: list[dict]) -> dict:
    out = _new_acc()
    for a in accs:
        for k in ("rows", "n", "n_empty"):
            out[k] += a[k]
        for k in ("sum_from", "sum_to", "sum_change"):
            out[k] += a[k]
        for d in out["dirs"]:
            out["dirs"][d] += a["dirs"][d]
        for k, pick in (("min", min), ("max", max)):
            vals = [x for x in (out[k], a[k]) if x is not None]
            out[k] = pick(vals) if vals else None
    return out


def majority_direction(dirs: dict[str, int]) -> str:
    """DR-PT-006: the sign held by more than half the cells, else `mixed`."""
    total = sum(dirs.values())
    for d, n in dirs.items():
        if total and 2 * n > total:
            return d
    return "mixed"


def robustness(same: int, total: int) -> str | None:
    """DR-PT-003."""
    if total == 0:
        return None
    if same == total:
        return "all_states_same_direction"
    if 2 * same > total:
        return "majority_same_direction"
    return "mixed"


def aggregate_values(spec: dict, acc: dict) -> dict:
    """DR-TD-003/004/005 on one accumulator (state, region or cell)."""
    out = {"n_cells_used": acc["n"], "n_cells_empty": acc["n_empty"], "dirs": dict(acc["dirs"]),
           "cell_min": dstr(acc["min"]) if acc["min"] is not None else None,
           "cell_max": dstr(acc["max"]) if acc["max"] is not None else None}
    if acc["n"] == 0:
        return {**out, "status": "not_computable", "reason": "no_cell_with_a_value"}
    if spec["kind"] == "percent_column":
        return {**out, "status": "computed", "direction": majority_direction(acc["dirs"]),
                "absolute_change": None, "percent_change": None, "percent_reason": NO_CENTRAL_VALUE}
    mean_from = mean_from_total(acc["sum_from"], acc["n"])
    change = mean_from_total(acc["sum_change"], acc["n"])
    out.update({"status": "computed", "direction": direction_of(change), "absolute_change": dstr(change),
                "mean_from": dstr(mean_from), "mean_to": dstr(mean_from_total(acc["sum_to"], acc["n"]))})
    if mean_from == 0:
        out.update({"percent_change": None, "percent_reason": "zero_baseline"})
    else:
        with localcontext() as ctx:
            ctx.prec = PRECISION
            out.update({"percent_change": dstr(quantise_derived(Decimal(100) * change / mean_from)),
                        "percent_reason": None})
    return out


def competition_rank(values: dict[str, Decimal]) -> dict[str, dict]:
    """DR-PT-004: descending signed value; tied geographies share a rank."""
    ordered = sorted(values.items(), key=lambda kv: (-kv[1], kv[0]))
    out, n = {}, len(ordered)
    for label, v in ordered:
        better = sum(1 for x in values.values() if x > v)
        ties = sum(1 for x in values.values() if x == v)
        out[label] = {"rank": better + 1, "of": n, "tied_with": ties - 1,
                      "order": "descending signed value (DR-PT-004)"}
    return out


def terciles(values: dict[str, Decimal], n_missing: int) -> tuple[dict[str, str] | None, str | None]:
    """DR-PT-005. Returns ({label: class}, None) or (None, skip reason)."""
    n = len(values)
    if n < TERCILE_MIN_POPULATION:
        return None, f"population_lt_{TERCILE_MIN_POPULATION} (n={n})"
    if len(set(values.values())) < 3:
        return None, f"degenerate_distribution ({len(set(values.values()))} distinct values among {n})"
    ordered = sorted(values.items(), key=lambda kv: (kv[1], kv[0]))
    k = n // 3
    vals = [v for _, v in ordered]
    if vals[k - 1] == vals[k] or vals[n - k - 1] == vals[n - k]:
        return None, f"tie_at_cut (n={n}, k={k})"
    if n_missing:
        return None, f"missing_states_change_cut_points ({n_missing} enumerated state(s) not computable)"
    classes = {}
    for i, (label, _) in enumerate(ordered):
        classes[label] = TERCILE_CLASSES[0] if i < k else TERCILE_CLASSES[2] if i >= n - k else TERCILE_CLASSES[1]
    return classes, None


def tercile_definition(cls: str, n: int, spec: dict, horizon: str, statistic: str) -> str:
    where = {"small": "lower", "moderate": "middle", "large": "upper"}[cls]
    return (f"{cls} = {where} tercile, by signed value, among the {n} U.S. State labels in the table with a "
            f"computed value for family={spec['family']}, metric={spec['metric_id']}, season={spec['season']}, "
            f"horizon={horizon} ({HORIZONS[horizon]['window']}), scenario={spec['scenario']}, "
            f"statistic={statistic} (DR-PT-005); a relative descriptor among states, not an absolute threshold")


# --- pattern records ---------------------------------------------------------------


class _Builder:
    def __init__(self, specs, scanned, states, regions, control_cell, table_sha, nca_sha, code_ver):
        self.specs, self.scanned, self.states, self.regions = specs, scanned, states, regions
        self.control_cell, self.table_sha, self.nca_sha, self.code_ver = control_cell, table_sha, nca_sha, code_ver
        self.records: list[dict] = []
        self.tercile_skips: list[dict] = []

    def _id(self) -> str:
        return f"TP1-{len(self.records) + 1:05d}"

    def _base(self, spec, horizon, statistic, gtype, geography) -> dict:
        blocked = IC_BLOCKING.get(spec["family"]) if spec["authorization"] != "verified" else None
        cols = horizon_columns(spec, horizon) if horizon else spec["columns"]
        provisional = []
        if gtype in ("state", "nca_region"):
            provisional.append("location_inferred_candidate: State label IC-012 (A-G1, A-G3; D-034)")
        if gtype != "cell_control" and spec["kind"] == "value":
            provisional.append(f"unweighted_mean: {PROVISIONAL_AGGREGATION_LABEL}")
        return {"pattern_id": self._id(), "pattern_kind": "single", "family": spec["family"],
                "metric": spec["metric_id"], "metric_wording": spec["wording"], "season": spec["season"],
                "horizon": horizon, "horizon_window": HORIZONS[horizon]["window"] if horizon else None,
                "scenario": spec["scenario"], "statistic": statistic, "geography_type": gtype, "geography": geography,
                "authorization": spec["authorization"], "acceptance_blocked": bool(blocked),
                "acceptance_blocked_by": blocked or [], "provisional": bool(provisional),
                "provisional_reasons": provisional,
                "cautions": ["C-fire_weather: a fire-danger index, never fire occurrence"] if spec["family"] == "fire_weather_index" else [],
                "provenance": {"columns": [{"index": c["index"], "column": c["column"]} for c in cols],
                               "column_statuses": {c["column"]: c["status"] for c in cols},
                               "column_sources": {c["column"]: c["source"] for c in cols},
                               "row_rule": None, "derivation_rule_id": None, "code_version": self.code_ver,
                               "table_data_sha256": self.table_sha}}

    def _stat_rule(self, spec, statistic) -> str:
        if spec["kind"] == "percent_column":
            return "DR-PT-006"
        return {"direction": "DR-TD-005", "absolute_change": "DR-TD-003", "percent_change": "DR-TD-004"}[statistic]

    def _value(self, agg, statistic):
        if statistic == "direction":
            return agg.get("absolute_change"), None
        if statistic == "absolute_change":
            return agg.get("absolute_change"), None
        return agg.get("percent_change"), agg.get("percent_reason")

    def build(self) -> list[dict]:
        accs = self.scanned["accs"]
        for spec in self.specs:
            statistics = ("direction", "absolute_change", "percent_change") if spec["kind"] == "value" \
                else ("direction", "percent_change")
            for h in HORIZONS:
                state_aggs = {s: aggregate_values(spec, accs[(("state", s), spec["metric_id"], h)])
                              for s in self.states if (("state", s), spec["metric_id"], h) in accs}
                region_aggs = {}
                for rid, r in self.regions.items():
                    if r["covered"]:
                        merged = _merge([accs[(("state", s), spec["metric_id"], h)] for s in r["covered"]])
                        region_aggs[rid] = aggregate_values(spec, merged)
                cell_key = (("cell_control", self.control_cell), spec["metric_id"], h)
                cell_agg = aggregate_values(spec, accs[cell_key]) if cell_key in accs else None
                for stat in statistics:
                    self._emit_group(spec, h, stat, state_aggs, region_aggs, cell_agg)
        return self.records

    def _emit_group(self, spec, h, stat, state_aggs, region_aggs, cell_agg):
        rule = self._stat_rule(spec, stat)
        ranked = stat != "direction" and spec["kind"] == "value"

        def numeric(aggs):
            return {k: Decimal(self._value(a, stat)[0]) for k, a in aggs.items()
                    if a["status"] == "computed" and self._value(a, stat)[0] is not None}

        state_vals = numeric(state_aggs) if ranked else {}
        region_vals = numeric(region_aggs) if ranked else {}
        state_ranks = competition_rank(state_vals) if ranked else {}
        region_ranks = competition_rank(region_vals) if ranked else {}
        if ranked:
            classes, skip = terciles(state_vals, len(self.states) - len(state_vals))
        else:
            classes, skip = None, ("not_applicable: categorical statistic" if stat == "direction" else NO_CENTRAL_VALUE)
        if ranked and skip:
            self.tercile_skips.append({"family": spec["family"], "metric": spec["metric_id"], "horizon": h,
                                       "statistic": stat, "reason": skip})
        # NCA regions
        for rid in sorted(region_aggs):
            r, agg = self.regions[rid], region_aggs[rid]
            rec = self._base(spec, h, stat, "nca_region", rid)
            members = [s for s in r["covered"] if state_aggs.get(s, {}).get("status") == "computed"]
            member_dirs = {s: state_aggs[s]["direction"] for s in members}
            member_vals = {s: self._value(state_aggs[s], stat)[0] for s in members}
            self._fill(rec, spec, agg, stat, rank=region_ranks.get(rid),
                       range_={"over": "member_states", **_minmax(member_vals)} if ranked else
                       {"over": "cells", "min": agg["cell_min"], "max": agg["cell_max"]},
                       support=len(members), unit="state",
                       same=sum(1 for d in member_dirs.values() if d == agg.get("direction")),
                       tercile=None, tercile_skip=f"population_lt_{TERCILE_MIN_POPULATION} (n={len(region_aggs)} regions)"
                       if ranked else skip)
            rec["region_name"] = r["name"]
            rec["region_member_states_covered"] = r["covered"]
            rec["region_member_states_uncovered"] = r["uncovered"]
            rec["member_directions"] = member_dirs
            rec["provenance"]["row_rule"] = f"State in nca_regions_v1[{rid}] ∩ table State labels: {r['covered']}"
            rec["provenance"]["derivation_rule_id"] = f"{rule} @ DR-PT-002"
            rec["provenance"]["region_scheme"] = {"region_scheme_id": "NCA5", "map": "data/metadata/geography/nca_regions_v1.yaml",
                                                  "map_sha256": self.nca_sha}
            self.records.append(rec)
        # states
        for s in sorted(state_aggs):
            agg = state_aggs[s]
            rec = self._base(spec, h, stat, "state", s)
            self._fill(rec, spec, agg, stat, rank=state_ranks.get(s),
                       range_={"over": "cells", "min": agg["cell_min"], "max": agg["cell_max"]},
                       support=agg["n_cells_used"], unit="cell", same=agg["dirs"].get(agg.get("direction"), 0),
                       tercile=(classes or {}).get(s) if ranked else None,
                       tercile_skip=skip if not (classes and s in classes) else None,
                       tercile_n=len(state_vals))
            rec["provenance"]["row_rule"] = f"State == {s!r}"
            rec["provenance"]["derivation_rule_id"] = f"{rule} @ DR-PT-001"
            rec["provenance"]["member_rows"] = self.scanned["cells"][("state", s)]["rows"]
            rec["provenance"]["member_cells_sha256"] = self.scanned["cells"][("state", s)]["cells_sha256"]
            self.records.append(rec)
        # control cell
        if cell_agg is not None:
            rec = self._base(spec, h, stat, "cell_control", self.control_cell)
            self._fill(rec, spec, cell_agg, stat, rank=None,
                       range_={"over": "cells", "min": cell_agg["cell_min"], "max": cell_agg["cell_max"]},
                       support=cell_agg["n_cells_used"], unit="cell",
                       same=cell_agg["dirs"].get(cell_agg.get("direction"), 0),
                       tercile=None, tercile_skip="not_applicable: control cell (P-CELL-1)")
            rec["provenance"]["row_rule"] = f"Crossmodel == {self.control_cell!r}"
            rec["provenance"]["derivation_rule_id"] = f"{rule} @ cell"
            self.records.append(rec)

    def _fill(self, rec, spec, agg, stat, *, rank, range_, support, unit, same, tercile, tercile_skip, tercile_n=0):
        value, reason = self._value(agg, stat) if agg["status"] == "computed" else (None, agg.get("reason"))
        if spec["kind"] == "percent_column" and stat == "percent_change":
            value, reason = None, NO_CENTRAL_VALUE
        rec["status"] = "computed" if agg["status"] == "computed" and (stat == "direction" or value is not None
                                                                        or spec["kind"] == "percent_column") \
            else "not_computable"
        rec["direction"] = agg.get("direction")
        rec["computed_value_or_range"] = {
            "value": value, "value_reason": reason,
            "unit": None if stat == "direction" and spec["kind"] == "percent_column" else
            ("percent" if stat == "percent_change" else spec["unit"]),
            "value_is": ("mean change (DR-TD-003), whose sign the direction is" if stat == "direction" and spec["kind"] == "value"
                         else "majority sign of the cells (DR-PT-006)" if stat == "direction" else stat),
            "range": range_, "n_cells_used": agg["n_cells_used"], "n_cells_empty": agg["n_cells_empty"],
            "cell_direction_counts": agg["dirs"],
        }
        if spec["kind"] == "value" and agg["status"] == "computed":
            rec["computed_value_or_range"]["mean_from"] = agg["mean_from"]
            rec["computed_value_or_range"]["mean_to"] = agg["mean_to"]
        rec["rank"] = rank
        rec["relative_magnitude"] = ({"class": tercile, "definition": tercile_definition(tercile, tercile_n, spec, rec["horizon"], stat)}
                                     if tercile else None)
        rec["relative_magnitude_skipped_reason"] = None if tercile else tercile_skip
        rec["pattern_support_n"] = support
        rec["pattern_robustness"] = robustness(same, support) if agg.get("direction") in ("increase", "decrease", "no_change") else "mixed"
        rec["robustness_unit"] = unit
        rec["robustness_share"] = f"{same}/{support}"

    # -- contrasts
    def seasonal_contrasts(self) -> None:
        """DR-PT-007, on the four-season percent-change columns."""
        pct = [s for s in self.specs if s["kind"] == "percent_column"]
        accs = self.scanned["accs"]
        geos = [("nca_region", rid) for rid in sorted(self.regions) if self.regions[rid]["covered"]] + \
               [("state", s) for s in self.states] + [("cell_control", self.control_cell)]
        for h in HORIZONS:
            for gtype, geo in geos:
                per = {}
                for spec in pct:
                    if gtype == "nca_region":
                        acc = _merge([accs[(("state", s), spec["metric_id"], h)] for s in self.regions[geo]["covered"]])
                    else:
                        acc = accs.get(((gtype, geo), spec["metric_id"], h))
                        if acc is None:
                            continue
                    agg = aggregate_values(spec, acc)
                    total = sum(agg["dirs"].values())
                    per[spec["season"]] = {"majority_direction": agg.get("direction"), "cell_direction_counts": agg["dirs"],
                                           "share_cells_increase": f"{agg['dirs']['increase']}/{total}",
                                           "cell_min": agg["cell_min"], "cell_max": agg["cell_max"]}
                if not per:
                    continue
                dirs = {v["majority_direction"] for v in per.values()}
                rec = {"pattern_id": self._id(), "pattern_kind": "seasonal_contrast", "family": "fire_weather_index",
                       "metric": "fwi_percent_change_column (four seasons)", "season": "autumn+spring+summer+winter",
                       "horizon": h, "horizon_window": HORIZONS[h]["window"], "scenario": UNSTATED,
                       "statistic": "seasonal_contrast", "geography_type": gtype, "geography": geo,
                       "direction": dirs.pop() if len(dirs) == 1 else "mixed",
                       "computed_value_or_range": {"value": None, "per_season": per},
                       "largest_change_season": None, "largest_change_season_skipped_reason": NO_CENTRAL_VALUE,
                       "seasons_majority_increase": sorted(k for k, v in per.items() if v["majority_direction"] == "increase"),
                       "rank": None, "relative_magnitude": None, "relative_magnitude_skipped_reason": NO_CENTRAL_VALUE,
                       "pattern_support_n": len(per), "pattern_robustness": None, "robustness_unit": "season",
                       "authorization": "verified", "acceptance_blocked": False, "acceptance_blocked_by": [],
                       "provisional": gtype != "cell_control",
                       "provisional_reasons": ["location_inferred_candidate: State label IC-012 (A-G1, A-G3; D-034)"] if gtype != "cell_control" else [],
                       "cautions": ["C-fire_weather: a fire-danger index, never fire occurrence"],
                       "provenance": {"columns": [{"index": s["percent"][h]["index"], "column": s["percent"][h]["column"]} for s in pct],
                                      "column_statuses": {s["percent"][h]["column"]: s["percent"][h]["status"] for s in pct},
                                      "row_rule": (f"State == {geo!r}" if gtype == "state" else f"Crossmodel == {geo!r}"
                                                   if gtype == "cell_control" else f"State in nca_regions_v1[{geo}]: {self.regions[geo]['covered']}"),
                                      "derivation_rule_id": "DR-PT-007 @ DR-PT-006", "code_version": self.code_ver,
                                      "table_data_sha256": self.table_sha}}
                if gtype == "nca_region":
                    rec["provenance"]["region_scheme"] = {"region_scheme_id": "NCA5", "map_sha256": self.nca_sha}
                self.records.append(rec)

    def regional_contrasts(self) -> None:
        """DR-PT-008, from the region records already built."""
        singles = [r for r in self.records if r["pattern_kind"] == "single" and r["geography_type"] == "nca_region"]
        groups: dict = {}
        for r in singles:
            if r["statistic"] == "direction" and not r["metric"].endswith("_percent_change_column"):
                continue
            if r["metric"].endswith("_percent_change_column") and r["statistic"] != "direction":
                continue
            groups.setdefault((r["family"], r["metric"], r["horizon"], r["statistic"]), []).append(r)
        for (fam, metric, h, stat), recs in groups.items():
            first = recs[0]
            if first["metric"].endswith("_percent_change_column"):
                order = [{"region": r["geography"], "name": r["region_name"], "majority_direction": r["direction"],
                          "cell_direction_counts": r["computed_value_or_range"]["cell_direction_counts"]} for r in recs]
                ordering = "region id; no central value to order by (DR-PT-006)"
            else:
                ranked = sorted([r for r in recs if r["rank"]], key=lambda r: (r["rank"]["rank"], r["geography"]))
                order = [{"region": r["geography"], "name": r["region_name"], "rank": r["rank"]["rank"],
                          "value": r["computed_value_or_range"]["value"], "direction": r["direction"]} for r in ranked]
                order += [{"region": r["geography"], "name": r["region_name"], "rank": None, "value": None,
                           "reason": r["computed_value_or_range"]["value_reason"]} for r in recs if not r["rank"]]
                ordering = "descending signed value (DR-PT-004)"
            dirs = {r["direction"] for r in recs}
            self.records.append({
                "pattern_id": self._id(), "pattern_kind": "regional_contrast", "family": fam, "metric": metric,
                "metric_wording": first["metric_wording"], "season": first["season"], "horizon": h,
                "horizon_window": first["horizon_window"], "scenario": first["scenario"], "statistic": stat,
                "geography_type": "nca_region", "geography": "all_covered_nca5_regions",
                "direction": dirs.pop() if len(dirs) == 1 else "mixed",
                "computed_value_or_range": {"value": None, "regions_ordered": order, "ordering": ordering},
                "rank": None, "relative_magnitude": None,
                "relative_magnitude_skipped_reason": f"population_lt_{TERCILE_MIN_POPULATION} (n={len(recs)} regions)",
                "pattern_support_n": len(recs),
                "pattern_robustness": robustness(max(sum(1 for r in recs if r["direction"] == d) for d in
                                                     {r["direction"] for r in recs}), len(recs)),
                "robustness_unit": "nca_region",
                "authorization": first["authorization"], "acceptance_blocked": first["acceptance_blocked"],
                "acceptance_blocked_by": first["acceptance_blocked_by"], "provisional": True,
                "provisional_reasons": first["provisional_reasons"], "cautions": first["cautions"],
                "provenance": {**first["provenance"], "row_rule": "every NCA5 region with ≥1 State label in the table",
                               "derivation_rule_id": "DR-PT-008 over " + first["provenance"]["derivation_rule_id"],
                               "region_pattern_ids": [r["pattern_id"] for r in recs]},
            })


def _minmax(values: dict[str, str | None]) -> dict:
    vals = {k: Decimal(v) for k, v in values.items() if v is not None}
    if not vals:
        return {"min": None, "max": None, "min_at": [], "max_at": []}
    lo, hi = min(vals.values()), max(vals.values())
    return {"min": dstr(lo), "max": dstr(hi), "min_at": sorted(k for k, v in vals.items() if v == lo),
            "max_at": sorted(k for k, v in vals.items() if v == hi)}


def build_patterns(slots: dict, coverage: dict, nca: dict, scanned: dict, table_sha: str, nca_sha: str,
                   code_ver: str | None = None) -> tuple[list[dict], list[dict]]:
    specs = metric_specs(slots, coverage)
    states = [v["label"] for v in td.location_values(slots, "state")]
    regions = region_members(nca, states)
    control = slots["location"]["cell"]["values"][0]["label"]
    b = _Builder(specs, scanned, states, regions, control, table_sha, nca_sha, code_ver or code_version())
    b.build()
    b.seasonal_contrasts()
    b.regional_contrasts()
    return b.records, b.tercile_skips


# --- summary, examples, doc ----------------------------------------------------------


def summarise(records: list[dict], tercile_skips: list[dict], regions: dict, table_states: list[str], nca: dict) -> dict:
    def count(fn) -> dict:
        out: dict = {}
        for r in records:
            k = fn(r)
            out[k] = out.get(k, 0) + 1
        return dict(sorted(out.items()))

    singles = [r for r in records if r["pattern_kind"] == "single"]
    skip_reasons: dict = {}
    for s in tercile_skips:
        key = s["reason"].split(" ")[0]
        skip_reasons[key] = skip_reasons.get(key, 0) + 1
    mapped = set(nca["state_to_region_map"])
    return {
        "schema_version": "table-patterns-v1",
        "n_patterns": len(records),
        "by_kind": count(lambda r: r["pattern_kind"]),
        "by_family": count(lambda r: r["family"]),
        "by_geography_type": count(lambda r: r["geography_type"]),
        "by_statistic": count(lambda r: r["statistic"]),
        "by_family_geography_statistic": count(lambda r: f"{r['family']}|{r['geography_type']}|{r['statistic']}"),
        "by_status": count(lambda r: r.get("status", "computed")),
        "by_authorization": count(lambda r: r["authorization"]),
        "n_acceptance_blocked": sum(r["acceptance_blocked"] for r in records),
        "n_with_relative_tercile": sum(1 for r in records if r["relative_magnitude"]),
        "tercile_groups_skipped": len(tercile_skips),
        "tercile_groups_skipped_by_reason": dict(sorted(skip_reasons.items())),
        "tercile_skips": tercile_skips,
        "n_single_state_patterns_without_tercile": sum(1 for r in singles if r["geography_type"] == "state" and not r["relative_magnitude"]),
        "table_states": table_states,
        "nca_states_not_in_table": sorted(mapped - set(table_states)),
        "table_states_not_in_nca_map": sorted(set(table_states) - mapped),
        "region_coverage": {rid: {"name": r["name"], "covered": r["covered"], "uncovered": r["uncovered"]}
                            for rid, r in regions.items()},
        "table_data_sha256": records[0]["provenance"]["table_data_sha256"] if records else None,
    }


def example_records(records: list[dict]) -> list[dict]:
    """The doc's ten examples: the first ten pattern ids."""
    return records[:10]


def write_jsonl(records: list[dict], path: Path | str) -> None:
    td.write_jsonl(records, path)


def read_jsonl(path: Path | str) -> list[dict]:
    return td.read_jsonl(path)


def _example_line(r: dict) -> list[str]:
    v = r["computed_value_or_range"]
    rng = v.get("range") or {}
    lines = [f"- **`{r['pattern_id']}`** --- {r['pattern_kind']}, `{r['family']}` / `{r['metric']}`, season {r['season']}, "
             f"horizon {r['horizon']} ({r['horizon_window']}), scenario {r['scenario']}, statistic `{r['statistic']}`, "
             f"{r['geography_type']} `{r['geography']}`" + (f" ({r['region_name']})" if r.get("region_name") else "")]
    lines.append(f"  - direction `{r['direction']}`; value `{v.get('value')}` {v.get('unit') or ''}; "
                 f"range over {rng.get('over')}: `{rng.get('min')}` .. `{rng.get('max')}`")
    rank = r["rank"]
    lines.append(f"  - rank: " + (f"{rank['rank']} of {rank['of']}" if rank else "---") + "; relative magnitude: "
                 + (f"`{r['relative_magnitude']['class']}` ({r['relative_magnitude']['definition']})" if r["relative_magnitude"]
                    else f"--- ({r['relative_magnitude_skipped_reason']})"))
    lines.append(f"  - support {r['pattern_support_n']} {r['robustness_unit']}(s), robustness `{r['pattern_robustness']}` "
                 f"({r.get('robustness_share', '')}); authorization `{r['authorization']}`"
                 + ("; **acceptance blocked** " + ", ".join(r["acceptance_blocked_by"]) if r["acceptance_blocked"] else ""))
    p = r["provenance"]
    lines.append(f"  - provenance: columns " + ", ".join(f"{c['index']} `{c['column']}` ({p['column_statuses'][c['column']]})" for c in p["columns"])
                 + f"; rows `{p['row_rule']}`; rule `{p['derivation_rule_id']}`")
    return lines


def render_doc(summary: dict, examples: list[dict], hashes: dict, nca: dict) -> str:
    L: list[str] = []
    add = L.append
    add("# Table patterns v1 --- deterministic, state / NCA-region level")
    add("")
    add("**Generated by `scripts/extract_table_patterns.py` --- never hand-edited; regenerate.**")
    add("")
    add("Pilot P1 (D-041; GUIDANCE re-anchor ruling 2026-10-29). **No model call. No item generated. No QA accepted.** "
        "No column status, concept-map entry or compatibility rule changed. A pattern is a table-side reference "
        "component (ruling, condition B): what an item's reference answer may state about the table --- never "
        "question content (D-035).")
    add("")
    add("## Inputs and outputs")
    add("")
    add("| File | SHA-256 |")
    add("| --- | --- |")
    for name, sha in hashes.items():
        add(f"| `{name}` | `{sha}` |")
    add("")
    add("## Method")
    add("")
    add("- **Families and metrics.** `heat_index`: days with daily max heat index above 95 / 105 / 115 / 125 F "
        "(summer; verified; DayMax is `inferred_candidate` and is not used). `fire_weather_index`: the summer "
        "seasonal value with its difference columns (`inferred_candidate`, IC-006..IC-010: computed, every pattern "
        "`acceptance_blocked`), and the **verified** per-cell percent-change columns Pmid / Pend for all four seasons "
        f"(columns 180--202; the dictionary states no scenario for them: `scenario: {UNSTATED}`).")
    add("- **Horizons.** mid (2045--2054) and end (2085--2094), each against the modeled historical baseline "
        "(1995--2004; a modeled baseline, not an observation). **Scenario:** RCP8.5 --- one high-emissions scenario, "
        "not the only future --- for every column whose field entry names it.")
    add("- **Statistics.** `direction` (DR-TD-005), `absolute_change` (DR-TD-003), `percent_change` (DR-TD-004, the "
        "ratio of mean change to mean baseline; never a mean of percentages; zero baseline → not computable). For the "
        "percent-change columns: `direction` = majority sign of the cells and `percent_change` = the min--max over "
        "cells, **no central value** (DR-PT-006; M1-WP3b: percentages are not averaged; owner decision 2026-10-29).")
    add("- **Geographies.** State (DR-PT-001: unweighted mean over the rows sharing a State label; `State` is "
        "`inferred_candidate` IC-012, so every state and region pattern is provisional, D-034); NCA5 region "
        "(DR-PT-002: unweighted mean over every row whose State label maps to the region; range = min--max of the "
        "member states' values); the P-CELL-1 control cell. No `multi_state_set` is defined in v1.")
    add("- **Rank** (DR-PT-004): descending signed value among geographies of one type; ties share a rank.")
    add("- **Relative tercile** (DR-PT-005): among the U.S. State labels only, by signed value: bottom ⌊n/3⌋ `small`, "
        f"top ⌊n/3⌋ `large`, the rest `moderate`. Skipped, with the reason recorded, when the population is under "
        f"{TERCILE_MIN_POPULATION}, there are fewer than three distinct values, a tie straddles a cut, or any "
        "enumerated state is not computable (placing missing states at either end moves a cut). A disclosed "
        "relative descriptor --- never an absolute threshold and never the sole answer key (ruling 5).")
    add("- **Support and robustness** (DR-PT-003): a state's support is its cells with a value, a region's its "
        "covered member states; robustness is the share of those units whose own direction equals the aggregate's "
        "(`all_states_same_direction` = all, `majority_same_direction` > 1/2, `mixed`); `robustness_unit` names the unit.")
    add("- **Contrasts.** Seasonal (DR-PT-007): per geography and horizon, the four seasons' majority direction and "
        "share of cells increasing on the percent-change columns; the largest-change season is not computed (no "
        "central value). Regional (DR-PT-008): the covered NCA5 regions ordered by value (value metrics) or listed "
        "with their majority direction (percent-change columns).")
    add("")
    add("## NCA5 regions and table coverage")
    add("")
    add(f"Scheme `{nca['region_scheme_id']}` ({nca['region_scheme_name']}, {nca['region_scheme_version']}); map "
        f"`data/metadata/geography/nca_regions_v1.yaml`; **source verification: `{nca['source_verification']}`** "
        "(the NCA5 site did not resolve from the EXECUTOR's machine; Kaiyuan checks the artifact named in the file).")
    add("")
    add("| Region | Covered State labels | Not in the table |")
    add("| --- | --- | --- |")
    for rid, r in summary["region_coverage"].items():
        add(f"| `{rid}` {r['name']} | {len(r['covered'])}: {', '.join(r['covered']) or '---'} | {', '.join(r['uncovered']) or '---'} |")
    add("")
    add(f"Mapped states and DC not in the table's `State` field: {', '.join(summary['nca_states_not_in_table']) or 'none'}. "
        f"Table State labels with no region: {', '.join(summary['table_states_not_in_nca_map']) or 'none'}.")
    add("")
    add("## Counts")
    add("")
    add(f"- Patterns: **{summary['n_patterns']}** --- " + ", ".join(f"{k} {v}" for k, v in summary["by_kind"].items()) + ".")
    add("- By family: " + ", ".join(f"`{k}` {v}" for k, v in summary["by_family"].items()) + ".")
    add("- By geography type: " + ", ".join(f"`{k}` {v}" for k, v in summary["by_geography_type"].items()) + ".")
    add("- By statistic: " + ", ".join(f"`{k}` {v}" for k, v in summary["by_statistic"].items()) + ".")
    add("- By status: " + ", ".join(f"`{k}` {v}" for k, v in summary["by_status"].items()) + ".")
    add(f"- Acceptance blocked (FWI summer value, IC-006..IC-010): {summary['n_acceptance_blocked']}.")
    add(f"- With a relative tercile: {summary['n_with_relative_tercile']}.")
    add("")
    add("| Family | Geography | Statistic | Patterns |")
    add("| --- | --- | --- | --- |")
    for k, v in summary["by_family_geography_statistic"].items():
        f, g, s = k.split("|")
        add(f"| `{f}` | {g} | `{s}` | {v} |")
    add("")
    add("## Degeneracy cases --- terciles skipped")
    add("")
    add(f"Among the ranked state groups (value metrics × horizon × absolute / percent change), "
        f"**{summary['tercile_groups_skipped']}** skipped the tercile: "
        + (", ".join(f"`{k}` {v}" for k, v in summary["tercile_groups_skipped_by_reason"].items()) or "none") + ". "
        f"Region patterns never carry one (population under {TERCILE_MIN_POPULATION}); percent-change-column patterns "
        "never do (no central value).")
    add("")
    if summary["tercile_skips"]:
        add("| Metric | Horizon | Statistic | Reason |")
        add("| --- | --- | --- | --- |")
        for s in summary["tercile_skips"]:
            add(f"| `{s['metric']}` | {s['horizon']} | `{s['statistic']}` | {s['reason']} |")
        add("")
    add("## Ten example patterns")
    add("")
    add("Rule: the first ten pattern ids. Ids are `TP1-<n>` in enumeration order (metric, horizon, statistic; then "
        "NCA region, state, control cell), then seasonal contrasts, then regional contrasts.")
    add("")
    for r in examples:
        L.extend(_example_line(r))
    add("")
    add("## What a pattern is not")
    add("")
    add("- Not a question: an item's prompt names no table, column, cell or value (D-035; ruling condition A).")
    add("- Not consensus: a table pattern is what this projection shows, not universal climate knowledge (ruling, risk 3).")
    add("- Not a mechanism: the mechanism comes from literature statements (ruling, condition E).")
    add("- FWI is a fire-danger index, never fire occurrence. The historical value is a modeled baseline.")
    add("")
    return "\n".join(L)


def doc_hashes(table_sha: str, patterns_sha: str) -> dict:
    def rel(p: Path) -> str:
        return str(p.relative_to(REPO_ROOT))

    return {"data/raw/FullData.csv": table_sha,
            rel(td.SLOTS_PATH): td.file_sha256(td.SLOTS_PATH),
            rel(NCA_MAP_PATH): td.file_sha256(NCA_MAP_PATH),
            rel(td.COVERAGE_PATH): td.file_sha256(td.COVERAGE_PATH),
            rel(PATTERNS_PATH): patterns_sha,
            rel(SUMMARY_PATH): td.file_sha256(SUMMARY_PATH),
            rel(EXAMPLES_PATH): td.file_sha256(EXAMPLES_PATH)}


def dumps(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
