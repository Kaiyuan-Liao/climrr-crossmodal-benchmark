# Project plan --- M0 through M5

Six milestones. Each milestone must pass its gate before the next scientific
stage begins. A milestone is not complete until GUIDANCE accepts its gate
criteria against a report in `reports/milestones/`.

Active milestone: **M0**.

> **[`docs/BLUEPRINT.md`](BLUEPRINT.md) is the project charter.** This file must
> not diverge from it without a logged decision in
> [`DECISION_LOG.md`](DECISION_LOG.md). Where the two disagree, the blueprint
> governs and this file is the defect. Objectives and gate criteria below are
> the blueprint's text, verbatim (blueprint section 8).

---

## M0. Reproducible project foundation *(ACTIVE)*

### Objective

Create a safe, synchronized, and documented local/GitHub/Sophia workspace.

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

For each milestone's required work, deliverables, and schemas, see blueprint
section 8. Those are not duplicated here, to keep a single source of truth.
