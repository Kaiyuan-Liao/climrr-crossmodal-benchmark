"""The frozen Track B orthographic normalization table v1 (D-027, ruling B4).

Only `>`, `<`, degree notation and `%` are transformed; the original term is
kept beside the normalized one; applying the table to the run-1 dropped terms
turns the threshold phrases into plain phrases and touches nothing else.
"""

from __future__ import annotations

import glob
import json
import re
from collections import Counter

import pytest

from climrr import termnorm
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

MANIFEST = REPO_ROOT / "data" / "manifest.json"
RUN1 = REPO_ROOT / "artifacts" / "literature" / "survey" / "run1"
TABLE_SHA256 = "80a5e0e386dfe8a984e1a5ba2ace781d15601f9b0723b75d238b6de5d1226e03"

#: The survey driver's plain-phrase rule (`TERM_OK` in survey_driver.py, unchanged).
TERM_OK = re.compile(r"^[a-z0-9][a-z0-9 \-/.]{0,59}$")
AUTHORIZED = {">", "<", "°", "%"}


@pytest.fixture(scope="module")
def table():
    return termnorm.load_table()


@pytest.fixture(scope="module")
def dropped_model_terms():
    """Run-1 model terms the sanitizer dropped as "not a plain lowercase phrase"."""
    out = []
    for p in sorted(glob.glob(str(RUN1 / "DC-*" / "candidates.json"))):
        c = json.loads(open(p, encoding="utf-8").read())
        out += [d["term"] for d in c["dropped"]
                if d["source"] == "model" and d["reason"].startswith("not a plain")]
    return out


def test_the_table_is_frozen_and_pinned_in_the_manifest():
    files = {f["path"]: f for f in json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]}
    rel = "data/metadata/litcollect/normalization_table_v1.yaml"
    assert sha256_file(termnorm.TABLE_PATH) == TABLE_SHA256 == files[rel]["sha256"]
    assert files[rel]["bytes"] == termnorm.TABLE_PATH.stat().st_size
    assert files[rel]["decision_ref"] == "D-027"


def test_exactly_the_seven_authorized_rules(table):
    assert table["status"] == "frozen" and table["decision_ref"] == "D-027"
    assert [r["id"] for r in table["rules"]] == [f"N-{i}" for i in range(1, 8)]
    assert [r["ruling_form"] for r in table["rules"]] == [
        "> → above", "< → below", "°F → degrees F", "° F → degrees F",
        "°C → degrees C", "° C → degrees C", "% → percent"]
    for r in table["rules"]:
        first = r["forms"][0]
        assert f"{first['match']} → {first['replace']}" == r["ruling_form"]
        # any further form is the same rule with the letter lowercased, nothing more
        for f in r["forms"][1:]:
            assert (f["match"], f["replace"]) == (first["match"].lower(), first["replace"].lower())
        for f in r["forms"]:
            assert set(f["match"]) - {" ", "F", "f", "C", "c"} <= AUTHORIZED


def test_the_work_package_example(table):
    n = termnorm.normalize("days with heat index above 95°f", table)
    assert n == {"original": "days with heat index above 95°f",
                 "normalized": "days with heat index above 95 degrees f", "rule_ids": ["N-3"]}


@pytest.mark.parametrize("term, normalized, rules", [
    ("hi >95°f days", "hi above 95 degrees f days", ["N-1", "N-3"]),
    ("summer days heat index >105f", "summer days heat index above 105f", ["N-1"]),
    ("x < 5", "x below 5", ["N-2"]),
    ("95° F days", "95 degrees F days", ["N-4"]),
    ("35°C", "35 degrees C", ["N-5"]),
    ("35° c", "35 degrees c", ["N-6"]),
    ("90% of days", "90 percent of days", ["N-7"]),
])
def test_each_rule(table, term, normalized, rules):
    assert termnorm.normalize(term, table) == {"original": term, "normalized": normalized, "rule_ids": rules}


@pytest.mark.parametrize("term", [
    "precipitation (mm)", "temperature (annual)", "degree days (hdd/cdd)",  # run-1 drops: parentheses kept
    "hi", "hdd", "max heat index", "heat index", "105 f",                  # no abbreviation expansion, no synonym
    "days ≥ 95", "10°", "heat-index days", "Summer Days",                  # unauthorized symbols, bare °, case
])
def test_nothing_else_is_transformed(table, term):
    assert termnorm.normalize(term, table) == {"original": term, "normalized": term, "rule_ids": []}


def test_run1_dropped_terms_become_plain_phrases_and_nothing_else_moves(table, dropped_model_terms):
    assert len(dropped_model_terms) == 29
    still_not_plain, plain = [], []
    for term in dropped_model_terms:
        n = termnorm.normalize(term, table)
        assert n["original"] == term                       # original retained
        assert not AUTHORIZED & set(n["normalized"])
        # the only new words are one per authorized symbol; no original word is lost or changed
        before = Counter(re.findall(r"[a-z0-9]+", term.replace("°", " ")))
        after = Counter(re.findall(r"[a-z0-9]+", n["normalized"]))
        assert after - before == Counter({"above": term.count(">"), "below": term.count("<"),
                                          "degrees": term.count("°"), "percent": term.count("%")}) - Counter()
        assert not before - after, term
        (plain if TERM_OK.match(n["normalized"]) else still_not_plain).append(n["normalized"])
    assert sorted(still_not_plain) == [
        "high heat index days (115 degrees f)", "precipitation (in)", "precipitation (mm)"]
    assert len(plain) == 26
    assert "days with heat index above 95 degrees f" in plain
    # Recorded, not acted on: the driver's unchanged "more than 6 words" rule would keep only 7 of the 26.
    assert sum(len(t.split()) <= 6 for t in plain) == 7


def test_run1_only_needs_n1_and_n3(table, dropped_model_terms):
    fired = {r for t in dropped_model_terms for r in termnorm.normalize(t, table)["rule_ids"]}
    assert fired == {"N-1", "N-3"}
