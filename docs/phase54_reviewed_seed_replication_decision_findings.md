# Phase 54 Reviewed Seed-Replication Decision Findings

## Executive Summary

Phase 54 completed a reviewed, decision-only synthesis of whether the established Phase 52 controlled 128x128, 40-epoch protocol should be replicated with additional seeds. Phase 54 ran no training, created no checkpoint, and produced no new model-performance evidence.

The selected decision is:

```text
selected_decision = phase54_authorize_controlled_128x128_seed_replication
authorized_next_phase = phase55_controlled_128x128_seed_replication
authorized_seeds = [123, 202]
reference_seed = 42
resolution = 128
maximum_epochs_per_seed = 40
no_training_in_phase54 = true
seed_robustness_demonstrated = false
level4_plus_route_supported = true
level5_supported = false
no_swe_pinn = true
no_uncontrolled_expansion = true
```

Phase 52 and Phase 53 provide sufficient evidence to authorize a bounded replication of the fixed Phase 52 protocol with seed123 and seed202. Seed42 remains the reference and must not be retrained under this authorization.

Authorization does not mean that seed robustness has already been demonstrated. Seed robustness may be assessed only after both authorized runs are complete, seed42, seed123, and seed202 are compared directly, and the required reliability, physical-proxy, and warning diagnostics have been reviewed. Even a favorable Phase 55 result would remain Level 4+ proxy-model evidence.

## Evidence Reviewed

Phase 54 reviewed:

- The Phase 54 decision plan.
- The Phase 52 controlled seed42 training summary and findings.
- The Phase 53 no-training diagnostic summary and findings.
- The 48-row matched Phase 52 versus Phase 48 diagnostic comparison.
- The Phase 53 reliability warning levels.
- The Phase 54 candidate-option matrix and risk assessment.
- The structured Phase 54 selected-decision record.

The evidence review passed with no recorded inconsistencies. The reviewed evidence defines a fixed training and diagnostic route suitable for bounded replication while retaining material limitations.

## Phase 52 Training Evidence

Phase 52 completed the controlled seed42 longer run under the established 128x128 route:

```text
seed = 42
resolution = 128
epochs_completed = 40
train_samples = 960
test_samples = 384
best_epoch = 40
test_rmse = 0.005160715272116552
test_mae = 0.002410597107882495
test_wet_dry_iou = 0.9130120601863988
test_rollout_stability = 0.9992842044060429
test_step_rmse_std = 0.0007178322914948391
test_loss = 0.0002713639403471764
```

These retained aggregate metrics improved substantially over the Phase 47 10-epoch seed42 reference. The completed run established a more suitable fixed protocol for replication than the earlier short-horizon baseline.

The Phase 52 result is evidence from one seed only. It does not demonstrate that the same behavior will occur for seed123, seed202, or other seeds.

## Phase 53 Diagnostic Evidence

Phase 53 completed no-training diagnostics on the Phase 52 best checkpoint:

```text
checkpoint_found = true
diagnostics_executed = true
evaluated_scenarios = 48
evaluated_windows = 384
diagnostic_rows = 4,608
matched_comparison_rows = 48
no_training = true
```

All 48 matched scenarios improved in RMSE, MAE, wet/dry IoU, false-dry rate, and false-wet rate relative to the retained Phase 48 reference. Average peak-depth, peak-timing, and summed-depth volume-response proxy behavior also improved, but these diagnostic families retained case-level degradations.

Warning-level counts changed as follows:

| Warning level | Phase 48/49 reference | Phase 52/53 checkpoint |
| --- | ---: | ---: |
| Reliable | 1 | 38 |
| Caution | 12 | 3 |
| High-risk | 35 | 7 |

Thirty-nine warning labels improved, nine were unchanged, and none worsened under the fixed diagnostic rules. Seven high-risk scenarios remained. The warning labels are conservative rule-based screening labels, not calibrated probabilities.

## Candidate Options

| Option | Candidate | Phase 54 disposition |
| --- | --- | --- |
| A | Controlled seed123 and seed202 replication | Selected and authorized for separate Phase 55 |
| B | Seed123-only pilot | Not preferred |
| C | Defer replication and move to 256x256 | Deferred |
| D | Defer training for reporting or manuscript work | Permissible non-training work, but not selected |
| E | Defer expansion because evidence is insufficient | Fail-closed fallback; not selected because evidence review passed |

Option A has the highest direct reproducibility value while changing only the seed. Option B provides only a partial comparison. Option C introduces a confounding resolution change. Option D does not address seed sensitivity. Option E would have been required if the evidence review had failed.

## Selected Decision

Phase 54 selects:

```text
phase54_authorize_controlled_128x128_seed_replication
```

The only authorized next phase is:

```text
phase55_controlled_128x128_seed_replication
```

This authorization is limited to exactly two new training runs, for seed123 and seed202, under the unchanged Phase 52 protocol. Phase 54 itself remains no-training and does not authorize training within Phase 54.

## Why Two-Seed Replication Is Authorized

Phase 52 established a completed, materially improved 40-epoch seed42 result. Phase 53 showed that the improvement extended beyond aggregate metrics to matched reliability, wet/dry, physical-proxy, and warning diagnostics. The model route, data split, sample counts, training basis, evaluation definitions, and diagnostic framework are therefore sufficiently specified for controlled replication.

The principal unresolved question is sensitivity to random seed. Running seed123 and seed202 while freezing all non-seed protocol fields provides a direct three-seed evidence set with limited experimental change. This is scientifically more informative than changing resolution, architecture, loss, or other protocol elements before testing whether the established result recurs.

The authorization is a bounded test of reproducibility and seed sensitivity. It is not a finding of seed robustness.

## Why a Seed123-Only Pilot Is Not Preferred

A seed123-only pilot would reduce immediate compute, but it would produce only a two-seed comparison and require another reviewed decision before seed202 could be run. That staging would delay the predefined three-seed comparison without materially reducing conceptual or implementation risk because the Phase 52 training protocol and Phase 53 diagnostic route are already established.

The bounded two-seed authorization remains limited to two runs and a 40-epoch maximum per run. Resource constraints should be managed through scheduling and explicit stop controls, not by weakening the replication design or substituting unapproved seeds.

## Authorized Phase 55 Scope

Phase 55 must use:

- Seeds 123 and 202 only.
- Resolution 128x128.
- A maximum of 40 epochs per seed.
- The same Phase 52 train/test split.
- 960 train windows.
- 384 test windows.
- The same model architecture.
- The same loss.
- The same optimizer and scheduler basis.
- The same batch-size basis.
- The same rainfall alignment.
- The same downsampling.
- The same wet threshold and metric definitions.
- A separate configuration for each seed.
- A separate, non-overwriting run directory for each seed.
- Locally retained best and final checkpoints for each seed.
- Direct comparison with the Phase 52 seed42 reference.
- Reliability, physical-proxy, and warning diagnostics after training.

Seed42 must remain the fixed reference and must not be retrained as part of the Phase 55 authorization.

Suggested run directories:

```text
runs/phase55_full_downsample128_seed123_40e/
runs/phase55_full_downsample128_seed202_40e/
```

Suggested analysis directory:

```text
analysis/phase55_controlled_128x128_seed_replication/
```

## Required Three-Seed Comparison

Phase 55 must compare seed42, seed123, and seed202 directly under the fixed protocol. The comparison should retain, at minimum:

- Best-epoch and final-epoch metrics.
- Training trajectories and selected best epochs.
- RMSE, MAE, wet/dry IoU, rollout stability, step RMSE variation, and loss.
- Reliability and wet/dry diagnostic distributions.
- Peak-depth, peak-timing, and summed-depth volume-response proxy behavior.
- Warning-level counts and applicable warning transitions.
- Persistent, resolved, and seed-specific failure cases.

Training completion for seed123 or seed202 alone is not sufficient. A robustness or bounded reproducibility assessment must wait until both authorized runs, their artifacts, the seed42 reference, and all required diagnostics are available for review.

Three tested seeds remain a limited evidence set. Any later favorable statement must be restricted to consistency across these three seeds under the tested 128x128, fixed-split, 40-epoch-maximum protocol.

## Post-Training Diagnostic Requirement

Each authorized seed must undergo the retained reliability, physical-proxy, and warning diagnostic evaluation after training. The definitions, thresholds, masks, scenario alignment, wet threshold, and aggregation basis must remain consistent with the Phase 52/53 route.

Required diagnostics are part of the Phase 55 evidence, not optional follow-up work. Phase 55 is incomplete if either seed lacks:

- A valid controlled training result.
- Readable best and final checkpoints.
- Complete metrics and configuration records.
- Reliability diagnostics.
- Physical-proxy diagnostics.
- Warning diagnostics.
- Inclusion in the direct three-seed comparison.

Favorable aggregate metrics must not be used to bypass or replace the diagnostic review.

## Deferred and Prohibited Options

Phase 54 does not authorize:

- Seed sweeps beyond seed123 and seed202.
- Training beyond 40 epochs per seed.
- 256x256 training.
- Tile training.
- Multiscale training.
- Full 500x500 training.
- Hyperparameter sweeps.
- Architecture sweeps.
- New loss redesign.
- Model, loss, configuration, or architecture changes.
- SWE residual implementation.
- PINN implementation.
- Level 5 claims.
- Strict conservation claims.
- Full mass conservation claims.
- Hydrodynamic closure claims.
- Calibrated probability warning labels.
- Production-readiness claims.
- Uncontrolled expansion.

Reporting, visualization, warning-case analysis, and manuscript work may continue as non-training activities, but they do not resolve seed sensitivity and must not be presented as Phase 55 evidence.

## Risk and Stop Boundaries

The principal risks are seed-specific performance degradation, seed-specific diagnostic degradation, protocol drift, incomplete artifacts, output overwrite, resource failure, and premature overclaiming.

An authorized seed run must stop or be classified as failed if:

- The Phase 52 split or the required sample counts cannot be preserved.
- Any non-seed protocol field differs from the fixed Phase 52 basis.
- The model, loss, optimizer or scheduler basis, batch-size basis, rainfall alignment, downsampling, masks, wet threshold, or metric definitions drift.
- The run would exceed 40 epochs.
- The output path would overwrite Phase 52 evidence or the other Phase 55 seed.
- Non-finite loss or required metrics cannot be recovered under the unchanged protocol.
- Checkpoints, logs, metrics, or configuration records are unreadable or incomplete.
- Resource exhaustion or repeated execution failure prevents controlled completion.

A failed seed must not be replaced by another seed. Phase 55 must be classified as incomplete if either seed123 or seed202 lacks valid training and diagnostic evidence. Failure, incompleteness, or unfavorable results must return to a later reviewed decision rather than trigger automatic expansion.

## What Phase 54 Demonstrates

Phase 54 demonstrates that:

- The Phase 52 and Phase 53 evidence passed the reviewed consistency checks.
- Phase 52 established a completed and diagnostically reviewed 128x128 seed42 protocol suitable for bounded replication.
- A controlled replication can be defined by changing only the seed.
- Seed123 and seed202 can be authorized within explicit protocol, compute, artifact, diagnostic, and claim boundaries.
- Seed42 can remain a fixed reference for a direct three-seed comparison.
- The current evidence continues to support only a Level 4+ proxy-model route.
- A reviewed decision process can authorize limited next work without permitting uncontrolled expansion.

## What Phase 54 Does Not Demonstrate

Phase 54 does not demonstrate:

- Any new training result.
- The performance of seed123 or seed202.
- That either authorized run will complete successfully.
- That either authorized seed will match or improve upon seed42.
- Seed robustness or general seed invariance.
- That Phase 55 results are already known.
- Robustness beyond the three specified seeds.
- 256x256, tile, multiscale, or full 500x500 feasibility or performance.
- Hyperparameter, architecture, loss, resolution, or dataset robustness.
- SWE residual behavior or PINN behavior.
- Level 5 support.
- Strict conservation, full mass conservation, or hydrodynamic closure.
- Calibrated probability warning labels.
- Production readiness or operational warning validity.

Authorization is permission for a bounded experiment, not evidence of its outcome.

## Guardrails

- Phase 54 is decision-only and ran no training.
- Do not create or modify model checkpoints under Phase 54.
- Authorize only seed123 and seed202 for Phase 55.
- Keep seed42 as the fixed reference; do not retrain it under this authorization.
- Keep resolution at 128x128.
- Enforce a maximum of 40 epochs per authorized seed.
- Preserve the Phase 52 split, 960 train windows, and 384 test windows.
- Preserve the Phase 52 architecture, loss, optimizer and scheduler basis, batch-size basis, rainfall alignment, downsampling, wet threshold, masks, metrics, and diagnostics.
- Use separate configurations and non-overwriting run directories.
- Retain local best and final checkpoints.
- Require post-training reliability, physical-proxy, and warning diagnostics.
- Review all three seeds before assessing bounded reproducibility.
- Do not claim seed robustness from authorization, training completion, or one additional seed.
- Do not run broader seed, resolution, hyperparameter, architecture, or loss sweeps.
- Do not redesign the model or loss.
- Do not implement or claim SWE residuals or PINN.
- Do not claim Level 5.
- Do not claim strict conservation, full mass conservation, or hydrodynamic closure.
- Do not describe warning labels as calibrated probabilities.
- Do not claim production readiness.
- Do not allow uncontrolled expansion.

## Recommended Next Step

Implement Phase 55 as exactly two separate controlled runs:

```text
phase55_controlled_128x128_seed_replication
```

Run seed123 and seed202 at 128x128 for no more than 40 epochs each under the unchanged Phase 52 protocol. Preserve separate configurations, run directories, logs, metrics, and local best and final checkpoints. After both runs, execute the retained reliability, physical-proxy, and warning diagnostics and produce a direct comparison across seed42, seed123, and seed202.

No stronger reproducibility, resolution, architecture, loss, physics-method, warning, or readiness conclusion should be considered before that evidence is complete and reviewed.

## Final Conclusion

Phase 54 completed the reviewed seed-replication decision and ran no training. The reviewed Phase 52 training evidence and Phase 53 diagnostic evidence are sufficient to authorize a bounded Phase 55 replication of the fixed protocol with seed123 and seed202.

Seed42 remains the reference and must not be retrained under this authorization. Phase 55 is limited to 128x128, a maximum of 40 epochs per authorized seed, the same Phase 52 split with 960 train and 384 test windows, the same model and training basis, separate outputs, retained best and final checkpoints, direct three-seed comparison, and required post-training reliability, physical-proxy, and warning diagnostics.

This authorization does not demonstrate seed robustness and does not predetermine Phase 55 results. Seed robustness may be assessed only after both authorized runs and the complete three-seed diagnostic comparison are reviewed. Even favorable Phase 55 evidence would remain Level 4+ proxy-model evidence and would not support Level 5, SWE/PINN, conservation closure, calibrated probability warnings, production readiness, or uncontrolled expansion.
