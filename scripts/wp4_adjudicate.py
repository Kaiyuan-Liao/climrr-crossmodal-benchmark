#!/usr/bin/env python3
"""M4-WP4r3 Phase A: compare reader 1 with the blind reader on the twenty, and adjudicate.

Same rules as M4-WP1b / M4-WP2 (D-019): scope by rule 1; alignment by
evidence-span overlap; rules 2--3 through `climrr.wp1b.resolve_pair` with the
judgements in `climrr.wp4_judgements` (span-limited trimming; no override
used); the geography role by rule 3-role (`climrr.wp4adj.resolve_role`); rule
4 for single-reader claims; nothing deleted; every claim gets
`claim_validation_status` and `evidence_tier`. **The adjudicator is reader 1.**

The hit-precision tables of `wp4_hit_classification.json` (reader 1, after
reading) are carried alongside, with whether the blind reader's geography role
for a claim naming the place agrees with reader 1's place-hit class. They are
not an input to any adjudication rule.

Writes, once (later runs verify byte equality):
`artifacts/literature/wp4_comparison.json`,
`artifacts/literature/wp4_claims_adjudicated/LIT2-*.json` + `adjudication_summary.json`,
`docs/LITERATURE_WP4_ADJUDICATION.md`.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import conceptmap, wp1b, wp4adj  # noqa: E402
from climrr.litingest import OFFSET_CONVENTION, evidence_sha256  # noqa: E402
from climrr.paths import get as get_local_path  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.wp4_judgements import PAIR_JUDGEMENTS  # noqa: E402

PKG = "M4-WP4r3 Phase A"
PLACE_TERMS = ("california", "oklahoma", "stephens")
#: Blind role class -> the place-hit class it corresponds to. Other classes have no counterpart.
ROLE_TO_HIT_CLASS = {"study_area": "study_area_or_phenomenon_geography", "contextual": "contextual_geography",
                     "affiliation": "institution_or_affiliation", "citation_or_person": "citation_surname_or_person"}


def _ov(c: dict, rejected: list[dict]) -> list[dict]:
    return [{"rejected_id": r["id"], "overlap_code_points": wp1b.overlaps(c["evidence"], r["span"]),
             "reason": r["reason"], "evidence_text": r["span"]["evidence_text"]}
            for r in rejected if wp1b.overlaps(c["evidence"], r["span"]) > 0]


def _with_hash(span: dict) -> dict:
    return {**span, "offset_convention": OFFSET_CONVENTION, "evidence_sha256": evidence_sha256(span["evidence_text"])}


def _role_single(c: dict, reader: int) -> dict:
    r = c["geography_role"]
    return {"adopted": {"value": r["value"], "class": r["class"]}, "rule": f"R4: single reader (reader {reader}); role as recorded",
            f"reader_{reader}": r}


def hit_tables(r1: dict, r2: dict) -> list[dict]:
    """Per item: reader 1's concept- and place-hit classes, and the blind reader's roles for claims naming each place."""
    hc = json.loads(wp4adj.HIT_CLASSIFICATION.read_text(encoding="utf-8"))
    order = list(wp4adj.ROLE_CONSERVATIVE_ORDER)[::-1]  # most substantive first
    out = []
    for it in sorted(hc["items"], key=lambda i: i["lit2_id"]):
        iid = it["lit2_id"]
        c2 = wp4adj.claims_of(r2[iid], 2)
        places = []
        for p in it["pairs"]:
            if p["kind"] != "place":
                continue
            naming = [c for c in c2 if conceptmap.find_term(p["term"], c["geography"]["value"])]
            roles = [{"blind_claim_id": c["claim_id"], "geography": c["geography"]["value"], "role": c["geography_role"]["value"],
                      "role_class": c["geography_role"]["class"]} for c in naming]
            if not roles:
                verdict, top = "not_comparable: no blind claim names the place", None
            else:
                top = min((r["role_class"] for r in roles), key=order.index)
                mapped = ROLE_TO_HIT_CLASS.get(top)
                if mapped is None:
                    verdict = f"not_comparable: blind role class {top} has no place-hit counterpart"
                else:
                    verdict = "agree" if mapped == p["primary_class"] else "disagree"
            places.append({"term": p["term"], "reader_1_place_hit_class": p["primary_class"], "blind_claims_naming_place": roles,
                           "blind_most_substantive_role_class": top, "blind_role_vs_place_hit_class": verdict})
        out.append({"lit2_id": iid, "arm": it["arm"], "item_concept_class": it["item_concept_class"],
                    "item_place_class": it["item_place_class"],
                    "concept_pairs": [{"term": p["term"], "primary_class": p["primary_class"]} for p in it["pairs"] if p["kind"] == "concept"],
                    "place_pairs": places})
    return out


def main() -> int:
    try:
        shas = wp4adj.verify_inputs()
        r1, r2 = wp4adj.load_r1(), wp4adj.load_r2()
        spans = wp4adj.verify_all_spans(Path(get_local_path(wp4adj.ROOT_KEY)), r1, r2)
    except wp1b.AdjudicationError as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 1
    print(f"  spans re-sliced: reader 1 {spans['reader_1']}, reader 2 {spans['reader_2']}; 0 failures")
    sample = {s["lit2_id"]: s for s in wp4adj.sample_items()}

    scope, items, all_pairs, used, role_rows = [], [], [], set(), []
    for iid in wp4adj.lit2_ids():
        s1, why1 = wp4adj.scope_of(r1[iid])
        s2, why2 = wp4adj.scope_of(r2[iid])
        adopted, rule = wp1b.adjudicate_scope(s1, s2)
        c1, c2 = wp4adj.claims_of(r1[iid], 1), wp4adj.claims_of(r2[iid], 2)
        row = {"item_id": iid, "corpus_item": sample[iid]["item_id"], "arm": sample[iid]["arm"],
               "blind_basename": r2[iid]["source_basename"], "reader_1_scope": s1, "reader_2_scope": s2,
               "agree": s1 == s2, "reader_1_reason": why1, "reader_2_reason": why2, "adopted_scope": adopted,
               "scope_rule": rule, "reader_1_terminal": r1[iid]["terminal_status"], "reader_2_terminal": r2[iid]["terminal_status"],
               "reader_1_n_claims": len(c1), "reader_2_n_claims": len(c2)}
        scope.append(row)
        rej1, rej2 = wp4adj.rejected_of(r1[iid], 1), wp4adj.rejected_of(r2[iid], 2)
        pairs, only1, only2 = wp1b.align(c1, c2)
        pout = []
        for a, b, n in pairs:
            if a["claim_id"] not in PAIR_JUDGEMENTS:
                raise wp1b.AdjudicationError(f"no judgement for aligned pair {a['claim_id']}")
            used.add(a["claim_id"])
            res = wp1b.resolve_pair(a, b, PAIR_JUDGEMENTS[a["claim_id"]])
            if res["overrides"]:
                raise wp1b.AdjudicationError(f"{a['claim_id']}: an override was used; D-019 needs explicit justification")
            geo = res["decisions"]["geography"]
            adopted_geo = geo.get("adopted") if not geo["agree"] else {"value": a["geography"]["value"], "tag": a["geography"]["tag"]}
            role = wp4adj.resolve_role(a["geography_role"], b["geography_role"], adopted_geo)
            e = {"reader_1_claim_id": a["claim_id"], "reader_2_claim_id": b["claim_id"], "overlap_code_points": n,
                 "reader_1_evidence": a["evidence"], "reader_2_evidence": b["evidence"],
                 "reader_1_text": a["text"], "reader_2_text": b["text"], **res, "geography_role": role}
            if not role["agree"]:
                e["status"] = "adjudicated_modified"  # a role disagreement is a disagreement (rule 3-role)
                e["rule"] = "R3"
            pout.append(e)
            all_pairs.append(e)
            role_rows.append({"pair": a["claim_id"], "agree": role["agree"], "reader_1": a["geography_role"]["class"],
                              "reader_2": b["geography_role"]["class"], "adopted": role["adopted"]["class"]})
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
    n1b = sum(len(i["_c1"]) for i in items if i["item_id"] in both)
    n2b = sum(len(i["_c2"]) for i in items if i["item_id"] in both)
    stats = wp1b.statistics(scope, all_pairs, n1, n2, both, n1b, n2b)
    stats["caveat"] = (f"n is small (20 items, {len(all_pairs)} aligned pairs). Descriptive counts of two readings of a "
                       "deterministic place-candidate sample, not estimates of reader reliability; no inferential statement.")
    stats["geography_role_class_over_aligned_pairs"] = {
        "n_pairs": len(role_rows), "class_agreement": sum(r["agree"] for r in role_rows),
        "disagreements": [r for r in role_rows if not r["agree"]]}

    hits = hit_tables(r1, r2)
    comparison = {
        "artifact": "M4-WP4 comparison of two readings of the twenty frozen candidates",
        "authorized_by": "docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md (D-025), Track A, required actions 12-15",
        "representativeness": wp4adj.REPRESENTATIVENESS,
        "inputs": {"reader_1": f"artifacts/literature/wp4_claims/ (the EXECUTOR, prototype-exposed; {wp4adj.READER_1_COMMIT})",
                   "reader_2": f"artifacts/literature/wp4_blind/ (blind reader, frozen at {wp4adj.BLIND_COMMIT})",
                   "sha256": shas},
        "adjudicator": wp4adj.ADJUDICATOR,
        "prior_exposure": {"item": wp4adj.PRIOR_EXPOSURE_ITEM, "note": wp4adj.PRIOR_EXPOSURE_NOTE,
                           "reader_1_record_field": r1[wp4adj.PRIOR_EXPOSURE_ITEM].get("prior_exposure"),
                           "reader_2_record_field": r2[wp4adj.PRIOR_EXPOSURE_ITEM].get("prior_exposure")},
        "span_verification": {**spans, "failures": 0},
        "alignment_rule": "same normalised json_path and overlapping [char_start, char_end); one-to-one or the run fails",
        "role_rule": ("3-role: each reader's geography role is put in a class (climrr.wp4adj.ROLE_CLASS_OF, "
                      "climrr.wp4_judgements.ROLE_CLASS_OF_R1); same class -> agree; different -> the more conservative class "
                      f"in the order {list(wp4adj.ROLE_CONSERVATIVE_ORDER)}; geography adopted unknown -> role unknown. "
                      "A role disagreement makes the pair adjudicated_modified."),
        "phase_a_scope": scope,
        "phase_b_alignment": [{k: v for k, v in i.items() if not k.startswith("_")} for i in items],
        "phase_b_counts": {"aligned_pairs": len(all_pairs), "reader_1_only": sum(len(i["_only1"]) for i in items),
                           "reader_2_only": sum(len(i["_only2"]) for i in items)},
        "phase_c_statistics": stats,
        "hit_precision_after_reading": {"source": "artifacts/literature/wp4_hit_classification.json (reader 1, after reading)",
                                        "sha256": wp4adj.HIT_CLASSIFICATION_SHA256,
                                        "role_to_hit_class": ROLE_TO_HIT_CLASS, "items": hits},
    }

    wp4adj.ADJ_DIR.mkdir(exist_ok=True)
    counts = {s: 0 for s in wp1b.STATUSES}
    tiers = {"A": 0, "B": 0, "C": 0}
    actions, per_item = {}, []
    for it in items:
        iid, row = it["item_id"], it["_row"]
        contested = row["adopted_scope"] == wp1b.CONTESTED
        promoted = row["adopted_scope"] in ("in_scope_hazard", wp1b.CONTESTED)
        rec = copy.deepcopy(r1[iid])
        pair_by = {p["reader_1_claim_id"]: p for p in it["pairs"]}
        only1 = {a["claim_id"]: a for a in it["reader_1_only"]}
        c1_by = {c["claim_id"]: c for c in it["_c1"]}
        for c in rec["claims"]:
            c["first_pass_claim_validation_status"] = c["claim_validation_status"]
            c["first_pass_evidence_tier"] = c.pop("evidence_tier")
            adj = {"package": PKG, "rules_applied": [], "flags": [], "notes": []}
            if not promoted:
                raise wp1b.AdjudicationError(f"{c['claim_id']}: a claim in an item adjudicated {row['adopted_scope']}")
            if c["claim_id"] in pair_by:
                p = pair_by[c["claim_id"]]
                status = p["status"]
                adj["rules_applied"].append(p["rule"])
                adj.update(aligned_blind_claim_id=p["reader_2_claim_id"], blind_evidence=p["reader_2_evidence"],
                           dimension_decisions=p["decisions"], geography_role=p["geography_role"])
                adopted = {d: dec["adopted"] for d, dec in p["decisions"].items() if not dec["agree"]}
                if adopted:
                    adj["adopted_dimensions"] = adopted
                    adj["notes"].append("claim_text is reader 1's, unchanged; adopted_dimensions replace the differing dimensions downstream")
                if not p["geography_role"]["agree"]:
                    adj["notes"].append("geography role classes differ; the more conservative class is adopted (rule 3-role)")
                if p["unresolved_ties"]:
                    adj["flags"].append("unresolved_tie")
            elif c["claim_id"] in only1:
                status = "single_reader_provisional"
                adj["rules_applied"].append("R4")
                adj["flags"].append("not_independently_found")
                adj["geography_role"] = _role_single(c1_by[c["claim_id"]], 1)
                if only1[c["claim_id"]]["overlaps_reader_2_rejected"]:
                    adj["blind_reader_considered_and_rejected"] = only1[c["claim_id"]]["overlaps_reader_2_rejected"]
            else:
                raise wp1b.AdjudicationError(f"{c['claim_id']}: no rule applies")
            if contested:
                if status == "independently_confirmed":
                    status = "adjudicated_modified"
                adj["rules_applied"].append("R1b")
                adj["flags"].append("scope_contested_by_blind_reader")
                adj["notes"].append(wp1b.CONTESTED_NOTE)
            c["claim_validation_status"] = status
            c["evidence_tier"] = wp1b.evidence_tier(status, contested)
            c["adjudication"] = adj
        r2claims = {c["claim_id"]: c for c in r2[iid]["claims"]}
        for b in it["_only2"]:
            if not promoted:
                raise wp1b.AdjudicationError(f"{b['claim_id']}: a blind claim in an item adjudicated {row['adopted_scope']}")
            raw = r2claims[b["claim_id"]]
            new = {"claim_id": f"{iid}-B{b['claim_id'].rsplit('-c', 1)[1]}", "origin": "blind_reader",
                   "blind_claim_id": b["claim_id"], "claim_text": b["text"], "claim_type": b["claim_type"]}
            for d in wp1b.DIMENSIONS:
                dd = {"value": b[d]["value"], "status": b[d]["tag"]}
                if "support" in b[d]:
                    dd["support"] = _with_hash(b[d]["support"])
                if d == "geography":
                    dd["role"] = b["geography_role"]["value"]
                    dd["blind_role_record"] = raw["geography"].get("role")
                new[d] = dd
            new["evidence"] = _with_hash(b["evidence"])
            new["claim_validation_status"] = "single_reader_provisional"
            new["evidence_tier"] = wp1b.evidence_tier("single_reader_provisional", contested)
            ov = next(x for x in it["reader_2_only"] if x["claim_id"] == b["claim_id"])["overlaps_reader_1_rejected"]
            new["adjudication"] = {"package": PKG, "rules_applied": ["R4"], "flags": ["blind_reader_only"],
                                   "notes": ["a new candidate from the blind reader, not confirmed"],
                                   "geography_role": _role_single(b, 2)}
            if ov:
                new["adjudication"]["first_reader_considered_and_rejected"] = ov
            rec["claims"].append(new)
        for c in rec["claims"]:
            counts[c["claim_validation_status"]] += 1
            tiers[c["evidence_tier"]] += 1
        rec["scope_adjudication"] = {"reader_1": row["reader_1_scope"], "reader_2": row["reader_2_scope"],
                                     "adopted": row["adopted_scope"], "rule": row["scope_rule"],
                                     "reader_2_record": f"artifacts/literature/wp4_blind/{row['blind_basename']}",
                                     "reader_2_reason": row["reader_2_reason"]}
        prov = {"package": PKG, "adjudicator": wp4adj.ADJUDICATOR,
                "first_pass_record_sha256": shas[f"artifacts/literature/wp4_claims/{iid}.json"],
                "blind_record_sha256": shas[f"artifacts/literature/wp4_blind/{row['blind_basename']}"],
                "no_paper_re_read": True, "representativeness": wp4adj.REPRESENTATIVENESS}
        if iid == wp4adj.PRIOR_EXPOSURE_ITEM:
            prov["prior_exposure_note"] = wp4adj.PRIOR_EXPOSURE_NOTE
        rec["adjudication_provenance"] = prov
        actions[f"{iid}.json"] = wp1b.write_json(wp4adj.ADJ_DIR / f"{iid}.json", rec)
        per_item.append({"item_id": iid, "adopted_scope": row["adopted_scope"], "n_claims": len(rec["claims"]),
                         "statuses": {s: sum(c["claim_validation_status"] == s for c in rec["claims"]) for s in wp1b.STATUSES},
                         "tiers": {t: sum(c["evidence_tier"] == t for c in rec["claims"]) for t in ("A", "B", "C")}})

    ties = [p["reader_1_claim_id"] for p in all_pairs if p["unresolved_ties"]]
    summary = {"artifact": "M4-WP4 adjudicated claim set", "decision": "D-025 (rules of D-019)",
               "adjudicator": wp4adj.ADJUDICATOR, "prior_exposure": wp4adj.PRIOR_EXPOSURE_NOTE,
               "representativeness": wp4adj.REPRESENTATIVENESS,
               "status_counts": counts, "evidence_tier_counts": tiers, "evidence_tiers": wp1b.EVIDENCE_TIERS,
               "n_claims_total": sum(counts.values()), "overrides_used": [], "unresolved_ties": ties, "items": per_item}
    comparison["phase_d_status_counts"] = counts
    comparison["phase_d_tier_counts"] = tiers
    actions["comparison"] = wp1b.write_json(wp4adj.COMPARISON_PATH, comparison)
    actions["summary"] = wp1b.write_json(wp4adj.ADJ_SUMMARY_PATH, summary)
    doc = render(comparison, summary)
    if wp4adj.DOC_PATH.exists() and wp4adj.DOC_PATH.read_text(encoding="utf-8") != doc:
        print("FAIL: docs/LITERATURE_WP4_ADJUDICATION.md differs from a rebuild", file=sys.stderr)
        return 1
    wp4adj.DOC_PATH.write_text(doc, encoding="utf-8")
    pc = comparison["phase_b_counts"]
    print(f"  scope agreement {stats['scope_agreement']}; aligned {pc['aligned_pairs']}; r1-only {pc['reader_1_only']}; r2-only {pc['reader_2_only']}")
    print(f"  statuses {counts}; tiers {tiers}; ties {ties}")
    rec = write_run_record("wp4_adjudicate", result_summary={"actions": actions, "spans": spans, "counts": pc,
                                                             "statuses": counts, "tiers": tiers, "unresolved_ties": ties},
                           passed=True, data_path=wp4adj.SAMPLE, output_path=wp4adj.COMPARISON_PATH,
                           config_snapshot={"corpus_root": f"config/local_paths.yaml:{wp4adj.ROOT_KEY}",
                                            "reader_1": wp4adj.READER_1_COMMIT, "blind": wp4adj.BLIND_COMMIT})
    print(f"Run record: {repo_relative(rec)}")
    return 0


def _md(s) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _dv(d) -> str:
    return d if isinstance(d, str) else f"{d['value']} [{d['tag']}]"


def render(cmp: dict, summ: dict) -> str:
    st = cmp["phase_c_statistics"]
    pe = cmp["prior_exposure"]
    L = ["# M4-WP4 --- comparison of two readings of the twenty candidates, and adjudication", "",
         "**Generated by `scripts/wp4_adjudicate.py`; do not edit by hand.** Reader 1 is the EXECUTOR "
         f"(prototype-exposed, `{wp4adj.READER_1_COMMIT}`); reader 2 is the blind reader (`{wp4adj.BLIND_COMMIT}`). "
         "**The adjudicator is reader 1.** Rules as M4-WP1b / M4-WP2 (D-019), plus rule 3-role for the geography role; "
         "**no override was used**; no paper was re-read. "
         f"**Sample: {wp4adj.REPRESENTATIVENESS}.**", "",
         f"**Prior exposure.** {pe['note']}", "",
         f"Span integrity: **{cmp['span_verification']['reader_1']}** reader-1 and **{cmp['span_verification']['reader_2']}** "
         "reader-2 spans re-sliced from the hash-verified sources; **0 failures**. Both input sets are pinned by SHA-256 "
         "(`climrr.wp4adj.FROZEN_INPUT_SHA256`, tested).", "",
         "## Scope", "", f"**Agreement {st['scope_agreement']['agree']} / {st['scope_agreement']['n']}.**", "",
         "| Item | Arm | Reader 1 | Reader 2 | Agree | Adopted | Reader 1 reason | Reader 2 reason |",
         "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in cmp["phase_a_scope"]:
        L.append(f"| `{r['item_id']}` | {r['arm'].split('_v')[0]} | {r['reader_1_scope']} | {r['reader_2_scope']} | "
                 f"{'yes' if r['agree'] else '**no**'} | {r['adopted_scope']} | \"{_md(r['reader_1_reason'])}\" | \"{_md(r['reader_2_reason'])}\" |")
    pc = cmp["phase_b_counts"]
    L += ["", "## Alignment", "", f"**{pc['aligned_pairs']} aligned; {pc['reader_1_only']} reader-1-only; {pc['reader_2_only']} reader-2-only.**", "",
          "| Item | Aligned (status) | Reader-1-only | Reader-2-only |", "| --- | --- | --- | --- |"]
    for it in cmp["phase_b_alignment"]:
        L.append(f"| `{it['item_id']}` | " + (", ".join(f"{p['reader_1_claim_id'].rsplit('-', 1)[1]}↔{p['reader_2_claim_id'].rsplit('-', 1)[1]} ({'A' if p['status'] == 'independently_confirmed' else 'B'})" for p in it["pairs"]) or "---")
                 + " | " + (", ".join(a["claim_id"].rsplit("-", 1)[1] for a in it["reader_1_only"]) or "---")
                 + " | " + (", ".join(b["claim_id"].rsplit("-", 1)[1] for b in it["reader_2_only"]) or "---") + " |")
    L += ["", "### Dimension-by-dimension, aligned pairs (disagreements only)", "",
          "Rules: 3a `unknown` beats a value; 3b explicit kept only where the explicit reader's span states the adopted value; "
          "3c same tag, content differs → the span-limited value both support, or `unresolved_tie`.", "",
          "| Claim | Dimension | Reader 1 | Reader 2 | Rule | Adopted |", "| --- | --- | --- | --- | --- | --- |"]
    for it in cmp["phase_b_alignment"]:
        for p in it["pairs"]:
            for d, dec in p["decisions"].items():
                if dec["agree"]:
                    continue
                m = p["mechanical"][d]
                L.append(f"| {p['reader_1_claim_id']} | {d} | {_md(_dv(m['reader_1']))} | {_md(_dv(m['reader_2']))} | {_md(dec['rule'])} | {_md(_dv(dec['adopted']))} |")
    L += ["", "### Geography role, aligned pairs", "",
          f"Role class agreement **{st['geography_role_class_over_aligned_pairs']['class_agreement']} / {st['geography_role_class_over_aligned_pairs']['n_pairs']}**. "
          f"{cmp['role_rule']}", "", "| Claim | Reader 1 role [class] | Reader 2 role [class] | Adopted class |", "| --- | --- | --- | --- |"]
    for it in cmp["phase_b_alignment"]:
        for p in it["pairs"]:
            g = p["geography_role"]
            if g["agree"]:
                continue
            L.append(f"| {p['reader_1_claim_id']} | {_md(g['reader_1']['value'])} [{g['reader_1']['class']}] | "
                     f"{_md(g['reader_2']['value'])} [{g['reader_2']['class']}] | **{g['adopted']['class']}** |")
    L += ["", "### Single-reader claims", ""]
    for it in cmp["phase_b_alignment"]:
        for a in it["reader_1_only"]:
            x = "; **the blind reader had considered and not promoted this passage**" if a["overlaps_reader_2_rejected"] else ""
            L.append(f"- reader-1-only **{a['claim_id']}** (tier C, `not_independently_found`): {_md(a['text'])}{x}")
        for b in it["reader_2_only"]:
            x = "; **reader 1 had considered and not promoted this passage**" if b["overlaps_reader_1_rejected"] else ""
            L.append(f"- reader-2-only **{b['claim_id']}** → `{it['item_id']}-B{b['claim_id'].rsplit('-c', 1)[1]}` (tier C, `blind_reader_only`): {_md(b['text'])}{x}")
    L += ["", "## Agreement (descriptive only)", "", f"_{st['caveat']}_", "", "| Measure | Value |", "| --- | --- |",
          f"| Scope agreement | {st['scope_agreement']['agree']} / {st['scope_agreement']['n']} |",
          f"| Per-item claim-count agreement | {st['per_item_claim_count_agreement']['agree']} / {st['per_item_claim_count_agreement']['n']} |",
          f"| Reader-1 claims aligned | {st['reader_1_claims_with_aligned_reader_2']['aligned']} / {st['reader_1_claims_with_aligned_reader_2']['n']} |",
          f"| Reader-2 claims aligned | {st['reader_2_claims_with_aligned_reader_1']['aligned']} / {st['reader_2_claims_with_aligned_reader_1']['n']} |",
          f"| Geography role class agreement | {st['geography_role_class_over_aligned_pairs']['class_agreement']} / {st['geography_role_class_over_aligned_pairs']['n_pairs']} |",
          "", "| Dimension | Tag agreement | Exact agreement (tag and content) |", "| --- | --- | --- |"]
    for d, v in st["per_dimension_over_aligned_pairs"].items():
        L.append(f"| {d} | {v['tag_agreement']} / {v['n_pairs']} | {v['exact_agreement_tag_and_content']} / {v['n_pairs']} |")
    sc, tc = summ["status_counts"], summ["evidence_tier_counts"]
    L += ["", "## Adjudicated set", "", "| Status | Claims |", "| --- | --- |"] + [f"| {s} | {sc[s]} |" for s in wp1b.STATUSES]
    L += [f"| **total** | **{summ['n_claims_total']}** |", "", "| Evidence tier | Claims |", "| --- | --- |"]
    L += [f"| {t} --- {_md(wp1b.EVIDENCE_TIERS[t])} | {tc[t]} |" for t in ("A", "B", "C")]
    L += ["", f"Unresolved ties: {', '.join(summ['unresolved_ties']) or 'none'} (`not_evaluable` wherever a rule depends on the tied dimension).", "",
          "| Item | Scope | Claims | A | B | C |", "| --- | --- | --- | --- | --- | --- |"]
    L += [f"| `{i['item_id']}` | {i['adopted_scope']} | {i['n_claims']} | {i['tiers']['A']} | {i['tiers']['B']} | {i['tiers']['C']} |" for i in summ["items"]]
    hp = cmp["hit_precision_after_reading"]
    L += ["", "## Hit precision (reader 1, after reading) and the blind reader's geography role", "",
          f"Carried from `{hp['source'].split(' ')[0]}` (SHA-256 `{hp['sha256'][:8]}…`); not an input to any rule above. "
          "Item class = the most substantive class among the item's term pairs (reader 1's convention). For each place-term pair, "
          "the blind reader's claims whose geography names the term are listed, and the most substantive blind role class is compared "
          f"with reader 1's place-hit class (mapping {hp['role_to_hit_class']}; `data_source` and `other` have no counterpart).", "",
          "| Item | Arm | Concept-hit class | Place-hit class | Place term: reader-1 class → blind role (claims) → agreement |",
          "| --- | --- | --- | --- | --- |"]
    for h in hp["items"]:
        cells = "; ".join(f"`{p['term']}`: {p['reader_1_place_hit_class']} → {p['blind_most_substantive_role_class'] or '---'} "
                          f"({', '.join(r['blind_claim_id'].rsplit('-', 1)[1] for r in p['blind_claims_naming_place']) or 'none'}) → **{p['blind_role_vs_place_hit_class']}**"
                          for p in h["place_pairs"])
        L.append(f"| `{h['lit2_id']}` | {h['arm'].split('_v')[0]} | {h['item_concept_class']} | {h['item_place_class']} | {_md(cells)} |")
    v = [p["blind_role_vs_place_hit_class"].split(":")[0] for h in hp["items"] for p in h["place_pairs"]]
    L += ["", f"Place-term pairs: agree **{v.count('agree')}**, disagree **{v.count('disagree')}**, not comparable **{v.count('not_comparable')}** "
          f"(of {len(v)}).", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
