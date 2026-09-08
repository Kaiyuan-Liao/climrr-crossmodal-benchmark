# Data notes

Working record of what is *known*, what is *guessed*, and what is *open* about
the ClimRR table. The three sections below are load-bearing: a statement may
only move from Provisional to Verified when it is backed by the data dictionary
in `data/metadata/` or by an explicit decision in `DECISION_LOG.md`.

Milestone status: **M0**. Interpretation of any column is out of scope until
M1. This file therefore records column *names* and nothing else.

## Verified facts

Facts confirmed against the raw bytes or the authoritative data dictionary.

- `data/raw/FullData.csv` contains 62,834 data rows and 275 columns
  (header excluded from the row count). Verified by streaming the file with
  Python's `csv` reader; see `reports/runs/` for the run record.
- The file is UTF-8 with a byte-order mark preceding the first header name.
  The BOM is part of the hashed bytes and is stripped only at read time
  (`encoding="utf-8-sig"`), never on disk.
- SHA-256 of the file as committed:
  `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`.

## Provisional interpretations

Nothing here yet. Populated in M1, and every entry must name its evidence.

Three cautions apply from M0 onward and constrain what may ever be written
here (see `CLAUDE.md`):

1. Historical fields are **modeled baselines**, not observations.
2. `wildfire*` columns are a **Fire Weather Index**, never wildfire occurrence.
3. GEOID and other Census identifiers are **strings with leading zeros**.

## Unresolved questions

- Acquisition date of the ClimRR export is unknown and has not been guessed.
- The mapping from column name to physical variable, scenario, and time window
  is not established. This is the M1 objective.
- Duplicate or truncated column names: None observed.

## Column-name inventory --- names only, no interpretation assigned

Transcribed verbatim from the CSV header in file order, including any
truncation, abbreviation or duplication present in the source. Names are **not**
renamed, corrected, grouped, or annotated. Assigning meaning to any of these is
an M1 task.

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
