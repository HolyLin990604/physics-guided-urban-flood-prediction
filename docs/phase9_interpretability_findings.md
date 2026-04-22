# Phase 9 Interpretability Findings

## 1. Objective

Phase 9 is an interpretability and trade-off diagnosis stage for `adapt010` after completed Phase 8 Batch 2. Its purpose is to explain the observed `adapt010` behavior, especially the `seed123` wet/dry IoU give-back, using existing artifacts.

This is not a new architecture search. Phase 9 does not change `adaptive_alpha_range`, train new models, introduce new sweeps, or promote a new variant.

## 2. Inputs Used

This summary uses the current Phase 9 generated artifacts:

- `analysis/phase9_af025_vs_adapt010/phase9_af025_vs_adapt010_summary.md`
- `analysis/phase9_wet_dry_iou_tradeoff/seed123/wet_dry_iou_tradeoff_summary.md`
- `analysis/phase9_wet_dry_iou_tradeoff/seed123/wet_dry_step_highlights.json`
- `analysis/phase9_adaptive_mechanism/phase9_adaptive_mechanism_cross_seed_summary.md`
- `analysis/phase9_seed123_spatial_tradeoff/seed123_step09_10_spatial_diagnosis.md`

## 3. What Phase 9 Currently Establishes

The unified `af025` vs `adapt010` report confirms that `adapt010` remains useful because RMSE, MAE, and loss improve across all three required full `40e` comparisons:

| seed | RMSE/MAE/loss | wet/dry IoU | rollout stability |
|---|---|---|---|
| seed202 | adapt010 better | adapt010 better | static better |
| seed123 | adapt010 better | static better | adapt010 better |
| seed42 | adapt010 better | adapt010 better | static better |

The unresolved mixed signal is specifically wet/dry IoU on `seed123`: `val_wet_dry_iou` changes from `0.614842` for static `af025` to `0.606377` for `adapt010`.

Cross-seed adaptive multiplier inspection does not show `seed123` as mechanism-wise unusual. The inspected bounded multiplier stays within the configured `[0.9, 1.1]` range for `seed202`, `seed123`, and `seed42`, with no near-bound saturation counts in the inspected subsets.

Therefore, the current evidence is more consistent with a case-specific wet/dry boundary trade-off on `seed123` than with adaptive scalar saturation, runaway modulation, or an obviously unstable adaptive mechanism.

## 4. Seed123 Diagnosis

The first-pass wet/dry diagnosis used paired `forecast_maps.npz` artifacts from `epoch_040`, batches `val_batch_0000` and `val_batch_0001`. In this paired subset, `adapt010` has lower mean IoU than static `af025`:

- mean static IoU: `0.678892`
- mean adapt010 IoU: `0.664950`
- mean IoU delta: `-0.013943`
- total FP delta: `+1284`
- total FN delta: `+1331`
- near-threshold prediction ratio delta: `+0.000593`

The aggregate mode is mixed: both FP and FN increase across the paired subset, with a slight FN-leaning total error increase and a small increase in near-threshold predictions.

The step-level diagnosis localizes the clearest transition:

- Step 9 is the largest IoU drop and largest FP increase:
  - static IoU: `0.754548`
  - adapt010 IoU: `0.664582`
  - IoU delta: `-0.089966`
  - FP delta: `+2210`
  - FN delta: `-272`
  - prediction wet-area ratio increases from `0.181808` to `0.219681`

- Step 10 is the largest FN increase but not an IoU failure in the paired subset:
  - static IoU: `0.736915`
  - adapt010 IoU: `0.739936`
  - IoU delta: `+0.003020`
  - FP delta: `-1172`
  - FN delta: `+826`
  - prediction wet-area ratio decreases from `0.193436` to `0.162949`

The spatial diagnosis of steps 9 and 10 supports a step-dependent wet/dry margin interpretation. Step 9 is wet-expansive and FP-growth dominated; step 10 flips toward dry-conservative behavior, trading lower FP for higher FN. Boundary ratios are high for FP/FN errors in both models under a simple one-pixel target wet/dry boundary band, so the inspected errors appear concentrated around wet/dry margins rather than cleanly inside stable wet or dry regions.

Current best-supported interpretation for `seed123`: the IoU give-back is a mixed, margin-region, step-dependent threshold trade-off. It is not a uniform failure mode across all steps.

## 5. Mechanism Diagnosis

The adaptive mechanism inspection recomputed the bounded multiplier:

`1 + adaptive_alpha_range * tanh(adaptive_alpha_mlp(future_rainfall))`

using checkpoint-embedded config and `val` split samples. All three seeds used `max_batches=8`, giving `192` scalar values per seed.

| seed | multiplier min | multiplier max | mean | std | near lower | near upper |
|---|---:|---:|---:|---:|---:|---:|
| seed202 | 0.968482 | 0.995805 | 0.988475 | 0.006890 | 0 | 0 |
| seed123 | 1.013127 | 1.077193 | 1.031357 | 0.015915 | 0 | 0 |
| seed42 | 1.020751 | 1.098093 | 1.047176 | 0.020226 | 0 | 0 |

The multiplier remains bounded and non-saturating in the inspected subsets, with conservative-to-moderate variation around identity. `seed42` shows the broadest variation and comes closest to the upper bound, while `seed202` is the narrowest and slightly below identity on average.

`seed123` is intermediate. It does not look mechanism-wise unusual relative to `seed202` and `seed42`.

## 6. Current Interpretation

`adapt010` may still help overall because its adaptive protected response path improves continuous-depth objectives consistently: RMSE, MAE, and validation loss are better than static `af025` for `seed202`, `seed123`, and `seed42`.

Wet/dry IoU can still be mixed on `seed123` because IoU is threshold-sensitive. The current diagnostics show that `adapt010` can improve depth-oriented metrics while shifting predictions across the wet threshold in margin regions. In the inspected seed123 artifacts, step 9 expands the wet mask too much and loses IoU through FP growth; step 10 contracts the wet mask and increases FN while keeping IoU roughly flat to slightly better.

Currently ruled out, within the inspected evidence:

- A broad `adapt010` failure across RMSE/MAE/loss.
- A seed123-specific adaptive multiplier saturation event.
- A single consistent wet-expansive or dry-conservative failure mode on seed123.
- A need for a broader sweep based on these diagnostics alone.

Still unresolved:

- Whether the margin-region threshold trade-off is driven by rainfall timing, local depth magnitude, spatial boundary geometry, or a combination.
- Whether the same step-dependent wet-expansive to dry-conservative transition appears outside the currently inspected paired artifact subset.
- How much of the wet/dry IoU give-back is avoidable without weakening the RMSE/MAE/loss gains.

## 7. Next Narrow Question

The next narrow question is: for the seed123 margin-region transition around steps 9 and 10, are threshold-crossing errors mainly caused by small near-threshold depth shifts, or by spatial displacement of the wet boundary?
