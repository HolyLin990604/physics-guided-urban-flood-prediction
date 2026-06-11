# Phase 52 Figure Summary

Generated figures:

- `phase52_metric_trajectory_40e.png`: test RMSE, test MAE, and test wet/dry IoU trajectories; epoch 40 is marked as best and final.
- `phase52_vs_phase47_key_metrics.png`: direct Phase 47 versus Phase 52 comparison for five key test metrics.
- `phase52_improvement_summary.png`: favorable changes relative to Phase 47.

Phase 52 epoch-40 test metrics:

| Metric | Phase 47 | Phase 52 | Change |
|---|---:|---:|---:|
| Test RMSE | 0.011092130421 | 0.00516071527212 | -0.00593141514886 |
| Test MAE | 0.00525291082279 | 0.00241059710788 | -0.00284231371491 |
| Wet/dry IoU | 0.825552421312 | 0.913012060186 | +0.0874596388749 |
| Rollout stability | 0.99872260758 | 0.999284204406 | +0.000561596825719 |
| Step RMSE std | 0.001282460499 | 0.000717832291495 | -0.000564628207504 |

Improvement summary:

- RMSE reduction: `53.47%`.
- MAE reduction: `54.11%`.
- Wet/dry IoU gain: `8.75` percentage points.
- Step RMSE std reduction: `44.03%`.

Source artifacts:

- `runs/phase52_full_downsample128_seed42_40e/metrics.csv`
- `analysis/phase52_controlled_128x128_seed42_longer_run/phase52_training_summary.json`

Scope and claim boundaries:

- Visualization only; no training was rerun and no training result was modified.
- These controlled metrics do not establish Level 5 capability, SWE/PINN modeling, strict conservation, hydrodynamic closure, calibrated probabilities, or production readiness.
