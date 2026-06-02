# Phase 46 Dataloader Smoke Summary

No training, seed runs, sweeps, loss/config/model edits, SWE residuals, or PINN components were executed.

## Decision

- scenario_index_loaded: `true`
- static_index_loaded: `true`
- representative_samples_count: `11`
- sample_shape_checks_passed: `true`
- downsample_128_passed: `true`
- downsample_256_passed: `true`
- tile_checks_passed: `true`
- batch_smoke_passed: `true`
- memory_safe: `true`
- selected_decision: `dataloader_smoke_ready_for_downsample_baseline`
- level4_plus_supported: `true`
- level5_supported: `false`
- training_authorized: `false`
- next_recommended_action: `Review Phase 46 evidence, then prepare a separate Phase 47 downsample baseline plan before any training authorization.`

## Representative Samples

- `01_train_location1_G1135_intensity_117`: `cover_split_train`, `train/location1/G1135_intensity_117`, type `measured`, flood `(360, 1, 500, 500)`, rainfall length `360`
- `02_test_location1_G1135_intensity_103`: `cover_split_test`, `test/location1/G1135_intensity_103`, type `measured`, flood `(360, 1, 500, 500)`, rainfall length `360`
- `03_train_location1_G1135_intensity_155`: `cover_location_location1`, `train/location1/G1135_intensity_155`, type `measured`, flood `(360, 1, 500, 500)`, rainfall length `360`
- `04_train_location2_G1135_intensity_117`: `cover_location_location2`, `train/location2/G1135_intensity_117`, type `measured`, flood `(360, 1, 500, 500)`, rainfall length `360`
- `05_train_location3_G1135_intensity_117`: `cover_location_location3`, `train/location3/G1135_intensity_117`, type `measured`, flood `(360, 1, 500, 500)`, rainfall length `360`
- `06_train_location1_r100y_p0.1_d3h`: `cover_scenario_type_design`, `train/location1/r100y_p0.1_d3h`, type `design`, flood `(360, 1, 500, 500)`, rainfall length `180`
- `07_train_location1_G1135_intensity_156`: `cover_scenario_type_measured`, `train/location1/G1135_intensity_156`, type `measured`, flood `(360, 1, 500, 500)`, rainfall length `360`
- `08_train_location1_G1135_intensity_163`: `cover_flood_shape_360_1_500_500`, `train/location1/G1135_intensity_163`, type `measured`, flood `(360, 1, 500, 500)`, rainfall length `360`
- `09_train_location2_r300y_p0.2_d3h`: `cover_flood_shape_480_1_500_500`, `train/location2/r300y_p0.2_d3h`, type `design`, flood `(480, 1, 500, 500)`, rainfall length `180`
- `10_train_location1_r100y_p0.2_d3h`: `cover_rainfall_length_180`, `train/location1/r100y_p0.2_d3h`, type `design`, flood `(360, 1, 500, 500)`, rainfall length `180`
- `11_train_location1_G1135_intensity_179`: `cover_rainfall_length_360`, `train/location1/G1135_intensity_179`, type `measured`, flood `(360, 1, 500, 500)`, rainfall length `360`

## Scenario Count By Split

- `test`: `48`
- `train`: `120`

## Scenario Count By Location

- `test/location1`: `16`
- `test/location2`: `16`
- `test/location3`: `16`
- `train/location1`: `40`
- `train/location2`: `40`
- `train/location3`: `40`

## Scenario Type Counts

- `design`: `108`
- `measured`: `60`

## Flood Shape Counts

- `(360, 1, 500, 500)`: `153`
- `(480, 1, 500, 500)`: `15`

## Rainfall Length Counts

- `180`: `108`
- `360`: `60`

## Static Coverage Status Counts

- `complete_500x500`: `6`
