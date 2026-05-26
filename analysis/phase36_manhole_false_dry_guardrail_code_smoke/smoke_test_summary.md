# Phase 36 Code Smoke Summary

- config_loaded: `true`
- loss_smoke_passed: `true`
- guardrail_checker_dry_run_passed: `true`
- training_authorized: `false`
- training_executed: `false`
- seed42_run_executed: `false`
- seed123_seed202_executed: `false`
- decision: `code_smoke_ready_training_still_blocked`

## Files Changed

- `utils/physics_losses.py`
- `configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`
- `scripts/check_phase36_pilot_guardrails.py`
- `analysis/phase36_manhole_false_dry_guardrail_code_smoke/guardrail_checker_dry_run.json`
- `analysis/phase36_manhole_false_dry_guardrail_code_smoke/guardrail_checker_dry_run.md`
- `analysis/phase36_manhole_false_dry_guardrail_code_smoke/smoke_test_summary.json`
- `analysis/phase36_manhole_false_dry_guardrail_code_smoke/smoke_test_summary.md`

## Notes

- Smoke checks used dummy tensors only and did not train a model.
- The new loss remains config-gated and Level 4+ proxy scoped.
- The Phase 36 run output directory was not created by these checks.
