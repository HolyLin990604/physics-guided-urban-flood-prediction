# Physics-Guided Urban Flood Process Prediction

A research prototype for physics-guided urban flood process prediction based on a U-Net + TCN framework.

## Method Diagram

```mermaid
flowchart LR
    A[Past flood sequence] --> B[U-Net encoder]
    C[Past rainfall sequence] --> D[Temporal conditioning]
    E[Future rainfall sequence] --> D
    F[Static maps<br/>DEM / impervious / manhole] --> B

    B --> G[TCN temporal module]
    D --> G
    G --> H[Decoder]
    H --> I[Predicted future flood depth field]

    I --> J[Data loss]
    I --> K[Non-negativity loss]
    I --> L[Wet/dry consistency loss]
    I --> M[Rainfall-depth consistency loss]
    E --> M
```

## Stage Evolution

```mermaid
flowchart TB
    A["Foundation<br/>Baseline U-Net + TCN<br/>Phases 1-5"]:::foundation
    B["Architecture Refinement<br/>Temporal gates / adaptive response<br/>Phases 6-11"]:::foundation
    C["Reliability-Aware Warning Framework<br/>Diagnostics / risk mapping / warning rules<br/>Phases 12-17"]:::reliability
    D["Manuscript + Application Layer<br/>Manuscript synthesis / case study prototype<br/>Phases 18-23"]:::reliability
    E["Physical Consistency Deepening<br/>Failure modes / target-wet recall<br/>Phases 24-25"]:::physics
    F["Strong Physics Feasibility<br/>Level 4 proxy supported<br/>Level 5 SWE/PINN not supported<br/>Phase 26"]:::physics
    G["Volume-Response Loss Redesign<br/>Phase 27 mixed pilot<br/>Phase 28 failure diagnosis<br/>Phase 29 tolerance-band mixed pilot"]:::physics
    H["Current Status<br/>Phase 49 warning framework complete<br/>UrbanFlood24 full 128x128 route<br/>Phase 50 synthesis or reviewed expansion decision next<br/>Level 5 SWE/PINN frozen"]:::current

    A --> B --> C --> D --> E --> F --> G --> H

    classDef foundation fill:#e8f1ff,stroke:#3b6ea8,stroke-width:1px,color:#10233f
    classDef reliability fill:#edf8f1,stroke:#3f8f5f,stroke-width:1px,color:#173824
    classDef physics fill:#fff3df,stroke:#b77722,stroke-width:1px,color:#3d2608
    classDef current fill:#f7e9ee,stroke:#a84b6b,stroke-width:2px,color:#3d1021
```

Detailed phase-by-phase records are maintained in docs/experiment_index.md.

## Overview

This repository implements a spatiotemporal urban flood forecasting prototype using the UrbanFlood24 Lite dataset.  
The baseline model is built on a U-Net + TCN architecture for multi-step flood process prediction.

On top of the baseline, a Phase 1 physics-guided model is implemented by adding two output-space regularization terms:

- Non-negativity loss
- Wet/dry consistency loss

These physics-guided losses are imposed on the predicted future flood depth field at the output layer, while the backbone architecture remains unchanged.

## Current Mainline

The current overall best-balanced architecture reference is:

- `temporal_gate_residual_partial`
- `hidden_channels = 16`
- `residual_alpha = 0.10`
- `conditioned_fraction = 0.25`

This configuration remains the M3 `f025` mainline reference.

The strongest static structured refinement discovered so far is:

- `temporal_gate_residual_response_split_protected`
- `hidden_channels = 16`
- `residual_alpha = 0.10`
- `conditioned_fraction = 0.25`
- `active_fraction_within_response = 0.25`

This configuration remains the Phase 3.3 `af025` static reference.

Phase 6 Pilot A added an optional bounded adaptive scalar on top of the protected response-split path. The mechanism was technically stable, but the `adapt025` setting did not beat the static Phase 3.3 `af025` control in final validation, so it is treated as a documented negative/neutral adaptive result.

Phase 7 and Phase 8 established the more conservative `adapt010` setting as the active adaptive candidate before margin-aware refinement. It showed consistent RMSE, MAE, and loss gains across the required full `40e` comparisons, but Phase 8 also exposed a mixed wet/dry IoU trade-off, mainly through `seed123`.

Phase 9 diagnosed that trade-off as a mixed, margin-region, step-dependent wet/dry issue rather than adaptive multiplier saturation or seed-specific mechanism instability.

Phase 10 introduced a minimal diagnosis-driven intervention: boundary-band weighted wet/dry consistency refinement. The recommended Phase 10 setting is:

- `boundary_band_pixels = 1`
- `boundary_weight = 2.0`

This setting passed test-facing confirmation across the three key seeds:

- `seed123`: original mixed-IoU problem seed
- `seed42`: favorable-case guardrail seed
- `seed202`: difficult-case confirmation seed

`boundary_weight = 1.5` remains only a conservative rollback setting. No broader Phase 10 boundary-weight sweep is justified at this point.

Phase 12 then diagnosed the reliability and applicability boundaries of this recommended model using saved test-facing forecast maps. The first-pass diagnosis generated timestep-wise, depth-bin, boundary-distance, scenario-level, failure-case, and figure-based outputs under `analysis/phase12_reliability/`.

The main Phase 12 finding is that the model is useful for rapid spatiotemporal flood-process approximation, but reliability is not uniform. Exact wet/dry boundary cells remain the main bottleneck, moderate-to-deep target depths show stronger underprediction, and high-intensity `location2` cases dominate the highest-ranked failures.

Phase 15 converts the Phase 12/13/14 diagnostic evidence into a functional reliability-screening and spatial risk-mapping layer. It does not retrain models, modify architecture, modify the Phase 10 loss, tune `boundary_weight` or `boundary_band_pixels`, or start a new sweep.

Phase 16 converts the Phase 15 deterministic reliability-screening labels into application-oriented warning-rule guidance and an applicability boundary summary. The project progression is now:

```text
rapid prediction + reliability screening + spatial risk mapping
becomes
rapid prediction + reliability screening + spatial risk mapping + warning-rule guidance
```

Phase 16 warning labels are deterministic operational interpretation labels. They are not calibrated probabilities, Bayesian uncertainty, or formal confidence intervals.

Phase 17 synthesizes the Phase 12 through Phase 16 evidence into a coherent reliability-aware flood-warning framework narrative. It does not retrain models, modify architecture, modify the Phase 10 loss, tune `boundary_weight` or `boundary_band_pixels`, or open a new sweep. The current recommended Phase 10 setting remains:

- `boundary_band_pixels = 1`
- `boundary_weight = 2.0`

The project position after Phase 17 is:

```text
rapid prediction + reliability diagnosis + failure-mode interpretation
+ confidence proxy diagnostics + spatial risk mapping + warning-rule guidance
```

This synthesis is intended to support manuscript writing, README narrative, and project positioning. It should not be interpreted as calibrated uncertainty or universal generalization beyond the tested evidence.

Phase 18 prepares manuscript-ready material for the section "Reliability-Aware Warning Layer for Urban Flood Surrogate Prediction" using the completed Phase 12-17 reliability-aware warning framework. It is a writing/synthesis phase only: no retraining, architecture modification, Phase 10 loss change, `boundary_weight` or `boundary_band_pixels` tuning, or new sweep was performed. See `docs/manuscript_reliability_aware_warning_layer.md`.

Phase 19 prepares a paper-ready manuscript structure and submission-consolidation plan from the completed Phase 12-18 materials. It is not a new experiment phase and does not involve retraining, architecture modification, Phase 10 loss modification, boundary-parameter tuning, a new sweep, or new result generation. See `docs/manuscript_structure_and_submission_consolidation.md`.

Phase 20 assembles the Phase 18 and Phase 19 manuscript-oriented materials into the first full manuscript draft skeleton. It is not a new experiment phase and does not involve retraining, architecture modification, Phase 10 loss modification, boundary-parameter tuning, a new sweep, or new result generation. See `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`.

Phase 21 aligns manuscript claims with existing evidence sources, figures, tables, JSON/CSV outputs, and findings documents before full manuscript expansion. It is not a new experiment phase and does not involve retraining, architecture modification, Phase 10 loss modification, boundary-parameter tuning, a new sweep, new result generation, or a new uncertainty claim. See `docs/manuscript_evidence_figure_table_alignment.md`.

Phase 22 expands the Phase 20 manuscript skeleton into a fuller academic manuscript draft using the Phase 21 evidence-alignment document. It is not a new experiment phase and does not involve retraining, architecture modification, Phase 10 loss modification, boundary-parameter tuning, a new sweep, new result generation, invented references, or unsupported claims. See `docs/manuscript_full_draft_reliability_aware_urban_flood_warning.md`.

Phase 23 converts the completed reliability-aware warning framework into a representative case-study prototype. It integrates Phase 15 reliability screening, Phase 16 warning rules, and existing Phase 10 forecast map arrays to support case-specific warning interpretation. It does not involve retraining, architecture modification, Phase 10 loss modification, boundary-parameter tuning, a new sweep, metric chasing, or new prediction generation. See `docs/phase23_reliability_warning_case_study_findings.md`.

Representative Phase 23 figures:

![Phase 23 warning level overview](analysis/phase23_warning_case_study/figures/case_warning_level_overview.png)

![Phase 23 risk component comparison](analysis/phase23_warning_case_study/figures/case_risk_component_comparison.png)

![Phase 23 reliable case maps](analysis/phase23_warning_case_study/figures/reliable_case_maps.png)

![Phase 23 caution case maps](analysis/phase23_warning_case_study/figures/caution_case_maps.png)

![Phase 23 high-risk case maps](analysis/phase23_warning_case_study/figures/high_risk_case_maps.png)

Phase 24 deepens the reliability-aware warning framework by diagnosing whether the existing Phase 10 recommended surrogate outputs are physically consistent in volume response, wet-area contraction, peak-depth preservation, wet-area connectivity, temporal behavior, and linkage with Phase 15/16 warning-risk labels. It is a diagnostic phase only: no retraining, architecture modification, Phase 10 loss modification, boundary-parameter tuning, new sweep, metric chasing, traffic-impact modeling, or new prediction generation was performed. See `docs/phase24_physical_consistency_deepening_findings.md`.

The main Phase 24 finding is that high-risk cases are not only statistically worse; they are physically less consistent. Relative to reliable cases, high-risk cases show stronger false-dry behavior, wet-area contraction, peak-depth underprediction, connectivity loss, and volume under-response. Correlations with `risk_score` are 0.913 for `false_dry_rate`, 0.862 for `wet_area_contraction`, 0.856 for `peak_depth_underprediction`, and 0.539 for `connectivity_loss_indicator`.

Phase 25 converts the Phase 24 physical-consistency diagnosis into a targeted model refinement: **Physics-Consistency Guided Surrogate Refinement: Target-Wet Recall Consistency**. The fixed Phase 10 boundary-band settings remain `boundary_band_pixels = 1` and `boundary_weight = 2.0`; Phase 25 adds a config-gated `target_wet_recall_consistency` loss with `weight = 0.02`, `threshold = 0.05`, `temperature = 0.02`, and `eps = 1e-6`. See `docs/phase25_three_seed_target_wet_recall_synthesis_findings.md`.

The main Phase 25 finding is that target-wet recall consistency is a strong three-seed positive candidate and a credible targeted refinement over the Phase 10 baseline. Across `seed123`, `seed42`, and `seed202`, it improved standard test metrics and reduced the intended aligned physical failure modes. Mean standard test deltas versus Phase 10 were `RMSE = -0.007057`, `MAE = -0.001519`, `wet/dry IoU = +0.076670`, `rollout stability = +0.001035`, and `step RMSE std = -0.001071`. Mean aligned physical deltas were `false_dry_rate = -0.111321`, `wet_area_contraction = -0.079104`, `relative_volume_bias = +0.105093`, `peak_depth_underprediction = -0.014962`, `RMSE = -0.007244`, and `MAE = -0.001885`.

Phase 25 is a diagnosis-driven, depth-field-compatible physical-consistency refinement. It improves target-wet recall and wet-region preservation while maintaining or improving standard prediction metrics. Remaining limitations include slight false-wet increase and non-uniform connectivity behavior; Phase 25 is not a complete hydrodynamic consistency solution and does not implement a full SWE/PINN residual.

Phase 26 performs **Strong Physics Constraint Feasibility Audit and Conservation-Proxy Diagnostics**. It is diagnostic only: no retraining, architecture modification, Phase 10 loss modification, boundary-parameter tuning, Phase 25 weight sweep, new prediction generation, or full SWE/PINN implementation was performed. See `docs/phase26_strong_physics_constraint_feasibility_findings.md` and `analysis/phase26_strong_physics_constraint_feasibility/conservation_residual_summary.md`.

The Phase 26 input audit found that repository-local `.npy` files were not found in the scanned directories; `evaluation_test` `forecast_maps.npz` artifacts under `runs/` are available; the representative flood spatial shape is `[128, 128]`; the Phase 10 recommended baseline is `boundary_weight = 2.0 / w20`; `w15` / `boundary_weight = 1.5` is rollback or non-default; Phase 25 `target_wet_recall` runs are available for `seed123`, `seed42`, and `seed202`; Level 4 conservation-oriented diagnostics are partially supported; Level 4 conservation-aware loss design remains unclear; and Level 5 full SWE/PINN residual constraints are not supported because velocity/flux fields, boundary inflow/outflow, pump/gate operations, `dx/dy`, and shape-compatible DEM/static elevation are missing or unclear.

The conservation-proxy diagnostics processed 114 map files and 2,736 step records. The main Phase 26 conclusion is that Phase 25 is directionally stronger than the Phase 10 recommended baseline on the main conservation-proxy diagnostics, especially aggregate water-volume response, false-dry volume loss, wet-area contraction, peak-depth preservation, RMSE, and MAE.

Key Phase 26 deltas show aggregate volume-response improvement and reduced under-response:

- Aggregate absolute relative volume bias improves across all three seeds: `seed123 = -0.064695`, `seed42 = -0.114739`, and `seed202 = -0.0405758`.
- False-dry volume loss decreases across all three seeds: `seed123 = -26.4163`, `seed42 = -32.2189`, and `seed202 = -13.3703`.
- Wet-area contraction decreases across all three seeds: `seed123 = -0.0848763`, `seed42 = -0.104508`, and `seed202 = -0.0519941`.

The boundary is important: Phase 25 improves aggregate water-volume response and reduces under-response, but it is not a strict timestep-wise conservation solution. Timestep-wise absolute relative volume bias is mixed: `seed42` improves, while `seed123` and `seed202` show very small increases. False-wet rate and false-wet volume excess increase slightly and should be treated as trade-offs.

Phase 27 introduced a conservative `volume_response_consistency` loss and tested a `seed42 / 40e` pilot. See `docs/phase27_seed42_volume_response_pilot_findings.md` and `analysis/phase27_conservative_volume_response_consistency/phase27_seed42_summary.md`.

The Phase 27 seed42 result is a mixed pilot. Relative to the Phase 25 seed42 reference, it improved all standard test metrics: `RMSE = -0.00236602`, `MAE = -0.000654673`, `wet/dry IoU = +0.00892365`, `rollout stability = +0.000618097`, and `step RMSE std = -0.000631138`. It also improved several under-response-related conservation proxies, including reduced false-dry volume loss, wet-area contraction, peak-depth underprediction, false-wet rate, and false-wet volume excess.

However, the primary conservative volume-response objective was not achieved. Aggregate absolute relative volume bias worsened by `+0.0216934`, mean-step absolute relative volume bias worsened by `+0.0170953`, and run-level aggregate relative volume bias moved from Phase 25 `+0.00296825` to Phase 27 `+0.0246616`. The result should therefore be interpreted as `seed42` standard-metric positive but volume-response objective not confirmed. Current decision: `remain_seed42_positive_only`; do not proceed to `seed123` / `seed202` confirmation, do not start a Phase 27 weight sweep, and do not claim strong physics success, strict mass conservation, or SWE/PINN support.

Phase 28 diagnosed why the Phase 27 seed42 pilot failed the primary volume-response objective. See `docs/phase28_volume_response_loss_diagnosis_findings.md` and `analysis/phase28_volume_response_loss_diagnosis/phase28_volume_response_failure_findings.md`.

Phase 28 is diagnostic only. It did not train a model, modify architecture, modify losses, modify configs, run `seed123` / `seed202`, or perform a Phase 27 weight sweep. The diagnosis found that the Phase 27 volume-bias worsening was not mainly caused by threshold-level false-wet expansion and was not primarily caused by already-wet amplification. The dominant source was `dry_or_threshold` target-depth-bin volume accumulation, suggesting sub-threshold or near-threshold low-depth mass accumulation.

Key Phase 28 evidence: `delta_volume_bias_total = +6974.12`; Phase 25 relative volume bias was `+0.00296825`; Phase 27 relative volume bias was `+0.0246616`; false-wet volume excess delta was `-184.071`; already-wet amplification was `+1396.20`; and the `dry_or_threshold` contribution was `+5362.82`, about `76.9%` of total delta volume bias. Phase 28 supported stopping direct expansion of the Phase 27 underresponse-only `volume_response_consistency` loss and motivated a tolerance-band direction only through a new plan; it does not support strict conservation, full mass conservation, or SWE/PINN claims.

Phase 29 introduced config-gated `tolerance_band_volume_consistency` and tested a `seed42 / 40e` mixed tolerance-band pilot. See `docs/phase29_seed42_tolerance_band_volume_findings.md` and `analysis/phase29_tolerance_band_volume_consistency/phase29_seed42_summary.md`.

Phase 29 partially repaired the Phase 27 volume-bias and `dry_or_threshold` target-depth-bin accumulation failure mode, but the current trade-off is not acceptable for `seed123` / `seed202` confirmation. Relative to Phase 27, aggregate absolute relative volume bias improved from `0.0246616` to `0.019464`, mean-step absolute relative volume bias improved from `0.257274` to `0.230447`, and `dry_or_threshold` contribution decreased from `0.137662` to `0.131428`. However, all listed standard metrics worsened, false-dry volume loss worsened from `5409.72` to `5964.83`, false-wet volume excess worsened from `7750.32` to `8289.77`, peak-depth underprediction worsened from `0.128045` to `0.134593`, and aggregate bias remains far from the Phase 25 near-zero aggregate bias of `0.00296825`.

Phase 29 seed42 test metrics are `RMSE = 0.0443854521`, `MAE = 0.0178462429`, `wet/dry IoU = 0.8016409529`, `rollout stability = 0.9895110601`, and `step RMSE std = 0.0106412431`. Current decision: `remain_seed42_only_pending_revision`; do not run `seed123` or `seed202`, do not perform a tolerance or weight sweep, and do not claim tolerance-band success, strict conservation, full mass conservation, or SWE/PINN support.

Phase 30 is a documentation-only strong-physics boundary synthesis. See `docs/phase30_strong_physics_boundary_synthesis.md` and `docs/phase30_strong_physics_boundary_synthesis_plan.md`. It defines the current project position as a Level 4 conservation-proxy / physical-consistency-guided surrogate for reliability-aware warning support, physical-consistency diagnosis, conservation-proxy evaluation, failure-mode interpretation, and applicability-boundary communication. It explicitly excludes strict mass conservation, full SWE/PINN residual consistency, and full hydrodynamic closure. The Phase 30 decision is to pause Phase 27/29 seed expansion, avoid `seed123` / `seed202` confirmation for those pilots, avoid tolerance or weight sweeps and immediate loss redesign without a new plan, keep Phase 27 and Phase 29 as documented mixed pilots, and prioritize manuscript / README / research narrative consolidation next.

Phase 31 is a diagnostic-only physics input recovery readiness phase. See `docs/phase31_physics_input_recovery_readiness_findings.md`, `analysis/phase31_physics_input_recovery_readiness/masked_physical_error_findings.md`, `analysis/phase31_physics_input_recovery_readiness/domain_boundary_mask_inspection.md`, and `analysis/phase31_physics_input_recovery_readiness/static_map_inspection.md`. It confirms that Level 4+ structured physical proxy diagnostics are supported: raw flood/rain/static arrays are available; `absolute_DEM.npy`, `impervious.npy`, and `manhole.npy` are available with `128 x 128` shape; train/test geodata are consistent; `DEM = 100` is likely high/invalid/no-data candidate; `absolute_DEM < 99` supports valid-domain mask construction; valid-domain, invalid/high, boundary-ring, and interior masks can be constructed; sample-to-location mapping for forecast maps was recovered from adjacent `summary.json` `metadata.location`; and masked physical diagnostics are fully supported.

Phase 31 does not change the strong-physics boundary. Level 5 remains unsupported because aligned velocity/flux fields, boundary/source-sink aligned fields, explicit `dx/dy`, full hydrodynamic state variables, and non-inferred `dt` are not available. The project should still avoid strict conservation, full mass conservation, SWE/PINN, and full hydrodynamic closure claims.

Masked Phase 31 diagnostics reinforce that Phase 29 should remain a mixed result, not a successful one. Relative to Phase 27, Phase 29 improved valid-domain masked relative volume-bias proxy from `0.0169359` to `0.0115344`, but worsened valid-domain `RMSE` from `0.0460827` to `0.0480984`, `MAE` from `0.0183693` to `0.0190492`, `false_dry_rate` from `0.0689175` to `0.0739891`, `false_wet_rate` from `0.0181923` to `0.0194308`, `false_dry_volume_loss_proxy` from `3575.36` to `4027.38`, and `false_wet_volume_excess_proxy` from `5263.67` to `5690.27`. Phase 29 also has the highest false-dry rate over `manhole_nonzero_valid` (`0.131298`) and the highest false-wet rate over `high_impervious_valid` (`0.0239894`).

Phase 32 completes a plan-first, design/diagnostic-only **Level 4+ Domain-/Boundary-Aware Physical Consistency Design**. See [Phase 32 findings](docs/phase32_domain_boundary_aware_physical_consistency_findings.md), [Phase 32 design](docs/phase32_domain_boundary_aware_design.md), and [Phase 32 guardrail summary](analysis/phase32_domain_boundary_aware_design/phase32_guardrail_summary.md). It translates the Phase 31 recovered masks and masked diagnostics into a conservative design and guardrail framework; it does not train a model, modify losses, modify configs, or alter model architecture. The current decision is `design_ready_no_training_yet`.

Phase 32 formalizes 20 guardrail metrics and 12 stop/go criteria across standard, valid-domain, boundary-ring, high-impervious-valid, manhole-nonzero-valid, dry-threshold, and level-boundary groups. It supports Level 4+ proxy diagnostics only. Level 5 remains unsupported, and the project should still avoid strict conservation, full mass conservation, SWE/PINN, and hydrodynamic closure claims. The Phase 31 masked evidence also remains binding: Phase 29 improved valid-domain relative volume-bias proxy but worsened valid-domain RMSE, MAE, false-dry, false-wet, false-dry volume-loss, and false-wet volume-excess proxies, so Phase 29 remains mixed rather than successful.

Phase 33 completes a diagnostic-only **seed42 pilot readiness review** under the Phase 32 guardrail framework. See [Phase 33 findings](docs/phase33_seed42_pilot_readiness_review_findings.md), [Phase 33 readiness summary](analysis/phase33_seed42_pilot_readiness/phase33_readiness_summary.md), [pilot option scores](analysis/phase33_seed42_pilot_readiness/pilot_option_scores.csv), and [readiness criteria status](analysis/phase33_seed42_pilot_readiness/readiness_criteria_status.csv). It reviewed 5 pilot options and 15 readiness criteria. The recommended future candidate is `manhole_nonzero_false_dry_guardrail`, because `manhole_nonzero_valid` had the highest Phase 29 false-dry rate. The current decision is `pilot_design_ready_but_training_not_started`, and `training_authorized = false`.

Phase 33 does not authorize training. Numeric acceptance thresholds, numeric rejection thresholds, and full Phase 25 / Phase 27 / Phase 29 baseline acceptance/rejection criteria are not fixed, so no `seed42` training, `seed123` / `seed202` training, sweep, Phase 29 continuation, loss modification, config modification, or architecture modification is justified. Claims remain Level 4+ proxy scope only; the project should not claim strict conservation, full mass conservation, SWE/PINN support, or hydrodynamic closure.

Phase 34 completes threshold-formalization only for a possible future `manhole_nonzero_false_dry_guardrail` seed42 pilot. See [Phase 34 findings](docs/phase34_pilot_threshold_formalization_findings.md), [Phase 34 threshold summary](analysis/phase34_pilot_thresholds/phase34_threshold_summary.md), [acceptance thresholds](analysis/phase34_pilot_thresholds/acceptance_thresholds.csv), [rejection thresholds](analysis/phase34_pilot_thresholds/rejection_thresholds.csv), and [baseline metric table](analysis/phase34_pilot_thresholds/baseline_metric_table.csv). Phase 34 formalized 23 baseline metric rows, 14 acceptance thresholds, and 9 rejection thresholds. The current decision is `thresholds_formalized_training_still_blocked`; `training_authorized = false`; `next_allowed_step = pilot_implementation_plan`; and `candidate = manhole_nonzero_false_dry_guardrail`.

The Phase 34 target is `manhole_nonzero_valid` `false_dry_rate`. AT01 requires that metric to be below Phase 29 and no higher than Phase 27: Phase 27 = `0.1172229713`, Phase 29 = `0.131297982994`, threshold = `0.1172229713`. RT01 hard-rejects the Phase 29 trade-off pattern: improving the absolute relative volume-bias proxy is not acceptable if `RMSE`, `MAE`, `false_dry_rate`, and `false_wet_rate` all worsen versus Phase 27. AT13 makes volume-bias proxy improvement conditional and insufficient alone, while AT14 / RT09 preserve the Level 4+ proxy claim boundary. Guardrails remain: no training, no `seed42` run, no `seed123` / `seed202`, no sweeps, no Phase 29 continuation, no loss/config/architecture modification, no strict or full mass-conservation claim, no SWE/PINN claim, no hydrodynamic closure claim, and Level 4+ proxy scope only.

Phase 35 completes a pilot implementation plan only for the possible future `manhole_nonzero_false_dry_guardrail` candidate. See [Phase 35 pilot plan](docs/phase35_manhole_false_dry_guardrail_pilot_plan.md). It does not implement losses, create configs, modify model code, or run training. The target region remains `manhole_nonzero_valid`; the target metric remains `false_dry_rate`; the key AT01 false-dry threshold remains `0.1172229713`; `training_authorized = false`; and the next allowed step is a code/smoke-test implementation phase, not training. Guardrails remain: no training, no `seed42`, no `seed123` / `seed202`, no sweep, no Phase 29 continuation, no strict conservation, no full mass conservation, no SWE/PINN, no hydrodynamic closure, and Level 4+ proxy claims only.

Phase 36 implements and smoke-tests the config-gated `manhole_nonzero_false_dry_guardrail` code path and guardrail checker only. See [Phase 36 findings](docs/phase36_manhole_false_dry_guardrail_code_smoke_findings.md), [Phase 36 plan](docs/phase36_manhole_false_dry_guardrail_code_smoke_plan.md), [smoke-test summary](analysis/phase36_manhole_false_dry_guardrail_code_smoke/smoke_test_summary.md), and [guardrail checker dry run](analysis/phase36_manhole_false_dry_guardrail_code_smoke/guardrail_checker_dry_run.md). Implemented artifacts are `utils/physics_losses.py`, `configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`, and `scripts/check_phase36_pilot_guardrails.py`. Smoke evidence records `config_loaded = true`, `loss_smoke_passed = true`, `guardrail_checker_dry_run_passed = true`, `training_authorized = false`, `training_executed = false`, and `decision = code_smoke_ready_training_still_blocked`. Phase 36 did not run `seed42`, did not run `seed123` / `seed202`, and did not execute training. At the Phase 36 boundary, the required next step was explicit training authorization review rather than automatic training.

Phase 37 completes a diagnostic **seed42 training authorization review**. See [Phase 37 findings](docs/phase37_seed42_training_authorization_review_findings.md), [authorization summary](analysis/phase37_seed42_training_authorization/training_authorization_summary.md), and [authorization checklist](analysis/phase37_seed42_training_authorization/authorization_checklist.csv). Required checks passed `18 / 18`; `decision = seed42_training_authorized_next_phase`; `training_authorized_next_phase = true`; and `training_executed = false`. Phase 37 itself did not train, did not run `seed42`, did not run `seed123` / `seed202`, and did not execute a sweep. It authorized only the reviewed seed42 config, `configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`, and required post-training evaluation plus guardrail checking. That authorization path was completed in Phase 38. Claims remain Level 4+ proxy scoped.

Phase 38 ran the single authorized `seed42` pilot for `manhole_nonzero_false_dry_guardrail`, completed test evaluation, completed guardrail evaluation, and rejected the pilot under the predeclared Phase 34 guardrail framework. See [Phase 38 findings](docs/phase38_seed42_pilot_training_guardrail_evaluation_findings.md), [guardrail decision](analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_guardrail_decision.md), [acceptance checks](analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_acceptance_check.csv), [rejection checks](analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_rejection_check.csv), and [standard metric checks](analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_standard_metric_check.csv). Training completed, test evaluation completed, and guardrail evaluation completed. Test metrics were `RMSE = 0.04456830142359985`, `MAE = 0.01795931400633172`, `wet_dry_iou = 0.8068740587485465`, `rollout_stability = 0.9899644569346779`, and `step_rmse_std = 0.01018835528214511`. Guardrail outcome: `final_decision = seed42_pilot_rejected`, with 2 standard checks passed, 3 standard checks failed, 6 acceptance checks passed, 8 acceptance checks failed, and 3 rejection rules triggered. This is useful negative evidence, not a training execution failure. The current `manhole_nonzero_false_dry_guardrail` design should not be treated as accepted; it shows a Phase 29-like trade-off pattern where the target/proxy behavior is not sufficient to pass broader Level 4+ guardrails. No `seed123` / `seed202` expansion, sweep, Phase 29 continuation, pilot success claim, or post-hoc loss/config rescue is allowed. Phase 39 later diagnosed this trade-off.

Phase 39 completed diagnostic-only trade-off analysis for the rejected Phase 38 seed42 pilot. See [Phase 39 findings](docs/phase39_failed_pilot_tradeoff_diagnosis_findings.md), [diagnosis summary](analysis/phase39_failed_pilot_tradeoff_diagnosis/phase39_tradeoff_diagnosis_summary.md), [failed acceptance components](analysis/phase39_failed_pilot_tradeoff_diagnosis/failed_acceptance_components.csv), [triggered rejection rules](analysis/phase39_failed_pilot_tradeoff_diagnosis/triggered_rejection_rules.csv), [metric comparison](analysis/phase39_failed_pilot_tradeoff_diagnosis/phase38_vs_baselines_metric_comparison.csv), and [region trade-off summary](analysis/phase39_failed_pilot_tradeoff_diagnosis/region_tradeoff_summary.csv). Phase 39 decision: `phase39_decision = tradeoff_diagnosis_completed_with_missing_optional_inputs`; Phase 38 remains `final_decision = seed42_pilot_rejected`; `failed_acceptance_count = 8`; `triggered_rejection_count = 3`; `comparison_rows = 13`; `region_rows = 5`; and `scenario_rows = 19`. Optional per-batch/scenario Phase 25, Phase 27, and Phase 29 baselines are unavailable, so scenario diagnostics are Phase 38-only.

The main Phase 39 diagnosis is that the current `manhole_nonzero_false_dry_guardrail` improved a narrow `manhole_nonzero_valid` false-dry proxy, but did not preserve broader valid-domain, regional guardrail, and standard metrics. RT01 indicates a Phase 29-like trade-off pattern, while RT05 and RT07 confirm unacceptable standard and valid-domain error behavior. This is useful negative evidence and does not indicate a training or evaluation execution failure.

Phase 40 completed a failed-pilot design review and next-constraint decision after the rejected Phase 38 pilot and the Phase 39 trade-off diagnosis. See [Phase 40 findings](docs/phase40_failed_pilot_design_review_next_constraint_findings.md), [next-constraint decision](analysis/phase40_failed_pilot_design_review/phase40_next_constraint_decision.md), [next-constraint options](analysis/phase40_failed_pilot_design_review/next_constraint_options.csv), and [decision criteria matrix](analysis/phase40_failed_pilot_design_review/decision_criteria_matrix.csv). Phase 40 evaluated 4 options and 13 criteria rows. The selected decision is `pause_loss_redesign_move_to_swe_data_readiness`; `training_authorized = false`; and `next_recommended_phase = phase41_swe_data_readiness_audit`. Phase 40 pauses proxy-loss redesign after repeated trade-off evidence from Phase 27, Phase 29, and Phase 38.

Phase 41 completed the no-training SWE data readiness audit requested by Phase 40. See [Phase 41 findings](docs/phase41_swe_data_readiness_audit_findings.md), [readiness summary](analysis/phase41_swe_data_readiness_audit/phase41_swe_data_readiness_summary.md), [SWE readiness matrix](analysis/phase41_swe_data_readiness_audit/swe_readiness_matrix.csv), [missing SWE inputs](analysis/phase41_swe_data_readiness_audit/missing_swe_inputs.csv), and [dataset field inventory](analysis/phase41_swe_data_readiness_audit/dataset_field_inventory.csv). Phase 41 evaluated 10 SWE-critical categories and found 5 partially or fully supported categories. The decision is `readiness_decision = readiness_uncertain_requires_external_data_export`; `level5_supported = false`; `external_hydrodynamic_model_export_needed = true`; and `level4_proxy_supported = true`. Current evidence supports Level 4+ proxy diagnostics and data recovery only. Level 5 SWE/PINN residual constraints are not currently supported. Phase 44 later froze the short-term Level 5/SWE/PINN route and redirected future work to UrbanFlood24 full Level 4+ modeling.

Phase 42 completed a no-training hydrodynamic export requirement specification. See [Phase 42 findings](docs/phase42_hydrodynamic_export_requirement_specification_findings.md), [export requirement summary](analysis/phase42_hydrodynamic_export_requirements/phase42_export_requirement_summary.md), [required hydrodynamic fields](analysis/phase42_hydrodynamic_export_requirements/required_hydrodynamic_fields.csv), [minimum SWE residual data contract](analysis/phase42_hydrodynamic_export_requirements/swe_residual_minimum_data_contract.csv), [UrbanFlood24 inspection checklist](analysis/phase42_hydrodynamic_export_requirements/urbanflood24_full_inspection_checklist.csv), and [ICM/MIKE export checklist](analysis/phase42_hydrodynamic_export_requirements/icm_mike_export_checklist.csv). The decision is `selected_decision = export_contract_ready_for_dataset_inspection`; `training_authorized = false`; `required_fields_count = 16`; `minimum_contract_items = 10`; `urbanflood24_checklist_items = 10`; and `icm_mike_checklist_items = 13`. Phase 42 created a formal data contract for inspection/export work only. It was not training, not SWE/PINN implementation, and not Level 5 support.

Phase 43 completed no-training inspection of the UrbanFlood24 full dataset. See [Phase 43 findings](docs/phase43_urbanflood24_full_dataset_inspection_findings.md), [full dataset summary](analysis/phase43_urbanflood24_full_dataset_inspection/phase43_urbanflood24_full_dataset_summary.md), [Phase 42 contract compliance matrix](analysis/phase43_urbanflood24_full_dataset_inspection/phase42_contract_compliance_matrix.csv), [Level 5 readiness assessment](analysis/phase43_urbanflood24_full_dataset_inspection/level5_readiness_assessment.csv), and [sample array shape inventory](analysis/phase43_urbanflood24_full_dataset_inspection/sample_array_shape_inventory.csv). The decision is `selected_decision = full_dataset_readiness_uncertain_needs_metadata`; `level5_supported = false`; `level4_plus_supported = true`; `training_authorized = false`; `total_files = 354`; `total_dirs = 186`; and `sampled_arrays_count = 54`. UrbanFlood24 full is useful and higher-resolution than UrbanFlood24 Lite: train/test splits exist, locations `location1`, `location2`, and `location3` are present, flood scenario directories contain `flood.npy` and `rainfall.npy`, and geodata includes `absolute_DEM.npy`, `impervious.npy`, and `manhole.npy`. This supports higher-resolution Level 4+ proxy diagnostics, but it does not provide direct Level 5 SWE/PINN readiness because velocity/flux, grid spacing, time-step, boundary/source-sink, pump/gate, CRS/grid, units, scenario, and time-axis metadata are absent or uncertain. Phase 44 supersedes the Phase 43 metadata/export path as the active project route.

Phase 44 completed replanning around the already downloaded UrbanFlood24 full dataset only. See [Phase 44 replanning](docs/phase44_urbanflood24_full_level4plus_replanning.md). Phase 44 did not run training, seed runs, sweeps, loss/config/model edits, SWE residual implementation, or PINN implementation, and it makes no Level 5 support claim. The short-term Level 5/SWE/PINN route is frozen. Future work is redirected to high-resolution Level 4+ proxy modeling, reliability diagnostics, and warning framework extension using UrbanFlood24 full, without depending on new external files, author clarification, or ICM/MIKE+ export as a project path.

Phase 45 completed no-training full-dataset indexing and lightweight adapter preparation for UrbanFlood24 full. See [Phase 45 findings](docs/phase45_full_dataset_indexing_lightweight_adapter_findings.md), [dataset index summary](analysis/phase45_full_dataset_indexing/dataset_index_summary.md), [scenario index](analysis/phase45_full_dataset_indexing/scenario_index.csv), [static geodata index](analysis/phase45_full_dataset_indexing/static_geodata_index.csv), and [adapter design notes](analysis/phase45_full_dataset_indexing/adapter_design_notes.md). The indexed dataset has `scenario_count_total = 168`, `static_index_rows = 6`, `warning_count = 0`, `selected_decision = indexing_ready_for_dataloader_smoke`, `training_authorized = false`, `level4_plus_supported = true`, and `level5_supported = false`. Sequence-length evidence records flood shape `(360, 1, 500, 500)` for 153 scenarios, flood shape `(480, 1, 500, 500)` for 15 scenarios, rainfall length `180` for 108 scenarios, and rainfall length `360` for 60 scenarios. Phase 45 is indexing/adapter preparation only, not training. It provided the index used by the completed Phase 46 dataloader smoke testing.

Phase 46 completed no-training dataloader smoke testing and downsample/tiling feasibility checks for UrbanFlood24 full. See [Phase 46 findings](docs/phase46_dataloader_smoke_downsample_tiling_feasibility_findings.md), [dataloader smoke summary](analysis/phase46_dataloader_smoke_downsample_tiling/dataloader_smoke_summary.md), [sample shape checks](analysis/phase46_dataloader_smoke_downsample_tiling/sample_shape_checks.csv), [downsample feasibility checks](analysis/phase46_dataloader_smoke_downsample_tiling/downsample_feasibility_checks.csv), [tile feasibility checks](analysis/phase46_dataloader_smoke_downsample_tiling/tile_feasibility_checks.csv), [batch smoke checks](analysis/phase46_dataloader_smoke_downsample_tiling/batch_smoke_checks.csv), and [memory safety notes](analysis/phase46_dataloader_smoke_downsample_tiling/memory_safety_notes.md). The decision is `selected_decision = dataloader_smoke_ready_for_downsample_baseline`; `scenario_index_loaded = true`; `static_index_loaded = true`; `representative_samples_count = 11`; `downsample_128_passed = true`; `downsample_256_passed = true`; `tile_checks_passed = true`; `batch_smoke_passed = true`; `memory_safe = true`; `training_authorized = false`; `level4_plus_supported = true`; and `level5_supported = false`. Phase 46 is dataloader smoke testing only: it did not materialize full flood sequences, write transformed training datasets, run a model forward pass, train a model, run seeds, run sweeps, implement SWE/PINN residuals, or authorize uncontrolled training. It provided the feasibility basis for the now-completed Phase 47 controlled `128 x 128` baseline pilot.

Phase 47 completed the first controlled UrbanFlood24 full-dataset `128 x 128` downsample `seed42` 10e baseline pilot. See [Phase 47 findings](docs/phase47_controlled_full_dataset_downsample_baseline_findings.md), [training summary](analysis/phase47_controlled_downsample_baseline/phase47_training_summary.md), [metrics CSV](analysis/phase47_controlled_downsample_baseline/metrics.csv), [metrics JSON](analysis/phase47_controlled_downsample_baseline/metrics.json), [runtime and memory notes](analysis/phase47_controlled_downsample_baseline/runtime_memory_notes.md), and [training config snapshot](analysis/phase47_controlled_downsample_baseline/training_config_snapshot.json). The decision is `selected_decision = phase47_controlled_128_downsample_seed42_pilot_completed`; `seed = 42`; `resolution = 128`; `epochs = 10`; `train_samples = 960`; `test_samples = 384`; `best_test_rmse = 0.01109213042097205`; `test_mae = 0.00525291082279485`; `test_wet_dry_iou = 0.8255524213115374`; `test_rollout_stability = 0.998722607580324`; `test_step_rmse_std = 0.0012824604989987165`; `no_swe_pinn = true`; and `level5_supported = false`. Phase 47 shows that the Level 4+ full-dataset `128 x 128` route is viable as a controlled baseline path. It does not claim Level 5 support, SWE/PINN support, strict conservation, full mass conservation, or hydrodynamic closure, and it does not authorize uncontrolled expansion to `seed123` / `seed202`, `256 x 256`, tile, multiscale, full `500 x 500`, sweeps, or new loss redesign.

Phase 48 completed no-training full-dataset reliability and physical proxy diagnostics for the Phase 47 `128 x 128` baseline. See [Phase 48 findings](docs/phase48_full_dataset_reliability_physical_proxy_diagnostics_findings.md), [reliability summary](analysis/phase48_full_dataset_reliability_physical_proxy/phase48_reliability_summary.md), [scenario reliability metrics](analysis/phase48_full_dataset_reliability_physical_proxy/scenario_reliability_metrics.csv), [step reliability metrics](analysis/phase48_full_dataset_reliability_physical_proxy/step_reliability_metrics.csv), [wet/dry error metrics](analysis/phase48_full_dataset_reliability_physical_proxy/wet_dry_error_metrics.csv), [peak-depth timing metrics](analysis/phase48_full_dataset_reliability_physical_proxy/peak_depth_timing_metrics.csv), [volume-response proxy metrics](analysis/phase48_full_dataset_reliability_physical_proxy/volume_response_proxy_metrics.csv), [location-type summary](analysis/phase48_full_dataset_reliability_physical_proxy/location_type_summary.csv), and [reliability warning levels](analysis/phase48_full_dataset_reliability_physical_proxy/reliability_warning_levels.csv). The decision is `selected_decision = phase48_diagnostics_ready_for_warning_framework_extension`; `checkpoint_found = true`; `evaluated_scenarios = 48`; `evaluated_windows = 384`; `mean_rmse = 0.012037189189155709`; `mean_mae = 0.005252910632811514`; `mean_wet_dry_iou = 0.863043953275997`; `mean_false_dry_rate = 0.0911363765964386`; `mean_false_wet_rate = 0.003937674554837349`; `mean_absolute_relative_volume_bias_proxy = 0.021456503649973275`; `warning_level_counts = reliable 1, caution 12, high-risk 35`; `no_training = true`; `no_swe_pinn = true`; and `level5_supported = false`. Warning labels are conservative diagnostic screening labels, not calibrated probabilities, and the large high-risk count should not be interpreted as poor overall model skill. Phase 48 provided the diagnostic inputs for the completed Phase 49 warning-framework extension. It does not claim Level 5, SWE/PINN, strict conservation, full mass conservation, or hydrodynamic closure, and it does not authorize uncontrolled training expansion.

Phase 49 completed the no-training full-dataset warning framework extension by converting the 48 Phase 48 test scenarios into scenario-level warning actions. See [Phase 49 findings](docs/phase49_full_dataset_warning_framework_extension_findings.md), [warning framework summary](analysis/phase49_full_dataset_warning_framework/warning_framework_summary.md), [scenario warning framework](analysis/phase49_full_dataset_warning_framework/scenario_warning_framework.csv), [location-type warning summary](analysis/phase49_full_dataset_warning_framework/location_type_warning_summary.csv), [warning rule table](analysis/phase49_full_dataset_warning_framework/warning_rule_table.csv), [warning message templates](analysis/phase49_full_dataset_warning_framework/warning_message_templates.md), [high-risk case review list](analysis/phase49_full_dataset_warning_framework/high_risk_case_review_list.csv), and [Phase 49 decision JSON](analysis/phase49_full_dataset_warning_framework/phase49_warning_framework_decision.json). The decision is `selected_decision = phase49_warning_framework_completed_with_conservative_labels`; `scenario_count = 48`; `warning_level_counts = reliable 1, caution 12, high-risk 35`; `high_risk_case_count = 35`; `no_training = true`; and `warning_labels_are_probabilities = false`. The action mapping is `reliable -> normal_use_with_standard_monitoring`, `caution -> use_with_caution_and_review_diagnostics`, and `high-risk -> high_risk_requires_review_or_supplemental_evidence`. Warning labels are conservative diagnostic screening labels, not calibrated probabilities, and the high-risk count reflects conservative screening sensitivity rather than poor overall model skill. Phase 49 supports conservative case reporting and diagnostic screening. It does not claim Level 5, SWE/PINN, strict conservation, full mass conservation, hydrodynamic closure, or production readiness, and it does not authorize uncontrolled training expansion.

Representative Phase 24 figures:

![Phase 24 volume bias by warning level](analysis/phase24_physical_consistency/figures/volume_bias_by_warning_level.png)

![Phase 24 peak underprediction by warning level](analysis/phase24_physical_consistency/figures/peak_underprediction_by_warning_level.png)

![Phase 24 physical consistency vs risk score](analysis/phase24_physical_consistency/figures/physics_consistency_vs_risk_score.png)

![Phase 24 wet connectivity fragmentation](analysis/phase24_physical_consistency/figures/wet_connectivity_fragmentation.png)

![Phase 24 temporal volume bias examples](analysis/phase24_physical_consistency/figures/temporal_volume_bias_examples.png)

![Phase 24 Phase 23 case physical failure profiles](analysis/phase24_physical_consistency/figures/phase23_case_physical_failure_profiles.png)


## Phase 12 Reliability Diagnostics

The first-pass Phase 12 reliability/applicability diagnosis evaluates where the Phase 10 recommended model is reliable and where caution is needed. The diagnosis uses saved test-facing forecast maps and does not involve retraining, architecture changes, Phase 10 loss changes, or a new boundary-weight sweep.

The main finding is that the model is useful for rapid spatiotemporal flood-process approximation, but reliability is not uniform. Exact wet/dry boundary cells remain the main bottleneck, moderate-to-deep target depths show stronger underprediction, and high-intensity `location2` cases dominate the highest-ranked failures.

### Boundary-distance reliability

![Boundary-distance wet/dry class error](analysis/phase12_reliability/figures/boundary_distance_class_error.png)

### Depth-bin reliability

![Depth-bin error comparison](analysis/phase12_reliability/figures/depth_bin_error_comparison.png)

<details>
<summary>Expand additional Phase 12 diagnostic figures</summary>

### Timestep error trend

![Timestep RMSE and MAE trend](analysis/phase12_reliability/figures/timestep_rmse_mae_trend.png)

### Top failure cases

![Top 10 failure cases by RMSE](analysis/phase12_reliability/figures/top_failure_cases_rmse.png)

</details>



## Phase 13 Failure-Case Visual Summary

Phase 13 converts the highest-ranked Phase 12 failure cases into representative worst-timestep visual summaries. The top failures are not random scattered cases. They collapse into two high-intensity `location2` target scenarios repeated across seeds:

- `location2 / r300y_p0.6_d3h / start_idx = 0`, worst step 1
- `location2 / r300y_p0.8_d3h / start_idx = 0`, worst step 4

The visual summaries show systematic underprediction, reduced predicted wet fraction, local peak-depth underprediction, and false-dry dominated wet/dry mismatch.

### Representative failure-case visual summary

![Representative Phase 13 failure case](analysis/phase13_failure_cases/figures/rank01_seed42_location2_r300y_p06_d3h_start0_t01_worst_maps.png)

<details>
<summary>Expand additional Phase 13 failure-case figures</summary>

### Repeated `r300y_p0.8_d3h` failure case

![Representative Phase 13 p0.8 failure case](analysis/phase13_failure_cases/figures/rank03_seed42_location2_r300y_p08_d3h_start0_t04_worst_maps.png)

### Cross-seed `r300y_p0.6_d3h` failure case

![Representative Phase 13 seed202 p0.6 failure case](analysis/phase13_failure_cases/figures/rank06_seed202_location2_r300y_p06_d3h_start0_t01_worst_maps.png)

</details>


## Phase 14 Confidence Proxy Diagnostics

Phase 14 diagnoses whether output-space proxy signals can help identify when the current Phase 10 recommended model may be less reliable. It does not retrain the model, modify the architecture, tune Phase 10 parameters, or claim calibrated probabilistic uncertainty.

The main finding is that confidence margin is useful for wet/dry classification risk: low-margin bins show much higher wet/dry class error and false-dry rate. Cross-seed disagreement is weaker as a global scenario-error predictor and should be treated as an auxiliary disagreement proxy.

### Confidence margin versus wet/dry error

![Phase 14 confidence margin proxy](analysis/phase14_confidence/figures/confidence_margin_vs_wet_dry_error.png)

<details>
<summary>Expand additional Phase 14 diagnostic figure</summary>

### Seed disagreement versus scenario error

![Phase 14 seed disagreement proxy](analysis/phase14_confidence/figures/seed_disagreement_vs_rmse.png)

</details>

## Phase 15 Reliability Screening and Risk Mapping

Phase 15 provides the first implementation of reliability screening and risk mapping for the current Phase 10 recommended model. It combines rapid flood prediction with deterministic reliability screening and spatial risk mapping, turning the Phase 12 reliability boundaries, Phase 13 repeated failure cases, and Phase 14 confidence proxies into operational screening outputs.

The Phase 15 run loaded 57 Phase 10 map files, generated 114 scenario-level risk records, and generated 16,384 pixel-level risk records. Scenario screening assigned 76 records to `reliable`, 25 to `caution`, and 13 to `high-risk`. As a validation check, all 24 known Phase 13-like `location2` + `r300y` cases were flagged as `caution` or `high-risk`.

The Phase 15 labels are deterministic screening labels. They should not be interpreted as calibrated probabilities, Bayesian uncertainty, or a replacement for formal uncertainty calibration.

### Scenario risk category counts

![Phase 15 scenario risk category counts](analysis/phase15_reliability_screening/figures/scenario_risk_category_counts.png)

### Risk component heatmap

![Phase 15 risk component heatmap](analysis/phase15_reliability_screening/figures/risk_component_heatmap.png)

### Pixel risk map example

![Phase 15 pixel risk map example](analysis/phase15_reliability_screening/figures/pixel_risk_map_example.png)

## Phase 16 Reliability-Aware Warning Rules and Applicability Boundary

Phase 16 provides the first implementation of reliability-aware warning rules and an applicability boundary for the current Phase 10 recommended model. It translates Phase 15 deterministic reliability-screening labels into application-oriented warning guidance without retraining, architecture changes, Phase 10 loss changes, `boundary_weight` tuning, `boundary_band_pixels` tuning, or a new sweep.

The Phase 16 scenario warning counts are 76 `reliable`, 25 `caution`, and 13 `high-risk`. The 13 high-risk warning cases match the Phase 15 high-risk cases. Pixel warning counts are 5,714 `reliable`, 8,805 `caution`, and 1,865 `high-risk`.

The warning labels are deterministic operational interpretation labels. They should not be read as calibrated probabilities, Bayesian uncertainty estimates, formal confidence intervals, or a substitute for a calibration design.

### Warning level counts

![Phase 16 warning level counts](analysis/phase16_warning_rules/figures/warning_level_counts.png)

### Warning action matrix

![Phase 16 warning action matrix](analysis/phase16_warning_rules/figures/warning_action_matrix.png)

### Applicability boundary summary

![Phase 16 applicability boundary summary](analysis/phase16_warning_rules/figures/applicability_boundary_summary.png)

### Pixel warning map example

![Phase 16 pixel warning map example](analysis/phase16_warning_rules/figures/pixel_warning_map_example.png)

## Phase 17 Reliability-Aware Warning Framework Synthesis

Phase 17 is a synthesis/documentation phase, not a new experiment phase. It integrates the Phase 12 reliability and applicability diagnosis, Phase 13 representative failure-case visualization, Phase 14 confidence/disagreement proxy diagnostics, Phase 15 reliability screening and spatial risk mapping, and Phase 16 warning-rule and applicability-boundary guidance into one reliability-aware warning framework narrative.

The synthesis frames the project as rapid flood-depth prediction plus reliability diagnosis, failure-mode interpretation, confidence proxy diagnostics, spatial risk mapping, and warning-rule guidance. Phase 17 does not retrain models, modify architecture, modify the Phase 10 loss, tune `boundary_weight` or `boundary_band_pixels`, or open a new sweep. The recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`.

See `docs/phase17_reliability_warning_framework_synthesis.md` for the synthesis document.

## Phase 18 Manuscript-Oriented Reliability-Aware Warning Layer

Phase 18 is a manuscript-writing and synthesis phase, not a new experiment phase. It converts the completed Phase 12-17 reliability-aware warning framework into manuscript-ready material for "Reliability-Aware Warning Layer for Urban Flood Surrogate Prediction" without retraining, model changes, Phase 10 loss changes, boundary-parameter tuning, or new result generation. See `docs/manuscript_reliability_aware_warning_layer.md`.

## Phase 19 Manuscript Structure and Paper-Ready Consolidation

Phase 19 is a manuscript-structure and submission-consolidation phase, not a new experiment phase. It converts the completed Phase 12-18 reliability-aware warning framework and manuscript notes into a paper-ready outline and submission-oriented planning document covering positioning, candidate titles, abstract logic, section structure, figure/table inventory, contribution statements, limitations, submission positioning, and immediate writing tasks. See `docs/manuscript_structure_and_submission_consolidation.md`.

## Phase 20 Manuscript Draft Assembly

Phase 20 is a manuscript draft assembly phase, not a new experiment phase. It assembles the Phase 18 and Phase 19 manuscript-oriented materials into the first full draft skeleton for "Reliability-Aware Urban Flood Warning." See `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`.

## Phase 21 Manuscript Evidence and Figure/Table Alignment

Phase 21 is an evidence-alignment phase, not a new experiment phase. It maps manuscript claims to existing evidence sources, figures, tables, JSON/CSV outputs, and findings documents before full manuscript expansion. See `docs/manuscript_evidence_figure_table_alignment.md`.

## Phase 22 Manuscript Full Draft Expansion

Phase 22 is a manuscript full-draft expansion phase, not a new experiment phase. It expands the Phase 20 manuscript skeleton into a fuller academic draft using the Phase 21 evidence-alignment document. See `docs/manuscript_full_draft_reliability_aware_urban_flood_warning.md`.

## Phase 23 Reliability-Aware Warning Case Study and Application Prototype

Phase 23 is an application-prototype phase, not a model-tuning phase. It converts the Phase 15 reliability screening, Phase 16 warning rules, and existing Phase 10 forecast map arrays into a representative warning-oriented case study covering one `reliable`, one `caution`, and one `high-risk` case.

Selected cases:

- `reliable`: `location1|r100y_p0.5_d3h|6`
- `caution`: `location2|r300y_p0.6_d3h|6`
- `high-risk`: `location2|r300y_p0.8_d3h|0`

The prototype demonstrates that the framework has moved beyond pure flood-depth prediction toward rapid prediction, reliability screening, scenario-level warning classification, pixel-level risk visualization, case-specific warning explanation, and applicability-boundary interpretation. See `docs/phase23_reliability_warning_case_study_findings.md`.

## Phase 24 Physical Consistency Deepening and Process Diagnostics

Phase 24 is a physical-consistency diagnostic phase for the existing Phase 10 recommended outputs. It links Phase 15/16 warning-risk labels with process-level behavior: false-dry rate, wet-area contraction, peak-depth underprediction, wet-connectivity loss, temporal volume response, and overall volume bias.

The diagnosis confirms that high-risk cases are physically less consistent than reliable cases. Warning-level means for `reliable` / `caution` / `high-risk` are 0.125 / 0.268 / 0.444 for `false_dry_rate`, 0.046 / 0.135 / 0.383 for `wet_area_contraction`, 0.024 m / 0.241 m / 1.381 m for `peak_depth_underprediction`, 0.197 / 0.240 / 1.000 for `connectivity_loss_indicator`, and -0.040 / -0.145 / -0.448 for `relative_volume_bias`. Topographic consistency was skipped because no shape-compatible DEM/static elevation layer was found.

The Phase 25 implication was a targeted model refinement around false-dry reduction and wet-area preservation while keeping the Phase 10 boundary-band settings fixed. A full SWE/PINN residual is not recommended unless compatible velocity, flux, boundary, DEM, and source-sink information become available.

## Phase 25 Physics-Consistency Guided Surrogate Refinement: Target-Wet Recall Consistency

Phase 25 adds a config-gated `target_wet_recall_consistency` loss to reduce false-dry behavior and wet-area contraction. It keeps the Phase 10 boundary-band settings fixed at `boundary_band_pixels = 1` and `boundary_weight = 2.0`.

The Phase 25 loss setting is:

- `target_wet_recall_consistency.weight = 0.02`
- `threshold = 0.05`
- `temperature = 0.02`
- `eps = 1e-6`

Across `seed123`, `seed42`, and `seed202`, Phase 25 consistently improved standard test metrics versus Phase 10. Mean deltas were `RMSE = -0.007057`, `MAE = -0.001519`, `wet/dry IoU = +0.076670`, `rollout stability = +0.001035`, and `step RMSE std = -0.001071`.

Aligned physical metrics also moved in the intended direction for the main diagnosed failure modes: mean deltas were `false_dry_rate = -0.111321`, `wet_area_contraction = -0.079104`, `relative_volume_bias = +0.105093`, `peak_depth_underprediction = -0.014962`, `RMSE = -0.007244`, and `MAE = -0.001885`. False-dry rate and wet-area contraction improved in all three seeds, with especially strong reductions in high-risk cases.

Phase 25 is a strong three-seed positive candidate and a credible targeted refinement over the Phase 10 baseline. It is not a complete physical-consistency solution: `false_wet_rate` increased slightly on average, `connectivity_loss_indicator` was not consistently improved, and the model still does not implement a full SWE/PINN residual.

Representative Phase 25 figures:

![Phase 25 standard metric deltas across three seeds](analysis/phase25_target_wet_recall_comparison/figures/phase25_standard_metric_deltas_three_seeds.png)

![Phase 25 aligned physical metric deltas across three seeds](analysis/phase25_target_wet_recall_comparison/figures/phase25_aligned_physical_deltas_three_seeds.png)

## Historical Qualitative Examples

The figures below are earlier-stage qualitative comparisons retained for visual reference. They are not the current primary evidence for the project state; the current project state is summarized above through the Phase 30 strong-physics boundary synthesis and Phase 31 physics input recovery readiness diagnostics.

<details>
<summary>Expand earlier-stage qualitative flood-map examples</summary>

### Baseline vs Phase 1

#### Spatial Inundation Comparison

![Baseline vs Phase 1 spatial comparison](assets/images/comparison_epoch19_step11_unified.png)

#### Region-Averaged Process Comparison

![Baseline vs Phase 1 process comparison](assets/images/comparison_timeseries_epoch19_regionavg.png)

### Phase 2A vs Phase 2B h16 on Difficult Case (`seed202`)

#### Spatial Inundation Comparison

![Phase 2A vs Phase 2B h16 seed202 spatial comparison](assets/images/comparison_maps_seed202_test_batch0000.png)

#### Region-Averaged Process Comparison

![Phase 2A vs Phase 2B h16 seed202 process comparison](assets/images/comparison_timeseries_seed202_test_batch0000.png)

### Phase 2A vs Phase 2B h16 on Favorable Case (`seed42`)

#### Spatial Inundation Comparison

![Phase 2A vs Phase 2B h16 seed42 spatial comparison](assets/images/comparison_maps_seed42_test_batch0000.png)

#### Region-Averaged Process Comparison

![Phase 2A vs Phase 2B h16 seed42 process comparison](assets/images/comparison_timeseries_seed42_test_batch0000.png)

</details>


## Research Roadmap

```mermaid
flowchart TD
    A["Completed Mainline<br/>Rapid flood-depth prediction<br/>reliability-aware warning framework<br/>Phases 1-23"]:::completed
    B["Physical Consistency Evidence<br/>Failure diagnosis<br/>target-wet recall<br/>physical proxy diagnostics<br/>Phases 24-25"]:::completed
    C["Strong Physics Boundary<br/>Level 4+ proxy diagnostics supported<br/>Level 5 SWE/PINN not supported<br/>Phases 26 + 30-49"]:::boundary
    D["Volume-Response Loss Lessons<br/>Phase 27 underresponse-only mixed<br/>Phase 28 failure diagnosis<br/>Phase 29 tolerance-band mixed<br/>volume-response partially repaired<br/>trade-off remains unacceptable"]:::diagnosis
    E["Current Decision<br/>Phase 49 warning framework complete<br/>conservative diagnostic screening labels<br/>not calibrated probabilities"]:::current
    F["Next Research Direction<br/>Phase 50 evidence synthesis or reviewed expansion decision<br/>no uncontrolled expansion<br/>no Level 5 claim"]:::current

    A --> B --> C --> D --> E --> F

    classDef completed fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    classDef boundary fill:#fff3e0,stroke:#ef6c00,color:#7a3b00
    classDef diagnosis fill:#fce4ec,stroke:#ad1457,color:#6a0032
    classDef current fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
```

Detailed implementation records and phase-by-phase evidence are maintained in docs/experiment_index.md.


## Documentation

For the current staged experiment record, see:

- `docs/project_status.md`
- `docs/experiment_index.md`
- `docs/phase6_pilot_a_results.md`
- `docs/phase7_adapt010_results.md`
- `docs/phase8_batch1_results.md`
- `docs/phase8_tradeoff_positioning.md`
- `docs/phase9_interpretability_findings.md`
- `docs/phase10_margin_aware_findings.md`
- `docs/phase12_reliability_applicability_plan.md`
- `docs/phase12_reliability_applicability_findings.md`
- `docs/phase13_failure_case_visual_summary_plan.md`
- `docs/phase13_failure_case_visual_summary_findings.md`
- `docs/phase14_uncertainty_confidence_diagnostics_plan.md`
- `docs/phase14_uncertainty_confidence_diagnostics_findings.md`
- `docs/phase15_reliability_screening_risk_mapping_plan.md`
- `docs/phase15_reliability_screening_risk_mapping_findings.md`
- `docs/phase16_reliability_warning_applicability_plan.md`
- `docs/phase16_reliability_warning_applicability_findings.md`
- `docs/phase17_reliability_warning_framework_synthesis.md`
- `docs/manuscript_reliability_aware_warning_layer.md`
- `docs/manuscript_structure_and_submission_consolidation.md`
- `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`
- `docs/manuscript_evidence_figure_table_alignment.md`
- `docs/manuscript_full_draft_reliability_aware_urban_flood_warning.md`
- `docs/phase23_reliability_warning_case_study_plan.md`
- `docs/phase23_reliability_warning_case_study_findings.md`
- `docs/phase24_physical_consistency_deepening_plan.md`
- `docs/phase24_physical_consistency_deepening_findings.md`
- `docs/phase25_physics_consistency_guided_refinement_plan.md`
- `docs/phase25_target_wet_recall_implementation_note.md`
- `docs/phase25_target_wet_recall_pilot_findings.md`
- `docs/phase25_seed42_guardrail_findings.md`
- `docs/phase25_three_seed_target_wet_recall_synthesis_findings.md`
- `docs/phase27_conservative_volume_response_consistency_plan.md`
- `docs/phase27_seed42_volume_response_pilot_findings.md`
- `docs/phase30_strong_physics_boundary_synthesis_plan.md`
- `docs/phase30_strong_physics_boundary_synthesis.md`
- `docs/phase34_pilot_threshold_formalization_findings.md`
- `docs/phase35_manhole_false_dry_guardrail_pilot_plan.md`
- `docs/phase36_manhole_false_dry_guardrail_code_smoke_findings.md`
- `docs/phase37_seed42_training_authorization_review_findings.md`


## Dataset

This project uses the **UrbanFlood24 Lite** dataset.

Expected dataset directory:

```text
data/
  urbanflood24_lite/
    train/
    test/
```

The dataset includes:

- dynamic flood depth sequences: `flood.npy`
- rainfall forcing sequences: `rainfall.npy`
- static geospatial factors:
  - `absolute_DEM.npy`
  - `impervious.npy`
  - `manhole.npy`


## Task Definition

This project studies **multi-step flood process prediction**.

### Inputs

- past flood sequence
- past rainfall sequence
- future rainfall sequence
- static maps

### Output

- future flood depth sequence

In the current setup, the model uses:

- `input_steps = 12`
- `pred_steps = 12`


## Method

### Backbone

The forecasting backbone is based on a U-Net + TCN style spatiotemporal model.

### Physics-guided strategy

This repository currently has:

- a stable baseline built on U-Net + TCN
- stable physics guidance from non-negativity loss and wet/dry consistency loss
- optional architecture-level rainfall conditioning modules used for staged research experiments

### Stable baseline

The stable baseline path keeps the backbone unchanged and preserves the two stable physics-guided losses:

- non-negativity loss
- wet/dry consistency loss

### Optional rainfall conditioning

Architecture-level rainfall conditioning remains optional and config-driven. Existing training scripts and configs remain usable when the `rainfall_conditioning` block is omitted or disabled.

## Environment

Example setup:

```bash
conda create -n your_env_name python=3.8 -y
conda activate your_env_name
pip install -r requirements.txt
```

## Training

The current main training entry is:

```bash
python scripts/train_model.py --config <config_path>
```

### Example: stable loss-guided baseline (40 epochs, seed42)

```bash
python scripts/train_model.py --config configs/train_phase2_loss_only_40e_seed42.json
```

### Example: M3 mainline reference (40 epochs, seed42)

```bash
python scripts/train_model.py --config configs/train_phase2b_temporal_gate_h16_40e_seed42.json
```

### Example: Phase 3.3 protected response-split control (40 epochs, seed42)

```bash
python scripts/train_model.py --config configs/train_phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42.json
```

### Example: Phase 6 Pilot A adaptive scalar variant (5 epochs, seed42)

```bash
python scripts/train_model.py --config configs/train_phase6_pilot_a_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt025_5e_seed42.json
```

### Example: Phase 8 adaptive candidate validation (40 epochs, seed42)

```bash
python scripts/train_model.py --config configs/train_phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42.json
```

### Example: debug run

```bash
python scripts/train_model.py --config configs/train_phase2b_temporal_gate_debug.json
```

Additional experiment settings are provided under `configs/`.


## Evaluation and Visualization

Current evaluation combines staged validation metrics, paired qualitative checks, and Phase 12 reliability/applicability diagnostics.

The historical comparison scripts remain useful for inspecting representative cases and earlier visual outputs:

```bash
python compare_maps.py
python compare_timeseries.py
```

Phase 12 and later stages add reliability-focused diagnostic and screening scripts:

```bash
python scripts/analyze_phase12_reliability.py
python scripts/plot_phase12_reliability.py
python scripts/visualize_phase13_failure_cases.py
python scripts/analyze_phase14_confidence.py
python scripts/screen_phase15_reliability.py
python scripts/build_phase16_warning_rules.py
python scripts/build_phase23_warning_case_study.py
python scripts/analyze_phase24_physical_consistency.py
python scripts/compare_phase25_target_wet_recall_aligned.py
python scripts/compare_phase27_volume_response_seed42.py
python scripts/compare_phase29_tolerance_band_volume_seed42.py
python scripts/audit_phase31_dataset_physics_inputs.py
python scripts/inspect_phase31_static_maps.py
python scripts/build_phase31_domain_boundary_masks.py
python scripts/analyze_phase31_masked_physical_errors.py
```

Generated figures and analysis outputs are organized under:

- `docs/figures/phase2_qualitative/` for earlier qualitative comparisons
- `analysis/phase12_reliability/figures/` for current reliability diagnostics
- `analysis/phase13_failure_cases/figures/` for representative failure-case visual summaries
- `analysis/phase14_confidence/figures/` for confidence proxy diagnostics
- `analysis/phase15_reliability_screening/figures/` for reliability-screening and risk-mapping outputs
- `analysis/phase16_warning_rules/figures/` for reliability-aware warning-rule and applicability-boundary outputs
- `analysis/phase23_warning_case_study/figures/` for representative warning case-study prototype outputs
- `analysis/phase24_physical_consistency/figures/` for physical-consistency and warning-risk linkage diagnostics
- `analysis/phase25_target_wet_recall_comparison/figures/` for Phase 25 versus Phase 10 summary comparison figures
- `analysis/phase26_strong_physics_constraint_feasibility/` for Phase 26 physics-input audit and conservation-proxy diagnostic outputs
- `analysis/phase27_conservative_volume_response_consistency/` for Phase 27 seed42 conservative volume-response pilot outputs
- `analysis/phase28_volume_response_loss_diagnosis/` for Phase 28 volume-response loss failure diagnosis outputs
- `analysis/phase29_tolerance_band_volume_consistency/` for Phase 29 seed42 tolerance-band volume consistency pilot outputs
- `analysis/phase31_physics_input_recovery_readiness/` for Phase 31 physics input recovery, domain/boundary mask, and masked physical diagnostic readiness outputs
- `analysis/phase32_domain_boundary_aware_design/` for Phase 32 domain-/boundary-aware physical-consistency design guardrail outputs
- `analysis/phase33_seed42_pilot_readiness/` for Phase 33 seed42 pilot readiness-review outputs
- `analysis/phase34_pilot_thresholds/` for Phase 34 pilot threshold-formalization outputs
- `analysis/phase37_seed42_training_authorization/` for Phase 37 seed42 training authorization review outputs
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/` for Phase 38 seed42 pilot guardrail-evaluation outputs
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/` for Phase 39 failed-pilot trade-off diagnostic outputs
- `analysis/phase40_failed_pilot_design_review/` for Phase 40 failed-pilot design-review and next-constraint decision outputs
- `analysis/phase41_swe_data_readiness_audit/` for Phase 41 SWE data readiness audit outputs
- `analysis/phase42_hydrodynamic_export_requirements/` for Phase 42 hydrodynamic export requirement specification outputs
- `analysis/phase43_urbanflood24_full_dataset_inspection/` for Phase 43 UrbanFlood24 full dataset inspection outputs
- `docs/phase44_urbanflood24_full_level4plus_replanning.md` for Phase 44 UrbanFlood24 full Level 4+ replanning
- `docs/phase45_full_dataset_indexing_lightweight_adapter_findings.md` for Phase 45 full dataset indexing and lightweight adapter preparation
- `analysis/phase45_full_dataset_indexing/` for Phase 45 dataset index, static geodata index, summary, and adapter design outputs
- `docs/phase46_dataloader_smoke_downsample_tiling_feasibility_findings.md` for Phase 46 no-training dataloader smoke and downsample/tiling feasibility findings
- `analysis/phase46_dataloader_smoke_downsample_tiling/` for Phase 46 sample shape, downsample, tiling, batch smoke, and memory-safety outputs
- `docs/phase47_controlled_full_dataset_downsample_baseline_findings.md` for Phase 47 controlled full-dataset `128 x 128` downsample baseline findings
- `analysis/phase47_controlled_downsample_baseline/` for Phase 47 metrics, training summary, runtime/memory notes, and config snapshot
- `docs/phase48_full_dataset_reliability_physical_proxy_diagnostics_findings.md` for Phase 48 full-dataset reliability and physical proxy diagnostic findings
- `analysis/phase48_full_dataset_reliability_physical_proxy/` for Phase 48 reliability summaries, warning labels, and physical proxy diagnostic outputs
- `docs/phase49_full_dataset_warning_framework_extension_findings.md` for Phase 49 full-dataset warning framework extension findings
- `analysis/phase49_full_dataset_warning_framework/` for Phase 49 warning summaries, scenario actions, rule tables, templates, and high-risk review outputs


## Current Project Status

The repository has completed the main Phase 2-3 architecture comparison cycle, closed the Phase 6 `adapt025` pilot as negative/neutral, established Phase 7/8 `adapt010` as the active adaptive candidate before margin-aware refinement, completed Phase 9 interpretability diagnosis, completed the Phase 10 margin-aware refinement intervention, completed the Phase 12-16 reliability-aware warning layer, completed the Phase 17-22 manuscript synthesis and drafting sequence, completed the Phase 23 reliability-aware warning case-study prototype, completed Phase 24 physical-consistency deepening diagnostics, completed Phase 25 target-wet recall consistency refinement through three-seed synthesis, completed Phase 26 strong-physics feasibility audit and conservation-proxy diagnostics, completed the Phase 27 seed42 conservative volume-response consistency pilot, completed the Phase 28 volume-response loss failure diagnosis, completed the Phase 29 seed42 tolerance-band volume consistency pilot, completed the Phase 30 strong-physics boundary synthesis, completed Phase 31 physics input recovery readiness diagnostics, completed Phase 32 domain-/boundary-aware physical consistency design guardrails, completed Phase 33 seed42 pilot readiness review, completed Phase 34 pilot threshold formalization, completed Phase 35 manhole false-dry guardrail pilot planning, completed Phase 36 manhole false-dry guardrail code/smoke-test implementation, completed Phase 37 seed42 training authorization review, completed Phase 38 seed42 pilot training plus guardrail evaluation with rejection, completed Phase 39 diagnostic-only failed-pilot trade-off analysis, completed Phase 40 failed-pilot design review and next-constraint decision, completed Phase 41 no-training SWE data readiness audit, completed Phase 42 no-training hydrodynamic export requirement specification, completed Phase 43 no-training UrbanFlood24 full dataset inspection, completed Phase 44 UrbanFlood24 full Level 4+ replanning, completed Phase 45 no-training full-dataset indexing and lightweight adapter preparation, completed Phase 46 no-training dataloader smoke testing with downsample/tiling feasibility checks, completed the Phase 47 controlled full-dataset `128 x 128` downsample `seed42` 10e baseline pilot, completed Phase 48 no-training full-dataset reliability and physical proxy diagnostics, and completed Phase 49 no-training full-dataset warning framework extension.

Current project-level conclusions:

- **M3 `f025` remains the overall best-balanced mainline reference**
- **Phase 3.3 `af025` remains the strongest static structured refinement**
- **Phase 6 Pilot A `adapt025` is closed as a negative/neutral result**
- **Phase 7/8 `adapt010` remains the active adaptive candidate before margin-aware refinement**
- **Phase 9 diagnosed the key wet/dry IoU issue as a mixed, margin-region, step-dependent trade-off**
- **Phase 10 boundary-band weighted wet/dry consistency refinement is the current recommended margin-aware setting**
- **Recommended Phase 10 setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`**
- **This setting passed test-facing confirmation on `seed123`, `seed42`, and `seed202`**
- **Phase 12 completed the first-pass reliability/applicability diagnosis of the Phase 10 recommended model**
- **Main Phase 12 caution zones: exact wet/dry boundary cells, shallow threshold-adjacent cells, moderate-to-deep depths, high-intensity `location2` cases, and local peak-depth extremes**
- **Phase 13 completed representative worst-timestep visual summaries for the highest-ranked failure cases**
- **Main Phase 13 finding: top failures collapse into two high-intensity `location2` target scenarios repeated across seeds, with systematic underprediction, reduced wet extent, local peak-depth underprediction, and false-dry dominated mismatch**
- **Phase 14 completed first-pass confidence proxy diagnostics**
- **Main Phase 14 finding: confidence margin is useful for wet/dry classification risk, while cross-seed disagreement is only an auxiliary proxy and not a strong standalone scenario-error predictor**
- **Phase 14 does not provide calibrated probabilistic uncertainty**
- **Phase 15 completed first-pass reliability screening and spatial risk mapping**
- **Phase 15 generated 114 scenario-level risk records and 16,384 pixel-level risk records from 57 Phase 10 map files**
- **Phase 15 scenario labels: 76 reliable, 25 caution, and 13 high-risk**
- **All 24 known Phase 13-like `location2` + `r300y` cases were flagged as `caution` or `high-risk`**
- **Phase 15 screening labels are deterministic labels, not calibrated probabilities or Bayesian uncertainty**
- **Phase 16 completed first-pass reliability-aware warning rules and applicability boundary guidance**
- **Phase 16 scenario warnings: 76 reliable, 25 caution, and 13 high-risk**
- **Phase 16 pixel warnings: 5,714 reliable, 8,805 caution, and 1,865 high-risk**
- **The 13 Phase 16 high-risk warning cases match the Phase 15 high-risk cases**
- **Phase 16 warning labels are deterministic operational interpretation labels, not calibrated probabilities, Bayesian uncertainty, or formal confidence intervals**
- **Phase 17 completed the synthesis of Phase 12-16 into a reliability-aware warning framework narrative for manuscript writing, README narrative, and project positioning**
- **Phase 17 is documentation synthesis only: no retraining, architecture change, Phase 10 loss change, boundary-parameter tuning, or new sweep**
- **Phase 18 has produced manuscript-ready reliability-aware warning layer material from the completed Phase 12-17 framework**
- **Phase 18 is writing/synthesis only: no retraining, architecture change, Phase 10 loss change, boundary-parameter tuning, new sweep, or new result generation**
- **Phase 19 has produced a paper-ready manuscript structure and submission-consolidation document from the completed Phase 12-18 materials**
- **Phase 19 is manuscript-structure consolidation only: no retraining, architecture change, Phase 10 loss change, boundary-parameter tuning, new sweep, or new result generation**
- **Phase 20 has produced the first full manuscript draft skeleton from the Phase 18-19 manuscript-oriented materials**
- **Phase 20 is manuscript draft assembly only: no retraining, architecture change, Phase 10 loss change, boundary-parameter tuning, new sweep, or new result generation**
- **Phase 21 has produced a claim-to-evidence and figure/table alignment document for the manuscript**
- **Phase 21 is evidence alignment only: no retraining, architecture change, Phase 10 loss change, boundary-parameter tuning, new sweep, new result generation, or new uncertainty claim**
- **Phase 22 has produced a fuller academic manuscript draft from the Phase 20 skeleton and Phase 21 evidence alignment**
- **Phase 22 is manuscript full-draft expansion only: no retraining, architecture change, Phase 10 loss change, boundary-parameter tuning, new sweep, new result generation, invented references, or unsupported claims**
- **Phase 23 has produced a representative reliability-aware warning case-study prototype**
- **Phase 23 selected one `reliable`, one `caution`, and one `high-risk` case for warning-oriented interpretation**
- **Phase 23 demonstrates rapid prediction, reliability screening, scenario-level warning classification, pixel-level risk visualization, case-specific warning explanation, and applicability-boundary interpretation**
- **Phase 23 is an application-prototype phase only: no retraining, architecture change, Phase 10 loss change, boundary-parameter tuning, new sweep, metric-chasing experiment, or new prediction generation**
- **Phase 24 has diagnosed physical consistency of the existing Phase 10 recommended outputs**
- **Main Phase 24 finding: high-risk cases are statistically worse and physically less consistent, with stronger false-dry behavior, wet-area contraction, peak-depth underprediction, connectivity loss, and volume under-response**
- **Phase 24 risk-score correlations: `false_dry_rate` = 0.913, `wet_area_contraction` = 0.862, `peak_depth_underprediction` = 0.856, and `connectivity_loss_indicator` = 0.539**
- **Phase 24 topographic consistency was skipped because no shape-compatible DEM/static elevation layer was found**
- **Phase 24 is diagnostic only: no retraining, architecture change, Phase 10 loss change, boundary-parameter tuning, new sweep, metric-chasing experiment, traffic-impact modeling, or new prediction generation**
- **Phase 25 completed Physics-Consistency Guided Surrogate Refinement: Target-Wet Recall Consistency**
- **Phase 25 keeps Phase 10 boundary-band settings fixed: `boundary_band_pixels = 1`, `boundary_weight = 2.0`**
- **Phase 25 adds config-gated `target_wet_recall_consistency` with `weight = 0.02`, `threshold = 0.05`, `temperature = 0.02`, and `eps = 1e-6`**
- **Mean Phase 25 standard test deltas versus Phase 10: `RMSE = -0.007057`, `MAE = -0.001519`, `wet/dry IoU = +0.076670`, `rollout stability = +0.001035`, and `step RMSE std = -0.001071`**
- **Mean aligned physical deltas versus Phase 10: `false_dry_rate = -0.111321`, `wet_area_contraction = -0.079104`, `relative_volume_bias = +0.105093`, `peak_depth_underprediction = -0.014962`, `RMSE = -0.007244`, and `MAE = -0.001885`**
- **Phase 25 is a strong three-seed positive candidate for reducing false-dry behavior and wet-area contraction, but not a complete physical-consistency solution**
- **Phase 26 completed Strong Physics Constraint Feasibility Audit and Conservation-Proxy Diagnostics**
- **Phase 26 found partial support for Level 4 conservation-proxy diagnostics, unclear support for Level 4 conservation-aware loss design, and no support for Level 5 full SWE/PINN residual constraints**
- **Phase 26 conservation-proxy diagnostics indicate aggregate volume-response improvement for Phase 25 versus Phase 10 w20, while preserving the guardrail that Phase 25 is not a strict timestep-wise conservation solution**
- **Phase 27 completed a seed42 conservative volume-response consistency pilot**
- **Phase 27 improved standard seed42 test metrics and several under-response-related proxies versus Phase 25 seed42**
- **Phase 27 did not confirm the primary volume-response objective because aggregate and timestep-wise absolute relative volume bias worsened**
- **Phase 27 decision: `remain_seed42_positive_only`; no `seed123` / `seed202` confirmation, no Phase 27 weight sweep, no strict conservation claim, and no SWE/PINN claim**
- **Phase 28 completed diagnostic-only analysis of the Phase 27 volume-response objective failure**
- **Phase 28 found that the Phase 27 volume-bias worsening was dominated by `dry_or_threshold` target-depth-bin volume accumulation rather than false-wet expansion or already-wet amplification**
- **Phase 28 evidence: `delta_volume_bias_total = +6974.12`, false-wet volume excess delta = `-184.071`, already-wet amplification = `+1396.20`, and `dry_or_threshold` contribution = `+5362.82` or about `76.9%` of total delta volume bias**
- **Phase 28 decision: stop direct expansion of the Phase 27 underresponse-only loss; only consider tolerance-band volume consistency through a new plan**
- **Phase 28 is diagnostic only: no training, architecture change, loss change, config change, `seed123` / `seed202` confirmation, sweep, strict conservation claim, full mass-conservation claim, or SWE/PINN claim**
- **Phase 29 completed a seed42 mixed tolerance-band volume consistency pilot**
- **Phase 29 partially repaired Phase 27 aggregate and mean-step absolute relative volume bias and reduced `dry_or_threshold` contribution**
- **Phase 29 worsened all listed standard metrics and worsened false-dry volume loss, false-wet volume excess, and peak-depth underprediction**
- **Phase 29 decision: `remain_seed42_only_pending_revision`; no `seed123` / `seed202`, no tolerance or weight sweep, no tolerance-band success claim, no strict conservation claim, no full mass-conservation claim, and no SWE/PINN claim**
- **Phase 30 completed documentation-only strong-physics boundary synthesis**
- **Phase 30 defines the current position as Level 4 conservation-proxy / physical-consistency-guided surrogate support, not Level 5 strong physics**
- **Phase 30 explicitly excludes strict mass conservation, full hydrodynamic closure, and full SWE/PINN residual consistency claims**
- **Phase 30 decision: pause Phase 27/29 seed expansion and volume-response loss sweeps; prioritize manuscript, README, and research narrative consolidation next**
- **Phase 31 completed diagnostic-only physics input recovery readiness**
- **Phase 31 confirms Level 4+ structured physical proxy diagnostics are supported by recovered shape-compatible static maps, domain masks, boundary-ring/interior masks, sample-to-location mapping, and masked physical diagnostics**
- **Phase 31 keeps Level 5 unsupported: no aligned velocity/flux fields, no boundary/source-sink aligned fields, no explicit `dx/dy`, inferred-only `dt`, and no full hydrodynamic state variables**
- **Phase 31 masked diagnostics reinforce that Phase 29 is mixed, not successful**
- **Phase 32 completed plan-first Level 4+ domain-/boundary-aware physical consistency design guardrails**
- **Phase 32 formalized 20 guardrail metrics and 12 stop/go criteria**
- **Phase 32 is design/diagnostic-only: no training, loss modification, config modification, or architecture change**
- **Current Phase 32 decision: `design_ready_no_training_yet`; no immediate training, no loss modification, no `seed123` / `seed202`, and no sweep**
- **Phase 33 completed diagnostic-only seed42 pilot readiness review under the Phase 32 guardrail framework**
- **Phase 33 reviewed 5 pilot options and 15 readiness criteria**
- **Phase 33 recommended future candidate: `manhole_nonzero_false_dry_guardrail`**
- **Current Phase 33 decision: `pilot_design_ready_but_training_not_started`; `training_authorized = false`**
- **Phase 33 blocks training until numeric acceptance thresholds, numeric rejection thresholds, and full Phase 25 / Phase 27 / Phase 29 baseline acceptance/rejection criteria are fixed**
- **Phase 34 completed threshold-formalization only for a possible future `manhole_nonzero_false_dry_guardrail` seed42 pilot**
- **Phase 34 formalized 23 baseline metric rows, 14 acceptance thresholds, 9 rejection thresholds, and 7 readiness rows**
- **Current Phase 34 decision: `thresholds_formalized_training_still_blocked`; `training_authorized = false`; `next_allowed_step = pilot_implementation_plan`**
- **Phase 34 AT01 fixes the `manhole_nonzero_valid` `false_dry_rate` threshold at `0.1172229713`, requiring performance below Phase 29 and no higher than Phase 27**
- **Phase 34 RT01 hard-rejects the Phase 29 trade-off pattern where absolute relative volume-bias proxy improves while RMSE, MAE, false-dry rate, and false-wet rate all worsen versus Phase 27**
- **Phase 34 AT13 makes volume-bias proxy improvement conditional and not sufficient alone, while AT14 / RT09 preserve the Level 4+ proxy claim boundary**
- **Phase 35 completed a pilot implementation plan only for `manhole_nonzero_false_dry_guardrail`**
- **Phase 35 does not implement losses, create configs, modify model code, or run training**
- **Current Phase 35 status: `implementation_plan_ready_code_next`; `training_authorized = false`; next allowed step is code/smoke-test implementation, not training**
- **Phase 35 target remains `manhole_nonzero_valid` `false_dry_rate`, with AT01 threshold `0.1172229713`**
- **Phase 36 implemented and smoke-tested the config-gated `manhole_nonzero_false_dry_guardrail` code path and guardrail checker**
- **Current Phase 36 decision: `code_smoke_ready_training_still_blocked`; `training_authorized = false`; `training_executed = false`**
- **Phase 36 did not run `seed42`, `seed123`, or `seed202`, and did not claim pilot success**
- **Phase 37 completed diagnostic seed42 training authorization review**
- **Current Phase 37 decision: `seed42_training_authorized_next_phase`; `training_authorized_next_phase = true`; `training_executed = false`; required checks passed `18 / 18`**
- **Phase 37 did not train; it authorized only `configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json` for the next phase**
- **Phase 37 required post-training evaluation and guardrail checking; Phase 38 completed those steps**
- **The Phase 37 seed-expansion block is now superseded by the Phase 38 rejection block**
- **Phase 38 ran the single authorized seed42 pilot, completed test evaluation, completed guardrail evaluation, and rejected the pilot**
- **Current Phase 38 decision: `seed42_pilot_rejected`; training completed; test evaluation completed; guardrail evaluation completed**
- **Phase 38 triggered RT01, RT05, and RT07, with failed checks AT02, AT03, AT04, AT06, AT07, AT08, AT09, and AT10**
- **Phase 38 is useful negative evidence, not a training execution failure; the `manhole_nonzero_false_dry_guardrail` design is not accepted**
- **Phase 39 completed diagnostic-only trade-off analysis for the rejected Phase 38 seed42 pilot**
- **Current Phase 39 decision: `tradeoff_diagnosis_completed_with_missing_optional_inputs`; Phase 38 remains `seed42_pilot_rejected`**
- **Phase 39 recorded `failed_acceptance_count = 8`, `triggered_rejection_count = 3`, `comparison_rows = 13`, `region_rows = 5`, and `scenario_rows = 19`**
- **Phase 39 found that narrow `manhole_nonzero_valid` false-dry proxy improvement did not translate into broader valid-domain, regional guardrail, and standard-metric success**
- **Phase 39 scenario diagnostics are Phase38-only because per-batch/scenario Phase25/Phase27/Phase29 baselines are unavailable**
- **Phase 40 completed failed-pilot design review and next-constraint decision**
- **Current Phase 40 decision: `pause_loss_redesign_move_to_swe_data_readiness`; `training_authorized = false`; `next_recommended_phase = phase41_swe_data_readiness_audit`**
- **Phase 40 evaluated 4 options and 13 criteria rows**
- **Phase 40 pauses proxy-loss redesign after repeated trade-off evidence from Phase 27, Phase 29, and Phase 38**
- **Phase 41 completed the no-training SWE data readiness audit**
- **Current Phase 41 decision: `readiness_decision = readiness_uncertain_requires_external_data_export`; `level5_supported = false`; `external_hydrodynamic_model_export_needed = true`; `level4_proxy_supported = true`**
- **Phase 41 supports Level 4+ proxy diagnostics and data recovery only**
- **Level 5 SWE/PINN residual constraints are not currently supported**
- **Phase 42 completed the no-training hydrodynamic export requirement specification**
- **Current Phase 42 decision: `selected_decision = export_contract_ready_for_dataset_inspection`; `training_authorized = false`**
- **Phase 42 data-contract counts: `required_fields_count = 16`; `minimum_contract_items = 10`; `urbanflood24_checklist_items = 10`; `icm_mike_checklist_items = 13`**
- **Phase 42 creates a formal hydrodynamic export/data contract only; it is not training, not SWE/PINN implementation, and not Level 5 support**
- **Phase 43 completed the no-training UrbanFlood24 full dataset inspection**
- **Current Phase 43 decision: `selected_decision = full_dataset_readiness_uncertain_needs_metadata`; `level5_supported = false`; `level4_plus_supported = true`; `training_authorized = false`**
- **Phase 43 dataset counts: `total_files = 354`; `total_dirs = 186`; `sampled_arrays_count = 54`**
- **UrbanFlood24 full supports higher-resolution Level 4+ proxy diagnostics, but not direct Level 5 SWE/PINN readiness**
- **Phase 44 completed no-training replanning around UrbanFlood24 full only**
- **Phase 44 freezes short-term Level 5/SWE/PINN claims and keeps `level5_supported = false`**
- **The future route is high-resolution Level 4+ proxy modeling, reliability diagnostics, and warning framework extension using UrbanFlood24 full**
- **Phase 45 completed no-training full-dataset indexing and lightweight adapter preparation**
- **Current Phase 45 decision: `selected_decision = indexing_ready_for_dataloader_smoke`; `training_authorized = false`; `level4_plus_supported = true`; `level5_supported = false`**
- **Phase 45 indexed evidence: `scenario_count_total = 168`; `static_index_rows = 6`; `warning_count = 0`; flood shape `(360, 1, 500, 500)` = 153 scenarios; flood shape `(480, 1, 500, 500)` = 15 scenarios; rainfall length `180` = 108 scenarios; rainfall length `360` = 60 scenarios**
- **Phase 46 completed no-training dataloader smoke testing and downsample/tiling feasibility**
- **Current Phase 46 decision: `selected_decision = dataloader_smoke_ready_for_downsample_baseline`; `training_authorized = false`; `level4_plus_supported = true`; `level5_supported = false`**
- **Phase 46 evidence: `scenario_index_loaded = true`; `static_index_loaded = true`; `representative_samples_count = 11`; `downsample_128_passed = true`; `downsample_256_passed = true`; `tile_checks_passed = true`; `batch_smoke_passed = true`; `memory_safe = true`**
- **Phase 46 is no-training dataloader smoke testing only and does not authorize uncontrolled training**
- **Phase 47 completed the first controlled UrbanFlood24 full-dataset `128 x 128` downsample `seed42` 10e baseline pilot**
- **Current Phase 47 decision: `selected_decision = phase47_controlled_128_downsample_seed42_pilot_completed`; `seed = 42`; `resolution = 128`; `epochs = 10`; `train_samples = 960`; `test_samples = 384`; `best_test_rmse = 0.01109213042097205`; `no_swe_pinn = true`; `level5_supported = false`**
- **Phase 47 final test metrics: `test_mae = 0.00525291082279485`; `test_wet_dry_iou = 0.8255524213115374`; `test_rollout_stability = 0.998722607580324`; `test_step_rmse_std = 0.0012824604989987165`**
- **Phase 47 supports a viable Level 4+ full-dataset `128 x 128` route, not Level 5, SWE/PINN, strict conservation, full mass conservation, or hydrodynamic closure**
- **Phase 47 does not authorize uncontrolled expansion to `seed123` / `seed202`, `256 x 256`, tile, multiscale, full `500 x 500`, sweeps, or new loss redesign**
- **Phase 48 completed no-training full-dataset reliability and physical proxy diagnostics for the Phase 47 checkpoint**
- **Current Phase 48 decision: `selected_decision = phase48_diagnostics_ready_for_warning_framework_extension`; `checkpoint_found = true`; `evaluated_scenarios = 48`; `evaluated_windows = 384`; `no_training = true`; `no_swe_pinn = true`; `level5_supported = false`**
- **Phase 48 mean metrics: `mean_rmse = 0.012037189189155709`; `mean_mae = 0.005252910632811514`; `mean_wet_dry_iou = 0.863043953275997`; `mean_false_dry_rate = 0.0911363765964386`; `mean_false_wet_rate = 0.003937674554837349`; `mean_absolute_relative_volume_bias_proxy = 0.021456503649973275`**
- **Phase 48 warning labels: reliable 1, caution 12, high-risk 35; these are conservative diagnostic screening labels, not calibrated probabilities, and the high-risk count is not proof of poor overall model skill**
- **Phase 48 provided the diagnostic inputs for completed Phase 49 warning-framework extension, not uncontrolled training expansion**
- **Phase 49 completed no-training full-dataset warning framework extension**
- **Current Phase 49 decision: `selected_decision = phase49_warning_framework_completed_with_conservative_labels`; `scenario_count = 48`; `warning_level_counts = reliable 1, caution 12, high-risk 35`; `high_risk_case_count = 35`; `no_training = true`; `warning_labels_are_probabilities = false`**
- **Phase 49 action mapping: `reliable -> normal_use_with_standard_monitoring`; `caution -> use_with_caution_and_review_diagnostics`; `high-risk -> high_risk_requires_review_or_supplemental_evidence`**
- **Phase 49 warning labels remain conservative diagnostic screening labels, not calibrated probabilities; the high-risk count reflects conservative screening sensitivity, not poor overall model skill**
- **Phase 49 supports conservative case reporting and diagnostic screening, not production readiness or uncontrolled training expansion**
- **Phase 45-50 roadmap: Phase 45 full dataset indexing and lightweight adapter complete; Phase 46 dataloader smoke test and downsample/tiling feasibility complete; Phase 47 controlled full dataset downsample baseline complete; Phase 48 full dataset reliability and physical proxy diagnostics complete; Phase 49 full dataset warning framework extension complete; Phase 50 framework consolidation / paper-ready evidence synthesis or reviewed expansion-decision phase next**
- **No `seed123` / `seed202` expansion, no sweep, no Phase 29 continuation, no Phase 38 rescue, no post-hoc loss/config rescue, and no unsupported pilot success claim are allowed**

At this stage, the project has moved from broad model tuning to rapid flood prediction with reliability diagnosis, failure-mode interpretation, confidence proxy diagnostics, spatial risk mapping, warning-rule guidance, manuscript drafting, representative warning-oriented case-study prototyping, physical-consistency diagnostics, diagnosis-driven target-wet recall refinement, strong-physics feasibility audit, conservation-proxy diagnostics, documented mixed Phase 27/29 volume-response pilots, Phase 30 boundary synthesis, Phase 31 Level 4+ physics input recovery readiness, Phase 32 Level 4+ domain-/boundary-aware design guardrails, Phase 33 diagnostic pilot-readiness review, Phase 34 threshold formalization, Phase 35 pilot implementation planning, Phase 36 code/smoke-test implementation, Phase 37 seed42 training authorization review, Phase 38 seed42 pilot rejection, Phase 39 failed-pilot trade-off diagnosis, Phase 40 next-constraint decision, Phase 41 SWE data readiness audit, Phase 42 hydrodynamic export/data-contract specification, Phase 43 UrbanFlood24 full dataset inspection, Phase 44 UrbanFlood24 full Level 4+ replanning, Phase 45 UrbanFlood24 full dataset indexing, Phase 46 dataloader smoke/downsample/tiling feasibility, Phase 47 controlled `128 x 128` full-dataset baseline training, Phase 48 full-dataset reliability and physical proxy diagnostics, and Phase 49 full-dataset warning framework extension. The current position is a viable UrbanFlood24 full Level 4+ `128 x 128` baseline route with conservative scenario-level warning actions, not Level 5 strong physics. The next technical work should be Phase 50 framework consolidation / paper-ready full-dataset evidence synthesis, or a reviewed expansion-decision phase, not uncontrolled seed expansion, resolution expansion, tile/multiscale/full-`500 x 500` training, a sweep, further proxy-loss redesign, SWE loss implementation, SWE residual implementation, PINN implementation, or post-hoc rescue.

## Representative Case Framing

Three representative cases continue to be useful for targeted comparison:

- `seed42`: favorable-case reference where stronger structured refinement must avoid unnecessary damage
- `seed202`: difficult-case reference where stronger structured refinement can show useful gains
- `seed123`: repeatability reference for checking whether candidate behavior generalizes beyond the two anchor cases

This framing motivated the Phase 6 Pilot A test, the Phase 7 conservative `adapt010` follow-up, the Phase 9 diagnosis, the Phase 10 margin-aware boundary-band refinement, the Phase 12 reliability/applicability diagnosis, the Phase 13 representative failure-case visual summary, the Phase 14 confidence proxy diagnosis, the Phase 15 reliability-screening layer, the Phase 16 warning-rule guidance layer, the Phase 17 reliability-aware framework synthesis, the Phase 19 manuscript-structure consolidation, the Phase 20 manuscript draft assembly, the Phase 21 manuscript evidence alignment, the Phase 22 manuscript full draft expansion, the Phase 23 warning case-study prototype, the Phase 24 physical-consistency diagnostics, the Phase 25 target-wet recall refinement, the Phase 26 strong-physics feasibility audit, the Phase 27 seed42 conservative volume-response pilot, the Phase 28 volume-response loss failure diagnosis, the Phase 29 seed42 tolerance-band volume consistency pilot, the Phase 30 strong-physics boundary synthesis, the Phase 31 physics input recovery readiness diagnostics, the Phase 32 domain-/boundary-aware physical consistency design, the Phase 33 seed42 pilot readiness review, the Phase 34 pilot threshold formalization, the Phase 35 manhole false-dry guardrail pilot plan, the Phase 36 manhole false-dry guardrail code/smoke-test implementation, the Phase 37 seed42 training authorization review, the Phase 38 seed42 pilot guardrail rejection, the Phase 39 failed-pilot trade-off diagnosis, the Phase 40 next-constraint decision, the Phase 41 SWE data readiness audit, the Phase 42 hydrodynamic export requirement specification, the Phase 43 UrbanFlood24 full dataset inspection, the Phase 44 UrbanFlood24 full Level 4+ replanning, the Phase 45 full dataset indexing and lightweight adapter preparation, the Phase 46 dataloader smoke/downsample/tiling feasibility check, the Phase 47 controlled full-dataset `128 x 128` baseline pilot, and the Phase 48 full-dataset reliability and physical proxy diagnostics.


## Adaptive Candidate and Margin-Aware Refinement

Phase 6 Pilot A kept the protected response-split path and added an optional bounded adaptive scalar. The earlier `adapt025` setting was technically stable, but it is now closed as a negative/neutral result:

```json
"rainfall_conditioning": {
  "enabled": true,
  "mode": "temporal_gate_residual_response_split_protected",
  "hidden_channels": 16,
  "residual_alpha": 0.10,
  "conditioned_fraction": 0.25,
  "active_fraction_within_response": 0.25,
  "adaptive_alpha_enabled": true,
  "adaptive_alpha_range": 0.25
}
```

The active adaptive candidate before margin-aware refinement is the more conservative Phase 7/Phase 8 `adapt010` setting:

```json
"rainfall_conditioning": {
  "enabled": true,
  "mode": "temporal_gate_residual_response_split_protected",
  "hidden_channels": 16,
  "residual_alpha": 0.10,
  "conditioned_fraction": 0.25,
  "active_fraction_within_response": 0.25,
  "adaptive_alpha_enabled": true,
  "adaptive_alpha_range": 0.10
}
```

When `adaptive_alpha_enabled` is omitted or set to `false`, the model falls back to the static protected response-split behavior. This keeps the adaptive addition optional and backward compatible with existing configs while preserving Phase 3.3 `af025` as the strongest static structured refinement.

Phase 10 keeps this adaptive structure and adds a margin-aware wet/dry consistency refinement. The recommended Phase 10 setting is:

```json
"wet_dry_consistency": {
  "enabled": true,
  "weight": 0.05,
  "threshold": 0.05,
  "temperature": 0.02,
  "boundary_band_pixels": 1,
  "boundary_weight": 2.0
}
```

This boundary-band setting has passed test-facing confirmation across `seed123`, `seed42`, and `seed202`. `boundary_weight = 1.5` is retained only as a conservative rollback setting.

Phase 25 keeps the Phase 10 boundary-band settings fixed and adds a targeted target-wet recall consistency term:

```json
"target_wet_recall_consistency": {
  "enabled": true,
  "weight": 0.02,
  "threshold": 0.05,
  "temperature": 0.02,
  "eps": 1e-6
}
```

## Future Work

The next justified follow-up is Phase 50 framework consolidation / paper-ready full-dataset evidence synthesis, or a reviewed expansion-decision phase. Phase 49 completed no-training full-dataset warning framework extension for the Phase 48 diagnostic labels with `selected_decision = phase49_warning_framework_completed_with_conservative_labels`, `scenario_count = 48`, `warning_level_counts = reliable 1, caution 12, high-risk 35`, `high_risk_case_count = 35`, `no_training = true`, and `warning_labels_are_probabilities = false`. Warning labels remain conservative diagnostic screening labels, not calibrated probabilities, and the high-risk count reflects conservative screening sensitivity rather than poor overall model skill. Phase 49 supports conservative case reporting and diagnostic screening, not Level 5, SWE/PINN, strict conservation, full mass conservation, hydrodynamic closure, production readiness, or uncontrolled expansion to `seed123` / `seed202`, `256 x 256`, tile, multiscale, full `500 x 500`, sweeps, or new loss redesign. The current Phase 10 boundary-band setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`, with Phase 25 target-wet recall consistency as a strong three-seed positive candidate and Phase 47-49 as the current controlled Level 4+ full-dataset baseline, diagnostic, and warning-framework boundary.

Recommended next work:

- analyze the remaining Phase 25 limitations, especially slight false-wet increase and non-uniform connectivity behavior
- treat Phase 25 as a targeted target-wet recall and wet-region preservation refinement, not as a complete physical-consistency solution
- treat Phase 26 as conservation-proxy diagnostics and aggregate volume-response improvement evidence, not full conservation enforcement
- treat Phase 27 as `seed42` standard-metric positive but volume-response objective not confirmed
- do not proceed to Phase 27 `seed123` / `seed202` confirmation or a Phase 27 weight sweep
- treat Phase 28 as diagnostic-only evidence that direct expansion of the Phase 27 underresponse-only loss should stop
- treat Phase 29 as partial volume-response repair with unacceptable standard-metric and physical-proxy trade-offs
- require a new plan before any further loss redesign or training
- do not proceed to Phase 29 `seed123` / `seed202` confirmation or a tolerance/weight sweep
- treat Phase 30 as documentation-only synthesis defining a Level 4 conservation-proxy / physical-consistency-guided surrogate boundary, not a model improvement
- treat Phase 31 as diagnostic-only Level 4+ physics input recovery readiness, not a Level 5 result
- treat Phase 32 as design/diagnostic-only Level 4+ domain-/boundary-aware physical consistency guardrails, not a model improvement
- keep the Phase 32 decision as `design_ready_no_training_yet`
- treat Phase 33 as diagnostic/readiness-review only, not a pilot success or training authorization
- keep the Phase 33 decision as `pilot_design_ready_but_training_not_started` and `training_authorized = false`
- treat Phase 34 as threshold-formalization only, not a pilot success or training authorization
- keep the Phase 34 decision as `thresholds_formalized_training_still_blocked`, with `training_authorized = false` and `next_allowed_step = pilot_implementation_plan`
- treat Phase 35 as a pilot implementation plan only, not code implementation or training authorization
- keep the Phase 35 status as `implementation_plan_ready_code_next`, with `training_authorized = false`
- treat Phase 36 as code/smoke-test implementation only, not pilot success or training authorization
- keep the Phase 36 decision as `code_smoke_ready_training_still_blocked`, with `training_authorized = false` and `training_executed = false`
- treat Phase 37 as diagnostic authorization review only, not training or pilot success
- keep the Phase 37 decision as `seed42_training_authorized_next_phase`, with `training_authorized_next_phase = true`, `training_executed = false`, and required checks passed `18 / 18`
- treat Phase 38 as completed seed42 pilot training, completed test evaluation, completed guardrail evaluation, and a rejected pilot under predeclared guardrails
- keep the Phase 38 decision as `seed42_pilot_rejected`
- treat Phase 38 as useful negative evidence, not a training execution failure
- treat Phase 39 as diagnostic-only evidence that the Phase 38 narrow target-proxy improvement did not preserve broader Level 4+ guardrails
- keep the Phase 39 decision as `tradeoff_diagnosis_completed_with_missing_optional_inputs`
- treat Phase 40 as failed-pilot design review and next-constraint decision, not training authorization or pilot rescue
- keep the Phase 40 decision as `pause_loss_redesign_move_to_swe_data_readiness`, with `training_authorized = false` and `next_recommended_phase = phase41_swe_data_readiness_audit`
- pause proxy-loss redesign after repeated trade-off evidence from Phase 27, Phase 29, and Phase 38
- treat Phase 41 as a completed no-training SWE data readiness audit, with `readiness_decision = readiness_uncertain_requires_external_data_export`
- keep `level5_supported = false`, `external_hydrodynamic_model_export_needed = true`, and `level4_proxy_supported = true`
- treat Phase 42 as a completed no-training hydrodynamic export requirement specification, with `selected_decision = export_contract_ready_for_dataset_inspection` and `training_authorized = false`
- use the Phase 42 contract counts conservatively: `required_fields_count = 16`, `minimum_contract_items = 10`, `urbanflood24_checklist_items = 10`, and `icm_mike_checklist_items = 13`
- treat Phase 43 as a completed no-training UrbanFlood24 full dataset inspection, with `selected_decision = full_dataset_readiness_uncertain_needs_metadata`, `level5_supported = false`, `level4_plus_supported = true`, and `training_authorized = false`
- use the Phase 43 dataset counts conservatively: `total_files = 354`, `total_dirs = 186`, and `sampled_arrays_count = 54`
- treat Phase 44 as completed no-training UrbanFlood24 full Level 4+ replanning, with no seed runs, no sweeps, no loss/config/model edits, no SWE residual implementation, no PINN implementation, and no Level 5 support claim
- freeze short-term Level 5/SWE/PINN claims and continue only with the UrbanFlood24 full Level 4+ route
- treat Phase 45 as completed no-training full-dataset indexing and lightweight adapter preparation, with `scenario_count_total = 168`, `static_index_rows = 6`, `warning_count = 0`, `selected_decision = indexing_ready_for_dataloader_smoke`, `training_authorized = false`, `level4_plus_supported = true`, and `level5_supported = false`
- use the Phase 45 sequence-length findings conservatively: flood shape `(360, 1, 500, 500)` = 153 scenarios, flood shape `(480, 1, 500, 500)` = 15 scenarios, rainfall length `180` = 108 scenarios, and rainfall length `360` = 60 scenarios
- treat Phase 46 as completed no-training dataloader smoke and downsample/tiling feasibility, with `selected_decision = dataloader_smoke_ready_for_downsample_baseline`, `scenario_index_loaded = true`, `static_index_loaded = true`, `representative_samples_count = 11`, `downsample_128_passed = true`, `downsample_256_passed = true`, `tile_checks_passed = true`, `batch_smoke_passed = true`, `memory_safe = true`, `training_authorized = false`, `level4_plus_supported = true`, and `level5_supported = false`
- treat Phase 47 as a completed controlled full-dataset `128 x 128` downsample `seed42` 10e baseline pilot, with `selected_decision = phase47_controlled_128_downsample_seed42_pilot_completed`, `train_samples = 960`, `test_samples = 384`, `best_test_rmse = 0.01109213042097205`, `no_swe_pinn = true`, and `level5_supported = false`
- use Phase 47 final test metrics conservatively: `test_mae = 0.00525291082279485`, `test_wet_dry_iou = 0.8255524213115374`, `test_rollout_stability = 0.998722607580324`, and `test_step_rmse_std = 0.0012824604989987165`
- treat Phase 48 as completed no-training full-dataset reliability and physical proxy diagnostics, with `selected_decision = phase48_diagnostics_ready_for_warning_framework_extension`, `checkpoint_found = true`, `evaluated_scenarios = 48`, `evaluated_windows = 384`, `no_training = true`, `no_swe_pinn = true`, and `level5_supported = false`
- use Phase 48 metrics conservatively: `mean_rmse = 0.012037189189155709`, `mean_mae = 0.005252910632811514`, `mean_wet_dry_iou = 0.863043953275997`, `mean_false_dry_rate = 0.0911363765964386`, `mean_false_wet_rate = 0.003937674554837349`, and `mean_absolute_relative_volume_bias_proxy = 0.021456503649973275`
- treat Phase 48 warning labels as conservative diagnostic screening labels, not calibrated probabilities; do not read the reliable 1, caution 12, high-risk 35 split as poor overall model skill
- treat Phase 49 as completed no-training full-dataset warning framework extension, with `selected_decision = phase49_warning_framework_completed_with_conservative_labels`, `scenario_count = 48`, `warning_level_counts = reliable 1, caution 12, high-risk 35`, `high_risk_case_count = 35`, `no_training = true`, and `warning_labels_are_probabilities = false`
- use Phase 49 action labels conservatively: `reliable -> normal_use_with_standard_monitoring`, `caution -> use_with_caution_and_review_diagnostics`, and `high-risk -> high_risk_requires_review_or_supplemental_evidence`
- treat Phase 49 warning labels as conservative diagnostic screening labels, not calibrated probabilities; the high-risk count reflects screening sensitivity rather than poor overall model skill
- treat the Level 4+ full-dataset `128 x 128` route as viable, not as Level 5 support, SWE/PINN support, strict conservation, full mass conservation, or hydrodynamic closure
- do not expand Phase 47-49 to `seed123` / `seed202`, `256 x 256`, tile, multiscale, full `500 x 500`, sweeps, or new loss redesign without a formal review and plan
- follow the compact Phase 45-50 route: Phase 45 full dataset indexing and lightweight adapter complete; Phase 46 dataloader smoke test and downsample/tiling feasibility complete; Phase 47 controlled full dataset downsample baseline complete; Phase 48 full dataset reliability and physical proxy diagnostics complete; Phase 49 full dataset warning framework extension complete; Phase 50 framework consolidation / paper-ready evidence synthesis or reviewed expansion decision
- do not run `seed123` / `seed202`, any sweep, Phase 29 continuation, or post-hoc loss/config rescue for the rejected Phase 38 pilot
- do not recommend or implement a full SWE/PINN residual unless compatible velocity/flux fields, `dx/dy`, `dt`, boundary conditions, pump/gate operations, complete source/sink terms, and complete hydrodynamic state variables are recovered and aligned
- consider calibrated uncertainty only if calibration data and evaluation design are added
- keep `boundary_weight = 1.5` only as a conservative rollback setting
- avoid new boundary-weight sweeps unless a new diagnosis clearly justifies them
- keep using the Phase 12/13/14/15/16/17 reliability, failure-case, confidence-proxy, screening, warning-rule, and synthesis findings, plus the Phase 18-22 manuscript materials, the Phase 23 warning case-study prototype, the Phase 24 physical-consistency diagnostics, the Phase 25 three-seed target-wet recall synthesis, the Phase 26 strong-physics feasibility audit, the Phase 27 mixed seed42 pilot, the Phase 28 failure diagnosis, the Phase 29 mixed tolerance-band pilot, the Phase 30 boundary synthesis, the Phase 31 input recovery readiness diagnostics, the Phase 32 design guardrails, the Phase 33 readiness review, the Phase 34 threshold formalization, the Phase 35 pilot plan, the Phase 36 code/smoke-test implementation, the Phase 41 SWE data readiness audit, the Phase 42 hydrodynamic export/data contract, the Phase 43 full dataset inspection, the Phase 44 replanning record, the Phase 45 full-dataset index, the Phase 46 dataloader smoke/downsample/tiling feasibility outputs, the Phase 47 controlled full-dataset baseline outputs, and the Phase 48 reliability/physical-proxy diagnostics, to define where the current model is reliable and where caution is required

## License

MIT License.
