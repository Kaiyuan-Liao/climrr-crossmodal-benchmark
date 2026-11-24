"""COORDINATOR dispositions of the infra impact groups (work package P5c hotfix; D-078). No model call.

Input: `data/metadata/benchmark/group_dispositions_infra_v1.csv` (COORDINATOR 2026-11-24, confirmed by Kaiyuan; byte-identical
copy of the file as received, CRLF, pinned by SHA-256 here and in `data/manifest.json`): one row per record of the P5c review
list (`artifacts/benchmark/review/P5_impact_groups_review_v1.csv`, 103 records tagged hazard_impact_on_asset or
impact_or_exposure), columns `group_id, kind, family, asset_class, claim_about, evidence_strength, label_or_statement,
coordinator_disposition, asset_class_override, reason, kaiyuan_disposition, kaiyuan_note`.

**Vocabulary** (the work package's): `accept`; `accept_two_hop` (usable only with the D-073c two-hop wording);
`relabel:<claim_about>`; `merge_with:<group_id>`; `not_about_family`; `reject`; `keep_excluded` (an impact_or_exposure tag
confirmed: stays out of packets). `asset_class_override`, where filled, reassigns the record's asset class (rail / runway ->
transportation; building groups -> commercial facilities; `other_assets` members to their class). `kaiyuan_disposition`,
where filled, overrides the COORDINATOR's (all 103 are empty in v1). A group of the infra grouping run that has no row (its
claim tag is neither of the two) is excluded with `no_disposition`, as before (D-053a).

**Applied** (`apply`) to the grouping run's records (`artifacts/litgroups/infra_run1/groups.jsonl`), each output record = the
run record + `disposition`, `disposition_source`, `disposition_exclude` (the reason, or absent when usable), `two_hop`,
`asset_class_override`:

- `accept` / `accept_two_hop`: usable as an impact group (the record must be `claim_about` hazard_impact_on_asset);
  `two_hop: true` for the second.
- `relabel:hazard_impact_on_asset`: `claim_about` set to it (the run tag kept as `claim_about_run`); a record of another
  statement type (the driver-partition groups the COORDINATOR relabelled) becomes `statement_type: impact` (the run's type
  kept as `statement_type_run`; EXECUTOR reading of a relabel into the impact claim, for confirmation).
  `relabel:impact_or_exposure`: `claim_about` set to it and the record kept out (`disposition_exclude:
  relabel:impact_or_exposure`; an impact_or_exposure tag stays out of packets, as `keep_excluded` says).
- `merge_with:<G>`: the record's members are appended to G's (`merged_from` on G; the record itself excluded
  `merged_into:<G>`). Strengths are recomputed from the members where the seeds read them (`seeds_infra.impact_group_view`).
- `not_about_family`, `reject`, `keep_excluded`: excluded with that reason.

The agent's label and members are never edited otherwise. The asset class of a usable record is the override where filled,
else its members' classes (as before).
"""

from __future__ import annotations

import copy
import csv
import io
from collections import Counter
from pathlib import Path

import yaml

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

VERSION = "dispositions_infra v1"
DECISION = "D-078"
PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "group_dispositions_infra_v1.csv"
SHA256 = "9b94e028bc571d9d84e6714ef1264bf2e087ea405d6561bfcdbd6d333c601bef"
COLUMNS = ("group_id", "kind", "family", "asset_class", "claim_about", "evidence_strength", "label_or_statement",
           "coordinator_disposition", "asset_class_override", "reason", "kaiyuan_disposition", "kaiyuan_note")
N_ROWS = 103
IMPACT_CLAIM = "hazard_impact_on_asset"
EXPOSURE_CLAIM = "impact_or_exposure"
PLAIN = ("accept", "accept_two_hop", "not_about_family", "reject", "keep_excluded")
RELABEL_TARGETS = (IMPACT_CLAIM, EXPOSURE_CLAIM)
USABLE = ("accept", "accept_two_hop", f"relabel:{IMPACT_CLAIM}")
#: The agent's catch-all class (the grouping partitions' `other`), allowed in an override besides the lexicon classes.
OTHER_CLASS = "other"
NO_DISPOSITION = "no_disposition"


def lexicon_classes() -> list[str]:
    d = yaml.safe_load((REPO_ROOT / "data" / "metadata" / "litstatements" / "infrastructure_lexicon_v1.yaml").read_text(encoding="utf-8"))
    return [a["id"] for a in d["asset_classes"]]


def effective(row: dict) -> tuple[str, str]:
    """(disposition, source): Kaiyuan's where filled, else the COORDINATOR's."""
    k = (row.get("kaiyuan_disposition") or "").strip()
    return (k, "kaiyuan") if k else ((row.get("coordinator_disposition") or "").strip(), "coordinator")


def kind_of(disposition: str) -> str:
    return disposition.split(":", 1)[0]


def load(path: Path = PATH, check_sha: bool = True) -> list[dict]:
    """The disposition rows, validated (columns, row count, vocabulary, merge targets, override classes)."""
    if check_sha and sha256_file(path) != SHA256:
        raise ValueError(f"{path.name} differs from its pinned SHA-256 {SHA256}")
    text = Path(path).read_text(encoding="utf-8")
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    if not rows or tuple(rows[0].keys()) != COLUMNS:
        raise ValueError(f"{path.name}: columns must be {COLUMNS}")
    if len(rows) != N_ROWS:
        raise ValueError(f"{path.name}: {len(rows)} rows, expected {N_ROWS}")
    ids = [r["group_id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{path.name}: duplicate group ids")
    classes = set(lexicon_classes()) | {OTHER_CLASS}
    for r in rows:
        d, _ = effective(r)
        if not d:
            raise ValueError(f"{r['group_id']}: no disposition")
        if d.startswith("relabel:"):
            if d.split(":", 1)[1] not in RELABEL_TARGETS:
                raise ValueError(f"{r['group_id']}: relabel target {d!r} not in {RELABEL_TARGETS}")
        elif d.startswith("merge_with:"):
            if d.split(":", 1)[1] not in ids:
                raise ValueError(f"{r['group_id']}: merge target {d!r} is not a reviewed record")
        elif d not in PLAIN:
            raise ValueError(f"{r['group_id']}: disposition {d!r} not in the vocabulary")
        o = (r["asset_class_override"] or "").strip()
        if o and o not in classes:
            raise ValueError(f"{r['group_id']}: asset_class_override {o!r} is not a lexicon class")
    return rows


def apply(groups: list[dict], rows: list[dict]) -> tuple[list[dict], dict]:
    """(the run records with the dispositions applied, a log of the counts). See the module docstring."""
    by_row = {r["group_id"]: r for r in rows}
    known = {g["group_id"] for g in groups}
    missing = sorted(set(by_row) - known)
    if missing:
        raise ValueError(f"dispositions name records not in the grouping run: {missing}")
    out = {g["group_id"]: copy.deepcopy(g) for g in groups}
    merges = []
    for gid, g in out.items():
        r = by_row.get(gid)
        if r is None:
            g.update({"disposition": None, "disposition_source": None, "disposition_exclude": NO_DISPOSITION, "two_hop": False,
                      "asset_class_override": None})
            continue
        d, src = effective(r)
        k = kind_of(d)
        o = (r["asset_class_override"] or "").strip() or None
        g.update({"disposition": d, "disposition_source": src, "two_hop": d == "accept_two_hop", "asset_class_override": o,
                  "disposition_reason": r["reason"]})
        if k in ("accept", "accept_two_hop"):
            if g.get("claim_about") != IMPACT_CLAIM:
                raise ValueError(f"{gid}: {d} on a record tagged {g.get('claim_about')!r}")
        elif k == "relabel":
            target = d.split(":", 1)[1]
            g["claim_about_run"], g["claim_about"] = g.get("claim_about"), target
            if target == IMPACT_CLAIM and g.get("statement_type") != "impact":
                g["statement_type_run"], g["statement_type"] = g.get("statement_type"), "impact"
            if target == EXPOSURE_CLAIM:
                g["disposition_exclude"] = d
        elif k == "merge_with":
            merges.append((gid, d.split(":", 1)[1]))
            g["disposition_exclude"] = f"merged_into:{d.split(':', 1)[1]}"
        else:
            g["disposition_exclude"] = k
    for src_id, dst_id in merges:
        dst = out[dst_id]
        if dst.get("disposition_exclude"):
            raise ValueError(f"{src_id}: merge target {dst_id} is itself excluded ({dst['disposition_exclude']})")
        dst["member_ids"] = list(dict.fromkeys(list(dst["member_ids"]) + list(out[src_id]["member_ids"])))
        dst.setdefault("merged_from", []).append(src_id)
    recs = [out[g["group_id"]] for g in groups]
    log = {"version": VERSION, "decision": DECISION, "file": {"path": "data/metadata/benchmark/group_dispositions_infra_v1.csv",
                                                             "sha256": SHA256, "rows": len(rows)},
           "by_disposition": dict(sorted(Counter(kind_of(effective(r)[0]) for r in rows).items())),
           "by_disposition_full": dict(sorted(Counter(effective(r)[0] for r in rows).items())),
           "by_source": dict(sorted(Counter(effective(r)[1] for r in rows).items())),
           "asset_class_overrides": {r["group_id"]: r["asset_class_override"] for r in rows if (r["asset_class_override"] or "").strip()},
           "merges": [{"from": a, "into": b} for a, b in merges],
           "statement_type_relabelled": {g["group_id"]: g["statement_type_run"] for g in recs if "statement_type_run" in g},
           "records": len(recs), "no_disposition": sum(g.get("disposition_exclude") == NO_DISPOSITION for g in recs),
           "usable": sum(not g.get("disposition_exclude") for g in recs),
           "usable_two_hop": sum(not g.get("disposition_exclude") and g["two_hop"] for g in recs),
           "excluded_by_reason": dict(sorted(Counter(str(g["disposition_exclude"]) for g in recs if g.get("disposition_exclude")).items()))}
    return recs, log
