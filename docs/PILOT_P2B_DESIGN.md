# Pilot P2b --- grouping, synthesis, packets, post-checks and shortlist (design)

**Status.** P2b-prep built on `work/meeting-2026-10-22` (D-046, D-047, D-048; authorized by D-041 and the
COORDINATOR rulings of 2026-11-01); **P2b-fix** (D-047a, D-049, D-050, DR-SEED-RANK-2; section 8) amends the
geography, the grouping agent (v2) and the packets, and fixes the ten pilot seeds. **No model call has been made; no
item exists.** The two agents below
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

## 2. Grouping agent --- `scripts/litcollect/litgroup_agent.py` v1 (v2 since P2b-fix: section 8; v3: section 9)

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

*Superseded by DR-SEED-RANK-2 (section 8) for the packets; kept as the P2b-prep record.* **Groups in a packet**
(EXECUTOR choice, for confirmation): >= 1 member geography-relevant to the pattern
(D-047); type mechanism / driver / consensus / caveat (schema v2 has no `pattern` literature type); strength over
the relevant members not `background_only` (schema v2 has no such strength); only relevant members carried and
the strength recomputed over them; ranked by strength, named-place members, size; at most 10 mechanism / driver /
consensus groups and 4 caveat groups (scenario-naming first). A level-1 packet carries no group.

**Numbers** (EXECUTOR): a value is shown to one decimal place, half up; allowed are that form, the nearest integer
and the exact stored string, plus the threshold, the horizon years, the robustness counts, the tercile's number of
states and the ranks.

## 4. Synthesis agent --- `scripts/litcollect/litsynth_agent.py` v1 (v2: section 9)

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

1. **Grouping run** (agent v3; run 1 at v2 superseded, section 9). From the Eagle execution clone at the pinned commit; output under the litcollect
   root (`LITCOLLECT_ROOT_POLARIS`, config key `litcollect_root_polaris`), never in the clone:
   ```
   bash "$CLIMRR_REPO_ROOT/scripts/sophia_pull_pinned.sh" <PINNED_SHA>
   cd "$CLIMRR_REPO_ROOT" && python -c "import yaml, duckdb"
   python scripts/litcollect/litgroup_agent.py --partitions artifacts/litgroups/partitions_v1.jsonl \
       --out "$LITCOLLECT_ROOT_POLARIS/litgroups/run2" \
       --base-url https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1 \
       --model openai/gpt-oss-120b --reasoning-effort low --max-tokens 16000 --chunk-size 40 \
       --sleep 5 --source-commit <PINNED_SHA>
   ```
   Deliver `litgroups/run2` (groups.jsonl, summary.json, agent.log, per-chunk files) as a tarball.
2. **Ingest and human check of the groups** (a following package): verify the tarball, freeze `groups.jsonl`, review
   labels and merges (including across chunks of one partition); a failed chunk is re-run with `--only <chunk_id>`.
3. **Kaiyuan selects 10 of the 20 shortlisted seeds** --- done: `pilot_selection_v1.yaml` (D-050).
4. **Packets** (local): `python scripts/build_synth_packets.py --groups <groups.jsonl>` (the selection is the
   default `--selection`); commit and push the packets.
5. **Synthesis run.** From the Eagle execution clone at the commit carrying the packets:
   ```
   bash "$CLIMRR_REPO_ROOT/scripts/sophia_pull_pinned.sh" <PINNED_SHA>
   cd "$CLIMRR_REPO_ROOT"
   python scripts/litcollect/litsynth_agent.py --packets artifacts/benchmark/synth_packets \
       --out "$LITCOLLECT_ROOT_POLARIS/litsynth/run1" \
       --base-url https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1 \
       --model openai/gpt-oss-120b --reasoning-effort low --max-tokens 16000 \
       --sleep 5 --source-commit <PINNED_SHA>
   ```
6. **Ingest, review workbook** (a following package): items with their post-check reasons go to Kaiyuan, then the
   mentor (D-041 condition F).

## 7. Open points for the COORDINATOR

- `deterministic_fail` vs schema v2's `rejected_pre_review` (section 4).
- The EXECUTOR choices in D-048 (seed rank, levels with 1 always applicable), section 3 (packet groups, rounding) and
  section 5 (fill order, control cell, regional contrasts uncapped).
- ~~D-047 as written drops 50 U.S.-wide statements~~ --- answered by D-047a (all 50 recovered; section 8).
- Most named-place heat-index statements are health / exposure findings rather than hazard mechanisms (hazard !=
  exposure != risk); the grouping run and the human check will show how much mechanism evidence remains.

## 8. P2b-fix (2026-11-01, second set of COORDINATOR rulings)

- **Geography v2 (D-047a).** `litgeo` v2 (default; v1 kept byte-for-byte for the frozen P2b-prep artifacts). A
  string naming the United States (United States, U.S., US, USA, contiguous / continental / conterminous United
  States, CONUS, lower 48) is U.S.-wide **regardless of scope**: with a directional or regional qualifier ->
  **`us_subregion`** (qualifier recorded, no mapping to states), else `us_national`. Under a subnational / local
  scope a state / NCA5 name still wins. `us_subregion` is relevant to every U.S. pattern, ranked below `state` /
  `nca_region`, above `us_national`. Inspection file `artifacts/litstatements/run2/region_strings_v2.csv` (+
  `_summary.json`): 747 statements --- us_national 81, **us_subregion 46**, state 119, nca 5, global 118, other 178,
  unknown 200; **all 50 D-047 drops recovered** (13 us_national, 37 us_subregion); 9 statements that were
  us_national ("western United States" under a continental / national scope, "Western U.S.", "southern United
  States", "western US") are now us_subregion.
- **Grouping agent v2 (D-049).** Every group and singleton carries `claim_about` (hazard_change_mechanism,
  hazard_definition_or_measurement, impact_or_exposure, method_or_data, other), defined one line each in the prompt;
  singletons are `{id, claim_about}`; a value outside the enum fails that record (kept, flagged). Template
  `ac135f00570d75f487c7bd414a662a18c271861afa5f026e3e17b3c4fb752ae7`; filled: heat
  `2c4a1dd0fa2c89db0096878f01c0be02e0e731df5f99f6580bdb4cb9356df311`, fire
  `1134a3083df2cd7d340d741b93e598455b8799c839389b3f9b1f634c54e4b7c7`. Code never infers the claim type.
- **Packets v2 (DR-SEED-RANK-2).** Relevance is recomputed per pattern under geography v2 (the seed file's v1
  relevance is kept as `n_relevant_statements_seed_file_v1`). Mechanism / driver / consensus groups:
  `hazard_change_mechanism` -> driver (<= 10), `hazard_definition_or_measurement` -> context (<= 4), the rest
  excluded; caveat groups only at rung 7 (<= 4, scenario-naming first). Order: relevance class, claim type, strength,
  more canonical papers, group id. Every excluded candidate is in `excluded_groups` with its reason (claim type,
  caveat outside rung 7, over the cap). Members carry `region_class` and the `region_qualifier`; the model view shows
  each group's `role` and `claim_about` and a member's qualifier.
- **Pilot selection (D-050).** `data/metadata/benchmark/pilot_selection_v1.yaml` (manifest-pinned): Kaiyuan's ten
  seeds in order with rungs (1, 1, 3, 3, 3, 3, 4, 4, 4, 7) and the nine exclusions with reasons;
  `build_synth_packets.py --selection` builds exactly these ten, item ids `BI-P2B-0001..0010`.
- **Open points.** (a) SD2-TP1-00017 is on the shortlist but neither selected nor excluded with a reason. (b) Level-1
  packets still carry no group (the work package's "rungs 1--7" is read as the filter for the rungs that carry
  literature). (c) Caveat groups at rung 7 are not filtered by `claim_about`. (d) A `us_subregion` statement is
  relevant to every U.S. pattern by the ruling, so "western United States" statements rank above U.S.-national ones
  for Georgia or Alabama. (e) "Houston, TX, USA" is `us_national` (a city is not a directional / regional
  qualifier). (f) "North America" stays scope-gated (D-047): it does not name the United States.

## 9. Grouping run 1 and the v3 agents (D-051, 2026-11-01)

- **Run 1 outcome** (`litgroup_agent` v2; Sophia vLLM, `openai/gpt-oss-120b`, 2026-11-02 00:48 UTC,
  `litgroups/run1`): 11 partitions, **2 pass, 9 fail**. Every partition of >= 46 statements (116, 118, 74, 65, 102,
  106, 66, 46) ended `finish_reason=length` with no content and >= 20,000 characters of reasoning: the `max_tokens` cap of 6,000
  went to reasoning. The 28-statement partition finished (`stop`) and failed `ids_exactly_once_pass`. The 11- and
  15-statement partitions passed. **Superseded (budget)**; the output stays on Eagle as evidence and is not ingested.
- **`litgroup_agent` v3** (`e094aa5c…45f4`): `--reasoning-effort` (default low) sent as `reasoning_effort`, retried
  once without it on HTTP 400 (`reasoning_effort_applied: false`); `--max-tokens` default 16000; `--chunk-size`
  default 40 --- members ordered by region class (state, nca, us_subregion, us_national, global, other, unknown), then
  statement id, cut into near-equal consecutive chunks `<partition>.c<k>`, one call each; group ids
  `LG-<arm>-<type>-c<k>-<nnn>`. At 40 the 11 partitions give **23 chunks** (sizes 28 | 39 39 38 | 40 39 39 | 15 |
  37 37 | 33 32 | 34 34 34 | 36 35 35 | 11 | 33 33 | 23 23). One corrective turn when a parsed reply fails
  `ids_exactly_once_pass` (missing and repeated ids named); a reply that does not parse is not retried. Every record
  carries the budget, `model_attempts`, `corrective_retry_used`, `finish_reason`, `content_chars`, `reasoning_chars`.
  System prompt unchanged.
- **`litsynth_agent` v2** (`a40909ef…cc21`): the same budget flags; one corrective turn on a parse failure only (an
  item that fails the post-checks is not retried). System prompt unchanged.
- **Limitations.** No merge across chunks by code: a claim split over two chunks gives two groups, which the
  reviewer may merge; a code merge pass would be a separate decision. Chunk order uses the partitions' stored region
  class (geography v1).

## 10. Grouping run 2, ingest and packets (P2b-ingest, D-052, 2026-11-02)

- **Run-2 outcome** (`litgroup_agent` v3 `e094aa5c…d845f4`; template `ac135f00…2ae7`; corrective template
  `5d052853…54b6`; `reasoning_effort=low`, `max_tokens=16000`, `chunk_size=40`, temperature 0; Sophia vLLM
  `openai/gpt-oss-120b` on all 23 chunks; source commit `7676e53`; 2026-11-02 01:17--06:10 UTC). Tarball
  `litgroups_run2_evidence.tar.gz` `a90ad7f0…2eb`; `groups.jsonl` `fc5ceea5…b4ce`; `summary.json` `0253c687…c5`.
  11 partitions, **23 chunks, 23 pass, 0 fail**, every `finish_reason=stop`. **Corrective turns 15**: 12 chunks passed
  on the first invocation; **3 passed on a second attempt with identical configuration** (same prompt hash, local
  ids, budget, endpoint, templates, source commit): `extreme_heat_v1.driver.c1`, `extreme_heat_v1.driver.c2`,
  `fire_weather_v1.mechanism.c2`, each first failing `ids_exactly_once_pass` after its corrective turn (missing /
  duplicate / unknown ids 1 / 32 / 0, 1 / 0 / 0, 2 / 0 / 0), kept as `chunks/<id>.failed_attempt1.json`. **239 groups,
  155 singletons, 747 statements each exactly once**; 0 label-digit fails, 0 `claim_about` fails. Run 1 (agent v2)
  superseded (budget, D-051), recorded only.
- **Ingest** (`scripts/ingest_litgroups.py`, `src/climrr/litgroups_run2.py`) -> `artifacts/litgroups/run2/`: the run
  files, both logs (`agent.log` = `litgroups_run2.log`), 23 chunk results + 3 failed first attempts; prompts and raw
  responses hashed in `manifest.json` (76 files), not copied. `groups_enriched.jsonl`: every record with its members
  resolved through the partition's local ids to `LS-` ids (paper, canonical paper, evidence role, passage type,
  region, **geography v2** class and qualifier, statement), `n_papers`, `n_independent_papers` (D-046, all members),
  `evidence_strength` recomputed (D-045 / D-048) and equal to the agent's for all 394, `claim_about` (the agent's),
  `region_classes`, `partition`, `chunk`, `is_singleton`. **105 of the 239 groups have one member** (the model returned
  a labelled one-member group; the agent's `single_member` check is recorded, not gating): 134 groups have >= 2
  members. `is_singleton` follows the agent's `kind`.
- **Groups (>= 1 member, `kind: group`) by arm x claim_about x strength** (multi / review / single / background):

  | arm | hazard_change_mechanism | hazard_definition_or_measurement | impact_or_exposure | method_or_data | other |
  | --- | --- | --- | --- | --- | --- |
  | extreme heat | 15 / 0 / 17 / 4 | 6 / 1 / 15 / 9 | 15 / 3 / 32 / 3 | 8 / 2 / 10 / 5 | 0 / 1 / 3 / 2 |
  | fire weather | 20 / 0 / 22 / 3 | 10 / 0 / 9 / 7 | 1 / 0 / 3 / 0 | 4 / 0 / 7 / 2 | --- |

  Multi-source `hazard_change_mechanism` groups: **heat 15, fire weather 20**. The largest group
  (`LG-extreme_heat_v1-mechanism-c1-021`, "heat index combines temperature and humidity as a perceived‑heat metric",
  14 papers) is a definition; of the ten largest, two are mechanism groups.
- **Packets** (`scripts/build_synth_packets.py --groups artifacts/litgroups/run2/groups_enriched.jsonl`, the selection
  `pilot_selection_v1.yaml`; synthpackets v2, DR-SEED-RANK-2): ten packets `PK-<seed_id>.json`, item ids
  `BI-P2B-0001..0010`, and `manifest.json` (each packet's SHA-256). *The work package named the files
  `BI-P2B-<nnnn>.json`; `litsynth_agent.py` v2 (pinned byte-identical) reads `PK-*.json`, so the file names are kept
  and the item id is inside each packet and in the manifest.* Rung 1 (0001, 0002): no group. Rungs 3 / 4 / 7: 10
  mechanism (driver) + 4 definition (context) groups each, and 4 caveat groups at rung 7 (0010); 4--5 multi-source
  per packet; 40--47 excluded with reasons.
- **Review workbook** (`scripts/build_p2b_groups_review.py`, `src/climrr/p2b_review.py`):
  `artifacts/benchmark/review/P2b_groups_v1.xlsx` (gitignored; OVERVIEW, GROUPS 239, SINGLETONS 155, PACKETS 116
  attachments, Legend) and the tracked `P2b_groups_v1.csv` (GROUPS). Reviewer columns `kaiyuan_disposition`
  (accept_group / split / merge_with / mislabelled_claim_about / reject) and `note` on GROUPS and SINGLETONS.
  Cross-chunk merging is deferred to this review (D-052).
- **Flagged for the reviewer.** (a) The heat-index packets' top drivers include fire statements from the heat arm
  tagged `hazard_change_mechanism` ("Prolonged heat increases fire or wildfire risk", `LG-extreme_heat_v1-driver-c1-007`;
  a Rocky Mountains large-fire experiment, `…-driver-c2-011`; "drought and high temperatures increase wildfire risk",
  `…-driver-c2-004`), and building / indoor-temperature singletons: candidates for `mislabelled_claim_about` or
  `reject`. (b) Relevance class ranks first (DR-SEED-RANK-2), so single-source `us_subregion` statements ("western
  US", "northern and central US Rocky Mountains", "southeastern United States") rank above U.S.-national multi-source
  groups even for New York and Northeast patterns (open point 8d, now visible). (c) Packets 0004--0010 carry nearly
  the same driver set: the literature varies little by seed. (d) `n_papers` counts background members: the second-
  largest group has 12 papers and is `single_source_supported`.

## 11. Final prep: dispositions, DR-SEED-RANK-3, DR-DESC-1, synthesis agent v3 (P2b-final-prep, D-053--D-055, 2026-11-02)

- **Synthesis run 0 (smoke test; superseded by agent v3).** Polaris `litsynth/run0_rung1`, synthesis agent v2, Sophia
  `gpt-oss-120b`, `reasoning_effort=low`, 2026-11-02 18:13 UTC: 2 rung-1 items, **both `rejected_pre_review`**. The only
  failing check was `numbers_untraced`: the model wrote rounded values not in the packet ("15", "44", "40"; "12", "8")
  and other values as number-words ("sixteen", "forty-five", "twenty-four"), which post-checks v1 did not detect.
  Prompt leakage passed on both; schema valid. Not ingested; recorded here only.
- **Dispositions (D-053).** `data/metadata/benchmark/group_dispositions_v1.csv` --- the COORDINATOR proposal
  `P2b_groups_dispositions_proposed_v1.csv`, confirmed by Kaiyuan 2026-11-02 as proposed, copied byte-identical
  (SHA-256 `71f07777…3d40b82`, CRLF as received; manifest-pinned). 107 heat-arm groups: accept 44,
  exclude_from_rung7 40, not_about_family 11, relabel 7 (impact_or_exposure 3, method_or_data 2,
  hazard_change_mechanism 1, hazard_definition_or_measurement 1), reject 3, merge_with 2 (both into
  `LG-extreme_heat_v1-mechanism-c1-021`). Kaiyuan's column is empty everywhere (0 overrides).
  `litgroups.apply_dispositions` applies them when the packets are built (`groups_enriched.jsonl` is unchanged):
  relabel -> `claim_about` replaced, `claim_about_source: reviewer`; not_about_family / reject -> excluded from every
  packet of the arm (`excluded_groups` reason `disposition:<kind>`); merge_with -> members unioned into the target,
  strength and paper counts recomputed (D-045 / D-046; `merged_from`, `evidence_strength_before_merge`), the source
  excluded as `merged_into:<target>`; exclude_from_rung7 -> excluded from caveat slots. Fire-arm groups untouched.
  **Not in the file:** 44 of the 151 heat-arm groups and every singleton (unchanged). No unlisted *group* reaches a
  packet; three heat singletons do (below).
- **DR-SEED-RANK-3 and the caveat filter (D-054).** Caveat slots accept only `claim_about` in {hazard_change_mechanism,
  hazard_definition_or_measurement} (excluded otherwise as `caveat_claim_about:<x>`). Order within every role:
  (1) place-named (a relevant member's basis is the seed's state or NCA region) first; (2) strength (multi > review >
  single); (3) relevance class (us_subregion > us_national > global); (4) canonical papers; (5) group id. The
  scenario-naming priority for caveats (v2) and the claim-type tier are dropped: the work package's order is complete.
- **Descriptors (DR-DESC-1, D-055).** `src/climrr/pattern_descriptors.py`, rules `descriptor_rules_v1.yaml`
  (SHA-256 `5c2090a7…934650`, manifest-pinned). Each packet pattern carries `allowed_descriptors`; their phrases are
  `checks_input.allowed_descriptors` and their digits join the allowed numbers (scenario names stripped, so "RCP8.5"
  adds no "8" or "5"); `checks_input.exact_values` lists the decimal forms of the pattern values (provenance only).
  EXECUTOR details, recorded for confirmation: class intervals `[lower, upper)`, 3.5 in "roughly tripling"; no class for
  a decrease (the work package's "a slight decrease" would cover every decrease); the low-baseline "<class>" read as
  the future anchor ("from rare or no such days to about 11 days"); anchors by Python `round()` as named (half-even at
  an exact .5); a regional contrast stores no baseline mean, so it has ranking words but no magnitude class or anchors;
  "about 0 days" can occur (Washington 105 °F, Alaska example) and is listed as written.
- **Synthesis agent v3** (`litsynth_agent.py` SHA-256 `d582c008…4dac`; system prompt `d5805e5d…0272`; corrective prompt
  unchanged). Pattern-level reference and rubric in the packet's descriptors; exact values only in
  `reference_components` (attached by code); any number copied as digits from the descriptors or pattern values; no
  number-words outside a copied descriptor; no rounding, ratio or range of the model's own; quantity named in general
  words with its threshold; required points = direction, magnitude class, region, mechanism (where groups exist),
  scenario / horizon handling, no-overclaim; numbers only as optional points; single-source hedged and tagged; no
  horizon years the packet does not state. Corrective retry: parse failure only (unchanged).
- **Post-checks v2** (`benchmark_items.synthesis_post_checks`): numbers traced in the prompt as well as the reference
  answer and rubric, against pattern values and descriptor digits; number-words (one ... ninety-nine, hundred,
  thousand, "-fold", twice, double, triple, half, with inflections) must lie inside an allowed descriptor phrase ("one
  study / paper / analysis" and "one high-emissions scenario" exempt); `exact_value_in_graded_text` for any exact
  pattern value with a decimal in the reference answer or rubric; leakage and group-id checks kept.
- **Packets v3** (synthpackets v3; `manifest.json` records the disposition counts, merges, relabels and the groups
  without a disposition). Rung 1 (0001, 0002): no group. Attached groups and the top three labels:

  | item | seed | rung | groups (driver / context / caveat) | top three labels |
  | --- | --- | --- | --- | --- |
  | 0003 | SD2-TP1-00071 California | 3 | 14 (10 / 4 / 0) | Observed increase in heat‑wave and drought frequency; Indoor temperature rises faster when ambient temperature is higher …; global warming increases heatwave frequency and intensity |
  | 0004 | SD2-TP1-00271 New York | 3 | 12 (9 / 3 / 0) | Observed increase in heat‑wave and drought frequency; global warming increases heatwave frequency and intensity; urban heat island intensifies due to nighttime conditions and reduced moisture |
  | 0005 | SD2-TP1-00460 Washington | 3 | 12 (9 / 3 / 0) | as 0004 |
  | 0006 | SD2-TP1-00589 Alabama | 3 | 12 (9 / 3 / 0) | as 0004 |
  | 0007--0009 | SD2-TP1-02785 / 02787 / 02789 NCA5 regions | 4 | 12 (9 / 3 / 0) | as 0004 |
  | 0010 | SD2-TP1-00075 Florida | 7 | 14 (9 / 3 / 2) | as 0004 |

  Rung-7 caveats (0010): `LG-extreme_heat_v1-caveat-c1-026` (review_supported) and `…-caveat-c1-024`
  (single_source_supported), both hazard_definition_or_measurement.
- **Flagged.** (a) Three heat singletons are attached with no disposition (singletons were not in the file):
  `LG-extreme_heat_v1-driver-c2-011` (a dew-point reduction experiment with runoff and fire wording; in eight packets),
  `…-mechanism-c1-020` (minimum temperature and overnight cooling; eight packets) and `…-mechanism-c1-010` (indoor
  temperature of a building; 0003, second). (b) Packets 0004--0010 still share nearly one driver set. (c) The rung-7
  caveat `…-caveat-c1-024` label carries "80 °F", which is not an allowed number: copied, it fails post-checks v2.
