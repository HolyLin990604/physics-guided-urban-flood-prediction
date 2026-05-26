# Phase 36 Pilot Guardrail Checker Dry Run

- candidate: `manhole_nonzero_false_dry_guardrail`
- claim_scope: `Level 4+ static-map-aware proxy diagnostics only`
- training_authorized: `false`
- training_result_available: `false`
- decision: `no_training_result_guardrail_check_dry_run`
- status: `dry_run_passed`

## Phase 34 Inputs

- acceptance_thresholds: `analysis\phase34_pilot_thresholds\acceptance_thresholds.csv`
- rejection_thresholds: `analysis\phase34_pilot_thresholds\rejection_thresholds.csv`
- baseline_metric_table: `analysis\phase34_pilot_thresholds\baseline_metric_table.csv`

## Threshold Structure

- acceptance_threshold_count: `14`
- rejection_threshold_count: `9`
- baseline_metric_count: `23`
- acceptance_structure_ready: `true`
- rejection_structure_ready: `true`

## Notes

- No Phase 36 training result was found, as expected for code-smoke scope.
- AT01-AT14 and RT01-RT09 are loaded and staged for a future result check.
- This checker does not authorize training.
