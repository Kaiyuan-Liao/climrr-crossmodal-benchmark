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

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

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
