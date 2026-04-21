# Phase 6 Pilot A Results

## Objective

Phase 6 Pilot A tested whether a bounded adaptive scalar on the protected response-split rainfall-conditioning path could preserve favorable-case stability while improving difficult-case behavior.

## Implementation

Pilot A was implemented on the archive-based Phase 3.3 protected response-split code path.

The change was intentionally minimal:

- keep existing protected response-split structure
- keep `residual_alpha`
- add a bounded adaptive scalar multiplier around `1.0`
- initialize the adaptive scalar head near identity

Config switch:

- `rainfall_conditioning.adaptive_alpha_enabled`
- `rainfall_conditioning.adaptive_alpha_range`

Pilot A v1 used:

- `adaptive_alpha_enabled = true`
- `adaptive_alpha_range = 0.25`

## Observations

### Seed42, 5e

Pilot A was neutral to slightly unfavorable on the favorable-case reference setup.

### Seed202, 5e

Pilot A showed a promising early difficult-case signal relative to the static Phase 3.3 control.

### Seed202, 40e

The early difficult-case advantage did not survive to full training.
Control ultimately remained stronger on the main final validation metrics.

## Conclusion

Phase 6 Pilot A v1 is technically successful but not experimentally superior.

The adaptive scalar mechanism is stable and trainable, but the current `adaptive_alpha_range = 0.25` configuration does not produce a better final result than the Phase 3.3 `af025` control.

## Decision

Close Phase 6 Pilot A v1 as a documented negative/neutral result.

Do not expand this exact configuration to more seeds or a broader sweep.

## Recommended Next Stage

The next stage should test a more conservative adaptive-strength follow-up rather than a broader search.

The most justified next step is to reduce the adaptive range and re-check difficult-case behavior before considering any wider expansion.

## Reference configs

- `configs/train_phase6_pilot_a_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt025_5e_seed42.json`
- `configs/train_phase6_pilot_a_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt025_5e_seed202.json`
- `configs/train_phase6_pilot_a_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt025_40e_seed42.json`
- `configs/train_phase6_pilot_a_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt025_40e_seed202.json`
