# Phase 43 UrbanFlood24 Full Dataset Inspection Plan

## 1. Executive Summary

Phase 43 is a no-training UrbanFlood24 full dataset inspection phase. Its purpose is to inspect the downloaded full UrbanFlood24 dataset against the Phase 42 hydrodynamic export/data contract and determine, conservatively, whether the dataset contains the Level 5 SWE-critical fields needed for future residual-based work.

Phase 43 must not train models, run seed experiments, run sweeps, edit loss/config/model code, implement SWE residuals, implement PINN components, or claim Level 5 support. The phase is limited to file inventory, lightweight metadata inspection, shape/dtype checks, keyword scans, and contract compliance assessment.

Planned inspection script:

`scripts/inspect_phase43_urbanflood24_full_dataset.py`

Expected output directory:

`analysis/phase43_urbanflood24_full_dataset_inspection/`

The expected conservative decision, if no velocity, flux, boundary-condition, source/sink, pump/gate, and grid/time metadata fields are found, is:

`full_dataset_level4_plus_only`

## 2. Dataset Path and Initial Manual Inspection

UrbanFlood24 full dataset path:

`E:\BaiduNetdiskDownload\urbanflood24\urbanflood24`

Initial manual inspection found that the dataset root contains:

- `train`
- `test`

The `train` and `test` directories each contain:

- `flood`
- `geodata`

The `flood` directory contains:

- `location1`
- `location2`
- `location3`

The `geodata` directory contains:

- `location1`
- `location2`
- `location3`

Observed static files in `geodata/location1`:

- `absolute_DEM.npy`
- `impervious.npy`
- `manhole.npy`

Observed sample static array shapes:

- `absolute_DEM.npy`: `(500, 500)`, `float64`
- `impervious.npy`: `(500, 500)`, `float64`
- `manhole.npy`: `(500, 500)`, `float64`

Observed sample synthetic/design rainfall scenario:

`train/flood/location1/r100y_p0.1_d3h`

- `flood.npy`: `(360, 1, 500, 500)`, `float64`
- `rainfall.npy`: `(180,)`, `float64`

Observed sample measured/real rainfall scenario:

`train/flood/location1/G1135_intensity_117`

- `flood.npy`: `(360, 1, 500, 500)`, `float64`
- `rainfall.npy`: `(360,)`, `float64`

These observations are preliminary. Phase 43 must inspect the full downloaded dataset structure before drawing any readiness conclusion.

## 3. Background from Phase 42

Phase 42 created a hydrodynamic export requirement specification and selected:

`selected_decision = export_contract_ready_for_dataset_inspection`

Phase 42 also recorded:

- `training_authorized = false`
- `required_fields_count = 16`
- `minimum_contract_items = 10`
- `urbanflood24_checklist_items = 10`
- `icm_mike_checklist_items = 13`

Phase 42 did not claim Level 5 support. It defined the data contract that must be satisfied before any future Level 5 SWE-oriented residual prototype can be responsibly considered.

Phase 43 starts from that contract and inspects the actual downloaded UrbanFlood24 full dataset. The inspection must not reinterpret file presence, array shape, or rainfall/depth availability as sufficient evidence for SWE residual readiness unless the missing hydrodynamic fields and alignment metadata are actually present.

## 4. Inspection Objectives

Phase 43 will inspect the full UrbanFlood24 dataset to determine:

- whether the dataset contains the Phase 42 required field categories;
- whether dynamic and static arrays have consistent shapes across train/test and locations;
- whether rainfall and flood arrays have documented or inferable time-axis alignment;
- whether grid spacing, timestep, coordinates, units, and scenario metadata are present;
- whether SWE-critical fields such as velocity, flux, boundary conditions, source/sink terms, and pump/gate operations exist;
- whether the dataset supports only higher-resolution Level 4+ proxy diagnostics or has enough aligned physical fields for a future Level 5 readiness review.

The output should be an evidence table, not an implementation claim.

## 5. Required Field Checks

Phase 43 will record `present`, `absent`, or `uncertain` status for each Phase 42 required field category:

- `flood / water_depth_h`
- `rainfall_source`
- `DEM_or_bed_elevation`
- `impervious`
- `manhole`
- `velocity_u_v`
- `flux_qx_qy`
- `dx_dy_grid_spacing`
- `dt_time_step`
- `boundary_conditions`
- `source_sink_terms`
- `pump_gate_operations`
- `coordinate_reference_or_grid_metadata`
- `units_and_scaling`
- `scenario_metadata`
- `time_axis_metadata`

For each field, the inspection should record:

- candidate file or directory evidence;
- split and location coverage;
- sample shape and dtype where applicable;
- whether evidence is direct, inferred, or only a filename-level clue;
- whether the field is aligned with `flood.npy` in space and time;
- whether the field is sufficient for Phase 42 contract compliance.

The field status must remain conservative. For example, `flood.npy` may support water-depth inspection only if the dataset documentation or naming supports interpreting it as depth or equivalent inundation state. `rainfall.npy` may support rainfall-source inspection but does not by itself establish source/sink completeness.

## 6. Shape and Metadata Checks

The planned inspection should check shapes and dtypes without loading full arrays into memory. It should use `numpy.load(..., mmap_mode='r')` for `.npy` files and read only metadata needed for shape/dtype reporting.

Shape checks should include:

- static geodata arrays for `train/test` and `location1/location2/location3`;
- sampled scenario `flood.npy` arrays from each split and location;
- sampled scenario `rainfall.npy` arrays from each split and location;
- consistency of spatial dimensions between static arrays and flood arrays;
- consistency of channel dimensions for flood arrays;
- consistency or documented variability of rainfall length;
- relationship between rainfall time length and flood time length, recorded as observed evidence only.

Metadata checks should include:

- presence of files or directories indicating `dx`, `dy`, `dt`, coordinate reference, grid origin, cell size, projection, units, or scaling;
- scenario naming conventions such as return period, rainfall probability, duration, event identifier, or intensity;
- any README, CSV, JSON, TXT, XML, YAML, metadata, or sidecar files near the dataset root, split directories, locations, or scenarios;
- whether metadata are machine-readable, human-readable, or absent.

## 7. Level 5 Readiness Criteria

Phase 43 may only consider `full_dataset_level5_ready` if all required Level 5 SWE-critical fields are actually present and aligned. At minimum, this requires evidence for:

- water depth or equivalent hydrodynamic state;
- rainfall forcing;
- bed elevation or DEM;
- velocity components `u/v` or flux components `qx/qy`;
- physical grid spacing or mesh geometry;
- physical timestep metadata;
- boundary conditions;
- source/sink terms, including drainage/manhole interpretation where relevant;
- pump/gate operations if applicable or explicit confirmation that none exist;
- coordinate/grid metadata;
- units and scaling metadata;
- scenario metadata;
- time-axis metadata.

If only `flood.npy`, `rainfall.npy`, `absolute_DEM.npy`, `impervious.npy`, and `manhole.npy` are found, Phase 43 should conclude that the full dataset supports higher-resolution Level 4+ proxy diagnostics but does not directly support Level 5 SWE residual constraints.

Candidate decisions:

- `full_dataset_level5_ready`
- `full_dataset_level4_plus_only`
- `full_dataset_readiness_uncertain_needs_metadata`
- `inspection_incomplete_dataset_path_issue`

The expected conservative decision if no velocity/flux/boundary/source-sink metadata are found is:

`full_dataset_level4_plus_only`

## 8. Planned Inspection Script

The planned script is:

`scripts/inspect_phase43_urbanflood24_full_dataset.py`

Important implementation requirements:

- Do not load full arrays into memory.
- Use `numpy.load(..., mmap_mode='r')` for shape/dtype checks only.
- Sample a limited number of scenarios from `train/test/location1/location2/location3`.
- Build a full file inventory from paths, sizes, suffixes, split, location, and scenario names.
- Scan file names and directory names for Level 5 keywords.
- Record `present`, `absent`, or `uncertain` status for each Phase 42 required field.
- Keep the script read-only with respect to the UrbanFlood24 dataset path.
- Write only inspection outputs under the Phase 43 analysis directory.

Level 5 keyword scan terms:

- `u`
- `v`
- `velocity`
- `qx`
- `qy`
- `flux`
- `discharge`
- `flow`
- `boundary`
- `inflow`
- `outflow`
- `stage`
- `water_level`
- `source`
- `sink`
- `pump`
- `gate`
- `dt`
- `dx`
- `dy`
- `metadata`

Single-letter keywords such as `u` and `v` should be handled carefully to avoid overclaiming. They should be recorded as keyword hits only when matched as path tokens, field-like names, or metadata keys, not as arbitrary characters inside unrelated words.

## 9. Expected Outputs

Expected output directory:

`analysis/phase43_urbanflood24_full_dataset_inspection/`

Expected outputs:

- `full_dataset_file_inventory.csv`
- `field_keyword_search_results.csv`
- `sample_array_shape_inventory.csv`
- `phase42_contract_compliance_matrix.csv`
- `level5_readiness_assessment.csv`
- `phase43_urbanflood24_full_dataset_summary.json`
- `phase43_urbanflood24_full_dataset_summary.md`

The summary JSON should include:

- dataset path inspected;
- inspection timestamp;
- script path;
- sampled splits, locations, and scenario counts;
- observed static and dynamic field categories;
- required field status counts;
- Level 5 blocking missing fields;
- selected conservative decision;
- guardrail flags confirming no training and no implementation changes.

The summary Markdown should be suitable for later inclusion in a Phase 43 findings document.

## 10. Guardrails

Phase 43 guardrails:

- no training;
- no seed runs;
- no sweeps;
- no loss/config/model edits;
- no SWE residual implementation;
- no PINN implementation;
- no strict conservation claim;
- no full mass conservation claim;
- no hydrodynamic closure claim;
- no Level 5 support claim unless all required fields are actually present and aligned.

The planned script must be an inspection utility only. It must not write derived training datasets, alter repository model behavior, alter experiment configuration, or run any model inference/training workflow.

## 11. Success Criteria

Phase 43 is successful if it produces a clear, auditable, no-training inspection of the downloaded full UrbanFlood24 dataset that:

- inventories the dataset files across train/test and all available locations;
- samples array shapes and dtypes without loading full arrays into memory;
- checks the Phase 42 required field categories with conservative statuses;
- identifies whether Level 5 SWE-critical fields are present, absent, or uncertain;
- separates direct evidence from inferred or filename-only evidence;
- records any path, metadata, or documentation gaps that limit the conclusion;
- produces all expected CSV, JSON, and Markdown outputs;
- selects one conservative decision candidate.

If the dataset path is unavailable or incomplete, the correct outcome is not a Level 5 readiness statement. The correct outcome is:

`inspection_incomplete_dataset_path_issue`

## 12. Final Conclusion

Phase 43 should inspect the full UrbanFlood24 dataset as evidence against the Phase 42 data contract. It should not treat the existence of depth-like flood arrays, rainfall arrays, DEM, imperviousness, and manhole rasters as sufficient for Level 5 SWE residual readiness.

Unless aligned velocity or flux fields, grid spacing, timestep metadata, boundary conditions, source/sink terms, coordinate/grid metadata, units, scenario metadata, and time-axis metadata are actually found, the conservative conclusion should be that UrbanFlood24 supports higher-resolution Level 4+ proxy diagnostics but does not directly support Level 5 SWE residual constraints.
