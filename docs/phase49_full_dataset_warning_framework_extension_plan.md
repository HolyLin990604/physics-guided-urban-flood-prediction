# Phase 49 Full Dataset Warning Framework Extension Plan

## Executive Summary

Phase 49 plans a no-training full-dataset warning framework extension for the Phase 47 controlled UrbanFlood24 128x128 downsample seed42 baseline, using the Phase 48 reliability and physical proxy diagnostics as fixed inputs.

The phase converts Phase 48 conservative reliability labels and failure-mode metrics into scenario-level warning actions, location and scenario-type summaries, reporting templates, and a prioritized high-risk case review list. It does not retrain the model, change model weights, change the loss, change the configuration, expand seeds, or introduce SWE/PINN or Level 5 claims.

The expected conservative decision is:

```text
phase49_warning_framework_completed_with_conservative_labels
```

This decision means the warning framework is suitable for conservative case reporting and diagnostic screening. It does not mean the labels are calibrated probabilities, and it does not establish the Phase 47 baseline as a final production model.

## Background from Phase 47-48

Phase 47 completed the first controlled UrbanFlood24 full-dataset 128x128 downsample seed42 10 epoch baseline pilot:

```text
selected_decision = phase47_controlled_128_downsample_seed42_pilot_completed
seed = 42
resolution = 128
epochs = 10
train_samples = 960
test_samples = 384
best_test_rmse = 0.01109213042097205
test_mae = 0.00525291082279485
test_wet_dry_iou = 0.8255524213115374
no_swe_pinn = true
level5_supported = false
```

Phase 47 provides a controlled Level 4+ baseline to evaluate. It does not authorize uncontrolled training expansion, new seeds, higher-resolution training, hydrodynamic closure claims, strict conservation claims, SWE residuals, PINN components, or Level 5 support.

Phase 48 completed no-training reliability and physical proxy diagnostics for the Phase 47 baseline:

```text
selected_decision = phase48_diagnostics_ready_for_warning_framework_extension
checkpoint_found = true
evaluated_scenarios = 48
evaluated_windows = 384
mean_rmse = 0.012037189189155709
mean_mae = 0.005252910632811514
mean_wet_dry_iou = 0.863043953275997
mean_false_dry_rate = 0.0911363765964386
mean_false_wet_rate = 0.003937674554837349
mean_absolute_relative_volume_bias_proxy = 0.021456503649973275
warning_level_counts = reliable 1, caution 12, high-risk 35
no_training = true
no_swe_pinn = true
level5_supported = false
```

Phase 48 found that the warning labels are conservative diagnostic screening labels, not calibrated probabilities. The large high-risk count reflects conservative screening sensitivity and should not be interpreted as proof of poor overall model skill.

## Purpose of Warning Framework Extension

The purpose of Phase 49 is to make the Phase 48 diagnostics usable for warning-oriented reporting without changing the model.

Phase 49 should answer:

- What warning action should be attached to each evaluated scenario?
- Which diagnostic failure modes most likely drive each warning label?
- How are warning labels distributed across locations and scenario types?
- Which high-risk cases should be reviewed first?
- What user-facing warning language should be used in reports?
- What decision record should document the conservative Level 4+ interpretation?

The framework is a reporting and screening layer. It is not a new model, not a recalibration procedure, not a training phase, and not a hydrodynamic validation phase.

## Inputs and Required Artifacts

Phase 49 uses the following Phase 48 outputs as fixed inputs:

```text
analysis/phase48_full_dataset_reliability_physical_proxy/reliability_warning_levels.csv
analysis/phase48_full_dataset_reliability_physical_proxy/scenario_reliability_metrics.csv
analysis/phase48_full_dataset_reliability_physical_proxy/wet_dry_error_metrics.csv
analysis/phase48_full_dataset_reliability_physical_proxy/peak_depth_timing_metrics.csv
analysis/phase48_full_dataset_reliability_physical_proxy/volume_response_proxy_metrics.csv
analysis/phase48_full_dataset_reliability_physical_proxy/location_type_summary.csv
analysis/phase48_full_dataset_reliability_physical_proxy/phase48_reliability_summary.json
analysis/phase48_full_dataset_reliability_physical_proxy/phase48_reliability_summary.md
```

The planned script is:

```text
scripts/build_phase49_warning_framework.py
```

The expected output directory is:

```text
analysis/phase49_full_dataset_warning_framework/
```

The script should first perform an input readiness check. If required Phase 48 files are missing, it should write a decision record selecting:

```text
phase49_warning_framework_blocked_by_missing_phase48_inputs
```

## Warning Label Interpretation

Phase 49 must preserve the Phase 48 labels:

```text
reliable
caution
high-risk
```

These labels are conservative diagnostic screening categories. They are not probabilities, calibrated confidence levels, operational alert probabilities, or direct estimates of event likelihood.

Interpretation:

- `reliable`: Phase 48 diagnostics did not identify major reliability or physical proxy concerns under the tested baseline and evaluated scenario.
- `caution`: At least one diagnostic suggests degraded reliability or a meaningful failure-mode risk that should be reviewed before using the prediction unqualified.
- `high-risk`: Diagnostics indicate elevated warning failure risk, severe or repeated metric degradation, or a physical proxy concern that requires review or supplemental evidence before relying on the prediction.

The framework should make clear that `high-risk` is a conservative screening category. It does not by itself prove model failure, and it does not negate the overall Phase 47/48 aggregate skill metrics.

## Warning Rule Design

Phase 49 should keep Phase 48 warning labels unchanged and add a warning action layer:

| Phase 48 label | Phase 49 warning action |
| --- | --- |
| `reliable` | `normal_use_with_standard_monitoring` |
| `caution` | `use_with_caution_and_review_diagnostics` |
| `high-risk` | `high_risk_requires_review_or_supplemental_evidence` |

The script should also attach concise failure-driver explanations using available metrics. Candidate drivers include:

- High RMSE.
- Low wet/dry IoU.
- Elevated false-dry rate.
- Elevated false-wet rate.
- Elevated volume-bias proxy.
- Peak-depth underprediction proxy.

Failure-driver thresholds should be traceable to Phase 48 rule outputs where available. If the Phase 48 artifacts already contain boolean flags or thresholds, Phase 49 should reuse them. If not, Phase 49 may compute ranked or thresholded driver flags from the Phase 48 metric columns, but it must document those thresholds in `warning_rule_table.csv` and `warning_framework_summary.md`.

The framework should prefer transparent rule tables over hidden scoring. It should not introduce an opaque combined risk score unless the score is purely descriptive and clearly labeled as uncalibrated.

## Scenario-Level Warning Summary

Phase 49 should produce one scenario-level warning framework table:

```text
scenario_warning_framework.csv
```

Recommended columns:

- `scenario_id`.
- `location`, if available.
- `scenario_type`, if available.
- `phase48_warning_label`.
- `phase49_warning_action`.
- `rmse`.
- `mae`.
- `wet_dry_iou`.
- `false_dry_rate`.
- `false_wet_rate`.
- `absolute_relative_volume_bias_proxy`.
- `peak_depth_underprediction_proxy`, if available.
- `primary_failure_driver`.
- `secondary_failure_drivers`.
- `warning_message_template_id`.
- `requires_case_review`.

The table should preserve all 48 evaluated test scenarios and should not silently drop scenarios with missing optional metrics. Missing optional metrics should be represented explicitly as unavailable.

## Location and Scenario-Type Warning Summary

Phase 49 should aggregate warning labels and warning actions by available metadata fields:

```text
location_type_warning_summary.csv
```

Required aggregation where columns are available:

- Warning counts by `location`.
- Warning counts by `scenario_type`.
- Warning counts by `location` and `scenario_type`.
- Reliable, caution, and high-risk proportions within each group.
- Mean RMSE, MAE, wet/dry IoU, false-dry rate, false-wet rate, and absolute relative volume-bias proxy within each group.

The summary should use only metadata present in Phase 48 or joined Phase 48 artifacts. It should not invent new location or scenario-type categories.

## Failure-Mode Explanation Design

Failure-mode explanations should be concise, metric-backed, and non-probabilistic.

Recommended explanation rules:

- High RMSE: report when scenario RMSE is above the Phase 48 reliability threshold or among the most degraded cases.
- Low wet/dry IoU: report when wet/dry agreement is below the Phase 48 caution or high-risk threshold.
- Elevated false-dry rate: report when dry predictions occur in target-wet regions at a concerning rate.
- Elevated false-wet rate: report when wet predictions occur in target-dry regions at a concerning rate.
- Elevated volume-bias proxy: report when summed predicted depth differs materially from summed target depth.
- Peak-depth underprediction proxy: report when predicted peak depth is meaningfully below target peak depth.

False-dry explanations should receive special attention because they can suppress warnings in flooded regions. False-wet explanations should also be reported because they can reduce credibility and increase unnecessary alert burden.

Volume-response explanations must remain proxy language only. They must not claim strict mass conservation, full mass conservation, hydrodynamic closure, SWE consistency, or physical law satisfaction.

## Recommended User-Facing Warning Messages

Phase 49 should produce:

```text
warning_message_templates.md
```

Recommended templates:

### Reliable

```text
Warning category: Reliable
Recommended action: Normal use with standard monitoring.
Interpretation: Phase 48 diagnostics did not identify major reliability or physical proxy concerns for this scenario under the evaluated Phase 47 baseline.
Limitations: This is a conservative diagnostic label, not a calibrated probability or final production guarantee.
```

### Caution

```text
Warning category: Caution
Recommended action: Use with caution and review diagnostics.
Interpretation: One or more diagnostics indicate degraded reliability or a potential warning failure mode for this scenario.
Limitations: This label supports review and contextual interpretation. It is not a calibrated probability and does not prove model failure.
```

### High-Risk

```text
Warning category: High-risk
Recommended action: Review before relying on the prediction, or supplement with additional evidence.
Interpretation: Conservative diagnostics indicate elevated risk of warning failure or physical proxy inconsistency for this scenario.
Limitations: This screening label is intentionally sensitive. It does not by itself prove poor overall model skill or establish event probability.
```

Template variables may include scenario ID, location, scenario type, primary failure driver, secondary failure drivers, and key metric values.

## Expected Outputs

Phase 49 should create:

```text
analysis/phase49_full_dataset_warning_framework/warning_framework_summary.json
analysis/phase49_full_dataset_warning_framework/warning_framework_summary.md
analysis/phase49_full_dataset_warning_framework/scenario_warning_framework.csv
analysis/phase49_full_dataset_warning_framework/location_type_warning_summary.csv
analysis/phase49_full_dataset_warning_framework/warning_rule_table.csv
analysis/phase49_full_dataset_warning_framework/warning_message_templates.md
analysis/phase49_full_dataset_warning_framework/high_risk_case_review_list.csv
analysis/phase49_full_dataset_warning_framework/phase49_warning_framework_decision.json
```

`warning_framework_summary.json` should include counts, input readiness, selected decision, no-training confirmation, preserved-label confirmation, and Level 4+/Level 5 claim status.

`warning_framework_summary.md` should provide a concise narrative suitable for project documentation.

`warning_rule_table.csv` should document label-to-action mappings, failure-driver rules, thresholds or ranking logic, and whether each rule comes from Phase 48 or Phase 49 post-processing.

`high_risk_case_review_list.csv` should prioritize high-risk cases for review using transparent sorting, such as high-risk first, then elevated false-dry rate, low wet/dry IoU, high RMSE, peak-depth underprediction, and elevated volume-bias proxy.

## Decision Criteria

Decision candidates:

```text
phase49_warning_framework_ready_for_case_reporting
phase49_warning_framework_completed_with_conservative_labels
phase49_warning_framework_blocked_by_missing_phase48_inputs
phase49_warning_framework_deferred
```

Select `phase49_warning_framework_completed_with_conservative_labels` when:

- Required Phase 48 inputs are present.
- Phase 48 labels are preserved.
- Scenario-level warning actions are produced.
- Failure-driver explanations are generated from available metrics.
- Location and scenario-type summaries are produced where metadata is available.
- Warning message templates are written.
- High-risk cases are prioritized for review.
- The summary explicitly states no training, no SWE/PINN, no Level 5 support, and no calibrated probability interpretation.

Select `phase49_warning_framework_ready_for_case_reporting` only if the outputs are complete enough to be directly used in case-study reporting without additional manual review.

Select `phase49_warning_framework_blocked_by_missing_phase48_inputs` if required Phase 48 artifacts are missing.

Select `phase49_warning_framework_deferred` if the framework cannot be completed for reasons other than missing Phase 48 inputs.

The expected conservative decision is:

```text
phase49_warning_framework_completed_with_conservative_labels
```

## Guardrails

Phase 49 must observe the following guardrails:

- No training.
- No seed123 or seed202.
- No seed sweep.
- No hyperparameter sweep.
- No 256x256 training.
- No tile, multiscale, or full-500 training.
- No new loss redesign.
- No model, loss, or config modification.
- No SWE residual.
- No PINN.
- No Level 5 support claim.
- No strict conservation, full mass conservation, or hydrodynamic closure claim.
- Do not reinterpret warning labels as calibrated probabilities.
- Do not claim Phase 47 is a final production model.
- Do not authorize uncontrolled training expansion.

The planned script should operate only on existing Phase 48 diagnostic artifacts and write Phase 49 reporting outputs.

## Success Criteria

Phase 49 is successful if it:

- Creates the expected output directory and all required output files.
- Preserves Phase 48 reliable, caution, and high-risk labels.
- Maps each label to the required warning action.
- Produces one scenario-level framework row for every Phase 48 evaluated scenario.
- Aggregates warning counts by location and scenario type where metadata is available.
- Documents failure-driver rules and applies them consistently.
- Produces reporting-ready warning message templates.
- Produces a prioritized high-risk case review list.
- Writes a decision JSON selecting the appropriate Phase 49 decision.
- Confirms `no_training = true`.
- Confirms `no_swe_pinn = true`.
- Confirms `level5_supported = false`.

## Final Conclusion

Phase 49 should create a full-dataset warning framework that converts Phase 48 diagnostic labels and failure-mode metrics into scenario-level warning actions and reporting templates. It remains Level 4+ and no-training. It does not claim Level 5, SWE/PINN, strict conservation, full mass conservation, or hydrodynamic closure.
