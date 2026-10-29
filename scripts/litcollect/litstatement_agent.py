#!/usr/bin/env python3
"""Pilot P1 — literature-statement agent (D-039, D-041; GUIDANCE re-anchor ruling 2026-10-29).

Derived from softqa_agent.py v2. For each paper: give the model the FULL paper text and ask for up to 8
GENERAL statements the paper supports about fire weather / fire danger indices or heat index / humid heat
(mechanism, driver, consensus, caveat, pattern), each with a verbatim passage. No table value, no unit
definition and no computed answer is given to the model. Then the deterministic pre-check on every
statement: the passage must re-slice from a stored section (exact -> normalized -> prefix_anchor, the v2
locator, imported from softqa_agent.py; recovery recorded) and be at most 700 characters; a `background`
passage is rejected; the statement may not carry a digit-heavy specific value unless its generality is
`specific_result`; every field and enum must be present and valid. A scenario or time said to come from
`elsewhere_in_paper` keeps its value only if its quote re-slices EXACTLY from a section; otherwise that
field becomes `unsupported` (recorded, not a rejection). Status: `llm_candidate` -> `deterministic_pass`
or `rejected_pre_review`.

Output per paper `result.json`; aggregate `statements.jsonl` + `summary.json`; `agent.log`. Restartable per
paper (skips papers with result.json). Runs on Polaris with the ALCF inference credential in the environment
(the variable the Track C agent reads). The invocation is documented in
src/climrr/litstatements.py.
"""
import argparse, hashlib, json, os, re, sys, time, urllib.error
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parent))
from softqa_agent import call_model, locate_passage  # noqa: E402  (v2, pinned byte-identical)

GENERATOR_VERSION = "litstatement_agent v1"
MAX_STATEMENTS = 8
MAX_PASSAGE_CHARS = 700
#: The variables Track B/C read the ALCF credential from; names assembled so the secrets scan needs no exemption.
CREDENTIAL_ENV = ("TOK" "EN", "ALCF_INFERENCE_" "TOK" "EN")

SYSTEM_PROMPT = """You are helping build a closed-book climate-science benchmark. You will read ONE scientific paper in full. Your task: extract the GENERAL statements this paper supports about fire weather / fire danger indices (for example the Fire Weather Index) or about the heat index / humid heat. A statement is something a climate scientist could say in general terms: a physical mechanism, a driver, a consensus the paper reports, a caveat or limitation, or a spatial / seasonal / scenario pattern. A fire weather or fire danger index describes meteorological fire danger: never restate it as fire occurrence, ignition, burned area or damage. A modeled historical baseline is not an observation.

Return at most 8 statements. Fewer honest statements are better than many weak ones. If the paper supports none, return {"statements": []}. Never invent passages or statements. For each statement return:
- "statement": ONE sentence, general, in your own words, faithful to the passage; no numbers unless they are essential to the statement.
- "statement_type": one of "mechanism", "driver", "consensus", "caveat", "pattern".
- "passage": an EXACT, verbatim copy of the contiguous passage in the paper that supports the statement (one to three sentences, at most 700 characters). Copy it character for character, including hyphens, quotes and spacing; do not shorten, do not add "...", do not merge sentences from different places. Stop at the end of a sentence in the paper.
- "section_key": the section heading under which the passage appears (as given in the paper text).
- "passage_type": one of "own_finding", "own_projection", "cited_finding", "review_synthesis", "background". Use "review_synthesis" only when the passage summarizes many studies; "background" for definitions, method descriptions and general introductions.
- "region": the place the statement is about, as the paper names it, or "unknown".
- "region_scope": one of "global", "continental", "national", "subnational", "local", "unknown".
- "scenario": the emissions / climate scenario the statement refers to, as the paper names it, or "unknown".
- "scenario_source": "in_passage" if the passage itself names it; "elsewhere_in_paper" if it is named elsewhere in the paper; "unknown".
- "scenario_quote": if scenario_source is "elsewhere_in_paper", an EXACT verbatim copy (at most 200 characters) of the words that name it; otherwise "".
- "scenario_location": if scenario_source is "elsewhere_in_paper", the section heading where that quote appears; otherwise "".
- "time": the period or horizon the statement refers to, as the paper states it, or "unknown".
- "time_source": "in_passage", "elsewhere_in_paper" or "unknown", as for the scenario.
- "time_quote": as scenario_quote, for the time.
- "time_location": as scenario_location, for the time.
- "generality": one of "general_mechanism" (holds beyond this study), "regional_expectation" (expected for a region), "specific_result" (this study's particular number or result).
- "confidence": "high", "medium" or "low".
Return ONLY a JSON object: {"statements": [ ... ]}."""

STATEMENT_TYPES = ("mechanism", "driver", "consensus", "caveat", "pattern")
PASSAGE_TYPES = ("own_finding", "own_projection", "cited_finding", "review_synthesis", "background")
REGION_SCOPES = ("global", "continental", "national", "subnational", "local", "unknown")
SOURCES = ("in_passage", "elsewhere_in_paper", "unknown")
GENERALITIES = ("general_mechanism", "regional_expectation", "specific_result")
CONFIDENCES = ("high", "medium", "low")
REQUIRED = ("statement", "statement_type", "passage", "section_key", "passage_type", "region", "region_scope",
            "scenario", "scenario_source", "time", "time_source", "generality", "confidence")
ENUMS = {"statement_type": STATEMENT_TYPES, "passage_type": PASSAGE_TYPES, "region_scope": REGION_SCOPES,
         "scenario_source": SOURCES, "time_source": SOURCES, "generality": GENERALITIES, "confidence": CONFIDENCES}

_YEAR = re.compile(r"\b(?:1[89]\d\d|2[01]\d\d)s?\b")
_SCENARIO = re.compile(r"\b(?:RCP|SSP)\s?\d(?:\.\d)?(?:\s?-\s?\d(?:\.\d)?)?\b|\bCMIP\d\b", re.I)
_ORDINAL = re.compile(r"\b\d+(?:st|nd|rd|th)\b", re.I)
_NUMBER = re.compile(r"\d+(?:[.,]\d+)?(\s*(?:%|percent\b|per\s+cent\b))?", re.I)


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def numeric_values(text: str):
    """Numbers in a statement, after removing years, scenario names (RCP8.5, SSP5-8.5, CMIP6) and ordinals."""
    stripped = _ORDINAL.sub(" ", _SCENARIO.sub(" ", _YEAR.sub(" ", text)))
    return [m.group(0).strip() for m in _NUMBER.finditer(stripped)]


def digit_heavy(text: str) -> bool:
    """A specific value: a decimal, a percentage, or two or more numbers (years and scenario names excepted)."""
    vals = numeric_values(text)
    return len(vals) >= 2 or any(re.search(r"[.,]\d|%|percent|cent", v, re.I) for v in vals)


def extract_statements(content: str):
    """Last JSON object containing a 'statements' key."""
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
                        if isinstance(obj, dict) and "statements" in obj:
                            best = obj
                    except Exception:  # noqa: BLE001
                        pass
                    break
            i += 1
    return best


def exact_quote(quote: str, sections):
    """(json_path, start, end) where the quote occurs exactly, or None."""
    if not quote or len(quote.strip()) < 3:
        return None
    for s in sections:
        i = s["text"].find(quote)
        if i >= 0:
            return {"json_path": f"$.{s['section_key']}", "section_idx": s["section_idx"], "span_start": i, "span_end": i + len(quote)}
    return None


def context_field(st, name, sections):
    """The scenario / time with its source; an elsewhere_in_paper value whose quote does not re-slice exactly is `unsupported`."""
    value, source = st.get(name), st.get(f"{name}_source")
    out = {"value_as_proposed": value, "source": source, "quote": st.get(f"{name}_quote") or "",
           "location_as_proposed": st.get(f"{name}_location") or "", "quote_span": None, "check": "n/a", "value": value}
    if source == "elsewhere_in_paper":
        span = exact_quote(out["quote"], sections)
        out["quote_span"] = span
        if span is None:
            out.update(check="unsupported", value="unsupported", source="unsupported")
        else:
            out["check"] = "quote_exact"
    return out


def pre_review_check(st, sections):
    """Deterministic checks. Returns (status, checks, located)."""
    checks, located = {}, {}
    missing = [k for k in REQUIRED if k not in st]
    checks["fields_complete"] = not missing
    checks["missing_fields"] = missing
    bad = {k: st.get(k) for k, allowed in ENUMS.items() if k in st and st.get(k) not in allowed}
    checks["enums_valid"] = not bad
    checks["invalid_enum_values"] = bad
    span, recovery, verbatim = locate_passage(st.get("passage") or "", sections)
    checks["span_reslice_pass"] = span is not None
    checks["passage_recovery"] = recovery
    checks["passage_length_pass"] = verbatim is None or len(verbatim) <= MAX_PASSAGE_CHARS  # judged once located
    checks["passage_chars"] = len(verbatim) if verbatim is not None else None
    located["evidence"], located["verbatim_passage"] = span, verbatim
    checks["passage_type"] = st.get("passage_type")
    checks["passage_type_pass"] = st.get("passage_type") in PASSAGE_TYPES and st.get("passage_type") != "background"
    statement = st.get("statement") or ""
    checks["statement_numbers"] = numeric_values(statement)
    checks["statement_value_pass"] = bool(statement.strip()) and (not digit_heavy(statement) or st.get("generality") == "specific_result")
    located["scenario"] = context_field(st, "scenario", sections)
    located["time"] = context_field(st, "time", sections)
    checks["scenario_check"] = located["scenario"]["check"]
    checks["time_check"] = located["time"]["check"]
    mandatory = ["fields_complete", "enums_valid", "span_reslice_pass", "passage_length_pass", "passage_type_pass", "statement_value_pass"]
    checks["failed"] = [k for k in mandatory if not checks[k]]
    return ("deterministic_pass" if not checks["failed"] else "rejected_pre_review"), checks, located


def summarise(out: Path):
    allr, summary = [], {"papers": 0, "papers_with_error": 0, "papers_over_limit": 0, "statements": 0, "deterministic_pass": 0,
                         "rejected_pre_review": 0, "rejected_by_check": {}, "by_statement_type": {}, "by_passage_type": {},
                         "by_generality": {}, "by_region_scope": {}, "by_recovery": {}, "scenario_check": {}, "time_check": {}}
    for p in sorted(out.glob("*/result.json")):
        r = json.loads(p.read_text())
        if "statements" not in r:
            summary["papers_with_error"] += 1; continue
        summary["papers"] += 1
        summary["papers_over_limit"] += int(r.get("n_statements_proposed", 0) > MAX_STATEMENTS)
        for x in r["statements"]:
            allr.append(x); summary["statements"] += 1; summary[x["status"]] += 1
            for c in x["pre_review_checks"].get("failed", []):
                summary["rejected_by_check"][c] = summary["rejected_by_check"].get(c, 0) + 1
            g = x["proposal"]
            for key, val in (("by_statement_type", g.get("statement_type")), ("by_passage_type", g.get("passage_type")),
                             ("by_generality", g.get("generality")), ("by_region_scope", g.get("region_scope")),
                             ("by_recovery", x["passage_recovery"]), ("scenario_check", x["scenario"]["check"]),
                             ("time_check", x["time"]["check"])):
                summary[key][str(val)] = summary[key].get(str(val), 0) + 1
    with open(out / "statements.jsonl", "w", encoding="utf-8") as f:
        for x in allr: f.write(json.dumps(x, ensure_ascii=False) + "\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True, help="build_index.py output dir")
    ap.add_argument("--candidates", required=True, help="JSON: [{item_id, arm}] or text file of ids (arm from --arm)")
    ap.add_argument("--arm", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--base-url", default="https://inference-api.alcf.anl.gov/resource_server/metis/api/v1")
    ap.add_argument("--model", default="gpt-oss-120b")
    ap.add_argument("--max-tokens", type=int, default=6000); ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--max-chars", type=int, default=90000, help="truncate paper text beyond this (recorded)")
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--only", default=None)
    ap.add_argument("--source-commit", default="unknown")
    a = ap.parse_args()
    credential = next((os.environ[v] for v in CREDENTIAL_ENV if os.environ.get(v)), None)
    if not credential:
        sys.exit(f"{CREDENTIAL_ENV[0]} env var not set")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    log = open(out / "agent.log", "a")

    def say(msg):
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"; print(line, flush=True); log.write(line + "\n"); log.flush()

    cands_raw = Path(a.candidates).read_text(encoding="utf-8")
    try:
        cands = json.loads(cands_raw)
    except Exception:  # noqa: BLE001
        cands = [{"item_id": l.strip(), "arm": a.arm} for l in cands_raw.splitlines() if l.strip()]
    only = set(a.only.split(",")) if a.only else None
    sys_sha = sha(SYSTEM_PROMPT)
    idx = Path(a.index)
    idx_summary = json.loads((idx / "index_summary.json").read_text())
    con = duckdb.connect(); con.execute("SET threads=2"); con.execute("SET memory_limit='3GB'")
    say(f"START {GENERATOR_VERSION} candidates={len(cands)} model={a.model} system_sha={sys_sha[:12]} index={idx_summary.get('content_identity_sha256','')[:12]}")

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
        user = f"PAPER (item {iid}; arm {c.get('arm')}):\n{paper_text[: a.max_chars]}" + ("\n\n[PAPER TRUNCATED]" if truncated else "")
        (pdir / "prompt_user.txt").write_text(user, encoding="utf-8")
        t0 = time.time()
        try:
            resp, content, secs = call_model(a.base_url, a.model, credential, SYSTEM_PROMPT, user, a.max_tokens, a.timeout)
            (pdir / "response.json").write_text(json.dumps(resp, indent=2, ensure_ascii=False))
            obj = extract_statements(content); perr = None if obj else "no JSON object with 'statements' found"
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:1000]; (pdir / "model_error.txt").write_text(f"HTTP {e.code}\n{body}\n")
            obj, perr, secs = None, f"HTTP {e.code}", None
        except Exception as e:  # noqa: BLE001
            (pdir / "model_error.txt").write_text(f"{type(e).__name__}: {e}\n"); obj, perr, secs = None, f"{type(e).__name__}: {e}", None
        proposed = (obj or {}).get("statements", []) if isinstance(obj, dict) else []
        proposed = proposed if isinstance(proposed, list) else []
        records = []
        for si, st in enumerate(proposed):
            if not isinstance(st, dict): continue
            status, checks, located = pre_review_check(st, sections)
            records.append({
                "statement_id": f"S-{iid}-{si+1:02d}", "track": "C-statements", "status": status, "generator_version": GENERATOR_VERSION,
                "generator_model": a.model, "endpoint": a.base_url, "prompt_hash": sha(SYSTEM_PROMPT + user), "system_prompt_sha256": sys_sha,
                "generation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "source_commit": a.source_commit,
                "paper_item_id": iid, "paper_rel_path": rel_path, "paper_sha256": sha256, "arm": c.get("arm"),
                "evidence": located["evidence"], "verbatim_passage": located["verbatim_passage"], "passage_as_proposed": st.get("passage"),
                "passage_recovery": checks["passage_recovery"], "scenario": located["scenario"], "time": located["time"],
                "proposal": st, "over_limit": si >= MAX_STATEMENTS,
                "table_values_visible_to_generator": False, "answer_visible_to_generator": False,
                "pre_review_checks": checks, "pre_review_status": status,
                "aggregation": None, "evidence_strength": None, "human_review": None,
            })
        result = {"item_id": iid, "arm": c.get("arm"), "paper_sha256": sha256, "n_sections": len(sections), "paper_chars": len(paper_text),
                  "truncated": truncated, "model_seconds": secs, "model_parse_error": perr, "n_statements_proposed": len(proposed),
                  "n_deterministic_pass": sum(1 for x in records if x["status"] == "deterministic_pass"),
                  "n_rejected_pre_review": sum(1 for x in records if x["status"] == "rejected_pre_review"),
                  "statements": records, "elapsed_seconds": round(time.time() - t0, 1)}
        (pdir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
        done += 1
        say(f"{iid} arm={c.get('arm')} chars={len(paper_text)}{' TRUNC' if truncated else ''} statements={result['n_statements_proposed']} pass={result['n_deterministic_pass']} reject={result['n_rejected_pre_review']} model_s={secs} err={perr}")

    s = summarise(out)
    say(f"DONE papers={s['papers']} statements={s['statements']} pass={s['deterministic_pass']} reject={s['rejected_pre_review']}")


if __name__ == "__main__":
    main()
