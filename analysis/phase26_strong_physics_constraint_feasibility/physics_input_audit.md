# Phase 26 Physics Input Audit

This diagnostic audit is read-only except for the files in this Phase 26 output directory. It does not train models or change model/loss code.

## Dataset and Array Availability

- `.npy` files inspected: 0
- `forecast_maps.npz` files found under `runs/`: 3653
- `forecast_maps.npz` files considered for representative selection: 3000
- Representative `forecast_maps.npz` files inspected: 23

- None found

Top discovered `.npy` files:

No `.npy` files were found in the scanned repository directories.

## Shape Compatibility

- Representative flood spatial shape: `[128, 128]`
- Representative flood spatial shape source: `forecast_maps.npz`
- DEM/static elevation shape-compatible: `False`
- Report: Shape-compatible DEM/static elevation was not found in the scanned repository files.

## Representative Forecast Map Archives

| Phase | Seed | Split | Baseline role | Path | Keys | Prediction/target compatible |
| --- | --- | --- | --- | --- | --- | --- |
| phase10 | seed123 | evaluation_test | recommended_baseline_boundary_weight_2.0_w20 | `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase10 | seed202 | evaluation_test | recommended_baseline_boundary_weight_2.0_w20 | `runs/phase10_margin_aware_boundary_band_seed202_40e/evaluation_test/test_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase10 | seed42 | evaluation_test | recommended_baseline_boundary_weight_2.0_w20 | `runs/phase10_margin_aware_boundary_band_seed42_40e/evaluation_test/test_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase10 | seed123 | evaluation_test | rollback_or_non_default_boundary_weight_1.5 | `runs/phase10_margin_aware_boundary_band_w15_seed123_40e/evaluation_test/test_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase10 | seed42 | evaluation_test | rollback_or_non_default_boundary_weight_1.5 | `runs/phase10_margin_aware_boundary_band_w15_seed42_40e/evaluation_test/test_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase25 | seed123 | evaluation_test |  | `runs/phase25_target_wet_recall_seed123_40e/evaluation_test/test_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase25 | seed202 | evaluation_test |  | `runs/phase25_target_wet_recall_seed202_40e/evaluation_test/test_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase25 | seed42 | evaluation_test |  | `runs/phase25_target_wet_recall_seed42_40e/evaluation_test/test_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| other | seed123 | evaluation_test |  | `runs/phase2_loss_only_40e_seed123/evaluation_test/test_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| other | seed202 | evaluation_test |  | `runs/phase2_loss_only_40e_seed202/evaluation_test/test_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| other | seed42 | evaluation_test |  | `runs/phase2_loss_only_40e_seed42/evaluation_test/test_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase10 | seed123 | visualizations | recommended_baseline_boundary_weight_2.0_w20 | `runs/phase10_margin_aware_boundary_band_seed123_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase10 | seed202 | visualizations | recommended_baseline_boundary_weight_2.0_w20 | `runs/phase10_margin_aware_boundary_band_seed202_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase10 | seed42 | visualizations | recommended_baseline_boundary_weight_2.0_w20 | `runs/phase10_margin_aware_boundary_band_seed42_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| other | None | visualizations |  | `runs/ablation_phase2_rainfall_only/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase10 | seed123 | visualizations | rollback_or_non_default_boundary_weight_1.5 | `runs/phase10_margin_aware_boundary_band_w15_seed123_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase10 | seed42 | visualizations | rollback_or_non_default_boundary_weight_1.5 | `runs/phase10_margin_aware_boundary_band_w15_seed42_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase25 | seed123 | visualizations |  | `runs/phase25_target_wet_recall_seed123_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase25 | seed202 | visualizations |  | `runs/phase25_target_wet_recall_seed202_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| phase25 | seed42 | visualizations |  | `runs/phase25_target_wet_recall_seed42_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| other | seed123 | visualizations |  | `runs/phase2_loss_only_40e_seed123/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| other | seed202 | visualizations |  | `runs/phase2_loss_only_40e_seed202/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |
| other | seed42 | visualizations |  | `runs/phase2_loss_only_40e_seed42/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` |

## Existing Model Output Availability

### Phase10

- Prediction/target map arrays: `supported`
- Evaluation-test prediction/target arrays available: `True`
- Prediction/target arrays shape-compatible: `True`
- Candidate files found: 1000 (showing 200)
- Note: Evaluation-test forecast_maps.npz files have recognizable prediction and target arrays; these are preferred over visualization epoch artifacts.

- Representative map: `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.12070449441671371 max=2.4008681774139404 mean=0.05587907135486603, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=1.9651845693588257 mean=0.06030810996890068, error:unknown [2, 12, 1, 128, 128] float32 min=1.4901161193847656e-08 max=0.7774874567985535 mean=0.02360084466636181)
- Representative map: `runs/phase10_margin_aware_boundary_band_seed202_40e/evaluation_test/test_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.11852642148733139 max=2.168839693069458 mean=0.05327525734901428, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=1.9651845693588257 mean=0.06030810996890068, error:unknown [2, 12, 1, 128, 128] float32 min=5.960464477539063e-08 max=0.7447614073753357 mean=0.020519280806183815)
- Representative map: `runs/phase10_margin_aware_boundary_band_seed42_40e/evaluation_test/test_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.08345811069011688 max=2.21053147315979 mean=0.053083062171936035, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=1.9651845693588257 mean=0.06030810996890068, error:unknown [2, 12, 1, 128, 128] float32 min=5.960464477539063e-08 max=0.8091593980789185 mean=0.022646596655249596)
- Representative map: `runs/phase10_margin_aware_boundary_band_w15_seed123_40e/evaluation_test/test_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.10179966688156128 max=2.589306592941284 mean=0.054796699434518814, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=1.9651845693588257 mean=0.06030810996890068, error:unknown [2, 12, 1, 128, 128] float32 min=1.4901161193847656e-08 max=0.9248275756835938 mean=0.023872874677181244)
- Representative map: `runs/phase10_margin_aware_boundary_band_w15_seed42_40e/evaluation_test/test_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.09008081257343292 max=2.1648619174957275 mean=0.0528779961168766, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=1.9651845693588257 mean=0.06030810996890068, error:unknown [2, 12, 1, 128, 128] float32 min=7.450580596923828e-08 max=0.8344137072563171 mean=0.023432141169905663)
- Representative map: `runs/phase10_margin_aware_boundary_band_seed123_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.5915942788124084 max=0.5249144434928894 mean=-0.017316928133368492, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=2.0691962242126465 mean=0.06826271116733551, error:unknown [2, 12, 1, 128, 128] float32 min=2.086162567138672e-07 max=2.046875 mean=0.10660233348608017)
- Representative map: `runs/phase10_margin_aware_boundary_band_seed202_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.9094162583351135 max=0.5055135488510132 mean=-0.02639458328485489, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=2.0103728771209717 mean=0.0626683160662651, error:unknown [2, 12, 1, 128, 128] float32 min=4.76837158203125e-07 max=1.974035620689392 mean=0.11587145179510117)
- Representative map: `runs/phase10_margin_aware_boundary_band_seed42_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-1.0888954401016235 max=0.44077393412590027 mean=-0.01249992847442627, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=2.096503734588623 mean=0.07221103459596634, error:unknown [2, 12, 1, 128, 128] float32 min=4.246830940246582e-07 max=1.9742889404296875 mean=0.13399963080883026)
- Representative map: `runs/phase10_margin_aware_boundary_band_w15_seed123_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.578786313533783 max=0.513146698474884 mean=-0.0187271386384964, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=2.0691962242126465 mean=0.06826271116733551, error:unknown [2, 12, 1, 128, 128] float32 min=1.6391277313232422e-07 max=2.0497400760650635 mean=0.10684410482645035)
- Representative map: `runs/phase10_margin_aware_boundary_band_w15_seed42_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-1.0938293933868408 max=0.4348014295101166 mean=-0.018911773338913918, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=2.096503734588623 mean=0.07221103459596634, error:unknown [2, 12, 1, 128, 128] float32 min=8.940696716308594e-08 max=1.9797782897949219 mean=0.13477449119091034)

### Phase25

- Prediction/target map arrays: `supported`
- Evaluation-test prediction/target arrays available: `True`
- Prediction/target arrays shape-compatible: `True`
- Candidate files found: 1000 (showing 200)
- Note: Evaluation-test forecast_maps.npz files have recognizable prediction and target arrays; these are preferred over visualization epoch artifacts.

- Representative map: `runs/phase25_target_wet_recall_seed123_40e/evaluation_test/test_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.09588763117790222 max=2.3517329692840576 mean=0.05709153413772583, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=1.9651845693588257 mean=0.06030810996890068, error:unknown [2, 12, 1, 128, 128] float32 min=5.960464477539063e-08 max=0.7491657137870789 mean=0.022410474717617035)
- Representative map: `runs/phase25_target_wet_recall_seed202_40e/evaluation_test/test_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.12211493402719498 max=2.209061622619629 mean=0.054231468588113785, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=1.9651845693588257 mean=0.06030810996890068, error:unknown [2, 12, 1, 128, 128] float32 min=4.470348358154297e-08 max=0.6468542814254761 mean=0.020563121885061264)
- Representative map: `runs/phase25_target_wet_recall_seed42_40e/evaluation_test/test_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.08594702184200287 max=2.217378854751587 mean=0.05865371599793434, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=1.9651845693588257 mean=0.06030810996890068, error:unknown [2, 12, 1, 128, 128] float32 min=1.210719347000122e-07 max=0.6953846216201782 mean=0.0195021815598011)
- Representative map: `runs/phase25_target_wet_recall_seed123_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.58821040391922 max=0.5440542697906494 mean=-0.00812972616404295, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=2.0691962242126465 mean=0.06826271116733551, error:unknown [2, 12, 1, 128, 128] float32 min=1.3969838619232178e-07 max=2.0125491619110107 mean=0.10597563534975052)
- Representative map: `runs/phase25_target_wet_recall_seed202_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-0.9210600256919861 max=0.5075278878211975 mean=-0.02290366403758526, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=2.0103728771209717 mean=0.0626683160662651, error:unknown [2, 12, 1, 128, 128] float32 min=4.470348358154297e-08 max=1.9595768451690674 mean=0.11723089218139648)
- Representative map: `runs/phase25_target_wet_recall_seed42_40e/visualizations/epoch_001/val_batch_0000/forecast_maps.npz` (prediction:prediction [2, 12, 1, 128, 128] float32 min=-1.0699735879898071 max=0.4663587808609009 mean=-0.007641518488526344, target:target [2, 12, 1, 128, 128] float32 min=0.0 max=2.096503734588623 mean=0.07221103459596634, error:unknown [2, 12, 1, 128, 128] float32 min=2.5890767574310303e-07 max=1.9665614366531372 mean=0.13414734601974487)

### Phase 10 Baseline Policy

- Use boundary_weight=2.0 / w20 when available. Phase 10 runs without an explicit w suffix are treated as the recommended boundary_weight=2.0 baseline when their run token is phase10_margin_aware_boundary_band_seed*. w15 / boundary_weight=1.5 runs are rollback or non-default candidates.

### Phase 25 Target-Wet Recall Seed Search

- `seed123`: found `True`; runs: `phase25_target_wet_recall_seed123_40e`
- `seed42`: found `True`; runs: `phase25_target_wet_recall_seed42_40e`
- `seed202`: found `True`; runs: `phase25_target_wet_recall_seed202_40e`

### Aligned Phase 10 vs Phase 25 Comparison Hints

- `seed123`: Phase 10 `phase10_margin_aware_boundary_band_seed123_40e` vs Phase 25 `phase25_target_wet_recall_seed123_40e`, common rows `38`, source `analysis/phase25_target_wet_recall_comparison/aligned_comparison/aligned_comparison_summary.json`
- `seed202`: Phase 10 `phase10_margin_aware_boundary_band_seed202_40e` vs Phase 25 `phase25_target_wet_recall_seed202_40e`, common rows `38`, source `analysis/phase25_target_wet_recall_comparison/aligned_comparison_seed202/aligned_comparison_summary.json`
- `seed42`: Phase 10 `phase10_margin_aware_boundary_band_seed42_40e` vs Phase 25 `phase25_target_wet_recall_seed42_40e`, common rows `38`, source `analysis/phase25_target_wet_recall_comparison/aligned_comparison_seed42/aligned_comparison_summary.json`
## Metadata Availability

- `dt_or_time_interval`: found (25 candidate files)
- `dx_dy_or_spatial_resolution`: missing (0 candidate files)
- `grid_size`: unclear (1 candidate files)
- `scenario_metadata`: found (25 candidate files)
- `rainfall_scenario_names`: unclear (25 candidate files)
- `train_test_split`: found (25 candidate files)
- `boundary_conditions`: missing (0 candidate files)
- `pump_gate_operations`: missing (0 candidate files)
- `source_sink_infiltration_drainage`: found (1 candidate files)
- `velocity_or_flux_fields`: unclear (1 candidate files)

## Strong Physics Feasibility Classification

### Level 4 Conservation Oriented Diagnostics

- Classification: `partially supported`
- Explanation: Paired Phase 10/25 prediction and target map artifacts are available, so conservation/volume-response diagnostics are feasible at a volume-proxy or aggregate depth level. Strict conservation residuals remain limited by missing or unclear dx/dy, boundary fluxes, and source/sink terms.

### Level 4 Conservation Aware Loss Design

- Classification: `unclear`
- Explanation: The scanned repository does not expose all raw flood/rain/static arrays needed for a concrete future loss design.

### Level 5 Full Swe Pinn Residual Constraints

- Classification: `not supported`
- Explanation: Full SWE/PINN residual constraints are not supported by the current scanned evidence; missing: velocity fields or flux/discharge fields, boundary inflow/outflow conditions, pump/gate operations, dx/dy or spatial resolution, shape-compatible DEM/static elevation.

## Missing Inputs for Full SWE/PINN Residuals

The audit is conservative. Full residual constraints require aligned velocity or flux fields, boundary inflow/outflow, pump/gate operations, source/sink or infiltration/drainage terms, explicit dt, dx/dy, and shape-compatible DEM/static elevation. Items not directly found above should be treated as missing or unclear, not inferred.
