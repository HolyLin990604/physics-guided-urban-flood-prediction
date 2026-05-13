# Manuscript Structure and Submission Consolidation

## 1. Manuscript positioning

The manuscript should be positioned as a reliability-aware deep learning surrogate framework for rapid urban flood warning.

The paper should not be framed only as a fast flood prediction model. The stronger framing is rapid flood-depth prediction plus reliability diagnosis, failure-mode interpretation, confidence proxy diagnostics, spatial risk mapping, and warning-rule guidance. This positions the trained surrogate as part of a warning-oriented decision-support framework rather than only a computational shortcut.

The central message is that rapid surrogate prediction is useful for urban flood warning only when paired with explicit information about where the prediction is reliable, where caution is needed, and where the output should not be used alone.

## 2. Candidate titles

- Reliability-Aware Deep Learning Surrogate Modeling for Rapid Urban Flood Warning
- From Rapid Flood Prediction to Reliability-Aware Warning: A Deep Learning Surrogate Framework
- A Reliability-Aware Urban Flood Surrogate Framework with Spatial Risk Mapping and Warning Guidance
- Reliability Diagnosis and Warning Guidance for Deep Learning Surrogate Urban Flood Prediction
- Rapid Urban Flood Prediction with Deterministic Reliability Screening and Applicability Mapping
- A Physics-Guided Urban Flood Surrogate with Reliability-Aware Warning Support
- Deep Learning Surrogate Modeling for Urban Flood Warning with Reliability Screening and Spatial Risk Mapping
- Reliability-Aware Interpretation of Rapid Urban Flood Surrogate Predictions

## 3. Core abstract logic

This should be an abstract skeleton rather than a final abstract.

1. Background problem: urban flood warning requires rapid spatial flood-depth information, but physics-based hydrodynamic simulation can be too computationally expensive for repeated or near-real-time use.
2. Limitation of prediction-only surrogates: deep learning surrogates can accelerate prediction, but aggregate accuracy alone does not show when and where predictions are reliable enough for warning interpretation.
3. Proposed framework: this study develops a reliability-aware surrogate framework that combines rapid flood-depth prediction with reliability diagnosis, failure-mode interpretation, confidence proxy diagnostics, spatial risk mapping, and warning-rule guidance.
4. Data/model basis: the framework is built on an UrbanFlood24 Lite multi-step flood prediction task using a U-Net + TCN surrogate with physically informed prediction refinements.
5. Reliability-aware warning layer: diagnostic evidence from depth ranges, wet/dry boundary zones, high-intensity scenarios, representative failure cases, confidence margins, and screening rules is converted into deterministic scenario-level and pixel-level labels.
6. Key results: the Phase 10 recommended setting is retained, Phase 12-16 evidence identifies nonuniform reliability, and Phase 15-16 screening produces reliable, caution, and high-risk labels at scenario and pixel levels.
7. Contribution and implication: the contribution is a practical warning-oriented interpretation layer around a rapid surrogate, supporting more transparent use while avoiding claims of calibrated uncertainty or replacement of hydrodynamic modeling.

## 4. Proposed manuscript structure

### 1. Introduction

Motivate rapid urban flood prediction for warning support. Explain the computational burden of hydrodynamic models, the promise of deep learning surrogates, and the limitation of prediction-only framing. Introduce reliability-aware interpretation as necessary for operational warning use.

### 2. Study Area and Dataset

Describe the urban flood prediction context, study area, UrbanFlood24 Lite dataset, scenario design, static geospatial inputs, rainfall and flood-depth sequences, input-output structure, and train/test logic needed for reproducibility.

### 3. Hydrodynamic Simulation and Surrogate Model

Summarize the hydrodynamic reference data and the surrogate prediction task. Explain that the surrogate predicts future flood-depth fields from past flood states, rainfall forcing, and static maps. Distinguish hydrodynamic simulation from surrogate inference.

### 4. Physics-Guided Prediction Framework

Describe the U-Net + TCN prediction framework, physics-guided or physically informed output refinements, and the current Phase 10 recommended setting with `boundary_band_pixels = 1` and `boundary_weight = 2.0`. Present the setting as fixed evidence, not a reopened tuning problem.

### 5. Reliability-Aware Warning Layer

Synthesize Phases 12 through 16 as a framework layer around the fixed surrogate. Include reliability/applicability diagnosis, failure-case interpretation, confidence margin as a wet/dry classification risk proxy, deterministic screening, spatial risk mapping, warning rules, and applicability-boundary interpretation.

### 6. Results

Report base prediction performance and then organize reliability-aware evidence: Phase 12 reliability diagnosis, Phase 13 representative failures, Phase 14 confidence proxy diagnostics, Phase 15 risk screening and mapping, and Phase 16 warning-rule outputs.

### 7. Discussion

Discuss why accuracy alone is insufficient, how reliability boundaries affect warning use, and how deterministic labels should be interpreted. Address false-dry risk, boundary-zone caution, peak-depth underprediction, non-probabilistic warning labels, and limits to generalization.

### 8. Conclusions

Summarize the framework as rapid urban flood surrogate prediction with reliability-aware warning support. Restate practical implications, conservative non-claims, and future needs such as broader validation and calibrated uncertainty only under a separate design.

## 5. Introduction storyline

The introduction should follow this logic:

1. Urban flooding requires rapid spatial prediction to support warning, emergency response, and situational awareness.
2. Hydrodynamic models provide physically credible flood simulations, but their computational cost can limit rapid repeated use.
3. Deep learning surrogates can approximate flood-depth fields much faster, but many surrogate studies emphasize prediction accuracy without enough attention to reliability boundaries.
4. Operational warning requires knowing not only what the model predicts, but also when the prediction is reliable, when it is sensitive, and when additional review is required.
5. Reliability, applicability boundaries, failure-mode interpretation, and warning guidance are therefore necessary for responsible use of rapid surrogate outputs.
6. This study proposes a reliability-aware surrogate framework that integrates rapid prediction with deterministic screening, spatial risk mapping, and warning-rule interpretation.

## 6. Methods structure

The methods should be organized as follows:

- Hydrodynamic simulation and data generation: describe the reference simulation basis, study domain, scenario construction, rainfall/flood-depth sequences, and static spatial inputs.
- U-Net + TCN surrogate model: describe the spatiotemporal input-output design, encoder-decoder structure, temporal conditioning, prediction horizon, and inference role.
- Physics-guided or physically informed refinement: describe the output-space physical constraints and margin-aware wet/dry refinement without reopening architecture or loss tuning.
- Phase 10 recommended setting: preserve the current recommended setting, `boundary_band_pixels = 1` and `boundary_weight = 2.0`, as the fixed model basis used by the reliability phases.
- Reliability-aware warning layer: define the Phase 12-16 logic chain from diagnosis to failure interpretation, proxy diagnostics, deterministic screening, risk mapping, warning rules, and applicability boundary.
- Deterministic screening and warning rules: explain reliable, caution, and high-risk labels as operational interpretation categories, not calibrated probabilities.

## 7. Results structure

The results should be organized in a progression from prediction to warning interpretation:

- Base prediction performance: report standard prediction metrics and representative predicted versus reference flood-depth outputs using the official evaluation outputs where appropriate.
- Phase 12 reliability/applicability diagnosis: present nonuniform reliability by timestep, depth bin, wet/dry boundary distance, scenario type, and seed.
- Phase 13 representative failure-case analysis: show that the strongest failures are systematic, especially repeated high-intensity `location2+r300y` cases with underprediction, wet-area contraction, peak-depth underprediction, and false-dry mismatch.
- Phase 14 confidence proxy diagnostics: show that confidence margin supports wet/dry classification risk screening, while cross-seed disagreement is only auxiliary.
- Phase 15 reliability screening and risk mapping: present scenario-level reliable/caution/high-risk labels, risk components, consistency with Phase 13-like cases, and pixel-level risk maps.
- Phase 16 warning-rule and applicability-boundary guidance: present warning-level counts, the warning action matrix, pixel warning maps, and applicability-boundary categories.

## 8. Discussion structure

The discussion should address:

- why prediction accuracy alone is insufficient for warning-oriented surrogate use;
- how physical plausibility and applicability boundaries affect operational interpretation;
- why false-dry errors and wet/dry boundary zones require explicit caution;
- how local peak-depth underprediction and high-intensity `location2+r300y` cases define high-risk use conditions;
- why deterministic reliable/caution/high-risk labels are useful operationally but should not be interpreted as probabilistic uncertainty;
- how reliable, caution, and high-risk categories can guide ordinary use, targeted review, and non-standalone use;
- limitations in scenario coverage, external generalization, calibrated uncertainty, and high-stakes decision use;
- future work on broader validation, calibration design, operational coupling, and targeted improvement for identified failure modes.

## 9. Figure and table inventory

| Proposed figure/table ID | Source phase | Candidate file or output | Manuscript purpose | Recommended placement |
|---|---|---|---|---|
| Figure 1 | Data/model overview | README method diagram or manuscript schematic | Show the hydrodynamic-to-surrogate prediction workflow and input-output structure | Methods: Study Area and Dataset or Hydrodynamic Simulation and Surrogate Model |
| Figure 2 | Model framework | README method diagram; Phase 10 configuration summary | Show U-Net + TCN plus physics-guided prediction components | Methods: Physics-Guided Prediction Framework |
| Figure 3 | Prediction performance | Official evaluation outputs and representative flood-depth maps | Establish base surrogate prediction performance before reliability interpretation | Results: Base prediction performance |
| Figure 4 | Phase 12 | `analysis/phase12_reliability/figures/boundary_distance_class_error.png` | Show wet/dry boundary cells as a major reliability bottleneck | Results: Reliability/applicability diagnosis |
| Figure 5 | Phase 12 | `analysis/phase12_reliability/figures/depth_bin_error_comparison.png` | Show depth-dependent error and stronger underprediction in moderate/deep ranges | Results: Reliability/applicability diagnosis |
| Figure 6 | Phase 12 | `analysis/phase12_reliability/figures/top_failure_cases_rmse.png` | Identify high-error scenario concentration | Results: Reliability/applicability diagnosis |
| Figure 7 | Phase 13 | `analysis/phase13_failure_cases/figures/rank01_seed42_location2_r300y_p06_d3h_start0_t01_worst_maps.png` | Show representative false-dry and peak-depth underprediction failure mode | Results: Failure-case analysis |
| Figure 8 | Phase 13 | `analysis/phase13_failure_cases/figures/rank03_seed42_location2_r300y_p08_d3h_start0_t04_worst_maps.png` | Show repeated high-intensity `location2+r300y` failure pattern | Results: Failure-case analysis |
| Figure 9 | Phase 14 | `analysis/phase14_confidence/figures/confidence_margin_vs_wet_dry_error.png` | Demonstrate confidence margin as wet/dry classification risk proxy | Results: Confidence proxy diagnostics |
| Figure 10 | Phase 15 | `analysis/phase15_reliability_screening/figures/scenario_risk_category_counts.png` | Report deterministic scenario-level risk category distribution | Results: Reliability screening |
| Figure 11 | Phase 15 | `analysis/phase15_reliability_screening/figures/risk_component_heatmap.png` | Explain which risk components drive reliable/caution/high-risk labels | Results: Reliability screening |
| Figure 12 | Phase 15 | `analysis/phase15_reliability_screening/figures/pixel_risk_map_example.png` | Show spatially explicit pixel-level reliability risk | Results: Spatial risk mapping |
| Figure 13 | Phase 16 | `analysis/phase16_warning_rules/figures/warning_level_counts.png` | Show warning-level distribution after translating screening labels | Results: Warning-rule guidance |
| Figure 14 | Phase 16 | `analysis/phase16_warning_rules/figures/warning_action_matrix.png` | Present reliable/caution/high-risk operational actions | Methods or Results: Reliability-Aware Warning Layer |
| Figure 15 | Phase 16 | `analysis/phase16_warning_rules/figures/applicability_boundary_summary.png` | Summarize applicability boundary for manuscript readers | Discussion or Results: Applicability boundary |
| Figure 16 | Phase 16 | `analysis/phase16_warning_rules/figures/pixel_warning_map_example.png` | Show spatial warning interpretation at pixel level | Results: Warning-rule guidance |
| Table 1 | Dataset/model | Dataset metadata and model configuration | Summarize scenario design, inputs, outputs, prediction horizon, and model basis | Methods |
| Table 2 | Phase 10 | Phase 10 recommended setting | Preserve `boundary_band_pixels = 1` and `boundary_weight = 2.0` | Methods: Physics-Guided Prediction Framework |
| Table 3 | Phase 12-16 | Summary of quantitative findings | Provide compact quantitative evidence across reliability, screening, and warning layers | Results |
| Table 4 | Phase 16 | Warning action matrix and applicability boundary table | Define operational meaning of reliable/caution/high-risk labels | Methods or Discussion |
| Table 5 | Manuscript synthesis | Contribution and limitation mapping | Make claims and non-claims explicit for reviewers | Discussion or Conclusions |

## 10. Key quantitative facts to preserve

- Current Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`
- Phase 15: 57 Phase 10 map files loaded
- Phase 15: 114 scenario-level risk records
- Phase 15: 16384 pixel-level risk records
- Phase 15: 76 reliable, 25 caution, 13 high-risk
- Phase 15: Phase 13-like `location2+r300y` cases 24/24 flagged as caution/high-risk
- Phase 16: scenario warnings reliable=76, caution=25, high-risk=13
- Phase 16: pixel warnings reliable=5714, caution=8805, high-risk=1865
- Phase 16: high-risk warning cases=13, matching Phase 15 high-risk cases

## 11. Contribution statements

Manuscript-ready contribution statements:

- This study develops a rapid urban flood surrogate prediction framework for multi-step flood-depth mapping using a U-Net + TCN architecture.
- The surrogate is paired with physically informed prediction refinements, including the fixed Phase 10 margin-aware wet/dry setting, to support more physically plausible flood-process approximation.
- The study diagnoses reliability and applicability boundaries across timesteps, depth ranges, wet/dry boundary zones, scenario types, failure cases, and repeated seeds.
- The framework converts reliability evidence into deterministic scenario-level screening labels and pixel-level spatial risk maps.
- The warning layer translates reliable, caution, and high-risk labels into operational guidance for rapid reference use, targeted review, and non-standalone use in high-risk cases.
- The contribution is an integrated reliability-aware interpretation framework around a rapid surrogate, rather than a claim of universal generalization or calibrated probabilistic uncertainty.

## 12. Limitations and non-claims

- No calibrated probabilistic uncertainty is claimed.
- Confidence margin is a wet/dry classification risk proxy, not a full depth-error uncertainty estimate.
- Warning labels are deterministic operational interpretation labels, not predictive probabilities, Bayesian posterior estimates, calibrated confidence intervals, or guaranteed error bounds.
- The surrogate does not replace hydrodynamic simulation in high-stakes decisions.
- High-risk cases should trigger conservative interpretation, expert review, hydrodynamic-model confirmation, or other operational evidence.
- Generalization is limited to the tested scenario space, data, locations, rainfall events, and evaluation protocol.
- The framework should not be described as universally reliable for all pixels, all depth ranges, all event intensities, or external flood domains.
- Phase 12-18 reliability and writing stages did not retrain the model, modify architecture, modify the Phase 10 loss, tune `boundary_weight` or `boundary_band_pixels`, or open a new sweep.

## 13. Submission positioning

The manuscript is suitable for journals interested in hydrology and water resources, urban flood modeling, hydroinformatics, data-driven environmental modeling, decision-support systems, and warning-oriented environmental prediction.

The submission positioning should emphasize the integration of rapid flood-depth surrogate modeling with reliability-aware interpretation. The paper is not only a machine learning speed-up study; it is also a warning-support framework that makes prediction reliability, failure modes, spatial risk, and applicability boundaries explicit.

The manuscript should be presented conservatively. It should avoid claiming calibrated uncertainty, universal transferability, or replacement of hydrodynamic simulation. The strongest submission-facing claim is that the framework demonstrates how a rapid urban flood surrogate can be made more operationally interpretable through deterministic reliability screening and warning-rule guidance within the tested scenario space.

## 14. Immediate next writing tasks

1. Decide the final manuscript title.
2. Draft the full abstract from the abstract logic skeleton.
3. Assemble the final figure and table list, including which existing outputs will be reproduced, combined, or redrawn.
4. Convert the manuscript reliability warning layer notes into Methods, Results, and Discussion text.
5. Select a target journal or journal category.
6. Prepare introduction literature positioning around rapid urban flood prediction, hydrodynamic simulation cost, surrogate modeling, reliability-aware interpretation, and warning decision support.
