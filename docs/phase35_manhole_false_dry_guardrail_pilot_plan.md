# Phase 35 Manhole False-Dry Guardrail Pilot Plan

## 1. Executive Summary

Phase 35 plans a possible future Level 4+ static-map-aware, domain-aware, manhole-region false-dry guardrail pilot for `manhole_nonzero_false_dry_guardrail`.

Phase 35 does not authorize training yet. It is a plan-only phase intended to translate the Phase 34 threshold formalization into a concrete future implementation plan for review.

The possible future pilot candidate is:

- candidate: `manhole_nonzero_false_dry_guardrail`
- target region: `manhole_nonzero_valid`
- target metric: `false_dry_rate`
- training authorized: `false`
- next allowed status from Phase 35: `implementation_plan_ready`

Phase 35 must not modify losses, configs, model architecture, or training code.

## 2. Background

Phase 31 recovered valid-domain, boundary-ring, high-impervious, and manhole masks. These masks made it possible to evaluate static-map-aware and region-specific diagnostic behavior without claiming strict conservation, full mass conservation, SWE/PINN behavior, or hydrodynamic closure.

Phase 32 designed domain-aware and boundary-aware guardrails for future pilot evaluation. These guardrails preserved Level 4+ proxy scope and framed future changes as masked diagnostic and auxiliary objective candidates, not as Level 5 physical solvers.

Phase 33 selected `manhole_nonzero_false_dry_guardrail` as the strongest future candidate because `manhole_nonzero_valid` had the highest Phase 29 false-dry rate among the reviewed masked diagnostic regions. Phase 33 still set `training_authorized=false`.

Phase 34 fixed baseline, acceptance, and rejection thresholds for a possible future seed42-only pilot. It retained `training_authorized=false`, set the decision to `thresholds_formalized_training_still_blocked`, and identified `pilot_implementation_plan` as the next allowed step.

## 3. Candidate Pilot Definition

Candidate:

`manhole_nonzero_false_dry_guardrail`

Target region:

`manhole_nonzero_valid`

Target metric:

`false_dry_rate`

Target rationale:

`manhole_nonzero_valid` had the highest Phase 29 false-dry rate among the reviewed masked diagnostic regions. This makes it the strongest narrow candidate for a future targeted false-dry guardrail, provided the future pilot also satisfies all Phase 34 acceptance thresholds and rejection rules.

## 4. Pilot Objective Concept

A future implementation may define a config-gated Level 4+ proxy loss concept that gently penalizes false-dry behavior in the target region.

The concept should:

- penalize false-dry behavior only where the target is wet and the prediction is dry or low-confidence wet;
- restrict the target to `manhole_nonzero_valid` cells;
- optionally restrict the target to `valid_domain` as a parent mask;
- keep the loss gentle and auxiliary;
- avoid increasing false-wet expansion;
- remain a static-map-aware, domain-aware, masked proxy objective.

This objective is not implemented in Phase 35. Phase 35 only records the proposed design direction for review.

## 5. Proposed Future Code Components

The following components may be written only after this plan is reviewed and accepted. They are proposed components only:

- A config-gated loss term in `utils/physics_losses.py`, tentatively named `manhole_false_dry_guardrail` or `manhole_nonzero_false_dry_guardrail`.
- A seed42-only pilot config cloned from the current strongest baseline, likely Phase 25 or Phase 27 depending on evidence available at implementation time.
- A guardrail checker script, for example `scripts/check_phase35_pilot_guardrails.py`, to enforce the Phase 34 acceptance thresholds, rejection rules, and Level 4+ claim boundary.
- An optional masked evaluation helper using the Phase 31 masks for `valid_domain`, `boundary_ring`, `high_impervious_valid`, and `manhole_nonzero_valid`.

No Phase 35 code change is authorized by this document. No loss modification, config creation, training run, seed expansion, or sweep is part of Phase 35.

## 6. Baseline References

Phase 35 carries forward the Phase 34 fixed baselines:

- Phase 25 seed42
- Phase 27 seed42
- Phase 29 seed42

Phase 27 is the main threshold reference for many metrics because Phase 29 showed trade-off behavior. Phase 29 may be used as a failure-pattern reference and upper bound for the target false-dry behavior, but it must not be treated as a success pattern to continue.

## 7. Acceptance Thresholds

Phase 35 carries forward the Phase 34 acceptance thresholds:

| ID | Acceptance threshold |
| --- | --- |
| AT01 | `manhole_nonzero_valid` `false_dry_rate` must be below Phase 29 and no higher than Phase 27; threshold = `0.1172229713`. |
| AT02 | Valid-domain RMSE <= `0.0470043492351`. |
| AT03 | Valid-domain MAE <= `0.0187366452965`. |
| AT04 | Valid-domain `false_dry_rate` <= `0.068917464101`. |
| AT05 | Valid-domain `false_wet_rate` <= `0.0186922750833`. |
| AT06 | `high_impervious_valid` `false_wet_rate` <= `0.0227046722562`. |
| AT07 | `boundary_ring` `false_dry_rate` <= `0.087764984526`. |
| AT08 | Standard RMSE <= `0.0432286009702`. |
| AT09 | Standard MAE <= `0.0176304670561`. |
| AT10 | `wet_dry_iou` >= `0.807801373632`. |
| AT11 | `rollout_stability` >= `0.989122296308`. |
| AT12 | `step_rmse_std` <= `0.0105237349255`. |
| AT13 | Valid-domain `absolute_relative_volume_bias_proxy` <= `0.0115344360041` is conditional and not sufficient alone. |
| AT14 | All claims remain Level 4+ proxy scope. |

AT13 is conditional. A valid-domain volume-bias proxy improvement is not enough to accept a future pilot unless all required error, masked-region, and claim-boundary thresholds also pass.

## 8. Rejection Rules

Phase 35 carries forward the Phase 34 rejection rules:

| ID | Rejection rule |
| --- | --- |
| RT01 | Reject the Phase 29 trade-off pattern: volume-bias proxy improves while RMSE, MAE, false-dry rate, and false-wet rate worsen versus Phase 27. |
| RT02 | Reject if `manhole_nonzero_valid` `false_dry_rate` worsens beyond Phase 29. |
| RT03 | Reject high-impervious false-wet substantial worsening. |
| RT04 | Reject boundary-ring false-dry substantial worsening. |
| RT05 | Reject standard RMSE/MAE beyond tolerance. |
| RT06 | Reject wet/dry IoU decline beyond tolerance. |
| RT07 | Reject valid-domain RMSE/MAE beyond acceptance tolerance. |
| RT08 | Reject if result requires seed expansion or sweep to interpret. |
| RT09 | Reject any Level 5, SWE/PINN, strict conservation, full mass conservation, or hydrodynamic closure claim. |

These rejection rules prevent a future pilot from being accepted on a narrow proxy improvement while broader behavior degrades.

## 9. Training Authorization Status

`training_authorized = false`

Phase 35 may authorize only:

`implementation_plan_ready`

Phase 35 must not authorize:

`training_now`

## 10. Stop/Go Decision After Phase 35

Possible Phase 35 decisions:

- `implementation_plan_not_ready`
- `implementation_plan_ready_code_next`

In both cases:

`training_authorized=false`

If this plan is accepted, the next phase may implement code and smoke tests. Actual training must still wait until code review and the guardrail checker are ready.

## 11. Guardrails

Phase 35 guardrails:

- no training;
- no loss modification in Phase 35;
- no config creation in Phase 35 unless explicitly kept as proposed text only;
- no seed42 run;
- no seed123 or seed202 run;
- no sweep;
- no Phase 29 continuation;
- no strict conservation claim;
- no full mass conservation claim;
- no SWE/PINN claim;
- no hydrodynamic closure claim.

All claims must remain at Level 4+ proxy scope.

## 12. Final Conclusion

Phase 35, if completed, will provide a reviewed implementation plan for the `manhole_nonzero_false_dry_guardrail` pilot. It will not implement the loss, create a training config, run seed42, expand to seed123 or seed202, perform sweeps, continue Phase 29, or authorize training.

Actual code and training should only proceed in the next phase after this plan is committed. Even then, training must wait until code review and the guardrail checker are ready.
