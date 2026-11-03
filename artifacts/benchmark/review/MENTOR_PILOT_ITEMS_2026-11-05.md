# Pilot items for mentor review --- 2026-11-05

Five pilot benchmark items. Question and reference answer are COORDINATOR-proposed edits, not yet frozen. Same content as `MENTOR_PILOT_ITEMS_2026-11-05.xlsx` (sheets ITEMS and README).

## README

- **What the benchmark question is.** A closed-book question: the model under test gets only the Question --- no table, no paper, no data. It must answer from what it knows about projected climate hazards and their physical drivers.
- **How the answer is graded.** At the pattern level: direction of the change, rough magnitude (e.g. 'roughly tripling'), ranking where the question asks for one, and the mechanisms named. Exact values (the numbers in 'Table side') are provenance for the reference answer; the model is not expected to reproduce them.
- **What 'single study' means.** The statement is found in one paper of our literature corpus (after counting duplicate copies of a paper once). The reference answer then hedges it ('one study suggests'), and a grader does not require it as consensus.
- **Two questions for the mentor.** (1) Are table-only items (item 1: pattern identification, no literature) acceptable in the benchmark? (2) Are single-study mechanisms acceptable in a reference answer if they are labelled as single-study?

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

### Paper side

- none — table-only item (pattern identification)

### Original passages

- none


## 2 · BI-P2B-0003

### Question

How is the summer frequency of days with a dangerous heat index (above 95 °F) expected to change in California by mid-century under RCP8.5, and what are the main physical drivers of this change?

### Reference answer

California is projected to see a moderate increase (about half again as many) in summer days with a dangerous heat index (above 95 °F) by mid-century (2045–2054) under RCP8.5, one high-emissions scenario. The main driver is large-scale warming rather than changes in regional atmospheric circulation; land–atmosphere feedbacks that sustain heat waves in the Southwest add to it, and one study suggests that night-time intensification of the urban heat island under calm, clear conditions contributes locally.

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

### Paper side

- Observed increase in heat‑wave and drought frequency — supported by 4 independent papers; the statements used come from 2 of them
    - Large‑scale warming, rather than changes in regional atmospheric circulation, is identified as the primary driver of future increases in extreme heat index days. (paper 199098498)
    - Land-atmosphere feedbacks are a stronger factor for heat wave maintenance at southern latitudes, and misrepresentation of these feedbacks in models leads to poor forecast skill in the Southwest United States. (paper 158091651)
- urban heat island intensifies due to nighttime conditions and reduced moisture — supported by 3 independent papers; the statements used come from 2 of them
    - The urban heat island effect is most pronounced at night and under high‑pressure, calm, clear‑sky conditions. (paper 128765172)
    - During heat‑wave events, CUHI intensifies markedly, especially at night, because urban areas experience lower moisture and reduced wind speed. (paper 246243282)

### Original passages

- [Observed increase in heat‑wave and drought frequency]
- 199098498, late century results: "Identifying the climatological processes responsible for the increases in the frequency of high heat index days we identify is beyond the scope of this study."
    - [provenance note: this passage was recovered by prefix anchor and stops where the extraction agent's proposed passage, not verified against the paper text, continues: "However, recent work ... finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."]
- 158091651, abstract: "Land-atmosphere feedbacks appear to be a stronger factor for heat wave maintenance at southern latitudes, but the NCEP model seems to misrepresent those feedbacks, particularly over the Southwest United States, leading to poor skill in that region."
- [urban heat island intensifies due to nighttime conditions and reduced moisture]
- 128765172, introduction: "Further, the UHI is most noticeable at night and under synoptic high pressure systems with calm conditions and clear skies [24,[26][27][28], and the UHI has been measured in cities spanning many varying climate regimes and sizes [29][30][31][32]."
- 246243282, impact on temperature and heat waves: "In general, simulated CUHI values during a heat wave have intensified extensively relative to pre-heat wave conditions, mostly due to the lower moisture and reduced wind speed in urban areas during the heat wave."


## 3 · BI-P2B-0006

### Question

How is the summer frequency of days with a dangerous heat index (above 105 °F) expected to change in Alabama by the end of the century under RCP8.5, and what are the main physical drivers of this change?

### Reference answer

In Alabama, summer days with a dangerous heat index (above 105 °F) are projected to increase by the end of the century (2085–2094) under RCP8.5, more than tripling. The rise is driven primarily by large-scale warming, which increases the frequency, intensity and duration of heat waves. Because the heat index combines temperature and humidity, one study suggests the magnifying effect of humidity on heat stress grows as temperatures rise, and urban heat-island effects add to night-time heat in cities.

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
- urban heat island intensifies due to nighttime conditions and reduced moisture — supported by 3 independent papers; the statement used comes from 1 of them
    - The urban heat island effect is most pronounced at night and under high‑pressure, calm, clear‑sky conditions. (paper 128765172)

### Original passages

- [global warming increases heatwave frequency and intensity]
- 14006228, discussion: "As global warming continues, the frequency, intensity and duration of heatwaves are likely to increase."
- 235602877, introduction: "With climate change, heat waves have become more frequent and intense."
- 221504407, conclusion: "The occurrence of heat events is expected to increase due to the worsening effects of anthropogenic global warming [60]. This will be seen in both higher mean annual temperatures and in the frequency of heat shocks [37]."
- 199381463, introduction: "Climate change has resulted in a significant rise in the global mean temperature and it is predicted to get worse [23]. This means more extreme heat events and heat exposure for people working in agriculture in the hot climates."
- [Observed increase in heat‑wave and drought frequency]
- 199098498, late century results: "Identifying the climatological processes responsible for the increases in the frequency of high heat index days we identify is beyond the scope of this study."
    - [provenance note: this passage was recovered by prefix anchor and stops where the extraction agent's proposed passage, not verified against the paper text, continues: "However, recent work ... finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."]
- [humidity magnifies heat stress and its effect grows with temperature]
- 239996006, results: "at similar or lower humidity, the magnifying power of humidity increases with increasing T, i.e. similar or lower relative humidity levels will still cause greater human discomfort at higher temperatures."
- [urban heat island intensifies due to nighttime conditions and reduced moisture]
- 128765172, introduction: "Further, the UHI is most noticeable at night and under synoptic high pressure systems with calm conditions and clear skies [24,[26][27][28], and the UHI has been measured in cities spanning many varying climate regimes and sizes [29][30][31][32]."


## 4 · BI-P2B-0007

### Question

How will the number of summer days with a dangerous heat index (above 95 °F) change by mid-century under RCP8.5 across the U.S. NCA5 climate regions — which region is projected to see the largest increase and which the smallest — and what are the main physical drivers?

### Reference answer

By mid-century (2045–2054) under RCP8.5, one high-emissions scenario, summer days with a dangerous heat index (above 95 °F) increase in every NCA5 climate region, with the largest increase in the Southeast and the smallest in Alaska. The increases are driven by large-scale warming; land–atmosphere feedbacks are a stronger factor for heat-wave maintenance at southern latitudes, and one study suggests that humidity magnifies heat stress more as temperatures rise.

### Table side

- Quantity: Number of Summer days with daily max heat index above 95 F (data dictionary, columns heatindex_HIS_Day95, heatindex_M85_Day95)
- Geography: NCA5 regions --- the 8 with a State label in the table (no U.S. Caribbean, no Hawai'i / U.S.-Affiliated Pacific Islands)
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

### Paper side

- Observed increase in heat‑wave and drought frequency — supported by 3 independent papers; the statements used come from 2 of them
    - Large‑scale warming, rather than changes in regional atmospheric circulation, is identified as the primary driver of future increases in extreme heat index days. (paper 199098498)
    - Land-atmosphere feedbacks are a stronger factor for heat wave maintenance at southern latitudes, and misrepresentation of these feedbacks in models leads to poor forecast skill in the Southwest United States. (paper 158091651)
- humidity magnifies heat stress and its effect grows with temperature — single study (1 paper)
    - The magnifying effect of relative humidity on heat stress grows with increasing temperature, so that even unchanged or lower humidity can cause greater discomfort at higher temperatures. (paper 239996006)

### Original passages

- [Observed increase in heat‑wave and drought frequency]
- 199098498, late century results: "Identifying the climatological processes responsible for the increases in the frequency of high heat index days we identify is beyond the scope of this study."
    - [provenance note: this passage was recovered by prefix anchor and stops where the extraction agent's proposed passage, not verified against the paper text, continues: "However, recent work ... finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."]
- 158091651, abstract: "Land-atmosphere feedbacks appear to be a stronger factor for heat wave maintenance at southern latitudes, but the NCEP model seems to misrepresent those feedbacks, particularly over the Southwest United States, leading to poor skill in that region."
- [humidity magnifies heat stress and its effect grows with temperature]
- 239996006, results: "at similar or lower humidity, the magnifying power of humidity increases with increasing T, i.e. similar or lower relative humidity levels will still cause greater human discomfort at higher temperatures."


## 5 · BI-P2B-0010

### Question

How is the number of summer days with a dangerous heat index (above 95 °F) in Florida expected to change by mid-century under a high-emissions scenario compared with a moderate one, and what are the main drivers and uncertainties?

### Reference answer

Under RCP8.5, one high-emissions scenario, Florida's summer days with a dangerous heat index (above 95 °F) are projected to roughly triple by mid-century (2045–2054). The main driver is large-scale warming, which raises heat-wave frequency, intensity and duration; one study suggests that humidity's magnifying effect on heat stress grows with temperature. The size of the change depends on the emissions pathway: one study reports heat-wave duration about one day longer under RCP8.5 than under the moderate RCP4.5 scenario, and no moderate-scenario projection of this quantity is available in the table used here, so the contrast rests on the literature alone. RCP8.5 should be read as one plausible high-emissions future, not a forecast.

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
- 199098498, late century results: "Identifying the climatological processes responsible for the increases in the frequency of high heat index days we identify is beyond the scope of this study."
    - [provenance note: this passage was recovered by prefix anchor and stops where the extraction agent's proposed passage, not verified against the paper text, continues: "However, recent work ... finds that large-scale warming, rather than changes in regional circulation, is the primary driver of future changes in extreme heat (Schoof et al 2019)."]
- [humidity magnifies heat stress and its effect grows with temperature]
- 239996006, results: "at similar or lower humidity, the magnifying power of humidity increases with increasing T, i.e. similar or lower relative humidity levels will still cause greater human discomfort at higher temperatures."
- [heat‑wave frequency, intensity and duration are projected to increase]
- 5882914, characteristics of heat waves: "Average heat wave durations estimated under the RCP8.5 scenario were almost 1 day longer than under the RCP4.5 scenario, regardless of the heat wave definition used (Table 3)."
