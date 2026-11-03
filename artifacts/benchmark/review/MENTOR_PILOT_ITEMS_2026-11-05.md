# Pilot items for mentor review --- 2026-11-05

Five pilot benchmark items. Question and reference answer are COORDINATOR-proposed edits (v2, 2026-11-03), not yet frozen. Same content as `MENTOR_PILOT_ITEMS_2026-11-05.xlsx` (sheets ITEMS and README).

## README

- **What the benchmark question is.** A closed-book question: the model under test gets only the Question --- no table, no paper, no data. It must answer from what it knows about projected climate hazards and their physical drivers.
- **How the answer is graded.** At the pattern level: direction of the change, rough magnitude (e.g. 'roughly tripling'), ranking where the question asks for one, and the mechanisms named. Exact values (the numbers in 'Table side') are provenance for the reference answer; the model is not expected to reproduce them.
- **What 'single study' means.** The statement is found in one paper of our literature corpus (after counting duplicate copies of a paper once). The reference answer then hedges it ('one study suggests'), and a grader does not require it as consensus.
- **Two questions for the mentor.** (1) Are table-only items (item 1: pattern identification, no literature) acceptable in the benchmark? (2) Are single-study mechanisms acceptable in a reference answer if they are labelled as single-study?
- **Papers citing earlier work.** Where a mechanism rests on a paper citing earlier work, the answer says so ('one study, citing earlier work…').

## 1 · BI-P2B-0001

### Question

How is the number of summer days with a dangerous heat index (above 95 °F) expected to change in Georgia by mid-century under RCP8.5, and roughly how large is the change?

### Reference answer

In Georgia, the number of summer days with a dangerous heat index (above 95 °F) is projected to increase by mid-century (2045–2054) under RCP8.5, roughly tripling relative to the modeled historical baseline. RCP8.5 is one high-emissions scenario, not a forecast, and the baseline is model output, not an observation.

### Table side

- Quantity: Number of Summer days with daily max heat index above 95 F (data dictionary, columns heatindex_HIS_Day95, heatindex_M85_Day95)
- Geography: Georgia (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: Mid-Century, 2045 to 2054
- Scenario: RCP8.5
- Statistic: direction of the change in the mean number of days (future minus baseline)
- Value: mean 15.8 days -> 44.9 days (+29.2 days)
- Grid cells: 1,031 (cells increasing: 1,031)
- State label provisional (IC-012)
- unweighted mean over grid cells (provisional aggregation rule)
- Pattern descriptor (DR-DESC-1 v2): roughly tripling; from about 16 to about 45 days

### Paper side

- none — table-only item (pattern identification)

### Original passages

- none


## 2 · BI-P2B-0003

### Question

How is the summer frequency of days with a dangerous heat index (above 95 °F) expected to change in California by mid-century under RCP8.5, and what are the main physical drivers of this change?

### Reference answer

California is projected to see a moderate increase (about half again as many) in summer days with a dangerous heat index (above 95 °F) by mid-century (2045–2054) under RCP8.5, one high-emissions scenario. Warming is the main driver: one study, citing earlier CMIP5 work, identifies large-scale warming rather than changes in regional circulation as the primary driver of future changes in extreme heat, and global warming is expected to increase the frequency, intensity and duration of heat waves. One study suggests that land–atmosphere feedbacks appear to be a stronger factor in sustaining heat waves in the Southwest.

### Table side

- Quantity: Number of Summer days with daily max heat index above 95 F (data dictionary, columns heatindex_HIS_Day95, heatindex_M85_Day95)
- Geography: California (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: Mid-Century, 2045 to 2054
- Scenario: RCP8.5
- Statistic: change in the mean number of days (future minus baseline)
- Value: mean 15.4 days -> 24.4 days (+9.0 days)
- Rank among State labels: 25 of 49 (largest change first)
- Grid cells: 2,827 (cells increasing: 2,681)
- State label provisional (IC-012)
- unweighted mean over grid cells (provisional aggregation rule)
- Pattern descriptor (DR-DESC-1 v2): a moderate increase (about half again as many); from about 15 to about 24 days

### Paper side

- Observed increase in heat‑wave and drought frequency — supported by 4 independent papers; the statements used come from 2 of them
    - Large‑scale warming, rather than changes in regional atmospheric circulation, is identified as the primary driver of future increases in extreme heat index days. (paper 199098498)
    - Land-atmosphere feedbacks are a stronger factor for heat wave maintenance at southern latitudes, and misrepresentation of these feedbacks in models leads to poor forecast skill in the Southwest United States. (paper 158091651)
- global warming increases heatwave frequency and intensity — supported by 4 independent papers; the statements used come from 4 of them (in the item's packet; cited by the edited answer, not by the generated item)
    - Projected climate warming is expected to increase the frequency, intensity, and duration of heatwaves, thereby elevating heat‑stress risk. (paper 14006228)
    - Climate change is causing heat waves to occur more often and with greater intensity. (paper 235602877)
    - Anthropogenic global warming is expected to increase both the mean annual temperature and the frequency of heat events. (paper 221504407)
    - Global warming is expected to increase the frequency of extreme heat events, raising heat exposure for agricultural workers. (paper 199381463)

### Original passages

- [Observed increase in heat‑wave and drought frequency]
- 199098498, late century results: "However, recent work examining changes in the frequency of different types of extreme heat days (considering both temperature and humidity) in CMIP5 projections after using a multivariate quantile mapping approach similar to the MACA methodology finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."
    - passage corrected by reviewer verification (D-057); the agent's original passage is kept in provenance
- 158091651, abstract: "Land-atmosphere feedbacks appear to be a stronger factor for heat wave maintenance at southern latitudes, but the NCEP model seems to misrepresent those feedbacks, particularly over the Southwest United States, leading to poor skill in that region."
- [global warming increases heatwave frequency and intensity]
- 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
- 235602877, introduction: "With climate change, heat waves have become more frequent and intense."
- 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
- 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."


## 3 · BI-P2B-0006

### Question

How is the summer frequency of days with a dangerous heat index (above 105 °F) expected to change in Alabama by the end of the century under RCP8.5, and what are the main physical drivers of this change?

### Reference answer

In Alabama, summer days with a dangerous heat index (above 105 °F) are projected to rise from rare — about 1 day per summer in the modeled historical baseline — to about 45 days by the end of the century (2085–2094) under RCP8.5, one high-emissions scenario. The rise is driven by warming: global warming is expected to increase the frequency, intensity and duration of heat waves, and one study, citing earlier CMIP5 work, identifies large-scale warming rather than regional circulation change as the primary driver of future changes in extreme heat. Because the heat index combines temperature and humidity, one study suggests the magnifying effect of humidity on heat stress grows as temperatures rise.

### Table side

- Quantity: Number of Summer days with daily max heat index above 105 F (data dictionary, columns heatindex_HIS_Day105, heatindex_E85_Day105)
- Geography: Alabama (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: End-Century, 2085 to 2094
- Scenario: RCP8.5
- Statistic: change in the mean number of days (future minus baseline)
- Value: mean 1.4 days -> 45.2 days (+43.9 days)
- Rank among State labels: 7 of 49 (largest change first)
- Grid cells: 934 (cells increasing: 934)
- State label provisional (IC-012)
- unweighted mean over grid cells (provisional aggregation rule)
- Pattern descriptor (DR-DESC-1 v2): rising from rare to common; from about 1 day to about 45 days

### Paper side

- global warming increases heatwave frequency and intensity — supported by 4 independent papers; the statements used come from 4 of them
    - Projected climate warming is expected to increase the frequency, intensity, and duration of heatwaves, thereby elevating heat‑stress risk. (paper 14006228)
    - Climate change is causing heat waves to occur more often and with greater intensity. (paper 235602877)
    - Anthropogenic global warming is expected to increase both the mean annual temperature and the frequency of heat events. (paper 221504407)
    - Global warming is expected to increase the frequency of extreme heat events, raising heat exposure for agricultural workers. (paper 199381463)
- Observed increase in heat‑wave and drought frequency — supported by 2 independent papers; the statement used comes from 1 of them
    - Large‑scale warming, rather than changes in regional atmospheric circulation, is identified as the primary driver of future increases in extreme heat index days. (paper 199098498)
- heat index combines temperature and humidity as a perceived‑heat metric — review-supported (11 papers); the statements used come from 2 of them (in the item's packet; cited by the edited answer, not by the generated item)
    - The heat index combines temperature and relative humidity to represent perceived temperature and underlies US National Weather Service heat advisories. (paper 199098498)
    - The heat index, also known as the apparent temperature, is a metric that combines air temperature and relative humidity to give an accurate representation of how hot it feels to the human body. (paper 269945312)
- humidity magnifies heat stress and its effect grows with temperature — single study (1 paper)
    - The magnifying effect of relative humidity on heat stress grows with increasing temperature, so that even unchanged or lower humidity can cause greater discomfort at higher temperatures. (paper 239996006)

### Original passages

- [global warming increases heatwave frequency and intensity]
- 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
- 235602877, introduction: "With climate change, heat waves have become more frequent and intense."
- 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
- 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."
- [Observed increase in heat‑wave and drought frequency]
- 199098498, late century results: "However, recent work examining changes in the frequency of different types of extreme heat days (considering both temperature and humidity) in CMIP5 projections after using a multivariate quantile mapping approach similar to the MACA methodology finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."
    - passage corrected by reviewer verification (D-057); the agent's original passage is kept in provenance
- [heat index combines temperature and humidity as a perceived‑heat metric]
- 199098498, introduction: "In contrast, the heat index (HI; also known as apparent temperature) combines temperature and relative humidity to produce a 'feels like' temperature. The HI serves as a primary basis for the issuance of heat advisories by the US National Weather Service (NWS) and has been correlated to heat-related mortality (Davis et al 2003)."
- 269945312, introduction: "The heat index, also known as the apparent temperature, is a metric that combines air temperature and relative humidity to give an accurate representation of how hot it feels to the human body."
- [humidity magnifies heat stress and its effect grows with temperature]
- 239996006, results: "at similar or lower humidity, the magnifying power of humidity increases with increasing T, i.e. similar or lower relative humidity levels will still cause greater human discomfort at higher temperatures."


## 4 · BI-P2B-0007

### Question

How will the number of summer days with a dangerous heat index (above 95 °F) change by mid-century under RCP8.5 across the U.S. NCA5 climate regions — which region is projected to see the largest increase and where is the change smallest — and what are the main physical drivers?

### Reference answer

By mid-century (2045–2054) under RCP8.5, one high-emissions scenario, summer days with a dangerous heat index (above 95 °F) increase in the eight NCA5 climate regions covered, with the largest increase in the Southeast and essentially no change in Alaska. The increases are driven by warming: global warming is expected to raise heat-wave frequency, intensity and duration, and one study, citing earlier CMIP5 work, identifies large-scale warming rather than regional circulation change as the primary driver of future changes in extreme heat. One study finds that land–atmosphere feedbacks appear to be a stronger factor for heat-wave maintenance at southern latitudes, and one study suggests that humidity magnifies heat stress more as temperatures rise.

### Table side

- Quantity: Number of Summer days with daily max heat index above 95 F (data dictionary, columns heatindex_HIS_Day95, heatindex_M85_Day95)
- Geography: NCA5 regions --- the 8 with a State label in the table (no U.S. Caribbean, no Hawai'i / U.S.-Affiliated Pacific Islands)
- Not covered (2 of the 10 NCA5 regions; no State label in the table): U.S. Caribbean; Hawai'i and U.S.-Affiliated Pacific Islands
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: Mid-Century, 2045 to 2054
- Scenario: RCP8.5
- Statistic: change in the mean number of days (future minus baseline), per region; regions ranked largest first
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
- State label provisional (IC-012)
- unweighted mean over grid cells (provisional aggregation rule)
- Pattern descriptor (DR-DESC-1 v2): the largest increase: Southeast; essentially no change: Alaska

### Paper side

- Observed increase in heat‑wave and drought frequency — supported by 3 independent papers; the statements used come from 2 of them
    - Large‑scale warming, rather than changes in regional atmospheric circulation, is identified as the primary driver of future increases in extreme heat index days. (paper 199098498)
    - Land-atmosphere feedbacks are a stronger factor for heat wave maintenance at southern latitudes, and misrepresentation of these feedbacks in models leads to poor forecast skill in the Southwest United States. (paper 158091651)
- global warming increases heatwave frequency and intensity — supported by 4 independent papers; the statements used come from 4 of them (in the item's packet; cited by the edited answer, not by the generated item)
    - Projected climate warming is expected to increase the frequency, intensity, and duration of heatwaves, thereby elevating heat‑stress risk. (paper 14006228)
    - Climate change is causing heat waves to occur more often and with greater intensity. (paper 235602877)
    - Anthropogenic global warming is expected to increase both the mean annual temperature and the frequency of heat events. (paper 221504407)
    - Global warming is expected to increase the frequency of extreme heat events, raising heat exposure for agricultural workers. (paper 199381463)
- humidity magnifies heat stress and its effect grows with temperature — single study (1 paper)
    - The magnifying effect of relative humidity on heat stress grows with increasing temperature, so that even unchanged or lower humidity can cause greater discomfort at higher temperatures. (paper 239996006)

### Original passages

- [Observed increase in heat‑wave and drought frequency]
- 199098498, late century results: "However, recent work examining changes in the frequency of different types of extreme heat days (considering both temperature and humidity) in CMIP5 projections after using a multivariate quantile mapping approach similar to the MACA methodology finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."
    - passage corrected by reviewer verification (D-057); the agent's original passage is kept in provenance
- 158091651, abstract: "Land-atmosphere feedbacks appear to be a stronger factor for heat wave maintenance at southern latitudes, but the NCEP model seems to misrepresent those feedbacks, particularly over the Southwest United States, leading to poor skill in that region."
- [global warming increases heatwave frequency and intensity]
- 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
- 235602877, introduction: "With climate change, heat waves have become more frequent and intense."
- 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
- 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."
- [humidity magnifies heat stress and its effect grows with temperature]
- 239996006, results: "at similar or lower humidity, the magnifying power of humidity increases with increasing T, i.e. similar or lower relative humidity levels will still cause greater human discomfort at higher temperatures."


## 5 · BI-P2B-0010

### Question

How is the number of summer days with a dangerous heat index (above 95 °F) in Florida expected to change by mid-century under a high-emissions scenario compared with a moderate one, and what are the main drivers and uncertainties?

### Reference answer

Under RCP8.5, one high-emissions scenario, Florida's summer days with a dangerous heat index (above 95 °F) are projected to roughly triple by mid-century (2045–2054). Warming is the main driver: global warming is expected to raise heat-wave frequency, intensity and duration, and one study, citing earlier CMIP5 work, identifies large-scale warming rather than regional circulation change as the primary driver of future changes in extreme heat; one study suggests that humidity's magnifying effect on heat stress grows with temperature. The change is scenario-dependent: one study of the eastern United States reports heat-wave duration almost one day longer under RCP8.5 than under the moderate RCP4.5 scenario. RCP8.5 should be read as one plausible high-emissions future, not a forecast.

### Table side

- Quantity: Number of Summer days with daily max heat index above 95 F (data dictionary, columns heatindex_HIS_Day95, heatindex_M85_Day95)
- Geography: Florida (State label in the table)
- Season: summer
- Baseline window: Historical, 1995 to 2004 (modeled)
- Future window: Mid-Century, 2045 to 2054
- Scenario: RCP8.5
- Statistic: change in the mean number of days (future minus baseline)
- Value: mean 25.7 days -> 68.2 days (+42.4 days)
- Rank among State labels: 1 of 49 (largest change first)
- Grid cells: 1,165 (cells increasing: 1,165)
- State label provisional (IC-012)
- unweighted mean over grid cells (provisional aggregation rule)
- Pattern descriptor (DR-DESC-1 v2): roughly tripling; from about 26 to about 68 days

### Paper side

- global warming increases heatwave frequency and intensity — supported by 4 independent papers; the statements used come from 4 of them
    - Projected climate warming is expected to increase the frequency, intensity, and duration of heatwaves, thereby elevating heat‑stress risk. (paper 14006228)
    - Climate change is causing heat waves to occur more often and with greater intensity. (paper 235602877)
    - Anthropogenic global warming is expected to increase both the mean annual temperature and the frequency of heat events. (paper 221504407)
    - Global warming is expected to increase the frequency of extreme heat events, raising heat exposure for agricultural workers. (paper 199381463)
- Observed increase in heat‑wave and drought frequency — supported by 2 independent papers; the statement used comes from 1 of them
    - Large‑scale warming, rather than changes in regional atmospheric circulation, is identified as the primary driver of future increases in extreme heat index days. (paper 199098498)
- humidity magnifies heat stress and its effect grows with temperature — single study (1 paper)
    - The magnifying effect of relative humidity on heat stress grows with increasing temperature, so that even unchanged or lower humidity can cause greater discomfort at higher temperatures. (paper 239996006)
- heat‑wave frequency, intensity and duration are projected to increase — single study (1 paper)
    - Average heat‑wave duration is projected to be about one day longer under the high‑emission RCP8.5 scenario than under the moderate RCP4.5 scenario, regardless of the heat‑wave definition used. (paper 5882914)

### Original passages

- [global warming increases heatwave frequency and intensity]
- 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
- 235602877, introduction: "With climate change, heat waves have become more frequent and intense."
- 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
- 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."
- [Observed increase in heat‑wave and drought frequency]
- 199098498, late century results: "However, recent work examining changes in the frequency of different types of extreme heat days (considering both temperature and humidity) in CMIP5 projections after using a multivariate quantile mapping approach similar to the MACA methodology finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."
    - passage corrected by reviewer verification (D-057); the agent's original passage is kept in provenance
- [humidity magnifies heat stress and its effect grows with temperature]
- 239996006, results: "at similar or lower humidity, the magnifying power of humidity increases with increasing T, i.e. similar or lower relative humidity levels will still cause greater human discomfort at higher temperatures."
- [heat‑wave frequency, intensity and duration are projected to increase]
- 5882914, characteristics of heat waves: "Average heat wave durations estimated under the RCP8.5 scenario were almost 1 day longer than under the RCP4.5 scenario, regardless of the heat wave definition used (Table 3)."
