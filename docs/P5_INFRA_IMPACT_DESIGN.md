# P5 --- hazard -> infrastructure impact items: design (work package P5a, 2026-11-23)

Follows the group meeting of 2026-11-23 (mentor, Alvi, JL; `MENTOR_BRIEF.md`) and D-069 -- D-073. P5a built the tools
and rules below with **no model call**; the runs are on Polaris (§6), then sample QAs go to Alvi. Successor of
`PILOT_P2B_DESIGN.md` for this line of work (that file stays the record of the P2b / P3 pilots).

## 1. Pipeline

The P1 -- P3 workflow (table concepts -> queries -> papers -> per-paper extraction -> grouping -> packets -> synthesis ->
polish -> review), applied to LITCORPUS-03 (`LITCORPUS03_PROVENANCE.md`):

1. transfer, verify, **inventory** (`scripts/litcollect/inventory_corpus.py`; v1 done 2026-11-24, `LITCORPUS03_PROVENANCE.md`
   §4; v1.1 adds the per-paper sector tags, D-070a), **index** (`build_index.py`);
2. **lexicon query** (`run_query.py` v4.1 `--lexicon --rule DR-CAND-INFRA-2`): per paper and hazard family, the hazard
   sections (governed and proxy terms, D-073a), the sections with an asset term, the sector tags and `in_186k_set`
   (`paper_hits.jsonl`);
3. **candidates** `DR-CAND-INFRA-3` (§3b; INFRA-2 §3a ran as the v2 diagnostic) -> `candidates.json`; the extraction reads it on Eagle
   (§6); shipped back afterwards, hash pinned on ingest and re-derived by `climrr.infra_lexicon.verify_candidates_3`;
4. **extraction** (`litstatement_agent.py` v4.1 `--arm infra_impact_v1`; statement type `impact`, D-073; `hazard_relation`,
   D-073a);
5. **grouping** (`litgroup_agent.py` v3.1 over `partitions_infra_v1.jsonl`, §8; run and ingested, §11), **review list**
   (§12), **rung-8 seeds and selection** (DR-SEED-INFRA-1, §9, §13), **rung-8 packets** (§14, provisional), synthesis
   (`litsynth_agent.py` v5.2, post-checks v3.3, §9), polish;
6. sample QAs for Alvi.

## 2. Infrastructure vocabulary (`data/metadata/litstatements/infrastructure_lexicon_v1.yaml`)

Asset classes = the 16 CISA critical-infrastructure sectors (names verbatim from the CISA sector list, read 2026-11-23);
119 whole-word surface forms (20 verbatim from five CISA sector pages, `source: CISA sector list`; 99
`source: EXECUTOR (common usage)`, `authorization: our_reading`); 15 impact terms (EXECUTOR). It classifies literature
only and never touches the table. Notes: "power plant" also matches inside "nuclear power plant" (both classes recorded);
the pipeline forms sit under `transportation_systems` (CISA's "Pipeline Systems" subsector), not under water as the work
package's example list had them; "oil", "satellite", "wireless" (CISA phrases) are excluded as too generic.

## 3. Candidate rule DR-CAND-INFRA-1

Hazard families = the governed concept-map terms, as before: the LITCORPUS-02 topical-only query files
(`artifacts/literature/litcorpus02/evidence/queries/*_diag_topical_only_query.txt`), with R-FWI-1 for the bare `fwi` (a
section's bare-`fwi` hit counts only when "fire weather" / "fire-weather" occurs in the same document). Per family: papers
with >= 1 section containing a hazard term of the family and an asset form; ranked by the number of such sections
(descending; ties by paper id in code-point order); the top 300 per family for the pilot extraction; the full distribution
is reported (`by_family.distribution_n_cooc_sections`). A paper in both families is listed once, with both ranks.

**Expected yield risk (for the COORDINATOR).** Infrastructure papers mostly write "extreme heat", "heat wave" or
"wildfire", rarely "heat index" or "Fire Weather Index". The governed terms will find few co-occurrences; widening the
hazard vocabulary is a scientific decision (an FWI is never fire occurrence; "extreme heat" is not the heat index), not
taken here. The query reports the counts that decision needs. *(Decided in the P5a hotfix: D-073a, §3a.)*

## 3a. Candidate rule DR-CAND-INFRA-2 (P5a hotfix; D-070a, D-073a) --- ran as the v2 diagnostic; superseded for the pilot by §3b

DR-CAND-INFRA-1 stays available (`--rule DR-CAND-INFRA-1`, the default; unchanged); the pilot uses INFRA-2.

- **Hazard terms per family** = the governed terms (the topical-only query files, R-FWI-1 as above) **plus** the broader
  hazard terms of `data/metadata/litstatements/hazard_proxy_lexicon_v1.yaml` (heat_index: extreme heat, heat wave(s),
  heatwave(s), high temperatures, hot days, humid heat; fire_weather_index: fire weather, fire danger, fire-weather,
  wildfire(s), wildland fire), relation `broader_hazard`, literature classification only, never table matching.
- **Sector tag** = `asset_sector_tag` from `_araiadoc_tags.critical_infrastructure.sectors[]` (JL's pipeline, `origin:
  external_model (JL pipeline)`), read from the inventory v1.1 per-paper file (the index does not hold the tags).
- A section **qualifies** for a family when it holds a hazard term of the family and (a) an asset form of the lexicon, or
  (b) the paper carries a sector tag. Basis `a` when the paper has a section of kind (a), else `b`.
- **Rank**: number of qualifying sections (descending), then basis a before b, then paper id. Top 300 per family. Reported:
  the distribution by count, by basis, by hazard relation (`governed_term` when a qualifying section holds a governed
  term, else `broader_hazard`) and in / not in the 186k set (`in_186k_set`).
- **Reading (for confirmation).** On LITCORPUS-03 almost every paper may carry a sector tag, so basis (b) admits nearly
  every paper with a hazard term, and the rank is then close to "number of hazard sections". The query's distribution
  shows how far that is so before the extraction run.

## 3b. v2 diagnostic and candidate rule DR-CAND-INFRA-3 (P5a hotfix 2; D-070b) --- the pilot's rule

**v2 diagnostic** (Polaris, `runs/infra_lexicon_v2`, 2026-11-24 04:30 UTC, run_query v4.1, DR-CAND-INFRA-2; relayed by
Kaiyuan): 89,497 docs; heat_index admitted 3,107 (39 governed-term, 3,068 proxy-only; "high temperatures" alone in 2,520
docs); fire_weather_index admitted 432 (10 governed-term); 588 candidates (heat basis a 248 / b 52; fire a 283 / b 17);
among the heat candidates 216 of 346 rest **only** on "high temperatures" (e.g. doc 100020824, section "integrated cpo and
pko processes" + "electricity"); `impact: true` on 411 of 588; the qualifying sections are mostly introductions.
**DR-CAND-INFRA-3** (`run_query.py` v4.2 `--rule DR-CAND-INFRA-3`; INFRA-1 / INFRA-2 unchanged, v4.1 held at `9890a00`):
"high temperatures" is a conditional proxy --- it counts in a section only with a term of `climate_coterms_v1` (climate,
climate change, warming, global warming, weather, summer, heat wave(s), heatwave(s), extreme heat, projected, projection(s);
plurals written out for the no-stemming matcher) in the same section (`hazard_proxy_lexicon_v1a.yaml`, v1 otherwise
unchanged); basis (a) only (a hazard term and an asset form in the same section), the tagged papers with a hazard section
but none qualifying go to `basis_b_only.json`, not candidates; rank `impact` true (an impact term anywhere in the paper)
first, then the number of qualifying sections, then governed-term before broader-hazard, then paper id; cap 300 per family,
a paper may be a candidate for both; `candidates.json` keeps the v4.1 shape (`basis` always a) plus `impact` and a `report`
per family (admitted and qualifying before / after the conditional rule; candidates; at each level governed-term,
`impact` true and in the 186k set; basis-b-only; sections dropped by the rule); re-derived by
`climrr.infra_lexicon.verify_candidates_3`.

## 4. Item type (rung 8, D-071) and the wording rule

Table pattern (hazard change at a place) + `impact` statements (hazard condition -> asset class -> mechanism / outcome) +
general drivers where available. The answer states the hazard change as projected, the impact pathway as what research
shows about such conditions, and never that a specific asset at the place will fail. Scope marking applies with extra
force: impact statements are almost always general, so most rung-8 answers will close with the general clause. Question
form QF-08: "What does a projected <change> in <hazard phrase> in <Place> <horizon> mean for <asset class>, and why?"

## 5. Scope rule and question forms (D-069, D-069a; packets v5 -> v5a, synthesis prompt v5.1, post-checks v3.2)

**P5a hotfix (D-069a).** The scope class of a group is now the **majority** class among its cited members (a tie -> `mixed`,
"In general, research"); cited members of a more specific place class (state / NCA) become the optional clause
", including work on <Place>" ("In general, research, including work on California, shows"). Packets v5a
(`artifacts/benchmark/synth_packets_v5a/`, manifest `changes_from_v5`): 11 group attachments change on the seven seeds
(the 5 minority cases and 6 others); BI-P3-0005 now needs the closing clause. Packets v5a also carry plain language v1b
(`broader_hazard_phrase`, D-073a). The text below describes v5; where it says "most specific", v5a reads "majority".


- **Scope.** Per group, the most specific geography class among its cited members (core / cited candidates and review
  passages; litgeo v2 basis, else the member's region class) -> "Research on <State>", "Research on the <Region>",
  "Research on the United States", "In general, research", + "shows" / "has shown" (multi-source or review) or "suggests"
  (single-source). Every literature sentence opens with its phrase; when no cited group is state- or NCA-specific, the
  literature part and the paragraph end with "These are general drivers of <quantity_short>, not findings specific to
  <Place>."; no required rubric point names the place on a group's authority; a place-specific group earns an optional
  point. Post-checks v3.2 fail (format-class) on each; `mixed_scope_report` lists sentences citing groups of different
  scope.
- **Question forms** (`data/metadata/benchmark/question_forms_v1.yaml`): eight forms, one per item by code (round-robin in
  selection order within the rung, over the forms that admit the item's rung, pattern kind and direction); prompt v5
  requires the form; v3.2 checks the opening and the number of question marks. Diversity report: at most 30 % of a batch
  with the same opening trigram. On the seven sample seeds: QF-01, 02, 03, 05 (heat), QF-04 (regions), QF-06, 07 (fire);
  the assigned skeletons pass (largest share 14 %); the run-5 questions would not (43 % "how are dangerous").
- **Not changed:** descriptor rules v4, plain language v1a, the polish agent v1.1 and polish checks v2. **Gap:** polish
  checks v2 do not require the scope phrases or the closing clause to survive a rewrite (the hedge-scope loss of P3c flag
  EX-1 is the same kind of fault); a checks v2.1 rule is needed before the next polish run.

## 6. Polaris plan (Kaiyuan; env as before: `module load conda/2026-10-01`, `conda activate globus_env`)

**Done (2026-11-24):** transfer, extraction and the v1 inventory (`LITCORPUS03_PROVENANCE.md` §4); the v2 query (§3b). **v2 plan**, at the pushed
commit `<PINNED_SHA>` that carries the P5a hotfix; the litcollect root in `$LITCOLLECT_ROOT_POLARIS`; first check the
environment: `python -c "import yaml, duckdb; print(duckdb.__version__)"` (DuckDB 1.5.4).

    bash "$CLIMRR_REPO_ROOT/scripts/sophia_pull_pinned.sh" <PINNED_SHA>
    cd "$CLIMRR_REPO_ROOT"
    L="$LITCOLLECT_ROOT_POLARIS"; SRC="$L/sources/critical_infrastructure_v1"
    # 1. inventory v1.1: the same figures as v1 plus the sector tags and their mapping; the per-paper tag file
    #    (new output names: the tool refuses to overwrite the v1 output)
    python scripts/litcollect/inventory_corpus.py --root "$SRC/kept" --out "$L/inventory/litcorpus03_inventory_v11.json" \
        --corpus-id LITCORPUS-03 --compare-ids "$L/index/full_705k_v2_filtered/manifest.csv" \
        --compare-label LITCORPUS-02-source-186k --tags-out "$L/inventory/litcorpus03_sector_tags_v11.jsonl"
    # -> stop if files != 89,497 or the content identity != 2dfc8eca...f725 (the v1 run)
    # 2. index (skip if done; its content identity must equal 2dfc8eca...f725)
    python scripts/litcollect/build_index.py --root "$SRC/kept" --out "$L/index/critical_infrastructure_v1"
    # 3. lexicon query and candidates (DR-CAND-INFRA-2, cap 300 per family)
    python scripts/litcollect/run_query.py --index "$L/index/critical_infrastructure_v1" \
        --out "$L/runs/infra_lexicon_v2" --name infra_lexicon_v2 \
        --lexicon data/metadata/litstatements/infrastructure_lexicon_v1.yaml \
        --rule DR-CAND-INFRA-2 --proxy-lexicon data/metadata/litstatements/hazard_proxy_lexicon_v1.yaml \
        --sector-tags "$L/inventory/litcorpus03_sector_tags_v11.jsonl" \
        --in-set-ids "$L/index/full_705k_v2_filtered/manifest.csv" --in-set-label LITCORPUS-02-source-186k \
        --family heat_index=artifacts/literature/litcorpus02/evidence/queries/extreme_heat_diag_topical_only_query.txt \
        --family fire_weather_index=artifacts/literature/litcorpus02/evidence/queries/fire_weather_diag_topical_only_query.txt \
        --family-disambiguate 'fire_weather_index:fwi=fire weather|fire-weather' --cap 300

**Next (P5a hotfix 2), at the pushed commit `<PINNED_SHA>` that carries DR-CAND-INFRA-3** (inventory, index and the
tag file as done for v2):

    python scripts/litcollect/run_query.py --index "$L/index/critical_infrastructure_v1" \
        --out "$L/runs/infra_lexicon_v3" --name infra_lexicon_v3 \
        --lexicon data/metadata/litstatements/infrastructure_lexicon_v1.yaml \
        --rule DR-CAND-INFRA-3 --proxy-lexicon data/metadata/litstatements/hazard_proxy_lexicon_v1a.yaml \
        --sector-tags "$L/inventory/litcorpus03_sector_tags_v11.jsonl" \
        --in-set-ids "$L/index/full_705k_v2_filtered/manifest.csv" --in-set-label LITCORPUS-02-source-186k \
        --family heat_index=artifacts/literature/litcorpus02/evidence/queries/extreme_heat_diag_topical_only_query.txt \
        --family fire_weather_index=artifacts/literature/litcorpus02/evidence/queries/fire_weather_diag_topical_only_query.txt \
        --family-disambiguate 'fire_weather_index:fwi=fire weather|fire-weather' --cap 300

Ship back `summary.json`, `candidates.json`, `paper_hits.jsonl` and `basis_b_only.json` (with SHA-256 of each). The infra
extraction (work package P5a hotfix 2) then reads that `candidates.json` directly:
`litstatement_agent.py --arm infra_impact_v1 --candidates "$L/runs/infra_lexicon_v3/candidates.json" --index
"$L/index/critical_infrastructure_v1" --out "$L/litstatements/infra_run1"` (Sophia `openai/gpt-oss-120b`, `--reasoning-effort
low --max-tokens 6000 --sleep 2 --source-commit <PINNED_SHA>`).

*(v2 plan, done 2026-11-24:)* Ship back: both inventory JSONs (v1 and v1.1; not the tag file, which stays on Eagle --- its SHA-256 is in the v1.1 JSON
and in `candidates.json`), the index's `index_summary.json` and `build.log`, and the query run's `summary.json`,
`candidates.json` and `paper_hits.jsonl` (with SHA-256 of each). The ingest checks the v1.1 inventory against the relayed v1
figures, pins `infra_candidates_v1.json` = `candidates.json` and re-derives it (`verify_candidates_2`). The extraction run
(`litstatement_agent.py --arm infra_impact_v1 --reasoning-effort low --max-tokens 6000`, invocation in the agent's
docstring) runs at the commit that carries the pinned candidates, after the COORDINATOR has seen the counts.

## 7. Infra run 1: run facts and ingest (work package P5b; D-074)

**Run** (Polaris, 2026-11-24 05:11 -- 06:15 UTC; Kaiyuan): `litstatement_agent.py` v4.1, arm `infra_impact_v1`, system prompt
`945b487c…e095` (the work package abbreviates it "…9095"; the full hash, recorded by every statement, the summary and the
log, is the hash of `SYSTEM_PROMPT_INFRA` in the agent at `157e49d`, tested), Sophia `openai/gpt-oss-120b`, reasoning low, max_tokens 6000, source commit `157e49d`, over the 572
DR-CAND-INFRA-3 candidates of `runs/infra_lexicon_v3`. Delivered `infra_run1_evidence.tar.gz` (`218a9a43…ad5a`).
**Reproduced on ingest** (`scripts/ingest_litstatements_infra1.py`, `climrr.litstatements_infra1.verify_source`; any
difference fails the ingest): 572 papers, 0 errors, 0 over limit, 31 truncated (`TRUNC`); 407 statements (impact 264, driver 79,
mechanism 38, pattern 14, caveat 5, consensus 5, background 2), 210 `deterministic_pass`, 197 rejected; 407 papers with no
statement (165 productive); recovery exact 213 / prefix_anchor 83 / normalized 30 / not_found 81; asset classes (all impact
statements) energy 120, transportation 49, water 24, healthcare 21, emergency 13, other 22, communications 6, food 3, dams 2,
commercial 2, transmission_systems 1, blank 1; hazard relation broader_hazard 242, governed_term 12, none 10. **The ten
without a relation** are all rejected before review; their hazard terms are outside both lexicons: "fire" (3: cable-gland
polymers above 300 °C, an optical-fibre fire alarm, Bluetooth attenuation in fire), "marine heat waves" (3: underwater data
centres), "fire hazard" (bridge fires), "low temperatures" (equipment failures in cold), "high wind loads" (utility poles),
and one blank.

**Query history (D-070a, D-070b).** v2 (`runs/infra_lexicon_v2`, run_query v4.1, DR-CAND-INFRA-2, 588 candidates) ran first
and was read as a diagnostic (§3b); v3 (`runs/infra_lexicon_v3`, run_query v4.2, DR-CAND-INFRA-3, 572 candidates, 28 in both
families) produced the candidates the run read. Both summaries are in `artifacts/literature/litcorpus03/runs/`; v3
`candidates.json` is pinned as `data/metadata/softqa/infra_candidates_v1.json` and re-derived on ingest from the delivered
`paper_hits.jsonl` and `basis_b_only.json` (`verify_candidates_3`); `paper_hits.jsonl` (both runs) and the v2 candidates are
recorded by hash only. The index summary, both query summaries and the index build log held an absolute Eagle path, which
the copies replace by a placeholder (both hashes in `redactions.json`). Corpus identity `2dfc8eca…f725` (inventory v1 and
v1.1, index), index manifest CSV `fc53ab3a…f42e`, 89,388 distinct SHA-256 among 89,497 files.

**Ingested** (`artifacts/litstatements/infra_run1/`): `statements_ingested.jsonl` (ids `LS3-<paper>-<nn>`, evidence roles as
run 2, `impact_candidate: true` on the 151 passing impact statements, `statement_family` and its basis), `independence_v2.json`
(D-046 over the 572 papers: one possible-duplicate title pair, 571 canonical papers), `breakdowns.json`, `manifest.json`.

**Passing statements by type x asset class x hazard family** (210): impact 151 --- heat 98 (energy 43, transportation 22,
healthcare 15, other 6, water 6, emergency 3, food 2, commercial 1), fire weather 53 (energy 21, transportation 13, water 7,
emergency 4, other 4, healthcare 2, communications 1, dams 1); driver 34; mechanism 13; pattern 8; consensus 3; caveat 1.
**Passing impact statements that name a U.S. place** (geography v2): 38 --- state 28, NCA5 region 2, U.S. subregion 1, U.S.
national 7. The other 113 are general (global, other countries, unknown).

## 8. Grouping partitions for the impact arm (D-075)

`artifacts/litgroups/partitions_infra_v1.jsonl` (`0d8f3229…9b50`; `scripts/build_group_partitions_infra.py`,
`climrr.litgroups_infra`): over the passing statements, **impact partitions** = hazard family x asset class, a class with < 8
statements (and the agent's `other`) merged into `other_assets`, `prompt_variant: impact_v1`; **driver / mechanism partitions**
by family and type, as before. Eleven partitions, 198 statements, 12 chunks of <= 40:

| partition | n | chunks |
| --- | ---: | ---: |
| infra_heat_index.impact.energy | 43 | 2 |
| infra_heat_index.impact.transportation_systems | 22 | 1 |
| infra_heat_index.impact.healthcare_and_public_health | 15 | 1 |
| infra_heat_index.impact.other_assets (water 6, other 6, emergency 3, food 2, commercial 1) | 18 | 1 |
| infra_heat_index.driver / .mechanism | 17 / 8 | 1 / 1 |
| infra_fire_weather_index.impact.energy | 21 | 1 |
| infra_fire_weather_index.impact.transportation_systems | 13 | 1 |
| infra_fire_weather_index.impact.other_assets (water 7, emergency 4, other 4, healthcare 2, communications 1, dams 1) | 19 | 1 |
| infra_fire_weather_index.driver / .mechanism | 17 / 5 | 1 / 1 |

Not partitioned: the 12 passing pattern / consensus / caveat statements. **Grouping agent v3.1**: the impact template
(`70018280…3925`) groups by the same hazard condition -> asset -> impact mechanism / outcome, adds `claim_about`
`hazard_impact_on_asset`, asks for a label naming the asset class and the impact; impact group records carry `asset_classes`,
`hazard_relations`, `impact_mechanisms`, `impact_outcomes` from `meta` (never sent). Partitions without a variant get the v3
template unchanged (`ac135f00…2ae7`). Filled system prompts: heat impact `1bd1f71e…b379`, fire impact `a98f67f5…81e5`, heat
driver / mechanism `4e6e4f1e…2212`, fire driver / mechanism `0c3997b6…9eaf`.

## 9. Pairing rule DR-SEED-INFRA-1, the rung-8 pilot selection and the wording rules (D-075; D-073b)

Implemented now, run after the grouping run is ingested (P5c): `climrr.seeds_infra`, `scripts/build_seeds_infra.py`.

- **Seed** = (table pattern for family F at state P, at `TABLE_SETTING`) + the impact groups of F for asset class A
  (`claim_about` `hazard_impact_on_asset`; a group is of class A when a passing member has class A) + the family's driver
  groups as a rung-3 packet attaches them (`synthpackets.packet_groups(3, ...)` over LITCORPUS-02 grouping run 2). Impact
  groups ranked by geography relevance (place_named: a member names P; us: an NCA5-region, U.S.-subregion, U.S.-national or
  other-state member; general), then strength, then independent papers; one seed per (pattern, asset class) with >= 1 impact
  group; seeds ranked by the best strength, then independent papers. A seed with no place-named group needs the closing
  clause (D-069).
- **Pilot selection** (8 cells): heat x {energy, transportation, water, healthcare}; fire weather x {energy, transportation,
  emergency services, communications}; each at the state with the largest table change among states named by a passing impact
  statement of that class (geography v2 state), else California; question forms QF-08 / QF-09 / QF-10 round-robin. On the
  ingest the candidate states are: heat energy {California, Virginia}, heat transportation {Arizona}, heat healthcare
  {Arizona}, fire energy {Arizona, California, Idaho, Nevada}, fire transportation {California, Montana}; heat water, fire
  emergency services and fire communications none (California). `TABLE_SETTING` (EXECUTOR default, for confirmation):
  days above 95 F / summer seasonal FWI, absolute change, mid-century.
- **Wording** (synthesis prompt v5.2 `0753023c…578a`; post-checks v3.3): (1) the hazard change at the place, projected (the
  table sentence, with scope); (2) "<scope phrase> that <hazard phrase> <impact mechanism> <asset class>", the broader-hazard
  phrase (`plain_language_v1b`) when an impact group rests on a broader hazard term, and the general closing clause when no
  cited group is place-specific; (3) never "<asset> in <Place> will fail / is at risk"; "For <asset class> in <Place>, this
  implies more exposure to <impact>" only with a cited place-named impact group; D-073b: "wildfire" only inside "conditions
  that favour wildfire". Question forms (`question_forms_v2.yaml`): QF-08 (v1), QF-09 "What could a <change> in <hazard phrase>
  mean for <asset class> in <Place>, and why?", QF-10 "Why does <hazard phrase> matter for <asset class>, and how is it
  projected to change in <Place>?".

## 10. Polaris: the infra grouping run (next)

At the pushed commit `<PINNED_SHA>` that carries `partitions_infra_v1.jsonl` and `litgroup_agent.py` v3.1 (env as in §6;
first `python -c "import yaml, duckdb"`):

    bash "$CLIMRR_REPO_ROOT/scripts/sophia_pull_pinned.sh" <PINNED_SHA>
    cd "$CLIMRR_REPO_ROOT"
    python scripts/litcollect/litgroup_agent.py \
        --partitions artifacts/litgroups/partitions_infra_v1.jsonl \
        --out "$LITCOLLECT_ROOT_POLARIS/litgroups/infra_run1" \
        --base-url https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1 \
        --model openai/gpt-oss-120b --reasoning-effort low --max-tokens 16000 --chunk-size 40 \
        --sleep 5 --source-commit <PINNED_SHA>

Expect 11 partitions, 12 chunks (`START ... partitions=11 chunks=12 ... template_impact_sha=70018280938b`). Ship back
`groups.jsonl`, `summary.json`, `agent.log` and every chunk directory (SHA-256 of each). Then P5c: ingest the groups, build the
seeds and the selection (`scripts/build_seeds_infra.py`), the rung-8 packets, the synthesis run, samples for Alvi.


## 11. Infra grouping run 1: run facts and ingest (work package P5c, part A; D-076)

**Run** (Polaris, 2026-11-24 07:19 -- 07:23 UTC; Kaiyuan): `litgroup_agent.py` v3.1 (`9c463369…1c8f`, the file at the source
commit), impact template `70018280…3925`, v3 template `ac135f00…2ae7` for the driver / mechanism chunks, corrective template
`5d052853…54b6`, Sophia `openai/gpt-oss-120b`, reasoning low, max_tokens 16000, chunk 40, source commit `7699412`, over
`partitions_infra_v1.jsonl` (`0d8f3229…9b50`). Delivered `litgroups_infra_run1_evidence.tar.gz` (`14797dc7…9f65`):
`groups.jsonl` `f61bf4f5…045ce`, `summary.json` `81d7f2b0…bf005`. **Reproduced on ingest** (`scripts/ingest_litgroups_infra1.py`,
`climrr.litgroups_infra_run1.verify_source`; any difference fails): 11 partitions, 12 chunks (8 impact_v1, 4 v3), 12 pass, 4
corrective turns (all passed; no failed first attempt), 84 groups + 59 singletons over the 198 statements each exactly once;
strength multi 20 / review 2 / single 121; group claim tags hazard_impact_on_asset 59, hazard_change_mechanism 8,
hazard_definition_or_measurement 1, impact_or_exposure 13, method_or_data 3 (singletons: 20 / 12 / 2 / 11 / 5, other 9).

**Ingested** (`artifacts/litgroups/infra_run1/`): `groups.jsonl`, `summary.json`, `agent.log`, `chunks/<chunk>.json` (the 12
`result.json`); prompts and raw responses by hash only (32); `groups_enriched.jsonl` (`1e5aa4fb…3eb1`): per record the members
resolved to `LS3-` ids, D-046 strength over the infra papers recomputed and equal to the agent's (no group touches the one
possible-duplicate pair), geography v2 classes and the states named, `family` and `asset_partition` from the partition,
`asset_class_counts`, impact mechanism / outcome / hazard relation read from the members (checked against the lists the agent
copied from `meta`); `groups_enriched_summary.json`; `manifest.json`.

**Groups by family x asset class x strength** (groups / singletons):

| family | partition | multi | single | singletons |
| --- | --- | ---: | ---: | ---: |
| heat | impact: energy | 5 | 11 | 12 |
| heat | impact: transportation_systems | 2 | 8 | 1 |
| heat | impact: healthcare_and_public_health | 1 | 1 | 8 |
| heat | impact: other_assets | 1 | 10 | 5 |
| heat | driver / mechanism | 3 / 0 | 5 / 0 | 3 / 8 |
| fire weather | impact: energy | 1 | 16 | 3 |
| fire weather | impact: transportation_systems | 0 | 9 | 0 |
| fire weather | impact: other_assets | 2 | 4 | 9 |
| fire weather | driver / mechanism | 4 / 1 | 0 / 0 | 7 (2 review) / 3 |

**59 of the 84 labelled groups have one member** (the agent's `single_member` check does not gate; fire x energy alone: 17
groups from 21 statements). **The 20 multi-source groups:** heat energy "extreme heat increases electricity demand and stresses
power supply" (9 papers), "thermal power plant output reduction", "electricity demand increase with temperature", "wildfire risk
to power transmission lines", "high temperatures cause transmission line sag and mechanical failure" (2 each); heat transportation
"pavement structural degradation from heat" (9), "rail track expansion and buckling causing disruptions" (3); heat healthcare
"population health risk increased by heat waves" (4; impact_or_exposure); heat other_assets "water-service interruptions and
stress on water infrastructure from extreme heat" (2); heat driver "projected increase in extreme heat intensity" (4),
"temperature stress degrades infrastructure performance" (3; impact_or_exposure), "heatwaves increase health risks" (2;
impact_or_exposure); fire energy "transmission line insulation reduction causing trips and outages" (2); fire other_assets "water
infrastructure degradation from wildfires" (4), "facility vulnerability to wildfire near hospitals and care sites" (2); fire
driver "Use of fire-weather indices as safety or operational indicators" (3), "Specific environmental or structural features
identified as key predictors of fire risk or damage" (3), "Climate change projected to increase fire hazard metrics" (2),
"Heat-dry conditions raise wildfire ignition or related hazards" (2); fire mechanism "Post-fire soil exposure increases runoff and
rockfall risk" (2; impact_or_exposure). **Place-named:** 14 of the 59 hazard_impact_on_asset groups have a member of geography
class state (19 a member naming any U.S. place); 6 of the 20 such singletons.

## 12. Review list for the COORDINATOR (P5c, part B; no disposition applied)

`artifacts/benchmark/review/P5_impact_groups_review_v1.csv` (`db89c906…56a7`): the 103 records tagged hazard_impact_on_asset or
impact_or_exposure (72 groups, 31 singletons), columns `group_id, kind, family, asset_partition, asset_class, claim_about,
evidence_strength, n_papers, n_independent_papers, label, member_statements` (` || `), `region_classes, place_named_states,
label_screen_flags, coordinator_disposition, kaiyuan_disposition` (the last two empty). Five columns beyond the work package's
list (`kind`, `asset_partition`, `n_independent_papers`, `place_named_states`, `label_screen_flags`) are added for the reviewer.
**Label screens** (`litgroups_infra_run1.LABEL_SCREENS`; whole-word keyword markers, never a disposition): (i) fire occurrence /
burned area as the hazard (wildfire, bushfire, fire(s), burn, ignition, smoke ...; "fire" followed by "-weather" / "danger", the index's own name, does not count), (ii) an impact on people (workers, patients, mortality,
evacuation, households, pedestrians, outdoor ...), (iii) a different hazard (flood, wind, cold, ice, storm, precipitation,
drought, debris flow, rockfall ...). Of the 59 hazard_impact_on_asset labels 31 trip a screen: (i) 25, (ii) 5, (iii) 6; by cell
fire energy 15 / 17, fire transportation 4 / 7, fire other_assets 5 / 6, heat energy 3 / 14, heat transportation 2 / 6, heat
healthcare 1 / 1, heat other_assets 1 / 8. The full listing with markers is in `groups_enriched_summary.json`
(`hazard_impact_on_asset_labels`) and the report, section 65. Kaiyuan uploads the CSV; the COORDINATOR returns dispositions; the
P5c-hotfix applies them (as `disposition_exclude` / re-tags) before the synthesis run.

## 13. Seeds and the rung-8 selection (P5c, part C; table setting confirmed, D-075)

`scripts/build_seeds_infra.py --groups artifacts/litgroups/infra_run1/groups.jsonl` (DR-SEED-INFRA-1, `seeds_infra` v1, table
setting days above 95 F / summer seasonal FWI, absolute change, mid-century): `item_seeds_infra_v1.jsonl` (`f724b4c8…0934`; 637
seeds = 49 states x 13 family-class pairs; best relevance place_named 16, us 425, general 196), `item_seeds_infra_v1_summary.json`,
`pilot_selection_infra_v1.yaml` (`0f42385a…e9e6`). P5c adds to the selection: `item_id` by cell position (`BI-P5-0001` --
`0008`, so that an unfilled cell keeps its id), `place_named_impact_evidence` (`none` for the California fallback) and
`review_state: impact_groups_unreviewed` (seeds too).

| item | cell | state (basis) | change | form |
| --- | --- | --- | ---: | --- |
| BI-P5-0001 | heat x energy | Virginia (largest of California, Virginia) | +12.5 days | QF-08 |
| BI-P5-0002 | heat x transportation | Arizona (only candidate) | +10.3 days | QF-09 |
| BI-P5-0003 | heat x water | California (fallback; `place_named_impact_evidence: none`) | +9.0 days | QF-10 |
| BI-P5-0004 | heat x healthcare | Arizona (only candidate) | +10.3 days | QF-08 |
| BI-P5-0005 | fire x energy | Arizona (largest of Arizona, California, Idaho, Nevada) | +3.9 | QF-09 |
| BI-P5-0006 | fire x transportation | California (largest of California, Montana) | +2.2 | QF-10 |
| BI-P5-0007 | fire x emergency services | **not filled** (California fallback; no seed) | --- | --- |
| BI-P5-0008 | fire x communications | California (fallback; `none`) | +2.2 | QF-08 |

**BI-P5-0007 has no seed:** the four passing fire-weather emergency-services statements were tagged `other` (2),
`hazard_change_mechanism` and `impact_or_exposure` by the agent, none `hazard_impact_on_asset`, so DR-SEED-INFRA-1 has no impact
group for the cell; reported, not filled (escalated; a COORDINATOR re-tag in the dispositions would fill it in the hotfix).

## 14. Rung-8 packets v1 (P5c, part C; provisional)

`scripts/build_synth_packets_infra.py`, `climrr.synthpackets_infra`: `artifacts/benchmark/synth_packets_infra_v1/PK-<seed>.json` +
`manifest.json` (`1aba0b10…eb1`). Per packet: the rung-3 packet v4b of the seed's pattern (same pinned inputs as packets
v4b / v5a) for the table pattern and the driver groups (driver only; their ids equal the seed's; rung-3 context groups excluded
`rung8:context_not_attached`); the seed's impact groups in rank order, at most 10 (the DR-SEED-RANK-3 driver cap; EXECUTOR, for
confirmation), the rest `over_cap:impact`; scope per group by the v5a majority rule (an impact member's basis =
`litgeo.relevance` to the item's place, so a member naming another state counts as `unknown`); `needs_general_clause` and the
v5a closing clause; `rung: 8`, `rung_instruction`, `asset_class` / `asset_class_phrase` (EXECUTOR phrases: energy systems,
transportation systems, water and wastewater systems, healthcare and public health systems, emergency services, communications
systems) / `cisa_sector`; `place_named_impact_group_ids`; plain language v1b; the selection's question form (QF-09 change slot
"projected increase"; QF-10 for a counted quantity "the number of <quantity>", both EXECUTOR for grammar); `must_not_use` = the
v4b list + "wildfire", "fires", "burned area" + "will fail", "at risk", with "wildfire" left out of a fire-weather packet and
`wildfire_rule` stating D-073b (as D-073b (b) asked); `checks_input.rung8` for post-checks v3.3; `review_state:
impact_groups_unreviewed` on the packet and every impact group. The per-packet attachment summary is in the manifest and the
report, section 65. **Synthesis blocker (escalated):** item schema v2 (frozen) allows literature statement types mechanism /
driver / consensus / caveat only, so every rung-8 item that cites an impact group fails `schema_errors` (`statement_type:
'impact'`), a non-format reason (checked offline with agent v5.2's `assemble`; `tests/test_p5c.py` documents the gap).

## 15. Sample sheet builder for Alvi (P5c, part D; not run)

`scripts/build_mentor_sheet.py --audience alvi --items <ingested rung-8 run>` (`climrr.mentor_sheet_alvi`): the mentor sheet v2's
six columns + `Asset class (CISA sector)`; "Paper side" marks each impact group "[impact; general]" or "[impact; place-specific:
<State>]" (and "[impact group not yet reviewed]" while unreviewed); README = the three mentor lines + two for Alvi (what the item
type is; the question for him). Writes `ALVI_SAMPLE_ITEMS_P5.{md,xlsx}`. Refuses to run without `--items`.

## 16. Next

COORDINATOR dispositions on the review CSV (and a decision on the schema blocker and on BI-P5-0007) -> P5c-hotfix (apply the
dispositions, rebuild seeds, selection and packets) -> Polaris: the synthesis run over the rung-8 packets
(`litsynth_agent.py --packets artifacts/benchmark/synth_packets_infra_v1 ...`; the agent's docstring example names
`synth_packets_rung8_v1`, the directory the work package renamed) and the polish -> the Alvi sheet.

(Section 16 is superseded by section 21: the dispositions are applied, the schema blocker and BI-P5-0007 are resolved.)

## 17. Item schema v2a (P5c hotfix, part A; D-077)

`data/metadata/benchmark/item_schema_v2a.json` (`deca317c…d2d8`, in `data/manifest.json`): schema v2 with `schema_version:
benchmark_item_v2a` and the literature statement type `impact`, which must carry `asset_class` (one of the 16 classes of
`infrastructure_lexicon_v1.yaml`), `impact_mechanism` and `impact_outcome` (non-empty strings), `hazard_relation`
(`governed_term` | `broader_hazard`) and `two_hop` (boolean); the requirement is a JSON-Schema `if` / `then` on the statement
type, which the project validator (`climrr.softqa._check`) now evaluates (no existing schema uses it). `benchmark_items.schema_for`
picks v2a for an item whose `schema_version` is `benchmark_item_v2a`, v2 otherwise: v2 items are unchanged, v2 stays frozen and
still refuses `impact` (`tests/test_p5c.py` keeps that test). Synthesis agent v5.3 writes a v2a item for a packet with `item_schema:
benchmark_item_v2a` (the v1a packets), each cited impact group a statement of type `impact` with the packet's `item_fields`.
**EXECUTOR readings (for confirmation):** the field types and the enum; `impact_mechanism` / `impact_outcome` are the group
members' distinct values joined by "; "; for a group whose members carry no impact fields (the two heat driver-partition groups
relabelled into the impact claim) the group label (or the singleton's statement), marked `impact_fields_source: group_label` ---
one such group is attached, `LG-infra_heat_index-driver-c1-007` in BI-P5-0001 (tenth of ten).

## 18. Dispositions applied (P5c hotfix, part B; D-078)

`data/metadata/benchmark/group_dispositions_infra_v1.csv` (COORDINATOR 2026-11-24, confirmed by Kaiyuan; byte copy `9b94e028…1bef`,
CRLF as received; in `data/manifest.json`), applied by `climrr.dispositions_infra` (vocabulary and merge targets validated; the SHA
checked) through `scripts/build_seeds_infra.py --dispositions …`. Written: `artifacts/litgroups/infra_run1/groups_dispositioned_v1.jsonl`
(`d92cd95f…91ce`; the run records + `disposition`, `disposition_source`, `disposition_exclude`, `two_hop`, `asset_class_override`,
`merged_from`) and `dispositions_v1_applied.json` (`6c371c35…8624`, the counts).

| disposition | rows |
| --- | ---: |
| accept | 41 |
| accept_two_hop | 13 |
| relabel:hazard_impact_on_asset | 6 |
| relabel:impact_or_exposure | 4 |
| merge_with | 1 (heat energy singleton c1-016 into c2-002 "transmission line sag", now 3 members) |
| not_about_family | 9 |
| reject | 15 |
| keep_excluded | 14 |

All 103 from the COORDINATOR column (Kaiyuan's empty); 17 asset-class overrides; the 40 grouping-run records without a row
(other claim tags) excluded `no_disposition`. **Usable impact groups after the dispositions: 60** (13 two-hop), by family x class
(override applied): heat energy 24, heat transportation 8, heat water 3, heat healthcare 4, heat emergency services 2, heat
commercial facilities 2, heat other 1; fire energy 8, fire transportation 3, fire water 1, fire healthcare 1, fire dams 1, fire
communications 1, fire emergency services 1 (the per-class counts are in the log). Strengths are recomputed from the members
(the merged group: multi-source). **EXECUTOR readings (for confirmation):** (i) `relabel:hazard_impact_on_asset` on a
driver-partition group also makes it an impact group (`statement_type: impact`, run type kept as `statement_type_run`), two
records; (ii) `relabel:impact_or_exposure` keeps the record out, as `keep_excluded` does; (iii) the override `other` on
`LG-infra_heat_index-driver-c1-005` is accepted (the grouping partitions' catch-all, not a lexicon class), so it seeds class
`other`, which no pilot cell uses.

## 19. Two-hop wording (P5c hotfix, part B; D-073c)

**Rule** (the work package's): a sentence resting on an `accept_two_hop` group takes the form "<scope opener> that when wildfires
occur, they <impact> <asset class>" or "… that wildfires can <impact> <asset class>" (for the heat -> ignition group: "… that
extreme heat and wind raise the chance of ignitions near power lines"); the item's table sentence states the fire-weather change;
the integrated paragraph contains, once, the bridge clause "fire-weather danger describes conditions that favour wildfire; it is
not fire occurrence". `accept` fire groups (direct fire-weather statements) need no bridge.

- **Synthesis prompt v5.3** (`litsynth_agent.py` v5.3, system prompt `1157f732…5ea5`, format corrective `46f2681c…84d6`, file
  `1be4ba2a…3edd`; `TWO-HOP (D-073c)` section, a TWO-HOP line in the format corrective prompt; check version v3.4; v5.2, which
  never ran, held by its bytes at `a549ea9`, `climrr.p5c.held_bytes`).
- **Post-checks v3.4** (`benchmark_items.SYNTH_CHECK_VERSION_V34`): v3.3 plus, when `checks_input.rung8.two_hop_group_ids` is
  present, (a) a literature sentence citing a two-hop group must match `when wildfires occur | wildfires can | raise the chance
  of ignition(s)` (`TWO_HOP_RE`) and is exempt from the hazard-phrase rule (the direct groups it cites keep it); (b) when the
  item cites a two-hop group and the packet gives `bridge_clause`, the integrated paragraph contains it exactly once (case and
  whitespace normalised); (c) in a fire-weather item "wildfires" inside the two phrases is masked like D-073b's phrase, in every
  graded field but the prompt. Both failures are format-class (one corrective turn). v3.3 is unchanged.
- **Packets** carry `two_hop_group_ids`, `two_hop_rule`, and in a fire-weather packet with a two-hop group `bridge_clause`;
  `checks_input.rung8` adds `two_hop_group_ids`, `bridge_clause`, `two_hop_phrases`.
- **EXECUTOR readings (for confirmation):** two heat groups are two-hop (`LG-infra_heat_index__energy-impact-c1-003`, the
  heat -> ignition group, in BI-P5-0001; `LG-infra_heat_index__transportation_systems-impact-c1-007` "heat-driven vegetation fires
  threaten railway corridors", in BI-P5-0002). The bridge clause names fire-weather danger, so it is required only in fire-weather
  items; in a heat packet with a two-hop group "wildfire" leaves `must_not_use` (the two-hop forms write "wildfires"), and no
  bridge is required. A two-hop sentence does not carry the broader-hazard phrase.

## 20. Seeds, selection and packets v1a (P5c hotfix, part C; D-078)

**Seeds / selection** (`seeds_infra` v1a; `item_seeds_infra_v1a.jsonl` `0bd723a0…ea2a`, 686 seeds; `pilot_selection_infra_v1a.yaml`
`316a93f9…9212`; `review_state: impact_groups_reviewed`). The candidate states of a cell are now read **through the dispositions**:
a state counts when a cited member of a usable impact group of the cell's family and class names it (EXECUTOR reading of "rebuild
the selection with the dispositions applied", for confirmation; without it BI-P5-0005 would stay at Arizona on the strength of a
group rejected as "operational heuristic, not an impact"). **Packets** `synth_packets_infra_v1a/` (manifest `829d80cf…5bf2`;
`scripts/build_synth_packets_infra.py --variant v1a`; not provisional). v1 seeds, selection and packets are kept and rebuild
byte-identically.

| item | cell | state (evidence) | form | impact groups (two-hop) | drivers | excluded |
| --- | --- | --- | --- | ---: | ---: | ---: |
| BI-P5-0001 | heat x energy | Virginia (place-named) | QF-08 | 10 of 24 (1) | 8 | 60 |
| BI-P5-0002 | heat x transportation | Arizona (place-named) | QF-09 | 8 (1) | 8 | 46 |
| BI-P5-0003 | heat x water | California (none) | QF-10 | 3 (0) | 8 | 53 |
| BI-P5-0004 | heat x healthcare | **California (none; was Arizona)** | QF-08 | 4 (0) | 8 | 53 |
| BI-P5-0005 | fire x energy | **California (none; was Arizona)** | QF-09 | 8 (7) | 8 | 37 |
| BI-P5-0006 | fire x transportation | California (none; was place-named) | QF-10 | 3 (1) | 8 | 37 |
| BI-P5-0007 | fire x emergency services | California (none) --- **now filled** | QF-08 | 1 (0) | 8 | 37 |
| BI-P5-0008 | fire x communications | California (none) | QF-09 | 1 (0) | 8 | 37 |

- **BI-P5-0004** no longer carries the two Arizona people-statements (relabelled `impact_or_exposure`); no other healthcare impact
  group names a state, so the cell falls back to California and is a **general item** (four single-source groups, all general;
  closing clause required).
- **BI-P5-0005** every place-named fire x energy group was rejected (Arizona / Nevada, Idaho, California): California fallback,
  general; seven of its eight impact groups are two-hop, so the bridge clause is required. **BI-P5-0006**: Montana's group
  rejected, the California group `not_about_family`; the state stays California, the evidence becomes `none`.
- **BI-P5-0007** carries the relabelled standby-cost singleton (`LG-infra_fire_weather_index__other_assets-impact-c1-012`,
  Northern Territory, governed term "fire-danger days", direct). **BI-P5-0008** keeps its one direct group (telecommunication
  loss).
- The per-packet groups (id, label, strength, two-hop, place class) are in `synth_packets_infra_v1a/manifest.json` and the report,
  section 67.

## 21. Next

Polaris (Kaiyuan): the synthesis run `infra_run1` over the eight v1a packets (agent v5.3) and the polish of its items, at the pushed
hotfix commit; then ingest -> the Alvi sheet (`scripts/build_mentor_sheet.py --audience alvi --items …`). Commands: the report,
section 68, and `docs/PROJECT_STATE.md`.

## 22. Synthesis run 1: outcome (agent v5.3, packets v1a; superseded)

Polaris `litsynth/infra_run1`, agent v5.3, post-checks v3.4, 2026-11-24 22:56 UTC, eight v1a packets. **Run 1, superseded** by the
answer shape v2 (§23). The facts below are **as relayed in the work package** (litsynth v5.4); the run's files are not in the
repository and no ingest was made.

- **2 deterministic_pass** (BI-P5-0001, BI-P5-0003), **6 rejected_pre_review**. Every failure is template conformance (format
  class):

| item | failure (as relayed) |
| --- | --- |
| BI-P5-0002 | scope opener a word off; broader-hazard phrase missing in an impact sentence |
| BI-P5-0004 | asset-class name missing in an impact sentence |
| BI-P5-0005 | bridge clause "found 0": written with U+2011 ("fire‑weather") and a lower-case start |
| BI-P5-0006 | scope opener a word off; broader-hazard phrase missing; bridge clause "found 0" (as 0005) |
| BI-P5-0007 | scope opener a word off |
| BI-P5-0008 | broader-hazard phrase missing in an impact sentence |

- **Text quality** (passing and failing items): the broader-hazard phrase repeated up to four times per answer (the v3.4
  per-sentence rule asked for it); five to six driver sentences before any impact; "that that when wildfires occur"; a garbled
  "this implies more exposure to more pavement distress points are detected" (BI-P5-0002).

## 23. Rung-8 answer shape v2 (work package litsynth v5.4; D-075a)

**Rules (D-075a, decided).** (1) Length budget: one table sentence, at most two driver claims (by strength), two to three impact
claims (by strength, then place), the closing clause, and the bridge clause in a fire-weather item that needs it; nothing else.
(2) The broader-hazard phrase once per answer, in the first impact sentence ("… extreme heat, of which dangerous heat-index days
are one measure, …"; fire: "… conditions that favour wildfire, of which fire-weather danger is one measure, …"); later impact
sentences say "such heat" / "such conditions"; the asset class named in full once, then by a stored short form. (3) Claims sharing
a scope class merged under one opener ("In general, research shows that A, that B, and that C"); place-named sentences keep
theirs; at most three openers (prompt only; the checker verifies openers per sentence as before). (4) Two-hop: "… that when
wildfires occur, they <impact>", never "that that". (5) The "this implies more exposure to" sentence is dropped for the pilot.
(6) Bridge clause as the second sentence, capitalised; every phrase check after Unicode normalisation (U+2010 / U+2011 / U+2012 ->
"-", NFKC) and case-insensitive. (7) Corrective turn: format class, as before.

- **Synthesis prompt v5.4** (`litsynth_agent.py` v5.4; system prompt `1a023c1e…3ade`, format corrective `a21eb42a…10e8`): the RUNG 8
  section is the answer shape v2 (parts in order, MERGE OPENERS, the integrated paragraph repeats the same sentences); TWO-HOP gives
  the bridge clause as the second sentence of `integrated`; WRITING asks for plain "-" hyphens; the format corrective prompt names
  the shape-v2 rules. v5.3, which ran (run 1), is held by its bytes at `b860658` (`climrr.p5c2.held_bytes`).
- **Post-checks v3.5** (`benchmark_items.SYNTH_CHECK_VERSION_V35`; all new failures format-class):
  - every phrase check through `phrase_norm` / `phrase_key` (scope openers, the closing clause, the integrated "research" sentences,
    hazard phrases, asset names, two-hop phrases, the bridge clause, the fire words);
  - `doubled 'that' (D-075a)` in any graded text, every v3.5 item;
  - with `checks_input.answer_shape == "rung8_v2"` (packets v1b): the budget (`rung8_budget`: claims = the "that"-clauses of a
    literature sentence, at least one; impact claims = sentences citing an impact group, driver claims = the others with a group;
    floor `min(2, impact groups in the packet)`; the integrated paragraph no longer than the reference sentences plus the bridge);
    the hazard named in the first **direct** impact sentence (broader-hazard phrase when a cited direct impact group rests on a
    broader term, else a quantity phrase); the broader-hazard phrase exactly once in the literature sentences when required (at
    most once otherwise) and at most once in the paragraph; the asset class in full in the first impact sentence and in full or a
    short form in every later one; "this implies more exposure to" a failure; reports `budget`, `broader_hazard_phrase_count`,
    `bridge_clause_sentence` (second sentence: reported, not failed), `scope_openers`.
  - without `answer_shape` (packets v1a; run-1 items) the v3.4 per-sentence rules apply and the budget is **reported, never
    failed** (`budget.enforced: false`).
- **Short forms** `data/metadata/benchmark/asset_short_forms_v1.yaml` (`de28eaa2…444d`, in `data/manifest.json`): energy "the grid",
  "power systems"; transportation "roads and rail"; water "water systems"; healthcare "hospitals and emergency services",
  "hospitals"; emergency services "emergency responders"; communications "communications networks".
- **Packets v1b** `synth_packets_infra_v1b/` (`scripts/build_synth_packets_infra.py --variant v1b`; manifest `b4cbbdb3…a3e`): the
  v1a packets (each checked against the v1a manifest) with `answer_shape: rung8_v2`, `asset_class_short_forms` (model view and
  `checks_input.rung8`), the rung instruction rewritten for shape v2 (`RUNG8_INSTRUCTION_V2`; the v1a instruction allowed the
  exposure sentence), and their own metadata (`version`, `decision`, `rules`, `inputs_sha256.asset_short_forms_v1`,
  `v1a_packet_sha256`). Groups, provenance, scope, question forms, bridge clause and every other field are v1a's (tested). v1a is
  kept.
- **EXECUTOR readings (for confirmation):** the claim as the budget unit; the floor for one-group cells (BI-P5-0007, BI-P5-0008);
  "first impact sentence" for the hazard is the first direct one (a two-hop sentence never carries the broader phrase); a later
  impact sentence must name the asset (full or short), a pronoun fails; the short-form assignments; "remove from checks" read as
  "the allowance is removed": the exposure sentence fails under shape v2; the bridge position reported, not failed; the bridge
  still required only where packets v1a required it (fire-weather item citing a two-hop group: BI-P5-0005, BI-P5-0006).

## 24. Next

Polaris (Kaiyuan): synthesis `infra_run2` over the eight v1b packets (agent v5.4) and the polish `litpolish/infra_run2`, at the
pushed build commit; then ingest -> the Alvi sheet. Commands: the report, section 70, and `docs/PROJECT_STATE.md`.

## 25. Synthesis runs 1 -- 2 and polish ingested (work package P5d, part A; D-080)

One tarball, `infra_synth_runs12_evidence.tar.gz` (`1ab28929…3f7`, verified), ingested by `scripts/ingest_litsynth_infra_run2.py`
(`src/climrr/litsynth_infra_run2.py`): every stated fact re-derived from the delivered files; every item and superseded attempt
re-assembled from its raw response by the pinned agent and re-checked (run 2: v5.4 at `bf69970`, post-checks v3.5, packets v1b
`b4cbbdb3…a3e`; run 1: v5.3 at `b860658`, v3.4, packets v1a `829d80cf…5bf2`); every rewrite re-extracted by polish v1.1 and
re-checked (checks v2). All equal to the recorded results (`checks_reproduced`). Run 2 ran at source commit `bf69970` (the
evidence-only commit on top of the build `ca6f56f`; agent bytes verified there).

- **Run 2 (`items/infra_run2/`; D-080, the impact sample set).** First start: 5 of 8 pass; BI-P5-0002 (three driver claims, above
  the budget), 0003 (doubled magnitude phrase) and 0005 (FWI wording in a rubric point; a two-hop sentence without its marker) rejected,
  moved to `attempt1/`, and each redrawn by its own restart: 0002 passed, 0003 and 0005 were rejected again. **6 pass** (0001, 0002,
  0004, 0006, 0007, 0008) -> `human_review`; **0003, 0005 -> `rejected_pre_review`, `redraws: 2`** (the work package's count; two
  generations of each seed in run 2, both rejected). The three first attempts are `superseded_attempt`s
  (`items/infra_run2/superseded/`). Format corrective used 6, passed 4; leakage flags 0; question diversity (opening trigram)
  largest share 0.375 (report, as in run 1).
- **Polish run 2 (`polish/infra_run2/`).** Two starts (before and after the 0002 redraw): 4 polished (0002, 0004, 0006, 0007), 2
  rejected (0001 places "United States" lost; 0008 hedge "shows" lost); 0003 and 0005 skipped.
- **Run 1 (`items/infra_run1/`, `polish/infra_run1/`; superseded).** Now in the repository: 2 pass (0001, 0003), 6 rejected, as
  relayed in §22; polish run 1 polished 0003, rejected 0001.
- **Regression fixture.** The two run-1 passing items, pinned in `items/infra_run1/items.jsonl`, pass post-checks v3.5 against their
  v1a packets with the budget reported (`within: false`, `enforced: false`) --- the check the v5.4 package made on synthetic items
  (`tests/test_p5d.py`; manifest `run1_regression`).

## 26. Display text: D-079 and the COORDINATOR display edits (P5d, parts A -- B)

**D-079 (decided).** Display text = the polished text **only if** the polish passed **and** post-checks v3.5, re-run on the
polished question and answer against the item's v1b packet, pass; otherwise the original. Each item's `human_review` event records
`display_source`, `display_recheck` and `display_text`.

| item | polish | v3.5 on the polished text | display |
| --- | --- | --- | --- |
| BI-P5-0001 | rejected (places) | fail: closing clause dropped; five "Research shows" openers without scope | original |
| BI-P5-0002 | polished | pass | **polished** |
| BI-P5-0004 | polished | fail: 8 sentences, budget 6 (sentences split) | original |
| BI-P5-0006 | polished | fail: 8 sentences, budget 6 | original |
| BI-P5-0007 | polished | fail: "In general," dropped from two openers; 5 sentences, budget 4 | original |
| BI-P5-0008 | rejected (hedges) | fail: 4 sentences, budget 3 | original |

**COORDINATOR display edits** (`artifacts/benchmark/review/P5_display_edits_v1.yaml`, `coordinator_edit`; applied after D-079 by
`mentor_sheet_alvi`; generated and polished texts kept in the items): the closing clause reworded to "These are general research
findings, not findings specific to <Place>." where the item has one (0001, 0002, 0004); the U.S. opener reordered (0002); 0001's
two-hop sentence replaced ("extreme heat and wind raise the chance of ignitions near power lines"); 0002's doubled magnitude removed
and its two-hop roads-and-rail sentence deleted (the group stays on the sheet, marked as no longer in the displayed answer); 0007's
humidity sentence replaced ("drier air, with a higher vapor-pressure deficit, raises fire danger"). 0006 and 0008: no edit applies.

**Checks on the edited texts** (`P5_display_edits_v1_checks.json`): leakage v2.3 **0 failures**; post-checks v3.5 **3 failures**
(0001, 0002, 0004), each only the closing clause: v3.5 compares it with the packet's pinned `general_clause` ("These are general
drivers of <quantity>, …"), and the new wording names "research", so the D-069 rule for paragraph sentences naming research also
catches it. With only the clause put back, **0 failures**. Escalated (report section 72): accept the wording in a post-checks bump
(the packets' `general_clause` and the scope rule's exemption), or keep the generated clause.

**"All six" read as "where a closing clause exists".** 0006, 0007, 0008 have none: they cite a California-specific driver group,
and D-069 (post-checks v3.2+) fails a closing clause there. None was added; for the COORDINATOR.

## 27. The two dropped cells (P5d)

- **BI-P5-0003 (water and wastewater x heat, California):** both draws wrote "increase a moderate increase" (DR-DESC-1 v4 doubled
  magnitude), in the table sentence and in the paragraph; format class, the corrective turn did not fix it.
- **BI-P5-0005 (energy x fire weather, California):** the first draw used "wildfire(s)" in a rubric point and a two-hop sentence
  without its marker; the second kept the two-hop fault: `literature_interpretation[1]` cites the two-hop group
  `LG-infra_fire_weather_index__energy-impact-c1-001` but is written as a direct sentence ("In general, research shows that
  conditions that favour wildfire, … can increase exposure of energy systems to fire perimeters, …") without "when wildfires
  occur" / "wildfires can" / "raise the chance of ignition".
- Neither enters review. The sheet carries six items (three heat, three fire weather; four California, one Virginia, one Arizona).

## 28. Next

The Alvi sample sheet (`ALVI_SAMPLE_ITEMS_2026-11-25.{xlsx,md}`; notes for Kaiyuan `…_notes.md`) goes to Alvi. After both reviews
(the mentor's of the 2026-11-19 sample, Alvi's of this one): the GUIDANCE packet P2 -- P5 and the merge, and the P6 scale-up plan.

## 29. P5d hotfix: closing clause as generated (COORDINATOR 2026-11-25; D-079)

The closing-clause rewording (§26) is removed from `P5_display_edits_v1.yaml`; BI-P5-0001, 0002, 0004 keep the generated clause
("These are general drivers of dangerous heat-index days, not findings specific to <Place>."). The other edits stay (0002 opener,
magnitude, roads-and-rail sentence; 0001 ignition sentence; 0007 humidity sentence); 0004 now carries no edit (display: original).
Leakage v2.3 and post-checks v3.5 on **all six** display texts: **0 failures**. The wording change is deferred to prompt v5.5 ("These
are general findings about <hazard phrase>, not findings specific to <Place>"), with the packets' pinned clause and the opener rule
updated together. The §26 escalation and the "All six" reading are closed by this.
