"""Infrastructure lexicon v1 and the candidate rule DR-CAND-INFRA-1 (work package P5a; D-070, D-071, D-073).

`infrastructure_lexicon_v1.yaml` classifies LITERATURE only (asset classes = the 16 CISA critical-infrastructure sectors;
surface forms; impact terms); it never touches the table. `validate` checks its shape and provenance rules: the sixteen
CISA sector names verbatim and in the page's order, every form's source one of the two allowed values, every EXECUTOR form
`authorization: our_reading`, every CISA form naming a sector page that was read, no form in two classes.

`derive_candidates` re-derives DR-CAND-INFRA-1 from a lexicon-mode `paper_hits.jsonl` independently of
`run_query.py`, so the ingest of the Polaris output can check `candidates.json` (`verify_candidates`). No model call; no
table value.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

LEXICON_PATH = REPO_ROOT / "data" / "metadata" / "litstatements" / "infrastructure_lexicon_v1.yaml"
#: The CISA sector list, verbatim and in the page's order (read 2026-11-23).
CISA_SECTORS = ("Chemical Sector", "Commercial Facilities Sector", "Communications Sector", "Critical Manufacturing Sector",
                "Dams Sector", "Defense Industrial Base Sector", "Emergency Services Sector", "Energy Sector",
                "Financial Services Sector", "Food and Agriculture Sector", "Government Services and Facilities Sector",
                "Healthcare and Public Health Sector", "Information Technology Sector",
                "Nuclear Reactors, Materials, and Waste Sector", "Transportation Systems Sector", "Water and Wastewater Sector")
SOURCES = ("CISA sector list", "EXECUTOR (common usage)")
CAND_RULE = "DR-CAND-INFRA-1"


def load(path: Path = LEXICON_PATH) -> dict:
    return {**yaml.safe_load(path.read_text(encoding="utf-8")), "sha256": sha256_file(path)}


def validate(lex: dict) -> list[str]:
    errs = []
    names = [c["cisa_sector"] for c in lex["asset_classes"]]
    if tuple(names) != CISA_SECTORS:
        errs.append("asset classes are not the sixteen CISA sectors in the page's order")
    pages = set(lex["taxonomy"]["sector_pages_read"])
    seen = {}
    for c in lex["asset_classes"]:
        for f in c["surface_forms"]:
            form = f["form"].lower()
            if form in seen:
                errs.append(f"form {form!r} in {seen[form]} and {c['id']}")
            seen[form] = c["id"]
            if f.get("source") not in SOURCES:
                errs.append(f"{form!r}: source {f.get('source')!r}")
            elif f["source"] == SOURCES[1] and f.get("authorization") != "our_reading":
                errs.append(f"{form!r}: EXECUTOR form without authorization: our_reading")
            elif f["source"] == SOURCES[0] and f.get("cisa_page") not in pages:
                errs.append(f"{form!r}: CISA form names no sector page read")
    for f in lex["impact_terms"]:
        if f.get("source") != SOURCES[1] or f.get("authorization") != "our_reading":
            errs.append(f"impact term {f.get('form')!r}: source / authorization")
        if f["form"].lower() in seen:
            errs.append(f"impact term {f['form']!r} is also an asset form")
    return errs


def counts(lex: dict) -> dict:
    forms = [f for c in lex["asset_classes"] for f in c["surface_forms"]]
    return {"asset_classes": len(lex["asset_classes"]), "surface_forms": len(forms),
            "surface_forms_cisa": sum(f["source"] == SOURCES[0] for f in forms),
            "surface_forms_executor": sum(f["source"] == SOURCES[1] for f in forms),
            "impact_terms": len(lex["impact_terms"]),
            "per_class": {c["id"]: len(c["surface_forms"]) for c in lex["asset_classes"]}}


def class_ids(lex: dict) -> tuple[str, ...]:
    return tuple(c["id"] for c in lex["asset_classes"])


def derive_candidates(papers: list[dict], families: list[str], cap: int) -> dict:
    """DR-CAND-INFRA-1: per family, papers with >= 1 co-occurrence section, ranked by their number (descending; ties by
    doc_id in code-point order), the first `cap`. Returns {family: [(doc_id, n_sections), ...]} and the unique id order."""
    chosen = {}
    for f in families:
        elig = [(p["doc_id"], p["cooc"][f]["n_sections"]) for p in papers if (p.get("cooc") or {}).get(f, {}).get("n_sections", 0) >= 1]
        chosen[f] = sorted(elig, key=lambda x: (-x[1], x[0]))[:cap]
    order = list(dict.fromkeys(d for f in families for d, _ in chosen[f]))
    return {"by_family": chosen, "order": order}


def verify_candidates(candidates: dict, paper_hits_path: Path) -> list[str]:
    """Problems with a lexicon-mode `candidates.json` against its `paper_hits.jsonl` (empty list: it checks)."""
    errs = []
    if sha256_file(paper_hits_path) != candidates["paper_hits_sha256"]:
        errs.append("paper_hits.jsonl differs from the hash candidates.json names")
    papers = [json.loads(x) for x in paper_hits_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    fams = list(candidates["families"])
    d = derive_candidates(papers, fams, candidates["cap_per_family"])
    if [c["item_id"] for c in candidates["candidates"]] != d["order"]:
        errs.append("candidate order differs from DR-CAND-INFRA-1 re-derived")
    for f in fams:
        got = [(c["item_id"], x["n_cooc_sections"]) for c in candidates["candidates"] for x in c["families"] if x["family"] == f]
        got = sorted(got, key=lambda x: (-x[1], x[0]))
        if got != d["by_family"][f]:
            errs.append(f"{f}: selected papers differ from DR-CAND-INFRA-1 re-derived")
        if candidates["by_family"][f]["selected"] != len(d["by_family"][f]):
            errs.append(f"{f}: selected count differs")
    if candidates.get("rule") != CAND_RULE:
        errs.append("rule is not DR-CAND-INFRA-1")
    return errs
