# Project Status

## Current Conclusion

The repository should currently be interpreted as follows:

- `M3 f025` remains the overall best-balanced mainline reference.
- Phase 3.3 `af025` remains the strongest static structured refinement.
- Phase 6 `adapt025` is closed as a negative/neutral adaptive result.
- Phase 7/8 `adapt010` remains the active adaptive candidate before margin-aware refinement.
- Phase 9 completed the interpretability and trade-off diagnosis for `adapt010`.
- Phase 10 completed the first margin-aware intervention and established the current recommended refinement setting: `boundary_band_pixels = 1`, `boundary_weight = 2.0`.

The current Phase 10 conclusion is that boundary-band weighted wet/dry consistency refinement has passed test-facing confirmation on the three key project seeds: `seed123`, `seed42`, and `seed202`.

No additional Phase 10 boundary-weight sweep is justified at this point.

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

## Practical Reading Guide

When reading the repository:

- use `M3 f025` as the overall project mainline reference
- use Phase 3.3 `af025` as the strongest static structured refinement reference
- treat Phase 6 `adapt025` as archived evidence that a larger adaptive range was too aggressive
- treat Phase 7/8 `adapt010` as the active adaptive candidate before margin-aware refinement
- read Phase 9 as the interpretability diagnosis explaining the wet/dry trade-off
- read Phase 10 as the successful first margin-aware intervention that establishes the current recommended refinement setting

## Key Documents

- `docs/phase6_pilot_a_results.md`
- `docs/phase7_adapt010_results.md`
- `docs/phase8_batch1_results.md`
- `docs/phase8_tradeoff_positioning.md`
- `docs/phase9_interpretability_findings.md`
- `docs/phase10_margin_aware_findings.md`
- `docs/experiment_index.md`
