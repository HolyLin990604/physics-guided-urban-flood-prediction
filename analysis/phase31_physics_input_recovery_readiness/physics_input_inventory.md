# Phase 31 Physics Input Inventory

This diagnostic inventory is read-only except for the files in this Phase 31 output directory. It does not train models, modify architecture, modify losses, modify training configs, or claim strict mass conservation / full SWE/PINN support.

## 1. Executive Summary

- Preliminary readiness classification: `Level 4+ possible`
- Level 5 status: `Level 5 unsupported`
- Representative flood spatial shape: `[128, 128]`
- Raw flood/rain/static availability: flood=True, rainfall=True, static=True
- DEM/static elevation compatibility: `true`
- dt status: `inferred_ratio_only`
- dx/dy status: `candidate_mentions_only`

## 2. Repository and Dataset Paths Inspected

- Repository roots: `configs`, `datasets`, `utils`, `scripts`, `analysis/phase26_strong_physics_constraint_feasibility`
- Repository files inspected: 66
- Config path records found: 50
- Dataset roots inspected: 1

- `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite`

Config-referenced paths:
- `configs/ablation_non_negativity.json` `dataset.dataset_config_path` -> `C:\Users\39053\Documents\New project\configs\urbanflood24_lite_adapter.json` (exists=True)
- `configs/ablation_non_negativity.json` `output.root` -> `C:\Users\39053\Documents\New project\runs\ablation_non_negativity` (exists=False)
- `configs/ablation_rainfall_only_debug.json` `dataset.dataset_config_path` -> `C:\Users\39053\Documents\New project\configs\urbanflood24_lite_adapter.json` (exists=True)
- `configs/ablation_rainfall_only_debug.json` `output.root` -> `C:\Users\39053\Documents\New project\runs\ablation_rainfall_only_debug` (exists=True)
- `configs/ablation_rainfall_topography_continuity.json` `dataset.dataset_config_path` -> `C:\Users\39053\Documents\New project\configs\urbanflood24_lite_adapter.json` (exists=True)
- `configs/ablation_rainfall_topography_continuity.json` `output.root` -> `C:\Users\39053\Documents\New project\runs\ablation_rain_topo_cont` (exists=False)
- `configs/ablation_topography_only_debug.json` `dataset.dataset_config_path` -> `C:\Users\39053\Documents\New project\configs\urbanflood24_lite_adapter.json` (exists=True)
- `configs/ablation_topography_only_debug.json` `output.root` -> `C:\Users\39053\Documents\New project\runs\ablation_topography_only_debug` (exists=True)
- `configs/ablation_wet_dry.json` `dataset.dataset_config_path` -> `C:\Users\39053\Documents\New project\configs\urbanflood24_lite_adapter.json` (exists=True)
- `configs/ablation_wet_dry.json` `output.root` -> `C:\Users\39053\Documents\New project\runs\ablation_wet_dry` (exists=False)
- `configs/train_baseline.json` `dataset.dataset_config_path` -> `C:\Users\39053\Documents\New project\configs\urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_baseline.json` `output.root` -> `C:\Users\39053\Documents\New project\runs\baseline_unet_tcn` (exists=True)
- `configs/train_baseline_20epoch.json` `dataset.dataset_config_path` -> `C:\Users\39053\Documents\New project\configs\urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_baseline_20epoch.json` `output.root` -> `C:\Users\39053\Documents\New project\runs\baseline_20epoch` (exists=True)
- `configs/train_baseline_5epoch.json` `dataset.dataset_config_path` -> `C:\Users\39053\Documents\New project\configs\urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_baseline_5epoch.json` `output.root` -> `C:\Users\39053\Documents\New project\runs\baseline_5epoch` (exists=True)
- `configs/train_baseline_debug.json` `dataset.dataset_config_path` -> `C:\Users\39053\Documents\New project\configs\urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_baseline_debug.json` `output.root` -> `C:\Users\39053\Documents\New project\runs\baseline_unet_tcn` (exists=True)
- `configs/train_phase10_margin_aware_boundary_band_seed123_40e.json` `dataset.dataset_config_path` -> `configs/urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_phase10_margin_aware_boundary_band_seed123_40e.json` `output.root` -> `runs/phase10_margin_aware_boundary_band_seed123_40e` (exists=True)
- `configs/train_phase10_margin_aware_boundary_band_seed202_40e.json` `dataset.dataset_config_path` -> `configs/urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_phase10_margin_aware_boundary_band_seed202_40e.json` `output.root` -> `runs/phase10_margin_aware_boundary_band_seed202_40e` (exists=True)
- `configs/train_phase10_margin_aware_boundary_band_seed42_40e.json` `dataset.dataset_config_path` -> `configs/urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_phase10_margin_aware_boundary_band_seed42_40e.json` `output.root` -> `runs/phase10_margin_aware_boundary_band_seed42_40e` (exists=True)
- `configs/train_phase25_target_wet_recall_seed123_40e.json` `dataset.dataset_config_path` -> `configs/urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_phase25_target_wet_recall_seed123_40e.json` `output.root` -> `runs/phase25_target_wet_recall_seed123_40e` (exists=True)
- `configs/train_phase25_target_wet_recall_seed202_40e.json` `dataset.dataset_config_path` -> `configs/urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_phase25_target_wet_recall_seed202_40e.json` `output.root` -> `runs/phase25_target_wet_recall_seed202_40e` (exists=True)
- `configs/train_phase25_target_wet_recall_seed42_40e.json` `dataset.dataset_config_path` -> `configs/urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_phase25_target_wet_recall_seed42_40e.json` `output.root` -> `runs/phase25_target_wet_recall_seed42_40e` (exists=True)
- `configs/train_phase27_volume_response_seed42_40e.json` `dataset.dataset_config_path` -> `configs/urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_phase27_volume_response_seed42_40e.json` `output.root` -> `runs/phase27_volume_response_seed42_40e` (exists=True)
- `configs/train_phase29_tolerance_band_volume_seed42_40e.json` `dataset.dataset_config_path` -> `configs/urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_phase29_tolerance_band_volume_seed42_40e.json` `output.root` -> `runs/phase29_tolerance_band_volume_seed42_40e` (exists=True)
- `configs/train_stage2b_phase1.json` `dataset.dataset_config_path` -> `C:\Users\39053\Documents\New project\configs\urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_stage2b_phase1.json` `output.root` -> `C:\Users\39053\Documents\New project\runs\stage2b_phase1` (exists=True)
- `configs/train_stage2b_phase1_20epoch.json` `dataset.dataset_config_path` -> `C:\Users\39053\Documents\New project\configs\urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_stage2b_phase1_20epoch.json` `output.root` -> `C:\Users\39053\Documents\New project\runs\stage2b_phase1_20epoch` (exists=True)
- `configs/train_stage2b_phase1_5epoch.json` `dataset.dataset_config_path` -> `C:\Users\39053\Documents\New project\configs\urbanflood24_lite_adapter.json` (exists=True)
- `configs/train_stage2b_phase1_5epoch.json` `output.root` -> `C:\Users\39053\Documents\New project\runs\stage2b_phase1_5epoch` (exists=True)

## 3. Raw Flood/Rain/Static Array Availability

- `flood.npy` files: 36
- `rainfall.npy` files: 36
- Static array files: 18
- Other `.npy` / `.npz` / metadata files inventoried: 33
- Metadata files inventoried: 33
- Counts by extension: `{'.csv': 4, '.md': 2, '.json': 27, '.npy': 90}`

## 4. Representative Shapes

- Representative flood spatial shape: `[128, 128]`
- Source: `forecast_maps.npz`
- Forecast prediction/target compatible: `true`
- Representative `forecast_maps.npz` files inspected: 250

| Forecast map | Keys | Prediction/target compatible | Representative spatial shape |
| --- | --- | --- | --- |
| `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0000/forecast_maps.npz` | `prediction, target, error` | `True` | `[128, 128]` |
| `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0001/forecast_maps.npz` | `prediction, target, error` | `True` | `[128, 128]` |
| `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0002/forecast_maps.npz` | `prediction, target, error` | `True` | `[128, 128]` |
| `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0003/forecast_maps.npz` | `prediction, target, error` | `True` | `[128, 128]` |
| `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0004/forecast_maps.npz` | `prediction, target, error` | `True` | `[128, 128]` |
| `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0005/forecast_maps.npz` | `prediction, target, error` | `True` | `[128, 128]` |
| `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0006/forecast_maps.npz` | `prediction, target, error` | `True` | `[128, 128]` |
| `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0007/forecast_maps.npz` | `prediction, target, error` | `True` | `[128, 128]` |
| `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0008/forecast_maps.npz` | `prediction, target, error` | `True` | `[128, 128]` |
| `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0009/forecast_maps.npz` | `prediction, target, error` | `True` | `[128, 128]` |
| `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0010/forecast_maps.npz` | `prediction, target, error` | `True` | `[128, 128]` |
| `runs/phase10_margin_aware_boundary_band_seed123_40e/evaluation_test/test_batch_0011/forecast_maps.npz` | `prediction, target, error` | `True` | `[128, 128]` |

## 5. Static-Map / DEM Compatibility

- Shape-compatible DEM/static elevation found: `true`
- Compatible DEM/static elevation files: `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\test\geodata\location1\absolute_DEM.npy`, `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\test\geodata\location2\absolute_DEM.npy`, `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\test\geodata\location3\absolute_DEM.npy`, `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\train\geodata\location1\absolute_DEM.npy`, `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\train\geodata\location2\absolute_DEM.npy`, `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\train\geodata\location3\absolute_DEM.npy`

| Path | Role | Shape | Dtype | Min | Max | Mean | Compatible With Flood |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\test\geodata\location1\absolute_DEM.npy` | dem_static_elevation | `[128, 128]` | `float32` | -0.016762489452958107 | 100.0 | 27.556705474853516 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\test\geodata\location1\impervious.npy` | impervious | `[128, 128]` | `float32` | 0.0 | 0.949999988079071 | 0.7079832553863525 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\test\geodata\location1\manhole.npy` | manhole_drainage | `[128, 128]` | `float32` | 0.0 | 0.04822835698723793 | 0.0003533980343490839 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\test\geodata\location2\absolute_DEM.npy` | dem_static_elevation | `[128, 128]` | `float32` | 3.168243646621704 | 100.0 | 20.033260345458984 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\test\geodata\location2\impervious.npy` | impervious | `[128, 128]` | `float32` | 0.0 | 0.949999988079071 | 0.7117959856987 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\test\geodata\location2\manhole.npy` | manhole_drainage | `[128, 128]` | `float32` | 0.0 | 0.030066024512052536 | 0.0004117012140341103 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\test\geodata\location3\absolute_DEM.npy` | dem_static_elevation | `[128, 128]` | `float32` | 10.688794136047363 | 100.0 | 39.55226135253906 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\test\geodata\location3\impervious.npy` | impervious | `[128, 128]` | `float32` | 0.0 | 0.949999988079071 | 0.7468476891517639 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\test\geodata\location3\manhole.npy` | manhole_drainage | `[128, 128]` | `float32` | 0.0 | 0.04908738657832146 | 0.0010424478678032756 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\train\geodata\location1\absolute_DEM.npy` | dem_static_elevation | `[128, 128]` | `float32` | -0.016762489452958107 | 100.0 | 27.556705474853516 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\train\geodata\location1\impervious.npy` | impervious | `[128, 128]` | `float32` | 0.0 | 0.949999988079071 | 0.7079832553863525 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\train\geodata\location1\manhole.npy` | manhole_drainage | `[128, 128]` | `float32` | 0.0 | 0.04822835698723793 | 0.0003533980343490839 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\train\geodata\location2\absolute_DEM.npy` | dem_static_elevation | `[128, 128]` | `float32` | 3.168243646621704 | 100.0 | 20.033260345458984 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\train\geodata\location2\impervious.npy` | impervious | `[128, 128]` | `float32` | 0.0 | 0.949999988079071 | 0.7117959856987 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\train\geodata\location2\manhole.npy` | manhole_drainage | `[128, 128]` | `float32` | 0.0 | 0.030066024512052536 | 0.0004117012140341103 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\train\geodata\location3\absolute_DEM.npy` | dem_static_elevation | `[128, 128]` | `float32` | 10.688794136047363 | 100.0 | 39.55226135253906 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\train\geodata\location3\impervious.npy` | impervious | `[128, 128]` | `float32` | 0.0 | 0.949999988079071 | 0.7468476891517639 | `True` |
| `E:\BaiduNetdiskDownload\urbanflood24_lite_release\urbanflood24_lite\train\geodata\location3\manhole.npy` | manhole_drainage | `[128, 128]` | `float32` | 0.0 | 0.04908738657832146 | 0.0010424478678032756 | `True` |

## 6. Time-Alignment Evidence

- dt status: `inferred_ratio_only`
- Flood shapes: `[{'shape': [36, 128, 128], 'count': 31}, {'shape': [48, 128, 128], 'count': 5}]`
- Rainfall shapes: `[{'shape': [18], 'count': 36}]`
- Paired flood/rainfall ratio examples: 36
- Observed timestep ratios: `[{'flood_steps': 36, 'rainfall_steps': 18, 'ratio': 2.0, 'count': 31}, {'flood_steps': 48, 'rainfall_steps': 18, 'ratio': 2.6666666666666665, 'count': 5}]`
- Metadata candidate files: 28

## 7. dx/dy / Spatial Resolution Evidence

- dx/dy status: `candidate_mentions_only`
- Candidate files: 3

## 8. Boundary / Operation / Source-Sink Evidence

- `velocity_flux_discharge`: `candidate_mentions_found` (3 candidate files)
- `boundary_inflow_outflow`: `candidate_mentions_found` (13 candidate files)
- `pump_gate_operations`: `candidate_mentions_found` (15 candidate files)
- `drainage_sewer_manhole`: `candidate_mentions_found` (3 candidate files)
- `infiltration_source_sink`: `candidate_mentions_found` (3 candidate files)
- `valid_domain_boundary_mask`: `missing` (0 candidate files)

## 9. Preliminary Readiness Classification

- Classification: `Level 4+ possible`
- Reason: Raw flood/rain/static arrays and shape-compatible DEM/static elevation are available, with mask or domain/boundary construction feasibility from aligned grid shapes. This supports structured proxy diagnostics, not strict conservation.
- Level 5: `Level 5 unsupported`

## 10. Missing Inputs

- aligned velocity/flux/discharge fields
- aligned boundary inflow/outflow fields or masks
- source/sink, infiltration, or drainage terms as aligned physical fields
- explicit dx/dy or spatial resolution
- explicit dt

## 11. Recommended Next Script

`scripts/inspect_phase31_static_maps.py` should inspect the recovered static maps in more detail, verify channel semantics/location coverage, and prepare evidence for any future domain or boundary mask construction. It should remain diagnostic-only.
