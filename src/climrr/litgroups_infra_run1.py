"""Infra grouping run 1: verification, ingest and enrichment (work package P5c, part A; D-076).

Run: `litgroup_agent.py` v3.1 on Polaris (Sophia vLLM, `openai/gpt-oss-120b`, reasoning low, max_tokens 16000, chunk 40)
over the tracked `partitions_infra_v1.jsonl` at source commit `7699412`: 11 partitions in 12 chunks (8 impact chunks with
the impact template `70018280…3925`, 4 driver / mechanism chunks with the v3 template). Delivered as
`litgroups_infra_run1_evidence.tar.gz`. `verify_source` re-derives every fact the work package states (hashes, agent and
template SHA-256, budget, chunks, corrective turns, groups / singletons, strengths, claim tags, each of the 198 statements
exactly once, endpoint, source commit, the log) and raises on any difference. `copy_run` copies `groups.jsonl`,
`summary.json`, `agent.log` and every chunk's `result.json` (as `chunks/<chunk_id>.json`) into
`artifacts/litgroups/infra_run1/`; prompts and raw responses are recorded by SHA-256 in `manifest.json` only.

`enrich` gives every group record (a singleton becomes a one-member group, `is_singleton: true`) as for grouping run 2
(`litgroups_run2.enrich`), over the infra statements:

- members resolved through the partition's local ids to `LS3-` ids with paper and canonical paper (D-046 over the 572
  infra papers, `artifacts/litstatements/infra_run1/independence_v2.json`), evidence role, passage type, region and its
  geography-v2 class (`litgeo` v2) and the states it names, statement family, and for impact statements `asset_class`,
  `hazard_relation`, `impact_mechanism`, `impact_outcome` read from the member statement (and checked against the lists
  the agent copied from the partition's `meta`);
- `n_papers`, `n_independent_papers`, the D-045 / D-048 `evidence_strength` recomputed under D-046 and checked against the
  agent's; the agent's `claim_about` (never inferred here);
- `family` (the partition's hazard family), `asset_partition` (the partition's), `asset_class_counts` (the members'
  classes), `region_classes` / `region_class_counts`, `place_named_states` (the states named by members of geography-v2
  class state) and `has_place_named_member` (D-075 (e): a member of class state), `has_us_place_member` (a member of class
  state, nca, us_subregion or us_national).

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from climrr import litaggregate as la
from climrr import litgeo as lg
from climrr import litgroups as lgr
from climrr import litgroups_infra as lgi
from climrr import litgroups_run2 as g2
from climrr import litindependence as li
from climrr import litstatements_infra1 as ir
from climrr import litstatements_run2 as r2
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

RUN_ID = "litgroups_infra_run1"
DECISION = "D-076"
ART = lgr.OUT_DIR / "infra_run1"
CHUNKS_DIR = ART / "chunks"
MANIFEST_PATH = ART / "manifest.json"
ENRICHED_PATH = ART / "groups_enriched.jsonl"
ENRICHED_SUMMARY_PATH = ART / "groups_enriched_summary.json"

TARBALL_NAME = "litgroups_infra_run1_evidence.tar.gz"
TARBALL_SHA256 = "14797dc7f804f4dbba4d7f6fc6e904765bbd87948a9c131abd4f003a07319f65"
GROUPS_SHA256 = "f61bf4f557c0f5fbdfec2779fc578b01e84bdc6edfca80c4b633d25f841045ce"
SUMMARY_SHA256 = "81d7f2b044b0256e47d1aac7ebff7cbce4664d8c9cee6ac214d6861647fbf005"
AGENT_REL = g2.AGENT_REL
AGENT_SHA256 = "9c4633692c3ae92b4a51cf96ee0bb540282a33c89cac8c52e941658ec2ea1c8f"            # v3.1 (P5b)
TEMPLATE_SHA256 = g2.TEMPLATE_SHA256                                                          # v3 template (driver / mechanism)
TEMPLATE_IMPACT_SHA256 = "70018280938b269fe854de6baca520bb2b84429a66ea0d7ac58520acec353925"
CORRECTIVE_SHA256 = g2.CORRECTIVE_SHA256
SOURCE_COMMIT = "76994126a1834984a3dd23fc4cab0cfe350d7142"
GENERATOR_VERSION = "litgroup_agent v3.1"
ENDPOINT_LABEL, MODEL, BASE_URL = g2.ENDPOINT_LABEL, g2.MODEL, g2.BASE_URL
ENDPOINT = f"{ENDPOINT_LABEL} {MODEL}"
BUDGET = dict(g2.BUDGET)
RUN_FACTS = {"partitions": 11, "chunks": 12, "chunks_pass": 12, "chunks_fail": 0, "corrective_retry_used": 4,
             "groups": 84, "singletons": 59, "statements": 198}
BY_STRENGTH = {"multi_source_supported": 20, "review_supported": 2, "single_source_supported": 121, "background_only": 0}
GROUPS_BY_CLAIM = {"hazard_impact_on_asset": 59, "hazard_change_mechanism": 8, "hazard_definition_or_measurement": 1,
                   "impact_or_exposure": 13, "method_or_data": 3, "other": 0}
PROMPT_VARIANTS = {"v3": 4, "impact_v1": 8}
EXCLUDED_NAMES = g2.EXCLUDED_NAMES
COPIED = {"litgroups/infra_run1/groups.jsonl": "groups.jsonl",
          "litgroups/infra_run1/summary.json": "summary.json",
          "litgroups/infra_run1/agent.log": "agent.log"}
US_PLACE_CLASSES = ("state", "nca", "us_subregion", "us_national")
REVIEW_CLAIMS = ("hazard_impact_on_asset", "impact_or_exposure")


def _run(src: Path) -> Path:
    return Path(src) / "litgroups" / "infra_run1"


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _load(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _without_id(g: dict) -> dict:
    return {k: v for k, v in g.items() if k != "group_id"}


def verify_source(src: Path, partitions: list[dict] | None = None) -> dict:
    """Every fact the work package states, re-derived from the delivered files. Raises on any difference."""
    src, run = Path(src), _run(src)
    _check(sha256_file(run / "groups.jsonl") == GROUPS_SHA256, "groups.jsonl differs from its stated SHA-256")
    _check(sha256_file(run / "summary.json") == SUMMARY_SHA256, "summary.json differs from its stated SHA-256")
    _check(g2.agent_sha_at(SOURCE_COMMIT) == AGENT_SHA256, f"{AGENT_REL} at the source commit differs from v3.1 {AGENT_SHA256}")
    s = _load(run / "summary.json")
    for k, v in (("generator_version", GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL),
                 ("base_url", BASE_URL), ("reasoning_effort", BUDGET["reasoning_effort"]), ("max_tokens", BUDGET["max_tokens"]),
                 ("chunk_size", BUDGET["chunk_size"]), ("partitions_in_file", RUN_FACTS["partitions"]),
                 ("chunks_in_file", RUN_FACTS["chunks"]), ("chunks_done", RUN_FACTS["chunks"]),
                 ("chunks_pass", RUN_FACTS["chunks_pass"]), ("corrective_retry_used", RUN_FACTS["corrective_retry_used"]),
                 ("corrective_retry_pass", RUN_FACTS["corrective_retry_used"]), ("groups", RUN_FACTS["groups"]),
                 ("singletons", RUN_FACTS["singletons"]), ("statements_grouped", RUN_FACTS["statements"]),
                 ("groups_label_fail", 0), ("claim_about_fail", 0), ("reasoning_effort_not_applied", 0),
                 ("by_strength", BY_STRENGTH), ("groups_by_claim_about", GROUPS_BY_CLAIM), ("prompt_variants", PROMPT_VARIANTS),
                 ("system_prompt_template_sha256", TEMPLATE_SHA256), ("system_prompt_template_impact_sha256", TEMPLATE_IMPACT_SHA256),
                 ("corrective_template_sha256", CORRECTIVE_SHA256)):
        _check(s.get(k) == v, f"summary {k} = {s.get(k)!r}, expected {v!r}")
    _check(s["chunks_fail"] == [], f"summary chunks_fail = {s['chunks_fail']}")
    _check(s["endpoints_in_results"] == {f"{ENDPOINT} {BASE_URL}": RUN_FACTS["chunks"]}, "endpoints_in_results differs")

    chunk_ids = g2.expected_chunk_ids(s)
    dirs = sorted(p.name for p in run.iterdir() if p.is_dir())
    _check(sorted(chunk_ids) == dirs, f"chunk dirs {dirs} != expected {sorted(chunk_ids)}")
    _check(not list(run.glob("*/result.failed_attempt*.json")), "a failed first attempt is present; the work package states none")
    results = {c: _load(run / c / "result.json") for c in chunk_ids}
    for c, r in results.items():
        _check(r["chunk_id"] == c and r["status"] == "deterministic_pass", f"{c}: status {r['status']}")
        impact = r.get("prompt_variant") == lgi.IMPACT_VARIANT
        for k, v in (("generator_version", GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL),
                     ("base_url", BASE_URL), ("source_commit", SOURCE_COMMIT), ("reasoning_effort_applied", True),
                     ("finish_reason", "stop"), ("corrective_template_sha256", CORRECTIVE_SHA256),
                     ("system_prompt_template_sha256", TEMPLATE_IMPACT_SHA256 if impact else TEMPLATE_SHA256), *BUDGET.items()):
            _check(r.get(k) == v, f"{c}: {k} = {r.get(k)!r}, expected {v!r}")
    corrective = sorted(c for c, r in results.items() if r["corrective_retry_used"])
    _check(len(corrective) == RUN_FACTS["corrective_retry_used"], f"{len(corrective)} chunks used the corrective turn")
    variants = Counter("impact_v1" if r.get("prompt_variant") == lgi.IMPACT_VARIANT else "v3" for r in results.values())
    _check(dict(variants) == PROMPT_VARIANTS, f"prompt variants {dict(variants)}")

    groups = lgr.read_groups(run / "groups.jsonl")
    rederived = [_without_id(g) for c in chunk_ids for g in results[c]["groups"]]
    _check([_without_id(g) for g in groups] == rederived, "groups.jsonl is not the chunks' records in chunk order")
    for g in groups:
        k = results[g["chunk_id"]]["chunk_index"]
        _check(g["group_id"].startswith(f"LG-{g['arm']}-{g['statement_type']}-c{k}-"), f"{g['group_id']}: id not of its chunk")
    _check(len({g["group_id"] for g in groups}) == len(groups), "duplicate group ids")
    kinds = Counter(g["kind"] for g in groups)
    _check(kinds == {"group": RUN_FACTS["groups"], "singleton": RUN_FACTS["singletons"]}, f"kinds {dict(kinds)}")
    _check(dict(Counter(g["evidence_strength"] for g in groups)) == {k: v for k, v in BY_STRENGTH.items() if v},
           "strengths differ from the stated ones")
    gc = Counter(g["claim_about"] for g in groups if g["kind"] == "group")
    _check({k: gc.get(k, 0) for k in GROUPS_BY_CLAIM} == GROUPS_BY_CLAIM, f"group claim tags {dict(gc)}")
    members = [m for g in groups for m in g["member_ids"]]
    _check(len(members) == len(set(members)) == RUN_FACTS["statements"], f"{len(members)} member slots, {len(set(members))} distinct")
    _check(all(g["endpoint_label"] == ENDPOINT_LABEL and g["model"] == MODEL for g in groups), "a group record names another endpoint")
    if partitions is not None:
        part_ids = {m["statement_id"] for p in partitions for m in p["meta"].values()}
        _check(set(members) == part_ids, "grouped statements differ from the partitions' statements")

    pl = g2.parse_log((run / "agent.log").read_text(encoding="utf-8"))
    _check(pl["invocations"] == 1, f"{pl['invocations']} START lines")
    last = pl["done"][-1]
    _check((last["chunks"], last["pass"], last["fail"], last["corrective"], last["groups"], last["singletons"]) ==
           ("12", "12", "0", "4", "84", "59"), f"last DONE line {last}")
    _check(pl["corrective_lines"] == RUN_FACTS["corrective_retry_used"], f"{pl['corrective_lines']} CORRECTIVE lines")
    st = pl["starts"][0]
    _check(sha256_file(lgi.PARTITIONS_PATH).startswith(st["partitions_sha"]), "partitions_infra_v1.jsonl differs from the run's")
    _check(TEMPLATE_IMPACT_SHA256.startswith(st["template_impact_sha"]), "START template_impact_sha differs")
    return {"summary": s, "chunk_ids": chunk_ids, "corrective_chunks": corrective,
            "log": {k: pl[k] for k in ("invocations", "start_utc", "end_utc", "corrective_lines")} | {"done_lines": pl["done"]}}


# --- copy ---------------------------------------------------------------------------------------


def copy_run(src: Path) -> int:
    src, n = Path(src), 0
    for rel, name in COPIED.items():
        n += r2._copy(src / rel, ART / name)
    for p in sorted(_run(src).glob("*/result.json")):
        n += r2._copy(p, CHUNKS_DIR / f"{p.parent.name}.json")
    return n


def excluded_files(src: Path) -> list[dict]:
    return [{"path": f"litgroups/infra_run1/{p.parent.name}/{p.name}", "sha256": sha256_file(p), "bytes": p.stat().st_size}
            for p in sorted(_run(src).glob("*/*")) if p.name in EXCLUDED_NAMES]


# --- enrichment ---------------------------------------------------------------------------------


def enrich(groups: list[dict], partitions: list[dict], records: list[dict], indep: dict, gz: lg.Gazetteer) -> list[dict]:
    """The enriched record of every group and singleton (module docstring); raises if a recomputation differs."""
    canon = li.canonical_map(indep)
    by_id = {r["statement_id"]: r for r in records}
    parts = {p["partition_id"]: p for p in partitions}
    out = []
    for g in groups:
        part = parts[g["partition_id"]]
        pm = part["meta"]
        resolved = [pm[loc]["statement_id"] for loc in g["member_local_ids"]]
        _check(resolved == g["member_ids"], f"{g['group_id']}: local ids do not resolve to its member ids")
        impact = g["statement_type"] == "impact"
        members = []
        for loc, sid in zip(g["member_local_ids"], g["member_ids"]):
            r, pr = by_id[sid], by_id[sid]["proposal"]
            _check(r["precheck_status"] == "pass", f"{g['group_id']}: member {sid} is not a passing statement")
            geo = lg.classify(pr.get("region"), pr.get("region_scope"), gz)
            m = {"local_id": loc, "statement_id": sid, "paper_item_id": r["paper_item_id"],
                 "canonical_paper": canon.get(r["paper_item_id"], r["paper_item_id"]), "evidence_role": r["evidence_role"],
                 "passage_type": pr.get("passage_type"), "region": pr.get("region"), "region_scope": pr.get("region_scope"),
                 "region_class": geo["class"], "region_qualifier": geo.get("qualifier"), "states": list(geo["states"]),
                 "statement_family": r["statement_family"], "statement": pr["statement"]}
            if impact:
                m.update(asset_class=pr.get("asset_class"), hazard_relation=r.get("hazard_relation"),
                         impact_mechanism=pr.get("impact_mechanism"), impact_outcome=pr.get("impact_outcome"))
            members.append(m)
        if impact:                                                   # the agent copied these from meta; check them
            for field, key in (("asset_classes", "asset_class"), ("hazard_relations", "hazard_relation"),
                               ("impact_mechanisms", "impact_mechanism"), ("impact_outcomes", "impact_outcome")):
                _check(g.get(field) == [m[key] for m in members], f"{g['group_id']}: {field} differ from the member statements")
        fams = {m["statement_family"] for m in members}
        _check(fams == {part["hazard_family"]}, f"{g['group_id']}: member families {sorted(map(str, fams))} != the partition's")
        strength = li.strength_v2(members, canon)
        _check(strength == g["evidence_strength"], f"{g['group_id']}: strength {strength} != the agent's {g['evidence_strength']}")
        cc = {m["canonical_paper"] for m in members if m["evidence_role"] in la.CORE_OR_CITED}
        _check(len(cc) == g["n_independent_core_cited_papers"], f"{g['group_id']}: independent core/cited papers differ")
        rc = Counter(m["region_class"] for m in members)
        e = dict(g)
        e.update({"is_singleton": g["kind"] == "singleton", "partition": g["partition_id"], "chunk": g["chunk_id"],
                  "family": part["hazard_family"], "asset_partition": part.get("asset_partition"),
                  "asset_class_counts": dict(sorted(Counter(m.get("asset_class") or "" for m in members).items())) if impact else {},
                  "members": members, "n_papers": len({m["paper_item_id"] for m in members}),
                  "n_independent_papers": li.n_independent([m["paper_item_id"] for m in members], canon),
                  "evidence_strength": strength, "evidence_strength_rule": "D-045 / D-048 definitions, DR-LIT-IND-1 v2 (D-046) over the infra papers",
                  "region_classes": [c for c in lg.CLASSES if c in rc], "region_class_counts": {c: rc[c] for c in lg.CLASSES if c in rc},
                  "place_named_states": sorted({s for m in members if m["region_class"] == "state" for s in m["states"]}),
                  "has_place_named_member": any(m["region_class"] == "state" for m in members),
                  "has_us_place_member": any(m["region_class"] in US_PLACE_CLASSES for m in members),
                  "geography": lg.VERSION,
                  "label_digits_not_in_members": g2.label_digits_not_in_members(g["label"], [m["statement"] for m in members])})
        out.append(e)
    return out


def asset_label(g: dict) -> str:
    """The asset class shown for a record: the partition's class, or for `other_assets` the members' classes."""
    if g["statement_type"] != "impact":
        return "-"
    if g["asset_partition"] != lgi.OTHER:
        return g["asset_partition"]
    return "other_assets: " + ", ".join(f"{c or 'blank'} {n}" for c, n in g["asset_class_counts"].items())


def summarise(enriched: list[dict]) -> dict:
    grp = [g for g in enriched if not g["is_singleton"]]
    sgl = [g for g in enriched if g["is_singleton"]]

    def table(recs):
        t: dict = {}
        for g in recs:
            key = f"{g['statement_type']}:{g['asset_partition'] or '-'}"
            t.setdefault(g["family"], {}).setdefault(key, Counter())[g["evidence_strength"]] += 1
        return {f: {k: {s: n[s] for s in la.STRENGTHS if n[s]} for k, n in sorted(v.items())} for f, v in sorted(t.items())}

    hia = [g for g in grp if g["claim_about"] == "hazard_impact_on_asset"]
    multi = sorted((g for g in grp if g["evidence_strength"] == "multi_source_supported"),
                   key=lambda g: (g["family"], g["partition"], -g["n_independent_papers"], g["group_id"]))
    return {
        "run": RUN_ID, "geography": lg.VERSION, "records": len(enriched), "groups": len(grp), "singletons": len(sgl),
        "statements": sum(g["n_members"] for g in enriched),
        "groups_by_family_partition_strength": table(grp), "singletons_by_family_partition_strength": table(sgl),
        "records_by_strength": dict(Counter(g["evidence_strength"] for g in enriched)),
        "groups_by_claim": dict(sorted(Counter(g["claim_about"] for g in grp).items())),
        "singletons_by_claim": dict(sorted(Counter(g["claim_about"] for g in sgl).items())),
        "multi_source_groups": [{"group_id": g["group_id"], "family": g["family"], "asset_class": asset_label(g),
                                 "claim_about": g["claim_about"], "n_independent_papers": g["n_independent_papers"],
                                 "label": g["label"]} for g in multi],
        "hazard_impact_on_asset_groups": len(hia),
        "hazard_impact_on_asset_groups_with_place_named_member": sum(g["has_place_named_member"] for g in hia),
        "hazard_impact_on_asset_groups_with_us_place_member": sum(g["has_us_place_member"] for g in hia),
        "hazard_impact_on_asset_place_named": [{"group_id": g["group_id"], "states": g["place_named_states"], "label": g["label"],
                                                "evidence_strength": g["evidence_strength"]} for g in hia if g["has_place_named_member"]],
        "hazard_impact_on_asset_singletons_with_place_named_member":
            sum(g["has_place_named_member"] for g in sgl if g["claim_about"] == "hazard_impact_on_asset"),
        "groups_with_one_member": sum(g["n_members"] == 1 for g in grp),
        "labels_with_digit_not_in_members": [g["group_id"] for g in grp if g["label_digits_not_in_members"]],
        "duplicate_paper_merges": sum(g["n_papers"] != g["n_independent_papers"] for g in enriched),
        "by_region_class_members": dict(Counter(m["region_class"] for g in enriched for m in g["members"])),
    }


# --- manifest ---------------------------------------------------------------------------------


def _file_entry(path: Path) -> dict:
    return {"path": path.relative_to(ART).as_posix(), "sha256": sha256_file(path), "bytes": path.stat().st_size}


def manifest(facts: dict, excluded: list[dict], ingested_at: str | None = None) -> dict:
    files = [_file_entry(ART / name) for name in COPIED.values()]
    files += [_file_entry(p) for p in sorted(CHUNKS_DIR.glob("*.json"))]
    derived = [_file_entry(p) for p in (ENRICHED_PATH, ENRICHED_SUMMARY_PATH)]
    return {
        "run": "infra_run1", "diagnostic_id": RUN_ID, "decision": DECISION,
        "tarball": {"name": TARBALL_NAME, "sha256": TARBALL_SHA256},
        "generator": {"version": GENERATOR_VERSION, "agent_path": AGENT_REL, "agent_sha256": AGENT_SHA256,
                      "system_prompt_template_sha256": TEMPLATE_SHA256, "system_prompt_template_impact_sha256": TEMPLATE_IMPACT_SHA256,
                      "corrective_template_sha256": CORRECTIVE_SHA256},
        "budget": BUDGET, "endpoint": {"endpoint_label": ENDPOINT_LABEL, "model": MODEL, "base_url": BASE_URL,
                                       "chunks": RUN_FACTS["chunks"]},
        "source_commit": SOURCE_COMMIT,
        "partitions": {"path": "artifacts/litgroups/partitions_infra_v1.jsonl", "sha256": sha256_file(lgi.PARTITIONS_PATH)},
        "statements": {"path": "artifacts/litstatements/infra_run1/statements_ingested.jsonl", "sha256": sha256_file(ir.INGESTED_PATH)},
        "independence": {"path": "artifacts/litstatements/infra_run1/independence_v2.json", "sha256": sha256_file(ir.INDEPENDENCE_PATH)},
        "counts": dict(RUN_FACTS), "by_strength": BY_STRENGTH, "groups_by_claim_about": GROUPS_BY_CLAIM,
        "prompt_variants": PROMPT_VARIANTS, "corrective_chunks": facts["corrective_chunks"],
        "cross_chunk_merge": "not done; deferred to human review (D-051)",
        "log": facts["log"], "groups_sha256": GROUPS_SHA256, "summary_sha256": SUMMARY_SHA256,
        "files": files, "derived_files": derived, "excluded_files": excluded,
        "ingested_at": ingested_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ingested_by": "EXECUTOR",
    }


# --- part B: the COORDINATOR review list -------------------------------------------------------------------------------

REVIEW_PATH = REPO_ROOT / "artifacts" / "benchmark" / "review" / "P5_impact_groups_review_v1.csv"
REVIEW_COLUMNS = ("group_id", "kind", "family", "asset_partition", "asset_class", "claim_about", "evidence_strength",
                  "n_papers", "n_independent_papers", "label", "member_statements", "region_classes", "place_named_states",
                  "label_screen_flags", "coordinator_disposition", "kaiyuan_disposition")
#: Keyword screens over a label (part B): markers for the reviewer, never a disposition. Whole words, case-insensitive.
LABEL_SCREENS = {
    # "fire" followed by a hyphen or space and "weather" / "danger" is the index's own name, not fire occurrence
    "i_fire_occurrence": re.compile(r"\b(?:wildfires?|bushfires?|fires|fire(?![-\u2010\u2011\u2012\u2013 ](?:weather|danger))|"
                                    r"burn(?:ed|t|ing|s)?|burned area|blazes?|ignitions?|flames?|smoke)\b", re.I),
    "ii_people": re.compile(r"\b(?:mortality|deaths?|died|illness(?:es)?|heat[-\u2010\u2011 ]related|patients?|people|persons?|workers?|"
                            r"residents?|public health outcomes?|hospitali[sz]ations?|admissions?|morbidity|population|"
                            r"evacuat\w*|injur\w*|human health|health risks?|well[-\u2010\u2011]?being|elderly|children|"
                            r"pedestrians?|households?|occupants?|outdoor)\b", re.I),
    "iii_other_hazard": re.compile(r"\b(?:floods?|flooding|flash floods?|winds?|windstorms?|cold|freez\w*|frost|ice|icing|snow\w*|"
                                   r"storms?|hurricanes?|cyclones?|typhoons?|sea[-\u2010\u2011 ]level|precipitation|rain\w*|drought\w*|"
                                   r"landslides?|debris[-\u2010\u2011 ]flows?|rockfalls?|mudslides?|earthquakes?)\b", re.I),
}
FLAG_MARK = {"i_fire_occurrence": "(i) fire", "ii_people": "(ii) people", "iii_other_hazard": "(iii) other hazard"}


def label_flags(label: str | None) -> list[str]:
    """['(i) fire: wildfire', ...] --- the screens a label trips, with the words matched."""
    out = []
    for k, rx in LABEL_SCREENS.items():
        words = list(dict.fromkeys(m.group(0).lower() for m in rx.finditer(label or "")))
        if words:
            out.append(f"{FLAG_MARK[k]}: {', '.join(words)}")
    return out


def review_rows(enriched: list[dict]) -> list[dict]:
    """Every group and singleton tagged hazard_impact_on_asset or impact_or_exposure; groups first, then singletons, each
    by family, claim tag, partition and id."""
    recs = [g for g in enriched if g["claim_about"] in REVIEW_CLAIMS]
    recs.sort(key=lambda g: (g["is_singleton"], g["family"], REVIEW_CLAIMS.index(g["claim_about"]), g["partition"], g["group_id"]))
    out = []
    for g in recs:
        out.append({"group_id": g["group_id"], "kind": g["kind"], "family": g["family"], "asset_partition": g["asset_partition"] or "",
                    "asset_class": "; ".join(f"{c or 'blank'} ({n})" for c, n in g["asset_class_counts"].items()),
                    "claim_about": g["claim_about"], "evidence_strength": g["evidence_strength"], "n_papers": g["n_papers"],
                    "n_independent_papers": g["n_independent_papers"], "label": g["label"] or "",
                    "member_statements": " || ".join(m["statement"] for m in g["members"]),
                    "region_classes": "; ".join(f"{c} ({g['region_class_counts'][c]})" for c in lg.CLASSES
                                                if c in g["region_class_counts"]),
                    "place_named_states": "; ".join(g["place_named_states"]),
                    "label_screen_flags": " | ".join(label_flags(g["label"])), "coordinator_disposition": "",
                    "kaiyuan_disposition": ""})
    return out


def write_review_csv(path: Path, rows: list[dict]) -> None:
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(REVIEW_COLUMNS), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def hia_label_listing(enriched: list[dict]) -> dict:
    """{family: {asset class: [{group_id, label, strength, n_independent_papers, place_named_states, flags}]}} over the
    hazard_impact_on_asset groups (not singletons: they carry no label)."""
    out: dict = {}
    for g in sorted((g for g in enriched if not g["is_singleton"] and g["claim_about"] == "hazard_impact_on_asset"),
                    key=lambda g: (g["family"], g["asset_partition"] == lgi.OTHER, g["asset_partition"], g["group_id"])):
        out.setdefault(g["family"], {}).setdefault(asset_label(g) if g["asset_partition"] != lgi.OTHER else lgi.OTHER, []).append(
            {"group_id": g["group_id"], "label": g["label"], "evidence_strength": g["evidence_strength"],
             "n_independent_papers": g["n_independent_papers"], "asset_class_counts": g["asset_class_counts"],
             "place_named_states": g["place_named_states"], "flags": label_flags(g["label"])})
    return out
