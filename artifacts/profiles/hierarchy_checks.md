# Hierarchy checks --- computed structural properties

Produced by `scripts/hierarchy_checks.py` (M1-WP3b Phase A). Every value is a
string read from the file. **No meaning is assigned to any of them.** That a set
of rows shares a label is a fact about the table; that the set is a *county* is
an `inferred_candidate` reading (IC-011, IC-012) and is not established here.

- CSV SHA-256: `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e`
- Data rows: 62834

## 1. Is `Crossmodel` unique?

| Rows | Distinct `Crossmodel` | Unique | Duplicated values |
| ---: | ---: | :--- | ---: |
| 62834 | 62834 | **True** | 0 |

Uniqueness is a property of the column's characters. It does not establish that one row is one grid cell; that is assumption A-G0.

## 2. Rows per `(State, NAME)` pair

| Pairs | Min rows | Median rows | Max rows | Rows covered |
| ---: | ---: | ---: | ---: | ---: |
| 3019 | 1 | 12 | 2865 | 62834 |

- The pair of `OID_` 1: `Oklahoma` / `Stephens` --- 10 rows.
- The pair of `OID_` 14: `California` / `San Bernardino` --- 330 rows.

A `(State, NAME)` pair is a label shared by a set of rows. Whether that set is a county, and whether it covers a county completely, is not established here --- IC-011 and IC-012 hold both readings at `inferred_candidate`.

## 3. Rows per `GEOID`

| `GEOID` keys | Min rows | Median rows | Max rows | Rows covered |
| ---: | ---: | ---: | ---: | ---: |
| 12941 | 1 | 2 | 877 | 62834 |

- `GEOID` values spanning more than one `(State, NAME)` pair: **3234**.
- Each `GEOID` carries exactly one `(State, NAME)` pair: **False**.

## 4. Are `NAME_1` and `NAMELSAD` functions of `GEOID`?

Structural only. Neither column is in the pilot subset, neither is interpreted, and no prototype record uses either.

| Column | `GEOID` keys with more than one value | One value per `GEOID` |
| --- | ---: | :--- |
| 110 `NAME_1` | 0 | **True** |
| 111 `NAMELSAD` | 0 | **True** |

## 5. Rows with no `State` value

7 row(s).

| `OID_` | `Crossmodel` | `NAME` | `GEOID` |
| --- | --- | --- | --- |
| 5760 | `R179C497` | `District of Columbia` | `11001009603` |
| 6779 | `R179C495` | `District of Columbia` | `11001000300` |
| 13685 | `R180C496` | `District of Columbia` | `11001003600` |
| 21870 | `R180C495` | `District of Columbia` | `11001000600` |
| 33646 | `R178C496` | `District of Columbia` | `11001010900` |
| 38055 | `R179C496` | `District of Columbia` | `11001004001` |
| 41681 | `R180C497` | `District of Columbia` | `11001009601` |

An empty cell is "no value in this file". It is not a zero and not a claim that the row lies outside any state (Q16).

## 6. The row sets the Phase C prototypes are built from

| Row set | Rows |
| --- | ---: |
| `State` = `Oklahoma` (the state of `OID_` 1) | 1232 |
| `(State, NAME)` = `Oklahoma` / `Stephens` (the pair of `OID_` 1) | 10 |
| `State` = `California` (the state of `OID_` 14) | 2831 |

Pilot columns checked for emptiness: 41.

Across the state of `OID_` 1, **no pilot column has an empty value** on any of its 1232 rows.

Across the `(State, NAME)` pair of `OID_` 1, **no pilot column has an empty value** on any of its 10 rows.
