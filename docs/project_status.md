# Project Status

## Current Conclusion

The repository should currently be interpreted as follows:

- `M3 f025` remains the overall best-balanced mainline reference.
- Phase 3.3 `af025` remains the strongest static structured refinement.
- Phase 6 `adapt025` is closed as a negative/neutral adaptive result.
- Phase 7/8 `adapt010` remains the active adaptive candidate before margin-aware refinement.
- Phase 9 completed the interpretability and trade-off diagnosis for `adapt010`.
- Phase 10 completed the first margin-aware intervention and established the current recommended refinement setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`.
- Phase 12 completed the first-pass reliability/applicability diagnosis of the Phase 10 recommended model.
- Phase 13 completed the first-pass representative failure-case visual summary.
- Phase 14 completed the first-pass proxy-based uncertainty/confidence diagnosis.
- Phase 15 completed the first implementation of reliability screening and risk mapping.
- Phase 16 completed the first implementation of reliability-aware warning rules and applicability boundary guidance.
- Phase 17 completed the reliability-aware warning framework synthesis across Phase 12 through Phase 16.
- Phase 18 completed the manuscript-oriented reliability-aware warning layer writing phase, with the first manuscript note completed.
- Phase 19 completed manuscript-structure and submission consolidation, with a paper-ready manuscript outline and submission-oriented planning document created.
- Phase 20 completed manuscript draft assembly, with the first full manuscript draft skeleton created.
- Phase 21 completed manuscript evidence and figure/table alignment, with a claim-to-evidence alignment document created.
- Phase 22 completed manuscript full draft expansion, with a fuller academic manuscript draft created from the Phase 20 skeleton and Phase 21 evidence alignment.
- Phase 23 completed the reliability-aware warning case-study and application prototype.
- Phase 24 completed physical consistency deepening and process diagnostics for the existing Phase 10 recommended outputs.
- Phase 25 completed Physics-Consistency Guided Surrogate Refinement: Target-Wet Recall Consistency through three-seed synthesis.
- Phase 26 completed Strong Physics Constraint Feasibility Audit and Conservation-Proxy Diagnostics.
- Phase 27 completed a seed42 conservative volume-response consistency pilot with mixed results.
- Phase 28 completed volume-response loss failure diagnosis for the Phase 27 seed42 pilot.
- Phase 29 completed a seed42 tolerance-band volume consistency pilot with mixed results.
- Phase 30 completed strong-physics boundary synthesis and current-position consolidation.
- Phase 31 completed physics input recovery readiness diagnostics, confirming Level 4+ structured physical proxy diagnostic support while keeping Level 5 unsupported.
- Phase 32 completed plan-first domain-/boundary-aware physical consistency design guardrails, confirming `design_ready_no_training_yet` while keeping the work design/diagnostic-only.
- Phase 33 completed diagnostic-only seed42 pilot readiness review under the Phase 32 guardrail framework, confirming `pilot_design_ready_but_training_not_started` with `training_authorized = false`.
- Phase 34 completed threshold-formalization only for a possible future `manhole_nonzero_false_dry_guardrail` seed42 pilot, confirming `thresholds_formalized_training_still_blocked` with `training_authorized = false`.
- Phase 35 completed a pilot implementation plan only for `manhole_nonzero_false_dry_guardrail`, confirming `implementation_plan_ready_code_next` with `training_authorized = false`.
- Phase 36 implemented and smoke-tested the config-gated `manhole_nonzero_false_dry_guardrail` code path and guardrail checker, confirming `code_smoke_ready_training_still_blocked` with `training_authorized = false` and `training_executed = false`.
- Phase 37 completed a diagnostic seed42 training authorization review, confirming `seed42_training_authorized_next_phase` with `training_authorized_next_phase = true`, `training_executed = false`, and required checks passed `18 / 18`.
- Phase 38 ran the single authorized seed42 pilot, completed test evaluation, completed guardrail evaluation, and rejected the pilot under the predeclared Phase 34 guardrail framework with `final_decision = seed42_pilot_rejected`.
- Phase 39 completed diagnostic-only trade-off analysis for the rejected Phase 38 seed42 pilot, confirming `tradeoff_diagnosis_completed_with_missing_optional_inputs` while keeping Phase 38 rejected.

The current Phase 10 conclusion is that boundary-band weighted wet/dry consistency refinement has passed test-facing confirmation on the three key project seeds: `seed123`, `seed42`, and `seed202`.

The current recommended model setting remains the Phase 10 setting:

- `boundary_band_pixels = 1`
- `boundary_weight = 2.0`

The current Phase 12 conclusion is that the Phase 10 recommended model is broadly useful for rapid spatiotemporal flood-process approximation under the tested scenario set, but its reliability is not uniform across all pixels, depth ranges, and scenarios. The main caution zones are exact wet/dry boundary cells, shallow threshold-adjacent cells, moderate-to-deep inundation depths, high-intensity `location2` scenarios, and local peak-depth extremes.

The current Phase 13 conclusion is that the highest-ranked failures are not random scattered cases. They collapse into two high-intensity `location2` target scenarios repeated across seeds: `location2 / r300y_p0.6_d3h / start_idx = 0` at worst step 1, and `location2 / r300y_p0.8_d3h / start_idx = 0` at worst step 4. The visual summaries show systematic underprediction, reduced predicted wet fraction, local peak-depth underprediction, and false-dry dominated wet/dry mismatch.

The current Phase 14 conclusion is that output-space confidence proxies are useful but limited. Confidence margin is useful for wet/dry classification risk because low-margin bins show much higher wet/dry error and false-dry rate. Cross-seed disagreement has only weak global correlation with scenario RMSE, so it should be treated as an auxiliary disagreement proxy rather than a strong standalone scenario-error predictor. Phase 14 is not calibrated probabilistic uncertainty.

The current Phase 15 conclusion is that the Phase 12/13/14 diagnostic evidence has been converted into a functional deterministic screening layer. The first implementation loaded 57 Phase 10 map files, generated 114 scenario-level risk records and 16,384 pixel-level risk records, and assigned 76 scenario records to `reliable`, 25 to `caution`, and 13 to `high-risk`. As a validation check, all 24 known Phase 13-like `location2` + `r300y` cases were flagged as `caution` or `high-risk`.

Phase 15 screening labels are deterministic risk-screening labels. They are not calibrated probabilities, Bayesian uncertainty estimates, or a substitute for a formal calibration design.

The current Phase 16 conclusion is that the Phase 15 deterministic reliability-screening labels have been converted into application-oriented warning guidance and an applicability boundary summary. Scenario warning counts are 76 `reliable`, 25 `caution`, and 13 `high-risk`. Pixel warning counts are 5,714 `reliable`, 8,805 `caution`, and 1,865 `high-risk`. The 13 high-risk warning cases match the Phase 15 high-risk cases.

Phase 16 warning labels are deterministic operational interpretation labels. They are not calibrated probabilities, Bayesian uncertainty estimates, formal confidence intervals, or a substitute for a formal calibration design.

The current Phase 17 conclusion is that Phase 12 through Phase 16 now form a coherent reliability-aware warning framework narrative: Phase 12 diagnoses reliability and applicability boundaries, Phase 13 visualizes representative repeated failure modes, Phase 14 evaluates confidence and disagreement proxies, Phase 15 converts the evidence into deterministic reliability screening and spatial risk mapping, and Phase 16 translates those labels into warning-rule and applicability-boundary guidance.

Phase 17 is a synthesis/documentation phase rather than a new experiment. It is intended to support manuscript writing, README narrative, and project positioning. It should not be read as calibrated uncertainty or universal generalization beyond the tested evidence.

The current Phase 19 conclusion is that the completed Phase 12 through Phase 18 reliability-aware warning framework and manuscript notes have been consolidated into a paper-ready manuscript structure and submission-oriented plan. The document covers paper positioning, candidate titles, abstract logic, methods/results/discussion structure, figure and table inventory, contribution statements, limitations, submission positioning, and immediate writing tasks.

The current Phase 20 conclusion is that the Phase 18 and Phase 19 manuscript-oriented materials have been assembled into the first full manuscript draft skeleton: `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`. Phase 20 is manuscript draft assembly, not a new experiment phase.

The current Phase 21 conclusion is that manuscript claims have been aligned with existing evidence sources, figures, tables, JSON/CSV outputs, and findings documents before full manuscript expansion. The claim-to-evidence and figure/table alignment document has been created: `docs/manuscript_evidence_figure_table_alignment.md`. Phase 21 is evidence alignment and figure/table planning, not a new experiment phase.

The current Phase 22 conclusion is that the Phase 20 manuscript skeleton has been expanded into a fuller academic manuscript draft using the Phase 21 evidence-alignment document. The full manuscript draft expansion has been created: `docs/manuscript_full_draft_reliability_aware_urban_flood_warning.md`. Phase 22 is manuscript full-draft expansion, not a new experiment phase.

The current Phase 23 conclusion is that the completed reliability-aware warning framework has been converted into a representative case-study prototype. Phase 23 integrates Phase 15 reliability screening, Phase 16 warning rules, and existing Phase 10 forecast map arrays for one `reliable`, one `caution`, and one `high-risk` case. The selected cases are `location1|r100y_p0.5_d3h|6`, `location2|r300y_p0.6_d3h|6`, and `location2|r300y_p0.8_d3h|0`.

The current Phase 24 conclusion is that high-risk cases are not only statistically worse; they are physically less consistent. Compared with reliable cases, high-risk cases show stronger false-dry behavior, stronger wet-area contraction, stronger peak-depth underprediction, stronger connectivity loss, and stronger volume under-response. Correlations with `risk_score` are 0.913 for `false_dry_rate`, 0.862 for `wet_area_contraction`, 0.856 for `peak_depth_underprediction`, and 0.539 for `connectivity_loss_indicator`.

The current Phase 25 conclusion is that the Phase 24 physical-consistency diagnosis has been converted into a targeted model refinement. The fixed Phase 10 boundary-band settings remain `boundary_band_pixels = 1` and `boundary_weight = 2.0`. Phase 25 adds config-gated `target_wet_recall_consistency` with `weight = 0.02`, `threshold = 0.05`, `temperature = 0.02`, and `eps = 1e-6`.

Across `seed123`, `seed42`, and `seed202`, Phase 25 consistently improved standard test metrics and reduced the intended aligned physical failure modes. Mean standard test deltas versus Phase 10 were `RMSE = -0.007057`, `MAE = -0.001519`, `wet/dry IoU = +0.076670`, `rollout stability = +0.001035`, and `step RMSE std = -0.001071`. Mean aligned physical deltas were `false_dry_rate = -0.111321`, `wet_area_contraction = -0.079104`, `relative_volume_bias = +0.105093`, `peak_depth_underprediction = -0.014962`, `RMSE = -0.007244`, and `MAE = -0.001885`.

Phase 25 is a diagnosis-driven, depth-field-compatible physical-consistency refinement. It improves target-wet recall and wet-region preservation while maintaining or improving standard prediction metrics. It is a strong three-seed positive candidate and a credible targeted refinement over the Phase 10 baseline, but not a complete physical-consistency solution: `false_wet_rate` increased slightly on average, `connectivity_loss_indicator` was not consistently improved, and no full SWE/PINN residual was implemented.

The current Phase 26 conclusion is that the project has tested whether the current data and outputs can support stronger physics constraints. Current data support Level 4 conservation-proxy diagnostics only partially, Level 4 conservation-aware loss design remains unclear, and Level 5 full SWE/PINN residual constraints are not supported. Phase 25 improves aggregate water-volume response and reduces under-response, but it is not a strict timestep-wise conservation solution. No retraining, architecture modification, Phase 10 loss modification, boundary tuning, Phase 25 sweep, or full SWE/PINN implementation was performed.

The current Phase 27 conclusion is that the conservative `volume_response_consistency` seed42 pilot is mixed. It improved all standard test metrics relative to the Phase 25 seed42 reference (`RMSE = -0.00236602`, `MAE = -0.000654673`, `wet/dry IoU = +0.00892365`, `rollout stability = +0.000618097`, and `step RMSE std = -0.000631138`) and improved several under-response-related proxies, including false-dry volume loss, wet-area contraction, peak-depth underprediction, false-wet rate, and false-wet volume excess. However, it did not achieve the primary conservative volume-response objective: aggregate absolute relative volume bias worsened by `+0.0216934`, mean-step absolute relative volume bias worsened by `+0.0170953`, and run-level aggregate relative volume bias moved from Phase 25 `+0.00296825` to Phase 27 `+0.0246616`.

Phase 27 is therefore not a confirmed conservation-constrained success. The current decision is `remain_seed42_positive_only`: do not proceed to `seed123` / `seed202` confirmation, do not start a Phase 27 weight sweep, and do not claim strong physics success, strict mass conservation, timestep-wise conservation, full mass conservation, or SWE/PINN support. Any future confirmation should require a revised loss design rather than extending the current Phase 27 pilot unchanged.

The current Phase 28 conclusion is that the Phase 27 volume-response objective failure should be attributed mainly to `dry_or_threshold` target-depth-bin volume accumulation, not threshold-level false-wet expansion or already-wet amplification. Key evidence is `delta_volume_bias_total = +6974.12`, Phase 25 relative volume bias = `+0.00296825`, Phase 27 relative volume bias = `+0.0246616`, false-wet volume excess delta = `-184.071`, already-wet amplification = `+1396.20`, and `dry_or_threshold` contribution = `+5362.82`, about `76.9%` of total delta volume bias.

Phase 28 is diagnostic only. It did not train a model, modify architecture, modify losses, modify configs, run `seed123` / `seed202`, or perform a Phase 27 weight sweep. It explains why Phase 27 should not be directly expanded and motivated a tolerance-band direction only through a new plan. Current guardrails remain no `seed123` / `seed202` confirmation of Phase 27, no Phase 27 sweep, no strict conservation claim, no full mass-conservation claim, and no SWE/PINN claim.

The current Phase 29 conclusion is that the mixed tolerance-band seed42 pilot partially repaired the Phase 27 volume-response and `dry_or_threshold` accumulation failure mode, but not enough to justify confirmation. Relative to Phase 27, aggregate absolute relative volume bias improved from `0.0246616` to `0.019464`, mean-step absolute relative volume bias improved from `0.257274` to `0.230447`, and `dry_or_threshold` contribution decreased from `0.137662` to `0.131428`. However, all listed standard metrics worsened; false-dry volume loss worsened from `5409.72` to `5964.83`; false-wet volume excess worsened from `7750.32` to `8289.77`; peak-depth underprediction worsened from `0.128045` to `0.134593`; and aggregate bias remains far from the Phase 25 near-zero aggregate bias of `0.00296825`.

Phase 29 seed42 test metrics were `RMSE = 0.0443854521`, `MAE = 0.0178462429`, `wet/dry IoU = 0.8016409529`, `rollout stability = 0.9895110601`, and `step RMSE std = 0.0106412431`. The current decision is `remain_seed42_only_pending_revision`: do not run `seed123` or `seed202`, do not perform a tolerance or weight sweep, do not claim tolerance-band success, and do not claim strict conservation, full mass conservation, or SWE/PINN support. Future work requires a new plan before any further loss redesign or training.

The current Phase 30 conclusion is that the project has reached a Level 4 conservation-proxy / physical-consistency-guided surrogate position. This supports reliability-aware warning support, physical-consistency diagnosis, conservation-proxy evaluation, failure-mode interpretation, and applicability-boundary communication. It does not support strict mass conservation, full hydrodynamic closure, SWE/PINN residual consistency, or Level 5 strong physics. Phase 30 is documentation-only synthesis, not a model improvement, training run, loss change, or new evaluation result.

The current Phase 31 conclusion is that Level 4+ structured physical proxy diagnostics are supported. Phase 31 recovered and verified shape-compatible static physical context and masks: raw flood/rain/static arrays are available; `absolute_DEM.npy`, `impervious.npy`, and `manhole.npy` are available at `128 x 128`; train/test geodata are consistent; `DEM = 100` is likely a high/invalid/no-data candidate; `absolute_DEM < 99` supports valid-domain mask construction; valid-domain, invalid/high, boundary-ring, and interior masks can be constructed; sample-to-location mapping for forecast maps was recovered from adjacent `summary.json` `metadata.location`; and masked physical diagnostics are fully supported.

Phase 31 does not support Level 5. The repository still lacks aligned velocity/flux fields, boundary/source-sink aligned fields, explicit `dx/dy`, full hydrodynamic state variables, and non-inferred `dt`. It should not claim strict conservation, full mass conservation, SWE/PINN residual consistency, or full hydrodynamic closure.

Phase 31 masked diagnostics reinforce that Phase 29 is mixed rather than successful. Relative to Phase 27, Phase 29 improves valid-domain masked relative volume-bias proxy from `0.0169359` to `0.0115344`, but worsens valid-domain `RMSE`, `MAE`, `false_dry_rate`, `false_wet_rate`, `false_dry_volume_loss_proxy`, and `false_wet_volume_excess_proxy`. The Phase 29 false-dry rate is highest over `manhole_nonzero_valid` (`0.131298`), and the Phase 29 false-wet rate is highest over `high_impervious_valid` (`0.0239894`).

The current Phase 32 conclusion is that a plan-first Level 4+ domain-/boundary-aware physical consistency design has been formalized from Phase 31 recovered masks and masked diagnostics. Phase 32 defines 20 guardrail metrics and 12 stop/go criteria across standard, valid-domain, boundary-ring, high-impervious-valid, manhole-nonzero-valid, dry-threshold, and level-boundary groups. It does not train a model, modify losses, modify configs, or alter model architecture. The current decision is `design_ready_no_training_yet`.

Phase 32 does not justify immediate `seed42` training, immediate loss modification, `seed123` / `seed202` confirmation, or a tolerance/weight sweep. Any future pilot work should fix the target objective, baseline comparisons, acceptance/rejection thresholds, and all guardrails before training.

The current Phase 33 conclusion is that seed42 pilot design is ready for future consideration but training has not started and is not authorized. Phase 33 reviewed 5 pilot options and 15 readiness criteria. The strongest future candidate is `manhole_nonzero_false_dry_guardrail`, because `manhole_nonzero_valid` had the highest Phase 29 false-dry rate. However, numeric acceptance thresholds, numeric rejection thresholds, and full Phase 25 / Phase 27 / Phase 29 baseline acceptance/rejection criteria are not fixed.

The current Phase 34 conclusion is that baseline, acceptance, and rejection thresholds have been formalized for a possible future `manhole_nonzero_false_dry_guardrail` seed42 pilot, but training remains blocked. Phase 34 fixed 23 baseline metric rows, 14 acceptance threshold rows, 9 rejection threshold rows, and 7 readiness rows. The current decision is `thresholds_formalized_training_still_blocked`; `training_authorized = false`; `next_allowed_step = pilot_implementation_plan`; and the future candidate remains `manhole_nonzero_false_dry_guardrail`.

Phase 34 AT01 targets `manhole_nonzero_valid` `false_dry_rate` and requires it to be below Phase 29 and no higher than Phase 27: Phase 27 = `0.1172229713`, Phase 29 = `0.131297982994`, and threshold = `0.1172229713`. RT01 rejects the Phase 29 trade-off pattern where absolute relative volume-bias proxy improves while RMSE, MAE, false-dry rate, and false-wet rate all worsen versus Phase 27. AT13 keeps volume-bias proxy improvement conditional and insufficient alone; AT14 / RT09 preserve the Level 4+ proxy claim boundary.

The current Phase 35 conclusion is that a pilot implementation plan has been completed for the possible future `manhole_nonzero_false_dry_guardrail` candidate, but no implementation or training has been performed. Phase 35 is plan-only: it does not implement losses, create configs, modify model code, run `seed42`, run `seed123` / `seed202`, perform a sweep, or continue Phase 29. The candidate remains `manhole_nonzero_false_dry_guardrail`; the target region is `manhole_nonzero_valid`; the target metric is `false_dry_rate`; the key AT01 threshold remains `0.1172229713`; `training_authorized = false`; and the next allowed step is a code/smoke-test implementation phase, not training.

The current Phase 36 conclusion is that the config-gated `manhole_nonzero_false_dry_guardrail` code path and guardrail checker are smoke-ready, but training remains blocked. Phase 36 updated `utils/physics_losses.py`, added `configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`, and added `scripts/check_phase36_pilot_guardrails.py`. Smoke-test evidence records `config_loaded = true`, `loss_smoke_passed = true`, `guardrail_checker_dry_run_passed = true`, `training_authorized = false`, `training_executed = false`, `seed42_run_executed = false`, `seed123_seed202_executed = false`, and `decision = code_smoke_ready_training_still_blocked`. The guardrail checker dry run remained Level 4+ static-map-aware proxy diagnostics only, with `status = dry_run_passed`, `acceptance_threshold_count = 14`, `rejection_threshold_count = 9`, `baseline_metric_count = 23`, `acceptance_structure_ready = true`, and `rejection_structure_ready = true`.

The current Phase 37 conclusion is that the reviewed seed42 training command is authorized for the next phase only. Phase 37 reviewed `python scripts/train_model.py --config configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`; all required checks passed (`18 / 18`); `decision = seed42_training_authorized_next_phase`; `training_authorized_next_phase = true`; and `training_executed = false`. Phase 37 itself did not train, did not run `seed42`, did not run `seed123` / `seed202`, and did not perform a sweep.

The current Phase 38 conclusion is that the single authorized seed42 pilot has been trained, test-evaluated, guardrail-evaluated, and rejected under the predeclared Phase 34 guardrail framework. Phase 38 used `python scripts/train_model.py --config configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`; test metrics were `RMSE = 0.04456830142359985`, `MAE = 0.01795931400633172`, `wet_dry_iou = 0.8068740587485465`, `rollout_stability = 0.9899644569346779`, and `step_rmse_std = 0.01018835528214511`. Guardrail evaluation produced `final_decision = seed42_pilot_rejected`, with 2 standard checks passed, 3 standard checks failed, 6 acceptance checks passed, 8 acceptance checks failed, and 3 rejection rules triggered. Failed checks were AT02, AT03, AT04, AT06, AT07, AT08, AT09, and AT10. Triggered rejection rules were RT01, RT05, and RT07.

Phase 38 is useful negative evidence, not a training execution failure. The current `manhole_nonzero_false_dry_guardrail` design should not be treated as accepted. The result indicates a Phase 29-like trade-off pattern: the target/proxy behavior is not sufficient to pass broader Level 4+ guardrails.

The current Phase 39 conclusion is that the Phase 38 negative result has been diagnosed. The current `manhole_nonzero_false_dry_guardrail` improved a narrow `manhole_nonzero_valid` false-dry proxy, but that improvement did not translate into broader valid-domain, regional guardrail, and standard-metric success. Phase 39 recorded `failed_acceptance_count = 8`, `triggered_rejection_count = 3`, `comparison_rows = 13`, `region_rows = 5`, and `scenario_rows = 19`. The diagnostic decision is `tradeoff_diagnosis_completed_with_missing_optional_inputs` because per-batch/scenario Phase 25, Phase 27, and Phase 29 baselines are unavailable, leaving scenario diagnostics Phase38-only.

The current project position after Phase 39 is rapid flood prediction with reliability diagnosis, failure-mode interpretation, confidence proxy diagnostics, spatial risk mapping, deterministic warning-rule guidance, manuscript-ready synthesis, manuscript drafting, representative case-specific warning interpretation, physical-consistency diagnosis, diagnosis-driven target-wet recall refinement, strong-physics feasibility audit, conservation-proxy diagnostics, documented mixed Phase 27/29 volume-response pilots, Phase 30 boundary synthesis, Phase 31 Level 4+ physics input recovery readiness, Phase 32 Level 4+ domain-/boundary-aware design guardrails, Phase 33 diagnostic seed42 pilot-readiness review, Phase 34 pilot threshold formalization, Phase 35 pilot implementation planning, Phase 36 code/smoke-test implementation, Phase 37 seed42 training authorization review, Phase 38 rejected seed42 pilot, and Phase 39 failed-pilot trade-off diagnosis. The project supports Level 4+ proxy diagnostics and conservative readiness planning only. It still does not support strict conservation, full mass conservation, SWE/PINN residual consistency, full hydrodynamic closure, or Level 5 strong physics. A full SWE/PINN residual is not recommended unless compatible velocity, flux, boundary, grid-spacing, and source-sink information become available.

Next technical work should be failed-pilot design review and diagnosis consolidation, not additional training, `seed123` / `seed202` expansion, a sweep, Phase 29 continuation, or post-hoc loss/config rescue. No additional Phase 10 boundary-weight sweep, Phase 10 boundary-parameter tuning, unreviewed training, traffic-impact modeling, invented references, unsupported claims, or new uncertainty claim was performed. The current Phase 10 boundary-band setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`.

## Meaning Of Each Reference

### Mainline reference

`M3 f025` remains the default project-level mainline reference because it provides the strongest overall balance across robustness, stability, and project-level confidence before the later adaptive and margin-aware refinements.

### Strongest static structured refinement

Phase 3.3 `af025` remains the strongest static structured refinement discovered so far. It is still the correct static control when evaluating whether adaptive follow-ups and margin-aware refinements add value.

### Closed adaptive result

Phase 6 `adapt025` established that the adaptive scalar mechanism is technically stable and trainable, but it did not remain superior to the static Phase 3.3 `af025` control after full training. It should therefore be treated as a documented negative/neutral result rather than an active candidate.

### Active adaptive candidate before margin-aware refinement

Phase 7/8 `adapt010` remains the active adaptive candidate before margin-aware refinement. It improved RMSE, MAE, and loss across the required full `40e` comparisons, but Phase 8 Batch 2 also showed mixed wet/dry IoU behavior, mainly because of the `seed123` trade-off.

### Interpretability diagnosis

Phase 9 diagnosed the `adapt010` trade-off rather than opening a new architecture search. The main finding was that the `seed123` IoU give-back was best interpreted as a mixed, margin-region, step-dependent wet/dry trade-off rather than adaptive multiplier saturation or seed-specific mechanism instability.

### Current recommended margin-aware refinement

Phase 10 introduced a minimal, diagnosis-driven intervention: boundary-band weighted wet/dry consistency refinement.

The recommended Phase 10 setting is:

- `boundary_band_pixels = 1`
- `boundary_weight = 2.0`

This setting passed test-facing confirmation across the three key seeds:

- `seed123`: original mixed-IoU problem seed
- `seed42`: favorable-case guardrail seed
- `seed202`: difficult-case confirmation seed

`boundary_weight = 1.5` remains only a conservative rollback setting and is no longer the preferred setting.

### Reliability and applicability diagnosis

Phase 12 diagnosed the reliability and applicability boundaries of the Phase 10 recommended model using saved test-facing forecast maps.

Generated diagnostics include:

- timestep-wise error
- depth-bin error
- wet/dry boundary-distance error
- scenario-level reliability
- failure-case ranking
- diagnostic figures

The first-pass Phase 12 findings indicate:

- the model has a mild overall underprediction bias
- exact wet/dry boundary cells remain the main reliability bottleneck
- moderate-to-deep target depths show stronger underprediction
- high-intensity `location2` cases dominate the highest-ranked failures
- no retraining, architecture change, Phase 10 loss change, or boundary-weight sweep was performed

### Representative failure-case visual summary

Phase 13 converted the highest-ranked Phase 12 failure cases into representative worst-timestep visual summaries.

Generated Phase 13 outputs include:

- `docs/phase13_failure_case_visual_summary_plan.md`
- `scripts/visualize_phase13_failure_cases.py`
- `analysis/phase13_failure_cases/selected_failure_cases.csv`
- `analysis/phase13_failure_cases/summary.json`
- `analysis/phase13_failure_cases/figures/`
- `docs/phase13_failure_case_visual_summary_findings.md`

The first-pass Phase 13 findings indicate:

- top failures collapse into two high-intensity `location2` target scenarios repeated across seeds
- worst-timestep visualization is more explanatory than final-timestep visualization
- the main visual failure mode is systematic underprediction with reduced wet extent
- local peak depths are strongly underestimated
- wet/dry mismatch is false-dry dominated

### Proxy-based uncertainty and confidence diagnosis

Phase 14 diagnosed whether output-space confidence and disagreement proxies can help identify less reliable predictions.

Generated Phase 14 outputs include:

- `docs/phase14_uncertainty_confidence_diagnostics_plan.md`
- `scripts/analyze_phase14_confidence.py`
- `analysis/phase14_confidence/summary.json`
- `analysis/phase14_confidence/confidence_margin_metrics.csv`
- `analysis/phase14_confidence/seed_disagreement_metrics.csv`
- `analysis/phase14_confidence/risk_proxy_metrics.csv`
- `analysis/phase14_confidence/scenario_confidence_metrics.csv`
- `analysis/phase14_confidence/figures/`
- `docs/phase14_uncertainty_confidence_diagnostics_findings.md`

The first-pass Phase 14 findings indicate:

- confidence margin is useful for wet/dry classification risk
- low-margin bins show much higher wet/dry class error and false-dry rate
- confidence margin is not a complete depth-error uncertainty measure
- high-confidence wet/dry state does not guarantee accurate depth magnitude
- cross-seed disagreement has weak global correlation with scenario RMSE
- cross-seed disagreement should be treated as an auxiliary proxy rather than a strong standalone error predictor
- Phase 14 does not provide calibrated probabilistic uncertainty

### Reliability screening and risk mapping

Phase 15 converted the Phase 12/13/14 diagnostic evidence into scenario-level reliability screening and pixel-level spatial risk mapping for the Phase 10 recommended model.

Generated Phase 15 outputs include:

- `docs/phase15_reliability_screening_risk_mapping_plan.md`
- `scripts/screen_phase15_reliability.py`
- `analysis/phase15_reliability_screening/summary.json`
- `analysis/phase15_reliability_screening/scenario_risk_scores.csv`
- `analysis/phase15_reliability_screening/pixel_risk_summary.csv`
- `analysis/phase15_reliability_screening/high_risk_cases.csv`
- `analysis/phase15_reliability_screening/figures/`
- `docs/phase15_reliability_screening_risk_mapping_findings.md`

The first-pass Phase 15 findings indicate:

- 57 Phase 10 map files were loaded
- 114 scenario-level risk records were generated
- 16,384 pixel-level risk records were generated
- scenario screening produced 76 `reliable`, 25 `caution`, and 13 `high-risk` records
- all 24 known Phase 13-like `location2` + `r300y` cases were flagged as `caution` or `high-risk`
- the labels are deterministic screening labels, not calibrated probabilities or Bayesian uncertainty
- no retraining, tuning, architecture change, or new sweep was performed

### Reliability-aware warning rules and applicability boundary

Phase 16 converted the Phase 15 deterministic scenario and pixel screening labels into warning-rule guidance and an applicability boundary summary for application-facing interpretation.

Generated Phase 16 outputs include:

- `docs/phase16_reliability_warning_applicability_plan.md`
- `scripts/build_phase16_warning_rules.py`
- `analysis/phase16_warning_rules/summary.json`
- `analysis/phase16_warning_rules/warning_rules.json`
- `analysis/phase16_warning_rules/scenario_warning_summary.csv`
- `analysis/phase16_warning_rules/applicability_boundary_table.csv`
- `analysis/phase16_warning_rules/high_risk_warning_cases.csv`
- `analysis/phase16_warning_rules/pixel_warning_summary.csv`
- `analysis/phase16_warning_rules/figures/`
- `docs/phase16_reliability_warning_applicability_findings.md`

The first-pass Phase 16 findings indicate:

- scenario warnings produced 76 `reliable`, 25 `caution`, and 13 `high-risk` records
- pixel warnings produced 5,714 `reliable`, 8,805 `caution`, and 1,865 `high-risk` records
- the 13 high-risk warning cases match the Phase 15 high-risk cases
- Phase 16 turns rapid prediction, reliability screening, and spatial risk mapping into application-oriented warning-rule guidance
- warning labels are deterministic operational interpretation labels, not calibrated probabilities, Bayesian uncertainty, or formal confidence intervals
- no retraining, tuning, architecture change, Phase 10 loss change, or new sweep was performed

### Reliability-aware warning framework synthesis

Phase 17 synthesizes Phase 12 through Phase 16 into a coherent reliability-aware flood-warning framework narrative.

Generated Phase 17 output:

- `docs/phase17_reliability_warning_framework_synthesis.md`

The Phase 17 synthesis indicates:

- the project has evolved from rapid flood-depth prediction to rapid prediction plus reliability diagnosis, failure-mode interpretation, confidence proxy diagnostics, spatial risk mapping, and warning-rule guidance
- Phase 17 does not introduce a new experiment, retrain models, modify architecture, modify the Phase 10 loss, tune `boundary_weight` or `boundary_band_pixels`, or open a new sweep
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`
- the synthesis supports manuscript writing, README narrative, and project positioning
- the framework remains deterministic and evidence-based; it does not claim calibrated uncertainty or universal generalization

### Manuscript-oriented reliability-aware warning layer

Phase 18 converts the completed Phase 12 through Phase 17 reliability-aware warning framework into manuscript-ready writing material for a section titled "Reliability-Aware Warning Layer for Urban Flood Surrogate Prediction."

Generated Phase 18 writing deliverables:

- `docs/phase18_manuscript_reliability_warning_layer_plan.md`
- `docs/manuscript_reliability_aware_warning_layer.md`

The Phase 18 writing phase indicates:

- the manuscript reliability-aware warning layer note has been created
- Phase 18 is manuscript-oriented synthesis/writing, not a new experiment
- no retraining, architecture modification, Phase 10 loss modification, `boundary_weight` tuning, `boundary_band_pixels` tuning, new sweep, or new result generation was performed
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`

### Manuscript structure and paper-ready consolidation

Phase 19 converts the completed reliability-aware warning framework and Phase 18 manuscript note into a paper-ready manuscript outline and submission-oriented planning document.

Generated Phase 19 deliverables:

- `docs/phase19_manuscript_structure_consolidation_plan.md`
- `docs/manuscript_structure_and_submission_consolidation.md`

The Phase 19 consolidation indicates:

- the manuscript structure and submission consolidation document has been created
- Phase 19 is manuscript-structure and submission consolidation, not a new experiment
- the document covers paper positioning, candidate titles, abstract logic, methods/results/discussion structure, figure/table inventory, contribution statements, limitations, submission positioning, and immediate writing tasks
- no retraining, architecture modification, Phase 10 loss modification, `boundary_weight` tuning, `boundary_band_pixels` tuning, new sweep, or new result generation was performed
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`

### Manuscript draft assembly

Phase 20 assembles the Phase 18 manuscript warning-layer note and the Phase 19 manuscript-structure consolidation into the first full manuscript draft skeleton.

Generated Phase 20 deliverables:

- `docs/phase20_manuscript_draft_assembly_plan.md`
- `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`

The Phase 20 assembly indicates:

- the first full manuscript draft skeleton has been created
- Phase 20 is manuscript draft assembly, not a new experiment phase
- no retraining, architecture modification, Phase 10 loss modification, `boundary_weight` tuning, `boundary_band_pixels` tuning, new sweep, or new result generation was performed
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`

### Manuscript evidence and figure/table alignment

Phase 21 aligns manuscript claims with existing evidence sources, figures, tables, JSON/CSV outputs, and findings documents before full manuscript expansion.

Generated Phase 21 deliverables:

- `docs/phase21_manuscript_evidence_figure_alignment_plan.md`
- `docs/manuscript_evidence_figure_table_alignment.md`

The Phase 21 alignment indicates:

- the claim-to-evidence and figure/table alignment document has been created
- Phase 21 is evidence alignment and figure/table planning, not a new experiment phase
- no retraining, architecture modification, Phase 10 loss modification, `boundary_weight` tuning, `boundary_band_pixels` tuning, new sweep, new result generation, or new uncertainty claim was performed
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`

### Manuscript full draft expansion

Phase 22 expands the Phase 20 manuscript skeleton into a fuller academic manuscript draft using the Phase 21 evidence-alignment document.

Generated Phase 22 deliverables:

- `docs/phase22_manuscript_full_draft_expansion_plan.md`
- `docs/manuscript_full_draft_reliability_aware_urban_flood_warning.md`

The Phase 22 expansion indicates:

- the full manuscript draft expansion has been created
- Phase 22 is manuscript full-draft expansion, not a new experiment phase
- no retraining, architecture modification, Phase 10 loss modification, `boundary_weight` tuning, `boundary_band_pixels` tuning, new sweep, new result generation, invented references, unsupported claims, or new uncertainty claim was performed
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`

### Reliability-aware warning case study and application prototype

Phase 23 converts the completed reliability-aware warning framework into a representative application prototype by integrating Phase 15 reliability screening, Phase 16 warning rules, and existing Phase 10 forecast map arrays.

Generated Phase 23 outputs include:

- `docs/phase23_reliability_warning_case_study_plan.md`
- `scripts/build_phase23_warning_case_study.py`
- `analysis/phase23_warning_case_study/summary.json`
- `analysis/phase23_warning_case_study/selected_cases.csv`
- `analysis/phase23_warning_case_study/case_warning_report.md`
- `analysis/phase23_warning_case_study/figures/`
- `docs/phase23_reliability_warning_case_study_findings.md`

The Phase 23 prototype indicates:

- selected cases: `location1|r100y_p0.5_d3h|6`, `location2|r300y_p0.6_d3h|6`, and `location2|r300y_p0.8_d3h|0`
- the framework now supports rapid prediction, reliability screening, scenario-level warning classification, pixel-level risk visualization, case-specific warning explanation, and applicability-boundary interpretation
- Phase 23 is an application-prototype phase, not a model-tuning phase
- no retraining, architecture modification, Phase 10 loss modification, `boundary_weight` tuning, `boundary_band_pixels` tuning, new sweep, new prediction generation, or metric-chasing experiment was performed
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`

### Physical consistency deepening and process diagnostics

Phase 24 diagnoses whether the existing Phase 10 recommended surrogate outputs are physically consistent in volume response, wet-area contraction, peak-depth preservation, wet-area connectivity, temporal behavior, and linkage with Phase 15/16 warning-risk labels.

Generated Phase 24 outputs include:

- `docs/phase24_physical_consistency_deepening_plan.md`
- `scripts/analyze_phase24_physical_consistency.py`
- `analysis/phase24_physical_consistency/summary.json`
- `analysis/phase24_physical_consistency/scenario_physical_consistency_metrics.csv`
- `analysis/phase24_physical_consistency/volume_response_metrics.csv`
- `analysis/phase24_physical_consistency/peak_depth_consistency.csv`
- `analysis/phase24_physical_consistency/wet_connectivity_metrics.csv`
- `analysis/phase24_physical_consistency/temporal_consistency_metrics.csv`
- `analysis/phase24_physical_consistency/physics_risk_linkage.csv`
- `analysis/phase24_physical_consistency/topographic_consistency.csv`
- `analysis/phase24_physical_consistency/figures/`
- `docs/phase24_physical_consistency_deepening_findings.md`

The Phase 24 diagnostics indicate:

- high-risk cases are physically less consistent than reliable cases
- warning-level means for `reliable` / `caution` / `high-risk` are 0.125 / 0.268 / 0.444 for `false_dry_rate`, 0.046 / 0.135 / 0.383 for `wet_area_contraction`, 0.024 m / 0.241 m / 1.381 m for `peak_depth_underprediction`, 0.197 / 0.240 / 1.000 for `connectivity_loss_indicator`, and -0.040 / -0.145 / -0.448 for `relative_volume_bias`
- topographic consistency was skipped because no shape-compatible DEM/static elevation layer was found; this limitation is recorded in `summary.json` and `topographic_consistency.csv`
- Phase 24 is a diagnostic phase, not a model-refinement or tuning phase
- no retraining, architecture modification, Phase 10 loss modification, `boundary_weight` tuning, `boundary_band_pixels` tuning, new sweep, new prediction generation, metric-chasing experiment, or traffic-impact modeling was performed
- the current recommended Phase 10 setting remains `boundary_band_pixels = 1` and `boundary_weight = 2.0`

### Physics-consistency guided surrogate refinement: target-wet recall consistency

Phase 25 converts the Phase 24 physical-consistency diagnosis into a targeted model refinement to reduce false-dry behavior and wet-area contraction.

Phase 25 artifacts include:

- `docs/phase25_physics_consistency_guided_refinement_plan.md`
- `utils/physics_losses.py`
- `configs/train_phase25_target_wet_recall_seed123_40e.json`
- `configs/train_phase25_target_wet_recall_seed42_40e.json`
- `configs/train_phase25_target_wet_recall_seed202_40e.json`
- `docs/phase25_target_wet_recall_implementation_note.md`
- `scripts/compare_phase25_target_wet_recall_aligned.py`
- `scripts/plot_phase25_summary_figures.py`
- `analysis/phase25_target_wet_recall_comparison/`
- `analysis/phase25_target_wet_recall_comparison/figures/`
- `docs/phase25_target_wet_recall_pilot_findings.md`
- `docs/phase25_seed42_guardrail_findings.md`
- `docs/phase25_three_seed_target_wet_recall_synthesis_findings.md`

The Phase 25 refinement indicates:

- Phase 10 boundary-band settings stayed fixed at `boundary_band_pixels = 1` and `boundary_weight = 2.0`
- `target_wet_recall_consistency` used `weight = 0.02`, `threshold = 0.05`, `temperature = 0.02`, and `eps = 1e-6`
- standard RMSE, MAE, and wet/dry IoU improved across `seed123`, `seed42`, and `seed202`
- mean standard test deltas versus Phase 10 were `RMSE = -0.007057`, `MAE = -0.001519`, `wet/dry IoU = +0.076670`, `rollout stability = +0.001035`, and `step RMSE std = -0.001071`
- false-dry rate and wet-area contraction improved in all three seeds
- mean aligned physical deltas versus Phase 10 were `false_dry_rate = -0.111321`, `wet_area_contraction = -0.079104`, `relative_volume_bias = +0.105093`, `peak_depth_underprediction = -0.014962`, `RMSE = -0.007244`, and `MAE = -0.001885`
- summary figures now show the three-seed standard metric deltas and aligned physical metric deltas
- high-risk cases showed especially strong false-dry and wet-area contraction reductions
- `false_wet_rate` increased slightly and `connectivity_loss_indicator` was not consistently improved
- Phase 25 is a strong three-seed positive candidate, not a complete hydrodynamic consistency solution or full SWE/PINN residual

## Practical Reading Guide

When reading the repository:

- use `M3 f025` as the overall project mainline reference
- use Phase 3.3 `af025` as the strongest static structured refinement reference
- treat Phase 6 `adapt025` as archived evidence that a larger adaptive range was too aggressive
- treat Phase 7/8 `adapt010` as the active adaptive candidate before margin-aware refinement
- read Phase 9 as the interpretability diagnosis explaining the wet/dry trade-off
- read Phase 10 as the successful first margin-aware intervention that establishes the current recommended refinement setting
- read Phase 12 as the first-pass reliability/applicability diagnosis of the current recommended model
- read Phase 13 as the representative visual explanation of the highest-ranked failure cases
- read Phase 14 as a proxy-based confidence and disagreement diagnosis, not as calibrated probabilistic uncertainty
- read Phase 15 as the first implementation of deterministic reliability screening and spatial risk mapping
- read Phase 16 as the first implementation of deterministic warning-rule guidance and applicability boundary interpretation
- read Phase 17 as the synthesis of Phase 12-16 into a reliability-aware warning framework narrative
- read Phase 18 as manuscript-oriented writing material derived from the Phase 12-17 reliability-aware warning framework
- read Phase 19 as manuscript-structure and submission consolidation derived from the completed Phase 12-18 materials
- read Phase 20 as the first full manuscript draft skeleton assembled from the Phase 18-19 manuscript-oriented materials
- read Phase 21 as claim-to-evidence and figure/table alignment for manuscript expansion, not as a new experiment
- read Phase 22 as the full academic manuscript draft expansion based on Phase 20 and Phase 21, not as a new experiment
- read Phase 23 as a representative warning-oriented case-study prototype, not as retraining, tuning, or new prediction generation
- read Phase 24 as physical-consistency diagnostics for existing Phase 10 outputs, not as retraining, tuning, new predictions, or a full physics-residual model
- read Phase 25 as a targeted target-wet recall and wet-region preservation refinement, not as a complete physical-consistency solution
- read Phase 26 as a strong-physics feasibility audit and conservation-proxy diagnostics phase, not as full conservation enforcement or SWE/PINN support
- read Phase 27 as a mixed seed42 conservative volume-response pilot: standard metrics improved, but the primary volume-response objective was not confirmed
- read Phase 28 as diagnostic-only failure analysis explaining why Phase 27 should not be directly expanded
- read Phase 29 as a mixed seed42 tolerance-band pilot: volume response was partially repaired, but the trade-off is not acceptable for confirmation
- read Phase 30 as documentation-only boundary synthesis: Level 4 conservation-proxy / physical-consistency-guided surrogate support is the current limit, while Level 5 SWE/PINN, strict mass conservation, and full hydrodynamic closure are not supported
- read Phase 31 as diagnostic-only physics input recovery readiness: Level 4+ static-map/domain/boundary/masked diagnostics are supported, while Level 5 remains unsupported
- read Phase 32 as design/diagnostic-only domain-/boundary-aware physical consistency guardrails: Level 4+ proxy diagnostics are formalized for possible future pilot design, while Level 5 remains unsupported
- read Phase 33 as diagnostic-only seed42 pilot readiness review: `manhole_nonzero_false_dry_guardrail` is the strongest future candidate, but `training_authorized = false`
- read Phase 34 as threshold-formalization only: baseline, acceptance, and rejection thresholds are fixed for a possible future `manhole_nonzero_false_dry_guardrail` pilot, but `training_authorized = false`
- read Phase 35 as pilot implementation planning only: the candidate is `manhole_nonzero_false_dry_guardrail`, the target is `manhole_nonzero_valid` `false_dry_rate`, and `training_authorized = false`
- read Phase 36 as code/smoke-test implementation only: the config-gated `manhole_nonzero_false_dry_guardrail` code path and guardrail checker are smoke-ready, but `training_authorized = false` and `training_executed = false`
- read Phase 37 as diagnostic seed42 training authorization review only: the next phase may run only the reviewed seed42 config, then must evaluate and run the Phase 36 guardrail checker before any seed expansion
- read Phase 38 as completed seed42 pilot training plus guardrail evaluation with rejection: useful negative evidence, not execution failure, and not support for seed expansion, a sweep, Phase 29 continuation, or post-hoc rescue
- read Phase 39 as diagnostic-only failed-pilot trade-off analysis: the Phase 38 narrow false-dry proxy improvement did not preserve broader Level 4+ guardrails, and the next technical work should be design review rather than additional training

## Key Documents

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
- `docs/phase18_manuscript_reliability_warning_layer_plan.md`
- `docs/manuscript_reliability_aware_warning_layer.md`
- `docs/phase19_manuscript_structure_consolidation_plan.md`
- `docs/manuscript_structure_and_submission_consolidation.md`
- `docs/phase20_manuscript_draft_assembly_plan.md`
- `docs/manuscript_draft_reliability_aware_urban_flood_warning.md`
- `docs/phase21_manuscript_evidence_figure_alignment_plan.md`
- `docs/manuscript_evidence_figure_table_alignment.md`
- `docs/phase22_manuscript_full_draft_expansion_plan.md`
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
- `docs/phase26_strong_physics_constraint_feasibility_plan.md`
- `docs/phase26_strong_physics_constraint_feasibility_findings.md`
- `docs/phase27_conservative_volume_response_consistency_plan.md`
- `docs/phase27_seed42_volume_response_pilot_findings.md`
- `docs/phase28_volume_response_loss_diagnosis_plan.md`
- `docs/phase28_volume_response_loss_diagnosis_findings.md`
- `docs/phase29_tolerance_band_volume_consistency_plan.md`
- `docs/phase29_seed42_tolerance_band_volume_findings.md`
- `docs/phase30_strong_physics_boundary_synthesis_plan.md`
- `docs/phase30_strong_physics_boundary_synthesis.md`
- `docs/phase31_physics_input_recovery_readiness_plan.md`
- `docs/phase31_physics_input_recovery_readiness_findings.md`
- `docs/phase32_domain_boundary_aware_physical_consistency_plan.md`
- `docs/phase32_domain_boundary_aware_design.md`
- `docs/phase32_domain_boundary_aware_physical_consistency_findings.md`
- `docs/phase33_seed42_pilot_readiness_review_plan.md`
- `docs/phase33_seed42_pilot_readiness_review_findings.md`
- `docs/phase34_pilot_threshold_formalization_plan.md`
- `docs/phase34_pilot_threshold_formalization_findings.md`
- `docs/phase35_manhole_false_dry_guardrail_pilot_plan.md`
- `docs/phase36_manhole_false_dry_guardrail_code_smoke_plan.md`
- `docs/phase36_manhole_false_dry_guardrail_code_smoke_findings.md`
- `docs/phase37_seed42_training_authorization_review_plan.md`
- `docs/phase37_seed42_training_authorization_review_findings.md`
- `docs/phase38_seed42_pilot_training_guardrail_evaluation_plan.md`
- `docs/phase38_seed42_pilot_training_guardrail_evaluation_findings.md`
- `docs/phase39_failed_pilot_tradeoff_diagnosis_plan.md`
- `docs/phase39_failed_pilot_tradeoff_diagnosis_findings.md`
- `docs/experiment_index.md`
