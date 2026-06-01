# Phase 43 UrbanFlood24 Full Dataset Inspection

This is a no-training, read-only inspection of the downloaded UrbanFlood24 full dataset against the Phase 42 hydrodynamic export/data contract.

## Decision

- Dataset path: `E:\BaiduNetdiskDownload\urbanflood24\urbanflood24`
- Dataset path exists: `true`
- Selected decision: `full_dataset_readiness_uncertain_needs_metadata`
- Level 5 supported: `false`
- Level 4+ supported: `true`
- Training authorized: `false`
- SWE residual implementation authorized: `false`

## Dataset Evidence

- Total files inventoried: `354`
- Total directories inventoried: `186`
- Splits found: `test, train`
- Locations found: `location1, location2, location3`
- Sampled arrays inspected with mmap: `54`

UrbanFlood24 full dataset appears to provide higher-resolution flood/rain/static-map data where `flood.npy`, `rainfall.npy`, and geodata arrays are present.

## Phase 42 Contract Matrix

| Field | Status | Evidence type | Sufficient for Level 5 | Notes |
| --- | --- | --- | --- | --- |
| `water_depth_h` | `present` | `direct_array` | `true` | flood.npy is treated conservatively as water-depth/flood-state evidence only. |
| `velocity_u_v` | `absent` | `missing` | `false` | Only explicit velocity/u/v files or fields would satisfy this field; path keywords alone are not sufficient. |
| `flux_qx_qy` | `absent` | `missing` | `false` | Only explicit qx/qy/flux/discharge arrays or metadata would satisfy this field. |
| `dx_dy_grid_spacing` | `absent` | `missing` | `false` | Shape compatibility is not physical dx/dy. This is not present without explicit local grid-spacing metadata. |
| `dt_time_step` | `uncertain` | `inferred_from_shape_or_known_dataset` | `false` | Flood/rainfall lengths indicate sequence axes but do not establish physical dt. |
| `DEM_or_bed_elevation` | `present` | `direct_array` | `true` | absolute_DEM.npy supports terrain/bed-elevation proxy evidence; vertical units/datum remain a metadata concern. |
| `rainfall_source` | `present` | `direct_array` | `true` | rainfall.npy supports rainfall forcing evidence, not complete source/sink closure. |
| `boundary_conditions` | `absent` | `missing` | `false` | Boundary conditions require explicit boundary locations/types/values; no inference is made from grid edges. |
| `source_sink_terms` | `uncertain` | `inferred_from_shape_or_known_dataset` | `false` | Rainfall, imperviousness, and manhole maps do not establish complete non-rain source/sink terms or closure. |
| `pump_gate_operations` | `absent` | `missing` | `false` | Pump/gate operations require explicit asset states, schedules, flows, or documented absence. |
| `valid_domain_mask` | `absent` | `missing` | `false` | No explicit valid-domain mask is inferred from flood/static array extents. |
| `boundary_mask` | `absent` | `missing` | `false` | A boundary mask is distinct from boundary-condition values and is not inferred from raster borders. |
| `coordinate_reference_or_grid_metadata` | `absent` | `missing` | `false` | CRS, projection, origin, orientation, and grid metadata must be explicit. |
| `units_and_scaling` | `absent` | `missing` | `false` | Units and scaling are not inferred from file names, shapes, or dtype. |
| `scenario_metadata` | `uncertain` | `inferred_from_shape_or_known_dataset` | `false` | Scenario folder names provide partial event identifiers only, not complete machine-readable scenario metadata. |
| `time_axis_metadata` | `uncertain` | `inferred_from_shape_or_known_dataset` | `false` | Flood/rainfall time dimensions are observed, but timestamps, cadence, units, and alignment metadata are incomplete. |

## Level 5 Blocking Fields

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

If no velocity/flux/boundary/source-sink/pump-gate/dx/dy/dt metadata are found, the dataset supports Level 4+ proxy diagnostics but not direct Level 5 SWE residual constraints.

No SWE/PINN, strict conservation, full mass conservation, hydrodynamic closure, or Level 5 support is claimed.

## Next Recommended Action

Use the dataset for Level 4+ proxy diagnostics only and recover/export explicit velocity or flux, boundary/source-sink, pump/gate, dx/dy, dt, CRS/grid, units, scenario, and time-axis metadata before any Level 5 review.
