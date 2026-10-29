# Benchmark redesign --- pattern-level open-ended QA (2026-10-29)

Design document for the redesign the mentor directed on 2026-10-29. It is
written from decisions **D-035 -- D-040** in [`DECISION_LOG.md`](DECISION_LOG.md);
where this document and the log disagree, the log governs. Nothing here has been
generated: **no item, pattern, statement or answer in this document comes from a
run**, and every value in §2 is marked illustrative.

**Status.** D-035, D-036, D-037, D-039, D-040 decided; **D-038 (the ladder)
proposed**, for mentor confirmation. **GUIDANCE re-anchor ruling 2026-10-29:
PASS WITH ACTIONS (D-041)**, ~10-item pilot authorized. **Pilot P1 done**
(schema v2, NCA5 map, table-pattern extractor, statement agent; no item yet);
next: the Polaris statement run, then P2 (aggregation, synthesis, review).

---

## 1. Use case and its consequence: closed-book (D-035)

**Use case, as stated by the mentor (2026-10-29, owner-relayed):** the benchmark
question is given directly to an LLM; the model answers from what it already
knows; it receives **no table and no papers**.

Consequences:

- **The question names no source.** No item may name the ClimRR table, a cell, a
  column, a paper, or say "according to ...". A question about "this table" or
  "this paper" is meaningless to a model that has neither.
- **Questions are answerable from general climate-science knowledge.** They are
  asked at the level of a general pattern (a state, several states, a climate
  region; a season; a scenario class; a horizon), never at the level of a single
  number or a single paper's detail.
- **The two sources supply the answer key and its provenance, not the
  question's subject.** The table fixes what the projection shows; the
  literature fixes the mechanisms, drivers, consensus and caveats. Both are
  recorded on the item so that a reviewer can check the key.
- The four soft-QA examples shown on 2026-10-28 are recorded as
  `rejected_by_mentor: too specific` (D-036): they were tied to concrete numbers
  and details of the table and the papers.

## 2. What an item is (D-037; schema v2, D-041)

**Machine schema: [`data/metadata/benchmark/item_schema_v2.json`](../data/metadata/benchmark/item_schema_v2.json)**
(pinned in `data/manifest.json`; validator `src/climrr/benchmark_items.py`). It
keeps the D-037 field set of the mentor-supplied ENSURE use-case sheet
(`ENSURE_Prompt Use Cases_v3.xlsx`, D-040, [`REFERENCES.md`](REFERENCES.md)) and
adds the guardrails of the GUIDANCE re-anchor ruling
([`BENCHMARK_REANCHOR_GUIDANCE_RULING.md`](BENCHMARK_REANCHOR_GUIDANCE_RULING.md),
D-041). The sheet's column *What ENSURE Is Doing* maps to **`system_task`**.

| Group | Fields | Notes |
| --- | --- | --- |
| Identity / intent | `item_id`, `use_case_level` (ladder rung, D-038), `capability_tested`, `system_task`, `reasoning_modalities` (`Hazard` / `Text` / `Hazard + Text`), `key_relationships`, `evidence_needed`, `desired_output_characteristics`, `expected_knowledge_level` (`general_climate_science` / `specialist_climate_science`) | |
| Prompt | `prompt`, `source_independent_answerability` (`yes` / `borderline` / `no`; only `yes` valid), `source_independence_note`, `source_leakage_check` {`clmrr_named`, `row_or_column_named`, `paper_named`, `hidden_exact_value_required`, `according_to_phrase`, `pass`} | the leakage check is recomputed by the validator; hits go to review |
| Reference components | `table_patterns[]` (family, season, horizon, scenario, statistic, `geography_type` ∈ state / nca_region / multi_state_set / cell_control, geography, direction, `computed_value_or_range`, rank, `relative_magnitude` {class, definition} or null, `pattern_support_n`, `pattern_robustness`, provenance {columns, column_statuses, row_rule, derivation_rule_id, code_version, table_data_sha256}); `literature_mechanisms[]`, `literature_caveats[]` (statement, `statement_type`, `evidence_strength` ∈ multi_source / review / single_source, `reference_scope`, `supports[]` with paper id, SHA-256, JSON path, span, verbatim passage, independence note) | a table pattern is a record of `table_patterns_v1.jsonl` (deterministic); literature supports come from the statement agent |
| Reference answer | `reference_answer` {`table_pattern`, `literature_interpretation`, `integrated`} | stored separately (ruling condition E) |
| Grading | `rubric` {`required_points`, `acceptable_variants`, `optional_points`, `disallowed_claims`, `fatal_errors`}; `guardrails[]` | free-text answers graded against the reference |
| Audit / provenance | `c_g_t_s_d_audit` (nullable; audit only), `generation` {generator_version, model, prompt_hash, timestamp, inputs_sha256} | |
| Review | `review` {status (D-033 lifecycle), history, `kaiyuan_disposition`, `mentor_disposition`, `final_frozen` {prompt, reference_answer, rubric}} | accepted only with both dispositions and a frozen final (condition F) |

The validator's `validity` returns the ruling's six conditions A--F (source
independence, deterministic table facts, provenance-backed literature, explicit
evidence strength, decomposition, human acceptance); only an item meeting all six
is benchmark-valid.

### 2.1 Worked item --- ILLUSTRATIVE, not generated

> **Every value below is illustrative.** It shows the *shape* of a v2 item. No
> item was generated, no paper was read, and nothing here is an answer key.
> Bracketed `<…>` slots are filled only by the pipeline (§4). The FWI summer
> value columns are `inferred_candidate` (IC-006..IC-010): a pattern on them is
> `acceptance_blocked`, so an item of this kind **could not reach `accepted`
> today**.

```yaml
# ILLUSTRATIVE --- not generated, not an answer key (schema v2)
item_id: BI-ILLUS-0001
use_case_level: 3            # Pattern + mechanism (D-038, proposed)
system_task: <what the system does: retrieve the projected pattern, explain it>
reasoning_modalities: Hazard + Text
expected_knowledge_level: general_climate_science
prompt: >-
  How is summer fire weather danger projected to change across the U.S.
  Southwest by the late 21st century under a high-emissions scenario, and what
  drives that change?
source_independent_answerability: yes
source_leakage_check: {clmrr_named: false, row_or_column_named: false, paper_named: false,
                       hidden_exact_value_required: false, according_to_phrase: false, pass: true}
reference_components:
  table_patterns:            # records of artifacts/benchmark/table_patterns_v1.jsonl
    - {pattern_id: <TP1-…>, family: fire_weather_index, season: summer, horizon: end, scenario: RCP8.5,
       statistic: direction, geography_type: nca_region, geography: NCA5-SW, direction: <…>,
       computed_value_or_range: <…>, rank: <…>, relative_magnitude: null, pattern_support_n: <…>,
       pattern_robustness: <…>, acceptance_blocked: true}
  literature_mechanisms:
    - {statement: <…>, statement_type: mechanism, evidence_strength: <multi_source_supported | review_supported>,
       reference_scope: regional_climate_expectation, supports: [<≥ 2 independent spans, or one review>]}
  literature_caveats: [<…>]
reference_answer:
  table_pattern: <direction / relative standing, as the pattern states it>
  literature_interpretation: <mechanism sentences, each traced to its supports>
  integrated: >-
    <…> Fire weather danger describes meteorological fire danger, not whether
    fires occur. RCP8.5 is one high-emissions scenario, not the only future.
rubric:
  required_points: [direction, region, mechanism, scenario/horizon handled]
  acceptable_variants: [<…>]
  optional_points: [<…>]
  disallowed_claims: [FWI equals fire occurrence or burned area]
  fatal_errors: [<reverses the direction>]
guardrails: [RCP8.5 is one high-emissions scenario, the historical value is a modeled baseline, FWI is fire danger not occurrence]
c_g_t_s_d_audit: <audit only>
review: {status: illustrative, kaiyuan_disposition: null, mentor_disposition: null, final_frozen: null}
```

## 3. The hazard-projection use-case ladder v1 (D-038, proposed)

Each rung adds a capability over the one before, as the ENSURE sheet's rungs
do. Example prompts are **illustrative**, all at general level.

| # | Use case | Modalities | Example prompt (illustrative) |
| --- | --- | --- | --- |
| 1 | Hazard pattern identification | Hazard | "How is the number of days with a heat index above 105 °F projected to change across the southern Great Plains by mid-century under a high-emissions scenario?" |
| 2 | Hazard mechanism | Text | "What meteorological conditions raise fire weather danger during summer in the western United States?" |
| 3 | Pattern + mechanism | Hazard + Text | "How is summer fire weather danger projected to change in California by the late 21st century under a high-emissions scenario, and what drives that change?" |
| 4 | Regional comparison | Hazard (+ Text) | "Under a high-emissions scenario, is extreme heat projected to increase more in the Southeast or in the Northwest by the end of the century, and why?" |
| 5 | Projection--literature consistency | Hazard + Text | "Is a projected late-century increase in summer fire weather danger across the Southwest consistent with what the climate literature reports about drying and warming there?" |
| 6 | Compound hazards: fire weather and extreme heat | Hazard + Text | "Where in the United States are increases in summer fire weather danger and in extreme-heat days projected to coincide under a high-emissions scenario, and what links the two?" |
| 7 | Scenario and uncertainty | Text (Hazard only where the table has the scenario) | "How do projections of extreme heat in the United States differ between high- and moderate-emissions scenarios, and what limits confidence in them?" |
| 8 | Exposure implications | Text | "What does a projected rise in extreme-heat days imply for populations and infrastructure in the Southwest, and what does such a projection not tell you?" (guardrail: hazard ≠ exposure ≠ risk) |

Rung 7: for our governed families only RCP8.5 exists in the table (Track D v1:
no governed column realizes RCP4.5), so a scenario contrast is Text-only.

## 4. The pipeline

```
table-pattern extraction      (deterministic; from Track D)
        │
literature-statement extraction (agent; from Track C)
        │
cross-paper aggregation        (deterministic clustering + agent-assisted paraphrase grouping)
        │
item synthesis                 (agent; forbidden to invent facts not in its inputs)
        │
deterministic checks           (every number/direction → a table pattern; every mechanism → ≥ 2 papers or single-source)
        │
human review                   (Kaiyuan, then the mentor)
        │
accepted
```

1. **Table-pattern extraction (deterministic; Track D machinery, D-039).**
   Patterns at state, multi-state and climate-region level: direction,
   magnitude class, seasonal and regional contrasts, ranking, scenario and
   horizon. Each pattern carries its columns, row-selection rule, derivation rule
   id and computed values. Cell-level outputs are kept only as provenance,
   never as question content. Column governance is unchanged: an
   `inferred_candidate` concept column blocks acceptance (D-033, D-034).
2. **Literature-statement extraction (agent; Track C machinery, D-039).** The
   agent prompt is rewritten to extract **general statements** --- mechanism,
   driver, consensus, caveat --- with region and scenario where the paper states
   them, each with a verbatim span. The span re-slice pre-check of D-033 applies
   unchanged. Corpus: the frozen 243 place candidates and LITCORPUS-02 (1,308).
3. **Cross-paper aggregation.** Deterministic clustering by family, region and
   direction, then agent-assisted paraphrase grouping within a cluster. **Every
   cluster keeps its member spans.** A statement supported by one paper is a
   citation, not a pattern (D-036).
4. **Item synthesis (agent).** From one table pattern plus its statement
   clusters, the agent writes the prompt, the reference answer and the rubric.
   It is **forbidden to introduce any fact not in its inputs**; the prompt must
   name no source (D-035).
5. **Deterministic checks.** Every number and direction in the reference answer
   traces to a table pattern; every mechanism sentence traces to ≥ 2 papers or
   is marked single-source; the prompt contains no source reference (table,
   column, cell, paper, "according to").
6. **Human review.** Kaiyuan first, then the mentor, on a sample of
   representatives (Kaiyuan's default, 2026-10-29: no quota --- generate, sample,
   design filters from feedback). Lifecycle per D-033.
7. **Accepted.**

Answers are **free text graded against the reference answer by the rubric**,
not multiple choice (Kaiyuan's default, 2026-10-29). Scenario names may appear
if the relationship is kept correct ("RCP8.5 is one case of a high-emissions
scenario").

## 5. What is retired and what is kept (D-036, D-039)

| Item | Status |
| --- | --- |
| Claim-level compatibility (C/G/T/S/D) | **retired as a gate**; kept as audit metadata where a literature statement is tied to a specific table pattern (`BRIDGE_ELIGIBILITY.md` §11) |
| Track D (slots, templates, deterministic answers) | **re-purposed** as the table-pattern extractor at state/region level |
| Track C (agent, pre-check, schema) | **re-purposed** as the literature-statement extractor; prompt rewritten |
| Frozen place-candidate set (243), LITCORPUS-02 (1,308) | **kept** as the corpus |
| Prototype units P-CELL-1, P-COUNTY-1, P-STATE-1 | **kept** as controls and provenance examples |
| Track A-next, Track B | **closed as superseded**; their outputs remain evidence |
| The four 2026-10-28 soft-QA examples | `rejected_by_mentor: too specific` |
| Column statuses, `concept_map.yaml`, governed families | **unchanged** |

The charter's "semantic bridge" (BLUEPRINT §M5) is redefined at **pattern
level**: a table pattern joined to an aggregated literature statement, not a
cell joined to a single claim. GUIDANCE is notified (D-039).

## 6. Open questions

Answers recorded 2026-10-29 from the GUIDANCE re-anchor ruling (D-041) and pilot
P1 are marked **answered**; the rest stay open.

**For the mentor**

1. Does the item schema (§2) match what you want? --- *GUIDANCE accepted the
   direction with additions (schema v2, §2); the mentor has not yet seen v2.*
2. Review of the first pilot items (next package, about ten). --- *open;
   GUIDANCE requires Kaiyuan and mentor acceptance of every pilot item.*
3. Does the ladder (§3, D-038) fit, or should rungs be added, merged or dropped?
   --- *open; GUIDANCE: span the ladder where evidence allows, no quota.*
4. May a mechanism supported by a single paper appear in a reference answer if
   it is marked single-source? --- **answered (ruling 2):** yes, labeled
   `single_source_supported` and conservatively framed, never as consensus; a
   core mechanism prefers ≥ 2 independent sources or one review/synthesis.
5. Region granularity: states only, or also NCA climate regions? ---
   **answered (ruling 3):** NCA regions, one pinned scheme with a tracked map
   (`nca_regions_v1.yaml`; source verification pending Kaiyuan); other state
   sets are `multi_state_set`.
6. Still relevant under the new design (table-side patterns depend on them):
   confirmation of the FWI columns (IC-006 -- IC-010); `State` / `NAME`
   (IC-011, IC-012); the FWI percent-change scenario. --- *open; FWI summer
   value patterns are `acceptance_blocked`, state/region patterns provisional,
   percent-change patterns carry `scenario: unstated_in_dictionary`.*

**For GUIDANCE**

7. Gate redefinition. --- **answered (D-041):** PASS WITH ACTIONS; the gate is
   source-independent answerability + deterministic table facts +
   provenance-backed literature + evidence strength + decomposition + human
   acceptance (conditions A--F); C/G/T/S/D audit only.
8. Whether single-source mechanisms may appear if marked. --- **answered**, as 4.

**Not yet decided (needed before the pilot)**

9. **Magnitude class.** --- **answered (ruling 5):** relative terciles among U.S.
   states, disclosed as relative, never an absolute threshold or the sole key;
   implemented as DR-PT-005 with its degeneracy guards (`TABLE_PATTERNS_V1.md`).
10. The sheet's *What ENSURE Is Doing* column. --- **answered (D-041):** field
    `system_task`.
11. The identities of the four 2026-10-28 examples. --- **ids attached** to D-036
    (`C-247866001-01`, `C-199098498-02` with -01/-03, `C-226260658-01`,
    `C-53050065-03`); `C-199098498-03` and `C-53050065-03` are not in
    `softqa_run1` --- flagged to the COORDINATOR.
12. **New:** per-cell percent-change columns are not averaged (D-042, owner;
    for COORDINATOR / GUIDANCE confirmation).
