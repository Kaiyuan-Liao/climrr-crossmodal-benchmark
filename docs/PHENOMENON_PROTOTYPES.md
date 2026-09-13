# Three prototype phenomenon units

**Prototype, ahead of its ruling.** Built for M1-WP3b on Kaiyuan's decision of
2026-09-13, following the mentor's direction R-002, while the GUIDANCE ruling that
would authorise county and state units, aggregation and a magnitude field is
pending. The D-010 ruling in force forbids all three inside an M1-WP3 example.
**Nothing here is evidence for a milestone gate**, nothing is merged, and the
ruling may revise or discard all of it.

- Schema version `p0-prototype` --- `src/climrr/phenomenon.py`
- Built from commit `ce8df0761dc74e498ee9ef99cdccfbc61a3f9afc`, CSV SHA-256 `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`
- Assumptions, in full: [`PHENOMENON_ASSUMPTIONS.md`](PHENOMENON_ASSUMPTIONS.md)
- Structural facts the units rest on: [`../artifacts/profiles/hierarchy_checks.md`](../artifacts/profiles/hierarchy_checks.md)

Each record's fields are `G` scope, `H` concept, `S` season, `T` time horizon,
`C` climate scenario, `V` values, `D` direction, `M` magnitude. **The reading of
`S`, `T` and `C` is the EXECUTOR's**: the work package names the letters without
defining them, and the blueprint's schema list runs "season; baseline period;
future period; scenario". Renaming them changes three labels and no number.

## P-CELL-1 --- cell level

| Field | Value | Status |
| --- | --- | --- |
| `G` identifier | `R106C361` | `verified_from_dictionary` |
| `G` members | 1 cell(s); 1 with a value, 0 without | `computed` |
| `H` variable | Fire Weather Index, summer --- modeled historical to end-century RCP8.5 | `inferred_candidate` |
| `H` columns | 189 `wildfire_summer_Hist` (baseline), 191 `wildfire_summer_Endc` (future), 193 `wildfire_summer_Dend` (change), 195 `wildfire_summer_Pend` (corroborating_change) | per column, below |
| `V` change value | `6.109189990000000` | `derived_from_inferred` |
| `D` direction | **increase** | `derived_from_inferred` |
| `M` category | upper_third, percentile 88.5253 of 62834 units | `provisional_rule` PR-1 |

Chosen by: the row `OID_` 1, which is M1-WP3's Example 1 --- itself selected by structural rule R-A, the first row non-empty on every pilot column. No value was consulted in the choice.

### Generated description

> Every `wildfire_*` column below holds a **Fire Weather Index** --- a meteorological fire-danger index, listed in the dictionary under the section "Fire Weather Index - Averages". It is not a wildfire, an ignition, a burned area, or a probability of any of those, and nothing in this record says that it is.

> `Historical` here means a **modeled historical baseline** --- the dictionary's historical period, 1995 to 2004, run through the same climate models. It is not an observation, a measurement, or a record of anything that happened.

**Scope.** One grid cell, identified by `R106C361`. Members: 1 cell(s) --- 1 with a value on every column used, 0 without. Cells without a value are excluded from every number below and are never read as a zero.

**Quantity.** [provisional: The multi-model ensemble mean of the summer seasonal average daily Fire Weather Index for the modeled historical period. The FWI is a meteorological fire-danger index: it describes weather conditions, not fire occurrence, ignition, or burned area]. Unit or type: [provisional: dimensionless index value]. Season: summer, defined by the dictionary as June, July and August.

**Compared.** Baseline horizon the modeled historical decade, 1995-2004; future horizon End-Century, the modeled decade 2085-2094; future scenario RCP8.5.

**Values.** `wildfire_summer_Hist` 25.080200200000000; `wildfire_summer_Endc` 31.189300540000001; `wildfire_summer_Dend` 6.109189990000000; `wildfire_summer_Pend` 24.358664999999998 --- read from the file, exactly as stored.

**Direction.** [provisional: increase], from the sign of the change value [provisional: 6.109189990000000], computed by `change_column_value` over `wildfire_summer_Dend`. The separate column `wildfire_summer_Pend` gives increase on the same unit; the two signs agree: True.

**Magnitude.** [provisional rule PR-1: upper_third, at percentile 88.5253 of 62834 cell-level units, by PR-1, which is a placeholder and not a scientific threshold].

Every clause marked [provisional:...] rests on an inferred-candidate record or on a field derived from one: reasoned and written down, **not verified and not owner-confirmed**. The clause marked [provisional rule PR-1:...] rests on a placeholder rule, not on science.

### What it depends on

Assumptions: `A1`, `A-G0`, `A-DIR1`, `A-DIR2`, `A-H1`, `A-H3`, `A-H5`, `A-M1`.

### Literature probe --- design stub, nothing sent

- Concept terms: fire weather index, FWI, fire weather, fire danger
- Place terms: R106C361 (`Crossmodel`, `verified_from_dictionary`)
- Direction term: increase
- Horizon terms: the modeled historical decade, 1995-2004 (baseline), End-Century, the modeled decade 2085-2094 (future), Historical (1995-2004) to End-Century (2085-2094) (change), Historical, End-Century (corroborating_change)
- Scenario terms: Historical --- a modeled baseline, not an observation (baseline), RCP8.5 (future), Historical compared with RCP8.5 (change)
- On the place terms: A grid-cell id is not a phrase any paper contains. At cell level the probe has **no usable place term**, which is itself a finding about what a cell-level unit could ever be matched to.
- Generated query sentence: *increase in fire weather index in R106C361 under RCP8.5 by End-Century, the modeled decade 2085-2094*

This is what would be sent to retrieval. **Nothing has been sent.** No literature corpus exists in this repository, no index has been built, and no passage has been read. M3 is not authorised.

Full record: [`../artifacts/phenomena/prototypes/P-CELL-1.json`](../artifacts/phenomena/prototypes/P-CELL-1.json)

## P-COUNTY-1 --- county level

| Field | Value | Status |
| --- | --- | --- |
| `G` identifier | `Oklahoma`, `Stephens` | `inferred_candidate` |
| `G` members | 10 cell(s); 10 with a value, 0 without | `computed` |
| `H` variable | Fire Weather Index, summer --- modeled historical to end-century RCP8.5 | `inferred_candidate` |
| `H` columns | 189 `wildfire_summer_Hist` (baseline), 191 `wildfire_summer_Endc` (future), 193 `wildfire_summer_Dend` (change), 195 `wildfire_summer_Pend` (corroborating_change) | per column, below |
| `V` change value | `6.083151960000000` | `derived_from_inferred` |
| `D` direction | **increase** | `derived_from_inferred` |
| `M` category | upper_third, percentile 90.6260 of 3019 units | `provisional_rule` PR-1 |

Chosen by: the `(State, NAME)` label carried by the row `OID_` 1. No value was consulted in the choice.

### Generated description

> Every `wildfire_*` column below holds a **Fire Weather Index** --- a meteorological fire-danger index, listed in the dictionary under the section "Fire Weather Index - Averages". It is not a wildfire, an ignition, a burned area, or a probability of any of those, and nothing in this record says that it is.

> `Historical` here means a **modeled historical baseline** --- the dictionary's historical period, 1995 to 2004, run through the same climate models. It is not an observation, a measurement, or a record of anything that happened.

> The `State` and `NAME` values used to form this unit are `inferred_candidate` readings (IC-011, IC-012): the dictionary does not mention either column, and the Census vintage and coordinate reference system behind them are unknown. **This prototype groups rows by those labels**, which M1-WP3 deliberately did not do. The group is the set of rows carrying the label --- not a boundary, not a geometry, and not keyed on `GEOID`, which Phase A measured does not determine the label (A-G3).

**Scope.** The set of rows sharing a `(State, NAME)` label, identified by [provisional: `Oklahoma`, `Stephens`]. Members: 10 cell(s) --- 10 with a value on every column used, 0 without. Cells without a value are excluded from every number below and are never read as a zero.

**Quantity.** [provisional: The multi-model ensemble mean of the summer seasonal average daily Fire Weather Index for the modeled historical period. The FWI is a meteorological fire-danger index: it describes weather conditions, not fire occurrence, ignition, or burned area]. Unit or type: [provisional: dimensionless index value]. Season: summer, defined by the dictionary as June, July and August.

**Compared.** Baseline horizon the modeled historical decade, 1995-2004; future horizon End-Century, the modeled decade 2085-2094; future scenario RCP8.5.

**Values.** Unweighted mean over n = 10 member cell(s): `wildfire_summer_Hist` [provisional: 25.784530258000000]; `wildfire_summer_Endc` [provisional: 31.867660141000000]; `wildfire_summer_Dend` [provisional: 6.083151960000000]; `wildfire_summer_Pend` [provisional: 23.603612800000000]. The complete per-cell values are in the record.

**Direction.** [provisional: increase], from the sign of the change value [provisional: 6.083151960000000], computed by `change_column_value per cell, then unweighted_mean` over `wildfire_summer_Dend`. The separate column `wildfire_summer_Pend` gives [provisional: increase] on the same unit; the two signs agree: True.

**Magnitude.** [provisional rule PR-1: upper_third, at percentile 90.6260 of 3019 county-level units, by PR-1, which is a placeholder and not a scientific threshold].

Every clause marked [provisional:...] rests on an inferred-candidate record or on a field derived from one: reasoned and written down, **not verified and not owner-confirmed**. The clause marked [provisional rule PR-1:...] rests on a placeholder rule, not on science.

### What it depends on

Assumptions: `A1`, `A-G0`, `A-G1`, `A-G2`, `A-G3`, `A-AGG1`, `A-DIR1`, `A-DIR2`, `A-H1`, `A-H3`, `A-H5`, `A-M1`.

### Literature probe --- design stub, nothing sent

- Concept terms: fire weather index, FWI, fire weather, fire danger
- Place terms: Oklahoma (`State`, `inferred_candidate`), Stephens (`NAME`, `inferred_candidate`)
- Direction term: increase
- Horizon terms: the modeled historical decade, 1995-2004 (baseline), End-Century, the modeled decade 2085-2094 (future), Historical (1995-2004) to End-Century (2085-2094) (change), Historical, End-Century (corroborating_change)
- Scenario terms: Historical --- a modeled baseline, not an observation (baseline), RCP8.5 (future), Historical compared with RCP8.5 (change)
- On the place terms: The place terms are the stored label strings. Reading them as the names of places is `inferred_candidate` (IC-011, IC-012), and a name like `Lincoln` belongs to counties in many states.
- Generated query sentence: *increase in fire weather index in Oklahoma, Stephens under RCP8.5 by End-Century, the modeled decade 2085-2094*

This is what would be sent to retrieval. **Nothing has been sent.** No literature corpus exists in this repository, no index has been built, and no passage has been read. M3 is not authorised.

Full record: [`../artifacts/phenomena/prototypes/P-COUNTY-1.json`](../artifacts/phenomena/prototypes/P-COUNTY-1.json)

## P-STATE-1 --- state level

| Field | Value | Status |
| --- | --- | --- |
| `G` identifier | `California` | `inferred_candidate` |
| `G` members | 2831 cell(s); 2827 with a value, 4 without | `computed` |
| `H` variable | Heat Index, summer days above 105 F --- modeled historical to end-century RCP8.5 | `verified_from_dictionary` |
| `H` columns | 241 `heatindex_HIS_Day105` (baseline), 253 `heatindex_E85_Day105` (future) | per column, below |
| `V` change value | `13.209951652865228` | `derived_from_inferred` |
| `D` direction | **increase** | `derived_from_inferred` |
| `M` category | middle_third, percentile 54.0000 of 50 units | `provisional_rule` PR-1 |

Chosen by: the `State` label carried by the row `OID_` 14, M1-WP3's Example 2. No value was consulted in the choice.

### Generated description

> `Historical` here means a **modeled historical baseline** --- the dictionary's historical period, 1995 to 2004, run through the same climate models. It is not an observation, a measurement, or a record of anything that happened.

> The `State` and `NAME` values used to form this unit are `inferred_candidate` readings (IC-011, IC-012): the dictionary does not mention either column, and the Census vintage and coordinate reference system behind them are unknown. **This prototype groups rows by those labels**, which M1-WP3 deliberately did not do. The group is the set of rows carrying the label --- not a boundary, not a geometry, and not keyed on `GEOID`, which Phase A measured does not determine the label (A-G3).

> A cell with no value is written "no value in this file". It is **not** a zero, it is not counted in any mean, and this record does not claim it means anything else (Q16).

**Scope.** The set of rows sharing a `State` label, identified by [provisional: `California`]. Members: 2831 cell(s) --- 2827 with a value on every column used, 4 without. Cells without a value are excluded from every number below and are never read as a zero.

**Quantity.** Number of Summer days with daily max heat index above 105 F -- Historical. Unit or type: Number of. Season: Summer.

**Compared.** Baseline horizon Historical; future horizon End-Century; future scenario RCP8.5.

**Values.** Unweighted mean over n = 2827 member cell(s): `heatindex_HIS_Day105` [provisional: 2.152729629062611]; `heatindex_E85_Day105` [provisional: 15.362681281927839]. The complete per-cell values are in the record.

**Direction.** [provisional: increase], from the sign of the change value [provisional: 13.209951652865228], computed by `difference_of_horizon_values per cell, then unweighted_mean` over `heatindex_HIS_Day105`, `heatindex_E85_Day105`.

**Magnitude.** [provisional rule PR-1: middle_third, at percentile 54.0000 of 50 state-level units, by PR-1, which is a placeholder and not a scientific threshold].

Every clause marked [provisional:...] rests on an inferred-candidate record or on a field derived from one: reasoned and written down, **not verified and not owner-confirmed**. The clause marked [provisional rule PR-1:...] rests on a placeholder rule, not on science.

### What it depends on

Assumptions: `A1`, `A-G0`, `A-G1`, `A-G2`, `A-G3`, `A-AGG1`, `A-DIR1`, `A-M1`.

### Literature probe --- design stub, nothing sent

- Concept terms: heat index, days above 105 F, extreme heat days, humid heat
- Place terms: California (`State`, `inferred_candidate`)
- Direction term: increase
- Horizon terms: Historical (baseline), End-Century (future)
- Scenario terms: RCP8.5 (future)
- On the place terms: The place terms are the stored label strings. Reading them as the names of places is `inferred_candidate` (IC-011, IC-012), and a name like `Lincoln` belongs to counties in many states.
- Generated query sentence: *increase in heat index in California under RCP8.5 by End-Century*

This is what would be sent to retrieval. **Nothing has been sent.** No literature corpus exists in this repository, no index has been built, and no passage has been read. M3 is not authorised.

Full record: [`../artifacts/phenomena/prototypes/P-STATE-1.json`](../artifacts/phenomena/prototypes/P-STATE-1.json)
