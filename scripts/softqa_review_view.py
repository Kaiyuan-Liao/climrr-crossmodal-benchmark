#!/usr/bin/env python3
"""Render one soft-QA candidate for a human reviewer, evidence first (D-033).

Prints the candidate in the ruling's review order
(`docs/SOFTQA_REVIEW_PROTOCOL.md` §5):

  1. paper passage;
  2. table provenance and deterministic values;
  3. QA pair;
  4. candidate semantic annotations;
  5. agent rationale/confidence last.

Section 5 --- the agent's `link_rationale` and `confidence` --- is **withheld**
unless `--show-rationale` is given. Record the checklist judgments
(`data/metadata/softqa/review_form_v1.yaml`) first, then re-run with the flag.

Input: a `candidates.jsonl` from `scripts/litcollect/softqa_agent.py` (agent
records, mapped onto `candidate_schema_v1.json` here) or a JSONL / JSON file of
schema records. A null field prints as `pending: <stage>`.

Writes a run record per view (the candidate id, the input file's SHA-256 and
whether the rationale was shown): evidence that the review order was followed.

  python scripts/softqa_review_view.py --candidates <run>/candidates.jsonl --candidate-id C-123-01
  python scripts/softqa_review_view.py --candidates <run>/candidates.jsonl --candidate-id C-123-01 --show-rationale
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import softqa  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

WITHHELD = "[withheld --- record the checklist judgments first, then re-run with --show-rationale]"
SECTION_TITLES = (
    "1. PAPER PASSAGE",
    "2. TABLE PROVENANCE AND DETERMINISTIC VALUES",
    "3. QA PAIR",
    "4. CANDIDATE SEMANTIC ANNOTATIONS",
    "5. AGENT RATIONALE / CONFIDENCE",
)


def load_records(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    try:
        obj = json.loads(text)
        raw = obj if isinstance(obj, list) else [obj]
    except json.JSONDecodeError:
        raw = [json.loads(ln) for ln in text.splitlines() if ln.strip()]
    schema = softqa.load_schema()
    return [r if r.get("schema_version") == softqa.SCHEMA_VERSION else softqa.map_trackc(r, schema) for r in raw]


def render(rec: dict, show_rationale: bool = False) -> str:
    pending = rec["mapping"]["pending_stages"]
    agent = rec.get("agent_record") or {}
    proposal = agent.get("proposal") if isinstance(agent.get("proposal"), dict) else {}
    pp, tp, sl = rec["paper_provenance"], rec["table_provenance"], rec["soft_link"]
    dv, hr = rec["deterministic_validation"], rec["human_review"]

    def val(group: str, field: str, d: dict) -> str:
        v = d[field]
        if v is None:
            stage = pending.get(f"{group}.{field}")
            return f"pending: {stage}" if stage else "null"
        return json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v

    out = [f"CANDIDATE {rec['candidate_identity']['candidate_id']}   status: {rec['status']}   "
           f"track: {rec['candidate_identity']['track']}", ""]

    out += [SECTION_TITLES[0]]
    for f in ("paper_item_id", "paper_sha256", "json_path"):
        out.append(f"  {f}: {val('paper_provenance', f, pp)}")
    out.append(f"  span [start,end): [{pp['span_start']}, {pp['span_end']})")
    out.append(f"  span_reslice_pass: {dv['span_reslice_pass']}")
    out.append("  verbatim passage:")
    out.append(f"    \"{pp['verbatim_passage']}\"")
    out.append(f"  concept term located: {json.dumps(agent.get('concept_hit'), ensure_ascii=False)}")
    out.append(f"  place term located:   {json.dumps(agent.get('place_hit'), ensure_ascii=False)}")
    out.append("")

    out += [SECTION_TITLES[1]]
    for f in tp:
        out.append(f"  {f}: {val('table_provenance', f, tp)}")
    out.append("  deterministic checks:")
    for f in dv:
        out.append(f"    {f}: {val('deterministic_validation', f, dv)}")
    out.append("")

    out += [SECTION_TITLES[2]]
    out.append(f"  proposed question (LLM): {proposal.get('example_question')}")
    out.append(f"  answer: {val('human_review', 'final_answer', hr)}")
    if hr["final_question"] is not None:
        out.append(f"  final question (frozen): {hr['final_question']}")
    out.append("")

    out += [SECTION_TITLES[3]]
    out.append(f"  qa_type: {val('soft_link', 'qa_type', sl)}")
    for f in ("paper_concept", "paper_geography", "paper_geography_role", "paper_time", "paper_scenario"):
        out.append(f"  {f}: {val('paper_provenance', f, pp)}")
    for f in ("concept_relation", "geography_relation", "time_relation", "scenario_relation",
              "direction_relation", "unmatched_dimensions"):
        out.append(f"  {f}: {val('soft_link', f, sl)}")
    out.append(f"  paper_side_fact (LLM): {proposal.get('paper_side_fact')}")
    out.append(f"  table_side_needed (LLM): {proposal.get('table_side_needed')}")
    out.append("")

    out += [SECTION_TITLES[4]]
    if show_rationale:
        out.append(f"  link_rationale: {sl['link_rationale']}")
        out.append(f"  confidence: {proposal.get('confidence')}")
    else:
        out.append(f"  {WITHHELD}")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--candidates", required=True, type=Path)
    ap.add_argument("--candidate-id", required=True)
    ap.add_argument("--show-rationale", action="store_true")
    ap.add_argument("--runs-dir", type=Path, default=None, help="run-record directory (default reports/runs)")
    a = ap.parse_args(argv)

    recs = [r for r in load_records(a.candidates) if r["candidate_identity"]["candidate_id"] == a.candidate_id]
    if len(recs) != 1:
        print(f"expected exactly one candidate {a.candidate_id}, found {len(recs)}", file=sys.stderr)
        return 2
    sys.stdout.write(render(recs[0], a.show_rationale))
    write_run_record(
        "softqa_review_view",
        result_summary={"candidate_id": a.candidate_id, "status": recs[0]["status"],
                        "rationale_shown": a.show_rationale},
        passed=True,
        data_path=a.candidates,
        config_snapshot={"candidates": a.candidates.name, "candidate_id": a.candidate_id,
                         "show_rationale": a.show_rationale,
                         "schema_sha256": softqa.schema_sha256()},
        runs_dir=a.runs_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
