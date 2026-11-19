"""P3 item review workbook v1 and the run-5 review-flag list (work package P3c, section C; report only, no item modified).

One row per run-5 sample item (in the mentor sheet's order): the display text and its source, the pre-polish text, the
polish status and reasons, the `edited_prompt` / `edited_reference_integrated` cells with `edit_origin`, the flag ids, and
empty disposition cells for Kaiyuan and the mentor. **BI-P3-0005** carries the COORDINATOR's proposed question
(`edit_origin = coordinator_proposed`; recorded, not applied: the mentor sheet shows the generated text).

The flags come from four sources, each named on the flag:

- `work_package` --- the two the COORDINATOR named (P3c C.1, C.3);
- `post_check_report` --- the v3.1 reports recorded on each item (`context_driver_report`, `regional_contrast_report`);
  a flag only when one fired;
- `rubric_lint` --- `rubric_lint` v1a on the seven items with each packet's group strengths;
- `executor_reading` --- what the EXECUTOR found reading the texts (`EXECUTOR_FLAGS`). Each is pinned to a substring of
  the field it names, and the build fails if that substring is no longer there.

No model call; no item, packet or status changed.
"""

from __future__ import annotations

from climrr import litsynth_run5 as s5
from climrr import mentor_sheet_v2b as ms
from climrr import rubric_lint as rl
from climrr.paths import REPO_ROOT

REVIEW_DIR = REPO_ROOT / "artifacts" / "benchmark" / "review"
CSV_PATH = REVIEW_DIR / "P3_items_review_v1.csv"
XLSX_PATH = REVIEW_DIR / "P3_items_review_v1.xlsx"
FLAGS_PATH = REVIEW_DIR / "P3_review_flags_v1.json"

PROPOSED = {"BI-P3-0005": {
    "prompt": ("How are dangerous heat-index days in summer projected to change by mid-century under a high-emissions future, "
               "how do the changes differ across U.S. regions, and what drives them?"),
    "origin": "coordinator_proposed",
    "reason": ("P3c C.1: the generated question does not ask about regional differences while the answer gives them; "
               "recorded, not applied (the mentor sheet shows the generated text)")}}

WORK_PACKAGE_FLAGS = [
    {"id": "WP-C1", "item_id": "BI-P3-0005", "kind": "question_scope", "field": "prompt", "needle": "what drives this change?",
     "note": "the question does not ask how the change differs across regions; the answer ranks the regions (Southeast largest, "
             "Alaska essentially no change). Proposed question in edited_prompt (coordinator_proposed)."},
    {"id": "WP-C3", "item_id": "BI-P3-0007", "kind": "duplicate_driver", "field": "answer",
     "needle": "Low humidity combined with strong winds",
     "note": "repeats 'strong winds' from the sentence before: the cited groups LG-fire_weather_v1-driver-c1-003 (strong winds) "
             "and LG-fire_weather_v1-mechanism-c1-002 (strong winds and low humidity) overlap. Note for synthesis prompt v4.2 "
             "(one driver per idea; merge overlapping groups in the answer). Also in the pre-polish text."},
]

EXECUTOR_FLAGS = [
    {"id": "EX-1", "kind": "hedge_scope_lost_in_polish",
     "where": [("BI-P3-0002", "answer", "Global warming raises heat"), ("BI-P3-0003", "answer", "The urban heat island effect intensifies"),
               ("BI-P3-0005", "answer", "Global warming raises heat"), ("BI-P3-0007", "answer", "Low humidity combined with strong winds also drives")],
     "note": "the original's one hedge covered every driver ('Research shows that A, that B, and that C'); the polished text "
             "splits it into sentences and only the first keeps 'Research shows', so the later drivers read as unhedged "
             "statements of fact. Polish checks v2 compare hedge words, not their scope, so they pass. 0004's rewrite keeps "
             "the scope ('It also shows ...'). Candidate for polish checks v2.1 / polish prompt v1.2."},
    {"id": "EX-2", "kind": "certainty_in_polish",
     "where": [("BI-P3-0002", "answer", "They will go from rare to common"), ("BI-P3-0004", "answer", "They will move from rare to common")],
     "note": "'will' states the projection as a certainty in its own sentence ('projected to' is only in the sentence before); "
             "the rubric's fatal errors include stating the projection as a certainty. The pre-polish text kept it inside "
             "'projected to increase, rising from rare to common'."},
    {"id": "EX-3", "kind": "grammar_in_polish", "where": [("BI-P3-0003", "answer", "The projection is for by mid-century")],
     "note": "ungrammatical sentence made by the polish ('The projection is for by mid-century under a high-emissions future.')."},
    {"id": "EX-4", "kind": "mixed_magnitude_classes", "where": [("BI-P3-0003", "answer", "increase slightly and remain rare")],
     "note": "Washington's class is 'remaining rare' (DR-DESC-1 v4: baseline 0.0, future 0.8 days); 'increase slightly' is a "
             "form of the class 'a slight increase', which v4 gives only to ratio classes. Post-checks v3.1 did not object "
             "(the class phrase is present). In the pre-polish text too."},
    {"id": "EX-5", "kind": "fire_outcome_wording",
     "where": [("BI-P3-0007", "literature_interpretation", "raise fire danger and fire size"),
               ("BI-P3-0007", "rubric.required_points", "Humidity and VPD affect fire risk")],
     "note": "the item is about fire-weather danger (FWI, never fire occurrence); 'fire size' is a fire outcome and 'fire "
             "risk' is a word the project avoids for FWI. Both come from the reviewer-tagged group labels (mechanism-c1-002, "
             "driver-c1-002); post-checks v3.1 fail only 'fires' / 'wildfire' / 'burned area'. Not in the display answer."},
    {"id": "EX-6", "kind": "rubric_consistency",
     "where": [("BI-P3-0001", "rubric.required_points", "[w=3] Magnitude class: a moderate increase"),
               ("BI-P3-0004", "rubric.required_points", "[w=1] Direction: increase"),
               ("BI-P3-0002", "rubric.required_points", "Regional ranking: a smaller change than in most states"),
               ("BI-P3-0004", "rubric.required_points", "Regional ranking: a larger change than in most states"),
               ("BI-P3-0003", "rubric.required_points", "(multi‑source)")],
     "note": "0001's required points omit the comparison with other states that its answer gives; 0004 weighs direction, "
             "magnitude and comparison 1 against 2 for each driver (the others weigh the table points 2-3); 0002 / 0004 label "
             "a comparison among states 'Regional ranking'; 0003 writes '(multi-source)' into required points (lint v1a "
             "matches only 'multi-source supported'). Grading-side only; not in the sheet."},
]

ITEM_HEADER = ["order", "item_id", "topic", "seed_id", "display_source", "polish_status", "polish_reasons", "question_display",
               "answer_display", "question_pre_polish", "answer_pre_polish", "edited_prompt", "edited_reference_integrated",
               "edit_origin", "edit_reason", "flags", "kaiyuan_disposition", "kaiyuan_notes", "mentor_disposition", "mentor_notes"]
FLAG_HEADER = ["flag_id", "item_id", "source", "kind", "field", "text", "note"]
README_ROWS = [
    ["what", "P3 item review workbook v1 (work package P3c, section C): the seven run-5 sample items in human_review; report only."],
    ["display", "question_display / answer_display = the text the mentor sheet shows: polished where display_source = polished, "
                "else the synthesis text."],
    ["edits", "edited_prompt / edited_reference_integrated with edit_origin = coordinator_proposed: recorded, not applied; "
              "Kaiyuan confirms or rewrites."],
    ["flags", "FLAGS sheet: source work_package (COORDINATOR), post_check_report (v3.1 reports), rubric_lint (v1a), "
              "executor_reading (EXECUTOR, pinned to the text)."],
    ["dispositions", "kaiyuan_* / mentor_* cells are empty: no item accepted; nothing frozen."],
]


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def field_text(item: dict, field: str) -> str:
    ev = next(h for h in reversed(item["review"]["history"]) if h.get("event") == "polish")
    tagged = item["review"]["history"][0]["reference_answer_tagged"]
    if field == "prompt":
        return item["prompt"]
    if field == "answer":
        return item["reference_answer"]["integrated"]
    if field == "answer_pre_polish":
        return ev["pre_polish"]["answer"]
    if field == "literature_interpretation":
        return "\n".join(s["sentence"] for s in tagged["literature_interpretation"])
    if field.startswith("rubric."):
        return "\n".join(item["rubric"][field.split(".", 1)[1]])
    raise ValueError(f"unknown field {field}")


def _line(text: str, needle: str) -> str:
    """The sentence or line of `text` that holds `needle`."""
    for ln in text.split("\n"):
        if needle in ln:
            i = ln.find(needle)
            start = max(ln.rfind(". ", 0, i) + 2 if ln.rfind(". ", 0, i) >= 0 else 0, 0)
            end = ln.find(". ", i)
            return ln[start:end + 1 if end >= 0 else len(ln)].strip()
    raise ValueError(f"{needle!r} not found")


def flags(items: dict, packets: dict) -> dict:
    out = []
    for f in WORK_PACKAGE_FLAGS:
        text = field_text(items[f["item_id"]], f["field"])
        _check(f["needle"] in text, f"{f['id']}: {f['needle']!r} not in {f['item_id']} {f['field']}")
        out.append({"flag_id": f["id"], "item_id": f["item_id"], "source": "work_package", "kind": f["kind"], "field": f["field"],
                    "text": _line(text, f["needle"]), "note": f["note"]})
    report_hits = {}
    for iid, it in items.items():
        c = it["review"]["history"][0]["checks"]
        for k in ("context_driver_report", "regional_contrast_report"):
            hits = c.get(k) or []
            report_hits.setdefault(k, {})[iid] = len(hits)
            for n, h in enumerate(hits, 1):
                out.append({"flag_id": f"PC-{iid[-4:]}-{k}-{n}", "item_id": iid, "source": "post_check_report", "kind": k,
                            "field": h.get("field"), "text": h.get("sentence") or str(h), "note": "post-checks v3.1 report"})
    lint = rl.lint(list(items.values()), {i: packets[i]["checks_input"]["group_strength"] for i in items})
    for x in lint["items"]:
        for n, fl in enumerate(x["flags"], 1):
            out.append({"flag_id": f"LINT-{x['item_id'][-4:]}-{n}", "item_id": x["item_id"], "source": "rubric_lint", "kind": fl["rule"],
                        "field": fl["field"], "text": fl["text"], "note": f"{lint['version']}: {fl['detail']}"})
    for f in EXECUTOR_FLAGS:
        for n, (iid, field, needle) in enumerate(f["where"], 1):
            text = field_text(items[iid], field)
            _check(needle in text, f"{f['id']}: {needle!r} not in {iid} {field}")
            out.append({"flag_id": f"{f['id']}.{n}", "item_id": iid, "source": "executor_reading", "kind": f["kind"], "field": field,
                        "text": _line(text, needle), "note": f["note"]})
    return {"version": "P3 review flags v1", "work_package": "P3c, section C", "report_only": True, "items_modified": 0,
            "context_driver_report_hits": report_hits["context_driver_report"],
            "regional_contrast_report_hits": report_hits["regional_contrast_report"],
            "rubric_lint": {"version": lint["version"], "totals": lint["totals"]}, "flags": out,
            "counts_by_source": {s: sum(f["source"] == s for f in out)
                                 for s in ("work_package", "post_check_report", "rubric_lint", "executor_reading")}}


def item_rows(items: dict, flag_report: dict) -> list[list]:
    rows = [ITEM_HEADER]
    for n, (iid, topic) in enumerate(ms.ORDER, 1):
        it = items[iid]
        ev = next(h for h in reversed(it["review"]["history"]) if h.get("event") == "polish")
        text, prop = s5.display_text(it), PROPOSED.get(iid)
        rows.append([n, iid, topic, it["review"]["history"][0]["seed_id"], s5.display_source(it), ev["status"],
                     " | ".join(ev["reasons"]), text["prompt"], text["answer"], ev["pre_polish"]["prompt"], ev["pre_polish"]["answer"],
                     prop["prompt"] if prop else "", "", prop["origin"] if prop else "", prop["reason"] if prop else "",
                     ", ".join(f["flag_id"] for f in flag_report["flags"] if f["item_id"] == iid), "", "", "", ""])
    return rows


def flag_rows(flag_report: dict) -> list[list]:
    return [FLAG_HEADER] + [[f[k] for k in ("flag_id", "item_id", "source", "kind", "field", "text", "note")]
                            for f in flag_report["flags"]]
