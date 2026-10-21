# Mentor brief — ClimRR cross-modal benchmark

Last updated: 2026-10-21   Next meeting: **Thursday 2026-10-22** --- bring the items under *For Thursday* below; the answer sheet is still outstanding

## Status in five lines

1. **The table is pinned and partly interpreted**: 62,834 rows, 275 columns, read as text; 41 columns interpreted (21 stated by the dictionary, 20 reasoned and marked so). Nothing reasoned is confirmed --- **the answer sheet has still not been reviewed**, so all 20 stay `inferred_candidate`; the project proceeds on "our reading" (D-014), which promotes nothing.
2. **Your concept-first method found papers, but still no link.** On the 186,346-file climate set JL shared, the fire weather index and heat-index searches gave 448 and 861 papers. 20 of those that mention Oklahoma, Stephens or California (10 + 10, picked by a fixed rule before anyone opened them) were each read by two independent readers and reconciled into **118 statements** (3 found identically by both readers, 47 found by both and reconciled, 68 found by one reader only): **0 of 354 statement--unit pairs qualify as a candidate link.**
3. **The zero now points at our units, not at the papers.** 12 pairs share the concept family and 2 share the place, but never both in the same statement. GUIDANCE's reading: papers usually describe a broader quantity (for example "heat index" rather than "days above 105 °F"), a broader area (a state or a region rather than one county or grid cell) and often no emissions scenario. GUIDANCE accepted the zero for these 20 papers only, and nothing beyond them (D-027).
4. **A survey of every concept in the data dictionary is done** (diagnostic counts, not prevalence). Broad quantities appear widely in the literature; the specific heat-index threshold measures barely appear by their exact wording. Under our current search terms, those threshold measures have **effectively no direct word-for-word footprint**. That does **not** show the literature lacks them.
5. **Next:** a small test of whether table units stated at the level papers use (a quantity family, a state or region) make links possible, with the current three units kept as controls. The second survey run, at the family level, is done and accepted as a diagnostic (D-028); the literature-survey track now pauses until your feedback. **No questions are generated** (QA is still not authorized).

## What I need from this meeting

> ### **For Thursday 2026-10-22**
>
> **Seven quantity families as discussion candidates.** These are **for discussion only**, not approved
> benchmark families. They are listed in dictionary order (pp. 6--11), and **the order is not a ranking**.
> The counts are **measure-level** survey run 1 counts (documents matching any search term for the
> dictionary's own measure; diagnostic coverage counts, not prevalence). **The second, family-level survey run
> separates three levels of coverage --- the dictionary's exact measure wording (0--2 documents for the heat-index
> measures), the approved family terms in our concept map (548 for the fire weather index, 1,080 for "heat index"),
> and broad families proposed by the model (2,681 to 143,266 documents, often much broader than the measure, such as
> "moisture" for precipitation) --- and only the middle level uses approved vocabulary; none is credited to a single
> measure.** GUIDANCE (D-028) adopted these three levels as the standing way we report coverage: they are
> never ranked or added together, and a zero at the exact-measure level means no word-for-word match under our
> current search rules, not that no relevant literature exists.
>
> | Family (discussion candidate) | Dictionary measure(s) | Measure-level coverage, run 1 (all / with climate context) | Concept-map family terms (approved vocabulary; all documents) |
> | --- | --- | --- | --- |
> | temperature | annual; seasonal | 124,420 / 88,245; 123,948 / 88,021 (both counts are almost entirely the bare word "temperature") | no concept-map entry |
> | precipitation | precipitation | 84,926 / 61,190 | no concept-map entry |
> | wind speed | wind speed | 27,498 / 17,394 | no concept-map entry |
> | consecutive dry days / dry spell | consecutive days with no precipitation | 6,981 / 4,946 | no concept-map entry |
> | degree days | heating and cooling degree days | 3,076 / 2,638 | no concept-map entry |
> | fire weather index | seasonal FWI; FWI classes | 548 / 395; 551 / 396 | **548** (the five approved fire-weather-index terms; 473 once a bare "FWI" must be backed by "fire weather") |
> | heat index | daily max; seasonal max; days above 95 / 105 / 115 / 125 °F | 0; 1; --- (no searchable term); 0; --- (no searchable term); 2 (all and with-context counts are equal) | **1,080** ("heat index" alone; 1,082 with "heat-index" and "extended heat index") |
>
> Only two of the seven families have approved concept-map terms so far, so the other five have no
> concept-map count. The model-proposed family totals from the second run are deliberately **not** shown
> here: they rest on search words the model proposed, many broader than the quantity itself, and no
> family count is ever credited to a single threshold measure.
>
> **Questions, in priority order.** The two families that already have approved concept-map terms, fire
> weather index and heat index, are the first candidates for redesigned units; the other five are not used
> until they are governed.
>
> **1. The key scientific question (GUIDANCE, verbatim):** *"Should a benchmark unit represent the exact
> ClimRR metric, or is a governed family-level quantity such as heat index / Fire Weather Index an acceptable
> table-side semantic object when the exact measure and scenario remain preserved as provenance?"* For
> example: a unit whose family is *heat index*, while the exact measure (*days above 105 °F*) and the emissions
> scenario stay attached to it as a record of where the number came from, not as something a paper must match.
>
> **2. Would state-level or region-level units be acceptable to you as the table-side granularity?**
>
> **3. A candidate question type: cross-location comparison.** *"A paper reports a pattern for a
> phenomenon family at place A; the table's deterministic value for the same family at place B; same or
> different direction."* This is a **candidate relation**. It would be defined and frozen before any test,
> and nothing has been generated. Guardrails:
>
> - **Paper side:** an adjudicated claim with an explicit concept, a direction, and the paper's own
>   study-area geography.
> - **Table side:** a frozen deterministic aggregate at a granularity papers actually name.
> - **Answer:** two attested facts plus a computed comparison.
> - **Scenario:** an unknown scenario is tolerated and flagged, never treated as a match.
> - **Exclusions:** papers that state no place are excluded.
>
> Is this a relation you would want the benchmark to test?
>
> **4. Which of the five families without approved terms --- temperature, precipitation, wind speed,
> consecutive dry days / dry spell, degree days --- would you want governed, if any?** Choosing one would start
> a separate decision on its approved vocabulary; coverage counts will not decide this on their own, and broader
> families the model proposed (for example "hydrology" for precipitation, or generic "fire risk") are not
> candidates.
>
> **Still open from 2026-10-19:** in general scientific text "FWI" often means
> something else (full waveform inversion, Forest Watch Indonesia, fatal work
> injuries); we count a bare "FWI" only when the same paper also says "fire
> weather" or a longer fire-weather phrase. **Is that the right rule for the
> fire-weather literature you have in mind?**

> ### **First question for the next one-on-one**
>
> *For 2026-10-22 this is asked as question 1 above, in GUIDANCE's sharper wording (D-028).*
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
