"""Pilot P2b review workbook for the grouping run 2 groups (P2b-ingest Phase C; D-052).

`artifacts/benchmark/review/P2b_groups_v1.xlsx` (gitignored) has the sheets OVERVIEW, GROUPS
(one row per group of >= 2 members), SINGLETONS (one row per one-member group), PACKETS (one row per
packet-group attachment, in packet order and rank) and Legend; the GROUPS sheet is also written as
the tracked `P2b_groups_v1.csv`. GROUPS and SINGLETONS carry the empty reviewer columns
`kaiyuan_disposition` (accept_group / split / merge_with / mislabelled_claim_about / reject) and `note`.
Cross-chunk merging is not done by code (D-051): a reviewer marks it with `merge_with`.

Read from tracked files only (the run-2 manifest, `groups_enriched.jsonl`, its summary, the packets),
so a test can rebuild the CSV. No model call, no table value.
"""

from __future__ import annotations

import json
from pathlib import Path

from climrr import litgroups_run2 as g2
from climrr import p2a_review as p2a
from climrr import synthpackets as spk
from climrr.paths import REPO_ROOT

REVIEW_DIR = REPO_ROOT / "artifacts" / "benchmark" / "review"
WORKBOOK_PATH = REVIEW_DIR / "P2b_groups_v1.xlsx"
GROUPS_CSV_PATH = REVIEW_DIR / "P2b_groups_v1.csv"
DISPOSITIONS = ("accept_group", "split", "merge_with", "mislabelled_claim_about", "reject")
REVIEW_COLS = ["kaiyuan_disposition", "note"]


def _members(g: dict) -> str:
    return " || ".join(f"{m['statement_id']} [{m['paper_item_id']}; {m['evidence_role']}; {m['region_class']}]: {m['statement']}"
                       for m in g["members"])


def _classes(g: dict) -> str:
    return "; ".join(f"{c}: {n}" for c, n in g["region_class_counts"].items())


GROUP_HEADER = ["group_id", "arm", "statement_type", "claim_about", "evidence_strength", "n_members", "n_papers",
                "n_independent_papers", "n_independent_core_cited_papers", "label", "rationale", "members", "region_classes",
                "partition", "chunk"] + REVIEW_COLS


def group_rows(enriched: list[dict]) -> list[list]:
    return [GROUP_HEADER] + [[g["group_id"], g["arm"], g["statement_type"], g["claim_about"], g["evidence_strength"], g["n_members"],
                              g["n_papers"], g["n_independent_papers"], g["n_independent_core_cited_papers"], g["label"],
                              g["rationale"], _members(g), _classes(g), g["partition"], g["chunk"], "", ""]
                             for g in enriched if not g["is_singleton"]]


SINGLETON_HEADER = ["group_id", "arm", "statement_type", "claim_about", "evidence_strength", "statement_id", "paper_item_id",
                    "evidence_role", "statement", "region", "region_class", "partition", "chunk"] + REVIEW_COLS


def singleton_rows(enriched: list[dict]) -> list[list]:
    rows = [SINGLETON_HEADER]
    for g in enriched:
        if g["is_singleton"]:
            m = g["members"][0]
            rows.append([g["group_id"], g["arm"], g["statement_type"], g["claim_about"], g["evidence_strength"], m["statement_id"],
                         m["paper_item_id"], m["evidence_role"], m["statement"], m["region"], m["region_class"], g["partition"],
                         g["chunk"], "", ""])
    return rows


PACKET_HEADER = ["packet_id", "item_id", "seed_id", "rung", "role", "rank", "group_id", "kind", "label", "claim_about",
                 "strength_in_packet", "group_strength_run", "relevance", "n_relevant_members", "n_papers_relevant"]


def packet_rows(packets: list[dict]) -> list[list]:
    rows = [PACKET_HEADER]
    for pk in packets:
        rank: dict = {}
        for g in pk["provenance"]["groups"]:
            rank[g["role"]] = rank.get(g["role"], 0) + 1
            rows.append([pk["packet_id"], pk["item_id"], pk["seed_id"], pk["use_case_level"], g["role"], rank[g["role"]], g["group_id"],
                         g["kind"], g["label"] or g["members"][0]["statement"], g["claim_about"], g["strength_in_packet"],
                         g["group_strength_run"], g["best_basis"], len(g["members"]), g["n_papers"]])
    return rows


def overview_rows(man: dict, summ: dict, packets_manifest: dict) -> list[list]:
    k = man["counts"]
    rows = [["item", "value"],
            ["run", f"litgroups run 2 ({man['generator']['version']}, {man['endpoint']['endpoint_label']} {man['endpoint']['model']}; {man['decision']})"],
            ["tarball sha256", man["tarball"]["sha256"]], ["source commit", man["source_commit"]],
            ["budget", ", ".join(f"{a}={b}" for a, b in man["budget"].items())],
            ["partitions / chunks / pass", f"{k['partitions']} / {k['chunks']} / {k['chunks_pass']}"],
            ["corrective turns (passed first time / second attempt)",
             f"{k['corrective_retry_used']} ({k['corrective_passed_first_attempt']} / {len(man['second_attempt_chunks'])})"],
            ["second-attempt chunks (same configuration)", "; ".join(
                f"{x['chunk_id']}: first attempt {', '.join(x['first_attempt']['failed'])} (missing {x['first_attempt']['missing_ids']}, "
                f"duplicate {x['first_attempt']['duplicate_ids']}, unknown {x['first_attempt']['unknown_ids']})"
                for x in man["second_attempt_chunks"])],
            ["groups / singletons / statements", f"{summ['groups']} / {summ['singletons']} / {summ['statements']}"],
            ["groups the agent returned with one member (labelled; non-gating single_member check)", summ["groups_with_one_member"]],
            ["cross-chunk merging", man["cross_chunk_merge"]]]
    for arm, by_claim in summ["groups_by_arm_claim_strength"].items():
        for claim, by_s in by_claim.items():
            rows.append([f"groups {arm} {claim}", "; ".join(f"{s}: {n}" for s, n in by_s.items())])
    rows += [[f"multi-source hazard_change_mechanism groups, {a}", n] for a, n in summ["multi_source_mechanism_groups_by_arm"].items()]
    rows.append(["labels with a digit no member has", len(summ["labels_with_digit_not_in_members"])])
    rows += [[f"packet {x['item_id']} ({x['seed_id']}, rung {x['level']})",
              f"driver {x['groups_driver']}, context {x['groups_context']}, caveat {x['groups_caveat']}; excluded {x['excluded_groups']}"]
             for x in packets_manifest["packets"]]
    return rows


LEGEND = [["field", "meaning"],
          ["claim_about", "the grouping agent's tag (D-049), never inferred by code: hazard_change_mechanism, hazard_definition_or_measurement, "
                          "impact_or_exposure, method_or_data, other"],
          ["evidence_strength", "multi_source_supported: >= 2 independent papers (DR-LIT-IND-1 v2, D-046) among core / cited members; "
                                "review_supported: a review_synthesis member; single_source_supported: one paper with core / cited members; "
                                "background_only: background passages only (D-045, D-048)"],
          ["n_papers / n_independent_papers", "distinct paper ids / distinct canonical papers (D-046) among all members, background included"],
          ["members", "statement id [paper id; evidence role; region class (geography v2)]: statement, verbatim; joined by ' || '"],
          ["region_classes", "litgeo v2 (D-047a) class of each member, with counts"],
          ["partition / chunk", "arm x statement_type partition; chunk of <= 40 statements (D-051). Groups never span chunks"],
          ["kaiyuan_disposition", "accept_group | split | merge_with (name the group id in note) | mislabelled_claim_about (name the "
                                  "right value in note) | reject"],
          ["PACKETS role / rank", "DR-SEED-RANK-2: driver = hazard_change_mechanism (<= 10), context = hazard_definition_or_measurement "
                                  "(<= 4), caveat at rung 7 only (<= 4); rank within role: relevance class, strength, papers, id"],
          ["PACKETS relevance", "best relevance basis among the group's relevant members: state > nca_region > us_subregion > us_national > global"],
          ["status", "nothing here is accepted: groups are agent proposals for human review"]]


def workbook_sheets(man: dict, summ: dict, enriched: list[dict], packets: list[dict], packets_manifest: dict) -> list[tuple]:
    return [("OVERVIEW", overview_rows(man, summ, packets_manifest), [52, 120]),
            ("GROUPS", group_rows(enriched), [34, 14, 12, 28, 22, 8, 8, 8, 8, 60, 50, 120, 30, 30, 32, 20, 40]),
            ("SINGLETONS", singleton_rows(enriched), [34, 14, 12, 28, 22, 18, 12, 24, 90, 24, 14, 30, 32, 20, 40]),
            ("PACKETS", packet_rows(packets), [20, 12, 16, 6, 8, 6, 34, 10, 70, 28, 22, 22, 12, 8, 8]),
            ("Legend", LEGEND, [32, 120])]


def inputs(packets_dir: Path = spk.PACKETS_DIR) -> tuple:
    load = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))  # noqa: E731
    man, summ = load(g2.MANIFEST_PATH), load(g2.ENRICHED_SUMMARY_PATH)
    enriched = [json.loads(ln) for ln in g2.ENRICHED_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
    pm = load(packets_dir / "manifest.json")
    packets = [load(packets_dir / f"{x['packet_id']}.json") for x in pm["packets"]]
    return man, summ, enriched, packets, pm


groups_csv = p2a.seeds_csv
