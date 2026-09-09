"""Deterministic, semantics-neutral column profile of a CSV read entirely as text.

Every value is read as a `str` by Python's `csv` module. No library type
inference is allowed to decide what a column "is": the only type-like facts
recorded here are whether *every* non-empty value in a column matches a regex
written out in full below. That is a statement about characters, not about
physical quantity, unit, scenario, or measurement.

Nothing in this module assigns meaning. There is no notion here of temperature,
identifier, county, sentinel, missing value, observation, or fire. Column names
are opaque strings, carried through verbatim including truncation and
duplication. `candidate_sentinel_values` is a frequency flag and nothing more:
it says "this extreme value repeats often", never "this value means missing".

Read-only by construction --- this module opens files for reading and writes
nothing under `data/`.

Matching rules
--------------

Each raw field value `v` is reduced to its **trimmed form**, `v.strip()`. A
value is **empty** when that trimmed form is the empty string; every other value
is *non-empty*. Regexes are matched against the trimmed form, so surrounding
whitespace never decides whether a column is numeric. Distinct counts, top-value counts, lengths, and
`candidate_sentinel_values` all use the **raw, unstripped** value, so no
original byte is hidden by the reduction.

`DECIMAL_PATTERN`::

    ^[+-]?(?:[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+)(?:[eE][+-]?[0-9]+)?$

An optional sign; then either digits with an optional fractional part, or a
bare fractional part; then an optional decimal exponent. It accepts `0`, `007`,
`-1`, `+1.5`, `1.`, `.5`, `1e6`, `-2.5E-3`. It rejects the empty string, `NA`,
`N/A`, `null`, `nan`, `inf`, `1,000`, `1 000`, `--1`, `1e`, `0x1F`, and
anything with a trailing or leading character outside the grammar. Special
float literals are deliberately rejected: `nan` and `inf` are parseable by
`decimal.Decimal` but are not decimal numerals, and admitting them would make
min/max meaningless.

`INTEGER_PATTERN`::

    ^[+-]?[0-9]+$

`LEADING_ZERO_PATTERN`::

    ^0[0-9]+$

Unsigned, at least two characters, first character `0`. This is the pattern
that makes leading-zero identifiers visible as a counted fact rather than an
assumption; `0` alone does not match, since a single zero has no leading zero
to lose.

Ranges are computed with `decimal.Decimal`, never `float`: the text in the file
is decimal, and binary floating point would introduce a rounding that is not in
the data.

Determinism
-----------

The profile is a pure function of the CSV bytes plus the rule constants above.
Every ordering is total: top values and sentinel candidates sort by descending
count then by raw value, and the raw value reported for a decimal minimum or
maximum is the lexicographically smallest raw spelling among those that tie
numerically. `profile_content_hash` hashes the profile with its `environment`
block removed, so two hosts running different Python minor versions must
produce the identical hash from identical bytes.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

#: Bump when the computed fields or the rules change; the profile content hash
#: is only comparable within one version.
PROFILE_VERSION = 1

DECIMAL_PATTERN = r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$"
INTEGER_PATTERN = r"^[+-]?[0-9]+$"
LEADING_ZERO_PATTERN = r"^0[0-9]+$"

DECIMAL_RE = re.compile(DECIMAL_PATTERN)
INTEGER_RE = re.compile(INTEGER_PATTERN)
LEADING_ZERO_RE = re.compile(LEADING_ZERO_PATTERN)

#: A value is flagged as a sentinel *candidate* only if it is an extreme of the
#: column and repeats on at least this fraction of rows. Purely quantitative.
SENTINEL_MIN_RATE = 0.005

ENCODING = "utf-8-sig"

TOP_VALUES_N = 5

#: Column fields written to the human-readable CSV sibling, in this order.
CSV_FIELDS = (
    "index",
    "name",
    "n_rows",
    "n_empty",
    "empty_rate",
    "n_distinct",
    "n_distinct_nonempty",
    "all_nonempty_match_decimal",
    "all_nonempty_match_integer",
    "min_decimal",
    "max_decimal",
    "n_negative",
    "n_zero",
    "n_with_leading_zero",
    "n_with_leading_zero_any",
    "min_len",
    "max_len",
    "is_constant",
    "looks_unique",
    "n_candidate_sentinel_values",
    "top1_value",
    "top1_count",
)

# Fields in this export can be long; raise the limit rather than fail late.
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def read_header(path: Path | str) -> list[str]:
    """Return the header row verbatim, as a list of opaque strings."""
    with Path(path).open("r", encoding=ENCODING, newline="") as handle:
        try:
            return next(csv.reader(handle))
        except StopIteration:
            return []


def duplicate_column_names(header: list[str]) -> dict[str, list[int]]:
    """Names that appear more than once, mapped to every ordinal index using them.

    Duplicates are reported, never renamed or deduplicated. The ordinal index
    is the key for a column throughout this profile precisely because a name
    may not be unique.
    """
    positions: dict[str, list[int]] = {}
    for index, name in enumerate(header):
        positions.setdefault(name, []).append(index)
    return {name: idx for name, idx in positions.items() if len(idx) > 1}


def accumulate_value_counts(path: Path | str, n_columns: int) -> tuple[list[dict[str, int]], dict]:
    """Stream the CSV once, counting raw values per column ordinal.

    Every distinct raw string is kept with its frequency; every per-column fact
    in this module is derived from those counts, so the file is read exactly
    once and no second pass can disagree with the first.

    Rows with an unexpected field count are counted and reported rather than
    repaired: a short row contributes an empty string to the columns it lacks,
    and a long row's surplus fields are counted but not attributed to any
    column, since there is no column to attribute them to.
    """
    counts: list[dict[str, int]] = [{} for _ in range(n_columns)]
    n_rows = 0
    n_short = 0
    n_long = 0
    min_fields = None
    max_fields = None

    with Path(path).open("r", encoding=ENCODING, newline="") as handle:
        reader = csv.reader(handle)
        try:
            next(reader)
        except StopIteration:
            pass
        for row in reader:
            n_rows += 1
            width = len(row)
            if min_fields is None or width < min_fields:
                min_fields = width
            if max_fields is None or width > max_fields:
                max_fields = width
            if width == n_columns:
                for column_counts, value in zip(counts, row):
                    column_counts[value] = column_counts.get(value, 0) + 1
                continue
            if width < n_columns:
                n_short += 1
            else:
                n_long += 1
            for index in range(n_columns):
                value = row[index] if index < width else ""
                column_counts = counts[index]
                column_counts[value] = column_counts.get(value, 0) + 1

    shape = {
        "n_rows": n_rows,
        "n_rows_with_too_few_fields": n_short,
        "n_rows_with_too_many_fields": n_long,
        "min_fields_per_row": min_fields,
        "max_fields_per_row": max_fields,
    }
    return counts, shape


def profile_column(
    index: int,
    name: str,
    counts: dict[str, int],
    n_rows: int,
    sentinel_min_rate: float = SENTINEL_MIN_RATE,
) -> dict:
    """Derive every recorded fact for one column from its raw value counts."""
    n_distinct = len(counts)

    nonempty: list[tuple[str, str, int]] = []  # (raw, trimmed, count)
    n_empty = 0
    for raw, count in counts.items():
        trimmed = raw.strip()
        if trimmed:
            nonempty.append((raw, trimmed, count))
        else:
            n_empty += count
    n_nonempty = n_rows - n_empty
    n_distinct_nonempty = len(nonempty)

    top_values = [
        {"value": raw, "count": count}
        for raw, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:TOP_VALUES_N]
    ]

    lengths = [len(raw) for raw, _trimmed, _count in nonempty]

    all_decimal = bool(nonempty) and all(DECIMAL_RE.match(trimmed) for _raw, trimmed, _c in nonempty)
    all_integer = bool(nonempty) and all(INTEGER_RE.match(trimmed) for _raw, trimmed, _c in nonempty)

    n_leading_zero_any = sum(
        count for _raw, trimmed, count in nonempty if LEADING_ZERO_RE.match(trimmed)
    )

    min_decimal = max_decimal = None
    n_negative = n_zero = None
    candidate_sentinels: list[dict] = []

    if all_decimal:
        parsed = [(raw, Decimal(trimmed), count) for raw, trimmed, count in nonempty]
        min_value = min(value for _raw, value, _c in parsed)
        max_value = max(value for _raw, value, _c in parsed)
        # Ties are broken lexicographically so the reported spelling is a
        # function of the bytes, not of dict iteration order.
        min_decimal = min(raw for raw, value, _c in parsed if value == min_value)
        max_decimal = min(raw for raw, value, _c in parsed if value == max_value)
        n_negative = sum(count for _raw, value, count in parsed if value < 0)
        n_zero = sum(count for _raw, value, count in parsed if value == 0)

        threshold = sentinel_min_rate * n_rows
        candidate_sentinels = sorted(
            (
                {"value": raw, "count": count}
                for raw, value, count in parsed
                if (value == min_value or value == max_value) and count >= threshold
            ),
            key=lambda item: (-item["count"], item["value"]),
        )

    return {
        "index": index,
        "name": name,
        "n_rows": n_rows,
        "n_empty": n_empty,
        "n_nonempty": n_nonempty,
        "empty_rate": (n_empty / n_rows) if n_rows else 0.0,
        "n_distinct": n_distinct,
        "n_distinct_nonempty": n_distinct_nonempty,
        "top5_values": top_values,
        "all_nonempty_match_decimal": all_decimal,
        "min_decimal": min_decimal,
        "max_decimal": max_decimal,
        "n_negative": n_negative,
        "n_zero": n_zero,
        "all_nonempty_match_integer": all_integer,
        "n_with_leading_zero": n_leading_zero_any if all_integer else None,
        "n_with_leading_zero_any": n_leading_zero_any,
        "min_len": min(lengths) if lengths else None,
        "max_len": max(lengths) if lengths else None,
        "is_constant": n_distinct_nonempty <= 1,
        "looks_unique": bool(n_nonempty) and n_distinct_nonempty == n_nonempty,
        "candidate_sentinel_values": candidate_sentinels,
    }


def build_profile(
    path: Path | str,
    *,
    data_sha256: str,
    data_bytes: int,
    data_path_label: str,
    environment: dict,
    sentinel_min_rate: float = SENTINEL_MIN_RATE,
) -> dict:
    """Profile every column of the CSV at `path`.

    `data_sha256` is supplied by the caller rather than computed here: the
    caller must have already verified it against `data/manifest.json` and
    failed closed if it did not match.
    """
    header = read_header(path)
    n_columns = len(header)
    counts, shape = accumulate_value_counts(path, n_columns)
    n_rows = shape["n_rows"]

    columns = [
        profile_column(index, name, counts[index], n_rows, sentinel_min_rate=sentinel_min_rate)
        for index, name in enumerate(header)
    ]

    return {
        "profile_version": PROFILE_VERSION,
        "data_path": data_path_label,
        "data_sha256": data_sha256,
        "data_bytes": data_bytes,
        "n_rows": n_rows,
        "n_columns": n_columns,
        "encoding": ENCODING,
        "read_as": "str (csv module; no type inference)",
        "empty_definition": "value.strip() == ''",
        "decimal_regex": DECIMAL_PATTERN,
        "integer_regex": INTEGER_PATTERN,
        "leading_zero_regex": LEADING_ZERO_PATTERN,
        "sentinel_min_rate": sentinel_min_rate,
        "duplicate_column_names": duplicate_column_names(header),
        "row_shape": shape,
        "environment": environment,
        "columns": columns,
    }


def canonical_profile_bytes(profile: dict) -> bytes:
    """The profile minus its `environment` block, as canonical JSON bytes.

    Sorted keys, no insignificant whitespace, ASCII-escaped. This is what the
    content hash is taken over, so the hash is invariant to key order, to the
    host, to the Python minor version, and to the commit the profile was run
    from --- and varies with any computed fact or rule constant.
    """
    payload = {key: value for key, value in profile.items() if key != "environment"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "ascii"
    )


def profile_content_hash(profile: dict) -> str:
    """SHA-256 of `canonical_profile_bytes`: the cross-host comparison value."""
    return hashlib.sha256(canonical_profile_bytes(profile)).hexdigest()


def profile_csv_rows(profile: dict) -> list[list]:
    """Rows for the human-readable CSV sibling: header row first."""
    rows: list[list] = [list(CSV_FIELDS)]
    for column in profile["columns"]:
        top = column["top5_values"][0] if column["top5_values"] else None
        flat = dict(column)
        flat["n_candidate_sentinel_values"] = len(column["candidate_sentinel_values"])
        flat["top1_value"] = top["value"] if top else ""
        flat["top1_count"] = top["count"] if top else ""
        rows.append(["" if flat.get(field) is None else flat.get(field) for field in CSV_FIELDS])
    return rows


def write_profile_csv(path: Path | str, profile: dict) -> None:
    """Write the human-readable sibling with LF line endings on every platform.

    `csv.writer` defaults to CRLF. Left at the default, a committed artifact
    would be rewritten by Git's newline normalisation and then differ from the
    file the next host regenerates --- a spurious diff on a clone that ran the
    same code over the same bytes.
    """
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle, lineterminator="\n").writerows(profile_csv_rows(profile))


def write_profile_json(path: Path | str, profile: dict) -> None:
    Path(path).write_text(
        json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
