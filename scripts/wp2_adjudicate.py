#!/usr/bin/env python3
"""M4-WP2 Phase 3: compare reader 1 with the blind reader on the four candidates, and adjudicate.

Same rules as M4-WP1b (D-019): scope by rule 1; alignment by evidence-span
overlap; rules 2--3 through `climrr.wp1b.resolve_pair` with the judgements in
`climrr.wp2_judgements` (span-limited trimming; no override used); rule 4 for
single-reader claims; nothing deleted; every claim gets
`claim_validation_status` and `evidence_tier`. **The adjudicator is reader 1.**

Writes, once (later runs verify byte equality):
`artifacts/literature/wp2_comparison.json`,
`artifacts/literature/wp2_claims_adjudicated/LIT-*.json` + `adjudication_summary.json`,
`docs/LITERATURE_WP2_ADJUDICATION.md`.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import wp1b, wp2adj  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.litingest import OFFSET_CONVENTION, evidence_sha256  # noqa: E402
from climrr.paths import get as get_local_path  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.wp2_judgements import PAIR_JUDGEMENTS  # noqa: E402

REPRESENTATIVENESS = "relevance-guided candidate sample, not representative"


def _ov(c: dict, rejected: list[dict]) -> list[dict]:
    return [{"rejected_id": r["id"], "overlap_code_points": wp1b.overlaps(c["evidence"], r["span"]),
             "reason": r["reason"], "evidence_text": r["span"]["evidence_text"]}
            for r in rejected if wp1b.overlaps(c["evidence"], r["span"]) > 0]


def _with_hash(span: dict) -> dict:
    return {**span, "offset_convention": OFFSET_CONVENTION, "evidence_sha256": evidence_sha256(span["evidence_text"])}


def main() -> int:
    try:
        shas = wp2adj.verify_inputs()
        r1, r2 = wp2adj.load_r1(), wp2adj.load_r2()
        spans = wp2adj.verify_all_spans(Path(get_local_path("literature_corpus_root")), r1, r2)
    except wp1b.AdjudicationError as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 1
    print(f"  spans re-sliced: reader 1 {spans['reader_1']}, reader 2 {spans['reader_2']}; 0 failures")
    ents = wp2adj.manifest_entries()

    scope, items, all_pairs, used = [], [], [], set()
    for iid in wp2adj.candidate_ids():
        s1, why1 = wp2adj.scope_of(r1[iid], 1)
        s2, why2 = wp2adj.scope_of(r2[iid], 2)
        adopted, rule = wp1b.adjudicate_scope(s1, s2)
        c1, c2 = wp2adj.claims_of(r1[iid], 1), wp2adj.claims_of(r2[iid], 2)
        row = {"item_id": iid, "blind_basename": ents[iid]["relative_path"], "reader_1_scope": s1, "reader_2_scope": s2,
               "agree": s1 == s2, "reader_1_reason": why1, "reader_2_reason": why2, "adopted_scope": adopted,
               "scope_rule": rule, "reader_1_terminal": r1[iid]["terminal_status"], "reader_2_terminal": r2[iid]["terminal_status"],
               "reader_1_n_claims": len(c1), "reader_2_n_claims": len(c2)}
        scope.append(row)
        rej1, rej2 = wp2adj.rejected_of(r1[iid], 1), wp2adj.rejected_of(r2[iid], 2)
        pairs, only1, only2 = wp1b.align(c1, c2)
        pout = []
        for a, b, n in pairs:
            if a["claim_id"] not in PAIR_JUDGEMENTS:
                raise wp1b.AdjudicationError(f"no judgement for aligned pair {a['claim_id']}")
            used.add(a["claim_id"])
            res = wp1b.resolve_pair(a, b, PAIR_JUDGEMENTS[a["claim_id"]])
            e = {"reader_1_claim_id": a["claim_id"], "reader_2_claim_id": b["claim_id"], "overlap_code_points": n,
                 "reader_1_evidence": a["evidence"], "reader_2_evidence": b["evidence"],
                 "reader_1_text": a["text"], "reader_2_text": b["text"], **res}
            if res["overrides"]:
                raise wp1b.AdjudicationError(f"{a['claim_id']}: an override was used; D-019 needs explicit justification")
            pout.append(e)
            all_pairs.append(e)
        items.append({"item_id": iid, "blind_basename": row["blind_basename"], "pairs": pout,
                      "reader_1_only": [{"claim_id": a["claim_id"], "text": a["text"], "evidence": a["evidence"],
                                         "overlaps_reader_2_rejected": _ov(a, rej2)} for a in only1],
                      "reader_2_only": [{"claim_id": b["claim_id"], "text": b["text"], "evidence": b["evidence"],
                                         "overlaps_reader_1_rejected": _ov(b, rej1)} for b in only2],
                      "_c1": c1, "_c2": c2, "_only1": only1, "_only2": only2, "_row": row})
    if set(PAIR_JUDGEMENTS) - used:
        raise wp1b.AdjudicationError(f"judgements for pairs that did not align: {sorted(set(PAIR_JUDGEMENTS) - used)}")

    n1 = sum(len(i["_c1"]) for i in items)
    n2 = sum(len(i["_c2"]) for i in items)
    both = [r["item_id"] for r in scope if r["reader_1_scope"] == r["reader_2_scope"] == "in_scope_hazard"]
    stats = wp1b.statistics(scope, all_pairs, n1, n2, both, n1, n2)
    stats["caveat"] = ("n is small (4 items, 13 aligned pairs). Descriptive counts of two readings of a relevance-guided "
                       "sample, not estimates of reader reliability; no inferential statement.")

    comparison = {
        "artifact": "M4-WP2 comparison of two readings of the four frozen candidates",
        "authorized_by": "docs/M4_WP1B_WP2_CANDIDATE_READING_GUIDANCE_RULING.md (D-019), Phase 3",
        "representativeness": REPRESENTATIVENESS,
        "inputs": {"reader_1": f"artifacts/literature/wp2_claims/ (the EXECUTOR, prototype-exposed; {wp2adj.READER_1_COMMIT})",
                   "reader_2": f"artifacts/literature/wp2_blind/ (blind reader, frozen at {wp2adj.BLIND_COMMIT})",
                   "sha256": shas},
        "adjudicator": "reader 1 (the EXECUTOR, prototype-exposed)",
        "span_verification": {**spans, "failures": 0},
        "alignment_rule": "same normalised json_path and overlapping [char_start, char_end); one-to-one or the run fails",
        "phase_a_scope": scope,
        "phase_b_alignment": [{k: v for k, v in i.items() if not k.startswith("_")} for i in items],
        "phase_b_counts": {"aligned_pairs": len(all_pairs), "reader_1_only": sum(len(i["_only1"]) for i in items),
                           "reader_2_only": sum(len(i["_only2"]) for i in items)},
        "phase_c_statistics": stats,
    }

    wp2adj.ADJ_DIR.mkdir(exist_ok=True)
    counts = {s: 0 for s in wp1b.STATUSES}
    tiers = {"A": 0, "B": 0, "C": 0}
    actions, per_item = {}, []
    for it in items:
        iid, row = it["item_id"], it["_row"]
        contested = row["adopted_scope"] == wp1b.CONTESTED
        rec = copy.deepcopy(r1[iid])
        pair_by = {p["reader_1_claim_id"]: p for p in it["pairs"]}
        only1 = {a["claim_id"]: a for a in it["reader_1_only"]}
        for c in rec["claims"]:
            c["first_pass_claim_validation_status"] = c["claim_validation_status"]
            c["first_pass_evidence_tier"] = c.pop("evidence_tier")
            adj = {"package": "M4-WP2 Phase 3", "rules_applied": [], "flags": [], "notes": []}
            if contested:
                status = "adjudicated_modified"
                adj["rules_applied"].append("R1b")
                adj["flags"].append("scope_contested_by_blind_reader")
                adj["notes"].append(wp1b.CONTESTED_NOTE)
            elif c["claim_id"] in pair_by:
                p = pair_by[c["claim_id"]]
                status = p["status"]
                adj["rules_applied"].append(p["rule"])
                adj.update(aligned_blind_claim_id=p["reader_2_claim_id"], blind_evidence=p["reader_2_evidence"],
                           dimension_decisions=p["decisions"])
                if status == "adjudicated_modified":
                    adj["adopted_dimensions"] = {d: dec["adopted"] for d, dec in p["decisions"].items() if not dec["agree"]}
                    adj["notes"].append("claim_text is reader 1's, unchanged; adopted_dimensions replace the differing dimensions downstream")
                if p["unresolved_ties"]:
                    adj["flags"].append("unresolved_tie")
            elif c["claim_id"] in only1:
                status = "single_reader_provisional"
                adj["rules_applied"].append("R4")
                adj["flags"].append("not_independently_found")
                if only1[c["claim_id"]]["overlaps_reader_2_rejected"]:
                    adj["blind_reader_considered_and_rejected"] = only1[c["claim_id"]]["overlaps_reader_2_rejected"]
            else:
                raise wp1b.AdjudicationError(f"{c['claim_id']}: no rule applies")
            c["claim_validation_status"] = status
            c["evidence_tier"] = wp1b.evidence_tier(status, contested)
            c["adjudication"] = adj
        r2claims = {c["claim_id"]: c for c in r2[iid]["claims"]}
        for b in it["_only2"]:
            raw = r2claims[b["claim_id"]]
            new = {"claim_id": f"{iid}-B{b['claim_id'].rsplit('-C', 1)[1]}", "origin": "blind_reader",
                   "blind_claim_id": b["claim_id"], "claim_text": b["text"], "claim_type": b["claim_type"]}
            for d in wp1b.DIMENSIONS:
                dd = {"value": b[d]["value"], "status": b[d]["tag"]}
                if "support" in b[d]:
                    dd["support"] = _with_hash(b[d]["support"])
                if raw[d].get("reason"):
                    dd["blind_reader_reason"] = raw[d]["reason"]
                new[d] = dd
            new["evidence"] = _with_hash(b["evidence"])
            new["claim_validation_status"] = "single_reader_provisional"
            new["evidence_tier"] = wp1b.evidence_tier("single_reader_provisional", contested)
            ov = next(x for x in it["reader_2_only"] if x["claim_id"] == b["claim_id"])["overlaps_reader_1_rejected"]
            new["adjudication"] = {"package": "M4-WP2 Phase 3", "rules_applied": ["R4"], "flags": ["blind_reader_only"],
                                   "notes": ["a new candidate from the blind reader, not confirmed"]}
            if ov:
                new["adjudication"]["first_reader_considered_and_rejected"] = ov
            rec["claims"].append(new)
        for c in rec["claims"]:
            counts[c["claim_validation_status"]] += 1
            tiers[c["evidence_tier"]] += 1
        rec["scope_adjudication"] = {"reader_1": row["reader_1_scope"], "reader_2": row["reader_2_scope"],
                                     "adopted": row["adopted_scope"], "rule": row["scope_rule"],
                                     "reader_2_record": f"artifacts/literature/wp2_blind/{row['blind_basename']}",
                                     "reader_2_reason": row["reader_2_reason"]}
        rec["adjudication_provenance"] = {"package": "M4-WP2 Phase 3", "adjudicator": "reader 1 (the EXECUTOR, prototype-exposed)",
                                          "first_pass_record_sha256": shas[f"artifacts/literature/wp2_claims/{iid}.json"],
                                          "blind_record_sha256": shas[f"artifacts/literature/wp2_blind/{row['blind_basename']}"],
                                          "no_paper_re_read": True, "representativeness": REPRESENTATIVENESS}
        actions[f"{iid}.json"] = wp1b.write_json(wp2adj.ADJ_DIR / f"{iid}.json", rec)
        per_item.append({"item_id": iid, "adopted_scope": row["adopted_scope"], "n_claims": len(rec["claims"]),
                         "statuses": {s: sum(c["claim_validation_status"] == s for c in rec["claims"]) for s in wp1b.STATUSES},
                         "tiers": {t: sum(c["evidence_tier"] == t for c in rec["claims"]) for t in ("A", "B", "C")}})

    summary = {"artifact": "M4-WP2 adjudicated claim set", "decision": "D-019",
               "adjudicator": "reader 1 (the EXECUTOR, prototype-exposed)", "representativeness": REPRESENTATIVENESS,
               "status_counts": counts, "evidence_tier_counts": tiers, "evidence_tiers": wp1b.EVIDENCE_TIERS,
               "n_claims_total": sum(counts.values()), "overrides_used": [], "items": per_item}
    comparison["phase_d_status_counts"] = counts
    comparison["phase_d_tier_counts"] = tiers
    actions["comparison"] = wp1b.write_json(wp2adj.COMPARISON_PATH, comparison)
    actions["summary"] = wp1b.write_json(wp2adj.ADJ_SUMMARY_PATH, summary)
    doc = render(comparison, summary)
    if wp2adj.DOC_PATH.exists() and wp2adj.DOC_PATH.read_text(encoding="utf-8") != doc:
        print("FAIL: docs/LITERATURE_WP2_ADJUDICATION.md differs from a rebuild", file=sys.stderr)
        return 1
    wp2adj.DOC_PATH.write_text(doc, encoding="utf-8")
    pc = comparison["phase_b_counts"]
    print(f"  scope agreement {stats['scope_agreement']}; aligned {pc['aligned_pairs']}; r1-only {pc['reader_1_only']}; r2-only {pc['reader_2_only']}")
    print(f"  statuses {counts}; tiers {tiers}; {actions}")
    rec = write_run_record("wp2_adjudicate", result_summary={"actions": actions, "spans": spans, "counts": pc,
                                                             "statuses": counts, "tiers": tiers},
                           passed=True, data_path=wp2adj.CANDIDATES, output_path=wp2adj.COMPARISON_PATH,
                           config_snapshot={"corpus_root": "config/local_paths.yaml:literature_corpus_root",
                                            "reader_1": wp2adj.READER_1_COMMIT, "blind": wp2adj.BLIND_COMMIT})
    print(f"Run record: {repo_relative(rec)}")
    return 0


def _md(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _dv(d) -> str:
    return d if isinstance(d, str) else f"{d['value']} [{d['tag']}]"


def render(cmp: dict, summ: dict) -> str:
    st = cmp["phase_c_statistics"]
    L = ["# M4-WP2 --- comparison of two readings of the four candidates, and adjudication", "",
         "**Generated by `scripts/wp2_adjudicate.py`; do not edit by hand.** Reader 1 is the EXECUTOR "
         f"(prototype-exposed, `{wp2adj.READER_1_COMMIT}`); reader 2 is the blind reader (`{wp2adj.BLIND_COMMIT}`). "
         "**The adjudicator is reader 1.** Rules as M4-WP1b (D-019); **no override was used**; no paper was re-read. "
         f"**{REPRESENTATIVENESS.capitalize()}.**", "",
         f"Span integrity: **{cmp['span_verification']['reader_1']}** reader-1 and **{cmp['span_verification']['reader_2']}** "
         "reader-2 spans re-sliced from the hash-verified sources; **0 failures**.", "",
         "## Scope", "", f"**Agreement {st['scope_agreement']['agree']} / {st['scope_agreement']['n']}.**", "",
         "| Item | Reader 1 | Reader 2 | Adopted | Reader 1 reason | Reader 2 reason |", "| --- | --- | --- | --- | --- | --- |"]
    for r in cmp["phase_a_scope"]:
        L.append(f"| `{r['item_id']}` | {r['reader_1_scope']} | {r['reader_2_scope']} | {r['adopted_scope']} | {_md(r['reader_1_reason'])} | {_md(r['reader_2_reason'])} |")
    pc = cmp["phase_b_counts"]
    L += ["", "## Alignment", "", f"**{pc['aligned_pairs']} aligned; {pc['reader_1_only']} reader-1-only; {pc['reader_2_only']} reader-2-only.**", "",
          "| Item | Aligned | Reader-1-only | Reader-2-only |", "| --- | --- | --- | --- |"]
    for it in cmp["phase_b_alignment"]:
        L.append(f"| `{it['item_id']}` | " + (", ".join(f"{p['reader_1_claim_id']}↔{p['reader_2_claim_id']} ({'confirmed' if p['status'] == 'independently_confirmed' else 'modified'})" for p in it["pairs"]) or "---")
                 + " | " + (", ".join(a["claim_id"] for a in it["reader_1_only"]) or "---")
                 + " | " + (", ".join(b["claim_id"] for b in it["reader_2_only"]) or "---") + " |")
    L += ["", "### Disagreements on aligned pairs", "", "| Claim | Dimension | Reader 1 | Reader 2 | Rule | Adopted |", "| --- | --- | --- | --- | --- | --- |"]
    for it in cmp["phase_b_alignment"]:
        for p in it["pairs"]:
            for d, dec in p["decisions"].items():
                if dec["agree"]:
                    continue
                m = p["mechanical"][d]
                L.append(f"| {p['reader_1_claim_id']} | {d} | {_md(_dv(m['reader_1']))} | {_md(_dv(m['reader_2']))} | {_md(dec['rule'])} | {_md(_dv(dec['adopted']))} |")
    L += ["", "### Single-reader claims", ""]
    for it in cmp["phase_b_alignment"]:
        for a in it["reader_1_only"]:
            L.append(f"- reader-1-only **{a['claim_id']}**: {_md(a['text'])}")
        for b in it["reader_2_only"]:
            x = "; **reader 1 had considered and not promoted this passage**: \"" + _md(b["overlaps_reader_1_rejected"][0]["reason"]) + "\"" if b["overlaps_reader_1_rejected"] else ""
            L.append(f"- reader-2-only **{b['claim_id']}** (`{it['item_id']}`): {_md(b['text'])}{x}")
    L += ["", "## Agreement (descriptive only)", "", f"_{st['caveat']}_", "", "| Measure | Value |", "| --- | --- |",
          f"| Per-item claim-count agreement | {st['per_item_claim_count_agreement']['agree']} / {st['per_item_claim_count_agreement']['n']} |",
          f"| Reader-1 claims aligned | {st['reader_1_claims_with_aligned_reader_2']['aligned']} / {st['reader_1_claims_with_aligned_reader_2']['n']} |",
          f"| Reader-2 claims aligned | {st['reader_2_claims_with_aligned_reader_1']['aligned']} / {st['reader_2_claims_with_aligned_reader_1']['n']} |",
          "", "| Dimension | Tag agreement | Exact agreement |", "| --- | --- | --- |"]
    for d, v in st["per_dimension_over_aligned_pairs"].items():
        L.append(f"| {d} | {v['tag_agreement']} / {v['n_pairs']} | {v['exact_agreement_tag_and_content']} / {v['n_pairs']} |")
    sc, tc = summ["status_counts"], summ["evidence_tier_counts"]
    L += ["", "## Adjudicated set", "", "| Status | Claims |", "| --- | --- |"] + [f"| {s} | {sc[s]} |" for s in wp1b.STATUSES]
    L += [f"| **total** | **{summ['n_claims_total']}** |", "", "| Evidence tier | Claims |", "| --- | --- |"]
    L += [f"| {t} --- {_md(wp1b.EVIDENCE_TIERS[t])} | {tc[t]} |" for t in ("A", "B", "C")]
    L += ["", "| Item | Claims | A | B | C |", "| --- | --- | --- | --- | --- |"]
    L += [f"| `{i['item_id']}` | {i['n_claims']} | {i['tiers']['A']} | {i['tiers']['B']} | {i['tiers']['C']} |" for i in summ["items"]]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
