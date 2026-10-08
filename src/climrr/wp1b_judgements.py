"""M4-WP1b adjudication: the adjudicator's recorded judgements on aligned pairs.

The adjudicator is the **WP1 EXECUTOR**, which was prototype-exposed and wrote
reader 1. These judgements are read only from the two recorded claims and the
spans they cite --- **no paper was re-read** to make them. `climrr.wp1b`
checks every entry against the rules; it does not trust them.

Per aligned pair (keyed by the reader-1 claim id), per dimension whose two
recorded values are not textually identical:

* `content`: `same` (the two values assert the same thing; wording or which
  dimension holds the driver differs) or `differs` (one asserts content the
  other does not);
* `explicit_span_states`: for explicit-vs-inferred, whether the explicit
  reader's cited span actually states the adopted value (rule 3's "check");
* `adopted`: the value adopted under rule 3, **limited to what the cited span
  states** (the operational reading of "more conservative" used throughout:
  where the readers' values differ in extent, the adopted value is the part
  both support and the span states, never the union); `support_from` names
  whose span supports it (`r1`, `r2`, or `r1_evidence` / `r2_evidence`);
* `override`: a post-rule judgement, with an id and a reason, reported
  separately from the rule result.
"""

from __future__ import annotations

_NWA = {"value": "Northwest Atlantic (the region of the species studied, per the title)",
        "tag": "inferred", "support_from": "r1"}
_NWA_J = {"content": "differs", "adopted": _NWA,
          "note": "Both infer Northwest Atlantic from the same title span. Reader 2 adds 'temperate estuaries', "
                  "which its cited span (the title) does not state; reader 1 adds a laboratory caveat. Adopted: the "
                  "part both state and the span supports."}

_DHS_ALT = ("Reader 2's site-level value (Dinghushan natural reserve, Guangdong Province) is supported by its own "
            "methods span but tagged inferred; it is recorded here, not adopted.")

_FM_GEO = {"content": "same", "explicit_span_states": True,
           "adopted": {"value": "Fortescue Marsh, inland northwest Australia", "tag": "explicit", "support_from": "r1"},
           "note": "Both name the Fortescue Marsh. Reader 1 tags it explicit via the abstract span 'the Fortescue Marsh, "
                   "the largest water feature of inland northwest Australia'; reader 2 tags the same link inferred. "
                   "The span states 'Fortescue Marsh' and 'inland northwest Australia' but not 'upper Fortescue River "
                   "catchment', 'semi-arid' or 'Pilbara', which both readers' values add; adopted trimmed to the span."}

_SMOKE_OVERRIDE = {
    "judgement_id": "J-1",
    "adopted": {"value": "simulated wildfire smoke versus filtered air, 2 h/d, 5 d/wk, for 16 wk",
                "tag": "explicit", "support_from": "r2"},
    "reason": ("Both readers record the same 16-week exposure regimen from the same experimental-design sentence "
               "(reader 1's span lies inside reader 2's) but under different dimensions: reader 1 as temporal_frame, "
               "reader 2 as experimental_condition. Rule 3a applied literally sets both to unknown and so loses a "
               "fact both readers found. D-017 placed laboratory treatments in experimental_condition; the regimen "
               "is a treatment, not the period of a hazard. Adopted in experimental_condition, limited to what "
               "reader 2's span states (strain and target concentration in reader 2's value are not in its span). "
               "temporal_frame stays unknown by rule 3a."),
}

_SMOKE_TEMPORAL = {"content": "differs", "note": "Reader 1 files the exposure regimen here; reader 2 leaves it unknown and files it under experimental_condition."}
_SMOKE_EXP = {"content": "differs", "override": _SMOKE_OVERRIDE,
              "note": "Reader 1 unknown; reader 2 explicit. Rule 3a gives unknown; see override J-1."}

PAIR_JUDGEMENTS: dict[str, dict] = {
    # --- LIT-000191 (bivalves) ---------------------------------------------------
    "LIT-000191-C1": {
        "concept": {"content": "same", "note": "Reader 1 puts the drivers (temperature, CO2) in concept, reader 2 in the relation; the proposition is the same."},
        "relation_or_direction": {"content": "same", "note": "Both: each significantly depressed; additive."},
        "geography": _NWA_J,
        "experimental_condition": {"content": "same", "note": "Both: 24 and 28 °C and ~250, 390, 750 ppm CO2, laboratory treatments; cited from different but consistent spans."},
    },
    "LIT-000191-C2": {
        "concept": {"content": "differs",
                    "adopted": {"value": "higher temperatures; juvenile M. mercenaria, A. irradians and C. virginica",
                                "tag": "explicit", "support_from": "r2_evidence"},
                    "note": "Reader 1's evidence covers two sentences (temperature and CO2 effects on juveniles); reader 2's covers the temperature sentence only. Adopted: the temperature part both found. The CO2 sentence remains reader-1-only content within this claim."},
        "relation_or_direction": {"content": "differs",
                                  "adopted": {"value": "negatively impacted by higher temperatures (M. mercenaria, A. irradians); C. virginica juveniles not",
                                              "tag": "explicit", "support_from": "r2_evidence"},
                                  "note": "As for concept: the CO2 half is reader-1-only."},
        "geography": _NWA_J,
        "experimental_condition": {"content": "differs",
                                   "adopted": {"value": "juvenile treatments at 24 or 28 °C", "tag": "explicit", "support_from": "r2"},
                                   "note": "Reader 1's support span states only the CO2 levels (~400, 1700 ppm); reader 2's states only the temperatures and adds '45 days', which its span does not state. Adopted: the temperatures, matching the adopted temperature-only scope, stated by reader 2's span."},
    },
    "LIT-000191-C3": {
        "concept": {"content": "same", "note": "Elevated CO2; larval vs juvenile vulnerability."},
        "geography": _NWA_J,
        "experimental_condition": {"content": "differs", "note": "Reader 1 unknown; reader 2 lists larval and juvenile CO2 levels, but its support span states only the juvenile levels."},
    },
    "LIT-000191-C4": {
        "concept": {"content": "same", "note": "Drivers in concept (reader 1) or relation (reader 2)."},
        "relation_or_direction": {"content": "same", "note": "Both keep the hedges 'suggest' and 'likely'."},
        "geography": {"content": "differs", "note": "Reader 1 unknown ('coastal' is a setting, not a geography); reader 2 'coastal', explicit."},
        "temporal_frame": {"content": "same", "note": "Both 'current and future'."},
        "experimental_condition": {"content": "differs", "note": "Reader 1 unknown; reader 2 'inference drawn from the laboratory experiments', tagged inferred."},
    },
    # --- LIT-000381 (Dinghushan forest) -----------------------------------------
    "LIT-000381-C1": {
        "concept": {"content": "same", "note": "Reader 1 lists the drivers in concept; reader 2 in the relation."},
        "relation_or_direction": {"content": "same", "note": "Same traits; due to soil dryness and disturbance."},
        "geography": {"content": "differs", "explicit_span_states": True,
                      "adopted": {"value": "old-growth subtropical forest in southern China", "tag": "explicit", "support_from": "r1"},
                      "note": "Reader 1's span ('an old-growth subtropical forest in southern China') does not state Dinghushan or Guangdong, which its value adds. Adopted: what that span states. " + _DHS_ALT},
    },
    "LIT-000381-C2": {
        "concept": {"content": "differs",
                    "adopted": {"value": "quadrats' trait value changes", "tag": "explicit", "support_from": "r1_evidence"},
                    "note": "Reader 1's concept names soil dryness and disturbance as explicit, but the evidence span says only 'These two factors'; reader 2 places that identification in an inferred relation. Adopted concept: what the span states. The identification of the two factors rests on the preceding sentence (reader 2's inferred support span) and is not adopted as explicit."},
        "relation_or_direction": {"content": "differs", "explicit_span_states": True,
                                  "adopted": {"value": "explained 47-58% together", "tag": "explicit", "support_from": "r1_evidence"},
                                  "note": "'explained 47-58% together' is stated in the evidence span; the '(by soil dryness and disturbance)' that reader 2 adds is the inferred link."},
        "geography": {"content": "differs", "explicit_span_states": True,
                      "adopted": {"value": "old-growth subtropical forest in southern China", "tag": "explicit", "support_from": "r1"},
                      "note": "As LIT-000381-C1. " + _DHS_ALT},
    },
    "LIT-000381-C3": {
        "concept": {"content": "same", "note": "Increasing drought tolerance; soil dryness vs disturbance."},
        "relation_or_direction": {"content": "same", "note": "Both keep 'likely due to soil dryness but not disturbance'."},
        "geography": {"content": "differs", "explicit_span_states": True,
                      "adopted": {"value": "monsoon evergreen broad-leaved forest in DHS plot", "tag": "explicit", "support_from": "r1"},
                      "note": "Reader 1's span states 'the monsoon evergreen broad-leaved forest in DHS plot' but not the expansion 'Dinghushan' its value adds. " + _DHS_ALT},
        "claim_type": {"content": "differs", "adopted": "unresolved_tie",
                       "note": "Reader 1: mechanism; reader 2: finding. The span is the authors' result-based causal attribution ('likely due to'); both labels fit the rubric and neither is more conservative. Breaking the tie would need a reading beyond the recorded claims."},
    },
    "LIT-000381-C4": {
        "concept": {"content": "same", "note": "Drivers in concept (reader 1) or relation (reader 2)."},
        "relation_or_direction": {"content": "same", "note": "Both: led to decrease."},
        "geography": {"content": "same", "explicit_span_states": True,
                      "adopted": {"value": "the study site: Dinghushan natural reserve, Guangdong Province, southern China", "tag": "explicit", "support_from": "r1"},
                      "note": "Same place; reader 1 explicit, reader 2 inferred, both citing the same methods sentence. That span states the full value, so explicit stands."},
    },
    # --- LIT-001141 (Bangalore) ---------------------------------------------------
    "LIT-001141-C1": {
        "concept": {"content": "same", "note": "Reader 2 adds the paper's definition of a UHI event (highest 8-day April window) from methods; same concept."},
        "relation_or_direction": {"content": "same", "note": "0.34 vs 0.14 °C per year, urban vs non-urban."},
        "geography": {"content": "same", "note": "Bangalore urban settlement areas (vs non-urban), both explicit in the evidence span."},
        "temporal_frame": {"content": "same", "note": "Punctuation only."},
    },
    "LIT-001141-C2": {
        "concept": {"content": "same", "note": "LST vs its abbreviation."},
        "relation_or_direction": {"content": "same", "note": "0.247 vs 0.056 °C per year."},
        "geography": {"content": "same", "explicit_span_states": True,
                      "adopted": {"value": "Bangalore city", "tag": "explicit", "support_from": "r1"},
                      "note": "Both cite the same introduction span; it states 'Bangalore city' but not 'India', which both values add."},
        "temporal_frame": {"content": "same", "explicit_span_states": True,
                           "adopted": {"value": "April months, 2001 to 2021", "tag": "explicit", "support_from": "r1"},
                           "note": "Reader 1's span 'during the April months from 2001 to 2021' states it; reader 2 cites the containing sentence as inferred."},
    },
    "LIT-001141-C3": {
        "concept": {"content": "same", "note": "UHI temperature events / their intensity."},
        "relation_or_direction": {"content": "same", "note": "Increased by 3.25 °C."},
        "geography": {"content": "same", "explicit_span_states": True,
                      "adopted": {"value": "Bangalore city", "tag": "explicit", "support_from": "r1"},
                      "note": "As LIT-001141-C2."},
        "temporal_frame": {"content": "same", "note": "Word order only."},
    },
    # --- LIT-001521 (wildfire smoke) ---------------------------------------------
    "LIT-001521-C1": {
        "concept": {"content": "same", "note": "Reader 1 names the exposure, reader 2 the measured response, with the exposure in experimental_condition; same proposition, different facet."},
        "relation_or_direction": {"content": "same", "note": "Robust changes; 2,862 DEGs (51.2% increased). Both readers note the paper's inconsistent up/down split."},
        "temporal_frame": _SMOKE_TEMPORAL,
        "experimental_condition": _SMOKE_EXP,
    },
    "LIT-001521-C2": {
        "concept": {"content": "same", "note": "Enriched pathways of the DEGs."},
        "relation_or_direction": {"content": "same", "note": "Same four pathway groups (BBB = blood-brain barrier)."},
        "temporal_frame": _SMOKE_TEMPORAL,
        "experimental_condition": _SMOKE_EXP,
    },
    "LIT-001521-C3": {
        "relation_or_direction": {"content": "same", "note": "No significant alteration ('did not appear')."},
        "temporal_frame": _SMOKE_TEMPORAL,
        "experimental_condition": _SMOKE_EXP,
    },
    "LIT-001521-C4": {
        "concept": {"content": "same", "note": "Air pollution in concept (reader 1) or relation (reader 2)."},
        "relation_or_direction": {"content": "same", "note": "Same wording save 'ambient'."},
        "temporal_frame": {"content": "differs", "note": "Reader 1 'present (now)' explicit; reader 2 unknown."},
    },
    # --- LIT-001711 (Fortescue Marsh) --------------------------------------------
    "LIT-001711-C1": {
        "concept": {"content": "same", "note": "Drivers in concept (reader 1) or relation (reader 2)."},
        "relation_or_direction": {"content": "same", "note": "'determine' / 'determined by'."},
        "geography": _FM_GEO,
        "temporal_frame": {"content": "same", "explicit_span_states": True,
                           "adopted": {"value": "1988 to 2012", "tag": "explicit", "support_from": "r1"},
                           "note": "Both cite the span 'from 1988 to 2012'; reader 1 explicit, reader 2 inferred. The span states the years; 'calibration' and 'satellite observations' in the values are not in it."},
    },
    "LIT-001711-C2": {
        "concept": {"content": "same", "note": "Inundation (flood area)."},
        "relation_or_direction": {"content": "same", "note": "Reader 2 moves the year 2000 into temporal_frame."},
        "geography": _FM_GEO,
        "temporal_frame": {"content": "same", "note": "Both 'last century'; reader 1 adds the reconstruction start (1912, from its support span), reader 2 the year 2000 (from the evidence)."},
    },
    "LIT-001711-C3": {
        "geography": _FM_GEO,
        "temporal_frame": {"content": "same", "note": "Wording only."},
    },
    "LIT-001711-C4": {
        "concept": {"content": "differs",
                    "adopted": {"value": "wetland persistence; frequency and intensity of extreme rainfall events", "tag": "explicit", "support_from": "r1_evidence"},
                    "note": "Reader 2's evidence runs on through 'which in turn will likely impact on the structure and functioning of this highly specialized ecosystem' and its concept adds that; reader 1 stops before it. Adopted: the narrower content both spans contain."},
        "relation_or_direction": {"content": "differs",
                                  "adopted": {"value": "will become more persistent (hedged: 'suggest')", "tag": "explicit", "support_from": "r1_evidence"},
                                  "note": "As for concept; the ecosystem-impact clause is reader-2-only content."},
        "geography": _FM_GEO,
        "temporal_frame": {"content": "differs", "note": "Reader 1 unknown; reader 2 'over the last 20 years (basis); future unspecified'."},
    },
}
