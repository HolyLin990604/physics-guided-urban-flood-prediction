# Phase 19 Manuscript Structure Consolidation Plan

## 1. Objective

Phase 19 aims to turn the completed technical framework into a paper-ready manuscript outline and submission-oriented consolidation package.

This phase should organize the project narrative, manuscript structure, contribution statements, limitations, figure and table inventory, and submission-facing writing plan. It should consolidate existing evidence into a coherent paper framework rather than generate new experiments.

The target manuscript narrative is:

- rapid flood-depth prediction;
- reliability diagnosis;
- failure-mode interpretation;
- confidence proxy diagnostics;
- spatial risk mapping;
- warning-rule guidance;
- manuscript-ready reliability-aware warning layer.

## 2. Current Basis

The current project has already completed the core technical and interpretive phases needed for manuscript consolidation:

- Phase 10 identified the recommended margin-aware model setting, with `boundary_band_pixels = 1` and `boundary_weight = 2.0`.
- Phase 12 produced reliability and applicability diagnosis.
- Phase 13 produced representative failure-case visualization.
- Phase 14 produced confidence/disagreement proxy diagnostics.
- Phase 15 produced reliability screening and spatial risk mapping.
- Phase 16 produced warning-rule and applicability-boundary guidance.
- Phase 17 synthesized the reliability-aware warning framework.
- Phase 18 produced manuscript-oriented reliability-aware warning layer notes.

Phases 12 through 18 have already produced the reliability-aware warning framework and manuscript-ready warning layer. Phase 19 should now consolidate these materials into a complete manuscript structure and submission-oriented package.

## 3. Non-Goals

Phase 19 must not include:

- no retraining;
- no architecture modification;
- no Phase 10 loss modification;
- no `boundary_weight` tuning;
- no `boundary_band_pixels` tuning;
- no new hyperparameter sweep;
- no new result generation unless later explicitly needed;
- no overclaiming calibrated uncertainty or universal generalization.

Phase 19 is a manuscript planning, organization, and consolidation phase.

## 4. Main Manuscript Positioning

The likely paper positioning is:

**A reliability-aware deep learning surrogate framework for rapid urban flood warning.**

The manuscript should not be positioned only as a fast prediction model. The stronger and more complete framing is rapid flood prediction plus a reliability-aware warning framework.

This positioning connects the trained surrogate model to reliability diagnosis, failure-mode interpretation, confidence-margin risk proxy analysis, spatial risk mapping, deterministic warning labels, and applicability-boundary guidance. The manuscript should therefore emphasize decision-support interpretation around rapid surrogate predictions, not only predictive speed or aggregate accuracy.

## 5. Planned Deliverables

Phase 19 should create the following manuscript consolidation materials:

- `docs/manuscript_structure_and_submission_consolidation.md`;
- optional `docs/manuscript_figure_table_inventory.md`;
- optional `docs/manuscript_contribution_and_limitations_summary.md`.

The required first output is this Phase 19 plan document:

- `docs/phase19_manuscript_structure_consolidation_plan.md`.

Additional documents should remain manuscript-planning materials. They should not alter model code, training scripts, analysis outputs, requirements, or previous result files.

## 6. Proposed Manuscript Title Candidates

Possible manuscript titles include:

- Reliability-Aware Deep Learning Surrogate Modeling for Rapid Urban Flood Warning
- From Rapid Flood Prediction to Reliability-Aware Warning: A Deep Learning Surrogate Framework
- A Reliability-Aware Urban Flood Surrogate Framework with Spatial Risk Mapping and Warning Guidance
- Reliability Diagnosis and Warning Guidance for Deep Learning Surrogate Urban Flood Prediction
- Rapid Urban Flood Prediction with Deterministic Reliability Screening and Applicability Mapping

The final title should make clear that the contribution is not only fast flood-depth prediction, but a reliability-aware warning framework built around the surrogate model.

## 7. Proposed Manuscript Structure

The proposed manuscript structure is:

1. Introduction
2. Study Area and Dataset
3. Hydrodynamic Simulation and Surrogate Model
4. Physics-Guided Prediction Framework
5. Reliability-Aware Warning Layer
6. Results
7. Discussion
8. Conclusions

This structure separates the base predictive framework from the reliability-aware warning layer while preserving a single coherent paper narrative.

## 8. Section-by-Section Content Plan

### 1. Introduction

The introduction should motivate rapid urban flood prediction for warning support, then explain why speed alone is insufficient. It should introduce the need for reliability-aware interpretation, especially around wet/dry boundaries, high-intensity scenarios, false-dry risk, and applicability limits.

The introduction should present the manuscript contribution as a rapid surrogate prediction framework with reliability diagnosis, deterministic risk screening, spatial risk mapping, and warning-rule guidance.

### 2. Study Area and Dataset

This section should describe the urban flood prediction context, study area, scenario design, input-output structure, target flood-depth maps, and data split logic. It should explain the scenario variables only to the level needed for manuscript readability and reproducibility.

The section should avoid introducing new datasets or new claims beyond the completed project evidence.

### 3. Hydrodynamic Simulation and Surrogate Model

This section should summarize the hydrodynamic simulation basis and the deep learning surrogate task. It should explain what the surrogate predicts, how rapid prediction is used, and how the trained model relates to the hydrodynamic reference outputs.

The text should distinguish hydrodynamic modeling from surrogate inference and avoid claiming that the surrogate replaces physics-based modeling in high-stakes decisions.

### 4. Physics-Guided Prediction Framework

This section should describe the final model setting and physically informed refinement used in the project. The Phase 10 recommended setting should be preserved as `boundary_band_pixels = 1` and `boundary_weight = 2.0`.

The section should explain the margin-aware or boundary-aware logic as part of the prediction framework, without reopening loss design or tuning.

### 5. Reliability-Aware Warning Layer

This section should synthesize Phases 12 through 18 into a manuscript-ready framework. It should describe:

- reliability and applicability diagnosis;
- representative failure-case interpretation;
- confidence margin as a wet/dry classification risk proxy;
- deterministic reliability screening;
- spatial risk mapping;
- warning-rule guidance;
- applicability-boundary interpretation.

The section should explicitly state that warning labels are deterministic screening labels, not calibrated probabilistic uncertainty estimates.

### 6. Results

The results should organize evidence around both prediction performance and warning-oriented reliability. It should include base prediction performance, reliability diagnosis, failure-case visualization, confidence proxy diagnostics, risk mapping, and warning-rule outputs.

The results should preserve key quantitative facts from Phases 15 and 16 and avoid reinterpretation as new experiments.

### 7. Discussion

The discussion should explain how the framework supports reliability-aware warning use. It should discuss where the surrogate is useful, where caution is needed, and where the model should not be used alone.

The discussion should include limitations on calibrated uncertainty, scenario coverage, generalization, high-intensity cases, local peak-depth underprediction, and high-stakes operational use.

### 8. Conclusions

The conclusions should summarize the paper as a rapid urban flood surrogate framework with reliability-aware warning support. They should restate the main contributions, practical implications, and limitations without overstating uncertainty calibration or universal applicability.

## 9. Figure and Table Planning

Figures and tables should be organized into the following groups.

### Model/Data Figures

- study area and model domain;
- scenario and dataset construction overview;
- surrogate model input-output workflow;
- hydrodynamic simulation to surrogate prediction pipeline.

### Prediction Performance Figures

- aggregate predictive performance summaries;
- representative predicted versus reference flood-depth maps;
- wet/dry classification performance summaries;
- boundary-aware prediction examples, if already available.

### Reliability Diagnosis Figures

- error patterns by depth range;
- error patterns by boundary-distance zone;
- scenario-level reliability diagnosis;
- seed-level or repeated-run reliability summaries where already available.

### Failure-Case Figures

- representative high-error cases from Phase 13;
- high-intensity `location2` and `r300y` failure examples;
- false-dry dominated mismatch maps;
- peak-depth underprediction examples.

### Confidence Proxy Figures

- confidence margin distribution and wet/dry threshold proximity;
- confidence margin versus wet/dry classification risk;
- cross-seed disagreement as auxiliary evidence;
- limitations of confidence/disagreement proxies.

### Risk Mapping Figures

- scenario-level reliability screening labels;
- pixel-level risk maps;
- spatial risk concentration patterns;
- Phase 13-like case screening consistency.

### Warning-Rule/Applicability Figures

- warning-rule decision flow;
- reliable/caution/high-risk warning label distribution;
- applicability-boundary summary diagram;
- manuscript-ready reliability-aware warning framework schematic.

Tables should include a compact summary of model settings, key quantitative outputs, contribution mapping, limitation statements, and figure inventory if needed.

## 10. Key Quantitative Facts to Preserve

The manuscript consolidation must preserve the following quantitative facts:

- current Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`;
- Phase 15: 57 Phase 10 map files loaded;
- Phase 15: 114 scenario-level risk records;
- Phase 15: 16,384 pixel-level risk records;
- Phase 15: 76 reliable, 25 caution, 13 high-risk;
- Phase 15: Phase 13-like `location2` + `r300y` cases 24/24 flagged as caution/high-risk;
- Phase 16: scenario warnings reliable = 76, caution = 25, high-risk = 13;
- Phase 16: pixel warnings reliable = 5,714, caution = 8,805, high-risk = 1,865;
- Phase 16: high-risk warning cases = 13, matching Phase 15 high-risk cases.

These values should be carried into manuscript text, tables, captions, or result summaries without changing their meaning.

## 11. Contribution Statement Plan

The manuscript contribution statement should be organized around these categories:

- rapid urban flood surrogate prediction;
- physics-guided or physically informed model refinement;
- reliability and applicability diagnosis;
- deterministic risk screening and spatial risk mapping;
- warning-rule and applicability-boundary guidance.

The contribution language should emphasize the integrated framework: rapid prediction is combined with reliability-aware interpretation so that outputs can be used more responsibly for warning-oriented decision support.

## 12. Discussion and Limitation Plan

The discussion and limitation language should include:

- no calibrated probabilistic uncertainty;
- confidence margin as a wet/dry classification risk proxy;
- deterministic warning labels;
- limited tested scenario space;
- surrogate does not replace hydrodynamic modeling in high-stakes decisions;
- current framework is a reliability-aware decision-support layer.

The manuscript should avoid overclaiming universal generalization. It should state that the current framework improves interpretability and operational screening for the tested scenario space, while future work should expand validation, scenario diversity, uncertainty calibration, and operational coupling.

## 13. Completion Criteria

Phase 19 is complete when:

- the plan document is committed;
- a manuscript structure document is created;
- figure/table inventory is drafted or included;
- contribution and limitation statements are drafted;
- `README`, `project_status`, and `experiment_index` are updated if useful;
- the branch is merged into `main`.

Completion should be judged by whether the project has a clear, paper-ready manuscript structure and submission-oriented consolidation package that accurately reflects the completed technical framework without reopening experiments or introducing unsupported claims.
