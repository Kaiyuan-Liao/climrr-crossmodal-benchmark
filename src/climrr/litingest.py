"""M4-WP1 ingestion primitives: verified reads, structure description, span integrity.

Offsets (D-016): **zero-based, half-open `[start, end)` Unicode code-point
offsets into the JSON string value exactly as it is after `json.loads` and
before any normalization.** Python `str` indexes by code point, so
`value[start:end]` is the evidence text. No lower-casing, whitespace
compression, Markdown conversion or sentence joining happens before an offset
is taken --- this module never normalizes a string at all.

JSON paths are written `$`, `$.key`, `$.key[3]`, `$.key[3].sub`; a key that is
not a plain identifier is written `$["a key"]`.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from climrr.checksums import sha256_file

OFFSET_CONVENTION = (
    "zero-based, half-open [start, end) Unicode code-point offsets into the JSON "
    "string value after json decoding and before any normalization"
)

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class IntegrityError(RuntimeError):
    """A file, span or hash does not match what it is recorded as."""


def read_verified(path: Path, expected_sha256: str) -> tuple[object | None, str | None]:
    """(decoded JSON, None) or (None, parse-failure reason). Hash mismatch raises."""
    observed = sha256_file(path)
    if observed != expected_sha256:
        raise IntegrityError(f"{path.name}: SHA-256 {observed} != manifest {expected_sha256}")
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return None, f"not UTF-8: {exc}"
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, f"not valid JSON: {exc}"


def child_path(parent: str, key: str | int) -> str:
    if isinstance(key, int):
        return f"{parent}[{key}]"
    return f"{parent}.{key}" if _IDENT.match(key) else f"{parent}[{json.dumps(key)}]"


def resolve(doc: object, path: str) -> object:
    """The value at a `$...` path. Raises KeyError / IndexError if absent."""
    if not path.startswith("$"):
        raise ValueError(f"path must start with $: {path!r}")
    rest, node = path[1:], doc
    token_re = re.compile(r'\.([A-Za-z_][A-Za-z0-9_]*)|\[(\d+)\]|\[("(?:[^"\\]|\\.)*")\]')
    pos = 0
    while pos < len(rest):
        m = token_re.match(rest, pos)
        if m is None:
            raise ValueError(f"bad path at {pos}: {path!r}")
        if m.group(1) is not None:
            node = node[m.group(1)]
        elif m.group(2) is not None:
            node = node[int(m.group(2))]
        else:
            node = node[json.loads(m.group(3))]
        pos = m.end()
    return node


def type_name(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def describe(value: object, path: str = "$", depth: int = 0) -> dict:
    """Structure only: types, keys in order, lengths. Never a string's content."""
    t = type_name(value)
    out: dict = {"path": path, "type": t}
    if t == "string":
        out["length_code_points"] = len(value)
    elif t == "object":
        out["keys"] = list(value)
        out["children"] = [describe(v, child_path(path, k), depth + 1) for k, v in value.items()]
    elif t == "array":
        out["length"] = len(value)
        types: dict[str, int] = {}
        for v in value:
            types[type_name(v)] = types.get(type_name(v), 0) + 1
        out["element_types"] = types
        objs = [v for v in value if isinstance(v, dict)]
        if objs:
            keysets = {tuple(v) for v in objs}
            out["object_element_keysets"] = [list(k) for k in sorted(keysets)]
        out["elements"] = [describe(v, child_path(path, i), depth + 1) for i, v in enumerate(value)]
    return out


def evidence_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_span(doc: object, evidence: dict) -> None:
    """Slice the decoded source with the span; it must equal the text and hash."""
    value = resolve(doc, evidence["json_path"])
    if not isinstance(value, str):
        raise IntegrityError(f"{evidence['json_path']} is not a string")
    start, end = evidence["char_start"], evidence["char_end"]
    if not (isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(value)):
        raise IntegrityError(f"{evidence['json_path']}: bad span [{start}, {end}) for length {len(value)}")
    if value[start:end] != evidence["evidence_text"]:
        raise IntegrityError(f"{evidence['json_path']} [{start}, {end}): slice != evidence_text")
    if evidence_sha256(evidence["evidence_text"]) != evidence["evidence_sha256"]:
        raise IntegrityError(f"{evidence['json_path']} [{start}, {end}): evidence_sha256 mismatch")


def locate(doc: object, json_path: str, text: str, occurrence: int = 1) -> dict:
    """Build an evidence block by exact search for `text` in the string at `json_path`.

    Exact, case-sensitive, on the unnormalized string. `occurrence` picks the
    n-th match; a text that is absent raises rather than being approximated.
    """
    value = resolve(doc, json_path)
    if not isinstance(value, str):
        raise IntegrityError(f"{json_path} is not a string")
    start = -1
    for _ in range(occurrence):
        start = value.find(text, start + 1)
        if start < 0:
            raise IntegrityError(f"{json_path}: text not found (occurrence {occurrence}): {text[:60]!r}")
    return {
        "json_path": json_path,
        "char_start": start,
        "char_end": start + len(text),
        "offset_convention": OFFSET_CONVENTION,
        "evidence_text": text,
        "evidence_sha256": evidence_sha256(text),
    }
