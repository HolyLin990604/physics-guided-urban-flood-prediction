# Phase 38 Seed42 Pilot Training Guardrail Evaluation

This evaluation is Level 4+ static-map-aware proxy scope only. It does not claim Level 5 support, SWE/PINN residuals, strict conservation, full mass conservation, or hydrodynamic closure.

## Decision

- final_decision: `seed42_pilot_rejected`
- standard_checks_passed: `2`
- standard_checks_failed: `3`
- acceptance_checks_passed: `6`
- acceptance_checks_failed: `8`
- acceptance_checks_not_evaluated: `0`
- rejection_rules_triggered: `3`
- rejection_rules_not_evaluated: `0`

## Standard AT08-AT12

| ID | Metric | Observed | Threshold | Direction | Status |
| --- | --- | ---: | ---: | --- | --- |
| `AT08` | `rmse` | 0.0445683014236 | 0.0432286009702 | `lower_or_equal` | `fail` |
| `AT09` | `mae` | 0.0179593140063 | 0.0176304670561 | `lower_or_equal` | `fail` |
| `AT10` | `wet_dry_iou` | 0.806874058749 | 0.807801373632 | `higher_or_equal` | `fail` |
| `AT11` | `rollout_stability` | 0.989964456935 | 0.989122296308 | `higher_or_equal` | `pass` |
| `AT12` | `step_rmse_std` | 0.0101883552821 | 0.0105237349255 | `lower_or_equal` | `pass` |

## Failed Acceptance Checks

- `AT02` `valid_domain_masked/rmse/valid_domain`: `fail` observed `0.0482901961137` threshold `0.0470043492351`. computed from 19 forecast map batches and static masks under E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite; location1: valid=13419, boundary_ring=1258, high_impervious_valid=8626, manhole_nonzero_valid=687; location2: valid=15625, boundary_ring=496, high_impervious_valid=7146, manhole_nonzero_valid=684; location3: valid=14102, boundary_ring=2419, high_impervious_valid=6129, manhole_nonzero_valid=2689
- `AT03` `valid_domain_masked/mae/valid_domain`: `fail` observed `0.0191286913686` threshold `0.0187366452965`. computed from 19 forecast map batches and static masks under E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite; location1: valid=13419, boundary_ring=1258, high_impervious_valid=8626, manhole_nonzero_valid=687; location2: valid=15625, boundary_ring=496, high_impervious_valid=7146, manhole_nonzero_valid=684; location3: valid=14102, boundary_ring=2419, high_impervious_valid=6129, manhole_nonzero_valid=2689
- `AT04` `valid_domain_masked/false_dry_rate/valid_domain`: `fail` observed `0.0718682210394` threshold `0.068917464101`. computed from 19 forecast map batches and static masks under E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite; location1: valid=13419, boundary_ring=1258, high_impervious_valid=8626, manhole_nonzero_valid=687; location2: valid=15625, boundary_ring=496, high_impervious_valid=7146, manhole_nonzero_valid=684; location3: valid=14102, boundary_ring=2419, high_impervious_valid=6129, manhole_nonzero_valid=2689
- `AT06` `guardrail_masked/false_wet_rate/high_impervious_valid`: `fail` observed `0.0231264618198` threshold `0.0227046722562`. computed from 19 forecast map batches and static masks under E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite; location1: valid=13419, boundary_ring=1258, high_impervious_valid=8626, manhole_nonzero_valid=687; location2: valid=15625, boundary_ring=496, high_impervious_valid=7146, manhole_nonzero_valid=684; location3: valid=14102, boundary_ring=2419, high_impervious_valid=6129, manhole_nonzero_valid=2689
- `AT07` `guardrail_masked/false_dry_rate/boundary_ring`: `fail` observed `0.0920545695699` threshold `0.087764984526`. computed from 19 forecast map batches and static masks under E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite; location1: valid=13419, boundary_ring=1258, high_impervious_valid=8626, manhole_nonzero_valid=687; location2: valid=15625, boundary_ring=496, high_impervious_valid=7146, manhole_nonzero_valid=684; location3: valid=14102, boundary_ring=2419, high_impervious_valid=6129, manhole_nonzero_valid=2689
- `AT08` `standard/rmse/all_evaluated_cells`: `fail` observed `0.0445683014236` threshold `0.0432286009702`. standard evaluation metrics
- `AT09` `standard/mae/all_evaluated_cells`: `fail` observed `0.0179593140063` threshold `0.0176304670561`. standard evaluation metrics
- `AT10` `standard/wet_dry_iou/all_evaluated_cells`: `fail` observed `0.806874058749` threshold `0.807801373632`. standard evaluation metrics

## Rejection Rules

- `RT01` `phase29_tradeoff_pattern` triggered. candidate={'absolute_relative_volume_bias_proxy': 0.009734633876527184, 'rmse': 0.04829019611370878, 'mae': 0.019128691368550627, 'false_dry_rate': 0.07186822103935803, 'false_wet_rate': 0.018617591273413805}; phase27={'absolute_relative_volume_bias_proxy': 0.0169359188921, 'rmse': 0.0460826953285, 'mae': 0.0183692600946, 'false_dry_rate': 0.068917464101, 'false_wet_rate': 0.0181922750833}
- `RT05` `standard_rmse_or_mae_worsens_beyond_tolerance` triggered. rmse=0.0445683014236 threshold=0.0445000304105; mae=0.0179593140063 threshold=0.0181490102048
- `RT07` `valid_domain_error_worsens_beyond_acceptance_tolerance` triggered. valid rmse=0.0482901961137; valid mae=0.0191286913686

## Inputs

- config: `configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`
- metrics: `runs/phase36_manhole_false_dry_guardrail_seed42_40e/evaluation_test/metrics.json`
- forecast_maps: `runs/phase36_manhole_false_dry_guardrail_seed42_40e/evaluation_test/test_batch_*/forecast_maps.npz`
- acceptance_thresholds: `analysis/phase34_pilot_thresholds/acceptance_thresholds.csv`
- rejection_thresholds: `analysis/phase34_pilot_thresholds/rejection_thresholds.csv`
- baseline_metric_table: `analysis/phase34_pilot_thresholds/baseline_metric_table.csv`
- phase31_masked_inputs: `analysis/phase31_physics_input_recovery_readiness`
- dataset_root_for_static_masks: `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite`
