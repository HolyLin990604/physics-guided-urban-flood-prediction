# Stage 2A Baseline: U-Net + TCN Flood Forecasting

## Input / Output Shapes
- `past_flood`: `[B, Tin, 1, 128, 128]`
- `past_rainfall`: `[B, Tin, 1]`
- `future_rainfall`: `[B, Tout, 1]`
- `static_maps`: `[B, 3, 128, 128]`
- `future_flood` target / prediction: `[B, Tout, 1, 128, 128]`

`Tin` and `Tout` come from the dataset adapter windowing config, so the baseline supports variable forecast horizons after windowing as long as the adapter emits the same interface.

## Model Structure
- A shared U-Net-style spatial encoder processes each past flood frame concatenated with static maps.
- Encoder bottleneck features are conditioned on `past_rainfall` and passed through a TCN across time at each bottleneck cell.
- The last temporal context is combined with `future_rainfall` and a normalized future-step embedding.
- A second TCN refines future bottleneck seeds across forecast steps.
- A shared U-Net-style decoder reconstructs each future flood map using configurable skip fusion from the past encoder stream:
  `temporal_mean`, `last_step`, or `learned_weighted`.

`temporal_mean` remains a useful baseline, but it can blur transient process cues because it collapses all past skip states into a single average before decoding.

This is a baseline process-prediction model, not the original U-RNN architecture.

The future bottleneck seeds are latent forecast-conditioned representations. They are decoder-side latent features, not explicit hydrodynamic state variables.

## Dataset Assumptions
- Raw `flood.npy` sequences are usually `(36, 128, 128)` with some `location2` events at `(48, 128, 128)`.
- Raw `rainfall.npy` sequences are `(18,)`.
- Static geodata maps are `(128, 128)` for `absolute_DEM`, `impervious`, and `manhole`.
- Training uses an event-level split inside the raw `train` partition to reduce leakage between windows from the same event.

## Rainfall Alignment Assumption
- Rainfall-to-flood alignment is a modeling assumption because the raw files do not provide explicit one-to-one temporal correspondence.
- The dataset adapter makes the alignment explicit and configurable.
- Default `alignment_mode` is `mass_preserving`, which is the most honest default when the raw rainfall samples are interpreted as rainfall amount per coarse time bin because it preserves cumulative rainfall up to floating-point error.
- Other modes (`piecewise_constant`, `linear`, `repeat_if_integer_ratio`) remain available for ablation and diagnostics.

## Metrics and Outputs
- Metrics: `RMSE`, `MAE`, `wet_dry_iou`, `rollout_stability`, and `step_rmse_std`.
- Evaluation artifacts include predicted flood maps, target flood maps, and absolute error maps saved as `.npz`; `.png` grids are also written when `matplotlib` is installed.
- Process-oriented visualization now includes predicted-vs-target flood-depth time series for either selected pixels or region-averaged depth, configured from JSON.

## Stage 2B Hook Points
- Stage 2B keeps the baseline architecture intact and adds optional loss terms on top of the supervised data loss.
- Physical constraint surrogates:
  1. `non_negativity`
  2. `wet_dry_consistency`
- Physical guidance terms:
  1. `rainfall_depth_consistency`
  2. `topography_regularization`
  3. `continuity_inspired`

These terms are not a full shallow-water-equation closure. They are lightweight physically motivated regularizers and guidance terms for ablation and incremental refinement.
