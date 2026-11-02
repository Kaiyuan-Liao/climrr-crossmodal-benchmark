#!/usr/bin/env python3
"""Pilot P2b — literature-statement grouping agent v3 (D-048, D-049, D-051; COORDINATOR rulings 2026-11-01).

Input: `artifacts/litgroups/partitions_v1.jsonl` (`scripts/build_group_partitions.py`): one partition = arm x
statement_type over the core / cited / background_consensus statements of litstatements run 2, split
deterministically where over 120 statements. One model call per chunk (v3, below). The model sees **local ids (S001...)
and sentences only** --- no passage, no paper id (statement ids LS-<item_id>-<nn> carry it, so they are not sent),
no table. It returns groups of sentences that make the same claim and singletons. Temperature 0.

v2 (D-049): every group and every singleton carries `claim_about` in `CLAIM_ABOUT` (hazard_change_mechanism,
hazard_definition_or_measurement, impact_or_exposure, method_or_data, other), defined one line each in the prompt.
Claim type is a human-checked semantic tag assigned by the model; code never infers it. Singletons are returned as
`{id, claim_about}` objects.

Deterministic checks per partition: the JSON parses; every returned id exists in the partition and appears exactly
once across groups and singletons, and every input id appears (else the partition is `deterministic_fail` and none
of its groups is written to groups.jsonl); no group is empty. Per group: a label holds no digit sequence that is not in
a member sentence (else the group is `deterministic_fail`, kept and flagged). Recorded, not gating: label words that
are neither in a member sentence nor a function word; a rationale over 25 words. Per group and per singleton:
`claim_about` is a value of `CLAIM_ABOUT` (else that record is `deterministic_fail`, kept and flagged). A group whose
members come from one paper only is still a group. Singletons become one-member records (kind `singleton`, no label).

Strength per group (D-045 definitions, D-046 independence --- the canonical paper id travels in the partition's
`meta`, never sent): `multi_source_supported` (>= 2 canonical papers among core / cited members), else
`review_supported` (a review_synthesis member), else `single_source_supported` (a core / cited member), else
`background_only`.

v3 (D-051; run 1 at v2 ended `finish_reason=length` with no content on every partition of >= 46 statements):
- Reasoning budget. `--reasoning-effort {low,medium,high}` (default low) is sent as `reasoning_effort` in the
  chat-completions body; if the server answers HTTP 400, the call is retried once without it and the record says
  `reasoning_effort_applied: false`. `--max-tokens` default 16000.
- Chunking. `--chunk-size` default 40: a partition's statements are ordered by (region class in `REGION_ORDER`, then
  statement id) and cut into ceil(n / chunk-size) consecutive chunks whose sizes differ by at most one (the first
  ones larger); chunk id `<partition_id>.c<k>`, one call per chunk, every partition has at least `.c1`. Local ids
  stay the partition's. Groups are never merged across chunks by code (a limitation; the reviewer may merge).
- Corrective retry. When a reply parses but fails `ids_exactly_once_pass`, one follow-up turn in the same
  conversation (`CORRECTIVE_TEMPLATE`) and the checks re-run on the second reply; a reply that does not parse is not
  retried. Still failing -> `deterministic_fail`. `model_attempts` (turns, 1 or 2), `corrective_retry_used`, and
  per turn `finish_reason`, `content_chars`, `reasoning_chars` are recorded; the first turn's checks and raw text are
  kept in `first_turn`.

Output: per chunk `<out>/<chunk_id>/result.json` (+ `prompt_user.txt`, `response.json`, and after a corrective turn
`prompt_corrective.txt`, `response_corrective.json`; raw model text in result.json as in litstatement_agent v3),
aggregate `groups.jsonl` (group_id `LG-<arm>-<type>-c<k>-<nnn>`, numbered per arm x type x chunk index over the
partitions in file order, groups then singletons; each with `claim_about`) and `summary.json` (chunks per partition,
the budget, retry counts, counts by `claim_about`); `agent.log`. Restartable per chunk (skips chunks with
result.json). Retries, backoff, `--base-url`, `--model`, `--sleep` as in litstatement_agent v3 (imported).

Polaris invocation (Sophia vLLM, D-043). Run from the execution clone on Eagle (`$CLIMRR_REPO_ROOT`,
docs/SOPHIA_RUNBOOK.md) checked out at the pinned commit, which holds the tracked input; output under the litcollect
root (`$LITCOLLECT_ROOT_POLARIS`, config key `litcollect_root_polaris`), never in the clone; the ALCF credential in
the environment; first check the environment: `python -c "import yaml, duckdb"`:

    bash "$CLIMRR_REPO_ROOT/scripts/sophia_pull_pinned.sh" <PINNED_SHA>
    cd "$CLIMRR_REPO_ROOT"
    python scripts/litcollect/litgroup_agent.py \\
        --partitions artifacts/litgroups/partitions_v1.jsonl \\
        --out "$LITCOLLECT_ROOT_POLARIS/litgroups/run2" \\
        --base-url https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1 \\
        --model openai/gpt-oss-120b --reasoning-effort low --max-tokens 16000 --chunk-size 40 \\
        --sleep 5 --source-commit <PINNED_SHA>
"""
import argparse, json, math, os, re, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from litstatement_agent import (  # noqa: E402  (v3)
    BACKOFF_SECONDS, CREDENTIAL_ENV, DEFAULT_BASE_URL, ModelCallFailed, call_with_retries, endpoint_label, raw_fields, sha)

GENERATOR_VERSION = "litgroup_agent v3"
MAX_RATIONALE_WORDS = 25
DEFAULT_MAX_TOKENS = 16000
DEFAULT_CHUNK_SIZE = 40
REASONING_EFFORTS = ("low", "medium", "high")
REGION_ORDER = ("state", "nca", "us_subregion", "us_national", "global", "other", "unknown")
CORRECTIVE_TEMPLATE = ("These ids are missing: [{missing}]. These ids appear more than once: [{duplicates}]. "
                       "Return the complete corrected JSON with every id exactly once.")

SYSTEM_PROMPT_TEMPLATE = """You are grouping sentences that each state a general claim about <family>. Put sentences that make the same claim — the same mechanism, driver, caveat or consensus — into one group. Do not merge sentences that differ in direction, in the quantity involved, or in the causal factor. Tag every group and every singleton with claim_about, exactly one of:
- hazard_change_mechanism: why or how the hazard quantity itself changes — e.g. humidity, temperature, circulation, land surface;
- hazard_definition_or_measurement: what the index is or how it is measured;
- impact_or_exposure: consequences for people, health, economy, infrastructure;
- method_or_data: datasets, models, methods;
- other: none of the above.
Return JSON: groups: [{label: one short neutral sentence naming the shared claim, using only words that appear in the member sentences or common function words; member_ids: [...]; rationale: ≤25 words; claim_about: one of the five values}], singletons: [{id: ..., claim_about: one of the five values}]. Every input id appears exactly once."""

STRENGTHS = ("multi_source_supported", "review_supported", "single_source_supported", "background_only")
CLAIM_ABOUT = ("hazard_change_mechanism", "hazard_definition_or_measurement", "impact_or_exposure", "method_or_data", "other")
CORE_OR_CITED = ("core_candidate", "cited_candidate")
FUNCTION_WORDS = frozenset("""a an the and or but nor of in on at to for from by with without within into onto over under
between among about as than then that this these those which who whom whose what when where while how why is are was were
be been being has have had do does did can could may might must shall should will would not no more less most least very
it its their they them there here so such both either neither each every all any some other another same also only even
if because through across during before after up down out off per via""".split())
_DIGITS = re.compile(r"\d+(?:[.,]\d+)?")
_WORD = re.compile(r"[a-z]+")


def system_prompt(family_phrase: str) -> str:
    return SYSTEM_PROMPT_TEMPLATE.replace("<family>", family_phrase)


def chunk_partition(part: dict, chunk_size: int = DEFAULT_CHUNK_SIZE) -> list[dict]:
    """The partition cut into chunks of <= chunk_size statements (D-051): ordered by region class, then statement id."""
    rank = lambda s: (REGION_ORDER.index(c) if (c := part["meta"][s["local_id"]].get("region_class")) in REGION_ORDER  # noqa: E731
                      else len(REGION_ORDER), part["meta"][s["local_id"]]["statement_id"])
    ordered = sorted(part["statements"], key=rank)
    k = max(1, math.ceil(len(ordered) / chunk_size))
    base, extra = divmod(len(ordered), k)
    chunks, start = [], 0
    for c in range(1, k + 1):
        members = ordered[start:start + base + (c <= extra)]
        start += len(members)
        chunks.append({**part, "chunk_id": f"{part['partition_id']}.c{c}", "chunk_index": c, "n_chunks": k,
                       "partition_n_statements": part["n_statements"], "n_statements": len(members), "statements": members,
                       "meta": {s["local_id"]: part["meta"][s["local_id"]] for s in members}})
    return chunks


def call_chat(base_url, model, credential, messages, max_tokens, timeout, reasoning_effort=None):
    """softqa_agent.call_model with a message list and an optional `reasoning_effort` field (D-051)."""
    body = {"model": model, "temperature": 0, "max_tokens": max_tokens, "messages": messages}
    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {credential}", "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read().decode("utf-8", "replace"))
    msg = resp["choices"][0]["message"]
    content = msg.get("content") or msg.get("reasoning_content") or msg.get("reasoning") or ""
    return resp, content, round(time.time() - t0, 1)


def call_turn(base_url, model, credential, messages, max_tokens, timeout, reasoning_effort, say, iid, backoff):
    """(resp, content, secs, attempts, reasoning_effort_applied). An HTTP 400 with reasoning_effort sent is retried
    once without it."""
    def call(effort):
        return call_with_retries(lambda: call_chat(base_url, model, credential, messages, max_tokens, timeout, effort), say, iid, backoff)
    if not reasoning_effort:
        return (*call(None), False)
    try:
        return (*call(reasoning_effort), True)
    except ModelCallFailed as e:
        if not str(e).startswith("HTTP 400"):
            raise
        say(f"REASONING_EFFORT_REJECTED id={iid} reason={e}; retrying once without reasoning_effort")
        return (*call(None), False)


def turn_stats(resp) -> dict:
    choice = ((resp or {}).get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    return {"finish_reason": choice.get("finish_reason"), "content_chars": len(msg.get("content") or ""),
            "reasoning_chars": len(msg.get("reasoning_content") or msg.get("reasoning") or "")}


def user_prompt(part: dict) -> str:
    lines = [f"{s['local_id']}: {s['sentence']}" for s in part["statements"]]
    return f"SENTENCES ({len(lines)}):\n" + "\n".join(lines)


def extract_groups(content: str):
    """Last JSON object containing a 'groups' key."""
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
                        if isinstance(obj, dict) and "groups" in obj:
                            best = obj
                    except Exception:  # noqa: BLE001
                        pass
                    break
            i += 1
    return best


def check_partition(obj, part: dict):
    """(checks, groups, singletons): groups = [{member_ids, label, rationale, claim_about, checks}], singletons =
    [{id, claim_about, checks}], with local ids."""
    known = [s["local_id"] for s in part["statements"]]
    sentence = {s["local_id"]: s["sentence"] for s in part["statements"]}
    checks = {"parse_pass": isinstance(obj, dict) and isinstance(obj.get("groups"), list)}
    groups, singles = [], []
    if checks["parse_pass"]:
        for g in obj["groups"]:
            g = g if isinstance(g, dict) else {}
            ids = g.get("member_ids") if isinstance(g.get("member_ids"), list) else []
            groups.append({"member_ids": [str(i) for i in ids], "label": str(g.get("label") or ""),
                           "rationale": str(g.get("rationale") or ""), "claim_about": g.get("claim_about")})
        for i in obj.get("singletons") or []:
            if isinstance(i, dict):
                singles.append({"id": str(i.get("id")), "claim_about": i.get("claim_about")})
            elif not isinstance(i, list):
                singles.append({"id": str(i), "claim_about": None})
    returned = [i for g in groups for i in g["member_ids"]] + [x["id"] for x in singles]
    counts = {i: returned.count(i) for i in set(returned)}
    checks["unknown_ids"] = sorted(i for i in counts if i not in sentence)
    checks["duplicate_ids"] = sorted(i for i, n in counts.items() if n > 1)
    checks["missing_ids"] = [i for i in known if i not in counts]
    checks["empty_groups"] = sum(not g["member_ids"] for g in groups)
    checks["ids_exactly_once_pass"] = checks["parse_pass"] and not (checks["unknown_ids"] or checks["duplicate_ids"] or checks["missing_ids"])
    checks["no_empty_group_pass"] = checks["empty_groups"] == 0
    for g in groups:
        text = " ".join(sentence.get(i, "") for i in g["member_ids"])
        member_words = set(_WORD.findall(text.lower()))
        digits = [d for d in _DIGITS.findall(g["label"]) if d not in text]
        g["checks"] = {"label_present": bool(g["label"].strip()), "label_digits_not_in_members": digits,
                       "label_digit_pass": not digits,
                       "label_words_not_in_members": sorted({w for w in _WORD.findall(g["label"].lower())
                                                             if w not in member_words and w not in FUNCTION_WORDS}),
                       "rationale_words": len(g["rationale"].split()),
                       "rationale_over_limit": len(g["rationale"].split()) > MAX_RATIONALE_WORDS,
                       "single_member": len(g["member_ids"]) == 1,
                       "claim_about_pass": g["claim_about"] in CLAIM_ABOUT}
        g["checks"]["failed"] = [k for k in ("label_present", "label_digit_pass", "claim_about_pass") if not g["checks"][k]]
    for x in singles:
        ok = x["claim_about"] in CLAIM_ABOUT
        x["checks"] = {"claim_about_pass": ok, "failed": [] if ok else ["claim_about_pass"]}
    checks["failed"] = [k for k in ("parse_pass", "ids_exactly_once_pass", "no_empty_group_pass") if not checks[k]]
    return checks, groups, singles


def strength(meta: list[dict]) -> str:
    cc = {m["canonical_paper"] for m in meta if m["evidence_role"] in CORE_OR_CITED}
    if len(cc) >= 2:
        return "multi_source_supported"
    if any(m.get("passage_type") == "review_synthesis" for m in meta):
        return "review_supported"
    if cc:
        return "single_source_supported"
    return "background_only"


def group_record(kind, local_ids, part, label, rationale, claim_about, gchecks, common):
    meta = [part["meta"][i] for i in local_ids]
    roles = {}
    for m in meta: roles[m["evidence_role"]] = roles.get(m["evidence_role"], 0) + 1
    return {"group_id": None, "kind": kind, "arm": part["arm"], "statement_type": part["statement_type"],
            "partition_id": part["partition_id"], "chunk_id": part["chunk_id"], "split_by": part["split_by"],
            "member_ids": [m["statement_id"] for m in meta], "member_local_ids": local_ids,
            "label": label, "rationale": rationale, "claim_about": claim_about, "n_members": len(meta),
            "papers": sorted({m["paper_item_id"] for m in meta}), "canonical_papers": sorted({m["canonical_paper"] for m in meta}),
            "n_independent_core_cited_papers": len({m["canonical_paper"] for m in meta if m["evidence_role"] in CORE_OR_CITED}),
            "role_counts": dict(sorted(roles.items())), "evidence_strength": strength(meta),
            "independence_rule": "DR-LIT-IND-1 v2 (D-046)",
            "checks": gchecks, "status": "deterministic_fail" if gchecks and gchecks["failed"] else "deterministic_pass",
            "human_review": None, **common}


def summarise(out: Path, parts: list, endpoint=None, chunk_size=DEFAULT_CHUNK_SIZE, budget=None):
    chunks = [c for p in parts for c in chunk_partition(p, chunk_size)]
    order = {c["chunk_id"]: i for i, c in enumerate(chunks)}
    numbering, records = {}, []
    summary = {"generator_version": GENERATOR_VERSION, **(endpoint or {}), **(budget or {}), "chunk_size": chunk_size,
               "partitions_in_file": len(parts), "chunks_in_file": len(chunks),
               "chunks_per_partition": {p["partition_id"]: sum(c["partition_id"] == p["partition_id"] for c in chunks) for p in parts},
               "cross_chunk_merge": "not done by code (D-051)",
               "chunks_done": 0, "chunks_pass": 0, "chunks_fail": [], "corrective_retry_used": 0, "corrective_retry_pass": 0,
               "reasoning_effort_not_applied": 0, "finish_reasons": {}, "groups": 0, "singletons": 0,
               "groups_label_fail": 0, "by_strength": {s: 0 for s in STRENGTHS}, "groups_by_strength": {s: 0 for s in STRENGTHS},
               "statements_grouped": 0, "by_claim_about": {c: 0 for c in CLAIM_ABOUT}, "groups_by_claim_about": {c: 0 for c in CLAIM_ABOUT},
               "statements_by_claim_about": {c: 0 for c in CLAIM_ABOUT}, "claim_about_fail": 0,
               "endpoints_in_results": {}, "system_prompt_template_sha256": sha(SYSTEM_PROMPT_TEMPLATE),
               "corrective_template_sha256": sha(CORRECTIVE_TEMPLATE)}
    results = []
    for p in sorted(out.glob("*/result.json")):
        r = json.loads(p.read_text())
        if r.get("chunk_id") in order:
            results.append(r)
    for r in sorted(results, key=lambda r: order[r["chunk_id"]]):
        summary["chunks_done"] += 1
        ep = f"{r.get('endpoint_label')} {r.get('model')} {r.get('base_url')}"
        summary["endpoints_in_results"][ep] = summary["endpoints_in_results"].get(ep, 0) + 1
        summary["finish_reasons"][str(r.get("finish_reason"))] = summary["finish_reasons"].get(str(r.get("finish_reason")), 0) + 1
        summary["corrective_retry_used"] += bool(r.get("corrective_retry_used"))
        summary["corrective_retry_pass"] += bool(r.get("corrective_retry_used")) and r["status"] == "deterministic_pass"
        summary["reasoning_effort_not_applied"] += r.get("reasoning_effort_applied") is False
        if r["status"] != "deterministic_pass":
            summary["chunks_fail"].append({"chunk_id": r["chunk_id"], "failed": r["checks"].get("failed"),
                                           "parse_error": r.get("model_parse_error"), "finish_reason": r.get("finish_reason")})
            continue
        summary["chunks_pass"] += 1
        for g in r["groups"]:
            key = (g["arm"], g["statement_type"], r["chunk_index"])
            numbering[key] = numbering.get(key, 0) + 1
            g = dict(g, group_id=f"LG-{g['arm']}-{g['statement_type']}-c{r['chunk_index']}-{numbering[key]:03d}")
            records.append(g)
            summary["by_strength"][g["evidence_strength"]] += 1
            summary["statements_grouped"] += g["n_members"]
            if g["claim_about"] in CLAIM_ABOUT:
                summary["by_claim_about"][g["claim_about"]] += 1
                summary["statements_by_claim_about"][g["claim_about"]] += g["n_members"]
                if g["kind"] == "group": summary["groups_by_claim_about"][g["claim_about"]] += 1
            else:
                summary["claim_about_fail"] += 1
            if g["kind"] == "group":
                summary["groups"] += 1; summary["groups_by_strength"][g["evidence_strength"]] += 1
                summary["groups_label_fail"] += any(k != "claim_about_pass" for k in g["checks"]["failed"])
            else:
                summary["singletons"] += 1
    with open(out / "groups.jsonl", "w", encoding="utf-8") as f:
        for g in records: f.write(json.dumps(g, ensure_ascii=False, sort_keys=True) + "\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--partitions", required=True, help="partitions_v1.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--model", default="gpt-oss-120b")
    ap.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS); ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--reasoning-effort", choices=REASONING_EFFORTS, default="low")
    ap.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--only", default=None, help="partition or chunk ids, comma-separated")
    ap.add_argument("--sleep", type=float, default=0, help="seconds between chunks")
    ap.add_argument("--backoff", default=",".join(map(str, BACKOFF_SECONDS)), help="retry waits, seconds")
    ap.add_argument("--source-commit", default="unknown")
    a = ap.parse_args()
    credential = next((os.environ[v] for v in CREDENTIAL_ENV if os.environ.get(v)), None)
    if not credential:
        sys.exit(f"{CREDENTIAL_ENV[0]} env var not set")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    log = open(out / "agent.log", "a")

    def say(msg):
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"; print(line, flush=True); log.write(line + "\n"); log.flush()

    parts_raw = Path(a.partitions).read_bytes()
    parts = [json.loads(l) for l in parts_raw.decode("utf-8").splitlines() if l.strip()]
    chunks = [c for p in parts for c in chunk_partition(p, a.chunk_size)]
    only = set(a.only.split(",")) if a.only else None
    backoff = tuple(float(x) for x in a.backoff.split(","))
    endpoint = {"base_url": a.base_url, "model": a.model, "endpoint_label": endpoint_label(a.base_url)}
    budget = {"reasoning_effort": a.reasoning_effort, "max_tokens": a.max_tokens}
    say(f"START {GENERATOR_VERSION} partitions={len(parts)} chunks={len(chunks)} chunk_size={a.chunk_size} partitions_sha={sha(parts_raw.decode('utf-8'))[:12]} endpoint_label={endpoint['endpoint_label']} base_url={a.base_url} model={a.model} reasoning_effort={a.reasoning_effort} max_tokens={a.max_tokens} template_sha={sha(SYSTEM_PROMPT_TEMPLATE)[:12]}")

    done = 0
    for chunk in chunks:
        cid = chunk["chunk_id"]
        if only and cid not in only and chunk["partition_id"] not in only: continue
        cdir = out / cid
        if (cdir / "result.json").exists(): continue
        if a.limit and done >= a.limit: break
        if done and a.sleep: time.sleep(a.sleep)
        cdir.mkdir(parents=True, exist_ok=True)
        system, user = system_prompt(chunk["family_phrase"]), user_prompt(chunk)
        (cdir / "prompt_user.txt").write_text(user, encoding="utf-8")
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        t0 = time.time()
        try:
            resp, content, secs, attempts, applied = call_turn(a.base_url, a.model, credential, messages, a.max_tokens, a.timeout,
                                                               a.reasoning_effort, say, cid, backoff)
        except ModelCallFailed as e:
            (cdir / "model_error.txt").write_text(f"{e}\n")
            with open(out / "failed_chunks.txt", "a") as f: f.write(cid + "\n")
            done += 1
            say(f"FAIL chunk={cid} reason={e}")
            continue
        (cdir / "response.json").write_text(json.dumps(resp, indent=2, ensure_ascii=False))
        obj = extract_groups(content)
        perr = None if obj else "no JSON object with 'groups' found"
        checks, groups, singles = check_partition(obj, chunk)
        turns = [{"turn": 1, **turn_stats(resp), "http_attempts": attempts, "model_seconds": secs}]
        first_turn, corrective_error = None, None
        if checks["parse_pass"] and not checks["ids_exactly_once_pass"]:
            correction = CORRECTIVE_TEMPLATE.format(missing=", ".join(checks["missing_ids"]), duplicates=", ".join(checks["duplicate_ids"]))
            (cdir / "prompt_corrective.txt").write_text(correction, encoding="utf-8")
            first_turn = {"checks": checks, "groups_as_returned": groups, "singletons_as_returned": singles, **raw_fields(resp)}
            say(f"CORRECTIVE chunk={cid} missing={len(checks['missing_ids'])} duplicates={len(checks['duplicate_ids'])} unknown={len(checks['unknown_ids'])}")
            try:
                resp2, content2, secs2, attempts2, _ = call_turn(
                    a.base_url, a.model, credential, messages + [{"role": "assistant", "content": content}, {"role": "user", "content": correction}],
                    a.max_tokens, a.timeout, a.reasoning_effort if applied else None, say, cid, backoff)
            except ModelCallFailed as e:
                corrective_error = str(e)
                say(f"CORRECTIVE_FAIL chunk={cid} reason={e}")
            else:
                (cdir / "response_corrective.json").write_text(json.dumps(resp2, indent=2, ensure_ascii=False))
                resp, secs = resp2, secs + secs2
                turns.append({"turn": 2, **turn_stats(resp2), "http_attempts": attempts2, "model_seconds": secs2})
                obj = extract_groups(content2)
                perr = None if obj else "no JSON object with 'groups' found (corrective turn)"
                checks, groups, singles = check_partition(obj, chunk)
        common = {"generator_version": GENERATOR_VERSION, **endpoint, "temperature": 0, **budget, "reasoning_effort_applied": applied,
                  "chunk_size": a.chunk_size, "chunk_id": cid, "model_attempts": len(turns), "corrective_retry_used": first_turn is not None,
                  **turn_stats(resp),
                  "system_prompt_sha256": sha(system), "system_prompt_template_sha256": sha(SYSTEM_PROMPT_TEMPLATE),
                  "prompt_hash": sha(system + user), "source_commit": a.source_commit,
                  "generation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        status = "deterministic_pass" if not checks["failed"] else "deterministic_fail"
        records = []
        if status == "deterministic_pass":
            records = [group_record("group", g["member_ids"], chunk, g["label"], g["rationale"], g["claim_about"], g["checks"], common)
                       for g in groups]
            records += [group_record("singleton", [x["id"]], chunk, None, None, x["claim_about"], x["checks"], common) for x in singles]
        result = {"partition_id": chunk["partition_id"], "chunk_index": chunk["chunk_index"], "n_chunks": chunk["n_chunks"],
                  "arm": chunk["arm"], "statement_type": chunk["statement_type"], "split_by": chunk["split_by"],
                  "partition_n_statements": chunk["partition_n_statements"], "n_statements": chunk["n_statements"],
                  "local_ids": [x["local_id"] for x in chunk["statements"]], **common, "status": status, "checks": checks,
                  "groups_as_returned": groups, "singletons_as_returned": singles, "groups": records,
                  "turns": turns, "first_turn": first_turn, "corrective_error": corrective_error,
                  "corrective_template_sha256": sha(CORRECTIVE_TEMPLATE),
                  "model_seconds": secs, "model_parse_error": perr,
                  "elapsed_seconds": round(time.time() - t0, 1), **raw_fields(resp)}
        (cdir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
        done += 1
        say(f"{cid} n={chunk['n_statements']} status={status} groups={len(groups)} singletons={len(singles)} failed={checks['failed']} turns={len(turns)} finish={result['finish_reason']} model_s={secs} err={perr}")

    s = summarise(out, parts, endpoint, a.chunk_size, budget)
    say(f"DONE chunks={s['chunks_done']} pass={s['chunks_pass']} fail={len(s['chunks_fail'])} corrective={s['corrective_retry_used']} groups={s['groups']} singletons={s['singletons']}")


if __name__ == "__main__":
    main()
