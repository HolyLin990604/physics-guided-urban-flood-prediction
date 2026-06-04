# Phase 48 Full-Dataset Reliability And Physical Proxy Diagnostics

- selected_decision: `phase48_diagnostics_ready_for_warning_framework_extension`
- checkpoint_found: `true`
- checkpoint_path: `C:/Users/39053/Documents/physics-guided-urban-flood-prediction/runs/phase47_full_downsample128_baseline_seed42_10e/checkpoints/best.pt`
- diagnostics_executed: `true`
- evaluated_split: `test`
- evaluated_scenarios: `48`
- evaluated_windows: `384`
- mean_rmse: `0.012037189189155709`
- mean_mae: `0.005252910632811514`
- mean_wet_dry_iou: `0.863043953275997`
- mean_false_dry_rate: `0.0911363765964386`
- mean_false_wet_rate: `0.003937674554837349`
- mean_absolute_relative_volume_bias_proxy: `0.021456503649973275`
- warning_level_counts: `{'caution': 12, 'reliable': 1, 'high-risk': 35}`
- no_training: `true`
- no_swe_pinn: `true`
- level5_supported: `false`

## Warning Thresholds

Scenario labels are conservative distribution-derived screening labels, not calibrated probabilities. A scenario is `reliable` only when RMSE is at or below the lower-tercile threshold, wet/dry IoU is at or above the upper-tercile threshold, and false-dry, false-wet, and absolute relative volume-bias proxies are not above their upper-tercile thresholds. A scenario is `high-risk` when any upper-quartile error proxy is triggered or wet/dry IoU is at or below its lower-quartile threshold. Remaining scenarios are `caution`.

- rmse_reliable_max: `0.011004068821235263`
- wet_dry_iou_reliable_min: `0.8860657485849278`
- rmse_high_risk_min: `0.013702530495076255`
- wet_dry_iou_high_risk_max: `0.8365939659875213`

## Scope Notes

These diagnostics are Level 4+ reliability and physical proxy diagnostics only. They do not implement SWE residuals, PINN components, strict conservation, full mass conservation, hydrodynamic closure, Level 5 support, or any training.

Next recommended action: Extend the warning framework using Phase 48 scenario labels as conservative diagnostics, not calibrated probabilities.