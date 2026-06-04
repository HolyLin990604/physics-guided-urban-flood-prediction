# Phase 48 Full Dataset Reliability Physical Proxy Diagnostics Findings

## Executive Summary

Phase 48 completed no-training reliability and physical proxy diagnostics for the Phase 47 controlled 128x128 full-dataset baseline. The Phase 47 checkpoint was found and evaluated on the Phase 45 test split.

The diagnostic pass evaluated 48 test scenarios and 384 windows. Mean error and wet/dry metrics remained strong, while conservative warning labels identified many scenarios for closer warning-framework treatment.

The selected decision is:

```text
phase48_diagnostics_ready_for_warning_framework_extension
```

This supports Phase 49 full-dataset warning-framework extension. It does not authorize uncontrolled training expansion, new seeds, 256x256 training, tile or multiscale training, full 500x500 training, sweeps, or loss redesign.

## Inputs and Outputs

Phase 48 used the Phase 47 128x128 full-dataset baseline checkpoint and the Phase 45 full-dataset test split. The evaluated baseline is the seed42, 10 epoch Phase 47 run.

Primary input artifacts:

```text
configs/train_phase47_full_downsample128_seed42_10e.json
analysis/phase47_controlled_downsample_baseline/metrics.csv
analysis/phase47_controlled_downsample_baseline/metrics.json
analysis/phase47_controlled_downsample_baseline/phase47_training_summary.json
runs/phase47_full_downsample128_baseline_seed42_10e/checkpoints/best.pt
analysis/phase45_full_dataset_indexing/scenario_index.csv
analysis/phase45_full_dataset_indexing/static_geodata_index.csv
```

Primary Phase 48 outputs:

```text
analysis/phase48_full_dataset_reliability_physical_proxy/phase48_diagnostic_readiness.json
analysis/phase48_full_dataset_reliability_physical_proxy/scenario_reliability_metrics.csv
analysis/phase48_full_dataset_reliability_physical_proxy/step_reliability_metrics.csv
analysis/phase48_full_dataset_reliability_physical_proxy/wet_dry_error_metrics.csv
analysis/phase48_full_dataset_reliability_physical_proxy/peak_depth_timing_metrics.csv
analysis/phase48_full_dataset_reliability_physical_proxy/volume_response_proxy_metrics.csv
analysis/phase48_full_dataset_reliability_physical_proxy/location_type_summary.csv
analysis/phase48_full_dataset_reliability_physical_proxy/reliability_warning_levels.csv
analysis/phase48_full_dataset_reliability_physical_proxy/phase48_reliability_summary.json
analysis/phase48_full_dataset_reliability_physical_proxy/phase48_reliability_summary.md
```

## Diagnostic Execution Evidence

The Phase 48 readiness and summary artifacts record:

```text
checkpoint_found = true
diagnostics_executed = true
evaluated_split = test
evaluated_scenarios = 48
evaluated_windows = 384
no_training = true
no_swe_pinn = true
level5_supported = false
```

This confirms that the Phase 47 checkpoint was found and diagnosed. It also confirms that Phase 48 remained diagnostic-only.

## Mean Reliability Metrics

Mean metrics across the evaluated Phase 48 test diagnostics were:

```text
mean_rmse = 0.012037189189155709
mean_mae = 0.005252910632811514
mean_wet_dry_iou = 0.863043953275997
```

These values indicate that the Phase 47 baseline retained strong average depth-error and wet/dry agreement behavior under the Phase 48 diagnostic pass.

## Wet/Dry Error Findings

Phase 48 separated overall wet/dry agreement from false-dry and false-wet behavior:

```text
mean_wet_dry_iou = 0.863043953275997
mean_false_dry_rate = 0.0911363765964386
mean_false_wet_rate = 0.003937674554837349
```

The wet/dry IoU remained strong on average. False-dry behavior remains operationally important because false-dry predictions can suppress warnings where target pixels are wet. False-wet behavior was much lower on average, but it still matters because false warnings can reduce warning credibility.

## Volume-Response Proxy Findings

Phase 48 computed a summed-depth volume-response proxy:

```text
mean_absolute_relative_volume_bias_proxy = 0.021456503649973275
```

This is a physical proxy for aggregate flood-response behavior. It should be interpreted as a diagnostic summary of summed predicted depth versus summed target depth, not as strict conservation, full mass conservation, SWE consistency, or hydrodynamic closure.

## Warning-Level Findings

Phase 48 produced conservative warning-level screening labels:

```text
reliable = 1
caution = 12
high-risk = 35
```

The labels are diagnostic screening labels. They are not calibrated probabilities and should not be interpreted as probabilistic risk estimates.

## Interpretation of Conservative High-Risk Labels

The large `high-risk` count reflects conservative screening rules. A scenario can be labeled `high-risk` if it triggers any upper-quartile error proxy, low wet/dry IoU, high false-dry rate, high false-wet rate, or high volume-bias proxy.

This means the high-risk count is intentionally sensitive to possible warning failure modes. It should not be read as proof of poor overall model skill. The mean metrics remain strong, and the labels are intended to identify where the warning framework needs conservative handling, review, or additional diagnostic context.

## What Phase 48 Demonstrates

Phase 48 demonstrates that:

- The Phase 47 checkpoint was found and evaluated.
- No-training reliability and physical proxy diagnostics can be executed on the full Phase 45 test split.
- The Phase 47 baseline retained strong mean RMSE, MAE, and wet/dry IoU in this diagnostic pass.
- Wet/dry false-dry and false-wet behavior can be summarized at diagnostic scale.
- Summed-depth volume-response proxy behavior can be summarized without claiming conservation.
- Conservative warning labels are available for Phase 49 warning-framework extension.

## What Phase 48 Does Not Demonstrate

Phase 48 does not demonstrate:

- New training performance.
- seed123 or seed202 behavior.
- Seed-sweep robustness.
- Hyperparameter-sweep robustness.
- 256x256, tile, multiscale, or full 500x500 performance.
- Benefits from a new loss, new architecture, or new configuration.
- SWE residual behavior.
- PINN behavior.
- Level 5 support.
- Strict conservation.
- Full mass conservation.
- Hydrodynamic closure.

## Guardrails

Phase 48 remains bounded by the following guardrails:

- No training was run.
- No seed123 or seed202 was run.
- No seed sweep was performed.
- No hyperparameter sweep was performed.
- No model architecture, loss, or training configuration was modified.
- No 256x256 training was run.
- No tile or multiscale training was run.
- No full 500x500 training was run.
- No SWE residual was implemented.
- No PINN was implemented.
- No Level 5 support is claimed.
- No strict conservation, full mass conservation, or hydrodynamic closure is claimed.

## Recommended Next Step

Proceed to Phase 49 full-dataset warning-framework extension using the Phase 48 scenario warning labels as conservative diagnostics. Phase 49 should treat these labels as screening inputs for warning logic and reporting, not as calibrated probabilities.

Phase 49 should not use Phase 48 as authorization for uncontrolled training expansion, seed expansion, higher-resolution training, tile or multiscale training, full 500x500 training, sweeps, or new loss redesign.

## Final Conclusion

Phase 48 completed the intended diagnostic-only evaluation of the Phase 47 128x128 full-dataset baseline. It found the checkpoint, diagnosed 48 test scenarios and 384 windows, preserved the no-training and no-SWE/PINN guardrails, and selected `phase48_diagnostics_ready_for_warning_framework_extension`.

The findings support Phase 49 warning-framework extension under conservative Level 4+ framing. They do not support Level 5 claims, SWE/PINN claims, strict conservation claims, full mass conservation claims, hydrodynamic closure claims, or uncontrolled training expansion.
