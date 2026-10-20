"""M4-WP4r1 Phase B: reader 1's reading of the twenty sampled LITCORPUS-02 papers, as data.

**Manual reading by the EXECUTOR as reader 1** (Claude Code, model
claude-opus-5-5), 2026-10-19. Every sampled file was verified against the
frozen sample hashes (`scripts/wp4_verify_sample.py`) before it was decoded,
then read completely, key by key, from its decoded JSON. No LLM API call, no
model service, no embedding, no search over any other corpus file. **The
term-hit files (`hits.csv`), the place-candidate hit locations, the ClimRR
prototypes and the pilot-family documents were not opened before this file was
complete**; the hit classification is a separate, later step
(`scripts/wp4_hit_classification.py`).

The rubric is the M4-WP1/WP2 rubric, unchanged (see `scripts/wp1_extractions.py`):

* `explicit` --- the paper says it, in the claim's own span or the quoted
  `support` span; `inferred` --- the reader linked it, and the `support` span the
  link rests on is quoted; `unknown` --- the paper does not state it for this
  claim, and the value is the string `unknown`. Nothing from general knowledge,
  filenames, the query, the place terms or the prototypes.
* `scenario` is an emissions or climate scenario only; experimental or
  laboratory treatment levels go in `experimental_condition` (D-017).
* Scope: `in_scope_hazard` --- the paper itself discusses a climate or weather
  hazard or its impacts, judged from its own text; `off_topic` --- it does not;
  `ambiguous` --- hazard language is present but the paper does not examine a
  hazard or its impacts. Claims only for `in_scope_hazard`.
* `geography` holds the place exactly as the paper states it; the role the
  place plays for that claim is recorded beside it under `role` (M4-WP4r1).

**Every quoted span is exact text of the decoded source string**; the builder
locates it by exact search (first occurrence unless `occurrence` is given),
re-slices the source and fails on any difference. No offset is written here by
hand.
"""

from __future__ import annotations

from climrr.litingest import child_path

EXTRACTION_METHOD = (
    "manual reading by the EXECUTOR as reader 1 (Claude Code, model claude-opus-5-5); "
    "every sampled file verified by SHA-256, then read completely; no LLM API call, no "
    "model service, no embedding, no search over other corpus files; no term-hit file, "
    "place-hit location, prototype or pilot-family document consulted before the reading "
    "was complete"
)
EXTRACTION_DATE = "2026-10-19"

PRIOR_EXPOSURE = {
    "LIT2-001075": "LIT-001536 read in M4-WP2; WP2 artifacts not consulted",
}


def K(key: str) -> str:
    """JSON path of a top-level key."""
    return child_path("$", key)


def E(key: str, text: str, occurrence: int = 1) -> dict:
    """An evidence span: exact text in the string at top-level `key`."""
    return {"json_path": K(key), "text": text, "occurrence": occurrence}


def D(value: str, status: str, support: dict | None = None) -> dict:
    return {"value": value, "status": status, "support": support}


def G(value: str, status: str, role: str, support: dict | None = None) -> dict:
    """A geography dimension: the place as stated, and the role it plays for the claim."""
    return {"value": value, "status": status, "support": support, "role": role}


UNKNOWN = {"value": "unknown", "status": "unknown", "support": None}
GEO_UNKNOWN = {"value": "unknown", "status": "unknown", "support": None, "role": "unknown"}


ITEMS: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# LIT2-000185 (208499235) --- fire_weather_v1 rank 10
ITEMS["LIT2-000185"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "A data-descriptor paper presenting a global database of individual wildfire events "
        "derived from MODIS burnt area, framed by wildfire damage and changing fire regimes, "
        "with comparisons against regional fire records."
    ),
    "scope_evidence": E("background & summary", "Wildfires are an important phenomenon at the global scale, as they are responsible for large amounts of economic and environmental damage."),
    "claims": [
        {
            "claim_text": "All of the biggest fires reported by CALFIRE from 2001 to 2017 were found in the GlobFire database, which also reports some additional big fires, with considerably different total burnt area per fire.",
            "claim_type": "finding",
            "concept": D("large fires; total burnt area of each fire (GlobFire versus CALFIRE)", "explicit"),
            "relation_or_direction": D("all found in GlobFire; additional big fires; burnt area considerably different", "explicit"),
            "geography": G("California", "explicit", "comparison / validation area for the database",
                           E("statistical analysis", "Table 2 shows a comparison of large fires in California using the GlobFire database and the top 20 largest wildfires of CALFIRE")),
            "temporal_frame": D("2001 to 2017", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("statistical analysis", "All the biggest fires reported by CALFIRE from 2001 to 2017 were found in the GlobFire database. However, the GlobFire database also reports some additional big fires and the total burnt area of each fire is considerably different."),
            "notes": None,
        },
        {
            "claim_text": "For Portugal, the magnitude of burnt area agrees strongly across the three sources compared (GlobFire, EFFIS remote sensing and national reports).",
            "claim_type": "finding",
            "concept": D("magnitude of the burnt area", "explicit"),
            "relation_or_direction": D("agreement of the three different sources is strong", "explicit"),
            "geography": G("Portugal", "explicit", "comparison / validation area for the database",
                           E("statistical analysis", "Considering the magnitude of the burnt area in Portugal, the agreement of the three different sources is strong.")),
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("statistical analysis", "Considering the magnitude of the burnt area in Portugal, the agreement of the three different sources is strong."),
            "notes": "The three sources are named earlier in the same field (GlobFire, EFFIS's MODIS-based database and the country reports).",
        },
        {
            "claim_text": "In Portugal the number of fires is considerably higher in the north, but the average fire size is much higher in the central area, so fires are on average bigger in the centre.",
            "claim_type": "finding",
            "concept": D("number of fires; average fire size", "explicit"),
            "relation_or_direction": D("number higher in the north; average size much higher in the central area", "explicit"),
            "geography": G("Portugal (north versus central area of the country)", "explicit", "example region of the global database's regional summary"),
            "temporal_frame": D("2001 to 2017 (the period of the regional summary)", "inferred",
                                E("statistical analysis", "The GlobFire database has been used to determine the number of fires, the average fire size and the maximum fire spread speed for each administrative 3rd level region from 2001 to 2017.")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("statistical analysis", "For instance, focusing on Portugal, the number of fires is considerable higher in the north of the country. However, the average fire size is much higher in the central area of Portugal."),
            "notes": None,
        },
        {
            "claim_text": "The fastest maximum fire spread speeds are found in south Spain, the Peloponnese and central Portugal within Europe, and globally in Santa Isabel, Malheur, Tableland, Halhgol, Chernozermel'skiy rayon and Tanganika.",
            "claim_type": "finding",
            "concept": D("maximum fire spread speed", "explicit"),
            "relation_or_direction": D("fastest moving fires occur in the named regions", "explicit"),
            "geography": G("south of Spain, the Peloponnese (Greece), central Portugal; Santa Isabel (Argentina), Malheur (USA), Tableland (Australia), Halhgol (Mongolia), Chernozermel'skiy rayon (Russia), the Republic of Tanganika", "explicit", "regions named as results of the global regional summary"),
            "temporal_frame": D("2001 to 2017 (the period of the regional summary)", "inferred",
                                E("statistical analysis", "The GlobFire database has been used to determine the number of fires, the average fire size and the maximum fire spread speed for each administrative 3rd level region from 2001 to 2017.")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("statistical analysis", "In Europe, the fastest moving fires occur in south of Spain (b), in the Peloponnese (Greece, annotation c) and specially in central Portugal (b)."),
            "notes": "The global list is in the following sentence of the same field: 'From the global perspective, Santa Isabel (Argentina, annotation f), Malheur (USA, annotation a), ...'.",
        },
        {
            "claim_text": "Fire danger indicators such as the Canadian Fire Weather Index have recently shown the highest values of the last 37 years in many European countries.",
            "claim_type": "background_citation",
            "concept": D("fire danger indicators such as the Canadian Fire Weather Index (FWI)", "explicit"),
            "relation_or_direction": D("highest values registered during the last 37 years", "explicit"),
            "geography": G("many European countries", "explicit", "background context"),
            "temporal_frame": D("recently; the last 37 years", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("background & summary", "Recently, fire danger indicators such as the Canadian Fire Weather Index (FWI) 3 have shown the highest values registered during the last 37 years in many European countries."),
            "notes": "Attributed to reference 3; background, not this paper's analysis.",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("background & summary", "Wildfire regimes are changing, wildfire seasons are becoming longer 1 , wildfire average sizes are increasing in many areas of the world and wildfires are happening in areas in which they did not occur in the past."),
            "reason": "General background with citations and no stated geography or period; not this paper's evidence.",
        },
        {
            "evidence": E("statistical analysis", "Recently, several works [35][36][37][38][39] establish the links between climate change and fires."),
            "reason": "A pointer to other works; no content of its own.",
        },
        {
            "evidence": E("statistical analysis", "Therefore, GlobFire is suitable for querying data about extreme fires in California."),
            "reason": "A usage recommendation drawn from claim C1, not a separate finding.",
        },
    ],
    "terminal_status": "claims_extracted",
}

# ---------------------------------------------------------------------------
# LIT2-000366 (229495849) --- fire_weather_v1 rank 20
_GEO_366 = G(
    "Montesinho nature park in Portugal", "inferred", "area of the forest fire data set used for testing",
    E("experiments and results", "The data set records the forest fire occurrence in Montesinho nature park in Portugal for three years"),
)
_TIME_366 = D(
    "three years (the period of the data set; years not stated)", "inferred",
    E("experiments and results", "The data set records the forest fire occurrence in Montesinho nature park in Portugal for three years"),
)
ITEMS["LIT2-000366"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper builds and tests a machine-learning framework that predicts forest fire "
        "occurrence from meteorological data, i.e. prediction of a weather-driven hazard."
    ),
    "scope_evidence": E("conclusion", "This framework can effectively predict the occurrence of forest fires based on meteorological data, and has good regional adaptability and good application prospects."),
    "claims": [
        {
            "claim_text": "The optimized automatic machine learning framework improves forest fire prediction accuracy by 13% on average across test sets compared with the unimproved framework.",
            "claim_type": "finding",
            "concept": D("forest fire risk prediction accuracy of an optimized auto-sklearn framework", "explicit"),
            "relation_or_direction": D("improved by 13% on average", "explicit"),
            "geography": _GEO_366,
            "temporal_frame": _TIME_366,
            "scenario": UNKNOWN,
            "experimental_condition": D(
                "binary classification of a discretized forest fire data set; training/test split 3:2; regional samples from unsupervised clustering of location",
                "explicit",
                E("experiments and results", "In the process of data preprocessing, we discretize the labels and transform the regression problem into a binary classification problem."),
            ),
            "evidence": E("abstract", "The comparative analysis results show that the prediction accuracy of the improved framework in different test sets is improved by 13% on average."),
            "notes": "A methods / model-performance finding; the hazard enters only as the prediction target.",
        },
        {
            "claim_text": "On the forest fire data set, the optimized framework's classification accuracy is not lower than that of general classifiers (SVM, random forest), and it shows natural regional adaptability.",
            "claim_type": "finding",
            "concept": D("classification accuracy of the optimized framework versus general classifiers", "explicit"),
            "relation_or_direction": D("not lower than existing models; natural regional adaptability", "explicit"),
            "geography": _GEO_366,
            "temporal_frame": _TIME_366,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("experiments and results", "Compared with the accuracy of general classifiers, the classification accuracy of the optimized automatic machine learning framework is not lower than that of the existing model, and has natural regional adaptability."),
            "notes": None,
        },
        {
            "claim_text": "Canada's forest fire weather index system calculates the FWI from temperature, humidity and wind speed; the United States, New Zealand and others built fire danger forecast systems on its ideas.",
            "claim_type": "background_citation",
            "concept": D("the Canada's forest fire weather index system; forest fire whether index(FWI)", "explicit"),
            "relation_or_direction": D("calculated from temperature, humidity and wind speed; adopted as the basis of other national systems", "explicit"),
            "geography": G("Canada; The United States, New Zealand and some others", "explicit", "background context (where the systems are used)"),
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("introduction", "It calculates the forest fire whether index(FWI) based on features such as temperature, humidity and wind speed."),
            "notes": "'whether' is the source's spelling; kept exactly. Background description, not this paper's analysis; no citation is given for it.",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("introduction", "Among many factors that may cause forest fires, weather and climate conditions have always been considered as the most important influencing factors."),
            "reason": "General background assertion without evidence in this paper.",
        },
        {
            "evidence": E("conclusion", "This framework also performs well on other binary imbalanced data sets, and has certain application potential in related fields."),
            "reason": "Concerns non-fire data sets; not about a hazard.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "The data set is described as 'provided by the University of California at Irvine' (data provider), separate from the study area.",
}

# ---------------------------------------------------------------------------
# LIT2-000499 (238725720) --- fire_weather_v1 rank 30
_GEO_499 = G(
    "540 houses exposed to two fires (Linksview and Mt York) in the Blue Mountains of NSW", "explicit",
    "study area (where the houses and fires were observed)",
    E("method the study area and fires", "Our study focused on 540 houses exposed to two fires in the Blue Mountains of NSW in October 2013"),
)
_TIME_499 = D(
    "October 2013 (fires of 17 October 2013)", "explicit",
    E("method the study area and fires", "Our study focused on 540 houses exposed to two fires in the Blue Mountains of NSW in October 2013"),
)
ITEMS["LIT2-000499"] = {
    "bibliographic": {
        "title": "$.title",
        "authors": ("$.abstract", "Price, O.F.; Whittaker, J.; Gibbons, P.; Bradstock, R."),
        "note": "`abstract` holds a truncated citation string, not an abstract; authors recovered from it. Year and venue are not stated in any field (the title's '2013' is the fire year).",
    },
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper analyses which factors determined damage to houses exposed to two wildfires, "
        "i.e. the impacts of a fire hazard on buildings, including the role of fire weather."
    ),
    "scope_evidence": E("introduction", "In this study, we examined the impact on houses from two fires from the Blue Mountains (New South Wales, Australia) in October 2013, using Random Forest modelling to disentangle the independent effects of risk factors from all six themes on fire impact."),
    "claims": [
        {
            "claim_text": "House defence was the most important variable for whether a house was impacted: 14.7% of defended houses were impacted compared with 42.4% of undefended houses.",
            "claim_type": "finding",
            "concept": D("defence of the house; likelihood a house would be impacted", "explicit"),
            "relation_or_direction": D("most important variable; defended 14.7% impacted versus undefended 42.4%", "explicit"),
            "geography": _GEO_499,
            "temporal_frame": _TIME_499,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "The proportion of defended houses that were impacted was 14.7% compared to 42.4% for undefended houses."),
            "notes": "The ranking is stated in the preceding sentence: 'The Random Forest analysis identified defence as the most important variable affecting the likelihood a house would be impacted'.",
        },
        {
            "claim_text": "Westerly distance to forest up to about 50 m had a strong negative relationship with house impact; forest cover beyond 50 m in that direction did not influence impact.",
            "claim_type": "finding",
            "concept": D("westerly distance to forest; house impact", "explicit"),
            "relation_or_direction": D("strong negative relationship up to about 50 m; no influence beyond 50 m", "explicit"),
            "geography": _GEO_499,
            "temporal_frame": _TIME_499,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "Westerly distance to forest up to about 50 m distance from houses had a strong negative relationship on house impact. Forest cover beyond 50 m in this direction did not influence impact."),
            "notes": None,
        },
        {
            "claim_text": "Weather had only a minor role in which houses were impacted: FFDI ranked 20th in the Random Forest model, although impact was twice as high at FFDI 75 as at 34 (38% versus 19%).",
            "claim_type": "finding",
            "concept": D("weather; Forest Fire Danger Index (FFDI); house impact", "explicit"),
            "relation_or_direction": D("minor role; impact 38% at FFDI 75 versus 19% at 34", "explicit"),
            "geography": _GEO_499,
            "temporal_frame": _TIME_499,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("weather", "Weather only had a minor role in determining which houses were impacted (Figure 5i), with FFDI being the 20th most important variable in the Random Forest model."),
            "notes": "The 38% versus 19% figures are in the same field: 'While house impact was twice the rate at FFDI 75 than at 34 (38% impacted compared to 19%)'. The paper suggests the muted role may reflect a fire-weather range that was 'quite low'.",
        },
        {
            "claim_text": "In the worst-case situation defined by the model (forest under 10 m to the west, undefended, facing west-south-west, dense vegetation), 71% of houses were impacted, versus 3% in the best case.",
            "claim_type": "finding",
            "concept": D("worst-case and best-case house situations; house impact", "explicit"),
            "relation_or_direction": D("71% impacted in the worst case versus 3% in the best case", "explicit"),
            "geography": _GEO_499,
            "temporal_frame": _TIME_499,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "The impact on houses in the worst-case situation, as defined by the Random Forest model, was 71%."),
            "notes": "The best-case figure is in the same field: 'By contrast, only 3% of the 31 houses in the best-case situation were impacted.'",
        },
        {
            "claim_text": "Preparedness actions and response actions were the most important themes for house impact, more important than house construction, landscape fuels, topography and weather.",
            "claim_type": "finding",
            "concept": D("preparedness actions; response actions; house impact themes", "explicit"),
            "relation_or_direction": D("most important themes; more important than the other four", "explicit"),
            "geography": G("houses exposed to destructive fires in south-eastern Australia", "explicit", "study area (as summarised in the conclusion)",
                           E("conclusion", "This analysis of houses exposed to destructive fires in south-eastern Australia")),
            "temporal_frame": _TIME_499,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("conclusion", "We found that preparedness actions and response actions were the most important themes (i.e., more important than house construction, landscape fuels, topography and weather)."),
            "notes": None,
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("introduction", "For example, in 2017, 7500 houses were destroyed in California [1], and 500 in Portugal [2], while Australia experienced its worst event in 2019/20 (3113 houses lost [3])."),
            "reason": "Background figures attributed to other sources; not this paper's evidence. Also beyond the five-claim cap.",
        },
        {
            "evidence": E("introduction", "Fire weather indices such as the Australian Forest Fire Danger Index [41], the Canadian Fire Weather Index [42] and the US Fosberg Fire Weather Index [43] all contain components describing temperature, humidity and wind speed."),
            "reason": "Background description of indices with citations; the paper's own analysis uses FFDI only. Not promoted (five-claim cap; background).",
        },
        {
            "evidence": E("introduction", "Weather is a natural feature that no human agents can control, although climate change is driven by human activity and in the long term, may increase the severity of fire weather [16]."),
            "reason": "Hedged background statement ('may') attributed to a reference; no horizon, scenario or place.",
        },
        {
            "evidence": E("defensive action", "Indeed, defence may become more dangerous as the fire weather becomes more severe [59]."),
            "reason": "Hedged statement attributed to a reference; not tested here.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "Several fields repeat whole passages (an extraction artifact); spans use the first occurrence.",
}

# ---------------------------------------------------------------------------
# LIT2-000560 (244714495) --- fire_weather_v1 rank 40
ITEMS["LIT2-000560"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper builds and evaluates a deep-learning model that predicts future wildfire "
        "burn area from historical fire and climate data, i.e. prediction of a hazard."
    ),
    "scope_evidence": E("abstract", "In this paper, we create a dynamic model for future wildfire predictions of five locations within the western United States through a deep neural network via historical burned area and climate data."),
    "claims": [
        {
            "claim_text": "On temporally held-out validation data, the proposed dynamic auto-encoder outperformed the alternative models in binary cross-entropy loss for Salt Lake City, Portland and Medford, but not in AUROC.",
            "claim_type": "finding",
            "concept": D("wildfire prediction performance (binary cross-entropy loss; AUROC) of a dynamic auto-encoder", "explicit"),
            "relation_or_direction": D("outperforms the others in BCE; did not outperform in AUROC", "explicit"),
            "geography": G("Salt Lake City, Portland, and Medford (100 km by 100 km grid squares in the western United States centred on these cities)", "explicit",
                           "study area (modelled grid squares)",
                           E("study area", "In this study, the regions chosen encompass 100 km by 100 km grid squares in the western United States")),
            "temporal_frame": D("trained on 11/01/2000 to 06/08/2016; validated on 06/08/2016 to 04/08/2020", "explicit",
                                E("evaluation and discussion", "We first trained a model using the time-series data from 11/01/2000 to 06/08/2016.")),
            "scenario": UNKNOWN,
            "experimental_condition": D("temporal 70% training / 30% validation split in weekly intervals; fire predicted four weekly steps ahead", "explicit",
                                        E("study area", "data set is divided temporally in weekly time intervals, t, following a ratio of 70% training data and 30% validation data")),
            "evidence": E("estimation", "The proposed model (dynamic auto-encoder) outperforms the other for the three locations (Salt Lake City, Portland, and Medford) in terms of the binary cross-entropy (BCE) loss. However, the proposed model did not outperform in terms of the other performance metric."),
            "notes": "A model-performance finding; five locations were modelled, three are named for this result.",
        },
        {
            "claim_text": "In the western United States, the 2020 season burned over 2.5 million hectares, the largest wildfire season recorded in modern history.",
            "claim_type": "background_citation",
            "concept": D("wildfire season burned area", "explicit"),
            "relation_or_direction": D("over 2.5 million hectares burned; largest season recorded in modern history", "explicit"),
            "geography": G("the western United States", "explicit", "background context"),
            "temporal_frame": D("the 2020 season", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("introduction", "In the western United States alone, the 2020 season saw over 2.5 million hectares burned, the largest wildfire season recorded in modern history (Higuera and Abatzoglou 2020)."),
            "notes": "Attributed to Higuera and Abatzoglou 2020.",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("evaluation and discussion", "In Figure 9, as shown in the linked video, the wildfire prediction map shows qualitative correlation with the ground truth."),
            "reason": "Qualitative statement about a figure and video; no measurable result to restate.",
        },
        {
            "evidence": E("related work", "Wildfire forecasting models have been created through several methods, but existing systems, such as the Canadian Forest Fire Weather Index System, rely on weather stations and closed-form mathematical equations to attain a fire risk probability (Wagner 1987)."),
            "reason": "Background characterisation of another system; not this paper's evidence.",
        },
        {
            "evidence": E("introduction", "Figure 1: Wildfire in Northern California between 06/01/2020 and 12/31/2020 from Fire Information for Resource Management System (FIRMS) data set"),
            "reason": "A figure caption illustrating the data; Northern California is not among the modelled locations.",
        },
        {
            "evidence": E("abstract", "As wildfires are expected to become more frequent and severe, improved prediction models are vital to mitigating risk and allocating resources."),
            "reason": "Motivational statement with no source, horizon or place.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "The five study cities are Portland, Oregon; Medford, Oregon; Reno, Nevada; Denver, Colorado; and Salt Lake City, Utah.",
}

# ---------------------------------------------------------------------------
# LIT2-000673 (250541813) --- fire_weather_v1 rank 50
_TIME_673_RT = D(
    "5 July to 30 November 2019 (Day-1 real-time forecasts)", "explicit",
    E("emissions", "for the period between 5 July and 30 November 2019"),
)
ITEMS["LIT2-000673"] = {
    "bibliographic": {
        "title": "$.title",
        "note": "The stored title begins with the label 'Model description paper'. `abstract` holds only a repeated fragment ('The National Oceanic and Atmospheric', three times).",
    },
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "Borderline. The paper describes and evaluates a global aerosol forecast model; a large "
        "part of the evaluation is its forecast of smoke (AOD) from wildfire and biomass-burning "
        "events and of dust events, framed by the health concern of PM2.5 exposure."
    ),
    "scope_evidence": E("introduction", "The US Environmental Protection Agency (EPA) and the Centers for Disease Control and Prevention (CDC) also use the NOAA forecasts for applications with wildfire, health, and smoke vulnerability assessments."),
    "claims": [
        {
            "claim_text": "For the August 2019 fires in South America, GEFS-Aerosols reproduced the enhanced AOD near the Bolivia-Paraguay-Brazil border seen by satellites and MERRA-2, whereas NGACv2 AOD was over 80% below observations.",
            "claim_type": "finding",
            "concept": D("total AOD forecast during fire events (smoke from large fires)", "explicit"),
            "relation_or_direction": D("GEFS-Aerosols reproduces the enhancement; NGACv2 more than 80% smaller than observations", "explicit"),
            "geography": G("South America near the border of Bolivia, Paraguay, and Brazil (Amazon rainforest fires)", "explicit", "evaluation case region (fire event)"),
            "temporal_frame": D("August 2019 (forecast for 25 August)", "explicit",
                                E("emissions", "Figure 4 shows the total AOD forecast on 25 August compared against the NGACv2 model")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("emissions", "The GEFS-Aerosols AOD is able to reproduce the enhanced AOD due to several fire events over South America near the border of Bolivia, Paraguay, and Brazil, which were also observed by the VIIRS and MODIS satellite instruments and captured by the MERRA-2 analysis."),
            "notes": "The NGACv2 figure is in the same field: 'NGACv2 AOD is more than 80 % smaller than the observations over the fire source region'.",
        },
        {
            "claim_text": "At the Alta Floresta AERONET site in the Amazon fire source region, GEFS-Aerosols Day-1 AOD reproduced two fire-plume AOD peaks (late August, late September), with correlation 0.66 versus ICAP 0.9 and NGACv2 0.68.",
            "claim_type": "finding",
            "concept": D("daily total AOD variations; fire plumes", "explicit"),
            "relation_or_direction": D("consistent with AERONET; correlation (RMSE) 0.66 (0.23) GEFS-Aerosols, 0.9 (0.12) ICAP, 0.68 (0.31) NGACv2", "explicit"),
            "geography": G("the Alta Floresta site, in the middle of the Amazon fire source region", "explicit", "evaluation site (fire source region)"),
            "temporal_frame": D("1 July-30 November 2019", "explicit",
                                E("evaluation of aod associated with fire events", "at the four AERONET sites near the fire source regions of South America during the period of 1 July-30 November 2019")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("evaluation of aod associated with fire events", "At the Alta Floresta site, which is in the middle of the Amazon fire source region, the daily AOD variations of both the ICAP and GEFS-Aerosols Day-1 predictions are quite consistent with those of the AERONET data, especially as they are able to reproduce two peaks in AOD enhancements in late August and late September caused by fire plumes (Fig. 9a)."),
            "notes": "The statistics are in the next sentence: 'The correlation (RMSE) is 0.66 (0.23), 0.9 (0.12), and 0.68 (0.31) for GEFS-Aerosols, ICAP, and NGACv2.'",
        },
        {
            "claim_text": "Of the selected AERONET sites, 20 (about 30%) had GEFS-Aerosols total AOD correlations above 0.7, against only one site for NGACv2.",
            "claim_type": "finding",
            "concept": D("correlation of daily total AOD with AERONET", "explicit"),
            "relation_or_direction": D("20 sites above 0.7 for GEFS-Aerosols versus 1 site for NGACv2", "explicit"),
            "geography": G("60 selected AERONET sites globally", "explicit", "evaluation network (global)",
                           E("emissions", "The locations of the 60 selected AERONET sites where these comparisons were made are listed in Table 1.")),
            "temporal_frame": _TIME_673_RT,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("emissions", "There are 20 sites (about 30 % of the site total) displaying highly correlated total AOD for the AERONET data and GEFS-Aerosols, with the correlation coefficients exceeding 0.7."),
            "notes": "The NGACv2 count is in the next sentence: 'In contrast, there is only 1 site with a correlation coefficient larger than 0.7 for NGACv2 model vs. AERONET'.",
        },
        {
            "claim_text": "During biomass burning events, GEFS-Aerosols captured major fires over southern Africa, Siberia, the central Amazon and central South America much better than NGACv2, possibly partly through plume-rise vertical transport.",
            "claim_type": "finding",
            "concept": D("forecast of biomass burning events (major fires) in AOD", "explicit"),
            "relation_or_direction": D("captured much better than NGACv2; part of the improvement may be due to the plume rise module (hedged)", "explicit"),
            "geography": G("southern Africa, Siberia, the central Amazon, and central South America", "explicit", "regions of evaluated fire events"),
            "temporal_frame": _TIME_673_RT,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("summary and future plan", "During the biomass burning events, GEFS-Aerosols captured major fires over southern Africa, Siberia, the central Amazon, and central South America much better than NGACv2."),
            "notes": "The plume-rise attribution is the next sentence: 'Part of the improvement may be due to the vertical transport by the plume rise module.'",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("emissions", "Additionally, a parameterization based on the fire weather index (FWI) to estimate biomass burning emissions on longer temporal scales may help to improve and extend the forecast of fire impacts."),
            "reason": "Hedged future work ('may help'); FWI is not used in this paper.",
        },
        {
            "evidence": E("emissions", "Angola experienced almost 3 times more fires than Brazil in mid-August 2019."),
            "reason": "Context attributed to NASA satellite imagery; not this paper's analysis.",
        },
        {
            "evidence": E("evaluation of major regional averages", "Both the eastern and western US regions exhibit GEFS-Aerosols low biases of about 5 %-30 %, with the largest differences in the eastern US occurring in August 2019."),
            "reason": "A general AOD bias result for US regions, not tied to a fire or dust hazard event.",
        },
        {
            "evidence": E("atom-1 retrospective forecast evaluation", "During ATom-1, plumes from dust storms and large biomass burning events and low-level sea-salt aerosols were observed over the South and central Atlantic, and anthropogenic pollution was observed over the United States on the last flight from Minnesota to southern California."),
            "reason": "Describes what the aircraft campaign observed; context for the retrospective evaluation, not a finding about a hazard.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "Most fields repeat whole passages two or three times (an extraction artifact); spans use the first occurrence. The ATom-1 section states measurements 'in July and August 2021' for a 2016 campaign; kept as stored, not used.",
}

# ---------------------------------------------------------------------------
# LIT2-000786 (257108685) --- fire_weather_v1 rank 60
_TIME_786 = D(
    "studies published through April 2021 (the review's search window)", "inferred",
    E("review approach and available literature", "to search for papers on responses of bats to prescribed fire and wildfire through April 2021"),
)
ITEMS["LIT2-000786"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "A global literature review of how bats respond to wildfire and prescribed fire, "
        "i.e. the ecological impacts of a fire hazard, including threats from more frequent and "
        "severe wildfires."
    ),
    "scope_evidence": E("abstract", "We reviewed this rapidly expanding body of literature to determine whether bats respond differently to prescribed fire and wildfire, and the important factors driving those differences."),
    "claims": [
        {
            "claim_text": "Across 52 reviewed studies, bats generally showed positive or neutral responses to prescribed fire, whereas a greater proportion of negative responses was reported for wildfire.",
            "claim_type": "finding",
            "concept": D("bat responses to prescribed fire and wildfire", "explicit"),
            "relation_or_direction": D("positive or neutral to prescribed fire; greater proportion negative for wildfire", "explicit"),
            "geography": G("North and South America, Europe, Australia, and Africa (studies from Europe, South America, and Africa limited)", "explicit",
                           "regions of the reviewed studies",
                           E("abstract", "Our review included 52 studies (29 prescribed fire, 23 wildfire) from North and South America, Europe, Australia, and Africa, although studies from Europe, South America, and Africa were limited.")),
            "temporal_frame": _TIME_786,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("abstract", "In general, we found that bats show positive or neutral responses to prescribed fire, whereas a greater proportion of negative responses were reported for wildfire."),
            "notes": "A synthesis finding of the review.",
        },
        {
            "claim_text": "Some negative bat responses to wildfire are short-lived or local, which the authors take to suggest that bats may be resilient to the effects of fire.",
            "claim_type": "finding",
            "concept": D("negative responses to wildfire; resilience of bats to fire", "explicit"),
            "relation_or_direction": D("short-lived or local; suggesting bats may be resilient (hedged)", "explicit"),
            "geography": G("North and South America, Europe, Australia, and Africa (studies from Europe, South America, and Africa limited)", "inferred",
                           "regions of the reviewed studies",
                           E("abstract", "Our review included 52 studies (29 prescribed fire, 23 wildfire) from North and South America, Europe, Australia, and Africa, although studies from Europe, South America, and Africa were limited.")),
            "temporal_frame": _TIME_786,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("abstract", "However, some of the negative responses to wildfire are short-lived or local, suggesting that bats may be resilient to the effects of fire."),
            "notes": None,
        },
        {
            "claim_text": "A cited study estimated that after a severe wildfire burned about 40% of Vesuvius National Park, suitable habitat for its 12 bat species fell about 40% for open-area foragers and 60-80% for interior-forest species.",
            "claim_type": "background_citation",
            "concept": D("suitable habitat for bat species after a severe wildfire", "explicit"),
            "relation_or_direction": D("declined by approximately 40% (open-area foragers) and up to 60-80% (interior-forest species)", "explicit"),
            "geography": G("Vesuvius National Park in southern Italy", "explicit", "study area of the cited study"),
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("introduction", "Bosso et al. (2018) estimated that suitable habitat for the 12 bat species in Vesuvius National Park in southern Italy declined by approximately 40% for species that foraged in open areas but up to 60-80% for species that were dependent on interior forests after a severe wildfire burned roughly 40% (~3400 ha) of the park."),
            "notes": "Attributed to Bosso et al. (2018).",
        },
        {
            "claim_text": "A cited study found bat species richness in Sierra Nevada mixed-conifer forests positively associated with the extent of area burned by wildfires in the prior 30 years, across 1-10 km buffers.",
            "claim_type": "background_citation",
            "concept": D("bat species richness; extent of areas burned by wildfires", "explicit"),
            "relation_or_direction": D("positively associated across all buffer sizes", "explicit"),
            "geography": G("mixed-conifer forests of the Sierra Nevada, California", "explicit", "study area of the cited study"),
            "temporal_frame": D("wildfires in the 30 years prior to the study", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("bat responses to burned versus unburned sites", "related bat species richness in mixed-conifer forests of the Sierra Nevada, California, to extent of areas burned by wildfires in the 30 years prior to the study, measured as proportion of circular buffers with 1-10-km radii, and found that bat species richness was positively associated with burned area extent across all buffer sizes."),
            "notes": "The sentence's subject (the cited authors) is missing in the source; it begins with lower-case 'related'. Kept as stored.",
        },
        {
            "claim_text": "A cited study found that in California montane forests, M. lucifugus occupancy declined with time since last fire, while Eptesicus fuscus occupancy rose to about 30 years post-fire, plateaued, then decreased.",
            "claim_type": "background_citation",
            "concept": D("bat occupancy; time since last fire", "explicit"),
            "relation_or_direction": D("M. lucifugus declined with time since fire; E. fuscus increased to ~30 years, levelled off 30-60 years, decreased at ~70 years", "explicit"),
            "geography": G("the montane forests of California", "explicit", "study area of the cited study"),
            "temporal_frame": D("time since last burn 3-107 years", "explicit",
                                E("effects of fire parameters on bats-burn extent", "examined bats' responses to burns where time since last burn was 3-107 years")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("effects of fire parameters on bats-burn extent", "They found that in the montane forests of California, occupancy of M. lucifugus declined as time since last fire increased"),
            "notes": "Attributed to Blakey et al. (2019).",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("bat responses to burned versus unburned sites", "The underlying map shows fire potential, measured by the linear trend in the number of days annually that exceeded the 95th percentile of the Fire Weather Index over the years 1979-2019."),
            "reason": "A figure caption describing a background map reproduced from Bowman et al. (2020); not a finding of this review and not analysed in it.",
        },
        {
            "evidence": E("abstract", "Although current studies suggest that fire may be an important management tool for improving bat habitat, the threat of more frequent, extensive, and severe wildfires may put additional stress on some bat populations, particularly those being impacted by disease, habitat loss and fragmentation, and climate change."),
            "reason": "Hedged ('may') forward-looking statement; no horizon, scenario or place.",
        },
        {
            "evidence": E("effects of fire on roosts and roosting habitat", "Changing climates along with changes in land use history and management practices are significantly influencing the frequency, severity, and extent of wildfires across the globe"),
            "reason": "Background statement attributed to several references; not examined in the review.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "Most fields repeat whole passages two or three times; spans use the first occurrence. The abstract also holds a Spanish translation. Some sentences are truncated in the source (e.g. 'In contrast, M. (Schwab 2006).').",
}

# ---------------------------------------------------------------------------
# LIT2-001063 (272211804) --- fire_weather_v1 rank 70
ITEMS["LIT2-001063"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "A perspective proposing a broader framework for attributing the impacts of extreme "
        "weather events (droughts, marine heatwave, wildfires, floods) to human influence, "
        "illustrated with five case studies."
    ),
    "scope_evidence": E("abstract", "In this perspective, we argue that adapting current practice in EEA to also consider other causal factors in attribution of extreme weather impacts would provide richer and more comprehensive insight into the causes of disasters."),
    "claims": [
        {
            "claim_text": "At Lake Mendocino, the water saved by the FIRO-enabled deviation from mandated reservoir storage limits was close to 20% in water year 2020.",
            "claim_type": "finding",
            "concept": D("Forecast Informed Reservoir Operations (FIRO) as a drought adaptation; reservoir water storage", "explicit"),
            "relation_or_direction": D("water saved close to 20% compared with the counterfactual mandated storage", "explicit"),
            "geography": G("Lake Mendocino, a reservoir in the upper Russian River watershed in coastal northern California", "explicit",
                           "case-study site (this paper's own counterfactual calculation)",
                           E("case study", "The pilot project was Lake Mendocino, a reservoir with a maximum storage of 111 000 acre-feet in the upper Russian River watershed in coastal northern California.")),
            "temporal_frame": D("water year 2020", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": D("counterfactual: storage limited to the previously mandated level during the cool season", "explicit",
                                        E("case study", "To construct the counterfactual, we limit the storage to the mandated level during the cool season when water input is provided from atmospheric rivers.")),
            "evidence": E("case study", "The water saved through the use of a major deviation, requested as a result of the positive FIRO viability assessment, was close to 20% in water year 2020 (figure 7)."),
            "notes": "The paper calls the factual/counterfactual pair 'both scenarios'; these are operating-rule counterfactuals, not emissions scenarios, so `scenario` is unknown.",
        },
        {
            "claim_text": "A cited study showed that the climate change signal would have led to larger burned areas in Portugal's 2017 fire season, in the absence of other drivers.",
            "claim_type": "background_citation",
            "concept": D("climate change signal; burned areas of the fire season", "explicit"),
            "relation_or_direction": D("would have led to larger burned areas", "explicit"),
            "geography": G("Portugal", "explicit", "case-study area (from a cited study)"),
            "temporal_frame": D("the 2017 fire season (not restricted to the October event)", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("case study", "Turco et al (2019) have already shown that the climate change signal would have led to larger burned areas for the 2017 fire season over Portugal (not restricted to the October event), in the absence of other drivers."),
            "notes": "Attributed to Turco et al (2019).",
        },
        {
            "claim_text": "On 15 October 2017, Hurricane Ophelia near the Iberian coast advected extremely hot, dry air from Northern Africa, with temperatures over 30 °C and relative humidity below 20% over most of Portugal.",
            "claim_type": "background_citation",
            "concept": D("advection of extremely hot and dry air; near-surface temperature; relative humidity", "explicit"),
            "relation_or_direction": D("temperature over 30 °C; relative humidity below 20%", "explicit"),
            "geography": G("most of the Portuguese territory", "explicit", "case-study area (fire event)"),
            "temporal_frame": D("15 October (2017)", "inferred",
                                E("case study", "here we focus on the event occurring between 15 and 16 of October")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("case study", "On 15 October Ophelia was close to the coast of the Iberian Peninsula and promoted the advection of extremely hot and dry air from Northern Africa, with near-surface temperature reaching over 30 • C and relative humidity below 20% over most of the Portuguese territory (Ramos et al 2023)."),
            "notes": "Attributed to Ramos et al (2023). The year is given by the case study's framing ('The year 2017 was one of the worst fire seasons recorded in Europe').",
        },
        {
            "claim_text": "A cited attribution analysis found anthropogenic influence on rainfall and evapotranspiration raised the 2021-2022 southern Horn of Africa drought to 'exceptional'; without climate change it would have been a normal drought.",
            "claim_type": "background_citation",
            "concept": D("drought severity; anthropogenic influence on rainfall and evapotranspiration", "explicit"),
            "relation_or_direction": D("increased the drought severity to 'exceptional'; otherwise a normal drought", "explicit"),
            "geography": G("the southern Horn of Africa covering parts of southern Ethiopia, southern Somalia, and eastern Kenya", "explicit", "case-study area (from a cited study)"),
            "temporal_frame": D("the drought years (2021-2022)", "explicit",
                                E("case study", "The drought years (2021-2022) have also been affected by internal variability")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("case study", "Attribution analysis of rainfall trends and the combined effect of rainfall deficit with high temperatures in the southern Horn of Africa covering parts of southern Ethiopia, southern Somalia, and eastern Kenya showed that anthropogenic influence on both rainfall and evapotranspiration increased the drought severity to 'exceptional' (based on the US Drought Monitor classification n.d.), whereas in the absence of climate change it would have been a normal drought (Kimutai et al 2023)."),
            "notes": "Attributed to Kimutai et al (2023). The counterfactual 'absence of climate change' is not an emissions scenario.",
        },
        {
            "claim_text": "From 2012 to 2016, California had one of its deepest, longest and warmest droughts in history, with an estimated return period of one in 1200 years.",
            "claim_type": "background_citation",
            "concept": D("drought (depth, length, warmth); return period", "explicit"),
            "relation_or_direction": D("one of the deepest, longest, and warmest; return period one in 1200 years", "explicit"),
            "geography": G("California", "explicit", "case-study area (from a cited study)"),
            "temporal_frame": D("2012 to 2016", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("case study", "From 2012 to 2016, California experienced one of its deepest, longest, and warmest droughts in history, with a return period estimated at one in 1200 years (Lund et al 2018)."),
            "notes": "Attributed to Lund et al (2018).",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("case study", "They based their analysis on a commonly used fire risk model, the Canadian Forest Fire Weather Index System to decompose the event into the most relevant components of the 'fire triangle': hydroclimatic drivers, fuel characteristics, and ignitions."),
            "reason": "Describes the method of a cited study (Ramos et al 2023); no result to restate.",
        },
        {
            "evidence": E("case study", "It thus appears reasonable to hypothesize (although no specific attribution analysis has been conducted to our knowledge) that climate change may have contributed to increasing the heat and atmospheric dryness advected by Ophelia"),
            "reason": "Explicitly a hypothesis without an attribution analysis; not promoted.",
        },
        {
            "evidence": E("introduction", "They found that urban development alone increased peak discharges by 54% (±28%) and climate change alone increased them by 20% (±3%) with a combined effect of 84% (±35%)."),
            "reason": "A cited result (Sebastian et al 2019, Hurricane Harvey); beyond the five-claim cap and peripheral to the paper's case studies.",
        },
        {
            "evidence": E("case study", "The severity of these extremes is predicted to increase with climate change, with high uncertainties on the average precipitation trends (Gershunov et al 2017, 2019, Swain et al 2018, Bevacqua et al 2022)."),
            "reason": "Cited projection with no stated scenario or horizon.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "A perspective paper; most quantitative statements are attributed to cited studies. Several sentences in the source run together without a space after the full stop.",
}

# ---------------------------------------------------------------------------
# LIT2-001157 (52918429) --- fire_weather_v1 rank 80
_GEO_1157 = G(
    "the Sierras Chicas (810,000 ha) in Córdoba province, Argentina, Chaco Serrano subregion", "explicit",
    "study area",
    E("abstract", "the Sierras Chicas in the Chaco Serrano subregion (Argentina)"),
)
_TIME_1157 = D(
    "FMC maps every 8 days from 2002 to 2016 (11 fire seasons analysed)", "explicit",
    E("abstract", "derived FMC maps every 8 days from 2002 to 2016 using MODIS reflectance products"),
)
ITEMS["LIT2-001157"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper derives satellite fuel-moisture thresholds to classify wildfire hazard for "
        "an Argentine mountain range, i.e. assessment of a fire hazard for early warning."
    ),
    "scope_evidence": E("abstract", "Our objectives were to analyze pre-fire FMC among different land covers and to propose a wildfire hazard classification for the Sierras Chicas in the Chaco Serrano subregion (Argentina)"),
    "claims": [
        {
            "claim_text": "Extreme and high fire hazard fuel moisture thresholds were set at 55% and 67% for grasslands, 72% and 105% for forests, and 106% and 121% for shrublands.",
            "claim_type": "finding",
            "concept": D("fuel moisture content (FMC) thresholds for extreme and high fire hazard", "explicit"),
            "relation_or_direction": D("thresholds differ by land cover (grasslands lowest)", "explicit"),
            "geography": _GEO_1157,
            "temporal_frame": _TIME_1157,
            "scenario": UNKNOWN,
            "experimental_condition": D("thresholds from percentiles of pre-fire FMC: P60 extreme, P85 high, P97 moderate", "explicit",
                                        E("relationship between pre-fire fmc and fire size", "we used the following percentiles: P60 defined Extreme hazard, P85 defined High hazard, P97 defined Moderate hazard")),
            "evidence": E("abstract", "Extreme and high fire hazard thresholds for grasslands were established at FMC of 55% and 67% respectively, at 72% and 105% for forests and at 106% and 121% for shrublands."),
            "notes": None,
        },
        {
            "claim_text": "Large fires (over 1000 ha) occurred at a median live fuel moisture of about 74%, significantly lower than small fires (100-500 ha) at about 91%.",
            "claim_type": "finding",
            "concept": D("pre-fire fuel moisture content; fire size", "explicit"),
            "relation_or_direction": D("large fires at lower LFMC (74% versus 91%; Kruskal Wallis H = 8.44, P = 0.0037)", "explicit"),
            "geography": _GEO_1157,
            "temporal_frame": _TIME_1157,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("relationship between pre-fire fmc and fire size", "Large fires occurred with median LFMC values around 74%; whereas small fires occurred with median values around 91%, which means a difference of 17 percentage points (Table 1)."),
            "notes": "The significance test is in the preceding sentence: '(Kruskal Wallis H = 8.44; P = 0.0037)'.",
        },
        {
            "claim_text": "Higher fuel moisture constrains the maximum size wildfires reach: quantile regression showed a significant negative relationship between the upper 30% of fire sizes and pre-fire FMC, with limited effect on mean size.",
            "claim_type": "finding",
            "concept": D("pre-fire FMC; fire size (upper quantiles)", "explicit"),
            "relation_or_direction": D("significant negative relationship for quantiles of 0.7 and above (p < 0.05); limited effect on the mean size", "explicit"),
            "geography": _GEO_1157,
            "temporal_frame": _TIME_1157,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("relationship between pre-fire fmc and fire size", "Quantile regression estimates indicated a significant negative relationship between the upper 30% fire sizes and pre-fire FMC"),
            "notes": None,
        },
        {
            "claim_text": "On average, fuel moisture was 12.1, 11.4 and 7.1 percentage points lower in years with high fire activity than in low-fire years for Chaco forests, grasslands and shrublands.",
            "claim_type": "finding",
            "concept": D("average FMC in high versus low fire-activity years", "explicit"),
            "relation_or_direction": D("lower by 12.1, 11.4 and 7.1 percentage points", "explicit"),
            "geography": _GEO_1157,
            "temporal_frame": _TIME_1157,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("wildfire hazard classification based on fmc", "On average, FMC was 12.1, 11.4 and 7.1 percentage points lower in years with high fire activity than in years with low fire activity for Chaco forests, grasslands and shrublands, respectively."),
            "notes": None,
        },
        {
            "claim_text": "Average FMC over all years never fell below the extreme hazard threshold for grasslands and Chaco forests, but in fire years it was below it for 48 and 40 days, respectively.",
            "claim_type": "finding",
            "concept": D("days below the extreme fire hazard FMC threshold", "explicit"),
            "relation_or_direction": D("never below on average; 48 and 40 days below during fire years", "explicit"),
            "geography": _GEO_1157,
            "temporal_frame": _TIME_1157,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("wildfire hazard classification based on fmc", "While the average FMC of all years was never below the extreme fire hazard threshold for grasslands and Chaco forests, during fire years FMC was below this threshold for 48 and 40 days, respectively."),
            "notes": None,
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("introduction", "At present, the existing early warning systems in the Sierras Chicas are based on: i) sparse point-based estimations of the fire danger indices from the Canadian Forest Fire Weather Index System [44]"),
            "reason": "Context on the current warning system; not a finding.",
        },
        {
            "evidence": E("discussion", "Similar to what we observed in the Sierras Chicas, large fires in the Chaparral in California take place when live fuel moisture lowers below a threshold of 79% [23], and small fires occur over a wide range of values [17]."),
            "reason": "A cited comparison result from another ecosystem; not this paper's evidence.",
        },
        {
            "evidence": E("discussion", "For instance, de Jong et al. [67] used the 99th percentile of historical FWI (Fire Weather Index of the Canadian Forest Fire Weather Rating System) data to determine exceptional fire weather conditions in the UK."),
            "reason": "Cited methodological example for choosing percentiles; not a finding about a hazard.",
        },
        {
            "evidence": E("abstract", "However, moisture alone is not sufficient to represent true fire hazard in Chaco forests and the combination with other variables would provide better hazard assessments."),
            "reason": "An interpretive judgement rather than a measured result.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "The 'introduction' field begins mid-sentence ('before fires in Mediterranean grasslands ...'); part of it is missing in the source.",
}

# ---------------------------------------------------------------------------
# LIT2-001236 (59342086) --- fire_weather_v1 rank 90
_GEO_1236 = G(
    "the eastern part of Attica Greece, 20 km from Athens city center, in a semi-rural touristic area called Rafina-Mati", "explicit",
    "evaluation case (retrospective wildfire incident)",
    E("experiment execution and evaluation of the findings", "a lethal wild fire broke out at the eastern part of Attica Greece, 20 km from Athens city center in a semi-"),
)
ITEMS["LIT2-001236"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "Borderline. Mainly an IoT data-interoperability paper, but its evaluation is early "
        "wildfire detection and fire-danger assessment, tested retrospectively on a deadly 2018 "
        "wildfire in Greece."
    ),
    "scope_evidence": E("abstract", "These specifications have been utilised for the implementation of the IoT2Edge interoperability enabling mechanism which is evaluated within the context of a catastrophic wildfire incident that took place in Greece on July 2018."),
    "claims": [
        {
            "claim_text": "Triggered every two minutes over 20-26 July 2018, the decision-making service correctly detected the presence or absence of the fire in 93.6-98.9% of over 5000 triggers for the optimal weight configurations.",
            "claim_type": "finding",
            "concept": D("cross-platform fire detection decision support (fire occurrence probability)", "explicit"),
            "relation_or_direction": D("successfully detects existence or lack of fire in 93.6-98.9% of triggers", "explicit"),
            "geography": _GEO_1236,
            "temporal_frame": D("20-26/7/2018 (fire on 23/7/2018 from 16:41)", "explicit",
                                E("experiment execution and evaluation of the findings", "the DMS was triggered to detect potential fire incidents every two min for the period 20-26/7/2018")),
            "scenario": UNKNOWN,
            "experimental_condition": D("weighted fusion of MESP image, social media, weather and EFFIS scores; FD TRUE thresholds tested in [0.60,0.95]", "explicit",
                                        E("experiment execution and evaluation of the findings", "where the range of FD TRUE values tested was [0.60,0.95]")),
            "evidence": E("experiment execution and evaluation of the findings", "This resulted in over 5000 DMS triggers for 93.6-98.9% of which the DMS successfully detects the existence or lack of fire incident occurrence for the optimal weight configurations"),
            "notes": "A retrospective evaluation on collected data, not a live deployment.",
        },
        {
            "claim_text": "The fire weather index computed from local weather data was above 100 when the Rafina-Mati fire ignited and stayed extremely high for the whole fire; EFFIS's Extreme class corresponds to FWI above 50.",
            "claim_type": "finding",
            "concept": D("fire weather index (FWI), based on the Canadian forest fire danger rating system", "explicit",
                         E("experiment execution and evaluation of the findings", "the weather measurements have been processed to extract the respective fire weather index (FWI), based on the Canadian forest fire danger rating system")),
            "relation_or_direction": D("very high at ignition (above 100); remained extremely high for the entire fire duration", "explicit"),
            "geography": _GEO_1236,
            "temporal_frame": D("23 July 2018 (the fire's duration)", "explicit",
                                E("experiment execution and evaluation of the findings", "at 16.40 on 23 July 2018")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("experiment execution and evaluation of the findings", "As one may easily observe, the fire ignition occurred when very high fire weather index levels were in place (i.e., above 100) and for the entire fire duration the respective FWI remained extremely high"),
            "notes": "FWI here is the Canadian fire weather index computed from air temperature, relative humidity, wind speed and precipitation from local weather stations.",
        },
        {
            "claim_text": "The first related tweet about the fire was posted at 16:53, 12 minutes after the official ignition, and tweet volumes rose promptly once the fire started.",
            "claim_type": "finding",
            "concept": D("social media (Twitter) activity as a fire-detection signal", "explicit"),
            "relation_or_direction": D("first tweet 12 min after ignition; tweet populations increased promptly", "explicit"),
            "geography": _GEO_1236,
            "temporal_frame": D("23 July 2018; tweets collected 19/7/2018 to 26/7/2018", "explicit",
                                E("experiment execution and evaluation of the findings", "we collected all the Tweets from 19/7/2018 until 26/7/2018")),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("experiment execution and evaluation of the findings", "It is also worth noting that the tweet was posted just 12 min after the official ignition of the fire."),
            "notes": "The time 16:53 is in the preceding sentence: 'the first related tweet was posted at 16:53'.",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("experiment design and rationale", "to the \"deadliest and most destructive fire in the USA's modern history\" in California, where more than 150,000 acres of land were burned and 86 casualties were recorded, in November of the same year"),
            "reason": "Background motivation about another fire; not this paper's evidence.",
        },
        {
            "evidence": E("experiment execution and evaluation of the findings", "This means that the employed data interoperability mechanism causes the MESP-R to operate approximately 2 hours and 18 min less."),
            "reason": "A device energy result; not about a hazard.",
        },
        {
            "evidence": E("experiment design and rationale", "These forecasts are based on the Canadian Forest Fire Weather Index (FWI) System where past, current and future weather information are aggregated with location specific information"),
            "reason": "Description of the EFFIS data source; not a finding.",
        },
        {
            "evidence": E("experiment design and rationale", "A combination of climate change, population growth, negligent forest management and modern building practices has had an increasing effect on the proliferation of forest wildfires at a global level over the last few years [65]."),
            "reason": "Background statement attributed to a reference.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "In the 'experiment design and rationale' field the source names a Raspberry Pi with an arduino.cc URL; kept as stored.",
}

# ---------------------------------------------------------------------------
# LIT2-001308 (999274) --- fire_weather_v1 rank 100
_GEO_1308 = G(
    "San Diego County, California (county region and six sub-regions)", "explicit", "study area",
    E("abstract", "A study of the impacts on respiratory health of the 2007 wildland fires in and around San Diego County, California is presented."),
)
_TIME_1308 = D(
    "2007 season; ED data analysed 08/01/2007 through 11/29/2007", "explicit",
    E("syndromic surveillance heath data", "analysis of the complete data set was limited to the time period of 08/01/2007 through 11/29/2007"),
)
ITEMS["LIT2-001308"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper models how particulate matter from the 2007 San Diego wildland fires "
        "affected emergency department visits for respiratory illness, i.e. the health impacts "
        "of a fire hazard."
    ),
    "scope_evidence": E("abstract", "A study of the impacts on respiratory health of the 2007 wildland fires in and around San Diego County, California is presented."),
    "claims": [
        {
            "claim_text": "For the 2007 season, at peak fire particulate concentrations the odds of a person seeking emergency care rose by about 50% compared with non-fire conditions (41% regional model, 72% sub-regional model).",
            "claim_type": "finding",
            "concept": D("wildfire (fire-emitted) particulate concentrations; odds of seeking emergency care for respiratory syndromes", "explicit"),
            "relation_or_direction": D("increased by approximately 50% (41% generalized case, 72% geographically specific case)", "explicit"),
            "geography": _GEO_1308,
            "temporal_frame": _TIME_1308,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("conclusion", "Model results from this study for the 2007 season, show that at peak fire particulate concentrations the odds of a person seeking emergency care is increased by approximately 50% compared to non-fire conditions (41% for the generalized case, 72% for a geographically specific case; see Table 4)."),
            "notes": "The abstract gives the same result as '40% for the regional case, 70% for a geographically specific case'; the conclusion's 41% / 72% match the results section.",
        },
        {
            "claim_text": "The county-level model explained 76.6% of deviance in respiratory ED visits, but under-estimated visits by roughly 15% in mid-August and during the PM10 spike after the October burn.",
            "claim_type": "finding",
            "concept": D("model fit for respiratory-related ED visits", "explicit"),
            "relation_or_direction": D("deviance explained 76.6%; under-estimated by roughly 15% on the two exception periods", "explicit"),
            "geography": _GEO_1308,
            "temporal_frame": _TIME_1308,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("model diagnostics and results", "The model performs well (deviance explained is 76.6%; Table 3) capturing the increasing seasonal trend in ED respiratory-related visits and inter-day variability related to the weekend effect."),
            "notes": "The exceptions and the 15% figure are in the following sentences of the same field.",
        },
        {
            "claim_text": "In the sub-regional model, a higher proportion of households above $50k lowered the odds of ED visits while a higher proportion of people under 24 raised them, suggesting geographic differences in health care access after a wildfire.",
            "claim_type": "finding",
            "concept": D("demographic variables (income, age); odds of ED visits following a wildfire", "explicit"),
            "relation_or_direction": D("wealthier households decrease odds; population below 24 increases odds; access may vary by geography (hedged)", "explicit"),
            "geography": _GEO_1308,
            "temporal_frame": _TIME_1308,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("model diagnostics and results", "The coefficients of these demographic variables in Table 4 show that an increase in proportion of wealthy households (>$50 k) leads to a decrease in ED visit odds while an increase in proportion of population below 24 years increases the odds."),
            "notes": None,
        },
        {
            "claim_text": "A separate analysis using the Canadian Fire Weather Index computed from Regional Climate Model output indicates San Diego County will see about two extreme fire seasons each decade by 2040, similar to the present.",
            "claim_type": "projection",
            "concept": D("Canadian Fire Weather Index; extreme fire seasons", "inferred",
                         E("discussion", "Canadian Fire Weather Index was calculated for the study area using weather variables produced by the Regional Climate Model (RegCM v. 4")),
            "relation_or_direction": D("approximately two extreme fire seasons each decade by 2040, similar to the present", "explicit"),
            "geography": G("San Diego County", "explicit", "study area (projection)"),
            "temporal_frame": D("by 2040", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("discussion", "San Diego County will experience approximately two extreme fire seasons each decade by 2040, similar to the present."),
            "notes": "The source text is truncated: the sentence naming the FWI and RegCM v. 4 breaks off and runs into this one, so the link between the FWI calculation and the projection is inferred from adjacency. No emissions scenario is named.",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("background", "In 2007, catastrophic wildland fires burned approximately 650,000 acres of southern Californian grassland and chaparral."),
            "reason": "Context for the study event, stated without analysis in this paper; not promoted.",
        },
        {
            "evidence": E("background", "Models of future climate generally predict weather conditions that favor an increase in the occurrence and severity of California wildland fires"),
            "reason": "General background projection attributed to a reference; no scenario or horizon.",
        },
        {
            "evidence": E("model diagnostics and results", "On Tuesdays, the effect is less pronounced with a 7% increase in the odds of seeking ED care for both models."),
            "reason": "Day-of-week effect; not about the hazard.",
        },
    ],
    "terminal_status": "claims_extracted",
}

# ---------------------------------------------------------------------------
# LIT2-000084 (154971876) --- extreme_heat_v1 rank 14
_TIME_84 = D(
    "8-year (2004-2011) simulated period", "explicit",
    E("methods", "We compared 8-year (2004-2011) differences (CROP-CROPIRR) in heat wave frequency"),
)
_EXP_84 = D(
    "two WRF3.3-CLM4crop simulations, without irrigation (CROP) and with irrigation (CROPIRR); a hypothetical irrigation loss scenario", "explicit",
    E("methods", "One is a simulation without irrigation (hereafter referred to as CROP), and the other includes irrigation (hereafter referred to as CRO-PIRR)."),
)
ITEMS["LIT2-000084"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper uses a regional climate model to quantify how loss of irrigation changes "
        "heat wave frequency, duration and intensity across the US, i.e. a heat hazard and its "
        "drivers."
    ),
    "scope_evidence": E("abstract", "In this study we investigated how loss of irrigation affects heat wave frequency, duration, and intensity across fifteen heat wave indices (HINs) using a regional climate model that incorporated dynamic crop growth."),
    "claims": [
        {
            "claim_text": "Averaged across all 15 heat wave indices in the US, simulated loss of irrigation increased heat wave frequency by 0.70 events/year, duration by 0.62 days/event, and intensity by 0.24 °C.",
            "claim_type": "finding",
            "concept": D("heat wave frequency, duration, and intensity; loss of irrigation", "explicit"),
            "relation_or_direction": D("increased by 0.70 events/year, 0.62 days/event, and 0.24 °C", "explicit"),
            "geography": G("the US (contiguous US model domain)", "explicit", "study area (model domain)",
                           E("introduction", "we analyze the effects of loss of irrigation on heat waves in the contiguous US")),
            "temporal_frame": _TIME_84,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_84,
            "evidence": E("results", "On average across all 15 HINs in the US, loss of irrigation increased heat wave frequency, duration, and intensity by 0.70 events/year, 0.62 days/event, and 0.24°C."),
            "notes": "The 'hypothetical irrigation loss scenario' is a model experiment, recorded under experimental_condition, not an emissions scenario.",
        },
        {
            "claim_text": "Without irrigation, heat wave frequency and duration increased significantly in California's Central Valley and the Southern High Plains for up to 8 of 15 indices, most in the Southern High Plains (up to 3 events/year, 2 days/event).",
            "claim_type": "finding",
            "concept": D("heat wave frequency and duration", "explicit"),
            "relation_or_direction": D("significantly increased; greatest increases up to 3 events/year and 2 days/event", "explicit"),
            "geography": G("California's Central Valley and the Southern High Plains", "explicit", "regions of strongest simulated effect"),
            "temporal_frame": _TIME_84,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_84,
            "evidence": E("results", "Heat wave frequency and duration was significantly increased without irrigation in California's Central Valley and the Southern High Plains for up to 8 out of 15 HINs (figures S1 and S2), with the greatest increases in the Southern High Plains of up to 3 events/year and 2 days/event for frequency and duration respectively (figures 1(a) and (b))."),
            "notes": None,
        },
        {
            "claim_text": "Heat index temperature metrics that include humidity were less sensitive to loss of irrigation, because increased temperature trades off against decreased humidity.",
            "claim_type": "mechanism",
            "concept": D("heat index temperature metrics that include humidity", "explicit"),
            "relation_or_direction": D("less sensitive to loss of irrigation (trade-off between increased temperature and decreased humidity)", "explicit"),
            "geography": G("the United States", "inferred", "study area (model domain)",
                           E("abstract", "In the United States, irrigation effects on heat waves were statistically significant over irrigated cropland for the majority of HINs")),
            "temporal_frame": _TIME_84,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_84,
            "evidence": E("abstract", "The heat index temperature metrics that include humidity were less sensitive to loss of irrigation due to the trade-off between increased temperature and decreased humidity."),
            "notes": "'Heat index' here covers the paper's humidity-including metrics (apparent temperature and HI, Schoen 2005); the paper uses 'HI' for heat index.",
        },
        {
            "claim_text": "In the Southern Great Plains, heat wave frequency, duration and intensity rose gradually as irrigation amount or irrigated area declined.",
            "claim_type": "finding",
            "concept": D("heat wave frequency, duration, and intensity; gradual declines in irrigation amount or irrigated area", "explicit"),
            "relation_or_direction": D("gradual increase with gradual declines in irrigation", "explicit"),
            "geography": G("the Southern Great Plains (Kansas, Nebraska, Oklahoma, and Texas)", "explicit", "analysis region",
                           E("methods", "we performed an analysis for the Southern Great Plains (Kansas, Nebraska, Oklahoma, and Texas)")),
            "temporal_frame": _TIME_84,
            "scenario": UNKNOWN,
            "experimental_condition": D("binned spatial comparison of grid cells by irrigated area / irrigation amount within CROPIRR, corrected with CROP", "explicit",
                                        E("methods", "We understand the gradual reduction irrigation effects by comparing subsets of grid cells with low irrigated area/irrigation amount to subsets with high irrigated area/irrigation amount in CROPIRR.")),
            "evidence": E("results", "We found a gradual increase in heat wave frequency, duration, and intensity with gradual declines in irrigation amount (figures 3(a)-(c)) or irrigated area (figures 3(d)-(f)) in the Southern Great Plains."),
            "notes": None,
        },
        {
            "claim_text": "The most affected areas are in Texas, Kansas, Nebraska and California, where irrigated area is greatest; nearly 35 million people live in counties sensitive to heat wave increases with irrigation decline.",
            "claim_type": "finding",
            "concept": D("areas and population sensitive to heat wave increases with irrigation decline", "explicit"),
            "relation_or_direction": D("most significantly affected where irrigated area is greatest; nearly 35 million people, mostly in California and Texas", "explicit"),
            "geography": G("Texas, Kansas, Nebraska, and California", "explicit", "regions of strongest simulated effect"),
            "temporal_frame": _TIME_84,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_84,
            "evidence": E("discussion and conclusions", "We found that the most significantly affected areas (sum of the stippled area in figures 1(a)-(c)) are in Texas, Kansas, Nebraska, and California, where irrigated area is greatest."),
            "notes": "The population figure is the next sentence: 'Nearly 35 million people live in counties sensitive to heat wave increases with irrigation decline, mostly in California and Texas.'",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("discussion and conclusions", "Deryng et al (2014) found that extreme heat stress during anthesis under the RCP 8.5 climate scenario could reduce maize, spring wheat, and soybean production."),
            "reason": "A cited projection under a named scenario (RCP 8.5); not this paper's evidence; beyond the five-claim cap.",
        },
        {
            "evidence": E("introduction", "For example, there were at least 700 excess deaths during the 1995 Chicago heat waves (Semenza et al 1996), and 15 000 excess deaths during the 2003 heat waves in France (Fouillet et al 2006)."),
            "reason": "Background figures attributed to other studies.",
        },
        {
            "evidence": E("discussion and conclusions", "With up to 2 days/event longer duration without irrigation, heat-related mortality is a concern in six counties (Fresno, Kern, Madera, Merced, Stanislaus, and Tulare) in California's Central Valley and many other counties in the Southern High Plains"),
            "reason": "An inference from the simulated duration change to a mortality concern; mortality is not modelled. Not promoted.",
        },
        {
            "evidence": E("introduction", "In the Southern High Plains, 35% of the area will be unable to support irrigation within the next 30 years under current ground water depletion rates (Scanlon et al 2012)."),
            "reason": "Cited projection of groundwater depletion; not a heat finding of this paper.",
        },
    ],
    "terminal_status": "claims_extracted",
}

# ---------------------------------------------------------------------------
# LIT2-000203 (211267687) --- extreme_heat_v1 rank 28
ITEMS["LIT2-000203"] = {
    "bibliographic": {
        "title": "$.title",
        "note": "The stored title carries the labels 'Open Peer Review STUDY PROTOCOL' and '[version 2; peer review: 2 approved]'. `abstract` holds the abstract followed by a reference list and reviewer comments.",
    },
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "A study protocol for measuring heat stress and heat strain in pregnant farmers in The "
        "Gambia and its effect on fetal wellbeing, i.e. the health impacts of a heat hazard. It "
        "reports no results of its own."
    ),
    "scope_evidence": E("abstract", "This protocol describes a study to assess the physiological response of pregnant women to environmental heat stress and the immediate effect this has on fetal wellbeing."),
    "claims": [
        {
            "claim_text": "A cited case-crossover study from California found an 8.6% increase in prematurity with every 5.6 °C increase in ambient temperature exposure.",
            "claim_type": "background_citation",
            "concept": D("ambient temperature exposure; prematurity", "explicit"),
            "relation_or_direction": D("8.6% increase per 5.6 °C increase", "explicit"),
            "geography": G("California (temperate regions)", "explicit", "study area of the cited study"),
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("introduction", "In temperate regions, a case-crossover study from California found an 8.6% increase in prematurity with every 5.6°C increase in ambient temperature exposure 17 ."),
            "notes": "Attributed to reference 17.",
        },
        {
            "claim_text": "Climate change predictions indicate global temperatures are likely to exceed those of the last 200,000 years, rising about 4 °C above pre-industrial levels by 2100 without effective mitigation of current emission rates.",
            "claim_type": "background_citation",
            "concept": D("global temperatures", "explicit"),
            "relation_or_direction": D("likely to exceed the last 200,000 years; rising by around 4 °C above pre-industrial levels", "explicit"),
            "geography": G("global", "explicit", "background context"),
            "temporal_frame": D("by 2100", "explicit"),
            "scenario": D("without effective mitigation of current emission rates", "explicit"),
            "experimental_condition": UNKNOWN,
            "evidence": E("abstract", "Climate change predictions indicate that global temperatures Introduction: are likely to exceed those seen in the last 200,000 years, rising by around 4°C above pre-industrial levels by 2100 (without effective mitigation of current emission rates)."),
            "notes": "The section label 'Introduction:' is embedded mid-sentence in the stored abstract; kept verbatim. The emissions pathway is described, not named (no RCP/SSP).",
        },
        {
            "claim_text": "A cited study showed low-income countries will bear a greater burden of severe heat events than high-income countries, even if warming targets below 1.5 °C are met.",
            "claim_type": "background_citation",
            "concept": D("burden of severe heat events; \"temperature of equivalence\"", "explicit"),
            "relation_or_direction": D("greater burden in low-income than high-income countries", "explicit"),
            "geography": G("low-income countries versus high-income countries", "explicit", "background context"),
            "temporal_frame": UNKNOWN,
            "scenario": D("target temperatures of less than 1.5°C are met", "explicit"),
            "experimental_condition": UNKNOWN,
            "evidence": E("introduction", "demonstrated that low-income countries will bear a greater burden of severe heat events compared to high-income countries, even if target temperatures of less than 1.5°C are met 4,5 ."),
            "notes": "Attributed to references 4 and 5; a warming target, recorded under scenario as stated.",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("history of cardiac disease", "These will include the WBGT, the Universal Thermal Climate Index, the apparent temperature and the heat index."),
            "reason": "Planned calculation of heat stress indices in a protocol; no result.",
        },
        {
            "evidence": E("abstract", "We will recruit 125 pregnant women of all ages who perform agricultural work during their pregnancy."),
            "reason": "Study design, not a finding.",
        },
        {
            "evidence": E("history of cardiac disease", "Based on published literature, we expect around 35% of agricultural workers to experience heat strain and assume this incidence risk remains at least as high in pregnancy 49,50 ."),
            "reason": "A planning assumption for the sample size, not a finding.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "A protocol with no results; every promoted claim is background attributed to cited work. Most fields repeat sentences (an extraction artifact); spans use the first occurrence. The study area is West Kiang district / Keneba, The Gambia.",
}

# ---------------------------------------------------------------------------
# LIT2-000315 (225397451) --- extreme_heat_v1 rank 42
_TIME_315 = D(
    "contemporary conditions (forcings and boundary conditions circa year 2000; 30 analysed model years)", "explicit",
    E("methods", "The No-irrig and Irrigated simulations were each run for 31 years, maintaining the forcings and boundary conditions at the values from circa 2000."),
)
_EXP_315 = D(
    "two GISS ModelE v2.1 simulations, 'No-irrig' and 'Irrigated' (year-2000 irrigation forcing), fixed SSTs", "explicit",
    E("methods", "We conducted two simulations using the latest version (v2.1) of the Goddard Institute for Space Studies (GISS) climate model, ModelE [23]."),
)
_GEO_315_HOT = G(
    "hot land locations and months globally (90th percentile of daily maximum T w at least 27 °C)", "explicit",
    "analysis domain (global hot land areas)",
    E("methods", "Hot locations and months were defined as ones where the 90th percentile of daily maximum T w is at least 27 • C"),
)
ITEMS["LIT2-000315"] = {
    "bibliographic": {
        "title": "$.title",
        "note": "The stored title carries the venue name and page labels: 'Environmental Research Letters ... OPEN ACCESS RECEIVED'. The venue is not recorded as a bibliographic field because no field holds only it.",
    },
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper estimates, with a global climate model, how irrigation changes humid heat "
        "extremes (wet-bulb temperature) and the frequency of dangerous humid heat."
    ),
    "scope_evidence": E("abstract", "We analyzed global climate model results over hot locations and seasons at high temporal resolution to estimate the impact of irrigation on humid heat extremes, quantified as different percentiles of wet-bulb temperature (T w ), under contemporary conditions."),
    "claims": [
        {
            "claim_text": "Over hot land areas and months, irrigation lowered median daily maximum temperature by about 0.1 °C but slightly raised median wet-bulb temperature (about 0.03 °C), with no significant change in its 90th or 99th percentiles.",
            "claim_type": "finding",
            "concept": D("median daily maximum temperature; wet-bulb temperature (T w) percentiles; irrigation", "explicit"),
            "relation_or_direction": D("temperature decrease ~0.1 °C; T w,50 increase ~0.03 °C; no significant change at 90th/99th", "explicit"),
            "geography": _GEO_315_HOT,
            "temporal_frame": _TIME_315,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_315,
            "evidence": E("results", "The cooling and higher humidity combine to yield a slight increase of~0.03 • C in median wet-bulb temperature (T w,50 ), but no significant change in the 90th or 99th percentiles ( figure 3)."),
            "notes": "The ~0.1 °C temperature decrease is in the preceding sentence: 'irrigation results in a decrease of~0.1 • C in median daily maximum temperature'.",
        },
        {
            "claim_text": "In central North America's Mississippi valley, irrigation produced significant increases of 0.3-0.5 °C in the 50th, 90th and 99th percentile wet-bulb temperatures, with no change in median temperature.",
            "claim_type": "finding",
            "concept": D("wet-bulb temperature percentiles; dew point; irrigation", "explicit"),
            "relation_or_direction": D("significant increases of 0.3-0.5 °C; no change in median temperature; increase in dew point", "explicit"),
            "geography": G("Central North America's Mississippi valley", "explicit", "analysis region (hot land region)"),
            "temporal_frame": _TIME_315,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_315,
            "evidence": E("results", "Central North America's Mississippi valley, some of which is irrigated, shows no change in median temperature and an increase in dew point, and significant increases of 0.3-0.5 • C in 50th, 90th, and 99th percetile wet bulb temperatures."),
            "notes": "'percetile' is the source's spelling.",
        },
        {
            "claim_text": "Irrigation raised the frequency of dangerous wet-bulb temperatures (≥27 °C) by half a day per year over hot areas, nearly doubling it in the Mississippi Valley (4 to 7 days) and decreasing it about 6% over the Ganges.",
            "claim_type": "finding",
            "concept": D("frequency of dangerous conditions with T w ≥ 27 °C", "explicit"),
            "relation_or_direction": D("+0.5 day/year overall (22.6 to 23.1); almost doubling in the Mississippi Valley; +10-20% Arabia and Indus; -6% Ganges", "explicit"),
            "geography": G("hot areas overall; the Mississippi Valley region; Arabia; the Indus Basin; the Ganges Basin", "explicit", "analysis regions"),
            "temporal_frame": _TIME_315,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_315,
            "evidence": E("results", "Dangerous conditions with T w ≥ 27 • C slightly increased in frequency overall in hot areas due to irrigation, by a half day per year (going from 22.6 to 23.1 days) or 2% (figure 6)."),
            "notes": "The regional changes are in the next sentence of the same field.",
        },
        {
            "claim_text": "Extremely dangerous wet-bulb conditions (≥30 °C) showed no significant overall change with irrigation, but increased significantly over Arabia (3.5 to 4.2 days/year) and decreased in the Indus basin (0.2 to 0.1).",
            "claim_type": "finding",
            "concept": D("frequency of extremely dangerous conditions with T w ≥ 30 °C", "explicit"),
            "relation_or_direction": D("no significant overall change; increase over Arabia; decrease in the Indus basin", "explicit"),
            "geography": G("hot regions overall; Arabia; the Indus basin", "explicit", "analysis regions"),
            "temporal_frame": _TIME_315,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_315,
            "evidence": E("results", "Extremely dangerous conditions with T w ≥ 30 • C (not shown; 2.6 days per year overall in hot regions) showed no significant change in frequency due to irrigation overall, but increased significantly over Arabia (from 3.5 to 4.2 days per year), while decreasing significantly in the Indus basin (0.2 to 0.1 days per year)."),
            "notes": None,
        },
        {
            "claim_text": "A cited regional modelling study of California and Nebraska found mean heat index decreased less than mean temperature in irrigated areas, and peak heat index, unlike peak temperature, did not decrease under irrigation.",
            "claim_type": "background_citation",
            "concept": D("mean heat index, which combines temperature and humidity; peak heat index; irrigation", "explicit"),
            "relation_or_direction": D("mean heat index decreased less than mean temperature; peak heat index did not decrease", "explicit"),
            "geography": G("California and Nebraska", "explicit", "study area of the cited study"),
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("introduction", "Lobell et al [21] studied heat extremes in California and Nebraska using regional climate modeling, finding that mean heat index, which combines temperature and humidity, decreased less in irrigated areas than mean temperature, and that the peak heat index value, unlike peak temperature, did not decrease under irrigation."),
            "notes": "Attributed to Lobell et al [21].",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("introduction", "Ambient T w of 35 • C, which could become widespread under greenhouse warming from continued high rates of fossil fuel burning, makes lethal overheating inevitable even at rest [16]."),
            "reason": "Cited, hedged ('could become') statement about future warming; no named scenario or horizon.",
        },
        {
            "evidence": E("methods", "the approximate threshold for dangerously hot conditions in the US National Weather Service classification based on heat index"),
            "reason": "Definition of the analysis threshold, not a finding.",
        },
        {
            "evidence": E("discussion and conclusions", "particularly in places like California where topographic variation is large [60,61]"),
            "reason": "A limitation remark about model resolution, not a finding.",
        },
    ],
    "terminal_status": "claims_extracted",
}

# ---------------------------------------------------------------------------
# LIT2-000470 (237371886) --- extreme_heat_v1 rank 56
_GEO_470 = G(
    "the US workers (US workplaces)", "explicit", "target population of the recommendations",
    E("abstract", "The purpose of this consensus document was to develop feasible, evidence-based occupational heat safety recommendations to protect the US workers that experience heat stress."),
)
ITEMS["LIT2-000470"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "A Delphi consensus of 51 experts producing occupational heat safety recommendations to "
        "protect US workers from heat stress and heat-related illness."
    ),
    "scope_evidence": E("abstract", "Heat safety recommendations were created to protect worker health and to avoid productivity losses associated with occupational heat stress."),
    "claims": [
        {
            "claim_text": "After two rounds of Delphi scoring, the 59 originally developed recommendations were reduced to 40 occupational heat safety recommendations across eight topics.",
            "claim_type": "finding",
            "concept": D("occupational heat safety recommendations (Delphi consensus)", "explicit"),
            "relation_or_direction": D("59 originally developed; 40 retained after two rounds of scoring", "explicit"),
            "geography": _GEO_470,
            "temporal_frame": D("roundtable meeting December 10, 2020", "explicit",
                                E("methods", "A virtual meeting was held on December 10, 2020")),
            "scenario": UNKNOWN,
            "experimental_condition": D("Delphi method; each recommendation scored 0-9 on scientific evidence, feasibility and clarity; retained if average 7 or higher", "explicit",
                                        E("methods", "Recommendations that received an average score 7 or higher for each category were transferred to the final version of the manuscript.")),
            "evidence": E("results: recommendations", "Following the round table meeting, 59 recommendations were originally developed. After two rounds of scoring, the Delphi method resulted in 40 recommendations across all eight topics"),
            "notes": "A result of the consensus process, not an observation of heat or health.",
        },
        {
            "claim_text": "Employers or supervisors should create and implement a gradual, progressive heat acclimatization program of 5-7 days to minimize the effects of heat stress (evidence level B).",
            "claim_type": "recommendation",
            "concept": D("heat acclimatization (HA) program; effects of heat stress", "explicit"),
            "relation_or_direction": D("should create and implement (5-7 days) to minimize effects", "explicit"),
            "geography": _GEO_470,
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("narrative review", "#1: Employers/supervisors should create and implement a gradual, progressive HA program (5-7 days) to minimize the effects of heat stress"),
            "notes": "The SORT grade 'B' follows the recommendation in the source table text.",
        },
        {
            "claim_text": "Environmental heat measurements should be taken on-site, as close to the individual work site as possible, to best represent environmental heat stress (evidence level A).",
            "claim_type": "recommendation",
            "concept": D("environmental monitoring of heat stress", "explicit"),
            "relation_or_direction": D("should be taken on-site, as close to the work site as possible", "explicit"),
            "geography": _GEO_470,
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("narrative review", "#1: Environmental measurements should be taken on-site-as close to the individual work site as possible-to best represent environmental heat stress."),
            "notes": "The SORT grade 'A' follows in the source table text.",
        },
        {
            "claim_text": "About 13.3 million US workers performed work in extreme heat every day in July 2017.",
            "claim_type": "background_citation",
            "concept": D("work in extreme heat", "explicit"),
            "relation_or_direction": D("approximately 13.3 million workers every day", "explicit"),
            "geography": G("US", "explicit", "background context (national)"),
            "temporal_frame": D("July 2017", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("introduction", "Approximately 13.3 million US workers performed work in extreme heat every day in July 2017 (Tanglis, 2018)."),
            "notes": "Attributed to Tanglis (2018).",
        },
        {
            "claim_text": "California, Washington and Minnesota are the only three US states that enforce OSHA-approved heat safety standards.",
            "claim_type": "background_citation",
            "concept": D("OSHA-approved heat safety standards (state enforcement)", "explicit"),
            "relation_or_direction": D("the only three states that enforce", "explicit"),
            "geography": G("California, Washington, and Minnesota", "explicit", "regulatory context (states with heat standards)"),
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("introduction", "California, Washington, and Minnesota are the only three states in the United States that enforce Occupational Safety and Health Administration (OSHA)-approved heat safety standards (NI-OSH, 2016)."),
            "notes": "Attributed to NIOSH (2016). A policy fact, not a hazard measurement.",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("introduction", "In 2016, the partnership updated a heat safety mobile application that provides safety recommendations based on heat index"),
            "reason": "Background on a tool; not a finding.",
        },
        {
            "evidence": E("narrative review", "Further, in certain hot and dry locations, air temperature alone is more appropriate to use than a heat index in determining necessary interventions to prevent heat-related illness (Anderson et al., 2013)."),
            "reason": "Cited methodological guidance without place; beyond the five-claim cap.",
        },
        {
            "evidence": E("introduction", "reported that 35% of workers experienced occupational heat strain during or following the work shift, while 30% of workers reported productivity losses"),
            "reason": "A cited meta-analysis result with no geography; beyond the five-claim cap.",
        },
        {
            "evidence": E("introduction", "Many workers have been at high risk of heat-related illness and death at worksites for decades, and the conditions are being exacerbated by rising temperatures related to climate change (Moda et al., 2019)."),
            "reason": "General background attributed to a reference; no horizon or scenario.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "The 'narrative review' field holds several sections and table text run together; recommendation numbers restart per topic, so '#1' occurs many times — each quote includes enough text to be unique at its first occurrence.",
}

# ---------------------------------------------------------------------------
# LIT2-000662 (250039675) --- extreme_heat_v1 rank 70
_GEO_662 = G(
    "49 cities of the U.S. (contiguous United States; grouped into West, South and North regions)", "explicit",
    "study area (city sample)",
    E("discussion", "Spearman correlation analysis within the 49 cities in the U.S. revealed that the heat wave duration and intensity changes are significantly linked to UEII."),
)
_TIME_662 = D(
    "land cover 1992 and 2019 (27 years)", "explicit",
    E("results", "In this study, the UEII was determined for 27 years."),
)
_EXP_662 = D(
    "heat wave defined as minimum apparent temperature above the local 85th percentile for two or more days; Spearman correlations with UEII/GEII", "explicit",
    E("materials and methods", "In this study, a heat wave is defined as any minimum apparent temperature that exceeds the local 85th percentile for two or more days in a row."),
)
ITEMS["LIT2-000662"] = {
    "bibliographic": {"note": "No `title` key; no field holds a title, authors, year or venue."},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper correlates urban and green-space expansion in 49 US cities with changes in "
        "heat wave frequency, duration, season and intensity, i.e. a heat hazard and its land-use "
        "drivers."
    ),
    "scope_evidence": E("introduction", "This study aimed to examine how changing land use conditions is related to the occurrence of heat waves."),
    "claims": [
        {
            "claim_text": "Across 49 US cities, the urban expansion intensity index was positively and significantly correlated with heat wave intensity change (Spearman 0.317, p = 0.02699) and negatively correlated with duration change.",
            "claim_type": "finding",
            "concept": D("urban expansion intensity index (UEII); heat wave intensity change; heat wave duration change", "explicit"),
            "relation_or_direction": D("positive and significant with intensity change (0.317); negative with duration change", "explicit"),
            "geography": _GEO_662,
            "temporal_frame": _TIME_662,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_662,
            "evidence": E("discussion", "However, UEII was positively and significantly (p = 0.02699) related to heat wave intensity, with the Spearman correlation coefficient of 0.317."),
            "notes": "The negative duration correlation is two sentences earlier: 'In this study, duration change was negatively correlated with UEII.'",
        },
        {
            "claim_text": "In the West region, UEII showed a significant positive correlation with heat wave intensity change (coefficient 0.64, p = 0.03).",
            "claim_type": "finding",
            "concept": D("UEII; heat wave intensity change", "explicit"),
            "relation_or_direction": D("significant and positive (0.64, p = 0.03)", "explicit"),
            "geography": G("the West region (12 cities, e.g. Seattle, Las Vegas, Fresno)", "explicit", "analysis region"),
            "temporal_frame": _TIME_662,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_662,
            "evidence": E("discussion", "The West region shows a significant and positive correlation only between UEII and intensity change. The coefficient value is 0.64 and the p-value is 0.03."),
            "notes": None,
        },
        {
            "claim_text": "The green expansion intensity index was not significantly related to heat wave frequency, duration, season or intensity.",
            "claim_type": "finding",
            "concept": D("green expansion intensity index (GEII); heat wave frequency, duration, season, and intensity", "explicit"),
            "relation_or_direction": D("relationships not statistically significant", "explicit"),
            "geography": _GEO_662,
            "temporal_frame": _TIME_662,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_662,
            "evidence": E("discussion", "However, the relationships between GEII and heat wave frequency, duration, season, and intensity were not statistically significant in this study."),
            "notes": None,
        },
        {
            "claim_text": "Urban expansion outpaced green expansion in the 49 cities: the mean annual GEII was 0.017% against a mean UEII of 1.5%.",
            "claim_type": "finding",
            "concept": D("green expansion versus urban expansion (GEII, UEII)", "explicit"),
            "relation_or_direction": D("mean GEII 0.017% versus mean UEII 1.5% per year", "explicit"),
            "geography": _GEO_662,
            "temporal_frame": _TIME_662,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("discussion", "The mean GEII of 0.017% and the mean UEII of 1.5% indicate that the urban expansion is more evident than green expansion in the 49 cities of the U.S. as an annual average."),
            "notes": "A land-use result supporting the heat analysis; not itself a heat measurement.",
        },
        {
            "claim_text": "A cited study found 2000-2010 heat-related worker fatality rates of 0.37, 0.33 and 0.24 per million workers per year in Florida, Texas and California, among the top ten states.",
            "claim_type": "background_citation",
            "concept": D("heat-related fatality rates (workers)", "explicit"),
            "relation_or_direction": D("0.37, 0.33, and 0.24 per million workers per year; among the top ten states", "explicit"),
            "geography": G("Florida, Texas, and California", "explicit", "study area of the cited study"),
            "temporal_frame": D("from 2000 to 2010", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("results", "They showed that the rates in Florida, Texas, and California were 0.37, 0.33, and 0.24 per million workers per year, respectively, which are listed among the top ten states."),
            "notes": "Attributed to Gubernot et al. [46].",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("materials and methods", "An excessive heat event (EHE) is defined by the NCDC (National Climatic Data Center) heat index as any day where the"),
            "reason": "A definition carried over from the source data; not a finding.",
        },
        {
            "evidence": E("conclusion", "The results imply that the cities would be better in a more compact pattern with more expanded green areas to mitigate the negative health impacts of heat waves on citizens in urban areas."),
            "reason": "An implication the paper draws although its GEII correlations were not significant; not promoted.",
        },
        {
            "evidence": E("introduction", "They proposed that in a city with a relatively compact urban spatial form, heat waves occur on fewer days."),
            "reason": "A cited result (Stone and Rodgers); beyond the five-claim cap.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "The heat wave data are taken from Habeeb et al. [12] (50 cities, San Juan dropped). The 'conclusion' field ends mid-word ('Different analytical ap-').",
}

# ---------------------------------------------------------------------------
# LIT2-000803 (257854681) --- extreme_heat_v1 rank 84
ITEMS["LIT2-000803"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "ambiguous",
    "scope_reason": (
        "The paper examines how outdoor PM2.5 air pollution limits natural-ventilation cooling "
        "hours in Indian informal settlements; heat appears through heat-index comfort thresholds "
        "and passing mentions of heat waves and heat stress, but no heat hazard or its impacts is "
        "itself examined."
    ),
    "scope_evidence": E("abstract", "Here, we propose a modeling approach that integrates highly granular air pollution data with a coupled EnergyPlus and differential equation airflow model to evaluate how NV potential for space cooling changes when accounting for air pollution exposure (PM2.5)."),
    "claims": [],
    "rejected_or_ambiguous": [
        {
            "evidence": E("results", "We observe an average reduction of 57% in NV potential for the NAAQS Scenarios-II A, II B and II C and a decrease of 90% for the WHO Scenarios-III A, III B and III C compared to the corresponding baseline scenarios."),
            "reason": "The paper's main result concerns air-pollution limits on ventilation hours in New Delhi; air pollution is not a climate or weather hazard. Kept as ambiguous, not promoted. The 'Scenarios' are air-quality operating rules, not climate scenarios.",
        },
        {
            "evidence": E("results", "On the other hand, during the summer, high temperatures drive the unfavorable conditions for NV especially during daytime as heat index levels greater than 39 • C are extremely unsafe for the occupants as shown in figure 9(B)."),
            "reason": "Uses heat index as a thermal-comfort control rule for a typical summer day in New Delhi; heat is a constraint on ventilation, not the object of study.",
        },
        {
            "evidence": E("abstract", "Amidst rising heat waves pushing temperatures beyond 110 • F in the country [14], cooling energy demand for India is projected to grow around 2.2 times in 2027 and around 8 times by 2037-38 [11]."),
            "reason": "Cited background on heat waves and cooling demand in India; not this paper's evidence.",
        },
        {
            "evidence": E("introduction", "studied the impact of PM2.5 specifically on the potential for NV cooling of office buildings for five locations in California, nine European cities and three megacities in Asia [30][31][32]."),
            "reason": "A cited air-quality/ventilation study; California appears only as a location of other work.",
        },
    ],
    "terminal_status": "ambiguous_only",
    "notes": "The 'abstract' field also holds part of the introduction and a publisher line; several fields repeat passages. Study cities: New Delhi and Bangalore.",
}

# ---------------------------------------------------------------------------
# LIT2-000927 (266658220) --- extreme_heat_v1 rank 98
_GEO_927 = G(
    "the 52 districts in South Africa", "explicit", "study area",
    E("introduction", "while adjusting for population in each of the 52 districts in South Africa"),
)
_TIME_927 = D(
    "1997 to 2013, summer months (October to March)", "explicit",
    E("abstract", "The mortality dataset contained records of daily registered deaths (n = 8,476,532) from 1997 to 2013 and data for the temperature indices were for the same period."),
)
_EXP_927 = D(
    "district-level distributed lag nonlinear models (quasi-Poisson), population-adjusted; threshold regression", "explicit",
    E("statistical analysis", "a distributed lag nonlinear model (DLNM) using a quasi-Poisson regression model was implemented to express the nonlinear exposure-lag-response relationship"),
)
ITEMS["LIT2-000927"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper estimates temperature-mortality associations and district heat thresholds "
        "for South Africa to inform a heat-health warning system, i.e. the health impacts of "
        "extreme heat."
    ),
    "scope_evidence": E("abstract", "This study contributes to the development of a HHWS for South Africa that can potentially minimize heat-related mortality."),
    "claims": [
        {
            "claim_text": "Maximum temperature was the most statistically significant predictor of all-cause summer mortality in 40 of 52 South African districts (77%), ahead of minimum temperature (7 districts) and diurnal temperature range (3).",
            "claim_type": "finding",
            "concept": D("maximum temperature, minimum temperature, diurnal temperature range; all-cause mortality", "explicit"),
            "relation_or_direction": D("maximum temperature most significant in 40 (77%) districts; minimum 7 (13%); DTR 3 (6%)", "explicit"),
            "geography": _GEO_927,
            "temporal_frame": _TIME_927,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_927,
            "evidence": E("dlnm", "Maximum temperature was the most statistically significant temperature metric in 40 (77%) districts out 52 (Table 1)."),
            "notes": "The minimum-temperature and DTR counts are two sentences later in the same field.",
        },
        {
            "claim_text": "Maximum temperature was associated with increased risk of mortality in all but three of the South African districts.",
            "claim_type": "finding",
            "concept": D("maximum temperature; risk of mortality", "explicit"),
            "relation_or_direction": D("increased risk in all but three districts", "explicit"),
            "geography": _GEO_927,
            "temporal_frame": _TIME_927,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_927,
            "evidence": E("abstract", "Maximum temperature was associated with increased risk of mortality in all but three of the districts."),
            "notes": None,
        },
        {
            "claim_text": "District maximum-temperature mortality thresholds followed climate zones: the hot arid Northern Cape and North West averaged 33.31 and 33.05, versus 27.92 in Mpumalanga and 26.37 in the Eastern Cape.",
            "claim_type": "finding",
            "concept": D("district-level maximum temperature thresholds above which daily mortality increases", "explicit"),
            "relation_or_direction": D("highest in hot arid interior provinces; lower in temperate interior and coastal provinces", "explicit"),
            "geography": G("Northern Cape and North West (hot arid interior); Mpumalanga (temperate interior); Eastern Cape (coast) — provinces of South Africa", "explicit", "study area (provincial averages)"),
            "temporal_frame": _TIME_927,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_927,
            "evidence": E("threshold regression", "Figure 1 shows that, on average, districts located in the hot arid interior provinces of the Northern Cape and the North West had the highest thresholds (provincial average of 33.31 and 33.05) compared to districts located in the temperate interior (Mpumalanga province) and along the coast (Eastern Cape province) 27.92 and 26.37, respectively."),
            "notes": "Units are not stated in this sentence (the thresholds are maximum temperatures, presumably °C, not asserted here).",
        },
        {
            "claim_text": "The study recommends a heat-health warning system for South Africa that issues heat alerts using district-level maximum temperature thresholds.",
            "claim_type": "recommendation",
            "concept": D("heat-health warning system (HHWS); district-level maximum temperature thresholds", "explicit"),
            "relation_or_direction": D("recommends incorporating thresholds to issue heat alerts", "explicit"),
            "geography": G("South Africa", "explicit", "target of the recommendation"),
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("conclusion", "Based on the findings, this study recommends a HHWS incorporating district-level maximum temperature thresholds to issue heat alerts."),
            "notes": None,
        },
        {
            "claim_text": "A cited study found the US National Weather Service's national heat index alert threshold of 40.1 °C ineffective in California's desert communities, where it was regularly exceeded by well-adapted residents.",
            "claim_type": "background_citation",
            "concept": D("the national heat index threshold of 40.1 °C used by the US National Weather Service to issue heat alerts", "explicit"),
            "relation_or_direction": D("found to be ineffective; regularly exceeded; residents well adapted", "explicit"),
            "geography": G("the desert communities of California", "explicit", "study area of the cited study"),
            "temporal_frame": UNKNOWN,
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("discussion", "For example, the national heat index threshold of 40.1 °C used by the US National Weather Service to issue heat alerts was found to be ineffective in the desert communities of California."),
            "notes": "Attributed to Guirguis et al. (2014).",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("introduction", "In 2006 in the USA, California (which was the most affected state) recorded 655 heat-related deaths over 2 weeks"),
            "reason": "Background figure attributed to other studies; beyond the five-claim cap.",
        },
        {
            "evidence": E("introduction", "Climate change is projected to intensify the adverse health impacts of extreme heat by increasing their frequency, severity, and duration of heatwave events (Ebi et al. 2021;Zhao et al. 2022)."),
            "reason": "Cited projection; no scenario, horizon or place.",
        },
        {
            "evidence": E("discussion", "The findings of our study relating to the high maximum temperature thresholds for hot regions indicate population adaptation to local climate."),
            "reason": "An interpretation (adaptation) not tested in the study.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "Several fields end mid-sentence in the source ('Buffalo City (Eastern Cape), Cape Winelands', 'These are among the hottest').",
}

# ---------------------------------------------------------------------------
# LIT2-001075 (272852900) --- extreme_heat_v1 rank 112; = LITCORPUS-00 LIT-001536 (prior exposure)
_GEO_1075 = G(
    "1,614 prisons in the United States", "explicit", "study area (facility sample)",
    E("abstract", "We leveraged a high-resolution air temperature data set to evaluate short and long-term patterns of heat metrics for 1,614 prisons in the United States from 1990 to 2023."),
)
_TIME_1075_ST = D(
    "summers (1 June-31 August) 2020-2023", "explicit",
    E("materials and methods", "We then calculated four heat exposure metrics at individual prisons from the daily summer air temperature measurements averaged for the years 2020-2023"),
)
_TIME_1075_2019 = D(
    "summer 2019 (to match the 2019 facility census)", "explicit",
    E("materials and methods", "we used the 2019 summer 90th percentile of daily max air temperature to match with the year of BJSCensus2019"),
)
_EXP_1075 = D(
    "modelled air temperature (Daymet v4, 1-km daily grid)", "explicit",
    E("materials and methods", "We obtained daily outdoor air temperatures on a 1-km grid for 1990-2023 from the freely available Daymet v4 Surface Weather and Climatological summaries"),
)
ITEMS["LIT2-001075"] = {
    "bibliographic": {"title": "$.title"},
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "The paper characterizes summer heat exposure, vulnerability and heat-related mortality "
        "risk at 1,614 US prisons, i.e. exposure to and impacts of a heat hazard."
    ),
    "scope_evidence": E("abstract", "Evaluating heat exposure in prisons, and the characteristics of exposed populations and prisons, can elucidate prison-level risk to heat exposure."),
    "claims": [
        {
            "claim_text": "From 2020 to 2023, 67.3% of US prison facilities, in 44 states and the District of Columbia, had at least one day with daily mean temperature over 85 °F.",
            "claim_type": "finding",
            "concept": D("days with daily mean temperature over 85°F at prisons", "explicit"),
            "relation_or_direction": D("67.3% of facilities had at least one such day", "explicit"),
            "geography": G("prisons in 44 states and the District of Columbia (United States)", "explicit", "study area (facility sample)",
                           E("results", "in 44 states and the District of Columbia")),
            "temporal_frame": D("2020 to 2023", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_1075,
            "evidence": E("results", "The majority (67.3%) of facilities (at least 986,145 incarcerated people and 222,154 staff) in 44 states and the District of Columbia had at least one day that the daily mean temperature was over 85°F from 2020 to 2023 (Figure 1a)."),
            "notes": "Temperatures are modelled (Daymet), not station observations.",
        },
        {
            "claim_text": "The ten most heat-exposed prisons by 2020-2023 summer 90th percentile temperature were in California, Arizona and Nevada; the maximum, 116.1 °F, was at Calipatria State Prison in California.",
            "claim_type": "finding",
            "concept": D("location-specific 90th percentile summer temperature at prisons", "explicit"),
            "relation_or_direction": D("top 10 in California, Arizona and Nevada; maximum 116.1°F; mean 93.6°F", "explicit"),
            "geography": G("California, Arizona and Nevada (top 10 facilities); Calipatria State Prison in California", "explicit", "facilities ranked within the study area"),
            "temporal_frame": _TIME_1075_ST,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_1075,
            "evidence": E("results", "The top 10 most heat-exposed facilities were in California, Arizona and Nevada (Figure 1b)."),
            "notes": "The maximum is the next sentence: 'The facility with the maximum value (116.1°F) was Calipatria State Prison in California'.",
        },
        {
            "claim_text": "Relative to 1990-2019, the highest 2020-2023 summer temperature anomalies occurred at prisons in Washington, California, Maine, Idaho and Texas, with a maximum of 4.1 °F and a mean of 0.7 °F.",
            "claim_type": "finding",
            "concept": D("anomaly in average 90th percentile summer temperature at prisons", "explicit"),
            "relation_or_direction": D("highest anomalies at prisons in the named states; maximum 4.1°F; mean 0.7°F", "explicit"),
            "geography": G("prisons in Washington, California, Maine, Idaho, and Texas", "explicit", "facilities ranked within the study area"),
            "temporal_frame": D("2020-2023 compared with a 1990-2019 summer average", "explicit",
                                E("results", "Figure 2 shows the spatial pattern of anomalies in the average 90th percentile summer temperature for prisons from 2020 to 2023 when compared to a 1990-2019 averaged summer 90th percentile.")),
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_1075,
            "evidence": E("results", "The highest facility-level temperature anomalies occurred at prisons in Washington, California, Maine, Idaho, and Texas."),
            "notes": None,
        },
        {
            "claim_text": "In 2019, the ten most heat-exposed US prisons had 8.6% higher proportions of nonwhite, non-Hispanic and 15.0% higher proportions of Hispanic or Latino incarcerated people than the ten least exposed.",
            "claim_type": "finding",
            "concept": D("heat exposure (90th percentile summer temperature) by race/ethnicity of incarcerated populations", "explicit"),
            "relation_or_direction": D("+8.6% nonwhite, non-Hispanic; +15.0% Hispanic or Latino in the top 10 versus lowest 10", "explicit"),
            "geography": G("Across the US (prisons with the top and lowest 10 heat exposures)", "explicit", "study area (national comparison)"),
            "temporal_frame": _TIME_1075_2019,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_1075,
            "evidence": E("results", "Across the US, the prisons with the top 10 heat exposures had 8.6% higher proportions of nonwhite, non-Hispanic incarcerated populations than the lowest 10 prisons (Figure 4)."),
            "notes": "The Hispanic figure is in the same field: 'The prisons with the top 10 heat exposures also had 15.0% higher proportions of Hispanic or Latino incarcerated populations than the lowest 10 prisons'.",
        },
        {
            "claim_text": "Nine of 17 facility-level characteristics hypothesized to modify heat risk had significantly higher heat exposure in 2019; for example, privately operated prisons had 2.7 °F higher exposure than public ones.",
            "claim_type": "finding",
            "concept": D("heat exposure by facility-level characteristics that could modify risk to heat", "explicit"),
            "relation_or_direction": D("9 of 17 significantly higher (p < 0.05); private +2.7°F", "explicit"),
            "geography": _GEO_1075,
            "temporal_frame": _TIME_1075_2019,
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_1075,
            "evidence": E("results", "Nine of the 17 test variables had statistically significant (p < 0.05) higher heat exposures for the groups with hypothesized effects on heat risk"),
            "notes": "The private-operator difference is in the same field: 'Post-hoc tests found that prisons that were operated privately had higher (+2.7°F) heat exposure than public facilities.'",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("results", "The next highest prison heat exposures averaged state-wide were in Nevada, Texas, Oklahoma, Utah, Kansas, New Mexico and Louisiana (Figure S2 in Supporting Information S1)."),
            "reason": "A state ranking subsidiary to claim C2's facility ranking; beyond the five-claim cap.",
        },
        {
            "evidence": E("discussion", "a national study on heat-related mortality in prisons determined that neither heat index or wet bulb globe temperature better capture the relationship between heat and total mortality in the incarcerated population (Skarha et al., 2023)."),
            "reason": "A cited result used to justify the exposure metric; not this paper's evidence.",
        },
        {
            "evidence": E("results", "Each of these days may be associated with a 5.2% increase in total mortality for the prison population, on average (Skarha et al., 2023)."),
            "reason": "Applies a cited risk ratio; mortality is not estimated here. Hedged ('may').",
        },
        {
            "evidence": E("introduction", "For example, while the provision of air conditioning (AC) has been shown to effectively eliminate heat-related mortality in Texas prisons (Skarha et al., 2022), 44 states including Texas do not universally provide access to air conditioning in prisons (Santucci et al., 2022)."),
            "reason": "Background attributed to other studies.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "Prior exposure: this item is LITCORPUS-00 LIT-001536, read twice in M4-WP2. It was re-read here from its source bytes; no WP2 artifact, document or bridge file was opened. The methods cite 'Stephan, 2008' for prison construction dates.",
}

# ---------------------------------------------------------------------------
# LIT2-001160 (53109236) --- extreme_heat_v1 rank 126
_EXP_1160_P90 = D(
    "heatwave defined by daily temperature above the 90th percentile of the long-term distribution for each grid and calendar day, at least four consecutive days (CPC 0.5° daily data)", "explicit",
    E("european heatwave (summer 2003", "as defined by minimum daily temperature exceeding 90 th percentile of long-term distribution of TMIN for each day and each grid for at least four consecutive days"),
)
ITEMS["LIT2-001160"] = {
    "bibliographic": {
        "title": "$.title",
        "note": "The stored title carries the labels 'Data Descriptor:' and 'Background & Summary'.",
    },
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "A data descriptor for a multi-method global heatwave and warm-spell record, introducing a "
        "standardized heat index and validating it on high-impact historical heatwaves."
    ),
    "scope_evidence": E("abstract", "Heatwaves are extended periods of unusually high temperatures with significant societal and environmental impacts."),
    "claims": [
        {
            "claim_text": "With a constant threshold (daily maximum above 35 °C for at least four days), Chicago and the Midwest had about 5 heatwave days in July 1995, while parts of western Arizona and southeast California counted all 31 days.",
            "claim_type": "finding",
            "concept": D("frequency of heatwave days under a constant temperature threshold", "explicit"),
            "relation_or_direction": D("around 5 days in the Midwest/Chicago; much more frequent in the South and Southwest US; entire month in some regions", "explicit"),
            "geography": G("Midwest US, specifically Chicago; South and Southwest US; west of Arizona and southeast of California", "explicit", "validation case region (July 1995 heatwave)"),
            "temporal_frame": D("July of 1995", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": D("maximum daily temperatures above 35°C with a duration of at least four consecutive days", "explicit"),
            "evidence": E("chicago heatwave (july 1995", "While Midwest US, and specifically Chicago, experienced around 5 heatwave days in July of 1995 according to this definition, heatwave days were much more frequent in South and Southwest US."),
            "notes": "The 31-day statement is the next sentence: 'Indeed, the entire month of July, 1995 (31 days) is categorized as heatwave days for some regions in the west of Arizona and southeast of California in this category.' The paper uses this to argue for local thresholds.",
        },
        {
            "claim_text": "In July-August 2003, some western European locations had around 45 night-time heatwave days, and peak night-time temperature exceeded 30 °C in an extended region around Paris.",
            "claim_type": "finding",
            "concept": D("frequency of heatwave days and heatwave amplitude (daily minimum temperature)", "explicit"),
            "relation_or_direction": D("around 45 heatwave days in two months; amplitude exceeding 30°C around Paris", "explicit"),
            "geography": G("western Europe; an extended region around Paris, France", "explicit", "validation case region (2003 heatwave)"),
            "temporal_frame": D("July and August, 2003", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_1160_P90,
            "evidence": E("european heatwave (summer 2003", "Some locations, interestingly, endure around 45 heatwave days in a two months period."),
            "notes": "The Paris amplitude is in the following sentence of the same field.",
        },
        {
            "claim_text": "In July-August 2010, a large region around Moscow experienced 40+ heatwave days, with heatwave daily maximum temperature amplitude above 45 °C for most of western Russia.",
            "claim_type": "finding",
            "concept": D("frequency of heatwave days; heatwave amplitude (daily maximum temperature)", "explicit"),
            "relation_or_direction": D("40+ heatwave days in two months; amplitude soaring 45+°C", "explicit"),
            "geography": G("A large region surrounding Moscow, Russia; western Russia", "explicit", "validation case region (2010 heatwave)"),
            "temporal_frame": D("July and August, 2010", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": D("daily maximum temperature exceeding the 90th percentile of the long-term TMAX climatology for at least four consecutive days", "explicit",
                                        E("european heatwave (summer 2003", "Heatwave is defined by daily maximum temperature exceeding 90 th percentile of the long-term TMAX climatology for at least four consecutive days for each location and calendar day.")),
            "evidence": E("european heatwave (summer 2003", "A large region surrounding Moscow, Russia, experienced 40+ heatwave days in two months."),
            "notes": "The Russia 2010 text is stored inside the 'european heatwave (summer 2003' field (section headings merged in the source).",
        },
        {
            "claim_text": "For Moscow in late July 2010, the excess heat factor dropped sharply (from about 60 to about 4 °C²) while the standardized heat index fell only moderately (about 2.5 to 1.75), reflecting EHF's acclimation term.",
            "claim_type": "finding",
            "concept": D("excess heat factor (EHF) versus standardized heat index (SHI)", "explicit"),
            "relation_or_direction": D("EHF drastically reduces; SHI shows a more moderate drop", "explicit"),
            "geography": G("Moscow, Russia", "explicit", "validation case (index comparison)"),
            "temporal_frame": D("June-September, 2010 (late July)", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("european heatwave (summer 2003", "In late July as average daily temperature drops from $32°C to $25°C, EHF drastically reduces from $60°C 2 to $ 4°C 2 , whereas SHI shows a more moderate drop from $ 2.5 ( $99 th percentile) to $1.75 ( $96 th percentile)."),
            "notes": "'$' in the stored text stands where '~' (approximately) appears to have been; kept exactly as stored. 'Standardized heat index' is this paper's probabilistic temperature index, not the NWS temperature-humidity heat index.",
        },
        {
            "claim_text": "During the July 1995 heatwave, hospital admissions rose 35% for people aged 65 and older, and multiple studies attributed at least 600 excess deaths to the heat.",
            "claim_type": "background_citation",
            "concept": D("excessive heat and humidity; hospital admission; excess deaths", "explicit"),
            "relation_or_direction": D("admissions increased 35% for the elderly; at least 600 excess deaths", "explicit"),
            "geography": G("Chicago, IL (Midwest US)", "explicit", "validation case region (from cited studies)"),
            "temporal_frame": D("July 1995", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": UNKNOWN,
            "evidence": E("chicago heatwave (july 1995", "Due to the excessive heat and humidity, hospital admission increased 35% for the elderly (65 years and older) 24 ."),
            "notes": "The excess-death figure is the next sentence ('Multiple studies 49,50 attributed at least 600 excess deaths').",
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("usage notes", "For example, warm-spells have induced earlier spring snow melt, which in turn increase western US forest wildfire activity 63 ."),
            "reason": "Cited background; not this paper's evidence.",
        },
        {
            "evidence": E("global heatwave/warm-spell maps", "Karachi, Pakistan, experienced an extreme heatwave in June, 2015, which along with power outage and water distribution system failure, imposed a death toll of 700+ people 62 ."),
            "reason": "Cited impact figure; beyond the five-claim cap.",
        },
        {
            "evidence": E("background & summary", "The GHWR data set is generated using the CPC global air temperature data provided by the NOAA/OAR/ESRL PSD, Boulder, Colorado, USA"),
            "reason": "Data-provider statement, not a finding.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "Several section headings are truncated or merged in the source keys (e.g. 'excess heat factor (ehf', 'european heatwave (summer 2003'). A Russian 2010 subsection is folded into the 2003 field.",
}

# ---------------------------------------------------------------------------
# LIT2-001293 (88523156) --- extreme_heat_v1 rank 140
_GEO_1293_SA = G(
    "the March AFB station, which lies in Riverside County, CA (southern California Santa Ana weather regime)", "explicit",
    "example data site (motivating application)",
    E("mathematical background for approach", "for the March AFB station 1 , which lies in Riverside County, CA"),
)
_GEO_1293_K = G(
    "the Karachi Airport station (Karachi, Pakistan)", "explicit", "example data site (motivating application)",
    E("mathematical background for approach", "this time for the Karachi Airport station."),
)
_EXP_1293_SA = D(
    "HadISD hourly data 1973-2015, September-November; daily windspeed and dryness; bivariate isolines under asymptotic dependence", "explicit",
    E("mathematical background for approach", "The data span the years 1973-2015 and we restrict our attention to the months of September, October, and November"),
)
_EXP_1293_K = D(
    "HadISD data 1973-2015, April-October; temperature and relative humidity at the time of the daily maximum heat index; isolines under asymptotic independence", "explicit",
    E("mathematical background for approach", "For each day, we retain the temperature (converted to Fahrenheit) and relative humidity both at the time of the maximum heat index value which itself is a function of temperature and humidity."),
)
ITEMS["LIT2-001293"] = {
    "bibliographic": {
        "title": "$.title",
        "note": "The 'introduction' field contains an arXiv identifier and date string ('arXiv:1710.05248v1 [stat.ME] 14 Oct 2017'); not recorded as venue or year because no field holds only it.",
    },
    "scope_status": "in_scope_hazard",
    "scope_reason": (
        "Borderline. A statistical methods paper for bivariate exceedance isolines, motivated by "
        "and applied to fire-weather conditions (Santa Ana winds) and a deadly heat wave "
        "(Karachi, June 2015), with results on how rare those hazard conditions were."
    ),
    "scope_evidence": E("introduction", "Here, risk is in terms of human health impacts which worsen by simultaneous hot and humid conditions."),
    "claims": [
        {
            "claim_text": "The temperature-humidity conditions recorded at Karachi airport on 18-23 June 2015 were all rare: every day exceeded the 0.005 joint-exceedance isoline, three exceeded 0.001 and one exceeded 0.0005.",
            "claim_type": "finding",
            "concept": D("joint exceedance probability of temperature and relative humidity (heat wave conditions)", "explicit"),
            "relation_or_direction": D("all exceed the 0.005 isoline; three exceed 0.001; one exceeds 0.0005", "explicit"),
            "geography": _GEO_1293_K,
            "temporal_frame": D("June 18 to June 23, 2015 (relative to a 1973-2015 record)", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_1293_K,
            "evidence": E("mathematical background for approach", "The conditions recorded at the Karachi airport on the dates between June 18 and June 23, 2015 were all rare."),
            "notes": "The counts are in the next sentence. The paper stresses that isolines denote rarity, not impact.",
        },
        {
            "claim_text": "At the March AFB station, the windspeed-dryness combination on the Cedar Fire ignition day was not extremely rare (below the 0.005 isoline), whereas conditions on the Witch Fire day were quite rare.",
            "claim_type": "finding",
            "concept": D("joint exceedance probability of windspeed and dryness (Santa Ana weather regime) on fire ignition days", "explicit"),
            "relation_or_direction": D("Cedar Fire day not extremely rare; Witch Fire day quite rare", "explicit"),
            "geography": _GEO_1293_SA,
            "temporal_frame": D("1973-2015 record, September-November", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_1293_SA,
            "evidence": E("mathematical background for approach", "We see that the combination of windspeed and dryness seen at this weather station on the day corresponding to the Cedar Fire was not extremely rare"),
            "notes": "The Witch Fire statement follows: 'The conditions at this station on the day corresponding to the Witch Fire were quite rare'; the sentence is truncated in the source.",
        },
        {
            "claim_text": "For the Santa Ana data, the estimated tail dependence χ ≈ 0.3 implies conditions are at their driest about 30% of the time when windspeeds are at their highest.",
            "claim_type": "finding",
            "concept": D("tail dependence between windspeed and dryness (Santa Ana weather regime)", "explicit"),
            "relation_or_direction": D("χ ≈ 0.3; driest about 30% of the time at highest windspeeds", "explicit"),
            "geography": _GEO_1293_SA,
            "temporal_frame": D("1973-2015 record, September-November", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_1293_SA,
            "evidence": E("mathematical background for approach", "implying that conditions are at their driest levels about 30% of the time when windspeeds are at their highest levels"),
            "notes": None,
        },
        {
            "claim_text": "The Karachi temperature and humidity data are asymptotically independent and negatively associated: the hottest days have lower humidity and the most humid days lower temperatures.",
            "claim_type": "finding",
            "concept": D("tail association of temperature and relative humidity", "explicit"),
            "relation_or_direction": D("asymptotically independent; negative association (η estimated 0.20)", "explicit"),
            "geography": _GEO_1293_K,
            "temporal_frame": D("1973-2015 record, April-October", "explicit"),
            "scenario": UNKNOWN,
            "experimental_condition": _EXP_1293_K,
            "evidence": E("mathematical background for approach", "In fact these data exhibit negative association: days with highest temperature are days with lower humidity, and conversely, the days with highest humidity are days with lower temperatures."),
            "notes": None,
        },
    ],
    "rejected_or_ambiguous": [
        {
            "evidence": E("introduction", "Shown in black are six successive days in June 2015 which correspond to a heat wave which is blamed for the deaths of more than 700 people (Masood et al., 2015)."),
            "reason": "Cited impact figure for the motivating example; not this paper's evidence.",
        },
        {
            "evidence": E("introduction", "The left panel shows data related to a southern California weather regime known as the Santa Ana winds, a windy and dry weather regime conducive for wildfires."),
            "reason": "Description of the motivating data, not a finding.",
        },
    ],
    "terminal_status": "claims_extracted",
    "notes": "Large parts of the stored text are plot-marker residue ('q q q ...'). The paper cites 'Stephenson, 2002' (the evd R package author).",
}
