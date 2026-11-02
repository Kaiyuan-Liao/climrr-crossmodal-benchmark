#!/usr/bin/env python3
"""Pilot P2b-fix A: region-string classification v2 (D-047a, amending D-047).

Reads `artifacts/litstatements/run2/statements_ingested.jsonl`, the pinned NCA5 map and
`region_match_exclusions_v1.yaml`. Writes:

- `artifacts/litstatements/run2/region_strings_v2.csv` --- every distinct (region string, scope)
  of the 747 entering statements with its count, the v2 classification, the `us_subregion`
  qualifier, the rule that fired and the v1 classification beside it (inspection file, generated);
- `artifacts/litstatements/run2/region_strings_v2_summary.json` --- class counts (rows, distinct
  strings, statements), v1 -> v2 transitions and the D-047 drops recovered.

`region_strings_v1.csv` is left as built (it is the D-047 evidence). Rules: `src/climrr/litgeo.py`
(version v2). Deterministic; no model call, no table value.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import itemseeds as sd  # noqa: E402
from climrr import litaggregate as la  # noqa: E402
from climrr import litgeo as lg  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

CSV_PATH = r2.ART / "region_strings_v2.csv"
SUMMARY_PATH = r2.ART / "region_strings_v2_summary.json"


def main() -> int:
    if not sd.NCA_MAP_PATH.is_file() or sha256_file(sd.NCA_MAP_PATH) != sd.NCA_MAP_SHA256:
        raise SystemExit(f"{repo_relative(sd.NCA_MAP_PATH)} is absent or differs from its pin {sd.NCA_MAP_SHA256}")
    ent = la.entering(sd.read_jsonl(r2.INGESTED_PATH))
    nca = sd.nca_map()
    gz, gz1 = lg.Gazetteer(nca), lg.Gazetteer(nca, version="v1")
    rows = lg.region_rows_v2(ent, gz, gz1)
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=lg.CSV_COLUMNS_V2, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    by_stmt = Counter(lg.classify(s["proposal"].get("region"), s["proposal"].get("region_scope"), gz)["class"] for s in ent)
    summary = {
        "version": lg.VERSION, "rule": lg.RULE_ID, "decisions": lg.DECISION,
        "inputs": {"statements_ingested_sha256": sha256_file(r2.INGESTED_PATH), "nca_map_sha256": sd.NCA_MAP_SHA256,
                   "exclusions_sha256": sha256_file(lg.EXCLUSIONS_PATH)},
        "region_strings_file": {"path": repo_relative(CSV_PATH), "sha256": sha256_file(CSV_PATH),
                                "rows_region_x_scope": len(rows), "distinct_region_strings": len({r["region"] for r in rows})},
        "entering_statements": len(ent),
        "statements_by_class": {c: by_stmt.get(c, 0) for c in lg.CLASSES},
        "rows_by_class": {c: sum(r["class"] == c for r in rows) for c in lg.CLASSES},
        "distinct_strings_by_class": {c: len({r["region"] for r in rows if r["class"] == c}) for c in lg.CLASSES},
        "us_subregion_qualifiers": dict(sorted(Counter(r["qualifier"] for r in rows if r["class"] == "us_subregion"
                                                       for _ in range(r["count"])).items())),
        "d047_drops": lg.recovered_d047a(ent, gz, gz1),
    }
    r2.write_json(SUMMARY_PATH, summary)
    rec = write_run_record(
        "build_region_strings_v2", result_summary=summary, passed=True, data_path=r2.INGESTED_PATH, output_path=CSV_PATH,
        config_snapshot={"geo_version": lg.VERSION, "rule": lg.RULE_ID, "us_names": list(lg.US_NAMES),
                         "national_extent": sorted(lg.NATIONAL_EXTENT), "directional": sorted(lg.DIRECTIONAL),
                         "regional": sorted(lg.REGIONAL), "exclusions_sha256": sha256_file(lg.EXCLUSIONS_PATH), "model_calls": 0},
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
