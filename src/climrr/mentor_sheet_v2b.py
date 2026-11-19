"""Mentor sample sheet v2 as sent 2026-11-19 (work package P3c, section B; D-068): the seven run-5 sample items.

Replaces the P3a draft rules (`mentor_sheet_v2.py`, packets v4, never sent; kept with its tests). Reads packets v4b and
the ingested run-5 items (`artifacts/benchmark/items/run5/items/<item_id>.json`, each checked against the run-5 manifest
and built from its v4b packet). One row per item, in the work package's order (`ORDER`). Columns, exactly:

- `#` --- the position and the item id;
- `Question`, `Answer` --- the **display text**: the polished prompt / answer where the polish status is `polished`, else
  the original (checked against the polish event; `litsynth_run5.display_text`);
- `Table side` --- plain words: the quantity as the data dictionary names it (with the columns), the place, the season, the
  baseline and future windows as the dictionary names them (lines 101-102), the scenario, the statistic, the computed values
  with one decimal (half up, as the packets), the grid cells, the rank or the regional ranking, the pattern descriptor
  (DR-DESC-1 v4), and the line "working assumptions relied on: ..." naming the WA ids;
- `Paper side` --- per literature group the item cites: "Research shows (N papers)" or "Research suggests (1 paper)" by the
  group's strength (D-062; N = the group's independent papers) and the group label;
- `Original passages` --- per cited group, every member passage verbatim (no cut), with paper id and section.

README of three lines (`README_LINES`). The Markdown copy has the same content. No model call; no item modified.
"""

from __future__ import annotations

import json
from pathlib import Path

from climrr import litsynth_run5 as s5
from climrr import p2b_mentor_export as mx
from climrr import p2b_mentor_v2 as m2
from climrr import synthpackets as spk
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

REVIEW_DIR = REPO_ROOT / "artifacts" / "benchmark" / "review"
SHEET_DATE = "2026-11-19"
MD_PATH = REVIEW_DIR / f"MENTOR_SAMPLE_ITEMS_{SHEET_DATE}.md"
XLSX_PATH = REVIEW_DIR / f"MENTOR_SAMPLE_ITEMS_{SHEET_DATE}.xlsx"
HEADER = ["#", "Question", "Answer", "Table side", "Paper side", "Original passages"]
WIDTHS = [12, 45, 60, 60, 50, 80]
ORDER = [("BI-P3-0001", "California heat"), ("BI-P3-0004", "Alabama heat"), ("BI-P3-0003", "Washington heat"),
         ("BI-P3-0002", "New York heat"), ("BI-P3-0005", "regions heat"), ("BI-P3-0007", "California fire weather"),
         ("BI-P3-0008", "Minnesota fire weather")]
HEDGE = {"multi_source_supported": "Research shows", "review_supported": "Research shows",
         "single_source_supported": "Research suggests"}
README_LINES = [
    ["The question is all the model sees",
     "The model under test gets only the Question: no table, no paper, no data."],
    ["Grading is at pattern level",
     "Direction of the change, rough size, comparison with other states, and drivers. The values in 'Table side' are where "
     "the answer comes from; the model is not expected to give them."],
    ["'Research suggests'",
     "Marks a driver found in one paper of our literature corpus ('research shows': two or more papers)."],
]


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def load_packets(packets_dir: Path) -> tuple[dict, dict]:
    """(packet manifest, {item_id: packet}), every packet checked against the manifest's SHA-256."""
    man = json.loads((Path(packets_dir) / "manifest.json").read_text(encoding="utf-8"))
    out = {}
    for p in man["packets"]:
        f = Path(packets_dir) / f"{p['packet_id']}.json"
        _check(sha256_file(f) == p["sha256"], f"{f.name} differs from the packet manifest")
        out[p["item_id"]] = json.loads(f.read_text(encoding="utf-8"))
    return man, out


def load_items(run_dir: Path, packets_manifest: dict) -> dict:
    """{item_id: item} from the ingested run (`manifest.json` items_ingested, each hash checked), each built from the
    packet the packet manifest names."""
    man = json.loads((Path(run_dir) / "manifest.json").read_text(encoding="utf-8"))
    sha = {p["item_id"]: p["sha256"] for p in packets_manifest["packets"]}
    out = {}
    for x in man["items_ingested"]:
        f = Path(run_dir) / x["path"]
        _check(sha256_file(f) == x["sha256"], f"{x['path']} differs from the run manifest")
        it = json.loads(f.read_text(encoding="utf-8"))
        _check(it["generation"]["inputs_sha256"]["packet"] == sha[it["item_id"]], f"{it['item_id']}: built from another packet")
        out[it["item_id"]] = it
    return out


def _f1(v) -> str:
    return spk.show(v)


def _signed(v) -> str:
    s = spk.show(v)
    return s if s.startswith("-") else "+" + s


def _quantity(p: dict) -> str:
    """The dictionary's description of the future column, without the period (the quote's own case and dash kept)."""
    srcs, cols = p["provenance"]["column_sources"], [c["column"] for c in p["provenance"]["columns"]]
    fut = next(c for c in cols if "_HIS_" not in c and not c.lower().endswith("_hist"))
    q = srcs[fut]["quote"]
    head = q.split(" ", 1)
    _check(head[0].lower() == fut.lower(), f"{fut}: dictionary quote does not start with the column name")
    desc = head[1].replace(" – ", " -- ").split(" -- ")[0].strip()
    lines = [f"{desc} (data dictionary line {srcs[fut]['line']}; columns {', '.join(cols)})"]
    if p["family"] == "fire_weather_index":
        lines[0] = (f"{desc}, under the dictionary's Wildfire columns (line {srcs[fut]['line']}; columns {', '.join(cols)}), "
                    f"read as the summer {p['metric_wording'].replace('seasonal value of the ', '')}: a fire-danger index, "
                    "not fire occurrence")
    return lines[0]


def table_side(packet: dict) -> str:
    p = packet["provenance"]["patterns"][0]
    d = packet["model_view"]["patterns"][0]["allowed_descriptors"]
    per, cv = mx.period_names(), p["computed_value_or_range"]
    fwi = p["family"] == "fire_weather_index"
    lines = [f"Quantity: {_quantity(p)}"]
    if p["geography_type"] == "nca_region":
        ranked = cv["regions_ordered"]
        miss = m2.uncovered_regions([r["region"] for r in ranked])
        lines.append(f"Place: the NCA5 climate regions with a State label in the table ({len(ranked)} of {len(ranked) + len(miss)}; "
                     f"not covered: {'; '.join(miss)})")
    else:
        lines.append(f"Place: {p['geography']} (State label in the table)")
    lines += [f"Season: {p['season']}", f"Baseline window: {per['historical']}", f"Future window: {per[p['horizon']]}",
              f"Scenario: {p['scenario']}"]
    _check(p["statistic"] == "absolute_change", f"{p['pattern_id']}: statistic {p['statistic']}")
    what = "the seasonal value" if fwi else "the number of days"
    if p["geography_type"] == "nca_region":
        regs = mx.region_patterns(p["provenance"]["region_pattern_ids"])
        by_region = {r["geography"]: r for r in regs.values()}
        lines.append(f"Statistic: change in {what} (future minus baseline), unweighted mean over the grid cells of each region; "
                     "regions ranked largest first")
        lines.append("Values (mean days, baseline -> future, change):")
        n = 0
        for r in ranked:
            rp = by_region[r["region"]]["computed_value_or_range"]
            _check(_f1(rp["value"]) == _f1(r["value"]), f"{r['region']}: region pattern value differs from the ranking")
            n += rp["n_cells_used"]
            lines.append(f"  {r['rank']}. {r['name']}: {_f1(rp['mean_from'])} -> {_f1(rp['mean_to'])} ({_signed(r['value'])}); "
                         f"{rp['n_cells_used']:,} grid cells")
        lines.append(f"Grid cells: {n:,} over the {len(ranked)} regions")
        lines.append(f"Pattern descriptor (DR-DESC-1 v4): {d['largest']}; {d['smallest']}")
    else:
        unit = "" if fwi else " days"
        lines.append(f"Statistic: change in {what} (future minus baseline), unweighted mean over grid cells")
        lines.append(f"Values: mean {_f1(cv['mean_from'])}{unit} -> {_f1(cv['mean_to'])}{unit} ({_signed(cv['value'])}{unit})"
                     + (" (index value, no unit)" if fwi else ""))
        if p.get("rank"):
            lines.append(f"Rank among State labels: {p['rank']['rank']} of {p['rank']['of']} (largest change first)")
        cells = cv.get("cell_direction_counts")
        lines.append(f"Grid cells: {cv['n_cells_used']:,}" + (f" (increasing: {cells['increase']:,}; decreasing: {cells['decrease']:,})"
                                                               if cells else ""))
        desc = [d["magnitude_class"], d["tercile_forms"][0] if d.get("tercile_forms") else None, d.get("anchor_pair")]
        lines.append("Pattern descriptor (DR-DESC-1 v4): " + "; ".join(x for x in desc if x))
    wa = packet.get("working_assumptions_relied_on") or []
    _check(bool(wa), f"{packet['item_id']}: no working assumption recorded")
    lines.append("working assumptions relied on: " + ", ".join(f"{w['id']} ({w['resolution']})" for w in wa)
                 + " --- owner-authorized (D-064), not confirmed")
    return "\n".join(lines)


def _section(json_path: str) -> str:
    _check(json_path.startswith("$."), f"json_path {json_path}")
    return json_path[2:].replace("_", " ")


def cited_groups(item: dict) -> list[str]:
    """The literature group ids the item's tagged answer cites, in order of first citation; = the reference components'."""
    tagged = item["review"]["history"][0]["reference_answer_tagged"]
    out = []
    for s in tagged["literature_interpretation"]:
        out += [g for g in s["group_ids"] if g not in out]
    rc = item["reference_components"]
    _check(sorted(out) == sorted(s["group_id"] for s in rc["literature_mechanisms"] + rc["literature_caveats"]),
           f"{item['item_id']}: tagged groups differ from the reference components")
    return out


def paper_cells(item: dict, packet: dict) -> tuple[str, str]:
    groups = {g["group_id"]: g for g in packet["provenance"]["groups"]}
    rc = item["reference_components"]
    stmts = {s["group_id"]: s for s in rc["literature_mechanisms"] + rc["literature_caveats"]}
    side, passages = [], []
    for gid in cited_groups(item):
        g, s = groups[gid], stmts[gid]
        _check(s["evidence_strength"] == g["strength_in_packet"], f"{gid}: strength differs between item and packet")
        n = g["n_papers"]
        _check((n == 1) == (g["strength_in_packet"] == "single_source_supported") or g["strength_in_packet"] == "review_supported",
               f"{gid}: {n} papers but {g['strength_in_packet']}")
        label = g["label"] or s["statement"]
        note = " (a review among them)" if g["strength_in_packet"] == "review_supported" else ""
        unrev = " [claim tag not yet human-reviewed]" if g.get("review_state") == "unreviewed_agent_tag" else ""
        side.append(f"{HEDGE[g['strength_in_packet']]} ({n} paper{'s' if n != 1 else ''}){note}: {label}{unrev}")
        passages.append(f"[{label}]")
        for m in g["members"]:
            sup = next((x for x in s["supports"] if x["statement_id"] == m["statement_id"]), None)
            _check(sup is None or sup["verbatim_passage"] == m["verbatim_passage"], f"{m['statement_id']}: passage differs from the item")
            passages.append(f"  paper {m['paper_item_id']}, {_section(m['json_path'])}: \"{m['verbatim_passage']}\"")
    return "\n".join(side), "\n".join(passages)


def rows(packets: dict, items: dict) -> list[list]:
    _check(sorted(items) == sorted(i for i, _ in ORDER), f"items {sorted(items)} are not the seven sample items")
    out = [HEADER]
    for n, (iid, _) in enumerate(ORDER, 1):
        it, pk = items[iid], packets[iid]
        text = s5.display_text(it)
        _check([w["id"] for w in it["review"]["history"][0]["working_assumptions_relied_on"]]
               == [w["id"] for w in pk["working_assumptions_relied_on"]], f"{iid}: working assumptions differ from the packet")
        side, passages = paper_cells(it, pk)
        out.append([f"{n}\n{iid}", text["prompt"], text["answer"], table_side(pk), side, passages])
    return out


def render_md(rs: list[list]) -> str:
    out = [f"# Sample items for mentor review --- {SHEET_DATE}", "",
           f"Seven sample items (five heat index, two fire weather). Same content as `MENTOR_SAMPLE_ITEMS_{SHEET_DATE}.xlsx` "
           "(sheets ITEMS and README).", "", "## README", ""]
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


def display_sources(items: dict) -> dict:
    return {iid: s5.display_source(items[iid]) for iid, _ in ORDER}

