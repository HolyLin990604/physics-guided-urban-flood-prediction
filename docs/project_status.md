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
- Phase 16 completed the first implementation of reliability-aware warning rules and applicability boundary guidance.
- Phase 17 completed the reliability-aware warning framework synthesis across Phase 12 through Phase 16.
- Phase 18 completed the manuscript-oriented reliability-aware warning layer writing phase, with the first manuscript note completed.
- Phase 19 completed manuscript-structure and submission consolidation, with a paper-ready manuscript outline and submission-oriented planning document created.
- Phase 20 completed manuscript draft assembly, with the first full manuscript draft skeleton created.
- Phase 21 completed manuscript evidence and figure/table alignment, with a claim-to-evidence alignment document created.

The current Phase 10 conclusion is that boundary-band weighted wet/dry consistency refinement has passed test-facing confirmation on the three key project seeds: `seed123`, `seed42`, and `seed202`.

The current recommended model setting remains the Phase 10 setting:

- `boundary_band_pixels = 1`
- `boundary_weight = 2.0`

The current Phase 12 conclusion is that the Phase 10 recommended model is broadly useful for rapid spatiotemporal flood-process approximation under the tested scenario set, but its reliability is not uniform across all pixels, depth ranges, and scenarios. The main caution zones are exact wet/dry boundary cells, shallow threshold-adjacent cells, moderate-to-deep inundation depths, high-intensity `location2` scenarios, and local peak-depth extremes.

The current Phase 13 conclusion is that the highest-ranked failures are not random scattered cases. They collapse into two high-intensity `location2` target scenarios repeated across seeds: `location2 / r300y_p0.6_d3h / start_idx = 0` at worst step 1, and `location2 / r300y_p0.8_d3h / start_idx = 0` at worst step 4. The visual summaries show systematic underprediction, reduced predicted wet fraction, local peak-depth underprediction, and false-dry dominated wet/dry mismatch.

The current Phase 14 conclusion is that output-space confidence proxies are useful but limited. Confidence margin is useful for wet/dry classification risk because low-margin bins show much higher wet/dry error and false-dry rate. Cross-seed disagreement has only weak global correlation with scenario RMSE, so it should be treated as an auxiliary disagreement proxy rather than a strong standalone scenario-error predictor. Phase 14 is not calibrated probabilistic uncertainty.

The current Phase 15 conclusion is that the Phase 12/13/14 diagnostic evidence has been converted into a functional deterministic screening layer. The first implementation loaded 57 Phase 10 map files, generated 114 scenario-level risk records and 16,384 pixel-level risk records, and assigned 76 scenario records to `reliable`, 25 to `caution`, and 13 to `high-risk`. As a validation check, all 24 known Phase 13-like `location2` + `r300y` cases were flagged as `caution` or `high-risk`.

Phase 15 screening labels are deterministic risk-screening labels. They are not calibrated probabilities, Bayesian uncertainty estimates, or a substitute for a formal calibration design.

The current Phase 16 conclusion is that the Phase 15 deterministic reliability-screening labels have been converted into application-oriented warning guidance and an applicability boundary summary. Scenario warning counts are 76 `reliable`, 25 `caution`, and 13 `high-risk`. Pixel warning counts are 5,714 `reliable`, 8,805 `caution`, and 1,865 `high-risk`. The 13 high-risk warning cases match the Phase 15 high-risk cases.

Phase 16 warning labels are deterministic operational interpretation labels. They are not calibrated probabilities, Bayesian uncertainty estimates, formal confidence intervals, or a substitute for a formal calibration design.

The current Phase 17 conclusion is that Phase 12 through Phase 16 now form a coherent reliability-aware warning framework narrative: Phase 12 diagnoses reliability and applicability boundaries, Phase 13 visualizes representative repeated failure modes, Phase 14 evaluates confidence and disagreement proxies, Phase 15 converts the evidence into deterministic reliability screening and spatial risk mapping, and Phase 16 translates those labels into warning-rule and applicability-boundary guidance.

Phase 17 is a synthesis/documentation phase rather than a new experiment. It is intended to support manuscript writing, README narrative, and project positioning. It should not be read as calibrated uncertainty or universal generalization beyond the tested evidence.

The current Phase 19 conclusion is that the completed Phase 12 through Phase 18 reliability-aware warning framework and manuscript notes have been consolidated into a paper-ready manuscript structure and submission-oriented plan. The document covers paper positioning, candidate titles, abstract logic, methods/results/discussion structure, figure and table inventory, contribution statements, limitations, submission positioning, and immediate writing tasks.

The current Phase 20 conclusion is that the Phase 18 and Phase 19 manuscript-oriented materials have been assembled into the first full manuscript draft skeleton: `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`. Phase 20 is manuscript draft assembly, not a new experiment phase.

The current Phase 21 conclusion is that manuscript claims have been aligned with existing evidence sources, figures, tables, JSON/CSV outputs, and findings documents before full manuscript expansion. The claim-to-evidence and figure/table alignment document has been created: `docs/manuscript_evidence_figure_table_alignment.md`. Phase 21 is evidence alignment and figure/table planning, not a new experiment phase.

The current project position after Phase 21 is rapid flood prediction with reliability diagnosis, failure-mode interpretation, confidence proxy diagnostics, spatial risk mapping, deterministic warning-rule guidance, manuscript-ready warning-layer synthesis, paper-ready manuscript/submission consolidation, a first full manuscript draft skeleton, and claim-to-evidence/figure-table alignment. Calibration should only be introduced through a separate calibration design, and the current Phase 10 setting remains fixed unless new evidence justifies changing it.

No retraining, architecture modification, Phase 10 loss modification, `boundary_band_pixels` tuning, `boundary_weight` tuning, additional Phase 10 boundary-weight sweep, new sweep, new result generation, or new uncertainty claim was performed. The current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`.

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

### Reliability-aware warning rules and applicability boundary

Phase 16 converted the Phase 15 deterministic scenario and pixel screening labels into warning-rule guidance and an applicability boundary summary for application-facing interpretation.

Generated Phase 16 outputs include:

- `docs/phase16_reliability_warning_applicability_plan.md`
- `scripts/build_phase16_warning_rules.py`
- `analysis/phase16_warning_rules/summary.json`
- `analysis/phase16_warning_rules/warning_rules.json`
- `analysis/phase16_warning_rules/scenario_warning_summary.csv`
- `analysis/phase16_warning_rules/applicability_boundary_table.csv`
- `analysis/phase16_warning_rules/high_risk_warning_cases.csv`
- `analysis/phase16_warning_rules/pixel_warning_summary.csv`
- `analysis/phase16_warning_rules/figures/`
- `docs/phase16_reliability_warning_applicability_findings.md`

The first-pass Phase 16 findings indicate:

- scenario warnings produced 76 `reliable`, 25 `caution`, and 13 `high-risk` records
- pixel warnings produced 5,714 `reliable`, 8,805 `caution`, and 1,865 `high-risk` records
- the 13 high-risk warning cases match the Phase 15 high-risk cases
- Phase 16 turns rapid prediction, reliability screening, and spatial risk mapping into application-oriented warning-rule guidance
- warning labels are deterministic operational interpretation labels, not calibrated probabilities, Bayesian uncertainty, or formal confidence intervals
- no retraining, tuning, architecture change, Phase 10 loss change, or new sweep was performed

### Reliability-aware warning framework synthesis

Phase 17 synthesizes Phase 12 through Phase 16 into a coherent reliability-aware flood-warning framework narrative.

Generated Phase 17 output:

- `docs/phase17_reliability_warning_framework_synthesis.md`

The Phase 17 synthesis indicates:

- the project has evolved from rapid flood-depth prediction to rapid prediction plus reliability diagnosis, failure-mode interpretation, confidence proxy diagnostics, spatial risk mapping, and warning-rule guidance
- Phase 17 does not introduce a new experiment, retrain models, modify architecture, modify the Phase 10 loss, tune `boundary_weight` or `boundary_band_pixels`, or open a new sweep
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`
- the synthesis supports manuscript writing, README narrative, and project positioning
- the framework remains deterministic and evidence-based; it does not claim calibrated uncertainty or universal generalization

### Manuscript-oriented reliability-aware warning layer

Phase 18 converts the completed Phase 12 through Phase 17 reliability-aware warning framework into manuscript-ready writing material for a section titled "Reliability-Aware Warning Layer for Urban Flood Surrogate Prediction."

Generated Phase 18 writing deliverables:

- `docs/phase18_manuscript_reliability_warning_layer_plan.md`
- `docs/manuscript_reliability_aware_warning_layer.md`

The Phase 18 writing phase indicates:

- the manuscript reliability-aware warning layer note has been created
- Phase 18 is manuscript-oriented synthesis/writing, not a new experiment
- no retraining, architecture modification, Phase 10 loss modification, `boundary_weight` tuning, `boundary_band_pixels` tuning, new sweep, or new result generation was performed
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`

### Manuscript structure and paper-ready consolidation

Phase 19 converts the completed reliability-aware warning framework and Phase 18 manuscript note into a paper-ready manuscript outline and submission-oriented planning document.

Generated Phase 19 deliverables:

- `docs/phase19_manuscript_structure_consolidation_plan.md`
- `docs/manuscript_structure_and_submission_consolidation.md`

The Phase 19 consolidation indicates:

- the manuscript structure and submission consolidation document has been created
- Phase 19 is manuscript-structure and submission consolidation, not a new experiment
- the document covers paper positioning, candidate titles, abstract logic, methods/results/discussion structure, figure/table inventory, contribution statements, limitations, submission positioning, and immediate writing tasks
- no retraining, architecture modification, Phase 10 loss modification, `boundary_weight` tuning, `boundary_band_pixels` tuning, new sweep, or new result generation was performed
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`

### Manuscript draft assembly

Phase 20 assembles the Phase 18 manuscript warning-layer note and the Phase 19 manuscript-structure consolidation into the first full manuscript draft skeleton.

Generated Phase 20 deliverables:

- `docs/phase20_manuscript_draft_assembly_plan.md`
- `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`

The Phase 20 assembly indicates:

- the first full manuscript draft skeleton has been created
- Phase 20 is manuscript draft assembly, not a new experiment phase
- no retraining, architecture modification, Phase 10 loss modification, `boundary_weight` tuning, `boundary_band_pixels` tuning, new sweep, or new result generation was performed
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`

### Manuscript evidence and figure/table alignment

Phase 21 aligns manuscript claims with existing evidence sources, figures, tables, JSON/CSV outputs, and findings documents before full manuscript expansion.

Generated Phase 21 deliverables:

- `docs/phase21_manuscript_evidence_figure_alignment_plan.md`
- `docs/manuscript_evidence_figure_table_alignment.md`

The Phase 21 alignment indicates:

- the claim-to-evidence and figure/table alignment document has been created
- Phase 21 is evidence alignment and figure/table planning, not a new experiment phase
- no retraining, architecture modification, Phase 10 loss modification, `boundary_weight` tuning, `boundary_band_pixels` tuning, new sweep, new result generation, or new uncertainty claim was performed
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`

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
- read Phase 16 as the first implementation of deterministic warning-rule guidance and applicability boundary interpretation
- read Phase 17 as the synthesis of Phase 12-16 into a reliability-aware warning framework narrative
- read Phase 18 as manuscript-oriented writing material derived from the Phase 12-17 reliability-aware warning framework
- read Phase 19 as manuscript-structure and submission consolidation derived from the completed Phase 12-18 materials
- read Phase 20 as the first full manuscript draft skeleton assembled from the Phase 18-19 manuscript-oriented materials
- read Phase 21 as claim-to-evidence and figure/table alignment for manuscript expansion, not as a new experiment

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
- `docs/phase16_reliability_warning_applicability_plan.md`
- `docs/phase16_reliability_warning_applicability_findings.md`
- `docs/phase17_reliability_warning_framework_synthesis.md`
- `docs/phase18_manuscript_reliability_warning_layer_plan.md`
- `docs/manuscript_reliability_aware_warning_layer.md`
- `docs/phase19_manuscript_structure_consolidation_plan.md`
- `docs/manuscript_structure_and_submission_consolidation.md`
- `docs/phase20_manuscript_draft_assembly_plan.md`
- `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`
- `docs/phase21_manuscript_evidence_figure_alignment_plan.md`
- `docs/manuscript_evidence_figure_table_alignment.md`
- `docs/experiment_index.md`
