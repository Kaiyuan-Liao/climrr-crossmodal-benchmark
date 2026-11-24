"""Grouping partitions for the LITCORPUS-03 impact arm (work package P5b, part B; D-075).

`artifacts/litgroups/partitions_infra_v1.jsonl` (tracked; read by `scripts/litcollect/litgroup_agent.py` v3.1 on Polaris)
over the **passing** (`deterministic_pass`) statements of infra run 1 (`artifacts/litstatements/infra_run1/
statements_ingested.jsonl`):

- **Impact partitions** = hazard family x asset class over the passing `impact` statements. Within a family, an asset
  class with fewer than `MIN_CLASS` (8) statements is merged into `other_assets` (the agent's own `other` class
  included); `prompt_variant: "impact_v1"` (the grouping agent's impact template). Partition id
  `infra_<family>.impact.<asset_partition>`, arm `infra_<family>__<asset_partition>` (so that group ids
  `LG-<arm>-impact-c<k>-<nnn>` name the family and the asset partition).
- **Driver / mechanism partitions** = family x statement type (`driver`, `mechanism`) over the passing driver and
  mechanism statements, "as before" (partitions v1: arm x statement type), with the v3 template (no `prompt_variant`).
  Partition id `infra_<family>.<type>`, arm `infra_<family>`. The family of such a statement is
  `statement_family` (`litstatements_infra1.statement_family`); a statement with no family is reported, not partitioned.

A partition over 120 statements would be split as in v1 (`litgroups.split_partition`; none is). The agent cuts each
partition into chunks of <= 40 (`--chunk-size 40`; `chunks_per_partition` here reproduces its rule). Each statement gets
an opaque local id (`S001`...) in statement-id order; the model sees ids and sentences only. `meta` (never sent) carries
paper, canonical paper (D-046 over the infra papers), evidence role, passage type, region class (geography v2), and for
impact statements `asset_class`, `hazard_relation`, `impact_mechanism`, `impact_outcome`, which the agent copies into the
group records.

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import math
from collections import Counter

from climrr import litgeo as lg
from climrr import litgroups as lgr
from climrr import litindependence as li
from climrr.paths import REPO_ROOT

VERSION = "litgroups partitions infra v1"
DECISION = "D-075"
MIN_CLASS = 8
CHUNK_SIZE = 40
OTHER = "other_assets"
IMPACT_VARIANT = "impact_v1"
FAMILIES = ("heat_index", "fire_weather_index")
DRIVER_TYPES = ("driver", "mechanism")
PARTITIONS_PATH = lgr.OUT_DIR / "partitions_infra_v1.jsonl"
SUMMARY_PATH = lgr.OUT_DIR / "partitions_infra_v1_summary.json"
#: The <family> slot of the grouping prompt (EXECUTOR wording, for confirmation): the broader hazards the infra statements
#: rest on, with the governed quantity named as one measure.
FAMILY_PHRASE = {"heat_index": "extreme heat and humid heat (of which the heat index is one measure)",
                 "fire_weather_index": "fire weather and fire danger (conditions that favour wildfire)"}


def asset_partitions(records: list[dict]) -> dict[str, dict[str, str]]:
    """{family: {asset_class: asset_partition}} --- a class with < MIN_CLASS passing impact statements -> `other_assets`."""
    out = {}
    for fam in FAMILIES:
        k = Counter(r["proposal"].get("asset_class") or "" for r in records
                    if r["impact_candidate"] and r["statement_family"] == fam)
        out[fam] = {c: (c if n >= MIN_CLASS and c not in ("other", "") else OTHER) for c, n in k.items()}
    return out


def n_chunks(n: int, chunk_size: int = CHUNK_SIZE) -> int:
    return max(1, math.ceil(n / chunk_size))


def _meta(r: dict, canon: dict, region_class: str) -> dict:
    m = {"statement_id": r["statement_id"], "paper_item_id": r["paper_item_id"],
         "canonical_paper": canon.get(r["paper_item_id"], r["paper_item_id"]), "evidence_role": r["evidence_role"],
         "passage_type": r["proposal"].get("passage_type"), "region_class": region_class}
    if r["proposal"]["statement_type"] == "impact":
        m.update(asset_class=r["proposal"].get("asset_class"), hazard_relation=r.get("hazard_relation"),
                 impact_mechanism=r["proposal"].get("impact_mechanism"), impact_outcome=r["proposal"].get("impact_outcome"))
    return m


def _partition(pid: str, arm: str, fam: str, stype: str, ids: list[str], by_id: dict, canon: dict, rc: dict,
               variant: str | None, asset_partition: str | None, labels: list[str], parent_n: int) -> dict:
    local = {sid: f"S{j:03d}" for j, sid in enumerate(ids, 1)}
    out = {"partition_id": pid, "version": VERSION, "decision": DECISION, "corpus": "LITCORPUS-03", "arm": arm,
           "hazard_family": fam, "family_phrase": FAMILY_PHRASE[fam], "statement_type": stype, "split_by": labels,
           "n_statements": len(ids), "parent_n_statements": parent_n,
           "statements": [{"local_id": local[s], "sentence": by_id[s]["proposal"]["statement"]} for s in ids],
           "meta": {local[s]: _meta(by_id[s], canon, rc[s]) for s in ids}}
    if variant:
        out.update(prompt_variant=variant, asset_partition=asset_partition,
                   asset_classes_in_partition=dict(sorted(Counter(by_id[s]["proposal"].get("asset_class") or "" for s in ids).items())))
    return out


def build_partitions(records: list[dict], indep: dict, gz: lg.Gazetteer) -> tuple[list[dict], dict]:
    """(partitions, report) from the ingested infra-run-1 records."""
    canon = li.canonical_map(indep)
    passing = [r for r in records if r["precheck_status"] == "pass"]
    by_id = {r["statement_id"]: r for r in passing}
    rc = {r["statement_id"]: lg.classify(r["proposal"].get("region"), r["proposal"].get("region_scope"), gz)["class"] for r in passing}
    amap = asset_partitions(passing)
    parts = []
    for fam in FAMILIES:
        imp = [r for r in passing if r["impact_candidate"] and r["statement_family"] == fam]
        for ap in sorted(set(amap[fam].values()), key=lambda a: (a == OTHER, a)):
            ids = sorted(r["statement_id"] for r in imp if amap[fam][r["proposal"].get("asset_class") or ""] == ap)
            for labels, part in lgr.split_partition(ids, {}, rc) if len(ids) > lgr.MAX_PARTITION else [([], ids)]:
                pid = ".".join([f"infra_{fam}", "impact", ap] + [lab.split("=", 1)[1] for lab in labels])
                parts.append(_partition(pid, f"infra_{fam}__{ap}", fam, "impact", part, by_id, canon, rc, IMPACT_VARIANT, ap, labels, len(ids)))
        for t in DRIVER_TYPES:
            ids = sorted(r["statement_id"] for r in passing if r["proposal"]["statement_type"] == t and r["statement_family"] == fam)
            if ids:
                parts.append(_partition(f"infra_{fam}.{t}", f"infra_{fam}", fam, t, ids, by_id, canon, rc, None, None, [], len(ids)))
    used = {m["statement_id"] for p in parts for m in p["meta"].values()}
    left = [r for r in passing if r["statement_id"] not in used]
    report = {
        "asset_partition_map": {f: dict(sorted(m.items())) for f, m in amap.items()},
        "merged_into_other_assets": {f: sorted(c for c, a in m.items() if a == OTHER) for f, m in amap.items()},
        "passing_not_partitioned": dict(sorted(Counter(f"{r['proposal']['statement_type']}|{r['statement_family']}" for r in left).items())),
        "passing_not_partitioned_ids": sorted(r["statement_id"] for r in left),
    }
    return parts, report


def summarise(parts: list[dict], report: dict) -> dict:
    return {"version": VERSION, "decision": DECISION, "min_class": MIN_CLASS, "chunk_size": CHUNK_SIZE,
            "partitions": len(parts), "statements": sum(p["n_statements"] for p in parts),
            "chunks": sum(n_chunks(p["n_statements"]) for p in parts),
            "chunks_per_partition": {p["partition_id"]: n_chunks(p["n_statements"]) for p in parts},
            "sizes": {p["partition_id"]: p["n_statements"] for p in parts},
            "impact_partitions": sum(p.get("prompt_variant") == IMPACT_VARIANT for p in parts),
            "impact_statements": sum(p["n_statements"] for p in parts if p.get("prompt_variant") == IMPACT_VARIANT),
            "by_role": dict(sorted(Counter(m["evidence_role"] for p in parts for m in p["meta"].values()).items())),
            "by_region_class": dict(sorted(Counter(m["region_class"] for p in parts for m in p["meta"].values()).items())),
            "family_phrase": FAMILY_PHRASE, **report}
