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
    ap.add_argument("--query-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default=None)
    ap.add_argument("--disambiguate", default=None, help="e.g. 'fwi=fire weather|fire-weather'")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--memory-limit", default="4GB")
    ap.add_argument("--no-hits", action="store_true", help="skip the per-section offset stage (counts and id sets only); for diagnostic surveys with large admitted sets")
    a = ap.parse_args()

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


if __name__ == "__main__":
    main()
