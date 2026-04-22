# Phase 9 Seed123 Spatial Wet/Dry Trade-Off Diagnosis

- static run root: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123`
- adapt010 run root: `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123`
- selected artifact epoch: `epoch_040`
- selected batches: `val_batch_0000, val_batch_0001`
- selected steps: `9, 10`
- wet threshold: `0.05`
- near-threshold target margin: `+/- 0.005`

## Artifact Paths Used

- val_batch_0000: static `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/visualizations/epoch_040/val_batch_0000/forecast_maps.npz`, adapt010 `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/visualizations/epoch_040/val_batch_0000/forecast_maps.npz`
- val_batch_0001: static `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_40e_seed123/visualizations/epoch_040/val_batch_0001/forecast_maps.npz`, adapt010 `runs/phase8_validation_temporal_gate_residual_response_split_protected_h16_a010_f025_af025_adapt010_40e_seed123/visualizations/epoch_040/val_batch_0001/forecast_maps.npz`

## Step Summary

| step | static IoU | adapt010 IoU | IoU delta | FP delta | FN delta | pred wet-area delta | static boundary FP/FN | adapt010 boundary FP/FN | shift reading |
|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| 9 | 0.754548 | 0.664582 | -0.089966 | 2210 | -272 | 0.037872 | FP 0.814164, FN 0.945205 | FP 0.612524, FN 0.942601 | wet-expansive, FP-growth dominated |
| 10 | 0.736915 | 0.739936 | 0.003020 | -1172 | 826 | -0.030487 | FP 0.796875, FN 0.961658 | FP 0.807851, FN 0.948632 | dry-conservative, FN-growth dominated |

## Interpretation

- Step 9 is wet-expansive for adapt010 in the inspected paired artifacts: FP changes by `2210` while FN changes by `-272`, and prediction wet-area ratio changes by `0.037872`. The IoU loss is therefore FP-growth dominated in this subset.
- Step 10 shifts in the opposite direction: adapt010 is dry-conservative relative to static af025, with FP changing by `-1172` and FN changing by `826`. IoU is nearly flat to slightly higher in this subset (`0.003020`), so the transition is not a step-10 IoU failure despite increased FN.
- Boundary ratios are high for FP/FN errors in both models, supporting a boundary/wet-margin interpretation for these selected artifacts. This is based on a simple one-pixel target wet/dry boundary band, not a hydrologic boundary model.
- The obvious step difference is direction: step 9 expands wet predictions and loses IoU through FP growth, while step 10 contracts wet predictions and trades lower FP for higher FN.
- This summary is limited to the paired `forecast_maps.npz` artifacts listed above and should not be read as a full validation-set spatial conclusion.

## Compact Mask Artifacts

For each selected batch and step, `spatial_masks_<batch>_stepXX.npz` stores target/static/adapt010 wet masks, FP/FN masks, error-class masks, one-pixel target boundary bands, target near-threshold masks, and absolute-error arrays. Error class encoding is `0=TN`, `1=TP`, `2=FP`, `3=FN`.