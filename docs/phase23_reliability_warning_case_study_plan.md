# Phase 23 Reliability-Aware Warning Case Study and Application Prototype Plan



## 1. Objective



Phase 23 moves the project from manuscript-oriented consolidation back to research development.



The objective is to build a case-based reliability-aware warning demonstration prototype by integrating the existing prediction outputs, Phase 15 reliability screening results, and Phase 16 warning-rule outputs.



This phase does not aim to improve the model by retraining or tuning. Instead, it aims to demonstrate how the existing reliability-aware framework can support interpretable warning-oriented case analysis.



The target workflow is:



- selected flood scenario

- predicted flood-depth field

- target/prediction/error comparison

- scenario-level reliability label

- pixel-level risk/warning map

- warning action

- applicability note

- case-based warning explanation



## 2. Research Position



Previous phases established the following chain:



- Phase 10: margin-aware physics-guided prediction model

- Phase 12: reliability and applicability diagnosis

- Phase 13: representative failure-case visualization

- Phase 14: confidence and disagreement proxy diagnostics

- Phase 15: reliability screening and spatial risk mapping

- Phase 16: warning-rule and applicability-boundary guidance

- Phase 17: reliability-aware warning framework synthesis

- Phase 18–22: manuscript-oriented consolidation



Phase 23 returns to research development by converting the reliability-aware warning framework into representative case demonstrations.



The core contribution of Phase 23 is not a new model, but a prototype-level demonstration of how reliability-aware flood prediction can be translated into warning interpretation.



## 3. What Phase 23 Should Do



Phase 23 should select representative cases from existing Phase 15 and Phase 16 outputs.



At minimum, the selected cases should include:



1. one reliable case

2. one caution case

3. one high-risk case



For each selected case, Phase 23 should generate:



1. target flood-depth map

2. predicted flood-depth map

3. absolute error map

4. risk/warning map

5. scenario-level warning label

6. warning action

7. applicability note

8. plain-language warning explanation



The final output should be a compact case-study report that can be used for README display, manuscript discussion, or future application prototype development.



## 4. What Phase 23 Should Not Do



Phase 23 must not perform the following actions:



1. no model retraining

2. no architecture modification

3. no Phase 10 boundary-weight sweep

4. no boundary_band_pixels tuning

5. no boundary_weight tuning

6. no new loss-function design

7. no metric-chasing experiment

8. no manuscript literature-review expansion

9. no reference formatting work



The current recommended Phase 10 setting remains:



- boundary_band_pixels = 1

- boundary_weight = 2.0



The boundary_weight = 1.5 setting remains only a conservative rollback option, not the current mainline setting.



## 5. Input Data and Existing Evidence



Phase 23 should reuse existing artifacts where possible.



Expected input sources include:



- analysis/phase15_reliability_screening/scenario_risk_scores.csv

- analysis/phase15_reliability_screening/pixel_risk_summary.csv

- analysis/phase15_reliability_screening/high_risk_cases.csv

- analysis/phase15_reliability_screening/summary.json

- analysis/phase16_warning_rules/scenario_warning_summary.csv

- analysis/phase16_warning_rules/pixel_warning_summary.csv

- analysis/phase16_warning_rules/high_risk_warning_cases.csv

- analysis/phase16_warning_rules/warning_rules.json

- analysis/phase16_warning_rules/summary.json



If map-level prediction files are needed, the script should locate and reuse existing Phase 10 evaluation map outputs rather than generating new predictions.



The script should be conservative. If exact target/prediction arrays cannot be located for a selected case, it should still generate a metadata-level case report and clearly mark the missing visual component instead of silently fabricating results.



## 6. Planned Script



The main script should be:



- scripts/build_phase23_warning_case_study.py



The script should create:



- analysis/phase23_warning_case_study/



Expected outputs:



- analysis/phase23_warning_case_study/summary.json

- analysis/phase23_warning_case_study/selected_cases.csv

- analysis/phase23_warning_case_study/case_warning_report.md

- analysis/phase23_warning_case_study/figures/



Recommended figures:



- figures/reliable_case_maps.png

- figures/caution_case_maps.png

- figures/high_risk_case_maps.png

- figures/case_warning_level_overview.png

- figures/case_risk_component_comparison.png



The exact figure names may be adjusted depending on available input fields, but the output should remain organized and reproducible.



## 7. Case Selection Logic



The case selection should be deterministic and transparent.



Recommended selection strategy:



Reliable case:



- choose a case labeled reliable

- prefer low scenario risk score

- prefer low false-dry risk

- prefer low boundary risk

- prefer relatively low RMSE if available



Caution case:



- choose a case labeled caution

- prefer moderate risk score

- prefer clear but not extreme warning components

- useful as an intermediate applicability-boundary example



High-risk case:



- choose a case labeled high-risk

- prefer Phase 13-like location2+r300y case if available

- prefer cases with false-dry, boundary, or peak-depth underprediction evidence



If multiple cases satisfy the same rule, choose the most representative one using stable sorting and document the selection criteria in selected_cases.csv.



## 8. Warning Explanation Logic



Each case should produce a warning explanation in technical but readable form.



The explanation should include:



1. scenario identity

2. warning level

3. dominant risk components

4. model reliability interpretation

5. suggested warning action

6. applicability boundary note



Example structure:



- Case: high-risk representative case

- Warning level: high-risk

- Dominant risk factors: high-intensity location2-like scenario, elevated false-dry risk, boundary-zone uncertainty

- Interpretation: the predicted flood extent and local peak depths should not be used without additional hydrodynamic-model or monitoring-based verification

- Suggested action: use as a preliminary screening result only; trigger manual review or physical-model confirmation

- Applicability note: this case lies near or outside the currently reliable operating envelope of the surrogate model



## 9. Expected Research Meaning



Phase 23 should demonstrate that the project has moved beyond pure prediction accuracy.



The intended contribution is:



- rapid flood prediction

- reliability screening

- warning-rule guidance

- representative warning case explanation



This supports the long-term project goal:



- a trustworthy, interpretable, physically consistent deep-learning surrogate framework for rapid urban flood warning



## 10. Acceptance Criteria



Phase 23 can be considered complete if the following conditions are satisfied:



1. the plan document is committed

2. scripts/build_phase23_warning_case_study.py is implemented

3. analysis/phase23_warning_case_study/ is generated

4. selected_cases.csv contains reliable, caution, and high-risk cases

5. case_warning_report.md gives readable warning explanations

6. figures are generated where source arrays are available

7. summary.json records inputs, selected cases, and limitations

8. README.md is updated with a concise Phase 23 section

9. docs/project_status.md is updated

10. docs/experiment_index.md is updated

11. no retraining, architecture modification, or Phase 10 parameter tuning is performed



## 11. Immediate Next Steps



After saving this plan:



1. inspect the plan

2. commit the plan

3. ask Codex to implement scripts/build_phase23_warning_case_study.py

4. run the script

5. inspect generated outputs

6. write Phase 23 findings

7. update README, project_status, and experiment_index

8. commit and merge Phase 23 into main if outputs are satisfactory

