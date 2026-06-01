# Phase 43 UrbanFlood24 Full Dataset Inspection Findings

## 1. Executive Summary

Phase 43 is a no-training, read-only inspection of the downloaded UrbanFlood24 full dataset against the Phase 42 hydrodynamic export/data contract.

The inspected dataset path exists, and the inventory found train/test splits, flood scenarios, rainfall arrays, and static geodata arrays for three locations. The full UrbanFlood24 dataset is useful and appears to provide higher-resolution flood, rainfall, and static-map data than the Lite dataset. It supports higher-resolution Level 4+ proxy diagnostics.

The inspection does not provide direct evidence that the dataset supports Level 5 SWE/PINN residual constraints. Key SWE-critical fields and metadata remain absent or uncertain, including velocity or flux fields, physical grid spacing, timestep metadata, boundary conditions, complete source/sink closure, pump/gate operations, masks, coordinate/grid metadata, units/scaling, scenario metadata, and complete time-axis metadata.

Conservative Phase 43 decision:

- `selected_decision = full_dataset_readiness_uncertain_needs_metadata`
- `level5_supported = false`
- `level4_plus_supported = true`
- `training_authorized = false`
- `swe_residual_implementation_authorized = false`

## 2. Inputs and Outputs

Input dataset path:

- `E:\BaiduNetdiskDownload\urbanflood24\urbanflood24`

Inspection script:

- `scripts/inspect_phase43_urbanflood24_full_dataset.py`

Phase 43 plan:

- `docs/phase43_urbanflood24_full_dataset_inspection_plan.md`

Generated inspection outputs:

- `analysis/phase43_urbanflood24_full_dataset_inspection/full_dataset_file_inventory.csv`
- `analysis/phase43_urbanflood24_full_dataset_inspection/field_keyword_search_results.csv`
- `analysis/phase43_urbanflood24_full_dataset_inspection/sample_array_shape_inventory.csv`
- `analysis/phase43_urbanflood24_full_dataset_inspection/phase42_contract_compliance_matrix.csv`
- `analysis/phase43_urbanflood24_full_dataset_inspection/level5_readiness_assessment.csv`
- `analysis/phase43_urbanflood24_full_dataset_inspection/phase43_urbanflood24_full_dataset_summary.json`
- `analysis/phase43_urbanflood24_full_dataset_inspection/phase43_urbanflood24_full_dataset_summary.md`

The inspection recorded:

- `dataset_path_exists = true`
- `total_files = 354`
- `total_dirs = 186`
- `sampled_arrays_count = 54`

## 3. Dataset Structure and Evidence

The UrbanFlood24 full dataset contains the following observed top-level split structure:

- `train`
- `test`

Both splits contain:

- `flood`
- `geodata`

Observed locations:

- `location1`
- `location2`
- `location3`

Observed flood scenario structure includes scenario directories containing:

- `flood.npy`
- `rainfall.npy`

Observed geodata files include:

- `absolute_DEM.npy`
- `impervious.npy`
- `manhole.npy`

Scenario counts by split and location:

- `train/location1`: 40
- `train/location2`: 40
- `train/location3`: 40
- `test/location1`: 16
- `test/location2`: 16
- `test/location3`: 16

This structure supports dataset inspection and higher-resolution proxy diagnostics. It does not, by itself, establish hydrodynamic closure or Level 5 readiness.

## 4. Array Shape Evidence

Sampled arrays were inspected with memory-mapped metadata reads. No full-array training workflow was run.

Observed dynamic flood arrays:

- `flood.npy`: `(360, 1, 500, 500)`, `float64`

Observed rainfall arrays include:

- `rainfall.npy`: `(180,)`, `float64`
- `rainfall.npy`: `(360,)`, `float64`

Observed static geodata arrays:

- `absolute_DEM.npy`: `(500, 500)`, `float64`
- `impervious.npy`: `(500, 500)`, `float64`
- `manhole.npy`: `(500, 500)`, `float64`

The shape evidence indicates spatial compatibility between sampled flood rasters and static geodata rasters at 500 by 500 resolution. Rainfall and flood arrays expose sequence axes. However, array shape and dtype do not provide physical grid spacing, physical timestep, units, coordinate reference, boundary conditions, or complete time-axis alignment metadata.

## 5. Phase 42 Contract Compliance

The Phase 42 contract compliance matrix uses conservative field statuses.

Fields with direct array evidence:

- `water_depth_h`: present, using `flood.npy` conservatively as water-depth or flood-state evidence.
- `rainfall_source`: present, using `rainfall.npy` as rainfall forcing evidence.
- `DEM_or_bed_elevation`: present, using `absolute_DEM.npy` as terrain or bed-elevation proxy evidence.

Fields marked uncertain:

- `dt_time_step`
- `source_sink_terms`
- `scenario_metadata`
- `time_axis_metadata`

Fields marked absent:

- `velocity_u_v`
- `flux_qx_qy`
- `dx_dy_grid_spacing`
- `boundary_conditions`
- `pump_gate_operations`
- `valid_domain_mask`
- `boundary_mask`
- `coordinate_reference_or_grid_metadata`
- `units_and_scaling`

The contract evidence supports Level 4+ proxy diagnostics. It is not sufficient for Level 5 SWE residual work because several required fields are absent or only uncertain.

## 6. Level 5 Blocking Fields

The following Level 5 blocking fields remain missing or insufficiently documented:

- `velocity_u_v`
- `flux_qx_qy`
- `dx_dy_grid_spacing`
- `dt_time_step`
- `boundary_conditions`
- `source_sink_terms`
- `pump_gate_operations`
- `valid_domain_mask`
- `boundary_mask`
- `coordinate_reference_or_grid_metadata`
- `units_and_scaling`
- `scenario_metadata`
- `time_axis_metadata`

The missing or uncertain evidence includes velocity/flux, dx/dy, dt, boundary conditions, source/sink closure, pump/gate operations, valid/boundary masks, CRS/grid metadata, units/scaling, scenario metadata, and complete time-axis metadata.

## 7. What the Full Dataset Supports

The full UrbanFlood24 dataset supports:

- read-only dataset inventory and inspection;
- train/test split inspection;
- location-level inspection for `location1`, `location2`, and `location3`;
- higher-resolution flood-state, rainfall, and static-map analysis;
- higher-resolution Level 4+ proxy diagnostics;
- static map diagnostics using DEM, imperviousness, and manhole rasters;
- scenario-level proxy evaluation where `flood.npy` and `rainfall.npy` are available.

These uses should remain framed as proxy diagnostics unless additional hydrodynamic metadata and fields are recovered.

## 8. What the Full Dataset Does Not Support

Based on the current inspection evidence, the full UrbanFlood24 dataset does not support:

- a Level 5 support claim;
- a SWE/PINN claim;
- SWE residual implementation;
- strict conservation claims;
- full mass conservation claims;
- hydrodynamic closure claims;
- training authorization for Phase 43;
- seed runs or sweep runs for Phase 43.

The dataset does not currently provide direct evidence for aligned velocity or flux fields, physical grid spacing, physical timestep metadata, boundary-condition values, complete source/sink terms, pump/gate operations, valid-domain masks, boundary masks, CRS/grid metadata, units/scaling metadata, complete scenario metadata, or complete time-axis metadata.

## 9. Recommended Next Step

The next work should be metadata recovery or export clarification, not SWE loss implementation or training.

Recommended next actions:

- search for UrbanFlood24 full dataset documentation and metadata;
- query the dataset authors for grid spacing, timestep, units, coordinate reference, scenario definitions, and time-axis alignment;
- request author-side exports for velocity or flux, boundary conditions, source/sink terms, masks, and pump/gate operations if available;
- request or create an ICM/MIKE+ export that satisfies the Phase 42 data contract before any future Level 5 review.

No SWE residual, PINN component, loss modification, model architecture modification, training run, seed run, or sweep should be started from the current Phase 43 evidence.

## 10. Guardrails

Phase 43 guardrails remain in force:

- no training was run;
- no seed runs were performed;
- no sweeps were performed;
- no loss/config/model architecture was modified;
- no SWE residual was implemented;
- no PINN was implemented;
- no strict conservation claim is made;
- no full mass conservation claim is made;
- no hydrodynamic closure claim is made;
- no Level 5 support claim is made.

The inspection script is read-only with respect to the UrbanFlood24 dataset. It writes only inspection outputs under the Phase 43 analysis directory.

## 11. Level Boundary

Phase 43 supports a conservative Level 4+ boundary.

The full dataset can support higher-resolution proxy diagnostics because it provides flood-state arrays, rainfall arrays, and static geodata rasters at 500 by 500 spatial resolution. This is useful evidence for analysis beyond the Lite dataset.

The current evidence does not cross the Level 5 boundary. Level 5 would require explicit, aligned hydrodynamic fields and metadata needed to evaluate SWE residual constraints, including velocity or flux, grid spacing, timestep, boundary conditions, source/sink closure, masks, units, coordinate/grid metadata, scenario metadata, and time-axis metadata.

Therefore:

- `level4_plus_supported = true`
- `level5_supported = false`

## 12. Final Conclusion

UrbanFlood24 full is useful and higher-resolution than UrbanFlood24 Lite. It supports higher-resolution Level 4+ proxy diagnostics using flood, rainfall, DEM, imperviousness, and manhole arrays.

Phase 43 does not authorize training or implementation work. It does not claim SWE/PINN readiness, strict conservation, full mass conservation, hydrodynamic closure, or Level 5 support.

The selected conservative decision is:

`full_dataset_readiness_uncertain_needs_metadata`

Before any future Level 5 review or SWE-oriented implementation, the project needs metadata recovery, documentation search, author-side data clarification, or an ICM/MIKE+ export request that directly provides the missing SWE-critical fields and alignment metadata.
