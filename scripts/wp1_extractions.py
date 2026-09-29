"""M4-WP1 Phase C: the EXECUTOR's reading of the ten sampled papers, as data.

**Manual reading by the EXECUTOR** (Claude Code, model claude-opus-5-5),
2026-09-29. Every sampled file was read completely, key by key, from its
decoded JSON. No LLM API call, no model inference service, no embedding, no
search over any other corpus file. Nothing here was guided by a ClimRR
prototype, a pilot family, or the collection query: none of them is read by
this file or by `build_wp1_claims.py`.

What this file holds and what it does not
-----------------------------------------

For each item: the scope judgement with one quoted span; bibliographic fields
only where a field with that content exists; up to five claims; and the
passages considered and not promoted. **Every quoted span is exact text of the
decoded source string** --- the builder locates it, slices the source with the
resulting `[start, end)` code-point span, and fails if the slice differs. No
offset is written here by hand.

Dimension rule. `explicit` means the paper says it, in the claim's own span or
in the quoted `support` span. `inferred` means the extractor linked it, and
always carries the `support` span that the link rests on. `unknown` means the
paper does not state it for this claim, and the value is the string `unknown`.
Nothing is filled from general knowledge, filenames, the query or the
prototypes.

Scope rule. `in_scope_hazard`: the paper itself discusses a climate or weather
hazard or its impacts, judged from its own text. `off_topic`: it does not.
`ambiguous`: hazard language is present but the paper does not examine a
hazard or its impacts. Claims are extracted only for `in_scope_hazard` items;
for the others the terminal status is `off_topic` or `ambiguous_only` and the
passages considered are kept under `rejected_or_ambiguous`.
"""

from __future__ import annotations

from climrr.litingest import child_path

EXTRACTION_METHOD = (
    "manual reading by the EXECUTOR (Claude Code, model claude-opus-5-5); every "
    "sampled file read completely; no LLM API call, no model service, no embedding, "
    "no search over other corpus files; no prototype, pilot family or collection "
    "query consulted"
)
EXTRACTION_DATE = "2026-09-29"


def K(key: str) -> str:
    """JSON path of a top-level key."""
    return child_path("$", key)


def E(key: str, text: str, occurrence: int = 1) -> dict:
    """An evidence span: exact text in the string at top-level `key`."""
    return {"json_path": K(key), "text": text, "occurrence": occurrence}


def D(value: str, status: str, support: dict | None = None) -> dict:
    return {"value": value, "status": status, "support": support}


UNKNOWN = {"value": "unknown", "status": "unknown", "support": None}


ITEMS: dict[str, dict] = {}

# ---------------------------------------------------------------------------
ITEMS["LIT-000001"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "off_topic",
    "scope_reason": (
        "A thermodynamics paper proposing an action-based method to estimate the entropy of "
        "atmospheric gases; it mentions global warming but examines no climate or weather hazard "
        "or its impacts."
    ),
    "scope_evidence": E("abstract", "A convenient model for estimating the total entropy (ΣS i ) of atmospheric gases based on physical action is proposed."),
    "claims": [],
    "rejected_or_ambiguous": [
        {
            "evidence": E("introduction", "This action model may help provide an approach to prediction of the rate of global warming based on causal responses to the increasing greenhouse gas content of the atmosphere, rather than statistical correlations."),
            "reason": "A hedged statement of possible future use ('may help'); not a finding, and not about a hazard. Paper is off_topic.",
        },
        {
            "evidence": E("greenhouse gases and temperature equilibration in the gravitational field", "Perhaps it is more apt to consider that the greenhouse gases such as water play an important role in holding up the sky, enabling reversible gravitational work, thereby cooling the atmosphere!"),
            "reason": "Speculative ('Perhaps'), not supported by an analysis in this paper, and not about a hazard. Paper is off_topic.",
        },
    ],
    "terminal_status": "off_topic",
}

# ---------------------------------------------------------------------------
_GEO_191 = D(
    "Northwest Atlantic (the region of the species studied, per the title); the experiments were laboratory treatments",
    "inferred",
    E("title", "Three Species of Northwest Atlantic Bivalves"),
)
ITEMS["LIT-000191"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper tests how elevated seawater temperature and CO2 (warming and acidification) "
        "affect survival and growth of coastal bivalves, i.e. impacts of climate-driven stressors."
    ),
    "scope_evidence": E("abstract", "Rising CO 2 concentrations and water temperatures this century are likely to have transformative effects on many coastal marine organisms."),
    "claims": [
        {
            "claim_text": "Higher temperature and higher CO2 each significantly depressed survival, development, growth and lipid synthesis of hard clam and bay scallop larvae, and the effects were additive.",
            "claim_type": "finding",
            "concept": D("increases in temperature and CO 2; larval survival, development, growth, and lipid synthesis", "explicit"),
            "relation_or_direction": D("each significantly depressed; effects additive", "explicit"),
            "geography": _GEO_191,
            "temporal_frame": UNKNOWN,
            "scenario": D(
                "experimental treatments 24 and 28 °C and ~250, 390 and 750 ppm CO2, described as representative of past, present and future summer conditions in temperate estuaries",
                "explicit",
                E("abstract", "to temperatures (24 and 28uC) and CO 2 concentrations (,250, 390, and 750 ppm) representative of past, present, and future summer conditions in temperate estuaries"),
            ),
            "evidence": E("abstract", "Results demonstrated that increases in temperature and CO 2 each significantly depressed survival, development, growth, and lipid synthesis of M. mercenaria and A. irradians larvae and that the effects were additive."),
            "notes": "'uC' in the source is the extracted form of °C; the evidence text is kept exactly as stored.",
        },
        {
            "claim_text": "Juvenile hard clams and bay scallops were harmed by the higher temperature but juvenile oysters were not; juvenile oysters and bay scallops were harmed by higher CO2 but juvenile hard clams were not.",
            "claim_type": "finding",
            "concept": D("higher temperatures; higher CO 2 concentrations; juvenile bivalves", "explicit"),
            "relation_or_direction": D("negatively impacted / negatively affected, species-dependent", "explicit"),
            "geography": _GEO_191,
            "temporal_frame": UNKNOWN,
            "scenario": D(
                "juvenile treatments 24 and 28 °C and ~400 and 1700 ppm CO2",
                "explicit",
                E("juvenile experiments", "CO 2 was continuously delivered as described above at ,400 and 1700 ppm"),
            ),
            "evidence": E("abstract", "Juvenile M. mercenaria and A. irradians were negatively impacted by higher temperatures while C. virginica juveniles were not. C. virginica and A. irradians juveniles were negatively affected by higher CO 2 concentrations, while M. mercenaria was not."),
            "notes": None,
        },
        {
            "claim_text": "Bivalve larvae were substantially more vulnerable to elevated CO2 than juvenile stages.",
            "claim_type": "finding",
            "concept": D("elevated CO 2; larval versus juvenile vulnerability", "explicit"),
            "relation_or_direction": D("larvae substantially more vulnerable than juveniles", "explicit"),
            "geography": _GEO_191,
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "evidence": E("abstract", "Larvae were substantially more vulnerable to elevated CO 2 than juvenile stages."),
            "notes": None,
        },
        {
            "claim_text": "The authors suggest current and future increases in temperature and CO2 are likely to have negative consequences for coastal bivalve populations.",
            "claim_type": "projection",
            "concept": D("current and future increases in temperature and CO 2; coastal bivalve populations", "explicit"),
            "relation_or_direction": D("likely negative consequences (hedged: 'suggest', 'likely')", "explicit"),
            "geography": UNKNOWN,
            "temporal_frame": D("current and future (horizon not stated)", "explicit"),
            "scenario": UNKNOWN,
            "evidence": E("abstract", "These findings suggest that current and future increases in temperature and CO 2 are likely to have negative consequences for coastal bivalve populations."),
            "notes": "'coastal' is a setting, not a stated geography, so geography is unknown.",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("discussion", "Our results demonstrate that interannual variability in temperature and CO 2 are also likely to promote such cycles."),
            "reason": "The experiments applied static treatments; interannual variability was not tested. An extrapolation, not promoted.",
        },
        {
            "evidence": E("introduction", "Global temperatures are expected to increase 2 to 5uC this century [2]."),
            "reason": "Background statement attributed to another source; not this paper's evidence. Not promoted.",
        },
        {
            "evidence": E("discussion", "three weeks .28uC in NY in 2010; C. Flagg, Stony Brook University, unpublished data"),
            "reason": "Context from unpublished data cited in passing; not a finding of this paper.",
        },
    ],
    "terminal_status": "claims_extracted",
}

# ---------------------------------------------------------------------------
_GEO_381 = D(
    "old-growth subtropical forest in southern China (Dinghushan natural reserve, Guangdong)",
    "explicit",
    E("abstract", "an old-growth subtropical forest in southern China"),
)
_TIME_381 = D(
    "past 24 years (censuses 1992-2015)",
    "explicit",
    E("abstract", "shifts in functional composition over past 24 years"),
)
ITEMS["LIT-000381"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper attributes a 24-year shift in forest composition to soil dryness (drought) "
        "under regional warming and changed precipitation, i.e. an impact of a climate hazard."
    ),
    "scope_evidence": E("introduction", "In our study site, previous studies have demonstrated that changes in regional warming and precipitation patterns led to decrease in annual relative humidity and soil water contents within root zone in past decades [14]."),
    "claims": [
        {
            "claim_text": "Over 24 years, the forest's species composition shifted toward species with high leaf nutrients, photosynthesis and hydraulic conductivity, low water-use efficiency and high drought tolerance, attributed to soil dryness and disturbance.",
            "claim_type": "finding",
            "concept": D("functional (species) composition; drought tolerance traits; soil dryness and disturbance", "explicit"),
            "relation_or_direction": D("shifted to favor ... high drought tolerance; due to soil dryness and disturbance", "explicit"),
            "geography": _GEO_381,
            "temporal_frame": _TIME_381,
            "scenario": UNKNOWN,
            "evidence": E("abstract", "We found that species composition had shifted to favor species with high leaf nutrient content, high photosynthesis rate, high hydraulic conductivity, low water-use efficiency, and high drought tolerance traits, which was due to soil dryness and disturbance."),
            "notes": None,
        },
        {
            "claim_text": "Soil dryness and disturbance together explained 47-58% of quadrat-level trait value changes.",
            "claim_type": "finding",
            "concept": D("soil dryness and disturbance; quadrats' trait value changes", "explicit"),
            "relation_or_direction": D("explained 47-58% together", "explicit"),
            "geography": _GEO_381,
            "temporal_frame": _TIME_381,
            "scenario": UNKNOWN,
            "evidence": E("abstract", "These two factors explained 47-58% of quadrats' trait value changes together."),
            "notes": "'These two factors' refers to soil dryness and disturbance, named in the preceding sentence of the same field.",
        },
        {
            "claim_text": "The increase in community drought tolerance was likely due to soil dryness rather than disturbance.",
            "claim_type": "mechanism",
            "concept": D("increasing drought tolerance; soil dryness; disturbance", "explicit"),
            "relation_or_direction": D("likely due to soil dryness but not disturbance (hedged)", "explicit"),
            "geography": D(
                "DHS plot (Dinghushan), monsoon evergreen broad-leaved forest",
                "explicit",
                E("discussion", "the species composition in the monsoon evergreen broad-leaved forest in DHS plot"),
            ),
            "temporal_frame": _TIME_381,
            "scenario": UNKNOWN,
            "evidence": E("discussion", "Increasing drought tolerance (Hypothesis 2) was supported by our result (Figure 2) and it was likely due to soil dryness but not disturbance"),
            "notes": "The discussion field repeats this passage; the first occurrence is used.",
        },
        {
            "claim_text": "Prior studies at the site found regional warming and changed precipitation patterns reduced annual relative humidity and root-zone soil water over past decades.",
            "claim_type": "background_citation",
            "concept": D("regional warming and precipitation patterns; annual relative humidity; soil water contents within root zone", "explicit"),
            "relation_or_direction": D("led to decrease", "explicit"),
            "geography": D(
                "the study site: Dinghushan natural reserve, Guangdong Province, southern China",
                "explicit",
                E("materials and methods", "Dinghushan natural reserve (DHS, 23.17 • N, 112.56 • E) located in the middle of Guangdong Province in southern China"),
            ),
            "temporal_frame": D("past decades", "explicit"),
            "scenario": UNKNOWN,
            "evidence": E("introduction", "In our study site, previous studies have demonstrated that changes in regional warming and precipitation patterns led to decrease in annual relative humidity and soil water contents within root zone in past decades [14]."),
            "notes": "Attributed to reference [14]; recorded as background, not as this paper's finding.",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("conclusion", "These changes of the monsoon evergreen broad-leaved forest might affect forest ecosystem services, such as carbon sequestration and biodiversity conservation."),
            "reason": "Speculative ('might affect'); not tested in the paper.",
        },
        {
            "evidence": E("discussion", "we hypothesized that environment change forced community-level ecology strategy to shift from conservation (K-strategy) to resource acquisition (r-strategy) with drought tolerance"),
            "reason": "Stated as a hypothesis; the support offered is consistency of patterns, not a test.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "Several fields repeat whole passages (an extraction artifact of the source file); spans use the first occurrence.",
}

# ---------------------------------------------------------------------------
_SITES_571 = "three study sites in the western pamirs in tajikistan"
ITEMS["LIT-000571"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "Borderline. The subject is social organization around irrigation, but the paper itself "
        "discusses water scarcity and weather-triggered mass movements as hazards to settlements "
        "and irrigation, and how communities respond to them."
    ),
    "scope_evidence": E("results", "On the other hand, in the high mountain context of the Pamirs, larger snow and ice masses, as well as rather rare heavy rainfall pose potential dangers for settlements, arable land, and irrigation infrastructure"),
    "claims": [
        {
            "claim_text": "At the Khorog and Ishkāshim stations, mean annual precipitation is below the threshold for successful rainfed agriculture, and nearly the whole April-September vegetation period is strongly arid.",
            "claim_type": "finding",
            "concept": D("mean annual precipitation; arid regime of the vegetation period", "explicit"),
            "relation_or_direction": D("below the threshold for rainfed agriculture; strong arid regime", "explicit"),
            "geography": D(
                "Khorog and Ishkāshim measuring stations, Western Pamirs, Tajikistan",
                "explicit",
                E(_SITES_571, "the climate diagrams of Khorog and the settlement of Ishka\u0304shim"),  # source: a + U+0304 combining macron
            ),
            "temporal_frame": D("vegetation period April to September (climatological period of the diagrams not stated)", "explicit"),
            "scenario": UNKNOWN,
            "evidence": E(_SITES_571, "at both measuring stations, first, the mean annual precipitation is below the threshold for practicing rainfed agriculture successfully and, second, that nearly the whole vegetation period from April to September is characterized by a strong arid regime"),
            "notes": "The field repeats this passage; the first occurrence is used.",
        },
        {
            "claim_text": "In the Pamirs, large snow and ice masses and rare heavy rainfall endanger settlements, arable land, irrigation infrastructure and transport links by triggering avalanches, mudflows and slope erosion.",
            "claim_type": "mechanism",
            "concept": D("larger snow and ice masses; rather rare heavy rainfall; destructive mass movements", "explicit"),
            "relation_or_direction": D("pose potential dangers; can trigger avalanches, mudflows, and slope erosion", "explicit"),
            "geography": D("the Pamirs (high mountain context)", "explicit"),
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "evidence": E("results", "On the other hand, in the high mountain context of the Pamirs, larger snow and ice masses, as well as rather rare heavy rainfall pose potential dangers for settlements, arable land, and irrigation infrastructure, as well as communication lines and traffic installations, as they can trigger destructive mass movements such as avalanches, mudflows, and slope erosion"),
            "notes": "Supported in the paper by references and respondents; recorded as the paper states it.",
        },
        {
            "claim_text": "In Shirgin Village, summers with serious water scarcity force irrigation subgroups to negotiate distribution themselves, and in severe shortage each beneficiary's irrigation slot can shrink below one hour.",
            "claim_type": "finding",
            "concept": D("serious water scarcity; irrigation water distribution", "explicit"),
            "relation_or_direction": D("time slot shortened to less than one hour per beneficiary", "explicit"),
            "geography": D(
                "Shirgin Village, Ishkāshim District, Western Pamirs",
                "explicit",
                E("results", "the local irrigation arrangement of shirgin village-"),
            ),
            "temporal_frame": D("summers with serious water scarcity", "explicit"),
            "scenario": UNKNOWN,
            "evidence": E("results", "In summers with serious water scarcity, the canal-specific subgroups mentioned before receiving 24-h-long irrigation rights, have to negotiate the water distribution within their groups independently. When the water shortage is severe, the time slot for irrigation can be shortened to less than one hour duration per beneficiary"),
            "notes": None,
        },
        {
            "claim_text": "In Sizhd Village, farms on the western edge suffer most from acute water shortages, especially after winters with low precipitation.",
            "claim_type": "finding",
            "concept": D("acute water shortages", "explicit"),
            "relation_or_direction": D("suffer the most, especially after winters with low precipitation", "explicit"),
            "geography": D(
                "Sizhd Village, Western Pamirs",
                "explicit",
                E("results", "the interlocal irrigation arrangement of sizhd village-"),
            ),
            "temporal_frame": D("after winters with low precipitation", "explicit"),
            "scenario": UNKNOWN,
            "evidence": E("results", "However, the farms located on the western edge of the village suffer the most from acute water shortages, especially after winters with low precipitation."),
            "notes": None,
        },
        {
            "claim_text": "In Porshnev, after winters with little snow farmers mainly grow early-ripening, less water-needy fodder crops such as alfalfa and sainfoin, because water flow can stop in July.",
            "claim_type": "finding",
            "concept": D("winters with little snow; irrigation water flow; cultivation choices", "explicit"),
            "relation_or_direction": D("shift to early ripening, less water-needy fodder plants", "explicit"),
            "geography": D(
                "municipality of Porshnev, Western Pamirs",
                "explicit",
                E("results", "In the municipality of Porshnev, cultivation patterns based on continuous weather observation and local environmental knowledge are widely applied."),
            ),
            "temporal_frame": D("after winters with little snow", "explicit"),
            "scenario": UNKNOWN,
            "evidence": E("results", "After winters with little snow, mainly early ripening and less water-needy fodder plants such as alfalfa and sainfoin are cultivated as sufficient water flow can already stop in July."),
            "notes": None,
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("discussion", "The broad involvement of the community in irrigation water management and the system's adaptability appear to be pivotal factors for its sustainability and resilience to the challenging socio-ecological conditions of the region."),
            "reason": "The author's interpretive assessment of governance ('appear to be'); not a hazard claim.",
        },
        {
            "evidence": E(_SITES_571, "However, a humid climate can be excluded"),
            "reason": "Qualitative statement about Shirgin, where the paper says no fact-based statement can be made about the precipitation regime; ambiguous.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "Scope is borderline (see scope_reason). Several fields repeat whole passages; spans use the first occurrence. The abstract field contains journal page fragments ('Water 2020, 12, 2905'), not recorded as bibliographic fields.",
}

# ---------------------------------------------------------------------------
ITEMS["LIT-000761"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "ambiguous",
    "scope_reason": (
        "One year of eddy-covariance measurements of water-use efficiency in a riparian forest of "
        "a permanently arid region; drought appears as the background condition and in cited "
        "statements, but the paper does not examine a hazard event or its impacts."
    ),
    "scope_evidence": E("abstract", "explored the main controlling factors of WUE in drought-stressed environment based on the synchronous meteorological data"),
    "claims": [],
    "rejected_or_ambiguous": [
        {
            "evidence": E("abstract", "Under the conditions of high temperature, strong radiation and low humidity in the summer, the growth rate of ET was much larger than that of GPP."),
            "reason": "Seasonal ecosystem physiology under ordinary summer conditions of the site; not framed as a hazard.",
        },
        {
            "evidence": E("results", "Figure 9(c) showed that WUE increased as SWC decreased."),
            "reason": "The abstract states the soil-water relation differently ('WUE increased under moderate soil water content (SWC), but decreased due to the continuously rising SWC'); the direction is ambiguous, and it is not a hazard claim.",
        },
        {
            "evidence": E("discussion", "because long-term drought enhanced the ecosystem's resistance and resilience to water scarcity in order to mitigate the effects of water loss (Gang et al. 2016)"),
            "reason": "An explanation borrowed from a cited source, not tested in this paper.",
        },
    ],
    "terminal_status": "ambiguous_only",
}

# ---------------------------------------------------------------------------
ITEMS["LIT-000951"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "off_topic",
    "scope_reason": (
        "A Bayesian geostatistical method for predicting annual runoff; floods are mentioned once "
        "as motivation, and no hazard or impact is examined."
    ),
    "scope_evidence": E("abstract", "We estimate annual runoff by using a Bayesian geostatistical model for interpolation of hydrological data of different spatial support"),
    "claims": [],
    "rejected_or_ambiguous": [
        {
            "evidence": E("introduction", "This makes Voss flood exposed, and accurate runoff models are of high importance."),
            "reason": "Motivation only; the paper models annual runoff, not floods.",
        },
    ],
    "terminal_status": "off_topic",
    "notes": "The abstract field ends with a keyword list and an author running head ('ROKSVÅG et al.'); not recorded as bibliographic fields.",
}

# ---------------------------------------------------------------------------
_GEO_1141 = D(
    "Bangalore city, India",
    "explicit",
    E("introduction", "The present study aims to assess the impacts of Bangalore city's urbanization over 20 years"),
)
_TIME_1141 = D(
    "April months, 2001 to 2021",
    "explicit",
    E("introduction", "during the April months from 2001 to 2021"),
)
_RD_1141 = "results and discussion"
ITEMS["LIT-001141"] = {
    "bibliographic": {
        "title": ("$.abstract", "Understanding the Linkage between Urban Growth and Land Surface Temperature-A Case Study of Bangalore City, India"),
        "authors": ("$.abstract", "Kanga, S.; Meraj, G.; Johnson, B.A.; Singh, S.K.; PV, M.N.; Farooq, M.; Kumar, P.; Marazi, A.; Sahu, N."),
        "year": ("$.abstract", "2022"),
        "venue": ("$.abstract", "Remote Sens."),
        "note": "No title key exists. The abstract field holds a citation string, not an abstract; bibliographic fields are taken from it.",
    },
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper examines urban heat island (UHI) events - the hottest April land surface "
        "temperatures - and their intensification with urban growth in Bangalore."
    ),
    "scope_evidence": E("introduction", "This study particularly focuses on the relationship between urban growth and UHI events during the April months from 2001 to 2021."),
    "claims": [
        {
            "claim_text": "During April UHI events, land surface temperature in Bangalore's urban areas rose about 0.34 °C per year between 2001 and 2021, versus 0.14 °C per year in non-urban areas.",
            "claim_type": "finding",
            "concept": D("land surface temperature during UHI events", "explicit"),
            "relation_or_direction": D("increased about 0.34 °C per year (urban) vs 0.14 °C per year (non-urban)", "explicit"),
            "geography": D("urban settlement areas of Bangalore", "explicit"),
            "temporal_frame": D("UHI events of April, 2001 and 2021", "explicit"),
            "scenario": UNKNOWN,
            "evidence": E("conclusion", "We further found land surface temperature, on average, increased by about 0.34 • C per year in urban settlement areas of Bangalore during the UHI events of April 2001 and 2021, in contrast to 0.14 • C per year in non-urban areas."),
            "notes": "The results section reports a different modelled rate (0.247 vs 0.056 °C per year, claim C2). Both are recorded as stated; the paper does not reconcile them.",
        },
        {
            "claim_text": "A mixed-effects model of April UHI-event land surface temperature gave an increasing trend of 0.247 °C per year at urban sites versus 0.056 °C per year at non-urbanized sites.",
            "claim_type": "finding",
            "concept": D("mean-modeled land surface temperature (LST)", "explicit"),
            "relation_or_direction": D("increasing trend, slope 0.247 °C per year vs 0.056 °C per year in non-urbanized areas", "explicit"),
            "geography": _GEO_1141,
            "temporal_frame": _TIME_1141,
            "scenario": UNKNOWN,
            "evidence": E(_RD_1141, "It was observed that the mean-modeled LST as a function of the above parameters shows an increasing trend with a slope of 0.247 • C per year in contrast to 0.056 • C per year in non-urbanized areas."),
            "notes": "Differs from the conclusion's 0.34 vs 0.14 °C per year (C1).",
        },
        {
            "claim_text": "Comparing three April UHI events, their intensity in the same month increased by 3.25 °C from 2001 to 2021.",
            "claim_type": "finding",
            "concept": D("UHI temperature events", "explicit"),
            "relation_or_direction": D("increased in intensity (3.25 °C)", "explicit"),
            "geography": _GEO_1141,
            "temporal_frame": D("2001 to 2021, same month (April)", "explicit"),
            "scenario": UNKNOWN,
            "evidence": E(_RD_1141, "Based on the comparison of three UHI temperature events, we observed that such events over the years in the same month have increased in intensity (3.25 • C from 2001 to 2021)."),
            "notes": None,
        },
        {
            "claim_text": "The annual average MODIS temperature for 2001, 2011 and 2021 showed no significant change, which is why the hottest month was analysed.",
            "claim_type": "finding",
            "concept": D("annual average temperature of MODIS", "explicit"),
            "relation_or_direction": D("did not show any significant changes", "explicit"),
            "geography": _GEO_1141,
            "temporal_frame": D("2001, 2011, and 2021", "explicit"),
            "scenario": UNKNOWN,
            "evidence": E(_RD_1141, "Here, it is also notable to mention that the annual average temperature of MODIS for 2001, 2011, and 2021 did not show any significant changes."),
            "notes": "Qualifies C1-C3: the reported increases are for the hottest-month events, not annual means.",
        },
        {
            "claim_text": "The authors attribute the temperature increase to increasing built-up area and decreasing vegetation.",
            "claim_type": "mechanism",
            "concept": D("increase in the temperature; increasing built-up and decreasing vegetation", "explicit"),
            "relation_or_direction": D("could be well-attributed to (hedged)", "explicit"),
            "geography": _GEO_1141,
            "temporal_frame": _TIME_1141,
            "scenario": UNKNOWN,
            "evidence": E(_RD_1141, "The increase in the temperature as such could be well-attributed to the increasing built-up and decreasing vegetation, as indicated in Figure 3."),
            "notes": None,
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E(_RD_1141, "This findings of this study, carried out in Bangalore city of Karnataka state of India, depict the same story of every city of India."),
            "reason": "Generalization beyond the study's evidence (one city).",
        },
        {
            "evidence": E("conclusion", "In 20 years, we found that built-up increased by 87.62%. Vegetation and water bodies decreased by 40% and 30%, respectively."),
            "reason": "A valid land-cover finding, not promoted: land-cover statistic rather than a hazard claim, and the five-claim cap.",
        },
        {
            "evidence": E(_RD_1141, "However, it must be noted that the results presented in this work related to LST change are event-based, and the actual observation might not be so worrisome."),
            "reason": "The authors' own caveat on C1-C3; kept for audit.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "Several passages in the results field are repeated; spans use the first occurrence.",
}

# ---------------------------------------------------------------------------
ITEMS["LIT-001331"] = {
    "bibliographic": {
        "title": "$.title",
        "note": "The title field holds 'HTS Teologiese Studies/Theological Studies', which reads as a journal name. Recorded as the field says; not corrected.",
    },
    "scope_status": "off_topic",
    "scope_reason": (
        "A theological essay on the human appreciation of nature's beauty; the climate crisis is "
        "framing, and no climate or weather hazard or impact is examined."
    ),
    "scope_evidence": E("abstract", "This article offers a hopeful conversation in the current climate catastrophe that implores humans to recover their ancient love of, and interdependence with, the beauty of the natural world."),
    "claims": [],
    "rejected_or_ambiguous": [
        {
            "evidence": E("jonathan edwards' ecotheology posits the human appreciation of nature's beauty as a divine communication of grace", "We are witnessing right before us climate instability, pollution, habitat destruction, species loss and the exhaustion of natural resources."),
            "reason": "Rhetorical statement without evidence in the paper. Paper is off_topic.",
        },
    ],
    "terminal_status": "off_topic",
}

# ---------------------------------------------------------------------------
_TIME_1521 = D(
    "16 weeks of exposure (2 h/d, 5 d/wk)",
    "explicit",
    E("experimental design", "for 2 h/d, 5 d/wk, for 16 wk"),
)
_CONCEPT_1521 = "exposure to laboratory-generated (simulated) wildfire smoke at an occupationally relevant dose"
ITEMS["LIT-001521"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper measures health-relevant effects of exposure to (laboratory-generated) wildfire "
        "smoke, an impact pathway of wildfire."
    ),
    "scope_evidence": E("abstract", "Here, we sought to address this by using RNA sequencing to examine transcriptomic signatures in the prefrontal cortex of male mice modeling career wildland firefighter smoke exposure."),
    "claims": [
        {
            "claim_text": "Chronic exposure to simulated wildfire smoke produced robust gene expression changes in the prefrontal cortex of male mice: 2,862 differentially expressed genes versus filtered-air controls.",
            "claim_type": "finding",
            "concept": D(_CONCEPT_1521, "explicit", E("title", "exposed to an occupationally relevant dose of laboratory-generated wildfire smoke")),
            "relation_or_direction": D("robust changes; 2,862 differentially expressed genes (51.2% increased)", "explicit"),
            "geography": UNKNOWN,
            "temporal_frame": _TIME_1521,
            "scenario": UNKNOWN,
            "evidence": E("abstract", "We report robust changes in gene expression profiles between smoke-exposed samples and filtered air controls, evidenced by 2,862 differentially expressed genes (51.2% increased)."),
            "notes": "The split between increased and decreased genes is stated inconsistently in the paper (see rejected_or_ambiguous); only the total is used in claim_text.",
        },
        {
            "claim_text": "The smoke-altered genes were enriched in pathways related to synaptic transmission, neuroplasticity, blood-brain barrier integrity and neurotransmitter metabolism.",
            "claim_type": "finding",
            "concept": D("differentially expressed genes; enriched pathways", "explicit"),
            "relation_or_direction": D("enriched in synaptic transmission, neuroplasticity, blood-brain barrier integrity, neurotransmitter metabolism pathways", "explicit"),
            "geography": UNKNOWN,
            "temporal_frame": _TIME_1521,
            "scenario": UNKNOWN,
            "evidence": E("abstract", "We further characterized the functional relevance of these genes highlighting enriched pathways related to synaptic transmission, neuroplasticity, blood-brain barrier integrity, and neurotransmitter metabolism."),
            "notes": None,
        },
        {
            "claim_text": "Contrary to expectation from prior smoke studies, the primary analyses showed no significant alterations in canonical neuroinflammatory pathways.",
            "claim_type": "finding",
            "concept": D("canonical neuroinflammatory pathways", "explicit"),
            "relation_or_direction": D("no significant alterations ('did not appear')", "explicit"),
            "geography": UNKNOWN,
            "temporal_frame": _TIME_1521,
            "scenario": UNKNOWN,
            "evidence": E("discussion", "Interestingly, there did not appear to be significant alterations in canonical neuroinflammatory pathways in our primary analyses."),
            "notes": None,
        },
        {
            "claim_text": "Wildfires have become common worldwide alongside warmer, drier climates and are now major contributors to ambient air pollution.",
            "claim_type": "background_citation",
            "concept": D("wildfires; ambient air pollution", "explicit"),
            "relation_or_direction": D("have become common, concurrent with warmer and drier climates; major contributors to air pollution", "explicit"),
            "geography": D("global / worldwide", "explicit"),
            "temporal_frame": D("present ('now')", "explicit"),
            "scenario": UNKNOWN,
            "evidence": E("abstract", "Wildfires have become common global phenomena concurrent with warmer and drier climates and are now major contributors to ambient air pollution worldwide."),
            "notes": "Background framing; not a finding of this paper.",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("overall transcriptional profile of wildfire smokeexposed and filtered air control samples", "genes/transcripts increased and 1,466 decreased in wildfire smoke-exposed samples compared with filtered air controls"),
            "reason": "The results text gives 1,396 increased and 1,466 decreased; the figure caption gives the reverse, and the abstract's '51.2% increased' matches 1,466 increased. The direction of the split is ambiguous.",
        },
        {
            "evidence": E("discussion", "In our present dataset, the transcriptomic profile is highly similar to those previously identified in AD"),
            "reason": "Interpretive comparison with other datasets; not promoted.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "Laboratory smoke, not an observed wildfire; the concept is recorded as the paper names it. The results field contains a journal page header ('Toxicological Sciences, 2024, Vol 201, Issue 2'), not recorded as a bibliographic field.",
}

# ---------------------------------------------------------------------------
_GEO_1711 = D(
    "Fortescue Marsh floodplain, upper Fortescue River catchment, semi-arid northwest Australia",
    "explicit",
    E("abstract", "the Fortescue Marsh, the largest water feature of inland northwest Australia"),
)
_CENTURY_1711 = D(
    "last century (reconstruction since 1912)",
    "explicit",
    E("abstract", "reconstruct monthly history of floods and droughts since 1912"),
)
ITEMS["LIT-001711"] = {
    "bibliographic": {
        "title": "$.title",
        "note": "The title field holds 'Discussion Paper | Discussion Paper | ...', a page-header artifact rather than a title. Recorded as the field says; not corrected.",
    },
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper reconstructs a century of floods and droughts of an arid-zone wetland and "
        "relates them to extreme rainfall."
    ),
    "scope_evidence": E("abstract", "Here, we sought to identify the main hydroclimatic determinants of the strongly episodic flood regime of a large catchment in the semi-arid, subtropical northwest of Australia"),
    "claims": [
        {
            "claim_text": "Severe, intense regional rainfall events and the sequence of recharge events within and between years determine surface water extent on the Fortescue Marsh floodplain.",
            "claim_type": "finding",
            "concept": D("severe and intense regional rainfall events; sequence of recharge events; surface water expression", "explicit"),
            "relation_or_direction": D("determine", "explicit"),
            "geography": _GEO_1711,
            "temporal_frame": D("model calibrated on 1988-2012 satellite observations", "explicit", E("abstract", "from 1988 to 2012")),
            "scenario": UNKNOWN,
            "evidence": E("abstract", "We found that severe and intense regional rainfall events, as well as the sequence of recharge events both within and between years, determine surface water expression on the floodplain"),
            "notes": None,
        },
        {
            "claim_text": "The most severe inundation of the last century on the Fortescue Marsh, about 1000 km2, was recorded in 2000.",
            "claim_type": "finding",
            "concept": D("inundation", "explicit"),
            "relation_or_direction": D("most severe (~1000 km2) in 2000", "explicit"),
            "geography": _GEO_1711,
            "temporal_frame": _CENTURY_1711,
            "scenario": UNKNOWN,
            "evidence": E("abstract", "The most severe inundation (∼ 1000 km 2 ) over the last century was recorded in 2000."),
            "notes": None,
        },
        {
            "claim_text": "Between 1999 and 2006, the duration, severity and frequency of inundations were above average and unprecedented relative to the last century.",
            "claim_type": "finding",
            "concept": D("duration, severity and frequency of inundations", "explicit"),
            "relation_or_direction": D("above average and unprecedented", "explicit"),
            "geography": _GEO_1711,
            "temporal_frame": D("1999-2006, compared with the last century", "explicit"),
            "scenario": UNKNOWN,
            "evidence": E("abstract", "Duration, severity and frequency of inundations between 1999 and 2006 were above average and unprecedented when compared to the last century."),
            "notes": None,
        },
        {
            "claim_text": "The authors suggest the wetland will become more persistent as extreme rainfall events in the region become more frequent and intense.",
            "claim_type": "projection",
            "concept": D("wetland persistence; frequency and intensity of extreme rainfall events", "explicit"),
            "relation_or_direction": D("will become more persistent (hedged: 'suggest')", "explicit"),
            "geography": _GEO_1711,
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "evidence": E("abstract", "changes to the flooding regime over the last 20 years suggest that the wetland will become more persistent in response to increased frequency and intensity of extreme rainfall events for the region"),
            "notes": "The basis is changes over the last 20 years; no future horizon and no scenario are stated, so both are unknown.",
        },
        {
            "claim_text": "Extended droughts with no surface water on the Marsh were more frequent from the late 1930s to the early 1960s; the longest lasted 4.3 years, 1961-1965.",
            "claim_type": "finding",
            "concept": D("extended drought periods (no surface water evident)", "explicit"),
            "relation_or_direction": D("more frequent late 1930s-early 1960s; longest 4.3 years", "explicit"),
            "geography": _GEO_1711,
            "temporal_frame": D("late 1930s to early 1960s; 1961-1965", "explicit"),
            "scenario": UNKNOWN,
            "evidence": E("results and discussion", "particularly extended drought periods (where no surface water is evident on the Marsh) were more frequent between the late 1930's and early 1960's, with the longest supraseasonal drought on record lasting 4.3 years (between 1961 and 1965)"),
            "notes": None,
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("abstract", "The Fortescue Marsh was completely dry for 32 % of all years, for periods of up to four consecutive years."),
            "reason": "Hard to reconcile with the results ('68 % of years ended with no surface water'; the longest drought 4.3 years); which quantity is meant is ambiguous.",
        },
        {
            "evidence": E("introduction", "Extreme climatic events such as tropical cyclones, heavy rainfall and severe drought are projected to become more intense and less frequent globally over the next hundred years in response to anthropogenic-driven climate change (Coumou and Rahmstorf, 2012)."),
            "reason": "Background statement attributed to another source; not this paper's evidence.",
        },
        {
            "evidence": E("conclusion", "if current rainfall trends are sustained, increased flooding of the Fortescue Marsh will prolong the inundation period in the year"),
            "reason": "Conditional projection overlapping claim C4; not promoted.",
        },
    ],
    "terminal_status": "claims_extracted",
}
