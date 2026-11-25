"""Work package P5c (2026-11-24; D-076): the infra grouping run ingest, the COORDINATOR review list, the rung-8 seeds,
selection and packets (provisional), and the sample-sheet builder for Alvi (not run).

The ingest is checked on the committed artifacts (the delivered tarball stays outside the repository: `verify_source` runs
on a tree rebuilt from the committed copies); the enrichment, the review list, the seeds, the selection and the packets are
rebuilt and compared byte for byte.
"""

from __future__ import annotations

import csv
import io
import json
import re
import shutil

import pytest
import yaml

from climrr import benchmark_items as bi
from climrr import itemseeds as sd
from climrr import litgeo as lg
from climrr import litgroups as lgr
from climrr import litgroups_infra as lgi
from climrr import litgroups_infra_run1 as gi
from climrr import litstatements_infra1 as ir
from climrr import mentor_sheet_alvi as ma
from climrr import mentor_sheet_v2b as ms
from climrr import seeds_infra as si
from climrr import synthpackets_infra as spi
from climrr.checksums import sha256_file

MAN = json.loads(gi.MANIFEST_PATH.read_text(encoding="utf-8"))
ENR = sd.read_jsonl(gi.ENRICHED_PATH)
SUMMARY = json.loads(gi.ENRICHED_SUMMARY_PATH.read_text(encoding="utf-8"))
REC = sd.read_jsonl(ir.INGESTED_PATH)
INDEP = json.loads(ir.INDEPENDENCE_PATH.read_text(encoding="utf-8"))
PARTS = lgr.read_groups(lgi.PARTITIONS_PATH)
SEEDS_SUMMARY = json.loads(si.SEEDS_SUMMARY_PATH.read_text(encoding="utf-8"))
SEL = yaml.safe_load(si.SELECTION_PATH.read_text(encoding="utf-8"))
PMAN = json.loads((spi.PACKETS_DIR / "manifest.json").read_text(encoding="utf-8"))
PACKETS = {p["item_id"]: json.loads((spi.PACKETS_DIR / f"{p['packet_id']}.json").read_text(encoding="utf-8")) for p in PMAN["packets"]}


def _src_from_artifacts(tmp_path):
    """The delivered tree, rebuilt from the committed copies (the prompts / responses are not needed by verify_source)."""
    run = tmp_path / "litgroups" / "infra_run1"
    run.mkdir(parents=True)
    for name in ("groups.jsonl", "summary.json", "agent.log"):
        shutil.copyfile(gi.ART / name, run / name)
    for p in gi.CHUNKS_DIR.glob("*.json"):
        (run / p.stem).mkdir()
        shutil.copyfile(p, run / p.stem / "result.json")
    return tmp_path


# --- A: ingest -----------------------------------------------------------------------------------------------------------


def test_manifest_is_the_run_facts():
    assert MAN["tarball"]["sha256"] == gi.TARBALL_SHA256 == "14797dc7f804f4dbba4d7f6fc6e904765bbd87948a9c131abd4f003a07319f65"
    assert MAN["groups_sha256"] == sha256_file(gi.ART / "groups.jsonl") == gi.GROUPS_SHA256
    assert MAN["summary_sha256"] == sha256_file(gi.ART / "summary.json") == gi.SUMMARY_SHA256
    assert MAN["counts"] == {"partitions": 11, "chunks": 12, "chunks_pass": 12, "chunks_fail": 0, "corrective_retry_used": 4,
                             "groups": 84, "singletons": 59, "statements": 198}
    assert MAN["by_strength"] == {"multi_source_supported": 20, "review_supported": 2, "single_source_supported": 121, "background_only": 0}
    assert MAN["groups_by_claim_about"]["hazard_impact_on_asset"] == 59 and MAN["groups_by_claim_about"]["impact_or_exposure"] == 13
    assert MAN["source_commit"].startswith("7699412") and MAN["generator"]["system_prompt_template_impact_sha256"].startswith("70018280")
    assert MAN["partitions"]["sha256"] == sha256_file(lgi.PARTITIONS_PATH)
    assert len(MAN["files"]) == 15 and len(MAN["excluded_files"]) == 32
    for f in MAN["files"] + MAN["derived_files"]:
        assert sha256_file(gi.ART / f["path"]) == f["sha256"], f["path"]
    assert not any((gi.ART / f["path"].split("/", 2)[-1]).exists() for f in MAN["excluded_files"])


def test_verify_source_on_the_committed_copies_and_fails_on_a_change(tmp_path):
    src = _src_from_artifacts(tmp_path)
    facts = gi.verify_source(src, PARTS)
    assert facts["corrective_chunks"] == MAN["corrective_chunks"] and len(facts["chunk_ids"]) == 12
    (src / "litgroups" / "infra_run1" / "summary.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="summary.json differs"):
        gi.verify_source(src, PARTS)


def test_enrichment_rebuilds_byte_identical_and_reports():
    enr = gi.enrich(lgr.read_groups(gi.ART / "groups.jsonl"), PARTS, REC, INDEP, lg.Gazetteer(sd.nca_map()))
    assert "".join(json.dumps(g, ensure_ascii=False, sort_keys=True) + "\n" for g in enr) == gi.ENRICHED_PATH.read_text(encoding="utf-8")
    s = gi.summarise(enr)
    s["hazard_impact_on_asset_labels"] = gi.hia_label_listing(enr)
    assert s == SUMMARY
    assert len(s["multi_source_groups"]) == 20 and s["hazard_impact_on_asset_groups"] == 59
    assert s["hazard_impact_on_asset_groups_with_place_named_member"] == 14
    assert s["groups_with_one_member"] == 59 and s["duplicate_paper_merges"] == 0


def test_enriched_records_carry_the_partition_and_member_fields():
    parts = {p["partition_id"]: p for p in PARTS}
    for g in ENR:
        assert g["family"] == parts[g["partition"]]["hazard_family"]
        if g["statement_type"] == "impact":
            assert g["asset_partition"] == parts[g["partition"]]["asset_partition"]
            assert g["impact_mechanisms"] == [m["impact_mechanism"] for m in g["members"]]
            assert sum(g["asset_class_counts"].values()) == g["n_members"]
        assert g["has_place_named_member"] == bool(g["place_named_states"])


# --- B: review list ------------------------------------------------------------------------------------------------------


def test_review_csv_rebuilds_and_holds_every_impact_record():
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(gi.REVIEW_COLUMNS), lineterminator="\n")
    w.writeheader()
    w.writerows(gi.review_rows(ENR))
    assert buf.getvalue() == gi.REVIEW_PATH.read_text(encoding="utf-8")
    rows = list(csv.DictReader(io.StringIO(buf.getvalue())))
    assert len(rows) == 103 and sum(r["kind"] == "group" for r in rows) == 72
    assert {r["claim_about"] for r in rows} == set(gi.REVIEW_CLAIMS)
    assert all(r["coordinator_disposition"] == "" and r["kaiyuan_disposition"] == "" for r in rows)
    want = {g["group_id"] for g in ENR if g["claim_about"] in gi.REVIEW_CLAIMS}
    assert {r["group_id"] for r in rows} == want


def test_label_screens():
    assert gi.label_flags("wildfire risk to power transmission lines") == ["(i) fire: wildfire"]
    assert gi.label_flags("healthcare workers performance reduced by heat stress") == ["(ii) people: workers"]
    assert gi.label_flags("downstream flooding damage to homes and infrastructure") == ["(iii) other hazard: flooding"]
    assert gi.label_flags("thermal power plant output reduction") == []
    listing = SUMMARY["hazard_impact_on_asset_labels"]
    assert sum(len(xs) for fam in listing.values() for xs in fam.values()) == 59


# --- C: seeds, selection, packets ----------------------------------------------------------------------------------------


def test_selection_cells_ids_and_fallbacks():
    assert SEL["review_state"] == "impact_groups_unreviewed" and SEL["version"] == "pilot_selection_infra v1"
    cells = {(x["family"], x["asset_class"]): x for x in SEL["selected"] + SEL["missing"]}
    assert [cells[c]["item_id"] for c in si.PILOT_CELLS] == [f"BI-P5-{k:04d}" for k in range(1, 9)]
    assert {c for c, x in cells.items() if x["place_named_impact_evidence"] == "none"} == {
        ("heat_index", "water_and_wastewater"), ("fire_weather_index", "emergency_services"), ("fire_weather_index", "communications")}
    assert all(x["state"] == "California" for x in cells.values() if x["place_named_impact_evidence"] == "none")
    assert [(m["family"], m["asset_class"]) for m in SEL["missing"]] == [("fire_weather_index", "emergency_services")]
    assert {x["item_id"]: x["state"] for x in SEL["selected"]} == {
        "BI-P5-0001": "Virginia", "BI-P5-0002": "Arizona", "BI-P5-0003": "California", "BI-P5-0004": "Arizona",
        "BI-P5-0005": "Arizona", "BI-P5-0006": "California", "BI-P5-0008": "California"}
    assert SEL["table_setting"] == si.TABLE_SETTING


def test_fire_emergency_services_has_no_impact_tagged_statement():
    """The missing cell: the passing fire emergency-services statements carry other claim tags (escalated, not filled)."""
    tags = [g["claim_about"] for g in ENR if g["family"] == "fire_weather_index"
            for m in g["members"] if m.get("asset_class") == "emergency_services"]
    assert len(tags) == 4 and si.IMPACT_CLAIM not in tags


def test_seeds_and_selection_rebuild_byte_identical():
    from climrr import itemseeds_v3 as s3

    seeds_v3 = sd.read_jsonl(s3.SEEDS_PATH)
    ctx = si.Context(REC, INDEP, lg.Gazetteer(sd.nca_map()))
    seeds = si.build_seeds(seeds_v3, sd.read_jsonl(gi.ART / "groups.jsonl"), ctx, si.rung3_driver_ids_factory())
    assert "".join(json.dumps(s, ensure_ascii=False, sort_keys=True) + "\n" for s in seeds) == si.SEEDS_PATH.read_text(encoding="utf-8")
    sel = si.select_pilot(seeds, seeds_v3, REC, ctx, si.load_question_forms_v2())
    assert yaml.safe_dump(sel, sort_keys=False, allow_unicode=True, width=120) == si.SELECTION_PATH.read_text(encoding="utf-8")
    assert SEEDS_SUMMARY["seeds_file"]["sha256"] == sha256_file(si.SEEDS_PATH)
    assert SEEDS_SUMMARY["selection_file"]["sha256"] == sha256_file(si.SELECTION_PATH)
    assert all(s["review_state"] == "impact_groups_unreviewed" for s in seeds)


def test_packets_rebuild_byte_identical():
    extra = {k: v for k, v in PMAN["inputs_sha256"].items()}
    packets = spi.build(SEL, sd.read_jsonl(si.SEEDS_PATH), ENR, REC, INDEP, extra)
    assert [p["item_id"] for p in packets] == [x["item_id"] for x in SEL["selected"]]
    for pk in packets:
        assert spi.dumps(pk) == (spi.PACKETS_DIR / f"{pk['packet_id']}.json").read_text(encoding="utf-8"), pk["packet_id"]
    for e in PMAN["packets"]:
        assert sha256_file(spi.PACKETS_DIR / f"{e['packet_id']}.json") == e["sha256"]


def test_packet_rung8_fields():
    seeds = {s["seed_id"]: s for s in sd.read_jsonl(si.SEEDS_PATH)}
    for iid, pk in PACKETS.items():
        mv, ci = pk["model_view"], pk["checks_input"]
        s8 = seeds[pk["seed_id"]]
        assert pk["use_case_level"] == mv["rung"] == ci["level"] == pk["provenance"]["item_frame"]["use_case_level"] == 8
        assert pk["review_state"] == mv["review_state"] == "impact_groups_unreviewed" and pk["provisional"]
        roles = [g["role"] for g in mv["groups"]]
        assert set(roles) <= {"driver", "impact"} and [g["group_id"] for g in mv["groups"] if g["role"] == "driver"] == s8["driver_group_ids"]
        impact = [g["group_id"] for g in mv["groups"] if g["role"] == "impact"]
        assert impact == ci["rung8"]["impact_group_ids"] == [x["group_id"] for x in s8["impact_groups"]][:spi.MAX_IMPACT_GROUPS]
        assert set(mv["place_named_impact_group_ids"]) <= set(impact)
        assert all(g["review_state"] == "impact_groups_unreviewed" for g in mv["groups"] if g["role"] == "impact")
        assert all(g["scope_phrase"].split(" ")[-1] in ("shows", "suggests") for g in mv["groups"])
        assert set(ci["scope"]["groups"]) == {g["group_id"] for g in mv["groups"]}
        assert mv["asset_class_phrase"] == ci["rung8"]["asset_class_phrase"] == spi.ASSET_CLASS_PHRASE[pk["asset_class"]]
        assert ci["rung8"]["broader_hazard_phrase"] == mv["plain_language"]["broader_hazard_phrase"]
        assert re.match(mv["question_form"]["opening_regex"], mv["question_form"]["skeleton"])
        assert mv["question_form"]["id"] == pk["selection"]["question_form_id"]
        assert {"will fail", "at risk", "fires", "burned area"} <= set(mv["must_not_use"])
        if pk["family"] == "fire_weather_index":                   # D-073b: the phrase is allowed, so not in must_not_use
            assert "wildfire" not in mv["must_not_use"] and "conditions that favour wildfire" in mv["wildfire_rule"]
        else:
            assert "wildfire" in mv["must_not_use"] and "wildfire_rule" not in mv
        reasons = {e["reason"] for e in pk["excluded_groups"]}
        assert not any(r.startswith("over_cap:impact") for r in reasons) or len(s8["impact_groups"]) > spi.MAX_IMPACT_GROUPS


def test_packets_pass_the_rung8_checks_on_a_well_formed_sentence():
    """The rung-8 rules of post-checks v3.3 accept the D-075 sentence shape on every packet (no model call)."""
    for pk in PACKETS.values():
        mv, ci = pk["model_view"], pk["checks_input"]
        gid = ci["rung8"]["impact_group_ids"][0]
        g = next(x for x in mv["groups"] if x["group_id"] == gid)
        hz = ci["rung8"]["broader_hazard_phrase"] if ci["rung8"]["group_hazard_relation"][gid] == "broader_hazard" else ci["rung8"]["quantity_phrases"][1]
        lit = [{"sentence": f"{g['scope_phrase']} that {hz} can affect {mv['asset_class_phrase']}.", "group_ids": [gid]}]
        reasons, _ = bi.rung8_reasons(lit, "", [("integrated", "")], ci)
        assert reasons == [], (pk["item_id"], reasons)
        bad = [("integrated", f"{mv['asset_class_phrase']} in {pk['state']} will fail.")]
        assert bi.rung8_reasons([], "", bad, ci)[0]


def test_schema_v2_rejects_an_impact_literature_statement_escalated():
    """P5c escalation, resolved by D-077 (P5c hotfix): item schema v2 (frozen) has no `impact` statement type and keeps refusing
    it; rung-8 items validate against item schema v2a instead (tests/test_p5c_hotfix.py)."""
    enum = bi.load_schema()["$defs"]["literature_statement"]["properties"]["statement_type"]["enum"]
    assert "impact" not in enum


# --- D: Alvi sheet -------------------------------------------------------------------------------------------------------


def test_alvi_sheet_superseded_by_p5d():
    """The P5c sheet design (seventh column, impact marks, --items required) was never run; P5d gave the sheet its inputs and
    final form (tests/test_p5d.py): seven columns with the asset class fourth, a five-line README, defaults packets v1b and
    the ingested infra run 2."""
    assert ma.HEADER[3] == "Asset class (CISA sector)" and len(ma.HEADER) == len(ma.WIDTHS) == 7
    assert len(ma.README_LINES) == 5 and ma.README_LINES[1] == ms.README_LINES[0]
    assert ma.PACKETS_DIR == spi.PACKETS_V1B_DIR
    pk = PACKETS["BI-P5-0001"]
    assert ma.asset_cell(pk) == 'Energy Sector (in the item: "energy systems")'
