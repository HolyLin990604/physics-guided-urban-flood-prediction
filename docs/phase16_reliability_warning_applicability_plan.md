# Phase 16 Reliability-Aware Warning Rules and Applicability Boundary Plan

## 1. Objective

Phase 16 aims to convert the Phase 15 reliability-screening results into an application-oriented warning-rule and applicability-boundary layer.

Phase 15 already generated scenario-level and pixel-level reliability screening outputs. It can label predictions as reliable, caution, or high-risk. Phase 16 should answer the next question:

How should these reliability labels be used in a rapid flood-warning workflow?

The goal is to transform reliability screening into practical warning guidance, including:

- scenario-level warning recommendations;

- pixel-level caution interpretation;

- applicability-boundary tables;

- high-risk usage notes;

- clear statements about when the surrogate prediction can be trusted, when it should be reviewed, and when it should not be used alone.

## 2. Current Mainline Context

The current main branch has completed Phase 15 and merged it into main.

The current recommended model remains the Phase 10 margin-aware setting:

- boundary_band_pixels = 1

- boundary_weight = 2.0

Phase 16 must treat this model setting as fixed.

Phase 16 should build on the existing Phase 12 to Phase 15 reliability evidence:

- Phase 12 identified reliability and applicability weaknesses.

- Phase 13 visualized representative failure cases.

- Phase 14 diagnosed confidence and disagreement proxies.

- Phase 15 converted these findings into automatic reliability screening and spatial risk mapping.

Phase 16 should not reopen model tuning. It should convert the existing screening outputs into warning rules and applicability guidance.

## 3. Non-Goals

Phase 16 must not include:

- no model retraining;

- no model architecture modification;

- no Phase 10 loss modification;

- no boundary_weight or boundary_band_pixels tuning;

- no new hyperparameter sweep;

- no new claim of calibrated probabilistic uncertainty;

- no replacement of Phase 15 screening results.

Phase 16 is an application-layer interpretation phase.

## 4. Main Question

The central question of Phase 16 is:

Given a Phase 15 risk label or risk map, how should a user interpret and use the flood prediction?

The expected interpretation should be similar to:

- reliable: prediction can be used as a rapid reference;

- caution: prediction can be used, but boundary areas, shallow wet/dry transitions, and local peak depths should be checked carefully;

- high-risk: prediction should not be used alone for warning decisions and should trigger review, conservative interpretation, or hydrodynamic-model confirmation.

## 5. Planned New Script

The main new script should be:

scripts/build_phase16_warning_rules.py

The script should read existing Phase 15 outputs and generate warning-rule and applicability-boundary products.

Expected output directory:

analysis/phase16_warning_rules/

## 6. Expected Inputs

The script should use existing Phase 15 outputs:

- analysis/phase15_reliability_screening/summary.json

- analysis/phase15_reliability_screening/scenario_risk_scores.csv

- analysis/phase15_reliability_screening/pixel_risk_summary.csv

- analysis/phase15_reliability_screening/high_risk_cases.csv

Optional supporting inputs may include:

- analysis/phase12_reliability/

- analysis/phase13_failure_cases/

- analysis/phase14_confidence/

The script should not require new model predictions or new training outputs.

## 7. Expected Outputs

The script should generate:

- analysis/phase16_warning_rules/summary.json

- analysis/phase16_warning_rules/warning_rules.json

- analysis/phase16_warning_rules/scenario_warning_summary.csv

- analysis/phase16_warning_rules/applicability_boundary_table.csv

- analysis/phase16_warning_rules/high_risk_warning_cases.csv

- analysis/phase16_warning_rules/pixel_warning_summary.csv

- analysis/phase16_warning_rules/figures/

Recommended figures include:

- warning_level_counts.png

- warning_action_matrix.png

- applicability_boundary_summary.png

- high_risk_warning_case_distribution.png

- pixel_warning_map_example.png

The exact figure list can be adjusted according to the available Phase 15 outputs.

## 8. Warning Levels

Phase 16 should define application-oriented warning levels based on Phase 15 risk categories.

Recommended mapping:

1. reliable

Use as rapid prediction reference.

Suggested interpretation:

The predicted flood-depth map is within the current model's stronger applicability range. It can be used for rapid situational awareness, but still should be interpreted as a surrogate-model output rather than a replacement for hydrodynamic simulation in high-stakes final decisions.

2. caution

Use with caution and review sensitive areas.

Suggested interpretation:

The prediction may still be useful, but wet/dry boundaries, shallow threshold-adjacent areas, and local peak-depth areas require careful interpretation. Users should inspect pixel-level risk maps and consider additional hydrodynamic or expert review.

3. high-risk

Do not use alone for warning decisions.

Suggested interpretation:

The prediction is likely outside the strongest applicability range of the current surrogate model. The case should trigger conservative interpretation, manual review, hydrodynamic-model confirmation, or warning escalation depending on the operational context.

## 9. Scenario-Level Warning Rules

The script should convert Phase 15 scenario-level risk scores into warning recommendations.

Candidate rules:

- reliable scenarios receive "rapid reference" recommendation;

- caution scenarios receive "review required" recommendation;

- high-risk scenarios receive "do not use alone" recommendation;

- scenarios with strong false-dry risk should receive a missed-inundation warning;

- scenarios with strong wet-fraction contraction should receive an inundation-extent underestimation warning;

- scenarios with strong peak-depth underprediction should receive a local-depth underestimation warning;

- high-intensity location2-like cases should receive an applicability-boundary warning.

The output should store both the warning level and the reason.

## 10. Pixel-Level Warning Rules

The script should convert Phase 15 pixel-level risk summaries into spatial warning guidance.

Candidate pixel-level warning indicators:

- repeated false-dry risk;

- low confidence-margin risk;

- wet/dry boundary risk;

- deep-depth underprediction risk;

- repeated high-risk pixels across scenarios or seeds.

Pixel-level warning summaries should help answer:

Where in the predicted flood-depth map should users be cautious?

The output should support statements such as:

- boundary-zone pixels require caution;

- repeated false-dry pixels may indicate missed inundation risk;

- local high-risk pixels should be highlighted in warning-map interpretation.

## 11. Applicability Boundary Table

Phase 16 should generate an applicability-boundary table that summarizes where the current model is stronger or weaker.

Suggested fields:

- condition_type;

- condition_description;

- reliability_level;

- evidence_source;

- recommended_use;

- caution_note.

Example rows:

1. ordinary test scenarios

Reliability level: stronger

Recommended use: rapid flood-depth reference.

2. wet/dry boundary cells

Reliability level: caution

Recommended use: inspect with pixel risk map.

3. shallow threshold-adjacent cells

Reliability level: caution

Recommended use: avoid overinterpreting exact wet/dry classification.

4. high-intensity location2+r300y cases

Reliability level: high-risk

Recommended use: do not use prediction alone; trigger review.

5. local peak-depth extremes

Reliability level: caution to high-risk

Recommended use: check for possible underprediction.

## 12. Warning Action Matrix

Phase 16 should produce a warning action matrix.

Suggested matrix:

- reliable:

&#x20; - action: use as rapid reference;

&#x20; - review level: normal;

&#x20; - operational note: suitable for quick screening.

- caution:

&#x20; - action: use with review;

&#x20; - review level: targeted review;

&#x20; - operational note: inspect boundary, shallow, and local peak-depth areas.

- high-risk:

&#x20; - action: do not use alone;

&#x20; - review level: mandatory review;

&#x20; - operational note: confirm with hydrodynamic model, expert judgment, or conservative warning strategy.

This matrix should be stored in warning_rules.json and summarized in the findings document.

## 13. Implementation Principles

The implementation should be:

- deterministic;

- transparent;

- rule-based;

- reproducible;

- based on existing Phase 15 outputs;

- robust to missing optional files;

- explicit about limitations.

The script should not claim that warning levels are calibrated probabilities.

The script should clearly state that the warning rules are an application-oriented interpretation of deterministic reliability screening results.

## 14. Validation Checks

After implementation, run:

python scripts/build_phase16_warning_rules.py --help

python scripts/build_phase16_warning_rules.py

Then verify that the following files exist:

- analysis/phase16_warning_rules/summary.json

- analysis/phase16_warning_rules/warning_rules.json

- analysis/phase16_warning_rules/scenario_warning_summary.csv

- analysis/phase16_warning_rules/applicability_boundary_table.csv

- analysis/phase16_warning_rules/high_risk_warning_cases.csv

- analysis/phase16_warning_rules/pixel_warning_summary.csv

The high-risk warning cases should be consistent with the Phase 15 high-risk cases.

The warning rules should preserve the Phase 15 conclusion that known Phase 13-like location2+r300y cases require caution or high-risk interpretation.

## 15. Expected Interpretation

If successful, Phase 16 should support the following interpretation:

The project now provides not only rapid flood-depth prediction and reliability screening, but also application-oriented warning guidance.

The project evolves from:

rapid prediction plus reliability screening and risk mapping

to:

rapid prediction plus reliability screening, risk mapping, and warning-rule interpretation.

This makes the surrogate model more suitable for trustworthy rapid-warning applications.

## 16. Expected Deliverables

Phase 16 should eventually deliver:

- docs/phase16_reliability_warning_applicability_plan.md

- scripts/build_phase16_warning_rules.py

- analysis/phase16_warning_rules/

- docs/phase16_reliability_warning_applicability_findings.md

- updated README.md

- updated docs/project_status.md

- updated docs/experiment_index.md

## 17. Completion Criteria

Phase 16 can be considered complete when:

1. the warning-rule script runs successfully;

2. warning_rules.json is generated;

3. scenario warning summaries are generated;

4. applicability-boundary tables are generated;

5. high-risk warning cases are consistent with Phase 15;

6. pixel-level warning summaries are generated;

7. findings are documented;

8. README and project documentation are updated;

9. the branch is merged into main.

## 18. Research Significance

Phase 16 is important because it converts reliability diagnosis into practical warning interpretation.

The contribution is no longer only:

rapid flood prediction with reliability screening

but becomes:

rapid flood prediction with reliability screening, spatial risk mapping, and warning-rule guidance.

This directly supports the long-term goal of building a trustworthy, interpretable, physically informed urban flood surrogate model for rapid warning applications.
