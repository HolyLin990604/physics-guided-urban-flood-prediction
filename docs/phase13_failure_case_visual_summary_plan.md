# Phase 13 Failure-Case Visual Summary Plan

## Objective

Phase 13 builds on the Phase 12 reliability/applicability diagnosis by turning the highest-ranked failure cases into representative visual summaries.

The purpose is not to retrain the model, tune Phase 10 parameters, change the architecture, or open a new sweep. The purpose is to visually explain why the current Phase 10 recommended model fails in the most difficult cases identified by Phase 12.

Phase 12 identified that the current model is useful for rapid spatiotemporal flood-process approximation but has clear reliability limits. The main caution zones are exact wet/dry boundary cells, shallow threshold-adjacent cells, moderate-to-deep depths, high-intensity `location2` scenarios, and local peak-depth extremes.

Phase 13 should provide figure-based evidence for these reliability limits.

## Starting Point

The current recommended Phase 10 model setting remains:

- `boundary_band_pixels = 1`

- `boundary_weight = 2.0`

This setting has already passed test-facing confirmation on:

- `seed123`

- `seed42`

- `seed202`

Phase 12 has already generated reliability diagnostics under:

- `analysis/phase12_reliability/summary.json`

- `analysis/phase12_reliability/timestep_metrics.csv`

- `analysis/phase12_reliability/depth_bin_metrics.csv`

- `analysis/phase12_reliability/boundary_distance_metrics.csv`

- `analysis/phase12_reliability/scenario_metrics.csv`

- `analysis/phase12_reliability/failure_cases.csv`

- `analysis/phase12_reliability/figures/`

Phase 13 should use these existing outputs as the starting point.

## Scope

In scope:

- select representative high-ranked failure cases from `analysis/phase12_reliability/failure_cases.csv`

- load saved test-facing forecast maps from Phase 10 evaluation outputs

- visualize target flood depth, predicted flood depth, absolute error, and wet/dry mismatch

- summarize common failure patterns across representative cases

- write a concise findings document based on actual generated figures

Out of scope:

- retraining

- changing the U-Net + TCN architecture

- changing rainfall-conditioned temporal gate design

- changing Phase 10 loss implementation

- tuning `boundary_weight`

- tuning `boundary_band_pixels`

- opening a new model or parameter sweep

- inventing conclusions before visual outputs are reviewed

## Primary Input Files

Failure-case ranking:

- `analysis/phase12_reliability/failure_cases.csv`

Saved Phase 10 test-facing forecast maps:

- `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_*/forecast_maps.npz`

- `runs/phase10_margin_aware_boundary_band_seed42_40e/evaluation_test/test_batch_*/forecast_maps.npz`

- `runs/phase10_margin_aware_boundary_band_seed202_40e/evaluation_test/test_batch_*/forecast_maps.npz`

Saved per-batch metadata:

- `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_*/summary.json`

- `runs/phase10_margin_aware_boundary_band_seed42_40e/evaluation_test/test_batch_*/summary.json`

- `runs/phase10_margin_aware_boundary_band_seed202_40e/evaluation_test/test_batch_*/summary.json`

## Representative Cases

The first Phase 13 pass should focus on the highest-ranked Phase 12 failure cases.

Initial candidate cases include:

- rank 1: `seed42`, `location2`, `r300y_p0.6_d3h`, `start_idx = 0`

- rank 2: `seed123`, `location2`, `r300y_p0.6_d3h`, `start_idx = 0`

- rank 3: `seed42`, `location2`, `r300y_p0.8_d3h`, `start_idx = 0`

- rank 4: `seed123`, `location2`, `r300y_p0.8_d3h`, `start_idx = 0`

- rank 5: `seed202`, `location2`, `r300y_p0.8_d3h`, `start_idx = 0`

The script may select the top `N` rows from `failure_cases.csv`, with a default such as `N = 6` or `N = 10`.

## Required Visual Outputs

For each selected failure case, generate a multi-panel figure containing:

1. Target flood depth

2. Predicted flood depth

3. Absolute error

4. Wet/dry mismatch map

Recommended wet/dry mismatch categories:

- true dry

- true wet

- false wet

- false dry

The visual summary should make it possible to inspect:

- whether the model underpredicts local peak depth

- whether wet/dry boundary errors dominate

- whether false dry regions are concentrated near target wet areas

- whether error is localized or spatially widespread

## Optional Visual Outputs

If straightforward, add:

- timestep-wise RMSE curve for the selected case

- timestep-wise MAE curve for the selected case

- selected timestep comparison, such as final forecast step or worst-error step

- a combined overview figure for the top failure cases

The first pass should not become overly complex. It is better to generate clear, reproducible figures than to over-design the visualization.

## Expected Output Directory

All Phase 13 outputs should be written under:

- `analysis/phase13_failure_cases/`

Expected structure:

- `analysis/phase13_failure_cases/selected_failure_cases.csv`

- `analysis/phase13_failure_cases/summary.json`

- `analysis/phase13_failure_cases/figures/`

Example figure names:

- `rank01_seed42_location2_r300y_p06_d3h_start0_maps.png`

- `rank02_seed123_location2_r300y_p06_d3h_start0_maps.png`

- `rank03_seed42_location2_r300y_p08_d3h_start0_maps.png`

## Suggested Script

Create:

- `scripts/visualize_phase13_failure_cases.py`

The script should:

- read `analysis/phase12_reliability/failure_cases.csv`

- select top-ranked failure cases

- locate the corresponding Phase 10 `evaluation_test/test_batch_*` folders

- load `forecast_maps.npz`

- extract prediction and target arrays

- generate multi-panel maps

- save selected-case metadata and summary outputs

- run from the repository root

Suggested CLI options:

- `--failure-cases-csv`

- `--output-dir`

- `--top-n`

- `--wet-threshold`

- `--timestep`

- `--dpi`

## Implementation Rules For Codex

Codex should follow these rules:

1. Do not modify model architecture.

2. Do not modify training code.

3. Do not modify Phase 10 loss implementation.

4. Do not retrain.

5. Do not recompute model predictions unless absolutely necessary.

6. Prefer saved Phase 10 `forecast_maps.npz` outputs.

7. Use Phase 12 `failure_cases.csv` as the case-selection source.

8. Do not invent conclusions before figures are reviewed.

9. Save all new outputs under `analysis/phase13_failure_cases/`.

10. Keep the first implementation simple and reproducible.

## Expected Deliverables

Minimum deliverables:

- `docs/phase13_failure_case_visual_summary_plan.md`

- `scripts/visualize_phase13_failure_cases.py`

- `analysis/phase13_failure_cases/selected_failure_cases.csv`

- `analysis/phase13_failure_cases/summary.json`

- `analysis/phase13_failure_cases/figures/*.png`

Optional deliverables:

- `docs/phase13_failure_case_visual_summary_findings.md`

- additional overview figures

- README update after Phase 13 findings are stable

## Success Criteria

Phase 13 should be considered successful if it can visually answer:

- Which high-ranked failure cases are most representative?

- Does the model fail mainly by underpredicting local peak depths?

- Are false dry or false wet errors concentrated near wet/dry boundaries?

- Are location2 high-intensity cases visually consistent with the Phase 12 statistical diagnosis?

- What visual evidence should be reported as the next reliability/applicability boundary?

## Next Step

After this plan is committed, Codex can be used to implement `scripts/visualize_phase13_failure_cases.py`.

The first coding pass should generate representative failure-case figures only. It should not modify the model, retrain, or reopen Phase 10 tuning.
