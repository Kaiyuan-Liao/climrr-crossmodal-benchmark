"""Literature statements (pilot P1, D-039, D-041, D-043): the agent's output, read back.

`scripts/litcollect/litstatement_agent.py` (derived from `softqa_agent.py` v2, whose
locator it imports) asks the model for up to six **general statements** a paper
supports about fire weather / fire danger indices or heat index / humid heat ---
mechanism, driver, consensus, caveat or pattern --- each with a verbatim passage,
and runs the deterministic pre-check: passage re-slice (exact → normalized →
prefix_anchor, recovery recorded) and at most 700 characters; `background`
passages rejected; no digit-heavy value in a statement unless
`generality: specific_result`; an `elsewhere_in_paper` scenario or time keeps its
value only if its quote re-slices exactly, else it becomes `unsupported`. No table
value, unit definition or computed answer reaches the model.

A statement that passes is still **one paper's citation**, not a pattern or a
consensus (D-036; ruling 2): evidence strength is assigned later, at cross-paper
aggregation (pilot P2), and `to_support` turns a passing record into the
`supports[]` entry of item schema v2 for that stage.

Nothing here calls a model, reads table values, or touches the concept map,
column statuses or compatibility rules.

**Polaris invocation** (the agent stays byte-identical to the file that runs, so
its invocation is documented here, as for Track C). `$CLIMRR_REPO` is a checkout
of the pinned commit; run from the litcollect root so `index/…` and the output
directory stay relative and no absolute path lands in any output; the ALCF
inference credential is in the environment variable the agent's `main` reads
(the same variable whichever `--base-url` is given). `softqa_agent.py` must sit beside the
agent (it does in the repository).

Run 1 --- the 243 frozen place candidates first, on Sophia vLLM (D-043; Metis
remains the fallback when the Sophia job is down --- drop `--base-url` / `--model`,
and use one host per run):

    cd "$LITCOLLECT_ROOT_POLARIS"
    PYTHONPATH="$CLIMRR_REPO/src" python "$CLIMRR_REPO/scripts/litcollect/litstatement_agent.py" \\
      --candidates "$CLIMRR_REPO/data/metadata/softqa/trackc_candidates_v1.json" \\
      --index index/full_705k_v2_filtered --out litstatements/run1 \\
      --base-url https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1 --model openai/gpt-oss-120b \\
      --sleep 2 --source-commit "$(git -C $CLIMRR_REPO rev-parse HEAD)" 2>&1 | tee -a reports/litstatements_run1.log

Reusing `--out litstatements/run1` is intended: on start the agent moves each
run-1 `result.json` that records an HTTP error (the Metis 504/502 papers) to
`result.failed_<timestamp>.json` and processes that paper again; finished papers
are skipped.

Then, optionally, the full LITCORPUS-02 (1,308 items): a new frozen candidates
file `data/metadata/benchmark/litstatement_candidates_litcorpus02_v1.json`, built
by a later package from the two arm manifests
`artifacts/literature/litcorpus02/fire_weather_v1_manifest.csv` and
`extreme_heat_v1_manifest.csv` (union per `lit2_ids.csv`, 1,308 rows; one arm per
item, as `[{item_id, arm}]`) and pinned in the manifest before the run --- not
built here. The 243 already processed are skipped if the same `--out` is reused
(restartable per paper).

Defaults: Metis `gpt-oss-120b`, temperature 0, `--max-chars 90000` (a longer
paper is truncated and flagged), `--max-tokens 3500`, `--timeout 300`,
`--sleep 0`; the reasoning-field fallback of `call_model` applies. Every record,
`result.json` and `summary.json` carries `base_url`, `model` and `endpoint_label`
(`metis` / `sophia_vllm` / `other`). HTTP 5xx, connection errors, timeouts and
empty or unparseable bodies are retried 3 times (10 s / 30 s / 60 s, `RETRY`
lines); a paper that still fails, or gets a 4xx, has no `result.json` (`FAIL`
line) and is appended to `failed_papers.txt`, so a restart retries it.
Restartable: a paper with `result.json` is skipped; `statements.jsonl` and
`summary.json` are rebuilt from every `result.json` at the end of each
invocation. Run evidence: `agent.log`, per-paper `result.json` /
`prompt_user.txt` / `response.json` (and any `result.failed_*.json`),
`failed_papers.txt`, `statements.jsonl`, `summary.json`.

Run 2 (agent v2, Sophia vLLM, at `7919bbf`) is ingested by
`scripts/ingest_litstatements.py` (`litstatements_run2.py`; D-044). Its 21 parse
errors all stopped at `finish_reason: length` at 3,500 completion tokens, so a
re-run of those papers would need a larger `--max-tokens`; not authorized for
the pilot (D-044). **Agent v3** (pilot P2a, not yet run) adds `raw_response`,
`raw_reasoning` (only when the content fallback fired), their lengths,
`content_fallback` and `finish_reason` to every `result.json`, text truncated to
20,000 characters; the system prompt is unchanged.

**Provenance corrections (D-057).** The deterministic pre-check verifies that a
passage exists in the paper, not that it entails the statement; a reviewer
entailment step is part of item review. Where a reviewer shows that the recorded
passage does not contain the claim and another passage of the paper does, the
correction is a record in `data/metadata/benchmark/provenance_corrections_v1.yaml`
(pinned). `apply_provenance_corrections` overlays it on statement records ---
the statements and groups files stay immutable --- keeping the original passage
under `provenance_correction`. The corrected passage's offsets come from
`reslice_correction`, an exact re-slice in the paper's own text (the corpus
index's section text is the JSON string value, `build_index.py`); when the paper
is not on this machine the overlay records `reslice: pending_polaris` and null
offsets. On Polaris, from the litcollect root at the pushed commit:

    PYTHONPATH="$CLIMRR_REPO/src" python -c 'import json; from climrr import litstatements as ls; c = ls.load_provenance_corrections()[0]; print(json.dumps(ls.reslice_correction(c, open("sources/full_705k_v2_filtered/98/199098498.json", "rb").read())))'
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import yaml

from climrr.paths import REPO_ROOT

AGENT_PATH = REPO_ROOT / "scripts" / "litcollect" / "litstatement_agent.py"
GENERATOR_VERSION = "litstatement_agent v3"
PASS = "deterministic_pass"
CORRECTIONS_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "provenance_corrections_v1.yaml"
RESLICE_PENDING = "pending_polaris"


def load_statements(path: Path | str) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def passing(records: list[dict]) -> list[dict]:
    return [r for r in records if r["status"] == PASS]


def to_support(record: dict, independence_note: str) -> dict:
    """A passing statement record as an item-schema-v2 `supports[]` entry."""
    if record["status"] != PASS:
        raise ValueError(f"{record['statement_id']} is {record['status']}, not {PASS}")
    ev = record["evidence"]
    return {"paper_item_id": record["paper_item_id"], "paper_sha256": record["paper_sha256"],
            "json_path": ev["json_path"], "span_start": ev["span_start"], "span_end": ev["span_end"],
            "verbatim_passage": record["verbatim_passage"], "independence_note": independence_note,
            "is_review_or_synthesis": record["proposal"].get("passage_type") == "review_synthesis",
            "statement_id": record["statement_id"]}


# --- provenance corrections (D-057) ---------------------------------------------------------------------------


def load_provenance_corrections(path: Path | str = CORRECTIONS_PATH, manifest_path: Path | str | None = None) -> list[dict]:
    """The correction records, read only when the file's bytes match the manifest pin."""
    from climrr.checksums import sha256_file
    from climrr.manifest import load_entry

    path = Path(path)
    pin = load_entry(path.name, manifest_path)["sha256"]
    if sha256_file(path) != pin:
        raise ValueError(f"{path.name} differs from its manifest pin {pin}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))["corrections"]


def reslice_correction(c: dict, paper_bytes: bytes) -> dict:
    """Exact re-slice of a correction's passage in the raw paper JSON: the paper's SHA-256 must be the recorded one,
    the corrected section key a string section, and the passage found exactly once in it. Offsets are in the section
    text, as the index and the agent's `evidence` count them; `section_idx` is the key's position in the object."""
    out = {"statement_id": c["statement_id"], "paper_sha256_match": hashlib.sha256(paper_bytes).hexdigest() == c["paper_sha256"],
           "reslice": "not_found", "json_path": f"$.{c['corrected_section_key']}", "section_idx": None,
           "span_start": None, "span_end": None, "occurrences": 0, "original_reslices": None}
    if not out["paper_sha256_match"]:
        out["reslice"] = "paper_sha256_mismatch"
        return out
    obj = json.loads(paper_bytes.decode("utf-8"))
    keys = list(obj)
    text = obj.get(c["corrected_section_key"])
    if not isinstance(text, str):
        out["reslice"] = "section_not_found"
        return out
    out["section_idx"] = keys.index(c["corrected_section_key"])
    out["occurrences"] = text.count(c["corrected_passage"])
    i = text.find(c["corrected_passage"])
    if i >= 0:
        out.update(span_start=i, span_end=i + len(c["corrected_passage"]), reslice="exact" if out["occurrences"] == 1 else "exact_not_unique")
    ev = c["original_evidence"]
    orig = obj.get(ev["json_path"][2:])
    out["original_reslices"] = isinstance(orig, str) and orig[ev["span_start"]:ev["span_end"]] == c["original_passage"]
    return out


def apply_provenance_corrections(records: list[dict], corrections: list[dict], reslices: dict | None = None) -> list[dict]:
    """Copies of `records` (statement records: `statements_ingested.jsonl`, or packet / group members) with each
    correction applied: `verbatim_passage`, the passage type and the evidence location replaced, the original kept under
    `provenance_correction`. `reslices` = {statement_id: `reslice_correction` result}; without one the offsets are null
    and `reslice` is pending_polaris. A record whose passage is neither the original nor the corrected one is an error.
    Records without a correction are returned unchanged (copied)."""
    by_id = {c["statement_id"]: c for c in corrections}
    reslices = reslices or {}
    out = []
    for r in records:
        r = copy.deepcopy(r)
        c = by_id.get(r.get("statement_id"))
        if c is None:
            out.append(r)
            continue
        if "verbatim_passage" in r and r["verbatim_passage"] not in (c["original_passage"], c["corrected_passage"]):
            raise ValueError(f"{c['statement_id']}: the record's passage is neither the original nor the corrected one")
        if r.get("paper_item_id") not in (None, c["paper_item_id"]) or r.get("paper_sha256") not in (None, c["paper_sha256"]):
            raise ValueError(f"{c['statement_id']}: paper id or SHA-256 differs from the correction's")
        rs = reslices.get(c["statement_id"])
        ok = bool(rs) and rs["reslice"] == "exact"
        if "verbatim_passage" in r or "proposal" in r:
            r["verbatim_passage"] = c["corrected_passage"]
        if "proposal" in r:
            r["proposal"]["passage_type"] = c["corrected_passage_type"]
            r["proposal"]["section_key"] = c["corrected_section_key"]
        if "passage_type" in r:
            r["passage_type"] = c["corrected_passage_type"]
        loc = {"json_path": f"$.{c['corrected_section_key']}", "section_idx": rs["section_idx"] if ok else None,
               "span_start": rs["span_start"] if ok else None, "span_end": rs["span_end"] if ok else None}
        if isinstance(r.get("evidence"), dict):
            r["evidence"] = loc
        for k in ("json_path", "span_start", "span_end"):
            if k in r:
                r[k] = loc[k]
        r["provenance_correction"] = {
            "decision": "D-057", "correction_file": CORRECTIONS_PATH.name, "statement_id": c["statement_id"],
            "original_passage": c["original_passage"], "original_passage_type": c["original_passage_type"],
            "original_evidence": c["original_evidence"], "original_recovery": c.get("original_recovery"),
            "reslice": rs["reslice"] if rs else RESLICE_PENDING, "verified_by": c["verified_by"], "method": c["method"],
            "reason": c["reason"]}
        out.append(r)
    return out
