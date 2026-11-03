"""Synthesis run 3: verification, ingest, the human-review lifecycle step and the items index (mentor export package).

Run 3 is `litsynth_agent` v3.2 on Polaris (Sophia vLLM, `openai/gpt-oss-120b`, reasoning low, max_tokens 16000) over one
packet, `PK-SD2-TP1-00075` (BI-P2B-0010, rung 7) of packets v3b at source commit `157c96c` (DR-SEED-RANK-3a, D-054a).
`verify_source` re-derives every fact the work package states from the delivered tarball (hashes; agent, system-prompt
and format-corrective-template SHA-256; one item, `deterministic_pass`, no leakage flag, no corrective turn; endpoint and
budget; the packet equal to packets v3b at the source commit; the log equal to its report copy; `items.jsonl` equal to
the per-item file) and raises on any difference. `reproduce_checks` (run 2's, at the run-3 source commit) re-assembles
the item from its raw response with the pinned agent and re-runs post-checks v2.2 against its v3b packet.

`copy_run` copies `items.jsonl`, `summary.json` and the log into `artifacts/benchmark/items/run3/`; the prompt and raw
response are not copied (SHA-256 in `manifest.json`). The ingested record `items/BI-P2B-0010.json` is the delivered record
with the D-033 lifecycle step (deterministic_pass -> human_review).

`build_index` writes `artifacts/benchmark/items/index.json`: per pilot item the current version (run 2 for 0001--0009,
run 3 for 0010) and every ingested version; the run-2 BI-P2B-0010 stays listed as `superseded_by_run3`. No ingested file
of run 2 changes.

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from climrr import benchmark_items as bi
from climrr import litstatements_run2 as r2
from climrr import litsynth_run2 as s2
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

RUN_ID = "litsynth_run3"
DECISION = "D-056"  # run 3 (0010 only) is the regeneration D-056 / D-054a set up; no new decision
ITEMS_ROOT = REPO_ROOT / "artifacts" / "benchmark" / "items"
ART = ITEMS_ROOT / "run3"
ITEMS_DIR = ART / "items"
MANIFEST_PATH = ART / "manifest.json"
INDEX_PATH = ITEMS_ROOT / "index.json"

TARBALL_NAME = "litsynth_run3_evidence.tar.gz"
TARBALL_SHA256 = "10dc8a43c7fafcab5b53a097304c5f563ca4bcbbac574cf47efce5071f8ddc54"
ITEMS_SHA256 = "792eebe914fc71713293d6f56c065cee54962657b1730a755c253bf02387f896"
SUMMARY_SHA256 = "17c7138f6d93be77cc2da0e2a8a29e878d669b7969bd70c4ac442a6467994a2a"
SOURCE_COMMIT = "157c96cffbe28b95554210efb0e8d455f62dba43"
PACKETS_MANIFEST_SHA256 = "09ca030a5e4de913b1a6efb29943c84754de796a4a3987f300e72083e7f172c7"  # packets v3b
SEED_ID, ITEM_ID = "SD2-TP1-00075", "BI-P2B-0010"
PACKET_SHA256 = "9ec338d64e963521d86de13a0ab6c8a40dadad9b69ad5079694abf3b685379ee"
RUN_FACTS = {"items": 1, "deterministic_pass": 1, "deterministic_fail": 0, "leakage_flags": 0, "corrective_retry_used": 0,
             "format_corrective_used": 0, "format_corrective_pass": 0}
COPIED = {"litsynth/run3/items.jsonl": "items.jsonl", "litsynth/run3/summary.json": "summary.json",
          "litsynth/run3/agent.log": "agent.log"}
HUMAN_REVIEW_NOTE = ("entered human review (D-033 lifecycle; D-056): run 3 regenerates BI-P2B-0010 on packets v3b (D-054a); "
                     "Kaiyuan in artifacts/benchmark/review/P2b_items_review_v2.xlsx, then the mentor; edits are recorded in "
                     "review.final_frozen")
INGEST_BY = "EXECUTOR (scripts/ingest_litsynth_run3.py)"


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _run(src: Path) -> Path:
    return Path(src) / "litsynth" / "run3"


def read_item_files(src: Path) -> list[dict]:
    run = _run(src)
    return [s2._load(run / "items" / f"{it['review']['history'][0]['seed_id']}.json") for it in s2.read_items(run / "items.jsonl")]


def verify_source(src: Path) -> dict:
    """Every run-3 fact the work package states, re-derived from the delivered files. Raises on any difference."""
    src, run = Path(src), _run(src)
    _check(sha256_file(run / "items.jsonl") == ITEMS_SHA256, "items.jsonl differs from its stated SHA-256")
    _check(sha256_file(run / "summary.json") == SUMMARY_SHA256, "summary.json differs from its stated SHA-256")
    _check(sha256_file(REPO_ROOT / s2.AGENT_REL) == s2.AGENT_SHA256, f"{s2.AGENT_REL} differs from the pinned v3.2 SHA-256")
    _check(hashlib.sha256(s2.git_blob(SOURCE_COMMIT, s2.AGENT_REL)).hexdigest() == s2.AGENT_SHA256,
           f"{s2.AGENT_REL} at the source commit differs from the pinned SHA-256")
    _check(hashlib.sha256(s2.git_blob(SOURCE_COMMIT, f"{s2.PACKETS_REL}/manifest.json")).hexdigest() == PACKETS_MANIFEST_SHA256,
           "the packet manifest at the source commit is not packets v3b")
    s = s2._load(run / "summary.json")
    for k, v in (("generator_version", s2.GENERATOR_VERSION), ("endpoint_label", s2.ENDPOINT_LABEL), ("model", s2.MODEL),
                 ("base_url", s2.BASE_URL), ("reasoning_effort", s2.BUDGET["reasoning_effort"]), ("max_tokens", s2.BUDGET["max_tokens"]),
                 ("system_prompt_sha256", s2.SYSTEM_PROMPT_SHA256), ("format_corrective_prompt_sha256", s2.FORMAT_CORRECTIVE_SHA256),
                 ("items", 1), ("deterministic_pass", 1), ("deterministic_fail", 0), ("fail_reasons_by_kind", {}),
                 ("corrective_retry_used", 0), ("format_corrective_used", 0), ("format_corrective_pass", 0),
                 ("reasoning_effort_not_applied", 0), ("finish_reasons", {"stop": 1}), ("by_level", {"7": 1})):
        _check(s.get(k) == v, f"summary {k} = {s.get(k)!r}, expected {v!r}")

    items = s2.read_items(run / "items.jsonl")
    _check(len(items) == 1, f"{len(items)} items")
    _check(sorted(p.name for p in (run / "items").glob("*.json")) == [f"{SEED_ID}.json"], "item files")
    it = items[0]
    h = it["review"]["history"][0]
    _check(s2._load(run / "items" / f"{SEED_ID}.json") == it, "the per-item file differs from its items.jsonl line")
    _check(h["seed_id"] == SEED_ID and it["item_id"] == ITEM_ID and it["use_case_level"] == 7, f"item {it['item_id']} / {h['seed_id']}")
    _check(it["review"]["status"] == "deterministic_pass" and h["event"] == "deterministic_pass" and h["reasons"] == [],
           f"status {it['review']['status']}")
    _check(h["check_version"] == bi.SYNTH_CHECK_VERSION, f"checks {h['check_version']}")
    _, pk_sha = s2.packet_at_source(SEED_ID, SOURCE_COMMIT)
    _check(h["packet_sha256"] == it["generation"]["inputs_sha256"]["packet"] == pk_sha == PACKET_SHA256, "packet SHA-256 is not packets v3b")
    for k, v in (("generator_version", s2.GENERATOR_VERSION), ("endpoint_label", s2.ENDPOINT_LABEL), ("model", s2.MODEL),
                 ("base_url", s2.BASE_URL), ("source_commit", SOURCE_COMMIT), ("reasoning_effort_applied", True),
                 ("system_prompt_sha256", s2.SYSTEM_PROMPT_SHA256), ("finish_reason", "stop"), ("corrective_retry_used", False),
                 ("corrective_turn_used", False), *s2.BUDGET.items()):
        _check(h.get(k) == v, f"{k} = {h.get(k)!r}, expected {v!r}")
    lk = it["source_leakage_check"]
    _check(lk["pass"] and not lk["flags"] and h["checks"]["prompt_leakage"]["pass"] and not h["checks"]["prompt_leakage"]["flags"],
           "leakage check fails")
    _check(all(t["http_attempts"] == 1 for t in h["turns"]), "an HTTP retry")

    log = (run / "agent.log").read_text(encoding="utf-8")
    _check(log == (src / "reports" / "litsynth_run3.log").read_text(encoding="utf-8"), "agent.log differs from reports/litsynth_run3.log")
    pl = s2.parse_log(log)
    _check(pl["done"] == ["items=1 pass=1 fail=0"] and not pl["format_corrective_seeds"] and not pl["retries"], f"log {pl['done']}")
    _check(len(pl["item_lines"]) == 1 and f"{SEED_ID} level=7 status=deterministic_pass" in pl["item_lines"][0], "log item line")
    return {"summary": s, "items": [{"item_id": it["item_id"], "seed_id": SEED_ID, "use_case_level": 7, "packet_sha256": h["packet_sha256"],
                                     "corrective_turn_used": False}],
            "log": {k: pl[k] for k in ("start_utc", "end_utc", "done")}}


def copy_run(src: Path) -> int:
    return sum(r2._copy(Path(src) / rel, ART / name) for rel, name in COPIED.items())


def excluded_files(src: Path) -> list[dict]:
    return [{"path": p.relative_to(Path(src)).as_posix(), "sha256": sha256_file(p), "bytes": p.stat().st_size}
            for p in sorted((_run(src) / "raw").rglob("*")) if p.is_file()]


def write_items(items: list[dict], at: str) -> list[dict]:
    schema, out = bi.load_schema(), []
    for it in items:
        x = s2.human_review_item(it, at, HUMAN_REVIEW_NOTE, INGEST_BY)
        errs = bi.schema_errors(x, schema) + bi.consistency_errors(x)
        _check(not errs, f"{x['item_id']}: invalid after the lifecycle step: {errs}")
        path = ITEMS_DIR / f"{x['item_id']}.json"
        r2.write_json(path, x)
        out.append({"item_id": x["item_id"], "path": path.relative_to(ART).as_posix(), "sha256": sha256_file(path),
                    "status": x["review"]["status"], "schema_valid": True})
    return out


def manifest(facts: dict, reproduced: dict, written: list[dict], excluded: list[dict], ingested_at: str) -> dict:
    return {
        "run": "run3", "diagnostic_id": RUN_ID, "decision": DECISION,
        "tarball": {"name": TARBALL_NAME, "sha256": TARBALL_SHA256},
        "generator": {"version": s2.GENERATOR_VERSION, "agent_path": s2.AGENT_REL, "agent_sha256": s2.AGENT_SHA256,
                      "system_prompt_sha256": s2.SYSTEM_PROMPT_SHA256, "format_corrective_template_sha256": s2.FORMAT_CORRECTIVE_SHA256},
        "endpoint": {"endpoint_label": s2.ENDPOINT_LABEL, "model": s2.MODEL, "base_url": s2.BASE_URL}, "budget": s2.BUDGET,
        "source_commit": SOURCE_COMMIT,
        "packets": {"version": "synthpackets v3b", "path": s2.PACKETS_REL, "at_commit": SOURCE_COMMIT,
                    "manifest_sha256": PACKETS_MANIFEST_SHA256, "only": f"PK-{SEED_ID}.json", "packet_sha256": PACKET_SHA256},
        "counts": dict(RUN_FACTS), "items": facts["items"], "log": facts["log"],
        "items_sha256": ITEMS_SHA256, "summary_sha256": SUMMARY_SHA256,
        "checks_reproduced": reproduced["checks_reproduced"], "checks": reproduced,
        "item_schema": {"path": "data/metadata/benchmark/item_schema_v2.json", "sha256": bi.schema_sha256()},
        "lifecycle": {"status": "human_review", "from": "deterministic_pass", "rule": "D-033", "decision": DECISION,
                      "kaiyuan_disposition": None, "mentor_disposition": None, "final_frozen": None,
                      "note": "items/<item_id>.json = the delivered record + this step; items.jsonl is the run's file, byte-identical"},
        "supersedes": [{"item_id": ITEM_ID, "run": "run2", "path": "run2/items/BI-P2B-0010.json",
                        "index_status": "superseded_by_run3", "note": "the run-2 file is unchanged; the index records the supersession"}],
        "files": [{"path": n, "sha256": sha256_file(ART / n), "bytes": (ART / n).stat().st_size} for n in COPIED.values()],
        "items_ingested": written, "excluded_files": excluded,
        "ingested_at": ingested_at, "ingested_by": "EXECUTOR",
    }


# --- the items index ---------------------------------------------------------------------------------------------


def _versions(run: str, man_path: Path) -> list[dict]:
    man = json.loads(man_path.read_text(encoding="utf-8"))
    out = []
    for x in man["items_ingested"]:
        path = man_path.parent / x["path"]
        _check(sha256_file(path) == x["sha256"], f"{path} differs from its manifest hash")
        it = json.loads(path.read_text(encoding="utf-8"))
        h = it["review"]["history"][0]
        out.append({"item_id": x["item_id"], "run": run, "path": path.relative_to(ITEMS_ROOT).as_posix(), "sha256": x["sha256"],
                    "status": it["review"]["status"], "generator_version": h["generator_version"], "source_commit": h["source_commit"],
                    "packet_sha256": h["packet_sha256"], "manifest": man_path.relative_to(ITEMS_ROOT).as_posix(),
                    "manifest_sha256": sha256_file(man_path)})
    return out


def index() -> dict:
    """Per item id: every ingested version, oldest run first; the newest is `current`, any earlier one is
    `superseded_by_<newer run>`."""
    versions = _versions("run2", s2.MANIFEST_PATH) + _versions("run3", MANIFEST_PATH)
    by_id: dict = {}
    for v in versions:
        by_id.setdefault(v["item_id"], []).append(v)
    items = []
    for iid in sorted(by_id):
        vs = sorted(by_id[iid], key=lambda v: v["run"])
        for i, v in enumerate(vs):
            v["index_status"] = "current" if i == len(vs) - 1 else f"superseded_by_{vs[i + 1]['run']}"
        items.append({"item_id": iid, "current": {k: vs[-1][k] for k in ("run", "path", "sha256", "status")}, "versions": vs})
    return {"index": "pilot P2b items", "decision": DECISION,
            "note": "current = the version reviewed and exported; a superseded version's file is unchanged and stays ingested",
            "counts": {"items": len(items), "current_by_run": {r: sum(x["current"]["run"] == r for x in items) for r in ("run2", "run3")},
                       "superseded": sum(len(x["versions"]) - 1 for x in items)},
            "items": items}


def current_items() -> list[dict]:
    """The current version of every pilot item, in id order, each checked against its index hash."""
    idx = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    out = []
    for x in idx["items"]:
        path = ITEMS_ROOT / x["current"]["path"]
        _check(sha256_file(path) == x["current"]["sha256"], f"{path} differs from the index hash")
        out.append(json.loads(path.read_text(encoding="utf-8")))
    return out
