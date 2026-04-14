# Phase 2 40-Epoch Multi-Seed Summary

## Scope

This note summarizes the 40-epoch multi-seed comparison between:

- Phase 2A (loss-only baseline)
- Phase 2B h16 (rainfall-conditioned temporal gate)

using three seeds: 42, 123, and 202.

## Summary Table

| Seed | Model | Val RMSE | Val MAE | Val wet/dry IoU | Val rollout stability |
| ---- | ----- | -------: | ------: | --------------: | --------------------: |
| 42 | Phase 2A | 0.04330 | 0.01533 | 0.74209 | 0.99077 |
| 42 | Phase 2B h16 | 0.04319 | 0.01473 | 0.76080 | 0.99073 |
| 123 | Phase 2A | 0.04190 | 0.01678 | 0.78940 | 0.99263 |
| 123 | Phase 2B h16 | 0.04212 | 0.01792 | 0.78645 | 0.99349 |
| 202 | Phase 2A | 0.03632 | 0.01516 | 0.81906 | 0.99222 |
| 202 | Phase 2B h16 | 0.03869 | 0.01663 | 0.77899 | 0.99198 |

## Main Observation

The 40-epoch multi-seed comparison shows that Phase 2B h16 is competitive, but it does not consistently outperform Phase 2A across seeds.

- Seed 42 favors Phase 2B h16 on RMSE, MAE, and wet/dry IoU.
- Seeds 123 and 202 favor Phase 2A on the main error metrics.
- Phase 2B h16 remains a strong alternative, but Phase 2A is currently the more stable primary candidate under the present multi-seed evidence.

## Current Working Conclusion

At the current stage:

- Primary candidate: Phase 2A (40 epochs)
- Strong alternative: Phase 2B h16 (40 epochs)

## Next Stage

Recommended next steps are:

1. test-set evaluation
2. qualitative visualization comparison
3. decision on whether README should be updated with a condensed version of this summary
