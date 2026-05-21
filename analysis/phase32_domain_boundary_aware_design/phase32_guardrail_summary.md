# Phase 32 Guardrail Summary

Phase 32 has a design and guardrail framework.

Current decision: `design_ready_no_training_yet`.

No training is currently justified.

A future seed42 pilot would require all guardrails and baseline comparisons to be fixed before training.

Phase 29 should not be continued directly.

Level 5 remains unsupported.

## Scope Boundary

Level 4+ proxy diagnostics supported; Level 5 remains unsupported.

This formalization does not claim strict conservation, full mass conservation, SWE/PINN, or full hydrodynamic closure.

## Guardrail Groups

- `boundary_ring`
- `dry_threshold`
- `high_impervious_valid`
- `level_boundary`
- `manhole_nonzero_valid`
- `standard`
- `valid_domain`

## Output Counts

- Guardrail metrics: `20`
- Stop/go criteria: `12`

## Stop/Go Position

The project should remain design/diagnostic-only until a seed42 pilot objective, fixed target region, baseline comparisons, and acceptance/rejection thresholds are all documented before training.
