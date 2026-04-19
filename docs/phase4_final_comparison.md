# Phase 4 Final Comparison

## Goal

Phase 4 consolidates final evidence for the two strongest contenders without changing model structure, training logic, or search scope.

Compared contenders:

- **M3 f025**
  - `temporal_gate_residual_partial`
  - `hidden_channels = 16`
  - `residual_alpha = 0.10`
  - `conditioned_fraction = 0.25`
- **Phase 3.3 af025**
  - `temporal_gate_residual_response_split_protected`
  - `hidden_channels = 16`
  - `residual_alpha = 0.10`
  - `conditioned_fraction = 0.25`
  - `active_fraction_within_response = 0.25`

All figures in this phase are generated directly from existing evaluated outputs under `evaluation_test/test_batch_0000/`.

## Quantitative Snapshot

| Variant | Seed202 RMSE | Seed202 MAE | Seed202 IoU | Seed42 RMSE | Seed42 MAE | Seed42 IoU |
|---|---:|---:|---:|---:|---:|---:|
| M3 f025 | 0.040568 | 0.016056 | 0.795732 | 0.035211 | 0.013695 | 0.830558 |
| Phase 3.3 af025 | 0.039514 | 0.015807 | 0.801322 | 0.038861 | 0.014598 | 0.800325 |

Interpretation:

- `seed202` remains the difficult case.
- `seed42` remains the favorable case.
- Phase 3.3 af025 is stronger on the difficult case.
- M3 f025 remains clearly stronger on the favorable case.
- The overall best-balanced mainline remains M3 f025.

## Qualitative Comparison

### Difficult Case (`seed202`)

#### Spatial Comparison

![M3 vs Phase 3.3 af025 seed202 spatial comparison](../assets/images/final/m3_vs_phase33_af025_seed202_maps.png)

#### Region-Averaged Process Comparison

![M3 vs Phase 3.3 af025 seed202 process comparison](../assets/images/final/m3_vs_phase33_af025_seed202_timeseries.png)

Reading:

- Phase 3.3 af025 tracks the difficult-case target slightly better overall.
- The improvement is consistent with the lower RMSE, lower MAE, and higher IoU on `seed202`.
- This supports the conclusion that the protected response-split refinement is meaningful, especially on harder cases.

### Favorable Case (`seed42`)

#### Spatial Comparison

![M3 vs Phase 3.3 af025 seed42 spatial comparison](../assets/images/final/m3_vs_phase33_af025_seed42_maps.png)

#### Region-Averaged Process Comparison

![M3 vs Phase 3.3 af025 seed42 process comparison](../assets/images/final/m3_vs_phase33_af025_seed42_timeseries.png)

Reading:

- M3 f025 remains cleaner and better aligned on the favorable case.
- This is consistent with the stronger `seed42` quantitative results for M3 f025.
- Phase 3.3 af025 remains competitive, but its structured refinement does not replace M3 as the best-balanced project-level choice.

## Final Conclusion

- **M3 f025** remains the current best-balanced architecture.
- **Phase 3.3 af025** is the strongest structured refinement discovered in Phase 3.
- The final evidence supports keeping M3 f025 as the mainline conclusion while preserving Phase 3.3 af025 as the clearest difficult-case refinement.
