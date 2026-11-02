"""Geography of literature statements: rules v1 (D-047, frozen) and v2 (D-047a amendment; pilot P2b-fix)."""

from __future__ import annotations

import csv
import json

import pytest

from climrr import itemseeds as sd
from climrr import itemseeds_v2 as s2
from climrr import litgeo as lg

GZ = lg.Gazetteer(sd.nca_map(), version="v1")
GZ2 = lg.Gazetteer(sd.nca_map())


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


# --- v2 (D-047a) ---------------------------------------------------------------------------------


@pytest.mark.parametrize("region,scope,expected,qualifier", [
    ("United States", "subnational", "us_national", None),            # a U.S. name is U.S.-wide regardless of scope
    ("United States", "national", "us_national", None),
    ("United States", "global", "us_national", None),
    ("U.S.", "local", "us_national", None),
    ("contiguous US", "subnational", "us_national", None),
    ("CONUS", "continental", "us_national", None),
    ("conterminous United States", "continental", "us_national", None),
    ("the lower 48", "unknown", "us_national", None),
    ("southeastern United States", "subnational", "us_subregion", "southeastern"),
    ("western US", "continental", "us_subregion", "western"),          # was us_national under v1
    ("the U.S. Southwest", "national", "us_subregion", "southwest"),
    ("Upper Midwestern United States", "subnational", "us_subregion", "upper midwestern"),
    ("dry ecoregions of the United States", "subnational", "us_subregion", "dry ecoregions"),
    ("northern and central US Rocky Mountains", "subnational", "us_subregion", "northern and central rocky mountains"),
    ("Southwest United States", "subnational", "nca:Southwest", None),  # a state / NCA5 name under subnational still wins
    ("north-central Minnesota, USA", "subnational", "state:Minnesota", None),
    ("Houston, TX, USA", "subnational", "us_national", None),          # a city is not a directional / regional qualifier
    ("Australia, Canada, United States", "continental", "us_national", None),
    ("Canada and the continental United States", "continental", "us_national", None),
    ("North America", "continental", "us_national", None),             # D-047 kept: not a U.S. name, scope-gated
    ("North America", "subnational", "other", None),
    ("Malaysia", "national", "other", None),
    ("unknown", "global", "global", None),
    ("unknown", "local", "unknown", None),
    ("Sierra Nevada", "subnational", "other", None),
])
def test_classification_v2(region, scope, expected, qualifier):
    g = lg.classify(region, scope, GZ2)
    assert (g["classification"], g["qualifier"]) == (expected, qualifier)


def test_us_subregion_is_relevant_to_every_us_pattern_below_state_and_nca():
    tx = {"state": ["Texas"], "nca_region": ["Southern Great Plains"]}
    assert lg.relevance(lg.classify("western United States", "subnational", GZ2), tx) == "us_subregion"
    assert lg.BASIS_ORDER == ("state", "nca_region", "us_subregion", "us_national", "global")
    assert lg.classify("western United States", "subnational", GZ2)["rule"] == "us_name:United States +qualifier"


def test_an_unknown_rule_version_is_refused():
    with pytest.raises(ValueError):
        lg.Gazetteer(sd.nca_map(), version="v3")


def test_the_region_string_csv_v2_and_the_recovered_drops():
    rows = list(csv.DictReader(open(lg_v2_csv(), encoding="utf-8")))
    assert sum(int(r["count"]) for r in rows) == 747 and len(rows) == 147
    for r in rows:
        g, g1 = lg.classify(r["region"], r["region_scope"], GZ2), lg.classify(r["region"], r["region_scope"], GZ)
        assert (g["classification"], g["qualifier"] or "", g1["classification"]) == (r["classification"], r["qualifier"], r["classification_v1"])
    s = json.loads(lg_v2_csv().with_name("region_strings_v2_summary.json").read_text(encoding="utf-8"))
    assert s["statements_by_class"] == {"us_national": 81, "us_subregion": 46, "state": 119, "nca": 5, "global": 118,
                                        "other": 178, "unknown": 200}
    assert s["d047_drops"]["dropped_under_v1"] == 50 and s["d047_drops"]["recovered_under_v2"] == 50
    assert s["d047_drops"]["recovered_by_class"] == {"us_national": 13, "us_subregion": 37}


def lg_v2_csv():
    return s2.REGION_CSV_PATH.with_name("region_strings_v2.csv")
