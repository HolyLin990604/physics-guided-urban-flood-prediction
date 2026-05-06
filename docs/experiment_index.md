# Experiment Index

## Active Project References

- `M3 f025`: overall best-balanced mainline reference
- Phase 3.3 `af025`: strongest static structured refinement
- Phase 7/8 `adapt010`: active adaptive candidate before margin-aware refinement
- Phase 10 boundary-band refinement: current recommended margin-aware setting, with `boundary_band_pixels = 1` and `boundary_weight = 2.0`
- Phase 12 reliability/applicability diagnosis: first-pass reliability boundary analysis of the current Phase 10 recommended model

## Phase 6

- Document: `docs/phase6_pilot_a_results.md`
- Status: closed as a negative/neutral result
- Takeaway: the adaptive scalar mechanism was stable, but `adapt025` did not remain better than the static Phase 3.3 `af025` control after full training

## Phase 7

- Document: `docs/phase7_adapt010_results.md`
- Status: active adaptive candidate established
- Takeaway: the conservative `adapt010` follow-up improved the decisive difficult-case `seed202 / 40e` result and also passed the favorable-case `seed42 / 5e` guardrail check

## Phase 8 Batch 1

- Document: `docs/phase8_batch1_results.md`
- Status: early validation support established
- Takeaway: `adapt010` remained favorable across a narrow Phase 8 Batch 1 check, with decisive difficult-case support, supportive repeatability evidence, and a strong full favorable-case guardrail pass

## Phase 8 Batch 2

- Documents: `docs/phase8_batch2_plan.md`, `docs/phase8_tradeoff_positioning.md`
- Status: trade-off positioning complete
- Takeaway: `adapt010` showed consistent RMSE/MAE/loss gains across the three required full `40e` comparisons, with mixed wet/dry IoU because of `seed123` and no favorable-case guardrail failure. No new architecture search or broader sweep was justified by Batch 2 evidence

## Phase 9

- Documents: `docs/phase9_interpretability_diagnosis_plan.md`, `docs/phase9_interpretability_findings.md`
- Status: interpretability and trade-off diagnosis complete
- Takeaway: the `seed123` wet/dry IoU give-back was best explained as a mixed, margin-region, step-dependent wet/dry trade-off. The diagnosis did not indicate adaptive multiplier saturation or seed-specific mechanism instability

## Phase 10

- Document: `docs/phase10_margin_aware_findings.md`
- Status: first margin-aware intervention complete
- Takeaway: boundary-band weighted wet/dry consistency refinement passed test-facing confirmation across `seed123`, `seed42`, and `seed202`
- Recommended setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`
- Rollback setting: `boundary_weight = 1.5` only
- Decision: no broader boundary-weight sweep is justified at this point

## Phase 12

- Plan: `docs/phase12_reliability_applicability_plan.md`
- Script: `scripts/analyze_phase12_reliability.py`
- Visualization script: `scripts/plot_phase12_reliability.py`
- Findings: `docs/phase12_reliability_applicability_findings.md`
- Outputs: `analysis/phase12_reliability/`
- Status: first-pass reliability/applicability diagnosis complete
- Takeaway: the Phase 10 recommended model is useful for rapid spatiotemporal flood-process approximation, but reliability is lower at exact wet/dry boundary cells, shallow threshold-adjacent areas, moderate-to-deep depths, high-intensity `location2` cases, and local peak-depth extremes
- Decision: no model retraining, architecture change, Phase 10 loss change, or boundary-weight sweep was performed

## Interpretation Order

For current repository interpretation, read the experiment trail in this order:

1. `docs/phase6_pilot_a_results.md`
2. `docs/phase7_adapt010_results.md`
3. `docs/phase8_batch1_results.md`
4. `docs/phase8_tradeoff_positioning.md`
5. `docs/phase9_interpretability_findings.md`
6. `docs/phase10_margin_aware_findings.md`
7. `docs/phase12_reliability_applicability_findings.md`
8. `docs/project_status.md`

## Next Stage

The next stage should build on the Phase 12 reliability/applicability diagnosis rather than reopening Phase 10 tuning.

Recommended next work:

- optionally add representative failure-case visual summaries
- consider uncertainty or confidence diagnostics for boundary and high-intensity failure cases
- keep the current Phase 10 setting fixed unless a new diagnosis clearly justifies a targeted intervention
- update the README after Phase 12 documentation review
