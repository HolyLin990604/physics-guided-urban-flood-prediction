\# Phase 23 Reliability-Aware Warning Case Study Findings



\## 1. Phase Objective



Phase 23 moved the project from manuscript-oriented consolidation back to research development.



The objective was to convert the existing reliability-aware warning framework into a representative case-study prototype. Instead of improving the model through retraining or parameter tuning, this phase demonstrates how existing prediction outputs, reliability-screening labels, and warning-rule outputs can be integrated into interpretable warning-oriented case analysis.



Phase 23 therefore acts as a bridge between model evaluation and practical warning interpretation.



\## 2. Inputs Reused



Phase 23 reused existing outputs from previous phases:



\- Phase 15 reliability-screening and spatial risk-mapping outputs

\- Phase 16 warning-rule and applicability-boundary outputs

\- Existing Phase 10 forecast map arrays referenced by the selected Phase 15/16 rows



No new model prediction, retraining, architecture modification, or Phase 10 parameter tuning was performed.



\## 3. Generated Outputs



The main script added in this phase is:



\- scripts/build\_phase23\_warning\_case\_study.py



The generated output directory is:



\- analysis/phase23\_warning\_case\_study/



The main outputs are:



\- analysis/phase23\_warning\_case\_study/summary.json

\- analysis/phase23\_warning\_case\_study/selected\_cases.csv

\- analysis/phase23\_warning\_case\_study/case\_warning\_report.md

\- analysis/phase23\_warning\_case\_study/figures/case\_warning\_level\_overview.png

\- analysis/phase23\_warning\_case\_study/figures/case\_risk\_component\_comparison.png

\- analysis/phase23\_warning\_case\_study/figures/reliable\_case\_maps.png

\- analysis/phase23\_warning\_case\_study/figures/caution\_case\_maps.png

\- analysis/phase23\_warning\_case\_study/figures/high\_risk\_case\_maps.png



\## 4. Selected Representative Cases



Phase 23 selected three representative warning cases.



\### Reliable case



\- Scenario identity: location1|r100y\_p0.5\_d3h|6

\- Warning level: reliable

\- Risk score: 0.106

\- False-dry rate: 0.074

\- Boundary false-dry rate: 0.126

\- RMSE: 0.047

\- Suggested warning action: use as rapid prediction reference



This case represents the stronger applicability range of the current surrogate model. The available missed-inundation and boundary indicators are comparatively low, so the prediction can be used as a rapid reference.



\### Caution case



\- Scenario identity: location2|r300y\_p0.6\_d3h|6

\- Warning level: caution

\- Risk score: 3.852

\- False-dry rate: 0.246

\- Boundary false-dry rate: 0.308

\- Peak underprediction: 0.384 m

\- RMSE: 0.063

\- Suggested warning action: use with targeted review



This case represents an intermediate applicability-boundary condition. The prediction may still be useful as a rapid reference, but wet/dry boundaries, shallow transition areas, local peak-depth regions, and pixel-level risk maps should be reviewed before warning use.



\### High-risk case



\- Scenario identity: location2|r300y\_p0.8\_d3h|0

\- Warning level: high-risk

\- Risk score: 8.735

\- False-dry rate: 0.585

\- Boundary false-dry rate: 0.682

\- Wet-fraction contraction: 0.549

\- Peak underprediction: 1.527 m

\- RMSE: 0.097

\- Suggested warning action: do not use alone for warning decisions



This case is consistent with the Phase 13 finding that high-intensity location2 scenarios form a repeated failure mode. The high-risk case shows strong false-dry tendency, wet-fraction contraction, and peak-depth underprediction. It should trigger conservative interpretation, hydrodynamic-model confirmation, or expert review before being used in warning decisions.



\## 5. Figure Interpretation



The warning-level overview figure summarizes the three selected cases and their warning labels.



The risk-component comparison figure shows how the reliable, caution, and high-risk cases differ in risk score, false-dry tendency, boundary false-dry risk, wet-fraction contraction, peak underprediction, and RMSE.



The three case-map figures provide target, prediction, error, and warning/risk visualization panels for the selected reliable, caution, and high-risk cases.



The map figures were generated from existing forecast map NPZ artifacts:



\- reliable case: runs/phase10\_margin\_aware\_boundary\_band\_seed123\_40e/evaluation\_test/test\_batch\_0000/forecast\_maps.npz

\- caution case: runs/phase10\_margin\_aware\_boundary\_band\_seed123\_40e/evaluation\_test/test\_batch\_0009/forecast\_maps.npz

\- high-risk case: runs/phase10\_margin\_aware\_boundary\_band\_seed123\_40e/evaluation\_test/test\_batch\_0011/forecast\_maps.npz



\## 6. Main Finding



Phase 23 demonstrates that the project has moved beyond pure flood-depth prediction.



The current framework can now support a warning-oriented interpretation workflow:



\- rapid flood-depth prediction

\- reliability screening

\- scenario-level warning classification

\- pixel-level risk visualization

\- case-specific warning explanation

\- applicability-boundary interpretation



The three selected cases show a clear progression from reliable to caution to high-risk conditions.



This supports the broader project goal of developing a trustworthy, interpretable, physically consistent deep-learning surrogate framework for rapid urban flood warning.



\## 7. Technical Boundaries



Phase 23 should not be interpreted as a new model-training phase.



The following actions were not performed:



\- no model retraining

\- no architecture modification

\- no new prediction generation

\- no Phase 10 loss modification

\- no boundary\_weight tuning

\- no boundary\_band\_pixels tuning

\- no new parameter sweep

\- no metric-chasing experiment



The current recommended Phase 10 setting remains:



\- boundary\_band\_pixels = 1

\- boundary\_weight = 2.0



The boundary\_weight = 1.5 setting remains only a conservative rollback option.



\## 8. Limitations



The warning levels are deterministic screening and warning-rule labels, not calibrated probabilities.



The case map figures reuse existing forecast artifacts referenced by selected rows. They do not represent newly generated predictions.



The pixel-warning panel summarizes the Phase 16 repeated pixel-warning signal and should not be interpreted as a newly calibrated, case-specific uncertainty field.



The current prototype is a research demonstration rather than a deployable operational warning system.



\## 9. Phase 23 Conclusion



Phase 23 successfully converts the existing reliability-aware framework into a representative warning case-study prototype.



The phase provides a concrete demonstration of how a deep-learning flood surrogate can be used not only to generate rapid flood-depth predictions, but also to identify where the prediction is reliable, where it requires targeted review, and where it should not be used alone for warning decisions.



This phase strengthens the project’s transition from a model-performance study toward a reliability-aware flood-warning framework.

