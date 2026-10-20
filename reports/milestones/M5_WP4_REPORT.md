# M5-WP4 --- positive-case compatibility run on LITCORPUS-02 (adjudicated WP4 claims × three prototypes)

Phase B of work package M4-WP4r3, authorized by
[`docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md`](../../docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md)
(D-025, Track A: "compatibility only after adjudication"). Every adjudicated claim of
the twenty frozen LITCORPUS-02 place candidates, of every evidence tier, against
P-CELL-1, P-COUNTY-1 and P-STATE-1 v2, by deterministic rules. **No QA.**

## 1. Milestone ID and title

**M5-WP4 --- positive-case compatibility run on LITCORPUS-02.** M5 (bridges). Follows
M5-WP2 (the same run on the four LITCORPUS-00 candidates, 0 of 78). **M1 remains
open** (D-014).

## 2. Objective

Find out whether any adjudicated claim from the concept-first working corpus survives
the bridge pipeline --- C-1 / C-2 with the D-025 concept map, geography string *and
role*, time, scenario, direction --- against the three prototypes; record per pair the
five judgments, eligibility, the `not_evaluable` list and a provisional relation; list
every "standardized heat index" match for GUIDANCE.

**Excluded:** new surface terms or masks (the SHI case is flagged, not masked); place
aliases or a looser G-1; extending the G-2 list; any change to `compat.py`, the
M5-WP1 / M5-WP2 freezes or the prototypes; human review of relations; QA.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/m4-wp4-adj` (from `work/m4-wp4-read` `72617da`; blind `c452d7d` merged at `d90595c`) |
| Adjudication (the claims this run reads) | **`6c856e2`** |
| Inputs frozen, **before the matrix existed** | **`220ca84`** |
| Matrix, CSV, compatibility document | **`8436c25`** |
| Reports, state, brief | the head of `work/m4-wp4-adj` handed back with this package |
| Remote | **not pushed, not merged** |

## 4. Data version and checksums

| Object | SHA-256 |
| --- | --- |
| `artifacts/bridges/m5wp4_inputs.json` | `fb8bd3cb12f9cf00bc9d03ffdaae90241266cb3dc44737619cd0cb49149635fc` |
| `artifacts/bridges/m5wp4_matrix.json` / `.csv` | `2af92a23…8c80d8f4` / `8aa9da33…ac059285` |
| `data/metadata/concept_map.yaml` (D-025) | `27f7a44d…0931d7b4` |
| `artifacts/phenomena/prototypes/P-STATE-1.v2.json` | `be8126dd…bd312b32` |
| `m5wp2_inputs.json` / `m5wp2_matrix.json` (**untouched**, pinned in the new freeze) | `5dd5de22…c1f5a114` / `749ef1d4…a0fba086` |
| `m5wp1_inputs.json` / `m5wp1_matrix.json` (**untouched**) | `bc22b4fa…28cc` / `526ac573…cd02` |

The freeze also pins each claim (file and record hash, tier, status, origin), each
prototype (file and record hash, version), the G-2 list, the compatibility-rule
version (`compat.py` hash, rule-table record, the M5-WP4 rule record, the relation
record) and **R-FWI-1 v1** (D-022; recorded only --- it governs retrieval, not claim
compatibility). `FullData.csv` and the corpus are not read by the run.

## 5. Environment and execution location

conda environment `climrr`, Python 3.11.16, location `local`; D-007 pins matched.
Sophia not used. Run records `20261020T221054Z_local_freeze_m5wp4_inputs.*`,
`20261020T221222Z_local_m5wp4_matrix.*`.

## 6. Work completed

`src/climrr/m5wp4.py`: freeze; effective claim (`m5wp2.effective_claim` plus the
adjudicated geography role); **G-R** and the granularity reason layered over the
unchanged `compat.compare_geography`; the SHI flag over the unchanged C-2; run,
summary, CSV. `scripts/freeze_m5wp4_inputs.py` (run and committed first);
`scripts/m5wp4_matrix.py` (verifies the freeze; 354 pairs through
`compat.evaluate_pair`, the role gate, `bridge.candidate_bridge_eligible`,
`m5wp2.assign_relation`; writes JSON, CSV and
[`docs/M5_WP4_COMPATIBILITY.md`](../../docs/M5_WP4_COMPATIBILITY.md));
`tests/test_m5wp4.py`.

## 7. Deliverables and exact file paths

`artifacts/bridges/m5wp4_inputs.json`, `m5wp4_matrix.json`, `m5wp4_matrix.csv`;
`docs/M5_WP4_COMPATIBILITY.md`; `src/climrr/m5wp4.py`;
`scripts/freeze_m5wp4_inputs.py`, `scripts/m5wp4_matrix.py`; `tests/test_m5wp4.py`;
this report; the run records in field 5.

## 8. Methods and rules that affect scientific meaning

1. **Effective claim** = the adjudicated record with each adopted dimension
   substituted (D-019 rule 3) and the adjudicated geography role class attached; all
   tiers enter, the tier travels on every row. `unresolved_tie` claim_type leaves T-2
   `not_evaluable`.
2. **C-1 / C-2 unchanged**, D-025 term set: `approved_lexical` forms (including
   `fire-weather index`, `canadian forest fire weather index`, `canadian fwi`,
   `heat-index`) participate; `extended heat index` (`approved_family_term`) is
   excluded and masks the `heat index` inside it. C-2 gives
   `compatible_at_family_level`, never metric equality; no metric mapping is
   approved, so C-1 cannot fire.
3. **Geography = string and role.** G-1 exact label equality as before; **G-R**: role
   class `affiliation` or `citation_or_person` → `not_evaluable` whatever the place
   (never compatible, never incompatible); an exact label match is `compatible` only
   for role class `study_area` or `cited_study_area`, else `not_evaluable`. A state
   name against a county prototype of that state → `not_evaluable`,
   `different_granularity_state_vs_county`. G-2 / G-3 unchanged.
4. **Standardized heat index**: no mask. A C-2 `heat index` hit inside "standardized
   heat index" keeps its status and carries `possible_collision: standardized heat
   index`.
5. T-1 / T-2 / T-3, S-1 (explicit RCP only), D-1 (only if concept metric-compatible),
   U-1 unchanged. Eligibility and relation precedence exactly as M5-WP2.

## 9. Results with compact tables or examples

**354 pairs (118 claims × 3); candidate-bridge-eligible: 0.**

> No candidate-bridge-eligible pair was found under the current deterministic rules
> among the adjudicated claims of the twenty frozen LITCORPUS-02 place candidates.

| Dimension | compatible | family-level | incompatible | not_evaluable |
| --- | ---: | ---: | ---: | ---: |
| concept | 0 | 12 | 0 | 342 |
| geography | 2 | --- | 9 | 343 |
| time | 0 | --- | 48 | 306 |
| scenario | 0 | --- | 0 | 354 |
| direction | 0 | --- | 0 | 354 |

| Relation | Pairs |
| --- | ---: |
| supporting / supporting_qualified / contradicting | 0 / 0 / 0 |
| related_insufficient | **12** (tier B 5, C 7) --- concept family-level, geography not compatible |
| incompatible | **57** --- T-2 48 (16 historical findings × 3), G-2 9 (3 claims × 3) |
| uncertain | 285 |

**Why nothing is eligible.** The two ingredients never meet on one claim. Concept is
family-level on 12 pairs (8 claims: `000084-C3`, `000185-C5`, `000315-C5`,
`000366-C3`, `000927-C5`, `001160-C4`, `001236-C2`, `001308-C4` --- 4 of them
background citations), and none of those claims has a geography equal to a
prototype label (`the United States` [inferred], `many European countries`,
`California and Nebraska`, `Canada`, `the desert communities of California`,
`Moscow, Russia`, `the eastern part of Attica Greece`, `San Diego County`).
Geography is `compatible` on 2 pairs, both bare `California` vs P-STATE-1
(`000185-C1`, role study area, CALFIRE large fires; `001063-C5`, cited study area,
the 2012-2016 drought); neither concept is in a pilot family. Two further bare
`California` claims are role-gated (`000203-C1`, `001308-B4`: contextual).
No claim's geography is the bare state `Oklahoma`; no claim records an
affiliation or person role, so those gates fired only in tests.

**Collision list (GUIDANCE).** `LIT2-001160-C4` (tier C, reader 1 only), concept
"excess heat factor (EHF) versus standardized heat index (SHI)": `heat index` at
[45, 55) inside SHI. × P-STATE-1 `compatible_at_family_level` → `related_insufficient`;
× P-CELL-1 / P-COUNTY-1 `not_evaluable` (other family). All three flagged.

**Scenario.** 2 of 118 claims have a non-`unknown` scenario (both `LIT2-000203`,
described, not named); **named scenario 0**.

## 10. Validation performed

| Check | Result |
| --- | --- |
| Order | adjudication `6c856e2` → freeze `220ca84` → matrix `8436c25` |
| Freeze | `verify_inputs` passes; a changed claim hash fails it (test); concept map `27f7a44d…`, P-STATE-1 v2, R-FWI-1 v1 named (test) |
| Reproduction | matrix JSON, CSV and summary re-derive from the frozen inputs (test) |
| Coverage | 354 pairs, each once; every row carries a tier and a role class |
| Geography and role | 11 synthetic cases (test): `California` study / cited → compatible; affiliation, citation/person, contextual, unknown → not_evaluable (G-R); `Oklahoma` vs P-COUNTY-1 → not_evaluable (granularity); `Oklahoma, Stephens` → compatible; `Dewey County, NW Oklahoma` → not_evaluable; `China` + affiliation → not_evaluable, + study area → incompatible |
| Collision / mask | "standardized heat index" → family-level + flag; "extended heat index" stays masked; "heat index trends" unflagged (test) |
| Untouched | M5-WP1 / M5-WP2 inputs and matrices byte-identical to their pins; `compat.py` unchanged; M5-WP2 tests pass |
| `pytest` / scan | **895 passed**; 0 hits |

## 11. Failures, rejected cases, and known limitations

- **G-2 over-reaches on a continent list**: `LIT2-000786-C1` ("North and South
  America, Europe, Australia, and Africa", a review's study regions) is `incompatible`
  because "Australia" is on the disjoint list and "North America" is on neither list.
  Pre-existing rule, not changed here; it cannot create eligibility.
- **The two geography-compatible pairs rest on `cited_study_area` once**
  (`001063-C5`, tier C, a background citation). Treating a cited study's area as study
  geography is this package's choice (M4-WP4 field 12, 9); it changes no eligibility
  here.
- **7 of the 12 concept-positive pairs are tier C** (5 of the 8 claims, single-reader);
  4 of the 8 claims are background citations. None could establish an accepted bridge.
- G-1 is strict: `San Diego County, California`, `California's Central Valley`,
  multi-state lists are not the California unit (as in M5-WP2).
- n = 20 deterministic place candidates; the zero says nothing about prevalence.

## 12. Deviations from the approved plan

1. **G-R implemented in a new module**, not in `compat.py`: the frozen M5-WP2 inputs
   pin `compat.py`'s hash, so editing it would break that freeze. `compat.py` is
   unchanged; G-R and the granularity reason post-process its geography judgment.
2. **`cited_study_area` passes G-R** (counted as study geography). The package names
   affiliation / person / citation as the blocked roles; a cited study's area is the
   geography of the restated finding, not a citation of the place. GUIDANCE may rule
   otherwise; no eligible pair depends on it.
3. **`contextual`, `data_source`, `other` and `unknown` roles also block G-1** (not
   listed in the package; the conservative reading of "role not study geography").
   Affiliation / person block G-2 too; other roles leave G-2 as it was.
4. The SHI flag is attached on all three prototypes of the claim, including the two
   where C-2 gives `not_evaluable` (other family): "record every such match".

## 13. Open decisions and mentor questions

For GUIDANCE: (a) the SHI collision --- mask, flag-only, or a narrower C-2;
(b) whether `background_citation` claims and `cited_study_area` geography may ever
bridge; (c) whether G-2 should treat a list that names North America (or the United
States) as not disjoint; (d) the role-gate reading in field 12, 3. For the mentor
(standing): is family-level support with disclosed metric and scenario gaps useful;
widen places or change the unit.

## 14. Proposed gate status

Against D-025 acceptance criteria 20--22 and the package: inputs frozen before the
matrix; all claims × 3 prototypes, each pair once, tier carried; five judgments with
rule ids and both values; eligibility and `not_evaluable` list per pair; provisional
relation per pair; G-1 with role; collision list made; **0 eligible**, bounded
sentence only. **Proposed status:** ready for GUIDANCE review with M4-WP4 --- a
second **negative result**, bounded to these twenty papers and these rules.

## 15. Proposed next bounded objective

After GUIDANCE and the mentor: decide whether the next experiment changes the unit
(a place a paper would name as its study area --- the 2 bare-`California` claims here
were not about a pilot concept) or the concept level (family-level support), and
predeclare it before any reading. No QA until an eligible pair exists.
