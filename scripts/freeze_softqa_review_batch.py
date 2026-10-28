#!/usr/bin/env python3
"""Freeze Track C review batch 01 and prepare (unfilled) reviewer forms (D-033; reviewer 1 = Kaiyuan Liao).

The batch is the deterministic triage of the ingested run 1
(`climrr.softqa_run1.triage`: `deterministic_pass`, `concept_relation` direct,
place role study_area / cited_study_area, at most two unmatched dimensions),
in `candidate_id` order, as `candidate_schema_v1` records taken verbatim from
`artifacts/softqa/run1/candidates_schema.jsonl`. Writes
`artifacts/softqa/review_batch_01.json` (pinned in `data/manifest.json`) and one
`review_form_v1.yaml` copy per candidate under `artifacts/softqa/review_batch_01_forms/`
with only `candidate_id` and `reviewer_role` filled. Table-side values are **not**
computed: the candidate structure is frozen first; values come after the review
disposition (D-033 §3). Refuses to overwrite a different batch or a touched form.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import softqa  # noqa: E402
from climrr import softqa_run1 as r1  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

BATCH_ID = "review_batch_01"
FROZEN_DATE = "2026-10-28"
REVIEWER_1 = "Kaiyuan Liao"


def build_batch() -> dict:
    data = json.loads(r1.MANIFEST.read_text(encoding="utf-8"))
    entry = next(d for d in data["diagnostics"] if d["diagnostic_id"] == r1.DIAGNOSTIC_ID)
    if sha256_file(r1.RUN_MANIFEST) != entry["manifest_sha256"]:
        raise ValueError("run-1 manifest.csv differs from its pin")
    schema = softqa.load_schema()
    by_id = {r["candidate_identity"]["candidate_id"]: r for r in r1._jsonl(r1.SCHEMA_JSONL)}
    ids = [c["candidate_id"] for c in r1.triage(r1.load_candidates())]
    recs = [softqa.validate(by_id[i], schema) for i in ids]
    return {
        "batch_id": BATCH_ID,
        "frozen_date": FROZEN_DATE,
        "statement": ("Candidates for first human review (reviewer 1). Not accepted QA. Table-side values not "
                      "computed: the candidate structure is frozen first; values come after the review "
                      "disposition (D-033 section 3). The Fire Weather Index is a fire-danger index, never fire "
                      "occurrence; historical periods are modeled baselines."),
        "source": {"diagnostic_id": r1.DIAGNOSTIC_ID, "run1_manifest_sha256": entry["manifest_sha256"],
                   "candidates_schema_sha256": sha256_file(r1.SCHEMA_JSONL)},
        "triage_rule": ("status deterministic_pass AND proposal.concept_relation == 'direct' AND "
                        "proposal.paper_geography_role in {study_area, cited_study_area} AND "
                        f"len(proposal.unmatched_dimensions) <= {r1.TRIAGE_MAX_UNMATCHED}"),
        "order": "candidate_id",
        "reviewer_1": REVIEWER_1,
        "review_protocol": "docs/SOFTQA_REVIEW_PROTOCOL.md (v1); form data/metadata/softqa/review_form_v1.yaml",
        "acceptance_gate": {i: softqa.acceptance_gate(r) for i, r in zip(ids, recs)},
        "n_candidates": len(recs),
        "candidates": recs,
    }


def form_text(candidate_id: str) -> str:
    text = r1.FORM.read_text(encoding="utf-8")
    for old, new in (("  candidate_id:\n", f"  candidate_id: {candidate_id}\n"),
                     ("  reviewer_role:          #", "  reviewer_role: reviewer_1  #")):
        if text.count(old) != 1:
            raise ValueError(f"review form layout changed: {old!r}")
        text = text.replace(old, new)
    return (f"# Prepared for {BATCH_ID} ({FROZEN_DATE}); NOT FILLED. Reviewer 1: {REVIEWER_1}.\n"
            f"# View: python scripts/softqa_review_view.py --candidates artifacts/softqa/{BATCH_ID}.json "
            f"--candidate-id {candidate_id}\n") + text


def main() -> int:
    batch = build_batch()
    text = json.dumps(batch, indent=1, ensure_ascii=False, sort_keys=False) + "\n"
    if r1.BATCH_PATH.exists() and r1.BATCH_PATH.read_text(encoding="utf-8") != text:
        raise SystemExit(f"{r1.BATCH_PATH} exists and differs; a frozen batch is not overwritten")
    r1.BATCH_PATH.write_text(text, encoding="utf-8")
    r1.FORMS_DIR.mkdir(parents=True, exist_ok=True)
    ids = [r["candidate_identity"]["candidate_id"] for r in batch["candidates"]]
    for i in ids:
        f = r1.FORMS_DIR / f"{i}.reviewer_1.yaml"
        if f.exists() and f.read_text(encoding="utf-8") != form_text(i):
            raise SystemExit(f"{f} exists and differs (a form being filled is never overwritten)")
        f.write_text(form_text(i), encoding="utf-8")
    sha = sha256_file(r1.BATCH_PATH)

    data = json.loads(r1.MANIFEST.read_text(encoding="utf-8"))
    entry = {
        "filename": r1.BATCH_PATH.name, "path": r1.repo_rel(r1.BATCH_PATH),
        "role": (f"Track C {BATCH_ID} --- the {len(ids)} run-1 triage candidates for reviewer 1 (Kaiyuan Liao), "
                 "candidate_schema_v1 records in candidate_id order; frozen before any review; not accepted QA"),
        "sha256": sha, "bytes": r1.BATCH_PATH.stat().st_size, "row_count": None, "column_count": None,
        "encoding_note": "UTF-8, LF line endings, no byte-order mark.",
        "acquisition_date": FROZEN_DATE,
        "storage_policy": "tracked in ordinary Git as an immutable object; a change is a new batch",
        "tracked_in_git": True, "decision_ref": "D-029, D-030, D-033",
        "source_description": "built by scripts/freeze_softqa_review_batch.py from artifacts/softqa/run1/candidates_schema.jsonl",
        "interpretation_notes": "no interpretation assigned; no column status, concept-map entry or compatibility rule changed",
        "n_records": len(ids), "candidate_ids": ids,
    }
    data["files"] = [f for f in data["files"] if f.get("path") != entry["path"]] + [entry]
    r1.MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rec = write_run_record(
        "freeze_softqa_review_batch",
        result_summary={"batch_id": BATCH_ID, "n_candidates": len(ids), "candidate_ids": ids, "sha256": sha,
                        "forms_prepared": len(ids), "acceptance_gate": {i: g["status"] for i, g in
                                                                       batch["acceptance_gate"].items()}},
        passed=True, data_path=r1.SCHEMA_JSONL, output_path=r1.BATCH_PATH,
        config_snapshot={"triage_rule": batch["triage_rule"], "reviewer_1": REVIEWER_1},
    )
    print(json.dumps({"batch_sha256": sha, "candidate_ids": ids}, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
