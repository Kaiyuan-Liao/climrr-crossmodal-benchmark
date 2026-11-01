#!/usr/bin/env python3
"""Pilot P2a Phase A: ingest literature-statement run 2 (agent v2, Polaris, Sophia vLLM; D-043, D-044).

Takes `litstatements_run2_evidence.tar.gz` extracted outside the repository. Verifies it
against every fact the work package states (243 papers, 1,018 statements, 485 pass, 533
rejected with the per-check counts, 0 errors, 21 parse errors, endpoint, generator and
system-prompt hashes, source commit; `statements.jsonl` re-derived from every
`result.json`; both run-2 logs identical) and fails on any difference. Copies the run
files and every `result.json` (as `papers/<item_id>.json`) into
`artifacts/litstatements/run2/`; `prompt_user.txt` and `response.json` are not copied
(SHA-256 in `manifest.json`). Writes `statements_ingested.jsonl` (ids `LS-<item_id>-<nn>`,
pre-check fields, evidence role), `papers_meta.json` (DR-LIT-IND-1), `parse_errors.json`
(counts only) and `manifest.json`. Run 1 is recorded as superseded, never ingested.

Rerunnable: every copy must be byte-identical, and an existing manifest keeps its
`ingested_at`. No model call, no table value.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litstatements_run2 as r2  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted litstatements_run2_evidence.tar.gz")
    ap.add_argument("--tarball", type=Path, help="the tarball itself, checked against its SHA-256")
    a = ap.parse_args()

    if a.tarball and sha256_file(a.tarball) != r2.TARBALL_SHA256:
        raise SystemExit(f"{a.tarball.name} is not the delivered tarball {r2.TARBALL_SHA256}")
    facts = r2.verify_source(a.src)
    copied = r2.copy_run(a.src)

    records = r2.ingested_records()
    if len(records) != r2.RUN_FACTS["statements"]:
        raise SystemExit(f"{len(records)} ingested statements, expected {r2.RUN_FACTS['statements']}")
    r2.write_jsonl(r2.INGESTED_PATH, records)
    meta = r2.papers_meta(a.src)
    r2.write_json(r2.PAPERS_META_PATH, meta)
    perr = r2.parse_error_diagnostics(a.src, facts["parse_error_ids"])
    r2.write_json(r2.PARSE_ERRORS_PATH, perr)

    previous = json.loads(r2.MANIFEST_PATH.read_text(encoding="utf-8")) if r2.MANIFEST_PATH.exists() else {}
    man = r2.manifest(facts, r2.excluded_files(a.src), records, previous.get("ingested_at"))
    r2.write_json(r2.MANIFEST_PATH, man)

    summary = {
        "manifest_sha256": sha256_file(r2.MANIFEST_PATH), "files_copied_this_run": copied,
        "files_in_manifest": len(man["files"]), "excluded_files": len(man["excluded_files"]),
        "counts": man["counts"], "independence_fields_available": meta["independence_fields_available"],
        "diagnostic_same_file_sha256": meta["diagnostic_same_file_sha256"],
        "diagnostic_same_title_section": meta["diagnostic_same_title_section"],
        "parse_error_finish_reasons": sorted({p["finish_reason"] for p in perr}),
        "run1": facts["run1"],
    }
    rec = write_run_record(
        "ingest_litstatements", result_summary=summary, passed=True, data_path=a.tarball, output_path=r2.ART,
        data_sha256=None if a.tarball else r2.TARBALL_SHA256,
        config_snapshot={"source": "litstatements_run2_evidence.tar.gz (extracted)", "source_tarball_sha256": r2.TARBALL_SHA256,
                         "excluded": list(r2.EXCLUDED_NAMES), "run_executed_on": "Polaris; this record is the local ingest, not the run",
                         "model_calls": 0},
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
