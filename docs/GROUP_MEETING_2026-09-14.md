# Turning a table row into something a paper could talk about

**Prototype for scientific-object validation. Not an accepted phenomenon record.**

**For the group meeting, 2026-09-14.** Everything below is a first attempt. The
point of showing it is to find out where it is wrong before it is built on.

## The problem

We have a climate projection table --- 62,834 rows, 275 columns --- and,
separately, a body of scientific papers. Nothing links them. A paper never
names a row, and a row never cites a paper. So before we can ask a question
that needs both, we have to say **what a row is about** in terms a paper could
plausibly also be about.

The attempt here is a *phenomenon record*: one unit of geography, one climate
quantity, one comparison between two time periods, and a direction. Eight
fields. Each field carries its own status, because some of what we "know" about
this table is quoted from its documentation and some of it is our reading.

| Field | What it holds | In these three records |
| --- | --- | --- |
| **G** scope | which rows, at what level | cell: documented. County and state: **our reading** |
| **H** concept | which quantity, from which columns | fire weather: **our reading**. Heat index: documented |
| **S** season | summer | documented |
| **T** time | baseline period and future period | documented |
| **C** scenario | RCP8.5 | documented |
| **V** values | the numbers, and the operation that made them | the raw numbers are the file's; the averages are **computed** |
| **D** direction | increase / decrease / no change | **computed, from a reading** |
| **M** magnitude | a category | **a placeholder rule**, explained below |

## Three things that are true of every line further down

> Every `wildfire_*` column holds a **Fire Weather Index** --- a meteorological
> fire-danger index. It is not a wildfire, an ignition, a burned area, or a
> probability of any of those.

> `Historical` means a **modeled historical baseline** --- the period 1995 to
> 2004, run through the same climate models. It is not an observation.

> Anything written `[provisional: ...]` rests on our reading of a column the
> documentation does not describe. Anything written `[provisional rule PR-1: ...]`
> rests on a placeholder, not on science. Text without a mark is quoted from the
> table's own documentation.

## How the three records were built

1. **The unit was chosen first, by identity, never by size.** One row that an
   earlier example already used; the `(State, NAME)` label that row carries; and
   the `State` label of a second example row. No number was looked at in the
   choosing.
2. **Members were taken as row sets.** A "county" here is *the set of rows
   carrying the same `State` and `NAME` label* --- not a boundary. The `GEOID`
   column cannot be used for this. **The `GEOID` column does not determine the
   `(State, NAME)` label: 3,234 `GEOID` values appear under more than one label.
   What that means is an open question for the data owner.**
3. **Every member is listed, none sampled.** The `Oklahoma` / `Stephens`
   label covers 10 rows; the `California` label covers 2,831, of which 2,827
   carry a heat-index value. Blanks are excluded from the averages and never
   read as zeros.
4. **Aggregation is a plain unweighted average**, every cell counting once. We
   do not know that cells are equal in area; nothing in the file says.
5. **Some columns are never averaged.** `wildfire_summer_Pend` is a *percent
   change*, and the mean of per-cell percent changes is not the percent change
   of the group --- it weights a cell with a tiny baseline as heavily as a large
   one. It is reported as a count of signs instead, and every per-cell value is
   kept.
6. **The prose is generated from the fields**, clause by clause, and the build
   fails if a value we reasoned reaches the text without its mark.

## The three records

### One grid cell

**Prototype for scientific-object validation. Not an accepted phenomenon record.**

**Scope.** One grid cell, identified by `R106C361`. Members: 1 cell(s) --- 1 with a value on every column used, 0 without. Cells without a value are excluded from every number below and are never read as a zero.

**Quantity.** [provisional: The multi-model ensemble mean of the summer seasonal average daily Fire Weather Index for the modeled historical period. The FWI is a meteorological fire-danger index: it describes weather conditions, not fire occurrence, ignition, or burned area]. Unit or type: [provisional: dimensionless index value]. Season: summer, defined by the dictionary as June, July and August.

**Compared.** Baseline horizon the modeled historical decade, 1995-2004; future horizon End-Century, the modeled decade 2085-2094; future scenario RCP8.5.

**Values.** `wildfire_summer_Hist` 25.080200200000000; `wildfire_summer_Endc` 31.189300540000001; `wildfire_summer_Dend` 6.109189990000000; `wildfire_summer_Pend` 24.358664999999998 --- read from the file, exactly as stored.

**Direction.** [provisional: increase], from the sign of the change value [provisional: 6.109189990000000], computed by `change_column_value` over `wildfire_summer_Dend`. The separate column `wildfire_summer_Pend` is positive on 1 of 1 member cell. It is a percent change and is never averaged here.

**Magnitude.** [provisional rule PR-1: upper_third, at percentile 88.5253 of 62834 cell-level units. Ranking is on the signed change value, not on its absolute size, so a unit in the lower third may be one with a large decrease rather than one where little changed. The reference population is every distinct `Crossmodel` value in the file, each forming one cell-level unit (62834 of them); a unit is included if at least one member cell is non-empty on every column this variable reads (62834 included, 0 excluded); its change value is the change value of its one cell; units whose label is the empty string are included (0 here). PR-1 is a placeholder and not a scientific threshold].

### One county-shaped row set

**Prototype for scientific-object validation. Not an accepted phenomenon record.**

**Scope.** The set of rows sharing a `(State, NAME)` label, identified by [provisional: `Oklahoma`, `Stephens`]. Members: 10 cell(s) --- 10 with a value on every column used, 0 without. Cells without a value are excluded from every number below and are never read as a zero.

**Quantity.** [provisional: The multi-model ensemble mean of the summer seasonal average daily Fire Weather Index for the modeled historical period. The FWI is a meteorological fire-danger index: it describes weather conditions, not fire occurrence, ignition, or burned area]. Unit or type: [provisional: dimensionless index value]. Season: summer, defined by the dictionary as June, July and August.

**Compared.** Baseline horizon the modeled historical decade, 1995-2004; future horizon End-Century, the modeled decade 2085-2094; future scenario RCP8.5.

**Values.** Unweighted mean over n = 10 member cell(s): `wildfire_summer_Hist` [provisional: 25.784530258000000]; `wildfire_summer_Endc` [provisional: 31.867660141000000]; `wildfire_summer_Dend` [provisional: 6.083151960000000]. Not averaged: `wildfire_summer_Pend`, because its recorded type is "Percent Change" --- a percent change is a ratio, the mean of per-cell ratios weights a cell with a near-zero baseline as heavily as one with a large baseline, and it is not the percent change of the aggregate. The M1-WP3b ruling forbids taking a mean of it (criterion 7). Every per-cell value, averaged or not, is in the record.

**Direction.** [provisional: increase], from the sign of the change value [provisional: 6.083151960000000], computed by `change_column_value per cell, then unweighted_mean` over `wildfire_summer_Dend`. The separate column `wildfire_summer_Pend` is [provisional: positive on 10 of 10 member cells]. It is a percent change and is never averaged here.

**Magnitude.** [provisional rule PR-1: upper_third, at percentile 90.6260 of 3019 county-level units. Ranking is on the signed change value, not on its absolute size, so a unit in the lower third may be one with a large decrease rather than one where little changed. The reference population is every distinct `(State, NAME)` label in the file, each forming one county-level unit (3019 of them); a unit is included if at least one member cell is non-empty on every column this variable reads (3019 included, 0 excluded); its change value is the unweighted mean of its member cells' change values; units whose label is the empty string are included (1 here). PR-1 is a placeholder and not a scientific threshold].

### One state-shaped row set

**Prototype for scientific-object validation. Not an accepted phenomenon record.**

**Scope.** The set of rows sharing a `State` label, identified by [provisional: `California`]. Members: 2831 cell(s) --- 2827 with a value on every column used, 4 without. Cells without a value are excluded from every number below and are never read as a zero.

**Quantity.** Number of Summer days with daily max heat index above 105 F -- Historical. Unit or type: Number of. Season: Summer.

**Compared.** Baseline horizon Historical; future horizon End-Century; future scenario RCP8.5.

**Values.** Unweighted mean over n = 2827 member cell(s): `heatindex_HIS_Day105` [provisional: 2.152729629062611]; `heatindex_E85_Day105` [provisional: 15.362681281927839]. Every per-cell value, averaged or not, is in the record.

**Direction.** [provisional: increase], from the sign of the change value [provisional: 13.209951652865228], computed by `difference_of_horizon_values per cell, then unweighted_mean` over `heatindex_HIS_Day105`, `heatindex_E85_Day105`.

**Magnitude.** [provisional rule PR-1: middle_third, at percentile 54.0000 of 50 state-level units. Ranking is on the signed change value, not on its absolute size, so a unit in the lower third may be one with a large decrease rather than one where little changed. The reference population is every distinct `State` label in the file, each forming one state-level unit (50 of them); a unit is included if at least one member cell is non-empty on every column this variable reads (50 included, 0 excluded); its change value is the unweighted mean of its member cells' change values; units whose label is the empty string are included (1 here). PR-1 is a placeholder and not a scientific threshold].

### About the magnitude field

"Upper third" means only this: the change value was ranked against every other
unit at the same level, and it landed above two thirds of them. **That is a
placeholder chosen so the field is not empty.** It is not a threshold, it rests
on no literature, and a tercile does not mean anything yet. Replacing it with
something defensible is question 2 below.

## What kind of question could this support?

None of these can be built yet --- the literature side does not exist. The
column that matters is the last one.

| Question type | Example shape | What it needs |
| --- | --- | --- |
| Pattern to explanation | "Fire-weather danger rises here by end of century. What mechanism would a paper give?" | county or state level; **needs a literature claim --- not yet available** |
| Claim to region | "A paper says humid heat rises fastest in the interior South. Which states does the table agree with?" | state level, all units; **needs a literature claim --- not yet available** |
| Support / contradiction | "Does the table's direction agree with what this paper reports?" | county or state level; **needs a literature claim --- not yet available** |
| Insufficient evidence | "Can this paper's claim be checked against this table at all?" | any level; **needs a literature claim --- not yet available** |
| Compositional | "Combine the table's magnitude with the paper's stated criteria to classify this area." | county or state; **needs a literature claim --- not yet available --- and a magnitude rule we believe** |
| Table-only lookup | "What is the end-century value in this cell?" | cell level; no literature --- **and this is the kind of question we are trying not to build** |

Two things are visible already. **A grid cell has no place name**, so a
cell-level record has nothing a paper could be searched with --- the identifier
is `R106C361`. And a county name alone is ambiguous: `Lincoln` is a county in
many states.

## Five questions for the group

1. **What should the unit of a phenomenon be?** A cell has no name a paper
   would use. A county has a name but 10 cells here and 2,865 in the largest
   case. A state is coarse enough that a paper might actually discuss it.
2. **How should magnitude be decided?** Terciles are a placeholder. What would
   make a category defensible --- a physical threshold, a distributional one, or
   something taken from the literature itself?
3. **Should cells be weighted?** Everything above averages cells equally. We do
   not know whether they are equal in area, and we have no population weighting.
   Does an unweighted average of a fire-danger index mean anything?
4. **Which question type should we try to build first?** The answer decides what
   the literature side has to deliver.
5. **What would a paper plausibly say about a county-level change in fire
   weather?** If the honest answer is "nothing --- papers discuss regions, fire
   regimes and seasons, not counties", that is the most useful thing we could
   learn today, and it changes the unit.

---

Full records, with every member cell and every operation:
[`PHENOMENON_PROTOTYPES.md`](PHENOMENON_PROTOTYPES.md). Everything we are
assuming, in one table: [`PHENOMENON_ASSUMPTIONS.md`](PHENOMENON_ASSUMPTIONS.md).
