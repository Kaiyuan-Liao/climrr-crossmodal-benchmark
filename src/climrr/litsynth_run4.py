"""Synthesis run 4 and polish run 1: verification, ingest and the human-review lifecycle step (work package P3b, section A).

**Synthesis run 4** is `litsynth_agent` v4 on Polaris (Sophia vLLM, `openai/gpt-oss-120b`, reasoning low, max_tokens 16000)
over the seven packets v4a at source commit `2601920` (P3a, P3a hotfix D-053b). **Polish run 1** is `litpolish_agent` v1
(checks `polish_checks` v1a, synonyms v1) over run 4's output at the same commit. Both arrive in one tarball.

`verify_source` re-derives every fact the work package states from the delivered files (hashes; agent, system-prompt and
corrective-template SHA-256 at the source commit; 7 items, 6 `deterministic_pass`, 1 `rejected_pre_review` = BI-P3-0007
with its five reasons; the format corrective turn on exactly BI-P3-0003 and 0004; endpoint and budget; every packet equal
to packets v4a at the source commit; the polish summary --- 6 items, 0 polished, 6 `polish_rejected`, mechanism 12 /
numbers 2, 0007 skipped; each polish item = its run-4 item + one `polish` event naming that item's SHA-256; the logs equal
to their report copies) and raises on any difference.

`reproduce_synthesis` re-assembles each item from its final raw response with the pinned v4 agent (loaded from its bytes
at the source commit) and re-runs `synthesis_post_checks` v3 against its v4a packet; the format-corrective first turns
likewise. `reproduce_polish` re-extracts each rewrite with the pinned v1 polish agent and re-runs `polish_checks.invariance`
(v1a, synonyms v1) on it. Both must equal what the runs recorded (`checks_reproduced`). `replay_polish_v2` runs
`polish_checks.invariance_v2` (checks v2, synonyms v2, DR-DESC-1 v4, plain language v1a) on the same rewrites as a
diagnostic only: no status changes.

`copy_runs` copies `items.jsonl`, `summary.json` and the log of run 4 into `artifacts/benchmark/items/run4/`, and
`polished.jsonl`, `summary.json` and the log of polish run 1 into `artifacts/benchmark/polish/run1/`; prompts, raw
responses and the polish per-item files are not copied (SHA-256 in the manifests). `items/<item_id>.json`: for the six
passing items the polish-run record (run-4 item + the `polish` event; text unchanged, every rewrite rejected) with the D-033
lifecycle step deterministic_pass -> human_review; for BI-P3-0007 the run-4 record as delivered (`rejected_pre_review`).

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

from climrr import benchmark_items as bi
from climrr import litstatements_run2 as r2
from climrr import litsynth_run2 as s2
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

RUN_ID, POLISH_RUN_ID = "litsynth_run4", "litpolish_run1"
DECISION = "D-053b"                     # packets v4a and the seven-item set (on D-059 -- D-065); no new decision for the run
ITEMS_ROOT = REPO_ROOT / "artifacts" / "benchmark" / "items"
ART = ITEMS_ROOT / "run4"
ITEMS_DIR = ART / "items"
MANIFEST_PATH = ART / "manifest.json"
POLISH_ART = REPO_ROOT / "artifacts" / "benchmark" / "polish" / "run1"
POLISH_MANIFEST_PATH = POLISH_ART / "manifest.json"

TARBALL_NAME = "litsynth_run4_polish_run1_evidence.tar.gz"
TARBALL_SHA256 = "ebd502ac7aaea764a86a40501d5b5347d8372164f9b17a28d0299ebf55fb7168"
ITEMS_SHA256 = "e333099bfacffdcd53f2f6cdd428ac4f5314b5689c3eabb962fbc7a1c74928c7"
SUMMARY_SHA256 = "cf9b71ac34a9d4e237d30f7ce3c0ffab2c6f11c485c0fcaed93fa3e1c1a4b7ea"
POLISH_SUMMARY_SHA256 = "53eafe9c63819502ba32a31eed95c0bf76417c2e16a10e662fca96b69693edce"
POLISHED_SHA256 = "7812d7fd9b30c49e761f6e3ea2efa854e292e0eaf32e9a540a2592b051d8d424"
SOURCE_COMMIT = "26019206581366185a59b4113824a7c62755cec3"

AGENT_REL = "scripts/litcollect/litsynth_agent.py"
AGENT_SHA256 = "8a8ca836a6cd6469ead6948305f721b9e0d6e7063770350f4c89810a3000fee1"           # litsynth_agent v4
SYSTEM_PROMPT_SHA256 = "33d387fe5098806cac70822194dc34804d80fc98cdb69ec850c919f88993db05"
CORRECTIVE_SHA256 = "256db051b3ddfa93d893e4573a2e818ecd4623d96ddac0aaebdba932c6e2a01a"
FORMAT_CORRECTIVE_SHA256 = "053037521584043f258b74c3e96fc1d5bf6e93f76d15b1c7a4d5229a041a239f"
GENERATOR_VERSION = "litsynth_agent v4"
PACKETS_REL = "artifacts/benchmark/synth_packets_v4a"
PACKETS_MANIFEST_SHA256 = "3119c0b3d29b12364519b3262da2b8c791a6e70ccda814bdb0bd9b5b92d3f687"   # packets v4a

POLISH_AGENT_REL = "scripts/litcollect/litpolish_agent.py"
POLISH_AGENT_SHA256 = "901e39540885b461fccb666803eb5d088ade229dc75253bc5901f3937a9f10dc"    # litpolish_agent v1
POLISH_SYSTEM_PROMPT_SHA256 = "42537289f4ee83a532dd6af22e9c6af1c72bb248c17bae640b2fde24ba6b43b9"
POLISH_CORRECTIVE_SHA256 = "b12f5fc80f7ad62b20c122f7cb28c5174a9c0c48888acdcd609dbab63f722bf8"
POLISH_GENERATOR_VERSION = "litpolish_agent v1"
POLISH_SYNONYMS_V1_SHA256 = "8236d5eb2444cfacbbbbf902499714f84902c3f15978683d02b53459f5dca549"

ENDPOINT_LABEL, MODEL, BASE_URL = "sophia_vllm", "openai/gpt-oss-120b", r2.BASE_URL
BUDGET = {"reasoning_effort": "low", "max_tokens": 16000, "temperature": 0}
RUN_FACTS = {"items": 7, "deterministic_pass": 6, "deterministic_fail": 1, "leakage_flags": 0, "corrective_retry_used": 0,
             "format_corrective_used": 2, "format_corrective_pass": 2}
FORMAT_CORRECTIVE_ITEMS = ("BI-P3-0003", "BI-P3-0004")
REJECTED = {"BI-P3-0007": [
    "rubric.acceptable_variants: number-word 'three' does not trace to an allowed descriptor in the packet",
    "rubric.optional_points: exact_value_in_graded_text 31.4 (exact values belong to provenance)",
    "rubric.optional_points: exact_value_in_graded_text 33.6 (exact values belong to provenance)",
    "rubric.disallowed_claims: generality (D-060/D-062): 'a single study' in graded text",
    "literature_interpretation: fire-weather wording (an FWI is never fire occurrence): 'fires' in graded text"]}
ITEM_IDS = {"SD2-TP1-00071": "BI-P3-0001", "SD2-TP1-00271": "BI-P3-0002", "SD2-TP1-00460": "BI-P3-0003",
            "SD2-TP1-00589": "BI-P3-0004", "SD2-TP1-02785": "BI-P3-0005", "SD2-TP1-01463": "BI-P3-0007",
            "SD2-TP1-01654": "BI-P3-0008"}
POLISH_FACTS = {"items": 6, "polished": 0, "polish_rejected": 6, "polish_parse_failed": 0,
                "reasons_by_kind": {"mechanism": 12, "numbers": 2}, "skipped_not_deterministic_pass": ["BI-P3-0007"]}
COPIED = {"litsynth/run4/items.jsonl": "items.jsonl", "litsynth/run4/summary.json": "summary.json",
          "litsynth/run4/agent.log": "agent.log"}
POLISH_COPIED = {"litpolish/run1/polished.jsonl": "polished.jsonl", "litpolish/run1/summary.json": "summary.json",
                 "litpolish/run1/agent.log": "agent.log"}
HUMAN_REVIEW_NOTE = ("entered human review (D-033 lifecycle): synthesis run 4 (agent v4, packets v4a); polish run 1 rejected the "
                     "rewrite, so the text is the synthesis text (pre_polish in the polish event); superseded for the mentor sheet "
                     "when synthesis run 5 (agent v4.1, packets v4b) is ingested")
INGEST_BY = "EXECUTOR (scripts/ingest_litsynth_run4.py)"


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _run(src: Path) -> Path:
    return Path(src) / "litsynth" / "run4"


def _prun(src: Path) -> Path:
    return Path(src) / "litpolish" / "run1"


def load_agent_at(commit: str, rel: str, sha256: str, name: str):
    """The agent file `rel` at `commit` as a module, after checking its SHA-256; sibling imports resolve from
    scripts/litcollect and `climrr` from the working tree."""
    blob = s2.git_blob(commit, rel)
    _check(hashlib.sha256(blob).hexdigest() == sha256, f"{rel} at {commit[:7]} differs from the pinned SHA-256 {sha256}")
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "litcollect"))
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / Path(rel).name
        path.write_bytes(blob)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    return mod


def materialize_agents() -> Path:
    """<tmp>/scripts/litcollect/{litsynth_agent.py, litpolish_agent.py} = the v4 and v1 bytes at the source commit (the
    working tree carries v4.1 and v1.1 since work package P3b); the sibling tools and <tmp>/src link to the repository's.
    Returns the tools directory."""
    root = Path(tempfile.mkdtemp(prefix="litsynth_run4_agents_"))
    tools = root / "scripts" / "litcollect"
    tools.mkdir(parents=True)
    for rel, sha in ((AGENT_REL, AGENT_SHA256), (POLISH_AGENT_REL, POLISH_AGENT_SHA256)):
        blob = s2.git_blob(SOURCE_COMMIT, rel)
        _check(hashlib.sha256(blob).hexdigest() == sha, f"{rel} at {SOURCE_COMMIT[:7]} differs from {sha}")
        (tools / Path(rel).name).write_bytes(blob)
    for name in ("litstatement_agent.py", "litgroup_agent.py"):
        (tools / name).symlink_to(REPO_ROOT / "scripts" / "litcollect" / name)
    (root / "src").symlink_to(REPO_ROOT / "src")
    return tools


def packet_at_source(seed_id: str) -> tuple[dict, str]:
    blob = s2.git_blob(SOURCE_COMMIT, f"{PACKETS_REL}/PK-{seed_id}.json")
    return json.loads(blob.decode("utf-8")), hashlib.sha256(blob).hexdigest()


def read_item_files(src: Path) -> list[dict]:
    """The run-4 per-item files in `items.jsonl` order (they keep the agent's key order)."""
    run = _run(src)
    return [s2._load(run / "items" / f"{it['review']['history'][0]['seed_id']}.json") for it in s2.read_items(run / "items.jsonl")]


def read_polish_items(src: Path) -> dict:
    """{seed_id: polish-run item} for every polish item file."""
    return {p.stem: s2._load(p) for p in sorted((_prun(src) / "items").glob("*.json"))}


def _summary_facts(s: dict, facts: tuple) -> None:
    for k, v in facts:
        _check(s.get(k) == v, f"summary {k} = {s.get(k)!r}, expected {v!r}")


def verify_source(src: Path) -> dict:
    """Every run-4 and polish-run-1 fact the work package states, re-derived from the delivered files."""
    src, run, prun = Path(src), _run(src), _prun(src)
    _check(sha256_file(run / "items.jsonl") == ITEMS_SHA256, "items.jsonl differs from its stated SHA-256")
    _check(sha256_file(run / "summary.json") == SUMMARY_SHA256, "litsynth summary.json differs from its pinned SHA-256")
    _check(sha256_file(prun / "summary.json") == POLISH_SUMMARY_SHA256, "litpolish summary.json differs from its stated SHA-256")
    _check(sha256_file(prun / "polished.jsonl") == POLISHED_SHA256, "polished.jsonl differs from its pinned SHA-256")
    for rel, sha in ((AGENT_REL, AGENT_SHA256), (POLISH_AGENT_REL, POLISH_AGENT_SHA256)):
        _check(hashlib.sha256(s2.git_blob(SOURCE_COMMIT, rel)).hexdigest() == sha, f"{rel} at the source commit differs from {sha}")
    _check(hashlib.sha256(s2.git_blob(SOURCE_COMMIT, f"{PACKETS_REL}/manifest.json")).hexdigest() == PACKETS_MANIFEST_SHA256,
           "the packet manifest at the source commit is not packets v4a")
    _check(hashlib.sha256(s2.git_blob(SOURCE_COMMIT, "data/metadata/benchmark/polish_synonyms_v1.yaml")).hexdigest()
           == POLISH_SYNONYMS_V1_SHA256, "polish synonyms v1 at the source commit differ from the pin")

    s = s2._load(run / "summary.json")
    _summary_facts(s, (("generator_version", GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL),
                       ("base_url", BASE_URL), ("reasoning_effort", BUDGET["reasoning_effort"]), ("max_tokens", BUDGET["max_tokens"]),
                       ("system_prompt_sha256", SYSTEM_PROMPT_SHA256), ("corrective_prompt_sha256", CORRECTIVE_SHA256),
                       ("format_corrective_prompt_sha256", FORMAT_CORRECTIVE_SHA256), ("items", 7), ("deterministic_pass", 6),
                       ("deterministic_fail", 1), ("corrective_retry_used", 0), ("format_corrective_used", 2),
                       ("format_corrective_pass", 2), ("reasoning_effort_not_applied", 0), ("finish_reasons", {"stop": 7}),
                       ("by_level", {"3": 6, "4": 1}), ("check_version", bi.SYNTH_CHECK_VERSION_V3), ("hedge_by_strength_flags", 0),
                       ("fail_reasons_by_kind", {"literature_interpretation": 1, "rubric.acceptable_variants": 1,
                                                 "rubric.disallowed_claims": 1, "rubric.optional_points": 2})))
    items = s2.read_items(run / "items.jsonl")
    v4a = json.loads(s2.git_blob(SOURCE_COMMIT, f"{PACKETS_REL}/manifest.json"))
    v4a_sha = {x["seed_id"]: x["sha256"] for x in v4a["packets"]}
    _check(sorted(p.stem for p in (run / "items").glob("*.json")) == sorted(v4a_sha) == sorted(ITEM_IDS), "item files")
    corrective, leakage_flags = [], 0
    for it in items:
        h = it["review"]["history"][0]
        sid, iid = h["seed_id"], it["item_id"]
        _check(s2._load(run / "items" / f"{sid}.json") == it, f"{sid}: the per-item file differs from its items.jsonl line")
        _check(iid == ITEM_IDS[sid], f"{sid}: item id {iid}")
        want = REJECTED.get(iid)
        if want is None:
            _check(it["review"]["status"] == "deterministic_pass" and h["event"] == "deterministic_pass" and h["reasons"] == [],
                   f"{iid}: status {it['review']['status']}")
        else:
            _check(it["review"]["status"] == "rejected_pre_review" and h["event"] == "deterministic_fail" and h["reasons"] == want,
                   f"{iid}: status {it['review']['status']}, reasons {h['reasons']}")
        _check(h["check_version"] == bi.SYNTH_CHECK_VERSION_V3, f"{iid}: checks {h['check_version']}")
        _, pk_sha = packet_at_source(sid)
        _check(h["packet_sha256"] == it["generation"]["inputs_sha256"]["packet"] == pk_sha == v4a_sha[sid], f"{iid}: not packets v4a")
        for k, v in (("generator_version", GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL), ("base_url", BASE_URL),
                     ("source_commit", SOURCE_COMMIT), ("reasoning_effort_applied", True), ("system_prompt_sha256", SYSTEM_PROMPT_SHA256),
                     ("finish_reason", "stop"), ("corrective_retry_used", False), *BUDGET.items()):
            _check(h.get(k) == v, f"{iid}: {k} = {h.get(k)!r}, expected {v!r}")
        lk = it["source_leakage_check"]
        leakage_flags += len(lk["flags"]) + len(h["checks"]["prompt_leakage"]["flags"])
        if h["corrective_turn_used"]:
            _check(h["corrective_class"] == "format" and h["first_check"]["event"] == "deterministic_fail", f"{iid}: corrective")
            _check(bi.format_class_only(h["first_check"]["reasons"], packet_at_source(sid)[0]["checks_input"]["allowed_descriptors"]),
                   f"{iid}: first check is not format-class only")
            corrective.append(iid)
        _check(all(t["http_attempts"] == 1 for t in h["turns"]), f"{iid}: an HTTP retry")
    _check(leakage_flags == 0, f"{leakage_flags} leakage flags")
    _check(tuple(sorted(corrective)) == FORMAT_CORRECTIVE_ITEMS, f"format corrective used on {sorted(corrective)}")
    log = (run / "agent.log").read_text(encoding="utf-8")
    _check(log == (src / "reports" / "litsynth_run4.log").read_text(encoding="utf-8"), "agent.log differs from reports/litsynth_run4.log")
    pl = s2.parse_log(log)
    _check(pl["done"] == ["items=7 pass=6 fail=1"] and not pl["retries"], f"log {pl['done']}")
    _check(sorted(ITEM_IDS[x] for x in pl["format_corrective_seeds"]) == list(FORMAT_CORRECTIVE_ITEMS), "log FORMAT_CORRECTIVE lines")

    ps = s2._load(prun / "summary.json")
    _summary_facts(ps, (("generator_version", POLISH_GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL),
                        ("base_url", BASE_URL), ("reasoning_effort", "low"), ("max_tokens", 16000),
                        ("system_prompt_sha256", POLISH_SYSTEM_PROMPT_SHA256), ("corrective_prompt_sha256", POLISH_CORRECTIVE_SHA256),
                        ("check_version", "polish_checks v1a"), *POLISH_FACTS.items()))
    by_seed = {it["review"]["history"][0]["seed_id"]: it for it in items}
    pitems = read_polish_items(src)
    recs = s2.read_items(prun / "polished.jsonl")
    passing = sorted(sid for sid, it in by_seed.items() if it["review"]["status"] == "deterministic_pass")
    _check(sorted(pitems) == passing == sorted(r["seed_id"] for r in recs), "polish items are not the six passing items")
    for r in recs:
        sid = r["seed_id"]
        p, orig = pitems[sid], by_seed[sid]
        ev = p["review"]["history"][-1]
        base = copy.deepcopy(p)
        base["review"]["history"] = base["review"]["history"][:-1]
        _check(base == s2._load(run / "items" / f"{sid}.json"), f"{sid}: the polish item is not the run-4 item + one event")
        _check(ev["event"] == "polish" and ev["status"] == r["status"] == "polish_rejected", f"{sid}: polish status {ev.get('status')}")
        _check(ev["item_sha256"] == sha256_file(run / "items" / f"{sid}.json"), f"{sid}: polish event names another item")
        _check(r["item_id"] == orig["item_id"] and r["pre_polish"] == ev["pre_polish"] ==
               {"prompt": orig["prompt"], "answer": orig["reference_answer"]["integrated"]}, f"{sid}: pre_polish")
        _check(r["polished"] == ev["rewrite"] and r["reasons"] == ev["reasons"] and r["checks"] == ev["checks"], f"{sid}: record")
        for k, v in (("generator_version", POLISH_GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL),
                     ("base_url", BASE_URL), ("source_commit", SOURCE_COMMIT), ("reasoning_effort_applied", True),
                     ("system_prompt_sha256", POLISH_SYSTEM_PROMPT_SHA256), ("check_version", "polish_checks v1a"),
                     ("corrective_retry_used", False), ("finish_reason", "stop"), *BUDGET.items()):
            _check(ev.get(k) == v, f"{sid}: polish {k} = {ev.get(k)!r}, expected {v!r}")
    plog = (prun / "agent.log").read_text(encoding="utf-8")
    _check(plog == (src / "reports" / "litpolish_run1.log").read_text(encoding="utf-8"), "polish agent.log differs from its report copy")
    _check(" DONE items=6 polished=0 rejected=6 parse_failed=0" in plog, "polish log DONE line")
    return {"summary": s, "polish_summary": ps,
            "items": [{"item_id": it["item_id"], "seed_id": it["review"]["history"][0]["seed_id"], "use_case_level": it["use_case_level"],
                       "status": it["review"]["status"], "packet_sha256": it["generation"]["inputs_sha256"]["packet"],
                       "corrective_turn_used": it["review"]["history"][0]["corrective_turn_used"]}
                      for it in sorted(items, key=lambda x: x["item_id"])],
            "format_corrective_items": sorted(corrective), "rejected": REJECTED,
            "log": {k: pl[k] for k in ("start_utc", "end_utc", "done")},
            "polish_log": {"start_utc": next(ln.split()[0] for ln in plog.splitlines() if " START " in ln),
                           "end_utc": next(ln.split()[0] for ln in reversed(plog.splitlines()) if " DONE " in ln)}}


# --- reproduction ------------------------------------------------------------------------------------------------


def reproduce_synthesis(items: list[dict], columns: list[str] | None = None) -> dict:
    """Per item: re-assembled by the pinned v4 agent from its final raw response = the delivered item (review aside);
    post-checks v3 on it against its v4a packet = the recorded check; a format-corrective first turn likewise."""
    agent = load_agent_at(SOURCE_COMMIT, AGENT_REL, AGENT_SHA256, "litsynth_agent_v4")
    cols = columns if columns is not None else bi.column_names()
    out = []
    for it in items:
        h = it["review"]["history"][0]
        packet, _ = packet_at_source(h["seed_id"])
        common = {k: h[k] for k in ("model", "prompt_hash", "generation_timestamp", "packet_sha256", "system_prompt_sha256")}
        _check(len(h["raw_response"]) == h["raw_response_chars"], f"{it['item_id']}: raw response truncated")
        again, tagged = agent.assemble(agent.extract_item(h["raw_response"]), packet, common, cols)
        _check({**again, "review": None} == {**it, "review": None}, f"{it['item_id']}: re-assembled item differs")
        _check(tagged == h["reference_answer_tagged"], f"{it['item_id']}: re-assembled tagged answer differs")
        res = bi.synthesis_post_checks(s2._as_candidate(it), tagged, packet["checks_input"], cols, check_version=bi.SYNTH_CHECK_VERSION_V3)
        same = {k: res[k] == h[k] for k in ("check_version", "reasons", "checks")} | {"pass": res["pass"] == (h["event"] == "deterministic_pass")}
        _check(all(same.values()), f"{it['item_id']}: post-checks differ from the recorded result: {same}")
        first = None
        if h["corrective_turn_used"]:
            fc = h["first_check"]
            f_item, f_tagged = agent.assemble(agent.extract_item(fc["raw_response"]), packet, common, cols)
            fr = bi.synthesis_post_checks(f_item, f_tagged, packet["checks_input"], cols, check_version=bi.SYNTH_CHECK_VERSION_V3)
            _check(f_tagged == fc["reference_answer_tagged"] and fr["reasons"] == fc["reasons"] and fr["checks"] == fc["checks"]
                   and not fr["pass"], f"{it['item_id']}: first-turn check differs from the recorded first_check")
            first = fr["reasons"]
        out.append({"item_id": it["item_id"], "pass": res["pass"], "reasons": res["reasons"], "first_check_reasons": first})
    return {"checks_reproduced": True, "check_version": bi.SYNTH_CHECK_VERSION_V3, "items": out}


def _cited(item: dict) -> list[dict]:
    rc = item["reference_components"]
    return [{"group_id": s["group_id"], "label": s["statement"]} for s in rc["literature_mechanisms"] + rc["literature_caveats"]]


def reproduce_polish(src: Path, columns: list[str] | None = None) -> dict:
    """Per polished record: the rewrite re-extracted by the pinned v1 polish agent from the raw response, and
    `polish_checks.invariance` (v1a, synonyms v1) on it, equal to what the run recorded."""
    from climrr import itemseeds as sd
    from climrr import polish_checks as pc

    agent = load_agent_at(SOURCE_COMMIT, POLISH_AGENT_REL, POLISH_AGENT_SHA256, "litpolish_agent_v1")
    cols = columns if columns is not None else bi.column_names()
    nca, syn = sd.nca_map(), pc.load_synonyms()
    _check(syn["sha256"] == POLISH_SYNONYMS_V1_SHA256, "polish synonyms v1 pin")
    pitems, out = read_polish_items(src), []
    for r in s2.read_items(_prun(src) / "polished.jsonl"):
        ev = pitems[r["seed_id"]]["review"]["history"][-1]
        _check(len(ev["raw_response"]) == ev["raw_response_chars"], f"{r['seed_id']}: raw response truncated")
        obj = agent.extract(ev["raw_response"])
        _check({"prompt": obj["prompt"], "answer": obj["answer"]} == r["polished"], f"{r['seed_id']}: re-extracted rewrite differs")
        res = pc.invariance(r["pre_polish"], r["polished"], agent.cited_labels(pitems[r["seed_id"]]), nca, syn, cols)
        _check(res["check_version"] == "polish_checks v1a" and res["reasons"] == r["reasons"] and res["checks"] == r["checks"]
               and not res["pass"], f"{r['seed_id']}: polish checks differ from the recorded result")
        out.append({"item_id": r["item_id"], "seed_id": r["seed_id"], "pass": res["pass"], "reasons": res["reasons"]})
    return {"checks_reproduced": True, "check_version": "polish_checks v1a", "synonyms_sha256": syn["sha256"], "items": out}


def replay_polish_v2(src: Path, columns: list[str] | None = None) -> dict:
    """Diagnostic: polish checks v2 on the run-1 rewrites (what v2 would have decided). No status changes."""
    from climrr import itemseeds as sd
    from climrr import pattern_descriptors as pd
    from climrr import plain_language as pl
    from climrr import polish_checks as pc

    cols = columns if columns is not None else bi.column_names()
    nca, syn, rules, plain = sd.nca_map(), pc.load_synonyms_v2(), pd.load_rules(pd.RULES_V4_PATH), pl.load(pl.PLAIN_V1A_PATH)
    pitems, out = read_polish_items(src), []
    for r in s2.read_items(_prun(src) / "polished.jsonl"):
        res = pc.invariance_v2(r["pre_polish"], r["polished"], _cited(pitems[r["seed_id"]]), nca, syn, rules, plain, cols)
        out.append({"item_id": r["item_id"], "pass": res["pass"], "reasons": res["reasons"]})
    return {"diagnostic": "polish checks v2 replayed on polish run 1 (no status changed)", "check_version": pc.VERSION_V2,
            "synonyms_sha256": syn["sha256"], "descriptor_rules_sha256": rules["sha256"], "plain_language_sha256": plain["sha256"],
            "items": out}


# --- copy, lifecycle, manifests ------------------------------------------------------------------------------------


def copy_runs(src: Path) -> int:
    return sum(r2._copy(Path(src) / rel, ART / name) for rel, name in COPIED.items()) + \
        sum(r2._copy(Path(src) / rel, POLISH_ART / name) for rel, name in POLISH_COPIED.items())


def excluded_files(root: Path, copied: dict) -> list[dict]:
    """Every delivered file under `root` that is not copied (prompts, raw responses, per-item files), with its SHA-256."""
    top = root.parents[1]
    return [{"path": p.relative_to(top).as_posix(), "sha256": sha256_file(p), "bytes": p.stat().st_size}
            for p in sorted(root.rglob("*")) if p.is_file() and p.relative_to(top).as_posix() not in copied]


def human_review_item(item: dict, at: str) -> dict:
    """The D-033 lifecycle step deterministic_pass -> human_review; nothing else changes."""
    _check(item["review"]["status"] == "deterministic_pass", f"{item['item_id']}: status {item['review']['status']}")
    x = copy.deepcopy(item)
    x["review"].update(status="human_review", kaiyuan_disposition=None, mentor_disposition=None, final_frozen=None)
    x["review"]["history"].append({"event": "human_review", "from_status": "deterministic_pass", "decision": "D-033", "at": at,
                                   "by": INGEST_BY, "note": HUMAN_REVIEW_NOTE})
    return x


def write_items(src: Path, items: list[dict], at: str) -> list[dict]:
    """`items/<item_id>.json`: the six passing items = polish-run record + human_review; BI-P3-0007 as delivered."""
    schema, pitems, out = bi.load_schema(), read_polish_items(src), []
    for it in sorted(items, key=lambda x: x["item_id"]):
        sid = it["review"]["history"][0]["seed_id"]
        x = human_review_item(pitems[sid], at) if it["review"]["status"] == "deterministic_pass" else copy.deepcopy(it)
        errs = bi.schema_errors(x, schema) + bi.consistency_errors(x)
        _check(not errs or x["review"]["status"] == "rejected_pre_review", f"{x['item_id']}: invalid: {errs}")
        path = ITEMS_DIR / f"{x['item_id']}.json"
        r2.write_json(path, x)
        out.append({"item_id": x["item_id"], "seed_id": sid, "path": path.relative_to(ART).as_posix(), "sha256": sha256_file(path),
                    "status": x["review"]["status"], "history": [h["event"] for h in x["review"]["history"]],
                    "schema_valid": not bi.schema_errors(x, schema), "consistency_errors": bi.consistency_errors(x) if not errs else errs})
    return out


def _entry(base: Path, name: str) -> dict:
    return {"path": name, "sha256": sha256_file(base / name), "bytes": (base / name).stat().st_size}


def manifest(facts: dict, reproduced: dict, written: list[dict], src: Path, at: str) -> dict:
    return {
        "run": "run4", "diagnostic_id": RUN_ID, "decision": DECISION, "work_package": "P3b",
        "tarball": {"name": TARBALL_NAME, "sha256": TARBALL_SHA256},
        "generator": {"version": GENERATOR_VERSION, "agent_path": AGENT_REL, "agent_sha256": AGENT_SHA256,
                      "system_prompt_sha256": SYSTEM_PROMPT_SHA256, "corrective_template_sha256": CORRECTIVE_SHA256,
                      "format_corrective_template_sha256": FORMAT_CORRECTIVE_SHA256},
        "endpoint": {"endpoint_label": ENDPOINT_LABEL, "model": MODEL, "base_url": BASE_URL}, "budget": BUDGET,
        "source_commit": SOURCE_COMMIT,
        "packets": {"version": "synthpackets v4a", "path": PACKETS_REL, "at_commit": SOURCE_COMMIT, "manifest_sha256": PACKETS_MANIFEST_SHA256},
        "counts": dict(RUN_FACTS), "items": facts["items"], "format_corrective_items": facts["format_corrective_items"],
        "rejected_pre_review": facts["rejected"], "log": facts["log"],
        "items_sha256": ITEMS_SHA256, "summary_sha256": SUMMARY_SHA256,
        "checks_reproduced": reproduced["checks_reproduced"], "checks": reproduced,
        "item_schema": {"path": "data/metadata/benchmark/item_schema_v2.json", "sha256": bi.schema_sha256()},
        "lifecycle": {"status": "human_review", "from": "deterministic_pass", "rule": "D-033", "kaiyuan_disposition": None,
                      "mentor_disposition": None, "final_frozen": None,
                      "note": ("items/<item_id>.json: the six passing items = the polish-run record (run-4 item + its polish event, "
                               "text unchanged: every rewrite was rejected) + this step; BI-P3-0007 = the run-4 record as delivered "
                               "(rejected_pre_review, not entered human review); items.jsonl is the run's file, byte-identical")},
        "polish": {"run": "polish/run1", "manifest": "../../polish/run1/manifest.json"},
        "files": [_entry(ART, n) for n in COPIED.values()],
        "items_ingested": written, "excluded_files": excluded_files(_run(src), COPIED),
        "ingested_at": at, "ingested_by": "EXECUTOR",
    }


def polish_manifest(facts: dict, reproduced: dict, replay: dict, src: Path, at: str) -> dict:
    return {
        "run": "polish/run1", "diagnostic_id": POLISH_RUN_ID, "decision": "D-063", "work_package": "P3b",
        "tarball": {"name": TARBALL_NAME, "sha256": TARBALL_SHA256},
        "generator": {"version": POLISH_GENERATOR_VERSION, "agent_path": POLISH_AGENT_REL, "agent_sha256": POLISH_AGENT_SHA256,
                      "system_prompt_sha256": POLISH_SYSTEM_PROMPT_SHA256, "corrective_template_sha256": POLISH_CORRECTIVE_SHA256,
                      "check_version": "polish_checks v1a", "synonyms_sha256": POLISH_SYNONYMS_V1_SHA256},
        "endpoint": {"endpoint_label": ENDPOINT_LABEL, "model": MODEL, "base_url": BASE_URL}, "budget": BUDGET,
        "source_commit": SOURCE_COMMIT, "input": "synthesis run 4 (artifacts/benchmark/items/run4)",
        "counts": dict(POLISH_FACTS), "log": facts["polish_log"],
        "summary_sha256": POLISH_SUMMARY_SHA256, "polished_sha256": POLISHED_SHA256,
        "checks_reproduced": reproduced["checks_reproduced"], "checks": reproduced,
        "replay_checks_v2": replay,
        "files": [_entry(POLISH_ART, n) for n in POLISH_COPIED.values()],
        "excluded_files": excluded_files(_prun(src), POLISH_COPIED),
        "note": ("every rewrite was rejected, so no item text changed; the six item records with their polish event are in "
                 "items/run4/items (human_review); polished.jsonl holds pre_polish, the rewrite, the reasons and the checks"),
        "ingested_at": at, "ingested_by": "EXECUTOR",
    }
