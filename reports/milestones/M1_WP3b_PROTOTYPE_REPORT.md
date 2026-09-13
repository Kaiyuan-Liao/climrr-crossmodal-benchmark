# M1-WP3b --- Phenomenon-unit prototypes

## 1. Milestone ID and title

**M1-WP3b --- Phenomenon-unit prototypes (bounded, assumption-recorded).** A work
package inside **M1, data grounding and metadata audit**. It is a **prototype
package**: nothing in it is offered as milestone evidence, nothing is merged,
and nothing was pushed.

## 2. Objective

Show, on exactly three concrete units built from the M1-WP3 pilot subset, what a
table-derived phenomenon looks like at cell, county and state level --- with
every operation, assumption and provisional rule written down --- so that the
group on 2026-09-14 and the mentor on 2026-09-17 can react to something real.

**Explicitly excluded, and not done:** a general extraction; a schema decision;
any literature, retrieval or embedding work; any column outside the 41 of
`docs/PILOT_SUBSET.md`; any selection of a unit by how large its values are.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/m1-wp3b`, created from `work/m1-wp3` at head `ad13649` |
| Commits in this package | 3: Phase A; Phases B–D; Phase E |
| Phase A | `ce8df0761dc74e498ee9ef99cdccfbc61a3f9afc` |
| Phases B–D | `140a649…` --- the parent of this report's commit |
| Remote | **Not pushed.** The work package says do not push and do not merge, and neither was done. `origin` has no `work/m1-wp3b` |
| `main` | unchanged, carrying the M1-WP1 merge at `62c9137` |
| `work/m1-wp3` | unchanged. This branch does not modify it and is not merged into it |

A commit cannot contain its own hash, so the head SHA after the Phase E commit
is reported with the package rather than written here.

## 4. Data version and checksums

| File | SHA-256 | Bytes | Shape | Storage |
| --- | --- | ---: | --- | --- |
| `data/raw/FullData.csv` | `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e` | 296,407,423 | 62,834 rows × 275 columns | Untracked, out of band, pinned by manifest hash (D-005) |
| `data/metadata/inferred_candidates.yaml` | unchanged from M1-WP3 | — | 20 records | Tracked; **read only** by this package |

**The manifest hash was verified before every read, fail-closed, in both runs.**
`CLIMRR_ALLOW_MISSING_RAW=1` was never set. No file under `data/raw/` was
modified, copied, or written back to. `scripts/build_phenomenon_prototypes.py`
carries forward the M1-WP3 guard: it refuses to run if the coverage report it
reads was built from different CSV bytes than the ones it just verified.

Artifacts produced, by SHA-256:

| File | SHA-256 | Bytes |
| --- | --- | ---: |
| `artifacts/profiles/hierarchy_checks.json` | `90b7e812fcdc86a089624afd0e7edafacdb2ef256122c5ad7e5145c6c79e4665` | 9,708 |
| `artifacts/phenomena/prototypes/P-CELL-1.json` | `b0a3f9dfaebd0ff23438d964444caa11679dbf1e61ada71019418bbebf8bfe3a` | 22,953 |
| `artifacts/phenomena/prototypes/P-COUNTY-1.json` | `fa9fd775d14a99f0cfba2277a57a38b85b325c5f163310b66ae112447cf0bde4` | 27,794 |
| `artifacts/phenomena/prototypes/P-STATE-1.json` | `b55e66a6db7119fecf26ce50de646014726330fcc911124997718a112af9da5e` | 329,076 |

Each record carries the CSV SHA-256 and the build commit in its own header
fields, so a record can be checked against the bytes it was made from without
consulting this report.

## 5. Environment and execution location

| | |
| --- | --- |
| Location label | `local` on every run |
| Python | 3.11.16 |
| Platform | macOS-15.3-arm64-arm-64bit |
| Environment | conda env `climrr` |
| `pip freeze` SHA-256 | `8d8e9add5995fdca…` --- the same fingerprint as the M1-WP3 runs |
| Pinned libraries (D-007) | all six match `requirements.txt`; no pin mismatch in any run record |

**Nothing ran on Sophia.** This package needs no Sophia access: it reads one
local file and writes small artifacts. The `pypdfium2==5.13.0` reinstall M1-WP3
flagged for Sophia is still outstanding and is untouched here.

Run records:

| Run | Result | Record |
| --- | --- | --- |
| `hierarchy_checks` | PASS | `reports/runs/20260913T191302Z_local_hierarchy_checks.json` |
| `build_phenomenon_prototypes` | PASS | `reports/runs/20260913T192854Z_local_build_phenomenon_prototypes.json` |

## 6. Work completed

**Phase A --- the structure, before anything was aggregated.**
`scripts/hierarchy_checks.py` streams the table twice and answers six questions
about what "cell", "county" and "state" can mean in it. Every value it reports
is a string; no meaning is attached to any of them. The findings are recorded in
`docs/DATA_NOTES.md` §1 as computed properties.

**Phase B --- the schema.** `src/climrr/phenomenon.py` defines schema version
`p0-prototype`: G scope, H concept, S season, T time horizon, C climate
scenario, V values, D direction, M magnitude, then the assumptions the record
depends on, a per-field provenance map, a generated description, and a
literature-probe design stub.

**Phase C --- three units.** `scripts/build_phenomenon_prototypes.py` streams
the table twice more --- once to find the two anchor rows, once to accumulate
the six PR-1 distributions and the complete member rows of the three chosen
units --- and writes the records, `docs/PHENOMENON_PROTOTYPES.md` and
`docs/PHENOMENON_ASSUMPTIONS.md`.

**Phase D --- the register.** Twelve assumptions, held as data in the module so
the document, the records and the tests cannot drift apart.

**Phase E --- the handout and this report.** `docs/GROUP_MEETING_2026-09-14.md`
quotes the three generated descriptions verbatim, with a test that fails if a
character of them is edited by hand.

To repeat the package from a clean checkout with the raw file in place:

```bash
python scripts/hierarchy_checks.py
python scripts/build_phenomenon_prototypes.py
pytest
python scripts/verify_no_secrets_or_paths.py
```

## 7. Deliverables and exact file paths

| Path | What it is |
| --- | --- |
| `scripts/hierarchy_checks.py` | Phase A: six structural checks |
| `artifacts/profiles/hierarchy_checks.json` | Phase A results, all values strings |
| `artifacts/profiles/hierarchy_checks.md` | the same, readable |
| `src/climrr/phenomenon.py` | the `p0-prototype` schema, PR-1, the assumptions register |
| `scripts/build_phenomenon_prototypes.py` | Phase C/D builder |
| `artifacts/phenomena/prototypes/P-CELL-1.json` | the cell-level record |
| `artifacts/phenomena/prototypes/P-COUNTY-1.json` | the county-level record |
| `artifacts/phenomena/prototypes/P-STATE-1.json` | the state-level record |
| `docs/PHENOMENON_PROTOTYPES.md` | the three units, generated |
| `docs/PHENOMENON_ASSUMPTIONS.md` | the register, generated |
| `docs/GROUP_MEETING_2026-09-14.md` | the group handout |
| `docs/DATA_NOTES.md` | §1 extended with the Phase A computed properties |
| `tests/test_hierarchy_checks.py` | 11 tests |
| `tests/test_phenomenon.py` | 38 tests |
| `tests/test_group_handout.py` | 12 tests |
| `reports/milestones/M1_WP3b_PROTOTYPE_REPORT.md` | this report |
| `reports/runs/20260913T191302Z_local_hierarchy_checks.{json,md}` | run record |
| `reports/runs/20260913T192854Z_local_build_phenomenon_prototypes.{json,md}` | run record |

## 8. Methods and rules that affect scientific meaning

Every rule below changes what a number in a record means. None was applied
silently; each has an assumption ID, a register entry, and a field in the record
that names it.

**1. Membership --- a row set, not a geometry (A-G3, computed).** A county is
*the set of rows sharing a `(State, NAME)` label*; a state is *the set of rows
sharing a `State` label*. No boundary, no area, no geometry. `GEOID` is used by
nothing, because Phase A measured that it cannot key a county here.

**2. What the labels mean (A-G1, unverified).** That those labels denote a
county and a state is an `inferred_candidate` reading (IC-011, IC-012). Every
field derived through them is `derived_from_inferred`.

**3. Aggregation --- unweighted mean (A-AGG1, A-G2, both unverified).** Each
member cell counts once. Nothing in the file states a cell area, so equal
weighting is an assumption and not a measurement. Every aggregate also reports
min, max and count beside the mean, and the complete list of per-cell values,
so a reader can see what the mean hides.

**4. Coverage --- a blank is excluded, never zero.** A member cell is used only
if it is non-empty on every column the variable reads. The record reports
`n_cells`, `n_cells_with_value` and `n_cells_empty`, and the description says
the excluded cells are never read as zeros. P-STATE-1 excludes 4 of 2,831.

**5. The change quantity, and the direction of the subtraction (A-DIR1,
A-DIR2, both unverified).** A change is the later horizon minus the historical
baseline; the dictionary never defines the direction. For the fire-weather
variable the change is carried by the **absolute difference** column
`wildfire_summer_Dend` (193), with the `verified_from_dictionary` percent-change
column `wildfire_summer_Pend` (195) reported beside it as a corroborating sign.
The reason is arithmetic --- a mean of per-cell differences is the difference of
the per-cell means, and a mean of per-cell percent changes is not. **That choice
is the EXECUTOR's and is recorded as A-DIR2 rather than presented as settled.**
For the heat-index variable no change column is in the pilot subset, so the
change is computed as index 253 minus index 241, both of them verified.

**6. Magnitude --- provisional rule PR-1 (A-M1, unverified).** The unit's change
value is ranked against every unit at the same level for the same variable; the
record reports the percentile and a tercile. **PR-1 is a placeholder that makes
the field non-empty. It is not a scientific threshold**, rests on no literature
and on no distributional reasoning, and the record says so in its own text,
every time, inside a distinct `[provisional rule PR-1: ...]` mark.

**7. Rounding.** Every derived value is quantised once, to the 15 decimal places
the CSV itself stores, half-to-even. Raw values are never rounded. The rounding
happens inside one function so that a mean accumulated while streaming and the
same mean recomputed from a retained list are the same digits --- otherwise a
unit could rank at the wrong percentile against itself.

**8. Distribution membership.** A unit with no member cell carrying a value is
absent from its level's distribution rather than present as a zero. A unit whose
label is the **empty string** is counted like any other: the 7 rows with no
`State` form one state-shaped unit and one county-shaped unit. Dropping them
would be a judgement about what an empty label means, and this project does not
have one (Q16). Every record carries this rule in its `M.distribution_membership`
field.

**9. Provenance inheritance.** A derived field takes the **weakest** status of
its inputs. The consequence is visible in the results: **no field in any of the
three records reaches `derived_from_verified`.** At cell level the fire-weather
change column is inferred; at county and state level the membership is inferred
whatever the columns are.

**10. Nothing was selected by magnitude.** The three units were fixed by
identity before a value was read --- the row `OID_` 1, the label that row
carries, and the `State` label of the row `OID_` 14. PR-1 is applied to a unit
already chosen, never to choose one.

**11. The reading of the letters S, T and C.** The work package names them
without defining them. The blueprint's phenomenon-schema list runs "season;
baseline period; future period; scenario", and that order is followed:
S = season, T = time horizon, C = climate scenario. Each record says the reading
is the EXECUTOR's. Renaming them changes three labels and no number.

## 9. Results with compact tables or examples

### Phase A --- what the structure says

| Key | Distinct keys | Min rows | Median rows | Max rows |
| --- | ---: | ---: | ---: | ---: |
| `Crossmodel` | **62,834** | 1 | 1 | **1** |
| `(State, NAME)` | 3,019 | 1 | 12 | 2,865 |
| `GEOID` | 12,941 | 1 | 2 | 877 |

- **`Crossmodel` is unique** --- 62,834 distinct over 62,834 rows, none empty.
- **`GEOID` does not determine `(State, NAME)`.** **3,234 of 12,941** `GEOID`
  values appear against more than one pair; `01003010400` appears with both
  `Alabama` / `Baldwin` and `Florida` / `Escambia`, and `01007010001` with three
  Alabama pairs. One of the 3,234 keys is the empty string.
- **Indices 110 `NAME_1` and 111 `NAMELSAD` each take exactly one value per
  `GEOID`** --- 0 keys violating. A structural count on two columns outside the
  pilot subset, interpreted nowhere and used by no record.
- **The 7 rows with no `State`** all carry `NAME` = `District of Columbia` and a
  `GEOID` beginning `11001`.
- Row sets behind the prototypes: `Oklahoma` 1,232 rows, `Oklahoma` / `Stephens`
  **10** rows, `California` **2,831** rows. **No pilot column is empty on any
  `Oklahoma` row.**

### The three prototypes

| Record | Level | Identifier | Cells | With value | Change | Direction | PR-1 |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| `P-CELL-1` | cell | `R106C361` | 1 | 1 | `6.109189990000000` | increase | upper_third, percentile 88.5253 of 62,834 |
| `P-COUNTY-1` | county | `Oklahoma` / `Stephens` | 10 | 10 | `6.083151960000000` | increase | upper_third, percentile 90.6260 of 3,019 |
| `P-STATE-1` | state | `California` | 2,831 | 2,827 | `13.209951652865228` | increase | middle_third, percentile 54.0000 of 50 |

`P-CELL-1` and `P-COUNTY-1` read the fire-weather variable (columns 189, 191,
193, 195); `P-STATE-1` reads the heat-index day-count variable (columns 241,
253, both `verified_from_dictionary`).

### Per-field status, by record

| Field | `P-CELL-1` | `P-COUNTY-1` | `P-STATE-1` |
| --- | --- | --- | --- |
| `G` identifier | `verified_from_dictionary` | `inferred_candidate` | `inferred_candidate` |
| `H` concept | `inferred_candidate` | `inferred_candidate` | `verified_from_dictionary` |
| `V` aggregate values | — (raw) | `derived_from_inferred` | `derived_from_inferred` |
| `D` direction | `derived_from_inferred` | `derived_from_inferred` | `derived_from_inferred` |
| `M` magnitude | `provisional_rule` | `provisional_rule` | `provisional_rule` |
| Assumptions | A1, A-G0, A-DIR1, A-DIR2, A-H1, A-H3, A-H5, A-M1 | the same **plus** A-G1, A-G2, A-G3, A-AGG1 | A1, A-G0, A-G1, A-G2, A-G3, A-AGG1, A-DIR1, A-M1 |

`P-STATE-1` names no `A-H` assumption because both of its columns are
`verified_from_dictionary`. That absence is deliberate and is recorded in the
register.

### The assumptions register

Twelve entries: **two `computed`** (A-G0's uniqueness half, A-G3), **ten
`unverified`**, **none `owner_confirmed`** --- and none will be until the mentor
answers. Nine are flagged as worth putting to her on 2026-09-17.

### The literature probe

A design stub in every record, and **nothing was retrieved**. It already
produces one finding: **at cell level there is no usable place term.** The
identifier is `R106C361`, which is not a phrase any paper contains. At county
and state level the place terms are the stored label strings, whose reading as
place names is itself inferred.

## 10. Validation performed

| Check | Result |
| --- | --- |
| `pytest` | **435 passed**, 0 failed |
| New tests in this package | 61 --- 11 hierarchy, 38 phenomenon, 12 handout |
| `python scripts/verify_no_secrets_or_paths.py` | **0 hits** over 169 tracked text files |
| Manifest verification | performed before every read, fail-closed, in both runs |
| Run records | 2, both `passed: true`, both with all six D-007 pins matching |
| Unlabelled-inference guard | 0 offences across the three records; the build fails the run if there is one |

Guards that fire in both directions, rather than only passing:

- `tests/test_hierarchy_checks.py` builds synthetic tables where `Crossmodel`
  **is** duplicated and where a `GEOID` **does** span two pairs, and asserts the
  checks report `False`. A change that silently turns a False into a True fails.
- `tests/test_phenomenon.py` doctors a record's description to strip one
  `[provisional: ...]` label and asserts the guard names the field. It also
  asserts that a derived field can never be stronger than its weakest input,
  that a cell unit with two members is refused, and that a unit with no usable
  member is a finding rather than an empty record.
- `tests/test_group_handout.py` re-runs the exact defect D-012 found --- a
  heading naming a place --- through the handout's own guard and requires it to
  fail.

Three findings from the guards during the build, all fixed rather than
suppressed: the direction word and the change value were reaching the prose
outside their labels through the values sentence and the corroboration sentence;
`Decimal`'s floor-division truncates toward zero, which made the nearest-rank
quantile off by one; and a mean of exactly zero serialised as `0E-15`.

## 11. Failures, rejected cases, and known limitations

1. **`GEOID` cannot key a county in this file, and 3,234 values prove it.** The
   work package anticipated this and said to report it prominently and to build
   the aggregates only if a county can be defined as a row set. It can: A-G3
   defines it that way, computed, without reference to `GEOID`. **What changed
   is that no record uses `GEOID` at all.**
2. **No record reaches `derived_from_verified`.** The package's rule --- status
   `derived_from_inferred` unless the change column is verified --- never
   triggers, because at cell level the fire-weather change column is inferred
   and at every other level the membership is. This is honest, and it also means
   the distinction is currently untested against a positive case.
3. **PR-1 is not a magnitude criterion and should not be shown to anyone as
   one.** It exists to make the field non-empty. Every place it appears says so.
4. **Unweighted averaging is unjustified, not merely unverified.** Nothing in
   the file states a cell area. If cells are not equal in area, every aggregate
   in this package is wrong by an unknown amount --- and no alternative
   (area weighting, population weighting, a median) was evaluated.
5. **The quantity clause quotes the *baseline* column's recorded meaning.** For
   a record that compares two horizons that is a partial description, and it
   reads oddly for the heat-index record, whose baseline meaning ends
   "-- Historical". A better template would compose the two.
6. **The empty-label unit is counted in every distribution.** The 7 rows with no
   `State` form a unit at state and county level. Counting it is a choice;
   dropping it would also have been one. It is recorded, not resolved.
7. **`A-DIR2` is an EXECUTOR choice inside a scientific question.** Which change
   column carries the direction for the fire-weather variable was decided on an
   arithmetic argument. The argument is sound; that it is the right choice for
   this project is not established.
8. **A county here may not be a whole county.** The row sets have between 1 and
   2,865 members. Whether a label's rows cover the geography the label names, or
   only the part of it the grid touches, is not established by anything.
9. **Nothing was verified on a second host.** The package is small and local;
   no cross-host reproduction was attempted.

## 12. Deviations from the approved plan

**This package precedes the GUIDANCE ruling that would authorise it, by
Kaiyuan's decision of 2026-09-13.**

The ruling in force, D-010/D-011, states that an M1-WP3 example **may not
contain** geographic aggregation, county/state aggregation, magnitude or
salience thresholds, or selection of interesting changes by new quantitative
criteria. **This package does the first three deliberately.** It was decided by
the project owner following the mentor's direction R-002, with a GUIDANCE ruling
requested in parallel and still pending at the time of writing.

What follows from that, and is honoured throughout:

- **Nothing is merged and nothing is pushed.** `work/m1-wp3b` exists locally
  only; `work/m1-wp3` and `main` are untouched.
- **Nothing here is evidence for any milestone gate.** Field 14 proposes no gate
  status.
- **Every record says so in its own text**, in a `prototype_notice` field, and
  both generated documents lead with it.
- **The schema is versioned `p0-prototype`**, not `v1`, so that adopting or
  discarding it is a visible act.
- **The pilot subset was not widened.** All six columns any record reads are
  among the 41 of `docs/PILOT_SUBSET.md`, and every provenance status carries
  through from M1-WP3 unchanged.

One further deviation, smaller: **Phase A reads two columns outside the pilot
subset**, indices 110 `NAME_1` and 111 `NAMELSAD`, because the work package's
check 4 asks whether they are functions of `GEOID`. The check is a count of
distinct values per key. Neither column is interpreted, neither is given a
status, and no record uses either. The hard constraint the package sets ---
"pilot subset only" --- is read as binding on the prototypes, which check 4 is
not part of, and the scope note is carried in the artifact itself.

**One sentence from M1-WP3 had to stop being used.** The location standing
caution in `climrr.examples` ends "no part of this pilot groups rows by any of
them". That was true of M1-WP3 and is false here. The prototypes therefore carry
their own location caution, which states that they group rows by inferred
labels; a test refuses the old sentence in a WP3b record. **The M1-WP3 records
are unchanged and their caution remains true of them.**

## 13. Open decisions and mentor questions

| # | Question | Owner | What it blocks |
| --- | --- | --- | --- |
| 1 | **Is the unit of a phenomenon a cell, a county-shaped row set, or a state-shaped one?** A cell has no place term at all | the group, then the mentor | the whole shape of the phenomenon schema, and what the literature side must deliver |
| 2 | **What replaces PR-1?** A physical threshold, a distributional one, or a criterion taken from the literature | GUIDANCE and the mentor | field `M` in every record |
| 3 | **Should cells be weighted?** By area, by population, or not at all --- and is an unweighted mean of a fire-danger index meaningful | the mentor | every aggregate (A-AGG1, A-G2) |
| 4 | **Which change column carries the fire-weather direction** --- the absolute difference or the verified percent change (A-DIR2) | COORDINATOR | fields `D` and `M` in the fire-weather records |
| 5 | **Do the letters S, T and C mean season, time and scenario?** | COORDINATOR | three labels, no numbers |
| 6 | **Do `NAME` and `State` denote a county and a state** (checklist line 14) | the mentor | `P-COUNTY-1` and `P-STATE-1` entirely |
| 7 | **Which way round is a difference** (checklist line 7) | the mentor | field `D` in every record |
| 8 | **Is one row one event** (checklist line 1) | the mentor | everything |
| 9 | **What would a paper plausibly say about a county-level fire-weather change?** If the answer is "nothing", the unit is wrong | the group | question 1 |

**For GUIDANCE specifically:** the ruling requested in parallel with this
package. Until it lands, the three judgements this package most needs are
whether aggregation may be performed at all inside M1, whether a magnitude field
may exist before a criterion is agreed, and whether `p0-prototype` is an
acceptable place to hold a schema that M2 will decide.

## 14. Proposed gate status

**This package proposes no gate status.** It is a prototype report, delivered
ahead of its ruling by the owner's decision, and it is not offered as evidence
for M1 or for any other milestone. The M1 gate criteria are quoted below for
completeness, with the state M1-WP3 left them in; **nothing in M1-WP3b changes
any of these judgements**, because nothing in M1-WP3b promotes a status,
resolves a question, or interprets a column.

| # | M1 gate criterion, verbatim | State | Evidence |
| --- | --- | --- | --- |
| 1 | "Every field selected for the pilot has a documented meaning, unit, time horizon, scenario, missing-value policy, and provenance status." | **PENDING --- unchanged by this package** | `docs/PILOT_SUBSET.md`; the 41 columns and their statuses are exactly as M1-WP3 left them |
| 2 | "No unresolved identifier or sentinel-value issue can silently corrupt the pilot." | **PENDING --- unchanged** | Q9.2, Q11 and Q17 remain open. This package adds one identifier fact --- `GEOID` does not determine `(State, NAME)` --- and responds to it by using `GEOID` nowhere |
| 3 | "The report clearly distinguishes verified facts from hypotheses." | **PENDING --- unchanged** | the separation is carried here too: computed facts in Phase A, `inferred_candidate` readings in the records, `provisional_rule` in `M` |
| 4 | "The mentor-facing metadata questions are specific and actionable." | **PENDING --- unchanged** | `docs/MENTOR_EXAMPLES.md` is untouched. This package adds candidate questions (field 13) but does not put them on the checklist |

**Proposed status for M1: unchanged --- still awaiting the mentor.** M1-WP3b
neither advances nor damages it.

## 15. Proposed next bounded objective

**None from this package.** The next event is the group meeting of 2026-09-14
and the mentor meeting of 2026-09-17, and the next bounded objective should be
written after the GUIDANCE ruling on this package and after the group answers
question 1 of field 13 --- what the unit of a phenomenon should be. Proposing
work now would mean choosing that answer, which is the one thing this package
exists to avoid.
