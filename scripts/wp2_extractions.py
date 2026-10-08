"""M4-WP2 Phase 1 (Phase B of M4-WP2r1): reader 1's reading of the four frozen candidates, as data.

**Manual reading by the EXECUTOR** (Claude Code, model claude-opus-5-5),
2026-10-08, under the WP1 rubric unchanged. Each file was SHA-256-verified
against the frozen corpus manifest and read completely, key by key. No LLM API
call, no model service, no embedding, no search over any other corpus file.

**What the reader knew beforehand, disclosed rather than claimed away.** Reader
1 is the prototype-exposed EXECUTOR. It knew the frozen retrieval terms
(`fire weather index`, `FWI`, `heat index`; `Oklahoma`, `Stephens`,
`California`) and each candidate's concept/place hit **counts** from the M4-WP2
retrieval report. It did **not** open the hit list (paths and spans in
`wp2_candidates.json` / `LITERATURE_WP2_CANDIDATES.md`) before every claim
below was recorded; hits are classified afterwards, in
`scripts/wp2_hit_classification.py`. No dimension is filled from a hit.

Claim selection under the five-claim cap preferred, in order: the paper's own
findings in the abstract and results; then background that frames the hazard
the paper examines. Passages considered and not promoted are kept.

The dimension rules, the scope rule, and the experimental-condition rule are
those of `scripts/wp1_extractions.py` (D-016, D-017). All four items are a
**relevance-guided candidate sample, not representative.**
"""

from __future__ import annotations

from climrr.litingest import child_path

EXTRACTION_METHOD = (
    "manual reading by the EXECUTOR (Claude Code, model claude-opus-5-5), reader 1; every candidate file "
    "read completely; no LLM API call, no model service, no embedding, no search over other corpus files; "
    "the reader is prototype-exposed and knew the frozen retrieval terms and per-candidate hit counts, but "
    "did not open hit locations before recording claims"
)
EXTRACTION_DATE = "2026-10-08"

ITEM_IDS = ("LIT-000166", "LIT-000519", "LIT-001501", "LIT-001536")


def K(key: str) -> str:
    return child_path("$", key)


def E(key: str, text: str, occurrence: int = 1) -> dict:
    return {"json_path": K(key), "text": text, "occurrence": occurrence}


def D(value: str, status: str, support: dict | None = None) -> dict:
    return {"value": value, "status": status, "support": support}


UNKNOWN = {"value": "unknown", "status": "unknown", "support": None}

ITEMS: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# LIT-000166 --- SPITFIRE, a global process-based fire regime model
_FIG3_166 = E("discussion", "(c) fractional area burnt (all as annual averages for 1982-1999)")
ITEMS["LIT-000166"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper builds and evaluates a global process-based model of wildfire regimes (ignition, spread, "
        "burnt area, fire season) and fire emissions; wildfire and its impacts are the subject."
    ),
    "scope_evidence": E("abstract", "A process-based fire regime model (SPITFIRE) has been developed, coupled with ecosystem dynamics in the LPJ Dynamic Global Vegetation Model, and used to explore fire regimes and the current impact of fire on the terrestrial carbon cycle and associated emissions of trace atmospheric constituents."),
    "claims": [
        {
            "claim_text": "The LPJ-SPITFIRE model estimates an average CO2 release of 2.24 Pg C per year from biomass burning during the 1980s and 1990s.",
            "claim_type": "finding",
            "concept": D("CO 2 from biomass burning (model estimate)", "explicit"),
            "relation_or_direction": D("average release of 2.24 Pg C yr −1", "explicit"),
            "geography": D("global", "inferred", E("results", "global patterns in simulated pyrogenic emissions")),
            "temporal_frame": D("1980s and 1990s", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("abstract", "The model estimates an average release of 2.24 Pg C yr −1 as CO 2 from biomass burning during the 1980s and 1990s."),
            "notes": "A model output. The results give 3.45 PgC yr −1 before croplands are excluded; 2.24 is after that correction (see rejected R4).",
        },
        {
            "claim_text": "Fire season length increases from wet/cold to warm/dry biomes in both satellite data and the model: one to three months in the boreal zone, four to seven in semi-arid and seasonal climates.",
            "claim_type": "finding",
            "concept": D("length of the fire season", "explicit"),
            "relation_or_direction": D("increases from wet/cold to warm/dry biomes; one to three months (boreal), four to seven months (semi-arid, highly seasonal)", "explicit"),
            "geography": D("biomes worldwide, aggregated by biome", "inferred", E("results", "Simulated and satellite-detected fire season lengths, defined on a grid cell basis as in Giglio et al. (2006), were aggregated by biomes")),
            "temporal_frame": D("November 2000 to October 2002 (MODIS evaluation period)", "inferred", E("methods", "Data from November 2000 to October 2002 are used in the evaluation.")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "The mean length of the fire season increases from wet/cold to warm/dry biomes, both in the data and in the model (Fig. 6).The fire season is short (one to three months) in the boreal zone and longer (four to seven months) in semi-arid and highly seasonal climates."),
            "notes": "The results add that the model tends to over-estimate fire season length.",
        },
        {
            "claim_text": "Simulated burnt area is greatest in seasonally dry regions, especially savannas, and least in wet or cold regions.",
            "claim_type": "finding",
            "concept": D("simulated area burnt", "explicit"),
            "relation_or_direction": D("maximal in seasonally dry regions, particularly savannas; minimal in wet and/or cold regions", "explicit"),
            "geography": D("seasonally dry regions; savannas; wet and/or cold regions (global simulation)", "explicit"),
            "temporal_frame": D("annual averages, 1982-1999", "inferred", _FIG3_166),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "Simulated area burnt (Fig. 3c) is maximal in seasonally dry regions, particularly in savannas (Fig. 4d), and minimal in wet and/or cold regions (Fig. 4b)."),
            "notes": "A model simulation result, not an observation.",
        },
        {
            "claim_text": "In the simulation, few ignitions along the west coast of the USA, western Iberian coasts and around the Rio de la Plata estuary produce burnt areas as high as inland regions with far more ignitions.",
            "claim_type": "finding",
            "concept": D("simulated burnt area relative to ignition frequency", "explicit"),
            "relation_or_direction": D("relatively few ignitions (<0.08 km−2 yr−1) produce simulated burnt area (>0.3 yr−1) as high as inland regions with much more frequent ignitions", "explicit"),
            "geography": D("west coast of the USA; western coasts of the Iberian Peninsula; north and south of the Rio de la Plata estuary", "explicit"),
            "temporal_frame": D("annual averages, 1982-1999", "inferred", _FIG3_166),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "In contrast, along the west coast of the USA, along the western coasts of the Iberian Peninsula, and north and south of the Rio de la Plata estuary in South America, relatively few ignitions (<0.08 km −2 yr −1 ) produce a simulated burnt area (>0.3 yr −1 ) as high as that found in inland regions with much more frequent ignitions."),
            "notes": "A model simulation result. The time frame is inferred from the Fig. 3 caption, to which the surrounding paragraph refers.",
        },
        {
            "claim_text": "The model's interannual variability of burnt area is weaker than observed in central Siberia; it tends to miss the large burnt areas of the most extreme years.",
            "claim_type": "finding",
            "concept": D("interannual variability of simulated area burnt", "explicit"),
            "relation_or_direction": D("less pronounced than observed; misses large burnt areas in the most extreme years", "explicit"),
            "geography": D("central Siberia", "inferred", E("discussion", "Comparison of (a) observed (Sukhinin et al., 2004) and (b) simulated annual average area burnt in central Siberia")),
            "temporal_frame": D("1996-2002 (period of the observed comparison data)", "inferred", E("methods", "The Sukhinin data are available on a monthly basis for 1996-2002.")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "The interannual variability of simulated area burnt is generally less pronounced than that observed (Fig. 9d), that is, the model tends to miss the large burnt areas in the most extreme years."),
            "notes": None,
        },
    ],
    "rejected_or_ambiguous": [
        {"evidence": E("methods", "Several fire danger indices are in use, including the Canadian Fire Weather Index (CFFBG, 1992) which has also been adapted to Indonesia"),
         "reason": "Lists operational fire danger indices as context for the model's design; the paper neither uses nor evaluates the Fire Weather Index."},
        {"evidence": E("discussion", "One is the prediction of the consequences of climate change for fire regimes, vegetation and pyrogenic trace-gas and particulate emissions."),
         "reason": "A proposed future application; no projection is made in this paper."},
        {"evidence": E("introduction", "Biomass burning is thought to contribute up to 50% of global CO and NO x emissions in the troposphere (Galanter et al., 2000)"),
         "reason": "Cited background; not promoted under the five-claim cap."},
        {"evidence": E("results", "The simulated average annual CO 2 release from biomass burning during the 1980s and 1990s amounts to 3.45 PgC yr −1 with an interannual variability (1 s.d.) of about 7%."),
         "reason": "The pre-cropland-correction figure; kept for audit of C1, which uses the corrected 2.24."},
    ],
    "terminal_status": "claims_extracted",
}

# ---------------------------------------------------------------------------
# LIT-000519 --- the Daily Fire Hazard Index (DFHI), Sardinia
_SARDINIA = E("results", "The area of interest, which consists of the region of Sardinia")
ITEMS["LIT-000519"] = {
    "bibliographic": {"title": "$.title", "note": "The stored title begins with 'remote sensing ', apparently the journal name fused to the title; recorded as stored."},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper develops a daily wildfire hazard (fire danger) index and validates it against official "
        "wildfire records for Sardinia; wildfire hazard is the subject."
    ),
    "scope_evidence": E("abstract", "The results were validated on the Italian region of Sardinia using official wildfire records provided by the regional administration."),
    "claims": [
        {
            "claim_text": "About one third of the pixels burned by wildfires in 2017 had been rated High or Very High Hazard on the day they burned, and a quarter Very High.",
            "claim_type": "finding",
            "concept": D("pixels reportedly burned by wildfires; 'High Hazard' and 'Very High Hazard' classes", "explicit"),
            "relation_or_direction": D("roughly one third classified High or Very High Hazard on the day they burnt; a quarter Very High", "explicit"),
            "geography": D("Sardinia", "inferred", _SARDINIA),
            "temporal_frame": D("2017", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("discussion", 'Roughly one third of the pixels that were reportedly burned by wildfires in the year 2017 were classified as "High Hazard" or "Very High Hazard" on the day they burnt, and in particular, a quarter of them was classified as "Very High Hazard".'),
            "notes": "The surrounding text places this result on the earlier index version (before the evapotranspiration correction); the new version gave 'slightly better, but qualitatively analogous results'. The authors caution that 2017 had too few qualifying fires for definitive conclusions (rejected R3).",
        },
        {
            "claim_text": "The revised DFHI algorithm generally returned more High and Very High Hazard pixels than the earlier version.",
            "claim_type": "finding",
            "concept": D("new algorithm; 'High' and 'Very High Hazard' pixels", "explicit"),
            "relation_or_direction": D("tended to return more", "explicit"),
            "geography": D("Sardinia", "inferred", _SARDINIA),
            "temporal_frame": D("2017 fire season, 1 June to 31 August", "inferred", E("results", "DFHI maps were generated for the entire fire season of 2017, conventionally assumed to start the first of June and to end on 31 August.")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("discussion", 'In general, the new algorithm tended to return more "High" and "Very High Hazard" pixels.'),
            "notes": None,
        },
        {
            "claim_text": "Per EFFIS data, 144,837 wildfires burned 1,717,369 hectares in France, Greece, Italy, Portugal and Spain from 2014 to 2018.",
            "claim_type": "background_citation",
            "concept": D("wildfires; land burned", "explicit"),
            "relation_or_direction": D("1,717,369 hectares burned as a result of 144,837 wildfires", "explicit"),
            "geography": D("France, Greece, Italy, Portugal, and Spain", "explicit"),
            "temporal_frame": D("2014 to 2018 (called a 'four-year time span' in the paper)", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("introduction", "According to the data gathered by the the European Forest Fire Information System (EFFIS), and taking into account only the wildfires recorded in a four-year time span that goes from 2014 to 2018 in France, Greece, Italy, Portugal, and Spain, 1,717,369 hectares of land were burned as a result of 144,837 wildfires [1][2][3][4]."),
            "notes": "The paper calls 2014-2018 a four-year span; recorded as stated.",
        },
        {
            "claim_text": "In Sardinia, the most damaging wildfires occur on days of strong Mistral winds (cited as well known).",
            "claim_type": "background_citation",
            "concept": D("most damaging wildfires; strong Mistral winds", "explicit"),
            "relation_or_direction": D("occur in days of strong Mistral winds", "explicit"),
            "geography": D("Sardinia", "explicit"),
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "The area of interest, which consists of the region of Sardinia, is particularly suitable for our purposes, since it is well known that the most damaging wildfires occur in days of strong Mistral winds [65]."),
            "notes": None,
        },
        {
            "claim_text": "The authors report that comparative studies in other regions found the FWI performed better than other fire danger methods in almost all instances.",
            "claim_type": "background_citation",
            "concept": D("FWI", "explicit"),
            "relation_or_direction": D("performed better than other methods in almost all instances", "explicit"),
            "geography": UNKNOWN,
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("introduction", "Similar studies have been carried out in other regions using other methods, with the result that the FWI performed better than other methods in almost all instances."),
            "notes": "Earlier in the same field the paper names the Canadian Forest Fire Weather Index (FWI) System. 'Other regions' are not named, so geography is unknown. The sentence follows the JRC comparative study [20] but carries no citation of its own.",
        },
    ],
    "rejected_or_ambiguous": [
        {"evidence": E("introduction", 'This index, commonly called "integrated" or "advanced", is based on the FPI derived by Burgan [27] for the United States and successfully validated in California.'),
         "reason": "Provenance of the method in passing; not about the study area or a hazard this paper examines."},
        {"evidence": E("discussion", "The index does not show any bias towards lower or higher risk classes, and predicts the areas at risk over the area of interest with good reliability."),
         "reason": "A conclusion stronger than the authors' own caveat (R3); not promoted."},
        {"evidence": E("discussion", "Unfortunately, the number of wildfires that satisfied the condition on the minimum burnt area in 2017, while significant, was not sufficient to draw definitive conclusions."),
         "reason": "The authors' caveat on C1-C2; kept for audit."},
        {"evidence": E("introduction", "notwithstanding the fact that over 90% of ignitions in the Mediterranean area are caused by human actions, either intentional or accidental."),
         "reason": "Uncited background; not promoted under the five-claim cap."},
    ],
    "terminal_status": "claims_extracted",
}

# ---------------------------------------------------------------------------
# LIT-001501 --- 2017-2018 precipitation whiplash and wildfires, Southern Great Plains
_SGP_DOMAIN = E("data and methods", "This study examined the role of a preceding precipitation whiplash event in providing fuel for wildfires across the SGP.Specifically, our study domain for analysis was a region bounded by a north and south latitude of 34")
ITEMS["LIT-001501"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper examines how a 2017-2018 precipitation whiplash (pluvial to drought) fuelled spring "
        "wildfires in the Southern Great Plains, with their impacts (acres burned, fatalities, homes)."
    ),
    "scope_evidence": E("abstract", "The aim of this study was to examine the role of preceding precipitation whiplash events in providing fuel for wildfires, with 2017-2018 investigated as a case study."),
    "claims": [
        {
            "claim_text": "Lag correlation showed a significant 0.53 correlation between precipitation in the preceding August and both the number of April wildfires and acres burned.",
            "claim_type": "finding",
            "concept": D("precipitation in the August prior; number of April wildfires and acres burned", "explicit"),
            "relation_or_direction": D("significant correlation of 0.53", "explicit"),
            "geography": D("study domain across the SGP (Southern Great Plains)", "inferred", _SGP_DOMAIN),
            "temporal_frame": D("wildfires 1984-2020 (historical record analysed)", "inferred", E("data and methods", "the number of acres burned and the ignition date were gathered for all fires designated as wildfires between 1984 and 2020.")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "Through lag correlation analysis, a significant correlation of 0.53 was found between precipitation in the August prior and the number of wildfires as well as the number of acres burned in April (figures 1(a) and (d))."),
            "notes": "Large fires only (MTBS thresholds); the authors note a skewed distribution because no large fire occurred in about a third of March-April months.",
        },
        {
            "claim_text": "Precipitation at 137% of normal in the 2017 growing season gave way rapidly to drought, with precipitation 21% of normal through the following cool winter season.",
            "claim_type": "finding",
            "concept": D("precipitation anomalies; drought conditions", "explicit"),
            "relation_or_direction": D("137% of normal, then rapidly cascaded into drought with 21% of normal", "explicit"),
            "geography": D("Oklahoma and Texas panhandles", "inferred", E("abstract", "this study examined a highly impactful precipitation whiplash event that occurred during the Fall of 2017 across the Oklahoma and Texas panhandles")),
            "temporal_frame": D("2017 growing season; then the cool winter season", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("abstract", "Precipitation anomalies that were 137% of normal during the 2017 growing season rapidly cascaded into drought conditions with precipitation anomalies 21% of normal throughout the cool winter season."),
            "notes": None,
        },
        {
            "claim_text": "In March-April 2018 the study domain had 23 wildfires burning 556,347 acres, against an average of 5.66 wildfires and about 120,500 acres.",
            "claim_type": "finding",
            "concept": D("number of wildfires; acres burned", "explicit"),
            "relation_or_direction": D("23 wildfires, 556 347 acres vs an average of 5.66 wildfires, ~120 500 acres", "explicit"),
            "geography": D("study domain across the SGP (Southern Great Plains)", "inferred", _SGP_DOMAIN),
            "temporal_frame": D("March-April 2018", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "In 2018, the March-April period yielded 23 wildfires that burned a total of 556 347 acres, compared to the average of 5.66 wildfires that burn approximately 120 500 acres (figure 2(c))."),
            "notes": None,
        },
        {
            "claim_text": "The Rhea Fire, starting 12 April 2018 in Dewey County, northwest Oklahoma, burned 277,949 acres, with at least two fatalities and dozens of homes destroyed.",
            "claim_type": "finding",
            "concept": D("Rhea Fire", "explicit"),
            "relation_or_direction": D("burned 277 949.00 acres; at least two fatalities; dozens of homes destroyed; over 500 personnel dispatched", "explicit"),
            "geography": D("Dewey County, NW Oklahoma", "explicit"),
            "temporal_frame": D("from 12 April 2018", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "The Rhea Fire was by far the largest, beginning at approximately 1730 UTC on 12 April 2018, in Dewey County, which lies in NW Oklahoma.The fire burned a total of 277 949.00 acres with at least two fatalities, dozens of homes destroyed, and over 500 personnel dispatched to fight and mitigate the fire."),
            "notes": "The abstract attributes the same fatalities and homes to the March-April 2018 fires collectively; the results attribute them to the Rhea Fire.",
        },
        {
            "claim_text": "The authors argue that more frequent whiplash events, with fast vegetation recovery and desiccation, raise the risk of whiplash cascading into mega-fire conditions much more often in the future.",
            "claim_type": "projection",
            "concept": D("precipitation whiplash events; conditions that support mega-fires", "explicit"),
            "relation_or_direction": D("enhances the risk ... at a much higher frequency", "explicit"),
            "geography": D("across the SGP", "explicit"),
            "temporal_frame": D("in the future (no horizon stated)", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("discussion", "Therefore, the combination of an increase in precipitation whiplash events and the quick recovery and desiccation of the environment across the SGP, enhances the risk of precipitation whiplash events cascading into conditions that support mega-fires at a much higher frequency in the future."),
            "notes": "No emissions scenario or horizon is named; the argument rests on cited projections of precipitation variability.",
        },
    ],
    "rejected_or_ambiguous": [
        {"evidence": E("results", "Unlike precipitation and NDVI, temperature anomalies do not correlate significantly with the number of wildfires and acres burned in April."),
         "reason": "A valid finding of the paper; not promoted under the five-claim cap."},
        {"evidence": E("data and methods", "In particular, to examine the soil moisture response, the fractional water index (FWI) was calculated at three different levels; 5, 25, and 60 cm below the natural sod cover"),
         "reason": "Defines 'FWI' in this paper as the Oklahoma Mesonet fractional water index (soil moisture), not a fire weather index. The soil-moisture transect is not promoted (cap)."},
        {"evidence": E("introduction", "For example, more than 1.4 million people in Oklahoma, or 41% of the population, live in an area at an elevated risk of wildfire (wildfirerisk.org2022)."),
         "reason": "Cited background; not promoted under the cap."},
        {"evidence": E("discussion", "These results also match those found by (Herna\u0301ndez Ayala et al 2021) in California, where 11 of the 20 wildfire seasons studied were found to be preceded by above-average levels of precipitation and vegetation growth."),
         "reason": "A cited comparison about another region; not this paper's evidence. (The source stores the accent in 'Hernández' as a separate combining code point, U+0301; the quote matches it.)"},
        {"evidence": E("introduction", "Under projected 21st-century climate change, precipitation variability is expected to increase, contributing to increased vulnerability across the SGP"),
         "reason": "Cited background projection; no scenario named; not promoted."},
    ],
    "terminal_status": "claims_extracted",
}

# ---------------------------------------------------------------------------
# LIT-001536 --- summer heat exposure at US prisons
_US_PRISONS = E("abstract", "for 1,614 prisons in the United States from 1990 to 2023")
_YEAR_2019 = E("results", "Next, we assessed how heat exposure (as measured by the 90th percentile summer temperature in 2019)")
ITEMS["LIT-001536"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper quantifies summer heat exposure (modelled air-temperature metrics) at US prisons and its "
        "relation to population and facility characteristics; heat hazard, exposure and vulnerability are the subject."
    ),
    "scope_evidence": E("abstract", "We leveraged a high-resolution air temperature data set to evaluate short and long-term patterns of heat metrics for 1,614 prisons in the United States from 1990 to 2023."),
    "claims": [
        {
            "claim_text": "The ten most heat-exposed US prisons, by 2020-2023 location-specific 90th-percentile summer temperature, were in California, Arizona and Nevada.",
            "claim_type": "finding",
            "concept": D("most heat-exposed facilities, measured by the location-specific 90th percentile temperature", "inferred", E("results", "Figure 1b shows variation in the location-specific 90th percentile temperature at prisons averaged from 2020 to 2023.")),
            "relation_or_direction": D("top 10 located in California, Arizona and Nevada", "explicit"),
            "geography": D("California, Arizona and Nevada", "explicit"),
            "temporal_frame": D("2020-2023 average", "inferred", E("results", "Figure 1b shows variation in the location-specific 90th percentile temperature at prisons averaged from 2020 to 2023.")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "The top 10 most heat-exposed facilities were in California, Arizona and Nevada (Figure 1b)."),
            "notes": "Temperatures are from the Daymet modelled air-temperature data set, not station observations.",
        },
        {
            "claim_text": "67.3% of US prisons, in 44 states and the District of Columbia, had at least one day with daily mean temperature above 85°F during 2020-2023.",
            "claim_type": "finding",
            "concept": D("days with daily mean temperature over 85°F", "explicit"),
            "relation_or_direction": D("majority (67.3%) of facilities had at least one such day", "explicit"),
            "geography": D("44 states and the District of Columbia", "explicit"),
            "temporal_frame": D("2020 to 2023", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "The majority (67.3%) of facilities (at least 986,145 incarcerated people and 222,154 staff) in 44 states and the District of Columbia had at least one day that the daily mean temperature was over 85°F from 2020 to 2023 (Figure 1a)."),
            "notes": "Summer months only (1 June to 31 August), per the methods; modelled temperatures.",
        },
        {
            "claim_text": "From 2020 to 2023, 1,135 prisons (70.3%) had positive anomalies in their upper-decile summer heat exposure relative to the 1990-2019 baseline.",
            "claim_type": "finding",
            "concept": D("upper decile of heat exposure", "explicit"),
            "relation_or_direction": D("positive changes for 1,135 (70.3%) prisons", "explicit"),
            "geography": D("United States (1,614 prisons)", "inferred", _US_PRISONS),
            "temporal_frame": D("2020-2023 compared with a 1990-2019 average", "inferred", E("results", "Figure 2 shows the spatial pattern of anomalies in the average 90th percentile summer temperature for prisons from 2020 to 2023 when compared to a 1990-2019 averaged summer 90th percentile.")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "From 2020 to 2023, there were positive changes in the upper decile of heat exposure for 1,135 (70.3%) prisons meaning these prisons experienced approximately 9 out of 92 total days of summer that were hotter than all previous summers, on average, for a given location."),
            "notes": "The 1990-2019 baseline is itself from the modelled Daymet data set, not observations. 'Hotter than all previous summers' is the paper's own gloss and is not adopted in claim_text.",
        },
        {
            "claim_text": "Population-weighted summer heat exposure was highest for Hispanic or Latino incarcerated people (97.1°F), against 93.2-94.7°F for the other groups.",
            "claim_type": "finding",
            "concept": D("population-weighted summer heat exposure by race/ethnicity", "explicit"),
            "relation_or_direction": D("Hispanic or Latino highest at 97.1°F; other groups 93.2-94.7°F", "explicit"),
            "geography": D("United States (all prisons)", "inferred", _US_PRISONS),
            "temporal_frame": D("summer 2019", "inferred", E("materials and methods", "we used the 2019 summer 90th percentile of daily max air temperature to match with the year of BJSCensus2019")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "Across all prisons, the population-weighted summer heat exposure for the white, non-Hispanic, Black, non-Hispanic, American Indian non-Hispanic, Asian, non-Hispanic, and non-white, non-Hispanic incarcerated populations was between 93.2 and 94.7°F, while the Hispanic or Latino subgroup had the highest population-weighted exposure at 97.1°F (Table S4 in Supporting Information S1)."),
            "notes": None,
        },
        {
            "claim_text": "Nine of 17 facility-level characteristics hypothesized to modify heat risk were associated with significantly higher heat exposure (p < 0.05).",
            "claim_type": "finding",
            "concept": D("facility-level characteristics hypothesized to modify heat risk; heat exposure", "explicit"),
            "relation_or_direction": D("9 of 17 had statistically significant (p < 0.05) higher heat exposures", "explicit"),
            "geography": D("United States (all prisons)", "inferred", _US_PRISONS),
            "temporal_frame": D("summer 2019", "inferred", _YEAR_2019),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "Nine of the 17 test variables had statistically significant (p < 0.05) higher heat exposures for the groups with hypothesized effects on heat risk suggesting that these groups may face elevated risk not only due to these facility-level characteristics but also due to elevated heat exposures."),
            "notes": None,
        },
    ],
    "rejected_or_ambiguous": [
        {"evidence": E("discussion", "a national study on heat-related mortality in prisons determined that neither heat index or wet bulb globe temperature better capture the relationship between heat and total mortality in the incarcerated population (Skarha et al., 2023)."),
         "reason": "A cited methodological aside justifying the paper's use of air temperature; not a finding about heat index in this paper; not promoted (cap)."},
        {"evidence": E("results", "From 2020 to 2023, 828 (51.3%) facilities had at least one day that the prison experienced an outdoor temperature 10°F higher than their location-specific mean summer temperature (Figure 3)."),
         "reason": "Valid; not promoted under the cap. Its mortality link is a cited estimate."},
        {"evidence": E("introduction", "while the provision of air conditioning (AC) has been shown to effectively eliminate heat-related mortality in Texas prisons (Skarha et al., 2022)"),
         "reason": "Cited background; not promoted under the cap."},
        {"evidence": E("discussion", "However, a decarceration approach is the most effective (physically and economically speaking) long-term solution to reduce environmental-related risk produced in carceral settings."),
         "reason": "A normative recommendation not tested by the paper's analysis."},
    ],
    "terminal_status": "claims_extracted",
}
