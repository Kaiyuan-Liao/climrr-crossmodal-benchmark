# M4-WP0 --- Literature Corpus Provenance and Inventory

**A provenance and inventory preflight. No paper was opened, parsed, retrieved
or interpreted.** Authorised by the GUIDANCE ruling
[`docs/M4_WP0_GUIDANCE_RULING.md`](../../docs/M4_WP0_GUIDANCE_RULING.md) (PASS
WITH ACTIONS), recorded as **D-015**. QA generation is still not authorised.

This report also carries the M1 bookkeeping since 2026-09-13 (Phase A), which
changed no column status.

## 1. Milestone ID and title

**M4-WP0 --- Literature Corpus Provenance and Inventory.** The first work package
of **M4, Literature Ingestion and Structured Claim Pilot**, and deliberately not
M4 claim work: it prepares the external evidence source without opening it.
Named M4-WP0 rather than M1-WP5, as the ruling directs.

**M1 is still open.** Its criterion 1 will be evaluated on provisional statuses,
explicitly declared (D-014).

## 2. Objective

Establish, before any paper is read, **what the literature corpus is and how it
was collected**: pin the collection query and its provenance; parse the query
deterministically; compare the pilot's vocabulary with the query as
**query-scope coverage**; and give every corpus file a stable id and hash by
byte-level reads only.

**Explicitly excluded, and not done:** opening, reading, decoding or parsing
any corpus file; extracting titles, abstracts or metadata; OCR; searching the
corpus for any term; assigning any paper to a hazard group; relevance scoring;
embeddings; table-to-paper pairs; claim extraction; M5 bridge scoring; QA.

## 3. Repository commit SHA

| | |
| --- | --- |
| Branch | `work/m4-wp0`, created from `work/m1-wp3b` at head `e359b26` |
| Phases A–E | `52a994a0bb8c30f5b7af4c8bf99a685938941d73` --- code, artifacts, bookkeeping |
| Evidence runs | re-run at `52a994a`, clean tree; all four M4-WP0 outputs reproduced byte for byte |
| This report, `PROJECT_STATE.md`, brief status | this report's own commit; a commit cannot contain its own hash, so its SHA travels with the hand-back |
| Remote | **Not pushed, not merged**, as the work package requires. `origin` has no `work/m4-wp0` |
| `main` | unchanged at `62c9137` |

**The unmerged branch chain**, for the merge request to GUIDANCE --- each branch
contains the one before it, linearly:

| Branch | Head | On `origin` |
| --- | --- | --- |
| `work/m1-wp2` | `391b442` | yes, same head |
| `work/m1-wp3` | `ad13649` | yes, same head |
| `work/m1-wp3b` | `e359b26` | yes, same head (pushed by Kaiyuan) |
| `work/m4-wp0` | this package | no |

## 4. Data version and checksums

| File | SHA-256 | Bytes | Storage |
| --- | --- | ---: | --- |
| `data/metadata/literature_query.txt` | `5a7ddf537d343b73fa0887e5f11ffbe3965fd25811f2adfc25cacee66f0ee1e5` | 2,292 | tracked, immutable, `-text` (**new**) |
| `artifacts/literature/corpus_manifest.json` --- **the corpus identity** | `3281aa724f9fd8e01975b8031861d7b2f30179f3d1ef1f9e3bf369006dd5f04a` | 890,471 | tracked |
| `artifacts/literature/corpus_manifest.csv` | `de795d7cd2ad0294dc4b8d0457a1707b7b37946b9c141b4ffe8a0d4f2e44a638` | 365,356 | tracked |
| Corpus content identity (recomputable from the folder) | `e217076f0f155a12f0954313059fba14904826658676e504e8cbb4c042e71f5e` | --- | --- |
| External corpus `LITCORPUS-00`, folder `00` | per file in the manifest | 78,798,270 | **external; never tracked** |
| `data/raw/FullData.csv` | `e87ac2cd…3bf43e`, verified on every coverage run | 296,407,423 | untracked (D-005), unchanged |
| `data/metadata/resolutions.yaml` | `f944dc76cf423757896e3ac6600f2f3cd37db03ba891445bd177c2c2efaca2e0` | --- | tracked; R-003 appended |

The query was copied from the file as supplied and compared with `cmp`:
identical. It is pure ASCII with LF line endings and no byte-order mark.

## 5. Environment and execution location

| | |
| --- | --- |
| Kind | conda environment `climrr` |
| Python | 3.11.16 |
| Platform | macOS-15.3-arm64 |
| `pip freeze` SHA-256 | `8d8e9add5995fdca95d820217755355d8a02c71af376c4de02d2ecba249af4c4` |
| D-007 pins | all six `matches_pin: true` in every evidence run record |
| Location label | `local` |
| Sophia | **not used.** The corpus is not on Sophia; see the runbook note, §8b |

The base interpreter on this host is **not** the project environment --- it
carries pandas 2.1.4 and fails `test_repo_requirements_pins_are_all_satisfied`.
Every run here used the `climrr` environment.

## 6. Work completed

**Phase A --- M1 bookkeeping, recording only.** The 2026-09-14 group meeting is
logged with the ruling's sentence verbatim. The one-on-ones of 2026-09-17 and
2026-09-24 are logged as **no review occurred**, against every one of the 19
answer-sheet lines. **R-003** records that outcome with `effect: null`. The
coverage and status-diff artifacts were regenerated: **no column moved** (20
changed since WP1, all by IC-records, as before). **D-014** and **D-015**
appended.

**Phase B --- the query pinned.** Copied byte for byte; manifest entry with a
provenance block: supplied by `JL` to Kaiyuan, received 2026-09-28, stated
collector the same person, platform / execution date / export date / complete
result set all `unknown`. Reported facts, verified facts and unverified claims
are three separate lists. Q19–Q21 added for the collection scientist, in
`METADATA_QUESTIONS.md` and in the brief under a new "Literature corpus" table.

**Phase C --- deterministic parse.** `src/climrr/litquery.py`, a closed grammar
that refuses anything outside it with a character offset;
`scripts/parse_literature_query.py` writes `artifacts/literature/query_parsed.json`
pinned to the query's SHA-256. Three absence rules applied.

**Phase D --- query-scope coverage.** `src/climrr/queryscope.py`,
`scripts/query_scope_coverage.py` → `artifacts/literature/query_scope_coverage.json`
and the generated `docs/LITERATURE_QUERY_SCOPE.md`.

**Phase E --- external inventory.** `src/climrr/corpus.py`,
`scripts/inventory_corpus.py` → the frozen manifest (`.json`, `.csv`), the
generated `docs/LITERATURE_CORPUS_INVENTORY.md`, and the `external_corpora`
block of `data/manifest.json`. Runbook note added; nothing transferred.

**To repeat it:** with `literature_corpus_root` set in `config/local_paths.yaml`,
run `scripts/parse_literature_query.py`, `scripts/query_scope_coverage.py`,
`scripts/inventory_corpus.py`. The first two regenerate identical bytes; the
third verifies the frozen manifest and fails on any difference.

## 7. Deliverables and exact file paths

**New:** `data/metadata/literature_query.txt`; `src/climrr/litquery.py`,
`src/climrr/queryscope.py`, `src/climrr/corpus.py`;
`scripts/parse_literature_query.py`, `scripts/query_scope_coverage.py`,
`scripts/inventory_corpus.py`; `artifacts/literature/query_parsed.json`,
`artifacts/literature/query_scope_coverage.json`,
`artifacts/literature/corpus_manifest.json`,
`artifacts/literature/corpus_manifest.csv`;
`docs/LITERATURE_QUERY_SCOPE.md`, `docs/LITERATURE_CORPUS_INVENTORY.md`;
`docs/M4_WP0_GUIDANCE_RULING.md` (tracked as placed, unedited);
`tests/test_litquery.py`, `tests/test_queryscope.py`, `tests/test_corpus.py`;
this report; run records under `reports/runs/20260928T*`.

**Changed:** `data/manifest.json`, `data/MANIFEST.md`,
`data/metadata/resolutions.yaml`, `artifacts/profiles/dictionary_coverage.json`,
`artifacts/profiles/status_diff.md`, `docs/DECISION_LOG.md`,
`docs/MENTOR_BRIEF.md`, `docs/METADATA_QUESTIONS.md`,
`docs/SOPHIA_RUNBOOK.md`, `docs/PROJECT_STATE.md`,
`config/local_paths.example.yaml`, `.gitattributes`, `.gitignore`.

## 8. Methods and rules that affect scientific meaning

**No rule was applied to any ClimRR column**, and nothing about any paper was
determined. The rules below govern what the new artifacts say.

1. **Parse grammar.** Parentheses; `AND`/`OR` in upper case only; quoted
   phrases; bare terms of letters, digits, `-`, `_`, `.`. Mixing `AND` and `OR`
   at one level without parentheses is refused, as is `NOT`, any wildcard, and
   any other character --- with the offset. **No precedence rule was invented.**
2. **Group ids are positional only** (`HG-01`…`HG-11`); no group is named.
   Documents refer to a group by id and first term, which is a quotation.
3. **Normalization:** curly quotes → straight, lower case, whitespace runs → one
   space, trimmed. Hyphens kept. Nothing else, not even the en dash.
4. **Round trip:** the re-rendered parse equals the source after removing
   whitespace **outside** quoted phrases. Whitespace inside a phrase must match
   exactly, so `"heat wave"` and `heatwave` stay different.
5. **Coverage classification** is **whole-string** comparison: exact, else
   normalized-equal, else absent. No substring, word, synonym or stem matching.
   `inferred_conceptual_relationship` is defined and cannot be emitted.
6. **A hazard group "has a pilot counterpart"** when one of its terms is the
   matched term of an exact or normalized row. Nothing more.
7. **Absence rules** --- the rule text is stored with each result:
   `AR-1` regex `rcp|ssp|\d{4}|century|mid-|end-|projection|scenario|baseline|historical`
   anywhere in a term; `AR-2` the 50 state names and DC as whole words, and
   their 51 USPS codes as whole alphanumeric words; `AR-3` `county`, `tract`,
   `united states`, `usa` as whole words.
8. **Inventory:** raw-byte reads only, through one guarded function; symlinks
   not followed; archives hashed, not expanded; ids by code-point order of the
   POSIX relative path, frozen; duplicates grouped by SHA-256, never removed.

## 9. Results with compact tables or examples

**The query.** `AND( OR(HG-01..HG-11), OR(CT-01..CT-22) )` --- **11 hazard
groups, 80 terms; 22 context terms; 102 terms** (64 quoted, 38 bare). Round trip:
passes.

| Group | First term | Terms | | Group | First term | Terms |
| --- | --- | ---: | --- | --- | --- | ---: |
| HG-01 | extreme heat | 13 | | HG-07 | convective storm | 10 |
| HG-02 | extreme cold | 10 | | HG-08 | sea level rise | 8 |
| HG-03 | flood | 12 | | HG-09 | sea ice loss | 5 |
| HG-04 | drought | 6 | | HG-10 | carbon dioxide fertilization | 2 |
| HG-05 | wildfire | 7 | | HG-11 | crop failure | 3 |
| HG-06 | tropical cyclone | 4 | | | | |

**Absence rules** --- each checked against all 102 terms:

| Rule | Hits | Result |
| --- | ---: | --- |
| `AR-1-scenario-horizon` | 0 | **absent** |
| `AR-2-us-state` | 0 | **absent** |
| `AR-3-geographic-unit` | 0 | **absent** |

**"No place name" is verified only against the lists in `AR-2` and `AR-3`.** A
city, a non-US country or a region on neither list would not be caught.

**Query-scope coverage:**

| | exact | normalized | absent | exact match |
| --- | ---: | ---: | ---: | --- |
| `P-CELL-1` concept terms | 1 | 0 | 3 | `fire weather` = `HG-05.T04` |
| `P-COUNTY-1` concept terms | 1 | 0 | 3 | `fire weather` = `HG-05.T04` |
| `P-STATE-1` concept terms | 1 | 0 | 3 | `heat index` = `HG-01.T11` |
| Pilot family names (4) | 0 | 0 | 4 | --- |

`fire weather index`, `FWI`, `fire danger`, `days above 105 F`,
`extreme heat days` and `humid heat` are not query terms. **9 of 11 hazard
groups have no pilot counterpart** --- HG-02, HG-03, HG-04, HG-06 to HG-11. No
context term equals any pilot string.

**The corpus inventory:**

| | |
| --- | ---: |
| Files | 1,918, all `accessibility: ok` |
| Extensions | `.json` 1,918 |
| Nested folders, symlinks, other entries | 0 --- flat folder |
| Total bytes | 78,798,270 |
| Smallest / median / largest | 5,873 / 37,207.5 / 329,585 |
| Zero-byte files | 0 |
| Distinct SHA-256 | 1,917 |
| Exact-byte duplicate groups | **1** --- `DUP-0001`: `LIT-001483`, `LIT-001484`, 10,507 bytes each |

## 10. Validation performed

| Check | Result |
| --- | --- |
| `pytest` (`climrr` env) | **531 passed** (476 before; 55 new) |
| `scripts/verify_no_secrets_or_paths.py` | **0 hits**, 215 tracked text files |
| Query copy vs source | `cmp` identical; SHA-256 equal |
| Parse reproducibility | two runs and a clean-head run: `query_parsed.json` byte-identical |
| Coverage reproducibility | clean-head run byte-identical |
| Inventory reproducibility | verify-mode re-run at a dirty and at a clean head: manifest, CSV, doc and `data/manifest.json` byte-identical |
| R-003 effect | status diff: 20 columns changed since WP1, the same 20 as before, all by IC-records |

**The tests that matter most:** every term offset points at its text;
out-of-grammar input is refused at the right offset; each absence rule fires on
a term it names and not on `co2` or `inundation`; `classify` has no code path to
the fourth category (checked on its AST); inventory ids are stable across runs
and a changed path set or changed bytes fail loudly; a symlink's target is never
opened; **a full inventory of a fixture folder of valid JSON opens every file
only as `rb`, never decodes, and never calls `json.load`/`loads`** (runtime spy);
the module imports no JSON, CSV, PDF or archive library, calls no `decode`,
`read_text` or `load`, and has exactly one `open` (AST check); the corpus path
appears in no tracked artifact.

## 11. Failures, rejected cases, and known limitations

- **The scanner flagged a credential-bearing word** (28 hits; the common word for a lexical unit) in the first draft of the
  parser. The scanner was not touched; the parser vocabulary was renamed to
  *lexeme*.
- **A stale hash was corrected in passing.** `artifacts/profiles/status_diff.md`
  had carried an `inferred_candidates.yaml` SHA-256 (`7a1e0414…`) that no longer
  matched the file; regenerating it for R-003 wrote the current value
  (`62cd7a2d…`). No status in it changed.
- **The `dictionary_coverage` and `status_diff` run records read
  `git_dirty: true` at the clean head**, because `dictionary_coverage.py`
  rewrites its own tracked output before recording. Pre-existing behaviour; the
  coverage artifact itself records `git_dirty: false`.
- **Whole-string classification is strict by design.** `Heat Index – Summer` is
  absent although `heat index` is a query term. A looser rule would be a new
  rule, and the fourth category is where that belongs --- later.
- **The absence rules are only as good as their lists** --- see field 9.
- **The query was not verified to be the one executed.** Only its bytes are
  verified; Q19--Q21.
- **One file was looked at by Kaiyuan before the inventory** and appeared
  off-topic (urban surface water, Wuhan). Recorded as an observation from one
  file, not a corpus property. Consequence: M4-WP1's sample should expect
  off-topic items. The inventory opened no file to check.
- **The filenames are numeric** (e.g. `100961700.json`); they were recorded as
  manifest fields and read for nothing else.

## 12. Deviations from the approved plan

1. **Eleven hazard groups, not ten.** The work package says the first
   disjunction holds ten; the deterministic parse finds eleven (its own list of
   unmatched groups plus heat and wildfire also comes to eleven). Reported as
   found; nothing merged.
2. **Three absence rules, with the geography rule split in two:** `AR-2` (US
   states and postal codes) and `AR-3` (county, tract, United States, USA). The
   work package lists the two geography lists in one sentence.
3. **`.gitignore` exception.** The existing `literature/` rule caught
   `artifacts/literature/`, the path the work package names. A narrow
   `!artifacts/literature/` was added; the corpus rule is unchanged (D-015).
4. **A content identity alongside the manifest's SHA-256.** The manifest's own
   hash is recorded as the corpus identity, as asked. Because the manifest
   carries an inventory timestamp, a timestamp-free content identity is also
   recorded, so the folder can be re-identified without the frozen file.
5. **Re-runs verify rather than rewrite**, so the manifest's SHA-256 stays
   stable. Re-freezing a changed corpus means deleting the manifest in a
   commit that says why.
6. **R-003 is dated 2026-09-24.** The schema takes one date; the record names
   both meetings in `source_detail` and says why the later date was used.
7. **R-003 names no question id**, because none was answered.
8. **Coverage inputs:** the prototype concept terms and the family names, as
   asked. The prototypes' place, horizon and scenario terms were not
   classified; the absence rules cover those dimensions from the query side.

## 13. Open decisions and mentor questions

**Group feedback (ruling action 12).** 2026-09-14, recorded as:

> **No material objection to the prototype-unit design was raised.**

**This is not validation.** Feedback was light; the group is not the data owner;
it confirms no column semantic and promotes nothing.

**Mentor-review outcome (ruling action 11).** 2026-09-17 and 2026-09-24: **no
review occurred** (R-003). All 19 answer-sheet lines are recorded as such in the
brief; no status promotion. The sheet remains outstanding.

**Open:**

| Item | Owner | Blocks |
| --- | --- | --- |
| Q19 --- platform / database and fields searched | JL | reproducing or citing the collection |
| Q20 --- execution and export dates | JL | citing the corpus as a snapshot |
| Q21 --- is the folder the complete result set | JL | how far an M4-WP1 sample generalises |
| Q1–Q18 and every answer-sheet line | mentor | promotion of any `inferred_candidate` column |
| Whether M1 criterion 1 may pass on declared provisional statuses (D-014) | GUIDANCE | the M1 gate |
| Merge of the chain `work/m1-wp2` → `wp3` → `wp3b` → `m4-wp0` | GUIDANCE, then Kaiyuan | `main` |
| The S/T/C letter convention (D-013, D-013-A1) | GUIDANCE | --- still open from WP3b |

## 14. Proposed gate status

The ruling's 18 acceptance criteria, one line each:

| # | Criterion (abridged from the ruling) | Status | Evidence |
| ---: | --- | --- | --- |
| 1 | Exact original query stored unchanged and hash-pinned | **MET** | `cmp` identical; `data/manifest.json`; `-text` |
| 2 | Provenance distinguishes known facts from `unknown` | **MET** | provenance block: reported / verified / not verified; four `unknown`s |
| 3 | Parsed representation reproducible from the exact query | **MET** | byte-identical re-runs; `test_the_tracked_parse_is_current` |
| 4 | Hazard groups and context terms deterministically represented | **MET** | 11 groups, 22 context terms, offsets tested |
| 5 | Query-scope table separates prototype concepts, outside-pilot groups, absent dimensions | **MET** | `LITERATURE_QUERY_SCOPE.md` §§1–2, 3, 4 |
| 6 | No query-level observation described as evidence about papers | **MET** | ruling sentence verbatim (tested); "What this document does not say" |
| 7 | Every corpus file receives a stable manifest entry | **MET** | 1,918 of 1,918 |
| 8 | Each entry has relative path, format, bytes, SHA-256 | **MET** | tested on every entry |
| 9 | Exact-byte duplicate groups identifiable | **MET** | `DUP-0001`; nothing removed |
| 10 | No corpus document copied into Git | **MET** | only manifests staged; path-leak test |
| 11 | No text, page, abstract, metadata or claim semantically inspected | **MET** | one `rb`-only reader; runtime spy and AST tests |
| 12 | Raw-file reads limited to provenance/inventory | **MET** | same |
| 13 | Manifest reproducible against the configured root | **MET** | verify-mode re-runs, byte-identical |
| 14 | No paper gets a hazard group from the query alone | **MET** | no such field exists in the manifest |
| 15 | Absence of geo/scenario/horizon constraints recorded if the parser confirms it | **MET** | AR-1..AR-3 absent, with the list caveat |
| 16 | Stable ids and hashes suitable for an M4-WP1 sample | **MET** | frozen `LIT-NNNNNN`, change detection |
| 17 | Mentor-review outcome recorded without inventing confirmation | **MET** | R-003; 19 lines "no review occurred" |
| 18 | No claim extraction, prototype matching, bridging or QA | **MET** | none performed or claimed |

**Proposed status: M4-WP0 ready for GUIDANCE review, all 18 criteria met.** The
EXECUTOR proposes; GUIDANCE decides.

## 15. Proposed next bounded objective

**M4-WP1 --- deterministic 6–12-paper ingestion and structured-claim pilot,
sample drawn from the frozen manifest by rule, independent of prototype
relevance.**
