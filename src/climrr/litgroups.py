"""Inputs to the grouping agent and the reading of its output (pilot P2b-prep; D-048).

**Partitions** (`artifacts/litgroups/partitions_v1.jsonl`, tracked): arm x statement_type
over the core / cited / background_consensus candidates of run 2. A partition over
`MAX_PARTITION` (120) statements is split, deterministically, by lexical direction
(DR-LIT-AGG-1 v2 step 1), then a part still over the limit by region class (`litgeo`), then
a part still over it into consecutive equal chunks in statement-id order; the split is
recorded (`split_by`). Within a partition each statement gets an opaque local id
(`S001`...) in statement-id order: statement ids `LS-<item_id>-<nn>` carry the paper id, and
the agent sends the model **ids and sentences only** --- no passage, no paper id, no table.
What the agent needs to compute evidence strength (paper, canonical paper under D-046,
evidence role, passage type) travels beside the sentences in `meta` and is never sent.

`litgroup_agent.py` reads this file on Polaris; its `groups.jsonl` is read back here by
`read_groups` for the synthesis packets.

**Dispositions** (D-053): `data/metadata/benchmark/group_dispositions_v1.csv` (manifest-pinned) holds one row per
reviewed group --- `accept`, `relabel:<claim_about>`, `not_about_family`, `reject`, `merge_with:<group_id>`,
`exclude_from_rung7`; Kaiyuan's column overrides the proposal where filled. `apply_dispositions` applies them when the
packets are built; the groups file itself is immutable evidence. A group not in the file is unchanged.

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path

from climrr import litaggregate as la
from climrr import litgeo as lg
from climrr import litindependence as li
from climrr.paths import REPO_ROOT

VERSION = "litgroups partitions v1"
MAX_PARTITION = 120
OUT_DIR = REPO_ROOT / "artifacts" / "litgroups"
PARTITIONS_PATH = OUT_DIR / "partitions_v1.jsonl"
PARTITIONS_SUMMARY_PATH = OUT_DIR / "partitions_v1_summary.json"
FAMILY_PHRASE = {"extreme_heat_v1": "the heat index and humid heat",
                 "fire_weather_v1": "fire weather and fire danger indices"}


def _split(ids: list[str], key, label: str) -> list[tuple[str, list[str]]]:
    parts: dict[str, list[str]] = {}
    for i in ids:
        parts.setdefault(key(i), []).append(i)
    return [(f"{label}={k}", sorted(v)) for k, v in sorted(parts.items())]


def _chunks(ids: list[str]) -> list[tuple[str, list[str]]]:
    n = math.ceil(len(ids) / MAX_PARTITION)
    size = math.ceil(len(ids) / n)
    return [(f"chunk={j + 1}of{n}", ids[j * size:(j + 1) * size]) for j in range(n)]


def split_partition(ids: list[str], direction: dict, region_class: dict) -> list[tuple[list[str], list[str]]]:
    """[(split labels applied, ids)] --- direction, then region class, then chunks, each only where still over the limit."""
    out = []
    stack = [([], sorted(ids), 0)]
    while stack:
        labels, part, level = stack.pop(0)
        if len(part) <= MAX_PARTITION:
            out.append((labels, part))
            continue
        if level == 0:
            subs = _split(part, direction.get, "direction")
        elif level == 1:
            subs = _split(part, region_class.get, "region_class")
        else:
            subs = _chunks(part)
        stack[0:0] = [(labels + [lab], sub, level + 1) for lab, sub in subs]
    return out


def build_partitions(records: list[dict], indep: dict, gz: lg.Gazetteer) -> list[dict]:
    p = la.Prepared(records)
    canon = li.canonical_map(indep)
    region_class = {r["statement_id"]: lg.classify(r["proposal"].get("region"), r["proposal"].get("region_scope"), gz)["class"]
                    for r in p.ent}
    out = []
    for arm in la.ARMS:
        for t in la.STATEMENT_TYPES:
            ids = sorted(r["statement_id"] for r in p.ent if r["arm"] == arm and r["proposal"]["statement_type"] == t)
            if not ids:
                continue
            for labels, part in split_partition(ids, p.direction, region_class):
                pid = ".".join([arm, t] + [lab.split("=", 1)[1] for lab in labels])
                local = {sid: f"S{j:03d}" for j, sid in enumerate(part, 1)}
                out.append({
                    "partition_id": pid, "version": VERSION, "arm": arm, "family_phrase": FAMILY_PHRASE[arm],
                    "statement_type": t, "split_by": labels, "n_statements": len(part), "parent_n_statements": len(ids),
                    "statements": [{"local_id": local[sid], "sentence": p.by_id[sid]["proposal"]["statement"]} for sid in part],
                    "meta": {local[sid]: {"statement_id": sid, "paper_item_id": p.by_id[sid]["paper_item_id"],
                                          "canonical_paper": canon.get(p.by_id[sid]["paper_item_id"], p.by_id[sid]["paper_item_id"]),
                                          "evidence_role": p.by_id[sid]["evidence_role"],
                                          "passage_type": p.by_id[sid]["proposal"].get("passage_type"),
                                          "direction": p.direction[sid], "region_class": region_class[sid]} for sid in part},
                })
    return out


def summarise_partitions(parts: list[dict]) -> dict:
    return {"version": VERSION, "max_partition": MAX_PARTITION, "partitions": len(parts),
            "statements": sum(x["n_statements"] for x in parts),
            "split": [{"partition_id": x["partition_id"], "split_by": x["split_by"], "n_statements": x["n_statements"],
                       "parent_n_statements": x["parent_n_statements"]} for x in parts if x["split_by"]],
            "sizes": {x["partition_id"]: x["n_statements"] for x in parts},
            "by_role": dict(sorted(Counter(m["evidence_role"] for x in parts for m in x["meta"].values()).items()))}


def read_groups(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]


# --- group dispositions (pilot P2b-final-prep; D-053) ---------------------------------------------

DISPOSITIONS_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "group_dispositions_v1.csv"
DISPOSITIONS_VERSION = "group_dispositions_v1"
DISPOSITION_KINDS = ("accept", "relabel", "not_about_family", "reject", "merge_with", "exclude_from_rung7")
EXCLUDING = ("not_about_family", "reject")
CLAIM_ABOUT = ("hazard_change_mechanism", "hazard_definition_or_measurement", "impact_or_exposure", "method_or_data", "other")


def parse_disposition(s: str) -> tuple[str, str | None]:
    """'accept' -> ('accept', None); 'relabel:<claim_about>' / 'merge_with:<group_id>' -> (kind, argument)."""
    kind, _, arg = s.strip().partition(":")
    if kind not in DISPOSITION_KINDS or bool(arg) != (kind in ("relabel", "merge_with")):
        raise ValueError(f"unknown disposition {s!r}")
    if kind == "relabel" and arg not in CLAIM_ABOUT:
        raise ValueError(f"relabel to a claim_about outside the enum: {arg!r}")
    return kind, arg or None


def load_dispositions(path: Path = DISPOSITIONS_PATH, manifest_path: Path | None = None) -> dict:
    """{group_id: {disposition, kind, arg, source, reason}} from the manifest-pinned file. Kaiyuan's column overrides the
    proposal where filled (D-053)."""
    from climrr.checksums import sha256_file
    from climrr.manifest import MANIFEST_PATH, load_entry
    path = Path(path)
    pin = load_entry(path.name, manifest_path or MANIFEST_PATH)["sha256"]
    if sha256_file(path) != pin:
        raise ValueError(f"{path.name} differs from its manifest pin {pin}")
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            own = (r.get("kaiyuan_disposition") or "").strip()
            d = own or r["proposed_disposition"].strip()
            kind, arg = parse_disposition(d)
            if r["group_id"] in out:
                raise ValueError(f"{r['group_id']} listed twice")
            out[r["group_id"]] = {"disposition": d, "kind": kind, "arg": arg, "source": "kaiyuan" if own else "proposed",
                                  "reason": r.get("kaiyuan_note") if own else r.get("reason")}
    return out


def apply_dispositions(groups: list[dict], disp: dict) -> list[dict]:
    """The groups with the dispositions applied (D-053); the input records are not changed. Every record gains
    `disposition` (None when the group is not in the file), `claim_about_source` (`agent` | `reviewer`),
    `disposition_exclude` (None | `disposition:not_about_family` | `disposition:reject` | `merged_into:<group_id>`) and
    `exclude_from_rung7`. A `merge_with` target gains the source's members (union, in order), `merged_from`, and its
    strength and paper counts recomputed under D-045 / D-046 (`evidence_strength_before_merge` kept)."""
    by_id = {g["group_id"]: g for g in groups}
    unknown = sorted(set(disp) - set(by_id))
    if unknown:
        raise ValueError(f"dispositions name groups not in the grouping output: {unknown}")
    out = {}
    for g in groups:
        d = disp.get(g["group_id"])
        x = dict(g, disposition=d["disposition"] if d else None, claim_about_source="agent", disposition_exclude=None,
                 exclude_from_rung7=bool(d and d["kind"] == "exclude_from_rung7"))
        if d and d["kind"] == "relabel":
            x.update(claim_about=d["arg"], claim_about_agent=g.get("claim_about"), claim_about_source="reviewer")
        if d and d["kind"] in EXCLUDING:
            x["disposition_exclude"] = f"disposition:{d['kind']}"
        out[g["group_id"]] = x
    for gid, d in sorted(disp.items()):
        if d["kind"] != "merge_with":
            continue
        tgt, src = d["arg"], out[gid]
        if tgt not in out or out[tgt]["arm"] != src["arm"] or tgt == gid:
            raise ValueError(f"{gid}: merge target {tgt} is not another group of the same arm")
        if disp.get(tgt, {}).get("kind") in EXCLUDING + ("merge_with",):
            raise ValueError(f"{gid}: merge target {tgt} is itself excluded or merged")
        t = out[tgt]
        seen = set(t["member_ids"])
        t["member_ids"] = list(t["member_ids"]) + [m for m in src["member_ids"] if m not in seen]
        if "members" in t:
            t["members"] = list(t["members"]) + [m for m in src.get("members", []) if m["statement_id"] not in seen]
        t["merged_from"] = t.get("merged_from", []) + [gid]
        src["disposition_exclude"] = f"merged_into:{tgt}"
    for t in out.values():
        if t.get("merged_from") and "members" in t:
            ms = t["members"]
            cc = {m["canonical_paper"] for m in ms if m["evidence_role"] in la.CORE_OR_CITED}
            t.update(evidence_strength_before_merge=t["evidence_strength"], n_members=len(t["member_ids"]),
                     evidence_strength=li.strength_v2([{"evidence_role": m["evidence_role"], "paper_item_id": m["canonical_paper"],
                                                        "passage_type": m["passage_type"]} for m in ms], {}),
                     papers=sorted({m["paper_item_id"] for m in ms}), n_papers=len({m["paper_item_id"] for m in ms}),
                     canonical_papers=sorted({m["canonical_paper"] for m in ms}),
                     n_independent_papers=len({m["canonical_paper"] for m in ms}), n_independent_core_cited_papers=len(cc))
        elif t.get("merged_from"):
            t["n_members"] = len(t["member_ids"])
    return [out[g["group_id"]] for g in groups]


def disposition_counts(disp: dict) -> dict:
    return dict(sorted(Counter(d["disposition"] for d in disp.values()).items()))
