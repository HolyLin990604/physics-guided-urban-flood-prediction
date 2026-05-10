# Experiment Index

## Active Project References

- `M3 f025`: overall best-balanced mainline reference
- Phase 3.3 `af025`: strongest static structured refinement
- Phase 7/8 `adapt010`: active adaptive candidate before margin-aware refinement
- Phase 10 boundary-band refinement: current recommended margin-aware setting, with `boundary_band_pixels = 1` and `boundary_weight = 2.0`
- Phase 12 reliability/applicability diagnosis: first-pass reliability boundary analysis of the current Phase 10 recommended model
- Phase 13 failure-case visual summary: representative visual explanation of the highest-ranked Phase 12 failures
- Phase 14 confidence proxy diagnosis: first-pass output-space confidence and cross-seed disagreement proxy analysis
- Phase 15 reliability screening and risk mapping: first implementation of deterministic scenario screening and pixel-level risk mapping
- Phase 16 reliability-aware warning rules and applicability boundary: first implementation of deterministic warning-rule guidance based on Phase 15 screening labels

## Phase 6

- Document: `docs/phase6_pilot_a_results.md`
- Status: closed as a negative/neutral result
- Takeaway: the adaptive scalar mechanism was stable, but `adapt025` did not remain better than the static Phase 3.3 `af025` control after full training

## Phase 7

- Document: `docs/phase7_adapt010_results.md`
- Status: active adaptive candidate established
- Takeaway: the conservative `adapt010` follow-up improved the decisive difficult-case `seed202 / 40e` result and also passed the favorable-case `seed42 / 5e` guardrail check

## Phase 8 Batch 1

- Document: `docs/phase8_batch1_results.md`
- Status: early validation support established
- Takeaway: `adapt010` remained favorable across a narrow Phase 8 Batch 1 check, with decisive difficult-case support, supportive repeatability evidence, and a strong full favorable-case guardrail pass

## Phase 8 Batch 2

- Documents: `docs/phase8_batch2_plan.md`, `docs/phase8_tradeoff_positioning.md`
- Status: trade-off positioning complete
- Takeaway: `adapt010` showed consistent RMSE/MAE/loss gains across the three required full `40e` comparisons, with mixed wet/dry IoU because of `seed123` and no favorable-case guardrail failure. No new architecture search or broader sweep was justified by Batch 2 evidence

## Phase 9

- Documents: `docs/phase9_interpretability_diagnosis_plan.md`, `docs/phase9_interpretability_findings.md`
- Status: interpretability and trade-off diagnosis complete
- Takeaway: the `seed123` wet/dry IoU give-back was best explained as a mixed, margin-region, step-dependent wet/dry trade-off. The diagnosis did not indicate adaptive multiplier saturation or seed-specific mechanism instability

## Phase 10

- Document: `docs/phase10_margin_aware_findings.md`
- Status: first margin-aware intervention complete
- Takeaway: boundary-band weighted wet/dry consistency refinement passed test-facing confirmation across `seed123`, `seed42`, and `seed202`
- Recommended setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`
- Rollback setting: `boundary_weight = 1.5` only
- Decision: no broader boundary-weight sweep is justified at this point

## Phase 12

- Plan: `docs/phase12_reliability_applicability_plan.md`
- Script: `scripts/analyze_phase12_reliability.py`
- Visualization script: `scripts/plot_phase12_reliability.py`
- Findings: `docs/phase12_reliability_applicability_findings.md`
- Outputs: `analysis/phase12_reliability/`
- Status: first-pass reliability/applicability diagnosis complete
- Takeaway: the Phase 10 recommended model is useful for rapid spatiotemporal flood-process approximation, but reliability is lower at exact wet/dry boundary cells, shallow threshold-adjacent areas, moderate-to-deep depths, high-intensity `location2` cases, and local peak-depth extremes
- Decision: no model retraining, architecture change, Phase 10 loss change, or boundary-weight sweep was performed

## Phase 13

- Plan: `docs/phase13_failure_case_visual_summary_plan.md`
- Script: `scripts/visualize_phase13_failure_cases.py`
- Findings: `docs/phase13_failure_case_visual_summary_findings.md`
- Outputs: `analysis/phase13_failure_cases/`
- Status: first-pass representative failure-case visual summary complete
- Takeaway: the top-ranked failures are not random. They collapse into two high-intensity `location2` target scenarios repeated across seeds: `r300y_p0.6_d3h` at worst step 1 and `r300y_p0.8_d3h` at worst step 4
- Visual failure mode: systematic underprediction, reduced predicted wet fraction, local peak-depth underprediction, and false-dry dominated wet/dry mismatch
- Decision: formal Phase 13 outputs use worst-timestep visualizations rather than final-timestep visualizations

## Phase 14

- Plan: `docs/phase14_uncertainty_confidence_diagnostics_plan.md`
- Script: `scripts/analyze_phase14_confidence.py`
- Findings: `docs/phase14_uncertainty_confidence_diagnostics_findings.md`
- Outputs: `analysis/phase14_confidence/`
- Status: first-pass proxy-based confidence diagnosis complete
- Takeaway: confidence margin is useful for wet/dry classification risk because low-margin bins show much higher wet/dry error and false-dry rate
- Disagreement result: cross-seed disagreement has weak global correlation with scenario RMSE and should be treated as an auxiliary disagreement proxy rather than a strong standalone scenario-error predictor
- Decision: Phase 14 should be interpreted as confidence/risk/disagreement proxy diagnostics, not calibrated probabilistic uncertainty

## Phase 15

- Plan: `docs/phase15_reliability_screening_risk_mapping_plan.md`
- Script: `scripts/screen_phase15_reliability.py`
- Findings: `docs/phase15_reliability_screening_risk_mapping_findings.md`
- Outputs: `analysis/phase15_reliability_screening/`
- Summary output: `analysis/phase15_reliability_screening/summary.json`
- Scenario scores: `analysis/phase15_reliability_screening/scenario_risk_scores.csv`
- Pixel summary: `analysis/phase15_reliability_screening/pixel_risk_summary.csv`
- High-risk cases: `analysis/phase15_reliability_screening/high_risk_cases.csv`
- Figures:
  - `analysis/phase15_reliability_screening/figures/scenario_risk_score_distribution.png`
  - `analysis/phase15_reliability_screening/figures/scenario_risk_category_counts.png`
  - `analysis/phase15_reliability_screening/figures/risk_component_heatmap.png`
  - `analysis/phase15_reliability_screening/figures/repeated_false_dry_pixel_risk.png`
  - `analysis/phase15_reliability_screening/figures/pixel_risk_map_example.png`
- Status: first implementation of reliability screening and risk mapping complete
- Core result: 57 Phase 10 map files were loaded, producing 114 scenario-level risk records and 16,384 pixel-level risk records
- Category counts: 76 `reliable`, 25 `caution`, and 13 `high-risk`
- Validation check: all 24 known Phase 13-like `location2` + `r300y` cases were flagged as `caution` or `high-risk`
- Decision: Phase 15 converts Phase 12/13/14 diagnostic evidence into deterministic screening labels and spatial risk maps; it does not provide calibrated probabilities or Bayesian uncertainty
- Model status: no retraining, architecture change, Phase 10 loss change, `boundary_band_pixels` tuning, `boundary_weight` tuning, or new sweep was performed

## Phase 16

- Plan: `docs/phase16_reliability_warning_applicability_plan.md`
- Script: `scripts/build_phase16_warning_rules.py`
- Findings: `docs/phase16_reliability_warning_applicability_findings.md`
- Outputs: `analysis/phase16_warning_rules/`
- Summary output: `analysis/phase16_warning_rules/summary.json`
- Warning rules: `analysis/phase16_warning_rules/warning_rules.json`
- Scenario warning summary: `analysis/phase16_warning_rules/scenario_warning_summary.csv`
- Applicability boundary table: `analysis/phase16_warning_rules/applicability_boundary_table.csv`
- High-risk warning cases: `analysis/phase16_warning_rules/high_risk_warning_cases.csv`
- Pixel warning summary: `analysis/phase16_warning_rules/pixel_warning_summary.csv`
- Figures:
  - `analysis/phase16_warning_rules/figures/warning_level_counts.png`
  - `analysis/phase16_warning_rules/figures/warning_action_matrix.png`
  - `analysis/phase16_warning_rules/figures/applicability_boundary_summary.png`
  - `analysis/phase16_warning_rules/figures/high_risk_warning_case_distribution.png`
  - `analysis/phase16_warning_rules/figures/pixel_warning_map_example.png`
- Status: first implementation of reliability-aware warning rules and applicability boundary complete
- Core result: Phase 16 converts Phase 15 deterministic reliability-screening labels into application-oriented warning guidance
- Scenario warning counts: 76 `reliable`, 25 `caution`, and 13 `high-risk`
- Pixel warning counts: 5,714 `reliable`, 8,805 `caution`, and 1,865 `high-risk`
- Validation check: the 13 high-risk warning cases match the Phase 15 high-risk cases
- Decision: Phase 16 warning labels are deterministic operational interpretation labels, not calibrated probabilities, Bayesian uncertainty, or formal confidence intervals
- Model status: no retraining, architecture change, Phase 10 loss change, `boundary_band_pixels` tuning, `boundary_weight` tuning, or new sweep was performed

## Interpretation Order

For current repository interpretation, read the experiment trail in this order:

1. `docs/phase6_pilot_a_results.md`
2. `docs/phase7_adapt010_results.md`
3. `docs/phase8_batch1_results.md`
4. `docs/phase8_tradeoff_positioning.md`
5. `docs/phase9_interpretability_findings.md`
6. `docs/phase10_margin_aware_findings.md`
7. `docs/phase12_reliability_applicability_findings.md`
8. `docs/phase13_failure_case_visual_summary_findings.md`
9. `docs/phase14_uncertainty_confidence_diagnostics_findings.md`
10. `docs/phase15_reliability_screening_risk_mapping_findings.md`
11. `docs/phase16_reliability_warning_applicability_findings.md`
12. `docs/project_status.md`

## Next Stage

The next stage should build on the Phase 12 to Phase 16 reliability/applicability, screening, and warning-rule evidence rather than reopening Phase 10 tuning.

Recommended next work:

- consider calibrated uncertainty only if calibration data and evaluation design are added
- keep the current Phase 10 setting fixed unless new evidence justifies changing it
- avoid broader boundary-weight sweeps
- maintain the Phase 15 screening layer and Phase 16 warning-rule layer as deterministic operational support unless a new calibration design is added
