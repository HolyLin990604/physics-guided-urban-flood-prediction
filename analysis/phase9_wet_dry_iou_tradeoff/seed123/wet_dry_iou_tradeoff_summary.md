# Phase 9 Wet/Dry IoU Trade-Off Diagnosis: seed123

- wet threshold: `0.05`
- near-threshold margin: `+/- 0.005`
- static run root: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123`
- adapt010 run root: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123`
- selected artifact epoch: `epoch_040`
- selected batches: `val_batch_0000, val_batch_0001`

## Artifact Availability

- val_batch_0000: static `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/visualizations/epoch_040/val_batch_0000/forecast_maps.npz`, adapt010 `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/visualizations/epoch_040/val_batch_0000/forecast_maps.npz`
- val_batch_0001: static `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/visualizations/epoch_040/val_batch_0001/forecast_maps.npz`, adapt010 `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/visualizations/epoch_040/val_batch_0001/forecast_maps.npz`

## Missing Or Limited Comparisons

- No missing paired batch artifacts in the selected epoch.

## First-Pass Interpretation

- The IoU give-back is mixed error mode, FN-leaning overall, with step-specific FP increases also present; adapt010 also has a higher near-threshold prediction ratio.
- This is a paired artifact diagnosis only; it does not replace the full validation metrics.
- Step-level conclusions are based only on the currently available paired artifact subset.

## Aggregate Deltas

| metric | delta |
|---|---:|
| mean IoU delta | -0.013943 |
| total FP delta | 1284 |
| total FN delta | 1331 |
| near-threshold prediction ratio delta | 0.000593 |

## Mean Per-Step IoU In Compared Artifacts

| model | mean IoU | total FP | total FN |
|---|---:|---:|---:|
| static_af025 | 0.678892 | 15797 | 36545 |
| adapt010 | 0.664950 | 17081 | 37876 |

## Step-Level Highlights

| highlight | step | static IoU | adapt010 IoU | IoU delta | FP delta | FN delta | static pred wet ratio | adapt010 pred wet ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| largest IoU drop | 9 | 0.754548 | 0.664582 | -0.089966 | 2210 | -272 | 0.181808 | 0.219681 |
| largest FN increase | 10 | 0.736915 | 0.739936 | 0.003020 | -1172 | 826 | 0.193436 | 0.162949 |
| largest FP increase | 9 | 0.754548 | 0.664582 | -0.089966 | 2210 | -272 | 0.181808 | 0.219681 |