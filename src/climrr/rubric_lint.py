"""Rubric lint v1 for the pilot items (P2b-ingest-items Phase B; D-056). A report, never an edit.

Flags, per item and rubric list, the lines a reviewer should look at --- the reviewer's checklist in the item review
workbook, not automatic edits:

- `generation_constraint` --- a rubric line (any list) that states a generation constraint rather than a grading
  criterion: `GENERATION_CONSTRAINT_RE` (the work package's pattern, case-insensitive; "multi.source" any separator);
- `required_single_source_only` --- a required point whose `source_ids` (the tagged rubric points) are all group ids
  and every one is `single_source_supported` in the item's packet;
- `hedge_strength_mismatch` --- a literature sentence tagged only with `multi_source_supported` groups that contains
  "one study" or "a single study";
- `rung1_prompt_mechanism` --- a rung-1 prompt containing "driver", "mechanism" or "cause" (word start; "because" is not
  a hit);
- `required_tercile` --- a required point containing "tercile".

Strengths are the packet's `strength_in_packet` (`checks_input.group_strength`) for the packet the item was built from.
No model call, no table value.
"""

from __future__ import annotations

import re

VERSION = "rubric_lint v1"
RUBRIC_LISTS = ("required_points", "optional_points", "acceptable_variants", "disallowed_claims", "fatal_errors")
GENERATION_CONSTRAINT_RE = re.compile(r"allowed descriptors|allowed_numbers|decimal number|exact values are not required|"
                                      r"multi.source supported|cite a|not in the packet|not provided in the packet", re.I)
ONE_STUDY_RE = re.compile(r"\b(?:one study|a single study)\b", re.I)
RUNG1_MECHANISM_RE = re.compile(r"\b(?:driver|mechanism|cause)", re.I)
TERCILE_RE = re.compile(r"tercile", re.I)
RULES = {
    "generation_constraint": "a rubric line that is a generation constraint, not a grading criterion (pattern: "
                             + GENERATION_CONSTRAINT_RE.pattern + ", case-insensitive)",
    "required_single_source_only": "a required point whose source ids are only single_source_supported groups",
    "hedge_strength_mismatch": "a literature sentence tagged only with multi_source_supported groups that says 'one study' / 'a single study'",
    "rung1_prompt_mechanism": "a rung-1 prompt that asks about a driver, mechanism or cause",
    "required_tercile": "a required point that names a tercile",
}


def _flag(rule: str, field: str, index: int | None, text: str, detail: str | None = None) -> dict:
    return {"rule": rule, "field": field, "index": index, "text": text, "detail": detail}


def lint_item(item: dict, group_strength: dict) -> list[dict]:
    """The flags of one schema-v2 item (`review.history[0].reference_answer_tagged` holds the tags)."""
    flags = []
    rub, tagged = item["rubric"], item["review"]["history"][0]["reference_answer_tagged"]
    for field in RUBRIC_LISTS:
        for i, t in enumerate(rub.get(field) or []):
            m = GENERATION_CONSTRAINT_RE.search(t)
            if m:
                flags.append(_flag("generation_constraint", f"rubric.{field}", i, t, f"matches {m.group(0)!r}"))
    req = [p for p in tagged.get("rubric_points") or [] if p.get("field") == "required_points"]
    for i, p in enumerate(req):
        ids = p.get("source_ids") or []
        if ids and all(g in group_strength for g in ids) and all(group_strength[g] == "single_source_supported" for g in ids):
            flags.append(_flag("required_single_source_only", "rubric.required_points", i, p["point"], ", ".join(ids)))
    for i, s in enumerate(tagged.get("literature_interpretation") or []):
        ids = [g for g in s.get("group_ids") or [] if g in group_strength]
        if ids and all(group_strength[g] == "multi_source_supported" for g in ids) and ONE_STUDY_RE.search(s["sentence"]):
            flags.append(_flag("hedge_strength_mismatch", "reference_answer.literature_interpretation", i, s["sentence"],
                               ", ".join(f"{g} ({group_strength[g]})" for g in ids)))
    if item["use_case_level"] == 1:
        m = RUNG1_MECHANISM_RE.search(item["prompt"])
        if m:
            flags.append(_flag("rung1_prompt_mechanism", "prompt", None, item["prompt"], f"matches {m.group(0)!r}"))
    for i, t in enumerate(rub.get("required_points") or []):
        if TERCILE_RE.search(t):
            flags.append(_flag("required_tercile", "rubric.required_points", i, t))
    return flags


def lint(items: list[dict], strengths: dict) -> dict:
    """`strengths`: {item_id: the packet's group_strength}. The report: rules, per-item flags and counts, totals."""
    out = []
    for it in sorted(items, key=lambda x: x["item_id"]):
        fl = lint_item(it, strengths[it["item_id"]])
        out.append({"item_id": it["item_id"], "use_case_level": it["use_case_level"], "n_flags": len(fl),
                    "counts": {r: sum(f["rule"] == r for f in fl) for r in RULES}, "flags": fl})
    return {"version": VERSION, "rules": RULES, "edits_made": 0, "items": out,
            "totals": {r: sum(x["counts"][r] for x in out) for r in RULES} | {"all": sum(x["n_flags"] for x in out)}}
