# Phase 8 Batch 2 Gap Assessment

## Required Comparisons

Phase 8 Batch 2 requires narrow comparison of `adapt010` against static Phase 3.3 `af025` for:

- `seed202`: difficult-case reference
- `seed123`: repeatability reference
- `seed42`: favorable-case guardrail reference

The required metrics are available in existing `history.json` files:

- `val_rmse`
- `val_mae`
- `val_wet_dry_iou`
- `val_rollout_stability`
- `val_loss`

## Supported By Existing Evidence

### `seed202`

Status: supported.

Evidence:

- static `af025`: `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed202/history.json`
- `adapt010`: `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202/history.json`
- documented metric table: `docs/phase7_adapt010_results.md`

Reading:

- full `40e` comparison exists
- all required metrics are available
- qualitative/process artifacts exist, although static control artifacts are under `evaluation_test/` while candidate artifacts are under `visualizations/epoch_040/`

### `seed123`

Status: supported.

Evidence:

- static `af025`: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/history.json`
- `adapt010`: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/history.json`
- summary note: `docs/phase8_batch1_results.md`

Reading:

- full `40e` comparison exists
- all required metrics are available
- artifacts exist for both runs under `visualizations/epoch_040/`
- Batch 1 summary already identifies the result as supportive but mixed because wet/dry IoU is weaker for `adapt010`

### `seed42`

Status: supported.

Evidence:

- static `af025`: `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42/history.json`
- `adapt010`: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42/history.json`
- summary note: `docs/phase8_batch1_results.md`
- available static-control config-like file: `runs/_tmp_phase8_control_af025_40e_seed42.json`

Reading:

- full `40e` comparison exists
- all required metrics are available
- qualitative/process artifacts exist, although static control artifacts are under `evaluation_test/` while candidate artifacts are under `visualizations/epoch_040/`
- Batch 1 summary already identifies this as a strong full favorable-case guardrail pass

## Incomplete Or Weak Areas

The required comparisons are not missing, but the evidence is fragmented:

- `docs/phase8_batch1_results.md` summarizes `seed123` and `seed42` without metric tables
- advanced config files referenced by docs are not present under `configs/`
- direct paired `adapt010` versus `af025` figure files are not consolidated under `assets/images/`
- some static-control qualitative artifacts are under `evaluation_test/`, while candidate artifacts are under `visualizations/epoch_040/`

These are documentation and consolidation gaps, not experimental gaps.

## Need For A New Experiment

Current repository evidence appears sufficient to complete Batch 2 without a new run.

No single missing comparison stands out as necessary because:

- `seed202 / 40e` already has static `af025` and `adapt010` metrics
- `seed123 / 40e` already has static `af025` and `adapt010` metrics
- `seed42 / 40e` already has static `af025` and `adapt010` metrics
- all required Batch 2 metrics are present for all three comparisons

## Why No Broader Sweep Is Justified

A broader sweep would violate the Batch 2 plan.

The current question is trade-off and robustness positioning for `adapt010`, not architecture search or adaptive-strength tuning. Existing evidence already covers:

- difficult-case behavior
- repeatability behavior
- favorable-case guardrail behavior
- RMSE/MAE versus wet/dry IoU trade-off
- rollout-stability guardrail

Additional runs would be hard to justify before consolidating the existing evidence into the required per-seed comparison table and final decision note.

## Conclusion

Batch 2 can proceed without new experiments.
