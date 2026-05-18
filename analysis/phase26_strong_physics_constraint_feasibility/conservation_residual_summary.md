# Phase 26 Conservation Residual Proxy Diagnostics

This diagnostic compares Phase 10 recommended baseline runs with Phase 25 target_wet_recall runs using existing `evaluation_test/test_batch_*/forecast_maps.npz` outputs only. It does not train models, alter losses, alter configs, or modify checkpoints.

## Direct Answers

1. Phase 25 more conservation-consistent at aggregate volume-proxy level: **Yes**. Mean seed delta in aggregate absolute relative volume bias: `-0.0733366`; lower is better.
2. Phase 25 reduces false-dry volume loss: **Yes**. Mean paired delta: `-24.0019`; lower is better.
3. Phase 25 reduces wet-area contraction: **Yes**. Mean paired delta: `-0.0804594`; lower is better.
4. Phase 25 improves peak-depth preservation: **Yes**. Mean paired delta in peak-depth underprediction: `-0.0290468`; lower is better.
5. Phase 25 introduces false-wet trade-offs: **Yes**. Mean paired false-wet-rate delta: `0.00382874`; mean paired false-wet-volume-excess delta: `3.99682`.
6. This is conservation-proxy diagnostics, not full SWE/PINN residual analysis, because the forecast maps only provide predicted and target water-depth rasters. They do not provide aligned velocity or flux fields, boundary inflow/outflow conditions, source/sink and drainage terms, pump/gate operations, or explicit `dt`, `dx`, and `dy` needed to compute shallow-water-equation residuals.

## Overall Conclusion

Phase 25 is directionally stronger on the main conservation-proxy diagnostics, especially aggregate volume response, false-dry volume loss, wet-area contraction, peak-depth preservation, RMSE, and MAE.

Phase 25 increases false-wet rate and false-wet volume excess slightly, so those remain trade-offs.

## Aggregate vs Timestep-Wise Volume Bias

- `aggregate_abs_relative_volume_bias` is computed from aggregate predicted volume and aggregate target volume over the full paired evaluation seed or set.
- `mean_step_absolute_relative_volume_bias` is the mean of timestep-level absolute relative volume bias and can move differently from the aggregate metric.
- Phase 25 strongly improves aggregate absolute relative volume bias across all three seeds.
- Timestep-wise absolute relative volume bias is mixed: seed42 improves, while seed123 and seed202 show very small increases.
- Therefore the conclusion is conservative: Phase 25 improves aggregate water-volume response and reduces under-response, but it is not a strict timestep-wise conservation solution.

## Phase-Level Aggregates

| Phase | Steps | Aggregate relative volume bias | Abs aggregate relative volume bias | Aggregate false dry rate | Aggregate false wet rate | Mean RMSE | Mean MAE |
|---|---:|---:|---:|---:|---:|---:|---:|
| `phase10` | 1368 | -0.0873309 | 0.0873309 | 0.165349 | 0.0128125 | 0.0517034 | 0.0208176 |
| `phase25` | 1368 | -0.0120155 | 0.0120155 | 0.0788559 | 0.0166286 | 0.0447715 | 0.0192989 |

## Paired Phase25 - Phase10 Deltas By Seed

| Seed | Paired steps | Delta aggregate abs rel volume bias | Delta mean-step abs rel volume bias | Delta false dry rate | Delta false dry volume loss | Delta wet-area contraction | Delta peak underprediction | Delta RMSE | Delta MAE | Delta false wet rate | Delta false wet volume excess |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `seed123` | 456 | -0.064695 | 0.000825707 | -0.105649 | -26.4163 | -0.0848763 | -0.00745827 | -0.00475925 | -0.000988539 | 0.00498559 | 5.05919 |
| `seed42` | 456 | -0.114739 | -0.0259662 | -0.149609 | -32.2189 | -0.104508 | -0.0757306 | -0.013858 | -0.00347597 | 0.00234719 | 2.54292 |
| `seed202` | 456 | -0.0405758 | 0.00247302 | -0.0651041 | -13.3703 | -0.0519941 | -0.00395138 | -0.00217833 | -9.16891e-05 | 0.00415345 | 4.38834 |

## Improvement Directions

- Lower absolute relative volume bias is better.
- Lower false-dry rate and lower false-dry volume loss are better.
- Lower wet-area contraction is better.
- Lower peak-depth underprediction is better.
- Lower RMSE and MAE are better.
- False-wet rate and false-wet volume excess are monitored as trade-offs.

## Missing Or Error Files

- None.
