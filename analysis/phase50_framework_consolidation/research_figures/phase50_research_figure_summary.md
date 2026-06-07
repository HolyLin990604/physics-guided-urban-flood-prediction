# Phase 50 Research Figure Summary

These figures use existing Phase 48 reliability/physical-proxy diagnostics and Phase 49 conservative warning-framework outputs. No training, seed runs, sweeps, or model/configuration changes were performed.

Warning levels are conservative diagnostic screening labels. They are not calibrated probabilities, event likelihoods, or production-readiness guarantees.

## Figures

- `phase50_reliability_metric_boxplots_by_warning_level.png`: Scenario-level distributions of six reliability and physical-proxy metrics by warning level.
- `phase50_false_dry_vs_volume_bias_scatter.png`: Joint false-dry and absolute relative volume-bias proxy diagnostics, colored and marked by warning level.
- `phase50_location_type_warning_stacked_counts.png`: Reliable, caution, and high-risk counts by location and scenario type.
- `phase50_high_risk_failure_driver_heatmap.png`: Normalized diagnostic severity matrix for the top 15 ranked high-risk cases.
- `phase50_top_high_risk_case_priority.png`: Top 15 high-risk cases by the Phase 49 uncalibrated diagnostic priority score.

## Source Rows Loaded

- `analysis/phase48_full_dataset_reliability_physical_proxy/scenario_reliability_metrics.csv`: 48 rows
- `analysis/phase48_full_dataset_reliability_physical_proxy/wet_dry_error_metrics.csv`: 48 rows
- `analysis/phase48_full_dataset_reliability_physical_proxy/volume_response_proxy_metrics.csv`: 48 rows
- `analysis/phase48_full_dataset_reliability_physical_proxy/peak_depth_timing_metrics.csv`: 48 rows
- `analysis/phase48_full_dataset_reliability_physical_proxy/location_type_summary.csv`: 6 rows
- `analysis/phase49_full_dataset_warning_framework/scenario_warning_framework.csv`: 48 rows
- `analysis/phase49_full_dataset_warning_framework/location_type_warning_summary.csv`: 6 rows
- `analysis/phase49_full_dataset_warning_framework/high_risk_case_review_list.csv`: 35 rows
- `analysis/phase49_full_dataset_warning_framework/warning_rule_table.csv`: 9 rows

## Missing or Skipped Metrics

- None. All requested metric fields were available.

## Interpretation Boundaries

- Visualization support only; this is not a new experiment.
- No SWE residual, PINN, or Level 5 support claim.
- No strict conservation, full mass conservation, or hydrodynamic closure claim.
- No calibrated probability or final production-readiness claim.
- Heatmap values are display-only min-max severity scaling across the 48 scenario rows; original CSV values are unchanged.
