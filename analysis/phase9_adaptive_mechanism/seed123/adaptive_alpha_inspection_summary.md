# Phase 9 Adaptive Mechanism Inspection

- run root: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123`
- checkpoint: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/checkpoints/best.pt`
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
- Overall mean multiplier: `1.0313571`.
- Overall range: `1.013127` to `1.0771929`.
- Near lower bound count: `0`.
- Near upper bound count: `0`.

## Limitations

- This is a limited evaluation-time inspection over the requested number of batches.
- The scalar is derived from the checkpoint MLP and dataset rainfall, not from pre-existing saved scalar artifacts.
- The scalar only multiplies the protected active response path; this report does not quantify downstream prediction sensitivity.

## Per-Step Summary

| step | count | mean | std | min | max | p05 | p50 | p95 | near lower | near upper |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 16 | 1.0259542 | 0.0090996895 | 1.0135089 | 1.047802 | 1.0147762 | 1.0235144 | 1.0428533 | 0 | 0 |
| 1 | 16 | 1.0263859 | 0.0093142196 | 1.0139362 | 1.047802 | 1.01533 | 1.0235144 | 1.0428533 | 0 | 0 |
| 2 | 16 | 1.0311564 | 0.017538376 | 1.0141503 | 1.0771929 | 1.0153835 | 1.0251202 | 1.0717223 | 0 | 0 |
| 3 | 16 | 1.0312736 | 0.017450723 | 1.0141503 | 1.0771929 | 1.0159253 | 1.0251202 | 1.0717223 | 0 | 0 |
| 4 | 16 | 1.0322066 | 0.014365669 | 1.0149012 | 1.0576326 | 1.0163844 | 1.0274932 | 1.0560807 | 0 | 0 |
| 5 | 16 | 1.0325121 | 0.014236822 | 1.0149012 | 1.0576326 | 1.0163844 | 1.0287838 | 1.0560807 | 0 | 0 |
| 6 | 16 | 1.034171 | 0.017076207 | 1.0151986 | 1.0703911 | 1.015661 | 1.0295203 | 1.0685132 | 0 | 0 |
| 7 | 16 | 1.0341727 | 0.016607818 | 1.0157946 | 1.0703911 | 1.01581 | 1.0301385 | 1.0685132 | 0 | 0 |
| 8 | 16 | 1.035153 | 0.018693868 | 1.0142707 | 1.0771929 | 1.0154136 | 1.0297015 | 1.0717223 | 0 | 0 |
| 9 | 16 | 1.033887 | 0.018395887 | 1.0142707 | 1.0771929 | 1.0159554 | 1.0258046 | 1.0717223 | 0 | 0 |
| 10 | 16 | 1.0295536 | 0.015771439 | 1.013127 | 1.0576326 | 1.0138425 | 1.0215531 | 1.0560807 | 0 | 0 |
| 11 | 16 | 1.0298591 | 0.015705862 | 1.013127 | 1.0576326 | 1.0138425 | 1.0217206 | 1.0560807 | 0 | 0 |