# Bridge eligibility and the final M5 relation

**Defined, tested, and not yet applied to any real pair.** Authorized by D-018
(`docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md`). Code:
`src/climrr/bridge.py`; tests: `tests/test_bridge.py`.

The ruling keeps two questions apart, and so does the code:

1. **May this pair be reviewed as a candidate bridge?** → `candidate_bridge_eligible`
2. **What is the pair, once reviewed?** → the final relation

A candidate is **not** a validated bridge, and a pair that nothing contradicts
is **not** thereby `supporting`.

## 1. `candidate_bridge_eligible(pair)`

Reads a compatibility row (five judgments, as `climrr.compat.evaluate_pair`
writes them) and returns `(eligible, not_evaluable_dimensions)`.

A pair is **eligible** iff all three hold:

| Condition | Statuses that satisfy it |
| --- | --- |
| concept matches | `compatible` (C-1, metric level) or `compatible_at_family_level` (C-2, revised by D-019 --- see below) |
| geography matches | `compatible` |
| nothing conflicts | no dimension is `incompatible` |

Time, scenario and direction may each be `compatible` or `not_evaluable`. The
`not_evaluable` dimensions come back with the result **whether or not the pair
is eligible**, so they travel with it and cannot be dropped.

**C-2 as revised by D-019.** When C-1 fails, the claim's tagged `concept`
value is searched with the frozen boundary-aware matcher
(`climrr.conceptmap.find_term`, the same function the M4-WP2 retrieval scan
used) for the accepted surface terms of the prototype concept's family
(`approved_lexical` entries only). A hit gives `compatible_at_family_level`
and records the family, the surface term, its `[start, end)` within the
concept value, and the concept-map entry and decision id. No new surface
terms: `"heat index trends"` matches `heat_index`; `"urban heat island"`,
`"wildfire smoke exposure"` and `"FWIs"` do not. This is lexical occurrence,
not synonymy, and a family match is never metric compatibility.

## 2. The final relation (closed vocabulary)

| Relation | Permitted when |
| --- | --- |
| `supporting` | eligible; concept `compatible` at **metric** level; time, scenario **and** direction all `compatible` |
| `supporting_qualified` | eligible, but concept is family-level **or** any of time / scenario / direction is `not_evaluable`. The unmatched dimensions are carried with it |
| `contradicting` | concept positive, geography `compatible`, and the **only** `incompatible` dimension is direction |
| `related_insufficient` | always available: related, but not enough established |
| `uncertain` | always available: the reviewer cannot decide |

`check_relation(pair, relation)` raises on any relation the row does not
permit.

**Consequences, each tested:**

- **Unknown scenario against a scenario-specific prototype can never be
  `supporting`.** Every ClimRR prototype in the pilot is scenario-specific
  (RCP8.5), and every WP1 claim's scenario is `unknown`; such a pair can at best
  be `supporting_qualified`. The ruling: *"a scenario-specific ClimRR prototype
  cannot receive an unqualified `supporting` relation from a claim whose
  scenario is unknown."*
- **A family-level concept match can never be `supporting`.** A paper about the
  heat index is not, by that phrase, about days above 105°F (D-018, item 3).
- **Missing scenario is not scenario compatibility.** `not_evaluable` stays
  `not_evaluable` from the matrix through to the relation.

## 3. Evidence tiers (D-019)

Every adjudicated claim carries `evidence_tier`. The tier qualifies what a
claim can do in M5; it does not change the compatibility rules.

| Tier | Claims | What it can do |
| --- | --- | --- |
| **A** | `independently_confirmed` | strongest evidence |
| **B** | `adjudicated_modified` (scope not contested) | usable for candidate/bridge analysis when the adopted value is source-supported, the disagreement is preserved, and no unresolved issue directly determines the bridge |
| **C** | `single_reader_provisional`, or any claim on a scope-contested item | diagnostic or candidate use only; **cannot independently establish an accepted bridge** |

WP1 adjudicated set: **A 1, B 18, C 10** (`artifacts/literature/wp1_claims_adjudicated/`).
WP2 reader-1 claims are all **C** until their blind reading and adjudication.

**Claim-type rules and ties.** A rule that depends on claim type treats
`unresolved_tie` as `not_evaluable` (D-019). Today that is T-2 (a historical
`finding` ending before 2045): `compare_time` returns `not_evaluable` with
reason `claim_type_unresolved_tie`. The proposition itself stays usable where
no rule depends on its type (`LIT-000381-C3`).

**Third reader.** Not required for the whole WP1 set. **Required** if a final
accepted bridge depends materially on a scope-contested claim, an unresolved
tie that affects the bridge, or a single-reader-only semantic assertion.

## 4. What decides the relation itself

Nothing yet. Choosing between the permitted relations for a real pair is
semantic review of an adjudicated claim, which waits for the M4-WP2 blind reading,
adjudication and Phase 4 compatibility run (D-019), and a later
M5 package. The mentor question now leading `MENTOR_BRIEF.md` --- exact
metric/scenario match, or disclosed family-level support --- decides whether
`supporting_qualified` is a bridge the benchmark will use.

## 5. Retrieval governance --- R-FWI-1 v1 (D-022)

Retrieval decides which documents a later package may inspect; it is upstream
of everything above and never establishes a claim or a bridge. One governed
rule exists. Code: `src/climrr/retrieval.py`; tests: `tests/test_retrieval.py`.

**R-FWI-1 v1** (GUIDANCE source-yield ruling, 2026-10-12, D-022). In
heterogeneous scientific text bare `FWI` is polysemous --- full waveform
inversion, Forest Watch Indonesia, fatal work injuries, a fractional water index
(LITCORPUS-01 evidence: 10 of 13 diagnostic hits; LITCORPUS-00: all 11 `FWI`
hits in `LIT-001501`). So:

| A document whose fire-weather topical hits are | is |
| --- | --- |
| a longer term --- `fire weather index`, `fire-weather index`, `canadian forest fire weather index`, `canadian fwi` | eligible (`direct_topical_term`) |
| bare `fwi`, and the **same document** contains an approved disambiguator --- `fire weather`, `fire-weather`, `fire weather index`, `fire-weather index`, `canadian forest fire weather index`, `canadian fwi` | eligible (`bare_fwi_with_same_document_disambiguator`) |
| bare `fwi` only | **not eligible** (`bare_fwi_without_disambiguator`) |

- **Same-document**, not same-sentence or same-section: a paper that defines FWI
  once and uses the acronym later is kept.
- **Both locations recorded**: the first bare-term hit and the first
  disambiguator hit, each as section key, section index and `[start, end)` on
  the unnormalized string.
- **`FWI` stays in `concept_map.yaml`** as a dictionary-backed surface term.
  The rule governs retrieval eligibility only; rule C-2 above still treats `FWI` as
  a `fire_weather_index` surface term inside a claim's concept field.
- **Applies to** LITCORPUS-01, LITCORPUS-02, the legacy corpus if it is
  re-queried, and every future source (ruling action 10).

**Matcher differences, disclosed.** `climrr.retrieval` uses the frozen repo
matcher (`climrr.conceptmap.find_term`). The external collection runs used
DuckDB `regexp_matches(text, '\b'+term+'\b', 'i')`, and their hit offsets were
computed with Python `re` `\b`. The three agree on ordinary text and differ in
two edge cases: `FWI_x` (an underscore is a boundary only for the repo
matcher), and a non-ASCII letter touching the term, e.g. `éFWI` (a boundary only
for DuckDB, whose `\b` is ASCII). Neither difference changes the synthetic-test
results (`tests/test_litcollect_tools.py`); its effect on the 705k arms is
unmeasured, because the texts are on Eagle.

## 6. Four layers, kept apart (D-025)

| Layer | Vocabulary | Decides | Code |
| --- | --- | --- | --- |
| **Collection** | the frozen query files: topical group (concept-map family terms, incl. D-025 `additional_surface_terms` of either status) AND a context clause (precision only, never an alias) | which documents a source run returns | `scripts/litcollect/run_query.py` |
| **Retrieval --- R-FWI-1** | bare `fwi` + the six disambiguators | whether a returned document is fire-weather eligible | `climrr.retrieval` |
| **C-2 family-level claim matching** | dictionary-backed `accepted_surface_terms` + `approved_lexical` additional forms (`fire-weather index`, `canadian forest fire weather index`, `canadian fwi`, `heat-index`); **not** `approved_family_term` forms --- an occurrence of `extended heat index` masks the `heat index` inside it | `compatible_at_family_level` for a claim's concept field | `climrr.compat.family_term_hits`, `climrr.conceptmap.c2_terms` |
| **Metric-level compatibility (C-1)** | metric canonical ids only; no surface term yet (`fwi_seasonal_value`, `heatindex_days_above_105F` are `proposed`) | `compatible` | `climrr.compat.compare_concept` |

**None of the first three establishes metric compatibility.** A collection hit,
an R-FWI-1 admission and a C-2 family match are each lexical; only C-1 gives
`compatible`, and no D-025 term reaches it (tested). `extended heat index` is
heat-index-family collection and retrieval vocabulary, not a synonym of heat
index and not the ClimRR threshold metric `heatindex_days_above_105F`.

## 8. Geography role, `cited_study_area`, and the prospective C-2 mask and G-2 revision (D-027)

*(§7, the Stage 2 candidate-surface-form governance, is on `work/trackb-stage2`;
this section is numbered to follow it after both merges.)*

GUIDANCE, 2026-10-20 (`docs/M4_WP4_TRACKB_GUIDANCE_RULING.md`, D-027), on the
M5-WP4 layer `climrr.m5wp4` (beside the frozen `compat.py`, which is unchanged;
**approved**).

**G-R --- the geography-role gate enters G-1: approved.** A place string alone is
insufficient. Affiliation, citation/person, contextual geography or data-source
geography never becomes geographic compatibility. As implemented in M5-WP4:
role class `affiliation` or `citation_or_person` → `not_evaluable` whatever the
place; an exact G-1 label match is `compatible` only for role class `study_area`
or `cited_study_area`, otherwise `not_evaluable`; G-R never gives `incompatible`.

**Conservative role on disagreement: approved.** The more conservative geography
role is used unless both readers independently support study geography (rule
3-role, `climrr.wp4adj.ROLE_CONSERVATIVE_ORDER`).

**`cited_study_area` is study geography, with evidence-tier qualification:
approved.** It may satisfy the role gate, but the claim's evidence tier (§3)
still constrains whether it can establish an accepted bridge.

**Prospective C-2 mask list (future runs only):**

| Masked compound | Masks | Decided |
| --- | --- | --- |
| `extended heat index` | the `heat index` inside it | D-025 (`approved_family_term`) |
| `standardized heat index` | the `heat index` inside it | **D-027, prospective** |

The rule, as ruled (verbatim):

> **A recognized compound concept containing an approved family term must mask that inner phrase when the compound's equivalence has not been explicitly approved.**

There is no approved equivalence between Standardized Heat Index and the ClimRR
heat-index family. **The frozen M5-WP4 matrix is not rewritten**: its three
`LIT2-001160-C4` pairs keep the `possible_collision: standardized heat index`
flag and their recorded judgments, and `artifacts/bridges/m5wp4_matrix.json` /
`.csv` keep their SHA-256 (tested). WP4 is not rerun to apply the mask.

**Prospective G-2 semantics (documented here; implemented in a later package,
not now).** G-2 may return `incompatible` only when the **entire** explicit
geography is wholly disjoint from the prototype. For a multi-region claim:

| Claim geography | G-2 result |
| --- | --- |
| all listed regions disjoint from the prototype | `incompatible` |
| a mixture of disjoint and potentially relevant regions | `not_evaluable` |
| a broad region containing the prototype but not resolving to the required granularity | `not_evaluable` |
| exact supported geography | G-1 / G-R |

The M5-WP4 G-2 judgments are as frozen; M5-WP4 is not rewritten. Containment and
granularity rules for state, county, national, climate-region and multi-region
geographies must be declared before any evaluation that uses them (ruling,
scientific risk 7); no ad hoc containment (e.g. `San Diego County` →
`California`).
