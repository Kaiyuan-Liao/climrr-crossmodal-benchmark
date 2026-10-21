#!/usr/bin/env python3
"""M4-WP4r1 Phase C: classify concept-hit and place-hit precision for the 20 sampled items.

Runs only after the reading is frozen (`artifacts/literature/wp4_claims/`). For each
sampled item it reads, from the frozen LITCORPUS-02 evidence:

* concept hits --- query group 0 rows of `evidence/runs/<arm>/hits.csv` (both arms,
  so an item hit by the other arm's concept terms is also covered);
* place hits --- `place_candidates/candidate_hits.csv`.

It verifies every source file's SHA-256, checks that each frozen first hit is
reproduced exactly, then finds **all** occurrences of each matched term with the
collection matcher (`\\bterm\\b`, case-insensitive, per string section), applies
reader 1's classes from `scripts/wp4_hit_judgements.py`, and records whether each
occurrence lies inside a promoted claim's evidence span (or a dimension's support
span). Fails if any judgement is missing or unused, or any frozen hit does not
reproduce. Writes `artifacts/literature/wp4_hit_classification.json`.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from climrr import litingest  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import get as get_local_path  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
import wp4_hit_judgements as hj  # noqa: E402

LIT = REPO_ROOT / "artifacts" / "literature"
EV = LIT / "litcorpus02"
SAMPLE = LIT / "wp4_sample.json"
CLAIMS_DIR = LIT / "wp4_claims"
OUT = LIT / "wp4_hit_classification.json"
ARMS = ("fire_weather_v1", "extreme_heat_v1")
HIT_FILES = {arm: EV / "evidence" / "runs" / arm / "hits.csv" for arm in ARMS}
PLACE_FILE = EV / "place_candidates" / "candidate_hits.csv"
DIMENSIONS = ("concept", "relation_or_direction", "geography", "temporal_frame", "scenario",
              "experimental_condition")


class ClassificationError(RuntimeError):
    pass


def frozen_hits(item_ids: set[str]) -> dict[tuple[str, str, str], list[dict]]:
    """(item_id, kind, term) -> frozen first-hit rows."""
    out: dict[tuple[str, str, str], list[dict]] = {}
    for arm, path in HIT_FILES.items():
        with path.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["doc_id"] in item_ids and r["group"] == "0":
                    out.setdefault((r["doc_id"], "concept", r["term"]), []).append({**r, "source_arm": arm})
    with PLACE_FILE.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["item_id"] in item_ids:
                out.setdefault((r["item_id"], "place", r["term"]), []).append({**r, "source_arm": r["arm"]})
    return out


def claim_spans(record: dict) -> list[tuple[str, str, int, int]]:
    """(label, json_path, start, end) for every promoted-claim evidence and support span."""
    spans = []
    for c in record.get("claims", []):
        e = c["evidence"]
        spans.append((f"{c['claim_id']}:evidence", e["json_path"], e["char_start"], e["char_end"]))
        for d in DIMENSIONS:
            if "support" in c[d]:
                s = c[d]["support"]
                spans.append((f"{c['claim_id']}:{d}.support", s["json_path"], s["char_start"], s["char_end"]))
    return spans


def classify_pair(lid: str, term: str, n: int) -> tuple[list[tuple[str, str]], dict]:
    j = hj.JUDGEMENTS.get((lid, term))
    if j is None:
        raise ClassificationError(f"no judgement for {lid} / {term!r}")
    per = [(j["class"], j["reason"])] * n
    for o in j["overrides"]:
        for i in o["occurrences"]:
            if not 0 <= i < n:
                raise ClassificationError(f"{lid} / {term!r}: override index {i} outside {n} occurrences")
            per[i] = (o["class"], o["reason"])
    return per, j


def main() -> int:
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    selected = sample["selected"]
    by_item = {s["item_id"]: s for s in selected}
    root = Path(get_local_path("litcorpus02_root"))
    hits = frozen_hits(set(by_item))
    used: set[tuple[str, str]] = set()
    items_out, n_occ, n_frozen = [], 0, 0
    try:
        for s in selected:
            lid = s["lit2_id"]
            doc, failure = litingest.read_verified(root / s["rel_path"], s["sha256"])
            if failure:
                raise ClassificationError(f"{lid}: {failure}")
            keys = list(doc)
            record = json.loads((CLAIMS_DIR / f"{lid}.json").read_text(encoding="utf-8"))
            spans = claim_spans(record)
            pairs = []
            for (iid, kind, term), rows in sorted(hits.items()):
                if iid != s["item_id"]:
                    continue
                rx = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
                occ = []
                for idx, (k, v) in enumerate(doc.items()):
                    if isinstance(v, str):
                        for m in rx.finditer(v):
                            occ.append({"json_path": litingest.child_path("$", k), "section_idx": idx,
                                        "char_start": m.start(), "char_end": m.end(), "matched_text": m.group(0)})
                for r in rows:
                    n_frozen += 1
                    k, idx, st = r["section_key"], int(r["section_idx"]), int(r["char_start"])
                    if idx >= len(keys) or keys[idx] != k:
                        raise ClassificationError(f"{lid} / {term!r}: frozen section_idx {idx} is not key {k!r}")
                    first = next((o for o in occ if o["section_idx"] == idx), None)
                    if first is None or first["char_start"] != st or first["char_end"] != int(r["char_end"]):
                        raise ClassificationError(f"{lid} / {term!r}: frozen first hit {k}[{st}] not reproduced")
                per, j = classify_pair(lid, term, len(occ))
                used.add((lid, term))
                for o, (cls, reason) in zip(occ, per):
                    o["class"], o["reason"] = cls, reason
                    o["inside_claim_spans"] = [lab for lab, p, a, b in spans
                                               if p == o["json_path"] and a <= o["char_start"] and o["char_end"] <= b]
                vocab = hj.CONCEPT_CLASSES if kind == "concept" else hj.PLACE_CLASSES
                if any(o["class"] not in vocab for o in occ):
                    raise ClassificationError(f"{lid} / {term!r}: class outside the {kind} vocabulary")
                present = [c for c in vocab if any(o["class"] == c for o in occ)]
                n_occ += len(occ)
                pairs.append({
                    "kind": kind,
                    "term": term,
                    "frozen_source": sorted({r["source_arm"] for r in rows}),
                    "frozen_first_hits": [{"section_key": r["section_key"], "section_idx": int(r["section_idx"]),
                                           "char_start": int(r["char_start"]), "char_end": int(r["char_end"])} for r in rows],
                    "frozen_first_hits_reproduced": True,
                    "n_occurrences": len(occ),
                    "primary_class": present[0],
                    "reason": j["reason"],
                    "class_counts": {c: sum(o["class"] == c for o in occ) for c in present},
                    "occurs_inside_promoted_claim_evidence": sorted({lab.split(":")[0] for o in occ for lab in o["inside_claim_spans"] if lab.endswith(":evidence")}),
                    "occurs_inside_claim_support_span": sorted({lab for o in occ for lab in o["inside_claim_spans"] if not lab.endswith(":evidence")}),
                    "occurrences": occ,
                })
            items_out.append({"lit2_id": lid, "item_id": s["item_id"], "arm": s["arm"],
                              "scope_status": record.get("scope_status"), "terminal_status": record["terminal_status"],
                              "n_claims": len(record.get("claims", [])), "pairs": pairs})
        unused = set(hj.JUDGEMENTS) - used
        if unused:
            raise ClassificationError(f"judgements with no frozen hit: {sorted(unused)}")
    except (ClassificationError, litingest.IntegrityError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    def pairs_of(kind):
        return [p for it in items_out for p in it["pairs"] if p["kind"] == kind]

    def item_primary(it, kind, vocab):
        cls = [p["primary_class"] for p in it["pairs"] if p["kind"] == kind]
        return next((c for c in vocab if c in cls), None)

    for it in items_out:
        it["item_concept_class"] = item_primary(it, "concept", hj.CONCEPT_CLASSES)
        it["item_place_class"] = item_primary(it, "place", hj.PLACE_CLASSES)
    totals = {
        "items": len(items_out),
        "item_term_pairs": {"concept": len(pairs_of("concept")), "place": len(pairs_of("place"))},
        "frozen_first_hit_rows": n_frozen,
        "occurrences": n_occ,
        "concept_pairs_by_primary_class": {c: sum(p["primary_class"] == c for p in pairs_of("concept")) for c in hj.CONCEPT_CLASSES},
        "place_pairs_by_primary_class": {c: sum(p["primary_class"] == c for p in pairs_of("place")) for c in hj.PLACE_CLASSES},
        "concept_occurrences_by_class": {c: sum(o["class"] == c for p in pairs_of("concept") for o in p["occurrences"]) for c in hj.CONCEPT_CLASSES},
        "place_occurrences_by_class": {c: sum(o["class"] == c for p in pairs_of("place") for o in p["occurrences"]) for c in hj.PLACE_CLASSES},
        "items_by_concept_class": {c: sum(it["item_concept_class"] == c for it in items_out) for c in hj.CONCEPT_CLASSES},
        "items_by_place_class": {c: sum(it["item_place_class"] == c for it in items_out) for c in hj.PLACE_CLASSES},
        "place_pairs_by_term": {t: {c: sum(p["term"] == t and p["primary_class"] == c for p in pairs_of("place")) for c in hj.PLACE_CLASSES}
                                for t in sorted({p["term"] for p in pairs_of("place")})},
    }
    inputs = {repo_relative(p): sha256_file(p) for p in [SAMPLE, *HIT_FILES.values(), PLACE_FILE,
                                                        REPO_ROOT / "scripts" / "wp4_hit_judgements.py",
                                                        LIT / "wp4_claims_summary.json"]}
    result = {
        "artifact": "M4-WP4 reader-1 concept-hit and place-hit precision",
        "reader": "reader_1",
        "made_after_reading_frozen_at": "e0857aa",
        "statement": ("Classification of lexical retrieval hits after reading; no hit is a bridge and none "
                      "changes a claim. Deterministic rank sample of lexical place candidates from LITCORPUS-02; "
                      "not representative of the corpus or the literature."),
        "matcher": "per-section whole-word, case-insensitive, no stemming: \\bterm\\b with re.IGNORECASE (as scripts/litcollect/run_query.py)",
        "scope_of_terms": "query group 0 concept terms (incl. bare fwi) and the place terms oklahoma / stephens / california; group-1 context terms not classified",
        "primary_class_rule": "most substantive class present among a pair's occurrences, in vocabulary order; an item's class is the most substantive pair class",
        "vocabulary": {"concept": list(hj.CONCEPT_CLASSES), "place": list(hj.PLACE_CLASSES)},
        "offset_convention": litingest.OFFSET_CONVENTION,
        "input_sha256": inputs,
        "totals": totals,
        "items": items_out,
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for it in items_out:
        cs = ", ".join(f"{p['term']}={p['primary_class']}({p['n_occurrences']})" for p in it["pairs"])
        print(f"  {it['lit2_id']}  concept={it['item_concept_class']}  place={it['item_place_class']}  | {cs}")
    print(f"  totals: {json.dumps(totals)}")
    rec = write_run_record("wp4_hit_classification", result_summary=totals, passed=True,
                           data_path=SAMPLE, output_path=OUT,
                           config_snapshot={"corpus_root": "config/local_paths.yaml:litcorpus02_root", "inputs": inputs})
    print(f"Run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
