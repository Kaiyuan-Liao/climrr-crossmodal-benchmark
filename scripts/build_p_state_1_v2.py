#!/usr/bin/env python3
"""D-018: write `P-STATE-1.v2.json`, a versioned provenance correction of P-STATE-1.

v1 states its horizons only as the dictionary labels "Historical" and
"End-Century". v2 adds the year windows those labels denote, citing the
dictionary lines that state them, and changes nothing else that carries a
number. `P-STATE-1.json` (v1) is read, never written: the frozen M5-WP1 input
points at it and must keep verifying.

The windows rest on the same reading P-CELL-1 and P-COUNTY-1 already use for
the same labels --- that a field entry's horizon label means the decade the
front matter defines at lines 101-102 --- and carry the same status.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr.checksums import sha256_file  # noqa: E402
from climrr.compat import prototype_file, record_sha256  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

DICTIONARY_TEXT = REPO_ROOT / "data" / "metadata" / "dictionary_extracted.txt"
V1 = prototype_file("P-STATE-1")
V2 = V1.with_name("P-STATE-1.v2.json")
REFERENCE = prototype_file("P-CELL-1")

#: Per role: the window, and the dictionary lines that state it. Line 101 is the
#: span IC-008 (P-CELL-1's and P-COUNTY-1's future column) cites for 2085-2094;
#: the range runs onto line 102, which also states the historical decade.
WINDOWS = {
    "baseline": {"start": 1995, "end": 2004, "lines": [102]},
    "future": {"start": 2085, "end": 2094, "lines": [101, 102]},
}
ASSUMPTION = {
    "baseline": ("That `Historical` in the field entry (line 680) means the historical period "
                 "(1995 to 2004) the front matter defines at line 102; the field entry gives no years."),
    "future": ("That `End-Century` in the field entry (line 695) means the end-of-century period "
               "(2085 to 2094) the front matter defines at lines 101-102; the field entry gives no years. "
               "The same reading IC-008 records for P-CELL-1 and P-COUNTY-1."),
}


def main() -> int:
    v1 = json.loads(V1.read_text(encoding="utf-8"))
    ref = json.loads(REFERENCE.read_text(encoding="utf-8"))
    lines = DICTIONARY_TEXT.read_text(encoding="utf-8").splitlines()
    v2 = copy.deepcopy(v1)

    for role, w in WINDOWS.items():
        per = v2["T"]["per_role"][role]
        ref_role = ref["T"]["per_role"][role]
        spans = [{"line": n, "quote": lines[n - 1].strip()} for n in w["lines"]]
        joined = " ".join(s["quote"] for s in spans)
        for year in (str(w["start"]), str(w["end"])):
            if year not in joined:
                print(f"FAIL: {role}: {year} not in cited lines {w['lines']}", file=sys.stderr)
                return 1
        per["value_v1"] = per["value"]
        per["value"] = ref_role["value"]  # the exact label string P-CELL-1 and P-COUNTY-1 carry
        per["window"] = {"start": w["start"], "end": w["end"]}
        per["window_spans"] = spans
        per["window_status"] = ref_role["status"]
        per["window_status_inherited_from"] = f"P-CELL-1 T.per_role.{role}.status (same label, same reading)"
        per["window_rests_on_assumption"] = ASSUMPTION[role]

    v2["version"] = 2
    v2["supersedes"] = "P-STATE-1 v1"
    v2["amendment"] = "D-018"
    v2["amendment_note"] = (
        "Versioned provenance correction (D-018): explicit year windows added to T.per_role.baseline "
        "and T.per_role.future, with dictionary spans. No ClimRR value changed. The generated "
        "`description`, `description_clauses` and `literature_probe` are v1's, unchanged: they name "
        "the horizons by their dictionary labels only.")
    v2["v1_file_sha256"] = sha256_file(V1)
    v2["v1_record_sha256"] = record_sha256(v1)
    v2["P"]["per_field"]["T.window"] = v2["T"]["per_role"]["future"]["window_status"]

    for key in ("V", "D", "M"):
        if v2[key] != v1[key]:
            print(f"FAIL: {key} differs from v1", file=sys.stderr)
            return 1

    if V2.exists():
        if json.loads(V2.read_text(encoding="utf-8")) != v2:
            print("FAIL: P-STATE-1.v2.json exists and differs from a rebuild", file=sys.stderr)
            return 1
        action = "verified"
    else:
        V2.write_text(json.dumps(v2, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        action = "written"
    sha = sha256_file(V2)
    print(f"  {action}: {repo_relative(V2)} sha256={sha}")
    record = write_run_record(
        "build_p_state_1_v2",
        result_summary={"action": action, "v2_sha256": sha, "v2_record_sha256": record_sha256(v2),
                        "v1_sha256": v2["v1_file_sha256"], "windows": WINDOWS},
        passed=True,
        data_path=V1,
        output_path=V2,
        config_snapshot={"dictionary_text_sha256": sha256_file(DICTIONARY_TEXT),
                         "reference_prototype": "P-CELL-1", "reference_sha256": sha256_file(REFERENCE)},
    )
    print(f"Run record: {repo_relative(record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
