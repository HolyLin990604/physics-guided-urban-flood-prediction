# Phase 29 Seed42 Tolerance-Band Volume Consistency Diagnostic

This diagnostic compares Phase 29 against Phase 25 and Phase 27 using existing test `forecast_maps.npz` and `metrics.json` artifacts only. Volume quantities are depth-raster volume proxies, not strict conservation, full mass conservation, SWE residuals, or PINN evidence.

## Direct Answers

1. Did Phase 29 improve aggregate volume response relative to Phase 27? **Yes**. Delta aggregate absolute relative volume bias: `-0.00519769`; lower is better.
2. Did Phase 29 reduce dry_or_threshold volume accumulation relative to Phase 27? **Yes**. Phase 27 contribution: `0.137662`; Phase 29 contribution: `0.131428`.
3. Did Phase 29 remain close to Phase 25's near-zero aggregate volume bias? **No**. Phase 25 aggregate bias: `0.00296825`; Phase 29 aggregate bias: `0.019464`.
4. Did Phase 29 worsen false-dry volume loss relative to Phase 25 or Phase 27? **Yes**. Delta vs Phase 25: `-254.498`; delta vs Phase 27: `555.113`.
5. Did Phase 29 increase false-wet rate or false-wet volume excess? **Yes**. False-wet-rate delta vs Phase 27: `0.00113924`; false-wet-volume delta vs Phase 27: `539.44`.
6. Did Phase 29 preserve standard metrics well enough? **No**. Standard metric losses vs Phase 27: `metrics_json_rmse, metrics_json_mae, metrics_json_wet_dry_iou, metrics_json_rollout_stability, metrics_json_step_rmse_std`.
7. Overall result: **mixed_result**. Recommendation: **remain_seed42_only_pending_revision**.

## Conservative Interpretation

Phase 29 improves the primary volume-response objective on seed42 under these proxy diagnostics, subject to the listed false-dry, false-wet, and standard-metric trade-offs.

## Standard Metrics

| Metric | Phase 25 | Phase 27 | Phase 29 | Phase29 - Phase25 | Phase29 - Phase27 |
|---|---:|---:|---:|---:|---:|
| `rmse` | 0.044747 | 0.042381 | 0.0443855 | -0.000361551 | 0.00200447 |
| `mae` | 0.0179394 | 0.0172848 | 0.0178462 | -9.32019e-05 | 0.000561471 |
| `wet_dry_iou` | 0.803878 | 0.812801 | 0.801641 | -0.00223677 | -0.0111604 |
| `rollout_stability` | 0.989504 | 0.990122 | 0.989511 | 6.86081e-06 | -0.000611236 |
| `step_rmse_std` | 0.0106537 | 0.0100226 | 0.0106412 | -1.24994e-05 | 0.000618638 |

## Run-Level Volume Proxies

| Phase | Aggregate rel. volume bias | Aggregate abs. rel. volume bias | Mean-step abs. rel. volume bias | False-dry loss | False-wet excess | False-dry rate | False-wet rate | Wet-area contraction | RMSE from maps | MAE from maps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase25` | 0.00296825 | 0.00296825 | 0.240179 | 6219.33 | 7934.4 | 0.0759878 | 0.0161966 | 0 | 0.0457574 | 0.0179394 |
| `phase27` | 0.0246616 | 0.0246616 | 0.257274 | 5409.72 | 7750.32 | 0.0689175 | 0.01585 | 0 | 0.0434774 | 0.0172848 |
| `phase29` | 0.019464 | 0.019464 | 0.230447 | 5964.83 | 8289.77 | 0.0739891 | 0.0169892 | 0 | 0.0453533 | 0.0178462 |

## Target-Depth-Bin Predicted Volume Contribution

| Phase | dry_or_threshold | shallow | moderate | deep |
|---|---:|---:|---:|---:|
| `phase25` | 0.124008 | 0.0966017 | 0.115221 | 0.664169 |
| `phase27` | 0.137662 | 0.0955096 | 0.114492 | 0.652337 |
| `phase29` | 0.131428 | 0.0953673 | 0.114498 | 0.658707 |

## Output Files

- `phase29_seed42_by_step.csv`
- `phase29_seed42_by_run.csv`
- `phase29_seed42_delta_vs_phase25.csv`
- `phase29_seed42_delta_vs_phase27.csv`
- `phase29_seed42_depth_bin_decomposition.csv`
- `phase29_seed42_summary.json`
- `phase29_seed42_summary.md`
