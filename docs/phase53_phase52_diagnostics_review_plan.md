# Phase 53 Phase 52 Diagnostics Review Plan

## 1. Executive Summary

Phase 53 is a no-training diagnostic review of the completed Phase 52 controlled UrbanFlood24 128x128 seed42 40-epoch longer-run baseline.

Phase 52 substantially improved over the directly comparable Phase 47 10-epoch baseline across all retained aggregate test metrics. Phase 53 will determine whether those gains also appear in scenario reliability, timestep reliability, wet/dry failure modes, peak-depth and timing behavior, volume-response proxies, and the conservative warning framework previously established in Phases 48 and 49.

Phase 53 will use the Phase 52 best checkpoint and retained results without modifying model weights, architecture, loss, configuration basis, dataset split, or training protocol. It will compare Phase 52 diagnostics against the Phase 48 diagnostics for the Phase 47 checkpoint and review how the Phase 49 warning-label distribution changes under the longer-run checkpoint.

The expected output directory is:

```text
analysis/phase53_phase52_diagnostics_review/
```

The expected conservative decision is:

```text
phase53_diagnostics_completed_for_later_expansion_review
```

This decision means the Phase 52 checkpoint has received the required diagnostic review. It does not authorize seed replication, seed123, seed202, 256x256 training, tile or multiscale training, sweeps, or loss redesign. Any later expansion must be considered in a separate reviewed decision phase.

## 2. Background from Phase 47-52

Phase 47 completed the first controlled UrbanFlood24 full-dataset 128x128 seed42 10-epoch baseline:

```text
test_rmse = 0.01109213042097205
test_mae = 0.00525291082279485
test_wet_dry_iou = 0.8255524213115374
test_rollout_stability = 0.998722607580324
test_step_rmse_std = 0.0012824604989987165
test_loss = 0.00110163203172912
```

Phase 48 evaluated the Phase 47 checkpoint using no-training reliability and physical-proxy diagnostics. It covered scenario and timestep error, wet/dry failures, peak behavior, and summed-depth volume-response proxies.

Phase 49 converted the Phase 48 results into conservative warning-framework labels:

```text
reliable = 1
caution = 12
high-risk = 35
```

These labels are conservative diagnostic screening labels. They are not calibrated probabilities, event probabilities, confidence intervals, or production alert guarantees.

Phase 50 consolidated the evidence and claim boundaries. Phase 51 then authorized one controlled longer-run experiment while deferring seed replication, higher resolution, and broader experimental expansion.

Phase 52 completed that controlled 128x128 seed42 40-epoch run:

```text
best_epoch = 40
test_rmse = 0.005160715272116552
test_mae = 0.002410597107882495
test_wet_dry_iou = 0.9130120601863988
test_rollout_stability = 0.9992842044060429
test_step_rmse_std = 0.0007178322914948391
test_loss = 0.0002713639403471764
```

Relative to Phase 47, Phase 52 achieved lower RMSE, MAE, step RMSE variation, and loss, together with higher wet/dry IoU and rollout stability. The best epoch was the final authorized epoch, and the retained trajectory was consistent with continued improvement or a late plateau within the 40-epoch cap.

These aggregate improvements justify diagnostic reassessment. They do not by themselves establish case-level reliability, eliminate false-dry risk, improve physical proxies in every scenario, reduce conservative warning risk, demonstrate seed robustness, or authorize resolution expansion.

## 3. Purpose of Phase 53

The purpose of Phase 53 is to evaluate whether the Phase 52 aggregate metric gains remain favorable under the established Phase 48 reliability and physical-proxy diagnostics and the Phase 49 warning framework.

Phase 53 should answer:

- Are Phase 52 errors lower across scenarios rather than only in aggregate?
- Is timestep reliability improved or at least not degraded?
- Are false-dry and false-wet rates improved across matched cases?
- Are peak-depth estimates and peak timing improved where aligned timestep data permit evaluation?
- Is the summed-depth volume-response proxy improved or at least not materially degraded?
- Do conservative warning labels shift from high-risk toward caution or reliable?
- Are any aggregate gains accompanied by new or concentrated failure modes?
- Is the diagnostic evidence complete enough for a later reviewed seed-replication decision?

Phase 53 is an evidence-review phase, not an expansion-authorization phase.

## 4. Diagnostic Inputs

Primary Phase 52 inputs:

```text
runs/phase52_full_downsample128_seed42_40e/checkpoints/best.pt
runs/phase52_full_downsample128_seed42_40e/metrics.csv
runs/phase52_full_downsample128_seed42_40e/metrics.json
configs/train_phase52_full_downsample128_seed42_40e.json
analysis/phase52_controlled_128x128_seed42_longer_run/phase52_training_summary.json
```

Phase 48 and Phase 49 reference inputs:

```text
analysis/phase48_full_dataset_reliability_physical_proxy/
analysis/phase49_full_dataset_warning_framework/
```

The review should also reuse the existing scenario index, static geodata index, dataset adapter, model loading code, evaluation definitions, split, wet threshold, and metadata joins used by the controlled Phase 47/48 route where required.

Before evaluation, Phase 53 must write:

```text
analysis/phase53_phase52_diagnostics_review/phase53_diagnostic_readiness.json
```

The readiness record should confirm:

- The Phase 52 best checkpoint exists and loads successfully.
- The checkpoint identifies epoch 40 as the selected best epoch.
- The Phase 52 configuration exists and passes the controlled-scope checks.
- Metrics CSV, metrics JSON, and training summary are present and mutually consistent.
- The Phase 48 and Phase 49 reference artifacts needed for comparison are present.
- The fixed test split and expected test scenario/window counts can be reconstructed.
- Model inference can run without optimization or weight modification.
- Prediction and target tensors are aligned for scenario and timestep diagnostics.
- Phase 48 metric definitions and Phase 49 warning thresholds or rule tables can be recovered.
- Any unavailable optional metadata or metric is explicitly recorded.

If compact Phase 52 predictions do not already exist, Phase 53 may run a no-gradient evaluation pass from `best.pt` to compute the required diagnostics. This is inference only and must not update model parameters, optimizer state, scheduler state, or checkpoints.

## 5. Diagnostic Outputs

Phase 53 should create:

```text
analysis/phase53_phase52_diagnostics_review/
  phase53_diagnostic_readiness.json
  scenario_reliability_metrics.csv
  step_reliability_metrics.csv
  wet_dry_error_metrics.csv
  peak_depth_timing_metrics.csv
  volume_response_proxy_metrics.csv
  location_type_summary.csv
  reliability_warning_levels.csv
  phase52_vs_phase48_diagnostic_comparison.csv
  phase53_diagnostics_summary.json
  phase53_diagnostics_summary.md
```

Optional low-risk figures may be written under:

```text
analysis/phase53_phase52_diagnostics_review/figures/
```

Permitted figures:

- Warning-level count comparison.
- False-dry and false-wet comparison.
- Volume-bias proxy comparison.
- Reliability metric boxplots or summary bars.

Figures must be generated only from retained diagnostic tables. They must not introduce new scoring systems, hidden normalization, unsupported uncertainty claims, or manual case relabeling.

## 6. Reliability Diagnostic Plan

Phase 53 should reproduce the Phase 48 reliability diagnostics for the Phase 52 best checkpoint using the same test split, sample alignment, metric definitions, and aggregation rules wherever compatible.

Required scenario-level metrics:

- RMSE.
- MAE.
- Wet/dry IoU.
- Rollout stability where available at the scenario level.
- Step RMSE mean and standard deviation.
- Valid timestep or window count.
- Missing or invalid metric flags.
- Conservative reliability label.

Required timestep-level metrics:

- Scenario ID.
- Window or sample identifier.
- Prediction step.
- RMSE.
- MAE where available.
- Wet/dry IoU where available.
- Valid-pixel count.
- Any stability field used by Phase 48.

The review should report:

- Mean, median, dispersion, and relevant quantiles across scenarios.
- Counts and proportions of scenarios improving, unchanged within tolerance, or degrading relative to Phase 48.
- Worst-performing scenarios under Phase 52.
- Scenarios with aggregate improvement but degraded reliability submetrics.
- Location or scenario-type concentration where existing metadata permits.

Phase 53 should not create more favorable reliability thresholds solely because Phase 52 has better aggregate metrics. Phase 48 thresholds and classification logic should be reused. If exact reuse is impossible because of an artifact or schema difference, the deviation must be documented and comparison fields affected by it must be marked non-equivalent.

## 7. Wet/Dry Error Diagnostic Plan

Phase 53 should evaluate wet/dry behavior using the same wet threshold used by the controlled Phase 47, Phase 48, and Phase 52 route.

Required metrics:

- Wet/dry IoU by scenario.
- False-dry rate.
- False-wet rate.
- False-dry count or valid-pixel fraction.
- False-wet count or valid-pixel fraction.
- Target-wet prevalence.
- Predicted-wet prevalence.
- Timestep concentration of false-dry and false-wet errors where available.

False-dry behavior must receive explicit review because it can suppress warnings in target-wet regions. False-wet behavior must also be retained because excessive false alerts can reduce warning credibility.

The Phase 52-versus-Phase 48 comparison should include:

- Mean and median false-dry rate change.
- Mean and median false-wet rate change.
- Counts of scenarios with lower, similar, or higher false-dry rates.
- Counts of scenarios with lower, similar, or higher false-wet rates.
- Cases where IoU improves while false-dry rate worsens.
- Cases where aggregate RMSE improves while wet/dry failure risk worsens.

No conclusion should rely on IoU alone when false-dry or false-wet behavior provides a conflicting signal.

## 8. Peak-Timing Diagnostic Plan

Phase 53 should reproduce the Phase 48 peak-depth and timing diagnostics where the Phase 52 inference outputs provide aligned timestep predictions.

Required metrics where available:

- Target peak depth by scenario.
- Predicted peak depth by scenario.
- Signed peak-depth bias.
- Absolute peak-depth error.
- Relative peak-depth error where numerically stable.
- Peak-depth underprediction flag or proxy.
- Target peak timestep.
- Predicted peak timestep.
- Signed and absolute peak-timing error.

The review should determine:

- Whether peak-depth underprediction is reduced.
- Whether peak-depth improvement is broad or concentrated in a small number of cases.
- Whether timing error improves, remains similar, or degrades.
- Whether lower aggregate RMSE masks delayed, early, or attenuated peaks.

Peak timing must be marked unavailable rather than inferred when timestep alignment is absent or ambiguous. Relative peak errors must avoid unstable division for near-zero target peaks and must follow the existing Phase 48 numerical safeguards.

## 9. Volume-Response Proxy Diagnostic Plan

Phase 53 should evaluate summed predicted depth against summed target depth using the same Phase 48 proxy definition.

Required metrics where available:

- Summed predicted depth by scenario.
- Summed target depth by scenario.
- Signed summed-depth bias.
- Absolute summed-depth error.
- Relative summed-depth error where numerically stable.
- Absolute relative volume-bias proxy.
- Optional timestep-level summed-depth bias.

The review should compare:

- Mean and median signed bias.
- Mean and median absolute relative bias.
- Counts of scenarios with improved or degraded proxy error.
- Directional under-response or over-response patterns.
- Location or scenario-type concentrations.
- Cases where RMSE improves while the volume-response proxy worsens.

These metrics are volume-response proxies based on summed depth. They do not establish strict conservation, full mass conservation, hydrodynamic closure, SWE consistency, or satisfaction of governing equations.

## 10. Warning-Framework Review Plan

Phase 53 should apply the Phase 49 conservative warning framework to the Phase 52 diagnostic results.

Required labels:

```text
reliable
caution
high-risk
```

The Phase 49 label definitions, thresholds, failure-driver rules, and label-to-action mappings should be preserved wherever the required fields are available. Phase 53 must not recalibrate thresholds to force a more favorable distribution.

`reliability_warning_levels.csv` should contain one row for every evaluated test scenario and include:

- Scenario and metadata identifiers.
- Phase 52 diagnostic metrics used by the rules.
- Phase 53 warning label.
- Warning action.
- Primary failure driver.
- Secondary failure drivers.
- Missing-metric flags.
- Phase 48 warning label for the matched scenario.
- Warning-label transition.

Required transition categories:

```text
improved
unchanged
worsened
not_comparable
```

The summary should report:

- Phase 53 counts and proportions for reliable, caution, and high-risk.
- Phase 48 reference counts of 1 reliable, 12 caution, and 35 high-risk.
- Full warning-label transition counts.
- Cases moving out of high-risk.
- Cases moving into high-risk.
- Cases retaining high-risk despite improved aggregate metrics.
- Dominant failure drivers before and after the longer run.

Warning labels remain uncalibrated diagnostic screening labels. A lower high-risk count would be favorable diagnostic evidence, not proof of calibrated confidence or operational readiness.

## 11. Phase 52 vs Phase 48 Comparison Plan

The direct diagnostic comparison should use matched Phase 52 and Phase 48 cases whenever possible.

`phase52_vs_phase48_diagnostic_comparison.csv` should include:

- Scenario ID and available metadata.
- Phase 48 metric values.
- Phase 52 metric values.
- Signed deltas.
- Favorable-direction indicators.
- Relative changes where numerically stable.
- Phase 48 warning label.
- Phase 53 warning label.
- Warning-label transition.
- Comparability status and reason.

Metrics should include, where available:

```text
rmse
mae
wet_dry_iou
false_dry_rate
false_wet_rate
peak_depth_bias
absolute_peak_depth_error
absolute_peak_timing_error
signed_volume_bias_proxy
absolute_relative_volume_bias_proxy
```

Comparison rules:

- Use identical scenario IDs, windows, timesteps, masks, thresholds, and aggregation definitions.
- Report matched sample counts and any unmatched cases.
- Preserve metric directionality: lower is favorable for error and absolute-bias metrics; higher is favorable for IoU and stability metrics.
- Avoid relative-change calculations when the reference value is zero or numerically unstable.
- Do not pool non-equivalent metrics into one composite score.
- Do not claim broad improvement when gains are driven by a small subset while important failure modes worsen elsewhere.

The comparison should distinguish:

- Broad diagnostic improvement.
- Mixed improvement with persistent failure modes.
- Aggregate improvement with diagnostic degradation.
- Incomplete or non-comparable evidence.

## 12. Guardrails

- No training in Phase 53.
- Do not run seed123 or seed202.
- Do not run seed replication.
- Do not run 256x256.
- Do not run tile, multiscale, or full 500x500 training.
- Do not run sweeps.
- Do not redesign the loss.
- Do not modify model, loss, configuration, or architecture.
- Do not update checkpoint weights.
- Do not implement SWE residuals.
- Do not implement PINN.
- Do not claim Level 5.
- Do not claim strict conservation, full mass conservation, or hydrodynamic closure.
- Do not claim calibrated probability warning labels.
- Do not claim production readiness.
- Do not authorize uncontrolled expansion.
- Do not treat improved aggregate RMSE, MAE, or IoU as sufficient evidence for seed or resolution expansion without diagnostics.
- Do not change the test split, wet threshold, masks, or metric definitions silently.
- Do not overwrite Phase 48, Phase 49, or Phase 52 artifacts.
- Do not present inference-only evaluation as training.
- Do not authorize seed replication or 256x256 training from Phase 53.

## 13. Success Criteria

Phase 53 is successful if:

- The Phase 52 checkpoint, metrics, configuration, and summary pass readiness checks.
- The Phase 48 and Phase 49 comparison artifacts are found and their rules are recoverable.
- No optimization or model-weight update occurs.
- The fixed Phase 52 test split is evaluated with the established diagnostic definitions.
- All required output tables and summaries are written.
- Scenario and timestep reliability metrics are produced where artifacts permit.
- False-dry and false-wet behavior is explicitly evaluated.
- Peak-depth and peak-timing behavior is evaluated where aligned data permit.
- Volume-response metrics remain explicitly labeled as proxies.
- Phase 49 warning rules are applied without favorable retuning.
- Phase 52 and Phase 48 diagnostics are compared on matched cases.
- Missing or non-comparable fields are explicitly identified.
- The summary identifies both improvements and persistent or newly concentrated failure modes.
- Claim boundaries and expansion guardrails remain intact.

Diagnostic success does not require every metric or every scenario to improve. A clear, reproducible finding of broad improvement, mixed behavior, degradation, or incomplete comparability is valid.

Allowed decision candidates:

```text
phase53_diagnostics_completed_for_later_expansion_review
phase53_diagnostics_completed_with_persistent_or_mixed_risk
phase53_diagnostics_completed_with_degradation
phase53_diagnostics_incomplete_due_to_missing_artifacts
phase53_diagnostics_blocked_by_checkpoint_or_evaluation_issue
```

No Phase 53 decision candidate should authorize new training.

## 14. Expected Interpretation

The preferred interpretation framework is:

### Broad Diagnostic Improvement

Use when matched scenario, timestep, wet/dry, peak, volume-response proxy, and warning-framework evidence generally improves or remains acceptable, with no material new failure concentration.

This result may support a later reviewed decision considering seed replication. It does not authorize seed replication in Phase 53.

### Mixed Improvement with Persistent Risk

Use when aggregate and several diagnostic metrics improve, but important false-dry, peak, timing, volume-bias, or high-risk warning cases remain.

This result should lead to targeted case review or additional no-training analysis before expansion is considered.

### Diagnostic Degradation

Use when Phase 52 aggregate metrics improve but one or more operationally important diagnostic families materially worsen, especially false-dry behavior, peak underprediction, timing error, volume-response proxy behavior, or warning-label risk.

This result should defer expansion and document the failure modes. It should not trigger an automatic loss or architecture redesign within Phase 53.

### Incomplete Evidence

Use when missing checkpoints, predictions, timestep alignment, reference rules, or matched identifiers prevent a defensible comparison.

This result should identify the exact missing evidence and should not be interpreted as diagnostic acceptance.

## 15. Final Conclusion

Phase 53 will perform a no-training reliability, physical-proxy, warning-framework, and matched-comparison review of the completed Phase 52 controlled 128x128 seed42 40-epoch checkpoint.

The phase will test whether Phase 52's substantial aggregate improvements over Phase 47 persist across scenario reliability, timestep behavior, wet/dry errors, peak behavior, volume-response proxies, and conservative warning labels. It will reuse the established Phase 48 and Phase 49 definitions wherever compatible and will document every material comparability limitation.

Only if the diagnostics improve or remain acceptable relative to Phase 48 and Phase 49 should a later reviewed decision consider seed replication. Phase 53 itself must not authorize seed replication, seed123, seed202, 256x256, tile or multiscale training, sweeps, loss redesign, SWE/PINN work, Level 5 claims, conservation claims, calibrated warning probabilities, production readiness, or uncontrolled expansion.
