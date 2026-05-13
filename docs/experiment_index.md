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
- Phase 17 reliability-aware warning framework synthesis: documentation synthesis integrating Phase 12-16 into the current project narrative
- Phase 18 manuscript-oriented reliability-aware warning layer: writing synthesis converting Phase 12-17 into manuscript-ready material
- Phase 19 manuscript structure and paper-ready consolidation: manuscript-structure and submission-consolidation planning based on Phase 12-18
- Phase 20 manuscript draft assembly: first full manuscript draft skeleton assembled from Phase 18-19 materials
- Phase 21 manuscript evidence and figure/table alignment: claim-to-evidence and figure/table planning based on existing outputs and findings
- Phase 22 manuscript full draft expansion: fuller academic manuscript draft expanded from the Phase 20 skeleton using Phase 21 evidence alignment
- Phase 23 reliability-aware warning case study and application prototype: representative warning-oriented interpretation using Phase 15 screening, Phase 16 rules, and existing Phase 10 forecast map arrays

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

## Phase 17

- Synthesis document: `docs/phase17_reliability_warning_framework_synthesis.md`
- Status: reliability-aware warning framework synthesis complete
- Core result: Phase 17 integrates Phase 12 reliability/applicability diagnosis, Phase 13 representative failure-case visualization, Phase 14 confidence/disagreement proxy diagnostics, Phase 15 reliability screening and spatial risk mapping, and Phase 16 warning-rule/applicability-boundary guidance into a coherent reliability-aware warning framework narrative
- Project position: rapid prediction plus reliability diagnosis, failure-mode interpretation, confidence proxy diagnostics, spatial risk mapping, and warning-rule guidance
- Purpose: support manuscript writing, README narrative, and project positioning
- Decision: Phase 17 is a synthesis/documentation phase, not a new experiment phase
- Model status: no retraining, architecture change, Phase 10 loss change, `boundary_band_pixels` tuning, `boundary_weight` tuning, or new sweep was performed
- Current recommended Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`
- Interpretation guardrail: the framework does not claim calibrated uncertainty or universal generalization

## Phase 18

- Plan: `docs/phase18_manuscript_reliability_warning_layer_plan.md`
- Manuscript note: `docs/manuscript_reliability_aware_warning_layer.md`
- Status: manuscript-oriented writing phase complete; first writing deliverable completed
- Core result: Phase 18 converts the completed Phase 12-17 reliability-aware warning framework into manuscript-ready material for "Reliability-Aware Warning Layer for Urban Flood Surrogate Prediction"
- Decision: Phase 18 is a manuscript-oriented synthesis/writing phase, not a new experiment phase
- Model status: no retraining, architecture modification, Phase 10 loss modification, `boundary_band_pixels` tuning, `boundary_weight` tuning, new sweep, or new result generation was performed
- Current recommended Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`

## Phase 19

- Plan: `docs/phase19_manuscript_structure_consolidation_plan.md`
- Manuscript consolidation: `docs/manuscript_structure_and_submission_consolidation.md`
- Status: manuscript-structure and submission-consolidation phase complete
- Core result: Phase 19 converts the completed Phase 12-18 reliability-aware warning framework and manuscript notes into a paper-ready manuscript outline and submission-oriented planning document
- Scope: paper positioning, candidate titles, abstract logic, methods/results/discussion structure, figure/table inventory, contribution statements, limitations, submission positioning, and immediate writing tasks
- Decision: Phase 19 is a manuscript-structure and submission-consolidation phase, not a new experiment phase
- Model status: no retraining, architecture modification, Phase 10 loss modification, `boundary_band_pixels` tuning, `boundary_weight` tuning, new sweep, or new result generation was performed
- Current recommended Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`

## Phase 20

- Plan: `docs/phase20_manuscript_draft_assembly_plan.md`
- Manuscript draft: `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`
- Status: manuscript draft assembly complete
- Core result: Phase 20 assembles the Phase 18 and Phase 19 manuscript-oriented materials into the first full manuscript draft skeleton
- Decision: Phase 20 is a manuscript draft assembly phase, not a new experiment phase
- Model status: no retraining, architecture modification, Phase 10 loss modification, `boundary_band_pixels` tuning, `boundary_weight` tuning, new sweep, or new result generation was performed
- Current recommended Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`

## Phase 21

- Plan: `docs/phase21_manuscript_evidence_figure_alignment_plan.md`
- Evidence alignment: `docs/manuscript_evidence_figure_table_alignment.md`
- Status: manuscript evidence and figure/table alignment complete
- Core result: Phase 21 aligns manuscript claims with existing evidence sources, figures, tables, JSON/CSV outputs, and findings documents before full manuscript expansion
- Decision: Phase 21 is an evidence-alignment and figure/table planning phase, not a new experiment phase
- Model status: no retraining, architecture modification, Phase 10 loss modification, `boundary_band_pixels` tuning, `boundary_weight` tuning, new sweep, new result generation, or new uncertainty claim was performed
- Current recommended Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`

## Phase 22

- Plan: `docs/phase22_manuscript_full_draft_expansion_plan.md`
- Full manuscript draft: `docs/manuscript_full_draft_reliability_aware_urban_flood_warning.md`
- Status: manuscript full draft expansion complete
- Core result: Phase 22 expands the Phase 20 manuscript skeleton into a fuller academic manuscript draft using the Phase 21 evidence-alignment document
- Decision: Phase 22 is a manuscript full-draft expansion phase, not a new experiment phase
- Model status: no retraining, architecture modification, Phase 10 loss modification, `boundary_band_pixels` tuning, `boundary_weight` tuning, new sweep, new result generation, invented references, unsupported claims, or new uncertainty claim was performed
- Current recommended Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`

## Phase 23

- Plan: `docs/phase23_reliability_warning_case_study_plan.md`
- Script: `scripts/build_phase23_warning_case_study.py`
- Findings: `docs/phase23_reliability_warning_case_study_findings.md`
- Outputs: `analysis/phase23_warning_case_study/`
- Summary output: `analysis/phase23_warning_case_study/summary.json`
- Selected cases: `analysis/phase23_warning_case_study/selected_cases.csv`
- Case report: `analysis/phase23_warning_case_study/case_warning_report.md`
- Figures:
  - `analysis/phase23_warning_case_study/figures/case_warning_level_overview.png`
  - `analysis/phase23_warning_case_study/figures/case_risk_component_comparison.png`
  - `analysis/phase23_warning_case_study/figures/reliable_case_maps.png`
  - `analysis/phase23_warning_case_study/figures/caution_case_maps.png`
  - `analysis/phase23_warning_case_study/figures/high_risk_case_maps.png`
- Status: reliability-aware warning case-study and application prototype complete
- Selected case IDs: `location1|r100y_p0.5_d3h|6`, `location2|r300y_p0.6_d3h|6`, and `location2|r300y_p0.8_d3h|0`
- Core result: Phase 23 demonstrates warning-oriented interpretation with rapid prediction, reliability screening, scenario-level warning classification, pixel-level risk visualization, case-specific warning explanation, and applicability-boundary interpretation
- Decision: Phase 23 is an application-prototype phase, not a model-tuning or metric-chasing experiment
- Model status: no retraining, architecture modification, Phase 10 loss modification, `boundary_band_pixels` tuning, `boundary_weight` tuning, new sweep, or new prediction generation was performed
- Current recommended Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`

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
12. `docs/phase17_reliability_warning_framework_synthesis.md`
13. `docs/manuscript_reliability_aware_warning_layer.md`
14. `docs/manuscript_structure_and_submission_consolidation.md`
15. `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`
16. `docs/manuscript_evidence_figure_table_alignment.md`
17. `docs/manuscript_full_draft_reliability_aware_urban_flood_warning.md`
18. `docs/phase23_reliability_warning_case_study_findings.md`
19. `docs/project_status.md`

## Next Stage

The next stage should build on the Phase 12 to Phase 23 reliability/applicability, screening, warning-rule, synthesis, manuscript-writing, manuscript-consolidation, manuscript-draft, evidence-alignment, full-draft expansion, and warning case-study prototype materials rather than reopening Phase 10 tuning.

Recommended next work:

- consider calibrated uncertainty only if calibration data and evaluation design are added
- keep the current Phase 10 setting fixed unless new evidence justifies changing it
- avoid broader boundary-weight sweeps
- maintain the Phase 15 screening layer and Phase 16 warning-rule layer as deterministic operational support unless a new calibration design is added
