#!/usr/bin/env python3
"""Work package P5b, part A: ingest LITCORPUS-03 infra extraction run 1 and its query runs (D-074; D-070a, D-070b).

Takes `infra_run1_evidence.tar.gz` extracted outside the repository (and, optionally, the tarball itself, checked
against its SHA-256). Verifies every fact the work package states (`climrr.litstatements_infra1.verify_source`) and fails
on any difference; copies the run files and every `result.json` into `artifacts/litstatements/infra_run1/`, the corpus
evidence (redacted where it holds an absolute path) into `artifacts/literature/litcorpus03/`, and pins the v3
`candidates.json` as `data/metadata/softqa/infra_candidates_v1.json`; re-derives the candidates from the delivered
`paper_hits.jsonl` and `basis_b_only.json` (`climrr.infra_lexicon.verify_candidates_3`); writes
`statements_ingested.jsonl` (`LS3-` ids, evidence roles, `impact_candidate`, statement family), `independence_v2.json`
(D-046 over the 572 papers), `breakdowns.json` and the two manifests.

Rerunnable: every copy must be byte-identical, and an existing manifest keeps its `ingested_at`. No model call, no table value.

    python scripts/ingest_litstatements_infra1.py --src <extracted dir> --tarball <path to infra_run1_evidence.tar.gz>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import infra_lexicon as il  # noqa: E402
from climrr import itemseeds as sd  # noqa: E402
from climrr import litgeo as lg  # noqa: E402
from climrr import litstatements_infra1 as ir  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted infra_run1_evidence.tar.gz")
    ap.add_argument("--tarball", type=Path, help="the tarball itself, checked against its SHA-256")
    a = ap.parse_args()

    if a.tarball and sha256_file(a.tarball) != ir.TARBALL_SHA256:
        raise SystemExit(f"{a.tarball.name} is not the delivered tarball {ir.TARBALL_SHA256}")
    facts = ir.verify_source(a.src)
    cand_errors = il.verify_candidates_3(json.loads((a.src / "runs/infra_lexicon_v3/candidates.json").read_text(encoding="utf-8")),
                                         a.src / "runs/infra_lexicon_v3/paper_hits.jsonl",
                                         a.src / "runs/infra_lexicon_v3/basis_b_only.json")
    if cand_errors:
        raise SystemExit("v3 candidates do not re-derive from paper_hits.jsonl: " + "; ".join(cand_errors[:5]))
    copied = ir.copy_run(a.src)
    redactions = ir.copy_corpus_evidence(a.src)

    records = ir.ingested_records()
    if len(records) != ir.RUN_FACTS["statements"]:
        raise SystemExit(f"{len(records)} ingested statements, expected {ir.RUN_FACTS['statements']}")
    ir.write_jsonl(ir.INGESTED_PATH, records)
    indep = ir.independence(a.src)
    ir.write_json(ir.INDEPENDENCE_PATH, indep)
    report = ir.breakdowns(records, lg.Gazetteer(sd.nca_map()))
    ir.write_json(ir.REPORT_PATH, report)

    prev = json.loads(ir.MANIFEST_PATH.read_text(encoding="utf-8")) if ir.MANIFEST_PATH.exists() else {}
    man = ir.manifest(facts, ir.excluded_files(a.src), records, prev.get("ingested_at"))
    ir.write_json(ir.MANIFEST_PATH, man)
    ir.write_json(ir.REDACTIONS_PATH, redactions)
    prev_c = json.loads(ir.CORPUS_MANIFEST_PATH.read_text(encoding="utf-8")) if ir.CORPUS_MANIFEST_PATH.exists() else {}
    cman = ir.corpus_manifest(a.src, redactions, prev_c.get("ingested_at"))
    ir.write_json(ir.CORPUS_MANIFEST_PATH, cman)

    summary = {
        "manifest_sha256": sha256_file(ir.MANIFEST_PATH), "corpus_manifest_sha256": sha256_file(ir.CORPUS_MANIFEST_PATH),
        "statements_ingested_sha256": sha256_file(ir.INGESTED_PATH), "independence_v2_sha256": sha256_file(ir.INDEPENDENCE_PATH),
        "breakdowns_sha256": sha256_file(ir.REPORT_PATH), "infra_candidates_v1_sha256": sha256_file(ir.CANDIDATES_PIN_PATH),
        "files_copied_this_run": copied, "files_in_manifest": len(man["files"]), "excluded_files": len(man["excluded_files"]),
        "redacted_files": sorted(redactions["files"]), "counts": man["counts"],
        "independence": {k: indep[k] for k in ("papers_n", "canonical_papers_n", "merged_groups", "by_basis")},
        "candidates_verify_3": "pass", "breakdowns": {k: report[k] for k in ("passing_by_type", "passing_impact_by_asset_family",
                                                                             "passing_impact_naming_us_place", "passing_by_family_basis")},
    }
    summary["breakdowns"]["passing_impact_naming_us_place"] = {k: v for k, v in report["passing_impact_naming_us_place"].items()
                                                               if k != "statements"}
    rec = write_run_record(
        "ingest_litstatements_infra1", result_summary=summary, passed=True, data_path=a.tarball, output_path=ir.ART,
        data_sha256=None if a.tarball else ir.TARBALL_SHA256,
        config_snapshot={"source": f"{ir.TARBALL_NAME} (extracted)", "source_tarball_sha256": ir.TARBALL_SHA256,
                         "excluded": list(ir.EXCLUDED_NAMES), "not_copied": list(ir.NOT_COPIED), "decision": ir.DECISION,
                         "run_executed_on": "Polaris; this record is the local ingest, not the run", "model_calls": 0},
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
