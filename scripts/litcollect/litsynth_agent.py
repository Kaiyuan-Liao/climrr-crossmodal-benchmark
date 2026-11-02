#!/usr/bin/env python3
"""Pilot P2b — item-synthesis agent v3.1 (D-041, D-048, D-051, D-055, D-055a; COORDINATOR rulings 2026-11-01 and 2026-11-02).

Input: a directory of seed packets `PK-<seed_id>.json` (`scripts/build_synth_packets.py`). One model call per packet,
temperature 0. The model sees the packet's `model_view` only: the table pattern in plain words with its values, the
relevant literature groups (label, strength, member statements with passages <= 400 characters and paper ids), the item
field list, the guardrails, the D-038 rung and the numbers it may use. It never sees a column name, a derivation rule,
a table hash or a span.

The model returns a closed-book prompt, a decomposed reference answer (table-pattern sentences tagged with pattern ids,
literature sentences tagged with group ids and a hedge flag, an integrated paragraph), a rubric with weighted required
points, guardrails, source-independent answerability with a note, and the short identity fields. The agent assembles a
schema-v2 item (`data/metadata/benchmark/item_schema_v2.json`): `reference_components` from the packet's provenance
(the pattern record; one literature statement per cited group, its supports the group's core / cited / review members
with exact spans; `reference_scope` single_study_observation for a single-source group, else
regional_climate_expectation), `source_leakage_check` computed, `generation` with the packet and prompt hashes. Then
`climrr.benchmark_items.synthesis_post_checks` (numbers trace to the packet, tags, hedges, leakage, schema, consistency).
An item that passes is `review.status: deterministic_pass`; one that fails is written with `review.status:
rejected_pre_review` (schema v2 has no `deterministic_fail` value) and `review.history[0]` = {event:
deterministic_fail, reasons}. The tagged reference answer and the rubric weights, which schema v2 has no field for, are
kept in `review.history[0]`.

Output: `<out>/items/<seed_id>.json` (+ `<out>/raw/<seed_id>/{prompt_user.txt, response.json}`), `items.jsonl`,
`summary.json`, `agent.log`. Restartable per packet (skips packets with an item file). Retries, backoff, `--base-url`,
`--model`, `--sleep` as in litstatement_agent v3 (imported). A parse failure is written as an item stub with
`review.status: rejected_pre_review` and the parse error.

v2 (D-051; the budget and retry of litgroup_agent v3, no chunking): `--reasoning-effort {low,medium,high}` (default
low) sent as `reasoning_effort`, retried once without it on HTTP 400 (`reasoning_effort_applied: false`);
`--max-tokens` default 16000. One corrective turn in the same conversation (`CORRECTIVE_PROMPT`) when the reply holds
no JSON object with 'prompt' and 'reference_answer' --- on a parse failure only; an item that parses and fails the
post-checks is not retried. `model_attempts` (turns), `corrective_retry_used`, per turn `finish_reason`,
`content_chars`, `reasoning_chars` go into `review.history[0]`; the first turn's raw text into `first_turn`.

v3 (D-055, pattern-level grading; run 0 --- two rung-1 items, both rejected_pre_review on numbers_untraced
only --- superseded): the system prompt asks for a pattern-level reference answer and rubric in the packet's
`allowed_descriptors` (DR-DESC-1); numbers only as digits copied from the descriptors or pattern values; no
number-words outside a copied descriptor; no exact value in the reference answer or rubric (provenance only); the
quantity named in general words with its threshold; specific numbers only as optional rubric points. The post-checks
are `synthesis_post_checks` v2 (number-words, `exact_value_in_graded_text`). Everything else as v2.

v3.1 (D-055a, literature-number rule): every required and optional rubric point carries `source_ids` (the pattern and
/ or group ids it rests on); a number a literature group states (for example a threshold such as "80 °F") may be
copied exactly into a literature sentence tagged with that group or a rubric point whose `source_ids` name it. The
item keeps the rubric as strings (schema v2); the tagged points go into `review.history[0].reference_answer_tagged
.rubric_points`. Post-checks `synthesis_post_checks` v2.1. Everything else as v3.

Polaris invocation (Sophia vLLM, D-043). Run from the execution clone on Eagle (`$CLIMRR_REPO_ROOT`,
docs/SOPHIA_RUNBOOK.md) checked out at the pinned commit that carries the packets and provides `climrr`; output
under the litcollect root (`$LITCOLLECT_ROOT_POLARIS`, config key `litcollect_root_polaris`), never in the clone; the
ALCF credential in the environment; first check the environment: `python -c "import yaml, duckdb"`:

    bash "$CLIMRR_REPO_ROOT/scripts/sophia_pull_pinned.sh" <PINNED_SHA>
    cd "$CLIMRR_REPO_ROOT"
    python scripts/litcollect/litsynth_agent.py \\
        --packets artifacts/benchmark/synth_packets \\
        --out "$LITCOLLECT_ROOT_POLARIS/litsynth/run1" \\
        --base-url https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1 \\
        --model openai/gpt-oss-120b --reasoning-effort low --max-tokens 16000 \\
        --sleep 5 --source-commit <PINNED_SHA>
"""
import argparse, json, os, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))
from litstatement_agent import (  # noqa: E402  (v3)
    BACKOFF_SECONDS, CREDENTIAL_ENV, DEFAULT_BASE_URL, ModelCallFailed, endpoint_label, raw_fields, sha)
from litgroup_agent import DEFAULT_MAX_TOKENS, REASONING_EFFORTS, call_turn, turn_stats  # noqa: E402  (v3)
from climrr import benchmark_items as bi  # noqa: E402

GENERATOR_VERSION = "litsynth_agent v3.1"
CORRECTIVE_PROMPT = ("Your reply did not contain a JSON object with the keys \"prompt\" and \"reference_answer\". "
                     "Return the complete JSON object.")

SYSTEM_PROMPT = """You write ONE closed-book benchmark item for climate scientists from a SEED PACKET. The packet holds (a) table patterns: deterministic facts about modeled climate projections, in plain words, with their values and, for each pattern, "allowed_descriptors": the pattern-level words (direction, magnitude class, coarse anchors, relative tercile, regional ranking, horizon, scenario and quantity phrases) computed by code; (b) groups of literature statements: each group has an id, a label, an evidence strength, and member statements with their supporting passages and paper ids; (c) the use-case rung, the guardrails and the numbers you may use. Use ONLY facts in the packet. Add no fact, number, place, mechanism, scenario or source that is not in it.

The item is graded at the PATTERN level: direction, magnitude class, region, horizon and scenario, mechanism. Exact values are NOT graded: they are attached to the item as provenance by code, never by you. Never put a decimal number or an exact pattern value in "reference_answer" or "rubric".

NUMBERS. Any number in "prompt", "reference_answer" or "rubric" must be copied AS DIGITS from the pattern's "allowed_descriptors" or from the packet's pattern values (for example the heat-index threshold, or "about 16 days" when it is an allowed anchor). Never write a number as a word ("sixteen", "forty-five", "twice", "double", "triple", "half", "threefold"), except inside an allowed descriptor phrase copied verbatim (for example "roughly tripling" or "about half again as many" when the packet lists it). Do not round a value yourself, and do not state a ratio, percentage or range the packet does not list. Do not state horizon years unless the packet states them; prefer the packet's horizon phrase (for example "by mid-century (2045–2054)") and scenario phrase (for example "under RCP8.5, one high-emissions scenario") exactly as given. One exception for literature: a number (or number-word) that a group's label or member statement states, for example a threshold such as "80 °F", may be copied exactly as written there into a "literature_interpretation" sentence whose "group_ids" include that group, or into a rubric point whose "source_ids" include that group --- nowhere else.

Return ONE JSON object with exactly these keys:
- "prompt": a closed-book question that a well-informed climate scientist could answer from general knowledge. It asks about the general pattern and its drivers at the state or region level the packet names, for the season, horizon and scenario the packet names. It names the quantity in general words a closed-book reader can answer, using the pattern's "quantity" descriptor (for the heat index: "days with a dangerous heat index (above 95 °F)" or "(above 105 °F)" --- the threshold stays, because it defines the quantity). It must NOT name or hint at any table, dataset, data portal, paper, study, author, column, variable name or grid cell, and must not say "according to", "the table", "the data", "the paper" or "the study". It must not require recalling an exact number: ask for direction, rough size, ranking or contrast, and the drivers.
- "reference_answer": {
  "table_pattern": [{"sentence": "...", "pattern_ids": ["..."]}] --- each sentence states what a pattern shows, in the pattern's allowed descriptors (direction, magnitude class or low-baseline phrase, place or regional ranking with largest / smallest, relative tercile where given, horizon and scenario phrases), and is tagged with the pattern id(s) it comes from;
  "literature_interpretation": [{"sentence": "...", "group_ids": ["..."], "hedged": true or false}] --- each sentence rests on the group(s) it cites. A sentence that rests only on single_source_supported groups must be hedged (for example "one study reports ...", "... may ...") and marked "hedged": true; never present a single-source claim as consensus. If the packet has no groups, return [];
  "integrated": "a short paragraph that combines the two, in the same terms, with no new fact" }
- "rubric": {"required_points": [{"point": "...", "weight": 1, 2 or 3, "source_ids": ["..."]}], "acceptable_variants": ["..."], "optional_points": [{"point": "...", "source_ids": ["..."]}], "disallowed_claims": ["..."], "fatal_errors": ["..."]}. Every required and optional point MUST carry "source_ids": the pattern id(s) and / or group id(s) from the packet that the point rests on. The required points are pattern-level: the direction; the magnitude class (or the low-baseline phrase); the place, or for a regional contrast the ranking (largest / smallest); the mechanism, where the packet has groups; the handling of the scenario and horizon (one high-emissions scenario, not a forecast); and no overclaim (no exact number demanded, no single-source claim as consensus, hazard not exposure). A specific number may appear only under "optional_points", and only as an allowed anchor copied as digits --- except a literature number under the exception above, in a point whose "source_ids" include its group.
- "guardrails": the packet guardrails that apply to this item, verbatim or made more specific.
- "source_independent_answerability": "yes", "borderline" or "no" --- could a well-informed climate scientist answer without the packet's sources?
- "source_independence_note": one sentence explaining that judgement.
- "capability_tested", "system_task", "key_relationships", "evidence_needed", "desired_output_characteristics": one short phrase each, for the packet's use-case rung.
- "expected_knowledge_level": "general_climate_science" or "specialist_climate_science".

Respect every guardrail: a modeled historical baseline is model output, not an observation; a Fire Weather Index is meteorological fire danger, never fire occurrence; RCP8.5 is one high-emissions scenario, not a forecast; hazard is not exposure and exposure is not risk. Return ONLY the JSON object."""

IDENTITY = ("capability_tested", "system_task", "key_relationships", "evidence_needed", "desired_output_characteristics")
CORE_OR_CITED = ("core_candidate", "cited_candidate")


def extract_item(content: str):
    """Last JSON object containing 'prompt' and 'reference_answer'."""
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
                        if isinstance(obj, dict) and "prompt" in obj and "reference_answer" in obj:
                            best = obj
                    except Exception:  # noqa: BLE001
                        pass
                    break
            i += 1
    return best


def _str(x):
    return x if isinstance(x, str) else ""


def _strings(xs):
    return [x for x in xs if isinstance(x, str) and x.strip()] if isinstance(xs, list) else []


def literature_statement(g: dict) -> dict:
    sups = [m for m in g["members"] if m["evidence_role"] in CORE_OR_CITED or m["passage_type"] == "review_synthesis"]
    return {"statement": g["label"] or g["members"][0]["statement"], "statement_type": g["statement_type"],
            "evidence_strength": g["strength_in_packet"],
            "reference_scope": "single_study_observation" if g["strength_in_packet"] == "single_source_supported" else "regional_climate_expectation",
            "group_id": g["group_id"], "group_strength_run": g["group_strength_run"],
            "supports": [{"paper_item_id": m["paper_item_id"], "paper_sha256": m["paper_sha256"], "json_path": m["json_path"],
                          "span_start": m["span_start"], "span_end": m["span_end"], "verbatim_passage": m["verbatim_passage"],
                          "independence_note": f"DR-LIT-IND-1 v2 (D-046): canonical paper {m['canonical_paper']}",
                          "is_review_or_synthesis": m["passage_type"] == "review_synthesis", "statement_id": m["statement_id"],
                          "evidence_role": m["evidence_role"]} for m in sups]}


def assemble(obj: dict, packet: dict, common: dict, columns) -> tuple[dict, dict]:
    """(schema-v2 item, tagged reference answer) from the model object and the packet."""
    ra = obj.get("reference_answer") if isinstance(obj.get("reference_answer"), dict) else {}
    tagged = {"table_pattern": ra.get("table_pattern") if isinstance(ra.get("table_pattern"), list) else [],
              "literature_interpretation": ra.get("literature_interpretation") if isinstance(ra.get("literature_interpretation"), list) else [],
              "integrated": _str(ra.get("integrated"))}
    sent = lambda xs: " ".join(x["sentence"] for x in xs if isinstance(x, dict) and isinstance(x.get("sentence"), str)) or None  # noqa: E731
    groups = {g["group_id"]: g for g in packet["provenance"]["groups"]}
    cited = []
    for s in tagged["literature_interpretation"]:
        for gid in (s.get("group_ids") or []) if isinstance(s, dict) else []:
            if gid in groups and gid not in cited:
                cited.append(gid)
    stmts = [literature_statement(groups[g]) for g in cited]
    rub = obj.get("rubric") if isinstance(obj.get("rubric"), dict) else {}
    req = rub.get("required_points") if isinstance(rub.get("required_points"), list) else []
    weights = [{"point": _str(r.get("point")), "weight": r.get("weight")} if isinstance(r, dict) else {"point": _str(r), "weight": None}
               for r in req]
    opt = rub.get("optional_points") if isinstance(rub.get("optional_points"), list) else []
    points = [{"field": field, "point": _str(r.get("point")) if isinstance(r, dict) else _str(r),
               "source_ids": r.get("source_ids") if isinstance(r, dict) and isinstance(r.get("source_ids"), list) else None}
              for field, xs in (("required_points", req), ("optional_points", opt)) for r in xs]
    prompt = _str(obj.get("prompt"))
    frame = packet["provenance"]["item_frame"]
    item = {
        "schema_version": bi.SCHEMA_VERSION, "item_id": packet["item_id"], "use_case_level": frame["use_case_level"],
        **{k: _str(obj.get(k)) for k in IDENTITY[:2]}, "reasoning_modalities": frame["reasoning_modalities"],
        **{k: _str(obj.get(k)) for k in IDENTITY[2:]}, "expected_knowledge_level": _str(obj.get("expected_knowledge_level")),
        "prompt": prompt, "source_independent_answerability": _str(obj.get("source_independent_answerability")),
        "source_independence_note": _str(obj.get("source_independence_note")),
        "source_leakage_check": bi.leakage_check(prompt, columns),
        "reference_components": {"table_patterns": packet["provenance"]["patterns"],
                                 "literature_mechanisms": [s for s in stmts if s["statement_type"] != "caveat"],
                                 "literature_caveats": [s for s in stmts if s["statement_type"] == "caveat"]},
        "reference_answer": {"table_pattern": sent(tagged["table_pattern"]), "literature_interpretation": sent(tagged["literature_interpretation"]),
                             "integrated": tagged["integrated"]},
        "rubric": {"required_points": [f"[w={w['weight']}] {w['point']}" if w["weight"] is not None else w["point"] for w in weights if w["point"]],
                   "optional_points": [p["point"] for p in points if p["field"] == "optional_points" and p["point"].strip()],
                   **{k: _strings(rub.get(k)) for k in ("acceptable_variants", "disallowed_claims", "fatal_errors")}},
        "guardrails": _strings(obj.get("guardrails")), "c_g_t_s_d_audit": None,
        "generation": {"generator_version": GENERATOR_VERSION, "model": common["model"], "prompt_hash": common["prompt_hash"],
                       "timestamp": common["generation_timestamp"],
                       "inputs_sha256": {"packet": common["packet_sha256"], "system_prompt": common["system_prompt_sha256"],
                                         **packet.get("inputs_sha256", {})}},
        "review": {"status": "llm_candidate", "history": [], "kaiyuan_disposition": None, "mentor_disposition": None, "final_frozen": None},
    }
    return item, {**tagged, "rubric_required_weights": weights, "rubric_points": points}


def finish(item: dict, tagged: dict, packet: dict, common: dict, columns, parse_error=None) -> dict:
    if parse_error:
        res = {"check_version": bi.SYNTH_CHECK_VERSION, "pass": False, "reasons": [f"parse: {parse_error}"], "checks": {}}
    else:
        res = bi.synthesis_post_checks(item, tagged, packet["checks_input"], columns)
    item["review"]["status"] = "deterministic_pass" if res["pass"] else "rejected_pre_review"
    item["review"]["history"] = [{"event": "deterministic_pass" if res["pass"] else "deterministic_fail", "reasons": res["reasons"],
                                  "check_version": res["check_version"], "checks": res["checks"], "reference_answer_tagged": tagged,
                                  "seed_id": packet["seed_id"], "packet_id": packet["packet_id"], **common}]
    return item


def summarise(out: Path, endpoint=None, budget=None):
    items = [json.loads(p.read_text()) for p in sorted((out / "items").glob("*.json"))]
    with open(out / "items.jsonl", "w", encoding="utf-8") as f:
        for it in items: f.write(json.dumps(it, ensure_ascii=False, sort_keys=True) + "\n")
    reasons = {}
    for it in items:
        for r in it["review"]["history"][0]["reasons"]:
            key = r.split(":")[0]
            reasons[key] = reasons.get(key, 0) + 1
    hist = [it["review"]["history"][0] for it in items]
    s = {"generator_version": GENERATOR_VERSION, **(endpoint or {}), **(budget or {}), "system_prompt_sha256": sha(SYSTEM_PROMPT),
         "corrective_prompt_sha256": sha(CORRECTIVE_PROMPT), "items": len(items),
         "deterministic_pass": sum(it["review"]["status"] == "deterministic_pass" for it in items),
         "deterministic_fail": sum(it["review"]["status"] != "deterministic_pass" for it in items),
         "fail_reasons_by_kind": dict(sorted(reasons.items())),
         "corrective_retry_used": sum(bool(h.get("corrective_retry_used")) for h in hist),
         "reasoning_effort_not_applied": sum(h.get("reasoning_effort_applied") is False for h in hist),
         "finish_reasons": {k: sum(str(h.get("finish_reason")) == k for h in hist) for k in sorted({str(h.get("finish_reason")) for h in hist})},
         "by_level": {str(k): sum(it["use_case_level"] == k for it in items) for k in sorted({it["use_case_level"] for it in items})}}
    (out / "summary.json").write_text(json.dumps(s, indent=2))
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packets", required=True, help="directory of PK-*.json seed packets")
    ap.add_argument("--out", required=True)
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--model", default="gpt-oss-120b")
    ap.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS); ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--reasoning-effort", choices=REASONING_EFFORTS, default="low")
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--only", default=None, help="seed ids, comma-separated")
    ap.add_argument("--sleep", type=float, default=0, help="seconds between packets")
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

    paths = sorted(Path(a.packets).glob("PK-*.json"))
    only = set(a.only.split(",")) if a.only else None
    backoff = tuple(float(x) for x in a.backoff.split(","))
    endpoint = {"base_url": a.base_url, "model": a.model, "endpoint_label": endpoint_label(a.base_url)}
    budget = {"reasoning_effort": a.reasoning_effort, "max_tokens": a.max_tokens}
    columns = bi.column_names()
    say(f"START {GENERATOR_VERSION} packets={len(paths)} endpoint_label={endpoint['endpoint_label']} base_url={a.base_url} model={a.model} reasoning_effort={a.reasoning_effort} max_tokens={a.max_tokens} system_sha={sha(SYSTEM_PROMPT)[:12]}")

    done = 0
    for path in paths:
        raw = path.read_text(encoding="utf-8")
        packet = json.loads(raw)
        sid = packet["seed_id"]
        if only and sid not in only: continue
        ipath = out / "items" / f"{sid}.json"
        if ipath.exists(): continue
        if a.limit and done >= a.limit: break
        if done and a.sleep: time.sleep(a.sleep)
        rdir = out / "raw" / sid; rdir.mkdir(parents=True, exist_ok=True)
        user = "SEED PACKET:\n" + json.dumps(packet["model_view"], indent=1, ensure_ascii=False)
        (rdir / "prompt_user.txt").write_text(user, encoding="utf-8")
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]
        t0 = time.time()
        try:
            resp, content, secs, attempts, applied = call_turn(a.base_url, a.model, credential, messages, a.max_tokens, a.timeout,
                                                               a.reasoning_effort, say, sid, backoff)
        except ModelCallFailed as e:
            (rdir / "model_error.txt").write_text(f"{e}\n")
            with open(out / "failed_packets.txt", "a") as f: f.write(sid + "\n")
            done += 1
            say(f"FAIL seed={sid} reason={e}")
            continue
        (rdir / "response.json").write_text(json.dumps(resp, indent=2, ensure_ascii=False))
        obj = extract_item(content)
        perr = None if obj else "no JSON object with 'prompt' and 'reference_answer' found"
        turns = [{"turn": 1, **turn_stats(resp), "http_attempts": attempts, "model_seconds": secs}]
        first_turn, corrective_error = None, None
        if not obj:
            (rdir / "prompt_corrective.txt").write_text(CORRECTIVE_PROMPT, encoding="utf-8")
            first_turn = {"model_parse_error": perr, **raw_fields(resp)}
            say(f"CORRECTIVE seed={sid}")
            try:
                resp2, content2, secs2, attempts2, _ = call_turn(
                    a.base_url, a.model, credential,
                    messages + [{"role": "assistant", "content": content}, {"role": "user", "content": CORRECTIVE_PROMPT}],
                    a.max_tokens, a.timeout, a.reasoning_effort if applied else None, say, sid, backoff)
            except ModelCallFailed as e:
                corrective_error = str(e)
                say(f"CORRECTIVE_FAIL seed={sid} reason={e}")
            else:
                (rdir / "response_corrective.json").write_text(json.dumps(resp2, indent=2, ensure_ascii=False))
                resp, secs = resp2, secs + secs2
                turns.append({"turn": 2, **turn_stats(resp2), "http_attempts": attempts2, "model_seconds": secs2})
                obj = extract_item(content2)
                perr = None if obj else "no JSON object with 'prompt' and 'reference_answer' found (corrective turn)"
        common = {"generator_version": GENERATOR_VERSION, **endpoint, "temperature": 0, **budget, "reasoning_effort_applied": applied,
                  "system_prompt_sha256": sha(SYSTEM_PROMPT), "corrective_prompt_sha256": sha(CORRECTIVE_PROMPT),
                  "prompt_hash": sha(SYSTEM_PROMPT + user), "packet_sha256": sha(raw), "source_commit": a.source_commit,
                  "generation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "model_seconds": secs,
                  "model_attempts": len(turns), "corrective_retry_used": first_turn is not None, "turns": turns,
                  "first_turn": first_turn, "corrective_error": corrective_error, **turn_stats(resp), **raw_fields(resp)}
        item, tagged = assemble(obj or {}, packet, common, columns)
        item = finish(item, tagged, packet, common, columns, perr)
        ipath.write_text(json.dumps(item, indent=2, ensure_ascii=False))
        done += 1
        reasons = item["review"]["history"][0]["reasons"]
        say(f"{sid} level={item['use_case_level']} status={item['review']['status']} reasons={len(reasons)} model_s={secs} elapsed={round(time.time() - t0, 1)} err={perr}")

    s = summarise(out, endpoint, budget)
    say(f"DONE items={s['items']} pass={s['deterministic_pass']} fail={s['deterministic_fail']}")


if __name__ == "__main__":
    main()
