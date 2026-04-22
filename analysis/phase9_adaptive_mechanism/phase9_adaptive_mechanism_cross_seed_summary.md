# Phase 9 Adaptive Mechanism Cross-Seed Summary

Source files:

- `analysis/phase9_adaptive_mechanism/seed202/adaptive_alpha_summary.json`
- `analysis/phase9_adaptive_mechanism/seed123/adaptive_alpha_summary.json`
- `analysis/phase9_adaptive_mechanism/seed42/adaptive_alpha_summary.json`

All three inspections used `split=val`, `max_batches=8`, checkpoint-embedded config, and `saturation_eps=0.001`. The inspected scalar is the bounded adaptive multiplier:

`1 + adaptive_alpha_range * tanh(adaptive_alpha_mlp(future_rainfall))`

## Summary Table

| seed | inspected run root | split | batches | samples | scalar values | min | max | mean | std | near lower | near upper |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| seed202 | `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202` | val | 8 | 16 | 192 | 0.968482 | 0.995805 | 0.988475 | 0.006890 | 0 | 0 |
| seed123 | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123` | val | 8 | 16 | 192 | 1.013127 | 1.077193 | 1.031357 | 0.015915 | 0 | 0 |
| seed42 | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42` | val | 8 | 16 | 192 | 1.020751 | 1.098093 | 1.047176 | 0.020226 | 0 | 0 |

## Interpretation

Across the three inspected validation subsets, the adaptive multiplier stays within the configured `[0.9, 1.1]` range and does not register any near-lower-bound or near-upper-bound saturation counts. The values are close to identity in the bounded-mechanism sense, but not exactly identity: seed202 is slightly below 1.0 on average, while seed123 and seed42 are above 1.0.

Seed42 shows the broadest variation in this subset, with `std=0.020226` and range `1.020751` to `1.098093`. Seed202 is the narrowest and most conservative, with `std=0.006890` and range `0.968482` to `0.995805`. Seed123 is intermediate: `std=0.015915`, range `1.013127` to `1.077193`.

Seed42 comes closest to the upper bound numerically, but still does not meet the near-upper-bound threshold because its maximum is below `1.099`. Seed123 does not look mechanism-wise unusual relative to seed202 and seed42; its adaptive multiplier behavior sits between the lower, narrow seed202 pattern and the higher, wider seed42 pattern.

## Limitation

This comparison is limited to the first 8 validation batches per seed and uses the scalar summaries already emitted by the inspection script. It does not evaluate downstream prediction sensitivity or causal effects of changing the multiplier.
