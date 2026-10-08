# M4-WP2 (retrieval half) and M5-WP1 closure --- Track B

**This is the retrieval half of M4-WP2.** It freezes which corpus items a later
package will inspect; **it reads none of them.** Semantic reading of the
candidates waits for M4-WP1b (D-018, action 17, criterion 23). The candidates
are a **relevance-guided candidate-generation sample, not representative.**
Authorized by
[`docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md`](../../docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md)
(D-018). No QA is generated.

## 1. Milestone ID and title

**M4-WP2 Track B --- relevance-guided candidate retrieval (retrieval only),
with the M5-WP1 closure actions.** M4 (literature), M5 (bridges). **M1 remains
open** (D-014). M4-WP1b (Track A) is in progress elsewhere.

## 2. Objective

Close M5-WP1's actions and build the semantic interfaces D-018 asks for ---
a versioned P-STATE-1 with year windows, a tracked concept map that keeps
family apart from metric, and the candidate-eligibility and relation
definitions --- then **freeze** a deterministic, boundary-aware candidate set
from approved terms, without reading it.

**Excluded, and not done:** reading, summarizing or extracting from any
candidate; any surface term not backed by a dictionary line; any place alias;
re-running the frozen M5-WP1 matrix; applying eligibility or relations to any
real pair; QA.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/m4-wp2-retrieval`, from `main` at **`87bce48`** (M4-WP1b blind reading, on top of the M5-WP1 merge `55decb3` and scan fix `656044c`) |
| Phase A --- D-018 bookkeeping | `8ee8857` |
| Phase B --- P-STATE-1 v2 | `7ba2657` |
| Phase C --- concept map, C-2 | `f586d29` |
| Phase D --- eligibility, relations | `13c56fb` |
| Phase E1 --- **terms frozen** (scan code present, not yet run) | `6080cc3` |
| Phase E2 --- **pool and candidates frozen** | `7d0e128` |
| Candidates document, this report, state, knowledge list | the commit after `7d0e128`; its SHA travels with the hand-back |
| Remote | **not pushed, not merged** |

## 4. Data version and checksums

| Object | SHA-256 |
| --- | --- |
| `artifacts/bridges/m5wp1_inputs.json` (frozen, **unchanged**) | `bc22b4fa9344283fd31e9b7ac1f70fa53276d8dd171d6749933a4cf0b6a628cc` |
| `artifacts/bridges/m5wp1_matrix.json` (frozen, **unchanged**) | `526ac573f58a027c53b99e90a88fc7b3509c550afe205a9d6f15f74072d4cd02` |
| `P-STATE-1.json` (v1, **unchanged**) | `898af41046b4edcaef19396913099fbb261b69a29ebd926b7a9b42c0468dcfb0` |
| **`P-STATE-1.v2.json`** | **`be8126dd57171e876e4e5bc36f63c4d8e957281307487a1fe957e7b2bd312b32`** (record hash `ae5659bd…`) |
| `data/metadata/concept_map.yaml` | `6ec6b081658e82b5fba4171bcd3135f69ce71710a7a515f32cac83404ebd3664` |
| **`artifacts/literature/wp2_terms.json`** | **`3d0b1513478b8096a4507f454df1ab5b22928b25fd3354d096961198a1e7d02c`** |
| **`artifacts/literature/wp2_qualifying_pool.json`** | **`8f097f7adfab4fc5987061aefb0d31b37f12c9fcc1fba8721b6e96316048a3f0`** |
| **`artifacts/literature/wp2_candidates.json`** | **`e155e70e338ffb67f8c881a8a3fdb794e28c0f048c43afc10b0a723135ec8d9c`** |
| Corpus manifest (`LITCORPUS-00`) | `3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a` |

All 1,918 corpus files were hash-verified against the manifest before
decoding (fail closed). `FullData.csv` was not read.

## 5. Environment and execution location

conda environment `climrr`, Python 3.11.16, location `local`; D-007 pins
matched. The external corpus was read from `literature_corpus_root` in the
untracked config. Sophia not used.

## 6. Work completed

**Phase A.** D-018 in `DECISION_LOG.md`, with the ruling's rules verbatim; the
ruling tracked as placed; M5-WP1 report fields 3 and 14 updated; the ruling's
mentor question leads `MENTOR_BRIEF.md`; a test pins both frozen M5-WP1
artifacts at their reviewed hashes.

**Phase B.** `scripts/build_p_state_1_v2.py` writes `P-STATE-1.v2.json` from
v1: explicit windows, spans, inherited status, `version: 2`,
`supersedes: P-STATE-1 v1`, `amendment: D-018`. Version note in
`PHENOMENON_PROTOTYPES.md`.

**Phase C.** `data/metadata/concept_map.yaml`, `src/climrr/conceptmap.py`
(validator, boundary-aware matcher), rule C-2 in `src/climrr/compat.py`
(opt-in).

**Phase D.** `src/climrr/bridge.py`, `docs/BRIDGE_ELIGIBILITY.md`.

**Phase E.** `src/climrr/wp2retrieve.py`; `scripts/wp2_terms.py` (terms
frozen, committed); then `scripts/wp2_retrieve.py` (scan, pool and candidates
frozen, committed); `docs/LITERATURE_WP2_CANDIDATES.md`.

**Phase F.** This report; `PROJECT_STATE.md`; three files added to
`KNOWLEDGE_FILES`.

## 7. Deliverables and exact file paths

**New:** `artifacts/phenomena/prototypes/P-STATE-1.v2.json`,
`data/metadata/concept_map.yaml`, `artifacts/literature/wp2_terms.json`,
`wp2_qualifying_pool.json`, `wp2_candidates.json`; `src/climrr/conceptmap.py`,
`src/climrr/bridge.py`, `src/climrr/wp2retrieve.py`;
`scripts/build_p_state_1_v2.py`, `scripts/wp2_terms.py`,
`scripts/wp2_retrieve.py`; `docs/BRIDGE_ELIGIBILITY.md`,
`docs/LITERATURE_WP2_CANDIDATES.md`,
`docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md` (tracked as placed);
`tests/test_prototype_versions.py`, `test_conceptmap.py`, `test_bridge.py`,
`test_wp2_retrieval.py`; this report; run records `reports/runs/20261008T2138*`
to `20261008T2145*`.

**Changed:** `src/climrr/compat.py` (C-2, opt-in), `src/climrr/queryscope.py`
(reads unversioned prototypes only), `tests/test_compat.py`,
`docs/DECISION_LOG.md`, `docs/MENTOR_BRIEF.md`, `docs/PHENOMENON_PROTOTYPES.md`,
`docs/PROJECT_STATE.md`, `reports/milestones/M5_WP1_REPORT.md`,
`scripts/stage_knowledge.py`.

## 8. Methods and rules that affect scientific meaning

1. **P-STATE-1 v2 windows.** Baseline 1995-2004 (line 102); future 2085-2094
   (lines 101-102 --- the range runs across the line break). Status inherited
   from P-CELL-1's `T.per_role` for the same label (`verified_from_dictionary`),
   with the same stated reading: the field entry gives no years, and its label
   is read as the decade the front matter defines.
2. **Concept map.** Two levels. A **family** term must appear, boundary-aware,
   on a cited dictionary line (validated). A **metric** may carry terms only
   with a `guidance` or `mentor` source (validated). Only `approved_lexical`
   entries match.
3. **C-2.** When C-1 fails, a claim concept that is **exactly** (after
   whitespace collapse and casefold) an approved family term of the
   prototype's family → `compatible_at_family_level`, a status distinct from
   `compatible`. An approved term of another family → `not_evaluable`.
   Direction stays `not_evaluable` on a family-level match (D-1 unchanged).
4. **Eligibility.** Concept `compatible` or family-level, geography
   `compatible`, nothing `incompatible`; the `not_evaluable` dimensions are
   always returned with the pair.
5. **Relations.** `supporting` only with metric-level concept and time,
   scenario and direction all `compatible`; otherwise at best
   `supporting_qualified`. So unknown scenario, or a family-level match, can
   never be `supporting`.
6. **Boundary rule.** Case-insensitive (`re.IGNORECASE`, no normalization;
   code-point offsets on the unnormalized string); the code points either side
   must not be Unicode letters, numbers or combining marks. `FWIs`, `FWI2`,
   `Californian`, `heat-index` do not match; `(FWI)`, `FWI-based`, `FWI_x`
   do.
7. **Retrieval.** Every string value at any depth; object keys not scanned.
   Qualify on ≥ 1 concept and ≥ 1 place hit; dedupe exact-byte duplicates
   (keep lowest id) before the cap; sort; first 12.

## 9. Results with compact tables or examples

**Concept map entries:**

| canonical_id | level | parent | terms | status | source span |
| --- | --- | --- | --- | --- | --- |
| `fire_weather_index` | family | --- | "fire weather index", "FWI" | **`approved_lexical`** (COORDINATOR, D-018) | 292, 293 |
| `heat_index` | family | --- | "heat index" | **`approved_lexical`** (COORDINATOR, D-018) | 390, 391 |
| `fwi_seasonal_value` | metric | `fire_weather_index` | *none* | **`proposed`** --- requires GUIDANCE/mentor | 346, 347, 352, 661, 663 (where described) |
| `heatindex_days_above_105F` | metric | `heat_index` | *none* | **`proposed`** --- requires GUIDANCE/mentor | 414, 680, 695 (where described) |

**WP2 terms:** concept `fire weather index`, `FWI`, `heat index`; place
`Oklahoma`, `Stephens`, `California`.

**Scan:** 1,918 items, 0 parse failures; 18 with a concept hit; 172 with a
place hit; **4 qualifying**; 0 removed as duplicates; **pool 4; candidates 4**.

| Candidate | Concept hits | Place hits |
| --- | ---: | ---: |
| `LIT-000166` | 1 | 1 |
| `LIT-000519` | 13 | 1 |
| `LIT-001501` | 11 | 22 |
| `LIT-001536` | 1 | 11 |

Per-term counts and every hit's path and span are in
`wp2_candidates.json` and `docs/LITERATURE_WP2_CANDIDATES.md`.

## 10. Validation performed

| Check | Result |
| --- | --- |
| `pytest` (`climrr` env) | **703 passed** (640 on `main` before; 63 new) |
| `scripts/verify_no_secrets_or_paths.py` | **0 hits**, run **after staging** at every commit, exit status read directly |
| Frozen M5-WP1 artifacts | `m5wp1_inputs.json` and `m5wp1_matrix.json` byte-identical to reviewed hashes (test); `verify_inputs()` passes; the matrix still re-derives row for row |
| P-STATE-1 v2 | V, D, M, G, H, C, S identical to v1; every window span equals its dictionary line; v1 file and record hashes recorded in v2 |
| Concept map | validates; refusal tests for metric terms without GUIDANCE/mentor source, family terms absent from cited lines, duplicate terms, approval without approver |
| Boundary rule | 14 cases incl. `FWIs`, `FWI2`, combining mark, underscore, hyphen, double space, astral-plane prefix |
| Eligibility | an eligible pair with scenario unknown is never `supporting` (8 combinations) |
| Retrieval determinism | second run verified identical; **full re-scan test ran against the corpus (not skipped)** and reproduced both files |
| Selection | the candidates re-derive from pool + manifest + rule; synthetic dedupe-before-cap test |
| No text stored | test: every hit holds only id, path, term, class, span and matched characters |
| `queryscope` | M4-WP0 coverage artifact still matches a fresh computation |

## 11. Failures, rejected cases, and known limitations

- **The pool is 4, not 12.** Only 18 of 1,918 items contain any approved
  concept term, and 4 of those also contain a place term. Under the ruling's
  terms (no aliases, family terms only), that is the yield. **Terms were not
  loosened.**
- **P-CELL-1 and P-COUNTY-1's baseline window cites no year span.** IC-006
  (`wildfire_summer_Hist`) records `proposed_horizon` "1995-2004" as
  `from_dictionary` but lists no line that states it. v2 cites line 102, as
  IC-001 (the heat-index family) already does. The years are not in doubt;
  the v1 citation chain is thinner than its status suggests.
- **v2's generated prose is v1's.** `description`, `description_clauses` and
  `literature_probe` still name horizons by label only; regenerating them is a
  rebuild this package did not authorize.
- **Place hits are lexical.** `Stephens` is also a surname; `California` may be
  an affiliation. Said about the terms, not about any candidate --- none was
  inspected.
- **A pre-existing gap the new test caught:** `queryscope` globbed every
  prototype file, so v2 appeared as a fourth prototype. It now reads
  unversioned records only; its tracked artifact is unchanged.

## 12. Deviations from the approved plan

1. **Branched from `87bce48`**, the current `main`, not `656044c`: `main` had
   gained the M4-WP1b blind-reading commit. Its artifacts were not opened.
2. **C-2 matches by exact membership**, as the ruling states ("exact membership
   in an approved surface-term set"), not by searching for a term inside a
   longer claim concept, which "boundary-aware" in the work package could be
   read to mean. The ruling governs. Containment would need its own ruling.
   C-2 is applied to no real data here.
3. **P-STATE-1 v2 baseline span** (field 11): the spans P-CELL-1 cites do not
   include one for 1995-2004, so line 102 is cited.
4. **v2 replaces `T.per_role.*.value`** with the exact label strings P-CELL-1
   and P-COUNTY-1 carry, keeping v1's under `value_v1`, so the existing PV-T1
   reads the windows without a code change.
5. **Family-level concept never permits `supporting`**, and **`contradicting`**
   is defined as concept positive + geography `compatible` + direction the
   only `incompatible`. Both follow D-018 items 3 and 6; neither is applied.
6. **Boundary details** the work package left open: combining marks count as
   word characters; underscore and hyphen are boundaries; internal whitespace
   is matched exactly; object keys are not scanned.
7. **Metric entries carry `source_span`** pointing to where the metric is
   described, with no terms --- context for GUIDANCE, not an approval.
8. **`queryscope.py` changed** (field 11).

## 13. Open decisions and mentor questions

| Item | Owner | Why it matters |
| --- | --- | --- |
| **Pool of 4 < 12.** Proceed with 4, or authorize a different retrieval design | GUIDANCE | the ruling's design yields 4 under its own term rules |
| **Metric-level terms** for `fwi_seasonal_value`, `heatindex_days_above_105F` | GUIDANCE / mentor | without them no real claim reaches C-1 `compatible`, so no pair can be `supporting` |
| **C-2 exact membership vs containment** | GUIDANCE | decides whether "heat index trends" is a family-level match |
| **The mentor question** now leading `MENTOR_BRIEF.md` (exact metric/scenario, or disclosed family-level support) | mentor | decides whether `supporting_qualified` is a usable bridge |
| P-CELL-1/P-COUNTY-1 baseline citation | COORDINATOR | v1 provenance gap (field 11) |
| M4-WP1b comparison and adjudication | COORDINATOR | WP2 reading waits for it |

## 14. Proposed gate status

| # | Criterion (abridged) | Status | Evidence |
| ---: | --- | --- | --- |
| 1 | M5-WP1 frozen and reproducible at original hashes | **MET** | hash test; `verify_inputs`; row-for-row re-derivation |
| 2 | M5-WP1 status is machinery validation | **MET** | D-018; M5-WP1 report field 14 |
| 3 | P-STATE-1 correction versioned, old input kept | **MET** | `P-STATE-1.v2.json`; v1 untouched; freeze names v1 |
| 4 | Exact metadata spans support the windows | **MET, with field 11's note** | lines 101-102, each quote tested against the dictionary |
| 5 | Concept map distinguishes family from metric | **MET** | `level`, `parent_family` |
| 6 | Every entry carries source, span, date, decision | **MET** | validator `REQUIRED` |
| 7 | No broad term silently narrowed | **MET** | metrics have no terms; validator refuses metric terms without GUIDANCE/mentor |
| 8 | COORDINATOR entries purely lexical/source-backed | **MET** | family terms quoted from cited lines (validated) |
| 9 | Synonym/equivalence additions separately approved | **MET** | none added |
| 10 | Eligibility: concept and geography `compatible`, no `incompatible` | **MET** | `bridge.py`, tests |
| 11 | `not_evaluable` time/scenario/direction allowed but explicit | **MET** | returned with every pair |
| 12 | No unqualified `supporting` with unknown scenario | **MET** | tested over 8 combinations |
| 13--15 | WP1b blindness, freeze, disagreements | **not this package** (Track A) | --- |
| 16 | Boundary-aware matching | **MET** | `find_term`, 14 tests |
| 17 | Retrieval terms frozen/versioned | **MET** | `6080cc3`, before the scan |
| 18 | Every hit auditable to item/path/span | **MET** | `wp2_candidates.json` |
| 19 | Pool deduplicated against the frozen corpus identity | **MET** | manifest duplicate groups; 0 removed |
| 20 | First 12 unique by stable id, no replacement | **MET** | 4 available; all taken; re-derivation test |
| 21 | Candidate ids frozen before semantic inspection | **MET** | `7d0e128`; nothing inspected |
| 22 | Labelled relevance-guided, not representative | **MET** | every artifact and document |
| 23 | WP2 reading waits for WP1b | **MET (by not reading)** | no candidate opened for meaning |
| 24 | No hit treated as a bridge | **MET** | stated; nothing downstream consumes hits |
| 25 | No QA | **MET** | none |

**Proposed status:** ready for GUIDANCE review as the **retrieval half** of
M4-WP2 plus the M5-WP1 closure actions; all binding criteria met, with the pool
shortfall (4 < 12) put to GUIDANCE.

## 15. Proposed next bounded objective

Close **M4-WP1b** (comparison and adjudication). If it does not materially
invalidate the premise, **read the 4 frozen candidates** under the WP1 rubric,
then a positive-case M5 package on adjudicated claims, P-STATE-1 v2, the
concept map, and the eligibility logic --- after GUIDANCE rules on the pool
size and on metric-level terms.
