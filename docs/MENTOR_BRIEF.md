# Mentor brief — ClimRR cross-modal benchmark

Last updated: 2026-09-13   Next meetings: group 2026-09-14; one-on-one 2026-09-17

## Status in five lines

1. The ClimRR table is in the project, unchanged and checksum-pinned — 62,834 rows, 275 columns, every value read as text so identifiers keep their leading zeros.
2. **The 2026-09-10 meeting settled the big question negatively: there is no further documentation.** No newer dictionary, no assembly document or script, no release note. What we have is all there is, and no per-column answer was given.
3. **The direction changed instead of the evidence**, and it is now approved and built. Rather than documenting all 275 columns: interpret a deliberately small subset, write down the reasoning column by column, and bring worked examples back for confirmation.
4. **41 of the 275 columns are now interpreted — 21 the dictionary states outright, 20 reasoned and marked as reasoned.** The other 234 are untouched and explicitly unresolved. Nothing reasoned is recorded as verified; the two are different statuses and stay visibly different.
5. **Three example records are built from real rows and are ready for you.** They are in [`MENTOR_EXAMPLES.md`](MENTOR_EXAMPLES.md), and your answers to the numbered lines there are what would promote any of the 20 reasoned readings to confirmed.

## What I need from this meeting

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
| 5 | Q10 | Which Census vintage are `GEOID`, `TRACTCE`, `NAME_1` and `NAMELSAD` from, and what coordinate system are `X`/`Y` in? | The tract vintage decides every geographic join this project can make; a wrong vintage silently mismatches tracts. | 9 columns; all mapping and all aggregation. |
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

## Answers received

| Date | Q-ID | Answer as relayed by Kaiyuan | Recorded as |
| --- | --- | --- | --- |
| 2026-09-10 | Q0 | There is no additional metadata for the table — no newer data dictionary, no assembly document or script, no release note. | R-001, D-010. **Q0 closed, answered negative.** Paraphrase, not verbatim. |
| 2026-09-10 | Q1–Q18 | "We do not need to use all the fields. We could let an AI reason out what the columns mean and use the fields that are reliable or can be reasonably explained. Each row stands for one event, so those fields can be used to construct the event and then build the connection to the literature. She wants to see examples." | R-002, D-010 (**approved 2026-09-13, with the GUIDANCE ruling incorporated as D-011**). A direction, not a column meaning: **no per-column answer was given for any of Q1–Q18**, and none was recorded. "Each row stands for one event" is Kaiyuan's reading and is **still to be confirmed with you** — it is line 1 of every checklist in `MENTOR_EXAMPLES.md`. Paraphrase, not verbatim. |

## Meeting log

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

---

**How this file is maintained.** After each meeting Kaiyuan pastes his notes — the answers as the mentor gave them, in the mentor's own words where possible — to the COORDINATOR. The EXECUTOR then makes one commit per meeting that updates three things together: this file (a new row in *Answers received*, a filled-in *Meeting log* entry, and a rewritten *Status in five lines*), `data/metadata/resolutions.yaml` (one record per answer, carrying the date, the source, the verbatim statement, and the columns it settles), and `docs/DECISION_LOG.md` (the decision to accept that answer). An answer that names no columns is still recorded — it just moves no column, and the file says so rather than guessing which columns were meant.
