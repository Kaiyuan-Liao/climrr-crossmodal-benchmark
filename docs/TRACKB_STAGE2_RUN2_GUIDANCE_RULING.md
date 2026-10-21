# ClimRR Cross-Modal Benchmark — Track B Stage 2 Run 2 GUIDANCE Ruling

**Decision context:** Stage 2 run 2 — family-level diagnostic coverage survey  
**Date:** 2026-10-21  
**Reviewed head:** `work/trackb-run2` @ `ea2f2ea`  
**Base:** `main` @ `d7032de`  
**GUIDANCE status:** PASS WITH ACTIONS

> This ruling accepts Stage 2 run 2 as a diagnostic, adopts three-level coverage reporting as the standing presentation, confirms that unit redesign should use governed concept-map families rather than model-proposed broad families or threshold measures, and pauses Track B until mentor feedback on 2026-10-22. No QA is authorized.

---

## Gate status

**PASS WITH ACTIONS**

Stage 2 run 2 is accepted as a **family-level diagnostic**.

Merge of `work/trackb-run2` @ `ea2f2ea` is authorized after this ruling is recorded.

Rulings:
1. **R1 — Accept run 2 and authorize merge:** Yes.
2. **R2 — Three-level reporting becomes the standing coverage presentation:** Yes.
3. **R3 — Unit redesign should operate at the governed concept-map family level, not model-family or threshold-measure level:** Yes.
4. **R4 — Pause Track B after merge until the October 22 mentor meeting. Do not run another vocabulary/family survey now.**

---

## Current-stage assessment

Track B has answered the question it was designed to answer.

Run 1 established **measure-level lexical coverage**. Run 2 established coverage under broader **model-proposed candidate families**. Existing concept-map vocabulary provides a governed intermediate family level.

The three semantic levels are:

1. **Dictionary measure level** — exact quantity described in the dictionary.
2. **Governed concept-map family level** — human/GUIDANCE-approved family vocabulary; currently available for `fire_weather_index` and `heat_index`.
3. **Model-proposed broad-family level** — exploratory hypotheses only.

Run 2 shows how quickly coverage expands as semantic scope broadens, e.g. precipitation → `hydrology`, Degree Days → `temperature`, FWI → `fire_risk`, and heat-index measures → broad heat-related families. This is useful diagnostically but cannot determine ontology.

---

## Evidence check

### 1. R1 — Accept run 2 and merge

**Approved.**

Run 2 is accepted as:

> **TRACKB-SURVEY-RUN2 — family-level diagnostic coverage survey**

It must not be described as ontology generation.

The normalization machinery is accepted. The fact that N-1…N-7 fired zero times in the real run is not a problem because the rules were predeclared, frozen, tested, and inert when unnecessary.

### 2. Run-2 execution provenance

If Polaris login-node / `conda/2026-10-01 + globus_env` information is retained from Kaiyuan's report, label it:

```text
owner_confirmed
```

rather than run-derived.

Keep:

```text
Python patch version: unknown
```

Do not copy the run-1 Python version into run 2.

### 3. R2 — Standing three-level coverage reporting

**Approved.**

#### Level 1 — Dictionary-measure diagnostic coverage

Corresponds to the specific quantity represented in the data dictionary and run-1 search terms.

A zero means no direct lexical matches under the current measure representation and search rules. It does **not** mean the literature contains no relevant work.

#### Level 2 — Governed concept-map family coverage

Only terms already accepted through concept-map governance belong here.

This is the appropriate family level for the upcoming unit-granularity diagnostic.

#### Level 3 — Model-proposed candidate-family coverage

Label:

> **candidate-family diagnostic coverage**

Never call this family prevalence, approved family coverage, benchmark relevance, or evidence for unit selection.

**Standing rule:** do not rank concepts across these three levels as though the counts are semantically comparable.

### 4. R3 — Granularity for Track A-next

**Confirmed: use the concept-map family level.**

The immediate redesign candidates should remain:

```text
fire_weather_index
heat_index
```

Do not use threshold-specific measures as the primary redesign level, and do not use model-generated broad families such as `fire_risk`, `hydrology`, or `extreme_heat_days`.

For the other five discussion candidates — temperature, precipitation, wind speed, dry spell, and degree days — there is currently no approved concept-map family. Do not build redesigned units around model-proposed families for these concepts yet.

### 5. What run 2 says about model families

Model families remain hypotheses.

Examples:
- precipitation → `hydrology` is broader than precipitation;
- Degree Days → `temperature` does not preserve the degree-day metric;
- FWI → `fire_risk` / `fire_danger` is related but not equivalent;
- threshold heat index → `extreme_heat_days` relies on broad phrases such as `hot days`.

Therefore none of these model families should enter concept-map governance automatically.

### 6. R4 — Further Track B run now?

**No. Pause Track B after merge until the October 22 mentor meeting.**

The next uncertainty is scientific/governance, not computational:

> Which quantity families does the mentor consider appropriate for redesigned table-side units?

A further automated run now would mostly create more ungoverned vocabulary before the project knows which concepts are worth governing.

---

## Scientific risks

1. **Treating model-family coverage as validation.** Broadening a metric can inflate coverage without supporting the exact measure.
2. **Choosing ontology to maximize yield.** Higher counts do not imply better scientific semantics.
3. **Concept-map family level becoming too broad.** Any new family needs explicit review.
4. **Conflating family and measure evidence.** Heat-index-family support does not equal support for 95/105/115/125°F thresholds.
5. **Using run 2 to select units.** Run 2 is diagnostic, not a selection mechanism.
6. **Premature Track B expansion.** More candidate-family generation before mentor feedback would increase ontology debt.

---

## Required actions

1. Record **Stage 2 run 2 PASS WITH ACTIONS — diagnostic only**.
2. Authorize merge of `work/trackb-run2` @ `ea2f2ea` after ruling bookkeeping.
3. Preserve run 1 and run 2 manifests, driver v4 hash, prompt F hash, and normalization-table hash.
4. Preserve all 14 run-2 assignments as `candidate_family`.
5. Do not promote any candidate family into `concept_map.yaml`.
6. Adopt the standing three-level coverage presentation:
   - dictionary measure;
   - governed concept-map family;
   - model-proposed candidate family.
7. Never combine or rank those three levels as semantically equivalent.
8. Do not attribute Level-2 or Level-3 coverage to a Level-1 threshold measure.
9. For Track A-next, use the **governed concept-map family** as the redesign semantic level.
10. Limit the first redesign diagnostic to already governed families unless a separate family-governance decision is made.
11. Treat `fire_weather_index` and `heat_index` as the immediate redesign candidates.
12. Do not treat `fire_risk`, `fire_danger`, `hydrology`, `temperature-for-degree-days`, `extreme_heat_days`, or `heat_wave_days` as approved unit families.
13. Label run-2 host/environment facts as `owner_confirmed` when not present in run output.
14. Keep Python patch version `unknown`.
15. Pause Track B after merge until mentor feedback on 2026-10-22.
16. Do not launch another family-vocabulary run before that feedback.

---

## Decisions for Kaiyuan or mentor

| Question | Ruling |
|---|---|
| R1 Stage 2 run 2 | **PASS WITH ACTIONS — diagnostic accepted** |
| Merge `work/trackb-run2` | **Authorized after ruling bookkeeping** |
| R2 three-level coverage reporting | **Approved as standing reporting structure** |
| Level 1 | **Dictionary-measure diagnostic coverage** |
| Level 2 | **Governed concept-map family coverage** |
| Level 3 | **Model-proposed candidate-family diagnostic coverage** |
| Rank concepts using model-family counts | **No** |
| Use model-family counts for unit selection | **No** |
| R3 redesigned units at threshold level | **No, not as primary redesign** |
| R3 redesigned units at model-family level | **No** |
| R3 redesigned units at concept-map family level | **Yes** |
| Immediate redesign families | **`fire_weather_index`, `heat_index`** |
| Automatically govern the other five discussion families | **No** |
| R4 additional Track B run before mentor meeting | **No — pause** |
| Concept-map changes now | **No** |
| QA | **Still not authorized** |

For the October 22 mentor discussion, the key scientific question is:

> **Should a benchmark unit represent the exact ClimRR metric, or is a governed family-level quantity such as “heat index” / “Fire Weather Index” an acceptable table-side semantic object when the exact measure and scenario remain preserved as provenance?**

---

## Next bounded objective

### Track B

**Pause/close Track B after merge.**

No run 3.

Reopen Track B only if:
- mentor approves a new candidate family for redesign;
- GUIDANCE needs vocabulary evidence to govern one of the five ungoverned families;
- a redesigned unit requires a new concept-map family.

At that point, the next task should be a **governance package**, not another unconstrained model-family survey.

### Track A-next

Continue with the authorized **Unit-Granularity Diagnostic**, initially centered on:

```text
fire_weather_index
heat_index
```

Use:

> **concept-map family = semantic comparison level**

while keeping the specific table metric and scenario as provenance.

Conceptually:

```text
unit.family = heat_index
unit.metric = days_above_105F
unit.metric_status = provenance_specific_measure
unit.scenario = RCP8.5
unit.scenario_role = provenance
unit.geography = deterministic_supported_aggregate
```

A literature claim may then be evaluated at the `heat_index` family level without pretending that it matches the exact threshold, scenario, or time horizon.

---

## Acceptance criteria

Track B may be considered closed for this diagnostic phase when:

1. Run 2 is merged from reviewed head `ea2f2ea`.
2. Run 1 remains byte-identical.
3. Run 2 remains explicitly diagnostic.
4. All 14 assignments remain `candidate_family`.
5. No model family enters the concept map.
6. The three coverage levels are documented separately.
7. Measure counts remain attached only to measures.
8. Concept-map family counts use only approved vocabulary.
9. Candidate-family counts remain labeled model hypotheses.
10. No ranking combines the three levels.
11. No candidate-family count determines unit selection.
12. `fire_weather_index` and `heat_index` remain distinct from broader `fire_risk` / extreme-heat concepts.
13. Threshold heat-index measures remain distinct from the heat-index family.
14. No claim is made that zero measure-level retrieval means no literature exists.
15. Run-2 host/environment provenance distinguishes run-recorded from owner-confirmed facts.
16. Python patch version remains `unknown`.
17. No additional Track B model run occurs before mentor feedback.
18. Track A redesign uses only governed family concepts initially.
19. Current exact prototypes remain controls.
20. No QA is generated.

---

## Do not do yet

Do not add `hydrology` to the concept map because precipitation produced high coverage.

Do not map Degree Days to generic `temperature`.

Do not replace Fire Weather Index with generic `fire risk` or `fire danger`.

Do not replace heat-index threshold measures with `hot days`, `heat-wave days`, or generic extreme heat.

Do not treat model-family coverage as literature support for the underlying dictionary measure.

Do not rank the seven discussion families by run-2 counts.

Do not run another LLM family survey before the mentor meeting.

Do not build units for the five families that currently lack concept-map governance.

Do not generate QA.

Track B has now supplied the diagnostic it needed to supply:

> **Coverage grows dramatically as representation moves from exact measure → governed family → broad model family, but only the governed family level currently has the semantic control required for benchmark construction.**

That makes the next move a **scientific unit-design decision**, not another retrieval experiment.
