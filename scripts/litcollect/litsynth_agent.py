#!/usr/bin/env python3
"""Pilot P2b / P3 — item-synthesis agent v4.1 (D-041, D-048, D-051, D-055, D-055a, D-055b, D-059 -- D-062; COORDINATOR rulings 2026-11-01 and 2026-11-02; work package P3a).

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

v3.2 (D-055b; synthesis run 1 --- agent v3.1, `litsynth/run1`, ten packets, all rejected_pre_review --- superseded):
the system prompt forbids any numeral with a decimal point and any exact pattern value in every rubric list; to tell the
grader exact values are not required it uses the fixed sentence `NOT_REQUIRED_SENTENCE`; magnitude language is copied
verbatim from `allowed_descriptors` ("roughly tripling", never "threefold"); a literature sentence resting only on
single-source groups carries one of the listed hedge words. Post-checks `synthesis_post_checks` v2.2 ("one" is not a
number-word). Format-class corrective turn: when the item parses and every post-check failure reason is a format failure
(`benchmark_items.format_class_only`: `exact_value_in_graded_text`, an untraced number-word, a missing hedge, or an
untraced number an allowed descriptor states under another form), one more turn in the same conversation
(`FORMAT_CORRECTIVE_PROMPT`, the reasons listed) asks for the complete corrected JSON with the facts unchanged, and every
check runs again on the reply. Any other failure (leakage, an untraced fact or id, schema, consistency) gets no turn.
`review.history[0]` holds the final check result and `corrective_turn_used`, `corrective_class` ("format" or null) and
`first_check` (the result that triggered the turn, with the first reply's raw text); an unparseable or failed corrective
reply keeps the first item, rejected_pre_review, with a `format corrective:` reason.

v4 (work package P3a; mentor 2026-11-13, D-059 -- D-062; packets v4, `scripts/build_synth_packets_v4.py`): the system
prompt asks for general words. The graded text (prompt, reference answer, every rubric list) uses the packet's
`plain_language` phrases (quantity without its threshold, "under a high-emissions future", "by mid-century" / "by late
this century") and never writes an RCP label, a threshold number, a year or "one study" / "a single study" (D-060); no
scenario talk beyond "a high-emissions future" (D-061); the hedge follows the cited groups' strength --- "research shows /
has shown" for a multi-source or review group, "research suggests" for single-source groups only (D-062); the question
may be two linked questions in one sentence or two short sentences; the required rubric points are direction, magnitude
class, place and the mechanisms resting on a multi-source or review group, a single-source mechanism is optional; the
fatal errors are climate errors only (wrong direction; projection as a certainty or forecast; baseline as observation;
FWI as fire; hazard as risk). Post-checks `synthesis_post_checks` v3 (v2.3 on by default, the generality rule, the
hedge-by-strength report); a generality failure is format-class (one corrective turn). `review.history[0]` also carries
the packet's `working_assumptions_relied_on` (D-064) and `fire_groups_unreviewed`. Everything else as v3.2.

v4.1 (work package P3b, D-066, D-067; synthesis run 4 --- v4, `litsynth/run4`, packets v4a: 6 deterministic_pass, 1
rejected_pre_review --- ingested; packets v4b, `scripts/build_synth_packets_v4b.py`): the system prompt uses the
DR-DESC-1 v4 descriptor forms --- one magnitude form as a natural phrase inside a sentence, never two magnitude phrases
for one pattern ("increase a slight increase" is an error), the comparison with other states only in a listed form,
never "tercile"; every sentence starts with a capital letter; a context group (role "context": a definition or a
measurement) only as an explanatory aside, never in a list of drivers or causes (D-067); for a regional contrast no
literature sentence claims to explain the contrast unless a cited group names the regions; nothing of the packet's
`must_not_use` anywhere, every rubric list included. Post-checks `synthesis_post_checks` v3.1 (v3 + `context_as_driver`,
tercile wording, doubled magnitude phrase, lower-case sentence start --- all format-class --- and two reports). The format
corrective prompt names the same rules. Everything else as v4.

Polaris invocation (Sophia vLLM, D-043). Run from the execution clone on Eagle (`$CLIMRR_REPO_ROOT`,
docs/SOPHIA_RUNBOOK.md) checked out at the pinned commit that carries the packets and provides `climrr`; output
under the litcollect root (`$LITCOLLECT_ROOT_POLARIS`, config key `litcollect_root_polaris`), never in the clone; the
ALCF credential in the environment; first check the environment: `python -c "import yaml, duckdb"`:

    bash "$CLIMRR_REPO_ROOT/scripts/sophia_pull_pinned.sh" <PINNED_SHA>
    cd "$CLIMRR_REPO_ROOT"
    python scripts/litcollect/litsynth_agent.py \\
        --packets artifacts/benchmark/synth_packets_v4b \\
        --out "$LITCOLLECT_ROOT_POLARIS/litsynth/run5" \\
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

GENERATOR_VERSION = "litsynth_agent v4.1"
CHECK_VERSION = bi.SYNTH_CHECK_VERSION_V31
CORRECTIVE_PROMPT = ("Your reply did not contain a JSON object with the keys \"prompt\" and \"reference_answer\". "
                     "Return the complete JSON object.")
NOT_REQUIRED_SENTENCE = "Exact values are not required; any statement consistent with the magnitude class counts."
FORMAT_CORRECTIVE_PROMPT = ("Your item failed these format checks:\n{reasons}\nReturn the complete corrected JSON object. Keep "
                            "every fact, pattern id, group id and source id unchanged; change only the wording the checks name. "
                            "Use the packet's \"plain_language\" phrases; in \"prompt\", \"reference_answer\" and \"rubric\" write "
                            "no emissions-scenario label, no threshold number or temperature, no year, no numeral with a decimal "
                            "point and no exact pattern value, never \"one study\" or \"a single study\", and no word of "
                            "\"must_not_use\" in any field or rubric list. Write the magnitude with ONE of the pattern's "
                            "\"magnitude_forms\", once per pattern, as a natural phrase in the sentence; compare with other states "
                            "only with one of the \"tercile_forms\" (to say exact values are not required, write: "
                            f"\"{NOT_REQUIRED_SENTENCE}\"). Start every sentence with a capital letter. A group whose role is "
                            "\"context\" is never a driver or a cause. A literature sentence that rests only on single-source "
                            "groups says \"research suggests\" and is marked \"hedged\": true.")


def format_corrective_prompt(reasons: list[str]) -> str:
    return FORMAT_CORRECTIVE_PROMPT.replace("{reasons}", "\n".join(f"- {r}" for r in reasons))

SYSTEM_PROMPT = """You write ONE closed-book benchmark item for climate scientists from a SEED PACKET. The packet holds (a) a table pattern: deterministic facts about modeled climate projections, in plain words, with "allowed_descriptors": the pattern-level words (direction, magnitude class with its "magnitude_forms", coarse anchor pair, comparison with other states with its "tercile_forms", regional ranking, horizon, scenario and quantity phrases) computed by code; (b) "plain_language": the phrases the item must use for the quantity, the scenario, the horizon and the hedges; (c) groups of literature statements: each group has an id, a role ("driver" or "context"), a label, an evidence strength, a "hedge" and member statements with their supporting passages and paper ids; (d) the use-case rung, the guardrails, the numbers you may use and "must_not_use": words never written anywhere in the item. Use ONLY facts in the packet. Add no fact, number, place, mechanism or source that is not in it.

GENERAL WORDS. The item is read by a general scientific reader and graded at the PATTERN level: direction, magnitude class, place, mechanism. In "prompt", "reference_answer" and every list of "rubric":
- name the quantity with the packet's "plain_language" "quantity" (or "quantity_short"), the scenario only as "under a high-emissions future", and the horizon only with the packet's horizon phrase ("by mid-century" or "by late this century");
- never write an emissions-scenario label (no "RCP", no "SSP"), a threshold number or temperature (no "95 °F", no "105 °F"), a year or a range of years, or a numeral with a decimal point;
- say nothing about scenarios beyond "under a high-emissions future", and compare no scenarios;
- never write "one study" or "a single study", and never any word or phrase of the packet's "must_not_use";
- these rules hold in EVERY rubric list too: "required_points", "acceptable_variants", "optional_points", "disallowed_claims" and "fatal_errors".
The exact values, the threshold, the scenario name and the years are attached to the item as provenance by code, never by you.

NUMBERS. The only digits allowed are those of the pattern's "anchor_pair", copied verbatim (for example "from about 16 to about 45 days a summer"). Never write a number as a word ("sixteen", "forty-five", "twice", "double", "triple", "half", "threefold"), except inside one of the listed "magnitude_forms" (for example "roughly tripling", "about twice as many" or "about half again as many"). State no ratio, percentage or range the packet does not list.

MAGNITUDE AND COMPARISON. Write the magnitude with ONE of the pattern's "magnitude_forms", any one, used as a natural phrase inside the sentence ("... is projected to increase slightly ...", "... shows a slight increase ...", "... days remain rare ..."). Never write two magnitude phrases for one pattern: "increase a slight increase" and "increase by a slight increase" are errors. Compare the place with other states only with one of the "tercile_forms" ("a larger change than in most states"); never write "tercile", "ranking large" or "moderate relative tercile".

WRITING. Every sentence starts with a capital letter ("Research shows ...", never "research shows ..."). Short sentences, plain words.

CONTEXT GROUPS. A group whose "role" is "context" (how the quantity is defined or measured, such as "the heat index combines temperature and humidity") is never a driver or a cause of the change. Use it only as an explanatory aside ("Because the heat index combines temperature and humidity, ..."), never in a list of drivers or causes, and never with "driven by", "driver", "cause" or "because of" in the same clause.

REGIONAL CONTRASTS. For a regional-contrast pattern, no literature sentence may claim to explain the contrast between regions unless a group it cites names those regions. The question asks how the quantity changes, which regions see the largest and smallest change, and what drives the increase; the answer says that the ranking comes from the projection and that the drivers are general.

HEDGES, by evidence strength. Each group carries its "hedge". A literature sentence that rests on at least one multi_source_supported or review_supported group says "research shows" or "research has shown" and is marked "hedged": false. A literature sentence that rests only on single_source_supported groups says "research suggests" and is marked "hedged": true. Never present a single-source claim as established.

Return ONE JSON object with exactly these keys:
- "prompt": a closed-book question that a well-informed climate scientist could answer from general knowledge, in plain words and short sentences: either one sentence holding two linked questions (how the quantity is projected to change, and why) or two short sentences. It asks about the general pattern and its drivers for the place, season and horizon the packet names, "under a high-emissions future". It must NOT name or hint at any table, dataset, data portal, model output, paper, study, author, column, variable name or grid cell, and must not say "according to", "the table", "the data", "the paper" or "the study". It must not require recalling a number: ask for direction, rough size, ranking or contrast, and the drivers.
- "reference_answer": {
  "table_pattern": [{"sentence": "...", "pattern_ids": ["..."]}] --- each sentence states what the pattern shows, in the pattern's allowed descriptors (direction, one magnitude form, place or regional ranking with largest / smallest, the comparison with other states where given, horizon and scenario phrases), and is tagged with the pattern id(s) it comes from;
  "literature_interpretation": [{"sentence": "...", "group_ids": ["..."], "hedged": true or false}] --- each sentence rests on the group(s) it cites and uses the hedge above. If the packet has no groups, return [];
  "integrated": "a short paragraph that combines the two, in the same words, with no new fact" }
- "rubric": {"required_points": [{"point": "...", "weight": 1, 2 or 3, "source_ids": ["..."]}], "acceptable_variants": ["..."], "optional_points": [{"point": "...", "source_ids": ["..."]}], "disallowed_claims": ["..."], "fatal_errors": ["..."]}. Every required and optional point MUST carry "source_ids": the pattern id(s) and / or group id(s) from the packet that the point rests on. The required points are exactly: the direction; the magnitude class; the place (for a regional contrast, the ranking: largest / smallest); and each mechanism that rests on a multi_source_supported or review_supported group. A mechanism that rests only on single_source_supported groups is an optional point, never a required one. The anchor pair, if used at all, is an optional point. "fatal_errors" lists climate errors only: the wrong direction; stating the projection as a certainty or a forecast; treating the modeled historical baseline as an observation; reading fire-weather danger as fire occurrence; treating a hazard as a risk. To tell the grader that exact values are not required, write exactly: "Exact values are not required; any statement consistent with the magnitude class counts.".
- "guardrails": the packet guardrails that apply to this item, verbatim or made more specific.
- "source_independent_answerability": "yes", "borderline" or "no" --- could a well-informed climate scientist answer without the packet's sources?
- "source_independence_note": one sentence explaining that judgement.
- "capability_tested", "system_task", "key_relationships", "evidence_needed", "desired_output_characteristics": one short phrase each, for the packet's use-case rung.
- "expected_knowledge_level": "general_climate_science" or "specialist_climate_science".

Respect every guardrail: a modeled historical baseline is model output, not an observation; a Fire Weather Index is meteorological fire danger, never fire occurrence; a high-emissions future is one plausible future, not a forecast; hazard is not exposure and exposure is not risk. Return ONLY the JSON object."""

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


def finish(item: dict, tagged: dict, packet: dict, common: dict, columns, parse_error=None, extra_reasons=()) -> dict:
    if parse_error:
        res = {"check_version": CHECK_VERSION, "pass": False, "reasons": [f"parse: {parse_error}"], "checks": {}}
    else:
        res = bi.synthesis_post_checks(item, tagged, packet["checks_input"], columns, check_version=CHECK_VERSION)
    if extra_reasons:
        res = {**res, "pass": False, "reasons": res["reasons"] + list(extra_reasons)}
    item["review"]["status"] = "deterministic_pass" if res["pass"] else "rejected_pre_review"
    item["review"]["history"] = [{"event": "deterministic_pass" if res["pass"] else "deterministic_fail", "reasons": res["reasons"],
                                  "check_version": res["check_version"], "checks": res["checks"], "reference_answer_tagged": tagged,
                                  "seed_id": packet["seed_id"], "packet_id": packet["packet_id"],
                                  "working_assumptions_relied_on": packet.get("working_assumptions_relied_on") or [],
                                  "fire_groups_unreviewed": bool(packet.get("fire_groups_unreviewed")), **common}]
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
         "corrective_prompt_sha256": sha(CORRECTIVE_PROMPT), "format_corrective_prompt_sha256": sha(FORMAT_CORRECTIVE_PROMPT),
         "items": len(items),
         "deterministic_pass": sum(it["review"]["status"] == "deterministic_pass" for it in items),
         "deterministic_fail": sum(it["review"]["status"] != "deterministic_pass" for it in items),
         "fail_reasons_by_kind": dict(sorted(reasons.items())),
         "corrective_retry_used": sum(bool(h.get("corrective_retry_used")) for h in hist),
         "format_corrective_used": sum(bool(h.get("corrective_turn_used")) for h in hist),
         "format_corrective_pass": sum(bool(h.get("corrective_turn_used")) and h["event"] == "deterministic_pass" for h in hist),
         "reasoning_effort_not_applied": sum(h.get("reasoning_effort_applied") is False for h in hist),
         "finish_reasons": {k: sum(str(h.get("finish_reason")) == k for h in hist) for k in sorted({str(h.get("finish_reason")) for h in hist})},
         "by_level": {str(k): sum(it["use_case_level"] == k for it in items) for k in sorted({it["use_case_level"] for it in items})},
         "check_version": CHECK_VERSION,
         "hedge_by_strength_flags": sum(len(h.get("checks", {}).get("hedge_by_strength") or []) for h in hist)}
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
        convo = messages + [{"role": "assistant", "content": content}]
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
                convo += [{"role": "user", "content": CORRECTIVE_PROMPT}, {"role": "assistant", "content": content2}]
                turns.append({"turn": 2, **turn_stats(resp2), "http_attempts": attempts2, "model_seconds": secs2})
                obj = extract_item(content2)
                perr = None if obj else "no JSON object with 'prompt' and 'reference_answer' found (corrective turn)"
        common = {"generator_version": GENERATOR_VERSION, **endpoint, "temperature": 0, **budget, "reasoning_effort_applied": applied,
                  "system_prompt_sha256": sha(SYSTEM_PROMPT), "corrective_prompt_sha256": sha(CORRECTIVE_PROMPT),
                  "prompt_hash": sha(SYSTEM_PROMPT + user), "packet_sha256": sha(raw), "source_commit": a.source_commit,
                  "generation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "model_seconds": secs,
                  "model_attempts": len(turns), "corrective_retry_used": first_turn is not None, "turns": turns,
                  "first_turn": first_turn, "corrective_error": corrective_error, "corrective_turn_used": False,
                  "corrective_class": None, "first_check": None, **turn_stats(resp), **raw_fields(resp)}
        item, tagged = assemble(obj or {}, packet, common, columns)
        item = finish(item, tagged, packet, common, columns, perr)
        h = item["review"]["history"][0]
        if not perr and bi.format_class_only(h["reasons"], packet["checks_input"].get("allowed_descriptors") or []):
            fprompt = format_corrective_prompt(h["reasons"])
            (rdir / "prompt_format_corrective.txt").write_text(fprompt, encoding="utf-8")
            first_check = {**{k: h[k] for k in ("event", "reasons", "check_version", "checks", "reference_answer_tagged")}, **raw_fields(resp)}
            say(f"FORMAT_CORRECTIVE seed={sid} reasons={len(h['reasons'])}")
            obj3, ferr = None, None
            try:
                resp3, content3, secs3, attempts3, _ = call_turn(
                    a.base_url, a.model, credential, convo + [{"role": "user", "content": fprompt}],
                    a.max_tokens, a.timeout, a.reasoning_effort if applied else None, say, sid, backoff)
            except ModelCallFailed as e:
                ferr = f"model call failed: {e}"
                say(f"FORMAT_CORRECTIVE_FAIL seed={sid} reason={e}")
            else:
                (rdir / "response_format_corrective.json").write_text(json.dumps(resp3, indent=2, ensure_ascii=False))
                resp, secs = resp3, secs + secs3
                turns.append({"turn": len(turns) + 1, **turn_stats(resp3), "http_attempts": attempts3, "model_seconds": secs3})
                obj3 = extract_item(content3)
                ferr = None if obj3 else "no JSON object with 'prompt' and 'reference_answer' found"
            common = {**common, "model_seconds": secs, "model_attempts": len(turns), "turns": turns, "corrective_turn_used": True,
                      "corrective_class": "format", "first_check": first_check,
                      "format_corrective_prompt_sha256": sha(fprompt), **turn_stats(resp), **raw_fields(resp)}
            if obj3:
                item, tagged = assemble(obj3, packet, common, columns)
                item = finish(item, tagged, packet, common, columns)
            else:                                                  # keep the first item, rejected, with the turn's failure
                item = finish(item, tagged, packet, common, columns, extra_reasons=[f"format corrective: {ferr}"])
        ipath.write_text(json.dumps(item, indent=2, ensure_ascii=False))
        done += 1
        reasons = item["review"]["history"][0]["reasons"]
        say(f"{sid} level={item['use_case_level']} status={item['review']['status']} reasons={len(reasons)} model_s={secs} elapsed={round(time.time() - t0, 1)} err={perr}")

    s = summarise(out, endpoint, budget)
    say(f"DONE items={s['items']} pass={s['deterministic_pass']} fail={s['deterministic_fail']}")


if __name__ == "__main__":
    main()
