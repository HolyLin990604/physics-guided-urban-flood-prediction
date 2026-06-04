# Phase 48 Full Dataset Reliability Physical Proxy Diagnostics Plan

## Executive Summary

Phase 48 is a no-training diagnostic phase for the Phase 47 controlled 128x128 UrbanFlood24 full-dataset baseline. It diagnoses reliability, wet/dry failure modes, peak-depth behavior, timing behavior where available, and volume-response proxy behavior using the Phase 47 trained checkpoint and evaluation artifacts.

Phase 48 must not train a new model. It must not expand the experiment to new seeds, new resolutions, tile or multiscale training, SWE residuals, PINN components, or Level 5 claims.

The expected conservative decision is:

```text
phase48_diagnostics_requires_evaluation_pass
```

This decision applies if per-scenario prediction diagnostics are not already available from the Phase 47 run. If the necessary prediction or timestep-level evaluation artifacts already exist, the expected decision may instead be:

```text
phase48_diagnostics_ready_for_warning_framework_extension
```

## Background from Phase 45-47

Phase 45 completed full UrbanFlood24 dataset indexing and lightweight adapter preparation. It established the train/test scenario split and static geodata index needed for full-dataset operation:

```text
scenario_count_total = 168
train scenarios = 120
test scenarios = 48
static_index_rows = 6
training_authorized = false
```

Phase 46 completed no-training dataloader smoke, downsample, and tiling feasibility checks. It showed that indexed scenarios and static geodata could be opened, representative samples could be loaded, and 128x128 downsample batching was feasible under a Level 4+ framing:

```text
downsample_128_passed = true
downsample_256_passed = true
tile_checks_passed = true
batch_smoke_passed = true
memory_safe = true
level4_plus_supported = true
level5_supported = false
```

Phase 47 completed the first controlled UrbanFlood24 full-dataset 128x128 downsample seed42 10 epoch baseline pilot. Its result was:

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
test_rollout_stability = 0.998722607580324
test_step_rmse_std = 0.0012824604989987165
no_swe_pinn = true
level5_supported = false
```

Phase 47 provides a controlled baseline to diagnose. It does not establish final model performance across future settings, higher resolutions, new seeds, new training recipes, or unsupported hydrodynamic claims.

## Purpose of Reliability and Physical Proxy Diagnostics

The purpose of Phase 48 is to determine where the Phase 47 baseline is reliable, where it fails, and whether its outputs can support an extension of the Level 4+ warning framework.

The phase focuses on diagnostic evidence rather than model improvement. It should answer:

- Which scenarios show stable low-error behavior?
- Which scenarios show high wet/dry classification risk?
- Does the model systematically underpredict peak depths?
- Are peak times shifted when timestep-wise predictions are available?
- Does summed predicted depth show a plausible volume-response relationship against targets?
- Are failures concentrated by scenario, location, or event type?
- Are static-mask checks useful for explaining systematic errors?

These diagnostics are physical proxies only. They do not prove strict conservation, hydrodynamic closure, SWE consistency, or Level 5 capability.

## Inputs and Required Artifacts

Phase 48 uses the following existing inputs:

```text
configs/train_phase47_full_downsample128_seed42_10e.json
scripts/train_phase47_full_downsample_baseline.py
analysis/phase47_controlled_downsample_baseline/metrics.csv
analysis/phase47_controlled_downsample_baseline/metrics.json
analysis/phase47_controlled_downsample_baseline/phase47_training_summary.json
analysis/phase47_controlled_downsample_baseline/phase47_training_summary.md
analysis/phase45_full_dataset_indexing/scenario_index.csv
analysis/phase45_full_dataset_indexing/static_geodata_index.csv
runs/phase47_full_downsample128_baseline_seed42_10e
```

The planned diagnostic script is:

```text
scripts/analyze_phase48_full_dataset_reliability.py
```

The expected output directory is:

```text
analysis/phase48_full_dataset_reliability_physical_proxy/
```

Before computing diagnostics, the script should write a readiness record that confirms which required files are present and which prediction/evaluation artifacts are available.

## Diagnostic Scope

Phase 48 covers only the Phase 47 baseline:

```text
model_source = Phase 47 checkpoint or saved run state
dataset_source = Phase 45 indexed UrbanFlood24 full dataset
split_source = scenario_index.csv
resolution = 128
seed = 42
training = false
```

If compact per-scenario or timestep-level prediction artifacts are already available, Phase 48 may compute diagnostics directly from them.

If per-scenario prediction diagnostics are not available, Phase 48 should first run a no-training evaluation and diagnostic pass using the Phase 47 checkpoint and dataloader. This pass may generate compact CSV metrics and summaries. It must not train, write transformed training datasets, run new seed experiments, alter model weights, or reinterpret the Phase 47 run as a broader final benchmark.

## Reliability Diagnostics

Reliability diagnostics should measure scenario-level and timestep-level error variation across the Phase 47 test split.

Required metrics where artifacts permit:

- RMSE by scenario.
- MAE by scenario.
- Wet/dry IoU by scenario.
- Step-level RMSE.
- Step-level MAE where available.
- Step-level wet/dry IoU where available.
- Scenario-level reliability class.

The reliability class should be conservative and traceable. Recommended classes:

```text
reliable
caution
high-risk
```

A scenario should be marked `reliable` only when continuous depth errors, wet/dry agreement, and stability proxies are all acceptable. A scenario should be marked `caution` when at least one diagnostic is degraded but not severe. A scenario should be marked `high-risk` when errors indicate likely warning failure, repeated wet/dry mistakes, severe peak underprediction, or unstable timestep behavior.

## Wet/Dry Error Diagnostics

Wet/dry diagnostics should distinguish overall IoU from operationally important false states.

Required metrics where artifacts permit:

- Wet/dry IoU by scenario.
- False-dry rate.
- False-wet rate.
- False-dry count or pixel fraction.
- False-wet count or pixel fraction.
- Error concentration by timestep where timestep predictions are available.

False-dry behavior should receive special attention because it can suppress warnings in flooded regions. False-wet behavior should also be reported because it can reduce warning credibility and create unnecessary alert burden.

The wet/dry threshold must be documented in the diagnostic summary. If Phase 47 used a threshold in its evaluation code, Phase 48 should reuse that threshold unless there is a documented reason to report a secondary sensitivity check.

## Peak-Depth and Timing Diagnostics

Peak-depth diagnostics should identify whether the baseline underpredicts maximum flood depth at scenario or timestep level.

Required metrics where artifacts permit:

- Target peak depth by scenario.
- Predicted peak depth by scenario.
- Peak-depth bias.
- Peak-depth underprediction proxy.
- Peak-depth relative error where numerically stable.
- Peak timing error if timestep-wise predictions are available.

The peak-depth underprediction proxy should flag cases where predicted maximum depth is lower than target maximum depth by a meaningful margin. The threshold should be explicit in the diagnostic script and reported in `phase48_reliability_summary.md`.

Peak timing error should only be computed when timestep-wise predictions are available and aligned with target timesteps. If only aggregate metrics are available, Phase 48 should mark peak timing as unavailable rather than infer timing from insufficient artifacts.

## Volume-Response Proxy Diagnostics

Volume-response diagnostics should use summed depths as a proxy for aggregate flood response. This is not a strict mass-conservation diagnostic.

Required metrics where artifacts permit:

- Summed predicted depth by scenario.
- Summed target depth by scenario.
- Signed summed-depth bias.
- Absolute summed-depth error.
- Relative summed-depth error where numerically stable.
- Optional timestep-level summed-depth bias if timestep predictions are available.

The summary must label this as a volume-response proxy. It must not claim full mass conservation, hydrodynamic closure, or SWE consistency.

## Scenario / Location / Type Stratification

Phase 48 should join diagnostic outputs with `scenario_index.csv` to summarize reliability by available scenario metadata.

Recommended stratifications:

- Scenario ID.
- Train/test split confirmation.
- Location or area field if present.
- Event or scenario type field if present.
- Rainfall or forcing category if present.
- Any other existing metadata field that can be joined without manual relabeling.

The script should avoid inventing metadata categories not present in the indexed inputs. Missing metadata should be reported explicitly in the readiness or summary output.

## Optional Static-Mask Diagnostics

Static-mask diagnostics are optional and should run only if the Phase 45 static geodata index and dataloader provide aligned static masks for evaluated samples.

Potential checks:

- Error summary inside valid domain masks.
- Wet/dry error near static drainage, terrain, or land-cover masks if such channels are present and interpretable.
- Error concentration in masked-out or invalid regions.
- Scenario-level flags for unusual static-mask coverage.

These checks are explanatory diagnostics only. They should not become a new loss design, new training target, or Level 5 physical validation claim.

## Expected Outputs

Phase 48 should write outputs under:

```text
analysis/phase48_full_dataset_reliability_physical_proxy/
```

Expected files:

```text
phase48_diagnostic_readiness.json
scenario_reliability_metrics.csv
step_reliability_metrics.csv
wet_dry_error_metrics.csv
peak_depth_timing_metrics.csv
volume_response_proxy_metrics.csv
location_type_summary.csv
reliability_warning_levels.csv
phase48_reliability_summary.json
phase48_reliability_summary.md
```

If an output cannot be populated because prediction artifacts are missing, the script should still record that status in `phase48_diagnostic_readiness.json` and `phase48_reliability_summary.md`. Empty or partial CSVs should include enough columns to make the missing-data reason clear.

## Decision Criteria

Allowed decision candidates:

```text
phase48_diagnostics_ready_for_warning_framework_extension
phase48_diagnostics_completed_with_missing_prediction_artifacts
phase48_diagnostics_blocked_by_checkpoint_or_artifact_issue
phase48_diagnostics_requires_evaluation_pass
```

Decision guidance:

- Use `phase48_diagnostics_ready_for_warning_framework_extension` when required prediction/evaluation artifacts are available, diagnostics are computed, and warning-level reliability classes are usable for Level 4+ framework extension.
- Use `phase48_diagnostics_completed_with_missing_prediction_artifacts` when available aggregate diagnostics are summarized but missing artifacts prevent full per-scenario or timestep-level analysis.
- Use `phase48_diagnostics_blocked_by_checkpoint_or_artifact_issue` when the Phase 47 checkpoint, configuration, scenario index, static geodata index, or required run directory cannot be found or loaded.
- Use `phase48_diagnostics_requires_evaluation_pass` when Phase 47 summary metrics exist but per-scenario prediction diagnostics are not already available and must be generated by a no-training evaluation pass.

The expected conservative decision is `phase48_diagnostics_requires_evaluation_pass` if per-scenario prediction diagnostics are not already available. Otherwise, the expected decision is `phase48_diagnostics_ready_for_warning_framework_extension`.

## Guardrails

Phase 48 is bound by the following guardrails:

- No training.
- No seed123 or seed202.
- No seed sweep.
- No hyperparameter sweep.
- No 256x256 training.
- No tile training.
- No multiscale training.
- No full-500 training.
- No new loss redesign.
- No SWE residual.
- No PINN.
- No Level 5 support claim.
- No strict conservation claim.
- No full mass conservation claim.
- No hydrodynamic closure claim.
- Do not reinterpret Phase 47 as final model performance across all future settings.
- Treat diagnostics as Level 4+ reliability and physical proxy diagnostics only.
- Do not write transformed training datasets.
- Do not modify Phase 47 model weights.
- Do not silently change the Phase 47 test split.

## Success Criteria

Phase 48 succeeds when it produces a clear diagnostic readiness record and either computes or explicitly scopes the missing requirements for the planned reliability diagnostics.

Minimum success criteria:

- Required Phase 47 and Phase 45 input artifacts are checked.
- Availability of checkpoint, run directory, metrics, scenario index, static geodata index, and prediction artifacts is recorded.
- Per-scenario diagnostics are computed if predictions are available.
- A no-training evaluation pass is identified as required if predictions are not available.
- Reliability warning classes are defined as `reliable`, `caution`, and `high-risk`.
- Wet/dry false-dry and false-wet diagnostics are included where possible.
- Peak-depth and volume-response proxy diagnostics are included where possible.
- Missing timing diagnostics are clearly labeled if timestep predictions are unavailable.
- The final summary preserves Level 4+ framing and rejects Level 5/SWE/PINN claims.

## Final Conclusion

Phase 48 plans no-training reliability and physical proxy diagnostics for the Phase 47 full-dataset baseline. It should diagnose where the model is reliable, where it fails, and whether the Level 4+ warning framework can be extended, without claiming Level 5, SWE, or PINN behavior.
