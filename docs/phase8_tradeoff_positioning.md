# Phase 8 Trade-Off Positioning

## Established By Batch 1

Phase 8 Batch 1 established that `adapt010` remains a viable adaptive candidate after narrow validation.

Current Batch 1 reading:

- `seed202 / 40e` remains the decisive difficult-case support result
- `seed123 / 40e` supports repeatability, but the wet/dry IoU signal is mixed
- `seed42 / 40e` is a strong full favorable-case guardrail pass

This means the evidence is no longer dependent on the original `seed202` result alone. It does not mean `adapt010` has replaced the project mainline.

## What Remains Unresolved

The unresolved issue is trade-off positioning.

`adapt010` needs to be interpreted against the static Phase 3.3 `af025` control, not as a standalone improvement claim. The remaining questions are:

- whether its gains are mainly in RMSE and MAE
- whether wet/dry IoU improvement is consistent or case-dependent
- whether rollout stability changes are small enough to remain acceptable
- whether difficult-case gains and favorable-case guardrail behavior can coexist
- whether the adaptive scalar is interpretable enough to keep as the focused development direction

Any new Batch 2 experiment should therefore be limited to at most one explicitly motivated comparison, not a sweep.

## Seed Interpretation

### `seed202`

`seed202` is the decisive difficult-case reference.

It matters because previous stages showed that stronger structured refinement can help this case. For `adapt010`, this seed is the main evidence that a conservative adaptive range can improve difficult-case behavior relative to the static `af025` control.

### `seed123`

`seed123` is the repeatability reference.

It should be read as a check on whether the `adapt010` signal generalizes beyond the two anchor cases. Batch 1 made this supportive but not clean: RMSE, MAE, rollout stability, and loss improved, while wet/dry IoU was weaker.

This makes `seed123` important for trade-off interpretation rather than simple pass/fail promotion.

### `seed42`

`seed42` is the favorable-case guardrail reference.

It matters because adaptive refinement should not damage a case where the project already has strong behavior. Batch 1 showed a full `40e` guardrail pass for `adapt010`, which keeps the candidate viable.

## Metrics That Matter Most

Batch 2 should separate error reduction from inundation-structure behavior.

Primary error metrics:

- `val_rmse`
- `val_mae`
- `val_loss`

Structural and process checks:

- `val_wet_dry_iou`
- paired spatial behavior where artifacts are available
- paired region or process behavior where artifacts are available

Stability guardrail:

- `val_rollout_stability`

The main interpretation should not collapse all metrics into a single win/loss label. A useful Batch 2 result may show stronger RMSE/MAE behavior with mixed IoU behavior.

## Required Batch 2 Outputs

Batch 2 should produce:

- one compact per-seed comparison table versus static Phase 3.3 `af025`
- one final positioning note / decision note for `adapt010`

## Key Batch 2 Questions

Batch 2 must answer four questions.

### Where is `adapt010` actually stronger?

The comparison should identify which seeds and metrics favor `adapt010` over static `af025`, and which do not.

### Are gains RMSE/MAE-oriented or IoU-oriented?

Batch 1 already suggests that RMSE/MAE gains may be more consistent than wet/dry IoU gains. Batch 2 should confirm whether this is the correct interpretation.

### Are difficult-case and favorable-case behaviors consistent?

The candidate remains useful only if difficult-case improvement does not come with unacceptable favorable-case regression. `seed202` and `seed42` should therefore be interpreted together.

### Is `adapt010` stable and interpretable enough for continued focused development?

The answer should consider:

- final validation metrics
- rollout stability
- whether mixed IoU behavior has a plausible case-level explanation
- whether the conservative adaptive range remains easier to defend than the closed `adapt025` setting

## Current Position Before Batch 2

Before Batch 2, the defensible position is:

- `adapt010` is the active adaptive candidate
- Phase 8 Batch 1 provides meaningful early validation evidence
- the candidate appears stronger on important error metrics, but IoU behavior still needs clearer positioning
- further work should remain narrow and hypothesis-driven

Batch 2 should convert this from early support into a sharper trade-off statement.
