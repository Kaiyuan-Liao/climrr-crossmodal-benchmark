#!/usr/bin/env python3
"""M4-WP2 Phase 1, Phase C: classify every frozen retrieval hit, **after** reading.

The hit list in `artifacts/literature/wp2_candidates.json` was opened only once
reader 1's claims were built (`scripts/build_wp2_claims.py`). Each hit gets:

* `classification` --- `substantive`: the passage states something about the
  term's concept or place, and the paper treats that concept or place (studies,
  analyses, or reviews it over more than a list entry); `incidental`: an author
  surname, a citation or reference-list entry, an instrument-network name, a
  list entry, a passing mention, or a **different referent** under the same
  letters;
* `referent_matches_term` --- `false` where the matched letters name something
  else (e.g. `FWI` = fractional water index);
* a one-line reason;
* `in_promoted_claim_evidence` / `in_promoted_claim_support` --- **computed**,
  not judged: whether the hit's span lies inside any promoted claim's evidence
  or support span on the same path.

Each hit is re-sliced from the hash-verified source and must equal its recorded
`matched_text`. Written once; a later run verifies byte equality.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litingest  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import get as get_local_path  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

LIT = REPO_ROOT / "artifacts" / "literature"
CANDIDATES = LIT / "wp2_candidates.json"
MANIFEST = LIT / "corpus_manifest.json"
CLAIMS_DIR = LIT / "wp2_claims"
OUT = LIT / "wp2_hit_classification.json"

S, I = "substantive", "incidental"
WFI = "different referent: 'FWI' here is the Oklahoma Mesonet fractional water index (soil moisture), not a fire weather index"
MESONET = "the name of an instrument network (Oklahoma Mesonet), not a statement about Oklahoma"

#: (item_id, json_path, char_start) -> (classification, referent_matches_term, reason)
JUDGEMENTS: dict[tuple[str, str, int], tuple[str, bool, str]] = {
    # LIT-000166 --- SPITFIRE
    ("LIT-000166", "$.methods", 1953): (I, True, "one entry in a list of operational fire danger indices; the paper neither uses nor evaluates it"),
    ("LIT-000166", "$.methods", 2981): (I, False, "author surname in an in-text citation ('Stephens and Finney, 2002'), not the place"),
    # LIT-000519 --- DFHI, Sardinia
    ("LIT-000519", "$.abstract", 390): (I, True, "named as one example of short-term hazard indices"),
    ("LIT-000519", "$.introduction", 3810): (I, True, "one entry in a list of meteorological fire danger indices"),
    ("LIT-000519", "$.introduction", 5350): (S, True, "describes the FWI System as a subsystem of the Canadian Forest Fire Danger Rating System, in the paper's review of indices"),
    ("LIT-000519", "$.introduction", 5370): (S, True, "abbreviation in the same descriptive sentence as the previous hit"),
    ("LIT-000519", "$.introduction", 5449): (S, True, "states what the FWI System does (severity of fire from weather readings alone)"),
    ("LIT-000519", "$.introduction", 5787): (S, True, "states that the FBP System relies on FWI System outputs"),
    ("LIT-000519", "$.introduction", 6728): (S, True, "states that the JRC focused its development on the FWI system"),
    ("LIT-000519", "$.introduction", 7087): (I, True, "one entry in the list of indices the JRC compared"),
    ("LIT-000519", "$.introduction", 7266): (S, True, "states that the JRC built a daily FWI service on a 10 km grid"),
    ("LIT-000519", "$.introduction", 7405): (S, True, "states that the FWI performed better than other methods (promoted as claim C5, background)"),
    ("LIT-000519", "$.introduction", 8425): (I, True, "reference point in a sentence about the RISICO model"),
    ("LIT-000519", "$.introduction", 8445): (I, True, "abbreviation in the same RISICO sentence"),
    ("LIT-000519", "$.introduction", 15265): (S, True, "states that the JRC adopted the FWI for European fire danger maps although it uses no satellite data"),
    ("LIT-000519", "$.introduction", 15062): (I, True, "passing mention of where the method's predecessor (FPI) was validated; not an affiliation, not the study area (Sardinia)"),
    # LIT-001501 --- Southern Great Plains whiplash
    ("LIT-001501", "$.abstract", 1179): (S, True, "names the study's case-study region (Oklahoma and Texas panhandles)"),
    ("LIT-001501", "$.abstract", 419): (I, True, "another region where such transitions were studied by others"),
    ("LIT-001501", "$.introduction", 74): (S, True, "defines the study region (SGP: Kansas, Oklahoma, Texas)"),
    ("LIT-001501", "$.introduction", 3453): (S, True, "states wildfire-risk exposure of Oklahoma's population (cited background on the study region)"),
    ("LIT-001501", "$.introduction", 1875): (I, True, "another region where the relationship was studied by others"),
    ("LIT-001501", "$.introduction", 3992): (I, True, "a cited finding for another region"),
    ("LIT-001501", '$["data and methods"]', 3980): (I, False, WFI),
    ("LIT-001501", '$["data and methods"]', 4119): (I, False, WFI),
    ("LIT-001501", '$["data and methods"]', 4262): (I, False, WFI),
    ("LIT-001501", '$["data and methods"]', 4316): (I, False, WFI),
    ("LIT-001501", '$["data and methods"]', 3243): (I, True, MESONET + " (section heading)"),
    ("LIT-001501", '$["data and methods"]', 3266): (I, True, MESONET),
    ("LIT-001501", '$["data and methods"]', 3368): (S, True, "the four soil-moisture sites span west-to-east across Oklahoma (study location)"),
    ("LIT-001501", '$["data and methods"]', 3707): (I, True, MESONET),
    ("LIT-001501", "$.results", 9803): (I, False, WFI),
    ("LIT-001501", "$.results", 10025): (I, False, WFI),
    ("LIT-001501", "$.results", 10180): (I, False, WFI),
    ("LIT-001501", "$.results", 10359): (I, False, WFI),
    ("LIT-001501", "$.results", 10610): (I, False, WFI),
    ("LIT-001501", "$.results", 11010): (I, False, WFI),
    ("LIT-001501", "$.results", 4428): (S, True, "drought harm to Oklahoma's wheat and cattle industry"),
    ("LIT-001501", "$.results", 5159): (S, True, "location of the Rhea Fire (promoted as claim C4)"),
    ("LIT-001501", "$.results", 9693): (I, True, MESONET),
    ("LIT-001501", "$.discussion", 668): (S, True, "the case-study region (Oklahoma and Texas panhandles)"),
    ("LIT-001501", "$.discussion", 2909): (I, True, "a cited comparison for another region"),
    ("LIT-001501", "$.discussion", 4008): (I, True, "method of a cited study in another region"),
    ("LIT-001501", "$.conclusion", 3616): (I, False, WFI + " (figure caption)"),
    ("LIT-001501", "$.conclusion", 2677): (S, True, "negative NDVI anomalies across Oklahoma (figure text stored in this field)"),
    ("LIT-001501", "$.conclusion", 3017): (I, True, MESONET + " (figure caption)"),
    ("LIT-001501", "$.conclusion", 3452): (I, True, MESONET + " (figure caption)"),
    ("LIT-001501", "$.conclusion", 3694): (I, True, MESONET + " (figure caption)"),
    ("LIT-001501", "$.conclusion", 439): (I, True, "other regions where the relationship was studied"),
    ("LIT-001501", "$.conclusion", 5596): (I, True, "reference-list entry (cited article title)"),
    # LIT-001536 --- US prisons
    ("LIT-001536", "$.results", 2142): (S, True, "Oklahoma among the next-highest state-averaged prison heat exposures"),
    ("LIT-001536", "$.results", 483): (S, True, "California among the states with the most facilities in the study population"),
    ("LIT-001536", "$.results", 907): (S, True, "California prisons' share of those with days over 85°F"),
    ("LIT-001536", "$.results", 1017): (S, True, "California prisons with at least 65 days over 85°F"),
    ("LIT-001536", "$.results", 1367): (S, True, "top-10 most heat-exposed facilities (promoted as claim C1)"),
    ("LIT-001536", "$.results", 1487): (S, True, "the maximum-value facility, Calipatria State Prison, California"),
    ("LIT-001536", "$.results", 1838): (I, True, "citation author ('State of California, 2021')"),
    ("LIT-001536", "$.results", 2830): (S, True, "California among the highest facility-level temperature anomalies"),
    ("LIT-001536", "$.discussion", 3243): (I, True, "a cited methodological aside on why the paper uses air temperature; heat index is not analysed"),
    ("LIT-001536", "$.discussion", 2772): (S, True, "Oklahoma among the states with the most heat-exposed facilities in this and a prior study"),
    ("LIT-001536", "$.discussion", 1868): (S, True, "California among the highest occurrences of the mortality-relevant metric"),
    ("LIT-001536", "$.discussion", 2744): (S, True, "California in the same comparison sentence as the Oklahoma hit"),
}


def inside(h: dict, span: dict) -> bool:
    return (span["json_path"] == h["json_path"] and span["char_start"] <= h["char_start"]
            and h["char_end"] <= span["char_end"])


def main() -> int:
    cands = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    entries = {e["item_id"]: e for e in json.loads(MANIFEST.read_text(encoding="utf-8"))["entries"]}
    root = Path(get_local_path("literature_corpus_root"))
    seen, items = set(), []
    for c in cands["candidates"]:
        iid = c["item_id"]
        doc, err = litingest.read_verified(root / entries[iid]["relative_path"], entries[iid]["sha256"])
        if err:
            print(f"FAIL: {iid}: {err}", file=sys.stderr)
            return 1
        rec = json.loads((CLAIMS_DIR / f"{iid}.json").read_text(encoding="utf-8"))
        claims = rec["claims"]
        rows = []
        for h in c["hits"]:
            key = (iid, h["json_path"], h["char_start"])
            if key not in JUDGEMENTS:
                print(f"FAIL: no classification for hit {key}", file=sys.stderr)
                return 1
            seen.add(key)
            if litingest.resolve(doc, h["json_path"])[h["char_start"]:h["char_end"]] != h["matched_text"]:
                print(f"FAIL: hit {key} does not re-slice", file=sys.stderr)
                return 1
            cls, ref, reason = JUDGEMENTS[key]
            ev = [x["claim_id"] for x in claims if inside(h, x["evidence"])]
            sup = sorted({x["claim_id"] for x in claims for d in ("concept", "relation_or_direction", "geography",
                          "temporal_frame", "scenario", "experimental_condition")
                          if "support" in x[d] and inside(h, x[d]["support"])})
            rows.append({**{k: h[k] for k in ("json_path", "term_id", "term", "term_class", "char_start", "char_end", "matched_text")},
                         "classification": cls, "referent_matches_term": ref, "reason": reason,
                         "in_promoted_claim_evidence": ev, "in_promoted_claim_support": sup})
        cnt = lambda cl, tc=None: sum(1 for r in rows if r["classification"] == cl and (tc is None or r["term_class"] == tc))  # noqa: E731
        items.append({"item_id": iid, "n_hits": len(rows),
                      "substantive": cnt(S), "incidental": cnt(I),
                      "concept_substantive": cnt(S, "concept"), "concept_incidental": cnt(I, "concept"),
                      "place_substantive": cnt(S, "place"), "place_incidental": cnt(I, "place"),
                      "different_referent": sum(1 for r in rows if not r["referent_matches_term"]),
                      "hits_inside_promoted_evidence": sum(1 for r in rows if r["in_promoted_claim_evidence"]),
                      "hits": rows})
    stray = set(JUDGEMENTS) - seen
    if stray:
        print(f"FAIL: classifications for hits that do not exist: {sorted(stray)}", file=sys.stderr)
        return 1
    out = {
        "artifact": "M4-WP2 retrieval-hit classification (after reading)",
        "statement": "Classified after reader 1's claims were built; no hit filled any claim field. Relevance-guided candidate sample, not representative.",
        "rule": {"substantive": "the passage states something about the term's concept or place, and the paper treats that concept or place (studies, analyses or reviews it beyond a list entry)",
                 "incidental": "author surname, citation or reference-list entry, instrument-network name, list entry, passing mention, or a different referent under the same letters"},
        "candidates_sha256": sha256_file(CANDIDATES),
        "claims_sha256": {p.name: sha256_file(p) for p in sorted(CLAIMS_DIR.glob("LIT-*.json"))},
        "totals": {k: sum(i[k] for i in items) for k in ("n_hits", "substantive", "incidental", "concept_substantive",
                                                         "concept_incidental", "place_substantive", "place_incidental",
                                                         "different_referent", "hits_inside_promoted_evidence")},
        "items": items,
    }
    text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if OUT.exists() and OUT.read_text(encoding="utf-8") != text:
        print("FAIL: wp2_hit_classification.json differs from a rebuild", file=sys.stderr)
        return 1
    action = "verified" if OUT.exists() else "written"
    OUT.write_text(text, encoding="utf-8")
    for i in items:
        print(f"  {i['item_id']}  hits={i['n_hits']:<3} substantive={i['substantive']:<3} incidental={i['incidental']:<3} "
              f"different_referent={i['different_referent']:<3} in_promoted_evidence={i['hits_inside_promoted_evidence']}")
    print(f"  totals {out['totals']}  ({action})")
    rec = write_run_record("wp2_hit_classification", result_summary={"action": action, "totals": out["totals"]},
                           passed=True, data_path=CANDIDATES, output_path=OUT,
                           config_snapshot={"corpus_root": "config/local_paths.yaml:literature_corpus_root"})
    print(f"Run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
