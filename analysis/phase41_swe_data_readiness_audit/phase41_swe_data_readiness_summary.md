# Phase 41 SWE Data Readiness Audit

This is a no-training data-readiness audit. It does not modify losses, configs, model architecture, or training behavior; it does not run seeds or implement SWE/PINN residuals.

## Final Readiness Decision

- Final readiness decision: `readiness_uncertain_requires_external_data_export`
- Level 5 SWE residual support: `False`
- External hydrodynamic model export needed: `True`
- Next recommended action: Recover or export hydrodynamic model fields: velocity/flux, dx/dy, dt, boundary conditions, and complete source/sink terms.

## Supported Data Categories

- `source_sink_terms`
- `hydrodynamic_state_variables`
- `rainfall_source_alignment`
- `DEM/static_elevation_alignment`
- `valid_domain_and_boundary_masks`

## Missing Or Uncertain Data Categories

- `velocity_or_flux_fields`: uncertain, likely requires external export or metadata recovery
- `dx_dy_grid_spacing`: uncertain, likely requires external export or metadata recovery
- `dt_time_step`: uncertain, likely requires external export or metadata recovery
- `boundary_conditions`: uncertain, likely requires external export or metadata recovery
- `pump_gate_operations`: uncertain, likely requires external export or metadata recovery

## What Supports Level 4+ Proxy Diagnostics

- Flood/depth target arrays and evaluation prediction/target rasters support depth-based proxy diagnostics.
- Rainfall fields are paired with flood/depth event sequences and are handled by the existing adapter alignment modes.
- `absolute_DEM`, impervious, and manhole static maps are available as static proxy inputs.
- Phase 31 valid-domain and boundary-ring masks support domain-aware and boundary-aware proxy diagnostics.

## What Blocks Level 5 SWE/PINN Residual Constraints

- `velocity_or_flux_fields`
- `dx_dy_grid_spacing`
- `dt_time_step`
- `boundary_conditions`
- `source_sink_terms`
- `hydrodynamic_state_variables`

Missing velocity/flux, physical dx/dy, physical dt, boundary conditions, complete source/sink terms, pump/gate operations, or complete hydrodynamic state variables blocks Level 5 SWE residual claims. Current evidence must not be described as strict conservation, full mass conservation, hydrodynamic closure, SWE/PINN support, or Level 5 support.

## Readiness Matrix

| Category | Readiness | Critical for Level 5 | Level 4 Proxy Only | Level 5 Residual |
| --- | --- | --- | --- | --- |
| `velocity_or_flux_fields` | `uncertain_external_export_needed` | `True` | `False` | `False` |
| `dx_dy_grid_spacing` | `uncertain_external_export_needed` | `True` | `False` | `False` |
| `dt_time_step` | `uncertain_external_export_needed` | `True` | `False` | `False` |
| `boundary_conditions` | `uncertain_external_export_needed` | `True` | `False` | `False` |
| `source_sink_terms` | `partial` | `True` | `True` | `False` |
| `pump_gate_operations` | `uncertain_external_export_needed` | `False` | `False` | `False` |
| `hydrodynamic_state_variables` | `partial` | `True` | `True` | `False` |
| `rainfall_source_alignment` | `present_aligned` | `False` | `True` | `False` |
| `DEM/static_elevation_alignment` | `present_aligned` | `False` | `True` | `False` |
| `valid_domain_and_boundary_masks` | `present_aligned` | `False` | `True` | `False` |

## External Export Need

External hydrodynamic model export is needed before any Level 5 residual prototype planning unless the missing categories are recovered locally with explicit grid/time alignment and physical units.

## Guardrail Conclusion

Phase 41 supports continued no-training data recovery and Level 4+ proxy diagnostics. It does not authorize training and does not justify SWE/PINN residual implementation.
