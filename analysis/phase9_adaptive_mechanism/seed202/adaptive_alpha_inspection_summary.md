# Phase 9 Adaptive Mechanism Inspection

- run root: `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202`
- checkpoint: `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202/checkpoints/best.pt`
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
- Overall mean multiplier: `0.98847488`.
- Overall range: `0.96848202` to `0.99580455`.
- Near lower bound count: `0`.
- Near upper bound count: `0`.

## Limitations

- This is a limited evaluation-time inspection over the requested number of batches.
- The scalar is derived from the checkpoint MLP and dataset rainfall, not from pre-existing saved scalar artifacts.
- The scalar only multiplies the protected active response path; this report does not quantify downstream prediction sensitivity.

## Per-Step Summary

| step | count | mean | std | min | max | p05 | p50 | p95 | near lower | near upper |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 16 | 0.98814533 | 0.0068264407 | 0.96848202 | 0.99452895 | 0.97645909 | 0.99071318 | 0.99350359 | 0 | 0 |
| 1 | 16 | 0.98764845 | 0.0074471809 | 0.96848202 | 0.99481863 | 0.97203536 | 0.99071318 | 0.99357601 | 0 | 0 |
| 2 | 16 | 0.98785315 | 0.0070413392 | 0.96880865 | 0.99496245 | 0.97211702 | 0.99053702 | 0.99420781 | 0 | 0 |
| 3 | 16 | 0.98846206 | 0.0062288186 | 0.96880865 | 0.99496245 | 0.97844131 | 0.99053702 | 0.99420781 | 0 | 0 |
| 4 | 16 | 0.98860061 | 0.0050015453 | 0.97957796 | 0.99530268 | 0.98024417 | 0.98997524 | 0.99443664 | 0 | 0 |
| 5 | 16 | 0.98867363 | 0.0050650596 | 0.97957796 | 0.99530268 | 0.98024417 | 0.98997524 | 0.99472238 | 0 | 0 |
| 6 | 16 | 0.98766409 | 0.00799258 | 0.96848202 | 0.99539477 | 0.96969938 | 0.99012864 | 0.9947454 | 0 | 0 |
| 7 | 16 | 0.98727767 | 0.0085681061 | 0.96848202 | 0.99557751 | 0.96969938 | 0.99012864 | 0.99500835 | 0 | 0 |
| 8 | 16 | 0.98790893 | 0.0080726692 | 0.96880865 | 0.99557751 | 0.97211702 | 0.9910489 | 0.99511622 | 0 | 0 |
| 9 | 16 | 0.98852732 | 0.0073792272 | 0.96880865 | 0.99572921 | 0.97402577 | 0.99152106 | 0.99515414 | 0 | 0 |
| 10 | 16 | 0.99043213 | 0.0054587691 | 0.97957796 | 0.99580455 | 0.98024417 | 0.99268082 | 0.99542814 | 0 | 0 |
| 11 | 16 | 0.99050516 | 0.0054927254 | 0.97957796 | 0.99580455 | 0.98024417 | 0.99291843 | 0.99542814 | 0 | 0 |