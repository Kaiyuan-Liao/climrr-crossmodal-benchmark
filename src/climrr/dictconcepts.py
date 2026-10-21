"""Stage 2a --- the dictionary concept inventory (Track B, diagnostic).

Authorized by `docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md` (D-025,
Stage 2a, criteria 23--25). The inventory lists the **ClimRR output quantities
the dictionary's narrative describes** (pp. 4--12), one entry each, so the
Stage 2b/2c survey has a dictionary-grounded concept to propose surface forms
for and count. It assigns **no meaning to any CSV column**; existing M1
statuses are unchanged; index 117 remains unlabeled.

Granularity (confirmed by Kaiyuan Liao, 2026-10-20 --- D-026): **measure
level**. One concept per output quantity the narrative describes. Where the
dictionary describes two quantities in one passage (maximum and minimum daily
temperature; HDD and CDD) they stay one concept, because the dictionary
presents them together. The heat index is split as the dictionary enumerates
it, with the four thresholds as four concepts (p. 12: "the 6 variables").
Methodology sections (Climate Scenarios, Downscaled Climate Models, Ensemble
Means, Components of the FWI) are not output quantities and are excluded; the
variable lists on pp. 4 and 13 are not separate concepts.

Every string the inventory stores --- name, passage, units, threshold,
scenario --- is an **exact slice of the pypdf text of one page**. The anchors
below only *locate* a slice (whitespace in an anchor matches any run of
whitespace in the page text); what is written is always the page's own
characters, so `page_text[start:end] == passage` holds by construction and is
re-checked by test.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

STATEMENT = (
    "Inventory of dictionary-described concepts for the Stage 2 coverage survey "
    "(diagnostic). It assigns no meaning to any CSV column; existing M1 statuses "
    "are unchanged; index 117 remains unlabeled."
)

SCHEMA_VERSION = "dc-v1"


@dataclass(frozen=True)
class Spec:
    """Where one concept's strings sit in the dictionary.

    `name_re` has exactly one capture group (the name). `name_occurrence`
    "only" demands a single match on the page; "first" takes the first of
    several (used for the per-threshold names, which the field table on p. 18
    repeats once per period). `passage` is (start anchor, end anchor): the
    passage runs from the start of the first start-anchor match to the end of
    the first end-anchor match after it. `units`, `metric_or_threshold` and
    `scenario_or_horizon` are anchors searched inside the passage, or inside
    the name when `*_in` says so; `None` means the passage does not state it.
    """

    name_page: int
    name_re: str
    passage_page: int
    passage: tuple[str, str] | None
    name_occurrence: str = "only"
    units: str | None = None
    metric_or_threshold: str | None = None
    metric_in: str = "passage"
    scenario_or_horizon: str | None = None


def _heading(title: str) -> str:
    return r"(?m)^(" + re.escape(title) + r") *$"


_HI3_START = "3. Number of summer days with daily max heat index above 95 / 105 / 115 / 125"  # U+F0B0 follows in the PDF text
_HI3_END = "to calculate the number of summer days in"


def _threshold(value: str) -> Spec:
    name = f"Number of Summer days with daily max heat index above {value} F"
    return Spec(
        name_page=18,
        name_re="(" + re.escape(name) + ")",
        name_occurrence="first",
        passage_page=11,
        passage=(_HI3_START, _HI3_END),
        metric_or_threshold=f"above {value} F",
        metric_in="name",
    )


# Document order. Ids DC-001... are assigned from this order and frozen.
SPECS: tuple[Spec, ...] = (
    Spec(6, _heading("Temperature (Annual)"), 6,
         ("Each climate model generates temperature readings",
          "both the maximum and minimum daily temperatures.")),
    Spec(7, _heading("Temperature (Seasonal)"), 7,
         ("Each climate model generates temperature readings",
          "autumn (Sep, Oct, Nov).")),
    Spec(7, _heading("Precipitation"), 7,
         ("Argonne calculated total annual precipitation",
          "precipitation (in inches) for each time period/scenario."),
         units="inches"),
    Spec(7, _heading("Wind Speed"), 7,
         ("Each climate model generates estimated wind speed readings",
          "average wind speed (in mph) for each time period/scenario."),
         units="mph"),
    Spec(8, _heading("Consecutive Days with No Precipitation"), 8,
         ("Using this information, Argonne identified",
          "consecutive days without precipitation in a single year."),
         metric_or_threshold="the total daily precipitation quantity equaled zero"),
    Spec(8, _heading("Degree Days (HDD/CDD)"), 8,
         ("Degree days measure how cold or warm",
          "has 25 CDD (90 – 65 = 25 CDD)."),
         metric_or_threshold="65°F (18.33°C)"),
    # The narrower heading "Calculating Seasonal Averages" (p. 9) names only a
    # procedure, so the enclosing section heading names the quantity.
    Spec(8, _heading("Fire Weather Index"), 10,
         ("Argonne calculated the average daily FWI value by season",
          "seasonal average daily FWI value.")),
    Spec(10, _heading("Calculating FWI Classes"), 10,
         ("Daily FWI values were used to calculate seasonal and annual 95th percentile",
          "(e.g., winter historical FWI class)."),
         metric_or_threshold="95th percentile",
         scenario_or_horizon="historical, mid-century RCP8.5, and end-of-century RCP8.5"),
    Spec(11, r"1\. (Summer daily maximum heat index):", 11,
         ("1. Summer daily maximum heat index:", "to produce the ensemble mean.")),
    Spec(11, r"2\. (Summer seasonal maximum heat index):", 11,
         ("2. Summer seasonal maximum heat index:", "to produce the ensemble mean.")),
    _threshold("95"),
    _threshold("105"),
    _threshold("115"),
    _threshold("125"),
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_pages(pdf_path: Path) -> list[str]:
    """pypdf text of every page, in the PDF's order (index 0 = page 1)."""
    import pypdf

    return [page.extract_text() or "" for page in pypdf.PdfReader(str(pdf_path)).pages]


def _flex(anchor: str) -> str:
    return r"\s+".join(re.escape(part) for part in anchor.split())


def _find(pattern: str, text: str, start: int = 0, end: int | None = None) -> tuple[int, int]:
    m = re.compile(pattern).search(text, start, len(text) if end is None else end)
    if m is None:
        raise ValueError(f"anchor not found: {pattern!r}")
    return m.start(), m.end()


def locate_name(spec: Spec, page_text: str) -> tuple[int, int]:
    matches = list(re.finditer(spec.name_re, page_text))
    if not matches:
        raise ValueError(f"name not found on page {spec.name_page}: {spec.name_re!r}")
    if spec.name_occurrence == "only" and len(matches) != 1:
        raise ValueError(f"name matches {len(matches)} times on page {spec.name_page}: {spec.name_re!r}")
    return matches[0].span(1)


def locate_passage(spec: Spec, page_text: str) -> tuple[int, int]:
    assert spec.passage is not None
    start, _ = _find(_flex(spec.passage[0]), page_text)
    _, end = _find(_flex(spec.passage[1]), page_text, start)
    return start, end


def _field(anchor: str | None, text: str) -> str | None:
    if anchor is None:
        return None
    s, e = _find(_flex(anchor), text)
    return text[s:e]


def build_concepts(pages: list[str], verified: dict[int, list[str]] | None = None) -> list[dict]:
    """One entry per spec, in order. `verified` maps a verified column index to
    the texts of the resolution records it cites (see `verified_columns_for`)."""
    concepts = []
    for n, spec in enumerate(SPECS, start=1):
        name_text = pages[spec.name_page - 1]
        ns, ne = locate_name(spec, name_text)
        name = name_text[ns:ne]
        if spec.passage is None:
            entry = {
                "id": f"DC-{n:03d}", "name": name,
                "name_source": {"page": spec.name_page, "char_span": [ns, ne]},
                "passage": None, "page": None, "char_span": None,
                "units": None, "metric_or_threshold": None, "scenario_or_horizon": None,
                "family_hint": None, "verified_columns": [], "status": "listed_only",
            }
            concepts.append(entry)
            continue
        page_text = pages[spec.passage_page - 1]
        ps, pe = locate_passage(spec, page_text)
        passage = page_text[ps:pe]
        concepts.append({
            "id": f"DC-{n:03d}",
            "name": name,
            "name_source": {"page": spec.name_page, "char_span": [ns, ne]},
            "passage": passage,
            "page": spec.passage_page,
            "char_span": [ps, pe],
            "units": _field(spec.units, passage),
            "metric_or_threshold": _field(spec.metric_or_threshold,
                                          name if spec.metric_in == "name" else passage),
            "scenario_or_horizon": _field(spec.scenario_or_horizon, passage),
            "family_hint": None,
            "verified_columns": verified_columns_for(passage, verified or {}),
            "status": "dictionary_described",
        })
    return concepts


def _norm(text: str) -> str:
    return " ".join(text.split())


def verified_columns_for(passage: str, verified: dict[int, list[str]]) -> list[int]:
    """Verified column indices whose resolution record cites this passage.

    The work package's rule, applied literally: a column qualifies only if its
    M1 status is already `verified_from_dictionary` AND one of the resolution
    records it references quotes this passage. `verified_from_dictionary` is
    assigned by the dictionary rules, never by a resolution record (rule 1 of
    `data/metadata/resolutions.yaml`), and no verified column references one
    today --- so every list is empty unless that changes.
    """
    target = _norm(passage)
    return sorted(i for i, texts in verified.items() if any(target in _norm(t) for t in texts))


def load_verified(coverage_path: Path, resolutions_path: Path) -> dict[int, list[str]]:
    """{column index: [text of each resolution record it references]} for every
    `verified_from_dictionary` column in the M1 coverage artifact."""
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    records = {
        r["id"]: " ".join(str(r.get(k) or "") for k in ("statement", "source_detail", "notes"))
        for r in (yaml.safe_load(resolutions_path.read_text(encoding="utf-8")).get("resolutions") or [])
    }
    return {
        c["index"]: [records[ref] for ref in c.get("resolution_refs") or [] if ref in records]
        for c in coverage["columns"]
        if c["status"] == "verified_from_dictionary"
    }


def render_yaml(concepts: list[dict], *, header: dict) -> str:
    """Deterministic YAML: no timestamps, fixed key order, so the file's bytes
    (and its manifest hash) depend only on the PDF, the extractor and SPECS."""
    preamble = (
        "# Stage 2a dictionary concept inventory --- GENERATED by\n"
        "# scripts/build_dictionary_inventory.py. Never hand-edited; regenerate.\n"
        "# " + STATEMENT + "\n"
        "# family_hint is always null: family assignment is a GUIDANCE decision.\n"
        "# Ids are frozen after Track B Stage 2a.\n"
    )
    body = yaml.safe_dump(
        {**header, "concepts": concepts},
        sort_keys=False, allow_unicode=True, width=100, default_flow_style=None,
    )
    return preamble + body
