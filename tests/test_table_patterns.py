"""Pilot P1 table-pattern extractor (D-041): the rules on synthetic tables, then the
committed outputs.

The engine is tested on synthetic tables only. The full `table_patterns_v1.jsonl`
is gitignored (regenerable, pinned by hash in the summary): its test fails when
the file is absent unless CLIMRR_ALLOW_MISSING_RAW=1, as for the raw table.
"""

from __future__ import annotations

import copy
import csv
import json
import os
from decimal import Decimal

import pytest

from climrr import benchmark_items as bi
from climrr import table_patterns as tp
from climrr import templates as td

SLOTS = td.load_yaml(td.SLOTS_PATH)
COVERAGE = td.load_coverage()
NCA = tp.load_nca_map()
SUMMARY = json.loads(tp.SUMMARY_PATH.read_text(encoding="utf-8"))
EXAMPLES = tp.read_jsonl(tp.EXAMPLES_PATH)
DICT_LINES = td.DICTIONARY_TEXT_PATH.read_text(encoding="utf-8").splitlines()


# --- rules ----------------------------------------------------------------------------


def _d(values):
    return {k: Decimal(v) for k, v in values.items()}


def test_terciles_on_a_clean_population():
    vals = _d({f"S{i:02d}": str(i) for i in range(1, 16)})
    classes, skip = tp.terciles(vals, 0)
    assert skip is None
    assert [classes[f"S{i:02d}"] for i in (1, 5, 6, 10, 11, 15)] == ["small", "small", "moderate", "moderate", "large", "large"]


@pytest.mark.parametrize("values,missing,reason", [
    ({f"S{i}": str(i) for i in range(14)}, 0, "population_lt_15"),
    ({f"S{i}": str(i % 2) for i in range(20)}, 0, "degenerate_distribution"),
    ({**{f"S{i:02d}": str(i) for i in range(15)}, "S04": "5"}, 0, "tie_at_cut"),
    ({f"S{i:02d}": str(i) for i in range(15)}, 1, "missing_states_change_cut_points"),
])
def test_terciles_are_skipped_with_the_reason(values, missing, reason):
    classes, skip = tp.terciles(_d(values), missing)
    assert classes is None and skip.startswith(reason)


def test_competition_rank_shares_ties_and_orders_signed_values():
    r = tp.competition_rank(_d({"a": "-1", "b": "3", "c": "3", "d": "0"}))
    assert (r["b"]["rank"], r["c"]["rank"], r["d"]["rank"], r["a"]["rank"]) == (1, 1, 3, 4)
    assert r["b"]["tied_with"] == 1 and r["a"]["of"] == 4


def test_robustness_and_majority():
    assert tp.robustness(3, 3) == "all_states_same_direction"
    assert tp.robustness(2, 3) == "majority_same_direction"
    assert tp.robustness(1, 2) == "mixed"
    assert tp.majority_direction({"increase": 2, "decrease": 1, "no_change": 0}) == "increase"
    assert tp.majority_direction({"increase": 1, "decrease": 1, "no_change": 0}) == "mixed"


def test_tercile_definition_is_explicitly_relative():
    spec = {"family": "heat_index", "metric_id": "m", "season": "summer", "scenario": "RCP8.5"}
    text = tp.tercile_definition("large", 49, spec, "end", "absolute_change")
    assert "upper tercile" in text and "relative" in text and "not an absolute threshold" in text and "49" in text


def test_percent_columns_are_verified_and_quoted_from_the_dictionary():
    for season, by_h in tp.PERCENT_COLUMNS.items():
        for h, (index, column, line) in by_h.items():
            assert COVERAGE[index]["column"] == column and COVERAGE[index]["status"] == "verified_from_dictionary"
            assert f"_{season}_P{h}" in DICT_LINES[line - 1] and tp.PERCENT_QUOTE[h] in DICT_LINES[line - 1]


def test_specs_carry_column_status_and_order():
    specs = tp.metric_specs(SLOTS, COVERAGE)
    assert [s["family"] for s in specs][:4] == ["heat_index"] * 4
    fwi = next(s for s in specs if s["metric_id"] == "fwi_summer_seasonal_value")
    assert fwi["authorization"] == "inferred_candidate"
    assert all(s["authorization"] == "verified" for s in specs if s["family"] == "heat_index")
    pct = [s for s in specs if s["kind"] == "percent_column"]
    assert len(pct) == 4 and all(s["scenario"] == tp.UNSTATED and s["authorization"] == "verified" for s in pct)


# --- engine on a synthetic table -------------------------------------------------------


def _write_table(tmp_path, rows):
    header = [COVERAGE[i]["column"] for i in range(len(COVERAGE))]
    path = tmp_path / "synthetic.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        w = csv.writer(handle)
        w.writerow(header)
        for values in rows:
            row = [""] * len(header)
            for i, v in values.items():
                row[i] = v
            w.writerow(row)
    return path


def _row(cell, state, hist, mid, end, pct=("10", "-5")):
    v = {1: cell, 3: state}
    for i in (240, 241, 242, 243):
        v[i] = hist
    for i in (246, 247, 248, 249):
        v[i] = mid
    for i in (252, 253, 254, 255):
        v[i] = end
    for i, x in zip((189, 190, 191, 192, 193), ("10", "12", "15", "2", "5")):
        v[i] = x
    for season in tp.PERCENT_COLUMNS.values():
        v[season["mid"][0]], v[season["end"][0]] = pct
    return v


@pytest.fixture
def synthetic(tmp_path):
    slots = copy.deepcopy(SLOTS)
    proto = slots["location"]["state"]["values"][0]
    slots["location"]["state"]["values"] = [dict(proto, label=s, n_cells=2) for s in ("Alpha", "Beta", "Gamma")]
    slots["location"]["cell"]["values"][0].update(label="R1C1")
    rows = [_row("R1C1", "Alpha", "2", "3", "5"), _row("R1C2", "Alpha", "4", "4", "9", pct=("-1", "-2")),
            _row("R2C1", "Beta", "0", "1", "1"), _row("R2C2", "Beta", "", "", ""),
            _row("R3C1", "Gamma", "1", "0", "0")]
    nca = {"region_scheme_id": "NCA5", "regions": [{"region_id": "NCA5-X", "name": "X"}, {"region_id": "NCA5-Y", "name": "Y"}],
           "state_to_region_map": {"Alpha": "NCA5-X", "Beta": "NCA5-X", "Gamma": "NCA5-Y", "Delta": "NCA5-Y"}}
    states = ["Alpha", "Beta", "Gamma"]
    specs = tp.metric_specs(slots, COVERAGE)
    scanned = tp.scan(_write_table(tmp_path, rows), specs, states, "R1C1")
    records, skips = tp.build_patterns(slots, COVERAGE, nca, scanned, "0" * 64, "1" * 64, code_ver="test")
    return {r["pattern_id"]: r for r in records}, records, skips, scanned


def _find(records, **kw):
    return [r for r in records if all(r.get(k) == v for k, v in kw.items())]


def test_state_and_region_values(synthetic):
    _, records, _, _ = synthetic
    m = "heatindex_days_above_105F"
    alpha = _find(records, metric=m, horizon="end", statistic="absolute_change", geography="Alpha")[0]
    assert alpha["computed_value_or_range"]["value"] == "4.000000000000000"            # mean of (3, 5)
    assert alpha["computed_value_or_range"]["range"] == {"over": "cells", "min": "3.000000000000000", "max": "5.000000000000000"}
    assert alpha["pattern_support_n"] == 2 and alpha["pattern_robustness"] == "all_states_same_direction"
    assert alpha["robustness_unit"] == "cell" and alpha["provenance"]["row_rule"] == "State == 'Alpha'"
    beta = _find(records, metric=m, horizon="end", statistic="absolute_change", geography="Beta")[0]
    assert beta["computed_value_or_range"]["n_cells_empty"] == 1 and beta["pattern_support_n"] == 1
    region = _find(records, metric=m, horizon="end", statistic="absolute_change", geography="NCA5-X")[0]
    assert region["computed_value_or_range"]["value"] == "3.000000000000000"            # cell mean of (3, 5, 1)
    assert region["computed_value_or_range"]["range"]["min"] == "1.000000000000000"     # min over member states
    assert region["region_member_states_covered"] == ["Alpha", "Beta"]
    assert region["provenance"]["derivation_rule_id"] == "DR-TD-003 @ DR-PT-002"
    assert region["relative_magnitude"] is None and region["relative_magnitude_skipped_reason"].startswith("population_lt_15")
    pct = _find(records, metric=m, horizon="end", statistic="percent_change", geography="Beta")[0]
    assert pct["status"] == "not_computable" and pct["computed_value_or_range"]["value_reason"] == "zero_baseline"


def test_region_robustness_counts_member_states(synthetic):
    _, records, _, _ = synthetic
    y = _find(records, metric="heatindex_days_above_95F", horizon="end", statistic="direction", geography="NCA5-Y")[0]
    assert y["direction"] == "decrease" and y["pattern_support_n"] == 1                  # Delta is not in the table
    assert y["region_member_states_uncovered"] == ["Delta"]


def test_small_population_has_no_tercile_but_records_why(synthetic):
    _, _, skips, _ = synthetic
    assert skips and all(s["reason"].startswith("population_lt_15") for s in skips)


def test_fwi_summer_patterns_are_acceptance_blocked(synthetic):
    _, records, _, _ = synthetic
    fwi = _find(records, metric="fwi_summer_seasonal_value")
    assert fwi and all(r["acceptance_blocked"] and "IC-006" in r["acceptance_blocked_by"] for r in fwi)
    assert all(r["authorization"] == "inferred_candidate" for r in fwi)
    cell = _find(fwi, geography_type="cell_control", horizon="end", statistic="absolute_change")[0]
    assert cell["computed_value_or_range"]["value"] == "5.000000000000000"              # the Dend column


def test_percent_columns_have_no_central_value(synthetic):
    _, records, _, _ = synthetic
    pct = [r for r in records if r["metric"].endswith("_percent_change_column") and r["pattern_kind"] == "single"]
    assert pct and all(r["computed_value_or_range"]["value"] is None for r in pct)
    assert all(r["rank"] is None and r["relative_magnitude"] is None for r in pct)
    assert all(r["scenario"] == tp.UNSTATED and not r["acceptance_blocked"] for r in pct)
    alpha = _find(pct, geography="Alpha", horizon="mid", statistic="direction")[0]
    assert alpha["computed_value_or_range"]["cell_direction_counts"] == {"increase": 1, "decrease": 1, "no_change": 0}
    assert alpha["direction"] == "mixed"
    seasonal = _find(records, pattern_kind="seasonal_contrast", geography="Alpha", horizon="mid")[0]
    assert seasonal["largest_change_season"] is None and "not averaged" in seasonal["largest_change_season_skipped_reason"]


def test_regional_contrast_orders_regions(synthetic):
    _, records, _, _ = synthetic
    rc = _find(records, pattern_kind="regional_contrast", metric="heatindex_days_above_105F", horizon="end",
               statistic="absolute_change")[0]
    order = rc["computed_value_or_range"]["regions_ordered"]
    assert [o["region"] for o in order] == ["NCA5-X", "NCA5-Y"] and order[0]["rank"] == 1


def test_every_synthetic_record_validates_against_the_item_schema(synthetic):
    _, records, _, _ = synthetic
    schema = bi.load_schema()
    assert all(bi.table_pattern_errors(r, schema) == [] for r in records)


def test_scan_rejects_a_wrong_header(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("a,b,c,d\n", encoding="utf-8")
    with pytest.raises(tp.PatternError):
        tp.scan(path, tp.metric_specs(SLOTS, COVERAGE), ["Alpha"], "R1C1")


# --- committed outputs -------------------------------------------------------------------


def test_summary_counts_are_consistent():
    s = SUMMARY
    assert sum(s["by_kind"].values()) == s["n_patterns"] == s["patterns_file"]["n_records"]
    for key in ("by_family", "by_geography_type", "by_statistic", "by_status", "by_family_geography_statistic"):
        assert sum(s[key].values()) == s["n_patterns"]
    assert s["nca_states_not_in_table"] == ["District of Columbia", "Hawaii"]
    assert s["table_states_not_in_nca_map"] == []
    assert s["nca_map_sha256"] == td.file_sha256(tp.NCA_MAP_PATH)


def test_examples_are_the_first_ten_ids():
    assert [r["pattern_id"] for r in EXAMPLES] == [f"TP1-{i:05d}" for i in range(1, 11)]


def test_generated_doc_is_current():
    hashes = tp.doc_hashes(SUMMARY["table_data_sha256"], SUMMARY["patterns_file"]["sha256"])
    assert tp.DOC_PATH.read_text(encoding="utf-8") == tp.render_doc(SUMMARY, EXAMPLES, hashes, NCA)


def _full_records():
    if not tp.PATTERNS_PATH.is_file():
        if os.environ.get("CLIMRR_ALLOW_MISSING_RAW") == "1":
            pytest.skip("table_patterns_v1.jsonl absent and CLIMRR_ALLOW_MISSING_RAW=1 is set")
        pytest.fail("artifacts/benchmark/table_patterns_v1.jsonl is absent (gitignored); regenerate with "
                    "scripts/extract_table_patterns.py, or set CLIMRR_ALLOW_MISSING_RAW=1 for code-only work")
    assert td.file_sha256(tp.PATTERNS_PATH) == SUMMARY["patterns_file"]["sha256"]
    return tp.read_jsonl(tp.PATTERNS_PATH)


def test_full_patterns_file_matches_pin_and_validates():
    records = _full_records()
    assert len(records) == SUMMARY["n_patterns"] and records[:10] == EXAMPLES
    schema = bi.load_schema()
    assert all(bi.table_pattern_errors(r, schema) == [] for r in records)
    assert all(r["acceptance_blocked"] for r in records if r["metric"] == "fwi_summer_seasonal_value")
    assert all(r["relative_magnitude"] is None for r in records if r["geography_type"] != "state")


def test_full_patterns_reproduce_p_state_1_and_track_d():
    records = _full_records()
    frozen = json.loads((td.PROTOTYPES_DIR / "P-STATE-1.v2.json").read_text(encoding="utf-8"))
    ca = _find(records, metric="heatindex_days_above_105F", geography="California", horizon="end",
               statistic="absolute_change")[0]
    assert ca["computed_value_or_range"]["value"] == frozen["D"]["change_value"]
    # every computed state-level Track D single-statistic answer from the historical baseline is reproduced
    if not td.QUESTIONS_PATH.is_file():
        if os.environ.get("CLIMRR_ALLOW_MISSING_RAW") == "1":
            pytest.skip("questions_v1.jsonl absent and CLIMRR_ALLOW_MISSING_RAW=1 is set")
        pytest.fail("artifacts/templates/questions_v1.jsonl is absent; regenerate with scripts/generate_template_questions.py")
    horizon = {"mid_century": "mid", "end_century": "end"}
    stat = {"TD-T01": "direction", "TD-T02": "absolute_change", "TD-T03": "percent_change"}
    index = {(r["metric"], r["geography"], r["horizon"], r["statistic"]): r for r in records
             if r["pattern_kind"] == "single" and r["geography_type"] == "state"}
    checked = 0
    for q in td.read_jsonl(td.QUESTIONS_PATH):
        sl = q["slots"]
        if q["template_id"] not in stat or q["answer_status"] != td.COMPUTED or not sl["LOCATION"]["value_id"].startswith("state:"):
            continue
        if sl["PERIOD_FROM"]["value_id"] != "historical":
            continue
        r = index[(sl["CONCEPT"]["value_id"].split(":")[1], sl["LOCATION"]["value_id"][6:],
                   horizon[sl["PERIOD_TO"]["value_id"]], stat[q["template_id"]])]
        got = r["direction"] if stat[q["template_id"]] == "direction" else r["computed_value_or_range"]["value"]
        assert got == q["answer"], q["question_id"]
        checked += 1
    # 4 thresholds x 2 horizons x 3 statistics x 49 states, less the zero-baseline percent changes
    assert checked == 4 * 2 * 3 * 49 - _n_zero_baseline(records)


def _n_zero_baseline(records):
    return sum(1 for r in records if r["geography_type"] == "state" and r["family"] == "heat_index"
               and r["pattern_kind"] == "single" and r["status"] == "not_computable")
