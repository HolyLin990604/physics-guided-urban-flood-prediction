# Phase 52 Controlled Longer-Run Training Summary

- selected_decision: `phase52_controlled_128x128_seed42_longer_run_completed`
- seed: `42`
- resolution: `128`
- epochs_configured: `40`
- train_samples: `960`
- test_samples: `384`
- best_epoch: `40`
- phase47_reference_best_test_rmse: `0.01109213042097205`
- phase47_reference_test_mae: `0.00525291082279485`
- phase47_reference_test_wet_dry_iou: `0.8255524213115374`
- no_swe_pinn: `true`
- level5_supported: `false`

## Direct Phase 47 Comparison

| Metric | Phase 47 | Phase 52 best | Phase 52 final | Best - Phase 47 | Final - Phase 47 |
|---|---:|---:|---:|---:|---:|
| test_rmse | 0.01109213042097205 | 0.005160715272116552 | 0.005160715272116552 | -0.005931415148855497 | -0.005931415148855497 |
| test_mae | 0.00525291082279485 | 0.002410597107882495 | 0.002410597107882495 | -0.002842313714912355 | -0.002842313714912355 |
| test_wet_dry_iou | 0.8255524213115374 | 0.9130120601863988 | 0.9130120601863988 | 0.08745963887486141 | 0.08745963887486141 |
| test_rollout_stability | 0.998722607580324 | 0.9992842044060429 | 0.9992842044060429 | 0.0005615968257188797 | 0.0005615968257188797 |
| test_step_rmse_std | 0.0012824604989987165 | 0.0007178322914948391 | 0.0007178322914948391 | -0.0005646282075038774 | -0.0005646282075038774 |
| test_loss | 0.00110163203172912 | 0.0002713639403471764 | 0.0002713639403471764 | -0.0008302680913819436 | -0.0008302680913819436 |

This controlled run does not support Level 5, strict conservation, hydrodynamic closure, calibrated probability warning labels, or production-readiness claims.
