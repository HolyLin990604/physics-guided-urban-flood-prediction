# Phase 52 Controlled 128x128 Seed42 Longer-Run Findings

## 1. Executive Summary

Phase 52 completed the controlled longer-run training authorized by Phase 51:

```text
selected_decision = phase52_controlled_128x128_seed42_longer_run_completed
seed = 42
resolution = 128
epochs_configured = 40
epochs_completed = 40
train_samples = 960
test_samples = 384
best_epoch = 40
final_epoch = 40
```

The Phase 52 result substantially improves over the directly comparable Phase 47 10-epoch baseline across all six reported test metrics. Test RMSE decreases from `0.01109213042097205` to `0.005160715272116552`, test MAE decreases from `0.00525291082279485` to `0.002410597107882495`, and wet/dry IoU increases from `0.8255524213115374` to `0.9130120601863988`.

The best observed test RMSE occurs at epoch 40, which is also the final configured epoch. The late-epoch trajectory is consistent with continued improvement or a late plateau within the 40-epoch cap, rather than early degradation. This finding does not authorize training beyond 40 epochs.

Phase 52 answers the bounded Phase 51 question for one 128x128 seed42 run. It does not establish seed robustness, higher-resolution feasibility, Level 5 support, SWE/PINN behavior, strict conservation, calibrated probabilities, or production readiness.

## 2. Phase 51 Authorization Recap

Phase 51 selected:

```text
selected_decision = phase51_authorize_128x128_seed42_longer_run
authorized_next_phase = phase52_controlled_128x128_seed42_longer_run_baseline
```

The authorization permitted one separate controlled run using the Phase 47 route at 128x128 with seed42, while extending the training horizon from 10 epochs to a maximum of 40 epochs. The data split, sample construction, model, loss, optimization basis, architecture, and metric definitions were to remain unchanged.

Phase 51 did not authorize seed123, seed202, 256x256 training, tile or multiscale training, full 500x500 training, sweeps, model or loss redesign, SWE residuals, PINN components, or stronger scientific and operational claims.

Phase 52 directly answers the authorized question: the established controlled route continued to improve materially when trained from 10 to 40 epochs under the fixed comparison basis.

## 3. Phase 52 Training Scope

Phase 52 used the following bounded scope:

```text
resolution = 128
seed = 42
epochs_configured = 40
epochs_completed = 40
train_samples = 960
test_samples = 384
training_scope = controlled_128x128_seed42_longer_run
no_swe_pinn = true
level5_supported = false
```

The run used the controlled Phase 47 data route and comparison basis. It changed the training horizon while retaining the same seed, resolution, train/test sample counts, model and loss basis, and evaluation definitions. Run artifacts were retained under:

```text
runs/phase52_full_downsample128_seed42_40e/
```

Checkpoints are local run artifacts and are not part of the committed findings.

## 4. Phase 47 Reference Baseline

Phase 47 is the direct 10-epoch reference:

```text
seed = 42
resolution = 128
epochs = 10
train_samples = 960
test_samples = 384
best_test_rmse = 0.01109213042097205
test_mae = 0.00525291082279485
test_wet_dry_iou = 0.8255524213115374
test_rollout_stability = 0.998722607580324
test_step_rmse_std = 0.0012824604989987165
test_loss = 0.00110163203172912
```

Because Phase 47 and Phase 52 share the controlled seed, resolution, and sample basis, this comparison isolates the longer training horizon more directly than a seed or resolution change would. It remains a comparison of two single-run checkpoints, not evidence of robustness across seeds or configurations.

## 5. Phase 52 Results

The selected Phase 52 result is:

```text
best_epoch = 40
final_epoch = 40
test_rmse = 0.005160715272116552
test_mae = 0.002410597107882495
test_wet_dry_iou = 0.9130120601863988
test_rollout_stability = 0.9992842044060429
test_step_rmse_std = 0.0007178322914948391
test_loss = 0.0002713639403471764
```

All required metrics are finite at epoch 40. The best-epoch and final-epoch values are identical because the selected best checkpoint occurs at the training cap.

## 6. Direct Metric Comparison

| Metric | Phase 47 10e | Phase 52 best/final 40e | Phase 52 - Phase 47 | Favorable relative change |
| --- | ---: | ---: | ---: | ---: |
| Test RMSE | 0.01109213042097205 | 0.005160715272116552 | -0.005931415148855497 | 53.47% lower |
| Test MAE | 0.00525291082279485 | 0.002410597107882495 | -0.002842313714912355 | 54.11% lower |
| Test wet/dry IoU | 0.8255524213115374 | 0.9130120601863988 | +0.08745963887486141 | 10.59% higher |
| Test rollout stability | 0.998722607580324 | 0.9992842044060429 | +0.0005615968257188797 | 0.056% higher |
| Test step RMSE standard deviation | 0.0012824604989987165 | 0.0007178322914948391 | -0.0005646282075038774 | 44.03% lower |
| Test loss | 0.00110163203172912 | 0.0002713639403471764 | -0.0008302680913819436 | 75.37% lower |

The lower RMSE, MAE, step RMSE variation, and loss are favorable. The higher wet/dry IoU and rollout-stability metric are also favorable. The comparison therefore shows broad improvement in the retained aggregate metrics rather than improvement limited to a single error measure.

These relative changes describe this controlled comparison only. They should not be generalized to other seeds, resolutions, datasets, event regimes, or deployment conditions.

## 7. Training Trajectory Interpretation

The retained late-epoch metrics show continued but smaller test-RMSE gains near the training cap. Test RMSE was `0.00533337455514508` at epoch 34, `0.0052452168874879135` at epoch 36, `0.005170888055242055` at epoch 38, and `0.005160715272116552` at epoch 40.

Small reversals occurred at individual late epochs, including epochs 37 and 39, but the lowest observed test RMSE was reached at epoch 40. Test loss likewise decreased from `0.00028908002968819346` at epoch 34 to `0.0002713639403471764` at epoch 40. Wet/dry IoU remained around `0.91` over the final epochs and ended above the Phase 47 reference.

This trajectory supports a conservative interpretation of continued improvement or a late plateau within the tested 40-epoch window. It does not show an early best epoch followed by sustained degradation. The shrinking late-epoch gains also mean the evidence is insufficient to infer how much, if any, benefit would occur beyond epoch 40.

## 8. Best-Epoch and Final-Epoch Interpretation

Phase 52 has:

```text
best_epoch = 40
final_epoch = 40
```

Therefore, there is no best-versus-final checkpoint gap to interpret in this run. The final authorized epoch is also the best observed epoch by test RMSE.

This result indicates that the selected metric had not produced an earlier, clearly superior checkpoint followed by persistent deterioration within the configured horizon. It does not prove that epoch 40 is the global optimum, that the model has fully converged, or that extending training would remain beneficial.

Training beyond 40 epochs was outside the Phase 51 authorization and is not authorized by this findings document.

## 9. Reliability and Warning Implications

The improved test RMSE, MAE, wet/dry IoU, rollout stability, and step RMSE standard deviation are favorable inputs to later reliability and warning review. In particular, the higher wet/dry IoU and lower temporal-step error variation suggest that the longer-run checkpoint warrants direct reassessment under the existing diagnostic framework.

Aggregate metrics alone do not establish reliability across depth bands, event cases, warning categories, or physical-proxy conditions. They also do not demonstrate that prior warning-framework failure modes have been removed.

Any warning labels derived from subsequent analysis must remain diagnostic and rule-based unless separate calibration evidence is produced. Phase 52 does not establish calibrated probability warning labels.

## 10. What Phase 52 Demonstrates

Phase 52 demonstrates that:

- The Phase 51 authorized 128x128 seed42 longer-run experiment completed all 40 configured epochs.
- The controlled 40-epoch result substantially outperforms the Phase 47 10-epoch reference on all six retained test metrics.
- The best observed test RMSE occurs at epoch 40.
- The late trajectory is consistent with continued improvement or a late plateau inside the authorized cap, not early sustained degradation.
- Longer training was consequential for this specific controlled seed42 baseline.
- The resulting checkpoint is a stronger candidate for separate reliability, physical-proxy, and warning-framework diagnostics than the Phase 47 10-epoch checkpoint.

## 11. What Phase 52 Does Not Demonstrate

Phase 52 does not demonstrate:

- That training beyond 40 epochs is beneficial or authorized.
- Seed robustness or expected behavior for seed123, seed202, or any other seed.
- 256x256 training feasibility or performance.
- Tile, multiscale, or full 500x500 training feasibility or performance.
- Hyperparameter, model, loss, or architecture robustness.
- SWE residual or PINN feasibility.
- Level 5 support.
- Strict conservation or full mass conservation.
- Hydrodynamic closure.
- Calibrated probability warning labels.
- Production readiness.
- Reliability across all events, depth bands, warning classes, or operating conditions.

The result remains bounded to one controlled seed42 run at 128x128 on the retained split and metric definitions.

## 12. Guardrails

- Do not train beyond 40 epochs under the Phase 51 or Phase 52 authorization.
- Do not authorize or run seed123 or seed202 from this findings document.
- Do not claim seed robustness from one seed42 result.
- Do not authorize or run 256x256 from this findings document.
- Do not claim tile, multiscale, or full 500x500 feasibility.
- Do not run or infer sweep results.
- Do not infer model, loss, or architecture superiority beyond the controlled horizon comparison.
- Do not claim SWE or PINN behavior.
- Do not claim Level 5.
- Do not claim strict conservation, full mass conservation, or hydrodynamic closure.
- Do not describe warning labels as calibrated probabilities.
- Do not claim production readiness.
- Do not treat aggregate metric improvement as sufficient evidence for broader experimental expansion.
- Keep checkpoints local and do not commit them.

## 13. Recommended Next Step

A separate follow-up diagnostic phase should evaluate the Phase 52 outputs using the established reliability, physical-proxy, and warning-framework diagnostics. That phase should examine whether the aggregate improvements persist across relevant cases, depth bands, temporal behavior, proxy checks, and warning categories.

Seed replication and 256x256 expansion should remain deferred until the Phase 52 checkpoint has completed that diagnostic review and a later decision explicitly evaluates the evidence. This findings document does not authorize seed123, seed202, or 256x256 training.

## 14. Final Conclusion

Phase 52 directly answers the bounded question authorized by Phase 51. Extending the controlled Phase 47 128x128 seed42 route from 10 to 40 epochs produced substantial improvements in test RMSE, MAE, wet/dry IoU, rollout stability, step RMSE standard deviation, and test loss.

The best observed result occurs at epoch 40, which is also the final epoch. The evidence is consistent with continued improvement or a late plateau within the 40-epoch cap and does not indicate early sustained degradation. It does not authorize training beyond that cap.

The result strengthens the controlled seed42 baseline but does not establish seed robustness, higher-resolution feasibility, broader physical validity, calibrated warnings, Level 5 support, or production readiness. The appropriate next action is a separate reliability, physical-proxy, and warning-framework diagnostic phase before any seed replication or 256x256 expansion decision.
