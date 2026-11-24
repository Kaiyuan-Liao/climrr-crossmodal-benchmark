# P5 --- hazard -> infrastructure impact items: design (work package P5a, 2026-11-23)

Follows the group meeting of 2026-11-23 (mentor, Alvi, JL; `MENTOR_BRIEF.md`) and D-069 -- D-073. P5a built the tools
and rules below with **no model call**; the runs are on Polaris (§6), then sample QAs go to Alvi. Successor of
`PILOT_P2B_DESIGN.md` for this line of work (that file stays the record of the P2b / P3 pilots).

## 1. Pipeline

The P1 -- P3 workflow (table concepts -> queries -> papers -> per-paper extraction -> grouping -> packets -> synthesis ->
polish -> review), applied to LITCORPUS-03 (`LITCORPUS03_PROVENANCE.md`):

1. transfer, verify, **inventory** (`scripts/litcollect/inventory_corpus.py`), **index** (`build_index.py`);
2. **lexicon query** (`run_query.py` v4 `--lexicon`): hazard-family hits, asset-class hits, impact-term hits and
   hazard + asset co-occurrence within a section, per paper (`paper_hits.jsonl`);
3. **candidates** `DR-CAND-INFRA-1` (§3) -> `candidates.json`, shipped back as `data/metadata/softqa/infra_candidates_v1.json`
   (hash pinned on ingest; re-derived by `climrr.infra_lexicon.verify_candidates`);
4. **extraction** (`litstatement_agent.py` v4 `--arm infra_impact_v1`; statement type `impact`, D-073);
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
taken here. The query reports the counts that decision needs.

## 4. Item type (rung 8, D-071) and the wording rule

Table pattern (hazard change at a place) + `impact` statements (hazard condition -> asset class -> mechanism / outcome) +
general drivers where available. The answer states the hazard change as projected, the impact pathway as what research
shows about such conditions, and never that a specific asset at the place will fail. Scope marking applies with extra
force: impact statements are almost always general, so most rung-8 answers will close with the general clause. Question
form QF-08: "What does a projected <change> in <hazard phrase> in <Place> <horizon> mean for <asset class>, and why?"

## 5. Scope rule and question forms (D-069; packets v5, synthesis prompt v5, post-checks v3.2)

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

At the pushed commit `<PINNED_SHA>` that carries P5a; the litcollect root in `$LITCOLLECT_ROOT_POLARIS`; first check the
environment: `python -c "import yaml, duckdb; print(duckdb.__version__)"` (DuckDB 1.5.4).

    bash "$CLIMRR_REPO_ROOT/scripts/sophia_pull_pinned.sh" <PINNED_SHA>
    cd "$CLIMRR_REPO_ROOT"
    L="$LITCOLLECT_ROOT_POLARIS"; SRC="$L/sources/critical_infrastructure_v1"
    # 1. transfer the tarball into "$SRC", then verify and extract (expect 6c6e21c2...1ec76; the archive should hold kept/)
    sha256sum "$SRC/critical_infrastructure_judged_relevant.tar.gz"
    tar -tzf "$SRC/critical_infrastructure_judged_relevant.tar.gz" | head -3
    tar -xzf "$SRC/critical_infrastructure_judged_relevant.tar.gz" -C "$SRC"
    # 2. inventory (overlap with the 186k set through its index manifest)
    mkdir -p "$L/inventory"
    python scripts/litcollect/inventory_corpus.py --root "$SRC/kept" --out "$L/inventory/litcorpus03_inventory.json" \
        --corpus-id LITCORPUS-03 --compare-ids "$L/index/full_705k_v2_filtered/manifest.csv" \
        --compare-label LITCORPUS-02-source-186k
    # -> stop here if the file count is not 89,497 or _araiadoc_tags is a string (LITCORPUS03_PROVENANCE.md §3)
    # 3. index
    python scripts/litcollect/build_index.py --root "$SRC/kept" --out "$L/index/critical_infrastructure_v1"
    # 4. lexicon query and candidates (DR-CAND-INFRA-1, cap 300 per family)
    python scripts/litcollect/run_query.py --index "$L/index/critical_infrastructure_v1" \
        --out "$L/runs/infra_lexicon_v1" --name infra_lexicon_v1 \
        --lexicon data/metadata/litstatements/infrastructure_lexicon_v1.yaml \
        --family heat_index=artifacts/literature/litcorpus02/evidence/queries/extreme_heat_diag_topical_only_query.txt \
        --family fire_weather_index=artifacts/literature/litcorpus02/evidence/queries/fire_weather_diag_topical_only_query.txt \
        --family-disambiguate 'fire_weather_index:fwi=fire weather|fire-weather' --cap 300

Ship back: `litcorpus03_inventory.json`, the index's `index_summary.json` and `build.log`, and the query run's
`summary.json`, `candidates.json` and `paper_hits.jsonl` (with SHA-256 of each). The ingest pins
`infra_candidates_v1.json` = `candidates.json` and re-derives it. The extraction run (`litstatement_agent.py --arm
infra_impact_v1 --reasoning-effort low --max-tokens 6000`, invocation in the agent's docstring) runs at the commit that
carries the pinned candidates, after the COORDINATOR has seen the counts.
