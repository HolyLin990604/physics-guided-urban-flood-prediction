# Phase 8 Batch 1 Results

## Scope

Phase 8 Batch 1 was the first narrow validation batch for `adapt010`.

Its purpose was to test whether the current adaptive candidate could hold up beyond the original decisive result without widening into a sweep.

---

## Case Results

### `seed202 / 40e`

This remains the decisive difficult-case support result.

`adapt010` beat the static Phase 3.3 `af025` control on the main final metrics and kept the adaptive direction viable.

### `seed123 / 40e`

This was a supportive repeatability check.

`adapt010` improved RMSE, MAE, rollout stability, and loss relative to the static control, but gave back some wet/dry IoU.

The result supports repeatability, but with a mixed IoU signal rather than a clean across-the-board win.

### `seed42 / 40e`

This was a strong full favorable-case guardrail pass.

`adapt010` improved RMSE, MAE, wet/dry IoU, and loss relative to the static control, with only a small rollout-stability decrease.

This means the adaptive candidate remains acceptable under the full favorable-case guardrail.

---

## Batch 1 Conclusion

The overall Phase 8 Batch 1 conclusion is:

- `adapt010` remains the active adaptive candidate
- the candidate now has meaningful early validation evidence
- the evidence is no longer dependent on the original `seed202` result alone
- validation should still remain narrow until a later batch justifies expansion
