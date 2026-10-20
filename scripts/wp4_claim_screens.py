#!/usr/bin/env python3
"""M4-WP4r1: three descriptive screens over reader 1's claims --- not a compatibility run.

1. **US geography**: the claim's `geography` value (status not `unknown`) names a US
   place, by the reader-1 place-term list below (states, cities, regions as the papers
   name them). Explicit and inferred counted separately.
2. **Pilot concept term**: an approved C-2 family term (`climrr.conceptmap.c2_terms`,
   `approved_lexical` only, `approved_family_term` forms masking) occurs, by the
   project boundary rule, inside the claim's `concept` value. This is the M4-WP2
   screen; it is **not** C-2 compatibility and nothing is compared with a prototype.
3. **Scenario**: the claim's `scenario` is not `unknown`; `named` if it names an
   RCP, SSP or SRES pathway.

Writes `artifacts/literature/wp4_claim_screens.json` and a run record.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import conceptmap  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

LIT = REPO_ROOT / "artifacts" / "literature"
SAMPLE = LIT / "wp4_sample.json"
CLAIMS_DIR = LIT / "wp4_claims"
OUT = LIT / "wp4_claim_screens.json"

#: Reader-1 list of US place names as they occur in the sample's geography values.
US_TOKENS = (
    "United States", "U.S.", "US", "USA", "contiguous US", "California", "Oklahoma", "Texas", "Kansas",
    "Nebraska", "Washington", "Maine", "Idaho", "Arizona", "Nevada", "Minnesota", "Florida", "Mississippi",
    "Chicago", "Salt Lake City", "Portland", "Medford", "San Diego", "Malheur", "Lake Mendocino",
    "Riverside County", "Midwest", "Southern High Plains", "Southern Great Plains", "West region",
    "District of Columbia",
)
NAMED_SCENARIO = re.compile(r"\b(RCP|SSP|SRES|A1B|A2|B1)\b", re.IGNORECASE)


def us_hits(value: str) -> list[str]:
    return [t for t in US_TOKENS if re.search(r"(?<![A-Za-z])" + re.escape(t) + r"(?![A-Za-z])", value)]


def main() -> int:
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    entries = conceptmap.load()
    families = [e for e in entries if e["level"] == "family" and e["status"] == "approved_lexical"]
    masks = conceptmap.family_term_masks(entries)
    rows = []
    for s in sample["selected"]:
        rec = json.loads((CLAIMS_DIR / f"{s['lit2_id']}.json").read_text(encoding="utf-8"))
        for c in rec.get("claims", []):
            geo, con, scen = c["geography"], c["concept"], c["scenario"]
            us = us_hits(geo["value"]) if geo["status"] != "unknown" else []
            masked = [span for m in masks for span in conceptmap.find_term(m, con["value"])]
            c2 = []
            for e in families:
                for term, dec in conceptmap.c2_terms(e):
                    for a, b in conceptmap.find_term(term, con["value"]):
                        if not any(ma <= a and b <= mb for ma, mb in masked):
                            c2.append({"family": e["canonical_id"], "term": term, "decision_id": dec, "span": [a, b]})
            rows.append({
                "claim_id": c["claim_id"], "arm": s["arm"], "claim_type": c["claim_type"],
                "geography": geo["value"], "geography_status": geo["status"], "geography_role": geo["role"],
                "us_geography_tokens": us,
                "concept": con["value"], "concept_status": con["status"], "pilot_family_terms_in_concept": c2,
                "scenario": scen["value"], "scenario_status": scen["status"],
                "scenario_named": bool(scen["status"] != "unknown" and NAMED_SCENARIO.search(scen["value"])),
            })
    totals = {
        "claims": len(rows),
        "us_geography": sum(bool(r["us_geography_tokens"]) for r in rows),
        "us_geography_explicit": sum(bool(r["us_geography_tokens"]) and r["geography_status"] == "explicit" for r in rows),
        "us_geography_inferred": sum(bool(r["us_geography_tokens"]) and r["geography_status"] == "inferred" for r in rows),
        "us_geography_by_type": {t: sum(bool(r["us_geography_tokens"]) and r["claim_type"] == t for r in rows)
                                 for t in sorted({r["claim_type"] for r in rows})},
        "pilot_family_term_in_concept": sum(bool(r["pilot_family_terms_in_concept"]) for r in rows),
        "pilot_family_term_in_concept_by_family": {e["canonical_id"]: sum(any(h["family"] == e["canonical_id"] for h in r["pilot_family_terms_in_concept"]) for r in rows) for e in families},
        "pilot_family_term_and_us_geography": sum(bool(r["pilot_family_terms_in_concept"]) and bool(r["us_geography_tokens"]) for r in rows),
        "scenario_not_unknown": sum(r["scenario_status"] != "unknown" for r in rows),
        "scenario_named": sum(r["scenario_named"] for r in rows),
    }
    inputs = {repo_relative(p): sha256_file(p) for p in [SAMPLE, LIT / "wp4_claims_summary.json", conceptmap.CONCEPT_MAP_PATH]}
    OUT.write_text(json.dumps({
        "artifact": "M4-WP4 reader-1 claim screens (descriptive; not a compatibility run)",
        "screens": __doc__.split("\n\n")[1],
        "us_tokens": list(US_TOKENS),
        "boundary_rule": conceptmap.BOUNDARY_RULE,
        "masks": masks,
        "input_sha256": inputs,
        "totals": totals,
        "claims": rows,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for r in rows:
        if r["us_geography_tokens"] or r["pilot_family_terms_in_concept"] or r["scenario_status"] != "unknown":
            print(f"  {r['claim_id']:<16} US={r['us_geography_tokens']} ({r['geography_status']})  "
                  f"C2={[h['term'] for h in r['pilot_family_terms_in_concept']]}  scen={r['scenario_status']}:{r['scenario'][:40]}")
    print(f"  totals: {json.dumps(totals)}")
    rec = write_run_record("wp4_claim_screens", result_summary=totals, passed=True, data_path=SAMPLE,
                           output_path=OUT, config_snapshot={"inputs": inputs})
    print(f"Run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
