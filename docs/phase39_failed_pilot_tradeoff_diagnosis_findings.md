# Phase 39 Failed Pilot Trade-Off Diagnosis Findings

## 1. Executive Summary

Phase 39 is diagnostic-only. It explains why the Phase 38 seed42 `manhole_nonzero_false_dry_guardrail` pilot remains rejected under the predeclared Level 4+ proxy guardrail framework.

No training was run in Phase 39. No loss, config, threshold, or model architecture was modified. Phase 39 only read existing Phase 38, Phase 34, and supporting diagnostic artifacts and wrote diagnostic summaries.

The final Phase 38 decision remains:

`seed42_pilot_rejected`

The Phase 39 diagnostic decision is:

`tradeoff_diagnosis_completed_with_missing_optional_inputs`

The diagnosis confirms that the rejected pilot should not be treated as accepted, mixed-positive, rescued, or successful. The current `manhole_nonzero_false_dry_guardrail` design likely shifted or failed to control broader errors rather than solving the wider Level 4+ reliability problem.

## 2. Inputs and Outputs

Phase 39 used existing artifacts only.

Primary Phase 38 inputs:

- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_standard_metric_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_acceptance_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_rejection_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_guardrail_decision.json`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_guardrail_decision.md`
- `runs/phase36_manhole_false_dry_guardrail_seed42_40e/evaluation_test/`

Primary Phase 34 threshold and baseline inputs:

- `analysis/phase34_pilot_thresholds/baseline_metric_table.csv`
- `analysis/phase34_pilot_thresholds/acceptance_thresholds.csv`
- `analysis/phase34_pilot_thresholds/rejection_thresholds.csv`
- `analysis/phase34_pilot_thresholds/phase34_threshold_summary.json`

Phase 39 outputs:

- `analysis/phase39_failed_pilot_tradeoff_diagnosis/failed_acceptance_components.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/triggered_rejection_rules.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/phase38_vs_baselines_metric_comparison.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/region_tradeoff_summary.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/scenario_tradeoff_summary.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/phase39_tradeoff_diagnosis_summary.json`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/phase39_tradeoff_diagnosis_summary.md`

Recorded diagnostic counts:

- `failed_acceptance_count = 8`
- `triggered_rejection_count = 3`
- `comparison_rows = 13`
- `region_rows = 5`
- `scenario_rows = 19`

## 3. Failed Acceptance Components

Phase 39 identified eight failed Phase 38 acceptance components.

| ID | Metric group | Metric | Region | Observed | Threshold | Interpretation |
| --- | --- | --- | --- | ---: | ---: | --- |
| AT02 | `valid_domain_masked` | `rmse` | `valid_domain` | 0.0482901961137 | 0.0470043492351 | Valid-domain RMSE exceeded the tolerance. |
| AT03 | `valid_domain_masked` | `mae` | `valid_domain` | 0.0191286913686 | 0.0187366452965 | Valid-domain MAE exceeded the tolerance. |
| AT04 | `valid_domain_masked` | `false_dry_rate` | `valid_domain` | 0.0718682210394 | 0.068917464101 | Valid-domain false-dry behavior was not controlled. |
| AT06 | `guardrail_masked` | `false_wet_rate` | `high_impervious_valid` | 0.0231264618198 | 0.0227046722562 | High-impervious false-wet behavior exceeded the regional guardrail. |
| AT07 | `guardrail_masked` | `false_dry_rate` | `boundary_ring` | 0.0920545695699 | 0.087764984526 | Boundary-ring false-dry behavior exceeded the regional guardrail. |
| AT08 | `standard` | `rmse` | `all_evaluated_cells` | 0.0445683014236 | 0.0432286009702 | Standard RMSE failed. |
| AT09 | `standard` | `mae` | `all_evaluated_cells` | 0.0179593140063 | 0.0176304670561 | Standard MAE failed. |
| AT10 | `standard` | `wet_dry_iou` | `all_evaluated_cells` | 0.806874058749 | 0.807801373632 | Standard wet/dry IoU fell below the required floor. |

These failures are broad enough that the pilot cannot be accepted based on a target-region improvement alone.

## 4. Triggered Rejection Rules

Phase 39 confirmed three triggered rejection rules.

| ID | Rule | Diagnostic meaning |
| --- | --- | --- |
| RT01 | `phase29_tradeoff_pattern` | The pilot matched a Phase29-like pattern: a valid-domain volume-bias proxy improved while multiple error metrics worsened versus Phase 27. |
| RT05 | `standard_rmse_or_mae_worsens_beyond_tolerance` | Standard global error worsened beyond hard rejection tolerance, driven by standard RMSE. |
| RT07 | `valid_domain_error_worsens_beyond_acceptance_tolerance` | Valid-domain RMSE or MAE exceeded the acceptance tolerance. |

Any triggered rejection rule is sufficient to block acceptance or expansion. Phase 38 triggered three.

## 5. Baseline Comparison Interpretation

The baseline comparison supports a conservative trade-off interpretation.

Against Phase 27 seed42, Phase 38 worsened on standard RMSE, standard MAE, standard wet/dry IoU, valid-domain RMSE, valid-domain MAE, valid-domain false-dry rate, valid-domain false-wet rate, high-impervious false-wet rate, and boundary-ring false-dry rate.

Phase 38 improved the target `manhole_nonzero_valid` false-dry rate relative to Phase 25, Phase 27, and Phase 29. It also improved the valid-domain absolute relative volume-bias proxy relative to Phase 27 and Phase 29. Those improvements were not sufficient for acceptance because broader valid-domain, regional guardrail, and standard metrics failed.

The important interpretation is not that every metric worsened. The important interpretation is that the targeted improvement did not preserve the required broader reliability checks.

## 6. Regional Trade-Off Interpretation

The regional summary shows failures in multiple regions:

- `valid_domain`: failed RMSE, MAE, and false-dry checks.
- `manhole_nonzero_valid`: did not fail an available check and showed target false-dry improvement.
- `high_impervious_valid`: failed false-wet guardrail.
- `boundary_ring`: failed false-dry guardrail.
- `all_evaluated_cells`: failed standard RMSE, MAE, and wet/dry IoU.

This pattern is consistent with a localized target improvement being outweighed by broader degradation or incomplete control of errors. The current guardrail design should therefore be treated as insufficient for Level 4+ reliability, not as a solved manhole false-dry problem.

## 7. Scenario-Level Limitation

Scenario diagnostics are limited.

Phase 39 produced 19 Phase38 per-batch diagnostic rows, but per-batch or scenario-level Phase25, Phase27, and Phase29 baselines were unavailable. Because of that missing optional input, Phase 39 cannot make a supported claim about scenario-level worsening relative to earlier phases.

The scenario output can describe Phase38-only batch variation. It should not be used to claim that a specific scenario, timestep, storm regime, peak, recession period, or transition period caused the rejection unless future diagnostics provide comparable baseline data.

## 8. Main Failure Mechanism

The main failure mechanism is a trade-off pattern rather than an execution failure.

Phase 38 appears to have improved the narrow `manhole_nonzero_valid` false-dry target, but this did not generalize into acceptable broader behavior. Valid-domain RMSE, MAE, and false-dry rate failed. High-impervious false-wet and boundary-ring false-dry guardrails failed. Standard RMSE, MAE, and wet/dry IoU also failed.

RT01 is central: the result resembles the earlier Phase29-like trade-off pattern, where an apparent improvement in one proxy is accompanied by unacceptable degradation in broader metrics. Conservative wording is required: the current evidence indicates that the `manhole_nonzero_false_dry_guardrail` design likely shifted or failed to control broader errors instead of solving the wider Level 4+ reliability problem.

## 9. What Is Not Allowed Next

Phase 39 does not allow:

- expansion to seed123;
- expansion to seed202;
- any multi-seed expansion;
- a sweep;
- Phase 29 continuation;
- post-hoc rescue of Phase 38;
- changing thresholds after seeing the result;
- relabeling the rejected pilot as accepted, mixed-positive, or successful;
- claiming pilot success;
- claiming strict conservation;
- claiming full mass conservation;
- claiming SWE/PINN behavior;
- claiming hydrodynamic closure;
- claiming Level 5 support.

The rejected pilot must remain rejected.

## 10. What Is Allowed Next

Allowed next work is limited to diagnosis, documentation, and design review.

Appropriate next steps include:

- accepting the Phase 38 negative result as final for this pilot;
- diagnosing why the target improvement did not preserve valid-domain and standard behavior;
- diagnosing why high-impervious false-wet and boundary-ring false-dry guardrails failed;
- reviewing whether the current target definition, mask interaction, or proxy objective is misaligned with the broader Level 4+ guardrail framework;
- designing a new approach only after this failed-pilot diagnosis is accepted.

Any future design must be separate from Phase 38 and must not be described as a rescue or continuation of the rejected pilot.

## 11. Level Boundary

All conclusions remain at Level 4+ proxy diagnostic scope.

Phase 39 does not establish strict conservation, full mass conservation, SWE/PINN residual satisfaction, hydrodynamic closure, or Level 5 physical support. The metrics are proxy diagnostics and guardrail checks for failure analysis. They are not proof of physical closure.

## 12. Final Conclusion

Phase 39 confirms that Phase 38 remains rejected.

The current `manhole_nonzero_false_dry_guardrail` pilot improved a narrow target proxy but failed broader valid-domain, regional guardrail, and standard checks. RT01 indicates a Phase29-like trade-off pattern. RT05 and RT07 confirm unacceptable standard and valid-domain error behavior.

The rejected pilot should not be expanded, swept, continued from Phase 29, rescued post hoc, or described as successful. Future work should begin with a failed-pilot design review and only then consider a genuinely new approach within Level 4+ proxy diagnostic boundaries.
