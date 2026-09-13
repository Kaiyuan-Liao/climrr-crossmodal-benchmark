#!/usr/bin/env python3
"""M1-WP3b Phases C and D: three prototype phenomenon units, and their register.

**Prototype work, ahead of its ruling.** Built on Kaiyuan's decision of
2026-09-13 following the mentor's direction R-002, while the GUIDANCE ruling
that would authorise county/state units, aggregation and a magnitude field is
still pending. The D-010 ruling in force forbids all three inside M1-WP3
examples. Nothing here is evidence for a milestone gate and the ruling may
discard it. See `reports/milestones/M1_WP3b_PROTOTYPE_REPORT.md` field 12.

What it does, in order
----------------------

1. Verifies `data/raw/FullData.csv` against `data/manifest.json`, fail-closed
   (D-005), and refuses to run if the coverage report was built from other bytes.
2. Loads the coverage report and the inferred-candidate records and builds the
   pilot semantics --- the same `climrr.examples.build_semantics` the M1-WP3
   example records use, so a column means here exactly what it means there.
3. Streams the CSV **once**, reading only the six columns the two variables use
   plus the three label columns, as strings. It accumulates, in the same pass:
   every cell's change value; per-county and per-state sums and counts; and the
   complete member rows of the three chosen units.
4. Builds the three distributions PR-1 ranks against, at all three levels for
   **both** variables --- six in total, of which three are used and none is
   narrated.
5. Builds `P-CELL-1`, `P-COUNTY-1` and `P-STATE-1`, checks that no inferred value
   appears in a generated description outside its label, and fails the run if one
   does.
6. Writes the records, `docs/PHENOMENON_PROTOTYPES.md`,
   `docs/PHENOMENON_ASSUMPTIONS.md` and a run record.

How the three units are chosen
------------------------------

By identity, before any value is read: the row `OID_` 1 of M1-WP3's Example 1;
the `(State, NAME)` label that row carries; and the `State` label of `OID_` 14,
M1-WP3's Example 2. **No magnitude is consulted anywhere in the choice.** PR-1
is applied to a unit already fixed, never to pick one.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr.dictionary import (  # noqa: E402
    InferredCandidateError,
    load_inferred_candidates,
)
from climrr.examples import build_semantics  # noqa: E402
from climrr.manifest import ManifestMismatchError, verify_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.phenomenon import (  # noqa: E402
    ASSUMPTIONS,
    VALIDATION_BANNER,
    LEVELS,
    NO_ASSUMPTION_NEEDED,
    PR1_STATEMENT,
    SCHEMA_VERSION,
    VARIABLES,
    PhenomenonError,
    assumptions_for,
    build_record,
    change_value_of,
    columns_used,
    has_all_values,
    mean_from_total,
    unlabelled_inferred_text,
    variable_of,
)
from climrr.profile import ENCODING  # noqa: E402
from climrr.runrecord import git_commit, write_run_record  # noqa: E402

DATA_PATH = REPO_ROOT / "data" / "raw" / "FullData.csv"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"
COVERAGE_PATH = REPO_ROOT / "artifacts" / "profiles" / "dictionary_coverage.json"
INFERRED_PATH = REPO_ROOT / "data" / "metadata" / "inferred_candidates.yaml"
OUT_DIR = REPO_ROOT / "artifacts" / "phenomena" / "prototypes"
PROTOTYPES_DOC = REPO_ROOT / "docs" / "PHENOMENON_PROTOTYPES.md"
ASSUMPTIONS_DOC = REPO_ROOT / "docs" / "PHENOMENON_ASSUMPTIONS.md"

#: How a level's key reads in the reference-population definition. Written out
#: rather than derived from `LEVEL_KEYS`, because the definition has to name the
#: columns a reader can go and look at.
KEY_PHRASE = {
    "cell": "`Crossmodel` value",
    "county": "`(State, NAME)` label",
    "state": "`State` label",
}

OID_INDEX = 0
CROSSMODEL_INDEX = 1
NAME_INDEX = 2
STATE_INDEX = 3

#: The three units, fixed by identity before a value is read.
PROTOTYPES = (
    {
        "record_id": "P-CELL-1",
        "level": "cell",
        "variable_key": "fwi_summer_hist_to_end85",
        "chosen_by": (
            "the row `OID_` 1, which is M1-WP3's Example 1 --- itself selected by "
            "structural rule R-A, the first row non-empty on every pilot column"
        ),
        "anchor_oid": "1",
    },
    {
        "record_id": "P-COUNTY-1",
        "level": "county",
        "variable_key": "fwi_summer_hist_to_end85",
        "chosen_by": "the `(State, NAME)` label carried by the row `OID_` 1",
        "anchor_oid": "1",
    },
    {
        "record_id": "P-STATE-1",
        "level": "state",
        "variable_key": "heatindex_day105_summer_hist_to_end85",
        "chosen_by": "the `State` label carried by the row `OID_` 14, M1-WP3's Example 2",
        "anchor_oid": "14",
    },
)

ANCHOR_OIDS = tuple(sorted({prototype["anchor_oid"] for prototype in PROTOTYPES}))


def unit_key(level: str, row: list[str]) -> tuple[str, ...]:
    if level == "cell":
        return (row[CROSSMODEL_INDEX],)
    if level == "county":
        return (row[STATE_INDEX], row[NAME_INDEX])
    return (row[STATE_INDEX],)


def identifier_of(level: str, key: tuple[str, ...]) -> dict:
    if level == "cell":
        return {"Crossmodel": key[0]}
    if level == "county":
        return {"State": key[0], "NAME": key[1]}
    return {"State": key[0]}


def find_anchors(path: Path) -> dict:
    """Pass one: the rows the three units are named after. Four columns read."""
    anchors: dict[str, dict] = {}
    n_rows = 0
    with path.open("r", encoding=ENCODING, newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        for row in reader:
            n_rows += 1
            oid = row[OID_INDEX]
            if oid in ANCHOR_OIDS and oid not in anchors:
                anchors[oid] = {
                    "OID_": oid,
                    "Crossmodel": row[CROSSMODEL_INDEX],
                    "NAME": row[NAME_INDEX],
                    "State": row[STATE_INDEX],
                }
    missing = [oid for oid in ANCHOR_OIDS if oid not in anchors]
    if missing:
        raise PhenomenonError(
            f"no row carries OID_ {missing}. That is a finding about the data, not an "
            "empty result; stop and report."
        )
    return {"anchors": anchors, "n_rows": n_rows}


def scan(path: Path, targets: dict) -> dict:
    """Pass two: the six PR-1 distributions, and the members of the three units.

    Counties and states accumulate as a running (sum, count) rather than as
    lists of values: 3,019 county keys over 62,834 rows is not a thing to hold,
    and a mean is all a distribution needs. The **complete** member rows of the
    three chosen units are retained in full, because a record has to carry every
    one of them --- no sampling, at any level.
    """
    indices = sorted({index for variable in VARIABLES for index in columns_used(variable)})
    members: dict[str, list[dict]] = {record_id: [] for record_id in targets}
    per_level: dict[tuple[str, str], defaultdict] = {
        (level, variable["key"]): defaultdict(lambda: [Decimal(0), 0])
        for level in LEVELS
        for variable in VARIABLES
    }
    n_rows = 0

    with path.open("r", encoding=ENCODING, newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        for row in reader:
            n_rows += 1
            member = {
                "crossmodel": row[CROSSMODEL_INDEX],
                "values": {index: row[index] for index in indices},
            }
            keys = {level: unit_key(level, row) for level in LEVELS}
            for record_id, target in targets.items():
                if keys[target["level"]] == target["key"]:
                    members[record_id].append(member)
            for variable in VARIABLES:
                if not has_all_values(member, variable):
                    continue
                change = change_value_of(member, variable)
                for level in LEVELS:
                    bucket = per_level[(level, variable["key"])][keys[level]]
                    bucket[0] += change
                    bucket[1] += 1
    return {"n_rows": n_rows, "members": members, "per_level": per_level}


def distributions(per_level: dict) -> tuple[dict, dict]:
    """The sorted change values PR-1 ranks against, one list per level per variable.

    Two rules, both stated in the membership note that travels with every record:

    * A unit with no member cell carrying a value on every column used has no
      change value and is **absent** from its level's distribution rather than
      present as a zero.
    * A unit whose label is the **empty string** is a unit like any other. The 7
      rows with no `State` form one state-shaped unit and one county-shaped unit,
      and they are counted. Dropping them would be a judgement about what an
      empty label means, and this project does not have one (Q16).
    """
    values_by_key = {}
    membership_by_key = {}
    for (level, variable_key), buckets in per_level.items():
        values = sorted(
            mean_from_total(total, count) for total, count in buckets.values() if count
        )
        empty_labelled = sum(
            1 for key, (_total, count) in buckets.items() if count and any(part == "" for part in key)
        )
        excluded = sum(1 for _total, count in buckets.values() if not count)
        key_phrase = KEY_PHRASE[level]
        change_phrase = (
            "the change value of its one cell"
            if level == "cell"
            else "the unweighted mean of its member cells' change values"
        )
        values_by_key[(level, variable_key)] = values
        membership_by_key[(level, variable_key)] = {
            "how_units_were_formed": (
                f"every distinct {key_phrase} in the file forms one {level}-level unit"
            ),
            "n_keys": str(len(buckets)),
            "n_units": str(len(values)),
            "n_units_excluded_for_having_no_value": str(excluded),
            "n_units_whose_label_is_the_empty_string": str(empty_labelled),
            # The exact definition the M1-WP3b ruling (action 10) asks every `M`
            # field to carry, assembled from the counts rather than asserted.
            "reference_population": (
                f"every distinct {key_phrase} in the file, each forming one "
                f"{level}-level unit ({len(buckets)} of them); a unit is included if at "
                f"least one member cell is non-empty on every column this variable reads "
                f"({len(values)} included, {excluded} excluded); its change value is "
                f"{change_phrase}; units whose label is the empty string are included "
                f"({empty_labelled} here)"
            ),
            "empty_label_note": (
                "A unit whose label is the empty string is counted. The 7 rows with no "
                "`State` form one such unit at state level and one at county level. "
                "Dropping them would be a judgement about what an empty label means, and "
                "this project does not have one (Q16)."
            ),
        }
    return values_by_key, membership_by_key


# --- the documents ------------------------------------------------------------


def render_assumptions_doc(records: list[dict]) -> str:
    """`docs/PHENOMENON_ASSUMPTIONS.md`, generated from the register."""
    used = {}
    for record in records:
        for assumption_id in record["assumptions"]:
            used.setdefault(assumption_id, []).append(record["record_id"])
    lines = [
        "# Phenomenon assumptions register --- M1-WP3b prototypes",
        "",
        "**Prototype.** Every row below is something the three records in",
        "[`PHENOMENON_PROTOTYPES.md`](PHENOMENON_PROTOTYPES.md) lean on that is **not**",
        "established by the data dictionary. Generated from `climrr.phenomenon.ASSUMPTIONS`;",
        "edit the module, not this file.",
        "",
        "`computed` means a script in this repository measured it from the bytes.",
        "`unverified` means it is reasoned, written down, and established by nothing.",
        "`owner_confirmed` means the mentor confirmed it --- **nothing holds that status**,",
        "and nothing will until she answers.",
        "",
        "Rows marked **T** in the last column are the ones worth putting in front of the",
        "mentor on Thursday, 2026-09-17.",
        "",
        "| ID | Statement | Affects | How it could be verified | Status | Maps to | Used by | T |",
        "| --- | --- | --- | --- | --- | --- | --- | :-: |",
    ]
    for item in ASSUMPTIONS:
        users = ", ".join(used.get(item["id"], [])) or "— (not used by a prototype)"
        flag = "**T**" if item["mentor_checkable"] else ""
        lines.append(
            f"| `{item['id']}` | {item['statement']} | {item['affects']} | "
            f"{item['how_verified']} | `{item['status']}` | {item['maps_to']} | {users} | {flag} |"
        )
    lines += [
        "",
        "## Where no assumption was needed",
        "",
        NO_ASSUMPTION_NEEDED,
        "",
        "## The provisional rule in full",
        "",
        f"> {PR1_STATEMENT}",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def render_prototypes_doc(records: list[dict], commit: str, csv_sha256: str) -> str:
    """`docs/PHENOMENON_PROTOTYPES.md` --- the three units, compactly."""
    lines = [
        "# Three prototype phenomenon units",
        "",
        VALIDATION_BANNER,
        "",
        "Built for M1-WP3b on Kaiyuan's decision of 2026-09-13, following the mentor's",
        "direction R-002, ahead of the GUIDANCE ruling that would authorise county and",
        "state units, aggregation and a magnitude field. That ruling came back **PASS",
        "WITH ACTIONS** and is recorded as D-013, which admits this package as an explicit",
        "**milestone-order exception** --- early M3-style validation while M1 is still",
        "open. **Nothing here is evidence for a milestone gate**, and nothing is merged.",
        "",
        f"- Schema version `{SCHEMA_VERSION}` --- `src/climrr/phenomenon.py`",
        f"- Built from commit `{commit}`, CSV SHA-256 `{csv_sha256}`",
        "- Assumptions, in full: [`PHENOMENON_ASSUMPTIONS.md`](PHENOMENON_ASSUMPTIONS.md)",
        "- Structural facts the units rest on:"
        " [`../artifacts/profiles/hierarchy_checks.md`](../artifacts/profiles/hierarchy_checks.md)",
        "",
        "Each record's fields are `G` scope, `H` concept, `S` season, `T` time horizon,",
        "`C` climate scenario, `V` values, `D` direction, `M` magnitude, `P` provenance.",
        "**Two conventions for the letters exist and neither is settled.** These are the",
        "mentor's and Kaiyuan's, which is what the code emits because they are what she has",
        "seen; the M1-WP3b ruling reads `S` as scenario, `T` as temporal horizon and `C` as",
        "compared quantity. Both agree on `P` and on what a record carries. D-013 records",
        "the pair for the next GUIDANCE packet. **No number depends on the choice.**",
        "",
    ]
    for record in records:
        g, h, m = record["G"], record["H"], record["M"]
        probe = record["literature_probe"]
        identifier = ", ".join(f"`{value}`" for value in g["identifier"].values())
        lines += [
            f"## {record['record_id']} --- {g['level']} level",
            "",
            VALIDATION_BANNER,
            "",
            "| Field | Value | Status |",
            "| --- | --- | --- |",
            f"| `G` identifier | {identifier} | `{g['provenance_status']}` |",
            f"| `G` members | {g['n_cells']} cell(s); {g['n_cells_with_value']} with a "
            f"value, {g['n_cells_empty']} without | `computed` |",
            f"| `H` variable | {h['variable_label']} | `{h['provenance_status']}` |",
            f"| `H` columns | "
            + ", ".join(f"{c['index']} `{c['column']}` ({c['role']})" for c in h["columns"])
            + " | per column, below |",
            f"| `V` change value | `{record['D']['change_value']}` | "
            f"`{record['D']['provenance_status']}` |",
            f"| `D` direction | **{record['D']['direction']}** | "
            f"`{record['D']['provenance_status']}` |",
            f"| `M` category | {m['tercile']}, percentile {m['percentile']} of "
            f"{m['n_units_at_this_level']} units, ranked on the **signed** change value "
            f"| `provisional_rule` PR-1 |",
            f"| `P` provenance | a status for every field above | see the record |",
            "",
            f"Chosen by: {record['chosen_by']}. No value was consulted in the choice.",
            "",
            "### Generated description",
            "",
        ]
        lines += [record["description"].rstrip(), ""]
        lines += [
            "### What it depends on",
            "",
            "Assumptions: " + ", ".join(f"`{item}`" for item in record["assumptions"]) + ".",
            "",
            f"PR-1 reference population: {m['reference_population']}.",
            "",
            "### Literature probe --- design stub, nothing sent",
            "",
            f"- Concept terms: {', '.join(probe['concept_terms'])}",
            "- Place terms: "
            + ", ".join(
                f"{term['term']} (`{term['from_column']}`, `{term['status']}`)"
                for term in probe["place_terms"]
            ),
            f"- Direction term: {probe['direction_term']}",
            "- Horizon terms: "
            + ", ".join(f"{term['term']} ({term['role']})" for term in probe["horizon_terms"]),
            "- Scenario terms: "
            + ", ".join(f"{term['term']} ({term['role']})" for term in probe["scenario_terms"]),
            f"- On the place terms: {probe['place_terms_note']}",
            f"- Generated query sentence: *{probe['query_sentence']}*",
            "",
            f"{probe['note']}",
            "",
            f"Full record: [`../artifacts/phenomena/prototypes/{record['record_id']}.json`]"
            f"(../artifacts/phenomena/prototypes/{record['record_id']}.json)",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--coverage", type=Path, default=COVERAGE_PATH)
    parser.add_argument("--inferred-candidates", type=Path, default=INFERRED_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    try:
        verified = verify_file(args.data, args.manifest)
    except (ManifestMismatchError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print(f"Manifest check OK: {args.data.name} sha256={verified['sha256']}")

    if not args.coverage.is_file():
        print(
            f"FAIL: coverage report not found: {args.coverage}\n"
            "Run scripts/dictionary_coverage.py first.",
            file=sys.stderr,
        )
        return 2
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    if coverage.get("data_sha256") != verified["sha256"]:
        print(
            "FAIL: the coverage report was built from different CSV bytes than the ones "
            f"just verified (coverage {coverage.get('data_sha256')}, "
            f"data {verified['sha256']}). Re-run scripts/dictionary_coverage.py.",
            file=sys.stderr,
        )
        return 2

    try:
        ic_records = load_inferred_candidates(
            args.inferred_candidates.read_text(encoding="utf-8")
        )
    except (InferredCandidateError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    inferred_by_index = {record["column_index"]: record for record in ic_records}
    semantics = build_semantics(coverage, inferred_by_index)
    semantics_by_index = {entry["index"]: entry for entry in semantics}

    try:
        first = find_anchors(args.data)
    except PhenomenonError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    anchors = first["anchors"]
    print(f"  rows                      : {first['n_rows']}")
    for oid, anchor in sorted(anchors.items(), key=lambda item: int(item[0])):
        print(
            f"    anchor OID_ {oid:<4}         : Crossmodel {anchor['Crossmodel']}, "
            f"State {anchor['State']!r}, NAME {anchor['NAME']!r}"
        )

    targets = {}
    for prototype in PROTOTYPES:
        anchor_row = anchors[prototype["anchor_oid"]]
        level = prototype["level"]
        if level == "cell":
            key = (anchor_row["Crossmodel"],)
        elif level == "county":
            key = (anchor_row["State"], anchor_row["NAME"])
        else:
            key = (anchor_row["State"],)
        targets[prototype["record_id"]] = {**prototype, "key": key}

    second = scan(args.data, targets)
    if second["n_rows"] != first["n_rows"]:
        print(
            f"FAIL: the two passes read different row counts ({first['n_rows']} then "
            f"{second['n_rows']}). Stop and report.",
            file=sys.stderr,
        )
        return 2
    dists, memberships = distributions(second["per_level"])
    for (level, variable_key), values in sorted(dists.items()):
        print(f"  distribution {level:<7} {variable_key:<40}: {len(values)} unit(s)")

    commit = git_commit()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    offences = []
    for prototype in PROTOTYPES:
        record_id = prototype["record_id"]
        target = targets[record_id]
        variable = variable_of(prototype["variable_key"])
        members = second["members"][record_id]
        ic_ids = sorted(
            {
                inferred_by_index[index]["id"]
                for index in columns_used(variable)
                if index in inferred_by_index
            }
        )
        try:
            record = build_record(
                record_id=record_id,
                level=prototype["level"],
                identifier=identifier_of(prototype["level"], target["key"]),
                members=members,
                variable=variable,
                semantics_by_index=semantics_by_index,
                sorted_change_values=dists[(prototype["level"], variable["key"])],
                distribution_membership=memberships[(prototype["level"], variable["key"])],
                built_from_commit=commit,
                csv_sha256=verified["sha256"],
                assumption_ids=assumptions_for(
                    level=prototype["level"], variable=variable, ic_ids=ic_ids
                ),
            )
        except PhenomenonError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 2
        record["chosen_by"] = prototype["chosen_by"]
        record["chosen_without_consulting_any_value"] = "yes"
        unlabelled = unlabelled_inferred_text(record)
        offences.extend((record_id, *item) for item in unlabelled)
        path = args.out_dir / f"{record_id}.json"
        path.write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        records.append(record)
        print(
            f"    {record_id:<12}: {record['G']['n_cells']} cell(s), change "
            f"{record['D']['change_value'][:14]}, {record['D']['direction']}, "
            f"{record['M']['tercile']} (percentile {record['M']['percentile'][:6]}) "
            f"-> {repo_relative(path)}"
        )

    for offence in offences:
        print(
            f"FAIL: inferred value shown unlabelled in {offence[0]} "
            f"(field {offence[1]}): {offence[2]!r}",
            file=sys.stderr,
        )

    PROTOTYPES_DOC.write_text(
        render_prototypes_doc(records, commit, verified["sha256"]), encoding="utf-8"
    )
    ASSUMPTIONS_DOC.write_text(render_assumptions_doc(records), encoding="utf-8")

    passed = not offences
    record_path = write_run_record(
        "build_phenomenon_prototypes",
        result_summary={
            "schema_version": SCHEMA_VERSION,
            "prototypes": [
                {
                    "record_id": record["record_id"],
                    "level": record["G"]["level"],
                    "identifier": record["G"]["identifier"],
                    "variable": record["H"]["variable_key"],
                    "n_cells": record["G"]["n_cells"],
                    "n_cells_with_value": record["G"]["n_cells_with_value"],
                    "change_value": record["D"]["change_value"],
                    "direction": record["D"]["direction"],
                    "percentile": record["M"]["percentile"],
                    "tercile": record["M"]["tercile"],
                    "assumptions": record["assumptions"],
                }
                for record in records
            ],
            "distribution_sizes": {
                f"{level}:{variable_key}": len(values)
                for (level, variable_key), values in sorted(dists.items())
            },
            "unlabelled_inferred_values": offences or "none",
        },
        passed=passed,
        data_path=args.data,
        data_sha256=verified["sha256"],
        output_path=args.out_dir,
        config_snapshot={
            "data_path": repo_relative(args.data),
            "coverage_path": repo_relative(args.coverage),
            "inferred_candidates_path": repo_relative(args.inferred_candidates),
            "out_dir": repo_relative(args.out_dir),
            "schema_version": SCHEMA_VERSION,
            "prototypes": [prototype["record_id"] for prototype in PROTOTYPES],
            "variables": [variable["key"] for variable in VARIABLES],
            "levels": list(LEVELS),
        },
    )
    print(f"Run record: {repo_relative(record_path)}")
    print(f"Wrote {repo_relative(PROTOTYPES_DOC)} and {repo_relative(ASSUMPTIONS_DOC)}")
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
