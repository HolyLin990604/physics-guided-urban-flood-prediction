# Phase 16 Reliability-Aware Warning Rules and Applicability Boundary Findings

## 1. Objective

Phase 16 converts the Phase 15 reliability-screening results into application-oriented warning rules and applicability-boundary guidance.

The purpose is to make the Phase 15 reliable, caution, and high-risk screening labels usable in a rapid flood-warning workflow. Phase 16 therefore translates deterministic reliability-screening outputs into practical guidance on when the surrogate prediction can be used as a rapid reference, when targeted review is required, and when the prediction should not be used alone for warning decisions.

## 2. Implementation Summary

The Phase 16 implementation is provided by:

- `scripts/build_phase16_warning_rules.py`

The generated outputs are saved under:

- `analysis/phase16_warning_rules/`

The implementation is an application-layer interpretation step. It does not:

- retrain any model;
- modify model architecture;
- modify the Phase 10 loss;
- tune `boundary_weight`;
- tune `boundary_band_pixels`;
- open a new sweep.

## 3. Main Outputs

Phase 16 generated the following outputs:

- `summary.json`
- `warning_rules.json`
- `scenario_warning_summary.csv`
- `applicability_boundary_table.csv`
- `high_risk_warning_cases.csv`
- `pixel_warning_summary.csv`
- `figures/warning_level_counts.png`
- `figures/warning_action_matrix.png`
- `figures/applicability_boundary_summary.png`
- `figures/high_risk_warning_case_distribution.png`
- `figures/pixel_warning_map_example.png`

## 4. Scenario Warning Results

The scenario-level warning summary contains 114 records. The warning-level counts are:

- reliable: 76
- caution: 25
- high-risk: 13

These counts preserve the Phase 15 scenario-level risk distribution while adding operational warning recommendations and review actions.

## 5. Pixel Warning Results

The pixel-level warning summary contains 16384 grid cells. The pixel warning-level counts are:

- reliable: 5714
- caution: 8805
- high-risk: 1865

The pixel-level labels provide spatial warning guidance for locations that repeatedly show low-margin, wet/dry boundary, false-dry, deep-underprediction, or high-risk-case signals.

## 6. Warning Action Matrix

The Phase 16 warning action matrix maps each warning level to an operational use recommendation:

- reliable -> use as rapid prediction reference;
- caution -> use with targeted review;
- high-risk -> do not use alone for warning decisions.

For reliable cases, the prediction is within the stronger applicability range of the current surrogate model and can support rapid situational awareness. For caution cases, users should review sensitive areas such as wet/dry boundaries, shallow threshold-adjacent zones, local peak-depth areas, and pixel-level risk maps. For high-risk cases, the prediction should trigger conservative interpretation, hydrodynamic-model confirmation, or expert review before warning decisions.

## 7. Applicability Boundary Interpretation

The applicability-boundary table summarizes where the current model evidence is stronger and where operational caution is required.

Ordinary test scenarios with Phase 15 reliable labels and no strong risk components are treated as the stronger applicability region. These cases can be used as rapid flood-depth references with normal review.

Wet/dry boundary cells are caution zones because small depth or threshold changes can move the apparent inundation edge. Shallow threshold-adjacent cells are also caution zones because exact wet/dry classification near the threshold should not be overinterpreted.

High-intensity `location2+r300y` cases are high-risk applicability-boundary cases. These cases match the known Phase 13-like failure pattern and should not be used alone for warning decisions.

Local peak-depth extremes are caution to high-risk conditions because local maximum depths can control warning severity and may require review for underprediction. Repeated false-dry pixels are high-risk spatial caution areas because they indicate recurring missed-inundation screening signals. Strong wet-fraction contraction cases are caution to high-risk cases because they can indicate underestimation of inundation extent.

## 8. Relationship to Phase 15

Phase 16 does not replace Phase 15. It converts Phase 15 deterministic screening labels into warning guidance.

The Phase 16 high-risk warning cases match the Phase 15 high-risk cases: Phase 15 reports 13 high-risk cases, and Phase 16 reports 13 high-risk warning cases. The Phase 13-like `location2+r300y` consistency check also remains intact: all 24 matching rows are flagged as caution or high-risk.

## 9. Limitations

The Phase 16 warning labels are deterministic operational interpretation labels. They are not calibrated probabilities, Bayesian uncertainty estimates, or formal confidence intervals.

The warning rules should support, not replace, hydrodynamic modeling or expert review in high-stakes decisions. Pixel warning labels summarize repeated screening signals and should be interpreted as spatial caution guidance rather than event probabilities.

## 10. Current Conclusion

Phase 16 establishes the first application-oriented warning-rule and applicability-boundary layer for the project.

The project now extends from rapid prediction plus reliability screening and spatial risk mapping to rapid prediction with explicit warning-rule interpretation and applicability-boundary guidance.
