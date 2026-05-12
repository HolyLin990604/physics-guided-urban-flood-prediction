# Phase 17 Reliability-Aware Warning Framework Synthesis

## 1. Purpose of the synthesis

This document synthesizes Phases 12 through 16 into a coherent reliability-aware flood-warning framework narrative for the current Phase 10 recommended model.

Phase 17 is not a new experiment phase. It does not introduce retraining, architecture changes, Phase 10 loss changes, `boundary_weight` tuning, `boundary_band_pixels` tuning, new analysis outputs, or a new sweep. The current recommended Phase 10 setting remains:

- `boundary_band_pixels = 1`
- `boundary_weight = 2.0`

The purpose is to connect the reliability diagnosis, failure-case visualization, confidence-proxy diagnostics, deterministic screening labels, and warning-rule guidance into a manuscript- and README-ready interpretation.

## 2. Why reliability-aware analysis is needed

The Phase 10 recommended model provides a rapid surrogate for spatiotemporal flood-depth prediction, but the Phase 12 to Phase 16 evidence shows that its reliability is not uniform across all pixels, depth ranges, and scenario conditions.

A single aggregate performance score is therefore insufficient for warning-oriented use. A warning workflow needs to know not only what the model predicts, but also where the prediction is more reliable, where interpretation requires caution, and where the surrogate should not be used alone for warning decisions.

The reliability-aware framework addresses this need by separating three functions:

1. rapid flood-process prediction from the Phase 10 recommended model;
2. deterministic reliability screening and spatial risk mapping from Phase 15;
3. warning-rule and applicability-boundary guidance from Phase 16.

## 3. Phase 12-16 logic chain

The full logic chain is:

1. Phase 12 diagnoses where the current Phase 10 recommended model is reliable or less reliable.
2. Phase 13 visually explains the highest-ranked failures and shows that they are systematic rather than random.
3. Phase 14 evaluates output-space confidence and disagreement proxies, identifying confidence margin as useful for wet/dry classification risk while limiting the role of cross-seed disagreement.
4. Phase 15 converts this evidence into deterministic scenario-level and pixel-level reliability screening.
5. Phase 16 converts the deterministic screening labels into warning-rule guidance and applicability-boundary interpretation.

This progression moves the project from rapid prediction alone to rapid prediction with reliability screening, spatial risk mapping, and deterministic warning-rule guidance.

## 4. Phase-by-phase contribution

### Phase 12: Reliability and applicability diagnosis

Phase 12 evaluated the Phase 10 recommended model using saved test-facing forecast maps from the three confirmed seeds. The analysis used 57 saved `forecast_maps.npz` batches and did not retrain or modify the model.

The main finding is that the model is broadly useful for rapid spatiotemporal flood-process approximation under the tested scenario set, but reliability is lower in specific conditions:

- exact wet/dry boundary cells, where regression and wet/dry classification errors are highest;
- shallow threshold-adjacent cells, where small depth errors can flip the wet/dry state;
- moderate-to-deep target depths, where underprediction becomes stronger;
- high-intensity `location2` scenarios, especially `r300y_p0.6_d3h`, `r300y_p0.8_d3h`, and related high-return-period cases;
- local peak-depth extremes, where maximum depths can be substantially underestimated.

Phase 12 therefore defines the first applicability boundary for the current model: useful for rapid distributed approximation, but not equally reliable for all cells, depths, and scenario types.

### Phase 13: Representative failure-case visual summary

Phase 13 converted the top Phase 12 failure cases into representative worst-timestep visual summaries.

The key result is that the most severe failures are systematic, not random. The top-ranked failures collapse into high-intensity `location2` target scenarios repeated across seeds, especially:

- `location2 / r300y_p0.6_d3h / start_idx = 0`;
- `location2 / r300y_p0.8_d3h / start_idx = 0`.

The visual failure modes are consistent:

- systematic underprediction;
- reduced predicted wet fraction;
- local peak-depth underestimation;
- false-dry dominated wet/dry mismatch;
- boundary-transition failure around wet/dry margins.

This strengthens the Phase 12 conclusion that the main reliability limits are structured physical and scenario-dependent failure modes rather than isolated noise.

### Phase 14: Confidence proxy diagnostics

Phase 14 evaluated whether deterministic output-space proxies can support reliability interpretation.

The strongest supported result is that confidence margin,

`confidence_margin = abs(prediction - wet_threshold)`,

with `wet_threshold = 0.05`, is useful as a wet/dry classification risk proxy. Predictions close to the wet/dry threshold have much higher wet/dry classification error and false-dry risk.

However, confidence margin is not a calibrated probabilistic uncertainty estimate and is not a complete depth-error uncertainty measure. A cell can be confidently wet or dry while still having substantial depth-magnitude error, especially in moderate-to-deep or local peak-depth regions.

Phase 14 also showed that cross-seed disagreement is only an auxiliary signal. Its weak global correlation with scenario RMSE means it should not be used as a strong standalone scenario-error predictor. This limitation is important because Phase 13 showed that multiple seeds can fail similarly on the same high-intensity `location2` cases.

### Phase 15: Reliability screening and risk mapping

Phase 15 converted the Phase 12, Phase 13, and Phase 14 evidence into automatic deterministic reliability screening.

The core Phase 15 results are:

- 57 Phase 10 map files loaded;
- 114 scenario-level risk records generated;
- 16,384 pixel-level risk records generated;
- scenario labels: 76 `reliable`, 25 `caution`, and 13 `high-risk`;
- Phase 13-like `location2+r300y` cases: 24/24 flagged as `caution` or `high-risk`.

The screening components reflect the earlier evidence: low confidence-margin risk, false-dry risk, wet-fraction contraction, peak-depth underprediction, mean underprediction bias, boundary-zone false-dry risk, high-intensity `location2` metadata risk, and auxiliary cross-seed disagreement.

The important interpretation is that Phase 15 labels are deterministic screening labels. They are not calibrated probabilities, Bayesian uncertainty estimates, or formal confidence intervals.

### Phase 16: Reliability-aware warning rules and applicability boundary

Phase 16 translated the Phase 15 deterministic screening labels into application-oriented warning guidance and applicability-boundary guidance.

The core Phase 16 results are:

- scenario warnings: `reliable=76`, `caution=25`, `high-risk=13`;
- pixel warnings: `reliable=5714`, `caution=8805`, `high-risk=1865`;
- high-risk warning cases: 13, matching the Phase 15 high-risk cases.

The warning interpretation is:

- `reliable`: use as a rapid prediction reference;
- `caution`: use with targeted review;
- `high-risk`: do not use alone for warning decisions.

Phase 16 therefore turns deterministic screening into warning-rule guidance while preserving the Phase 15 risk structure.

## 5. Current reliability-aware framework

The current framework has three layers.

The first layer is the Phase 10 recommended surrogate prediction layer. It provides rapid flood-depth forecasts using the confirmed margin-aware setting `boundary_band_pixels = 1` and `boundary_weight = 2.0`.

The second layer is the Phase 15 reliability-screening layer. It attaches deterministic scenario and pixel labels to the prediction output using evidence from reliability diagnostics, representative failure cases, and confidence proxies.

The third layer is the Phase 16 warning-interpretation layer. It converts those deterministic labels into application guidance: normal rapid-reference use, targeted review, or high-risk non-standalone use.

Together, these layers form a reliability-aware flood-warning framework rather than only a flood-depth surrogate.

## 6. Applicability boundary of the current model

The current model is most applicable as a rapid reference for tested scenarios that do not show strong reliability-risk components. It is most defensible for general spatiotemporal flood-pattern approximation and for regions away from the exact wet/dry transition boundary.

The main applicability-boundary caution zones are:

- exact wet/dry boundary cells;
- shallow cells near the wet/dry threshold;
- moderate-to-deep inundation depths where magnitude underprediction increases;
- high-intensity `location2` scenarios, especially `location2+r300y` cases;
- local peak-depth extremes;
- repeated false-dry pixel regions;
- cases with strong predicted wet-fraction contraction.

These boundaries do not invalidate the surrogate. They define where the model output should be interpreted with additional review and where high-stakes warning decisions require confirmation from hydrodynamic modeling, expert review, or other operational evidence.

## 7. Warning interpretation layer

The warning interpretation layer is deterministic and application-oriented.

`Reliable` means the prediction lies within the stronger current applicability region and can be used as a rapid flood-depth reference with normal review.

`Caution` means the prediction remains useful, but the user should review sensitive areas such as wet/dry boundaries, shallow threshold-adjacent zones, peak-depth regions, and pixel-level risk maps.

`High-risk` means the prediction should not be used alone for warning decisions. These cases require conservative interpretation and should trigger hydrodynamic-model confirmation, expert review, or other supporting evidence before high-stakes decisions.

The warning labels should be read as guidance for interpretation, not as event probabilities.

## 8. Research contribution for a paper or README narrative

The Phase 12 to Phase 16 sequence supports a clear research contribution:

This project does not stop at improving aggregate surrogate-model accuracy. It adds a reliability-aware interpretation framework that diagnoses where a physics-guided urban flood surrogate is reliable, visualizes systematic failure modes, tests deterministic confidence proxies, converts the evidence into scenario and pixel screening labels, and translates those labels into warning-rule guidance.

The contribution is therefore a rapid prediction framework with explicit reliability boundaries:

- Phase 12 identifies the reliability limits;
- Phase 13 shows that the dominant failures are structured and scenario-dependent;
- Phase 14 provides proxy evidence for wet/dry classification risk while explicitly avoiding calibrated uncertainty claims;
- Phase 15 operationalizes the evidence as deterministic risk screening and spatial risk maps;
- Phase 16 translates screening outputs into warning guidance and applicability-boundary interpretation.

This narrative is suitable for manuscript framing because it distinguishes model prediction performance from reliability-aware use. It also makes the current limitations explicit rather than presenting the surrogate as uniformly reliable.

## 9. Limitations and non-claims

The Phase 12 to Phase 16 reliability and warning stages do not claim calibrated probabilistic uncertainty.

The deterministic labels are not:

- predictive probabilities;
- Bayesian posterior uncertainty;
- calibrated confidence intervals;
- guaranteed error bounds;
- evidence of universal generalization.

The current model should not be described as universally generalizable beyond the tested data and scenario set. It should also not be described as replacing hydrodynamic modeling in high-stakes decisions.

The correct claim is narrower and stronger: the current Phase 10 recommended surrogate can support rapid flood-process approximation under the tested setting, and Phases 12 to 16 provide deterministic reliability screening, applicability boundaries, and warning-rule guidance for interpreting its outputs.

No retraining, architecture change, Phase 10 loss change, `boundary_weight` tuning, `boundary_band_pixels` tuning, or new sweep was performed in Phases 12 through 16.

## 10. Recommended next step

The next step should build on the reliability-aware framework rather than reopening Phase 10 tuning.

Recommended follow-up work is to prepare the Phase 12 to Phase 16 narrative for manuscript and README use, while keeping the current Phase 10 setting fixed at `boundary_band_pixels = 1` and `boundary_weight = 2.0`.

Calibrated uncertainty should only be introduced through a separate calibration design with appropriate calibration data and evaluation protocol. Until then, the Phase 15 and Phase 16 outputs should remain deterministic screening labels and warning-rule guidance.
