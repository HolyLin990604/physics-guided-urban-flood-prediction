# Phase 23 Reliability-Aware Warning Case Study

This Phase 23 prototype reuses existing Phase 15 reliability-screening outputs and Phase 16 warning-rule outputs. It does not retrain models, tune Phase 10 settings, or generate new predictions.

## Selected Cases

### Reliable Case

- Scenario identity: location1|r100y_p0.5_d3h|6
- Warning level: reliable
- Dominant risk components: cross seed disagreement=0.0559; low margin=0.0505
- Model reliability interpretation: Phase 15/16 screening labels this case reliable with risk score 0.106; the available missed-inundation and boundary indicators are comparatively low.
- Suggested warning action: use as rapid prediction reference
- Applicability boundary note: Prediction is within the stronger applicability range of the current surrogate model.
- Selection basis: Selected as the lowest-risk reliable-labeled case using risk score, false-dry, boundary, RMSE, and stable identity tie-breaks.

### Caution Case

- Scenario identity: location2|r300y_p0.6_d3h|6
- Warning level: caution
- Dominant risk components: high intensity location2=2.5; false dry=0.65; boundary=0.316
- Model reliability interpretation: Phase 15/16 screening labels this case caution with risk score 3.85; the prediction may be useful as a rapid reference after targeted review.
- Suggested warning action: use with targeted review
- Applicability boundary note: Inspect wet/dry boundaries, shallow transition areas, local peak-depth areas, and pixel-level risk maps.
- Selection basis: Selected as a representative caution-labeled case closest to the caution risk midpoint with stable tie-breaks.

### High-Risk Case

- Scenario identity: location2|r300y_p0.8_d3h|0
- Warning level: high-risk
- Dominant risk components: high intensity location2=2.5; false dry=2; peak underprediction=1.5
- Model reliability interpretation: Phase 15/16 screening labels this case high-risk with risk score 8.74, false-dry rate 0.585, wet-fraction contraction 0.549, and peak underprediction 1.53 m.
- Suggested warning action: do not use alone for warning decisions
- Applicability boundary note: Trigger conservative interpretation, hydrodynamic-model confirmation, or expert review before warning decisions.
- Selection basis: Selected as a high-risk case, prioritizing Phase-13-like location2+r300y evidence and then stronger risk evidence.

## Figures

- analysis\phase23_warning_case_study\figures\case_warning_level_overview.png
- analysis\phase23_warning_case_study\figures\case_risk_component_comparison.png
- analysis\phase23_warning_case_study\figures\reliable_case_maps.png
- analysis\phase23_warning_case_study\figures\caution_case_maps.png
- analysis\phase23_warning_case_study\figures\high_risk_case_maps.png

## Map-Level Visualization Status

Case map figures were generated from existing forecast map `.npz` files referenced by Phase 15/16 rows. The pixel-warning panel, when present, uses the existing Phase 16 pixel warning summary grid.
- Generated analysis\phase23_warning_case_study\figures\reliable_case_maps.png from runs\phase10_margin_aware_boundary_band_seed123_40e\evaluation_test\test_batch_0000\forecast_maps.npz.
- Generated analysis\phase23_warning_case_study\figures\caution_case_maps.png from runs\phase10_margin_aware_boundary_band_seed123_40e\evaluation_test\test_batch_0009\forecast_maps.npz.
- Generated analysis\phase23_warning_case_study\figures\high_risk_case_maps.png from runs\phase10_margin_aware_boundary_band_seed123_40e\evaluation_test\test_batch_0011\forecast_maps.npz.

## Missing Inputs And Limitations

- All expected Phase 15 and Phase 16 input files were found.
- Warning labels are deterministic screening labels, not calibrated probabilities.
- No model retraining, architecture changes, Phase 10 parameter tuning, or new predictions were performed.
