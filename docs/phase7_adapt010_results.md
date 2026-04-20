# Phase 7 Adapt010 Results

## Objective

Phase 7 tested whether the adaptive scalar idea becomes more viable when the adaptive strength is reduced from `0.25` to `0.10`.

This stage was intentionally conservative:

- keep the protected response-split architecture unchanged
- keep `residual_alpha`
- keep the adaptive mechanism optional
- change only `adaptive_alpha_range`

## Context

Phase 6 Pilot A `adapt025` established that the adaptive scalar mechanism was stable and trainable, but it did not remain superior to the static Phase 3.3 `af025` control after full training.

Therefore, the justified follow-up was not a broader sweep. It was a narrower adaptive-strength check.

## Phase 7 Candidate

Phase 7 uses:

- `temporal_gate_residual_response_split_protected`
- `hidden_channels = 16`
- `residual_alpha = 0.10`
- `conditioned_fraction = 0.25`
- `active_fraction_within_response = 0.25`
- `adaptive_alpha_enabled = true`
- `adaptive_alpha_range = 0.10`

This candidate is referred to as `adapt010`.

## Results

### Difficult-case decisive check: seed202 / 40e

Final validation metrics:

| config | val_rmse | val_mae | val_wet_dry_iou | val_rollout_stability | val_loss |
|---|---:|---:|---:|---:|---:|
| Phase 3.3 `af025` control | 0.037756 | 0.016027 | 0.795961 | 0.992497 | 0.013834 |
| Phase 6 `adapt025` | 0.038403 | 0.016333 | 0.776135 | 0.992273 | 0.014162 |
| Phase 7 `adapt010` | 0.036812 | 0.015720 | 0.807813 | 0.992127 | 0.013404 |

Interpretation:

- `adapt010` survives to `40e` better than `adapt025`
- `adapt010` beats the static `af025` control on the main final metrics except for a small rollout-stability decrease
- the adaptive-strength direction remains viable when kept conservative

### Favorable-case guardrail check: seed42 / 5e

Final validation metrics:

| config | val_rmse | val_mae | val_wet_dry_iou | val_rollout_stability | val_loss |
|---|---:|---:|---:|---:|---:|
| Phase 3.3 `af025` control | 0.118634 | 0.042448 | 0.235387 | 0.987600 | 0.043159 |
| Phase 7 `adapt010` | 0.117590 | 0.041802 | 0.256863 | 0.987770 | 0.042368 |

Interpretation:

- `adapt010` remains acceptable on the favorable-case reference setup
- the seed42 guardrail check does not show the kind of early regression that would block the candidate

## Conclusion

The current Phase 7 conclusion is:

- Phase 6 `adapt025` was stable but not ultimately superior
- Phase 7 `adapt010` is a conservative follow-up that improved the difficult-case result
- `adapt010` passed the decisive `seed202 / 40e` check
- `adapt010` also passed the `seed42 / 5e` favorable-case guardrail check
- therefore `adapt010` should now be treated as the current adaptive candidate

## Reference configs

- `configs/train_phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_5e_seed202.json`
- `configs/train_phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202.json`
- `configs/train_phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_5e_seed42.json`
