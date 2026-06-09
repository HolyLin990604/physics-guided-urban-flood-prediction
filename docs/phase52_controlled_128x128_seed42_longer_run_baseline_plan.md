# Phase 52 Controlled 128x128 Seed42 Longer-Run Baseline Plan

## 1. Executive Summary

Phase 52 is the controlled training phase authorized by the Phase 51 reviewed expansion decision. It will repeat the established Phase 47 UrbanFlood24 full-dataset route at 128x128 with seed42 while changing only the training horizon from 10 epochs to a recommended cap of 40 epochs.

The purpose is to determine whether the Phase 47 route continues to improve, plateaus, overfits, or degrades under longer training. Phase 52 must preserve the Phase 47 dataset split, sample construction, model, loss, optimization basis, and architecture so that training horizon remains the primary changed factor.

Planned implementation and output paths:

```text
config = configs/train_phase52_full_downsample128_seed42_40e.json
script = scripts/train_phase52_controlled_longer_run.py
output_dir = runs/phase52_full_downsample128_seed42_40e/
analysis_dir = analysis/phase52_controlled_128x128_seed42_longer_run/
```

Phase 52 is not a seed replication, resolution expansion, model redesign, loss redesign, physics-method expansion, or claim escalation.

## 2. Phase 51 Authorization

Phase 51 completed a decision-only review and selected:

```text
selected_decision = phase51_authorize_128x128_seed42_longer_run
authorized_next_phase = phase52_controlled_128x128_seed42_longer_run_baseline
```

The authorization is bounded to a separate Phase 52 run with:

```text
resolution = 128
seed = 42
reference_epochs = 10
target_epochs = 40
train_test_split_unchanged = true
model_loss_config_architecture_unchanged = true
separate_non_overwriting_output_required = true
phase47_comparison_required = true
```

Phase 51 did not run training and did not establish that 40 epochs will improve performance. It authorized Phase 52 to test that question under controlled conditions.

## 3. Phase 47 Reference Baseline

Phase 47 is the fixed reference for the Phase 52 comparison:

```text
resolution = 128
seed = 42
epochs = 10
train_samples = 960
test_samples = 384
best_test_rmse = 0.01109213042097205
test_mae = 0.00525291082279485
test_wet_dry_iou = 0.8255524213115374
test_rollout_stability = 0.998722607580324
```

Additional Phase 47 final-epoch context:

```text
test_step_rmse_std = 0.0012824604989987165
test_loss = 0.00110163203172912
```

Phase 52 must compare both its best epoch and final epoch against these Phase 47 results. The comparison must not substitute a different split, seed, resolution, sample count, wet threshold, or metric definition.

## 4. Training Scope

Phase 52 will run one controlled UrbanFlood24 full-dataset baseline:

```text
phase = 52
resolution = 128
seed = 42
epochs = 40
train_samples_expected = 960
test_samples_expected = 384
training_scope = controlled_128x128_seed42_longer_run
```

The run must preserve the Phase 47 route:

- Use the same Phase 45 scenario and static indexes.
- Use the same 120-train / 48-test scenario split.
- Use the same 12 input steps and 12 prediction steps.
- Use the same sampling stride and maximum windows per scenario.
- Use the same rainfall alignment and known-forcing treatment.
- Use the same in-memory bilinear downsampling.
- Use the same model architecture and channel definitions.
- Use the same Smooth L1 loss, optimizer basis, learning rate, weight decay, gradient clipping, and wet threshold.
- Use the same batch-size and runtime basis unless execution must stop for a documented resource failure.

Only the phase identity, output locations, training-scope label, and epoch horizon should change from the Phase 47 controlled configuration.

## 5. Configuration Plan

Create:

```text
configs/train_phase52_full_downsample128_seed42_40e.json
```

The configuration should be derived directly from `configs/train_phase47_full_downsample128_seed42_10e.json` with these controlled changes:

```text
phase = 52
epochs = 40
output_dir = runs/phase52_full_downsample128_seed42_40e
analysis_dir = analysis/phase52_controlled_128x128_seed42_longer_run
training_scope = controlled_128x128_seed42_longer_run
```

The following values must remain unchanged:

```text
seed = 42
resolution = 128
dataset input_steps = 12
dataset pred_steps = 12
dataset sampling_stride = 24
dataset max_windows_per_scenario = 8
dataset rainfall_alignment = proportional_bin_mean_known_forcing
dataset downsample_method = torch.nn.functional.interpolate_bilinear
optimization batch_size = 2
optimization eval_batch_size = 2
optimization lr = 0.0003
optimization weight_decay = 0.0001
optimization loss = smooth_l1
optimization grad_clip_norm = 1.0
metrics wet_threshold = 0.05
```

The complete `model` block must match Phase 47. No Phase 52-only model, loss, architecture, seed, resolution, sweep, tile, multiscale, SWE, PINN, or Level 5 option may be added.

## 6. Script Plan

Create:

```text
scripts/train_phase52_controlled_longer_run.py
```

The script should reuse or conservatively adapt the Phase 47 training implementation. It must preserve the existing indexed dataset adapter, rainfall alignment, downsampling, model construction, dataloader construction, loss, optimizer, scheduler basis, metric computation, and deterministic seed handling.

The script must validate:

- `phase == 52`.
- `seed == 42`.
- `resolution == 128`.
- `epochs == 40` and never exceeds the 40-epoch cap.
- Phase 52 output and analysis paths are exact and non-overwriting.
- Scenario counts remain 120 train and 48 test.
- Sample counts remain 960 train and 384 test.
- Model, dataset, optimization, metric, and runtime settings match the controlled Phase 47 basis.
- Prohibited seed, sweep, resolution-expansion, tile, multiscale, SWE, PINN, and Level 5 keys are absent.

The script must support:

```text
python scripts/train_phase52_controlled_longer_run.py --config configs/train_phase52_full_downsample128_seed42_40e.json --dry-run
```

and:

```text
python scripts/train_phase52_controlled_longer_run.py --config configs/train_phase52_full_downsample128_seed42_40e.json
```

## 7. Output Directory Plan

Training outputs must be written only to:

```text
runs/phase52_full_downsample128_seed42_40e/
```

Analysis outputs must be written only to:

```text
analysis/phase52_controlled_128x128_seed42_longer_run/
```

The Phase 52 run must not overwrite or modify:

```text
runs/phase47_full_downsample128_baseline_seed42_10e/
analysis/phase47_controlled_downsample_baseline/
```

Planned run artifacts include:

```text
training_config_snapshot.json
metrics.json
metrics.csv
runtime_memory_notes.md
checkpoints/best.pt
checkpoints/final.pt
```

Planned analysis artifacts should include a Phase 52 training summary, direct Phase 47 comparison table, and concise findings inputs. Checkpoints remain local run artifacts and should not be committed.

## 8. Dry-Run Requirement

A successful dry run is mandatory before training:

```text
python scripts/train_phase52_controlled_longer_run.py --config configs/train_phase52_full_downsample128_seed42_40e.json --dry-run
```

The dry run must perform no optimization and create no run outputs. It must validate:

- Configuration guardrails.
- Required index presence and schema.
- Dataset and static-map availability.
- Train/test scenario counts.
- Train/test sample counts.
- Input, target, rainfall, and static tensor shapes.
- One model forward pass.
- Prediction and target shape equality.
- Finite forward-pass output.
- Exact planned training command.

Training must not start if any dry-run check fails.

## 9. Training Execution Requirement

After a successful dry run, execute exactly:

```text
python scripts/train_phase52_controlled_longer_run.py --config configs/train_phase52_full_downsample128_seed42_40e.json
```

The run should attempt the full authorized 40 epochs unless a predefined stop or failure criterion occurs. Every epoch must record train and held-out test metrics using the existing metric definitions.

The execution record must include:

- Epoch-level train and test loss.
- Epoch-level RMSE and MAE.
- Epoch-level wet/dry IoU.
- Epoch-level rollout stability.
- Epoch-level step RMSE standard deviation.
- Learning-rate trajectory.
- Total runtime and useful per-epoch runtime observations.
- CPU process memory observations and CUDA peak memory when applicable.
- Best epoch selected by held-out test RMSE.
- Final epoch status.

Completion of 40 epochs alone is not sufficient for a successful scientific result; numerical behavior and comparison outcomes must also be reviewed.

## 10. Evaluation and Comparison Plan

Phase 52 must evaluate:

1. The best Phase 52 epoch by test RMSE.
2. The Phase 52 final epoch at epoch 40.
3. The full Phase 52 metric trajectory.
4. Direct deltas against the Phase 47 10-epoch reference.

Required comparison fields:

```text
test_rmse
test_mae
test_wet_dry_iou
test_rollout_stability
test_step_rmse_std
test_loss
```

For each metric, report:

```text
phase47_reference
phase52_best_epoch_value
phase52_final_epoch_value
best_minus_phase47
final_minus_phase47
```

The review must identify whether longer training:

- Improves beyond Phase 47.
- Reaches a practical plateau.
- Produces a best epoch before epoch 40 followed by degradation.
- Creates a train/test divergence consistent with overfitting.
- Reduces rollout stability or wet/dry IoU despite improving aggregate error.
- Becomes numerically or operationally unstable.

Phase 48 reliability and physical-proxy diagnostics and Phase 49 warning-framework diagnostics should be reapplied or compared after training where compatible. Aggregate RMSE improvement must not override adverse reliability, proxy, or warning evidence.

## 11. Checkpoint and Metrics Retention

Phase 52 must retain:

```text
checkpoints/best.pt
checkpoints/final.pt
metrics.json
metrics.csv
training_config_snapshot.json
runtime_memory_notes.md
```

`best.pt` must record the selected epoch, model state, optimizer state, scheduler state, configuration, and best test RMSE. `final.pt` must retain the epoch-40 state, or the last valid state if execution stops under a documented failure criterion.

Metrics must retain all completed epochs, not only the best result. The summary must distinguish best-epoch metrics from final-epoch metrics and must not present the best checkpoint as though it were the epoch-40 result.

## 12. Stop and Failure Criteria

Stop before training if:

- The dry run fails.
- Phase 52 config values violate the controlled boundary.
- Phase 45 indexes or required dataset files are unavailable.
- Scenario or sample counts differ from the Phase 47 basis.
- Tensor shapes or model output shapes differ from the Phase 47 route.
- The Phase 52 output path would overwrite an existing incompatible run.
- Implementing the run requires a model, loss, architecture, data-route, seed, or resolution change.

Stop during training if:

- Loss or any required metric becomes NaN or infinite.
- Gradients or model outputs become non-finite.
- Checkpoint or metrics persistence fails.
- Memory usage becomes unsafe or repeatedly causes out-of-memory failure.
- Dataset reads or batch construction fail persistently.
- The process cannot continue without exceeding the 40-epoch cap or changing the authorized route.

Any stopped run must retain the last valid metrics and checkpoint when possible, document the exact failure, and must not silently restart with changed settings.

## 13. Guardrails

- Use only seed42.
- Use only 128x128.
- Recommended and maximum epoch cap is 40.
- Do not use seed123 or seed202.
- Do not perform seed replication.
- Do not run 256x256.
- Do not run tile, multiscale, or full 500x500 training.
- Do not run sweeps.
- Do not make model, loss, configuration-basis, or architecture changes beyond creating the controlled Phase 52 config and script.
- Do not redesign the loss.
- Do not add an SWE residual.
- Do not add a PINN.
- Do not make a Level 5 claim.
- Do not claim strict conservation, full mass conservation, or hydrodynamic closure.
- Do not make a calibrated probability claim.
- Do not make a production-readiness claim.
- Compare directly against the Phase 47 10-epoch baseline.
- Do not overwrite Phase 47 or other prior-phase artifacts.
- Do not treat an improved aggregate metric as authorization for further expansion.

## 14. Success Criteria

Phase 52 is operationally successful if:

- The mandatory dry run passes.
- Exactly one 128x128 seed42 run is executed.
- The run uses the controlled Phase 47 data, sample, model, loss, and optimization basis.
- The run completes up to 40 epochs or stops under a documented predefined criterion.
- All completed epochs have finite, retained metrics.
- Best and final checkpoints are retained separately.
- Phase 47 artifacts remain unchanged.
- Best and final Phase 52 results are directly compared with Phase 47.
- Reliability, physical-proxy, and warning implications are reviewed conservatively.
- All claim and expansion guardrails remain intact.

Scientific success does not require Phase 52 to outperform Phase 47. A clear finding of improvement, plateau, overfitting, degradation, or instability is valid if it is supported by the controlled trajectory and retained evidence.

No Phase 52 result automatically authorizes seed replication, higher resolution, new losses, architecture changes, SWE/PINN work, or stronger claims.

## 15. Final Conclusion

Phase 52 will implement and run the single controlled longer-horizon baseline authorized by Phase 51:

```text
phase52_controlled_128x128_seed42_longer_run_baseline
```

It will preserve the Phase 47 128x128 seed42 route and extend only the training horizon from 10 epochs to a maximum of 40 epochs. The run will use separate outputs, require a successful dry run, retain best and final checkpoints and complete metrics, and directly compare best-epoch and final-epoch behavior against the Phase 47 reference.

All seed replication, higher-resolution, tile, multiscale, full-resolution, sweep, model redesign, loss redesign, SWE/PINN, Level 5, conservation, hydrodynamic-closure, calibrated-probability, production-readiness, and uncontrolled-expansion paths remain outside Phase 52.
