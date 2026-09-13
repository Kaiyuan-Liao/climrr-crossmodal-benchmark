#!/usr/bin/env python3
"""M1-WP3b Phase A: what the table's own structure says about "cell", "county" and "state".

Computed facts first, and nothing else. This script answers six structural
questions about `data/raw/FullData.csv` so that the prototype phenomenon units
built in Phase C rest on measured properties rather than on the assumption that
a label behaves like a geography.

Every value it reports is a string. Nothing here is interpreted: that a column
holds one value per `GEOID` is a statement about the table, not a statement
about counties, and the output says so wherever the distinction could be lost.

Two columns outside the pilot subset are touched
------------------------------------------------

Check 4 tests whether indices 110 `NAME_1` and 111 `NAMELSAD` are functions of
`GEOID`. Neither column is in the M1-WP3 pilot subset, neither is interpreted
here, and no prototype record uses either. The check counts distinct values per
key and reports the count. That is the whole of it.

What this script does not do
----------------------------

No aggregation of climate values. No magnitude. No ranking. No claim that a
`(State, NAME)` pair is a county, or that a `GEOID` is a Census tract --- those
readings are `inferred_candidate` (IC-011, IC-012, IC-017) and stay that way.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr.examples import PILOT_INDICES  # noqa: E402
from climrr.manifest import ManifestMismatchError, verify_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.profile import ENCODING  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

DATA_PATH = REPO_ROOT / "data" / "raw" / "FullData.csv"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"
OUT_JSON = REPO_ROOT / "artifacts" / "profiles" / "hierarchy_checks.json"
OUT_MD = REPO_ROOT / "artifacts" / "profiles" / "hierarchy_checks.md"

#: Serialised as a string like every other value in this report. The work
#: package asks for `str` throughout so that nothing in the output can be
#: compared, sorted or rounded as a number by accident.
HIERARCHY_CHECKS_VERSION = "1"

OID_INDEX = 0
CROSSMODEL_INDEX = 1
NAME_INDEX = 2
STATE_INDEX = 3
TRACTCE_INDEX = 108
GEOID_INDEX = 109
NAME_1_INDEX = 110
NAMELSAD_INDEX = 111

#: The two rows Phase C builds its prototypes around, addressed by `OID_` value.
FOCUS_OIDS = ("1", "14")

#: How many duplicated values a check will list before truncating. A check that
#: truncates says so in its own output; it never reports a shortened list as
#: though it were complete.
LIST_CAP = 50


class HierarchyError(RuntimeError):
    """The file does not have the shape the checks assume."""


def _stats(counts: list[int]) -> dict:
    """min / median / max of a list of per-key row counts, all as strings."""
    if not counts:
        return {"n_keys": "0", "min": None, "median": None, "max": None, "total_rows": "0"}
    return {
        "n_keys": str(len(counts)),
        "min": str(min(counts)),
        "median": str(statistics.median(counts)),
        "max": str(max(counts)),
        "total_rows": str(sum(counts)),
    }


def run_checks(path: Path) -> dict:
    """One streaming pass, then a second for the focus coverage.

    The two passes are deliberate: the coverage in check 6 is measured against
    the `State` and `(State, NAME)` labels of rows the first pass locates, and
    resolving those labels before counting keeps the counting rule fixed rather
    than dependent on file order.
    """
    header, focus_rows, n_rows = _first_pass(path)
    if len(header) <= NAMELSAD_INDEX:
        raise HierarchyError(
            f"header has {len(header)} fields, fewer than the {NAMELSAD_INDEX + 1} "
            "the checks need. Stop and report."
        )
    missing = [oid for oid in FOCUS_OIDS if oid not in focus_rows]
    if missing:
        raise HierarchyError(
            f"no row carries OID_ {missing}. That is a finding about the data, not an "
            "empty result; stop and report."
        )

    focus_state = focus_rows["1"][STATE_INDEX]
    focus_pair = (focus_rows["1"][STATE_INDEX], focus_rows["1"][NAME_INDEX])
    state_of_14 = focus_rows["14"][STATE_INDEX]

    crossmodel_counts: Counter[str] = Counter()
    pair_counts: Counter[tuple[str, str]] = Counter()
    geoid_counts: Counter[str] = Counter()
    geoid_to_pairs: defaultdict[str, set] = defaultdict(set)
    geoid_to_name1: defaultdict[str, set] = defaultdict(set)
    geoid_to_namelsad: defaultdict[str, set] = defaultdict(set)
    empty_state_rows: list[dict] = []

    # Coverage accumulators for check 6.
    state_rows = 0
    pair_rows = 0
    state14_rows = 0
    state_empty = Counter()
    pair_empty = Counter()

    with path.open("r", encoding=ENCODING, newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        for row in reader:
            crossmodel_counts[row[CROSSMODEL_INDEX]] += 1
            pair = (row[STATE_INDEX], row[NAME_INDEX])
            pair_counts[pair] += 1
            geoid = row[GEOID_INDEX]
            geoid_counts[geoid] += 1
            geoid_to_pairs[geoid].add(pair)
            geoid_to_name1[geoid].add(row[NAME_1_INDEX])
            geoid_to_namelsad[geoid].add(row[NAMELSAD_INDEX])
            if row[STATE_INDEX] == "":
                empty_state_rows.append(
                    {
                        "OID_": row[OID_INDEX],
                        "Crossmodel": row[CROSSMODEL_INDEX],
                        "NAME": row[NAME_INDEX],
                        "GEOID": row[GEOID_INDEX],
                    }
                )
            if row[STATE_INDEX] == focus_state:
                state_rows += 1
                for index in PILOT_INDICES:
                    if row[index] == "":
                        state_empty[index] += 1
            if pair == focus_pair:
                pair_rows += 1
                for index in PILOT_INDICES:
                    if row[index] == "":
                        pair_empty[index] += 1
            if row[STATE_INDEX] == state_of_14:
                state14_rows += 1

    duplicated = {value: n for value, n in crossmodel_counts.items() if n > 1}
    geoid_multi_pair = {
        geoid: sorted("\t".join(pair) for pair in pairs)
        for geoid, pairs in geoid_to_pairs.items()
        if len(pairs) > 1
    }
    name1_multi = {geoid: len(values) for geoid, values in geoid_to_name1.items() if len(values) > 1}
    namelsad_multi = {
        geoid: len(values) for geoid, values in geoid_to_namelsad.items() if len(values) > 1
    }

    return {
        "hierarchy_checks_version": HIERARCHY_CHECKS_VERSION,
        "n_rows": str(n_rows),
        "focus_rows": {
            oid: {
                "row_ordinal": str(ordinal),
                "Crossmodel": focus_rows[oid][CROSSMODEL_INDEX],
                "NAME": focus_rows[oid][NAME_INDEX],
                "State": focus_rows[oid][STATE_INDEX],
                "GEOID": focus_rows[oid][GEOID_INDEX],
            }
            for oid, ordinal in _focus_ordinals(focus_rows).items()
        },
        "check_1_crossmodel_uniqueness": {
            "question": "Is `Crossmodel` unique across the rows of this file?",
            "n_rows": str(n_rows),
            "n_distinct": str(len(crossmodel_counts)),
            "is_unique": str(len(crossmodel_counts) == n_rows),
            "n_duplicated_values": str(len(duplicated)),
            "duplicated_values": {value: str(n) for value, n in sorted(duplicated.items())[:LIST_CAP]},
            "duplicated_values_truncated": str(len(duplicated) > LIST_CAP),
            "what_it_does_not_say": (
                "Uniqueness is a property of the column's characters. It does not "
                "establish that one row is one grid cell; that is assumption A-G0."
            ),
        },
        "check_2_rows_per_state_name_pair": {
            "question": "How many rows share a `(State, NAME)` label?",
            **_stats(list(pair_counts.values())),
            "focus_pair_OID_1": {
                "State": focus_pair[0],
                "NAME": focus_pair[1],
                "n_rows": str(pair_counts[focus_pair]),
            },
            "focus_pair_OID_14": {
                "State": focus_rows["14"][STATE_INDEX],
                "NAME": focus_rows["14"][NAME_INDEX],
                "n_rows": str(
                    pair_counts[(focus_rows["14"][STATE_INDEX], focus_rows["14"][NAME_INDEX])]
                ),
            },
            "what_it_does_not_say": (
                "A `(State, NAME)` pair is a label shared by a set of rows. Whether "
                "that set is a county, and whether it covers a county completely, is "
                "not established here --- IC-011 and IC-012 hold both readings at "
                "`inferred_candidate`."
            ),
        },
        "check_3_rows_per_geoid": {
            "question": "How many rows share a `GEOID`, and does each `GEOID` carry one `(State, NAME)`?",
            **_stats(list(geoid_counts.values())),
            "n_geoid_spanning_multiple_state_name_pairs": str(len(geoid_multi_pair)),
            "geoid_spanning_multiple_state_name_pairs": {
                geoid: pairs for geoid, pairs in sorted(geoid_multi_pair.items())[:LIST_CAP]
            },
            "geoid_spanning_multiple_truncated": str(len(geoid_multi_pair) > LIST_CAP),
            "each_geoid_one_state_name_pair": str(not geoid_multi_pair),
            "note_empty_geoid": (
                "The empty string is counted as a key like any other value; "
                "`check_5` reports the rows that carry it."
            ),
        },
        "check_4_name1_namelsad_by_geoid": {
            "question": (
                "Do indices 110 `NAME_1` and 111 `NAMELSAD` take exactly one value per `GEOID`?"
            ),
            "scope_note": (
                "Structural only. Neither column is in the pilot subset, neither is "
                "interpreted, and no prototype record uses either."
            ),
            "n_geoid_keys": str(len(geoid_counts)),
            "NAME_1_n_geoid_with_more_than_one_value": str(len(name1_multi)),
            "NAME_1_is_function_of_geoid": str(not name1_multi),
            "NAMELSAD_n_geoid_with_more_than_one_value": str(len(namelsad_multi)),
            "NAMELSAD_is_function_of_geoid": str(not namelsad_multi),
        },
        "check_5_rows_with_empty_state": {
            "question": "Which rows carry no `State` value?",
            "n_rows": str(len(empty_state_rows)),
            "rows": empty_state_rows[:LIST_CAP],
            "truncated": str(len(empty_state_rows) > LIST_CAP),
            "what_it_does_not_say": (
                'An empty cell is "no value in this file". It is not a zero and not a '
                "claim that the row lies outside any state (Q16)."
            ),
        },
        "check_6_focus_coverage": {
            "question": (
                "How many rows carry the `State` of `OID_` 1, the `(State, NAME)` of "
                "`OID_` 1, and the `State` of `OID_` 14 --- and how complete are the "
                "pilot columns on the first two?"
            ),
            "state_of_OID_1": {
                "State": focus_state,
                "n_rows": str(state_rows),
                "empty_pilot_columns": _coverage(state_empty, state_rows),
            },
            "state_name_pair_of_OID_1": {
                "State": focus_pair[0],
                "NAME": focus_pair[1],
                "n_rows": str(pair_rows),
                "empty_pilot_columns": _coverage(pair_empty, pair_rows),
            },
            "state_of_OID_14": {"State": state_of_14, "n_rows": str(state14_rows)},
            "n_pilot_columns": str(len(PILOT_INDICES)),
        },
    }


def _coverage(empty: Counter, n_rows: int) -> dict:
    """Per pilot column, how many of the selected rows are empty. Zeroes omitted."""
    return {
        str(index): {"n_empty": str(empty[index]), "of_n_rows": str(n_rows)}
        for index in PILOT_INDICES
        if empty[index]
    }


def _focus_ordinals(focus_rows: dict) -> dict:
    return {oid: focus_rows[oid + "__ordinal"] for oid in FOCUS_OIDS}


def _first_pass(path: Path) -> tuple[list[str], dict, int]:
    """Header, the focus rows by `OID_` (plus their ordinals), and the row count."""
    focus: dict = {}
    n_rows = 0
    with path.open("r", encoding=ENCODING, newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, None) or []
        for ordinal, row in enumerate(reader):
            n_rows += 1
            oid = row[OID_INDEX]
            if oid in FOCUS_OIDS and oid not in focus:
                focus[oid] = list(row)
                focus[oid + "__ordinal"] = ordinal
    return header, focus, n_rows


# --- the markdown summary -----------------------------------------------------


def render_markdown(result: dict, csv_sha256: str) -> str:
    c1 = result["check_1_crossmodel_uniqueness"]
    c2 = result["check_2_rows_per_state_name_pair"]
    c3 = result["check_3_rows_per_geoid"]
    c4 = result["check_4_name1_namelsad_by_geoid"]
    c5 = result["check_5_rows_with_empty_state"]
    c6 = result["check_6_focus_coverage"]
    lines = [
        "# Hierarchy checks --- computed structural properties",
        "",
        "Produced by `scripts/hierarchy_checks.py` (M1-WP3b Phase A). Every value is a",
        "string read from the file. **No meaning is assigned to any of them.** That a set",
        "of rows shares a label is a fact about the table; that the set is a *county* is",
        "an `inferred_candidate` reading (IC-011, IC-012) and is not established here.",
        "",
        f"- CSV SHA-256: `{csv_sha256}`",
        f"- Data rows: {result['n_rows']}",
        "",
        "## 1. Is `Crossmodel` unique?",
        "",
        f"| Rows | Distinct `Crossmodel` | Unique | Duplicated values |",
        "| ---: | ---: | :--- | ---: |",
        f"| {c1['n_rows']} | {c1['n_distinct']} | **{c1['is_unique']}** | {c1['n_duplicated_values']} |",
        "",
        f"{c1['what_it_does_not_say']}",
        "",
        "## 2. Rows per `(State, NAME)` pair",
        "",
        "| Pairs | Min rows | Median rows | Max rows | Rows covered |",
        "| ---: | ---: | ---: | ---: | ---: |",
        f"| {c2['n_keys']} | {c2['min']} | {c2['median']} | {c2['max']} | {c2['total_rows']} |",
        "",
        f"- The pair of `OID_` 1: `{c2['focus_pair_OID_1']['State']}` / "
        f"`{c2['focus_pair_OID_1']['NAME']}` --- {c2['focus_pair_OID_1']['n_rows']} rows.",
        f"- The pair of `OID_` 14: `{c2['focus_pair_OID_14']['State']}` / "
        f"`{c2['focus_pair_OID_14']['NAME']}` --- {c2['focus_pair_OID_14']['n_rows']} rows.",
        "",
        f"{c2['what_it_does_not_say']}",
        "",
        "## 3. Rows per `GEOID`",
        "",
        "| `GEOID` keys | Min rows | Median rows | Max rows | Rows covered |",
        "| ---: | ---: | ---: | ---: | ---: |",
        f"| {c3['n_keys']} | {c3['min']} | {c3['median']} | {c3['max']} | {c3['total_rows']} |",
        "",
        f"- `GEOID` values spanning more than one `(State, NAME)` pair: "
        f"**{c3['n_geoid_spanning_multiple_state_name_pairs']}**.",
        f"- Each `GEOID` carries exactly one `(State, NAME)` pair: "
        f"**{c3['each_geoid_one_state_name_pair']}**.",
        "",
        "## 4. Are `NAME_1` and `NAMELSAD` functions of `GEOID`?",
        "",
        f"{c4['scope_note']}",
        "",
        "| Column | `GEOID` keys with more than one value | One value per `GEOID` |",
        "| --- | ---: | :--- |",
        f"| 110 `NAME_1` | {c4['NAME_1_n_geoid_with_more_than_one_value']} | "
        f"**{c4['NAME_1_is_function_of_geoid']}** |",
        f"| 111 `NAMELSAD` | {c4['NAMELSAD_n_geoid_with_more_than_one_value']} | "
        f"**{c4['NAMELSAD_is_function_of_geoid']}** |",
        "",
        "## 5. Rows with no `State` value",
        "",
        f"{c5['n_rows']} row(s).",
        "",
        "| `OID_` | `Crossmodel` | `NAME` | `GEOID` |",
        "| --- | --- | --- | --- |",
    ]
    for row in c5["rows"]:
        name = row["NAME"] or "(empty)"
        geoid = row["GEOID"] or "(empty)"
        lines.append(f"| {row['OID_']} | `{row['Crossmodel']}` | `{name}` | `{geoid}` |")
    lines += [
        "",
        f"{c5['what_it_does_not_say']}",
        "",
        "## 6. The row sets the Phase C prototypes are built from",
        "",
        "| Row set | Rows |",
        "| --- | ---: |",
        f"| `State` = `{c6['state_of_OID_1']['State']}` (the state of `OID_` 1) | "
        f"{c6['state_of_OID_1']['n_rows']} |",
        f"| `(State, NAME)` = `{c6['state_name_pair_of_OID_1']['State']}` / "
        f"`{c6['state_name_pair_of_OID_1']['NAME']}` (the pair of `OID_` 1) | "
        f"{c6['state_name_pair_of_OID_1']['n_rows']} |",
        f"| `State` = `{c6['state_of_OID_14']['State']}` (the state of `OID_` 14) | "
        f"{c6['state_of_OID_14']['n_rows']} |",
        "",
        f"Pilot columns checked for emptiness: {c6['n_pilot_columns']}.",
        "",
    ]
    for key, label in (
        ("state_of_OID_1", "the state of `OID_` 1"),
        ("state_name_pair_of_OID_1", "the `(State, NAME)` pair of `OID_` 1"),
    ):
        empty = c6[key]["empty_pilot_columns"]
        if not empty:
            lines.append(
                f"Across {label}, **no pilot column has an empty value** on any of its "
                f"{c6[key]['n_rows']} rows."
            )
        else:
            lines.append(
                f"Across {label}, the pilot columns with at least one empty value are:"
            )
            lines.append("")
            lines.append("| Column index | Empty rows | Of rows |")
            lines.append("| ---: | ---: | ---: |")
            for index, counts in empty.items():
                lines.append(f"| {index} | {counts['n_empty']} | {counts['of_n_rows']} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    try:
        verified = verify_file(args.data, args.manifest)
    except (ManifestMismatchError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print(f"Manifest check OK: {args.data.name} sha256={verified['sha256']}")

    try:
        result = run_checks(args.data)
    except HierarchyError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    result = {"data_sha256": verified["sha256"], **result}

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    args.out_md.write_text(render_markdown(result, verified["sha256"]), encoding="utf-8")

    c1 = result["check_1_crossmodel_uniqueness"]
    c2 = result["check_2_rows_per_state_name_pair"]
    c3 = result["check_3_rows_per_geoid"]
    print(f"  Crossmodel unique              : {c1['is_unique']} "
          f"({c1['n_distinct']} distinct / {c1['n_rows']} rows)")
    print(f"  (State, NAME) pairs            : {c2['n_keys']} "
          f"(min {c2['min']}, median {c2['median']}, max {c2['max']} rows)")
    print(f"    pair of OID_ 1               : {c2['focus_pair_OID_1']['State']} / "
          f"{c2['focus_pair_OID_1']['NAME']} -> {c2['focus_pair_OID_1']['n_rows']} rows")
    print(f"  GEOID keys                     : {c3['n_keys']} "
          f"(min {c3['min']}, median {c3['median']}, max {c3['max']} rows)")
    print(f"    each GEOID one (State, NAME) : {c3['each_geoid_one_state_name_pair']} "
          f"({c3['n_geoid_spanning_multiple_state_name_pairs']} span more than one)")
    print(f"  rows with empty State          : "
          f"{result['check_5_rows_with_empty_state']['n_rows']}")
    c6 = result["check_6_focus_coverage"]
    print(f"  state of OID_ 14               : {c6['state_of_OID_14']['State']} -> "
          f"{c6['state_of_OID_14']['n_rows']} rows")

    record_path = write_run_record(
        "hierarchy_checks",
        result_summary={
            "crossmodel_is_unique": c1["is_unique"],
            "crossmodel_n_distinct": c1["n_distinct"],
            "n_state_name_pairs": c2["n_keys"],
            "rows_in_pair_of_OID_1": c2["focus_pair_OID_1"]["n_rows"],
            "n_geoid_keys": c3["n_keys"],
            "each_geoid_one_state_name_pair": c3["each_geoid_one_state_name_pair"],
            "n_geoid_spanning_multiple_pairs": c3["n_geoid_spanning_multiple_state_name_pairs"],
            "NAME_1_is_function_of_geoid": result["check_4_name1_namelsad_by_geoid"][
                "NAME_1_is_function_of_geoid"
            ],
            "NAMELSAD_is_function_of_geoid": result["check_4_name1_namelsad_by_geoid"][
                "NAMELSAD_is_function_of_geoid"
            ],
            "n_rows_with_empty_state": result["check_5_rows_with_empty_state"]["n_rows"],
            "rows_in_state_of_OID_14": c6["state_of_OID_14"]["n_rows"],
        },
        passed=True,
        data_path=args.data,
        data_sha256=verified["sha256"],
        output_path=args.out_json,
        config_snapshot={
            "data_path": repo_relative(args.data),
            "out_json": repo_relative(args.out_json),
            "out_md": repo_relative(args.out_md),
            "focus_oids": list(FOCUS_OIDS),
            "pilot_indices": list(PILOT_INDICES),
            "list_cap": LIST_CAP,
        },
    )
    print(f"Run record: {repo_relative(record_path)}")
    print(f"Wrote {repo_relative(args.out_json)} and {repo_relative(args.out_md)}")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
