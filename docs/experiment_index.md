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
- Phase 24 physical consistency deepening and process diagnostics: diagnostic linkage between warning-risk labels and physical consistency of existing Phase 10 recommended outputs
- Phase 25 Physics-Consistency Guided Surrogate Refinement: Target-Wet Recall Consistency: targeted model refinement to reduce false-dry behavior and wet-area contraction while preserving the fixed Phase 10 boundary-band settings
- Phase 26 Strong Physics Constraint Feasibility Audit and Conservation-Proxy Diagnostics: audit of available physics inputs and conservation-proxy comparison of Phase 10 w20 versus Phase 25 target_wet_recall
- Phase 27 Conservative Volume-Response Consistency: seed42 mixed pilot with standard-metric improvement but primary volume-response objective not confirmed
- Phase 28 Volume-Response Loss Failure Diagnosis: diagnostic-only analysis explaining why the Phase 27 volume-response objective failed and why direct expansion should stop
- Phase 29 Tolerance-Band Volume Consistency: seed42 mixed pilot with partial volume-response repair but unacceptable trade-off
- Phase 30 Strong Physics Boundary Synthesis: documentation-only synthesis defining the current Level 4 conservation-proxy / physical-consistency-guided surrogate boundary
- Phase 31 Physics Input Recovery Readiness: diagnostic-only recovery and verification of Level 4+ static-map/domain/boundary/masked diagnostic support; Level 5 remains unsupported
- Phase 32 Domain-/Boundary-Aware Physical Consistency Design: design/diagnostic-only Level 4+ guardrail framework with decision `design_ready_no_training_yet`
- Phase 33 Seed42 Pilot Readiness Review: diagnostic/readiness-review complete with decision `pilot_design_ready_but_training_not_started` and `training_authorized = false`
- Phase 34 Pilot Threshold Formalization: threshold-formalization complete with decision `thresholds_formalized_training_still_blocked` and `training_authorized = false`
- Phase 35 Manhole False-Dry Guardrail Pilot Plan: pilot implementation plan complete with status `implementation_plan_ready_code_next` and `training_authorized = false`
- Phase 36 Manhole False-Dry Guardrail Code Smoke: code/smoke-test implementation complete with decision `code_smoke_ready_training_still_blocked`, `training_authorized = false`, and `training_executed = false`
- Phase 37 Seed42 Training Authorization Review: diagnostic authorization review complete with decision `seed42_training_authorized_next_phase`, `training_authorized_next_phase = true`, `training_executed = false`, and required checks passed `18 / 18`
- Phase 38 Seed42 Pilot Training and Guardrail Evaluation: single authorized seed42 pilot trained, test-evaluated, guardrail-evaluated, and rejected with decision `seed42_pilot_rejected`
- Phase 39 Failed Pilot Trade-off Diagnosis: diagnostic-only analysis complete with decision `tradeoff_diagnosis_completed_with_missing_optional_inputs`; Phase 38 remains `seed42_pilot_rejected`
- Phase 40 Failed Pilot Design Review and Next-Constraint Decision: design-review complete with decision `pause_loss_redesign_move_to_swe_data_readiness`, `training_authorized = false`, and next recommended phase `phase41_swe_data_readiness_audit`
- Phase 41 SWE Data Readiness Audit: no-training audit complete with decision `readiness_uncertain_requires_external_data_export`, `level5_supported = false`, `external_hydrodynamic_model_export_needed = true`, and `level4_proxy_supported = true`
- Phase 42 Hydrodynamic Export Requirement Specification: no-training requirement specification complete with decision `export_contract_ready_for_dataset_inspection` and `training_authorized = false`
- Phase 43 UrbanFlood24 Full Dataset Inspection: no-training inspection complete with decision `full_dataset_readiness_uncertain_needs_metadata`, `level5_supported = false`, `level4_plus_supported = true`, and `training_authorized = false`
- Phase 44 UrbanFlood24 Full Level 4+ Replanning: no-training replanning complete; short-term Level 5/SWE/PINN claims are frozen, and future work uses UrbanFlood24 full for Level 4+ proxy modeling, reliability diagnostics, and warning framework extension
- Phase 45 Full Dataset Indexing and Lightweight Adapter Preparation: no-training full dataset indexing complete with decision `indexing_ready_for_dataloader_smoke`, `scenario_count_total = 168`, `static_index_rows = 6`, `warning_count = 0`, `training_authorized = false`, `level4_plus_supported = true`, and `level5_supported = false`
- Phase 46 Dataloader Smoke, Downsample, and Tiling Feasibility: no-training dataloader smoke test complete with decision `dataloader_smoke_ready_for_downsample_baseline`, `scenario_index_loaded = true`, `static_index_loaded = true`, `representative_samples_count = 11`, `downsample_128_passed = true`, `downsample_256_passed = true`, `tile_checks_passed = true`, `batch_smoke_passed = true`, `memory_safe = true`, `training_authorized = false`, `level4_plus_supported = true`, and `level5_supported = false`
- Phase 47 Controlled Full-Dataset Downsample Baseline: controlled UrbanFlood24 full-dataset `128 x 128` downsample `seed42` 10e baseline complete with decision `phase47_controlled_128_downsample_seed42_pilot_completed`, `train_samples = 960`, `test_samples = 384`, `best_test_rmse = 0.01109213042097205`, `test_mae = 0.00525291082279485`, `test_wet_dry_iou = 0.8255524213115374`, `test_rollout_stability = 0.998722607580324`, `test_step_rmse_std = 0.0012824604989987165`, `no_swe_pinn = true`, and `level5_supported = false`
- Phase 48 Full-Dataset Reliability and Physical Proxy Diagnostics: no-training diagnostics complete with decision `phase48_diagnostics_ready_for_warning_framework_extension`, `checkpoint_found = true`, `evaluated_scenarios = 48`, `evaluated_windows = 384`, `mean_rmse = 0.012037189189155709`, `mean_mae = 0.005252910632811514`, `mean_wet_dry_iou = 0.863043953275997`, warning counts of 1 reliable, 12 caution, and 35 high-risk, `no_training = true`, `no_swe_pinn = true`, and `level5_supported = false`
- Phase 49 Full-Dataset Warning Framework Extension: no-training warning framework extension complete with decision `phase49_warning_framework_completed_with_conservative_labels`, `scenario_count = 48`, warning counts of 1 reliable, 12 caution, and 35 high-risk, `high_risk_case_count = 35`, `no_training = true`, and `warning_labels_are_probabilities = false`
- Phase 50 Framework Consolidation and Paper-Ready Evidence Synthesis: no-training synthesis complete with decision `phase50_framework_synthesis_ready_for_paper_outline`, `phases_synthesized = 43-49`, `level4_plus_route_supported = true`, `level5_supported = false`, `no_training = true`, `no_swe_pinn = true`, and `warning_labels_are_probabilities = false`

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

## Phase 24

- Plan: `docs/phase24_physical_consistency_deepening_plan.md`
- Script: `scripts/analyze_phase24_physical_consistency.py`
- Findings: `docs/phase24_physical_consistency_deepening_findings.md`
- Outputs: `analysis/phase24_physical_consistency/`
- Summary output: `analysis/phase24_physical_consistency/summary.json`
- Scenario metrics: `analysis/phase24_physical_consistency/scenario_physical_consistency_metrics.csv`
- Volume response: `analysis/phase24_physical_consistency/volume_response_metrics.csv`
- Peak-depth consistency: `analysis/phase24_physical_consistency/peak_depth_consistency.csv`
- Wet connectivity: `analysis/phase24_physical_consistency/wet_connectivity_metrics.csv`
- Temporal consistency: `analysis/phase24_physical_consistency/temporal_consistency_metrics.csv`
- Physics-risk linkage: `analysis/phase24_physical_consistency/physics_risk_linkage.csv`
- Topographic consistency: `analysis/phase24_physical_consistency/topographic_consistency.csv`
- Figures:
  - `analysis/phase24_physical_consistency/figures/volume_bias_by_warning_level.png`
  - `analysis/phase24_physical_consistency/figures/peak_underprediction_by_warning_level.png`
  - `analysis/phase24_physical_consistency/figures/physics_consistency_vs_risk_score.png`
  - `analysis/phase24_physical_consistency/figures/wet_connectivity_fragmentation.png`
  - `analysis/phase24_physical_consistency/figures/temporal_volume_bias_examples.png`
  - `analysis/phase24_physical_consistency/figures/phase23_case_physical_failure_profiles.png`
- Status: physical consistency deepening and process diagnostics complete
- Core result: high-risk cases are not only statistically worse; they are physically less consistent than reliable cases
- Risk-score correlations: `false_dry_rate` = 0.913, `wet_area_contraction` = 0.862, `peak_depth_underprediction` = 0.856, and `connectivity_loss_indicator` = 0.539
- Warning-level means for `reliable` / `caution` / `high-risk`: `false_dry_rate` = 0.125 / 0.268 / 0.444, `wet_area_contraction` = 0.046 / 0.135 / 0.383, `peak_depth_underprediction` = 0.024 m / 0.241 m / 1.381 m, `connectivity_loss_indicator` = 0.197 / 0.240 / 1.000, and `relative_volume_bias` = -0.040 / -0.145 / -0.448
- Skipped diagnostic: topographic consistency was skipped because no shape-compatible DEM/static elevation layer was found
- Decision: later model refinement should prioritize targeted physical-consistency constraints; a full SWE/PINN residual is not recommended without compatible velocity, flux, boundary, DEM, and source-sink information
- Model status: no retraining, architecture modification, Phase 10 loss modification, `boundary_band_pixels` tuning, `boundary_weight` tuning, new sweep, metric-chasing experiment, traffic-impact modeling, or new prediction generation was performed
- Current recommended Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`

## Phase 25

- Plan: `docs/phase25_physics_consistency_guided_refinement_plan.md`
- Loss implementation: `utils/physics_losses.py`
- Configs:
  - `configs/train_phase25_target_wet_recall_seed123_40e.json`
  - `configs/train_phase25_target_wet_recall_seed42_40e.json`
  - `configs/train_phase25_target_wet_recall_seed202_40e.json`
- Implementation note: `docs/phase25_target_wet_recall_implementation_note.md`
- Comparison script: `scripts/compare_phase25_target_wet_recall_aligned.py`
- Visualization script: `scripts/plot_phase25_summary_figures.py`
- Outputs: `analysis/phase25_target_wet_recall_comparison/`
- Figures:
  - `analysis/phase25_target_wet_recall_comparison/figures/phase25_standard_metric_deltas_three_seeds.png`
  - `analysis/phase25_target_wet_recall_comparison/figures/phase25_aligned_physical_deltas_three_seeds.png`
- Pilot findings: `docs/phase25_target_wet_recall_pilot_findings.md`
- Guardrail findings: `docs/phase25_seed42_guardrail_findings.md`
- Three-seed synthesis: `docs/phase25_three_seed_target_wet_recall_synthesis_findings.md`
- Status: three-seed target-wet recall refinement synthesis complete
- Fixed inherited setting: Phase 10 boundary-band settings remained `boundary_band_pixels = 1` and `boundary_weight = 2.0`
- Phase 25 loss setting: `target_wet_recall_consistency.weight = 0.02`, `threshold = 0.05`, `temperature = 0.02`, and `eps = 1e-6`
- Standard test mean deltas versus Phase 10: `RMSE = -0.007057`, `MAE = -0.001519`, `wet/dry IoU = +0.076670`, `rollout stability = +0.001035`, and `step RMSE std = -0.001071`
- Aligned physical mean deltas versus Phase 10: `false_dry_rate = -0.111321`, `wet_area_contraction = -0.079104`, `relative_volume_bias = +0.105093`, `peak_depth_underprediction = -0.014962`, `RMSE = -0.007244`, `MAE = -0.001885`, `false_wet_rate = +0.003844`, and `connectivity_loss_indicator = +0.078947`
- Core result: false-dry rate and wet-area contraction improved in all three seeds, relative volume bias became less negative on average, and standard RMSE/MAE/wet-dry IoU improved across all three seeds
- Limitation: false-wet rate increased slightly and connectivity loss was not consistently improved
- Decision: Phase 25 target-wet recall is a strong three-seed positive candidate and credible targeted refinement over the Phase 10 baseline, but not a complete physical-consistency solution or full SWE/PINN residual

## Phase 26

- Plan: `docs/phase26_strong_physics_constraint_feasibility_plan.md`
- Input audit script: `scripts/audit_phase26_physics_inputs.py`
- Conservation diagnostic script: `scripts/analyze_phase26_conservation_residual.py`
- Findings: `docs/phase26_strong_physics_constraint_feasibility_findings.md`
- Outputs: `analysis/phase26_strong_physics_constraint_feasibility/`
- Summary outputs:
  - `physics_input_audit.json`
  - `physics_input_audit.md`
  - `conservation_residual_by_step.csv`
  - `conservation_residual_by_run.csv`
  - `conservation_residual_by_seed.csv`
  - `conservation_residual_phase_delta.csv`
  - `summary.json`
  - `conservation_residual_summary.md`
- Status: strong-physics feasibility audit and conservation-proxy diagnostics complete
- Core result: current data partially support Level 4 conservation-oriented diagnostics, leave Level 4 conservation-aware loss design unclear, and do not support Level 5 full SWE/PINN residual constraints
- Conservation-proxy result: Phase 25 improves aggregate volume response, false-dry volume loss, wet-area contraction, peak-depth preservation, RMSE, and MAE relative to Phase 10 w20
- Guardrail: Phase 25 is not a strict timestep-wise conservation solution; timestep-wise absolute relative volume bias is mixed, and false-wet trade-offs increase slightly
- Model status: no retraining, architecture modification, Phase 10 loss change, boundary tuning, Phase 25 weight sweep, full SWE/PINN implementation, or new prediction generation was performed

## Phase 27

- Plan: `docs/phase27_conservative_volume_response_consistency_plan.md`
- Loss implementation: `utils/physics_losses.py`
- Config: `configs/train_phase27_volume_response_seed42_40e.json`
- Comparison script: `scripts/compare_phase27_volume_response_seed42.py`
- Findings: `docs/phase27_seed42_volume_response_pilot_findings.md`
- Outputs: `analysis/phase27_conservative_volume_response_consistency/`
- Summary output: `analysis/phase27_conservative_volume_response_consistency/phase27_seed42_summary.md`
- Status: seed42 mixed pilot complete
- Core result: standard metrics improved and several under-response proxies improved, but the primary volume-response objective was not confirmed
- Standard metric deltas versus Phase 25 seed42: `RMSE = -0.00236602`, `MAE = -0.000654673`, `wet/dry IoU = +0.00892365`, `rollout stability = +0.000618097`, and `step RMSE std = -0.000631138`
- Positive physical indicators: `false_dry_volume_loss = -1.77546`, `wet_area_contraction = -0.00626303`, `peak_depth_underprediction = -0.011376`, `false_wet_rate = -0.000387357`, and `false_wet_volume_excess = -0.403664`
- Failed primary objective: aggregate absolute relative volume bias worsened by `+0.0216934`, mean-step absolute relative volume bias worsened by `+0.0170953`, and run-level aggregate relative volume bias moved from Phase 25 `+0.00296825` to Phase 27 `+0.0246616`
- Decision: `remain_seed42_positive_only`
- Guardrail: no `seed123` / `seed202` confirmation, no Phase 27 weight sweep, no SWE/PINN claim, no strict timestep-wise conservation claim, no full mass-conservation claim, and no strong physics success claim

## Phase 28

- Plan: `docs/phase28_volume_response_loss_diagnosis_plan.md`
- Diagnostic script: `scripts/diagnose_phase28_volume_response_failure.py`
- Findings: `docs/phase28_volume_response_loss_diagnosis_findings.md`
- Outputs: `analysis/phase28_volume_response_loss_diagnosis/`
- Summary outputs:
  - `volume_bias_decomposition_by_step.csv`
  - `volume_bias_depth_bin_decomposition.csv`
  - `volume_bias_timestep_ranking.csv`
  - `volume_bias_decomposition_summary.csv`
  - `phase28_volume_response_failure_summary.json`
  - `phase28_volume_response_failure_findings.md`
- Status: volume-response loss failure diagnosis complete
- Core result: Phase 27 volume-bias worsening is dominated by `dry_or_threshold` depth-bin volume accumulation, not false-wet expansion or already-wet amplification.
- Key evidence: `delta_volume_bias_total = +6974.12`, Phase 25 relative volume bias = `+0.00296825`, Phase 27 relative volume bias = `+0.0246616`, false-wet volume excess delta = `-184.071`, already-wet amplification = `+1396.20`, and `dry_or_threshold` contribution = `+5362.82`, about `76.9%` of total delta volume bias.
- Decision: stop direct expansion of the Phase 27 underresponse-only loss.
- Historical next direction: tolerance-band volume consistency redesign, only after a new plan.
- Guardrail: no `seed123` / `seed202` confirmation, no sweep, no strict conservation, no mass-conservation, no SWE/PINN claim.
- Model status: diagnostic only; no training, architecture modification, loss modification, config modification, new confirmation run, or weight sweep was performed.

## Phase 29

- Plan: `docs/phase29_tolerance_band_volume_consistency_plan.md`
- Loss/config:
  - `utils/physics_losses.py`
  - `configs/train_phase29_tolerance_band_volume_seed42_40e.json`
- Comparison script: `scripts/compare_phase29_tolerance_band_volume_seed42.py`
- Findings: `docs/phase29_seed42_tolerance_band_volume_findings.md`
- Outputs: `analysis/phase29_tolerance_band_volume_consistency/`
- Summary outputs:
  - `phase29_seed42_by_step.csv`
  - `phase29_seed42_by_run.csv`
  - `phase29_seed42_delta_vs_phase25.csv`
  - `phase29_seed42_delta_vs_phase27.csv`
  - `phase29_seed42_depth_bin_decomposition.csv`
  - `phase29_seed42_summary.json`
  - `phase29_seed42_summary.md`
- Status: seed42 mixed tolerance-band pilot complete
- Core result: partial volume-response repair, unacceptable trade-off
- Positive evidence versus Phase 27: aggregate absolute relative volume bias improved from `0.0246616` to `0.019464`, mean-step absolute relative volume bias improved from `0.257274` to `0.230447`, and `dry_or_threshold` contribution decreased from `0.137662` to `0.131428`
- Negative evidence versus Phase 27: all listed standard metrics worsened, false-dry volume loss worsened from `5409.72` to `5964.83`, false-wet volume excess worsened from `7750.32` to `8289.77`, peak-depth underprediction worsened from `0.128045` to `0.134593`, and aggregate bias remains far from Phase 25 `0.00296825`
- Seed42 test metrics: `RMSE = 0.0443854521`, `MAE = 0.0178462429`, `wet/dry IoU = 0.8016409529`, `rollout stability = 0.9895110601`, and `step RMSE std = 0.0106412431`
- Decision: `remain_seed42_only_pending_revision`
- Guardrail: no `seed123` / `seed202`, no tolerance or weight sweep, no strict conservation, no mass-conservation, no SWE/PINN claim.
- Model status: no tolerance-band success claim; future loss redesign or training requires a new plan.

## Phase 30

- Plan: `docs/phase30_strong_physics_boundary_synthesis_plan.md`
- Synthesis: `docs/phase30_strong_physics_boundary_synthesis.md`
- Status: strong-physics boundary synthesis complete
- Core result: Level 4 conservation-proxy / physical-consistency-guided surrogate; Level 5 SWE/PINN is not supported
- Decision: pause Phase 27/29 seed expansion and sweeps; prefer manuscript / README / research narrative consolidation next
- Guardrails: no training, no loss change, no `seed123` / `seed202`, no sweep, no strict conservation, no SWE/PINN, and no full hydrodynamic closure claim

## Phase 31

- Plan: `docs/phase31_physics_input_recovery_readiness_plan.md`
- Findings: `docs/phase31_physics_input_recovery_readiness_findings.md`
- Scripts:
  - `scripts/audit_phase31_dataset_physics_inputs.py`
  - `scripts/inspect_phase31_static_maps.py`
  - `scripts/build_phase31_domain_boundary_masks.py`
  - `scripts/analyze_phase31_masked_physical_errors.py`
- Outputs: `analysis/phase31_physics_input_recovery_readiness/`
- Key output files:
  - `physics_input_inventory.md`
  - `physics_input_inventory.json`
  - `static_map_inspection.md`
  - `static_map_inspection.json`
  - static-map inspection CSVs
  - `domain_boundary_mask_inspection.md`
  - `domain_boundary_mask_inspection.json`
  - domain-boundary mask CSV
  - `masked_physical_error_findings.md`
  - masked physical error JSON
  - masked physical error CSVs
  - `figures/`
- Status: Level 4+ physics input recovery and masked diagnostic readiness complete
- Core result: Level 4+ static-map/domain/boundary/masked diagnostics are supported; Level 5 is unsupported
- Evidence: raw flood/rain/static arrays are available; `absolute_DEM.npy`, `impervious.npy`, and `manhole.npy` are `128 x 128`; `absolute_DEM < 99` supports valid-domain masks; valid-domain, invalid/high, boundary-ring, and interior masks can be constructed; sample-to-location mapping was recovered from adjacent `summary.json` `metadata.location`
- Masked diagnostic result: Phase 29 improves valid-domain masked relative volume-bias proxy versus Phase 27 (`0.0169359` to `0.0115344`) but worsens valid-domain `RMSE`, `MAE`, false-dry, false-wet, false-dry volume-loss proxy, and false-wet volume-excess proxy
- Decision: pass forward to Phase 32 design guardrails; no immediate training or loss change from Phase 31 alone
- Guardrails: no strict conservation, no full mass conservation, no SWE/PINN, no hydrodynamic closure, no Phase 29 success claim, no `seed123` / `seed202` expansion from Phase 29
- Model status: diagnostic only; no retraining, architecture modification, loss modification, config modification, seed expansion, or sweep was performed

## Phase 32

- Plan: `docs/phase32_domain_boundary_aware_physical_consistency_plan.md`
- Design: `docs/phase32_domain_boundary_aware_design.md`
- Guardrail script: `scripts/design_phase32_domain_boundary_guardrails.py`
- Findings: `docs/phase32_domain_boundary_aware_physical_consistency_findings.md`
- Outputs: `analysis/phase32_domain_boundary_aware_design/`
- Key output files:
  - `guardrail_metrics.csv`
  - `stop_go_criteria.csv`
  - `design_summary.json`
  - `phase32_guardrail_summary.md`
- Status: design/diagnostic-only complete
- Core result: Level 4+ domain-/boundary-aware physical consistency design formalized; current decision `design_ready_no_training_yet`
- Decision: no immediate training; no loss modification; no `seed123` / `seed202`; no sweep
- Guardrail groups: standard, valid_domain, boundary_ring, high_impervious_valid, manhole_nonzero_valid, dry_threshold, and level_boundary
- Guardrail formalization: 20 guardrail metrics and 12 stop/go criteria
- Evidence basis: Phase 31 recovered `valid_domain = absolute_DEM < 99`; boundary-ring and interior masks are supported; `high_impervious_valid` and `manhole_nonzero_valid` are supported; sample-to-location mapping is recovered; masked diagnostics are supported
- Mixed Phase 29 evidence: Phase 29 improved valid-domain relative volume-bias proxy versus Phase 27 from `0.0169359` to `0.0115344`, but worsened valid-domain `RMSE` from `0.0460827` to `0.0480984`, `MAE` from `0.0183693` to `0.0190492`, `false_dry_rate` from `0.0689175` to `0.0739891`, `false_wet_rate` from `0.0181923` to `0.0194308`, `false_dry_volume_loss_proxy` from `3575.36` to `4027.38`, and `false_wet_volume_excess_proxy` from `5263.67` to `5690.27`
- Guardrails: no strict conservation, no full mass conservation, no SWE/PINN, no hydrodynamic closure, no Phase 29 success claim
- Level boundary: Level 4+ proxy diagnostics supported; Level 5 remains unsupported
- Model status: design/diagnostic only; no training, architecture modification, loss modification, config modification, seed expansion, or sweep was performed

## Phase 33

- Plan: `docs/phase33_seed42_pilot_readiness_review_plan.md`
- Script: `scripts/review_phase33_seed42_pilot_readiness.py`
- Findings: `docs/phase33_seed42_pilot_readiness_review_findings.md`
- Outputs: `analysis/phase33_seed42_pilot_readiness/`
- Key output files:
  - `pilot_option_scores.csv`
  - `readiness_criteria_status.csv`
  - `phase33_readiness_summary.json`
  - `phase33_readiness_summary.md`
- Status: diagnostic/readiness-review complete
- Core result: `manhole_nonzero_false_dry_guardrail` is the strongest future candidate, but `training_authorized = false`
- Decision: `pilot_design_ready_but_training_not_started`
- Evidence: 5 pilot options and 15 readiness criteria were reviewed
- Blocking criteria: numeric acceptance thresholds, numeric rejection thresholds, and full Phase 25 / Phase 27 / Phase 29 baseline acceptance/rejection criteria are not fixed
- Guardrails: no training, no `seed123` / `seed202`, no sweep, no Phase 29 continuation, no strict conservation, no full mass conservation, no SWE/PINN, and no hydrodynamic closure
- Model status: diagnostic/readiness-review only; no training, architecture modification, loss modification, config modification, seed expansion, sweep, or Phase 29 continuation was performed

## Phase 34

- Plan: `docs/phase34_pilot_threshold_formalization_plan.md`
- Script: `scripts/formalize_phase34_pilot_thresholds.py`
- Findings: `docs/phase34_pilot_threshold_formalization_findings.md`
- Outputs: `analysis/phase34_pilot_thresholds/`
- Key output files:
  - `baseline_metric_table.csv`
  - `acceptance_thresholds.csv`
  - `rejection_thresholds.csv`
  - `threshold_readiness_status.csv`
  - `phase34_threshold_summary.json`
  - `phase34_threshold_summary.md`
- Status: threshold formalization complete
- Core result: baseline, acceptance, and rejection thresholds fixed for future `manhole_nonzero_false_dry_guardrail` pilot
- Evidence: 23 baseline metric rows, 14 acceptance threshold rows, 9 rejection threshold rows, and 7 readiness rows were formalized
- Candidate: `manhole_nonzero_false_dry_guardrail`
- Target: `manhole_nonzero_valid` `false_dry_rate`
- AT01 threshold: Phase 27 = `0.1172229713`, Phase 29 = `0.131297982994`, threshold = `0.1172229713`; the target metric must be below Phase 29 and no higher than Phase 27
- RT01 rejection rule: reject the Phase 29 trade-off pattern if absolute relative volume-bias proxy improves while RMSE, MAE, false-dry rate, and false-wet rate all worsen versus Phase 27
- AT13: volume-bias proxy improvement is conditional and not sufficient alone
- AT14 / RT09: preserve the Level 4+ proxy claim boundary
- Decision: `thresholds_formalized_training_still_blocked`
- Next allowed step: `pilot_implementation_plan`
- Guardrails: no training, no `seed42` run, no `seed123` / `seed202`, no sweep, no Phase 29 continuation, no loss modification, no config modification, no architecture modification, no strict conservation, no full mass conservation, no SWE/PINN, no hydrodynamic closure
- Model status: threshold-formalization only; no training, architecture modification, loss modification, config modification, seed expansion, sweep, or Phase 29 continuation was performed

## Phase 35

- Plan: `docs/phase35_manhole_false_dry_guardrail_pilot_plan.md`
- Status: pilot implementation plan complete
- Decision: `implementation_plan_ready_code_next`
- Current authorization: `training_authorized = false`
- Candidate: `manhole_nonzero_false_dry_guardrail`
- Target region: `manhole_nonzero_valid`
- Target metric: `false_dry_rate`
- Key threshold: AT01 `false_dry_rate` threshold = `0.1172229713`
- Core result: Phase 35 translates the Phase 34 thresholds into a conservative implementation plan for review only
- Implementation status: no losses implemented; no configs created; no model code modified; no training run performed
- Next allowed step: code/smoke-test implementation phase, not training
- Guardrails: no training, no `seed42` run, no `seed123` / `seed202`, no sweep, no Phase 29 continuation, no strict conservation, no full mass conservation, no SWE/PINN, no hydrodynamic closure, and Level 4+ proxy scope only
- Model status: planning-only; any later code/smoke-test phase must still keep training blocked unless separately authorized

## Phase 36

- Plan: `docs/phase36_manhole_false_dry_guardrail_code_smoke_plan.md`
- Findings: `docs/phase36_manhole_false_dry_guardrail_code_smoke_findings.md`
- Loss/code: `utils/physics_losses.py`
- Config draft: `configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`
- Guardrail checker: `scripts/check_phase36_pilot_guardrails.py`
- Outputs: `analysis/phase36_manhole_false_dry_guardrail_code_smoke/`
- Key output files:
  - `guardrail_checker_dry_run.json`
  - `guardrail_checker_dry_run.md`
  - `smoke_test_summary.json`
  - `smoke_test_summary.md`
- Status: code/smoke-test complete; training blocked
- Core result: config-gated `manhole_nonzero_false_dry_guardrail` code path and guardrail checker smoke-tested
- Decision: `code_smoke_ready_training_still_blocked`
- Smoke-test evidence: `config_loaded = true`; `loss_smoke_passed = true`; `guardrail_checker_dry_run_passed = true`; `training_authorized = false`; `training_executed = false`; `seed42_run_executed = false`; `seed123_seed202_executed = false`
- Guardrail checker dry-run evidence: `candidate = manhole_nonzero_false_dry_guardrail`; `claim_scope = Level 4+ static-map-aware proxy diagnostics only`; `training_authorized = false`; `training_result_available = false`; `decision = no_training_result_guardrail_check_dry_run`; `status = dry_run_passed`; `acceptance_threshold_count = 14`; `rejection_threshold_count = 9`; `baseline_metric_count = 23`; `acceptance_structure_ready = true`; `rejection_structure_ready = true`
- Guardrails: no training, no seed42 run, no seed123/seed202, no sweep, no Phase 29 continuation, no strict conservation, no SWE/PINN, no hydrodynamic closure
- Model status: code/smoke-test only; no pilot success claim and no training authorization

## Phase 37

- Plan: `docs/phase37_seed42_training_authorization_review_plan.md`
- Script: `scripts/review_phase37_seed42_training_authorization.py`
- Findings: `docs/phase37_seed42_training_authorization_review_findings.md`
- Outputs: `analysis/phase37_seed42_training_authorization/`
- Key output files:
  - `authorization_checklist.csv`
  - `training_authorization_summary.json`
  - `training_authorization_summary.md`
- Status: authorization review complete
- Core result: seed42 training authorized for next phase only
- Decision: `seed42_training_authorized_next_phase`
- Required checks passed: `18 / 18`
- Authorization: `training_authorized_next_phase = true`; `training_executed = false`; `seed42_run_executed = false`; `seed123_seed202_executed = false`
- Reviewed command: `python scripts/train_model.py --config configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`
- Reviewed config: `configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`
- Guardrails: Phase 37 did not train; next phase may run only the reviewed seed42 config; after training, evaluate and run the Phase 36 guardrail checker; any RT01-RT09 trigger rejects the result; no seed123/seed202; no sweep; no Phase 29 continuation; no strict conservation / SWE/PINN / hydrodynamic closure claims; Level 4+ proxy scope only
- Model status: diagnostic authorization review only; no pilot success claim and no training result claim

## Phase 38

- Plan: `docs/phase38_seed42_pilot_training_guardrail_evaluation_plan.md`
- Guardrail evaluator: `scripts/evaluate_phase38_seed42_guardrails.py`
- Findings: `docs/phase38_seed42_pilot_training_guardrail_evaluation_findings.md`
- Run output: `runs/phase36_manhole_false_dry_guardrail_seed42_40e/`
- Evaluation metrics: `runs/phase36_manhole_false_dry_guardrail_seed42_40e/evaluation_test/metrics.json`
- Outputs: `analysis/phase38_seed42_pilot_training_guardrail_evaluation/`
- Key output files:
  - `phase38_standard_metric_check.csv`
  - `phase38_acceptance_check.csv`
  - `phase38_rejection_check.csv`
  - `phase38_guardrail_decision.json`
  - `phase38_guardrail_decision.md`
- Status: seed42 pilot trained, evaluated, and rejected
- Decision: `seed42_pilot_rejected`
- Training/evaluation status: training completed; test evaluation completed; guardrail evaluation completed
- Test metrics: `RMSE = 0.04456830142359985`, `MAE = 0.01795931400633172`, `wet_dry_iou = 0.8068740587485465`, `rollout_stability = 0.9899644569346779`, and `step_rmse_std = 0.01018835528214511`
- Guardrail counts: standard checks passed `2`, standard checks failed `3`, acceptance checks passed `6`, acceptance checks failed `8`, acceptance checks not evaluated `0`, rejection rules triggered `3`, and rejection rules not evaluated `0`
- Failed checks: AT02 valid-domain RMSE, AT03 valid-domain MAE, AT04 valid-domain false_dry_rate, AT06 high_impervious_valid false_wet_rate, AT07 boundary_ring false_dry_rate, AT08 standard RMSE, AT09 standard MAE, and AT10 standard wet_dry_iou
- Triggered rejection rules: RT01 `phase29_tradeoff_pattern`, RT05 `standard_rmse_or_mae_worsens_beyond_tolerance`, and RT07 `valid_domain_error_worsens_beyond_acceptance_tolerance`
- Interpretation: useful negative evidence, not a training execution failure; the `manhole_nonzero_false_dry_guardrail` design is not accepted
- Guardrails: no seed123/seed202 expansion; no sweep; no Phase 29 continuation; no post-hoc loss/config rescue; no pilot success claim; no strict conservation / SWE/PINN / hydrodynamic closure claims; Level 4+ proxy scope only
- Model status: rejected seed42 pilot; Phase 39 later diagnosed the trade-off before any further design work

## Phase 39

- Plan: `docs/phase39_failed_pilot_tradeoff_diagnosis_plan.md`
- Script: `scripts/diagnose_phase39_failed_pilot_tradeoffs.py`
- Findings: `docs/phase39_failed_pilot_tradeoff_diagnosis_findings.md`
- Outputs: `analysis/phase39_failed_pilot_tradeoff_diagnosis/`
- Key output files:
  - `failed_acceptance_components.csv`
  - `triggered_rejection_rules.csv`
  - `phase38_vs_baselines_metric_comparison.csv`
  - `region_tradeoff_summary.csv`
  - `scenario_tradeoff_summary.csv`
  - `phase39_tradeoff_diagnosis_summary.json`
  - `phase39_tradeoff_diagnosis_summary.md`
- Status: diagnostic-only trade-off diagnosis complete
- Decision: `tradeoff_diagnosis_completed_with_missing_optional_inputs`
- Phase 38 status: remains `seed42_pilot_rejected`
- Diagnostic counts: `failed_acceptance_count = 8`, `triggered_rejection_count = 3`, `comparison_rows = 13`, `region_rows = 5`, and `scenario_rows = 19`
- Main diagnosis: the current `manhole_nonzero_false_dry_guardrail` improved a narrow `manhole_nonzero_valid` false-dry proxy, but did not preserve broader valid-domain, regional guardrail, and standard metrics
- Rejection interpretation: RT01 indicates a Phase29-like trade-off pattern; RT05 and RT07 confirm unacceptable standard and valid-domain error behavior
- Missing optional inputs: per-batch/scenario Phase25/Phase27/Phase29 baselines are unavailable, so scenario diagnostics are Phase38-only
- Interpretation: useful negative evidence, not a training or evaluation failure
- Guardrails: no training; no seed123/seed202 expansion; no sweep; no Phase 29 continuation; no post-hoc rescue; no pilot success claim; no strict conservation / SWE/PINN / hydrodynamic closure claims
- Model status: rejected pilot diagnosed; Phase 40 later completed the failed-pilot design review and next-constraint decision before any further technical work

## Phase 40

- Plan: `docs/phase40_failed_pilot_design_review_next_constraint_plan.md`
- Script: `scripts/review_phase40_next_constraint_decision.py`
- Findings: `docs/phase40_failed_pilot_design_review_next_constraint_findings.md`
- Outputs: `analysis/phase40_failed_pilot_design_review/`
- Key output files:
  - `next_constraint_options.csv`
  - `decision_criteria_matrix.csv`
  - `phase40_next_constraint_decision.json`
  - `phase40_next_constraint_decision.md`
- Status: failed-pilot design review and next-constraint decision complete
- Decision: `pause_loss_redesign_move_to_swe_data_readiness`
- Next recommended phase: `phase41_swe_data_readiness_audit`
- Guardrails:
  - no training
  - no seed123/seed202 expansion
  - no sweep
  - no Phase38 rescue
  - no loss/config/model edits
  - no strict conservation / SWE/PINN / hydrodynamic closure claims
  - no Level 5 support claim
- Model status: proxy-loss redesign paused after repeated trade-off evidence from Phase 27, Phase 29, and Phase 38; the no-training SWE data readiness audit was completed in Phase 41

## Phase 41

- Plan: `docs/phase41_swe_data_readiness_audit_plan.md`
- Script: `scripts/audit_phase41_swe_data_readiness.py`
- Findings: `docs/phase41_swe_data_readiness_audit_findings.md`
- Outputs: `analysis/phase41_swe_data_readiness_audit/`
- Key output files:
  - `swe_required_data_inventory.csv`
  - `repository_search_summary.csv`
  - `dataset_field_inventory.csv`
  - `swe_readiness_matrix.csv`
  - `missing_swe_inputs.csv`
  - `phase41_swe_data_readiness_summary.json`
  - `phase41_swe_data_readiness_summary.md`
- Status: no-training SWE data readiness audit complete
- Decision: `readiness_uncertain_requires_external_data_export`
- Summary: `categories_evaluated = 10`; `categories_supported = 5`; `level5_supported = false`; `external_hydrodynamic_model_export_needed = true`; `level4_proxy_supported = true`
- Interpretation: current evidence supports Level 4+ proxy diagnostics and data recovery only. Level 5 SWE/PINN residual constraints are not currently supported.
- Missing or uncertain SWE-critical categories: velocity or flux fields, `dx/dy` grid spacing, `dt` time step, boundary conditions, pump/gate operations, complete source/sink terms, and complete hydrodynamic state variables.
- Guardrails:
  - no training
  - no seed runs
  - no sweeps
  - no loss/config/model edits
  - no SWE residual implementation
  - no PINN implementation
  - no strict conservation / full mass conservation / hydrodynamic closure claims
  - no Level 5 support claim
- Model status: SWE data readiness has been audited; Phase 44 later froze the short-term Level 5/SWE/PINN route

## Phase 42

- Plan: `docs/phase42_hydrodynamic_export_requirement_specification_plan.md`
- Script: `scripts/specify_phase42_hydrodynamic_export_requirements.py`
- Findings: `docs/phase42_hydrodynamic_export_requirement_specification_findings.md`
- Outputs: `analysis/phase42_hydrodynamic_export_requirements/`
- Key output files:
  - `required_hydrodynamic_fields.csv`
  - `field_unit_shape_time_requirements.csv`
  - `swe_residual_minimum_data_contract.csv`
  - `export_priority_table.csv`
  - `urbanflood24_full_inspection_checklist.csv`
  - `icm_mike_export_checklist.csv`
  - `phase42_export_requirement_summary.json`
  - `phase42_export_requirement_summary.md`
- Status: no-training hydrodynamic export requirement specification complete
- Decision: `export_contract_ready_for_dataset_inspection`
- Summary: `training_authorized = false`; `required_fields_count = 16`; `minimum_contract_items = 10`; `urbanflood24_checklist_items = 10`; `icm_mike_checklist_items = 13`
- Interpretation: Phase 42 creates a formal hydrodynamic export/data contract for future dataset inspection and external export requests. It does not claim Level 5 support.
- Next work at the time: inspect the UrbanFlood24 full dataset if available and/or evaluate export requirements. Phase 44 later superseded this as the active route.
- Guardrails:
  - no training
  - no seed runs
  - no sweeps
  - no loss/config/model edits
  - no SWE residual implementation
  - no PINN implementation
  - no strict conservation / full mass conservation / hydrodynamic closure claims
  - no Level 5 support claim
- Model status: export/data-contract specification only; Phase 44 later redirected active work to UrbanFlood24 full Level 4+ modeling rather than SWE/PINN implementation

## Phase 43

- Plan: `docs/phase43_urbanflood24_full_dataset_inspection_plan.md`
- Script: `scripts/inspect_phase43_urbanflood24_full_dataset.py`
- Findings: `docs/phase43_urbanflood24_full_dataset_inspection_findings.md`
- Outputs: `analysis/phase43_urbanflood24_full_dataset_inspection/`
- Key output files:
  - `full_dataset_file_inventory.csv`
  - `field_keyword_search_results.csv`
  - `sample_array_shape_inventory.csv`
  - `phase42_contract_compliance_matrix.csv`
  - `level5_readiness_assessment.csv`
  - `phase43_urbanflood24_full_dataset_summary.json`
  - `phase43_urbanflood24_full_dataset_summary.md`
- Status: no-training UrbanFlood24 full dataset inspection complete
- Decision: `full_dataset_readiness_uncertain_needs_metadata`
- Summary: `level5_supported = false`; `level4_plus_supported = true`; `training_authorized = false`; `total_files = 354`; `total_dirs = 186`; `sampled_arrays_count = 54`
- Interpretation: UrbanFlood24 full supports higher-resolution Level 4+ proxy diagnostics, but direct Level 5 SWE/PINN readiness remains unsupported because required velocity/flux, grid/time, boundary/source-sink, pump/gate, CRS/grid, units, scenario, and time-axis metadata are absent or uncertain.
- Next work at the time: metadata/export-path review. Phase 44 later superseded this with the UrbanFlood24 full Level 4+ route.
- Guardrails:
  - no training
  - no seed runs
  - no sweeps
  - no loss/config/model edits
  - no SWE residual implementation
  - no PINN implementation
  - no strict conservation / full mass conservation / hydrodynamic closure claims
  - no Level 5 support claim
- Model status: full dataset inspection only; Phase 44 later superseded metadata/export follow-up as the active project path

## Phase 44

- Plan/Replanning: `docs/phase44_urbanflood24_full_level4plus_replanning.md`
- Status: Level 4+ full-dataset replanning complete
- Decision: freeze short-term Level 5/SWE/PINN claims and proceed with UrbanFlood24 full Level 4+ route
- Next phase: Phase 45 full dataset indexing and lightweight adapter
- Guardrails:
  - no training
  - no seed runs
  - no sweeps
  - no loss/config/model edits
  - no SWE residual implementation
  - no PINN implementation
  - no strict conservation / full mass conservation / hydrodynamic closure claims
  - no Level 5 support claim
- Model status: replanning only; future work is high-resolution Level 4+ proxy modeling, reliability diagnostics, and warning framework extension using the already downloaded UrbanFlood24 full dataset

## Phase 45

- Plan: `docs/phase45_full_dataset_indexing_lightweight_adapter_plan.md`
- Script: `scripts/build_phase45_full_dataset_index.py`
- Findings: `docs/phase45_full_dataset_indexing_lightweight_adapter_findings.md`
- Outputs: `analysis/phase45_full_dataset_indexing/`
- Key output files:
  - `scenario_index.csv`
  - `static_geodata_index.csv`
  - `dataset_index_summary.json`
  - `dataset_index_summary.md`
  - `adapter_design_notes.md`
- Status: no-training full dataset indexing complete
- Decision: `indexing_ready_for_dataloader_smoke`
- Next phase: Phase 46 dataloader smoke test and downsample/tiling feasibility
- Guardrails:
  - no training
  - no seed runs
  - no sweeps
  - no loss/config/model edits
  - no SWE residual implementation
  - no PINN implementation
  - no strict conservation / full mass conservation / hydrodynamic closure claims
  - no Level 5 support claim
- Model status: indexing and lightweight adapter preparation only; UrbanFlood24 full has a reproducible machine-readable index, but training remains unauthorized until Phase 46 dataloader smoke tests pass

## Phase 46

- Plan: `docs/phase46_dataloader_smoke_downsample_tiling_feasibility_plan.md`
- Script: `scripts/smoke_phase46_full_dataloader.py`
- Findings: `docs/phase46_dataloader_smoke_downsample_tiling_feasibility_findings.md`
- Outputs: `analysis/phase46_dataloader_smoke_downsample_tiling/`
- Key output files:
  - `dataloader_smoke_summary.json`
  - `dataloader_smoke_summary.md`
  - `sample_shape_checks.csv`
  - `downsample_feasibility_checks.csv`
  - `tile_feasibility_checks.csv`
  - `batch_smoke_checks.csv`
  - `memory_safety_notes.md`
- Status: no-training dataloader smoke test complete
- Decision: `dataloader_smoke_ready_for_downsample_baseline`
- Summary: `scenario_index_loaded = true`; `static_index_loaded = true`; `representative_samples_count = 11`; `sample_shape_checks_passed = true`; `downsample_128_passed = true`; `downsample_256_passed = true`; `tile_checks_passed = true`; `batch_smoke_passed = true`; `memory_safe = true`; `training_authorized = false`; `level4_plus_supported = true`; `level5_supported = false`
- Evidence: representative samples covered train/test, `location1`/`location2`/`location3`, design/measured scenarios, flood sequence lengths `360` and `480`, and rainfall lengths `180` and `360`; lazy/mmap reads, `128 x 128` downsampling, `256 x 256` downsampling, tile extraction, and tiny batch checks passed
- Next phase: Phase 47 controlled full dataset downsample baseline training plan, now completed by the Phase 47 baseline pilot
- Guardrails:
  - no training in Phase 46
  - no seed runs
  - no sweeps
  - no loss/config/model edits
  - no SWE residual implementation
  - no PINN implementation
  - no strict conservation / full mass conservation / hydrodynamic closure claims
  - no Level 5 support claim
  - Phase 47 training required a separate reviewed plan before execution
- Model status: dataloader smoke and feasibility checks only; no full flood sequences were materialized, no transformed training datasets were written, no model forward pass was run, and no model was trained

## Phase 47

- Plan: `docs/phase47_controlled_full_dataset_downsample_baseline_plan.md`
- Config: `configs/train_phase47_full_downsample128_seed42_10e.json`
- Script: `scripts/train_phase47_full_downsample_baseline.py`
- Findings: `docs/phase47_controlled_full_dataset_downsample_baseline_findings.md`
- Outputs: `analysis/phase47_controlled_downsample_baseline/`
- Key output files:
  - `metrics.csv`
  - `metrics.json`
  - `phase47_training_summary.json`
  - `phase47_training_summary.md`
  - `runtime_memory_notes.md`
  - `training_config_snapshot.json`
- Status: controlled `128 x 128` full-dataset `seed42` 10e baseline completed
- Decision: `phase47_controlled_128_downsample_seed42_pilot_completed`
- Summary: `seed = 42`; `resolution = 128`; `epochs = 10`; `train_samples = 960`; `test_samples = 384`; `best_test_rmse = 0.01109213042097205`; final `test_mae = 0.00525291082279485`; final `test_wet_dry_iou = 0.8255524213115374`; final `test_rollout_stability = 0.998722607580324`; final `test_step_rmse_std = 0.0012824604989987165`; `no_swe_pinn = true`; `level5_supported = false`
- Evidence: test RMSE improved from `0.0922387704437521` at epoch 1 to `0.01109213042097205` at epoch 10; test MAE improved from `0.029571487813276082` to `0.00525291082279485`; test wet/dry IoU improved from `0.2572032731241052` to `0.8255524213115374`
- Guardrails:
  - no Level 5 support claim
  - no SWE/PINN claim
  - no strict conservation / full mass conservation / hydrodynamic closure claims
  - no `seed123` / `seed202` expansion yet
  - no `256 x 256`, tile, multiscale, or full `500 x 500` training yet
  - no sweep
  - no new loss redesign
  - next work should be diagnostics or reviewed expansion planning
- Model status: Level 4+ full-dataset `128 x 128` baseline route is viable, but Phase 47 is not Level 5 evidence and does not authorize uncontrolled expansion

## Phase 48

- Plan: `docs/phase48_full_dataset_reliability_physical_proxy_diagnostics_plan.md`
- Script: `scripts/analyze_phase48_full_dataset_reliability.py`
- Findings: `docs/phase48_full_dataset_reliability_physical_proxy_diagnostics_findings.md`
- Outputs: `analysis/phase48_full_dataset_reliability_physical_proxy/`
- Key output files:
  - `phase48_diagnostic_readiness.json`
  - `scenario_reliability_metrics.csv`
  - `step_reliability_metrics.csv`
  - `wet_dry_error_metrics.csv`
  - `peak_depth_timing_metrics.csv`
  - `volume_response_proxy_metrics.csv`
  - `location_type_summary.csv`
  - `reliability_warning_levels.csv`
  - `phase48_reliability_summary.json`
  - `phase48_reliability_summary.md`
- Status: no-training full-dataset reliability and physical proxy diagnostics complete
- Decision: `phase48_diagnostics_ready_for_warning_framework_extension`
- Summary: `checkpoint_found = true`; `diagnostics_executed = true`; `evaluated_split = test`; `evaluated_scenarios = 48`; `evaluated_windows = 384`; `mean_rmse = 0.012037189189155709`; `mean_mae = 0.005252910632811514`; `mean_wet_dry_iou = 0.863043953275997`; `mean_false_dry_rate = 0.0911363765964386`; `mean_false_wet_rate = 0.003937674554837349`; `mean_absolute_relative_volume_bias_proxy = 0.021456503649973275`; `warning_level_counts = reliable 1, caution 12, high-risk 35`; `no_training = true`; `no_swe_pinn = true`; `level5_supported = false`
- Interpretation: warning labels are conservative diagnostic screening labels, not calibrated probabilities; the high-risk count should not be interpreted as poor overall model skill
- Follow-up: completed by Phase 49 full-dataset warning-framework extension
- Guardrails:
  - no training
  - no seed expansion
  - no sweeps
  - no `256 x 256`, tile, multiscale, or full-`500 x 500` expansion
  - no new loss redesign
  - no SWE residual implementation
  - no PINN implementation
  - no strict conservation / full mass conservation / hydrodynamic closure claims
  - no Level 5 support claim
- Model status: Phase 48 provided the diagnostic inputs for completed Phase 49 warning-framework extension; it does not authorize uncontrolled training expansion

## Phase 49

- Plan: `docs/phase49_full_dataset_warning_framework_extension_plan.md`
- Script: `scripts/build_phase49_warning_framework.py`
- Findings: `docs/phase49_full_dataset_warning_framework_extension_findings.md`
- Outputs: `analysis/phase49_full_dataset_warning_framework/`
- Key output files:
  - `warning_framework_summary.json`
  - `warning_framework_summary.md`
  - `scenario_warning_framework.csv`
  - `location_type_warning_summary.csv`
  - `warning_rule_table.csv`
  - `warning_message_templates.md`
  - `high_risk_case_review_list.csv`
  - `phase49_warning_framework_decision.json`
- Status: no-training full-dataset warning framework extension complete
- Decision: `phase49_warning_framework_completed_with_conservative_labels`
- Summary: `input_files_found = true`; `scenario_count = 48`; `warning_level_counts = reliable 1, caution 12, high-risk 35`; `high_risk_case_count = 35`; `no_training = true`; `warning_labels_are_probabilities = false`
- Action mapping: `reliable -> normal_use_with_standard_monitoring`; `caution -> use_with_caution_and_review_diagnostics`; `high-risk -> high_risk_requires_review_or_supplemental_evidence`
- Interpretation: Phase 49 converted Phase 48 diagnostic labels into scenario-level warning actions. Warning labels are conservative diagnostic screening labels, not calibrated probabilities, and the high-risk count reflects conservative screening sensitivity rather than poor overall model skill.
- Follow-up: completed by Phase 50 framework consolidation and paper-ready evidence synthesis
- Guardrails:
  - no training
  - no seed expansion
  - no sweeps
  - no `256 x 256`, tile, multiscale, or full-`500 x 500` expansion
  - no new loss redesign
  - no model/loss/config edits
  - no SWE residual implementation
  - no PINN implementation
  - no strict conservation / full mass conservation / hydrodynamic closure claims
  - no Level 5 support claim
  - no calibrated probability claim
- Model status: Phase 49 supports conservative case reporting and diagnostic screening only; it does not authorize uncontrolled training expansion, production readiness claims, SWE/PINN claims, or Level 5 support claims.

## Phase 50

- Plan: `docs/phase50_framework_consolidation_paper_ready_evidence_synthesis_plan.md`
- Script: `scripts/synthesize_phase50_full_dataset_evidence.py`
- Figure-support script: `scripts/plot_phase50_framework_summary_figures.py`
- Findings: `docs/phase50_framework_consolidation_paper_ready_evidence_synthesis_findings.md`
- Outputs: `analysis/phase50_framework_consolidation/`
- Figures directory: `analysis/phase50_framework_consolidation/figures/`
- Key output files:
  - `phase50_evidence_chain_table.csv`
  - `phase50_key_metrics_summary.csv`
  - `phase50_claim_boundary_table.csv`
  - `phase50_recommended_next_steps.csv`
  - `phase50_framework_synthesis.json`
  - `phase50_framework_synthesis.md`
  - `phase50_paper_ready_contribution_outline.md`
- Key figure files:
  - `phase50_evidence_chain_overview.png`
  - `phase50_key_metrics_summary.png`
  - `phase50_warning_level_counts.png`
  - `phase50_claim_boundary_matrix.png`
  - `phase50_reviewed_next_steps_matrix.png`
  - `phase50_figure_summary.md`
- Status: no-training framework consolidation and paper-ready full-dataset evidence synthesis complete
- Decision: `phase50_framework_synthesis_ready_for_paper_outline`
- Summary: `phases_synthesized = 43-49`; `level4_plus_route_supported = true`; `level5_supported = false`; `no_training = true`; `no_swe_pinn = true`; `warning_labels_are_probabilities = false`
- Evidence chain: dataset inspection -> full dataset indexing -> dataloader feasibility -> controlled `128 x 128` baseline -> reliability diagnostics -> warning framework -> evidence synthesis
- Interpretation: Phase 50 consolidates the UrbanFlood24 full-dataset Level 4+ route for paper-outline use. It does not establish Level 5, SWE/PINN, strict conservation, full mass conservation, hydrodynamic closure, calibrated probabilities, final production readiness, or uncontrolled training expansion.
- Next phase: Phase 51 reviewed expansion decision
- Guardrails:
  - no training
  - no new seeds
  - no sweeps
  - no `256 x 256`, tile, multiscale, or full-`500 x 500` expansion
  - no new loss redesign
  - no model/loss/config edits
  - no SWE residual implementation
  - no PINN implementation
  - no strict conservation / full mass conservation / hydrodynamic closure claims
  - no Level 5 support claim
  - no calibrated probability claim
  - no final production-readiness claim
  - no uncontrolled training expansion
- Model status: Phase 50 supports paper-ready Level 4+ evidence synthesis and a reviewed Phase 51 expansion decision only.

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
19. `docs/phase24_physical_consistency_deepening_findings.md`
20. `docs/phase25_three_seed_target_wet_recall_synthesis_findings.md`
21. `docs/phase26_strong_physics_constraint_feasibility_findings.md`
22. `docs/phase27_seed42_volume_response_pilot_findings.md`
23. `docs/phase28_volume_response_loss_diagnosis_findings.md`
24. `docs/phase29_seed42_tolerance_band_volume_findings.md`
25. `docs/phase30_strong_physics_boundary_synthesis.md`
26. `docs/phase31_physics_input_recovery_readiness_findings.md`
27. `docs/phase32_domain_boundary_aware_physical_consistency_findings.md`
28. `docs/phase33_seed42_pilot_readiness_review_findings.md`
29. `docs/phase34_pilot_threshold_formalization_findings.md`
30. `docs/phase35_manhole_false_dry_guardrail_pilot_plan.md`
31. `docs/phase36_manhole_false_dry_guardrail_code_smoke_findings.md`
32. `docs/phase37_seed42_training_authorization_review_findings.md`
33. `docs/phase38_seed42_pilot_training_guardrail_evaluation_findings.md`
34. `docs/phase39_failed_pilot_tradeoff_diagnosis_findings.md`
35. `docs/phase40_failed_pilot_design_review_next_constraint_findings.md`
36. `docs/phase41_swe_data_readiness_audit_findings.md`
37. `docs/phase42_hydrodynamic_export_requirement_specification_findings.md`
38. `docs/phase43_urbanflood24_full_dataset_inspection_findings.md`
39. `docs/phase44_urbanflood24_full_level4plus_replanning.md`
40. `docs/phase45_full_dataset_indexing_lightweight_adapter_findings.md`
41. `docs/phase46_dataloader_smoke_downsample_tiling_feasibility_findings.md`
42. `docs/phase47_controlled_full_dataset_downsample_baseline_findings.md`
43. `docs/phase48_full_dataset_reliability_physical_proxy_diagnostics_findings.md`
44. `docs/phase49_full_dataset_warning_framework_extension_findings.md`
45. `docs/phase50_framework_consolidation_paper_ready_evidence_synthesis_findings.md`
46. `docs/project_status.md`

## Next Stage

The next stage should build on the Phase 12 to Phase 50 reliability/applicability, screening, warning-rule, synthesis, manuscript-writing, manuscript-consolidation, manuscript-draft, evidence-alignment, full-draft expansion, warning case-study prototype, physical-consistency diagnostic, target-wet recall refinement, strong-physics feasibility audit, mixed conservative volume-response pilot, volume-response failure diagnosis, mixed tolerance-band pilot, strong-physics boundary synthesis, physics input recovery readiness, domain-/boundary-aware design guardrail, seed42 pilot-readiness, pilot-threshold formalization, manhole false-dry guardrail pilot-planning, code/smoke-test implementation, seed42 training authorization review, rejected Phase 38 seed42 pilot, Phase 39 failed-pilot diagnosis, Phase 40 next-constraint decision, Phase 41 SWE data readiness audit, Phase 42 hydrodynamic export requirement specification, Phase 43 UrbanFlood24 full dataset inspection, Phase 44 UrbanFlood24 full Level 4+ replanning, Phase 45 full dataset indexing, Phase 46 dataloader smoke/downsample/tiling feasibility, Phase 47 controlled full-dataset `128 x 128` baseline materials, Phase 48 full-dataset reliability and physical proxy diagnostics, Phase 49 warning framework extension, and Phase 50 paper-ready evidence synthesis rather than reopening Phase 10 tuning, expanding seeds, starting a sweep, further proxy-loss redesign, implementing SWE residuals, implementing PINN components, or rescuing the rejected pilot post hoc.

Recommended next work:

- analyze the remaining Phase 25 limitations, especially slight false-wet increase and non-uniform connectivity behavior
- treat Phase 25 as a targeted target-wet recall and wet-region preservation refinement, not a complete hydrodynamic consistency solution
- treat Phase 27 as a mixed seed42 pilot whose direct expansion should stop
- use Phase 28 as the diagnostic basis that motivated Phase 29, not as support for direct expansion of the Phase 27 loss
- treat Phase 29 as partial volume-response repair with unacceptable trade-offs, not as tolerance-band success
- treat Phase 30 as the current Level 4 conservation-proxy / physical-consistency-guided surrogate boundary, not as Level 5 strong physics
- treat Phase 31 as Level 4+ physics input recovery and masked diagnostic readiness, not as Level 5 strong physics
- treat Phase 32 as design/diagnostic-only Level 4+ domain-/boundary-aware physical consistency guardrails, not as model improvement
- keep the Phase 32 decision as `design_ready_no_training_yet`
- treat Phase 33 as diagnostic/readiness-review only, not as pilot success or training authorization
- keep the Phase 33 decision as `pilot_design_ready_but_training_not_started` and `training_authorized = false`
- treat Phase 34 as threshold-formalization only, not as pilot success or training authorization
- keep the Phase 34 decision as `thresholds_formalized_training_still_blocked` and `training_authorized = false`
- treat Phase 35 as pilot implementation planning only, not as loss implementation, config creation, model-code modification, or training authorization
- keep the Phase 35 status as `implementation_plan_ready_code_next` and `training_authorized = false`
- treat Phase 36 as code/smoke-test implementation only, not as pilot success or training authorization
- keep the Phase 36 decision as `code_smoke_ready_training_still_blocked`, with `training_authorized = false` and `training_executed = false`
- treat Phase 37 as diagnostic authorization review only, not as pilot success or a training result
- keep the Phase 37 decision as `seed42_training_authorized_next_phase`, with `training_authorized_next_phase = true`, `training_executed = false`, and required checks passed `18 / 18`
- treat Phase 38 as completed seed42 pilot training, completed test evaluation, completed guardrail evaluation, and a rejected pilot
- keep the Phase 38 decision as `seed42_pilot_rejected`
- treat Phase 38 as useful negative evidence, not a training execution failure
- treat Phase 39 as diagnostic-only failed-pilot trade-off analysis, with decision `tradeoff_diagnosis_completed_with_missing_optional_inputs`
- treat the Phase 38 negative result as diagnosed: narrow target-proxy improvement did not preserve broader Level 4+ guardrails
- treat Phase 40 as failed-pilot design review and next-constraint decision, with decision `pause_loss_redesign_move_to_swe_data_readiness`
- pause proxy-loss redesign after repeated trade-off evidence from Phase 27, Phase 29, and Phase 38
- treat Phase 41 as a completed no-training SWE data readiness audit, with decision `readiness_uncertain_requires_external_data_export`
- keep `level5_supported = false`, `external_hydrodynamic_model_export_needed = true`, and `level4_proxy_supported = true`
- treat Phase 42 as a completed no-training hydrodynamic export requirement specification, with decision `export_contract_ready_for_dataset_inspection` and `training_authorized = false`
- use Phase 42 counts conservatively: `required_fields_count = 16`, `minimum_contract_items = 10`, `urbanflood24_checklist_items = 10`, and `icm_mike_checklist_items = 13`
- treat Phase 43 as a completed no-training UrbanFlood24 full dataset inspection, with decision `full_dataset_readiness_uncertain_needs_metadata`, `level5_supported = false`, `level4_plus_supported = true`, and `training_authorized = false`
- use Phase 43 counts conservatively: `total_files = 354`, `total_dirs = 186`, and `sampled_arrays_count = 54`
- treat Phase 44 as completed no-training UrbanFlood24 full Level 4+ replanning, not as training, SWE/PINN implementation, strict conservation, full mass conservation, hydrodynamic closure, or Level 5 support
- freeze short-term Level 5/SWE/PINN claims and proceed with the UrbanFlood24 full Level 4+ route
- treat Phase 45 as completed no-training full dataset indexing and lightweight adapter preparation, with decision `indexing_ready_for_dataloader_smoke`
- use Phase 45 counts conservatively: `scenario_count_total = 168`, train scenarios = 120, test scenarios = 48, `static_index_rows = 6`, `warning_count = 0`, `level4_plus_supported = true`, and `level5_supported = false`
- treat Phase 46 as completed no-training dataloader smoke and downsample/tiling feasibility, with decision `dataloader_smoke_ready_for_downsample_baseline`
- use Phase 46 evidence conservatively: `representative_samples_count = 11`, lazy/mmap reads passed, `downsample_128_passed = true`, `downsample_256_passed = true`, `tile_checks_passed = true`, `batch_smoke_passed = true`, and `memory_safe = true`
- treat Phase 47 as completed controlled full-dataset `128 x 128` downsample `seed42` 10e baseline training, with decision `phase47_controlled_128_downsample_seed42_pilot_completed`
- use Phase 47 metrics conservatively: `train_samples = 960`, `test_samples = 384`, `best_test_rmse = 0.01109213042097205`, `test_mae = 0.00525291082279485`, `test_wet_dry_iou = 0.8255524213115374`, `test_rollout_stability = 0.998722607580324`, and `test_step_rmse_std = 0.0012824604989987165`
- treat Phase 47 as a viable Level 4+ full-dataset `128 x 128` baseline route, not as Level 5 support
- treat Phase 48 as completed no-training full-dataset reliability and physical proxy diagnostics, with decision `phase48_diagnostics_ready_for_warning_framework_extension`
- use Phase 48 metrics conservatively: `evaluated_scenarios = 48`, `evaluated_windows = 384`, `mean_rmse = 0.012037189189155709`, `mean_mae = 0.005252910632811514`, `mean_wet_dry_iou = 0.863043953275997`, `mean_false_dry_rate = 0.0911363765964386`, `mean_false_wet_rate = 0.003937674554837349`, and `mean_absolute_relative_volume_bias_proxy = 0.021456503649973275`
- treat Phase 48 warning labels as conservative diagnostic screening labels, not calibrated probabilities; the reliable 1, caution 12, high-risk 35 split is not proof of poor overall model skill
- treat Phase 49 as completed no-training full-dataset warning framework extension, with decision `phase49_warning_framework_completed_with_conservative_labels`, `scenario_count = 48`, `warning_level_counts = reliable 1, caution 12, high-risk 35`, `high_risk_case_count = 35`, `no_training = true`, and `warning_labels_are_probabilities = false`
- treat Phase 49 warning actions as conservative diagnostic screening actions, not calibrated probabilities; use `reliable -> normal_use_with_standard_monitoring`, `caution -> use_with_caution_and_review_diagnostics`, and `high-risk -> high_risk_requires_review_or_supplemental_evidence`
- treat Phase 50 as completed no-training framework consolidation and paper-ready full-dataset evidence synthesis, with decision `phase50_framework_synthesis_ready_for_paper_outline`, `phases_synthesized = 43-49`, `level4_plus_route_supported = true`, `level5_supported = false`, `no_training = true`, `no_swe_pinn = true`, and `warning_labels_are_probabilities = false`
- treat the Phase 50 evidence chain as paper-ready Level 4+ support only: dataset inspection -> full dataset indexing -> dataloader feasibility -> controlled `128 x 128` baseline -> reliability diagnostics -> warning framework -> evidence synthesis
- do not claim SWE/PINN support, strict conservation, full mass conservation, or hydrodynamic closure from Phase 47, Phase 48, Phase 49, or Phase 50
- do not expand to `seed123` / `seed202`, `256 x 256`, tile, multiscale, full `500 x 500`, sweeps, or new loss redesign without a reviewed expansion-decision phase
- make the next step Phase 51 reviewed expansion decision, not immediate training expansion
- do not run Phase 29 `seed123` / `seed202` confirmation or a tolerance/weight sweep
- do not run Phase 27 or Phase 29 `seed123` / `seed202` confirmation
- do not run Phase 38 `seed123` / `seed202` expansion, any sweep, Phase 29 continuation, or post-hoc loss/config rescue
- do not implement SWE residuals, PINN losses, strict conservation, full mass conservation, hydrodynamic closure, or Level 5 support unless compatible velocity/flux fields, `dx/dy`, `dt`, boundary conditions, pump/gate operations, complete source/sink terms, and complete hydrodynamic state variables are recovered and aligned
- consider calibrated uncertainty only if calibration data and evaluation design are added
- keep the current Phase 10 setting fixed unless new evidence justifies changing it
- avoid broader boundary-weight sweeps
- maintain the Phase 15 screening layer and Phase 16 warning-rule layer as deterministic operational support unless a new calibration design is added
