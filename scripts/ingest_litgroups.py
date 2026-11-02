#!/usr/bin/env python3
"""Pilot P2b-ingest Phase A: ingest grouping run 2 (litgroup_agent v3, Polaris, Sophia vLLM; D-051, D-052).

Takes `litgroups_run2_evidence.tar.gz` extracted outside the repository. Verifies it against
every fact the work package states (hashes, agent / template / corrective-template SHA-256,
budget, 11 partitions in 23 chunks, 23 pass, 15 corrective turns of which 12 passed first time
and 3 on a second attempt with identical configuration, 239 groups, 155 singletons, 747
statements each exactly once, endpoint, source commit, logs) and fails on any difference.
Copies the run files and the per-chunk results into `artifacts/litgroups/run2/` (prompts and raw
responses: SHA-256 in `manifest.json` only), writes `groups_enriched.jsonl` (`src/climrr/litgroups_run2.py`),
its summary, and `manifest.json`. Run 1 is recorded as superseded (budget), never ingested.

Rerunnable: every copy must be byte-identical, and an existing manifest keeps its `ingested_at`.
No model call, no table value.

    python scripts/ingest_litgroups.py --src <extracted tarball> --tarball <litgroups_run2_evidence.tar.gz>
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
from climrr import litgroups_run2 as g2  # noqa: E402
from climrr import litindependence as li  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True, type=Path, help="the extracted litgroups_run2_evidence.tar.gz")
    ap.add_argument("--tarball", type=Path, help="the tarball itself, checked against its SHA-256")
    a = ap.parse_args()

    if a.tarball and sha256_file(a.tarball) != g2.TARBALL_SHA256:
        raise SystemExit(f"{a.tarball.name} is not the delivered tarball {g2.TARBALL_SHA256}")
    partitions = lgr.read_groups(lgr.PARTITIONS_PATH)  # one JSON object per line
    facts = g2.verify_source(a.src, partitions)
    copied = g2.copy_run(a.src)

    records = sd.read_jsonl(r2.INGESTED_PATH)
    indep = json.loads(li.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
    enriched = g2.enrich(lgr.read_groups(g2.ART / "groups.jsonl"), partitions, records, indep, lg.Gazetteer(sd.nca_map()))
    r2.write_jsonl(g2.ENRICHED_PATH, enriched)
    summary = g2.summarise(enriched)
    if summary["labels_with_digit_not_in_members"]:
        raise SystemExit(f"labels with a digit no member has: {summary['labels_with_digit_not_in_members']}")
    r2.write_json(g2.ENRICHED_SUMMARY_PATH, summary)

    previous = json.loads(g2.MANIFEST_PATH.read_text(encoding="utf-8")) if g2.MANIFEST_PATH.exists() else {}
    man = g2.manifest(facts, g2.excluded_files(a.src), previous.get("ingested_at"))
    r2.write_json(g2.MANIFEST_PATH, man)

    result = {"manifest_sha256": sha256_file(g2.MANIFEST_PATH), "files_copied_this_run": copied,
              "files_in_manifest": len(man["files"]), "excluded_files": len(man["excluded_files"]),
              "enriched_sha256": sha256_file(g2.ENRICHED_PATH), "counts": man["counts"],
              "second_attempt_chunks": man["second_attempt_chunks"], "report": summary, "run1": facts["run1"]["partitions_pass"]}
    rec = write_run_record(
        "ingest_litgroups", result_summary=result, passed=True, data_path=a.tarball, output_path=g2.ART,
        data_sha256=None if a.tarball else g2.TARBALL_SHA256,
        config_snapshot={"source": f"{g2.TARBALL_NAME} (extracted)", "source_tarball_sha256": g2.TARBALL_SHA256,
                         "excluded": list(g2.EXCLUDED_NAMES), "geography": lg.VERSION,
                         "run_executed_on": "Polaris; this record is the local ingest, not the run", "model_calls": 0},
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
