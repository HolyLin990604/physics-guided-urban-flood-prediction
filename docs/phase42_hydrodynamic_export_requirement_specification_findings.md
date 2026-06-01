# Phase 42 Hydrodynamic Export Requirement Specification Findings

## 1. Executive Summary

Phase 42 is a no-training hydrodynamic export requirement specification phase. It converts the Phase 41 SWE data-readiness uncertainty into a conservative data contract for future hydrodynamic export inspection or external export requests.

Phase 42 produced the required specification outputs under `analysis/phase42_hydrodynamic_export_requirements/`. The generated summary records `required_fields_count = 16`, `minimum_contract_items = 10`, `urbanflood24_checklist_items = 10`, and `icm_mike_checklist_items = 13`.

The selected Phase 42 decision is `export_contract_ready_for_dataset_inspection`. Training remains unauthorized: `training_authorized = false`.

Phase 42 does not claim Level 5 support. It does not claim SWE/PINN support. It does not claim strict conservation, full mass conservation, or hydrodynamic closure.

## 2. Inputs and Outputs

Phase 42 was based on the Phase 42 plan and the generated requirement specification script:

- `docs/phase42_hydrodynamic_export_requirement_specification_plan.md`
- `scripts/specify_phase42_hydrodynamic_export_requirements.py`

The Phase 42 outputs are:

- `analysis/phase42_hydrodynamic_export_requirements/required_hydrodynamic_fields.csv`
- `analysis/phase42_hydrodynamic_export_requirements/field_unit_shape_time_requirements.csv`
- `analysis/phase42_hydrodynamic_export_requirements/swe_residual_minimum_data_contract.csv`
- `analysis/phase42_hydrodynamic_export_requirements/export_priority_table.csv`
- `analysis/phase42_hydrodynamic_export_requirements/urbanflood24_full_inspection_checklist.csv`
- `analysis/phase42_hydrodynamic_export_requirements/icm_mike_export_checklist.csv`
- `analysis/phase42_hydrodynamic_export_requirements/phase42_export_requirement_summary.json`
- `analysis/phase42_hydrodynamic_export_requirements/phase42_export_requirement_summary.md`

These outputs are specification artifacts only. They do not prove that the required fields are already available in the repository or in any external dataset.

## 3. Export Contract Decision

Phase 42 selected:

`selected_decision = export_contract_ready_for_dataset_inspection`

This means the export contract is organized enough to support later no-training dataset inspection or external export requests. It does not mean that Level 5 residual work is ready.

The generated summary also records:

- `training_authorized = false`
- `level5_supported = false`
- `swe_residual_implementation_authorized = false`
- `external_export_needed = true`

## 4. Required Hydrodynamic Field Categories

Phase 42 defines 16 required hydrodynamic field categories:

- `water_depth_h`
- `velocity_u_v`
- `flux_qx_qy`
- `dx_dy_grid_spacing`
- `dt_time_step`
- `DEM_or_bed_elevation`
- `rainfall_source`
- `boundary_conditions`
- `source_sink_terms`
- `pump_gate_operations`
- `valid_domain_mask`
- `boundary_mask`
- `coordinate_reference_or_grid_metadata`
- `units_and_scaling`
- `scenario_metadata`
- `time_axis_metadata`

These categories cover the minimum physical state, forcing, geometry, alignment, metadata, and operational-control information that would need to be inspected before any future SWE residual prototype could be considered.

Phase 42 treats missing velocity or flux, physical `dx/dy`, physical `dt`, boundary conditions, complete source/sink terms, and aligned metadata as blocking uncertainties for Level 5-oriented claims.

## 5. Minimum SWE Residual Data Contract

Phase 42 defines 10 minimum contract items:

- `MC01`: aligned water depth, `h(t,y,x)`, or documented equivalent.
- `MC02`: velocity components `u/v` or flux components `qx/qy` aligned to depth.
- `MC03`: physical `dx/dy`, cell areas, or mesh geometry.
- `MC04`: physical timestep duration, `dt`, aligned to all dynamic fields.
- `MC05`: DEM, terrain, or bed elevation aligned to the hydrodynamic state grid.
- `MC06`: rainfall source aligned to the depth time axis.
- `MC07`: boundary masks, boundary locations, boundary types, and boundary values.
- `MC08`: complete source/sink documentation, including represented non-rain terms.
- `MC09`: valid-domain mask.
- `MC10`: scenario metadata, units, scaling, sign conventions, and nodata conventions.

This minimum contract must be satisfied before any SWE residual prototype is considered. Satisfying the contract would still only support a later feasibility review; it would not by itself authorize training, implementation, or Level 5 claims.

## 6. UrbanFlood24 Full Dataset Inspection Requirements

Phase 42 defines 10 no-training inspection checklist items for the UrbanFlood24 full dataset, if that dataset is available.

The checklist requires a file tree scan, searches for velocity or flux fields, explicit `dx/dy/dt` metadata, boundary definitions, pump/gate/source/sink metadata, shape and axis-order evidence, full-resolution evidence, time interval metadata, and a present/absent/uncertain status for each Level 5-relevant variable.

The UrbanFlood24 checklist is an inspection requirement only. Phase 42 did not inspect heavy dataset contents, did not run training, and did not infer Level 5 readiness from the existence of the checklist.

## 7. InfoWorks ICM / MIKE+ Export Requirements

Phase 42 defines 13 export request items for InfoWorks ICM, MIKE+, UrbanFlood24 full data, or an equivalent hydrodynamic source.

The requested exports include 2D depth, velocity or flux, timestep metadata, grid spacing or mesh geometry, DEM or bed elevation, boundary time series, rainfall forcing, sewer/drainage/outfall/source-sink exchange terms, pump/gate operations, CRS and vertical datum metadata, scenario metadata, units and scaling, and alignment rules to the repository flood/rain/static arrays.

For network, link, mesh, or mixed 1D/2D outputs, the contract requires explicit mapping to the repository grid or target arrays. Matching file names or array dimensions alone are not treated as sufficient evidence of physical alignment.

## 8. What This Enables

Phase 42 enables a future no-training inspection or export request to be performed against a clear contract.

It provides:

- a field list for hydrodynamic exports;
- unit, shape, grid, and time-axis requirements;
- a minimum SWE residual data contract;
- an UrbanFlood24 full dataset inspection checklist;
- an InfoWorks ICM / MIKE+ export checklist;
- conservative guardrails for interpreting any future recovered fields.

This is useful for future Level 5-oriented work because it defines what evidence would be needed before residual feasibility can be reviewed.

## 9. What Is Still Not Allowed

Phase 42 does not allow:

- training;
- seed runs;
- sweeps;
- loss modification;
- config modification;
- model architecture modification;
- SWE residual implementation;
- PINN implementation;
- claims of SWE/PINN support;
- claims of strict conservation;
- claims of full mass conservation;
- claims of hydrodynamic closure;
- claims of Level 5 support.

No training was run. No seed runs were performed. No loss, config, or model architecture was modified. No SWE residual or PINN component was implemented.

## 10. Recommended Next Step

The next recommended action is:

Inspect the UrbanFlood24 full dataset if available and/or request/export fields from InfoWorks ICM, MIKE+, or an equivalent hydrodynamic source.

The inspection or export request should record present, absent, or uncertain status for every minimum contract item, with file paths, metadata excerpts, units, shapes, time-axis evidence, and grid-alignment evidence where available.

## 11. Level Boundary

Phase 42 creates a data contract for future Level 5-oriented work, but it does not claim Level 5 support.

The boundary is:

- Level 4+ proxy diagnostics may remain possible where supported by existing evidence.
- Level 5 SWE/PINN residual claims remain unsupported.
- Future Level 5-oriented consideration requires explicit hydrodynamic exports or metadata recovery satisfying the minimum contract.

The existence of a requirement is not evidence that the corresponding data exist. Missing physical terms must not be silently assumed zero unless source-model documentation supports that closure assumption.

## 12. Final Conclusion

Phase 42 completed a conservative, no-training hydrodynamic export requirement specification. It produced a reviewable export contract and selected `export_contract_ready_for_dataset_inspection`.

Training remains unauthorized: `training_authorized = false`.

Phase 42 prepares the repository for future dataset inspection or external hydrodynamic export requests. It does not implement SWE residuals, does not implement PINN components, and does not claim Level 5 support, strict conservation, full mass conservation, or hydrodynamic closure.
