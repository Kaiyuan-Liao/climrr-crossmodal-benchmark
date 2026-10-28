#!/usr/bin/env python3
"""Track C run 1: ingest the Polaris output as a diagnostic and candidate pool (D-029, D-030, D-033).

Takes `softqa_run1.tar.gz` extracted outside the repository. Verifies it (log
START line: 243 candidates, units / QA-types as-loaded hashes recomputed from the
tracked files, v1 system prompt, model, index identity; DONE totals; both logs
identical; `candidates.jsonl` and `summary.json` re-derived from every
`result.json`; every record's source commit and input pins), copies
`result.json`, `candidates.jsonl`, `summary.json` and the logs into
`artifacts/softqa/run1/` --- **not** `prompt_user.txt` or `response.json`, whose
SHA-256 go to `excluded_files.csv` --- maps every record onto
`candidate_schema_v1.json` (`candidates_schema.jsonl`; all must validate), writes
`manifest.csv`, pins it in `data/manifest.json` under `diagnostics` /
`softqa_run1`, and generates `docs/SOFTQA_TRACKC_RUN1.md`.

Rerunnable: an existing copy must be byte-identical. No model call, no table value.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import softqa_run1 as r1  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

AMENDMENT = {
    "date": "2026-10-28",
    "milestone": "Track C run 1 ingest",
    "change": ("Added softqa_run1 to the diagnostics block (artifacts/softqa/run1/manifest.csv; softqa_agent v1 "
               "output, 243 papers, 193 proposals). A diagnostic and candidate pool, not accepted QA; "
               "prompt_user.txt and response.json not copied (SHA-256 in excluded_files.csv). Every other entry "
               "unchanged."),
    "decision_ref": "D-029, D-030, D-033",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted softqa_run1.tar.gz")
    ap.add_argument("--tarball", type=Path, help="softqa_run1.tar.gz, checked against its SHA-256")
    a = ap.parse_args()

    if a.tarball and sha256_file(a.tarball) != r1.TARBALL_SHA256:
        raise SystemExit(f"{a.tarball} is not the delivered tarball {r1.TARBALL_SHA256}")
    src_facts = r1.verify_source(a.src)
    copied = r1.copy_run(a.src)

    excluded = r1.excluded_text(a.src / "softqa" / "run1")
    if r1.EXCLUDED_CSV.exists() and r1.EXCLUDED_CSV.read_text(encoding="utf-8") != excluded:
        raise SystemExit("excluded_files.csv exists and differs")
    r1.EXCLUDED_CSV.write_text(excluded, encoding="utf-8")
    copy_facts = r1.verify_run(r1.RUN_DIR, with_excluded=False)  # the ingested copy, re-checked
    recs = r1.write_schema_jsonl()

    text = r1.manifest_text()
    r1.RUN_MANIFEST.write_text(text, encoding="utf-8")
    manifest_sha = sha256_file(r1.RUN_MANIFEST)
    lines = text.splitlines()[1:]
    total = sum(int(ln.split(",")[-2]) for ln in lines)

    data = json.loads(r1.MANIFEST.read_text(encoding="utf-8"))
    entry = r1.manifest_entry(manifest_sha, len(lines), total, src_facts["log"], sha256_file(r1.EXCLUDED_CSV))
    data["diagnostics"] = [d for d in data["diagnostics"] if d["diagnostic_id"] != r1.DIAGNOSTIC_ID] + [entry]
    if AMENDMENT not in data["amendments"]:
        data["amendments"].append(AMENDMENT)
    r1.MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    r1.DOC_PATH.write_text(r1.render_doc(), encoding="utf-8")

    k = r1.counts()
    tri = r1.triage(r1.load_candidates())
    summary = {
        "n_files_ingested": len(lines), "files_copied_from_source": copied, "total_bytes": total,
        "manifest_sha256": manifest_sha, "excluded_files": len(excluded.splitlines()) - 1,
        "schema_records_validated": len(recs), "log_start": src_facts["log"]["start"],
        "counts": {x: k[x] for x in ("papers", "groups", "papers_with_zero_groups", "deterministic_pass",
                                     "rejected_pre_review", "rejection_reason_counts_incl_combos")},
        "triage": [c["candidate_id"] for c in tri],
        "copy_recheck_candidates": copy_facts["candidates"],
        "doc_sha256": sha256_file(r1.DOC_PATH),
    }
    rec = write_run_record(
        "ingest_softqa_run1", result_summary=summary, passed=True, data_path=a.tarball, output_path=r1.RUN_DIR,
        data_sha256=None if a.tarball else r1.TARBALL_SHA256,
        config_snapshot={"source": a.tarball.name if a.tarball else "extracted softqa_run1.tar.gz",
                         "source_tarball_sha256": r1.TARBALL_SHA256, "excluded": list(r1.EXCLUDED_NAMES),
                         "run_executed_on": "Polaris; this record is the local ingest, not the run"},
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
