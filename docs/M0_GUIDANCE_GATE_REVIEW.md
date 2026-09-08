# ClimRR Cross-Modal Benchmark — M0 GUIDANCE Gate Review

**Milestone:** M0 — Reproducible Project Foundation  
**GUIDANCE decision:** PASS WITH ACTIONS  
**Final accepted repository commit:** `b87564b64ec44fda025b2c994ab6862880e2f2f5`  
**Review date:** 2026-09-08  
**Project:** ClimRR Cross-Modal Benchmark

> **Scope of this review:** M0 only. This decision authorizes bounded entry into M1-WP1 after the required closure actions below. It does **not** authorize phenomenon extraction, literature processing, semantic bridge matching, or QA generation.

---

## Gate status

**PASS WITH ACTIONS**

M0 has met its substantive gate. The evidence packet supports the five M0 criteria, including cross-host byte identity, pinned-run provenance, repository hygiene, and cold-resume safety.

The remaining actions are closure/documentation actions and one reproducibility requirement that should be completed at the start of M1. They do **not** require repeating the M0 Sophia smoke test unless the M0 execution mechanism itself changes.

---

## Current-stage assessment

The project now has a defensible reproducible foundation.

Most importantly:

- the authoritative CSV is identified by a full SHA-256, exact byte count, and shape;
- source, local copy, and Sophia copy produced the same hash;
- Sophia successfully executed against a pinned Git commit;
- local/Sophia execution records capture environment and data identity;
- the raw CSV never entered Git history;
- secrets and machine-path checks passed;
- the Sophia clone is operationally pull-only;
- an independent cold-resume test was actually performed rather than merely asserted.

The accepted M0 repository state is finalized at:

```text
b87564b64ec44fda025b2c994ab6862880e2f2f5
```

M0 therefore does **not** need to remain open for additional infrastructure experimentation.

---

## Evidence check

### 1. D-005 — Out-of-band CSV transfer

**Accepted. D-005 satisfies M0 gate criteria 1 and 4 in intent and in demonstrated operation.**

The scientific/reproducibility requirement is that the actual data used be unambiguously identified and byte-identical across environments. It does not require the Git commit itself to contain those bytes.

D-005 establishes a two-part execution identity:

```text
Git commit SHA + manifest-pinned data SHA-256
```

This is scientifically sufficient provided the fail-closed verification remains mandatory before data use. D-005 requires each host to verify the hash, and the tests/smoke procedures fail when the file is absent or mismatched.

This is preferable to forcing an unsuitable storage mechanism merely to preserve the original blueprint assumption.

### 2. CSV size discrepancy

**Resolved. No further scientific action required.**

The observed file is:

- **296,407,423 bytes**
- **62,834 rows × 275 columns**
- SHA-256:
  `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`

The source, local copy, and Sophia copy agree. The earlier `~48 MB` figure was therefore an inaccurate preliminary size estimate caused by the compressed-upload context, not evidence of a different logical dataset.

Future project documentation should use **296,407,423 bytes** as the authoritative file size.

### 3. Environment skew and unpinned dependencies

**Acceptable for M0, but do not defer stabilization until M2.**

M0 operations were hashes, byte counts, row/column counts, and basic file reads, and those reproduced successfully across:

- Local: Python 3.11.16
- Sophia: Python 3.13.13

The current skew therefore does not invalidate M0.

However, M1-WP1 already introduces computed schema/quality results such as dtype behavior, missingness, distinct counts, numeric detection, and min/max. Those outputs can depend on Python/library versions and parsing defaults.

Therefore:

> **Environment stabilization must occur during M1-WP1 before the schema/profile artifact becomes authoritative.**

### 4. Milestone-label correction

One documentation issue should be corrected before M0 is frozen: the M0 report's early exclusion table assigns later activities to the wrong milestone numbers.

The accepted charter remains:

- M1 — Data grounding and metadata audit
- M2 — Canonical semantic representation
- M3 — Table-derived phenomenon discovery pilot
- M4 — Literature ingestion and structured claim extraction pilot
- M5 — Semantic bridge discovery and validation

This documentation error does not invalidate the M0 work, but the accepted milestone report should not preserve misleading milestone ownership.

---

## Scientific risks

### 1. Environment-dependent profiling

A profile produced under one dependency set but interpreted or reproduced later under another weakens the meaning of “reproducible schema profile.”

This is why environment stabilization becomes an M1 requirement rather than remaining a deferred M2 item.

### 2. Profiling must not silently become interpretation

M1-WP1 may calculate structural/statistical properties of columns, but labels such as:

- “temperature variable,”
- “county identifier,”
- “missing sentinel,”
- “historical observation,”

must not be assigned merely because names or distributions suggest them.

The tracked ClimRR data dictionary is the authoritative semantic evidence source for M1.

### 3. Parser-observed dtype is not scientific ground truth

“dtype as read” is a software observation, not a scientific property of a field.

Identifiers, especially Census-style values, must be protected from destructive coercion and leading-zero loss.

### 4. Incomplete acquisition provenance

The acquisition date of the ClimRR export remains unknown.

This does **not** block M1, but it must remain explicitly recorded as `unknown`. It must not be guessed or silently filled.

---

## Required actions

1. **Accept D-005 as the permanent M0 raw-data mechanism** unless a future explicit infrastructure decision supersedes it.

   The fail-closed SHA-256 verification requirement remains mandatory before data use.

2. **Close the M0 documentation state before tagging.**

   Specifically:
   - correct the mistaken milestone-owner labels in the M0 report;
   - ensure the final accepted M0 report, `PROJECT_STATE.md`, and D-005 are present on the authoritative remote state;
   - use final accepted commit:
     `b87564b64ec44fda025b2c994ab6862880e2f2f5`;
   - then tag that accepted state as `m0-setup`.

   A new Sophia execution is **not required** merely because report/bookkeeping files are pushed, provided no execution, manifest, data-handling, or smoke-test code changes during closure.

3. **Amend the environment policy for M1-WP1.**

   Before accepting the authoritative schema/profile artifact:
   - stabilize the parsing/profiling environment, or
   - otherwise demonstrate deterministic equivalent behavior across supported environments.

   At minimum, versions of the libraries governing CSV parsing and profiling must be fixed and recorded.

4. **Retire the obsolete `~48 MB` operational figure.**

   Use **296,407,423 bytes** as the authoritative raw CSV size in future project records.

---

## Decisions for Kaiyuan or mentor

### Kaiyuan

**Approve an amendment to D-004:**

Environment stabilization occurs **during M1-WP1 before the profile is frozen**, rather than being deferred until M2.

This does **not** require forcing the Mac and Sophia to use the same environment manager. The scientific requirement is that parsing and profiling semantics be controlled and reproducible.

### Mentor

No mentor decision is required for:

- D-005;
- the file-size discrepancy;
- the local/Sophia Python-version difference at M0.

These are infrastructure/provenance matters and do not alter the scientific interpretation of ClimRR.

No mentor decision is required yet on individual column semantics. M1 should first determine which questions are resolved by the authoritative ClimRR data dictionary and escalate only the remaining specific ambiguities.

---

## Next bounded objective

**Authorize M1-WP1 with one refinement:**

Produce a **reproducible, semantics-neutral per-column schema and quality profile** of the exact manifest-pinned `FullData.csv`, and construct a metadata-status/question inventory by checking those columns against the tracked ClimRR data dictionary.

M1-WP1 should establish:

> **what is present, what is deterministically observable, and what metadata support exists**

It should **not** yet choose pilot phenomena or derive scientific patterns.

The profile may include deterministic structural facts such as:

- exact column name and order;
- parser-observed type information;
- missing count and rate;
- distinct count;
- safe numeric range where applicable;
- compact representative values where appropriate;
- dictionary coverage/status.

The output must explicitly distinguish:

1. **Computed data properties**
2. **Dictionary-verified semantics**
3. **Unresolved metadata questions**

---

## Acceptance criteria

M1-WP1 will be ready for GUIDANCE review when all of the following are satisfied:

1. **Dataset identity is explicit.**  
   Every profile artifact identifies the exact CSV SHA-256 used.

2. **Profiling is reproducible.**  
   The parsing/profiling environment and rules are sufficiently controlled that rerunning the profile does not depend on accidental package drift.

3. **All 275 columns are accounted for.**  
   The machine-readable schema/profile contains no silent omissions.

4. **Identifiers are protected from destructive coercion.**  
   Census-style identifiers and other potential string IDs retain their original representation, including leading zeros.

5. **Computed properties and scientific interpretations are separated.**  
   A numeric range may be computed before its scientific unit or meaning is known.

6. **Metadata status is evidence-based.**  
   Fields are classified using statuses such as:
   - verified from the ClimRR dictionary;
   - partially resolved;
   - unresolved;
   - structurally observed only.

7. **Sentinels and missingness are not guessed.**  
   Suspicious values may be flagged quantitatively, but their semantic meaning must come from metadata or remain unresolved.

8. **The metadata-question inventory is specific and actionable.**  
   It should not reduce to a generic request for “more documentation.”

9. **The charter's scientific cautions remain enforced.**
   - ClimRR historical values remain **modeled historical baselines**, not observations.
   - Fire Weather Index remains distinct from **wildfire occurrence**.

---

## Do not do yet

Do **not** begin:

- table-derived phenomenon extraction;
- geographic aggregation for scientific claims;
- magnitude or salience threshold design;
- humid-heat pilot generation;
- fire-weather phenomenon generation;
- literature-corpus ingestion;
- literature passage retrieval;
- embeddings;
- candidate bridge generation;
- bridge scoring or validation;
- QA construction.

In particular, M1-WP1 profiling results must **not** be converted into natural-language climate claims.

The next task is to establish trustworthy metadata grounding—not to discover phenomena yet.

---

## Gate handoff summary

| Item                                 | Decision                                                          |
| ------------------------------------ | ----------------------------------------------------------------- |
| M0 gate                              | **PASS WITH ACTIONS**                                             |
| Final accepted commit                | `b87564b64ec44fda025b2c994ab6862880e2f2f5`                        |
| D-005 out-of-band CSV policy         | **Accepted**                                                      |
| CSV size discrepancy                 | **Resolved**                                                      |
| Environment skew                     | **Non-blocking for M0**                                           |
| Dependency/environment stabilization | **Required during M1-WP1 before profile freeze**                  |
| Repeat Sophia M0 smoke test          | **Not required unless execution/data-handling mechanism changes** |
| M0 tag                               | Tag `m0-setup` after closure actions                              |
| Next authorized work                 | **M1-WP1 only**                                                   |
| Phenomenon extraction                | **Not authorized**                                                |
| Literature processing                | **Not authorized**                                                |
| Bridge matching                      | **Not authorized**                                                |
| QA generation                        | **Not authorized before M5 passes**                               |

---

## Leo confirms "D-004 amendment approved"

Approved. I’ll treat the D-004 amendment as authoritative going forward:

environment stabilization moves into M1-WP1;
it must be completed before the schema/quality profile is frozen as authoritative;
Mac and Sophia do not need identical environment managers, but parsing/profiling behavior and relevant dependency versions must be controlled and reproducible.
This closes the only Kaiyuan-level decision I raised in the M0 review.

As the complete M0_GUIDANCE_GATE_REVIEW.md
