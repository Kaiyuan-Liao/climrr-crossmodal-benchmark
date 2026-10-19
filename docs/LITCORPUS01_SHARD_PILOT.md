# LITCORPUS-01 --- the concept-first shard pilot

**`LITCORPUS-01-conceptfirst-v1`** --- frozen 2026-10-19 (D-022, D-024). A
**provenance/yield pilot, not the bridge corpus** (confirmed, D-025;
sectionization closed as not required). Retained, not discarded.
**No paper was read, opened for content, or sampled.** Retrieval hits are
lexical locations, not claims and not bridges.

Records: `artifacts/literature/litcorpus01/` --- `litcorpus01_manifest.json`
(this document's numbers, machine-readable), `litcorpus01_manifest.csv` (the 14
production items), `litcorpus01_diagnostics.csv`, the six query files, the
evidence files as received (`evidence/`), the id lists (`ids/`) and
`redactions.json`. Built by `scripts/freeze_litcorpus.py` from
`litcorpus02_evidence.tar.gz` (SHA-256
`a38c816455564a026235a2db23cf1b2c497de95662ae099c61039e5817da2fbb`);
checked by `tests/test_litcorpus.py`.

## 1. Source

| Field | Value | Provenance |
| --- | --- | --- |
| Source | S2ORC v1 shard, via ANL araiadoc | collection-tool team |
| Shard filename | `20250110_123425_00414_fcji5_ece7efc6-de1c-4b47-8d63-7d0a484800e3.gz` | `evidence/shard_listing.txt` |
| Shard bytes | **1,073,892,084** | `evidence/shard_listing.txt` (`ls -l` on Eagle; directory redacted) |
| Records | **54,081** | **reported by the collection-tool team; not computed by this project** |
| Composition | ~48% PubMed, ~18% arXiv | **reported by the collection-tool team; not computed by this project** |
| Year / venue / authors | **`unknown`** for every item | source limitation (D-021) |

**Source-domain skew.** As reported, the shard is biomedical-heavy. Nothing here
infers that fire-weather literature is rare, or that heat-index literature is
predominantly biomedical, from this shard (ruling, "Do not do yet").

## 2. Collection tool and execution

| Field | Value |
| --- | --- |
| Tool | ANL araiadoc, commit **`f9d3c6bbf1183bc16040a280a33b5ac9f5a20f23`** (`evidence/araiadoc_commit.txt`) |
| Matcher | DuckDB, whole-word, case-insensitive, no stemming --- as reported for araiadoc, over the **concatenated document** |
| DuckDB settings | `threads=1, memory_limit=16GB` (each `evidence/*_extract.log`) |
| Host | Polaris login node |
| Date | 2026-10-12 |
| Output | one raw JSON record per document, `raw/<run>/<bucket>/<id>.json`, on Eagle |
| Duplicate policy | none applied by the tool; "unique document(s)" per run (extract logs) |

## 3. Queries --- six files, hash-pinned

| Query file | SHA-256 | Role |
| --- | --- | --- |
| `fire_weather_v1_query.txt` | `73c13461940d6cff39bdf5740bab55e16308093df576f2f3ed573000b4732d35` | **production** (corpus-defining) |
| `extreme_heat_v1_query.txt` | `04cbcee537a4571952ab90bdd22933d6a998e5cd1b86c753bb997605156579c8` | **production** (corpus-defining) |
| `fire_weather_diag_topical_only_query.txt` | `88d148d6f5db9db03e9f42895759afc1f183a45b7311b6b39c2da76f5f87a07b` | collection sensitivity diagnostic --- no corpus identity |
| `extreme_heat_diag_topical_only_query.txt` | `849388b459b2523587cbb358fa40738cb283b84b9c5b9444f9dc21be7282a3ba` | collection sensitivity diagnostic --- no corpus identity |
| `fire_weather_v1_btsd_unused_query.txt` | `0ba70b64766386c6baab187192351b578a1f0809cdc20ba02ae7b472dc88744f` | **unused / not executed as corpus-defining query** |
| `extreme_heat_v1_btsd_unused_query.txt` | `bf292b1fabf45c8dbd977026c8863475c83fc3500434f7b343ac918ddc7ad20b` | **unused / not executed as corpus-defining query** |

Hashes from `evidence/query_hashes_v1.txt`; every tracked query file re-hashes to
them (test). In each production query the first group is **topical** (decides
concept membership) and the second an AND-ed **context clause** (constrains
precision only; never a concept alias --- D-022). Places: none, in any query.

**Traceability of the topical terms to `concept_map.yaml`** (concept-first
ruling, acceptance criteria 5--6), computed with the repo matcher:

| Topical term | In `concept_map.yaml` | On a dictionary line |
| --- | --- | --- |
| `fire weather index` | yes (`fire_weather_index`) | yes (12 lines) |
| `fwi` | yes, as `FWI` | yes (47 lines) |
| `canadian forest fire weather index` | **no** | yes --- line 293, a cited span of `fire_weather_index` |
| `fire-weather index` | **no** | **no** |
| `canadian fwi` | **no** | **no** |
| `heat index` | yes (`heat_index`) | yes (53 lines) |
| `heat-index` | **no** | **no** |
| `extended heat index` | **no** | **no** |

Five topical terms are hyphenation or compound variants that are not concept-map
surface terms. GUIDANCE accepted the production queries as "restricted to
approved family vocabulary" (D-022) and named `fire-weather index` and
`canadian fwi` as approved disambiguators; the concept map was **not** changed.
Whether that acceptance is the governance record for all five is put to
GUIDANCE (report field 13).

## 4. Yields

| Run | Role | Count | Ids |
| --- | --- | --- | --- |
| `fire_weather_v1` | production | **4** | `ids/fire_weather_v1_ids.txt` |
| `extreme_heat_v1` | production | **10** | `ids/extreme_heat_v1_ids.txt` |
| `fire_weather_diag_topical_only` | diagnostic | 13 | `ids/fire_weather_diag_topical_only_ids.txt` |
| `extreme_heat_diag_topical_only` | diagnostic | 11 | `ids/extreme_heat_diag_topical_only_ids.txt` |

- Each count equals the extract log's "DuckDB returned N unique document(s)" and
  the raw-record hash list (test).
- **Cross-arm overlap: 0.** Unique production items: **14**. Exact-byte duplicate
  groups among them: **none**.
- Each production arm is contained in its diagnostic: the context clause removes
  **9** fire-weather and **1** heat-index document. Dropping it does not reveal
  a large hidden pool (ruling).

## 5. FWI collision evidence (verbatim, `evidence/fwi_collision_snippets.txt`)

Ten of the 13 diagnostic `fwi` documents, as the collection team extracted them:

```text
== 244316563: c and statistical seismic inversion [5], and Full Waveform Inversion (FWI) for P-wave velocity estimation of near-surface seismic data [6]. Sur
== 258509670: C893DC7103AD48AA0FarXiv:2111.02926v6[cs.LG]\nFull waveform inversion (FWI) is widely used in geophysics to reconstruct highresolution velocity 
== 232342359: an for Older Cattle. Farmers Weekly. Available online at: https://www.fwi.co.uk/livestock/ beef/beef-farmers-split-over-carbon-tax-plan-for-old
== 232332945: on for certain structured velocity models\n\nFull-waveform inversion (FWI) is a method used to determine properties of the Earth from informati
== 257970033: r: (a)Database JATAM, 2000, (b).Perkembangan Jumlah HPH di Indonesia, FWI (April 2001), (c)Siaran pers WALHt Jakarta, 6 Nopember 2001, (d)Dephu
== 213672196: te transpose of P + j .\n\n\nTarget-oriented full waveform inversion (FWI-res)\n\nFWI-res is a target-oriented elastic wave-equation based inve
== 270637568: d.The maximal standard deviation of a Young's modulus determined with FWI was 0.36, while that determined with manual picking was 1.11.Young's 
== 253457291: sing a wave-equation based methodology named full-waveform inversion (FWI). From the assumption that the residual seismic data (the difference 
== 116023495: Table 1 gives an overview of the total number of fatal work injuries (FWI) occurring in the Czech Republic in the period 2006 -2016, including 
== 108962524: ms and management: fraction of the soil surface wetted by irrigation (fwi), distribution efficiency for the desired percentage adequacy (EDad),
```

Two of them, **`232342359`** and **`257970033`**, are in the 4-paper production
arm. So the arm holds **at most 2 plausible Fire Weather Index papers before
reading** (D-022). The snippets are the collection team's evidence, kept as
received; they motivated R-FWI-1 and were not used to read any paper.

## 6. R-FWI-1 applied retroactively --- **2 of 4 admitted**

The rule (D-022; `docs/BRIDGE_ELIGIBILITY.md` §5) was applied to the four
fire-weather records **by term-hit evidence only**, from the raw JSON text with
the repo matcher (`climrr.retrieval.evaluate`, every string value at any depth;
`section_key` is the value's JSON path). It ran on a **Polaris login node**
(`polaris-login-01`) **from the Eagle checkout at `968e7ba`** (clean tree), by
Kaiyuan, with `scripts/litcollect/apply_rfwi1_litcorpus01.py`; each record was
SHA-256-verified against `evidence/litcorpus01_raw_hashes.txt` first. Result:
`artifacts/literature/litcorpus01/rfwi1_retroactive.json` (SHA-256
`7ba860d6d179f929c47254f7a10c94506ffe91fd6a0a9f0da23ca86f00c75db0`); run record
`reports/runs/20261019T225623Z_local_apply_rfwi1_litcorpus01.{json,md}`.

**Post-R-FWI-1 count for the fire arm: 2.**

| Item | Decision | Basis | First hits (`$.content.text`, section idx, `[start, end)`) |
| --- | --- | --- | --- |
| 134165809 | **admitted** | `direct_topical_term` | `Fire Weather Index` 6 `[4467, 4485)`; bare `FWI` 6 `[4487, 4490)` |
| 188013273 | **admitted** | `direct_topical_term` | `Fire Weather Index` 7 `[145599, 145617)`; bare `FWI` 7 `[145619, 145622)`; disambiguator `fire weather` 7 `[137550, 137562)` |
| 232342359 | excluded | `bare_fwi_without_disambiguator` | bare `fwi` 5 `[118340, 118343)`; no disambiguator |
| 257970033 | excluded | `bare_fwi_without_disambiguator` | bare `FWI` 6 `[39325, 39328)`; no disambiguator |

The two excluded records are exactly the two collision documents of §5 that sit
in this arm --- consistent with the collision evidence, and with "at most 2
plausible FWI papers". Admission is a retrieval decision only; it does not
establish that either paper concerns the ClimRR FWI metric. Checked by
`tests/test_litcorpus.py` (all four hashes equal the pinned raw-record hashes;
decisions; run record).

**Disclosed about the run:**

- The run record's `location` label reads `local` (hence `_local_` in its file
  name): `climrr.runrecord.detect_location()` knows only `sophia` (by hostname)
  and labels every other host `local`. The `hostname`, `polaris-login-01`, is
  the authoritative execution location. The labeller is unchanged.
- The Polaris Python (3.13.14) does **not** match the D-007 pins (pandas,
  pytest, pypdfium2 not installed; numpy 2.5.3; pypdf 6.14.2; `pip freeze`
  unavailable). The rule uses only the standard library and PyYAML (to load
  the concept map), and PyYAML 6.0.3 **matches** its pin; none of the
  mismatched libraries is imported on this path.
- `litcorpus01_manifest.json` (frozen at `85ed69a`, pinned in
  `data/manifest.json`) still reads `rfwi1_retroactive: pending`. It is left
  unchanged as the freeze-time record; `rfwi1_retroactive.json` is the result
  and supersedes that field.

## 7. Stable ids and manifest

Item id = the source basename (S2 corpus id); per-item SHA-256 of the raw record
from `evidence/litcorpus01_raw_hashes.txt`. No `LIT1-` id is minted: the work
package assigns project ids only to LITCORPUS-02.

| Item | Arm | SHA-256 (raw record) |
| --- | --- | --- |
| 134165809 | fire_weather_v1 | `6c62d5cdbc68895f3ca4350376fc641a598afaa918c7e31b73b2ddd7c86d00db` |
| 188013273 | fire_weather_v1 | `20a6b7998b97f7edbd8d7f68209540a7edd8c4347a1d4303bccee0d10c5936c9` |
| 232342359 | fire_weather_v1 | `1d68b87de377c029689dc7e4f79076ca20488488a9d767230d88b4be9d77310f` |
| 257970033 | fire_weather_v1 | `0593280c0d011553eeae9d35f5c1f4ac8f0ecabc0e582327ac7d6f927019550a` |
| 225650344, 231794159, 237366756, 253185764, 255846265, 257091399, 268348353, 271592278, 271724531, 4865538 | extreme_heat_v1 | full hashes in `litcorpus01_manifest.csv` |

`litcorpus01_manifest.csv` SHA-256
**`c686425710a5c5ad23abdd904d0ca38982933b978c04463594b3ea6469faeda8`**, recorded
in `data/manifest.json` under `external_corpora` (`LITCORPUS-01-conceptfirst-v1`).

## 8. Sectionization --- **closed as not required (D-025)**

GUIDANCE confirmed LITCORPUS-02 as the working corpus and closed LITCORPUS-01
sectionization as not required. The record below is kept as written.

The ruling authorizes sectionizing and flattening the 14 raw records (action 13).
**It was not done.** The raw records are hash-pinned and stay on Eagle; GUIDANCE
is asked first to confirm that **LITCORPUS-02 supersedes LITCORPUS-01 as the
working corpus**, before the sectionizer run is spent on 14 records that may not
be used.

## 9. Redaction

`evidence/shard_listing.txt` carried the absolute Eagle directory of the shard;
the tracked copy reads `<EAGLE_DIR>/`. Original and redacted SHA-256 are in
`redactions.json`. Every other LITCORPUS-01 evidence file is byte-identical to
the bundle.
