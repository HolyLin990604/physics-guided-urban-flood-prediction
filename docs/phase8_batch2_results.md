# Phase 8 Batch 2 Results

## Objective

Phase 8 Batch 2 consolidates existing evidence for one objective:

**Trade-off and robustness positioning for `adapt010`.**

No new experiments were required. The repository already contains full `40e` `adapt010` versus static Phase 3.3 `af025` comparisons for the required Batch 2 seeds.

## Compared Seeds

| seed | role | Batch 2 use |
|---|---|---|
| `seed202` | difficult-case reference | checks whether `adapt010` preserves the difficult-case gain |
| `seed123` | repeatability reference | checks whether the signal generalizes beyond the anchor cases |
| `seed42` | favorable-case guardrail reference | checks whether `adapt010` avoids unacceptable favorable-case regression |

## Evidence Sources

| seed | static Phase 3.3 `af025` source | `adapt010` source |
|---|---|---|
| `seed202` | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed202/history.json` | `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202/history.json` |
| `seed123` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/history.json` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/history.json` |
| `seed42` | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42/history.json` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42/history.json` |

Advanced tracked config files for these runs are unavailable in `configs/`; run identity is taken from run directory names and `history.json`.

## Key Metrics

### `seed202 / 40e`

| config | val_rmse | val_mae | val_wet_dry_iou | val_rollout_stability | val_loss |
|---|---:|---:|---:|---:|---:|
| static Phase 3.3 `af025` | 0.0377557039 | 0.0160268947 | 0.7959613860 | 0.9924974322 | 0.0138341115 |
| `adapt010` | 0.0368119974 | 0.0157201619 | 0.8078125060 | 0.9921274006 | 0.0134038284 |
| delta: `adapt010 - af025` | -0.0009437066 | -0.0003067329 | +0.0118511200 | -0.0003700316 | -0.0004302831 |

Reading:

- `adapt010` is stronger on RMSE, MAE, wet/dry IoU, and loss
- rollout stability is slightly lower
- this remains the strongest difficult-case support result

### `seed123 / 40e`

| config | val_rmse | val_mae | val_wet_dry_iou | val_rollout_stability | val_loss |
|---|---:|---:|---:|---:|---:|
| static Phase 3.3 `af025` | 0.0752188995 | 0.0277036250 | 0.6148424268 | 0.9876747310 | 0.0319689646 |
| `adapt010` | 0.0743570298 | 0.0272570301 | 0.6063774705 | 0.9891355038 | 0.0309368635 |
| delta: `adapt010 - af025` | -0.0008618697 | -0.0004465949 | -0.0084649563 | +0.0014607728 | -0.0010321011 |

Reading:

- `adapt010` is stronger on RMSE, MAE, rollout stability, and loss
- wet/dry IoU is weaker
- this supports repeatability, but the evidence is mixed rather than across-the-board

### `seed42 / 40e`

| config | val_rmse | val_mae | val_wet_dry_iou | val_rollout_stability | val_loss |
|---|---:|---:|---:|---:|---:|
| static Phase 3.3 `af025` | 0.0635491393 | 0.0205040259 | 0.5593203035 | 0.9849066951 | 0.0227522201 |
| `adapt010` | 0.0563517565 | 0.0187763797 | 0.6364080256 | 0.9843570698 | 0.0205736460 |
| delta: `adapt010 - af025` | -0.0071973828 | -0.0017276462 | +0.0770877221 | -0.0005496253 | -0.0021785741 |

Reading:

- `adapt010` is stronger on RMSE, MAE, wet/dry IoU, and loss
- rollout stability is slightly lower
- this is a full favorable-case guardrail pass

## Compact Per-Seed Comparison

| seed | seed role | RMSE/MAE reading | IoU reading | stability reading | overall Batch 2 reading |
|---|---|---|---|---|---|
| `seed202` | difficult-case | `adapt010` improves both | `adapt010` improves | slight decrease | supports difficult-case strength |
| `seed123` | repeatability | `adapt010` improves both | `adapt010` gives back IoU | `adapt010` improves | supportive but mixed |
| `seed42` | favorable-case guardrail | `adapt010` improves both | `adapt010` improves | slight decrease | guardrail pass |

## Qualitative / Process Evidence

Repository artifacts are available for qualitative/process inspection:

- `seed202` static `af025`: `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed202/evaluation_test/`
- `seed202` `adapt010`: `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202/visualizations/epoch_040/`
- `seed123` static `af025`: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/visualizations/epoch_040/`
- `seed123` `adapt010`: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/visualizations/epoch_040/`
- `seed42` static `af025`: `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42/evaluation_test/`
- `seed42` `adapt010`: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42/visualizations/epoch_040/`

Direct paired `adapt010` versus `af025` figure files are unavailable as consolidated assets. Therefore, Batch 2 does not claim additional qualitative findings beyond the metric-supported interpretation above.

## Trade-Off Interpretation

`adapt010` is consistently stronger on the main error metrics:

- RMSE improves on all three required seeds
- MAE improves on all three required seeds
- loss improves on all three required seeds

Wet/dry IoU is mixed:

- improves on `seed202`
- decreases on `seed123`
- improves on `seed42`

Rollout stability is acceptable but not uniformly improved:

- slightly lower on `seed202`
- higher on `seed123`
- slightly lower on `seed42`

The Batch 2 trade-off is therefore not a universal win. The strongest supported reading is that `adapt010` gives consistent RMSE/MAE-oriented gains, with mostly favorable but case-dependent IoU behavior.

## Guardrail Interpretation

The favorable-case guardrail is `seed42 / 40e`.

`adapt010` improves RMSE, MAE, wet/dry IoU, and loss relative to static `af025`, with only a small rollout-stability decrease. This does not show an unacceptable favorable-case regression.

Difficult-case and favorable-case behavior remain compatible under the current evidence:

- `seed202` supports difficult-case gain
- `seed42` passes the full favorable-case guardrail
- `seed123` adds repeatability support, but keeps IoU behavior mixed

## Decision Note

Batch 2 decision:

**Continue focused `adapt010` development.**

This decision is limited. `adapt010` remains the active adaptive candidate, not the overall project mainline. `M3 f025` remains the overall best-balanced mainline reference, and static Phase 3.3 `af025` remains the static structured refinement control.

## Final Positioning For `adapt010`

`adapt010` is stronger where RMSE, MAE, and loss are the priority. It improves these metrics across all three required Batch 2 seed comparisons.

Evidence is mixed for wet/dry IoU because `seed123` gives back IoU despite improving the main error metrics and rollout stability.

The gains should be described as primarily RMSE/MAE-oriented with case-dependent IoU behavior, not as a clean across-the-board improvement.

The candidate remains stable and interpretable enough for continued focused development because:

- all required full `40e` comparisons are available
- the difficult-case reference remains favorable
- the favorable-case guardrail passes
- the repeatability case is supportive but identifies the main trade-off

No new experiment or broader sweep is justified by Batch 2 evidence.
