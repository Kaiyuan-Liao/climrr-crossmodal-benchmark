"""Infra synthesis runs 1 -- 2 and polish runs 1 -- 2: verification, ingest, the D-079 display rule and the lifecycle step
(work package P5d, section A; D-079, D-080).

**Synthesis infra run 2** is `litsynth_agent` v5.4 on Polaris (Sophia vLLM, `openai/gpt-oss-120b`, reasoning low,
max_tokens 16000) over the eight rung-8 packets v1b at source commit `bf69970` (D-075a). **Polish infra run 2** is
`litpolish_agent` v1.1 (checks v2) over run 2's output at the same commit. **Infra run 1** (agent v5.3, packets v1a, source
commit `b860658`) and its polish run are superseded and ingested as such. All four arrive in one tarball. Run 2 is the impact
sample set (D-080).

How run 2 went, from its log (kept whole): a first start made all eight items (5 `deterministic_pass`, 3
`rejected_pre_review`: BI-P5-0002, 0003, 0005); the three rejected item files were moved to `attempt1/` and each seed was
drawn again with its own restart (three restarts, one item each): BI-P5-0002 passed, BI-P5-0003 (doubled magnitude phrase)
and BI-P5-0005 (a two-hop sentence without its marker) were rejected again. Final: **6 pass, 2 rejected after a second
attempt**. The three first attempts are ingested as **`superseded_attempt`**s (byte-identical copies). Polish run 2 ran
twice: over the five items passing after the first start, then over the redrawn BI-P5-0002 (4 polished, 2 polish-rejected;
the two rejected synthesis items skipped).

`verify_source` re-derives every fact the work package states from the delivered files and raises on any difference.
`reproduce_synthesis` re-assembles every item and superseded attempt from its final raw response with the pinned agent (v5.4
at `bf69970` for run 2, v5.3 at `b860658` for run 1, each loaded from its bytes) and re-runs its post-checks (v3.5 against
packets v1b; v3.4 against packets v1a) --- the format-corrective first turns likewise. `reproduce_polish` re-extracts each
rewrite with the pinned polish agent v1.1 and re-runs `polish_checks.invariance_v2`. Each must equal what the run recorded
(`checks_reproduced`).

**D-079 (display rule).** The display text is the polished text **only if** the polish passed **and** post-checks v3.5,
re-run on the polished prompt and answer against the item's v1b packet (`display_recheck`), pass; otherwise the original.
`display_source` and the re-check result are recorded per item in its `human_review` event, with the display text itself.

`items/<item_id>.json`: for the six passing items, the polish-run record (run-2 item + its polish event; the text is the
rewrite where the polish status is `polished`, as the polish agent wrote it) + the D-033 lifecycle step
deterministic_pass -> human_review, whose event records `display_source`, `display_recheck` and `display_text`; for
BI-P5-0003 and 0005, the run-2 item as delivered (`rejected_pre_review`), the manifest recording `redraws: 2`.

**Regression fixture.** The two items infra run 1 passed (BI-P5-0001, 0003; v5.3, packets v1a) are pinned in
`items/infra_run1/items.jsonl` (byte-identical) and must pass post-checks v3.5 against their v1a packets with the length
budget reported (`run1_regression`), the check the v5.4 package had to make on synthetic items.

No model call, no table value; no concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from climrr import benchmark_items as bi
from climrr import litstatements_run2 as r2
from climrr import litsynth_run2 as s2
from climrr import litsynth_run4 as s4
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

DECISION, DISPLAY_RULE = "D-080", "D-079"
WORK_PACKAGE = "P5d"
ITEMS_ROOT = REPO_ROOT / "artifacts" / "benchmark" / "items"
ART = ITEMS_ROOT / "infra_run2"
ITEMS_DIR = ART / "items"
SUPERSEDED_DIR = ART / "superseded"
MANIFEST_PATH = ART / "manifest.json"
ART1 = ITEMS_ROOT / "infra_run1"
MANIFEST1_PATH = ART1 / "manifest.json"
POLISH_ROOT = REPO_ROOT / "artifacts" / "benchmark" / "polish"
POLISH_ART = POLISH_ROOT / "infra_run2"
POLISH_MANIFEST_PATH = POLISH_ART / "manifest.json"
POLISH_ART1 = POLISH_ROOT / "infra_run1"
POLISH_MANIFEST1_PATH = POLISH_ART1 / "manifest.json"

TARBALL_NAME = "infra_synth_runs12_evidence.tar.gz"
TARBALL_SHA256 = "1ab289297f0ba606c147f97eb0b1d5758991598b7e78216ef5fb3ca80a4d33f7"
ITEMS_SHA256 = "ce23c904520b67b0fbed9f4182cdc34feae0cc6ad9f8b96c259a0ce8327c4b2b"            # stated
SUMMARY_SHA256 = "f65373dab6389c58467852419ee08920fcd14f44f5dd9f5234eac42b72e06ec7"          # pinned on receipt
POLISH_SUMMARY_SHA256 = "4e66b248b4c3b6937db0531aecafe1d95e5ff710c934d600884d467d732ccc0d"   # stated
POLISHED_SHA256 = "21f6620738cf3958eea049448ee2f4c0e98a9a40503bf3aaa8bb173a6ffdb1c7"          # pinned on receipt
SOURCE_COMMIT = "bf699700ab45ee9f3b0f5715515c1b7b42a7ba66"

AGENT_REL = "scripts/litcollect/litsynth_agent.py"
AGENT_SHA256 = "9f0f8900fe9f2d3f65a2baf2e7bd2c91998cb9c3d024d0d2d65e114e6d8611ed"           # litsynth_agent v5.4
SYSTEM_PROMPT_SHA256 = "1a023c1e98e822f74304801fce5a8b4605f6148c528c3dc4f5e236c5c87c3ade"
CORRECTIVE_SHA256 = "256db051b3ddfa93d893e4573a2e818ecd4623d96ddac0aaebdba932c6e2a01a"
FORMAT_CORRECTIVE_SHA256 = "a21eb42a4a61ecf540803ba1b0da19fc80bb4c9c8077089b2d0cf58b8c6f10e8"
GENERATOR_VERSION = "litsynth_agent v5.4"
CHECK_VERSION = bi.SYNTH_CHECK_VERSION_V35
PACKETS_REL = "artifacts/benchmark/synth_packets_infra_v1b"
PACKETS_MANIFEST_SHA256 = "b4cbbdb308ab90b5cd68a761009d88431315099aa9bb31acb9bd496061736a3e"  # packets v1b

POLISH_AGENT_REL = "scripts/litcollect/litpolish_agent.py"
POLISH_AGENT_SHA256 = "6abc7b2b46298934682bf8342793e185cc73b85d69b505ef61e6cbe0c374366e"    # litpolish_agent v1.1
POLISH_SYSTEM_PROMPT_SHA256 = "2dbbce7f345fdcdeccd4661c22f5c22d87e6c4bcaa070856b59e6234093f0a18"
POLISH_CORRECTIVE_SHA256 = "b12f5fc80f7ad62b20c122f7cb28c5174a9c0c48888acdcd609dbab63f722bf8"
POLISH_GENERATOR_VERSION = "litpolish_agent v1.1"
POLISH_CHECK_VERSION = "polish_checks v2"

ENDPOINT_LABEL, MODEL, BASE_URL = "sophia_vllm", "openai/gpt-oss-120b", r2.BASE_URL
BUDGET = {"reasoning_effort": "low", "max_tokens": 16000, "temperature": 0}

SEEDS = {"SD8-TP1-00111-energy": "BI-P5-0001", "SD8-TP1-00069-transportation_systems": "BI-P5-0002",
         "SD8-TP1-00071-water_and_wastewater": "BI-P5-0003", "SD8-TP1-00071-healthcare_and_public_health": "BI-P5-0004",
         "SD8-TP1-01463-energy": "BI-P5-0005", "SD8-TP1-01463-transportation_systems": "BI-P5-0006",
         "SD8-TP1-01463-emergency_services": "BI-P5-0007", "SD8-TP1-01463-communications": "BI-P5-0008"}
ITEM_IDS = tuple(sorted(SEEDS.values()))
PASSING = ("BI-P5-0001", "BI-P5-0002", "BI-P5-0004", "BI-P5-0006", "BI-P5-0007", "BI-P5-0008")
REJECTED = {
    "BI-P5-0003": ["table_pattern: doubled magnitude phrase (DR-DESC-1 v4): 'increase a moderate increase'",
                   "integrated: doubled magnitude phrase (DR-DESC-1 v4): 'increase a moderate increase'"],
    "BI-P5-0005": ["literature_interpretation[1]: two-hop wording (D-073c): a sentence citing a two-hop group must say "
                   "'when wildfires occur', 'wildfires can' or 'raise the chance of ignition'"]}
REJECTED_READING = {"BI-P5-0003": "doubled magnitude phrase ('increase a moderate increase'), on both attempts",
                    "BI-P5-0005": "a sentence citing a two-hop group without its two-hop marker (second attempt)"}
#: The work package's `redraws: 2` for the two rejected items: two generations of the seed in run 2 (the first draw and one
#: redraw), both rejected (`attempts` lists them).
REDRAWS = 2
SUPERSEDED = {
    "BI-P5-0002": {"seed_id": "SD8-TP1-00069-transportation_systems",
                   "sha256": "1b798519440a96a4415498a5b052d23c603a579ee94f88cba3c4e764275135d3",
                   "reasons": ["literature_interpretation: rung 8 answer shape (D-075a): at most 2 driver claims, the strongest (found 3)"]},
    "BI-P5-0003": {"seed_id": "SD8-TP1-00071-water_and_wastewater",
                   "sha256": "1a657a691b614475f29be623dbdfb75544482e661db7e0fb092c144a90beba45",
                   "reasons": REJECTED["BI-P5-0003"]},
    "BI-P5-0005": {"seed_id": "SD8-TP1-01463-energy",
                   "sha256": "efb33fe0524a6e2f5624e3e76cd68034f5a8e5f467f8372ace7e26a17d9161d9",
                   "reasons": ["rubric.optional_points: fire-weather wording (an FWI is never fire occurrence): 'wildfires' in graded text",
                               "rubric.optional_points: fire-weather wording (an FWI is never fire occurrence): 'wildfire' in graded text",
                               "literature_interpretation[2]: two-hop wording (D-073c): a sentence citing a two-hop group must say "
                               "'when wildfires occur', 'wildfires can' or 'raise the chance of ignition'"]}}
RUN_FACTS = {"items": 8, "deterministic_pass": 6, "deterministic_fail": 2, "corrective_retry_used": 0, "format_corrective_used": 6,
             "format_corrective_pass": 4, "first_pass": 5, "redraws": 3, "superseded_attempts": 3, "restarts": 3}
LOG_DONE = ["items=8 pass=5 fail=3", "items=6 pass=6 fail=0", "items=7 pass=6 fail=1", "items=8 pass=6 fail=2"]
LOG_ITEMS = [("SD8-TP1-00069-transportation_systems", "rejected_pre_review"),
             ("SD8-TP1-00071-healthcare_and_public_health", "deterministic_pass"),
             ("SD8-TP1-00071-water_and_wastewater", "rejected_pre_review"), ("SD8-TP1-00111-energy", "deterministic_pass"),
             ("SD8-TP1-01463-communications", "deterministic_pass"), ("SD8-TP1-01463-emergency_services", "deterministic_pass"),
             ("SD8-TP1-01463-energy", "rejected_pre_review"), ("SD8-TP1-01463-transportation_systems", "deterministic_pass"),
             ("SD8-TP1-00069-transportation_systems", "deterministic_pass"),
             ("SD8-TP1-00071-water_and_wastewater", "rejected_pre_review"), ("SD8-TP1-01463-energy", "rejected_pre_review")]
POLISH_FACTS = {"items": 6, "polished": 4, "polish_rejected": 2, "polish_parse_failed": 0,
                "reasons_by_kind": {"hedges": 1, "places": 1}, "skipped_not_deterministic_pass": ["BI-P5-0003", "BI-P5-0005"]}
POLISH_REJECTED = {
    "BI-P5-0001": ["answer: places differ (original ['United States', 'Virginia'], polished ['Virginia'])"],
    "BI-P5-0008": ["answer: hedges differ (original ['show', 'shows', 'suggests'], polished ['show', 'suggests'])"]}
POLISH_DONE = ["items=5 polished=3 rejected=2 parse_failed=0", "items=6 polished=4 rejected=2 parse_failed=0"]
COPIED = {"litsynth/infra_run2/items.jsonl": "items.jsonl", "litsynth/infra_run2/summary.json": "summary.json",
          "litsynth/infra_run2/agent.log": "agent.log"}
SUPERSEDED_COPIED = {f"litsynth/infra_run2/attempt1/{v['seed_id']}.json": f"superseded/{k}_attempt1.json" for k, v in SUPERSEDED.items()}
POLISH_COPIED = {"litpolish/infra_run2/polished.jsonl": "polished.jsonl", "litpolish/infra_run2/summary.json": "summary.json",
                 "litpolish/infra_run2/agent.log": "agent.log"}

# --- infra run 1 (superseded) -------------------------------------------------------------------------------------
RUN1_ITEMS_SHA256 = "d4f91da923246c4756fb8e50f436709c0aca685101fb819eeccf5ef7bd1615ae"
RUN1_SUMMARY_SHA256 = "af5b0e9995805545e91c044cc2fbd89eb97cbf21c67e550e1da5f3129d657dd6"
RUN1_POLISHED_SHA256 = "9bc096cfeafdfc21fa0739588b850d851dbd8d17d7b922df28fd37fead371186"
RUN1_POLISH_SUMMARY_SHA256 = "4c54e8823e214b062ecf2267960ea28167e2a9c778383f93cb2447536138a942"
RUN1_SOURCE_COMMIT = "b860658873bd4d80ae9500587e23b18d4778c387"
RUN1_AGENT_SHA256 = "1be4ba2a6aec418b2729f6d165a3ed159208a0d31b786ad92413d7d195f43edd"      # litsynth_agent v5.3
RUN1_SYSTEM_PROMPT_SHA256 = "1157f73286a6de3a443a20becf924be401abd22e46170a62d6f4a580bbd75ea5"
RUN1_GENERATOR_VERSION = "litsynth_agent v5.3"
RUN1_CHECK_VERSION = bi.SYNTH_CHECK_VERSION_V34
RUN1_PACKETS_REL = "artifacts/benchmark/synth_packets_infra_v1a"
RUN1_PACKETS_MANIFEST_SHA256 = "829d80cfa3fdff217ddc19a2f2b8ffc97bf7b41cc7f1f869ecfa0daaf37e5bf2"  # packets v1a
RUN1_PASSING = ("BI-P5-0001", "BI-P5-0003")
RUN1_FACTS = {"items": 8, "deterministic_pass": 2, "deterministic_fail": 6, "format_corrective_used": 8, "format_corrective_pass": 2}
RUN1_POLISH_FACTS = {"items": 2, "polished": 1, "polish_rejected": 1, "polish_parse_failed": 0}
RUN1_COPIED = {"litsynth/infra_run1/items.jsonl": "items.jsonl", "litsynth/infra_run1/summary.json": "summary.json",
               "litsynth/infra_run1/agent.log": "agent.log"}
RUN1_POLISH_COPIED = {"litpolish/infra_run1/polished.jsonl": "polished.jsonl", "litpolish/infra_run1/summary.json": "summary.json",
                      "litpolish/infra_run1/agent.log": "agent.log"}

HUMAN_REVIEW_NOTE = ("entered human review (D-033 lifecycle): infra synthesis run 2 (agent v5.4, packets v1b) and polish infra "
                     "run 2 (agent v1.1, checks v2); the impact sample set (D-080); display text by D-079 (polished only if the "
                     "polish passed and post-checks v3.5 pass on the polished text)")
INGEST_BY = "EXECUTOR (scripts/ingest_litsynth_infra_run2.py)"


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _run(src: Path, n: int = 2) -> Path:
    return Path(src) / "litsynth" / f"infra_run{n}"


def _prun(src: Path, n: int = 2) -> Path:
    return Path(src) / "litpolish" / f"infra_run{n}"


def packet_at(commit: str, rel: str, seed_id: str) -> tuple[dict, str]:
    blob = s2.git_blob(commit, f"{rel}/PK-{seed_id}.json")
    return json.loads(blob.decode("utf-8")), hashlib.sha256(blob).hexdigest()


def packet_v1b(seed_id: str) -> dict:
    return packet_at(SOURCE_COMMIT, PACKETS_REL, seed_id)[0]


def read_item_files(src: Path, n: int = 2) -> list[dict]:
    """The per-item files of run `n` in `items.jsonl` order."""
    run = _run(src, n)
    return [s2._load(run / "items" / f"{it['review']['history'][0]['seed_id']}.json") for it in s2.read_items(run / "items.jsonl")]


def read_attempts(src: Path) -> dict:
    return {iid: s2._load(_run(src) / "attempt1" / f"{v['seed_id']}.json") for iid, v in SUPERSEDED.items()}


def read_polish_items(src: Path, n: int = 2) -> dict:
    return {p.stem: s2._load(p) for p in sorted((_prun(src, n) / "items").glob("*.json"))}


def _summary_facts(s: dict, facts) -> None:
    for k, v in facts:
        _check(s.get(k) == v, f"summary {k} = {s.get(k)!r}, expected {v!r}")


def _generation_facts(h: dict, iid: str, run: int = 2) -> None:
    gv, commit, prompt, cv = ((GENERATOR_VERSION, SOURCE_COMMIT, SYSTEM_PROMPT_SHA256, CHECK_VERSION) if run == 2 else
                              (RUN1_GENERATOR_VERSION, RUN1_SOURCE_COMMIT, RUN1_SYSTEM_PROMPT_SHA256, RUN1_CHECK_VERSION))
    for k, v in (("generator_version", gv), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL), ("base_url", BASE_URL),
                 ("source_commit", commit), ("reasoning_effort_applied", True), ("system_prompt_sha256", prompt),
                 ("corrective_prompt_sha256", CORRECTIVE_SHA256), ("finish_reason", "stop"), ("corrective_retry_used", False),
                 ("check_version", cv), *BUDGET.items()):
        _check(h.get(k) == v, f"{iid}: {k} = {h.get(k)!r}, expected {v!r}")
    _check(all(t["http_attempts"] == 1 for t in h["turns"]), f"{iid}: an HTTP retry")


def log_facts(log: str) -> dict:
    lines = log.splitlines()
    starts = [ln.split()[0] for ln in lines if " START " in ln]
    _check(len(starts) == 4, f"{len(starts)} START lines in the run-2 log, expected 4 (first start, three restarts)")
    _check(not any(" FAIL " in ln for ln in lines), "a FAIL line in the run-2 log")
    done = [ln.split(" DONE ", 1)[1] for ln in lines if " DONE " in ln]
    _check(done == LOG_DONE, f"log DONE lines {done}")
    items = [(ln.split()[1], ln.split("status=")[1].split()[0]) for ln in lines if " level=8 " in ln]
    _check(items == LOG_ITEMS, f"log item lines {items}")
    return {"start_utc": starts[0], "restart_utc": starts[1:], "end_utc": lines[-1].split()[0], "done": done,
            "format_corrective_lines": sum(" FORMAT_CORRECTIVE " in ln for ln in lines),
            "restarts": [{"start_utc": starts[k + 1], "made": 1, "seed_id": s, "item_id": SEEDS[s],
                          "status": LOG_ITEMS[8 + k][1]} for k, s in enumerate(x[0] for x in LOG_ITEMS[8:])],
            "reading": ("the first start made all eight items (5 pass); the three rejected item files were moved to attempt1/ "
                        "and each seed was drawn again by its own restart")}


def verify_source(src: Path) -> dict:
    """Every run-1 / run-2 synthesis and polish fact the work package states, re-derived from the delivered files."""
    src, run, prun = Path(src), _run(src), _prun(src)
    for f, sha, what in ((run / "items.jsonl", ITEMS_SHA256, "run-2 items.jsonl (stated)"),
                         (run / "summary.json", SUMMARY_SHA256, "run-2 summary.json"),
                         (prun / "summary.json", POLISH_SUMMARY_SHA256, "polish run-2 summary.json (stated)"),
                         (prun / "polished.jsonl", POLISHED_SHA256, "polish run-2 polished.jsonl"),
                         (_run(src, 1) / "items.jsonl", RUN1_ITEMS_SHA256, "run-1 items.jsonl"),
                         (_run(src, 1) / "summary.json", RUN1_SUMMARY_SHA256, "run-1 summary.json"),
                         (_prun(src, 1) / "polished.jsonl", RUN1_POLISHED_SHA256, "polish run-1 polished.jsonl"),
                         (_prun(src, 1) / "summary.json", RUN1_POLISH_SUMMARY_SHA256, "polish run-1 summary.json")):
        _check(sha256_file(f) == sha, f"{what} differs from its SHA-256 {sha}")
    for iid, v in SUPERSEDED.items():
        _check(sha256_file(run / "attempt1" / f"{v['seed_id']}.json") == v["sha256"], f"{iid}: attempt1 differs from its pin")
    for commit, rel, sha in ((SOURCE_COMMIT, AGENT_REL, AGENT_SHA256), (SOURCE_COMMIT, POLISH_AGENT_REL, POLISH_AGENT_SHA256),
                             (RUN1_SOURCE_COMMIT, AGENT_REL, RUN1_AGENT_SHA256), (RUN1_SOURCE_COMMIT, POLISH_AGENT_REL, POLISH_AGENT_SHA256),
                             (SOURCE_COMMIT, f"{PACKETS_REL}/manifest.json", PACKETS_MANIFEST_SHA256),
                             (RUN1_SOURCE_COMMIT, f"{RUN1_PACKETS_REL}/manifest.json", RUN1_PACKETS_MANIFEST_SHA256)):
        _check(hashlib.sha256(s2.git_blob(commit, rel)).hexdigest() == sha, f"{rel} at {commit[:7]} differs from {sha}")
    _check(sha256_file(REPO_ROOT / PACKETS_REL / "manifest.json") == PACKETS_MANIFEST_SHA256, "working-tree packets v1b changed")
    for n in (1, 2):
        for sub, name in (("litsynth", f"litsynth_infra_run{n}"), ("litpolish", f"litpolish_infra_run{n}")):
            _check((src / sub / f"infra_run{n}" / "agent.log").read_bytes() == (src / "reports" / f"{name}.log").read_bytes(),
                   f"{sub}/infra_run{n}/agent.log differs from reports/{name}.log")

    s = s2._load(run / "summary.json")
    _summary_facts(s, (("generator_version", GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL),
                       ("base_url", BASE_URL), ("reasoning_effort", "low"), ("max_tokens", 16000),
                       ("system_prompt_sha256", SYSTEM_PROMPT_SHA256), ("corrective_prompt_sha256", CORRECTIVE_SHA256),
                       ("format_corrective_prompt_sha256", FORMAT_CORRECTIVE_SHA256), ("check_version", CHECK_VERSION),
                       ("finish_reasons", {"stop": 8}), ("by_level", {"8": 8}), ("reasoning_effort_not_applied", 0),
                       *((k, RUN_FACTS[k]) for k in ("items", "deterministic_pass", "deterministic_fail", "corrective_retry_used",
                                                     "format_corrective_used", "format_corrective_pass"))))
    items = s2.read_items(run / "items.jsonl")
    v1b = json.loads(s2.git_blob(SOURCE_COMMIT, f"{PACKETS_REL}/manifest.json"))
    v1b_sha = {x["seed_id"]: x["sha256"] for x in v1b["packets"]}
    _check(sorted(p.stem for p in (run / "items").glob("*.json")) == sorted(v1b_sha) == sorted(SEEDS), "run-2 item files")
    leakage, corrective, reports = 0, [], {}
    for it in items:
        h = it["review"]["history"][0]
        sid, iid = h["seed_id"], it["item_id"]
        _check(s2._load(run / "items" / f"{sid}.json") == it, f"{sid}: the per-item file differs from its items.jsonl line")
        _check(iid == SEEDS[sid], f"{sid}: item id {iid}")
        want = ("deterministic_pass", "deterministic_pass", []) if iid in PASSING else ("rejected_pre_review", "deterministic_fail", REJECTED[iid])
        _check((it["review"]["status"], h["event"], h["reasons"]) == want, f"{iid}: status {it['review']['status']} {h['reasons']}")
        _check(h["packet_sha256"] == it["generation"]["inputs_sha256"]["packet"] == packet_at(SOURCE_COMMIT, PACKETS_REL, sid)[1]
               == v1b_sha[sid], f"{iid}: not packets v1b")
        _generation_facts(h, iid)
        leakage += len(it["source_leakage_check"]["flags"]) + len(h["checks"]["prompt_leakage"]["flags"])
        if h["corrective_turn_used"]:
            _check(h["corrective_class"] == "format" and h["first_check"]["event"] == "deterministic_fail", f"{iid}: corrective")
            corrective.append(iid)
        reports[iid] = {"budget": h["checks"]["rung8_report"]["budget"], "scope_openers": h["checks"].get("scope_openers")}
    _check(leakage == 0, f"{leakage} leakage flags")
    _check(len(corrective) == RUN_FACTS["format_corrective_used"], f"format corrective on {corrective}")

    final = {it["item_id"]: it for it in items}
    for iid, att in read_attempts(src).items():
        ah, sup = att["review"]["history"][0], SUPERSEDED[iid]
        _check(att["item_id"] == iid and ah["seed_id"] == sup["seed_id"], f"attempt1 is not {iid}")
        _check(att["review"]["status"] == "rejected_pre_review" and ah["event"] == "deterministic_fail" and ah["reasons"] == sup["reasons"],
               f"{iid} attempt1: {att['review']['status']} {ah['reasons']}")
        _check(ah["packet_sha256"] == v1b_sha[sup["seed_id"]], f"{iid} attempt1: packet")
        _generation_facts(ah, f"{iid} attempt1")
        fh = final[iid]["review"]["history"][0]
        _check(ah["generation_timestamp"] < fh["generation_timestamp"] and ah["raw_response"] != fh["raw_response"],
               f"{iid}: attempt1 is not an earlier, different draw")
    lf = log_facts((run / "agent.log").read_text(encoding="utf-8"))

    # Polish run 2.
    ps = s2._load(prun / "summary.json")
    _summary_facts(ps, (("generator_version", POLISH_GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL),
                        ("base_url", BASE_URL), ("reasoning_effort", "low"), ("max_tokens", 16000),
                        ("system_prompt_sha256", POLISH_SYSTEM_PROMPT_SHA256), ("corrective_prompt_sha256", POLISH_CORRECTIVE_SHA256),
                        ("check_version", POLISH_CHECK_VERSION), *POLISH_FACTS.items()))
    _verify_polish(src, 2, {it["review"]["history"][0]["seed_id"]: it for it in items if it["item_id"] in PASSING}, POLISH_REJECTED)
    plog = (prun / "agent.log").read_text(encoding="utf-8").splitlines()
    pdone = [ln.split(" DONE ", 1)[1] for ln in plog if " DONE " in ln]
    _check(pdone == POLISH_DONE, f"polish DONE {pdone}")
    _check(not any(" FAIL " in ln or "CORRECTIVE" in ln for ln in plog), "a FAIL or CORRECTIVE line in the polish log")
    pstarts = [ln.split()[0] for ln in plog if " START " in ln]

    # Infra run 1 (superseded) and its polish run.
    s1 = s2._load(_run(src, 1) / "summary.json")
    _summary_facts(s1, (("generator_version", RUN1_GENERATOR_VERSION), ("system_prompt_sha256", RUN1_SYSTEM_PROMPT_SHA256),
                        ("check_version", RUN1_CHECK_VERSION), *RUN1_FACTS.items()))
    items1 = s2.read_items(_run(src, 1) / "items.jsonl")
    v1a = json.loads(s2.git_blob(RUN1_SOURCE_COMMIT, f"{RUN1_PACKETS_REL}/manifest.json"))
    v1a_sha = {x["seed_id"]: x["sha256"] for x in v1a["packets"]}
    for it in items1:
        h = it["review"]["history"][0]
        _check(s2._load(_run(src, 1) / "items" / f"{h['seed_id']}.json") == it, f"run 1 {h['seed_id']}: per-item file differs")
        _check(it["item_id"] == SEEDS[h["seed_id"]] and h["packet_sha256"] == v1a_sha[h["seed_id"]], f"run 1 {it['item_id']}: packet")
        _check((it["review"]["status"] == "deterministic_pass") == (it["item_id"] in RUN1_PASSING), f"run 1 {it['item_id']}: status")
        _generation_facts(h, f"run 1 {it['item_id']}", run=1)
    ps1 = s2._load(_prun(src, 1) / "summary.json")
    _summary_facts(ps1, (("generator_version", POLISH_GENERATOR_VERSION), ("check_version", POLISH_CHECK_VERSION), *RUN1_POLISH_FACTS.items()))
    _verify_polish(src, 1, {it["review"]["history"][0]["seed_id"]: it for it in items1 if it["item_id"] in RUN1_PASSING}, None)
    return {"summary": s, "polish_summary": ps, "run1_summary": s1, "run1_polish_summary": ps1,
            "items": [{"item_id": it["item_id"], "seed_id": it["review"]["history"][0]["seed_id"], "status": it["review"]["status"],
                       "packet_sha256": it["generation"]["inputs_sha256"]["packet"],
                       "corrective_turn_used": it["review"]["history"][0]["corrective_turn_used"]}
                      for it in sorted(items, key=lambda x: x["item_id"])],
            "format_corrective_items": sorted(corrective), "rung8_reports": reports, "log": lf,
            "polish_log": {"start_utc": pstarts[0], "restart_utc": pstarts[1:], "done": pdone,
                           "reading": ("the first polish start ran after the first synthesis start (BI-P5-0002 then rejected, "
                                       "skipped); the second, after BI-P5-0002 was redrawn, polished it")},
            "run1_items": [{"item_id": it["item_id"], "status": it["review"]["status"], "reasons": it["review"]["history"][0]["reasons"]}
                           for it in sorted(items1, key=lambda x: x["item_id"])]}


def _verify_polish(src: Path, n: int, by_seed: dict, rejected: dict | None) -> None:
    """Polish run `n`: one record per passing synthesis item; each polish item = the synthesis item + one polish event, text
    replaced only when polished; the event names the synthesis item file by its SHA-256."""
    pitems, recs = read_polish_items(src, n), s2.read_items(_prun(src, n) / "polished.jsonl")
    _check(sorted(pitems) == sorted(by_seed) == sorted(r["seed_id"] for r in recs), f"polish run {n}: items")
    cols = bi.column_names()
    for r in recs:
        sid = r["seed_id"]
        p, orig = pitems[sid], by_seed[sid]
        ev = p["review"]["history"][-1]
        _check(ev["event"] == "polish" and ev["status"] == r["status"] and r["status"] in ("polished", "polish_rejected"), f"{sid}: polish")
        if rejected is not None:
            _check(r["reasons"] == rejected.get(r["item_id"], []), f"{sid}: polish reasons {r['reasons']}")
        _check(ev["item_sha256"] == sha256_file(_run(src, n) / "items" / f"{sid}.json"), f"{sid}: polish event names another item")
        pre = {"prompt": orig["prompt"], "answer": orig["reference_answer"]["integrated"]}
        _check(r["item_id"] == orig["item_id"] and r["pre_polish"] == ev["pre_polish"] == pre, f"{sid}: pre_polish")
        _check(r["polished"] == ev["rewrite"] and r["reasons"] == ev["reasons"] and r["checks"] == ev["checks"], f"{sid}: record")
        base = copy.deepcopy(p)
        base["review"]["history"] = base["review"]["history"][:-1]
        want = copy.deepcopy(orig)
        if r["status"] == "polished":
            want["prompt"], want["reference_answer"]["integrated"] = r["polished"]["prompt"], r["polished"]["answer"]
            want["source_leakage_check"] = bi.leakage_check(r["polished"]["prompt"], cols)
        _check(base == want, f"{sid}: the polish item is not the synthesis item + one event")
        commit = SOURCE_COMMIT if n == 2 else RUN1_SOURCE_COMMIT
        for k, v in (("generator_version", POLISH_GENERATOR_VERSION), ("endpoint_label", ENDPOINT_LABEL), ("model", MODEL),
                     ("base_url", BASE_URL), ("source_commit", commit), ("reasoning_effort_applied", True),
                     ("system_prompt_sha256", POLISH_SYSTEM_PROMPT_SHA256), ("check_version", POLISH_CHECK_VERSION),
                     ("corrective_retry_used", False), ("finish_reason", "stop"), *BUDGET.items()):
            _check(ev.get(k) == v, f"{sid}: polish {k} = {ev.get(k)!r}, expected {v!r}")


# --- reproduction ------------------------------------------------------------------------------------------------


def _reproduce_one(agent, it: dict, cols: list[str], expect_pass: bool, run: int = 2) -> dict:
    h = it["review"]["history"][0]
    commit, rel, cv = (SOURCE_COMMIT, PACKETS_REL, CHECK_VERSION) if run == 2 else (RUN1_SOURCE_COMMIT, RUN1_PACKETS_REL, RUN1_CHECK_VERSION)
    packet, _ = packet_at(commit, rel, h["seed_id"])
    common = {k: h[k] for k in ("model", "prompt_hash", "generation_timestamp", "packet_sha256", "system_prompt_sha256")}
    _check(len(h["raw_response"]) == h["raw_response_chars"], f"{it['item_id']}: raw response truncated")
    again, tagged = agent.assemble(agent.extract_item(h["raw_response"]), packet, common, cols)
    _check({**again, "review": None} == {**it, "review": None}, f"{it['item_id']}: re-assembled item differs")
    _check(tagged == h["reference_answer_tagged"], f"{it['item_id']}: re-assembled tagged answer differs")
    res = bi.synthesis_post_checks(s2._as_candidate(it), tagged, packet["checks_input"], cols, check_version=cv)
    same = {k: res[k] == h[k] for k in ("check_version", "reasons", "checks")} | {"pass": res["pass"] == (h["event"] == "deterministic_pass")}
    _check(all(same.values()) and res["pass"] == expect_pass, f"{it['item_id']}: post-checks differ from the recorded result: {same}")
    first = None
    if h["corrective_turn_used"]:
        fc = h["first_check"]
        f_item, f_tagged = agent.assemble(agent.extract_item(fc["raw_response"]), packet, common, cols)
        fr = bi.synthesis_post_checks(f_item, f_tagged, packet["checks_input"], cols, check_version=cv)
        _check(f_tagged == fc["reference_answer_tagged"] and fr["reasons"] == fc["reasons"] and fr["checks"] == fc["checks"]
               and not fr["pass"], f"{it['item_id']}: first-turn check differs from the recorded first_check")
        first = fr["reasons"]
    return {"item_id": it["item_id"], "pass": res["pass"], "reasons": res["reasons"], "first_check_reasons": first}


def reproduce_synthesis(items: list[dict], attempts: dict, items1: list[dict], columns: list[str] | None = None) -> dict:
    """Run 2 (items and superseded attempts) with agent v5.4 / post-checks v3.5 / packets v1b; run 1 with agent v5.3 / v3.4 /
    packets v1a; each equal to its recorded result."""
    cols = columns if columns is not None else bi.column_names()
    agent = s4.load_agent_at(SOURCE_COMMIT, AGENT_REL, AGENT_SHA256, "litsynth_agent_v54")
    out = [_reproduce_one(agent, it, cols, it["item_id"] in PASSING) for it in items]
    sup = {iid: _reproduce_one(agent, att, cols, False) for iid, att in attempts.items()}
    _check(all(sup[i]["reasons"] == SUPERSEDED[i]["reasons"] for i in sup), "attempt1: reproduced reasons differ")
    agent1 = s4.load_agent_at(RUN1_SOURCE_COMMIT, AGENT_REL, RUN1_AGENT_SHA256, "litsynth_agent_v53")
    out1 = [_reproduce_one(agent1, it, cols, it["item_id"] in RUN1_PASSING, run=1) for it in items1]
    return {"checks_reproduced": True, "check_version": CHECK_VERSION, "items": out, "superseded_attempts": sup,
            "run1": {"check_version": RUN1_CHECK_VERSION, "items": out1}}


def reproduce_polish(src: Path, items: list[dict], items1: list[dict], columns: list[str] | None = None) -> dict:
    """Per polish record (runs 2 and 1): the rewrite re-extracted by the pinned v1.1 polish agent and `invariance_v2` on it,
    equal to what the run recorded."""
    from climrr import itemseeds as sd
    from climrr import pattern_descriptors as pd
    from climrr import plain_language as pl
    from climrr import polish_checks as pc

    agent = s4.load_agent_at(SOURCE_COMMIT, POLISH_AGENT_REL, POLISH_AGENT_SHA256, "litpolish_agent_v11")
    cols = columns if columns is not None else bi.column_names()
    nca, syn = sd.nca_map(), pc.load_synonyms_v2()
    rules, plain = pd.load_rules(pd.RULES_V4_PATH), pl.load(pl.PLAIN_V1A_PATH)
    out = {}
    for n, its in ((2, items), (1, items1)):
        by_seed = {it["review"]["history"][0]["seed_id"]: it for it in its}
        pitems, rows = read_polish_items(src, n), []
        for r in s2.read_items(_prun(src, n) / "polished.jsonl"):
            ev = pitems[r["seed_id"]]["review"]["history"][-1]
            _check(len(ev["raw_response"]) == ev["raw_response_chars"], f"{r['seed_id']}: raw response truncated")
            obj = agent.extract(ev["raw_response"])
            _check({"prompt": obj["prompt"], "answer": obj["answer"]} == r["polished"], f"{r['seed_id']}: re-extracted rewrite differs")
            res = pc.invariance_v2(r["pre_polish"], r["polished"], agent.cited_groups(by_seed[r["seed_id"]]), nca, syn, rules, plain, cols)
            _check(res["check_version"] == POLISH_CHECK_VERSION and res["reasons"] == r["reasons"] and res["checks"] == r["checks"]
                   and res["pass"] == (r["status"] == "polished"), f"{r['seed_id']}: polish checks differ from the recorded result")
            rows.append({"item_id": r["item_id"], "seed_id": r["seed_id"], "pass": res["pass"], "reasons": res["reasons"]})
        out[f"run{n}"] = rows
    return {"checks_reproduced": True, "check_version": POLISH_CHECK_VERSION, "synonyms_sha256": syn["sha256"],
            "descriptor_rules_sha256": rules["sha256"], "plain_language_sha256": plain["sha256"], "items": out["run2"],
            "run1_items": out["run1"]}


# --- D-079, the regression fixture -------------------------------------------------------------------------------


def recheck(item: dict, text: dict, packet: dict, columns: list[str] | None = None) -> dict:
    """Post-checks v3.5 on `text` ({prompt, answer}) as the item's prompt and integrated answer, against its v1b packet; the
    tagged sentences and rubric are the run's (which passed)."""
    cols = columns if columns is not None else bi.column_names()
    x = s2._as_candidate(item)
    x["prompt"], x["reference_answer"]["integrated"] = text["prompt"], text["answer"]
    tagged = copy.deepcopy(item["review"]["history"][0]["reference_answer_tagged"])
    tagged["integrated"] = text["answer"]
    res = bi.synthesis_post_checks(x, tagged, packet["checks_input"], cols, check_version=CHECK_VERSION)
    return {"check_version": res["check_version"], "pass": res["pass"], "reasons": res["reasons"]}


def polish_event(item: dict) -> dict:
    return next(h for h in reversed(item["review"]["history"]) if h.get("event") == "polish")


def display_decision(polish_item: dict, packet: dict, columns: list[str] | None = None) -> dict:
    """D-079: {display_source, display_recheck, display_text}. The re-check runs on the rewrite whatever the polish status
    (recorded either way); the polished text is shown only when the polish passed and the re-check passes."""
    ev = polish_event(polish_item)
    rc = recheck(polish_item, ev["rewrite"], packet, columns)
    use = ev["status"] == "polished" and rc["pass"]
    return {"display_source": "polished" if use else "original",
            "display_recheck": {**rc, "on": "polished text", "polish_status": ev["status"]},
            "display_text": dict(ev["rewrite"] if use else ev["pre_polish"])}


def display_text(item: dict) -> dict:
    """{prompt, answer} a reviewer sees (D-079), from the human_review event, checked against the polish event."""
    hr = next(h for h in reversed(item["review"]["history"]) if h.get("event") == "human_review")
    ev = polish_event(item)
    want = ev["rewrite"] if hr["display_source"] == "polished" else ev["pre_polish"]
    _check(hr["display_text"] == want, f"{item['item_id']}: display text is not the {hr['display_source']} text")
    _check(hr["display_source"] != "polished" or (ev["status"] == "polished" and hr["display_recheck"]["pass"]),
           f"{item['item_id']}: polished display without a passing polish and re-check (D-079)")
    return dict(hr["display_text"])


def run1_regression(items1: list[dict], columns: list[str] | None = None) -> list[dict]:
    """The run-1 passing items under post-checks v3.5 against their v1a packets: pass, with the budget reported (not enforced;
    v1a packets carry no answer shape)."""
    cols = columns if columns is not None else bi.column_names()
    out = []
    for it in sorted(items1, key=lambda x: x["item_id"]):
        if it["item_id"] not in RUN1_PASSING:
            continue
        h = it["review"]["history"][0]
        packet, _ = packet_at(RUN1_SOURCE_COMMIT, RUN1_PACKETS_REL, h["seed_id"])
        res = bi.synthesis_post_checks(s2._as_candidate(it), h["reference_answer_tagged"], packet["checks_input"], cols,
                                       check_version=CHECK_VERSION)
        b = res["checks"]["rung8_report"]["budget"]
        out.append({"item_id": it["item_id"], "check_version": CHECK_VERSION, "packets": "v1a", "pass": res["pass"],
                    "reasons": res["reasons"], "budget": b})
    _check([x["item_id"] for x in out] == list(RUN1_PASSING), "run-1 passing items")
    return out


# --- copy, lifecycle, manifests ------------------------------------------------------------------------------------


def copy_runs(src: Path) -> int:
    src = Path(src)
    n = sum(r2._copy(src / rel, ART / name) for rel, name in {**COPIED, **SUPERSEDED_COPIED}.items())
    n += sum(r2._copy(src / rel, POLISH_ART / name) for rel, name in POLISH_COPIED.items())
    n += sum(r2._copy(src / rel, ART1 / name) for rel, name in RUN1_COPIED.items())
    n += sum(r2._copy(src / rel, POLISH_ART1 / name) for rel, name in RUN1_POLISH_COPIED.items())
    return n


def human_review_item(polish_item: dict, decision: dict, at: str) -> dict:
    _check(polish_item["review"]["status"] == "deterministic_pass", f"{polish_item['item_id']}: status {polish_item['review']['status']}")
    x = copy.deepcopy(polish_item)
    x["review"].update(status="human_review", kaiyuan_disposition=None, mentor_disposition=None, final_frozen=None)
    x["review"]["history"].append({"event": "human_review", "from_status": "deterministic_pass", "decision": "D-033",
                                   "display_rule": DISPLAY_RULE, "at": at, "by": INGEST_BY, **decision, "note": HUMAN_REVIEW_NOTE})
    display_text(x)
    return x


def write_items(src: Path, items: list[dict], at: str, columns: list[str] | None = None) -> list[dict]:
    """`items/<item_id>.json`: six polish-run records + human_review (D-079 display); two rejected run-2 items as delivered."""
    pitems, out = read_polish_items(src), []
    for it in sorted(items, key=lambda x: x["item_id"]):
        sid, iid = it["review"]["history"][0]["seed_id"], it["item_id"]
        if iid in PASSING:
            dec = display_decision(pitems[sid], packet_v1b(sid), columns)
            x = human_review_item(pitems[sid], dec, at)
        else:
            x, dec = it, None
        errs = bi.schema_errors(x) + bi.consistency_errors(x)
        _check(not errs, f"{iid}: invalid: {errs}")
        path = ITEMS_DIR / f"{iid}.json"
        r2.write_json(path, x)
        rec = {"item_id": iid, "seed_id": sid, "path": path.relative_to(ART).as_posix(), "sha256": sha256_file(path),
               "status": x["review"]["status"], "history": [h["event"] for h in x["review"]["history"]],
               "schema_valid": True, "consistency_errors": []}
        if dec:
            rec.update(display_source=dec["display_source"], display_recheck=dec["display_recheck"])
        else:
            rec.update(redraws=REDRAWS, reasons=REJECTED[iid], reading=REJECTED_READING[iid],
                       attempts=[{"attempt": 1, "path": SUPERSEDED_COPIED[f"litsynth/infra_run2/attempt1/{sid}.json"],
                                  "reasons": SUPERSEDED[iid]["reasons"]},
                                 {"attempt": 2, "path": rec["path"], "reasons": REJECTED[iid]}])
        out.append(rec)
    return out


def _excluded(root: Path, copied: dict) -> list[dict]:
    return s4.excluded_files(root, copied)


def manifest(facts: dict, reproduced: dict, written: list[dict], regression: list[dict], src: Path, at: str) -> dict:
    by_id = {x["item_id"]: x for x in written}
    return {
        "run": "infra_run2", "diagnostic_id": "litsynth_infra_run2", "decision": DECISION, "display_rule": DISPLAY_RULE,
        "work_package": WORK_PACKAGE, "tarball": {"name": TARBALL_NAME, "sha256": TARBALL_SHA256},
        "generator": {"version": GENERATOR_VERSION, "agent_path": AGENT_REL, "agent_sha256": AGENT_SHA256,
                      "system_prompt_sha256": SYSTEM_PROMPT_SHA256, "corrective_template_sha256": CORRECTIVE_SHA256,
                      "format_corrective_template_sha256": FORMAT_CORRECTIVE_SHA256},
        "endpoint": {"endpoint_label": ENDPOINT_LABEL, "model": MODEL, "base_url": BASE_URL}, "budget": BUDGET,
        "source_commit": SOURCE_COMMIT,
        "packets": {"version": "synthpackets infra v1b", "path": PACKETS_REL, "at_commit": SOURCE_COMMIT,
                    "manifest_sha256": PACKETS_MANIFEST_SHA256},
        "counts": dict(RUN_FACTS), "items": facts["items"], "format_corrective_items": facts["format_corrective_items"],
        "rung8_reports": facts["rung8_reports"], "log": facts["log"], "items_sha256": ITEMS_SHA256, "summary_sha256": SUMMARY_SHA256,
        "question_diversity": facts["summary"]["question_diversity"],
        "superseded_attempts": [{
            "role": "superseded_attempt", "item_id": iid, "seed_id": v["seed_id"],
            "delivered_as": f"litsynth/infra_run2/attempt1/{v['seed_id']}.json", "path": f"superseded/{iid}_attempt1.json",
            "sha256": v["sha256"], "status": "rejected_pre_review", "reasons": v["reasons"],
            "superseded_by": {"path": by_id[iid]["path"], "sha256": by_id[iid]["sha256"], "status": by_id[iid]["status"]}}
            for iid, v in SUPERSEDED.items()],
        "rejected_pre_review": {iid: {"redraws": REDRAWS, "reasons": REJECTED[iid], "reading": REJECTED_READING[iid]} for iid in REJECTED},
        "checks_reproduced": reproduced["checks_reproduced"], "checks": reproduced,
        "item_schema": {"path": bi.SCHEMA_V2A_PATH.relative_to(REPO_ROOT).as_posix(), "sha256": sha256_file(bi.SCHEMA_V2A_PATH)},
        "lifecycle": {"status": "human_review", "items": list(PASSING), "from": "deterministic_pass", "rule": "D-033",
                      "kaiyuan_disposition": None, "mentor_disposition": None, "final_frozen": None,
                      "rejected_pre_review": sorted(REJECTED),
                      "note": ("items/<item_id>.json: for the six, the polish-run record (run-2 item + its polish event; the text "
                               "is the rewrite where the polish status is polished) + human_review, whose event records "
                               "display_source, display_recheck and display_text (D-079); for BI-P5-0003 and 0005 the run-2 "
                               "item as delivered; items.jsonl is the run's file, byte-identical (pre-polish text)")},
        "display_rule_d079": {"rule": ("display text = the polished text only if the polish passed and post-checks v3.5, re-run on "
                                       "the polished prompt and answer against the v1b packet, pass; otherwise the original"),
                              "display_source": {x["item_id"]: x["display_source"] for x in written if "display_source" in x},
                              "display_recheck": {x["item_id"]: x["display_recheck"] for x in written if "display_recheck" in x}},
        "run1_regression": regression,
        "polish": {"run": "polish/infra_run2", "manifest": "../../polish/infra_run2/manifest.json"},
        "superseded_run": {"run": "infra_run1", "manifest": "../infra_run1/manifest.json"},
        "files": [s4._entry(ART, n) for n in COPIED.values()] + [s4._entry(ART, n) for n in SUPERSEDED_COPIED.values()],
        "items_ingested": written, "excluded_files": _excluded(_run(src), {**COPIED, **SUPERSEDED_COPIED}),
        "ingested_at": at, "ingested_by": "EXECUTOR",
    }


def polish_manifest(facts: dict, reproduced: dict, written: list[dict], src: Path, at: str) -> dict:
    return {
        "run": "polish/infra_run2", "diagnostic_id": "litpolish_infra_run2", "decision": DECISION, "display_rule": DISPLAY_RULE,
        "work_package": WORK_PACKAGE, "tarball": {"name": TARBALL_NAME, "sha256": TARBALL_SHA256},
        "generator": {"version": POLISH_GENERATOR_VERSION, "agent_path": POLISH_AGENT_REL, "agent_sha256": POLISH_AGENT_SHA256,
                      "system_prompt_sha256": POLISH_SYSTEM_PROMPT_SHA256, "corrective_template_sha256": POLISH_CORRECTIVE_SHA256,
                      "check_version": POLISH_CHECK_VERSION},
        "endpoint": {"endpoint_label": ENDPOINT_LABEL, "model": MODEL, "base_url": BASE_URL}, "budget": BUDGET,
        "source_commit": SOURCE_COMMIT, "input": "infra synthesis run 2 (artifacts/benchmark/items/infra_run2)",
        "counts": dict(POLISH_FACTS), "rejected": POLISH_REJECTED, "log": facts["polish_log"],
        "summary_sha256": POLISH_SUMMARY_SHA256, "polished_sha256": POLISHED_SHA256,
        "checks_reproduced": reproduced["checks_reproduced"], "checks": {k: v for k, v in reproduced.items() if k != "run1_items"},
        "display_source": {x["item_id"]: x["display_source"] for x in written if "display_source" in x},
        "files": [s4._entry(POLISH_ART, n) for n in POLISH_COPIED.values()],
        "excluded_files": _excluded(_prun(src), POLISH_COPIED),
        "note": ("four rewrites passed polish checks v2 (BI-P5-0002, 0004, 0006, 0007); BI-P5-0001 and 0008 were rejected. Under "
                 "D-079 only BI-P5-0002's rewrite also passes post-checks v3.5 and is its display text; the item records with "
                 "their polish event are in items/infra_run2/items (human_review)"),
        "ingested_at": at, "ingested_by": "EXECUTOR",
    }


def run1_manifest(facts: dict, reproduced: dict, regression: list[dict], src: Path, at: str) -> dict:
    return {
        "run": "infra_run1", "role": "superseded", "superseded_by": "infra_run2 (D-080)", "work_package": WORK_PACKAGE,
        "tarball": {"name": TARBALL_NAME, "sha256": TARBALL_SHA256},
        "generator": {"version": RUN1_GENERATOR_VERSION, "agent_path": AGENT_REL, "agent_sha256": RUN1_AGENT_SHA256,
                      "system_prompt_sha256": RUN1_SYSTEM_PROMPT_SHA256, "held": "climrr.p5c2 (bytes at b860658)"},
        "endpoint": {"endpoint_label": ENDPOINT_LABEL, "model": MODEL, "base_url": BASE_URL}, "budget": BUDGET,
        "source_commit": RUN1_SOURCE_COMMIT,
        "packets": {"version": "synthpackets infra v1a", "path": RUN1_PACKETS_REL, "at_commit": RUN1_SOURCE_COMMIT,
                    "manifest_sha256": RUN1_PACKETS_MANIFEST_SHA256},
        "counts": dict(RUN1_FACTS), "items": facts["run1_items"], "items_sha256": RUN1_ITEMS_SHA256, "summary_sha256": RUN1_SUMMARY_SHA256,
        "checks_reproduced": True, "checks": reproduced["run1"],
        "regression_fixture": {"items": list(RUN1_PASSING), "file": "items.jsonl", "sha256": RUN1_ITEMS_SHA256,
                               "rule": "the two run-1 passing items pass post-checks v3.5 against their v1a packets, budget reported",
                               "result": regression},
        "files": [s4._entry(ART1, n) for n in RUN1_COPIED.values()],
        "excluded_files": _excluded(_run(src, 1), RUN1_COPIED),
        "note": ("superseded by infra run 2 (agent v5.4, packets v1b); no item enters review. Recorded as relayed in "
                 "P5_INFRA_IMPACT_DESIGN.md section 22 and now in the repository"),
        "ingested_at": at, "ingested_by": "EXECUTOR",
    }


def run1_polish_manifest(reproduced: dict, src: Path, at: str) -> dict:
    return {
        "run": "polish/infra_run1", "role": "superseded", "superseded_by": "polish/infra_run2", "work_package": WORK_PACKAGE,
        "tarball": {"name": TARBALL_NAME, "sha256": TARBALL_SHA256},
        "generator": {"version": POLISH_GENERATOR_VERSION, "agent_sha256": POLISH_AGENT_SHA256, "check_version": POLISH_CHECK_VERSION},
        "source_commit": RUN1_SOURCE_COMMIT, "input": "infra synthesis run 1 (its two passing items)",
        "counts": dict(RUN1_POLISH_FACTS), "summary_sha256": RUN1_POLISH_SUMMARY_SHA256, "polished_sha256": RUN1_POLISHED_SHA256,
        "checks_reproduced": True, "checks": reproduced["run1_items"],
        "files": [s4._entry(POLISH_ART1, n) for n in RUN1_POLISH_COPIED.values()],
        "excluded_files": _excluded(_prun(src, 1), RUN1_POLISH_COPIED),
        "ingested_at": at, "ingested_by": "EXECUTOR",
    }
