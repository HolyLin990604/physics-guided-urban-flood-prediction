# Phase 40 Failed Pilot Design Review and Next Constraint Findings

## 1. Executive Summary

Phase 40 is a review-only and decision-only phase after the rejected Phase 38 seed42 pilot and the Phase 39 failed-pilot trade-off diagnosis.

No training was run in Phase 40. No loss, config, model architecture, threshold, or evaluation code was modified. Phase 40 only reviewed existing Phase 38 and Phase 39 evidence, compared next-direction options, and wrote decision artifacts.

The Phase 38 decision remains:

`seed42_pilot_rejected`

The Phase 39 diagnosis remains that the rejected pilot showed a Phase29-like trade-off pattern. The narrow `manhole_nonzero_false_dry_guardrail` proxy improved in its target region, but broader valid-domain, regional guardrail, and standard checks failed.

Phase 40 evaluated:

- `options_evaluated = 4`
- `criteria_rows = 13`

The selected Phase 40 decision is:

`pause_loss_redesign_move_to_swe_data_readiness`

Training remains unauthorized:

`training_authorized = false`

The recommended next phase is:

`phase41_swe_data_readiness_audit`

This conclusion does not claim pilot success, Phase 38 success, strict conservation, full mass conservation, SWE/PINN behavior, hydrodynamic closure, or Level 5 support.

## 2. Inputs and Outputs

Phase 40 used existing artifacts only.

Primary Phase 40 plan input:

- `docs/phase40_failed_pilot_design_review_next_constraint_plan.md`

Primary Phase 38 evidence reviewed:

- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_standard_metric_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_acceptance_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_rejection_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_guardrail_decision.json`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_guardrail_decision.md`

Primary Phase 39 evidence reviewed:

- `analysis/phase39_failed_pilot_tradeoff_diagnosis/failed_acceptance_components.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/triggered_rejection_rules.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/phase38_vs_baselines_metric_comparison.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/region_tradeoff_summary.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/scenario_tradeoff_summary.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/phase39_tradeoff_diagnosis_summary.json`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/phase39_tradeoff_diagnosis_summary.md`
- `docs/phase39_failed_pilot_tradeoff_diagnosis_findings.md`

Phase 40 review script:

- `scripts/review_phase40_next_constraint_decision.py`

Phase 40 outputs:

- `analysis/phase40_failed_pilot_design_review/next_constraint_options.csv`
- `analysis/phase40_failed_pilot_design_review/decision_criteria_matrix.csv`
- `analysis/phase40_failed_pilot_design_review/phase40_next_constraint_decision.json`
- `analysis/phase40_failed_pilot_design_review/phase40_next_constraint_decision.md`

This findings document summarizes those outputs without changing their decision status.

## 3. Phase 38 and Phase 39 Evidence Reviewed

Phase 38 ran the single authorized seed42 pilot using:

`configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`

The pilot used the `manhole_nonzero_false_dry_guardrail` proxy loss and was evaluated against the predeclared guardrail framework. The final Phase 38 decision was:

`seed42_pilot_rejected`

The rejection included failures in valid-domain RMSE, valid-domain MAE, valid-domain false-dry rate, high-impervious valid false-wet rate, boundary-ring false-dry rate, standard RMSE, standard MAE, and standard wet/dry IoU. The triggered rejection rules included:

- `RT01`
- `RT05`
- `RT07`

Phase 39 diagnosed the rejected pilot as negative evidence. Its central interpretation was that the pilot improved a narrow manhole-related false-dry proxy while failing to preserve broader valid-domain, regional guardrail, and standard behavior. `RT01` identified a Phase29-like trade-off pattern.

Phase 40 treats this evidence conservatively. It does not reinterpret the Phase 38 pilot as successful or partly accepted.

## 4. Option Comparison

Phase 40 compared four next-direction options.

| Option | Decision candidate | Score | Priority | Phase 40 interpretation |
| --- | --- | ---: | --- | --- |
| A | `redesign_level4_proxy_constraint_plan_first` | 60 | medium_low | Possible only as a future plan-first redesign; it does not authorize implementation or training. |
| B | `pause_loss_redesign_move_to_swe_data_readiness` | 88 | high | Conservative no-training pivot toward auditing data needed for future residual-style physical constraints. |
| C | `consolidate_negative_result_no_new_training` | 76 | medium | Valid negative-result consolidation, but less useful for identifying what evidence future physical constraints would require. |
| D | `decision_deferred_pending_more_evidence` | 35 | low | Fail-closed fallback if required evidence is missing or contradictory. |

The decision matrix included `criteria_rows = 13`. The criteria emphasized preserving the Phase 38 rejection, avoiding seed expansion, avoiding sweeps, avoiding post-hoc rescue, addressing the Phase29-like trade-off pattern, reducing narrow-proxy error-transfer risk, and keeping all claims within the allowed Phase 40 boundary.

## 5. Selected Decision

The selected decision is:

`pause_loss_redesign_move_to_swe_data_readiness`

This decision means the project should pause proxy-loss redesign rather than continue seed expansion, sweeps, or post-hoc rescue attempts.

The rationale is conservative:

- Phase 38 remains `seed42_pilot_rejected`.
- Phase 39 diagnosed a Phase29-like trade-off pattern.
- The narrow target proxy improvement was not enough to pass broader guardrails.
- Repeated proxy-loss attempts have shown trade-off limitations.
- The next useful step is to audit whether the data needed for future residual-style or SWE-oriented physical constraints is available.

This selected decision does not authorize SWE implementation. It only recommends a no-training data-readiness audit.

## 6. Why Training Remains Blocked

Training remains blocked because the most recent pilot evidence is rejected under the predeclared guardrail framework.

Phase 40 does not authorize:

- seed42 rerun;
- seed123 training;
- seed202 training;
- multi-seed expansion;
- sweeps;
- loss edits;
- config edits;
- model architecture edits.

The recorded Phase 40 decision field is:

`training_authorized = false`

The review found no evidence that another immediate training run would address the diagnosed trade-off mechanism. Running more training before resolving the design limitation would risk treating a rejected pilot as a tunable success path.

## 7. Why Seed Expansion / Sweeps / Rescue Remain Blocked

Seed expansion remains blocked because seed123 or seed202 would expand a rejected pilot design rather than address why the seed42 pilot failed.

Sweeps remain blocked because they would search around the same rejected proxy-loss design before the project has evidence that the design can avoid narrow-region error transfer.

Post-hoc rescue remains blocked because Phase 38 failed predeclared acceptance checks and triggered rejection rules. Phase 40 does not relabel the pilot as successful, mixed-positive, or acceptable.

The conservative interpretation is that the project should not continue optimizing the current proxy-loss family without stronger evidence that the design can preserve valid-domain, boundary, high-impervious, and standard behavior.

## 8. Why SWE Data Readiness Is the Recommended Next Step

Phase 40 recommends SWE data readiness because repeated proxy-loss attempts have shown trade-off limitations. The current evidence suggests that static-mask proxy losses can improve a narrow target while leaving broader physical or spatial behavior unresolved.

The recommended next step is therefore not an SWE/PINN implementation. It is only an audit of whether the data required for future residual-style or SWE-oriented constraints exists and is usable.

The Phase 41 audit should check availability of:

- `velocity_or_flux_fields`
- `dx_dy_grid_spacing`
- `dt_time_step`
- `boundary_conditions`
- `source_sink_terms`
- `pump_gate_operations`
- `hydrodynamic_state_variables`

If these inputs are unavailable, incomplete, or not aligned, the project should document that limitation before claiming readiness for stronger physical constraints.

## 9. What Is Not Allowed Next

The selected Phase 40 decision does not allow:

- training;
- seed42 rerun;
- seed123 training;
- seed202 training;
- seed expansion;
- sweeps;
- loss redesign implementation;
- config edits;
- model architecture edits;
- post-hoc Phase 38 rescue;
- relabeling Phase 38 as successful;
- strict conservation claims;
- full mass conservation claims;
- SWE/PINN claims;
- hydrodynamic closure claims;
- Level 5 support claims.

It also does not authorize continuing Phase 29 or treating the Phase29-like trade-off pattern as solved.

## 10. What Is Allowed Next

The selected Phase 40 decision allows a no-training Phase 41 SWE data-readiness audit.

Allowed Phase 41 work may include:

- inventorying available data fields;
- checking whether velocity or flux variables exist;
- checking grid spacing and time-step metadata;
- checking boundary-condition availability;
- checking source, sink, pump, and gate operation records;
- checking whether hydrodynamic state variables are available and aligned;
- documenting missing data needed before future residual-style constraint design.

Allowed work should remain diagnostic and should not implement SWE residuals or modify the training system.

## 11. Level Boundary

Phase 40 remains a Level 4+ diagnostic/design-review phase. It does not advance the project to Level 5.

Phase 40 does not claim:

- strict conservation;
- full mass conservation;
- SWE/PINN behavior;
- hydrodynamic closure;
- Level 5 support.

The only forward-looking recommendation is a no-training readiness audit for data that might be needed before future residual-style or SWE-oriented physical constraints could be responsibly considered.

## 12. Final Conclusion

Phase 40 reviewed the failed Phase 38 pilot and the Phase 39 trade-off diagnosis without running training or changing the model system.

The evidence supports pausing proxy-loss redesign. The project should not continue seed expansion, sweeps, or rescue attempts around the rejected `manhole_nonzero_false_dry_guardrail` pilot. The conservative next step is:

`phase41_swe_data_readiness_audit`

This next step should audit data availability only. It should not claim SWE/PINN behavior, strict conservation, full mass conservation, hydrodynamic closure, or Level 5 support.
