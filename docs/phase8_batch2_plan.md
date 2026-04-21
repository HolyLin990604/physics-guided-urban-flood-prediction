# Phase 8 Batch 2 Plan

## Objective

Phase 8 Batch 2 has one objective:

**Trade-off and robustness positioning for `adapt010`.**

The goal is not to promote `adapt010` unconditionally. The goal is to define where it is actually stronger, where it remains mixed, and whether the evidence is stable enough to justify continued focused development.

## Why Batch 2 Is Needed

Phase 8 Batch 1 established meaningful early validation evidence:

- `seed202 / 40e` remains the decisive difficult-case support result
- `seed123 / 40e` provided supportive repeatability evidence, but with a mixed wet/dry IoU signal
- `seed42 / 40e` provided a strong full favorable-case guardrail pass

This is enough to keep `adapt010` active, but not enough to claim broad superiority.

Batch 2 is needed because the current unresolved question is no longer whether `adapt010` can work at all. The unresolved question is how its gains should be positioned relative to the static Phase 3.3 `af025` control:

- are the gains mainly RMSE/MAE-oriented?
- are wet/dry IoU changes consistent or case-dependent?
- does difficult-case behavior remain favorable without damaging favorable-case behavior?
- is the adaptive mechanism stable and interpretable enough to keep as the focused direction?

## What Batch 2 Is Not Doing

Batch 2 is not:

- a Phase 9 start
- a broad architecture search
- a parameter sweep
- a return to `adapt025`
- a model-code or training-code change
- a new configuration-family expansion
- a claim that `adapt010` is the new overall mainline

`M3 f025` remains the overall best-balanced mainline reference. Phase 3.3 `af025` remains the strongest static structured refinement and the correct static control for this comparison.

## Minimum Experiment Package

The minimum Batch 2 package should stay narrow and comparison-focused.

Any new experimental work in Batch 2 should be limited to at most one explicitly motivated comparison, not a sweep.

Required comparisons:

- `adapt010` versus static Phase 3.3 `af025`
- full `40e` comparisons only where the matching static control and adaptive result are available or explicitly produced
- case-level interpretation for `seed202`, `seed123`, and `seed42`

Required reported metrics:

- `val_rmse`
- `val_mae`
- `val_wet_dry_iou`
- `val_rollout_stability`
- `val_loss`

Required qualitative or behavioral checks:

- difficult-case behavior on `seed202`
- repeatability behavior on `seed123`
- favorable-case guardrail behavior on `seed42`
- whether metric gains align with visible or process-level behavior where paired artifacts are available

## Required Batch 2 Outputs

Batch 2 should produce:

- one compact per-seed comparison table versus static Phase 3.3 `af025`
- one final positioning note / decision note for `adapt010`

## Mandatory Work

Batch 2 must:

- keep `adapt010` as the only adaptive candidate under review
- compare against the static Phase 3.3 `af025` control
- separate RMSE/MAE interpretation from wet/dry IoU interpretation
- report cases where `adapt010` improves some metrics but gives back others
- preserve the distinction between active adaptive candidate and overall project mainline
- document the end-of-batch decision without inflated claims

## Optional Work

Optional work is allowed only if it directly supports trade-off positioning:

- add a compact table that groups Batch 1 and Batch 2 evidence by seed
- add paired qualitative notes if artifacts already exist or are cheap to generate
- lightly sync `docs/project_status.md` or `docs/experiment_index.md` after Batch 2 conclusions are known

Optional work should not expand the experiment family.

## Success Criteria

Batch 2 succeeds if it produces a clearer position for `adapt010`, even if that position is mixed.

A successful Batch 2 should answer:

- where `adapt010` is stronger than `af025`
- whether the advantage is primarily RMSE/MAE-oriented, IoU-oriented, or mixed
- whether difficult-case and favorable-case behavior remain compatible
- whether repeatability evidence supports continued narrow validation
- whether the adaptive mechanism remains stable enough to justify focused development

Batch 2 does not require universal improvement on every metric and seed. It does require honest trade-off accounting.

## End-Of-Batch Decision Rule

At the end of Batch 2:

- continue focused `adapt010` development if it remains stable, improves the main error metrics on the important cases, and does not show a blocking IoU or guardrail regression
- keep `adapt010` active but limited if gains are useful but clearly metric-dependent or case-dependent
- pause adaptive expansion if Batch 2 shows inconsistent behavior that cannot be explained by the current trade-off framing
- do not reopen `adapt025` unless a separate future rationale is documented outside Phase 8 Batch 2

The expected decision output is a narrow positioning statement, not a new phase or a broad roadmap.
