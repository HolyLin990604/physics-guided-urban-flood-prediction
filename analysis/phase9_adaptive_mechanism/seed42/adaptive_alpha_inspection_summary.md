# Phase 9 Adaptive Mechanism Inspection

- run root: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42`
- checkpoint: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42/checkpoints/best.pt`
- split: `val`
- inspected batches: `8`
- inspected samples: `16`
- adaptive alpha range: `0.1`

## What Was Inspected

- Loaded the saved `temporal_rainfall_gate.adaptive_alpha_mlp` weights from the adapt010 checkpoint.
- Recomputed the bounded adaptive multiplier from batch `future_rainfall` only.
- Did not run training, update checkpoint files, or write into the run directory.

## Available Signals

- Available: per-sample, per-forecast-step adaptive multiplier `1 + adaptive_alpha_range * tanh(mlp(future_rainfall))`.
- Not inspected in this first pass: gate channel values, decoder activations, gradients, or prediction changes with the scalar disabled.

## First-Pass Reading

- The adaptive mechanism appears `broadly varying within the configured range` for the inspected subset.
- Overall mean multiplier: `1.0471758`.
- Overall range: `1.0207511` to `1.0980926`.
- Near lower bound count: `0`.
- Near upper bound count: `0`.

## Limitations

- This is a limited evaluation-time inspection over the requested number of batches.
- The scalar is derived from the checkpoint MLP and dataset rainfall, not from pre-existing saved scalar artifacts.
- The scalar only multiplies the protected active response path; this report does not quantify downstream prediction sensitivity.

## Per-Step Summary

| step | count | mean | std | min | max | p05 | p50 | p95 | near lower | near upper |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 16 | 1.0506971 | 0.020430038 | 1.0249382 | 1.0886283 | 1.0278722 | 1.0442771 | 1.0864708 | 0 | 0 |
| 1 | 16 | 1.0523499 | 0.021468584 | 1.0259655 | 1.094053 | 1.0267662 | 1.0462466 | 1.0899845 | 0 | 0 |
| 2 | 16 | 1.0509271 | 0.021781885 | 1.0261248 | 1.0980926 | 1.0263912 | 1.0475855 | 1.0950629 | 0 | 0 |
| 3 | 16 | 1.0500273 | 0.020337513 | 1.0261248 | 1.0980926 | 1.0263912 | 1.0441623 | 1.0861855 | 0 | 0 |
| 4 | 16 | 1.0493655 | 0.020207682 | 1.0239619 | 1.0900288 | 1.0272018 | 1.0418954 | 1.0841747 | 0 | 0 |
| 5 | 16 | 1.0495113 | 0.020516019 | 1.0239619 | 1.0900288 | 1.0272018 | 1.041638 | 1.0841747 | 0 | 0 |
| 6 | 16 | 1.0466627 | 0.019205719 | 1.0233743 | 1.0879669 | 1.0274812 | 1.0403679 | 1.0863055 | 0 | 0 |
| 7 | 16 | 1.0472992 | 0.020299227 | 1.0222052 | 1.094053 | 1.0258261 | 1.0403679 | 1.085457 | 0 | 0 |
| 8 | 16 | 1.0457363 | 0.020612952 | 1.0222052 | 1.094053 | 1.0251449 | 1.038338 | 1.085457 | 0 | 0 |
| 9 | 16 | 1.0428903 | 0.016378138 | 1.0212337 | 1.0822165 | 1.024902 | 1.0396268 | 1.0752257 | 0 | 0 |
| 10 | 16 | 1.0402485 | 0.017858881 | 1.0207511 | 1.0900288 | 1.0231592 | 1.0343887 | 1.0751568 | 0 | 0 |
| 11 | 16 | 1.0403943 | 0.018279896 | 1.0207511 | 1.0900288 | 1.0231592 | 1.0343887 | 1.0751568 | 0 | 0 |