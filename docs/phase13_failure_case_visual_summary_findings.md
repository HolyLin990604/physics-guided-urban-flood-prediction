# Phase 13 Failure-Case Visual Summary Findings

## Purpose

Phase 13 builds on the Phase 12 reliability/applicability diagnosis by converting the highest-ranked failure cases into representative visual summaries.

The purpose is not to retrain the model, modify the architecture, change the Phase 10 loss, tune `boundary_weight`, tune `boundary_band_pixels`, or open a new sweep. The purpose is to visually explain the main failure modes of the current Phase 10 recommended model.

The diagnostic object remains the Phase 10 recommended setting:

- `boundary_band_pixels = 1`
- `boundary_weight = 2.0`

The visual summaries use saved test-facing Phase 10 forecast maps and the Phase 12 failure-case ranking.

## Inputs

Phase 13 uses the following Phase 12 output as the case-selection source:

- `analysis/phase12_reliability/failure_cases.csv`

It uses saved Phase 10 test-facing forecast maps from:

- `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_*/forecast_maps.npz`
- `runs/phase10_margin_aware_boundary_band_seed42_40e/evaluation_test/test_batch_*/forecast_maps.npz`
- `runs/phase10_margin_aware_boundary_band_seed202_40e/evaluation_test/test_batch_*/forecast_maps.npz`

No model prediction was recomputed by retraining. The analysis reuses saved evaluation outputs.

## Outputs

Phase 13 generated the following outputs:

- `scripts/visualize_phase13_failure_cases.py`
- `analysis/phase13_failure_cases/selected_failure_cases.csv`
- `analysis/phase13_failure_cases/summary.json`
- `analysis/phase13_failure_cases/figures/`

The formal Phase 13 visual outputs use the `worst` timestep mode rather than the `final` timestep mode.

This decision was made because the final forecast step did not always expose the dominant failure pattern. The worst-timestep view better captures the high-error, low-IoU, underprediction-dominated failure states identified by the Phase 12 ranking.

## Selected Representative Failure Cases

The first Phase 13 pass selected the top six failure cases from the Phase 12 failure-case ranking.

The selected cases are:

| Failure rank | Seed | Location | Event | Start index | Worst step |
|---:|---|---|---|---:|---:|
| 1 | `seed42` | `location2` | `r300y_p0.6_d3h` | 0 | 1 |
| 2 | `seed123` | `location2` | `r300y_p0.6_d3h` | 0 | 1 |
| 3 | `seed42` | `location2` | `r300y_p0.8_d3h` | 0 | 4 |
| 4 | `seed123` | `location2` | `r300y_p0.8_d3h` | 0 | 4 |
| 5 | `seed202` | `location2` | `r300y_p0.8_d3h` | 0 | 4 |
| 6 | `seed202` | `location2` | `r300y_p0.6_d3h` | 0 | 1 |

A key finding is that the top-ranked failures are not six unrelated physical cases. They collapse into two high-intensity `location2` target scenarios repeated across seeds:

- `location2 / r300y_p0.6_d3h / start_idx = 0`, with worst step 1
- `location2 / r300y_p0.8_d3h / start_idx = 0`, with worst step 4

This explains why the generated figures look visually similar. The target fields are identical within each scenario group, while the predictions differ by seed but show visually similar failure modes.

## Indexing Verification

A verification pass found no indexing bug.

The script was checked for the following mappings:

- `run_root + batch_index` maps to the correct `evaluation_test/test_batch_*` folder
- `sample_index` indexes axis 0 of prediction and target arrays
- `selected_forecast_step` is derived from the selected timestep index and indexes the forecast-time axis
- saved batch metadata are checked for split, location, event, start index, input steps, prediction steps, and alignment mode

The similarity among figures is therefore expected and reflects repeated physical failure patterns rather than accidental reuse of the same arrays.

## Visual Failure Pattern

The Phase 13 figures show a consistent failure mode.

Across the representative cases, the target flood-depth maps contain localized high-depth regions and broader wet areas, while the predicted flood-depth maps are spatially weaker and have much smaller high-depth regions.

The absolute-error panels show that the largest errors are concentrated near localized high-depth areas and wet-region expansion zones.

The wet/dry mismatch panels show extensive false-dry regions, indicating that the model often predicts cells as dry where the target is wet.

Overall, the visual pattern can be summarized as:

- systematic underprediction
- local peak-depth underprediction
- predicted wet-area contraction
- false-dry dominated wet/dry mismatch
- boundary-transition failure around wet/dry margins

## Quantitative Debug Summary

The debug summaries added to `analysis/phase13_failure_cases/summary.json` support the visual interpretation.

For the `r300y_p0.6_d3h` group:

- target maximum depth is approximately 2.78
- predicted maximum depth ranges from approximately 0.20 to 0.51
- target wet fraction is approximately 0.143
- predicted wet fraction ranges from approximately 0.022 to 0.049
- selected-step bias is negative for all three seeds

For the `r300y_p0.8_d3h` group:

- target maximum depth is approximately 2.73
- predicted maximum depth ranges from approximately 0.45 to 1.14
- target wet fraction is approximately 0.157
- predicted wet fraction ranges from approximately 0.039 to 0.061
- selected-step bias is negative for all three seeds

These summaries confirm that the representative failures are dominated by underprediction and reduced predicted wet extent.

## Relationship To Phase 12

Phase 12 identified the main reliability limits of the current model as:

- exact wet/dry boundary cells
- shallow threshold-adjacent cells
- moderate-to-deep depths
- high-intensity `location2` scenarios
- local peak-depth extremes

Phase 13 provides visual evidence for these Phase 12 findings.

The selected failure cases are all high-intensity `location2` cases. The maps show that the model misses parts of the target wet extent, underpredicts local peak depths, and produces false-dry dominated mismatch patterns.

This strengthens the Phase 12 interpretation: the current model is useful for rapid spatiotemporal flood-process approximation, but it should be used cautiously for high-intensity `location2` scenarios, local peak-depth interpretation, and wet/dry boundary-transition regions.

## Applicability Implication

The Phase 13 visual summaries indicate that the current Phase 10 recommended model does not fail randomly across the test set. Instead, its highest-ranked failures concentrate in a small number of physically similar, high-intensity `location2` scenarios.

This is important for applicability assessment.

The model remains useful for rapid flood-process approximation, but the following caution should be reported:

- the model may underpredict early or mid-forecast wet-area expansion in high-intensity `location2` cases
- local peak depths can be substantially underestimated
- predicted wet extent can be too conservative
- false-dry errors can dominate the wet/dry mismatch map
- reliability is lower where rapid wet/dry transitions and localized high-depth features occur together

## Decision

The Phase 13 first pass is successful as a representative failure-case visualization step.

The formal Phase 13 output should use the `worst` timestep visualizations, not the initial final-timestep version.

The similarity among the top-six figures should not be treated as a visualization weakness. It is a finding: the highest-ranked failures collapse into two high-intensity `location2` target scenarios repeated across seeds.

## Next Step

After this findings document is reviewed and committed, the next step is a light documentation sync:

- update `docs/project_status.md`
- update `docs/experiment_index.md`
- optionally update `README.md` with a concise Phase 13 note

No model retraining, Phase 10 boundary-weight sweep, or architecture change is justified by this Phase 13 first pass.

A future follow-up may consider uncertainty or confidence diagnostics for the same high-intensity `location2` scenarios and wet/dry boundary-transition regions.
