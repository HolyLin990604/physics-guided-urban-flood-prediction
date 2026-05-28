# Phase 39 Failed Pilot Trade-Off Diagnosis

This is a diagnostic-only Level 4+ proxy summary. It does not train, sweep, change thresholds, modify losses/configs/model architecture, or claim strict conservation, full mass conservation, SWE/PINN behavior, hydrodynamic closure, or Level 5 support.

## Decision

- final_decision: `seed42_pilot_rejected`
- phase39_decision: `tradeoff_diagnosis_completed_with_missing_optional_inputs`
- failed_acceptance_count: `8`
- triggered_rejection_count: `3`

## Key Diagnosis

- RT01 indicates a Phase29-like trade-off pattern.
- The current manhole_nonzero_false_dry_guardrail did not pass broader Level 4+ guardrails.
- The result should not be expanded to seed123/seed202 or rescued by sweep/post-hoc edits.
- Next recommended step: failed-pilot diagnosis / design review, not training.

## Failed Acceptance Components

- `AT02` `valid_domain_masked/rmse/valid_domain`: observed `0.0482901961137` vs threshold `0.0470043492351`. Valid-domain RMSE exceeded the Phase 27 plus tolerance guardrail, indicating broader depth-error degradation.
- `AT03` `valid_domain_masked/mae/valid_domain`: observed `0.0191286913686` vs threshold `0.0187366452965`. Valid-domain MAE exceeded the Phase 27 plus tolerance guardrail, so aggregate valid-cell error worsened.
- `AT04` `valid_domain_masked/false_dry_rate/valid_domain`: observed `0.0718682210394` vs threshold `0.068917464101`. Valid-domain false-dry rate exceeded the Phase 27 guardrail, repeating the dry-miss concern outside the target-only view.
- `AT06` `guardrail_masked/false_wet_rate/high_impervious_valid`: observed `0.0231264618198` vs threshold `0.0227046722562`. High-impervious valid false-wet rate exceeded its regional tolerance, indicating the pilot introduced wet overprediction in a guardrail region.
- `AT07` `guardrail_masked/false_dry_rate/boundary_ring`: observed `0.0920545695699` vs threshold `0.087764984526`. Boundary-ring false-dry rate exceeded its tolerance, consistent with a boundary-sensitive trade-off rather than a clean target improvement.
- `AT08` `standard/rmse/all_evaluated_cells`: observed `0.0445683014236` vs threshold `0.0432286009702`. Standard RMSE failed the global quality guardrail.
- `AT09` `standard/mae/all_evaluated_cells`: observed `0.0179593140063` vs threshold `0.0176304670561`. Standard MAE failed the global quality guardrail.
- `AT10` `standard/wet_dry_iou/all_evaluated_cells`: observed `0.806874058749` vs threshold `0.807801373632`. Standard wet/dry IoU fell below the required floor, indicating wet/dry classification quality was not maintained.

## Triggered Rejection Rules

- `RT01` `phase29_tradeoff_pattern`: The result matches the Phase 29-like pattern: valid-domain volume-bias proxy improves while multiple error metrics worsen versus Phase 27.
- `RT05` `standard_rmse_or_mae_worsens_beyond_tolerance`: At least one standard global error metric exceeded the hard rejection tolerance, so the pilot cannot be treated as a localized-only change.
- `RT07` `valid_domain_error_worsens_beyond_acceptance_tolerance`: Valid-domain RMSE or MAE exceeded the acceptance tolerance, blocking expansion despite target-region improvement.

## Missing Optional Inputs

- Per-batch/scenario Phase25/Phase27/Phase29 baselines are unavailable; scenario summary is Phase38-only.
