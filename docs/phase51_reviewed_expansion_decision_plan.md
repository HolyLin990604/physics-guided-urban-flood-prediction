# Phase 51 Reviewed Expansion Decision Plan

## 1. Executive Summary

Phase 51 plans a decision-only review of the next controlled expansion path after the Phase 43-50 UrbanFlood24 full-dataset Level 4+ evidence chain, framework consolidation, and research-grade visualization support.

Phase 51 does not run training. It reviews the available evidence, compares bounded expansion options, records risks and deferrals, and determines whether one follow-up training route may be authorized in a separate controlled phase.

The expected conservative selected decision is:

```text
phase51_authorize_128x128_seed42_longer_run
```

This decision authorizes only the preparation of a separate controlled follow-up phase for a 128x128 seed42 longer run, such as 40 epochs. It does not authorize training within Phase 51, seed replication, 256x256 training, tile or multiscale training, full 500x500 training, sweeps, model or loss redesign, SWE residuals, PINN implementation, or expanded physics claims.

The current claim boundary remains unchanged:

- The UrbanFlood24 full-dataset Level 4+ proxy modeling route is supported.
- Level 5 is not supported.
- SWE/PINN is not supported.
- Strict conservation, full mass conservation, and hydrodynamic closure are not supported.
- Warning labels are conservative diagnostic screening labels, not calibrated probabilities.
- Production readiness is not claimed.

## 2. Background from Phase 43-50

Phases 43-50 established a staged full-dataset evidence chain:

| Phase | Evidence role | Conservative result |
| --- | --- | --- |
| 43-44 | Full dataset inspection and Level 4+ route replanning | UrbanFlood24 supports a controlled Level 4+ proxy modeling route; Level 5, SWE, and PINN claims remain unsupported. |
| 45 | Full dataset indexing | 168 scenarios were indexed, including 120 train scenarios and 48 test scenarios. |
| 46 | Dataloader, downsample, tile, batch, and memory feasibility | 128x128 and 256x256 downsample checks, tile checks, batch smoke, and memory-safety checks passed without training. |
| 47 | Controlled baseline training | One 128x128 seed42 10-epoch baseline completed with 960 train samples and 384 test samples. |
| 48 | Reliability and physical proxy diagnostics | 48 scenarios and 384 windows were evaluated without retraining. |
| 49 | Warning framework extension | Diagnostic results were mapped to conservative warning labels and review actions. |
| 50 | Framework consolidation and paper-ready evidence synthesis | The evidence chain, claim boundary, contribution language, and research-grade figures were consolidated. |

Phase 47 provides the current training evidence:

```text
seed = 42
resolution = 128
epochs = 10
train_samples = 960
test_samples = 384
best_test_rmse = 0.01109213042097205
test_mae = 0.00525291082279485
test_wet_dry_iou = 0.8255524213115374
test_rollout_stability = 0.998722607580324
```

Phase 48 and Phase 49 provide the current diagnostic and warning evidence:

```text
evaluated_scenarios = 48
evaluated_windows = 384
mean_rmse = 0.012037189189155709
mean_mae = 0.005252910632811514
mean_wet_dry_iou = 0.863043953275997
warning_level_counts = reliable 1, caution 12, high-risk 35
```

The large high-risk count reflects conservative screening sensitivity and is not proof of poor overall model skill. The warning labels are not probabilities and do not establish operational forecast calibration.

Phase 50 made the evidence suitable for README-facing and manuscript-facing reporting. It did not create evidence for longer training, seed robustness, higher-resolution training, physics closure, or production use. Phase 51 therefore serves as a reviewed gate before any further training expansion.

## 3. Purpose of Reviewed Expansion Decision

The purpose of Phase 51 is to decide which single controlled expansion path, if any, should be prepared next.

Phase 51 should answer:

- Is the current evidence sufficient to authorize a longer run using the existing 128x128 seed42 route?
- Should seed replication occur before longer-run behavior is understood?
- Is a 256x256 pilot justified by the current training evidence?
- Should training be deferred in favor of warning-framework case reporting and manuscript development?
- What explicit limits must govern any authorized follow-up phase?

The phase is a review and authorization gate. It should preserve the existing model, loss, configuration, data split, and Level 4+ claim boundary while selecting the lowest-risk next step that can add meaningful evidence.

## 4. Candidate Expansion Options

### Option A: 128x128 Seed42 Longer Run

Authorize a separate follow-up phase to extend the current 128x128 seed42 baseline from the Phase 47 10-epoch pilot to a bounded longer run, such as 40 epochs.

Decision candidate:

```text
phase51_authorize_128x128_seed42_longer_run
```

Purpose:

- Test whether the established route remains numerically and diagnostically stable under longer training.
- Determine whether validation performance improves, plateaus, or degrades beyond 10 epochs.
- Preserve the current resolution, seed, architecture, loss, data split, and Level 4+ interpretation.

This is the recommended option because it changes only the training horizon and directly addresses the largest unresolved question in the current baseline.

### Option B: 128x128 Seed Replication

Authorize separate 128x128 runs for seed123 and seed202 using the existing route.

Decision candidate:

```text
phase51_authorize_128x128_seed_replication
```

Purpose:

- Assess seed sensitivity.
- Begin estimating variability across controlled repetitions.

This option is useful but premature. Replicating a short 10-epoch pilot would estimate variability around a training horizon that has not yet been shown to be adequate. Replicating a longer-run protocol should be reconsidered only after the seed42 longer-run evidence is reviewed.

### Option C: 256x256 Pilot

Authorize a bounded 256x256 training pilot.

Decision candidate:

```text
phase51_authorize_256x256_pilot
```

Purpose:

- Test whether higher spatial resolution changes predictive detail or diagnostic behavior.
- Extend the Phase 46 no-training 256x256 feasibility evidence into training evidence.

This option has greater compute, memory, runtime, and comparison risk than Option A. Phase 46 established data-path feasibility, not 256x256 training stability. A higher-resolution pilot should remain deferred until the existing 128x128 route has been reviewed under a longer training horizon.

### Option D: Warning-Framework Case Reporting or Manuscript Path

Defer new training and expand case-level reporting, warning-framework interpretation, research-grade figures, or manuscript development.

Decision candidate:

```text
phase51_defer_training_for_case_reporting
```

Purpose:

- Deepen reporting around representative reliable, caution, and high-risk cases.
- Improve manuscript and README interpretation without generating new training evidence.

This remains a valid low-risk reporting path, but it does not resolve whether the Phase 47 baseline is stable or improved under a longer training horizon.

### Option E: Defer Expansion

Make no training or reporting expansion authorization.

Decision candidate:

```text
phase51_defer_expansion
```

This option should be selected if the Phase 43-50 evidence is incomplete, inconsistent, or insufficient to define a bounded follow-up protocol.

## 5. Evidence Used for Decision

The Phase 51 decision should use only reviewed Phase 43-50 evidence.

Primary evidence:

- Phase 43-44 support a full-dataset Level 4+ route while excluding Level 5, SWE, PINN, and hydrodynamic closure claims.
- Phase 45 establishes a fixed full-dataset index with 120 train scenarios and 48 test scenarios.
- Phase 46 establishes no-training feasibility for 128x128 and 256x256 downsampling, tiling, batches, and checked memory use.
- Phase 47 establishes one successful 128x128 seed42 10-epoch baseline.
- Phase 48 establishes diagnostic coverage over 48 scenarios and 384 windows.
- Phase 49 establishes conservative warning labels and warning actions.
- Phase 50 consolidates the evidence, claim boundaries, paper-ready summaries, and research-grade figures.

The decision should interpret the evidence as follows:

- The 128x128 seed42 route is the only route with actual training evidence.
- The 10-epoch horizon is a pilot horizon and does not establish longer-run behavior.
- Seed123 and seed202 have no current training evidence.
- 256x256 has data-path feasibility evidence but no training evidence.
- Tile, multiscale, and full 500x500 paths have no authorized training evidence.
- Current diagnostics support review and screening, not calibrated uncertainty or probability claims.
- No available evidence justifies changing the model, loss, architecture, or physics claim level.

## 6. Risk Assessment

| Option | Main value | Main risk | Relative risk | Phase 51 disposition |
| --- | --- | --- | --- | --- |
| A. 128x128 seed42 longer run | Tests longer-run stability on the established route | Overfitting, performance plateau, or degradation after 10 epochs | Low | Recommend authorization for a separate phase |
| B. 128x128 seed replication | Measures seed sensitivity | Replicates an inadequately reviewed short-horizon protocol and multiplies compute | Moderate | Defer |
| C. 256x256 pilot | Tests higher-resolution behavior | Increased memory/runtime risk and confounding from changing resolution before training-horizon review | Moderate to high | Defer |
| D. Case reporting/manuscript path | Adds interpretation without training risk | Does not resolve longer-run baseline behavior | Low | Retain as a parallel future reporting option, but do not select as the next training decision |
| E. Defer expansion | Avoids new experimental risk | Leaves the main unresolved training-horizon question unanswered | Low operational risk, high evidence-stagnation risk | Use only if authorization inputs are incomplete |

Specific risks for Option A must be controlled in the follow-up phase:

- Longer training may overfit the fixed train/test protocol.
- Best-epoch and final-epoch metrics may diverge.
- Aggregate metrics may improve while warning-framework failure modes remain unchanged or worsen.
- Checkpoint or output naming may accidentally overwrite Phase 47 evidence.
- Unbounded runtime or implicit configuration changes could prevent fair comparison.
- A better longer-run result could be overstated as seed robustness, higher-resolution validation, physics closure, or production readiness.

These risks are manageable with a fixed protocol, separate output directory, explicit epoch limit, checkpoint retention, metric comparison, and unchanged claim boundaries.

## 7. Training Authorization Boundary

Phase 51 is decision-only.

Phase 51 may:

- Review Phase 43-50 artifacts.
- Compare candidate expansion options.
- Record one selected decision.
- Define guardrails and success criteria for a future controlled phase.
- Specify the minimum required configuration, script, output-directory, and evaluation controls for that future phase.

Phase 51 may not:

- Run training.
- Create new model checkpoints.
- Run seed123 or seed202.
- Run 256x256 training.
- Run tile, multiscale, or full 500x500 training.
- Run hyperparameter, seed, resolution, loss, or architecture sweeps.
- Modify the model, loss, architecture, or experiment configuration.
- Implement SWE residuals or PINN components.

Selection of:

```text
phase51_authorize_128x128_seed42_longer_run
```

means only that a separate controlled implementation/training phase may be created. That follow-up phase must define:

- A fixed 128x128 seed42 configuration.
- A bounded longer-run epoch target, recommended as 40 epochs.
- The exact training and evaluation script.
- A new output directory that does not overwrite Phase 47.
- Checkpoint and best-epoch retention rules.
- Explicit train/test sample and split preservation.
- Runtime and resource limits.
- A direct Phase 47 versus longer-run comparison.
- Post-training reliability and warning-diagnostic review requirements.
- Stop, failure, and rollback criteria.

No training authorization exists until that separate follow-up phase is explicitly created and approved.

## 8. Recommended Decision

Phase 51 should select:

```text
phase51_authorize_128x128_seed42_longer_run
```

The recommendation is based on the following:

- Phase 47 was only a 10-epoch seed42 pilot.
- The 128x128 seed42 route is the only path with completed training evidence.
- Extending the training horizon changes fewer variables than changing the seed or resolution.
- A longer run can determine whether the current route improves, plateaus, overfits, or becomes unstable.
- The result can define a more defensible protocol for later seed replication.
- The option has lower compute and interpretation risk than immediate 256x256, tile, multiscale, full-resolution, or sweep expansion.
- The option preserves the current model, loss, architecture, data route, and Level 4+ claim boundary.

The authorized future comparison should treat Phase 47 as the fixed reference:

```text
reference_seed = 42
reference_resolution = 128
reference_epochs = 10
candidate_seed = 42
candidate_resolution = 128
candidate_epochs = 40
```

The follow-up phase should review training curves, best and final test metrics, rollout stability, wet/dry behavior, physical proxy diagnostics, and warning-label effects before any further expansion is considered.

## 9. Rejected or Deferred Options

The following options should not be authorized by Phase 51:

- `phase51_authorize_128x128_seed_replication`: deferred until the longer-run seed42 protocol is reviewed. Seed123 and seed202 must not run in Phase 51.
- `phase51_authorize_256x256_pilot`: deferred until longer-run 128x128 stability is established and resource limits are reviewed.
- Tile training: deferred because tile feasibility is not equivalent to validated tile-training behavior.
- Multiscale training: deferred because it changes the experimental route and introduces additional comparison variables.
- Full 500x500 training: deferred because it has substantially greater memory, runtime, and implementation risk.
- Hyperparameter or architecture sweeps: rejected for the next step because they would obscure the controlled comparison.
- New loss design: rejected because Phase 51 should not alter the current model/loss/config claim basis.
- SWE residual or PINN implementation: rejected because available evidence does not support these paths.
- Level 5 expansion: rejected because hydrodynamic closure and required physical-state evidence remain unavailable.

The decision:

```text
phase51_defer_training_for_case_reporting
```

should remain available if reviewers determine that manuscript or warning-case reporting has higher immediate priority than new training evidence. It is not the recommended selected decision because it leaves longer-run behavior unresolved.

The decision:

```text
phase51_defer_expansion
```

should be used only if the evidence review finds missing or inconsistent inputs that prevent a bounded authorization.

## 10. Expected Outputs

Phase 51 should produce documentation and decision records only. No checkpoint, training log, or new performance result should be produced.

Required output:

```text
docs/phase51_reviewed_expansion_decision_plan.md
```

Recommended follow-up decision artifacts, if Phase 51 is later implemented as a scripted review:

```text
analysis/phase51_reviewed_expansion_decision/
  phase51_candidate_option_comparison.csv
  phase51_risk_register.csv
  phase51_training_authorization_boundary.json
  phase51_reviewed_expansion_decision.json
  phase51_reviewed_expansion_decision.md
```

The structured decision record should include:

- Selected decision.
- Reviewed source phases and artifacts.
- Candidate options considered.
- Reasons for authorization, rejection, or deferral.
- Claim-boundary flags.
- `no_training = true`.
- Required controls for the separate follow-up phase.

The expected selected decision field is:

```text
selected_decision = phase51_authorize_128x128_seed42_longer_run
```

## 11. Guardrails

Phase 51 must follow these guardrails:

- Phase 51 itself is decision-only.
- Do not train in Phase 51.
- Do not run seed123 or seed202 in Phase 51.
- Do not run 256x256 in Phase 51.
- Do not run tile, multiscale, or full 500x500 training.
- Do not run sweeps.
- Do not modify model, loss, configuration, or architecture.
- Do not implement SWE residuals.
- Do not implement PINN.
- Do not claim Level 5 support.
- Do not claim strict conservation.
- Do not claim full mass conservation.
- Do not claim hydrodynamic closure.
- Do not claim calibrated probability warning labels.
- Do not claim production readiness.
- Do not reinterpret high-risk labels as proof of poor overall model skill.
- Do not generalize beyond the tested seed, resolution, dataset split, model configuration, and diagnostic protocol.
- Do not overwrite or modify Phase 47-50 evidence artifacts.
- Require a separate controlled follow-up phase before any actual training.
- Require that the follow-up phase define its config, script, output directory, checkpoint policy, resource limits, evaluation protocol, and explicit stop conditions.

## 12. Success Criteria

Phase 51 is successful if:

- All candidate options are reviewed against the Phase 43-50 evidence.
- The selected decision is explicitly recorded.
- The selected decision is `phase51_authorize_128x128_seed42_longer_run`, unless a documented evidence inconsistency requires deferral.
- The reason for preferring a longer 128x128 seed42 run over seed replication or higher resolution is clear.
- Phase 51 produces no training runs, checkpoints, or new model metrics.
- Seed123, seed202, 256x256, tile, multiscale, full 500x500, and sweep paths remain unexecuted.
- Model, loss, configuration, and architecture remain unchanged.
- The Level 4+ claim boundary remains intact.
- Level 5, SWE/PINN, strict conservation, full mass conservation, hydrodynamic closure, calibrated warning probability, and production-readiness claims remain excluded.
- The future training authorization boundary requires a separate controlled phase with explicit limits and non-overwriting outputs.
- Deferred options have clear reconsideration conditions.

The future longer-run phase should not be considered successful merely because it completes 40 epochs. It must compare best-epoch and final-epoch behavior against Phase 47 and review reliability, physical proxy, and warning-framework effects before seed or resolution expansion is reconsidered.

## 13. Final Conclusion

Phase 51 should authorize only one conservative next training path:

```text
phase51_authorize_128x128_seed42_longer_run
```

This is an authorization decision for a separate controlled follow-up phase, not permission to train during Phase 51. The next experiment should retain the 128x128 resolution, seed42, current model, current loss, current configuration basis, and Level 4+ claim boundary while extending the training horizon under explicit limits.

Seed replication, 256x256, tile, multiscale, full 500x500, sweeps, and new loss or architecture design should remain deferred until the longer-run evidence is completed and reviewed. Level 5, SWE/PINN, strict conservation, full mass conservation, hydrodynamic closure, calibrated probability warning labels, and production readiness remain unsupported.
