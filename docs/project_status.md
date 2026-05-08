# Project Status

## Current Conclusion

The repository should currently be interpreted as follows:

- `M3 f025` remains the overall best-balanced mainline reference.
- Phase 3.3 `af025` remains the strongest static structured refinement.
- Phase 6 `adapt025` is closed as a negative/neutral adaptive result.
- Phase 7/8 `adapt010` remains the active adaptive candidate before margin-aware refinement.
- Phase 9 completed the interpretability and trade-off diagnosis for `adapt010`.
- Phase 10 completed the first margin-aware intervention and established the current recommended refinement setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`.
- Phase 12 completed the first-pass reliability/applicability diagnosis of the Phase 10 recommended model.
- Phase 13 completed the first-pass representative failure-case visual summary.
- Phase 14 completed the first-pass proxy-based uncertainty/confidence diagnosis.
- Phase 15 completed the first implementation of reliability screening and risk mapping.

The current Phase 10 conclusion is that boundary-band weighted wet/dry consistency refinement has passed test-facing confirmation on the three key project seeds: `seed123`, `seed42`, and `seed202`.

The current recommended model setting remains the Phase 10 setting:

- `boundary_band_pixels = 1`
- `boundary_weight = 2.0`

The current Phase 12 conclusion is that the Phase 10 recommended model is broadly useful for rapid spatiotemporal flood-process approximation under the tested scenario set, but its reliability is not uniform across all pixels, depth ranges, and scenarios. The main caution zones are exact wet/dry boundary cells, shallow threshold-adjacent cells, moderate-to-deep inundation depths, high-intensity `location2` scenarios, and local peak-depth extremes.

The current Phase 13 conclusion is that the highest-ranked failures are not random scattered cases. They collapse into two high-intensity `location2` target scenarios repeated across seeds: `location2 / r300y_p0.6_d3h / start_idx = 0` at worst step 1, and `location2 / r300y_p0.8_d3h / start_idx = 0` at worst step 4. The visual summaries show systematic underprediction, reduced predicted wet fraction, local peak-depth underprediction, and false-dry dominated wet/dry mismatch.

The current Phase 14 conclusion is that output-space confidence proxies are useful but limited. Confidence margin is useful for wet/dry classification risk because low-margin bins show much higher wet/dry error and false-dry rate. Cross-seed disagreement has only weak global correlation with scenario RMSE, so it should be treated as an auxiliary disagreement proxy rather than a strong standalone scenario-error predictor. Phase 14 is not calibrated probabilistic uncertainty.

The current Phase 15 conclusion is that the Phase 12/13/14 diagnostic evidence has been converted into a functional deterministic screening layer. The first implementation loaded 57 Phase 10 map files, generated 114 scenario-level risk records and 16,384 pixel-level risk records, and assigned 76 scenario records to `reliable`, 25 to `caution`, and 13 to `high-risk`. As a validation check, all 24 known Phase 13-like `location2` + `r300y` cases were flagged as `caution` or `high-risk`.

Phase 15 screening labels are deterministic risk-screening labels. They are not calibrated probabilities, Bayesian uncertainty estimates, or a substitute for a formal calibration design.

No retraining, architecture change, Phase 10 loss change, `boundary_band_pixels` tuning, `boundary_weight` tuning, or additional Phase 10 boundary-weight sweep was performed.

## Meaning Of Each Reference

### Mainline reference

`M3 f025` remains the default project-level mainline reference because it provides the strongest overall balance across robustness, stability, and project-level confidence before the later adaptive and margin-aware refinements.

### Strongest static structured refinement

Phase 3.3 `af025` remains the strongest static structured refinement discovered so far. It is still the correct static control when evaluating whether adaptive follow-ups and margin-aware refinements add value.

### Closed adaptive result

Phase 6 `adapt025` established that the adaptive scalar mechanism is technically stable and trainable, but it did not remain superior to the static Phase 3.3 `af025` control after full training. It should therefore be treated as a documented negative/neutral result rather than an active candidate.

### Active adaptive candidate before margin-aware refinement

Phase 7/8 `adapt010` remains the active adaptive candidate before margin-aware refinement. It improved RMSE, MAE, and loss across the required full `40e` comparisons, but Phase 8 Batch 2 also showed mixed wet/dry IoU behavior, mainly because of the `seed123` trade-off.

### Interpretability diagnosis

Phase 9 diagnosed the `adapt010` trade-off rather than opening a new architecture search. The main finding was that the `seed123` IoU give-back was best interpreted as a mixed, margin-region, step-dependent wet/dry trade-off rather than adaptive multiplier saturation or seed-specific mechanism instability.

### Current recommended margin-aware refinement

Phase 10 introduced a minimal, diagnosis-driven intervention: boundary-band weighted wet/dry consistency refinement.

The recommended Phase 10 setting is:

- `boundary_band_pixels = 1`
- `boundary_weight = 2.0`

This setting passed test-facing confirmation across the three key seeds:

- `seed123`: original mixed-IoU problem seed
- `seed42`: favorable-case guardrail seed
- `seed202`: difficult-case confirmation seed

`boundary_weight = 1.5` remains only a conservative rollback setting and is no longer the preferred setting.

### Reliability and applicability diagnosis

Phase 12 diagnosed the reliability and applicability boundaries of the Phase 10 recommended model using saved test-facing forecast maps.

Generated diagnostics include:

- timestep-wise error
- depth-bin error
- wet/dry boundary-distance error
- scenario-level reliability
- failure-case ranking
- diagnostic figures

The first-pass Phase 12 findings indicate:

- the model has a mild overall underprediction bias
- exact wet/dry boundary cells remain the main reliability bottleneck
- moderate-to-deep target depths show stronger underprediction
- high-intensity `location2` cases dominate the highest-ranked failures
- no retraining, architecture change, Phase 10 loss change, or boundary-weight sweep was performed

### Representative failure-case visual summary

Phase 13 converted the highest-ranked Phase 12 failure cases into representative worst-timestep visual summaries.

Generated Phase 13 outputs include:

- `docs/phase13_failure_case_visual_summary_plan.md`
- `scripts/visualize_phase13_failure_cases.py`
- `analysis/phase13_failure_cases/selected_failure_cases.csv`
- `analysis/phase13_failure_cases/summary.json`
- `analysis/phase13_failure_cases/figures/`
- `docs/phase13_failure_case_visual_summary_findings.md`

The first-pass Phase 13 findings indicate:

- top failures collapse into two high-intensity `location2` target scenarios repeated across seeds
- worst-timestep visualization is more explanatory than final-timestep visualization
- the main visual failure mode is systematic underprediction with reduced wet extent
- local peak depths are strongly underestimated
- wet/dry mismatch is false-dry dominated

### Proxy-based uncertainty and confidence diagnosis

Phase 14 diagnosed whether output-space confidence and disagreement proxies can help identify less reliable predictions.

Generated Phase 14 outputs include:

- `docs/phase14_uncertainty_confidence_diagnostics_plan.md`
- `scripts/analyze_phase14_confidence.py`
- `analysis/phase14_confidence/summary.json`
- `analysis/phase14_confidence/confidence_margin_metrics.csv`
- `analysis/phase14_confidence/seed_disagreement_metrics.csv`
- `analysis/phase14_confidence/risk_proxy_metrics.csv`
- `analysis/phase14_confidence/scenario_confidence_metrics.csv`
- `analysis/phase14_confidence/figures/`
- `docs/phase14_uncertainty_confidence_diagnostics_findings.md`

The first-pass Phase 14 findings indicate:

- confidence margin is useful for wet/dry classification risk
- low-margin bins show much higher wet/dry class error and false-dry rate
- confidence margin is not a complete depth-error uncertainty measure
- high-confidence wet/dry state does not guarantee accurate depth magnitude
- cross-seed disagreement has weak global correlation with scenario RMSE
- cross-seed disagreement should be treated as an auxiliary proxy rather than a strong standalone error predictor
- Phase 14 does not provide calibrated probabilistic uncertainty

### Reliability screening and risk mapping

Phase 15 converted the Phase 12/13/14 diagnostic evidence into scenario-level reliability screening and pixel-level spatial risk mapping for the Phase 10 recommended model.

Generated Phase 15 outputs include:

- `docs/phase15_reliability_screening_risk_mapping_plan.md`
- `scripts/screen_phase15_reliability.py`
- `analysis/phase15_reliability_screening/summary.json`
- `analysis/phase15_reliability_screening/scenario_risk_scores.csv`
- `analysis/phase15_reliability_screening/pixel_risk_summary.csv`
- `analysis/phase15_reliability_screening/high_risk_cases.csv`
- `analysis/phase15_reliability_screening/figures/`
- `docs/phase15_reliability_screening_risk_mapping_findings.md`

The first-pass Phase 15 findings indicate:

- 57 Phase 10 map files were loaded
- 114 scenario-level risk records were generated
- 16,384 pixel-level risk records were generated
- scenario screening produced 76 `reliable`, 25 `caution`, and 13 `high-risk` records
- all 24 known Phase 13-like `location2` + `r300y` cases were flagged as `caution` or `high-risk`
- the labels are deterministic screening labels, not calibrated probabilities or Bayesian uncertainty
- no retraining, tuning, architecture change, or new sweep was performed

## Practical Reading Guide

When reading the repository:

- use `M3 f025` as the overall project mainline reference
- use Phase 3.3 `af025` as the strongest static structured refinement reference
- treat Phase 6 `adapt025` as archived evidence that a larger adaptive range was too aggressive
- treat Phase 7/8 `adapt010` as the active adaptive candidate before margin-aware refinement
- read Phase 9 as the interpretability diagnosis explaining the wet/dry trade-off
- read Phase 10 as the successful first margin-aware intervention that establishes the current recommended refinement setting
- read Phase 12 as the first-pass reliability/applicability diagnosis of the current recommended model
- read Phase 13 as the representative visual explanation of the highest-ranked failure cases
- read Phase 14 as a proxy-based confidence and disagreement diagnosis, not as calibrated probabilistic uncertainty
- read Phase 15 as the first implementation of deterministic reliability screening and spatial risk mapping

## Key Documents

- `docs/phase6_pilot_a_results.md`
- `docs/phase7_adapt010_results.md`
- `docs/phase8_batch1_results.md`
- `docs/phase8_tradeoff_positioning.md`
- `docs/phase9_interpretability_findings.md`
- `docs/phase10_margin_aware_findings.md`
- `docs/phase12_reliability_applicability_plan.md`
- `docs/phase12_reliability_applicability_findings.md`
- `docs/phase13_failure_case_visual_summary_plan.md`
- `docs/phase13_failure_case_visual_summary_findings.md`
- `docs/phase14_uncertainty_confidence_diagnostics_plan.md`
- `docs/phase14_uncertainty_confidence_diagnostics_findings.md`
- `docs/phase15_reliability_screening_risk_mapping_plan.md`
- `docs/phase15_reliability_screening_risk_mapping_findings.md`
- `docs/experiment_index.md`
