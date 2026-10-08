# M5-WP2 --- positive-case compatibility run (adjudicated WP2 claims × three prototypes)

Phase 4 of the M4-WP2 sequence authorized by
[`docs/M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md`](../../docs/M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md)
(D-019). Every adjudicated claim of the four relevance-guided candidates, of
every evidence tier, against P-CELL-1, P-COUNTY-1 and P-STATE-1 v2, by
deterministic rules. **No QA.**

## 1. Milestone ID and title

**M5-WP2 --- positive-case compatibility run.** M5 (bridges). Follows M5-WP1
(machinery validation, D-018). **M1 remains open** (D-014).

## 2. Objective

Find out whether any real, adjudicated literature claim survives the full
provenance-preserving bridge pipeline --- revised C-2, geography, time,
scenario, direction --- against the three prototypes; record eligibility and a
provisional relation for every pair, separately.

**Excluded:** widening the sample; new surface terms, synonyms or place
aliases; extending the G-2 list; any change to the M5-WP1 freeze or to
P-STATE-1 v1; deciding any relation by human review; QA.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/m4-wp2-adj`, from `work/m4-wp2-read` at `258536a`, with `work/m4-wp2-blind` (`939111e`) merged at `ab80335` |
| Inputs frozen (with the adjudication), **before the matrix existed** | **`59880d7`** |
| Matrix, documents, mentor report, reports, state | the commit after `59880d7`; its SHA travels with the hand-back |
| Remote | **not pushed, not merged** |

## 4. Data version and checksums

| Object | SHA-256 |
| --- | --- |
| `artifacts/bridges/m5wp2_inputs.json` | `5dd5de22de4f5feb1ff5d6dcffc01ad750394690d73183740af81208c1f5a114` |
| `artifacts/phenomena/prototypes/P-STATE-1.v2.json` | `be8126dd57171e876e4e5bc36f63c4d8e957281307487a1fe957e7b2bd312b32` |
| `data/metadata/concept_map.yaml` (unchanged since D-018) | `6ec6b081658e82b5fba4171bcd3135f69ce71710a7a515f32cac83404ebd3664` |
| `m5wp1_inputs.json` / `m5wp1_matrix.json` (**untouched**, pinned in the new freeze) | `bc22b4fa…28cc` / `526ac573…cd02` |
| Matrix JSON / CSV, compatibility document | in the run record `reports/runs/20261008T231742Z_local_m5wp2_matrix.json` |

The freeze also pins every claim (file and record hash, tier, status), each
prototype (file and record hash, version), the G-2 list and the compatibility
rule version (`compat.py` hash, rule-table and relation-table record hashes).
`FullData.csv` was not read.

## 5. Environment and execution location

conda environment `climrr`, Python 3.11.16, location `local`; D-007 pins
matched. No corpus file is read by the run. Sophia not used.

## 6. Work completed

`src/climrr/m5wp2.py` (freeze, effective claims, relation precedence, run,
summary, CSV); `scripts/freeze_m5wp2_inputs.py` (run and committed first);
`scripts/m5wp2_matrix.py` (verifies the freeze, runs 78 pairs through the
unchanged `compat.evaluate_pair` with the concept map, `bridge.candidate_bridge_eligible`,
the relation; writes JSON, CSV and `docs/M5_WP2_COMPATIBILITY.md`);
`tests/test_m5wp2.py`. The plain-language report for the mentor:
`docs/MENTOR_REPORT_2026-10-09.md`.

## 7. Deliverables and exact file paths

`artifacts/bridges/m5wp2_inputs.json`, `m5wp2_matrix.json`, `m5wp2_matrix.csv`;
`docs/M5_WP2_COMPATIBILITY.md`; `docs/MENTOR_REPORT_2026-10-09.md`;
`src/climrr/m5wp2.py`; `scripts/freeze_m5wp2_inputs.py`,
`scripts/m5wp2_matrix.py`; `tests/test_m5wp2.py`; this report; run records
`20261008T231622Z_*`, `20261008T231742Z_*`.

## 8. Methods and rules that affect scientific meaning

1. **Effective claim** = the adjudicated record with each `adopted_dimension`
   substituted (D-019 rule 3); all tiers enter, tier carried on every row.
2. **Compatibility rules unchanged** from `compat.py`: C-1 (metric, no mapping
   approved), **C-2 revised** (boundary-aware approved family term inside the
   concept value → `compatible_at_family_level`), G-1 exact label at the
   prototype's level, G-2 committed list only, G-3 otherwise, T-1/T-2/T-3 (T-2
   skips `unresolved_tie`), S-1 explicit RCP only, D-1 only when concept is
   metric-compatible, U-1 unknown → `not_evaluable`.
3. **Eligibility** (`bridge.candidate_bridge_eligible`): concept compatible or
   family-level, geography compatible, nothing incompatible.
4. **Provisional relation**, in precedence: `contradicting` (concept + and
   geography compatible, direction the only incompatible); `incompatible` (any
   other incompatible); `supporting` (eligible, metric concept, scenario, time
   and direction compatible); `supporting_qualified` (eligible, direction
   compatible or not_evaluable, family-level or scenario/time not_evaluable);
   `related_insufficient` (concept +, not eligible); `uncertain` otherwise.
   Every non-`incompatible` relation is also checked against D-018's
   `bridge.check_relation`.
5. **Geography cases** (work package): another Oklahoma county vs Stephens →
   `not_evaluable`; state-level Oklahoma vs the county unit → `not_evaluable`;
   "California, Arizona and Nevada" vs California → `not_evaluable` (a list is
   not the label).

## 9. Results with compact tables or examples

**78 pairs; candidate-bridge-eligible: 0.**

> No candidate-bridge-eligible pair was found under the current deterministic
> rules among the adjudicated claims of the four frozen relevance-guided
> candidates.

| Dimension | compatible | family-level | incompatible | not_evaluable |
| --- | ---: | ---: | ---: | ---: |
| concept | 0 | 2 | 0 | 76 |
| geography | 0 | --- | 0 | 78 |
| time | 0 | --- | 3 | 75 |
| scenario | 0 | --- | 0 | 78 |
| direction | 0 | --- | 0 | 78 |

| Relation | Pairs |
| --- | ---: |
| supporting / supporting_qualified / contradicting | 0 / 0 / 0 |
| related_insufficient | **2** --- `LIT-000519-C5` × P-CELL-1, × P-COUNTY-1: concept "FWI" family-level (C-2, `fire_weather_index`); geography, time, scenario unknown; **tier C** (reader 1 only) |
| incompatible | **3** --- `LIT-001536-C2` (tier B, a 2020-2023 finding) × all three, T-2 |
| uncertain | 73 |

**Why nothing is eligible.** Geography is `compatible` in **0** of 78: no
explicit claim geography equals a prototype label (closest: "Dewey County, NW
Oklahoma"; "California, Arizona and Nevada"; the inferred "Oklahoma and Texas
panhandles"). Concept is positive in 2 of 78, both on a background claim with
no geography. Scenario is unknown in every claim.

## 10. Validation performed

| Check | Result |
| --- | --- |
| Freeze | `verify_inputs` passes; a changed claim hash fails it (test) |
| Reproduction | matrix JSON and CSV re-derive row for row from the frozen inputs (test) |
| Coverage | 78 pairs, each once |
| Prototype version | P-STATE-1 v2 in the freeze; M5-WP1 inputs and matrix byte-identical to their pins |
| Relation precedence | 8 synthetic cases; unknown scenario and family-level concept never `supporting` |
| Geography cases | the five work-package cases on synthetic claims (`California` → compatible; `Oklahoma, Stephens` → compatible; the three others → not_evaluable) |
| `pytest` / scan | **784 passed**; 0 hits |

## 11. Failures, rejected cases, and known limitations

- **The G-2 list is M5-WP1's** (four countries). Claims about Sardinia,
  European countries or the Sahel are `not_evaluable` rather than
  `incompatible` on geography. This cannot create eligibility; it understates
  conflicts.
- **The two concept-positive pairs rest on one reader** (tier C) and on a
  background sentence with no place; even if geography were known, it could
  not establish an accepted bridge without further independent resolution.
- **Lexical concept matching found the right family once and was spared a
  false friend only because no reader put the fractional water index into a
  concept field** (`LIT-001501`): C-2 would match the letters "FWI".
- **G-1 is strict by design**: a multi-state list naming California is not the
  California unit. Whether a looser rule is wanted is a mentor/GUIDANCE
  question, not decided here.
- n = 4 papers, relevance-selected: the zero says nothing about corpus
  prevalence.

## 12. Deviations from the approved plan

1. `incompatible` is placed **above** `supporting`/`supporting_qualified` and
   below `contradicting` in the precedence, so a pair is never both eligible
   and labelled incompatible; the work package listed it last.
2. `related_insufficient` is applied as "concept positive, geography not
   compatible, nothing incompatible", the work package's "eligible on concept
   only".
3. No extension of the G-2 list (not authorized).

## 13. Open decisions and mentor questions

Put to the mentor in `docs/MENTOR_REPORT_2026-10-09.md`: (a) is a family-level
match with disclosed metric/scenario gaps useful; (c) widen place terms to all
US states (predeclared) or change the unit to a region a paper would name. For
GUIDANCE: whether G-1 may accept a state named within a list, and whether the
G-2 list may be extended.

## 14. Proposed gate status

Against D-019 criteria 13--25 (see `M4_WP2_REPORT.md` field 14 for each line):
all **MET**, with criterion 6 (blind isolation) put to Kaiyuan. **Proposed
status:** ready for GUIDANCE review as the first positive-case run --- a
**negative result**, bounded to these four papers and these rules.

## 15. Proposed next bounded objective

After the mentor answers, predeclare one WP2b retrieval experiment (all US
state names, or a region-level unit), with terms and prototype-selection rules
frozen before any reading.
