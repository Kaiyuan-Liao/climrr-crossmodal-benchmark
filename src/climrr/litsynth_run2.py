"""Synthesis run 2: verification, ingest and the human-review lifecycle step (pilot P2b-ingest-items; D-055b, D-056).

Run 2 is `litsynth_agent` v3.2 on Polaris (Sophia vLLM, `openai/gpt-oss-120b`, reasoning low, max_tokens 16000) over the
ten packets v3a at source commit `1f175da`. `verify_source` re-derives every fact the work package states from the
delivered tarball (hashes; agent, system-prompt and format-corrective-template SHA-256; ten items, ten
`deterministic_pass`, no leakage flag; the format corrective turn on exactly 0001, 0002, 0006, 0008, 0009, 0010; the
recovered HTTP retries; endpoint and budget; every item's packet equal to packets v3a at the source commit; the logs;
`items.jsonl` equal to the per-item files) and raises on any difference. `reproduce_checks` re-assembles each item from
its final raw response with the pinned agent, and re-runs `synthesis_post_checks` v2.2 on the delivered item against its
v3a packet (`checks_input`): both must equal what the run recorded (`checks_reproduced`).

`copy_run` copies `items.jsonl`, `summary.json`, the log and the dump `.md` into `artifacts/benchmark/items/run2/`, and
the two superseded runs' logs and summaries under `superseded/`; prompts and raw responses are not copied (SHA-256 in
`manifest.json`). `human_review_item` is the D-033 lifecycle step: `review.status` deterministic_pass -> human_review, a
history event appended, both dispositions and `final_frozen` null. The ingested per-item records
`items/<item_id>.json` are the delivered records with that step applied; `items.jsonl` stays byte-identical to the run.

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from climrr import benchmark_items as bi
from climrr import litstatements_run2 as r2
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

RUN_ID = "litsynth_run2"
DECISION = "D-056"
ART = REPO_ROOT / "artifacts" / "benchmark" / "items" / "run2"
ITEMS_DIR = ART / "items"
SUPERSEDED_DIR = ART / "superseded"
MANIFEST_PATH = ART / "manifest.json"

TARBALL_NAME = "litsynth_runs012_evidence.tar.gz"
TARBALL_SHA256 = "00c909340bd08d61331e1eb6515da0b2bf375627b63d7491456c740949ebaac1"
ITEMS_SHA256 = "b0e0c60ff007ce1542c04534cdb1a89bad36aafe26d95f6cbfa5a6090c308bb8"
SUMMARY_SHA256 = "8908314133ca38630d2b691e0c503f17e54c9b0b4eb5a48ad1932939fb89b0cc"
AGENT_REL = "scripts/litcollect/litsynth_agent.py"
AGENT_SHA256 = "f5778fbf54ea44794d40086b997a504971812fe8a4481f7fedefae5f6d4b8b5e"
SYSTEM_PROMPT_SHA256 = "9c79f45262b1a039e43edb46c928b6d32fa75f903eca34229d32838a734f5715"
FORMAT_CORRECTIVE_SHA256 = "919f52cb2612c6f7544a2d62f4488231a16092376e43ebef03e4a23ca7066d20"
SOURCE_COMMIT = "1f175dac7801b3d27ca7ed1961debe88e22b4dc6"
PACKETS_REL = "artifacts/benchmark/synth_packets"
PACKETS_MANIFEST_SHA256 = "86b02cd00f333249b91e49bca3d4ce4b40f33d1bea30bb76463875d392b8b84c"  # packets v3a
GENERATOR_VERSION = "litsynth_agent v3.2"
ENDPOINT_LABEL, MODEL, BASE_URL = "sophia_vllm", "openai/gpt-oss-120b", r2.BASE_URL
BUDGET = {"reasoning_effort": "low", "max_tokens": 16000, "temperature": 0}
RUN_FACTS = {"items": 10, "deterministic_pass": 10, "deterministic_fail": 0, "leakage_flags": 0, "corrective_retry_used": 0,
             "format_corrective_used": 6, "format_corrective_pass": 6}
FORMAT_CORRECTIVE_ITEMS = ("BI-P2B-0001", "BI-P2B-0002", "BI-P2B-0006", "BI-P2B-0008", "BI-P2B-0009", "BI-P2B-0010")
#: The two HTTP retries the log records, each recovered on the second attempt: (seed id, reason prefix).
HTTP_RETRIES = (("SD2-TP1-00069", "RemoteDisconnected"), ("SD2-TP1-02787", "HTTP 502"))
SUPERSEDED_RUNS = [
    {"run": "run0_rung1", "generator_version": "litsynth_agent v2", "reason": "number formatting", "decision": "D-055",
     "note": "2 rung-1 items, both rejected_pre_review on numbers_untraced (rounded values, number-words)"},
    {"run": "run1", "generator_version": "litsynth_agent v3.1", "reason": "format checks", "decision": "D-055b",
     "note": "10 items, all rejected_pre_review on format checks only (7 of them the 'one' false positive)"},
]
COPIED = {  # source (relative to the extracted tarball) -> destination under ART
    "litsynth/run2/items.jsonl": "items.jsonl",
    "litsynth/run2/summary.json": "summary.json",
    "litsynth/run2/agent.log": "agent.log",
    "reports/litsynth_run2_items.md": "litsynth_run2_items.md",
    "reports/litsynth_run0_rung1.log": "superseded/litsynth_run0_rung1.log",
    "litsynth/run0_rung1/summary.json": "superseded/run0_rung1_summary.json",
    "reports/litsynth_run1.log": "superseded/litsynth_run1.log",
    "litsynth/run1/summary.json": "superseded/run1_summary.json",
}
HUMAN_REVIEW_NOTE = ("entered human review (D-033 lifecycle; D-056): Kaiyuan in artifacts/benchmark/review/P2b_items_review_v1.xlsx, "
                     "then the mentor; edits are recorded in review.final_frozen")


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _load(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _run(src: Path, run: str = "run2") -> Path:
    return Path(src) / "litsynth" / run


def git_blob(commit: str, rel: str) -> bytes:
    return subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=REPO_ROOT, capture_output=True, check=True).stdout


def packet_at_source(seed_id: str) -> tuple[dict, str]:
    """(the v3a packet the run read, its SHA-256), from the source commit --- not the working tree, which carries v3b."""
    blob = git_blob(SOURCE_COMMIT, f"{PACKETS_REL}/PK-{seed_id}.json")
    return json.loads(blob.decode("utf-8")), hashlib.sha256(blob).hexdigest()


def read_items(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]


def read_item_files(src: Path) -> list[dict]:
    """The per-item files `items/<seed_id>.json`, in `items.jsonl` order. `items.jsonl` is written with sorted keys, which
    reorders the rubric lists and so the order of `checks.texts_traced_to_literature`; the per-item files keep the agent's
    key order (`verify_source` checks they are equal to the `items.jsonl` lines as objects)."""
    run = _run(src)
    return [_load(run / "items" / f"{it['review']['history'][0]['seed_id']}.json") for it in read_items(run / "items.jsonl")]


def parse_log(text: str) -> dict:
    lines = text.splitlines()
    return {"start_utc": next((ln.split()[0] for ln in lines if " START " in ln), None),
            "end_utc": next((ln.split()[0] for ln in reversed(lines) if " DONE " in ln), None),
            "done": [ln.split(" DONE ", 1)[1] for ln in lines if " DONE " in ln],
            "format_corrective_seeds": [re.search(r"seed=(\S+)", ln).group(1) for ln in lines if " FORMAT_CORRECTIVE " in ln],
            "retries": [(re.search(r"paper=(\S+)", ln).group(1), ln.split("reason=", 1)[1]) for ln in lines if " RETRY " in ln],
            "item_lines": [ln for ln in lines if " status=" in ln]}


def verify_source(src: Path) -> dict:
    """Every run-2 fact the work package states, re-derived from the delivered files. Raises on any difference."""
    src, run = Path(src), _run(src)
    _check(sha256_file(run / "items.jsonl") == ITEMS_SHA256, "items.jsonl differs from its stated SHA-256")
    _check(sha256_file(run / "summary.json") == SUMMARY_SHA256, "summary.json differs from its stated SHA-256")
    _check(sha256_file(REPO_ROOT / AGENT_REL) == AGENT_SHA256, f"{AGENT_REL} differs from the pinned v3.2 SHA-256")
    _check(hashlib.sha256(git_blob(SOURCE_COMMIT, AGENT_REL)).hexdigest() == AGENT_SHA256,
           f"{AGENT_REL} at the source commit differs from the pinned SHA-256")
    _check(hashlib.sha256(git_blob(SOURCE_COMMIT, f"{PACKETS_REL}/manifest.json")).hexdigest() == PACKETS_MANIFEST_SHA256,
           "the packet manifest at the source commit is not packets v3a")
    s = _load(run / "summary.json")
    for k, v in (("generator_version", GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL), ("base_url", BASE_URL),
                 ("reasoning_effort", BUDGET["reasoning_effort"]), ("max_tokens", BUDGET["max_tokens"]),
                 ("system_prompt_sha256", SYSTEM_PROMPT_SHA256), ("format_corrective_prompt_sha256", FORMAT_CORRECTIVE_SHA256),
                 ("items", RUN_FACTS["items"]), ("deterministic_pass", RUN_FACTS["deterministic_pass"]),
                 ("deterministic_fail", RUN_FACTS["deterministic_fail"]), ("fail_reasons_by_kind", {}),
                 ("corrective_retry_used", RUN_FACTS["corrective_retry_used"]),
                 ("format_corrective_used", RUN_FACTS["format_corrective_used"]),
                 ("format_corrective_pass", RUN_FACTS["format_corrective_pass"]), ("reasoning_effort_not_applied", 0),
                 ("finish_reasons", {"stop": RUN_FACTS["items"]})):
        _check(s.get(k) == v, f"summary {k} = {s.get(k)!r}, expected {v!r}")

    items = read_items(run / "items.jsonl")
    _check(len(items) == RUN_FACTS["items"], f"{len(items)} items")
    v3a = json.loads(git_blob(SOURCE_COMMIT, f"{PACKETS_REL}/manifest.json"))
    v3a_sha = {x["seed_id"]: x["sha256"] for x in v3a["packets"]}
    v3a_item = {x["seed_id"]: x["item_id"] for x in v3a["packets"]}
    files = sorted(p.name for p in (run / "items").glob("*.json"))
    _check(files == sorted(f"{seed}.json" for seed in v3a_sha), f"item files {files}")
    corrective, leakage_flags, http = [], 0, []
    for it in items:
        h = it["review"]["history"][0]
        sid = h["seed_id"]
        _check(_load(run / "items" / f"{sid}.json") == it, f"{sid}: items/{sid}.json differs from its items.jsonl line")
        _check(it["item_id"] == v3a_item[sid], f"{sid}: item id {it['item_id']} != the packet's {v3a_item[sid]}")
        _check(it["review"]["status"] == "deterministic_pass" and h["event"] == "deterministic_pass" and h["reasons"] == [],
               f"{it['item_id']}: status {it['review']['status']}")
        _check(h["check_version"] == bi.SYNTH_CHECK_VERSION, f"{it['item_id']}: checks {h['check_version']}")
        _, pk_sha = packet_at_source(sid)
        _check(h["packet_sha256"] == it["generation"]["inputs_sha256"]["packet"] == pk_sha == v3a_sha[sid],
               f"{it['item_id']}: packet SHA-256 is not packets v3a")
        for k, v in (("generator_version", GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL),
                     ("base_url", BASE_URL), ("source_commit", SOURCE_COMMIT), ("reasoning_effort_applied", True),
                     ("system_prompt_sha256", SYSTEM_PROMPT_SHA256), ("finish_reason", "stop"),
                     ("corrective_retry_used", False), *BUDGET.items()):
            _check(h.get(k) == v, f"{it['item_id']}: {k} = {h.get(k)!r}, expected {v!r}")
        lk = it["source_leakage_check"]
        leakage_flags += len(lk["flags"]) + len(h["checks"]["prompt_leakage"]["flags"])
        _check(lk["pass"] and h["checks"]["prompt_leakage"]["pass"], f"{it['item_id']}: leakage check fails")
        if h["corrective_turn_used"]:
            _check(h["corrective_class"] == "format" and h["first_check"]["event"] == "deterministic_fail", f"{it['item_id']}: corrective")
            _check(bi.format_class_only(h["first_check"]["reasons"],
                                        packet_at_source(sid)[0]["checks_input"].get("allowed_descriptors") or []),
                   f"{it['item_id']}: first check is not format-class only")
            corrective.append(it["item_id"])
        http += [(sid, t["http_attempts"]) for t in h["turns"] if t["http_attempts"] > 1]
    _check(leakage_flags == RUN_FACTS["leakage_flags"], f"{leakage_flags} leakage flags")
    _check(tuple(sorted(corrective)) == FORMAT_CORRECTIVE_ITEMS, f"format corrective used on {sorted(corrective)}")

    log = (run / "agent.log").read_text(encoding="utf-8")
    _check(log == (src / "reports" / "litsynth_run2.log").read_text(encoding="utf-8"), "agent.log differs from reports/litsynth_run2.log")
    pl = parse_log(log)
    _check(pl["done"] == [f"items={RUN_FACTS['items']} pass={RUN_FACTS['deterministic_pass']} fail=0"], f"DONE lines {pl['done']}")
    by_seed = {it["review"]["history"][0]["seed_id"]: it["item_id"] for it in items}
    _check(sorted(by_seed[x] for x in pl["format_corrective_seeds"]) == list(FORMAT_CORRECTIVE_ITEMS), "log FORMAT_CORRECTIVE lines differ")
    _check(len(pl["retries"]) == len(HTTP_RETRIES) and all(sid == e[0] and why.startswith(e[1])
                                                           for (sid, why), e in zip(pl["retries"], HTTP_RETRIES)),
           f"log RETRY lines {pl['retries']}")
    _check(sorted(sid for sid, _ in http) == sorted(sid for sid, _ in HTTP_RETRIES) and all(n == 2 for _, n in http),
           f"turns with more than one HTTP attempt: {http}")
    for name in ("run0_rung1", "run1"):
        _check(_run(src, name).joinpath("agent.log").read_text(encoding="utf-8")
               == (src / "reports" / f"litsynth_{name}.log").read_text(encoding="utf-8"), f"{name} log differs from its report copy")
    return {"summary": s, "items": [{"item_id": it["item_id"], "seed_id": it["review"]["history"][0]["seed_id"],
                                     "use_case_level": it["use_case_level"], "packet_sha256": it["generation"]["inputs_sha256"]["packet"],
                                     "corrective_turn_used": it["review"]["history"][0]["corrective_turn_used"]}
                                    for it in sorted(items, key=lambda x: x["item_id"])],
            "format_corrective_items": sorted(corrective),
            "http_retries_recovered": [{"seed_id": sid, "reason": why[:60]} for sid, why in pl["retries"]],
            "log": {k: pl[k] for k in ("start_utc", "end_utc", "done")},
            "superseded": {name: superseded_facts(src, name) for name in ("run0_rung1", "run1")}}


def superseded_facts(src: Path, name: str) -> dict:
    run = _run(src, name)
    s = _load(run / "summary.json")
    return {"generator_version": s["generator_version"], "system_prompt_sha256": s["system_prompt_sha256"], "items": s["items"],
            "deterministic_pass": s["deterministic_pass"], "deterministic_fail": s["deterministic_fail"],
            "fail_reasons_by_kind": s["fail_reasons_by_kind"],
            "files": [{"path": p.relative_to(Path(src)).as_posix(), "sha256": sha256_file(p), "bytes": p.stat().st_size}
                      for p in sorted(run.rglob("*")) if p.is_file()]}


# --- reproduction of the post-checks -------------------------------------------------------------


def _agent():
    import importlib.util
    import sys
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "litcollect"))
    spec = importlib.util.spec_from_file_location("litsynth_agent", REPO_ROOT / AGENT_REL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _as_candidate(item: dict) -> dict:
    """The item as `synthesis_post_checks` saw it: `assemble` leaves review at llm_candidate with an empty history."""
    x = copy.deepcopy(item)
    x["review"] = {"status": "llm_candidate", "history": [], "kaiyuan_disposition": None, "mentor_disposition": None, "final_frozen": None}
    return x


def reproduce_checks(items: list[dict], columns: list[str] | None = None) -> dict:
    """Per item: (a) the item re-assembled by the pinned agent from its final raw response equals the delivered item
    (review aside); (b) `synthesis_post_checks` v2.2 on the delivered item and its v3a packet equals the recorded final check;
    (c) for a format-corrective item, the same on the first reply equals the recorded `first_check`. Raises on a difference."""
    agent, cols = _agent(), columns if columns is not None else bi.column_names()
    out = []
    for it in items:
        h = it["review"]["history"][0]
        packet, _ = packet_at_source(h["seed_id"])
        common = {k: h[k] for k in ("model", "prompt_hash", "generation_timestamp", "packet_sha256", "system_prompt_sha256")}
        obj = agent.extract_item(h["raw_response"])
        _check(len(h["raw_response"]) == h["raw_response_chars"], f"{it['item_id']}: raw response truncated")
        again, tagged = agent.assemble(obj, packet, common, cols)
        _check({**again, "review": None} == {**it, "review": None}, f"{it['item_id']}: re-assembled item differs from the delivered item")
        _check(tagged == h["reference_answer_tagged"], f"{it['item_id']}: re-assembled tagged answer differs")
        res = bi.synthesis_post_checks(_as_candidate(it), h["reference_answer_tagged"], packet["checks_input"], cols)
        same = {k: res[k] == h[k] for k in ("check_version", "reasons", "checks")} | {"pass": res["pass"] == (h["event"] == "deterministic_pass")}
        _check(all(same.values()), f"{it['item_id']}: post-checks differ from the recorded result: {same}")
        first = None
        if h["corrective_turn_used"]:
            fc = h["first_check"]
            f_item, f_tagged = agent.assemble(agent.extract_item(fc["raw_response"]), packet, common, cols)
            fr = bi.synthesis_post_checks(f_item, f_tagged, packet["checks_input"], cols)
            _check(f_tagged == fc["reference_answer_tagged"] and fr["reasons"] == fc["reasons"] and fr["checks"] == fc["checks"]
                   and not fr["pass"], f"{it['item_id']}: first-turn check differs from the recorded first_check")
            first = fr["reasons"]
        out.append({"item_id": it["item_id"], "pass": res["pass"], "reasons": res["reasons"], "first_check_reasons": first})
    return {"checks_reproduced": True, "check_version": bi.SYNTH_CHECK_VERSION, "items": out}


# --- copy and lifecycle ------------------------------------------------------------------------


def copy_run(src: Path) -> int:
    return sum(r2._copy(Path(src) / rel, ART / name) for rel, name in COPIED.items())


def excluded_files(src: Path) -> list[dict]:
    return [{"path": p.relative_to(Path(src)).as_posix(), "sha256": sha256_file(p), "bytes": p.stat().st_size}
            for p in sorted((_run(src) / "raw").rglob("*")) if p.is_file()]


def human_review_item(item: dict, at: str) -> dict:
    """The D-033 lifecycle step deterministic_pass -> human_review; nothing else changes."""
    _check(item["review"]["status"] == "deterministic_pass", f"{item['item_id']}: status {item['review']['status']}")
    x = copy.deepcopy(item)
    x["review"]["status"] = "human_review"
    x["review"]["kaiyuan_disposition"] = None
    x["review"]["mentor_disposition"] = None
    x["review"]["final_frozen"] = None
    x["review"]["history"].append({"event": "human_review", "from_status": "deterministic_pass", "decision": DECISION, "at": at,
                                   "by": "EXECUTOR (scripts/ingest_litsynth.py)", "note": HUMAN_REVIEW_NOTE})
    return x


def write_items(items: list[dict], at: str) -> list[dict]:
    """Write `items/<item_id>.json` (human_review) and validate each against schema v2 and the consistency rules."""
    schema, out = bi.load_schema(), []
    for it in sorted(items, key=lambda x: x["item_id"]):
        x = human_review_item(it, at)
        errs = bi.schema_errors(x, schema) + bi.consistency_errors(x)
        _check(not errs, f"{x['item_id']}: invalid after the lifecycle step: {errs}")
        path = ITEMS_DIR / f"{x['item_id']}.json"
        r2.write_json(path, x)
        out.append({"item_id": x["item_id"], "path": path.relative_to(ART).as_posix(), "sha256": sha256_file(path),
                    "status": x["review"]["status"], "schema_valid": True})
    return out


def _file_entry(path: Path) -> dict:
    return {"path": path.relative_to(ART).as_posix(), "sha256": sha256_file(path), "bytes": path.stat().st_size}


def manifest(facts: dict, reproduced: dict, written: list[dict], excluded: list[dict], ingested_at: str) -> dict:
    observed = facts["superseded"]
    return {
        "run": "run2", "diagnostic_id": RUN_ID, "decision": DECISION,
        "tarball": {"name": TARBALL_NAME, "sha256": TARBALL_SHA256},
        "generator": {"version": GENERATOR_VERSION, "agent_path": AGENT_REL, "agent_sha256": AGENT_SHA256,
                      "system_prompt_sha256": SYSTEM_PROMPT_SHA256, "format_corrective_template_sha256": FORMAT_CORRECTIVE_SHA256},
        "endpoint": {"endpoint_label": ENDPOINT_LABEL, "model": MODEL, "base_url": BASE_URL}, "budget": BUDGET,
        "source_commit": SOURCE_COMMIT,
        "packets": {"version": "synthpackets v3a", "path": PACKETS_REL, "at_commit": SOURCE_COMMIT,
                    "manifest_sha256": PACKETS_MANIFEST_SHA256},
        "counts": dict(RUN_FACTS), "items": facts["items"], "format_corrective_items": facts["format_corrective_items"],
        "http_retries_recovered": facts["http_retries_recovered"], "log": facts["log"],
        "items_sha256": ITEMS_SHA256, "summary_sha256": SUMMARY_SHA256,
        "checks_reproduced": reproduced["checks_reproduced"], "checks": reproduced,
        "item_schema": {"path": "data/metadata/benchmark/item_schema_v2.json", "sha256": bi.schema_sha256()},
        "lifecycle": {"status": "human_review", "from": "deterministic_pass", "rule": "D-033", "decision": DECISION,
                      "kaiyuan_disposition": None, "mentor_disposition": None, "final_frozen": None,
                      "note": "items/<item_id>.json = the delivered record + this step; items.jsonl is the run's file, byte-identical"},
        "superseded_runs": [dict(x, observed=observed[x["run"]]) for x in SUPERSEDED_RUNS],
        "files": [_file_entry(ART / name) for name in COPIED.values()],
        "items_ingested": written, "excluded_files": excluded,
        "ingested_at": ingested_at, "ingested_by": "EXECUTOR",
    }


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
