# M4-WP3 --- concept-first corpus provenance, FWI disambiguation, source-yield review

Authorized by [`docs/M4_WP3_CONCEPT_FIRST_GUIDANCE_RULING.md`](../../docs/M4_WP3_CONCEPT_FIRST_GUIDANCE_RULING.md)
(D-021) and [`docs/M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md`](../../docs/M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md)
(D-022). **No paper was read, opened for content, or sampled. No QA. No
vocabulary change. No concept-map change.** Retrieval and place hits are
lexical locations, not claims and not bridges.

## 1. Milestone ID and title

**M4-WP3 --- concept-first corpus provenance, FWI disambiguation and
source-yield review.** M4 (literature). **M1 remains open** (D-014).

## 2. Objective

Freeze the shard pilot as `LITCORPUS-01-conceptfirst-v1` and the 705k arm as
`LITCORPUS-02-conceptfirst-705k-v1` with M4-WP0-style provenance; implement
retrieval rule R-FWI-1 v1; run the geography-filter preflight and freeze its
candidates unread; log the mentor direction, both rulings, the source receipt
and the freeze (D-020--D-024); return the packet to GUIDANCE before any
reading.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/m4-wp3`, from `main` at **`ccd2d24`** (Phase 0: clean tree apart from the untracked ruling; `git branch --no-merged main` empty) |
| Package commit | this commit; its SHA travels with the hand-back |
| Remote | **not pushed, not merged** |

Decision numbers: D-A → **D-020**, D-B → **D-021**, D-C → **D-022**, D-D →
**D-023**, D-E → **D-024** (the log's last entry was D-019).

## 4. Data version and checksums

| Object | SHA-256 |
| --- | --- |
| `litcorpus02_evidence.tar.gz` (collection evidence, read) | `a38c816455564a026235a2db23cf1b2c497de95662ae099c61039e5817da2fbb` |
| `litindex_scripts.tar.gz` (source of `build_index.py`, `run_v1_on_705k.sh`) | `eecb6b902d15285f7e6107bd25a7abfc096b3399f1e34de11275391099967554` |
| `scripts/litcollect/build_index.py` (byte-identical to the tarball's) | `5e063a44f30bee0da81205b6b119d647d87fd08ddf38998eb1d8fa0c235b99a9` |
| `scripts/litcollect/run_query.py` (the standalone file, byte-identical) | `a93eeba766f2eb4d487a8a157d2a2d207b41af0482fefdb774886a66c2d57708` |
| `run_v1_on_705k.sh` **as executed** | `0c9516b78a0f8ac6a55e62975c0f58e567e0689c5ab1e4bfb2076ff04fbcaf2c` |
| `scripts/litcollect/run_v1_on_705k.sh` **as tracked** (one line placeholdered, field 11) | `47fe1e17f3dc27fa8267ec21a173bbb3c773d4bc5f2e2045a7d5ccd379ffba59` |
| D-023 source zip | `516baf87049eda6b117f230e23ec52a016301ce482fc4edcd3581a6897baaa94` |
| 705k index content identity / manifest CSV | `fbb4affb…7a94` / `a94885b9…d212` |
| `litcorpus01_manifest.csv` | `c686425710a5c5ad23abdd904d0ca38982933b978c04463594b3ea6469faeda8` |
| `fire_weather_v1_manifest.csv` / `extreme_heat_v1_manifest.csv` | `e0943c66…edc4` / `5de3e7ae…da2d` |
| `lit2_ids.csv` | `415aae90c9888291d46f4afc99c6f630aa5789a1190711b77aa718363cccbb82` |
| `data/metadata/concept_map.yaml` (**unchanged**, pinned by test) | `6ec6b081658e82b5fba4171bcd3135f69ce71710a7a515f32cac83404ebd3664` |
| LITCORPUS-00 manifest (**unchanged**) | `3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a` |

All corpus manifests and summaries are pinned in `data/manifest.json`
(`external_corpora`). `FullData.csv` was not read.

## 5. Environment and execution location

- **Collection (not by this repo's EXECUTOR):** LITCORPUS-01 --- araiadoc on a
  Polaris login node, 2026-10-12, DuckDB `threads=1, 16GB`. LITCORPUS-02 ---
  `run_v1_on_705k.sh` on `polaris-login-01`, 2026-10-19, Python 3.13.14, DuckDB
  1.5.4, `threads=4, 4GB`; places run 22:11:46Z.
- **Freeze (this repo):** local macOS, conda env `climrr`, Python 3.11.16, every
  D-007 pin matched (run record `reports/runs/*_local_freeze_litcorpus.json`).
  **`duckdb==1.5.4` was installed into that env**, pinned in
  `scripts/litcollect/requirements.txt` (not the D-007 set).

## 6. Work completed

- **Phase A.** Both rulings tracked and added to `KNOWLEDGE_FILES`; D-020--D-024
  appended; `MENTOR_BRIEF.md` --- 2026-10-09 and 2026-10-13 entries (the latter
  records only JL's email as outcome), status line 7, two next questions; Q22
  added; `litcollect_root_polaris` added to the example config (placeholder)
  and to the untracked local config; `stage_knowledge.py` writes no run record
  (test; exemption noted in `CLAUDE.md`).
- **Phase B.** LITCORPUS-01 record (`docs/LITCORPUS01_SHARD_PILOT.md`,
  `artifacts/literature/litcorpus01/`). R-FWI-1 retroactive count **not
  computed** (field 11); Polaris helper and runbook ready.
- **Phase C.** LITCORPUS-02 record (`docs/LITCORPUS02_PROVENANCE.md`,
  `artifacts/literature/litcorpus02/`): source, index, matcher, yields, R-FWI-1
  evidence, duplicates, legacy overlap, `LIT2` ids, manifests.
- **Phase D.** Place candidates frozen with first-hit locations, unread.
- **Phase E.** `src/climrr/retrieval.py` (R-FWI-1 v1); `docs/BRIDGE_ELIGIBILITY.md`
  §5; the three collection tools under `scripts/litcollect/`; synthetic-index
  test.
- **Phase F.** This report; `docs/PROJECT_STATE.md`.

## 7. Deliverables and exact file paths

| Path | What |
| --- | --- |
| `docs/M4_WP3_CONCEPT_FIRST_GUIDANCE_RULING.md`, `docs/M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md` | the rulings, as placed |
| `docs/LITCORPUS01_SHARD_PILOT.md`, `artifacts/literature/litcorpus01/` | LITCORPUS-01 record |
| `docs/LITCORPUS02_PROVENANCE.md`, `artifacts/literature/litcorpus02/` | LITCORPUS-02 record, incl. `place_candidates/` |
| `src/climrr/retrieval.py`, `tests/test_retrieval.py` | R-FWI-1 v1 |
| `src/climrr/litcorpus.py`, `scripts/freeze_litcorpus.py`, `tests/test_litcorpus.py` | the freeze and its checks |
| `scripts/litcollect/{build_index.py,run_query.py,run_v1_on_705k.sh,requirements.txt}`, `tests/test_litcollect_tools.py` | the collection tools |
| `scripts/litcollect/apply_rfwi1_litcorpus01.py` | Polaris helper for the deferred LITCORPUS-01 count |
| `docs/DECISION_LOG.md`, `docs/MENTOR_BRIEF.md`, `docs/METADATA_QUESTIONS.md`, `docs/BRIDGE_ELIGIBILITY.md`, `docs/PROJECT_STATE.md`, `CLAUDE.md`, `config/local_paths.example.yaml`, `data/manifest.json`, `scripts/stage_knowledge.py`, `tests/test_stage_knowledge.py` | bookkeeping |

## 8. Methods and rules that affect scientific meaning

- **R-FWI-1 v1 (D-022).** Bare `fwi` admits only with a same-document approved
  disambiguator; longer terms admit directly; both locations recorded. Repo
  implementation uses `climrr.conceptmap.find_term`. The 705k run passed the
  two-term argument `fire weather|fire-weather`, **equivalent** to the six-term
  rule for this query (`LITCORPUS02_PROVENANCE.md` §4).
- **Topical vs context clause.** The topical group decides concept membership;
  the AND-ed context clause constrains precision only and is part of the
  corpus definition (D-022).
- **Ids.** Item id = source basename; `LIT2-NNNNNN` in code-point order over the
  admitted union. Duplicates identified, not removed.
- **Geography preflight** used only `oklahoma`, `stephens`, `california`, over
  the whole source, intersected with the admitted arms afterwards.

## 9. Results with compact tables or examples

**Every number below was read from the evidence files; all equal the work
package except the directory count** (field 11).

| | LITCORPUS-01 (shard) | LITCORPUS-02 (705k) |
| --- | --- | --- |
| fire_weather_v1 | **4** | raw **495** → admitted **448** (R-FWI-1 excludes 47) |
| extreme_heat_v1 | **10** | **861 / 861** |
| fire diag (topical only) | 13 | 548 raw → 473 |
| heat diag (topical only) | 11 | 1,082 |
| context clause removes | 9 / 1 | 53 / 221 |
| cross-arm overlap | 0 | **1** --- `270275181` (`LIT2-001017`) |
| unique items | 14 | **1,308** (`LIT2-000001`…`LIT2-001308`) |
| exact-byte redundant copies in arms | 0 | **10** (5 + 5; none across arms) |
| place candidates | --- | fire **100** (CA 96, Stephens 10, OK 3); heat **143** (CA 136, OK 13, Stephens 3) |

LITCORPUS-00 ⊂ 705k source: **1,918 / 1,918**; in the arms 4 (fire:
`LIT-000166`, `LIT-000519`, `LIT-000792`, `LIT-001815`) and 10 (heat:
`LIT-000289`, `000372`, `000897`, `001427`, `001468`, `001487`, `001517`,
`001536`, `001547`, `001914`), all byte-identical to the LITCORPUS-00 files.

**Acceptance criteria (source-yield ruling, 1--25):**

| # | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| 1 | LITCORPUS-01 stable corpus identity | met | `artifacts/literature/litcorpus01/litcorpus01_manifest.json`; `data/manifest.json` |
| 2 | Both production query hashes pinned | met | `litcorpus01/evidence/query_hashes_v1.txt`; `tests/test_litcorpus.py` |
| 3 | Diagnostic query hashes pinned, labelled diagnostic-only | met | same; roles in `litcorpus01_manifest.json` |
| 4 | Unused broader queries preserved, marked non-executed | met | `litcorpus01/queries/*_btsd_unused_query.txt`; roles |
| 5 | Shard identity, bytes, record count | met (count **reported by the tool team**) | `docs/LITCORPUS01_SHARD_PILOT.md` §1; `evidence/shard_listing.txt` |
| 6 | araiadoc commit and execution configuration | met | `evidence/araiadoc_commit.txt`, `evidence/*_extract.log` |
| 7 | Production yield per family | met | `LITCORPUS01_SHARD_PILOT.md` §4; `LITCORPUS02_PROVENANCE.md` §5 |
| 8 | Diagnostic yield separately | met | same |
| 9 | Diagnostics have no corpus identity | met | `litcorpus01_diagnostics.csv` (no id); `QUERY_ROLE` in `src/climrr/litcorpus.py` |
| 10 | FWI collision evidence preserved | met | `litcorpus01/evidence/fwi_collision_snippets.txt` (verbatim) |
| 11 | R-FWI-1 versioned and deterministic | met | `src/climrr/retrieval.py`; `docs/BRIDGE_ELIGIBILITY.md` §5 |
| 12 | Bare `FWI` alone cannot admit | met | `tests/test_retrieval.py`; 47 exclusions in `rfwi1_fire_weather_v1.csv` |
| 13 | Longer terms directly eligible | met | `tests/test_retrieval.py` (Canadian FWI, Fire Weather Index) |
| 14 | Same-document disambiguator hits stored with locations | **met for LITCORPUS-02; pending for LITCORPUS-01** | `litcorpus02/rfwi1_fire_weather_v1.csv`; `scripts/litcollect/apply_rfwi1_litcorpus01.py` |
| 15 | No change to the concept-map identity of `FWI` | met | hash test in `tests/test_retrieval.py` |
| 16 | Outputs external except manifests / provenance / small evidence | met | corpus files on Eagle; `litcorpus0{1,2}/` hold ids, hashes, locations |
| 17 | Every v1 document has a stable id / hash | met | `litcorpus01_manifest.csv` (14); `lit2_ids.csv` (1,308) |
| 18 | Cross-arm duplicates identifiable | met | `overlaps.json` (overlap, duplicate groups) |
| 19 | Year / venue / author `unknown` | met | `metadata` block in both manifests and `data/manifest.json` |
| 20 | Source-domain skew documented | met | `LITCORPUS01_SHARD_PILOT.md` §1; `LITCORPUS02_PROVENANCE.md` §1 (filter unknown, Q22) |
| 21 | Request for better coverage recorded | met (disciplinary emphasis **not recorded**) | `docs/MENTOR_BRIEF.md` 2026-10-13; `LITCORPUS02_PROVENANCE.md` §10 |
| 22 | New source reuses the frozen production queries | met | byte-identity test; `queries_byte_identical_to_litcorpus01: true` |
| 23 | Geography filtering only after corpus freeze | met in substance (field 11) | places run 22:11:46Z after the arm runs (≤ 22:04:30Z); arms not altered by it |
| 24 | Geography candidates frozen before reading | met | `litcorpus02/place_candidates/` (hashes in `place_candidates.json`) |
| 25 | No semantic claim extraction or QA | met | no claim artifact created; no paper opened |

## 10. Validation performed

- `python -m pytest -q` (conda env `climrr`): **817 passed, 0 failed, 0
  skipped**; `python scripts/verify_no_secrets_or_paths.py`: **0 hits** (480
  tracked text files).
- At freeze, fail-closed: every copied evidence file listed in a hash list
  matched it; id lists match extract-log counts and raw-record hash lists;
  `query_sha256` in every 705k summary equals the shard-run hash; every run
  names the same index identity; `hits.csv` covers exactly the admitted ids
  with consistent `rel_path`/`sha256`; each of the 495 R-FWI-1 decisions is
  backed by recorded hit locations; each place-candidate list equals the sorted
  intersection.
- The freeze is deterministic: a second run reproduced every artifact
  byte-for-byte.
- Synthetic 5-document index through the real tools (`tests/test_litcollect_tools.py`):
  parser refuses `NOT` and nesting; parse failure and non-string recorded, not
  repaired; `FWIs` not matched; bare-`FWI` document excluded; offsets re-slice
  on the unnormalized string past an accented prefix; repo R-FWI-1 agrees with
  the tool on all four parseable documents.

## 11. Failures, rejected cases, known limitations, and deviations

1. **LITCORPUS-01 R-FWI-1 count not computed.** The four raw records are on
   Eagle only, and the ids are not in the 705k source. Not substituted with the
   tool team's "3 of 13 contain `fire weather`". Helper + runbook ready
   (`LITCORPUS01_SHARD_PILOT.md` §6).
2. **Sectionization of LITCORPUS-01 deferred** (disclosed in the work package):
   GUIDANCE asked to confirm LITCORPUS-02 supersedes it first.
3. **Per-section (705k) vs concatenated-document (shard) matching**; also
   different DuckDB settings. Three matchers with two disclosed edge-case
   differences (`BRIDGE_ELIGIBILITY.md` §5); their effect on the 705k arms is
   unmeasured.
4. **Shard composition and record count are reported by the tool team**, not
   computed.
5. **No `bytes` column** in the arm manifests: not in the evidence bundle.
6. **Directory count mismatch with the work package:** the source has **100**
   directories (`00`--`62`, `64`--`99`, `unknown`), not 101; there is no `63`.
   The file count (186,346) and `unknown` (2,126) match.
7. **`run_v1_on_705k.sh` is not byte-identical to the executed file:** its one
   absolute-path line (`BASE=`) now reads `LITCOLLECT_ROOT_POLARIS` from the
   environment, as `CLAUDE.md` requires; both hashes in field 4.
8. **Seven evidence files redacted** (absolute Eagle paths →
   placeholders); original and redacted hashes in each `redactions.json`.
9. **The 705k run's R-FWI-1 argument was two terms**, not six; equivalent for
   this query (field 8).
10. **The 47 R-FWI-1-excluded documents have no recorded hit locations**
    (`run_query.py` writes hits for admitted documents only).
11. **The places run's command line is not in the evidence**; it is not in
    `run_v1_on_705k.sh`.
12. **Ordering (criterion 23):** the place query ran over the whole source after
    the arm runs had written their ids, but before D-024 formally froze them in
    this commit. The arms are unchanged by it (checked by hash).
13. **Five topical query terms are not concept-map surface terms**
    (`fire-weather index`, `canadian forest fire weather index`, `canadian
    fwi`, `heat-index`, `extended heat index`); four are on no dictionary line
    (`LITCORPUS01_SHARD_PILOT.md` §3). Nothing changed; put to GUIDANCE.
14. **duckdb added to the local `climrr` env** and pinned outside D-007; tests
    needing it skip where it is absent (e.g. Sophia).
15. **`.gitattributes` precedence defect (pre-existing, found here):** the later
    `* text=auto eol=lf` line overrides `*.csv -text`, so Git would have
    rewritten the CRLF evidence CSVs and broken their pinned hashes on a fresh
    clone. Fixed **for `artifacts/literature/litcorpus0{1,2}/` only** (explicit
    `-text`, tested); the global rule is unchanged and the older tracked CSVs
    are not touched --- reported for the COORDINATOR.
16. Three LITCORPUS-02 items (`LIT-000166`, `LIT-000519`, `LIT-001536`) were read
    in M4-WP2; their earlier readings are not carried over.

## 12. Deviations from the approved plan

Items 1, 2, 5, 7, 8, 14 and 15 of field 11. Nothing else was added to or removed
from the work package; no scope, vocabulary or concept-map decision was taken.

## 13. Open decisions, mentor questions, and the requested comparison

**Same concept, same query, different source** (ruling, "next scientific
comparison"):

| Family | LITCORPUS-01 shard | LITCORPUS-02 705k |
| --- | --- | --- |
| fire weather (production) | 4 | **448** admitted (495 raw) |
| heat index (production) | 10 | **861** |
| fire weather (diagnostic) | 13 | 548 raw / 473 after R-FWI-1 |
| heat index (diagnostic) | 11 | 1,082 |

The sources differ in size and composition (54,081 records reported vs 186,346
files, filter unknown) and in matcher granularity; the ratio is not a property
of the literature, and no representativeness is inferred.

**For GUIDANCE:**

1. Does LITCORPUS-02 supersede LITCORPUS-01 as the working corpus (so LITCORPUS-01
   sectionization is not spent)?
2. Was the 705k arm in scope for WP3 under the ruling's "same frozen
   query/provenance protocol" condition, given per-section matching --- or
   should it be relabelled M4-WP3b?
3. Is D-022's acceptance of the production queries the governance record for the
   five topical variants absent from `concept_map.yaml`?
4. Is the two-term R-FWI-1 argument accepted as equivalent to the six-term rule?
5. Duplicates kept with their own `LIT2` ids --- acceptable, or drop later
   members before any sample (as WP2 did)?

**For the mentor** (`MENTOR_BRIEF.md`): (i) confirmation of the FWI rule; (ii)
Kaiyuan's proposal of a dictionary-grounded concept survey (pending GUIDANCE).
**For JL:** Q22. **For Kaiyuan:** run the LITCORPUS-01 R-FWI-1 helper on Polaris.

## 14. Proposed gate status

**Ready for GUIDANCE review.** Proposed: **PASS WITH ACTIONS** --- actions: the
LITCORPUS-01 R-FWI-1 Polaris run; decisions 1--5 above. Not proposed for merge
by the EXECUTOR.

## 15. Proposed next bounded objective

GUIDANCE review of this packet. Then, if approved, a **two-reader reading plan on
a predeclared sample of the place candidates** (100 fire, 143 heat), sample rule
and size frozen before any file is opened. Separately, and pending GUIDANCE:
Kaiyuan's proposal for a **dictionary-grounded concept survey** across the whole
data dictionary. QA remains unauthorized.
