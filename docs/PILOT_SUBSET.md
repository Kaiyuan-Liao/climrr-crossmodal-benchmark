# The M1-WP3 pilot subset

**41 of 275 columns.** Selected under D-010 and D-011 so that a small set of
fields can be carried all the way to a mentor-confirmable record, while the
other 234 columns stay exactly where M1-WP1 left them.

> **The scope narrows; the rigour does not.** GUIDANCE ruled that M1 gate
> criterion 1 --- meaning, unit where applicable, time horizon, scenario,
> missing-value policy and provenance status --- is evaluated on **every field
> selected for this pilot**, and on no others. A column not in the table below
> has not been interpreted, is not used by any example, and is not claimed to be
> understood.

| Status | Columns | What it means here |
| --- | ---: | --- |
| `verified_from_dictionary` | **21** | The dictionary states meaning, a unit or type, and a scenario or horizon, in a cited span. D-009's bar, unchanged. |
| `owner_confirmed` | **0** | Nothing has been confirmed by the mentor yet. That is what the examples are for. |
| `inferred_candidate` | **20** | Reasoned, recorded, column-specific --- and **not verified, not owner-confirmed**. Each cites an IC-record in [`../data/metadata/inferred_candidates.yaml`](../data/metadata/inferred_candidates.yaml). |
| **Total** | **41** | |

The 21 verified columns are **every** `verified_from_dictionary` column in the
file. That is not a coincidence and it is the shape of the selection: the pilot
is built outward from the places where the dictionary speaks for itself, adding
only the neighbouring columns needed to make those readable, and stopping.

---

## What was selected, and why

### Family 1 --- Heat Index – Summer (17 columns: 12 verified, 5 inferred)

| Indices | Columns | Status |
| --- | --- | --- |
| 240–243, 246–249, 252–255 | `heatindex_{HIS,M85,E85}_Day{95,105,115,125}` | `verified_from_dictionary` |
| 238, 244, 250 | `heatindex_{HIS,M85,E85}_DayMax` | `inferred_candidate` — IC-001, IC-002, IC-003 |
| 256, 262 | `heatindex_C_{M85,E85}_DMax` | `inferred_candidate` — IC-004, IC-005 |

**Scientific relevance.** Summer heat is the ClimRR variable that bears most
directly on human exposure, and the eventual purpose of these records is to
connect a table row to published work. **How large the literature actually is,
here or for any other family, is not established** --- no literature work is
authorised yet (M3), so this is a reason for the choice and not a measured
claim.

**Interpretability.** This is the only family in the file where twelve columns
are already verified from the dictionary's own words, with a single, specific
gap: **the unit** (Q14). The dictionary names the quantity, the season, the
scenario and the horizon for every one of these columns and states a unit for
none of them. That makes it the cleanest possible test of whether an
`inferred_candidate` record can close one well-defined gap without quietly
widening.

**Provenance awareness.** Every one of the five inferred columns matched a
dictionary field name **exactly**, so nothing about which section they belong to
is being inferred --- unlike Family 4, where the section link is the whole
question. The inference here is one attribute, not a correspondence.

**Literature compatibility.** The dictionary cites Lu and Romps' *Extending the
Heat Index* (line 417), which is a specific, findable paper; a confirmed unit
would tie these columns to a defined scale rather than to a number.

**Why the `DayMax` trio and not the `SeaMax` trio.** They carry the identical
unit question and confirming one answers the other, so including both would have
doubled the records without adding a question. `DayMax` was chosen because of what IC-001 proposes about
it: that the narrative at lines 406–407 describes this column, and so that
`DayMax` holds the summer *average* of daily maxima rather than the summer's
single maximum. **That is an inference, not a quotation** --- the dictionary
never says that its narrative item and its field entry are the same
quantity --- and it is worth putting in front of the mentor precisely because it
contradicts the reading the name invites. Checklist line 3 asks her directly.

### Family 2 --- Fire Weather Index - Averages (13 columns: 8 verified, 5 inferred)

| Indices | Columns | Status |
| --- | --- | --- |
| 180, 181, 187, 188, 194, 195, 201, 202 | `wildfire_{autumn,spring,summer,winter}_{Pmid,Pend}` | `verified_from_dictionary` |
| 189–193 | `wildfire_summer_{Hist,Midc,Endc,Dmid,Dend}` | `inferred_candidate` — IC-006 … IC-010 |

> **These columns hold a Fire Weather Index.** FWI is a meteorological
> fire-danger index. It is not wildfire occurrence, ignition, burned area, or
> risk to a structure. No record, no example and no sentence generated from
> either may read an FWI value as a fire. This is a standing rule of the
> repository, not a caution specific to this pilot.

**Scientific relevance.** FWI is the other family this project expects to be
able to connect to published work --- again a reason for the choice rather than
a measured claim, for the same reason as Family 1 --- and its four seasons and
three horizons, both of which the dictionary names in its own field entries,
give the pilot its widest scenario coverage.

**Interpretability.** The eight percent-change columns are verified because the
dictionary writes "Percent Change" against them. Their `D` siblings say only
"Difference", and the value columns say only "Seasonal value" --- so the family
has a documented half and an undocumented half **within one table**, which is
exactly the boundary a mentor can rule on quickly.

**Provenance awareness.** The gap here is larger than Family 1's and the records
say so: besides the unit (Q13), "Seasonal value" could denote the seasonal
*average* the narrative defines at lines 346–352, or the seasonal *95th
percentile* the FWI-classes narrative defines from line 357. IC-006 records that
ambiguity as unresolved rather than choosing quietly.

**Why summer only.** One season is enough to build one example, and the unit
question is identical across all four. Taking all four would have added fifteen
records that ask the same question.

### Family 3 --- Location anchor (8 columns: 1 verified, 7 inferred)

| Indices | Columns | Status |
| --- | --- | --- |
| 1 | `Crossmodel` | `verified_from_dictionary` |
| 2, 3, 4 | `NAME`, `State`, `State_Abbr` | `inferred_candidate` — IC-011, IC-012, IC-013 |
| 106, 107 | `X`, `Y` | `inferred_candidate` — IC-014, IC-015 |
| 108, 109 | `TRACTCE`, `GEOID` | `inferred_candidate` — IC-016, IC-017 |

**Why any location at all.** An example has to be able to say *where* the row
is, or the mentor cannot recognise it as a record of anything. This is the
minimum set that does that.

**Two things are stated plainly and neither is resolved by this pilot.** Note
that both sentences below describe **inferred** readings: the dictionary says
nothing about any of these four columns, so even the *kind* of thing they hold is
an inference this pilot is asking the mentor to confirm.

1. **The Census vintage is unknown.** `GEOID` and `TRACTCE` are read here as
   Census tract identifiers --- an inference, IC-017 and IC-016 --- whose codes
   are re-cut between decennial vintages. **If** that reading is right, the
   vintage decides every join this project could later make, and nothing here
   establishes it. Q10.1 and Q10.2 are the questions; the records propose
   answers and say what they cannot rule out.
2. **The coordinate reference system is unknown.** `X` and `Y` are read here as
   longitude and latitude in decimal degrees --- an inference, IC-014 and
   IC-015, resting on the observed ranges rather than on any statement in the
   dictionary. At the precision stored, the common geographic systems are not
   distinguishable from a coordinate range, and the dictionary names none, so
   the system would remain unknown even if the reading is confirmed (Q10.3).

**No geographic aggregation is performed anywhere in this pilot**, by these
columns or any others. They label one row; they do not group rows.

**Provenance awareness.** These seven columns appear **nowhere** in the data
dictionary --- not as field names, not in the narrative. They are taken to have
been joined in from elsewhere before the file reached this project, on the
strength of D-008 --- which is **stated by Kaiyuan and not independently
verified** --- and R-001 established that no assembly document exists to say
from where. Each record therefore cites the two
passages that establish *why* the column is absent: the document's statement of
its own scope (line 79) and the `Crossmodel` entry (line 455), which shows that
the dictionary's unit of record is a **grid cell**, not a Census geography.

**`OID_` (index 0) is deliberately not in the subset.** The examples report its
value as an address into the file alongside `Crossmodel`, because a reader needs
a stable handle on a row. That is not a claim about what the column means, and
Q11 --- which column is the authoritative grid-cell key --- stays open.

### Family 4 --- Stem-assumption probe (3 columns, all inferred)

| Indices | Columns | Status |
| --- | --- | --- |
| 44, 48, 52 | `tempmaxann_hist`, `tempmaxann_rcp85_endc`, `tempmaxann_end85_hist` | `inferred_candidate` — IC-018, IC-019, IC-020 |

**These three exist to make Q1 concrete.** The dictionary names its fields by
suffix inside a per-variable section --- `HIST`, `RCP85_ENDC`, `END85_HIST` ---
and the CSV writes a stem plus that suffix. **The dictionary never states that a
CSV stem denotes a section.** Reaching the section's description therefore
requires an inference about how the export was built, which D-009 reserves for
the data owner, and R-001 established that no export specification exists to
settle it.

**101 columns (indices 5–105) depend on that one link.** Asking about it in the
abstract has already been tried and produced no answer. These three records put
it in front of the mentor on a case she can look at: if she rejects the link
here, 101 columns fall with it; if she confirms it, the largest block in the
inventory moves at once.

Note what the records do with the unit. The dictionary prints "(°F)" in plain
sight at lines 518, 522 and 526 --- and the records tag it `inferred` anyway,
because **a quoted unit reached through an unconfirmed link is an inference, not
a quotation.**

**Three columns and no more**, as the ruling allows: a historical value, a
projected value, and a change between them, which is the smallest set that
exercises the link across all three shapes the family takes.

---

## What was deliberately excluded, and why

| Excluded | Indices | Why |
| --- | --- | --- |
| `precipdaily_*` | 119–174 | **The largest undocumented family in the table (56 columns).** No field table lists any `precipdaily` field and no narrative describes one (Q7). There is nothing to reason *from* --- a record here could only say "the name suggests it", which D-011 forbids. |
| `Aggregate_Resilience_Indicator_` | 117 | Constant `-9` on all 62,834 rows. **D-009 ruling 3 kept this column with `-9` unlabelled**: whether it is a no-data code is a decision for the data owner, not an inference from the value (Q9.2). Unchanged here. |
| `FWI_Bins_*`, `FWIBins_*` | 205–234 | 30 columns whose only related passage is the "Calculating FWI Classes" narrative (Q8). What `NC` abbreviates is unknown, and whether the `_95` columns hold the 95th-percentile values the classes are cut from is unknown. Interpreting them would require choosing among readings, not reasoning between them. |
| The other three FWI seasons' value/difference columns | 175–179, 182–186, 196–200 | The unit question is identical to summer's. Fifteen more records asking one question is not more rigour. |
| `heatindex_*_SeaMax` and the `C_*` day-count changes | 239, 245, 251, 257–261, 263–267 | Same unit question as the selected heat-index columns; confirming IC-001 answers them. |
| The other 98 stem-family columns | 5–43, 45–47, 49–51, 53–105 | All depend on the same Q1 link the three probe columns test. Three cases is enough to ask the question; 101 is not a subset. |
| Socioeconomic columns | 112–118 | Undocumented, on incompatible scales (index 112 ranges 0–100, index 113 ranges 0.04–0.80), from an unnamed source and vintage (Q9). Outside what an example needs. |
| The other identifier and bookkeeping columns | 0, 110, 111, 203, 204, 235–237, 268–274 | `OID_` is used as an address only, as above. The rest are the suffixed `Crossmodel`/`OBJECTID` copies, whose relationship to one another is **open** (Q11 — and Q11.4 showed indices 235 and 236 are *not* duplicates, so "duplicate" is exactly what must not be assumed), and the columns Q12 asks about, which it *proposes* are ArcGIS editor-tracking and shape fields without that being established. None has any established climate content, which is why none is used. |

**Every excluded column keeps the status M1-WP1 gave it.** The WP1 baseline is
frozen per column in `status_baseline_wp1` and nothing in this work package
touches it; `scripts/status_diff.py` shows the 20 columns that moved and
attributes each to its IC-record.

---

## How to check this document against the artifacts

```bash
python scripts/dictionary_coverage.py   # rebuilds the coverage report
python scripts/status_diff.py           # shows the 20 columns that moved, and why
python scripts/build_examples.py        # rebuilds the three example records
pytest
```

- Per-column reasoning: [`../data/metadata/inferred_candidates.yaml`](../data/metadata/inferred_candidates.yaml)
- Per-column status and spans: [`../artifacts/profiles/dictionary_coverage.json`](../artifacts/profiles/dictionary_coverage.json)
- What moved since WP1: [`../artifacts/profiles/status_diff.md`](../artifacts/profiles/status_diff.md)
- The open questions this subset leaves open: [`METADATA_QUESTIONS.md`](METADATA_QUESTIONS.md)
- The ruling that bounds all of it: [`M1_D010_GUIDANCE_RULING.md`](M1_D010_GUIDANCE_RULING.md)
