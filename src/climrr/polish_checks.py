"""Deterministic invariance checks for the readability polish (D-063; work package P3a, section C).

`scripts/litcollect/litpolish_agent.py` v1 asks a model to rewrite an item's question and integrated answer for a general
scientific reader without changing their meaning. `invariance` decides whether a rewrite may replace the pre-polish text,
per field (the question, the answer):

- **numbers**: the identical set of numbers (`benchmark_items.NUMBER_RE` on the normalised text);
- **places**: the identical set of place and region names --- U.S. state and NCA5 region names of the pinned map, "United
  States", "U.S." (`place_names`; whole phrases, longest first, case-sensitive);
- **hedges**: the identical set of hedge words ("shows", "shown", "suggests", ...; `HEDGE_WORD_RE`);
- **no new source words**: no source word (data, table, model, paper, study, ...) the original lacks, and no leakage flag
  (`text_leakage`, `model_source_flags`, for the question `leakage_check`) or generality flag (post-checks v3) the original
  lacks --- "leakage v2.3"; v1a (P3a hotfix, D-053b): nor a fire-occurrence word ("wildfire", "fires", "burned area";
  `benchmark_items.FWI_FORBIDDEN_RE`) the original lacks, for every item (the polish step does not see the family);
- **length**: between 0.6x and 1.2x the original's characters;
- **mechanism keywords**: every content word of the original that is a mechanism keyword (a content word of the label of
  a group the item cites) still present, or replaced by a word `polish_synonyms_v1.yaml` lists for it.

A rewrite that fails any check is not used: the agent keeps the pre-polish text (`polish_rejected`).

No model call.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from climrr import benchmark_items as bi
from climrr.checksums import sha256_file
from climrr.manifest import MANIFEST_PATH, load_entry
from climrr.paths import REPO_ROOT

VERSION = "polish_checks v1a"   # v1 + the fire-occurrence words (D-053b)
SYNONYMS_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "polish_synonyms_v1.yaml"
LENGTH_BOUNDS = (0.6, 1.2)
HEDGE_WORD_RE = re.compile(r"\b(?:shows?|shown|suggests?|suggested|indicates?|reports?|reported)\b", re.I)
SOURCE_WORD_RE = re.compile(r"\b(?:data|dataset|datasets|table|tables|model|models|modeled|modelled|paper|papers|study|studies"
                            r"|author|authors|simulation|simulations|literature|article|articles)\b", re.I)
WORD_RE = re.compile(r"[A-Za-z]+")
FIELDS = ("prompt", "answer")


def load_synonyms(path: Path = SYNONYMS_PATH, manifest_path: Path = MANIFEST_PATH) -> dict:
    path = Path(path)
    pin = load_entry(path.name, manifest_path)["sha256"]
    if sha256_file(path) != pin:
        raise ValueError(f"{path.name} differs from its manifest pin {pin}")
    return dict(yaml.safe_load(path.read_text(encoding="utf-8")), sha256=pin)


def stem(word: str) -> str:
    w = word.lower()
    return w[:-1] if len(w) > 4 and w.endswith("s") and not w.endswith("ss") else w


def words(text: str) -> set[str]:
    return {stem(w) for w in WORD_RE.findall(text)}


def place_names(nca: dict) -> list[str]:
    """State and NCA5 region names of the map, and the U.S. names, longest first."""
    names = set(nca["state_region"]) | set(nca["region_name"].values()) | {"United States", "U.S."}
    return sorted(names, key=lambda n: (-len(n), n))


def places(text: str, names: list[str]) -> list[str]:
    """The names in `text`, each occurrence consumed by the longest name that covers it ("West Virginia", not "Virginia")."""
    taken: list[tuple[int, int]] = []
    out = set()
    for n in names:
        for m in re.finditer(rf"(?<![A-Za-z]){re.escape(n)}(?![A-Za-z])", text):
            if not any(a <= m.start() < b for a, b in taken):
                taken.append(m.span())
                out.add(n)
    return sorted(out)


def numbers(text: str) -> list[str]:
    return sorted({m.group(0).replace(",", "") for m in bi.NUMBER_RE.finditer(bi.normalise_number_text(text))})


def hedges(text: str) -> list[str]:
    return sorted({m.group(0).lower() for m in HEDGE_WORD_RE.finditer(text)})


def source_words(text: str) -> list[str]:
    return sorted({m.group(0).lower() for m in SOURCE_WORD_RE.finditer(text)})


def leakage_flags(text: str, field: str, columns: list[str]) -> set[str]:
    flags = set(bi.text_leakage(text, columns)) | set(bi.model_source_flags(text)) | {f"generality: {g}" for g in bi.generality_flags(text)}
    flags |= {f"fire-occurrence word: {w.lower()}" for w in bi.fwi_forbidden_flags(text)}
    if field == "prompt":
        flags |= set(bi.leakage_check(text, columns)["flags"])
    return flags


def mechanism_keywords(labels: list[str], syn: dict) -> set[str]:
    """Content words (stems) of the cited groups' labels: alphabetic, at least `min_keyword_length` letters, not a stopword."""
    stop = {stem(w) for w in syn["stopwords"]}
    return {stem(w) for t in labels for w in WORD_RE.findall(t or "") if len(w) >= syn["min_keyword_length"]} - stop


def invariance(original: dict, polished: dict, labels: list[str], nca: dict, syn: dict, columns: list[str] | None = None) -> dict:
    """{pass, reasons, checks} for a rewrite. `original` / `polished`: {"prompt", "answer"}; `labels`: the labels of the
    groups the item cites."""
    cols = columns if columns is not None else bi.column_names()
    names = place_names(nca)
    keys = mechanism_keywords(labels, syn)
    synonyms = {stem(k): {stem(v) for v in vs} for k, vs in (syn.get("synonyms") or {}).items()}
    reasons: list[str] = []
    checks: dict = {}
    for f in FIELDS:
        o, p = original.get(f) or "", polished.get(f)
        if not isinstance(p, str) or not p.strip():
            reasons.append(f"{f}: missing or empty in the rewrite")
            continue
        c = {}
        for name, fn in (("numbers", numbers), ("places", lambda t: places(t, names)), ("hedges", hedges)):
            a, b = fn(o), fn(p)
            c[name] = {"original": a, "polished": b}
            if a != b:
                reasons.append(f"{f}: {name} differ (original {a}, polished {b})")
        new_src = sorted(set(source_words(p)) - set(source_words(o)))
        new_leak = sorted(leakage_flags(p, f, cols) - leakage_flags(o, f, cols))
        c["new_source_words"], c["new_leakage_flags"] = new_src, new_leak
        reasons += [f"{f}: new source word {w!r}" for w in new_src] + [f"{f}: new leakage flag {x}" for x in new_leak]
        ratio = len(p) / len(o) if o else float("inf")
        c["length_ratio"] = round(ratio, 3)
        if not LENGTH_BOUNDS[0] <= ratio <= LENGTH_BOUNDS[1]:
            reasons.append(f"{f}: length ratio {ratio:.2f} outside {LENGTH_BOUNDS[0]}-{LENGTH_BOUNDS[1]}")
        ow, pw = words(o), words(p)
        lost = sorted(k for k in keys & ow if k not in pw and not (synonyms.get(k, set()) & pw))
        c["mechanism_keywords_in_original"] = sorted(keys & ow)
        c["mechanism_keywords_lost"] = lost
        reasons += [f"{f}: mechanism keyword {k!r} lost (no listed synonym present)" for k in lost]
        checks[f] = c
    return {"check_version": VERSION, "pass": not reasons, "reasons": reasons, "checks": checks}
