# Phase 34 Pilot Threshold Summary

## 1. Executive summary

Phase 34 formalized diagnostic-only pre-pilot acceptance and rejection thresholds for a possible future seed42 pilot. The recommended future candidate is `manhole_nonzero_false_dry_guardrail`, targeting `manhole_nonzero_valid` `false_dry_rate`. Training remains unauthorized.

## 2. Baselines fixed

Fixed baseline metric rows: 23.

| metric_group | metric_name | region | phase25_seed42 | phase27_seed42 | phase29_seed42 | preferred_direction | reference_baseline | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| standard | rmse | all_evaluated_cells | 0.0447470026189 | 0.0423809813434 | 0.0443854521176 | lower_is_better | Phase 27 seed42 baseline with Phase 29 trade-off check | Standard evaluation_test metric from fixed seed42 baseline runs. |
| standard | mae | all_evaluated_cells | 0.0179394448274 | 0.0172847716236 | 0.0178462429168 | lower_is_better | Phase 27 seed42 baseline with Phase 29 trade-off check | Standard evaluation_test metric from fixed seed42 baseline runs. |
| standard | wet_dry_iou | all_evaluated_cells | 0.803877720707 | 0.812801373632 | 0.801640952888 | higher_is_better | Phase 27 seed42 baseline with Phase 29 trade-off check | Standard evaluation_test metric from fixed seed42 baseline runs. |
| standard | rollout_stability | all_evaluated_cells | 0.989504199279 | 0.990122296308 | 0.989511060087 | higher_is_better | Phase 27 seed42 baseline with Phase 29 trade-off check | Standard evaluation_test metric from fixed seed42 baseline runs. |
| standard | step_rmse_std | all_evaluated_cells | 0.0106537425645 | 0.010022604691 | 0.010641243125 | lower_is_better | Phase 27 seed42 baseline with Phase 29 trade-off check | Standard evaluation_test metric from fixed seed42 baseline runs. |
| valid_domain_masked | rmse | valid_domain | 0.0485218595133 | 0.0460826953285 | 0.048098430567 | lower_is_better | Phase 27 seed42 baseline with Phase 29 trade-off check | Phase 31 masked valid-domain diagnostic; Level 4+ proxy only. |
| valid_domain_masked | mae | valid_domain | 0.0191194754249 | 0.0183692600946 | 0.0190492177388 | lower_is_better | Phase 27 seed42 baseline with Phase 29 trade-off check | Phase 31 masked valid-domain diagnostic; Level 4+ proxy only. |
| valid_domain_masked | false_dry_rate | valid_domain | 0.0759877543587 | 0.068917464101 | 0.0739890775888 | lower_is_better | Phase 27 seed42 baseline with Phase 29 trade-off check | Phase 31 masked valid-domain diagnostic; Level 4+ proxy only. |
| valid_domain_masked | false_wet_rate | valid_domain | 0.0185593790698 | 0.0181922750833 | 0.0194308140094 | lower_is_better | Phase 27 seed42 baseline with Phase 29 trade-off check | Phase 31 masked valid-domain diagnostic; Level 4+ proxy only. |
| valid_domain_masked | false_dry_volume_loss_proxy | valid_domain | 4241.30893057 | 3575.36233313 | 4027.37928723 | lower_is_better | Phase 27 seed42 baseline with Phase 29 trade-off check | Phase 31 masked valid-domain diagnostic; Level 4+ proxy only. |
| valid_domain_masked | false_wet_volume_excess_proxy | valid_domain | 5436.24205765 | 5263.66506363 | 5690.2698406 | lower_is_better | Phase 27 seed42 baseline with Phase 29 trade-off check | Phase 31 masked valid-domain diagnostic; Level 4+ proxy only. |
| valid_domain_masked | relative_volume_bias_proxy | valid_domain | -0.00347947154694 | 0.0169359188921 | 0.0115344360041 | lower_is_better | Phase 27 and Phase 29 signed proxy values; absolute proxy is preferred for thresholding | Phase 31 masked valid-domain diagnostic; Level 4+ proxy only. |

Full table: `baseline_metric_table.csv`.

## 3. Acceptance thresholds

Acceptance threshold rows: 14.

| threshold_id | metric_group | metric_name | region | baseline_reference | acceptance_rule | numeric_threshold | threshold_type | required_for_pilot_acceptance | rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AT01 | manhole_nonzero_target | false_dry_rate | manhole_nonzero_valid | Phase 27=0.1172229713; Phase 29=0.131297982994 | candidate value must be below Phase 29 and no higher than Phase 27 | 0.1172229713 | improvement_required_and_no_worse_than_phase27 | yes | The selected candidate targets the manhole-nonzero false-dry failure mode. |
| AT02 | valid_domain_masked | rmse | valid_domain | Phase 27=0.0460826953285 | candidate value must be <= Phase 27 plus 2 percent tolerance | 0.0470043492351 | small_tolerance_no_worse_than_phase27 | yes | Depth-error regressions cannot be traded for a single proxy improvement. |
| AT03 | valid_domain_masked | mae | valid_domain | Phase 27=0.0183692600946 | candidate value must be <= Phase 27 plus 2 percent tolerance | 0.0187366452965 | small_tolerance_no_worse_than_phase27 | yes | Depth-error regressions cannot be traded for a single proxy improvement. |
| AT04 | valid_domain_masked | false_dry_rate | valid_domain | Phase 27=0.068917464101 | candidate value must be <= Phase 27 | 0.068917464101 | no_worse_than_phase27 | yes | Phase 29 worsened this metric; a future pilot must not repeat that pattern. |
| AT05 | valid_domain_masked | false_wet_rate | valid_domain | Phase 27=0.0181922750833 | candidate value must be <= Phase 27 plus 0.0005 absolute tolerance | 0.0186922750833 | absolute_tolerance_no_worse_than_phase27 | yes | Conservative pre-pilot tolerance for region-specific masked proxy guardrails. |
| AT06 | guardrail_masked | false_wet_rate | high_impervious_valid | Phase 27=0.0222046722562 | candidate value must be <= Phase 27 plus 0.0005 absolute tolerance | 0.0227046722562 | absolute_tolerance_no_worse_than_phase27 | yes | Conservative pre-pilot tolerance for region-specific masked proxy guardrails. |
| AT07 | guardrail_masked | false_dry_rate | boundary_ring | Phase 27=0.086764984526 | candidate value must be <= Phase 27 plus 0.001 absolute tolerance | 0.087764984526 | absolute_tolerance_no_worse_than_phase27 | yes | Conservative pre-pilot tolerance for region-specific masked proxy guardrails. |
| AT08 | standard | rmse | all_evaluated_cells | Phase 27=0.0423809813434 | candidate value must be <= Phase 27 plus 2 percent tolerance | 0.0432286009702 | small_tolerance_no_worse_than_phase27 | yes | Standard test metrics remain required global quality guardrails. |
| AT09 | standard | mae | all_evaluated_cells | Phase 27=0.0172847716236 | candidate value must be <= Phase 27 plus 2 percent tolerance | 0.0176304670561 | small_tolerance_no_worse_than_phase27 | yes | Standard test metrics remain required global quality guardrails. |
| AT10 | standard | wet_dry_iou | all_evaluated_cells | Phase 27=0.812801373632 | candidate value must be >= Phase 27 minus 0.005 absolute tolerance | 0.807801373632 | minimum_no_material_decline | yes | Wet/dry classification quality cannot be sacrificed for proxy gains. |
| AT11 | standard | rollout_stability | all_evaluated_cells | Phase 27=0.990122296308 | candidate value must be >= Phase 27 minus 0.001 absolute tolerance | 0.989122296308 | minimum_no_material_decline | yes | Temporal rollout behavior must not degrade under a future pilot. |
| AT12 | standard | step_rmse_std | all_evaluated_cells | Phase 27=0.010022604691 | candidate value must be <= Phase 27 plus 5 percent tolerance | 0.0105237349255 | small_tolerance_no_worse_than_phase27 | yes | Step-wise error variability must remain bounded. |
| AT13 | valid_domain_masked | absolute_relative_volume_bias_proxy | valid_domain | Phase 29=0.0115344360041 | candidate value may improve this proxy only if all required error guardrails pass | 0.0115344360041 | conditional_proxy_improvement_not_sufficient | no | Volume-bias proxy improvement alone cannot authorize pilot acceptance. |
| AT14 | level_boundary | claim_scope | all_outputs | Phase 31/32/33 Level 4+ boundary statements | all claims must remain Level 4+ proxy diagnostics with no Level 5, SWE/PINN, strict conservation, full mass conservation, or hydrodynamic closure claim |  | mandatory_claim_boundary | yes | A future pilot remains proxy-scoped and cannot rely on unavailable Level 5 variables. |

## 4. Rejection thresholds

Rejection threshold rows: 9.

| rejection_id | rejection_rule | trigger_metric_group | trigger_metric_name | trigger_region | trigger_condition | required_for_pilot_rejection | rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RT01 | phase29_tradeoff_pattern | multi_metric | absolute_relative_volume_bias_proxy_plus_error_metrics | valid_domain | absolute relative volume-bias proxy improves while RMSE, MAE, false-dry rate, and false-wet rate all worsen versus Phase 27 | yes | This is the Phase 29 trade-off pattern and is a hard rejection. |
| RT02 | target_metric_worsens_under_targeted_pilot | manhole_nonzero_target | false_dry_rate | manhole_nonzero_valid | candidate false_dry_rate > Phase 29 value 0.131297982994 | yes | A manhole false-dry pilot cannot worsen the selected target failure metric. |
| RT03 | high_impervious_false_wet_substantial_worsening | guardrail_masked | false_wet_rate | high_impervious_valid | candidate false_wet_rate > Phase 29 value 0.0239893681941 | yes | Substantial high-impervious false-wet expansion blocks acceptance. |
| RT04 | boundary_ring_false_dry_substantial_worsening | guardrail_masked | false_dry_rate | boundary_ring | candidate false_dry_rate > Phase 29 value 0.105112739216 | yes | Substantial boundary-ring false-dry degradation blocks acceptance. |
| RT05 | standard_rmse_or_mae_worsens_beyond_tolerance | standard | rmse_or_mae | all_evaluated_cells | standard RMSE > 0.0445000304105 or standard MAE > 0.0181490102048 | yes | Global error regressions beyond a hard tolerance reject the pilot. |
| RT06 | wet_dry_iou_declines_beyond_tolerance | standard | wet_dry_iou | all_evaluated_cells | wet_dry_iou < 0.802801373632 | yes | Wet/dry classification decline beyond tolerance rejects the pilot. |
| RT07 | valid_domain_error_worsens_beyond_acceptance_tolerance | valid_domain_masked | rmse_or_mae | valid_domain | valid RMSE > 0.0470043492351 or valid MAE > 0.0187366452965 | yes | Masked valid-domain depth errors remain required guardrails. |
| RT08 | requires_seed_expansion_or_sweep_to_interpret | study_design | interpretability | seed42_only | result cannot be interpreted without seed123, seed202, or a sweep | yes | Phase 34 does not authorize seed expansion or sweeps to rescue ambiguous results. |
| RT09 | claim_exceeds_level4_plus_proxy_scope | level_boundary | claim_scope | all_outputs | any claim states or implies Level 5 support, SWE/PINN residuals, strict conservation, full mass conservation, or hydrodynamic closure | yes | Unsupported strong-physics claims are hard rejection conditions. |

## 5. Phase 29 trade-off rejection rule

RT01 rejects any future result that improves the absolute relative volume-bias proxy while worsening valid-domain RMSE, MAE, false-dry rate, and false-wet rate versus Phase 27. This prevents repeating the Phase 29 pattern and does not claim Phase 29 success.

## 6. Manhole-nonzero false-dry pilot target

The future candidate is fixed only for threshold design: `manhole_nonzero_false_dry_guardrail`. Acceptance requires `manhole_nonzero_valid` `false_dry_rate` to improve versus Phase 29 and be no higher than Phase 27.

## 7. Threshold readiness status

Readiness rows: 7.

| criterion | status | evidence | blocker | next_required_action |
| --- | --- | --- | --- | --- |
| baseline_metric_table_generated | met | 23 Phase 25/27/29 baseline metric rows fixed | none | Use fixed baselines in a future pilot implementation plan. |
| single_future_candidate_locked_for_thresholds | met | candidate=manhole_nonzero_false_dry_guardrail; region=manhole_nonzero_valid; metric=false_dry_rate | none | Do not train; translate this into a separate implementation plan first. |
| acceptance_thresholds_fixed | met_pre_pilot_thresholds_formalized | 14 acceptance thresholds generated | training still blocked | Review thresholds in the future pilot implementation plan. |
| rejection_thresholds_fixed | met_pre_pilot_thresholds_formalized | 9 hard rejection rules generated | training still blocked | Carry rejection rules forward unchanged unless explicitly revised. |
| phase29_tradeoff_rejection_rule_written | met | RT01 rejects volume-bias proxy improvement with concurrent RMSE/MAE/false-dry/false-wet worsening. | none | Do not claim Phase 29 success. |
| level4_plus_scope_preserved | met | Acceptance and rejection rules include mandatory Level 4+ proxy claim boundary. | none | Keep all future pilot wording at proxy-diagnostic scope. |
| phase34_training_authorization | not_authorized | Phase 33 prior decision=pilot_design_ready_but_training_not_started; Phase 34 decision=thresholds_formalized_training_still_blocked | Phase 34 is threshold formalization only. | pilot_implementation_plan |

## 8. Current decision

Decision: `thresholds_formalized_training_still_blocked`.

Training authorized: `false`.

## 9. Why training remains blocked

Phase 34 only formalizes thresholds. It does not implement a loss, config, architecture change, or training run. A separate pilot implementation plan is still required before any future training decision.

## 10. Next allowed step

Next allowed step: `pilot_implementation_plan`.

## 11. Level boundary

All conclusions remain Level 4+ proxy diagnostics. This script does not claim strict conservation, full mass conservation, SWE/PINN behavior, or hydrodynamic closure.
