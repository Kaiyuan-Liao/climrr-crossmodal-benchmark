"""Mentor sheet v3 (2026-11-03, final for 2026-11-05): D-057 closed with the recorded re-slice, a corrected statement, a
reviewer group label (D-058), COORDINATOR texts v3.

**Corrections v1a.** `provenance_corrections_v1a.yaml` (pinned; v1 kept) adds to v1 the Polaris re-slice Kaiyuan ran
(exact, one occurrence, `original_reslices: true`, `paper_sha256_match: true`), a `corrected_statement` that replaces the
agent's paraphrase of LS-199098498-04, and `group_label_overrides` (driver-c1-008 gets a reviewer label; the agent's label
kept). `reslices_v1a` takes the recorded re-slice, and checks it against an exact local re-slice when the paper JSON is on
this machine. `applied_record_v1a` is the v2 overlay record built from v1a, plus the label overrides and, for each overlay,
where it is applied and where the original stays unchanged (`uses`). Nothing on disk is rewritten.

**Mentor sheet v3.** The v3 texts (`P2b_coordinator_edits_2026-11-03_v3.yaml`, pinned) and the EXECUTOR support map v3; the
paper side shows the reviewer label with "(agent label: ...)" in small text after it (`<small>` in the Markdown, a small
run in the xlsx) and the corrected statement, marked; the passages and the README are v2's.

No model call; no item, statement, group, packet, concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import re

from climrr import litstatements as ls
from climrr import p2b_mentor_export as mx
from climrr import p2b_mentor_v2 as m2
from climrr.checksums import sha256_file
from climrr.paths import repo_relative
from climrr.xlsxlite import Rich

EDITS_V3_PATH = mx.REVIEW_DIR / "P2b_coordinator_edits_2026-11-03_v3.yaml"
EDITS_V3_SHA256 = "dba28d141d0c0e1d6e8007ddf54c4f88ecad562759d7316ad12a8d55fc3d943d"  # v2 + the work package's section B
SUPPORT_MAP_V3_PATH = mx.REVIEW_DIR / "P2b_mentor_support_map_v3.yaml"
APPLIED_V1A_PATH = m2.CORRECTIONS_DIR / "provenance_corrections_v1a_applied.json"
CHECKS_V3_PATH = mx.REVIEW_DIR / "MENTOR_PILOT_ITEMS_2026-11-05_v3_checks.json"
MD_INTRO_V3 = ("Five pilot benchmark items. Question and reference answer are COORDINATOR-proposed edits (v3, 2026-11-03), not "
               "yet frozen. Same content as `MENTOR_PILOT_ITEMS_2026-11-05.xlsx` (sheets ITEMS and README).")
SMALL = re.compile(r"<small>(.*?)</small>")


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def edits_v3(path=EDITS_V3_PATH) -> dict:
    """{item_id: edit record, with the file's `edit_origin`} in the work package's order (n 1-5)."""
    _check(sha256_file(path) == EDITS_V3_SHA256, f"{path.name} differs from its pinned SHA-256")
    doc = mx.load_yaml(path)
    return {x["item_id"]: {**x, "edit_origin": doc["edit_origin"]} for x in sorted(doc["items"], key=lambda x: x["n"])}


def support_map_v3(path=SUPPORT_MAP_V3_PATH) -> dict:
    return {x["item_id"]: x for x in mx.load_yaml(path)["items"]}


def corrections_v1a() -> tuple[list[dict], list[dict]]:
    """(corrections, group label overrides) of v1a; each correction is v1's record plus the v1a fields."""
    doc = ls.load_corrections_doc(ls.CORRECTIONS_V1A_PATH)
    v1 = {c["statement_id"]: c for c in ls.load_provenance_corrections()}
    for c in doc["corrections"]:
        _check(all(c.get(k) == v for k, v in v1[c["statement_id"]].items()), f"{c['statement_id']}: v1a changes a v1 field")
    return doc["corrections"], doc.get("group_label_overrides") or []


# --- the re-slice -------------------------------------------------------------------------------------------------


def reslices_v1a(corrections: list[dict], statements: dict) -> dict:
    """{statement_id: the recorded re-slice}; checked for consistency with the passage, and against an exact local
    re-slice when the paper JSON is on this machine."""
    out = {}
    for c in corrections:
        rec = ls.recorded_reslice(c)
        _check(rec is not None, f"{c['statement_id']}: no recorded re-slice")
        _check(rec["reslice"] == "exact" and rec["occurrences"] == 1 and rec["paper_sha256_match"] and rec["original_reslices"],
               f"{c['statement_id']}: the recorded re-slice is not exact, unique and on the recorded paper")
        _check(rec["span_end"] - rec["span_start"] == len(c["corrected_passage"]), f"{c['statement_id']}: span length != passage length")
        _check(rec["json_path"] == f"$.{c['corrected_section_key']}" and rec["section_idx"] == c["original_evidence"]["section_idx"],
               f"{c['statement_id']}: the recorded location is not the corrected section")
        raw, key = m2.local_paper_bytes(statements[c["statement_id"]]["paper_rel_path"])
        if raw is None:
            out[c["statement_id"]] = {**rec, "paper_found_locally": False}
        else:
            local = ls.reslice_correction(c, raw)
            _check(all(local[k] == rec[k] for k in ls.RESLICE_FIELDS), f"{c['statement_id']}: the local re-slice differs from the record")
            out[c["statement_id"]] = {**rec, "paper_found_locally": True, "corpus_root_key": key, "local_reslice_agrees": True}
    return out


# --- the overlay record ------------------------------------------------------------------------------------------


def _group_cited(it: dict, gid: str) -> bool:
    tagged = it["review"]["history"][0]["reference_answer_tagged"]
    return any(gid in s["group_ids"] for s in tagged["literature_interpretation"])


def overlay_uses(corrections: list[dict], overrides: list[dict], items: list[dict], packets: dict, smap: dict) -> dict:
    """Where each overlay is applied, and where the original stays unchanged on disk."""
    groups = m2._jsonl(m2.GROUPS_ENRICHED_PATH)
    rel = lambda p: repo_relative(p)  # noqa: E731
    out = {"corrections": [], "group_label_overrides": []}
    for c in corrections:
        sid = c["statement_id"]
        in_groups = [g["group_id"] for g in groups if sid in {m["statement_id"] for m in g["members"]}]
        in_packets = sorted(iid for iid, pk in packets.items() for pg in pk["provenance"]["groups"]
                            if sid in {m["statement_id"] for m in pg["members"]})
        in_items = sorted({it["item_id"] for it in items for key in ("literature_mechanisms", "literature_caveats")
                           for s in it["reference_components"].get(key) or [] for x in s["supports"] if x.get("statement_id") == sid})
        mentor = [iid for iid, x in smap.items() for g in x["groups"] if sid in g["members"]]
        out["corrections"].append({
            "statement_id": sid,
            "applied_in": {"overlay_record": ["corrected_statements", "groups[].members (strength recomputed)", "items[].supports_corrected"],
                           "mentor_sheet_paper_side": {"items": mentor, "replaces": "the member statement (agent paraphrase)",
                                                       "marked": m2.STATEMENT_NOTE.strip()},
                           "mentor_sheet_original_passages": {"items": mentor, "replaces": "the verbatim passage", "marked": m2.CORRECTED_NOTE}},
            "original_unchanged_in": {rel(mx.STATEMENTS_PATH): [sid], rel(mx.STATEMENTS_INGESTED_PATH): [sid],
                                      rel(m2.GROUPS_ENRICHED_PATH): in_groups, "packets (by item)": in_packets, "item files": in_items}})
    for o in overrides:
        gid = o["group_id"]
        in_packets = sorted(iid for iid, pk in packets.items() if gid in {g["group_id"] for g in pk["provenance"]["groups"]})
        out["group_label_overrides"].append({
            "group_id": gid,
            "applied_in": {"mentor_sheet_paper_side": {"items": [iid for iid, x in smap.items() if gid in {g["group_id"] for g in x["groups"]}],
                                                       "shown": "reviewer label, then '(agent label: ...)' in small text"}},
            "not_applied_in": {"mentor_sheet_original_passages": "the group heading keeps the agent label (passages unchanged)",
                               "review workbook": "GROUPS_CITED keeps the agent label; the override is named on OVERVIEW"},
            "original_unchanged_in": {rel(m2.GROUPS_ENRICHED_PATH): [gid], "packets (by item)": in_packets,
                                      "items citing the group (generated)": sorted(it["item_id"] for it in items if _group_cited(it, gid))}})
    return out


def applied_record_v1a(corrections: list[dict], overrides: list[dict], items: list[dict], packets: dict, reslices: dict,
                       smap: dict) -> dict:
    rec = m2.applied_record(corrections, items, packets, reslices)
    statements = {r["statement_id"]: r for r in m2._jsonl(mx.STATEMENTS_INGESTED_PATH)}
    groups = {g["group_id"]: g for g in m2._jsonl(m2.GROUPS_ENRICHED_PATH)}
    _check(all(o["group_id"] in groups for o in overrides), "a label override names a group not in the groups file")
    rec.update(
        version="provenance_corrections_v1a applied", decisions=["D-057", "D-058"],
        corrections_file={"path": repo_relative(ls.CORRECTIONS_V1A_PATH), "sha256": sha256_file(ls.CORRECTIONS_V1A_PATH)},
        corrected_statements=ls.apply_provenance_corrections([statements[c["statement_id"]] for c in corrections], corrections,
                                                             reslices, ls.CORRECTIONS_V1A_PATH.name),
        group_label_overrides=[{**o, "group_label_after": g["label"], "label_override": g["label_override"]}
                               for o in overrides for g in ls.apply_group_label_overrides([groups[o["group_id"]]], [o])],
        uses=overlay_uses(corrections, overrides, items, packets, smap))
    return rec


# --- the mentor sheet v3 -----------------------------------------------------------------------------------------


def mentor_rows_v3(items: dict, edit_records: dict, smap: dict, corrections: list[dict], overrides: list[dict], reslices: dict,
                   descs: dict) -> list[list]:
    rows = [mx.MENTOR_HEADER]
    for iid, e in edit_records.items():
        it = items[iid]
        paper, passages = m2.paper_cells_v2(it, smap[iid], corrections, reslices, overrides)
        rows.append([f"{e['n']}\n{iid}", e["edited_prompt"], e["edited_reference_integrated"], m2.table_side_v2(it, descs[iid]["v2"]),
                     paper, passages])
    return rows


def render_md_v3(rows: list[list]) -> str:
    return mx.render_md(rows, m2.README_V2_LINES, MD_INTRO_V3)


def rich(cell):
    """A cell with `<small>...</small>` markup as an xlsx rich-text cell; any other cell unchanged."""
    if not isinstance(cell, str) or "<small>" not in cell:
        return cell
    runs, at = [], 0
    for m in SMALL.finditer(cell):
        runs += [(cell[at:m.start()], False), (m.group(1), True)]
        at = m.end()
    return Rich([r for r in runs + [(cell[at:], False)] if r[0]])


def sheets_v3(rows: list[list]) -> list[tuple]:
    return m2.sheets_v2([[rich(c) for c in r] for r in rows])


def checks_record_v3(edit_records: dict, smap: dict, descs: dict, leakage: list[dict]) -> dict:
    rec = m2.checks_record(edit_records, smap, descs, leakage)
    v2 = {(iid, c["text"]): c["verdict"] for iid, x in m2.support_map_v2().items() for c in x["clauses"]}
    v3 = {(iid, c["text"]): c["verdict"] for iid, x in smap.items() for c in x["clauses"]}
    rec.update(version="mentor sheet v3 checks", edits_sha256=sha256_file(EDITS_V3_PATH), support_map_sha256=sha256_file(SUPPORT_MAP_V3_PATH),
               clauses_changed_since_v2={"removed": [{"item_id": i, "clause": t, "verdict_v2": v} for (i, t), v in v2.items() if (i, t) not in v3],
                                         "added": [{"item_id": i, "clause": t, "verdict_v3": v} for (i, t), v in v3.items() if (i, t) not in v2]})
    return rec
