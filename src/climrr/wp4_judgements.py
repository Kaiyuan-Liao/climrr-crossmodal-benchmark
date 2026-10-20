"""M4-WP4r3 Phase A: the adjudicator's recorded judgements on the 50 aligned pairs.

**The adjudicator is reader 1** --- the prototype-exposed EXECUTOR. Judgements
are read only from the two recorded claims and the spans they cite; no paper
was re-read. Format and rules as `climrr.wp2_judgements` (D-019: span-limited
trimming approved; overrides only with explicit justification --- **none is
used here**). Helpers:

* `S(note)` --- the two values say the same thing (no adoption);
* `U(note)` --- differs and one side is `unknown` (rule 3a adopts `unknown`);
* `B(states, value, src, note, content)` --- explicit vs inferred (rule 3b):
  does the explicit reader's span state `value`? `src` names the span the
  adopted value rests on (`r1`/`r2` support, `r1_evidence`/`r2_evidence`);
  `content` is `same` when the two values say the same thing and only the tag
  differs, `differs` otherwise;
* `C(value, tag, note)` --- same tag, content differs (rule 3c): the
  span-limited value both readers support;
* `T(adopted, note)` --- claim_type differs: adopted by judgement, or
  `unresolved_tie`.

Also here: `ROLE_CLASS_OF_R1`, the class of every free-text geography role
reader 1 recorded (the blind reader used the rubric's categories, mapped in
`climrr.wp4adj.ROLE_CLASS_OF`). A role string not listed fails the run.
"""

from __future__ import annotations


def S(note: str) -> dict:
    return {"content": "same", "note": note}


def U(note: str) -> dict:
    return {"content": "differs", "note": note}


def B(states: bool, value: str, src: str, note: str, content: str = "same") -> dict:
    return {"content": content, "explicit_span_states": states,
            "adopted": {"value": value, "tag": "explicit" if states else "inferred", "support_from": src}, "note": note}


def C(value: str, tag: str, note: str) -> dict:
    return {"content": "differs", "adopted": {"value": value, "tag": tag}, "note": note}


def T(adopted: str, note: str) -> dict:
    return {"content": "differs", "adopted": adopted, "note": note}


_R1_SUP = "reader 1's support span states it; reader 2 cites the same sentence and tags it inferred. Rule 3b: explicit kept."

ROLE_CLASS_OF_R1 = {
    # the paper's own study / phenomenon geography
    "study area": "study_area",
    "study area (as summarised in the conclusion)": "study_area",
    "study area (city sample)": "study_area",
    "study area (facility sample)": "study_area",
    "study area (model domain)": "study_area",
    "study area (modelled grid squares)": "study_area",
    "study area (national comparison)": "study_area",
    "study area (projection)": "study_area",
    "study area (provincial averages)": "study_area",
    "study area (where the houses and fires were observed)": "study_area",
    "analysis region": "study_area",
    "analysis regions": "study_area",
    "analysis domain (global hot land areas)": "study_area",
    "analysis region (hot land region)": "study_area",
    "regions of strongest simulated effect": "study_area",
    "facilities ranked within the study area": "study_area",
    "case-study site (this paper's own counterfactual calculation)": "study_area",
    "comparison / validation area for the database": "study_area",
    "example region of the global database's regional summary": "study_area",
    "regions named as results of the global regional summary": "study_area",
    "evaluation case (retrospective wildfire incident)": "study_area",
    "evaluation case region (fire event)": "study_area",
    "evaluation site (fire source region)": "study_area",
    "evaluation network (global)": "study_area",
    "regions of evaluated fire events": "study_area",
    "validation case region (2003 heatwave)": "study_area",
    "validation case region (2010 heatwave)": "study_area",
    "validation case region (July 1995 heatwave)": "study_area",
    "validation case (index comparison)": "study_area",
    # a cited study's area (the geography of a restated finding, not this paper's)
    "study area of the cited study": "cited_study_area",
    "case-study area (from a cited study)": "cited_study_area",
    "case-study area (fire event)": "cited_study_area",
    "regions of the reviewed studies": "cited_study_area",
    "validation case region (from cited studies)": "cited_study_area",
    # background / context
    "background context": "contextual",
    "background context (national)": "contextual",
    "background context (where the systems are used)": "contextual",
    "regulatory context (states with heat standards)": "contextual",
    # the area of a data set or station used to demonstrate a method
    "area of the forest fire data set used for testing": "data_source",
    "example data site (motivating application)": "data_source",
    # the addressee of a recommendation
    "target of the recommendation": "other",
    "target population of the recommendations": "other",
}

PAIR_JUDGEMENTS: dict[str, dict] = {
    # --- LIT2-000084 (irrigation loss and heat waves, US) ---------------------------
    "LIT2-000084-C1": {
        "concept": C("heat wave frequency, duration, and intensity", "explicit",
                     "Reader 1 adds the driver 'loss of irrigation', which reader 2 keeps in the relation. Adopted: the part both state."),
        "relation_or_direction": S("Same increases (0.70 events/year, 0.62 days/event, 0.24 °C); elision only."),
        "geography": C("the US", "explicit", "Reader 1 adds 'contiguous US model domain' from its support span; the evidence says 'in the US'."),
        "temporal_frame": B(True, "8-year (2004-2011)", "r1", _R1_SUP + " 'simulated period' trimmed."),
        "experimental_condition": B(True, "simulation without irrigation (CROP) versus with irrigation (CROPIRR)", "r1",
                                    "Reader 1's support states the two runs; its 'WRF3.3-CLM4crop' and 'hypothetical irrigation loss scenario' are not in that span. Trimmed."),
    },
    "LIT2-000084-C2": {
        "relation_or_direction": S("Significantly increased; up to 3 events/year and 2 days/event in the Southern High Plains."),
        "temporal_frame": B(True, "8-year (2004-2011)", "r1", _R1_SUP),
        "experimental_condition": C("without irrigation", "explicit",
                                    "Reader 2 records the evidence's 'without irrigation'; reader 1 the full run description from a methods span. Adopted: the part both state."),
    },
    "LIT2-000084-C3": {
        "relation_or_direction": S("Less sensitive because of the temperature-humidity trade-off; wording only."),
        "geography": S("'the United States' / 'In the United States', both inferred from the same sentence."),
        "temporal_frame": U("Reader 1 explicit 8-year period; reader 2 unknown. Rule 3a."),
        "experimental_condition": C("loss of irrigation", "explicit", "Reader 2 keeps the evidence's words; reader 1 adds the run description. Adopted: the part both state."),
    },
    # --- LIT2-000185 (GlobFire burnt-area database) ---------------------------------
    "LIT2-000185-C1": {
        "concept": C("biggest fires reported by CALFIRE", "explicit",
                     "Reader 1 adds per-fire burnt area (which reader 2 keeps in the relation). Adopted: the fires both name."),
        "relation_or_direction": S("All found in GlobFire; burnt area per fire considerably different; reader 1 also notes the additional big fires in the same sentence."),
        "geography": B(True, "California", "r1", _R1_SUP),
        "temporal_frame": S("'2001 to 2017' / 'from 2001 to 2017'."),
    },
    "LIT2-000185-C3": {
        "relation_or_direction": S("More fires in the north; larger average size in the centre."),
        "geography": S("Portugal, its north and its central area; wording only."),
        "temporal_frame": S("2001 to 2017, both inferred from the same regional-summary sentence."),
    },
    "LIT2-000185-C4": {
        "concept": S("'maximum fire spread speed' / 'fastest moving fires': the same measure."),
        "relation_or_direction": S("The fastest moving fires occur in the named regions."),
        "geography": C("south of Spain; the Peloponnese (Greece); central Portugal", "explicit",
                       "Reader 1 adds global places (Santa Isabel, Malheur, ...) that the evidence span does not name. Adopted: the evidence's places."),
        "temporal_frame": S("2001 to 2017, both inferred from the same sentence."),
    },
    # --- LIT2-000203 (heat and pregnancy, The Gambia) -------------------------------
    "LIT2-000203-C1": {
        "concept": S("Prematurity and ambient temperature exposure; reader 2 keeps the exposure in the relation."),
        "relation_or_direction": S("8.6% increase per 5.6 °C; wording only."),
        "geography": C("California", "explicit", "Reader 1 adds '(temperate regions)', the sentence's framing, not the study's place. Adopted: 'California'."),
    },
    "LIT2-000203-C2": {
        "relation_or_direction": S("Likely to exceed the last 200,000 years; around 4 °C above pre-industrial."),
        "claim_type": T("unresolved_tie",
                        "Reader 1 background_citation, reader 2 projection. The shared span (an abstract sentence with no citation marker) "
                        "does not settle whether the projection is the paper's or cited; breaking it would need re-reading the paper. Recorded as a tie."),
    },
    # --- LIT2-000315 (irrigation and wet-bulb temperature) ---------------------------
    "LIT2-000315-C1": {
        "concept": C("median wet-bulb temperature (T w,50) and its 90th / 99th percentiles", "explicit",
                     "Reader 1 adds daily maximum temperature and irrigation; reader 2 names T w,50. Both spans state the T w percentiles."),
        "relation_or_direction": C("slight increase of ~0.03 °C in median T w; no significant change in the 90th or 99th percentiles", "explicit",
                                   "Reader 1 adds the ~0.1 °C temperature decrease, which only reader 2's longer span contains. Adopted: what both spans state."),
        "geography": C("hot land areas and months", "explicit", "Reader 1 adds the 27 °C definition from a support span; reader 2 the evidence's words."),
        "temporal_frame": B(True, "contemporary conditions (forcings and boundary conditions circa 2000)", "r1",
                            "Reader 1's support span states the circa-2000 forcings; '30 analysed model years' is not in it and is trimmed."),
        "experimental_condition": B(False, "irrigation (Irrigated versus No-irrig ModelE simulations)", "r2",
                                    "Reader 1's support span states only that two ModelE simulations were run, not the irrigation contrast. Rule 3b: inferred.", content="differs"),
    },
    "LIT2-000315-C3": {
        "concept": S("Frequency of dangerous conditions, T w ≥ 27 °C."),
        "relation_or_direction": C("+0.5 day per year overall (22.6 to 23.1 days, 2%); almost doubling over hot locations in the Mississippi Valley (4 to 7 days per year)", "explicit",
                                   "Reader 1 adds Arabia, Indus and Ganges changes that neither evidence span states. Adopted: what reader 2's span states and reader 1's claim also states."),
        "geography": C("hot areas; the Mississippi Valley region", "explicit", "Reader 1 adds Arabia, Indus, Ganges. Adopted: the places both name."),
        "temporal_frame": B(True, "contemporary conditions (forcings and boundary conditions circa 2000)", "r1", _R1_SUP),
        "experimental_condition": C("due to irrigation", "explicit", "Reader 2 keeps the evidence's words; reader 1 the run description. Adopted: the part both state."),
    },
    "LIT2-000315-C4": {
        "concept": S("Frequency of extremely dangerous conditions, T w ≥ 30 °C."),
        "relation_or_direction": S("No significant overall change; increase over Arabia; decrease in the Indus basin."),
        "geography": C("Arabia; the Indus basin", "explicit", "Reader 1 adds 'hot regions overall'. Adopted: the places both name."),
        "temporal_frame": B(True, "contemporary conditions (forcings and boundary conditions circa 2000)", "r1", _R1_SUP),
        "experimental_condition": C("due to irrigation", "explicit", "As LIT2-000315-C3."),
    },
    # --- LIT2-000366 (auto-sklearn forest fire prediction) --------------------------
    "LIT2-000366-C1": {
        "concept": S("Prediction accuracy of the optimized framework."),
        "temporal_frame": S("'three years', both inferred."),
        "experimental_condition": C("different test sets", "explicit", "Reader 2 keeps the evidence's words; reader 1 the preprocessing from a support span. Adopted: the part both state."),
    },
    "LIT2-000366-C3": {
        "concept": C("forest fire whether index(FWI)", "explicit",
                     "Reader 1 adds 'the Canada's forest fire weather index system', which is in reader 2's longer span but not reader 1's. Adopted: the index both name, as stored (the source misspells 'weather')."),
        "relation_or_direction": C("calculated from temperature, humidity and wind speed", "explicit",
                                   "Reader 1 adds adoption by other national systems, from a sentence neither evidence span contains."),
        "geography": C("Canada", "explicit", "Reader 1 adds the United States, New Zealand and others from outside both evidence spans. Adopted: 'Canada'."),
        "temporal_frame": U("Reader 1 unknown; reader 2 explicit 'currently'. Rule 3a."),
    },
    # --- LIT2-000470 (US occupational heat safety consensus) -------------------------
    "LIT2-000470-C2": {
        "concept": S("A heat acclimatization (HA) program."),
        "relation_or_direction": S("Create and implement a 5-7-day progressive HA program."),
        "geography": B(True, "the US workers", "r1", _R1_SUP),
    },
    "LIT2-000470-C3": {
        "concept": S("Environmental (heat) measurements."),
        "relation_or_direction": S("Taken on-site, as close to the work site as possible."),
        "geography": B(True, "the US workers", "r1", _R1_SUP),
    },
    "LIT2-000470-C4": {
        "concept": S("Work in extreme heat by US workers."),
        "relation_or_direction": S("About 13.3 million every day."),
    },
    # --- LIT2-000499 (house impact, Blue Mountains NSW) ------------------------------
    "LIT2-000499-C1": {
        "concept": S("House defence and the likelihood of impact."),
        "relation_or_direction": S("Most important variable; 14.7% versus 42.4%."),
        "geography": B(True, "the Blue Mountains of NSW", "r1", _R1_SUP + " The fire names are in neither span and are trimmed."),
        "temporal_frame": B(True, "October 2013", "r1", _R1_SUP),
    },
    "LIT2-000499-C2": {
        "concept": S("Westerly distance to forest (and house impact)."),
        "relation_or_direction": S("Strong negative relationship up to ~50 m; none beyond."),
        "geography": B(True, "the Blue Mountains of NSW", "r1", _R1_SUP),
        "temporal_frame": B(True, "October 2013", "r1", _R1_SUP),
    },
    "LIT2-000499-C3": {
        "concept": S("Weather and the FFDI (Forest Fire Danger Index) in house impact."),
        "relation_or_direction": S("A minor role (20th variable), though impact was twice as high at FFDI 75 as at 34."),
        "geography": B(True, "the Blue Mountains of NSW", "r1", _R1_SUP),
        "temporal_frame": B(True, "October 2013", "r1", _R1_SUP),
    },
    # --- LIT2-000560 (dynamic auto-encoder wildfire prediction) ----------------------
    "LIT2-000560-C1": {
        "concept": S("Model performance on BCE loss (and the other metric)."),
        "relation_or_direction": S("Outperforms on BCE; not on the other metric."),
        "geography": C("Salt Lake City, Portland, and Medford", "explicit", "Reader 1 adds the grid-square description from a support span. Adopted: the evidence's places."),
        "temporal_frame": B(False, "validation data 06/08/2016 to 04/08/2020", "r2",
                            "Reader 1's support span states only the training period; the claim is about the validation period, which reader 2's span states. Rule 3b: inferred.", content="differs"),
        "experimental_condition": B(True, "temporal 70% training / 30% validation split", "r1",
                                    "Reader 1's support span states the temporal 70/30 split, which carries reader 2's 'different time period'."),
    },
    "LIT2-000560-C2": {
        "concept": S("Hectares burned in the wildfire season."),
        "relation_or_direction": S("Over 2.5 million ha; the largest season recorded in modern history."),
    },
    # --- LIT2-000662 (urban expansion and heat waves, 49 US cities) -------------------
    "LIT2-000662-C1": {
        "concept": C("urban expansion intensity index (UEII); heat wave intensity", "explicit",
                     "Reader 1 adds heat wave duration change, which its evidence span does not state."),
        "relation_or_direction": C("positive and significant (Spearman 0.317, p = 0.02699)", "explicit",
                                   "Reader 1 adds the negative duration correlation, from outside both evidence spans."),
        "geography": B(True, "the 49 cities in the U.S.", "r1", _R1_SUP),
        "temporal_frame": B(True, "27 years", "r1", "Reader 1's support span states '27 years' but not 1992 / 2019. Explicit kept for '27 years' only."),
        "experimental_condition": U("Reader 1 explicit heat-wave definition; reader 2 unknown. Rule 3a."),
    },
    "LIT2-000662-C2": {
        "concept": S("UEII and heat wave intensity change."),
        "relation_or_direction": S("Significant positive, 0.64, p = 0.03."),
        "geography": C("the West region", "explicit", "Reader 1 adds example cities from outside the evidence span."),
        "temporal_frame": U("Reader 1 explicit 27 years; reader 2 unknown. Rule 3a."),
        "experimental_condition": U("Rule 3a."),
    },
    "LIT2-000662-C3": {
        "concept": S("GEII and heat wave frequency, duration, season, intensity."),
        "relation_or_direction": S("Not statistically significant."),
        "geography": B(True, "the 49 cities in the U.S.", "r1", _R1_SUP),
        "temporal_frame": B(True, "27 years", "r1", "As LIT2-000662-C1."),
        "experimental_condition": U("Rule 3a."),
    },
    # --- LIT2-000673 (GEFS-Aerosols forecasts) ----------------------------------------
    "LIT2-000673-C2": {
        "concept": S("Daily AOD variations / enhancements caused by fire plumes."),
        "relation_or_direction": S("Two peaks reproduced; correlation (RMSE) 0.66 (0.23), 0.9 (0.12), 0.68 (0.31)."),
        "geography": S("The Alta Floresta site in the Amazon fire source region; elision only."),
        "temporal_frame": C("late August and late September", "explicit",
                            "Reader 1 gives the evaluation period from a support span; reader 2 the two peak dates in the evidence. Adopted: the evidence's dates."),
        "experimental_condition": U("Reader 1 unknown; reader 2 inferred. Rule 3a."),
    },
    "LIT2-000673-C4": {
        "concept": S("Major fires (biomass burning events) in the forecasts."),
        "relation_or_direction": S("Captured much better than NGACv2; the plume-rise part is hedged in both."),
        "temporal_frame": B(True, "5 July to 30 November 2019", "r1", "Reader 1's support span states the period; reader 2 infers '9 months from July 2019' from another sentence.", content="differs"),
        "claim_type": T("finding", "Reader 1 finding, reader 2 mechanism. The sentence both spans contain is the comparative forecast result; the hedged plume-rise "
                                   "explanation is only in reader 2's longer span. Span-limited: finding."),
    },
    # --- LIT2-000786 (bats and fire review) ------------------------------------------
    "LIT2-000786-C1": {
        "concept": B(True, "bat responses to prescribed fire and wildfire", "r1_evidence", "The evidence sentence itself names bat responses to prescribed fire and wildfire."),
        "relation_or_direction": S("Positive or neutral to prescribed fire; more negative for wildfire."),
        "geography": B(True, "North and South America, Europe, Australia, and Africa", "r1", _R1_SUP),
        "temporal_frame": S("Studies through April 2021, both inferred from the same sentence."),
        "experimental_condition": U("Reader 1 unknown; reader 2 explicit. Rule 3a."),
    },
    "LIT2-000786-C3": {
        "concept": S("Suitable habitat for the park's bat species after the wildfire."),
        "relation_or_direction": S("Declined ~40% and up to 60-80%."),
    },
    # --- LIT2-000927 (temperature and mortality, South Africa) -------------------------
    "LIT2-000927-C1": {
        "concept": C("maximum temperature", "explicit", "Reader 1 adds minimum temperature, DTR and mortality, which its evidence span does not state."),
        "relation_or_direction": C("most statistically significant temperature metric in 40 (77%) districts out of 52", "explicit",
                                   "Reader 1 adds the minimum-temperature and DTR counts, which only reader 2's span contains."),
        "geography": B(True, "the 52 districts in South Africa", "r1", _R1_SUP),
        "temporal_frame": B(True, "1997 to 2013", "r1", "Reader 1's support span states 1997 to 2013, not the summer months. Trimmed."),
        "experimental_condition": U("Reader 1 explicit DLNM; reader 2 unknown. Rule 3a."),
    },
    "LIT2-000927-C2": {
        "concept": S("Maximum temperature and mortality risk."),
        "relation_or_direction": S("Increased risk in all but three districts."),
        "geography": B(True, "the 52 districts in South Africa", "r1", _R1_SUP.replace("cites the same sentence", "cites another sentence"), content="differs"),
        "temporal_frame": B(True, "1997 to 2013", "r1", _R1_SUP),
        "experimental_condition": U("Rule 3a."),
    },
    "LIT2-000927-C3": {
        "concept": S("District maximum-temperature thresholds."),
        "relation_or_direction": S("Highest in the hot arid interior; lower in the temperate interior and on the coast."),
        "geography": S("The same four provinces; wording only."),
        "temporal_frame": B(False, "summer months", "r2",
                            "Reader 1's support span (the mortality data sentence) states 1997-2013 but not the summer months; reader 2's states the summer months. Adopted: what both value strings contain and a span states.", content="differs"),
        "experimental_condition": U("Rule 3a."),
    },
    "LIT2-000927-C4": {
        "concept": S("A heat-health warning system with district-level maximum-temperature thresholds."),
        "relation_or_direction": S("Recommends it."),
        "geography": B(False, "South Africa", "r2", "Reader 1 tagged 'South Africa' explicit, but its evidence span does not name it; reader 2's support span does. Rule 3b: inferred."),
    },
    # --- LIT2-001063 (FIRO, Lake Mendocino) -------------------------------------------
    "LIT2-001063-C1": {
        "concept": C("water saved through a FIRO-enabled major deviation", "explicit", "Reader 1 frames FIRO as drought adaptation; reader 2 'water saved'. Adopted: what the evidence states."),
        "relation_or_direction": S("Close to 20%."),
        "geography": B(True, "Lake Mendocino, a reservoir in the upper Russian River watershed in coastal northern California", "r1", _R1_SUP),
        "experimental_condition": B(True, "counterfactual: storage limited to the mandated level during the cool season", "r1",
                                    "Reader 1's support span states the counterfactual; reader 2 infers the same from another sentence."),
    },
    # --- LIT2-001075 (heat exposure in US prisons) -------------------------------------
    "LIT2-001075-C1": {
        "concept": S("Days with daily mean temperature over 85 °F (at prisons)."),
        "relation_or_direction": S("67.3% of facilities."),
        "geography": C("44 states and the District of Columbia", "explicit", "Reader 1 adds 'prisons ... (United States)'. Adopted: the span's own words."),
        "temporal_frame": S("2020 to 2023."),
        "experimental_condition": B(True, "daily air temperature from Daymet v4 (1-km grid)", "r1", "Reader 1's support span states Daymet v4 daily temperatures on a 1-km grid."),
    },
    "LIT2-001075-C3": {
        "concept": S("Anomaly in the upper decile (90th percentile) of summer temperature at prisons."),
        "relation_or_direction": C("highest anomalies at prisons in Washington, California, Maine, Idaho, and Texas", "explicit",
                                   "Reader 2 records the share of prisons and the mean anomaly from its longer span; reader 1's span states only the highest states. Adopted: what both spans state."),
        "geography": S("The same five states; reader 1 says 'prisons in'."),
        "temporal_frame": B(True, "2020 to 2023 compared with a 1990-2019 average", "r1", _R1_SUP),
        "experimental_condition": B(True, "daily air temperature from Daymet v4 (1-km grid)", "r1", "As LIT2-001075-C1."),
    },
    "LIT2-001075-C4": {
        "concept": S("Heat exposure of prisons by race/ethnicity of incarcerated populations."),
        "relation_or_direction": S("+8.6% nonwhite non-Hispanic; +15.0% Hispanic or Latino."),
        "geography": S("Across the US."),
        "temporal_frame": B(True, "summer 2019", "r1", "Reader 1's support span states the 2019 summer 90th percentile; reader 2 infers '2019' from another sentence."),
        "experimental_condition": U("Reader 1 explicit; reader 2 unknown. Rule 3a."),
    },
    # --- LIT2-001157 (fuel moisture thresholds, Sierras Chicas) ------------------------
    "LIT2-001157-C1": {
        "concept": S("Extreme and high fire-hazard fuel moisture thresholds."),
        "relation_or_direction": C("established at FMC of 55% and 67% (grasslands), 72% and 105% (forests), 106% and 121% (shrublands)", "explicit",
                                   "Reader 1 summarises ('differ by land cover'); reader 2 records the values both claims state."),
        "geography": B(True, "the Sierras Chicas in the Chaco Serrano subregion (Argentina)", "r1", _R1_SUP),
        "temporal_frame": B(True, "2002 to 2016", "r1", _R1_SUP),
        "experimental_condition": U("Reader 1 explicit percentile rule; reader 2 unknown. Rule 3a."),
    },
    "LIT2-001157-C2": {
        "concept": S("Pre-fire FMC and fire size."),
        "relation_or_direction": S("Large fires at ~74% versus small at ~91%."),
        "geography": B(True, "the Sierras Chicas (Argentina)", "r1", "Reader 1's support span names the Sierras Chicas (Argentina); reader 2 cites another sentence."),
        "temporal_frame": B(True, "2002 to 2016", "r1", _R1_SUP),
    },
    "LIT2-001157-C3": {
        "concept": S("Pre-fire FMC and upper-quantile fire size."),
        "relation_or_direction": S("Significant negative for the upper 30%; limited effect on the mean."),
        "geography": B(True, "the Sierras Chicas (Argentina)", "r1", "As LIT2-001157-C2."),
        "temporal_frame": B(True, "2002 to 2016", "r1", _R1_SUP),
    },
    "LIT2-001157-C4": {
        "concept": S("FMC in high versus low fire-activity years."),
        "relation_or_direction": S("12.1, 11.4 and 7.1 percentage points lower."),
        "geography": B(True, "the Sierras Chicas (Argentina)", "r1", "As LIT2-001157-C2."),
        "temporal_frame": B(True, "2002 to 2016", "r1", _R1_SUP),
    },
    # --- LIT2-001160 (heatwave metrics) -----------------------------------------------
    "LIT2-001160-C1": {
        "concept": S("Frequency of heatwave days (constant threshold)."),
        "relation_or_direction": C("around 5 days in the Midwest / Chicago; much more frequent in the South and Southwest US", "explicit",
                                   "Reader 1 adds 'entire month in some regions', which its evidence span does not state."),
        "geography": C("Midwest US, specifically Chicago; South and Southwest US", "explicit", "Reader 1 adds western Arizona and south-east California from outside its evidence span."),
        "experimental_condition": B(False, "heatwave defined as daily maximum temperature above 35 °C for at least four consecutive days", "r2",
                                    "Reader 1 tagged the definition explicit, but its evidence says only 'this definition'; reader 2's support span states it. Rule 3b: inferred."),
    },
    "LIT2-001160-C2": {
        "concept": C("frequency of heatwave days", "explicit", "Reader 1 adds heatwave amplitude, which its evidence span does not state."),
        "relation_or_direction": C("around 45 heatwave days in a two-month period at some locations", "explicit", "Reader 1 adds the Paris amplitude above 30 °C."),
        "geography": C("western Europe", "explicit", "Reader 1 adds the region around Paris. Adopted: the place both name (in reader 2's evidence span)."),
        "experimental_condition": C("minimum daily temperature exceeding the 90th percentile of the long-term TMIN distribution for each day and grid, for at least four consecutive days", "explicit",
                                    "Same definition; reader 1 adds the CPC data set. Adopted: reader 2's evidence words."),
    },
    "LIT2-001160-C3": {
        "concept": C("frequency of heatwave days", "explicit", "As LIT2-001160-C2."),
        "relation_or_direction": C("40+ heatwave days in two months", "explicit", "Reader 1 adds the 45+ °C amplitude."),
        "geography": C("a large region surrounding Moscow, Russia", "explicit", "Reader 1 adds western Russia."),
        "temporal_frame": B(False, "July and August, 2010", "r2", "Reader 1 tagged the dates explicit, but its evidence does not state them; reader 2's support does. Rule 3b: inferred."),
        "experimental_condition": B(True, "daily maximum temperature exceeding the 90th percentile of the long-term TMAX climatology for at least four consecutive days", "r1", _R1_SUP),
    },
    # --- LIT2-001236 (IoT fire detection, Attica) --------------------------------------
    "LIT2-001236-C1": {
        "concept": C("detection of the existence or lack of fire incident occurrence", "explicit",
                     "Reader 1 frames it as cross-platform decision support; reader 2 keeps the evidence's words."),
        "relation_or_direction": S("Detects presence or absence in 93.6-98.9% of over 5000 triggers."),
        "geography": B(True, "the eastern part of Attica Greece", "r1", _R1_SUP + " 'Rafina-Mati' falls outside reader 1's span and is trimmed."),
        "temporal_frame": B(True, "20-26/7/2018", "r1", _R1_SUP),
        "experimental_condition": C("optimal weight configurations; FD TRUE values tested in [0.60, 0.95]", "explicit", "Reader 2 keeps the evidence's words; reader 1 adds the fusion inputs."),
    },
    "LIT2-001236-C2": {
        "concept": S("The fire weather index (FWI); reader 1 adds its Canadian basis."),
        "relation_or_direction": S("Above 100 at ignition; extremely high for the whole fire."),
        "geography": B(True, "the eastern part of Attica Greece", "r1", _R1_SUP),
        "temporal_frame": B(True, "23 July 2018", "r1", _R1_SUP),
    },
    # --- LIT2-001293 (bivariate extremes method) ---------------------------------------
    "LIT2-001293-C1": {
        "concept": B(False, "recorded temperature and relative humidity conditions", "r2",
                     "Reader 1's evidence says only 'the conditions recorded'; reader 2's support states temperature and relative humidity. Rule 3b: inferred.", content="differs"),
        "relation_or_direction": S("All exceed 0.005; three exceed 0.001; one exceeds 0.0005."),
        "geography": C("the Karachi airport", "explicit", "Reader 1 adds 'Karachi, Pakistan'. Adopted: the evidence's words."),
        "temporal_frame": C("June 18 to June 23, 2015", "explicit", "Reader 1 adds the 1973-2015 record."),
        "experimental_condition": U("Reader 1 explicit; reader 2 unknown. Rule 3a."),
    },
    "LIT2-001293-C2": {
        "concept": S("The windspeed-dryness combination."),
        "relation_or_direction": S("Cedar Fire day not extremely rare; Witch Fire day quite rare."),
        "geography": B(True, "the March AFB station, Riverside County, CA", "r1", _R1_SUP.replace("cites the same sentence", "cites another sentence")),
        "temporal_frame": B(False, "ignition days of the Cedar and Witch Fires", "r2",
                            "Reader 1 tagged '1973-2015, September-November' explicit with no span stating it; reader 2's support states the ignition days. Rule 3b: inferred.", content="differs"),
        "experimental_condition": U("Rule 3a."),
    },
    "LIT2-001293-C3": {
        "concept": B(False, "windspeed and dryness (tail dependence χ)", "r2",
                     "Reader 1's evidence states the co-occurrence but not 'tail dependence'; reader 2's support names the variables. Rule 3b: inferred."),
        "relation_or_direction": S("χ ≈ 0.3; driest about 30% of the time at the highest windspeeds."),
        "geography": B(True, "the March AFB station, Riverside County, CA", "r1", _R1_SUP.replace("cites the same sentence", "cites another sentence")),
        "temporal_frame": B(False, "1973-2015, months of September, October, and November", "r2",
                            "Reader 1 tagged it explicit with no span; reader 2's support states it. Rule 3b: inferred."),
        "experimental_condition": U("Rule 3a."),
    },
    "LIT2-001293-C4": {
        "concept": C("temperature and humidity association", "explicit", "Reader 2's 'The Karachi data' names the data set; reader 1 the variables, which the evidence states."),
        "relation_or_direction": S("Asymptotically independent; negative association (η = 0.20)."),
        "geography": B(True, "the Karachi Airport station", "r1", _R1_SUP.replace("cites the same sentence", "cites another sentence")),
        "temporal_frame": B(False, "1973-2015", "r2", "Reader 1 tagged 'April-October' explicit with no span; reader 2's support states 1973-2015 only. Rule 3b: inferred.", content="differs"),
        "experimental_condition": U("Rule 3a."),
    },
    # --- LIT2-001308 (San Diego 2007 wildfires and ED visits) ---------------------------
    "LIT2-001308-C2": {
        "concept": S("Model fit for respiratory ED visits."),
        "relation_or_direction": S("76.6% deviance explained; ~15% under-estimate on the exception days."),
        "geography": B(True, "San Diego County, California", "r1", _R1_SUP.replace("cites the same sentence", "cites another sentence")),
        "temporal_frame": B(True, "08/01/2007 through 11/29/2007", "r1", _R1_SUP),
    },
}
