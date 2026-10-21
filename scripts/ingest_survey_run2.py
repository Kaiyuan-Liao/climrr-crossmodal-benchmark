#!/usr/bin/env python3
"""Track B survey run 2 (family level): ingest the Polaris output as a diagnostic (D-025, D-026, D-027).

Takes `survey_run2.tar.gz` extracted outside the repository. Verifies it (log
START line against the v4 driver, prompt F, normalization table, inventory,
context clause and index identity; every row's pins, `status:
candidate_family`, counts re-derived from its id files, and measure counts equal
to the ingested run-1 rows), copies `survey/run2/` into
`artifacts/literature/survey/run2/` except the header-only `topical/hits.csv`
files, copies the log beside it, writes `manifest.csv`, pins it in
`data/manifest.json` under `diagnostics`, and regenerates
`docs/CONCEPT_COVERAGE_SURVEY.md` from runs 1 and 2.

Run 1 is read, never written: its copy and `manifest.csv` must be unchanged
before and after. Rerunnable: an existing copy must be byte-identical.
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
from climrr import coveragesurvey_run2 as cs2  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

AMENDMENT = {
    "date": "2026-10-21",
    "milestone": "Track B Stage 2 run 2",
    "change": ("Added TRACKB-SURVEY-RUN2 to the diagnostics block (artifacts/literature/survey/run2/manifest.csv; "
               "family level, candidate_family). A diagnostic, not a corpus: not under external_corpora. "
               "TRACKB-SURVEY-RUN1 and every other entry unchanged."),
    "decision_ref": "D-025, D-026, D-027",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted survey_run2.tar.gz")
    ap.add_argument("--tarball", type=Path, help="survey_run2.tar.gz, checked against its SHA-256")
    a = ap.parse_args()

    if a.tarball and sha256_file(a.tarball) != cs2.TARBALL_SHA256:
        raise SystemExit(f"{a.tarball} is not the delivered tarball {cs2.TARBALL_SHA256}")
    run1_before = sha256_file(cs.RUN_MANIFEST)
    if cs.manifest_text() != cs.RUN_MANIFEST.read_text(encoding="utf-8"):
        raise SystemExit("run-1 copy differs from its manifest.csv; refusing to ingest run 2")

    cs2.verify_source(a.src)
    copied = cs2.copy_run(a.src)
    rows = cs2.verify_run(cs2.RUN_DIR)  # the ingested copy, re-checked

    text = cs.manifest_text(cs2.RUN_DIR)
    cs2.RUN_MANIFEST.write_text(text, encoding="utf-8")
    manifest_sha = sha256_file(cs2.RUN_MANIFEST)
    lines = text.splitlines()[1:]
    n_files = len(lines)
    total = sum(int(ln.split(",")[-2]) for ln in lines)

    data = json.loads(cs.MANIFEST.read_text(encoding="utf-8"))
    entry = cs2.manifest_entry(manifest_sha, n_files, total, copied["skipped_header_only_hits"])
    diags = [d for d in data.get("diagnostics", []) if d["diagnostic_id"] != cs2.DIAGNOSTIC_ID]
    data["diagnostics"] = diags + [entry]
    if AMENDMENT not in data["amendments"]:
        data["amendments"].append(AMENDMENT)
    cs.MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    cs.DOC_PATH.write_text(cs2.render_full_doc(), encoding="utf-8")

    run1_after = sha256_file(cs.RUN_MANIFEST)
    if run1_after != run1_before or cs.manifest_text() != cs.RUN_MANIFEST.read_text(encoding="utf-8"):
        raise SystemExit("run 1 changed during the run-2 ingest")

    summary = {
        "n_rows": len(rows),
        "n_files_ingested": n_files,
        "total_bytes": total,
        "manifest_sha256": manifest_sha,
        "run1_manifest_sha256_unchanged": run1_after,
        "header_only_hits_not_copied": len(copied["skipped_header_only_hits"]),
        "forms": cs2.form_stats(rows),
        "doc_sha256": sha256_file(cs.DOC_PATH),
        "side_by_side": {r["row"]["concept_id"]: {
            "measure": [r["row"]["measure_topical_only_count"], r["row"]["measure_context_filtered_count"]],
            "candidate_family": r["row"]["candidate_family"],
            "family": [r["row"]["family_topical_only_count"], r["row"]["family_context_filtered_count"]]}
            for r in rows},
        "label": cs2.FAMILY_LABEL,
    }
    rec = write_run_record(
        "ingest_survey_run2",
        result_summary=summary,
        passed=True,
        data_path=a.tarball,
        output_path=cs2.RUN_DIR,
        config_snapshot={
            "source": a.tarball.name if a.tarball else "extracted survey_run2.tar.gz",
            "source_tarball_sha256": cs2.TARBALL_SHA256,
            "driver_sha256": cs2.DRIVER_SHA256,
            "prompt_f_sha256": cs2.PROMPT_F_SHA256,
            "normalization_table_sha256": cs2.NORM_TABLE_SHA256,
            "run_executed_on": "Polaris; this record is the local ingest, not the run",
            "excluded": "header-only topical/hits.csv",
        },
    )
    print(json.dumps(summary, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
