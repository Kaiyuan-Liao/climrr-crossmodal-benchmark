#!/usr/bin/env python3
"""Pilot P2a Phases D and F: the review workbook, the SEEDS CSV and the generated docs/LITSTATEMENTS_RUN2.md.

Reads the run-2 ingest (`artifacts/litstatements/run2/`), `clusters_v1.jsonl` and its
summary, `item_seeds_v1.jsonl` (gitignored; checked against the hash in its summary) and
its summary. Writes `artifacts/benchmark/review/P2a_clusters_and_seeds_v1.xlsx` (gitignored),
the tracked `P2a_seeds_v1.csv` (the SEEDS sheet) and `docs/LITSTATEMENTS_RUN2.md`.
Rules: `src/climrr/p2a_review.py`. No model call, no table value.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import litaggregate as la  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr import p2a_review as rv  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.xlsxlite import write_xlsx  # noqa: E402


def main() -> int:
    man, meta, perr, cs, ss, agent_sha = rv.doc_inputs()
    if sha256_file(sd.SEEDS_PATH) != ss["seeds_file"]["sha256"]:
        raise SystemExit("item_seeds_v1.jsonl differs from the hash in its summary; rerun scripts/build_item_seeds.py")
    if sha256_file(la.CLUSTERS_PATH) != cs["clusters_file"]["sha256"]:
        raise SystemExit("clusters_v1.jsonl differs from the hash in its summary")
    seeds = sd.read_jsonl(sd.SEEDS_PATH)
    clusters = sd.read_jsonl(la.CLUSTERS_PATH)
    records = sd.read_jsonl(r2.INGESTED_PATH)

    sheets = rv.workbook_sheets(man, cs, ss, seeds, clusters, records, perr)
    write_xlsx(rv.WORKBOOK_PATH, sheets)
    seed_rows = next(rows for name, rows, _ in sheets if name == "SEEDS")
    rv.SEEDS_CSV_PATH.write_text(rv.seeds_csv(seed_rows), encoding="utf-8")
    rv.DOC_PATH.write_text(rv.render_doc(man, meta, perr, cs, ss, agent_sha), encoding="utf-8")

    result = {"sheets": {name: len(rows) - 1 for name, rows, _ in sheets},
              "workbook_sha256": sha256_file(rv.WORKBOOK_PATH), "seeds_csv_sha256": sha256_file(rv.SEEDS_CSV_PATH),
              "doc_sha256": sha256_file(rv.DOC_PATH)}
    rec = write_run_record(
        "build_p2a_review", result_summary=result, passed=True, data_path=sd.SEEDS_PATH, output_path=rv.WORKBOOK_PATH,
        config_snapshot={"clusters_sha256": cs["clusters_file"]["sha256"], "seeds_sha256": ss["seeds_file"]["sha256"],
                         "manifest_sha256": sha256_file(r2.MANIFEST_PATH), "model_calls": 0},
    )
    print(json.dumps(result, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
