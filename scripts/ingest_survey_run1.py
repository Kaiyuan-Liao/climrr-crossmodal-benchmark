#!/usr/bin/env python3
"""Track B survey run 1: ingest the Polaris output as a diagnostic artifact (D-025, D-026).

Takes `survey_run1.tar.gz` extracted outside the repository. Verifies it (tools
equal the tracked v3 files; inventory, context clause and index identity pinned;
every row's counts re-derived from its id files), copies `survey/run1/` into
`artifacts/literature/survey/run1/` except `_duckdb_tmp` directories and the
header-only `topical/hits.csv` files, copies the log beside it, writes
`manifest.csv`, pins it in `data/manifest.json` under `diagnostics`, and
generates `docs/CONCEPT_COVERAGE_SURVEY.md` from the ingested rows.

Rerunnable: an existing copy must be byte-identical to the delivered files.
Changes no concept map, no column status, no production query.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import coveragesurvey as cs  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

AMENDMENT = {
    "date": "2026-10-20",
    "milestone": "Track B Stage 2b/2c",
    "change": ("Added the diagnostics block pinning Track B survey run 1 "
               "(artifacts/literature/survey/run1/manifest.csv). A diagnostic, not a corpus: "
               "not under external_corpora. Existing entries unchanged."),
    "decision_ref": "D-025, D-026",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted survey_run1.tar.gz")
    ap.add_argument("--tarball", type=Path, help="survey_run1.tar.gz, to record its SHA-256")
    a = ap.parse_args()

    cs.verify_source(a.src)
    cs.SURVEY_DIR.mkdir(parents=True, exist_ok=True)
    copied = cs.copy_run(a.src)
    rows = cs.verify_run(cs.RUN_DIR)  # the ingested copy, re-checked

    text = cs.manifest_text()
    cs.RUN_MANIFEST.write_text(text, encoding="utf-8")
    manifest_sha = sha256_file(cs.RUN_MANIFEST)
    lines = text.splitlines()[1:]
    n_files = len(lines)
    total = sum(int(ln.split(",")[-2]) for ln in lines)

    data = json.loads(cs.MANIFEST.read_text(encoding="utf-8"))
    entry = cs.manifest_entry(manifest_sha, n_files, total, copied["skipped_header_only_hits"])
    diags = [d for d in data.get("diagnostics", []) if d["diagnostic_id"] != cs.DIAGNOSTIC_ID]
    data["diagnostics"] = diags + [entry]
    if AMENDMENT not in data["amendments"]:
        data["amendments"].append(AMENDMENT)
    cs.MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    cs.DOC_PATH.write_text(cs.render_doc(rows, manifest_sha), encoding="utf-8")

    summary = {
        "n_rows": len(rows),
        "n_ok": sum(r["row"]["status"] == "ok" for r in rows),
        "n_error": sum(r["row"]["status"] == "error" for r in rows),
        "n_files_ingested": n_files,
        "total_bytes": total,
        "manifest_sha256": manifest_sha,
        "header_only_hits_not_copied": len(copied["skipped_header_only_hits"]),
        "duckdb_tmp_dirs_removed": len(copied["skipped_duckdb_tmp"]),
        "doc_sha256": sha256_file(cs.DOC_PATH),
        "counts": {r["row"]["concept_id"]: [r["row"]["topical_only_count"], r["row"]["context_filtered_count"],
                                            r["row"]["status"]] for r in rows},
        "label": cs.LABEL,
    }
    rec = write_run_record(
        "ingest_survey_run1",
        result_summary=summary,
        passed=True,
        data_path=a.tarball,
        output_path=cs.RUN_DIR,
        config_snapshot={
            "source": a.tarball.name if a.tarball else "extracted survey_run1.tar.gz",
            "tools_sha256": cs.TOOL_SHA256,
            "run_executed_on": "Polaris (polaris-login-01); this record is the local ingest, not the run",
            "excluded": "_duckdb_tmp directories; header-only topical/hits.csv",
        },
    )
    print(json.dumps(summary, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
