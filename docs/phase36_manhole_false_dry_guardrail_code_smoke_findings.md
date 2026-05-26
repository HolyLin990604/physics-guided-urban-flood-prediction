# Phase 36 Manhole False-Dry Guardrail Code / Smoke-Test Findings

## 1. Executive Summary

Phase 36 implemented the first code-level support for the `manhole_nonzero_false_dry_guardrail` candidate and completed no-training smoke checks for the new code path.

The implementation is code-smoke ready, but it does not authorize training. The current Phase 36 decision is:

`code_smoke_ready_training_still_blocked`

No seed42 training run was executed, and no seed123 or seed202 expansion was executed.

## 2. Implemented Components

Phase 36 added or updated the following implementation artifacts:

- `utils/physics_losses.py`
- `configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`
- `scripts/check_phase36_pilot_guardrails.py`
- `analysis/phase36_manhole_false_dry_guardrail_code_smoke/guardrail_checker_dry_run.json`
- `analysis/phase36_manhole_false_dry_guardrail_code_smoke/guardrail_checker_dry_run.md`
- `analysis/phase36_manhole_false_dry_guardrail_code_smoke/smoke_test_summary.json`
- `analysis/phase36_manhole_false_dry_guardrail_code_smoke/smoke_test_summary.md`

These components are limited to code support, config drafting, guardrail-checker staging, and smoke-test reporting.

## 3. Loss Implementation Scope

Phase 36 added config-gated support for the `manhole_nonzero_false_dry_guardrail` loss candidate.

The loss remains scoped as a Level 4+ static-map-aware proxy diagnostic component. It is intended to target false-dry behavior in the `manhole_nonzero_valid` region when explicitly enabled by configuration.

This implementation does not claim strict conservation, full mass conservation, SWE/PINN behavior, or hydrodynamic closure.

## 4. Config Draft

Phase 36 created the seed42 config draft:

`configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`

The config loads successfully according to the smoke-test summary:

- `config_loaded`: `true`

This config is a draft for a possible future seed42 pilot review. Its existence does not authorize training.

## 5. Guardrail Checker

Phase 36 added:

`scripts/check_phase36_pilot_guardrails.py`

The checker reads the Phase 34 threshold inputs and stages the acceptance and rejection structures for a future trained-result check.

Dry-run evidence reports:

- `candidate`: `manhole_nonzero_false_dry_guardrail`
- `claim_scope`: `Level 4+ static-map-aware proxy diagnostics only`
- `training_authorized`: `false`
- `training_result_available`: `false`
- `decision`: `no_training_result_guardrail_check_dry_run`
- `status`: `dry_run_passed`
- `acceptance_threshold_count`: `14`
- `rejection_threshold_count`: `9`
- `baseline_metric_count`: `23`
- `acceptance_structure_ready`: `true`
- `rejection_structure_ready`: `true`

The guardrail checker passed dry-run mode only. It does not report pilot success because no Phase 36 training result was available.

## 6. Smoke Test Results

The Phase 36 smoke-test summary reports:

- `config_loaded`: `true`
- `loss_smoke_passed`: `true`
- `guardrail_checker_dry_run_passed`: `true`
- `training_authorized`: `false`
- `training_executed`: `false`
- `seed42_run_executed`: `false`
- `seed123_seed202_executed`: `false`
- `decision`: `code_smoke_ready_training_still_blocked`

These smoke checks used dummy tensors only and did not train a model.

## 7. Training Authorization Status

Training remains blocked.

Phase 36 explicitly reports:

- `training_authorized`: `false`
- `training_executed`: `false`
- `seed42_run_executed`: `false`
- `seed123_seed202_executed`: `false`

The seed42 config draft may support a future review, but Phase 36 itself does not authorize or execute a training run.

## 8. Level Boundary

All Phase 36 claims remain within Level 4+ static-map-aware proxy scope.

The implemented guardrail loss and checker are diagnostic and guardrail-oriented support components. Phase 36 does not establish pilot success, Phase 29 success, strict conservation, full mass conservation, SWE/PINN status, or hydrodynamic closure.

## 9. What Is Allowed Next

The next allowed step is a training readiness review or explicit training authorization review.

Such a review may examine whether the seed42 Phase 36 draft config is appropriate to run in a later phase. Any future training decision should remain separate from the Phase 36 code-smoke result.

## 10. What Is Not Allowed

Phase 36 does not allow:

- automatic training;
- a seed42 40-epoch run without separate authorization;
- seed123 or seed202 expansion;
- sweeps;
- claims of pilot success;
- claims of Phase 29 success;
- claims of strict conservation;
- claims of full mass conservation;
- claims of SWE/PINN behavior;
- claims of hydrodynamic closure.

## 11. Final Conclusion

Phase 36 successfully implemented and smoke-tested the config-gated `manhole_nonzero_false_dry_guardrail` code path and guardrail checker. The implementation is code-smoke ready, but training remains blocked. The next phase may review whether seed42 training can be authorized, but no automatic training is authorized by Phase 36.
