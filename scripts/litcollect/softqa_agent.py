#!/usr/bin/env python3
"""Track C — soft-QA candidate proposal agent (D-029/D-030; GUIDANCE guardrails 2026-10-27).

For each frozen place-candidate paper: give the model the FULL paper text, the unit DEFINITIONS
(never computed values), the family descriptions and the permitted QA types; ask for groups
(passage -> unit -> QA type -> one example QA pair -> rationale). Then run the deterministic
pre_review_check on every proposal: the passage must re-slice EXACTLY from a stored section
(zero-based code-point [start,end) on the unnormalized string), the unit's concept terms and the
place terms are located (first occurrence anywhere in the paper), place role is recorded from the
model's annotation, provenance completeness is checked. Output status: `llm_candidate` ->
`deterministic_pass` or `rejected_pre_review`. Table-side values are NOT filled here (answer side
is computed later by deterministic code after the candidate structure is frozen).

Restartable per paper (skips papers with result.json). Runs on Polaris with TOKEN in env.
"""
import argparse, hashlib, json, os, re, sys, time, urllib.request, urllib.error
from pathlib import Path

import duckdb

GENERATOR_VERSION = "softqa_agent v2"

SYSTEM_PROMPT = """You are helping build a benchmark that links statements in scientific papers to a table of climate projections (ClimRR). You will read ONE paper in full. You are given the DEFINITIONS of table-side objects called units (no numbers are given to you on purpose) and a list of permitted question types.

Your task: find passages in THIS paper that could be paired with one of the units to form a question. Only passages that state the paper's OWN finding, observation or projection about the quantity (or a clearly cited study's finding) qualify; definitions, lists of indices, method descriptions and general background do not. Return at most 3 groups. For each pairing, return a group with:
- "passage": an EXACT, verbatim copy of a contiguous passage from the paper (one to three sentences, at most 700 characters). Copy it character for character from the paper text, including its hyphens, quotes and spacing; do not shorten, do not add "...", do not merge sentences from different places. Stop at the end of a sentence in the paper.
- "passage_type": one of "own_finding", "own_projection", "cited_finding", "background_or_definition", "method_description".
- "section_key": the section heading under which the passage appears (as given in the paper text).
- "unit_id": one of the unit ids provided.
- "qa_type": one of the permitted question types.
- "example_question": one question a benchmark could ask, written so that it CANNOT be answered from the paper alone or from the table alone (for example: compare, validate, explain a difference, identify the region). Do not concatenate "what does the table say" with "what does the paper say". Do not put any table number in it.
- "paper_side_fact": what the passage states, in one sentence, with no additions.
- "table_side_needed": what value or pattern would have to be read from the table to answer (describe it; do NOT guess the value).
- "paper_geography": the place the passage is about, as the paper names it, or "unknown".
- "paper_geography_role": one of "study_area", "cited_study_area", "contextual", "affiliation", "person_or_citation", "data_source", "unknown".
- "paper_time": the period the passage refers to, as stated, or "unknown".
- "paper_scenario": the emissions/climate scenario named in or around the passage, or "unknown".
- "paper_concept": the quantity the passage is about, as the paper names it.
- "concept_relation": "direct" (same quantity as the unit's family), "related" (close but different), "mismatch".
- "geography_relation": "same", "contains", "contained_in", "different", "unknown".
- "link_rationale": one or two sentences on why this passage and this unit belong together for this question type.
- "unmatched_dimensions": list of any of ["concept","geography","time","scenario","direction"] that do not match the unit.
- "confidence": "high", "medium", or "low".
Return ONLY a JSON object: {"groups": [ ... ]}. If nothing in the paper can be paired honestly, return {"groups": []}. Fewer honest groups are better than many weak ones. Never invent passages."""


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def call_model(base_url, model, token, system, user, max_tokens, timeout):
    body = {"model": model, "temperature": 0, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read().decode("utf-8", "replace"))
    msg = resp["choices"][0]["message"]
    content = msg.get("content") or msg.get("reasoning_content") or msg.get("reasoning") or ""
    return resp, content, round(time.time() - t0, 1)


def extract_json_object(content: str):
    """Last JSON object containing a 'groups' key."""
    best = None
    for m in re.finditer(r"\{", content):
        depth, i = 0, m.start()
        while i < len(content):
            if content[i] == "{": depth += 1
            elif content[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(content[m.start():i + 1])
                        if isinstance(obj, dict) and "groups" in obj:
                            best = obj
                    except Exception:  # noqa: BLE001
                        pass
                    break
            i += 1
    return best


def first_hit(text: str, term: str):
    m = re.search(r"\b" + re.escape(term) + r"\b", text, re.IGNORECASE)
    return [m.start(), m.end()] if m else None


_TRANS = {0x2010: "-", 0x2011: "-", 0x2012: "-", 0x2013: "-", 0x2014: "-", 0x2212: "-",
          0x2018: "'", 0x2019: "'", 0x201C: '"', 0x201D: '"', 0x00A0: " ", 0x202F: " ", 0x2009: " ", 0x2007: " "}


def norm_with_map(text: str):
    """Length-preserving character normalization (hyphen/quote/space variants), then whitespace collapse with an index map."""
    out, idx = [], []
    prev_space = False
    for i, ch in enumerate(text):
        ch2 = _TRANS.get(ord(ch), ch)
        if ch2.isspace():
            if prev_space:
                continue
            ch2, prev_space = " ", True
        else:
            prev_space = False
        out.append(ch2); idx.append(i)
    return "".join(out), idx


def norm_plain(text: str):
    return norm_with_map(text)[0].strip()


def locate_passage(passage: str, sections):
    """Return (span dict, recovery method, recovered verbatim text) or (None, 'not_found', None).
    Methods: exact | normalized | prefix_anchor (first 80 normalized chars found once; extended to the sentence end in the original)."""
    if not passage or len(passage) < 20:
        return None, "not_found", None
    for s in sections:
        i = s["text"].find(passage)
        if i >= 0:
            return {"json_path": f"$.{s['section_key']}", "section_idx": s["section_idx"], "span_start": i, "span_end": i + len(passage)}, "exact", passage
    np_ = norm_plain(passage)
    for s in sections:
        nt, idx = norm_with_map(s["text"])
        j = nt.find(np_)
        if j >= 0 and np_:
            a, b = idx[j], idx[j + len(np_) - 1] + 1
            return {"json_path": f"$.{s['section_key']}", "section_idx": s["section_idx"], "span_start": a, "span_end": b}, "normalized", s["text"][a:b]
    prefix = np_[:80]
    if len(prefix) >= 60:
        hits = []
        for s in sections:
            nt, idx = norm_with_map(s["text"])
            k = nt.find(prefix)
            if k >= 0 and nt.find(prefix, k + 1) < 0:
                hits.append((s, idx[k], nt, idx))
        if len(hits) == 1:
            s, a, nt, idx = hits[0]
            k = nt.find(prefix)
            # the recovered passage is the ONE sentence that starts at the anchor: end at the first sentence
            # terminator after the prefix; capped at 900 chars; and it must share most of its words with the proposal
            m = re.compile(r"[.!?](?=\s|$)").search(nt, k + len(prefix))
            end_n = m.end() if m else min(len(nt), k + len(np_))
            b = idx[min(end_n, len(idx)) - 1] + 1
            recovered = s["text"][a:b]
            rw, pw = set(re.findall(r"\w+", norm_plain(recovered).lower())), set(re.findall(r"\w+", np_.lower()))
            overlap = len(rw & pw) / max(1, len(rw))
            if b - a <= 900 and overlap >= 0.6:
                return {"json_path": f"$.{s['section_key']}", "section_idx": s["section_idx"], "span_start": a, "span_end": b}, "prefix_anchor", recovered
    return None, "not_found", None


def pre_review_check(group, sections, unit, place_terms):
    """Deterministic checks. Returns (status, checks dict, located fields)."""
    checks, located = {}, {}
    passage = group.get("passage") or ""
    # 1. locate the passage: exact, else normalized (typographic variants), else prefix-anchored to the sentence end.
    span, recovery, verbatim = locate_passage(passage, sections)
    checks["span_reslice_pass"] = span is not None
    checks["passage_recovery"] = recovery
    located["evidence"] = span
    located["verbatim_passage"] = verbatim
    # 1b. passage type: background/method passages are not candidates
    ptype = group.get("passage_type")
    checks["passage_type"] = ptype
    checks["passage_type_pass"] = ptype in ("own_finding", "own_projection", "cited_finding")
    # 2. concept term located anywhere in the paper (unit family surface terms)
    concept_hit = None
    for s in sections:
        for t in unit["family_surface_terms"]:
            h = first_hit(s["text"], t)
            if h:
                concept_hit = {"term": t, "json_path": f"$.{s['section_key']}", "section_idx": s["section_idx"], "span": h}; break
        if concept_hit: break
    checks["concept_location_pass"] = concept_hit is not None
    located["concept_hit"] = concept_hit
    # 3. place: for same/contains/contained_in relations the unit's place term must occur in the paper;
    #    for a cross-location ("different") relation the paper must instead name its own place with a study-area role;
    #    "unknown" relation with a placed unit fails.
    place_hit = None
    for s in sections:
        for t in place_terms:
            h = first_hit(s["text"], t)
            if h:
                place_hit = {"term": t, "json_path": f"$.{s['section_key']}", "section_idx": s["section_idx"], "span": h}; break
        if place_hit: break
    located["place_hit"] = place_hit
    rel = group.get("geography_relation")
    if not place_terms:
        checks["place_location_pass"] = True
    elif rel in ("same", "contains", "contained_in"):
        checks["place_location_pass"] = place_hit is not None
    elif rel == "different":
        checks["place_location_pass"] = (group.get("paper_geography", "unknown") != "unknown"
                                         and group.get("paper_geography_role") in ("study_area", "cited_study_area"))
    else:
        checks["place_location_pass"] = False
    checks["place_check_mode"] = "unit_place_in_paper" if rel in ("same", "contains", "contained_in") else ("paper_names_own_place" if rel == "different" else "n/a")
    checks["place_role_recorded"] = group.get("paper_geography_role") in {"study_area", "cited_study_area", "contextual", "affiliation", "person_or_citation", "data_source", "unknown"}
    # 4. provenance completeness of the proposal
    required = ["passage", "passage_type", "section_key", "unit_id", "qa_type", "example_question", "paper_side_fact", "table_side_needed",
                "paper_geography", "paper_geography_role", "paper_time", "paper_scenario", "paper_concept", "concept_relation",
                "geography_relation", "link_rationale", "unmatched_dimensions", "confidence"]
    missing = [k for k in required if k not in group]
    checks["proposal_fields_complete"] = not missing
    checks["missing_fields"] = missing
    # 5. no table number in the question (crude leakage guard: digits followed by units/percent in the question)
    checks["question_has_no_table_number"] = not re.search(r"\d+(\.\d+)?\s*(%|percent|days|°|degrees)", group.get("example_question", ""), re.I)
    mandatory = ["span_reslice_pass", "passage_type_pass", "concept_location_pass", "place_location_pass", "place_role_recorded", "proposal_fields_complete"]
    status = "deterministic_pass" if all(checks[k] for k in mandatory) else "rejected_pre_review"
    return status, checks, located


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True, help="build_index.py output dir")
    ap.add_argument("--candidates", required=True, help="JSON: [{item_id, arm}] or text file of ids (arm from --arm)")
    ap.add_argument("--arm", default=None)
    ap.add_argument("--units", required=True, help="units.json: definitions only, no values")
    ap.add_argument("--qa-types", required=True, help="qa_types.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--base-url", default="https://inference-api.alcf.anl.gov/resource_server/metis/api/v1")
    ap.add_argument("--model", default="gpt-oss-120b")
    ap.add_argument("--max-tokens", type=int, default=6000); ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--max-chars", type=int, default=90000, help="truncate paper text beyond this (recorded)")
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--only", default=None)
    ap.add_argument("--source-commit", default="unknown")
    a = ap.parse_args()
    token = os.environ.get("TOKEN") or os.environ.get("ALCF_INFERENCE_TOKEN")
    if not token:
        sys.exit("TOKEN env var not set")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    log = open(out / "agent.log", "a")

    def say(msg):
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"; print(line, flush=True); log.write(line + "\n"); log.flush()

    units = json.loads(Path(a.units).read_text(encoding="utf-8"))
    for u in units["units"]:
        for forbidden in ("value", "values", "computed", "answer", "change", "baseline_value", "future_value"):
            if forbidden in u:
                sys.exit(f"units file must contain definitions only; field '{forbidden}' found in {u.get('unit_id')}")
    qa_types = json.loads(Path(a.qa_types).read_text(encoding="utf-8"))
    cands_raw = Path(a.candidates).read_text(encoding="utf-8")
    try:
        cands = json.loads(cands_raw)
    except Exception:  # noqa: BLE001
        cands = [{"item_id": l.strip(), "arm": a.arm} for l in cands_raw.splitlines() if l.strip()]
    only = set(a.only.split(",")) if a.only else None
    units_sha, qa_sha, sys_sha = sha(json.dumps(units, sort_keys=True)), sha(json.dumps(qa_types, sort_keys=True)), sha(SYSTEM_PROMPT)
    idx = Path(a.index)
    idx_summary = json.loads((idx / "index_summary.json").read_text())
    con = duckdb.connect(); con.execute("SET threads=2"); con.execute("SET memory_limit='3GB'")
    say(f"START candidates={len(cands)} units={len(units['units'])} qa_types={len(qa_types['qa_types'])} model={a.model} units_sha={units_sha[:12]} qa_sha={qa_sha[:12]} system_sha={sys_sha[:12]} index={idx_summary.get('content_identity_sha256','')[:12]}")

    unit_text = "\n".join(f"- {u['unit_id']}: {u['definition']} (family: {u['family']}; family surface terms: {', '.join(u['family_surface_terms'])}; place label: {u.get('place_label','none')})" for u in units["units"])
    qa_text = "\n".join(f"- {q['qa_type']}: {q['description']}" for q in qa_types["qa_types"])
    done = 0
    for c in cands:
        iid = str(c["item_id"])
        if only and iid not in only: continue
        pdir = out / iid
        if (pdir / "result.json").exists(): continue
        if a.limit and done >= a.limit: break
        pdir.mkdir(parents=True, exist_ok=True)
        rows = con.execute(f"SELECT s.section_idx, s.section_key, s.text, d.rel_path, d.sha256 FROM read_parquet('{(idx/'sections').as_posix()}/*.parquet') s JOIN read_parquet('{(idx/'docs').as_posix()}/*.parquet') d USING(doc_id) WHERE s.doc_id = ? ORDER BY s.section_idx", [iid]).fetchall()
        if not rows:
            say(f"{iid}: not in index"); (pdir / "result.json").write_text(json.dumps({"item_id": iid, "error": "not in index"})); continue
        sections = [{"section_idx": r[0], "section_key": r[1], "text": r[2]} for r in rows]
        rel_path, sha256 = rows[0][3], rows[0][4]
        paper_text = "\n\n".join(f"[SECTION: {s['section_key']}]\n{s['text']}" for s in sections)
        truncated = len(paper_text) > a.max_chars
        shown = paper_text[: a.max_chars]
        user = f"UNITS (definitions only; no values):\n{unit_text}\n\nPERMITTED QUESTION TYPES:\n{qa_text}\n\nPAPER (item {iid}; arm {c.get('arm')}):\n{shown}" + ("\n\n[PAPER TRUNCATED]" if truncated else "")
        (pdir / "prompt_user.txt").write_text(user, encoding="utf-8")
        t0 = time.time()
        try:
            resp, content, secs = call_model(a.base_url, a.model, token, SYSTEM_PROMPT, user, a.max_tokens, a.timeout)
            (pdir / "response.json").write_text(json.dumps(resp, indent=2, ensure_ascii=False))
            obj = extract_json_object(content); perr = None if obj else "no JSON object with 'groups' found"
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:1000]; (pdir / "model_error.txt").write_text(f"HTTP {e.code}\n{body}\n")
            obj, perr, secs, content = None, f"HTTP {e.code}", None, ""
        except Exception as e:  # noqa: BLE001
            (pdir / "model_error.txt").write_text(f"{type(e).__name__}: {e}\n"); obj, perr, secs, content = None, f"{type(e).__name__}: {e}", None, ""
        groups = (obj or {}).get("groups", []) if isinstance(obj, dict) else []
        unit_by_id = {u["unit_id"]: u for u in units["units"]}
        candidates = []
        for gi, g in enumerate(groups if isinstance(groups, list) else []):
            if not isinstance(g, dict): continue
            u = unit_by_id.get(g.get("unit_id"))
            if u is None:
                status, checks, located = "rejected_pre_review", {"unit_id_known": False}, {}
            else:
                status, checks, located = pre_review_check(g, sections, u, u.get("place_terms", []))
                checks["unit_id_known"] = True
            if g.get("qa_type") not in {q["qa_type"] for q in qa_types["qa_types"]}:
                checks["qa_type_known"] = False; status = "rejected_pre_review"
            else:
                checks["qa_type_known"] = True
            cid = f"C-{iid}-{gi+1:02d}"
            candidates.append({
                "candidate_id": cid, "track": "C", "status": status, "generator_version": GENERATOR_VERSION, "generator_model": a.model,
                "endpoint": a.base_url, "prompt_hash": sha(SYSTEM_PROMPT + user), "system_prompt_sha256": sys_sha, "units_sha256": units_sha, "qa_types_sha256": qa_sha,
                "generation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "source_commit": a.source_commit,
                "paper_item_id": iid, "paper_rel_path": rel_path, "paper_sha256": sha256, "arm": c.get("arm"),
                "evidence": located.get("evidence"), "verbatim_passage": located.get("verbatim_passage"), "passage_as_proposed": g.get("passage"),
                "passage_recovery": checks.get("passage_recovery"),
                "concept_hit": located.get("concept_hit"), "place_hit": located.get("place_hit"),
                "proposal": g,
                "table_values_visible_to_generator": False, "answer_visible_to_generator": False,
                "pre_review_checks": checks, "pre_review_status": status,
                "table_side": None, "c_g_t_s_d_audit": None, "human_review": None,
            })
        result = {"item_id": iid, "arm": c.get("arm"), "paper_sha256": sha256, "n_sections": len(sections), "paper_chars": len(paper_text), "truncated": truncated,
                  "model_seconds": secs, "model_parse_error": perr, "n_groups_proposed": len(groups) if isinstance(groups, list) else 0,
                  "n_deterministic_pass": sum(1 for x in candidates if x["status"] == "deterministic_pass"),
                  "n_rejected_pre_review": sum(1 for x in candidates if x["status"] == "rejected_pre_review"),
                  "candidates": candidates, "elapsed_seconds": round(time.time() - t0, 1)}
        (pdir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
        done += 1
        say(f"{iid} arm={c.get('arm')} chars={len(paper_text)}{' TRUNC' if truncated else ''} groups={result['n_groups_proposed']} pass={result['n_deterministic_pass']} reject={result['n_rejected_pre_review']} model_s={secs} err={perr}")

    # Aggregate
    allc, summary = [], {"papers": 0, "groups": 0, "deterministic_pass": 0, "rejected_pre_review": 0, "by_qa_type": {}, "by_unit": {}, "by_concept_relation": {}, "by_place_role": {}}
    for p in sorted(out.glob("*/result.json")):
        r = json.loads(p.read_text())
        if "candidates" not in r: continue
        summary["papers"] += 1
        for x in r["candidates"]:
            allc.append(x); summary["groups"] += 1; summary[x["status"]] += 1
            g = x["proposal"]
            for key, field in (("by_qa_type", "qa_type"), ("by_unit", "unit_id"), ("by_concept_relation", "concept_relation"), ("by_place_role", "paper_geography_role")):
                summary[key][str(g.get(field))] = summary[key].get(str(g.get(field)), 0) + 1
    with open(out / "candidates.jsonl", "w", encoding="utf-8") as f:
        for x in allc: f.write(json.dumps(x, ensure_ascii=False) + "\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    say(f"DONE papers={summary['papers']} groups={summary['groups']} pass={summary['deterministic_pass']} reject={summary['rejected_pre_review']}")


if __name__ == "__main__":
    main()
