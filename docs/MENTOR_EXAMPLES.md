# Answer sheet --- ClimRR example records

**For:** the ClimRR data owner.  **From:** Kaiyuan Liao.  **Date: \_\_\_\_\_\_\_\_\_\_**

Each line below is a reading of a column in `FullData.csv` that the ClimRR data
dictionary does **not** state, and that I reasoned out instead. Please tick one
box per line. **"Don't know" is a real answer** and more useful to me than a
guess --- a line answered that way stays marked unconfirmed and its columns stay
out of use.

This sheet is the short form. The full wording of any line, the raw values it
refers to, and the reasoning behind it are on that example's page in the
document that follows.

## Example 1 --- row `OID_` 1 (`R106C361`), Stephens County, Oklahoma

| # | The reading, in brief | Tick one | If "correct" --- to what? |
| ---: | --- | --- | --- |
| **1** | **One row of this file is one "event".** The grain everything else rests on. | ☐ confirm ☐ correct ☐ don't know | |
| 2 | `heatindex_*_DayMax` (238, 244, 250) is in **°F**, on the extended heat-index scale of Lu and Romps. | ☐ confirm ☐ correct ☐ don't know | |
| 3 | `DayMax` is the summer **average** of daily maxima --- *not* the summer's single highest reading. | ☐ confirm ☐ correct ☐ don't know | |
| 4 | `heatindex_C_*_DMax` (256, 262) is that quantity **differenced**, same units. **Which way round?** | ☐ confirm ☐ correct ☐ don't know | |
| 5 | `wildfire_summer_Hist/Midc/Endc` (189–191): "Seasonal value" = the **seasonal average daily FWI**, not the 95th percentile. | ☐ confirm ☐ correct ☐ don't know | |
| 6 | FWI values are **dimensionless** index values. | ☐ confirm ☐ correct ☐ don't know | |
| 7 | `wildfire_summer_Dmid/Dend` (192–193) are **absolute differences** in index units. **Which way round?** | ☐ confirm ☐ correct ☐ don't know | |
| **8** | **The name stem `tempmaxann` denotes the dictionary section "Temperature Maximum - Annual".** **101 columns depend on this one link.** | ☐ confirm ☐ correct ☐ don't know | |
| 9 | Granting line 8: columns 44, 48, 52 are annual averages of daily max temperature in **°F** --- historical, end-century RCP8.5, and the change. | ☐ confirm ☐ correct ☐ don't know | |
| **10** | `GEOID` (109) is a **Census tract id**: state + county + tract. **Which Census vintage?** | ☐ confirm ☐ correct ☐ don't know | vintage: |
| 11 | `TRACTCE` (108) is the **tract code alone**, unique only within its county. | ☐ confirm ☐ correct ☐ don't know | |
| 12 | `X`, `Y` (106, 107) are **longitude / latitude in decimal degrees**. **Which coordinate system?** Is it the cell centroid? | ☐ confirm ☐ correct ☐ don't know | system: |
| 13 | `NAME` (2) is a **county name**; `State`/`State_Abbr` (3, 4) the state. There are **49** states here, not 50, and **7 blank rows**. Which is absent? What are the 7? | ☐ confirm ☐ correct ☐ don't know | |
| **14** | **Are these the kinds of table-side records you expect to connect to the literature?** | ☐ confirm ☐ correct ☐ don't know | |

## Example 2 --- row `OID_` 14 (`R107C232`), San Bernardino County, California

Lines 1 and 2–13 above apply here unchanged; please answer them once, above.

| # | The reading, in brief | Tick one | If "correct" --- to what? |
| ---: | --- | --- | --- |
| **E2-2** | Identifiers are carried as **text with leading zeros intact** (`GEOID` `06071010300`). Is that right, and does anything downstream expect them as numbers? | ☐ confirm ☐ correct ☐ don't know | |

## Example 3 --- row `OID_` 148 (`R105C198`), Ventura County, California

Lines 1 and 2–13 above apply here unchanged; please answer them once, above.

| # | The reading, in brief | Tick one | If "correct" --- to what? |
| ---: | --- | --- | --- |
| **E3-2** | An empty cell is written **"no value in this file"** --- never `0`, never "missing". Right? Or does an empty heat-index cell mean something specific? | ☐ confirm ☐ correct ☐ don't know | |
| **E3-3** | **83 rows are empty across every column from index 235 on.** Do you know what those 83 rows are? | ☐ confirm ☐ correct ☐ don't know | |

## The four questions behind all of this

Quoted from the project's review ruling. Each is already covered by lines above,
so there is nothing extra to tick --- they are here so you can see what the
lines add up to.

| | Question | Answered by |
| ---: | --- | --- |
| 1 | **Is one CSV row the correct unit for what she means by an “event”?** | line 1 |
| 2 | **Are the selected field interpretations correct?** | lines 2–13, E2-2, E3-2 |
| 3 | **Which assumptions in each example does she endorse or reject?** | every line you ticked |
| 4 | **Are these the kinds of table-side records she expects to connect to literature?** | line 14 |

## Anything else

Anything I have got wrong, or any field you would want in a record like this
that is not here:

&nbsp;

&nbsp;

&nbsp;

*Signed / initialled:* \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---
---

*Everything below this line is the supporting detail behind the sheet above.
You do not need to read it to answer.*

# Three example records, for review

**What I need from you: the numbered lines.** Each one is a reading I could not
confirm from the ClimRR data dictionary and had to reason out instead. Please
answer each **confirm / correct (with what) / don't know** --- "don't know" is a
useful answer and I would rather have it than a guess.

Ten minutes is enough. Everything else on this page is evidence you can ignore
unless a line looks wrong.

**How to read a record.** Each record separates three things and never mixes
them:

| | |
| --- | --- |
| **raw** | the file's own bytes, unchanged, as text |
| **semantics** | what each column is taken to mean, and on whose authority |
| **presentation** | prose generated from the semantics by template --- not written by hand |

In the generated prose, a clause in `[provisional: ...]` rests on **my
reasoning**, not on the dictionary. A clause without that mark is quoted from
the dictionary. Nothing is asserted in between.

**One thing that is assumed everywhere and confirmed nowhere:** that **one row
of the CSV is one "event"**. That is my reading of what you said on 2026-09-10,
not something you said in those words, and the whole shape of these records
rests on it. It is line 1 of every checklist below.

**Two standing cautions, which the records enforce rather than mention.** The
`wildfire_*` columns hold a **Fire Weather Index** --- a meteorological
fire-danger index, never a fire, an ignition or a burned area. Anything named
`Historical` is a **modeled baseline** for 1995--2004, never an observation.

**Scope.** 41 of the 275 columns are interpreted here --- 21 the dictionary
states outright, 20 reasoned. The other 234 are untouched and explicitly
unresolved. Full reasoning per column, with dictionary line numbers and the
alternatives I could not rule out, is in
[`../data/metadata/inferred_candidates.yaml`](../data/metadata/inferred_candidates.yaml);
the subset rationale is in [`PILOT_SUBSET.md`](PILOT_SUBSET.md).

The raw tables and generated prose below are folded away by default. Click to
open one if a checklist line makes you want to see the numbers.

---

## Example 1 --- row `OID_` 1, `Crossmodel` `R106C361`

Row ordinal 0, the first row of the file. Selected by **rule R-A**: the first
row that has a value in every one of the 41 columns. Nothing about the rule
looks at how large any value is.

Where it is: `NAME` `Stephens`, `State` `Oklahoma`, `GEOID` `40137000902`, `TRACTCE` `000902`.

<details><summary><b>Raw values (41 columns)</b></summary>

| # | Column | Raw value, exactly as stored | Status |
| ---: | --- | --- | --- |
| 1 | `Crossmodel` | `R106C361` | dictionary |
| 2 | `NAME` | `Stephens` | **inferred** |
| 3 | `State` | `Oklahoma` | **inferred** |
| 4 | `State_Abbr` | `OK` | **inferred** |
| 44 | `tempmaxann_hist` | `71.192901610000007` | **inferred** |
| 48 | `tempmaxann_rcp85_endc` | `79.597702029999994` | **inferred** |
| 52 | `tempmaxann_end85_hist` | `8.404820440000000` | **inferred** |
| 106 | `X` | `-97.592125260000003` | **inferred** |
| 107 | `Y` | `34.635850460000000` | **inferred** |
| 108 | `TRACTCE` | `000902` | **inferred** |
| 109 | `GEOID` | `40137000902` | **inferred** |
| 180 | `wildfire_autumn_Pmid` | `-24.979724999999998` | dictionary |
| 181 | `wildfire_autumn_Pend` | `-8.983711000000000` | dictionary |
| 187 | `wildfire_spring_Pmid` | `-1.958522000000000` | dictionary |
| 188 | `wildfire_spring_Pend` | `13.865197999999999` | dictionary |
| 189 | `wildfire_summer_Hist` | `25.080200200000000` | **inferred** |
| 190 | `wildfire_summer_Midc` | `28.119600299999998` | **inferred** |
| 191 | `wildfire_summer_Endc` | `31.189300540000001` | **inferred** |
| 192 | `wildfire_summer_Dmid` | `3.039439920000000` | **inferred** |
| 193 | `wildfire_summer_Dend` | `6.109189990000000` | **inferred** |
| 194 | `wildfire_summer_Pmid` | `12.118892000000001` | dictionary |
| 195 | `wildfire_summer_Pend` | `24.358664999999998` | dictionary |
| 201 | `wildfire_winter_Pmid` | `9.778568999999999` | dictionary |
| 202 | `wildfire_winter_Pend` | `57.715946000000002` | dictionary |
| 238 | `heatindex_HIS_DayMax` | `93.318659460000006` | **inferred** |
| 240 | `heatindex_HIS_Day95` | `39.799999870000001` | dictionary |
| 241 | `heatindex_HIS_Day105` | `4.499999940000000` | dictionary |
| 242 | `heatindex_HIS_Day115` | `0.000000000000000` | dictionary |
| 243 | `heatindex_HIS_Day125` | `0.000000000000000` | dictionary |
| 244 | `heatindex_M85_DayMax` | `100.914197290000004` | **inferred** |
| 246 | `heatindex_M85_Day95` | `62.933334350000003` | dictionary |
| 247 | `heatindex_M85_Day105` | `26.999999360000000` | dictionary |
| 248 | `heatindex_M85_Day115` | `4.966666530000000` | dictionary |
| 249 | `heatindex_M85_Day125` | `3.433333340000000` | dictionary |
| 250 | `heatindex_E85_DayMax` | `107.289067590000002` | **inferred** |
| 252 | `heatindex_E85_Day95` | `78.699999489999996` | dictionary |
| 253 | `heatindex_E85_Day105` | `56.099998470000003` | dictionary |
| 254 | `heatindex_E85_Day115` | `17.366666790000000` | dictionary |
| 255 | `heatindex_E85_Day125` | `2.933333400000000` | dictionary |
| 256 | `heatindex_C_M85_DMax` | `7.595537820000000` | **inferred** |
| 262 | `heatindex_C_E85_DMax` | `13.970408120000000` | **inferred** |

</details>

<details><summary><b>Generated description</b></summary>

### Candidate record --- row `OID_` 1, `Crossmodel` `R106C361`

Row ordinal 0 of the file, selected by rule **R-A** --- the first row, in file order, that is non-empty on every selected pilot column. The rule tests the ordinary case, where nothing about presentation is in question.

**A1.** One CSV row is treated as one "event". That grain is under mentor review and is **not** established as a property of this file.

> `Historical` wherever it appears below means a **modeled historical baseline** --- the dictionary's historical period, 1995 to 2004, run through the same climate models. It is not an observation, a measurement, or a record of anything that happened.

**Heat Index – Summer**

- **[238] `heatindex_HIS_DayMax`** = `93.318659460000006` --- [provisional: The ensemble-mean summer daily maximum heat index for the modeled historical period --- that is, the average over the summer's roughly 90 days of each day's maximum heat index, averaged across the three climate models. Not the single highest reading of the summer; the dictionary gives that a separate field, `heatindex_HIS_SeaMax`.] (unit or type: [provisional: degrees Fahrenheit, on the extended heat index scale of Lu and Romps (2022)]; scenario: Historical --- a modeled baseline, not an observation; horizon: the modeled historical decade, 1995-2004; season: Summer) [status: `inferred_candidate`]
- **[240] `heatindex_HIS_Day95`** = `39.799999870000001` --- Number of Summer days with daily max heat index above 95 F -- Historical (unit or type: Number of; horizon: Historical; season: Summer) [status: `verified_from_dictionary`]
- **[241] `heatindex_HIS_Day105`** = `4.499999940000000` --- Number of Summer days with daily max heat index above 105 F -- Historical (unit or type: Number of; horizon: Historical; season: Summer) [status: `verified_from_dictionary`]
- **[242] `heatindex_HIS_Day115`** = `0.000000000000000` --- Number of Summer days with daily max heat index above 115 F -- Historical (unit or type: Number of; horizon: Historical; season: Summer) [status: `verified_from_dictionary`]
- **[243] `heatindex_HIS_Day125`** = `0.000000000000000` --- Number of Summer days with daily max heat index above 125 F -- Historical (unit or type: Number of; horizon: Historical; season: Summer) [status: `verified_from_dictionary`]
- **[244] `heatindex_M85_DayMax`** = `100.914197290000004` --- [provisional: The same quantity as IC-001 --- the ensemble-mean summer daily maximum heat index --- for the mid-century RCP8.5 projection.] (unit or type: [provisional: degrees Fahrenheit, on the extended heat index scale of Lu and Romps (2022)]; scenario: RCP8.5; horizon: Mid-Century, the modeled decade 2045-2054; season: Summer) [status: `inferred_candidate`]
- **[246] `heatindex_M85_Day95`** = `62.933334350000003` --- Number of Summer days with daily max heat index above 95 F -- Mid-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[247] `heatindex_M85_Day105`** = `26.999999360000000` --- Number of Summer days with daily max heat index above 105 F -- Mid-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[248] `heatindex_M85_Day115`** = `4.966666530000000` --- Number of Summer days with daily max heat index above 115 F -- Mid-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[249] `heatindex_M85_Day125`** = `3.433333340000000` --- Number of Summer days with daily max heat index above 125 F -- Mid-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[250] `heatindex_E85_DayMax`** = `107.289067590000002` --- [provisional: The same quantity as IC-001 --- the ensemble-mean summer daily maximum heat index --- for the end-of-century RCP8.5 projection.] (unit or type: [provisional: degrees Fahrenheit, on the extended heat index scale of Lu and Romps (2022)]; scenario: RCP8.5; horizon: End-Century, the modeled decade 2085-2094; season: Summer) [status: `inferred_candidate`]
- **[252] `heatindex_E85_Day95`** = `78.699999489999996` --- Number of Summer days with daily max heat index above 95 F -- End-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[253] `heatindex_E85_Day105`** = `56.099998470000003` --- Number of Summer days with daily max heat index above 105 F -- End-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[254] `heatindex_E85_Day115`** = `17.366666790000000` --- Number of Summer days with daily max heat index above 115 F -- End-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[255] `heatindex_E85_Day125`** = `2.933333400000000` --- Number of Summer days with daily max heat index above 125 F -- End-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[256] `heatindex_C_M85_DMax`** = `7.595537820000000` --- [provisional: The change in the ensemble-mean summer daily maximum heat index between the modeled historical baseline and mid-century RCP8.5 --- that is, between the quantities in index 238 and index 244.] (unit or type: [provisional: degrees Fahrenheit on the same extended heat index scale as indices 238 and 244, expressed as a difference]; scenario: Historical compared with RCP8.5; horizon: Historical (1995-2004) to Mid-Century (2045-2054); season: Summer) [status: `inferred_candidate`]
- **[262] `heatindex_C_E85_DMax`** = `13.970408120000000` --- [provisional: The change in the ensemble-mean summer daily maximum heat index between the modeled historical baseline and end-of-century RCP8.5 --- that is, between the quantities in index 238 and index 250.] (unit or type: [provisional: degrees Fahrenheit on the same extended heat index scale as indices 238 and 250, expressed as a difference]; scenario: Historical compared with RCP8.5; horizon: Historical (1995-2004) to End-Century (2085-2094); season: Summer) [status: `inferred_candidate`]

**Fire Weather Index - Averages**

> Every `wildfire_*` column below holds a **Fire Weather Index** --- a meteorological fire-danger index, listed in the dictionary under the section "Fire Weather Index - Averages". It is not a wildfire, an ignition, a burned area, or a probability of any of those, and nothing in this record says that it is.

- **[180] `wildfire_autumn_Pmid`** = `-24.979724999999998` --- Percent Change between Mid-Century and Historical (unit or type: Percent Change; horizon: Historical, Mid-Century; season: Autumn) [status: `verified_from_dictionary`]
- **[181] `wildfire_autumn_Pend`** = `-8.983711000000000` --- Percent Change between End-Century and Historical (unit or type: Percent Change; horizon: Historical, End-Century; season: Autumn) [status: `verified_from_dictionary`]
- **[187] `wildfire_spring_Pmid`** = `-1.958522000000000` --- Percent Change between Mid-Century and Historical (unit or type: Percent Change; horizon: Historical, Mid-Century; season: Spring) [status: `verified_from_dictionary`]
- **[188] `wildfire_spring_Pend`** = `13.865197999999999` --- Percent Change between End-Century and Historical (unit or type: Percent Change; horizon: Historical, End-Century; season: Spring) [status: `verified_from_dictionary`]
- **[189] `wildfire_summer_Hist`** = `25.080200200000000` --- [provisional: The multi-model ensemble mean of the summer seasonal average daily Fire Weather Index for the modeled historical period. The FWI is a meteorological fire-danger index: it describes weather conditions, not fire occurrence, ignition, or burned area.] (unit or type: [provisional: dimensionless index value]; scenario: Historical --- a modeled baseline, not an observation; horizon: the modeled historical decade, 1995-2004; season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[190] `wildfire_summer_Midc`** = `28.119600299999998` --- [provisional: The same Fire Weather Index quantity as IC-006 --- the ensemble-mean summer seasonal average daily FWI --- for the mid-century RCP8.5 projection.] (unit or type: [provisional: dimensionless index value]; scenario: RCP8.5; horizon: Mid-Century, the modeled decade 2045-2054; season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[191] `wildfire_summer_Endc`** = `31.189300540000001` --- [provisional: The same Fire Weather Index quantity as IC-006 --- the ensemble-mean summer seasonal average daily FWI --- for the end-of-century RCP8.5 projection.] (unit or type: [provisional: dimensionless index value]; scenario: RCP8.5; horizon: End-Century, the modeled decade 2085-2094; season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[192] `wildfire_summer_Dmid`** = `3.039439920000000` --- [provisional: The difference between the mid-century RCP8.5 and modeled historical summer Fire Weather Index values --- that is, between index 190 and index 189.] (unit or type: [provisional: dimensionless index value, expressed as a difference]; scenario: Historical compared with RCP8.5; horizon: Historical (1995-2004) to Mid-Century (2045-2054); season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[193] `wildfire_summer_Dend`** = `6.109189990000000` --- [provisional: The difference between the end-of-century RCP8.5 and modeled historical summer Fire Weather Index values --- that is, between index 191 and index 189.] (unit or type: [provisional: dimensionless index value, expressed as a difference]; scenario: Historical compared with RCP8.5; horizon: Historical (1995-2004) to End-Century (2085-2094); season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[194] `wildfire_summer_Pmid`** = `12.118892000000001` --- Percent Change between Mid-Century and Historical (unit or type: Percent Change; horizon: Historical, Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[195] `wildfire_summer_Pend`** = `24.358664999999998` --- Percent Change between End-Century and Historical (unit or type: Percent Change; horizon: Historical, End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[201] `wildfire_winter_Pmid`** = `9.778568999999999` --- Percent Change between Mid-Century and Historical (unit or type: Percent Change; horizon: Historical, Mid-Century; season: Winter) [status: `verified_from_dictionary`]
- **[202] `wildfire_winter_Pend`** = `57.715946000000002` --- Percent Change between End-Century and Historical (unit or type: Percent Change; horizon: Historical, End-Century; season: Winter) [status: `verified_from_dictionary`]

**Location anchor**

> The Census vintage and the coordinate reference system of these columns are **unknown**. They locate this one row; no part of this pilot groups rows by any of them.

- **[1] `Crossmodel`** = `R106C361` --- Truncated name for "Crossmodel_CellName". Text ID for each cell in the polygon grid. (unit or type: Text ID) [status: `verified_from_dictionary`]
- **[2] `NAME`** = `Stephens` --- [provisional: A county or county-equivalent name for the area the row's grid cell falls in, joined in from a Census or similar source.] [status: `inferred_candidate`]
- **[3] `State`** = `Oklahoma` --- [provisional: The full name of the US state or state-equivalent the row's grid cell falls in, joined in from the same source as index 2.] [status: `inferred_candidate`]
- **[4] `State_Abbr`** = `OK` --- [provisional: The two-letter postal abbreviation of the state named in index 3.] [status: `inferred_candidate`]
- **[106] `X`** = `-97.592125260000003` --- [provisional: A longitude coordinate, in decimal degrees, for the row's grid cell.] (unit or type: [provisional: decimal degrees of longitude, in an unknown coordinate reference system]) [status: `inferred_candidate`]
- **[107] `Y`** = `34.635850460000000` --- [provisional: A latitude coordinate, in decimal degrees, for the row's grid cell.] (unit or type: [provisional: decimal degrees of latitude, in an unknown coordinate reference system]) [status: `inferred_candidate`]
- **[108] `TRACTCE`** = `000902` --- [provisional: A US Census tract code --- the six-digit, zero-padded tract portion of a tract identifier, unique only within its county.] [status: `inferred_candidate`]
- **[109] `GEOID`** = `40137000902` --- [provisional: A US Census tract identifier: an 11-character string composed of a 2-character state FIPS code, a 3-character county FIPS code and the 6-character tract code of index 108.] [status: `inferred_candidate`]

**Temperature Maximum – Annual (stem-assumption probe)**

> These three columns reach their meaning through an **unconfirmed** link between the CSV name stem `tempmaxann` and a dictionary section (Q1). The dictionary never states that link, and 101 columns of this file depend on it.

- **[44] `tempmaxann_hist`** = `71.192901610000007` --- [provisional: The ensemble-mean annual average of daily maximum temperature for the modeled historical period --- if, and only if, the CSV stem `tempmaxann` denotes the dictionary section "Temperature Maximum - Annual".] (unit or type: [provisional: degrees Fahrenheit]; scenario: [provisional: Historical --- a modeled baseline, not an observation]; horizon: [provisional: the modeled historical decade, 1995-2004]; season: [provisional: none --- an annual average, not a seasonal one]) [status: `inferred_candidate`]
- **[48] `tempmaxann_rcp85_endc`** = `79.597702029999994` --- [provisional: The ensemble-mean annual average of daily maximum temperature for end-of-century RCP8.5 --- under the same unconfirmed stem-to-section link as IC-018.] (unit or type: [provisional: degrees Fahrenheit]; scenario: [provisional: RCP8.5]; horizon: [provisional: End-Century, the modeled decade 2085-2094]; season: [provisional: none --- an annual average, not a seasonal one]) [status: `inferred_candidate`]
- **[52] `tempmaxann_end85_hist`** = `8.404820440000000` --- [provisional: The change in the ensemble-mean annual average of daily maximum temperature between the modeled historical baseline and end-of-century RCP8.5 --- under the same unconfirmed stem-to-section link as IC-018.] (unit or type: [provisional: degrees Fahrenheit, expressed as a difference]; scenario: [provisional: Historical compared with RCP8.5]; horizon: [provisional: Historical (1995-2004) to End-Century (2085-2094)]; season: [provisional: none --- an annual average, not a seasonal one]) [status: `inferred_candidate`]

Every clause marked [provisional:...] rests on an inferred-candidate record: reasoned and written down, **not verified and not owner-confirmed**. Clauses without that mark are quoted from the tracked data dictionary.

</details>

### Checklist --- Example 1

This is the full list. Examples 2 and 3 use the same 41 columns, so their
checklists ask only what is specific to them.

| # | Please confirm, correct, or say "don't know" | Affects |
| ---: | --- | --- |
| **1** | **One row of this file is one "event".** Is that the right unit for what you meant? If not --- is an event a cell across scenarios, a season, a region, something else? | everything below |
| 2 | `heatindex_*_DayMax` (238, 244, 250) is in **degrees Fahrenheit**, on the *extended* heat index scale of Lu and Romps that the dictionary cites at line 417. The dictionary states no unit for these; I read it across from the verified day-count columns, which threshold "above 95 F". | Q14, 5 columns |
| 3 | `DayMax` is the summer **average** of each day's maximum heat index (about 90 readings), *not* the single highest reading of the summer --- the dictionary's narrative says so at lines 406--407, and the name suggests the opposite. Is that right? | Q14 |
| 4 | `heatindex_C_*_DMax` (256, 262) is that same quantity **differenced**, in the same units. The dictionary calls it only "Change". **Which way round is the subtraction** --- later minus historical, or the reverse? | Q14, 2 columns |
| 5 | `wildfire_summer_Hist/Midc/Endc` (189--191): "Seasonal value" means the **multi-model ensemble mean of the seasonal average daily FWI** described at lines 346--352 --- and *not* the seasonal 95th percentile described further down at line 357. Which is it? | Q13, 3 columns |
| 6 | FWI values are **dimensionless index values** with no physical unit. The dictionary states no unit anywhere. | Q13, 5 columns |
| 7 | `wildfire_summer_Dmid/Dend` (192--193) are **absolute differences** in those index units --- distinguished from the verified `Pmid`/`Pend`, which the dictionary calls "Percent Change". **Which way round is the subtraction?** | Q13, 2 columns |
| 8 | **`tempmaxann` names the dictionary section "Temperature Maximum - Annual".** The dictionary never says that a CSV name's stem denotes a section; I inferred the link. **This is the one that matters most: 101 columns of the file (indices 5--105) stand or fall with it.** | Q1, 101 columns |
| 9 | Granting that link, `tempmaxann_hist`, `_rcp85_endc` and `_end85_hist` (44, 48, 52) are annual averages of daily maximum temperature in **°F**, historical / end-century RCP8.5 / the change between them. | Q1, 3 columns |
| 10 | `GEOID` (109) is a **Census tract identifier**: 2-character state + 3-character county + 6-character tract. **Which Census vintage?** Every join this project could make depends on the answer. | Q10 |
| 11 | `TRACTCE` (108) is the **tract code alone**, unique only within its county. | Q10 |
| 12 | `X` and `Y` (106, 107) are **longitude and latitude in decimal degrees**. **Which coordinate reference system**, and is the point the grid cell's centroid? | Q10 |
| 13 | `NAME` (2) is a **county or county-equivalent name**, and `State`/`State_Abbr` (3, 4) the state it sits in. `State` holds **49 distinct non-empty values plus 7 blank rows** --- so 49 states, not 50. Do you know which one is absent, or whether the set is not the 50 states; and what the 7 blank rows are? | Q10, Q16 |
| 14 | **Are these the kinds of table-side records you expect to connect to the literature?** If the shape is wrong, that matters more than any line above. | the whole approach |

---

## Example 2 --- row `OID_` 14, `Crossmodel` `R107C232`

Row ordinal 13. Selected by **rule R-B**: the first fully-populated row whose
`GEOID` begins with a zero.

Where it is: `NAME` `San Bernardino`, `State` `California`, `GEOID` `06071010300`, `TRACTCE` `010300`.

**Why this row exists in the set.** `GEOID` here is `06071010300` and `TRACTCE`
is `010300` --- both start with a zero. **19,074 rows of this file carry a
leading-zero `GEOID`.** Reading that column as a number instead of as text would
delete the zero and turn `06071010300` into `6071010300`, which is a different
identifier or none at all, and every join built on it would be silently wrong.
This example is here so you can see that the zero survives into what you read.

<details><summary><b>Raw values (41 columns)</b></summary>

| # | Column | Raw value, exactly as stored | Status |
| ---: | --- | --- | --- |
| 1 | `Crossmodel` | `R107C232` | dictionary |
| 2 | `NAME` | `San Bernardino` | **inferred** |
| 3 | `State` | `California` | **inferred** |
| 4 | `State_Abbr` | `CA` | **inferred** |
| 44 | `tempmaxann_hist` | `75.547500610000000` | **inferred** |
| 48 | `tempmaxann_rcp85_endc` | `83.991897580000000` | **inferred** |
| 52 | `tempmaxann_end85_hist` | `8.444319730000000` | **inferred** |
| 106 | `X` | `-114.874260719999995` | **inferred** |
| 107 | `Y` | `34.882867230000002` | **inferred** |
| 108 | `TRACTCE` | `010300` | **inferred** |
| 109 | `GEOID` | `06071010300` | **inferred** |
| 180 | `wildfire_autumn_Pmid` | `-2.885749000000000` | dictionary |
| 181 | `wildfire_autumn_Pend` | `-0.864642000000000` | dictionary |
| 187 | `wildfire_spring_Pmid` | `9.185529000000001` | dictionary |
| 188 | `wildfire_spring_Pend` | `21.720673000000001` | dictionary |
| 189 | `wildfire_summer_Hist` | `52.565601350000001` | **inferred** |
| 190 | `wildfire_summer_Midc` | `56.876499180000003` | **inferred** |
| 191 | `wildfire_summer_Endc` | `58.591499329999998` | **inferred** |
| 192 | `wildfire_summer_Dmid` | `4.310910220000000` | **inferred** |
| 193 | `wildfire_summer_Dend` | `6.025909900000000` | **inferred** |
| 194 | `wildfire_summer_Pmid` | `8.201013000000000` | dictionary |
| 195 | `wildfire_summer_Pend` | `11.463613000000000` | dictionary |
| 201 | `wildfire_winter_Pmid` | `0.111682000000000` | dictionary |
| 202 | `wildfire_winter_Pend` | `29.645517000000002` | dictionary |
| 238 | `heatindex_HIS_DayMax` | `93.136647539999998` | **inferred** |
| 240 | `heatindex_HIS_Day95` | `37.200000760000002` | dictionary |
| 241 | `heatindex_HIS_Day105` | `1.366666700000000` | dictionary |
| 242 | `heatindex_HIS_Day115` | `0.000000000000000` | dictionary |
| 243 | `heatindex_HIS_Day125` | `0.000000000000000` | dictionary |
| 244 | `heatindex_M85_DayMax` | `97.389831540000003` | **inferred** |
| 246 | `heatindex_M85_Day95` | `58.499998730000002` | dictionary |
| 247 | `heatindex_M85_Day105` | `9.133333130000000` | dictionary |
| 248 | `heatindex_M85_Day115` | `1.099999980000000` | dictionary |
| 249 | `heatindex_M85_Day125` | `0.433333320000000` | dictionary |
| 250 | `heatindex_E85_DayMax` | `103.138158160000003` | **inferred** |
| 252 | `heatindex_E85_Day95` | `78.666666669999998` | dictionary |
| 253 | `heatindex_E85_Day105` | `36.733333590000001` | dictionary |
| 254 | `heatindex_E85_Day115` | `2.000000030000000` | dictionary |
| 255 | `heatindex_E85_Day125` | `0.466666660000000` | dictionary |
| 256 | `heatindex_C_M85_DMax` | `4.253184000000000` | **inferred** |
| 262 | `heatindex_C_E85_DMax` | `10.001510619999999` | **inferred** |

</details>

<details><summary><b>Generated description</b></summary>

### Candidate record --- row `OID_` 14, `Crossmodel` `R107C232`

Row ordinal 13 of the file, selected by rule **R-B** --- the first row, in file order, whose `GEOID` begins with `0` and that is non-empty on every selected pilot column. The rule tests whether a leading-zero Census identifier survives into what the mentor reads. Coercing `GEOID` to an integer would delete the zero and silently corrupt every join; 19,074 rows of this file carry one.

**A1.** One CSV row is treated as one "event". That grain is under mentor review and is **not** established as a property of this file.

> `Historical` wherever it appears below means a **modeled historical baseline** --- the dictionary's historical period, 1995 to 2004, run through the same climate models. It is not an observation, a measurement, or a record of anything that happened.

**Heat Index – Summer**

- **[238] `heatindex_HIS_DayMax`** = `93.136647539999998` --- [provisional: The ensemble-mean summer daily maximum heat index for the modeled historical period --- that is, the average over the summer's roughly 90 days of each day's maximum heat index, averaged across the three climate models. Not the single highest reading of the summer; the dictionary gives that a separate field, `heatindex_HIS_SeaMax`.] (unit or type: [provisional: degrees Fahrenheit, on the extended heat index scale of Lu and Romps (2022)]; scenario: Historical --- a modeled baseline, not an observation; horizon: the modeled historical decade, 1995-2004; season: Summer) [status: `inferred_candidate`]
- **[240] `heatindex_HIS_Day95`** = `37.200000760000002` --- Number of Summer days with daily max heat index above 95 F -- Historical (unit or type: Number of; horizon: Historical; season: Summer) [status: `verified_from_dictionary`]
- **[241] `heatindex_HIS_Day105`** = `1.366666700000000` --- Number of Summer days with daily max heat index above 105 F -- Historical (unit or type: Number of; horizon: Historical; season: Summer) [status: `verified_from_dictionary`]
- **[242] `heatindex_HIS_Day115`** = `0.000000000000000` --- Number of Summer days with daily max heat index above 115 F -- Historical (unit or type: Number of; horizon: Historical; season: Summer) [status: `verified_from_dictionary`]
- **[243] `heatindex_HIS_Day125`** = `0.000000000000000` --- Number of Summer days with daily max heat index above 125 F -- Historical (unit or type: Number of; horizon: Historical; season: Summer) [status: `verified_from_dictionary`]
- **[244] `heatindex_M85_DayMax`** = `97.389831540000003` --- [provisional: The same quantity as IC-001 --- the ensemble-mean summer daily maximum heat index --- for the mid-century RCP8.5 projection.] (unit or type: [provisional: degrees Fahrenheit, on the extended heat index scale of Lu and Romps (2022)]; scenario: RCP8.5; horizon: Mid-Century, the modeled decade 2045-2054; season: Summer) [status: `inferred_candidate`]
- **[246] `heatindex_M85_Day95`** = `58.499998730000002` --- Number of Summer days with daily max heat index above 95 F -- Mid-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[247] `heatindex_M85_Day105`** = `9.133333130000000` --- Number of Summer days with daily max heat index above 105 F -- Mid-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[248] `heatindex_M85_Day115`** = `1.099999980000000` --- Number of Summer days with daily max heat index above 115 F -- Mid-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[249] `heatindex_M85_Day125`** = `0.433333320000000` --- Number of Summer days with daily max heat index above 125 F -- Mid-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[250] `heatindex_E85_DayMax`** = `103.138158160000003` --- [provisional: The same quantity as IC-001 --- the ensemble-mean summer daily maximum heat index --- for the end-of-century RCP8.5 projection.] (unit or type: [provisional: degrees Fahrenheit, on the extended heat index scale of Lu and Romps (2022)]; scenario: RCP8.5; horizon: End-Century, the modeled decade 2085-2094; season: Summer) [status: `inferred_candidate`]
- **[252] `heatindex_E85_Day95`** = `78.666666669999998` --- Number of Summer days with daily max heat index above 95 F -- End-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[253] `heatindex_E85_Day105`** = `36.733333590000001` --- Number of Summer days with daily max heat index above 105 F -- End-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[254] `heatindex_E85_Day115`** = `2.000000030000000` --- Number of Summer days with daily max heat index above 115 F -- End-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[255] `heatindex_E85_Day125`** = `0.466666660000000` --- Number of Summer days with daily max heat index above 125 F -- End-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[256] `heatindex_C_M85_DMax`** = `4.253184000000000` --- [provisional: The change in the ensemble-mean summer daily maximum heat index between the modeled historical baseline and mid-century RCP8.5 --- that is, between the quantities in index 238 and index 244.] (unit or type: [provisional: degrees Fahrenheit on the same extended heat index scale as indices 238 and 244, expressed as a difference]; scenario: Historical compared with RCP8.5; horizon: Historical (1995-2004) to Mid-Century (2045-2054); season: Summer) [status: `inferred_candidate`]
- **[262] `heatindex_C_E85_DMax`** = `10.001510619999999` --- [provisional: The change in the ensemble-mean summer daily maximum heat index between the modeled historical baseline and end-of-century RCP8.5 --- that is, between the quantities in index 238 and index 250.] (unit or type: [provisional: degrees Fahrenheit on the same extended heat index scale as indices 238 and 250, expressed as a difference]; scenario: Historical compared with RCP8.5; horizon: Historical (1995-2004) to End-Century (2085-2094); season: Summer) [status: `inferred_candidate`]

**Fire Weather Index - Averages**

> Every `wildfire_*` column below holds a **Fire Weather Index** --- a meteorological fire-danger index, listed in the dictionary under the section "Fire Weather Index - Averages". It is not a wildfire, an ignition, a burned area, or a probability of any of those, and nothing in this record says that it is.

- **[180] `wildfire_autumn_Pmid`** = `-2.885749000000000` --- Percent Change between Mid-Century and Historical (unit or type: Percent Change; horizon: Historical, Mid-Century; season: Autumn) [status: `verified_from_dictionary`]
- **[181] `wildfire_autumn_Pend`** = `-0.864642000000000` --- Percent Change between End-Century and Historical (unit or type: Percent Change; horizon: Historical, End-Century; season: Autumn) [status: `verified_from_dictionary`]
- **[187] `wildfire_spring_Pmid`** = `9.185529000000001` --- Percent Change between Mid-Century and Historical (unit or type: Percent Change; horizon: Historical, Mid-Century; season: Spring) [status: `verified_from_dictionary`]
- **[188] `wildfire_spring_Pend`** = `21.720673000000001` --- Percent Change between End-Century and Historical (unit or type: Percent Change; horizon: Historical, End-Century; season: Spring) [status: `verified_from_dictionary`]
- **[189] `wildfire_summer_Hist`** = `52.565601350000001` --- [provisional: The multi-model ensemble mean of the summer seasonal average daily Fire Weather Index for the modeled historical period. The FWI is a meteorological fire-danger index: it describes weather conditions, not fire occurrence, ignition, or burned area.] (unit or type: [provisional: dimensionless index value]; scenario: Historical --- a modeled baseline, not an observation; horizon: the modeled historical decade, 1995-2004; season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[190] `wildfire_summer_Midc`** = `56.876499180000003` --- [provisional: The same Fire Weather Index quantity as IC-006 --- the ensemble-mean summer seasonal average daily FWI --- for the mid-century RCP8.5 projection.] (unit or type: [provisional: dimensionless index value]; scenario: RCP8.5; horizon: Mid-Century, the modeled decade 2045-2054; season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[191] `wildfire_summer_Endc`** = `58.591499329999998` --- [provisional: The same Fire Weather Index quantity as IC-006 --- the ensemble-mean summer seasonal average daily FWI --- for the end-of-century RCP8.5 projection.] (unit or type: [provisional: dimensionless index value]; scenario: RCP8.5; horizon: End-Century, the modeled decade 2085-2094; season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[192] `wildfire_summer_Dmid`** = `4.310910220000000` --- [provisional: The difference between the mid-century RCP8.5 and modeled historical summer Fire Weather Index values --- that is, between index 190 and index 189.] (unit or type: [provisional: dimensionless index value, expressed as a difference]; scenario: Historical compared with RCP8.5; horizon: Historical (1995-2004) to Mid-Century (2045-2054); season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[193] `wildfire_summer_Dend`** = `6.025909900000000` --- [provisional: The difference between the end-of-century RCP8.5 and modeled historical summer Fire Weather Index values --- that is, between index 191 and index 189.] (unit or type: [provisional: dimensionless index value, expressed as a difference]; scenario: Historical compared with RCP8.5; horizon: Historical (1995-2004) to End-Century (2085-2094); season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[194] `wildfire_summer_Pmid`** = `8.201013000000000` --- Percent Change between Mid-Century and Historical (unit or type: Percent Change; horizon: Historical, Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[195] `wildfire_summer_Pend`** = `11.463613000000000` --- Percent Change between End-Century and Historical (unit or type: Percent Change; horizon: Historical, End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[201] `wildfire_winter_Pmid`** = `0.111682000000000` --- Percent Change between Mid-Century and Historical (unit or type: Percent Change; horizon: Historical, Mid-Century; season: Winter) [status: `verified_from_dictionary`]
- **[202] `wildfire_winter_Pend`** = `29.645517000000002` --- Percent Change between End-Century and Historical (unit or type: Percent Change; horizon: Historical, End-Century; season: Winter) [status: `verified_from_dictionary`]

**Location anchor**

> The Census vintage and the coordinate reference system of these columns are **unknown**. They locate this one row; no part of this pilot groups rows by any of them.

- **[1] `Crossmodel`** = `R107C232` --- Truncated name for "Crossmodel_CellName". Text ID for each cell in the polygon grid. (unit or type: Text ID) [status: `verified_from_dictionary`]
- **[2] `NAME`** = `San Bernardino` --- [provisional: A county or county-equivalent name for the area the row's grid cell falls in, joined in from a Census or similar source.] [status: `inferred_candidate`]
- **[3] `State`** = `California` --- [provisional: The full name of the US state or state-equivalent the row's grid cell falls in, joined in from the same source as index 2.] [status: `inferred_candidate`]
- **[4] `State_Abbr`** = `CA` --- [provisional: The two-letter postal abbreviation of the state named in index 3.] [status: `inferred_candidate`]
- **[106] `X`** = `-114.874260719999995` --- [provisional: A longitude coordinate, in decimal degrees, for the row's grid cell.] (unit or type: [provisional: decimal degrees of longitude, in an unknown coordinate reference system]) [status: `inferred_candidate`]
- **[107] `Y`** = `34.882867230000002` --- [provisional: A latitude coordinate, in decimal degrees, for the row's grid cell.] (unit or type: [provisional: decimal degrees of latitude, in an unknown coordinate reference system]) [status: `inferred_candidate`]
- **[108] `TRACTCE`** = `010300` --- [provisional: A US Census tract code --- the six-digit, zero-padded tract portion of a tract identifier, unique only within its county.] [status: `inferred_candidate`]
- **[109] `GEOID`** = `06071010300` --- [provisional: A US Census tract identifier: an 11-character string composed of a 2-character state FIPS code, a 3-character county FIPS code and the 6-character tract code of index 108.] [status: `inferred_candidate`]

**Temperature Maximum – Annual (stem-assumption probe)**

> These three columns reach their meaning through an **unconfirmed** link between the CSV name stem `tempmaxann` and a dictionary section (Q1). The dictionary never states that link, and 101 columns of this file depend on it.

- **[44] `tempmaxann_hist`** = `75.547500610000000` --- [provisional: The ensemble-mean annual average of daily maximum temperature for the modeled historical period --- if, and only if, the CSV stem `tempmaxann` denotes the dictionary section "Temperature Maximum - Annual".] (unit or type: [provisional: degrees Fahrenheit]; scenario: [provisional: Historical --- a modeled baseline, not an observation]; horizon: [provisional: the modeled historical decade, 1995-2004]; season: [provisional: none --- an annual average, not a seasonal one]) [status: `inferred_candidate`]
- **[48] `tempmaxann_rcp85_endc`** = `83.991897580000000` --- [provisional: The ensemble-mean annual average of daily maximum temperature for end-of-century RCP8.5 --- under the same unconfirmed stem-to-section link as IC-018.] (unit or type: [provisional: degrees Fahrenheit]; scenario: [provisional: RCP8.5]; horizon: [provisional: End-Century, the modeled decade 2085-2094]; season: [provisional: none --- an annual average, not a seasonal one]) [status: `inferred_candidate`]
- **[52] `tempmaxann_end85_hist`** = `8.444319730000000` --- [provisional: The change in the ensemble-mean annual average of daily maximum temperature between the modeled historical baseline and end-of-century RCP8.5 --- under the same unconfirmed stem-to-section link as IC-018.] (unit or type: [provisional: degrees Fahrenheit, expressed as a difference]; scenario: [provisional: Historical compared with RCP8.5]; horizon: [provisional: Historical (1995-2004) to End-Century (2085-2094)]; season: [provisional: none --- an annual average, not a seasonal one]) [status: `inferred_candidate`]

Every clause marked [provisional:...] rests on an inferred-candidate record: reasoned and written down, **not verified and not owner-confirmed**. Clauses without that mark are quoted from the tracked data dictionary.

</details>

### Checklist --- Example 2

| # | Please confirm, correct, or say "don't know" | Affects |
| ---: | --- | --- |
| **1** | **One row of this file is one "event".** Same question as Example 1, line 1. | everything |
| 2 | The identifiers above are **text, with their leading zeros intact**. Is that how they should be carried, and is there any consumer of this data that expects them as numbers? | Q10 |
| 3 | Lines 2--13 of Example 1's checklist apply to this row unchanged --- the same 41 columns, the same readings. Please answer them there rather than twice. | — |

---

## Example 3 --- row `OID_` 148, `Crossmodel` `R105C198`

Row ordinal 147. Selected by **rule R-C**: the first row that is **empty** in at
least one of the 41 columns.

Where it is: `NAME` `Ventura`, `State` `California`, `GEOID` `06111990100`, `TRACTCE` `990100`.

**Why this row exists in the set.** All **17** heat-index columns are empty on
this row, while the fire-weather, location and temperature columns are
populated. The generated description writes each of them as
**"no value in this file"** --- never `0`, never "missing", never "N/A". A zero
would be a claim that no summer day passed 95 °F here; "missing" would be a
claim that something ought to be there. The file supports neither.

<details><summary><b>Raw values (41 columns)</b></summary>

| # | Column | Raw value, exactly as stored | Status |
| ---: | --- | --- | --- |
| 1 | `Crossmodel` | `R105C198` | dictionary |
| 2 | `NAME` | `Ventura` | **inferred** |
| 3 | `State` | `California` | **inferred** |
| 4 | `State_Abbr` | `CA` | **inferred** |
| 44 | `tempmaxann_hist` | `64.439201350000005` | **inferred** |
| 48 | `tempmaxann_rcp85_endc` | `70.121200560000005` | **inferred** |
| 52 | `tempmaxann_end85_hist` | `5.682020190000000` | **inferred** |
| 106 | `X` | `-119.285083569999998` | **inferred** |
| 107 | `Y` | `34.253087080000000` | **inferred** |
| 108 | `TRACTCE` | `990100` | **inferred** |
| 109 | `GEOID` | `06111990100` | **inferred** |
| 180 | `wildfire_autumn_Pmid` | `0.601562000000000` | dictionary |
| 181 | `wildfire_autumn_Pend` | `0.665466000000000` | dictionary |
| 187 | `wildfire_spring_Pmid` | `22.998621000000000` | dictionary |
| 188 | `wildfire_spring_Pend` | `24.993120000000001` | dictionary |
| 189 | `wildfire_summer_Hist` | `8.258279800000000` | **inferred** |
| 190 | `wildfire_summer_Midc` | `9.659990310000000` | **inferred** |
| 191 | `wildfire_summer_Endc` | `9.762570380000000` | **inferred** |
| 192 | `wildfire_summer_Dmid` | `1.401700020000000` | **inferred** |
| 193 | `wildfire_summer_Dend` | `1.504279970000000` | **inferred** |
| 194 | `wildfire_summer_Pmid` | `16.973309000000000` | dictionary |
| 195 | `wildfire_summer_Pend` | `18.215430999999999` | dictionary |
| 201 | `wildfire_winter_Pmid` | `-10.704121000000001` | dictionary |
| 202 | `wildfire_winter_Pend` | `39.904465000000002` | dictionary |
| 238 | `heatindex_HIS_DayMax` | *(no value in this file)* | **inferred** |
| 240 | `heatindex_HIS_Day95` | *(no value in this file)* | dictionary |
| 241 | `heatindex_HIS_Day105` | *(no value in this file)* | dictionary |
| 242 | `heatindex_HIS_Day115` | *(no value in this file)* | dictionary |
| 243 | `heatindex_HIS_Day125` | *(no value in this file)* | dictionary |
| 244 | `heatindex_M85_DayMax` | *(no value in this file)* | **inferred** |
| 246 | `heatindex_M85_Day95` | *(no value in this file)* | dictionary |
| 247 | `heatindex_M85_Day105` | *(no value in this file)* | dictionary |
| 248 | `heatindex_M85_Day115` | *(no value in this file)* | dictionary |
| 249 | `heatindex_M85_Day125` | *(no value in this file)* | dictionary |
| 250 | `heatindex_E85_DayMax` | *(no value in this file)* | **inferred** |
| 252 | `heatindex_E85_Day95` | *(no value in this file)* | dictionary |
| 253 | `heatindex_E85_Day105` | *(no value in this file)* | dictionary |
| 254 | `heatindex_E85_Day115` | *(no value in this file)* | dictionary |
| 255 | `heatindex_E85_Day125` | *(no value in this file)* | dictionary |
| 256 | `heatindex_C_M85_DMax` | *(no value in this file)* | **inferred** |
| 262 | `heatindex_C_E85_DMax` | *(no value in this file)* | **inferred** |

</details>

<details><summary><b>Generated description</b></summary>

### Candidate record --- row `OID_` 148, `Crossmodel` `R105C198`

Row ordinal 147 of the file, selected by rule **R-C** --- the first row, in file order, that is empty on at least one selected pilot column. The rule tests how a blank is presented --- as "no value in this file", never as a zero and never as a claim that something is missing.

**A1.** One CSV row is treated as one "event". That grain is under mentor review and is **not** established as a property of this file.

> `Historical` wherever it appears below means a **modeled historical baseline** --- the dictionary's historical period, 1995 to 2004, run through the same climate models. It is not an observation, a measurement, or a record of anything that happened.

> An empty cell is written "no value in this file". It is **not** a zero and this record does not claim it means anything else; what the empty rows of this file are is an open question (Q16).

**Heat Index – Summer**

- **[238] `heatindex_HIS_DayMax`** = no value in this file --- [provisional: The ensemble-mean summer daily maximum heat index for the modeled historical period --- that is, the average over the summer's roughly 90 days of each day's maximum heat index, averaged across the three climate models. Not the single highest reading of the summer; the dictionary gives that a separate field, `heatindex_HIS_SeaMax`.] (unit or type: [provisional: degrees Fahrenheit, on the extended heat index scale of Lu and Romps (2022)]; scenario: Historical --- a modeled baseline, not an observation; horizon: the modeled historical decade, 1995-2004; season: Summer) [status: `inferred_candidate`]
- **[240] `heatindex_HIS_Day95`** = no value in this file --- Number of Summer days with daily max heat index above 95 F -- Historical (unit or type: Number of; horizon: Historical; season: Summer) [status: `verified_from_dictionary`]
- **[241] `heatindex_HIS_Day105`** = no value in this file --- Number of Summer days with daily max heat index above 105 F -- Historical (unit or type: Number of; horizon: Historical; season: Summer) [status: `verified_from_dictionary`]
- **[242] `heatindex_HIS_Day115`** = no value in this file --- Number of Summer days with daily max heat index above 115 F -- Historical (unit or type: Number of; horizon: Historical; season: Summer) [status: `verified_from_dictionary`]
- **[243] `heatindex_HIS_Day125`** = no value in this file --- Number of Summer days with daily max heat index above 125 F -- Historical (unit or type: Number of; horizon: Historical; season: Summer) [status: `verified_from_dictionary`]
- **[244] `heatindex_M85_DayMax`** = no value in this file --- [provisional: The same quantity as IC-001 --- the ensemble-mean summer daily maximum heat index --- for the mid-century RCP8.5 projection.] (unit or type: [provisional: degrees Fahrenheit, on the extended heat index scale of Lu and Romps (2022)]; scenario: RCP8.5; horizon: Mid-Century, the modeled decade 2045-2054; season: Summer) [status: `inferred_candidate`]
- **[246] `heatindex_M85_Day95`** = no value in this file --- Number of Summer days with daily max heat index above 95 F -- Mid-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[247] `heatindex_M85_Day105`** = no value in this file --- Number of Summer days with daily max heat index above 105 F -- Mid-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[248] `heatindex_M85_Day115`** = no value in this file --- Number of Summer days with daily max heat index above 115 F -- Mid-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[249] `heatindex_M85_Day125`** = no value in this file --- Number of Summer days with daily max heat index above 125 F -- Mid-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[250] `heatindex_E85_DayMax`** = no value in this file --- [provisional: The same quantity as IC-001 --- the ensemble-mean summer daily maximum heat index --- for the end-of-century RCP8.5 projection.] (unit or type: [provisional: degrees Fahrenheit, on the extended heat index scale of Lu and Romps (2022)]; scenario: RCP8.5; horizon: End-Century, the modeled decade 2085-2094; season: Summer) [status: `inferred_candidate`]
- **[252] `heatindex_E85_Day95`** = no value in this file --- Number of Summer days with daily max heat index above 95 F -- End-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[253] `heatindex_E85_Day105`** = no value in this file --- Number of Summer days with daily max heat index above 105 F -- End-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[254] `heatindex_E85_Day115`** = no value in this file --- Number of Summer days with daily max heat index above 115 F -- End-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[255] `heatindex_E85_Day125`** = no value in this file --- Number of Summer days with daily max heat index above 125 F -- End-Century RCP8.5 (unit or type: Number of; scenario: RCP8.5; horizon: End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[256] `heatindex_C_M85_DMax`** = no value in this file --- [provisional: The change in the ensemble-mean summer daily maximum heat index between the modeled historical baseline and mid-century RCP8.5 --- that is, between the quantities in index 238 and index 244.] (unit or type: [provisional: degrees Fahrenheit on the same extended heat index scale as indices 238 and 244, expressed as a difference]; scenario: Historical compared with RCP8.5; horizon: Historical (1995-2004) to Mid-Century (2045-2054); season: Summer) [status: `inferred_candidate`]
- **[262] `heatindex_C_E85_DMax`** = no value in this file --- [provisional: The change in the ensemble-mean summer daily maximum heat index between the modeled historical baseline and end-of-century RCP8.5 --- that is, between the quantities in index 238 and index 250.] (unit or type: [provisional: degrees Fahrenheit on the same extended heat index scale as indices 238 and 250, expressed as a difference]; scenario: Historical compared with RCP8.5; horizon: Historical (1995-2004) to End-Century (2085-2094); season: Summer) [status: `inferred_candidate`]

**Fire Weather Index - Averages**

> Every `wildfire_*` column below holds a **Fire Weather Index** --- a meteorological fire-danger index, listed in the dictionary under the section "Fire Weather Index - Averages". It is not a wildfire, an ignition, a burned area, or a probability of any of those, and nothing in this record says that it is.

- **[180] `wildfire_autumn_Pmid`** = `0.601562000000000` --- Percent Change between Mid-Century and Historical (unit or type: Percent Change; horizon: Historical, Mid-Century; season: Autumn) [status: `verified_from_dictionary`]
- **[181] `wildfire_autumn_Pend`** = `0.665466000000000` --- Percent Change between End-Century and Historical (unit or type: Percent Change; horizon: Historical, End-Century; season: Autumn) [status: `verified_from_dictionary`]
- **[187] `wildfire_spring_Pmid`** = `22.998621000000000` --- Percent Change between Mid-Century and Historical (unit or type: Percent Change; horizon: Historical, Mid-Century; season: Spring) [status: `verified_from_dictionary`]
- **[188] `wildfire_spring_Pend`** = `24.993120000000001` --- Percent Change between End-Century and Historical (unit or type: Percent Change; horizon: Historical, End-Century; season: Spring) [status: `verified_from_dictionary`]
- **[189] `wildfire_summer_Hist`** = `8.258279800000000` --- [provisional: The multi-model ensemble mean of the summer seasonal average daily Fire Weather Index for the modeled historical period. The FWI is a meteorological fire-danger index: it describes weather conditions, not fire occurrence, ignition, or burned area.] (unit or type: [provisional: dimensionless index value]; scenario: Historical --- a modeled baseline, not an observation; horizon: the modeled historical decade, 1995-2004; season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[190] `wildfire_summer_Midc`** = `9.659990310000000` --- [provisional: The same Fire Weather Index quantity as IC-006 --- the ensemble-mean summer seasonal average daily FWI --- for the mid-century RCP8.5 projection.] (unit or type: [provisional: dimensionless index value]; scenario: RCP8.5; horizon: Mid-Century, the modeled decade 2045-2054; season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[191] `wildfire_summer_Endc`** = `9.762570380000000` --- [provisional: The same Fire Weather Index quantity as IC-006 --- the ensemble-mean summer seasonal average daily FWI --- for the end-of-century RCP8.5 projection.] (unit or type: [provisional: dimensionless index value]; scenario: RCP8.5; horizon: End-Century, the modeled decade 2085-2094; season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[192] `wildfire_summer_Dmid`** = `1.401700020000000` --- [provisional: The difference between the mid-century RCP8.5 and modeled historical summer Fire Weather Index values --- that is, between index 190 and index 189.] (unit or type: [provisional: dimensionless index value, expressed as a difference]; scenario: Historical compared with RCP8.5; horizon: Historical (1995-2004) to Mid-Century (2045-2054); season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[193] `wildfire_summer_Dend`** = `1.504279970000000` --- [provisional: The difference between the end-of-century RCP8.5 and modeled historical summer Fire Weather Index values --- that is, between index 191 and index 189.] (unit or type: [provisional: dimensionless index value, expressed as a difference]; scenario: Historical compared with RCP8.5; horizon: Historical (1995-2004) to End-Century (2085-2094); season: summer, defined by the dictionary as June, July and August) [status: `inferred_candidate`]
- **[194] `wildfire_summer_Pmid`** = `16.973309000000000` --- Percent Change between Mid-Century and Historical (unit or type: Percent Change; horizon: Historical, Mid-Century; season: Summer) [status: `verified_from_dictionary`]
- **[195] `wildfire_summer_Pend`** = `18.215430999999999` --- Percent Change between End-Century and Historical (unit or type: Percent Change; horizon: Historical, End-Century; season: Summer) [status: `verified_from_dictionary`]
- **[201] `wildfire_winter_Pmid`** = `-10.704121000000001` --- Percent Change between Mid-Century and Historical (unit or type: Percent Change; horizon: Historical, Mid-Century; season: Winter) [status: `verified_from_dictionary`]
- **[202] `wildfire_winter_Pend`** = `39.904465000000002` --- Percent Change between End-Century and Historical (unit or type: Percent Change; horizon: Historical, End-Century; season: Winter) [status: `verified_from_dictionary`]

**Location anchor**

> The Census vintage and the coordinate reference system of these columns are **unknown**. They locate this one row; no part of this pilot groups rows by any of them.

- **[1] `Crossmodel`** = `R105C198` --- Truncated name for "Crossmodel_CellName". Text ID for each cell in the polygon grid. (unit or type: Text ID) [status: `verified_from_dictionary`]
- **[2] `NAME`** = `Ventura` --- [provisional: A county or county-equivalent name for the area the row's grid cell falls in, joined in from a Census or similar source.] [status: `inferred_candidate`]
- **[3] `State`** = `California` --- [provisional: The full name of the US state or state-equivalent the row's grid cell falls in, joined in from the same source as index 2.] [status: `inferred_candidate`]
- **[4] `State_Abbr`** = `CA` --- [provisional: The two-letter postal abbreviation of the state named in index 3.] [status: `inferred_candidate`]
- **[106] `X`** = `-119.285083569999998` --- [provisional: A longitude coordinate, in decimal degrees, for the row's grid cell.] (unit or type: [provisional: decimal degrees of longitude, in an unknown coordinate reference system]) [status: `inferred_candidate`]
- **[107] `Y`** = `34.253087080000000` --- [provisional: A latitude coordinate, in decimal degrees, for the row's grid cell.] (unit or type: [provisional: decimal degrees of latitude, in an unknown coordinate reference system]) [status: `inferred_candidate`]
- **[108] `TRACTCE`** = `990100` --- [provisional: A US Census tract code --- the six-digit, zero-padded tract portion of a tract identifier, unique only within its county.] [status: `inferred_candidate`]
- **[109] `GEOID`** = `06111990100` --- [provisional: A US Census tract identifier: an 11-character string composed of a 2-character state FIPS code, a 3-character county FIPS code and the 6-character tract code of index 108.] [status: `inferred_candidate`]

**Temperature Maximum – Annual (stem-assumption probe)**

> These three columns reach their meaning through an **unconfirmed** link between the CSV name stem `tempmaxann` and a dictionary section (Q1). The dictionary never states that link, and 101 columns of this file depend on it.

- **[44] `tempmaxann_hist`** = `64.439201350000005` --- [provisional: The ensemble-mean annual average of daily maximum temperature for the modeled historical period --- if, and only if, the CSV stem `tempmaxann` denotes the dictionary section "Temperature Maximum - Annual".] (unit or type: [provisional: degrees Fahrenheit]; scenario: [provisional: Historical --- a modeled baseline, not an observation]; horizon: [provisional: the modeled historical decade, 1995-2004]; season: [provisional: none --- an annual average, not a seasonal one]) [status: `inferred_candidate`]
- **[48] `tempmaxann_rcp85_endc`** = `70.121200560000005` --- [provisional: The ensemble-mean annual average of daily maximum temperature for end-of-century RCP8.5 --- under the same unconfirmed stem-to-section link as IC-018.] (unit or type: [provisional: degrees Fahrenheit]; scenario: [provisional: RCP8.5]; horizon: [provisional: End-Century, the modeled decade 2085-2094]; season: [provisional: none --- an annual average, not a seasonal one]) [status: `inferred_candidate`]
- **[52] `tempmaxann_end85_hist`** = `5.682020190000000` --- [provisional: The change in the ensemble-mean annual average of daily maximum temperature between the modeled historical baseline and end-of-century RCP8.5 --- under the same unconfirmed stem-to-section link as IC-018.] (unit or type: [provisional: degrees Fahrenheit, expressed as a difference]; scenario: [provisional: Historical compared with RCP8.5]; horizon: [provisional: Historical (1995-2004) to End-Century (2085-2094)]; season: [provisional: none --- an annual average, not a seasonal one]) [status: `inferred_candidate`]

Every clause marked [provisional:...] rests on an inferred-candidate record: reasoned and written down, **not verified and not owner-confirmed**. Clauses without that mark are quoted from the tracked data dictionary.

</details>

### Checklist --- Example 3

| # | Please confirm, correct, or say "don't know" | Affects |
| ---: | --- | --- |
| **1** | **One row of this file is one "event".** Same question as Example 1, line 1. | everything |
| 2 | Is **"no value in this file"** the right way to present an empty cell, or does an empty heat-index cell mean something specific --- a cell outside the layer's coverage, a computation that did not run, something else? | Q16, Q17 |
| 3 | **83 rows of the file are empty across every column from index 235 on**, which is this group. Do you know what those 83 rows are? | Q16 |
| 4 | Lines 2--13 of Example 1's checklist apply to this row unchanged. Please answer them there rather than twice. | — |

---

## The four questions behind all of this

Quoted verbatim from the GUIDANCE ruling of 2026-09-13
([`M1_D010_GUIDANCE_RULING.md`](M1_D010_GUIDANCE_RULING.md), "Mentor"), which
asks that the next mentor interaction be answered **through the examples**
rather than by re-presenting Q1--Q18 in the abstract:

> 1. **Is one CSV row the correct unit for what she means by an “event”?**
> 2. **Are the selected field interpretations correct?**
> 3. **Which assumptions in each example does she endorse or reject?**
> 4. **Are these the kinds of table-side records she expects to connect to literature?**

---

### A note on what your answers will and will not do

Whatever you confirm gets written down as a record naming **exactly those
columns and exactly what was confirmed** --- nothing wider. A general "yes, this
is the kind of thing I want" is genuinely useful to hear, and it will be
recorded as approval of the *approach*; it will not be taken as confirming any
of the field readings above. Those move one line at a time.

Anything you correct, or answer "don't know" to, stays marked as unconfirmed and
the columns it touches stay out of scientific use.

---

- The records themselves: [`../artifacts/examples/`](../artifacts/examples/)
- Per-column reasoning and unresolved alternatives: [`../data/metadata/inferred_candidates.yaml`](../data/metadata/inferred_candidates.yaml)
- Why these 41 columns and not others: [`PILOT_SUBSET.md`](PILOT_SUBSET.md)
- The full question inventory, for background only: [`METADATA_QUESTIONS.md`](METADATA_QUESTIONS.md)
