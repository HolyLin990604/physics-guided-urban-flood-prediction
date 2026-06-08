# Phase 51 Reviewed Expansion Decision

Phase 51 is decision synthesis only. It performs no training and creates no model checkpoint or new performance result.

## Selected Decision

`phase51_authorize_128x128_seed42_longer_run`

- Authorized next phase: `phase52_controlled_128x128_seed42_longer_run_baseline`
- No training in Phase 51: `true`
- Level 4+ route supported: `true`
- Level 5 supported: `false`
- No SWE/PINN: `true`
- No uncontrolled expansion: `true`

## Why Option A Is Authorized

Phase 47 is the only route with completed training evidence: one controlled 128x128 seed42 10-epoch pilot. A bounded longer seed42 run changes only the training horizon and directly tests whether the established route improves, plateaus, overfits, or degrades. It is lower risk than changing seed, resolution, model, loss, or architecture.

Authorization applies only to a separate Phase 52 controlled baseline, recommended at 40 epochs. Phase 51 does not run seed42.

## Why Options B and C Are Deferred

Seed123 and seed202 are deferred because replicating an unreviewed short-horizon protocol would multiply compute before the baseline duration is established. The 256x256 pilot is deferred because Phase 46 proved data-path feasibility, not training stability, and a resolution change would confound the training-horizon review.

## Why Option D Remains Useful

Warning-framework case reporting and manuscript development remain valid low-risk work. They directly use Phase 48/49 diagnostics, but they are not the next training step because they do not resolve longer-run baseline behavior. Warning labels must remain conservative screening labels, not calibrated probabilities.

## Deferred Options

- `phase51_authorize_128x128_seed_replication`
- `phase51_authorize_256x256_pilot`
- `phase51_defer_training_for_case_reporting_as_next_training_step`
- `tile_training`
- `multiscale_training`
- `full_500x500_training`
- `hyperparameter_or_architecture_sweeps`
- `new_loss_design`
- `swe_residual_implementation`
- `pinn_implementation`

## Guardrails

- Do not train in Phase 51.
- Do not run seed42, seed123, or seed202 in Phase 51.
- Do not run 256x256, tile, multiscale, or full 500x500 training.
- Do not run sweeps or modify model, loss, config, or architecture.
- Do not implement SWE residuals or PINN components.
- Do not claim Level 5, strict conservation, full mass conservation, or hydrodynamic closure.
- Do not claim calibrated probability warning labels or production readiness.
- Do not authorize uncontrolled training expansion.
- Require separate outputs, bounded resources, checkpoint retention, stop criteria, and direct Phase 47 comparison in Phase 52.

## Next Phase

The next phase should be **Phase 52 controlled 128x128 seed42 longer-run baseline**, with a recommended 40-epoch cap and unchanged Level 4+ claim boundary.
