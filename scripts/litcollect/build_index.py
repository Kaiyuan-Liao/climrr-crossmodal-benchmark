#!/usr/bin/env python3
"""Build a restartable DuckDB/Parquet index over a flat-JSON literature corpus.

Corpus layout expected: <root>/<bucket>/<docid>.json where each file is a flat JSON
object of string values keyed by section heading (the JL / full_705k family).

For every file: SHA-256 of the raw bytes, byte count, and one row per (section key,
string value) with the value stored EXACTLY as decoded (no normalization). One Parquet
file per bucket directory, so an interrupted run resumes by skipping finished buckets.
Non-string values and parse failures are recorded, never repaired.

Usage:
  python build_index.py --root sources/full_705k_v2_filtered --out index/full_705k_v2_filtered

Outputs under --out:
  sections/<bucket>.parquet   doc_id, rel_path, section_idx, section_key, text
  docs/<bucket>.parquet       doc_id, rel_path, bytes, sha256, n_sections, n_nonstring, parse_ok
  manifest.csv                rel_path,bytes,sha256,doc_id   (sorted by rel_path; written at the end)
  index_summary.json          counts, root, content identity hash, timestamps
  build.log                   progress (one line per bucket)
"""
import argparse, hashlib, json, os, sys, time
from pathlib import Path

import duckdb


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def process_bucket(root: Path, bucket: Path, out_sec: Path, out_doc: Path, con) -> dict:
    doc_rows, sec_rows = [], []
    files = sorted(p for p in bucket.iterdir() if p.is_file() and p.suffix == ".json")
    for p in files:
        raw = p.read_bytes()
        rel = p.relative_to(root).as_posix()
        doc_id = p.stem
        parse_ok, n_sections, n_nonstring = True, 0, 0
        try:
            obj = json.loads(raw.decode("utf-8"))
            if not isinstance(obj, dict):
                raise ValueError("top level is not an object")
            for i, (k, v) in enumerate(obj.items()):
                if isinstance(v, str):
                    sec_rows.append((doc_id, rel, i, k, v))
                    n_sections += 1
                else:
                    n_nonstring += 1
        except Exception:
            parse_ok = False
        doc_rows.append((doc_id, rel, len(raw), sha256_bytes(raw), n_sections, n_nonstring, parse_ok))

    con.execute("CREATE OR REPLACE TABLE _docs(doc_id VARCHAR, rel_path VARCHAR, bytes BIGINT, sha256 VARCHAR, n_sections INTEGER, n_nonstring INTEGER, parse_ok BOOLEAN)")
    con.execute("CREATE OR REPLACE TABLE _secs(doc_id VARCHAR, rel_path VARCHAR, section_idx INTEGER, section_key VARCHAR, text VARCHAR)")
    if doc_rows:
        con.executemany("INSERT INTO _docs VALUES (?,?,?,?,?,?,?)", doc_rows)
    if sec_rows:
        con.executemany("INSERT INTO _secs VALUES (?,?,?,?,?)", sec_rows)
    con.execute(f"COPY _docs TO '{out_doc.as_posix()}' (FORMAT PARQUET)")
    con.execute(f"COPY _secs TO '{out_sec.as_posix()}' (FORMAT PARQUET)")
    return {"files": len(files), "sections": len(sec_rows), "parse_failures": sum(1 for r in doc_rows if not r[6])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root, out = Path(a.root).resolve(), Path(a.out)
    (out / "sections").mkdir(parents=True, exist_ok=True)
    (out / "docs").mkdir(parents=True, exist_ok=True)
    log = open(out / "build.log", "a")
    con = duckdb.connect()
    t0 = time.time()
    buckets = sorted(p for p in root.iterdir() if p.is_dir())
    done = skipped = 0
    for b in buckets:
        out_sec, out_doc = out / "sections" / f"{b.name}.parquet", out / "docs" / f"{b.name}.parquet"
        if out_sec.exists() and out_doc.exists():
            skipped += 1
            continue
        tb = time.time()
        stats = process_bucket(root, b, out_sec, out_doc, con)
        done += 1
        msg = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} bucket={b.name} files={stats['files']} sections={stats['sections']} parse_failures={stats['parse_failures']} secs={time.time()-tb:.1f} done={done+skipped}/{len(buckets)}"
        print(msg, flush=True); log.write(msg + "\n"); log.flush()

    # Final manifest + identity, from the parquet files (deterministic order).
    docs = con.execute(f"SELECT rel_path, bytes, sha256, doc_id, parse_ok, n_sections, n_nonstring FROM read_parquet('{(out/'docs').as_posix()}/*.parquet') ORDER BY rel_path").fetchall()
    man = out / "manifest.csv"
    h = hashlib.sha256()
    with open(man, "w", encoding="utf-8", newline="\n") as f:
        f.write("rel_path,bytes,sha256,doc_id,parse_ok,n_sections,n_nonstring\n")
        for rel, by, sh, did, ok, ns, nn in docs:
            f.write(f"{rel},{by},{sh},{did},{int(ok)},{ns},{nn}\n")
            h.update(f"{rel}\t{sh}\t{by}\n".encode("utf-8"))
    n_sec = con.execute(f"SELECT count(*) FROM read_parquet('{(out/'sections').as_posix()}/*.parquet')").fetchone()[0]
    summary = {
        "root": root.as_posix(),
        "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds_this_run": round(time.time() - t0, 1),
        "buckets": len(buckets), "buckets_built_this_run": done, "buckets_skipped_existing": skipped,
        "files": len(docs),
        "parse_failures": sum(1 for d in docs if not d[4]),
        "section_rows": n_sec,
        "total_bytes": sum(d[1] for d in docs),
        "distinct_sha256": len({d[2] for d in docs}),
        "manifest_csv_sha256": sha256_bytes(man.read_bytes()),
        "content_identity_sha256": h.hexdigest(),
        "content_identity_rule": "SHA-256 of UTF-8 lines 'rel_path<TAB>sha256<TAB>bytes<LF>' in rel_path order",
        "duckdb_version": duckdb.__version__, "python": sys.version.split()[0],
    }
    (out / "index_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
