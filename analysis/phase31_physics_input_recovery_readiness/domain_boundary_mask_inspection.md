# Phase 31 Domain Boundary Mask Inspection

This diagnostic constructs candidate masks from recovered DEM/static maps and writes only Phase 31 analysis outputs. It does not train, modify architecture, modify losses, modify training configs, run seed123/seed202, or perform sweeps.

## Executive Summary

- Locations processed: 3
- All masks shape-compatible with 128 x 128 flood maps: `True`
- Valid-domain mask status: `supported_dem_lt_99`
- Boundary-ring mask status: `supported`
- Interior mask status: `supported`
- Train/test mask consistency: `consistent_equal`
- Level 4+ domain/boundary-aware readiness: `supported`
- Level 5 status: `unsupported`

## Direct Answers

1. A valid-domain mask can be constructed from `absolute_DEM < 99`: `True`. This is a Level 4+ proxy support, not a conservation proof.
2. Train/test masks are consistent: `consistent_equal`.
3. A boundary-ring mask can be constructed from valid cells adjacent to invalid/high cells or the image border: `True`.
4. An interior mask can be constructed as valid cells not in the boundary ring: `True`.
5. Manhole and impervious maps support additional static proxy diagnostics: manhole=`supported_nonzero_indicator`, impervious=`supported_high_impervious_indicator`.
6. This supports Level 4+ domain-aware / boundary-aware diagnostics: `supported`.
7. This does not change Level 5 status. Level 5 remains unsupported unless velocity/flux, boundary source/sink, dx/dy, dt, and hydrodynamic state variables are found.
8. Recommended next technical step: implement a diagnostic-only Level 4+ script that applies these masks to existing prediction/target flood-depth rasters and reports domain-interior, boundary-ring, high-impervious, and manhole-proximal proxy errors without changing training.

## Train Split Location Summary

| Location | Valid ratio | Invalid/high ratio | Boundary/valid | Interior/valid | Border valid count | Manhole/valid | High impervious/valid |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| location1 | 0.81903076171875 | 0.18096923828125 | 0.09374767121245994 | 0.90625232878754 | 54 | 0.05119606528057232 | 0.642819882256502 |
| location2 | 0.95367431640625 | 0.04632568359375 | 0.031744 | 0.968256 | 249 | 0.043776 | 0.457344 |
| location3 | 0.8607177734375 | 0.1392822265625 | 0.1715359523471848 | 0.8284640476528152 | 74 | 0.1906821727414551 | 0.43461920294993617 |

## Train/Test Mask Consistency

| Location | Same shape | All masks equal | Valid domain | Boundary ring | Interior | Manhole nonzero | High impervious |
| --- | --- | --- | --- | --- | --- | --- | --- |
| location1 | `True` | `True` | `True` | `True` | `True` | `True` | `True` |
| location2 | `True` | `True` | `True` | `True` | `True` | `True` | `True` |
| location3 | `True` | `True` | `True` | `True` | `True` | `True` | `True` |

## Classification

Because the valid-domain and boundary-ring masks are shape-compatible and train/test consistent, Level 4+ domain-aware and boundary-aware proxy diagnostics are supported. Level 5 remains unsupported because this diagnostic does not recover aligned hydrodynamic state, velocity/flux, boundary/source-sink, dx/dy, or dt variables.

## Optional Figures

- `analysis/phase31_physics_input_recovery_readiness/figures/domain_boundary_mask_location1.png`
- `analysis/phase31_physics_input_recovery_readiness/figures/domain_boundary_mask_location2.png`
- `analysis/phase31_physics_input_recovery_readiness/figures/domain_boundary_mask_location3.png`
