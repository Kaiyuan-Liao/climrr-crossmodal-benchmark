"""M4-WP4r1 Phase C: reader 1's classification of the frozen term hits, as data.

Made **after** the reading was frozen (commit e0857aa), by the EXECUTOR as reader 1,
2026-10-19. For every sampled item and every matched concept term (query group 0,
including bare `fwi`) and place term, `scripts/wp4_hit_classification.py` finds
**all** occurrences in the decoded source with the collection matcher
(`\\bterm\\b`, case-insensitive, per string section) --- the frozen files hold only
the first per section --- and applies the class below. Context terms (query group 1:
"climate change", "warming", ...) are outside this package and are not classified.

Each entry: a default `class` and one-line `reason` for the item-term pair, and
optional `overrides` --- `{"occurrences": [i, ...], "class": ..., "reason": ...}`
with zero-based occurrence indices in document order (section order, then offset).
The pair's `primary_class` is the most substantive class present among its
occurrences (order below). Vocabulary per the GUIDANCE ruling (D-025, Track A).
"""

from __future__ import annotations

CONCEPT_CLASSES = ("substantive_concept_use", "incidental_mention", "ambiguous_acronym_or_collision")
PLACE_CLASSES = ("study_area_or_phenomenon_geography", "contextual_geography", "institution_or_affiliation",
                 "citation_surname_or_person", "other_incidental")

SUB, INC, COL = CONCEPT_CLASSES
STUDY, CTX, INST, CIT, OTHER = PLACE_CLASSES


def J(cls: str, reason: str, *overrides: dict) -> dict:
    return {"class": cls, "reason": reason, "overrides": list(overrides)}


def O(occ: list[int], cls: str, reason: str) -> dict:
    return {"occurrences": occ, "class": cls, "reason": reason}


JUDGEMENTS: dict[tuple[str, str], dict] = {
    # ---------------------------------------------------------------- fire weather arm
    ("LIT2-000185", "fire weather index"): J(INC, "One background sentence attributed to ref. 3 (FWI highest in 37 years in Europe); the paper builds a burnt-area event database and never uses FWI."),
    ("LIT2-000185", "fwi"): J(INC, "The same background passage (FWI and its DC/DMC components); no use of FWI in the analysis."),
    ("LIT2-000185", "california"): J(STUDY, "California is the validation area: GlobFire's large fires are compared with CALFIRE's top-20 list."),

    ("LIT2-000366", "fire weather index"): J(INC, "Background description of Canada's forest fire weather index system; the paper's model uses a UCI meteorological data set, not FWI."),
    ("LIT2-000366", "fwi"): J(INC, "The same background passage ('forest fire whether index(FWI)', systems built on FWI ideas); FWI is not computed or used."),
    ("LIT2-000366", "california"): J(INST, "'University of California at Irvine' names the data-set provider; the study area is Montesinho park, Portugal."),

    ("LIT2-000499", "fire weather index"): J(INC, "Background list of indices (Canadian FWI, US Fosberg FWI); the paper's own analysis uses the Australian FFDI."),
    ("LIT2-000499", "california"): J(CTX, "Background only: 2017 house losses in California, the California Public Resource Code, a 2007 southern California evacuation; the study area is the Blue Mountains, NSW."),

    ("LIT2-000560", "canadian forest fire weather index"): J(INC, "Related-work characterisation of the Canadian Forest Fire Weather Index System; not used."),
    ("LIT2-000560", "fire weather index"): J(INC, "The same related-work sentence (inside 'Canadian Forest Fire Weather Index System'); not used."),
    ("LIT2-000560", "california"): J(CTX, "A Figure 1 caption illustrating FIRMS data for Northern California; the modelled sites are Portland, Medford, Reno, Denver and Salt Lake City."),

    ("LIT2-000673", "fire weather index"): J(INC, "Future-work sentence ('a parameterization based on the fire weather index (FWI) ... may help'), stored three times; FWI is not used."),
    ("LIT2-000673", "fwi"): J(INC, "The same future-work sentence, three copies."),
    ("LIT2-000673", "california"): J(OTHER, "ATom-1 aircraft route logistics (flights 'returned to California', 'from Minnesota to southern California'); not a study area of the forecast evaluation.",
        O([0, 2, 4], INST, "Locates the Armstrong Flight Research Center 'in Palmdale, California', where the flights originated.")),

    ("LIT2-000786", "fire weather index"): J(INC, "A figure caption describing a background fire-potential map (days above the 95th percentile of FWI, Bowman et al. 2020), stored three times."),
    ("LIT2-000786", "california"): J(STUDY, "Study areas of the reviewed bat-fire studies (Sierra Nevada, montane and mixed-conifer forests of California); the review's evidence base."),
    ("LIT2-000786", "stephens"): J(CIT, "Citation surname: 'Stephens and Moghaddas 2005' (snag availability), stored three times."),

    ("LIT2-001063", "canadian forest fire weather index"): J(INC, "Describes the method of a cited study (Ramos et al 2023) for the Portugal 2017 case; this perspective does not compute FWI."),
    ("LIT2-001063", "fire weather index"): J(INC, "The same sentence (inside 'Canadian Forest Fire Weather Index System')."),
    ("LIT2-001063", "california"): J(STUDY, "The 2020 California drought and FIRO at Lake Mendocino (coastal northern California) is one of the paper's case studies.",
        O([3, 4], CTX, "Marine-heatwave case context: sea-lion strandings and whale entanglements off California."),
        O([17], INST, "'the University of California' as a partner institution of the FIRO programme.")),

    ("LIT2-001157", "canadian forest fire weather index"): J(INC, "Context: the existing Sierras Chicas warning system uses CFWIS point estimates; CFWIS percentile calibration cited as a precedent. The paper's metric is fuel moisture content."),
    ("LIT2-001157", "fire weather index"): J(INC, "The same CFWIS mentions plus a cited example (de Jong et al. used the 99th percentile of FWI in the UK); FWI is not used."),
    ("LIT2-001157", "fwi"): J(INC, "The de Jong et al. citation only."),
    ("LIT2-001157", "california"): J(CTX, "A cited comparison: large fires in the Chaparral in California below 79% live fuel moisture; the study area is Córdoba, Argentina."),

    ("LIT2-001236", "canadian forest fire weather index"): J(SUB, "Names the basis of the EFFIS fire danger forecasts that the system ingests as one of its four classifier inputs."),
    ("LIT2-001236", "fire weather index"): J(SUB, "The system computes the fire weather index from local weather data; the evaluation reports FWI above 100 at the Rafina-Mati ignition (claim C2)."),
    ("LIT2-001236", "fwi"): J(SUB, "FWI is computed, normalised to alert classes, and reported for the 2018 fire; EFFIS FWI data are an input."),
    ("LIT2-001236", "california"): J(CTX, "Background and analogy: the November 2018 Camp fire in California; the evaluation case is Rafina-Mati, Greece."),

    ("LIT2-001308", "fire weather index"): J(SUB, "The authors report a separate project analysis: Canadian FWI calculated for the study area from RegCM v.4 output, yielding a 2040 projection (claim C4); the sentence is truncated in the source."),
    ("LIT2-001308", "california"): J(STUDY, "San Diego County, California and the 2007 southern California wildland fires are the study area and event.",
        O([2, 3, 4], CTX, "Cited background on southern California: Santa Ana winds accompany the largest fires; climate models favour more California wildland fires.")),

    # ---------------------------------------------------------------- extreme heat arm
    ("LIT2-000084", "heat index"): J(SUB, "The paper uses heat index (Schoen 2005) as its heat-wave intensity measure and reports humidity-including metrics as less sensitive (claim C3).",
        O([1], INC, "Introduction background: greenhouse gas emissions increase the heat index of heat waves (cited).")),
    ("LIT2-000084", "california"): J(STUDY, "California's Central Valley is a region of the paper's own significant simulated effects (results, discussion).",
        O([0], CTX, "Introduction example of irrigation loss in drought years in California's Central Valley.")),
    ("LIT2-000084", "oklahoma"): J(STUDY, "Oklahoma is one of the four states defining the paper's Southern Great Plains analysis region (claim C4)."),

    ("LIT2-000203", "heat index"): J(INC, "Listed among heat stress indices the protocol will calculate (stored twice); a protocol with no results."),
    ("LIT2-000203", "california"): J(CTX, "A cited case-crossover study from California (prematurity and temperature), stored twice.",
        O([0, 1], CIT, "Inside a cited article title in the reference list: 'Risk of Stillbirth in California'.")),

    ("LIT2-000315", "heat index"): J(INC, "Cited background (Lobell et al.: mean and peak heat index under irrigation) and the NWS heat-index basis of the 27 °C threshold; the paper's measure is wet-bulb temperature."),
    ("LIT2-000315", "california"): J(CTX, "Cited study area (Lobell et al., California and Nebraska) and a limitation remark on topography; the analysis is global."),

    ("LIT2-000470", "heat index"): J(SUB, "The narrative review discusses heat index as an occupational heat-stress metric (definition, adjustments, limits, OSHA guidance on heat index usage).",
        O([0], INC, "Background: an OSHA/NIOSH app giving recommendations based on heat index."),
        O([8], INC, "Inside a cited title: 'Using the heat index: A guide for employers'.")),
    ("LIT2-000470", "california"): J(CTX, "Regulatory context: California is one of three states enforcing OSHA-approved heat standards (claim C5, background)."),

    ("LIT2-000662", "heat index"): J(INC, "Only in the definition of an excessive heat event 'by the NCDC heat index' (stored three times, twice truncated); the analysed variables are apparent-temperature heat-wave statistics taken from another study. Borderline."),
    ("LIT2-000662", "california"): J(CTX, "Cited worker heat-fatality rates (Gubernot et al.) for Florida, Texas and California."),

    ("LIT2-000803", "heat index"): J(SUB, "Heat index caution levels are an operational control rule of the ventilation model and appear throughout the results (the paper's scope is ambiguous)."),
    ("LIT2-000803", "california"): J(CTX, "Locations of a cited ventilation study ('five locations in California'), stored twice."),

    ("LIT2-000927", "heat index"): J(INC, "A cited example: the NWS national heat index threshold found ineffective in California desert communities (claim C5, background); the paper's metric is maximum temperature."),
    ("LIT2-000927", "california"): J(CTX, "Background (2006 California heat deaths) and the cited California-desert example; the study area is South Africa."),

    ("LIT2-001075", "heat index"): J(INC, "A cited finding (Skarha et al. 2023) used to justify air temperature over heat index; heat index is not used."),
    ("LIT2-001075", "california"): J(STUDY, "California prisons are part of the national study sample and its rankings (claims C2, C3).",
        O([5], CIT, "Citation author: '(State of California, 2021)'.")),
    ("LIT2-001075", "oklahoma"): J(STUDY, "Oklahoma appears in the paper's state-average heat exposure ranking and in its comparison with a prior national study."),

    ("LIT2-001160", "heat index"): J(COL, "Every occurrence is inside a different index: the paper's own 'standardized heat index (SHI)', a probabilistic temperature-percentile index, or 'Excess heat index' (EHI, a component of EHF); not the temperature-humidity heat index."),
    ("LIT2-001160", "california"): J(STUDY, "Southeast California appears in the paper's own July 1995 validation map (heatwave days by the constant-threshold definition)."),

    ("LIT2-001293", "heat index"): J(SUB, "Operational use in data construction: daily observations are taken at the time of the maximum heat index, and months selected where heat index exceeded its 0.95 quantile."),
    ("LIT2-001293", "california"): J(STUDY, "'a southern California weather regime known as the Santa Ana winds' locates one of the paper's two applied data examples."),
}
