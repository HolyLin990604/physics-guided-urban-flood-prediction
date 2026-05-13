# Reliability-Aware Deep Learning Surrogate Framework for Rapid Urban Flood Warning

## 1. Title

Working title:

# Reliability-Aware Deep Learning Surrogate Framework for Rapid Urban Flood Warning

Alternative title options:

- From Rapid Flood Prediction to Reliability-Aware Urban Flood Warning: A Deep Learning Surrogate Framework
- Reliability Screening and Spatial Risk Mapping for Deep Learning Surrogate Urban Flood Prediction
- Physics-Guided Urban Flood Surrogate Prediction with Deterministic Warning Guidance

## 2. Abstract Draft

This abstract is a draft skeleton and is not final.

Urban flood warning requires timely spatial information on flood-depth evolution to support situational awareness, emergency response, and operational decision support. Physics-based hydrodynamic simulations provide physically credible reference information, but their computational cost can limit repeated or near-real-time use across rainfall scenarios and forecast updates [literature to be added]. Deep learning surrogate models offer a path toward rapid flood-depth prediction, but prediction-only surrogates are insufficient for warning use when aggregate accuracy does not identify where predictions are reliable, where wet/dry classification is sensitive, or where severe failures may occur.

This study develops a reliability-aware deep learning surrogate framework for rapid urban flood warning. The framework combines a U-Net + TCN multi-step flood-depth surrogate with physically informed prediction refinements and a post-prediction reliability-aware warning layer. The model is built for the UrbanFlood24 Lite setting, using past flood-depth sequences, past and future rainfall forcing, and static spatial inputs to predict future flood-depth fields. The reliability layer diagnoses applicability across timesteps, depth ranges, wet/dry boundary zones, scenario types, representative failure cases, confidence-margin behavior, deterministic risk screening, spatial risk mapping, and warning-rule interpretation.

The Phase 10 recommended model setting is retained with `boundary_band_pixels = 1` and `boundary_weight = 2.0`. In the reliability-screening stage, Phase 15 loaded 57 Phase 10 map files, generated 114 scenario-level risk records and 16384 pixel-level risk records, and assigned 76 records to reliable, 25 to caution, and 13 to high-risk. Phase 13-like location2+r300y cases were flagged as caution or high-risk in 24/24 cases. In the warning-rule stage, Phase 16 produced scenario warnings of reliable=76, caution=25, and high-risk=13; pixel warnings of reliable=5714, caution=8805, and high-risk=1865; and 13 high-risk warning cases, matching the Phase 15 high-risk cases.

These results support a warning-oriented interpretation of rapid surrogate predictions: the model can provide fast flood-depth references within the tested scenario space, while deterministic reliability labels, pixel risk maps, and applicability-boundary guidance indicate when targeted review or non-standalone use is required. The framework does not claim calibrated probabilistic uncertainty, universal generalization, or replacement of hydrodynamic modeling in high-stakes decisions.

## 3. Keywords

Urban flood warning; deep learning surrogate; reliability screening; flood-depth prediction; physics-guided learning; spatial risk mapping; applicability boundary

## 4. Introduction Draft

### 4.1 Urban flood warning challenge

Urban flooding can evolve rapidly across complex built environments, making spatially distributed flood-depth information important for warning, response planning, and situational awareness. Operational users need not only an estimate of inundation extent and depth, but also timely information about where the prediction is credible enough to guide interpretation. The warning context therefore places pressure on both speed and reliability [literature to be added].

### 4.2 Hydrodynamic model credibility and computational cost

Hydrodynamic flood models remain important because they encode process-based representations of rainfall-runoff, flow routing, topographic controls, and inundation dynamics. In this study, hydrodynamic simulation outputs are treated as the data-generating reference for training and evaluating the surrogate. However, repeated high-resolution simulation across many rainfall scenarios, forecast windows, or decision cycles may be computationally expensive, motivating fast approximation tools [literature to be added].

### 4.3 Deep learning surrogate potential and limitation

Deep learning surrogates can approximate spatiotemporal flood-depth fields at much lower inference cost than full hydrodynamic simulation. A U-Net + TCN architecture is suitable for this task because it can combine spatial encoding-decoding with temporal conditioning. Nevertheless, a surrogate framed only around aggregate prediction accuracy can hide important warning-relevant weaknesses. Errors near wet/dry boundaries, missed inundation, peak-depth underprediction, and scenario-specific failures may matter more operationally than small changes in average error metrics.

### 4.4 Need for reliability diagnosis and applicability boundary

For warning-oriented use, the central question is not only what the surrogate predicts, but also when and where the prediction should be trusted. Reliability diagnosis is needed to identify caution zones, failure modes, and applicability boundaries. In this manuscript, reliability is treated as deterministic diagnostic evidence derived from prediction behavior, confidence-margin proximity to the wet/dry threshold, screening labels, and spatial risk maps. It is not treated as calibrated probabilistic uncertainty.

### 4.5 Contribution of this study

This study contributes a reliability-aware deep learning surrogate framework for rapid urban flood warning. The contribution is not a new hydrodynamic model and not a claim that a surrogate should replace process-based simulation in high-stakes decisions. Instead, the study assembles rapid flood-depth prediction, physics-guided prediction refinement, reliability/applicability diagnosis, representative failure-mode interpretation, deterministic screening, pixel-level risk mapping, and warning-rule guidance into a single manuscript framework.

## 5. Study Area and Dataset

This section is a draft skeleton. Project-specific study-area details, map resolution, domain extent, scenario construction, and final dataset statistics should be verified before submission.

### 5.1 Urban flood prediction setting

The study addresses multi-step urban flood-process prediction in the UrbanFlood24 Lite setting. The task is to predict future flood-depth fields over an urban domain from observed or simulated past flood states, rainfall forcing, and static spatial descriptors. The warning-oriented objective is to produce rapid spatial flood-depth information while also identifying the reliability limits of the surrogate prediction.

### 5.2 Hydrodynamic simulation outputs

Hydrodynamic simulations provide the reference flood-depth sequences used for model training, evaluation, and reliability analysis. These outputs are treated as the benchmark representation of flood-process evolution within the tested scenario design. Details of the hydrodynamic model setup, numerical configuration, boundary conditions, rainfall design, and validation basis should be added here after final verification [hydrodynamic model details to be added].

### 5.3 Flood-depth maps

The dynamic target variable is flood depth, stored as gridded flood-depth sequences. The current project setup uses `flood.npy` files and a multi-step prediction task with `input_steps = 12` and `pred_steps = 12`. The manuscript should later report the spatial resolution, temporal interval, depth units, and preprocessing steps [details to be verified].

### 5.4 Static spatial inputs

Static geospatial inputs include digital elevation, imperviousness, and manhole-related spatial information. In the current dataset layout, these inputs are represented by `absolute_DEM.npy`, `impervious.npy`, and `manhole.npy`. These static maps provide topographic and urban-surface context for the surrogate model. Final manuscript text should describe their source, resolution, normalization, and physical interpretation [static-map metadata to be added].

### 5.5 Rainfall and scenario inputs

Rainfall forcing is represented by `rainfall.npy` and is used both as past rainfall context and future rainfall conditioning. The scenario set includes different rainfall and location conditions, including high-intensity `location2` and `r300y` cases identified in the reliability analysis. Final scenario definitions, return-period notation, storm durations, and rainfall temporal patterns should be documented here [rainfall scenario table to be added].

### 5.6 Train/test scenario context

The dataset is organized into train and test partitions under `data/urbanflood24_lite/train/` and `data/urbanflood24_lite/test/`. The manuscript should clarify the train/test split logic, scenario independence, seed usage, and whether test cases represent interpolation within the scenario design or more difficult extrapolative conditions [split protocol to be verified].

## 6. Hydrodynamic Simulation and Surrogate Model

### 6.1 Hydrodynamic model role

The hydrodynamic model is used as the reference data generator and evaluation basis. It defines the target flood-depth fields that the surrogate learns to approximate. The surrogate should therefore be interpreted as a rapid approximation tool trained against hydrodynamic outputs, not as a replacement for hydrodynamic simulation in high-stakes decision-making.

[Equation placeholder: governing hydrodynamic model or process description, if included in final manuscript.]

### 6.2 U-Net + TCN surrogate architecture

The surrogate model uses a U-Net + TCN style spatiotemporal architecture. The U-Net component encodes static maps and spatial flood patterns, while the temporal convolutional module supports multi-step temporal representation. The decoder produces future flood-depth fields over the prediction horizon.

[Figure placeholder: Fig. 2 Surrogate model architecture.]

### 6.3 Temporal rainfall conditioning

The model conditions prediction on rainfall information, including past rainfall context and future rainfall forcing. The current project history includes optional architecture-level rainfall conditioning modules, with the active adaptive candidate before margin-aware refinement represented by the Phase 7/8 `adapt010` setting. Final manuscript text should describe the exact configuration used in the Phase 10 recommended model without reopening architecture comparison [model configuration table to be added].

### 6.4 Predicted future flood-depth fields

Given past flood-depth sequences, rainfall forcing, and static spatial inputs, the surrogate predicts a sequence of future flood-depth maps. In the current setup, `input_steps = 12` and `pred_steps = 12`. The output is evaluated against hydrodynamic reference flood-depth fields for each predicted timestep.

### 6.5 Evaluation metrics

Prediction performance should be reported using the established project metrics, including regression error and wet/dry classification-oriented measures where appropriate. Final manuscript equations and definitions should be added for RMSE, MAE, wet/dry IoU or related classification metrics, false-dry rate, wet fraction, and any reliability-screening components used in the Results section.

[Equation placeholder: prediction metrics.]

## 7. Physics-Guided Prediction Framework

### 7.1 Physically informed losses and constraints

The surrogate framework incorporates physically informed prediction refinements at the output level. These refinements are intended to improve physical plausibility and warning relevance while preserving the surrogate architecture and training workflow. They should be described as physics-guided or physically informed constraints, not as a full replacement for hydrodynamic governing equations.

### 7.2 Non-negativity

Flood depth is physically non-negative. The non-negativity loss discourages negative predicted depths and supports physically plausible output fields.

[Equation placeholder: non-negativity loss.]

### 7.3 Wet/dry consistency

Wet/dry consistency addresses the classification of cells relative to a wet/dry threshold. This is important because small errors near the threshold can change whether a cell is interpreted as inundated. The wet/dry consistency component supports more consistent threshold behavior while retaining the continuous flood-depth prediction task.

[Equation placeholder: wet/dry consistency loss.]

### 7.4 Rainfall-depth consistency

Rainfall-depth consistency connects rainfall forcing and predicted flood-depth response. This component should be described in the final manuscript using the implemented project formulation and any relevant assumptions [exact formulation to be verified].

[Equation placeholder: rainfall-depth consistency.]

### 7.5 Topographic regularization

Topographic regularization should describe how static terrain or spatial context constrains or informs flood-depth prediction. Final wording should align with the implemented project components and should avoid implying unsupported hydrodynamic guarantees [exact implementation details to be verified].

[Equation placeholder: topographic regularization or spatial regularization.]

### 7.6 Phase 10 recommended margin-aware setting

Phase 10 introduced a minimal diagnosis-driven boundary-band refinement to the wet/dry consistency component. The current recommended setting is fixed as:

```text
boundary_band_pixels = 1
boundary_weight = 2.0
```

This setting is used as the model basis for the reliability-oriented phases. It should be presented as the retained Phase 10 configuration, not as a parameter tuning exercise reopened in this manuscript draft.

## 8. Reliability-Aware Warning Layer

### 8.1 Framework overview

The reliability-aware warning layer is an application-oriented interpretation layer built around the fixed surrogate model. It does not modify the trained model architecture, loss formulation, or prediction procedure. Instead, it interprets surrogate outputs after prediction and translates diagnostic evidence into deterministic scenario-level labels, pixel-level risk maps, warning-rule guidance, and an applicability-boundary summary.

The layer follows a five-step chain: reliability and applicability diagnosis; representative failure-case interpretation; confidence and disagreement proxy diagnostics; reliability screening and spatial risk mapping; and warning-rule and applicability-boundary guidance. This chain corresponds to the Phase 12 through Phase 16 reliability work.

### 8.2 Reliability and applicability diagnosis

Reliability diagnosis evaluates the Phase 10 recommended model across forecast timesteps, target depth ranges, wet/dry boundary-distance zones, scenario types, and repeated seed runs. This diagnosis is distinct from aggregate model evaluation. Its purpose is to identify where errors occur, whether they have physical or scenario-dependent structure, and how these patterns affect warning interpretation.

The established caution zones include exact wet/dry boundary cells, shallow threshold-adjacent cells, moderate-to-deep depths, high-intensity `location2` scenarios, and local peak-depth extremes. These conditions define the main applicability-boundary evidence for the current surrogate within the tested scenario space.

### 8.3 Failure-mode interpretation

Representative failure-case analysis translates high-error cases into visual and quantitative interpretation. The most severe failures are systematic rather than random. They concentrate in high-intensity `location2` target scenarios, especially repeated `location2` + `r300y` cases across seeds.

The dominant failure modes include systematic underprediction, reduced predicted wet fraction, local peak-depth underprediction, and false-dry dominated wet/dry mismatch. These patterns are warning-relevant because they can underestimate inundation extent or severity, especially in high-intensity cases.

[Figure placeholder: Fig. 5 Representative failure-case visualization.]

### 8.4 Confidence margin as wet/dry classification risk proxy

The confidence-margin diagnostic is defined conceptually as:

```text
confidence_margin = abs(prediction - wet_threshold)
```

with `wet_threshold = 0.05`.

A low confidence margin means that the predicted depth lies near the wet/dry threshold. Such cells have higher wet/dry classification risk because small depth errors can change the interpreted state from dry to wet or wet to dry. Confidence margin is therefore used as a wet/dry classification risk proxy.

This proxy is not calibrated probabilistic uncertainty. It is not a probability of error, Bayesian posterior uncertainty, a confidence interval, or a full depth-error uncertainty estimate. A cell can have a high wet/dry confidence margin while still having substantial depth-magnitude error, particularly in moderate-to-deep or local peak-depth regions.

### 8.5 Deterministic reliability screening

The reliability-screening component converts diagnostic evidence into deterministic labels. Screening components include low confidence-margin risk, false-dry risk, wet-fraction contraction, peak-depth underprediction, mean underprediction bias, boundary-zone false-dry risk, high-intensity `location2` metadata risk, and auxiliary cross-seed disagreement.

The labels reliable, caution, and high-risk are deterministic operational interpretation labels. They are not calibrated probabilities, Bayesian posterior estimates, formal confidence intervals, or guaranteed error bounds.

### 8.6 Spatial risk mapping

Pixel-level risk mapping extends reliability interpretation from scenario labels to spatially explicit warning support. Risk maps indicate where the surrogate output is more likely to require caution, especially near wet/dry boundaries, repeated false-dry regions, threshold-adjacent pixels, and areas associated with severe underprediction.

[Figure placeholder: Fig. 8 Pixel risk map and warning action matrix.]

### 8.7 Warning-rule and applicability-boundary guidance

The warning-rule layer translates deterministic labels into application guidance:

| Warning level | Operational interpretation |
|---|---|
| reliable | use as rapid prediction reference |
| caution | use with targeted review |
| high-risk | do not use alone for warning decisions |

Reliable cases fall within the stronger current applicability range and may support rapid situational awareness with normal review. Caution cases remain useful but require targeted inspection of sensitive areas, such as wet/dry boundaries, threshold-adjacent zones, local peak-depth regions, and pixel-level risk maps. High-risk cases should trigger conservative interpretation and should not be used alone for warning decisions; they require hydrodynamic-model confirmation, expert review, or other operational evidence.

## 9. Results Draft

This section is a structured results skeleton. It should be completed with final figures, tables, and concise quantitative descriptions drawn only from existing verified outputs.

### 9.1 Prediction performance overview

The first results subsection should establish the baseline surrogate prediction performance before introducing reliability interpretation. It should report the established regression and wet/dry classification metrics for the Phase 10 recommended setting, with representative predicted and reference flood-depth maps.

[Result placeholder: quantitative performance table from official evaluation outputs.]

[Figure placeholder: Fig. 3 Prediction performance examples.]

### 9.2 Reliability and applicability diagnosis results

Reliability diagnosis should report how model behavior varies across timestep, depth range, wet/dry boundary distance, scenario type, and seed. The expected manuscript message is that the Phase 10 recommended model is useful for rapid spatiotemporal flood-process approximation under the tested scenario set, but reliability is nonuniform.

Key diagnostic interpretation to preserve:

- exact wet/dry boundary cells are a major reliability bottleneck;
- shallow threshold-adjacent cells require caution because small depth errors can change wet/dry state;
- moderate-to-deep target depths show stronger underprediction;
- high-intensity `location2` cases dominate the highest-ranked failures;
- local peak-depth extremes remain warning-relevant caution zones.

[Figure placeholder: Fig. 4 Reliability diagnosis plots.]

### 9.3 Representative failure-case analysis

Representative failure-case analysis should show that severe errors are structured and scenario-dependent rather than isolated random failures. The top failure patterns collapse into high-intensity `location2` target scenarios repeated across seeds, especially `location2+r300y` cases.

The manuscript should describe the visual failure modes as systematic underprediction, reduced predicted wet fraction, local peak-depth underprediction, and false-dry dominated mismatch. These patterns motivate the later high-risk warning interpretation.

[Figure placeholder: Fig. 5 Representative failure-case visualization.]

### 9.4 Confidence proxy results

The confidence proxy results should present confidence margin as a wet/dry classification risk proxy. Low-margin cells near `wet_threshold = 0.05` should be interpreted as classification-sensitive areas. Cross-seed disagreement may be reported only as an auxiliary disagreement signal and should not be presented as a strong standalone scenario-error predictor.

[Figure placeholder: Fig. 6 Confidence proxy diagnostics.]

### 9.5 Reliability screening and risk mapping results

Phase 15 converted the diagnostic evidence into deterministic scenario-level and pixel-level screening outputs. The following exact facts should be preserved:

- Phase 15: 57 Phase 10 map files loaded
- Phase 15: 114 scenario-level risk records
- Phase 15: 16384 pixel-level risk records
- Phase 15: 76 reliable, 25 caution, 13 high-risk
- Phase 15: Phase 13-like location2+r300y cases 24/24 flagged as caution/high-risk

These counts indicate that the screening layer can attach deterministic reliability interpretation to surrogate predictions and that the known Phase 13-like high-intensity failure cases are captured by caution or high-risk labels.

[Figure placeholder: Fig. 7 Scenario risk category counts and risk component heatmap.]

### 9.6 Warning-rule and applicability-boundary results

Phase 16 translated Phase 15 labels into warning guidance and an applicability-boundary summary. The following exact facts should be preserved:

- Phase 16: scenario warnings reliable=76, caution=25, high-risk=13
- Phase 16: pixel warnings reliable=5714, caution=8805, high-risk=1865
- Phase 16: high-risk warning cases=13, matching Phase 15 high-risk cases

These results support the operational interpretation that reliable predictions can be used as rapid references, caution predictions require targeted review, and high-risk predictions should not be used alone for warning decisions.

[Figure placeholder: Fig. 8 Pixel risk map and warning action matrix.]

## 10. Discussion Draft

### 10.1 Beyond prediction accuracy

The results indicate that rapid surrogate prediction should not be evaluated only through aggregate accuracy. For warning-oriented use, reliability depends on where errors occur, whether they affect wet/dry classification, whether they underestimate flood extent or peak depth, and whether they cluster in known scenario conditions.

### 10.2 False-dry and wet/dry boundary risks

False-dry errors are operationally important because they can hide inundation rather than merely perturb a continuous depth estimate. Wet/dry boundary cells are also sensitive because small depth errors near the threshold can alter interpreted inundation extent. These risks justify explicit boundary-aware diagnosis and pixel-level caution mapping.

### 10.3 Deterministic labels versus probabilistic uncertainty

The reliable, caution, and high-risk labels are deterministic operational interpretation labels. They should not be read as calibrated probabilities, Bayesian uncertainty estimates, formal confidence intervals, or guaranteed error bounds. Confidence margin is useful as a wet/dry classification risk proxy, but it is not a full depth-error uncertainty estimate.

### 10.4 Applicability boundary and operational interpretation

The framework defines an applicability boundary for the current surrogate within the tested scenario space. Ordinary cases without strong risk components can support rapid reference use. Caution cases require targeted review of sensitive pixels, local peaks, and boundary zones. High-risk cases, especially repeated high-intensity `location2+r300y` patterns, should not be used alone for warning decisions.

### 10.5 Relationship to hydrodynamic modeling

The surrogate should be interpreted as a rapid approximation and screening tool trained against hydrodynamic outputs. Hydrodynamic simulation remains the reference modeling approach, especially for high-stakes decisions, severe high-risk cases, model confirmation, scenario design, and future validation. The reliability-aware warning layer clarifies when surrogate output requires additional evidence rather than replacing hydrodynamic modeling.

### 10.6 Transferability and scenario-space limitations

The present evidence is limited to the tested data, locations, rainfall scenarios, model configuration, and evaluation protocol. The manuscript should avoid universal generalization claims. Transfer to other cities, rainfall regimes, grid resolutions, drainage systems, or hydrodynamic model settings would require additional validation and possibly recalibration or retraining.

### 10.7 Future work

Future work should include broader external validation, formal calibration design if probabilistic uncertainty is needed, additional testing under independent storm scenarios, operational coupling with hydrodynamic confirmation workflows, and targeted model improvement for false-dry risk, peak-depth underprediction, and high-intensity scenario failures. Any calibrated uncertainty claim should be introduced only through a separate calibration dataset and evaluation protocol.

## 11. Conclusions Draft

This manuscript draft frames the project as a reliability-aware surrogate framework for rapid urban flood warning rather than a prediction-only model.

The U-Net + TCN surrogate provides rapid multi-step flood-depth prediction using past flood states, rainfall forcing, and static spatial inputs. The Phase 10 recommended margin-aware setting is retained with `boundary_band_pixels = 1` and `boundary_weight = 2.0`.

Reliability diagnosis shows that model performance is not spatially or physically uniform. Key caution zones include wet/dry boundaries, shallow threshold-adjacent cells, moderate-to-deep depths, local peak-depth extremes, and high-intensity `location2` scenarios.

The reliability-aware warning layer converts diagnostic evidence into deterministic scenario labels, pixel risk maps, warning rules, and applicability-boundary guidance. Phase 15 and Phase 16 results preserve consistent reliable, caution, and high-risk counts and capture known Phase 13-like `location2+r300y` cases as caution or high-risk.

The framework supports warning-oriented decision support by indicating when surrogate predictions may be used as rapid references, when targeted review is needed, and when outputs should not be used alone. It does not provide calibrated probabilistic uncertainty, universal generalization, or a replacement for hydrodynamic simulation in high-stakes decisions.

## 12. Figure and Table Placeholders

Figure placeholders:

- Fig. 1 Study area and workflow
- Fig. 2 Surrogate model architecture
- Fig. 3 Prediction performance examples
- Fig. 4 Reliability diagnosis plots
- Fig. 5 Representative failure-case visualization
- Fig. 6 Confidence proxy diagnostics
- Fig. 7 Scenario risk category counts and risk component heatmap
- Fig. 8 Pixel risk map and warning action matrix

Table placeholders:

- Table 1 Dataset/scenario summary
- Table 2 Model settings and Phase 10 configuration
- Table 3 Reliability-screening and warning-rule summary
- Table 4 Applicability boundary table

## 13. Contribution Summary

- This study develops a rapid urban flood surrogate prediction framework for multi-step flood-depth mapping using a U-Net + TCN architecture.
- The surrogate is paired with physically informed prediction refinements, including the fixed Phase 10 margin-aware wet/dry setting, to support more physically plausible flood-process approximation.
- The study diagnoses reliability and applicability boundaries across timesteps, depth ranges, wet/dry boundary zones, scenario types, failure cases, and repeated seeds.
- The framework converts reliability evidence into deterministic scenario-level screening labels and pixel-level spatial risk maps.
- The warning layer translates reliable, caution, and high-risk labels into operational guidance for rapid reference use, targeted review, and non-standalone use in high-risk cases.
- The contribution is an integrated reliability-aware interpretation framework around a rapid surrogate, rather than a claim of universal generalization or calibrated probabilistic uncertainty.

## 14. Limitations and Non-Claims

- No calibrated probabilistic uncertainty is claimed.
- Confidence margin is a wet/dry classification risk proxy.
- Warning labels are deterministic operational interpretation labels.
- The surrogate does not replace hydrodynamic simulation in high-stakes decisions.
- Generalization is limited to the tested scenario space.
- Phases 12-20 did not retrain the model, modify architecture, modify Phase 10 loss, tune `boundary_weight` or `boundary_band_pixels`, or open a new sweep.
- Confidence margin should not be interpreted as a probability of error, Bayesian posterior uncertainty, calibrated confidence interval, or full depth-error uncertainty estimate.
- Reliable, caution, and high-risk labels should not be interpreted as guaranteed error bounds.
- High-risk cases require conservative interpretation, targeted expert review, hydrodynamic-model confirmation, or other operational evidence before high-stakes use.
