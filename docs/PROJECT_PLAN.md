# Project plan --- M0 through M5

Six milestones. Each has an objective (summarised) and **gate criteria**. A
milestone is not complete until GUIDANCE accepts its gate criteria against a
report in `reports/milestones/`.

Active milestone: **M0**.

> **Provenance warning --- read before relying on M1--M5 criteria.**
>
> **M0's gate criteria below are the blueprint text, verbatim** (corrected
> 2026-09-08; see decision D-005).
>
> **M1--M5's are not.** The blueprint's M1--M5 text was never supplied to the
> EXECUTOR, which drafted those criteria from the work package's summary of the
> milestone objectives. They are a reasonable reading, not a transcription, and
> they have not been checked against the blueprint by anyone. **Replace each
> with the blueprint text before the corresponding milestone opens**, and do
> not treat them as authoritative in the meantime. Tracked as an open item in
> `reports/milestones/M0_SETUP_REPORT.md` field 13.

---

## M0 --- Reproducible project foundation *(ACTIVE)*

**Objective.** Stand up a repository that any collaborator, or a future
session with no memory of this one, can pick up and reproduce: fixed structure,
persistent documentation, pinned environment, immutable raw data with recorded
checksums, a run-record mechanism, a smoke test, and a verified local/Sophia
sync path.

**Gate criteria** (blueprint text, verbatim).
1. the raw CSV is byte-identical locally and on Sophia
2. the repository can be cleanly cloned or pulled in both environments
3. no secrets or machine-specific paths are tracked
4. a run can be tied to a precise commit, configuration, environment, and data
   checksum
5. project state and role instructions are sufficient for a new coding-agent
   session to resume safely

---

## M1 --- Data understanding and column semantics

**Objective.** Establish, with the ClimRR data dictionary as evidence, what
each of the 275 columns actually is: physical variable, units, scenario, time
window, and identifier semantics. Separate verified facts from provisional
interpretation in `docs/DATA_NOTES.md`. This is the milestone in which the
column inventory acquires meaning.

**Gate criteria** (EXECUTOR-drafted, NOT blueprint-verbatim --- see the
provenance warning above).
- Every column is classified as identifier, geometry, or climate variable, with
  its scenario and time window resolved, or explicitly listed as unresolved.
- Units and the modeled-baseline status of historical fields are documented.
- The Fire Weather Index semantics of the `wildfire*` columns are stated
  explicitly, with the misreading as wildfire occurrence called out.
- Census identifier columns are documented as strings with leading zeros.
- No interpretation is recorded without a citation to the data dictionary or an
  entry in the decision log.

---

## M2 --- Climate phenomenon profiles

**Objective.** Aggregate the row-level table into defensible descriptions of
climate phenomena at chosen spatial and scenario granularities, producing
structured profiles under `artifacts/profiles/` and `artifacts/phenomena/`.

**Gate criteria** (EXECUTOR-drafted, NOT blueprint-verbatim --- see the
provenance warning above).
- Every aggregation is reproducible from a script with a run record.
- Aggregation choices (spatial unit, scenario pairing, statistic) are recorded
  in the decision log with rationale.
- Profiles carry provenance back to the source columns and rows.
- No profile asserts a phenomenon that the underlying columns cannot support.

---

## M3 --- Literature corpus and claim extraction

**Objective.** Ingest the independently collected scientific-literature corpus
and extract structured claims into `artifacts/claims/`, with citation
provenance. The corpus itself never enters this repository.

**Gate criteria** (EXECUTOR-drafted, NOT blueprint-verbatim --- see the
provenance warning above).
- Claims are traceable to a specific source document and location within it.
- The literature corpus remains outside the repository; only derived,
  small artifacts are tracked.
- Extraction is reproducible and run-recorded.
- Claim structure is fixed and documented before matching begins.

---

## M4 --- Cross-modal bridging

**Objective.** Match literature claims to data-derived phenomenon profiles,
producing scored bridges under `artifacts/bridges/` that identify where a
textual claim and a tabular pattern speak about the same thing.

**Gate criteria** (EXECUTOR-drafted, NOT blueprint-verbatim --- see the
provenance warning above).
- The matching method, its scoring, and its thresholds are documented and
  reproducible.
- A sample of bridges is manually validated and the validation is recorded.
- False-positive modes are characterised, not just counted.
- No bridge relies on a column interpretation that M1 left unresolved.

---

## M5 --- Benchmark QA construction and release

**Objective.** Construct the cross-modal QA benchmark from validated bridges,
with answers verifiable against both modalities, and release it with full
provenance and documentation.

**Gate criteria** (EXECUTOR-drafted, NOT blueprint-verbatim --- see the
provenance warning above).
- Every question's answer is verifiable against the data, the literature, or
  both, with the evidence recorded.
- The benchmark ships with documented construction provenance and known
  limitations.
- The full pipeline reruns end to end from the pinned commit and reproduces the
  released benchmark.
- No question depends on the three prohibited misreadings (observed history,
  FWI as wildfire occurrence, numeric Census identifiers).
