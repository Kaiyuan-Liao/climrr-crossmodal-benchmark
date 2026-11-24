"""Infrastructure lexicon v1 and the candidate rules DR-CAND-INFRA-1 / -2 / -3 (P5a; D-070, D-070a, D-070b, D-071, D-073).

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


# --- P5a hotfix (D-073a): the hazard-proxy lexicon -------------------------------------------------------------------

PROXY_PATH = REPO_ROOT / "data" / "metadata" / "litstatements" / "hazard_proxy_lexicon_v1.yaml"
PROXY_FAMILIES = ("heat_index", "fire_weather_index")
HAZARD_RELATIONS = ("governed_term", "broader_hazard")
PROXY_USE = "literature classification only; never table matching"


def load_proxy(path: Path = PROXY_PATH) -> dict:
    return {**yaml.safe_load(path.read_text(encoding="utf-8")), "sha256": sha256_file(path)}


def proxy_terms(proxy: dict) -> dict[str, list[str]]:
    """{family: [term, ...]} in file order."""
    return {f: [t["term"] for t in proxy["families"][f]["terms"]] for f in proxy["families"]}


def validate_proxy(proxy: dict) -> list[str]:
    """The D-073a shape: the two families, relation broader_hazard, every term EXECUTOR / our_reading / the use line, no
    term in two families, no table use."""
    errs = []
    if tuple(proxy.get("families") or ()) != PROXY_FAMILIES:
        errs.append(f"families are not {PROXY_FAMILIES}")
    if proxy.get("never_used_for") != ["table_columns"] or proxy.get("use") != PROXY_USE:
        errs.append("use / never_used_for not the D-073a lines")
    if tuple(proxy.get("relations") or ()) != HAZARD_RELATIONS:
        errs.append(f"relations are not {HAZARD_RELATIONS}")
    seen = {}
    for f, fam in (proxy.get("families") or {}).items():
        if fam.get("relation") != "broader_hazard":
            errs.append(f"{f}: relation {fam.get('relation')!r}")
        for t in fam["terms"]:
            k = t["term"].lower()
            if k in seen:
                errs.append(f"term {k!r} in {seen[k]} and {f}")
            seen[k] = f
            if t.get("source") != SOURCES[1] or t.get("authorization") != "our_reading" or t.get("use") != PROXY_USE:
                errs.append(f"{f}: {k!r}: source / authorization / use")
    return errs


# --- P5a hotfix: CISA sector names of the corpus tags -> lexicon classes, by name -------------------------------------

def norm_sector(name: str) -> str:
    """Lowercase, '&' -> 'and', every character outside [a-z0-9] a space, a trailing word 'sector' dropped, whitespace
    collapsed. 'Nuclear Reactors, Materials, and Waste Sector' -> 'nuclear reactors materials and waste'."""
    import re

    s = re.sub(r"[^a-z0-9]+", " ", name.lower().replace("&", " and ")).split()
    if s and s[-1] == "sector":
        s = s[:-1]
    return " ".join(s)


def map_sector_name(name: str, lex: dict | None = None) -> dict:
    """{class_id, match} for one sector name as the corpus writes it. `exact`: the normalised name equals a CISA sector
    name normalised; `prefix`: its words are a leading run of exactly one CISA name's words ('Transportation' ->
    'Transportation Systems'); else {class_id: None, match: 'unmapped'}. EXECUTOR rule (the work package: "by name")."""
    lex = lex or load()
    names = [(c["id"], norm_sector(c["cisa_sector"]).split()) for c in lex["asset_classes"]]
    w = norm_sector(name).split()
    exact = [cid for cid, n in names if n == w]
    if exact:
        return {"class_id": exact[0], "match": "exact"}
    pre = [cid for cid, n in names if w and len(w) < len(n) and n[:len(w)] == w]
    return {"class_id": pre[0], "match": "prefix"} if len(pre) == 1 else {"class_id": None, "match": "unmapped"}


# --- P5a hotfix: DR-CAND-INFRA-2 -------------------------------------------------------------------------------------

CAND_RULE_2 = "DR-CAND-INFRA-2"
BASIS_ORDER = ("a", "b")


def derive_candidates_2(papers: list[dict], families: list[str], cap: int) -> dict:
    """DR-CAND-INFRA-2, independently of run_query.py: per family, papers with >= 1 qualifying section, ranked by the
    number of qualifying sections (descending), then basis a before b, then doc_id in code-point order; the first `cap`.
    Returns {"by_family": {family: [(doc_id, n_qualifying, basis), ...]}, "order": [doc_id, ...]}."""
    chosen = {}
    for f in families:
        elig = []
        for p in papers:
            q = (p.get("infra2") or {}).get(f) or {}
            if q.get("n_qualifying_sections", 0) >= 1:
                elig.append((p["doc_id"], q["n_qualifying_sections"], q["basis"]))
        chosen[f] = sorted(elig, key=lambda x: (-x[1], BASIS_ORDER.index(x[2]), x[0]))[:cap]
    order = list(dict.fromkeys(d for f in families for d, _, _ in chosen[f]))
    return {"by_family": chosen, "order": order}


def paper_record_errors_2(p: dict, families: list[str]) -> list[str]:
    """Internal consistency of one INFRA-2 paper record: the counts equal its qualifying-section list; basis a iff a
    co-occurrence section; an untagged paper qualifies only on co-occurrence sections; the paper relation is governed iff
    a qualifying section is."""
    errs, tagged = [], bool(p.get("asset_sector_tag"))
    if p.get("sector_tagged") is not tagged:
        errs.append(f"{p['doc_id']}: sector_tagged does not match asset_sector_tag")
    for f in families:
        q = (p.get("infra2") or {}).get(f)
        if not q:
            continue
        secs = q["qualifying_sections"]
        n_cooc = sum(s["cooc"] for s in secs)
        if q["n_qualifying_sections"] != len(secs) or q["n_cooc_sections"] != n_cooc:
            errs.append(f"{p['doc_id']}/{f}: counts differ from the qualifying sections")
        if secs and q["basis"] != ("a" if n_cooc else "b"):
            errs.append(f"{p['doc_id']}/{f}: basis {q['basis']!r}")
        if not tagged and n_cooc != len(secs):
            errs.append(f"{p['doc_id']}/{f}: an untagged paper qualifies on a section without an asset term")
        rel = "governed_term" if any(s["hazard_relation"] == "governed_term" for s in secs) else ("broader_hazard" if secs else None)
        if q["hazard_relation"] != rel:
            errs.append(f"{p['doc_id']}/{f}: hazard_relation {q['hazard_relation']!r}")
    return errs


def verify_candidates_2(candidates: dict, paper_hits_path: Path) -> list[str]:
    """Problems with a DR-CAND-INFRA-2 `candidates.json` against its `paper_hits.jsonl` (empty list: it checks)."""
    errs = []
    if candidates.get("rule") != CAND_RULE_2:
        return ["rule is not DR-CAND-INFRA-2"]
    if sha256_file(paper_hits_path) != candidates["paper_hits_sha256"]:
        errs.append("paper_hits.jsonl differs from the hash candidates.json names")
    papers = [json.loads(x) for x in paper_hits_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    fams = list(candidates["families"])
    for p in papers:
        errs += paper_record_errors_2(p, fams)
    d = derive_candidates_2(papers, fams, candidates["cap_per_family"])
    if [c["item_id"] for c in candidates["candidates"]] != d["order"]:
        errs.append("candidate order differs from DR-CAND-INFRA-2 re-derived")
    by_id = {p["doc_id"]: p for p in papers}
    for f in fams:
        got = [(c["item_id"], x["n_qualifying_sections"], x["basis"]) for c in candidates["candidates"] for x in c["families"] if x["family"] == f]
        if sorted(got, key=lambda x: (-x[1], BASIS_ORDER.index(x[2]), x[0])) != d["by_family"][f]:
            errs.append(f"{f}: selected papers differ from DR-CAND-INFRA-2 re-derived")
        if candidates["by_family"][f]["selected"] != len(d["by_family"][f]):
            errs.append(f"{f}: selected count differs")
    for c in candidates["candidates"]:
        p = by_id.get(c["item_id"])
        if p is None or c.get("in_186k_set") != p.get("in_186k_set") or c.get("asset_sector_tag") != p.get("asset_sector_tag"):
            errs.append(f"{c['item_id']}: in_186k_set / asset_sector_tag differ from paper_hits")
    return errs


# --- P5a hotfix 2 (D-070b): proxy lexicon v1a (conditional "high temperatures") and DR-CAND-INFRA-3 --------------------

PROXY_V1A_PATH = REPO_ROOT / "data" / "metadata" / "litstatements" / "hazard_proxy_lexicon_v1a.yaml"
#: The work package's co-term list, verbatim, then written out for the no-stemming matcher ("heat wave(s)" -> two terms).
CLIMATE_COTERMS_V1_WP = ("climate", "climate change", "warming", "global warming", "weather", "summer", "heat wave(s)",
                         "heatwave(s)", "extreme heat", "projected", "projection(s)")
CLIMATE_COTERMS_V1 = ("climate", "climate change", "warming", "global warming", "weather", "summer", "heat wave", "heat waves",
                      "heatwave", "heatwaves", "extreme heat", "projected", "projection", "projections")
CONDITIONAL_TERMS_V1A = {("heat_index", "high temperatures"): "climate_coterms_v1"}
CAND_RULE_3 = "DR-CAND-INFRA-3"
RELATION_ORDER = ("governed_term", "broader_hazard")


def expand_plurals(terms) -> tuple[str, ...]:
    """'heat wave(s)' -> 'heat wave', 'heat waves'; other terms unchanged; order kept."""
    out = []
    for t in terms:
        out += [t[:-3], t[:-3] + "s"] if t.endswith("(s)") else [t]
    return tuple(out)


def conditional_terms(proxy: dict) -> dict[tuple[str, str], str]:
    """{(family, term): coterm list name} for every conditional term of a proxy lexicon."""
    return {(f, t["term"].lower()): (t.get("condition") or {}).get("same_section_any_of")
            for f, fam in (proxy.get("families") or {}).items() for t in fam["terms"] if t.get("conditional")}


def validate_proxy_v1a(proxy: dict, base: dict | None = None) -> list[str]:
    """v1's rules, plus D-070b: the terms identical to v1's (same families, order, relation, provenance); exactly
    "high temperatures" conditional, on `climate_coterms_v1`; the list the work package's, plurals written out."""
    errs = validate_proxy(proxy)
    base = base or load_proxy()
    strip = lambda p: {f: [{k: v for k, v in t.items() if k not in ("conditional", "condition")} for t in fam["terms"]]  # noqa: E731
                       for f, fam in p["families"].items()}
    if strip(proxy) != strip(base) or {f: fam["relation"] for f, fam in proxy["families"].items()} != \
            {f: fam["relation"] for f, fam in base["families"].items()}:
        errs.append("terms differ from hazard_proxy_lexicon_v1 beyond the conditional fields")
    if conditional_terms(proxy) != CONDITIONAL_TERMS_V1A:
        errs.append(f"conditional terms are not {CONDITIONAL_TERMS_V1A}")
    lists = proxy.get("coterm_lists") or {}
    if set(lists) != {"climate_coterms_v1"}:
        errs.append("coterm_lists is not exactly climate_coterms_v1")
    elif tuple(lists["climate_coterms_v1"].get("terms") or ()) != CLIMATE_COTERMS_V1 or \
            expand_plurals(CLIMATE_COTERMS_V1_WP) != CLIMATE_COTERMS_V1:
        errs.append("climate_coterms_v1 is not the work package's list")
    elif lists["climate_coterms_v1"].get("use") != PROXY_USE:
        errs.append("climate_coterms_v1: use line")
    return errs


def rank_key_3(impact: bool, n: int, relation: str, doc_id: str) -> tuple:
    return (0 if impact else 1, -n, RELATION_ORDER.index(relation), doc_id)


def derive_candidates_3(papers: list[dict], families: list[str], cap: int) -> dict:
    """DR-CAND-INFRA-3, independently of run_query.py: per family, papers with >= 1 qualifying section, ranked by impact
    true first, then the number of qualifying sections (descending), then governed_term before broader_hazard, then
    doc_id in code-point order; the first `cap`. Returns {"by_family": {family: [doc_id, ...]}, "order": [doc_id, ...]}."""
    chosen = {}
    for f in families:
        elig = [p for p in papers if ((p.get("infra3") or {}).get(f) or {}).get("n_qualifying_sections", 0) >= 1]
        elig.sort(key=lambda p: rank_key_3(p["impact"], p["infra3"][f]["n_qualifying_sections"], p["infra3"][f]["hazard_relation"], p["doc_id"]))
        chosen[f] = [p["doc_id"] for p in elig[:cap]]
    return {"by_family": chosen, "order": list(dict.fromkeys(d for f in families for d in chosen[f]))}


def paper_record_errors_3(p: dict, families: list[str], cond: dict[tuple[str, str], list[str]]) -> list[str]:
    """Internal consistency of one INFRA-3 paper record: every qualifying section holds an asset form and a hazard term of
    the family; a conditional term in it has a co-term of its list; a dropped conditional term has none; the counts equal
    the list; basis a iff qualifying; the relation governed iff a qualifying section holds a governed term; basis_b_only iff
    tagged, a hazard section and none qualifying."""
    errs, tagged = [], bool(p.get("asset_sector_tag"))
    if p.get("sector_tagged") is not tagged:
        errs.append(f"{p['doc_id']}: sector_tagged does not match asset_sector_tag")
    for f in families:
        q = (p.get("infra3") or {}).get(f)
        if not q:
            continue
        secs = q["qualifying_sections"]
        for s in secs:
            if not s["asset_forms"] or not (s["governed_terms"] or s["proxy_terms"]):
                errs.append(f"{p['doc_id']}/{f}/{s['section_idx']}: qualifying section without an asset form or a hazard term")
            for t in s["conditional_terms"]:
                if not set(s["coterms"]) & set(cond.get((f, t), ())):
                    errs.append(f"{p['doc_id']}/{f}/{s['section_idx']}: conditional {t!r} without a co-term")
            if s["conditional_terms_dropped"] and set(s["coterms"]) & {c for t in s["conditional_terms_dropped"] for c in cond.get((f, t), ())}:
                errs.append(f"{p['doc_id']}/{f}/{s['section_idx']}: a dropped conditional term has a co-term")
        if q["n_qualifying_sections"] != len(secs) or q["basis"] != ("a" if secs else None):
            errs.append(f"{p['doc_id']}/{f}: counts / basis differ from the qualifying sections")
        if q["n_hazard_sections"] < len(secs) or q["n_qualifying_sections_before_conditional"] < len(secs):
            errs.append(f"{p['doc_id']}/{f}: fewer hazard / before-conditional sections than qualifying sections")
        rel = ("governed_term" if any(s["governed_terms"] for s in secs) else "broader_hazard") if secs else None
        if q["hazard_relation"] != rel:
            errs.append(f"{p['doc_id']}/{f}: hazard_relation {q['hazard_relation']!r}")
        if q["basis_b_only"] != bool(tagged and q["n_hazard_sections"] and not secs):
            errs.append(f"{p['doc_id']}/{f}: basis_b_only")
    return errs


def verify_candidates_3(candidates: dict, paper_hits_path: Path, basis_b_path: Path | None = None) -> list[str]:
    """Problems with a DR-CAND-INFRA-3 `candidates.json` against its `paper_hits.jsonl` (and `basis_b_only.json` if given);
    an empty list: it checks."""
    errs = []
    if candidates.get("rule") != CAND_RULE_3:
        return ["rule is not DR-CAND-INFRA-3"]
    if sha256_file(paper_hits_path) != candidates["paper_hits_sha256"]:
        errs.append("paper_hits.jsonl differs from the hash candidates.json names")
    papers = [json.loads(x) for x in paper_hits_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    fams = list(candidates["families"])
    lists = candidates["proxy_lexicon"]["coterm_lists"]
    cond = {tuple(k.split(":", 1)): lists[ln] for k, ln in candidates["proxy_lexicon"]["conditional_terms"].items()}
    for p in papers:
        errs += paper_record_errors_3(p, fams, cond)
    d = derive_candidates_3(papers, fams, candidates["cap_per_family"])
    if [c["item_id"] for c in candidates["candidates"]] != d["order"]:
        errs.append("candidate order differs from DR-CAND-INFRA-3 re-derived")
    by_id = {p["doc_id"]: p for p in papers}
    for f in fams:
        got = [(x["rank"], c["item_id"]) for c in candidates["candidates"] for x in c["families"] if x["family"] == f]
        if [i for _, i in sorted(got)] != d["by_family"][f]:
            errs.append(f"{f}: selected papers or ranks differ from DR-CAND-INFRA-3 re-derived")
        if candidates["by_family"][f]["selected"] != len(d["by_family"][f]) or candidates["report"][f]["candidates"]["n"] != len(d["by_family"][f]):
            errs.append(f"{f}: selected count differs")
    for c in candidates["candidates"]:
        p = by_id.get(c["item_id"])
        if p is None or any(c.get(k) != p.get(k) for k in ("in_186k_set", "asset_sector_tag", "impact")) or set(c["basis"].values()) != {"a"}:
            errs.append(f"{c['item_id']}: in_186k_set / asset_sector_tag / impact / basis differ from paper_hits")
    if basis_b_path is not None:
        if sha256_file(basis_b_path) != candidates["basis_b_only_sha256"]:
            errs.append("basis_b_only.json differs from the hash candidates.json names")
        bb = json.loads(basis_b_path.read_text(encoding="utf-8"))
        for f in fams:
            want = sorted(p["doc_id"] for p in papers if ((p.get("infra3") or {}).get(f) or {}).get("basis_b_only"))
            if [x["doc_id"] for x in bb["families"][f]["papers"]] != want or bb["families"][f]["n"] != len(want):
                errs.append(f"{f}: basis_b_only.json differs from paper_hits")
            if set(want) & set(d["by_family"][f]):
                errs.append(f"{f}: a basis-b-only paper is a candidate")
    return errs
