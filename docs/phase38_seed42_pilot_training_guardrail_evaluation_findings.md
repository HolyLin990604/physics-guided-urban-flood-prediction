# Phase 38 Seed42 Pilot Training Guardrail Evaluation Findings

## 1. Executive Summary

Phase 38 ran the single authorized seed42 pilot for the `manhole_nonzero_false_dry_guardrail` candidate, evaluated the trained result on the test split, and completed the predeclared guardrail evaluation.

The final Phase 38 decision is:

`seed42_pilot_rejected`

The rejection is based on failed standard metrics, failed masked acceptance checks, and triggered rejection rules. The result must not be interpreted as pilot success. The current `manhole_nonzero_false_dry_guardrail` design should not be treated as accepted.

The result is useful negative evidence. The targeted proxy improvement was not sufficient to pass the predeclared Level 4+ guardrail framework, and RT01 indicates that the result repeats a Phase 29-like trade-off pattern.

## 2. Training and Evaluation Completed

Phase 38 executed only the authorized seed42 training command:

```bash
python scripts/train_model.py --config configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json
```

Training completed. No seed123 run, seed202 run, multi-seed expansion, sweep, or post-hoc rescue run was performed.

The trained result was evaluated on the test split. The standard test evaluation output is:

`runs/phase36_manhole_false_dry_guardrail_seed42_40e/evaluation_test/metrics.json`

The guardrail evaluation was completed using:

`scripts/evaluate_phase38_seed42_guardrails.py`

The Phase 38 guardrail outputs are:

- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_standard_metric_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_acceptance_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_rejection_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_guardrail_decision.json`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_guardrail_decision.md`

## 3. Standard Test Metrics

The standard AT08-AT12 checks produced 2 passes and 3 failures.

| ID | Metric | Observed | Threshold | Direction | Status |
| --- | --- | ---: | ---: | --- | --- |
| AT08 | `rmse` | 0.0445683014236 | 0.0432286009702 | lower or equal | fail |
| AT09 | `mae` | 0.0179593140063 | 0.0176304670561 | lower or equal | fail |
| AT10 | `wet_dry_iou` | 0.806874058749 | 0.807801373632 | higher or equal | fail |
| AT11 | `rollout_stability` | 0.989964456935 | 0.989122296308 | higher or equal | pass |
| AT12 | `step_rmse_std` | 0.0101883552821 | 0.0105237349255 | lower or equal | pass |

The standard RMSE, MAE, and wet/dry IoU results did not satisfy the predeclared acceptance thresholds.

## 4. Acceptance Threshold Results

The acceptance check summary is:

- `acceptance_checks_passed = 6`
- `acceptance_checks_failed = 8`
- `acceptance_checks_not_evaluated = 0`

The failed acceptance checks are:

| ID | Metric group | Metric | Region | Observed | Threshold | Status |
| --- | --- | --- | --- | ---: | ---: | --- |
| AT02 | `valid_domain_masked` | `rmse` | `valid_domain` | 0.0482901961137 | 0.0470043492351 | fail |
| AT03 | `valid_domain_masked` | `mae` | `valid_domain` | 0.0191286913686 | 0.0187366452965 | fail |
| AT04 | `valid_domain_masked` | `false_dry_rate` | `valid_domain` | 0.0718682210394 | 0.068917464101 | fail |
| AT06 | `guardrail_masked` | `false_wet_rate` | `high_impervious_valid` | 0.0231264618198 | 0.0227046722562 | fail |
| AT07 | `guardrail_masked` | `false_dry_rate` | `boundary_ring` | 0.0920545695699 | 0.087764984526 | fail |
| AT08 | `standard` | `rmse` | `all_evaluated_cells` | 0.0445683014236 | 0.0432286009702 | fail |
| AT09 | `standard` | `mae` | `all_evaluated_cells` | 0.0179593140063 | 0.0176304670561 | fail |
| AT10 | `standard` | `wet_dry_iou` | `all_evaluated_cells` | 0.806874058749 | 0.807801373632 | fail |

These failures show that the target proxy was not sufficient to preserve the required valid-domain, guardrail-region, and standard test behavior.

## 5. Rejection Rule Results

The rejection rule summary is:

- `rejection_rules_triggered = 3`
- `rejection_rules_not_evaluated = 0`

The triggered rejection rules are:

| ID | Rule | Status | Interpretation |
| --- | --- | --- | --- |
| RT01 | `phase29_tradeoff_pattern` | triggered | The result repeats the predeclared Phase 29-like trade-off pattern. |
| RT05 | `standard_rmse_or_mae_worsens_beyond_tolerance` | triggered | Standard RMSE exceeded the hard rejection tolerance. |
| RT07 | `valid_domain_error_worsens_beyond_acceptance_tolerance` | triggered | Valid-domain RMSE and MAE exceeded acceptance tolerance. |

Any triggered RT01-RT09 rule is sufficient to reject the pilot. Phase 38 triggered three rejection rules.

## 6. Final Decision

The final Phase 38 decision is:

`seed42_pilot_rejected`

The decision summary is:

- `standard_checks_passed = 2`
- `standard_checks_failed = 3`
- `acceptance_checks_passed = 6`
- `acceptance_checks_failed = 8`
- `acceptance_checks_not_evaluated = 0`
- `rejection_rules_triggered = 3`
- `rejection_rules_not_evaluated = 0`

This is a rejection under the predeclared Level 4+ guardrail framework.

## 7. Interpretation

Phase 38 provides negative evidence for the current `manhole_nonzero_false_dry_guardrail` design.

The result may show improvement on a targeted proxy, but that improvement is not enough for acceptance. The pilot failed required valid-domain error checks, standard RMSE and MAE checks, wet/dry IoU acceptance, and multiple guardrail-region checks.

RT01 is especially important because it flags a Phase 29-like trade-off pattern. The result should therefore be treated as evidence that this guardrail design can shift error rather than resolve the broader failure mode under the predeclared checks.

Future work should diagnose why the guardrail caused these trade-offs before designing another loss. The next step should be analysis, not expansion or rescue.

## 8. What Is Not Allowed Next

Phase 38 does not allow:

- expansion to seed123;
- expansion to seed202;
- multi-seed expansion;
- sweeps;
- post-hoc loss or config rescue for this pilot;
- treating the current `manhole_nonzero_false_dry_guardrail` design as accepted;
- claiming pilot success;
- claiming Phase 29 success;
- claiming strict conservation;
- claiming full mass conservation;
- claiming SWE/PINN behavior;
- claiming hydrodynamic closure;
- claiming Level 5 support.

The rejected seed42 result must not be rescued by changing thresholds, changing the loss, changing the config, or adding seeds after seeing the outcome.

## 9. What Is Allowed Next

Allowed next work is limited to conservative diagnosis and documentation.

Appropriate next steps include:

- inspecting which regions and frames drove the valid-domain RMSE and MAE increases;
- diagnosing why valid-domain false-dry behavior worsened;
- diagnosing why high-impervious false-wet and boundary-ring false-dry guardrails failed;
- comparing the observed trade-off against the Phase 29 pattern used by RT01;
- documenting candidate failure modes before proposing any new loss;
- preparing a separate future design review if a different loss or diagnostic experiment is proposed.

Any future design should remain separate from this rejected pilot and should not be presented as a continuation, rescue, or success of Phase 38.

## 10. Level Boundary

All Phase 38 wording remains Level 4+ static-map-aware proxy scope only.

Phase 38 does not establish strict conservation, full mass conservation, SWE/PINN residual satisfaction, hydrodynamic closure, or Level 5 physical support.

The metrics used here are proxy diagnostics and guardrail checks. They are useful for model comparison and failure analysis, but they do not establish physical closure.

## 11. Final Conclusion

Phase 38 ran the single authorized seed42 pilot, completed training, completed test evaluation, completed guardrail evaluation, and reached the final decision `seed42_pilot_rejected`.

The pilot must not be expanded to seed123 or seed202. No sweep is allowed. No post-hoc loss or config rescue is allowed. The current `manhole_nonzero_false_dry_guardrail` design should not be treated as accepted.

The result is useful negative evidence: the target proxy was not sufficient to pass the predeclared Level 4+ guardrail framework, and RT01 shows that the result repeats a Phase 29-like trade-off pattern. Future work should diagnose the trade-offs before designing another loss.
