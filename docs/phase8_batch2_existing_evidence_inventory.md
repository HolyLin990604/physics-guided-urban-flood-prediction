# Phase 8 Batch 2 Existing Evidence Inventory

## Scope

This inventory maps repository evidence relevant to Phase 8 Batch 2:

- `seed202`: difficult-case reference
- `seed123`: repeatability reference
- `seed42`: favorable-case guardrail reference

The required comparison is `adapt010` versus static Phase 3.3 `af025`.

## Evidence Summary

| seed | seed role | model / config identity | role | full 40e | primary metric source | key metrics available | qualitative / process artifacts | Batch 2 usability |
|---|---|---|---|---|---|---|---|---|
| `seed202` | difficult-case reference | `temporal_gate_residual_response_split_protected`, `a010/f025/af025` | static Phase 3.3 `af025` | yes | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed202/history.json` | yes: `val_rmse`, `val_mae`, `val_wet_dry_iou`, `val_rollout_stability`, `val_loss` | yes: `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed202/evaluation_test/` | usable as the static difficult-case control |
| `seed202` | difficult-case reference | `temporal_gate_residual_response_split_protected`, `a010/f025/af025/adapt010` | `adapt010` | yes | `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202/history.json` | yes: `val_rmse`, `val_mae`, `val_wet_dry_iou`, `val_rollout_stability`, `val_loss` | yes: `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202/visualizations/epoch_040/` | usable as the decisive difficult-case candidate result |
| `seed123` | repeatability reference | `temporal_gate_residual_response_split_protected`, `a010/f025/af025` | static Phase 3.3 `af025` | yes | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/history.json` | yes: `val_rmse`, `val_mae`, `val_wet_dry_iou`, `val_rollout_stability`, `val_loss` | yes: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/visualizations/epoch_040/` | usable as the repeatability static control |
| `seed123` | repeatability reference | `temporal_gate_residual_response_split_protected`, `a010/f025/af025/adapt010` | `adapt010` | yes | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/history.json` | yes: `val_rmse`, `val_mae`, `val_wet_dry_iou`, `val_rollout_stability`, `val_loss` | yes: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/visualizations/epoch_040/` | usable as the repeatability candidate result |
| `seed42` | favorable-case guardrail reference | `temporal_gate_residual_response_split_protected`, `a010/f025/af025` | static Phase 3.3 `af025` | yes | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42/history.json` | yes: `val_rmse`, `val_mae`, `val_wet_dry_iou`, `val_rollout_stability`, `val_loss` | yes: `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42/evaluation_test/` | usable as the favorable-case static control |
| `seed42` | favorable-case guardrail reference | `temporal_gate_residual_response_split_protected`, `a010/f025/af025/adapt010` | `adapt010` | yes | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42/history.json` | yes: `val_rmse`, `val_mae`, `val_wet_dry_iou`, `val_rollout_stability`, `val_loss` | yes: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42/visualizations/epoch_040/` | usable as the full favorable-case guardrail candidate result |

## Metric Values In Existing Run Histories

| seed | role | val_rmse | val_mae | val_wet_dry_iou | val_rollout_stability | val_loss |
|---|---|---:|---:|---:|---:|---:|
| `seed202` | static Phase 3.3 `af025` | 0.0377557039 | 0.0160268947 | 0.7959613860 | 0.9924974322 | 0.0138341115 |
| `seed202` | `adapt010` | 0.0368119974 | 0.0157201619 | 0.8078125060 | 0.9921274006 | 0.0134038284 |
| `seed123` | static Phase 3.3 `af025` | 0.0752188995 | 0.0277036250 | 0.6148424268 | 0.9876747310 | 0.0319689646 |
| `seed123` | `adapt010` | 0.0743570298 | 0.0272570301 | 0.6063774705 | 0.9891355038 | 0.0309368635 |
| `seed42` | static Phase 3.3 `af025` | 0.0635491393 | 0.0205040259 | 0.5593203035 | 0.9849066951 | 0.0227522201 |
| `seed42` | `adapt010` | 0.0563517565 | 0.0187763797 | 0.6364080256 | 0.9843570698 | 0.0205736460 |

## Documentation Evidence

| path | evidence type | Batch 2 relevance |
|---|---|---|
| `docs/phase7_adapt010_results.md` | result note with explicit `seed202 / 40e` metric table versus static `af025`; also includes `seed42 / 5e` guardrail context | supports `seed202` difficult-case comparison and historical promotion of `adapt010` |
| `docs/phase8_batch1_results.md` | summary result note for `seed202 / 40e`, `seed123 / 40e`, and `seed42 / 40e` | supports Batch 1 interpretation, but does not include metric tables |
| `docs/project_status.md` | current status summary | confirms `adapt010` is active and `af025` is the static control |
| `docs/experiment_index.md` | experiment index | points to Phase 7 and Phase 8 Batch 1 result documents |
| `docs/phase4_final_comparison.md` | older final comparison of M3 versus Phase 3.3 `af025` | useful only as background for static `af025`; not a direct `adapt010` comparison |

## Config Evidence

The currently tracked `configs/` directory does not contain the advanced Phase 3.3, Phase 7, or Phase 8 config files referenced in recent docs. Concrete run identity is therefore available primarily through run directory names and `history.json`.

Available config-like file:

- `runs/_tmp_phase8_control_af025_40e_seed42.json`

This file matches the static `af025` `seed42 / 40e` control setup and points output to `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42`.

## Figure And Artifact Evidence

Direct run artifacts exist for each required seed comparison:

- `seed202` static `af025`: `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed202/evaluation_test/`
- `seed202` `adapt010`: `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202/visualizations/epoch_040/`
- `seed123` static `af025`: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/visualizations/epoch_040/`
- `seed123` `adapt010`: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/visualizations/epoch_040/`
- `seed42` static `af025`: `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42/evaluation_test/`
- `seed42` `adapt010`: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42/visualizations/epoch_040/`

Older paired figures also exist:

- `assets/images/final/m3_vs_phase33_af025_seed202_maps.png`
- `assets/images/final/m3_vs_phase33_af025_seed202_timeseries.png`
- `assets/images/final/m3_vs_phase33_af025_seed42_maps.png`
- `assets/images/final/m3_vs_phase33_af025_seed42_timeseries.png`

These older paired figures are not direct `adapt010` evidence.

## Inventory Reading

The repository contains usable full `40e` metric evidence for all three required Batch 2 seed comparisons:

- `seed202`: static `af025` versus `adapt010`
- `seed123`: static `af025` versus `adapt010`
- `seed42`: static `af025` versus `adapt010`

The main limitation is not missing runs. The main limitation is consolidation: the evidence exists across run histories, visualization folders, and summary docs rather than in one Batch 2 result note.
