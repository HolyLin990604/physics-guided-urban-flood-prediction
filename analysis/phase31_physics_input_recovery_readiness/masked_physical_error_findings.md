# Phase 31 Masked Physical Error Diagnostics

This diagnostic applies recovered domain, boundary, impervious, and manhole masks to existing prediction/target flood-depth rasters. All values are depth-raster proxy diagnostics, not strict mass conservation, full SWE/PINN residuals, or hydrodynamic closure.

## Direct Answers

1. Could sample-to-location mapping be recovered? **Yes**. Source: `adjacent evaluation_test/test_batch_*/summary.json metadata.location`. `forecast_maps.npz` stores only arrays; adjacent `summary.json` metadata supplies `location`.
2. Are masked diagnostics fully supported or partially blocked? **fully_supported**.
3. Largest Phase 29 RMSE region: `manhole_nonzero_valid` with RMSE `0.0558996`. Largest MAE region: `high_impervious_valid` with MAE `0.0217034`.
4. Highest Phase 29 false-dry region: `manhole_nonzero_valid` at `0.131298`. Highest false-wet region: `high_impervious_valid` at `0.0239894`.
5. Do boundary-ring cells behave worse than interior cells in Phase 29? RMSE `False`, MAE `False`, false-dry `True`, false-wet `False`.
6. Do high-impervious or manhole-nonzero regions show distinct errors? High-impervious Phase 29 RMSE `0.0548261`, false-dry `0.0740523`; manhole-nonzero Phase 29 RMSE `0.0558996`, false-dry `0.131298`.
7. Does Phase 29 improve or worsen masked physical errors relative to Phase 27? On valid-domain lower-is-better metrics, improved `1` and worsened `8`.
8. Does this support Level 4+ masked physical diagnostics? **supported**.
9. Does this change Level 5 status? **No. Level 5 remains `unsupported`**.

## Valid-Domain Phase Summary

| Phase | RMSE | MAE | Bias | False dry | False wet | Rel. volume bias proxy | Peak underprediction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `phase25` | 0.0485219 | 0.0191195 | -0.00388663 | 0.0759878 | 0.0185594 | -0.00347947 | 0.139421 |
| `phase27` | 0.0460827 | 0.0183693 | -0.00223264 | 0.0689175 | 0.0181923 | 0.0169359 | 0.128045 |
| `phase29` | 0.0480984 | 0.0190492 | -0.00294176 | 0.0739891 | 0.0194308 | 0.0115344 | 0.134593 |

## Phase29 - Phase27 Valid-Domain Deltas

| Metric | Phase 27 | Phase 29 | Delta | Improved |
| --- | ---: | ---: | ---: | --- |
| `rmse` | 0.0460827 | 0.0480984 | 0.00201574 | `False` |
| `mae` | 0.0183693 | 0.0190492 | 0.000679958 | `False` |
| `absolute_error_mean` | 0.0183693 | 0.0190492 | 0.000679958 | `False` |
| `false_dry_rate` | 0.0689175 | 0.0739891 | 0.00507161 | `False` |
| `false_wet_rate` | 0.0181923 | 0.0194308 | 0.00123854 | `False` |
| `false_dry_volume_loss_proxy` | 3575.36 | 4027.38 | 452.017 | `False` |
| `false_wet_volume_excess_proxy` | 5263.67 | 5690.27 | 426.605 | `False` |
| `relative_volume_bias_proxy` | 0.0169359 | 0.0115344 | -0.00540148 | `None` |

## Interpretation Guardrail

`invalid_or_high` is included only as a diagnostic contrast and is not treated as a physical target domain. The supported claim is Level 4+ masked physical error diagnostics from static masks and depth rasters. Level 5 remains unsupported because the needed hydrodynamic state and flux variables are absent.

## Output Files

- `masked_physical_error_by_region.csv`
- `masked_physical_error_by_phase.csv`
- `masked_physical_error_delta_phase29_vs_phase27.csv`
- `masked_physical_error_summary.json`
- `masked_physical_error_findings.md`

## Optional Figures

- `analysis/phase31_physics_input_recovery_readiness/figures/masked_error_region_rmse.png`
- `analysis/phase31_physics_input_recovery_readiness/figures/masked_error_false_dry_rate.png`
- `analysis/phase31_physics_input_recovery_readiness/figures/masked_error_volume_bias.png`
