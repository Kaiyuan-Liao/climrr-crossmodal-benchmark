"""Literature statements (pilot P1, D-039, D-041): the agent's output, read back.

`scripts/litcollect/litstatement_agent.py` (derived from `softqa_agent.py` v2, whose
locator it imports) asks the model for up to eight **general statements** a paper
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
inference credential is in the environment variable the agent's `main` reads.
`softqa_agent.py` must sit beside the agent (it does in the repository).

Run 1 --- the 243 frozen place candidates first:

    cd "$LITCOLLECT_ROOT_POLARIS"
    PYTHONPATH="$CLIMRR_REPO/src" python "$CLIMRR_REPO/scripts/litcollect/litstatement_agent.py" \\
        --candidates "$CLIMRR_REPO/data/metadata/softqa/trackc_candidates_v1.json" \\
        --index index/full_705k_v2_filtered --out litstatements/run1 \\
        --source-commit "$(git -C "$CLIMRR_REPO" rev-parse HEAD)"

Then, optionally, the full LITCORPUS-02 (1,308 items): a new frozen candidates
file `data/metadata/benchmark/litstatement_candidates_litcorpus02_v1.json`, built
by a later package from the two arm manifests
`artifacts/literature/litcorpus02/fire_weather_v1_manifest.csv` and
`extreme_heat_v1_manifest.csv` (union per `lit2_ids.csv`, 1,308 rows; one arm per
item, as `[{item_id, arm}]`) and pinned in the manifest before the run --- not
built here. The 243 already processed are skipped if the same `--out` is reused
(restartable per paper).

Defaults: Metis `gpt-oss-120b`, temperature 0, `--max-chars 90000` (a longer
paper is truncated and flagged), `--max-tokens 6000`; the reasoning-field
fallback of `call_model` applies. Restartable: a paper with `result.json` is
skipped; `statements.jsonl` and `summary.json` are rebuilt from every
`result.json` at the end of each invocation. Run evidence: `agent.log`, per-paper
`result.json` / `prompt_user.txt` / `response.json`, `statements.jsonl`,
`summary.json`.
"""

from __future__ import annotations

import json
from pathlib import Path

from climrr.paths import REPO_ROOT

AGENT_PATH = REPO_ROOT / "scripts" / "litcollect" / "litstatement_agent.py"
GENERATOR_VERSION = "litstatement_agent v1"
PASS = "deterministic_pass"


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
