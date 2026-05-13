# Reliability-Aware Warning Layer for Urban Flood Surrogate Prediction

## 1. Manuscript positioning

This manuscript section describes an application-oriented reliability-aware warning layer built on top of the trained urban flood surrogate model. The layer is intended to support operational interpretation of rapid flood-depth predictions by identifying where predictions are more reliable, where caution is required, and where the surrogate output should not be used alone for warning decisions.

The warning layer does not replace the prediction model. It also does not alter the trained model architecture, loss formulation, or prediction procedure. Instead, it interprets and screens the surrogate outputs after prediction, translating model fields into deterministic scenario-level risk labels, pixel-level risk maps, and warning-rule guidance.

In manuscript terms, the contribution should therefore be positioned as a reliability-aware use layer for an existing rapid surrogate, rather than as a new model-training phase or a new hydrodynamic simulator.

## 2. Methodological motivation

Rapid flood-depth prediction is necessary but insufficient for warning applications. A prediction map can provide fast spatial information, but warning-oriented use also requires knowledge of when that map can be trusted, where interpretation is sensitive, and where additional review is required before decisions are made.

The reliability-aware warning layer is motivated by five operational needs. First, users need to know where predictions are reliable enough to serve as rapid references. Second, wet/dry boundary regions require explicit caution because small depth errors can change the predicted inundation state. Third, false-dry risks must be identified because missed inundation can be more consequential than small continuous-depth error. Fourth, high-intensity scenarios may exceed the strongest applicability range of the trained surrogate, especially when localized peak depths and wet-area expansion are underpredicted. Fifth, prediction outputs must be translated into warning guidance that distinguishes ordinary use, targeted review, and non-standalone use.

This framing shifts the manuscript narrative from rapid prediction alone to rapid prediction with explicit reliability interpretation.

## 3. Framework design

The reliability-aware warning framework is organized as a five-step chain:

1. reliability and applicability diagnosis;
2. representative failure-case interpretation;
3. confidence/disagreement proxy diagnostics;
4. automatic reliability screening and spatial risk mapping;
5. warning-rule and applicability-boundary guidance.

These steps correspond directly to Phases 12 through 16. Phase 12 diagnoses reliability across timesteps, depth ranges, boundary-distance zones, scenarios, and seeds. Phase 13 interprets representative high-error cases and identifies structured failure modes. Phase 14 evaluates deterministic confidence and disagreement proxies, with confidence margin used as a wet/dry classification risk proxy. Phase 15 converts the diagnostic evidence into deterministic scenario-level and pixel-level reliability labels. Phase 16 translates those labels into warning actions and an applicability-boundary summary.

Together, these components form an interpretation layer around the fixed surrogate model. The framework preserves the speed of the trained predictor while adding deterministic reliability screening for application-facing use.

## 4. Reliability diagnosis component

The reliability diagnosis evaluates the surrogate output across forecast timesteps, target depth ranges, wet/dry boundary-distance zones, scenario types, and repeated seed runs. This diagnostic view is distinct from aggregate model evaluation: its purpose is to identify where errors occur and how they relate to physical or operational conditions.

The diagnosis shows that the surrogate is useful for rapid spatiotemporal flood-process approximation under the tested scenario set, but its reliability is not spatially or physically uniform. Known caution zones include exact wet/dry boundary cells, shallow threshold-adjacent cells, moderate-to-deep depths, high-intensity `location2` scenarios, and local peak-depth extremes.

These zones have different reliability meanings. Exact wet/dry boundary cells and shallow threshold-adjacent cells are sensitive to classification changes near the wet/dry threshold. Moderate-to-deep cells and local peak-depth extremes are more closely associated with depth-magnitude underprediction. High-intensity `location2` scenarios indicate a scenario-level applicability limit in which localized severe inundation and wet-area expansion may be underestimated.

## 5. Failure-mode interpretation component

The representative failure-case analysis converts the highest-ranked diagnostic failures into visual and quantitative interpretation. Rather than treating failures as isolated random errors, this component examines whether severe failures share common scenario conditions and spatial error patterns.

The most severe failures are systematic rather than random. They concentrate in high-intensity `location2` target scenarios, especially repeated `location2` + `r300y` cases across seeds. This repetition indicates a structured applicability limit: multiple trained seeds can fail in similar ways when the target scenario contains intense localized inundation.

The observed failure modes are systematic underprediction, reduced predicted wet fraction, local peak-depth underprediction, and false-dry dominated mismatch. These patterns show that the main severe failures are not only small boundary classification errors. They also involve underestimated flood extent and underestimated high-depth regions, which are directly relevant to warning interpretation.

## 6. Confidence proxy component

The confidence proxy component evaluates whether deterministic output-space signals can help identify wet/dry classification risk. The primary proxy is confidence margin, defined conceptually as:

```text
confidence_margin = abs(prediction - wet_threshold)
```

with `wet_threshold = 0.05`.

A low confidence margin means that the predicted depth lies close to the wet/dry decision threshold. Such cells have higher wet/dry classification risk because small depth errors can change the predicted state from dry to wet or wet to dry. The confidence-margin diagnostic is therefore useful for identifying threshold-adjacent areas where classification should be interpreted cautiously.

This proxy is not calibrated probabilistic uncertainty. It should not be described as a probability of error, Bayesian posterior uncertainty, a confidence interval, or a complete depth-error uncertainty measure. A cell can have a high wet/dry confidence margin while still exhibiting substantial depth-magnitude error, particularly in moderate-to-deep or local peak-depth regions.

Cross-seed disagreement is included only as an auxiliary disagreement signal. It can indicate some prediction variability across seeds, but it is not a strong standalone scenario-error predictor because multiple seeds can fail similarly on the same high-intensity cases.

## 7. Reliability screening and spatial risk mapping component

Phase 15 converts the diagnostic evidence into deterministic scenario-level and pixel-level reliability labels. This component takes evidence from reliability diagnosis, representative failure-case interpretation, and confidence proxy diagnostics, then assigns screening labels that can be attached to surrogate predictions.

The Phase 15 implementation loaded 57 Phase 10 map files, produced 114 scenario-level risk records, and produced 16384 pixel-level risk records. Scenario-level labels were distributed as 76 reliable, 25 caution, and 13 high-risk. As a consistency check against the representative failure-case evidence, Phase 13-like location2+r300y cases were flagged as caution or high-risk in 24/24 cases.

The screening logic uses deterministic evidence components, including low confidence-margin risk, false-dry risk, wet-fraction contraction, peak-depth underprediction, mean underprediction bias, boundary-zone false-dry risk, high-intensity `location2` metadata risk, and auxiliary cross-seed disagreement. The result is an operational screening layer: predictions are not only produced rapidly, but also accompanied by reliability labels and spatial risk maps.

These labels are deterministic screening labels. They are not calibrated probabilities and should not be interpreted as formal uncertainty quantification.

## 8. Warning-rule and applicability-boundary component

Phase 16 translates Phase 15 screening labels into application-oriented warning guidance. This step preserves the deterministic risk structure while making it usable for warning interpretation.

The Phase 16 scenario warnings were reliable=76, caution=25, and high-risk=13. Pixel warnings were reliable=5714, caution=8805, and high-risk=1865. The number of high-risk warning cases was 13, matching the Phase 15 high-risk cases.

The warning action matrix is:

| Warning level | Operational interpretation |
|---|---|
| reliable | use as rapid prediction reference |
| caution | use with targeted review |
| high-risk | do not use alone for warning decisions |

Reliable cases fall within the stronger current applicability range and can support rapid situational awareness with normal review. Caution cases remain useful, but sensitive areas such as wet/dry boundaries, shallow threshold-adjacent cells, local peak-depth regions, and pixel-level risk maps should be reviewed. High-risk cases should trigger conservative interpretation and should not be used alone for warning decisions.

## 9. Applicability boundary

The current surrogate is strongest for ordinary test scenarios that do not exhibit strong reliability-risk components. In these cases, the model can be used as a rapid flood-depth reference for general spatiotemporal flood-pattern approximation.

Several applicability-boundary zones require caution. Wet/dry boundary cells are caution zones because small depth errors can move the apparent inundation edge. Shallow threshold-adjacent cells are also caution zones because wet/dry classification near `wet_threshold = 0.05` is sensitive to small prediction changes. Local peak-depth extremes are caution to high-risk conditions because maximum depths can control warning severity and may be underpredicted.

High-intensity `location2+r300y` cases are high-risk applicability-boundary cases because they match the repeated Phase 13 severe-failure pattern. Repeated false-dry pixels are high-risk spatial caution areas because they indicate recurring missed-inundation signals. Strong wet-fraction contraction cases are caution to high-risk cases because they can indicate underestimated inundation extent.

This applicability boundary does not invalidate the surrogate. It defines how the prediction should be interpreted: rapid reference use in stronger regions, targeted review in caution regions, and non-standalone use in high-risk regions.

## 10. Suggested manuscript figures and tables

Existing project outputs can support a manuscript section or subsection on reliability-aware warning interpretation. Suitable figures and tables include:

- reliability diagnosis plots from Phase 12, especially boundary-distance error, depth-bin error, timestep trends, and top failure cases;
- representative failure-case figures from Phase 13 showing target depth, predicted depth, absolute error, and wet/dry mismatch;
- confidence margin vs wet/dry error from Phase 14;
- scenario risk category counts from Phase 15;
- risk component heatmap from Phase 15;
- pixel risk map example from Phase 15;
- warning level counts from Phase 16;
- warning action matrix from Phase 16;
- applicability boundary summary from Phase 16.

In a manuscript, these materials can be organized as one methods figure explaining the five-step framework, one results figure showing reliability-risk evidence, and one application figure showing warning labels, pixel risk maps, and the action matrix.

## 11. Contribution statement

A reliability-aware warning layer is developed to transform rapid flood surrogate predictions into scenario-level risk labels, pixel-level risk maps, and warning-rule guidance.

The framework connects reliability diagnosis, representative failure-mode interpretation, confidence proxy diagnostics, deterministic screening, and warning-rule interpretation into a single application-facing layer.

The warning layer provides an explicit applicability boundary for the trained surrogate by identifying ordinary reliable-use scenarios, caution zones, and high-risk cases where the prediction should not be used alone.

The approach is technically conservative: it improves the interpretability and operational use of existing surrogate predictions without claiming calibrated uncertainty or replacing hydrodynamic simulation.

The framework demonstrates how a rapid urban flood surrogate can be paired with deterministic reliability evidence to support more transparent warning-oriented interpretation.

## 12. Limitations and non-claims

No calibrated probabilistic uncertainty is claimed. The warning labels are deterministic operational interpretation labels, not predictive probabilities, Bayesian posterior estimates, calibrated confidence intervals, or guaranteed error bounds.

Confidence margin is a wet/dry classification risk proxy, not a full depth-error uncertainty measure. It is most informative near the wet/dry threshold and does not capture all depth-magnitude errors in moderate-to-deep or peak-depth regions.

Cross-seed disagreement is auxiliary. It should not be used as a strong standalone predictor of scenario-level error because repeated seeds can fail similarly on structured high-intensity cases.

The surrogate does not replace hydrodynamic simulation in high-stakes decisions. High-risk warning cases require conservative interpretation, expert review, hydrodynamic-model confirmation, or other operational evidence.

Applicability should be interpreted within the tested scenario space. The current evidence does not establish universal generalization beyond the evaluated data, locations, rainfall events, and scenario conditions.

Phases 12-17 did not retrain the model, modify architecture, modify Phase 10 loss, tune `boundary_weight` or `boundary_band_pixels`, or open a new sweep. The reliability-aware warning layer is an interpretation and screening layer built around the fixed Phase 10 recommended model.

## 13. Possible manuscript paragraph

To support warning-oriented use of the rapid urban flood surrogate, we developed a reliability-aware warning layer that interprets model outputs after prediction rather than modifying the trained predictor. The layer first diagnoses reliability across timesteps, depth ranges, wet/dry boundary-distance zones, and scenario types, then uses representative failure cases to identify structured high-risk modes such as systematic underprediction, reduced wet extent, local peak-depth underprediction, and false-dry dominated mismatch in high-intensity `location2` scenarios. A deterministic confidence-margin proxy, defined as the absolute distance between the predicted depth and the wet/dry threshold of 0.05, is used to flag wet/dry classification risk near the threshold, while cross-seed disagreement is retained only as auxiliary evidence. These diagnostics are converted into deterministic scenario-level and pixel-level screening labels and then into warning rules: reliable predictions may be used as rapid references, caution predictions require targeted review, and high-risk predictions should not be used alone for warning decisions. This layer does not provide calibrated probabilistic uncertainty and does not replace hydrodynamic simulation; instead, it provides an explicit applicability boundary for reliability-aware interpretation of rapid surrogate predictions within the tested scenario space.
