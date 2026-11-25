"""Sample sheet for Alvi: the six rung-8 hazard -> infrastructure items (work package P5d, part C; D-079, D-080).

Implemented in P5c (part D, not run); P5d gives it its inputs and final form. `scripts/build_mentor_sheet.py --audience alvi`
reads the rung-8 packets v1b (`synth_packets_infra_v1b/`, each checked against its manifest) and the ingested infra synthesis
run 2 (`artifacts/benchmark/items/infra_run2/`, each item checked against the run manifest and built from its packet), as the
mentor sheet v2 does (`mentor_sheet_v2b.load_packets` / `load_items`; the two rejected items are not on the sheet). One row per
item in the work package's order (`ORDER`). Columns, exactly:

- `#` --- the position and the item id;
- `Question`, `Answer` --- the display text: the D-079 text (`litsynth_infra_run2.display_text`: polished only if the polish
  passed and post-checks v3.5 pass on it) with the COORDINATOR display edits applied (`P5_display_edits_v1.yaml`);
- `Asset class (CISA sector)` --- the CISA sector name and the asset-class phrase the item uses;
- `Table side` --- as on the mentor sheet (`mentor_sheet_v2b.table_side`), plus "Place-named impact evidence: yes/no" (the
  packet's `place_named_impact_evidence`, with the number of cited impact groups whose papers name the state);
- `Paper side` --- per cited group, impact groups first, then drivers: "Impact, research shows (N papers): <label>" or
  "research suggests (1 paper)" by the group's strength (D-062); a two-hop group marked "--- via wildfire occurrence"
  (D-073c); an impact group whose papers name the item's state marked "[place-named: <State>]";
- `Original passages` --- per cited group, in the same order, every member passage verbatim with paper id and section.

README of five lines (`README_LINES`). The Markdown copy has the same content. `render_notes`: the notes for Kaiyuan (what each
item rests on, the two dropped cells and why, run history). `edited_text_checks`: leakage v2.3 and post-checks v3.5 on every
edited text (report only). No model call; no item modified.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from climrr import benchmark_items as bi
from climrr import litsynth_infra_run2 as ir
from climrr import mentor_sheet_v2b as ms
from climrr import p2b_mentor_export as mx
from climrr import synthpackets_infra as spi
from climrr.checksums import sha256_file

REVIEW_DIR = ms.REVIEW_DIR
SHEET_DATE = "2026-11-25"
SHEET_ID = SHEET_DATE
MD_PATH = REVIEW_DIR / f"ALVI_SAMPLE_ITEMS_{SHEET_DATE}.md"
XLSX_PATH = REVIEW_DIR / f"ALVI_SAMPLE_ITEMS_{SHEET_DATE}.xlsx"
NOTES_PATH = REVIEW_DIR / f"ALVI_SAMPLE_ITEMS_{SHEET_DATE}_notes.md"
PACKETS_DIR = spi.PACKETS_V1B_DIR
ITEMS_DIR = ir.ART
EDITS_PATH = REVIEW_DIR / "P5_display_edits_v1.yaml"
EDITS_CHECKS_PATH = REVIEW_DIR / "P5_display_edits_v1_checks.json"
EDIT_ORIGIN = "coordinator_edit"
ORDER = [("BI-P5-0001", "energy / heat (Virginia)"), ("BI-P5-0002", "transportation / heat (Arizona)"),
         ("BI-P5-0004", "healthcare / heat (California)"), ("BI-P5-0006", "transportation / fire weather (California)"),
         ("BI-P5-0007", "emergency services / fire weather (California)"), ("BI-P5-0008", "communications / fire weather (California)")]
HEADER = ["#", "Question", "Answer", "Asset class (CISA sector)", "Table side", "Paper side", "Original passages"]
WIDTHS = [12, 45, 60, 32, 60, 55, 80]
HEDGE = {"multi_source_supported": "research shows", "review_supported": "research shows",
         "single_source_supported": "research suggests"}
README_LINES = [
    ["What this item type is",
     "Each item pairs a projected hazard change at one place (from the ClimRR table: dangerous heat-index days or summer "
     "fire-weather danger) with what research shows such conditions do to one class of infrastructure (a CISA sector). No item "
     "says that a particular asset at the place will fail."],
    ["The question is all the model sees",
     "The model under test gets only the Question: no table, no paper, no data."],
    ["Grading is at pattern level",
     "Direction and rough size of the hazard change, the drivers, and the kind of impact on the asset class. The values in "
     "'Table side' are where the answer comes from; the model is not expected to give them."],
    ["'Research suggests'",
     "Marks a finding from one paper in our literature corpus ('research shows': two or more papers)."],
    ["Our three questions for you",
     "(1) Are these the hazard -> infrastructure questions and answers scientists want? (2) Which asset classes and which "
     "impact types matter most? (3) Is the general-evidence wording (\"not findings specific to California\") acceptable, or "
     "should items be restricted to evidence that names the place?"],
]


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def order(_packets_manifest: dict | None = None) -> list[str]:
    return [i for i, _ in ORDER]


# --- COORDINATOR display edits ------------------------------------------------------------------------------------


def load_edits(path: Path = EDITS_PATH) -> dict:
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    _check(doc.get("edit_origin") == EDIT_ORIGIN and doc.get("by") == "COORDINATOR", f"{path}: not a COORDINATOR display edit")
    ids = set(order())
    seen = set()
    for e in doc.get("items") or []:
        _check(e["item_id"] in ids and e["item_id"] not in seen, f"{e['item_id']}: not a sample item, or listed twice")
        seen.add(e["item_id"])
        for op in e["edits"]:
            _check(("find" in op and "replace" in op) != ("delete_sentence" in op), f"{e['item_id']}: malformed edit {op}")
    for op in doc.get("all_items") or []:
        _check(op.get("id") and (("find" in op) != ("find_regex" in op)) and "replace" in op, f"malformed all_items edit {op}")
    return doc


def apply_edits(text: str, item_id: str, doc: dict) -> tuple[str, list[dict]]:
    """(edited answer, log). `all_items` edits where their phrase occurs (else logged as absent); item edits exactly once."""
    log = []
    for op in doc.get("all_items") or []:
        if "find_regex" in op:
            ms_ = list(re.finditer(op["find_regex"], text))
            _check(len(ms_) <= 1, f"{item_id}: {op['id']} matches {len(ms_)} times")
            if ms_:
                new = op["replace"].format(**ms_[0].groupdict())
                log.append({"edit": op["id"], "applied": True, "old": ms_[0].group(0), "new": new})
                text = text.replace(ms_[0].group(0), new)
            else:
                log.append({"edit": op["id"], "applied": False, "reason": "phrase absent from the display text"})
        else:
            n = text.count(op["find"])
            _check(n <= 1, f"{item_id}: {op['id']} occurs {n} times")
            if n:
                text = text.replace(op["find"], op["replace"])
                log.append({"edit": op["id"], "applied": True, "old": op["find"], "new": op["replace"]})
            else:
                log.append({"edit": op["id"], "applied": False, "reason": "phrase absent from the display text"})
    rec = next((e for e in doc.get("items") or [] if e["item_id"] == item_id), None)
    for k, op in enumerate(rec["edits"] if rec else [], 1):
        old = op.get("find") or op["delete_sentence"]
        _check(text.count(old) == 1, f"{item_id}: edit {k} {old[:50]!r} found {text.count(old)} times (must be once)")
        if "delete_sentence" in op:
            span = (" " + old) if (" " + old) in text else old
            text = text.replace(span, "")
            log.append({"edit": f"{item_id}#{k}", "applied": True, "old": old, "new": None, "kind": "delete_sentence"})
        else:
            text = text.replace(old, op["replace"])
            log.append({"edit": f"{item_id}#{k}", "applied": True, "old": old, "new": op["replace"]})
    return text, log


def display(item: dict, doc: dict | None) -> dict:
    """{prompt, answer, base_source, display_source, edits}: the D-079 text, then the COORDINATOR edits (answer only)."""
    base = ir.display_text(item)
    hr = next(h for h in reversed(item["review"]["history"]) if h.get("event") == "human_review")
    answer, log = apply_edits(base["answer"], item["item_id"], doc) if doc else (base["answer"], [])
    changed = answer != base["answer"]
    return {"prompt": base["prompt"], "answer": answer, "base_source": hr["display_source"],
            "display_source": EDIT_ORIGIN if changed else hr["display_source"], "edits": log, "base_answer": base["answer"],
            "groups_removed": removed_groups(item, log)}


def removed_groups(item: dict, log: list[dict]) -> list[str]:
    """Groups cited only by tagged literature sentences that a `delete_sentence` edit removed from the displayed answer."""
    lit = item["review"]["history"][0]["reference_answer_tagged"]["literature_interpretation"]
    gone = {bi.phrase_key(e["old"]) for e in log if e.get("kind") == "delete_sentence"}
    dropped = [s for s in lit if bi.phrase_key(s["sentence"]) in gone]
    _check(len(dropped) == len(gone), f"{item['item_id']}: a deleted sentence is not a tagged literature sentence")
    kept = {g for s in lit if s not in dropped for g in s.get("group_ids") or []}
    return sorted({g for s in dropped for g in s.get("group_ids") or []} - kept)


# --- cells ---------------------------------------------------------------------------------------------------------


def asset_cell(packet: dict) -> str:
    mv = packet["model_view"]
    return f"{mv['cisa_sector']} (in the item: \"{mv['asset_class_phrase']}\")"


def cited(item: dict, packet: dict) -> list[dict]:
    """Cited groups, impact groups first, then drivers (each in order of first citation), with strength checks."""
    groups = {g["group_id"]: g for g in packet["provenance"]["groups"]}
    rc = item["reference_components"]
    stmts = {s["group_id"]: s for s in rc["literature_mechanisms"] + rc["literature_caveats"]}
    out = []
    for gid in ms.cited_groups(item):
        g, s = groups[gid], stmts[gid]
        _check(s["evidence_strength"] == g["strength_in_packet"], f"{gid}: strength differs between item and packet")
        _check((g["n_papers"] == 1) == (g["strength_in_packet"] == "single_source_supported") or g["strength_in_packet"] == "review_supported",
               f"{gid}: {g['n_papers']} papers but {g['strength_in_packet']}")
        out.append({"group": g, "statement": s, "label": g["label"] or s["statement"], "impact": g["role"] == "impact"})
    return [x for x in out if x["impact"]] + [x for x in out if not x["impact"]]


def place_named_cell(item: dict, packet: dict) -> str:
    yes = packet["place_named_impact_evidence"] == "place_named_impact_statement"
    k = sum(1 for x in cited(item, packet) if x["impact"] and x["group"].get("relevance") == "place_named")
    if yes:
        return f"Place-named impact evidence: yes (cited impact groups resting on papers that name {packet['state']}: {k})"
    return f"Place-named impact evidence: no (no impact statement in our corpus names {packet['state']}; general evidence only)"


def table_side(item: dict, packet: dict) -> str:
    return ms.table_side(packet) + "\n" + place_named_cell(item, packet)


def paper_cells(item: dict, packet: dict, removed: list[str] = ()) -> tuple[str, str]:
    """`removed`: groups whose only sentence a COORDINATOR edit deleted from the displayed answer (marked, still listed)."""
    side, passages = [], []
    for x in cited(item, packet):
        g, s, label = x["group"], x["statement"], x["label"]
        n = g["n_papers"]
        note = " (a review among them)" if g["strength_in_packet"] == "review_supported" else ""
        hop = " --- via wildfire occurrence" if g.get("two_hop") else ""
        place = f" [place-named: {packet['state']}]" if x["impact"] and g.get("relevance") == "place_named" else ""
        gone = " [not in the displayed answer: its sentence was removed by a COORDINATOR edit]" if g["group_id"] in removed else ""
        side.append(f"{'Impact' if x['impact'] else 'Driver'}, {HEDGE[g['strength_in_packet']]} ({n} paper{'s' if n != 1 else ''})"
                    f"{note}: {label}{hop}{place}{gone}")
        passages.append(f"[{label}]")
        for m in g["members"]:
            sup = next((y for y in s["supports"] if y["statement_id"] == m["statement_id"]), None)
            _check(sup is None or sup["verbatim_passage"] == m["verbatim_passage"], f"{m['statement_id']}: passage differs from the item")
            passages.append(f"  paper {m['paper_item_id']}, {ms._section(m['json_path'])}: \"{m['verbatim_passage']}\"")
    return "\n".join(side), "\n".join(passages)


def rows(packets: dict, items: dict, doc: dict | None) -> tuple[list[list], dict]:
    """(sheet rows, {item_id: display record})."""
    ids = order()
    _check(set(ids) <= set(items), f"items {sorted(items)} lack sample items {sorted(set(ids) - set(items))}")
    out, disp = [HEADER], {}
    for n, iid in enumerate(ids, 1):
        it, pk = items[iid], packets[iid]
        _check(it["review"]["status"] == "human_review", f"{iid}: status {it['review']['status']}")
        _check([w["id"] for w in it["review"]["history"][0]["working_assumptions_relied_on"]]
               == [w["id"] for w in pk["working_assumptions_relied_on"]], f"{iid}: working assumptions differ from the packet")
        d = display(it, doc)
        disp[iid] = d
        side, passages = paper_cells(it, pk, d["groups_removed"])
        out.append([f"{n}\n{iid}", d["prompt"], d["answer"], asset_cell(pk), table_side(it, pk), side, passages])
    return out, disp


def render_md(rs: list[list]) -> str:
    out = [f"# Sample hazard -> infrastructure items for Alvi --- {SHEET_DATE}", "",
           f"{len(rs) - 1} sample items (three heat, three fire weather). Same content as `{XLSX_PATH.name}` (sheets ITEMS and "
           "README).", "", "## README", ""]
    out += [f"- **{k}.** {v}" for k, v in README_LINES]
    for r in rs[1:]:
        n, iid = r[0].split("\n")
        out += ["", f"## {n} · {iid}", ""]
        for h, v in zip(rs[0][1:], r[1:]):
            out += [f"### {h}", ""]
            if h in ("Table side", "Paper side", "Original passages"):
                out += [f"    - {ln.strip()}" if ln.startswith("  ") else f"- {ln}" for ln in v.split("\n")]
            else:
                out.append(v)
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def sheets(rs: list[list]) -> list[tuple]:
    return [("ITEMS", rs, WIDTHS), ("README", [list(x) for x in README_LINES], [36, 110])]


def load(packets_dir: Path = PACKETS_DIR, items_dir: Path = ITEMS_DIR) -> tuple[dict, dict, dict, dict]:
    """(packets manifest, packets, items in human_review, run manifest)."""
    man, packets = ms.load_packets(packets_dir)
    run = json.loads((Path(items_dir) / "manifest.json").read_text(encoding="utf-8"))
    items = {iid: it for iid, it in ms.load_items(items_dir, man).items() if it["review"]["status"] == "human_review"}
    return man, packets, items, run


def build(packets_dir: Path = PACKETS_DIR, items_dir: Path = ITEMS_DIR, edits_path: Path | None = EDITS_PATH):
    man, packets, items, run = load(packets_dir, items_dir)
    doc = load_edits(edits_path) if edits_path else None
    rs, disp = rows(packets, items, doc)
    return man, rs, disp, packets, items, run


# --- checks on the edited texts ------------------------------------------------------------------------------------


def edited_text_checks(items: dict, packets: dict, disp: dict, edits_path: Path = EDITS_PATH, columns: list[str] | None = None) -> dict:
    """Per edited item, on its sheet text: leakage v2.3 (question, answer) and post-checks v3.5 against its v1b packet (the
    tagged sentences and rubric are the run's, which passed). Where the closing-clause edit applied, a diagnostic run with
    only the closing clause put back to the packet's wording isolates what the clause edit alone causes. Report only."""
    cols = columns if columns is not None else bi.column_names()
    out = []
    for iid in order():
        d = disp[iid]
        if d["display_source"] != EDIT_ORIGIN:
            continue
        pk = packets[iid]
        lk = mx.edited_text_flags({"item_id": iid, "edited_prompt": d["prompt"], "edited_reference_integrated": d["answer"]}, cols)
        pc = ir.recheck(items[iid], {"prompt": d["prompt"], "answer": d["answer"]}, pk, cols)
        rec = {"item_id": iid, "base_source": d["base_source"], "edits_applied": [e["edit"] for e in d["edits"] if e["applied"]],
               "edits_absent": [e["edit"] for e in d["edits"] if not e["applied"]], "display_answer": d["answer"],
               "leakage_v2_3": {"prompt": lk["prompt"], "answer": lk["reference_integrated"]},
               "post_checks_v3_5": {"pass": pc["pass"], "reasons": pc["reasons"]}}
        clause = next((e for e in d["edits"] if e["edit"] == "closing_clause" and e["applied"]), None)
        if clause:
            back = d["answer"].replace(clause["new"], clause["old"])
            pb = ir.recheck(items[iid], {"prompt": d["prompt"], "answer": back}, pk, cols)
            rec["post_checks_v3_5_closing_clause_reverted"] = {"pass": pb["pass"], "reasons": pb["reasons"],
                                                               "packet_general_clause": pk["checks_input"]["scope"]["general_clause"]}
        out.append(rec)
    fails = [x["item_id"] for x in out if x["leakage_v2_3"]["prompt"] or x["leakage_v2_3"]["answer"] or not x["post_checks_v3_5"]["pass"]]
    lk_fails = [x["item_id"] for x in out if x["leakage_v2_3"]["prompt"] or x["leakage_v2_3"]["answer"]]
    rev_fails = [x["item_id"] for x in out if not x.get("post_checks_v3_5_closing_clause_reverted", x["post_checks_v3_5"])["pass"]]
    return {"version": "P5 display edits v1 checks", "edits_sha256": sha256_file(edits_path),
            "leakage_check_version": bi.SYNTH_CHECK_VERSION_V23, "post_check_version": bi.SYNTH_CHECK_VERSION_V35,
            "report_only": True, "items_modified": 0, "items": out,
            "not_edited": [iid for iid in order() if disp[iid]["display_source"] != EDIT_ORIGIN],
            "failures": len(fails), "items_failing": fails, "leakage_failures": len(lk_fails),
            "failures_with_closing_clause_reverted": len(rev_fails),
            "reading": ("post-checks v3.5 compare the closing clause with the packet's pinned general_clause ('These are general "
                        "drivers of <quantity>, not findings specific to <Place>.'), and the new wording names 'research', so the "
                        "D-069 scope-opener rule for paragraph sentences also catches it; with only the clause put back, the "
                        "count is failures_with_closing_clause_reverted")}


# --- notes for Kaiyuan ---------------------------------------------------------------------------------------------


def render_notes(rs: list[list], disp: dict, packets: dict, items: dict, run: dict, checks: dict) -> str:
    out = [f"# Notes for Kaiyuan --- Alvi sample sheet {SHEET_DATE}", "",
           f"Companion to `{MD_PATH.name}` (not for Alvi). Built by `scripts/build_mentor_sheet.py --audience alvi`; no model call.",
           "", "## Run history", "",
           "- **Infra synthesis run 1** (agent v5.3, packets v1a, source `b860658`): 2 pass (BI-P5-0001, 0003), 6 rejected, all "
           "template conformance. Superseded; polish run 1 polished 0003, rejected 0001. Its two passing items are now the "
           "regression fixture (they pass post-checks v3.5 against their v1a packets; budget reported, not enforced).",
           "- **Infra synthesis run 2** (agent v5.4, packets v1b, source `bf69970`; D-080): first pass 5 of 8; BI-P5-0002, 0003 "
           "and 0005 redrawn once each -> 0002 passed; **6 pass, 2 rejected after a second attempt**.",
           "- **Polish infra run 2** (agent v1.1, checks v2): 4 polished (0002, 0004, 0006, 0007), 2 rejected (0001 places, "
           "0008 hedges).",
           "- **D-079 display rule** (polished only if it also passes post-checks v3.5): only BI-P5-0002 shows its polished text; "
           "0004 and 0006 rewrites split sentences beyond the answer-shape budget, 0007's rewrite drops the 'In general,' scope "
           "opener; 0001 and 0008 were polish-rejected.",
           f"- **COORDINATOR display edits** (`{EDITS_PATH.name}`): leakage v2.3 failures {checks['leakage_failures']}; post-checks "
           f"v3.5 failures {checks['failures']} ({', '.join(checks['items_failing']) or 'none'}), "
           f"{checks['failures_with_closing_clause_reverted']} with only the closing clause put back (`{EDITS_CHECKS_PATH.name}`). "
           "The closing-clause edit ('All six') applies where the clause exists: "
           f"{', '.join(i for i in order() if any(e['edit'] == 'closing_clause' and e['applied'] for e in disp[i]['edits']))}; "
           f"{', '.join(i for i in order() if not any(e['edit'] == 'closing_clause' and e['applied'] for e in disp[i]['edits']))} "
           "carry none (D-069: they cite a California-specific driver group, and post-checks v3.5 fail a clause there), so none "
           "was added --- for the COORDINATOR.",
           "", "## The two dropped cells", ""]
    for iid, r in sorted(run["rejected_pre_review"].items()):
        pk_ = json.loads((PACKETS_DIR / f"PK-{ir.SUPERSEDED[iid]['seed_id']}.json").read_text(encoding="utf-8"))
        out.append(f"- **{iid}** ({pk_['model_view']['cisa_sector']}, {pk_['family'].replace('_', ' ')}, {pk_['state']}): "
                   f"rejected_pre_review, redraws {r['redraws']} --- {r['reading']}. Not on the sheet.")
    out += ["", "## What each item rests on", ""]
    for r in rs[1:]:
        n, iid = r[0].split("\n")
        pk, d = packets[iid], disp[iid]
        hr = next(h for h in reversed(items[iid]["review"]["history"]) if h.get("event") == "human_review")
        groups = cited(items[iid], pk)
        out += [f"### {n} · {iid} --- {dict(ORDER)[iid]}", "",
                f"- Table: {pk['family'].replace('_', ' ')}, {pk['state']}; "
                f"{next(ln for ln in r[4].splitlines() if ln.startswith('Pattern descriptor')).split(': ', 1)[1]}.",
                f"- {place_named_cell(items[iid], pk)}.",
                f"- Cited: {sum(x['impact'] for x in groups)} impact group(s), {sum(not x['impact'] for x in groups)} driver group(s); "
                f"two-hop: {', '.join(x['label'] for x in groups if x['group'].get('two_hop')) or 'none'}.",
                f"- Display: {d['base_source']} (D-079 re-check of the polished text: "
                f"{'pass' if hr['display_recheck']['pass'] else 'fail --- ' + '; '.join(hr['display_recheck']['reasons'])})"
                + (f"; COORDINATOR edits: {', '.join(e['edit'] for e in d['edits'] if e['applied'])}" if d["display_source"] == EDIT_ORIGIN
                   else "; no COORDINATOR edit applies") + ".", ""]
    return "\n".join(out).rstrip() + "\n"


def display_sources(disp: dict) -> dict:
    return {iid: {"base": d["base_source"], "sheet": d["display_source"]} for iid, d in disp.items()}
