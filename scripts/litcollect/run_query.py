#!/usr/bin/env python3
"""Run a frozen boolean query over a build_index.py index. Deterministic, auditable, streaming.

Query grammar (exactly the subset used by the frozen v1 files; anything else is refused):
    query := group ( AND group )*
    group := '(' term ( OR term )* ')'  |  term
    term  := "quoted phrase"  |  bareword
Semantics (aligned with the araiadoc DuckDB matcher): a term matches a document when some
string section of the document satisfies
    regexp_matches(text, '\\b' || escape(term) || '\\b', 'i')
i.e. whole-word, case-insensitive, no stemming. Matching is per section (a phrase cannot
straddle a section boundary). Terms are regex-escaped; the v1 terms contain no regex
metacharacters other than '-', which is literal, so results equal the unescaped matcher.
A document matches the query when every group has at least one matching term.

Implementation: ONE streaming scan of the Parquet sections per query, evaluating every
term as a boolean column and aggregating with bool_or() per doc_id. Memory stays small
(186k rows x ~40 booleans); nothing is materialized from the text.

Optional disambiguation (GUIDANCE ruling 2026-10-12): --disambiguate 'fwi=fire weather|fire-weather'
a document whose ONLY matching term in group 1 is the bare 'fwi' is admitted only if one of
the disambiguators occurs in the same document. Raw and post-disambiguation counts reported.

Outputs under --out (refuses a non-empty dir):
  summary.json, ids.txt (admitted, sorted), ids_raw.txt, disambiguation.csv (if used),
  hits.csv: doc_id, rel_path, sha256, group, term, section_key, section_idx, char_start, char_end
            first occurrence per (doc, term, section); zero-based code-point offsets into the
            UNNORMALIZED decoded string (case-insensitive search on the original text).

v4 (work package P5a; D-070, D-071): an opt-in LEXICON MODE, `--lexicon <infrastructure_lexicon_v1.yaml>` with one or
more `--family NAME=QUERYFILE` (each query file one OR group of governed hazard terms, e.g. the frozen LITCORPUS-02
topical-only queries) and optional `--family-disambiguate 'NAME:bare=t1|t2'` (R-FWI-1: a bare-only hit counts only when a
disambiguator occurs in the same document). One pass reports, per paper: hazard-family hits, asset-class hits, impact-term
hits and CO-OCCURRENCE WITHIN A SECTION (a section holding a hazard term of the family and an asset term). Every
membership decision is DuckDB's (`regexp_matches`, the matcher above); no offsets are computed in this mode. Candidate
rule DR-CAND-INFRA-1: papers with >= 1 co-occurrence section for a family, ranked by the number of such sections (ties:
doc_id in code-point order), the top `--cap` (default 300) per family; the full distribution is reported. Outputs:
summary.json, paper_hits.jsonl (every paper with a hazard-family hit), candidates.json. Without --lexicon the script
behaves exactly as v3. Lexicon mode needs PyYAML (present in the Polaris env: `python -c "import yaml, duckdb"`).
"""
import argparse, csv, hashlib, json, re, sys, time
from pathlib import Path

import duckdb


def tokenize(s: str):
    toks, i = [], 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
        elif c in "()":
            toks.append(("P", c)); i += 1
        elif c == '"':
            j = s.index('"', i + 1)
            toks.append(("T", s[i + 1:j])); i = j + 1
        else:
            j = i
            while j < len(s) and not s[j].isspace() and s[j] not in '()"':
                j += 1
            w = s[i:j]
            toks.append(("K", w.upper()) if w.upper() in ("AND", "OR", "NOT") else ("T", w)); i = j
    return toks


def parse(s: str):
    toks = tokenize(s)
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else (None, None)

    def take():
        t = toks[pos[0]]; pos[0] += 1; return t

    def take_term():
        k, v = take()
        if k != "T":
            raise ValueError(f"expected a term, got {v!r}")
        return v.strip().lower()

    def group():
        k, v = peek()
        if k == "P" and v == "(":
            take(); terms = [take_term()]
            while peek() == ("K", "OR"):
                take(); terms.append(take_term())
            if take() != ("P", ")"):
                raise ValueError("expected ')'")
            return terms
        return [take_term()]

    groups = [group()]
    while peek() == ("K", "AND"):
        take(); groups.append(group())
    if pos[0] != len(toks):
        raise ValueError(f"unparsed tokens from position {pos[0]}: {toks[pos[0]:pos[0]+5]} (NOT and nested groups are not supported)")
    return groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True)
    ap.add_argument("--query-file", default=None, help="required unless --lexicon is given")
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default=None)
    ap.add_argument("--disambiguate", default=None, help="e.g. 'fwi=fire weather|fire-weather'")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--memory-limit", default="4GB")
    ap.add_argument("--no-hits", action="store_true", help="skip the per-section offset stage (counts and id sets only); for diagnostic surveys with large admitted sets")
    ap.add_argument("--lexicon", default=None, help="v4 lexicon mode: infrastructure lexicon YAML")
    ap.add_argument("--family", action="append", default=[], help="lexicon mode: NAME=QUERYFILE (one OR group), repeatable")
    ap.add_argument("--family-disambiguate", action="append", default=[], help="lexicon mode: 'NAME:bare=t1|t2', repeatable")
    ap.add_argument("--cap", type=int, default=300, help="lexicon mode: DR-CAND-INFRA-1 cap per hazard family")
    a = ap.parse_args()
    if a.lexicon:
        if a.query_file or a.disambiguate:
            sys.exit("--lexicon mode takes --family / --family-disambiguate, not --query-file / --disambiguate")
        return lexicon_main(a)
    if not a.query_file:
        sys.exit("--query-file is required (or --lexicon)")

    out = Path(a.out)
    if out.exists() and any(out.iterdir()):
        sys.exit(f"refusing to write into non-empty {out}")
    out.mkdir(parents=True, exist_ok=True)
    idx = Path(a.index)
    qtext = Path(a.query_file).read_text(encoding="utf-8")
    qsha = hashlib.sha256(qtext.encode("utf-8")).hexdigest()
    groups = parse(qtext)
    dis_bare, dis_terms = None, []
    if a.disambiguate:
        b, d = a.disambiguate.split("=", 1)
        dis_bare, dis_terms = b.strip().lower(), [x.strip().lower() for x in d.split("|")]
    t0 = time.time()

    con = duckdb.connect()
    con.execute(f"SET threads={a.threads}"); con.execute(f"SET memory_limit='{a.memory_limit}'")
    con.execute("SET preserve_insertion_order=false")
    (out / "_duckdb_tmp").mkdir(exist_ok=True); con.execute(f"SET temp_directory='{(out/'_duckdb_tmp').as_posix()}'")
    sec_glob, doc_glob = f"{(idx/'sections').as_posix()}/*.parquet", f"{(idx/'docs').as_posix()}/*.parquet"

    # One streaming scan: every term (and disambiguator) as a boolean column, bool_or per doc.
    cols, names = [], []  # names: (kind, term) where kind = group index or 'D'
    for gi, g in enumerate(groups):
        for t in g:
            names.append((gi, t))
    for d in dis_terms:
        names.append(("D", d))
    for i, (_, t) in enumerate(names):
        pat = r"\b" + re.escape(t) + r"\b"
        cols.append(f"bool_or(regexp_matches(text, {duckdb_str(pat)}, 'i')) AS c{i}")
    sql = f"SELECT doc_id, {', '.join(cols)} FROM read_parquet('{sec_glob}') GROUP BY doc_id"
    rows = con.execute(sql).fetchall()
    n_docs = len(rows)
    term_docs = {nm: set() for nm in names}
    for r in rows:
        for i, nm in enumerate(names):
            if r[i + 1]:
                term_docs[nm].add(r[0])
    group_docs = [set().union(*[term_docs[(gi, t)] for t in g]) for gi, g in enumerate(groups)]
    raw_ids = set.intersection(*group_docs) if group_docs else set()

    dis_rows, admitted = [], set(raw_ids)
    if dis_bare is not None:
        dis_docs = set().union(*[term_docs[("D", d)] for d in dis_terms]) if dis_terms else set()
        for did in sorted(raw_ids):
            matched_g0 = {t for t in groups[0] if did in term_docs[(0, t)]}
            bare_only = matched_g0 == {dis_bare}
            found = did in dis_docs
            ok = (not bare_only) or found
            dis_rows.append((did, int(bare_only), int(found), int(ok)))
            if not ok:
                admitted.discard(did)

    # Exact offsets on the unnormalized strings, for admitted docs only.
    hits = []
    if admitted and not a.no_hits:
        con.execute("CREATE TABLE adm(doc_id VARCHAR)"); con.executemany("INSERT INTO adm VALUES (?)", [(d,) for d in sorted(admitted)])
        meta = {r[0]: (r[1], r[2]) for r in con.execute(f"SELECT d.doc_id, d.rel_path, d.sha256 FROM read_parquet('{doc_glob}') d JOIN adm USING(doc_id)").fetchall()}
        secs = con.execute(f"SELECT s.doc_id, s.section_idx, s.section_key, s.text FROM read_parquet('{sec_glob}') s JOIN adm USING(doc_id) ORDER BY s.doc_id, s.section_idx").fetchall()
        compiled = [(k, t, re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE)) for k, t in names]
        for did, sidx, skey, text in secs:
            for k, t, rx in compiled:
                m = rx.search(text)
                if m:
                    hits.append((did, meta[did][0], meta[did][1], k, t, skey, sidx, m.start(), m.end()))

    with open(out / "hits.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["doc_id", "rel_path", "sha256", "group", "term", "section_key", "section_idx", "char_start", "char_end"]); w.writerows(hits)
    (out / "ids.txt").write_text("".join(f"{d}\n" for d in sorted(admitted)))
    (out / "ids_raw.txt").write_text("".join(f"{d}\n" for d in sorted(raw_ids)))
    if dis_bare is not None:
        with open(out / "disambiguation.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["doc_id", "bare_fwi_only", "disambiguator_found", "admitted"]); w.writerows(dis_rows)
    try:
        (out / "_duckdb_tmp").rmdir()
    except OSError:
        pass

    idx_summary = json.loads((idx / "index_summary.json").read_text()) if (idx / "index_summary.json").exists() else {}
    summary = {
        "name": a.name or out.name,
        "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "query_file": Path(a.query_file).name, "query_sha256": qsha, "query_text": qtext,
        "parsed_groups": groups,
        "matcher": "per-section whole-word, case-insensitive, no stemming: regexp_matches(text, '\\b'+escape(term)+'\\b', 'i'); doc matches iff every group has a matching term in some section",
        "index": {"path": idx.as_posix(), "content_identity_sha256": idx_summary.get("content_identity_sha256"), "files": idx_summary.get("files")},
        "documents_in_index": n_docs,
        "per_group_doc_counts": [len(s) for s in group_docs],
        "per_term_doc_counts": {f"g{k}:{t}": len(s) for (k, t), s in term_docs.items()},
        "raw_count": len(raw_ids),
        "disambiguation": a.disambiguate,
        "admitted_count": len(admitted),
        "excluded_by_disambiguation": len(raw_ids) - len(admitted),
        "hits_recorded": not a.no_hits,
        "elapsed_seconds": round(time.time() - t0, 1),
        "duckdb_version": duckdb.__version__, "threads": a.threads, "memory_limit": a.memory_limit,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: summary[k] for k in ("name", "documents_in_index", "per_group_doc_counts", "raw_count", "admitted_count", "excluded_by_disambiguation", "elapsed_seconds")}, indent=2))


def duckdb_str(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


# --- v4 lexicon mode (P5a) ------------------------------------------------------------------------------------------

CAND_RULE = "DR-CAND-INFRA-1"
CAND_RULE_TEXT = ("papers with >= 1 section containing a hazard term of the family and an asset term; ranked by the number of "
                  "such sections, descending, ties by doc_id in code-point order; the top `cap` per hazard family")
CAND_ARM = "infra_impact_v1"


def word_pattern(terms) -> str:
    """One whole-word, case-insensitive alternation: '\\b(?:t1|t2)\\b' with every term regex-escaped."""
    return r"\b(?:" + "|".join(re.escape(t) for t in terms) + r")\b"


def load_lexicon(path: Path) -> dict:
    import yaml  # lexicon mode only

    lex = yaml.safe_load(path.read_text(encoding="utf-8"))
    classes = [(c["id"], [f["form"].lower() for f in c["surface_forms"]]) for c in lex["asset_classes"]]
    impact = [f["form"].lower() for f in lex["impact_terms"]]
    return {"version": lex["version"], "classes": classes, "impact": impact}


def select_candidates(papers: list, families: list, cap: int) -> dict:
    """DR-CAND-INFRA-1 over paper_hits records. Returns {"by_family": {F: {eligible, selected, distribution, ids}},
    "candidates": [{item_id, arm, families: [{family, rank, n_cooc_sections}]}]} (ids unique; family order, then rank)."""
    by_family, order, entry = {}, [], {}
    for f in families:
        elig = sorted(((p["cooc"][f]["n_sections"], p["doc_id"]) for p in papers if p["cooc"].get(f, {}).get("n_sections", 0) >= 1),
                      key=lambda x: (-x[0], x[1]))
        dist = {}
        for n, _ in elig:
            dist[str(n)] = dist.get(str(n), 0) + 1
        chosen = elig[:cap]
        by_family[f] = {"eligible": len(elig), "selected": len(chosen),
                        "distribution_n_cooc_sections": dict(sorted(dist.items(), key=lambda kv: int(kv[0]))),
                        "cutoff_n_cooc_sections": chosen[-1][0] if chosen else None,
                        "ids": [d for _, d in chosen]}
        for rank, (n, d) in enumerate(chosen, 1):
            if d not in entry:
                entry[d] = {"item_id": d, "arm": CAND_ARM, "families": []}
                order.append(d)
            entry[d]["families"].append({"family": f, "rank": rank, "n_cooc_sections": n})
    return {"by_family": by_family, "candidates": [entry[d] for d in order]}


def lexicon_main(a):
    out = Path(a.out)
    if out.exists() and any(out.iterdir()):
        sys.exit(f"refusing to write into non-empty {out}")
    out.mkdir(parents=True, exist_ok=True)
    idx, lex_path = Path(a.index), Path(a.lexicon)
    lex_text = lex_path.read_text(encoding="utf-8")
    lex = load_lexicon(lex_path)
    fams, fam_files = [], {}
    for spec in a.family:
        name, qf = spec.split("=", 1)
        qtext = Path(qf).read_text(encoding="utf-8")
        groups = parse(qtext)
        if len(groups) != 1:
            sys.exit(f"--family {name}: the query must be ONE OR group of hazard terms, got {len(groups)} groups")
        fams.append((name.strip(), groups[0]))
        fam_files[name.strip()] = {"query_file": Path(qf).name, "query_sha256": hashlib.sha256(qtext.encode("utf-8")).hexdigest(),
                                   "terms": groups[0]}
    if not fams:
        sys.exit("--lexicon needs at least one --family NAME=QUERYFILE")
    dis = {}
    for spec in a.family_disambiguate:
        name, rest = spec.split(":", 1)
        bare, terms = rest.split("=", 1)
        dis[name.strip()] = (bare.strip().lower(), [x.strip().lower() for x in terms.split("|")])
    unknown = sorted(set(dis) - {f for f, _ in fams})
    if unknown:
        sys.exit(f"--family-disambiguate names no --family: {unknown}")
    t0 = time.time()
    con = duckdb.connect()
    con.execute(f"SET threads={a.threads}"); con.execute(f"SET memory_limit='{a.memory_limit}'")
    con.execute("SET preserve_insertion_order=false")
    (out / "_duckdb_tmp").mkdir(exist_ok=True); con.execute(f"SET temp_directory='{(out/'_duckdb_tmp').as_posix()}'")
    sec_glob, doc_glob = f"{(idx/'sections').as_posix()}/*.parquet", f"{(idx/'docs').as_posix()}/*.parquet"
    rx = lambda pat: f"regexp_matches(text, {duckdb_str(pat)}, 'i')"  # noqa: E731

    # Pass 1, document level: every hazard term, every disambiguator, every asset class, the impact terms.
    hz = [(f, t) for f, terms in fams for t in terms]
    dz = [(f, t) for f, (_, ts) in dis.items() for t in ts]
    cols = [f"bool_or({rx(word_pattern([t]))})" for _, t in hz] + [f"bool_or({rx(word_pattern([t]))})" for _, t in dz] + \
           [f"bool_or({rx(word_pattern(forms))})" for _, forms in lex["classes"]] + [f"bool_or({rx(word_pattern(lex['impact']))})"]
    rows = con.execute(f"SELECT doc_id, {', '.join(cols)} FROM read_parquet('{sec_glob}') GROUP BY doc_id").fetchall()
    n_docs = len(rows)
    nh, nd, nc = len(hz), len(dz), len(lex["classes"])
    doc = {}
    for r in rows:
        v = r[1:]
        doc[r[0]] = {"hz": {hz[i] for i in range(nh) if v[i]}, "dz": {dz[i] for i in range(nd) if v[nh + i]},
                     "classes": [lex["classes"][i][0] for i in range(nc) if v[nh + nd + i]], "impact": bool(v[nh + nd + nc])}

    def family_ok(f, matched_terms, doc_dz):
        """R-FWI-1: matched only by the bare term -> needs a disambiguator in the document."""
        if not matched_terms:
            return False
        if f in dis and matched_terms == {dis[f][0]}:
            return any((f, t) in doc_dz for t in dis[f][1])
        return True

    # Pass 2, section level, only sections with a hazard term: hazard terms, asset forms, impact forms.
    forms = [(c, x) for c, fs in lex["classes"] for x in fs]
    all_hz = sorted({t for _, t in hz})
    cols2 = [rx(word_pattern([t])) for t in all_hz] + [rx(word_pattern([x])) for _, x in forms] + [rx(word_pattern([x])) for x in lex["impact"]]
    secs = con.execute(f"SELECT doc_id, section_idx, section_key, {', '.join(cols2)} FROM read_parquet('{sec_glob}') "
                       f"WHERE {rx(word_pattern(all_hz))} ORDER BY doc_id, section_idx").fetchall()
    meta = {r[0]: (r[1], r[2]) for r in con.execute(f"SELECT doc_id, rel_path, sha256 FROM read_parquet('{doc_glob}')").fetchall()}
    nt, nf = len(all_hz), len(forms)
    cooc = {}
    for r in secs:
        did, sidx, skey, v = r[0], r[1], r[2], r[3:]
        terms = {all_hz[i] for i in range(nt) if v[i]}
        hit_forms = [forms[i] for i in range(nf) if v[nt + i]]
        if not hit_forms:
            continue
        imp = [lex["impact"][i] for i in range(len(lex["impact"])) if v[nt + nf + i]]
        for f, fterms in fams:
            ft = terms & set(fterms)
            if family_ok(f, ft, doc[did]["dz"]):
                cooc.setdefault(did, {}).setdefault(f, []).append({
                    "section_idx": sidx, "section_key": skey, "hazard_terms": sorted(ft),
                    "asset_classes": sorted({c for c, _ in hit_forms}), "asset_forms": sorted({x for _, x in hit_forms}),
                    "impact_forms": sorted(imp)})

    papers = []
    for did in sorted(doc):
        d = doc[did]
        fam_hits = {}
        for f, fterms in fams:
            ft = {t for (ff, t) in d["hz"] if ff == f}
            if ft:
                fam_hits[f] = {"terms": sorted(ft), "admitted": family_ok(f, ft, d["dz"])}
        if not fam_hits:
            continue
        c = cooc.get(did, {})
        papers.append({"doc_id": did, "rel_path": meta.get(did, (None, None))[0], "sha256": meta.get(did, (None, None))[1],
                       "families": fam_hits, "asset_classes": d["classes"], "impact": d["impact"],
                       "cooc": {f: {"n_sections": len(c[f]), "sections": c[f]} for f in c}})
    sel = select_candidates(papers, [f for f, _ in fams], a.cap)
    with open(out / "paper_hits.jsonl", "w", encoding="utf-8") as fh:
        for p in papers:
            fh.write(json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n")
    try:
        (out / "_duckdb_tmp").rmdir()
    except OSError:
        pass
    idx_summary = json.loads((idx / "index_summary.json").read_text()) if (idx / "index_summary.json").exists() else {}
    paper_hits_sha = hashlib.sha256((out / "paper_hits.jsonl").read_bytes()).hexdigest()
    cand = {"rule": CAND_RULE, "rule_text": CAND_RULE_TEXT, "cap_per_family": a.cap, "arm": CAND_ARM,
            "lexicon": {"file": lex_path.name, "version": lex["version"], "sha256": hashlib.sha256(lex_text.encode("utf-8")).hexdigest()},
            "families": fam_files, "family_disambiguation": {f: {"bare": b, "disambiguators": ts} for f, (b, ts) in dis.items()},
            "index_content_identity_sha256": idx_summary.get("content_identity_sha256"), "paper_hits_sha256": paper_hits_sha,
            "by_family": {f: {k: v for k, v in x.items() if k != "ids"} for f, x in sel["by_family"].items()},
            "n_candidates": len(sel["candidates"]), "candidates": sel["candidates"]}
    (out / "candidates.json").write_text(json.dumps(cand, indent=2, ensure_ascii=False) + "\n")
    summary = {
        "name": a.name or out.name, "mode": "lexicon (run_query v4)",
        "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "matcher": "per-section whole-word, case-insensitive, no stemming: regexp_matches(text, '\\b'+escape(term)+'\\b', 'i'); co-occurrence = a hazard term of the family and an asset form in the same section",
        "lexicon": cand["lexicon"], "families": fam_files, "family_disambiguation": cand["family_disambiguation"],
        "index": {"path": idx.as_posix(), "content_identity_sha256": idx_summary.get("content_identity_sha256"), "files": idx_summary.get("files")},
        "documents_in_index": n_docs,
        "per_family_doc_counts": {f: {"any_term": sum(f in p["families"] for p in papers),
                                      "admitted": sum(f in p["families"] and p["families"][f]["admitted"] for p in papers)} for f, _ in fams},
        "per_hazard_term_doc_counts": {f"{f}:{t}": sum(1 for d in doc.values() if (f, t) in d["hz"]) for f, t in hz},
        "per_asset_class_doc_counts": {c: sum(c in d["classes"] for d in doc.values()) for c, _ in lex["classes"]},
        "impact_doc_count": sum(d["impact"] for d in doc.values()),
        "hazard_sections_scanned": len(secs),
        "per_family_cooc_doc_counts": {f: sel["by_family"][f]["eligible"] for f, _ in fams},
        "per_family_cooc_asset_class_doc_counts": {f: {c: sum(1 for p in papers if f in p["cooc"] and any(c in s["asset_classes"] for s in p["cooc"][f]["sections"]))
                                                       for c, _ in lex["classes"]} for f, _ in fams},
        "candidate_rule": CAND_RULE, "cap_per_family": a.cap, "by_family": cand["by_family"], "n_candidates": len(sel["candidates"]),
        "paper_hits_sha256": paper_hits_sha, "candidates_sha256": hashlib.sha256((out / "candidates.json").read_bytes()).hexdigest(),
        "elapsed_seconds": round(time.time() - t0, 1),
        "duckdb_version": duckdb.__version__, "threads": a.threads, "memory_limit": a.memory_limit,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: summary[k] for k in ("name", "documents_in_index", "per_family_doc_counts", "per_family_cooc_doc_counts", "n_candidates", "elapsed_seconds")}, indent=2))


if __name__ == "__main__":
    main()
