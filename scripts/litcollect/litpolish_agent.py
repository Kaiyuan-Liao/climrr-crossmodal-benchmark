#!/usr/bin/env python3
"""Pilot P3 — readability polish agent v1 (D-063; mentor 2026-11-13; work package P3a, section C).

Input: the output directory of a synthesis run (`litsynth_agent.py` v4: `<items>/items/<seed_id>.json`). For every item
with `review.status: deterministic_pass`, one model call, temperature 0: the system prompt `SYSTEM_PROMPT` (stored
verbatim; its SHA-256 in every record) and, as the user message, the JSON object {"prompt": <the item's prompt>, "answer":
<reference_answer.integrated>}. The model returns {"prompt", "answer"} rewritten for readability only.

Deterministic invariance checks (`climrr.polish_checks.invariance`, per field): the identical set of numbers; the identical
set of place / region names (U.S. states and NCA5 regions of the pinned map); the identical hedge words; no new source
word and no new leakage or generality flag (leakage v2.3, post-checks v3); a length between 0.6x and 1.2x the original's;
every mechanism keyword of the original (a content word of the label of a group the item cites) still present or
replaced by a word `data/metadata/benchmark/polish_synonyms_v1.yaml` lists. A rewrite that passes replaces the item's
`prompt` and `reference_answer.integrated` (`source_leakage_check` recomputed on the new prompt); one that fails leaves the
item's text unchanged (`polish_rejected`). Either way the item's `review.history` gains a `polish` event holding
`pre_polish` (the original prompt and answer), the rewrite, the check result and the model record; the review status is
not changed (schema v2 has no polish status; the human review sees both texts). Items that did not pass the synthesis
post-checks are skipped (listed in the summary).

Output: `<out>/items/<seed_id>.json` (+ `<out>/raw/<seed_id>/{prompt_user.txt, response.json}`), `polished.jsonl` (one
record per item: item id, status `polished` | `polish_rejected` | `polish_parse_failed`, `pre_polish`, `polished`,
reasons, checks), `summary.json`, `agent.log`. Restartable per item (skips items with an output file). One corrective
turn on a reply with no JSON object holding "prompt" and "answer" (`CORRECTIVE_PROMPT`). Retries, backoff, `--base-url`,
`--model`, `--reasoning-effort`, `--max-tokens`, `--sleep` as in litsynth_agent v4 (imported).

Polaris invocation (Sophia vLLM, D-043). Run from the execution clone on Eagle (`$CLIMRR_REPO_ROOT`,
docs/SOPHIA_RUNBOOK.md) checked out at the pinned commit; input the synthesis run's output and output under the
litcollect root (`$LITCOLLECT_ROOT_POLARIS`), never in the clone; the ALCF credential in the environment; first check the
environment: `python -c "import yaml, duckdb"`:

    bash "$CLIMRR_REPO_ROOT/scripts/sophia_pull_pinned.sh" <PINNED_SHA>
    cd "$CLIMRR_REPO_ROOT"
    python scripts/litcollect/litpolish_agent.py \\
        --items "$LITCOLLECT_ROOT_POLARIS/litsynth/run4" \\
        --out "$LITCOLLECT_ROOT_POLARIS/litpolish/run1" \\
        --base-url https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1 \\
        --model openai/gpt-oss-120b --reasoning-effort low --max-tokens 16000 \\
        --sleep 5 --source-commit <PINNED_SHA>
"""
import argparse, copy, json, os, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))
from litstatement_agent import (  # noqa: E402  (v3)
    BACKOFF_SECONDS, CREDENTIAL_ENV, DEFAULT_BASE_URL, ModelCallFailed, endpoint_label, raw_fields, sha)
from litgroup_agent import DEFAULT_MAX_TOKENS, REASONING_EFFORTS, call_turn, turn_stats  # noqa: E402  (v3)
from climrr import benchmark_items as bi  # noqa: E402
from climrr import itemseeds as sd  # noqa: E402
from climrr import polish_checks as pc  # noqa: E402

GENERATOR_VERSION = "litpolish_agent v1"
SYSTEM_PROMPT = ("Rewrite for a general scientific reader: shorter sentences, plain words, same meaning. Do not add, remove or "
                 "change any fact, number, place, time phrase, hedge word (shows/suggests) or mechanism. Do not mention data, "
                 "tables, models, papers or studies beyond the hedge words already present. Return JSON {prompt, answer}.")
CORRECTIVE_PROMPT = ("Your reply did not contain a JSON object with the keys \"prompt\" and \"answer\". "
                     "Return the complete JSON object.")


def extract(content: str):
    """Last JSON object containing 'prompt' and 'answer' (strings)."""
    best = None
    for m in re.finditer(r"\{", content):
        depth, i = 0, m.start()
        while i < len(content):
            if content[i] == "{": depth += 1
            elif content[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(content[m.start():i + 1])
                        if isinstance(obj, dict) and isinstance(obj.get("prompt"), str) and isinstance(obj.get("answer"), str):
                            best = obj
                    except Exception:  # noqa: BLE001
                        pass
                    break
            i += 1
    return best


def cited_labels(item: dict) -> list[str]:
    """The labels (statements) of the literature groups the item cites."""
    rc = item["reference_components"]
    return [s["statement"] for s in rc["literature_mechanisms"] + rc["literature_caveats"]]


def apply(item: dict, original: dict, rewrite, res: dict | None, status: str, common: dict, columns) -> dict:
    """The item after the polish: text replaced only when `status` is `polished`; a `polish` event appended."""
    out = copy.deepcopy(item)
    if status == "polished":
        out["prompt"] = rewrite["prompt"]
        out["reference_answer"]["integrated"] = rewrite["answer"]
        out["source_leakage_check"] = bi.leakage_check(rewrite["prompt"], columns)
    out["review"]["history"].append({"event": "polish", "status": status, "pre_polish": original,
                                     "rewrite": rewrite, "reasons": (res or {}).get("reasons", []),
                                     "check_version": (res or {}).get("check_version"), "checks": (res or {}).get("checks"), **common})
    return out


def summarise(out: Path, endpoint=None, budget=None, skipped=()):
    recs = [json.loads(x) for x in (out / "polished.jsonl").read_text(encoding="utf-8").splitlines()] if (out / "polished.jsonl").exists() else []
    reasons = {}
    for r in recs:
        for x in r["reasons"]:
            key = x.split(":")[1].strip().split(" ")[0] if ":" in x else x
            reasons[key] = reasons.get(key, 0) + 1
    s = {"generator_version": GENERATOR_VERSION, **(endpoint or {}), **(budget or {}), "system_prompt_sha256": sha(SYSTEM_PROMPT),
         "corrective_prompt_sha256": sha(CORRECTIVE_PROMPT), "check_version": pc.VERSION, "items": len(recs),
         **{k: sum(r["status"] == k for r in recs) for k in ("polished", "polish_rejected", "polish_parse_failed")},
         "reasons_by_kind": dict(sorted(reasons.items())), "skipped_not_deterministic_pass": list(skipped)}
    (out / "summary.json").write_text(json.dumps(s, indent=2))
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True, help="a synthesis run's output directory (with items/*.json)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--model", default="gpt-oss-120b")
    ap.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS); ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--reasoning-effort", choices=REASONING_EFFORTS, default="low")
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--only", default=None, help="seed ids, comma-separated")
    ap.add_argument("--sleep", type=float, default=0, help="seconds between items")
    ap.add_argument("--backoff", default=",".join(map(str, BACKOFF_SECONDS)), help="retry waits, seconds")
    ap.add_argument("--source-commit", default="unknown")
    a = ap.parse_args()
    credential = next((os.environ[v] for v in CREDENTIAL_ENV if os.environ.get(v)), None)
    if not credential:
        sys.exit(f"{CREDENTIAL_ENV[0]} env var not set")
    out = Path(a.out); (out / "items").mkdir(parents=True, exist_ok=True)
    log = open(out / "agent.log", "a")

    def say(msg):
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"; print(line, flush=True); log.write(line + "\n"); log.flush()

    paths = sorted((Path(a.items) / "items").glob("*.json"))
    only = set(a.only.split(",")) if a.only else None
    backoff = tuple(float(x) for x in a.backoff.split(","))
    endpoint = {"base_url": a.base_url, "model": a.model, "endpoint_label": endpoint_label(a.base_url)}
    budget = {"reasoning_effort": a.reasoning_effort, "max_tokens": a.max_tokens}
    columns, nca, syn = bi.column_names(), sd.nca_map(), pc.load_synonyms()
    say(f"START {GENERATOR_VERSION} items={len(paths)} endpoint_label={endpoint['endpoint_label']} base_url={a.base_url} model={a.model} reasoning_effort={a.reasoning_effort} max_tokens={a.max_tokens} system_sha={sha(SYSTEM_PROMPT)[:12]}")

    done, skipped = 0, []
    for path in paths:
        raw = path.read_text(encoding="utf-8")
        item = json.loads(raw)
        sid = path.stem
        if only and sid not in only: continue
        if item["review"]["status"] != "deterministic_pass":
            skipped.append(item["item_id"]); continue
        opath = out / "items" / f"{sid}.json"
        if opath.exists(): continue
        if a.limit and done >= a.limit: break
        if done and a.sleep: time.sleep(a.sleep)
        rdir = out / "raw" / sid; rdir.mkdir(parents=True, exist_ok=True)
        original = {"prompt": item["prompt"], "answer": item["reference_answer"]["integrated"]}
        user = json.dumps(original, indent=1, ensure_ascii=False)
        (rdir / "prompt_user.txt").write_text(user, encoding="utf-8")
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]
        try:
            resp, content, secs, attempts, applied = call_turn(a.base_url, a.model, credential, messages, a.max_tokens, a.timeout,
                                                               a.reasoning_effort, say, sid, backoff)
        except ModelCallFailed as e:
            (rdir / "model_error.txt").write_text(f"{e}\n")
            with open(out / "failed_items.txt", "a") as f: f.write(sid + "\n")
            done += 1
            say(f"FAIL item={sid} reason={e}")
            continue
        (rdir / "response.json").write_text(json.dumps(resp, indent=2, ensure_ascii=False))
        obj = extract(content)
        turns = [{"turn": 1, **turn_stats(resp), "http_attempts": attempts, "model_seconds": secs}]
        if not obj:
            say(f"CORRECTIVE item={sid}")
            try:
                resp2, content2, secs2, attempts2, _ = call_turn(
                    a.base_url, a.model, credential,
                    messages + [{"role": "assistant", "content": content}, {"role": "user", "content": CORRECTIVE_PROMPT}],
                    a.max_tokens, a.timeout, a.reasoning_effort if applied else None, say, sid, backoff)
            except ModelCallFailed as e:
                say(f"CORRECTIVE_FAIL item={sid} reason={e}")
            else:
                (rdir / "response_corrective.json").write_text(json.dumps(resp2, indent=2, ensure_ascii=False))
                resp, secs = resp2, secs + secs2
                turns.append({"turn": 2, **turn_stats(resp2), "http_attempts": attempts2, "model_seconds": secs2})
                obj = extract(content2)
        common = {"generator_version": GENERATOR_VERSION, **endpoint, "temperature": 0, **budget, "reasoning_effort_applied": applied,
                  "system_prompt_sha256": sha(SYSTEM_PROMPT), "prompt_hash": sha(SYSTEM_PROMPT + user), "item_sha256": sha(raw),
                  "source_commit": a.source_commit, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  "model_seconds": secs, "model_attempts": len(turns), "corrective_retry_used": len(turns) > 1, "turns": turns,
                  **turn_stats(resp), **raw_fields(resp)}
        if obj:
            rewrite = {"prompt": obj["prompt"], "answer": obj["answer"]}
            res = pc.invariance(original, rewrite, cited_labels(item), nca, syn, columns)
            status = "polished" if res["pass"] else "polish_rejected"
        else:
            rewrite, status = None, "polish_parse_failed"
            res = {"check_version": pc.VERSION, "pass": False, "reasons": ["parse: no JSON object with 'prompt' and 'answer' found"], "checks": None}
        new = apply(item, original, rewrite, res, status, common, columns)
        opath.write_text(json.dumps(new, indent=2, ensure_ascii=False))
        with open(out / "polished.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"item_id": item["item_id"], "seed_id": sid, "status": status, "pre_polish": original, "polished": rewrite,
                                "reasons": res["reasons"], "checks": res["checks"], "system_prompt_sha256": sha(SYSTEM_PROMPT)},
                               ensure_ascii=False, sort_keys=True) + "\n")
        done += 1
        say(f"{sid} status={status} reasons={len(res['reasons'])} model_s={secs}")

    s = summarise(out, endpoint, budget, skipped)
    say(f"DONE items={s['items']} polished={s['polished']} rejected={s['polish_rejected']} parse_failed={s['polish_parse_failed']}")


if __name__ == "__main__":
    main()
