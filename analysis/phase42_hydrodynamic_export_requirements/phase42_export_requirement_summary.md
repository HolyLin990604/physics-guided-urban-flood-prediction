# Phase 42 Hydrodynamic Export Requirement Specification

Phase 42 is a no-training specification only. It creates the data contract required before future Level 5 SWE-oriented work can be considered.

It does not claim Level 5 support. It does not implement SWE residuals. It does not implement PINN components. It does not authorize training.

## Decision

- Selected decision: `export_contract_ready_for_dataset_inspection`
- Training authorized: `false`
- Level 5 supported: `false`
- SWE residual implementation authorized: `false`
- External export needed: `true`

## What This Contract Clarifies

This contract clarifies what must be exported or recovered before SWE/PINN work can be considered: aligned depth, velocity or flux, physical dx/dy, physical dt, DEM or bed elevation, rainfall, boundary conditions, complete source/sink terms, valid-domain masks, units, scenario metadata, and time-axis metadata.

## Required Hydrodynamic Field Categories

| Field | Priority | Required for Level 5 | Missing consequence |
| --- | --- | --- | --- |
| `water_depth_h` | `P0` | `true` | Blocks even depth-based target verification and blocks future SWE residual consideration. |
| `velocity_u_v` | `P0` | `true` | Blocks momentum residuals and full hydrodynamic state closure; depth-only work remains Level 4 proxy. |
| `flux_qx_qy` | `P0` | `true` | Blocks continuity residual and mass-balance closure unless velocity plus depth and geometry can form flux. |
| `dx_dy_grid_spacing` | `P0` | `true` | Blocks physical derivatives, volume conversion, and residual scaling. |
| `dt_time_step` | `P0` | `true` | Blocks temporal derivatives and physical source/rainfall rate conversion. |
| `DEM_or_bed_elevation` | `P0` | `true` | Blocks bed-slope and momentum residual terms and weakens terrain-aware diagnostics. |
| `rainfall_source` | `P0` | `true` | Blocks continuity source term and mass-balance forcing review. |
| `boundary_conditions` | `P0` | `true` | Blocks treatment of open boundaries and can invalidate residual or mass-balance interpretation. |
| `source_sink_terms` | `P0` | `true` | Blocks complete continuity closure and full mass-balance claims. |
| `pump_gate_operations` | `P1` | `true` | Blocks closure wherever controlled assets affect flows; absence must be documented if not represented. |
| `valid_domain_mask` | `P0` | `true` | Blocks reliable masking of nodata/outside-domain cells. |
| `boundary_mask` | `P0` | `true` | Blocks boundary-aware residual handling and boundary mass-balance accounting. |
| `coordinate_reference_or_grid_metadata` | `P0` | `true` | Blocks defensible spatial alignment and physical derivative interpretation. |
| `units_and_scaling` | `P0` | `true` | Blocks physical interpretation and any residual or conservation-style claim. |
| `scenario_metadata` | `P1` | `true` | Blocks reproducibility and can mix incompatible event fields. |
| `time_axis_metadata` | `P0` | `true` | Blocks temporal derivatives and dynamic forcing alignment. |

## Minimum SWE Residual Data Contract

| Item | Category | Minimum requirement |
| --- | --- | --- |
| `MC01` | `water_depth_h` | aligned h(t,y,x) |
| `MC02` | `velocity_u_v_or_flux_qx_qy` | either u/v or qx/qy aligned to h |
| `MC03` | `dx_dy_grid_spacing` | dx/dy with physical units |
| `MC04` | `dt_time_step` | dt with physical units |
| `MC05` | `DEM_or_bed_elevation` | DEM or bed elevation aligned to h |
| `MC06` | `rainfall_source` | rainfall source aligned to h time axis |
| `MC07` | `boundary_conditions` | boundary mask and boundary values / boundary conditions |
| `MC08` | `source_sink_terms` | complete source/sink documentation |
| `MC09` | `valid_domain_mask` | valid-domain mask |
| `MC10` | `scenario_metadata_and_units` | scenario metadata and units |

## Guardrails

- no training
- no seed runs
- no sweeps
- no loss modification
- no config modification
- no model architecture modification
- no SWE residual implementation
- no PINN implementation
- no strict conservation claim
- no full mass conservation claim
- no hydrodynamic closure claim
- no Level 5 support claim

No strict conservation, full mass conservation, hydrodynamic closure, SWE/PINN support, or Level 5 support claim is made.

## Next Recommended Action

Inspect UrbanFlood24 full dataset if available and/or request/export fields from InfoWorks ICM, MIKE+, or an equivalent hydrodynamic source.

Inspect the UrbanFlood24 full dataset if available and/or request/export the required fields from InfoWorks ICM, MIKE+, or an equivalent hydrodynamic source.
