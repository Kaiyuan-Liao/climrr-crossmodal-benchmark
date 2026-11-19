# Sample items for mentor review --- 2026-11-19

Seven sample items (five heat index, two fire weather). Same content as `MENTOR_SAMPLE_ITEMS_2026-11-19.xlsx` (sheets ITEMS and README).

## README

- **The question is all the model sees.** The model under test gets only the Question: no table, no paper, no data.
- **Grading is at pattern level.** Direction of the change, rough size, comparison with other states, and drivers. The values in 'Table side' are where the answer comes from; the model is not expected to give them.
- **'Research suggests'.** Marks a driver found in one paper of our literature corpus ('research shows': two or more papers).

## 1 · BI-P3-0001

### Question

How are dangerous heat‑index days projected to change in California during summer by mid-century under a high‑emissions future, and what physical mechanisms drive this change?

### Answer

In California during summer, dangerous heat‑index days are projected to show a moderate increase by mid-century under a high‑emissions future, a change similar to most states. Research shows that large‑scale warming, global warming‑driven heat‑wave intensification, and an intensified urban heat island effect at night are the main physical mechanisms behind this increase.

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

### Paper side

- Research shows (4 papers): Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat
- Research shows (4 papers): global warming increases heatwave frequency and intensity
- Research shows (3 papers): urban heat island intensifies due to nighttime conditions and reduced moisture

### Original passages

- [Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat]
    - paper 52215224, introduction: "For example, parallels can currently be seen in California, where the occurrence of droughts and intense heat waves has increased [7]."
    - paper 199098498, late century results: "However, recent work examining changes in the frequency of different types of extreme heat days (considering both temperature and humidity) in CMIP5 projections after using a multivariate quantile mapping approach similar to the MACA methodology finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."
    - paper 158091651, abstract: "Land-atmosphere feedbacks appear to be a stronger factor for heat wave maintenance at southern latitudes, but the NCEP model seems to misrepresent those feedbacks, particularly over the Southwest United States, leading to poor skill in that region."
    - paper 5838629, results: "Air mass stagnation events, which increase O3 production and will increase in frequency as weather conditions favorable to heat waves increase (CCSP 2008), are another important indicator."
- [global warming increases heatwave frequency and intensity]
    - paper 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
    - paper 235602877, abstract: "With climate change, heat waves have become more frequent and intense."
    - paper 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
    - paper 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."
- [urban heat island intensifies due to nighttime conditions and reduced moisture]
    - paper 128765172, introduction: "Further, the UHI is most noticeable at night and under synoptic high pressure systems with calm conditions and clear skies [24,[26][27][28], and the UHI has been measured in cities spanning many varying climate regimes and sizes [29][30][31][32]."
    - paper 246243282, impact on temperature and heat waves: "In general, simulated CUHI values during a heat wave have intensified extensively relative to pre-heat wave conditions, mostly due to the lower moisture and reduced wind speed in urban areas during the heat wave."
    - paper 230583145, discussion and conclusions on the mitigation potential of gi: "During the daytime, evapotranspiration is the main cooling mechanism, however its impact on the surface energy budget may not be enough to compensate and counterbalance heat fluxes due to advection and sensible heat released by the impervious surfaces."
    - paper 230583145, the impact of increased green infrastructure on health: "During excessive temperature and drought conditions, trees may close their stomata while the surface temperature of leaves increases, contributing more sensible heat to the atmosphere and increasing the ambient temperature [150,151]."
    - paper 230583145, discussion and conclusions on the mitigation potential of gi: "During the night, the maximum ambient temperature decrease corresponding to a GI rise of 80% may not exceed 2.3 • C, while the temperature drop for a GI increase by 20% is close to 0.5 • C."


## 2 · BI-P3-0004

### Question

How are summer days hot and humid enough to be dangerous projected to change in Alabama by late this century under a high-emissions future, and what are the main physical drivers of this change?

### Answer

In Alabama, days that are hot and humid enough to be dangerous are projected to increase. They will move from rare to common. This is a larger change than in most states. The change is expected by late this century under a high-emissions future. Research shows that large‑scale warming drives the increase. It also shows that global warming raises heat‑wave frequency and intensity. It further shows that intensified urban heat islands at night amplify dangerous heat‑index days.

### Table side

- Quantity: Number of Summer days with daily max heat index above 105 F (data dictionary line 695; columns heatindex_HIS_Day105, heatindex_E85_Day105)
- Place: Alabama (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: End-Century, 2085 to 2094
- Scenario: RCP8.5
- Statistic: change in the number of days (future minus baseline), unweighted mean over grid cells
- Values: mean 1.4 days -> 45.2 days (+43.9 days)
- Rank among State labels: 7 of 49 (largest change first)
- Grid cells: 934 (increasing: 934; decreasing: 0)
- Pattern descriptor (DR-DESC-1 v4): rising from rare to common; a larger change than in most states; from about 1 day to about 45 days a summer
- working assumptions relied on: WA-STATE-LABEL (R-005), WA-UNWEIGHTED-MEAN (R-008) --- owner-authorized (D-064), not confirmed

### Paper side

- Research shows (2 papers): Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat
- Research shows (4 papers): global warming increases heatwave frequency and intensity
- Research shows (3 papers): urban heat island intensifies due to nighttime conditions and reduced moisture

### Original passages

- [Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat]
    - paper 199098498, late century results: "However, recent work examining changes in the frequency of different types of extreme heat days (considering both temperature and humidity) in CMIP5 projections after using a multivariate quantile mapping approach similar to the MACA methodology finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."
    - paper 5838629, results: "Air mass stagnation events, which increase O3 production and will increase in frequency as weather conditions favorable to heat waves increase (CCSP 2008), are another important indicator."
- [global warming increases heatwave frequency and intensity]
    - paper 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
    - paper 235602877, abstract: "With climate change, heat waves have become more frequent and intense."
    - paper 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
    - paper 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."
- [urban heat island intensifies due to nighttime conditions and reduced moisture]
    - paper 128765172, introduction: "Further, the UHI is most noticeable at night and under synoptic high pressure systems with calm conditions and clear skies [24,[26][27][28], and the UHI has been measured in cities spanning many varying climate regimes and sizes [29][30][31][32]."
    - paper 246243282, impact on temperature and heat waves: "In general, simulated CUHI values during a heat wave have intensified extensively relative to pre-heat wave conditions, mostly due to the lower moisture and reduced wind speed in urban areas during the heat wave."
    - paper 230583145, discussion and conclusions on the mitigation potential of gi: "During the daytime, evapotranspiration is the main cooling mechanism, however its impact on the surface energy budget may not be enough to compensate and counterbalance heat fluxes due to advection and sensible heat released by the impervious surfaces."
    - paper 230583145, the impact of increased green infrastructure on health: "During excessive temperature and drought conditions, trees may close their stomata while the surface temperature of leaves increases, contributing more sensible heat to the atmosphere and increasing the ambient temperature [150,151]."
    - paper 230583145, discussion and conclusions on the mitigation potential of gi: "During the night, the maximum ambient temperature decrease corresponding to a GI rise of 80% may not exceed 2.3 • C, while the temperature drop for a GI increase by 20% is close to 0.5 • C."


## 3 · BI-P3-0003

### Question

How are dangerous heat‑index days projected to change in Washington during summer by mid-century under a high‑emissions future, and what physical drivers explain this change?

### Answer

In Washington, dangerous heat‑index days are projected to increase slightly and remain rare. This is a smaller change than in most states. The projection is for by mid-century under a high‑emissions future. Research shows that large‑scale warming and global warming drive the increase. The urban heat island effect intensifies nighttime heat. That further contributes to the projected rise.

### Table side

- Quantity: Number of Summer days with daily max heat index above 105 F (data dictionary line 686; columns heatindex_HIS_Day105, heatindex_M85_Day105)
- Place: Washington (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: Mid-Century, 2045 to 2054
- Scenario: RCP8.5
- Statistic: change in the number of days (future minus baseline), unweighted mean over grid cells
- Values: mean 0.0 days -> 0.8 days (+0.8 days)
- Rank among State labels: 37 of 49 (largest change first)
- Grid cells: 1,202 (increasing: 1,035; decreasing: 0)
- Pattern descriptor (DR-DESC-1 v4): remaining rare; a smaller change than in most states; from essentially none to about 1 day a summer
- working assumptions relied on: WA-STATE-LABEL (R-005), WA-UNWEIGHTED-MEAN (R-008) --- owner-authorized (D-064), not confirmed

### Paper side

- Research shows (2 papers): Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat
- Research shows (4 papers): global warming increases heatwave frequency and intensity
- Research shows (3 papers): urban heat island intensifies due to nighttime conditions and reduced moisture

### Original passages

- [Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat]
    - paper 199098498, late century results: "However, recent work examining changes in the frequency of different types of extreme heat days (considering both temperature and humidity) in CMIP5 projections after using a multivariate quantile mapping approach similar to the MACA methodology finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."
    - paper 5838629, results: "Air mass stagnation events, which increase O3 production and will increase in frequency as weather conditions favorable to heat waves increase (CCSP 2008), are another important indicator."
- [global warming increases heatwave frequency and intensity]
    - paper 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
    - paper 235602877, abstract: "With climate change, heat waves have become more frequent and intense."
    - paper 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
    - paper 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."
- [urban heat island intensifies due to nighttime conditions and reduced moisture]
    - paper 128765172, introduction: "Further, the UHI is most noticeable at night and under synoptic high pressure systems with calm conditions and clear skies [24,[26][27][28], and the UHI has been measured in cities spanning many varying climate regimes and sizes [29][30][31][32]."
    - paper 246243282, impact on temperature and heat waves: "In general, simulated CUHI values during a heat wave have intensified extensively relative to pre-heat wave conditions, mostly due to the lower moisture and reduced wind speed in urban areas during the heat wave."
    - paper 230583145, discussion and conclusions on the mitigation potential of gi: "During the daytime, evapotranspiration is the main cooling mechanism, however its impact on the surface energy budget may not be enough to compensate and counterbalance heat fluxes due to advection and sensible heat released by the impervious surfaces."
    - paper 230583145, the impact of increased green infrastructure on health: "During excessive temperature and drought conditions, trees may close their stomata while the surface temperature of leaves increases, contributing more sensible heat to the atmosphere and increasing the ambient temperature [150,151]."
    - paper 230583145, discussion and conclusions on the mitigation potential of gi: "During the night, the maximum ambient temperature decrease corresponding to a GI rise of 80% may not exceed 2.3 • C, while the temperature drop for a GI increase by 20% is close to 0.5 • C."


## 4 · BI-P3-0002

### Question

How are summer days hot and humid enough to be dangerous projected to change in New York by late this century under a high-emissions future, and what drives this change?

### Answer

In New York, dangerous heat‑index days in summer are projected to increase. They will go from rare to common. This is a smaller change than in most states. The change will occur by late this century under a high-emissions future. Research shows that large‑scale warming drives this increase. Global warming raises heat‑wave frequency and intensity. Intensified urban heat islands at night further amplify dangerous heat‑index days.

### Table side

- Quantity: Number of Summer days with daily max heat index above 95 F (data dictionary line 694; columns heatindex_HIS_Day95, heatindex_E85_Day95)
- Place: New York (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: End-Century, 2085 to 2094
- Scenario: RCP8.5
- Statistic: change in the number of days (future minus baseline), unweighted mean over grid cells
- Values: mean 0.2 days -> 11.2 days (+11.0 days)
- Rank among State labels: 44 of 49 (largest change first)
- Grid cells: 888 (increasing: 888; decreasing: 0)
- Pattern descriptor (DR-DESC-1 v4): rising from rare to common; a smaller change than in most states; from essentially none to about 11 days a summer
- working assumptions relied on: WA-STATE-LABEL (R-005), WA-UNWEIGHTED-MEAN (R-008) --- owner-authorized (D-064), not confirmed

### Paper side

- Research shows (2 papers): Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat
- Research shows (4 papers): global warming increases heatwave frequency and intensity
- Research shows (3 papers): urban heat island intensifies due to nighttime conditions and reduced moisture

### Original passages

- [Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat]
    - paper 199098498, late century results: "However, recent work examining changes in the frequency of different types of extreme heat days (considering both temperature and humidity) in CMIP5 projections after using a multivariate quantile mapping approach similar to the MACA methodology finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."
    - paper 5838629, results: "Air mass stagnation events, which increase O3 production and will increase in frequency as weather conditions favorable to heat waves increase (CCSP 2008), are another important indicator."
- [global warming increases heatwave frequency and intensity]
    - paper 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
    - paper 235602877, abstract: "With climate change, heat waves have become more frequent and intense."
    - paper 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
    - paper 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."
- [urban heat island intensifies due to nighttime conditions and reduced moisture]
    - paper 128765172, introduction: "Further, the UHI is most noticeable at night and under synoptic high pressure systems with calm conditions and clear skies [24,[26][27][28], and the UHI has been measured in cities spanning many varying climate regimes and sizes [29][30][31][32]."
    - paper 246243282, impact on temperature and heat waves: "In general, simulated CUHI values during a heat wave have intensified extensively relative to pre-heat wave conditions, mostly due to the lower moisture and reduced wind speed in urban areas during the heat wave."
    - paper 230583145, discussion and conclusions on the mitigation potential of gi: "During the daytime, evapotranspiration is the main cooling mechanism, however its impact on the surface energy budget may not be enough to compensate and counterbalance heat fluxes due to advection and sensible heat released by the impervious surfaces."
    - paper 230583145, the impact of increased green infrastructure on health: "During excessive temperature and drought conditions, trees may close their stomata while the surface temperature of leaves increases, contributing more sensible heat to the atmosphere and increasing the ambient temperature [150,151]."
    - paper 230583145, discussion and conclusions on the mitigation potential of gi: "During the night, the maximum ambient temperature decrease corresponding to a GI rise of 80% may not exceed 2.3 • C, while the temperature drop for a GI increase by 20% is close to 0.5 • C."


## 5 · BI-P3-0005

### Question

How are dangerous heat-index days projected to change in summer by mid-century under a high-emissions future, and what drives this change?

### Answer

Dangerous heat-index days are projected to increase in summer by mid-century under a high-emissions future. The Southeast shows the largest increase. Alaska shows essentially no change. Research shows that large‑scale warming is the primary driver of future extreme heat. Global warming raises heat‑wave frequency and intensity. The urban heat island effect further intensifies heat stress, especially at night.

### Table side

- Quantity: Number of Summer days with daily max heat index above 95 F (data dictionary line 685; columns heatindex_HIS_Day95, heatindex_M85_Day95)
- Place: the NCA5 climate regions with a State label in the table (8 of 10; not covered: U.S. Caribbean; Hawai'i and U.S.-Affiliated Pacific Islands)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: Mid-Century, 2045 to 2054
- Scenario: RCP8.5
- Statistic: change in the number of days (future minus baseline), unweighted mean over the grid cells of each region; regions ranked largest first
- Values (mean days, baseline -> future, change):
    - 1. Southeast: 18.9 -> 45.9 (+27.0); 9,383 grid cells
    - 2. Southern Great Plains: 31.5 -> 56.8 (+25.3); 7,478 grid cells
    - 3. Midwest: 8.3 -> 17.4 (+9.0); 7,944 grid cells
    - 4. Northern Great Plains: 4.3 -> 11.6 (+7.3); 7,869 grid cells
    - 5. Southwest: 6.9 -> 14.1 (+7.1); 12,050 grid cells
    - 6. Northeast: 0.6 -> 3.8 (+3.2); 3,652 grid cells
    - 7. Northwest: 1.2 -> 4.0 (+2.7); 4,271 grid cells
    - 8. Alaska: 0.0 -> 0.0 (+0.0); 10,097 grid cells
- Grid cells: 62,744 over the 8 regions
- Pattern descriptor (DR-DESC-1 v4): the largest increase: Southeast; essentially no change: Alaska
- working assumptions relied on: WA-STATE-LABEL (R-005), WA-UNWEIGHTED-MEAN (R-008) --- owner-authorized (D-064), not confirmed

### Paper side

- Research shows (3 papers): Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat
- Research shows (4 papers): global warming increases heatwave frequency and intensity
- Research shows (3 papers): urban heat island intensifies due to nighttime conditions and reduced moisture

### Original passages

- [Large-scale warming and land–atmosphere feedbacks drive increases in extreme heat]
    - paper 199098498, late century results: "However, recent work examining changes in the frequency of different types of extreme heat days (considering both temperature and humidity) in CMIP5 projections after using a multivariate quantile mapping approach similar to the MACA methodology finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."
    - paper 158091651, abstract: "Land-atmosphere feedbacks appear to be a stronger factor for heat wave maintenance at southern latitudes, but the NCEP model seems to misrepresent those feedbacks, particularly over the Southwest United States, leading to poor skill in that region."
    - paper 5838629, results: "Air mass stagnation events, which increase O3 production and will increase in frequency as weather conditions favorable to heat waves increase (CCSP 2008), are another important indicator."
- [global warming increases heatwave frequency and intensity]
    - paper 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
    - paper 235602877, abstract: "With climate change, heat waves have become more frequent and intense."
    - paper 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
    - paper 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."
- [urban heat island intensifies due to nighttime conditions and reduced moisture]
    - paper 128765172, introduction: "Further, the UHI is most noticeable at night and under synoptic high pressure systems with calm conditions and clear skies [24,[26][27][28], and the UHI has been measured in cities spanning many varying climate regimes and sizes [29][30][31][32]."
    - paper 246243282, impact on temperature and heat waves: "In general, simulated CUHI values during a heat wave have intensified extensively relative to pre-heat wave conditions, mostly due to the lower moisture and reduced wind speed in urban areas during the heat wave."
    - paper 230583145, discussion and conclusions on the mitigation potential of gi: "During the daytime, evapotranspiration is the main cooling mechanism, however its impact on the surface energy budget may not be enough to compensate and counterbalance heat fluxes due to advection and sensible heat released by the impervious surfaces."
    - paper 230583145, the impact of increased green infrastructure on health: "During excessive temperature and drought conditions, trees may close their stomata while the surface temperature of leaves increases, contributing more sensible heat to the atmosphere and increasing the ambient temperature [150,151]."
    - paper 230583145, discussion and conclusions on the mitigation potential of gi: "During the night, the maximum ambient temperature decrease corresponding to a GI rise of 80% may not exceed 2.3 • C, while the temperature drop for a GI increase by 20% is close to 0.5 • C."


## 6 · BI-P3-0007

### Question

How is fire‑weather danger projected to change in California during summer by mid‑century under a high‑emissions future, and what physical drivers are behind this change?

### Answer

In California during summer, fire‑weather danger is projected to show a slight increase. This is a larger change than in most states. The change occurs by mid‑century under a high‑emissions future. Research shows that strong winds are a main physical driver. Low humidity combined with strong winds also drives the increase. Higher temperatures and aridity are additional drivers. Humidity‑related vapor‑pressure‑deficit effects also contribute.

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

### Paper side

- Research shows (5 papers): strong winds are a primary driver of fire danger and spread
- Research shows (5 papers): strong winds and low humidity raise fire danger and fire size
- Research shows (4 papers): higher temperatures and aridity dry fuels, creating extreme fire‑weather
- Research shows (2 papers): humidity and vapor pressure deficit affect fire risk

### Original passages

- [strong winds are a primary driver of fire danger and spread]
    - paper 236175367, discussion: "This study shows that (i) SAW wind speed plays a key role in area burned, (ii) variation in SAW windspeed outweighs fuel characteristics in explaining area burned, (iii) winds alone are insufficient to explain burning without consideration of human ignitions, (iv) ignition sources have changed markedly in recent decades, and (v) autumn and winter temperature and precipitation are less critical than winds and ignitions, and have substantially different effects on autumn versus winter SAW events."
    - paper 255372301, results and discussion: "It is seen that higher temperature and stronger wind speed increase the wildfire risks by the factors of 1.94 (i.e., exp(β 2 )) and 2.43 (i.e., exp(β 3 )). Such findings can be well justified as follows: (i) a higher temperature makes the ignition of the underlying fuels more easily (e.g. grasses, shrubs, dead leaves, etc.), (ii) with an increased wind speed, the electrical conductors and surrounding vegetation are more likely to result in arcing, increasing the probability of wildfire ignition (Mitchell, 2013;Vazquez et al., 2022)."
    - paper 53050065, summary: "Common to both events was the occurrence of strong winds that have been shown to be a key determinant in large human-caused wildfires [56]."
    - paper 999274, background: "It has been shown that the largest and longest duration wildfires in southern California are often accompanied by Santa Ana winds [2], a seasonal weather phenomenon affecting southern California from Los Angeles to San Diego that typically occurs from September to April [3,4]."
    - paper 14300, results: "Whereas fire numbers are determined by the presence of fuel, lightning frequency, population density and surface fire intensity, fire spread (and hence area burnt) is driven by wind speed, fire duration and the amount, moisture content and characteristics of the fuel."
- [strong winds and low humidity raise fire danger and fire size]
    - paper 236175367, of 9: "maximum wind speed was tied to greater area burned by fires in the 1000 to 5000 ha class (Fig. 3B)."
    - paper 56076970, discussion and implications: "Meteorology was clearly the dominant factor controlling SA fires; the spatial and temporal variability of SA FS was well correlated with meteorological drivers, including RH and wind as modulated by terrain (see also figure S3)."
    - paper 89025663, contrasting patterns of sa and non-sa fires: "Low relative humidity and strong wind promote ignition and increase the rate of fire spread within dry fuels, especially for SA fires."
    - paper 253201868, introduction: "While wildfres cannot strictly be defned as meteorological hazards in the same way as droughts, foods and storms, fre danger is greater during periods of high temperature, minimal precipitation, low relative humidity and strong winds."
    - paper 53050065, meteorological conditions: "The strong winds and adiabatic compression associated with the downslope flow and mixing inhibited radiative cooling and nocturnal RH recovery."
    - paper 56076970, discussion and implications: "The SA wind events studied here are examples as dry and hot Foehn winds; these winds occur in the leeside of the mountain ranges and are associated with the elevated fire danger in many other parts of the world, including Europe and Australia (Sharples et al 2010)."
- [higher temperatures and aridity dry fuels, creating extreme fire‑weather]
    - paper 273287103, types of disturbances wildfires: "Beginning in the late twentieth century, increasing temperature and aridity [23,[59][60][61] have created more frequent extreme fireweather conditions, leading to more very large wildfires [62,63] and area burned at high severity [38,64], although sufficient fuels are necessary for this pattern to continue."
    - paper 268308343, drivers of lightning-induced fire: "An increase in the temperature causes the quick drying of wildland fuel, and the drier fuels are easy to ignite and endure a faster rate of fire spread."
    - paper 999274, background: "Drought-level rainfall, fire-susceptible vegetation fuels, high temperatures, and strong Santa Ana winds created an ideal fire weather environment for fast moving, high intensity burns."
    - paper 53050065, climatic basis: "The delayed arrival of autumn precipitation and continued warm temperatures leading up to the fire events allowed for dead fuel moistures to remain at levels more commonly found in mid-to-late summer."
- [humidity and vapor pressure deficit affect fire risk]
    - paper 255372301, results and discussion: "Both the NDVI and the SPFH have negative impacts on wildfire risks, while SPFH has a relatively weaker effect compared with that of NDVI. Note that, a higher NDVI indicates healthier vegetation with more water conditions and fewer potential fuels that can be ignited. Similarly, a high SPFH attaches potential fuels with more moisture, reducing the wildfire risk."
    - paper 247649715, abstract: "Additionally, among the individual climate variables that comprise the FWI, relative humidity and temperature are the most influential factors that affect the observed BA."
    - paper 247649715, discussion: "Globally, in the case of forest BA anomaly, the most highly associated climate variable is found to be relative humidity, while in the case of the non-forest BA anomaly, temperature and relative humidity are found to be most highly associated for most of the regions, without, however, exhibiting any clear spatial or latitudinal pattern."


## 7 · BI-P3-0008

### Question

How is fire‑weather danger projected to change in summer in Minnesota by late this century under a high‑emissions future, and what physical drivers are expected to cause this change?

### Answer

In summer, fire‑weather danger in Minnesota is projected to show a slight increase, a change similar to most states, by late this century under a high‑emissions future. Research shows that higher temperatures and increased aridity dry fuels, creating more extreme fire‑weather conditions.

### Table side

- Quantity: Seasonal value, under the dictionary's Wildfire columns (line 663; columns wildfire_summer_Hist, wildfire_summer_Endc, wildfire_summer_Dend), read as the summer Fire Weather Index (FWI): a fire-danger index, not fire occurrence
- Place: Minnesota (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: End-Century, 2085 to 2094
- Scenario: RCP8.5
- Statistic: change in the seasonal value (future minus baseline), unweighted mean over grid cells
- Values: mean 15.3 -> 16.8 (+1.5) (index value, no unit)
- Rank among State labels: 26 of 49 (largest change first)
- Grid cells: 1,465 (increasing: 1,191; decreasing: 274)
- Pattern descriptor (DR-DESC-1 v4): a slight increase; a change similar to most states
- working assumptions relied on: WA-FWI-SUMMER (R-004), WA-STATE-LABEL (R-005), WA-UNWEIGHTED-MEAN (R-008) --- owner-authorized (D-064), not confirmed

### Paper side

- Research shows (2 papers): higher temperatures and aridity dry fuels, creating extreme fire‑weather

### Original passages

- [higher temperatures and aridity dry fuels, creating extreme fire‑weather]
    - paper 273287103, types of disturbances wildfires: "Beginning in the late twentieth century, increasing temperature and aridity [23,[59][60][61] have created more frequent extreme fireweather conditions, leading to more very large wildfires [62,63] and area burned at high severity [38,64], although sufficient fuels are necessary for this pattern to continue."
    - paper 268308343, drivers of lightning-induced fire: "An increase in the temperature causes the quick drying of wildland fuel, and the drier fuels are easy to ignite and endure a faster rate of fire spread."
