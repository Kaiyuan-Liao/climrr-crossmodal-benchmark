#!/usr/bin/env python3
"""Stage 2b+2c driver — dictionary-grounded concept coverage survey (DIAGNOSTIC ONLY). v4.

Authorized by the M4-WP3 working-corpus/Stage-2 GUIDANCE ruling (D-025 bookkeeping):
  2b  a model proposes candidate surface forms per DICTIONARY concept; every proposal is stored
      with status `candidate_surface_form`, model id, endpoint, prompt text + sha256, date, concept id.
      Candidates never enter the concept map, production queries, C-2 or compatibility by this script.
  2c  deterministic counts over the frozen LITCORPUS-02 source index: topical-only, and
      context-filtered (= topical ∩ a cached document set matching the survey context clause).
      Counts are coverage diagnostics, not literature-prevalence estimates.

Modes (v4; the Track B ruling of 2026-10-20, D-027, B2-B4)
  --mode measure  (default) v3 behaviour, unchanged: the outputs are byte-identical to v3's for the
                  same inputs. --normalize applies the frozen orthographic table to model-proposed
                  terms (below); without it nothing is normalized, exactly as in v3.
  --mode family   run 2: prompt variant F (PROMPT_F) asks for the broader scientific quantity family
                  of each measure; out/<id>/family.json is `status: candidate_family` (a hypothesis,
                  never vocabulary, ontology, C-2 input, compatibility logic or unit design). Counts
                  run over the family surface forms only; each row carries the run-1 MEASURE counts
                  copied from --run1 beside the FAMILY counts. Family coverage is not attributable to
                  the measure; the two are never added, merged or substituted.
Normalization (B4; family mode always, measure mode with --normalize): every model-proposed form
  goes through climrr.termnorm with data/metadata/litcollect/normalization_table_v1.yaml (SHA-256
  verified, fail closed) BEFORE the sanitizer; each form is recorded with original, normalized,
  rules_applied (ids) and searched. A form a rule changed may have up to 10 words (the ruling sets no
  limit; this is the driver's choice, disclosed); every other form keeps the 6-word limit.
Context cache: out/_context is reused only if its summary.json records the same context clause
  SHA-256 and index identity, and its ids.txt holds admitted_count ids; otherwise the run stops.

Inputs
  --inventory  YAML/JSON list of dictionary concepts: {id, name, passage, page, ...} (Stage 2a output)
  --index      build_index.py output dir (frozen LITCORPUS-02 source index)
  --context    text file with the survey context clause in run_query grammar (one OR-group)
  --out        survey output dir (restartable: a concept with out/<id>/row.json is skipped)
  --run1       (family mode, required) run-1 output dir holding <id>/row.json for every concept;
               each must match this run's inventory, context clause and index identity
  TOKEN        env var with the ALCF inference access token
Per concept, out/<id>/ holds: prompt.txt, response.json, candidates.json (measure) or family.json
(family), query_topical.txt, topical/ (run_query output), row.json. out/survey_table.csv is
regenerated from all row.json files (family mode: measure and family columns side by side).
Family mode imports climrr.termnorm, so it needs the repository's src/ on PYTHONPATH.

Run 2 on Polaris (paths under the collection root stay relative, as in run 1, so no absolute path is
recorded; CLIMRR_REPO = a checkout of the pinned commit, LITCOLLECT_ROOT_POLARIS as in run 1):
  module load conda/2026-10-01 && conda activate globus_env
  cd "$LITCOLLECT_ROOT_POLARIS"
  export TOKEN=<ALCF inference access token>
  PYTHONPATH="$CLIMRR_REPO/src" python "$CLIMRR_REPO/scripts/litcollect/survey_driver.py" --mode family \
      --inventory "$CLIMRR_REPO/data/metadata/dictionary_concepts.yaml" \
      --index index/full_705k_v2_filtered \
      --context "$CLIMRR_REPO/data/metadata/litcollect/survey_context_clause_v1.txt" \
      --run1 survey/run1 --out survey/run2
"""
import argparse, csv, hashlib, json, os, re, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN_QUERY = HERE / "run_query.py"
DRIVER_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
TERM_OK = re.compile(r"^[a-z0-9][a-z0-9 \-/.]{0,59}$")  # no %, °, quotes: they defeat \b word boundaries

PROMPT_TEMPLATE = """You are helping build a lexical search over scientific papers. Below is ONE variable from a climate-data dictionary, quoted verbatim. Propose up to {k} surface forms (words or short phrases, lowercase, no regular expressions) that a scientific paper would use when it discusses THIS variable or the quantity it measures. Rules: (1) propose only forms that name the same quantity or a standard name for it, not broader topics; (2) include common abbreviations and hyphenation variants; (3) do not include place names, years, or scenario names; (4) each form at most 6 words. Return ONLY a JSON array of strings, nothing else.

Dictionary name: {name}
Dictionary passage: {passage}"""

#: Prompt variant F (run 2, family level; D-027 B2). Filled by plain replacement of {k}, {name},
#: {passage} (the JSON braces are literal). PROMPT_F_SHA256 is the template's hash; each concept
#: records the SHA-256 of its filled prompt.
PROMPT_F = """You are helping build a lexical search over scientific papers. Below is ONE variable from a climate-data dictionary, quoted verbatim. Given its dictionary name and passage, return ONLY a JSON object, nothing else, of this form: {"candidate_family": "<short lowercase snake_case name of the broader scientific quantity family this measure belongs to>", "family_surface_forms": [up to {k} lowercase words/phrases a paper would use for that family, no place names, years, scenario names, thresholds or statistics]}

Dictionary name: {name}
Dictionary passage: {passage}"""

#: The frozen orthographic table (D-027 B4), as pinned in data/manifest.json.
NORM_TABLE_SHA256 = "80a5e0e386dfe8a984e1a5ba2ace781d15601f9b0723b75d238b6de5d1226e03"
WORDS_PLAIN, WORDS_NORMALIZED, MAX_KEPT, MAX_CHARS = 6, 10, 10, 60
TERM_CHARS = re.compile(r"^[a-z0-9][a-z0-9 \-/.]*$")  # TERM_OK without its length bound
PLAIN_REASON = "not a plain lowercase phrase (letters, digits, space, - / . only)"
FAMILY_LABEL = "diagnostic — family coverage is not attributable to the measure"


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


def name_variants(name: str):
    """Dictionary name as stored, plus a parenthetical-stripped variant (e.g. 'temperature (annual)' -> 'temperature')."""
    base = " ".join(name.lower().strip().split())
    out = [base]
    stripped = " ".join(re.sub(r"\([^)]*\)", " ", base).split())
    if stripped and stripped != base:
        out.append(stripped)
    return out


def sanitize(name: str, proposed):
    """Lowercase, whitespace-normalize, drop anything that is not a plain phrase; dictionary name first."""
    kept, dropped, seen = [], [], set()
    for src, t in [("dictionary_name", v) for v in name_variants(name)] + [("model", p) for p in proposed]:
        t2 = " ".join(str(t).lower().strip().split())
        if not TERM_OK.match(t2):
            dropped.append({"term": t, "reason": "not a plain lowercase phrase (letters, digits, space, - / . only)", "source": src}); continue
        if len(t2.split()) > 6:
            dropped.append({"term": t, "reason": "more than 6 words", "source": src}); continue
        if t2 in seen:
            dropped.append({"term": t, "reason": "duplicate", "source": src}); continue
        seen.add(t2); kept.append({"term": t2, "source": src})
        if len(kept) >= 10:
            break
    return kept, dropped


def run_query(index, qfile, out):
    cmd = [sys.executable, str(RUN_QUERY), "--index", str(index), "--query-file", str(qfile), "--out", str(out), "--name", out.name, "--no-hits"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"run_query failed: {r.stderr[-2000:]}")
    return json.loads((out / "summary.json").read_text())


# --- v4 -----------------------------------------------------------------------

def fill_prompt_f(k, name, passage):
    return PROMPT_F.replace("{k}", str(k)).replace("{name}", name).replace("{passage}", passage)


def extract_family(content: str):
    """The last JSON object in the reply that has a `candidate_family` key (a reasoning field may
    hold drafts before the answer). Returns (candidate_family, forms, parse_error)."""
    dec, found = json.JSONDecoder(), None
    for m in re.finditer(r"\{", content):
        try:
            obj, _ = dec.raw_decode(content, m.start())
        except ValueError:
            continue
        if isinstance(obj, dict) and "candidate_family" in obj:
            found = obj
    if found is None:
        return None, [], "no JSON object with candidate_family found"
    fam, forms = found.get("candidate_family"), found.get("family_surface_forms", [])
    if not isinstance(fam, str) or not fam.strip():
        return None, [], "candidate_family is not a non-empty string"
    if not isinstance(forms, list):
        return fam, [], "family_surface_forms is not a list"
    return fam, [x if isinstance(x, str) else str(x) for x in forms], None


def load_norm_table(path=None):
    """climrr.termnorm and the frozen table, verified against NORM_TABLE_SHA256 (fail closed)."""
    try:
        from climrr import termnorm
    except ImportError as e:
        sys.exit(f"cannot import climrr.termnorm ({e}); put the repository's src/ on PYTHONPATH")
    p = Path(path) if path else termnorm.TABLE_PATH
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    if got != NORM_TABLE_SHA256:
        sys.exit(f"normalization table {p} has SHA-256 {got}, expected {NORM_TABLE_SHA256}; refusing to run")
    return termnorm, termnorm.load_table(p)


def screen_forms(dictionary_forms, model_forms, norm):
    """v4 sanitizer. Model forms are normalized (orthographic table only) before the plain-phrase
    rule; dictionary names are not. Every form gets a record: source, original, normalized,
    rules_applied, searched, search_term (the exact string queried, else None), reason (else None)."""
    termnorm, table = norm
    records, seen, n_kept = [], set(), 0
    for src, original in [("dictionary_name", v) for v in dictionary_forms] + [("model", p) for p in model_forms]:
        if src == "model":
            n = termnorm.normalize(original, table)
            normalized, rules = n["normalized"], n["rule_ids"]
        else:
            normalized, rules = original, []
        limit = WORDS_NORMALIZED if rules else WORDS_PLAIN
        t2 = " ".join(normalized.lower().strip().split())
        if not TERM_CHARS.match(t2):
            reason = PLAIN_REASON
        elif len(t2) > MAX_CHARS:
            reason = f"longer than {MAX_CHARS} characters"
        elif len(t2.split()) > limit:
            reason = f"more than {limit} words"
        elif t2 in seen:
            reason = "duplicate"
        elif n_kept >= MAX_KEPT:
            reason = f"over the {MAX_KEPT}-term cap"
        else:
            reason = None
            seen.add(t2); n_kept += 1
        records.append({"source": src, "original": original, "normalized": normalized, "rules_applied": rules,
                        "searched": reason is None, "search_term": t2 if reason is None else None, "reason": reason})
    return records


def load_run1(run1: Path, concepts, inv_sha, ctx_sha, idx_id):
    """Run-1 rows for `concepts`, each checked against this run's inventory, context and index."""
    rows, problems = {}, []
    for c in concepts:
        p = run1 / c["id"] / "row.json"
        if not p.is_file():
            problems.append(f"{c['id']}: no run-1 row.json"); continue
        raw = p.read_bytes(); r = json.loads(raw)
        for key, want in (("concept_id", c["id"]), ("dictionary_name", c["name"]), ("inventory_sha256", inv_sha),
                          ("context_clause_sha256", ctx_sha), ("index_content_identity_sha256", idx_id)):
            if r.get(key) != want:
                problems.append(f"{c['id']}: run-1 {key} {r.get(key)!r} != {want!r}")
        rows[c["id"]] = {"row": r, "sha256": hashlib.sha256(raw).hexdigest()}
    if problems:
        sys.exit("run-1 rows do not match this run: " + "; ".join(problems))
    return rows


def check_context_cache(ctx_dir: Path, ctx_sha, idx_id):
    """A cached _context may be reused only for the same clause and the same index (missing in v3)."""
    summ = json.loads((ctx_dir / "summary.json").read_text())
    ids = (ctx_dir / "ids.txt").read_text().split()
    problems = []
    if summ.get("query_sha256") != ctx_sha:
        problems.append(f"context clause SHA-256 {summ.get('query_sha256')} != {ctx_sha}")
    if (summ.get("index") or {}).get("content_identity_sha256") != idx_id:
        problems.append(f"index identity {(summ.get('index') or {}).get('content_identity_sha256')} != {idx_id}")
    if summ.get("admitted_count") != len(ids):
        problems.append(f"ids.txt holds {len(ids)} ids, summary says {summ.get('admitted_count')}")
    if problems:
        sys.exit(f"refusing to reuse {ctx_dir}: " + "; ".join(problems))


def run_family(a, token, inventory, only, out, index, ctx_ids, ctx_sha, inv_sha, idx_id, run1, norm, say):
    """Run 2 (D-027 B2): one candidate family per dictionary measure; family counts beside run-1 measure counts."""
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
        prompt = fill_prompt_f(a.max_terms, c["name"], c["passage"])
        (cdir / "prompt.txt").write_text(prompt, encoding="utf-8")
        try:
            resp, content, secs = call_model(a.base_url, a.model, token, prompt, a.max_tokens, a.timeout)
            (cdir / "response.json").write_text(json.dumps(resp, indent=2, ensure_ascii=False))
            family, proposed, perr = extract_family(content)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:1000]
            say(f"{cid}: model HTTP {e.code}: {body}"); (cdir / "model_error.txt").write_text(f"HTTP {e.code}\n{body}\n")
            family, proposed, perr, secs, content = None, [], f"HTTP {e.code}", None, ""
        except Exception as e:  # noqa: BLE001
            say(f"{cid}: model error {type(e).__name__}: {e}"); (cdir / "model_error.txt").write_text(f"{type(e).__name__}: {e}\n")
            family, proposed, perr, secs, content = None, [], f"{type(e).__name__}: {e}", None, ""
        records = screen_forms([], proposed, norm)
        fam = {
            "dictionary_concept_id": cid, "dictionary_passage": c["passage"], "model_id": a.model, "endpoint": a.base_url,
            "prompt_sha256": sha(prompt), "candidate_family": family, "candidate_family_surface_forms": records,
            "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "status": "candidate_family",
            "model_raw_response_excerpt": content[:500], "parse_error": perr,
        }
        (cdir / "family.json").write_text(json.dumps(fam, indent=2, ensure_ascii=False))
        # counts over the family surface forms only (never abort the run on one concept)
        terms = [r["search_term"] for r in records if r["searched"]]
        t0 = time.time(); topical_ids, ctx_count, per_term, scan_err = set(), None, {}, None
        if family is None:
            scan_err = "no candidate family (model call failed or reply did not parse)"
        elif not terms:
            scan_err = "no searchable family surface form (all proposals dropped)"
        else:
            qtext = "( " + " OR ".join(f'"{t}"' for t in terms) + " )\n"
            (cdir / "query_topical.txt").write_text(qtext, encoding="utf-8")
            try:
                summ = run_query(index, cdir / "query_topical.txt", cdir / "topical")
                topical_ids = set((cdir / "topical" / "ids.txt").read_text().split())
                ctx_count = len(topical_ids & ctx_ids)
                (cdir / "topical_and_context_ids.txt").write_text("".join(f"{d}\n" for d in sorted(topical_ids & ctx_ids)))
                per_term = summ.get("per_term_doc_counts", {})
            except Exception as e:  # noqa: BLE001
                scan_err = f"run_query failed: {e}"[:500]; (cdir / "scan_error.txt").write_text(scan_err + "\n")
        n_dropped = sum(not r["searched"] for r in records)
        notes = "; ".join(x for x in [f"model parse error: {perr}" if perr else "",
                                      f"dropped {n_dropped} proposed forms" if n_dropped else "", scan_err or ""] if x)
        m = run1[cid]["row"]
        row = {
            "mode": "family", "concept_id": cid, "dictionary_name": c["name"], "dictionary_page": c.get("page"),
            "measure_topical_only_count": m["topical_only_count"], "measure_context_filtered_count": m["context_filtered_count"],
            "measure_status": m["status"], "run1_row_sha256": run1[cid]["sha256"],
            "candidate_family": family, "candidate_family_status": "candidate_family",
            "family_surface_forms_searched": terms,
            "per_term_doc_counts": {k.split(":", 1)[1]: v for k, v in per_term.items()},
            "family_topical_only_count": len(topical_ids) if not scan_err else None,
            "family_context_filtered_count": ctx_count,
            "model_seconds": secs, "prompt_sha256": sha(prompt), "prompt_template_sha256": sha(PROMPT_F),
            "topical_query_sha256": sha(qtext) if terms and family is not None else None,
            "context_clause_sha256": ctx_sha, "inventory_sha256": inv_sha, "index_content_identity_sha256": idx_id,
            "normalization_table_sha256": NORM_TABLE_SHA256, "driver_sha256": DRIVER_SHA256,
            "sanitizer_word_limits": {"unnormalized": WORDS_PLAIN, "normalized": WORDS_NORMALIZED},
            "scan_seconds": round(time.time() - t0, 1),
            "label": FAMILY_LABEL,
            "status": "error" if scan_err else "ok",
            "notes": notes,
        }
        (cdir / "row.json").write_text(json.dumps(row, indent=2, ensure_ascii=False))
        done += 1
        say(f"{cid} '{c['name']}': status={row['status']} family={family} forms={len(terms)} "
            f"family_topical={row['family_topical_only_count']} family_context={ctx_count} "
            f"measure_topical={row['measure_topical_only_count']} model_s={secs} scan_s={row['scan_seconds']}")

    # Regenerate the side-by-side table from all rows (measure and family in separate columns).
    rows = [json.loads(p.read_text()) for p in sorted(out.glob("*/row.json")) if p.parent.name != "_context"]
    with open(out / "survey_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["concept_id", "dictionary_name", "measure_topical_only_count", "measure_context_filtered_count",
                    "candidate_family", "family_topical_only_count", "family_context_filtered_count", "notes"])
        for r in sorted(rows, key=lambda r: r["concept_id"]):
            w.writerow([r["concept_id"], r["dictionary_name"], r["measure_topical_only_count"], r["measure_context_filtered_count"],
                        r["candidate_family"], r["family_topical_only_count"], r["family_context_filtered_count"], r["notes"]])
    say(f"DONE rows={len(rows)} table={out/'survey_table.csv'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True); ap.add_argument("--index", required=True)
    ap.add_argument("--context", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--base-url", default="https://inference-api.alcf.anl.gov/resource_server/metis/api/v1")
    ap.add_argument("--model", default="gpt-oss-120b")
    ap.add_argument("--max-terms", type=int, default=8); ap.add_argument("--max-tokens", type=int, default=2000)
    ap.add_argument("--timeout", type=int, default=180); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default=None, help="comma-separated concept ids")
    ap.add_argument("--mode", choices=("measure", "family"), default="measure")
    ap.add_argument("--normalize", action="store_true", help="measure mode: normalize model terms (family mode always does)")
    ap.add_argument("--run1", default=None, help="family mode: run-1 output dir with <id>/row.json (required)")
    ap.add_argument("--norm-table", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.mode == "family" and not a.run1:
        sys.exit("--mode family requires --run1 <run-1 output dir>")
    norm = load_norm_table(a.norm_table) if (a.mode == "family" or a.normalize) else None
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
    idx_id = idx_summary.get("content_identity_sha256")
    only = set(a.only.split(",")) if a.only else None
    if a.mode == "family":
        run1 = load_run1(Path(a.run1), [c for c in inventory if not only or c["id"] in only], inv_sha, ctx_sha, idx_id)
        say(f"START mode=family inventory={len(inventory)} concepts inventory_sha={inv_sha[:12]} context_sha={ctx_sha[:12]} index_identity={(idx_id or '')[:12]} model={a.model} base_url={a.base_url} prompt_f_sha={sha(PROMPT_F)[:12]} norm_table_sha={NORM_TABLE_SHA256[:12]} driver_sha={DRIVER_SHA256[:12]} run1_rows={len(run1)}")
    else:
        say(f"START inventory={len(inventory)} concepts inventory_sha={inv_sha[:12]} context_sha={ctx_sha[:12]} index_identity={idx_summary.get('content_identity_sha256','')[:12]} model={a.model} base_url={a.base_url}")

    # Context clause: evaluated once, cached as an id set.
    ctx_dir = out / "_context"
    if not (ctx_dir / "summary.json").exists():
        say("context clause: scanning index once")
        run_query(index, Path(a.context), ctx_dir)
    else:
        check_context_cache(ctx_dir, ctx_sha, idx_id)
        if a.mode == "family":
            say("context clause: cached id set reused (clause SHA-256 and index identity match)")
    ctx_ids = set((ctx_dir / "ids.txt").read_text().split())
    say(f"context clause matches {len(ctx_ids)} documents")

    if a.mode == "family":
        run_family(a, token, inventory, only, out, index, ctx_ids, ctx_sha, inv_sha, idx_id, run1, norm, say)
        return
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
        if norm:
            records = screen_forms(name_variants(c["name"]), proposed, norm)
            kept = [{"term": r["search_term"], "source": r["source"]} for r in records if r["searched"]]
            dropped = [{"term": r["original"], "reason": r["reason"], "source": r["source"]} for r in records if not r["searched"]]
        else:
            kept, dropped = sanitize(c["name"], proposed)
        candidates = {
            "concept_id": cid, "dictionary_name": c["name"], "status": "candidate_surface_form",
            "model": a.model, "endpoint": a.base_url, "prompt_sha256": sha(prompt), "date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model_seconds": secs, "model_raw_terms": proposed, "model_parse_error": perr, "model_content_excerpt": content[:500],
            "candidates": kept, "dropped": dropped,
            "note": "Candidates are inert: not approved vocabulary; not in concept_map.yaml; not used by production queries, C-2 or compatibility.",
        }
        if norm:
            candidates.update({"surface_forms": records, "normalization_table_sha256": NORM_TABLE_SHA256,
                               "sanitizer_word_limits": {"unnormalized": WORDS_PLAIN, "normalized": WORDS_NORMALIZED}})
        (cdir / "candidates.json").write_text(json.dumps(candidates, indent=2, ensure_ascii=False))
        # 2c — deterministic counts (never abort the run on one concept)
        terms = [k["term"] for k in kept]
        t0 = time.time(); topical_ids, ctx_count, per_term, scan_err = set(), None, {}, None
        if not terms:
            scan_err = "no searchable candidate term (all proposals dropped and/or model call failed)"
        else:
            qtext = "( " + " OR ".join(f'"{t}"' for t in terms) + " )\n"
            (cdir / "query_topical.txt").write_text(qtext, encoding="utf-8")
            try:
                summ = run_query(index, cdir / "query_topical.txt", cdir / "topical")
                topical_ids = set((cdir / "topical" / "ids.txt").read_text().split())
                ctx_count = len(topical_ids & ctx_ids)
                (cdir / "topical_and_context_ids.txt").write_text("".join(f"{d}\n" for d in sorted(topical_ids & ctx_ids)))
                per_term = summ.get("per_term_doc_counts", {})
            except Exception as e:  # noqa: BLE001
                scan_err = f"run_query failed: {e}"[:500]; (cdir / "scan_error.txt").write_text(scan_err + "\n")
        notes = "; ".join(x for x in [f"model parse error: {perr}" if perr else "", f"dropped {len(dropped)} proposed terms" if dropped else "", scan_err or ""] if x)
        row = {
            "concept_id": cid, "dictionary_name": c["name"], "dictionary_page": c.get("page"), "dictionary_span": c.get("passage"),
            "candidate_surface_forms": terms, "per_term_doc_counts": {k.split(":", 1)[1]: v for k, v in per_term.items()},
            "topical_only_count": len(topical_ids) if not scan_err else None, "context_filtered_count": ctx_count,
            "topical_query_sha256": sha(qtext) if terms else None, "context_clause_sha256": ctx_sha, "inventory_sha256": inv_sha,
            "index_content_identity_sha256": idx_summary.get("content_identity_sha256"), "scan_seconds": round(time.time() - t0, 1),
            "label": "diagnostic — coverage count, not prevalence; candidate vocabulary, not approved",
            "status": "error" if scan_err else "ok",
            "notes": notes,
        }
        if norm:
            row.update({"normalization_table_sha256": NORM_TABLE_SHA256,
                        "sanitizer_word_limits": {"unnormalized": WORDS_PLAIN, "normalized": WORDS_NORMALIZED}})
        (cdir / "row.json").write_text(json.dumps(row, indent=2, ensure_ascii=False))
        done += 1
        say(f"{cid} '{c['name']}': status={row['status']} terms={len(terms)} topical={row['topical_only_count']} context={ctx_count} model_s={secs} scan_s={row['scan_seconds']}")

    # Regenerate the table from all rows.
    rows = [json.loads(p.read_text()) for p in sorted(out.glob("*/row.json")) if p.parent.name != "_context"]
    with open(out / "survey_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["concept_id", "dictionary_name", "dictionary_page", "candidate_surface_forms", "topical_only_count", "context_filtered_count", "notes"])
        for r in sorted(rows, key=lambda r: -(r["topical_only_count"] if r["topical_only_count"] is not None else -1)):
            w.writerow([r["concept_id"], r["dictionary_name"], r.get("dictionary_page"), " | ".join(r["candidate_surface_forms"]), r["topical_only_count"], r["context_filtered_count"], r["notes"]])
    say(f"DONE rows={len(rows)} table={out/'survey_table.csv'}")


if __name__ == "__main__":
    main()
