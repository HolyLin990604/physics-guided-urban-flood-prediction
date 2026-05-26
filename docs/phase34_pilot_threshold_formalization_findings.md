# Phase 34 Pilot Threshold Formalization Findings

## 1. Executive Summary

Phase 34 is a threshold-formalization phase only. It formalizes pre-pilot baseline, acceptance, and rejection criteria for a possible future seed42 pilot, but it does not train, modify losses, modify training configs, modify model architecture, run sweeps, continue Phase 29, or expand to other seeds.

The Phase 34 outputs fix Phase 25 / Phase 27 / Phase 29 seed42 baseline metrics and define predeclared acceptance and rejection thresholds for a possible future `manhole_nonzero_false_dry_guardrail` pilot. The target region is `manhole_nonzero_valid`, and the target metric is `false_dry_rate`.

The generated summary reports:

- baseline metric rows: 23
- acceptance threshold rows: 14
- rejection threshold rows: 9
- readiness rows: 7
- decision: `thresholds_formalized_training_still_blocked`
- training authorized: `false`
- next allowed step: `pilot_implementation_plan`

This finding does not authorize training and does not claim pilot success. The next allowed step is a pilot implementation plan, not a training run.

## 2. Inputs and Outputs

Phase 34 used the threshold formalization plan and prior diagnostic evidence from the Phase 25, Phase 27, Phase 29, Phase 31, Phase 32, and Phase 33 artifacts.

The Phase 34 implementation and outputs are:

- `docs/phase34_pilot_threshold_formalization_plan.md`
- `scripts/formalize_phase34_pilot_thresholds.py`
- `analysis/phase34_pilot_thresholds/baseline_metric_table.csv`
- `analysis/phase34_pilot_thresholds/acceptance_thresholds.csv`
- `analysis/phase34_pilot_thresholds/rejection_thresholds.csv`
- `analysis/phase34_pilot_thresholds/threshold_readiness_status.csv`
- `analysis/phase34_pilot_thresholds/phase34_threshold_summary.json`
- `analysis/phase34_pilot_thresholds/phase34_threshold_summary.md`

The summary evidence fixes the current result as a threshold document set only. No training, loss implementation, config implementation, architecture change, or seed expansion is part of Phase 34.

## 3. Baselines Fixed

Phase 34 fixes 23 baseline metric rows across the Phase 25, Phase 27, and Phase 29 seed42 references. These baselines are now available for future pilot acceptance and rejection checks.

The fixed baseline groups include:

- standard evaluation metrics;
- valid-domain masked metrics;
- manhole-nonzero target metrics;
- boundary-ring and high-impervious guardrail metrics;
- Level 4+ claim-boundary support.

The baselines are fixed for comparison and decision control. They do not imply that Phase 29 succeeded, and they do not authorize a new pilot.

## 4. Acceptance Thresholds

Phase 34 defines 14 acceptance threshold rows. These thresholds are pre-pilot criteria for a possible future `manhole_nonzero_false_dry_guardrail` seed42 pilot.

The selected target threshold is:

| ID | Metric | Region | Rule | Threshold |
| --- | --- | --- | --- | ---: |
| AT01 | `false_dry_rate` | `manhole_nonzero_valid` | Candidate value must be below Phase 29 and no higher than Phase 27. | 0.1172229713 |

AT01 uses:

- Phase 27 `manhole_nonzero_valid` `false_dry_rate`: 0.1172229713
- Phase 29 `manhole_nonzero_valid` `false_dry_rate`: 0.131297982994
- threshold: 0.1172229713

The other acceptance thresholds are:

| ID | Metric | Region | Threshold | Interpretation |
| --- | --- | --- | ---: | --- |
| AT02 | `rmse` | `valid_domain` | 0.0470043492351 | Valid-domain RMSE must stay within the Phase 27 tolerance. |
| AT03 | `mae` | `valid_domain` | 0.0187366452965 | Valid-domain MAE must stay within the Phase 27 tolerance. |
| AT04 | `false_dry_rate` | `valid_domain` | 0.068917464101 | Valid-domain false-dry rate must not worsen versus Phase 27. |
| AT05 | `false_wet_rate` | `valid_domain` | 0.0186922750833 | Valid-domain false-wet rate must stay within the predeclared tolerance. |
| AT06 | `false_wet_rate` | `high_impervious_valid` | 0.0227046722562 | High-impervious false-wet behavior must stay within the guardrail tolerance. |
| AT07 | `false_dry_rate` | `boundary_ring` | 0.087764984526 | Boundary-ring false-dry behavior must stay within the guardrail tolerance. |
| AT08 | `rmse` | `all_evaluated_cells` | 0.0432286009702 | Standard RMSE must stay within the global tolerance. |
| AT09 | `mae` | `all_evaluated_cells` | 0.0176304670561 | Standard MAE must stay within the global tolerance. |
| AT10 | `wet_dry_iou` | `all_evaluated_cells` | 0.807801373632 | Wet/dry IoU must not materially decline. |
| AT11 | `rollout_stability` | `all_evaluated_cells` | 0.989122296308 | Rollout stability must not materially decline. |
| AT12 | `step_rmse_std` | `all_evaluated_cells` | 0.0105237349255 | Step-wise RMSE variability must remain bounded. |
| AT13 | `absolute_relative_volume_bias_proxy` | `valid_domain` | 0.0115344360041 | Conditional proxy improvement only; not sufficient alone. |
| AT14 | `claim_scope` | `all_outputs` | n/a | Claims must remain within Level 4+ proxy scope. |

AT13 is explicitly conditional. Improvement in valid-domain absolute relative volume-bias proxy is not sufficient for pilot acceptance unless all required error and guardrail thresholds also pass.

## 5. Rejection Thresholds

Phase 34 defines 9 rejection threshold rows. These are hard rejection rules for a possible future pilot.

The rejection rules are:

| ID | Rule | Rejection condition |
| --- | --- | --- |
| RT01 | Phase 29 trade-off pattern | Reject if absolute relative volume-bias proxy improves while RMSE, MAE, false-dry rate, and false-wet rate all worsen versus Phase 27. |
| RT02 | Target metric worsens under targeted pilot | Reject if `manhole_nonzero_valid` `false_dry_rate` worsens beyond the Phase 29 value. |
| RT03 | High-impervious false-wet substantial worsening | Reject substantial worsening in `high_impervious_valid` `false_wet_rate`. |
| RT04 | Boundary-ring false-dry substantial worsening | Reject substantial worsening in `boundary_ring` `false_dry_rate`. |
| RT05 | Standard RMSE/MAE beyond tolerance | Reject standard RMSE or MAE beyond hard tolerance. |
| RT06 | Wet/dry IoU decline beyond tolerance | Reject wet/dry IoU decline beyond tolerance. |
| RT07 | Valid-domain RMSE/MAE beyond acceptance tolerance | Reject valid-domain RMSE or MAE beyond acceptance tolerance. |
| RT08 | Requires seed expansion or sweep to interpret | Reject if the result cannot be interpreted without seed123, seed202, or a sweep. |
| RT09 | Claim exceeds Level 4+ proxy scope | Reject claims that exceed Level 4+ proxy diagnostics. |

These rejection rules prevent a future pilot from being accepted on a narrow proxy gain while broader error and guardrail behavior degrades.

## 6. Phase 29 Trade-Off Rejection Rule

Phase 34 writes the Phase 29 trade-off pattern as a hard rejection rule.

RT01 rejects a future result if the valid-domain absolute relative volume-bias proxy improves while valid-domain RMSE, MAE, false-dry rate, and false-wet rate all worsen versus Phase 27. This is conservative because it treats the Phase 29 pattern as a failure mode to avoid, not as a success pattern to repeat.

This rule does not claim Phase 29 success. It uses Phase 29 as evidence for a trade-off that future pilot design must avoid.

## 7. Future Candidate Target

The future candidate remains:

`manhole_nonzero_false_dry_guardrail`

The target is fixed for threshold design as:

- target region: `manhole_nonzero_valid`
- target metric: `false_dry_rate`

This candidate is only a future pilot candidate. Phase 34 does not implement the candidate, does not train it, and does not claim that the target failure mode has been corrected.

## 8. Current Decision

The current Phase 34 decision is:

`thresholds_formalized_training_still_blocked`

Training authorized:

`false`

Next allowed step:

`pilot_implementation_plan`

This decision means that Phase 34 completed threshold formalization but did not clear the project for immediate training.

## 9. Why Training Remains Blocked

Training remains blocked because Phase 34 is threshold formalization only.

It does not:

- implement a new loss;
- modify `utils/physics_losses.py`;
- create or modify training configs;
- modify model architecture;
- run seed42;
- run seed123 or seed202;
- perform sweeps;
- continue Phase 29.

A separate pilot implementation plan is still required before any training decision. That plan may specify loss/config design, but the plan itself should be reviewed and committed before actual training begins.

## 10. Next Allowed Step

The next allowed step is:

`pilot_implementation_plan`

The pilot implementation plan may translate the fixed Phase 34 thresholds into a concrete proposed design for a future `manhole_nonzero_false_dry_guardrail` seed42 pilot. It should preserve the Phase 34 acceptance thresholds, rejection thresholds, Phase 29 trade-off rejection rule, and Level 4+ claim boundary.

The next allowed step is not training.

## 11. Level Boundary and Guardrails

All Phase 34 conclusions remain Level 4+ proxy diagnostics.

Phase 34 does not claim:

- strict conservation;
- full mass conservation;
- SWE/PINN behavior;
- hydrodynamic closure;
- Level 5 physical support;
- pilot success;
- Phase 29 success.

The threshold set also preserves the claim boundary through AT14 and RT09. Any future pilot interpretation must remain within static-map-aware, domain-aware, boundary-aware, and masked proxy diagnostic scope unless separate evidence supports a stronger claim.

## 12. Final Conclusion

Phase 34 completes baseline, acceptance, and rejection threshold formalization for a possible future `manhole_nonzero_false_dry_guardrail` seed42 pilot. It fixes 23 baseline metric rows, defines 14 acceptance threshold rows, defines 9 rejection threshold rows, writes the Phase 29 trade-off pattern as a hard rejection rule, and preserves the Level 4+ proxy boundary.

It does not authorize training. The next allowed step is a pilot implementation plan, where loss/config design may be specified, but actual training should still wait until that implementation plan is reviewed and committed.
