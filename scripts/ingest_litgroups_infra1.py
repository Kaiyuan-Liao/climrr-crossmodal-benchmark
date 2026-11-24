#!/usr/bin/env python3
"""Work package P5c, parts A and B: ingest the infra grouping run (litgroup_agent v3.1, Polaris, Sophia vLLM; D-076) and
export the COORDINATOR review list of the impact groups.

Takes `litgroups_infra_run1_evidence.tar.gz` extracted outside the repository. Verifies it against every fact the work
package states and fails on any difference (`climrr.litgroups_infra_run1.verify_source`). Copies the run files and the
per-chunk results into `artifacts/litgroups/infra_run1/` (prompts and raw responses: SHA-256 in `manifest.json` only), writes
`groups_enriched.jsonl` (D-046 strengths over the infra papers, geography v2, asset class from the partition and the
members, impact mechanism / outcome from the members), its summary and `manifest.json`. Part B: writes
`artifacts/benchmark/review/P5_impact_groups_review_v1.csv` --- every group and singleton tagged `hazard_impact_on_asset`
or `impact_or_exposure`, empty disposition columns, the label keyword screens (markers, not dispositions).

Rerunnable: every copy must be byte-identical, and an existing manifest keeps its `ingested_at`. No model call, no table
value.

    python scripts/ingest_litgroups_infra1.py --src <extracted tarball> --tarball <litgroups_infra_run1_evidence.tar.gz>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import litgeo as lg  # noqa: E402
from climrr import litgroups as lgr  # noqa: E402
from climrr import litgroups_infra as lgi  # noqa: E402
from climrr import litgroups_infra_run1 as gi  # noqa: E402
from climrr import litstatements_infra1 as ir  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted litgroups_infra_run1_evidence.tar.gz")
    ap.add_argument("--tarball", type=Path, help="the tarball itself, checked against its SHA-256")
    a = ap.parse_args()

    if a.tarball and sha256_file(a.tarball) != gi.TARBALL_SHA256:
        raise SystemExit(f"{a.tarball.name} is not the delivered tarball {gi.TARBALL_SHA256}")
    partitions = lgr.read_groups(lgi.PARTITIONS_PATH)  # one JSON object per line
    facts = gi.verify_source(a.src, partitions)
    copied = gi.copy_run(a.src)

    records = sd.read_jsonl(ir.INGESTED_PATH)
    indep = json.loads(ir.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    enriched = gi.enrich(lgr.read_groups(gi.ART / "groups.jsonl"), partitions, records, indep, lg.Gazetteer(sd.nca_map()))
    ir.write_jsonl(gi.ENRICHED_PATH, enriched)
    summary = gi.summarise(enriched)
    if summary["labels_with_digit_not_in_members"]:
        raise SystemExit(f"labels with a digit no member has: {summary['labels_with_digit_not_in_members']}")
    summary["hazard_impact_on_asset_labels"] = gi.hia_label_listing(enriched)
    ir.write_json(gi.ENRICHED_SUMMARY_PATH, summary)

    rows = gi.review_rows(enriched)
    gi.write_review_csv(gi.REVIEW_PATH, rows)

    previous = json.loads(gi.MANIFEST_PATH.read_text(encoding="utf-8")) if gi.MANIFEST_PATH.exists() else {}
    man = gi.manifest(facts, gi.excluded_files(a.src), previous.get("ingested_at"))
    ir.write_json(gi.MANIFEST_PATH, man)

    flagged = [x for fam in summary["hazard_impact_on_asset_labels"].values() for xs in fam.values() for x in xs if x["flags"]]
    result = {"manifest_sha256": sha256_file(gi.MANIFEST_PATH), "files_copied_this_run": copied,
              "files_in_manifest": len(man["files"]), "excluded_files": len(man["excluded_files"]),
              "enriched_sha256": sha256_file(gi.ENRICHED_PATH), "enriched_summary_sha256": sha256_file(gi.ENRICHED_SUMMARY_PATH),
              "counts": man["counts"],
              "review_csv": {"path": repo_relative(gi.REVIEW_PATH), "sha256": sha256_file(gi.REVIEW_PATH), "rows": len(rows),
                             "groups": sum(r["kind"] == "group" for r in rows), "singletons": sum(r["kind"] == "singleton" for r in rows)},
              "hazard_impact_on_asset_labels_flagged": len(flagged),
              "report": {k: v for k, v in summary.items() if k != "hazard_impact_on_asset_labels"}}
    rec = write_run_record(
        "ingest_litgroups_infra1", result_summary=result, passed=True, data_path=a.tarball, output_path=gi.ART,
        data_sha256=None if a.tarball else gi.TARBALL_SHA256,
        config_snapshot={"source": f"{gi.TARBALL_NAME} (extracted)", "source_tarball_sha256": gi.TARBALL_SHA256,
                         "excluded": list(gi.EXCLUDED_NAMES), "geography": lg.VERSION,
                         "label_screens": {k: rx.pattern for k, rx in gi.LABEL_SCREENS.items()},
                         "run_executed_on": "Polaris; this record is the local ingest, not the run", "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
