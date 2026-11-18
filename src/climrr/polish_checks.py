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


# --- v2 (work package P3b, section D; D-063) ---------------------------------------------------------------------
#
# Polish run 1 (litpolish_agent v1, checks v1a) rejected all six rewrites, 12 of 14 reasons a mechanism keyword lost
# word by word ("condition", "creating"; "frequency" for "more frequent") and 2 a number ("1" written "one"; "about half
# again as many" written "50 %"). v2 replaces the two checks and adds one:
#
# - **mechanism, by group**: every cited group recognisable in the original (one of its key terms present:
#   `group_terms`, `polish_synonyms_v2.yaml`) must stay recognisable in the rewrite --- one term per group, not every
#   keyword;
# - **numbers, by value**: the set of numeric values --- digits, and a cardinal number-word before a counting noun ("about
#   one day" = "about 1 day"); "about 11 days" = "11 days"; a descriptor form ("about half again as many") is not a number;
# - **descriptor phrases** (EXECUTOR, from the run-1 rewrites that changed a fact: "about 50 %" for "a moderate increase",
#   "under a high-emissions scenario", "rank among the highest in the nation"): every phrase class the original uses ---
#   the magnitude class and the tercile comparison of DR-DESC-1 v4 (any of the class's forms), the scenario and horizon
#   phrases and the quantity (long or short) of plain language v1a --- is still used by the rewrite, in any form of the
#   same class.
# Places, hedges, no new source word / leakage / generality / fire-occurrence word, and the length bounds are v1a's.

VERSION_V2 = "polish_checks v2"
SYNONYMS_V2_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "polish_synonyms_v2.yaml"
_DASHES = "‐‑‒–—−-"
COUNT_NOUN_RE = re.compile(r"\b(" + "|".join(sorted(bi._WORD_VALUES, key=len, reverse=True)) + r")(?:[-\s](one|two|three|four|five|six|"
                           r"seven|eight|nine))?\s+(?:more\s+|extra\s+|additional\s+)?(?:days?|weeks?|months?|seasons?|summers?"
                           r"|degrees?|percent|states?|regions?)\b", re.I)


def stem2(word: str) -> str:
    """v2: lower case; "-ies" / "-ied" -> "-y"; "-ing", "-ed", a plural "s" removed (the stem keeps >= 3 letters); then one
    final "e" ("increase", "increases", "increased", "increasing" -> "increas")."""
    w = word.lower()
    if len(w) > 5 and w.endswith(("ies", "ied")):
        w = w[:-3] + "y"
    elif w.endswith("ing") and len(w) >= 6:
        w = w[:-3]
    elif w.endswith("ed") and len(w) >= 5:
        w = w[:-2]
    elif w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        w = w[:-1]
    return w[:-1] if len(w) > 3 and w.endswith("e") else w


def tokens(text: str, stemmed: bool = True) -> list[str]:
    t = (text or "").lower()
    for d in _DASHES:
        t = t.replace(d, " ")
    ws = re.findall(r"[a-z]+", t)
    return [stem2(w) for w in ws] if stemmed else ws


def _has(seq: list[str], sub: tuple[str, ...]) -> bool:
    n = len(sub)
    return n > 0 and any(tuple(seq[i:i + n]) == sub for i in range(len(seq) - n + 1))


def load_synonyms_v2(path: Path = SYNONYMS_V2_PATH, manifest_path: Path = MANIFEST_PATH) -> dict:
    return load_synonyms(path, manifest_path)


def group_terms(label: str, syn: dict) -> list[tuple[str, ...]]:
    """v2: the key terms of a group (word tuples, stemmed): the label's content words, then every `terms` key found in
    the label with its phrases."""
    stop = {stem2(w) for w in syn["stopwords"]} | {stem2(w) for w in syn["non_distinctive"]}
    lab = tokens(label)
    raw = [w for w in tokens(label, stemmed=False)]
    out = [(stem2(w),) for w in raw if len(w) >= syn["min_term_length"] and stem2(w) not in stop]
    for key, phrases in (syn.get("terms") or {}).items():
        k = tuple(tokens(str(key)))
        if _has(lab, k):
            out += [k] + [tuple(tokens(str(ph))) for ph in phrases]
    return list(dict.fromkeys(t for t in out if t))


def recognised(text: str, terms: list[tuple[str, ...]]) -> list[str]:
    seq = tokens(text)
    return [" ".join(t) for t in terms if _has(seq, t)]


def number_values(text: str) -> list[float]:
    """v2: numeric values --- every number in digits (normalised text, thousands separators dropped), and a cardinal
    number-word before a counting noun ("one day", "eleven days"); "half", "twice", "-fold" and the descriptor forms are
    not numbers here."""
    t = bi.normalise_number_text(text or "")
    vals = {float(m.group(0).replace(",", "")) for m in bi.NUMBER_RE.finditer(t)}
    for m in COUNT_NOUN_RE.finditer(t):
        v = bi._WORD_VALUES.get(m.group(1).lower())
        if v is not None:
            vals.add(float(v + (bi._WORD_VALUES[m.group(2).lower()] if m.group(2) else 0)))
    return sorted(vals)


def phrase_classes(rules: dict, plain: dict) -> dict[str, list[str]]:
    """v2: {class id: phrases} --- each DR-DESC-1 v4 magnitude class and rare class (its forms), each tercile class (its
    forms), the plain-language scenario and horizon phrases, and each family's quantity (long and short)."""
    m = rules["magnitude"]
    out = {f"magnitude: {c['increase']}": list(c["forms"]) for c in m["classes"]}
    out |= {f"magnitude: {m[k]['class']}": list(m[k]["forms"]) for k in ("rare_to_common", "remaining_rare")}
    out |= {f"comparison with other states: {k}": list(v) for k, v in rules["tercile"]["forms"].items()}
    out |= {f"scenario: {k}": [v] for k, v in plain["scenario"].items()}
    out |= {f"horizon: {k}": [v] for k, v in plain["horizon"].items()}
    out |= {f"quantity: {k}": [v["quantity"], v["quantity_short"]] for k, v in plain["families"].items()}
    return out


#: v2: relative-clause filler ignored when phrases are compared ("days that are hot and humid enough to be dangerous").
PHRASE_FILLER = frozenset({"that", "which", "is", "are"})


def _phrase_tokens(text: str) -> list[str]:
    return [w for w in tokens(text, stemmed=False) if w not in PHRASE_FILLER]


def classes_in(text: str, classes: dict[str, list[str]]) -> dict[str, list[str]]:
    """The phrase classes `text` uses, with the phrases found (compared as unstemmed tokens, dashes read as spaces,
    `PHRASE_FILLER` words dropped on both sides)."""
    seq = _phrase_tokens(text)
    out = {}
    for k, phs in classes.items():
        hit = [ph for ph in phs if _has(seq, tuple(_phrase_tokens(ph)))]
        if hit:
            out[k] = hit
    return out


def invariance_v2(original: dict, polished: dict, groups: list[dict], nca: dict, syn: dict, rules: dict, plain: dict,
                  columns: list[str] | None = None) -> dict:
    """{check_version, pass, reasons, checks} for a rewrite under checks v2. `groups`: [{group_id, label}] of the groups the
    item cites; `syn`: `polish_synonyms_v2.yaml`; `rules`: DR-DESC-1 v4; `plain`: plain language v1a."""
    cols = columns if columns is not None else bi.column_names()
    names = place_names(nca)
    classes = phrase_classes(rules, plain)
    terms = {g["group_id"]: group_terms(g.get("label") or "", syn) for g in groups}
    reasons: list[str] = []
    checks: dict = {}
    for f in FIELDS:
        o, p = original.get(f) or "", polished.get(f)
        if not isinstance(p, str) or not p.strip():
            reasons.append(f"{f}: missing or empty in the rewrite")
            continue
        c = {}
        a, b = number_values(o), number_values(p)
        c["numbers"] = {"original": a, "polished": b}
        if a != b:
            reasons.append(f"{f}: numbers differ by value (original {a}, polished {b})")
        for name, fn in (("places", lambda t: places(t, names)), ("hedges", hedges)):
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
        per_group = {}
        for gid, ts in terms.items():
            ro, rp = recognised(o, ts), recognised(p, ts)
            if ro:
                per_group[gid] = {"original": ro, "polished": rp}
                if not rp:
                    reasons.append(f"{f}: mechanism of group {gid} lost (no key term of {sorted(set(ro))} or its listed phrases)")
        c["groups_recognised"] = per_group
        co, cp = classes_in(o, classes), classes_in(p, classes)
        c["descriptor_phrases"] = {"original": co, "polished": cp}
        reasons += [f"{f}: descriptor phrase lost: {k} (original {co[k]})" for k in co if k not in cp]
        checks[f] = c
    return {"check_version": VERSION_V2, "pass": not reasons, "reasons": reasons, "checks": checks}
