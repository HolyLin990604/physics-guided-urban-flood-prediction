# Phase 15 Reliability Screening and Risk Mapping Plan

## 1. Objective

Phase 15 aims to convert the diagnostic evidence from Phase 12, Phase 13, and Phase 14 into an automatic reliability-screening and risk-mapping module.

The goal is not to retrain the model or improve metrics through tuning. The goal is to attach reliability information to the existing Phase 10 recommended predictions.

The intended output is a prediction-aware screening system that can identify:

- which scenarios are reliable;

- which scenarios require caution;

- which scenarios are high-risk;

- which spatial pixels are likely to be unreliable.

## 2. Current Mainline Context

The current recommended model remains the Phase 10 margin-aware setting:

- boundary_band_pixels = 1

- boundary_weight = 2.0

This setting is fixed in Phase 15.

Phase 12 showed that model reliability is not uniform across space, depth range, timestep, and scenario type.

Phase 13 showed that the most serious failures are systematic rather than random. The top failures are concentrated in high-intensity location2 scenarios and are characterized by underprediction, reduced predicted wet fraction, peak-depth underestimation, and false-dry dominated wet/dry mismatch.

Phase 14 showed that confidence margin is useful as a wet/dry classification risk proxy, while cross-seed disagreement should only be treated as an auxiliary signal.

## 3. Non-Goals

Phase 15 must not include:

- no model retraining;

- no model architecture modification;

- no Phase 10 loss modification;

- no boundary_weight or boundary_band_pixels tuning;

- no new hyperparameter sweep;

- no claim of calibrated probabilistic uncertainty.

This phase is a reliability-screening module built on top of existing trained predictions.

## 4. Main Script

The main new script should be:

scripts/screen_phase15_reliability.py

The expected output directory is:

analysis/phase15_reliability_screening/

## 5. Expected Inputs

The script should use existing outputs from:

- Phase 10 prediction and evaluation results;

- Phase 12 reliability diagnosis;

- Phase 13 failure-case visualization;

- Phase 14 confidence proxy diagnostics.

Candidate input directories include:

- runs/phase10_margin_aware_boundary_band_seed*_40e/evaluation_test/

- analysis/phase12_reliability/

- analysis/phase13_failure_cases/

- analysis/phase14_confidence/

The script should not require new model training.

## 6. Expected Outputs

The script should generate:

- analysis/phase15_reliability_screening/summary.json

- analysis/phase15_reliability_screening/scenario_risk_scores.csv

- analysis/phase15_reliability_screening/pixel_risk_summary.csv

- analysis/phase15_reliability_screening/high_risk_cases.csv

- analysis/phase15_reliability_screening/figures/

Possible figures include:

- scenario_risk_score_distribution.png

- scenario_risk_category_counts.png

- pixel_risk_map_examples.png

- risk_component_heatmap.png

## 7. Risk Categories

The module should assign three interpretable categories:

- reliable

- caution

- high-risk

These labels are rule-based or score-based screening labels. They are not probabilistic confidence intervals.

## 8. Scenario-Level Risk Indicators

Scenario-level risk scoring should consider:

1. High-intensity location2-like scenario risk

&#x20;  Scenarios similar to the Phase 13 repeated failures should receive elevated risk.

2. Predicted wet-fraction contraction

&#x20;  Risk increases when predicted wet area is much smaller than target wet area.

3. False-dry risk

&#x20;  Risk increases when target cells are wet but predictions classify them as dry.

4. Deep or peak-depth underprediction risk

&#x20;  Risk increases when target peak depth is high but predicted peak depth is much lower.

5. Low confidence-margin risk

&#x20;  Risk increases when many predicted cells are close to the wet/dry threshold.

6. Boundary risk

&#x20;  Risk increases when errors are concentrated near wet/dry boundaries.

7. Cross-seed disagreement

&#x20;  This may be used as an auxiliary risk signal when comparable seed outputs are available.

## 9. Pixel-Level Risk Indicators

Pixel-level risk mapping should consider:

- low confidence margin;

- wet/dry threshold proximity;

- false-dry pixels;

- boundary-zone pixels;

- deep target underprediction pixels;

- repeated high-error pixels across scenarios or seeds.

The pixel-level result should answer:

Where in the predicted flood map should users be cautious?

## 10. Suggested Risk-Scoring Design

The script may use a transparent additive score:

risk_score =

low_margin_component

\+ false_dry_component

\+ wet_fraction_contraction_component

\+ peak_underprediction_component

\+ boundary_component

\+ high_intensity_location2_component

\+ auxiliary_disagreement_component

The script should store both total risk score and individual component scores.

This is important for interpretability.

## 11. Validation Checks

After implementation, run:

python scripts/screen_phase15_reliability.py --help

python scripts/screen_phase15_reliability.py

Then verify that these files exist:

- analysis/phase15_reliability_screening/summary.json

- analysis/phase15_reliability_screening/scenario_risk_scores.csv

- analysis/phase15_reliability_screening/pixel_risk_summary.csv

- analysis/phase15_reliability_screening/high_risk_cases.csv

The known high-intensity location2 failure cases from Phase 13 should be flagged as caution or high-risk.

## 12. Completion Criteria

Phase 15 can be considered complete when:

1. the screening script runs successfully;

2. scenario-level risk scores are generated;

3. pixel-level risk summaries or maps are generated;

4. high-risk cases are identified;

5. known Phase 13 location2 failure cases are correctly flagged;

6. findings are documented;

7. README, docs/project_status.md, and docs/experiment_index.md are updated;

8. the branch is merged into main.

## 13. Research Significance

Phase 15 changes the project from a prediction-only surrogate model into a reliability-aware surrogate modeling framework.

The contribution becomes:

rapid urban flood prediction with explicit reliability screening and spatial risk mapping.

This directly supports the long-term goal of building a trustworthy, interpretable, physically informed urban flood surrogate model for rapid warning applications.
