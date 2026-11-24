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
5. grouping, rung-8 packets, synthesis, polish --- designed after the extraction run is ingested;
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
