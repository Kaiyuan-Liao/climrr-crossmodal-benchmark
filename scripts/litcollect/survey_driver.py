#!/usr/bin/env python3
"""Stage 2b+2c driver — dictionary-grounded concept coverage survey (DIAGNOSTIC ONLY).

Authorized by the M4-WP3 working-corpus/Stage-2 GUIDANCE ruling (D-025 bookkeeping):
  2b  a model proposes candidate surface forms per DICTIONARY concept; every proposal is stored
      with status `candidate_surface_form`, model id, endpoint, prompt text + sha256, date, concept id.
      Candidates never enter the concept map, production queries, C-2 or compatibility by this script.
  2c  deterministic counts over the frozen LITCORPUS-02 source index: topical-only, and
      context-filtered (= topical ∩ a cached document set matching the survey context clause).
      Counts are coverage diagnostics, not literature-prevalence estimates.

Inputs
  --inventory  YAML/JSON list of dictionary concepts: {id, name, passage, page, ...} (Stage 2a output)
  --index      build_index.py output dir (frozen LITCORPUS-02 source index)
  --context    text file with the survey context clause in run_query grammar (one OR-group)
  --out        survey output dir (restartable: a concept with out/<id>/row.json is skipped)
  TOKEN        env var with the ALCF inference access token
Per concept, out/<id>/ holds: prompt.txt, response.json, candidates.json, query_topical.txt,
topical/ (run_query output), row.json. out/survey_table.csv is regenerated from all row.json files.
"""
import argparse, csv, hashlib, json, os, re, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN_QUERY = HERE / "run_query.py"
TERM_OK = re.compile(r"^[a-z0-9][a-z0-9 \-/.%°']{0,59}$")

PROMPT_TEMPLATE = """You are helping build a lexical search over scientific papers. Below is ONE variable from a climate-data dictionary, quoted verbatim. Propose up to {k} surface forms (words or short phrases, lowercase, no regular expressions) that a scientific paper would use when it discusses THIS variable or the quantity it measures. Rules: (1) propose only forms that name the same quantity or a standard name for it, not broader topics; (2) include common abbreviations and hyphenation variants; (3) do not include place names, years, or scenario names; (4) each form at most 6 words. Return ONLY a JSON array of strings, nothing else.

Dictionary name: {name}
Dictionary passage: {passage}"""


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_inventory(p: Path):
    txt = p.read_text(encoding="utf-8")
    if p.suffix in (".yaml", ".yml"):
        import yaml  # PyYAML
        data = yaml.safe_load(txt)
    else:
        data = json.loads(txt)
    items = data["concepts"] if isinstance(data, dict) and "concepts" in data else data
    for c in items:
        for k in ("id", "name", "passage"):
            if k not in c:
                raise SystemExit(f"inventory item missing {k}: {c}")
    return items


def call_model(base_url, model, token, prompt, max_tokens, timeout):
    body = {"model": model, "temperature": 0, "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "replace")
    resp = json.loads(raw)
    msg = resp["choices"][0]["message"]
    content = msg.get("content") or msg.get("reasoning_content") or msg.get("reasoning") or ""
    return resp, content, round(time.time() - t0, 1)


def extract_terms(content: str):
    m = re.search(r"\[.*\]", content, re.S)
    if not m:
        return [], "no JSON array found"
    try:
        arr = json.loads(m.group(0))
    except Exception as e:  # noqa: BLE001
        return [], f"JSON parse failed: {e}"
    if not isinstance(arr, list):
        return [], "not a list"
    return [str(x) for x in arr], None


def sanitize(name: str, proposed):
    """Lowercase, whitespace-normalize, drop anything that is not a plain phrase; dictionary name first."""
    kept, dropped, seen = [], [], set()
    for src, t in [("dictionary_name", name)] + [("model", p) for p in proposed]:
        t2 = " ".join(str(t).lower().strip().split())
        if not TERM_OK.match(t2):
            dropped.append({"term": t, "reason": "not a plain lowercase phrase", "source": src}); continue
        if len(t2.split()) > 6:
            dropped.append({"term": t, "reason": "more than 6 words", "source": src}); continue
        if t2 in seen:
            dropped.append({"term": t, "reason": "duplicate", "source": src}); continue
        seen.add(t2); kept.append({"term": t2, "source": src})
        if len(kept) >= 10:
            break
    return kept, dropped


def run_query(index, qfile, out):
    cmd = [sys.executable, str(RUN_QUERY), "--index", str(index), "--query-file", str(qfile), "--out", str(out), "--name", out.name]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"run_query failed: {r.stderr[-2000:]}")
    return json.loads((out / "summary.json").read_text())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True); ap.add_argument("--index", required=True)
    ap.add_argument("--context", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--base-url", default="https://inference-api.alcf.anl.gov/resource_server/metis/api/v1")
    ap.add_argument("--model", default="gpt-oss-120b")
    ap.add_argument("--max-terms", type=int, default=8); ap.add_argument("--max-tokens", type=int, default=2000)
    ap.add_argument("--timeout", type=int, default=180); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default=None, help="comma-separated concept ids")
    a = ap.parse_args()
    token = os.environ.get("TOKEN") or os.environ.get("ALCF_INFERENCE_TOKEN")
    if not token:
        sys.exit("TOKEN env var not set")
    out, index = Path(a.out), Path(a.index)
    out.mkdir(parents=True, exist_ok=True)
    log = open(out / "survey.log", "a")

    def say(msg):
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
        print(line, flush=True); log.write(line + "\n"); log.flush()

    inventory = load_inventory(Path(a.inventory))
    inv_sha = sha(Path(a.inventory).read_text(encoding="utf-8"))
    ctx_text = Path(a.context).read_text(encoding="utf-8"); ctx_sha = sha(ctx_text)
    idx_summary = json.loads((index / "index_summary.json").read_text())
    say(f"START inventory={len(inventory)} concepts inventory_sha={inv_sha[:12]} context_sha={ctx_sha[:12]} index_identity={idx_summary.get('content_identity_sha256','')[:12]} model={a.model} base_url={a.base_url}")

    # Context clause: evaluated once, cached as an id set.
    ctx_dir = out / "_context"
    if not (ctx_dir / "summary.json").exists():
        say("context clause: scanning index once")
        run_query(index, Path(a.context), ctx_dir)
    ctx_ids = set((ctx_dir / "ids.txt").read_text().split())
    say(f"context clause matches {len(ctx_ids)} documents")

    only = set(a.only.split(",")) if a.only else None
    done = 0
    for c in inventory:
        cid = c["id"]
        if only and cid not in only:
            continue
        cdir = out / cid
        if (cdir / "row.json").exists():
            continue
        if a.limit and done >= a.limit:
            break
        cdir.mkdir(parents=True, exist_ok=True)
        # 2b — candidate surface forms
        prompt = PROMPT_TEMPLATE.format(k=a.max_terms, name=c["name"], passage=c["passage"])
        (cdir / "prompt.txt").write_text(prompt, encoding="utf-8")
        try:
            resp, content, secs = call_model(a.base_url, a.model, token, prompt, a.max_tokens, a.timeout)
            (cdir / "response.json").write_text(json.dumps(resp, indent=2, ensure_ascii=False))
            proposed, perr = extract_terms(content)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:1000]
            say(f"{cid}: model HTTP {e.code}: {body}"); (cdir / "model_error.txt").write_text(f"HTTP {e.code}\n{body}\n")
            proposed, perr, secs, content = [], f"HTTP {e.code}", None, ""
        except Exception as e:  # noqa: BLE001
            say(f"{cid}: model error {type(e).__name__}: {e}"); (cdir / "model_error.txt").write_text(f"{type(e).__name__}: {e}\n")
            proposed, perr, secs, content = [], f"{type(e).__name__}: {e}", None, ""
        kept, dropped = sanitize(c["name"], proposed)
        candidates = {
            "concept_id": cid, "dictionary_name": c["name"], "status": "candidate_surface_form",
            "model": a.model, "endpoint": a.base_url, "prompt_sha256": sha(prompt), "date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model_seconds": secs, "model_raw_terms": proposed, "model_parse_error": perr, "model_content_excerpt": content[:500],
            "candidates": kept, "dropped": dropped,
            "note": "Candidates are inert: not approved vocabulary; not in concept_map.yaml; not used by production queries, C-2 or compatibility.",
        }
        (cdir / "candidates.json").write_text(json.dumps(candidates, indent=2, ensure_ascii=False))
        # 2c — deterministic counts
        terms = [k["term"] for k in kept]
        qtext = "( " + " OR ".join(f'"{t}"' for t in terms) + " )\n"
        (cdir / "query_topical.txt").write_text(qtext, encoding="utf-8")
        t0 = time.time()
        summ = run_query(index, cdir / "query_topical.txt", cdir / "topical")
        topical_ids = set((cdir / "topical" / "ids.txt").read_text().split())
        ctx_count = len(topical_ids & ctx_ids)
        (cdir / "topical_and_context_ids.txt").write_text("".join(f"{d}\n" for d in sorted(topical_ids & ctx_ids)))
        per_term = summ.get("per_term_doc_counts", {})
        row = {
            "concept_id": cid, "dictionary_name": c["name"], "dictionary_page": c.get("page"), "dictionary_span": c.get("passage"),
            "candidate_surface_forms": terms, "per_term_doc_counts": {k.split(":", 1)[1]: v for k, v in per_term.items()},
            "topical_only_count": len(topical_ids), "context_filtered_count": ctx_count,
            "topical_query_sha256": sha(qtext), "context_clause_sha256": ctx_sha, "inventory_sha256": inv_sha,
            "index_content_identity_sha256": idx_summary.get("content_identity_sha256"), "scan_seconds": round(time.time() - t0, 1),
            "label": "diagnostic — coverage count, not prevalence; candidate vocabulary, not approved",
            "notes": "; ".join(x for x in [f"model parse error: {perr}" if perr else "", f"dropped {len(dropped)} proposed terms" if dropped else ""] if x),
        }
        (cdir / "row.json").write_text(json.dumps(row, indent=2, ensure_ascii=False))
        done += 1
        say(f"{cid} '{c['name']}': terms={len(terms)} topical={len(topical_ids)} context={ctx_count} model_s={secs} scan_s={row['scan_seconds']}")

    # Regenerate the table from all rows.
    rows = [json.loads(p.read_text()) for p in sorted(out.glob("*/row.json")) if p.parent.name != "_context"]
    with open(out / "survey_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["concept_id", "dictionary_name", "dictionary_page", "candidate_surface_forms", "topical_only_count", "context_filtered_count", "notes"])
        for r in sorted(rows, key=lambda r: -r["topical_only_count"]):
            w.writerow([r["concept_id"], r["dictionary_name"], r.get("dictionary_page"), " | ".join(r["candidate_surface_forms"]), r["topical_only_count"], r["context_filtered_count"], r["notes"]])
    say(f"DONE rows={len(rows)} table={out/'survey_table.csv'}")


if __name__ == "__main__":
    main()
