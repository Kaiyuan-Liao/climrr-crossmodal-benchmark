"""Geography of literature statements v2 (DR-SEED-1 v2 geography, D-047; pilot P2b-prep)."""

from __future__ import annotations

import csv
import json

import pytest

from climrr import itemseeds as sd
from climrr import itemseeds_v2 as s2
from climrr import litgeo as lg

GZ = lg.Gazetteer(sd.nca_map())


@pytest.mark.parametrize("region,scope,expected", [
    ("unknown", "global", "global"),                                   # a global scope alone is relevant
    ("savanna", "global", "global"),
    ("Malaysia", "national", "other"),                                 # a non-U.S. national scope is not (v1 made it relevant)
    ("Canada", "national", "other"),
    ("Europe", "continental", "other"),
    ("United States", "national", "us_national"),
    ("U.S.", "national", "us_national"),
    ("USA", "national", "us_national"),
    ("CONUS", "continental", "us_national"),
    ("conterminous United States", "continental", "us_national"),
    ("North America", "continental", "us_national"),
    ("United States", "subnational", "other"),                         # subnational needs a state / NCA5 region name
    ("contiguous US", "subnational", "other"),
    ("southeastern United States", "subnational", "other"),            # 'southeastern' is not the whole phrase 'Southeast'
    ("California", "subnational", "state:California"),
    ("Southern California", "subnational", "state:California"),
    ("California and Arizona", "subnational", "state:Arizona|state:California"),
    ("Southwest United States", "subnational", "nca:Southwest"),
    ("Upper Midwest and Northeast United States", "subnational", "nca:Midwest|nca:Northeast"),
    ("Alaska", "subnational", "state:Alaska|nca:Alaska"),
    ("Sierra Nevada", "subnational", "other"),                         # exclusions (ruling)
    ("Dinkey Creek watershed, Sierra Nevada", "subnational", "other"),
    ("Nevada County", "local", "other"),
    ("Washington, D.C.", "local", "other"),
    ("Washington DC", "local", "other"),
    ("Washington State", "subnational", "state:Washington"),
    ("Kansas City", "local", "other"),                                 # neither Kansas nor Missouri by the city alone
    ("Kansas City, Kansas", "local", "state:Kansas"),
    ("New York City", "subnational", "state:New York"),
    ("Brazil and Southeast Asia", "subnational", "other"),             # exclusion found in the data
    ("West Virginia", "subnational", "state:West Virginia"),           # not also Virginia
    ("Houston, TX, USA", "subnational", "other"),                      # no abbreviation matching
    ("unknown", "local", "unknown"),
    ("cities", "unknown", "unknown"),
])
def test_classification(region, scope, expected):
    assert lg.classify(region, scope, GZ)["classification"] == expected


def test_the_rule_and_masks_are_recorded():
    g = lg.classify("Sierra Nevada", "subnational", GZ)
    assert g["rule"] == "subnational_no_state_or_nca_name (masked by sierra nevada)" and g["masked_by"] == ["sierra nevada"]
    assert lg.classify("United States", "national", GZ)["rule"] == "us_gazetteer:United States"
    assert lg.classify("contiguous US", "subnational", GZ)["us_gazetteer_in_string"] == "US"
    assert lg.classify("Georgia", "subnational", GZ)["ambiguous"] == "the country Georgia"


def test_relevance_basis_most_specific_first():
    ca = {"state": ["California"], "nca_region": ["Southwest"]}
    tx = {"state": ["Texas"], "nca_region": ["Southern Great Plains"]}
    assert lg.relevance(lg.classify("California", "subnational", GZ), ca) == "state"
    assert lg.relevance(lg.classify("Southwest United States", "subnational", GZ), ca) == "nca_region"
    assert lg.relevance(lg.classify("United States", "national", GZ), tx) == "us_national"
    assert lg.relevance(lg.classify("unknown", "global", GZ), tx) == "global"
    assert lg.relevance(lg.classify("California", "subnational", GZ), tx) is None
    assert lg.relevance(lg.classify("Canada", "national", GZ), tx) is None


def test_the_exclusion_file_lists_the_ruling_phrases():
    ex = lg.load_exclusions()
    phrases = {e["phrase"] for e in ex["exclusions"]}
    assert {"Sierra Nevada", "Nevada County", "Washington, D.C.", "Washington DC", "Kansas City"} <= phrases
    assert ex["allowed"] == [{"phrase": "New York City", "names": "New York", "source": "ruling"}]


def test_the_frozen_region_string_csv():
    rows = list(csv.DictReader(open(s2.REGION_CSV_PATH, encoding="utf-8")))
    assert sum(int(r["count"]) for r in rows) == 747 and len({r["region"] for r in rows}) == 133
    for r in rows:   # the stored classification is what the rule gives today
        assert lg.classify(r["region"], r["region_scope"], GZ)["classification"] == r["classification"]
    s = json.loads(s2.SUMMARY_PATH.read_text(encoding="utf-8"))["region_string_classification"]
    assert s["statements_by_class"] == {"us_national": 77, "state": 119, "nca": 5, "global": 118, "other": 228, "unknown": 200}
