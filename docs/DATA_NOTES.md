# Data notes

What is **computed**, what the **data dictionary states**, and what is **open**.
The three are kept apart on purpose: a computed number is a fact about characters
in a file, and it stays one until the tracked data dictionary says what it measures.
A statement may enter section 2 only with an exact quoted span and a line number in
`data/metadata/dictionary_extracted.txt`.

Milestone status: **M1, work package WP1.** M1 is not complete.

## The three charter cautions

These constrain everything below and are restated from [`../CLAUDE.md`](../CLAUDE.md).
They are project rules, not findings of this work package.

1. **Historical fields are modeled baselines, not observations.** Anything named
   `*_hist` (or `Hist`, `HIS`) is model output for a historical period. It is never
   described here as measured, observed, or recorded. The dictionary is explicit that
   the historical period 1995–2004 is *modeled* using the greenhouse-gas
   concentrations of that period (`dictionary_extracted.txt` line 102).
2. **`wildfire*` columns are a Fire Weather Index, never wildfire occurrence.** The
   dictionary places every `wildfire_*` field under the section “Fire Weather Index -
   Averages” (line 637) and states that FWI “is useful for evaluating
   weather-based conditions that heighten the danger of wildfire spread once ignition
   has occurred; it does not account for sources of ignition”
   (lines 300–301). An FWI value is not a fire, a burned
   area, an ignition probability, or a risk to a structure.
3. **GEOID and other Census identifiers are strings with leading zeros.** They are
   read as text and kept as text. Section 1 records the counts that prove the zeros
   survived both readers.

---

## 1. Computed data properties

Deterministic facts about the bytes, produced by `scripts/profile_fulldata.py` and
re-checked by `scripts/crosscheck_profile_pandas.py`. **No meaning is assigned to any
number in this section.**

- Full machine-readable profile: [`../artifacts/profiles/fulldata_profile.json`](../artifacts/profiles/fulldata_profile.json)
- Human-readable summary: [`../artifacts/profiles/fulldata_profile.csv`](../artifacts/profiles/fulldata_profile.csv)
- Independent re-count: [`../artifacts/profiles/crosscheck_pandas.json`](../artifacts/profiles/crosscheck_pandas.json)

### Dataset identity

| | |
| --- | --- |
| SHA-256 | `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e` |
| Bytes | 296,407,423 |
| Data rows | 62,834 (header excluded) |
| Columns | 275 |
| Encoding | UTF-8 with a byte-order mark on the header line; read `utf-8-sig`, never stripped on disk |
| Profile content hash | `772991c7c9adf475c2ca51806998494595d445725d6d3b7d5046752074fcba9c` |

The **profile content hash** is the SHA-256 of the profile JSON with its `environment`
block removed, canonicalised with sorted keys. It excludes hostname, Python version,
pinned library versions and the commit, and covers every computed fact and rule
constant — so it is the value two hosts compare.

### Structural facts

| Fact | Value |
| --- | --- |
| Duplicate column names | **none** — all 275 names are distinct |
| Rows with an unexpected field count | 0 short, 0 long (every row has exactly 275 fields) |
| Columns whose non-empty values all match the decimal regex | 248 |
| Columns whose non-empty values all match the integer regex | 7 |
| Columns containing values with a leading zero | 2 |
| Constant columns (≤ 1 distinct non-empty value) | 5 |
| Columns whose non-empty values are all distinct | 20 |
| Columns with at least one empty value | 105 |
| Columns with at least one candidate-sentinel value | 24 |

The decimal regex is `^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$`,
the integer regex `^[+-]?[0-9]+$`, and the leading-zero regex
`^0[0-9]+$`. All three are documented in
`src/climrr/profile.py`. A column “matching the decimal regex” is a statement about
characters; it says nothing about what the number counts or in what unit.

### Columns carrying leading zeros

Caution 3 in numbers. Both readers agree on every count.

| Index | Name | Values with a leading zero | Distinct | Length | Text range |
| --- | --- | --- | --- | --- | --- |
| 108 | `TRACTCE` | 29,467 | 4,689 | 6–6 | `000100` … `990300` |
| 109 | `GEOID` | 19,074 | 12,941 | 11–11 | `01001020300` … `56045951100` |

Read as integers these would become 100 and 1001020300, destroying real identifiers
and silently corrupting every join. They are read as text and stay text.

### Constant columns

| Index | Name | The single non-empty value | Rows carrying it | Empty rows |
| --- | --- | --- | --- | --- |
| 117 | `Aggregate_Resilience_Indicator_` | `-9` | 62,834 | 0 |
| 269 | `created_us` | `CBURDI` | 62,751 | 83 |
| 270 | `created_da` | `9/13/2023 0:00:00` | 62,751 | 83 |
| 271 | `last_edite` | `CBURDI` | 62,751 | 83 |
| 272 | `last_edi_1` | `9/13/2023 0:00:00` | 62,751 | 83 |

### Empty values

A value is empty when it is the empty string after `str.strip()`. Emptiness clusters
into a small number of groups, which is itself a structural fact — what it *means* is
not established.

| Empty rows | Columns | Column indices |
| --- | --- | --- |
| 7 | 2 | 3–4 |
| 8 | 4 | 108–111 |
| 22 | 32 | 203–234 |
| 83 | 40 | 235–274 |
| 241 | 5 | 112–113, 115–116, 118 |
| 6,938 | 22 | 11–32 |
| 0 | 170 | all remaining |

### Candidate sentinel values — quantitative flag only

A value is listed here when it is a numeric extreme of its column **and** occurs on at
least 0.5% of rows. **This is a frequency statement and nothing more.** It is
not a claim that the value is missing, invalid, a fill value, or special in any way.
No semantics are assigned; see section 3.

That the rule flags `TRACTCE` — an identifier column — is the clearest demonstration
of its limits: `000100` is simply that column's smallest text value and a common one.

| Index | Name | Value | Rows |
| --- | --- | --- | --- |
| 8 | `cdd_hist` | `0.000000000000000` | 1,156 |
| 9 | `cdd_rcp85_midc` | `0.000000000000000` | 762 |
| 108 | `TRACTCE` | `000100` | 6,618 |
| 110 | `NAME_1` | `1` | 6,618 |
| 112 | `Percentage_of_the_population_65` | `0.000000000000000` | 380 |
| 115 | `Percentage_of_housing_units_tha` | `0.000000000000000` | 2,889 |
| 117 | `Aggregate_Resilience_Indicator_` | `-9` | 62,834 |
| 240 | `heatindex_HIS_Day95` | `0.000000000000000` | 19,707 |
| 241 | `heatindex_HIS_Day105` | `0.000000000000000` | 32,960 |
| 242 | `heatindex_HIS_Day115` | `0.000000000000000` | 48,975 |
| 243 | `heatindex_HIS_Day125` | `0.000000000000000` | 54,443 |
| 246 | `heatindex_M85_Day95` | `0.000000000000000` | 10,944 |
| 247 | `heatindex_M85_Day105` | `0.000000000000000` | 14,647 |
| 248 | `heatindex_M85_Day115` | `0.000000000000000` | 16,157 |
| 249 | `heatindex_M85_Day125` | `0.000000000000000` | 17,256 |
| 252 | `heatindex_E85_Day95` | `0.000000000000000` | 7,141 |
| 253 | `heatindex_E85_Day105` | `0.000000000000000` | 11,815 |
| 254 | `heatindex_E85_Day115` | `0.000000000000000` | 13,684 |
| 255 | `heatindex_E85_Day125` | `0.000000000000000` | 14,914 |
| 259 | `heatindex_C_M85_D105` | `0.000000000000000` | 14,647 |
| 261 | `heatindex_C_M85_D125` | `0.000000000000000` | 17,256 |
| 264 | `heatindex_C_E85_D95` | `0.000000000000000` | 7,141 |
| 265 | `heatindex_C_E85_D105` | `0.000000000000000` | 11,815 |
| 267 | `heatindex_C_E85_D125` | `0.000000000000000` | 14,915 |

### Independent re-count

`artifacts/profiles/fulldata_profile.json` was recomputed with pandas 3.0.5 /
numpy 2.4.6 reading the same bytes with
`dtype=str, keep_default_na=False, na_filter=False`, addressing columns by position.
**275 of 275 columns agree on every compared field**
(`n_rows`, `n_columns`, `name`, `n_empty`, `n_distinct`, `n_with_leading_zero_any`), with
0 disagreements. Row and column counts agree.

### Environment (non-pinned facts)

The two hosts run different Python minor versions, and D-007 leaves that free
deliberately. What is pinned is the parsing and profiling stack.

| Host | Python | Environment |
| --- | --- | --- |
| Local authoring machine | **3.11.16** | conda env `climrr` |
| Sophia (`sophia-login-02`) | **3.13.13** | venv `.venv-sophia` over the ALCF conda base |

Pinned under D-007 in `requirements.txt`, and recorded in every run record's
`pinned_libraries` field: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`, `pyyaml==6.0.3`, `pytest==9.1.1`.

---

## 2. Dictionary-verified semantics

**Only** columns whose status in
[`../artifacts/profiles/dictionary_coverage.json`](../artifacts/profiles/dictionary_coverage.json)
is `verified_from_dictionary` — 21 of 275 columns. Every row quotes the
dictionary verbatim and cites a line of `data/metadata/dictionary_extracted.txt`.
Nothing here is paraphrased, and nothing enters this section without a span.

A column reaches this status only when **its own name** appears in the dictionary,
every entry using that name agrees, and the quoted span states a meaning, a unit or
type, and a scenario or horizon. That is why the list is short: the dictionary names
most of its fields by suffix within a per-variable section (`HIST`, `RCP45_MIDC`),
while the CSV writes a stem plus that suffix (`tempmaxann_rcp45_midc`), and the
dictionary never states that a CSV stem denotes a section. Section 3 covers the rest.

| Index | Column | Dictionary section | Line | Quoted dictionary text |
| --- | --- | --- | --- | --- |
| 1 | `Crossmodel` | Temperature Minimum – Annual | 455 | Crossmodel Truncated name for "Crossmodel_CellName". Text ID for each cell in the polygon grid. |
| 180 | `wildfire_autumn_Pmid` | Fire Weather Index - Averages | 652 | Wildfire_autumn_Pmid Percent Change between Mid-Century and Historical |
| 181 | `wildfire_autumn_Pend` | Fire Weather Index - Averages | 653 | Wildfire_autumn_Pend Percent Change between End-Century and Historical |
| 187 | `wildfire_spring_Pmid` | Fire Weather Index - Averages | 659 | Wildfire_spring_Pmid Percent Change between Mid-Century and Historical |
| 188 | `wildfire_spring_Pend` | Fire Weather Index - Averages | 660 | Wildfire_spring_Pend Percent Change between End-Century and Historical |
| 194 | `wildfire_summer_Pmid` | Fire Weather Index - Averages | 666 | Wildfire_summer_Pmid Percent Change between Mid-Century and Historical |
| 195 | `wildfire_summer_Pend` | Fire Weather Index - Averages | 667 | Wildfire_summer_Pend Percent Change between End-Century and Historical |
| 201 | `wildfire_winter_Pmid` | Fire Weather Index - Averages | 673 | Wildfire_winter_Pmid Percent Change between Mid-Century and Historical |
| 202 | `wildfire_winter_Pend` | Fire Weather Index - Averages | 674 | Wildfire_winter_Pend Percent Change between End-Century and Historical |
| 240 | `heatindex_HIS_Day95` | Heat Index – Summer | 679 | heatindex_HIS_Day95 Number of Summer days with daily max heat index above 95 F -- Historical |
| 241 | `heatindex_HIS_Day105` | Heat Index – Summer | 680 | heatindex_HIS_Day105 Number of Summer days with daily max heat index above 105 F -- Historical |
| 242 | `heatindex_HIS_Day115` | Heat Index – Summer | 681 | heatindex_HIS_Day115 Number of Summer days with daily max heat index above 115 F -- Historical |
| 243 | `heatindex_HIS_Day125` | Heat Index – Summer | 682 | heatindex_HIS_Day125 Number of Summer days with daily max heat index above 125 F -- Historical |
| 246 | `heatindex_M85_Day95` | Heat Index – Summer | 685 | heatindex_M85_Day95 Number of Summer days with daily max heat index above 95 F -- Mid-Century RCP8.5 |
| 247 | `heatindex_M85_Day105` | Heat Index – Summer | 686 | heatindex_M85_Day105 Number of Summer days with daily max heat index above 105 F -- Mid-Century RCP8.5 |
| 248 | `heatindex_M85_Day115` | Heat Index – Summer | 687 | heatindex_M85_Day115 Number of Summer days with daily max heat index above 115 F -- Mid-Century RCP8.5 |
| 249 | `heatindex_M85_Day125` | Heat Index – Summer | 688 | heatindex_M85_Day125 Number of Summer days with daily max heat index above 125 F -- Mid-Century RCP8.5 |
| 252 | `heatindex_E85_Day95` | Heat Index – Summer | 694 | heatindex_E85_Day95 Number of Summer days with daily max heat index above 95 F -- End-Century RCP8.5 |
| 253 | `heatindex_E85_Day105` | Heat Index – Summer | 695 | heatindex_E85_Day105 Number of Summer days with daily max heat index above 105 F -- End-Century RCP8.5 |
| 254 | `heatindex_E85_Day115` | Heat Index – Summer | 696 | heatindex_E85_Day115 Number of Summer days with daily max heat index above 115 F -- End-Century RCP8.5 |
| 255 | `heatindex_E85_Day125` | Heat Index – Summer | 697 | heatindex_E85_Day125 Number of Summer days with daily max heat index above 125 F -- End-Century RCP8.5 |

Two things these rows establish that matter beyond their own columns:

- The dictionary itself places the `wildfire_*` columns under **“Fire Weather Index -
  Averages”**. Caution 2 is therefore not merely a project rule; it is what the
  authoritative metadata says.
- `Crossmodel` is described as a **“Text ID for each cell in the polygon grid”**, and
  identically in all eleven sections. Whether the CSV's `Crossmodel_1` and
  `Crossmodel_12` are the same identifier is **not** stated — see section 3.

---

## 3. Unresolved metadata questions

The full, mentor-facing inventory is [`METADATA_QUESTIONS.md`](METADATA_QUESTIONS.md),
grouped by column family, each question naming the column indices it affects and the
dictionary line to check. Per-column detail, including the exact spans, is in
[`../artifacts/profiles/dictionary_coverage.json`](../artifacts/profiles/dictionary_coverage.json).

| Status | Columns | Meaning |
| --- | --- | --- |
| `verified_from_dictionary` | 21 | Name, meaning and unit/scenario/horizon all stated in a cited span |
| `partially_resolved` | 143 | Evidence cited, but something is missing or the link to it is EXECUTOR-proposed |
| `unresolved` | 28 | Name not found, or the cited evidence is blank or ambiguous |
| `structurally_observed_only` | 83 | No dictionary evidence at all; only the section 1 facts |
| **Total** | **275** | |

Also unresolved, and not guessed:

- The **acquisition date** of the ClimRR export is unknown.
- Whether a `candidate_sentinel_value` in section 1 means anything at all.

---

## Appendix A — column-name inventory (names only, no interpretation)

Transcribed verbatim from the CSV header in file order during M0, including any
truncation or abbreviation present in the source. Names are **not** renamed,
corrected, grouped, or annotated. The profile confirms all 275 names are distinct.

| # | Column name (verbatim) |
| --- | --- |
| 0 | `OID_` |
| 1 | `Crossmodel` |
| 2 | `NAME` |
| 3 | `State` |
| 4 | `State_Abbr` |
| 5 | `hdd_hist` |
| 6 | `hdd_rcp85_midc` |
| 7 | `hdd_mid85_hist` |
| 8 | `cdd_hist` |
| 9 | `cdd_rcp85_midc` |
| 10 | `cdd_mid85_hist` |
| 11 | `noprecip_hist` |
| 12 | `noprecip_rcp45_midc` |
| 13 | `noprecip_rcp45_endc` |
| 14 | `noprecip_rcp85_midc` |
| 15 | `noprecip_rcp85_endc` |
| 16 | `noprecip_mid45_hist` |
| 17 | `noprecip_end45_hist` |
| 18 | `noprecip_mid85_hist` |
| 19 | `noprecip_end85_hist` |
| 20 | `noprecip_mid85_45` |
| 21 | `noprecip_end85_45` |
| 22 | `precipann_hist` |
| 23 | `precipann_rcp45_midc` |
| 24 | `precipann_rcp45_endc` |
| 25 | `precipann_rcp85_midc` |
| 26 | `precipann_rcp85_endc` |
| 27 | `precipann_mid45_hist` |
| 28 | `precipann_end45_hist` |
| 29 | `precipann_mid85_hist` |
| 30 | `precipann_end85_hist` |
| 31 | `precipann_mid85_45` |
| 32 | `precipann_end85_45` |
| 33 | `windspeed_hist` |
| 34 | `windspeed_rcp45_midc` |
| 35 | `windspeed_rcp45_endc` |
| 36 | `windspeed_rcp85_midc` |
| 37 | `windspeed_rcp85_endc` |
| 38 | `windspeed_mid45_hist` |
| 39 | `windspeed_end45_hist` |
| 40 | `windspeed_mid85_hist` |
| 41 | `windspeed_end85_hist` |
| 42 | `windspeed_mid85_45` |
| 43 | `windspeed_end85_45` |
| 44 | `tempmaxann_hist` |
| 45 | `tempmaxann_rcp45_midc` |
| 46 | `tempmaxann_rcp45_endc` |
| 47 | `tempmaxann_rcp85_midc` |
| 48 | `tempmaxann_rcp85_endc` |
| 49 | `tempmaxann_mid45_hist` |
| 50 | `tempmaxann_end45_hist` |
| 51 | `tempmaxann_mid85_hist` |
| 52 | `tempmaxann_end85_hist` |
| 53 | `tempmaxann_mid85_45` |
| 54 | `tempmaxann_end85_45` |
| 55 | `tempmax_seas_hist_winter` |
| 56 | `tempmax_seas_rcp85_midc_winter` |
| 57 | `tempmax_seas_rcp85_endc_winter` |
| 58 | `tempmax_seas_mid85_hist_winter` |
| 59 | `tempmax_seas_end85_hist_winter` |
| 60 | `tempmax_seas_hist_summer` |
| 61 | `tempmax_seas_rcp85_mid_summer` |
| 62 | `tempmax_seas_rcp85_end_summer` |
| 63 | `tempmax_seas_mid85_hist_summer` |
| 64 | `tempmax_seas_end85_hist_summer` |
| 65 | `tempmax_seas_hist_spring` |
| 66 | `tempmax_seas_rcp85_mid_spring` |
| 67 | `tempmax_seas_rcp85_end_spring` |
| 68 | `tempmax_seas_mid85_hist_sprin` |
| 69 | `tempmax_seas_end85_hist_sprin` |
| 70 | `tempmax_seas_hist_autum` |
| 71 | `tempmax_seas_rcp85_mid_autumn` |
| 72 | `tempmax_seas_rcp85_end_autumn` |
| 73 | `tempmax_seas_mid85_hist_autumn` |
| 74 | `tempmax_seas_end85_hist_autumn` |
| 75 | `tempminann_hist` |
| 76 | `tempminann_rcp45_midc` |
| 77 | `tempminann_rcp45_endc` |
| 78 | `tempminann_rcp85_midc` |
| 79 | `tempminann_rcp85_endc` |
| 80 | `tempminann_mid45_hist` |
| 81 | `tempminann_end45_hist` |
| 82 | `tempminann_mid85_hist` |
| 83 | `tempminann_end85_hist` |
| 84 | `tempminann_mid85_45` |
| 85 | `tempminann_end85_45` |
| 86 | `tempmin_seas_hist_winter` |
| 87 | `tempmin_seas_rcp85_midc_winter` |
| 88 | `tempmin_seas_rcp85_endc_winter` |
| 89 | `tempmin_seas_mid85_hist_winter` |
| 90 | `tempmin_seas_end85_hist_winter` |
| 91 | `tempmin_seas_hist_summer` |
| 92 | `tempmin_seas_rcp85_mid_summer` |
| 93 | `tempmin_seas_rcp85_end_summer` |
| 94 | `tempmin_seas_mid85_hist_summer` |
| 95 | `tempmin_seas_end85_hist_summer` |
| 96 | `tempmin_seas_hist_spring` |
| 97 | `tempmin_seas_rcp85_mid_spring` |
| 98 | `tempmin_seas_rcp85_end_spring` |
| 99 | `tempmin_seas_mid85_hist_sprin` |
| 100 | `tempmin_seas_end85_hist_sprin` |
| 101 | `tempmin_seas_hist_autum` |
| 102 | `tempmin_seas_rcp85_mid_autumn` |
| 103 | `tempmin_seas_rcp85_end_autumn` |
| 104 | `tempmin_seas_mid85_hist_autumn` |
| 105 | `tempmin_seas_end85_hist_autumn` |
| 106 | `X` |
| 107 | `Y` |
| 108 | `TRACTCE` |
| 109 | `GEOID` |
| 110 | `NAME_1` |
| 111 | `NAMELSAD` |
| 112 | `Percentage_of_the_population_65` |
| 113 | `Gini_Index_of_income_inequality` |
| 114 | `Pop_below_U_S__Census_poverty_l` |
| 115 | `Percentage_of_housing_units_tha` |
| 116 | `Aggregate_Resilience_Indicator` |
| 117 | `Aggregate_Resilience_Indicator_` |
| 118 | `The_net_migration__internationa` |
| 119 | `precipdaily_histmean_winter` |
| 120 | `precipdaily_mid85mean_winter` |
| 121 | `precipdaily_end85mean_winter` |
| 122 | `precipdaily_Dmid_mean_winter` |
| 123 | `precipdaily_Dend_mean_winter` |
| 124 | `precipdaily_Pmid_mean_winter` |
| 125 | `precipdaily_Pend_mean_winter` |
| 126 | `precipdaily_histmax_winter` |
| 127 | `precipdaily_mid85max_winter` |
| 128 | `precipdaily_end85max_winter` |
| 129 | `precipdaily_Dmid_max_winter` |
| 130 | `precipdaily_Dend_max_winter` |
| 131 | `precipdaily_Pmid_max_winter` |
| 132 | `precipdaily_Pend_max_winter` |
| 133 | `precipdaily_histmean_spring` |
| 134 | `precipdaily_mid85mean_spring` |
| 135 | `precipdaily_end85mean_spring` |
| 136 | `precipdaily_Dmid_mean_spring` |
| 137 | `precipdaily_Dend_mean_spring` |
| 138 | `precipdaily_Pmid_mean_spring` |
| 139 | `precipdaily_Pend_mean_spring` |
| 140 | `precipdaily_histmax_spring` |
| 141 | `precipdaily_mid85max_spring` |
| 142 | `precipdaily_end85max_spring` |
| 143 | `precipdaily_Dmid_max_spring` |
| 144 | `precipdaily_Dend_max_spring` |
| 145 | `precipdaily_Pmid_max_spring` |
| 146 | `precipdaily_Pend_max_spring` |
| 147 | `precipdaily_histmean_summer` |
| 148 | `precipdaily_mid85mea_summer` |
| 149 | `precipdaily_end85mea_summer` |
| 150 | `precipdaily_Dmid_mea_summer` |
| 151 | `precipdaily_Dend_mea_summer` |
| 152 | `precipdaily_Pmid_mea_summer` |
| 153 | `precipdaily_Pend_mea_summer` |
| 154 | `precipdaily_histmax_summer` |
| 155 | `precipdaily_mid85max_summer` |
| 156 | `precipdaily_end85max_summer` |
| 157 | `precipdaily_Dmid_max_summer` |
| 158 | `precipdaily_Dend_max_summer` |
| 159 | `precipdaily_Pmid_max_summer` |
| 160 | `precipdaily_Pend_max_summer` |
| 161 | `precipdaily_histmean_autumn` |
| 162 | `precipdaily_mid85mea_autumn` |
| 163 | `precipdaily_end85mea_autumn` |
| 164 | `precipdaily_Dmid_mea_autumn` |
| 165 | `precipdaily_Dend_mea_autumn` |
| 166 | `precipdaily_Pmid_mea_autumn` |
| 167 | `precipdaily_Pend_mea_autumn` |
| 168 | `precipdaily_histmax_autumn` |
| 169 | `precipdaily_mid85max_autumn` |
| 170 | `precipdaily_end85max_autumn` |
| 171 | `precipdaily_Dmid_max_autumn` |
| 172 | `precipdaily_Dend_max_autumn` |
| 173 | `precipdaily_Pmid_max_autumn` |
| 174 | `precipdaily_Pend_max_autumn` |
| 175 | `wildfire_autumn_Hist` |
| 176 | `wildfire_autumn_Midc` |
| 177 | `wildfire_autumn_Endc` |
| 178 | `wildfire_autumn_Dmid` |
| 179 | `wildfire_autumn_Dend` |
| 180 | `wildfire_autumn_Pmid` |
| 181 | `wildfire_autumn_Pend` |
| 182 | `wildfire_spring_Hist` |
| 183 | `wildfire_spring_Midc` |
| 184 | `wildfire_spring_Endc` |
| 185 | `wildfire_spring_Dmid` |
| 186 | `wildfire_spring_Dend` |
| 187 | `wildfire_spring_Pmid` |
| 188 | `wildfire_spring_Pend` |
| 189 | `wildfire_summer_Hist` |
| 190 | `wildfire_summer_Midc` |
| 191 | `wildfire_summer_Endc` |
| 192 | `wildfire_summer_Dmid` |
| 193 | `wildfire_summer_Dend` |
| 194 | `wildfire_summer_Pmid` |
| 195 | `wildfire_summer_Pend` |
| 196 | `wildfire_winter_Hist` |
| 197 | `wildfire_winter_Midc` |
| 198 | `wildfire_winter_Endc` |
| 199 | `wildfire_winter_Dmid` |
| 200 | `wildfire_winter_Dend` |
| 201 | `wildfire_winter_Pmid` |
| 202 | `wildfire_winter_Pend` |
| 203 | `OBJECTID_1` |
| 204 | `Crossmodel_1` |
| 205 | `FWI_Bins_Hist_95` |
| 206 | `FWI_Bins_Hist_NC` |
| 207 | `FWI_Bins_MidC_95` |
| 208 | `FWI_Bins_MidC_NC` |
| 209 | `FWI_Bins_EndC_95` |
| 210 | `FWI_Bins_EndC_NC` |
| 211 | `FWIBins_HistSpr_95` |
| 212 | `FWIBins_HistSpr_NC` |
| 213 | `FWIBins_HistSum_95` |
| 214 | `FWIBins_HistSum_NC` |
| 215 | `FWIBins_HistAut_95` |
| 216 | `FWIBins_HistAut_NC` |
| 217 | `FWIBins_HistWin_95` |
| 218 | `FWIBins_HistWin_NC` |
| 219 | `FWIBins_MidSpr_95` |
| 220 | `FWIBins_MidSpr_NC` |
| 221 | `FWIBins_MidSum_95` |
| 222 | `FWIBins_MidSum_NC` |
| 223 | `FWIBins_MidAut_95` |
| 224 | `FWIBins_MidAut_NC` |
| 225 | `FWIBins_MidWin_95` |
| 226 | `FWIBins_MidWin_NC` |
| 227 | `FWIBins_EndSpr_95` |
| 228 | `FWIBins_EndSpr_NC` |
| 229 | `FWIBins_EndSum_95` |
| 230 | `FWIBins_EndSum_NC` |
| 231 | `FWIBins_EndAut_95` |
| 232 | `FWIBins_EndAut_NC` |
| 233 | `FWIBins_EndWin_95` |
| 234 | `FWIBins_EndWin_NC` |
| 235 | `OBJECTID_12` |
| 236 | `OBJECTID_12_13` |
| 237 | `Crossmodel_12` |
| 238 | `heatindex_HIS_DayMax` |
| 239 | `heatindex_HIS_SeaMax` |
| 240 | `heatindex_HIS_Day95` |
| 241 | `heatindex_HIS_Day105` |
| 242 | `heatindex_HIS_Day115` |
| 243 | `heatindex_HIS_Day125` |
| 244 | `heatindex_M85_DayMax` |
| 245 | `heatindex_M85_SeaMax` |
| 246 | `heatindex_M85_Day95` |
| 247 | `heatindex_M85_Day105` |
| 248 | `heatindex_M85_Day115` |
| 249 | `heatindex_M85_Day125` |
| 250 | `heatindex_E85_DayMax` |
| 251 | `heatindex_E85_SeaMax` |
| 252 | `heatindex_E85_Day95` |
| 253 | `heatindex_E85_Day105` |
| 254 | `heatindex_E85_Day115` |
| 255 | `heatindex_E85_Day125` |
| 256 | `heatindex_C_M85_DMax` |
| 257 | `heatindex_C_M85_SMax` |
| 258 | `heatindex_C_M85_D95` |
| 259 | `heatindex_C_M85_D105` |
| 260 | `heatindex_C_M85_D115` |
| 261 | `heatindex_C_M85_D125` |
| 262 | `heatindex_C_E85_DMax` |
| 263 | `heatindex_C_E85_SMax` |
| 264 | `heatindex_C_E85_D95` |
| 265 | `heatindex_C_E85_D105` |
| 266 | `heatindex_C_E85_D115` |
| 267 | `heatindex_C_E85_D125` |
| 268 | `GlobalID` |
| 269 | `created_us` |
| 270 | `created_da` |
| 271 | `last_edite` |
| 272 | `last_edi_1` |
| 273 | `Shape_STAr` |
| 274 | `Shape_STLe` |
