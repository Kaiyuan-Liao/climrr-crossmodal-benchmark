"""LITCORPUS-03 infra extraction run 1 and its query runs: verification, ingest, evidence roles, independence (P5b; D-074).

The delivered `infra_run1_evidence.tar.gz` holds:

- `litstatements/infra_run1/<item_id>/{prompt_user.txt, response.json, result.json}` for 572 papers, `statements.jsonl`,
  `summary.json`, `agent.log` (litstatement_agent v4.1, arm `infra_impact_v1`, Sophia `openai/gpt-oss-120b`, reasoning
  low, max_tokens 6000, source commit `157e49d`);
- `runs/infra_lexicon_v2/` (run_query v4.1, DR-CAND-INFRA-2: the v2 diagnostic, D-070a) and `runs/infra_lexicon_v3/`
  (run_query v4.2, DR-CAND-INFRA-3, D-070b: the candidates the extraction read);
- `inventory/litcorpus03_inventory{,_v11}.json` (inventory_corpus v1 / v1.1), `index/critical_infrastructure_v1/
  index_summary.json`, and the logs under `reports/`.

`verify_source` re-derives every fact the work package states and raises on any difference. `copy_run` copies into
`artifacts/litstatements/infra_run1/` `statements.jsonl`, `summary.json`, `agent.log` and every `result.json` (as
`papers/<item_id>.json`, byte-identical); `prompt_user.txt` (the paper text; the corpus stays external) and
`response.json` are not copied (SHA-256 in `manifest.json`). `copy_corpus_evidence` copies into
`artifacts/literature/litcorpus03/` the two inventories, the index summary, both query summaries, the v3
`basis_b_only.json` and the logs; files that hold an absolute Eagle path are written with the path replaced by a
placeholder (`litcorpus.redact`, the LITCORPUS-02 rule) and both SHA-256 recorded in `redactions.json`. The v3
`candidates.json` is pinned byte-identical as `data/metadata/softqa/infra_candidates_v1.json` (manifest entry);
`paper_hits.jsonl` (both runs) and the v2 `candidates.json` are not copied (SHA-256 in the corpus manifest).

Statement ids `LS3-<item_id>-<nn>` (nn = the agent's position, S-<item_id>-<nn>). **Evidence roles** as for run 2
(D-044; `litstatements_run2.evidence_role`: core / cited / background_consensus / unusable), and a passing (`deterministic_pass`)
`impact` statement also gets `impact_candidate: true` (EXECUTOR reading of "plus `impact_candidate`", for confirmation:
a flag beside the role, so that strength under D-045 still reads the role). **Hazard family** of a statement:
`hazard_family` where the agent set it (impact statements: computed from `hazard_term`); for the other types the family
of `hazard_term` by the same lookup (governed terms, then the proxy terms of `hazard_proxy_lexicon_v1a`), else the
paper's only candidate family, else `None` (`family_basis` records which; EXECUTOR rule, for confirmation).

**Independence (DR-LIT-IND-1 v2, D-046)** over the 572 papers: `litindependence.build` with each paper's `paper_sha256`
and the `[SECTION: title]` of its `prompt_user.txt` (title kept as a hash). The inventory's corpus-wide duplicate groups
are listed only as their first ten, under another normalisation (NFKC), so they are reported, not used.

Nothing here calls a model, reads a table value, or changes the concept map, a column status or a compatibility rule.
"""

from __future__ import annotations

import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from climrr import litcorpus as lc
from climrr import litgeo as lg
from climrr import litindependence as li
from climrr import litstatements_run2 as r2
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

RUN_ID = "litstatements_infra_run1"
DECISION = "D-074"
ART = REPO_ROOT / "artifacts" / "litstatements" / "infra_run1"
PAPERS_DIR = ART / "papers"
MANIFEST_PATH = ART / "manifest.json"
INGESTED_PATH = ART / "statements_ingested.jsonl"
INDEPENDENCE_PATH = ART / "independence_v2.json"
REPORT_PATH = ART / "breakdowns.json"
CORPUS_DIR = REPO_ROOT / "artifacts" / "literature" / "litcorpus03"
CORPUS_MANIFEST_PATH = CORPUS_DIR / "litcorpus03_evidence_manifest.json"
REDACTIONS_PATH = CORPUS_DIR / "redactions.json"
CANDIDATES_PIN_PATH = REPO_ROOT / "data" / "metadata" / "softqa" / "infra_candidates_v1.json"

TARBALL_NAME = "infra_run1_evidence.tar.gz"
TARBALL_SHA256 = "218a9a430daf249f340c6ecbe46dd03c610bc77069520a93171d131655a1ad5a"
STATEMENTS_SHA256 = "86750028968a869419849b3097d7f2335c9baa3512ee42913cd42d4f5ad70b01"
SUMMARY_SHA256 = "952280a175dd96e00460f1786c9b73eac2a3470192aacf21f38484584a8b1286"
SYSTEM_PROMPT_SHA256 = "945b487ca515d89fd25755d82e3c4d63e662888dea61f9f386028857ed69e095"
SOURCE_COMMIT = "157e49d5135cbdb6c15cc4aee4ad286351e75061"
GENERATOR_VERSION = "litstatement_agent v4.1"
ARM = "infra_impact_v1"
INDEX_IDENTITY = "2dfc8eca533a0e983c4863e712b37ce35a08bc4980996d1483b711b05e3ff725"
INDEX_MANIFEST_CSV_SHA256 = "fc53ab3a73e8a18c61938a4ac9c1a67e81b126df7107a600b1d1638f10a5f42e"
ENDPOINT_LABEL, MODEL, BASE_URL = "sophia_vllm", "openai/gpt-oss-120b", r2.BASE_URL
BUDGET = {"reasoning_effort": "low", "max_tokens": 6000}

#: The query runs (D-070a v2 diagnostic; D-070b the candidates). SHA-256 of the delivered files.
QUERY_RUNS = {
    "infra_lexicon_v2": {"tool": "run_query v4.1", "rule": "DR-CAND-INFRA-2", "decision": "D-070a", "role": "v2 diagnostic (superseded for the pilot by v3)",
                         "files": {"summary.json": "b81f2b4ddbdf94c3b0a9fe670aaf14401247c763d6372f7500035d027d243b49",
                                   "candidates.json": "af8a37598ca1888b46defbd6e018374a1cd10d8c30066f8715874d5b9e8792ac",
                                   "paper_hits.jsonl": "26864b97525ef05039c8885412c5148f1a1b3dae8bba700d946bf33e0a146010"},
                         "n_candidates": 588},
    "infra_lexicon_v3": {"tool": "run_query v4.2", "rule": "DR-CAND-INFRA-3", "decision": "D-070b", "role": "the candidates infra run 1 read",
                         "files": {"summary.json": "55e2674562c81e6e1378fe48a59bc2e04cabc114be71cc5a7888759e81ca8c28",
                                   "candidates.json": "079687206168f75c2e8e924391b8db18f3b1659fc5e3a2f6177dabcf0309b176",
                                   "paper_hits.jsonl": "dc208d70f7eaf03af5beec8d9a134832f491c2e217a763609e3e5f7cc77b0174",
                                   "basis_b_only.json": "067ef97f5a88b64c4008113e97f2baaf199be4f2e8d68abbcb682b3a782150c1"},
                         "n_candidates": 572},
}
INVENTORY_V1_IDENTITY = INDEX_IDENTITY
INDEX_DISTINCT_SHA256 = 89388
CORPUS_FILES = 89497

#: The run's facts as the work package states them; the ingest fails if any differs.
RUN_FACTS = {"papers": 572, "papers_with_error": 0, "papers_over_limit": 0, "truncated": 31, "statements": 407,
             "deterministic_pass": 210, "rejected_pre_review": 197, "papers_zero_statements": 407, "papers_productive": 165}
BY_TYPE = {"impact": 264, "driver": 79, "mechanism": 38, "pattern": 14, "caveat": 5, "consensus": 5, "background": 2}
BY_RECOVERY = {"exact": 213, "prefix_anchor": 83, "normalized": 30, "not_found": 81}
#: Asset classes the work package names (over all impact statements); the rest are recorded as observed.
BY_ASSET_CLASS_STATED = {"energy": 120, "transportation_systems": 49, "water_and_wastewater": 24,
                         "healthcare_and_public_health": 21, "emergency_services": 13, "other": 22}
BY_HAZARD_RELATION = {"broader_hazard": 242, "governed_term": 12, "None": 10}

COPIED = {
    "litstatements/infra_run1/statements.jsonl": "statements.jsonl",
    "litstatements/infra_run1/summary.json": "summary.json",
    "litstatements/infra_run1/agent.log": "agent.log",
}
#: Corpus evidence copied to artifacts/literature/litcorpus03/ (source -> destination); redacted where it holds a path.
CORPUS_COPIED = {
    "inventory/litcorpus03_inventory.json": "inventory/litcorpus03_inventory.json",
    "inventory/litcorpus03_inventory_v11.json": "inventory/litcorpus03_inventory_v11.json",
    "index/critical_infrastructure_v1/index_summary.json": "index/index_summary.json",
    "runs/infra_lexicon_v2/summary.json": "runs/infra_lexicon_v2/summary.json",
    "runs/infra_lexicon_v3/summary.json": "runs/infra_lexicon_v3/summary.json",
    "runs/infra_lexicon_v3/basis_b_only.json": "runs/infra_lexicon_v3/basis_b_only.json",
    "reports/litcorpus03_inventory.log": "logs/litcorpus03_inventory.log",
    "reports/litcorpus03_inventory_v11.log": "logs/litcorpus03_inventory_v11.log",
    "reports/litcorpus03_index_build.log": "logs/litcorpus03_index_build.log",
    "reports/infra_lexicon_v2.log": "logs/infra_lexicon_v2.log",
    "reports/infra_lexicon_v3.log": "logs/infra_lexicon_v3.log",
    "reports/litstatements_infra_run1.log": "logs/litstatements_infra_run1.log",
}
NOT_COPIED = ("runs/infra_lexicon_v2/candidates.json", "runs/infra_lexicon_v2/paper_hits.jsonl",
              "runs/infra_lexicon_v3/paper_hits.jsonl")
EXCLUDED_NAMES = ("prompt_user.txt", "response.json")
US_PLACE_CLASSES = ("state", "nca", "us_subregion", "us_national")


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _run(src: Path) -> Path:
    return Path(src) / "litstatements" / "infra_run1"


def _load(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _result_paths(run: Path) -> list[Path]:
    return sorted(run.glob("*/result.json"))


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]


def parse_log(text: str) -> dict:
    lines = text.splitlines()
    kv = lambda ln: dict(re.findall(r"(\w+)=(\S+)", ln))  # noqa: E731
    start = [ln for ln in lines if " START " in ln]
    done = [ln for ln in lines if " DONE " in ln]
    _check(len(start) == 1 and len(done) == 1, f"expected one START and one DONE line, found {len(start)} and {len(done)}")
    paper = [ln for ln in lines if " arm=" in ln and " START " not in ln]
    return {"start": kv(start[0]), "done": kv(done[0]), "start_utc": start[0].split()[0], "end_utc": done[0].split()[0],
            "paper_lines": len(paper), "trunc_lines": sum(" TRUNC " in ln for ln in paper),
            "retry_lines": sum(" RETRY " in ln for ln in lines), "fail_lines": sum(" FAIL " in ln for ln in lines),
            "err_not_none": sum("err=None" not in ln for ln in paper)}


def verify_source(src: Path) -> dict:
    """Every infra-run-1 and query fact the work package states, re-derived from the delivered files. Raises on any difference."""
    src, run = Path(src), _run(src)
    _check(sha256_file(run / "statements.jsonl") == STATEMENTS_SHA256, "statements.jsonl SHA-256 differs")
    _check(sha256_file(run / "summary.json") == SUMMARY_SHA256, "summary.json SHA-256 differs")
    for name, q in QUERY_RUNS.items():
        for f, h in q["files"].items():
            _check(sha256_file(src / "runs" / name / f) == h, f"runs/{name}/{f} SHA-256 differs from {h}")
    results = [_load(p) for p in _result_paths(run)]
    _check(len(results) == RUN_FACTS["papers"], f"{len(results)} result.json, expected {RUN_FACTS['papers']}")
    _check(all("statements" in r for r in results), "a result.json records an error")
    lines = [json.dumps(x, ensure_ascii=False) for r in results for x in r["statements"]]
    _check((run / "statements.jsonl").read_text(encoding="utf-8") == "".join(ln + "\n" for ln in lines),
           "statements.jsonl is not the concatenation of the result.json files")
    recs = [x for r in results for x in r["statements"]]
    k = Counter(x["status"] for x in recs)
    _check(len(recs) == RUN_FACTS["statements"], f"{len(recs)} statements, expected {RUN_FACTS['statements']}")
    for s in ("deterministic_pass", "rejected_pre_review"):
        _check(k[s] == RUN_FACTS[s], f"{k[s]} {s}, expected {RUN_FACTS[s]}")
    _check(sum(r.get("model_parse_error") is not None for r in results) == RUN_FACTS["papers_with_error"], "papers with a parse error")
    _check(sum(bool(r.get("truncated")) for r in results) == RUN_FACTS["truncated"], "truncated papers")
    zero = sum(not r["statements"] for r in results)
    _check(zero == RUN_FACTS["papers_zero_statements"] and len(results) - zero == RUN_FACTS["papers_productive"],
           f"{zero} papers with zero statements, expected {RUN_FACTS['papers_zero_statements']}")
    _check(dict(Counter(x["proposal"]["statement_type"] for x in recs)) == BY_TYPE, "statements by type differ")
    _check(dict(Counter(x["passage_recovery"] for x in recs)) == BY_RECOVERY, "recovery counts differ")
    imp = [x for x in recs if x["proposal"]["statement_type"] == "impact"]
    ac = Counter(x["proposal"].get("asset_class") for x in imp)
    for c, n in BY_ASSET_CLASS_STATED.items():
        _check(ac.get(c, 0) == n, f"asset class {c}: {ac.get(c, 0)}, expected {n}")
    _check(dict(Counter(str(x.get("hazard_relation")) for x in imp)) == BY_HAZARD_RELATION, "hazard relations differ")
    s = _load(run / "summary.json")
    for key in ("papers", "statements", "deterministic_pass", "rejected_pre_review", "papers_with_error", "papers_over_limit"):
        _check(s[key] == RUN_FACTS[key], f"summary {key}={s[key]}, expected {RUN_FACTS[key]}")
    _check(s["by_statement_type"] == BY_TYPE and s["by_recovery"] == BY_RECOVERY, "summary type / recovery differ")
    _check(s["by_hazard_relation"] == BY_HAZARD_RELATION, "summary hazard relation differs")
    _check(s["by_asset_class"] == dict(ac), "summary asset classes differ from the records")
    _check(s["rejected_by_check"] == dict(Counter(c for x in recs for c in x["pre_review_checks"]["failed"])),
           "summary rejected_by_check differs from the records")
    _check(s["endpoints_in_results"] == {f"{ENDPOINT_LABEL} {MODEL} {BASE_URL}": RUN_FACTS["papers"]}, "summary endpoints differ")
    for r in results:
        _check(r["endpoint_label"] == ENDPOINT_LABEL and r["model"] == MODEL and r["base_url"] == BASE_URL, f"{r['item_id']}: endpoint")
        _check(r["generator_version"] == GENERATOR_VERSION and r["arm"] == ARM, f"{r['item_id']}: generator / arm")
        _check(r["system_prompt_sha256"] == SYSTEM_PROMPT_SHA256, f"{r['item_id']}: system prompt")
        _check(r["reasoning_effort"] == BUDGET["reasoning_effort"] and r["reasoning_effort_applied"] is True, f"{r['item_id']}: reasoning")
        for i, x in enumerate(r["statements"], 1):
            _check(x["statement_id"] == f"S-{r['item_id']}-{i:02d}", f"{x['statement_id']}: not at position {i}")
            _check(x["system_prompt_sha256"] == SYSTEM_PROMPT_SHA256 and x["source_commit"] == SOURCE_COMMIT,
                   f"{x['statement_id']}: system prompt / source commit")
            _check(x["max_tokens"] == BUDGET["max_tokens"] and x["candidate_arm"] == ARM, f"{x['statement_id']}: budget / arm")
    agent_log = (run / "agent.log").read_text(encoding="utf-8")
    _check(agent_log == (src / "reports" / "litstatements_infra_run1.log").read_text(encoding="utf-8"),
           "agent.log and reports/litstatements_infra_run1.log differ")
    log = parse_log(agent_log)
    exp = {"arm": ARM, "reasoning_effort": "low", "max_tokens": "6000", "candidates": str(RUN_FACTS["papers"]),
           "endpoint_label": ENDPOINT_LABEL, "model": MODEL, "base_url": BASE_URL, "system_sha": SYSTEM_PROMPT_SHA256[:12],
           "index": INDEX_IDENTITY[:12]}
    for key, v in exp.items():
        _check(log["start"].get(key) == v, f"log START {key}={log['start'].get(key)!r}, expected {v!r}")
    for key, f in (("papers", "papers"), ("statements", "statements"), ("deterministic_pass", "pass"), ("rejected_pre_review", "reject")):
        _check(log["done"].get(f) == str(RUN_FACTS[key]), f"log DONE {f}={log['done'].get(f)!r}")
    _check(log["paper_lines"] == RUN_FACTS["papers"] and log["fail_lines"] == 0 and log["err_not_none"] == 0, "log paper / FAIL lines")
    _check(log["trunc_lines"] == RUN_FACTS["truncated"], f"log TRUNC lines {log['trunc_lines']}")
    # the candidates the run read: v3, the same 572 papers
    cand = _load(src / "runs" / "infra_lexicon_v3" / "candidates.json")
    _check(cand["rule"] == "DR-CAND-INFRA-3" and cand["arm"] == ARM and cand["n_candidates"] == RUN_FACTS["papers"], "v3 candidates header")
    _check(cand["index_content_identity_sha256"] == INDEX_IDENTITY, "v3 candidates index identity")
    _check(sorted(c["item_id"] for c in cand["candidates"]) == sorted(r["item_id"] for r in results),
           "the run's papers are not the v3 candidates")
    v3s = _load(src / "runs" / "infra_lexicon_v3" / "summary.json")
    _check(v3s["candidates_sha256"] == QUERY_RUNS["infra_lexicon_v3"]["files"]["candidates.json"], "v3 summary candidates hash")
    v2s = _load(src / "runs" / "infra_lexicon_v2" / "summary.json")
    _check(v2s["n_candidates"] == QUERY_RUNS["infra_lexicon_v2"]["n_candidates"]
           and v2s["candidates_sha256"] == QUERY_RUNS["infra_lexicon_v2"]["files"]["candidates.json"], "v2 summary")
    # corpus identity
    idx = _load(src / "index" / "critical_infrastructure_v1" / "index_summary.json")
    _check(idx["content_identity_sha256"] == INDEX_IDENTITY and idx["manifest_csv_sha256"] == INDEX_MANIFEST_CSV_SHA256
           and idx["distinct_sha256"] == INDEX_DISTINCT_SHA256 and idx["files"] == CORPUS_FILES, "index summary facts")
    for f, ver in (("litcorpus03_inventory.json", "inventory_corpus v1"), ("litcorpus03_inventory_v11.json", "inventory_corpus v1.1")):
        inv = _load(src / "inventory" / f)
        _check(inv["tool_version"] == ver and inv["content_identity_sha256"] == INVENTORY_V1_IDENTITY and inv["files"] == CORPUS_FILES,
               f"{f}: identity / files")
    return {"log": log, "results": len(results), "candidates_both_families": v3s["candidates_in_both_families"]}


# --- copy -------------------------------------------------------------------------------------------


def _copy(src_file: Path, dest: Path) -> bool:
    if dest.exists():
        if sha256_file(dest) != sha256_file(src_file):
            raise ValueError(f"{dest} exists and differs from {src_file.name}")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src_file, dest)
    return True


def copy_run(src: Path) -> int:
    src, n = Path(src), 0
    for rel, name in COPIED.items():
        n += _copy(src / rel, ART / name)
    for p in _result_paths(_run(src)):
        n += _copy(p, PAPERS_DIR / f"{p.parent.name}.json")
    return n


def copy_corpus_evidence(src: Path) -> dict:
    """Copy the corpus evidence (redacting absolute Eagle paths) and pin the v3 candidates. Returns the redactions record."""
    src, red = Path(src), {}
    for rel, dest_rel in CORPUS_COPIED.items():
        text = (src / rel).read_text(encoding="utf-8")
        redacted, counts = lc.redact(text)
        dest = CORPUS_DIR / dest_rel
        if dest.exists() and dest.read_text(encoding="utf-8") != redacted:
            raise ValueError(f"{dest} exists and differs from the (redacted) delivered file")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(redacted, encoding="utf-8", newline="")
        if counts:
            red[f"artifacts/literature/litcorpus03/{dest_rel}"] = {"source": rel, "original_sha256": sha256_file(src / rel),
                                                                     "redacted_sha256": sha256_file(dest), "substitutions": counts}
    _copy(src / "runs" / "infra_lexicon_v3" / "candidates.json", CANDIDATES_PIN_PATH)
    return {"rule": "absolute Eagle paths -> <LITCOLLECT_ROOT_POLARIS> / <EAGLE_DIR> (climrr.litcorpus.REDACTION_RULES)", "files": red}


def excluded_files(src: Path) -> list[dict]:
    run = _run(src)
    return [{"path": f"litstatements/infra_run1/{p.parent.name}/{p.name}", "sha256": sha256_file(p), "bytes": p.stat().st_size}
            for p in sorted(run.glob("*/*")) if p.name in EXCLUDED_NAMES]


# --- records ----------------------------------------------------------------------------------------


#: The agent's own lookup tables (litstatement_agent v4.1 `INFRA_HAZARD_FAMILY`, `INFRA_PROXY_TERMS`; equality tested).
AGENT_GOVERNED_TERMS = {"heat_index": ("heat index", "heat-index", "extended heat index", "days hot and humid enough to be dangerous",
                                       "dangerous heat-index days"),
                        "fire_weather_index": ("fire weather index", "FWI", "fire-weather index", "canadian forest fire weather index",
                                               "canadian fwi", "fire-weather danger (how hot, dry and windy conditions favour fire)",
                                               "fire-weather danger")}
AGENT_PROXY_TERMS = {"heat_index": ("extreme heat", "heat wave", "heat waves", "heatwave", "heatwaves", "high temperatures", "hot days",
                                    "humid heat"),
                     "fire_weather_index": ("fire weather", "fire danger", "fire-weather", "wildfire", "wildfires", "wildland fire")}


def family_lookup() -> dict:
    """term (lowercase) -> (relation, family), in the agent's order: governed terms, then proxy terms (`hazard_relation_of`)."""
    out = {}
    for rel, table in (("governed_term", AGENT_GOVERNED_TERMS), ("broader_hazard", AGENT_PROXY_TERMS)):
        for fam, terms in table.items():
            for t in terms:
                out.setdefault(t.lower(), (rel, fam))
    return out


def statement_family(rec: dict, lookup: dict) -> tuple[str | None, str]:
    """(hazard family, basis) --- module docstring."""
    if rec.get("hazard_family"):
        return rec["hazard_family"], "agent_hazard_family"
    term = str(rec["proposal"].get("hazard_term") or "").strip().lower()
    if term in lookup:
        return lookup[term][1], "hazard_term_lookup"
    fams = sorted({f["family"] for f in rec.get("candidate_families") or []})
    if len(fams) == 1:
        return fams[0], "paper_only_candidate_family"
    return None, "unassigned_paper_in_both_families" if len(fams) > 1 else "unassigned"


def ingest_record(rec: dict, lookup: dict) -> dict:
    iid, nn = rec["paper_item_id"], rec["statement_id"].rsplit("-", 1)[1]
    fam, basis = statement_family(rec, lookup)
    out = {"statement_id": f"LS3-{iid}-{nn}", "agent_statement_id": rec["statement_id"]}
    out.update({k: v for k, v in rec.items() if k != "statement_id"})
    passing = rec["status"] == "deterministic_pass"
    out.update({"precheck_status": "pass" if passing else "rejected", "rejected_checks": list(rec["pre_review_checks"]["failed"]),
                "recovery": rec["passage_recovery"], "evidence_role": r2.evidence_role(rec),
                "impact_candidate": passing and rec["proposal"]["statement_type"] == "impact",
                "statement_family": fam, "statement_family_basis": basis, "corpus": "LITCORPUS-03"})
    return out


def ingested_records(papers_dir: Path = PAPERS_DIR, lookup: dict | None = None) -> list[dict]:
    lookup = lookup if lookup is not None else family_lookup()
    out = []
    for p in sorted(papers_dir.glob("*.json"), key=lambda q: q.stem):
        out.extend(ingest_record(x, lookup) for x in _load(p)["statements"])
    return out


# --- independence -----------------------------------------------------------------------------------


def independence(src: Path) -> dict:
    run, papers = _run(src), []
    for p in _result_paths(run):
        r = _load(p)
        papers.append({"item_id": r["item_id"], "paper_sha256": r["paper_sha256"],
                       "title": r2._title((p.parent / "prompt_user.txt").read_text(encoding="utf-8"))})
    out = li.build(papers)
    out["corpus"] = "LITCORPUS-03 (infra run 1 papers)"
    out["inventory_duplicates_note"] = ("the inventory's corpus-wide duplicate groups (by content SHA-256: 103 groups; by "
                                        "normalised title: 891) list only the first ten and use NFKC normalisation; reported, not used")
    return out


# --- breakdowns ---------------------------------------------------------------------------------------


def breakdowns(records: list[dict], gz: lg.Gazetteer) -> dict:
    passing = [r for r in records if r["precheck_status"] == "pass"]
    imp = [r for r in passing if r["proposal"]["statement_type"] == "impact"]
    geo = {r["statement_id"]: lg.classify(r["proposal"].get("region"), r["proposal"].get("region_scope"), gz) for r in records}
    tri = Counter((r["proposal"]["statement_type"], r["proposal"].get("asset_class") if r["proposal"]["statement_type"] == "impact" else "-",
                   r["statement_family"] or "unassigned") for r in passing)
    us = [r for r in imp if geo[r["statement_id"]]["class"] in US_PLACE_CLASSES]
    none_rel = [r for r in records if r["proposal"]["statement_type"] == "impact" and r.get("hazard_relation") is None]
    return {
        "passing_by_type": dict(sorted(Counter(r["proposal"]["statement_type"] for r in passing).items())),
        "passing_by_type_asset_family": [{"statement_type": t, "asset_class": a, "hazard_family": f, "n": n}
                                         for (t, a, f), n in sorted(tri.items())],
        "passing_impact_by_asset_family": {f"{a} | {f}": n for (t, a, f), n in sorted(tri.items()) if t == "impact"},
        "passing_impact_by_hazard_relation": dict(sorted(Counter(str(r.get("hazard_relation")) for r in imp).items())),
        "passing_impact_geography_v2": dict(sorted(Counter(geo[r["statement_id"]]["class"] for r in imp).items())),
        "passing_impact_naming_us_place": {"n": len(us), "classes": list(US_PLACE_CLASSES),
                                           "by_class": dict(sorted(Counter(geo[r["statement_id"]]["class"] for r in us).items())),
                                           "statements": [{"statement_id": r["statement_id"], "class": geo[r["statement_id"]]["class"],
                                                           "classification": geo[r["statement_id"]]["classification"],
                                                           "region": r["proposal"].get("region"), "asset_class": r["proposal"].get("asset_class"),
                                                           "hazard_family": r["statement_family"]} for r in us]},
        "passing_by_family_basis": dict(sorted(Counter(r["statement_family_basis"] for r in passing).items())),
        "impact_hazard_relation_none": [{"statement_id": r["statement_id"], "status": r["status"], "hazard_term": r["proposal"].get("hazard_term"),
                                         "asset_class": r["proposal"].get("asset_class"), "rejected_checks": r["rejected_checks"],
                                         "statement": r["proposal"]["statement"]} for r in none_rel],
        "evidence_roles": dict(sorted(Counter(r["evidence_role"] for r in records).items())),
        "impact_candidates": sum(r["impact_candidate"] for r in records),
        "geography_rule": lg.VERSION,
    }


# --- manifests -----------------------------------------------------------------------------------------


def _file_entry(path: Path, base: Path) -> dict:
    return {"path": path.relative_to(base).as_posix(), "sha256": sha256_file(path), "bytes": path.stat().st_size}


def manifest(facts: dict, excluded: list[dict], records: list[dict], ingested_at: str | None = None) -> dict:
    files = [_file_entry(ART / n, ART) for n in COPIED.values()]
    files += [_file_entry(p, ART) for p in sorted(PAPERS_DIR.glob("*.json"), key=lambda q: q.stem)]
    files += [_file_entry(p, ART) for p in (INGESTED_PATH, INDEPENDENCE_PATH, REPORT_PATH)]
    return {
        "run": "infra_run1", "diagnostic_id": RUN_ID, "decision": DECISION, "corpus": "LITCORPUS-03",
        "tarball": {"name": TARBALL_NAME, "sha256": TARBALL_SHA256},
        "counts": {**RUN_FACTS, "by_statement_type": BY_TYPE, "by_recovery": BY_RECOVERY,
                   "evidence_roles": dict(sorted(Counter(r["evidence_role"] for r in records).items())),
                   "impact_candidates": sum(r["impact_candidate"] for r in records)},
        "generator": {"version": GENERATOR_VERSION, "arm": ARM, "system_prompt_sha256": SYSTEM_PROMPT_SHA256, **BUDGET},
        "endpoint": {"endpoint_label": ENDPOINT_LABEL, "model": MODEL, "base_url": BASE_URL},
        "source_commit": SOURCE_COMMIT, "candidates": {"run": "infra_lexicon_v3", "rule": "DR-CAND-INFRA-3",
                                                       "pinned_as": "data/metadata/softqa/infra_candidates_v1.json",
                                                       "sha256": QUERY_RUNS["infra_lexicon_v3"]["files"]["candidates.json"]},
        "log": {k: facts["log"][k] for k in ("start_utc", "end_utc", "retry_lines", "fail_lines", "trunc_lines")},
        "statement_ids": "LS3-<item_id>-<nn>, nn = position in the paper's statement list (the agent's S-<item_id>-<nn>)",
        "files": files, "excluded_files": excluded,
        "ingested_at": ingested_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "ingested_by": "EXECUTOR",
    }


def corpus_manifest(src: Path, redactions: dict, ingested_at: str | None = None) -> dict:
    src = Path(src)
    return {
        "corpus_id": "LITCORPUS-03", "decision": "D-070, D-070a, D-070b, D-074", "tarball": {"name": TARBALL_NAME, "sha256": TARBALL_SHA256},
        "index": {"content_identity_sha256": INDEX_IDENTITY, "manifest_csv_sha256": INDEX_MANIFEST_CSV_SHA256,
                  "distinct_sha256": INDEX_DISTINCT_SHA256, "files": CORPUS_FILES},
        "query_runs": {k: {kk: vv for kk, vv in v.items()} for k, v in QUERY_RUNS.items()},
        "query_history": ("v2 (DR-CAND-INFRA-2, D-070a) ran first and was read as a diagnostic: 'high temperatures' alone "
                          "admitted most heat papers; v3 (DR-CAND-INFRA-3, D-070b: conditional 'high temperatures', basis a "
                          "only, impact first) produced the 572 candidates infra run 1 read"),
        "candidates_pinned": {"path": "data/metadata/softqa/infra_candidates_v1.json", "sha256": sha256_file(CANDIDATES_PIN_PATH)},
        "files": [_file_entry(p, CORPUS_DIR) for p in sorted(CORPUS_DIR.rglob("*")) if p.is_file()
                  and p.name not in (CORPUS_MANIFEST_PATH.name,)],
        "not_copied": [{"path": rel, "sha256": sha256_file(src / rel), "bytes": (src / rel).stat().st_size} for rel in NOT_COPIED],
        "redactions": redactions,
        "ingested_at": ingested_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "ingested_by": "EXECUTOR",
    }


write_json = r2.write_json
write_jsonl = r2.write_jsonl
