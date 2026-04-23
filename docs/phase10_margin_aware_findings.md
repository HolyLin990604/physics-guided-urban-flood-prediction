# Phase 10 Margin-Aware Findings

## Objective

Phase 10 moved from diagnosis to a single targeted intervention: boundary-band weighted wet/dry consistency refinement. This document summarizes the outcome of that first intervention.

## Intervention Summary

The intervention keeps the existing wet/dry consistency objective, but gives higher BCE weight to cells inside a narrow target wet/dry boundary band. The tested boundary band was fixed at `boundary_band_pixels = 1`.

After the initial seed42 train-time validation concern at `boundary_weight = 2.0`, only the boundary-band weighting strength was varied. The later explicit seed42 test evaluation changed the decision. No model-family, dataset, metric, or loss-structure change is part of this result.

## Compact Comparison

The table uses explicit test metrics from `evaluation_test/metrics.json` for all four completed comparisons.

| seed | boundary_weight | source | rmse | mae | wet_dry_iou | rollout_stability | reading |
|---:|---:|---|---:|---:|---:|---:|---|
| 123 | 2.0 | test | 0.061625 | 0.022525 | 0.706808 | 0.982880 | Strongest tested seed123 setting. |
| 42 | 2.0 | test | 0.058588 | 0.021415 | 0.682114 | 0.987815 | Stronger than `w=1.5` on the completed seed42 test comparison. |
| 42 | 1.5 | test | 0.059121 | 0.021440 | 0.663052 | 0.988781 | Conservative rollback; stable, but weaker than `w=2.0` on seed42 test metrics. |
| 123 | 1.5 | test | 0.062689 | 0.022631 | 0.683618 | 0.982618 | Conservative rollback; still positive, but weaker than `w=2.0` on seed123 test metrics. |

## Main Findings

`boundary_weight = 2.0` originally looked risky because the first seed42 concern came from train-time validation reading, where the favorable-case guardrail appeared to miss.

The completed test-facing evidence changes the decision. With explicit seed42 `w=2.0` test metrics now present, `w=2.0` is stronger than `w=1.5` on both tested seeds: seed123 and seed42.

`boundary_weight = 1.5` is no longer the default conclusion. It remains a conservative rollback setting because it preserves useful behavior at lower boundary emphasis, but it is not the best current tested setting.

Within the completed seed123 and seed42 test-facing comparisons, `boundary_weight = 2.0` is the current leading tested setting. This does not establish broader robustness beyond those tested seeds.

## Current Decision

Current leading tested setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`.

`boundary_weight = 1.5` is a conservative rollback setting, not the current default conclusion.

## Ruled Out / Open

Ruled out: the earlier conclusion that `boundary_weight = 1.5` should be the default based on incomplete seed42 test-facing evidence.

Open: whether `boundary_weight = 2.0` remains the best balanced setting on the remaining difficult-case reference seed (`seed202`).

## Next Narrow Step

Run one seed202 confirmation run under `boundary_band_pixels = 1`, `boundary_weight = 2.0`, because no corresponding Phase 10 seed202 run exists in the repository.
