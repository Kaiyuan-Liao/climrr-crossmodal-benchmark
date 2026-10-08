"""M4-WP1b: compare the first-pass and blind readings, then adjudicate.

Two frozen inputs, neither edited:

* **reader 1** --- `artifacts/literature/wp1_claims/` (the M4-WP1 EXECUTOR,
  prototype-exposed; 27 claims);
* **reader 2** --- `artifacts/literature/wp1b_blind/` (the blind reader at
  `87bce48`; 21 claims), keyed by corpus basename and mapped to LIT ids through
  `wp1_sample.json`.

Everything mechanical lives here: input pinning, span re-slicing, path
normalisation, alignment by evidence-span overlap, tag comparison, the
adjudication rules of the work package applied **in order**, and the
statistics. Every place a human reading of two recorded values is needed ---
"do these two values say the same thing", "does this support span actually
state this value" --- is supplied by `climrr.wp1b_judgements`, which this
module validates against the rules rather than trusting.

No corpus file is re-read for meaning. The corpus is opened only to re-slice
recorded spans (fail closed on any mismatch, as the work package requires).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from climrr.checksums import sha256_file
from climrr.litingest import IntegrityError, child_path, evidence_sha256, read_verified, resolve
from climrr.paths import REPO_ROOT

LIT = REPO_ROOT / "artifacts" / "literature"
R1_DIR = LIT / "wp1_claims"
R1_SUMMARY = LIT / "wp1_claims_summary.json"
R2_DIR = LIT / "wp1b_blind"
R2_SUMMARY = R2_DIR / "wp1b_blind_summary.json"
SAMPLE_PATH = LIT / "wp1_sample.json"
COMPARISON_PATH = LIT / "wp1b_comparison.json"
ADJ_DIR = LIT / "wp1_claims_adjudicated"
ADJ_SUMMARY_PATH = ADJ_DIR / "adjudication_summary.json"
DOC_PATH = REPO_ROOT / "docs" / "LITERATURE_WP1B_ADJUDICATION.md"

BLIND_COMMIT = "87bce48"

#: Both readings as committed (reader 2 at `87bce48`, reader 1 at the M4-WP1
#: closure). A comparison is only meaningful against these exact bytes.
FROZEN_INPUT_SHA256 = {
    "artifacts/literature/wp1_claims/LIT-000001.json": "fb618e99761c266777d36df7a740a008903657640fdb0c2eb86b67869062fac6",
    "artifacts/literature/wp1_claims/LIT-000191.json": "04269ea82b9ff3317d9cf66898c96014ae7de9c17e584d25cae613eb290d6ba5",
    "artifacts/literature/wp1_claims/LIT-000381.json": "1113784e769f520f373e783f95cefa12336fbde6c53f7ed65cf2f78f53f3152a",
    "artifacts/literature/wp1_claims/LIT-000571.json": "c473d3cb7cbf09be67153a510f4efe349875b916a2282a15d12866034c86ffd8",
    "artifacts/literature/wp1_claims/LIT-000761.json": "1dccff144e11a9ab4d8341c9e2e5d3b543283b5177c855904005ab9d068643bc",
    "artifacts/literature/wp1_claims/LIT-000951.json": "5034397d52ee7437e7cd490558e12558dfba3c03b36bf36a2a22591073a8306c",
    "artifacts/literature/wp1_claims/LIT-001141.json": "007719936968055d94b2fd8d32e8b30e83d36d8c926b9ccd94f6dc4626d3862c",
    "artifacts/literature/wp1_claims/LIT-001331.json": "4df7adc8103f0b55089a5d7ca697b6aa35a99c0845c508ddb9b2e9a3bf3397cf",
    "artifacts/literature/wp1_claims/LIT-001521.json": "9efe23aedba6202e3555b9ca781a8aa87b0c20a47d8f8a066634c944f0470810",
    "artifacts/literature/wp1_claims/LIT-001711.json": "95991a9e3297a80c40d905e30874343b70c1de6e3304eb85454955be4c5d260b",
    "artifacts/literature/wp1_claims_summary.json": "fb913fe4242355af17794b1218ab30b88d0abe84ce53f5c89cf71a18c1f9cdde",
    "artifacts/literature/wp1b_blind/100961700.json": "46d53bc75b6ef80c83bc5a239bcc5f36bd7f5b231461ceb386d993cd4af5ebbe",
    "artifacts/literature/wp1b_blind/15420300.json": "f7769d9c3df66ffea5747da203d983f9bd7e04e03e4b66e9fde5b4269e0e16b1",
    "artifacts/literature/wp1b_blind/211092500.json": "1afa78d43ffe1cfcda059f66a03559803ab234f9d4b23485d48384171653b1d3",
    "artifacts/literature/wp1b_blind/225107600.json": "86568a5b80430654529c140406725bbf677eacaa3f4f24d6c03ac88932607156",
    "artifacts/literature/wp1b_blind/235097800.json": "904404d247c83881a80048533ce249678f66e5d36237ced9fa4e9f7ede96ccb7",
    "artifacts/literature/wp1b_blind/242697800.json": "e5bf6767111dc793ccedd962ec9d45c5ad3a04e7191a463ca4cc978148efe592",
    "artifacts/literature/wp1b_blind/251972000.json": "9e2cb2129e3b5e5e0750b74b7cfa146fc8f2f0d2157c3d89369042bc93114845",
    "artifacts/literature/wp1b_blind/259631800.json": "49b1267f6d4c8c41db7bcdb899a1ed4a717bc499d251f268a50c6584808de94d",
    "artifacts/literature/wp1b_blind/271744500.json": "6914ec02070845d7cc9ab1979d615a28599a1f4d2e7989f3c6f0bb7dfd20b1f0",
    "artifacts/literature/wp1b_blind/54542600.json": "adc00ea75b3df109f153457f08683680a7ed1420bb091dd17795f741ba034c5a",
    "artifacts/literature/wp1b_blind/wp1b_blind_summary.json": "e732867f2afd73283c76662e1244a8b8cd44ba7e4a6dcf1ebb85003c192ff7df",
    "artifacts/literature/wp1_sample.json": "5cb81f9585040dd1d73a89ca7062d3c5e0060112f54e08ef4795db96a657b578",
}

DIMENSIONS = ("concept", "relation_or_direction", "geography", "temporal_frame", "scenario", "experimental_condition")
COMPARED = DIMENSIONS + ("claim_type",)

STATUSES = ("independently_confirmed", "adjudicated_modified", "single_reader_provisional", "rejected_on_review")
CONTESTED = "in_scope_hazard (contested)"
CONTESTED_NOTE = "scope contested by blind reader"


class AdjudicationError(RuntimeError):
    """An input, span, judgement or rule application is inconsistent."""


# --- inputs ---------------------------------------------------------------------


def verify_inputs() -> dict:
    """Every pinned input file byte-identical; no unpinned file in either reading."""
    observed = {}
    for rel, expected in FROZEN_INPUT_SHA256.items():
        got = sha256_file(REPO_ROOT / rel)
        if got != expected:
            raise AdjudicationError(f"{rel}: SHA-256 {got} != frozen {expected}")
        observed[rel] = got
    for d in (R1_DIR, R2_DIR):
        present = {str(p.relative_to(REPO_ROOT)) for p in d.glob("*.json")}
        extra = present - set(FROZEN_INPUT_SHA256)
        if extra:
            raise AdjudicationError(f"unpinned file(s) in a frozen reading: {sorted(extra)}")
    return observed


def load_sample() -> dict:
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


def basename_to_item(sample: dict) -> dict:
    return {i["relative_path"].removesuffix(".json"): i["item_id"] for i in sample["items"]}


def load_r1() -> dict:
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(R1_DIR.glob("LIT-*.json"))}


def load_r2(sample: dict) -> dict:
    """Reader-2 records keyed by LIT id."""
    b2i = basename_to_item(sample)
    out = {}
    for p in sorted(R2_DIR.glob("*.json")):
        if p.name == R2_SUMMARY.name:
            continue
        out[b2i[p.stem]] = json.loads(p.read_text(encoding="utf-8"))
    if set(out) != set(b2i.values()):
        raise AdjudicationError("reader 2 does not cover exactly the ten sampled items")
    return out


def load_r2_summary() -> dict:
    return json.loads(R2_SUMMARY.read_text(encoding="utf-8"))


# --- spans ----------------------------------------------------------------------


def norm_path(p: str) -> str:
    """Reader 2 records the raw key; reader 1 a `$...` path. Return the `$...` form."""
    return p if p.startswith("$") else child_path("$", p)


def iter_spans(obj, where: str = ""):
    """Every recorded span (any dict with json_path + offsets), with a locator."""
    if isinstance(obj, dict):
        if "json_path" in obj and "char_start" in obj and "char_end" in obj:
            yield where, obj
        for k, v in obj.items():
            yield from iter_spans(v, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_spans(v, f"{where}[{i}]")


def check_one_span(doc: object, span: dict) -> None:
    value = resolve(doc, norm_path(span["json_path"]))
    if not isinstance(value, str):
        raise IntegrityError(f"{span['json_path']} is not a string")
    s, e = span["char_start"], span["char_end"]
    if not (isinstance(s, int) and isinstance(e, int) and 0 <= s < e <= len(value)):
        raise IntegrityError(f"{span['json_path']}: bad span [{s}, {e})")
    if value[s:e] != span["evidence_text"]:
        raise IntegrityError(f"{span['json_path']} [{s}, {e}): slice != evidence_text")
    if "evidence_sha256" in span and evidence_sha256(span["evidence_text"]) != span["evidence_sha256"]:
        raise IntegrityError(f"{span['json_path']} [{s}, {e}): evidence_sha256 mismatch")


def verify_all_spans(corpus_root: Path, sample: dict, r1: dict, r2: dict) -> dict:
    """Re-slice every span of both readings from hash-verified sources. Fail closed."""
    by_id = {i["item_id"]: i for i in sample["items"]}
    counts = {"reader_1": 0, "reader_2": 0}
    for item_id, meta in by_id.items():
        doc, err = read_verified(Path(corpus_root) / meta["relative_path"], meta["sha256"])
        if err:
            raise AdjudicationError(f"{item_id}: {err}")
        for label, rec in (("reader_1", r1[item_id]), ("reader_2", r2[item_id])):
            for where, span in iter_spans(rec):
                try:
                    check_one_span(doc, span)
                except (IntegrityError, KeyError, ValueError) as exc:
                    raise AdjudicationError(f"{label} {item_id}{where}: span fails to re-slice: {exc}") from exc
                counts[label] += 1
    return counts


# --- normalised claim views -----------------------------------------------------


def _dim(d: dict, reader: int) -> dict:
    tag = d["status"] if reader == 1 else d["tag"]
    sup = d.get("support") if reader == 1 else d.get("support_span")
    out = {"value": d["value"], "tag": tag}
    if sup:
        out["support"] = _span(sup)
    return out


def _span(s: dict) -> dict:
    out = {"json_path": norm_path(s["json_path"]), "char_start": s["char_start"],
           "char_end": s["char_end"], "evidence_text": s["evidence_text"]}
    if "occurrence_note" in s:
        out["occurrence_note"] = s["occurrence_note"]
    return out


def claims_of(rec: dict, reader: int) -> list[dict]:
    out = []
    for c in rec["claims"]:
        view = {
            "claim_id": c["claim_id"],
            "text": c["claim_text"] if reader == 1 else c["restatement"],
            "claim_type": c["claim_type"],
            "evidence": _span(c["evidence"]),
        }
        for d in DIMENSIONS:
            view[d] = _dim(c[d], reader)
        out.append(view)
    return out


def rejected_spans_of(rec: dict, reader: int) -> list[dict]:
    out = []
    for i, r in enumerate(rec["rejected_or_ambiguous"]):
        sp = r["evidence"] if reader == 1 else r
        ident = r.get("candidate_id", f"{i}") if reader == 1 else f"rejected[{i}]"
        out.append({"id": ident, "span": _span(sp), "reason": r["reason"]})
    return out


def overlaps(a: dict, b: dict) -> int:
    if a["json_path"] != b["json_path"]:
        return 0
    return max(0, min(a["char_end"], b["char_end"]) - max(a["char_start"], b["char_start"]))


# --- Phase A: scope -------------------------------------------------------------


def scope_rows(r1: dict, r2: dict) -> list[dict]:
    rows = []
    for item_id in sorted(r1):
        a, b = r1[item_id], r2[item_id]
        rows.append({
            "item_id": item_id,
            "blind_basename": b["source_file"],
            "reader_1_scope": a["scope_status"],
            "reader_2_scope": b["scope_status"],
            "agree": a["scope_status"] == b["scope_status"],
            "reader_1_reason": a["scope_reason"],
            "reader_2_reason": b["scope_reason"],
            "reader_1_terminal": a["terminal_status"],
            "reader_2_terminal": b["terminal_status"],
            "reader_1_n_claims": len(a["claims"]),
            "reader_2_n_claims": len(b["claims"]),
        })
    return rows


def adjudicate_scope(s1: str, s2: str) -> tuple[str, str]:
    """Rule 1. Returns (adopted scope, rule label)."""
    if s1 == s2:
        return s1, "R1a: both readers agree; adopted"
    pair = {s1, s2}
    if "off_topic" in pair:
        return "ambiguous", "R1c: one reader off_topic, the other not; scope ambiguous, zero promoted claims"
    if pair == {"in_scope_hazard", "ambiguous"}:
        return CONTESTED, "R1b: in_scope_hazard vs ambiguous; claims proceed, each adjudicated_modified"
    raise AdjudicationError(f"no scope rule for {s1!r} vs {s2!r}")


# --- Phase B: alignment ---------------------------------------------------------


def align(c1: list[dict], c2: list[dict]) -> tuple[list[tuple[dict, dict, int]], list[dict], list[dict]]:
    """One-to-one alignment by evidence overlap (same path, overlapping [start, end)).

    Fails if any claim overlaps more than one claim of the other reader: a
    many-to-one overlap would need a judgement the rule does not give.
    """
    pairs = []
    for a in c1:
        hits = [(b, overlaps(a["evidence"], b["evidence"])) for b in c2]
        hits = [(b, n) for b, n in hits if n > 0]
        if len(hits) > 1:
            raise AdjudicationError(f"{a['claim_id']} overlaps several reader-2 claims")
        if hits:
            pairs.append((a, hits[0][0], hits[0][1]))
    used2 = [b["claim_id"] for _, b, _ in pairs]
    if len(used2) != len(set(used2)):
        raise AdjudicationError("a reader-2 claim overlaps several reader-1 claims")
    only1 = [a for a in c1 if a["claim_id"] not in {p[0]["claim_id"] for p in pairs}]
    only2 = [b for b in c2 if b["claim_id"] not in used2]
    return pairs, only1, only2


def _norm(v: str) -> str:
    return " ".join(str(v).split()).casefold()


def mechanical_diff(a: dict, b: dict) -> dict:
    """Per dimension: tags, values, tag equality, exact (normalised) value equality."""
    out = {}
    for d in DIMENSIONS:
        x, y = a[d], b[d]
        out[d] = {"reader_1": x, "reader_2": y, "tag_agree": x["tag"] == y["tag"],
                  "value_identical": _norm(x["value"]) == _norm(y["value"])}
    out["claim_type"] = {"reader_1": a["claim_type"], "reader_2": b["claim_type"],
                         "tag_agree": True, "value_identical": a["claim_type"] == b["claim_type"]}
    return out


# --- Phase D: rules 2-3 on an aligned pair --------------------------------------


def resolve_pair(a: dict, b: dict, judgement: dict) -> dict:
    """Apply rules 2 and 3 to one aligned pair, with the recorded judgements.

    For each dimension the judgement gives `content` (`same` / `differs`) where
    the values are not identical. Rule 3 is then applied mechanically:

    * either tag `unknown` and the dimension differs -> adopted `unknown` (3a);
    * explicit vs inferred -> the judgement must say whether the explicit
      reader's support (or evidence) span actually states the adopted value
      (`explicit_span_states`); explicit only if it does (3b);
    * same tag, content differs -> the judgement's span-limited adopted value,
      or `unresolved_tie` (3c).

    A post-rule `override` is allowed only with a judgement id and reason, and
    is reported separately.
    """
    mech = mechanical_diff(a, b)
    judgement = {k: _materialise(v, a, b, k) for k, v in judgement.items()}
    decisions, differs_any, ties, overrides = {}, False, [], []
    for d in COMPARED:
        m = mech[d]
        j = judgement.get(d, {})
        if m["value_identical"] and m["tag_agree"]:
            if j and j.get("content") == "differs":
                raise AdjudicationError(f"{a['claim_id']} {d}: identical values judged as differing")
            decisions[d] = {"agree": True, "rule": "identical"}
            continue
        if "content" not in j:
            raise AdjudicationError(f"{a['claim_id']} {d}: values differ textually; a content judgement is required")
        content_same = j["content"] == "same"
        agree = content_same and m["tag_agree"]
        dec = {"agree": agree, "content_judgement": j["content"], "note": j.get("note", "")}
        if agree:
            dec["rule"] = "judged same content, same tag"
            decisions[d] = dec
            continue
        differs_any = True
        if d == "claim_type":
            if j.get("adopted") == "unresolved_tie":
                dec.update(rule="3c: claim_type differs; no conservative order; unresolved_tie", adopted="unresolved_tie")
                ties.append(d)
            else:
                dec.update(rule="3c: claim_type adopted by judgement", adopted=j["adopted"])
            decisions[d] = dec
            continue
        t1, t2 = m["reader_1"]["tag"], m["reader_2"]["tag"]
        if "unknown" in (t1, t2):
            dec.update(rule="3a: unknown beats a value", adopted={"value": "unknown", "tag": "unknown"})
        elif t1 != t2:
            if "explicit_span_states" not in j or "adopted" not in j:
                raise AdjudicationError(f"{a['claim_id']} {d}: explicit vs inferred needs explicit_span_states and adopted")
            tag = "explicit" if j["explicit_span_states"] else "inferred"
            if j["adopted"]["tag"] != tag:
                raise AdjudicationError(f"{a['claim_id']} {d}: adopted tag {j['adopted']['tag']} contradicts rule 3b ({tag})")
            explicit_reader = "r1" if t1 == "explicit" else "r2"
            if tag == "explicit" and not j["adopted"].get("support_from", "").startswith(explicit_reader):
                raise AdjudicationError(f"{a['claim_id']} {d}: explicit kept, so its support must be the explicit reader's span")
            dec.update(rule="3b: explicit kept only where its span states the adopted value" if tag == "explicit"
                       else "3b: inferred beats explicit; the explicit span does not state it",
                       explicit_span_states=j["explicit_span_states"], adopted=j["adopted"])
        else:
            if j.get("adopted") == "unresolved_tie":
                dec.update(rule="3c: same tag, content differs; unresolved_tie", adopted="unresolved_tie")
                ties.append(d)
            else:
                if "adopted" not in j:
                    raise AdjudicationError(f"{a['claim_id']} {d}: same tag, content differs; adopted value required")
                if j["adopted"]["tag"] != t1:
                    raise AdjudicationError(f"{a['claim_id']} {d}: rule 3c keeps the shared tag")
                dec.update(rule="3c: same tag, content differs; span-limited value both readers support", adopted=j["adopted"])
        if "override" in j:
            ov = j["override"]
            if not ov.get("judgement_id") or not ov.get("reason"):
                raise AdjudicationError(f"{a['claim_id']} {d}: override without judgement id and reason")
            dec["rule_result"] = dec["adopted"]
            dec["adopted"] = ov["adopted"]
            dec["override"] = {"judgement_id": ov["judgement_id"], "reason": ov["reason"]}
            overrides.append(ov["judgement_id"])
        decisions[d] = dec
    status = "adjudicated_modified" if differs_any else "independently_confirmed"
    return {"status": status, "rule": "R3" if differs_any else "R2", "decisions": decisions,
            "unresolved_ties": ties, "overrides": overrides, "mechanical": mech}


def _support(src: str, a: dict, b: dict, d: str) -> dict:
    """`r1`/`r2`: that reader's support span for the dimension; `*_evidence`: its claim evidence."""
    claim = a if src.startswith("r1") else b
    if src.endswith("_evidence"):
        return claim["evidence"]
    sup = claim[d].get("support")
    if sup is None:
        raise AdjudicationError(f"{claim['claim_id']} {d}: support_from {src!r} but that reader cites no support span")
    return sup


def _materialise(j: dict, a: dict, b: dict, d: str) -> dict:
    j = copy.deepcopy(j)
    for key in ("adopted",):
        ad = j.get(key)
        if isinstance(ad, dict) and "support_from" in ad:
            ad["support"] = _support(ad["support_from"], a, b, d)
    ov = j.get("override")
    if ov and isinstance(ov.get("adopted"), dict) and "support_from" in ov["adopted"]:
        ov["adopted"]["support"] = _support(ov["adopted"]["support_from"], a, b, d)
    return j


# --- Phase C: statistics ---------------------------------------------------------


def statistics(scope: list[dict], pairs: list[dict], n1: int, n2: int, both_in_scope: list[str],
               n1_in_both: int, n2_in_both: int) -> dict:
    per_dim = {}
    for d in COMPARED:
        tag_agree = sum(1 for p in pairs if p["mechanical"][d]["tag_agree"])
        exact = sum(1 for p in pairs if p["decisions"][d]["agree"])
        per_dim[d] = {"n_pairs": len(pairs), "tag_agreement": tag_agree,
                      "exact_agreement_tag_and_content": exact,
                      "exact_agreement_rate": round(exact / len(pairs), 3) if pairs else None}
    return {
        "caveat": ("n is small (10 items, 19 aligned pairs at most). These are descriptive counts of two "
                   "readings, not estimates of reader reliability, and support no inferential statement."),
        "scope_agreement": {"agree": sum(r["agree"] for r in scope), "n": len(scope)},
        "per_item_claim_count_agreement": {
            "agree": sum(r["reader_1_n_claims"] == r["reader_2_n_claims"] for r in scope), "n": len(scope),
            "note": "equal counts do not imply the same claims (see alignment)"},
        "reader_1_claims_with_aligned_reader_2": {"aligned": len(pairs), "n": n1},
        "reader_2_claims_with_aligned_reader_1": {"aligned": len(pairs), "n": n2},
        "restricted_to_items_both_in_scope": {
            "items": both_in_scope,
            "reader_1_aligned": {"aligned": len(pairs), "n": n1_in_both},
            "reader_2_aligned": {"aligned": len(pairs), "n": n2_in_both}},
        "per_dimension_over_aligned_pairs": per_dim,
    }


# --- adjudicated records ---------------------------------------------------------


def to_r1_dim(d: dict) -> dict:
    out = {"value": d["value"], "status": d["tag"]}
    if "support" in d:
        out["support"] = d["support"]
    return out


def write_json(path: Path, obj: dict) -> str:
    text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise AdjudicationError(f"{path.relative_to(REPO_ROOT)} differs from a rebuild; adjudicated artifacts are frozen")
        return "verified"
    path.write_text(text, encoding="utf-8")
    return "written"


def deep(obj):
    return copy.deepcopy(obj)
