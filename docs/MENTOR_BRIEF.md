# Mentor brief — ClimRR cross-modal benchmark

Last updated: 2026-10-20   Next meeting: **Thursday 2026-10-22** --- bring the items under *For Thursday* below; the answer sheet is still outstanding

## Status in five lines

1. **The table is pinned and partly interpreted**: 62,834 rows, 275 columns, read as text; 41 columns interpreted (21 stated by the dictionary, 20 reasoned and marked so). Nothing reasoned is confirmed --- **the answer sheet has still not been reviewed**, so all 20 stay `inferred_candidate`; the project proceeds on "our reading" (D-014), which promotes nothing.
2. **The first literature corpus gave no link.** 1,918 papers collected for another purpose; ten read at random and four found by a strict concept + place search, each read twice: **0 of 78 statement-unit pairs qualify as a candidate link** ([MENTOR_REPORT_2026-10-09.md](MENTOR_REPORT_2026-10-09.md)).
3. **Your direction of 2026-10-09 is now the method:** concepts from the table units first, then papers for those concepts. The same two fixed searches (Fire Weather Index, heat index) gave **2 and 10** papers on one S2ORC shard (fire weather after the FWI rule below) and **448 and 861** on the 186,346-file climate set JL shared after 2026-10-13. A bare "FWI" counts only when the same paper also says "fire weather". GUIDANCE accepted this as the working corpus (D-025) --- for finding candidates, not as a sample of the literature.
4. **100 fire-weather and 143 heat-index papers mention Oklahoma, Stephens or California somewhere.** That is a word match only --- the word may be a study area, an affiliation or a surname. **20 of them (10 + 10), picked by a fixed rank rule that never looks at content, were read by two readers independently and reconciled.** On the first reader's classification, the place word was the paper's own study area in 8 of the 20; in the others it was context, an affiliation (2) or a surname (1).
5. **Result: 118 reconciled statements, 0 of 354 statement-unit pairs qualify as a candidate link.** 12 pairs share the concept family (fire weather index or heat index) but not the place; the 2 that name exactly "California" are not about either index. Next, separately: a survey of which other dictionary concepts have literature coverage, diagnostics only. **No questions are generated** until a link exists.

## What I need from this meeting

> ### **For Thursday 2026-10-22**
>
> 1. **Same concepts, same queries, new source.** Fire weather **2 → 448**
>    papers, heat index **10 → 861** (shard → climate set). 100 and 143 of them
>    mention one of our three places --- word matches, not yet read.
> 2. **The 20-paper double reading is done** (10 fire weather + 10 heat
>    index, chosen by a fixed rule before anyone opened them). Two readers
>    agreed on scope 20/20.
>    - **Statements after reconciliation: 118** --- 3 found identically by
>      both readers, 47 found by both and reconciled, 68 found by one reader
>      only.
>    - **Candidate links: 0 of 354** --- 12 "same concept family, place
>      unknown or different", 57 ruled out (mostly a past period against the
>      units' future window), 285 undecidable; no statement names an
>      emissions scenario.
> 3. **The dictionary-wide concept survey runs on Polaris as diagnostics**: for
>    each concept the dictionary describes, how much literature mentions it.
>    It ranks nothing into the benchmark by itself.
>
> **Question for you:** *if coverage turned out comparable, which dictionary
> concepts would you prioritize for new units?*
>
> **Still open from 2026-10-19:** in general scientific text "FWI" often means
> something else (full waveform inversion, Forest Watch Indonesia, fatal work
> injuries); we count a bare "FWI" only when the same paper also says "fire
> weather" or a longer fire-weather phrase. **Is that the right rule for the
> fire-weather literature you have in mind?**

> ### **First question for the next one-on-one**
>
> **"Does the intended bridge require literature to match the exact ClimRR metric/scenario, or is support at the broader hazard/concept level sufficient when unmatched dimensions are explicitly disclosed?"**
>
> **Why it matters:** it decides whether a paper about heat-index trends can support a record built on *days above 105°F* — the same hazard family, but not the same measure, and usually without the record's emissions scenario.
>
> **What it unblocks:** the final set of relation categories for connecting a paper to a table record, and the design of the questions the benchmark will eventually ask.

*Unchanged since 2026-09-13 and still outstanding: the sheet was brought to the one-on-ones of 2026-09-17 and 2026-09-24 and not reviewed at either (R-003).*

> ### **Please review the three example records in [`MENTOR_EXAMPLES.md`](MENTOR_EXAMPLES.md).**
>
> That is the whole ask. Each has a short numbered checklist; each line is a
> reading I could not confirm from the dictionary and had to reason out.
> **Confirm / correct / "don't know"** on each line — ten minutes is enough, and
> "don't know" is a genuinely useful answer.
>
> Four lines matter more than the rest:
>
> 1. **Is one row of the CSV one "event"?** Everything rests on this, and it is
>    my reading of what you said on 2026-09-10 rather than your words.
> 2. **Does the name stem `tempmaxann` denote the dictionary section
>    "Temperature Maximum - Annual"?** 101 columns stand or fall with that one
>    link, and the dictionary never states it.
> 3. **Which Census vintage are `GEOID` and `TRACTCE` from?** It decides every
>    join this project could make.
> 4. **Are these the kinds of table-side records you expect to connect to the
>    literature?** If the shape is wrong, that matters more than any field.

Whatever you confirm is recorded as naming **exactly those columns and exactly
what was confirmed**. A general "yes, this is the kind of thing I want" will be
recorded as approval of the approach and will not be taken as confirming any
field reading.

## Background: the full question inventory

**Demoted below the examples on purpose.** Q0 was answered on 2026-09-10 and is
closed; Q1–Q18 were put and not answered per column, and the ruling of
2026-09-13 asks that the next conversation go **through the examples** rather
than re-presenting these in the abstract. The table is kept because several
checklist lines in `MENTOR_EXAMPLES.md` are these questions made concrete — the
"Affects" column there names the Q-number — and because the ones no example
touches are still open.

## Questions for this meeting (priority order)

**Q0 was answered on 2026-09-10 and is closed; Q1–Q18 were put but not answered,
and stand unchanged for a future meeting.** They are kept here rather than
deleted: if the proposed way of working (D-010) is approved, the examples we
bring will make several of them concrete enough to answer in passing.

| # | Q-ID | Question (one sentence) | Why we need it | What it unblocks |
| --- | --- | --- | --- | --- |
| 1 | Q0 | **ANSWERED 2026-09-10 — no.** Is there any other authoritative material about this file we should have** — (a) a newer or more complete data dictionary than our 19-page PDF, (b) a document, script or ArcGIS project describing how `FullData.csv` was assembled from the ClimRR layers and the Census and socioeconomic sources, (c) a ClimRR web page or release note naming the data version and export date? | One such document could answer many of the questions below at once, and it is the kind of evidence we are allowed to treat as authoritative — an answer in conversation settles one question, a specification settles a family of them. | Potentially most of Q1–Q18. |
| 2 | Q1 | The column names start with prefixes — `tempmaxann`, `tempmin_seas`, `precipann`, `noprecip`, `windspeed`, `hdd`, `cdd` — so **which ClimRR variable does each prefix come from**? | The PDF describes each variable in its own table and names fields only by their ending (`hist`, `rcp45_midc`), never by the prefix, so we cannot tell which table a column belongs to. | 101 columns — the largest single unblock in the project. |
| 3 | Q7 | What are the 56 `precipdaily_*` columns, in what unit, and do `D` and `P` mean difference and percent change? | They are the largest family in the table and appear nowhere in the PDF. | 56 columns; any precipitation work at all. |
| 4 | Q8 | Do the FWI class columns hold the six fire-danger classes from the PDF, what does `NC` stand for, and are `FWI_Bins_*` and `FWIBins_*` the same thing at two aggregations? | 30 columns have no entry in the PDF; the text ones hold values like `High` and `Very High`. | 30 columns; the fire-weather pilot. |
| 5 | Q10 | Which Census vintage are `GEOID`, `TRACTCE`, `NAME_1` and `NAMELSAD` from, and what coordinate system are `X`/`Y` in? | If these columns carry Census tracts — which is itself only a reading (IC-016, IC-017) — their vintage decides every geographic join this project can make, and a wrong vintage mismatches silently. | 9 columns; all mapping and all aggregation. |
| 6 | Q11 | Which single column is the authoritative grid-cell key, and are `Crossmodel`, `Crossmodel_1` and `Crossmodel_12` the same identifier from three source layers? | They cannot be identical as stored — they are blank on 0, 22 and 83 rows respectively — so joining on the wrong one drops rows. | 8 columns; every join. |
| 7 | Q12 | Are `created_us`, `last_edite`, `Shape_STAr` and the rest GIS bookkeeping we can ignore, and in what units are the shape area and length? | We want to exclude them deliberately rather than by assumption. | 6 columns. |
| 8 | Q17 | For the 24 columns where one value repeats very often, is that value a real measurement or a "no data" code? | Treating a fill code as a measurement would corrupt any average we ever compute. A per-column answer is needed; a general rule will not do. | 24 columns; every summary statistic. |
| 9 | Q9 | What are the seven population and resilience columns, from which source, and **is `-9` in `Aggregate_Resilience_Indicator_` a no-data code**? | That column is `-9` on all 62,834 rows. We will not call it "missing" without you saying so. | 7 columns. |
| 10 | Q18 | When was this file exported, and from which ClimRR release? | We know when it was downloaded, not when it was made; the benchmark has to cite a data version. | Citability of the whole dataset. |
| 11 | Q2 | Six "consecutive days with no precipitation" fields are listed in the PDF with the description column left empty — what do they hold, and in days? | The PDF is blank there, so no amount of re-reading resolves it. | 6 columns. |
| 12 | Q3 | Two rows describing *minimum* temperature appear inside the *maximum* temperature table — is that a typo in the PDF? | If so, four columns are currently pointed at the wrong description. | 4 columns. |
| 13 | Q4 | All the winter rows for seasonal minimum temperature read "Annual Average – Historical" regardless of scenario, unlike spring, summer and autumn — is that a typo? | As written, the scenario of four columns is not established. | 4 columns. |
| 14 | Q5 | Is `rcp85_mid` in a column name the same as `RCP85_MIDC` in the PDF, and `rcp85_end` the same as `RCP85_ENDC`? | The file is inconsistent with itself here, not only with the PDF. | 12 columns. |
| 15 | Q6 | Are the truncated season names — `sprin`, `autum` — just shortened spellings of `spring` and `autumn`? | Probably yes, but we do not want to assume it. | 6 columns. |
| 16 | Q13 | What is a Fire Weather Index value's unit, and is the "seasonal value" the ensemble mean of the seasonal average daily FWI? | The PDF describes these columns without naming the quantity or its unit. | 20 columns. |
| 17 | Q14 | Are the heat-index values degrees Fahrenheit on the extended scale of Lu and Romps that the PDF cites? | No unit is stated; the observed values span roughly 27 to 107. | 10 columns. |
| 18 | Q15 | Are the degree-day columns computed against a 65 °F reference, in °F-degree-days? | The PDF says "usually 65°F" in its narrative but does not state it for these columns. | 6 columns. |
| 19 | Q16 | Do the blank cells mark grid cells a source layer simply does not cover — in particular the 6,938 rows (11% of the table) blank across all precipitation columns? | It decides whether a blank is "no coverage" or something meaningful. | Interpretation of every blank in the table. |

Full detail for any question, including the exact columns and the PDF line numbers, is in `docs/METADATA_QUESTIONS.md`.

### Literature corpus

**Not for the mentor.** These go to **JL**, who supplied the literature corpus and
its collection query on 2026-09-28 and is stated to have collected it. They are
listed here so the whole question inventory stays in one place. Each is
`unknown` in `data/manifest.json` until answered.

| # | Q-ID | Question (one sentence) | Why we need it | What it unblocks |
| --- | --- | --- | --- | --- |
| 1 | Q19 | On which platform or database was the query executed, and which fields did it search? | The same Boolean text returns different results on different databases. | Reproducing or citing the collection. |
| 2 | Q20 | When was the query executed, and when were the results exported? | The corpus has to be cited as a dated snapshot. | Citability of the corpus. |
| 3 | Q21 | Is the folder of 1,918 files the complete result set, and if not, what selected them? | A capped or filtered set changes what any sample drawn from it can represent. | How far M4-WP1's sample can be generalised. |
| 4 | Q22 | How was `full_705k_v2_filtered` (186,346 files) filtered from the 705k set? | The filter decides what the concept-first yields can be compared against. | Interpreting LITCORPUS-02's yields. |

## Answers received

| Date | Q-ID | Answer as relayed by Kaiyuan | Recorded as |
| --- | --- | --- | --- |
| 2026-09-10 | Q0 | There is no additional metadata for the table — no newer data dictionary, no assembly document or script, no release note. | R-001, D-010. **Q0 closed, answered negative.** Paraphrase, not verbatim. |
| 2026-09-10 | Q1–Q18 | "We do not need to use all the fields. We could let an AI reason out what the columns mean and use the fields that are reliable or can be reasonably explained. Each row stands for one event, so those fields can be used to construct the event and then build the connection to the literature. She wants to see examples." | R-002, D-010 (**approved 2026-09-13, with the GUIDANCE ruling incorporated as D-011**). A direction, not a column meaning: **no per-column answer was given for any of Q1–Q18**, and none was recorded. "Each row stands for one event" is Kaiyuan's reading and is **still to be confirmed with you** — it is line 1 of every checklist in `MENTOR_EXAMPLES.md`. Paraphrase, not verbatim. |
| 2026-09-17, 2026-09-24 | — | No review of the `MENTOR_EXAMPLES` answer sheet occurred. | R-003, D-014. **No line answered; no status changed.** Not an answer to any question --- recorded because the ruling requires the outcome to be recorded either way. |

## Meeting log

*Entries are in date order. The three added on 2026-09-28 follow the
2026-09-13 entry.*

### 2026-09-10 — mentor one-on-one

**Reported:** the table is pinned and fully profiled; the column catalogue and what the dictionary does and does not cover (21 / 143 / 28 / 83); and questions Q0, Q1, Q7, Q8, Q10 and Q11 — is there other documentation, which variable each column prefix comes from, the 56 undocumented daily-precipitation columns, the 30 fire-weather class columns, the Census vintage of the geographic columns, and which column is the join key.

**Answered:** Q0, in the negative — there is no other documentation of any kind. No per-column answer to any of Q1–Q18. Instead a direction: use a reliable subset, let reasoning fill in what can be reasonably explained, treat each row as one event, connect those events to the literature, and come back with examples.

**Newly asked:** confirm with the mentor that **one row = one event** is the right grain, by presenting 2–3 worked example records rather than asking in the abstract.

### 2026-09-13 — no meeting; the work between them

Not a meeting entry, kept here so the meeting log reads continuously. GUIDANCE
ruled on D-010 (**PASS WITH ACTIONS**) and Kaiyuan approved it with the ruling
incorporated (D-011). A fifth column status, `inferred_candidate`, now carries
readings reached by recorded reasoning — strictly below both
`verified_from_dictionary` and what the mentor confirms, and settable only by a
column-specific record that quotes the dictionary and states what it could not
rule out. Twenty columns hold it. Three example records were built from rows
0, 13 and 147 of the file, picked by rules that look only at whether a cell is
populated and never at how large a value is.

**To bring to the next meeting:** [`MENTOR_EXAMPLES.md`](MENTOR_EXAMPLES.md).

### 2026-09-14 — group meeting

**Presented:** the three prototype records and the handout
[`GROUP_MEETING_2026-09-14.md`](GROUP_MEETING_2026-09-14.md) --- whether the
phenomenon unit is the right scientific object.

**Feedback, recorded as the ruling allows it to be recorded:**

> **No material objection to the prototype-unit design was raised.**

Feedback was light. **It is not validation, and it confirms no column
semantic**: the group is not the data owner, and ruling action 12 of
`docs/M4_WP0_GUIDANCE_RULING.md` forbids reading light group feedback as owner
confirmation of field meanings. No status moved. The handout's five questions
received no recorded answer.

### 2026-09-17 and 2026-09-24 — mentor one-on-ones

**Brought:** [`MENTOR_EXAMPLES.md`](MENTOR_EXAMPLES.md) and its answer sheet.

**Outcome: no review occurred**, at either meeting (R-003). Recorded line by
line, as ruling action 11 requires --- exact responses if obtained, otherwise
`no review occurred`, with no status promotion:

| Answer-sheet line | Reading | Outcome | Status change |
| --- | --- | --- | --- |
| 1 | One row of the file is one "event" | no review occurred | none |
| 2 | `heatindex_*_DayMax` in °F, extended heat-index scale | no review occurred | none |
| 3 | `DayMax` is the summer average of daily maxima | no review occurred | none |
| 4 | `heatindex_C_*_DMax` is that quantity differenced; which way round | no review occurred | none |
| 5 | FWI "Seasonal value" is the seasonal average daily FWI | no review occurred | none |
| 6 | FWI values are dimensionless | no review occurred | none |
| 7 | `wildfire_summer_Dmid/Dend` are absolute differences; which way round | no review occurred | none |
| 8 | Stem `tempmaxann` denotes "Temperature Maximum - Annual" | no review occurred | none |
| 9 | Columns 44, 48, 52 are annual averages of daily max temperature in °F | no review occurred | none |
| 10 | `GEOID` is a Census tract id; which vintage | no review occurred | none |
| 11 | `TRACTCE` is the tract code alone | no review occurred | none |
| 12 | `X`, `Y` are longitude / latitude; which coordinate system | no review occurred | none |
| 13 | Observation only --- nothing to confirm | no review occurred | none |
| 14 | `NAME` / `State` / `State_Abbr` are county, state, postal code | no review occurred | none |
| 15 | What coverage explains 49 values; what the 7 blank rows are | no review occurred | none |
| 16 | Are these the kinds of records to connect to the literature | no review occurred | none |
| E2-2 | Identifiers carried as text with leading zeros | no review occurred | none |
| E3-2 | An empty cell is "no value in this file" | no review occurred | none |
| E3-3 | What the 83 rows empty from index 235 on are | no review occurred | none |

**No status promotion.** All 20 `inferred_candidate` columns stay
`inferred_candidate`. What the project does instead is D-014.

### 2026-09-28 — no meeting; literature corpus received

Not a meeting entry. JL supplied the literature corpus (a folder of 1,918
files) and the Boolean query it was collected with. Both are pinned by
SHA-256 (M4-WP0, D-015); no paper has been opened. Q19--Q21 are for JL.

### 2026-10-09 — mentor one-on-one

**Reported:** [MENTOR_REPORT_2026-10-09.md](MENTOR_REPORT_2026-10-09.md) --- the
M4-WP2 / M5-WP2 result, 0 eligible pairs of 78.

**Direction (D-020, relayed by Kaiyuan):** define concepts from the table units
first, then collect papers for those concepts with the ANL paper-collection
tool, rather than reading a corpus collected for another purpose; keep the
three units for now.

### 2026-10-13 — mentor meeting

**Reported:** the first concept-first run on one S2ORC shard --- **4** papers for
fire weather and **10** for heat index; the topical-only diagnostics, **13** and
**11**; and that bare "FWI" collides with other meanings (10 of the 13
diagnostic hits). **Asked:** for a larger source.

**Outcome:** JL shared a Google Drive link. JL's email: *"the google drive link
that I shared with you have 200K version of filtered climate dataset with name
full_705k_v2_filtered. This contains actually 186,346 json files."* Received
and pinned 2026-10-19 (D-023). Nothing else from the meeting is recorded here.

---

**How this file is maintained.** After each meeting Kaiyuan pastes his notes — the answers as the mentor gave them, in the mentor's own words where possible — to the COORDINATOR. The EXECUTOR then makes one commit per meeting that updates three things together: this file (a new row in *Answers received*, a filled-in *Meeting log* entry, and a rewritten *Status in five lines*), `data/metadata/resolutions.yaml` (one record per answer, carrying the date, the source, the verbatim statement, and the columns it settles), and `docs/DECISION_LOG.md` (the decision to accept that answer). An answer that names no columns is still recorded — it just moves no column, and the file says so rather than guessing which columns were meant.
