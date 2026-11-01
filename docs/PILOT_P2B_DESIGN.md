# Pilot P2b --- grouping, synthesis, packets, post-checks and shortlist (design)

**Status.** P2b-prep built on `work/meeting-2026-10-22` (D-046, D-047, D-048; authorized by D-041 and the
COORDINATOR rulings of 2026-11-01). **No model call has been made; no item exists.** The two agents below
are pinned in their tests and wait for a Polaris run. Nothing here changes a column status, the concept map or a
compatibility rule.

## 1. Where P2b sits

```
run-2 statements (D-044) ── independence v2 (D-046) ── geography v2 (D-047) ── seeds v2 (D-048)
        │                                                                        │
        └── partitions ── litgroup_agent (Polaris) ── groups.jsonl ──┐           │
                                                                     ├── packets ── litsynth_agent (Polaris)
                                         pilot shortlist (20) ── Kaiyuan selects 10 ┘        │
                                                                                   items ── post-checks ── review
```

## 2. Grouping agent --- `scripts/litcollect/litgroup_agent.py` v1

- **Input.** `artifacts/litgroups/partitions_v1.jsonl` (`scripts/build_group_partitions.py`,
  `src/climrr/litgroups.py`): arm x statement_type over the 747 core / cited / background-consensus statements.
  A partition over 120 statements is split by lexical direction, then by region class, then into equal chunks
  in id order; the split is recorded. Run 2 gives **11 partitions**; only extreme-heat mechanism (144) splits,
  by direction, into 28 and 116.
- **What the model sees.** Opaque local ids (`S001`...) and sentences. Statement ids `LS-<item_id>-<nn>` carry
  the paper id, so they are not sent; no passage, paper id or table. The paper, its D-046 canonical id, the
  evidence role and the passage type travel in the partition's `meta` and stay local.
- **System prompt.** The ruling text verbatim, with `<family>` filled per arm ("the heat index and humid heat" /
  "fire weather and fire danger indices"). Template SHA-256
  `ca7fec4c7b9b1736d561e73da7ad3d268b7adb4d56d61bf81b76bc181c51bfc9`; rendered: heat
  `8d573531149d3599fed924b8055f894c9a0222ba3f4e16d3964fee75669a42af`, fire
  `90c5a737df9cd909cdef4ea50d56ab586c64eff1ac4779d0de536ba3acc003d1`. Temperature 0; `--max-tokens` 6000.
- **Checks.** Partition: the JSON parses; every returned id exists and appears exactly once across groups and
  singletons, and every input id appears; no empty group --- else `deterministic_fail` and **none of its groups
  is written**. Group: a label digit must occur in a member sentence --- else that group is
  `deterministic_fail` (kept, flagged). Recorded, not gating: label words outside the members and the function
  words; a rationale over 25 words; a one-member group.
- **Strength per group** (D-045 definitions, D-046 independence): `multi_source_supported` (>= 2 canonical papers
  among core / cited members), `review_supported`, `single_source_supported`, `background_only`. Singletons are
  written as one-member records so that every statement has a group id.
- **Output.** `groups.jsonl` (group_id `LG-<arm>-<type>-<nnn>`, members, label, rationale, partition, model, prompt
  hash, strength), `summary.json`, per partition `result.json` with the raw model text, `prompt_user.txt`,
  `response.json`; `agent.log`. Restartable per partition. Retries, backoff and the host flags as in
  `litstatement_agent` v3 (imported).

## 3. Seed packets --- `scripts/build_synth_packets.py`, `src/climrr/synthpackets.py`

A packet is built per selected seed, at the level the shortlist gives it, in three parts:

| part | sent to the model | contents |
| --- | --- | --- |
| `model_view` | **yes** | the pattern in plain words (place, quantity with its °F threshold, season, horizon and window, RCP8.5 with the guardrail text, statistic, direction, values rounded to one decimal, cell range, robustness, relative tercile); the groups (id, type, label, strength, independent papers, members with statement, passage cut to 400 characters, paper id, region); the allowed numbers; the guardrails; the item fields; the D-038 rung |
| `provenance` | no | the full pattern record; per member the paper SHA-256, json path, span and the full passage; the item frame (level, modality) |
| `checks_input` | no | pattern ids, group ids and strengths, allowed numbers, forbidden strings (the pattern's columns, the packet's paper ids) |

**Groups in a packet** (EXECUTOR choice, for confirmation): >= 1 member geography-relevant to the pattern
(D-047); type mechanism / driver / consensus / caveat (schema v2 has no `pattern` literature type); strength over
the relevant members not `background_only` (schema v2 has no such strength); only relevant members carried and
the strength recomputed over them; ranked by strength, named-place members, size; at most 10 mechanism / driver /
consensus groups and 4 caveat groups (scenario-naming first). A level-1 packet carries no group.

**Numbers** (EXECUTOR): a value is shown to one decimal place, half up; allowed are that form, the nearest integer
and the exact stored string, plus the threshold, the horizon years, the robustness counts, the tercile's number of
states and the ranks.

## 4. Synthesis agent --- `scripts/litcollect/litsynth_agent.py` v1

- **System prompt** (stored verbatim; SHA-256 `8750154045817aeff187674d67efef3b0560947de10c381bc85c9bf0e077ccd9`):
  a closed-book prompt naming no table, dataset, paper, column, cell or "according to", about the general pattern
  and its drivers at state / region level; `reference_answer` decomposed into table-pattern sentences tagged with
  pattern ids (numbers exact or the disclosed range / direction / tercile), literature sentences tagged with group
  ids (single-source groups hedged and flagged) and an integrated paragraph; a rubric with weighted required
  points, acceptable variants, optional points, disallowed claims, fatal errors; guardrails;
  source-independent answerability with a note; **no fact not in the packet**.
- **Assembly.** The agent builds a schema-v2 item: `reference_components` from the packet's provenance (one
  literature statement per cited group; supports = the group's core / cited / review members with exact spans;
  `reference_scope` `single_study_observation` for a single-source group, else `regional_climate_expectation`),
  `source_leakage_check` computed, `generation` with the packet and prompt hashes. Required-point weights are written
  `[w=n] point`; the tagged decomposition, which schema v2 has no field for, is kept in `review.history[0]`.
- **Post-checks** (`climrr.benchmark_items.synthesis_post_checks`): every number in the reference answer and the
  rubric traces to the packet (scenario names and ordinals are not numbers); tags and citations exist in the
  packet; single-source-only sentences are marked hedged and carry a hedge word; the prompt passes
  `leakage_check` and names no internal id, identifier-like name, column or paper id; the reference texts pass
  `text_leakage` (ClimRR, column names, "according to" / "the table" / "the paper", "et al.", years in parentheses,
  corpus and internal ids); schema v2 and `consistency_errors`.
- **Status.** Pass -> `review.status: deterministic_pass`. Fail -> **`review.status: rejected_pre_review`** with
  `review.history[0] = {event: deterministic_fail, reasons}`. *The work package said `review.status:
  deterministic_fail`; schema v2's status enum has no such value, and `rejected_pre_review` is its value for a
  deterministic rejection before human review. Flagged to the COORDINATOR; adding the value to the schema is a
  one-line change if preferred.*
- **Output.** `items/<seed_id>.json`, `items.jsonl`, `summary.json`, `raw/<seed_id>/{prompt_user.txt,
  response.json}`, `agent.log`. Restartable per packet. It imports `climrr` from the repo clone, so it needs PyYAML.

## 5. Pilot shortlist --- `scripts/pilot_shortlist.py`, `src/climrr/pilot_shortlist.py`

`artifacts/benchmark/pilot_shortlist_v1.csv` (tracked): 20 eligible heat-index seeds --- level 1 x 3 (pattern only;
direction or a tercile), level 3 x 9 (the 8 combinations of 95 / 105 °F, mid / end, absolute / percent change, in
turn, the ninth repeating the first), level 4 x 6 (regional contrasts), level 7 x 2 (a relevant caveat naming a
scenario); highest-ranked first; at most 2 seeds per state. EXECUTOR choices: levels filled 7, 3, 4, 1 (scarcest
first, so pattern-only items do not spend the states the literature levels need); a regional contrast is not
capped; the control cell is not shortlisted. Result: all quotas met, no shortfall (candidates: level 1 946, level 3
446, level 4 16, level 7 1,280). Besides the top three statements by rank the CSV lists each seed's top named-place
statements, because the strength-first rank puts the same U.S.-national statements on top of every seed.

## 6. Polaris run plan

Kaiyuan runs each step on Polaris (Sophia vLLM, `openai/gpt-oss-120b`, D-043) from the Eagle clone at a pinned
commit, and copies back the small evidence.

1. **Grouping run.** `python -c "import yaml, duckdb"`; then
   ```
   python scripts/litcollect/litgroup_agent.py --partitions artifacts/litgroups/partitions_v1.jsonl \
       --out <EAGLE_LITCOLLECT_ROOT>/litgroups/run1 \
       --base-url https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1 \
       --model openai/gpt-oss-120b --sleep 5 --source-commit <PINNED_SHA>
   ```
   Deliver `litgroups/run1` (groups.jsonl, summary.json, agent.log, per-partition files) as a tarball.
2. **Ingest and human check of the groups** (a following package): verify the tarball, freeze `groups.jsonl`, review
   labels and merges; a failed partition is re-run with `--only`.
3. **Kaiyuan selects 10 of the 20 shortlisted seeds.**
4. **Packets** (local): `python scripts/build_synth_packets.py --groups <groups.jsonl> --select <10 seed ids>`;
   commit and push the packets.
5. **Synthesis run.**
   ```
   python scripts/litcollect/litsynth_agent.py --packets artifacts/benchmark/synth_packets \
       --out <EAGLE_LITCOLLECT_ROOT>/litsynth/run1 \
       --base-url https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1 \
       --model openai/gpt-oss-120b --sleep 5 --source-commit <PINNED_SHA>
   ```
6. **Ingest, review workbook** (a following package): items with their post-check reasons go to Kaiyuan, then the
   mentor (D-041 condition F).

## 7. Open points for the COORDINATOR

- `deterministic_fail` vs schema v2's `rejected_pre_review` (section 4).
- The EXECUTOR choices in D-048 (seed rank, levels with 1 always applicable), section 3 (packet groups, rounding) and
  section 5 (fill order, control cell, regional contrasts uncapped).
- D-047 as written drops 50 U.S.-wide statements with a subnational scope and directional adjectives ("southeastern").
- Most named-place heat-index statements are health / exposure findings rather than hazard mechanisms (hazard !=
  exposure != risk); the grouping run and the human check will show how much mechanism evidence remains.
