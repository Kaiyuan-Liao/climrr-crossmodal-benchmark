"""Grouping run 2: verification, ingest and enrichment (pilot P2b-ingest; D-051, D-052).

Run 2 is `litgroup_agent` v3 on Polaris (Sophia vLLM, `openai/gpt-oss-120b`) over the tracked
`partitions_v1.jsonl` at source commit `7676e53`: 11 partitions in 23 chunks of <= 40 statements.
`verify_source` re-derives every fact the work package states from the delivered tarball (hashes,
budget, chunks, corrective turns, the three chunks that passed on a second attempt with identical
configuration, groups / singletons, each of the 747 statements exactly once, endpoints, the logs) and
raises on any difference. `copy_run` copies the run files and every chunk's `result.json` (as
`chunks/<chunk_id>.json`, a failed first attempt as `chunks/<chunk_id>.failed_attempt1.json`) into
`artifacts/litgroups/run2/`; prompts and raw responses are not copied (SHA-256 in `manifest.json`).
Run 1 (agent v2) is recorded as superseded (budget, D-051), never ingested.

`enrich` gives every group record (a singleton becomes a one-member group, `is_singleton: true`):
members resolved through the partition's local ids to `LS-` ids with paper and canonical paper (D-046),
`n_papers`, `n_independent_papers`, the D-045 / D-048 `evidence_strength` recomputed and checked against
the agent's, the agent's `claim_about` (never inferred here), the members' `region_classes` under
geography v2 (`litgeo` v2, D-047a), `partition` and `chunk`. `is_singleton` follows the agent's `kind`: a
labelled group the model returned with one member (the agent's non-gating `single_member` check) stays a group,
and is counted in the summary.

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from climrr import litaggregate as la
from climrr import litgeo as lg
from climrr import litgroups as lgr
from climrr import litindependence as li
from climrr import litstatements_run2 as r2
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

RUN_ID = "litgroups_run2"
DECISION = "D-052"
ART = lgr.OUT_DIR / "run2"
CHUNKS_DIR = ART / "chunks"
MANIFEST_PATH = ART / "manifest.json"
ENRICHED_PATH = ART / "groups_enriched.jsonl"
ENRICHED_SUMMARY_PATH = ART / "groups_enriched_summary.json"

TARBALL_NAME = "litgroups_run2_evidence.tar.gz"
TARBALL_SHA256 = "a90ad7f011424db37082ea692b1987c9a7697d399ef20c1737afa8535374e2eb"
GROUPS_SHA256 = "fc5ceea5b57a7d0bcfc9fe7f88de5f171aaebd60b4ce1afeb51acd179d4b558a"
SUMMARY_SHA256 = "0253c687deb304d0a3a72e6755d6fe5a39815932e680977e11834c4bbf4ab5c5"
AGENT_REL = "scripts/litcollect/litgroup_agent.py"
AGENT_SHA256 = "e094aa5cbd4b981042fe07f165afc5d83ba77000ca718f185bcecee325d845f4"
TEMPLATE_SHA256 = "ac135f00570d75f487c7bd414a662a18c271861afa5f026e3e17b3c4fb752ae7"
CORRECTIVE_SHA256 = "5d052853cc681596553912d25747cd59bbc7b548009e10715b7da30ea88d54b6"
SOURCE_COMMIT = "7676e53319b3b7a5962b0b431c5457837e7c37ba"
GENERATOR_VERSION = "litgroup_agent v3"
ENDPOINT_LABEL, MODEL, BASE_URL = "sophia_vllm", "openai/gpt-oss-120b", r2.BASE_URL
ENDPOINT = f"{ENDPOINT_LABEL} {MODEL}"
BUDGET = {"reasoning_effort": "low", "max_tokens": 16000, "chunk_size": 40, "temperature": 0}
RUN_FACTS = {"partitions": 11, "chunks": 23, "chunks_pass": 23, "chunks_fail": 0, "corrective_retry_used": 15,
             "corrective_passed_first_attempt": 12, "groups": 239, "singletons": 155, "statements": 747}
SECOND_ATTEMPT_CHUNKS = ("extreme_heat_v1.driver.c1", "extreme_heat_v1.driver.c2", "fire_weather_v1.mechanism.c2")
#: Fields that must be equal between a failed first attempt and its second attempt ("same configuration").
SAME_CONFIG_FIELDS = ("generator_version", "base_url", "model", "endpoint_label", "temperature", "reasoning_effort",
                      "max_tokens", "chunk_size", "system_prompt_sha256", "system_prompt_template_sha256",
                      "corrective_template_sha256", "prompt_hash", "source_commit", "local_ids")
SUPERSEDED_RUNS = [{"run": "run1", "generator_version": "litgroup_agent v2", "reason": "budget", "decision": "D-051",
                    "note": "max_tokens 6000 spent on reasoning; every partition >= 46 statements finish_reason=length"}]
EXCLUDED_NAMES = ("prompt_user.txt", "response.json", "prompt_corrective.txt", "response_corrective.json")
COPIED = {  # source (relative to the extracted tarball) -> destination name under ART
    "litgroups/run2/groups.jsonl": "groups.jsonl",
    "litgroups/run2/summary.json": "summary.json",
    "litgroups/run2/agent.log": "agent.log",
    "reports/litgroups_run1.log": "litgroups_run1.log",
    "reports/litgroups_run2.log": "litgroups_run2.log",
}
_DIGITS = re.compile(r"\d+(?:[.,]\d+)?")  # as the agent's label check


def _run(src: Path, run: str = "run2") -> Path:
    return Path(src) / "litgroups" / run


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _load(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def expected_chunk_ids(summary: dict) -> list[str]:
    return [f"{pid}.c{k}" for pid, n in summary["chunks_per_partition"].items() for k in range(1, n + 1)]


def parse_log(text: str) -> dict:
    kv = lambda ln: dict(re.findall(r"(\w+)=(\S+)", ln))  # noqa: E731
    lines = text.splitlines()
    starts = [ln for ln in lines if " START " in ln]
    dones = [ln for ln in lines if " DONE " in ln]
    chunk_lines = [ln for ln in lines if " status=" in ln]
    return {"invocations": len(starts), "start_utc": starts[0].split()[0] if starts else None,
            "end_utc": dones[-1].split()[0] if dones else None, "done": [kv(ln) for ln in dones],
            "corrective_lines": sum(" CORRECTIVE " in ln for ln in lines),
            "chunk_lines": [{"chunk_id": ln.split()[1], **kv(ln)} for ln in chunk_lines],
            "starts": [kv(ln) for ln in starts]}


def agent_sha_at(commit: str) -> str:
    blob = subprocess.run(["git", "show", f"{commit}:{AGENT_REL}"], cwd=REPO_ROOT, capture_output=True, check=True).stdout
    return hashlib.sha256(blob).hexdigest()


def _without_id(g: dict) -> dict:
    return {k: v for k, v in g.items() if k != "group_id"}


def first_attempt_record(failed: dict, final: dict) -> dict:
    c = failed["checks"]
    ft = failed.get("first_turn") or {}
    return {"chunk_id": failed["chunk_id"],
            "first_attempt": {"generation_timestamp": failed["generation_timestamp"], "status": failed["status"],
                              "failed": c["failed"], "missing_ids": len(c["missing_ids"]), "duplicate_ids": len(c["duplicate_ids"]),
                              "unknown_ids": len(c["unknown_ids"]), "corrective_retry_used": failed["corrective_retry_used"],
                              "model_attempts": failed["model_attempts"], "finish_reason": failed["finish_reason"],
                              "first_turn_failed": (ft.get("checks") or {}).get("failed")},
            "second_attempt": {"generation_timestamp": final["generation_timestamp"], "status": final["status"],
                               "corrective_retry_used": final["corrective_retry_used"], "model_attempts": final["model_attempts"],
                               "finish_reason": final["finish_reason"]},
            "same_configuration": all(failed.get(k) == final.get(k) for k in SAME_CONFIG_FIELDS),
            "same_configuration_fields": list(SAME_CONFIG_FIELDS)}


def verify_source(src: Path, partitions: list[dict] | None = None) -> dict:
    """Every run-2 fact the work package states, re-derived from the delivered files. Raises on any difference."""
    src, run = Path(src), _run(src)
    _check(sha256_file(run / "groups.jsonl") == GROUPS_SHA256, "groups.jsonl differs from its stated SHA-256")
    _check(sha256_file(run / "summary.json") == SUMMARY_SHA256, "summary.json differs from its stated SHA-256")
    _check(sha256_file(REPO_ROOT / AGENT_REL) == AGENT_SHA256, f"{AGENT_REL} differs from the pinned v3 SHA-256")
    _check(agent_sha_at(SOURCE_COMMIT) == AGENT_SHA256, f"{AGENT_REL} at the source commit differs from the pinned SHA-256")
    s = _load(run / "summary.json")
    for k, v in (("generator_version", GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL),
                 ("base_url", BASE_URL), ("reasoning_effort", BUDGET["reasoning_effort"]), ("max_tokens", BUDGET["max_tokens"]),
                 ("chunk_size", BUDGET["chunk_size"]), ("partitions_in_file", RUN_FACTS["partitions"]),
                 ("chunks_in_file", RUN_FACTS["chunks"]), ("chunks_done", RUN_FACTS["chunks"]),
                 ("chunks_pass", RUN_FACTS["chunks_pass"]), ("corrective_retry_used", RUN_FACTS["corrective_retry_used"]),
                 ("corrective_retry_pass", RUN_FACTS["corrective_retry_used"]), ("groups", RUN_FACTS["groups"]),
                 ("singletons", RUN_FACTS["singletons"]), ("statements_grouped", RUN_FACTS["statements"]),
                 ("groups_label_fail", 0), ("claim_about_fail", 0), ("reasoning_effort_not_applied", 0),
                 ("system_prompt_template_sha256", TEMPLATE_SHA256), ("corrective_template_sha256", CORRECTIVE_SHA256)):
        _check(s.get(k) == v, f"summary {k} = {s.get(k)!r}, expected {v!r}")
    _check(s["chunks_fail"] == [], f"summary chunks_fail = {s['chunks_fail']}")
    _check(s["endpoints_in_results"] == {f"{ENDPOINT} {BASE_URL}": RUN_FACTS["chunks"]}, "endpoints_in_results differs")

    chunk_ids = expected_chunk_ids(s)
    dirs = sorted(p.name for p in run.iterdir() if p.is_dir())
    _check(sorted(chunk_ids) == dirs, f"chunk dirs {dirs} != expected {sorted(chunk_ids)}")
    results = {c: _load(run / c / "result.json") for c in chunk_ids}
    for c, r in results.items():
        _check(r["chunk_id"] == c and r["status"] == "deterministic_pass", f"{c}: status {r['status']}")
        for k, v in (("generator_version", GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL),
                     ("base_url", BASE_URL), ("source_commit", SOURCE_COMMIT), ("reasoning_effort_applied", True),
                     ("finish_reason", "stop"), ("system_prompt_template_sha256", TEMPLATE_SHA256),
                     ("corrective_template_sha256", CORRECTIVE_SHA256), *BUDGET.items()):
            _check(r.get(k) == v, f"{c}: {k} = {r.get(k)!r}, expected {v!r}")
    failed_paths = sorted(run.glob("*/result.failed_attempt1.json"))
    _check(tuple(sorted(p.parent.name for p in failed_paths)) == SECOND_ATTEMPT_CHUNKS,
           f"failed first attempts in {[p.parent.name for p in failed_paths]}")
    second = []
    for p in failed_paths:
        f = _load(p)
        _check(f["status"] == "deterministic_fail", f"{p.parent.name}: failed attempt status {f['status']}")
        rec = first_attempt_record(f, results[p.parent.name])
        _check(rec["same_configuration"], f"{p.parent.name}: second attempt configuration differs")
        second.append(rec)
    corrective = sorted(c for c, r in results.items() if r["corrective_retry_used"])
    _check(len(corrective) == RUN_FACTS["corrective_retry_used"], f"{len(corrective)} chunks used the corrective turn")
    first_time = [c for c in corrective if c not in SECOND_ATTEMPT_CHUNKS]
    _check(len(first_time) == RUN_FACTS["corrective_passed_first_attempt"], f"{len(first_time)} corrective chunks passed first time")

    # groups.jsonl is the chunks' records in chunk order, numbered per (arm, type, chunk index)
    groups = lgr.read_groups(run / "groups.jsonl")
    rederived = [_without_id(g) for c in chunk_ids for g in results[c]["groups"]]
    _check([_without_id(g) for g in groups] == rederived, "groups.jsonl is not the chunks' records in chunk order")
    for g in groups:
        k = results[g["chunk_id"]]["chunk_index"]
        _check(g["group_id"].startswith(f"LG-{g['arm']}-{g['statement_type']}-c{k}-"), f"{g['group_id']}: id not of its chunk")
    _check(len({g["group_id"] for g in groups}) == len(groups), "duplicate group ids")
    kinds = Counter(g["kind"] for g in groups)
    _check(kinds == {"group": RUN_FACTS["groups"], "singleton": RUN_FACTS["singletons"]}, f"kinds {dict(kinds)}")
    members = [m for g in groups for m in g["member_ids"]]
    _check(len(members) == len(set(members)) == RUN_FACTS["statements"], f"{len(members)} member slots, {len(set(members))} distinct")
    _check(all(g["endpoint_label"] == ENDPOINT_LABEL and g["model"] == MODEL for g in groups), "a group record names another endpoint")
    if partitions is not None:
        part_ids = {m["statement_id"] for p in partitions for m in p["meta"].values()}
        _check(set(members) == part_ids, "grouped statements differ from the partitions' statements")

    log = (run / "agent.log").read_text(encoding="utf-8")
    _check(log == (src / "reports" / "litgroups_run2.log").read_text(encoding="utf-8"), "agent.log differs from reports/litgroups_run2.log")
    pl = parse_log(log)
    last = pl["done"][-1]
    _check((last["chunks"], last["pass"], last["fail"], last["corrective"], last["groups"], last["singletons"]) ==
           ("23", "23", "0", "15", "239", "155"), f"last DONE line {last}")
    first_fail = sorted(x["chunk_id"] for x in pl["chunk_lines"][:RUN_FACTS["chunks"]] if x["status"] == "deterministic_fail")
    _check(tuple(first_fail) == SECOND_ATTEMPT_CHUNKS, f"first invocation failed {first_fail}")
    partitions_sha = {x["partitions_sha"] for x in pl["starts"]}
    _check(len(partitions_sha) == 1, f"partitions_sha in START lines {partitions_sha}")
    _check(sha256_file(lgr.PARTITIONS_PATH).startswith(partitions_sha.pop()), "partitions_v1.jsonl differs from the run's partitions")
    return {"summary": s, "chunk_ids": chunk_ids, "corrective_chunks": corrective, "corrective_passed_first_attempt": first_time,
            "second_attempt_chunks": second, "log": {k: pl[k] for k in ("invocations", "start_utc", "end_utc", "corrective_lines")}
            | {"done_lines": pl["done"]}, "run1": run1_facts(src)}


def run1_facts(src: Path) -> dict:
    run = _run(src, "run1")
    s = _load(run / "summary.json")
    return {"generator_version": s["generator_version"], "partitions_in_file": s["partitions_in_file"],
            "partitions_pass": s["partitions_pass"], "partitions_fail": len(s["partitions_fail"]),
            "groups": s["groups"], "singletons": s["singletons"],
            "files": [{"path": p.relative_to(Path(src)).as_posix(), "sha256": sha256_file(p), "bytes": p.stat().st_size}
                      for p in sorted(run.rglob("*")) if p.is_file()]}


# --- copy ---------------------------------------------------------------------------------------


def copy_run(src: Path) -> int:
    src, n = Path(src), 0
    for rel, name in COPIED.items():
        n += r2._copy(src / rel, ART / name)
    for p in sorted(_run(src).glob("*/result.json")):
        n += r2._copy(p, CHUNKS_DIR / f"{p.parent.name}.json")
    for p in sorted(_run(src).glob("*/result.failed_attempt1.json")):
        n += r2._copy(p, CHUNKS_DIR / f"{p.parent.name}.failed_attempt1.json")
    return n


def excluded_files(src: Path) -> list[dict]:
    return [{"path": f"litgroups/run2/{p.parent.name}/{p.name}", "sha256": sha256_file(p), "bytes": p.stat().st_size}
            for p in sorted(_run(src).glob("*/*")) if p.name in EXCLUDED_NAMES]


# --- enrichment ---------------------------------------------------------------------------------


def label_digits_not_in_members(label: str | None, sentences: list[str]) -> list[str]:
    text = " ".join(sentences)
    return [d for d in _DIGITS.findall(label or "") if d not in text]


def enrich(groups: list[dict], partitions: list[dict], records: list[dict], indep: dict, gz: lg.Gazetteer) -> list[dict]:
    """The enriched record of every group and singleton (module docstring); raises if a recomputation differs."""
    canon = li.canonical_map(indep)
    by_id = {r["statement_id"]: r for r in la.entering(records)}
    meta = {p["partition_id"]: p["meta"] for p in partitions}
    out = []
    for g in groups:
        pm = meta[g["partition_id"]]
        resolved = [pm[loc]["statement_id"] for loc in g["member_local_ids"]]
        _check(resolved == g["member_ids"], f"{g['group_id']}: local ids do not resolve to its member ids")
        members = []
        for loc, sid in zip(g["member_local_ids"], g["member_ids"]):
            r, pr = by_id[sid], by_id[sid]["proposal"]
            geo = lg.classify(pr.get("region"), pr.get("region_scope"), gz)
            members.append({"local_id": loc, "statement_id": sid, "paper_item_id": r["paper_item_id"],
                            "canonical_paper": canon.get(r["paper_item_id"], r["paper_item_id"]),
                            "evidence_role": r["evidence_role"], "passage_type": pr.get("passage_type"),
                            "region": pr.get("region"), "region_scope": pr.get("region_scope"),
                            "region_class": geo["class"], "region_qualifier": geo.get("qualifier"),
                            "statement": pr["statement"]})
        strength = li.strength_v2(members, canon)
        _check(strength == g["evidence_strength"], f"{g['group_id']}: strength {strength} != the agent's {g['evidence_strength']}")
        cc = {m["canonical_paper"] for m in members if m["evidence_role"] in la.CORE_OR_CITED}
        _check(len(cc) == g["n_independent_core_cited_papers"], f"{g['group_id']}: independent core/cited papers differ")
        rc = Counter(m["region_class"] for m in members)
        e = dict(g)
        e.update({"is_singleton": g["kind"] == "singleton", "partition": g["partition_id"], "chunk": g["chunk_id"],
                  "members": members, "n_papers": len({m["paper_item_id"] for m in members}),
                  "n_independent_papers": li.n_independent([m["paper_item_id"] for m in members], canon),
                  "evidence_strength": strength, "evidence_strength_rule": "D-045 / D-048 definitions, DR-LIT-IND-1 v2 (D-046)",
                  "region_classes": [c for c in lg.CLASSES if c in rc], "region_class_counts": {c: rc[c] for c in lg.CLASSES if c in rc},
                  "geography": lg.VERSION,
                  "label_digits_not_in_members": label_digits_not_in_members(g["label"], [m["statement"] for m in members])})
        out.append(e)
    return out


def summarise(enriched: list[dict]) -> dict:
    def table(recs):
        t: dict = {}
        for g in recs:
            t.setdefault(g["arm"], {}).setdefault(g["claim_about"], Counter())[g["evidence_strength"]] += 1
        return {a: {c: {s: n[s] for s in la.STRENGTHS if n[s]} for c, n in sorted(v.items())} for a, v in sorted(t.items())}

    grp = [g for g in enriched if not g["is_singleton"]]
    sgl = [g for g in enriched if g["is_singleton"]]
    largest = sorted(grp, key=lambda g: (-g["n_papers"], -g["n_members"], g["group_id"]))[:10]
    return {
        "run": RUN_ID, "geography": lg.VERSION, "records": len(enriched), "groups": len(grp), "singletons": len(sgl),
        "statements": sum(g["n_members"] for g in enriched),
        "groups_by_arm_claim_strength": table(grp), "singletons_by_arm_claim_strength": table(sgl),
        "multi_source_mechanism_groups_by_arm": {a: sum(g["arm"] == a and g["claim_about"] == "hazard_change_mechanism"
                                                        and g["evidence_strength"] == "multi_source_supported" for g in grp)
                                                 for a in la.ARMS},
        "largest_groups": [{"group_id": g["group_id"], "label": g["label"], "n_papers": g["n_papers"], "n_members": g["n_members"],
                            "evidence_strength": g["evidence_strength"], "claim_about": g["claim_about"]} for g in largest],
        "groups_with_one_member": sum(g["n_members"] == 1 for g in grp),
        "groups_with_one_member_by_chunk": dict(sorted(Counter(g["chunk"] for g in grp if g["n_members"] == 1).items())),
        "labels_with_digit_not_in_members": [g["group_id"] for g in grp if g["label_digits_not_in_members"]],
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
        "run": "run2", "diagnostic_id": RUN_ID, "decision": DECISION,
        "tarball": {"name": TARBALL_NAME, "sha256": TARBALL_SHA256},
        "generator": {"version": GENERATOR_VERSION, "agent_path": AGENT_REL, "agent_sha256": AGENT_SHA256,
                      "system_prompt_template_sha256": TEMPLATE_SHA256, "corrective_template_sha256": CORRECTIVE_SHA256},
        "budget": BUDGET, "endpoint": {"endpoint_label": ENDPOINT_LABEL, "model": MODEL, "base_url": BASE_URL,
                                       "chunks": RUN_FACTS["chunks"]},
        "source_commit": SOURCE_COMMIT,
        "partitions": {"path": "artifacts/litgroups/partitions_v1.jsonl", "sha256": sha256_file(lgr.PARTITIONS_PATH)},
        "counts": dict(RUN_FACTS), "corrective_chunks": facts["corrective_chunks"],
        "corrective_passed_first_attempt": facts["corrective_passed_first_attempt"],
        "second_attempt_chunks": facts["second_attempt_chunks"],
        "cross_chunk_merge": "not done; deferred to human review (D-051, D-052)",
        "log": facts["log"], "groups_sha256": GROUPS_SHA256, "summary_sha256": SUMMARY_SHA256,
        "superseded_runs": [dict(SUPERSEDED_RUNS[0], observed=facts["run1"])],
        "files": files, "derived_files": derived, "excluded_files": excluded,
        "ingested_at": ingested_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ingested_by": "EXECUTOR",
    }
