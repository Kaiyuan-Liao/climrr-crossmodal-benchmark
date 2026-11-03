"""Pilot P2b item review workbook (P2b-ingest-items Phase C; D-056).

`artifacts/benchmark/review/P2b_items_review_v1.xlsx` (gitignored) has the sheets OVERVIEW, ITEMS (one row per item, in
the GUIDANCE field order, then the COORDINATOR's disposition and notes, then the empty reviewer columns), PROVENANCE (one
row per item: pattern, columns, row rule, DR id, FullData SHA-256, cited groups with papers and spans, packet SHA-256,
generation fields), GROUPS_CITED (every group any item cites), LINT (rubric lint v1, one row per flag) and Legend; the
ITEMS sheet is also written as the tracked `P2b_items_review_v1.csv`. A cell holding a list has one entry per line.

The `edited_*` cells are what becomes `review.final_frozen` after Kaiyuan's pass (applied by the next package; this one
only builds the sheet). Read from tracked files only (the run-2 items and manifest, the lint report, the COORDINATOR
notes, the packets v3a at the run's source commit), so a test can rebuild the CSV. No model call, no table value.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from climrr import litsynth_run2 as s2
from climrr import p2a_review as p2a
from climrr import rubric_lint as rl
from climrr.checksums import sha256_file
from climrr.manifest import load_entry
from climrr.paths import REPO_ROOT

REVIEW_DIR = REPO_ROOT / "artifacts" / "benchmark" / "review"
WORKBOOK_PATH = REVIEW_DIR / "P2b_items_review_v1.xlsx"
ITEMS_CSV_PATH = REVIEW_DIR / "P2b_items_review_v1.csv"
COORDINATOR_NOTES_PATH = REVIEW_DIR / "P2b_items_coordinator_notes_v1.csv"
COORDINATOR_NOTES_SHA256 = "1f4f72c39af8b73ed926dfe889c1784a6229afb11e7f7f7bca0e814ee1e849ea"
LINT_PATH = s2.ART / "rubric_lint_v1.json"
KAIYUAN_DISPOSITIONS = ("accept", "accept_with_edits", "reject", "regenerate")
REVIEWER_COLS = ["kaiyuan_disposition", "edited_prompt", "edited_reference_table", "edited_reference_literature",
                 "edited_reference_integrated", "edited_rubric_required", "edited_rubric_optional", "edited_rubric_fatal",
                 "kaiyuan_note", "mentor_disposition", "mentor_note"]
ITEMS_HEADER = ["item_id", "rung", "capability_tested", "prompt", "source_independent_answerability", "source_independence_note",
                "reference_answer.table_pattern", "reference_answer.literature_interpretation", "reference_answer.integrated",
                "rubric.required_points", "rubric.optional_points", "rubric.acceptable_variants", "rubric.disallowed_claims",
                "rubric.fatal_errors", "guardrails", "evidence_strength_summary", "leakage_check", "lint_flags",
                "coordinator_disposition", "coordinator_notes"] + REVIEWER_COLS


def _lines(xs) -> str:
    return "\n".join(xs)


def _tagged(it: dict) -> dict:
    return it["review"]["history"][0]["reference_answer_tagged"]


def cited_groups(it: dict) -> list[tuple[str, str]]:
    """(group id, where) in citation order: literature sentence L<n>, then rubric points R:<field>[i]."""
    t, out = _tagged(it), []
    for i, s in enumerate(t["literature_interpretation"]):
        out += [(g, f"L{i + 1}") for g in s.get("group_ids") or []]
    for i, p in enumerate(t.get("rubric_points") or []):
        out += [(g, f"R:{p['field']}[{i}]") for g in p.get("source_ids") or [] if g.startswith("LG-")]
    return out


def read_coordinator_notes(path: Path = COORDINATOR_NOTES_PATH) -> dict:
    rows = list(csv.DictReader(io.StringIO(Path(path).read_text(encoding="utf-8-sig"))))
    return {r["item_id"]: r for r in rows}


def evidence_summary(it: dict, packet: dict) -> str:
    groups = {g["group_id"]: g for g in packet["provenance"]["groups"]}
    out = []
    for i, s in enumerate(_tagged(it)["literature_interpretation"]):
        for g in s.get("group_ids") or []:
            pg = groups.get(g)
            out.append(f"L{i + 1}{' [hedged]' if s.get('hedged') else ''}: {g} ({pg['strength_in_packet'] if pg else 'not in packet'}"
                       f"{'; ' + str(pg['n_papers']) + ' papers' if pg else ''}) {pg['label'] or pg['members'][0]['statement'] if pg else ''}")
    for g, where in cited_groups(it):
        if where.startswith("R:"):
            pg = groups.get(g)
            out.append(f"{where}: {g} ({pg['strength_in_packet'] if pg else 'not in packet'})")
    return _lines(out) or "no literature group (rung 1: pattern only)"


def leakage_cell(it: dict) -> str:
    lk = it["source_leakage_check"]
    pl = it["review"]["history"][0]["checks"]["prompt_leakage"]
    return (f"{lk['check_version']}: pass={lk['pass']}; flags: {', '.join(lk['flags']) or 'none'}; "
            f"post-check prompt leakage pass={pl['pass']}")


def lint_cell(lint_item: dict) -> str:
    return _lines(f"{f['rule']} @ {f['field']}{'' if f['index'] is None else '[' + str(f['index']) + ']'}: {f['text']}"
                  for f in lint_item["flags"]) or "none"


def item_rows(items: list[dict], packets: dict, lint: dict, notes: dict) -> list[list]:
    by_lint = {x["item_id"]: x for x in lint["items"]}
    rows = [ITEMS_HEADER]
    for it in items:
        t, rub, n = _tagged(it), it["rubric"], notes[it["item_id"]]
        rows.append([it["item_id"], it["use_case_level"], it["capability_tested"], it["prompt"], it["source_independent_answerability"],
                     it["source_independence_note"], _lines(s["sentence"] for s in t["table_pattern"]),
                     _lines(s["sentence"] for s in t["literature_interpretation"]), t["integrated"],
                     *(_lines(rub[k]) for k in rl.RUBRIC_LISTS),
                     _lines(it["guardrails"]), evidence_summary(it, packets[it["item_id"]]), leakage_cell(it),
                     lint_cell(by_lint[it["item_id"]]), n["coordinator_disposition"], n["coordinator_notes"]] + [""] * len(REVIEWER_COLS))
    return rows


PROVENANCE_HEADER = ["item_id", "seed_id", "packet_id", "packet_version", "packet_sha256", "rung", "pattern_id", "metric", "geography",
                     "horizon", "scenario", "statistic", "columns", "row_rule", "derivation_rule_id", "member_rows_or_region_patterns",
                     "table_data_sha256", "table_data_is_fulldata_manifest_sha256", "provisional_reasons", "groups_cited",
                     "generator_version", "model", "endpoint_label", "reasoning_effort", "max_tokens", "temperature", "source_commit",
                     "generation_timestamp", "prompt_hash", "system_prompt_sha256", "corrective_turn_used", "corrective_class",
                     "model_attempts", "http_attempts", "model_seconds", "item_file_sha256"]


def _fulldata_sha() -> str:
    return load_entry("FullData.csv")["sha256"]


def groups_cited_cell(it: dict, packet: dict) -> str:
    stmts = {s["group_id"]: s for s in it["reference_components"]["literature_mechanisms"] + it["reference_components"]["literature_caveats"]}
    groups = {g["group_id"]: g for g in packet["provenance"]["groups"]}
    out, seen = [], set()
    for g, _ in cited_groups(it):
        if g in seen:
            continue
        seen.add(g)
        if g in stmts:
            sup = stmts[g]["supports"]
            out.append(f"{g}: papers {', '.join(sorted({x['paper_item_id'] for x in sup}))}; spans {len(sup)}")
        else:
            ms = groups[g]["members"]
            out.append(f"{g}: papers {', '.join(sorted({m['paper_item_id'] for m in ms}))}; spans {len(ms)} (cited in the rubric "
                       "only; not in reference_components)")
    return _lines(out)


def provenance_rows(items: list[dict], packets: dict, item_sha: dict) -> list[list]:
    full = _fulldata_sha()
    rows = [PROVENANCE_HEADER]
    for it in items:
        h, pk = it["review"]["history"][0], packets[it["item_id"]]
        for p in it["reference_components"]["table_patterns"]:
            pv = p["provenance"]
            rows.append([it["item_id"], h["seed_id"], h["packet_id"], pk["version"], h["packet_sha256"], it["use_case_level"],
                         p["pattern_id"], p["metric"], p["geography"], f"{p['horizon']} ({p['horizon_window']})", p["scenario"],
                         p["statistic"], _lines(f"{c['column']} ({pv['column_statuses'].get(c['column'])})" for c in pv["columns"]),
                         pv["row_rule"], pv["derivation_rule_id"],
                         pv.get("member_rows", "regions: " + ", ".join(pv.get("region_pattern_ids") or [])), pv["table_data_sha256"],
                         pv["table_data_sha256"] == full, _lines(p.get("provisional_reasons") or []), groups_cited_cell(it, pk),
                         h["generator_version"], h["model"], h["endpoint_label"], h["reasoning_effort"], h["max_tokens"],
                         h["temperature"], h["source_commit"], h["generation_timestamp"], h["prompt_hash"], h["system_prompt_sha256"],
                         h["corrective_turn_used"], h["corrective_class"], h["model_attempts"], sum(t["http_attempts"] for t in h["turns"]),
                         h["model_seconds"], item_sha[it["item_id"]]])
    return rows


GROUPS_HEADER = ["group_id", "label", "statement_type", "claim_about", "strength_in_packet", "group_strength_run", "n_members_in_packet",
                 "n_papers_in_packet", "members", "cited_by"]


def group_rows(items: list[dict], packets: dict) -> list[list]:
    cites: dict = {}
    for it in items:
        for g, where in cited_groups(it):
            cites.setdefault(g, []).append((it["item_id"], where))
    rows = [GROUPS_HEADER]
    for g in sorted(cites):
        recs = [next(x for x in packets[iid]["provenance"]["groups"] if x["group_id"] == g) for iid in dict.fromkeys(i for i, _ in cites[g])]
        first = recs[0]
        rows.append([g, first["label"] or first["members"][0]["statement"], first["statement_type"], first["claim_about"],
                     "; ".join(sorted({r["strength_in_packet"] for r in recs})), first["group_strength_run"],
                     "; ".join(sorted({str(len(r["members"])) for r in recs})), "; ".join(sorted({str(r["n_papers"]) for r in recs})),
                     _lines(f"{m['statement_id']} [{m['paper_item_id']}; {m['evidence_role']}]: {m['statement']}" for m in first["members"]),
                     _lines(f"{i} {w}" for i, w in cites[g])])
    return rows


LINT_HEADER = ["item_id", "rung", "rule", "field", "index", "text", "detail"]


def lint_rows(lint: dict) -> list[list]:
    return [LINT_HEADER] + [[x["item_id"], x["use_case_level"], f["rule"], f["field"], f["index"], f["text"], f["detail"]]
                            for x in lint["items"] for f in x["flags"]]


def overview_rows(man: dict, lint: dict, notes: dict, items: list[dict]) -> list[list]:
    k = man["counts"]
    disp: dict = {}
    for n in notes.values():
        disp[n["coordinator_disposition"]] = disp.get(n["coordinator_disposition"], 0) + 1
    rows = [["item", "value"],
            ["run", f"litsynth run 2 ({man['generator']['version']}, {man['endpoint']['endpoint_label']} {man['endpoint']['model']}; "
                    f"reasoning {man['budget']['reasoning_effort']}, max_tokens {man['budget']['max_tokens']}; {man['decision']})"],
            ["tarball sha256", man["tarball"]["sha256"]], ["source commit", man["source_commit"]],
            ["agent / system prompt / format-corrective template sha256",
             f"{man['generator']['agent_sha256']} / {man['generator']['system_prompt_sha256']} / "
             f"{man['generator']['format_corrective_template_sha256']}"],
            ["packets", f"{man['packets']['version']} (manifest {man['packets']['manifest_sha256']}, at {man['packets']['at_commit'][:7]})"],
            ["items.jsonl / summary.json sha256", f"{man['items_sha256']} / {man['summary_sha256']}"],
            ["items / deterministic_pass / leakage flags", f"{k['items']} / {k['deterministic_pass']} / {k['leakage_flags']}"],
            ["format corrective turn used (all passed)", ", ".join(man["format_corrective_items"])],
            ["HTTP retries recovered", "; ".join(f"{x['seed_id']}: {x['reason']}" for x in man["http_retries_recovered"])],
            ["post-checks reproduced at ingest", f"{man['checks_reproduced']} ({man['checks']['check_version']})"],
            ["review status (all items)", ", ".join(sorted({it["review"]["status"] for it in items}))],
            ["items by rung", "; ".join(f"rung {r}: {sum(it['use_case_level'] == r for it in items)}"
                                        for r in sorted({it["use_case_level"] for it in items}))],
            ["superseded runs", "; ".join(f"{x['run']} ({x['generator_version']}; {x['reason']})" for x in man["superseded_runs"])],
            ["COORDINATOR notes", f"{COORDINATOR_NOTES_PATH.name} (sha256 {sha256_file(COORDINATOR_NOTES_PATH)}): "
                                  + "; ".join(f"{d} {n}" for d, n in sorted(disp.items()))],
            ["rubric lint", f"{lint['version']}: " + "; ".join(f"{r} {n}" for r, n in lint["totals"].items())]]
    rows += [[f"lint {x['item_id']} (rung {x['use_case_level']})", "; ".join(f"{r} {n}" for r, n in x["counts"].items() if n) or "none"]
             for x in lint["items"]]
    return rows


LEGEND = [["field", "meaning"],
          ["ITEMS order", "the GUIDANCE field order, then the COORDINATOR's disposition and notes, then the reviewer columns"],
          ["reference_answer.*", "one tagged sentence per line (review.history[0].reference_answer_tagged); integrated is one paragraph"],
          ["rubric.*", "one entry per line; '[w=n]' is a required point's weight (1-3)"],
          ["evidence_strength_summary", "L<n>: literature sentence n, '[hedged]' when the model marked it, then each cited group with its "
                                        "strength over the packet's relevant members and paper count; R:<field>[i]: a rubric point's group"],
          ["evidence strength", "multi_source_supported: >= 2 independent papers (DR-LIT-IND-1 v2) among core / cited members; "
                                "review_supported: a review_synthesis member; single_source_supported: one paper (D-045, D-048)"],
          ["leakage_check", "leakage_check v1 on the prompt (ClimRR named, column / cell, paper, hidden exact value, 'according to')"],
          ["lint_flags", rl.VERSION_V1 + ": the reviewer's checklist; no item was edited. Rules: "
                         + "; ".join(f"{r} = {d}" for r, d in rl.rules(rl.VERSION_V1).items())],
          ["coordinator_disposition / notes", f"from {COORDINATOR_NOTES_PATH.name}, verbatim"],
          ["kaiyuan_disposition", "accept | accept_with_edits | reject | regenerate (a reviewer vocabulary; schema v2's disposition enum is "
                                  "accept / accept_after_edit / reject / needs_revision --- the next package maps it)"],
          ["edited_*", "leave empty to keep the item's text; filled cells become review.final_frozen (prompt, reference_answer, rubric) "
                       "in the next package. One entry per line in the rubric cells"],
          ["mentor_disposition / mentor_note", "for the mentor review (Thursday 2026-11-05)"],
          ["PROVENANCE", "table pattern (columns with their status, row rule, derivation rule id, FullData SHA-256), cited groups with "
                         "papers and spans, packet and generation fields; exact values stay in the item's reference_components only"],
          ["status", "every item is human_review: nothing here is accepted"]]


def workbook_sheets(man: dict, items: list[dict], packets: dict, lint: dict, notes: dict, item_sha: dict) -> list[tuple]:
    return [("OVERVIEW", overview_rows(man, lint, notes, items), [48, 140]),
            ("ITEMS", item_rows(items, packets, lint, notes),
             [13, 6, 22, 60, 12, 40, 60, 70, 70, 60, 45, 50, 50, 50, 50, 70, 30, 60, 18, 70] + [20, 50, 50, 60, 60, 60, 45, 45, 40, 18, 40]),
            ("PROVENANCE", provenance_rows(items, packets, item_sha),
             [13, 15, 18, 18, 22, 6, 11, 26, 18, 18, 9, 16, 40, 22, 22, 9, 22, 10, 50, 70] + [16] * 16),
            ("GROUPS_CITED", group_rows(items, packets), [36, 50, 12, 28, 24, 24, 8, 8, 110, 36]),
            ("LINT", lint_rows(lint), [13, 6, 26, 40, 6, 90, 50]),
            ("Legend", LEGEND, [32, 140])]


def inputs() -> tuple:
    """(items manifest, items in id order, {item_id: packet v3a}, lint report, COORDINATOR notes, {item_id: file sha256})."""
    load = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))  # noqa: E731
    man = load(s2.MANIFEST_PATH)
    items = [load(s2.ART / x["path"]) for x in man["items_ingested"]]
    packets = {it["item_id"]: s2.packet_at_source(it["review"]["history"][0]["seed_id"])[0] for it in items}
    item_sha = {x["item_id"]: x["sha256"] for x in man["items_ingested"]}
    return man, items, packets, load(LINT_PATH), read_coordinator_notes(), item_sha


items_csv = p2a.seeds_csv


# --- v2 (mentor-export package, 2026-11-03) --------------------------------------------------------------------------
# The same workbook over the *current* items of the items index (run 2 for 0001-0009, run 3 for 0010), with rubric lint
# v1a, the COORDINATOR notes column unchanged, and the COORDINATOR-proposed texts written into `edited_prompt` /
# `edited_reference_integrated` with a new column `edit_origin` = coordinator_proposed (recorded, not frozen). v1 and its
# CSV are kept as built.

WORKBOOK_V2_PATH = REVIEW_DIR / "P2b_items_review_v2.xlsx"
ITEMS_CSV_V2_PATH = REVIEW_DIR / "P2b_items_review_v2.csv"
LINT_V1A_PATH = s2.ART.parent / "rubric_lint_v1a.json"
EDIT_ORIGIN_COL = "edit_origin"
EDITED_COLS = {"edited_prompt": "edited_prompt", "edited_reference_integrated": "edited_reference_integrated"}


def item_rows_v2(items: list[dict], packets: dict, lint: dict, notes: dict, edits: dict) -> list[list]:
    """`item_rows` with `edit_origin` after `edited_reference_integrated` and the proposed texts filled in."""
    rows = item_rows(items, packets, lint, notes)
    at = rows[0].index("edited_reference_integrated") + 1
    out = [rows[0][:at] + [EDIT_ORIGIN_COL] + rows[0][at:]]
    for r in rows[1:]:
        e = edits.get(r[0])
        r = list(r)
        if e:
            for col, key in EDITED_COLS.items():
                r[rows[0].index(col)] = e[key]
        out.append(r[:at] + [e["edit_origin"] if e else ""] + r[at:])
    return out


def overview_rows_v2(man2: dict, man3: dict, index: dict, lint: dict, notes: dict, items: list[dict], edits: dict) -> list[list]:
    rows = overview_rows(man2, lint, notes, items)
    rows += [["run 3 (BI-P2B-0010 only)", f"{man3['generator']['version']} on {man3['packets']['version']} "
                                          f"({man3['packets']['only']}, at {man3['source_commit'][:7]}); "
                                          f"{man3['counts']['deterministic_pass']} / {man3['counts']['items']} deterministic_pass, "
                                          f"{man3['counts']['leakage_flags']} leakage flags, no corrective turn; checks reproduced "
                                          f"{man3['checks_reproduced']}"],
             ["run 3 tarball sha256", man3["tarball"]["sha256"]],
             ["items index", "; ".join(f"{x['item_id']}: {x['current']['run']}" for x in index["items"])
              + "; superseded: " + ", ".join(f"{x['item_id']} {v['run']} ({v['index_status']})" for x in index["items"]
                                            for v in x["versions"] if v["index_status"] != "current")],
             ["COORDINATOR-proposed edits", f"{len(edits)} items ({', '.join(edits)}): edited_prompt and edited_reference_integrated, "
                                            "edit_origin = coordinator_proposed; recorded, not frozen (Kaiyuan confirms or rewrites)"]]
    return rows


LEGEND_V2 = [r for r in LEGEND if r[0] != "lint_flags"] + [
    ["lint_flags", rl.VERSION + ": the reviewer's checklist; no item was edited. Rules: "
                   + "; ".join(f"{r} = {d}" for r, d in rl.rules(rl.VERSION).items())],
    ["edit_origin", "coordinator_proposed: the edited_prompt / edited_reference_integrated cells hold the COORDINATOR's proposed "
                    "texts (2026-11-03), not yet confirmed; empty: no edit proposed"],
    ["BI-P2B-0010", "the row is the run-3 version (packets v3b); the COORDINATOR notes column is unchanged and refers to the "
                    "run-2 version it superseded"],
]


def inputs_v2() -> tuple:
    """(run-2 manifest, run-3 manifest, items index, current items in id order, {item_id: packet}, lint v1a, notes,
    {item_id: file sha256})."""
    from climrr import litsynth_run3 as s3
    load = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))  # noqa: E731
    index = load(s3.INDEX_PATH)
    items = s3.current_items()
    packets = {it["item_id"]: s2.packet_for_item(it) for it in items}
    item_sha = {x["item_id"]: x["current"]["sha256"] for x in index["items"]}
    return (load(s2.MANIFEST_PATH), load(s3.MANIFEST_PATH), index, items, packets, load(LINT_V1A_PATH), read_coordinator_notes(),
            item_sha)


def workbook_sheets_v2(man2: dict, man3: dict, index: dict, items: list[dict], packets: dict, lint: dict, notes: dict,
                       item_sha: dict, edits: dict) -> list[tuple]:
    v1 = {name: widths for name, _, widths in workbook_sheets(man2, items, packets, lint, notes, item_sha)}
    at = ITEMS_HEADER.index("edited_reference_integrated") + 1
    return [("OVERVIEW", overview_rows_v2(man2, man3, index, lint, notes, items, edits), v1["OVERVIEW"]),
            ("ITEMS", item_rows_v2(items, packets, lint, notes, edits), v1["ITEMS"][:at] + [22] + v1["ITEMS"][at:]),
            ("PROVENANCE", provenance_rows(items, packets, item_sha), v1["PROVENANCE"]),
            ("GROUPS_CITED", group_rows(items, packets), v1["GROUPS_CITED"]),
            ("LINT", lint_rows(lint), v1["LINT"]),
            ("Legend", LEGEND_V2, v1["Legend"])]
