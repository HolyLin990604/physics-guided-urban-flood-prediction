# Phase 25 Physics-Consistency Guided Surrogate Refinement Plan



## 1. Objective



Phase 25 moves from physical-consistency diagnosis to targeted physics-consistency guided surrogate refinement.



Phase 24 showed that high-risk cases are not only statistically worse, but physically less consistent. In particular, high-risk cases show stronger false-dry behavior, stronger wet-area contraction, stronger peak-depth underprediction, stronger wet-connectivity loss, and stronger volume under-response.



The purpose of Phase 25 is to design and test a narrow, interpretable refinement that directly targets these physical-consistency failure modes.



Phase 25 should not become a broad architecture search or a metric-chasing sweep. The first intervention should be small, targeted, and justified by Phase 24 evidence.



## 2. Research Position



The current project has already established the following chain:



- Phase 10: margin-aware physics-guided prediction model

- Phase 12: reliability and applicability diagnosis

- Phase 13: representative failure-case visualization

- Phase 14: confidence and disagreement proxy diagnostics

- Phase 15: reliability screening and spatial risk mapping

- Phase 16: warning-rule and applicability-boundary guidance

- Phase 17: reliability-aware warning framework synthesis

- Phase 18-22: manuscript-oriented consolidation

- Phase 23: reliability-aware warning case-study prototype

- Phase 24: physical-consistency deepening and process diagnostics



Phase 25 should build directly on Phase 24.



The core transition is:



- from diagnosing physical inconsistency

- to designing a targeted physics-consistency refinement

- to testing whether the refinement reduces the dominant physical failure modes without damaging the established mainline performance



## 3. Phase 24 Evidence Base



Phase 24 identified the following physical-consistency linkages with the Phase 15/16 risk score:



- false_dry_rate correlation with risk_score = 0.913

- wet_area_contraction correlation with risk_score = 0.862

- peak_depth_underprediction correlation with risk_score = 0.856

- connectivity_loss_indicator correlation with risk_score = 0.539



The warning-level group means also showed a clear reliable-to-high-risk physical degradation pattern.



False-dry rate:



- reliable = 0.125

- caution = 0.268

- high-risk = 0.444



Wet-area contraction:



- reliable = 0.046

- caution = 0.135

- high-risk = 0.383



Peak-depth underprediction:



- reliable = 0.024 m

- caution = 0.241 m

- high-risk = 1.381 m



Connectivity loss indicator:



- reliable = 0.197

- caution = 0.240

- high-risk = 1.000



Relative volume bias:



- reliable = -0.040

- caution = -0.145

- high-risk = -0.448



These results indicate that the first Phase 25 intervention should prioritize false-dry reduction and wet-area contraction reduction, while monitoring peak-depth preservation and connectivity behavior.



## 4. First Intervention Priority



The first Phase 25 intervention should focus on:



- false-dry reduction

- wet-area contraction penalty

- peak-depth preservation monitoring

- wet-connectivity preservation monitoring

- volume-response consistency monitoring



The primary intervention should not attempt to implement a full shallow-water-equation residual or a full PINN formulation.



Reason:



- the current artifacts do not include complete velocity, flux, boundary, DEM, and source-sink fields

- a full SWE/PINN loss would be under-supported by available variables

- Phase 24 already identified more directly actionable failure modes from existing depth-field outputs



Therefore, the first intervention should be a depth-field-compatible physical-consistency refinement.



## 5. Candidate Refinement Design



The recommended first candidate is a wet-area contraction and false-dry reduction refinement.



Possible loss components:



1. false-dry weighted wet-region loss

2. wet-area contraction penalty

3. high-depth or peak-depth preservation weight

4. temporal volume-response consistency penalty

5. optional connectivity-aware diagnostic term, initially used for evaluation rather than training



The first coding step should inspect the existing loss framework before changing anything.



The intervention should be implemented as a configurable option, not as a hard-coded replacement.



Suggested configuration fields may include:



- enable_wet_area_contraction_loss

- wet_area_contraction_weight

- enable_false_dry_weighted_loss

- false_dry_weight

- enable_peak_depth_preservation_weight

- peak_depth_weight

- enable_volume_response_consistency_loss

- volume_response_weight



The exact names should follow the current repository style after inspecting existing configs.



## 6. Recommended First Experiment



The first formal test should be conservative.



Recommended initial candidate:



- start from the current Phase 10 recommended setting

- keep boundary_band_pixels = 1

- keep boundary_weight = 2.0

- add only one primary physical-consistency refinement first



The preferred first refinement is:



- wet-area contraction / false-dry reduction



A possible first experimental label:



- phase25_wet_area_false_dry_refinement



The first run should use one representative seed first, preferably seed123 or the seed most relevant to the known high-risk failure cases, before any multi-seed expansion.



Only after the first pilot is stable should additional seeds be considered.



## 7. Evaluation Metrics



Phase 25 should evaluate both standard predictive metrics and physical-consistency metrics.



Standard metrics:



- RMSE

- MAE

- wet/dry IoU

- validation loss

- test loss if evaluated



Physical-consistency metrics:



- false_dry_rate

- false_wet_rate

- wet_area_contraction

- relative_volume_bias

- peak_depth_underprediction

- connectivity_loss_indicator

- largest_component_ratio_change

- timestep-wise volume bias

- timestep-wise wet-area bias



Warning-oriented metrics:



- risk_score if reused from Phase 15/16 logic

- warning-level grouped physical metrics

- high-risk case improvement

- Phase 23 selected case physical profile comparison



The key question is not only whether RMSE improves.



The key question is whether the targeted refinement reduces physically meaningful failure modes without causing unacceptable degradation in established predictive metrics.



## 8. Comparison Baseline



The baseline should remain the current recommended Phase 10 setting:



- boundary_band_pixels = 1

- boundary_weight = 2.0



This setting is the current mainline and should not be replaced unless Phase 25 evidence is clearly stronger.



The baseline comparison should use existing Phase 10 outputs whenever possible.



If new training is eventually run, it should be compared against the same seed and comparable training schedule.



## 9. Acceptance Criteria



A Phase 25 candidate can be considered promising only if it satisfies most of the following:



1. false_dry_rate decreases in caution/high-risk scenarios

2. wet_area_contraction decreases in caution/high-risk scenarios

3. peak_depth_underprediction does not worsen and preferably improves

4. connectivity_loss_indicator does not worsen and preferably improves

5. RMSE and MAE do not degrade substantially

6. wet/dry IoU does not suffer a serious regression

7. the known Phase 23 high-risk case shows improved physical-consistency profile

8. improvements are not limited to one isolated case

9. no obvious new failure mode appears in qualitative maps

10. the result is explainable in terms of the Phase 24 physical-consistency diagnosis



A candidate should not be promoted merely because it improves one metric.



## 10. What Phase 25 Should Not Do



Phase 25 must not perform the following actions:



- no broad architecture search

- no uncontrolled hyperparameter sweep

- no return to Phase 10 boundary_weight tuning

- no boundary_band_pixels sweep

- no full SWE/PINN residual unless required variables are available

- no traffic-impact modeling yet

- no manuscript-only work

- no unsupported claim that the model is physically complete

- no replacement of the current Phase 10 recommendation without sufficient evidence



The current recommended Phase 10 setting remains:



- boundary_band_pixels = 1

- boundary_weight = 2.0



The boundary_weight = 1.5 setting remains only a conservative rollback option.



## 11. Expected Outputs



Phase 25 should produce, at minimum:



- docs/phase25_physics_consistency_guided_refinement_plan.md

- an implementation note or script/config changes for the first targeted refinement

- a pilot training or diagnostic result directory if training is performed

- Phase 25 comparison metrics

- updated physical-consistency diagnostics for the candidate

- docs/phase25_physics_consistency_guided_refinement_findings.md



If the first step is only code preparation and dry-run validation, that should be documented honestly.



## 12. Suggested Workflow



Recommended Phase 25 workflow:



1. write and commit this plan

2. inspect the current loss implementation and config structure

3. ask Codex to propose the smallest safe implementation plan

4. implement the targeted false-dry / wet-area contraction refinement behind config flags

5. run a minimal smoke test or syntax test

6. run one pilot training only after the implementation is verified

7. evaluate the pilot with standard metrics and Phase 24 physical-consistency diagnostics

8. decide whether the candidate deserves multi-seed testing

9. write findings and update project documentation



## 13. Expected Research Meaning



Phase 25 should move the project from physical-consistency diagnosis to targeted physical-consistency improvement.



The intended contribution is:



- identify dominant physical failure modes

- design a depth-field-compatible physical refinement

- test whether the refinement reduces physically meaningful failure modes

- preserve the reliability-aware warning framework

- avoid blind metric chasing



If successful, Phase 25 will move the project closer to a physically consistent, interpretable, and operationally useful flood surrogate model.



## 14. Immediate Next Steps



After saving this plan:



1. inspect the plan

2. commit the plan

3. inspect existing loss and config files

4. ask Codex for a minimal implementation proposal before coding

5. do not train until the implementation plan is clear

