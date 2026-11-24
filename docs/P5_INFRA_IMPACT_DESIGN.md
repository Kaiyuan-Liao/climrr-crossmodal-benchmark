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
