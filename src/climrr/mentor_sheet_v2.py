"""Mentor sample sheet v2 (work package P3a, section E; D-059 -- D-065): the polished sample items for the mentor.

One row per seed packet v4 (`artifacts/benchmark/synth_packets_v4/manifest.json`, in order) whose item exists: the item
from the polish run when present (`litpolish_agent` v1 output), else from the synthesis run (`litsynth_agent` v4 output).
Columns:

- `#` --- the order and the item id;
- `Question`, `Answer` --- the item's prompt and integrated reference answer (polished when the polish passed its
  invariance checks; the pre-polish text follows in the Markdown, in small type, so the review sees both, D-063);
- `Table side` --- the pattern in plain words (DR-DESC-1 v3) and then the exact values the graded text omits: threshold,
  scenario, window, baseline and future means or the regional ranking, the table columns, and the working assumptions
  relied on (D-064);
- `Paper side` --- per literature group the item cites: "research shows" / "research suggests" (D-062), the label, the
  number of independent papers and the strength; a fire-arm group whose claim tag was never human-reviewed says so;
- `Original passages` --- the verbatim passages behind each cited group (cut at a sentence end after 700 characters).

`README_LINES` holds the three framing lines. The same content is written as Markdown. No model call; no item modified.
"""

from __future__ import annotations

import json
from pathlib import Path

from climrr import p2b_mentor_export as mx
from climrr import synthpackets as spk
from climrr.paths import REPO_ROOT

REVIEW_DIR = REPO_ROOT / "artifacts" / "benchmark" / "review"
MD_PATH = REVIEW_DIR / "MENTOR_SAMPLE_SHEET_v2.md"
XLSX_PATH = REVIEW_DIR / "MENTOR_SAMPLE_SHEET_v2.xlsx"
HEADER = ["#", "Question", "Answer", "Table side", "Paper side", "Original passages"]
WIDTHS = [12, 45, 60, 50, 50, 70]
HEDGE = {"multi_source_supported": "Research shows", "review_supported": "Research shows",
         "single_source_supported": "Research suggests"}
README_LINES = [
    ["The question is closed-book",
     "The model under test gets only the Question: no table, no paper, no data. It answers from what it knows about "
     "projected climate hazards and their physical drivers."],
    ["Grading is at the pattern level",
     "Direction of the change, rough size, place (or ranking), and the mechanisms named. The exact values, threshold, "
     "scenario and years in 'Table side' are provenance for the answer; the model is not expected to give them."],
    ["What 'research suggests' means",
     "The finding rests on one independent paper in our literature corpus. 'Research shows' means two or more independent "
     "papers or a review. A grader requires only the 'research shows' mechanisms; a 'research suggests' one is optional."],
]


def load_items(packets_manifest: dict, synth_dir: Path, polish_dir: Path | None = None) -> dict:
    """{item_id: (item, source)} --- `source` is `polish` or `synthesis`; packets with no item are left out."""
    out = {}
    for p in packets_manifest["packets"]:
        sid = p["seed_id"]
        for src, d in (("polish", polish_dir), ("synthesis", synth_dir)):
            f = Path(d) / "items" / f"{sid}.json" if d else None
            if f is not None and f.is_file():
                out[p["item_id"]] = (json.loads(f.read_text(encoding="utf-8")), src)
                break
    return out


def polish_event(item: dict) -> dict | None:
    return next((h for h in reversed(item["review"]["history"]) if h.get("event") == "polish"), None)


def _columns(p: dict) -> str:
    return ", ".join(f"{c['column']} ({c['index']})" for c in p["provenance"]["columns"])


def table_side(packet: dict) -> str:
    p = packet["provenance"]["patterns"][0]
    d = packet["model_view"]["patterns"][0]["allowed_descriptors"]
    ex = packet["provenance"]["exact"]
    v = p["computed_value_or_range"]
    place = "the NCA5 climate regions" if p["pattern_kind"] == "regional_contrast" else p["geography"]
    lines = [f"Plain words: {d['quantity']}, {place}, {d['horizon']} {d['scenario']}: {d['direction']}"
             + (f", {d['magnitude_class']}" if d.get("magnitude_class") else "")
             + (f"; {d['largest']}; {d['smallest']}" if d.get("largest") else "") + "."]
    if d.get("tercile"):
        lines.append(f"Relative size: {d['tercile'].split(' (')[0]} (a relative descriptor among states).")
    exact = [f"metric: {ex['metric_wording']}" + (f" (threshold {ex['threshold_F']} °F)" if ex["threshold_F"] else ""),
             f"scenario: {ex['scenario_effective']}" + (" (assumed; R-007)" if ex["scenario"] != ex["scenario_effective"] else ""),
             f"window: {ex['horizon_window']} vs the modeled historical baseline (model output, not an observation)"]
    if p["pattern_kind"] == "regional_contrast":
        exact.append("change by region, largest first: " + "; ".join(
            f"{r['name']} {spk.show(r['value'])}" if r.get("value") is not None else f"{r['name']} (not ranked)"
            for r in v["regions_ordered"]))
    else:
        unit = " days" if p["family"] == "heat_index" else ""
        if v.get("mean_from") is not None:
            exact.append(f"mean {spk.show(v['mean_from'])}{unit} (baseline) -> {spk.show(v['mean_to'])}{unit}; change "
                         f"{'+' if float(v['value']) > 0 else ''}{spk.show(v['value'])}{unit} (unweighted mean over grid cells)")
    lines.append("Exact (provenance, not graded): " + "; ".join(exact) + ".")
    lines.append(f"Columns: {_columns(p)}.")
    wa = packet.get("working_assumptions_relied_on") or []
    if wa:
        lines.append("Working assumptions relied on (owner-authorized, D-064; not confirmed): "
                     + ", ".join(f"{w['id']} ({w['resolution']})" for w in wa) + ".")
    return "\n".join(lines)


def paper_cells(item: dict, packet: dict) -> tuple[str, str]:
    rc = item["reference_components"]
    stmts = rc["literature_mechanisms"] + rc["literature_caveats"]
    if not stmts:
        return "none", "none"
    groups = {g["group_id"]: g for g in packet["provenance"]["groups"]}
    side, passages = [], []
    for s in stmts:
        g = groups[s["group_id"]]
        n = len({sup["paper_sha256"] for sup in s["supports"]})
        note = " [fire-arm claim tag not yet human-reviewed]" if g.get("review_state") == "unreviewed_agent_tag" else ""
        side.append(f"{HEDGE[s['evidence_strength']]}: {s['statement']} --- {n} independent paper{'s' if n != 1 else ''}, "
                    f"{s['evidence_strength'].replace('_', ' ')}{note}")
        passages.append(f"[{s['statement']}]")
        passages += [f"  {sup['paper_item_id']}: \"{mx.cut_passage(sup['verbatim_passage'])}\"" for sup in s["supports"]]
    return "\n".join(side), "\n".join(passages)


def rows(packets_manifest: dict, packets: dict, items: dict) -> list[list]:
    out = [HEADER]
    for n, p in enumerate(packets_manifest["packets"], 1):
        if p["item_id"] not in items:
            continue
        it, _ = items[p["item_id"]]
        pk = packets[p["item_id"]]
        side, passages = paper_cells(it, pk)
        out.append([f"{n}\n{p['item_id']}", it["prompt"], it["reference_answer"]["integrated"], table_side(pk), side, passages])
    return out


def render_md(rs: list[list], items: dict, title: str = "Sample items for mentor review --- v2") -> str:
    out = [f"# {title}", "", "Polished sample items (question and answer in general words; D-060 -- D-063). Same content as "
           "`MENTOR_SAMPLE_SHEET_v2.xlsx` (sheets ITEMS and README).", "", "## README", ""]
    out += [f"- **{k}.** {v}" for k, v in README_LINES]
    for r in rs[1:]:
        n, iid = r[0].split("\n")
        it, src = items[iid]
        ev = polish_event(it)
        out += ["", f"## {n} · {iid}", ""]
        for h, v in zip(rs[0][1:], r[1:]):
            out += [f"### {h}", ""]
            if h in ("Table side", "Paper side", "Original passages"):
                out += [f"    - {ln.strip()}" if ln.startswith("  ") else f"- {ln}" for ln in v.split("\n")]
            else:
                out.append(v)
                if ev and ev["status"] == "polished":
                    key = "prompt" if h == "Question" else "answer"
                    out += ["", f"<small>Before the readability polish: {ev['pre_polish'][key]}</small>"]
                elif ev and h == "Answer":
                    out += ["", f"<small>Readability polish not used ({ev['status']}).</small>"]
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def sheets(rs: list[list]) -> list[tuple]:
    return [("ITEMS", rs, WIDTHS), ("README", [list(x) for x in README_LINES], [32, 120])]
