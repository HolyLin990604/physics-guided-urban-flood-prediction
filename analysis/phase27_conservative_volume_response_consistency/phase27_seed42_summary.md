# Phase 27 Seed42 Conservative Volume-Response Diagnostic

This diagnostic compares Phase 27 against the Phase 25 seed42 baseline using existing `evaluation_test/test_batch_*/forecast_maps.npz` and `metrics.json` outputs only. It does not train, alter architecture, alter losses, alter configs, or claim full mass conservation.

## Direct Answers

1. Does Phase 27 improve standard metrics over Phase 25 seed42? **Yes**. All listed standard metrics move in the preferred direction.
2. Does Phase 27 improve aggregate volume response? **No**. Delta aggregate absolute relative volume bias: `0.0216934`; lower is better.
3. Does Phase 27 improve or worsen timestep-wise absolute relative volume bias? **Worsen**. Delta mean-step absolute relative volume bias: `0.0170953`; lower is better.
4. Does Phase 27 reduce false-dry volume loss? **Yes**. Mean paired delta: `-1.77546`; lower is better.
5. Does Phase 27 reduce wet-area contraction? **Yes**. Mean paired delta: `-0.00626303`; lower is better.
6. Does Phase 27 improve peak-depth preservation? **Yes**. Mean paired delta in peak-depth underprediction: `-0.011376`; lower is better.
7. Does Phase 27 increase false-wet rate or false-wet volume excess? **No**. False-wet-rate delta: `-0.000387357`; false-wet-volume-excess delta: `-0.403664`.
8. Is the result a genuine conservative volume-response improvement or a false-wet-driven over-expansion? **Mixed seed42 result; not a confirmed conservative volume-response improvement**.
9. Should Phase 27 proceed? **remain_seed42_positive_only**.

## Conservative Conclusion

Phase 27 is mixed on seed42: standard metrics and several under-response proxies improve, but aggregate and timestep-wise absolute relative volume bias do not. It should remain seed42-positive only rather than being treated as confirmed volume-response progress.

This is a volume-response proxy diagnostic from depth rasters. It is not a full mass-conservation, SWE, or PINN residual analysis, and it does not establish strict timestep-wise conservation.

## Standard Metrics

| Metric | Phase 25 | Phase 27 | Delta Phase27 - Phase25 | Improved |
|---|---:|---:|---:|---|
| `rmse` | 0.0447470026189 | 0.0423809813434 | -0.00236602127552 | Yes |
| `mae` | 0.0179394448274 | 0.0172847716236 | -0.000654673203826 | Yes |
| `wet_dry_iou` | 0.803877720707 | 0.812801373632 | 0.00892365292499 | Yes |
| `rollout_stability` | 0.989504199279 | 0.990122296308 | 0.000618097029234 | Yes |
| `step_rmse_std` | 0.0106537425645 | 0.010022604691 | -0.000631137873585 | Yes |

## Run-Level Volume Metrics

| Phase | Steps | Aggregate relative volume bias | Aggregate absolute relative volume bias | Mean-step relative volume bias | Mean-step absolute relative volume bias | Aggregate wet-area contraction | Aggregate false dry rate | Aggregate false wet rate | Mean false-dry volume loss | Mean false-wet volume excess | Mean peak underprediction |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phase25` | 456 | 0.00296825 | 0.00296825 | 0.0379278 | 0.240179 | 0 | 0.0759878 | 0.0161966 | 13.6389 | 17.4 | 0.139421 |
| `phase27` | 456 | 0.0246616 | 0.0246616 | 0.0981603 | 0.257274 | 0 | 0.0689175 | 0.01585 | 11.8634 | 16.9963 | 0.128045 |

## Paired Phase27 - Phase25 Delta Summary

| Metric | Mean paired delta | Direction |
|---|---:|---|
| `absolute_relative_volume_bias` | 0.0170953 | lower is better |
| `false_dry_volume_loss` | -1.77546 | lower is better |
| `wet_area_contraction` | -0.00626303 | lower is better |
| `peak_depth_underprediction` | -0.011376 | lower is better |
| `rmse` | -0.00231054 | lower is better |
| `mae` | -0.000654673 | lower is better |
| `false_wet_rate` | -0.000387357 | trade-off monitor |
| `false_wet_volume_excess` | -0.403664 | trade-off monitor |

## Outputs

- `phase27_seed42_by_step.csv`
- `phase27_seed42_by_run.csv`
- `phase27_seed42_delta.csv`
- `phase27_seed42_summary.json`
- `phase27_seed42_summary.md`
