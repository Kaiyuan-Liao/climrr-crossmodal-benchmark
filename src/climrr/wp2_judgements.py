"""M4-WP2 Phase 3: the adjudicator's recorded judgements on the 13 aligned pairs.

**The adjudicator is reader 1** --- the prototype-exposed EXECUTOR. Judgements
are read only from the two recorded claims and the spans they cite; no paper
was re-read. Format and rules as `climrr.wp1b_judgements` (D-019: span-limited
trimming approved; overrides only with explicit justification --- **none is
used here**).
"""

from __future__ import annotations

_SAME = {"content": "same"}

PAIR_JUDGEMENTS: dict[str, dict] = {
    # --- LIT-000166 (SPITFIRE) ---------------------------------------------------
    "LIT-000166-C1": {
        "concept": {**_SAME, "note": "CO2 release from biomass burning; wording only."},
        "relation_or_direction": {**_SAME, "note": "Average release of 2.24 Pg C per year (model estimate)."},
        "experimental_condition": {"content": "differs",
                                   "note": "Reader 1 unknown (the cropland exclusion is in its notes, not a dimension); reader 2 inferred the post-simulation cropland exclusion. Rule 3a: unknown. No override: reader 1 did not record the fact in any dimension, so J-1's circumstance does not arise."},
    },
    "LIT-000166-C2": {
        "concept": {**_SAME, "note": "'length' vs 'mean length' of the fire season."},
        "relation_or_direction": {"content": "differs",
                                  "adopted": {"value": "increases from wet/cold to warm/dry biomes", "tag": "explicit", "support_from": "r1_evidence"},
                                  "note": "Reader 1 adds the month ranges (one to three, four to seven); reader 2's longer span adds the model's over-estimation. Adopted: the part both state."},
        "geography": {"content": "differs", "note": "Reader 1 inferred 'biomes worldwide'; reader 2 unknown. Rule 3a."},
        "temporal_frame": {**_SAME, "note": "November 2000 to October 2002, both inferred from the same methods sentence."},
    },
    "LIT-000166-C5": {
        "relation_or_direction": {**_SAME, "note": "Less pronounced than observed; misses the extreme years."},
        "temporal_frame": {**_SAME, "note": "1996-2002, both inferred from the same sentence."},
    },
    # --- LIT-000519 (DFHI, Sardinia) ---------------------------------------------
    "LIT-000519-C1": {
        "concept": {**_SAME, "note": "Hazard class of burnt pixels; reader 2 names the DFHI."},
        "relation_or_direction": {"content": "differs",
                                  "adopted": {"value": "roughly one third classified High or Very High Hazard on the day they burnt; a quarter Very High", "tag": "explicit", "support_from": "r1_evidence"},
                                  "note": "Reader 2 adds the comparison with about 14% of all pixels, which its evidence span does not state."},
        "geography": {**_SAME, "note": "Sardinia, both inferred from the same results sentence."},
        "temporal_frame": {"content": "differs",
                           "adopted": {"value": "2017", "tag": "explicit", "support_from": "r1_evidence"},
                           "note": "Both explicit; reader 2 adds the 1 June-31 August season from another sentence. Adopted: the year the evidence states."},
        "experimental_condition": {"content": "differs",
                                   "note": "Reader 1 unknown (old-version caveat in its notes); reader 2 inferred the old algorithm and the 10 ha threshold. Rule 3a: unknown; no override."},
    },
    "LIT-000519-C2": {
        "concept": {**_SAME, "note": "'High' / 'Very High Hazard' pixels of the new algorithm."},
        "relation_or_direction": {"content": "differs",
                                  "adopted": {"value": "tended to return more", "tag": "explicit", "support_from": "r1_evidence"},
                                  "note": "Reader 2's longer span adds the authors' evapotranspiration explanation. Adopted: the part both state."},
        "geography": {**_SAME, "note": "Sardinia, both inferred from the same sentence."},
        "temporal_frame": {"content": "differs",
                           "adopted": {"value": "2017 fire season", "tag": "inferred", "support_from": "r2"},
                           "note": "Both inferred; reader 1 adds 1 June-31 August, which its longer support span states but reader 2's does not. Adopted: the part both support."},
        "experimental_condition": {"content": "differs", "note": "Reader 1 unknown; reader 2 inferred the version comparison. Rule 3a; no override."},
    },
    "LIT-000519-C3": {
        "concept": {**_SAME, "note": "Burned land and number of wildfires."},
        "temporal_frame": {**_SAME, "note": "2014-2018, both noting the paper's 'four-year' wording."},
    },
    "LIT-000519-C4": {
        "concept": {**_SAME, "note": "Mistral winds in concept (reader 1) or relation (reader 2)."},
        "geography": {**_SAME, "note": "'Sardinia' / 'the region of Sardinia'."},
    },
    # --- LIT-001501 (Southern Great Plains) -----------------------------------------
    "LIT-001501-C1": {
        "concept": {**_SAME, "note": "Wording only."},
        "relation_or_direction": {**_SAME, "note": "Significant 0.53; reader 2 adds '(positive)', which the value already implies."},
        "geography": {"content": "differs",
                      "adopted": {"value": "study domain across the SGP", "tag": "inferred", "support_from": "r1"},
                      "note": "Both inferred. Reader 2 adds latitude/longitude bounds from a passage split across values that its support span does not state; reader 1 adds the expansion 'Southern Great Plains'. Adopted: what reader 1's support span states."},
        "temporal_frame": {"content": "differs", "note": "Reader 1 inferred 1984-2020 (the MTBS record); reader 2 unknown. Rule 3a."},
    },
    "LIT-001501-C2": {
        "relation_or_direction": {**_SAME, "note": "137% then drought at 21% of normal."},
        "geography": {**_SAME, "note": "Oklahoma and Texas panhandles, both inferred from the same abstract sentence."},
        "temporal_frame": {**_SAME, "note": "2017 growing season, then the cool winter season."},
    },
    "LIT-001501-C3": {
        "relation_or_direction": {"content": "differs",
                                  "adopted": {"value": "23 wildfires, 556 347 acres vs an average of 5.66 wildfires, ~120 500 acres", "tag": "explicit", "support_from": "r1_evidence"},
                                  "note": "Reader 1 records the counts; reader 2 the ratios from the next sentence, which only its longer span contains. Adopted: the counts, stated in both spans."},
        "geography": {**_SAME, "note": "The SGP study domain, both inferred (different support sentences, same place)."},
    },
    "LIT-001501-C5": {
        "concept": {**_SAME, "note": "Whiplash events and mega-fire conditions."},
        "relation_or_direction": {**_SAME, "note": "'enhances the risk ... at a much higher frequency'."},
        "geography": {**_SAME, "note": "'across the SGP' / 'the SGP (Southern Great Plains)'."},
        "temporal_frame": {**_SAME, "note": "'in the future', no horizon."},
    },
    # --- LIT-001536 (US prisons) -------------------------------------------------
    "LIT-001536-C2": {
        "concept": {**_SAME, "note": "Days with daily mean over 85°F (at prisons)."},
        "relation_or_direction": {**_SAME, "note": "67.3% of facilities."},
        "geography": {"content": "differs",
                      "adopted": {"value": "44 states and the District of Columbia", "tag": "explicit", "support_from": "r1_evidence"},
                      "note": "Reader 2 adds '(United States)', which the evidence span does not state. Adopted: the span's own words."},
        "temporal_frame": {"content": "differs",
                           "adopted": {"value": "2020 to 2023", "tag": "explicit", "support_from": "r1_evidence"},
                           "note": "Reader 2 adds 'summer months, 1 June-31 August' from the methods, not stated in the evidence."},
    },
    "LIT-001536-C5": {
        "concept": {**_SAME, "note": "Heat exposure by facility-level characteristics."},
        "relation_or_direction": {**_SAME, "note": "Significantly higher (p < 0.05); reader 2 keeps the authors' hedge, reader 1 the count (9 of 17); same proposition."},
        "geography": {**_SAME, "note": "US prisons, both inferred."},
        "temporal_frame": {**_SAME, "note": "2019 / summer 2019."},
    },
}
