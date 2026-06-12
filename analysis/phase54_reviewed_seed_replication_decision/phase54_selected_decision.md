# Phase 54 Reviewed Seed-Replication Decision

Phase 54 is decision synthesis only. It performs no training, creates no
checkpoint, and generates no new model-performance evidence.

## Evidence Reviewed

- Phase 52 completed seed42 at 128x128 for 40 epochs using 960 train and 384 test windows.
- The Phase 52 best epoch was 40 with test RMSE `0.005160715272116552`.
- Phase 53 executed no-training diagnostics over 48 scenarios, 384 windows, and 4,608 diagnostic rows.
- The matched Phase 52-versus-Phase 48 comparison contains 48 scenarios.
- Warning counts improved from reliable/caution/high-risk = `1/12/35` to `38/3/7`.
- Seven high-risk scenarios and case-level peak, timing, and volume-proxy degradations remain.

## Candidate Options

- **A:** Authorize controlled seed123 and seed202 replication.
- **B:** Authorize seed123 only as a pilot.
- **C:** Defer replication and authorize 256x256.
- **D:** Defer training for reporting or manuscript work.
- **E:** Defer all expansion because evidence is insufficient.

## Selected Decision

`phase54_authorize_controlled_128x128_seed_replication`

- Authorized next phase: `phase55_controlled_128x128_seed_replication`
- Authorized seeds: `[123, 202]`
- Reference seed: `42`
- No training in Phase 54: `true`
- Seed robustness demonstrated: `false`
- Level 4+ route supported: `true`
- Level 5 supported: `false`

## Why Bounded Two-Seed Replication Is Authorized

Phase 52 materially improved all retained aggregate metrics under a completed
and controlled 40-epoch seed42 protocol. Phase 53 showed that the improvement
extends across matched reliability, wet/dry, physical-proxy, and warning
diagnostics. The protocol and diagnostic basis are therefore sufficiently
defined to test the main unresolved limitation: sensitivity to training seed.

Authorizing exactly seed123 and seed202 changes only the seed and creates a
direct, bounded three-seed comparison. Authorization does not demonstrate seed
robustness; that conclusion remains false until both runs and all required
diagnostics are complete and reviewed.

## Why a Seed123-Only Pilot Is Not Preferred

A seed123-only pilot lowers immediate compute but yields only a partial
two-seed comparison and adds another decision cycle before seed202. Because the
Phase 52 protocol and Phase 53 diagnostics are already established, the extra
staging does not materially reduce conceptual risk. Resource constraints must
be managed inside the two-run cap rather than by weakening the replication
design.

## Why 256x256 Remains Deferred

Moving to 256x256 would change resolution and resource behavior before seed
sensitivity at 128x128 is understood. That would confound attribution and would
not answer whether the favorable Phase 52 result is reproducible. Resolution
expansion requires a later reviewed decision after Phase 55 evidence is complete.

## Authorized Phase 55 Protocol

- Train exactly seed123 and seed202; seed42 remains reference only.
- Use 128x128 resolution and a maximum of 40 epochs per seed.
- Preserve the Phase 52 scenario split, 960 train windows, and 384 test windows.
- Preserve the model architecture, loss, optimizer and scheduler basis, batch-size basis, rainfall alignment, downsampling, wet threshold, and metrics.
- Use a separate config and run directory for each seed.
- Retain best and final checkpoints locally.
- Compare seed42, seed123, and seed202 directly.
- Run reliability, physical-proxy, and warning diagnostics after training.

Suggested run directories:

```text
runs/phase55_full_downsample128_seed123_40e/
runs/phase55_full_downsample128_seed202_40e/
```

Suggested analysis directory:

```text
analysis/phase55_controlled_128x128_seed_replication/
```

## Stop and Failure Boundaries

- Stop a run if the fixed split, sample counts, model, loss, optimizer/scheduler basis, masks, wet threshold, metrics, or other non-seed protocol fields drift from Phase 52.
- Stop rather than overwrite Phase 52 or another Phase 55 seed directory.
- Do not exceed 40 epochs per seed.
- Classify non-finite required metrics, unreadable checkpoints, resource exhaustion, or repeated controlled-execution failure explicitly.
- Do not replace a failed authorized seed with another seed.
- Treat Phase 55 as incomplete if either authorized seed lacks valid training artifacts or required diagnostics.
- Do not make a seed-reproducibility conclusion until all three seeds are reviewed.

## Deferred Paths

- `phase54_authorize_single_seed123_pilot`
- `phase54_defer_replication_for_256x256`
- `phase54_defer_training_for_reporting`
- `phase54_defer_expansion_insufficient_evidence`
- `256x256_training`
- `tile_training`
- `multiscale_training`
- `full_500x500_training`
- `seed_sweep_beyond_seed123_and_seed202`
- `hyperparameter_sweep`
- `architecture_sweep`
- `loss_redesign`
- `training_beyond_40_epochs_per_seed`
- `swe_residual_implementation`
- `pinn_implementation`

Reporting and manuscript work may continue as non-training activity, but it
does not resolve seed sensitivity.

## Claim Guardrails

- Do not claim seed robustness from Phase 54 authorization or one additional run.
- Limit any later reproducibility statement to the tested three seeds and fixed 128x128 protocol.
- Do not claim Level 5, SWE/PINN behavior, strict conservation, full mass conservation, or hydrodynamic closure.
- Warning labels remain rule-based diagnostics, not calibrated probabilities.
- Do not claim production readiness.
- Do not authorize 256x256, tile, multiscale, full 500x500, sweep, redesign, or other uncontrolled expansion.

## Next Action

Implement Phase 55 as exactly two separate controlled 128x128 runs for seed123 and seed202, each capped at 40 epochs under the unchanged Phase 52 protocol, followed by direct three-seed reliability, physical-proxy, and warning-diagnostic comparison.
