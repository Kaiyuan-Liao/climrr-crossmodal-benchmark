# Benchmark redesign --- pattern-level open-ended QA (2026-10-29)

Design document for the redesign the mentor directed on 2026-10-29. It is
written from decisions **D-035 -- D-040** in [`DECISION_LOG.md`](DECISION_LOG.md);
where this document and the log disagree, the log governs. Nothing here has been
generated: **no item, pattern, statement or answer in this document comes from a
run**, and every value in §2 is marked illustrative.

**Status.** D-035, D-036, D-037, D-039, D-040 decided; **D-038 (the ladder)
proposed**, for mentor confirmation. Next work package: a pilot of about ten
items (§4), not started.

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

## 2. What an item is (D-037)

An item adopts the field set of the mentor-supplied ENSURE use-case sheet
(`ENSURE_Prompt Use Cases_v3.xlsx`, D-040, [`REFERENCES.md`](REFERENCES.md)),
plus answer-key, provenance and review fields.

| Field | Content |
| --- | --- |
| `use_case` | the rung of the hazard-projection ladder (§3, D-038) |
| `prompt` | open-ended question; names no source |
| `reasoning_modalities` | `Hazard` / `Text` / `Hazard + Text` |
| `key_relationships` | the relationship chain the item exercises (e.g. hazard metric → season → region → scenario → horizon → driver) |
| `evidence_needed` | what a correct answer has to draw on |
| `capability_tested` | what the item adds over lower rungs |
| `desired_output_characteristics` | what a good answer looks like |
| `reference_answer` | the sheet's "illustrative output": the table pattern plus the literature mechanism, in plain language |
| `rubric` | required elements with weights: direction, magnitude class, region, mechanism, scenario/horizon handling, no-overclaim |
| `guardrails` | item-specific limits (e.g. "RCP8.5 is one high-emissions scenario"; "modeled baseline, not observation"; "FWI is fire weather danger, not fire occurrence") |
| `provenance` | table: columns, row-selection rule, derivation rule id, computed values; literature: paper ids, SHA-256, spans, aggregation count |
| `review` | the D-033 lifecycle: `llm_candidate → deterministic_pass → human_review → accepted`, with `rejected_*` exits |

The sheet's column *What ENSURE Is Doing* has no field of its own in D-037 (see
§6).

### 2.1 Worked item --- ILLUSTRATIVE, not generated

> **Every value below is illustrative.** It shows the *shape* of an item. No
> pattern was extracted, no paper was read, no number was computed, and nothing
> here is an answer key. Bracketed `<…>` slots are filled only by the pipeline
> (§4). The FWI columns are `inferred_candidate` (IC-006, IC-008, IC-010) and
> `State` is `inferred_candidate` (IC-012), so an item of this kind **could not
> reach `accepted` today** (D-033 addendum; mentor brief, question 0).

```yaml
# ILLUSTRATIVE --- not generated, not an answer key
item_id: ILLUSTRATIVE-0001
use_case: 3  # Pattern + mechanism (D-038, proposed)
prompt: >-
  How is summer fire weather danger projected to change in California by the
  late 21st century under a high-emissions scenario, and what drives that
  change?
reasoning_modalities: Hazard + Text
key_relationships: >-
  fire weather index (summer) → state → high-emissions scenario → late-century
  horizon → meteorological drivers
evidence_needed: >-
  projected direction and magnitude class of summer fire weather danger for the
  region; the meteorological drivers named across the literature
capability_tested: >-
  joins a projected hazard pattern to its physical mechanism without treating
  fire weather danger as fire occurrence
desired_output_characteristics: >-
  states direction and rough magnitude, names the scenario class and horizon,
  explains the drivers, keeps hazard distinct from fire occurrence and from risk
reference_answer: >-   # shape only
  Summer fire weather danger in California is projected to <direction> by the
  late 21st century under a high-emissions scenario (RCP8.5 is one such
  scenario), a <magnitude class> change relative to a modeled historical
  baseline. <Mechanism sentence(s), each traced to ≥ 2 papers or marked
  single-source.> This describes meteorological fire danger, not whether fires
  occur or what they burn.
rubric:   # shape only; weights are illustrative
  - {element: direction,         weight: <w>, required: "<direction> matches the table pattern"}
  - {element: magnitude_class,   weight: <w>, required: "<magnitude class> matches the table pattern"}
  - {element: region,            weight: <w>, required: "answer is about California / the stated region"}
  - {element: mechanism,         weight: <w>, required: "names <driver cluster(s)> from the literature key"}
  - {element: scenario_horizon,  weight: <w>, required: "treats the result as high-emissions, late-century; does not generalize to all scenarios"}
  - {element: no_overclaim,      weight: <w>, required: "does not equate fire weather danger with fire occurrence, burned area or structure risk"}
guardrails:
  - RCP8.5 is one high-emissions scenario, not the only future.
  - The historical value is a modeled baseline, not an observation.
  - FWI is fire weather danger, not fire occurrence.
provenance:
  table:
    columns: [wildfire_summer_Hist, wildfire_summer_Endc]  # indices 189, 191; inferred_candidate IC-006, IC-008
    row_selection_rule: "State == 'California'"            # State inferred_candidate IC-012
    derivation_rule_id: <DR-TD-003 / DR-TD-005 + magnitude-class rule, not yet defined>
    computed_values: {baseline: <…>, future: <…>, change: <…>, direction: <…>, magnitude_class: <…>}
  literature:
    - cluster_id: <…>
      aggregation_count: <n papers>
      members:
        - {paper_id: <…>, sha256: <…>, json_path: <…>, span: [<start>, <end>], passage: "<verbatim>"}
review:
  status: illustrative   # never entered the lifecycle
  history: []
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

**For the mentor**

1. Does the item schema (§2) match what you want?
2. Review of the first pilot items (next package, about ten).
3. Does the ladder (§3, D-038) fit, or should rungs be added, merged or dropped?
4. May a mechanism supported by a single paper appear in a reference answer if
   it is marked single-source?
5. Region granularity: states only, or also NCA climate regions? Regions need a
   deterministic state → region map and a citable source for it.
6. Still relevant under the new design (table-side patterns depend on them):
   confirmation of the FWI columns (IC-006 -- IC-010); `State` / `NAME`
   (IC-011, IC-012); the FWI percent-change scenario.

**For GUIDANCE**

7. Gate redefinition: the acceptance gate moves from claim-level compatibility
   to deterministic traceability + human review; the bridge is redefined at
   pattern level. Guardrails are requested.
8. Whether single-source mechanisms may appear if marked (same as 4).

**Not yet decided (needed before the pilot)**

9. **Magnitude class** has no derivation rule: class boundaries (and whether
   they are absolute or relative to baseline) must be defined and logged.
10. The sheet's *What ENSURE Is Doing* column is not mapped to a D-037 field.
11. The identities of the four 2026-10-28 examples were not given in the work
    package; they are recorded as a set until named.
