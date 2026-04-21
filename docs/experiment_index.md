# Experiment Index

## Active Project References

- `M3 f025`: overall best-balanced mainline reference
- Phase 3.3 `af025`: strongest static structured refinement
- Phase 7/8 `adapt010`: current adaptive candidate

## Phase 6

- `docs/phase6_pilot_a_results.md`
- Status: closed as a negative/neutral result
- Takeaway: the adaptive scalar mechanism was stable, but `adapt025` did not remain better than the static Phase 3.3 `af025` control after full training

## Phase 7

- `docs/phase7_adapt010_results.md`
- Status: active adaptive candidate established
- Takeaway: the conservative `adapt010` follow-up improved the decisive difficult-case `seed202 / 40e` result and also passed the favorable-case `seed42 / 5e` guardrail check

## Phase 8 Batch 1

- `docs/phase8_batch1_results.md`
- Status: early validation support established
- Takeaway: `adapt010` remained favorable across a narrow Phase 8 Batch 1 check, with decisive difficult-case support, supportive repeatability evidence, and a strong full favorable-case guardrail pass

## Phase 8 Batch 2

- `docs/phase8_batch2_results.md`
- Status: trade-off positioning complete
- Takeaway: `adapt010` showed consistent RMSE/MAE/loss gains across the three required full `40e` comparisons, with mixed wet/dry IoU because of `seed123` and no favorable-case guardrail failure. No new experiment or broader sweep is justified by Batch 2 evidence

## Interpretation Order

For current repository interpretation, read the experiment trail in this order:

1. `docs/phase3_summary.md`
2. `docs/phase6_pilot_a_results.md`
3. `docs/phase7_adapt010_results.md`
4. `docs/phase8_batch1_results.md`
5. `docs/phase8_batch2_results.md`
6. `docs/project_status.md`
