# Phase 54 Reviewed Seed-Replication Decision Plan

## 1. Executive Summary

Phase 54 is a no-training, reviewed decision phase that determines whether the established Phase 52 controlled 128x128, 40-epoch protocol should be replicated with seed123 and seed202.

Phase 52 substantially improved aggregate prediction metrics over the Phase 47 10-epoch reference. Phase 53 then showed that the Phase 52 checkpoint also improved retained reliability, physical-proxy, and conservative warning diagnostics. These results establish a suitable protocol for bounded replication, but they do not demonstrate seed robustness because only seed42 has been trained under the 40-epoch protocol.

The recommended decision is:

```text
selected_decision = phase54_authorize_controlled_128x128_seed_replication
authorized_next_phase = phase55_controlled_128x128_seed_replication
no_training_in_phase54 = true
```

This decision would authorize only a separate Phase 55 controlled replication using seed123 and seed202. Each run must retain the Phase 52 resolution, 40-epoch maximum, train/test split, sample counts, model, loss, optimizer basis, scheduler basis, wet threshold, and diagnostic definitions. Seed42 remains the fixed reference.

Authorization does not imply that seed robustness has already been demonstrated. Phase 55 results and post-training diagnostics must be reviewed across seed42, seed123, and seed202 before any stronger reproducibility, resolution, architecture, loss, physics-method, warning, or readiness conclusion is considered.

## 2. Background from Phase 47-53

Phases 47-53 established and reviewed the current controlled route:

| Phase | Evidence role | Conservative result |
| --- | --- | --- |
| 47 | Controlled 128x128 seed42 baseline | Completed a 10-epoch run using 960 train samples and 384 test samples. |
| 48 | Reliability and physical-proxy diagnostics | Evaluated 48 scenarios and 384 windows without retraining. |
| 49 | Warning-framework extension | Assigned conservative diagnostic warning labels: 1 reliable, 12 caution, and 35 high-risk. |
| 50 | Evidence consolidation | Consolidated the Level 4+ proxy-modeling evidence and claim boundaries. |
| 51 | Reviewed expansion decision | Authorized only a separate 128x128 seed42 longer-run phase. |
| 52 | Controlled seed42 longer run | Completed the fixed 128x128 seed42 protocol through 40 epochs and substantially improved aggregate metrics. |
| 53 | No-training Phase 52 diagnostic review | Confirmed broad reliability and warning-diagnostic improvement and recommended a later reviewed seed-replication decision. |

The Phase 52 result is:

```text
seed = 42
resolution = 128
epochs = 40
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

Phase 53 completed the following diagnostic scope:

```text
checkpoint_found = true
diagnostics_executed = true
evaluated_scenarios = 48
evaluated_windows = 384
diagnostic_rows = 4608
matched_comparison_rows = 48
no_training = true
```

The warning-level comparison was:

| Warning level | Phase 48/49 reference | Phase 52/53 checkpoint |
| --- | ---: | ---: |
| Reliable | 1 | 38 |
| Caution | 12 | 3 |
| High-risk | 35 | 7 |

Phase 53 found that all 48 matched scenarios improved in RMSE, MAE, wet/dry IoU, false-dry rate, and false-wet rate. Average peak-depth, peak-timing, and volume-response proxy behavior also improved, while retaining case-level degradations and seven high-risk scenarios.

The evidence therefore supports reviewing a bounded replication of the established protocol. It does not establish seed robustness, Level 5 support, SWE/PINN behavior, conservation closure, calibrated warning probabilities, or production readiness.

## 3. Purpose of Seed-Replication Review

The purpose of Phase 54 is to decide whether the Phase 52 protocol is sufficiently established to justify controlled replication with two additional seeds.

Phase 54 should answer:

- Is the Phase 52/53 evidence sufficient to authorize seed123 and seed202 under the same controlled protocol?
- Would a two-seed replication add meaningful evidence about reproducibility and seed sensitivity?
- Is a single seed123 pilot preferable to authorizing both seeds?
- Should replication be deferred in favor of 256x256, reporting work, or no further training?
- What boundaries must govern a separate Phase 55 implementation and training phase?

Phase 54 is an authorization gate. It must not run training, create checkpoints, or generate new model-performance evidence.

## 4. Evidence Used for Decision

The Phase 54 decision should use the reviewed Phase 47-53 evidence.

Primary evidence includes:

- Phase 47 established the original controlled 128x128 seed42 route.
- Phases 48 and 49 established the retained reliability, physical-proxy, and warning definitions.
- Phase 51 selected longer training as the prerequisite to later replication.
- Phase 52 completed the resulting 40-epoch seed42 protocol and improved all six retained aggregate test metrics over Phase 47.
- Phase 53 confirmed broad diagnostic improvement under the retained comparison basis.
- Phase 53 explicitly identified a reviewed seed-replication decision as the appropriate next step.

The decision should interpret this evidence conservatively:

- The 128x128, 40-epoch protocol has completed training and diagnostic review for seed42.
- The protocol is sufficiently defined for direct controlled replication.
- Seed123 and seed202 have not been trained under this protocol.
- A single successful seed42 result cannot establish seed robustness.
- The seven remaining high-risk cases and case-level proxy degradations remain relevant limitations.
- Warning labels remain rule-based diagnostic screening labels, not calibrated probabilities.
- No evidence supports changing resolution, data route, model, loss, optimizer basis, scheduler basis, architecture, wet threshold, or diagnostic definitions during replication.

## 5. Candidate Options

### Option A: Authorize Seed123 and Seed202 Replication

Authorize a separate Phase 55 to run seed123 and seed202 at 128x128 for a maximum of 40 epochs per seed under the fixed Phase 52 protocol.

Decision candidate:

```text
phase54_authorize_controlled_128x128_seed_replication
```

This is the recommended option. It directly tests whether the Phase 52 result is reproducible across two additional controlled initializations while minimizing experimental changes.

### Option B: Authorize Only a Seed123 Pilot

Authorize a separate phase for seed123 only, followed by another decision before seed202.

Decision candidate:

```text
phase54_authorize_single_seed123_pilot
```

This option reduces immediate compute but weakens the replication design and adds another decision boundary before a three-seed comparison can be made. Because the protocol and diagnostics are already established, the additional staging is not necessary unless resource constraints prevent the bounded two-seed plan.

### Option C: Defer Replication and Move to 256x256

Defer seed replication and authorize or prepare a 256x256 route.

Decision candidate:

```text
phase54_defer_replication_for_256x256
```

This option is not recommended. It changes resolution before seed sensitivity at 128x128 is understood, increases compute and implementation risk, and makes attribution of performance changes less controlled.

### Option D: Defer Training for Reporting or Manuscript Work

Run no new training and continue reporting, visualization, warning-case analysis, or manuscript development.

Decision candidate:

```text
phase54_defer_training_for_reporting
```

This is a valid low-compute path, but it does not resolve the current seed-robustness gap.

### Option E: Defer Expansion Because Evidence Is Insufficient

Authorize no training because the reviewed evidence is incomplete, inconsistent, or insufficient to define a controlled replication.

Decision candidate:

```text
phase54_defer_expansion_insufficient_evidence
```

This option should be selected only if Phase 52/53 artifacts fail consistency or readiness review. The current reviewed findings do not indicate such a failure.

## 6. Scientific Value of Seed Replication

Controlled seed replication addresses the main unresolved question left by Phases 52 and 53: whether the favorable result is reproducible or materially sensitive to random initialization and training stochasticity.

A three-seed evidence set can:

- Test whether the Phase 52 aggregate improvements recur under seed123 and seed202.
- Identify dispersion in best epoch, RMSE, MAE, wet/dry IoU, rollout stability, step RMSE variation, and loss.
- Test whether reliability and warning improvements are consistent across seeds.
- Reveal whether the seven retained high-risk cases are persistent, seed-dependent, or replaced by different failure cases.
- Distinguish a reproducible protocol from an unusually favorable seed42 outcome.
- Provide a stronger basis for later decisions about resolution or method expansion.

Three seeds remain a limited replication set. Even favorable Phase 55 results should support only a bounded statement about consistency across the three tested seeds, not universal robustness or operational reliability.

## 7. Compute and Implementation Risk

Option A requires two controlled training runs and two complete post-training diagnostic evaluations. Its compute cost is approximately twice one Phase 52 training-and-diagnostic route, subject to the same environment and runtime conditions.

The main risks are:

| Risk | Required control |
| --- | --- |
| Training or diagnostics differ from Phase 52 for reasons other than seed | Freeze all non-seed protocol fields and record a configuration comparison before execution. |
| A run exceeds the authorized budget | Enforce a maximum of 40 epochs per seed with no automatic extension. |
| Outputs overwrite prior evidence or each other | Use separate Phase 55 run directories and a separate analysis directory. |
| One seed fails while the other proceeds | Preserve all completed artifacts, classify the failed seed, and do not silently substitute another seed. |
| Checkpoint or metric corruption prevents comparison | Require finite metrics, readable checkpoints, complete logs, and explicit artifact validation. |
| Diagnostics are skipped after training | Treat missing required diagnostics as an incomplete Phase 55 evidence set. |
| Parallel execution creates avoidable resource contention | Use resource-aware scheduling; concurrency is optional and must not change the protocol. |

The controlled two-seed design has moderate aggregate compute cost but low conceptual implementation risk because it reuses an established route. It is lower risk than changing resolution, architecture, loss, or physics method.

## 8. Claim-Boundary Risk

The main interpretation risk is treating authorization or favorable replication results as evidence for claims outside the tested scope.

Phase 54 and any authorized Phase 55 must preserve these boundaries:

- Authorization is not evidence that seed robustness has already been demonstrated.
- Completion of seed123 and seed202 is not sufficient by itself; all three seeds and their diagnostics must be reviewed.
- Three-seed consistency does not establish robustness across arbitrary seeds, datasets, resolutions, architectures, or event distributions.
- Aggregate accuracy does not establish strict conservation, full mass conservation, hydrodynamic closure, or governing-equation satisfaction.
- Physical-proxy diagnostics are not SWE residuals and do not establish PINN behavior.
- Warning labels are not calibrated probabilities.
- No result supports Level 5 or production-readiness claims.

Any later robustness language must be limited to the tested 128x128, 40-epoch, fixed-split, fixed-model protocol and the three specified seeds.

## 9. Recommended Decision

Phase 54 should select:

```text
selected_decision = phase54_authorize_controlled_128x128_seed_replication
authorized_next_phase = phase55_controlled_128x128_seed_replication
```

The recommendation is based on the following:

- Phase 52 established a materially improved 40-epoch seed42 result.
- Phase 53 showed that improvement extended to reliability and conservative warning diagnostics.
- The training and diagnostic protocol is sufficiently defined for direct replication.
- Seed robustness is now the most important unresolved limitation of the established route.
- Running seed123 and seed202 changes only the seed and provides a direct three-seed comparison.
- A single-seed pilot would delay the complete comparison without resolving the robustness question.
- Moving to 256x256 or changing methods before replication would introduce avoidable confounding.

This recommendation authorizes a separate Phase 55 only. No Phase 54 training is permitted.

## 10. Authorized Phase 55 Scope

The only authorized next phase should be:

```text
phase55_controlled_128x128_seed_replication
```

Phase 55 may train exactly:

```text
seed = 123
resolution = 128
epochs_maximum = 40

seed = 202
resolution = 128
epochs_maximum = 40
```

Phase 55 must preserve:

- The same Phase 52 train/test split.
- `train_samples = 960`.
- `test_samples = 384`.
- The same model and architecture.
- The same loss.
- The same optimizer basis.
- The same scheduler basis.
- The same sample construction and data route.
- The same masks and wet threshold.
- The same metric and diagnostic definitions.
- The same checkpoint-selection basis.
- Separate, non-overwriting outputs for each seed.
- Direct comparison against the Phase 52 seed42 reference.
- Post-training reliability, physical-proxy, and warning diagnostics for each seed.

Suggested run directories:

```text
runs/phase55_full_downsample128_seed123_40e/
runs/phase55_full_downsample128_seed202_40e/
```

Suggested analysis directory:

```text
analysis/phase55_controlled_128x128_seed_replication/
```

The Phase 55 review set must include seed42, seed123, and seed202. It should compare per-seed metrics, best and final epochs, training trajectories, diagnostic distributions, warning counts, warning transitions where applicable, and persistent or seed-specific failure cases.

## 11. Deferred Options

Phase 54 should defer or prohibit:

- 256x256 training.
- Tile training.
- Multiscale training.
- Full 500x500 training.
- Hyperparameter sweeps.
- Architecture sweeps.
- Seed sweeps beyond seed123 and seed202.
- Resolution sweeps.
- New loss redesign.
- Model, loss, configuration, or architecture changes.
- Training beyond 40 epochs per seed.
- SWE residuals.
- PINN implementation.
- Level 5 claims.
- Strict conservation claims.
- Full mass conservation claims.
- Hydrodynamic closure claims.
- Calibrated probability warning claims.
- Production-readiness claims.
- Any uncontrolled expansion.

Reporting and manuscript work may continue as non-training activity, but it must not be used to imply that the seed-replication question has been resolved.

## 12. Stop and Failure Boundaries

Phase 54 must stop without authorization if:

- Required Phase 52 or Phase 53 evidence is missing or internally inconsistent.
- The fixed Phase 52 protocol cannot be identified precisely enough for controlled replication.
- The selected decision cannot preserve the no-training Phase 54 boundary.

If Phase 55 is authorized, an individual seed run must stop or be classified as failed when:

- A non-finite loss or required metric occurs and cannot be recovered under the unchanged protocol.
- The run cannot preserve the fixed train/test split or required sample counts.
- The model, loss, optimizer basis, scheduler basis, masks, wet threshold, or diagnostic definitions differ from Phase 52.
- The output path would overwrite Phase 52 or another Phase 55 seed.
- Resource exhaustion or repeated execution failure prevents controlled completion.
- The 40-epoch cap would be exceeded.

Phase 55 as a whole is incomplete rather than successful if:

- Either seed123 or seed202 lacks a valid training result.
- Required checkpoints, metrics, or configuration records are missing.
- Post-training reliability, physical-proxy, or warning diagnostics are missing for either seed.
- Direct comparison across all three seeds cannot be completed.

A failed or incomplete seed must not be replaced with an unapproved seed. Failure must be documented and returned to a later reviewed decision.

## 13. Guardrails

- Phase 54 is decision-only.
- Do not run training in Phase 54.
- Do not create or modify model checkpoints in Phase 54.
- Authorize only seed123 and seed202.
- Keep seed42 as the reference.
- Keep resolution at 128x128.
- Enforce a maximum of 40 epochs per authorized seed.
- Preserve the Phase 52 train/test split and sample counts.
- Preserve the model, architecture, loss, optimizer basis, scheduler basis, wet threshold, and diagnostic definitions.
- Use separate output directories for each seed.
- Require post-training diagnostics for each seed.
- Review all three seeds before making a stronger conclusion.
- Do not claim seed robustness from authorization, run completion, or one additional successful seed.
- Do not run 256x256, tile, multiscale, or full 500x500 training.
- Do not run hyperparameter, architecture, loss, resolution, or uncontrolled seed sweeps.
- Do not redesign the loss or change model/config architecture.
- Do not train beyond 40 epochs per seed.
- Do not implement SWE residuals or PINN.
- Do not claim Level 5.
- Do not claim strict conservation, full mass conservation, or hydrodynamic closure.
- Do not describe warning labels as calibrated probabilities.
- Do not claim production readiness.
- Do not overwrite Phase 47-53 evidence.
- Do not authorize further expansion from Phase 54 without completed Phase 55 review.

## 14. Success Criteria

Phase 54 is successful if:

- It completes a documented review of Options A-E.
- It records whether the Phase 52/53 evidence is sufficient for bounded replication.
- It selects `phase54_authorize_controlled_128x128_seed_replication`, unless a documented evidence inconsistency requires deferral.
- It authorizes only `phase55_controlled_128x128_seed_replication`.
- It defines seed123 and seed202 as the only authorized training seeds.
- It preserves seed42 as the reference.
- It preserves the fixed Phase 52 protocol and 40-epoch maximum.
- It defines separate run and analysis directories.
- It requires post-training reliability, physical-proxy, and warning diagnostics.
- It defines explicit stop, failure, and incompleteness conditions.
- It produces no training run, checkpoint, or new performance metric.
- It preserves all scientific and operational claim boundaries.

Phase 55 should be considered complete only when both authorized seeds have valid controlled results and required diagnostics. A later review should then determine:

- Whether aggregate performance is consistent across the three seeds.
- Whether diagnostic and warning behavior is consistent across the three seeds.
- Which limitations are persistent versus seed-specific.
- Whether the evidence supports a bounded three-seed reproducibility statement.
- Whether any later expansion should be considered.

Phase 55 completion alone must not automatically authorize 256x256, architecture, loss, physics-method, or production expansion.

## 15. Final Conclusion

Phase 53 provides sufficient evidence to consider a bounded two-seed replication of the Phase 52 protocol. Phase 54 should therefore make the following no-training decision:

```text
selected_decision = phase54_authorize_controlled_128x128_seed_replication
authorized_next_phase = phase55_controlled_128x128_seed_replication
no_training_in_phase54 = true
```

The authorization should cover only seed123 and seed202 at 128x128 for a maximum of 40 epochs per seed under the unchanged Phase 52 protocol. Seed42 remains the reference, and each new seed requires complete post-training reliability, physical-proxy, and warning diagnostics.

This decision tests reproducibility and seed sensitivity; it does not presume seed robustness. All three seeds must be reviewed before any stronger conclusion is made. Resolution, architecture, loss, physics-method, and uncontrolled training expansion must remain deferred, along with Level 5, SWE/PINN, conservation, hydrodynamic-closure, calibrated-probability warning, and production-readiness claims.
