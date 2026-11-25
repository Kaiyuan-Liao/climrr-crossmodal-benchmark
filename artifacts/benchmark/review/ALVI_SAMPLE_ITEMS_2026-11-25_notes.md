# Notes for Kaiyuan --- Alvi sample sheet 2026-11-25

Companion to `ALVI_SAMPLE_ITEMS_2026-11-25.md` (not for Alvi). Built by `scripts/build_mentor_sheet.py --audience alvi`; no model call.

## Run history

- **Infra synthesis run 1** (agent v5.3, packets v1a, source `b860658`): 2 pass (BI-P5-0001, 0003), 6 rejected, all template conformance. Superseded; polish run 1 polished 0003, rejected 0001. Its two passing items are now the regression fixture (they pass post-checks v3.5 against their v1a packets; budget reported, not enforced).
- **Infra synthesis run 2** (agent v5.4, packets v1b, source `bf69970`; D-080): first pass 5 of 8; BI-P5-0002, 0003 and 0005 redrawn once each -> 0002 passed; **6 pass, 2 rejected after a second attempt**.
- **Polish infra run 2** (agent v1.1, checks v2): 4 polished (0002, 0004, 0006, 0007), 2 rejected (0001 places, 0008 hedges).
- **D-079 display rule** (polished only if it also passes post-checks v3.5): only BI-P5-0002 shows its polished text; 0004 and 0006 rewrites split sentences beyond the answer-shape budget, 0007's rewrite drops the 'In general,' scope opener; 0001 and 0008 were polish-rejected.
- **COORDINATOR display edits** (`P5_display_edits_v1.yaml`): leakage v2.3 failures 0; post-checks v3.5 failures 3 (BI-P5-0001, BI-P5-0002, BI-P5-0004), 0 with only the closing clause put back (`P5_display_edits_v1_checks.json`). The closing-clause edit ('All six') applies where the clause exists: BI-P5-0001, BI-P5-0002, BI-P5-0004; BI-P5-0006, BI-P5-0007, BI-P5-0008 carry none (D-069: they cite a California-specific driver group, and post-checks v3.5 fail a clause there), so none was added --- for the COORDINATOR.

## The two dropped cells

- **BI-P5-0003** (Water and Wastewater Sector, heat index, California): rejected_pre_review, redraws 2 --- doubled magnitude phrase ('increase a moderate increase'), on both attempts. Not on the sheet.
- **BI-P5-0005** (Energy Sector, fire weather index, California): rejected_pre_review, redraws 2 --- a sentence citing a two-hop group without its two-hop marker (second attempt). Not on the sheet.

## What each item rests on

### 1 · BI-P5-0001 --- energy / heat (Virginia)

- Table: heat index, Virginia; more than tripling; a change similar to most states; from about 4 to about 16 days a summer.
- Place-named impact evidence: yes (cited impact groups resting on papers that name Virginia: 1).
- Cited: 3 impact group(s), 2 driver group(s); two-hop: wildfire risk to power transmission lines.
- Display: original (D-079 re-check of the polished text: fail --- integrated: closing clause (D-069) missing at the end: 'These are general drivers of dangerous heat-index days, not findings specific to Virginia.'; integrated: scope phrase (D-069): a sentence naming research must begin with one of the cited scope phrases: 'Research shows that large-scale warming and land–atmosphere '; integrated: scope phrase (D-069): a sentence naming research must begin with one of the cited scope phrases: 'Research shows that global warming increases heatwave freque'; integrated: scope phrase (D-069): a sentence naming research must begin with one of the cited scope phrases: 'Research shows that extreme heat can reduce generation outpu'; integrated: scope phrase (D-069): a sentence naming research must begin with one of the cited scope phrases: 'Research shows that such heat raises electricity demand and '; integrated: scope phrase (D-069): a sentence naming research must begin with one of the cited scope phrases: 'Research shows that when wildfires occur, they increase igni'); COORDINATOR edits: closing_clause, BI-P5-0001#1.

### 2 · BI-P5-0002 --- transportation / heat (Arizona)

- Table: heat index, Arizona; a moderate increase; a change similar to most states; from about 14 to about 24 days a summer.
- Place-named impact evidence: yes (cited impact groups resting on papers that name Arizona: 1).
- Cited: 2 impact group(s), 2 driver group(s); two-hop: heat‑driven vegetation fires threaten railway corridors.
- Display: polished (D-079 re-check of the polished text: pass); COORDINATOR edits: closing_clause, us_southwest_opener, BI-P5-0002#1, BI-P5-0002#2.

### 3 · BI-P5-0004 --- healthcare / heat (California)

- Table: heat index, California; a moderate increase; a change similar to most states; from about 15 to about 24 days a summer.
- Place-named impact evidence: no (no impact statement in our corpus names California; general evidence only).
- Cited: 2 impact group(s), 2 driver group(s); two-hop: none.
- Display: original (D-079 re-check of the polished text: fail --- integrated: rung 8 answer shape (D-075a): at most 6 sentences, no more than the reference sentences (found 8)); COORDINATOR edits: closing_clause.

### 4 · BI-P5-0006 --- transportation / fire weather (California)

- Table: fire weather index, California; a slight increase; a larger change than in most states.
- Place-named impact evidence: no (no impact statement in our corpus names California; general evidence only).
- Cited: 3 impact group(s), 2 driver group(s); two-hop: wildfire activity increases road network exposure to fire.
- Display: original (D-079 re-check of the polished text: fail --- integrated: rung 8 answer shape (D-075a): at most 6 sentences, no more than the reference sentences (found 8)); no COORDINATOR edit applies.

### 5 · BI-P5-0007 --- emergency services / fire weather (California)

- Table: fire weather index, California; a slight increase; a larger change than in most states.
- Place-named impact evidence: no (no impact statement in our corpus names California; general evidence only).
- Cited: 1 impact group(s), 2 driver group(s); two-hop: none.
- Display: original (D-079 re-check of the polished text: fail --- integrated: scope phrase (D-069): a sentence naming research must begin with one of the cited scope phrases: 'Research shows that humidity and vapor pressure deficit affe'; integrated: scope phrase (D-069): a sentence naming research must begin with one of the cited scope phrases: 'Research suggests that fire‑weather danger can increase dail'; integrated: rung 8 answer shape (D-075a): at most 4 sentences, no more than the reference sentences (found 5)); COORDINATOR edits: BI-P5-0007#1.

### 6 · BI-P5-0008 --- communications / fire weather (California)

- Table: fire weather index, California; a slight increase; a larger change than in most states.
- Place-named impact evidence: no (no impact statement in our corpus names California; general evidence only).
- Cited: 1 impact group(s), 2 driver group(s); two-hop: none.
- Display: original (D-079 re-check of the polished text: fail --- integrated: rung 8 answer shape (D-075a): at most 3 sentences, no more than the reference sentences (found 4)); no COORDINATOR edit applies.
