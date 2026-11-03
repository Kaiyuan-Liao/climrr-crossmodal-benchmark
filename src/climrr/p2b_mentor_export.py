"""Pilot P2b mentor export: post-checks v2.3 report-only re-run and the five-item mentor sheet (2026-11-03).

`recheck_v23` re-runs `synthesis_post_checks` at v2.2 (must equal the recorded result) and v2.3 on the current version of
every pilot item (items index) against the packet it was built from, and v2.3's leakage checks on the COORDINATOR-proposed
texts. **No item is modified.**

`mentor_rows` builds the mentor sheet ITEMS (five rows, six columns): the COORDINATOR-proposed question and reference
answer (`P2b_coordinator_edits_2026-11-03.yaml`, verbatim), the table side in plain words from the item's table-pattern
provenance and the data dictionary, the paper side (the groups and member statements the answer uses, from the EXECUTOR
support map `P2b_mentor_support_map_v1.yaml`) and the original passages, verbatim from
`artifacts/litstatements/run2/statements.jsonl`. `README` holds the four framing lines. The same content is rendered as
Markdown. The regional item's per-region means and cell counts come from `table_patterns_v1.jsonl` (gitignored, pinned).

No model call; no item, concept-map, column-status or compatibility change.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from climrr import benchmark_items as bi
from climrr import itemseeds as sd
from climrr import litsynth_run2 as s2
from climrr import litsynth_run3 as s3
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

REVIEW_DIR = REPO_ROOT / "artifacts" / "benchmark" / "review"
EDITS_PATH = REVIEW_DIR / "P2b_coordinator_edits_2026-11-03.yaml"
EDITS_SHA256 = "98bae42677f5cc5727527f865657c53e3bcfae2b2c3a4e183a1126b2c4efff86"  # the work package's section D, verbatim
SUPPORT_MAP_PATH = REVIEW_DIR / "P2b_mentor_support_map_v1.yaml"
RECHECK_PATH = s3.ITEMS_ROOT / "post_checks_v2_3_report.json"
STATEMENTS_PATH = REPO_ROOT / "artifacts" / "litstatements" / "run2" / "statements.jsonl"
STATEMENTS_INGESTED_PATH = REPO_ROOT / "artifacts" / "litstatements" / "run2" / "statements_ingested.jsonl"
DICTIONARY_PATH = REPO_ROOT / "data" / "metadata" / "dictionary_extracted.txt"
MENTOR_XLSX_PATH = REVIEW_DIR / "MENTOR_PILOT_ITEMS_2026-11-05.xlsx"
MENTOR_MD_PATH = REVIEW_DIR / "MENTOR_PILOT_ITEMS_2026-11-05.md"
PASSAGE_MAX = 700
MENTOR_HEADER = ["#", "Question", "Reference answer", "Table side", "Paper side", "Original passages"]
MENTOR_WIDTHS = [12, 45, 60, 45, 45, 70]


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def edits(path: Path = EDITS_PATH) -> dict:
    """{item_id: edit record, with the file's `edit_origin`} in the work package's order (n 1-5)."""
    _check(sha256_file(path) == EDITS_SHA256, f"{Path(path).name} differs from its pinned SHA-256")
    doc = load_yaml(path)
    return {x["item_id"]: {**x, "edit_origin": doc["edit_origin"]} for x in sorted(doc["items"], key=lambda x: x["n"])}


def support_map(path: Path = SUPPORT_MAP_PATH) -> dict:
    return {x["item_id"]: x for x in load_yaml(path)["items"]}


# --- post-checks v2.3, report only -----------------------------------------------------------------------------


def _recheck(it: dict, cols: list[str]) -> dict:
    h = it["review"]["history"][0]
    ci = s2.packet_for_item(it)["checks_input"]
    v22 = bi.synthesis_post_checks(s2._as_candidate(it), h["reference_answer_tagged"], ci, cols)
    _check(v22["reasons"] == h["reasons"] and v22["pass"] == (h["event"] == "deterministic_pass"),
           f"{it['item_id']}: v2.2 recomputed differs from the recorded result")
    v23 = bi.synthesis_post_checks(s2._as_candidate(it), h["reference_answer_tagged"], ci, cols, bi.SYNTH_CHECK_VERSION_V23)
    new = [r for r in v23["reasons"] if r not in v22["reasons"]]
    return {"item_id": it["item_id"], "run": h["source_commit"][:7], "v2_2_pass": v22["pass"], "v2_3_pass": v23["pass"],
            "v2_3_new_reasons": new, "hit": bool(new)}


def edited_text_flags(e: dict, cols: list[str]) -> dict:
    """v2.3's leakage checks on a COORDINATOR-proposed prompt and integrated answer (leakage_check v1 on the prompt,
    the reference-text check on both, plus the v2.3 model-source phrases)."""
    p, a = e["edited_prompt"], e["edited_reference_integrated"]
    lk = bi.leakage_check(p, cols)
    return {"item_id": e["item_id"],
            "prompt": lk["flags"] + [f for f in bi.text_leakage(p, cols) if f.startswith(("internal id", "identifier-like"))]
                      + bi.model_source_flags(p),
            "reference_integrated": bi.text_leakage(a, cols) + bi.model_source_flags(a)}


def recheck_v23(items: list[dict], superseded: list[dict], edit_records: list[dict], cols: list[str] | None = None) -> dict:
    cols = cols if cols is not None else bi.column_names()
    cur = [_recheck(it, cols) for it in items]
    sup = [_recheck(it, cols) for it in superseded]
    ed = [edited_text_flags(e, cols) for e in edit_records]
    return {"check_version": bi.SYNTH_CHECK_VERSION_V23, "baseline_version": bi.SYNTH_CHECK_VERSION, "report_only": True,
            "items_modified": 0, "patterns": [rx.pattern for rx in bi.MODEL_SOURCE_RES],
            "current_items": cur, "items_hit": [x["item_id"] for x in cur if x["hit"]],
            "superseded_items": sup, "coordinator_proposed_texts": ed,
            "coordinator_proposed_hits": [x["item_id"] for x in ed if x["prompt"] or x["reference_integrated"]]}


# --- the mentor sheet ---------------------------------------------------------------------------------------------


def _f1(v) -> str:
    return f"{float(v):.1f}"


def _signed(v) -> str:
    return ("+" if float(v) >= 0 else "") + _f1(v)


def dictionary_lines() -> list[str]:
    return DICTIONARY_PATH.read_text(encoding="utf-8").splitlines()


def period_names() -> dict:
    """The dictionary's period sentences (lines 101-102), checked: {'historical': ..., 'mid': ..., 'end': ...}."""
    text = " ".join(x.strip() for x in dictionary_lines()[100:102])
    m = re.search(r"mid-century period \((\d{4}) to (\d{4})\) and end-of-century period \((\d{4}) to (\d{4})\)\. "
                  r"A historical period \((\d{4}) to (\d{4})\) is also modeled", text)
    _check(bool(m), "dictionary lines 101-102 no longer state the periods")
    g = m.groups()
    return {"historical": f"Historical, {g[4]} to {g[5]} (modeled)", "mid": f"Mid-Century, {g[0]} to {g[1]}",
            "end": f"End-Century, {g[2]} to {g[3]}"}


def _quantity(p: dict) -> str:
    """The dictionary's description of the future column, without its period suffix (e.g. 'Number of Summer days with
    daily max heat index above 95 F')."""
    srcs = p["provenance"]["column_sources"]
    fut = next(c["column"] for c in p["provenance"]["columns"] if "_HIS_" not in c["column"])
    q = srcs[fut]["quote"]
    _check(q.startswith(fut + " "), f"{fut}: dictionary quote does not start with the column name")
    desc = q[len(fut) + 1:].split(" -- ")[0].strip()
    return f"{desc} (data dictionary, columns {', '.join(c['column'] for c in p['provenance']['columns'])})"


def _provisional(p: dict) -> list[str]:
    out = []
    if any("IC-012" in r for r in p.get("provisional_reasons") or []):
        out.append("State label provisional (IC-012)")
    if any(r.startswith("unweighted_mean") for r in p.get("provisional_reasons") or []):
        out.append("unweighted mean over grid cells (provisional aggregation rule)")
    return out


def region_patterns(ids: list[str]) -> dict:
    """The per-region patterns of a regional contrast, from `table_patterns_v1.jsonl` (checked against its pin)."""
    _check(sha256_file(sd.PATTERNS_PATH) == sd.PATTERNS_SHA256, "table_patterns_v1.jsonl differs from its pinned SHA-256")
    want, out = set(ids), {}
    with open(sd.PATTERNS_PATH, encoding="utf-8") as f:
        for line in f:
            p = json.loads(line)
            if p["pattern_id"] in want:
                out[p["pattern_id"]] = p
    _check(set(out) == want, f"region patterns missing: {sorted(want - set(out))}")
    return out


def table_side(it: dict) -> str:
    p = it["reference_components"]["table_patterns"][0]
    per, cv = period_names(), p["computed_value_or_range"]
    lines = [f"Quantity: {_quantity(p)}"]
    if p["geography_type"] == "nca_region":
        regs = region_patterns(p["provenance"]["region_pattern_ids"])
        by_region = {r["geography"]: r for r in regs.values()}
        ranked = cv["regions_ordered"]
        lines.append(f"Geography: NCA5 regions --- the {len(ranked)} with a State label in the table (no U.S. Caribbean, no "
                     "Hawai'i / U.S.-Affiliated Pacific Islands)")
    else:
        lines.append(f"Geography: {p['geography']} (State label in the table)")
    lines += [f"Season: {p['season']}", f"Baseline window: {per['historical']}", f"Future window: {per[p['horizon']]}",
              f"Scenario: {p['scenario']}"]
    if p["geography_type"] == "nca_region":
        lines.append("Statistic: change in the mean number of days (future minus baseline), per region; regions ranked largest first")
        lines.append("Values (mean days, baseline -> future, change):")
        n = 0
        for r in ranked:
            rp = by_region[r["region"]]["computed_value_or_range"]
            _check(_f1(rp["value"]) == _f1(r["value"]), f"{r['region']}: region pattern value differs from the ranking")
            n += rp["n_cells_used"]
            lines.append(f"  {r['rank']}. {r['name']}: {_f1(rp['mean_from'])} -> {_f1(rp['mean_to'])} ({_signed(r['value'])}); "
                         f"{rp['n_cells_used']:,} grid cells")
        lines.append(f"Grid cells: {n:,} over the {len(ranked)} regions")
    else:
        stat = {"direction": "direction of the change in the mean number of days (future minus baseline)",
                "absolute_change": "change in the mean number of days (future minus baseline)"}[p["statistic"]]
        lines.append(f"Statistic: {stat}")
        cells = cv["cell_direction_counts"] if "cell_direction_counts" in cv else None
        lines.append(f"Value: mean {_f1(cv['mean_from'])} days -> {_f1(cv['mean_to'])} days ({_signed(cv['value'])} days)")
        if p.get("rank"):
            lines.append(f"Rank among State labels: {p['rank']['rank']} of {p['rank']['of']} (largest change first)")
        lines.append(f"Grid cells: {cv['n_cells_used']:,}"
                     + (f" (cells increasing: {cells['increase']:,})" if cells else ""))
    lines += _provisional(p)
    return "\n".join(lines)


def strength_words(strength: str, n_papers: int) -> str:
    return {"multi_source_supported": f"supported by {n_papers} independent papers",
            "single_source_supported": f"single study ({n_papers} paper)",
            "review_supported": f"review-supported ({n_papers} papers)"}[strength]


def _statements() -> tuple[dict, dict]:
    """({LS id: ingested record}, {agent statement id: statements.jsonl record})."""
    ing = {json.loads(ln)["statement_id"]: json.loads(ln) for ln in STATEMENTS_INGESTED_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()}
    raw = {json.loads(ln)["statement_id"]: json.loads(ln) for ln in STATEMENTS_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()}
    return ing, raw


def cut_passage(text: str, limit: int = PASSAGE_MAX) -> str:
    """The passage unchanged up to `limit` characters; longer, cut at the last sentence end within the limit + ' […]'."""
    if len(text) <= limit:
        return text
    ends = [m.end() for m in re.finditer(r"[.!?](?=\s)", text[:limit])]
    return (text[:ends[-1]] if ends else text[:limit]).rstrip() + " […]"


def paper_cells(it: dict, smap: dict) -> tuple[str, str]:
    """(Paper side, Original passages) from the support map's groups and members, checked against the packet."""
    if smap.get("table_only"):
        _check(not smap["groups"], f"{it['item_id']}: a table-only item lists groups")
        return "none — table-only item (pattern identification)", "none"
    packet = s2.packet_for_item(it)
    groups = {g["group_id"]: g for g in packet["provenance"]["groups"]}
    tagged = it["review"]["history"][0]["reference_answer_tagged"]
    cited = {g for s in tagged["literature_interpretation"] for g in s["group_ids"]}
    ing, raw = _statements()
    side, passages = [], []
    for sg in smap["groups"]:
        g = groups[sg["group_id"]]
        _check(sg["group_id"] in cited, f"{it['item_id']}: {sg['group_id']} is not cited by the item")
        members = {m["statement_id"]: m for m in g["members"]}
        used = [members[sid] for sid in sg["members"]]
        papers_used = sorted({m["paper_item_id"] for m in used})
        of_them = (f"; the statement{'s' if len(used) > 1 else ''} used come{'s' if len(used) == 1 else ''} from "
                   f"{len(papers_used)} of them") if g["n_papers"] > 1 else ""
        side.append(f"{g['label'] or used[0]['statement']} — {strength_words(g['strength_in_packet'], g['n_papers'])}{of_them}")
        side += [f"  - {m['statement']} (paper {m['paper_item_id']})" for m in used]
        passages.append(f"[{g['label'] or sg['group_id']}]")
        for m in used:
            rec = raw[ing[m["statement_id"]]["agent_statement_id"]]
            _check(rec["verbatim_passage"] == m["verbatim_passage"] == ing[m["statement_id"]]["verbatim_passage"],
                   f"{m['statement_id']}: verbatim passage differs between statements.jsonl, the ingest and the packet")
            passages.append(f"{m['paper_item_id']}, {rec['proposal']['section_key']}: \"{cut_passage(rec['verbatim_passage'])}\"")
            if rec.get("passage_recovery") == "prefix_anchor" and rec["passage_as_proposed"] != rec["verbatim_passage"]:
                passages.append("  [provenance note: this passage was recovered by prefix anchor and stops where the extraction "
                                "agent's proposed passage, not verified against the paper text, continues: "
                                f"\"{cut_passage(rec['passage_as_proposed'][len(rec['verbatim_passage']):].strip())}\"]")
    return "\n".join(side), "\n".join(passages)


README_LINES = [
    ["What the benchmark question is",
     "A closed-book question: the model under test gets only the Question --- no table, no paper, no data. It must answer "
     "from what it knows about projected climate hazards and their physical drivers."],
    ["How the answer is graded",
     "At the pattern level: direction of the change, rough magnitude (e.g. 'roughly tripling'), ranking where the question "
     "asks for one, and the mechanisms named. Exact values (the numbers in 'Table side') are provenance for the reference "
     "answer; the model is not expected to reproduce them."],
    ["What 'single study' means",
     "The statement is found in one paper of our literature corpus (after counting duplicate copies of a paper once). The "
     "reference answer then hedges it ('one study suggests'), and a grader does not require it as consensus."],
    ["Two questions for the mentor",
     "(1) Are table-only items (item 1: pattern identification, no literature) acceptable in the benchmark? (2) Are "
     "single-study mechanisms acceptable in a reference answer if they are labelled as single-study?"],
]


def mentor_rows(items: dict, edit_records: dict, smap: dict) -> list[list]:
    rows = [MENTOR_HEADER]
    for iid, e in edit_records.items():
        it = items[iid]
        paper, passages = paper_cells(it, smap[iid])
        rows.append([f"{e['n']}\n{iid}", e["edited_prompt"], e["edited_reference_integrated"], table_side(it), paper, passages])
    return rows


MD_INTRO = ("Five pilot benchmark items. Question and reference answer are COORDINATOR-proposed edits, not yet frozen. "
            "Same content as `MENTOR_PILOT_ITEMS_2026-11-05.xlsx` (sheets ITEMS and README).")


def render_md(rows: list[list], readme: list[list] = README_LINES, intro: str = MD_INTRO) -> str:
    out = ["# Pilot items for mentor review --- 2026-11-05", "", intro, "", "## README", ""]
    out += [f"- **{k}.** {v}" for k, v in readme]
    for r in rows[1:]:
        n, iid = r[0].split("\n")
        out += ["", f"## {n} · {iid}", ""]
        for h, v in zip(rows[0][1:], r[1:]):
            out += [f"### {h}", ""]
            if h in ("Table side", "Paper side", "Original passages"):
                out += [f"    - {ln.strip().removeprefix('- ')}" if ln.startswith("  ") else f"- {ln}" for ln in v.split("\n")]
            else:
                out.append(v)
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def sheets(rows: list[list], readme: list[list] = README_LINES) -> list[tuple]:
    return [("ITEMS", rows, MENTOR_WIDTHS), ("README", [list(x) for x in readme], [32, 120])]
