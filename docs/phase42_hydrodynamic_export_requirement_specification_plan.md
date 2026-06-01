# Phase 42 Hydrodynamic Export Requirement Specification Plan

## 1. Executive Summary

Phase 42 is a no-training hydrodynamic export requirement specification phase. It follows Phase 41, which concluded that the current repository evidence is insufficient for Level 5 SWE residual constraints and that external hydrodynamic model export or metadata recovery is needed.

Phase 42 will specify the data contract that must be satisfied before any future Level 5 SWE-oriented residual prototype can be responsibly considered. It does not implement SWE residuals, does not implement PINN components, does not train models, and does not claim Level 5 support.

Planned specification script:

`scripts/specify_phase42_hydrodynamic_export_requirements.py`

Expected output directory:

`analysis/phase42_hydrodynamic_export_requirements/`

## 2. Background from Phase 40 and Phase 41

Phase 40 selected:

`selected_decision = pause_loss_redesign_move_to_swe_data_readiness`

Phase 40 also recorded:

`training_authorized = false`

`next_recommended_phase = phase41_swe_data_readiness_audit`

Phase 41 completed a no-training SWE data readiness audit and recorded:

`readiness_decision = readiness_uncertain_requires_external_data_export`

`level5_supported = false`

`external_hydrodynamic_model_export_needed = true`

`level4_proxy_supported = true`

Phase 41 found that current evidence supports Level 4+ proxy diagnostics, but does not support Level 5 SWE/PINN residual constraints. Missing, incomplete, or uncertain SWE-critical categories include:

- `velocity_or_flux_fields`
- `dx_dy_grid_spacing`
- `dt_time_step`
- `boundary_conditions`
- `pump_gate_operations`
- complete `source_sink_terms`
- complete `hydrodynamic_state_variables`

Phase 42 starts from that conservative finding. It must not reinterpret Phase 41 as Level 5 readiness.

## 3. Purpose of Hydrodynamic Export Requirement Specification

The purpose of Phase 42 is to define what must be exported or recovered from external hydrodynamic sources before future SWE residual prototype planning can proceed.

Candidate external sources include:

- InfoWorks ICM
- MIKE+
- UrbanFlood24 full dataset
- other source hydrodynamic models or source exports with equivalent physical fields and metadata

Phase 42 should convert the Phase 41 missing-input findings into explicit export requirements. The output should be a reviewable data contract covering required fields, units, shapes, grid alignment, time alignment, boundary conditions, source/sink terms, operational controls, and scenario metadata.

This phase is a specification phase only. It should not treat a planned export contract as evidence that the data already exist or that future SWE residuals are authorized.

## 4. Required Export Field Categories

Phase 42 should specify requirements for the following field categories:

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

For each category, the specification should record:

- whether the category is required for a minimum SWE residual data contract;
- whether an equivalent field is acceptable;
- expected units;
- expected dimensionality and shape;
- expected time-axis behavior;
- expected grid alignment;
- whether values must be physical values or may be metadata only;
- whether absence may be allowed only with an explicit source-model closure assumption;
- export priority;
- notes on likely InfoWorks ICM, MIKE+, or UrbanFlood24 full-dataset representations.

## 5. Minimum SWE Residual Data Contract

The minimum data contract for future SWE residual consideration should require explicit, aligned evidence for:

- water depth or stage, represented as `water_depth_h` or a documented equivalent;
- velocity components `velocity_u_v` or flux/discharge components `flux_qx_qy`;
- physical grid spacing through `dx_dy_grid_spacing`;
- physical timestep duration through `dt_time_step`;
- bed elevation or DEM through `DEM_or_bed_elevation`;
- rainfall or external forcing through `rainfall_source`;
- boundary condition types and values through `boundary_conditions`;
- complete source/sink terms, including drainage, infiltration, outfalls, lateral exchange, or other modeled exchange terms when present;
- pump, gate, valve, or control operations when represented by the source model;
- valid-domain and boundary masks aligned to the same grid;
- coordinate reference system, grid origin, resolution, and orientation metadata;
- units, scaling, nodata conventions, and sign conventions;
- scenario and event metadata;
- time-axis metadata that aligns all dynamic fields.

If any minimum category is unavailable, Phase 42 should require that the missing category be recorded explicitly. Missing physical terms should not be silently assumed zero unless the source hydrodynamic model or dataset documentation supports that closure assumption.

## 6. Field Unit Requirements

The specification should require units for every exported field and metadata item.

Expected unit requirements include:

- `water_depth_h`: meters or a documented convertible depth unit.
- `velocity_u_v`: meters per second or documented component velocity units with axis convention.
- `flux_qx_qy`: cubic meters per second, square meters per second, discharge per width, or another documented flux convention with conversion notes.
- `dx_dy_grid_spacing`: meters or documented projected-coordinate units.
- `dt_time_step`: seconds, minutes, or a documented temporal unit convertible to seconds.
- `DEM_or_bed_elevation`: meters or documented vertical datum units.
- `rainfall_source`: millimeters per interval, millimeters per hour, meters per second, or another documented forcing convention.
- `boundary_conditions`: units appropriate to the boundary type, such as stage, depth, discharge, velocity, flux, or rating-curve parameters.
- `source_sink_terms`: units appropriate to source/sink representation, such as depth rate, volume rate, discharge, or cell-normalized exchange.
- `pump_gate_operations`: units appropriate to state, opening, discharge, rule state, or control schedule.
- masks: boolean, integer, or categorical encodings with explicit meaning.
- coordinate metadata: CRS identifier, projection units, origin, orientation, and grid-index convention.

The specification should require unit conversion notes whenever exported source units differ from model-ready units.

## 7. Shape and Grid Alignment Requirements

Phase 42 should require every spatial field to declare its shape and alignment relationship to the model grid and target grid.

The specification should include requirements for:

- grid height and width;
- node-centered, cell-centered, edge-centered, link-based, or irregular-mesh representation;
- transformation needed to align source-model exports to the repository grid;
- mapping from source nodes, links, cells, or mesh elements to raster cells, if applicable;
- grid origin, orientation, and axis ordering;
- nodata values and valid-domain handling;
- shape compatibility among water depth, velocity or flux, rainfall, DEM, masks, boundaries, and source/sink terms;
- whether interpolation, aggregation, or rasterization is required before residual-style use.

If fields are exported on different grids or meshes, the contract should require explicit remapping metadata. Phase 42 should not assume that matching array dimensions prove physical alignment.

## 8. Time-Axis Alignment Requirements

Phase 42 should require dynamic fields to include explicit time-axis metadata.

The specification should include:

- timestamps or timestep indices for every dynamic field;
- timestep duration and cadence;
- start time and end time;
- timezone or reference-time convention, if applicable;
- event or scenario identifier;
- relationship between rainfall intervals, hydrodynamic states, boundary values, and source/sink terms;
- handling of warm-up periods, spin-up periods, missing timesteps, and irregular timesteps;
- alignment between input sequences, target horizons, and exported hydrodynamic states.

The contract should require `dt_time_step` to be explicit. It should not infer physical timestep duration from file ordering alone.

## 9. Boundary and Source/Sink Requirements

Phase 42 should require boundaries and source/sink terms to be specified with enough detail to support future residual feasibility review.

Boundary requirements should include:

- boundary type, such as open boundary, wall, inflow, outflow, stage, discharge, rating curve, or control boundary;
- boundary location aligned to grid cells, faces, links, nodes, or masks;
- boundary values over time where applicable;
- sign convention for inflow and outflow;
- units and temporal cadence;
- whether a boundary is fixed, time-varying, scenario-specific, or rule-controlled.

Source/sink requirements should include:

- rainfall forcing;
- infiltration or losses, if represented;
- sewer, drain, outfall, inlet, or lateral exchange terms, if represented;
- pump, gate, valve, or controlled-flow terms, if represented;
- external inflow or imposed discharge terms, if represented;
- evaporation, abstraction, or storage exchange terms, if represented;
- explicit documentation of terms that are not represented in the source model.

The specification should treat incomplete source/sink closure as a blocking uncertainty for future Level 5 residual claims.

## 10. UrbanFlood24 Full Dataset Inspection Requirements

If the UrbanFlood24 full dataset is available, Phase 42 should define a checklist for inspecting it without training.

The inspection checklist should verify:

- whether full hydrodynamic state variables are included beyond depth-like outputs;
- whether velocity, flux, discharge, or equivalent transport fields are present;
- whether `dx`, `dy`, and `dt` are explicitly documented;
- whether rainfall, DEM/static maps, masks, targets, and dynamic hydrodynamic fields share a common grid and time axis;
- whether boundary-condition values are included or only implied;
- whether pump, gate, drainage, sewer, or source/sink terms are included;
- whether scenario metadata links all exported files for the same event;
- whether units, scaling, nodata conventions, and coordinate metadata are complete;
- whether any files are proxies, derived diagnostics, or visualization products rather than physical state exports.

The checklist should distinguish directly usable physical exports from partial metadata, documentation-only references, and proxy diagnostics.

## 11. InfoWorks ICM / MIKE+ Export Requirements

Phase 42 should define an external export request checklist for InfoWorks ICM, MIKE+, or equivalent hydrodynamic model systems.

The checklist should request, when available:

- depth or water-level rasters or mesh/cell state exports;
- velocity component exports or flow/flux/discharge exports;
- grid, mesh, node, link, and cell geometry metadata;
- physical grid spacing or mesh geometry needed to derive equivalent `dx` and `dy`;
- simulation timestep and output timestep metadata;
- DEM, bed elevation, ground elevation, or hydraulic elevation references;
- rainfall and external forcing series;
- boundary-condition definitions and time series;
- source/sink definitions and time series;
- pump, gate, valve, weir, inlet, outlet, and control-operation schedules;
- coordinate reference system and vertical datum;
- scenario names, event IDs, model version, export timestamp, and run settings;
- units, scaling, nodata conventions, and sign conventions.

For link- or network-based exports, the request should include the mapping needed to relate network elements to the raster or grid used by this repository. The checklist should not assume that a 1D/2D source model can be used for residual constraints without explicit spatial mapping.

## 12. Planned Specification Script

Phase 42 should implement:

`scripts/specify_phase42_hydrodynamic_export_requirements.py`

The script should be specification-only. It must not train, evaluate checkpoints, run seeds, launch sweeps, modify losses, modify configs, modify model architecture, implement SWE residuals, or implement PINN components.

The script should:

- define the required hydrodynamic export field categories;
- define minimum SWE residual data contract entries;
- define unit, shape, grid, time-axis, boundary, and source/sink requirements;
- define export priority levels;
- produce checklists for UrbanFlood24 full dataset inspection;
- produce checklists for InfoWorks ICM, MIKE+, or equivalent external model export requests;
- write CSV, JSON, and Markdown outputs to the Phase 42 output directory;
- fail closed or mark the export contract incomplete if required specification entries are missing.

The script may encode requirements and checklist rows, but it should not inspect heavy datasets unless a future phase explicitly authorizes a no-training dataset inspection.

## 13. Expected Outputs

Phase 42 should write outputs to:

`analysis/phase42_hydrodynamic_export_requirements/`

Required output files:

- `required_hydrodynamic_fields.csv`
- `field_unit_shape_time_requirements.csv`
- `swe_residual_minimum_data_contract.csv`
- `export_priority_table.csv`
- `urbanflood24_full_inspection_checklist.csv`
- `icm_mike_export_checklist.csv`
- `phase42_export_requirement_summary.json`
- `phase42_export_requirement_summary.md`

Suggested fields for `required_hydrodynamic_fields.csv`:

- `category`
- `required_for_minimum_contract`
- `acceptable_equivalent_fields`
- `why_required`
- `blocking_if_missing`
- `notes`

Suggested fields for `field_unit_shape_time_requirements.csv`:

- `category`
- `expected_units`
- `expected_shape`
- `grid_alignment_requirement`
- `time_alignment_requirement`
- `metadata_required`
- `conversion_notes`

Suggested fields for `swe_residual_minimum_data_contract.csv`:

- `contract_item`
- `field_category`
- `minimum_requirement`
- `required_evidence`
- `allowed_absence_condition`
- `level5_blocking_if_absent`
- `interpretation`

Suggested fields for `export_priority_table.csv`:

- `priority`
- `category`
- `reason`
- `recommended_source`
- `inspection_or_request_action`
- `notes`

Suggested fields for `phase42_export_requirement_summary.json`:

- `phase`
- `phase41_readiness_decision`
- `training_authorized`
- `level5_supported`
- `swe_residual_implementation_authorized`
- `external_export_needed`
- `decision_candidate`
- `required_outputs`
- `guardrails`
- `summary`

Decision candidates:

- `export_contract_ready_for_dataset_inspection`
- `export_contract_ready_for_icm_mike_request`
- `export_contract_incomplete_needs_review`

## 14. Guardrails

Phase 42 must follow these guardrails:

- no training
- no seed42 run
- no seed123 run
- no seed202 run
- no sweeps
- no loss modification
- no config modification
- no model architecture modification
- no SWE residual implementation
- no PINN implementation
- no claim of SWE/PINN support
- no claim of strict conservation
- no claim of full mass conservation
- no claim of hydrodynamic closure
- no claim of Level 5 support
- no reinterpretation of Phase 41 uncertainty as readiness

Phase 42 may specify requirements for future data recovery. It may not treat the existence of a requirement as evidence that the corresponding data are available.

## 15. Success Criteria

Phase 42 succeeds if it produces a conservative, reproducible, no-training hydrodynamic export requirement specification.

Minimum success criteria:

- all required export field categories are listed;
- the minimum SWE residual data contract is explicit;
- unit requirements are recorded for each field category;
- shape and grid alignment requirements are recorded;
- time-axis alignment requirements are recorded;
- boundary and source/sink requirements are recorded;
- UrbanFlood24 full dataset inspection requirements are documented;
- InfoWorks ICM / MIKE+ export requirements are documented;
- expected CSV, JSON, and Markdown outputs are defined;
- final decision is one of the approved decision candidates;
- all guardrails are preserved;
- final wording states that Phase 42 does not implement residual constraints, does not train, and does not claim Level 5 support.

Phase 42 does not require obtaining the external export. A valid successful outcome may be a complete export contract ready for later dataset inspection or external model export request.

## 16. Final Conclusion

Phase 42 creates a data contract and export requirement specification for future Level 5 SWE-oriented constraints. It is a no-training planning and specification phase only.

The expected conclusion is that future Level 5 residual consideration requires explicit hydrodynamic exports or metadata recovery for velocity or flux, grid spacing, timestep, boundary conditions, complete source/sink terms, operational controls, and aligned state variables. Phase 42 does not implement those constraints, does not train, and does not claim Level 5 support.
