# Phase 47 Controlled Full Dataset Downsample Baseline Findings

## 1. Executive Summary

Phase 47 completed the single controlled UrbanFlood24 full-dataset 128x128 downsample baseline pilot authorized for seed42 and 10 epochs.

This is the first actual UrbanFlood24 full-dataset baseline training after the Phase 43-46 readiness work. The run completed successfully and produced finite train and test metrics.

The selected decision is:

```text
phase47_controlled_128_downsample_seed42_pilot_completed
```

The final held-out test metrics are strong for a first controlled 128x128 full-dataset baseline:

```text
test_rmse = 0.01109213042097205
test_mae = 0.00525291082279485
test_wet_dry_iou = 0.8255524213115374
test_rollout_stability = 0.998722607580324
test_step_rmse_std = 0.0012824604989987165
```

These results support the viability of the Level 4+ full-dataset route. They do not support Level 5 claims, SWE/PINN claims, strict conservation claims, hydrodynamic closure claims, or immediate uncontrolled training expansion.

## 2. Inputs and Outputs

Primary training command:

```text
python scripts/train_phase47_full_downsample_baseline.py --config configs/train_phase47_full_downsample128_seed42_10e.json
```

Primary configuration:

```text
configs/train_phase47_full_downsample128_seed42_10e.json
```

Primary training script:

```text
scripts/train_phase47_full_downsample_baseline.py
```

Committed analysis outputs:

```text
analysis/phase47_controlled_downsample_baseline/metrics.csv
analysis/phase47_controlled_downsample_baseline/metrics.json
analysis/phase47_controlled_downsample_baseline/phase47_training_summary.json
analysis/phase47_controlled_downsample_baseline/phase47_training_summary.md
analysis/phase47_controlled_downsample_baseline/runtime_memory_notes.md
analysis/phase47_controlled_downsample_baseline/training_config_snapshot.json
```

Local run directory:

```text
runs/phase47_full_downsample128_baseline_seed42_10e/
```

The local run directory may contain checkpoints or runtime artifacts. Checkpoints should remain local and should not be committed.

## 3. Training Scope

Phase 47 trained one controlled full-dataset downsample baseline with the following scope:

```text
phase = 47
seed = 42
resolution = 128
epochs = 10
train_samples = 960
test_samples = 384
best_test_rmse = 0.01109213042097205
no_swe_pinn = true
level5_supported = false
```

The run used the existing Level 4+ supervised model route with adapter plumbing for Phase 45 indexed full-dataset compatibility. It was not a model-family redesign and was not a new physics-loss experiment.

## 4. Controlled Authorization Boundary

The completed run stayed within the narrow Phase 47 authorization boundary:

- One seed only: seed42.
- One resolution only: 128x128 downsample.
- One pilot length only: 10 epochs.
- Full UrbanFlood24 indexed train/test split from the Phase 45/46 readiness path.
- Level 4+ supervised baseline framing.
- No SWE residuals.
- No PINN components.
- No Level 5 claims.
- No seed sweep.
- No 256x256, tile, multiscale, or full 500x500 training.
- No uncontrolled hyperparameter search.

This findings document records the result of that bounded pilot. It does not expand the authorization boundary.

## 5. Training Completion Evidence

The pilot completed all 10 authorized epochs and produced finite training and held-out test metrics.

Completion evidence:

```text
selected_decision = phase47_controlled_128_downsample_seed42_pilot_completed
phase = 47
seed = 42
resolution = 128
epochs = 10
train_samples = 960
test_samples = 384
best_test_rmse = 0.01109213042097205
```

The final epoch reported finite loss, MAE, RMSE, rollout stability, step RMSE standard deviation, and wet/dry IoU for both train and test splits.

## 6. Final Test Metrics

Epoch 10 final held-out test metrics:

```text
test_loss = 0.00110163203172912
test_mae = 0.00525291082279485
test_rmse = 0.01109213042097205
test_rollout_stability = 0.998722607580324
test_step_rmse_std = 0.0012824604989987165
test_wet_dry_iou = 0.8255524213115374
```

The best recorded test RMSE for this controlled pilot was:

```text
best_test_rmse = 0.01109213042097205
```

## 7. Final Train Metrics

Epoch 10 final train metrics:

```text
train_loss = 0.00115450383894616
train_mae = 0.005356151910382323
train_rmse = 0.01145584367623087
train_rollout_stability = 0.998658082758387
train_step_rmse_std = 0.0013474915721872094
train_wet_dry_iou = 0.8562279426647971
```

The train and test metrics are broadly aligned at epoch 10, which is a useful first indication that the controlled baseline is behaving coherently. This should be treated as pilot evidence, not as a final generalization claim.

## 8. Training Trajectory

The pilot showed clear improvement across the 10 authorized epochs:

```text
test_rmse: 0.0922387704437521 -> 0.01109213042097205
test_mae: 0.029571487813276082 -> 0.00525291082279485
test_wet_dry_iou: 0.2572032731241052 -> 0.8255524213115374
```

The trajectory indicates that the model learned from the controlled full-dataset 128x128 setup during the pilot window. It does not by itself establish robustness across additional seeds, resolutions, architectures, loss designs, or deployment conditions.

## 9. Interpretation

Phase 47 provides the first concrete evidence that the UrbanFlood24 full-dataset Level 4+ route can train successfully at 128x128 under a controlled boundary.

The finite metrics, improved trajectory, and strong final held-out test RMSE support continuing with a cautious full-dataset baseline program. The wet/dry IoU improvement is also meaningful for a first controlled baseline because it suggests the model is learning a useful flood extent signal, not only reducing aggregate numeric error.

The interpretation should remain conservative. The run is a single seed42 10-epoch pilot at 128x128. It is not yet a multi-seed reliability result, not a higher-resolution result, and not a physics-closure result.

## 10. What Phase 47 Demonstrates

Phase 47 demonstrates:

- The single controlled 128x128 full-dataset downsample seed42 10-epoch pilot completed.
- The Phase 45/46 full-dataset readiness path can support actual baseline training.
- The training path produced finite metrics.
- The Level 4+ full-dataset route is viable at 128x128 for this controlled pilot.
- The held-out test metrics are strong for a first controlled 128x128 baseline.
- The training trajectory improved substantially from epoch 1 to epoch 10.
- The project now has a concrete full-dataset baseline artifact to review before any expansion.

## 11. What Phase 47 Does Not Demonstrate

Phase 47 does not demonstrate:

- Level 5 support.
- SWE behavior.
- PINN behavior.
- Strict conservation.
- Full mass conservation.
- Hydrodynamic closure.
- Reliability across seed123 or seed202.
- Reliability across a seed sweep.
- Viability of 256x256 training.
- Viability of tile training.
- Viability of multiscale training.
- Viability of full 500x500 training.
- That new proxy-loss redesign is needed or authorized.
- That uncontrolled training expansion is appropriate.

These limitations should remain explicit in downstream documentation and decisions.

## 12. Guardrails

The following guardrails remain active after Phase 47:

- Do not claim Level 5 support.
- Do not claim SWE/PINN behavior.
- Do not claim strict conservation, full mass conservation, or hydrodynamic closure.
- Do not start seed123 or seed202 expansion without review.
- Do not start seed sweeps without review.
- Do not start 256x256, tile, multiscale, or full 500x500 training without review.
- Do not redesign losses or add new physics proxy losses without a separate reviewed plan.
- Do not commit checkpoints from `runs/phase47_full_downsample128_baseline_seed42_10e/`.
- Keep Phase 47 findings framed as a controlled 128x128 seed42 pilot result.

## 13. Recommended Next Step

The recommended next step is a conservative review and sync of the Phase 47 baseline artifacts before any training expansion.

Reasonable next paths after review are:

```text
Phase 48 full-dataset reliability and physical proxy diagnostics
```

or:

```text
formal Phase 47 baseline review before any expansion
```

The next step should not be immediate uncontrolled training expansion. Any seed123/seed202 expansion, 256x256 run, tile route, multiscale route, full 500x500 route, sweep, or loss redesign should require a separate reviewed authorization boundary.

## 14. Final Conclusion

Phase 47 completed the first controlled UrbanFlood24 full-dataset 128x128 downsample baseline training pilot after the Phase 43-46 readiness work. The seed42 10-epoch run completed successfully and produced finite, strong first-baseline metrics, including:

```text
test_rmse = 0.01109213042097205
test_mae = 0.00525291082279485
test_wet_dry_iou = 0.8255524213115374
test_rollout_stability = 0.998722607580324
test_step_rmse_std = 0.0012824604989987165
```

The result supports the viability of the Level 4+ full-dataset route at 128x128. It does not support Level 5, SWE/PINN, strict conservation, full mass conservation, hydrodynamic closure, seed expansion, higher-resolution training, tile/multiscale/full-resolution training, sweeps, or new loss redesign.

The conservative final decision is:

```text
phase47_controlled_128_downsample_seed42_pilot_completed
```
