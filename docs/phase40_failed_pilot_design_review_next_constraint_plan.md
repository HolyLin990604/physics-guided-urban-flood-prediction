# Phase 40 Failed Pilot Design Review and Next Constraint Plan

## 1. Executive Summary

Phase 40 is a design-review and next-constraint decision phase after the rejected Phase 38 seed42 pilot and the Phase 39 trade-off diagnosis.

Phase 38 ran the single authorized seed42 pilot using `manhole_nonzero_false_dry_guardrail` and rejected it under the predeclared guardrail framework. Phase 39 diagnosed that rejection and found that the pilot improved a narrow `manhole_nonzero_valid` false-dry proxy while failing broader valid-domain, regional guardrail, and standard metrics. RT01 showed a Phase29-like trade-off pattern.

Phase 40 must decide the next technical direction before any future implementation work. It is diagnostic and design-review only. It does not train, rerun seed42, run seed123, run seed202, perform sweeps, modify losses, modify configs, modify model architecture, or rescue Phase 38 post hoc.

Expected review script:

`scripts/review_phase40_next_constraint_decision.py`

Expected output directory:

`analysis/phase40_failed_pilot_design_review/`

## 2. Background from Phase 38 and Phase 39

Phase 38 ran only the authorized seed42 pilot:

`configs/train_phase36_manhole_false_dry_guardrail_seed42_40e.json`

The pilot used the `manhole_nonzero_false_dry_guardrail` proxy loss and was evaluated against the Phase 34 acceptance and rejection guardrail framework. The final Phase 38 decision was:

`seed42_pilot_rejected`

Phase 38 failed broader acceptance checks including valid-domain RMSE, valid-domain MAE, valid-domain false-dry rate, high-impervious valid false-wet rate, boundary-ring false-dry rate, standard RMSE, standard MAE, and standard wet/dry IoU. It also triggered rejection rules including RT01 `phase29_tradeoff_pattern`, RT05 `standard_rmse_or_mae_worsens_beyond_tolerance`, and RT07 `valid_domain_error_worsens_beyond_acceptance_tolerance`.

Phase 39 diagnosed the rejected pilot as useful negative evidence. The key finding was that the pilot appeared to improve a narrow manhole-related false-dry proxy while transferring or amplifying error in broader valid-domain, boundary, high-impervious, and standard metric regions. This means Phase 40 should not assume that another static-mask proxy loss is justified without stronger design evidence.

Phase 40 starts from the premise that Phase 38 was rejected and Phase 39 documented a trade-off mechanism. The review must preserve that decision and use it to choose whether to redesign the Level 4+ proxy constraint, pause proxy-loss work, or consolidate the negative result.

## 3. Core Decision Questions

Phase 40 should answer:

1. Is there enough evidence to design a new Level 4+ proxy constraint that avoids narrow-region error transfer?
2. If a new proxy constraint is considered, should it be domain-balanced, boundary-aware, and paired across false-dry and false-wet behavior?
3. Did Phase 38-39 show a limitation of static-mask proxy constraints that should pause loss-redesign work?
4. Should the project move next toward auditing the data needed for future SWE residual constraints instead of modifying current proxy losses?
5. Should the project consolidate Phase 38-39 as a negative result with no new constraint and no new training?
6. What evidence is required before any future phase may authorize implementation, config changes, or training?

## 4. Candidate Next Directions

Phase 40 should review these candidate directions:

- Redesign a Level 4+ proxy constraint only if the design explicitly avoids narrow-region error transfer.
- Develop a domain-balanced, boundary-aware, false-dry-false-wet paired constraint design for later review.
- Pause proxy-loss work and audit the data needed for future SWE residual constraints.
- Document Phase 38-39 as a negative result showing limits of static-mask proxy constraints.

These are decision candidates, not implementation tasks. Phase 40 may compare options, define required evidence, and recommend a future planning path. It may not modify the codebase to implement any option.

## 5. Option A: Redesign Level 4+ Proxy Constraint

Option A is to plan a redesigned Level 4+ proxy constraint before any future implementation.

This option is viable only if the proposed design addresses the Phase 38-39 failure mechanism. A valid design should not simply increase weight on the original `manhole_nonzero_false_dry_guardrail` objective or narrow the same static mask further.

Required design properties:

- Balance target-region improvement against valid-domain RMSE and MAE preservation.
- Pair false-dry reduction with false-wet control.
- Include boundary-aware checks so boundary-ring false-dry behavior is not sacrificed.
- Include high-impervious valid checks so false-wet degradation is not hidden.
- Define pre-implementation review criteria before any loss code or config changes.
- Preserve Level 4+ proxy wording and avoid strict conservation, full mass conservation, SWE/PINN, hydrodynamic closure, or Level 5 claims.

Phase 40 may recommend this option only as:

`redesign_level4_proxy_constraint_plan_first`

This decision means a future phase may draft a design plan. It does not authorize training, loss edits, config edits, or architecture changes.

## 6. Option B: Pause Loss Redesign and Move to SWE Data Readiness

Option B is to pause proxy-loss redesign and move to a data-readiness audit for future SWE residual constraints.

This option treats Phase 38-39 as evidence that the current static-mask proxy path may be too brittle without richer physical inputs, boundary conditions, forcing terms, topology, and temporal state information. The next useful step would be to audit what data is missing before any future SWE residual constraint can be designed responsibly.

The audit may review needs such as:

- rainfall or inflow forcing availability;
- boundary condition availability;
- flow direction, connectivity, or drainage topology;
- elevation, slope, and roughness inputs;
- temporal state alignment and time-step consistency;
- valid-domain masks and wet/dry transition labels;
- whether existing outputs support residual-style diagnostics without claiming SWE closure.

Phase 40 may recommend this option only as:

`pause_loss_redesign_move_to_swe_data_readiness`

This decision does not claim SWE/PINN behavior and does not authorize SWE implementation. It only moves the next phase toward data-readiness review.

## 7. Option C: Consolidate Negative Result Without New Constraint

Option C is to consolidate Phase 38-39 as a negative result and avoid proposing a new constraint.

This option is appropriate if Phase 40 finds that the available evidence is insufficient to justify either a redesigned Level 4+ proxy constraint or a SWE data-readiness pivot. It would document that the static-mask manhole false-dry proxy produced localized improvement but unacceptable broader trade-offs under the predeclared guardrails.

The consolidation should preserve:

- Phase 38 final decision: `seed42_pilot_rejected`.
- Phase 39 diagnosis: narrow proxy improvement did not generalize safely.
- RT01 interpretation: the result showed a Phase29-like trade-off pattern.
- No post-hoc rescue or relabeling of the pilot.
- No new training or loss redesign authorization.

Phase 40 may recommend this option only as:

`consolidate_negative_result_no_new_training`

## 8. Decision Criteria

Phase 40 should evaluate each option against these criteria:

- Does the option directly address the Phase 38-39 trade-off mechanism?
- Does it avoid narrow-region error transfer?
- Does it protect valid-domain RMSE and MAE?
- Does it account for boundary-ring false-dry behavior?
- Does it account for high-impervious valid false-wet behavior?
- Does it preserve standard RMSE, MAE, and wet/dry IoU guardrails?
- Does it avoid post-hoc rescue of Phase 38?
- Does it avoid unauthorized training, seed expansion, sweeps, loss edits, config edits, and architecture edits?
- Does it keep claims at Level 4+ proxy scope unless explicitly moving only to data-readiness review?
- Is the evidence strong enough to justify a future planning phase?

Final decision candidates:

- `redesign_level4_proxy_constraint_plan_first`
- `pause_loss_redesign_move_to_swe_data_readiness`
- `consolidate_negative_result_no_new_training`
- `decision_deferred_pending_more_evidence`

## 9. Required Inputs

Phase 40 should use existing artifacts only.

Required Phase 38 inputs:

- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_standard_metric_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_acceptance_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_rejection_check.csv`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_guardrail_decision.json`
- `analysis/phase38_seed42_pilot_training_guardrail_evaluation/phase38_guardrail_decision.md`

Required Phase 39 inputs:

- `analysis/phase39_failed_pilot_tradeoff_diagnosis/failed_acceptance_components.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/triggered_rejection_rules.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/phase38_vs_baselines_metric_comparison.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/region_tradeoff_summary.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/scenario_tradeoff_summary.csv`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/phase39_tradeoff_diagnosis_summary.json`
- `analysis/phase39_failed_pilot_tradeoff_diagnosis/phase39_tradeoff_diagnosis_summary.md`

Required threshold context:

- `analysis/phase34_pilot_thresholds/baseline_metric_table.csv`
- `analysis/phase34_pilot_thresholds/acceptance_thresholds.csv`
- `analysis/phase34_pilot_thresholds/rejection_thresholds.csv`
- `analysis/phase34_pilot_thresholds/phase34_threshold_summary.json`
- `analysis/phase34_pilot_thresholds/phase34_threshold_summary.md`

Optional context may include prior design plans and findings from Phase 31, Phase 32, Phase 35, Phase 36, and Phase 37. Missing optional inputs should be recorded explicitly and should not be regenerated through training.

## 10. Expected Review Script

Phase 40 should implement:

`scripts/review_phase40_next_constraint_decision.py`

The script should be review-only. It must not train, evaluate a model checkpoint, modify configs, modify losses, modify architecture, or invoke any seed run.

The script should:

- read Phase 38 guardrail outputs;
- read Phase 39 trade-off diagnosis outputs;
- read Phase 34 threshold context;
- construct candidate next-direction options;
- score or classify each option against the decision criteria;
- identify required evidence for any future phase;
- write the decision matrix, final decision JSON, and final decision markdown.

The script should fail closed or mark the decision deferred if required inputs are missing or contradictory.

## 11. Expected Outputs

Phase 40 should write outputs to:

`analysis/phase40_failed_pilot_design_review/`

Required output files:

- `next_constraint_options.csv`
- `decision_criteria_matrix.csv`
- `phase40_next_constraint_decision.json`
- `phase40_next_constraint_decision.md`

Suggested fields for `next_constraint_options.csv`:

- `option_id`
- `option_name`
- `decision_candidate`
- `description`
- `addresses_phase38_phase39_tradeoff`
- `avoids_narrow_region_error_transfer`
- `requires_future_training`
- `requires_loss_change`
- `requires_config_change`
- `allowed_in_phase40`
- `notes`

Suggested fields for `decision_criteria_matrix.csv`:

- `criterion_id`
- `criterion`
- `option_a_redesign_level4_proxy`
- `option_b_swe_data_readiness`
- `option_c_consolidate_negative_result`
- `evidence_source`
- `review_note`

Suggested fields for `phase40_next_constraint_decision.json`:

- `phase`
- `phase38_decision`
- `phase39_interpretation`
- `final_decision_candidate`
- `training_authorized`
- `seed42_rerun_authorized`
- `seed123_authorized`
- `seed202_authorized`
- `swe_claim_authorized`
- `level5_claim_authorized`
- `required_next_phase`
- `decision_rationale`

## 12. Guardrails

Phase 40 must follow these guardrails:

1. Do not train.
2. Do not rerun seed42.
3. Do not run seed123.
4. Do not run seed202.
5. Do not perform sweeps.
6. Do not modify losses.
7. Do not modify configs.
8. Do not modify model architecture.
9. Do not rescue Phase 38 post hoc.
10. Do not continue Phase 29.
11. Do not claim pilot success.
12. Do not claim strict conservation.
13. Do not claim full mass conservation.
14. Do not claim SWE/PINN.
15. Do not claim hydrodynamic closure.
16. Do not claim Level 5 support.
17. Preserve the Phase 38 final decision as `seed42_pilot_rejected`.
18. Treat Phase 39 as diagnostic evidence, not as a justification for post-hoc acceptance.

Phase 40 may only review existing evidence, compare decision options, and write decision artifacts.

## 13. Success Criteria

Phase 40 succeeds if it:

- reviews Phase 38 and Phase 39 evidence without changing it;
- documents all candidate next directions;
- evaluates whether a redesigned Level 4+ proxy constraint can avoid narrow-region error transfer;
- evaluates whether proxy-loss redesign should pause in favor of SWE data-readiness audit;
- evaluates whether the negative result should be consolidated with no new constraint;
- writes `next_constraint_options.csv`;
- writes `decision_criteria_matrix.csv`;
- writes `phase40_next_constraint_decision.json`;
- writes `phase40_next_constraint_decision.md`;
- selects one final decision candidate or defers with clear missing-evidence reasons;
- explicitly states that no training, seed rerun, seed expansion, sweep, loss edit, config edit, or architecture edit is authorized.

## 14. Final Conclusion

Phase 40 reviews the failed pilot and decides the next technical direction. It does not authorize training or any post-hoc rescue.
