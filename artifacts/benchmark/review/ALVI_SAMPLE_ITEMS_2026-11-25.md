# Sample hazard -> infrastructure items for Alvi --- 2026-11-25

6 sample items (three heat, three fire weather). Same content as `ALVI_SAMPLE_ITEMS_2026-11-25.xlsx` (sheets ITEMS and README).

## README

- **What this item type is.** Each item pairs a projected hazard change at one place (from the ClimRR table: dangerous heat-index days or summer fire-weather danger) with what research shows such conditions do to one class of infrastructure (a CISA sector). No item says that a particular asset at the place will fail.
- **The question is all the model sees.** The model under test gets only the Question: no table, no paper, no data.
- **Grading is at pattern level.** Direction and rough size of the hazard change, the drivers, and the kind of impact on the asset class. The values in 'Table side' are where the answer comes from; the model is not expected to give them.
- **'Research suggests'.** Marks a finding from one paper in our literature corpus ('research shows': two or more papers).
- **Claim groups and passages.** Claim groups are formed by an agent and checked by a reviewer at the claim level; individual member passages are still under review.
- **Our three questions for you.** (1) Are these the hazard -> infrastructure questions and answers scientists want? (2) Which asset classes and which impact types matter most? (3) Is the general-evidence wording ("not findings specific to California") acceptable, or should items be restricted to evidence that names the place?

## 1 · BI-P5-0001

### Question

What does a projected increase in dangerous heat-index days in Virginia by mid-century mean for energy systems, and why?

### Answer

In Virginia, dangerous heat-index days in summer are projected to increase more than tripling, from about 4 to about 16 days a summer, by mid-century under a high-emissions future. Research on the United States shows that large-scale warming and land–atmosphere feedbacks drive increases in extreme heat. In general, research shows that global warming increases heatwave frequency and intensity. In general, research shows that extreme heat, of which dangerous heat-index days are one measure, can reduce generation output of energy systems. In general, research shows that such heat raises electricity demand and stresses energy systems. In general, research shows that extreme heat and wind raise the chance of ignitions near power lines. These are general drivers of dangerous heat-index days, not findings specific to Virginia.

### Asset class (CISA sector)

Energy Sector (in the item: "energy systems")

### Table side

- Quantity: Number of Summer days with daily max heat index above 95 F (data dictionary line 685; columns heatindex_HIS_Day95, heatindex_M85_Day95)
- Place: Virginia (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: Mid-Century, 2045 to 2054
- Scenario: RCP8.5
- Statistic: change in the number of days (future minus baseline), unweighted mean over grid cells
- Values: mean 3.5 days -> 16.0 days (+12.5 days)
- Rank among State labels: 18 of 49 (largest change first)
- Grid cells: 705 (increasing: 705; decreasing: 0)
- Pattern descriptor (DR-DESC-1 v4): more than tripling; a change similar to most states; from about 4 to about 16 days a summer
- working assumptions relied on: WA-STATE-LABEL (R-005), WA-UNWEIGHTED-MEAN (R-008) --- owner-authorized (D-064), not confirmed
- Place-named impact evidence: yes (cited impact groups resting on papers that name Virginia: 1)

### Paper side

- Impact, research shows (2 papers): thermal power plant output reduction [place-named: Virginia]
- Impact, research shows (9 papers): extreme heat increases electricity demand and stresses power supply
- Impact, research shows (2 papers): wildfire risk to power transmission lines --- via wildfire occurrence
- Driver, research shows (2 papers): Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat
- Driver, research shows (4 papers): global warming increases heatwave frequency and intensity

### Original passages

- [thermal power plant output reduction]
    - paper 257463109, test case 2: "The 2012 heat wave exerted impact on all three ncSFE time series, albeit moderately. Changing once-through systems to cooling towers reduced power production slightly relative to Baseline, a limited decrement that reflected the small increase in power consumption to pump water between the condenser and cooling towers. In contrast, the Fixed-CF scenario decreased electricity production even more, indicating the importance of fuel mix on total power production."
    - paper 257463109, test case 2: "The climate extreme alone plus the two climate-technology scenarios all generated negative impacts on overall regional power production, with the coal fuel scenario showing the lowest potential production and, as with Approach A, an approximate 10% penalty. The bars on the right side of Figure 4C are the Δ values showing that in our example electricity production was reduced under all scenarios but by less than 5%."
    - paper 132959901, ii. mitigation plan by the utility company: "In a warming climate the power station input water temperature may become too high and thus reduce the generation efficiency when electric demand is at its peak."
- [extreme heat increases electricity demand and stresses power supply]
    - paper 169368231, introduction: "In July and August of 2016, electric power consumption was the highest ever due to the heat wave in Korea."
    - paper 199326805, bushfires and extreme heat: "Extreme fire weather days are characterised by strong gusty winds and high temperatures."
    - paper 203641904, a. physical threats: "Heatwaves can cause an abrupt rise in air-conditioning loads, and if generation cannot match the demand, site-wide outages or load-shedding can happen;"
    - paper 209454109, conclusion: "Increasing frequency and intensity of heat waves.-Increase in average temperature."
    - (5 more in provenance)
- [wildfire risk to power transmission lines]
    - paper 249431725, vi. conclusion and future work: "We find that weather and vegetation features are among the most important predictors of ignition events on distribution circuits and wire down events on transmission lines."
    - paper 255372301, results and discussion: "It is seen that higher temperature and stronger wind speed increase the wildfire risks by the factors of 1.94 (i.e., exp(β 2 )) and 2.43 (i.e., exp(β 3 ))."
- [Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat]
    - paper 199098498, late century results: "However, recent work examining changes in the frequency of different types of extreme heat days (considering both temperature and humidity) in CMIP5 projections after using a multivariate quantile mapping approach similar to the MACA methodology finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."
    - paper 5838629, results: "Air mass stagnation events, which increase O3 production and will increase in frequency as weather conditions favorable to heat waves increase (CCSP 2008), are another important indicator."
- [global warming increases heatwave frequency and intensity]
    - paper 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
    - paper 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
    - paper 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."
    - paper 235602877, abstract: "With climate change, heat waves have become more frequent and intense."


## 2 · BI-P5-0002

### Question

What could a projected increase in dangerous heat-index days mean for transportation systems in Arizona, and why?

### Answer

Dangerous heat-index days are projected to increase moderately in Arizona by mid-century under a high-emissions future. Research on the United States, including work on the Southwest, shows that large-scale warming and land‑atmosphere feedbacks drive increases in extreme heat. In general, research shows that global warming increases heat‑wave frequency and intensity. In general, research shows that extreme heat, of which dangerous heat-index days are one measure, can degrade transportation systems. In general, research shows that such heat increases pavement distress, reducing the performance of transportation systems. These are general drivers of dangerous heat-index days, not findings specific to Arizona.

### Asset class (CISA sector)

Transportation Systems Sector (in the item: "transportation systems")

### Table side

- Quantity: Number of Summer days with daily max heat index above 95 F (data dictionary line 685; columns heatindex_HIS_Day95, heatindex_M85_Day95)
- Place: Arizona (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: Mid-Century, 2045 to 2054
- Scenario: RCP8.5
- Statistic: change in the number of days (future minus baseline), unweighted mean over grid cells
- Values: mean 13.9 days -> 24.2 days (+10.3 days)
- Rank among State labels: 23 of 49 (largest change first)
- Grid cells: 2,007 (increasing: 1,976; decreasing: 0)
- Pattern descriptor (DR-DESC-1 v4): a moderate increase; a change similar to most states; from about 14 to about 24 days a summer
- working assumptions relied on: WA-STATE-LABEL (R-005), WA-UNWEIGHTED-MEAN (R-008) --- owner-authorized (D-064), not confirmed
- Place-named impact evidence: yes (cited impact groups resting on papers that name Arizona: 1)

### Paper side

- Impact, research shows (9 papers): pavement structural degradation from heat [place-named: Arizona]
- Impact, research suggests (1 paper): heat‑driven vegetation fires threaten railway corridors --- via wildfire occurrence [not in the displayed answer: its sentence was removed by a COORDINATOR edit]
- Driver, research shows (3 papers): Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat
- Driver, research shows (4 papers): global warming increases heatwave frequency and intensity

### Original passages

- [pavement structural degradation from heat]
    - paper 269406624, bepam: "It shows that the number of identified POIs, which signify pavement distress, varies with changes in pavement temperature.The data exhibit a strong correlation between pavement temperature and the frequency of POIs, with an 83% R-squared value for road section 1 and 70% for road section 2."
    - paper 158185209, temperature: "The increase in temperatures causes a greater vulnerability of common road pavements (with surface layer composed of asphalt concrete) and rail (track), increases the energy demand to operate buses, especially for auxiliaries [17], which is perceived by the fleets managers as one more items in the overall lists of operational costs [18,19], and worsens the public's living conditions."
    - paper 213951900, temperature: "In extreme cases, when temperature has significant daily/hourly increases, accelerated development of permanent deformation can be expected [3,16]."
    - paper 213951900, temperature: "Increases in the temperature ranges due to climate change can increase thermal stresses in asphalt layers, and more thermal cracking can be expected [17,18]."
    - (6 more in provenance)
- [heat‑driven vegetation fires threaten railway corridors]
    - paper 237251104, climate change impact on swedish railways infrastructure: "Heat and drought also increase the risk of vegetation fires and thus also the need to stop or redirect traffic."
- [Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat]
    - paper 158091651, abstract: "Land-atmosphere feedbacks appear to be a stronger factor for heat wave maintenance at southern latitudes, but the NCEP model seems to misrepresent those feedbacks, particularly over the Southwest United States, leading to poor skill in that region."
    - paper 199098498, late century results: "However, recent work examining changes in the frequency of different types of extreme heat days (considering both temperature and humidity) in CMIP5 projections after using a multivariate quantile mapping approach similar to the MACA methodology finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."
    - paper 5838629, results: "Air mass stagnation events, which increase O3 production and will increase in frequency as weather conditions favorable to heat waves increase (CCSP 2008), are another important indicator."
- [global warming increases heatwave frequency and intensity]
    - paper 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
    - paper 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
    - paper 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."
    - paper 235602877, abstract: "With climate change, heat waves have become more frequent and intense."


## 3 · BI-P5-0004

### Question

What does a projected increase in dangerous heat-index days in California by mid-century mean for healthcare and public health systems, and why?

### Answer

Dangerous heat-index days in California are projected to show a moderate increase by mid-century under a high-emissions future. Research on the United States, including work on the Southwest, shows that large-scale warming and land–atmosphere feedbacks drive increases in extreme heat. In general, research shows that global warming increases heatwave frequency and intensity. In general, research suggests that extreme heat, of which dangerous heat-index days are one measure, can increase demand for emergency and hospital services, straining healthcare and public health systems. In general, research suggests that such heat can damage critical public health infrastructure, impeding healthcare and public health systems. These are general drivers of dangerous heat-index days, not findings specific to California.

### Asset class (CISA sector)

Healthcare and Public Health Sector (in the item: "healthcare and public health systems")

### Table side

- Quantity: Number of Summer days with daily max heat index above 95 F (data dictionary line 685; columns heatindex_HIS_Day95, heatindex_M85_Day95)
- Place: California (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: Mid-Century, 2045 to 2054
- Scenario: RCP8.5
- Statistic: change in the number of days (future minus baseline), unweighted mean over grid cells
- Values: mean 15.4 days -> 24.4 days (+9.0 days)
- Rank among State labels: 25 of 49 (largest change first)
- Grid cells: 2,827 (increasing: 2,681; decreasing: 0)
- Pattern descriptor (DR-DESC-1 v4): a moderate increase; a change similar to most states; from about 15 to about 24 days a summer
- working assumptions relied on: WA-STATE-LABEL (R-005), WA-UNWEIGHTED-MEAN (R-008) --- owner-authorized (D-064), not confirmed
- Place-named impact evidence: no (no impact statement in our corpus names California; general evidence only)

### Paper side

- Impact, research suggests (1 paper): Heat waves increase demand for ambulance services, emergency medical services, and hospitalizations, thereby straining healthcare facility capacity.
- Impact, research suggests (1 paper): Heatwaves can damage critical public health infrastructure and impede health system functioning.
- Driver, research shows (4 papers): Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat
- Driver, research shows (4 papers): global warming increases heatwave frequency and intensity

### Original passages

- [Heat waves increase demand for ambulance services, emergency medical services, and hospitalizations, thereby straining healthcare facility capacity.]
    - paper 243834420, literature co-citation network and timeline view: "Hajat et al. and Nitschke et al. discussed the effects of heat waves on human health and the increased demand for healthcare facilities (44,45). Morbidity, demand for ambulance services, demand for emergency medical services, hospitalization rates, and other indicators can be used to measure the impact on human health (14,44,45). Furthermore, indicators such as demand for ambulance services, hospitalization rates, and demand for emergency medical services can also be used to reflect the impact on health facilities (44,45)."
- [Heatwaves can damage critical public health infrastructure and impede health system functioning.]
    - paper 53113505, climate-related shocks and stresses: "Examples of shocks include environmental, climatic, or other types of events, such as floods, high winds, landslides, heatwaves or droughts, that can impact health, damage critical public health infrastructure, and impede health system functioning."
- [Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat]
    - paper 158091651, abstract: "Land-atmosphere feedbacks appear to be a stronger factor for heat wave maintenance at southern latitudes, but the NCEP model seems to misrepresent those feedbacks, particularly over the Southwest United States, leading to poor skill in that region."
    - paper 199098498, late century results: "However, recent work examining changes in the frequency of different types of extreme heat days (considering both temperature and humidity) in CMIP5 projections after using a multivariate quantile mapping approach similar to the MACA methodology finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."
    - paper 5838629, results: "Air mass stagnation events, which increase O3 production and will increase in frequency as weather conditions favorable to heat waves increase (CCSP 2008), are another important indicator."
    - paper 52215224, introduction: "For example, parallels can currently be seen in California, where the occurrence of droughts and intense heat waves has increased [7]."
- [global warming increases heatwave frequency and intensity]
    - paper 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
    - paper 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
    - paper 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."
    - paper 235602877, abstract: "With climate change, heat waves have become more frequent and intense."


## 4 · BI-P5-0006

### Question

Why does fire-weather danger matter for transportation systems, and how is it projected to change in California?

### Answer

Fire-weather danger is projected to increase slightly in California by mid-century under a high-emissions future, a larger change than in most states. Fire-weather danger describes conditions that favour wildfire; it is not fire occurrence. Research on California shows that strong winds are a primary driver of fire danger, and that strong winds and low humidity raise fire danger and fire size. In general, research suggests that conditions that favour wildfire, of which fire-weather danger is one measure, can damage, block or destroy transportation systems. Research on the United States suggests that when wildfires occur, they intersect road networks, increasing exposure of transportation systems. In general, research suggests that such conditions increase fire‑risk days and fire intensity, which can impede emergency response and reduce mobility of transportation systems.

### Asset class (CISA sector)

Transportation Systems Sector (in the item: "transportation systems")

### Table side

- Quantity: Seasonal value, under the dictionary's Wildfire columns (line 662; columns wildfire_summer_Hist, wildfire_summer_Midc, wildfire_summer_Dmid), read as the summer Fire Weather Index (FWI): a fire-danger index, not fire occurrence
- Place: California (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: Mid-Century, 2045 to 2054
- Scenario: RCP8.5
- Statistic: change in the seasonal value (future minus baseline), unweighted mean over grid cells
- Values: mean 31.4 -> 33.6 (+2.2) (index value, no unit)
- Rank among State labels: 8 of 49 (largest change first)
- Grid cells: 2,831 (increasing: 2,723; decreasing: 108)
- Pattern descriptor (DR-DESC-1 v4): a slight increase; a larger change than in most states
- working assumptions relied on: WA-FWI-SUMMER (R-004), WA-STATE-LABEL (R-005), WA-UNWEIGHTED-MEAN (R-008) --- owner-authorized (D-064), not confirmed
- Place-named impact evidence: no (no impact statement in our corpus names California; general evidence only)

### Paper side

- Impact, research suggests (1 paper): fire‑weather damage to roads and bridges
- Impact, research suggests (1 paper): wildfire activity increases road network exposure to fire --- via wildfire occurrence
- Impact, research suggests (1 paper): extreme fire‑weather exposure risk to residential and critical infrastructure
- Driver, research shows (5 papers): strong winds are a primary driver of fire danger and spread
- Driver, research shows (5 papers): strong winds and low humidity raise fire danger and fire size

### Original passages

- [fire‑weather damage to roads and bridges]
    - paper 237693112, victorian bushfires: "Further, many roads, bridges, and paths for vehicles are damaged, blocked, or destroyed due to bushfires or other associated emergencies that make road-based response planning very difficult in the post-disaster scenario."
- [wildfire activity increases road network exposure to fire]
    - paper 259716408, increasing road and powerline exposure to large fires: "Road exposure to fire increased in the CONUS at a rate of 485 km yr −1 (s.e.400) from 2000 to 2019, corresponding to a 58% growth in two decades (Fig. 3a)."
- [extreme fire‑weather exposure risk to residential and critical infrastructure]
    - paper 152679625, case study 1: climate change adaptation to address bushfire risk and disaster management: "The changes will likely result in a longer fire season, increased frequency of extreme or catastrophic fire-risk days, increased fire intensity, reduced opportunity to undertake prescribed Traditional measures applied to reduce the risk of bushfire have proved inadequate in the face of large scale, catastrophic fires (VBRC 2009)."
- [strong winds are a primary driver of fire danger and spread]
    - paper 236175367, discussion: "This study shows that (i) SAW wind speed plays a key role in area burned, (ii) variation in SAW windspeed outweighs fuel characteristics in explaining area burned, (iii) winds alone are insufficient to explain burning without consideration of human ignitions, (iv) ignition sources have changed markedly in recent decades, and (v) autumn and winter temperature and precipitation are less critical than winds and ignitions, and have substantially different effects on autumn versus winter SAW events."
    - paper 255372301, results and discussion: "It is seen that higher temperature and stronger wind speed increase the wildfire risks by the factors of 1.94 (i.e., exp(β 2 )) and 2.43 (i.e., exp(β 3 )). Such findings can be well justified as follows: (i) a higher temperature makes the ignition of the underlying fuels more easily (e.g. grasses, shrubs, dead leaves, etc.), (ii) with an increased wind speed, the electrical conductors and surrounding vegetation are more likely to result in arcing, increasing the probability of wildfire ignition (Mitchell, 2013;Vazquez et al., 2022)."
    - paper 53050065, summary: "Common to both events was the occurrence of strong winds that have been shown to be a key determinant in large human-caused wildfires [56]."
    - paper 14300, results: "Whereas fire numbers are determined by the presence of fuel, lightning frequency, population density and surface fire intensity, fire spread (and hence area burnt) is driven by wind speed, fire duration and the amount, moisture content and characteristics of the fuel."
    - (1 more in provenance)
- [strong winds and low humidity raise fire danger and fire size]
    - paper 236175367, of 9: "maximum wind speed was tied to greater area burned by fires in the 1000 to 5000 ha class (Fig. 3B)."
    - paper 53050065, meteorological conditions: "The strong winds and adiabatic compression associated with the downslope flow and mixing inhibited radiative cooling and nocturnal RH recovery."
    - paper 56076970, discussion and implications: "Meteorology was clearly the dominant factor controlling SA fires; the spatial and temporal variability of SA FS was well correlated with meteorological drivers, including RH and wind as modulated by terrain (see also figure S3)."
    - paper 56076970, discussion and implications: "The SA wind events studied here are examples as dry and hot Foehn winds; these winds occur in the leeside of the mountain ranges and are associated with the elevated fire danger in many other parts of the world, including Europe and Australia (Sharples et al 2010)."
    - (2 more in provenance)


## 5 · BI-P5-0007

### Question

What does a projected increase in fire-weather danger in California by mid-century mean for emergency services, and why?

### Answer

Fire‑weather danger in California is projected to show a slight increase by mid-century under a high-emissions future, a larger change than in most states. Research on California shows that strong winds are a primary driver of fire‑weather danger. In general, research shows that drier air, with a higher vapor-pressure deficit, raises fire danger. In general, research suggests that fire‑weather danger can increase daily standby costs for emergency services.

### Asset class (CISA sector)

Emergency Services Sector (in the item: "emergency services")

### Table side

- Quantity: Seasonal value, under the dictionary's Wildfire columns (line 662; columns wildfire_summer_Hist, wildfire_summer_Midc, wildfire_summer_Dmid), read as the summer Fire Weather Index (FWI): a fire-danger index, not fire occurrence
- Place: California (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: Mid-Century, 2045 to 2054
- Scenario: RCP8.5
- Statistic: change in the seasonal value (future minus baseline), unweighted mean over grid cells
- Values: mean 31.4 -> 33.6 (+2.2) (index value, no unit)
- Rank among State labels: 8 of 49 (largest change first)
- Grid cells: 2,831 (increasing: 2,723; decreasing: 108)
- Pattern descriptor (DR-DESC-1 v4): a slight increase; a larger change than in most states
- working assumptions relied on: WA-FWI-SUMMER (R-004), WA-STATE-LABEL (R-005), WA-UNWEIGHTED-MEAN (R-008) --- owner-authorized (D-064), not confirmed
- Place-named impact evidence: no (no impact statement in our corpus names California; general evidence only)

### Paper side

- Impact, research suggests (1 paper): Higher numbers of fire‑danger days lead to substantially higher daily costs for standby firefighting equipment and personnel.
- Driver, research shows (5 papers): strong winds are a primary driver of fire danger and spread
- Driver, research shows (2 papers): humidity and vapor pressure deficit affect fire risk

### Original passages

- [Higher numbers of fire‑danger days lead to substantially higher daily costs for standby firefighting equipment and personnel.]
    - paper 6254910, effect of increased fuel load on fire management costs: "The cost per day of equipment that were required to be 'on stand-by' in readiness for fighting wildfires had increased by 30 times from 2007 to 2010 ($375 to $11,442; Table 3, NT Government, unpublished data)."
- [strong winds are a primary driver of fire danger and spread]
    - paper 236175367, discussion: "This study shows that (i) SAW wind speed plays a key role in area burned, (ii) variation in SAW windspeed outweighs fuel characteristics in explaining area burned, (iii) winds alone are insufficient to explain burning without consideration of human ignitions, (iv) ignition sources have changed markedly in recent decades, and (v) autumn and winter temperature and precipitation are less critical than winds and ignitions, and have substantially different effects on autumn versus winter SAW events."
    - paper 255372301, results and discussion: "It is seen that higher temperature and stronger wind speed increase the wildfire risks by the factors of 1.94 (i.e., exp(β 2 )) and 2.43 (i.e., exp(β 3 )). Such findings can be well justified as follows: (i) a higher temperature makes the ignition of the underlying fuels more easily (e.g. grasses, shrubs, dead leaves, etc.), (ii) with an increased wind speed, the electrical conductors and surrounding vegetation are more likely to result in arcing, increasing the probability of wildfire ignition (Mitchell, 2013;Vazquez et al., 2022)."
    - paper 53050065, summary: "Common to both events was the occurrence of strong winds that have been shown to be a key determinant in large human-caused wildfires [56]."
    - paper 14300, results: "Whereas fire numbers are determined by the presence of fuel, lightning frequency, population density and surface fire intensity, fire spread (and hence area burnt) is driven by wind speed, fire duration and the amount, moisture content and characteristics of the fuel."
    - (1 more in provenance)
- [humidity and vapor pressure deficit affect fire risk]
    - paper 255372301, results and discussion: "Both the NDVI and the SPFH have negative impacts on wildfire risks, while SPFH has a relatively weaker effect compared with that of NDVI. Note that, a higher NDVI indicates healthier vegetation with more water conditions and fewer potential fuels that can be ignited. Similarly, a high SPFH attaches potential fuels with more moisture, reducing the wildfire risk."
    - paper 247649715, abstract: "Additionally, among the individual climate variables that comprise the FWI, relative humidity and temperature are the most influential factors that affect the observed BA."
    - paper 247649715, discussion: "Globally, in the case of forest BA anomaly, the most highly associated climate variable is found to be relative humidity, while in the case of the non-forest BA anomaly, temperature and relative humidity are found to be most highly associated for most of the regions, without, however, exhibiting any clear spatial or latitudinal pattern."


## 6 · BI-P5-0008

### Question

What could a projected increase in fire‑weather danger mean for communications systems in California, and why?

### Answer

Fire‑weather danger is projected to show a slight increase in California by mid-century under a high-emissions future, representing a larger change than in most states. Research on California shows that strong winds are a primary driver of fire danger, and that strong winds and low humidity raise fire danger and fire size. In general, research suggests that conditions that favour wildfire, of which fire‑weather danger is one measure, can destroy communications systems.

### Asset class (CISA sector)

Communications Sector (in the item: "communications systems")

### Table side

- Quantity: Seasonal value, under the dictionary's Wildfire columns (line 662; columns wildfire_summer_Hist, wildfire_summer_Midc, wildfire_summer_Dmid), read as the summer Fire Weather Index (FWI): a fire-danger index, not fire occurrence
- Place: California (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: Mid-Century, 2045 to 2054
- Scenario: RCP8.5
- Statistic: change in the seasonal value (future minus baseline), unweighted mean over grid cells
- Values: mean 31.4 -> 33.6 (+2.2) (index value, no unit)
- Rank among State labels: 8 of 49 (largest change first)
- Grid cells: 2,831 (increasing: 2,723; decreasing: 108)
- Pattern descriptor (DR-DESC-1 v4): a slight increase; a larger change than in most states
- working assumptions relied on: WA-FWI-SUMMER (R-004), WA-STATE-LABEL (R-005), WA-UNWEIGHTED-MEAN (R-008) --- owner-authorized (D-064), not confirmed
- Place-named impact evidence: no (no impact statement in our corpus names California; general evidence only)

### Paper side

- Impact, research suggests (1 paper): telecommunication system loss due to fire‑weather damage
- Driver, research shows (5 papers): strong winds are a primary driver of fire danger and spread
- Driver, research shows (5 papers): strong winds and low humidity raise fire danger and fire size

### Original passages

- [telecommunication system loss due to fire‑weather damage]
    - paper 237693112, victorian bushfires: "Also, the bushfires damages may destroy the telecommunication system resulting in loss of internet services, leading to the unavailability of technologies like GPS and GIS."
- [strong winds are a primary driver of fire danger and spread]
    - paper 236175367, discussion: "This study shows that (i) SAW wind speed plays a key role in area burned, (ii) variation in SAW windspeed outweighs fuel characteristics in explaining area burned, (iii) winds alone are insufficient to explain burning without consideration of human ignitions, (iv) ignition sources have changed markedly in recent decades, and (v) autumn and winter temperature and precipitation are less critical than winds and ignitions, and have substantially different effects on autumn versus winter SAW events."
    - paper 255372301, results and discussion: "It is seen that higher temperature and stronger wind speed increase the wildfire risks by the factors of 1.94 (i.e., exp(β 2 )) and 2.43 (i.e., exp(β 3 )). Such findings can be well justified as follows: (i) a higher temperature makes the ignition of the underlying fuels more easily (e.g. grasses, shrubs, dead leaves, etc.), (ii) with an increased wind speed, the electrical conductors and surrounding vegetation are more likely to result in arcing, increasing the probability of wildfire ignition (Mitchell, 2013;Vazquez et al., 2022)."
    - paper 53050065, summary: "Common to both events was the occurrence of strong winds that have been shown to be a key determinant in large human-caused wildfires [56]."
    - paper 14300, results: "Whereas fire numbers are determined by the presence of fuel, lightning frequency, population density and surface fire intensity, fire spread (and hence area burnt) is driven by wind speed, fire duration and the amount, moisture content and characteristics of the fuel."
    - (1 more in provenance)
- [strong winds and low humidity raise fire danger and fire size]
    - paper 236175367, of 9: "maximum wind speed was tied to greater area burned by fires in the 1000 to 5000 ha class (Fig. 3B)."
    - paper 53050065, meteorological conditions: "The strong winds and adiabatic compression associated with the downslope flow and mixing inhibited radiative cooling and nocturnal RH recovery."
    - paper 56076970, discussion and implications: "Meteorology was clearly the dominant factor controlling SA fires; the spatial and temporal variability of SA FS was well correlated with meteorological drivers, including RH and wind as modulated by terrain (see also figure S3)."
    - paper 56076970, discussion and implications: "The SA wind events studied here are examples as dry and hot Foehn winds; these winds occur in the leeside of the mountain ranges and are associated with the elevated fire danger in many other parts of the world, including Europe and Australia (Sharples et al 2010)."
    - (2 more in provenance)
