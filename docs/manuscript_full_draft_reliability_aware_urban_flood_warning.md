# Reliability-Aware Deep Learning Surrogate Framework for Rapid Urban Flood Warning

## 1. Title and manuscript status

Working title:

# Reliability-Aware Deep Learning Surrogate Framework for Rapid Urban Flood Warning

Manuscript status:

This document is a full draft expansion prepared for Phase 22. It is not a final journal submission. Literature citations, study-area wording, dataset metadata, figure selection, captions, tables, and journal formatting remain to be completed before submission.

Alternative title options:

- From Rapid Flood Prediction to Reliability-Aware Urban Flood Warning: A Deep Learning Surrogate Framework
- Reliability Screening and Spatial Risk Mapping for Deep Learning Surrogate Urban Flood Prediction
- Physics-Guided Urban Flood Surrogate Prediction with Deterministic Warning Guidance
- Rapid Urban Flood Prediction with Reliability Diagnosis and Applicability Mapping

## 2. Abstract

Draft abstract:

Urban pluvial flood warning requires rapid spatial information on inundation extent and flood-depth evolution. Physics-based hydrodynamic models provide physically credible flood simulations and remain essential references for scenario analysis and high-stakes decision support, but their computational burden can limit repeated near-real-time use across rainfall scenarios, forecast updates, and operational decision cycles [literature to be added]. Deep learning surrogate models can approximate hydrodynamic flood-depth fields at much lower inference cost, yet prediction-only surrogate outputs are insufficient for warning use when aggregate accuracy does not identify where predictions are reliable, where wet/dry classification is sensitive, or where severe underprediction may occur.

This study develops a reliability-aware deep learning surrogate framework for rapid urban flood warning. The framework combines a U-Net + TCN multi-step flood-depth surrogate with physically informed prediction components and a post-prediction reliability-aware warning layer. The surrogate is evaluated in the fixed Phase 10 setting, with `boundary_band_pixels = 1` and `boundary_weight = 2.0`; later reliability phases do not retrain the model, modify the architecture, modify the Phase 10 loss, or reopen boundary-parameter tuning. The reliability layer diagnoses applicability across timesteps, depth ranges, wet/dry boundary zones, scenario types, and seeds; interprets representative failure modes; evaluates confidence margin as a wet/dry classification risk proxy with `wet_threshold = 0.05`; uses cross-seed disagreement only as auxiliary evidence; converts diagnostic evidence into deterministic reliability screening and spatial risk maps; and translates reliable, caution, and high-risk labels into warning-rule guidance.

The Phase 15 screening stage loaded 57 Phase 10 map files, generated 114 scenario-level risk records and 16384 pixel-level risk records, and classified 76 cases as reliable, 25 as caution, and 13 as high-risk. Phase 13-like `location2+r300y` cases were flagged as caution or high-risk in 24/24 cases. Phase 16 produced scenario warnings of reliable=76, caution=25, high-risk=13; pixel warnings of reliable=5714, caution=8805, high-risk=1865; and 13 high-risk warning cases, matching the Phase 15 high-risk cases. These results support a warning-oriented interpretation in which rapid surrogate predictions are accompanied by deterministic reliability labels and applicability-boundary guidance. The framework does not claim calibrated probabilistic uncertainty, universal generalization, or replacement of hydrodynamic modeling in high-stakes decisions.

## 3. Keywords

Urban flood warning; deep learning surrogate; reliability screening; flood-depth prediction; physics-guided learning; spatial risk mapping; applicability boundary

## 4. Introduction

Urban pluvial flooding can develop rapidly when intense rainfall exceeds the capacity of surface drainage pathways, stormwater infrastructure, and local storage. In dense urban environments, shallow topographic gradients, impervious surfaces, road networks, underground drainage structures, and localized depressions can create complex inundation patterns. Warning and emergency-response workflows therefore require more than a scalar rainfall threshold or a delayed post-event assessment. They benefit from spatially distributed information about flood depth, wet/dry extent, and how inundation may evolve over the next prediction window [literature to be added].

Hydrodynamic flood models remain a central tool for representing urban flood processes. They encode process-based assumptions about rainfall-runoff transformation, flow routing, topographic controls, and inundation dynamics. When properly configured and validated, hydrodynamic simulations provide a credible basis for scenario design, hazard mapping, and reference flood-depth fields [literature to be added]. However, high-resolution hydrodynamic simulation can be computationally demanding, especially when repeated over many rainfall scenarios, forecast updates, uncertain boundary conditions, or operational decision cycles. This computational burden motivates surrogate models that can approximate flood-depth evolution rapidly while retaining useful spatial detail.

Deep learning surrogate models provide one path toward rapid urban flood prediction. Encoder-decoder neural networks can learn spatial patterns in gridded flood-depth fields, while temporal modules can represent the evolution of rainfall-driven inundation over multiple forecast steps [literature to be added]. In this manuscript, the surrogate uses a U-Net + TCN architecture to predict future flood-depth maps from past flood states, rainfall forcing, and static spatial inputs. Such a model can serve as a fast approximation of hydrodynamic outputs within the tested scenario space.

For warning use, however, rapid prediction alone is not enough. A surrogate model can have acceptable aggregate error while still underperforming in operationally important regions. Errors at wet/dry boundaries can alter the predicted inundation extent. False-dry predictions can hide inundated cells. Moderate-to-deep depths and local peaks can be underpredicted even when wet/dry classification appears confident. High-intensity scenarios may expose applicability limits that are not obvious from global metrics. A prediction-only workflow may therefore provide a flood-depth map without indicating where the map should be trusted, where it should be reviewed, or where it should not be used alone.

This study addresses that gap by framing the surrogate as part of a reliability-aware warning framework. Reliability is treated as deterministic diagnostic evidence, not as calibrated probabilistic uncertainty. The framework diagnoses reliability and applicability boundaries, interprets representative failure cases, evaluates confidence-margin behavior near the wet/dry threshold, maps spatial risk, and translates screening labels into warning guidance. The contribution is an integrated warning-oriented interpretation layer around a fixed rapid surrogate, rather than a claim that the surrogate universally generalizes or replaces hydrodynamic modeling.

The remainder of the manuscript is organized as follows. Section 5 describes the study context and dataset. Section 6 summarizes the hydrodynamic reference role and the U-Net + TCN surrogate. Section 7 describes the physics-guided prediction framework and the fixed Phase 10 setting. Section 8 develops the reliability-aware warning layer. Section 9 reports prediction, reliability, confidence, screening, and warning-rule results. Section 10 discusses operational interpretation, limitations, and future work. Section 11 concludes the draft.

## 5. Study Area and Dataset

This draft section describes the urban flood surrogate prediction context. Final study-area name, domain extent, map resolution, hydrodynamic model configuration, rainfall scenario definitions, drainage representation, and dataset statistics should be verified before submission [study-area details to verify].

The study considers multi-step urban flood-depth prediction in an UrbanFlood24 Lite-style setting. Hydrodynamic simulation outputs are used as the reference or pseudo-observation data for training, evaluating, and diagnosing the surrogate. The surrogate task is to predict future gridded flood-depth fields from past flood-depth sequences, rainfall forcing, and static spatial descriptors. The operational motivation is rapid warning support: the model should provide fast spatial predictions while the reliability-aware layer indicates the limits of interpretation.

The dynamic target variable is a flood-depth map sequence. Each sample contains past flood-depth states and future reference flood-depth fields. In the current project setup, the dynamic flood data are represented by `flood.npy`, with `input_steps = 12` and `pred_steps = 12`. The manuscript should later report the temporal interval, depth unit, spatial grid resolution, preprocessing method, and whether any transformations or masks are applied [dataset preprocessing details to verify].

Rainfall forcing provides the event driver for the flood response. The current dataset uses `rainfall.npy`, and the surrogate conditions on both past and future rainfall information. Scenario metadata include location and rainfall-event descriptors; high-intensity `location2` and `r300y` cases are especially important in the reliability analysis because they appear in the representative failure and warning-risk evidence. Final manuscript text should define the event notation, return-period interpretation, rainfall duration, temporal pattern, and whether scenarios are synthetic, design-based, historical, or otherwise generated [rainfall scenario table to be added].

Static spatial inputs provide the urban context for flood-depth prediction. The current dataset layout includes `absolute_DEM.npy`, `impervious.npy`, and `manhole.npy`, representing elevation, imperviousness, and drainage/manhole-related spatial information. These layers are used as spatial conditioning variables for the surrogate. Final submission text should verify the source, resolution, normalization, physical interpretation, and limitations of each layer [static spatial metadata to verify].

Training and testing are organized through train/test scenario partitions. The current project references `data/urbanflood24_lite/train/` and `data/urbanflood24_lite/test/`. The final manuscript should clarify whether the test split evaluates interpolation within the scenario design, more difficult extrapolative rainfall/location combinations, or a mixture of both. It should also document seed usage, scenario independence, and whether repeated seeds are used only for diagnostic reliability interpretation or for model selection [split protocol to verify].

## 6. Hydrodynamic Simulation and Surrogate Model

The hydrodynamic model is used as the reference data generator. It defines the flood-depth fields that the surrogate learns to approximate and against which prediction errors are evaluated. In this manuscript, hydrodynamic outputs are treated as reference or pseudo-observation data because the surrogate is trained to reproduce these simulated fields. This role should be stated clearly: the surrogate is a rapid approximation of hydrodynamic outputs within the evaluated scenario space, not a replacement for hydrodynamic simulation in high-stakes decisions.

[equation to be inserted: hydrodynamic governing-equation summary or process description, if included in the final manuscript]

The surrogate model follows a U-Net + TCN design. The U-Net encoder-decoder component represents spatial structure in flood-depth maps and static input layers. The encoder compresses spatial flood and terrain information into latent features, while the decoder reconstructs predicted future flood-depth maps. The temporal convolutional module supports temporal representation across the input sequence and prediction horizon. This architecture is appropriate for the project objective because it combines spatial feature learning with multi-step temporal conditioning.

Rainfall conditioning links the predicted flood response to the forcing sequence. The model uses rainfall information from the relevant input and future windows, together with past flood states and static maps, to predict future flood-depth fields. Final manuscript text should describe the exact implemented conditioning path used by the retained Phase 10 model without reopening architecture comparison or introducing new model variants [model configuration details to verify].

The prediction target is a sequence of future flood-depth maps. The current setup uses `input_steps = 12` and `pred_steps = 12`, so the surrogate maps a past flood and rainfall context into a future flood-depth trajectory. Evaluation should include standard continuous-depth metrics such as RMSE and MAE, plus wet/dry classification-oriented metrics such as wet/dry IoU, wet/dry classification error, false-dry behavior, and wet-fraction diagnostics where supported by the existing evidence. Official evaluation metrics should remain the reference for final performance reporting, while Phase 12 pooled diagnostics should be used for reliability profiling rather than substituted for official test metrics.

[figure to be finalized: hydrodynamic reference, surrogate inputs, U-Net + TCN model, and prediction horizon]

[equation to be inserted: RMSE, MAE, wet/dry IoU, and wet/dry threshold definitions]

## 7. Physics-Guided Prediction Framework

The surrogate framework includes physically informed prediction components designed to improve physical plausibility and warning relevance. These components should be described as output-level or loss-level physical guidance, not as a complete replacement for hydrodynamic governing equations. Their purpose is to discourage physically implausible predictions and improve sensitivity to warning-relevant flood features while retaining the computational advantages of the surrogate.

Non-negativity is the most direct physical constraint. Flood depth should not be negative, so the prediction framework discourages or penalizes negative depth values. This helps maintain physically interpretable flood-depth maps.

[equation to be inserted: non-negativity component]

Wet/dry consistency addresses the thresholded interpretation of inundation state. Because warning users often interpret flood maps through both continuous depth and wet/dry extent, cells near the wet/dry threshold require special care. Small errors around the threshold can change whether a cell is classified as inundated. The wet/dry consistency component therefore supports more stable behavior around the wet/dry decision boundary.

[equation to be inserted: wet/dry consistency component]

Rainfall-depth consistency connects rainfall forcing to predicted flood response. The final manuscript should describe the implemented formulation exactly and avoid implying hydrodynamic guarantees beyond the project implementation [exact formulation to verify].

[equation to be inserted: rainfall-depth consistency component]

Topographic regularization uses terrain or spatial context to guide predicted flood-depth patterns. Its final description should align with the implemented project component and should not overstate process fidelity. The appropriate claim is that static spatial information and regularization help condition the surrogate on physically relevant surface properties [exact formulation to verify].

[equation to be inserted: topographic or spatial regularization component]

Margin-aware wet/dry boundary refinement is the retained Phase 10 configuration. The current recommended setting is:

```text
boundary_band_pixels = 1
boundary_weight = 2.0
```

This setting is fixed for the reliability-oriented manuscript. Later phases use it as the diagnostic basis; they do not tune `boundary_weight`, tune `boundary_band_pixels`, modify the Phase 10 loss, retrain the model, change the architecture, or open a new sweep. The Results and Discussion should therefore present the reliability analysis as interpretation of the fixed Phase 10 surrogate, not as a new experiment phase.

## 8. Reliability-Aware Warning Layer

The reliability-aware warning layer is an application-oriented interpretation layer built around the fixed surrogate. It does not modify the trained model, loss function, architecture, or prediction procedure. Instead, it interprets saved or generated surrogate outputs after prediction and translates reliability evidence into deterministic scenario-level labels, pixel-level risk maps, warning rules, and applicability-boundary guidance.

The layer follows a five-step chain. First, reliability and applicability diagnosis evaluates model behavior across timesteps, target depth ranges, wet/dry boundary-distance zones, scenario types, and seeds. Second, representative failure-case interpretation examines the highest-ranked failures to identify recurring physical and spatial error modes. Third, confidence and disagreement proxy diagnostics evaluate deterministic output-space signals, especially confidence margin near the wet/dry threshold. Fourth, deterministic reliability screening and spatial risk mapping convert these diagnostics into scenario-level and pixel-level labels. Fifth, warning-rule and applicability-boundary guidance translate labels into operational interpretation.

Reliability and applicability diagnosis distinguishes warning-relevant behavior from aggregate accuracy. The established caution zones include exact wet/dry boundary cells, shallow threshold-adjacent cells, moderate-to-deep target depths, high-intensity `location2` scenarios, and local peak-depth extremes. These zones have different meanings. Boundary and shallow threshold-adjacent cells are sensitive to wet/dry classification changes. Moderate-to-deep depths and local peaks are more closely associated with depth-magnitude underprediction. High-intensity `location2` scenarios indicate a scenario-level applicability limit within the tested evidence.

Representative failure-case interpretation shows that severe failures are structured rather than random. The strongest documented failures concentrate in high-intensity `location2` target scenarios, especially repeated `location2+r300y` cases across seeds. The dominant failure modes are systematic underprediction, reduced predicted wet fraction, local peak-depth underprediction, false-dry dominated wet/dry mismatch, and boundary-transition failure around wet/dry margins. These patterns are operationally important because they can underestimate inundation extent and severity.

The confidence-margin diagnostic is defined conceptually as:

```text
confidence_margin = abs(prediction - wet_threshold)
```

with:

```text
wet_threshold = 0.05
```

A low confidence margin means that a predicted depth lies near the wet/dry decision threshold. Such cells are sensitive because small depth errors can change the interpreted state from dry to wet or wet to dry. Confidence margin is therefore used as a wet/dry classification risk proxy. It is not calibrated probabilistic uncertainty, not a probability of error, not a Bayesian posterior estimate, not a confidence interval, and not a complete depth-error uncertainty measure. A cell can be confidently wet or dry while still having substantial depth-magnitude error, especially in moderate-to-deep or peak-depth regions.

Cross-seed disagreement is retained only as auxiliary evidence. It can indicate some prediction variability across trained seeds, but Phase 14 evidence indicates that it is not a strong standalone scenario-error predictor. Multiple seeds can fail similarly on the same high-intensity cases, so low disagreement should not be interpreted as proof of reliability.

The deterministic reliability-screening layer uses transparent components derived from the earlier diagnostics: low confidence-margin risk, false-dry risk, predicted wet-fraction contraction, peak-depth underprediction, mean underprediction bias, boundary-zone false-dry risk, high-intensity `location2` metadata risk, and auxiliary cross-seed disagreement. These components support reliable, caution, and high-risk labels. The labels are deterministic operational interpretation labels, not calibrated probabilities or guaranteed error bounds.

The warning-rule guidance is:

| Warning level | Operational interpretation |
|---|---|
| reliable | use as rapid prediction reference |
| caution | use with targeted review |
| high-risk | do not use alone for warning decisions |

Reliable predictions fall within the stronger current applicability region and may support rapid situational awareness with normal review. Caution predictions remain useful, but sensitive areas such as wet/dry boundaries, shallow threshold-adjacent cells, local peak-depth regions, and pixel-level risk maps should be reviewed. High-risk predictions require conservative interpretation and should not be used alone for warning decisions; hydrodynamic-model confirmation, expert review, or other operational evidence is needed before high-stakes use.

## 9. Results

### 9.1 Prediction performance overview

The base surrogate provides rapid multi-step flood-depth prediction using past flood states, rainfall forcing, and static spatial inputs. This result supports the first part of the manuscript framing: a trained U-Net + TCN surrogate can produce spatial flood-depth fields for the tested UrbanFlood24 Lite-style scenario space. Final submission text should insert the official evaluation metrics and representative prediction maps from the standard evaluation outputs, rather than substituting Phase 12 pooled diagnostic metrics for official performance reporting [official performance table to be added].

The prediction-performance section should establish the model as a useful rapid approximation before introducing reliability limitations. The appropriate claim is not that the surrogate is uniformly accurate, but that it provides a rapid prediction basis that can be interpreted through later reliability diagnostics. This subsection should include RMSE, MAE, wet/dry IoU, and representative target-prediction-error maps when final figures are selected.

[figure to be finalized: representative prediction, reference flood-depth map, and error map]

### 9.2 Reliability and applicability diagnosis

Reliability diagnosis shows that aggregate performance is not sufficient for warning interpretation. Phase 12 evidence indicates that reliability varies across timesteps, target depth ranges, wet/dry boundary-distance zones, scenario types, and seeds. The model is useful for rapid spatiotemporal flood-process approximation under the tested scenarios, but it is not equally reliable for every pixel, depth range, or event condition.

The main diagnostic caution zones are exact wet/dry boundary cells, shallow threshold-adjacent cells, moderate-to-deep depths, high-intensity `location2` scenarios, and local peak-depth extremes. Boundary cells and shallow threshold-adjacent cells are warning-sensitive because small depth errors can change wet/dry interpretation. Moderate-to-deep cells and local peaks require attention because Phase 12 and Phase 13 evidence identify stronger underprediction risk in these conditions. High-intensity `location2` scenarios require caution because they dominate the highest-ranked failure cases in the existing evidence.

[figure to be finalized: boundary-distance classification error and depth-bin error diagnostics]

### 9.3 Representative failure-case interpretation

Representative failure-case analysis shows that severe errors are systematic rather than random. Phase 13 selected the top representative failures from the Phase 12 failure-case ranking. The top cases collapse into repeated high-intensity `location2` target scenarios across seeds, especially `location2 / r300y_p0.6_d3h / start_idx = 0` and `location2 / r300y_p0.8_d3h / start_idx = 0`.

The visual and quantitative interpretation is consistent across the representative cases: predicted depths are weaker than the target fields, predicted wet fractions are reduced, local peak depths are underpredicted, and wet/dry mismatch is dominated by false-dry regions. These failure modes directly affect warning interpretation because they can hide inundation extent and underestimate local severity. The reliability-aware framework therefore treats these cases as evidence for applicability-boundary guidance rather than as isolated outliers.

[figure to be finalized: representative systematic failure case from Phase 13]

### 9.4 Confidence proxy diagnostics

Phase 14 supports confidence margin as a wet/dry classification risk proxy. The proxy is defined as `confidence_margin = abs(prediction - wet_threshold)`, with `wet_threshold = 0.05`. Low-margin cells lie close to the wet/dry decision threshold and show higher wet/dry classification risk in the documented diagnostics. This supports the use of confidence margin for identifying threshold-sensitive areas that should be interpreted cautiously.

The same evidence also defines the limits of the proxy. Confidence margin should not be interpreted as calibrated probabilistic uncertainty or as a full depth-error uncertainty estimate. It primarily addresses wet/dry classification sensitivity near the threshold. Moderate-to-deep depth errors, peak-depth underprediction, and wet-area contraction require additional diagnostics. Cross-seed disagreement is useful only as auxiliary evidence because its global relationship with scenario-level error is weak and because multiple seeds can fail similarly on structured high-intensity scenarios.

[figure to be finalized: confidence margin versus wet/dry classification error]

### 9.5 Reliability screening and spatial risk mapping

Phase 15 converted the Phase 12-14 evidence into deterministic reliability screening and spatial risk mapping. The exact preserved Phase 15 facts are:

- Phase 15: 57 Phase 10 map files loaded
- Phase 15: 114 scenario-level risk records
- Phase 15: 16384 pixel-level risk records
- Phase 15: 76 reliable, 25 caution, 13 high-risk
- Phase 15: Phase 13-like `location2+r300y` cases 24/24 flagged as caution/high-risk

These results show that the diagnostic evidence can be operationalized as scenario-level reliability labels and pixel-level risk summaries. The 76/25/13 distribution indicates that the framework does not treat all surrogate predictions as globally unreliable; instead, it identifies specific cases with stronger risk evidence. The 24/24 flagging of Phase 13-like `location2+r300y` cases supports consistency between the representative failure-case interpretation and the automatic screening layer.

Pixel-level risk mapping extends the analysis from scenario labels to spatial warning support. It identifies grid cells that repeatedly show low-margin, wet/dry boundary, false-dry, deep-underprediction, or high-risk-case signals. These maps are intended to guide targeted review of sensitive regions rather than provide event probabilities.

[figure to be finalized: scenario risk category counts, risk component heatmap, and pixel risk map]

### 9.6 Warning-rule and applicability-boundary guidance

Phase 16 translated the Phase 15 deterministic screening labels into warning guidance. The exact preserved Phase 16 facts are:

- Phase 16: scenario warnings reliable=76, caution=25, high-risk=13
- Phase 16: pixel warnings reliable=5714, caution=8805, high-risk=1865
- Phase 16: high-risk warning cases=13, matching Phase 15 high-risk cases

The scenario warning counts preserve the Phase 15 distribution while attaching operational recommendations. Reliable cases may be used as rapid prediction references with normal review. Caution cases require targeted review of sensitive areas, including wet/dry boundaries, threshold-adjacent cells, peak-depth regions, and spatial risk maps. High-risk cases should not be used alone for warning decisions and should trigger conservative interpretation, hydrodynamic-model confirmation, expert review, or other supporting evidence.

The pixel warning counts provide spatially explicit interpretation. The presence of 5714 reliable, 8805 caution, and 1865 high-risk pixel warnings indicates that warning guidance is not only scenario-level but also spatially differentiated. These labels are deterministic operational interpretation labels and should not be read as probabilities of flooding or probabilities of model error.

[figure to be finalized: warning action matrix, pixel warning map, and applicability boundary summary]

## 10. Discussion

The results support a manuscript framing that moves beyond prediction accuracy alone. Rapid flood-depth prediction is necessary for warning workflows, but aggregate metrics do not reveal whether the model is reliable at wet/dry boundaries, shallow threshold-adjacent cells, local peaks, or high-intensity scenarios. The reliability-aware framework addresses this limitation by attaching diagnostic interpretation to the fixed surrogate output.

Physical plausibility and reliability-aware interpretation play complementary roles. The Phase 10 margin-aware setting supports boundary-sensitive prediction through the retained `boundary_band_pixels = 1` and `boundary_weight = 2.0` configuration. The reliability phases then show where the model remains weaker even under this setting. This distinction is important: the physics-guided components improve the prediction framework, while the warning layer interprets the residual reliability limits without changing the model.

False-dry and wet/dry boundary risks are especially important for warning use. A false-dry prediction can hide inundation rather than merely perturb a continuous depth estimate. Wet/dry boundary cells and shallow threshold-adjacent cells are sensitive because small depth errors can move the apparent inundation edge. These risks justify confidence-margin diagnostics, boundary-distance reliability analysis, and pixel-level caution mapping.

Depth-magnitude errors require a separate interpretation. Confidence margin can identify wet/dry classification risk near `wet_threshold = 0.05`, but it does not guarantee accurate depth magnitude. Moderate-to-deep depths, local peak-depth extremes, and high-intensity `location2+r300y` scenarios can show underprediction even when wet/dry classification is not ambiguous everywhere. This is why the framework combines confidence margin with failure-case interpretation, wet-fraction contraction, peak-depth underprediction, mean bias, and scenario metadata risk.

The reliable, caution, and high-risk labels should be understood as deterministic operational interpretation labels. They are useful because they translate diagnostic evidence into practical review actions. They are not calibrated probabilities, Bayesian uncertainty estimates, confidence intervals, or guaranteed error bounds. If calibrated probabilistic uncertainty is required, it should be developed through a separate calibration design, calibration dataset, and validation protocol.

The applicability boundary is limited to the tested scenario space. The current evidence supports rapid reference use for ordinary test scenarios without strong risk components, caution for wet/dry boundary regions and threshold-adjacent cells, and non-standalone use for high-risk cases such as repeated high-intensity `location2+r300y` patterns. Transfer to other cities, rainfall regimes, grid resolutions, drainage systems, or hydrodynamic configurations would require additional validation and possibly retraining or recalibration.

Operationally, the surrogate should support hydrodynamic modeling rather than replace it. A rapid surrogate can provide fast situational awareness, screening, and preliminary spatial warning context. Hydrodynamic simulation remains the reference modeling approach for scenario design, validation, high-risk confirmation, and high-stakes decisions. The value of the reliability-aware layer is that it indicates when surrogate output can be used as a rapid reference, when targeted review is required, and when additional hydrodynamic or expert evidence is necessary.

Future work should add literature citations, verify the study-area and dataset descriptions, select final main and supplementary figures, and test the framework under broader independent scenarios. Methodological extensions could include calibrated uncertainty only under a dedicated calibration protocol, targeted improvements for false-dry and peak-depth underprediction, and operational workflows that couple surrogate screening with hydrodynamic confirmation.

## 11. Conclusions

1. This study frames rapid urban flood surrogate prediction as a reliability-aware warning-support problem. The U-Net + TCN surrogate provides fast multi-step flood-depth prediction from past flood states, rainfall forcing, and static spatial inputs, but warning interpretation requires more than aggregate accuracy.

2. The fixed Phase 10 model basis is retained with `boundary_band_pixels = 1` and `boundary_weight = 2.0`. Phases 12-22 use this setting for diagnosis and manuscript synthesis; they do not retrain the model, modify the architecture, modify the Phase 10 loss, tune boundary parameters, or open a new sweep.

3. Reliability is nonuniform across the tested evidence. Key caution zones include exact wet/dry boundary cells, shallow threshold-adjacent cells, moderate-to-deep depths, local peak-depth extremes, and high-intensity `location2` scenarios.

4. Representative failures are structured and warning-relevant. The dominant severe failure modes include systematic underprediction, wet-area contraction, local peak-depth underprediction, and false-dry dominated mismatch in repeated high-intensity `location2+r300y` cases.

5. The reliability-aware warning layer converts diagnostic evidence into deterministic scenario labels, pixel risk maps, warning rules, and applicability-boundary guidance. Phase 15 and Phase 16 preserve consistent reliable, caution, and high-risk counts and capture Phase 13-like `location2+r300y` cases as caution or high-risk.

6. The framework supports transparent use of rapid surrogate predictions within the tested scenario space. It does not provide calibrated probabilistic uncertainty, universal generalization, or a replacement for hydrodynamic modeling in high-stakes decisions.

## 12. Figure and table placeholders

Planned main-text figures, aligned with the Phase 21 evidence map:

- Fig. 1. Study area and prediction workflow. Source: final study-area/workflow schematic to be selected or drafted. Purpose: introduce hydrodynamic reference outputs, surrogate inputs, static layers, rainfall forcing, and prediction horizon. [figure to be finalized]
- Fig. 2. U-Net + TCN surrogate and reliability-aware warning framework. Source: model/framework overview and Phase 17 synthesis. Purpose: show the fixed surrogate plus post-prediction reliability and warning layer. [figure to be finalized]
- Fig. 3. Representative base prediction performance. Source: official Phase 10 evaluation outputs. Purpose: establish base prediction behavior before reliability analysis. [figure to be finalized]
- Fig. 4. Reliability varies by wet/dry boundary distance and depth range. Source: `analysis/phase12_reliability/figures/boundary_distance_class_error.png` and `analysis/phase12_reliability/figures/depth_bin_error_comparison.png`.
- Fig. 5. Representative systematic failure case. Source: `analysis/phase13_failure_cases/figures/rank01_seed42_location2_r300y_p06_d3h_start0_t01_worst_maps.png`.
- Fig. 6. Confidence margin as wet/dry classification risk proxy. Source: `analysis/phase14_confidence/figures/confidence_margin_vs_wet_dry_error.png`.
- Fig. 7. Scenario reliability-screening category counts. Source: `analysis/phase15_reliability_screening/figures/scenario_risk_category_counts.png`.
- Fig. 8. Risk component heatmap. Source: `analysis/phase15_reliability_screening/figures/risk_component_heatmap.png`.
- Fig. 9. Pixel-level risk map example. Source: `analysis/phase15_reliability_screening/figures/pixel_risk_map_example.png`.
- Fig. 10. Warning action matrix. Source: `analysis/phase16_warning_rules/figures/warning_action_matrix.png`.
- Fig. 11. Applicability boundary summary. Source: `analysis/phase16_warning_rules/figures/applicability_boundary_summary.png`.

Planned supplementary figures:

- Fig. S1. Seed-level reliability overview. Source: `analysis/phase12_reliability/figures/seed_level_overview.png`.
- Fig. S2. Timestep RMSE and MAE trend. Source: `analysis/phase12_reliability/figures/timestep_rmse_mae_trend.png`.
- Fig. S3. Depth-bin bias comparison. Source: `analysis/phase12_reliability/figures/depth_bin_bias_comparison.png`.
- Fig. S4. Scenario RMSE versus target wet fraction. Source: `analysis/phase12_reliability/figures/scenario_scatter_rmse_vs_target_wet_fraction.png`.
- Fig. S5. Top failure cases by RMSE. Source: `analysis/phase12_reliability/figures/top_failure_cases_rmse.png`.
- Fig. S6. Additional `location2+r300y` representative failure cases. Source: additional Phase 13 failure-case maps listed in the Phase 21 alignment.
- Fig. S7. Cross-seed disagreement versus RMSE. Source: `analysis/phase14_confidence/figures/seed_disagreement_vs_rmse.png`.
- Fig. S8. Scenario risk score distribution. Source: `analysis/phase15_reliability_screening/figures/scenario_risk_score_distribution.png`.
- Fig. S9. Repeated false-dry pixel risk. Source: `analysis/phase15_reliability_screening/figures/repeated_false_dry_pixel_risk.png`.
- Fig. S10. Pixel warning map example. Source: `analysis/phase16_warning_rules/figures/pixel_warning_map_example.png`.
- Fig. S11. Warning-level counts. Source: `analysis/phase16_warning_rules/figures/warning_level_counts.png`.
- Fig. S12. High-risk warning case distribution. Source: `analysis/phase16_warning_rules/figures/high_risk_warning_case_distribution.png`.

Planned tables:

- Table 1. Dataset and scenario summary. Source: dataset metadata to be verified. Purpose: summarize domain, train/test split, rainfall scenarios, static inputs, `input_steps = 12`, and `pred_steps = 12`. [table to be finalized]
- Table 2. Model configuration and Phase 10 recommended setting. Source: Phase 10 basis summarized in Phase 12 and Phase 17. Purpose: preserve `boundary_band_pixels = 1` and `boundary_weight = 2.0`.
- Table 3. Reliability-screening rule summary. Source: Phase 15 summary and screening outputs. Purpose: define deterministic screening components.
- Table 4. Warning action matrix. Source: Phase 16 warning rules and action matrix. Purpose: define reliable, caution, and high-risk operational interpretation.
- Table 5. Applicability boundary table. Source: Phase 16 applicability-boundary table and summary figure. Purpose: summarize stronger-use conditions, caution zones, and high-risk conditions.
- Table 6. Quantitative summary of Phase 15 and Phase 16 outputs. Source: Phase 15 and Phase 16 summary files and findings documents. Purpose: compactly report the preserved screening and warning counts.

## 13. Limitations and non-claims

- No calibrated probabilistic uncertainty is claimed.
- Confidence margin is a wet/dry classification risk proxy, not a full depth-error uncertainty estimate.
- Warning labels are deterministic operational interpretation labels.
- Cross-seed disagreement is auxiliary and should not be treated as a strong standalone scenario-error predictor.
- The surrogate does not replace hydrodynamic simulation in high-stakes decisions.
- Generalization is limited to the tested scenario space, data, locations, rainfall events, model configuration, and evaluation protocol.
- Reliable, caution, and high-risk labels are not predictive probabilities, Bayesian posterior estimates, calibrated confidence intervals, formal uncertainty bounds, or guaranteed error limits.
- High-risk cases require conservative interpretation, targeted expert review, hydrodynamic-model confirmation, or other operational evidence before high-stakes use.
- Phases 12-22 did not retrain the model, modify architecture, modify Phase 10 loss, tune `boundary_weight` or `boundary_band_pixels`, or open a new sweep.

## 14. Immediate revision tasks

Before this manuscript can become submission-ready, the following tasks remain:

1. Add literature citations for urban pluvial flood warning, hydrodynamic simulation cost, deep learning flood surrogates, uncertainty/reliability interpretation, and warning decision support.
2. Verify final study area, hydrodynamic model, dataset, scenario, static-input, and train/test wording.
3. Select final main figures and supplementary figures from the Phase 21 candidate inventory.
4. Finalize figure captions and tables using only existing evidence and verified quantitative facts.
5. Insert final equations for metrics and physically informed loss components.
6. Adapt formatting, section order, length, references, figure limits, and supplementary policy to a target journal.
7. Refine the abstract and conclusions after final figures, tables, and citations are selected.
