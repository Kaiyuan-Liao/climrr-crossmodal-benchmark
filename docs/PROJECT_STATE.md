# Project state

One screen. **Refresh this file at the end of every work package.** A stale
state file is worse than a thin one: the M0 cold-resume trial showed a fresh
session reasoning correctly from out-of-date facts and repeating them.

| | |
| --- | --- |
| **Current milestones** | **M1 --- data grounding and metadata audit: open.** Criterion 1 will be evaluated on **provisional statuses, explicitly declared** (D-014). **M4:** M4-WP0 PASS (D-016); M4-WP1 PASS WITH ACTIONS (D-017), merged `0053968`; **M4-WP1b PASS WITH ACTIONS** and **M4-WP2 retrieval PASS (sample 4)** (D-019), both merged at `e7da7cc`; **M4-WP2 reading complete** and merged into `main` at `ccd2d24` (pending GUIDANCE review at `2206c00`). **M5-WP2 positive-case run: 0 eligible pairs of 78.** **M4-WP3 --- PASS WITH ACTIONS (D-025)** on reviewed head `6b2b5a6` (pushed `origin/work/m4-wp3`, not merged); closeout done. **M4-WP4 + M5-WP4 (Track A) --- PASS WITH ACTIONS (D-027)**, reviewed `c0be540`: read twice and adjudicated; **0 eligible pairs of 354**, a bounded zero for these 20 papers only. **Track B Stage 2 run 1 --- PASS as diagnostic (D-027)**, reviewed `2331e19`; **run 2 (family level) executed and ingested, pending GUIDANCE**. **M5:** **M5-WP1 closed --- PASS WITH ACTIONS, machinery validation only (D-018)**, merged `55decb3` |
| **Active task** | **Track B run 2 executed and ingested (diagnostic `TRACKB-SURVEY-RUN2`) --- `work/trackb-run2` from `main` `d7032de`, not pushed, not merged; pending GUIDANCE review** (`reports/milestones/TRACKB_STAGE2_REPORT.md` §§9, 13--15). *Before:* driver v4 ready (`3ccb4ba`). *Earlier:* **Both tracks accepted by GUIDANCE (D-027) and combined:** `work/m4-wp4-adj` (Track A, head `a7479bb`) merged into `work/trackb-stage2` (Track B, head `e1ae9d6`); not pushed, not merged to `main` --- **Kaiyuan performs the merge to `main`**. Ruling bookkeeping done on both branches (Track A: reports 14--15, `BRIDGE_ELIGIBILITY.md` §8; Track B: `normalization_table_v1.yaml` frozen, survey doc, mentor brief). **Next (not started):** Track A-next unit-granularity diagnostic; Stage 2 run 2 at family level after a driver update. **QA not authorized.** *Previous:* Track A --- M4-WP4r3 adjudication + M5-WP4 (`work/m4-wp4-adj`); Track B --- Stage 2a and survey run 1 (`work/trackb-stage2`); see `reports/milestones/M4_WP4_REPORT.md`, `M5_WP4_REPORT.md`, `TRACKB_STAGE2_REPORT.md` |
| **Latest accepted commit** | **`e7da7cc`** --- the merge of M4-WP1b (reviewed `25a86e5`) and M4-WP2 retrieval (reviewed `7ddee2c`) into `main`, both accepted under D-019. Previous: **`55decb3`** (M5-WP1, D-018; scan fix `656044c`); **`0053968`** (M4-WP1, D-017); `6f24b78` (M4-WP0 chain, D-016); `62c9137` (M1-WP1, D-009). It does **not** pass M1 |
| **Tooling on `main`** | `d68ba15` --- merge of `work/knowledge-staging` (`c13a3d4`, `scripts/stage_knowledge.py`) on top of `6f24b78`. **No scientific content**; not a GUIDANCE-accepted package, and not an accepted scientific state |
| **Sophia-verified commit** | `2b7345f` --- the pinned commit the cross-host reproduction ran at. The literature corpus is **not** on Sophia (runbook §8b) |
| **Branch lineage** | M1-WP2 → M1-WP3 → M1-WP3b → M4-WP0 merged at `6f24b78`; M4-WP1 merged at `0053968`; M5-WP1 merged at `55decb3` (reviewed head `c1010f0`), scan fix `656044c`; M4-WP1b blind reading `87bce48` on `main`. **`work/m4-wp2-retrieval`** branches from `87bce48`: `8ee8857` (D-018 bookkeeping), `7ba2657` (P-STATE-1 v2), `f586d29` (concept map, C-2), `13c56fb` (eligibility), **`6080cc3` (terms frozen)**, **`7d0e128` (candidates frozen)**, then the report commit `7ddee2c`. **`work/m4-wp1b-adj`** branches from `7ddee2c`: **`0706679`** (Phases A--D), `25a86e5` (report). Both merged into `main` at **`e7da7cc`** (D-019). **`work/m4-wp2-read`** branches from `e7da7cc`: `410a7d0`, `258536a`. **`work/m4-wp2-blind`** (`939111e`) branches from `e7da7cc`. **`work/m4-wp2-adj`** branches from `258536a`: merge of the blind branch `ab80335`, `59880d7` (adjudication, M5-WP2 freeze), then the matrix/report commit `2206c00`; merged into `main` at **`ccd2d24`**. **`work/m4-wp3`** branches from `ccd2d24`. **`work/m4-wp4-read`** from `38116a0` (`e0857aa`, `72617da`); **`work/m4-wp4-blind`** (`c452d7d`) from `38116a0`; **`work/m4-wp4-adj`** from `72617da`: `d90595c` (blind merge), `90d55fc` (scan fix), `6c856e2` (adjudication), `220ca84` (M5-WP4 freeze), `8436c25` (matrix), then the report commit. **Not pushed, not merged** |
| **M4-WP0 commits** | `52a994a` (Phases A–E); **`1e2fd9f`** (report and state --- **the reviewed head**); then `e4a9de0`, the D-016 pre-merge bookkeeping |
| **M4-WP1 sample** | `LIT-000001, 000191, 000381, 000571, 000761, 000951, 001141, 001331, 001521, 001711` --- every 190th id; no duplicate skip; `wp1_sample.json` SHA-256 `5cb81f95…`, committed before any file was opened |
| **Prototypes built from** | `56eb10d` --- v1 records unchanged since M1-WP3b. **P-STATE-1 v2** (`P-STATE-1.v2.json`, D-018) adds explicit year windows only; V/D/M identical to v1; the frozen M5-WP1 input still names v1 |
| **M0 gate** | **PASSED --- PASS WITH ACTIONS**, GUIDANCE, at commit `b87564b` (D-006) |
| **Rulings in force** | **D-027** (Track A + Track B PASS WITH ACTIONS; G-R; prospective C-2 mask and G-2; unit-granularity diagnostic next; family-level run 2; narrow orthographic normalization), **D-025** (M4-WP3 PASS WITH ACTIONS; LITCORPUS-02 working corpus; five terms governed; WP4 10+10 sample; Stage 2a--2c diagnostics), **D-021** (concept-first collection), **D-022** (source yield; LITCORPUS-01 a pilot; **R-FWI-1**; no reading), D-009, D-011, D-012, D-013 + D-013-A1, D-015, D-016, D-017, D-018, **D-019 (M4-WP1b PASS WITH ACTIONS; rule-3 trimming and J-1 approved; `LIT-000381-C3` tie and `LIT-000571` contest kept; evidence tiers A/B/C; C-2 revised; WP2 retrieval PASS with 4; reading of the four authorized, two readers + adjudication, then compatibility with P-STATE-1 v2)** |
| **Owner decisions since** | **D-026** (Kaiyuan, 2026-10-20): Stage 2a inventory at measure level --- one concept per output quantity the dictionary narrative describes; assigns no column meaning. **D-014** (Kaiyuan, 2026-09-28): proceed on the "our reading" basis to test what QA could be generated; every `inferred_candidate` and `derived_from_inferred` status carried through; **promotes nothing, and does not authorise QA generation** |
| **Meetings since the last refresh** | **Mentor 2026-10-09:** direction D-020 --- concepts from the table units first, then collect papers for them; keep the three units. **Mentor 2026-10-13:** shard yields reported, a larger source asked for; outcome = JL's Drive link (D-023). *Earlier:* **Group 2026-09-14:** "No material objection to the prototype-unit design was raised." --- not validation, no semantic confirmed. **Mentor 2026-09-17 and 2026-09-24:** **no review of the answer sheet occurred** (R-003); nothing promoted |
| **Blockers** | **M1** promotion of any column: blocked on the mentor, who has not reviewed the sheet. **M1 remains open.** **Next relevance-guided step:** waits on the mentor (family-level usefulness; widen places or change the unit) and GUIDANCE; any WP2b must be predeclared. **Metric-level concept terms** (`fwi_seasonal_value`, `heatindex_days_above_105F`): `proposed`, need GUIDANCE or the mentor. **QA generation: not authorised by any ruling.** **Reading of any LITCORPUS-01/02 paper: not authorised** (D-022) |

## Where things stand --- Track B run 2 executed and ingested (2026-10-21)

- **Run 2 executed on Polaris** by Kaiyuan (20:02--20:18 Z, `--mode family`,
  `gpt-oss-120b`); log pins verified (driver `f929ab6a…`, prompt F `7097c86c…`,
  table `80a5e0e3…`, inventory, clause, index; 120,050 context documents).
  Ingested as **`TRACKB-SURVEY-RUN2`**: 132 files, `manifest.csv` **`1182deea…c363`**,
  under `diagnostics`; **run 1 untouched** (`74ba7d7c…125d`, test). Login node,
  environment and Python not recorded in the run outputs.
- **14 rows `ok`; every family `status: candidate_family`** (hypotheses, not
  approved). 112 forms, 112 searched, 0 over cap; **no normalization rule fired**.
- **Finding --- three coverage levels:** measure phrases **0--2** (heat-index
  measures); concept-map family terms **548** (FWI group) / **1,080** (`heat
  index`); model-proposed families **2,681--143,266**, often broader than the
  measure (`hydrology` with `moisture`; `temperature` with `heat`, `cold`;
  FWI families from non-concept-map terms; thresholds on `hot days`). No family
  count attributed to a measure. Doc: `docs/CONCEPT_COVERAGE_SURVEY.md`.
- Mentor brief (2026-10-22): the three-level sentence; concept-map counts for
  FWI and heat index only (the other five families have no concept-map entry).
- **Next:** GUIDANCE review of run 2. **QA not authorized.**

## Where things stand --- Track B run 2 driver (2026-10-21)

- **`survey_driver.py` v4** (`f929ab6a…af9f`): `--mode measure` (default) is v3,
  byte-identical outputs (test); `--mode family` = prompt F (`7097c86c…7931`),
  `family.json` `status: candidate_family`, frozen table applied before the
  sanitizer (originals kept, rule ids; 10 words for a normalized form, 6
  otherwise), family counts beside run-1 measure counts, never conflated.
  `run_query.py` v3 unchanged. Context-cache and run-1 checks fail closed.
- **Disclosed choices for the COORDINATOR:** measure-mode normalization opt-in
  (`--normalize`) to keep v3 byte-identity; Polaris invocation from
  `$LITCOLLECT_ROOT_POLARIS` with `PYTHONPATH="$CLIMRR_REPO/src"` (relative paths,
  as run 1). Knowledge list gains `LITERATURE_WP4_READING.md`,
  `DICTIONARY_CONCEPTS.md`. **Run 1 unchanged; nothing executed; QA not authorized.**

## Where things stand --- GUIDANCE ruling D-027, pre-merge bookkeeping (2026-10-20)

- **D-027: PASS WITH ACTIONS** for Track A (M4-WP4 / M5-WP4, reviewed `c0be540`;
  bounded zero of 354 accepted) and Track B (Stage 2 run 1 **PASS as diagnostic**,
  reviewed `2331e19`). Ruling: [M4_WP4_TRACKB_GUIDANCE_RULING.md](M4_WP4_TRACKB_GUIDANCE_RULING.md).
  Both merges authorized after bookkeeping; **Kaiyuan performs them**.
- **Track B bookkeeping (this branch):** D-027 logged; orthographic table
  `normalization_table_v1.yaml` (N-1 … N-7) frozen and pinned, driver unchanged;
  survey doc carries the B3 sentence and the run-2 side-by-side note; Polaris
  Python patch `unknown`; mentor brief for 2026-10-22 (seven discussion families,
  questions a--c). **Track A bookkeeping** is on `work/m4-wp4-adj` (`a7479bb`), now merged into this branch.
- **Next (not started):** Track A-next unit-granularity diagnostic; Stage 2
  run 2 at family level after a driver update. **QA not authorized.**

## Where things stand --- Track B survey run 1 (2026-10-20)

- **Run 1 executed on Polaris** (`polaris-login-01`, 21:54--22:09 Z; `gpt-oss-120b`
  on Metis) from untracked copies whose SHA-256 equal the tracked **v3** tools,
  after an aborted first attempt (offsets stage, >3 h; no outputs kept). v3 = an
  opt-in `--no-hits` in `run_query.py`, passed by the driver; logged in D-026.
- **Ingested as diagnostic `TRACKB-SURVEY-RUN1`**: 122 files, `manifest.csv`
  `74ba7d7c…125d`, pinned under `diagnostics` (not `external_corpora`); the 12
  header-only `topical/hits.csv` not copied. Every row's counts re-derive from its id
  files (test). **12 `ok`, 2 `error`** (DC-011, DC-013: every proposed phrase had
  `°`/`>`, so no searchable phrase; the model answered).
- **Facts** (diagnostic coverage counts, not prevalence): DC-007 topical set =
  the LITCORPUS-02 fire diagnostic, **548 = 548, same ids**; DC-001/002/003 are
  99.6--100 % bare `temperature` / `precipitation`; heat-index measures DC-009--014
  reach **0--2** vs **1,082** for the family group (`heat index` alone 1,080).
- **Open for GUIDANCE:** Q-a (family-level run 2), Q-b (thresholds family-level
  only), Q-c (sanitizer normalization). Nothing moved in `concept_map.yaml`, no
  column status, index 117 unlabeled.

## Where things stand --- Track B Stage 2a (2026-10-20)

- **Stage 2a inventory built** (diagnostic, D-025): `data/metadata/dictionary_concepts.yaml`,
  **14** concepts at measure level (D-026, Kaiyuan's answer to an EXECUTOR escalation),
  **0** `listed_only`; every name and passage an exact slice of one page's pypdf 6.18.0
  text; `family_hint` all null; `verified_columns` all empty (no verified column has a
  resolution record). **No column status moved; index 117 unlabeled.**
- **Survey context clause v1** (diagnostic) tracked and pinned; **revised
  `survey_driver.py` (`877fec47…7155`)** and `probe_alcf_inference.py` tracked
  byte-identical to the delivered files, tested against a mock server. Candidates are
  inert (`docs/BRIDGE_ELIGIBILITY.md` §7). **D-026 confirmed by the COORDINATOR.**
- **Driver behaviour to know before the Polaris run:** 7 of 14 stored dictionary names
  are not searchable; DC-001/002/006 get parenthetical-stripped variants (DC-001/002
  both search bare `temperature`); the four threshold concepts (shared passage) rely on
  model terms only. A failing concept gives a `status: "error"` row and the run
  continues; error rows are not retried on restart.
- **Next:** Kaiyuan runs 2b/2c on Polaris with the pinned driver; GUIDANCE reviews.

## Where things stand --- M4-WP4 adjudication and M5-WP4 (2026-10-20)

- **Branch `work/m4-wp4-adj`** (not pushed, not merged): merge of the blind reading
  `d90595c`; scan fix `90d55fc`; **adjudication `6c856e2`**; **M5-WP4 freeze `220ca84`**
  (before the matrix); matrix `8436c25`; reports and state in the head commit.
- **Scan fix:** `72617da` failed the secrets/paths scan (2 hits, a credential-class word
  in the `wp4_claim_screens.py` docstring, embedded in its JSON) although its report said
  0. Reworded; `wp4_claim_screens.json` `4fec0b51…` → `125a566d…`, counts unchanged.
- **Adjudication (D-019 rules; adjudicator = reader 1):** both readings pinned and tested
  against their commits; 300 + 377 spans re-slice, 0 failures. Scope **20/20**.
  **50 aligned, 33 reader-1-only, 35 reader-2-only.** Tiers **A 3, B 47, C 68**; no
  override; 1 `unresolved_tie` (`LIT2-000203-C2`, claim_type). New **rule 3-role**
  (geography role by class, more conservative adopted); new class `cited_study_area`.
  `LIT2-001075` prior exposure recorded. Hit precision carried: blind role vs reader-1
  place-hit class --- 5 agree, 1 disagree, 17 not comparable (of 23).
- **M5-WP4** (118 claims × P-CELL-1, P-COUNTY-1, P-STATE-1 v2 = 354): **0 eligible**.
  Concept family-level 12 (8 claims); geography compatible 2 (bare `California` vs
  P-STATE-1, concepts not in a pilot family), role-gated 2 (contextual); incompatible 57
  (T-2 48, G-2 9); scenario `not_evaluable` 354/354, **named scenario 0**. **G-R** (role
  gate) and the granularity reason live in `m5wp4.py`; `compat.py` unchanged.
  **SHI:** `LIT2-001160-C4` × 3 flagged `possible_collision`, no mask.
- **Open for GUIDANCE:** criterion 16 (blind base held hits + prototypes; put to
  Kaiyuan); rule 3-role order and `cited_study_area`; SHI; background-citation
  eligibility; G-2 on a continent list naming North America (`LIT2-000786-C1`).
- Documents: [LITERATURE_WP4_ADJUDICATION.md](LITERATURE_WP4_ADJUDICATION.md),
  [M5_WP4_COMPATIBILITY.md](M5_WP4_COMPATIBILITY.md),
  [../reports/milestones/M4_WP4_REPORT.md](../reports/milestones/M4_WP4_REPORT.md),
  [../reports/milestones/M5_WP4_REPORT.md](../reports/milestones/M5_WP4_REPORT.md).

## Where things stand --- M4-WP4 reader-1 reading (2026-10-19)

- **On `work/m4-wp4-read` only** (from `38116a0`; not pushed, not merged). The blind
  reader must work from `main` without this branch, the hit files or the prototypes.
- **Phase A:** sample = manifest; 20/20 source files matched before any decode.
  `LIT2-001075` = `LIT-001536` (read in M4-WP2) carries `prior_exposure`; no WP2
  artifact or bridge file opened.
- **Phase B (frozen `e0857aa`):** 19 `in_scope_hazard`, 1 `ambiguous` (`LIT2-000803`);
  **83 claims** (59 finding, 19 background citation); 300 spans exact.
- **Phase C (after reading):** concept hits substantive in **6** items (fire 2, heat 4),
  incidental 13, collision 1 (`001160`, "standardized heat index"); every bare `fwi`
  is the fire index. Place hits study-area in **8** items; `california` is an
  affiliation in 2 items (UC Irvine; Palmdale flight base); `stephens` is a citation
  surname (1 item); `oklahoma` study-area in both its items.
- **Screens (not compatibility):** US geography 42 claims; pilot family term in
  `concept` 8 (1 = the SHI collision); named scenario **0**.
- Documents: [LITERATURE_WP4_READING.md](LITERATURE_WP4_READING.md),
  [../reports/milestones/M4_WP4_REPORT.md](../reports/milestones/M4_WP4_REPORT.md)
  (fields 1--9; 10--15 pending).

## Where things stand --- M4-WP3 closeout and M4-WP4 sample (2026-10-19)

- **D-025: M4-WP3 PASS WITH ACTIONS** on `6b2b5a6`. LITCORPUS-02 is the working
  concept-first **candidate** corpus (not representative); LITCORPUS-01 stays the
  pilot, sectionization closed; Q22 open, not a blocker; matcher difference a
  disclosed limitation (no source-effect estimate).
- **Concept map:** `fire-weather index`, `canadian forest fire weather index`,
  `canadian fwi`, `heat-index` are `approved_lexical` (C-2 participates);
  `extended heat index` is `approved_family_term` (collection / retrieval only,
  masks the `heat index` inside it, never C-2, never metric). Frozen WP2 terms
  and M5-WP2 inputs keep their pre-D-025 hashes; the M5-WP2 matrix reproduces.
- **M4-WP4 sample frozen before reading** (`58e0fd6`): fire `LIT2-000185`,
  `000366`, `000499`, `000560`, `000673`, `000786`, `001063`, `001157`, `001236`,
  `001308`; heat `LIT2-000084`, `000203`, `000315`, `000470`, `000662`, `000803`,
  `000927`, `001075`, `001160`, `001293`. **`LIT2-001075` = `272852900` =
  LITCORPUS-00 `LIT-001536`**, already read twice in M4-WP2 --- kept (no manual
  replacement); for the reading package to handle.

## Where things stand --- M4-WP3 concept-first provenance (2026-10-19)

- **Mentor direction (D-020) and two GUIDANCE rulings (D-021, D-022) logged.**
  Concepts first, then collection; no US place in collection; year / venue /
  authors `unknown`; diagnostics are never a corpus; **R-FWI-1**: bare `FWI`
  admits only with a same-document fire-weather disambiguator, `FWI` stays in
  `concept_map.yaml` (hash unchanged, tested).
- **LITCORPUS-01-conceptfirst-v1** (S2ORC shard, 54,081 records *as reported by
  the tool team*): **4** fire, **10** heat; diagnostics 13 / 11; 2 of the 4 fire
  papers are FWI collisions. **R-FWI-1 retroactively (Polaris, `968e7ba`): 2 of 4
  admitted** (`134165809`, `188013273`); the two excluded are the two collisions.
  Sectionization deferred for GUIDANCE.
- **LITCORPUS-02-conceptfirst-705k-v1** (D-023 source, `full_705k_v2_filtered.zip`
  from JL, 186,346 files; filter unknown, Q22): same queries byte for byte;
  fire raw 495 → **448**, heat **861**, overlap 1 (`270275181`), union
  **1,308** with frozen `LIT2-000001…001308`; 10 redundant exact-byte copies,
  kept. LITCORPUS-00 is wholly inside the source (1,918/1,918); 4 + 10 of it in
  the arms, byte-identical. **100 directories, not 101** (no `63`).
- **Geography preflight frozen, unread:** `( oklahoma OR stephens OR california )`
  → 16,457 source docs; candidates **fire 100** (CA 96, Stephens 10, OK 3),
  **heat 143** (CA 136, OK 13, Stephens 3), first-hit locations recorded. Role
  of each place term unknown until reading.
- Documents: [LITCORPUS01_SHARD_PILOT.md](LITCORPUS01_SHARD_PILOT.md),
  [LITCORPUS02_PROVENANCE.md](LITCORPUS02_PROVENANCE.md),
  [BRIDGE_ELIGIBILITY.md](BRIDGE_ELIGIBILITY.md) §5,
  [../reports/milestones/M4_WP3_REPORT.md](../reports/milestones/M4_WP3_REPORT.md).

## Where things stand --- M4-WP2 adjudication and M5-WP2 (2026-10-08)

- **Two readings of the four, adjudicated** by the WP1b rules: scope agrees
  4/4; 13 aligned pairs (6 `independently_confirmed`, 7 `adjudicated_modified`),
  7 reader-1-only, 6 blind-only; **tiers A 6, B 7, C 13**; no override. The
  adjudicator is reader 1. The one pilot-term claim (`LIT-000519-C5`, "FWI"
  background) was **not** found by the blind reader --- tier C.
- **M5-WP2 positive-case run** (inputs frozen at `59880d7` before the matrix):
  26 claims × P-CELL-1, P-COUNTY-1, **P-STATE-1 v2** = 78 pairs. **0 eligible.**
  Concept positive 2 (family-level "FWI", no geography → `related_insufficient`);
  geography compatible **0** (closest: "Dewey County, NW Oklahoma"; "California,
  Arizona and Nevada"; inferred "Oklahoma and Texas panhandles"); scenario
  `not_evaluable` 78/78; 3 `incompatible` (T-2, a 2020-2023 prison-heat finding).
- **Criterion 6 not verifiable from artifacts**: the blind branch never held
  reader 1's outputs, but its base holds the hit list and prototypes and its
  summary has no protocol disclosure --- put to Kaiyuan.
- **For the mentor (2026-10-09)**: [MENTOR_REPORT_2026-10-09.md](MENTOR_REPORT_2026-10-09.md)
  --- plain language, three questions.
- Documents: [LITERATURE_WP2_ADJUDICATION.md](LITERATURE_WP2_ADJUDICATION.md),
  [M5_WP2_COMPATIBILITY.md](M5_WP2_COMPATIBILITY.md),
  [../reports/milestones/M4_WP2_REPORT.md](../reports/milestones/M4_WP2_REPORT.md),
  [../reports/milestones/M5_WP2_REPORT.md](../reports/milestones/M5_WP2_REPORT.md).

## Where things stand --- M4-WP2 reading, Phase 1, and D-019 (2026-10-08)

- **D-019 recorded** (GUIDANCE, placed by Kaiyuan): WP1b PASS WITH ACTIONS; WP2
  retrieval PASS with a sample of **4**; evidence tiers; C-2 revised; reading of
  the four authorized. Open cleanup: P-CELL-1/P-COUNTY-1 baseline citations.
- **Evidence tiers** on the WP1 adjudicated set: **A 1, B 18, C 10** (C = the
  five scope-contested `LIT-000571` claims, three reader-1-only, two
  blind-only). A test proves the records changed only by `evidence_tier`.
- **C-2 revised**: an approved family term occurring, boundary-aware, inside the
  claim's concept value → `compatible_at_family_level`, with term, span and
  decision id; same matcher as retrieval. `"heat index trends"` matches;
  `"urban heat island"`, `"wildfire smoke exposure"`, `"FWIs"` do not. Internal
  whitespace is now matched exactly (a double space no longer matches).
- **Reader 1 read the four** (all `in_scope_hazard`, 5 claims each, 20 total),
  claims built before the hit list was opened. **Hits after reading: 26
  substantive, 35 incidental.** `Stephens` is an author surname; `California`
  is never an affiliation; **all 11 `FWI` hits in `LIT-001501` are a
  fractional water index (soil moisture)**; only `LIT-000519`'s FWI hits are
  substantive (a literature review).
- **Screens:** 11 claims name a US place (5 explicit); **1** has an approved
  pilot term in its concept field (`LIT-000519-C5`, "FWI", background,
  geography `unknown`); **0** name a scenario. No compatibility run.
- Documents: [LITERATURE_WP2_READING.md](LITERATURE_WP2_READING.md),
  [../reports/milestones/M4_WP2_REPORT.md](../reports/milestones/M4_WP2_REPORT.md)
  (fields 1--9; 10--15 pending).

## Where things stand --- M4-WP1b comparison and adjudication (2026-10-08)

- **Both readings frozen and pinned.** The blind records equal their `87bce48`
  blobs (test); every span of both readings --- 96 + 85 --- re-slices from the
  hash-verified sources, **0 failures**. Neither reading was edited.
- **Scope agreement 6/10.** Agreement on the five papers both read as in scope
  and on `LIT-000761` (both `ambiguous`). All four disagreements are reader 1
  `off_topic`/`in_scope` vs reader 2 `ambiguous`: three become `ambiguous`
  (R1c; no first-pass claims there), and **`LIT-000571` becomes `in_scope_hazard
  (contested)`** --- its five claims are `adjudicated_modified`, "scope
  contested by blind reader"; the blind reader had rejected the passages under
  two of them.
- **Claims: 19 aligned, 8 reader-1-only, 2 reader-2-only.** Geography agrees
  least (5/19 exact), almost entirely on the tag (explicit vs inferred for the
  same place); scenario agrees 19/19 (all `unknown`).
- **Statuses (29 claims): 1 `independently_confirmed`** (`LIT-001141-C1`),
  **23 `adjudicated_modified`**, **5 `single_reader_provisional`** (3 first-pass,
  2 new `blind_reader_only`), **0 `rejected_on_review`**. One unresolved tie
  (`LIT-000381-C3`, claim_type); one post-rule override (J-1, smoke-exposure
  regimen kept in `experimental_condition`). Originals untouched; adjudicated
  set in `artifacts/literature/wp1_claims_adjudicated/`.
- **Rule 3 was operationalised as span-limited trimming** (report field 12):
  adopted values hold only what both readers support and the cited span states.
- **Field 13: the premise stands.** A lexical screen of all 48 recorded claims
  finds no pilot concept term, no US place term and no non-`unknown` scenario in
  either reading; the blind reader found nothing of that kind reader 1 missed.
- **The adjudicator is reader 1** (prototype-exposed). GUIDANCE may require a
  third party for the contested items.
- Documents: [LITERATURE_WP1B_ADJUDICATION.md](LITERATURE_WP1B_ADJUDICATION.md),
  [../reports/milestones/M4_WP1B_REPORT.md](../reports/milestones/M4_WP1B_REPORT.md).

## Where things stand --- M4-WP2 retrieval and D-018 closure (2026-10-08)

- **M5-WP1 closed: PASS WITH ACTIONS, machinery validation only (D-018).** Its
  inputs and matrix are pinned by test at their reviewed hashes.
- **P-STATE-1 v2** adds baseline 1995-2004 and future 2085-2094, citing
  dictionary lines 101-102 with P-CELL-1's status for the same labels; no
  ClimRR value changed. Found on the way: **P-CELL-1's own baseline window
  cites no year span** (IC-006 lists none) --- the years are not in doubt,
  but the citation chain is thinner than the record suggests.
- **`data/metadata/concept_map.yaml`**: `fire_weather_index` ("fire weather
  index", "FWI") and `heat_index` ("heat index") as **families**,
  `approved_lexical` by COORDINATOR; `fwi_seasonal_value` and
  `heatindex_days_above_105F` as **metrics**, `proposed`, **no terms**. Rule
  **C-2** gives `compatible_at_family_level` --- never `compatible` --- by exact
  membership, and only when a concept map is passed.
- **`bridge.py`**: candidate eligibility and a closed relation vocabulary;
  unknown scenario or a family-level concept can never be `supporting`.
  Defined, tested, applied to nothing.
- **WP2 retrieval**: 6 frozen terms; 1,918 items scanned; 18 with a concept
  hit, 172 with a place hit, **4 with both**. **Pool 4 < cap 12**; all four are
  candidates: `LIT-000166`, `LIT-000519`, `LIT-001501`, `LIT-001536`. Terms
  not loosened. **No candidate read.**
- Documents: [LITERATURE_WP2_CANDIDATES.md](LITERATURE_WP2_CANDIDATES.md),
  [BRIDGE_ELIGIBILITY.md](BRIDGE_ELIGIBILITY.md),
  [../reports/milestones/M4_WP2_RETRIEVAL_REPORT.md](../reports/milestones/M4_WP2_RETRIEVAL_REPORT.md).

## Where things stand --- M5-WP1 (2026-10-08)

- **All 81 pairs (27 claims × 3 prototypes) evaluated once each, by rule.** Each
  pair has five judgments --- concept, geography, time, scenario, direction ---
  each `compatible` / `incompatible` / `not_evaluable` with a rule ID, both
  compared values (raw and derived, each with its derivation rule) and a reason.
  No embedding, no similarity, no model judgement. Inputs frozen by file and
  record hash (`m5wp1_inputs.json`, `bc22b4fa…`) before any comparison code.
- **Counts:** concept 0/0/81, geography 0/39/42, time 0/14/67, scenario
  0/0/81, direction 0/0/81 (compatible / incompatible / not_evaluable).
  **0 pairs all-compatible.** 39 pairs carry ≥1 `incompatible`: **G-2** (a named
  country outside the US --- China, India, Tajikistan, Australia) ×39 and
  **T-2** (a `finding` whose explicit year range ends before 2045) ×14; every
  T-2 falls on a pair G-2 already marks. **42 pairs fail only by being
  `not_evaluable`.**
- **The positive path works on fixtures:** a synthetic claim against the real
  P-COUNTY-1 and P-CELL-1 records is `compatible` on all five (tested).
- **Zero is structural under these rules.** No concept mapping is approved, so
  C-1 can match only a claim concept that *is* a canonical ID; and `scenario` is
  `unknown` 27/27. No real claim could have been all-compatible. **A
  relevance-guided M4-WP2 under the same rules would also give zero** --- a
  concept-mapping decision is needed first; put to GUIDANCE in the report.
- **P-STATE-1's record carries no year window** ("Historical" / "End-Century"
  only), so its time judgment is always `not_evaluable`; windows were taken from
  the record, not imported.
- Only the bounded conclusion is drawn: *"No fully compatible pair was found
  under the current deterministic rules in this fixed provisional pilot set."*
- Documents: [M5_WP1_COMPATIBILITY.md](M5_WP1_COMPATIBILITY.md),
  [../reports/milestones/M5_WP1_REPORT.md](../reports/milestones/M5_WP1_REPORT.md).

## Where things stand --- M4-WP1 (2026-09-29; closure 2026-10-08)

- **GUIDANCE: PASS WITH ACTIONS (D-017)**, on `7ded08e`. The 27 claims are
  **single-reader provisional** --- usable to test compatibility machinery,
  not accepted literature evidence. Excerpts stay, as **minimal evidence
  windows** with hash + offsets authoritative. The scope rule and both
  borderline calls are accepted. **A blind second reader over all ten papers
  is required** before any claim is accepted M5 evidence (planned as
  **M4-WP1b**). A relevance-guided M4-WP2 needs the ruling's five conditions,
  and its retrieval rule returns to GUIDANCE after M5-WP1.
- **Closure, done:** laboratory treatment levels moved from `scenario` to a new
  `experimental_condition` dimension; **`scenario` is `unknown` in 27 of 27
  claims**. Every claim carries `claim_validation_status:
  single_reader_provisional`. All 96 span locators and hashes are unchanged.

- **Ten corpus items were sampled by rule, frozen, and then read in full.** The
  sample reads only ids and duplicate groups from the frozen manifest; it was
  committed (`6f9006c`, 05:17:40Z) before the first file was opened (05:18:25Z).
  **Ten items, deterministically sampled, for workflow validation; not
  representative of the corpus.**
- **The JSON has no shared schema.** Every file is a flat object of strings
  whose keys are section headings; all ten key sequences differ. `title` is
  missing once and holds a non-title twice (a journal name; a page header).
- **Outcome:** 6 `in_scope_hazard` → `claims_extracted` (27 claims), 3
  `off_topic`, 1 `ambiguous_only`. 3 claims carry an `inferred` dimension, each
  with its support span. 22 rejected or ambiguous passages are kept. No claim
  states an emissions scenario (at `7ded08e` the two `LIT-000191` treatment
  levels sat under `scenario`; D-017 moved them).
- **Every one of 96 evidence spans re-slices exactly** from the decoded source:
  zero-based, half-open `[start, end)` code-point offsets on the unnormalized
  string, computed by exact search, never typed. A combining macron in a place
  name stopped the build once --- the check working.
- **The reading is the EXECUTOR's, once**, and the EXECUTOR is a language model
  that had built the prototypes. The code reads no prototype, family or query
  (tested); the reader's prior exposure is disclosed, not claimed away. For
  GUIDANCE: whether a second, independent reader is needed before M5, and
  whether tracked verbatim excerpts (96 short quotations) are acceptable ---
  both answered in D-017.
- Documents: [LITERATURE_WP1_PILOT.md](LITERATURE_WP1_PILOT.md),
  [../reports/milestones/M4_WP1_REPORT.md](../reports/milestones/M4_WP1_REPORT.md).

## Where things stand --- M4-WP0 (2026-09-28)

- **The literature corpus has arrived and is pinned, unopened.** JL supplied a
  folder (`00`) of **1,918 `.json` files, 78,798,270 bytes**, and the Boolean
  query it was collected with. The folder stays external, at
  `literature_corpus_root` in the untracked config. Every file was read as raw
  bytes for SHA-256 and size and **for nothing else** --- one `rb`-only reader,
  with runtime and AST tests that nothing decodes or parses. **0 zero-byte files;
  1 exact-duplicate pair** (`LIT-001483`, `LIT-001484`), identified, not removed.
  Ids `LIT-000001`… are frozen; a re-run verifies and fails on any change.
- **The corpus identity for later packages** is the SHA-256 of
  `artifacts/literature/corpus_manifest.json`,
  **`3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a`**,
  recorded in `data/manifest.json` under `external_corpora` with a
  timestamp-free content identity beside it.
- **The query is pinned**: `data/metadata/literature_query.txt`, SHA-256
  **`5a7ddf53…e1e5`**, 2,292 bytes, byte for byte as received. Platform,
  execution date, export date and completeness are **`unknown`** --- Q19–Q21,
  for JL, not the mentor.
- **The query has eleven hazard groups, not ten** as the work package said ---
  reported as found. 80 hazard terms, 22 context terms. **It carries no
  scenario, horizon, US state, postal code, county, tract or USA term** (three
  absence rules, 0 hits) --- verified only against those lists, and a finding
  about the query, not about any paper.
- **Query-scope coverage, not corpus coverage.** Each prototype's concept terms:
  **1 exact, 0 normalized, 3 absent** (`fire weather`, `fire weather`,
  `heat index`). All four family names absent. **9 of 11 query hazard groups
  have no pilot counterpart.** `inferred_conceptual_relationship` is defined and
  cannot be emitted.
- **Kaiyuan opened one file before the inventory**; it appeared off-topic (urban
  surface water, Wuhan). An observation from one file, not a corpus property ---
  M4-WP1's sample should expect off-topic items.
- **`!artifacts/literature/` was added to `.gitignore`**, because the corpus
  rule `literature/` caught the path the work package names. The corpus rule is
  unchanged.

## Where things stand --- M1 (carried forward; unchanged by M4-WP0 except as marked)

- **The M1 problem changed shape and the project followed it.** R-001 (2026-09-10)
  established that **no further documentation exists** --- no newer dictionary,
  no assembly document, no release note --- and R-002 gave a direction rather
  than any per-column answer. D-010, now decided, is the response: interpret a
  small subset, name the inference as inference, and let the data owner confirm
  it on worked examples.
- **A fifth status exists and twenty columns hold it.** `inferred_candidate` is
  **strictly below** `owner_confirmed` and `verified_from_dictionary` and is
  settable **only** by a column-specific record in the new tracked
  `data/metadata/inferred_candidates.yaml`. The dictionary rules never emit it,
  the EXECUTOR candidate maps cannot produce it, and `validate_resolution`
  refuses it by name --- **a resolution record can never assign it**, and it can
  never overwrite a stronger status. A record with no dictionary spans, or with
  no reasoning, is refused.
- **Status counts are now 21 / 0 / 20 / 130 / 28 / 76** --- verified,
  owner-confirmed, inferred, partially resolved, unresolved, structurally
  observed only. `status_diff.py` attributes all 20 changes to an IC-record and
  D-011, with 0 invariant violations. **Nothing reached `owner_confirmed`; the
  count there is still zero and stays there until the mentor answers.**
- **The pilot subset is 41 of 275 columns** in four families --- heat index (Q14),
  summer fire weather (Q13), a location anchor (Q10), and three `tempmaxann`
  columns that make the Q1 stem assumption concrete. It contains **every**
  `verified_from_dictionary` column in the file and then the minimum needed to
  make those readable. **The other 234 columns are untouched**, at their WP1
  baseline. See `docs/PILOT_SUBSET.md` for the rationale and the exclusions.
- **Three example records are built and ready for the mentor**, from rows 0, 13
  and 147, picked by rules that look only at whether cells are populated ---
  never at how large a value is. Each keeps raw bytes, recorded semantics and
  generated prose in three layers; the prose is produced **by template** from the
  semantics, and every clause resting on an inference is wrapped
  `[provisional: ...]`, with the build failing if one is not.
- **The answer sheet was not reviewed** at the one-on-ones of 2026-09-17 or
  2026-09-24 (R-003, *new*). It remains outstanding. **`docs/MENTOR_EXAMPLES.md`
  is what goes to the mentor, and to nothing else.** Sixteen numbered
  lines --- fifteen answerable confirm / correct / don't know in ten minutes, and
  line 13 a stated observation with nothing to confirm --- behind a printable
  answer sheet. `MENTOR_BRIEF.md` leads with it and demotes the Q1--Q18 table
  beneath.
- **The pre-meeting review (D-012) found one real defect and it is fixed.** Some
  **inferred location semantics were stated as fact outside the confirmation
  surface**: headings read `Stephens County, Oklahoma` and framing read
  `Where it is:`, while `NAME`, `State` and `State_Abbr` are themselves
  `inferred_candidate`. The generated prose was correct throughout --- the
  **hand-authored framing around it was not**. Titles are now neutral, the
  location line quotes the stored strings under a label that claims nothing, and
  the location checklist item is **split three ways** so one tick cannot confirm
  a character count and a semantic claim together. A bounded guard,
  `test_no_unwrapped_location_semantic_in_the_hand_authored_framing`, now checks
  the hand-authored surface and a second test feeds the rejected heading back
  through it. **The standing rule this establishes: a labelling discipline
  enforced only where output is generated is not enforced.**
- **M1-WP3b built three prototype phenomenon units, and the ruling admitted them
  as validation objects and nothing more.** Every record carries
  `validation_only` and opens with **"Prototype for scientific-object
  validation. Not an accepted phenomenon record."** Schema version
  `p0-prototype`, not `v1`. One grid cell (`R106C361`), one
  county-shaped row set (`Oklahoma` / `Stephens`, 10 rows), one state-shaped row
  set (`California`, 2,831 rows of which 2,827 carry a value). Every derived
  field takes the **weakest** status of its inputs, with the consequence that
  **no field in any of the three reaches `derived_from_verified`**. Every
  operation, assumption and provisional rule is named in the record that uses
  it. Nothing is merged, nothing is pushed, nothing is milestone evidence.
- **Phase A measured two things that decide what "county-level" can mean.**
  `Crossmodel` is **unique** --- 62,834 distinct over 62,834 rows. And **`GEOID`
  does not determine `(State, NAME)`**: 3,234 of 12,941 values appear against
  more than one pair. The consequence is procedural and is now a repository
  rule: **no row set in this project may be keyed on `GEOID`**, and none is. A
  county here is the set of rows sharing a `(State, NAME)` label (A-G3,
  computed), and nothing else.
- **A column's dictionary type decides what arithmetic it admits.** The ruling
  found that `P-COUNTY-1` was reporting an **unweighted mean of
  `wildfire_summer_Pend`**, a column the dictionary itself labels "Percent
  Change". The mean is gone; the ten per-cell values are kept; the corroboration
  is now a count --- *positive on 10 of 10 member cells*. The fix is general:
  `aggregate_column` **refuses** any column typed `Percent Change` or `Text ID`
  and any location column, with tests in both directions. **The standing rule:
  whether the characters parse as a number is not the question.**
- **The magnitude field is a placeholder and says so everywhere it appears.**
  `provisional_rule PR-1` ranks a unit's change value against every unit at the
  same level and reports a tercile. It is not a threshold, rests on no
  literature, and is wrapped in its own distinct mark --- `[provisional rule
  PR-1: ...]` --- so a reader can tell a provisional *value* from a placeholder
  *rule*. It ranks on the **signed** change value, not on absolute magnitude ---
  a unit in the lower third may be one with a large **decrease** --- and every
  `M` field now says so and carries the exact reference-population definition.
  **Wherever a percentile is reported, the population's composition is stated
  with it** --- "of 50 `State`-label groups: 49 named labels plus one
  empty-label group (7 rows with a value)", "of 3,019 `(State, NAME)` label
  groups: 3,018 named labels plus one empty-label group", "of 62,834
  `Crossmodel`-key groups: all named, no empty-label group". **"Group", not
  "county" or "state"**: at those levels a unit is a set of rows sharing a
  label, and calling it a county would assert the reading A-G1 is still asking
  the mentor to confirm.
- **Every unweighted mean carries the ruling's own label for it.**
  **"Provisional aggregation rule for representation validation"** --- the
  ruling's words, quoted, not paraphrased --- travels beside the number in the
  record, in the generated sentence, in both generated documents and in the
  handout, with a test that a cell-level record, which averages nothing, does
  **not** carry it. The mean is acceptable for these three prototypes on that
  condition and is **not** the project's aggregation method.
- **The assumptions register says what breaks.** Every one of the **thirteen**
  assumptions carries a **rationale** and a **failure mode** --- what goes
  wrong downstream if it is false --- as columns separate from the statement.
  The sharpest: if cells are not equal in area, every aggregate is biased by an
  unknown amount in an unknown direction, **and none of the numbers would look
  wrong**. Ten are flagged as worth putting to the mentor on 2026-09-17.
- **A-M2 is the newest, and it is a choice nobody has made.** PR-1's reference
  population **includes empty-label groups**: the 7 rows with no `State` form
  one group of the 50 ranked at state level and one of the 3,019 at county
  level. Counting them asserts nothing; excluding them would assert that those
  rows are not a place, and what they are is Q16, open. At state level one group
  is 2% of the population --- enough to move a tercile boundary.
- **Two conventions for the schema letters exist and neither is settled.** The
  mentor and Kaiyuan use S = season, T = horizon, C = scenario; the WP3b ruling
  uses S = scenario, T = temporal horizon, C = compared quantity. **The code
  emits the mentor's**, because they are what she has already seen. `P`, the
  per-field provenance map, is now an explicit field and both conventions agree
  on it. D-013 records the pair for the next GUIDANCE packet. **No number
  depends on the choice.**
- **The literature probe is a design stub and nothing was retrieved.** It
  already yields one finding: **at cell level there is no usable place term.**
  A grid-cell id is not a phrase any paper contains.
- **One M1-WP3 sentence stopped being true and was not carried across.** The
  location caution there ends "no part of this pilot groups rows by any of
  them". WP3b groups rows by `State` and `NAME` deliberately, so its records
  carry their own caution saying so, and a test refuses the old sentence in a
  WP3b record. **The M1-WP3 records are unchanged and their caution remains
  true of them.**
- **"Each row = one event" is still an assumption.** It is line 1 of every
  checklist and A1 of every record. Nothing treats it as settled.
- **Four GUIDANCE rulings from D-009 remain in force**, none of them reopened:
  the strict `verified_from_dictionary` bar; candidate maps for navigation only;
  index 117 kept with `-9` unlabelled; D-008 stated, not verified.
- **`pypdfium2==5.13.0` is in the D-007 pin set.** **Sophia must re-run
  `pip install -r requirements.txt`** before its next pinned checkout.
- **D-005/D-006/D-007 hold.** Every run verified the manifest SHA-256 before
  reading, fail-closed. `CLIMRR_ALLOW_MISSING_RAW=1` was never set. WP3 added
  one more guard: `build_examples.py` refuses to run if the coverage report it
  reads was built from different CSV bytes than the ones it just verified.

## Outstanding

- **For COORDINATOR:** the M4-WP4 reading package (reader 1, then a blind
  reader in a fresh session); how to treat `LIT2-001075` (= `LIT-001536`, read in
  M4-WP2); the Stage 2a--2c package; `.gitattributes` housekeeping (D-025).
- **For JL:** Q22 (the 705k → 186,346 filter).
- **For the mentor (Thursday 2026-10-22):** the FWI-rule confirmation; which
  dictionary concepts to prioritize for new units if coverage is comparable.
- **For GUIDANCE:** review **M4-WP2** (two readings + adjudication) and
  **M5-WP2** (0 eligible of 78); whether G-1 may accept a state within a list;
  whether the G-2 list may be extended.
- **For Kaiyuan:** what the WP2 blind session was given and opened (criterion 6).
- **For the mentor (2026-10-09):** the three questions in
  `MENTOR_REPORT_2026-10-09.md`.
- **For GUIDANCE / mentor:** metric-level terms for `fwi_seasonal_value` and
  `heatindex_days_above_105F` are still `proposed`; the D-019 mentor question
  (family-level bridge with disclosed mismatch vs exact metric/scenario).
- **Cleanup (D-019):** P-CELL-1/P-COUNTY-1 baseline-window citation chain.
- **For GUIDANCE, still open from WP3b:** the S/T/C letter convention (D-013, D-013-A1), and --- at the
  M1 gate --- whether criterion 1 may pass on declared provisional statuses
  (D-014).
- **For JL, the collection scientist:** Q19 (platform / database, fields
  searched), Q20 (execution and export dates), Q21 (is the folder the complete
  result set).
- **For the mentor, through the examples --- still unanswered:** is one row one
  "event"; does the stem `tempmaxann` denote "Temperature Maximum - Annual"
  (**101 columns** turn on it); which Census vintage are `GEOID` and `TRACTCE`;
  and is this the shape of record to connect to literature.
- **Pending choice: exclude empty-label groups from PR-1 populations (A-M2).**
  It was to be decided after a mentor answer on Q16; **no answer came**. PR-1
  still counts them and every record says so.
- **For Kaiyuan:** the Sophia `pip install -r requirements.txt` reinstall (`pypdfium2` pin).
- **Q7, Q8, Q9, Q11, Q12, Q15, Q17, Q18** still block downstream use of the
  columns they name. **Export date** of the ClimRR file remains unknown (Q18).

## Next

**Track A --- M4-WP4:** the 20-paper reading on the frozen sample (reading
package to be issued; reader 1 → blind reader → freeze → comparison →
adjudication → tiers → compatibility). **Track B:** GUIDANCE review of survey
run 1 and answers to Q-a/Q-b/Q-c before any run 2; diagnostics only. Mentor one-on-one Thursday
2026-10-22. GUIDANCE review of M4-WP2 / M5-WP2 still pending.

Still not authorised by any ruling: **QA generation**; semantic bridges beyond
what D-019 authorizes; widening the WP2 sample (a WP2b must be predeclared); embeddings; corpus-wide search; hazard labels
for papers outside the sample; any interpretation of a ClimRR column outside the
41 in the pilot subset. **D-014 changes none of that.**

## Knowledge files

The files staged for the COORDINATOR and GUIDANCE chats --- the same list as
`KNOWLEDGE_FILES` in `scripts/stage_knowledge.py` (the COORDINATOR maintains it;
`tests/test_stage_knowledge.py` checks that every file linked here is on it):
[BLUEPRINT.md](BLUEPRINT.md) · [CLAUDE.md](../CLAUDE.md) · [PROJECT_STATE.md](PROJECT_STATE.md) · [DECISION_LOG.md](DECISION_LOG.md) · [MENTOR_BRIEF.md](MENTOR_BRIEF.md) · [METADATA_QUESTIONS.md](METADATA_QUESTIONS.md) · [PILOT_SUBSET.md](PILOT_SUBSET.md) · [MENTOR_EXAMPLES.md](MENTOR_EXAMPLES.md) · [PHENOMENON_PROTOTYPES.md](PHENOMENON_PROTOTYPES.md) · [PHENOMENON_ASSUMPTIONS.md](PHENOMENON_ASSUMPTIONS.md) · [GROUP_MEETING_2026-09-14.md](GROUP_MEETING_2026-09-14.md) · [hierarchy_checks.md](../artifacts/profiles/hierarchy_checks.md) · [LITERATURE_QUERY_SCOPE.md](LITERATURE_QUERY_SCOPE.md) · [LITERATURE_CORPUS_INVENTORY.md](LITERATURE_CORPUS_INVENTORY.md) · [M1_WP3B_GUIDANCE_RULING.md](M1_WP3B_GUIDANCE_RULING.md) · [M4_WP0_GUIDANCE_RULING.md](M4_WP0_GUIDANCE_RULING.md) · [M4_WP0_REVIEW_MERGE_WP1_GUIDANCE_RULING.md](M4_WP0_REVIEW_MERGE_WP1_GUIDANCE_RULING.md) · [LITERATURE_WP1_PILOT.md](LITERATURE_WP1_PILOT.md) · [M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md](M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md) · [M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md](M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md) · [BRIDGE_ELIGIBILITY.md](BRIDGE_ELIGIBILITY.md) · [LITERATURE_WP2_CANDIDATES.md](LITERATURE_WP2_CANDIDATES.md) · [LITERATURE_WP1B_ADJUDICATION.md](LITERATURE_WP1B_ADJUDICATION.md) · [M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md](M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md) · [MENTOR_REPORT_2026-10-09.md](MENTOR_REPORT_2026-10-09.md) · [M5_WP2_COMPATIBILITY.md](M5_WP2_COMPATIBILITY.md) · [M4_WP3_CONCEPT_FIRST_GUIDANCE_RULING.md](M4_WP3_CONCEPT_FIRST_GUIDANCE_RULING.md) · [M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md](M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md) · [LITCORPUS01_SHARD_PILOT.md](LITCORPUS01_SHARD_PILOT.md) · [LITCORPUS02_PROVENANCE.md](LITCORPUS02_PROVENANCE.md) · [M4_WP3_REPORT.md](../reports/milestones/M4_WP3_REPORT.md) · [M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md](M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md) · [CONCEPT_COVERAGE_SURVEY.md](CONCEPT_COVERAGE_SURVEY.md) · [M4_WP4_TRACKB_GUIDANCE_RULING.md](M4_WP4_TRACKB_GUIDANCE_RULING.md) · [LITERATURE_WP4_ADJUDICATION.md](LITERATURE_WP4_ADJUDICATION.md) · [M5_WP4_COMPATIBILITY.md](M5_WP4_COMPATIBILITY.md) · [LITERATURE_WP4_READING.md](LITERATURE_WP4_READING.md) · [DICTIONARY_CONCEPTS.md](DICTIONARY_CONCEPTS.md)

## Links

- Charter: [BLUEPRINT.md](BLUEPRINT.md)
- Plan and gate criteria: [PROJECT_PLAN.md](PROJECT_PLAN.md)
- Decisions, including D-010 to D-013-A1 and **D-014, D-015, D-016, D-017**: [DECISION_LOG.md](DECISION_LOG.md)
- The ruling that authorised WP3: [M1_D010_GUIDANCE_RULING.md](M1_D010_GUIDANCE_RULING.md)
- The pre-meeting review of WP3 (**REVISE**, framing only): [M1_WP3_PREMEETING_GUIDANCE_REVIEW.md](M1_WP3_PREMEETING_GUIDANCE_REVIEW.md)
- The pilot subset, its rationale and its exclusions: [PILOT_SUBSET.md](PILOT_SUBSET.md)
- **What goes to the mentor one-on-one, 2026-09-17:** [MENTOR_EXAMPLES.md](MENTOR_EXAMPLES.md)
- **What goes to the group, 2026-09-14:** [GROUP_MEETING_2026-09-14.md](GROUP_MEETING_2026-09-14.md)
- **The ruling on M1-WP3b (PASS WITH ACTIONS):** [M1_WP3B_GUIDANCE_RULING.md](M1_WP3B_GUIDANCE_RULING.md)
- **M1-WP3b, prototype and unmerged:** [PHENOMENON_PROTOTYPES.md](PHENOMENON_PROTOTYPES.md),
  [PHENOMENON_ASSUMPTIONS.md](PHENOMENON_ASSUMPTIONS.md),
  [GROUP_MEETING_2026-09-14.md](GROUP_MEETING_2026-09-14.md),
  [../reports/milestones/M1_WP3b_PROTOTYPE_REPORT.md](../reports/milestones/M1_WP3b_PROTOTYPE_REPORT.md)
- Structural facts the prototypes rest on: [../artifacts/profiles/hierarchy_checks.md](../artifacts/profiles/hierarchy_checks.md)
- Data facts, dictionary-verified semantics, open questions: [DATA_NOTES.md](DATA_NOTES.md)
- Mentor-facing question inventory: [METADATA_QUESTIONS.md](METADATA_QUESTIONS.md)
- Per-column reasoning for every inferred candidate: [../data/metadata/inferred_candidates.yaml](../data/metadata/inferred_candidates.yaml)
- Sophia procedure, including M1-WP1 reproduction: [SOPHIA_RUNBOOK.md](SOPHIA_RUNBOOK.md)
- M0 report (accepted): [../reports/milestones/M0_SETUP_REPORT.md](../reports/milestones/M0_SETUP_REPORT.md)
- M1-WP1 report, frozen at the WP1 stage: [../reports/milestones/M1_DATA_GROUNDING_REPORT.md](../reports/milestones/M1_DATA_GROUNDING_REPORT.md)
- M1-WP2 report: [../reports/milestones/M1_WP2_REPORT.md](../reports/milestones/M1_WP2_REPORT.md)
- **M1-WP3 report, current M1 status:** [../reports/milestones/M1_WP3_REPORT.md](../reports/milestones/M1_WP3_REPORT.md)
- M1-WP1 GUIDANCE review: [M1_WP1_GUIDANCE_REVIEW.md](M1_WP1_GUIDANCE_REVIEW.md)
- Mentor meeting document: [MENTOR_BRIEF.md](MENTOR_BRIEF.md)
- **M4-WP0 ruling (PASS WITH ACTIONS):** [M4_WP0_GUIDANCE_RULING.md](M4_WP0_GUIDANCE_RULING.md)
- **M4-WP0 review, merge authorization and M4-WP1 ruling (WP0 PASS):** [M4_WP0_REVIEW_MERGE_WP1_GUIDANCE_RULING.md](M4_WP0_REVIEW_MERGE_WP1_GUIDANCE_RULING.md)
- **M4-WP0 report:** [../reports/milestones/M4_WP0_REPORT.md](../reports/milestones/M4_WP0_REPORT.md)
- **M4-WP1 review and M5-WP1 ruling (PASS WITH ACTIONS):** [M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md](M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md)
- **M5-WP2 report:** [../reports/milestones/M5_WP2_REPORT.md](../reports/milestones/M5_WP2_REPORT.md); **matrix:** [M5_WP2_COMPATIBILITY.md](M5_WP2_COMPATIBILITY.md); **adjudication:** [LITERATURE_WP2_ADJUDICATION.md](LITERATURE_WP2_ADJUDICATION.md); **mentor report:** [MENTOR_REPORT_2026-10-09.md](MENTOR_REPORT_2026-10-09.md)
- **M4-WP2 report:** [../reports/milestones/M4_WP2_REPORT.md](../reports/milestones/M4_WP2_REPORT.md); **reader-1 reading:** [LITERATURE_WP2_READING.md](LITERATURE_WP2_READING.md); **ruling:** [M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md](M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md)
- **M4-WP1b report:** [../reports/milestones/M4_WP1B_REPORT.md](../reports/milestones/M4_WP1B_REPORT.md); **adjudication:** [LITERATURE_WP1B_ADJUDICATION.md](LITERATURE_WP1B_ADJUDICATION.md)
- **M4-WP2 retrieval report:** [../reports/milestones/M4_WP2_RETRIEVAL_REPORT.md](../reports/milestones/M4_WP2_RETRIEVAL_REPORT.md); **candidates:** [LITERATURE_WP2_CANDIDATES.md](LITERATURE_WP2_CANDIDATES.md); **eligibility:** [BRIDGE_ELIGIBILITY.md](BRIDGE_ELIGIBILITY.md); **ruling:** [M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md](M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md)
- **M5-WP1 report:** [../reports/milestones/M5_WP1_REPORT.md](../reports/milestones/M5_WP1_REPORT.md); **matrix:** [M5_WP1_COMPATIBILITY.md](M5_WP1_COMPATIBILITY.md)
- **M4-WP1 report:** [../reports/milestones/M4_WP1_REPORT.md](../reports/milestones/M4_WP1_REPORT.md); **pilot claims:** [LITERATURE_WP1_PILOT.md](LITERATURE_WP1_PILOT.md)
- **Query scope:** [LITERATURE_QUERY_SCOPE.md](LITERATURE_QUERY_SCOPE.md); **corpus inventory:** [LITERATURE_CORPUS_INVENTORY.md](LITERATURE_CORPUS_INVENTORY.md)
- The pinned query and the corpus identity: [../data/MANIFEST.md](../data/MANIFEST.md)
- **M4-WP3 ruling (PASS WITH ACTIONS, D-025):** [M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md](M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md); **WP4 sample:** [../artifacts/literature/wp4_sample.json](../artifacts/literature/wp4_sample.json)
- **M4-WP3 report:** [../reports/milestones/M4_WP3_REPORT.md](../reports/milestones/M4_WP3_REPORT.md); **rulings:** [M4_WP3_CONCEPT_FIRST_GUIDANCE_RULING.md](M4_WP3_CONCEPT_FIRST_GUIDANCE_RULING.md), [M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md](M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md); **corpora:** [LITCORPUS01_SHARD_PILOT.md](LITCORPUS01_SHARD_PILOT.md), [LITCORPUS02_PROVENANCE.md](LITCORPUS02_PROVENANCE.md)
- Operating rules: [../CLAUDE.md](../CLAUDE.md)
