# LITCORPUS-02 --- provenance of the concept-first 705k arm

**Status: working concept-first candidate corpus (D-025)** --- for candidate
generation, not a representative sample of the literature. Q22 stays open.

**`LITCORPUS-02-conceptfirst-705k-v1`** --- frozen 2026-10-19 (D-024): the union
of the two admitted production arms, produced by the **frozen v1 queries** and
**R-FWI-1 v1** over the D-023 source. **1,308 items.** **No paper was read,
opened for content, or sampled.** Retrieval and place hits are lexical
locations, not claims and not bridges. QA is not generated.

Records: `artifacts/literature/litcorpus02/` --- `litcorpus02_manifest.json`
(every number below, machine-readable), the two arm manifests, `lit2_ids.csv`,
`rfwi1_fire_weather_v1.csv`, `overlaps.json`, `place_candidates/`, the evidence
as received (`evidence/`) and `redactions.json`. Built by
`scripts/freeze_litcorpus.py`; checked by `tests/test_litcorpus.py`. Every
number here was read from the evidence files by code, not typed from the work
package.

## 1. Source identity (D-023)

| Field | Value |
| --- | --- |
| File | `full_705k_v2_filtered.zip`, supplied by **JL** via Google Drive link after the 2026-10-13 mentor meeting |
| JL's description | *"the google drive link that I shared with you have 200K version of filtered climate dataset with name full_705k_v2_filtered. This contains actually 186,346 json files."* |
| Zip bytes | **2,283,251,035** |
| Zip SHA-256 | **`516baf87049eda6b117f230e23ec52a016301ce482fc4edcd3581a6897baaa94`** (`evidence/full_705k_v2_filtered.zip.sha256`) |
| Files | **186,346** `.json` |
| Unpacked bytes | **7,651,208,072** |
| Directories | **100**: `00`--`62`, `64`--`99`, and one literally named `unknown` (2,126 files). **There is no directory `63`** (`evidence/705k_stage1.log`, `index_summary.json` `buckets: 100`). The source's own layout --- recorded, not interpreted |
| Location | Polaris/Eagle, under `config/local_paths.yaml:litcollect_root_polaris` (untracked). Immutable from receipt |
| 705k → 186,346 filter | **unknown** --- **Q22**, for JL |
| 705k parent | JL's provenance; **reported, not verified** |
| Year / venue / authors | **`unknown`** for every item |

## 2. Index identity (`evidence/index_summary.json`)

Built by `scripts/litcollect/build_index.py` on `polaris-login-01`, DuckDB
1.5.4, Python 3.13.14; 100 buckets, 9,045 s (first run, 2026-10-19).

| Field | Value |
| --- | --- |
| Files indexed | **186,346** |
| Parse failures | **0** |
| String sections | **1,658,731** |
| Total bytes | **7,651,208,072** |
| Distinct SHA-256 | **184,268** → **2,078** redundant exact-byte copies in the source |
| `manifest_csv_sha256` | **`a94885b9f2ebb6c47adb2f1ca09a2b62941cfb200151aad7ca4199ced1e4d212`** --- the full-source manifest stays external |
| Content identity | **`fbb4affb71622e07259182ec4922d1496b47fa09ad08396d6e4ceaa8eeb77a94`** --- SHA-256 of `rel_path⇥sha256⇥bytes⏎` lines in `rel_path` order |

Every run's `summary.json` names this same content identity (checked at freeze).

## 3. Matcher

`scripts/litcollect/run_query.py`: **per-section** whole-word, case-insensitive,
no stemming --- `regexp_matches(text, '\b'+escape(term)+'\b', 'i')`; a document
matches iff every AND-group has a matching term in some section. One streaming
scan per query; `threads=4`, `memory_limit=4GB`.

**Differences, disclosed.**

- **Per-section, not concatenated-document** (LITCORPUS-01's araiadoc run): a
  phrase cannot straddle a section boundary here.
- **Execution settings differ** from LITCORPUS-01 (`threads=1, 16GB`); this does
  not change matching.
- **Three matchers are in play**: DuckDB `\b` (ASCII) decides membership;
  Python `re` `\b` (Unicode) computes the recorded offsets; the repo matcher
  (`climrr.conceptmap.find_term`) implements R-FWI-1 in this repository. They
  differ only on `_` and on a non-ASCII letter touching the term
  (`docs/BRIDGE_ELIGIBILITY.md` §5). Every admitted document has at least one
  recorded hit (checked), so no admitted id is offset-less.
- A first attempt with the superseded concatenating `run_query.py` (inside
  `litindex_scripts.tar.gz`) ran out of memory before writing anything
  (`evidence/705k_stage1.log`); every result here is from the tracked
  `run_query.py` (SHA-256 `a93eeba766f2eb4d487a8a157d2a2d207b41af0482fefdb774886a66c2d57708`).

**Queries are byte-identical to LITCORPUS-01's.** The `query_sha256` in each of
the four 705k `summary.json` files equals the hash in
`litcorpus01/evidence/query_hashes_v1.txt`, and the tracked query files are
byte-equal (test). **No place term is in either production query.**

## 4. R-FWI-1 v1 as executed

The fire-weather runs passed `--disambiguate 'fwi=fire weather|fire-weather'`:
a document whose **only** topical hit is bare `fwi` is admitted only if `fire
weather` or `fire-weather` occurs in some section of the same document. **This
is equivalent to the six-disambiguator rule of D-022 for this query**: under
whole-word matching `fire weather index` and `canadian forest fire weather
index` contain `fire weather`, `fire-weather index` contains `fire-weather`, and
a document containing `canadian fwi` hits that topical term and so is never
"bare-only".

**The repository implementation carries all six.** `src/climrr/retrieval.py`
defines `DISAMBIGUATORS = ("fire weather", "fire-weather", "fire weather
index", "fire-weather index", "canadian forest fire weather index", "canadian
fwi")`, in the ruling's order; `tests/test_retrieval.py::test_disambiguators_are_exactly_the_rulings_list`
parses the list out of `docs/M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md` and
requires equality. So the two-term argument is confined to the external 705k
run; every application inside this repository --- including the LITCORPUS-01
retroactive run --- uses the full six-term rule.

`rfwi1_fire_weather_v1.csv` holds, for each of the 495 raw documents, the run's
decision, its basis and the first **bare-term**, **disambiguator** and **direct
topical** hit (term, section key, section index, `[start, end)`):

| Basis | Documents |
| --- | --- |
| `direct_topical_term` | 444 |
| `bare_fwi_with_same_document_disambiguator` | 4 |
| `bare_fwi_without_disambiguator` --- **excluded** | **47** |

Every decision is backed by the recorded hit locations (checked at freeze and by
test). The 47 excluded documents have **no** recorded locations: `run_query.py`
writes hits only for admitted documents.

## 5. Yields (verified from the files; all equal the work package)

| Run | Role | Topical-group docs | Raw | Admitted | R-FWI-1 excluded |
| --- | --- | --- | --- | --- | --- |
| `fire_weather_v1` | **production** | 548 | **495** | **448** | **47** |
| `extreme_heat_v1` | **production** | 1,082 | **861** | **861** | 0 |
| `fire_weather_diag_topical_only` | diagnostic | 548 | 548 | 473 | 75 |
| `extreme_heat_diag_topical_only` | diagnostic | 1,082 | 1,082 | 1,082 | 0 |

- **The context clause removes 548 − 495 = 53** fire-weather and **1,082 − 861 =
  221** heat-index documents (raw counts). Diagnostic runs are **collection
  sensitivity diagnostics**, with no corpus identity.
- Every admitted production document is in its diagnostic set (448/448,
  861/861).
- **Per-term document counts** (`per_term_doc_counts`): fire topical ---
  `fire weather index` 462, `fire-weather index` 9, `fwi` 408, `canadian forest
  fire weather index` 104, `canadian fwi` 42; disambiguators --- `fire weather`
  1,298, `fire-weather` 128. Heat topical --- `heat index` 1,080, `heat-index`
  13, `extended heat index` 1. Context-clause counts are in the manifest.
- **Cross-arm overlap: 1** --- **`270275181`** (`LIT2-001017`,
  `81/270275181.json`). It is not a place candidate in either arm.
- **Union: 448 + 861 − 1 = 1,308.**

## 6. Duplicates

Exact-byte duplicate groups, by per-document SHA-256 from `hits.csv`:
**5 in each arm, 10 redundant copies in total**, no group spanning the arms.
Each pair is two different source ids with identical bytes. **Identified, not
removed**; every copy keeps its own item id and `LIT2` id.

| Arm | Pairs (item id / LIT2 id) |
| --- | --- |
| fire_weather_v1 | 198147267 / 88514560 (`LIT2-000147` / `001292`); 220375355 / 256834064 (`000270` / `000776`); 225979119 / 264715271 (`000339` / `000902`); 254745154 / 27543019 (`000746` / `001101`); 256835474 / 67860751 (`000777` / `001260`) |
| extreme_heat_v1 | 239052352 / 257056592 (`000516` / `000782`); 243481766 / 247886089 (`000541` / `000631`); 255550896 / 8665340 (`000755` / `001287`); 259841886 / 265127382 (`000846` / `000906`); 261620656 / 266081070 (`000877` / `000920`) |

## 7. LITCORPUS-00 inside the source

**All 1,918 LITCORPUS-00 ids are in the source** (`evidence/705k_stage1.log`;
the id list equals the LITCORPUS-00 manifest basenames). The arms contain 4 and
10 of them, each **byte-identical** to the LITCORPUS-00 file (SHA-256 equal) and
each at `00/<id>.json`:

| Arm | Item id → LIT2 id → LITCORPUS-00 id |
| --- | --- |
| fire_weather_v1 | 14300 → `LIT2-000070` → `LIT-000166`; 221115000 → `LIT2-000275` → `LIT-000519`; 235725400 → `LIT2-000445` → `LIT-000792`; 59268800 → `LIT2-001235` → `LIT-001815` |
| extreme_heat_v1 | 189111700 → `LIT2-000139` → `LIT-000289`; 210876700 → `LIT2-000197` → `LIT-000372`; 238809100 → `LIT2-000504` → `LIT-000897`; 266868200 → `LIT2-000928` → `LIT-001427`; 268963400 → `LIT2-000982` → `LIT-001468`; 269873800 → `LIT2-001003` → `LIT-001487`; 271213500 → `LIT2-001036` → `LIT-001517`; 272852900 → `LIT2-001075` → `LIT-001536`; 273701500 → `LIT2-001090` → `LIT-001547`; 9506300 → `LIT2-001303` → `LIT-001914` |

`LIT-000166`, `LIT-000519` and `LIT-001536` were M4-WP2 candidates and have been
read (two readers, adjudicated); their earlier readings are not carried into
LITCORPUS-02. Bucket `00` holds 1,918 files, the same count as LITCORPUS-00 ---
recorded, not interpreted.

## 8. Stable ids and manifests

- **Item id** = source basename (S2 corpus id); `rel_path` and `sha256` from
  `hits.csv` (consistent across every hit row of a document; checked).
- **`LIT2-NNNNNN`** assigned once in **code-point order of the item id** over
  the 1,308-item union: `LIT2-000001` … `LIT2-001308`. Frozen.
- Arm manifests: `item_id, lit2_id, arm, rel_path, sha256`. **No `bytes`
  column**: per-item byte counts are not in the evidence bundle and were not
  guessed.

| File | SHA-256 |
| --- | --- |
| `fire_weather_v1_manifest.csv` (448) | `e0943c668f9fb2442385edd87e93fdaf2c27d3f297191292e40f86488dffedc4` |
| `extreme_heat_v1_manifest.csv` (861) | `5de3e7aef402f0beed606f50ee61c210c84f4a2c838eea66e26535402a43da2d` |
| `lit2_ids.csv` (1,308) | `415aae90c9888291d46f4afc99c6f630aa5789a1190711b77aa718363cccbb82` |

Recorded in `data/manifest.json` under `external_corpora`
(`LITCORPUS-02-conceptfirst-705k-v1`), with the summary's hash.

## 9. Geography-filter preflight --- frozen, unread (`place_candidates/`)

Run **after** the concept corpus was defined, with the approved place
vocabulary only: query `( oklahoma OR stephens OR california )`, SHA-256
`cd0d596f538e838ee7ada805e655bdc781efa9a5919c5240909c18238c17ae75`, over the
whole source --- **16,457** documents (`oklahoma` 1,525, `stephens` 1,643,
`california` 14,054). Each candidate list is the sorted intersection of an
admitted arm with those 16,457 (checked).

| Arm | Candidates | `california` | `stephens` | `oklahoma` | List SHA-256 |
| --- | --- | --- | --- | --- | --- |
| fire_weather_v1 | **100** | 96 | 10 | 3 | `122ee177f45dd98ecb76765a7ce0e8c543261694c5e991380ab94139d756a149` |
| extreme_heat_v1 | **143** | 136 | 3 | 13 | `eb28845e43bbd63875a8ac7b25f64fef9aabb07abde69a7ae75e14bb689c623c` |

`first_hits.csv` records, per candidate and place term, the first hit's section
key, section index and `[start, end)`; `candidate_hits.csv` every recorded
(first-per-section) place hit.

> **Lexical hits; role of each place term (study area, affiliation, surname)
> unknown until reading; reading not authorized.**

The places run is not in `run_v1_on_705k.sh`; its exact command line is not in
the evidence. Its `summary.json` records the query hash, no disambiguation,
`threads=4`, `4GB`, and the same index identity.

## 10. Source request and comparison

- **Requested:** a larger source, at the 2026-10-13 mentor meeting (D-022
  authorized a larger and/or atmospheric / geoscience-oriented one). Whether a
  disciplinary emphasis was asked for is **not recorded**.
- **Recipient / supplier:** JL. **Supplied:** one source, described by JL as a
  "filtered climate dataset" (D-023). Its filter is unknown (Q22).
- **Same frozen queries, unchanged:** yes, byte-identical (§3). Diagnostics
  were also run.
- **Comparison --- same concept, same query, different source:**
  fire weather **4 → 448** admitted (495 raw); heat index **10 → 861**.
  Diagnostics 13 → 548 raw / 473 admitted, 11 → 1,082. The two sources differ in
  composition and size (54,081 records reported vs 186,346 files) and in
  matcher granularity (§3), so the ratio is not a property of the literature.

## 11. Redaction

Six evidence files carried absolute Eagle paths (`index_summary.json`, the four
production/diagnostic `summary.json`, `705k_stage1.log`); in the tracked copies
each reads `<LITCOLLECT_ROOT_POLARIS>`. Original and redacted SHA-256 are in
`redactions.json`; five of the six originals were verified against
`705k_stage1_hashes.txt` first (the log is not listed there). Every other
evidence file is byte-identical to the bundle and matches its listed hash.

## 12. Survey context clause v1 (diagnostic)

`data/metadata/litcollect/survey_context_clause_v1.txt`, SHA-256
**`fec9b5ca97f18e6e409a4b6e10b50faf5ab3c5404a33381eb8e67e9debc3626f`**, 403 bytes
(one line plus a trailing LF), pinned in `data/manifest.json` and `-text` in
`.gitattributes`. Authorized by D-025 for the Track B Stage 2c coverage survey.

It is the v1 production context group --- identical, term for term and in order,
in `fire_weather_v1` and `extreme_heat_v1` --- **minus the family-specific
terms** `fire season`, `fire danger` (fire arm) and `public health`, `heat
wave`, `heatwave` (heat arm): 28 terms, one OR-group in `run_query.py` grammar.
Checked by `tests/test_survey_driver.py` against the frozen query files.

**Diagnostic only.** It is not a production query, has no corpus identity, and
changes neither LITCORPUS-02 nor any arm. `survey_driver.py` evaluates it once
over the frozen source index (cached as `_context/`) and intersects it with each
concept's topical set; the resulting `context_filtered_count` is a coverage
diagnostic, not a prevalence estimate.
