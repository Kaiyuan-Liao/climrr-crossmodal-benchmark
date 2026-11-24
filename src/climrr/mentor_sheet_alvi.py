"""Sample sheet for Alvi: the rung-8 hazard -> infrastructure items (work package P5c, part D; D-076). Implemented, not run.

Runs only after the rung-8 synthesis run (and polish) are ingested: `scripts/build_mentor_sheet.py --audience alvi --items
<ingested run dir>`. Reads the rung-8 packets (`synth_packets_infra_v1/`, each checked against its manifest) and the
ingested items (each checked against the run manifest and built from its packet), as the mentor sheet v2 does
(`mentor_sheet_v2b.load_packets` / `load_items`). One row per item, in the packets' selection order. Columns: the six of
the mentor sheet v2 (`#`, `Question`, `Answer` (display text), `Table side`, `Paper side`, `Original passages`; rules
`mentor_sheet_v2b`), plus a seventh, `Asset class (CISA sector)`: the CISA sector name (the lexicon's `cisa_sector`) and the
asset-class phrase the item uses. In `Paper side` an impact group is marked "[impact; general]" or, when it names the
item's state, "[impact; place-specific: <State>]"; a group still awaiting its COORDINATOR disposition is marked
"[impact group not yet reviewed]".

README: the mentor sheet's three lines, then two lines for Alvi: what the item type is, and the question for him.

No model call; no item modified.
"""

from __future__ import annotations

from pathlib import Path

from climrr import mentor_sheet_v2b as ms
from climrr import synthpackets_infra as spi

REVIEW_DIR = ms.REVIEW_DIR
SHEET_ID = "P5"
MD_PATH = REVIEW_DIR / f"ALVI_SAMPLE_ITEMS_{SHEET_ID}.md"
XLSX_PATH = REVIEW_DIR / f"ALVI_SAMPLE_ITEMS_{SHEET_ID}.xlsx"
HEADER = ms.HEADER + ["Asset class (CISA sector)"]
WIDTHS = ms.WIDTHS + [32]
README_ALVI = [
    ["What this item type is",
     "Each item pairs a projected hazard change at one place (from the ClimRR table) with what research shows such conditions "
     "do to one kind of infrastructure asset (a CISA sector). The impact statements are general findings about that asset "
     "class unless 'Paper side' marks them place-specific; no item says that a particular asset at the place will fail."],
    ["Our question for you",
     "Are these the kind of hazard -> infrastructure questions and answers scientists want? Which asset classes and which "
     "impact types matter most to you?"],
]
README_LINES = ms.README_LINES + README_ALVI


def order(packets_manifest: dict) -> list[str]:
    return [p["item_id"] for p in packets_manifest["packets"]]


def impact_marks(packet: dict) -> dict:
    """{group label or first statement: marker} for the packet's impact groups."""
    out = {}
    for g in packet["provenance"]["groups"]:
        if g["role"] != "impact":
            continue
        label = g["label"] or g["members"][0]["statement"]
        mark = (f"[impact; place-specific: {packet['state']}]" if g["relevance"] == "place_named" else "[impact; general]")
        if g.get("review_state") == spi.REVIEW_STATE:
            mark += " [impact group not yet reviewed]"
        out[label] = mark
    return out


def paper_cells(item: dict, packet: dict) -> tuple[str, str]:
    side, passages = ms.paper_cells(item, packet)
    marks = impact_marks(packet)
    lines = []
    for ln in side.split("\n"):
        label = ln.split(": ", 1)[1] if ": " in ln else ln
        lines.append(f"{ln} {marks[label]}" if label in marks else ln)
    return "\n".join(lines), passages


def asset_cell(packet: dict) -> str:
    mv = packet["model_view"]
    return f"{mv['cisa_sector']} (in the item: \"{mv['asset_class_phrase']}\")"


def rows(packets_manifest: dict, packets: dict, items: dict) -> list[list]:
    ids = order(packets_manifest)
    ms._check(sorted(items) == sorted(ids), f"items {sorted(items)} are not the packets' items {sorted(ids)}")
    out = [HEADER]
    for n, iid in enumerate(ids, 1):
        it, pk = items[iid], packets[iid]
        text = ms.display(it)
        ms._check([w["id"] for w in it["review"]["history"][0]["working_assumptions_relied_on"]]
                  == [w["id"] for w in pk["working_assumptions_relied_on"]], f"{iid}: working assumptions differ from the packet")
        side, passages = paper_cells(it, pk)
        out.append([f"{n}\n{iid}", text["prompt"], text["answer"], ms.table_side(pk), side, passages, asset_cell(pk)])
    return out


def render_md(rs: list[list]) -> str:
    out = [f"# Sample hazard -> infrastructure items for Alvi --- {SHEET_ID}", "",
           f"{len(rs) - 1} sample items. Same content as `{XLSX_PATH.name}` (sheets ITEMS and README).", "", "## README", ""]
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


def build(packets_dir: Path, items_dir: Path) -> tuple[dict, list[list]]:
    man, packets = ms.load_packets(packets_dir)
    items = ms.load_items(items_dir, man)
    return man, rows(man, packets, items)
