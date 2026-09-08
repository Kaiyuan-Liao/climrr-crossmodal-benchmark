# ClimRR Cross-Modal Benchmark
## Project Blueprint, Workflow Contract, and GUIDANCE Handoff

Version: 1.0  
Prepared for: Kaiyuan Liao  
Initial scope: project setup through validated links between table-derived scientific phenomena and literature claims  

---

## 1. Project overview

This project aims to construct a scientifically meaningful cross-modal question-answering benchmark from two independently collected evidence sources:

1. A large ClimRR CSV containing spatially resolved climate projections, hazard indicators, scenario and time-horizon fields, and selected social or resilience-related variables.
2. A corpus of scientific literature collected using related domain concepts such as climate, wildfire, heat, precipitation, and resilience.

Unlike many table-text QA benchmarks, the table and papers are not directly aligned. A paper does not identify a particular CSV row, and a CSV row is not drawn from a paper. The intended benchmark should also avoid simple search-style questions in which the text merely tells a model where to retrieve a value from the table.

The core research problem is therefore:

> How can we discover and validate a defensible scientific phenomenon shared by independently collected tabular and textual evidence, and then use that link to support genuinely cross-source reasoning?

The initial project stops after producing and validating those table-to-literature links. It does not yet generate the final benchmark at scale.

---

## 2. Conceptual starting point from XModBench

XModBench builds its benchmark around aligned tri-modal semantic instances. The same concept or event is represented through text, vision, and audio. Depending on the source task, the authors extract modalities already present in existing datasets, synthesize or generate missing representations, or collect additional materials from the web. Task-specific templates then create multiple-choice questions, which are instantiated across six context-to-candidate modality directions. An LLM refines phrasing without changing semantics, followed by automated filtering and human verification.

Its high-level principle is useful:

> Define or establish the semantic relationship before generating the questions.

However, its exact construction pipeline does not directly solve this project. XModBench begins with a known semantic item and constructs aligned representations:

`known semantic item → aligned modality realizations`

This project begins with independently collected modalities and must discover the relationship:

`independent table + independent literature → shared scientific phenomenon → validated semantic bridge`

The semantic bridge, rather than QA generation, is the central technical object of the current stage.

---

## 3. Known data facts and scientific cautions

The available `FullData.csv` has been preliminarily inspected.

### Basic profile

| Property | Current understanding |
| --- | --- |
| Rows | 62,834 |
| Columns | 275 |
| Current file size | approximately 48 MB |
| Spatial structure | grid identifiers plus geographic and Census-related fields |
| Time structure | historical, mid-century, and end-century fields |
| Scenarios | RCP4.5 and RCP8.5 where available |
| Climate concepts | temperature, precipitation, dry periods, wind, heating/cooling degree days, heat index, and fire-weather-related variables |
| Other fields | selected socioeconomic and resilience-related attributes |

### Non-negotiable interpretation cautions

1. ClimRR historical fields represent modeled historical baselines, not direct observational records.
2. Columns whose names contain `wildfire` represent Fire Weather Index information. They must not be described as wildfire counts, ignitions, burned area, or observed wildfire occurrence.
3. Census identifiers such as GEOID must be treated as strings so leading zeros are preserved.
4. Sentinel-like values, truncated field names, duplicate-looking identifiers, missing values, units, and aggregation rules must be resolved from authoritative metadata before scientific interpretation.
5. A visualization generated from the CSV is another representation of ClimRR evidence, not an independent evidence source.
6. Grid-to-county, state, or scientific-region aggregation is provisional until the correct mapping and aggregation method are documented.
7. RCP and SSP scenarios must not be treated as numerically interchangeable without scientific justification.
8. LLMs must not be the primary mechanism for converting raw numerical rows into scientific claims. Deterministic or explicitly specified computation should establish the tabular facts first.

### Literature input

The literature corpus will be stored externally on the ALCF Sophia server. Its path will be provided later. The repository should not create or populate a literature-data subfolder during initial setup. Once the path is available, record it in a local path configuration and create a tracked manifest containing stable identifiers, filenames, checksums where practical, and corpus-level provenance. Do not commit the source PDFs unless explicitly approved later.

---

## 4. Roles and authority

The workflow uses three distinct roles. Keeping these roles separate is important for avoiding both high-level drift and low-level micromanagement.

### 4.1 GUIDANCE: fresh GPT chat

Primary responsibility:

* Protect the scientific direction and milestone logic.
* Review milestone reports and evidence.
* Decide whether a milestone passes its gate.
* Identify conceptual risks, missing validation, and decisions that require Kaiyuan or mentor input.
* Define the next bounded high-level objective and its acceptance criteria.

GUIDANCE should not:

* Write implementation code.
* Dictate individual shell commands unless a command-level issue materially affects scientific validity or reproducibility.
* Redesign the entire pipeline in response to one incidental technical problem.
* Approve a milestone based only on a narrative summary when supporting artifacts are missing.
* Allow QA generation to begin before the semantic bridges are scientifically and procedurally defensible.

### 4.2 COORDINATOR: Claude chat

Primary responsibility:

* Translate GUIDANCE decisions into bounded work packages for Claude Code.
* Lead intermediate reasoning, inspect implementation evidence, and determine whether a task is ready for milestone review.
* Maintain project state, decision records, and milestone reports.
* Separate scientific decisions from implementation choices.
* Escalate to GUIDANCE only when a milestone gate is ready or when a decision changes project scope, data meaning, or evaluation validity.

COORDINATOR should not:

* Pretend an ambiguous data field has a known meaning.
* silently change an approved scientific rule.
* Ask the coding agent to generate benchmark questions directly from raw rows and arbitrary papers.
* Fill reports with implementation chronology while omitting evidence, limitations, and unresolved decisions.

### 4.3 EXECUTOR: Claude Code in local VS Code

Primary responsibility:

* Create and maintain the repository.
* Implement scripts, tests, configurations, and reproducible analyses.
* Run lightweight local checks.
* Prepare server-ready commands and configurations for large-scale execution.
* Produce machine-readable artifacts and concise reports required by the current work package.

EXECUTOR should not:

* Change project scope or scientific definitions without an explicit decision from COORDINATOR, GUIDANCE, or Kaiyuan.
* Modify the raw CSV in place.
* commit secrets, machine-specific absolute paths, source literature PDFs, or large generated outputs.
* Treat a successful script exit as evidence that the scientific result is valid.

### 4.4 Kaiyuan

Kaiyuan owns final decisions, provides missing paths and metadata, communicates mentor feedback, approves meaningful scope changes, and decides when a milestone gate is accepted if GUIDANCE identifies alternatives or residual risk.

---

## 5. GitHub and local/server operating model

Use a private GitHub repository as the authoritative source for code, tracked documentation, configuration templates, tests, and small reproducibility artifacts.

### Recommended synchronization policy

Adopt a single-writer model:

* The local clone is the only clone that authors commits and pushes to GitHub.
* The Sophia clone pulls a specific commit for execution.
* Large run outputs remain on Sophia and are not committed.
* Small summaries, manifests, logs, and milestone evidence are copied back to the local machine, reviewed, and committed from the local clone.
* Every server run records the exact Git commit SHA, configuration, environment information, data checksum, and output path.

This policy avoids diverging histories and unclear ownership when both local and server copies exist.

### Branching and milestones

* `main`: accepted, reproducible project state.
* `work/<milestone>-<short-task>`: short-lived local work branches.
* Merge only after the relevant checks pass.
* Tag accepted milestone states as `m0-setup`, `m1-data-grounding`, and so on.

Do not create an elaborate branching system for the initial project.

### Raw CSV handling

`FullData.csv` is approximately 48 MB. It is under GitHub's normal per-file limit, but repeated commits would unnecessarily enlarge repository history.

Preferred rule:

1. Check whether Git LFS is available locally, on Sophia, and for the private GitHub repository.
2. If available, store `data/raw/FullData.csv` with Git LFS.
3. If LFS is unavailable, a single ordinary Git commit is acceptable because the file is under the limit, but the file must then be treated as immutable.
4. Record SHA-256, byte size, row count, column count, source, acquisition date if known, and interpretation notes in `data/MANIFEST.md` or a machine-readable companion.
5. Any corrected or updated dataset must be a new version with a new filename and manifest entry. Never silently replace the original bytes.

### Files that must not enter Git history

* API keys, tokens, credentials, or private connection details
* machine-specific path configurations
* literature PDFs unless explicitly approved
* large model outputs, embeddings, caches, or intermediate arrays
* server environments or copied package installations
* temporary notebooks and exploratory outputs without a reproducibility purpose

---

## 6. Recommended repository structure

The initial structure should remain small and purposeful.

```text
climrr-crossmodal-benchmark/
├── README.md
├── CLAUDE.md
├── .gitignore
├── .gitattributes
├── pyproject.toml or environment.yml
│
├── config/
│   ├── project.yaml
│   └── local_paths.example.yaml
│
├── data/
│   ├── README.md
│   ├── MANIFEST.md
│   └── raw/
│       └── FullData.csv
│
├── docs/
│   ├── PROJECT_PLAN.md
│   ├── PROJECT_STATE.md
│   ├── DECISION_LOG.md
│   ├── DATA_NOTES.md
│   └── REPORT_TEMPLATE.md
│
├── src/
├── scripts/
├── tests/
│
├── reports/
│   ├── milestones/
│   └── runs/
│
└── artifacts/
    ├── profiles/
    ├── phenomena/
    ├── claims/
    └── bridges/
```

The `artifacts/` directory may contain small, reviewable outputs. Large or readily reproducible outputs should be ignored by Git and referenced through manifests. Do not create a repository subfolder for the external literature corpus during initial setup.

---

## 7. Persistent documentation contract

### `README.md`

Human entry point. It should explain the project goal, current scope, basic setup, data location policy, and how to reproduce the latest accepted stage.

### `CLAUDE.md`

Persistent instructions for Claude Code. It should contain:

* role boundaries;
* raw-data immutability;
* required testing and validation;
* prohibition on inventing data semantics;
* local/server synchronization policy;
* reporting requirements;
* prohibition on committing secrets, machine paths, large outputs, or literature PDFs;
* requirement to read `PROJECT_STATE.md` and the active milestone report before work;
* requirement to stop and escalate when a scientific decision is missing.

### `docs/PROJECT_PLAN.md`

The stable roadmap and milestone acceptance criteria. Change only through an explicit, logged decision.

### `docs/PROJECT_STATE.md`

The concise living state. It should contain:

* current milestone and status;
* active bounded task;
* latest accepted Git commit;
* completed outputs;
* current blockers;
* next review event;
* links to the relevant report and artifacts.

Update after every accepted work package. Keep it concise; do not use it as a chronological diary.

### `docs/DECISION_LOG.md`

Append-only record for decisions that affect scientific meaning, scope, interfaces, reproducibility, or milestone acceptance. Use stable IDs such as `D-001`.

Each entry should include:

* date;
* decision;
* rationale;
* alternatives considered;
* consequences;
* owner or approver;
* affected files or milestones.

Do not log routine implementation details.

### `docs/DATA_NOTES.md`

Authoritative working record of field meanings, units, time windows, scenarios, sentinel values, aggregation assumptions, geography, and unresolved metadata questions. Distinguish verified facts from provisional interpretations.

### `reports/milestones/`

One report per milestone. The report may be revised while the gate is under review. Once accepted, freeze it and tag the repository state.

### `reports/runs/`

One concise record per meaningful local or Sophia run. Use a timestamped run ID. Include commit SHA, command or entry point, config, environment, data checksum, output path, result summary, and pass/fail status.

---

## 8. Milestone roadmap

The initial project contains six milestones, M0 through M5. Each milestone must pass its gate before the next scientific stage begins.

## M0. Reproducible project foundation

### Objective

Create a safe, synchronized, and documented local/GitHub/Sophia workspace.

### Required work

* Create the private GitHub repository and local clone.
* Create the initial repository structure and persistent documentation.
* Place the CSV under the approved Git/LFS policy and record its checksum and basic inventory.
* Establish the local-authoring and Sophia-execution synchronization flow.
* Add a minimal environment specification, smoke test, and run-record mechanism.
* Verify that Sophia can pull a pinned commit and read the expected data without changing it.
* Do not add the literature corpus yet.

### Deliverables

* initial repository;
* `CLAUDE.md`;
* project plan, state, decision log, data notes, and report template;
* CSV manifest and checksum;
* local smoke-test record;
* Sophia synchronization smoke-test record;
* `reports/milestones/M0_SETUP_REPORT.md`.

### Gate criteria

M0 passes only if:

1. The raw CSV is byte-identical locally and on Sophia.
2. The repository can be cleanly cloned or pulled in both environments.
3. No secrets or machine-specific paths are tracked.
4. A run can be tied to a precise commit, configuration, environment, and data checksum.
5. Project state and role instructions are sufficient for a new coding-agent session to resume safely.

### Explicit non-goals

No climate-variable interpretation, aggregation, literature processing, embedding generation, or QA construction.

---

## M1. Data grounding and metadata audit

### Objective

Determine what the CSV actually contains and which fields can be interpreted safely.

### Required work

* Generate a reproducible schema and quality profile.
* Identify identifiers, geography fields, climate variables, units, time windows, scenarios, derived columns, missingness, constant fields, suspicious values, and duplicated or truncated names.
* Locate authoritative metadata or record missing metadata questions.
* Verify the meaning of fire-weather, heat-index, precipitation, temperature, and selected resilience fields before using them.
* Separate verified metadata from inferred or unresolved interpretations.

### Deliverables

* machine-readable schema profile;
* human-readable data audit;
* initial variable inventory and metadata-status table;
* unresolved metadata request for mentor or data owner;
* `reports/milestones/M1_DATA_GROUNDING_REPORT.md`.

### Gate criteria

M1 passes only if:

1. Every field selected for the pilot has a documented meaning, unit, time horizon, scenario, missing-value policy, and provenance status.
2. No unresolved identifier or sentinel-value issue can silently corrupt the pilot.
3. The report clearly distinguishes verified facts from hypotheses.
4. The mentor-facing metadata questions are specific and actionable.

### Explicit non-goals

No full phenomenon extraction and no literature matching.

---

## M2. Canonical semantic representation

### Objective

Define a shared representation that allows numerical ClimRR patterns and scientific literature claims to be compared without pretending they are directly aligned.

### Table-side phenomenon schema

A provisional table-derived phenomenon record should contain at least:

* phenomenon ID;
* source data version and row/group provenance;
* geographic unit and geographic hierarchy;
* climate or hazard concept;
* metric and unit;
* season;
* baseline period;
* future period;
* scenario;
* baseline and future summary values;
* absolute and/or relative change;
* direction of change;
* magnitude category and the rule used to assign it;
* aggregation method;
* uncertainty or coverage fields;
* natural-language description derived from the structured record;
* metadata-confidence status.

### Literature-side claim schema

A provisional literature claim record should contain at least:

* claim ID and document ID;
* exact evidence span and location in the source;
* geographic scope;
* climate or hazard concept;
* direction or relationship;
* season, time horizon, and scenario when stated;
* mechanism;
* impact or vulnerability context when stated;
* claim type, such as projection, observation, mechanism, or impact;
* extraction confidence;
* human-review status.

### Required work

* Define a conservative climate-concept vocabulary that connects dataset field names to literature language.
* Define the geography hierarchy from grid to literature-friendly regions.
* Define time-horizon and scenario normalization rules.
* Define magnitude categories using explicit quantitative or domain rules.
* Create several hand-worked examples from raw rows through canonical records.
* Document forbidden inferences, including FWI-to-wildfire-occurrence substitution.

### Deliverables

* phenomenon schema;
* claim schema;
* controlled vocabulary or ontology draft;
* geography and scenario normalization rules;
* hand-worked examples;
* `reports/milestones/M2_SEMANTIC_REPRESENTATION_REPORT.md`.

### Gate criteria

M2 passes only if:

1. The representation preserves provenance back to exact tabular cells or literature spans.
2. Structured fields can express the planned humid-heat and fire-weather pilots without unsupported inference.
3. Geography, time, scenario, and concept compatibility can be evaluated explicitly.
4. Natural-language descriptions are generated from structured facts rather than used as the factual source.

---

## M3. Table-derived phenomenon discovery pilot

### Objective

Produce a small, auditable collection of meaningful ClimRR phenomena at spatial scales that scientific literature can plausibly discuss.

### Recommended pilot scope

Begin with two phenomenon families, subject to mentor feedback:

1. Humid heat or heat-index change.
2. Fire-weather change, carefully described through FWI rather than wildfire occurrence.

### Required work

* Implement deterministic extraction and aggregation from the approved fields.
* Generate phenomena at one or two approved geographic levels rather than every possible level.
* Define and justify salience or magnitude criteria.
* Preserve exact source rows, computations, coverage, and aggregation rules.
* Review a stratified sample covering strong increases, weak changes, decreases if present, and edge cases.
* Reject or flag cases with insufficient coverage or ambiguous metadata.

### Deliverables

* structured phenomenon records;
* compact evidence slices for each record;
* computation and validation tests;
* reviewed sample with error categories;
* `reports/milestones/M3_TABLE_PHENOMENA_REPORT.md`.

### Gate criteria

M3 passes only if:

1. A reviewer can reproduce each phenomenon from the cited table evidence.
2. Descriptions remain within what the metrics support.
3. Geographic aggregation is documented and coverage-aware.
4. The pilot yields enough scientifically useful variation for literature matching.
5. Known failure modes and rejection rules are documented.

---

## M4. Literature ingestion and structured claim extraction pilot

### Objective

Turn a small, traceable subset of the external literature corpus into structured claims compatible with the table phenomenon schema.

### Preconditions

* Kaiyuan provides the Sophia literature path.
* The source corpus remains external to Git unless separately approved.
* A tracked corpus manifest is created.

### Required work

* Inventory documents and establish stable document identifiers.
* Parse text while preserving page, section, paragraph, or other evidence locations.
* Retrieve passages relevant to the approved pilot phenomena.
* Extract structured claims using a constrained schema.
* Preserve exact supporting spans and distinguish explicit claims from inferred interpretations.
* Review a stratified sample for extraction accuracy and overclaiming.
* Record documents or passages that are topically similar but lack a usable scientific claim.

### Deliverables

* literature corpus manifest;
* structured claim records;
* exact evidence spans;
* extraction and review statistics;
* error taxonomy;
* `reports/milestones/M4_LITERATURE_CLAIMS_REPORT.md`.

### Gate criteria

M4 passes only if:

1. Every retained claim has an exact evidence span.
2. Geography, phenomenon, direction, time, scenario, mechanism, and claim type are explicit or marked missing rather than guessed.
3. The extraction process distinguishes relevance from evidentiary support.
4. Human review shows an acceptable level of factual faithfulness for bridge discovery.

---

## M5. Semantic bridge discovery and validation

### Objective

Create a validated bridge dataset linking table-derived phenomena to compatible literature claims.

### Matching principle

Use structured compatibility before generic semantic similarity. A provisional score may combine:

* geographic compatibility;
* climate or hazard concept compatibility;
* trend or relationship compatibility;
* season compatibility;
* time-horizon compatibility;
* scenario compatibility;
* claim-type compatibility;
* embedding or LLM-based semantic similarity.

The structured dimensions should dominate. A generic paper about climate and wildfire must not match every FWI phenomenon simply because the vocabulary is similar.

### Bridge relation labels

At minimum, distinguish:

* compatible or supporting;
* potentially contradictory;
* related but insufficient for comparison;
* incompatible;
* uncertain and requires domain review.

Do not force every semantically related pair into agreement.

### Required work

* Generate candidate pairs using transparent structured filters.
* Use embeddings or an LLM only as a secondary ranking or interpretation layer.
* Preserve table provenance, paper evidence, scores, rules, and rejection reasons.
* Human-review a stratified sample, including high-scoring pairs, borderline pairs, and hard negatives.
* Measure precision of accepted bridges and characterize why false matches occur.
* Identify which bridge types can later support genuinely compositional QA.

### Deliverables

* candidate bridge dataset;
* accepted and rejected bridge records;
* bridge-scoring configuration;
* reviewed sample and error analysis;
* examples ready for mentor inspection;
* `reports/milestones/M5_BRIDGE_VALIDATION_REPORT.md`.

### Gate criteria

M5 passes only if:

1. Accepted bridges are scientifically defensible and traceable to both sources.
2. Structured compatibility and semantic similarity are separately visible.
3. The validation sample includes hard negatives and disagreement cases.
4. The report estimates bridge precision and documents limitations.
5. At least some accepted bridges support a clear division of evidentiary roles: the table identifies or quantifies a pattern, while the paper explains, contextualizes, qualifies, or provides criteria for interpreting it.

### Stop point

After M5, pause for mentor review before designing or generating the final QA benchmark.

---

## 9. Milestone reporting and review protocol

Every milestone report should use the same structure.

### Required report fields

1. Milestone ID and title
2. Objective
3. Repository commit SHA
4. Data version and checksums
5. Environment and execution location
6. Work completed
7. Deliverables and exact file paths
8. Methods and rules that affect scientific meaning
9. Results with compact tables or examples
10. Validation performed
11. Failures, rejected cases, and known limitations
12. Deviations from the approved plan
13. Open decisions and mentor questions
14. Proposed gate status
15. Proposed next bounded objective

The report must include evidence, not only a statement that tasks completed.

### Packet sent to GUIDANCE

For each gate, Kaiyuan should send:

* the milestone report;
* current `PROJECT_STATE.md`;
* relevant new entries from `DECISION_LOG.md`;
* only the key artifacts required to verify the claims;
* any explicit questions from COORDINATOR.

Do not send the full repository or every run log unless GUIDANCE requests them.

### Required GUIDANCE response format

GUIDANCE should reply with:

1. **Gate status:** `PASS`, `PASS WITH ACTIONS`, `REVISE`, or `BLOCKED`.
2. **Current-stage assessment:** what is established and what is not.
3. **Evidence check:** whether the report supports its claims.
4. **Scientific risks:** issues affecting validity, provenance, or interpretation.
5. **Required actions:** only actions necessary for the gate or next stage.
6. **Decisions for Kaiyuan or mentor:** choices GUIDANCE should not make silently.
7. **Next bounded objective:** one high-level work package for COORDINATOR.
8. **Acceptance criteria:** observable conditions for the next review.
9. **Do not do yet:** premature work that should remain out of scope.

GUIDANCE should avoid rewriting the entire implementation plan unless the evidence invalidates the approved direction.

---

## 10. Decision discipline

Use the following categories.

### Scientific decisions

Examples: interpretation of a field, geographic aggregation, phenomenon definition, bridge relation, validation threshold, pilot scope. These require GUIDANCE review and, when consequential, Kaiyuan or mentor approval.

### Interface decisions

Examples: phenomenon-record schema, claim schema, configuration format, provenance contract. COORDINATOR may propose them, but changes affecting later milestones must be logged.

### Implementation decisions

Examples: package choice, function decomposition, test organization, command-line interface. EXECUTOR and COORDINATOR may decide these unless they change the scientific result.

### Incidental issues

Examples: formatting, a broken local path, a dependency warning. Resolve locally when safe; do not escalate every incidental issue to GUIDANCE.

When uncertain, ask whether the choice changes what a result means. If yes, treat it as scientific or interface-level.

---

## 11. Immediate next action: M0 setup

The first Claude COORDINATOR session should begin with M0 only. It should ask Kaiyuan for the minimum unresolved operational inputs:

* private GitHub repository name or URL;
* desired local project path;
* desired Sophia project path;
* whether Git LFS is available and approved;
* preferred Python environment manager if one already exists.

It should then prepare a bounded setup plan for Claude Code. M0 must not perform climate analysis beyond verifying the CSV inventory and checksum.

### Prompt for the Claude COORDINATOR chat

```text
You are the COORDINATOR for a new research project that will build a cross-modal benchmark from a ClimRR CSV and an independently collected scientific-literature corpus. You do not directly write the implementation. You lead the intermediate work, convert approved scientific milestones into bounded instructions for a Claude Code agent running locally in VS Code, inspect its reports and evidence, maintain project state, and escalate milestone-level decisions to me and a separate GUIDANCE chat.

Read the attached project blueprint completely and treat its role boundaries, milestone gates, scientific cautions, Git policy, and reporting contract as authoritative unless I explicitly approve a change.

We are starting only with M0: Reproducible project foundation. The local machine will hold the authoring clone. A private GitHub repository will be the authoritative tracked source. The ALCF Sophia server will be an execution clone that pulls pinned commits. FullData.csv is approximately 48 MB and must be stored under the approved Git LFS or immutable ordinary-Git policy with a checksum and manifest. The literature corpus path will be provided later and must not be added during M0.

First, briefly restate your role and the M0 success conditions. Then ask me only for the unresolved repository name or URL, local path, Sophia path, Git LFS availability or preference, and environment-manager preference. After I answer, produce the first bounded task prompt for Claude Code. Do not begin M1 analysis, literature ingestion, embeddings, semantic matching, or QA generation.
```

---

## 12. Anticipated later phases, not yet authorized

The following steps are deliberately deferred until M5 passes:

* define final QA families, likely including pattern-to-explanation and claim-to-region identification;
* construct compositional answers from a table-derived intermediate and a literature-derived intermediate;
* create semantically challenging distractors;
* test table-only, text-only, and table-plus-text performance to detect unimodal shortcuts;
* add support, contradiction, and insufficient-evidence questions;
* consider table-versus-graph representation consistency inspired by XModBench;
* incorporate socioeconomic vulnerability or compound-risk reasoning;
* scale generation and perform expert validation;
* release benchmark splits and evaluation harnesses.

These are useful future directions, but beginning them before bridge validation would make the project harder to audit and could hide weak source alignment behind fluent generated questions.

---

## 13. Fresh GPT GUIDANCE takeover prompt

Send this document together with the following prompt to a fresh GPT chat when transferring the GUIDANCE role.

```text
You are taking over as the high-level GUIDANCE agent for the ClimRR Cross-Modal Benchmark project. Read the attached project blueprint completely before responding. Treat it as the current approved project charter unless I explicitly revise a decision.

Project goal:
We have a 62,834-row, 275-column ClimRR CSV and a separately collected scientific-literature corpus. They share a domain but are not directly aligned. We ultimately want a multimodal QA benchmark whose questions require meaningful reasoning across tabular evidence and literature, rather than simple search or value lookup. The current authorized scope stops after we discover and validate semantic bridges between table-derived scientific phenomena and literature claims.

Your role:
You protect the scientific direction, review milestone reports and key evidence, issue milestone gate decisions, identify conceptual risks and decisions requiring my or my mentor's input, and define the next bounded high-level objective with acceptance criteria. You do not write code or micromanage routine implementation. A Claude COORDINATOR chat translates your decisions into work packages, and a Claude Code agent implements them locally. The ALCF Sophia server is used for larger executions.

Required operating behavior:
1. Base judgments on milestone reports and supporting artifacts, not confidence or narrative alone.
2. Use the gate outcomes PASS, PASS WITH ACTIONS, REVISE, or BLOCKED.
3. Separate scientific decisions, interface decisions, implementation choices, and incidental issues.
4. Preserve provenance from every table phenomenon to exact source rows and computations, and from every literature claim to exact evidence spans.
5. Do not allow LLM-generated descriptions to replace deterministic numerical analysis.
6. Never equate Fire Weather Index with wildfire occurrence, and remember that ClimRR historical values are modeled baselines.
7. Do not authorize QA generation before M5 bridge validation passes.
8. Keep recommendations high level and bounded. Do not redesign the complete project after every report.

For every milestone review, respond with exactly these sections:
Gate status
Current-stage assessment
Evidence check
Scientific risks
Required actions
Decisions for Kaiyuan or mentor
Next bounded objective
Acceptance criteria
Do not do yet

Current state:
The project is beginning at M0, Reproducible project foundation. No data interpretation, phenomenon extraction, literature processing, bridge matching, or QA generation has been authorized yet.

In your first response, briefly confirm your understanding of the project, state the M0 gate criteria in your own words, and tell me what M0 report and evidence packet you will expect. Do not generate implementation commands or expand the project scope.
```

---

## 14. Final operating principle

The project should move through three distinct layers:

```text
Raw sources
    ↓
Auditable table phenomena and literature claims
    ↓
Validated semantic bridges
    ↓
Future cross-modal QA construction
```

The central discipline is simple:

> Build and validate the bridge before generating the benchmark.

