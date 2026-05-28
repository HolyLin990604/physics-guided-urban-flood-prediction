# Phase 39 Failed Pilot Trade-Off Diagnosis Plan

## 1. Executive Summary

Phase 39 is a diagnostic-only phase to explain why the Phase 38 seed42 `manhole_nonzero_false_dry_guardrail` pilot was rejected.

Phase 38 completed the single authorized seed42 training run, test evaluation, and guardrail evaluation. The final decision was:

`seed42_pilot_rejected`

Phase 39 will not train, modify loss terms, modify configs, modify model architecture, run additional seeds, perform sweeps, or rescue Phase 38 post hoc. Its purpose is to analyze the rejected result, compare it with fixed seed42 baselines, identify regional and scenario-level trade-off mechanisms, and document why the Phase 34 acceptance and rejection framework rejected the pilot.

Expected diagnostic script:

`scripts/diagnose_phase39_failed_pilot_tradeoffs.py`

Expected output directory:

`analysis/phase39_failed_pilot_tradeoff_diagnosis/`

## 2. Background from Phase 38

Phase 38 ran only the authorized seed42 pilot:

`configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`

The trained result was evaluated on the test split:

`runs/phase36_manhole_false_dry_guardrail_seed42_40e/evaluation_test/`

The Phase 38 guardrail evaluation outputs are stored in:

`analysis/phase38_seed42_pilot_training_guardrail_evaluation/`

The final Phase 38 decision was:

`seed42_pilot_rejected`

The failed acceptance checks were:

- AT02 valid-domain RMSE failed.
- AT03 valid-domain MAE failed.
- AT04 valid-domain false_dry_rate failed.
- AT06 high_impervious_valid false_wet_rate failed.
- AT07 boundary_ring false_dry_rate failed.
- AT08 standard RMSE failed.
- AT09 standard MAE failed.
- AT10 standard wet_dry_iou failed.

The triggered rejection rules were:

- RT01 `phase29_tradeoff_pattern`
- RT05 `standard_rmse_or_mae_worsens_beyond_tolerance`
- RT07 `valid_domain_error_worsens_beyond_acceptance_tolerance`

Phase 38 must be treated as useful negative evidence, not as pilot success and not as a training or evaluation failure.

## 3. Diagnostic Questions

Phase 39 should answer these diagnostic questions:

1. Which failed acceptance components drove the Phase 38 rejection?
2. Did the pilot improve the intended manhole-related proxy while shifting error into valid-domain, high-impervious, boundary-ring, or standard metrics?
3. Which regions contributed most to the valid-domain RMSE, valid-domain MAE, and valid-domain false-dry failures?
4. Why did high-impervious valid false-wet rate fail despite the pilot targeting false-dry behavior?
5. Why did boundary-ring false-dry rate fail, and is this consistent with a boundary trade-off observed in earlier phases?
6. Which scenarios, timesteps, or event regimes contributed most to the standard RMSE, MAE, and wet/dry IoU failures?
7. How closely does the Phase 38 result repeat the Phase 29 trade-off pattern captured by RT01?
8. Did the rejected pilot create a localized improvement that was outweighed by broader valid-domain or standard-metric degradation?
9. What failure mechanism should be understood before any future loss redesign is proposed?

## 4. Required Inputs

Phase 39 should use existing artifacts only.

Required Phase 38 inputs:

- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_standard_metric_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_acceptance_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_rejection_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_guardrail_decision.json`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_guardrail_decision.md`
- `runs/phase36_manhole_false_dry_guardrail_seed42_40e/evaluation_test/`

Required threshold and baseline inputs:

- `analysis/phase34_pilot_thresholds/baseline_metric_table.csv`
- `analysis/phase34_pilot_thresholds/acceptance_thresholds.csv`
- `analysis/phase34_pilot_thresholds/rejection_thresholds.csv`
- `analysis/phase34_pilot_thresholds/phase34_threshold_summary.json`
- `analysis/phase34_pilot_thresholds/phase34_threshold_summary.md`

Required masked diagnostic context:

- `analysis/phase31_physics_input_recovery_readiness/`

Prior seed42 baselines should be used if available:

- Phase 25 seed42 baseline.
- Phase 27 seed42 baseline.
- Phase 29 seed42 baseline.

Phase 39 should record missing optional inputs explicitly rather than regenerating them through training.

## 5. Planned Comparisons

Phase 39 should compare the Phase 38 rejected pilot against fixed prior seed42 baselines and predeclared thresholds.

Minimum comparisons:

- Phase 38 versus Phase 25 seed42 standard metrics.
- Phase 38 versus Phase 27 seed42 standard metrics.
- Phase 38 versus Phase 29 seed42 standard metrics.
- Phase 38 versus Phase 34 acceptance thresholds.
- Phase 38 versus Phase 34 rejection thresholds.
- Phase 38 valid-domain masked metrics versus prior seed42 baselines.
- Phase 38 guardrail-region metrics versus prior seed42 baselines.
- Phase 38 target-region behavior versus broader valid-domain and standard-metric behavior.

The comparisons should emphasize direction, magnitude, and acceptance/rejection consequence:

- improved, maintained, worsened, or unavailable;
- absolute delta;
- relative delta where meaningful;
- pass/fail status under Phase 34 rules;
- whether the metric contributes to AT failure or RT trigger.

## 6. Regional Trade-Off Diagnosis

Phase 39 should diagnose whether the rejected pilot moved error across regions.

Required regional focus:

- valid_domain
- manhole_nonzero_valid if available
- high_impervious_valid
- boundary_ring
- all_evaluated_cells

For each region, Phase 39 should summarize:

- RMSE.
- MAE.
- false_dry_rate.
- false_wet_rate.
- wet/dry IoU if available.
- false-dry volume-loss proxy if available.
- false-wet volume-excess proxy if available.
- delta versus Phase 25 / Phase 27 / Phase 29 seed42 where available.
- whether the direction supports a target improvement or a harmful trade-off.

The key diagnostic issue is whether the manhole false-dry guardrail reduced a narrow target error while increasing valid-domain errors, high-impervious false-wet behavior, or boundary-ring false-dry behavior.

## 7. Scenario-Level Trade-Off Diagnosis

Phase 39 should diagnose whether the Phase 38 failures were broad or concentrated in specific scenarios, timesteps, or regimes.

Scenario-level diagnosis should summarize:

- scenario-level RMSE and MAE deltas where available;
- scenario-level wet/dry IoU deltas where available;
- false-dry and false-wet rate deltas by scenario where available;
- timesteps with the largest Phase 38 worsening relative to baselines;
- whether worsening concentrates near peak inundation, recession, dry-to-wet transition, or boundary-sensitive periods;
- whether a small number of scenarios dominate the standard RMSE, MAE, or wet/dry IoU failures.

If per-scenario forecast maps or per-step outputs are unavailable in the required inputs, the script should state that limitation and restrict conclusions to available aggregate and masked diagnostics.

## 8. Rejection Rule Diagnosis

Phase 39 should explain each triggered rejection rule in plain diagnostic terms.

RT01 `phase29_tradeoff_pattern`:

- Compare Phase 38 metric directions against the Phase 29 trade-off pattern.
- Identify which components match the earlier pattern.
- State whether the target-region behavior appears to be offset by broader error degradation.

RT05 `standard_rmse_or_mae_worsens_beyond_tolerance`:

- Identify whether RMSE, MAE, or both exceeded hard rejection tolerance.
- Report observed values, thresholds, and deltas.
- Explain whether this is broad standard-metric degradation or a localized contribution if supporting inputs exist.

RT07 `valid_domain_error_worsens_beyond_acceptance_tolerance`:

- Identify whether valid-domain RMSE, MAE, or both exceeded acceptance tolerance.
- Report observed values, thresholds, and deltas.
- Connect valid-domain degradation to regional or scenario-level evidence where available.

The diagnosis should distinguish acceptance-check failure from rejection-rule trigger. Failed AT checks describe unmet acceptance criteria; triggered RT rules explain why the pilot cannot be accepted or expanded.

## 9. Expected Outputs

Phase 39 should write outputs to:

`analysis/phase39_failed_pilot_tradeoff_diagnosis/`

Required output files:

- `failed_acceptance_components.csv`
- `triggered_rejection_rules.csv`
- `phase38_vs_baselines_metric_comparison.csv`
- `region_tradeoff_summary.csv`
- `scenario_tradeoff_summary.csv`
- `phase39_tradeoff_diagnosis_summary.json`
- `phase39_tradeoff_diagnosis_summary.md`

Suggested fields for `failed_acceptance_components.csv`:

- `acceptance_id`
- `metric_group`
- `metric_name`
- `region`
- `observed`
- `threshold`
- `direction`
- `delta_to_threshold`
- `status`
- `diagnostic_interpretation`

Suggested fields for `triggered_rejection_rules.csv`:

- `rejection_id`
- `rule`
- `status`
- `trigger_metric_group`
- `trigger_metric_name`
- `trigger_region`
- `observed`
- `threshold_or_condition`
- `diagnostic_interpretation`

Suggested fields for `phase38_vs_baselines_metric_comparison.csv`:

- `metric_group`
- `metric_name`
- `region`
- `phase25_seed42`
- `phase27_seed42`
- `phase29_seed42`
- `phase38_seed42`
- `preferred_direction`
- `phase38_minus_phase25`
- `phase38_minus_phase27`
- `phase38_minus_phase29`
- `tradeoff_flag`
- `notes`

## 10. Guardrails

Phase 39 must follow these guardrails:

1. Do not train.
2. Do not run seed42 training again.
3. Do not run seed123.
4. Do not run seed202.
5. Do not perform multi-seed expansion.
6. Do not sweep loss weights, thresholds, masks, or configs.
7. Do not modify loss code.
8. Do not modify training configs.
9. Do not modify model architecture.
10. Do not change acceptance or rejection thresholds after seeing Phase 38.
11. Do not rescue Phase 38 post hoc.
12. Do not relabel the rejected Phase 38 pilot as accepted, mixed-positive, or successful.
13. Do not continue Phase 29.
14. Do not claim strict conservation.
15. Do not claim full mass conservation.
16. Do not claim SWE/PINN behavior.
17. Do not claim hydrodynamic closure.
18. Keep all conclusions at Level 4+ proxy diagnostic scope.

Phase 39 may only read existing artifacts, compute diagnostic comparisons, and write diagnostic outputs.

## 11. Success Criteria

Phase 39 succeeds if it:

- identifies all failed Phase 38 acceptance components;
- identifies all triggered Phase 38 rejection rules;
- compares Phase 38 against Phase 25, Phase 27, and Phase 29 seed42 baselines where available;
- explains whether Phase 38 repeated the Phase 29 trade-off pattern;
- separates regional trade-offs from standard metric failures;
- reports scenario-level concentration if the available inputs support it;
- documents missing inputs without filling gaps through new training;
- produces all required output files under `analysis/phase39_failed_pilot_tradeoff_diagnosis/`;
- preserves the final Phase 38 decision as `seed42_pilot_rejected`;
- avoids any action that would authorize more training or rescue the rejected pilot.

## 12. Final Conclusion

Phase 39 is diagnostic-only. It explains the rejected Phase 38 pilot and identifies trade-off mechanisms before any future loss redesign. It does not authorize more training.
