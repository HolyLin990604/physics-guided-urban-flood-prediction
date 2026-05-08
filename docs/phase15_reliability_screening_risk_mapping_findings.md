\# Phase 15 Reliability Screening and Risk Mapping Findings



\## 1. Objective



Phase 15 converts the reliability evidence from Phase 12, Phase 13, and Phase 14 into an automatic reliability-screening and risk-mapping module.



The purpose is not to retrain the model or improve metrics through parameter tuning. Instead, Phase 15 attaches interpretable reliability information to the existing Phase 10 recommended predictions.



The main output is a deterministic screening system that labels predictions as reliable, caution, or high-risk.



\## 2. Implementation Summary



The main new script is:



scripts/screen\_phase15\_reliability.py



The script reads existing Phase 10 prediction artifacts and available Phase 12, Phase 13, and Phase 14 diagnostic outputs.



The script does not:



\- retrain any model;

\- evaluate a checkpoint;

\- modify model architecture;

\- modify the Phase 10 loss;

\- tune boundary\_weight;

\- tune boundary\_band\_pixels;

\- open a new experiment sweep.



The outputs are saved under:



analysis/phase15\_reliability\_screening/



\## 3. Generated Outputs



Phase 15 generated the following core outputs:



\- summary.json

\- scenario\_risk\_scores.csv

\- pixel\_risk\_summary.csv

\- high\_risk\_cases.csv



It also generated the following figures:



\- scenario\_risk\_score\_distribution.png

\- scenario\_risk\_category\_counts.png

\- risk\_component\_heatmap.png

\- repeated\_false\_dry\_pixel\_risk.png

\- pixel\_risk\_map\_example.png



These outputs provide both scenario-level risk screening and pixel-level risk mapping.



\## 4. Scenario-Level Screening Results



The script loaded 57 Phase 10 map files and generated 114 scenario-level risk records.



The final category counts were:



\- reliable: 76

\- caution: 25

\- high-risk: 13



This distribution is reasonable because the model is not treated as globally unreliable. Instead, only specific scenarios with strong risk evidence are elevated to caution or high-risk.



\## 5. Risk Components



The scenario-level risk score is based on transparent additive components.



The main components include:



\- low confidence-margin risk;

\- false-dry risk;

\- predicted wet-fraction contraction;

\- peak-depth underprediction;

\- mean underprediction bias;

\- boundary-zone false-dry risk;

\- high-intensity location2-like metadata risk;

\- optional cross-seed disagreement.



These components are designed to reflect the known reliability issues identified in Phase 12, Phase 13, and Phase 14.



\## 6. Phase 13 Consistency Check



A key validation check is whether Phase 15 can flag the known Phase 13-like high-risk cases.



The Phase 13-like location2+r300y check produced:



\- matching rows: 24

\- flagged as caution or high-risk: 24

\- all matching rows flagged: true



This confirms that the Phase 15 screening logic is consistent with the representative failure-case evidence from Phase 13.



The strongest high-risk cases are dominated by high-intensity location2+r300y scenarios, especially r300y\_p0.6\_d3h and r300y\_p0.8\_d3h. Several additional location2 cases are also flagged because they show measurable false-dry, wet-fraction contraction, and peak-depth underprediction risk.



\## 7. Pixel-Level Risk Mapping



Phase 15 also generated pixel-level risk outputs.



The pixel-level output contains 16384 rows, corresponding to the 128 by 128 spatial grid.



The pixel-level risk products help identify where the predicted flood map should be interpreted with caution.



The generated figures include:



\- repeated false-dry pixel risk;

\- example pixel-level risk map.



This extends the project from scenario-level reliability diagnosis to spatially explicit risk mapping.



\## 8. Interpretation



The Phase 15 results show that the current model can be used not only to generate rapid flood-depth predictions, but also to attach reliability-screening information to those predictions.



This is an important transition from:



rapid prediction only



to:



rapid prediction plus reliability screening and risk mapping.



The result directly supports the long-term goal of building a trustworthy, interpretable, physically informed urban flood surrogate model for rapid warning applications.



\## 9. Limitations



The Phase 15 labels are deterministic screening labels. They should not be interpreted as calibrated probabilities, Bayesian uncertainty, or formal confidence intervals.



The confidence-margin component is mainly a wet/dry classification risk proxy. It does not fully represent depth-error uncertainty.



Cross-seed disagreement is only used as an auxiliary signal because Phase 14 showed that it is not a strong standalone predictor of scenario-level RMSE.



The current screening rules are transparent and interpretable, but future work could refine them using calibration data, operational expert rules, or additional validation scenarios.



\## 10. Current Conclusion



Phase 15 first implementation passed validation.



The module successfully generated scenario-level risk scores, pixel-level risk summaries, high-risk case lists, and risk figures.



Most importantly, it successfully flagged all known Phase 13-like location2+r300y failure cases as caution or high-risk.



Phase 15 therefore establishes the first functional reliability-screening and risk-mapping layer for the project.
