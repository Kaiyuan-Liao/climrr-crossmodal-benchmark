#!/usr/bin/env python3
"""M4-WP1b-adj: compare the first-pass and blind readings, then adjudicate.

Reads the two frozen readings (pinned by hash; neither edited), re-slices every
span of both from the hash-verified corpus files (fail closed), aligns claims by
evidence-span overlap, applies the work package's adjudication rules in order
with the judgements recorded in `climrr.wp1b_judgements`, and writes:

* `artifacts/literature/wp1b_comparison.json` --- Phases A-C;
* `artifacts/literature/wp1_claims_adjudicated/LIT-*.json` and
  `adjudication_summary.json` --- Phase D (originals untouched);
* `docs/LITERATURE_WP1B_ADJUDICATION.md` --- the readable version.

Artifacts are written once; a later run verifies byte equality and fails on
any change. Prints counts only.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import wp1b as w  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.conceptmap import find_term  # noqa: E402
from climrr.litingest import evidence_sha256  # noqa: E402
from climrr.paths import get as get_local_path  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402
from climrr.wp1b_judgements import PAIR_JUDGEMENTS  # noqa: E402

#: Field-13 lexical check. Pilot concept terms are the frozen WP2 concept terms;
#: US-geography terms are the frozen WP2 place terms plus three generic forms.
#: A lexical screen over recorded claim text, not a reading.
US_GENERIC = ("United States", "USA", "U.S.")  # bare "US" omitted: the matcher is case-insensitive and would hit the pronoun


def claim_texts(c: dict) -> list[str]:
    out = [c["text"], c["evidence"]["evidence_text"]]
    for d in w.DIMENSIONS:
        out.append(c[d]["value"])
        if "support" in c[d]:
            out.append(c[d]["support"]["evidence_text"])
    return out


def lexical_screen(c: dict, concept_terms: list[str], place_terms: list[str]) -> dict:
    texts = claim_texts(c)
    hit = lambda terms: sorted({t for t in terms for s in texts if find_term(t, s)})  # noqa: E731
    return {"pilot_concept_terms": hit(concept_terms), "us_geography_terms": hit(place_terms),
            "scenario_tag": c["scenario"]["tag"], "scenario_value": c["scenario"]["value"]}


def rejected_overlaps(c: dict, rejected: list[dict]) -> list[dict]:
    return [{"rejected_id": r["id"], "overlap_code_points": w.overlaps(c["evidence"], r["span"]),
             "reason": r["reason"], "evidence_text": r["span"]["evidence_text"]}
            for r in rejected if w.overlaps(c["evidence"], r["span"]) > 0]


def main() -> int:
    try:
        input_shas = w.verify_inputs()
    except w.AdjudicationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    sample = w.load_sample()
    r1, r2 = w.load_r1(), w.load_r2(sample)
    r2_summary = w.load_r2_summary()
    root = Path(get_local_path("literature_corpus_root"))
    try:
        span_counts = w.verify_all_spans(root, sample, r1, r2)
    except w.AdjudicationError as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 1
    print(f"  spans re-sliced: reader 1 {span_counts['reader_1']}, reader 2 {span_counts['reader_2']}; 0 failures")

    import json
    terms = json.loads((w.LIT / "wp2_terms.json").read_text(encoding="utf-8"))["terms"]
    concept_terms = [t["term"] for t in terms if t["term_class"] == "concept"]
    place_terms = [t["term"] for t in terms if t["term_class"] == "place"] + list(US_GENERIC)

    # Phase A
    scope = w.scope_rows(r1, r2)
    for row in scope:
        row["adopted_scope"], row["scope_rule"] = w.adjudicate_scope(row["reader_1_scope"], row["reader_2_scope"])

    # Phase B + D (rules 2-3)
    items, all_pairs, used_judgements = [], [], set()
    for row in scope:
        iid = row["item_id"]
        c1, c2 = w.claims_of(r1[iid], 1), w.claims_of(r2[iid], 2)
        rej1, rej2 = w.rejected_spans_of(r1[iid], 1), w.rejected_spans_of(r2[iid], 2)
        pairs, only1, only2 = w.align(c1, c2)
        pair_out = []
        for a, b, n in pairs:
            if a["claim_id"] not in PAIR_JUDGEMENTS:
                raise w.AdjudicationError(f"no judgement recorded for aligned pair {a['claim_id']}")
            used_judgements.add(a["claim_id"])
            res = w.resolve_pair(a, b, PAIR_JUDGEMENTS[a["claim_id"]])
            entry = {"reader_1_claim_id": a["claim_id"], "reader_2_claim_id": b["claim_id"],
                     "overlap_code_points": n, "reader_1_evidence": a["evidence"], "reader_2_evidence": b["evidence"],
                     "reader_1_text": a["text"], "reader_2_text": b["text"], **res}
            pair_out.append(entry)
            all_pairs.append(entry)
        items.append({
            "item_id": iid, "blind_basename": row["blind_basename"], "pairs": pair_out,
            "reader_1_only": [{"claim_id": a["claim_id"], "text": a["text"], "evidence": a["evidence"],
                               "overlaps_reader_2_rejected": rejected_overlaps(a, rej2)} for a in only1],
            "reader_2_only": [{"claim_id": b["claim_id"], "text": b["text"], "evidence": b["evidence"],
                               "overlaps_reader_1_rejected": rejected_overlaps(b, rej1)} for b in only2],
            "_c1": c1, "_c2": c2, "_only1": only1, "_only2": only2,
        })
    stray = set(PAIR_JUDGEMENTS) - used_judgements
    if stray:
        raise w.AdjudicationError(f"judgements for pairs that did not align: {sorted(stray)}")

    # Phase C
    n1 = sum(len(i["_c1"]) for i in items)
    n2 = sum(len(i["_c2"]) for i in items)
    both = [r["item_id"] for r in scope if r["reader_1_scope"] == r["reader_2_scope"] == "in_scope_hazard"]
    n1b = sum(len(i["_c1"]) for i in items if i["item_id"] in both)
    n2b = sum(len(i["_c2"]) for i in items if i["item_id"] in both)
    stats = w.statistics(scope, all_pairs, n1, n2, both, n1b, n2b)

    # Field-13 screen, both readers, so the asymmetry is visible
    screen = {"method": ("boundary-aware lexical match (climrr.conceptmap.find_term) of the frozen WP2 concept terms "
                         "and of the WP2 place terms plus " + ", ".join(US_GENERIC) + " over every recorded text of each "
                         "claim (claim text, evidence, dimension values, support spans); scenario read from the tag. "
                         "A screen of recorded claims, not a reading of any paper."),
              "concept_terms": concept_terms, "place_terms": place_terms, "claims": []}
    for it in items:
        for reader, cs in (("reader_1", it["_c1"]), ("reader_2", it["_c2"])):
            for c in cs:
                screen["claims"].append({"reader": reader, "item_id": it["item_id"], "claim_id": c["claim_id"],
                                         **lexical_screen(c, concept_terms, place_terms)})
    r2_only_ids = {b["claim_id"] for it in items for b in it["_only2"]}
    flagged = [s for s in screen["claims"] if s["pilot_concept_terms"] or s["us_geography_terms"] or s["scenario_tag"] != "unknown"]
    screen["flagged_any_reader"] = flagged
    screen["reader_2_only_flagged"] = [s for s in flagged if s["claim_id"] in r2_only_ids]
    screen["answer"] = ("The blind reader found no claim with US geography, an emissions scenario, or a pilot concept "
                        "term that reader 1 missed." if not screen["reader_2_only_flagged"] else
                        "The blind reader found claim(s) reader 1 missed that carry a flagged dimension; see reader_2_only_flagged.")

    comparison = {
        "artifact": "M4-WP1b comparison of two readings (Phases A-C)",
        "authorized_by": "docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md (D-018), Track A",
        "inputs": {"reader_1": "artifacts/literature/wp1_claims/ (M4-WP1 EXECUTOR, prototype-exposed)",
                   "reader_2": f"artifacts/literature/wp1b_blind/ (blind reader, frozen at {w.BLIND_COMMIT})",
                   "sha256": input_shas},
        "reader_2_disclosed_deviations_verbatim": r2_summary["protocol_notes"],
        "span_verification": {**span_counts, "failures": 0,
                              "rule": "every span of both readings re-sliced from the hash-verified decoded source"},
        "alignment_rule": ("same normalised json_path and overlapping [char_start, char_end); one-to-one or the run fails; "
                           "reader-2 raw keys normalised to $-paths with climrr.litingest.child_path"),
        "phase_a_scope": scope,
        "phase_b_alignment": [{k: v for k, v in it.items() if not k.startswith("_")} for it in items],
        "phase_b_counts": {"aligned_pairs": len(all_pairs),
                           "reader_1_only": sum(len(i["_only1"]) for i in items),
                           "reader_2_only": sum(len(i["_only2"]) for i in items)},
        "phase_c_statistics": stats,
        "field_13_screen": screen,
    }

    # Phase D: adjudicated records
    w.ADJ_DIR.mkdir(exist_ok=True)
    status_counts = {s: 0 for s in w.STATUSES}
    flags_count: dict[str, int] = {}
    adj_files = {}
    per_item = []
    for it, row in zip(items, scope):
        iid = it["item_id"]
        rec = w.deep(r1[iid])
        adopted_scope = row["adopted_scope"]
        pair_by_r1 = {p["reader_1_claim_id"]: p for p in it["pairs"]}
        only1_ids = {a["claim_id"] for a in it["_only1"]}
        for c in rec["claims"]:
            c["first_pass_claim_validation_status"] = c["claim_validation_status"]
            adj = {"package": "M4-WP1b-adj", "rules_applied": [], "flags": [], "notes": []}
            if adopted_scope == "ambiguous" and row["reader_1_scope"] != "ambiguous":
                status = "rejected_on_review"
                adj["rules_applied"].append("R1c")
                adj["notes"].append(row["scope_rule"])
            elif adopted_scope == w.CONTESTED:
                status = "adjudicated_modified"
                adj["rules_applied"].append("R1b")
                adj["flags"].append("scope_contested_by_blind_reader")
                adj["notes"].append(w.CONTESTED_NOTE)
                if c["claim_id"] in only1_ids:
                    adj["rules_applied"].append("R4 (flag only; R1b governs the status)")
                    adj["flags"].append("not_independently_found")
                    ov = next(a for a in it["reader_1_only"] if a["claim_id"] == c["claim_id"])["overlaps_reader_2_rejected"]
                    if ov:
                        adj["blind_reader_considered_and_rejected"] = ov
            elif c["claim_id"] in pair_by_r1:
                p = pair_by_r1[c["claim_id"]]
                status = p["status"]
                adj["rules_applied"].append(p["rule"])
                adj["aligned_blind_claim_id"] = p["reader_2_claim_id"]
                adj["blind_evidence"] = p["reader_2_evidence"]
                adj["dimension_decisions"] = p["decisions"]
                if status == "adjudicated_modified":
                    adopted = {}
                    for d, dec in p["decisions"].items():
                        if not dec["agree"]:
                            adopted[d] = dec["adopted"]
                    adj["adopted_dimensions"] = adopted
                    adj["notes"].append("claim_text is reader 1's, unchanged; adopted_dimensions replace the "
                                        "differing dimensions for downstream use; both readers' values are kept above")
                if p["unresolved_ties"]:
                    adj["flags"].append("unresolved_tie")
                    adj["unresolved_ties"] = p["unresolved_ties"]
                if p["overrides"]:
                    adj["judgement_overrides"] = p["overrides"]
            elif c["claim_id"] in only1_ids:
                status = "single_reader_provisional"
                adj["rules_applied"].append("R4")
                adj["flags"].append("not_independently_found")
                ov = next(a for a in it["reader_1_only"] if a["claim_id"] == c["claim_id"])["overlaps_reader_2_rejected"]
                if ov:
                    adj["blind_reader_considered_and_rejected"] = ov
            else:
                raise w.AdjudicationError(f"{c['claim_id']}: no rule applies")
            c["claim_validation_status"] = status
            c["adjudication"] = adj
            status_counts[status] += 1
            for f in adj["flags"]:
                flags_count[f] = flags_count.get(f, 0) + 1
        # rule 4: reader-2-only claims added as new candidates
        for b in it["_only2"]:
            if adopted_scope == "ambiguous":
                raise w.AdjudicationError(f"{b['claim_id']}: blind-only claim on an ambiguous item")
            n = b["claim_id"].rsplit("-C", 1)[1]
            ev = dict(b["evidence"])
            ev["offset_convention"] = rec["offset_convention"]
            ev["evidence_sha256"] = evidence_sha256(ev["evidence_text"])
            new = {"claim_id": f"{iid}-B{n}", "origin": "blind_reader", "blind_claim_id": b["claim_id"],
                   "claim_text": b["text"], "claim_type": b["claim_type"]}
            for d in w.DIMENSIONS:
                dd = w.to_r1_dim(b[d])
                if "support" in dd:
                    dd["support"] = dict(dd["support"], offset_convention=rec["offset_convention"],
                                         evidence_sha256=evidence_sha256(dd["support"]["evidence_text"]))
                new[d] = dd
            new["evidence"] = ev
            new["claim_validation_status"] = "single_reader_provisional"
            ov = next(x for x in it["reader_2_only"] if x["claim_id"] == b["claim_id"])["overlaps_reader_1_rejected"]
            new["adjudication"] = {"package": "M4-WP1b-adj", "rules_applied": ["R4"], "flags": ["blind_reader_only"],
                                   "notes": ["a new candidate from the blind reader, not confirmed"]}
            if ov:
                new["adjudication"]["first_reader_considered_and_rejected"] = ov
            rec["claims"].append(new)
            status_counts["single_reader_provisional"] += 1
            flags_count["blind_reader_only"] = flags_count.get("blind_reader_only", 0) + 1
        adj_terminal = ("ambiguous_only" if adopted_scope == "ambiguous" else
                        "claims_extracted" if rec["claims"] else rec["terminal_status"])
        rec["scope_adjudication"] = {"reader_1": row["reader_1_scope"], "reader_2": row["reader_2_scope"],
                                     "adopted": adopted_scope, "rule": row["scope_rule"],
                                     "reader_2_record": f"artifacts/literature/wp1b_blind/{row['blind_basename']}",
                                     "reader_2_reason": row["reader_2_reason"],
                                     "adjudicated_terminal_status": adj_terminal}
        rec["adjudication_provenance"] = {
            "package": "M4-WP1b-adj", "adjudicator": "the WP1 EXECUTOR (prototype-exposed; also reader 1)",
            "first_pass_record_sha256": input_shas[f"artifacts/literature/wp1_claims/{iid}.json"],
            "blind_record_sha256": input_shas[f"artifacts/literature/wp1b_blind/{row['blind_basename']}"],
            "no_paper_re_read": True}
        path = w.ADJ_DIR / f"{iid}.json"
        adj_files[path.name] = w.write_json(path, rec)
        per_item.append({"item_id": iid, "adopted_scope": adopted_scope, "adjudicated_terminal_status": adj_terminal,
                         "statuses": {s: sum(1 for c in rec["claims"] if c["claim_validation_status"] == s) for s in w.STATUSES}})

    summary = {
        "artifact": "M4-WP1b adjudicated claim set (Phase D)",
        "rules": ["R1 scope (a agree; b in_scope vs ambiguous -> contested, claims adjudicated_modified; c off_topic vs other -> ambiguous, zero promoted)",
                  "R2 aligned and agreeing on concept, direction and all explicit dimensions -> independently_confirmed, reader-1 text kept, both spans cited",
                  "R3 aligned and differing -> more conservative value (unknown beats a value; inferred beats explicit only where the explicit span does not state it), adjudicated_modified, both values recorded; ties recorded as unresolved_tie",
                  "R4 reader-1-only -> single_reader_provisional, not_independently_found; reader-2-only -> added as single_reader_provisional, blind_reader_only",
                  "R5 nothing deleted; every first-pass claim keeps its id and gains a status"],
        "adjudicator": "the WP1 EXECUTOR (prototype-exposed; also reader 1). GUIDANCE may require a third party for contested items.",
        "status_counts": status_counts,
        "status_counts_first_pass_claims_only": {s: status_counts[s] - (flags_count.get("blind_reader_only", 0) if s == "single_reader_provisional" else 0) for s in w.STATUSES},
        "flag_counts": flags_count,
        "n_claims_total": sum(status_counts.values()),
        "items": per_item,
        "judgement_overrides": sorted({o for p in all_pairs for o in p["overrides"]}),
        "unresolved_ties": [{"claim_id": p["reader_1_claim_id"], "dimensions": p["unresolved_ties"]} for p in all_pairs if p["unresolved_ties"]],
    }
    comparison["phase_d_status_counts"] = status_counts
    a_cmp = w.write_json(w.COMPARISON_PATH, comparison)
    a_sum = w.write_json(w.ADJ_SUMMARY_PATH, summary)
    doc = render_doc(comparison, summary)
    if w.DOC_PATH.exists() and w.DOC_PATH.read_text(encoding="utf-8") != doc:
        print("FAIL: docs/LITERATURE_WP1B_ADJUDICATION.md differs from a rebuild", file=sys.stderr)
        return 1
    w.DOC_PATH.write_text(doc, encoding="utf-8")

    pc = comparison["phase_b_counts"]
    print(f"  scope agreement {stats['scope_agreement']['agree']}/{stats['scope_agreement']['n']}")
    print(f"  aligned {pc['aligned_pairs']}; reader-1-only {pc['reader_1_only']}; reader-2-only {pc['reader_2_only']}")
    print(f"  statuses {status_counts}")
    print(f"  field-13: {screen['answer']}")
    shas = {repo_relative(p): sha256_file(p) for p in [w.COMPARISON_PATH, w.ADJ_SUMMARY_PATH, w.DOC_PATH, *sorted(w.ADJ_DIR.glob('LIT-*.json'))]}
    record = write_run_record(
        "wp1b_adjudicate",
        result_summary={"actions": {"comparison": a_cmp, "summary": a_sum, **adj_files}, "sha256": shas,
                        "span_counts": span_counts, "phase_b_counts": pc, "status_counts": status_counts,
                        "scope_agreement": stats["scope_agreement"], "field_13_answer": screen["answer"]},
        passed=True,
        data_path=w.SAMPLE_PATH,
        output_path=w.COMPARISON_PATH,
        config_snapshot={"corpus_root": "config/local_paths.yaml:literature_corpus_root",
                         "frozen_inputs": len(w.FROZEN_INPUT_SHA256), "blind_commit": w.BLIND_COMMIT},
    )
    print(f"Run record: {repo_relative(record)}")
    return 0


# --- rendering -------------------------------------------------------------------


def _md(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _dimval(d) -> str:
    if isinstance(d, str):
        return d
    return f"{d['value']} [{d['tag']}]"


def render_doc(cmp: dict, summ: dict) -> str:
    st = cmp["phase_c_statistics"]
    L = []
    L += ["# M4-WP1b --- comparison of two readings and adjudication", "",
          "**Generated by `scripts/wp1b_adjudicate.py` from the two frozen readings; do not edit by hand.** "
          "Reader 1 is the M4-WP1 EXECUTOR (prototype-exposed); reader 2 is the blind reader frozen at "
          f"`{w.BLIND_COMMIT}`. The adjudicator is **the WP1 EXECUTOR** --- reader 1 itself --- applying the work "
          "package's rules first and recorded judgements second. **No paper was re-read.** GUIDANCE may require a "
          "third party for contested items.", "",
          "Ten items, deterministically sampled; **not representative of the corpus.** Statistics below are "
          "descriptive counts on a very small n, not estimates of reliability.", "",
          "## Blind reader's disclosed deviations (verbatim)", ""]
    L += [f"- {_md(x)}" for x in cmp["reader_2_disclosed_deviations_verbatim"]]
    sv = cmp["span_verification"]
    L += ["", f"Span integrity: **{sv['reader_1']}** reader-1 spans and **{sv['reader_2']}** reader-2 spans re-sliced "
          "from the hash-verified sources; **0 failures**.", "",
          "## Phase A --- scope", "",
          f"**Scope agreement: {st['scope_agreement']['agree']} / {st['scope_agreement']['n']}.**", "",
          "| Item | Blind file | Reader 1 | Reader 2 | Agree | Adopted (rule) |", "| --- | --- | --- | --- | --- | --- |"]
    for r in cmp["phase_a_scope"]:
        L.append(f"| `{r['item_id']}` | `{r['blind_basename']}` | {r['reader_1_scope']} | {r['reader_2_scope']} | "
                 f"{'yes' if r['agree'] else '**no**'} | {r['adopted_scope']} ({r['scope_rule'].split(':')[0]}) |")
    L += ["", "Reasons, quoted from each record:", ""]
    for r in cmp["phase_a_scope"]:
        L += [f"- **`{r['item_id']}`** --- reader 1: \"{_md(r['reader_1_reason'])}\" --- reader 2: \"{_md(r['reader_2_reason'])}\""]
    pc = cmp["phase_b_counts"]
    L += ["", "## Phase B --- claim alignment", "",
          f"Rule: {cmp['alignment_rule']}.", "",
          f"**Aligned pairs {pc['aligned_pairs']}; reader-1-only {pc['reader_1_only']}; reader-2-only {pc['reader_2_only']}.**", "",
          "| Item | Aligned pairs | Reader-1-only | Reader-2-only |", "| --- | --- | --- | --- |"]
    for it in cmp["phase_b_alignment"]:
        L.append(f"| `{it['item_id']}` | " + (", ".join(f"{p['reader_1_claim_id']}↔{p['reader_2_claim_id']}" for p in it["pairs"]) or "---")
                 + " | " + (", ".join(a["claim_id"] for a in it["reader_1_only"]) or "---")
                 + " | " + (", ".join(b["claim_id"] for b in it["reader_2_only"]) or "---") + " |")
    L += ["", "### Disagreement table (aligned pairs, differing dimensions only)", "",
          "| Reader-1 claim | Dimension | Reader 1 | Reader 2 | Rule | Adopted |", "| --- | --- | --- | --- | --- | --- |"]
    for it in cmp["phase_b_alignment"]:
        for p in it["pairs"]:
            for d, dec in p["decisions"].items():
                if dec["agree"]:
                    continue
                m = p["mechanical"][d]
                r1v = m["reader_1"] if d == "claim_type" else _dimval(m["reader_1"])
                r2v = m["reader_2"] if d == "claim_type" else _dimval(m["reader_2"])
                ad = _dimval(dec["adopted"])
                if "override" in dec:
                    ad += f" (override {dec['override']['judgement_id']}; rule gave {_dimval(dec['rule_result'])})"
                L.append(f"| {p['reader_1_claim_id']} | {d} | {_md(r1v)} | {_md(r2v)} | {_md(dec['rule'])} | {_md(ad)} |")
    L += ["", "### Unaligned claims", ""]
    for it in cmp["phase_b_alignment"]:
        for a in it["reader_1_only"]:
            extra = "; **reader 2 considered and rejected this passage**: \"" + _md(a["overlaps_reader_2_rejected"][0]["reason"]) + "\"" if a["overlaps_reader_2_rejected"] else ""
            L.append(f"- reader-1-only **{a['claim_id']}**: {_md(a['text'])}{extra}")
        for b in it["reader_2_only"]:
            extra = "; **reader 1 considered and rejected this passage**: \"" + _md(b["overlaps_reader_1_rejected"][0]["reason"]) + "\"" if b["overlaps_reader_1_rejected"] else ""
            L.append(f"- reader-2-only **{b['claim_id']}** (`{it['item_id']}`): {_md(b['text'])}{extra}")
    L += ["", "## Phase C --- agreement statistics (descriptive only)", "", f"_{st['caveat']}_", "",
          "| Measure | Value |", "| --- | --- |",
          f"| Scope agreement | {st['scope_agreement']['agree']} / {st['scope_agreement']['n']} |",
          f"| Per-item claim-count agreement | {st['per_item_claim_count_agreement']['agree']} / {st['per_item_claim_count_agreement']['n']} (equal counts ≠ same claims) |",
          f"| Reader-1 claims with an aligned reader-2 claim | {st['reader_1_claims_with_aligned_reader_2']['aligned']} / {st['reader_1_claims_with_aligned_reader_2']['n']} |",
          f"| Reader-2 claims with an aligned reader-1 claim | {st['reader_2_claims_with_aligned_reader_1']['aligned']} / {st['reader_2_claims_with_aligned_reader_1']['n']} |",
          f"| Same, on the {len(st['restricted_to_items_both_in_scope']['items'])} items both readers put in scope | reader 1 {st['restricted_to_items_both_in_scope']['reader_1_aligned']['aligned']} / {st['restricted_to_items_both_in_scope']['reader_1_aligned']['n']}; reader 2 {st['restricted_to_items_both_in_scope']['reader_2_aligned']['aligned']} / {st['restricted_to_items_both_in_scope']['reader_2_aligned']['n']} |",
          "", "Per dimension, over the aligned pairs (exact = same tag **and** judged same content):", "",
          "| Dimension | Tag agreement | Exact agreement | Rate |", "| --- | --- | --- | --- |"]
    for d, v in st["per_dimension_over_aligned_pairs"].items():
        L.append(f"| {d} | {v['tag_agreement']} / {v['n_pairs']} | {v['exact_agreement_tag_and_content']} / {v['n_pairs']} | {v['exact_agreement_rate']} |")
    sc = summ["status_counts"]
    L += ["", "## Phase D --- adjudicated claim set", "",
          "Rules, applied in order:", ""] + [f"{i}. {_md(r)}" for i, r in enumerate(summ["rules"], 1)] + [
          "", "Rule 3 in practice: where two values differ in extent, the adopted value is the part both readers "
          "support **and the cited span states** --- never the union. Adopted dimensions sit beside reader 1's "
          "unchanged claim text in each record; both readers' values are kept.", "",
          "| Status | All claims | First-pass claims only |", "| --- | --- | --- |"]
    for s in w.STATUSES:
        L.append(f"| {s} | {sc[s]} | {summ['status_counts_first_pass_claims_only'][s]} |")
    L.append(f"| **total** | **{summ['n_claims_total']}** | **{sum(summ['status_counts_first_pass_claims_only'].values())}** |")
    L += ["", "Flags: " + ", ".join(f"`{k}` × {v}" for k, v in sorted(summ["flag_counts"].items())) + ".", "",
          "Post-rule judgement overrides: " + (", ".join(summ["judgement_overrides"]) or "none") +
          (" --- the wildfire-smoke exposure regimen, recorded by both readers under different dimensions, is kept in "
           "`experimental_condition` rather than lost to rule 3a; the rule result is recorded beside it."
           if summ["judgement_overrides"] == ["J-1"] else "."),
          "", "Unresolved ties: " + ("; ".join(f"{t['claim_id']} ({', '.join(t['dimensions'])})" for t in summ["unresolved_ties"]) or "none") + ".", "",
          "| Item | Adopted scope | Terminal | confirmed | modified | provisional | rejected |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for i in summ["items"]:
        s = i["statuses"]
        L.append(f"| `{i['item_id']}` | {i['adopted_scope']} | {i['adjudicated_terminal_status']} | {s['independently_confirmed']} | "
                 f"{s['adjudicated_modified']} | {s['single_reader_provisional']} | {s['rejected_on_review']} |")
    scr = cmp["field_13_screen"]
    L += ["", "## Did the blind reading find what relevance-guided sampling is for?", "",
          f"Method: {scr['method']}", "",
          f"Claims flagged in either reading: **{len(scr['flagged_any_reader'])}**; flagged among reader-2-only claims: "
          f"**{len(scr['reader_2_only_flagged'])}**. {scr['answer']}", ""]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
