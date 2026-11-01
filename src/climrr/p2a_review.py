"""Pilot P2a review workbook, SEEDS CSV and the generated `docs/LITSTATEMENTS_RUN2.md` (Phases D and F).

The workbook `artifacts/benchmark/review/P2a_clusters_and_seeds_v1.xlsx` (gitignored) has
the sheets OVERVIEW, SEEDS (one row per eligible seed), CLUSTERS (one row per multi-source
or review-supported cluster), STATEMENTS (all 1,018), PARSE_ERRORS (21) and Legend; the
SEEDS sheet is also written as the tracked `P2a_seeds_v1.csv`. Where the GUIDANCE field
order applies, columns follow it: statement, type, strength, scope, supports.

The doc is rendered from tracked files only (the run-2 manifest, `papers_meta.json`,
`parse_errors.json`, `clusters_v1_summary.json`, `item_seeds_v1_summary.json`), so a test
can re-render it without the gitignored seeds file. No model call, no table value.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from climrr import itemseeds as sd
from climrr import litaggregate as la
from climrr import litstatements_run2 as r2
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

REVIEW_DIR = REPO_ROOT / "artifacts" / "benchmark" / "review"
WORKBOOK_PATH = REVIEW_DIR / "P2a_clusters_and_seeds_v1.xlsx"
SEEDS_CSV_PATH = REVIEW_DIR / "P2a_seeds_v1.csv"
DOC_PATH = REPO_ROOT / "docs" / "LITSTATEMENTS_RUN2.md"
AGENT_PATH = REPO_ROOT / "scripts" / "litcollect" / "litstatement_agent.py"
PASSAGE_CHARS = 300


def _load(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _clip(s: str | None, n: int = PASSAGE_CHARS) -> str:
    s = s or ""
    return s if len(s) <= n else s[: n - 1] + "…"


def _value(p: dict) -> str:
    v = p["computed_value_or_range"]
    parts = []
    if v.get("value") is not None:
        parts.append(f"{v['value']} {v.get('unit', '')}".strip())
    if v.get("range"):
        parts.append(f"range {v['range']['min']}..{v['range']['max']} ({v['range']['over']})")
    if p["pattern_kind"] == "regional_contrast":
        parts.append(" > ".join(f"{r['name']} {r['value']}" for r in v["regions_ordered"]))
    if p["pattern_kind"] == "seasonal_contrast":
        parts.append("; ".join(f"{s}: {d['majority_direction']} {d['share_cells_increase']}" for s, d in sorted(v["per_season"].items())))
    if v.get("value_reason"):
        parts.append(f"({v['value_reason']})")
    return "; ".join(parts)


# --- sheets ---------------------------------------------------------------------------------------

SEED_HEADER = (["seed_rank", "seed_id", "use_case_level", "family", "pattern_kind", "geography_type", "geography",
                "season", "horizon", "horizon_window", "scenario", "statistic", "direction", "computed_value_or_range",
                "pattern_robustness", "robustness_share"]
               + [f"cluster{i}_{f}" for i in (1, 2, 3) for f in ("statement", "type", "strength", "scope", "supports", "id")]
               + ["acceptance_blockers", "eligibility_relies_on_diagnostic_pair", "pattern_id"])


def seed_rows(seeds: list[dict], clusters_by_id: dict) -> list[list]:
    rows = [SEED_HEADER]
    for s in sorted((s for s in seeds if s["eligible_for_pilot"]), key=lambda s: s["seed_rank_key"]):
        p = s["pattern"]
        row = [s["seed_rank_key"], s["seed_id"], s["use_case_level"], s["family"], s["pattern_kind"], s["geography_type"],
               s["geography"], s["season"], s["horizon"], s["horizon_window"], s["scenario"], s["statistic"], s["direction"],
               _value(p), p.get("pattern_robustness"), p.get("robustness_share")]
        for ref in (s["clusters"] + [None] * 3)[:3]:
            if ref is None:
                row += [""] * 6
                continue
            c = clusters_by_id[ref["cluster_id"]]
            row += [c["representative_statement"]["statement"], c["statement_type"], c["evidence_strength"],
                    f"{ref['relevance']} ({ref['geography_match'] or 'none'}); regions: {'; '.join(c['regions_named']) or 'none named'}",
                    f"{c['n_papers']} papers ({c['n_independent_papers']} independent): {', '.join(c['papers'])}", c["cluster_id"]]
        row += ["; ".join(b["blocker"] for b in s["acceptance_blockers"]), s["eligibility_relies_on_diagnostic_pair"], p["pattern_id"]]
        rows.append(row)
    return rows


CLUSTER_HEADER = ["representative_statement", "statement_type", "evidence_strength", "region_scopes", "regions_named",
                  "supports_n_papers", "n_independent_papers", "papers", "cluster_id", "arm", "direction", "n_statements",
                  "scenarios_named", "member_statements", "multi_source_relies_on_diagnostic_pair"]


def cluster_rows(clusters: list[dict]) -> list[list]:
    rows = [CLUSTER_HEADER]
    keep = [c for c in clusters if c["evidence_strength"] in ("multi_source_supported", "review_supported")]
    for c in sorted(keep, key=lambda c: (la.STRENGTHS.index(c["evidence_strength"]), c["cluster_id"])):
        rows.append([c["representative_statement"]["statement"], c["statement_type"], c["evidence_strength"],
                     "; ".join(f"{k}: {v}" for k, v in c["region_scopes"].items()), "; ".join(c["regions_named"]),
                     c["n_papers"], c["n_independent_papers"], ", ".join(c["papers"]), c["cluster_id"], c["arm"], c["direction"],
                     c["n_statements"], "; ".join(c["scenarios_named"]),
                     " | ".join(f"{m['statement_id']} ({m['evidence_role']}): {m['statement']}" for m in c["members"]),
                     c["multi_source_relies_on_diagnostic_pair"]])
    return rows


STATEMENT_HEADER = ["statement_id", "statement", "statement_type", "evidence_role", "region_scope", "region", "paper_item_id",
                    "passage_300", "passage_type", "generality", "recovery", "precheck_status", "rejected_checks", "cluster_id",
                    "cluster_evidence_strength", "arm"]


def statement_rows(records: list[dict], clusters: list[dict]) -> list[list]:
    member_of = {m: c for c in clusters for m in c["member_statement_ids"]}
    rows = [STATEMENT_HEADER]
    for r in records:
        c = member_of.get(r["statement_id"])
        g = r["proposal"]
        rows.append([r["statement_id"], g.get("statement"), g.get("statement_type"), r["evidence_role"], g.get("region_scope"),
                     g.get("region"), r["paper_item_id"], _clip(r["verbatim_passage"] or r["passage_as_proposed"]),
                     g.get("passage_type"), g.get("generality"), r["recovery"], r["precheck_status"], "; ".join(r["rejected_checks"]),
                     c["cluster_id"] if c else "", c["evidence_strength"] if c else "", r["arm"]])
    return rows


PARSE_HEADER = ["item_id", "arm", "paper_chars", "truncated", "finish_reason", "completion_tokens", "content_chars",
                "reasoning_chars", "model_parse_error"]


def parse_rows(perr: list[dict]) -> list[list]:
    return [PARSE_HEADER] + [[p[k] for k in PARSE_HEADER] for p in perr]


def overview_rows(man: dict, cs: dict, ss: dict) -> list[list]:
    k = man["counts"]
    rows = [["item", "value"],
            ["run", "litstatements run 2 (agent v2, Sophia vLLM openai/gpt-oss-120b; D-043, D-044)"],
            ["tarball sha256", man["tarball"]["sha256"]], ["papers", k["papers"]], ["statements", k["statements"]],
            ["deterministic_pass", k["deterministic_pass"]], ["rejected_pre_review", k["rejected_pre_review"]],
            ["parse errors (finish_reason length)", k["parse_errors"]]]
    rows += [[f"evidence role: {r}", n] for r, n in k["evidence_roles"].items()]
    rows += [["aggregation rule", f"{cs['rule']} (cosine >= {cs['threshold']}; DF filter > {cs['df_max_share']:.0%})"],
             ["statements entering", cs["entering_statements"]], ["clusters", cs["clusters"]], ["singleton clusters", cs["singletons"]]]
    rows += [[f"clusters {s}", n] for s, n in cs["by_strength"].items()]
    rows += [["multi-source clusters resting on a diagnostic pair", ", ".join(cs["multi_source_relies_on_diagnostic_pair"]) or "none"],
             ["seeds", ss["seeds"]], ["eligible seeds (DR-SEED-1)", ss["eligible"]],
             ["eligible seeds not resting on a diagnostic pair", ss["eligible_without_diagnostic_pair"]],
             ["FWI seeds / acceptance-blocked / eligible", f"{ss['fwi']['seeds']} / {ss['fwi']['acceptance_blocked']} / {ss['fwi']['eligible']}"]]
    rows += [[f"eligible seeds via {c}", n] for c, n in ss["eligible_cluster_ids"].items()]
    return rows


LEGEND = [["field", "meaning"],
          ["evidence_role", "core_candidate: pass + own_finding/own_projection/review_synthesis; cited_candidate: pass + cited_finding; "
                            "background_consensus_candidate: rejected only for a background passage that re-sliced; unusable: otherwise (D-044)"],
          ["evidence_strength", "multi_source_supported: >= 2 independent papers (DR-LIT-IND-1) with core or cited statements; "
                                "review_supported: a review_synthesis member; single_source_supported: one paper with core or cited statements; "
                                "background_only: background passages only (D-045)"],
          ["cluster", "DR-LIT-AGG-1 v2: arm x statement_type x lexical direction; unigrams + bigrams, per-arm DF filter > 15 %, "
                      "IDF-weighted cosine, union-find at 0.30. Lexical only: paraphrases stay apart (semantic merging is P2b)"],
          ["representative_statement", "the member with the highest mean cosine to the other members (ties: lowest id); verbatim, never a paraphrase"],
          ["scope (SEEDS)", "geography_relevant / geography_other (DR-SEED-1) with the basis that matched: state, nca_region, us_term or scope"],
          ["supports", "papers in the cluster; independence is assumed for distinct ids (authors absent from the corpus index)"],
          ["seed_rank", "EXECUTOR-defined seed order: more eligible clusters first, then the top-three cluster rank keys, then pattern id"],
          ["acceptance_blockers", "IC-006..IC-010: FWI summer value columns inferred_candidate (block eligibility); IC-012: provisional State label (carried)"],
          ["eligibility_relies_on_diagnostic_pair", "every qualifying cluster is multi-source only through papers with an equal file hash or title"],
          ["passage_300", "the re-sliced verbatim passage (or, if it did not re-slice, the passage as proposed), clipped to 300 characters"],
          ["status", "nothing here is accepted: seeds are candidates for P2b synthesis and human review"]]


def workbook_sheets(man, cs, ss, seeds, clusters, records, perr) -> list[tuple]:
    by_id = {c["cluster_id"]: c for c in clusters}
    return [("OVERVIEW", overview_rows(man, cs, ss), [52, 90]),
            ("SEEDS", seed_rows(seeds, by_id), [8, 18, 8, 12, 12, 12, 14, 10, 8, 12, 10, 14, 10, 50, 14, 12]
             + [60, 10, 18, 40, 40, 30] * 3 + [20, 10, 12]),
            ("CLUSTERS", cluster_rows(clusters), [70, 12, 22, 30, 40, 8, 8, 30, 34, 14, 12, 8, 20, 100, 10]),
            ("STATEMENTS", statement_rows(records, clusters), [20, 70, 12, 26, 12, 24, 12, 70, 16, 18, 12, 10, 30, 34, 22, 14]),
            ("PARSE_ERRORS", parse_rows(perr), [12, 16, 10, 8, 10, 10, 10, 10, 40]),
            ("Legend", LEGEND, [32, 120])]


def seeds_csv(rows: list[list]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    for r in rows:
        w.writerow(["" if v is None else v for v in r])
    return buf.getvalue()


# --- the generated doc -------------------------------------------------------------------------------


def _t(header: list[str], rows: list[list]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    out += ["| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in r) + " |" for r in rows]
    return out


def render_doc(man: dict, meta: dict, perr: list[dict], cs: dict, ss: dict, agent_sha: str) -> str:
    k = man["counts"]
    L = ["# Literature-statement run 2 --- ingest, aggregation and item seeds (pilot P2a)", "",
         "*Generated by `scripts/build_p2a_review.py` from tracked files; do not edit by hand.* Decisions **D-044** (run 2",
         "accepted as the pilot's literature-statement evidence) and **D-045** (deterministic aggregation and seeding rules",
         "v1). **No model call. No item generated. Nothing accepted:** clusters and seeds are candidates for P2b synthesis",
         "and human review. No column status, concept-map entry or compatibility rule changed.", "",
         "## 1. Run facts", ""]
    L += _t(["", ""], [
        ["tarball", f"`litstatements_run2_evidence.tar.gz` `{man['tarball']['sha256']}`"],
        ["agent", f"`{man['generator']['version']}` `{man['generator']['agent_sha256']}`; system prompt `{man['generator']['system_prompt_sha256']}`"],
        ["endpoint", f"`{man['endpoint']['endpoint_label']}` `{man['endpoint']['model']}` on all {man['endpoint']['papers']} records"],
        ["source commit", f"`{man['source_commit']}`"],
        ["run window (UTC)", f"{man['log']['start_utc']} -- {man['log']['end_utc']}; {man['log']['retry_lines']} RETRY lines, {man['log']['fail_lines']} FAIL"],
        ["papers / statements", f"{k['papers']} / {k['statements']} ({k['papers_with_error']} papers with error)"],
        ["pre-check", f"{k['deterministic_pass']} `deterministic_pass`, {k['rejected_pre_review']} `rejected_pre_review`"],
        ["rejections by check", ", ".join(f"`{c}` {n}" for c, n in sorted(k["rejected_by_check"].items(), key=lambda x: -x[1]))
         + " (a statement may fail several)"],
        ["parse errors", f"{k['parse_errors']} papers, no statement recorded"],
        ["superseded", "; ".join(f"{s['run']} ({s['endpoint']}, {s['papers']} papers with output, {s['reason']}, {s['decision']}; "
                                 f"{s['observed']['paper_dirs']} paper directories, agent `{s['observed']['generator_version']}`) --- recorded, not ingested"
                                 for s in man["superseded_runs"])],
    ])
    L += ["", "Ingested into `artifacts/litstatements/run2/` (`manifest.json` lists every file's SHA-256): the run files, every",
          "`result.json` as `papers/<item_id>.json`, and `statements_ingested.jsonl`. `prompt_user.txt` (the paper text) and",
          "`response.json` were not copied; their SHA-256 are in the manifest.", "",
          "## 2. Evidence roles (D-044)", ""]
    L += _t(["role", "rule", "statements"], [
        ["`core_candidate`", "pass; passage_type own_finding / own_projection / review_synthesis", k["evidence_roles"]["core_candidate"]],
        ["`cited_candidate`", "pass; passage_type cited_finding", k["evidence_roles"]["cited_candidate"]],
        ["`background_consensus_candidate`", "rejected only by `passage_type_pass` (a background passage), passage re-sliced",
         k["evidence_roles"]["background_consensus_candidate"]],
        ["`unusable`", "everything else (passage not found, invalid enum, numeric value, length)", k["evidence_roles"]["unusable"]]])
    L += ["", "Statement ids `LS-<item_id>-<nn>`, nn = the position in the paper's list (the agent's `S-<item_id>-<nn>`).", "",
          "## 3. Independence (DR-LIT-IND-1)", "",
          meta["rule"], "",
          f"The corpus index stores per document only {', '.join(f'`{f}`' for f in meta['index_fields']['docs'])} and per section "
          f"{', '.join(f'`{f}`' for f in meta['index_fields']['sections'][2:])}. **Year, venue and authors are absent**, so every check is "
          f"`author_check: unavailable` and the basis is `{meta['independence_basis']}`. {meta['n_title_section_present']} of "
          f"{len(meta['papers'])} papers have a `title` section.", "",
          "Diagnostics the rule does not use (for the reviewer):", ""]
    L += [f"- equal file SHA-256: {', '.join(' = '.join(g) for g in meta['diagnostic_same_file_sha256']) or 'none'}",
          f"- equal title section: {', '.join(' = '.join(g) for g in meta['diagnostic_same_title_section']) or 'none'}", ""]
    L += ["## 4. Aggregation (DR-LIT-AGG-1 v2)", "",
          "**The first rule degenerated.** The work package's rule (Jaccard >= 0.35 on unigrams, plus a merge of any two",
          "statements sharing >= 2 of the arm's 60 most frequent tokens) let `fire` + `weather` or `heat` + `temperature`",
          "join almost any pair, so nearly every arm x type x direction partition became one cluster, whatever the",
          "threshold. Replayed on the same statements:", ""]
    L += _t(["Jaccard", "concept-lexicon merge", "clusters", "singletons", "multi-source", "largest", "five largest"],
            [[r["threshold"], r["concept_lexicon_merge"], r["clusters"], r["singletons"], r["multi_source_clusters"], r["largest"],
              ", ".join(map(str, r["five_largest"]))] for r in cs["rule_v1_degeneracy"]])
    L += ["", "The COORDINATOR replaced it on 2026-11-01 (D-045) with **DR-LIT-AGG-1 v2**, deliberately conservative:", "",
          "1. Partition: arm x statement_type x direction; direction from `direction_lexicon_v1.yaml` (a term from one list and",
          "   none from the other; otherwise `unspecified`).",
          "2. Tokens: lowercase; characters outside [a-z0-9] become spaces; `stopwords_v1.yaml`, one-character and all-digit",
          "   words dropped; crude lemmatizer, first rule that fits: `-ing` (word > 5 chars), `-ed` (> 4), `-s` but not `-ss` (> 3).",
          "   Content unigrams plus bigrams of tokens adjacent after the removal.",
          f"3. Document-frequency filter: within an arm, a gram in more than {cs['df_max_share']:.0%} of the arm's entering statements is dropped",
          "   (`df_filter_dropped_v1.yaml`).",
          "4. Similarity: cosine of binary vectors weighted by IDF = ln(N/df) over the arm's entering statements.",
          f"5. Union-find within a partition at cosine >= {cs['threshold']}. No concept-lexicon merge: `concept_lexicon_v1.yaml` is a frequency",
          "   table only.",
          "6. The representative statement is the member with the highest mean cosine to the others (the work package said",
          "   Jaccard, the first rule's similarity; v2 uses its own); ties go to the lowest id. It is verbatim.", "",
          "Semantic merging of paraphrases (which may upgrade clusters) is P2b --- agent-proposed, human-checked, never code.", ""]
    L += _t(["file", "SHA-256"], [[f"`{v['path']}`", f"`{v['sha256']}`"] for v in cs["lexicons"].values()]
            + [[f"`{cs['clusters_file']['path']}`", f"`{cs['clusters_file']['sha256']}`"]])
    L += ["", "Grams dropped by the DF filter:", ""]
    L += [f"- `{a}`: " + ", ".join(f"{g} ({n})" for g, n in d.items()) for a, d in cs["df_dropped"].items()]
    L += ["", f"**Entering:** {cs['entering_statements']} statements ("
          + ", ".join(f"{a} {n}" for a, n in cs["entering_by_arm"].items()) + "; "
          + ", ".join(f"{r} {n}" for r, n in cs["entering_by_role"].items()) + ").", "",
          f"**Clusters:** {cs['clusters']}, of which **{cs['singletons']} singletons**; "
          + ", ".join(f"{s} {n}" for s, n in cs["by_strength"].items()) + ".", "",
          "Threshold sensitivity (the rule is not changed by it):", ""]
    L += _t(["measure", "threshold", "clusters", "singletons", "multi-source", "largest", "clusters > 25"],
            [[r["measure"], r["threshold"], r["clusters"], r["singletons"], r["multi_source_clusters"], r["largest"], r["clusters_over_25"]]
             for r in cs["sensitivity"]])
    L += ["", "Clusters by arm x type x evidence strength:", ""]
    L += _t(["arm", "type"] + list(la.STRENGTHS),
            [[r["arm"], r["statement_type"]] + [r[s] for s in la.STRENGTHS] for r in cs["by_arm_type_strength"]])
    L += ["", "**The ten largest clusters** (by statements, then papers, then id):", ""]
    L += _t(["cluster", "statements", "papers", "strength", "direction", "representative statement"],
            [[f"`{c['cluster_id']}`", c["n_statements"], c["n_papers"], c["evidence_strength"], c["direction"], c["representative"]]
             for c in cs["largest"]])
    relied = cs["multi_source_relies_on_diagnostic_pair"]
    L += ["", f"Multi-source clusters that rest on a diagnostic pair: {', '.join(f'`{c}`' for c in relied) or 'none'}.", "",
          "## 5. Item seeds (DR-SEED-1)", "",
          "One seed per table pattern (`table_patterns_v1.jsonl`, `ed3c2154…f3b0`) with the clusters that could explain it:",
          "family must match (heat_index <-> `extreme_heat_v1`, fire_weather_index <-> `fire_weather_v1`); the cluster's",
          "direction equals the pattern's or is `unspecified`; a cluster is `geography_relevant` if a member's region string",
          "names the pattern's state, its NCA5 region (`nca_regions_v1.yaml`), a covered region of a regional contrast, or",
          "\"United States\" / \"US\" / \"CONUS\" / \"contiguous\" (periods removed, whole words), or a member's scope is global /",
          "national; otherwise `geography_other`, still listed. Rank: strength (multi > review > single > background), relevant",
          "first, more independent papers; EXECUTOR tie-breaks: more statements, cluster id. `use_case_level` (D-038, proposed),",
          "first that applies: regional contrast with a cluster -> 4; a mechanism / driver cluster -> 3; a caveat cluster naming",
          "a scenario -> 7; else 1. **Eligible**: not `acceptance_blocked`, computed (EXECUTOR: a `not_computable` pattern has no",
          "value), and >= 1 `multi_source_supported` mechanism / driver cluster that is geography_relevant. Seed order",
          "(EXECUTOR-defined): more eligible clusters, then the top-three cluster keys, then pattern id.", ""]
    L += _t(["", ""], [
        ["seeds", ss["seeds"]], ["by family", ", ".join(f"{f} {n}" for f, n in ss["by_family"].items())],
        ["by kind", ", ".join(f"{f} {n}" for f, n in ss["by_kind"].items())],
        ["by use-case level (first that applies)", ", ".join(f"{lv}: {n}" for lv, n in ss["by_level"].items())],
        ["levels that apply (any)", ", ".join(f"{lv}: {n}" for lv, n in ss["levels_applicable"].items())],
        ["**eligible**", f"**{ss['eligible']}** ({', '.join(f'{f} {n}' for f, n in ss['eligible_by_family'].items())}; "
                         f"levels {', '.join(f'{lv}: {n}' for lv, n in ss['eligible_by_level'].items())})"],
        ["eligible through each cluster", ", ".join(f"`{c}` {n}" for c, n in ss["eligible_cluster_ids"].items())],
        ["**eligible, not resting on a diagnostic pair**", f"**{ss['eligible_without_diagnostic_pair']}**"],
        ["not_computable patterns kept out of eligibility", ss["eligible_not_computable_excluded"]],
        ["FWI seeds", f"{ss['fwi']['seeds']}: {ss['fwi']['acceptance_blocked']} acceptance-blocked (IC-006..IC-010, FWI summer value), "
                      f"{ss['fwi']['not_blocked']} not blocked (verified percent-change columns), {ss['fwi']['eligible']} eligible"],
        ["seeds file", f"`{ss['seeds_file']['path']}` (gitignored) `{ss['seeds_file']['sha256']}`"]])
    L += ["", "**The ten highest-ranked eligible seeds** (pattern, then its top three clusters):", ""]
    for t in ss["top_eligible"]:
        L += [f"{t['seed_rank_key']}. `{t['seed_id']}` --- level {t['use_case_level']}; blockers {', '.join(t['acceptance_blockers']) or 'none'}"
              + ("; **rests on a diagnostic pair**" if t["eligibility_relies_on_diagnostic_pair"] else ""),
              f"   {t['pattern_summary']}"]
        L += [f"   - [{c['rank']}] `{c['cluster_id']}` {c['evidence_strength']}, {c['relevance']} ({c['geography_match']}), "
              f"{c['n_papers']} papers: \"{c['representative']}\"" for c in t["top_clusters"]]
    a = ss["geography_match_audit"]
    L += ["", "Region strings matched by a place name (for review; whole-word matching, no gazetteer):", ""]
    L += [f"- {n}: " + "; ".join(f"\"{r}\"" for r in v) for n, v in a["place_names"].items()]
    L += ["", f"Clusters relevant to every pattern of their family and direction only through a global / national scope (no member "
          f"names a U.S. place): {a['scope_only_clusters']} ("
          + ", ".join(f"{s} {n}" for s, n in a["scope_only_by_strength"].items()) + "); multi-source among them: "
          + (", ".join(f"`{c}`" for c in a["scope_only_multi_source"]) or "none") + ".", "",
          "## 6. Parse errors", "",
          f"{len(perr)} papers recorded `model_parse_error` and no statement. `response.json` (not copied) was read for counts only:",
          f"**every one ended with `finish_reason: {', '.join(sorted({p['finish_reason'] for p in perr}))}` at "
          f"{', '.join(map(str, sorted({p['completion_tokens'] for p in perr})))} completion tokens** --- the `--max-tokens` cap",
          "cut the JSON off; the raw text exists in the delivered `response.json`. No second pass for the pilot (D-044).", ""]
    L += _t(["item", "arm", "paper chars", "truncated", "finish", "completion tokens", "content chars", "reasoning chars"],
            [[p["item_id"], p["arm"], p["paper_chars"], p["truncated"], p["finish_reason"], p["completion_tokens"],
              p["content_chars"], p["reasoning_chars"]] for p in perr])
    L += ["", f"Agent v3 (`{agent_sha}`, not run; system prompt unchanged) stores `raw_response` --- and `raw_reasoning` when the",
          "content fallback fired --- in every `result.json`, truncated to 20,000 characters, plus `finish_reason`.", "",
          "## 7. Limitations", "",
          "- **Lexical clustering only.** Paraphrases of one claim stay in separate clusters, so most clusters are singletons and",
          "  `multi_source_supported` is rare and conservative; semantic merging is P2b.",
          "- **Author, year and venue data are absent** from the corpus index; independence is assumed for distinct ids. The two",
          "  diagnostics show this assumption fails at least once: a byte-identical paper under two ids, whose cluster is one of",
          "  the multi-source clusters and supplies most eligible seeds.",
          "- **Global / national scope makes a cluster relevant to every U.S. pattern** of its family and direction, whatever",
          "  nation it names (DR-SEED-1 as written); name matching has no gazetteer (e.g. \"Sierra Nevada\" -> Nevada, \"Brazil and",
          "  Southeast Asia\" -> Southeast, \"Georgia\").",
          "- **The multi-source clusters are not hazard mechanisms of the kind the ladder needs**: one is a dataset-validation",
          "  statement whose two members are both cited findings (possibly the same cited study), one links heat index to a health",
          "  outcome, one is the duplicated paper.",
          "- Some extreme-heat statements concern the Thornthwaite heat index (a potential-evapotranspiration parameter), not",
          "  humid heat; the lexical rules cannot tell them apart.",
          "- **No raw text was stored by agent v2** for the 21 parse errors; the delivered `response.json` holds it, and v3 keeps it.",
          "- Direction is lexical: a statement such as \"lower humidity raises fire danger\" has terms from both lists and is",
          "  `unspecified`.", ""]
    return "\n".join(L) + "\n"


def doc_inputs() -> tuple:
    return (_load(r2.MANIFEST_PATH), _load(r2.PAPERS_META_PATH), _load(r2.PARSE_ERRORS_PATH), _load(la.SUMMARY_PATH),
            _load(sd.SUMMARY_PATH), sha256_file(AGENT_PATH))
