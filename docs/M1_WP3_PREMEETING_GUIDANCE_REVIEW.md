# ClimRR Cross-Modal Benchmark — M1-WP3 Pre-Meeting GUIDANCE Review

**Milestone:** M1 — Data Grounding and Metadata Audit  
**Work package:** M1-WP3 — Pilot-subset semantic validation through row-centered candidate examples  
**GUIDANCE status:** REVISE  
**Reviewed branch:** `work/m1-wp3`  
**Reviewed head:** `c8f47117b54be3a83c8d79313c3dbad3a86fdc7f`  
**Mentor meeting:** 2026-09-17

> This is a bounded pre-meeting review. The scientific design is accepted; the required revision is limited to mentor-facing framing and report bookkeeping. No redesign of the subset, example rows, or inferred-candidate machinery is required.

---

## Gate status

**REVISE**

The scientific design is sound, and I have **no objection to the 41-column subset, the structural row selection, the inferred-candidate machinery, or the standing-caution mechanism**.

However, I would **not send the current `MENTOR_EXAMPLES.md` to the mentor yet**, because one specific presentation issue cuts directly across the pre-meeting risk this review was intended to catch: **some inferred location semantics are presented as established facts outside the explicit confirmation surface**.

Examples include mentor-facing headings such as:

- `Stephens County, Oklahoma`
- `San Bernardino County, California`
- `Ventura County, California`

even though `NAME`, `State`, and `State_Abbr` are themselves `inferred_candidate` fields whose interpretation is still being submitted for confirmation.

This is a bounded framing fix, not a redesign. Once corrected, I have no scientific objection to the examples going to the September 17 mentor meeting.

---

## Current-stage assessment

M1-WP3 is otherwise doing what was authorized.

The package has:

- introduced `inferred_candidate` without weakening stronger statuses;
- created 20 column-specific inference records backed by dictionary spans and reasoning;
- selected three rows using **structural rather than climate-magnitude criteria**;
- generated mentor-facing prose from structured semantics;
- mechanically labeled inferred clauses `[provisional: ...]`;
- kept “one row = one event” explicitly under review;
- avoided aggregation, thresholds, phenomenon mining, literature processing, bridges, and QA.

The mentor interaction is also designed correctly against the “confirmation by impression” risk:

- individual readings receive `confirm / correct / don't know`;
- “don't know” is explicitly treated as a valid, non-promoting answer;
- broad approval of the overall approach is not supposed to promote individual field semantics.

So the issue is not the underlying methodology.

The remaining problem is a small set of **human-facing framing sentences that bypass the otherwise strong provisional-label machinery**.

---

## Evidence check

### Judgment (a): Is 41 columns “deliberately small”?

**Yes. Keep all 41, including the three-column stem probe.**

“Small” should not be interpreted as an arbitrary percentage threshold. What matters is whether every added field has a bounded role and whether the subset avoids sprawling interpretation of the full table.

The subset is defensible because:

- 21 columns are all currently `verified_from_dictionary`;
- 20 are specific adjacent fields required to make those verified families interpretable or to test a high-value unresolved assumption;
- 234 columns remain untouched;
- major undocumented families remain excluded.

The three `tempmaxann` probe fields are particularly justified.

They are the smallest set that tests:

- a historical value;
- a projected value;
- a change value;

under the same stem-to-section assumption.

One mentor decision on that link could clarify the assumption underlying 101 columns.

Removing these three would make the subset numerically smaller but scientifically less useful.

**Decision: keep the 3-column stem probe.**

---

### Judgment (b): Does the presentation templating satisfy criterion 6?

**The mechanism does; the current mentor document does not yet satisfy it completely.**

The three standing cautions are legitimate repository-level rendering rules rather than hidden semantic interpretations:

- FWI must never be rendered as wildfire occurrence;
- historical values must remain modeled baselines, not observations;
- an empty cell may safely be rendered as “no value in this file” without asserting why it is empty.

Conditionally inserting those cautions does **not** violate raw / semantics / presentation separation.

The mechanical safeguards are strong:

- inferred values must appear inside `[provisional: ...]`;
- verified values must not be mislabeled provisional;
- raw blocks are checked back against the CSV;
- FWI language is constrained so that wildfire-occurrence language appears only in a denial.

The remaining problem is **outside the generated field-level template**.

Mentor-facing headings and framing such as:

```text
Stephens County, Oklahoma
```

or:

```text
Where it is:
```

already express an interpretation of `NAME` / `State` before the mentor has confirmed that those columns carry county/state semantics.

That creates exactly the anchoring effect the project is trying to avoid.

Therefore:

> **Criterion 6 is satisfied by the architecture, but the mentor-facing framing must be revised before the meeting.**

---

### Artifact-hash disclosure

**No gate concern.**

The stale `dictionary_coverage.json` metadata hash was an artifact-integrity defect, but the disclosed facts make it non-substantive for the examples:

- counts did not change;
- selected columns did not change;
- the three examples were generated after the IC wording fix;
- the artifact was regenerated;
- a new regression test now rejects tracked-metadata hash mismatches;
- the old artifact was verified to fail that new test.

This is the correct remediation.

No scientific rerun or redesign is required solely because of this disclosure.

One bookkeeping inconsistency must still be corrected before WP3 is frozen:

- the attached report carries an earlier repository-state description;
- this pre-review packet identifies the actual review head as  
  `c8f47117b54be3a83c8d79313c3dbad3a86fdc7f`
  and states that the branch is pushed.

The report's branch/head/push metadata should match the actual reviewed state.

---

## Scientific risks

### 1. Pre-confirmation anchoring

This is the main remaining risk.

If the mentor sees:

> `Stephens County, Oklahoma`

at the top of an example, she may naturally process the county/state interpretation as already settled and focus her attention on the climate fields below.

Later asking:

> “Is `NAME` a county name?”

does not fully undo that framing.

That is especially important because:

- the location fields are not documented in the ClimRR dictionary;
- the Census vintage remains unknown;
- the coordinate reference system remains unknown;
- `X` / `Y` being longitude / latitude is still an inferred reading.

### 2. Compound confirmation

Some checklist items bundle multiple propositions.

For example, the location item currently combines:

- `NAME` = county/county-equivalent;
- `State` = state;
- `State_Abbr` = state abbreviation;
- interpretation of the distinct-count result;
- interpretation of the blank rows.

The deterministic observation:

```text
State has 49 distinct non-empty values and 7 blank rows
```

should remain separate from the semantic claim:

```text
State is a U.S. state field
```

until the latter is confirmed.

### 3. Stem-probe anchoring

This is **not** a blocking problem.

The stem probe explicitly says the mapping is inferred and asks the mentor to confirm or correct it.

Its role is appropriately diagnostic.

---

## Required actions

Before the 2026-09-17 mentor meeting:

1. **Remove unmarked inferred location semantics from headings and framing.**

   Replace headings such as:

   ```text
   Stephens County, Oklahoma
   ```

   with something semantically neutral, for example:

   ```text
   NAME = Stephens, State = Oklahoma
   ```

   or explicitly provisional:

   ```text
   [provisional location reading: Stephens County, Oklahoma]
   ```

2. Replace wording such as:

   ```text
   Where it is:
   ```

   with a neutral label such as:

   ```text
   Location-related raw fields:
   ```

   or:

   ```text
   Provisional location interpretation:
   ```

3. **Separate structural counts from semantic interpretation** in the location checklist.

   Prefer:
   - structural fact: `State` has **49 distinct non-empty values and 7 blank rows**;
   - proposed interpretation: `NAME` is county/county-equivalent and `State` / `State_Abbr` are state fields;
   - question: if that interpretation is right, what geographic coverage explains the observed count and blanks?

4. Add a **targeted guard** preventing known inferred location semantics from appearing unmarked in mentor-facing headings / hand-authored framing where practical.

   This does not need to solve arbitrary natural language. A bounded check for the known inferred fields is sufficient.

5. **Refresh the WP3 report repository-state metadata** so that branch, head, and push status match the actual pre-review packet.

No change is required to:

- the 41-column subset;
- the three row-selection rules;
- the three selected rows;
- the IC records;
- the generated field-level presentation;
- the standing cautions;
- the mentor-confirmation protocol.

---

## Decisions for Kaiyuan or mentor

### GUIDANCE decisions now

| Item                                            | Decision                                   |
| ----------------------------------------------- | ------------------------------------------ |
| 41-column subset                                | **Approved**                               |
| Three-column stem probe                         | **Keep**                                   |
| Standing FWI caution                            | **Approved**                               |
| Standing modeled-baseline caution               | **Approved**                               |
| Empty-cell rendering as “no value in this file” | **Approved**                               |
| Raw / semantics / presentation architecture     | **Approved in principle**                  |
| Current location framing                        | **Revise before mentor meeting**           |
| Stale metadata-hash disclosure                  | **Accepted; no scientific rerun required** |
| Example rows                                    | **Keep unchanged**                         |
| IC records                                      | **Keep unchanged**                         |

### Kaiyuan

At the mentor meeting, continue to distinguish:

- confirmation of a specific interpretation;
- correction of that interpretation;
- “don't know” / uncertainty;
- broad approval of the example format.

Broad approval must not be promoted into semantic confirmation.

### Mentor

The answer sheet already uses the correct response model:

```text
confirm / correct / don't know
```

That structure should be preserved.

---

## Next bounded objective

**Revise the mentor-facing framing only, then use the three examples in the September 17 mentor meeting.**

Do not expand WP3.

After the meeting, the next bounded objective remains:

**M1-WP4 — apply mentor feedback and prepare the M1 milestone gate packet.**

WP4 should:

- promote only explicitly confirmed semantics to `owner_confirmed`;
- record exactly what the mentor confirmed;
- keep corrections unconfirmed until updated and re-reviewed;
- keep “don't know” interpretations out of scientific use;
- distinguish broad approach approval from field-level confirmation;
- assemble the M1 milestone gate packet.

No additional examples or field families should be added before seeing whether these three examples successfully elicit the needed confirmations.

---

## Acceptance criteria

For this pre-meeting revision to be accepted:

1. No mentor-facing heading or framing sentence presents an `inferred_candidate` semantic as established fact.

2. Location-related raw observations remain visible, but proposed geographic meanings are:
   - marked provisional; or
   - phrased as questions.

3. The `State` distinct-count statement remains a **structural observation** until the semantics of the field are confirmed.

4. The answer sheet continues to preserve per-interpretation:
   - `confirm`;
   - `correct`;
   - `don't know`.

5. The three standing caution mechanisms remain as implemented.

6. The 41-column subset remains unchanged.

7. The three structurally selected rows remain unchanged.

8. The metadata-hash consistency guard remains in place.

9. The WP3 report reflects the actual:
   - reviewed branch;
   - reviewed head;
   - push state.

After those bounded changes:

- criteria 1–9 are ready for mentor interaction;
- criteria 10–11 correctly remain pending until mentor feedback.

---

## Do not do yet

Do not shrink the subset merely to improve the percentage.

Do not remove the stem probe.

Do not add more fields or examples before mentor feedback.

Do not promote any of the 20 inferred candidates before explicit mentor confirmation.

Do not infer from plausibility alone:

- Census vintage;
- coordinate reference system;
- blank-cell cause;
- FWI unit or aggregation;
- subtraction direction;
- stem-to-section mapping.

Do not start:

- phenomenon extraction;
- geographic aggregation;
- magnitude or salience thresholds;
- literature ingestion;
- literature claim extraction;
- semantic matching;
- bridge construction or validation;
- QA generation.

The only pre-meeting correction required is:

> **Make the mentor-facing surface obey the same provisional-vs-established distinction that the underlying structured records already enforce.**
