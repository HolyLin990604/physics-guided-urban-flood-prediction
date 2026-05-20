# Phase 31 Static Map Inspection

This diagnostic inspection reads recovered static maps and writes only Phase 31 analysis outputs. It does not train models, modify architecture, modify losses, modify training configs, run seed123/seed202, or perform sweeps.

## Executive Summary

- Static maps inspected: 18 / 18
- Shape-compatible with 128 x 128 flood maps: `True`
- Train/test geodata consistency: `consistent_allclose`
- DEM valid-domain candidate: `supported_dem_lt_99`
- Level 4+ static-map-aware readiness: `supported`
- Level 5 status: `unsupported`

## Direct Answers

1. Static maps are shape-compatible with flood maps: `True`. The inspected static maps have the expected 128 x 128 grid shape.
2. Train/test geodata are consistent: `consistent_allclose`. Consistency here means numerically close for the same location/channel.
3. DEM is usable as a Level 4+ static elevation proxy: `True`. This supports DEM-aware proxy diagnostics, not SWE/PINN closure.
4. DEM=100.0 likely indicates an invalid, high-boundary, or no-data candidate: `True`.
5. A candidate valid-domain mask can be constructed from `absolute_DEM < 99`: `True`.
6. Impervious and manhole maps are usable as static runoff/drainage proxies: impervious=`usable`, manhole=`usable_sparse_indicator`.
7. This supports a next domain/boundary mask construction script: `True`.
8. This does not change Level 5 status. Level 5 remains unsupported unless aligned velocity/flux, boundary/source-sink variables, dx/dy, and dt are found.

## Location Summary

| Location | DEM valid ratio | DEM=100 count | Impervious mean | Impervious valid mean | Manhole nonzero ratio | Train/test allclose |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| location1 | 0.81903076171875 | 2965 | 0.7079832094791527 | 0.7082418161117824 | 0.0423583984375 | `True` |
| location2 | 0.95367431640625 | 759 | 0.7117959946165229 | 0.7463721968510151 | 0.041748046875 | `True` |
| location3 | 0.8607177734375 | 2282 | 0.746847720034566 | 0.7651044577508087 | 0.16552734375 | `True` |

## Classification

Because DEM, impervious, and manhole maps are shape-compatible and consistent across train/test, Level 4+ static-map-aware diagnostics are supported. Level 5 remains unsupported by this inspection because hydrodynamic state, velocity/flux, boundary/source-sink, dx/dy, and dt variables were not found.

## Optional Figures

- `analysis/phase31_physics_input_recovery_readiness/figures/static_map_location1_preview.png`
- `analysis/phase31_physics_input_recovery_readiness/figures/static_map_location2_preview.png`
- `analysis/phase31_physics_input_recovery_readiness/figures/static_map_location3_preview.png`
