"""Prototype phenomenon records, schema version `p0-prototype`.

**Everything in this module is a prototype for scientific-object validation.
Nothing it produces is an accepted phenomenon record.** It was written for
M1-WP3b on Kaiyuan's decision of 2026-09-13, following the mentor's direction
R-002, ahead of the GUIDANCE ruling that would authorise it. That ruling came
back **PASS WITH ACTIONS** and is recorded as D-013, which admits M1-WP3b as an
explicit **milestone-order exception**: early M3-style validation carried out
while M1 is still open. Nothing built here is evidence for any milestone gate,
every record carries `validation_only` and says so in its own first line, and
the schema stays versioned `p0-prototype` so that adopting it is a visible act.

What a record is
----------------

A record describes **one unit** --- one grid cell, or one county-shaped row set,
or one state-shaped row set --- against **one variable**, and carries the
operations that produced every derived number. The tuple is

    G  scope          which rows, and at what level
    H  concept        which quantity, from which columns
    S  season         }
    T  time horizon   }  taken from the semantics of the columns used
    C  climate scenario }
    V  values         the raw strings, the operation, and the result
    D  direction      the sign of the change quantity
    M  magnitude      a tercile from provisional rule PR-1
    P  provenance     the status of every field above, one line each

Two conventions for the letters, and neither is settled
-------------------------------------------------------

The mentor and Kaiyuan read them as **S = season, T = time horizon, C = climate
scenario, P = provenance**. The M1-WP3b GUIDANCE ruling reads them as
**S = scenario, T = temporal horizon, C = compared quantity, P = provenance**.

The two agree on `P` and on everything a record carries; they disagree only on
which letter names the scenario, and on whether a letter names the season or the
compared quantity. **The code emits the mentor's letters**, because they are the
ones she has already seen, and every record carries
`SCHEMA_LETTER_CONVENTIONS` so that a reader meets both. D-013 records the pair
for the next GUIDANCE packet to settle. **No number depends on the choice.**

Five rules the code enforces
----------------------------

1. **Provenance carries through.** A field derived from an `inferred_candidate`
   column is `derived_from_inferred`. It never becomes stronger by being
   computed, and `unlabelled_inferred_text` fails the build if the generated
   description shows such a value outside a label.
2. **Every derived number names its operation and its inputs.** There is no
   field in a record whose provenance is "this module computed it somehow".
3. **`provisional_rule PR-1` is a placeholder, not a threshold.** It exists so
   that `M` is non-empty and the group has something to argue with. It is not a
   scientific magnitude criterion and the record says so in its own text.
4. **The three standing cautions apply to every generated sentence.** A Fire
   Weather Index is never a fire; a `Historical` value is a modeled baseline,
   never an observation; an empty cell is "no value in this file", never a zero.
5. **Some columns may not be averaged, and the aggregator refuses them.** A
   column whose dictionary type is "Percent Change" or "Text ID", and any column
   in the location family, is refused by `aggregate_column`. A record that needs
   to say something about such a column reports **counts**, never a mean.
   Required by the M1-WP3b ruling, criterion 7 (D-013).

What this module does not do
----------------------------

No literature retrieval, no embedding, no bridge, no QA. `literature_probe` is a
**design stub**: it assembles the terms a retrieval step *would* be given and
stops there. No row is ever selected, ordered or filtered by how large a value
is --- the three prototypes are chosen by identity, and PR-1 is applied after
the unit is fixed, never to choose it.
"""

from __future__ import annotations

import re
from decimal import (
    ROUND_CEILING,
    ROUND_HALF_EVEN,
    Decimal,
    InvalidOperation,
    localcontext,
)

from climrr.dictionary import INFERRED_CANDIDATE, VERIFIED_FROM_DICTIONARY
from climrr.examples import (
    FROM_DICTIONARY,
    FROM_INFERENCE,
    FROM_NOWHERE,
    NO_VALUE,
    PROVISIONAL_CLOSE,
    PROVISIONAL_OPEN,
    PROVISIONAL_RE,
    ExampleError,
    family_of,
)

SCHEMA_VERSION = "p0-prototype"

#: **Two conventions for the letters exist and neither is settled.** Recorded
#: side by side in every record's `P` field and in D-013 so that the next
#: GUIDANCE packet can choose one. Renaming changes labels and no number.
#:
#:   * **This schema, and the mentor's**: S = season, T = time horizon,
#:     C = climate scenario, P = provenance. These are the letters the mentor and
#:     Kaiyuan use, and they are what she has already seen, so they are what the
#:     code emits.
#:   * **The M1-WP3b ruling's**: S = scenario, T = temporal horizon,
#:     C = compared quantity, P = provenance.
#:
#: The two agree on P and on the *set* of things carried; they disagree on which
#: letter names the scenario and on whether a letter names the season or the
#: compared quantity. Nothing downstream reads a letter as a key to a meaning.
SCHEMA_LETTER_CONVENTIONS = (
    "Two conventions exist and neither is settled. This record uses the mentor's "
    "and Kaiyuan's: S = season, T = time horizon, C = climate scenario, "
    "P = provenance. The M1-WP3b GUIDANCE ruling uses S = scenario, "
    "T = temporal horizon, C = compared quantity, P = provenance. They agree on P "
    "and on what is carried, and differ on which letter names the scenario. The "
    "mentor's letters are emitted because they are the ones she has seen. D-013 "
    "records both for the next GUIDANCE packet to settle. No number depends on "
    "the choice."
)

#: Statuses this module adds to the three the pilot columns already carry.
#: `derived_from_inferred` is the one that matters: it is what a computed field
#: becomes when any input to it is an `inferred_candidate`.
DERIVED_FROM_VERIFIED = "derived_from_verified"
DERIVED_FROM_INFERRED = "derived_from_inferred"
PROVISIONAL_RULE = "provisional_rule"
COMPUTED = "computed"
UNKNOWN = "unknown"

#: What a value read straight out of the CSV is. Not a semantic status --- it
#: never enters `weakest()` --- but the description has to distinguish "these are
#: the file's digits" from "this number was computed from them". A raw value is
#: shown plainly; what it *means* is a separate clause with its own status.
RAW_VALUE = "raw_value_as_read"

#: Wrapper for the magnitude clause. Distinct from `[provisional: ...]` on
#: purpose --- a provisional *value* and a placeholder *rule* are different
#: kinds of weakness and a reader must be able to tell them apart.
PR1_OPEN = "[provisional rule PR-1: "
PR1_CLOSE = "]"

LEVELS = ("cell", "county", "state")

#: How a level's identity is formed. `county` and `state` are the **names of
#: row sets**, not geometries: A-G3. `GEOID` appears in none of them, because
#: Phase A measured that 3,234 `GEOID` values span more than one `(State, NAME)`
#: pair and so cannot key a county here.
LEVEL_KEYS = {
    "cell": (1,),
    "county": (3, 2),
    "state": (3,),
}

#: Provenance of the identifier at each level, and what it rests on.
LEVEL_IDENTIFIER_STATUS = {
    "cell": VERIFIED_FROM_DICTIONARY,
    "county": INFERRED_CANDIDATE,
    "state": INFERRED_CANDIDATE,
}

LEVEL_IDENTIFIER_RESTS_ON = {
    "cell": {
        "kind": "dictionary_span",
        "line": 455,
        "quote": (
            'Crossmodel Truncated name for "Crossmodel_CellName". Text ID for each cell '
            "in the polygon grid."
        ),
        "note": (
            "Phase A measured `Crossmodel` unique over all 62,834 rows. Uniqueness is a "
            "property of the characters; that the key names a grid cell is A-G0."
        ),
    },
    "county": {
        "kind": "inferred_candidate_records",
        "ids": ["IC-011", "IC-012"],
        "note": (
            "A county here is **the set of rows sharing a `(State, NAME)` label** and "
            "nothing else (A-G3). It is not a boundary, not a geometry, and not keyed on "
            "`GEOID`."
        ),
    },
    "state": {
        "kind": "inferred_candidate_records",
        "ids": ["IC-012"],
        "note": (
            "A state here is **the set of rows sharing a `State` label** and nothing else "
            "(A-G3)."
        ),
    },
}

#: The aggregation operations a record may report. `unweighted_mean` is the one
#: the derived fields use; the other three are reported beside it so a reader
#: can see the spread the mean is hiding.
OPERATIONS = ("unweighted_mean", "min", "max", "count")

#: Dictionary type markers that forbid an average, whatever the characters look
#: like. Required by the M1-WP3b ruling, criterion 7 (D-013).
#:
#: A **percent change** is a ratio. The mean of per-cell percent changes weights a
#: cell with a near-zero baseline as heavily as one with a large baseline, and it
#: is not the percent change of the aggregate. A **`Text ID`** is an identifier
#: and has no arithmetic at all.
UNMEANABLE_TYPE_MARKERS = ("Percent Change", "Text ID")

#: Why each marker forbids a mean, in the words a record will print.
UNMEANABLE_REASON = {
    "Percent Change": (
        "a percent change is a ratio, the mean of per-cell ratios weights a cell with a "
        "near-zero baseline as heavily as one with a large baseline, and it is not the "
        "percent change of the aggregate"
    ),
    "Text ID": "an identifier is not a quantity and has no arithmetic",
}

#: Pilot families whose columns are identifiers or categorical labels. Nothing in
#: one may be averaged. `X` and `Y` parse as decimals and their mean would be a
#: centroid this project has not defined, does not use, and could not justify
#: without the coordinate reference system it does not know.
UNMEANABLE_FAMILY_KEYS = ("location",)

#: The word for a sign, and the count that carries it. Used where a mean is
#: refused and a count has to say what the mean would have said.
SIGN_WORD = {"increase": "positive", "decrease": "negative", "no_change": "zero"}
SIGN_COUNT_KEY = {
    "increase": "n_positive",
    "decrease": "n_negative",
    "no_change": "n_zero",
}

#: The M1-WP3b ruling's **verbatim** label for an unweighted mean, required by
#: its evidence check 3 and required action 5: the mean is acceptable for these
#: three prototypes *only if labelled this way*. It travels beside every
#: `unweighted_mean` in a record, in the generated prose, and in both generated
#: documents, so a reader cannot meet the number without meeting the label.
#:
#: **Do not reword it.** The phrase is the ruling's, quoted, and a test asserts
#: it reaches the reader unchanged.
PROVISIONAL_AGGREGATION_LABEL = (
    "provisional aggregation rule for representation validation"
)

#: Where the label comes from, carried beside it so it is checkable.
PROVISIONAL_AGGREGATION_LABEL_SOURCE = (
    "M1-WP3b GUIDANCE ruling, evidence check 3 and required action 5 (D-013)"
)

#: Stamped on every record and at the head of every generated page (D-013).
VALIDATION_BANNER = (
    "**Prototype for scientific-object validation. Not an accepted phenomenon record.**"
)

#: The operation that produces a per-cell change value.
CHANGE_FROM_COLUMN = "change_column_value"
CHANGE_FROM_DIFFERENCE = "difference_of_horizon_values"

DIRECTIONS = ("increase", "decrease", "no_change")

#: The two pilot variables Phase C builds on. `label` is a heading, used in the
#: tables and **never in a generated description** --- descriptions are built
#: from the recorded semantics of the columns, so that no hand-written phrase
#: about what a column holds can reach the mentor through the prose.
VARIABLES = (
    {
        "key": "fwi_summer_hist_to_end85",
        "family_key": "fire_weather",
        "label": (
            "Fire Weather Index, summer --- modeled historical to end-century RCP8.5"
        ),
        "baseline_index": 189,
        "future_index": 191,
        "change_index": 193,
        "corroborating_change_index": 195,
        "change_operation": CHANGE_FROM_COLUMN,
        "change_choice_note": (
            "Two change columns exist for this variable and the work package allows "
            "either. `wildfire_summer_Dend` (193) is used because it is an absolute "
            "difference, and the unweighted mean of per-cell differences is the "
            "difference of the per-cell means --- an arithmetic property that the mean "
            "of per-cell **percent** changes does not have. `wildfire_summer_Pend` "
            "(195) is `verified_from_dictionary` and is reported beside it as a "
            "corroborating sign, not as the quantity. Which of the two should carry the "
            "direction is assumption A-DIR2 and is an open choice for the group."
        ),
        "concept_terms": ("fire weather index", "FWI", "fire weather", "fire danger"),
    },
    {
        "key": "heatindex_day105_summer_hist_to_end85",
        "family_key": "heat_index",
        "label": (
            "Heat Index, summer days above 105 F --- modeled historical to end-century RCP8.5"
        ),
        "baseline_index": 241,
        "future_index": 253,
        "change_index": None,
        "corroborating_change_index": None,
        "change_operation": CHANGE_FROM_DIFFERENCE,
        "change_choice_note": (
            "No change column for this variable is in the pilot subset, so the change is "
            "computed as index 253 minus index 241. Both inputs are "
            "`verified_from_dictionary`; the **direction of the subtraction** is "
            "assumption A-DIR1."
        ),
        "concept_terms": (
            "heat index",
            "days above 105 F",
            "extreme heat days",
            "humid heat",
        ),
    },
)


class PhenomenonError(RuntimeError):
    """A record cannot be built from what was supplied. Never silently patched."""


def variable_of(key: str) -> dict:
    for variable in VARIABLES:
        if variable["key"] == key:
            return variable
    raise PhenomenonError(f"no variable named {key!r}")


def columns_used(variable: dict) -> tuple[int, ...]:
    """Every column index a record for this variable reads, in file order."""
    indices = [variable["baseline_index"], variable["future_index"]]
    for key in ("change_index", "corroborating_change_index"):
        if variable[key] is not None:
            indices.append(variable[key])
    return tuple(sorted(indices))


def role_of(variable: dict, index: int) -> str:
    for role, key in (
        ("baseline", "baseline_index"),
        ("future", "future_index"),
        ("change", "change_index"),
        ("corroborating_change", "corroborating_change_index"),
    ):
        if variable[key] == index:
            return role
    raise PhenomenonError(f"column {index} has no role in variable {variable['key']!r}")


# --- arithmetic ---------------------------------------------------------------
#
# Decimal throughout, from the raw strings, so that the values in a record are
# the file's digits and not a binary float's nearest approximation to them.
# Every result is stored as `str(Decimal)`.

#: Working precision. Well above the 17-18 significant digits the file stores,
#: so a mean over 2,831 cells does not lose the digits it was given.
PRECISION = 50

#: Decimal places every derived number is rounded to, and the rounding mode.
#:
#: The file stores 15 decimal places. A mean carried at the working precision
#: would print fifty of them, which claims a precision the inputs do not have,
#: so every derived value --- a mean, a difference of means, a change value ---
#: is quantised back to the precision the source is written at. The rounding
#: happens **once**, inside `mean_from_total`, so that a value accumulated while
#: streaming and the same value recomputed from a retained list are the same
#: digits, and a unit ranks against its own distribution consistently.
DERIVED_DECIMAL_PLACES = 15
ROUNDING_MODE = ROUND_HALF_EVEN
ROUNDING_RULE = (
    f"every derived value is rounded to {DERIVED_DECIMAL_PLACES} decimal places, "
    "half-to-even --- the precision the CSV itself stores. Raw values are never "
    "rounded: they are reported as the characters the file holds."
)

#: Decimal places a PR-1 percentile is reported to.
PERCENTILE_DECIMAL_PLACES = 4


def dstr(value: Decimal) -> str:
    """A Decimal as plain digits, never in exponent notation.

    `str(Decimal("0E-15"))` is `"0E-15"`, which is the correct value and an
    unreadable one in a record a mentor is meant to check by eye. Every Decimal
    that becomes a string in this module goes through here.
    """
    return f"{value:f}"


def quantise_derived(value: Decimal) -> Decimal:
    """Round a derived value to the file's own precision. See ROUNDING_RULE."""
    with localcontext() as ctx:
        ctx.prec = PRECISION
        return value.quantize(
            Decimal(1).scaleb(-DERIVED_DECIMAL_PLACES), rounding=ROUNDING_MODE
        )


def to_decimal(raw: str, *, index: int) -> Decimal:
    try:
        return Decimal(raw)
    except (InvalidOperation, ValueError) as exc:
        raise PhenomenonError(
            f"column {index} holds {raw!r}, which is not a decimal number. This is a "
            "finding about the data; stop and report."
        ) from exc


def mean_from_total(total: Decimal, count: int) -> Decimal:
    """A mean from a running sum, at the module's precision.

    Split out so that a value accumulated while streaming and the same value
    recomputed from a retained list agree digit for digit. A record's change
    value and its entry in the distribution PR-1 ranks it against are produced
    by these two paths, and a precision difference between them would put a unit
    at the wrong percentile against itself.
    """
    if not count:
        raise PhenomenonError("a mean of no values; the caller must handle n = 0")
    with localcontext() as ctx:
        ctx.prec = PRECISION
        mean = total / Decimal(count)
    return quantise_derived(mean)


def unweighted_mean(values: list[Decimal]) -> Decimal:
    """The plain arithmetic mean. Every member counts once --- assumptions A-G2, A-AGG1."""
    if not values:
        raise PhenomenonError("unweighted_mean of no values; the caller must handle n = 0")
    with localcontext() as ctx:
        ctx.prec = PRECISION
        total = sum(values, Decimal(0))
    return mean_from_total(total, len(values))


def refuse_to_mean(entry: dict) -> str | None:
    """Why this column may not be averaged over cells, or `None` if it may be.

    Decided from the column's **recorded semantics** --- the dictionary type it
    carries, and the pilot family it belongs to --- and never from its name or
    from what its characters look like. `wildfire_summer_Pend` is refused because
    the dictionary writes "Percent Change" against it, which is the same fact that
    made the column `verified_from_dictionary` in the first place.
    """
    unit = (entry.get("unit") or {}).get("value") or ""
    for marker in UNMEANABLE_TYPE_MARKERS:
        if marker in unit:
            return (
                f'its recorded type is "{marker}" --- '
                f"{UNMEANABLE_REASON[marker]}. The M1-WP3b ruling forbids taking a mean "
                "of it (criterion 7)"
            )
    family = family_of(entry["index"])
    if family["key"] in UNMEANABLE_FAMILY_KEYS:
        return (
            f"it belongs to the {family['label']!r} family, whose columns are "
            "identifiers and categorical labels rather than quantities"
        )
    return None


def aggregate(values: list[Decimal]) -> dict:
    """All four reportable operations over one column's member values."""
    return {
        "unweighted_mean": dstr(unweighted_mean(values)),
        "unweighted_mean_label": PROVISIONAL_AGGREGATION_LABEL,
        "unweighted_mean_label_source": PROVISIONAL_AGGREGATION_LABEL_SOURCE,
        "min": dstr(min(values)),
        "max": dstr(max(values)),
        "count": str(len(values)),
    }


def aggregate_column(entry: dict, values: list[Decimal]) -> dict:
    """`aggregate`, but it refuses columns that must not be averaged.

    This is the aggregator's gate. A caller that wants a summary of a refused
    column has to ask for something other than a mean --- `sign_counts` is what
    the records use --- rather than reaching past this function.
    """
    reason = refuse_to_mean(entry)
    if reason is not None:
        raise PhenomenonError(
            f"column {entry['index']} `{entry['column']}` may not be averaged: {reason}"
        )
    return aggregate(values)


def sign_counts(values: list[Decimal]) -> dict:
    """How many member cells are positive, negative and zero.

    What a record reports where a mean is refused. A count of signs makes no
    arithmetic claim about the quantity and is checkable against the per-cell
    values the record also carries.
    """
    return {
        "n": str(len(values)),
        "n_positive": str(sum(1 for value in values if value > 0)),
        "n_negative": str(sum(1 for value in values if value < 0)),
        "n_zero": str(sum(1 for value in values if value == 0)),
    }


def direction_of(change: Decimal) -> str:
    if change > 0:
        return "increase"
    if change < 0:
        return "decrease"
    return "no_change"


# --- provisional rule PR-1 ----------------------------------------------------

#: The whole of PR-1, written out so that it travels with every record that uses
#: it. It is a placeholder that makes `M` non-empty. It is not a scientific
#: threshold, it was not derived from any literature, and no part of this
#: project treats a tercile as meaning anything.
PR1_STATEMENT = (
    "provisional_rule PR-1 --- rank this unit's change value against the change "
    "values of **all units at the same level for the same variable**, and report "
    "the percentile and the tercile it falls in. The percentile is "
    "100 x (units with a strictly smaller change value) / (units with a change "
    "value). The terciles cut at the 100/3 and 200/3 percentile marks. "
    "**PR-1 is a placeholder chosen to make this field non-empty, not a "
    "scientific magnitude threshold.** It rests on no literature, no distribution "
    "assumption and no physical reasoning, and assumption A-M1 records that."
)

PR1_TERCILES = ("lower_third", "middle_third", "upper_third")

#: What PR-1 ranks. Required by the M1-WP3b ruling, action 10 / criterion 10.
#:
#: Stated in every `M` field because the two readings give different answers: a
#: large decrease is at the **bottom** of a signed ranking and near the **top** of
#: an absolute one, and a reader who assumes the wrong one reads "lower_third" as
#: "little happened" when it may mean "the largest decrease in the file".
PR1_RANKED_ON = (
    "the **signed** change value. The sign is kept, so a decrease ranks below a "
    "no-change and a no-change below an increase. PR-1 does **not** rank on "
    "absolute magnitude, and a unit in the lower third may be one with a large "
    "decrease rather than one where little changed."
)

#: Quantile method, named because a different one gives different numbers.
QUANTILE_METHOD = (
    "nearest-rank on the sorted values: the p-th percentile is the value at "
    "1-based position ceil(p/100 x n), with the 0th percentile the minimum"
)


def _nearest_rank(sorted_values: list[Decimal], percent: Decimal) -> Decimal:
    n = len(sorted_values)
    if n == 0:
        raise PhenomenonError("no values to take a quantile of")
    # Decimal's `//` truncates toward zero rather than flooring, so the usual
    # `-(-a // b)` ceiling trick is wrong here. Ask for the ceiling directly.
    with localcontext() as ctx:
        ctx.prec = PRECISION
        exact = percent * Decimal(n) / Decimal(100)
    position = int(exact.to_integral_value(rounding=ROUND_CEILING))
    return sorted_values[max(0, min(n - 1, position - 1))]


def distribution_summary(sorted_values: list[Decimal]) -> dict:
    """n, min, quartiles and max of a level's change values. Strings throughout."""
    return {
        "n": str(len(sorted_values)),
        "min": dstr(sorted_values[0]),
        "q1": dstr(_nearest_rank(sorted_values, Decimal(25))),
        "median": dstr(_nearest_rank(sorted_values, Decimal(50))),
        "q3": dstr(_nearest_rank(sorted_values, Decimal(75))),
        "max": dstr(sorted_values[-1]),
        "quantile_method": QUANTILE_METHOD,
    }


def tercile_of(percentile: Decimal) -> str:
    with localcontext() as ctx:
        ctx.prec = PRECISION
        third = Decimal(100) / Decimal(3)
        if percentile < third:
            return "lower_third"
        if percentile < third * 2:
            return "middle_third"
        return "upper_third"


def apply_pr1(change: Decimal, sorted_values: list[Decimal]) -> dict:
    """PR-1 for one unit against its level's distribution."""
    n = len(sorted_values)
    if n == 0:
        raise PhenomenonError("PR-1 needs a non-empty distribution to rank against")
    below = sum(1 for value in sorted_values if value < change)
    equal = sum(1 for value in sorted_values if value == change)
    with localcontext() as ctx:
        ctx.prec = PRECISION
        percentile = (Decimal(100) * Decimal(below) / Decimal(n)).quantize(
            Decimal(1).scaleb(-PERCENTILE_DECIMAL_PLACES), rounding=ROUNDING_MODE
        )
    return {
        "rule": "PR-1",
        "rule_statement": PR1_STATEMENT,
        "is_a_scientific_threshold": "no",
        "change_value": dstr(change),
        "n_units_at_this_level": str(n),
        "n_units_strictly_below": str(below),
        "n_units_equal": str(equal),
        "ranked_on": PR1_RANKED_ON,
        "percentile": dstr(percentile),
        "percentile_definition": (
            "100 x (units strictly below) / (units with a change value), rounded to "
            f"{PERCENTILE_DECIMAL_PLACES} decimal places"
        ),
        "tercile": tercile_of(percentile),
        "distribution": distribution_summary(sorted_values),
        "provenance_status": PROVISIONAL_RULE,
    }


# --- the semantic attribute blocks (S, T, C) ----------------------------------

#: An attribute's own status, from its own provenance --- finer than the
#: column's status, because an IC-record can quote the dictionary for a
#: scenario while inferring the unit.
_PROVENANCE_TO_STATUS = {
    FROM_DICTIONARY: VERIFIED_FROM_DICTIONARY,
    FROM_INFERENCE: INFERRED_CANDIDATE,
    FROM_NOWHERE: UNKNOWN,
}


def _attribute_block(entry: dict, key: str) -> dict:
    attribute = entry[key]
    return {
        "index": entry["index"],
        "column": entry["column"],
        "value": attribute["value"],
        "provenance": attribute["provenance"],
        "status": _PROVENANCE_TO_STATUS[attribute["provenance"]],
    }


def semantic_block(letter: str, label: str, reading: str, entries: dict, key: str) -> dict:
    """One of S, T, C: the attribute per column role, each with its own status."""
    per_role = {role: _attribute_block(entry, key) for role, entry in entries.items()}
    statuses = {block["status"] for block in per_role.values()}
    return {
        "letter": letter,
        "label": label,
        "letter_reading_is_this_modules": reading,
        "per_role": per_role,
        "status": (
            statuses.pop() if len(statuses) == 1 else "mixed --- see per_role"
        ),
    }


def weakest(statuses) -> str:
    """The status a derived field inherits: the weakest of everything it reads.

    Order, strongest first: `verified_from_dictionary`, `derived_from_verified`,
    `inferred_candidate`, `derived_from_inferred`, `unknown`. A derived field
    can never be stronger than its weakest input, which is the whole of the
    provenance discipline in one function.
    """
    order = [
        VERIFIED_FROM_DICTIONARY,
        DERIVED_FROM_VERIFIED,
        INFERRED_CANDIDATE,
        DERIVED_FROM_INFERRED,
        UNKNOWN,
    ]
    worst = VERIFIED_FROM_DICTIONARY
    for status in statuses:
        if status not in order:
            raise PhenomenonError(f"unknown status {status!r}")
        if order.index(status) > order.index(worst):
            worst = status
    return worst


def derived_status(input_statuses) -> str:
    """What a computed field becomes, given the statuses of its inputs."""
    worst = weakest(input_statuses)
    if worst in (INFERRED_CANDIDATE, DERIVED_FROM_INFERRED, UNKNOWN):
        return DERIVED_FROM_INFERRED
    return DERIVED_FROM_VERIFIED


# --- standing cautions --------------------------------------------------------
#
# Emitted when, and only when, something in *this* record triggers them. Each
# names what triggered it, exactly as the M1-WP3 example records do.

#: The location caution for a **prototype**, which is not the M1-WP3 one.
#: `climrr.examples` ends its location caution with "no part of this pilot groups
#: rows by any of them", and that sentence was true of M1-WP3 and is false here.
#: WP3b groups rows by `State` and `NAME` deliberately, so the caution has to say
#: so rather than be quoted across unchanged.
LOCATION_CAUTION = (
    "The `State` and `NAME` values used to form this unit are `inferred_candidate` "
    "readings (IC-011, IC-012): the dictionary does not mention either column, and "
    "the Census vintage and coordinate reference system behind them are unknown. "
    "**This prototype groups rows by those labels**, which M1-WP3 deliberately did "
    "not do. The group is the set of rows carrying the label --- not a boundary, not "
    "a geometry, and not keyed on `GEOID`, which Phase A measured does not "
    "determine the label (A-G3)."
)

HISTORICAL_CAUTION = (
    "`Historical` here means a **modeled historical baseline** --- the dictionary's "
    "historical period, 1995 to 2004, run through the same climate models. It is "
    "not an observation, a measurement, or a record of anything that happened."
)

BLANK_CAUTION = (
    f'A cell with no value is written "{NO_VALUE}". It is **not** a zero, it is not '
    "counted in any mean, and this record does not claim it means anything else (Q16)."
)


def build_cautions(*, variable: dict, level: str, n_cells_empty: int) -> list[dict]:
    family = family_of(variable["baseline_index"])
    cautions = []
    if family["caution"] is not None:
        cautions.append(
            {
                "id": f"C-{family['key']}",
                "text": family["caution"],
                "span": family["caution_span"],
                "triggered_by": f"the family of the columns used: {family['label']}",
            }
        )
    cautions.append(
        {
            "id": "C-historical",
            "text": HISTORICAL_CAUTION,
            "span": {
                "line": 102,
                "quote": (
                    "2094). A historical period (1995 to 2004) is also modeled using GHG "
                    "concentrations during this period."
                ),
            },
            "triggered_by": (
                f"the baseline column of this variable, index {variable['baseline_index']}"
            ),
        }
    )
    if level in ("county", "state"):
        cautions.append(
            {
                "id": "C-location-grouping",
                "text": LOCATION_CAUTION,
                "span": None,
                "triggered_by": f"the unit level {level!r}, whose identifier is a label",
            }
        )
    if n_cells_empty:
        cautions.append(
            {
                "id": "C-blank",
                "text": BLANK_CAUTION,
                "span": None,
                "triggered_by": (
                    f"{n_cells_empty} member cell(s) with no value on at least one column used"
                ),
            }
        )
    return cautions


# --- the record ---------------------------------------------------------------


def change_input_indices(variable: dict) -> tuple[int, ...]:
    """The columns the change value is computed from --- one, or two.

    `CHANGE_FROM_COLUMN` reads the change straight out of a column.
    `CHANGE_FROM_DIFFERENCE` subtracts the baseline column from the future one,
    which is where assumption A-DIR1 enters.
    """
    if variable["change_operation"] == CHANGE_FROM_COLUMN:
        return (variable["change_index"],)
    return (variable["baseline_index"], variable["future_index"])


def change_value_of(member: dict, variable: dict) -> Decimal:
    """One member cell's change value, by the operation the variable declares."""
    values = member["values"]
    if variable["change_operation"] == CHANGE_FROM_COLUMN:
        index = variable["change_index"]
        return quantise_derived(to_decimal(values[index], index=index))
    baseline = to_decimal(values[variable["baseline_index"]], index=variable["baseline_index"])
    future = to_decimal(values[variable["future_index"]], index=variable["future_index"])
    return quantise_derived(future - baseline)


def has_all_values(member: dict, variable: dict) -> bool:
    return all(member["values"][index] != "" for index in columns_used(variable))


def _aggregate_entry(entry: dict, variable: dict, usable: list[dict]) -> dict:
    """One column's block inside an aggregate record's `V`.

    A column the aggregator refuses keeps every per-cell value and reports
    **counts** instead of a mean. `aggregates` is `None` there rather than
    absent, so a reader scanning the field cannot mistake a refusal for an
    oversight.
    """
    index = entry["index"]
    values = [to_decimal(member["values"][index], index=index) for member in usable]
    block = {
        "index": index,
        "column": entry["column"],
        "role": role_of(variable, index),
        "per_cell_raw_values": [member["values"][index] for member in usable],
        "per_cell_raw_values_are_complete": (
            "yes --- every member cell with a value, not a sample"
        ),
    }
    reason = refuse_to_mean(entry)
    if reason is None:
        block["aggregates"] = aggregate_column(entry, values)
        block["not_averaged"] = None
        return block
    block["aggregates"] = None
    block["not_averaged"] = {
        "reason": reason,
        "reported_instead": "counts of sign over the member cells, and the per-cell values",
        **sign_counts(values),
    }
    return block


def build_record(
    *,
    record_id: str,
    level: str,
    identifier: dict,
    members: list[dict],
    variable: dict,
    semantics_by_index: dict[int, dict],
    sorted_change_values: list[Decimal],
    distribution_membership: dict,
    built_from_commit: str,
    csv_sha256: str,
    assumption_ids: list[str],
) -> dict:
    """One prototype record. Every derived field names its operation and inputs."""
    if level not in LEVELS:
        raise PhenomenonError(f"level {level!r} is not one of {LEVELS}")
    if not members:
        raise PhenomenonError(
            f"{record_id}: the unit has no member rows. That is a finding, not an "
            "empty result; stop and report."
        )
    if level == "cell" and len(members) != 1:
        raise PhenomenonError(
            f"{record_id}: a cell-level unit has {len(members)} members. `Crossmodel` was "
            "measured unique in Phase A, so this is a defect; stop and report."
        )

    used = columns_used(variable)
    usable = [member for member in members if has_all_values(member, variable)]
    n_cells_empty = len(members) - len(usable)
    if not usable:
        raise PhenomenonError(
            f"{record_id}: no member cell has a value on every column used. Stop and report."
        )

    identifier_status = LEVEL_IDENTIFIER_STATUS[level]
    entries = {role_of(variable, index): semantics_by_index[index] for index in used}

    # --- G ---------------------------------------------------------------
    g_block = {
        "letter": "G",
        "label": "scope",
        "level": level,
        "identifier": identifier,
        "identifier_columns": [
            {"index": index, "column": semantics_by_index[index]["column"]}
            if index in semantics_by_index
            else {"index": index, "column": None}
            for index in LEVEL_KEYS[level]
        ],
        "member_cells": [member["crossmodel"] for member in members],
        "member_cells_are_complete": "yes --- every row carrying the identifier, not a sample",
        "n_cells": str(len(members)),
        "n_cells_with_value": str(len(usable)),
        "n_cells_empty": str(n_cells_empty),
        "provenance_status": identifier_status,
        "rests_on": LEVEL_IDENTIFIER_RESTS_ON[level],
    }

    # --- H ---------------------------------------------------------------
    family = family_of(variable["baseline_index"])
    h_block = {
        "letter": "H",
        "label": "concept",
        "family": family["label"],
        "family_key": family["key"],
        "variable_key": variable["key"],
        "variable_label": variable["label"],
        "variable_label_is_a_heading_only": (
            "used in tables and never in the generated description, which is built "
            "from the recorded semantics of the columns"
        ),
        "columns": [
            {
                "index": index,
                "column": semantics_by_index[index]["column"],
                "role": role_of(variable, index),
                "status": semantics_by_index[index]["status"],
                "meaning": semantics_by_index[index]["meaning"]["value"],
                "meaning_status": _PROVENANCE_TO_STATUS[
                    semantics_by_index[index]["meaning"]["provenance"]
                ],
                "unit": semantics_by_index[index]["unit"]["value"],
                "unit_status": _PROVENANCE_TO_STATUS[
                    semantics_by_index[index]["unit"]["provenance"]
                ],
                "rests_on": semantics_by_index[index]["rests_on"],
            }
            for index in used
        ],
        "provenance_status": weakest(
            semantics_by_index[index]["status"] for index in used
        ),
    }

    # --- S, T, C ---------------------------------------------------------
    s_block = semantic_block(
        "S",
        "season",
        "S is read as season; the work package names the letter without defining it",
        entries,
        "season",
    )
    t_block = semantic_block(
        "T",
        "time horizon",
        "T is read as time horizon",
        entries,
        "horizon",
    )
    c_block = semantic_block(
        "C",
        "climate scenario",
        "C is read as climate scenario (the RCP pathway)",
        entries,
        "scenario",
    )

    # --- V ---------------------------------------------------------------
    per_cell_changes = [change_value_of(member, variable) for member in usable]
    if level == "cell":
        unit_change = per_cell_changes[0]
        change_operation = variable["change_operation"]
        v_values = {
            "kind": "raw_values_of_one_cell",
            "per_column": [
                {
                    "index": index,
                    "column": semantics_by_index[index]["column"],
                    "role": role_of(variable, index),
                    "raw_value": usable[0]["values"][index],
                }
                for index in used
            ],
        }
    else:
        unit_change = unweighted_mean(per_cell_changes)
        change_operation = (
            f"{variable['change_operation']} per cell, then unweighted_mean "
            f"({PROVISIONAL_AGGREGATION_LABEL})"
        )
        v_values = {
            "kind": "aggregate_over_member_cells",
            "operation": "unweighted_mean",
            "operation_label": PROVISIONAL_AGGREGATION_LABEL,
            "operation_label_source": PROVISIONAL_AGGREGATION_LABEL_SOURCE,
            "operations_reported": list(OPERATIONS),
            "n": str(len(usable)),
            "per_column": [
                _aggregate_entry(semantics_by_index[index], variable, usable)
                for index in used
            ],
            "columns_not_averaged": [
                {
                    "index": index,
                    "column": semantics_by_index[index]["column"],
                    "reason": refuse_to_mean(semantics_by_index[index]),
                }
                for index in used
                if refuse_to_mean(semantics_by_index[index]) is not None
            ],
        }
    v_block = {
        "letter": "V",
        "label": "values",
        **v_values,
        "change": {
            "operation": change_operation,
            "operation_note": variable["change_choice_note"],
            "input_columns": [
                {
                    "index": index,
                    "column": semantics_by_index[index]["column"],
                    "role": role_of(variable, index),
                }
                for index in change_input_indices(variable)
            ],
            "per_cell_change_values": [dstr(value) for value in per_cell_changes],
            "value": dstr(unit_change),
            "n": str(len(usable)),
            "rests_on_assumptions": ["A-AGG1", "A-G2"] if level != "cell" else [],
        },
        "rests_on_assumptions": ["A-AGG1", "A-G2"] if level != "cell" else [],
    }

    # --- D ---------------------------------------------------------------
    change_input_statuses = [identifier_status]
    if variable["change_operation"] == CHANGE_FROM_COLUMN:
        change_input_statuses.append(semantics_by_index[variable["change_index"]]["status"])
    else:
        change_input_statuses.append(semantics_by_index[variable["baseline_index"]]["status"])
        change_input_statuses.append(semantics_by_index[variable["future_index"]]["status"])
    d_status = derived_status(change_input_statuses)

    # Corroboration is a **count of signs**, never an average. The corroborating
    # column is a percent change, which `refuse_to_mean` refuses, and the
    # M1-WP3b ruling (criterion 7) is explicit that it must not be averaged. A
    # count says what the mean was reached for --- does the second column agree
    # about the direction --- and says it per cell, where it is checkable.
    corroborating = None
    corroborating_index = variable["corroborating_change_index"]
    if corroborating_index is not None:
        entry = semantics_by_index[corroborating_index]
        values = [
            to_decimal(member["values"][corroborating_index], index=corroborating_index)
            for member in usable
        ]
        counts = sign_counts(values)
        direction = direction_of(unit_change)
        agreeing = counts[SIGN_COUNT_KEY[direction]]
        corroborating = {
            "index": corroborating_index,
            "column": entry["column"],
            "status": entry["status"],
            "not_averaged": refuse_to_mean(entry),
            "unit_direction": direction,
            "sign_word": SIGN_WORD[direction],
            "n_member_cells_with_that_sign": agreeing,
            "of_n_member_cells": counts["n"],
            "agrees_on_every_member_cell": str(agreeing == counts["n"]),
            **counts,
            "provenance_status": derived_status([identifier_status, entry["status"]]),
            "note": (
                "A count of per-cell signs, not a quantity and not an average. A cell "
                "disagreeing with the unit's direction is not an error; a systematic "
                "disagreement would be a finding to escalate."
            ),
        }

    d_block = {
        "letter": "D",
        "label": "direction",
        "direction": direction_of(unit_change),
        "from": "the sign of the change value in V",
        "change_value": dstr(unit_change),
        "input_columns": v_block["change"]["input_columns"],
        "provenance_status": d_status,
        "rests_on_assumptions": ["A-DIR1"]
        + (["A-DIR2"] if corroborating_index is not None else [])
        + (["A-G1", "A-G3", "A-AGG1"] if level != "cell" else []),
        "corroborating": corroborating,
    }

    # --- M ---------------------------------------------------------------
    m_block = {
        "letter": "M",
        "label": "magnitude category",
        **apply_pr1(unit_change, sorted_change_values),
        "ranked_against": (
            f"every {level}-level unit of this file with a change value for variable "
            f"{variable['key']}"
        ),
        "reference_population": distribution_membership.get(
            "reference_population",
            "not supplied by the caller --- this is a defect, not an empty field",
        ),
        "distribution_membership": distribution_membership,
        "rests_on_assumptions": ["A-M1"] + d_block["rests_on_assumptions"],
    }

    cautions = build_cautions(
        variable=variable, level=level, n_cells_empty=n_cells_empty
    )

    record = {
        "schema_version": SCHEMA_VERSION,
        "record_id": record_id,
        "validation_only": True,
        "validation_banner": VALIDATION_BANNER,
        "prototype_notice": (
            "PROTOTYPE. Built for M1-WP3b on Kaiyuan's decision of 2026-09-13, ahead of "
            "the GUIDANCE ruling that would authorise county/state units, aggregation "
            "and a magnitude field. It is not evidence for any milestone gate and may "
            "be revised or discarded by that ruling."
        ),
        "built_from_commit": built_from_commit,
        "csv_sha256": csv_sha256,
        "rounding_rule": ROUNDING_RULE,
        "G": g_block,
        "H": h_block,
        "S": s_block,
        "T": t_block,
        "C": c_block,
        "V": v_block,
        "D": d_block,
        "M": m_block,
        "assumptions": list(assumption_ids),
        "cautions": cautions,
    }
    rendered = render_description(record)
    record["description"] = rendered["text"]
    record["description_clauses"] = rendered["clauses"]
    record["description_generated_by"] = (
        "template in climrr.phenomenon.render_description, from fields G through M"
    )
    record["P"] = {
        "letter": "P",
        "label": "provenance",
        "letter_reading_note": SCHEMA_LETTER_CONVENTIONS,
        "per_field": provenance_statuses(record),
    }
    record["literature_probe"] = build_probe(record, variable)
    return record


def provenance_statuses(record: dict) -> dict:
    """The per-field map. One line per field a reader could quote out of context."""
    return {
        "G.level": COMPUTED,
        "G.identifier": record["G"]["provenance_status"],
        "G.member_cells": COMPUTED,
        "G.n_cells": COMPUTED,
        "G.n_cells_with_value": COMPUTED,
        "H.concept": record["H"]["provenance_status"],
        **{
            f"H.columns[{column['index']}].meaning": column["meaning_status"]
            for column in record["H"]["columns"]
        },
        **{
            f"H.columns[{column['index']}].unit": column["unit_status"]
            for column in record["H"]["columns"]
        },
        "S.season": record["S"]["status"],
        "T.horizon": record["T"]["status"],
        "C.scenario": record["C"]["status"],
        "V.values": COMPUTED,
        "V.change": record["D"]["provenance_status"],
        "D.direction": record["D"]["provenance_status"],
        "M.percentile": PROVISIONAL_RULE,
        "M.tercile": PROVISIONAL_RULE,
        "description": "generated from the fields above by template",
        "literature_probe": "design stub --- no retrieval has been performed",
    }


# --- the generated description -------------------------------------------------
#
# Every sentence is assembled from a record field. Nothing in here is a
# hand-written statement about a unit, a column or a number, and the connective
# scaffolding ("Scope ---", "Direction ---") says nothing that could be right or
# wrong. If this template ever needs a sentence that no field supports, that is a
# defect to escalate and not a string to add.

#: Statuses whose text must be shown inside `[provisional: ...]`.
WEAK_STATUSES = frozenset(
    {INFERRED_CANDIDATE, DERIVED_FROM_INFERRED, UNKNOWN}
)

#: Written with their own capitals: these phrases contain column names, and
#: case-folding a sentence must never reach into `(State, NAME)`.
LEVEL_PHRASE = {
    "cell": "One grid cell",
    "county": "The set of rows sharing a `(State, NAME)` label",
    "state": "The set of rows sharing a `State` label",
}


class _Clauses:
    """Collects what the template rendered, so the guard can check it exactly."""

    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, field: str, text: str | None, status: str) -> str:
        if text is None:
            rendered = NO_VALUE
            self.items.append(
                {"field": field, "text": rendered, "status": UNKNOWN, "wrapper": "none"}
            )
            return rendered
        if "[" in text or "]" in text:
            raise PhenomenonError(
                f"{field}: a value contains a square bracket and cannot be labelled "
                f"unambiguously: {text!r}"
            )
        if status == PROVISIONAL_RULE:
            rendered = f"{PR1_OPEN}{text}{PR1_CLOSE}"
            wrapper = "provisional_rule"
        elif status in WEAK_STATUSES:
            rendered = f"{PROVISIONAL_OPEN}{text}{PROVISIONAL_CLOSE}"
            wrapper = "provisional"
        else:
            rendered = text
            wrapper = "none"
        self.items.append(
            {"field": field, "text": text, "status": status, "wrapper": wrapper}
        )
        return rendered


def _identifier_text(record: dict) -> str:
    identifier = record["G"]["identifier"]
    return ", ".join(f"`{value}`" for value in identifier.values())


def render_description(record: dict) -> dict:
    """The prose, and the manifest of clauses it was built from."""
    clauses = _Clauses()
    g, h, s, t, c, v, d, m = (record[key] for key in "GHSTCVDM")
    roles = {column["role"]: column for column in h["columns"]}
    baseline, future = roles["baseline"], roles["future"]

    scope = clauses.add("G.identifier", _identifier_text(record), g["provenance_status"])
    # The dictionary's descriptions end with a full stop and the IC-records' do
    # not, so the sentence supplies its own and the clause never carries one.
    quantity = clauses.add(
        "H.baseline.meaning",
        (baseline["meaning"] or "").rstrip(". ") or None,
        baseline["meaning_status"],
    )
    unit = clauses.add("H.baseline.unit", baseline["unit"], baseline["unit_status"])
    season = clauses.add(
        "S.season", s["per_role"]["baseline"]["value"], s["per_role"]["baseline"]["status"]
    )
    t_baseline = clauses.add(
        "T.baseline", t["per_role"]["baseline"]["value"], t["per_role"]["baseline"]["status"]
    )
    t_future = clauses.add(
        "T.future", t["per_role"]["future"]["value"], t["per_role"]["future"]["status"]
    )
    c_future = clauses.add(
        "C.future", c["per_role"]["future"]["value"], c["per_role"]["future"]["status"]
    )
    direction = clauses.add("D.direction", d["direction"], d["provenance_status"])
    change = clauses.add("D.change_value", d["change_value"], d["provenance_status"])
    magnitude = clauses.add(
        "M.tercile",
        f"{m['tercile']}, at percentile {m['percentile']} of {m['n_units_at_this_level']} "
        f"{g['level']}-level units. Ranking is on the signed change value, not on its "
        f"absolute size, so a unit in the lower third may be one with a large decrease "
        f"rather than one where little changed. The reference population is "
        f"{m['reference_population']}. {m['rule']} is a placeholder and not a scientific "
        f"threshold",
        PROVISIONAL_RULE,
    )

    lines = [VALIDATION_BANNER, ""]
    for caution in record["cautions"]:
        lines.append(f"> {caution['text']}")
        lines.append("")

    lines.append(
        f"**Scope.** {LEVEL_PHRASE[g['level']]}, identified by {scope}. "
        f"Members: {g['n_cells']} cell(s) --- {g['n_cells_with_value']} with a value on every "
        f"column used, {g['n_cells_empty']} without. Cells without a value are excluded "
        "from every number below and are never read as a zero."
    )
    lines.append("")
    lines.append(
        f"**Quantity.** {quantity}. Unit or type: {unit}. Season: {season}."
    )
    lines.append("")
    lines.append(
        f"**Compared.** Baseline horizon {t_baseline}; future horizon {t_future}; "
        f"future scenario {c_future}."
    )
    lines.append("")
    if v["kind"] == "aggregate_over_member_cells":
        # An aggregate is a computed number over a row set, so it inherits the
        # membership's status as well as the column's --- at county and state
        # level that is what makes these values provisional, not the digits.
        averaged = [column for column in v["per_column"] if column["aggregates"]]
        refused = [column for column in v["per_column"] if not column["aggregates"]]
        summaries = "; ".join(
            "`{}` {}".format(
                column["column"],
                clauses.add(
                    f"V.{column['role']}.unweighted_mean",
                    column["aggregates"]["unweighted_mean"],
                    derived_status([g["provenance_status"], roles[column["role"]]["status"]]),
                ),
            )
            for column in averaged
        )
        sentence = (
            f"**Values.** Unweighted mean over n = {v['n']} member cell(s), a "
            f"**{PROVISIONAL_AGGREGATION_LABEL}**: {summaries}."
        )
        if refused:
            # Named rather than silently dropped: a reader who knows the column is
            # in the record has to be told why no mean of it appears here.
            sentence += " Not averaged: " + "; ".join(
                f"`{column['column']}`, because {column['not_averaged']['reason']}"
                for column in refused
            ) + "."
        lines.append(sentence + " Every per-cell value, averaged or not, is in the record.")
    else:
        summaries = "; ".join(
            "`{}` {}".format(
                column["column"],
                clauses.add(f"V.{column['role']}.raw", column["raw_value"], RAW_VALUE),
            )
            for column in v["per_column"]
        )
        lines.append(f"**Values.** {summaries} --- read from the file, exactly as stored.")
    lines.append("")
    corroborating = d["corroborating"]
    corroborating_sentence = ""
    if corroborating is not None:
        of_n = corroborating["of_n_member_cells"]
        cells = "member cell" if of_n == "1" else "member cells"
        corroborating_count = clauses.add(
            "D.corroborating.sign_count",
            f"{corroborating['sign_word']} on "
            f"{corroborating['n_member_cells_with_that_sign']} of {of_n} {cells}",
            corroborating["provenance_status"],
        )
        corroborating_sentence = (
            f" The separate column `{corroborating['column']}` is {corroborating_count}. "
            f"It is a percent change and is never averaged here."
        )
    lines.append(
        f"**Direction.** {direction}, from the sign of the change value {change}, computed "
        f"by `{v['change']['operation']}` over "
        + ", ".join(f"`{column['column']}`" for column in v["change"]["input_columns"])
        + f".{corroborating_sentence}"
    )
    lines.append("")
    lines.append(f"**Magnitude.** {magnitude}.")
    lines.append("")
    lines.append(
        "Every clause marked "
        f"{PROVISIONAL_OPEN.strip()}...{PROVISIONAL_CLOSE} rests on an inferred-candidate "
        "record or on a field derived from one: reasoned and written down, **not verified "
        "and not owner-confirmed**. The clause marked "
        f"{PR1_OPEN.strip()}...{PR1_CLOSE} rests on a placeholder rule, not on science."
    )
    return {"text": "\n".join(lines).rstrip() + "\n", "clauses": clauses.items}


_CODE_SPAN_RE = re.compile(r"`[^`]*`")


def _without_code_spans(text: str) -> str:
    """Blank out backtick-quoted spans before scanning.

    Column names are always rendered as code --- `wildfire_summer_Hist` --- and a
    short semantic value such as "summer" occurs inside several of them. Counting
    those as unlabelled occurrences of the *value* would report a leak that is
    not there. Code spans carry no claim, so they are removed from both sides of
    the comparison rather than from one.
    """
    return _CODE_SPAN_RE.sub(" ", text)


def unlabelled_inferred_text(record: dict) -> list[tuple[str, str]]:
    """Weak values shown in the description outside their label. Empty is the goal.

    The check is exact rather than statistical because the template records what
    it rendered: for every clause whose status is weak, the wrapped form must
    appear in the text, and the bare value must not appear anywhere the labels do
    not cover --- unless a clause with a **strong** status emitted the identical
    string, which is legitimate and is why the exemption exists.
    """
    text = record["description"]
    scannable = _without_code_spans(text)
    labelled = _without_code_spans(" ".join(PROVISIONAL_RE.findall(text)))
    strong_texts = {
        item["text"] for item in record["description_clauses"] if item["wrapper"] == "none"
    }
    offences = []
    for item in record["description_clauses"]:
        if item["wrapper"] == "provisional_rule":
            if f"{PR1_OPEN}{item['text']}{PR1_CLOSE}" not in text:
                offences.append((item["field"], item["text"]))
            continue
        if item["wrapper"] != "provisional":
            continue
        wrapped = f"{PROVISIONAL_OPEN}{item['text']}{PROVISIONAL_CLOSE}"
        if wrapped not in text:
            offences.append((item["field"], item["text"]))
            continue
        if item["text"] in strong_texts:
            continue
        value = _without_code_spans(item["text"])
        if not value.strip(" ,;."):
            # The value is entirely code --- an identifier such as `California`.
            # Masking leaves nothing to count, so the exact "is the wrapped form
            # present" check above is the whole check for it.
            continue
        if scannable.count(value) != labelled.count(value):
            offences.append((item["field"], item["text"]))
    return offences


# --- the literature probe: a design stub, and nothing more ---------------------


def build_probe(record: dict, variable: dict) -> dict:
    """The terms a retrieval step **would** be given. None has been sent anywhere.

    This is what the next milestone would need in order to look for a paper that
    talks about this unit. It is assembled here so the shape can be criticised
    before any literature work is authorised --- M3 is not authorised, no corpus
    exists in this repository, and nothing in this function reads or writes one.
    """
    g, t, c, d = record["G"], record["T"], record["C"], record["D"]
    place_terms = [
        {
            "term": value,
            "from_column": column,
            "status": g["provenance_status"],
            "note": "a label read as a place name; that reading is inferred",
        }
        for column, value in g["identifier"].items()
    ]
    horizon_terms = [
        {"term": block["value"], "role": role, "status": block["status"]}
        for role, block in t["per_role"].items()
        if block["value"] is not None
    ]
    scenario_terms = [
        {"term": block["value"], "role": role, "status": block["status"]}
        for role, block in c["per_role"].items()
        if block["value"] is not None
    ]
    def _future(terms, fallback):
        for term in terms:
            if term["role"] == "future":
                return term["term"]
        return fallback

    query_sentence = (
        f"{d['direction']} in {variable['concept_terms'][0]} in "
        + ", ".join(term["term"] for term in place_terms)
        + f" under {_future(scenario_terms, 'an unstated scenario')}"
        + f" by {_future(horizon_terms, 'an unstated horizon')}"
    )
    place_terms_note = (
        "A grid-cell id is not a phrase any paper contains. At cell level the probe "
        "has **no usable place term**, which is itself a finding about what a "
        "cell-level unit could ever be matched to."
        if g["level"] == "cell"
        else (
            "The place terms are the stored label strings. Reading them as the names of "
            "places is `inferred_candidate` (IC-011, IC-012), and a name like `Lincoln` "
            "belongs to counties in many states."
        )
    )
    return {
        "kind": "design stub",
        "retrieval_performed": "no",
        "note": (
            "This is what would be sent to retrieval. **Nothing has been sent.** No "
            "literature corpus exists in this repository, no index has been built, and "
            "no passage has been read. M3 is not authorised."
        ),
        "concept_terms": list(variable["concept_terms"]),
        "place_terms": place_terms,
        "direction_term": d["direction"],
        "horizon_terms": horizon_terms,
        "scenario_terms": scenario_terms,
        "place_terms_note": place_terms_note,
        "query_sentence": query_sentence,
        "query_sentence_caveat": (
            "The place terms in this sentence are inferred readings of label columns, and "
            "a Fire Weather Index term in it names an index, never a fire."
        ),
    }


# --- Phase D: the assumptions register ----------------------------------------
#
# Held here as data, not as prose, so that `docs/PHENOMENON_ASSUMPTIONS.md`, the
# records' `assumptions` lists and the tests cannot drift apart. Every record
# names the IDs it depends on and the document is generated from this tuple.
#
# `status` is one of:
#   computed        --- measured from the bytes by a script in this repository
#   unverified      --- reasoned, written down, and not established by anything
#   owner_confirmed --- the mentor confirmed it. Nothing holds this yet.

UNVERIFIED = "unverified"
OWNER_CONFIRMED = "owner_confirmed"

#: Which assumption stands for which inferred-candidate record. IDs are assigned
#: once and never reused, so the map covers all five fire-weather records even
#: though the prototypes use three. Reaching for `A-H2` or `A-H4` raises at the
#: register rather than inventing an entry.
IC_ASSUMPTIONS = {
    "IC-006": "A-H1",
    "IC-007": "A-H2",
    "IC-008": "A-H3",
    "IC-009": "A-H4",
    "IC-010": "A-H5",
}

ASSUMPTIONS = (
    {
        "id": "A1",
        "statement": (
            'One CSV row is treated as one "event". The grain everything else rests on.'
        ),
        "rationale": (
            "The ClimRR table is laid out one row per grid cell carrying a full "
            "set of variables, and that is the only grain the file offers "
            "without joining rows or splitting them. It is Kaiyuan's reading of "
            "the 2026-09-10 direction (R-002), not the mentor's words."
        ),
        "failure_mode": (
            "**Every record describes the wrong object.** If an \u201cevent\u201d is a "
            "season, a cell-decade, or a threshold exceedance rather than a "
            "row, then not only the contents but the *number* of records is "
            "wrong, and nothing downstream survives unchanged."
        ),
        "affects": "every record, at every level",
        "how_verified": "the mentor answers checklist line 1",
        "status": UNVERIFIED,
        "maps_to": "MENTOR_EXAMPLES line 1",
        "mentor_checkable": True,
    },
    {
        "id": "A-G0",
        "statement": (
            "One row is one grid cell, identified by `Crossmodel`. Phase A measured "
            "`Crossmodel` unique across all 62,834 rows, which is what a per-cell key "
            "would look like. **Uniqueness does not by itself establish that the key "
            "names a cell**; the dictionary's own words for the column (line 455) and "
            "checklist line 1 are what would."
        ),
        "rationale": (
            "`Crossmodel` is unique on all 62,834 rows --- computed, not "
            "assumed --- which is what a per-cell key looks like, and the "
            "dictionary calls the column a \u201cText ID for each cell in the "
            "polygon grid\u201d (line 455)."
        ),
        "failure_mode": (
            "**Member counts stop being cell counts.** If rows are cell "
            "fragments, or one cell spans several rows, every unweighted mean "
            "is taken over the wrong population and `n` misreports how much of "
            "the unit the number covers."
        ),
        "affects": "the cell-level unit, and the membership of every aggregate",
        "how_verified": (
            "the uniqueness half is computed by `scripts/hierarchy_checks.py`; the "
            '"names a cell" half is the mentor'
        ),
        "status": COMPUTED,
        "maps_to": "MENTOR_EXAMPLES line 1; dictionary line 455",
        "mentor_checkable": True,
    },
    {
        "id": "A-G1",
        "statement": (
            "`NAME` holds a county or county-equivalent name and `State` holds a US "
            "state name, so a `(State, NAME)` label identifies a county and a `State` "
            "label identifies a state."
        ),
        "rationale": (
            "Value-level evidence recorded in IC-011 and IC-012: the most "
            "frequent `NAME` values are US county-equivalents, 1,770 distinct "
            "names is fewer than the roughly 3,100 US counties (which is what a "
            "column of *names* looks like, not one of identifiers), and the "
            "`State` values are state names ordered by land area, as a grid "
            "over land would produce."
        ),
        "failure_mode": (
            "**`P-COUNTY-1` and `P-STATE-1` describe row sets with no "
            "geographic meaning.** The literature probe's place terms become "
            "noise and no paper could ever be matched to either record --- "
            "while every aggregate still computes, and is about nothing."
        ),
        "affects": "P-COUNTY-1 and P-STATE-1 entirely --- what the unit *is*",
        "how_verified": "the mentor answers checklist line 14",
        "status": UNVERIFIED,
        "maps_to": "MENTOR_EXAMPLES line 14; IC-011, IC-012",
        "mentor_checkable": True,
    },
    {
        "id": "A-G2",
        "statement": (
            "Every grid cell covers the same area, and therefore deserves the same "
            "weight in a mean over cells. **Nothing in this file states a cell area.**"
        ),
        "rationale": (
            "The dictionary describes a single polygon grid (line 455) and the "
            "cell keys are a regular row/column scheme (`R106C361`), which is "
            "what a uniform grid looks like. **No column of this file states a "
            "cell area**, so this is inference from the naming and nothing "
            "more."
        ),
        "failure_mode": (
            "**Every aggregate is biased by an unknown amount in an unknown "
            "direction**, toward wherever cells are smaller. Values, direction "
            "and percentile in the county and state records would all be wrong, "
            "and none of them would look wrong."
        ),
        "affects": "every aggregate value, and through it D and M at county and state level",
        "how_verified": (
            "the grid's definition --- cell size and projection --- from the data owner. "
            "The dictionary describes a polygon grid (line 455) and gives no geometry."
        ),
        "status": UNVERIFIED,
        "maps_to": "a new question for the mentor; related to checklist line 12 (the CRS)",
        "mentor_checkable": True,
    },
    {
        "id": "A-G3",
        "statement": (
            "A county or state in these records is **the set of rows sharing its "
            "label** --- not a boundary and not a geometry. Phase A computed those row "
            "sets, and computed that `GEOID` cannot key them: 3,234 `GEOID` values "
            "appear against more than one `(State, NAME)` pair."
        ),
        "rationale": (
            "Computed rather than reasoned: `scripts/hierarchy_checks.py` "
            "counted the row sets and measured that `GEOID` cannot key them --- "
            "3,234 values span more than one label. The definition is "
            "structural and needs no interpretation to hold."
        ),
        "failure_mode": (
            "**A record names a county and describes a fragment of one.** If "
            "the grid covers only part of what a label names, the arithmetic "
            "stays correct and the reading does not. The risk is to "
            "interpretation, not to the numbers."
        ),
        "affects": "the membership of every aggregate",
        "how_verified": "computed by `scripts/hierarchy_checks.py`, checks 2 and 3",
        "status": COMPUTED,
        "maps_to": "artifacts/profiles/hierarchy_checks.json",
        "mentor_checkable": False,
    },
    {
        "id": "A-AGG1",
        "statement": (
            "The unweighted mean over member cells is a meaningful summary of the unit. "
            "It is the operation these prototypes use; no alternative (area weighting, "
            "population weighting, a median, a quantile) was evaluated. It is applied "
            "**only to columns the aggregator accepts**: a column typed `Percent Change` "
            "or `Text ID`, and every location column, is refused and reported as counts "
            "instead (D-013, ruling criterion 7)."
        ),
        "rationale": (
            "A mean is the simplest summary that uses every member once, and it "
            "is the operation the M1-WP3b ruling permits for representation "
            "validation --- explicitly as a provisional rule and explicitly not "
            "as the project's method. No alternative was evaluated."
        ),
        "failure_mode": (
            "**The county and state records report a number that describes no "
            "cell and no county.** If the quantity is non-linear across space, "
            "or the member distribution is bimodal, the mean sits where nothing "
            "is --- and PR-1 then ranks that artefact against other artefacts."
        ),
        "affects": "V, D and M at county and state level",
        "how_verified": (
            "a scientific judgement --- GUIDANCE and the mentor, not a computation"
        ),
        "status": UNVERIFIED,
        "maps_to": "a new question for the group and the mentor",
        "mentor_checkable": True,
    },
    {
        "id": "A-DIR1",
        "statement": (
            "A change is the later horizon **minus** the historical baseline, so that a "
            "positive value is an increase. The dictionary writes "
            '"Difference between End-Century and Historical" and never defines the '
            "direction of the subtraction."
        ),
        "rationale": (
            "The dictionary writes \u201cDifference between End-Century and "
            "Historical\u201d in that order (line 665), which reads as later minus "
            "earlier. **It never defines the subtraction**, and the same "
            "ambiguity is checklist line 7."
        ),
        "failure_mode": (
            "**Every direction in every record flips**, and PR-1's signed "
            "ranking inverts with it: what is reported as an upper-third "
            "increase is a lower-third decrease. No value changes; every "
            "reading of one does."
        ),
        "affects": "D in every record, and the sign PR-1 ranks in M",
        "how_verified": "the mentor answers checklist line 7 (and line 4 for heat index)",
        "status": UNVERIFIED,
        "maps_to": "MENTOR_EXAMPLES line 7",
        "mentor_checkable": True,
    },
    {
        "id": "A-DIR2",
        "statement": (
            "For the fire-weather variable the **absolute difference** column "
            "`wildfire_summer_Dend` (193) carries the change, with the "
            "`verified_from_dictionary` percent-change column `wildfire_summer_Pend` "
            "(195) reported beside it as a corroborating sign. The reason is "
            "arithmetic --- a mean of per-cell differences is the difference of the "
            "per-cell means, and a mean of per-cell percent changes is not --- and the "
            "choice is the EXECUTOR's, not a decided one."
        ),
        "rationale": (
            "Arithmetic: the unweighted mean of per-cell differences *is* the "
            "difference of the per-cell means, and the mean of per-cell percent "
            "changes is not. The absolute difference therefore aggregates "
            "consistently across levels and the percent change does not --- "
            "which is also why the ruling forbids averaging the latter."
        ),
        "failure_mode": (
            "**The fire-weather records answer a question the project did not "
            "ask.** If the percent change is the quantity of interest, the "
            "county-level number would have to be recomputed by a rule that "
            "does not yet exist, since averaging it is forbidden."
        ),
        "affects": "D and M in P-CELL-1 and P-COUNTY-1",
        "how_verified": "a choice for the COORDINATOR and the group, not a computation",
        "status": UNVERIFIED,
        "maps_to": "a new question for the group; MENTOR_EXAMPLES line 7 bears on it",
        "mentor_checkable": False,
    },
    {
        "id": "A-H1",
        "statement": (
            "IC-006: `wildfire_summer_Hist` (189) holds the ensemble-mean summer "
            "seasonal average daily Fire Weather Index for the modeled historical "
            'period --- rather than the seasonal 95th percentile. The unit "dimensionless '
            'index value" is inferred; the dictionary states none.'
        ),
        "rationale": (
            "The section title \u201cFire Weather Index - Averages\u201d (line 637) "
            "supplies the variable, and the narrative at lines 346-352 defines "
            "the ensemble mean of the seasonal average daily FWI in full. The "
            "field entry itself says only \u201cSeasonal value\u201d (line 661)."
        ),
        "failure_mode": (
            "**The concept clause is wrong while every number stays valid** --- "
            "the most dangerous shape of error here. If \u201cSeasonal value\u201d is the "
            "seasonal 95th percentile (the FWI-classes narrative, line 357 "
            "onward), the baseline is a different quantity and the change is a "
            "change in a different quantity."
        ),
        "affects": "the baseline value and the concept of both fire-weather prototypes",
        "how_verified": "the mentor answers checklist lines 5 and 6",
        "status": UNVERIFIED,
        "maps_to": "MENTOR_EXAMPLES lines 5, 6; IC-006",
        "mentor_checkable": True,
    },
    {
        "id": "A-H3",
        "statement": (
            "IC-008: `wildfire_summer_Endc` (191) holds the same quantity for the "
            "end-of-century RCP8.5 projection. Its recorded minimum is exactly "
            "`0.000000000000000` on 2 rows of the file, and whether that is a value or "
            "a fill is open (Q17)."
        ),
        "rationale": (
            "As A-H1, with the end-of-century endpoint quoted at line 663 and "
            "dated from line 101."
        ),
        "failure_mode": (
            "As A-H1. Additionally, **if the two exact `0.000000000000000` "
            "values are a fill rather than a value (Q17), two cells are not "
            "comparable to the rest** and the PR-1 percentile of every cell- "
            "level unit shifts."
        ),
        "affects": "the future value and the concept of both fire-weather prototypes",
        "how_verified": "the mentor answers checklist lines 5 and 6; Q17 separately",
        "status": UNVERIFIED,
        "maps_to": "MENTOR_EXAMPLES lines 5, 6; IC-008; Q17",
        "mentor_checkable": True,
    },
    {
        "id": "A-H5",
        "statement": (
            "IC-010: `wildfire_summer_Dend` (193) is the absolute difference between "
            "index 191 and index 189, in whatever units the index carries, and its "
            "endpoints are those two stored columns rather than separately computed "
            "ones."
        ),
        "rationale": (
            "The `D`/`P` pairing at lines 665 and 667 runs over the same two "
            "endpoints: the sibling is `verified_from_dictionary` as a percent "
            "change, so this column is the absolute difference of the same "
            "comparison."
        ),
        "failure_mode": (
            "**The record becomes internally inconsistent while each number "
            "stays individually correct.** If `Dend`'s endpoints are not "
            "indices 189 and 191, the change value is not the change between "
            "the two values the same record reports."
        ),
        "affects": "the change value, and therefore D and M, in both fire-weather prototypes",
        "how_verified": "the mentor answers checklist line 7",
        "status": UNVERIFIED,
        "maps_to": "MENTOR_EXAMPLES line 7; IC-010",
        "mentor_checkable": True,
    },
    {
        "id": "A-M1",
        "statement": (
            "`provisional_rule PR-1` --- the tercile of the change value against all "
            "units at the same level --- is a **placeholder that makes the magnitude "
            "field non-empty**. It is not a scientific threshold, rests on no "
            "literature and on no distributional reasoning, and no part of this project "
            "treats a tercile as meaning anything."
        ),
        "rationale": (
            "`M` had to be non-empty for the group to have something to argue "
            "with, and a rank is the weakest claim available --- it asserts "
            "only an ordering the data already contains, and no threshold, no "
            "category boundary and no significance."
        ),
        "failure_mode": (
            "**The project ships a magnitude criterion it never chose.** If a "
            "tercile is read as scientific importance, PR-1 becomes the "
            "definition by default. The label and the distinct `[provisional "
            "rule PR-1: ...]` mark exist to prevent exactly that; the failure "
            "is one of reading, not of arithmetic."
        ),
        "affects": "M in every record",
        "how_verified": (
            "it cannot be verified as it stands --- it has to be replaced by a "
            "criterion GUIDANCE and the mentor accept"
        ),
        "status": UNVERIFIED,
        "maps_to": "a new question for the group; blueprint M3 'define and justify salience'",
        "mentor_checkable": True,
    },
)

#: Assumptions that no record uses because the columns they would cover are
#: `verified_from_dictionary`. Recorded so the absence is visibly deliberate.
NO_ASSUMPTION_NEEDED = (
    "The heat-index day-count columns 241 `heatindex_HIS_Day105` and 253 "
    "`heatindex_E85_Day105` are `verified_from_dictionary`: the dictionary states the "
    "quantity, the threshold, the season, the scenario and the horizon in its own "
    "words at lines 680 and 695. No `A-H` assumption covers them, and none is needed."
)


def assumption(assumption_id: str) -> dict:
    for item in ASSUMPTIONS:
        if item["id"] == assumption_id:
            return item
    raise PhenomenonError(f"no assumption {assumption_id!r} in the register")


def assumptions_for(*, level: str, variable: dict, ic_ids) -> list[str]:
    """The register entries a record at this level, on this variable, depends on."""
    ids = ["A1", "A-G0"]
    if level != "cell":
        ids += ["A-G1", "A-G2", "A-G3", "A-AGG1"]
    ids.append("A-DIR1")
    if variable["corroborating_change_index"] is not None:
        ids.append("A-DIR2")
    for ic_id in sorted(ic_ids):
        mapped = IC_ASSUMPTIONS.get(ic_id)
        if mapped is None:
            raise PhenomenonError(
                f"inferred-candidate record {ic_id} has no assumption in the register"
            )
        ids.append(mapped)
    ids.append("A-M1")
    for item in ids:
        assumption(item)
    return ids
