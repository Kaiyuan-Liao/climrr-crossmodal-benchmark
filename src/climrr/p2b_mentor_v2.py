"""Mentor sheet v2 (2026-11-03): provenance correction LS-199098498-04 (D-057), DR-DESC-1 v2 (D-055c), edited answers v2.

**D-057 overlay.** `provenance_corrections_v1.yaml` is applied by `climrr.litstatements.apply_provenance_corrections` to
the statement records, to the members of every group and packet group that holds a corrected statement, and to the
`supports[]` entries of every current item that cites one. Nothing on disk is rewritten: statements, groups, packets and
item files stay byte-identical (their hashes are pinned by manifests and the items index). `applied_record` is what
`scripts/apply_provenance_corrections.py` writes: the corrections with their re-slice status, the corrected statement
record, each affected group's evidence strength recomputed (D-045 / D-048 with DR-LIT-IND-1 v2) over the group file and
over every packet's member subset, and each affected item's `provenance_corrections_applied`. The re-slice is exact, in
the paper's own text, when the paper JSON is on this machine (under a configured corpus root); otherwise
`pending_polaris` with the one-line Polaris command (`litstatements` module docstring).

**DR-DESC-1 v2.** `descriptors_v2` computes v2 descriptors (`descriptor_rules_v2.yaml`) for the mentor items. The seed
packets are not rebuilt: they keep v1 descriptors, which `pattern_descriptors.descriptors` with v1 rules reproduces.

**Mentor sheet v2.** The v2 COORDINATOR texts (`P2b_coordinator_edits_2026-11-03_v2.yaml`, pinned), the EXECUTOR support
map v2 (`P2b_mentor_support_map_v2.yaml`): the paper side may list a packet group the edit cites but the generated item
does not (`added_by_edit`), and the corrected passage replaces the recorded one with a one-line note; the prefix-anchor
continuation note of v1 is gone. The table side names the NCA5 regions a regional contrast does not cover and the v2
descriptor. README = v1 plus one line.

No model call; no item, statement, group, packet, concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from climrr import benchmark_items as bi
from climrr import itemseeds as sd
from climrr import litaggregate as la
from climrr import litindependence as li
from climrr import litstatements as ls
from climrr import litsynth_run2 as s2
from climrr import p2b_mentor_export as mx
from climrr import pattern_descriptors as pd
from climrr import paths
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

EDITS_V2_PATH = mx.REVIEW_DIR / "P2b_coordinator_edits_2026-11-03_v2.yaml"
EDITS_V2_SHA256 = "a1b011d4179c9c57eb3a05911e15b6264a84bde6726c43a9c673faf729c19ebf"  # the work package's section C, verbatim
SUPPORT_MAP_V2_PATH = mx.REVIEW_DIR / "P2b_mentor_support_map_v2.yaml"
GROUPS_ENRICHED_PATH = REPO_ROOT / "artifacts" / "litgroups" / "run2" / "groups_enriched.jsonl"
CORRECTIONS_DIR = REPO_ROOT / "artifacts" / "litstatements" / "corrections"
APPLIED_PATH = CORRECTIONS_DIR / "provenance_corrections_v1_applied.json"
CHECKS_V2_PATH = mx.REVIEW_DIR / "MENTOR_PILOT_ITEMS_2026-11-05_v2_checks.json"
CORPUS_ROOT_KEYS = ("literature_corpus_root", "litcorpus02_root")
POLARIS_COMMAND = ('cd "$LITCOLLECT_ROOT_POLARIS" && PYTHONPATH="$CLIMRR_REPO/src" python -c \'import json; from climrr import '
                   'litstatements as ls; c = ls.load_provenance_corrections()[0]; print(json.dumps(ls.reslice_correction(c, '
                   'open("sources/full_705k_v2_filtered/98/199098498.json", "rb").read())))\'')
CORRECTED_NOTE = "passage corrected by reviewer verification (D-057); the agent's original passage is kept in provenance"
ADDED_NOTE = "in the item's packet; cited by the edited answer, not by the generated item"
README_V2_LINES = mx.README_LINES + [
    ["Papers citing earlier work",
     "Where a mechanism rests on a paper citing earlier work, the answer says so ('one study, citing earlier work…')."]]
MD_INTRO_V2 = ("Five pilot benchmark items. Question and reference answer are COORDINATOR-proposed edits (v2, 2026-11-03), not "
               "yet frozen. Same content as `MENTOR_PILOT_ITEMS_2026-11-05.xlsx` (sheets ITEMS and README).")
ROLE_BY_PASSAGE_TYPE = {"own_finding": "core_candidate", "own_projection": "core_candidate", "review_synthesis": "core_candidate",
                        "cited_finding": "cited_candidate"}


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]


def edits_v2(path: Path = EDITS_V2_PATH) -> dict:
    """{item_id: edit record, with the file's `edit_origin`} in the work package's order (n 1-5)."""
    _check(sha256_file(path) == EDITS_V2_SHA256, f"{Path(path).name} differs from its pinned SHA-256")
    doc = mx.load_yaml(path)
    return {x["item_id"]: {**x, "edit_origin": doc["edit_origin"]} for x in sorted(doc["items"], key=lambda x: x["n"])}


def support_map_v2(path: Path = SUPPORT_MAP_V2_PATH) -> dict:
    return {x["item_id"]: x for x in mx.load_yaml(path)["items"]}


# --- D-057: the overlay --------------------------------------------------------------------------------------------


def local_paper_bytes(rel_path: str) -> tuple[bytes | None, str | None]:
    """(raw bytes, config key) of a corpus paper under a configured corpus root, or (None, None)."""
    try:
        cfg = paths.load_local_paths()
    except Exception:  # no config/local_paths.yaml: nothing local
        return None, None
    for key in CORPUS_ROOT_KEYS:
        root = cfg.get(key)
        if not isinstance(root, str):
            continue
        for cand in (Path(root) / rel_path, Path(root) / Path(rel_path).name):
            if cand.is_file():
                return cand.read_bytes(), key
    return None, None


def local_reslices(corrections: list[dict], statements: dict) -> dict:
    """{statement_id: reslice result}: exact where the paper is local, else pending_polaris."""
    out = {}
    for c in corrections:
        raw, key = local_paper_bytes(statements[c["statement_id"]]["paper_rel_path"])
        if raw is None:
            out[c["statement_id"]] = {"statement_id": c["statement_id"], "reslice": ls.RESLICE_PENDING, "paper_found_locally": False,
                                      "json_path": f"$.{c['corrected_section_key']}", "section_idx": None, "span_start": None,
                                      "span_end": None, "polaris_command": POLARIS_COMMAND}
        else:
            out[c["statement_id"]] = {**ls.reslice_correction(c, raw), "paper_found_locally": True, "corpus_root_key": key}
    return out


def _corrected_roles(members: list[dict], corrections: list[dict], reslices: dict) -> list[dict]:
    """Overlaid members; a corrected member's evidence role follows its corrected passage type (it passed the pre-check)."""
    ids = {c["statement_id"] for c in corrections}
    out = ls.apply_provenance_corrections(members, corrections, reslices)
    for m in out:
        if m.get("statement_id") in ids:
            _check(m["passage_type"] in ROLE_BY_PASSAGE_TYPE, f"{m['statement_id']}: no evidence role for {m['passage_type']}")
            m["evidence_role"] = ROLE_BY_PASSAGE_TYPE[m["passage_type"]]
    return out


def group_strength(members_before: list[dict], corrections: list[dict], reslices: dict, canon: dict) -> dict:
    after = _corrected_roles(members_before, corrections, reslices)
    cc = lambda ms: sorted({canon.get(m["paper_item_id"], m["paper_item_id"]) for m in ms if m["evidence_role"] in la.CORE_OR_CITED})  # noqa: E731
    b, a = li.strength_v2(members_before, canon), li.strength_v2(after, canon)
    return {"strength_before": b, "strength_after": a, "unchanged": a == b,
            "core_cited_papers_before": cc(members_before), "core_cited_papers_after": cc(after),
            "members": [{"statement_id": m["statement_id"], "paper_item_id": m["paper_item_id"], "evidence_role": m["evidence_role"],
                         "passage_type": m["passage_type"], "corrected": "provenance_correction" in m} for m in after]}


def item_with_corrections(it: dict, corrections: list[dict], reslices: dict) -> dict:
    """A copy of item `it` with its corrected supports overlaid and `reference_components.provenance_corrections_applied`."""
    ids = {c["statement_id"] for c in corrections}
    it = copy.deepcopy(it)
    applied = []
    for key in ("literature_mechanisms", "literature_caveats"):
        for s in it["reference_components"].get(key) or []:
            hit = [x["statement_id"] for x in s["supports"] if x.get("statement_id") in ids]
            if hit:
                s["supports"] = ls.apply_provenance_corrections(s["supports"], corrections, reslices)
                applied += hit
    if applied:
        it["reference_components"]["provenance_corrections_applied"] = sorted(set(applied))
    return it


def applied_record(corrections: list[dict], items: list[dict], packets: dict, reslices: dict) -> dict:
    statements = {r["statement_id"]: r for r in _jsonl(mx.STATEMENTS_INGESTED_PATH)}
    canon = li.canonical_map(json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8")))
    ids = {c["statement_id"] for c in corrections}
    groups = [g for g in _jsonl(GROUPS_ENRICHED_PATH) if ids & {m["statement_id"] for m in g["members"]}]
    grp = []
    for g in groups:
        rec = {"group_id": g["group_id"], "label": g["label"], "file": "groups_enriched.jsonl",
               "recorded_strength": g["evidence_strength"], **group_strength(g["members"], corrections, reslices, canon)}
        _check(rec["strength_before"] == g["evidence_strength"], f"{g['group_id']}: recomputed strength differs from the file")
        per_packet = []
        for iid, pk in packets.items():
            for pg in pk["provenance"]["groups"]:
                if pg["group_id"] == g["group_id"]:
                    r = group_strength(pg["members"], corrections, reslices, canon)
                    _check(r["strength_before"] == pg["strength_in_packet"], f"{iid} {pg['group_id']}: packet strength differs")
                    per_packet.append({"item_id": iid, "packet_id": pk["packet_id"], "strength_in_packet": pg["strength_in_packet"],
                                       "n_papers": pg["n_papers"], **{k: r[k] for k in ("strength_after", "unchanged",
                                                                                         "core_cited_papers_after")}})
        rec["per_packet"] = per_packet
        rec["stays_multi_source"] = (rec["strength_after"] == "multi_source_supported"
                                     and all(p["strength_after"] == "multi_source_supported" for p in per_packet
                                             if p["strength_in_packet"] == "multi_source_supported"))
        grp.append(rec)
    its = []
    for it in items:
        o = item_with_corrections(it, corrections, reslices)
        if "provenance_corrections_applied" in o["reference_components"]:
            its.append({"item_id": it["item_id"], "provenance_corrections_applied": o["reference_components"]["provenance_corrections_applied"],
                        "supports_corrected": [{"group_id": s.get("group_id"), "statement_id": x["statement_id"],
                                                "json_path": x["json_path"], "span_start": x["span_start"], "span_end": x["span_end"]}
                                               for key in ("literature_mechanisms", "literature_caveats")
                                               for s in o["reference_components"].get(key) or [] for x in s["supports"]
                                               if "provenance_correction" in x]})
    corrected = ls.apply_provenance_corrections([statements[i] for i in sorted(ids)], corrections, reslices)
    return {"version": "provenance_corrections_v1 applied", "decision": "D-057", "overlay": True, "files_modified": 0,
            "corrections_file": {"path": "data/metadata/benchmark/provenance_corrections_v1.yaml", "sha256": sha256_file(ls.CORRECTIONS_PATH)},
            "reslices": reslices, "corrected_statements": corrected, "groups": grp, "items": its,
            "note": "the pre-check verifies passage existence, not entailment; a reviewer entailment step is part of item review (D-057)"}


# --- DR-DESC-1 v2 ------------------------------------------------------------------------------------------------


def descriptors_v2(items: dict, ids: list[str]) -> dict:
    """{item_id: {v1, v2, changed}} for the first table pattern of each item."""
    r1, r2 = pd.load_rules(), pd.load_rules(pd.RULES_V2_PATH)
    out = {}
    for iid in ids:
        p = items[iid]["reference_components"]["table_patterns"][0]
        d1, d2 = pd.descriptors(p, r1), pd.descriptors(p, r2)
        out[iid] = {"pattern_id": p["pattern_id"], "v1": d1, "v2": d2,
                    "changed": sorted(k for k in set(d1) | set(d2) if k not in ("rule", "rules_sha256") and d1.get(k) != d2.get(k))}
    return out


# --- the mentor sheet v2 -----------------------------------------------------------------------------------------


def uncovered_regions(ranked_ids: list[str]) -> list[str]:
    _check(sha256_file(sd.NCA_MAP_PATH) == sd.NCA_MAP_SHA256, "nca_regions_v1.yaml differs from its pinned SHA-256")
    names = sd.nca_map()["region_name"]
    return [n for rid, n in names.items() if rid not in set(ranked_ids)]


def descriptor_line(d: dict) -> str:
    if d.get("ranking_largest_first") is not None:
        return f"Pattern descriptor (DR-DESC-1 v2): {d['largest']}; {d['smallest']}"
    return f"Pattern descriptor (DR-DESC-1 v2): {d['magnitude_class']}; {d['anchor_pair']}"


def table_side_v2(it: dict, d2: dict) -> str:
    lines = mx.table_side(it).split("\n")
    p = it["reference_components"]["table_patterns"][0]
    if p["geography_type"] == "nca_region":
        ranked = [r["region"] for r in p["computed_value_or_range"]["regions_ordered"]]
        at = next(i for i, ln in enumerate(lines) if ln.startswith("Geography:")) + 1
        miss = uncovered_regions(ranked)
        lines.insert(at, f"Not covered ({len(miss)} of the {len(miss) + len(ranked)} NCA5 regions; no State label in the table): "
                         + "; ".join(miss))
    return "\n".join(lines + [descriptor_line(d2)])


def paper_cells_v2(it: dict, smap: dict, corrections: list[dict], reslices: dict) -> tuple[str, str]:
    """(Paper side, Original passages) from support map v2, checked against the packet, with the D-057 overlay."""
    if smap.get("table_only"):
        _check(not smap["groups"], f"{it['item_id']}: a table-only item lists groups")
        return "none — table-only item (pattern identification)", "none"
    by_c = {c["statement_id"]: c for c in corrections}
    canon = li.canonical_map(json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8")))
    packet = s2.packet_for_item(it)
    groups = {g["group_id"]: g for g in packet["provenance"]["groups"]}
    tagged = it["review"]["history"][0]["reference_answer_tagged"]
    cited = {g for s in tagged["literature_interpretation"] for g in s["group_ids"]}
    ing, raw = mx._statements()
    side, passages = [], []
    for sg in smap["groups"]:
        gid = sg["group_id"]
        _check(gid in groups, f"{it['item_id']}: {gid} is not in the item's packet")
        added = bool(sg.get("added_by_edit"))
        _check((gid in cited) != added, f"{it['item_id']}: {gid} cited {gid in cited}, added_by_edit {added}")
        g = groups[gid]
        strength = group_strength(g["members"], corrections, reslices, canon)
        _check(strength["strength_before"] == g["strength_in_packet"], f"{it['item_id']} {gid}: packet strength differs")
        members = {m["statement_id"]: m for m in g["members"]}
        used = [members[sid] for sid in sg["members"]]
        papers_used = sorted({m["paper_item_id"] for m in used})
        of_them = (f"; the statement{'s' if len(used) > 1 else ''} used come{'s' if len(used) == 1 else ''} from "
                   f"{len(papers_used)} of them") if g["n_papers"] > 1 else ""
        side.append(f"{g['label'] or used[0]['statement']} — {mx.strength_words(strength['strength_after'], g['n_papers'])}{of_them}"
                    + (f" ({ADDED_NOTE})" if added else ""))
        side += [f"  - {m['statement']} (paper {m['paper_item_id']})" for m in used]
        passages.append(f"[{g['label'] or gid}]")
        for m in used:
            rec = raw[ing[m["statement_id"]]["agent_statement_id"]]
            _check(rec["verbatim_passage"] == m["verbatim_passage"] == ing[m["statement_id"]]["verbatim_passage"],
                   f"{m['statement_id']}: verbatim passage differs between statements.jsonl, the ingest and the packet")
            c = by_c.get(m["statement_id"])
            if c:
                _check(rec["verbatim_passage"] == c["original_passage"], f"{m['statement_id']}: recorded passage is not the correction's original")
                passages.append(f"{m['paper_item_id']}, {c['corrected_section_key']}: \"{mx.cut_passage(c['corrected_passage'])}\"")
                passages.append(f"  {CORRECTED_NOTE}")
            else:
                passages.append(f"{m['paper_item_id']}, {rec['proposal']['section_key']}: \"{mx.cut_passage(rec['verbatim_passage'])}\"")
    return "\n".join(side), "\n".join(passages)


def mentor_rows_v2(items: dict, edit_records: dict, smap: dict, corrections: list[dict], reslices: dict, descs: dict) -> list[list]:
    rows = [mx.MENTOR_HEADER]
    for iid, e in edit_records.items():
        it = items[iid]
        paper, passages = paper_cells_v2(it, smap[iid], corrections, reslices)
        rows.append([f"{e['n']}\n{iid}", e["edited_prompt"], e["edited_reference_integrated"], table_side_v2(it, descs[iid]["v2"]),
                     paper, passages])
    return rows


def render_md_v2(rows: list[list]) -> str:
    return mx.render_md(rows, README_V2_LINES, MD_INTRO_V2)


def sheets_v2(rows: list[list]) -> list[tuple]:
    return mx.sheets(rows, README_V2_LINES)


def clause_verdicts(edit_records: dict, smap: dict) -> dict:
    """Every support-map clause is an exact substring of its edited answer; {verdict: [(item_id, clause)]}."""
    out: dict = {}
    for iid, e in edit_records.items():
        for c in smap[iid]["clauses"]:
            _check(c["text"] in e["edited_reference_integrated"], f"{iid}: support-map clause not in the edited answer: {c['text']}")
            out.setdefault(c["verdict"], []).append((iid, c["text"]))
    return out


def edited_texts_check(edit_records: dict, cols: list[str] | None = None) -> list[dict]:
    """Post-checks v2.3 leakage (as `p2b_mentor_export.edited_text_flags`) on every v2 text."""
    cols = cols if cols is not None else bi.column_names()
    return [mx.edited_text_flags(e, cols) for e in edit_records.values()]


def checks_record(edit_records: dict, smap: dict, descs: dict, leakage: list[dict]) -> dict:
    v = clause_verdicts(edit_records, smap)
    return {"version": "mentor sheet v2 checks", "edits_sha256": sha256_file(EDITS_V2_PATH), "support_map_sha256": sha256_file(SUPPORT_MAP_V2_PATH),
            "leakage_check_version": bi.SYNTH_CHECK_VERSION_V23, "leakage": leakage,
            "leakage_hits": [x["item_id"] for x in leakage if x["prompt"] or x["reference_integrated"]],
            "clause_verdicts": {k: len(x) for k, x in sorted(v.items())},
            "not_fully_supported": {k: [{"item_id": i, "clause": t} for i, t in x] for k, x in sorted(v.items())
                                    if k not in ("supported", "guardrail")},
            "conditional_on_reslice": [{"item_id": iid, "clause": c["text"]} for iid in edit_records for c in smap[iid]["clauses"]
                                       if c.get("conditional_on")],
            "descriptors_v2": {iid: {"pattern_id": d["pattern_id"], "changed": d["changed"], **{k: d["v2"].get(k) for k in
                               ("magnitude_class", "anchor_pair", "anchors", "magnitude_note", "largest", "smallest", "negligible_regions")
                               if k in d["v2"]}} for iid, d in descs.items()}}

