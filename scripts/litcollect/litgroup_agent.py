#!/usr/bin/env python3
"""Pilot P2b — literature-statement grouping agent v1 (D-048; COORDINATOR rulings 2026-11-01).

Input: `artifacts/litgroups/partitions_v1.jsonl` (`scripts/build_group_partitions.py`): one partition = arm x
statement_type over the core / cited / background_consensus statements of litstatements run 2, split
deterministically where over 120 statements. One model call per partition. The model sees **local ids (S001...)
and sentences only** --- no passage, no paper id (statement ids LS-<item_id>-<nn> carry it, so they are not sent),
no table. It returns groups of sentences that make the same claim and singletons. Temperature 0.

Deterministic checks per partition: the JSON parses; every returned id exists in the partition and appears exactly
once across groups and singletons, and every input id appears (else the partition is `deterministic_fail` and none
of its groups is written to groups.jsonl); no group is empty. Per group: a label holds no digit sequence that is not in
a member sentence (else the group is `deterministic_fail`, kept and flagged). Recorded, not gating: label words that
are neither in a member sentence nor a function word; a rationale over 25 words. A group whose members come from one
paper only is still a group. Singletons become one-member records (kind `singleton`, no label).

Strength per group (D-045 definitions, D-046 independence --- the canonical paper id travels in the partition's
`meta`, never sent): `multi_source_supported` (>= 2 canonical papers among core / cited members), else
`review_supported` (a review_synthesis member), else `single_source_supported` (a core / cited member), else
`background_only`.

Output: per partition `<out>/<partition_id>/result.json` (+ `prompt_user.txt`, `response.json`; raw model text
in result.json as in litstatement_agent v3), aggregate `groups.jsonl` (group_id `LG-<arm>-<type>-<nnn>`, numbered per
arm x type over its partitions in file order, groups then singletons) and `summary.json`; `agent.log`. Restartable
per partition (skips partitions with result.json). Retries, backoff, `--base-url`, `--model`, `--sleep` as in
litstatement_agent v3 (imported); `--max-tokens` default 6000.

Polaris invocation (Sophia vLLM, D-043; the repo clone on Eagle at a pinned commit; the ALCF credential in the
environment):

    python scripts/litcollect/litgroup_agent.py \\
        --partitions artifacts/litgroups/partitions_v1.jsonl \\
        --out <EAGLE_LITCOLLECT_ROOT>/litgroups/run1 \\
        --base-url https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1 \\
        --model openai/gpt-oss-120b --sleep 5 --source-commit <PINNED_SHA>
"""
import argparse, json, os, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from softqa_agent import call_model  # noqa: E402  (v2, pinned byte-identical)
from litstatement_agent import (  # noqa: E402  (v3)
    BACKOFF_SECONDS, CREDENTIAL_ENV, DEFAULT_BASE_URL, ModelCallFailed, call_with_retries, endpoint_label, raw_fields, sha)

GENERATOR_VERSION = "litgroup_agent v1"
MAX_RATIONALE_WORDS = 25

SYSTEM_PROMPT_TEMPLATE = """You are grouping sentences that each state a general claim about <family>. Put sentences that make the same claim — the same mechanism, driver, caveat or consensus — into one group. Do not merge sentences that differ in direction, in the quantity involved, or in the causal factor. Return JSON: groups: [{label: one short neutral sentence naming the shared claim, using only words that appear in the member sentences or common function words; member_ids: [...]; rationale: ≤25 words}], singletons: [ids]. Every input id appears exactly once."""

STRENGTHS = ("multi_source_supported", "review_supported", "single_source_supported", "background_only")
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
    """(checks, groups, singletons): groups = [{member_ids, label, rationale, checks}] with local ids."""
    known = [s["local_id"] for s in part["statements"]]
    sentence = {s["local_id"]: s["sentence"] for s in part["statements"]}
    checks = {"parse_pass": isinstance(obj, dict) and isinstance(obj.get("groups"), list)}
    groups, singles = [], []
    if checks["parse_pass"]:
        for g in obj["groups"]:
            g = g if isinstance(g, dict) else {}
            ids = g.get("member_ids") if isinstance(g.get("member_ids"), list) else []
            groups.append({"member_ids": [str(i) for i in ids], "label": str(g.get("label") or ""),
                           "rationale": str(g.get("rationale") or "")})
        singles = [str(i) for i in obj.get("singletons") or [] if not isinstance(i, (dict, list))]
    returned = [i for g in groups for i in g["member_ids"]] + singles
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
                       "single_member": len(g["member_ids"]) == 1}
        g["checks"]["failed"] = [k for k in ("label_present", "label_digit_pass") if not g["checks"][k]]
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


def group_record(kind, local_ids, part, label, rationale, gchecks, common):
    meta = [part["meta"][i] for i in local_ids]
    roles = {}
    for m in meta: roles[m["evidence_role"]] = roles.get(m["evidence_role"], 0) + 1
    return {"group_id": None, "kind": kind, "arm": part["arm"], "statement_type": part["statement_type"],
            "partition_id": part["partition_id"], "split_by": part["split_by"],
            "member_ids": [m["statement_id"] for m in meta], "member_local_ids": local_ids,
            "label": label, "rationale": rationale, "n_members": len(meta),
            "papers": sorted({m["paper_item_id"] for m in meta}), "canonical_papers": sorted({m["canonical_paper"] for m in meta}),
            "n_independent_core_cited_papers": len({m["canonical_paper"] for m in meta if m["evidence_role"] in CORE_OR_CITED}),
            "role_counts": dict(sorted(roles.items())), "evidence_strength": strength(meta),
            "independence_rule": "DR-LIT-IND-1 v2 (D-046)",
            "checks": gchecks, "status": "deterministic_fail" if gchecks and gchecks["failed"] else "deterministic_pass",
            "human_review": None, **common}


def summarise(out: Path, parts: list, endpoint=None):
    order = {p["partition_id"]: i for i, p in enumerate(parts)}
    numbering, records = {}, []
    summary = {"generator_version": GENERATOR_VERSION, **(endpoint or {}), "partitions_in_file": len(parts),
               "partitions_done": 0, "partitions_pass": 0, "partitions_fail": [], "groups": 0, "singletons": 0,
               "groups_label_fail": 0, "by_strength": {s: 0 for s in STRENGTHS}, "groups_by_strength": {s: 0 for s in STRENGTHS},
               "statements_grouped": 0, "endpoints_in_results": {}, "system_prompt_template_sha256": sha(SYSTEM_PROMPT_TEMPLATE)}
    results = []
    for p in sorted(out.glob("*/result.json")):
        r = json.loads(p.read_text())
        if r.get("partition_id") in order:
            results.append(r)
    for r in sorted(results, key=lambda r: order[r["partition_id"]]):
        summary["partitions_done"] += 1
        ep = f"{r.get('endpoint_label')} {r.get('model')} {r.get('base_url')}"
        summary["endpoints_in_results"][ep] = summary["endpoints_in_results"].get(ep, 0) + 1
        if r["status"] != "deterministic_pass":
            summary["partitions_fail"].append({"partition_id": r["partition_id"], "failed": r["checks"].get("failed"),
                                               "parse_error": r.get("model_parse_error")})
            continue
        summary["partitions_pass"] += 1
        for g in r["groups"]:
            key = (g["arm"], g["statement_type"])
            numbering[key] = numbering.get(key, 0) + 1
            g = dict(g, group_id=f"LG-{g['arm']}-{g['statement_type']}-{numbering[key]:03d}")
            records.append(g)
            summary["by_strength"][g["evidence_strength"]] += 1
            summary["statements_grouped"] += g["n_members"]
            if g["kind"] == "group":
                summary["groups"] += 1; summary["groups_by_strength"][g["evidence_strength"]] += 1
                summary["groups_label_fail"] += g["status"] == "deterministic_fail"
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
    ap.add_argument("--max-tokens", type=int, default=6000); ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--only", default=None, help="partition ids, comma-separated")
    ap.add_argument("--sleep", type=float, default=0, help="seconds between partitions")
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
    only = set(a.only.split(",")) if a.only else None
    backoff = tuple(float(x) for x in a.backoff.split(","))
    endpoint = {"base_url": a.base_url, "model": a.model, "endpoint_label": endpoint_label(a.base_url)}
    say(f"START {GENERATOR_VERSION} partitions={len(parts)} partitions_sha={sha(parts_raw.decode('utf-8'))[:12]} endpoint_label={endpoint['endpoint_label']} base_url={a.base_url} model={a.model} template_sha={sha(SYSTEM_PROMPT_TEMPLATE)[:12]}")

    done = 0
    for part in parts:
        pid = part["partition_id"]
        if only and pid not in only: continue
        pdir = out / pid
        if (pdir / "result.json").exists(): continue
        if a.limit and done >= a.limit: break
        if done and a.sleep: time.sleep(a.sleep)
        pdir.mkdir(parents=True, exist_ok=True)
        system, user = system_prompt(part["family_phrase"]), user_prompt(part)
        (pdir / "prompt_user.txt").write_text(user, encoding="utf-8")
        t0 = time.time()
        try:
            resp, content, secs, attempts = call_with_retries(
                lambda: call_model(a.base_url, a.model, credential, system, user, a.max_tokens, a.timeout), say, pid, backoff)
        except ModelCallFailed as e:
            (pdir / "model_error.txt").write_text(f"{e}\n")
            with open(out / "failed_partitions.txt", "a") as f: f.write(pid + "\n")
            done += 1
            say(f"FAIL partition={pid} reason={e}")
            continue
        (pdir / "response.json").write_text(json.dumps(resp, indent=2, ensure_ascii=False))
        obj = extract_groups(content)
        perr = None if obj else "no JSON object with 'groups' found"
        checks, groups, singles = check_partition(obj, part)
        common = {"generator_version": GENERATOR_VERSION, **endpoint, "temperature": 0,
                  "system_prompt_sha256": sha(system), "system_prompt_template_sha256": sha(SYSTEM_PROMPT_TEMPLATE),
                  "prompt_hash": sha(system + user), "source_commit": a.source_commit,
                  "generation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        status = "deterministic_pass" if not checks["failed"] else "deterministic_fail"
        records = []
        if status == "deterministic_pass":
            records = [group_record("group", g["member_ids"], part, g["label"], g["rationale"], g["checks"], common) for g in groups]
            records += [group_record("singleton", [i], part, None, None, None, common) for i in singles]
        result = {"partition_id": pid, "arm": part["arm"], "statement_type": part["statement_type"], "split_by": part["split_by"],
                  "n_statements": part["n_statements"], **common, "status": status, "checks": checks,
                  "groups_as_returned": groups, "singletons_as_returned": singles, "groups": records,
                  "model_seconds": secs, "model_attempts": attempts, "model_parse_error": perr,
                  "elapsed_seconds": round(time.time() - t0, 1), **raw_fields(resp)}
        (pdir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
        done += 1
        say(f"{pid} n={part['n_statements']} status={status} groups={len(groups)} singletons={len(singles)} failed={checks['failed']} model_s={secs} err={perr}")

    s = summarise(out, parts, endpoint)
    say(f"DONE partitions={s['partitions_done']} pass={s['partitions_pass']} fail={len(s['partitions_fail'])} groups={s['groups']} singletons={s['singletons']}")


if __name__ == "__main__":
    main()
