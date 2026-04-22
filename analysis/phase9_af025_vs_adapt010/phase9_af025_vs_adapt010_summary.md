# Phase 9 af025 vs adapt010 Summary

Source priority: final validation metrics from `history.json`; `evaluation_*/metrics.json` is used only when a final validation field is unavailable.

| seed | role | RMSE/MAE/loss | wet/dry IoU | rollout stability |
|---|---|---|---|---|
| seed202 | difficult-case reference | adapt010_better | adapt010_better | static_better |
| seed123 | repeatability reference with mixed IoU | adapt010_better | static_better | adapt010_better |
| seed42 | favorable-case guardrail reference | adapt010_better | adapt010_better | static_better |

## Metric Values

### seed202: difficult-case reference

- static run: `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed202`
- adapt010 run: `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202`

| metric | static af025 | adapt010 | delta | direction | static source | adapt010 source |
|---|---:|---:|---:|---|---|---|
| val_rmse | 0.037756 | 0.036812 | -0.000944 | adapt010_better | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed202/history.json` | `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202/history.json` |
| val_mae | 0.016027 | 0.015720 | -0.000307 | adapt010_better | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed202/history.json` | `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202/history.json` |
| val_wet_dry_iou | 0.795961 | 0.807813 | 0.011851 | adapt010_better | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed202/history.json` | `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202/history.json` |
| val_rollout_stability | 0.992497 | 0.992127 | -0.000370 | static_better | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed202/history.json` | `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202/history.json` |
| val_loss | 0.013834 | 0.013404 | -0.000430 | adapt010_better | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed202/history.json` | `runs/phase7_conservative_adaptive_followup_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed202/history.json` |

### seed123: repeatability reference with mixed IoU

- static run: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123`
- adapt010 run: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123`

| metric | static af025 | adapt010 | delta | direction | static source | adapt010 source |
|---|---:|---:|---:|---|---|---|
| val_rmse | 0.075219 | 0.074357 | -0.000862 | adapt010_better | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/history.json` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/history.json` |
| val_mae | 0.027704 | 0.027257 | -0.000447 | adapt010_better | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/history.json` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/history.json` |
| val_wet_dry_iou | 0.614842 | 0.606377 | -0.008465 | static_better | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/history.json` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/history.json` |
| val_rollout_stability | 0.987675 | 0.989136 | 0.001461 | adapt010_better | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/history.json` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/history.json` |
| val_loss | 0.031969 | 0.030937 | -0.001032 | adapt010_better | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/history.json` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/history.json` |

### seed42: favorable-case guardrail reference

- static run: `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42`
- adapt010 run: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42`

| metric | static af025 | adapt010 | delta | direction | static source | adapt010 source |
|---|---:|---:|---:|---|---|---|
| val_rmse | 0.063549 | 0.056352 | -0.007197 | adapt010_better | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42/history.json` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42/history.json` |
| val_mae | 0.020504 | 0.018776 | -0.001728 | adapt010_better | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42/history.json` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42/history.json` |
| val_wet_dry_iou | 0.559320 | 0.636408 | 0.077088 | adapt010_better | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42/history.json` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42/history.json` |
| val_rollout_stability | 0.984907 | 0.984357 | -0.000550 | static_better | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42/history.json` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42/history.json` |
| val_loss | 0.022752 | 0.020574 | -0.002179 | adapt010_better | `runs/phase3_3_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed42/history.json` | `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed42/history.json` |
